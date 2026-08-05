# AutoAssist — Handoff Document

**Purpose of this file:** a complete, standalone briefing so a new Claude session (chat or Claude Code) can pick up this project with zero prior context. Read this fully before doing anything. It supersedes assumptions from `AUTOASSIST_BUILD_GUIDE.md` wherever the two disagree — this file documents what actually happened, including every deliberate deviation from the original guide.

**Companion file:** `AUTOASSIST_BUILD_GUIDE_ANNOTATED.md`. That file is the original build guide with inline ⚠️ DEVIATION / 🔲 OPEN notes inserted at the exact points where real practice diverged from plan, or where the guide calls for a decision that hasn't been made yet. This document (HANDOFF.md) is the narrative/state summary; the annotated guide is the full spec, including complete un-summarized detail for Phases 6–12 which this document only briefly outlines. Read both — they're designed to be used together, not as alternatives.

## 1. Who this is for

Muneera Othman (GitHub: Muneeraothman), a complete beginner to software development, building this project for two goals simultaneously: (1) genuine technical mastery, (2) a strong, honestly-explainable project for job interviews. Repo: https://github.com/Muneeraothman/autoassist (currently private).

Critical standing instruction, from the project's own `AUTOASSIST_LEARNING_INTERVIEW_GUIDE`: "You own every line in the repo — 'an AI wrote that part' is not an answer." AI (Claude in chat, Claude Code) is used heavily and openly — this is explicitly endorsed as normal, standard practice — but Muneera must be able to explain any piece of the code, not just point at it. See Section 3 for exactly which parts she personally wrote vs. which were AI-authored boilerplate.

