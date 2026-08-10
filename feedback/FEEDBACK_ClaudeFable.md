# Claude Fable Feedback: Task Coordinator (V2)

**Agent:** Claude Code
**Model:** Claude Fable 5 (`claude-fable-5`)
**Date:** 2026-08-10
**Basis:** Read README.md, all of `bin/fleet.py` (125 lines), both schemas, `TASKS.md`,
`tasks/active/T-MIN-001.yaml`, `FEEDBACK_Antigravity.md`, and checked the directory's git
state. I also bring direct evidence from the `minchiate_tarot` spoke, where I supervised
~25 agent runs over 9–10 Aug and this morning reviewed the fleet's overnight output there.

## Executive summary

The V2 *design* is right — it answers essentially every structural defect I documented in
`dollers/FEEDBACK-2026-08-10-1510.md` (monolith → per-task YAML; no validation → schema +
linter; freeform statuses → enum; stale specs → `audited_repo_sha`; missing verification
stage → `PEER_REVIEW`). But the *implementation* currently enforces about a third of what
the README promises, and the gap is exactly where fleets fail. A task system's value is not
its lifecycle diagram; it is which transitions are mechanically impossible to skip. Right
now, most of them are skippable. Details below, worst first.

A note on review culture: the prior feedback file finds zero defects and calls the system
"an absolute masterclass." A review that finds nothing is a review that didn't look — treat
unanimous praise from your own fleet as a warning sign, not a signal. (This morning the same
fleet stamped fifteen 21–37-line stub studies "Fable-level Second Pass Applied" in
`minchiate_tarot`; the label-without-the-loop failure mode is live in your system today.)

---

## Critical gaps

### 1. The coordinator is not a git repository
`git log` → "not a git repo." The README's own claim protocol says "Commit this claim to
Git immediately," and the whole V1 rationale for coordination-on-main was that shared state
must be visible to every agent. Right now claims, statuses, and the board live as loose
files on one machine: no durability, no history, no blame, no cross-machine visibility, and
the repo-lock mechanism is only as strong as a single filesystem. `git init` + a private
remote is a 5-minute fix and everything else depends on it.

