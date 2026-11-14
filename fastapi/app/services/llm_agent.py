import json
import os
import re
from datetime import datetime, timezone

import httpx
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from sqlalchemy.orm import Session

from app.crud.appointments import get_appointment_types
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
_LLM_TIMEOUT = 60.0

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

# A-12: the authoritative, closed set of intents the Agent may classify a message
# as. This tuple is the single source of truth: the code-default classification
# prompt is generated from it and classify() validates the model's output against
# it, so the set, the instructions, and the validation can't drift apart. To add an
# intent, append it here — the prompt and validation pick it up automatically.
# (Initial working set; to be extended to the full set.)
INTENTS = ("booking", "hours", "repair_request", "parts_inquiry", "other")

# A-6: the "unmatched" sentinel — returned when the model can't map a message to a
# real intent. Distinct from None, which means "no LLM was run" (A-4 / A-13).
NONE_INTENT = "none"

# The closed set the model is allowed to return: the real intents plus the sentinel.
_VALID_INTENTS = frozenset(INTENTS) | {NONE_INTENT}


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


def _default_classification_prompt() -> str:
    """A-10/A-11: code-default classification instructions, derived from INTENTS.

    Defines the closed intent set and a strict machine-parseable JSON contract.
    Because the allowed list is generated from INTENTS, extending the set never
    desynchronises the instructions from the validation.
    """
    allowed = ", ".join(INTENTS)
    return (
        "You are a message classifier, not a conversational assistant. "
        "Do not answer the customer. "
        f"Classify their latest message into exactly one intent: {allowed}, "
        f"or \"{NONE_INTENT}\" if it fits none of them. "
        "Respond with JSON only: {\"intent\": \"<one of the above>\"}"
    )


def _classification_instructions(settings) -> str:
    """A-10: LlmSettings.classificationPrompt, else the code default."""
    prompt = getattr(settings, "classificationPrompt", None)
    if prompt and prompt.strip():
        return prompt.strip()
    return _default_classification_prompt()


def _extract_intent(raw) -> str:
    """Reduce the model's output to a valid intent, else the none sentinel (A-6/A-12).

    Prefers a well-formed {"intent": "..."} object, then a bare known intent word,
    then a lenient pull from a noisy/fenced response. Anything unrecognised degrades
    to NONE_INTENT rather than raising (best-effort).
    """
    text = raw.strip() if isinstance(raw, str) else ("" if raw is None else str(raw).strip())
    if not text:
        return NONE_INTENT

    # 1) strict: a JSON object with an "intent" key whose value is in the closed set
    try:
        data = json.loads(text)
        if isinstance(data, dict) and isinstance(data.get("intent"), str):
            intent = data["intent"].strip().lower()
            if intent in _VALID_INTENTS:
                return intent
    except (ValueError, TypeError):
        pass

    # 2) lenient: the whole response is a single known intent word
    if text.lower() in _VALID_INTENTS:
        return text.lower()

    # 3) lenient: pull "intent": "<value>" out of a fenced/noisy response
    match = re.search(r'"?intent"?\s*[:=]\s*"?([a-z0-9_]+)"?', text, re.IGNORECASE)
    if match and match.group(1).lower() in _VALID_INTENTS:
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
        result = await agent.run(prompt, timeout=_LLM_TIMEOUT)
    except Exception as exc:  # A-13: any failure -> no-op
        print(f"LLM converse failed: {exc}")
        return None

    output = getattr(result, "output", None)
    if isinstance(output, str) and output.strip():
        return output.strip()
    return None


async def classify(db: Session, messages, context: dict | None = None) -> str | None:
    """Classify a debounced burst of messages into an intent (A-6).

    The Agent is the only component that invokes the LLM (A-1). The active config —
    model, shared persona, and classification instructions — is read from
    LlmSettings per operation (A-3); the instructions fall back to a code-defined
    default when blank (A-10) and carry a strict machine-parseable contract (A-11).
    The dynamic block of workshop facts is assembled from the site's database at
    call time (#505 D-1). When no model is configured the Agent is inactive and
    makes no LLM call (A-4).

    Returns one of INTENTS, or the NONE_INTENT sentinel when the model can't map the
    message to a real intent. Returns None when no LLM call is made (no model,
    unconfigured/dead backend, timeout) — best-effort per A-13 — so the caller falls
    back to the base human chat.

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
        return None  # nothing to classify

    # A-10 / #505 D-1: persona (site row or core) + dynamic block for both
    # routes; classify adds the classification contract (A-11).
    system_prompt = _system_prompt(db, settings) + "\n\n" + _classification_instructions(settings)

    agent = Agent(
        OllamaModel(model, provider=OllamaProvider(base_url=LLM_V1_BASE_URL)),
        system_prompt=system_prompt,
    )
    try:
        result = await agent.run(prompt, timeout=_LLM_TIMEOUT)
    except Exception as exc:  # A-13: any transport failure -> no-op
        print(f"LLM classify failed: {exc}")
        return None

    return _extract_intent(getattr(result, "output", None))
