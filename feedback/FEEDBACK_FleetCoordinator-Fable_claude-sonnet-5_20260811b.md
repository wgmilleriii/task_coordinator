# Feedback — Fleet Coordinator (session 2, 11 Aug 2026, Fable 5 → Sonnet 5 mid-run)

Required end-of-session feedback per README §5. Second coordinator session of the day:
Scout-F2, PM-F5, Workers F11/F12/F13, Reviewers F16/F17/F18 dispatched. Model switched
from claude-fable-5 to claude-sonnet-5 mid-run (usage-credit exhaustion on two agents);
coordination quality held constant across the switch.

## System-Level Feedback

1. **Two agents were killed mid-task by provider-side limits** (session limit, then
   usage credits) — both while holding a worktree, neither having recorded any
   partial state via the CLI. Recovery was cheap exactly because the CLI's
   claim/verify/submit/review actions are atomic and only committed on success: a
   dead agent before its first `fleet` write leaves zero mess. Recommend documenting
   this as the intended safety property — "subagents die cheaply if killed before
   their first CLI mutation" — so operators don't over-worry about mid-task kills.
2. **Stale-checkout illusion:** Reviewer-F18's second attempt found its local
   `task_coordinator` clone diverged from `origin/main` and nearly duplicated
   Worker-F13's already-completed claim/verify/submit before a stash-pop conflict
   surfaced it. The coordinator has no cheap "is this task already actively owned by
   a live process" signal beyond re-pulling before every action — recommend a
   README reminder to `git fetch && git log origin/main -1` before assuming local
   state is current, not just before commits.
3. **Repeated this session:** the `--model` flag inconsistency (rejected by `claim`,
   required by `verify`) hit multiple agents again — still unfixed, now filed four
   times across two sessions.
4. **Coordinator checkout drift is now routine, not exceptional** — every agent this
   session found the shared checkout on `feature/dewey-decimal-docs` (another
   agent's in-flight work) and had to checkout-main-commit-restore. The pattern
   held every time, but it's fragile by hand; worktree-per-agent for the
   coordinator's own repo (not just the spoke repos) would remove the whole class.

## Repository-Level Feedback (minchiate_tarot)

**How the work was accomplished.** This session authored and verified the entire
remaining trump sequence: the five arie (T-MIN-011: Star/Moon/Sun/World/Trumpets,
0 pricing violations, CW-10 dispositioned not enacted, one-owner-per-register-row
matrix clean) and the Papi/Fool batch (T-MIN-012: TRUMP-01/02/04 fresh + TRUMP-03's
five triage corrections applied in place, Fool's CW-5 dispositioned by splitting
structural-fact-kept from mechanical-immunity-refused). Both went through independent
adversarial review before merging to `test`. **Canon now carries 42 of 97 cards
verified — the complete 41-trump sequence plus the Fool** — up from 20 at the start
of 10 Aug and 32 after the zodiac batch alone.

In parallel, a light-tier suit-card format was designed and reviewed (T-MIN-013): the
redundancy test against the two existing full pilot dossiers found the compression
asymptomatic for pip cards but decision-relevant for courts — the Cavalier pilot's one
load-bearing finding is structurally dependent on a full-dossier-only source opening,
which the light tier can't reproduce standalone. That asymmetry was verified
independently twice (once by the original reviewer, re-derived from primary evidence
by the replacement after a kill), not merely asserted by the author.

**Lessons.** (a) The "answer committed edges on the record, defer to unmerged
branches explicitly" discipline (used across T-MIN-011/012, which were authored
concurrently on separate branches) worked cleanly — both workers left grep-able
deferral notes exactly where a same-batch reconciliation would have been tempting,
and no cross-branch edge was silently dropped. (b) Root-causing failures to their
originating fleet brief (now true for both convicted batches from 10 Aug) means the
replacement briefs are the actual deliverable protecting future authoring — worth
treating brief-writing as its own auditable artifact, not throwaway scaffolding.

**Concerns / open work.**
1. Three tasks await your ruling in HUMAN_REVIEW: T-MIN-001 (grid app), T-MIN-007
   (guidebook format spec), T-MIN-013 (suit-card format — the court-tier question is
   the real decision). None merged to `test`; branches held.
2. T-MIN-008 remains OPEN, blocked on acquiring the Bernardi 1790 scan
   (archive.org bub_gb_4_rdG3SVa48C) — now higher-leverage than before, since every
   arie/Fool study's *verzicola*-boundary language is hedged pending it.
3. Queued follow-ups from this session's reviews: arie-edge reconciliation against
   the now-merged T-MIN-011 (flagged by T-MIN-012's deferral notes); Quarantine
   Register maintenance (QC-077..089, CW-10, QC-043..054 disposition lines never
   written back into the register itself, plus one stale QC-049 heading);
   register-maintenance is accumulating across three separate review passes now and
   deserves its own task rather than more deferred notes.
4. T-MIN-002/003 (identification write path, apply 93 renames) remain AUDITED and
   unclaimed — the oldest unclaimed work on the board.

**Recommended next steps.** Human rulings on the three HUMAN_REVIEW tasks first
(they gate merges and the venture plan). Then: a Scout round for (a) the Quarantine
Register maintenance task, (b) T-MIN-002/003 pickup, (c) once T-MIN-008 unblocks,
retiring the *verzicola* hedge across all thirteen affected files.
