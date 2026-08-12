# Feedback — PM-F8 (claude-sonnet-5), 2026-08-12

## System-Level Feedback

- **Self-contradictory verification commands are a real, recurring failure mode, not a one-off.**
  T-MIN-016's audited `verification_command` looped a blind "zero occurrences of TRUMP-FOOL" grep
  over `Stage5_Master_Card_Registry.csv`, `Stage5_Master_Card_Registry.json`, and
  `Card_Dossier_Skeletons.json` — the exact three files the same task's `definition_of_done` (item 1)
  required to carry a `TRUMP-FOOL` string inside a new `aliases` field. No implementation could ever
  pass both. Worker-F18 did the right thing: implemented the full DoD, ran `fleet verify`, watched it
  fail deterministically, and self-BLOCKed with a precise root-cause writeup instead of falsely
  submitting or silently reworking the command itself. That is exactly the intended escalation path
  and it worked. Feature request: when a PM audits a task whose DoD requires a literal string to
  **remain** present in a file, and the same task's verification also asserts a **zero-occurrence**
  check touching that same file, `fleet audit` could flag it as a likely self-contradiction before
  the command is locked in (a cheap static check: does the DoD's "must contain X" file set intersect
  the verification's "must not contain X" file set for the same literal X?). Would have caught this
  at audit time instead of costing a full worker cycle.
- **`fleet lint` output is noisy for PMs scoped to one repo lane.** Running `./bin/fleet lint` to
  confirm my edit didn't break schema also surfaced an unrelated failure in `T-INTY-017.yaml`
  ('dod' unexpected additional property), which is a different repo's task entirely and out of my
  lane per the boundary rule. It cost a moment of "is this mine?" triage. A `--repo <name>` filter
  on `lint` (or at minimum grouping output by repo) would let a PM confirm "my file is schema-valid"
  without wading through other lanes' pre-existing breakage.
- **Concurrent same-checkout writes are visible and can bleed into unrelated commits if a PM isn't
  careful.** Mid-session, `git status` picked up an uncommitted modification to `tasks/active/T-INTY-018.yaml`
  (status CLAIMED -> PEER_REVIEW, new SUBMIT event) plus a new untracked `handoffs/T-INTY-018_handoff.yaml`,
  clearly another agent (Worker-Gazelle1) acting in the same working tree at the same time. I did not
  stage or commit either — only `tasks/active/T-MIN-016.yaml` and a fresh `TASKS.md` render went into
  my commit — but the *rendered* `TASKS.md` unavoidably reflects that other agent's uncommitted
  in-flight state too, since `fleet render` reads whatever is on disk. This is a real race: two agents
  sharing one working directory means one agent's `render` can publish a preview of another agent's
  not-yet-committed work. Recommend either (a) each agent operate in its own `git worktree` as the
  README hints for humans, or (b) `fleet render` gain a `--staged-only` / `--committed-only` mode that
  reads from HEAD instead of the working tree, so a PM's TASKS.md commit can't accidentally leak a
  peer's uncommitted status transition ahead of their own commit landing.

## Repository-Level Feedback (minchiate_tarot)

- **What was actually broken and how I fixed it:** T-MIN-016's DoD correctly required a new `aliases`
  field to land on the SPECIAL-FOOL row of `Stage5_Master_Card_Registry.csv`/`.json` and in
  `Card_Dossier_Skeletons.json`, containing the literal `TRUMP-FOOL` (the permanent-alias mechanism
  for D3, later reused by D4/T-MIN-017). But the audited `verification_command`'s first loop treated
  those same three files as "must have zero TRUMP-FOOL occurrences," which is the opposite requirement.
  I rewrote the command to (1) keep the blind zero-occurrence loop only for the eleven study-draft
  files (where TRUMP-FOOL must be fully gone, id or alias), (2) add positive/negative pairs asserting
  `card_id`/`dossier_id`/`database_id`/question-id-prefix is `SPECIAL-FOOL` and never `TRUMP-FOOL` as
  a *primary* identifier in the three data files, and (3) keep/verify the existing checks that the
  `aliases` field/column literally contains `TRUMP-FOOL` for that one row (those were already correct
  in the original command; I left them alone).
- **I did not trust theory — I dry-ran the real thing.** I checked out `origin/test-T-MIN-016`
  (head `3ac0db7`) into a disposable `git worktree` (kept the PM's own checkout on branch `test`
  undisturbed the whole time — never touched or committed inside the target repo) and ran the exact
  corrected `bash -c '...'` string against it: **PASS**. As a control, I ran the identical command
  against the pre-implementation sha `09f857d` and confirmed it correctly **FAILS** (caught the first
  un-renamed draft file), so the new checks aren't accidentally toothless. One real bug surfaced during
  this dry run that pure inspection would have missed: the registry CSV has **CRLF line endings**, so
  a naive `grep -E "^SPECIAL-FOOL,.*TRUMP-FOOL$"` end-anchor silently failed against the trailing `\r`
  on BSD/macOS grep even though the row content was correct — I dropped the end anchor
  (`grep "^SPECIAL-FOOL," | grep -q "TRUMP-FOOL"`) to make the check CRLF-agnostic. This is worth
  flagging for whoever eventually touches that CSV's line endings — any future line-anchored check
  against it should account for `\r`.
- **Worker-F18's implementation on `test-T-MIN-016` looks complete and correct** against every DoD
  item I could independently verify: `SPECIAL-FOOL` is the primary id everywhere required, `TRUMP-FOOL`
  is fully purged from the eleven cross-referencing drafts, the old
  `PERSONALITY_TRUMP-FOOL_Fool.md` file is gone and `PERSONALITY_SPECIAL-FOOL_Fool.md` exists,
  `sort_order` is 0 in the CSV/JSON/skeletons, the schema's `sort_order.minimum` was widened to 0,
  and the `aliases` mechanism is present and correctly scoped (schema `description`, optional/not
  required, exactly one `TRUMP-FOOL` mention in the skeletons file). I did not touch any content file
  in `minchiate_tarot` myself — only read via `git show`/worktrees.
- **Next steps:** the task is `CLAIMED` again (unblocked, owner still Worker-F18). A worker should
  resume it, run `fleet verify T-MIN-016` for real against `test-T-MIN-016`, fill in the handoff
  `head_sha`, and `fleet submit`. T-MIN-017 (Knight alias, D4) depends on this task and reuses the
  same `aliases` mechanism — whoever audits that one should point at this same field rather than
  inventing a second shape, per the scope note already baked into T-MIN-016.
