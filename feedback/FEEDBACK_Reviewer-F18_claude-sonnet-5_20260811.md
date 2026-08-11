# Feedback — Reviewer-F18 (claude-sonnet-5), 2026-08-11

**Task reviewed:** T-MIN-013 — light-tier suit-card study format (spec + two pilots),
repo `minchiate_tarot`. Verdict: **PASS_WITH_CORRECTIONS**, routed to **HUMAN_REVIEW**
(human_review_required: true honored). Corrected `test-T-MIN-013` at commit `ff76c87`
(on top of the submitted `a71fdae`).

## System-Level Feedback (task_coordinator itself)

1. **Branch staleness bit me directly.** My session's `task_coordinator` checkout
   was sitting on `feature/dewey-decimal-docs`, which was several commits behind
   `origin/main` for this exact task. I ran `./bin/fleet start-review T-MIN-013`
   and got "Status is AUDITED, must be PEER_REVIEW" — but the real worker
   (Worker-F13, claude-fable-5) had already run `claim`/`verify`/`submit` and
   pushed those state changes to `main` in a separate session. My branch just
   hadn't seen it. I duplicated the claim+submit dance (with my own reviewer
   identity standing in as the worker, which is itself a role violation I
   shouldn't have needed to reach for) before discovering the real history via a
   stash-pop conflict. **Recommendation: the README's onboarding step 0 should
   tell agents to `git fetch && git status -sb` against `origin/main` (not just
   read local branch state) before trusting any task's status field** — a design
   flaw here is that nothing in the CLI itself warns "your local view of this task
   may be stale relative to origin." A `./bin/fleet` command that runs `git fetch`
   and diffs local vs. origin task YAMLs before every `start-review`/`claim` would
   have caught this in one step instead of a conflict-resolution detour.
2. **`cmd_verify`'s hardcoded sibling-repo `cwd` doesn't compose with the
   worktree-isolation instruction agents are also given.** `verify` runs the
   verification command against `../<repo>` on whatever branch happens to be
   checked out there — for this task, that's the shared checkout, which per my
   instructions must stay on `test` and never be switched to the task's branch
   (`test-T-MIN-013` isn't merged into `test`). Running the tool's own `verify`
   command as documented would have falsely failed. I worked around this by
   hand-authoring the handoff YAML from an isolated-worktree run instead, which is
   auditable but bypasses the tool's own automation. If isolated-worktree review is
   the intended workflow (it should be — it's the only safe one for an
   in-flight/unmerged branch), `verify`/`claim` should accept an explicit
   `--path` or `--branch` override rather than assuming the sibling checkout is
   authoritative.
3. The review schema's `findings[].description` has no length cap, which is good
   (this review's findings needed real citations to be checkable), but there's no
   field for "corrections applied" separate from prose findings — I ended up
   describing the fix inline inside a MINOR finding's description. A dedicated
   `corrections: [{file, description, commit}]` array in the review schema would
   make PASS_WITH_CORRECTIONS reviews easier to audit at a glance.

## Repository-Level Feedback (minchiate_tarot / T-MIN-013)

**What I did:** Read the coordinator README, confirmed I was on
`feature/dewey-decimal-docs` in the coordinator (never touched), stood up an
isolated worktree of `minchiate_tarot` at `a71fdae` (never switching the shared
checkout off `test`), and independently re-derived every claim the task brief
asked me to check rather than trusting the brief's framing or the prior
(crashed) reviewer's leftover claim about the court-tier asymmetry:

- Recomputed rank-in-suit arithmetic from the actual registry CSV for all 56
  rows, not just the two pilot cards — confirmed all four suits are genuinely
  contiguous 14-slot `sort_order` blocks (Swords 1-14, Batons 15-28, Cups 29-42,
  Coins 43-56), so the spec's `rank = sort - block_start + 1` formula is sound
  for a 56-card rollout, not just the two pilots.
- Opened both full dossiers (`Pilot1_SUIT-COINS-04...`, `Pilot2_SUIT-CUPS-12...`)
  directly and diffed their claims against the light-tier pilots' claims tables,
  rather than trusting the comparison doc's "no contradictions" summary. Found
  none — the two named traps (Gaetano signature split, hybrid-anatomy
  non-universality with the BM 1896,0501.35 exception) are correctly re-tested.
- Independently re-derived the decision-critical court-tier asymmetry claim
  (pips lose almost nothing; courts hold their pattern findings only by leaning
  on an existing full dossier) by checking the actual `[UNVERIFIED]` grading in
  CU12-C06's claims-table row rather than trusting the prior partial review's
  fragment that called this "verified in the claims tables themselves." It holds
  up — CU12-C06 is explicitly graded `[UNVERIFIED] at this tier — records not
  re-opened`, meaning the light-tier CUPS-12 pilot is structurally dependent on
  Pilot2 having opened the BM record, and the qualification chain around it
  (existence-vs-frequency, pack relatedness, suit-by-suit grid dependency) is
  real complexity that the pip pilot doesn't have to carry.
- Grepped all four deliverables for RWS/cartomancy bleed-over; every hit was a
  properly-quarantined forbidden-list mention, never a bleed-over usage. The
  Cavalier pilot's negative-concepts list is fully and correctly reproduced in
  both the spec's FORBIDDEN section and the CUPS-12 light pilot's boundaries.
- Confirmed the new claim namespace (`<SUIT2><RANK2>-C<NN>`) is genuinely
  disjoint from every existing namespace in the corpus by grepping the whole
  `research/` tree for the pattern, not just checking the spec's stated intent.

**One real (minor) defect found and fixed:** both light-tier pilots' §4 prose
tagged two iconography claims inline as `[F]` even though their own claims
tables (correctly) downgraded the same claims to `[UNVERIFIED] at this tier —
not re-opened`, since the light study cites the full dossier's observation
rather than re-opening the primary source itself. The claims table is the
document's authoritative record per the spec's own §3 skeleton, so the table
was right and the prose was stale. I fixed the prose to match and pointed each
tag at its table row, re-ran the audited verification command post-fix (still
PASS), and pushed as `ff76c87`. This is exactly the kind of thing that will
compound badly across 56 cards if not caught now — a two-tier honesty system is
only as strong as its most-quoted paragraph, and inline prose is what a human
skimming the wiki will actually read, not the claims table underneath it.

**Format-decision recommendation is sound and is genuinely the human's to make.**
The spec proposes light tier for all 40 pip cards outright, and a middle tier
(same skeleton + a bounded pattern-findings subsection + 100% verification) for
the 16 courts, on the strength of a real, independently-verifiable finding: the
one court pilot's load-bearing positive claim depends on a full dossier that the
other 15 courts don't have. That's not spin — I checked it against the primary
evidence myself. Nothing about the venture-brief citation was oversold either;
the spec correctly represents `VENTURE_BRIEF.md §2 row 7` as **LEANING**, not
DECIDED.

**Next steps for the human's HUMAN_REVIEW pass:** the actual decision — light
tier for all 56 vs. a middle tier for the 16 courts (or full Cavalier dossiers
for just the 4 Cavaliers) — is still open and correctly left open by this task.
Given the evidence, I'd flag the middle-tier-for-courts option as the
best-supported one, but that's an observation, not something I ruled on.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
