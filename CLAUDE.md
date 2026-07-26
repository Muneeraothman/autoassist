# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

AutoAssist is a personal vehicle-maintenance tracker, currently modeled on a 2002 Lexus ES300 (owner's manual PDFs `manuals/OM33566U.pdf` and `manuals/SMG202.pdf`). It stores vehicle info, a maintenance schedule, and service history, with a frontend, deployment, reminders, and an AI assistant planned for later phases. The project is in early backend-only stages — no frontend exists yet.

The project previously tracked a 2013 Honda Accord; `manuals/2A1313OM.pdf` is that car's manual, left over from before the switch and no longer the source of truth for schedule data. The Lexus uses fixed mileage/time maintenance intervals (a static schedule table in the manual), unlike Honda's adaptive Maintenance Minder system (which calculates a live oil-life % and surfaces dashboard codes like "A1"/"B12" instead of a fixed table) — don't carry over Maintenance Minder-style code/interval assumptions when working on schedule data or logic.

**`AUTOASSIST_BUILD_GUIDE.md` is the authoritative roadmap.** It defines what each phase covers, the build order (do not reorder), the default stack, and per-phase checkpoints — read it before assuming what "the next phase" means, rather than guessing. Its own "Instructions for Claude" section overlaps with the learning workflow below (guided build, one step at a time, explain the why, let the builder write the parts that matter for interviews); treat the two as compatible, and defer to the more specific one when they'd otherwise conflict.

## Learning-project workflow — read this before doing anything else

The user (repo owner) is new to software development and is building this project specifically to learn, not just to end up with working code. `LEARNING_PROCESS.md` is a standing agreement for how work in this repo should proceed:

1. **Before introducing new material** — give a plain-language explanation first. Assume no prior jargon knowledge; define terms as they come up rather than using them casually. Use an analogy where one helps a concept click. Any new term or analogy used gets added to `GLOSSARY.md`.
2. **While building** — the user does the actual typing/running of commands themselves, not copy-paste from a generated block. Explain each command piece by piece (what it does, what each flag means) *before* it's run, not after.
3. **End of every phase — mandatory review, no exceptions:**
   - Quiz on everything from that phase, **one question at a time**, multiple choice.
   - **Shuffle which option is correct** across questions — don't default to always putting the right answer in the same position (e.g. always option 1).
   - Anything answered wrong, or "not sure," gets re-explained immediately and fully before moving to the next question — don't just reveal the right answer and continue.
   - **Last question is open-ended, not multiple choice**: explain one concept back unprompted, in their own words. This is the real test, closer to what an interviewer would ask.
4. **After the review** — update `GLOSSARY.md` (new terms, fully explained) and `JOURNAL.md` (what happened, what was solid vs. needed re-teaching) to reflect it. Log this the same way Session 3/4 in `JOURNAL.md` do: a "solid on first try" list and a "needed re-teaching" list, not just a pass/fail.
5. **Do not start the next phase's work until that phase's review has happened.** Hard checkpoint, not optional — if asked to start a new phase, check whether the prior phase's review and journal/glossary updates are actually done first, and say so if they aren't.

Two more standing rules:
- **Real bugs become interview-story journal entries.** When something breaks and gets debugged (a zombie process, a Docker Desktop hiccup, a mixed-up file edit), log it in `JOURNAL.md` as a story with a cause and a fix, not just "fixed a bug" — per the build guide's philosophy, these are supposed to be repeatable as interview answers later, and reviewed at each phase checkpoint like everything else.
- **Have the builder write the parts that matter for learning/interviews** (schema design, validation rules, due-date engine logic, LLM tool definitions) — walk through the concept, then let them write it, rather than generating it and handing it over. Boilerplate (config files, Dockerfiles, CSS) is fine to generate directly.

In practice: default to explaining concepts and commands rather than silently generating large diffs, and treat `GLOSSARY.md` / `JOURNAL.md` as living docs updated as part of the work, not afterthoughts. If the user pastes a secret (API key, token, password) into chat, flag it and tell them to revoke/rotate it immediately — this has happened before in this project (see `JOURNAL.md`).

## Architecture

Single FastAPI app in `backend/`:

- `backend/main.py` — all API routes. Currently `GET /`, `GET /api/vehicle`, `GET /api/schedule`, `GET /api/services`. Each route opens a DB session via the `get_db` dependency and hand-serializes SQLAlchemy rows into dicts (no Pydantic response models yet).
- `backend/models.py` — SQLAlchemy ORM models: `Vehicle` (1 row per car), `ScheduleItem` (maintenance schedule entries, FK to `vehicles`), `ServiceRecord` (actual service history, FK to `vehicles` and optionally `schedule_items`).
- `backend/database.py` — engine/session setup. Reads `DATABASE_URL` from `.env` via `python-dotenv`; `get_db()` is the FastAPI dependency that yields a session and closes it after the request.
- `seed.sql` — a full `pg_dump` of the Postgres schema plus seed data (real Lexus ES300 maintenance intervals). Used to (re)create the local database.

Postgres runs locally via Docker (not committed here — see `GLOSSARY.md` for the Docker/Postgres setup story). `backend/.env` (git-ignored) holds `DATABASE_URL`; `backend/.env.example` shows the expected format.

## Common commands

Run from `backend/`, with the venv active:

```bash
cd backend
python3 -m venv venv && source venv/bin/activate   # first time only
pip install -r requirements.txt
uvicorn main:app --reload                            # start the API on http://127.0.0.1:8000
```

Load/reset the local database from the committed dump:

```bash
psql "$DATABASE_URL" -f seed.sql
```

There is no test suite, linter, or frontend build configured yet.
