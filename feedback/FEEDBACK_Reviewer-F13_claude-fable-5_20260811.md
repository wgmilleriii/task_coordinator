# Feedback — Reviewer-F13 (claude-fable-5), 2026-08-11

Session: peer review of T-MIN-006 (verification-triage of the fleet sweep's ten
rulers/Fool/arie personality drafts). Verdict: PASS; task moved to DONE.

## System-Level Feedback

- **Review template severities are undiscoverable until they bite.** `fleet start-review`
  emits a stub with `severity: INFO` and no comment listing the legal enum. I wrote
  `LOW` findings and only learned the schema (`INFO/MINOR/MAJOR/CRITICAL`) from the
  `record-review` rejection. One comment line in the generated template
  (`# severity: INFO | MINOR | MAJOR | CRITICAL`) would save every reviewer a round-trip.
- **The template defaults `verdict: FAIL`.** Sensible as a fail-safe, but paired with
  `reviewed_at` being stamped at generation time (not at record time), a recorded review
  can carry a timestamp minutes earlier than the checks it describes. `record-review`
  should refresh `reviewed_at`.
- **PASS goes straight to DONE.** The README's lifecycle lists HUMAN_REVIEW between
  PEER_REVIEW and DONE, but `record-review` sent this PASS directly to DONE (the task
  had `human_review_required: false`). The README should say the HUMAN_REVIEW stage is
  conditional on that flag, or reviewers will think they skipped a gate.
- **Second-order reviews need a place for follow-up work.** My review found real
  out-of-scope debris (the GUIDEBOOK drafts, below) and the only channel for it is a
  MINOR finding on a task that is now closed. A `fleet propose` (reviewer files an OPEN
  task stub from inside a review) would keep such findings from evaporating.
- Positive: the `start-review`/`record-review` schema enforcement and the audited-sha /
  head-sha discipline made verifying provenance trivial. The R100 rename check plus the
  recorded verification command is a genuinely good losslessness contract.

## Repository-Level Feedback

**How the review was done.** I worked in a detached worktree at f5291eb, never touching
the shared checkout. Every triage claim I tested was recomputed from primary artifacts,
not from the report: registry rows dumped from `Stage5_Master_Card_Registry.csv` for all
ten cards (sorts 57–61, 93–97 confirmed; "sort 45" confirmed to belong to the Three of
Coins, proving TRUMP-04's header false); TRUMP-03's rank arithmetic re-derived (beats 2,
loses to 37, 56 suit cards, 97-row reconciliation); the Quarantine Register read at
source for QC-077–089, QC-107, CW-5, CW-10; the pilot's JUS-C006 (Bernardi bounded at
XXVII) and the committed Wheel study's formal withdrawal of "origins" (L305–306) read
directly; the verification command re-run (passes); the diff confirmed to touch only the
thirteen in-scope paths.

**What I found.** The triage is correct end to end. The 1-KEEP/9-REWRITE barbell holds
under adversarial re-reading: the Star draft asserts the registry's own `names_to_avoid`
text as [F]-secure fact; the Trumpets draft stamps "Quarantine Addressed" while ignoring
all five of its register rows and CW-10, and its "10 points" traces to nothing but the
failed brief; my independent acquittal-risk re-read (TRUMP-02) reached REWRITE on its
own — its errors concentrate in the identity layer, which is the entire point of a
Low-naming-confidence card. Nothing was wrongly condemned; nothing was wrongly kept.
The two replacement briefs are the strongest artifacts of the batch: they quote the
withdrawn coinages, bound Bernardi at XXVII, and grade every pricing amount
[UNVERIFIED].

**Concern / next steps.** (1) The same fleet sweep left ten `GUIDEBOOK_TRUMP-*.md`
drafts in `research/pilots/drafts/` repeating the convicted defects verbatim ("10
points", rank-40-as-fact, the enacted final-sounding frame). They are now the last
uncaught carriers of the superseded brief's fabrications — a Scout should open a
GUIDEBOOK triage task before anything cites them. (2) The rewrite batches should be
scoped as tasks pointing at ARIE_BATCH_BRIEF and PAPI_FOOL_BATCH_BRIEF, with the
TRUMP-03 correction pass (five itemized fixes) riding in the Papi batch. (3) On
acceptance of the rewrites, the register maintenance the report queues (dispositions
for QC-043–050, QC-053/054, QC-077–089, CW-5, CW-10) needs an owner, one file per
collective row per the element report's M-2 rule.
