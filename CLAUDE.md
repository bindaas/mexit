# CLAUDE.md — mexit

## Dev commands

Backend needs Postgres running first — the app seeds a system user at
startup (see `ARCHITECTURE.MD`).

```
docker-compose up -d postgres          # or: cd backend && docker-compose up -d postgres
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload          # never `cd app && uvicorn main:app`
```

```
cd frontend && npm install
npm run dev
```

Tests:

```
cd backend && pytest                    # runs tests/test_api.py + tests/unit/
cd frontend && npm test                 # vitest
```

## Deploy trigger

Deploys trigger on changes under `backend/app/` only. Tests, scripts, and
tooling live outside `app/` on purpose so they don't trigger a deploy.

## CI/CD deploy tagging

No CI pipeline exists yet — nothing to tag/skip. Document the convention
here once one is added.

## Agent roster

This repo follows `RULES_OF_ENGAGEMENT.MD` (copied verbatim from
`claude-global-tools`). The full agent/skill roster (plan-review, code-review,
test-review, arch-review, requirements-review) is available globally via
`~/.claude/agents` and `~/.claude/commands`, which symlink to
`claude-global-tools/.claude/`. No project-local copies are needed.

## Current state

Structural bootstrap only — see
`development-plans/PLAN-chore-bootstrap-uniform-structure.md`. No product
routes/data model exist. `DESIGN.md` is the real product spec, not yet
implemented.
