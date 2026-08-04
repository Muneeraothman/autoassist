# AutoAssist Journal

A running log of what I did and learned each session. One entry per session/day.

---

## Session 1 — Phase 0: Setup

**What I did:**
- Installed Homebrew (a package manager — see GLOSSARY.md)
- Installed Git, Node, and confirmed Python was already on my Mac
- Installed TablePlus (a visual tool for looking at databases later)
- Created a GitHub account and a new repo called `autoassist`
- Cloned the repo to my Mac (`git clone`)
- Chose my stack: **Python + FastAPI** for the backend, **OpenAI** for the AI assistant later
- Figured out my car for the project: started with my 2020 Acura TLX, ended up switching to my **mom's 2013 Honda Accord** instead
- Uploaded the Accord's real owner's manual and found the **Maintenance Minder** section — the codes (A, B, 1, 2, 3...) and real mileage intervals for oil, tires, transmission fluid, spark plugs, coolant, etc.
- Made a `manuals/` folder in the repo and committed the manual PDF
- Hit and fixed two real problems:
  - Paste stopped working in Terminal — fixed by opening a fresh Terminal window
  - `git push` kept failing with "password authentication not supported" — GitHub requires a **Personal Access Token** instead of your actual password now. Generated one, and (important lesson) **revoked it immediately after accidentally pasting it into chat**, since any secret typed outside its intended password prompt should be treated as compromised and replaced.

**What I learned:**
- Docker doesn't touch my Mac directly — it runs things in sealed "containers," which is why it's safe to experiment with.
- `git add` → `git commit` → `git push` is a three-step process: stage a snapshot, save it locally, then send it to GitHub. Nothing goes to GitHub until you `push`.
- My car's Acura/Honda-style Maintenance Minder doesn't use a simple "5,000 miles" table like some brands — it calculates a live oil-life percentage from actual driving conditions and only falls back to fixed mileage numbers for specific things (like "replace air filter every 15,000 mi if you drive in dusty conditions").
- Even though the car already has its own dashboard reminder system, my app isn't redundant — the car's system is temporary/on-dash only, while AutoAssist stores permanent history, costs, and can be asked questions.

**Gotchas / things that took longer than expected:**
- Terminal paste silently failing was confusing at first — no error, it just didn't work. Turned out to be terminal-specific weirdness, fixed by restarting the terminal window.
- Almost pushed a broken/empty commit because I ran `git push` before actually running `git add` + `git commit` first. Lesson: always run `git status` if something seems off — it tells you exactly what's staged vs. not.

---

## Session 3 — Concept Review Quiz (before Phase 1 hands-on work)

Did a full quiz review of everything from Phase 0 before touching new material. Format: get asked a concept, answer, get re-taught if shaky.

**Solid on the first try:**
- Difference between Git and GitHub
- What a Personal Access Token is (and why it's sensitive — lived through revoking one after pasting it somewhere it shouldn't have been)
- What Postgres is
- How Docker + Postgres fit together (Postgres runs inside a Docker container)

