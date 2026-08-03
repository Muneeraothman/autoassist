# AutoAssist Glossary

Plain-English explanations of every term as I encounter it. No jargon assumed.

---

## Terminal / Command Line

**Terminal** — An app on your Mac where you type text commands instead of clicking buttons. It's how developers control their computer directly.

**Command** — A line of text you type into Terminal and press Enter to run. Example: `git status`.

**Prompt** — The line in Terminal waiting for you to type something (usually ends in `$` or shows your folder name).

**Flag** — Extra options added to a command, usually starting with `-` or `--`. Example: in `docker run -d postgres`, `-d` is a flag meaning "detached" (run in the background).

**Path** — The location of a file or folder on your computer, like an address. `~/autoassist` means "the autoassist folder inside my home folder." `~` is shorthand for your home folder.

**cd** — "Change directory." Moves you into a different folder in Terminal. Example: `cd ~/autoassist`.

**ls** — Lists the files and folders in your current location.

**mkdir** — "Make directory." Creates a new folder. Example: `mkdir manuals`.

---

## Package Managers

**Homebrew (brew)** — A tool that installs other developer tools for you on a Mac, so you don't have to hunt down installers on random websites. Think of it like an App Store, but for command-line tools. Normally, installing an app means visiting a website, downloading an installer, clicking through a wizard, dragging to Applications. Homebrew replaces all of that with one command — `brew install node` finds, downloads, and correctly installs Node in one step.

**Package** — A piece of software you can install, usually with one command. Example: `brew install node`.

**Cask** — A Homebrew package that installs a full app with a window (like TablePlus), as opposed to a command-line-only tool.

---

## Git & GitHub

**Git** — A tool that tracks every version/change of your code over time, so you can undo mistakes and see history. Runs on your own computer.

**GitHub** — A website that stores a copy of your Git project online, so you can back it up and (later) collaborate with others.

**Repo (repository)** — A project folder that Git is tracking. "The autoassist repo" = the autoassist project folder.

**Commit** — A saved snapshot of your code at a point in time, with a short message describing what changed. Local only until you push it.

**Push** — Sends your local commits up to GitHub, so they're backed up online.

**Clone** — Downloads a copy of a GitHub repo onto your own computer.

**git add** — Tells Git "include this file in my next snapshot (commit)." This is called **staging** — nothing is saved yet, you're just marking what should be included.

**git commit** — Takes everything staged and locks it into a permanent snapshot, saved on your own computer only. GitHub doesn't know about it yet at this point.

**git push** — Sends your saved commits up to GitHub.com. This is the only step of the three that actually talks to the internet, which is why it's the step that asks for login credentials.

**The full real example, from this project:**
1. `git status` showed `manuals/` as "untracked" — Git saw the folder but wasn't paying attention to it yet
2. `git add manuals/` — staged it: "include this in my next save"
3. `git commit -m "Add owner's manual for 2013 Honda Accord"` — saved a permanent snapshot on the laptop only, got back a snapshot ID (`7f7c909`)
4. `git push` — finally sent that snapshot to GitHub.com, which is why it asked for username + token

**Box analogy:** `add` = putting an item in the box. `commit` = sealing the box with a label (saved on your desk, not sent anywhere). `push` = mailing the box to GitHub.

**git status** — Shows what's changed, what's staged, what's not tracked yet. Good habit to run this often when confused.

**.gitignore** — A file listing things Git should never track (like junk files macOS creates automatically, e.g. `.DS_Store`).

**Personal Access Token (PAT)** — A long password-like string GitHub gives you to log in from Terminal, since GitHub no longer accepts your actual account password for this. Treat it exactly like a password — never share it or paste it anywhere public.

---

## Docker

**Docker** — A tool that packages software into sealed, self-contained boxes (containers) that run the same way on any computer. Solves "it works on my machine" problems. Works identically on Mac, Windows, and Linux.

**Analogy that made this click:** Your computer is an apartment. Installing something (like Postgres) *directly* is like moving a giant piece of furniture straight into your living room — it's now part of your actual space, tangled up with everything else, and hard to remove cleanly later. Docker instead gives that software its own separate, sealed storage unit next to your apartment. The software lives entirely inside that unit. Your apartment (your actual computer) never gets touched. Delete the container, and it's like it was never there — nothing else on your machine is affected.

**Why use it instead of installing directly:** direct installs accumulate mess over time — permanent background services, system-level files, version conflicts between different projects that need different versions of the same tool. Docker keeps every project's tools isolated and disposable, so nothing clashes and nothing lingers.

**One-sentence interview answer:** "I ran Postgres in Docker instead of installing it directly, so it's isolated in its own container and doesn't touch my system — I can delete or rebuild it anytime with zero risk to my machine."

**Image** — The blueprint/template for a container (e.g. "postgres:16" is an image — a snapshot of Postgres version 16 ready to run).

