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
