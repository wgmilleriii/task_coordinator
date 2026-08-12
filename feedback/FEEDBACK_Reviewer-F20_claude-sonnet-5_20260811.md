# Feedback — Reviewer-F20 (claude-sonnet-5), 2026-08-11

Task reviewed: T-MIN-014 (PEER_REVIEW → DONE), Worker-F15, branch
`test-T-MIN-014`, head `925d124662aac435995b1ef047f14c825b665aa8` (base
`19c26db`). Verdict: **PASS**, no corrections needed.

## System-Level Feedback

- **`start-review` template's YAML single-quoting trap.** The generated review
  template uses single-quoted block strings. When a finding's `description`
  contains an apostrophe (e.g. "CW-1's TEM-C020"), it must be escaped as `''`
  or the file silently fails `yaml.safe_load` inside `record-review` with a
  fairly opaque `ParserError` pointing at the wrong line. I hit this once
  (line 94, "CW-1's" vs the escaped "CW-1's" — 33 lines away from the actual
  unescaped apostrophe at "record's" a few lines earlier had been escaped
  correctly, which made the bug non-obvious at a glance). A reviewer writing
  long, quote-heavy citation-verification findings (which this task type
  demands) is exactly the case most likely to trip this. Suggestion: either
  have `record-review` validate/report the offending line more precisely, or
  switch the template to a literal block scalar (`|-` / `>-`) so apostrophes
  don't need escaping at all — that would remove an entire class of avoidable
  friction for reviewers writing prose-heavy findings.
- **Worktree-based review flow worked cleanly.** `git worktree add` at the
  exact head sha, doing all verification there, then `git worktree remove
  --force` at the end, kept this review fully isolated from the shared
  `minchiate_tarot` checkout, which (as flagged in the task) was mid-flight on
  `test-T-MIN-015` for a concurrent worker both before and after my review —
  I never had to touch or even look closely at its state. This pattern (cite
  an exact worktree path, review there, tear down) is worth keeping as the
  default reviewer instruction for any task where the shared checkout can't be
  assumed idle.
- **`./bin/fleet render` picks up unrelated concurrent changes cleanly.**
  `TASKS.md` regeneration only reflected the T-MIN-014 status change even
  though other lanes (T-INTY-017, an Antigravity feedback file) had untracked
  files sitting in the coordinator working tree at the same time. No
  cross-contamination in the generated board.

## Repository-Level Feedback (minchiate_tarot)

T-MIN-014 was a pure citations/accuracy review: every STATUS block and QC
annotation in `Quarantine_Register_Outside_Set_Claims.md` claims a specific
claim ID in a specific committed study file, and the job was to catch a
citation that looks right but isn't fabricated or drifted.

**How the review was done:** built an isolated worktree at the exact head
sha, confirmed by `git diff --name-only 19c26db..925d124` that only the
register file changed (two commits: one substantive write-back, one pure
line-reflow — both register-only). Then, rather than trusting the register's
own prose, I opened every cited study file directly: the Fool study's §0 and
FOO-C007 row for CW-5; Air/Fire/Earth's AIR-C006/FIR-C009/FIR-C017 for CW-6
(specifically verifying Fire, not Air or Earth, owns the Death-edge
sub-disposition FIR-C017, and that Water/Earth/Air correctly cite rather than
re-disposition it); Libra/Gemini's LIB-C010/GEM-C010 for CW-7; and the
Trumpets study's TRO-C012 for CW-10. All four matched the register's claims
exactly — no paraphrase drift, no invented content.

I then spot-checked 14 of the 42 annotated QC rows (the task asked for at
least 8) across all four groups — Papi/Fool, elements, zodiac, and arie —
opening the cited study file for each and checking the annotation against the
actual claims-table row, not just against how plausible it sounded. Every one
checked out. One thing worth calling out: this register is dense enough
(42 rows, ~12 different study files cited) that a superficial "does this
citation format look right" pass would not have caught a subtle swap (e.g.
citing the wrong element file for a shared claim, or misattributing which
card "owns" a collective disposition like FIR-C017). The only way to actually
catch that class of error is opening the source file per citation, which is
what the task correctly demanded and what I did.

The QC-076 flagged conflict (Gemini types a `most-easily-confused` resolver
that the committed Love study's decline explicitly refuses to type) is real —
I opened both committed files and confirmed the Love study's exact declining
parenthetical and the Gemini study's exact typed edge, word for word against
what the register quotes. The worker handled this exactly per the task's
scope instruction: state both sides on the record, flag for human
adjudication, do not attempt to resolve it. This is good register discipline
— it would have been easy (and wrong) for the worker to quietly pick a side.

**Concern for next steps:** CW-11 (Courts) and CW-12 (Pips) remain
un-dispositioned, correctly left untouched by this task since no verified
study exists yet for either. Whoever picks up those studies should expect the
same register-writeback pattern to repeat, and the human adjudicator still
owes a decision on QC-076's Gemini/Love resolver-type conflict — that's now
the one open loose end in an otherwise fully reconciled quarantine register
for CW-1 through CW-10.
