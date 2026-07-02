# ARCHITECTURE.MD — mexit

Bootstrapped from `~/projects/claude-global-tools/UniformProject.md`, minus
the mobile stack (this project has no mobile app). See
`development-plans/PLAN-chore-bootstrap-uniform-structure.md` for the
rationale behind every divergence noted here.

## Layout

```
backend/
  app/                   # importable package — everything deployed lives here
    main.py              # FastAPI() instance, lifespan, /health, static mount
    config.py            # pydantic-settings singleton
    database.py          # engine, SessionLocal, get_db
    dependencies.py      # get_current_user — TEST_AUTH_BYPASS + lazy Firebase
    models.py             # SQLAlchemy ORM models (User only, so far)
    schemas.py            # Pydantic request/response models
    routers/              # one file per resource — empty, no resources yet
    services/             # one file per resource — empty, no resources yet
  tests/
    test_api.py           # integration — owned exclusively by /test-review
    unit/                 # dev-owned, add alongside business logic changes
    conftest.py            # sets TEST_AUTH_BYPASS=true; TEST_DATABASE_URL override
  scripts/                # one-off/migration scripts
  requirements.txt         # pinned exact versions
frontend/
  src/
    api/                  # thin HTTP client wrappers, one file per resource
    components/
    context/               # AuthContext (Firebase auth state)
    hooks/
    pages/
    utils/                 # pure functions — primary unit test target
    __tests__/              # Vitest — currently one App.tsx smoke test (see
                             # "Divergence" below; utils/ and api/ are empty)
    firebase.ts
    App.tsx
    main.tsx
```

No `mobile/` — intentional, this project has no mobile app.

## Import convention

`backend/app/` is a real package, always run as `uvicorn app.main:app` —
never `cd app && uvicorn main:app`. All intra-package imports are relative
(`from .config import settings`, `from ..database import get_db`). This must
stay consistent across `backend/Dockerfile`'s `CMD`, the root `Dockerfile`'s
prod `CMD`, `backend/docker-compose.yml`'s `command:`/build, and this file —
check all four before changing how the app boots.

## Auth pattern

Firebase Bearer token, verified in `app/dependencies.py`, with a
`TEST_AUTH_BYPASS` escape hatch for local/CI:

- `get_current_user` resolves the caller to an internal user UUID (string).
- When `settings.TEST_AUTH_BYPASS` is true, the `X-User-ID` header is
  accepted directly — the user row must already exist (a system user is
  seeded at startup in `main.py`'s lifespan; never auto-created per-request).
- When bypass is false, `Authorization: Bearer <token>` is verified via
  `firebase_admin.auth.verify_id_token`.
- **Bootstrap-specific note**: `firebase_admin.initialize_app()` is called
  lazily, only the first time the non-bypass branch actually runs — not at
  import or startup. This lets the app boot and serve `/health` with zero
  Firebase credentials configured, since `TEST_AUTH_BYPASS=true` is the only
  path exercised until a real product feature needs real auth. Creating an
  actual Firebase project is out of scope until then.

## Startup dependency

`main.py`'s lifespan runs `Base.metadata.create_all` and seeds a system user
(`SYSTEM_USER_ID` in `models.py`) on every boot. This means a live Postgres
connection is required just to serve `/health` — run `docker-compose up`
(root, or `backend/docker-compose.yml` for backend-only) before `uvicorn`.

## Test organization

- `backend/tests/test_api.py` — integration, hits a real Postgres DB via
  `TestClient`. Owned exclusively by the `/test-review` skill — do not modify
  directly.
- `backend/tests/unit/` — dev-owned, mocks the DB session with `MagicMock`.
- `backend/tests/conftest.py` sets `TEST_AUTH_BYPASS=true` for the whole test
  session, and overrides `DATABASE_URL` from `TEST_DATABASE_URL` if that's
  set. **Scope note**: this bootstrap pass does not stand up an isolated test
  database — tests run against the same local Postgres instance/db as dev
  (`mexit`). Revisit if/when test data volume or CI isolation becomes a real
  concern.
- `frontend/src/__tests__/` — Vitest + `@testing-library/react` + jsdom.
  **Divergence from template**: the template's stated test target is pure
  functions in `utils/` and API wrappers in `api/`; both are empty this pass
  (no resources yet), so the only test is a smoke test on `App.tsx`. Revisit
  once real `utils/`/`api/` code exists.

## Deploy setup

- Root `Dockerfile`: 2-stage — stage 1 builds `frontend/` (`npm ci && npm run
  build`, `VITE_FIREBASE_*` as build `ARG`s), stage 2 installs backend deps,
  copies `backend/app/` in, copies stage 1's `dist/` in as `static/`. `main.py`
  mounts `static/` at `/` if the directory exists (prod only — it won't in
  local dev), registered after all API routes so it never shadows them.
- `railway.toml`: Dockerfile builder, health check on `/health`.
- **Deploy-trigger rule**: triggers on `backend/app/` only — tests, scripts,
  and tooling already live outside `app/`.
- **CI/CD deploy tagging**: not yet configured — no CI pipeline exists in
  this repo yet. Add the skip-tag convention here once one does.