Working style note for whoever picks this up: Muneera works across multiple laptops (her own + occasionally her dad's, with his explicit permission — see Section 6). She is not a fast typist and has repeatedly hit terminal/paste friction (see Section 7, "Environment Gotchas" — this is the single most valuable section to read before giving her multi-step instructions). Prefer having her paste one thing at a time and verify with cat/git status rather than trusting that multi-step instructions landed correctly.

## 2. Tech stack (as actually built, confirmed working)

- **Backend:** Python 3.14 (note: NOT 3.9, which is some machines' system default — see gotcha in Section 7), FastAPI, SQLAlchemy 2.0, Pydantic v2, psycopg2-binary, python-dotenv, python-dateutil, pytest, `passlib[bcrypt]` (pinned to `bcrypt==4.0.1` specifically — see the Phase 4.5 entry for the compatibility bug that pin fixes), `python-jose[cryptography]` (JWT), `boto3` (SES + S3)
- **Database:** PostgreSQL 16. Locally: Docker (`autoassist-db` container, `postgres:16` image, password `devpassword`, port 5432) — either standalone (`docker run`) or via `docker compose up` as of Phase 6 (see Section 4/5). In AWS: RDS `db.t3.micro`, single-AZ, private subnets, as of Phase 7 — only exists while the Terraform infra is actually applied (destroy-between-sessions, see the Phase 7 entry).
- **Frontend:** React + Vite, plain useState/useEffect/fetch (explicitly no Redux, no React Query — kept simple), recharts for the spending dashboard charts
- **Dev tools:** VS Code (for writing code), Terminal (for running commands — deliberately kept separate after early friction), Claude Code (installed via `curl -fsSL https://claude.ai/install.sh | bash`, authenticated to Muneera's own Claude Pro account, muneera0615@gmail.com)
- **AWS/infra (built as of Phase 5–8, not "planned" anymore):** S3 (receipt uploads, Phase 5), SES (email verification/password reset, pulled forward from Phase 9 into Phase 4.5), Terraform (`infra/` + `infra/bootstrap/`, Phase 7–8) provisioning a VPC, RDS, an EC2 instance, ECR, GitHub OIDC federation, and a CloudWatch billing alarm. GitHub Actions CI/CD (Phase 8) — `.github/workflows/ci.yml` + `cd.yml`, deploying via SSM Run Command, no static AWS keys in GitHub Secrets. Four separate IAM identities in use across the project (`autoassist-dev`, `autoassist-terraform`, `autoassist-ec2-role`, `autoassist-github-actions-deploy`) — see the Phase 7/8 entries for why each is scoped the way it is.
- **Still genuinely not touched:** OpenAI or Bedrock (Phases 10–11 — provider undecided, see §3.6), pgvector.

## 3. MAJOR DEVIATIONS from the original AUTOASSIST_BUILD_GUIDE.md

These are deliberate, discussed decisions — not mistakes. Do not "correct" them back toward the original guide without discussing with Muneera first.

### 3.1 — The car was switched: 2013 Honda Accord → 2002 Lexus ES300

This is the single biggest deviation and affects Phase 1 data, all manuals, and any documentation referencing "Maintenance Minder."

- Original plan: track a 2013 Honda Accord.
- What happened: After extensive discussion about Honda's Maintenance Minder system (which computes oil-change intervals dynamically via an onboard oil-life algorithm rather than a fixed manual schedule — codes like "A1"/"B12" with no fixed mileage/month table), the project switched to Muneera's actual 2002 Lexus ES300, specifically because it uses simple, fixed mileage/month maintenance intervals (no adaptive computer), which is a cleaner fit for the schema (`schedule_items.interval_miles` / `interval_months` as fixed numbers).
- Old Honda data was fully deleted from the database (a real, deliberately-executed DELETE exercise — this is documented as a teaching moment, not an error).
- Manuals in the repo, `manuals/` folder:
  - `manuals/2A1313OM.pdf` — the OLD Honda Accord manual. Still sitting in the repo, deliberately left there, but is stale/unused. CLAUDE.md explicitly flags this so future sessions don't accidentally treat it as a data source.
  - `manuals/OM33566U.pdf` — the current Lexus's MAIN owner's manual (364 pages). Does NOT contain maintenance intervals — it explicitly points to a separate supplement booklet.
  - `manuals/SMG202.pdf` — the current Lexus's Scheduled Maintenance supplement (261 pages). This is the authoritative source for real maintenance intervals, roughly pages 99–109 for the interval table. All 6 "real" schedule items (see 3.2) were sourced from here, not from memory or assumption.

### 3.2 — schedule_items data: 6 real manufacturer numbers + 3 honestly-labeled estimates

This is a deliberate, discussed data-honesty decision, worth being able to explain in an interview:

- 6 items came directly from the real Lexus supplement (SMG202.pdf), on the 7,500-mile/6-month "normal conditions" track: oil + filter change, tire rotation, air filter, brake fluid, coolant, transmission fluid inspection.
- 3 items are NOT in the manual at all and are explicitly labeled as estimates in their notes column: brake pads (50,000 mi, wear-based estimate), battery (48 months, typical lifespan estimate), tires (55,000 mi, wear-based estimate). These are genuinely unscheduled wear items — no manufacturer publishes a fixed interval for them, so honesty in the data (rather than inventing a fake "official" number) was the deliberate choice.
- Current real seeded values: `vehicles` table has 1 row (id=2 — not id=1, because SERIAL doesn't reuse ids after the Honda row was deleted), 164,784 miles, `avg_miles_per_day` defaults to 30.0 until a real PATCH recomputes it. `schedule_items` has 9 rows (ids 8–16, same id-skip reason). `service_records` has 16 rows of REAL service history, April 2023 – June 2026, sourced from Muneera's actual receipts/memory, not fabricated.
- Known, deliberate, ACCEPTED data gap: there is a real ~106,000-mile gap between the last logged service record (~58,410 mi, June 2026) and current_mileage (164,784 mi). This is not a bug or data-entry error — Muneera confirmed 164,784 is the real current odometer reading, and the service history genuinely has an undocumented gap (years of driving/maintenance that was never logged). The due-date engine (Phase 4) correctly shows nearly everything as OVERDUE given this real gap — that is correct behavior given real, honestly-imperfect data, not something to "fix" by altering the seed data.

### 3.3 — Pacing changed mid-project: slow/Socratic → fast/reviewed

- Phases 1–2 (and the start of the Phase 2 mileage endpoint): built via strict, slow, fill-in-the-blank Socratic teaching — Muneera wrote every line of logic herself after concept explanations, with quizzes at phase boundaries (shuffled multiple-choice + open-ended explain-back).
- Partway through Phase 2 (after `PATCH /api/vehicle/mileage` was built and tested), Muneera explicitly asked to speed up, citing frustration with the slow pace and general "how fast can this be finished" pressure. Deliberate decision made: Claude Code now writes most code directly and tests it itself, checking in with a summary at phase/task boundaries rather than at every function.
- Explicit standing exception, re-affirmed multiple times by both Muneera and Claude Code unprompted: the due-date engine's core comparison + bucketing logic (Phase 4 — see Section 4.4) was deliberately kept as something Muneera wrote herself, specifically because it's the single most likely piece to be asked about in an interview ("walk me through your due-date algorithm"). Claude Code itself proactively recommended this split and it should be honored again for any future similarly-central logic (the AI tool-calling loop in Phase 10 is a strong candidate for the same treatment — flag it if that phase is reached).
- Practical implication for whoever picks this up: default to the fast pace (build → test → summarize) for boilerplate/plumbing/infrastructure, but proactively suggest slowing down and having Muneera write it herself for anything that's genuinely "the interesting algorithm" of a phase, the same way this was handled in Phase 4.

### 3.4 — LEARNING_PROCESS.md / CLAUDE.md were updated to reflect the new pace

Both files should already say something to the effect of "build and test each phase, check in with a summary at phase boundaries, not step-by-step" — if a future session finds them still describing the old slow-only process, that's stale and should be updated to match this document.

### 3.5 — Repo made private

The GitHub repo was switched from public to private specifically because Muneera didn't want an interviewer stumbling onto the public contributor list and seeing "claude" listed as a contributor without context. (Worth knowing: this is a completely normal, defensible thing either way — Claude Code commits genuinely do show up as a contributor — but Muneera's preference was to control that reveal herself, in an interview conversation, rather than have it be silently visible.) If a future session needs to share the repo with an interviewer, the mechanism is adding them as a collaborator or screen-sharing — not making it public again, unless Muneera says otherwise.

### 3.6 — Two genuinely open/undecided items, surfaced by cross-checking against the original guide

- LLM provider for Phases 10–11 (Bedrock vs. OpenAI) has NOT been decided. The guide asks for this to be settled in Phase 0; it wasn't. Ask Muneera directly when Phase 10 approaches — don't default to pgvector/OpenAI or Bedrock just because one is "cheaper" or "simpler," actually ask which she has access to / prefers, per the guide's own instruction.
- Whether Muneera actually did the Phase 4 checkpoint's "explain the whichever-comes-first logic out loud, unprompted" rehearsal is unconfirmed. It was suggested to her in conversation but no explicit confirmation came back before the session moved on to Phase 5 discussions. Worth confirming/doing if picking this project back up, since the guide calls this her "#1 interview talking point."
- ~~The Phase 4 bucketing OR-condition fix (see 4.4 below) was flagged as needed and Claude Code said it would add it, but this was never independently re-verified in the final `engine.py`.~~ **Resolved as of the Phase 4.5 session**: independently re-verified directly in `engine.py` (`miles_remaining is not None and miles_remaining <= due_soon_miles`, present) and confirmed by the full passing test suite including `test_due_soon_triggered_by_miles_threshold_alone`. Settled — no longer an open item.

### 3.7 — Phase 4.5 addendum's Section 6 open decisions, as actually decided

Per `AUTOASSIST_ADDENDUM_PHASE_4_5_AUTH.md` §6, these were not to be defaulted silently. Decided directly with Muneera before Phase 4.5 work began:

- **Token storage**: httpOnly cookie (not localStorage) — the more defensible choice against XSS token theft, at the cost of needing the backend to read `Request.cookies` instead of an `Authorization` header (this actually contradicted the addendum's own Section 4 step 5 wording, which assumed a header — corrected during implementation, see the Phase 4.5 entry below).
- **JWT expiry**: a single longer-lived token (~7 days), no refresh token — simpler, judged "good enough for a portfolio project" per the addendum's own framing of that option.
- **Password reset**: build now, real sending via AWS SES — pulled forward from Phase 9 rather than deferred to a "v2 ideas" note.
- **Email verification**: build now, same SES mechanism — same reasoning as password reset.
- **Schedule-item entry (add-a-car UX)**: stays a manual SQL insert per new vehicle for now, NOT a real UI form. `POST /api/vehicles` solves "add a car" only; entering that car's maintenance intervals is still the same manual transcription process used for the original Lexus data. Deliberately kept out of scope to avoid Phase 4.5 scope creep — a real form remains a good, explicitly-recorded follow-up (see the addendum's Section 7 idea about reusing Phase 11's PDF-parsing pipeline for this eventually).

## 4. Phase-by-phase status

### ✅ Phase 0 — Setup (COMPLETE)

Homebrew, Git, Node (added late — see 7.6), Python, Docker Desktop, VS Code, TablePlus (installed but its GUI connection to Postgres was never successfully debugged — not blocking, `psql` via `docker exec` is the working fallback), GitHub account + repo.

### ✅ Phase 1 — Database Schema + Seed Data (COMPLETE)

3 tables (vehicles, schedule_items, service_records), exact schema per the build guide, foreign keys enforced and live-tested (deliberately tried inserting a bad vehicle_id to confirm rejection). Real seed data as described in Section 3.2. Quiz passed (with a couple of re-teaches on delete-order/foreign-key mechanics, both confirmed solid on second pass).

### ✅ Phase 2 — Backend API (COMPLETE)

All endpoints built, tested, and confirmed working against the real database:

- `GET /` — health check (not in original spec, harmless extra)
- `GET /api/vehicle` — single vehicle row
- `GET /api/schedule` — all 9 schedule items, ordered by id
- `GET /api/services` — all 16 service records, newest-first (`service_date.desc()`), optional `?schedule_item_id=` query filter
- `PATCH /api/vehicle/mileage` — the first genuinely hand-written business logic. Pydantic model `MileageUpdate` (`mileage: int = Field(gt=0)`). Route logic (written by Muneera personally, piece by piece): rejects a mileage decrease (422), skips the `avg_miles_per_day` recompute if less than a day has passed since the last update (avoids division-by-zero and noisy short-window averages), otherwise recomputes `avg_miles_per_day = miles_driven / days_elapsed`. Known real gotcha here: `vehicle.avg_miles_per_day` comes back from Postgres as a `Decimal` (column type `NUMERIC(6,2)`), not a float — must be explicitly cast with `float(...)` before doing math with it or passing it to functions like `timedelta()` that reject Decimal. This exact gotcha recurs in Phase 4's engine — see 4.4.
- `POST /api/services` (201) — `ServiceCreate` Pydantic model with a custom `@field_validator` rejecting future `service_date` (can't be expressed as a static `Field()` bound since "today" changes daily — needs a real function call to `date.today()` at request time). Route-level check (Muneera's own call): reject if `mileage_at_service` is more than 500 miles ahead of `vehicle.current_mileage` (likely a typo) — but explicitly ALLOW lower mileage, since backfilling older historical records should be possible.
- `PUT /api/services/{id}` — full update, same validation as POST, 404 on bad id.
- `DELETE /api/services/{id}` (204) — 404 on bad id.
- Consistent 404 handling added via two small reusable helpers, `get_vehicle_or_404(db)` and `get_service_or_404(db, service_id)` — retrofitted across every route. Before this existed, a missing row would crash with an unhandled `AttributeError` instead of a clean HTTP error; this was deliberately deferred until all the CRUD endpoints existed, then fixed everywhere at once rather than piecemeal.
- Also factored: `serialize_service(record)` (deduplicates the repeated dict-building logic used by 3+ endpoints), `check_mileage_sane(mileage, vehicle)` (used by both POST and PUT).
- Full Phase 2 review quiz completed and logged in JOURNAL.md (covering Pydantic vs. route-level validation split, `db.add()` vs `db.commit()`, query params vs. path params, the 404-helper rationale, and the `@field_validator`-vs-`Field()` distinction for dynamic bounds).

### ✅ Phase 3 — Frontend (COMPLETE — built at the FAST pace, Claude Code did most of the writing)

Vite + React, dev server proxies `/api/*` to the FastAPI backend on :8000. Components: `VehicleCard` (shows current mileage + avg, has the mileage-update form), `LogServiceForm` (schedule-item dropdown or "Other/Repair", date, mileage, cost, performed-by, notes → `POST /api/services`), `ServiceHistory` (table, newest-first, filterable). State is lifted to `App.jsx` and passed down as props — no state management library. Real bug found and fixed via actual browser testing (not just curl): the mileage input field in `LogServiceForm` only pre-filled once and went stale after the vehicle's mileage was updated elsewhere — fixed with a `mileageTouched` flag that keeps re-syncing the field to the live current mileage until the user actually starts typing in it, then stops. This is a good, real "found via manual QA, not unit tests" story. Verified end-to-end in a real browser: update mileage → average recalculates → log a service (correct pre-filled mileage) → appears at top of history → refresh page → data survives (proving it's really in Postgres, not just React state).

### ✅ Phase 4 — Due-Date Engine + Dashboard (COMPLETE — "THE core phase" per the guide, treated accordingly)

This is the most important phase to understand and be able to explain. `backend/engine.py`, function `get_upcoming_maintenance(vehicle, schedule_items, service_records, today, due_soon_days=30, due_soon_miles=500)`.

Design principle (explained and internalized, not just implemented): this is a deliberate pure function — no database access inside it, no hidden `date.today()` call, `today` is always passed in as an explicit parameter. This is why it's unit-testable without spinning up Postgres, and it's presented as the reason `avg_miles_per_day` exists on the `vehicles` table at all (Session 5's mileage-PATCH work was really laying groundwork for this).

The algorithm, per schedule item:

- Find the most recent `service_records` row matching this `schedule_item_id` via `max(matching_records, key=lambda r: r.service_date)`.
- **Never-serviced edge case** (a real, discussed design decision): if no matching record exists at all, the item is immediately marked `status="OVERDUE"` with `due_date`, `due_miles`, `days_remaining`, `miles_remaining` all set to `None` (not a fabricated date/zero — the reasoning: "we don't know a real due date, only that it's never happened; forcing honest None-handling into the frontend is a smaller problem than inventing fake precision"). This surfaces genuinely neglected items rather than hiding them.
- **Mileage trigger** (only if `item.interval_miles is not None AND avg_miles_per_day > 0`, guarding both "time-only items" and "division by zero on a freshly-created vehicle row"):
  - `avg_miles_per_day = float(vehicle.avg_miles_per_day)` — the Decimal-to-float cast is mandatory here, same gotcha as the mileage PATCH endpoint. This was actually MISSED on the first draft and caught during review — worth remembering as a recurring category of bug ("this will pass every hand-constructed unit test since test doubles naturally use plain floats, and only blow up against the real database").
  - `due_at_miles = last_record.mileage_at_service + item.interval_miles`
  - `days_since_update = (today - vehicle.mileage_updated_at.date()).days` — note the explicit `.date()` call, since `mileage_updated_at` is a timezone-aware datetime (`DateTime(timezone=True)` in the schema) while `today` is a plain date; subtracting across those types directly raises `TypeError`. Deliberate choice: convert `mileage_updated_at` down to `.date()` rather than upgrade `today` to a full datetime, since the function's whole design point is that `today` stays a simple, easily-test-pinnable value.
  - `estimated_current_mileage = vehicle.current_mileage + avg_miles_per_day * days_since_update`
  - `miles_remaining = due_at_miles - estimated_current_mileage`
  - `mileage_due_date = today + timedelta(days=miles_remaining / avg_miles_per_day)`
- **Time trigger** (only if `item.interval_months is not None`):
  - Uses `dateutil.relativedelta.relativedelta(months=item.interval_months)`, NOT `timedelta`. This is a deliberate, explained choice: `timedelta` only understands fixed-length units (days/weeks/seconds); months are variable-length (28–31 days), so naive `interval_months * 30` approximations would drift wrong over the car's lifetime and mishandle month-end edge cases (e.g., Jan 31 + 1 month has no literal answer without calendar-aware logic). `python-dateutil` is a new dependency (added to `requirements.txt`) specifically for this — worth knowing by name as "the standard thing everyone reaches for since Python's stdlib doesn't do month math."
  - `time_due_date = last_record.service_date + relativedelta(months=item.interval_months)`
- **Whichever comes first, and bucketing** — written personally by Muneera, the one piece of Phase 4 kept at the slow/hand-written pace on purpose:

```python
candidates = [d for d in [mileage_due_date, time_due_date] if d is not None]
if not candidates:
    due_date = None
    status = "OK"  # or however the "genuinely unknown, nothing computable" case is finally handled
else:
    due_date = min(candidates)
    days_remaining = (due_date - today).days
    if due_date < today:
        status = "OVERDUE"
    elif days_remaining <= due_soon_days:
        status = "DUE_SOON"
    else:
        status = "OK"
```

One real bug caught and fixed during review, worth rehearsing as an interview edge case: the bucketing above only checks `days_remaining <= due_soon_days`. Claude Code caught that per the build guide's actual spec ("within 30 days OR 500 miles"), this needs an additional OR-condition on `miles_remaining is not None and miles_remaining <= due_soon_miles` — otherwise a low-mileage/light-driver scenario (e.g., 500 miles left, but that's 60+ days out at their driving pace) would incorrectly show OK instead of DUE_SOON. A dedicated unit test (`test_triggered_by_miles_threshold_alone` or similarly named) exists specifically to lock this in. **Confirm this OR-condition is actually present in the final engine.py before treating this as settled — it was flagged as needed but verify it landed.**

Thresholds: `due_soon_days=30`, `due_soon_miles=500`, implemented as function parameters with module-level constant defaults (deliberate choice over hardcoded magic numbers, specifically so tests can pin exact boundary values, e.g. "exactly 30 days out" vs "31 days out").

Tests: `backend/test_engine.py`, pytest, 8 cases covering: mileage-trigger wins, time-trigger wins, time-only item, never-serviced (OVERDUE), already-serviced-but-time-trigger-passed (OVERDUE), the miles-threshold-alone DUE_SOON case, the `avg_miles_per_day == 0` guard, and an item with no intervals at all.

Endpoint: `GET /api/upcoming`, sorted by urgency (OVERDUE → DUE_SOON → OK, then by due date within each bucket).

Frontend: `UpcomingMaintenance.jsx`, refetches when mileage is updated or a new service is logged. Verified rendering correctly against real data (screenshot-equivalent confirmed in conversation — cards show correct badges, correct "X mi overdue / by DATE" or "No projection available" text for never-serviced items).

Stats/Dashboard (Phase 4's stretch goal, also done): `backend/stats.py`, function `compute_stats(vehicle, schedule_items, service_records)` — same pure-function pattern. Returns `total_spend`, `spend_by_category` (grouped by `schedule_item.service_name`, with an "Other / Unscheduled Repair" bucket for records with `schedule_item_id=None`, sorted highest-spend-first), `spend_by_year`, `cost_per_mile` (`total_spend / (current_mileage - earliest_record.mileage_at_service)`, `None` if there are zero service records — explicitly not faked as 0). 6 passing tests. Endpoint `GET /api/stats`. Frontend `SpendingDashboard.jsx` using recharts (bar chart by category, line chart by year). Verified against real data: $2,040.25 total spend, $0.0139/mi.

Phase 4 fully committed and pushed (commits `6829497` then `bee8210` for the stats/dashboard addition).

### ✅ Phase 4.5 — Multi-User Auth, Email Verification, Password Reset (COMPLETE)

Inserted before Phase 5 per `AUTOASSIST_ADDENDUM_PHASE_4_5_AUTH.md` — see that file for the full rationale and forward-impact on Phases 5–12. Core auth and the email-verification/password-reset extension (pulled forward from Phase 9) are both done.

**Schema:** `users` table (email, hashed_password, created_at, email_verified), `vehicles.user_id` (nullable during backfill, then `NOT NULL` — backfilled via the real registration endpoint per the addendum's Section 3 plan, not a hand-inserted row), `email_tokens` (single-use, typed `verify_email`/`reset_password`, expiring).

**Core auth — hand-write split honored, then explicitly relaxed partway through** (Muneera's own call, same pattern as the Phase 2→fast-pace shift): `POST /api/auth/register` (hashing + insert) was hand-written with the bcrypt concept walkthrough first (salting, work factor — see GLOSSARY.md's new Authentication section). Muneera then asked to move fast for the rest — `POST /api/auth/login`, `get_current_user`, and `get_owned_vehicle_or_404` were Claude-written with only brief inline explanations rather than the full walkthrough treatment. Worth being honest about in an interview: the addendum called for hand-writing all four; only the first one actually was.

- JWT in an **httpOnly cookie**, 7-day expiry, no refresh token (both per the locked-in decisions — see 3.7 below).
- `get_owned_vehicle_or_404` returns 404, not 403, on a vehicle that exists but belongs to someone else — deliberately doesn't confirm the ID is real.
- `get_service_or_404` was tightened beyond the addendum's literal spec to also check the service belongs to the `vehicle_id` in the URL, not just that the service exists — otherwise a user could edit another user's service record by guessing its ID while going through a vehicle they *do* own. Caught and fixed during the retrofit, not shipped as a gap.
- All Phase 2 endpoints restructured under `/api/vehicles/{vehicle_id}/...` (previously `/api/vehicle`, `/api/schedule`, `/api/services` assumed a single hardcoded vehicle — those paths no longer exist). New `GET/POST /api/vehicles`, `DELETE /api/vehicles/{id}`.
- Frontend: `AuthForm.jsx` (login/register), `Garage.jsx` (vehicle switcher + add-vehicle form), `App.jsx` rewired around an auth-check → vehicle-list → vehicle-scoped-data flow.

**Email verification + password reset via AWS SES** (sandbox mode, Muneera's own verified address): `email_utils.py` (boto3 SES wrapper, HTML+text templates for both), verify-email auto-sent on register, `GET /api/auth/verify-email` (returns HTML, not JSON — a human clicks this from their inbox), `POST /api/auth/forgot-password` (uniform response regardless of whether the email exists — same anti-enumeration principle as login's uniform 401), `POST /api/auth/reset-password`. Frontend: a third "forgot password" mode in `AuthForm.jsx`, new `ResetPasswordForm.jsx`, `App.jsx` detects `?reset_token=` in the URL regardless of login state.

Three real bugs caught and fixed during testing (logged in full in JOURNAL.md, Session 7):
1. **AWS access key exposed in chat mid-project** — rotated immediately (same lesson as the Session 1 GitHub PAT incident: any secret visible outside its intended prompt is compromised, no exceptions).
2. **SES region mismatch** — the SES console showed the identity as "Verified" while displaying a different region than the app's `us-east-1`; SES verification is per-region, not account-wide.
3. **Import-order env bug** — `email_utils.py` read `os.getenv()` at import time but was imported before `database.py` (which calls `load_dotenv()`) in `main.py`, so the real running server silently sent every email with `Source=None` while standalone test scripts happened to mask it via a different import order. A bare `except Exception: pass` around the SES calls hid this completely until logging was added. Fixed by having `email_utils.py` load its own environment rather than depending on import order elsewhere.

**Checkpoint verified directly against the API** (not just the UI): two disposable test accounts confirmed fully isolated from each other *and* from Muneera's real vehicle data — cross-account 404s on vehicles, services, and nested service records; no/garbage/expired token all correctly 401; single-use enforcement on both verify-email and reset-password tokens; a full reset-password cycle (old password rejected, new password works) completed on a disposable account so Muneera's real password was never touched by Claude. 14/14 Phase 4 tests passed throughout, including after two real regressions were caught and fixed (`bcrypt`/`passlib` version incompatibility from a routine dependency install, and the accidental backend-process kill described in this session's setup notes).

Committed as `e69d417`. Immediate next step: **Phase 5 (S3 receipts)**, object keys ownership-scoped per this addendum's Section 5.2 — see that section before writing any Phase 5 code.

### ✅ Phase 5 — Receipt Photo Uploads (S3) — COMPLETE

Bucket `autoassist-receipts-224603709350` (`us-east-1`), created by Muneera directly (console), public access blocked. `autoassist-dev` has a second scoped inline policy for it (`s3:PutObject`, `s3:GetObject` only, resource-restricted to that bucket — no `s3:DeleteObject`, confirmed during testing when Claude's own cleanup attempt correctly got `AccessDenied`).

Pre-signed PUT/GET flow, exactly as the original guide's architecture note recommends (backend never proxies image bytes — no bandwidth/memory pressure, S3 handles the transfer directly): `backend/s3_utils.py`, `POST /api/vehicles/{vehicle_id}/services/{service_id}/receipt-upload-url` and `GET .../receipt-url`, both behind `get_owned_vehicle_or_404` + `get_service_or_404`. Object keys ownership-scoped per the addendum's §5.2: `users/{user_id}/vehicles/{vehicle_id}/receipts/{service_id}/receipt.{ext}`.

**Content-type handled via a fixed server-side allowlist** (`image/jpeg`, `image/png`, `image/webp`, `image/heic`, `image/heif` → their extensions), not a client-provided filename. Worth knowing as a real security catch, not just a design preference: an earlier draft would have taken the filename from the upload request and used it directly in the S3 key — that's a path-traversal-style injection vector (a filename like `../../../whatever` could escape the intended key prefix and write outside the ownership-scoped path). Caught before it shipped.

Frontend: `ReceiptCell.jsx` (per-service-row file input or "View" button depending on whether `receipt_key` is set), wired into `ServiceHistory.jsx`'s new Receipt column. 5MB client-side size cap; no server-side size enforcement yet (would need a pre-signed POST with policy conditions rather than a simple pre-signed PUT — noted as a real, known gap rather than silently skipped).

**Checkpoint fully done, for real** (not just code review): uploaded a genuine PNG through the presigned PUT URL, downloaded it back through the presigned GET URL, confirmed byte-for-byte identical. Confirmed the bucket is truly private — the raw S3 URL without a presigned token returns 403. Cross-account isolation confirmed on both new endpoints (404, not just wrong data). Content-type rejection confirmed for a non-image type. All done against disposable test accounts, never Muneera's real vehicle.

One minor loose end: a tiny leftover test image sits in the bucket at `users/7/vehicles/6/receipts/18/receipt.png` — Claude couldn't delete it (see the no-`DeleteObject` policy note above), harmless, Muneera can remove it manually if she wants a pristine bucket.

### ✅ Phase 6 — Dockerize + docker-compose (COMPLETE — "local MVP complete" milestone)

Whole stack runs with `docker compose up --build`: `db` (Postgres 16, named volume `db_data`, auto-seeded from `seed.sql` via `docker-entrypoint-initdb.d` on first boot only — subsequent starts reuse the volume), `backend` (multi-stage-free `python:3.14-slim` image, waits for `db`'s healthcheck via `depends_on: condition: service_healthy`), `frontend` (multi-stage: Node build → static files served by nginx, which also reverse-proxies `/api/*` to the backend service — mirrors Vite's dev-time proxy so every component's relative `fetch('/api/...')` call keeps working unchanged).

**Colima, not Docker Desktop** — this machine runs Colima as its Docker runtime (see the machine-context note at the top of this project's setup). Nothing in the compose file or Dockerfiles assumes Docker Desktop's GUI; `docker compose` (the CLI plugin, confirmed present under Colima) is all that's used.

**A real, serious risk caught before it caused damage**: the `autoassist-db` container had been running since the very start of the project via a plain `docker run --name autoassist-db ...` with **no volume** — meaning Muneera's real data (her actual Lexus vehicle, her real user account, all Phase 4.5/5 auth and token data) existed only in that container's writable layer. Removing/replacing it for the compose migration would have destroyed it permanently. Caught and handled correctly: regenerated `seed.sql` from the live database first (the committed version was badly stale — predated the entire `users`/`email_tokens`/`vehicles.user_id` schema from Phase 4.5), verified row counts matched exactly and the dump wasn't truncated, *then* removed the old container. The new named-volume setup means this specific risk can't recur — data now survives container removal by design.

**AWS credentials inside the container**: `~/.aws` mounted read-only into the `backend` service so `boto3` finds credentials via the same default chain `aws configure` already set up on the host — Claude never read or copied the actual key values, just added the mount path.

**Checkpoint verified thoroughly, not just "it started"**: full `docker compose up --build` from a genuinely clean state (old non-volume container removed, fresh volume created, auto-seed exercised for real) — all three containers reported healthy/started, real data confirmed present with exact matching row counts, a full register → cookie → authenticated `/api/auth/me` request round-tripped correctly through nginx's proxy, and `boto3` confirmed working inside the container via a live `sts.get_caller_identity()` call. Also tested the more common real-world case — `docker compose down` (containers removed, volume kept) then `docker compose up` again — data persisted correctly, proving the volume genuinely works and the first test wasn't just a fluke of the initial auto-seed.

### ✅ Phase 7 — Deploy to AWS via Terraform (COMPLETE)

**Real cost conversation happened first, with current verified numbers** (not just the guide's estimate): Muneera's AWS account was created after AWS's July 15, 2025 free-tier overhaul, so she's on the $100–200/6-month credit model, not the old 12-months-free-per-service tier the guide's "~$25-30/mo if outside free tier" phrasing assumed. Verified current on-demand rates: EC2 `t3.micro` ≈ $7.59/mo, RDS `db.t3.micro` single-AZ ≈ $12-22/mo depending on source. **Decided and now the standing workflow, not just a one-time test**: destroy the infrastructure between work sessions (`terraform destroy` when done, `terraform apply` to bring it back) rather than always-on, to stretch the credit. Billing alarm set up this time (skipped for Phase 5 when cost was near-zero regardless).

**Separate IAM identity for infrastructure provisioning, deliberately**: `autoassist-terraform` (AdministratorAccess) is distinct from `autoassist-dev` (the app's narrowly-scoped runtime credential — SES-send-only + one S3 bucket), and both are distinct from the EC2 instance's own role (`autoassist-ec2-role`, SES + S3-receipts only, assumed automatically via the instance profile — no static keys on the deployed instance at all). Three identities, three different jobs, three different blast radii — worth naming explicitly in an interview.

- **Remote state**: `infra/bootstrap/` (local-state, one-time — the classic chicken-and-egg, can't store Terraform's own state in a bucket that doesn't exist yet) created `autoassist-terraform-state-224603709350` (S3, versioned, encrypted, public access blocked) and `autoassist-terraform-locks` (DynamoDB, pay-per-request). The main `infra/` project uses these as its S3 backend.
- **Billing alarm**: SNS topic + email subscription (confirmed) + two CloudWatch alarms on `AWS/Billing` `EstimatedCharges` ($10/$50), applied before anything that spends money. **Lives in the same Terraform state as the compute resources**, meaning it gets destroyed and recreated along with everything else on each destroy/apply cycle — fine while resources are torn down (nothing running, nothing to alert on), but worth reconsidering later if continuous alarm coverage across the *apply→destroy* transition itself ever matters.
- **Network**: custom VPC (2 public + 2 private subnets across 2 AZs, IGW, route tables), EC2 security group (80/443 open, 22 restricted to Muneera's IP — `var.my_ip_cidr` in `infra/variables.tf`, needs updating if she works from a different network; port 8000 deliberately NOT opened, backend is only reachable via nginx's proxy on 80), RDS security group (5432 from the EC2 security group only, SG-to-SG reference not a CIDR). No NAT gateway — RDS never needs outbound internet access, saves ~$32/mo for something nothing here needs.
- **RDS**: `db.t3.micro`, private subnets, `publicly_accessible = false` — confirmed directly via the AWS API, not just assumed. `skip_final_snapshot`/`deletion_protection = false` deliberately, matching the destroy-between-sessions workflow (`seed.sql` is the durable source of truth, not the instance).
- **EC2**: `t3.small`. At the time Phase 7 was built this was sized for `docker compose up --build` running a real Vite/npm build on the instance itself; **as of Phase 8 the instance pulls pre-built images from ECR instead** (see the Phase 8 entry below) so `t3.micro` would work again — left at `t3.small` since it's already proven and the cost difference is small. SSH key pair generated by Terraform (app-internal cryptographic material, same treatment as the JWT secret), private key saved locally and git-ignored.
- **`docker-compose.prod.yml`**: standalone (not a compose override) with just `backend`+`frontend` — no local `db` service, since the backend connects to the external RDS endpoint via a `backend/.env` that `user_data` constructs at boot (RDS endpoint, generated DB password and JWT secret, and the instance's own public IP determined via IMDSv2 so the base-URL env vars are correct without knowing the IP in advance).

**Real bugs hit and fixed, all now folded into `user_data.sh.tpl` so future recreations don't repeat them:**
1. Security group description fields reject apostrophes and non-ASCII characters entirely (an em dash broke a `terraform apply` mid-run).
2. `docker compose build` requires buildx 0.17+, which Amazon Linux 2023's `docker` package doesn't ship — first deploy failed outright with "compose build requires buildx 0.17.0 or later." Fixed live via SSH to unblock verification, then added to `user_data.sh.tpl` install steps.
3. Wrote `${BUILDX_VERSION}` (braces) for that fix's own bash variable and immediately collided with Terraform's `templatefile()`, which treats *any* `${...}` in the script as its own interpolation syntax requiring a matching key in the vars map — the exact class of collision already avoided once for `$PUBLIC_IP` earlier in the same file, missed on the second pass. Fixed by dropping the braces (bash doesn't need them; `.` already terminates a variable name).

**Checkpoint fully verified, twice** — once on the initial deploy, once again after a full `terraform destroy` → `terraform apply` cycle (28 resources destroyed, 28 recreated, zero manual intervention needed the second time, confirming the buildx fix actually works): real seed data loaded and confirmed matching row counts, app reachable from outside the VPC at the instance's public IP, a full register → cookie → authenticated request round-tripped through nginx's proxy, and the deployed backend confirmed getting AWS credentials via the EC2 instance role automatically (`arn:aws:sts::224603709350:assumed-role/autoassist-ec2-role/...`) with zero static keys anywhere on the instance.

**Current infra state — DESTROYED**, as of the session that wrote this line. Given destroy-between-sessions is the standing pattern, this line goes stale by design and should never be trusted blindly — a prior session's "I'll destroy it when done" was said but the actual `terraform destroy` never got run, and the infra sat live and billing for an unknown stretch until the next session caught it by checking directly (`aws ec2 describe-instances` / `aws rds describe-db-instances`, not just `terraform state list`, since state can in principle drift from what's actually running — it hadn't here, but verify both, not just one). **Always verify directly before assuming either way**; don't rely on this note.

### ✅ Phase 8 — CI/CD via GitHub Actions (COMPLETE)

**Two open decisions, asked directly rather than defaulted**: registry (chose ECR over GitHub Container Registry — integrates cleanly with the EC2 instance role, no extra credential needed to pull) and deploy mechanism (chose AWS SSM Run Command over SSH via GitHub Secret — no open port needed at all, stronger interview story than bastion/SSH-key management).

**Architecture**: `.github/workflows/ci.yml` runs on every push and PR (backend pytest, frontend lint+build, Docker build validation for both images — no AWS credentials needed for this workflow at all). `.github/workflows/cd.yml` runs on push to `main`: its own independent `test` gate (deliberately not shared with `ci.yml`'s job, since CD triggers in parallel with CI on the same push rather than depending on CI's separate run) → `build-and-push` (both images to ECR) → `deploy` (SSM Run Command to the running instance, or a graceful skip with a clear message if nothing's running — destroy-between-sessions from Phase 7 means CD frequently has nothing to deploy *to*, and that's an expected condition, not a failure).

**GitHub OIDC federation, not static keys**: a new IAM role (`autoassist-github-actions-deploy`) that GitHub Actions assumes via a short-lived OIDC token — no AWS access keys in GitHub Secrets at all, same "avoid static credentials where a role will do" pattern as the EC2 instance role and the `autoassist-dev`/`autoassist-terraform` split. Trust policy restricted to `main` specifically — PR builds from branches or forks never get AWS credentials.

**ECR + the OIDC provider/role live in `infra/bootstrap/`, not the destroyable `infra/` project** — otherwise every `terraform destroy` between sessions would wipe the built images and the CI/CD auth setup along with the EC2/RDS teardown. `infra/bootstrap/`'s own scope note was updated to reflect this (it's no longer just "remote state bootstrap").

**`docker-compose.prod.yml` now uses `image: ${ECR_...}` instead of `build:`** — the instance no longer needs the source tree or `buildx` at all, just pulls two pre-built images. `user_data.sh.tpl` correspondingly simplified: fetches only `docker-compose.prod.yml` + `seed.sql` from S3 (not the full source), authenticates to ECR via the instance role, `docker compose pull && up -d`.

**This phase turned into the longest, most genuinely educational debugging chain in the project so far — six distinct real bugs, each hiding the next:**

1. **CI test failure unrelated to the actual code**: `test_engine.py`/`test_stats.py` test pure functions that never touch a database, but transitively import `database.py` (via `models.py`, just for ORM class definitions), which calls `create_engine(DATABASE_URL)` at import time. No `.env` exists in CI (correctly — it's git-ignored), so `DATABASE_URL` was `None` and engine construction failed before any test ran. Fixed with a syntactically-valid dummy `DATABASE_URL` in the CI/CD workflow env — never actually connected to.
2. **OIDC role assumption failed**: `"Not authorized to perform sts:AssumeRoleWithWebIdentity"`. Root cause #1 — the OIDC provider's thumbprint used `certificates[0]` (the leaf/server cert) instead of the root CA (the correct one is the *last* entry in the chain). AWS validates against the root CA's thumbprint specifically.
3. **Same error, different cause**, found by adding a temporary debug step that actually decoded the JWT rather than guessing further: GitHub's real `sub` claim embeds immutable numeric owner/repo IDs — `repo:Muneeraothman@307808101/autoassist@1308257599:ref:refs/heads/main` — not the simpler `repo:owner/repo:ref:refs/heads/branch` format most OIDC guides show. Fixed the trust policy's `StringLike` condition to match the real format.
4. **`ec2:DescribeInstances` never granted** to the GitHub Actions role — only the SSM actions were. CD's "find the running instance" step failed with `UnauthorizedOperation` even though ECR push (using the same role) had just succeeded.
5. **SSM deploy failed with `InvalidInstanceId: Instances not in a valid state for account`** — the EC2 instance's *own* role needs `AmazonSSMManagedInstanceCore` for its SSM Agent to register as a managed instance at all; this is separate from the GitHub Actions role's `ssm:SendCommand` permission (which only controls who can *issue* commands to an already-registered instance).
6. **Root cause of #5 turned out to be something else entirely**: attaching the missing policy and even fully recreating the instance still didn't register with SSM. Traced by checking the actual AMI being selected — `data.aws_ami` filter `"al2023-ami-*-x86_64"` was matching the ***minimal*** Amazon Linux 2023 variant (`al2023-ami-minimal-2023.12...`), which doesn't ship the SSM Agent at all. Every earlier symptom (no SSM-related console output, empty `describe-instance-information` results, no explicit error anywhere) made sense in hindsight: nothing was misconfigured, the agent binary simply didn't exist on the instance. Fixed by tightening the filter to `"al2023-ami-2*-x86_64"` (standard variant only).

Two smaller, unrelated things caught along the way during verification: the EC2 AMI's **default root volume is only 2GB**, nowhere near enough to pull two real Docker images plus OS overhead — hit "no space left on device" mid-pull; fixed with an explicit 20GB `root_block_device` (~$1.60/mo). And **`var.my_ip_cidr` went stale between sessions** (home/network IP changed), silently breaking SSH — direct HTTP access still worked, which is what made this one non-obvious at first (the app was reachable, only port 22 wasn't).

**Checkpoint fully verified, both halves, with real content checks not just "the pipeline said success"**: pushed a visible frontend change, watched the full pipeline (test → build-and-push → SSM deploy) complete with zero manual steps, then confirmed via `curl` against the actual built JS asset (not the empty `index.html` shell — a React app's content is client-rendered, so checking the raw HTML root proves nothing) that the new text was genuinely being served. Separately: pushed a deliberately failing test, confirmed both CI's `test-backend` job and CD's `build-and-push`/`deploy` jobs never ran (`needs: test` correctly blocked them), then reverted and confirmed a fully green pipeline again.

- **Phase 9:** Email reminders via EventBridge + Lambda + SES.
- **Phase 10:** AI assistant, function-calling over the car's own data (NOT raw SQL generation — this is explicitly the project's security talking point). Strong candidate for the same "Muneera writes the core part herself" treatment given to Phase 4's bucketing logic — the guide itself says tool-schema design "is the skill interviewers probe."
- **Phase 11:** RAG over the actual Lexus owner's manual PDFs (already in the repo, `manuals/OM33566U.pdf` and `manuals/SMG202.pdf`) — pgvector in Postgres is the guide's recommended approach.
- **Phase 12:** README, architecture diagram, demo video, resume bullets, final interview-prep rehearsal (due-date algorithm, tool-calling security design, one thing to improve for production).

## 5. Portability — confirmed genuinely working across machines

This project has been actually tested, not just theoretically documented, running on a second physical laptop (Muneera's dad's, with his explicit permission) from a fresh git clone — full stack (backend + frontend + real database) confirmed working end-to-end, matching the primary laptop exactly.

**What's in Git (safe, portable):** all backend code, all frontend code, `manuals/` (both Lexus PDFs + the stale Honda one), `seed.sql` (full schema + real data, regenerated via `docker exec autoassist-db pg_dump -U postgres -d autoassist --inserts > seed.sql` whenever the data changes meaningfully), `backend/requirements.txt`, `frontend/package.json` (dependencies, not `node_modules`), `backend/Dockerfile`, `frontend/Dockerfile` + `nginx.conf`, `docker-compose.yml`, CLAUDE.md, GLOSSARY.md, JOURNAL.md, LEARNING_PROCESS.md, AUTOASSIST_BUILD_GUIDE.md.

**What's NOT in Git (by design, must be recreated per-machine):** `backend/.env` (holds secrets — DB password, JWT signing key, SES/S3 config; recreated by hand per `.env.example`), `backend/venv/` and `frontend/node_modules/` (only relevant for the manual/non-Docker dev workflow — rebuilt via `pip install -r requirements.txt` / `npm install`), Claude Code's own login (must re-authenticate per machine, `claude` → `/login`).

**As of Phase 6, running the whole stack no longer requires the manual per-service setup at all** — `docker compose up --build` handles Postgres (auto-seeded from `seed.sql` on first run), the backend, and the frontend together, and reads secrets from `backend/.env` via `env_file`. The manual `venv`/`node_modules`/`docker run` workflow described in Section 4's Phase 0 checkpoint still works and remains useful for fast local iteration (hot reload), but is no longer the only — or the primary — way to stand the project up on a fresh machine.

**As of Phase 7**, `infra/` is also in Git — `.tf`/`.tf.tpl` files, `.terraform.lock.hcl` (Terraform's own recommendation, for reproducible provider versions across machines), `docker-compose.prod.yml`. NOT in Git: `infra/.terraform/` (provider plugin cache), any `*.tfstate*` (state lives remotely in S3, never locally), and `infra/autoassist-ec2-key.pem` (the SSH private key Terraform generates on `apply` — regenerated fresh every time, per the destroy-between-sessions workflow, so there's nothing durable to lose by not committing it).

Full fresh-machine setup sequence (confirmed accurate, actually executed once successfully):

```bash
git clone https://github.com/Muneeraothman/autoassist.git
cd autoassist
# Install: Homebrew, Docker Desktop, Python (verify version — see gotcha 7.2), Node, VS Code, Claude Code
open -a Docker   # wait ~1 min for it to fully start
docker run --name autoassist-db -e POSTGRES_PASSWORD=devpassword -e POSTGRES_DB=autoassist -p 5432:5432 -d postgres:16
sleep 3
docker exec -i autoassist-db psql -U postgres -d autoassist < seed.sql
cd backend
python3.14 -m venv venv   # NOT bare python3 — see gotcha 7.2
source venv/bin/activate
pip install -r requirements.txt
echo 'DATABASE_URL=postgresql://postgres:devpassword@localhost:5432/autoassist' > .env
uvicorn main:app --reload   # leave running in this tab
# new tab:
cd ../frontend
npm install
npm run dev
```

## 6. Environment / machine notes

- **Primary laptop:** Muneera's own Mac, zsh shell, has a persistent alias issue where new terminal tabs default `python` → `/usr/local/bin/python3` instead of the venv — every fresh tab needs `unalias python && source venv/bin/activate` before backend work.
- **Secondary laptop:** her dad's Mac. He was explicitly asked and confirmed he's fine with dev tools (Homebrew/Docker/VS Code/Claude Code) being installed on his machine. Muneera used her own AWS account and her own GitHub account throughout — nothing of his was used for actual credentials. A real mishap happened here worth knowing: Claude Code auto-logged into an already-signed-in session that turned out to be her DAD's Claude account (rothmaan@gmail.com), not hers — caught via `/status`, corrected via `/login`. Always run `/status` in Claude Code on a shared/unfamiliar machine before doing real work, to confirm which account is active.
- Git identity (`user.email`/`user.name`) was not globally configured on the dad's laptop and had to be set explicitly (`git config --global user.name/user.email`) before Claude Code could make its first commit there.
- GitHub authentication on the dad's laptop required a real Personal Access Token, and the first couple of attempts failed due to (a) commands being typed into the wrong place (see 7.4) and (b) a case-sensitivity issue — GitHub wanted the exact-case username `Muneeraothman`, and a lowercase attempt failed authentication. If `git push` fails with "Invalid username or token," check exact username casing first.

## 7. Environment Gotchas — READ BEFORE GIVING MULTI-STEP TERMINAL INSTRUCTIONS

This is the single most failure-prone part of working with Muneera and is worth internalizing fully.

### 7.1 — Terminal paste/multi-line issues (recurring theme, many forms)

Multi-line heredocs have stripped indentation on paste. The most reliable file-creation method found across this whole project: have her use VS Code to write/paste code files (not the terminal) — select-all + delete + paste, verify via a fresh terminal `cat` afterward. For short, single-line-safe content, `printf '...\n...' > file` (a single unbroken line with escaped `\n`s) was also proven reliable when VS Code wasn't available. Never assume a multi-step paste landed correctly — always verify with `cat` or `git status` in a FRESH terminal tab before proceeding.

### 7.2 — Python version mismatches across machines

`requirements.txt` was built against Python 3.11 originally, but a second laptop's default `python3` was 3.9, which cannot satisfy `annotated-types==0.8.0` (needs 3.10+). Symptom: `pip install -r requirements.txt` fails with a version-not-found error that looks like a broken package, but is actually a Python-version mismatch. Fix: always explicitly recreate the venv with a known-good Python version (`python3.14 -m venv venv`, or whatever Homebrew installed), not the bare `python3` command, on any new machine.

### 7.3 — seed.sql cannot be reloaded against a non-empty database

The file is a plain `pg_dump --inserts` output with no DROP TABLE statements. Reapplying it against a database that already has the tables throws a wall of silent "already exists" errors and does NOT actually reset the data. Correct reset procedure, confirmed working:

```bash
docker exec -i autoassist-db psql -U postgres -d autoassist -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker exec -i autoassist-db psql -U postgres -d autoassist < seed.sql
```

Also, `psql` is generally not installed on the host Mac itself — it only exists inside the `autoassist-db` container, so always reach it via `docker exec`, not a bare `psql` command.

### 7.4 — Typing commands directly into the Claude Code chat prompt does NOT execute them

This caused significant, repeated confusion, especially around `git config` and `git push`. Claude Code's chat window is for natural-language messages; the `!` prefix on its own message (e.g. `! git push`, sent as a complete, standalone message with nothing else in it) runs a real shell command from inside the session. Sending it merged with other text in the same message does NOT work reliably. The consistently reliable fallback: have Muneera open a genuinely separate, plain terminal tab (not the one showing the claude prompt/task list) and type the command there directly. This was the pattern that ultimately worked for both `git config` and `git push` after `!`-prefix attempts got garbled by paste-timing issues.

### 7.5 — Zombie background processes holding port 8000

Old `uvicorn --reload` processes from closed/"broken-looking" terminal tabs kept silently running in the background, causing `[Errno 48] Address already in use` on subsequent `uvicorn main:app --reload` attempts. Diagnose with `lsof -ti:8000` (prints PIDs), fix with `kill <pid> <pid>`.

### 7.6 — Docker Desktop must be actually RUNNING, not just installed

`docker ps`/`docker run` fail with a "cannot connect to the Docker daemon" error if Docker Desktop (the actual GUI app) isn't open, even though the `docker` CLI itself is installed correctly. Fix: `open -a Docker`, wait ~30–60 seconds for it to fully boot, then retry.

### 7.7 — Node.js is not assumed pre-installed

Unlike Python, a fresh machine may not have Node/npm at all. `brew install node` if `npm: command not found`.

### 7.8 — Never let credentials pass through this chat

This happened once for real (a GitHub Personal Access Token was accidentally pasted into chat during early setup, and immediately revoked/regenerated as the correct response) and Claude Code has since proactively, correctly refused to touch AWS credentials or generate/store them itself, redirecting Muneera to enter them directly in her own terminal instead. Maintain this policy strictly for any future credential (AWS keys, OpenAI API keys in Phase 10, etc.) — never ask for or accept a real secret pasted into the chat, always redirect to a local terminal prompt.

## 8. Standing process / preferences (for Claude, going forward)

- Explain new concepts in plain language before code, with analogies, for anything genuinely core to a phase's interview story — see Section 3.3 for exactly which parts of Phase 4 got this treatment and why. Default to the faster build-then-summarize pace for everything else, per Muneera's explicit later request.
- Update GLOSSARY.md and JOURNAL.md as work happens — this has been consistently done well by Claude Code directly editing these files (much easier now that Claude Code can write directly into the repo, versus the earlier chat-only era where generated files had to be manually downloaded and dragged in, which was a recurring source of friction and files going stale).
- Turn real bugs into documented "interview story" journal entries — several excellent ones already exist (the three-layer file-mixup/zombie-process/Docker-not-running debugging session from Phase 2; the mileage-field-staleness React bug from Phase 3; the Decimal/float-conversion bug caught during Phase 4 code review). Continue this pattern for any new real bug encountered.
- When a genuinely new environment gotcha is discovered (in the spirit of Section 7), document it — Claude Code has been proactively good about this (e.g., writing memory notes about the seed.sql/psql reset gotcha) and should keep doing so.
- Muneera has explicitly and repeatedly asked to move fast and finish the project — respect that as the default, but don't be afraid to flag (briefly, without being preachy about it) when something is worth slowing down for, the way the Phase 4 bucketing logic and the AWS credential/billing decisions were both correctly flagged as worth extra care despite the general "move fast" instruction. She has responded well to those flags when they were brief, concrete, and left the actual decision to her.

## 9. Immediate next action for whoever picks this up

1. Confirm current git status on whichever machine is being used (`git status`, `git log --oneline -3`) — don't assume the last-known committed state is current.
2. **Check whether Phase 7/8's AWS infrastructure is actually running before assuming either way** — this has already bitten the project once (a session said it would `terraform destroy` on wrap-up, didn't, and the infra sat live for an unknown stretch until the next session caught it). Don't trust a prior session's "current infra state" note or `terraform state list` alone; confirm directly: `AWS_PROFILE=terraform aws ec2 describe-instances --filters "Name=tag:Name,Values=autoassist-app"` and `aws rds describe-db-instances --db-instance-identifier autoassist-db --region us-east-1`. If anything's running and isn't being actively used, `terraform destroy` it (`cd infra`, `export AWS_PROFILE=terraform`, set `TF_VAR_db_password`/`TF_VAR_jwt_secret_key`, `terraform destroy`).
3. **Check `var.my_ip_cidr` in `infra/variables.tf` is still current** if planning to SSH in (`curl https://checkip.amazonaws.com` vs. the value in that file) — this went stale between sessions once already and silently broke SSH while HTTP access kept working, which made it non-obvious.
4. Proceed to **Phase 9 — Email reminders via EventBridge + Lambda + SES**: a Lambda function that queries `/api/upcoming` (or imports `engine.py` directly — discuss the tradeoff) for anything OVERDUE/DUE_SOON not notified in the last 7 days, a `notifications_log` table to prevent daily nagging, an EventBridge scheduled rule (daily), all via Terraform. Per Phase 4.5's addendum, this needs to run *per user* now (join `vehicles` to `users.email`), not once for "the vehicle" as the original guide assumed pre-multi-tenancy. Decide whether Lambda queries RDS directly (needs VPC config) or calls the public API (simpler, no VPC needed) — both are legitimate, discuss with Muneera rather than defaulting.
