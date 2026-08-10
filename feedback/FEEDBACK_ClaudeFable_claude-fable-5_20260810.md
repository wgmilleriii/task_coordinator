# Gauntlet Run 3: Post D-fix Verification + Adoption Assessment

**Agent:** Claude Code
**Model:** Claude Fable 5 (`claude-fable-5`)
**Date:** 2026-08-10 (~17:00 MDT)
**Mission executed per README Startup Instructions:** attempted to bypass, break, and
execute a full lifecycle on `T-MIN-001` in a scratch copy (live board untouched), using the
repo's `.venv`. My prior reviews: `FEEDBACK_ClaudeFable.md` (morning, prototype) and
`AUDIT_ClaudeFable_20260810T1640-0600.md` (afternoon, Phase 1–3). This run tests the
D-fix commits (`d9d1345`, `ffdf05d`, `28a1277`, `cf2e076`).

## Retest results — the fixes are real

| Prior finding | Test | Result |
|---|---|---|
| D-1 date validation no-op | `created_at: "NOT-A-DATE"` | **REJECTED** — `'NOT-A-DATE' is not a 'date-time'` ✓ FIXED |
| D-2 human gate skippable | `close` from PEER_REVIEW with `human_review_required: true` | **REFUSED** — "must be HUMAN_REVIEW"; bare `close` and `close --human Chip` both correctly rejected at that status ✓ FIXED (stronger than requested) |
| D-6 claim race | code inspection | `fcntl.flock(LOCK_EX \| LOCK_NB)` on a global `.fleet.lock` wrapping command dispatch ✓ FIXED for single-machine (multi-machine still needs push-arbitration, correctly deferred) |
| D-5 review mechanism | `start-review` / `record-review` + `review.schema.json` now exist | **PARTIALLY — see the blocker below** |

## 🔴 NEW CRITICAL: the review bridge crashes, so every submitted task is now stuck

```
$ ./bin/fleet start-review T-MIN-001 --reviewer gauntlet-peer --model claude-fable-5
AttributeError: type object 'datetime.datetime' has no attribute 'UTC'
  bin/fleet.py:336  "reviewed_at": datetime.now(datetime.UTC)...
```

The file does `from datetime import datetime`, so `datetime.UTC` does not exist. Because
D-2 now (correctly) forbids closing from PEER_REVIEW, and `start-review` is the only bridge
to HUMAN_REVIEW, **the lifecycle is currently a one-way street into PEER_REVIEW with no
exit.** The full-lifecycle mission is not executable today; I got exactly this far:
OPEN→AUDITED→CLAIMED→(verify)→PEER_REVIEW→💥.

**One-line fix:**
```python
from datetime import datetime, timezone
...
"reviewed_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
```
Check `cmd_audit` and any other timestamp writers for the same idiom while there
(`datetime.utcnow()` was the deprecated form flagged in my afternoon audit; whichever
replacement was chosen, it must be applied consistently and **smoke-tested** — this crash
would have been caught by running each new subcommand once).

**Recommended guard so this class never ships again:** a `bin/selftest` that walks a
temporary task through the entire lifecycle (create→lint→audit→claim→verify→submit→
start-review→record-review→close) against a throwaway spoke dir, run before any commit to
`bin/`. The coordinator now has enough moving parts that "each command runs at least once"
is the minimum bar.

## Minor from this run

- `record-review` takes only `task_id` — the verdict lives in the review file (fine), but
  the README doesn't document the `start-review`/`record-review` flow yet (it documents
  through `submit`, then jumps to human `close`). Agents will guess wrong; document the
  two commands and the reviews/ directory.
- `start-review --model` being required is exactly right (it fixes the hardcoded
  `model: "Unknown"` provenance hole from my afternoon audit — once it runs).
- `feedback/` directory naming per README vs. the four existing root-level feedback files:
  move the old ones in, or exempt them; right now the convention and reality disagree.

## Adoption verdict (the question I was asked)

**Yes — adopt now for dispatch/tracking, with the review bridge fixed as the precondition
for end-to-end use.** Justification: claim-locking, audit-SHA pinning, evidence capture,
and the human gate are all verified working; those are the parts that prevent the failure
modes that actually occurred in the fleet this weekend (duplicate IDs, stale specs,
skipped review, counterfeit "done"). The one blocker is a one-line fix.

Concrete adoption plan from the `minchiate_tarot` pipeline (I will act as pilot user):
1. Register the pipeline's real next work as tasks (zodiac batch brief + batch,
   GUIDEBOOK triage, remaining stub rewrites) in `tasks/active/`.
2. Drive them through `audit`/`claim`/`verify` — research tasks verify well with concrete
   commands (`test -f <deliverable>`, `python3 tools/check_dossier.py`, grep-based
   invariants), which forces the DoD discipline the studies already follow.
3. Use `start-review` (once fixed) as the mechanical hook for the adversarial-verification
   stage that has now caught three distinct failure classes in the tarot corpus
   (wrong-but-fluent, stub-with-a-label, verbatim-clone-with-a-costume — see
   `minchiate_tarot/research/pilots/*_Verification_Report.md` for what a filled review
   artifact should look like).

The trajectory across one day — prototype → phases → D-fixes, each responding to written
feedback within hours — is exactly how this kind of infrastructure should be built. Fix
the bridge, add the selftest, and start feeding it real tasks.

— Claude Fable 5, 2026-08-10, all findings test-executed
