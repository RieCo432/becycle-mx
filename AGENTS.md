# AGENTS.md

Bike-workshop management app: FastAPI + PostgreSQL backend in `fastapi/`, Vue 3 + Vite frontend in `vuejs/`. Setup docs: `README.md` (env + run steps), `CONTRIBUTING.md` (branch/PR flow), `vuejs/README.md`.

The same codebase serves multiple bike shops (becycle-mx, belfastcyclecoop-mx); org identity comes from env (`OFFICIAL_NAME`, `COMMON_NAME`, `DOMAIN` in `secrets/organisation.env`). Do not hardcode org-specific names/text.

## Hard rules

- **Never commit anything.** No `git commit` (or push) — for security reasons. Leave changes in the working tree for the owner to review.
- **Avoid accessing the database if possible.** Do not start the API, run migrations, or run tests against Postgres unless there is no other way to verify the change.
- **No write operations on GitHub without explicit, per-action consent.** Reads (`gh issue view`, API GETs, etc.) are fine. Any write — commenting on or editing an issue, opening/merging a PR, pushing — requires me to ask about that specific action and get a clear go-ahead first; a past "yes" does not carry over.

## Layout

- `fastapi/app/main.py` — composition root: registers all routers and runs startup maintenance (permission sync, pruning, and — when `PRODUCTION=true` — email sends) **at import time**.
- `fastapi/app/routers/` — one module per domain; `crud/` business logic; `models/` + `schemas/`; `database/db.py` (SQLAlchemy engine, built from env vars).
- `fastapi/app/tests/` — pytest. Fixtures live in `pytestFixtures.py` and are pulled in with `from app.tests.pytestFixtures import *` (there is no `conftest.py`); new fixtures go in that file.
- `vuejs/src/requests/index.js` — the **only** API client; all endpoint calls go through it.
- `secrets/*.env` feed the Docker containers; `fastapi/local-api.env` feeds local API/alembic; `vuejs/.env` feeds the frontend build/dev server.

## Commands

- Full stack: `docker compose up` (services: `postgres`, `api`, `web`). Postgres only: `docker compose up -d postgres`.
- API (from `fastapi/`): `uvicorn app.main:app --reload --env-file local-api.env` (README: root-level `venv`, or the `fastapi/venv` — both gitignored).
- Migrations (from `fastapi/`): `alembic upgrade head`; new: `alembic revision --autogenerate -m "what changed"` — then review the generated file in `fastapi/alembic/versions/`.
- Frontend (from `vuejs/`): `yarn` → `yarn dev`; `yarn lint` (eslint `--fix`); `yarn build`. There is no typecheck script; JS + ESLint only.
- Tests (from `fastapi/`): `pytest app/tests/routers/user.py::test_get_user_token_correct_password` (or a file/node id) — *currently known-broken, see Testing quirks*.

## Environment gotchas

- Create from templates: `secrets/api.env`, `secrets/postgres.env`, `secrets/organisation.env` (required by `compose.yaml` but not listed in README), `fastapi/local-api.env`, `vuejs/.env`. `local-api.env` must mirror the secrets files and also set `POSTGRES_HOST` (localhost for dev).
- The backend reads env vars at import time and there is **no dotenv loading in app code** — only `alembic/env.py` auto-loads `fastapi/local-api.env`. `uvicorn --env-file` and pytest do not: for pytest, export the vars from `local-api.env` into your shell first.
- Python 3.11 (`.python-version` = 3.11.17, matches the Docker image).

## Testing quirks

- **`demo_data.py` and the unit tests are known-broken — ignore them for now.** Don't rely on their output, don't treat their failures as blocking, and don't change them to force them green. Owner is aware and plans to fix them later.
- Tests run against a **real local Postgres** and **wipe it**: `pytestFixtures.py` runs `Base.metadata.create_all` + `delete_all()` (deletes nearly every table) at import. Never point this at a database with data you need.
- Fixtures are plain pytest fixtures imported explicitly per test file — they are not auto-discovered.

## Migrations

- The Docker API entrypoint runs `alembic upgrade head` on every container start (`fastapi/Dockerfile`); a broken migration breaks deploy.
- Migration filenames use a custom `YYYY_MM_DD_HHMMSS_slug` template (`alembic.ini`); slugs are capped at 234 chars.

## Frontend quirks

- API base URL is built from `VITE_API_PROTOCOL/HOST/PORT/SUBDIR` in `src/requests/index.js`. In dev the browser calls the API directly; CORS is open unless `PRODUCTION=true`.
- For Web NFC development you must enable `https: true` and the commented-out `mkcert()` plugin in `vite.config.js` (browser NFC requires a secure context).
- The `"proxy"` field in `vuejs/package.json` is a leftover from Vue CLI and is ignored by Vite.

## CI/CD and branching

- No test/lint CI. The only workflow deploys on push to `main`: SSH to a Raspberry Pi, `git pull` + `docker compose build` + service restarts for both orgs.
- `dev` is the default/integration branch; feature branches come off `dev`, named `#<issue>-slug` (e.g. `#53-eslint-fixes`); PRs go to `dev`. A CI check **rejects any PR to `main` that does not come from `dev`** — main merges happen only after dev is verified.
- Prefix commits and branches with the GitHub issue number.

## Ops notes

- The recurring cleanup SQL in README (expired logins, dormant liabilities, orphan culls) is run via cron **on the server**, not by the app.
- `fastapi/serve.sh`: set `SEGFAULT_DEBUG=1` in the api service env to get native backtraces from `libSegFault` on crashes.
- Email goes out via Gmail SMTP app passwords (`GOOGLE_ACCOUNT`/`GOOGLE_APP_PASSWORD`); optional for local dev.
