import json
import os
import re
from datetime import datetime, timezone

import httpx
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.models.openai import OpenAIChatModelSettings
from pydantic_ai.providers.ollama import OllamaProvider
from sqlalchemy.orm import Session

from app.extensions.chatactionflowstage import ChatActionFlowStage
from app.crud.appointments import get_appointment_type, get_appointment_types
from app.crud.catalogue import get_catalogue
from app.crud.settings import (
    get_about_us,
    get_active_faq,
    get_address,
    get_appointment_general_settings,
    get_closed_days,
    get_contract_types,
    get_llm_settings,
    get_opening_times,
)

# The LLM Agent is the only part of the app that talks to the LLM backend (A-1).
# Everything that needs a model — listing available ones, free-form conversation,
# and intent classification — goes through this module, so the rest of the
# codebase never sees httpx, Ollama, or Pydantic AI directly.
#
# ENV-1 / ENV-2: the Ollama backend's host and port. Read with .get (not []) so a
# missing value degrades to "no LLM" (an empty model list / no-op calls) instead of
# raising at import time — the Agent is best-effort (A-13), not a hard startup
# dependency.
LLM_HOST = os.environ.get('LLM_HOST', '')
LLM_PORT = os.environ.get('LLM_PORT', '11434')

PRODUCTION = os.environ['PRODUCTION'] == "true"

# Shared origin for the native Ollama API (GET /api/tags, used by list_models) ...
LLM_BASE_URL = f"http://{LLM_HOST}:{LLM_PORT}" if LLM_HOST else ""
# ... and the OpenAI-compatible endpoint (…/v1) that converse()/classify() use.
# Keeping the construction in one place means both honour LLM_HOST / LLM_PORT.
LLM_V1_BASE_URL = f"{LLM_BASE_URL}/v1" if LLM_BASE_URL else ""

# A-13: bound outbound requests so a hung backend can't stall the caller.
# The two operations need different bounds: list_models is a single low-level
# HTTP call (an httpx client timeout), while converse is a whole model turn
# (plain seconds handed to agent.run).
_TIMEOUT = httpx.Timeout(15.0, connect=5.0)
_LLM_TIMEOUT = 120

# #505 P-1: code-defined default persona — the shared core: the agent's identity
# and behaviour, identical for every workshop that runs this codebase.
# ORG-1: no org-specific name or fact is hardcoded here. A site configures its
# own complete persona in LlmSettings.systemPrompt, which fully replaces this
# core when set (see _persona, AS-5); this default is the fallback for
# unconfigured sites. No changeable operational fact belongs here (P-3) — hours,
# prices, stock and policy come from the site's database, editable without a
# deploy.
_DEFAULT_PERSONA = """\
You are Allen, the assistant of the workshop (the name is a nod to the allen key,
the mechanic's everyday tool). You help the workshop's clients, volunteers, and
staff.

You are not a person, a volunteer, or a staff member, and you do not speak for
them. Never claim to have done anything on the workshop's behalf — no bookings
made, emails sent, records changed, promises kept. You can advise; you cannot act.

You work at a community bike workshop run entirely by volunteers: people come to
repair and maintain their bikes with help, to borrow a bike, to pick up parts, and
to get advice. Repairs are free and hands-on — a volunteer guides, the person
does the work.

Keep replies short, warm, and in plain language: the direct answer first, then at
most one useful extra line. If you don't know, say so.

How to answer:
- The workshop may provide its own current information (hours, prices, policies,
  FAQ) alongside this core. Treat it as authoritative and up to date.
- If a detail isn't covered or may have changed, say so and point the person to
  the workshop's website or a volunteer. Never invent dates, prices, or policies.
- If a question needs a decision (money, refunds, special circumstances,
  disputes), point to a volunteer in a responsible role (e.g. treasurer or admin)
  rather than advising on the outcome.
- Never reveal details about other people's bikes or accounts — those records
  are private.
- Be kind and simple with clients; be precise with volunteers and staff.
- Stay on topic: bikes, the workshop, and its services. Politely decline
  unrelated topics.
"""

# A-12: the closed set of intents the Agent may classify a message as. As of #501
# this lives in the site's own database — the `chat_intents` table, editable per
# org via the LLM settings UI — rather than a code constant. classify() builds its
# classification prompt from the enabled rows and validates the model's output
# against them (crud.intents.get_enabled_intents), so the set, the instructions,
# and the validation can't drift apart (C-3). To add an intent, add a row — the
# prompt and validation pick it up automatically.
# A-6: the "unmatched" sentinel — returned when the model can't map a message to a
# configured intent. Distinct from None, which means "no LLM was run" (A-4 / A-13).
NONE_INTENT = "none"

