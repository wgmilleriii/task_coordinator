# Feedback — Reviewer-F16 (claude-fable-5), 11 August 2026

Session: independent adversarial peer review of T-MIN-011 (arie batch, TRUMP-36..40,
author Worker-F11, branch test-T-MIN-011, head 8c69b9f). Verdict: PASS_WITH_CORRECTIONS;
task auto-advanced to DONE (human_review_required: false). A prior attempt at this review
was killed by a session limit before recording anything; this session started fresh.

## System-Level Feedback

1. **record-review skips HUMAN_REVIEW when human_review_required is false.** The README's
   lifecycle diagram presents HUMAN_REVIEW as a mandatory stage; the CLI jumps
   PEER_REVIEW -> DONE. That is presumably intended behavior for low-risk tasks, but the
   README should say so, and a research batch that establishes project canon for five
   cards is arguably not a low-risk task — the PM's audit decided `human_review_required:
   false` and nothing downstream can reinstate it. Consider letting a reviewer's verdict
   escalate to HUMAN_REVIEW even when the flag is false.
2. **The review template defaults to `verdict: FAIL`** with a REQUIRED_PLEASE_FILL
   finding. Good fail-safe design — a lazy reviewer who records without editing produces
   a FAIL, not a rubber-stamp PASS. Worth keeping and worth documenting as intentional.
3. **Reviewed SHA vs corrections SHA.** The review YAML records `reviewed_head_sha:
   8c69b9f`, but my corrections commit (a3993d7) is what actually sits at the branch tip
   the human will merge. There is no field for "resulting head after review corrections";
   I recorded it inside the finding text. A `corrections_head_sha` field would make the
   audit trail mechanical.
4. **Shared-checkout hazards are real.** On arrival the coordinator checkout sat on
   another agent's branch (feature/dewey-decimal-docs, dirty README.md), and the
   minchiate checkout sat on Worker-F12's test-T-MIN-012 — not on `test` as the boundary
   note assumed. The worktree-isolation instruction in my dispatch was the only thing
   that made a safe review possible. Recommend making "reviewers always work in a
   throwaway worktree pinned to the handoff SHA" a README-level rule, not a per-dispatch
   improvisation.
5. **The verification command is necessarily shallow.** It checks file existence and that
   the report names five cards and mentions failed-runs. Every substantive property
   (pricing, numbering, CW-10, disposition ownership) is only checkable by an adversarial
   reader. That is fine — but the task YAML's `scope` bullets were unusually good this
   time (each named trap was binding and checkable), and that is what made deep review
   tractable. PMs should keep writing scopes at that level.

## Repository-Level Feedback

**How the review was done.** I worked in an isolated worktree at 8c69b9f and re-derived
every check rather than trusting the author's self-verification report: recomputed all
five rank claims from the registry CSV (40 numbered trumps, sorts 58–97; 35/4, 36/3,
37/2, 38/1, 39/0 all correct, ascending ordinals consistent per finding F-1); swept all
five files for arie point amounts (none — the only amounts are the bounded Bernardi
transcription and the Trumpets file's convicted "10 points" quote) and confirmed the
outside-the-bound formulation is used instead of the zodiac nil-reading formula, against
Justice pilot L80/L92 which land exactly; swept for printed-number assertions (none);
read the Quarantine Register's CW-10 and QC-077..089/QC-107 rows in full and built the
one-owner disposition matrix (17 rows + CW-10 + GEM-C016, each owned exactly once,
siblings citing, "origins" never revived outside quoted withdrawals); verified
SYM-TRUMPET and all five Iconographic Matrix rows against the Stage 3 workbook via
openpyxl (quoted accurately; SYM-TRUMPET is the only arie symbol row); verified the
committed Gemini GEM-C016 offer and the Fire FIR-C020 decline against the new files'
answers; spot-checked nine committed-study "current text" line locators (all exact);
recomputed the comm -12 clone diffs against the archived failed drafts (5/0/0/0/2
boilerplate-only, matching the report); and re-ran the audited verification command
(PASS).

**What I found.** The batch is genuinely clean — the author's self-pass report is
accurate in every claim I recomputed, which was not a given after the fleet-stub
failure this batch replaces. The only defects were cosmetic: the Star file's STA-C015
claims row wrote the predecessor edge in the reverse arrow order from the committed
AIR-C011/Libra convention without the prose's disambiguating clause (fixed by adding
the clause), and a stray line-wrap in the Moon §5 checklist (fixed). Both in commit
a3993d7 on test-T-MIN-011.

**Lessons and concerns.** (1) The self-verification-report pattern (author records a
reproducible self-pass with locators, reviewer re-runs everything) worked well here; the
report's honesty disclosure ("this is a self-pass, not independent verification") is the
right norm. (2) The corpus's line-number locators ("current L305–314") are fragile —
they were all exact this time, but any future edit to a committed study silently breaks
them; the register's own maintenance note prefers section anchors, and studies should
too. (3) The report's §5 note is right that on merge the Quarantine Register rows
QC-077–089, QC-107, and CW-10 should gain disposition lines citing the new claim IDs —
that follow-up task should be scouted now so it is not forgotten. (4) Worker-F12's
Papi/Fool batch is in flight on test-T-MIN-012; its brief-driven pattern should get the
same adversarial review, and its Fool file must answer the Trumpets file's queued
Fool↔Trumpets question (TRO-C018/§4.5).

**Next steps for the human.** Merge test-T-MIN-011 (tip a3993d7) into the mainline;
commission the register-maintenance follow-up; decide whether research batches should
keep `human_review_required: false`.
