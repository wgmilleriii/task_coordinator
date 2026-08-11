# Session Feedback: Reviewer-F17 (claude-fable-5), 2026-08-11

Role: independent adversarial peer review of T-MIN-012 (Papi/Fool batch, minchiate_tarot).
Verdict: **PASS_WITH_CORRECTIONS** (one MINOR report-only fix, applied and pushed as 14a0fff).

## System-Level Feedback

- The `start-review` template pre-fills `reviewed_head_sha` with the submitted sha and a
  `verdict: FAIL` placeholder. That is a good fail-safe default, but when a reviewer pushes a
  correction commit to the task branch the schema offers no field for a
  `corrections_head_sha`. I recorded 14a0fff inside a finding row; a dedicated optional field
  would make the audit trail mechanical instead of prose.
- `record-review` moved the task straight to DONE because `human_review_required: false`.
  Correct per the lifecycle, but worth noting: for research-artifact tasks whose "merge" step
  is a git branch merge into the spoke's `test`, DONE fires before anyone has actually merged
  `test-T-MIN-012`. The board now says DONE while the branch sits unmerged and `test` has
  advanced (a3993d7). A MERGED terminal state, or a merge-check in `record-review`, would
  close the gap.
- The base-advance problem was handled well by prompt convention this time (the dispatcher
  told me not to fail the deferrals), but nothing in the task YAML records "base moved to
  a3993d7 mid-flight; reconciliation queued." A `followups:` list in the task schema would let
  the queued arie reconciliation be a first-class task seed instead of living in a review
  finding.
- Worktree isolation (`git worktree add <scratchpad> <sha>`) worked cleanly for reviewing
  while the shared checkout stayed on `test`; recommend it as standard reviewer procedure in
  the README.

## Repository-Level Feedback (minchiate_tarot)

**How the review was accomplished.** I recomputed rather than re-read: all five rank claims
were rebuilt from `Stage5_Master_Card_Registry.csv` sort orders (Fool 57 bookkeeping,
Ganellino 58 beating 0 trumps, Rulers 59/60/61; every n+1+m=40 sum and the 56-suit-card count
checked); every witness anchor was fetched at its locator (Justice pilot L80 = JUS-C006
five-points-to-I / three-to-II-V bounded at XXVII; L92 = verzicola examples I-V; JUS-C005/C007;
DEA-C004; Stage 2 Foundation L95 for the amount-free Minucci list; the candidate corpus's
numeral list, which excludes I/II/III and contains IIII). The five TRUMP-03 corrections were
verified item-by-item against the triage report's KEEP section; the CW-5/QC-043..050 matrix
was checked for one-owner-per-row, and three QC rulings were spot-checked against committed
files' CURRENT text (QC-052 "worth more" in Love, QC-049's corrected "opposite" in the Devil
second pass, QC-044's bookkeeping/gloss discipline in the Wheel) - all three landed. Clone
diffs against the archived failed-runs counterparts found only legend/heading boilerplate
shared. The audited verification command re-ran PASS in the worktree.

**Quality of the work under review.** This is the strongest batch I have seen in this lane.
The Fool study's split of CW-5 into a substantiated structural half and a refused mechanical
half is exactly the adversarial move the register system exists to force, and the author's own
in-wave catches (the QC-052 register-drift, the 830161001 reasoning repair) were real. The
single defect in ~1,470 inserted lines was a claim-ID slip in the report's edge matrix.

**Concerns / next steps.**
1. Merge `test-T-MIN-012` into `test` and run the queued arie reconciliation: all four
   ruler-side files plus the Fool carry explicit "T-MIN-011 in flight, deferred" notes, and
   the arie batch is now merged (a3993d7). The Fool<->Trumpets pairing is the named hot spot.
2. Register maintenance is queued, not done: disposition lines for QC-043..054 and the stale
   QC-049 "immune party" heading in `Quarantine_Register_Outside_Set_Claims.md`.
3. The corpus-wide dependence on the Justice pilot's Bernardi transcription (bounded at
   XXVII) is now load-bearing for five more files; a direct RULE-1790 scan pass would
   de-risk the whole personality corpus at once, and the Fool's rules (Bernardi beyond the
   transcribed pages, Dresden 1798, Brunetti 1747) are the highest-value single fetch.