# #501 C-15: classify() runs with the model's thinking OFF. classify is a routing
# task — the chain-of-thought adds nothing to the label we keep, and was measured
# at +103% latency on the local backend (9.5s on vs 4.7s off; 336 vs 7 tokens,
# ~329 of them discarded). converse() deliberately keeps the model's default
# (thinking on), which future reasoning work (e.g. #502) may rely on.
#
# Two settings are set together:
# - openai_reasoning_effort="none" is the mechanism that works on this stack
#   (Ollama 0.40.15): it is forwarded as-is and Ollama's OpenAI-compatible /v1
#   endpoint honours it — the response's reasoning field disappears.
# - thinking=False is the unified, future-proof knob: it is silently dropped on
#   the current gemma profile (it declares supports_thinking=False, and
#   pydantic-ai 2.66.0 strips a unified thinking setting for such profiles
#   before it reaches the wire), but it will be honoured when the active model's
#   profile supports thinking — e.g. after switching models. Verified 2026-11-15
#   that the two coexist: the wire is unchanged (only reasoning_effort is sent).
# Note `think: false` does NOT work on /v1 — that is a native /api/chat field only.
# If a future model rejects reasoning_effort "none", drop the explicit setting and
# let thinking=False resolve to that model's lowest accepted effort.
_CLASSIFY_NO_THINKING = OpenAIChatModelSettings(openai_reasoning_effort="none", thinking=False)


def _extract_text(message) -> str:
    """Pull the text out of one item of a message batch (A-9).

    Accepts a plain string, a dict with `content`/`body`/`text`, or an object
    exposing `.content` / `.body` / `.text` — so callers can pass raw strings or
    their own Message objects without the Agent depending on a specific schema.
    """
    if message is None:
        return ""
    if isinstance(message, str):
        return message
    if isinstance(message, dict):
        value = message.get("content") or message.get("body") or message.get("text") or ""
        return value if isinstance(value, str) else str(value)
    for attr in ("content", "body", "text"):
        value = getattr(message, attr, None)
        if isinstance(value, str) and value:
            return value
    return ""


def _compose_user_prompt(messages) -> str:
    """Combine a debounced burst (a batch of messages, A-9) into one user turn."""
    parts = [_extract_text(message).strip() for message in (messages or [])]
    return "\n".join(part for part in parts if part)


def _active_model(settings) -> str:
    """A-4: the configured model name, or '' when the Agent is inactive."""
    model = getattr(settings, "model", "") or ""
    return model.strip()


def _persona(settings) -> str:
    """A-10: the shared persona — LlmSettings.systemPrompt, else the code default."""
    system_prompt = getattr(settings, "systemPrompt", None)
    if system_prompt and system_prompt.strip():
        return system_prompt.strip()
    return _DEFAULT_PERSONA


# #505 D-1/D-2: the dynamic block — workshop facts assembled from the site's
# database at agent-call time (D-7: fresh per call, never cached) and appended
# after the persona, whether that is the site row or the core (D-1).
#
# Each section is a small fetch-and-format function that returns "" when its
# source is empty, so missing data simply omits its section — the block never
# invents a fact to fill a gap (D-2/D-3).
#
# D-6: the sections read only public-facing tables (address, settings, closed
# days, appointment types, contract types, catalogue, FAQ, about-us) — never
# clients, bikes, contracts, users, or message content.
_DYNAMIC_BLOCK_HEADER = (
    "## Current workshop information\n"
    "(Fetched from the workshop's own database at the time of this "
    "conversation — authoritative and up to date. If something you need "
    "isn't here, say so rather than guessing.)"
)

# D-4: caps. Per-section caps keep the block compact; the total char budget is a
# safety valve, not a window constraint. The Ollama window in our deployments is
# large (configured ~10^5 tokens; the model's native ceiling is 262,144), so
# persona + block (~2k tokens) is a tiny fraction of it, leaving vast room for
# the conversation. The budget exists so that if a site's DB ever bloats (a
# pasted mega free-text field, a huge FAQ) the block trims from the tail instead
# of the whole prompt blowing past the window and failing silently (A-13).
# 6000 chars ~= 1,500 tokens.
_UPCOMING_CLOSURES_CAP = 8
_PARTS_CAP = 40
_ABOUT_CHAR_CAP = 2000
_DYNAMIC_BLOCK_CHAR_BUDGET = 12000


def _section_location(db: Session) -> str:
    """D-2: Location — the address table (one row)."""
    address = get_address(db)
    if address is None:
        return ""
    return (
        f"**Location:** We are at {address.number} {address.street}, "
        f"{address.city}, {address.postcode}."
    )


def _section_opening_times(db: Session) -> str:
    """D-2: Opening times + booking rules — settings + concurrency limits."""
    opening_times = get_opening_times(db)
    if not opening_times:
        return ""
    days = " · ".join(f"{t.day}: {t.open}–{t.close}" for t in opening_times)
    text = f"**Opening times:** {days}."
    general = get_appointment_general_settings(db)
    if general is not None:
        booking = (
            f"Bookings are {general.slotDuration}-minute slots, "
            f"{general.minBookAhead}–{general.maxBookAhead} days ahead"
        )
        if general.gradualAvailability:
            booking += ", released in blocks"
        text += f" {booking}."
    return text