**Container** — A running instance of an image. If the image is a recipe, the container is the actual dish being cooked.

**docker run** — Starts a new container from an image.

**docker ps** — Lists containers currently running.

**Detached mode (-d)** — Runs a container in the background, so it doesn't take over your terminal window.

**Port** — A "channel" a program listens on for connections. Postgres defaults to port 5432. `-p 5432:5432` connects a port on your Mac to a port inside the container.

---

## Databases

**Database** — Organized, structured storage for data — like a very powerful spreadsheet system that can be queried, filtered, and connected across tables.

**Postgres (PostgreSQL)** — A specific, popular, free database system. What AutoAssist will use to store vehicles, services, and schedule data.

**Table** — One "sheet" inside a database — e.g. a `vehicles` table, a `schedule_items` table.

**Schema** — The overall design of a database: what tables exist, what columns each has, and how tables relate to each other.

**Column** — A single field/attribute in a table, like `make`, `model`, or `current_mileage`.

**Row** — A single record in a table — e.g. one specific car, or one specific service log entry.

**Foreign key** — A column that points to a row in another table, linking them together. Example: a `schedule_items` row has a `vehicle_id` pointing to which car it belongs to.

**Seed data** — Starter data loaded into a database when it's first set up, so there's something real to work with (in our case: the actual maintenance items from the Accord's manual).

---

## Local Dev Debugging

**Zombie process** — A program (like the `uvicorn` dev server) that's still running in the background even though you closed the terminal window or thought you stopped it. It keeps holding onto whatever it was using (like a network port), so the next time you try to start the same thing, it fails as if it were already running — because it is.

**Port already in use** — An error you get trying to start a server on a port (like 8000) that's already occupied by another running process — usually a zombie process from a previous run. Fixed by finding what's using the port (`lsof -i :8000`) and stopping it (`kill <PID>`), then starting fresh.

**lsof** — "List open files." A command that can show you what process is using a given network port: `lsof -i :8000` lists whatever has port 8000 open.

**kill** — Stops a running process by its process ID (PID). `kill <PID>` asks it to shut down; needed when a zombie process is blocking a port you want to reuse.

**Docker Desktop** — The actual application on your Mac that runs the Docker engine in the background. Installing Docker isn't enough — Docker Desktop has to be open and running before commands like `docker run` or `docker ps` will work. If it's not running, those commands fail with a connection error even though Docker itself is installed correctly.

---

## Backend API (FastAPI, Pydantic, SQLAlchemy)

**Pydantic model** — A Python class (inherits from `BaseModel`) that describes the required shape of incoming data: field names, types, and rules. FastAPI checks every request body against it automatically, before your route function ever runs. If the data doesn't match, the client gets a `422` error with no extra code needed. **Analogy:** a bouncer with a checklist at the door — data has to pass the checklist before it's let in.

**`Field(...)`** — Attaches extra constraints to a Pydantic field beyond its basic type, e.g. `Field(gt=0)` ("greater than 0") or `Field(ge=0)` ("greater than or equal to 0"). Used for static, always-true bounds — a plain type hint alone can't express "must be positive."

**Custom validator (`@field_validator`)** — For rules `Field(...)` can't express because they depend on something computed at request time (like "not in the future," which needs today's actual date). A function decorated with `@field_validator("field_name")` runs after normal type-checking, and can `raise ValueError(...)` to reject the value — Pydantic turns that into a `422` automatically. Must always `return` the value if it passes.

**`HTTPException`** — FastAPI's mechanism for returning an error response from inside a route function: `raise HTTPException(status_code=..., detail="...")`. Stops the function immediately and sends that status code + message back to the client.

**HTTP status codes used in this project** — `200` (success, default), `201` (successfully created something new, set via `status_code=201` on `@app.post`), `204` (success, no content to return — used for `DELETE`), `404` (nothing found at this ID), `422` (the request itself was invalid — bad shape or failed a validation rule).

**PATCH vs. PUT vs. POST vs. DELETE** — the four HTTP verbs this project's API uses: `POST` creates a new resource, `PUT` replaces an existing one entirely (all fields), `PATCH` updates only part of one (this project's `PATCH /api/vehicle/mileage` only ever touches mileage-related fields), `DELETE` removes it. FastAPI has a matching decorator for each (`@app.post`, `@app.put`, etc.).

**Query parameter** — Data passed in the URL after a `?`, like `?schedule_item_id=8`. In FastAPI, any plain function parameter with a default value that *isn't* part of the URL path becomes a query parameter automatically — no special decorator syntax needed, e.g. `def get_services(schedule_item_id: int | None = None, ...)`.

