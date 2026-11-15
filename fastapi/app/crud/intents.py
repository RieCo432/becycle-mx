"""#501 client-chat intents: CRUD, the live-data fragment registry, and the safe
template evaluator that assembles a pre-formed reply from a stored template.

This module is deliberately free of any ``app.services.llm_agent`` import: the
Agent (services/llm_agent) pulls ``get_enabled_intents`` from here to build its
classification prompt, and the only thing that needs the LLM — the
``customerFreeForm`` free-form fallback — lives in crud/chats.py, which composes
this module with the Agent. Keeping the LLM out of here is what both prevents a
crud<->services import cycle and keeps the handlers pure app logic
(C-5: LLM-independent).
"""
import re
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas

from .settings import get_opening_times, get_closed_days
from .appointments import get_appointment_types
from .catalogue import get_catalogue

# Python's date.weekday() is Monday=0 .. Sunday=6, matching get_opening_times'
# day_translate and the day names it returns.
_WEEKDAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def _normalise_name(name: str) -> str:
    """Reduce a user-supplied intent key to the stable slug form the classifier
    emits and the dispatcher matches on (lowercase letters, digits, underscores)."""
    slug = (name or "").strip().lower().replace(" ", "_").replace("-", "_")
    return re.sub(r"[^a-z0-9_]", "", slug)


def get_all_intents(db: Session) -> list[models.ChatIntent]:
    """All intent rows (enabled and disabled), ordered for display."""
    return list(db.scalars(
        select(models.ChatIntent)
        .order_by(models.ChatIntent.orderIndex, models.ChatIntent.name)
    ))


def get_enabled_intents(db: Session) -> list[models.ChatIntent]:
    """The active intent set (C-9): enabled rows, in order.

    Single source of truth the classifier's prompt and validation are built from
    (services/llm_agent.classify), so the set, the instructions, and the dispatch
    can't drift apart (C-3).
    """
    return list(db.scalars(
        select(models.ChatIntent)
        .where(models.ChatIntent.enabled.is_(True))
        .order_by(models.ChatIntent.orderIndex, models.ChatIntent.name)
    ))


def get_intent_by_name(db: Session, name: str) -> models.ChatIntent | None:
    return db.scalar(select(models.ChatIntent).where(models.ChatIntent.name == name))


def get_intent_by_id(db: Session, intent_id: UUID) -> models.ChatIntent | None:
    return db.scalar(select(models.ChatIntent).where(models.ChatIntent.id == intent_id))


def create_intent(db: Session, data: schemas.ChatIntentCreate) -> models.ChatIntent:
    name = _normalise_name(data.name)
    if not name:
        raise ValueError("An intent needs a non-empty name.")
    intent = models.ChatIntent(
        name=name,
        whenToUse=data.whenToUse.strip() if data.whenToUse and data.whenToUse.strip() else None,
        replyTemplate=data.replyTemplate,
        enabled=data.enabled,
        orderIndex=data.orderIndex,
    )
    db.add(intent)
    db.commit()
    db.refresh(intent)
    return intent


def update_intent(db: Session, intent: models.ChatIntent, data: schemas.ChatIntentUpdate) -> models.ChatIntent:
    if data.name is not None:
        new_name = _normalise_name(data.name)
        if not new_name:
            raise ValueError("An intent needs a non-empty name.")
        intent.name = new_name
    if data.whenToUse is not None:
        intent.whenToUse = data.whenToUse.strip() or None
    if data.replyTemplate is not None:
        intent.replyTemplate = data.replyTemplate
    if data.enabled is not None:
        intent.enabled = data.enabled
    if data.orderIndex is not None:
        intent.orderIndex = data.orderIndex
    db.commit()
    db.refresh(intent)
    return intent


def delete_intent(db: Session, intent: models.ChatIntent) -> None:
    db.delete(intent)
    db.commit()


# ---------------------------------------------------------------------------
# Live-data fragments — the "how to assemble the answer" palette (#501).
#
# Each fragment is a pure function of (db) -> str | None, computed from this
# shop's own live data (C-5: LLM-independent). A fragment returns None when the
# shop has no data for it; a template referencing such a fragment can't be filled
# and falls through to the free-form fallback (see crud/chats.py).
# ---------------------------------------------------------------------------

def _opening_by_name(db: Session) -> dict[str, schemas.DayOpeningTimes]:
    return {t.day: t for t in get_opening_times(db)}


def _minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _next_opening(openings: dict[str, schemas.DayOpeningTimes], now: datetime):
    """The soonest future opening (tomorrow onward, wrapping a week), or None."""
    today_idx = now.weekday()
    for offset in range(1, 8):
        candidate = _WEEKDAY_NAMES[(today_idx + offset) % 7]
        if candidate in openings:
            return candidate, openings[candidate].open
    return None


