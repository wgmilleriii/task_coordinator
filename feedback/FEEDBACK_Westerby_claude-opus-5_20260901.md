---
title: "Task Coordinator V3 — agent feedback after a full shift in a spoke repo"
created_at: "2026-09-01T06:00:00Z"
last_modified: "2026-09-01T06:00:00Z"
author: "Westerby (newmexicoptg-org-3f)"
status: "active"
category: "00-Meta"
---

## Why this file is here and not in `task_coordinator_v3`

V3's `AGENTS.md` Rule 1 is absolute: *"You may NEVER modify, delete, or alter any
files in the `task_coordinator_v3` repository unless you are explicitly
dispatched."* I was asked for feedback, not dispatched to modify the engine, so
it goes to the established `feedback/` channel under the existing naming
convention. **Filing feedback about the engine by writing into the engine would
be the first thing the feedback should warn about.**

## System-Level Feedback

Spoke: `newmexicoptg.org`. One shift, ~20 tasks touched, 5 agents concurrent.

### What worked

**The schema is a real gate, and it caught me three times.** `fleet lint`
rejected an `open_questions` key I invented, then caught malformed YAML when I
appended events by hand, then required `audited_at`/`owner` before it would
accept a `DONE`. Every rejection was correct. **A task tracker that refuses
malformed work is worth more than one that accepts everything and reports
nicely.**

**`verification_command` per task is the single best field.** Board
reconciliation was only defensible because each task carried its own declared
proof — I ran them rather than inferring completion from commit counts. In one
case I *expected* the check to be stale and it was sound; **verifying beat
predicting in the one case I was confident**, which is the argument for the field
existing.

### Five things I would change

**1. Two tasks shipped with NO TASK FILE AT ALL** (`T-PTG-262`, `T-PTG-209`),
found only by cross-referencing commits against the board. A stale `OPEN` is a
*visible* error someone can correct; **an absent record is invisible**, and
anyone planning capacity would not know the work existed. **Suggest a
reconciliation command** — `tc audit --orphans` — flagging commits whose
`T-PTG-NNN` has no task file. The data is already in the commit messages.

**2. `status: DONE` should require the `verification_command` to have passed.**
The schema requires `audited_at`, `audited_by`, `audited_repo_sha` — attestation
that *someone looked* — but not that the task's own declared check ran green.
That is the gap between "audited" and "verified", and this epic's whole defect
family is scope mismatch.

**3. Hand-appending `events:` is expected and unguarded.** §4 of the new
coordination protocol explicitly says to hand-append when the CLI fails — "the
record beats the tooling", which I agree with. But I broke three task files doing
exactly that, because the files ended without an `events:` list and my append
produced invalid YAML. Lint caught it; **`tc event <id> --action X --details Y`
would have prevented it.** The blessed fallback path is the one with no
guardrail.

**4. Status vocabulary drifts.** `DONE` (106), `OPEN` (31), `open` (3, lowercase)
coexist, plus `HUMAN_REVIEW`, `PEER_REVIEW`, `DRAFT`, `CLAIMED`, `AUDITED`,
`CANCELLED`, `BLOCKED`. Nine values and a case variant. **Suggest the schema
enumerate them and normalise case** — three lowercase `open` rows will be missed
by any `grep "^status: OPEN"`, and that is precisely how I found the orphans.

**5. Nothing warns that a peer is inside the file you are about to edit.**
V3's own `AGENTS.md` says this honestly — *"nothing in `.fleet/` can tell you
another agent is mid-deploy"* — and defers to the vault. That is the right
division. But in practice **I pushed seven commits tonight that other agents had
left unpushed in the shared working copy**, including citation-correctness work
on papers heading for delivery. That is not a lock problem, it is a *visibility*
problem, and it sits exactly on the seam between the two systems. **Suggest `tc
exit` warn on unpushed commits in the spoke**, since it already runs at session
end and already checks for orphaned worktrees.

## The one number worth carrying

Seven unpushed commits rescued in one shift, three of them work that corrects
wrong citations. **A laptop restart has already cost this fleet once.** Whatever
form it takes, "you are leaving work only on this disk" belongs in the tooling
rather than in an agent's memory.
