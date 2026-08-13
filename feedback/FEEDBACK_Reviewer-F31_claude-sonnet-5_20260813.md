# Feedback — Reviewer-F31 (claude-sonnet-5), 2026-08-13

Session scope: peer review of T-MIN-024 (Cups pip cards, Ace–Ten, minchiate_tarot lane) only.
T-INTY-* and T-PTG-* tasks were seen in the board but ignored per the boundary rule. The
coordinator's primary checkout was left untouched (dirty on `test-engine-fixes` with other
agents' work) — all coordinator-side work was done in a worktree cut from a freshly fetched
`origin/main`.

## System-Level Feedback

1. **`bin/fleet` hardcodes a venv path that doesn't exist in a worktree.** `bin/fleet` sources
   `$DIR/../.venv/bin/activate`, which only exists in the primary checkout, not in any worktree
   created from it (the venv isn't tracked/copied). Running `./bin/fleet ...` inside a coordinator
   worktree fails with "No such file or directory" / "python: command not found". Every reviewer/PM
   that follows the HARD REQUIREMENT (isolated worktrees) will hit this. I worked around it by
   invoking `/Users/.../task_coordinator/.venv/bin/python bin/fleet.py ...` directly from inside
   the worktree, but this is a workaround, not a fix. Suggest either (a) a `requirements.txt`-based
   bootstrap that `bin/fleet` falls back to when no `.venv` is found next to it, or (b) documenting
   the direct-python invocation pattern in the README's worktree instructions so agents don't have
   to rediscover it.

2. **`record-review` silently jumps PASS_WITH_CORRECTIONS straight to DONE**, skipping
   `HUMAN_REVIEW`. The README's lifecycle table lists `PEER_REVIEW → HUMAN_REVIEW → DONE` as the
   standard path and says a human must `fleet close` a task once it reaches `HUMAN_REVIEW`. In
   practice `cmd_record_review` appears to treat any non-FAIL verdict (including
   PASS_WITH_CORRECTIONS, which by definition means the reviewer found something worth a human's
   attention) as terminal and marks the task DONE without a human ever seeing it. If that's
   intentional, the README's lifecycle diagram is misleading; if it's not intentional, tasks with
   real-but-non-blocking findings (like the citation-precision note I left on T-MIN-024) can reach
   DONE without a human ever reading the findings list. Worth a source check by whoever owns
   `bin/fleet.py`.

3. **`start-review`/`record-review` YAML round-tripping is fragile for long free-text findings.**
   PyYAML's default plain-scalar dumper breaks on findings text containing a colon-space sequence
   mid-sentence (e.g. "...cards 01, 04, 05, 09, 10 (plus full read of all 10): every card's...")
   — it silently produces invalid YAML that only fails at `record-review` time with an opaque
   scanner traceback, after the reviewer has already hand-edited a large findings block. Dumping
   review findings via `yaml.safe_dump` (which knows to quote a scalar containing `": "`) rather
   than hand-editing the template in a text editor avoids this, but the template itself invites
   hand-editing. A `fleet lint-review` command (parallel to `fleet lint`) that validates a
   review YAML's syntax and schema before `record-review` is attempted would catch this earlier.

4. **Stale `audited_repo_sha`/base is normal and requires the reviewer to know the difference
   between "worker's base" and "current test-branch tip."** T-MIN-024's audit sha (0ff3c97) was
   several merges behind the actual parent commit the worker branched from (493605c, after
   T-MIN-022's Swords batch landed). A naive `git diff <audited_sha> <head>` would have shown 22
   changed files including an entire unrelated Swords batch and produced a false "scope violation"
   finding. This is a trap for any reviewer who diffs against the recorded audit sha instead of
   `git log <audit_sha>..<head>` to find the worker's actual parent commit. Consider having `fleet
   audit`/the handoff record capture the worker's actual branch-point sha explicitly (distinct from
   the PM's audited_repo_sha) so reviewers don't have to reconstruct it via `git log`.

## Repository-Level Feedback (minchiate_tarot)

**Task reviewed:** T-MIN-024, ten Cups pip cards (Ace–Ten), light-tier format, by Worker-F26.
**Verdict recorded: PASS_WITH_CORRECTIONS.** Task is now DONE.

**What I checked and how:**
- Re-ran the audited verification command fresh in an isolated worktree at head
  `309e235672e6bf5db9be45d469e9706207d250eb` — passed, "OK, found 10 cards", exit 0.
- Recomputed every card's rank-in-suit from `Stage5_Master_Card_Registry.csv` by hand (Cups block
  sort_order 29–42, pips 29–38) — all 10 match the files and the batch report exactly.
- Diffed the worker's actual commit against its true parent (`493605c`, not the stale audited sha
  `0ff3c97`) — exactly 11 files touched (10 new drafts + the batch report), zero scope creep.
- Independently opened both cited primary sources rather than trusting the worker's characterization:
  - `CL-SC04-008` (Four of Coins pilot / its full dossier) genuinely and explicitly states a
    *general* round-suit rule naming Cups by name — "Bernardi's 1790 rules rank Coins and Cups
    numerals inversely." This is solid, direct support for the headline claim on its own.
  - `C-CUPS12-002` (Cavalier of Cups pilot) turned out to be narrower than the citation implies:
    the actual atomic claim register entry only covers the four-court ordering (Fantina < Cavallo
    < Regina < Re), not the numeral run "10…Ace" that the ten new files quote alongside it. The
    numeral-run sentence is real and does appear in the same source document's body prose, sourced
    to the same RULE-1790 pp. 5–6 witness — so nothing is fabricated — but citing it under that
    specific claim ID overstates the ID's registered scope. Importantly, this exact attribution
    pattern already existed verbatim in the pre-existing (already-DONE, out-of-scope) Cavalier of
    Cups pilot draft; Worker-F26 reused an existing citation rather than inventing a new one, and
    the general CL-SC04-008 citation alone is sufficient to support the headline claim regardless.
    I logged this as a MAJOR-severity finding for visibility but did not treat it as FAIL-worthy,
    since the substance survives independent check even though one of the two citation IDs is
    imprecise.
- Spot-checked five cards' (01, 04, 05, 09, 10) trick-order prose against the sourced ordering —
  consistent throughout; Ten of Cups correctly self-identifies as the trick-weakest card despite
  carrying the highest printed number.
- Independently verified the self-reported "stray second card-ID token" bug fix: grepped all 10
  files for `SUIT-CUPS-\d{2}` uniqueness — each file contains exactly one token, matching the
  batch report's account of the catch-and-fix.
- Independently verified the Five of Cups RWS-exclusion rewrite — no literal "upright" token
  remains anywhere in the file, while the RWS scene is still substantively excluded.
- Grepped section 3 (scoring) across all 10 files for unsourced point/combination amounts — none
  found; every card states "none" for intrinsic points and cites the same claim chain.
- Read the batch verification report in full — it is genuine and specific (matches my independent
  findings almost line for line, including the same bug-fix narrative), not templated boilerplate.

**Lessons / process note for future reviewers on this lane:** the biggest single risk on a
"we finally found a sourced rule" claim isn't fabrication outright — it's citation-ID
over-attribution, where a real sentence from a real source gets pinned to the nearest available
claim ID rather than one that was actually scoped to cover it. Worth grepping the *literal text*
of every cited claim ID's register entry, not just trusting that the ID exists in the source
document, before signing off on a "headline sourced" claim.

**Recommended next steps:** none blocking. The claim-ID precision issue flagged above is cheap to
fix in a future pass (add a dedicated atomic claim to the Cavalier of Cups pilot's claims table
for the numeral-run sentence, then repoint the ten Cups pip files' `C-CUPS12-002` references to
the new ID) but does not need to hold up DONE status given the general CL-SC04-008 citation
independently supports the batch's headline claim.