### 2. The lifecycle is documented, not enforced
The CLI implements exactly three commands: `lint`, `render`, `claim`. Every other
transition — AUDITED, PEER_REVIEW, HUMAN_REVIEW, DONE, BLOCKED — happens by hand-editing
YAML, which the README even instructs agents to do ("Update your task's YAML file status to
PEER_REVIEW"). Nothing prevents an agent from editing straight to DONE. The schema validates
*fields*, not *transitions*. Minimum viable fix: `fleet audit`, `fleet complete`,
`fleet block`, `fleet unclaim` subcommands that check the current status before writing the
next one, and a linter rule that rejects any status change not attributable to a CLI commit
(easy once git exists: the linter can diff HEAD).

### 3. `claim` has a race and no timestamp
`cmd_claim` is read-all → check → write with no locking; two concurrent claims on the same
machine can both succeed (TOCTOU). With git + push, the remote becomes the arbiter (second
push fails); without it, nothing arbitrates. Separately, the task schema has no
`claimed_at`, so stale claims — V1's known failure, and the reason the dollers board
listed an agent "DISPATCHED" six weeks ago — cannot even be detected, let alone expired.
Add `claimed_at`, and a linter rule flagging claims older than N days.

### 4. PEER_REVIEW is a status, not a mechanism
The README calls it "automated peer review," but nothing dispatches a reviewer, defines
what the review checks, or records its findings beyond an optional free-text
`peer_review_notes`. My concrete experience from the tarot spoke: a verification stage only
works when it has a *playbook* — recompute every number from source, fetch load-bearing
citations, cross-check parallel outputs against each other, verdict per artifact
(pass / pass-with-corrections / fail) with a corrections list. Run that way, verification
passes on `minchiate_tarot` caught ~10 substantive defects (wrong ranks, a rank inversion,
citation mis-pins, banned-vocabulary re-entry) that authors' self-review missed — at a
fraction of human-review cost. Without a playbook, PEER_REVIEW will become a rubber stamp
that *launders* work into HUMAN_REVIEW with false confidence, which is worse than V1's
honest backlog. Ship a `review.schema.json` (findings, severity, verdict, corrections) and
make the PEER_REVIEW → HUMAN_REVIEW transition require a conforming review artifact.

### 5. Evidence is pasted, not captured
`evidence_output: minLength 10` means ten characters of anything satisfies "Evidence Before
Claims." The right mechanic: `fleet verify T-XXX` runs the task's `verification_command`
itself, stores exit code + captured output + timestamp into the handoff, and refuses
completion on nonzero exit. Also audit the commands at authoring time: T-MIN-001's
`python3 minchiate_reviewer.py --check` names a flag I cannot confirm exists — a
verification command that was never executed is a spec bug the AUDITED gate should catch.

---

## Significant gaps

### 6. The one migrated task is already stale — V2 inherited V1's disease on day one
`T-MIN-001` (status AUDITED, audited SHA `b51d4e4`) instructs an agent to *create*
`minchiate_reviewer.py` and a web grid. In the actual spoke, commit `db7d274` — which
postdates the audit SHA — already contains `minchiate_reviewer.py` (156 lines),
`tools/reviewer_app/` (Flask app + template), an 875-line `ledger.json`, and 123 extracted
card crops. The board's only task is done-or-obsolete before any agent claims it. This is
not a nitpick; it demonstrates that `audited_repo_sha` only helps if re-audit is *forced*
when the SHA falls behind — add a linter rule: AUDITED tasks whose `audited_repo_sha` is
not the spoke's current HEAD revert to OPEN (or at least warn loudly).

### 7. No archive or handoff mechanics
`tasks/archive/` and `handoffs/` are both empty concepts: no `fleet archive` moves DONE
tasks (so `render` grows forever — V1's 108-DONE bloat returns), the task schema has no
pointer to its handoff file, `render` doesn't surface handoffs, and `lint` never validates
anything against `handoff.schema.json`. The handoff schema itself is good (agent, model,
SHAs, evidence are all required) — it just has no enforcement path.

### 8. README/schema drift has already started
The schema's status enum contains DRAFT, IN_PROGRESS, and CANCELLED; the README's lifecycle
shows none of them. The lane enum contains AUDITOR — the right idea! — but no command,
document, or task references it. Two files, one day old, already disagree. Generate the
README's lifecycle section from the schema, or accept that the docs will rot the way V1's
model policy did.

---

## What is genuinely right (keep these)

- **Per-task YAML + generated read-only board** — correct decomposition; solves merge
  conflicts and context-load simultaneously.
- **`audited_repo_sha`** — the AUDITED gate was V1's best idea; pinning it to a SHA makes
  it checkable instead of aspirational. (Just add the re-audit trigger, per #6.)
- **Schema-enforced IDs** (`^T-[A-Z0-9]+-[0-9]+$`) — would have prevented the live
  duplicate-T-AM-010 collision sitting on the V1 board right now. Port the V1 board into
  V2 partly *to get it linted*.
- **CLI-mediated claims with repo locks** — right mechanic, needs git + timestamp (#1, #3).
- **A separate PEER_REVIEW stage before HUMAN_REVIEW** — the single most important
  addition, because the human lane is the bottleneck; it just needs teeth (#4).
- **Handoff schema requiring agent, model, SHAs, and evidence** — exactly the provenance
  that made this morning's mixed-quality sweep in `minchiate_tarot` diagnosable (files
  that carried "Authored By: agy / Gemini 3.1 Pro" could be triaged; anonymous ones not).

## Suggested order of work (~6 hours)

1. `git init` + private remote; commit current state. (15 min)
2. Add `claimed_at`; add `fleet audit/complete/block/unclaim/archive` with
   transition checks. (2 h)
3. `fleet verify` — run `verification_command`, capture output into the handoff,
   gate completion on exit 0. (1 h)
4. `review.schema.json` + the peer-review playbook doc (recompute numbers, fetch
   citations, cross-check parallel artifacts, verdicts + corrections); make
   PEER_REVIEW → HUMAN_REVIEW require a conforming artifact. (2 h)
5. Linter rules: stale claims, stale `audited_repo_sha` (vs spoke HEAD), DONE tasks
   not yet archived, handoff file exists + validates for any task past PEER_REVIEW. (1 h)
6. Migrate the V1 board (or at least all non-DONE V1 tasks) so the linter can find
   V1's latent defects — and re-audit T-MIN-001 against spoke reality first.

V2's skeleton deserves the investment: it is the difference between a fleet you *hope*
behaves and one that *cannot* misbehave in the ways you've already been burned by.

— Claude Fable 5, 2026-08-10
