# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

AutoAssist is a personal vehicle-maintenance tracker, currently modeled on a 2002 Lexus ES300 (owner's manual PDFs `manuals/OM33566U.pdf` and `manuals/SMG202.pdf`). It stores vehicle info, a maintenance schedule, and service history, with an AI assistant planned for later. The project is in early backend-only stages — no frontend exists yet.

The project previously tracked a 2013 Honda Accord; `manuals/2A1313OM.pdf` is that car's manual, left over from before the switch and no longer the source of truth for schedule data. The Lexus uses fixed mileage/time maintenance intervals (a static schedule table in the manual), unlike Honda's adaptive Maintenance Minder system (which calculates a live oil-life % and surfaces dashboard codes like "A1"/"B12" instead of a fixed table) — don't carry over Maintenance Minder-style code/interval assumptions when working on schedule data or logic.

## Learning-project workflow — read this before doing anything else

The user (repo owner) is new to software development and is building this project specifically to learn, not just to end up with working code. `LEARNING_PROCESS.md` is a standing agreement for how work in this repo should proceed:

- **Before introducing new material**: give a plain-language explanation first, no assumed knowledge. If a good analogy is used, it should get added to `GLOSSARY.md`.
- **While building**: the user does the actual typing/running of commands. Explain each command piece by piece before it's run — don't just hand over something to paste blindly.
- **End of every phase**: a mandatory review/quiz before moving on — this is a hard checkpoint, not optional. Don't start the next phase of work until this has happened.
- **After a review**: update `GLOSSARY.md` (new terms, fully explained) and `JOURNAL.md` (a running per-session log of what was done and learned) to reflect it.

In practice: when asked to build a new feature or phase, default to explaining concepts and commands rather than silently generating large diffs, and treat `GLOSSARY.md` / `JOURNAL.md` as living docs to keep updated as part of the work, not afterthoughts. If the user pastes a secret (API key, token, password) into chat, flag it and tell them to revoke/rotate it immediately — this has happened before in this project (see `JOURNAL.md`).

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
