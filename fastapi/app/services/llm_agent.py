import json
import os
import re

import httpx
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from sqlalchemy.orm import Session

from app.crud.settings import get_llm_settings

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

# A-10 / A-11: code-defined default persona — neutral and domain-focused.
# ORG-1: no org-specific name is hardcoded here. The admin can override via
# LlmSettings.systemPrompt; an env-injected org name (an open question on the
# ticket) would be folded into this default later without breaking ORG-1.
_DEFAULT_PERSONA = (
    "You are a helpful assistant for a community bike repair workshop. "
    "You answer customers' questions about bike repairs, booking appointments, "
    "parts, and opening hours. Be friendly, clear, and concise. "
    "If you don't know the answer, say so rather than guessing."
)

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
    default when blank (A-10). When no model is configured the Agent is
    inactive and makes no LLM call (A-4).

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
        system_prompt=_persona(settings),
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
    When no model is configured the Agent is inactive and makes no LLM call (A-4).

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

    # A-10: the shared persona alone for converse; persona + classification
    # instructions for classify.
    system_prompt = _persona(settings) + "\n\n" + _classification_instructions(settings)

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
