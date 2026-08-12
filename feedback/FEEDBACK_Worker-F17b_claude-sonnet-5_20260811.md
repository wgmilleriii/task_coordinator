# FEEDBACK: Worker-F17b (claude-sonnet-5) — 2026-08-11/12

Resuming T-MIN-003 after it was BLOCKED by Worker-F17 on a genuine data
collision (two ledger entries both independently identified as Trump 27 /
Aries) and then UNBLOCKED once the human (Chip) reviewed the collision live
in the running app and made a curation decision.

## System-Level Feedback

- **The block/unblock loop worked exactly as designed.** Worker-F17 correctly
  refused to paper over a real data collision inside a one-shot rename
  script's scope, wrote a clear BLOCK reason with concrete evidence (dhash
  Hamming distance, visual match, likely double-extraction from overlapping
  tile geometry), and left the branch in a clean, re-resumable state (script
  committed, 92/93 renames already applied). That meant this session needed
  zero rediscovery work — I could read the block reason, confirm Chip's
  resolution against the ledger, and finish in under 10 tool-call rounds.
  This is a good advertisement for keeping BLOCK a first-class status rather
  than forcing an agent to either fudge verification or abandon a task.
- **One friction point**: nothing in the coordinator enforces that a human's
  resolution recorded in a throwaway demo worktree (the `wt-run-tmin001`
  scratch checkout mentioned in my dispatch) gets carried into the real
  branch. I had to be told explicitly which fields Chip set and copy them by
  hand into `test-T-MIN-003`'s `ledger.json`. If a human is going to resolve
  a data collision interactively in a running app, it would be worth the
  coordinator (or a small helper script) diffing the demo worktree's
  ledger.json against the real branch's and proposing the patch, rather than
  relying on the dispatch prompt to transcribe it correctly by hand.
- `./bin/fleet verify` and `./bin/fleet submit` both worked cleanly on the
  first try once the branch was in the right state — no complaints there.

## Repository-Level Feedback

- Chip's resolution: `830154001_card_05.jpg` (the duplicate scan) got
  `type="Trump"`, `value="AriesDuplicate"` in ledger.json, keeping
  `identified: true` / `human_confirmed: true` as-is. `830140001_card_08.jpg`
  remains the canonical Trump 27 (Aries) and was already renamed to
  `Trump_27Aries.jpg` in the prior 92-rename batch on this branch.
- Applied that single-field ledger edit by hand (minimal diff — only the
  `value` field changed, formatting preserved via `json.dump(..., indent=4)`
  to match `save_ledger()`'s convention), then re-ran
  `python3 finalize_identifications.py`. It renamed the file to
  `Trump_AriesDuplicate.jpg` with zero collision against `Trump_27Aries.jpg`
  — the two archival names diverge as soon as "AriesDuplicate" stops
  matching "27 (Aries)", which is exactly why Chip's naming choice unblocks
  the script without any code changes.
- Verified idempotency by hashing `ledger.json` and the sorted directory
  listing before/after a second run of the script — both hashes were
  identical, confirming the second run was a true no-op.
- Ran the full audited `verification_command` end-to-end (double
  `finalize_identifications.py` run + the inline Python assertions +
  `minchiate_reviewer.py --check`) — it now passes cleanly: 97 ledger
  entries, 0 pending renames, 0 missing files on disk, and the reviewer
  server still starts and serves a 97-card geographic grid.
- **Lesson learned**: the "duplicate scan" resolution pattern (give the
  extra scan a distinguishing `value` suffix like "Duplicate" rather than
  deleting the file or moving it out of `cards_raw/`) is a clean, minimal
  way to resolve dedupe-script blind spots after identification has already
  happened — it required zero changes to `finalize_identifications.py`,
  `update_card_identity()`, or the archival naming convention. If more such
  collisions turn up in future identification batches (this one was missed
  by `dedupe_cards.py` before identification because the two tiles were
  visually similar but not identical enough to trip its threshold), the same
  pattern should generalize fine.
- **Next steps for the human**: consider whether `830154001_card_05.jpg` /
  `Trump_AriesDuplicate.jpg` should eventually be moved to a
  `cards_raw/duplicates/` subfolder (as originally speculated by Worker-F17)
  so the main 97-card grid reflects only physically distinct cards, or
  whether keeping it in the primary set as a labeled duplicate is the
  intended long-term state. That's a product decision outside this task's
  scope — T-MIN-003 only covered applying the already-recorded
  identifications, which is now fully done (93/93).