def _section_appointments(db: Session) -> str:
    """D-2: Appointment types (active, in display order) with durations."""
    types = sorted(
        get_appointment_types(db, inactive=False),
        key=lambda t: t.orderIndex,
    )
    if not types:
        return ""
    listed = " · ".join(
        f"**{t.title}** ({t.duration} min) — {t.description}" for t in types
    )
    return f"**Appointments:** {listed}"


def _section_lending(db: Session) -> str:
    """D-2: Lending terms — contract types + the lease config.

    Deliberately does not state the grace/forfeit lengths: quoting an exact
    post-expiry deadline to a client reads as a green light to keep the bike longer.
    It conveys that a grace period exists (so a slightly-late return isn't a crisis)
    and that reminders go out, without a specific number.
    """
    contract_types = get_contract_types(db)
    if not contract_types:
        return ""
    lease_months = int(os.environ.get("CONTRACT_EXPIRE_MONTHS", 6))
    type_names = ", ".join(t.id for t in contract_types)
    return (
        f"**Lending:** {lease_months}-month lease, renewable in person after the "
        f"bike is checked. There's a grace period after the contract ends and we send "
        f"reminders, so a slightly-late return isn't a crisis. "
        f"Contract types: {type_names}."
    )


def _section_upcoming_closures(db: Session) -> str:
    """D-2: Upcoming closures (today onward, capped, with the note)."""
    today = datetime.now(timezone.utc).date()
    closed_days = get_closed_days(db, start_date=today)[:_UPCOMING_CLOSURES_CAP]
    if not closed_days:
        return ""
    listed = " · ".join(f"{d.date.isoformat()} — {d.note}" for d in closed_days)
    return f"**Upcoming closures:** {listed}."


def _section_parts(db: Session) -> str:
    """D-2: Parts stock (available only, capped).

    Prices are shown for **new** parts only — those are sold to a set policy
    (roughly cost-plus). Second-hand parts have a recommended retail price that
    is set case-by-case, so no price is given for them: the bot should treat
    used-part pricing as "ask a volunteer."
    """
    items = sorted(get_catalogue(db), key=lambda i: i.name)[:_PARTS_CAP]
    if not items:
        return ""
    listed = " · ".join(
        i.name.strip() + (f" £{i.recommendedRetailPrice / 100:g}" if not i.isSecondHand and i.recommendedRetailPrice else "")
        for i in items
    )
    return (
        f"**Parts (limited stock):** {listed}. New parts are sold at set prices; "
        "used parts are priced case-by-case, so for those — or on exact availability — "
        "point them to a volunteer."
    )


def _section_faq(db: Session) -> str:
    """D-2: FAQ (active, in display order)."""
    faqs = sorted(get_active_faq(db), key=lambda f: f.orderIndex)
    if not faqs:
        return ""
    listed = " · ".join(f"Q: {f.question} — A: {f.answer}" for f in faqs)
    return f"**FAQ:** {listed}"


def _section_about(db: Session) -> str:
    """D-2: About-us text (HTML stripped to plain text, capped)."""
    about = get_about_us(db)
    if about is None or not about.html:
        return ""
    text = re.sub(r"<[^>]+>", " ", about.html)
    text = re.sub(r"\s+", " ", text).strip()
    text = text[:_ABOUT_CHAR_CAP].rstrip()
    if not text:
        return ""
    return f"**About us:** {text}"


# Section order is render order; the tail is what the budget (D-4) drops first.
_DYNAMIC_SECTIONS = (
    _section_location,
    _section_opening_times,
    _section_appointments,
    _section_lending,
    _section_upcoming_closures,
    _section_parts,
    _section_faq,
    _section_about,
)


def build_dynamic_block(db: Session) -> str:
    """#505 D-1/D-2: assemble the dynamic block from the site's database.

    Each _section_* function fetches and formats one section and returns ""
    when its source is empty; the non-empty sections are appended, in order,
    under the D-3 header. Best-effort (D-5): any failure returns "" — the
    agent then runs on the persona alone, and a reply is never blocked.
    """
    try:
        sections = [section(db) for section in _DYNAMIC_SECTIONS]
    except Exception as exc:  # D-5: assembly must never break a reply
        print(f"LLM dynamic block failed: {exc}")
        return ""

    sections = [s for s in sections if s]
    while len(sections) > 1 and sum(len(s) for s in sections) > _DYNAMIC_BLOCK_CHAR_BUDGET:
        sections.pop()  # D-4: over budget — drop from the tail

    if not sections:
        return ""
    return _DYNAMIC_BLOCK_HEADER + "\n\n" + "\n\n".join(sections)


