# Feedback — Reviewer-F14 (claude-fable-5), 2026-08-11

Session: peer review of T-MIN-007 (guidebook triage). Verdict PASS; task moved to
HUMAN_REVIEW.

## System-Level Feedback

- The `start-review` stub defaults `verdict: FAIL` with a placeholder finding. Good
  fail-safe design: an unedited stub cannot accidentally pass a task. Keep this.
- `record-review` gave no schema pushback on my finding severities (INFO/MINOR). If
  severities are meant to be a controlled set, the schema should enforce them; if not,
  document the expected values in the stub comment.
- The review flow has no field for what the reviewer actually re-executed (commands,
  worktree sha). I put it in findings prose, but a structured `evidence` list on the
  review YAML — parallel to the worker handoff's evidence — would make reviews
  auditable in the same way worker submissions are.
- The isolated-worktree instruction in my dispatch was essential: the shared
  minchiate checkout was on another worker's branch (test-T-MIN-009) the whole time.
  The coordinator README should codify "reviewers verify in a detached worktree at the
  handoff head_sha, never in the shared checkout" as standard reviewer protocol.
- Cross-branch dependencies are invisible to the board. T-MIN-007's spec references
  briefs that exist only on unmerged branch test-T-MIN-006. A task field like
  `depends_on_branch:` (or making merges themselves tasks) would surface this.

## Repository-Level Feedback

How the review was done: I added a worktree at head 58f3a6e and re-derived the
report's decisive claims from primary artifacts rather than re-reading its prose.
For the KEEP-side (wrongful acquittal) I checked GB-08 against the committed Justice
study: the scoring and naming claims match the JUS-C005/C006 witnesses, and the two
out-of-vocabulary "Subordinate" edges are real, really mistyped (committed Chariot
type is rival, rec 8; the Old Man edge was rejected at QC-023), and really queued as
corrections in report Sec 5 — the report claims nothing it did not do. I also
re-verified GB-05's four edges type-exact against the committed Love study. For the
FAIL-side (wrongful conviction) I recomputed GB-01 from the registry — Trump I at
sort 58 beats all 56 suit cards, so "cannot win a fight against anyone" is flatly
false — and GB-36 against the registry names_to_avoid field and the committed Old Man
study's explicit "no typed relationship" over the Star. Both convictions hold. The
report's central empirical claim — the 3/8 KEEP/FAIL split tracks upstream source
verification status exactly — survived every probe.

The GUIDEBOOK_FORMAT_SPEC is the piece the human should read closely. Its five gates
(existence, no uncorpused amounts, controlled vocabulary, confidence disclosure, no
self-audit logs) are all present and enforceable, and the no-self-audit rule is the
single highest-value change: all eight failed guidebooks carried self-authored
"PASSED" audit logs, several certifying the very violation. Three minor items for the
human gate, none blocking: (1) spec Sec 4.4 says TRUMP-01 naming is Low where the
registry detail says Low-Moderate; (2) spec Sec 6 gates regeneration on batch briefs
that live only on unmerged branch test-T-MIN-006; (3) the three keepers still carry
their own audit logs and the queued corrections do not yet include deleting them.

Direction: the project now has a defensible two-layer structure — adversarially
verified personality studies feeding a gated product layer. Next steps in order:
merge test-T-MIN-006 so the regeneration briefs land; run the queued correction pass
on the three keeper guidebooks (including audit-log removal); then regenerate the
eight archived entries only as their personality rewrites clear verification.