**`db.add()` vs. `db.commit()`** — `db.commit()` alone is enough for an object SQLAlchemy is already tracking (e.g. one fetched via `db.query(...)`, then modified). A brand-new object built with `Model(...)` isn't tracked yet — `db.add(new_object)` is what tells SQLAlchemy "start tracking this," and has to happen before `db.commit()` for it to actually get saved.

**`.desc()`** — Called on a SQLAlchemy column inside `.order_by(...)` to sort descending (newest/highest first) instead of the default ascending order.

---

## Frontend (React, Vite)

**Vite** — A fast build tool/dev server for frontend projects. `npm create vite@latest` scaffolds a new project; `npm run dev` starts a local dev server with hot-reload (edit a file, browser updates without a manual refresh).

**Dev server proxy** — A Vite config setting (`server.proxy` in `vite.config.js`) that forwards requests matching a path (e.g. `/api/*`) from the frontend's dev server to another server (the FastAPI backend on port 8000). Lets frontend code just call `fetch('/api/vehicle')` without hardcoding a backend URL, and sidesteps CORS issues in local dev.

**Component** — A self-contained, reusable piece of UI written as a function that returns JSX (HTML-like syntax inside JavaScript). This project has one per major page section: `VehicleCard`, `LogServiceForm`, `ServiceHistory`, composed together inside `App`.

**Props** — Data passed from a parent component into a child component, e.g. `<VehicleCard vehicle={vehicle} loading={vehicleLoading} onMileageUpdated={fetchVehicle} />`. One-directional: the child reads props but can't change them directly.

**`useState`** — A React "hook" that gives a component memory across re-renders: `const [value, setValue] = useState(initialValue)`. Calling `setValue` updates `value` *and* triggers the component to re-render with the new value.

**`useEffect`** — A React hook for running code in response to a component appearing or specific values changing (e.g. fetching data when a component first loads). The array at the end (`[currentMileage, mileageTouched]`) lists which values, when changed, should re-run the effect.

**Lifting state up** — Keeping shared data (like the `vehicle` object) in a parent component (`App`) instead of duplicating it in multiple children, so every child that needs it gets it via props and always sees the same up-to-date value. Why `vehicle` lives in `App` rather than inside `VehicleCard` alone: `LogServiceForm` also needs `current_mileage` to pre-fill its mileage field.

**Controlled input** — A form input whose displayed value is driven entirely by React state (`value={mileage}` + `onChange={(e) => setMileage(e.target.value)}`), rather than the browser managing its own internal value. Necessary any time you need to read, validate, or reset a field's value from JavaScript.

---

## This Project's Car-Specific Terms

**Maintenance Minder™** — Honda/Acura's built-in system that calculates a live "engine oil life %" based on actual driving conditions, and tells you via a dashboard code (like "A1" or "B12") when service is due. Not a fixed mileage table like some other brands use. This described the project's *original* car (a 2013 Honda Accord) — the project has since switched to a 2002 Lexus ES300, so these terms are historical context, not how the current car's schedule works.

**Maintenance code** — The letter/number Honda uses to label a bundle of services (e.g. Code A = oil change only, Code B = oil change + filter + brake inspection + more, Code 1 = rotate tires). Historical/Honda-specific — see note above.

**Fixed maintenance interval** — The Lexus's (and most other brands') approach to maintenance scheduling: the owner's manual lists a straightforward table of services due at specific mileage/time marks (e.g. "replace every 30,000 miles or 24 months"), instead of Honda's adaptive Maintenance Minder system. Simpler to model in the database — no live oil-life calculation needed, just mileage/date math against a fixed table.

---

## Authentication (Phase 4.5)

**Hashing** — A one-way scramble of data into a fixed-length string. Like blending a strawberry into a smoothie: you can't un-blend the smoothie back into the strawberry, but blending the *same* strawberry the *same* way always produces the *same* smoothie (deterministic). Used for passwords so the raw password is never stored — only its hash.

**Salt** — A random string mixed into a password before hashing, unique per password. Without it, two users with the same password would produce identical hashes, which is itself a leak (an attacker with a table of "common password → hash" could look yours up directly — a "rainbow table" attack). The salt doesn't need to be kept secret; bcrypt stores it right alongside the hash. Its job is uniqueness, not secrecy.

**Work factor (a.k.a. cost / rounds)** — A tunable "how slow should this be on purpose" knob on bcrypt. A fast hash can be computed millions of times per second, which makes brute-forcing a stolen password database practical. bcrypt deliberately takes ~100-300ms per hash instead, controlled by the work factor — invisible to a real user logging in once, but it turns "try a billion password guesses" into a computationally impractical task. As hardware gets faster over the years, the work factor gets bumped up rather than switching hash algorithms entirely.

**bcrypt** — The specific slow, salted hashing algorithm used for passwords in this project (via the `passlib` library). Not to be confused with general-purpose hash functions like SHA-256, which are fast by design and wrong for passwords for exactly that reason.