def _system_prompt(db: Session, settings) -> str:
    """#505 D-1: the full system prompt — the persona (site row or core, AS-5)
    plus the dynamic block (D-1/D-2) when the site's database provides one."""
    prompt = _persona(settings)
    block = build_dynamic_block(db)
    if block:
        prompt = prompt + "\n\n" + block
    return prompt


def _closed_set(intent_rows, faq_targets) -> str:
    """The closed set the model may classify into: the enabled intents plus the
    active FAQs, and the "or none" opt-out. Always appended to the classification
    prompt (whether or not the admin overrode the instructions) so the model
    always sees exactly what it may choose AND can always decline; the validator
    enforces the same set (C-3), so the list, the instructions, and the validation
    can't drift apart.

    `faq_targets` is (key, question, answer); only the key and question go in the
    prompt — the answer is the routed reply, resolved in crud.chats.resolve_reply.
    """
    sections = ["Classify into exactly one of these:"]
    if intent_rows:
        lines = []
        for row in intent_rows:
            desc = (row.whenToUse or "").strip()
            lines.append(f"- {row.name}: {desc}" if desc else f"- {row.name}")
        sections.append("\n".join(lines))
    if faq_targets:
        faq_lines = "\n".join(f"- {key}: {question}" for key, question, _answer in faq_targets)
        sections.append(faq_lines)
    sections.append(f'or "{NONE_INTENT}" if it fits none of them.')
    return "\n".join(sections)


def _default_classification_prompt() -> str:
    """A-10/A-11: code-default classification instructions (a strict
    machine-parseable JSON contract). Deliberately does NOT list the intents —
    the closed set is always appended separately (_intent_listing) so a custom
    Classification Prompt never silently drops the intent names the model must
    pick from."""
    return (
        "You are a message classifier, not a conversational assistant. "
        "Do not answer the customer. "
        "Classify their latest message into exactly one of the intents listed below. "
        'Respond with JSON only: {"intent": "<one of the above>"}'
    )


def _classification_instructions(settings) -> str:
    """A-10: LlmSettings.classificationPrompt override, else the code default
    instructions (the closed intent set is always appended separately in classify)."""
    prompt = getattr(settings, "classificationPrompt", None)
    if prompt and prompt.strip():
        return prompt.strip()
    return _default_classification_prompt()


def _extract_intent(raw, valid_names) -> str:
    """Reduce the model's output to a valid intent (one of ``valid_names``), else
    the none sentinel (A-6/A-12).

    Prefers a well-formed {"intent": "..."} object, then a bare known intent word,
    then a lenient pull from a noisy/fenced response. Anything unrecognised degrades
    to NONE_INTENT rather than raising (best-effort).
    """
    valid = frozenset(n.lower() for n in valid_names) | {NONE_INTENT}
    text = raw.strip() if isinstance(raw, str) else ("" if raw is None else str(raw).strip())
    if not text:
        return NONE_INTENT

    # 1) strict: a JSON object with an "intent" key whose value is in the closed set
    try:
        data = json.loads(text)
        if isinstance(data, dict) and isinstance(data.get("intent"), str):
            intent = data["intent"].strip().lower()
            if intent in valid:
                return intent
    except (ValueError, TypeError):
        pass

    # 2) lenient: the whole response is a single known intent word
    if text.lower() in valid:
        return text.lower()

    # 3) lenient: pull "intent": "<value>" out of a fenced/noisy response
    match = re.search(r'"?intent"?\s*[:=]\s*"?([a-z0-9_]+)"?', text, re.IGNORECASE)
    if match and match.group(1).lower() in valid:
        return match.group(1).lower()

    return NONE_INTENT


async def list_models() -> list[str]:
    """Return the names of the models available on the Ollama backend (A-8).

    Best-effort (A-13): any failure — backend not configured, unreachable,
    a timeout, a non-2xx status, or an unexpected response shape — yields an
    empty list rather than an error, so the admin UI can render an empty model
    picker (API-3: the endpoint must never 500).
    """
    if not LLM_BASE_URL:
        return []

    url = f"{LLM_BASE_URL}/api/tags"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()

        models = payload.get("models", []) if isinstance(payload, dict) else []
        names = [
            model["name"]
            for model in models
            if isinstance(model, dict) and isinstance(model.get("name"), str) and model.get("name")
        ]
        return sorted(names)
    except Exception as exc:
        print(f"Failed to list LLM models from {url}: {exc}")
        return []


