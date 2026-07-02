# DATA_MODEL_AND_API.MD — mexit

This is the bootstrap pass — see
`development-plans/PLAN-chore-bootstrap-uniform-structure.md`. No product
data model exists yet; `DESIGN.md`'s financial-statement schema is
out of scope until that work is separately planned.

## Data model

### `users`

Exists solely to make the auth pattern in `ARCHITECTURE.MD` functional — not
a product table.

| Column | Type | Notes |
|---|---|---|
| `id` | String (UUID) | Primary key. Internal user identifier returned by `get_current_user`. |
| `firebase_uid` | String, nullable, unique | Set once real Firebase auth is wired to a route. |
| `email` | String, nullable, unique | |

A single row — the seeded system user (`SYSTEM_USER_ID` in
`backend/app/models.py`) — is created automatically at startup, for use with
`TEST_AUTH_BYPASS`.

## API

### `GET /health`

Returns `{"status": "ok"}`. No auth required. Used by `railway.toml`'s health
check.

No other endpoints exist. Resource routers/services get added to
`backend/app/routers/` and `backend/app/services/` — and documented here —
as product features (from a future plan built on `DESIGN.md`, or otherwise)
are implemented.
