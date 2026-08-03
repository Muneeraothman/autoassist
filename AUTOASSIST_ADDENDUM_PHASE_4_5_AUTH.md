# AutoAssist Addendum — Phase 4.5: Multi-User Auth + Multi-Vehicle Support

📌 **WHAT THIS FILE IS.** This is a third project document, meant to be read alongside the existing two:

- `AUTOASSIST_BUILD_GUIDE_ANNOTATED.md` — the original spec (Phases 0–12), with inline deviation notes.
- `HANDOFF.md` — the narrative/state summary of what's actually been built, decided, and is still open.
- This file (`AUTOASSIST_ADDENDUM_PHASE_4_5_AUTH.md`) — a new phase, inserted between Phase 4 and Phase 5, that did not exist in the original guide. It was added by explicit decision, after Phase 4 was already complete and before Phase 5 (receipt uploads) was started. Read this file in full before touching Phase 5 or any later phase — it changes assumptions baked into all of them.

**Status as of this writing: 🔲 NOT STARTED.** Nothing in this file has been built yet. Treat every code snippet below as a plan, not a confirmed implementation, until a future session's handoff notes say otherwise. When this phase is actually built, whoever does it should go back through this file and convert the 🔲 OPEN markers into ✅ DONE or ⚠️ DEVIATION annotations, the same way the original build guide was annotated — this file is written to be edited in place, not replaced.

## 1. Why this phase exists

The original guide explicitly scoped the project to one car, one user, no login — see `AUTOASSIST_BUILD_GUIDE_ANNOTATED.md`'s "Deliberately out of scope" line: "authentication, multi-user support, multiple vehicles in the UI." That was the right call for getting an MVP shipped fast, and Phases 0–4 were correctly built that way.

This decision is now explicitly reversed, on purpose, before Phase 5. The project is being generalized from "tracks Muneera's 2002 Lexus ES300" to "tracks any car, for any user, with real accounts." This was a deliberate scope expansion discussed and decided in a planning session (not a Claude Code session) on August 1, 2026, specifically choosing the "full multi-user with accounts/auth" option over a lighter "multiple cars, still just me" alternative — the reasoning being that real auth is a stronger, more standard "production app" story for interviews than a single-user multi-vehicle picker would be.

Why insert this BEFORE Phase 5, not after it or at the end: Phase 5 (S3 receipt uploads) and Phase 10 (AI tool calling) both produce artifacts that are much more annoying to retrofit with ownership scoping after the fact than to build correctly from day one — S3 object keys and AI tool parameters. Doing auth now means every phase from here forward is built multi-tenant natively, instead of being built single-tenant and then patched. See Section 5 for the specific forward-impact on each later phase.

## 2. Instructions for Claude (read this before writing any code for this phase)

Same overall spirit as the original guide's "Instructions for Claude" section, with adjustments specific to this phase:

- Default to the fast pace (build → test → summarize at checkpoints) for everything in this phase EXCEPT the item flagged below — this matches the pace the project has been running at since mid-Phase-2 (see HANDOFF.md §3.3).
- **Hand-write exception**, same reasoning as the Phase 4 due-date engine: the core auth logic — password hashing call, JWT issuance, and especially the `get_current_user` / ownership-verification dependency — should be written by Muneera personally, with Claude explaining concepts first. Rationale, discussed and agreed before this phase started: this is a real security boundary, not just business logic, and "walk me through how a request gets authenticated" is a near-certain interview question. This is the same treatment Phase 4's bucketing logic got, and the same treatment already flagged (but not yet applied, since Phase 10 hasn't started) for the AI tool-calling loop. See Section 4 for the exact line between "hand-write" and "Claude Code builds it."
- Do not silently decide the open questions in Section 6. Several real product/security decisions (token storage mechanism, session expiry, whether password reset is in scope) are listed as open below. Ask Muneera directly when this phase starts, the same way the LLM-provider decision for Phase 10 was correctly left open rather than defaulted.
- This phase touches already-shipped, tested code (Phases 1–4). Treat this like a refactor with a safety net, not a rewrite: Phase 4's `test_engine.py` and the stats tests must still pass after this phase, since the engine/stats functions are pure functions that don't know about users at all (see Section 5.1) — if changes here break those tests, that's a signal something leaked into the wrong layer.
- Update HANDOFF.md when this phase is done — specifically Section 4 (add a Phase 4.5 entry, following the existing phase-status format), Section 2 (tech stack — add the new auth libraries), and Section 3 (add a new numbered deviation/decision entry, 3.7, documenting what was actually decided for each open question in Section 6 below). Also update CLAUDE.md and LEARNING_PROCESS.md per the existing standing instruction in HANDOFF.md §3.4/§8.