**Needed re-teaching:**
- **Homebrew** — had installed it but was never actually taught what it does. Re-explained as a package manager (like an App Store for command-line tools) — now solid.
- **git add / git commit / git push** — remembered push (since that's when the token/password prompt happened) but not add or commit. Re-taught using the actual real commands from Session 1 (staging `manuals/`, committing with message, then pushing) plus a box-mailing analogy: add = put in box, commit = seal box with label (saved on my computer only), push = mail box to GitHub.

**Takeaway:** review sessions like this are genuinely useful — worth doing again before starting each new phase, not just once at the start.

---



**What I'm doing:**
- Starting Postgres locally using Docker
- About to design the `vehicles` and `schedule_items` tables myself
- Loading in the real Accord maintenance codes as seed data

*(This section will be filled in as we go.)*

---

## Session 4 — Phase 2: Schedule & Service Endpoints, plus the Lexus Switch

**What I did:**
- Switched the project's car from the 2013 Honda Accord to my actual daily driver, a **2002 Lexus ES300** — added its owner's manual PDFs (`manuals/OM33566U.pdf`, `manuals/SMG202.pdf`) and refreshed `seed.sql` with the Lexus's real fixed-interval maintenance schedule. (`manuals/2A1313OM.pdf`, the old Accord manual, is still in the repo but no longer the source of truth.)
- Built out `main.py` so it now has three working endpoints: `GET /api/vehicle` (already existed), plus new `GET /api/schedule` and `GET /api/services`, each querying its table via SQLAlchemy and returning JSON.

**What I learned:**
- The Lexus doesn't have anything like Honda's Maintenance Minder — its manual just lists a fixed mileage/time table, which is actually simpler to model: no live oil-life calculation, just compare current mileage/date against fixed intervals.

**Gotchas / things that took longer than expected:**
- **Files getting mixed up while editing** — with `main.py`, `models.py`, and `database.py` all open and being edited around the same time, it was easy to lose track of which file a change actually landed in. Lesson: check `git diff` after edits to confirm the change went where expected, rather than assuming.
- **Zombie server process on port 8000** — restarting `uvicorn` failed because a previous run was still holding port 8000 in the background even though the terminal that started it was closed. Fixed by finding the leftover process (`lsof -i :8000`) and killing it (`kill <PID>`) before starting the server again.
- **Docker Desktop not running** — Postgres commands failed with a connection error because Docker Desktop (the actual app) wasn't open, even though Docker itself is installed. Docker Desktop has to be running in the background before `docker run`/`docker ps` will work.

**Phase 2 review quiz — multiple choice, one at a time:**

Solid on the first try:
- What `Depends(get_db)` does (opens a session, hands it to the endpoint, closes it after)
- Why Docker commands were failing (Docker Desktop, the app, wasn't running — separate from Docker being installed)
- Lexus vs. Honda scheduling (fixed mileage/time table vs. Honda's live oil-life % + dashboard codes)

Needed re-teaching:
- **Why the port 8000 error happened** — first guessed it was a bad `DATABASE_URL`; that variable only affects the Postgres connection, not the port the FastAPI server itself listens on. The actual cause was a zombie `uvicorn` process from an earlier run still holding the port.
- **Finding what's using a port** — first guessed `kill -9 8000` (which would try to kill a process with PID 8000, not free the port). Correct command is `lsof -i :8000` to find the actual PID, *then* `kill <PID>`.
- **`GET /api/services` walkthrough (own words, no multiple choice)** — described it as listing `schedule_items`. Re-taught the distinction: `schedule_items` is the *reference* table (what should happen, at what interval); `service_records` (what `/api/services` actually queries) is the *history* table (what maintenance actually happened, when, and for how much). Also missed the manual serialization step (dates converted to `str`, `cost` converted to `float`/`None`) since raw `date`/`Decimal` values aren't JSON-serializable.

**Takeaway:** the `schedule_items` vs. `service_records` mix-up lines up with the "files getting mixed up while editing" gotcha above — worth deliberately re-reading `models.py` next session before touching either table again.

---

## Session 5 — Phase 2: Finishing the Backend API (2026-07-27)

**What I did:**
- Built `PATCH /api/vehicle/mileage` — updates `current_mileage` and recomputes `avg_miles_per_day` from the elapsed time and mileage since the last update. Wrote the `MileageUpdate` Pydantic model (`Field(gt=0)`) and the three-way logic (reject a decrease, skip the recompute if less than a day has passed, otherwise divide miles driven by days elapsed) myself before it went into `main.py`.
- Fixed `GET /api/services` to sort newest-first (`.order_by(ServiceRecord.service_date.desc())`) and added the optional `?schedule_item_id=` filter.
- Built `POST /api/services` (creates a record, `ServiceCreate` Pydantic model with a custom `@field_validator` rejecting future dates, plus a route-level check rejecting `mileage_at_service` more than 500 miles ahead of the vehicle's current mileage — my call, since backfilling older service records with lower mileage should still be allowed), `PUT /api/services/{id}` (full update, reuses `ServiceCreate`), and `DELETE /api/services/{id}`.
- Added consistent 404 handling across every route via two small helpers, `get_vehicle_or_404` and `get_service_or_404` — previously `db.query(...).first()` returning `None` would crash with an unhandled `AttributeError` instead of a clean error.
- Had Claude test every new endpoint with curl (valid + invalid cases for each validation rule, 404s on bad IDs, decrease rejection) instead of doing it by hand this session, to move faster since the underlying patterns (Pydantic validation, `db.add`/`commit`/`refresh`) were already covered in earlier phases.

**What I learned:**
- The split between **Pydantic-level validation** (shape/type/static bounds, no DB access — e.g. cost ≥ 0, date not in the future) and **route-level validation** (needs a DB lookup — e.g. mileage decrease, mileage-vs-current-mileage sanity bound) is a real architectural line, not just a style choice: Pydantic models have no access to `db`.
- A freshly-built ORM object (`ServiceRecord(...)`) isn't tracked by SQLAlchemy until `db.add(...)` — different from `PATCH`, which only needed `db.commit()` because it modified an object already fetched via `db.query(...)`.

**Gotchas / things that took longer than expected:**
- **Resetting the DB from `seed.sql` didn't work as documented.** `CLAUDE.md` says `psql "$DATABASE_URL" -f seed.sql`, but `psql` isn't installed on the Mac itself — it only exists inside the `autoassist-db` Docker container. On top of that, `seed.sql` is a plain dump with no `DROP TABLE` statements, so reapplying it against a database that already has the tables just threw a wall of "already exists" errors and silently left stale test data in place. The actual fix: `docker exec` into the container, `DROP SCHEMA public CASCADE; CREATE SCHEMA public;` first, *then* reload `seed.sql`.

**Still pending before Phase 3:** the full Phase 2 review quiz needs to happen on this session's material specifically — the quiz logged earlier only covered the three `GET` endpoints, not the `PATCH`/`POST`/`PUT`/`DELETE` work or the validation-split concept from this session.

*(Update, same day: did a 5-question multiple-choice quiz + one open-ended question on this session's material. Missed 4 of the 5 multiple-choice questions on the first pass — Pydantic-vs-route validation split, `db.add()` vs `db.commit()`, the missing-vehicle 404 bug, and why the future-date rule needs a custom validator instead of `Field()` — each was re-taught in full before moving on. Correctly got the query-parameter-vs-path-parameter question. Didn't attempt the final open-ended "walk through a POST request" question ("idk"), so I did the full walkthrough instead. After that quiz, explicitly asked to stop doing the fill-in-the-blank/quiz process for the rest of the project — see below.)*

---

## Session 6 — Phase 3: Frontend, and a Pacing Change (2026-07-29)

**What changed first:** partway through the Phase 2 review quiz, decided to stop the teaching-loop process (fill-in-the-blank, step-by-step walkthroughs, phase-end quizzes) for the rest of the project. From here on: build each phase, test it, get a summary, check in at phase boundaries only. `LEARNING_PROCESS.md`/`CLAUDE.md` still describe the old process on disk; that's now intentionally stale rather than actively followed.

**What got built (Phase 3 — Frontend):**
- Scaffolded `frontend/` with Vite + React, configured `vite.config.js` to proxy `/api/*` to the FastAPI backend on port 8000 for local dev.
- Three components composed in `App.jsx`: `VehicleCard` (vehicle info + inline mileage update), `LogServiceForm` (dropdown of schedule items or "Other/Repair", date, mileage pre-filled with current mileage, cost, performed by, notes), `ServiceHistory` (table, newest first, filterable by schedule item).
- Plain `useState`/`fetch`, no state management library — vehicle data lives in `App` and gets passed down as props ("lifting state up") since both `VehicleCard` and `LogServiceForm` need it.
- Basic dark/light-aware styling in `App.css`, loading and empty states on every fetch-backed view.

**Bug caught during actual browser testing (not just curl):** the mileage field in `LogServiceForm` pre-filled once from `current_mileage` and then never updated again, even after `VehicleCard` successfully changed the vehicle's mileage — so logging a service right after updating mileage would silently use the *stale* pre-filled number instead of the new one. Fixed by tracking a separate `mileageTouched` flag: the field re-syncs to `current_mileage` whenever it changes, unless the user has actually typed into it, and resets to "untouched" after each successful submit. This is exactly the kind of bug that never shows up in an API-only curl test — it only appeared once the two components were exercised together in a real browser session.

**Full-loop checkpoint (via actual browser automation, not just curl):** updated mileage on the vehicle card → confirmed the average recalculated correctly → logged a service (pre-filled mileage matched the just-updated value) → saw it appear at the top of Service History → refreshed the page → data was still there, confirming it's really coming from Postgres and not just sitting in React state. No console errors.

**Gotchas:** none new this session beyond the mileage pre-fill bug above — DB reset (`docker exec` + schema drop, from Session 5) worked cleanly on the first try this time.

---

## Session 7 — Phase 4.5: Multi-User Auth, Email Verification, Password Reset (2026-08-03)

**What I did:**
- Added multi-user auth: `users` table, `vehicles.user_id`, JWT stored in an httpOnly cookie (7-day expiry, no refresh token — kept intentionally simple for a portfolio project's scope), password hashing with bcrypt via passlib.
- Wrote the core security-critical pieces myself with Claude explaining concepts first: the bcrypt hashing/insert logic in `POST /api/auth/register`, and (once I asked to move faster) `POST /api/auth/login`, the `get_current_user` dependency, and `get_owned_vehicle_or_404` — the actual ownership boundary, returns 404 rather than 403 so a vehicle ID belonging to someone else doesn't even reveal it exists.
- Had Claude retrofit every existing endpoint to require auth and live under `/api/vehicles/{vehicle_id}/...`, add new vehicle CRUD endpoints, and build the login/register/garage frontend.
- Set up AWS SES for real email sending (sandbox mode, my own verified email address) and had Claude build email verification and password reset on top of it.

**What I learned:**
- httpOnly cookies vs. an `Authorization` header for a JWT — httpOnly means client-side JS can never read the token (defends against XSS token theft), but it also means the browser sends it automatically on same-origin requests, so the backend reads it via `Request.cookies`, not a header.
- Why bcrypt is deliberately slow (the "work factor") and why every password gets its own random salt instead of one shared secret for the whole app — defeats both brute-forcing and precomputed rainbow-table lookups.
- Verification/reset tokens are deliberately NOT JWTs — they're random DB-backed tokens (`secrets.token_urlsafe`) with a `used_at` column, because they need to be single-use and revocable, which a stateless JWT can't do without extra tracked state anyway.

**Gotchas / things that took longer than expected:**
- **AWS access key exposed in chat, mid-project.** Rotated it immediately (revoked the old key, generated a new one) — same lesson as the GitHub Personal Access Token in Session 1: any secret typed somewhere other than its intended prompt is compromised the moment it's visible, no exceptions, rotate first and ask questions later.
- **SES region mismatch.** My email identity showed "Verified" in the SES console, but sending still failed with `MessageRejected: Email address is not verified`. The console was displaying a different AWS region than the one the app was actually configured to send from (`us-east-1`) — SES identity verification is per-region, not account-wide, which isn't obvious from the console UI alone.
- **A real "worked in testing, silently broken for real" bug.** The email-sending module read its config (`SES_SENDER_EMAIL`, etc.) from environment variables at import time, but got imported *before* the other module that actually loads the `.env` file — so the real running server was silently sending every email with `Source=None`, while a standalone test script happened to import things in an order that accidentally loaded `.env` first and masked the bug completely. Fixed by having the email module load its own environment instead of depending on some other file being imported first — a good example of why implicit import-order dependencies are dangerous.
- **A silent `except: pass` around the email-sending calls was hiding the bug above.** It existed so a real-world SES sandbox restriction (can't email unverified addresses) wouldn't block account registration entirely — a reasonable intent — but with zero logging it also swallowed the actual `Source=None` bug without a trace. Added a log line before retesting, and the real cause showed up immediately. Lesson: "best-effort, don't block on this" is a reasonable design choice, but it should never mean "silent" — always log what got swallowed.

---

## Session 8 — Phase 5: S3 Receipt Photo Uploads (2026-08-03)

**What I did:**
- Created the S3 bucket myself (`autoassist-receipts-224603709350`, `us-east-1`, public access blocked) and attached a second scoped IAM policy to `autoassist-dev` — `s3:PutObject`/`s3:GetObject` only, restricted to that one bucket. Same least-privilege pattern as the SES policy from Phase 4.5.
- Had Claude build the pre-signed upload/download flow: `backend/s3_utils.py`, two new endpoints, and the frontend receipt column with an upload input / view button.

**What I learned:**
- Why the app never touches the actual image bytes — the backend only ever generates a signed URL; the browser uploads and downloads directly against S3. This avoids the backend having to buffer large files in memory or spend its own bandwidth relaying them.
- Object keys are ownership-scoped (`users/{user_id}/vehicles/{vehicle_id}/receipts/{service_id}/...`), decided as part of the Phase 4.5 addendum specifically so this phase wouldn't need a retrofit later — a good example of "build it multi-tenant from day one" paying off in practice.

**Gotchas / things that took longer than expected:**
- **A path-traversal-shaped bug caught before it ever shipped.** An early version of the upload-URL endpoint design took the filename straight from the upload request and used it to build the S3 object key. Claude caught that a filename like `../../../whatever` could escape the intended `users/{id}/vehicles/{id}/receipts/{id}/` prefix and write somewhere unintended in the bucket. Fixed by mapping the request's `content_type` through a small fixed allowlist (`image/jpeg` → `jpg`, etc.) server-side instead — no string coming from the client ever ends up inside the S3 key at all. Good real example of "validate against an allowlist, don't sanitize a blocklist" — an interview-worthy security detail even though it never actually reached production.
- **Cleanup went sideways from a Postgres detail I didn't know**: after testing with disposable accounts, a `docker exec ... psql -c "DELETE ...; DELETE ...; DELETE ..."` multi-statement cleanup partially failed (an `email_tokens` foreign key I forgot to clear first), and the *entire batch* silently rolled back — including the deletes that had already reported success in the output. Learned that `psql -c` with multiple semicolon-separated statements runs as one implicit transaction; one failure anywhere in the batch undoes all of it, even the parts that looked like they'd already succeeded. Fixed by redoing the cleanup as a single correctly-ordered batch (tokens → services → vehicle → users) instead of multiple separate commands.

---

## Session 9 — Phase 6: Docker Compose, "Local MVP Complete" (2026-08-03)

**What I did:**
- Had Claude build `backend/Dockerfile`, `frontend/Dockerfile` (multi-stage: Node build → nginx serves the static files, nginx also reverse-proxies `/api/*` to the backend container so every component's existing `fetch('/api/...')` call keeps working unchanged), and `docker-compose.yml` wiring all three services together with a healthcheck on the database and `depends_on: condition: service_healthy` on the backend.
- Confirmed the whole thing actually works with `docker compose up --build` from a genuinely clean state, not just "it built."

**What I learned:**
- Why the db needs a healthcheck and the backend needs `depends_on: condition: service_healthy` instead of a plain `depends_on`: Postgres accepting TCP connections isn't the same moment as it being ready to actually run queries — a plain `depends_on` only waits for the container to *start*, not for the database inside it to be usable, which is a classic source of "works most of the time, randomly fails on a slow machine" bugs.
- Docker named volumes vs. a container's own writable layer: data in the writable layer disappears the moment the container is removed (`docker rm`); data in a named volume survives container removal and gets reattached to whatever container mounts that same volume next.

**Gotchas / things that took longer than expected:**
- **The single scariest moment of the project so far, caught in time.** The `autoassist-db` container had been running since Session 1 via a plain `docker run` with no volume flag at all — meaning my real data (my actual car, my real account, everything from the last two sessions) existed *only* inside that one container's writable layer. Migrating to Docker Compose meant replacing that container, which would have deleted all of it permanently with zero warning. Claude caught this before touching anything, regenerated `seed.sql` from the live database first (the version already in Git was badly out of date — it predated the entire multi-user auth schema from Phase 4.5), and verified the row counts matched exactly before removing the old container. Real lesson, not just a "glad that worked out": always ask "where does this data actually live, and does removing this container delete it?" before running any `docker rm` — not every container is backed by a volume just because it's been running fine for weeks.
- **`docker compose down` vs. `docker compose down -v`** — the former removes containers but keeps named volumes (data survives); the latter wipes volumes too (data gone). Easy to mix these up and not realize which one you actually ran until it's too late.

---

## Session 10 — Phase 7 (part 1): Terraform Remote State, Billing Alarm, Network (2026-08-04)

**What I did:**
- Had a real conversation about cost before touching anything, since Terraform in this phase means actual continuous compute spend, not S3/SES pennies. Learned my AWS account (created after July 2025) is on a $200/6-month credit model, not the old 12-month free tier the build guide assumed — real numbers, not the guide's estimate. Decided to destroy the infrastructure between work sessions instead of leaving it running continuously, and to actually set up the billing alarm this time (skipped it for Phase 5, where the cost was near-zero regardless).
- Created a second, separate IAM user (`autoassist-terraform`, admin-level) just for infrastructure provisioning — deliberately not reusing `autoassist-dev`, the app's own narrowly-scoped runtime credential.
- Bootstrapped Terraform's remote state (S3 + DynamoDB), then applied the billing alarm (SNS + two CloudWatch alarms) as the very first real resource, before anything that spends money. Then the network layer: VPC, public/private subnets across 2 AZs, security groups.

**What I learned:**
- Why infrastructure-provisioning credentials and application-runtime credentials should be separate identities: they have completely different jobs (one manages the AWS account itself, one just needs to send an email and touch one S3 bucket), so they should have completely different blast radii if either one is ever compromised.
- Why RDS in a private subnet doesn't need a NAT gateway even though NAT is usually mentioned in the same breath as private subnets: NAT is only needed when something in the private subnet needs to *initiate* outbound connections to the internet. RDS never does that — it only accepts inbound connections from EC2 within the VPC. Skipping the NAT gateway saves about $32/mo for something nothing here actually needs.
- The "chicken-and-egg" problem with Terraform remote state is real, not just a guide talking point: you can't store Terraform's state in an S3 bucket that Terraform itself needs to create, so that one bucket has to be created by a tiny separate Terraform config using local state, just once.

**Gotchas / things that took longer than expected:**
- **AWS security group description fields have a surprisingly strict character set** — no apostrophes, and ASCII only. Wrote "SSH from Muneera's IP only" and "...only — no direct internet access" (an em dash), and both failed `terraform apply` with a validation error partway through, after several other resources had already been created successfully. Small thing, but a good reminder that cloud APIs often have string-field restrictions that don't show up until you actually hit them.
