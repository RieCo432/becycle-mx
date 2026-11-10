import os

import httpx

# The LLM Agent is the only part of the app that talks to the LLM backend (A-1).
# Everything that needs a model — listing available ones now, and classification
# / conversation later — goes through this module, so the rest of the codebase
# never sees httpx, Ollama, or Pydantic AI directly.
#
# ENV-1 / ENV-2: the Ollama backend's host and port. Read with .get (not []) so a
# missing value degrades to "no LLM" (an empty model list) instead of raising at
# import time — the Agent is best-effort (A-13), not a hard startup dependency.
LLM_HOST = os.environ.get('LLM_HOST', '')
LLM_PORT = os.environ.get('LLM_PORT', '11434')

# Shared origin for both the native Ollama API (GET /api/tags, used below) and the
# OpenAI-compatible API (…/v1) that classify()/converse() will use later. Keeping
# the construction in one place means both honour LLM_HOST / LLM_PORT identically.
LLM_BASE_URL = f"http://{LLM_HOST}:{LLM_PORT}" if LLM_HOST else ""

# Bounded so a hung or unreachable backend can't stall the request (A-13).
_TIMEOUT = httpx.Timeout(15.0, connect=5.0)


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
    except Exception as e:
        print(f"Failed to list LLM models from {url}: {e}")
        return []
