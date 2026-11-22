"""#503: the chat booking flow (B-1..B-9) — the one stateful route.

A small guided conversation (the ticket's flow chart):
  1. understand what the customer needs,
  2. confirm the appointment type with them,
  3. offer real slots,
  4. the customer picks one,
  5. the pick is summarised (type + date + time) and the customer confirms
     it, so they always see exactly what would be booked,
  6. the confirmed pick becomes a normal (pending) appointment request
     through the existing booking backend — the single source of truth, no
     parallel path (B-4/B-5).

Division of labour (B-3): the Agent (services.llm_agent.booking_step) is the
only LLM caller — it understands the need, proposes/confirms the type,
interprets the slot choice, and decides the customer's yes/no on the summary;
it writes no customer-facing text. This module is the app logic: the flow's
state (the chatactionflows row), the closed-set re-checks, the slot-offer
shape, the two budgets, the fixed messages, the booking itself, and the
row's lifecycle.

Best-effort throughout (B-6): any failure -> nothing happens or a polite
degradation, never an error surfaced to the customer; the base chat
continues. Terminal outcomes delete the row (the unique
conversation+flowtype means "a booking flow is in progress"), and the audit
trail is the assistant's replies themselves (messages with intent 'booking',
#510).
"""
from datetime import datetime, timezone, date, time as time_cls

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas

from app.extensions.chatactionflowtype import ChatActionFlowType
from app.extensions.chatactionflowstage import ChatActionFlowStage
from app.services.llm_agent import booking_step

from .appointments import (
    get_appointment_type,
    get_appointment_types,
    get_available_start_dates_and_times_for_appointment_type,
    request_appointment,
)

STAGE_ELICITING = ChatActionFlowStage.BOOKING_ELICITING
STAGE_AWAITING_SLOT_CHOICE = ChatActionFlowStage.BOOKING_AWAITING_SLOT_CHOICE
STAGE_AWAITING_CONFIRM = ChatActionFlowStage.BOOKING_AWAITING_CONFIRM

# The seeded intent name (migration #501) that the classifier routes here on:
# "booking" is what the flow's replies record as their intent (audit, #510).
BOOKING_INTENT = "booking"

# The two budgets (ticket decisions): a turn is one assistant message in the
# flow (outer); a re-offer is one additional slot offer (inner), so
# re-offering alone can never eat the whole turn budget. The outer budget
# counts the booking confirmation step (propose -> confirm -> book), so it is
# wider than the original six.
FLOW_TURN_BUDGET = 8
FLOW_MAX_REOFFERS = 2
# The offer shape (ticket decision): the earliest 3 available dates on
# distinct weekdays, first + last available slot of each day.
OFFER_WEEKDAYS = 3
# How many of the client's own messages before the flow's start go into the
# appointment's notes (the trigger burst and its immediate lead-in); the
# flow's own turns are always included on top of this. Matches the harness
# debounce batch cap default (LlmSettings).
BATCH_SIZE = 6

# The fixed messages (org-agnostic, so they hold for every shop). The LLM only
# decides; the app says every word (the owner wants the AI's own text minimal),
# so each customer-facing line is a fixed string here. The confirmation is the
# ticket's wording, verbatim: the booking is a normal pending request, so it is
# true by construction.
CONFIRMATION_MESSAGE = (
    "Your appointment request has been received, an email confirmation of the "
    "reception of request has been sent, and a confirmation of appointment "
    "will follow once a volunteer approves."
)
HANDOFF_MESSAGE = (
    "I'm not quite getting this over chat - the booking page is the surest way "
    "in, or a volunteer can book you in directly."
)
PROPOSE_MESSAGE = "That sounds like a {title} ({duration} min) - does that fit what you need?"
CONFIRM_SLOTS_MESSAGE = "Great - a {title} appointment it is. Here are the next free slots:\n{offer}\nWhich suits you?"
NO_SLOTS_MESSAGE = "A {title} has no free slots right now - the booking page is the place to grab one later."
CLARIFY_MESSAGE = "What would you like to bring your bike in for? We can book: {titles}."
ABORT_MESSAGE = "All good - just say the word if you'd like to book later."
REOFFER_MESSAGE = "No problem - here are some more free slots:\n{offer}\nWhich suits you?"
GUIDE_BACK_MESSAGE = "Which of these suits you?\n{offer}"
# The confirmation step: the picked slot is summarised and the request is
# only put in on the customer's yes (a misread pick is bounded the same way
# as the pending approval - nothing is final until a human approves).
SUMMARY_MESSAGE = "So that's a {title} on {when} - shall I put in the request?"
DENIED_MESSAGE = "No problem - which of these suits you?\n{offer}"
BOOK_FAILED_LEAD = "That one just went while we were looking."
SLOT_TAKEN_LEAD = "That one's already taken."