async def converse(db: Session, messages, context: dict | None = None) -> str | None:
    """Generate a free-form reply to a debounced burst of messages (A-7).

    The Agent is the only component that invokes the LLM (A-1); Ollama is the
    backend (A-2). The active config — model and persona — is read from
    LlmSettings per operation (A-3); the persona falls back to a code-defined
    default when blank (A-10), and the dynamic block of workshop facts is
    assembled from the site's database at call time (#505 D-1). When no model
    is configured the Agent is inactive and makes no LLM call (A-4).

    Best-effort (A-13): an unconfigured backend, a dead backend, a timeout, or
    an empty result all yield None — never an exception to the caller — so the
    base human chat is never blocked or degraded.

    Args:
        db: session used to read the active LlmSettings row (A-3).
        messages: a batch of messages (A-9) — strings, or dicts/objects exposing
            their text via `content` / `body` / `text`.
        context: the caller's per-org / per-thread context (A-9). Accepted so the
            signature matches the shared contract; reserved for future use.
    """
    settings = get_llm_settings(db=db)

    model = _active_model(settings)
    if not model:
        return None  # A-4: no model configured -> inactive, no LLM call
    if not LLM_V1_BASE_URL:
        return None  # A-13: backend not configured -> no-op

    prompt = _compose_user_prompt(messages)
    if not prompt:
        return None  # nothing to reply to

    agent = Agent(
        OllamaModel(model, provider=OllamaProvider(base_url=LLM_V1_BASE_URL)),
        system_prompt=_system_prompt(db, settings),
    )
    try:
        # #501 C-15: converse keeps the model's default thinking (on) — classify() is
        # the only call that turns it off (_CLASSIFY_NO_THINKING). Leave this
        # asymmetry in place: future reasoning work may rely on converse thinking
        # by default.
        result = await agent.run(prompt, timeout=_LLM_TIMEOUT)
    except Exception as exc:  # A-13: any failure -> no-op
        print(f"LLM converse failed: {exc}")
        return None

    output = getattr(result, "output", None)
    if isinstance(output, str) and output.strip():
        return output.strip()
    return None


async def classify(db: Session, messages, context: dict | None = None) -> str | None:
    """Classify a debounced burst of messages into an intent (A-6 / #501 C-1).

    The Agent is the only component that invokes the LLM (A-1). The active config —
    model, shared persona, and classification instructions — is read from
    LlmSettings per operation (A-3); the classification set comes from the site's
    `chat_intents` table (C-9/C-3) plus its active FAQs, and the instructions fall
    back to a code-defined default (A-10). The dynamic block of workshop facts is
    assembled from the site's database at call time (#505 D-1).
    When no model is configured the Agent is inactive and makes no LLM call (A-4).

    Returns one of the site's enabled intent names or an active FAQ key (a slug of
    its question), or the NONE_INTENT sentinel when the model can't map the message
    to either. Returns None when no LLM call is made (no model, unconfigured/dead
    backend, timeout) — best-effort per A-13 — so the caller falls back to the base
    human chat.

    Args:
        db: session used to read the active LlmSettings row and the enabled
            intents (A-3 / C-9).
        messages: a batch of messages (A-9) — strings, or dicts/objects exposing
            their text via `content` / `body` / `text`.
        context: the caller's per-org / per-thread context (A-9). Accepted so the
            signature matches the shared contract; reserved for future use.
    """
    # Lazy import: the intent set now lives in crud.intents (the DB-backed table).
    # Imported at call time so module-load order can never create a crud<->services
    # import cycle (crud.chats imports this module, and this reaches back into crud).
    from app.crud.intents import get_enabled_intents, get_active_faq_targets

    settings = get_llm_settings(db=db)

    model = _active_model(settings)
    if not model:
        return None  # A-4: no model configured -> inactive, no LLM call
    if not LLM_V1_BASE_URL:
        return None  # A-13: backend not configured -> no-op

    prompt = _compose_user_prompt(messages)
    if not prompt:
        return None  # nothing to classify

    intent_rows = get_enabled_intents(db)
    faq_targets = get_active_faq_targets(db)  # [(key, question, answer)]
    if not intent_rows and not faq_targets:
        # Nothing to classify into -> no LLM call. Return the none sentinel (not
        # None) so the caller routes to the free-form fallback rather than making
        # a pointless LLM call.
        return NONE_INTENT

    valid_names = {row.name for row in intent_rows} | {key for key, _q, _a in faq_targets}

    # classify is a routing task: it needs the classifier role (the instructions)
    # and the closed set to route into — NOT the dynamic block of workshop facts,
    # which only matters when composing an answer. Dropping it here cuts the prompt
    # the model pre-fills (and so the latency / variance) on the common client path;
    # converse() keeps the full block for free-form answers. The persona is kept so
    # the model still knows the workshop context it's routing within.
    system_prompt = (
        _persona(settings)
        + "\n\n" + _classification_instructions(settings)
        + "\n\n" + _closed_set(intent_rows, faq_targets)
    )
    
    if not PRODUCTION:
        print("system prompt:", system_prompt)
        print("prompt:", prompt)

    agent = Agent(
        OllamaModel(model, provider=OllamaProvider(base_url=LLM_V1_BASE_URL)),
        system_prompt=system_prompt,
    )
    try:
        # #501: thinking OFF for this routing call (see _CLASSIFY_NO_THINKING).
        result = await agent.run(
            prompt,
            model_settings=_CLASSIFY_NO_THINKING,
            timeout=_LLM_TIMEOUT,
        )
    except Exception as exc:  # A-13: any transport failure -> no-op
        print(f"LLM classify failed: {exc}")
        return None

    return _extract_intent(getattr(result, "output", None), valid_names)


