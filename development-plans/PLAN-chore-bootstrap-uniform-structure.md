# PLAN — chore/bootstrap-uniform-structure

## Scope

Bootstrap `mexit` to match `~/projects/claude-global-tools/UniformProject.md` (the
FastAPI + Postgres + Firebase + React/Vite baseline), **minus the mobile app**,
per explicit user instruction. This is a structural/tooling bootstrap only —
no product features are (re)implemented in this pass.

Confirmed with user before drafting this plan:
- `app.py` (Flask PDF-text-extractor) was **experimental** — delete entirely,
  do not port its logic forward.
- `DESIGN.md` (MA Probate Court financial-statement app) is a **future**
  product spec — leave the file untouched at the repo root, out of scope for
  this pass.
- Match `UniformProject.md`'s tech stack as closely as possible; only diverge
  where there's a concrete reason. No mobile stack (`mobile/` dir, Expo, RN)
  since this project has no mobile app.
- No response received on whether to seed a first real backend resource vs.
  bare skeleton — proceeding with **bare skeleton** (health check, config, db,
  auth plumbing, zero product routers) as the lower-risk default.
- **Post-review update:** "bare skeleton" still requires a live Postgres
  connection at boot (the auth pattern seeds a system user on startup) — this
  is not a zero-dependency skeleton. `CLAUDE.md`'s dev-commands section must
  say `docker-compose up` (or equivalent) has to precede first run.

## Divergences from template (and why)

- **Auth (Firebase)**: template includes it as baseline plumbing.
  **Post-review resolution**: write `dependencies.py` per the template shape
  (both the `TEST_AUTH_BYPASS` branch and the `firebase_admin.verify_id_token`
  branch), but guard Firebase initialization so `firebase_admin.initialize_app()`
  is only called lazily, on first use of the non-bypass branch — never at
  import/startup. This keeps template fidelity (the code exists, matches the
  documented pattern) while fixing the actual risk Sneezy raised: the app must
  boot and serve `/health` with zero real Firebase credentials, since
  `TEST_AUTH_BYPASS=true` is the only mode actually exercised this pass.
  Creating a real Firebase project remains out of scope until a protected
  endpoint ships.
- **Anthropic Claude API**: template pins `anthropic==0.40.0` and a
  `CLAUDE_MODEL` setting as baseline even when unused. Keeping the pin/config
  for consistency; no route calls it yet.
- **Database**: template defaults to Postgres. Using Postgres per baseline.
  `DESIGN.md` (out of scope here) separately proposed SQLite — not relevant to
  this pass since DESIGN.md's schema isn't being implemented now.
- **Mobile**: omitted entirely (dir, deps, docs) — explicit user instruction,
  matches the template's own "note the divergence" guidance for stacks that
  intentionally don't need a mobile app.

## Files to delete

- `app.py`
- `templates/` (`index.html`, `view.html`)
- `requirements.txt` (root — replaced by `backend/requirements.txt`)

**Post-review resolution**: `uploads/`/`output/` deletion is struck from this
plan's scope entirely (Sneezy blocker, agreed). Both are already
gitignored/untracked so this bootstrap's tracked-file diff is unaffected
either way. They hold real personal financial documents — left for the user
to handle manually, outside any agent-run commit.

## Files to keep as-is

- `DESIGN.md` (future scope, untouched) — `PRODUCT_REQUIREMENTS_DOCUMENT.MD`
  stub will cross-reference it by name so a future reader isn't left with two
  disconnected specs.
- `RULES_OF_ENGAGEMENT.MD` (already present at root, matches global doc)
- `.claude/settings.local.json` (existing permissions; may need new entries
  for `npm`, `uvicorn`, `docker` commands — additive only)

**Post-review correction to Sneezy's Gap 4**: `.claude/agents/` and
`.claude/commands/` are not missing from the agent/skill lifecycle — verified
that `~/.claude/agents` and `~/.claude/commands` are symlinks to
`claude-global-tools/.claude/{agents,commands}`, so the full roster
(plan-review/Sneezy, test-review, code-review, arch-review,
requirements-review) is already globally active for every project including
this one. No action needed.

## New root-level structure