# ---------------------------------------------------------------------------
# The flow's data payload (the chatactionflows.data JSON column)
# ---------------------------------------------------------------------------

class BookingFlowData(BaseModel):
    """The booking flow's own state. The generic table stores it as JSON;
    this shape is what the flow code reads and writes (the other flow types
    will define their own shapes for the same column)."""

    appointmentTypeId: str | None = None
    # The slot the customer picked and was summarised - the request is only
    # filed once they confirm it (stage BOOKING_AWAITING_CONFIRM).
    pendingSlot: dict | None = None
    # The closed set of slots offered so far (a re-offer appends to it) -
    # the customer's prose choice is validated against exactly this.
    offeredSlots: list[dict] = []
    reoffersUsed: int = 0


# ---------------------------------------------------------------------------
# Row lifecycle
# ---------------------------------------------------------------------------

def get_active_booking_flow(db: Session, conversation_id) -> models.ChatActionFlow | None:
    """The conversation's active booking flow, if any (one per type - the
    unique conversation+flowtype constraint)."""
    return db.scalar(
        select(models.ChatActionFlow)
        .where(models.ChatActionFlow.conversationId == conversation_id)
        .where(models.ChatActionFlow.flowtype == ChatActionFlowType.BOOKING)
    )


def start_booking_flow(db: Session, conversation_id) -> models.ChatActionFlow:
    """Begin a booking flow (stage ELICITING, empty data, no turns used)."""
    flow = models.ChatActionFlow(
        conversationId=conversation_id,
        flowtype=ChatActionFlowType.BOOKING,
        stage=STAGE_ELICITING,
        data=BookingFlowData().model_dump(),
        turnsUsed=0,
    )
    db.add(flow)
    db.commit()
    db.refresh(flow)
    return flow


def end_booking_flow(db: Session, flow: models.ChatActionFlow) -> None:
    """End the flow, whatever the outcome: the row is working state, and it
    goes away so the next booking starts fresh (the replies are the audit)."""
    db.delete(flow)
    db.commit()


# ---------------------------------------------------------------------------
# The slot offer (pure - testable without a database or an LLM)
# ---------------------------------------------------------------------------

def _slot_time_str(value) -> str | None:
    """The availability query returns `time` as datetime.time objects (not
    strings); normalize both to an ISO 'HH:MM:SS' string (None if absent).
    Everything downstream (the stored offeredSlots, the LLM's closed set,
    the booking) uses the string form, so this is the single boundary."""
    if isinstance(value, time_cls):
        return value.isoformat()
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _offer_slice(availability: dict, already_offered: list, count: int = OFFER_WEEKDAYS) -> list[dict]:
    """The next slot offer: the earliest `count` dates not already offered,
    each on a distinct weekday, with the first and last available slot of
    each day (as far apart as possible). Fewer dates available -> what
    exists; none -> []. `already_offered` is empty for the first offer and
    the flow's full offered set for a re-offer (the next slice)."""
    offered_dates = {
        entry.get("date") for entry in (already_offered or []) if isinstance(entry, dict)
    }
    slots_by_date: dict[str, list[str]] = {}
    for day, slots in availability.items():
        day_str = day.isoformat() if isinstance(day, date) else str(day)
        times = []
        for s in (slots or []):
            if isinstance(s, dict) and s.get("available"):
                t = _slot_time_str(s.get("time"))
                if t:
                    times.append(t)
        if times:
            slots_by_date[day_str] = sorted(times)

    out: list[dict] = []
    weekdays_seen: set[int] = set()
    for day_str in sorted(slots_by_date):
        if len({entry["date"] for entry in out}) >= count:
            break
        if day_str in offered_dates:
            continue
        weekday = date.fromisoformat(day_str).weekday()
        if weekday in weekdays_seen:
            continue
        weekdays_seen.add(weekday)
        out.append({"date": day_str, "time": slots_by_date[day_str][0]})
        if len(slots_by_date[day_str]) > 1:
            out.append({"date": day_str, "time": slots_by_date[day_str][-1]})
    return out


