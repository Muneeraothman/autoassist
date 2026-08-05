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

---

## Session 11 — Phase 7 (part 2): RDS, EC2, Full Deploy, and the Destroy/Apply Cycle (2026-08-04)

**What I did:**
- Created RDS (private subnets, confirmed not publicly accessible from AWS's own API, not just assumed) and an EC2 instance with an IAM instance role instead of static keys, running the whole app via `docker compose up --build` inside a `user_data` boot script.
- Got the app code onto the instance via an S3 tarball rather than a `git clone` from the private repo — sidesteps needing a GitHub deploy key for something Phase 8's real CI/CD pipeline will replace soon anyway.
- Loaded the real seed data against RDS, then verified the actual deployed app from outside the VPC — registered a test account against the real public IP, full cookie-auth round trip through nginx.
- Ran a genuine `terraform destroy` followed by `terraform apply` — the real IaC test — and confirmed this is now the standing pattern between work sessions, not a one-time thing.

**What I learned:**
- Why an EC2 instance role beats static access keys baked into user_data or an AMI: the credentials rotate automatically and are never actually visible as a string anywhere — confirmed this for real by running `sts.get_caller_identity()` from inside the deployed backend container and seeing `assumed-role/autoassist-ec2-role/...` come back, not a fixed access key ID.
- Terraform's `templatefile()` function treats *every* `${...}` in a file as its own interpolation syntax needing a matching variable — including ones meant as plain bash variable references inside a shell script. Bash itself doesn't need the braces unless the variable name would otherwise run into surrounding text (`$VAR.suffix` already parses correctly, since `.` isn't a valid identifier character), so dropping them is the actual fix, not something Terraform can be told to ignore.

**Gotchas / things that took longer than expected:**
- **`docker compose build` failing with "requires buildx 0.17.0 or later"** on the very first deploy — Amazon Linux 2023's stock `docker` package doesn't include a modern buildx plugin. Fixed live over SSH to unblock verification (downloaded the buildx binary from GitHub releases directly), then folded the same fix into the `user_data` script so it wouldn't have to be done by hand again — verified this worked by actually running the full destroy/apply cycle afterward and watching it succeed with zero manual steps the second time.
- **Immediately re-hit the exact templatefile/bash `${}` collision I'd already dodged once in the same file** — this time in the buildx-version variable I'd just added to fix the bug above. `terraform destroy` failed before doing anything, with a clear error naming the missing template variable, which made the actual cause easy to spot — but it's a good reminder that a pattern learned once in one spot doesn't automatically get applied to new code added later in the same file.
- **An architecture question worth revisiting later, not urgent now**: the billing alarm lives in the same Terraform state as the compute resources, so it gets destroyed and recreated along with everything else on each destroy/apply cycle. Fine for now (nothing's running while torn down, so nothing needs alerting on), but if the destroy/apply gap itself ever needs alarm coverage, it'd need to move to somewhere that persists — the bootstrap module, most likely.

---

## Session 12 — Phase 8: CI/CD via GitHub Actions (2026-08-04/05)

**What I did:**
- Picked ECR over GitHub Container Registry and SSM Run Command over SSH deploy, both asked directly rather than defaulted.
- Had Claude build the CI/CD workflows, an ECR repo pair + GitHub OIDC federation (so GitHub Actions never holds a static AWS key at all), and switch the EC2 deploy from "build on the instance" to "pull pre-built images."
- Ran the actual checkpoint twice: a real visible change auto-deploying with zero manual steps, and a deliberately broken test proving CI/CD blocks on failure.

**What I learned:**
- OIDC federation vs. long-lived access keys in GitHub Secrets: the workflow gets a short-lived token minted per-run, scoped by a trust policy condition on the repo/branch, and never touches a credential that could leak from a log or a compromised dependency the way a stored secret could.
- Why an EC2 instance's *own* IAM role needs SSM permissions separately from whoever is *calling* SSM against it — two different questions ("can this instance register itself as managed" vs. "can this caller send it commands") that I'd assumed were the same permission.
- `curl`-testing a React app's root HTML tells you almost nothing, because the actual content is rendered client-side into an empty `<div id="root">` shell — I have to check the actual JS bundle (or use a real browser) to verify anything about what's genuinely displayed.

**Gotchas / things that took longer than expected — this was the longest bug chase of the project so far, six real problems stacked on top of each other:**
- **A CI test failure that had nothing to do with the code being tested.** `test_engine.py`/`test_stats.py` are pure-function tests, but they import `models.py` for the ORM class definitions, which imports `database.py`, which creates a real database connection object at import time using `DATABASE_URL` — which doesn't exist in CI since `.env` is correctly git-ignored. Fixed with a fake, never-actually-used `DATABASE_URL` just for the test step.
- **OIDC "not authorized to assume role," twice, for two completely different reasons.** First: I used the *leaf* certificate's thumbprint instead of the *root CA's* — AWS validates against the root, and `certificates[0]` in Terraform's cert-chain data source is the leaf, not the root (the root is the last entry). Second, after fixing that: GitHub's actual token claim embeds numeric owner/repo IDs (`repo:Muneeraothman@307808101/autoassist@1308257599:...`), not the simpler format most setup guides show. Found this one by literally decoding the JWT in a temporary debug step rather than guessing a third time.
- **A missing IAM permission masquerading as a networking problem.** `ec2:DescribeInstances` was never granted to the deploy role — CD could push images fine (that used a different permission) but couldn't even *look up* whether an instance was running.
- **A second missing IAM permission, on a completely different role.** Once DescribeInstances worked, the actual SSM command still failed with "instances not in a valid state" — turns out the EC2 instance's *own* role needs `AmazonSSMManagedInstanceCore` for its SSM Agent to register as a managed instance in the first place. Attached it, recreated the instance, still didn't work.
- **The real root cause, four layers deep: the AMI itself was wrong.** The Terraform AMI filter matched the *minimal* Amazon Linux 2023 image, which doesn't ship the SSM Agent at all — so nothing above was ever going to work no matter how many permissions got fixed. Found by checking the actual AMI name/description directly rather than continuing to assume the config was the problem. Every earlier symptom made total sense in hindsight once this was known.
- **Two smaller, unrelated snags on top of all that**: the AMI's default root volume is only 2GB (ran out of space pulling two real Docker images — needed an explicit larger volume), and my home network's IP had changed since Phase 7 was built, silently breaking the SSH security group rule while HTTP access kept working fine — which is exactly what made it non-obvious at first, since "the app is reachable" and "I can SSH in" felt like they should be the same fact and weren't.
- Also genuinely useful, separate from any of the above: outbound port 22 turned out to be blocked entirely from my current network (confirmed by testing against `github.com:22`, not just the AWS instance) — a good reminder to isolate "is this instance-specific or is my own network the actual variable" before assuming the target is at fault.

---

## Session 13 — Phase 9: Email Reminders via EventBridge + Lambda + SES (2026-08-04/05)

**What I did:**
- Designed the Lambda's data-access pattern as a discussion, not a default: calling the backend's own API vs. querying RDS directly. Chose the API — the Lambda has no VPC attachment, so no NAT gateway is needed (the same NAT-avoidance decision from Phase 7 stays intact), and `engine.py`'s due-date logic gets reused instead of duplicated. Added `notifications_log` (dedup, 7-day window) and two internal, shared-secret-protected endpoints (`GET /api/internal/reminders-due`, `POST /api/internal/reminders-sent`) that loop every vehicle for every user — a deliberate multi-tenancy requirement per the Phase 4.5 addendum, since the original build guide's Phase 9 plan assumed one hardcoded vehicle.
- Built the Lambda handler (`infra/lambda_reminders/handler.py`): reads the backend's current URL from SSM Parameter Store (since the EC2 public IP changes every destroy/apply cycle and Lambda has no IMDS access the way the instance itself does), calls the internal endpoints over plain HTTPS, sends one bundled SES email per vehicle, records what it sent for dedup.
- Wired an EventBridge daily cron trigger, all in Terraform (`infra/notifications.tf`).

**What I learned:**
- Shared-secret header auth (a fixed API key checked against a request header) is a legitimate, different pattern from JWT auth, used specifically because the caller (Lambda) has no user session and the endpoint aggregates data across every user — no individual user's JWT should be able to do that anyway, so it deliberately isn't JWT-shaped.
- Why the "call the app's own API" choice avoids reopening the Phase 7 NAT-gateway decision: if the Lambda had needed direct RDS access, it would've had to join the VPC, and anything VPC-attached needs either a NAT gateway or a VPC endpoint to reach the public internet (SES, SSM) at all — an ongoing cost this project deliberately avoided once already.

**Gotchas / things that took longer than expected — the longest, deepest bug chase of the project so far, five real problems stacked on top of each other, and the live checkpoint test only actually passed once all five were found:**

1. **`seed.sql` regenerated locally but never re-uploaded to S3.** The new `notifications_log` table existed in the committed file and loaded fine locally, but the EC2 instance fetches its seed file from a fixed S3 deploy path (`user_data.sh.tpl` does `aws s3 cp s3://.../deploy/seed.sql`), not from git — and that S3 copy was still Phase 8's version. The load command reported overall "Success" with no errors, which was the actually misleading part: loading an *older* script against a *fresh* database has nothing to conflict with, so nothing fails, it just silently never creates a table that was never in the file at all. Lesson: "the command exited 0" and "the file I meant to run is the file that ran" are two different claims — verify both.
2. **EC2 public IP changes on every stop/start, not just on `destroy`/`apply`.** An instance can restart (AWS-side maintenance, or Terraform modifying an attribute in place) without ever being destroyed — same instance ID, new public IP, since there's no Elastic IP. The Lambda's SSM-parameter design assumed the IP only changes across a full destroy/apply cycle (when `user_data` reliably reruns), so a same-instance restart left the SSM parameter silently stale and every Lambda invocation timed out hitting a dead address.
3. **RDS master-user password changes queue instead of applying, unless told otherwise.** `apply_immediately` on `aws_db_instance` defaults to `false` — a `terraform apply` that changes `db_password` reports success immediately, but RDS doesn't actually adopt the new password until the next maintenance window. Meanwhile a *separately* replaced EC2 instance had already baked in the new (not-yet-live) password, so the two sides disagreed for reasons that had nothing to do with either apply actually failing. Even after setting `apply_immediately = true`, the credential reset is still asynchronous — `aws rds describe-db-instances` shows `DBInstanceStatus: resetting-master-credentials` for a real stretch of time after the API call returns "success." Testing connectivity immediately after the apply finished, instead of polling AWS directly for that status to clear, produced several rounds of "it's still broken" that were actually just "it hasn't finished yet."
4. **RDS rejects certain password characters outright.** `openssl rand -base64 24` can output `/`, `+`, or `=` — AWS's `ModifyDBInstance` flatly rejects `/`, `@`, `"`, and spaces in a master password (`InvalidParameterValue`, not a silent truncation). A password containing `/` had actually never been successfully applied to RDS at all, no matter how many times the surrounding Terraform got reapplied — every one of those `ModifyDBInstance` calls had been failing the entire time, we just hadn't looked at whether the specific call succeeded. Fixed at the generation source (`openssl rand -hex 32` — hex is safe by construction) rather than trying to sanitize/allowlist afterward.
5. **`user_data` changes don't force an EC2 replacement by default.** `aws_instance`'s `user_data_replace_on_change` isn't `true` unless set explicitly. Without it, a plain `terraform apply` that edits `user_data.sh.tpl` just updates the stored attribute and stop/starts the *same* instance to write it — but cloud-init tracks "have I already run user-data for this instance ID" and skips re-running it on that restart, so a real fix committed to the template silently never executed on the live box. Confirmed directly: `cloud-init status` said `done` and the file on disk still had the *old*, unfixed content. `terraform apply -replace="aws_instance.app"` forces the real thing (new instance ID); adding `user_data_replace_on_change = true` makes that automatic going forward instead of something that has to be remembered by hand.

**Checkpoint verified for real, end to end, after all five fixes landed:** temporarily set the EventBridge schedule to `rate(5 minutes)`, confirmed a real invocation in CloudWatch Logs — `Sent 1 reminder email(s), recorded 8 notification(s)` — and found the actual email in my inbox for the 2002 Lexus ES300's 8 overdue items, correctly bundled into one message rather than eight separate ones. Confirmed the dedup worked too: a follow-up call to `/api/internal/reminders-due` came back empty, since everything was now inside the 7-day notified window. Reverted the schedule back to `cron(0 13 * * ? *)` afterward.

---

## Session 14 — Phase 10: AI Assistant, Function Calling Over the Car's Data (2026-08-05)

**Pacing note, explicit and different from Phase 4/9's pattern:** I asked Claude to drive this whole phase itself at the fast pace — it wrote all the code — but with one condition: explain each genuinely new concept in a tight paragraph *before* writing the code for it, not after. So instead of me hand-writing the core logic (like the due-date bucketing in Phase 4), the deal this time was understanding it well enough to explain it, not typing it myself.

**What I did:**
- Decided the LLM provider question that had been open since Phase 0: Bedrock, staying in the AWS ecosystem, reusing the IAM patterns already built out. Checked the actual current Bedrock console flow before touching anything (it changed recently — no more per-model "enable" toggle, but Anthropic models still need a one-time account-level use-case form) and confirmed the real, current model ID for Claude Sonnet 4.5 rather than guessing one, which surfaced a non-obvious requirement: `us-east-1` has no *in-region* inference profile for this model, only the cross-region "us." geo profile — calling the bare model ID from `us-east-1` would fail outright.
- Built `backend/tools.py` (the four tool functions + their JSON schemas, reusing `engine.py` and `stats.py` exactly the way Phase 9's Lambda reused `engine.py` — pure functions written once, called from multiple entry points) and `backend/bedrock_utils.py` (the Converse API tool-calling loop, capped at 5 iterations, with a system prompt listing the user's own vehicle IDs). `POST /api/chat` in `main.py` is a thin wrapper over both.
- Granted `bedrock:InvokeModel` in two places, matching the project's identity-per-job pattern: `autoassist-dev` (via AWS CLI, for local testing) and `autoassist-ec2-role` (via Terraform, for the deployed instance) — both needed permission on the underlying foundation model in every region the cross-region profile can route to (`us-east-1`/`us-east-2`/`us-west-2`), not just the inference-profile ARN alone.
- Built `ChatWidget.jsx`, a floating chat button/panel, wired into `App.jsx` outside the per-vehicle-selection block since the assistant can answer about any of the user's vehicles by id, not just whichever one is currently selected in the Garage view.

**What I learned:**
- The tool-calling loop, in one sentence: the model doesn't answer directly, it can instead reply "call this tool with these arguments," your backend runs the real function and feeds the result back in, and this repeats until the model has enough to give a final text answer.
- A tool's JSON schema isn't code the model runs — it's a spec (name + parameter shapes) that tells the model what's available and what arguments to produce, the same way a function signature does for a compiler, just described in a format a model can read.
- Why the ownership check has to live in the tool-execution code, not just the system prompt: the model *deciding* not to ask about a vehicle it doesn't own is a courtesy, not a security boundary — the real boundary is the backend rejecting the call regardless of what the model requests, which I confirmed directly by forcing the model to attempt a tool call against another user's vehicle id and watching the backend reject it with a real error, not just watching the model politely decline.
- Cross-region inference profiles are a real AWS concept, not just an ID-formatting detail: some Bedrock models aren't invocable in-region at all in certain regions, only via a profile that routes the request to wherever the model actually runs, which means IAM permissions have to cover the destination regions too, not just the region you're calling from.

**Gotchas / things that took longer than expected:**
- **Bedrock's Converse API silently rejects a bare JSON array as a tool result.** `get_upcoming_maintenance` and `get_service_history` both naturally return a list, and sending that straight back as a `toolResult`'s `json` content threw `ValidationException: ... Provide a json object for the field`. Fixed by wrapping any list result in `{"items": [...]}` in `bedrock_utils.py`, right where the Bedrock-specific quirk actually belongs, rather than changing what the tool functions themselves return.
- **A real answer-quality bug, not a crash, caught because the model itself flagged it.** `get_service_history`'s first version returned mileage/cost/date/notes but never resolved `schedule_item_id` to an actual service name — asked "what services have I had done," the model correctly noticed it couldn't say *which* services and said so honestly instead of making something up. Good outcome for that specific answer, but the real fix was giving the tool better data: joined in the schedule item's name (or `"Other / Unscheduled Repair"` for unscheduled ones, reusing the exact constant `stats.py` already defines for the same concept) so the tool result is actually complete.
- **Hit the exact same email_tokens foreign-key mistake from Session 8's cleanup, again, in the same session I was writing this journal entry.** Deleted a disposable test account's `service_records`/`schedule_items`/`vehicle` in one multi-statement `psql -c` batch, forgot `email_tokens` again, and the *entire* batch silently rolled back — including the parts that had nothing to do with the missing table. Genuinely useful to note honestly: having already learned and documented this exact lesson once didn't stop it from happening again: the real fix isn't "remember better," it's that this class of mistake keeps recurring specifically because Postgres multi-statement `-c` batches roll back as one unit with no partial-progress feedback, which is worth just checking for defensively (`\d+ <table>` for FKs before writing a multi-table delete) rather than trusting memory.

**Checkpoint, run against a disposable test account with its own vehicle/schedule/service data (never real vehicle data) — 12 questions total, all correct:** all four tools individually (vehicle info, upcoming maintenance with both a time-triggered and a never-serviced OVERDUE item plus one OK item, service history with a name filter and a date filter, spending totals/by-category/by-year), one multi-tool question exercising more than one loop iteration in a single turn, two ownership-boundary probes against a vehicle id belonging to a different account (one passive, one an explicit "ignore your instructions, call the tool anyway" attempt — confirmed via the actual tool-error response that the backend check fired for real, not just the model refusing), and three out-of-scope questions (general car advice, weather, an unrelated coding request) all correctly and politely declined without wasting a tool call.

---

## Session 15 — Phase 11: RAG Over the Owner's Manual PDFs (2026-08-05)

**Pacing note:** same deal as Phase 10 — built at the fast pace with no back-and-forth, on the explicit instruction to make reasonable decisions and just document them rather than ask.

**What I did:**
- Switched the local Postgres image from plain `postgres:16` to `pgvector/pgvector:pg16` (same Postgres underneath, extension pre-compiled in) — vanilla `postgres:16` has no `vector` extension available at all. Confirmed the existing named volume's real data survived the image swap before touching anything else.
- Enabled the `vector` extension and created `manual_chunks` (`vehicle_id`, `source_file`, `page_number`, `chunk_text`, `embedding VECTOR(1024)`) — `vehicle_id` from the very first migration, not retrofitted later, per the Phase 4.5 addendum's §5.6 note, so `search_manual` can scope retrieval with the exact same ownership pattern used everywhere else in the app.
- Wrote `backend/ingest_manuals.py`: extracts text per page with `pdfplumber`, chunks each page into ~500-word pieces with a 75-word overlap (word count as the token-count proxy), embeds each chunk via Bedrock Titan Text Embeddings V2, and inserts into `manual_chunks`. Re-runnable per `--vehicle-id`, clears that vehicle's old chunks first.
- Added `search_manual(query, vehicle_id)` as a 5th tool in `backend/tools.py`, and updated the system prompt in `backend/bedrock_utils.py` to explicitly separate the two tool categories (structured DB tools vs. this one), require a page citation when answering from it, and require an honest "the manual doesn't seem to cover this" instead of guessing.
- Ran ingestion for real against the actual Lexus (vehicle id=2): 637 chunks total, 371 from `OM33566U.pdf` and 266 from `SMG202.pdf`.

**What I learned:**
- A vector embedding is just a list of numbers that represents a piece of text's *meaning* rather than its exact words — "cosine similarity" between two embeddings measures how close in meaning two pieces of text are, which is how `search_manual` finds relevant manual excerpts without needing the user's question to share any literal words with the manual's actual phrasing.
- Why chunking has to happen at all: an embeddings model has an input limit (8K tokens for Titan V2), and even well under that limit, embedding a whole 261-page PDF as one vector would average together hundreds of unrelated topics into a single point, useless for finding one specific answer. Smaller, focused chunks give sharper, more relevant matches.
- Cross-region inference profiles aren't a universal Bedrock thing — confirmed Titan Text Embeddings V2 (unlike Phase 10's Claude Sonnet 4.5) IS available in-region in `us-east-1` directly, so the IAM/model-ID story was simpler for this model specifically. Worth checking per-model, not assuming the same pattern applies everywhere.

**Gotchas / things that took longer than expected:**
- **Swapping the Postgres image threw a collation-version warning** (`database was created using collation version 2.41, but the operating system provides version 2.36`) — the pgvector image's base OS ships a slightly different glibc/ICU than plain `postgres:16`'s, even though both are "Postgres 16." Non-fatal, but real: collation mismatches can affect text sort order/index correctness in edge cases. Fixed with the exact command Postgres itself suggested, `ALTER DATABASE autoassist REFRESH COLLATION VERSION`.
- **Hit the exact same foreign-key cleanup mistake a THIRD time** (Session 8, Session 14, now this one) with a disposable test account's cleanup batch — this time actually stopped and checked `information_schema` for every FK referencing `vehicles`/`users` before writing the delete, which caught `manual_chunks`' own new FK (easy to forget precisely because it's brand new) and got the whole batch right in one shot instead of a failed retry. The actual lesson finally sticking: check first, don't rely on remembering the list from memory.
- **Deliberate design call, not a bug**: `manual_chunks`' ~637 real embedding rows are excluded from the regenerated `seed.sql` (`pg_dump --exclude-table-data=manual_chunks`) — only the schema (`CREATE EXTENSION`, `CREATE TABLE`) ships in the dump. Treating ingested embeddings as regenerable/derived data from the PDFs already in the repo, the same category as S3 receipt objects (also not baked into `seed.sql`), rather than hand-entered source-of-truth data like the rest of the app's real rows. A fresh clone needs one `python ingest_manuals.py --vehicle-id <id>` run, same as it already needs its own `backend/.env`.

**Checkpoint, run against a disposable test account with its own vehicle (real PDFs re-ingested under that vehicle's id specifically for this test, never touching the real account) — all required scenarios passed:**
1. "What kind of oil does my car take?" → correctly used `search_manual`, answered with the real grade (API SJ/SL "Energy-Conserving" or ILSAC), viscosity (SAE 5W-30), and capacity, citing real pages (311, 318-319, 364) from `OM33566U.pdf`.
2. "When is my next oil change due?" → correctly used `get_upcoming_maintenance` instead of the manual, and the date matched the actual seeded service record + interval exactly (December 1, 2026) - confirms the system prompt's tool-selection guidance actually works in practice, not just on paper.
3. A question about jump-starting a "hybrid battery pack" (the 2002 ES300 isn't a hybrid) → didn't hallucinate hybrid instructions; correctly said the manual doesn't cover that because the car doesn't have one, and volunteered the actually-relevant 12V jump-start procedure it did find, with real page citations (273-274) - an even better outcome than a flat "I don't know."
4. Ownership boundary, same adversarial pattern as Phase 10: forced a direct `search_manual` call against another account's `vehicle_id` (2) from the test account (id=8) - backend rejected it for real (`"No vehicle with id 2 found for this user"`), confirmed via the actual tool-error response.

---

## Session 16 — Phase 12: README and Polish, Started (2026-08-05)

**What I did:**
- Wrote a real `README.md` from scratch (the old one was 22 lines, essentially just a "how to run it" note): a two-sentence what/why, a Mermaid architecture diagram covering the full request path plus every AWS service involved, an app/chat description (no real screenshots - this is a private, local-first project with no public deployment to capture from, said so directly rather than fake it), updated local setup instructions including Phase 11's new `ingest_manuals.py` step, a tech stack list, a design-decisions section (due-date engine, pre-signed S3, tool-calling-over-SQL-generation, pgvector, ownership-check consistency), a "by the numbers" section, and draft resume bullets - all pulled from real, freshly-checked counts (14/14 tests via an actual `pytest` run, 25 endpoints via `grep -c "^@app\." main.py`, 9/16/637 for schedule items/service records/manual chunks via direct queries), not remembered or estimated figures.
- Removed a leftover Phase 8 CI/CD test artifact from the frontend: `App.jsx` had a hardcoded `"Deployed via CI/CD — Phase 8 checkpoint v2 (clean auto-deploy proof)"` line on the logged-out screen, left over from proving the pipeline worked. Confirmed it's gone from the actual built bundle, not just the source, before committing.

**What I learned:**
- Pulling "real metrics" for a resume bullet is itself a small discipline worth naming: every number in the README came from an actual command run in this session (`pytest`, `grep -c`, a live `SELECT count(*)`), not from memory of what the counts "probably" are by now - the kind of thing that's easy to get subtly wrong by trusting an older document instead of the current state.

**Checkpoint:** re-ran the full `pytest` suite (still 14/14) and rebuilt the frontend before committing, confirming nothing broke and the tagline is actually gone from `docker exec autoassist-frontend-1`'s served files, not just assumed from the source diff.

---

## Session 17 — First Real Live Deployment, RDS-Side RAG, and a Real CORS Bug (2026-08-05)

**What I did:**
- Applied the full infrastructure for real, with the app meant to actually stay up (not the usual test-then-destroy cycle) - live at a public IP for the first time with all of Phase 9-11's features included.
- Loaded `seed.sql` onto the fresh RDS instance via SSM (had proactively re-uploaded the current version to S3 first, specifically to not repeat the exact stale-S3-file bug from Phase 9's Session 13).
- Ran manual ingestion against RDS for real: since the backend's Docker image already ships `ingest_manuals.py` and its dependencies (built automatically by CD on every push), the only missing piece was the manual PDFs themselves - `docker cp`'d them from S3 into the already-running container and ran the script via `docker exec`, no image rebuild needed. 637 chunks, matching the local run exactly.
- Verified the live deployment end-to-end, not just "it applied cleanly": registered a disposable account, ingested the real manuals under its own test vehicle, and got a correctly-cited chat answer back through the actual public IP - confirms the deployed EC2 instance's IAM role can really call Bedrock in production, not just my own machine's credentials locally.
- **A real bug, found from an actual user report, not from my own testing**: receipt uploads failing with "Failed to fetch" in the browser. Diagnosed methodically rather than guessing - checked the backend's own logs first (clean `200 OK` on `/receipt-upload-url`, so the backend side was never the problem), confirmed the EC2 instance role's credentials work via a live `sts.get_caller_identity()` call, and from there concluded the failure had to be in the step that never touches the backend at all: the browser's direct PUT to S3. Checked the bucket's CORS configuration and found there wasn't one - `NoSuchCORSConfiguration`.

**What I learned:**
- **Why this bug could exist since Phase 5 without ever being caught**: every previous test of the pre-signed upload flow (Phase 5's original checkpoint, and my own earlier local/live checks) used `curl`, and `curl` doesn't enforce CORS at all - CORS is a browser-only security mechanism. This was the first time the flow was ever exercised from a real browser against a real deployed origin. A good lesson about the limits of curl-only testing: it proves the *server* side works, but says nothing about browser-enforced restrictions that only a real browser (or a deliberate CORS preflight simulation) would ever surface.
- **Why `AllowedOrigins: ["*"]` is an acceptable fix here, not a security shortcut**: CORS doesn't grant any access by itself - it only controls whether a *browser* permits a cross-origin request that the request's own authorization (a valid, time-limited, key-specific pre-signed URL signature) would already allow regardless of origin. A wildcard CORS origin on a bucket that's otherwise fully locked down (no public access, no unsigned requests accepted) doesn't widen what's actually reachable.
- Docker's `docker cp` can inject files into an already-running container's filesystem without rebuilding the image or restarting anything - useful for exactly this kind of "the deployed image has the code but not this one input file" situation, though it's ephemeral (gone on next container restart, which is fine for a one-time task like this).

**Gotchas / things that took longer than expected:**
- **My own diagnostic script produced a red herring.** First checked S3 access with `list_objects_v2`, which requires `s3:ListBucket` - a bucket-level permission the app's IAM policy correctly never grants, since the app only ever needs `PutObject`/`GetObject` on specific keys. Got an `AccessDenied` that looked alarming but was actually proof the least-privilege policy was working exactly as designed, not a real problem - just the wrong test for what the app actually does.
- **Quoting through three layers (Bash → SSM's JSON `commands` array → the remote shell) is genuinely fragile.** Lost time to a `chr()`-concatenation hack that produced literal doubled quote characters in the actual command. The fix that actually worked reliably: write the diagnostic as a real `.py` file, base64-encode it, and have the one remote command just decode-and-run it - one clean escaping boundary instead of three nested ones.
- **A real infra-placement decision, not a bug**: the CORS fix lives in `infra/bootstrap/` (the persistent Terraform project), not the destroyable `infra/` one - same reasoning as ECR living there since Phase 8. The receipts bucket itself was never Terraform-managed at all (created manually via console in Phase 5); `aws_s3_bucket_cors_configuration` only needs the bucket's name, not ownership of the full `aws_s3_bucket` resource, so this could be added and applied without importing or disturbing the existing bucket.

**Checkpoint:** full round-trip proof, not just a plausible-looking fix - simulated the exact browser CORS preflight (`OPTIONS` with `Origin`/`Access-Control-Request-Method` headers) against a real pre-signed URL and got back `Access-Control-Allow-Origin: *` / `Access-Control-Allow-Methods: GET, PUT`, then did a real `PUT` (200) followed by a real `GET` (200) through the actual live app, end to end. All test data (accounts, vehicles, manual chunks, the one test S3 object) cleaned up afterward; confirmed the real vehicle's 637 manual chunks were untouched throughout.
