# Feedback — Claude Fable 5, 10 Aug 2026 ~18:30 MDT (second note)

Filed after resuming coordination following the evening pause. Supplements my earlier
feedback/audit files; per convention, nothing existing was modified.

## Defect found live: task-ID collision on T-MIN-004

**What happened.** My session drove T-MIN-004 (zodiac batch brief) through
claim → verify → submit → start-review → record-review to **DONE** (commit `9f4b5a5`,
review verdict PASS). During the evening's concurrent-agent branch churn, main's
history was rewritten and that commit became unreachable; the DONE yaml fell out of
tracking. A later Scout/PM pass (PM-1) then minted a **new, unrelated task** ("Fix grid
caption dropping card value") reusing the id `T-MIN-004`, while the tracked
`reviews/T-MIN-004_review.yaml` (verdict: PASS) and `handoffs/T-MIN-004_handoff.yaml`
still referred to the *original* task. Had anyone exercised the review path on the new
T-MIN-004, it could have inherited a stale PASS on work never reviewed.

**Remediation applied (this session).** The caption task is renumbered to
**T-MIN-010** (it was unclaimed; only the id and filename changed). The original
T-MIN-004 is restored from `9f4b5a5` in its DONE state and moved to
`tasks/archive/T-MIN-004.yaml`. PM-1's uncommitted T-MIN-002/003 audits are committed.
Board re-linted and re-rendered clean under the post-hardening schema.

## Root causes worth fixing in the CLI

1. **`record-review` leaves DONE tasks in `tasks/active/`.** Archive should be part of
   the DONE transition (or a `fleet archive` command); a retired id that lingers in
   active is what made the collision invisible.
2. **No id-uniqueness guard across active + archive + reviews + handoffs.** Task
   creation (including by hand) should fail if the id appears anywhere in the
   repository's history of record. A `fleet create` that allocates the next free id
   would remove the failure mode entirely.
3. **Stale review/handoff files are not cross-checked.** `start-review` and `submit`
   should refuse to proceed when an existing review/handoff file for that id contains
   a different task title or a terminal verdict.
4. **Shared-checkout branch churn** (also reported in my earlier note and by others):
   three agents switched branches under each other in both repos today; commits landed
   on wrong branches three times, and one history rewrite orphaned a lifecycle commit.
   Worktree-per-agent (or the CLI committing through a dedicated plumbing path pinned
   to a branch) is now the highest-leverage hardening item on my list.

## Praise

The strict schema + lint caught nothing false-positive throughout; `fleet lint`
validating reviews and handoffs (post-hardening) is exactly the right direction —
finding my restored archive yaml and the renumbered task valid on first try made the
remediation cheap.
