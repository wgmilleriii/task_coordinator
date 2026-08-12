# Feedback — Worker-F14 (claude-sonnet-5), T-MIN-002

Executed T-MIN-002 ("Add card-identification write path to
minchiate_reviewer.py") end to end: claim → branch → implement → verify →
submit → PEER_REVIEW.

## System-Level Feedback

1. **Audited tasks can be based on a sha that never landed on the branch a
   Worker is told to start from.** T-MIN-002 was audited against
   `0509f6914e201ba192717c7a90c3c4154e5120fc` (the stdlib http.server
   rewrite of `minchiate_reviewer.py`, done on branch `test-T-MIN-001`).
   But the shared repo's `test` branch — the branch Workers are told to
   branch from — never merged that rewrite; `test` HEAD still had the
   *original Flask version* of the file (no `--check` mode, no
   `do_GET`/stdlib server at all). Branching from `test` as literally
   instructed would have produced a task built on the wrong file and a
   `verification_command` (`python3 minchiate_reviewer.py --check`) that
   couldn't even run. I found `test-T-MIN-010` (a separate, since-DONE
   task) carried the rewrite forward correctly and branched from its tip
   (`86ef0e4`) instead, which matched what the task's `scope` actually
   described. This is a real discoverability gap: nothing in `fleet claim`
   or the task YAML flags that the `audited_repo_sha` isn't reachable from
   `test`, or points a Worker at the branch that *does* have it. Suggest
   `fleet claim`/`fleet audit` verifying `audited_repo_sha` is an ancestor
   of the target branch (or the branch itself, if task-branches are meant
   to compose) and failing loudly, or printing the nearest branch that
   contains it, rather than leaving a Worker to `git log --all -- <file>`
   across every sibling `test-T-MIN-*` branch to reconstruct provenance by
   hand.

2. **Confirms Worker-1's prior report on shared-checkout risk.** The
   minchiate_tarot checkout is genuinely shared, mutable state across
   concurrent agents — mid-session, one `git log -5` and the next showed
   different HEAD commits without me switching branches, which only makes
   sense if another agent's process touched the working tree in between
   my two Bash calls. Nothing was lost this session (branches are
   independent refs and I re-verified state before every commit), but this
   is the second independent report of the same failure mode. Per-task
   `git worktree` isolation (as Worker-1 already suggested) would remove
   the need for every Worker to defensively re-check `git branch
   --show-current` before every single command, which is currently the
   only thing standing between this pattern and real data loss.

## Repository-Level Feedback

**What was implemented:** `minchiate_reviewer.py` (branch
`test-T-MIN-002`, head `94da0cc5845782f8eeacca57f7eacd5dbd41efb3`, based on
`test-T-MIN-010`'s tip `86ef0e4`):
- `update_card_identity(ledger, original_name, card_type, card_value)` — a
  pure-ish helper that validates a proposed identity, checks the target
  archival filename (`{Type}_{Value}.jpg`) doesn't already exist on disk,
  renames the file under `research/evidence/cards_raw/`, and mutates the
  ledger dict in place (`current_name`, `type`, `value`, `identified`).
  Caller still owns persisting via `save_ledger()`, matching the module's
  existing separation of concerns.
- `ReviewerHandler.do_POST` / `_handle_update` / `_send_json` — a new
  `POST /api/update` route reading a JSON body
  (`{original_name, type, value}`), calling the helper, and returning JSON
  with 200 on success or 400 on any validation/collision/unknown-card
  failure — matching the old pre-rewrite Flask `/api/update` route's
  semantics, stdlib only (no Flask/Jinja2 added).
- `render_grid_html` — each card `<figure>` now carries an
  `onclick="identifyCard(...)"` (JSON-escaped `original_name`, since
  `current_name` changes on rename) that runs a `prompt()`/`prompt()`/
  `fetch(POST)`/`location.reload()` flow, so identification is enterable
  from the browser, not only via curl, per the task's scope.

**How this satisfies the definition_of_done:** verified with a manual
integration test in an isolated scratch fixture (two real card images,
a synthetic ledger, a real `ThreadingHTTPServer` on an ephemeral port) —
not committed to the repo, just used to prove behavior before submitting:
  - Valid POST renamed the file, updated
    `current_name`/`type`/`value`/`identified` in `ledger.json`, and the
    new filename existed on disk while the old one didn't.
  - A POST whose computed target filename already existed on disk
    returned 400, left the ledger entry and both files untouched (no
    clobber).
  - Reloading `/` after a successful update showed the new label and
    `/images/<new-name>` in the rendered HTML.
  - An unknown `original_name` also returned 400.
  - `python3 minchiate_reviewer.py --check` still exits 0 on the real repo
    (unaffected by the scratch fixture).

**Verification output** (`./bin/fleet verify T-MIN-002 --model
claude-sonnet-5`): PASSED —
`Found 97 image(s)... Loaded and sorted 97 card record(s)... GET / ->
status 200... Rendered page references 97 card image(s)... GET
/images/830136001_card_00.jpg -> status 200... OK: server starts cleanly
and serves a 97-card geographic grid.` Exit code 0. Handoff captured at
`handoffs/T-MIN-002_handoff.yaml`, `head_sha`
`94da0cc5845782f8eeacca57f7eacd5dbd41efb3`, submitted to `PEER_REVIEW`.

**Concerns / next steps:**
- `test-T-MIN-002` and `test-T-MIN-010` are still unmerged into `test`
  (same for `test-T-MIN-001` itself). Someone (PM or human) needs to
  decide a merge order — T-MIN-002 depends on T-MIN-010's caption fix
  being present, and both depend on the T-MIN-001 rewrite. Landing `test`
  → these branches in the wrong order, or landing `test-T-MIN-002` without
  first landing `test-T-MIN-010`, would silently drop the caption fix.
- The `prompt()`-based identification UI is intentionally minimal per the
  task's own wording ("a click handler / small inline form per card, or a
  simple prompt-based flow") — it's usable for a human doing the actual
  card-review pass, but a follow-up task to replace the two sequential
  `prompt()` calls with a proper inline form (dropdown for
  Suit/Trump/Fool, text input for value) would materially speed up
  reviewing all 97 cards.
- No authentication/CSRF protection on `/api/update` — acceptable for a
  localhost-only dev tool per the module's existing design, but worth
  flagging if this is ever exposed beyond `127.0.0.1`.
