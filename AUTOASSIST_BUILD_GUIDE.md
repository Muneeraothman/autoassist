# AutoAssist Build Guide - Single-Car Maintenance Tracker with AI Assistant

## Instructions for Claude (read this first)

You are walking a student through building this project step by step. Ground rules:

- **This is a guided build, not a code dump.** Work through ONE phase at a time. Within a phase, work through one step at a time. Wait for the builder to confirm each step works before moving on.
- **Explain the "why" behind decisions**, not just the "what." The builder will be asked to defend this project in internship interviews, so every architectural choice should come with a one-paragraph rationale they can repeat.
- **Have the builder type/write code themselves where learning matters** (schema design, due-date engine logic, tool definitions for the LLM). It's fine to generate boilerplate (config files, Dockerfiles, CSS) for them.
- **At the end of each phase, run the checkpoint** listed in that phase. Do not proceed until it passes.
- **If the builder is stuck for more than 2-3 exchanges on the same error**, give them the fix directly with an explanation, then move on. Don't let debugging kill momentum.
- **Track deviations.** If the builder chooses a different stack option than the default, note it and keep all later phases consistent with that choice.
- At the end of each phase, help the builder write a short commit message and remind them to push to GitHub.

## Project Overview

**What we're building:** A deployed full-stack web app that tracks ONE specific car's maintenance. It stores the car's real factory maintenance schedule (transcribed from the owner's manual), logs services with costs and receipt photos, computes what's due next, sends email reminders, shows a cost dashboard, and includes an AI chat assistant that answers questions about the car's data (via LLM function calling) and about the owner's manual (via RAG).

**Deliberately out of scope:** authentication, multi-user support, multiple vehicles in the UI. The schema stays general (vehicles table with foreign keys) so these are clean v2 additions, but do NOT build them now.

**Resume coverage:** SWE (full-stack app, real business logic), Cloud (AWS deployment), DevOps (Docker, Terraform, CI/CD), AI/ML (function calling + RAG).