def _frag_open_today(db: Session) -> str | None:
    """Live 'are we open today / right now?' status, computed from this shop's hours.

    Uses the codebase's UTC 'now' convention (consistent with the rest of the app);
    the open/closed boundary is therefore UTC-relative, which the owner has
    confirmed is fine.
    """
    openings = _opening_by_name(db)
    if not openings:
        return None
    now = datetime.now(timezone.utc)
    today = openings.get(_WEEKDAY_NAMES[now.weekday()])
    if today is not None:
        now_min = now.hour * 60 + now.minute
        if now_min < _minutes(today.open):
            return f"We're not open yet today — we open at {today.open}."
        if now_min < _minutes(today.close):
            return f"We're open today until {today.close}."
    # Not open today (or closed for the day) -> point at the next opening.
    nxt = _next_opening(openings, now)
    if nxt is None:
        return "We're closed today."
    day, open_time = nxt
    return f"We're closed today — we open {day} at {open_time}."


def _frag_opening_hours(db: Session) -> str | None:
    opening_times = get_opening_times(db)
    if not opening_times:
        return None
    return " · ".join(f"{t.day} {t.open}–{t.close}" for t in opening_times)


def _frag_next_opening(db: Session) -> str | None:
    openings = _opening_by_name(db)
    if not openings:
        return None
    nxt = _next_opening(openings, datetime.now(timezone.utc))
    if nxt is None:
        return None
    day, open_time = nxt
    return f"{day} at {open_time}"


def _frag_parts_in_stock(db: Session) -> str | None:
    items = get_catalogue(db)
    if not items:
        return None
    count = len(items)
    names = [i.name.strip() for i in sorted(items, key=lambda i: i.name)][:5]
    listing = ", ".join(names)
    if count > len(names):
        listing += f", and {count - len(names)} more"
    return f"we have {count} parts in stock ({listing})"


def _frag_appointment_types(db: Session) -> str | None:
    types = sorted(get_appointment_types(db, inactive=False), key=lambda t: t.orderIndex)
    if not types:
        return None
    return ", ".join(t.title for t in types)


def _frag_upcoming_closures(db: Session) -> str | None:
    closed = get_closed_days(db, start_date=datetime.now(timezone.utc).date())
    if not closed:
        return None
    return ", ".join(d.date.strftime("%a %d %b") for d in closed[:5])


# name -> (description shown in the UI palette, compute function).
_FRAGMENTS: dict[str, tuple[str, object]] = {
    "open_today": ("Are we open today / right now? (from this shop's live hours)", _frag_open_today),
    "opening_hours": ("The shop's opening hours (weekly schedule)", _frag_opening_hours),
    "next_opening": ("The next day the shop opens", _frag_next_opening),
    "parts_in_stock": ("How many parts are in stock", _frag_parts_in_stock),
    "appointment_types": ("The bookable appointment types", _frag_appointment_types),
    "upcoming_closures": ("Upcoming closure dates", _frag_upcoming_closures),
}


def list_fragments(db: Session) -> list[schemas.FragmentInfo]:
    """The fragment palette (#501): what a reply template may reference, with each
    fragment's example computed from this shop's own data (None = no data, so a
    template using it would fall through)."""
    out = []
    for name, (description, compute) in _FRAGMENTS.items():
        try:
            example = compute(db)
        except Exception:  # a fragment must never take the palette down
            example = None
        out.append(schemas.FragmentInfo(name=name, description=description, example=example))
    return out


# ---------------------------------------------------------------------------
# Template evaluation (C-5: pure app logic, no LLM, no code execution)
# ---------------------------------------------------------------------------

_SLOT = re.compile(r"\{\{\s*([a-z0-9_]+)\s*\}\}")


class _CannotFill(Exception):
    """A template referenced a fragment that is unknown or has no data."""


def evaluate_template(db: Session, template: str | None) -> str | None:
    """Assemble a reply from a stored template by filling its ``{{fragment}}``
    references with values computed from this shop's live data.

    Returns the reply, or None when it can't be filled (template empty, or a
    referenced fragment is unknown / has no data) so the caller falls through to
    the free-form fallback instead of sending a gap. This is safe string
    substitution over a closed set of known fragments — it never executes the
    template.
    """
    if template is None or not template.strip():
        return None
    if not _SLOT.search(template):
        return template.strip()  # pure static text

    def _replace(match):
        name = match.group(1)
        entry = _FRAGMENTS.get(name)
        if entry is None:
            raise _CannotFill()
        value = entry[1](db)
        if value is None or not str(value).strip():
            raise _CannotFill()
        return str(value)

    try:
        result = _SLOT.sub(_replace, template)
    except _CannotFill:
        return None

    result = result.strip()
    return result or None
