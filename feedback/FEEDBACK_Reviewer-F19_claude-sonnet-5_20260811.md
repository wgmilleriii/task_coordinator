# Feedback: Reviewer-F19 (claude-sonnet-5) — T-MIN-002 — 2026-08-11

## System-Level Feedback (task_coordinator engine)

- **Stale/false-positive `.fleet.lock`:** `./bin/fleet start-review` initially
  failed with "❌ Could not acquire lock. Another fleet process is currently
  running." `ps aux` showed no `bin/fleet` process running anywhere on the
  box, and `.fleet.lock` was a 0-byte file with an old mtime (from a prior
  session, `Aug 11 22:17`). `fcntl.flock` locks are normally released
  automatically when the holding process's file descriptor closes (including
  on crash), so this reads like either (a) a genuinely concurrent agent
  briefly holding the lock at the exact moment I ran the command, or (b) a
  lock acquired by a process that didn't exit cleanly and left the fd
  attached to something still alive (e.g. an orphaned child). A short retry
  (~15s) cleared it on its own. Recommend: `fleet` print the PID that
  currently holds the lock (readable via `/proc`/`lsof` equivalent) so an
  agent hitting this can tell "actually contended" from "stale," and/or a
  `--retry`/backoff flag on commands that can hit this instead of a hard
  fail on first attempt.
- **Concurrent scout/other-lane churn during review:** while reviewing, the
  working tree picked up unrelated uncommitted/untracked changes from other
  active agents (`tasks/active/T-PTG-001.yaml` modified, `T-INTY-017.yaml`
  + handoff, `T-PTG-001` review + handoff, an `Antigravity_Gemini` feedback
  file). None of these were touched or committed by me — I staged only
  `TASKS.md`, `tasks/active/T-MIN-002.yaml`, and
  `reviews/T-MIN-002_review.yaml`. This worked fine with careful `git add`
  of specific paths, but a repo with many parallel agents committing loose
  files to the same `main` branch (no locking around git itself, only
  around the `fleet` CLI's own file writes) is a latent source of an agent
  accidentally `git add -A`-ing someone else's in-flight work. Worth calling
  out in the README's safety notes explicitly: "never `git add -A` /
  `git add .` in this repo."
- Otherwise the review workflow (`start-review` → fill `reviews/*.yaml` →
  `record-review`) is clean and worked exactly as documented.

## Repository-Level Feedback (minchiate_tarot)

**Task:** T-MIN-002 — add a card-identification write path
(`/api/update`, file rename to archival name, ledger update, clickable
grid) to the stdlib `http.server`-based `minchiate_reviewer.py` that
`test-T-MIN-001` had rewritten from Flask. Author: Worker-F14, branch
`test-T-MIN-002`, head `94da0cc5`.

**Verdict: PASS.** No corrections needed or applied — the branch is
unchanged from what Worker-F14 submitted.

How the review was done: I created an isolated git worktree at the review
sha (`94da0cc5`) rather than touching the shared `minchiate_tarot` checkout
(which stayed on `test` throughout, confirmed before and after). I read the
full diff against the merge-base (`86ef0e4`, the tip of `test-T-MIN-010`)
and confirmed it introduces no new imports — `re`, `json`, `os`,
`urllib.parse` were all already imported in the pre-diff file, so the
"stdlib-only, no Flask" constraint from the module docstring holds.

Rather than trust the worker's handoff narrative, I ran the actual server
(`python3 minchiate_reviewer.py --port 8099`) in the worktree and drove it
with `curl`:

- A valid `POST /api/update` (`830124001_card_05.jpg` → type `TestType`,
  value `TestVal`) renamed the file on disk to `TestType_TestVal.jpg` and
  updated `ledger.json`'s `current_name`/`type`/`value`/`identified` fields
  — verified by re-reading the ledger and `os.listdir`, not by trusting the
  200 response alone.
- The highest-risk scenario per the review brief — a filename collision —
  was constructed directly: a second card was pointed at the same target
  filename the first card had just claimed. The server correctly returned
  HTTP 400 (`"File TestType_TestVal.jpg already exists"`), and I confirmed
  by MD5 that the existing file was byte-for-byte untouched and the second
  card's ledger entry was unchanged — no clobber.
- Unknown `original_name`, missing `type`/`value`, and malformed JSON bodies
  all return 400 with a JSON error and don't crash the server (confirmed the
  server still answered `GET /` with 200 immediately after each).
- Path traversal was attempted two ways: via `type` containing
  `../../../../tmp/evil` (the `SAFE_NAME_RE = [^A-Za-z0-9]+` filter strips
  all separators/dots before the filename is built, so it degraded to a
  harmless `tmpevil_x.jpg` inside `RAW_DIR`), and via `original_name` set to
  `../../../etc/passwd` (this is only ever used as a ledger dict-key lookup,
  never joined into a filesystem path, so it just returned "Unknown card").
  Neither escaped `RAW_DIR`.
- `python3 minchiate_reviewer.py --check` was re-run in the worktree both
  before and after the manual mutation tests and exits 0 with the expected
  97-card count each time.
- Grid HTML (`render_grid_html` via `load_sorted_cards`) reflects an
  update's new identity immediately on next load, with no manual ledger
  edit required — confirmed by re-rendering and checking the label text.

All four `definition_of_done` bullets in `tasks/active/T-MIN-002.yaml` are
met, and nothing beyond scope was added.

**System observation, not a task defect:** `test-T-MIN-002` descends from
`test-T-MIN-010` (`86ef0e4`), which descends from `test-T-MIN-001`
(`0509f69`) — neither ancestor is merged into `test` yet. `T-MIN-001` is
`human_review_required: true` and still awaiting the human's ruling;
`T-MIN-010` passed peer review previously but is being held pending that
same gate. T-MIN-002 is therefore also correctly *not* mergeable today, but
that is a sequencing/gate issue for the human and Fleet Coordinator, not a
correctness problem in this task's code — I did not attempt to merge
anything or resolve the gate.

**Recommended next steps:** the human should rule on `T-MIN-001` so the
whole `T-MIN-001 → T-MIN-010 → T-MIN-002` chain can merge into `test`
together; there's now a three-task backlog stacked behind that single
decision. Once merged, it would be worth a quick manual pass in a real
browser (not just curl) to confirm the `prompt()`-based UX is tolerable for
actually identifying 97 cards — it's minimal by design but very manual
(two blocking `prompt()` dialogs per card, no keyboard-only flow, no way to
correct a typo without re-clicking).