**Default stack** (adjust if the builder prefers alternatives, but stay consistent):
- Frontend: React (Vite)
- Backend: Python + FastAPI (alternative: Node + Express - ask the builder which language they're stronger in and pick that)
- Database: PostgreSQL
- Storage: AWS S3 (receipt photos, manual PDF)
- Deployment: Docker → AWS (EC2 for MVP simplicity, ECS as stretch), RDS for Postgres
- IaC: Terraform
- CI/CD: GitHub Actions
- Reminders: EventBridge scheduled rule → Lambda → SES
- AI: Amazon Bedrock (Converse API with tool use) or OpenAI - ask which the builder has access to. RAG via Bedrock Knowledge Base (S3 Vectors to avoid idle charges) or a simple pgvector setup in the existing Postgres instance (cheaper, more impressive to explain - prefer pgvector if the builder is comfortable).

**Build order (do not reorder):**
1. Phase 0: Setup and prerequisites
2. Phase 1: Database schema + seed data (the car's real schedule)
3. Phase 2: Backend API (CRUD for service records)
4. Phase 3: Frontend (log services, view history)
5. Phase 4: Due-date engine + dashboard (the core business logic)
6. Phase 5: Receipt photo uploads (S3)
7. Phase 6: Dockerize + local docker-compose
8. Phase 7: Deploy to AWS with Terraform
9. Phase 8: CI/CD with GitHub Actions
10. Phase 9: Email reminders (Lambda + SES)
11. Phase 10: AI assistant part 1 - function calling over the car's data
12. Phase 11: AI assistant part 2 - RAG over the owner's manual
13. Phase 12: Polish, README, resume bullets

Phases 1-6 = local MVP. Phases 7-9 = cloud/DevOps. Phases 10-11 = AI layer. A working local MVP through Phase 6 is a legitimate milestone - celebrate it.

---

## Phase 0: Setup and Prerequisites

**Goal:** Dev environment ready, repo created, the car's manual in hand.

Steps:
1. Confirm installed: Git, Docker Desktop, Node 18+ (for React), Python 3.11+ (if FastAPI), psql or a DB GUI (TablePlus/DBeaver/pgAdmin).
2. Create a GitHub repo (e.g., `autoassist`) with a README stub and a `.gitignore` for the chosen stack. Initialize locally, first commit.
3. Have the builder download the PDF owner's manual for THEIR specific car (manufacturer websites host these free). Locate the maintenance schedule section and skim it together. Note whether it distinguishes "normal" vs. "severe" driving conditions.
4. Create an AWS account if they don't have one (or confirm access). Set up an IAM user with programmatic access for later phases - do NOT use root credentials. Install and configure AWS CLI (`aws configure`).
5. Decide the two stack questions now: backend language (Python vs. Node) and LLM provider (Bedrock vs. OpenAI). Record the choices at the top of the conversation.

**Checkpoint:** Repo exists on GitHub with first commit; `docker --version`, `aws sts get-caller-identity`, and the backend language runtime all work; manual PDF saved locally.

---

## Phase 1: Database Schema + Seed Data

**Goal:** Postgres running locally (in Docker), schema created, the car's REAL factory maintenance schedule loaded as seed data.

**Teaching moment:** Walk through why the schema stays general even for one car (vehicles table with FKs = v2-ready without a rewrite). This is a talking point for interviews.

Steps:
1. Run Postgres locally via Docker: `docker run --name autoassist-db -e POSTGRES_PASSWORD=devpassword -e POSTGRES_DB=autoassist -p 5432:5432 -d postgres:16`
2. Design the schema WITH the builder (make them propose it first, then refine). Target schema:

```sql
CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INT NOT NULL,
    vin TEXT,
    current_mileage INT NOT NULL,
    mileage_updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    avg_miles_per_day NUMERIC(6,2) DEFAULT 30.0
);

CREATE TABLE schedule_items (
    id SERIAL PRIMARY KEY,
    vehicle_id INT NOT NULL REFERENCES vehicles(id),
    service_name TEXT NOT NULL,            -- e.g., 'Engine oil and filter'
    interval_miles INT,                    -- NULL if time-only
    interval_months INT,                   -- NULL if mileage-only
    severe_interval_miles INT,             -- optional severe-condition override
    notes TEXT
);

CREATE TABLE service_records (
    id SERIAL PRIMARY KEY,
    vehicle_id INT NOT NULL REFERENCES vehicles(id),
    schedule_item_id INT REFERENCES schedule_items(id),  -- NULL for unscheduled repairs
    service_date DATE NOT NULL,
    mileage_at_service INT NOT NULL,
    cost NUMERIC(8,2),
    performed_by TEXT,                     -- 'DIY' or shop name
    notes TEXT,
    receipt_key TEXT                       -- S3 object key, filled in Phase 5
);
```

3. Key design discussions to have: why `schedule_item_id` is nullable on service_records (unscheduled repairs like a flat tire), why intervals allow NULL on either dimension ("X miles OR Y months, whichever first" - some items are time-only like brake fluid), why we store `avg_miles_per_day` (mileage extrapolation in Phase 4).
4. Seed data: the builder opens their manual's maintenance table and transcribes it into an `INSERT` script - one vehicles row (their actual car, actual current mileage) and 10-20 schedule_items rows with the REAL intervals. This takes 20-30 minutes and is the moment the app becomes "for my actual car."
5. Also seed 3-5 historical service_records if the builder knows past services (last oil change etc.) - the due-date engine needs history to be interesting.
6. Save schema + seed as versioned SQL files in a `db/` folder (e.g., `db/001_schema.sql`, `db/002_seed.sql`). Explain that real projects use migration tools (Alembic/Flyway) and this is the manual version of that idea.

**Checkpoint:** `SELECT * FROM schedule_items;` returns the car's real schedule; a join query showing "each schedule item with its most recent service record" works (write this query together - it's the seed of the Phase 4 engine).

---

## Phase 2: Backend API

**Goal:** REST API with CRUD for service records and read endpoints for vehicle + schedule.

Steps:
1. Scaffold the backend (FastAPI + SQLAlchemy/psycopg, or Express + pg). Folder structure: `backend/` with clear separation of routes, db access, and (later) the due-date engine and AI code.
2. Environment config via `.env` (DATABASE_URL etc.) - never hardcode. Add `.env` to `.gitignore` NOW and provide a `.env.example`.
3. Build endpoints in this order, testing each with curl or the FastAPI docs page before the next:
   - `GET /api/vehicle` - the vehicle profile
   - `PATCH /api/vehicle/mileage` - update current mileage (body: `{ "mileage": 87500 }`); also recompute `avg_miles_per_day` from the delta since `mileage_updated_at` (teaching moment: this little calculation powers the reminder accuracy)
   - `GET /api/schedule` - all schedule items
   - `GET /api/services` - service history, newest first, with optional `?schedule_item_id=` filter
   - `POST /api/services` - log a service (validate: mileage_at_service can't exceed a sane bound, cost >= 0, date not in future)
   - `PUT /api/services/{id}` and `DELETE /api/services/{id}`
4. Input validation with Pydantic models (or express-validator/zod). Have the builder write the validation rules - this is interview material ("how do you validate input?").
5. Consistent error responses (404 for missing records, 422 for bad input).

**Checkpoint:** Builder can log a fake oil change via the API, see it in `GET /api/services`, update it, delete it. All endpoints tested manually at least once.

---

## Phase 3: Frontend

**Goal:** React app where the owner can view the car, log services, and browse history.

Steps:
1. Scaffold with Vite (`npm create vite@latest frontend -- --template react`). Set up a proxy to the backend for local dev.
2. Pages/views (keep it simple - one-page app with sections is fine):
   - **Home/Overview:** vehicle card (make/model/year, current mileage with an inline "update mileage" input)
   - **Log Service form:** dropdown of schedule items (plus "Other/Repair"), date, mileage (pre-filled with current), cost, performed by, notes
   - **Service History:** table/list, newest first, filterable by service type
3. State management: plain useState + fetch is fine. No Redux. Explain why (scope-appropriate tooling is itself a good interview answer).
4. Styling: keep it clean but don't sink days here. A component library (e.g., minimal Tailwind or plain CSS) is fine. The demo needs to look presentable, not designer-grade.
5. Empty states and loading states - small touches that read as "finished product."

**Checkpoint:** Full loop works in the browser: update mileage → log a service → see it in history. Data survives refresh (it's in Postgres, not component state).

---

## Phase 4: Due-Date Engine + Dashboard (THE core phase)

**Goal:** The app computes what's due next and shows cost analytics. This is the business logic that makes the project more than CRUD - spend real time here and make the builder write this logic themselves.

**The algorithm (walk through this conceptually before any code):**

For each schedule_item:
1. Find the most recent service_record for that item (if none, treat the vehicle's history start / a "since new" assumption - discuss the edge case).
2. **Mileage trigger:** `due_at_miles = mileage_at_last_service + interval_miles`. Estimated current mileage = `current_mileage + avg_miles_per_day * days_since_mileage_update`. Miles remaining = `due_at_miles - estimated_current_mileage`. Estimated due date from miles = today + `miles_remaining / avg_miles_per_day` days.
3. **Time trigger:** `due_at_date = last_service_date + interval_months`.
4. **Whichever comes first:** the item's effective due date is the EARLIER of the mileage-projected date and the time-based date. (Handle NULLs: some items only have one trigger.)
5. Status buckets: `OVERDUE` (due date passed or miles already exceeded), `DUE_SOON` (within 30 days or 500 miles - make thresholds configurable), `OK`.

Steps:
1. Implement as a pure function/module (e.g., `engine.py` / `engine.js`) that takes vehicle + schedule + records and returns a list of `{schedule_item, due_date, due_miles, status, days_remaining, miles_remaining}`. Pure = easily unit-testable.
2. **Write unit tests for the engine** (pytest or vitest/jest). Minimum cases: item with both triggers where mileage wins; where time wins; time-only item; never-serviced item; overdue item. These tests are the backbone of the CI phase and a strong interview point ("what did you test and why").
3. Expose `GET /api/upcoming` returning the computed list sorted by urgency.
4. Frontend: "Upcoming Maintenance" section on Home - status-colored cards (red/yellow/green) with "due in ~X miles / by DATE."
5. Dashboard endpoints + UI: `GET /api/stats` returning total spend, spend by category, spend per year, cost per mile (total spend / miles driven since first record). Simple charts (recharts) - one bar chart (spend by category) and one line (spend over time) is plenty.

**Checkpoint:** Unit tests pass. With the real seed data, the upcoming list looks CORRECT for the actual car (sanity-check against the manual together). Builder can explain the whichever-comes-first logic out loud without notes - rehearse it once, this is their #1 interview talking point.

---

## Phase 5: Receipt Photo Uploads (S3)

**Goal:** Attach a receipt photo to a service record, stored in S3.

Steps:
1. Create an S3 bucket (console or CLI for now - it moves into Terraform in Phase 7). Block public access ON.
2. Backend: implement **pre-signed URL upload** flow (teaching moment - explain why this beats proxying bytes through the API): `POST /api/services/{id}/receipt-upload-url` returns a pre-signed PUT URL; frontend uploads directly to S3; backend stores the object key on the record. `GET` side: pre-signed GET URLs to display receipts.
3. Frontend: file input on the service form + thumbnail/link in history.
4. Validate content type and cap file size.

**Checkpoint:** Upload a real receipt photo (or any image), refresh, view it from history. Confirm the bucket is not publicly readable.

---

## Phase 6: Dockerize + docker-compose

**Goal:** Whole stack runs with one command locally.

Steps:
1. Write a Dockerfile for the backend (multi-stage if Node; slim base for Python). Explain layer caching and why dependencies install before code copy.
2. Dockerfile for the frontend: build stage → serve static files via nginx (or serve from the backend - either is fine, nginx is the more "real" pattern).
3. `docker-compose.yml`: services for db (with a named volume), backend, frontend. Env vars wired through. Healthcheck on the db, `depends_on` with condition.
4. Document the one-command startup in the README: `docker compose up --build`.

**Checkpoint:** Fresh clone test - `git clone` into a new folder, `docker compose up`, app fully works at localhost. This exact test is what a reviewer/interviewer might do.

**Milestone: local MVP complete.** Everything from here is the cloud/DevOps/AI layer that differentiates the project.

---

## Phase 7: Deploy to AWS with Terraform

**Goal:** App live on the internet, all infrastructure defined in Terraform.

**Architecture (MVP-pragmatic):** one EC2 instance (t3.micro/small) running docker compose, RDS Postgres (db.t3.micro, NOT publicly accessible), the existing S3 bucket, proper security groups. Explain the tradeoff honestly: ECS/Fargate is the more "production" answer and a great v2, but EC2-with-compose keeps Phase 7 tractable. The builder should be able to ARTICULATE the ECS upgrade path in interviews even without building it.

Steps:
1. Terraform project structure: `infra/` with `main.tf`, `variables.tf`, `outputs.tf`. Remote state in an S3 bucket + DynamoDB lock table (create these manually first - the classic chicken-and-egg, worth explaining).
2. Resources, built and applied incrementally in this order (plan/apply after each, don't write everything then apply once):
   a. VPC with 2 public + 2 private subnets across 2 AZs, IGW, route tables (or default VPC to simplify - but the builder's AWS background means custom VPC is achievable and worth more)
   b. Security groups: EC2 SG (80/443 from world, 22 from builder's IP only), RDS SG (5432 from EC2 SG only - explain SG-to-SG references)
   c. RDS Postgres in private subnets, credentials via variables (sensitive), NOT in state-committed tfvars
   d. S3 bucket (import the existing one or recreate)
   e. IAM role + instance profile for EC2 (S3 access, later Bedrock access) - explain roles vs. access keys on instances
   f. EC2 instance with user_data that installs Docker and runs the app (pulling from GitHub or, better, from images - see Phase 8)
3. Run the schema/seed SQL against RDS (via the EC2 host or a bastion approach).
4. Point the app's env at RDS. Verify live.
5. Optional stretch: Elastic IP + a cheap domain + HTTPS via Caddy/nginx + Let's Encrypt. Nice for demos; skip if momentum is flagging.

**Checkpoint:** App reachable at the public IP/domain from a phone. `terraform destroy` + `terraform apply` recreates everything (the true IaC test - actually run this once). RDS is not publicly accessible (verify from outside).

**Cost note:** walk the builder through expected monthly cost (t3.micro EC2 + db.t3.micro RDS ≈ $25-30/mo if not free tier). Set a billing alarm in Terraform too - both prudent and a nice resume detail.

---

## Phase 8: CI/CD with GitHub Actions

**Goal:** Push to main → tests run → deploy happens automatically.

Steps:
1. Workflow 1 - CI on every push/PR: install deps, run the Phase 4 unit tests, lint, build the frontend, build Docker images (fail fast on any step).
2. Push images to a registry: ECR (add to Terraform) or GitHub Container Registry (simpler). 
3. Workflow 2 - CD on merge to main: build + push images, then deploy - simplest robust option is SSH into EC2 via GitHub Actions (SSH key in GitHub Secrets) and run `docker compose pull && docker compose up -d`. Alternative: AWS SSM Run Command (no open SSH needed - more impressive, moderate extra effort; offer the choice).
4. GitHub Secrets for all credentials. Explain why secrets never live in the repo or workflow file.
5. Add a status badge to the README.

**Checkpoint:** Builder changes a visible string on the frontend, pushes to main, and watches it appear on the live site with zero manual steps. Also verify a failing test BLOCKS deployment (break a test on purpose once).

---

## Phase 9: Email Reminders (EventBridge + Lambda + SES)

**Goal:** Automated email when maintenance is due soon.

Steps:
1. SES setup: verify the builder's email identity (sandbox mode is fine - it can send to verified addresses, which is all this needs).
2. Lambda function (same language as backend): queries the DB for upcoming items via the engine logic (either import the engine module into the Lambda package or call the app's `/api/upcoming` endpoint - calling the API is simpler and avoids code duplication; discuss the tradeoff), and sends a formatted email for anything OVERDUE or DUE_SOON that hasn't been notified in the last 7 days.
3. Add a `notifications_log` table (item, sent_at) to prevent daily nagging - small but real design detail.
4. EventBridge scheduled rule: daily at 8am local. All of it in Terraform (Lambda, IAM role, EventBridge rule, permissions).
5. VPC consideration: if the Lambda queries RDS directly it must be in the VPC (needs subnets/SG); if it calls the public API it doesn't. This decision is a genuinely good interview story either way.

**Checkpoint:** Temporarily set the schedule to "every 5 minutes," receive a real email about the real car, set it back to daily.

---

## Phase 10: AI Assistant Part 1 - Function Calling Over the Car's Data

**Goal:** Chat widget in the app that answers questions like "when's my next oil change?" and "how much have I spent on brakes?" via LLM tool use - NOT raw SQL generation.

**Architecture (explain before coding):** Backend endpoint `POST /api/chat` receives `{messages: [...]}`. Backend calls the LLM (Bedrock Converse API or OpenAI) with a system prompt + tool definitions. If the model requests a tool, the BACKEND executes a pre-defined, parameterized function and returns the result to the model; the model composes the final answer. The LLM never writes SQL, never touches the DB. This design is the project's best AI security talking point.

Steps:
1. Define 3-4 tools maximum (more degrades selection accuracy):
   - `get_upcoming_maintenance()` - returns the engine's output
   - `get_service_history(service_name?, since_date?)` - filtered records
   - `get_spending_summary(category?, year?)` - totals/breakdowns
   - `get_vehicle_info()` - profile + current mileage
2. Write the JSON schema for each tool WITH the builder (this is the skill interviewers probe). Descriptions matter: the model picks tools based on them.
3. Implement the tool-call loop in the backend: send → check for tool_use in response → execute → send tool_result back → repeat until the model returns text (cap at ~5 iterations).
4. System prompt: the assistant is scoped to this car; answer only from tool results; if a question can't be answered by available tools, say so instead of guessing. Include today's date (the model needs it for "when is X due" phrasing).
5. Frontend: chat widget (floating panel or dedicated tab), messages state, send full history each request (the API is stateless - explain this).
6. Test with a written list of ~15 questions across all tools plus 3-4 out-of-scope questions ("what's the weather") to verify graceful refusal. Save this list - it's the informal eval set, and "I built a test set of questions to evaluate tool selection" is a strong line.

**Checkpoint:** All 15 eval questions get correct, grounded answers; out-of-scope questions get honest "I can't help with that" responses; the builder can trace one full request → tool call → answer cycle in the logs and explain it.

---

## Phase 11: AI Assistant Part 2 - RAG Over the Owner's Manual

**Goal:** The assistant also answers reference questions ("what oil does my car take?", "what does this dashboard light mean?") from the actual manual PDF.

**Design choice to make together (both are defensible):**
- **Option A - pgvector in the existing RDS Postgres:** extract manual text (pypdf/pdfplumber), chunk (~500-800 tokens with overlap), embed via Bedrock Titan Embeddings or OpenAI embeddings, store in a `manual_chunks` table with a vector column, retrieve via cosine similarity. Cheaper (no new infra), and the builder can explain every step - RECOMMENDED.
- **Option B - Bedrock Knowledge Base with S3 Vectors:** managed, less code, mirrors the builder's mentor's prior project. Fine fallback if Option A stalls.
1. Implement ingestion as a one-time script: parse PDF → chunk → embed → insert. Log chunk counts. Discuss chunking tradeoffs (too small = lost context, too big = diluted retrieval).
2. Add a retrieval tool to the EXISTING tool set: `search_manual(query)` - embeds the query, returns top 4-6 chunks with page numbers. Now the same function-calling loop routes naturally: data questions → DB tools, manual questions → search_manual. No separate "RAG mode" - one agent, five tools. This unified design is elegant and worth naming in interviews.
3. Update the system prompt: cite page numbers when answering from the manual; if retrieval returns nothing relevant, say the manual doesn't cover it.
4. Extend the eval question list with ~8 manual questions (mix of ones the manual clearly answers and ones it doesn't).

**Checkpoint:** "What's the recommended tire pressure?" returns the real number with a page citation. "When's my next oil change?" still uses the DB tool (verify the routing). A question the manual doesn't cover gets an honest no.

---

## Phase 12: Polish, README, Resume Bullets

Steps:
1. **README** (this is what recruiters/engineers actually look at): what/why in 2 sentences, architecture diagram (draw.io or mermaid - include the AI tool-calling flow), screenshots/GIF of the app and chat, local setup (`docker compose up`), deployment summary, tech stack, and a short "design decisions" section (whichever-comes-first engine, pre-signed uploads, tool calling over SQL generation, pgvector choice).
2. Record a 60-90 second demo GIF/video - logging a service, the upcoming list updating, asking the chatbot two questions.
3. Sanity pass: no secrets in repo history, billing alarm on, RDS private, S3 private.
4. Draft 3-4 resume bullets together. Guidance: strong ownership verbs, real metrics where they exist (number of schedule items tracked, test count, eval question accuracy, deploy time). Example shapes (rewrite in the builder's own voice with real numbers):
   - Built and deployed a full-stack vehicle maintenance tracker (React, FastAPI, PostgreSQL, AWS) implementing dual mileage/time-interval scheduling logic with mileage extrapolation, validated by a unit test suite
   - Engineered an AI assistant using LLM function calling over user data with 5 parameterized tools and RAG over the owner's manual via pgvector, designed so the model never generates SQL
   - Automated infrastructure with Terraform (VPC, EC2, RDS, S3, Lambda, EventBridge) and CI/CD via GitHub Actions, enabling zero-touch deployments on merge
   - Implemented automated maintenance reminders via EventBridge-scheduled Lambda and SES with notification deduplication
5. Interview prep: have the builder explain, out loud, (a) the due-date algorithm, (b) the tool-calling security design, (c) one thing they'd change for production (ECS, auth/multi-tenancy, migrations tooling). These three answers cover 80% of likely questions.

---

## Appendix: Common Pitfalls to Watch For

- **CORS errors** when frontend first calls backend - configure CORS middleware early (Phase 2/3 boundary).
- **Timezone bugs** in the due-date engine - store dates as DATE, do arithmetic in one timezone, test around month boundaries.
- **Docker networking confusion** - inside compose, the backend reaches the DB at hostname `db`, not `localhost`.
- **Terraform state drift** - if the builder clicks around the AWS console changing things, plan will show surprises. Rule: after Phase 7, all infra changes go through Terraform.
- **RDS accidentally public** - double-check `publicly_accessible = false`.
- **LLM tool loops** - always cap iterations; log every tool call during development.
- **PDF extraction quality** - some manuals are image-heavy; if text extraction is poor, may need OCR or manual copy-paste of the schedule section for the RAG corpus.
- **Scope creep** - no auth, no multi-user, no mobile app, no VIN-lookup-for-any-car. Single car, finished, deployed. Write "v2 ideas" in the README instead of building them.
