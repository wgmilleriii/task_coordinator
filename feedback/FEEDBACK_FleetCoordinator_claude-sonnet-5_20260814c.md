# Feedback: Fleet Coordinator (claude-sonnet-5), 2026-08-14 (session c)

Session summary: dispatched into `task_coordinator` mid-conversation, after a
long direct human-agent discussion in `newmexicoptg.org` about a per-article
extraction spike that had already run (see
`docs/superpowers/specs/2026-08-14-per-article-extraction-spike-findings.md`
and same-day session handoff). Did three things as Fleet Coordinator: (1)
found and cancelled four stale duplicate tasks, (2) dispatched a Scout + PM
audit + Worker for a new, real task (T-PTG-047), (3) this write-up. Did not
touch code or task YAML content myself except the cancellations (explicit
human-authorized cleanup, not scope work).

## System-Level Feedback

1. **No `.venv` existed in `task_coordinator` at session start** — `bin/fleet`
   (a bash shim) sources `$DIR/../.venv/bin/activate` unconditionally and
   fails with a raw Python traceback (`invalid syntax` from trying to run the
   shim itself as a Python script — a confusing first error) if it's
   missing. Had to `python3 -m venv .venv && .venv/bin/pip install -r
   requirements.txt` before anything worked. `pip install -r
   requirements.txt` directly also fails on this machine (Homebrew Python's
   PEP 668 externally-managed-environment guard) — the venv step isn't
   optional, but nothing in the README's "Startup Instructions" or
   "Environment" step says to create one; it just says "install dependencies
   via `pip install -r requirements.txt`," which doesn't work as literally
   written. Worth an explicit `python3 -m venv .venv` step in the README, or
   a `bin/fleet` self-check that creates it on first run with a clear
   message instead of a Python `SyntaxError`.

2. **`./bin/fleet close` only supports transitioning a task to `DONE`** —
   there's no CLI path to `CANCELLED`, even though it's a valid status in
   `schemas/task.schema.json`'s enum and `bin/fleet archive`'s own help text
   explicitly mentions sweeping "DONE, CANCELLED, and DEFERRED" tasks. I
   needed to cancel four stale tasks (see Repository-Level) and had to hand-edit
   the YAML files directly (`status: CANCELLED` + an appended `CANCEL` event)
   rather than use a documented command, then ran `fleet lint` to sanity
   check. A `./bin/fleet cancel <task_id> --human <name> --reason <text>`
   command would close this gap and give cancellations a consistent event
   shape instead of whatever format each hand-edit happens to use.

3. **Confirmed independently, same defect a Worker already reported this
   session (`FEEDBACK_Worker-ExtractionRepair1_...`) and a prior day's
   session also reported: `fleet lint` currently fails on 5 pre-existing
   task files** (`T-PTG-042` through `046`) with `Additional properties are
   not allowed ('description' was unexpected)` — these files use a bare
   `description:` field instead of the schema's required `scope:` (array)
   and have `definition_of_done` as a single formatted string instead of an
   array. This predates my session (I didn't author these tasks, a prior
   Scout/PM pair did) and I left it as-is rather than silently reshaping
   task content I was there to cancel, not fix — but it means `fleet lint`
   currently reports 5 failures on a totally ordinary board, which trains
   whoever runs it to expect lint noise and skim past real new errors. Worth
   either a one-time migration pass on the old files, or relaxing the schema
   to accept the drifted shape if it's actually meant to be tolerated.

## Repository-Level Feedback (newmexicoptg.org)

### 1. Cancelled T-PTG-042, 043, 044, 045 (stale duplicates, human-approved)

These four tasks (Phase 1-4 of a "Metadata Index / RAG Pipeline / Citation
Analytics / Member Knowledge Profiles" plan) were sitting in `PEER_REVIEW`,
audited and claimed/submitted on 2026-08-13, by a different session/model
(`Antigravity`, per the handoff branches' commit metadata) than the one that
actually shipped the real equivalent features. I found, and confirmed with
the project owner before acting, that all four described building things
that **already exist**, built through a separate, non-fleet-tracked session
documented in `docs/superpowers/specs/2026-08-14-session-handoff.md`: the
real `articles` table (T-PTG-042's proposed `journalgpt_articles`), the real
`journalgpt_citation_logs` table with live production data in it (T-PTG-044),
and the real "My Knowledge Profile" / Research Topics page on `profile.php`
(T-PTG-045, described as a new "radar chart" page). Checked `git branch -a`
and confirmed none of `test-T-PTG-042` through `045` were ever pushed to
`origin` — so there was no actual merge collision, just board/reality drift.
Cancelled all four with a `CANCEL` event citing the specific already-shipped
equivalent for each (see the task YAMLs' event logs for exact rationale).

**Lesson for whoever Scouts/PMs next in this repo:** this board currently has
no reliable way to detect "a human already built this outside the fleet,"
and it will keep happening as long as direct human-agent sessions (a
completely normal way to use this tool) and fleet-dispatched sessions both
write to the same repo without cross-referencing each other. A PM auditing a
new task should grep the target repo's own recent `docs/` and `git log`
for the feature name before auditing, not just check `audited_repo_sha`
mechanically — that would have caught this before four tasks got claimed and
"submitted" against work that didn't need doing.

### 2. Dispatched and closed out T-PTG-047 (the real, new work)

Wrote via Scout, audited via PM (myself), executed via Worker
(`Worker-ExtractionRepair1`) in isolated worktree
`../newmexicoptg.org-T-PTG-047`. Full technical outcome is in the Worker's
own feedback file and `docs/30-Engineering/2026-08-14-page-coverage-validation-repair-pass.md`
— not duplicating it here. Headline for the project owner: the repair pass
closes most overlaps (51→7) but makes gap pages measurably worse (108→164,
mechanically explained — repairing mis-anchored pieces un-masks gaps that
overlaps were previously hiding), so **schema design should not proceed on
the strength of this pass alone.** The clearest next step, given the
Worker's one successful vision-model data point, is a gap-page fallback
classifier (vision-based, given text extraction's demonstrated blindness on
sparse ad pages) and/or giving each piece a `review_status`/`needs_review`
field so imperfect page ranges don't silently pass as trustworthy.

**Recommended next steps for the human:**
- Decide whether to greenlight a follow-up task scoped specifically to the
  gap-page problem (vision-model fallback classifier) before any schema
  design work starts — that's the one finding from T-PTG-047 that should
  gate the next task, not just inform it.
- The FTP transfer of original PDFs into `journalgpt/pdfs/` was still in
  progress during this session (74-82 of ~94 expected files landed,
  covering most but not all of the corpus). Worth re-confirming the
  full set landed before any wider vision-model prototype task, since
  that work is specifically unlocked by having real PDFs, not just the
  already-extracted `.txt` corpus.
- The five schema-drift task files (see System-Level #3) are worth a
  cleanup pass whenever someone's next touching this repo's lane on the
  board, so `fleet lint` returns to a clean baseline.