def _format_offer(slots: list[dict]) -> str:
    """The offered slots, human-readable, grouped by day:
    'Mon 24 Nov, 10:00 or 16:30'."""
    by_date: dict[str, list[str]] = {}
    for entry in slots:
        by_date.setdefault(entry["date"], []).append(entry["time"])
    lines = []
    for day_str in sorted(by_date):
        day = date.fromisoformat(day_str)
        times = sorted(t[:5] for t in by_date[day_str])  # '14:00:00' -> '14:00'
        lines.append(f"{day.strftime('%a %d %b')}, " + " or ".join(times))
    return "\n".join(lines)


def _slot_when(slot: dict) -> str:
    """A stored slot to its human form, same shape as the offer lines:
    '2026-12-03' + '18:15:00' -> 'Wed 03 Dec, 18:15'."""
    day = date.fromisoformat(slot["date"])
    return f"{day.strftime('%a %d %b')}, {str(slot['time'])[:5]}"


def _time_minutes(time_str: str) -> int | None:
    """'HH:MM' or 'HH:MM:SS' to minutes-of-day, or None (lenient compare)."""
    parts = (time_str or "").split(":")
    if len(parts) not in (2, 3):
        return None
    try:
        return int(parts[0]) * 60 + int(parts[1])
    except ValueError:
        return None


