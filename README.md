# AutoAssist

A vehicle maintenance tracker — real fixed-interval maintenance schedules, service history with receipt photos, cost tracking, and multi-user accounts.

Full project narrative, architecture, and decisions: see `HANDOFF.md`. Build roadmap: `AUTOASSIST_BUILD_GUIDE_ANNOTATED.md`.

## Running locally

**Prerequisites:** Docker (this project uses [Colima](https://github.com/abiosoft/colima) as the Docker runtime, not Docker Desktop — any Docker-compatible runtime works) and a `backend/.env` file (see `backend/.env.example` for the required variables; `DATABASE_URL` gets overridden automatically for the containerized network, so its value there doesn't matter for `docker compose`).

```bash
docker compose up --build
```

This builds and starts all three services — Postgres (auto-seeded from `seed.sql` on first run), the FastAPI backend, and the React frontend served via nginx — and waits for the database to report healthy before starting the backend.

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

Data persists in a named Docker volume across restarts (`docker compose down` / `docker compose up` again). To wipe and start fresh: `docker compose down -v`.

AWS features (SES email, S3 receipt uploads) require your local `~/.aws/credentials` (via `aws configure`) — the backend container mounts that directory read-only.