```
ARCHITECTURE.MD
DATA_MODEL_AND_API.MD
PRODUCT_REQUIREMENTS_DOCUMENT.MD      # stub — real content is DESIGN.md's job later
RULES_OF_ENGAGEMENT.MD                 # unchanged, kept as-is
CLAUDE.md                              # dev commands, deploy trigger, agent roster
Dockerfile                              # 2-stage build
docker-compose.yml                      # dev: backend + Postgres, for local `docker-compose up`
railway.toml
.gitignore                              # updated for backend/frontend artifacts
development-plans/
  PLAN-chore-bootstrap-uniform-structure.md
backend/
  app/
    __init__.py
    main.py                            # FastAPI(), lifespan (seeds system user), router registration, /health
    config.py                          # pydantic-settings singleton
    database.py                        # engine, SessionLocal, get_db
    dependencies.py                    # get_current_user: TEST_AUTH_BYPASS branch + lazy-init Firebase branch
    models.py                          # Base + User (minimum viable for auth)
    schemas.py                         # empty/minimal for now
    routers/__init__.py                # no resources yet
    services/__init__.py               # no resources yet
  tests/
    __init__.py
    test_api.py                        # integration — health check only, hits real Postgres via TestClient
    unit/__init__.py
  scripts/
  requirements.txt
  Dockerfile
  docker-compose.yml                    # backend + Postgres services; same Postgres used for test_api.py
                                         # via a separate TEST_DATABASE_URL/db name, documented in .env.example
  .env.example
frontend/
  src/
    api/                               # empty, first client added with first resource
    components/
    context/                           # AuthContext
    hooks/
    pages/                             # placeholder landing page
    utils/
    __tests__/                         # App.tsx smoke test only this pass (utils/, api/ start empty —
                                         # logged divergence from template's stated unit-test target)
    firebase.ts
    App.tsx
    main.tsx
  eslint.config.js
  tsconfig.json                         # references tsconfig.app.json + tsconfig.node.json
  tsconfig.app.json
  tsconfig.node.json
  tailwind.config.js
  postcss.config.js
  package.json                          # includes react-router-dom 7 per template baseline, unused until
                                         # a second page/route exists
```

No `mobile/` directory.

**Post-review addition — import-convention verification**: every place
`main:app` could appear (`backend/Dockerfile` `CMD`, root `Dockerfile`'s prod
`CMD`, `backend/docker-compose.yml` `command:`, `CLAUDE.md` dev-command
block, `ARCHITECTURE.MD`) must say `app.main:app`, never `main:app`. Called
out here as an explicit implementation checklist item, not left implicit.

## Data model changes