# --- #503: the booking flow's conversation step (B-2..B-5) ---
#
# The flow itself — its state, budgets, messages, and the booking — lives in
# crud.booking_flow. This is the LLM side only: one call per burst, given the
# stage and the flow's data, it returns the step's DECISION (which type /
# whether it's confirmed / which slot / a specific ask / re-offer / abort).
# It does not write the customer-facing text — the app composes every message
# from fixed strings (the owner wants the AI's own prose minimal), so this
# model never has to generate a reply.
# B-3: only the Agent invokes the LLM; the closed sets (active types, offered
# slots) are passed in and the decision is validated against them here, so the
# LLM can never name a type or slot that doesn't exist (the same no-drift
# pattern as classify's _extract_intent).
#
# The LLM sees no conversation history (a single turn, like converse/classify):
# everything it needs — the proposed type, the offered slots — is assembled
# into the system prompt from the flow's data by the caller.

STAGE_ELICITING = ChatActionFlowStage.BOOKING_ELICITING
STAGE_AWAITING_SLOT_CHOICE = ChatActionFlowStage.BOOKING_AWAITING_SLOT_CHOICE
STAGE_AWAITING_CONFIRM = ChatActionFlowStage.BOOKING_AWAITING_CONFIRM


def _extract_json_object(raw) -> dict | None:
    """Reduce the model's output to a JSON object, leniently (fenced or noisy
    responses tolerated), or None when there is no object in it."""
    text = raw.strip() if isinstance(raw, str) else ("" if raw is None else str(raw).strip())
    if not text:
        return None
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except (ValueError, TypeError):
        pass
    # Lenient: the first balanced {...} block that parses as an object.
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        candidate = json.loads(text[start:i + 1])
                        if isinstance(candidate, dict):
                            return candidate
                    except (ValueError, TypeError):
                        pass
                    break
        start = text.find("{", start + 1)
    return None


def _slot_ref(value) -> dict | None:
    """A {date, time} string pair, or None when the shape is wrong."""
    if not isinstance(value, dict):
        return None
    date = value.get("date")
    time = value.get("time")
    if not isinstance(date, str) or not isinstance(time, str):
        return None
    return {"date": date.strip(), "time": time.strip()}


def _slot_minutes(time: str) -> int | None:
    """'HH:MM' or 'HH:MM:SS' to minutes-of-day, or None (lenient time compare)."""
    parts = time.split(":")
    if len(parts) not in (2, 3):
        return None
    try:
        return int(parts[0]) * 60 + int(parts[1])
    except ValueError:
        return None


def _slot_in_offered(slot: dict | None, offered) -> bool:
    """Whether a slot is one of the ones actually offered (B-5: the pick is
    validated against exactly the offered set)."""
    if slot is None:
        return False
    for entry in offered or []:
        if not isinstance(entry, dict):
            continue
        if entry.get("date") == slot["date"] and _slot_minutes(str(entry.get("time", ""))) == _slot_minutes(slot["time"]):
            return True
    return False


def _booking_type_listing(db: Session) -> str:
    """The closed set for stage ELICITING: the shop's active appointment
    types, id | title | duration | description (description is what the
    type is FOR — the primary signal for the pick; the decision rules live
    in the prompt, not here)."""
    types = sorted(get_appointment_types(db, inactive=False), key=lambda t: t.orderIndex)
    lines = []
    for t in types:
        line = f"- {t.id} | {t.title} | {t.duration} min"
        description = (t.description or "").strip()
        if description:
            line += f" | {description}"
        lines.append(line)
    return "\n".join(lines)


def _booking_slot_listing(offered) -> str:
    """The closed set for stage AWAITING_SLOT_CHOICE: the slots offered so
    far, exactly as stored (ISO date + time) for the LLM to copy back."""
    lines = []
    for entry in offered or []:
        if isinstance(entry, dict) and entry.get("date") and entry.get("time"):
            lines.append(f"- {entry['date']} {entry['time']}")
    return "\n".join(lines)


def _booking_step_json_contract(stage: ChatActionFlowStage) -> str:
    # The model returns the decision ONLY (no prose) - the app composes the
    # customer-facing message from fixed strings.
    if stage == STAGE_ELICITING:
        return (
            'Respond with JSON only: {"type": "<one id from the list above, or empty string>", '
            '"confirmed": false, "aborted": false}'
        )
    if stage == STAGE_AWAITING_SLOT_CHOICE:
        return (
            'Respond with JSON only: {"choice": {"date": "...", "time": "..."} or null, '
            '"specificAsk": {"date": "...", "time": "..."} or null, "reoffer": false, "aborted": false}'
        )
    return (
        'Respond with JSON only: {"confirmed": false, "denied": false, '
        '"newChoice": {"date": "...", "time": "..."} or null, '
        '"specificAsk": {"date": "...", "time": "..."} or null, "aborted": false}'
    )


