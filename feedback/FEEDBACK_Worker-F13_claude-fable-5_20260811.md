# Feedback — Worker-F13 (claude-fable-5), 11 August 2026, T-MIN-013

## System-Level Feedback

1. **The audited verification command was well-shaped for a design task.** The
   `find ... ! -name "Pilot1_*"` exclusion plus the two-stage grep for a comparison doc
   naming both full dossiers made the deliverable's hardest-to-fake property (a real
   comparison against the existing records, not a self-referential spec) mechanically
   checkable. One subtlety worth documenting: the comparison-doc grep scans
   `research/pilots/*.md` non-recursively, so the comparison must sit at the top of
   pilots/ while the light-tier cards may live in drafts/. That constraint is invisible
   in the task prose and only discoverable by reading the command — PMs should state
   path constraints in scope text too.
2. **Concurrent-agent working-tree churn is real and the staging discipline matters.**
   When I committed my submission, Reviewer-F17's T-MIN-012 review state (modified task
   yaml, review file, feedback file) was sitting in the coordinator tree. `git add -A`
   would have committed another agent's in-flight work. I staged only my three files;
   the pull --rebase then showed the reviewer had pushed their own state moments
   before. Worker-F11's earlier suggestion stands: `fleet submit` should print an
   explicit "stage only these files" list.
3. **The coordinator checkout sat on a third agent's feature branch**
   (`feature/dewey-decimal-docs`) at session start. The claim/submit lifecycle forces
   checkouts to main; "restore what you found" is the right rule but it means every
   worker must remember an out-of-band fact. `fleet claim` could record the pre-claim
   branch and `fleet submit` could offer to restore it.
4. **human_review_required tasks fit the lifecycle well.** Nothing in the CLI needed
   to change; the task simply parks at PEER_REVIEW→HUMAN_REVIEW. But TASKS.md does not
   visually distinguish "awaiting human decision by design" from "awaiting routine
   sign-off" — a `decision:` marker would help humans triage their queue.

## Repository-Level Feedback

**How the work was accomplished.** T-MIN-013 asked for a proposal, not a rollout: a
light-tier format spec for the 56 suit cards, two pilots written to it over cards that
already have full dossiers (an intentional redundancy test), and a comparison giving
the human a real decision. Before writing, I read the venture brief (§2 row 7 and the
§4 maturity mechanic are the format's actual requirements), both full pilot dossiers,
the Libra zodiac study as the heavyweight-discipline model, and recomputed the
rank-in-suit arithmetic from the registry (suits are contiguous 14-slot sort blocks:
Coins 43–56 so COINS-04=46→rank 4; Cups 29–42 so CUPS-12=40→rank 12, the Cavalier).
The only Bernardi material sourced for suit cards on the corpus is the pp. 5–6
cartiglia chapter (inverse round-suit order, Kings-only five points, one-card count
contribution) plus the Justice pilot's hedged "around XXVIII" verzicola boundary —
so the spec's scoring section is written as sourced-or-absent with the
bounded-transcription caveat mandatory.

Key design choices worth recording:

- **The spec cuts coverage, never honesty.** 60–120 lines/card; drops the source
  ledger, specimen grids, prompt/wiki packages, and gate tables; keeps the full
  grading legend (with [UNVERIFIED] as the explicit anti-invention valve), recomputed
  arithmetic, forbidden-imports list, confusion resolvers (SYM-SCALES precedent),
  explicit Verified/Draft/Stub maturity state, and a 6–12 row claims table.
- **Claim namespace:** `<SUIT2><RANK2>-C<NN>` (CO04-C01, CU12-C07) — disjoint from
  trump namespaces and from the two full pilots' mutually inconsistent legacy schemes,
  which the light cards cite as sources rather than reuse.
- **Citing-through is graded honestly.** A light card citing Bernardi through a
  dossier transcription carries the transcription's confidence and is marked
  [UNVERIFIED] where the source was not re-opened this session.
- **The redundancy test found no contradictions** but a real asymmetry: the pip card
  compressed with almost no loss (its full dossier is mostly scaffolding around one
  direct observation), while the court card holds its load-bearing pattern findings
  (hybrid anatomy non-universal, .35/.103 relatedness, gender caution) only by
  leaning on a full dossier that the other 15 courts will not have. The comparison
  therefore recommends a middle tier for the 16 courts — the human decides.
- **Verification workflow is proposed, not decided:** 100% mechanical pass
  (arithmetic + forbidden-term grep), adversarial verification sampled at 3 of 14 per
  suit with escalation on any failure, and a maturity mapping (light+unverified=Stub,
  light+verified=Draft, Verified reserved for post-IMG-001 crop-backed cards).

**Lessons learned.** (a) A "light" format is designed at the boundaries: deciding what
is FORBIDDEN and what must be absent-with-a-witness took more care than the section
skeleton. (b) The two full pilots use different claim-ID schemes for the same kind of
card — normalizing at the new tier rather than retrofitting the old records was the
cheap honest path. (c) The comparison doc is where the deliverable earns its keep;
without it the human would be choosing a format blind.

**Concerns / next steps for the human.** (1) Decide the format — specifically the
pip/court tier split; the comparison's recommendation is middle-tier courts, but
"full dossiers for the four Cavaliers only" is a named alternative. (2) The 54
remaining cards will cite witnesses directly (no dossier to cite through); the first
batch brief must carry the opened-witness list, and Bernardi's suit chapters would be
worth a dedicated transcription task before pip batches start. (3) The spec's
maturity mapping interacts with the wiki product — worth checking against the
venture's Verified/Draft/Stub display before rollout. (4) Nothing beyond the two
pilots was authored, per the task's explicit stop.