## 3. Schema changes

New table:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Modified table:

```sql
ALTER TABLE vehicles
    ADD COLUMN user_id INT REFERENCES users(id);
-- After backfilling existing data (see below), make it NOT NULL:
ALTER TABLE vehicles
    ALTER COLUMN user_id SET NOT NULL;
```

No other table changes needed. `schedule_items` and `service_records` already reach ownership transitively through `vehicle_id` — this is the direct payoff of the original guide's decision to make `vehicles` a proper FK-linked table "for v2-readiness" even in the single-car MVP (see the original guide's Phase 1 teaching moment). Same is true for the `manual_chunks` table Phase 11 will introduce — it should be given a `vehicle_id` (or `manual_id`, see Phase 11 impact note in Section 5.5) from the start, not retrofitted.

**Backfill plan for existing real data:** Muneera's real Lexus data (vehicle id=2, 9 schedule items, 16 service records — see HANDOFF.md §3.2) already exists in the database and must not be lost or re-entered. Steps, in order:

1. Create the `users` table.
2. Create a real user account for Muneera through the new registration endpoint (once built) — do NOT hand-insert a row with a plaintext or dummy password hash; use the real registration flow so the hashing logic is exercised on real data from day one.
3. `UPDATE vehicles SET user_id = <muneera's new user id> WHERE id = 2;`
4. Only then apply the `NOT NULL` constraint.
5. Regenerate `seed.sql` (per the existing `pg_dump --inserts` process documented in HANDOFF.md §5) so the new `users` table and the `user_id` column are captured for future fresh-machine setups.

## 4. Build steps, in order

Each step is tagged `[DELEGATE]` (Claude Code writes it at the fast pace) or `[HAND-WRITE]` (Muneera writes it personally, Claude explains concepts first, per Section 2).