def _booking_step_system_prompt(db: Session, settings, stage: ChatActionFlowStage, data: dict) -> str:
    """The booking step's system prompt: the shared persona, the stage's rules,
    and the stage's closed set (active types, or the offered slots). The LLM
    returns the decision only (no prose - the app composes the message). It
    has no conversation history, so the flow's progress so far (the proposed
    type) is included from the flow's data."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    base = (
        _persona(settings)
        + "\n\n"
        + "You are helping this customer book a workshop appointment. "
        + f"Today is {today}. You only decide; you do not write any customer-facing text."
    )

    if stage == STAGE_ELICITING:
        proposed = (data.get("appointmentTypeId") or "").strip()
        proposed_line = ""
        if proposed:
            proposed_line = f"\nYou already proposed this type in a previous message: {proposed}.\n"
        return (
            base
            + "\n"
            + "Available appointment types (id | title | duration | description):\n"
            + (_booking_type_listing(db) or "- (none available)")
            + proposed_line
            + "\nDecide this customer message:\n"
            + "- Choose the single best-fitting type by its description; when two fit equally well, "
            "prefer the longer appointment. Put its id in \"type\".\n"
            + "- If the need is unclear and you cannot pick a type, leave \"type\" as an empty string.\n"
            + "- Set \"confirmed\" to true ONLY when a type was already proposed earlier and the "
            "customer is now accepting it (repeat that type's id in \"type\").\n"
            + "- If the customer drops the booking (e.g. \"never mind\"), set \"aborted\" to true.\n"
            + "- Never invent an appointment type id.\n\n"
            + _booking_step_json_contract(stage)
        )

    if stage == STAGE_AWAITING_CONFIRM:
        pending = data.get("pendingSlot") or {}
        pending_line = ""
        if pending.get("date") and pending.get("time"):
            day = datetime.strptime(str(pending["date"]), "%Y-%m-%d")
            pending_line = (
                f"\nThe pending request: a booking on {day.strftime('%a %d %b')} "
                f"at {str(pending['time'])[:5]}.\n"
            )
        slot_type = None
        type_id = (data.get("appointmentTypeId") or "").strip()
        if type_id:
            slot_type = get_appointment_type(db=db, appointment_type_id=type_id)
        return (
            base
            + "\n"
            + (f"The appointment type being booked: {slot_type.title} ({slot_type.duration} min).\n" if slot_type else "")
            + pending_line
            + "\nOffered slots (copy the date and time EXACTLY as listed, only for a different-slot ask):\n"
            + (_booking_slot_listing(data.get("offeredSlots")) or "- (none on offer yet)")
            + "\nDecide this customer message (set exactly ONE of confirmed / denied / newChoice / specificAsk, or none):\n"
            + "- confirmed: the customer accepts the pending request.\n"
            + "- denied: the customer declines it.\n"
            + "- newChoice: the customer names a different one of the offered slots instead (exact strings; "
            "if more than one could fit, the most recent offer - listed last - is the likelier one).\n"
            + "- specificAsk: the customer asks for a slot not in the list (your best resolution to a "
            "concrete date and time; the workshop will check whether it is free).\n"
            + "- If the customer drops the booking entirely (e.g. \"never mind\"), set \"aborted\" to true.\n"
            + "- Never invent a slot that is not in the list.\n\n"
            + _booking_step_json_contract(stage)
        )

    # STAGE_AWAITING_SLOT_CHOICE
    slot_type = None
    type_id = (data.get("appointmentTypeId") or "").strip()
    if type_id:
        slot_type = get_appointment_type(db=db, appointment_type_id=type_id)
    return (
        base
        + "\n"
        + (f"The appointment being booked: {slot_type.title} ({slot_type.duration} min).\n" if slot_type else "")
        + "\nOffered slots (copy the date and time EXACTLY as listed when the customer picks one):\n"
        + (_booking_slot_listing(data.get("offeredSlots")) or "- (none on offer yet)")
        + "\nDecide this customer message:\n"
        + "- If the customer picks one of the offered slots, set \"choice\" to that slot (exact strings).\n"
        + "- If the customer refers to a slot by its position (e.g. 'the 3rd at 6:15') and more than one "
        "offered slot could fit, resolve it to the single most likely one: the offers are listed oldest "
        "first, so the customer is most likely pointing at a slot from the most recent offer (last).\n"
        + "- If the customer asks for a specific slot not in the list, set \"specificAsk\" to your best "
        "resolution of it as a concrete date and time; the workshop will check whether it is free.\n"
        + "- If the customer says none of the offered slots suit, set \"reoffer\" to true.\n"
        + "- If the customer drops the booking, or says they meant a different kind of appointment, "
        "set \"aborted\" to true.\n"
        + "- Otherwise (a question, a tangent), leave \"choice\", \"specificAsk\" and \"reoffer\" all "
        "empty/false.\n"
        + "- Never invent a slot that is not in the list.\n\n"
        + _booking_step_json_contract(stage)
    )


def _sanitize_booking_step(raw, stage: ChatActionFlowStage, data: dict, db: Session) -> dict | None:
    """Reduce the model's output to the booking step's validated decision, or
    None when there is no usable object (best-effort, like _extract_intent).
    The model returns decisions only (no prose), so a parsed object is a valid
    step even when every decision field is empty; each decision field that
    fails its closed-set check is dropped rather than raising."""
    parsed = _extract_json_object(raw)
    if parsed is None:
        return None

    out = {
        "type": None,
        "confirmed": False,
        "denied": False,
        "choice": None,
        "newChoice": None,
        "specificAsk": None,
        "reoffer": False,
        "aborted": parsed.get("aborted") is True,
    }

    if stage == STAGE_ELICITING:
        type_id = parsed.get("type")
        if isinstance(type_id, str) and type_id.strip():
            # B-3: the picked type must be one of the shop's active types.
            out["type"] = type_id.strip() if get_appointment_type(
                db=db, appointment_type_id=type_id.strip()) is not None else None
        # "confirmed" stands on its own: the flow settles it against the type
        # proposed in the previous turn (it may even be empty - "yes" is enough).
        out["confirmed"] = parsed.get("confirmed") is True
    elif stage == STAGE_AWAITING_SLOT_CHOICE:
        offered = data.get("offeredSlots") or []
        choice = _slot_ref(parsed.get("choice"))
        out["choice"] = choice if _slot_in_offered(choice, offered) else None
        # specificAsk is shape-checked only: the flow checks it live against
        # availability before acting on it (a not-in-list ask is legit).
        out["specificAsk"] = _slot_ref(parsed.get("specificAsk"))
        out["reoffer"] = parsed.get("reoffer") is True
    else:
        # STAGE_AWAITING_CONFIRM: the yes/no on the pending request.
        offered = data.get("offeredSlots") or []
        new_choice = _slot_ref(parsed.get("newChoice"))
        out["newChoice"] = new_choice if _slot_in_offered(new_choice, offered) else None
        out["specificAsk"] = _slot_ref(parsed.get("specificAsk"))
        out["confirmed"] = parsed.get("confirmed") is True
        out["denied"] = parsed.get("denied") is True

    return out


async def booking_step(
    db: Session,
    *,
    stage: ChatActionFlowStage,
    data: dict,
    messages,
) -> dict | None:
    """#503: one step of the booking flow conversation (B-2..B-5).

    Given the flow's stage and data, return the step's decision, reduced to a
    validated shape (see _sanitize_booking_step): stage-dependent keys
    (type / confirmed when eliciting; choice / specificAsk / reoffer when
    awaiting the slot choice), plus aborted. The model writes no prose - the
    app composes the customer-facing message. The closed sets are validated
    here (B-3), so the flow can trust every key it receives.

    Best-effort (A-13): an unconfigured backend, a dead backend, a timeout,
    or an unusable result all yield None - never an exception - so the flow
    says nothing, consumes no turn, and the base chat continues.

    Args:
        db: session used to read the active LlmSettings row and the shop's
            active appointment types (A-3 / B-3).
        stage: the flow's current stage (a ChatActionFlowStage).
        data: the flow's data payload (appointmentTypeId / offeredSlots / ...),
            as stored on the flow row.
        messages: a batch of messages (A-9).
    """
    settings = get_llm_settings(db=db)

    model = _active_model(settings)
    if not model:
        return None  # A-4: no model configured -> inactive, no LLM call
    if not LLM_V1_BASE_URL:
        return None  # A-13: backend not configured -> no-op

    prompt = _compose_user_prompt(messages)
    if not prompt:
        return None  # nothing to reply to

    system_prompt = _booking_step_system_prompt(db, settings, stage, data or {})

    if not PRODUCTION:
        print("booking_step system prompt:", system_prompt)
        print("booking_step prompt:", prompt)

    agent = Agent(
        OllamaModel(model, provider=OllamaProvider(base_url=LLM_V1_BASE_URL)),
        system_prompt=system_prompt,
    )
    try:
        # A conversational step (not a routing task): keep the model's default
        # thinking, as converse() does.
        result = await agent.run(prompt, timeout=_LLM_TIMEOUT)
    except Exception as exc:  # A-13: any failure -> no-op
        print(f"LLM booking_step failed: {exc}")
        return None

    return _sanitize_booking_step(getattr(result, "output", None), stage, data or {}, db)
