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

## This Project's Car-Specific Terms

**Maintenance Minder™** — Honda/Acura's built-in system that calculates a live "engine oil life %" based on actual driving conditions, and tells you via a dashboard code (like "A1" or "B12") when service is due. Not a fixed mileage table like some other brands use. This described the project's *original* car (a 2013 Honda Accord) — the project has since switched to a 2002 Lexus ES300, so these terms are historical context, not how the current car's schedule works.

**Maintenance code** — The letter/number Honda uses to label a bundle of services (e.g. Code A = oil change only, Code B = oil change + filter + brake inspection + more, Code 1 = rotate tires). Historical/Honda-specific — see note above.

**Fixed maintenance interval** — The Lexus's (and most other brands') approach to maintenance scheduling: the owner's manual lists a straightforward table of services due at specific mileage/time marks (e.g. "replace every 30,000 miles or 24 months"), instead of Honda's adaptive Maintenance Minder system. Simpler to model in the database — no live oil-life calculation needed, just mileage/date math against a fixed table.
