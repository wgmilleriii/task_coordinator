# Feedback — Fleet Coordinator (Claude Fable 5), session of 11 Aug 2026

Required end-of-session feedback per README §5. Coordinator session: nine subagents
dispatched (PM-F2/F3, Workers F10/F6/F7/F9, Reviewers F11/F13/F14/F15 — F11 counted
with the 10 Aug tail), zero branch collisions, zero lifecycle violations.

## System-Level Feedback

1. **The lifecycle worked end-to-end, repeatedly.** Six tasks driven through
   claim→verify→submit→review this session (T-MIN-005/006/007/009/010 plus T-MIN-001's
   review earlier): every handoff's evidence reproduced independently, every reviewer
   worked in an isolated git worktree, every checkout restored. The worktree-per-agent
   convention (adopted informally by all my dispatch briefs) eliminated the branch-churn
   failures of 10 Aug — recommend making it a README requirement, not folklore.
2. **CLI flag inconsistency:** `fleet claim` REJECTS `--model` while `fleet verify`
   REQUIRES it (hit by three workers). Unify.
3. **`fleet lint` fails globally on another repo's tasks** (thirteen T-INTY-* schema
   violations at time of writing). Lint needs a per-lane mode, or the boundary rule is
   unenforceable in practice: agents cannot tell "my YAML is broken" from "someone
   else's is."
4. **`fleet onboard` janitor timestamp bug:** ".fleet_context.md" reports ~496,238
   hours since last doc update — an epoch-default. Cosmetic but erodes trust in the
   janitor gate.
5. **PM audit quality matters more than any other control.** PM-F3 replaced a vacuous
   always-pass verification command with a fail-first one and dry-ran it red before
   auditing; that single practice is why T-MIN-009's completion is meaningful.
   Recommend README language: a PM must demonstrate the verification command FAILS
   against the pre-work tree before auditing.
6. Previously filed, still open: archive-on-DONE (DONE tasks linger in tasks/active/),
   id-uniqueness guard, stale review/handoff cross-checks (the T-MIN-004 collision).

## Repository-Level Feedback (minchiate_tarot)

**How the work was accomplished.** The session ran the project's adversarial-
verification method at fleet scale. The zodiac batch (12 studies authored 10 Aug by
this coordinator's parent session) was independently verified (T-MIN-005: 0 FAIL,
9 PASS_WITH_CORRECTIONS — including one major at Gemini where the author had smoothed
over a genuine brief-vs-committed-record conflict), then its verification was itself
reviewed. The remaining fleet-sweep output was triaged: personality drafts (T-MIN-006:
1 KEEP / 9 REWRITE, root-caused to FINAL_TRUMPS_BATCH_BRIEF.md mandating unsourced
pricing and quarantined framings) and guidebooks (T-MIN-007: 3 KEEP / 8 FAIL — the
bins tracked upstream verification status exactly; a format spec now exists with an
existence gate). Finally the zodiac studies' classical locators were resolved against
opened editions (T-MIN-009: Tetrabiblos I.13/I.17, Aratus by line via Scaife, Isidore
III.71, Sacrobosco cap. II, Hyginus 2.22; two claims honestly downgraded), and a
citations reviewer reopened the sources independently. Canon (`test`) advanced to
f8bb1b8 with only verified material.

**Lessons.** (a) Derivative documents inherit their sources' health exactly — the
guidebook split proves popularization is safe only behind a verification gate.
(b) Fleet briefs are a single point of failure: two of two convicted batches trace to
brief-mandated defects; briefs deserve the same adversarial pass as studies.
(c) Same-model verification found real defects, but the model-diversity caveat stands
— disclosed in every report header.

**Concerns.** The 56 suit cards remain untouched; the venture plan (teamwork/
VENTURE_BRIEF.md) needs them at a lighter tier — that format does not exist yet.
Bernardi's high-trump schedule (beyond XXVII) is the single evidence item blocking
honest Fool/arie pricing, and no agent can fetch it (T-MIN-008 blocked on source
acquisition).

**Recommended next steps (in order).**
1. Human: rule on T-MIN-007 (guidebook format spec) — `fleet close T-MIN-007`; and
   T-MIN-001 likewise.
2. Human: acquire the Bernardi 1790 scan (archive.org bub_gb_4_rdG3SVa48C) into the
   repo → unblocks T-MIN-008, which firms up thirteen studies' verzicola hedges.
3. Scout: open tasks for the two rewrite batches (arie ×5, Papi/Fool ×3+Fool) against
   the new ARIE_BATCH_BRIEF and PAPI_FOOL_BATCH_BRIEF, and a light-tier suit-card
   study format task (venture dependency).
4. Merge test-T-MIN-007's deliverables only after the human's format ruling.