- New `users` table (SQLAlchemy `User` model) — minimum required for the auth
  dependency to resolve a caller to an internal UUID, and for
  `TEST_AUTH_BYPASS` to have a seeded system user to bind to. No other tables
  — no product data model exists yet (DESIGN.md's schema is out of scope).

## API changes

- New: `GET /health` only. No resource endpoints (no routers besides the
  empty `routers/` package) since no product feature is in scope this pass.

## Test plan

- `backend/tests/test_api.py`: one integration test hitting `/health` via
  `TestClient`. Per this repo's `RULES_OF_ENGAGEMENT.MD`, this file is owned
  exclusively by `/test-review` going forward — creating the initial stub now
  is a one-time bootstrap exception; all subsequent edits route through that
  skill.
- `backend/tests/unit/`: unit test for `config.py` (settings load) and
  `dependencies.py` (bypass vs. Firebase branch), mocking the DB session.
- `frontend/src/__tests__/`: Vitest smoke test for `App.tsx` rendering.

## Deployment

- Nothing is currently deployed (no Railway project referenced anywhere in
  the existing repo). This pass sets up `Dockerfile` + `railway.toml` but
  does not trigger an actual deploy — single component, no live traffic to
  protect, no backward-compat window needed.
- Deploy-trigger rule for `CLAUDE.md`: triggers on `backend/app/` only, per
  template convention.

## Doc content specs (post-review addition)

Closing Sneezy's Gap 8 — these aren't shipping as unspecified stubs:

- **`ARCHITECTURE.MD`**: backend/frontend directory layout (this plan's tree),
  the relative-import convention and the `app.main:app` rule, the auth
  pattern (`TEST_AUTH_BYPASS` vs. lazy Firebase), dev commands
  (`docker-compose up`, `uvicorn app.main:app --reload`, `npm run dev`), the
  test split (`tests/test_api.py` vs. `tests/unit/`), and the deploy-trigger
  rule (`backend/app/` only).
- **`DATA_MODEL_AND_API.MD`**: the `users` table schema and why it exists
  (auth resolution only, no product data yet), the `/health` endpoint
  contract, and a note that no other tables/endpoints exist pending
  DESIGN.md-derived work.
- **`CLAUDE.md`**: dev commands, deploy-trigger rule, CI/CD deploy-tagging
  convention (per `RULES_OF_ENGAGEMENT.MD`'s reference to it), agent roster
  (confirmed globally active per the `.claude/agents` symlink note above).

## Out of scope for this pass

- Any product feature (PDF extraction, DESIGN.md's financial-statement form)
- Firebase project creation / real credentials (env vars documented in
  `.env.example` with placeholders only)
- Actual Railway deployment

---

## Sneezy's Review — 2026-07-01

**Verdict:** Changes required

### Issues

1. **[Blocker] `uploads/`/`output/` deletion should not be bundled into this
   plan's scope.** These directories hold the user's real financial documents
   (bank/pay statements — confirmed by inspection: `LongForm_FS.pdf`,
   `Fidelity-Statement-1-31-2024 copy.pdf`, `CapitalOne-Statement-2023-11
   copy.pdf`, `ServiceNow-Pay-2024-09-13 copy.pdf`, etc.). Confirmed both are
   already `.gitignore`d and untracked (verified: `git status` shows nothing
   for them, `.gitignore` lists `uploads/` and `output/`), so deleting them
   produces **zero diff and zero benefit** to this PR — the repo's tracked
   state is identical whether or not this deletion happens. The plan does
   the right thing by saying "will confirm before deleting," but folding an
   irreversible, unrelated filesystem deletion of sensitive personal data
   into the same "Files to delete" list as `app.py`/`templates/`/
   `requirements.txt` risks a single top-level "Shall I proceed?" being read
   as authorizing all of it at once, including the one item that isn't
   actually recoverable. Recommend striking this from the plan's scope
   entirely and leaving it to the user to archive/delete manually, outside
   any agent-run `rm`/commit — it has no structural bearing on the bootstrap.

2. **[Risk] "Bare skeleton, lower risk" undersells the actual runtime
   dependency footprint.** The auth pattern this plan adopts verbatim from
   `UniformProject.md` requires seeding a system user at startup for
   `TEST_AUTH_BYPASS` to resolve ("the user row must already exist... don't
   auto-create"). If `main.py`'s lifespan does this seed on boot (as the
   template implies), a fresh checkout needs a **live Postgres connection**
   before `GET /health` will even respond — there is no such thing as a
   zero-dependency skeleton once Postgres + startup seeding are in the loop.
   Separately, if `firebase_admin` is initialized eagerly at import/startup
   (a common pattern) rather than lazily on first authenticated request, the
   app may fail to boot with no `FIREBASE_SERVICE_ACCOUNT_JSON` set — which
   is guaranteed this pass, since Firebase project creation is explicitly
   out of scope. Neither `main.py` nor `dependencies.py` exist yet to check
   directly, so this is a design decision the plan should pin down
   explicitly (lazy Firebase init; document that `docker-compose up` must
   precede first run) rather than leave implicit.

3. **[Risk] Firebase inclusion is not proportionate given the plan's own
   stated constraints.** The plan flags this itself as "the item most worth
   a second look" and resolves it toward inclusion via "match unless a
   concrete reason surfaces not to" — but a concrete reason is already
   stated two lines later: zero product routes, zero users, and Firebase
   project/credential creation explicitly out of scope this pass. Wiring the
   real `firebase_admin.auth.verify_id_token` branch now, with no way to
   exercise it (no creds, no protected route), buys nothing this pass and
   adds setup cost (a Firebase project) before there's anything to protect.
   The plan's own proposed "cheapest fix if wrong" (strip Firebase later,
   keep `TEST_AUTH_BYPASS`) is backwards from a risk-minimization standpoint
   — it's cheaper to start with `TEST_AUTH_BYPASS`-only now and add the
   Firebase branch in the PR that ships the first protected endpoint, when
   there's something to verify it against.

4. **[Gap] No plan to bring in `.claude/agents/` or `.claude/commands/`.**
   `RULES_OF_ENGAGEMENT.MD` (copied verbatim into this repo, confirmed
   identical via diff to `claude-global-tools/RULES_OF_ENGAGEMENT.MD`)
   references `/test-review`, the plan-review agent (Sneezy), and an "agent
   roster" in `CLAUDE.md" as if they're operative in this repo. Checked:
   neither `mexit/.claude/` (only contains `settings.local.json`) nor
   `~/.claude/agents` / `~/.claude/commands` (both empty) contain these
   definitions — only `claude-global-tools/.claude/agents` and
   `.claude/commands` do. Without copying these in, the development-plan
   lifecycle this very plan is following (and the "Test plan" section's
   claim that `test_api.py` is "owned exclusively by `/test-review` going
   forward") has no teeth in this repo. Either add this to scope or
   explicitly note it as a deferred, separately-tracked item.

5. **[Gap] Import-convention risk not called out.** `UniformProject.md`
   explicitly warns that `uvicorn app.main:app` (never `cd app && uvicorn
   main:app`) must be reflected consistently in the Dockerfile `CMD`,
   `docker-compose.yml`'s `command:`, and `CLAUDE.md`/`ARCHITECTURE.MD` dev
   command blocks, calling it out as an easy point of drift. The plan's file
   list and deployment section don't mention this as a specific
   verification item, even though it's the kind of detail this plan-review
   process exists to catch before implementation.

6. **[Gap] Frontend file tree is incomplete relative to the template.**
   `UniformProject.md` states `tsconfig.json` "references
   tsconfig.app.json + tsconfig.node.json" — the plan's frontend tree lists
   only a single `tsconfig.json`. Tailwind 3 + postcss + autoprefixer is
   listed in the template's pinned tech stack but has no corresponding
   config file (`tailwind.config.js`/`postcss.config.js`) or dependency
   entry anywhere in the plan, and isn't logged as an intentional
   divergence either. `react-router-dom 7` (also pinned baseline) is
   likewise never mentioned, though with a single placeholder page that may
   be deferred reasonably — but silently, not as a stated choice.

7. **[Gap] No test-database provisioning story.** Per the template,
   `backend/tests/test_api.py` "hits a real DB via `TestClient`." The plan
   doesn't say what supplies that live Postgres instance locally (does
   `backend/docker-compose.yml` stand one up? is there a separate test
   `DATABASE_URL`?) or in any future CI. This matters more than usual here
   because this project is moving from no DB at all (or DESIGN.md's SQLite
   proposal) straight to Postgres, and it's exactly the kind of detail that
   becomes expensive to retrofit once `/test-review` starts owning the file.

8. **[Gap] `ARCHITECTURE.MD` / `DATA_MODEL_AND_API.MD` content is
   unspecified.** The plan lists these as files to create but never
   describes what goes in them (the auth pattern, the import convention,
   the users-table schema, dev commands). Given these docs are the
   project's designated "ground truth" for later `arch-review` passes,
   shipping them as unspecified stubs in the bootstrap PR risks them
   starting out already out of date with what actually got built.

9. **[Nit]** The "New root-level structure" tree omits
   `RULES_OF_ENGAGEMENT.MD` even though the prose confirms it's kept as-is
   — the tree should be the single authoritative picture of the resulting
   layout.

10. **[Nit]** `frontend/src/__tests__/` smoke-testing `App.tsx` is a
    reasonable practical call given `utils/` and `api/` start empty, but it
    diverges from the template's stated test target ("pure functions in
    `utils/` and API client wrappers in `api/`") without being logged in
    "Divergences from template."

11. **[Nit]** `RULES_OF_ENGAGEMENT.MD`'s "CI/CD deploy tagging: consult
    `CLAUDE.md` for which commit paths trigger a deployment and what tag to
    include to skip it" isn't mentioned as required `CLAUDE.md` content,
    even though the plan otherwise carefully specifies the deploy-trigger
    rule.

### Unverified assumptions

- **"`RULES_OF_ENGAGEMENT.MD`... matches global doc"** — verified true:
  `diff` against `claude-global-tools/RULES_OF_ENGAGEMENT.MD` shows the
  files are byte-identical.
- **"`uploads/`, `output/`... already gitignored/untracked, never
  committed"** — verified true: both appear in `.gitignore`, neither
  appears in `git status` or the single existing commit's file list.
- **"Nothing is currently deployed (no Railway project referenced anywhere
  in the existing repo)"** — verified true: the only repo-wide match for
  "railway" (case-insensitive) is the plan file itself.
- **Whether `main.py`'s lifespan eagerly seeds a system user / initializes
  `firebase_admin` at startup** — could not verify; `backend/app/main.py`
  doesn't exist yet. This is the crux of Issue 2 and should be settled by
  the plan (explicitly, in prose) rather than left to whoever implements
  it to decide.
- **Root `requirements.txt`/`package.json` version pins matching
  `UniformProject.md` exactly** — the plan doesn't restate the pinned
  versions (`fastapi==0.115.0`, `React 19`, etc.) inline, so there's nothing
  in the plan file itself to check implementation against without
  re-opening `UniformProject.md` side by side.

### Suggestions

- Pull the `uploads/`/`output/` deletion out of this plan/PR entirely (see
  Issue 1); if the user wants it gone, do it as its own explicit,
  standalone action.
- Default to `TEST_AUTH_BYPASS`-only for this bootstrap pass; add the real
  `firebase_admin` branch in the PR that ships the first protected
  endpoint (see Issue 3).
- Inline the exact pinned dependency versions from `UniformProject.md` into
  this plan (or a linked appendix) so the plan is self-contained per the
  development-plan-lifecycle requirement ("enough context for an
  independent agent to review it").
- Add a one-line cross-reference from the `PRODUCT_REQUIREMENTS_DOCUMENT.MD`
  stub to `DESIGN.md`, so a future reader doesn't find two disconnected
  product specs at the repo root with no link between them.
- Decide and state explicitly whether `.claude/agents/` +
  `.claude/commands/` are in scope for this pass (see Issue 4) — even a
  one-line "deferred to a follow-up PR, tracked as X" closes the gap.

— *Sneezy*

---

## Author response to review — 2026-07-01

User approved proceeding after reviewing Sneezy's findings. Disposition of
every item, inline edits made above:

1. Blocker (uploads/output deletion) — **Addressed**: struck from scope, see
   "Files to delete."
2. Risk (bare skeleton / Postgres-at-boot) — **Addressed**: acknowledged
   explicitly in Scope; `CLAUDE.md` will document the Postgres-first
   requirement.
3. Risk (Firebase proportionality) — **Addressed**: resolved to
   lazy-init Firebase + `TEST_AUTH_BYPASS`-as-only-exercised-path, see
   "Divergences from template."
4. Gap (.claude/agents missing) — **Addressed, correction**: not actually
   missing — symlinked globally, see "Files to keep as-is."
5. Gap (import-convention risk) — **Addressed**: explicit checklist item
   added under "New root-level structure."
6. Gap (frontend tree incomplete) — **Addressed**: `tsconfig.app.json`/
   `tsconfig.node.json`, Tailwind/postcss config, `react-router-dom` added to
   the tree.
7. Gap (test-DB provisioning) — **Addressed**: `backend/docker-compose.yml`
   provisions Postgres for both dev and `test_api.py`, noted in the tree.
8. Gap (doc content unspecified) — **Addressed**: see new "Doc content
   specs" section.
9. Nit (RULES_OF_ENGAGEMENT.MD omitted from tree) — **Addressed**.
10. Nit (App.tsx smoke test divergence not logged) — **Addressed**: logged
    inline in the frontend tree.
11. Nit (CI/CD deploy tagging in CLAUDE.md) — **Addressed**: added to "Doc
    content specs."

Implementation proceeds per this updated plan.