def _slot_datetime(slot: dict) -> datetime | None:
    """An offered/asked slot to a UTC datetime (slots are UTC - the existing
    client booking path parses them as +00:00), or None when malformed."""
    try:
        day = date.fromisoformat(slot["date"])
        parts = slot["time"].split(":")
        clock = time_cls(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
    except (KeyError, ValueError, TypeError):
        return None
    return datetime.combine(day, clock, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# The booking (the existing backend, for this chat's client)
# ---------------------------------------------------------------------------

def _client_notes(db: Session, conversation: models.Conversation, started_on: datetime) -> str | None:
    """The client's own words about this booking, in order - the trigger burst
    and its immediate lead-in (up to the flow's start), plus the flow's own
    turns (everything the client said after the flow started, up to the
    booking). This is the booking conversation, not the whole chat history:
    the trigger is always before createdOn (the flush fires after the
    debounce window) and the flow's turns after it, so createdOn is the clean
    split. The flow's turns are naturally short (the flow's turn budget), and
    a final cap guards against any runaway."""
    owner = conversation.initiatorParticipant
    if owner is None:
        return None
    base = (
        models.Message.conversationId == conversation.id,
        models.Message.sentByParticipantId == owner.id,
    )
    # Trigger + lead-in: the most recent BATCH_SIZE client messages up to the flow start.
    lead_in = db.scalars(
        select(models.Message.body)
        .where(*base)
        .where(models.Message.sentOn <= started_on)
        .order_by(models.Message.sentOn.desc(), models.Message.id.desc())
        .limit(BATCH_SIZE)
    ).all()
    # The flow's own turns: every client message after the flow started (to now).
    flow_turns = db.scalars(
        select(models.Message.body)
        .where(*base)
        .where(models.Message.sentOn > started_on)
        .order_by(models.Message.sentOn.asc(), models.Message.id.asc())
    ).all()
    bodies = list(reversed(lead_in)) + list(flow_turns)
    # Blank line between messages so the notes read as distinct turns.
    notes = "\n\n".join(b.strip() for b in bodies if b and b.strip())
    if not notes:
        return None
    if len(notes) > 1000:
        notes = notes[:997].rstrip() + "..."
    return notes


def _try_book(db: Session, conversation: models.Conversation, flow: models.ChatActionFlow,
              data: BookingFlowData, slot: dict):
    """Book the chosen slot through the shared request path (B-4/B-5): the
    same `request_appointment` the client endpoint uses — create the pending
    request for this chat's own client and send the request-received email.
    The client's trigger message and the flow's own turns go into the notes,
    so the approving volunteer has the context. Returns the appointment, or
    None (slot just taken, the 2-pending cap, or no client) - the caller
    degrades, B-6."""
    client = conversation.initiatorParticipant.client
    if client is None or not data.appointmentTypeId:
        return None
    start = _slot_datetime(slot)
    if start is None:
        return None
    try:
        return request_appointment(
            db=db,
            appointment_data=schemas.AppointmentCreate(
                clientId=client.id,
                typeId=data.appointmentTypeId,
                startDateTime=start,
                notes=_client_notes(db=db, conversation=conversation, started_on=flow.createdOn),
            ),
        )
    except HTTPException:
        # Slot just taken, or the client is at the pending-request cap:
        # nothing to surface - the caller offers alternatives / hands off.
        return None


def _slot_is_live_available(db: Session, type_id: str, slot: dict) -> bool:
    """A specific ask ("what about Friday 3pm?"), checked against real
    availability right now (app logic, B-4) - not just the offered set."""
    start = _slot_datetime(slot)
    if start is None or not type_id:
        return False
    availability = get_available_start_dates_and_times_for_appointment_type(
        db=db, appointment_type_id=type_id, ignore_limits=False
    )
    ask_minutes = _time_minutes(str(slot.get("time", "")))
    for entry in availability.get(start.date(), []):
        t = _slot_time_str(entry.get("time"))
        if entry.get("available") and t and _time_minutes(t) == ask_minutes:
            return True
    return False


# ---------------------------------------------------------------------------
# The stage handlers (the app composes every message from fixed strings; the
# LLM only decides)
# ---------------------------------------------------------------------------

def _save_turn(db: Session, flow: models.ChatActionFlow, data: BookingFlowData) -> None:
    """Persist the flow's data and spend a turn (one assistant message)."""
    flow.data = data.model_dump()
    flow.turnsUsed += 1
    db.commit()


def _type_title_duration(db: Session, type_id: str) -> tuple[str, int]:
    """The type's (title, duration-min) for a message, or a generic fallback
    when the id is somehow not found (it was validated by the Agent)."""
    t = get_appointment_type(db=db, appointment_type_id=type_id)
    if t is None:
        return "appointment", 0
    return (t.title or "appointment").strip() or "appointment", (t.duration or 0)


def _active_type_titles(db: Session) -> str:
    """The active types' titles, for the clarifying question's closed set."""
    types = sorted(get_appointment_types(db=db, inactive=False), key=lambda t: t.orderIndex)
    titles = [(t.title or "").strip() for t in types]
    return ", ".join(t for t in titles if t)


def _step_eliciting(db: Session, conversation: models.Conversation,
                    flow: models.ChatActionFlow, data: BookingFlowData, step: dict) -> str:
    """Stage ELICITING: understand the need, propose a type, confirm it.
    On confirmation the type is settled and real slots are queried (app
    logic, B-4). The propose -> confirm sequence is enforced: a confirmation
    is only honoured for a type proposed in a previous turn, so the customer
    always gets the one-turn type confirmation."""
    proposed = data.appointmentTypeId  # the type proposed in a previous turn
    if step["type"]:
        data.appointmentTypeId = step["type"]
    type_id = data.appointmentTypeId

    # A confirmation is honoured only for the type proposed in a previous
    # turn (the one-turn confirmation rule): "yes" (whether or not the model
    # repeats the id) settles the proposed type; a different id is a
    # (re)proposal, not a confirmation; with nothing proposed, it clarifies.
    if step["confirmed"] and proposed and (step["type"] is None or step["type"] == proposed):
        title, duration = _type_title_duration(db, type_id)
        availability = get_available_start_dates_and_times_for_appointment_type(
            db=db, appointment_type_id=type_id, ignore_limits=False
        )
        offer = _offer_slice(availability, [])
        if not offer:
            end_booking_flow(db, flow)
            return NO_SLOTS_MESSAGE.format(title=title)
        data.offeredSlots = offer
        flow.stage = STAGE_AWAITING_SLOT_CHOICE
        _save_turn(db, flow, data)
        return CONFIRM_SLOTS_MESSAGE.format(title=title, offer=_format_offer(offer))

    if step["type"] and type_id:
        # (Re)propose the best-fitting type; the customer confirms next.
        title, duration = _type_title_duration(db, type_id)
        _save_turn(db, flow, data)
        return PROPOSE_MESSAGE.format(title=title, duration=duration)

    # Need still unclear: one fixed clarifying question, grounded on the types.
    _save_turn(db, flow, data)
    return CLARIFY_MESSAGE.format(titles=_active_type_titles(db) or "one of our appointments")


def _reoffer_or_handoff(db: Session, flow: models.ChatActionFlow,
                        data: BookingFlowData, lead: str = "") -> str:
    """More options while the re-offer budget allows (inner budget), else
    the handoff; the flow ends on a handoff or when nothing is left to
    offer. `lead` (when given) is the fixed reason line that precedes it."""
    prefix = f"{lead}\n\n" if lead else ""
    if data.reoffersUsed < FLOW_MAX_REOFFERS and data.appointmentTypeId:
        availability = get_available_start_dates_and_times_for_appointment_type(
            db=db, appointment_type_id=data.appointmentTypeId, ignore_limits=False
        )
        extra = _offer_slice(availability, data.offeredSlots)
        if extra:
            data.offeredSlots = list(data.offeredSlots) + extra
            data.reoffersUsed += 1
            _save_turn(db, flow, data)
            return prefix + REOFFER_MESSAGE.format(offer=_format_offer(extra))

    end_booking_flow(db, flow)
    return prefix + HANDOFF_MESSAGE


def _propose_booking(db: Session, conversation: models.Conversation,
                     flow: models.ChatActionFlow, data: BookingFlowData, slot: dict) -> str:
    """A valid pick: record it as pending and summarise it for the customer
    (type + date + time) - the request is only put in on their yes. This is
    the confirmation step that keeps a misread pick bounded: they see exactly
    what would be booked before anything is filed."""
    data.pendingSlot = slot
    flow.stage = STAGE_AWAITING_CONFIRM
    _save_turn(db, flow, data)
    title, _ = _type_title_duration(db, data.appointmentTypeId or "")
    return SUMMARY_MESSAGE.format(title=title, when=_slot_when(slot))


def _finish_or_reoffer(db: Session, conversation: models.Conversation,
                       flow: models.ChatActionFlow, data: BookingFlowData,
                       slot: dict) -> str:
    """The confirmed slot, through the existing backend (the only place a
    request is created). Success -> the confirmation (ticket wording) and
    the flow ends; failure (slot just taken / pending cap) -> no error
    surfaced (B-6): back to the slot stage with a re-offer if the budget
    allows, else the handoff."""
    appointment = _try_book(db=db, conversation=conversation, flow=flow, data=data, slot=slot)
    if appointment is not None:
        data.pendingSlot = None
        end_booking_flow(db, flow)
        return CONFIRMATION_MESSAGE

    data.pendingSlot = None
    flow.stage = STAGE_AWAITING_SLOT_CHOICE
    return _reoffer_or_handoff(db=db, flow=flow, data=data, lead=BOOK_FAILED_LEAD)


def _step_slot_choice(db: Session, conversation: models.Conversation,
                      flow: models.ChatActionFlow, data: BookingFlowData, step: dict) -> str:
    """Stage AWAITING_SLOT_CHOICE: a pick from the offered set (or a
    specific ask, live-checked) moves to the confirmation step; 'none
    appeal' re-offers; anything else steers back to the offered slots.
    Priority: choice > specificAsk > reoffer > guide back."""
    if step["choice"]:
        return _propose_booking(db, conversation, flow, data, step["choice"])

    if step["specificAsk"]:
        if _slot_is_live_available(db=db, type_id=data.appointmentTypeId or "", slot=step["specificAsk"]):
            return _propose_booking(db, conversation, flow, data, step["specificAsk"])
        # Taken (or unresolvable): the same polite path as a failed booking.
        return _reoffer_or_handoff(db=db, flow=flow, data=data, lead=SLOT_TAKEN_LEAD)

    if step["reoffer"]:
        return _reoffer_or_handoff(db=db, flow=flow, data=data)

    # Tangent / question: stay, spend a turn, steer back to the offered slots.
    _save_turn(db, flow, data)
    if data.offeredSlots:
        return GUIDE_BACK_MESSAGE.format(offer=_format_offer(data.offeredSlots))
    return GUIDE_BACK_MESSAGE.format(offer="(none left - pick any time that suits you)")


def _step_confirm(db: Session, conversation: models.Conversation,
                  flow: models.ChatActionFlow, data: BookingFlowData, step: dict) -> str:
    """Stage AWAITING_CONFIRM: the customer's yes/no on the pending request.
    yes -> book (the only place a request is created); no -> back to the
    offered slots; a different slot -> re-summarise; unclear -> re-ask.
    Priority: confirmed > newChoice > specificAsk > denied > re-ask."""
    if step["confirmed"] and data.pendingSlot:
        return _finish_or_reoffer(db, conversation, flow, data, data.pendingSlot)

    if step["newChoice"]:
        # Validated against the offered set by the Agent; re-summarise it.
        return _propose_booking(db, conversation, flow, data, step["newChoice"])

    if step["specificAsk"]:
        if _slot_is_live_available(db=db, type_id=data.appointmentTypeId or "", slot=step["specificAsk"]):
            return _propose_booking(db, conversation, flow, data, step["specificAsk"])
        return _reoffer_or_handoff(db=db, flow=flow, data=data, lead=SLOT_TAKEN_LEAD)

    if step["denied"]:
        # The pending request is dropped; back to the offered slots.
        data.pendingSlot = None
        flow.stage = STAGE_AWAITING_SLOT_CHOICE
        _save_turn(db, flow, data)
        return DENIED_MESSAGE.format(offer=_format_offer(data.offeredSlots))

    # Unclear (or nothing pending): re-ask the confirmation, or re-offer.
    if data.pendingSlot:
        title, _ = _type_title_duration(db, data.appointmentTypeId or "")
        _save_turn(db, flow, data)
        return SUMMARY_MESSAGE.format(title=title, when=_slot_when(data.pendingSlot))
    data.pendingSlot = None
    flow.stage = STAGE_AWAITING_SLOT_CHOICE
    _save_turn(db, flow, data)
    return DENIED_MESSAGE.format(offer=_format_offer(data.offeredSlots))


# ---------------------------------------------------------------------------
# The entry point (one burst -> one assistant reply, or None)
# ---------------------------------------------------------------------------

async def handle_booking_burst(db: Session, conversation: models.Conversation, bodies: list[str]) -> str | None:
    """One burst of the booking flow -> the assistant's reply, or None
    (nothing happens, B-6). This is the state machine (the ticket's flow
    chart): every branch either advances the stage, re-offers, or ends the
    flow (row deleted). The LLM down on any step -> None: no reply, no state
    change, no turn consumed.

    `bodies` is the debounced burst (the harness passes exactly the messages
    the agent answered).
    """
    flow = get_active_booking_flow(db=db, conversation_id=conversation.id)
    if flow is None:
        flow = start_booking_flow(db=db, conversation_id=conversation.id)

    data = BookingFlowData.model_validate(flow.data or {})

    # Turn budget (outer): the flow has already said its piece - hand off
    # rather than spending another LLM call.
    if flow.turnsUsed >= FLOW_TURN_BUDGET:
        end_booking_flow(db, flow)
        return HANDOFF_MESSAGE

    step = await booking_step(db=db, stage=flow.stage, data=data.model_dump(), messages=bodies)
    if step is None:
        return None

    if step["aborted"]:
        # "Never mind" (or "I meant a different kind" in the slot stage):
        # the customer closes it; a fresh booking starts a fresh flow on the
        # next burst. The close is a fixed string (not the LLM's own words).
        end_booking_flow(db, flow)
        return ABORT_MESSAGE

    if flow.stage == STAGE_ELICITING:
        return _step_eliciting(db=db, conversation=conversation, flow=flow, data=data, step=step)
    if flow.stage == STAGE_AWAITING_SLOT_CHOICE:
        return _step_slot_choice(db=db, conversation=conversation, flow=flow, data=data, step=step)
    if flow.stage == STAGE_AWAITING_CONFIRM:
        return _step_confirm(db=db, conversation=conversation, flow=flow, data=data, step=step)

    return None