1. `[DELEGATE]` Add the `users` table and the `vehicles.user_id` column (migration SQL, run manually against the local Postgres container the same way Phase 1's schema was applied).
2. `[DELEGATE]` Add new dependencies to `backend/requirements.txt`: `passlib[bcrypt]` (password hashing) and `python-jose[cryptography]` (JWT signing/verification). These are the standard, widely-used choices for a FastAPI project — explain why during the concept walkthrough (bcrypt is a deliberately slow hash function, resistant to brute-force; JWT is stateless, which fits the API's existing stateless design philosophy already established for the AI chat endpoint in the build guide's Phase 10 section).
3. `[HAND-WRITE]` `POST /api/auth/register` — takes email + password, hashes the password with passlib, inserts a new `users` row, returns a JWT. Muneera writes the actual hashing call and the insert logic herself; Claude explains what bcrypt is doing conceptually (salting, work factor) before she writes it, the same teaching pattern used for the Phase 4 Decimal/float gotcha.
4. `[HAND-WRITE]` `POST /api/auth/login` — takes email + password, looks up the user, verifies the password against the stored hash (`passlib.verify`), issues a JWT if it matches, returns 401 if not. Same hand-write reasoning as step 3.
5. `[HAND-WRITE]` The `get_current_user` FastAPI dependency — decodes and verifies the JWT from the `Authorization` header, looks up the corresponding user, raises 401 if the token is missing/invalid/expired. This is the single most important piece of this whole phase to understand deeply — every protected route depends on this function being correct. Muneera writes this herself with Claude walking through JWT structure (header/payload/signature) conceptually first.
6. `[HAND-WRITE]` A second dependency, `get_owned_vehicle_or_404(db, vehicle_id, current_user)` — extends the existing `get_vehicle_or_404` pattern from Phase 2 (see HANDOFF.md §4, Phase 2 entry) to also check `vehicle.user_id == current_user.id`, raising 404 (not 403 — deliberately don't reveal that a vehicle ID exists but belongs to someone else) if it doesn't match. This is the ownership-check function that every other endpoint in the app will now route through. Hand-write this one specifically because it's the actual security boundary that makes multi-tenancy safe, not just a plumbing detail.
7. `[DELEGATE]` Retrofit all 8 existing Phase 2 endpoints (GET/PATCH `/api/vehicle`, GET `/api/schedule`, GET/POST/PUT/DELETE `/api/services`) to require `Depends(get_current_user)` and to look up the vehicle via `get_owned_vehicle_or_404` instead of assuming a single hardcoded vehicle. Because these endpoints already went through the `get_vehicle_or_404`/`get_service_or_404` refactor in Phase 2, this should be a fairly mechanical find-and-extend pass, not a rewrite of route logic.
8. `[DELEGATE]` New endpoints: `POST /api/vehicles` (add a car — this becomes the new home for what used to be one-time seed-script data entry), `GET /api/vehicles` (list the current user's cars), `DELETE /api/vehicles/{id}`.
9. `[DELEGATE]` Frontend: login/register forms, token storage (mechanism TBD — see Section 6), a "my garage" view listing vehicles, and a vehicle switcher replacing the current hardcoded single-car assumption on Home.
10. `[DELEGATE]` Re-run Phase 4's existing test suites (`test_engine.py`, stats tests) to confirm they still pass untouched — they should, since those functions are pure and vehicle-agnostic (see Section 5.1).

**Checkpoint for this phase:** Register two different test accounts. Confirm each can only see, edit, and delete their own vehicle(s) and service records — explicitly try to access another account's `vehicle_id` via the API directly (not just through the UI) and confirm it 404s rather than leaking data. Confirm a request with no token, an expired token, and a malformed token are all rejected with 401. Confirm Phase 4's existing pytest suite still passes unmodified.

## 5. Impact on other phases

### 5.1 — Phases 1–4 (already built): mostly unaffected, one mechanical retrofit

The Phase 4 due-date engine (`engine.py`) and stats module (`stats.py`) are pure functions that take `vehicle`, `schedule_items`, and `service_records` as plain arguments — they have no idea a `users` table exists, and they don't need to. This was a good design decision made for testability reasons back in Phase 4 (see HANDOFF.md §4) that happens to also pay off here: no changes needed inside `engine.py` or `stats.py` themselves. The only change is one layer up, at the API route level (Section 4, step 7): the route now has to figure out which vehicle's data to hand to the pure function, based on the authenticated user and a `vehicle_id`, instead of assuming there's only one vehicle in the database.

### 5.2 — Phase 5 (receipt uploads, not yet started)

The pre-signed S3 URL flow needs to be scoped from the start. Object keys should be prefixed by ownership, e.g. `users/{user_id}/vehicles/{vehicle_id}/receipts/{service_id}/{filename}`, not a flat `receipts/{filename}` scheme. This prevents one user's pre-signed URL request from being guessable/collidable with another user's objects. The receipt-upload-url and receipt-viewing endpoints both need to run through `get_owned_vehicle_or_404` before issuing any pre-signed URL. Everything else in the original Phase 5 plan (pre-signed PUT for upload, pre-signed GET for viewing, private bucket) is unchanged.

### 5.3 — Phase 7 (Terraform/AWS deploy, not yet started)

No architectural change — RDS still holds one Postgres instance with all users' data, same as any normal multi-tenant app. Worth noting in the eventual README's "design decisions" section (Phase 12) as a deliberate choice: row-level ownership via `user_id`/`vehicle_id` foreign keys, not separate databases or schemas per user.

### 5.4 — Phase 9 (email reminders, not yet started)

The Lambda's daily query needs to run per user now, not once for "the vehicle." It should iterate over all `vehicles` rows (joined to their owning `user.email`) rather than assuming a single hardcoded recipient. The `notifications_log` table (already planned in the original guide to prevent daily nagging) should also gain a `user_id` or be scoped through `vehicle_id`, so dedup logic is correct per user.

### 5.5 — Phase 10 (AI function calling, not yet started)

This is the phase most affected. Every existing tool definition in the original guide's Phase 10 plan (`get_upcoming_maintenance()`, `get_service_history()`, `get_spending_summary()`, `get_vehicle_info()`) implicitly assumed "the one car" and takes no vehicle-identifying parameter. All four need a `vehicle_id` argument now, and — critically — the backend tool-execution code must verify the authenticated user actually owns that `vehicle_id` before running the query, exactly the same ownership check as every REST endpoint. This is a natural, good extension of the guide's own stated security talking point ("the LLM never writes SQL, never touches the DB, the backend executes pre-defined parameterized functions") — now that story extends to "...and the backend also verifies the calling user owns the vehicle_id it's asking about," which is arguably a stronger interview answer than the original single-tenant version. This reinforces, not replaces, the original guide's plan to hand-write the tool definitions and tool-execution loop personally (see HANDOFF.md §3.3 and §4's Phase 10 entry) — if anything, this makes that hand-write decision more important, not less, since the ownership check is now part of the security-critical code path.

### 5.6 — Phase 11 (RAG over the manual, not yet started)

The `manual_chunks` table (not yet created) should be given a `vehicle_id` (or a `manual_id` that itself belongs to a vehicle, if one user's car ever has multiple manual documents) from its very first migration — not retrofitted later. The `search_manual(query, vehicle_id)` tool then filters retrieval to only the chunks belonging to the requesting user's specified vehicle, via the same cosine-similarity search, just with a `WHERE vehicle_id = ...` scope added. This also means the ingestion script (parse PDF → chunk → embed → insert) needs to be re-run per uploaded manual, per vehicle, rather than being a one-time script against a single fixed PDF — which fits naturally with the "upload your manual" onboarding idea discussed for making schedule-item data entry general-purpose too (see Section 7).

### 5.7 — Phase 12 (polish/README/resume bullets, not yet started)

The eventual README's architecture section and resume bullets should describe the finished app as multi-user/multi-vehicle from the start (since that will be true by the time Phase 12 is reached), not describe a single-car app with an auth system bolted on. Worth a "design decisions" paragraph on the ownership-check pattern specifically, since it's used consistently in three different places by the end (REST routes, S3 keys, AI tool execution) — that consistency is itself a good thing to name explicitly in an interview.

## 6. Open decisions — do not default these silently, ask Muneera

- 🔲 **Token storage on the frontend:** httpOnly cookie (more secure against XSS, slightly more setup complexity, needs CSRF consideration) vs. localStorage (simpler, but vulnerable to XSS token theft). The original guide has no precedent to lean on here since auth wasn't in scope. Recommend httpOnly cookie as the more defensible choice to explain in an interview, but this should be a real discussed decision, not a silent default — same spirit as the LLM-provider decision being left open for Phase 10.
- 🔲 **JWT expiry / refresh strategy:** a short-lived access token with a refresh token, or a single longer-lived token accepted as "good enough for a portfolio project"? The second is simpler and defensible for this project's scope; worth stating explicitly either way rather than leaving it implicit.
- 🔲 **Password reset flow:** in scope for this phase, or explicitly deferred to a "v2 ideas" README note (the same way the original guide deferred auth entirely in Phase 0–4)? Given this project's one real actual user account, a full "forgot password" email flow may be disproportionate effort — but that's Muneera's call, not a default.
- 🔲 **Email verification on registration:** same question as above — likely reasonable to skip for a portfolio project, but should be a stated decision, not an omission.
- 🔲 **Should schedule-item entry become a real UI form as part of this phase, or stay a manual SQL insert per new vehicle for now?** This phase's `POST /api/vehicles` endpoint solves "add a car," but doesn't by itself solve "enter that car's maintenance intervals" in a user-friendly way — right now that's still the same manual transcription process used for the original Lexus data. Worth deciding whether that's this phase's problem or a separate follow-up (see Section 7).

## 7. Related idea, deliberately NOT part of this phase's scope (yet)

Separately from auth, there's a good idea worth recording here so it isn't lost: since Phase 11 will already need to parse uploaded manual PDFs for RAG, that same parsing pipeline could be reused to auto-suggest `schedule_items` rows from an uploaded manual (LLM-extracted candidates, with a required human review/edit/confirm step before anything is saved — never auto-trust extracted maintenance intervals directly, since they're safety-relevant data). This would turn "add a car" from step 8 above into a genuinely good onboarding feature instead of just a bare form, and would be a strong, differentiated resume line. This is explicitly out of scope for Phase 4.5 itself — it depends on Phase 11's PDF-parsing infrastructure existing first — but is recorded here so a future session doesn't have to rediscover the idea from scratch. Revisit once Phase 11 is underway.

## 8. Summary for a future Claude session in one paragraph

If you're picking this project up and haven't read anything else yet: the project was single-user/single-car through a fully-complete, tested Phase 4, then a deliberate decision was made to generalize it to full multi-user auth before Phase 5, because retrofitting ownership scoping into S3 keys and AI tool calls later would be more painful than building them ownership-aware from the start. The schema absorbs this cleanly (one new `users` table, one new FK column) because the original guide already built `vehicles` as a proper FK-linked table. The auth logic itself (hashing, JWT issuance, and especially the ownership-verification dependency) is meant to be hand-written by Muneera, not generated, for the same reason the Phase 4 due-date algorithm was — it's both genuinely important to understand and a likely interview topic. Check Section 4 for exact build steps and their delegate/hand-write split, Section 5 for how this changes the plan for every phase from 5 onward, and Section 6 for decisions that still need to be made with Muneera directly rather than assumed.
