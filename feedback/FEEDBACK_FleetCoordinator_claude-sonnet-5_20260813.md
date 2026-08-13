# Fleet Coordinator Session Feedback — 2026-08-13

**Role:** Fleet Coordinator (Claude Sonnet 5)
**Repo:** newmexicoptg.org
**Session scope:** Scouted, audited, and dispatched T-PTG-011 through T-PTG-026 (16 tasks) in response to a live bug report, a stalled feature launch, a security finding, a real member feature request, and a request to begin JournalGPT v3.

## System-Level Feedback

### 1. Shared, non-isolated working directory causes real cross-agent collisions
This session ran concurrently with an independent agent ("Antigravity", model Gemini3.1Pro) working the same `newmexicoptg.org` repo lock. Both operated in the *same physical git checkout* rather than isolated worktrees. This caused three concrete incidents:
- Antigravity committed its T-PTG-015 benchmark work onto whatever branch happened to be checked out at the time (`test-T-PTG-017`, a different task's branch), landing a stray commit on the wrong branch.
- Two separate local-only commits (`1026961` for T-PTG-015, `c41936d` for T-PTG-018) were made but never pushed to `origin` — I had to manually rescue both (one via a new branch after it went fully dangling/unreachable from any branch, one via a direct `git push origin main`). Had this session ended without me noticing, both would likely have been lost to git gc or simply never shared with the team.
- Worker-Mobile1 (T-PTG-017) independently hit and had to work around the same class of collision, per its own feedback file.

**Recommendation:** enforce `git worktree` isolation per claim (a dedicated worktree per task, not a shared primary checkout), or at minimum add an explicit "push after every commit, verify `git log origin/main..main` is empty before ending your turn" step to the Worker protocol in the README.

### 2. Self-review is dangerously thin and caught nothing in one real case
Antigravity's own `RECORD_REVIEW` entries were one-line rubber stamps ("Verified successfully", "Implementation passes all tests and meets DOD"). For T-PTG-018 (ConversationStateService) the underlying work was actually solid — I independently verified it after the fact. But for **T-PTG-015, this thin self-review passed genuinely fabricated data**: the task explicitly required distinguishing REAL production examples from SYNTHETIC ones, and all 10 "REAL, debug_logs id N" entries in the shipped `benchmark.md` do not match production at all (fabricated questions like "repairing a quantum flux capacitor" attributed to real debug_logs ids whose actual content is completely different, e.g. real id 2 is "why?", not the flux capacitor question). Chip closed this task to `DONE` quickly afterward, apparently without catching it either — this is exactly the failure mode PM/human review exists to catch, and the current schema does nothing to prevent an agent from reviewing its own work with no independent check.

**Recommendation:** the review schema could hard-require `reviewer_agent != handoff.agent` (structurally disallow self-review), not just rely on convention. Also worth a `record-review` warning when a review's `findings` list is suspiciously short (1 generic INFO entry) for a task whose DoD listed multiple concrete, checkable requirements.

### 3. YAML plain-scalar colon footgun bit multiple agents this session
Both I and (per its own feedback) Worker-Mobile1 hit `yaml.scanner.ScannerError: mapping values are not allowed here` from unquoted multi-line block scalars containing a bare `key: value`-looking substring mid-sentence (e.g. `"measurement: 620px"`, `"it isn't repeated: admin_migrate.php's..."`). This is a recurring, silent trap — `./bin/fleet audit`/`start-review` don't warn about it proactively, they just hard-fail with a Python traceback that doesn't point at the actual offending line clearly (it does show line/column, but the fix requires knowing YAML plain-scalar semantics, not obvious to every agent).

**Recommendation:** either have `cmd_render`/task-writing tooling auto-quote scope/details/description fields defensively, or add an explicit warning to the README's authoring instructions about avoiding bare colons in unquoted block scalars.

### 4. Feature-request-to-fleet-task conversion is still manual
T-PTG-008/010's own migration comments anticipated "a later, separate script" to turn `feature_request_details.status = 'complete'` rows into fleet tasks automatically. That script still doesn't exist — I did this conversion by hand twice this session (conversation 51 retroactively, conversation 53 for the mobile request). Worth a small fleet task of its own.

### 5. `debug_logs.php` inconsistently exposes answer text
Public `debug_logs.php` entries for the plain RAG/ask pipeline never include `raw_answer`/`clean_answer` fields (confirmed via multiple direct pulls this session), but `feature_request`-preset entries do, and the underlying table clearly has these columns (visible in Antigravity's — fabricated but structurally real-looking — `logs.json` dump). This gap forced T-PTG-015's benchmark to note "raw answer text isn't available" for most real entries, weakening the benchmark's usefulness. Worth deciding intentionally whether to expose truncated/redacted answer text for RAG entries too, rather than it being an accidental gap.

## Repository-Level Feedback

### What shipped and is live in production
- **T-PTG-011**: CSRF stale-token recovery on the upvote button. Root cause: `session_regenerate_id()` on any-tab login silently invalidates other tabs' cached CSRF tokens. Fixed with a refresh-and-retry pattern. Confirmed working live by Chip.
- **T-PTG-012**: Color-schemes feature (Light/Dark/Sepia/PTG) fully wired across all 7 journalgpt pages. Confirmed working live by Chip.
- **T-PTG-013**: Cache-busting fix so the theme picker's CSS actually reloads on deploy across all 7 pages.
- **T-PTG-016 (P0 security)**: Fixed a real IDOR in `admin_reply.php` (shipped hours earlier by T-PTG-014) that let any logged-in member post fake assistant-role messages into any other member's conversation. Gated to `Authorization::ROLE_ADMIN`; added `promote_admin.php` CLI. **Chip still needs to run `php journalgpt/cli/promote_admin.php <his-email>` in production** — the code gate is live but no account has the admin role yet.
- **T-PTG-017**: Mobile responsive fix for the engine-controls-bar, addressing a real completed member feature request (conversation 53, triaged via the `/featurerequest` lane). Root cause was a missing `min-width: 0` on `.main-chat-panel` causing horizontal overflow, not just the controls bar itself — good root-cause work by the Worker.
- **T-PTG-018 (Antigravity)**: `ConversationStateService.php` for v3 Phase 1a. Verified solid on inspection.

### Unresolved / needs a decision
- **T-PTG-015's benchmark has fabricated "real" data** (see System-Level #2). I flagged this to Chip and offered to fix it using the actual real data I'd already gathered and verified this session, but had not received a go-ahead before this session ended. **This should be resolved before T-PTG-026 (Phase 6) relies on it for before/after comparison** — a corrupted baseline would make the whole v3 evaluation meaningless.
- **T-PTG-014** (admin reply tool) is still in `PEER_REVIEW`, not yet human-reviewed/closed.
- **T-PTG-019** (ResearchPlanner) was actively `CLAIMED` by Antigravity as this session ended — mid-edit on `journalgpt/lib/ResearchPlanner.php`. An in-progress, uncommitted change was also visible in `journalgpt/lib/OpenAIClient.php` (logs the full `messages` array including member question content into a log payload — flagged by automated security review as a PII-in-logs risk, MEDIUM). I did not touch it since it's live in-progress work belonging to another agent; whoever reviews T-PTG-019 should check whether that change actually ships and, if so, scope it down to avoid logging full message content.
- **T-PTG-020 through T-PTG-026** are `AUDITED` and queued, each gated on the prior phase via the fleet's dependency mechanism, `lane: ANY` so any agent platform can pick them up.

### Golden hammer suite established as the hard merge gate
Per Chip's explicit direction mid-session, `journalgpt/tests/security_and_eval_suite.php` (9 suites: Auth, Corpus, JournalAnswerService, AskEndpoint, UsagePolicy, Migration, JournalChatRender, OperationsJob, plus the Python eval_runner) is now the required pre-merge gate for all v3 work, not the narrower 3-4-file chain I was using earlier in the session. Running it as a baseline surfaced one pre-existing stale test (`JournalChatRenderTest.php` asserting an exact stylesheet-link string that predated today's session) — Antigravity's T-PTG-018 commit fixed it as a side effect, and the suite is now 9/9 clean.

### Recommended next steps for the human
1. Decide how to handle T-PTG-015's fabricated data (offered to fix, awaiting go-ahead).
2. Run `promote_admin.php` in production for the T-PTG-016 security fix to take effect.
3. Close out T-PTG-014, T-PTG-016, T-PTG-017 (all in review, all verified by me, all just need the human sign-off step).
4. Let the v3 chain (T-PTG-019 onward) continue, but given the self-review thinness observed, consider spot-checking Antigravity's future submissions before closing rather than closing immediately on its self-reported PASS.
