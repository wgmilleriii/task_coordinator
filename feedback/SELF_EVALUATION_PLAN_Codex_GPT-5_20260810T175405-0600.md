# Task Coordinator Self-Evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to execute this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evaluate `task_coordinator` through its own Scout, PM, Worker, Reviewer, verification, and archival lifecycle without modifying the engine.

**Architecture:** A Scout creates three independent `task_coordinator` evaluation tasks with `fleet create`; a PM audits them; Workers and independent Reviewers process them sequentially because the repository-level claim lock permits only one claimed task per repository. Each task produces a focused report in `feedback/`, and the Coordinator synthesizes those reports into the required timestamped self-evaluation.

**Tech Stack:** `./bin/fleet`, YAML task/handoff/review records, Markdown reports, Git, POSIX shell, temporary Git copies under `/tmp`.

---

## File map

- Create through CLI, then complete: `tasks/active/T-TAS-001.yaml` — protocol and role consistency task.
- Create through CLI, then complete: `tasks/active/T-TAS-002.yaml` — state-machine and evidence enforcement task.
- Create through CLI, then complete: `tasks/active/T-TAS-003.yaml` — operational and concurrency safety task.
- Create: `feedback/EVALUATION_T-TAS-001_PROTOCOL.md` — Worker report for protocol consistency.
- Create: `feedback/EVALUATION_T-TAS-002_STATE_MACHINE.md` — Worker report for state-machine enforcement.
- Create: `feedback/EVALUATION_T-TAS-003_OPERATIONS.md` — Worker report for operational safety.
- Create through CLI: `handoffs/T-TAS-001_handoff.yaml`, `handoffs/T-TAS-002_handoff.yaml`, and `handoffs/T-TAS-003_handoff.yaml` — captured verification evidence.
- Create through CLI: `reviews/T-TAS-001_review.yaml`, `reviews/T-TAS-002_review.yaml`, and `reviews/T-TAS-003_review.yaml` — independent review verdicts.
- Move through CLI after all three tasks reach `DONE`: the three task files from `tasks/active/` to `tasks/archive/`.
- Create: `feedback/SELF_EVALUATION[Codex-GPT-5-20260810T175405-0600].md` — final synthesis.
- Regenerate but do not stage: `TASKS.md` — shared board already contains unrelated user changes.
- Allow CLI appends but do not stage: `logs/fleet.jsonl` — pre-existing untracked user-owned event log.

## Safety invariants for every task

- Never modify `bin/`, `schemas/`, `README.md`, `.github/`, or `AGENTS.md`.
- Never stage `TASKS.md`, `logs/`, or any `T-MIN-*` artifact.
- Use `apply_patch` for report and generated-YAML completion edits.
- Run corrupt-state, collision, or concurrency experiments only in a temporary copy created with `mktemp -d`.
- Use the live repository only for read-only inspection and the intended `fleet` lifecycle commands.
- Dispatch Workers sequentially; do not attempt concurrent claims for `repo: task_coordinator`.

### Task 1: Establish the current baseline

**Files:**
- Read: `AGENTS.md`
- Read: `README.md`
- Read: `bin/fleet.py`
- Read: `schemas/*.schema.json`
- Read: `tasks/active/*.yaml`
- Read: `handoffs/*.yaml`
- Read: `reviews/*.yaml`

- [ ] **Step 1: Confirm branch and external engine commits**

Run:

```bash
git status --short --branch
git log -6 --oneline --decorate
./bin/fleet create --help
```

Expected: branch `test/self-evaluation-20260810T175405-0600`; commits `b3bd27e` and `9244092` are present; `create` requires `--title` and `--repo`.

- [ ] **Step 2: Confirm fleet state is valid before evaluation**

Run:

```bash
./bin/fleet lint
```

Expected: exit 0 and `All active tasks, handoffs, and reviews passed strict schema validation.` If unrelated user state makes lint fail, record the exact failure and stop before any task creation.

- [ ] **Step 3: Record the engine baseline**

Run:

```bash
git diff --name-only HEAD -- bin schemas README.md .github AGENTS.md
git rev-parse HEAD
```

Expected: no restricted-zone working-tree diff; save the returned SHA as the evaluation baseline in Coordinator notes.

### Task 2: Scout creates and completes three OPEN tasks

**Files:**
- Create: `tasks/active/T-TAS-001.yaml`
- Create: `tasks/active/T-TAS-002.yaml`
- Create: `tasks/active/T-TAS-003.yaml`
- Regenerate: `TASKS.md`

- [ ] **Step 1: Dispatch one Scout subagent**

The prompt must assign only Scout work, require `pwd`, forbid engine/report work, preserve all `T-MIN-*` files, and require the exact commands and task content below.

- [ ] **Step 2: Create the three OPEN records with the CLI**

Run in order:

```bash
./bin/fleet create --title "Evaluate protocol and role consistency" --repo task_coordinator --priority P1 --lane codex
./bin/fleet create --title "Evaluate state-machine and evidence enforcement" --repo task_coordinator --priority P1 --lane codex
./bin/fleet create --title "Evaluate operational and concurrency safety" --repo task_coordinator --priority P1 --lane codex
```

Expected: creation of `T-TAS-001`, `T-TAS-002`, and `T-TAS-003`, each in `OPEN` status.

- [ ] **Step 3: Complete T-TAS-001 generated fields**

Use `apply_patch` to replace its generated scope and definition-of-done arrays and add the missing policy fields with this content:

```yaml
dependencies: []
scope:
- Compare AGENTS.md, README.md, fleet CLI help, schemas, and current lifecycle artifacts.
- Map every documented agent role to executable commands and identify contradictions, missing steps, unsafe manual edits, and ambiguous authority.
- Evaluate the new fleet create workflow, including ID generation and required post-creation YAML edits.
definition_of_done:
- feedback/EVALUATION_T-TAS-001_PROTOCOL.md exists with Executive verdict, Scope and evidence, Confirmed strengths, Findings, Prior feedback disposition, Recommendations, and Domain verdict sections.
- Every defect claim cites a file, command output, or reproducible observation from the current repository.
- No restricted-zone file is modified by the evaluation.
human_review_required: false
```

- [ ] **Step 4: Complete T-TAS-002 generated fields**

Use `apply_patch` with this content:

```yaml
dependencies: []
scope:
- Inspect lifecycle and schema enforcement for create, audit, claim, verify, submit, peer review, human review, block, close, and archive behavior.
- Reproduce suspected bypasses only in a temporary repository copy under /tmp.
- Evaluate dependency readiness, stale audit handling, verification provenance, fabricated artifacts, and transition failure behavior.
definition_of_done:
- feedback/EVALUATION_T-TAS-002_STATE_MACHINE.md exists with Executive verdict, Scope and evidence, Confirmed strengths, Findings, Prior feedback disposition, Recommendations, and Domain verdict sections.
- Each current defect has direct static evidence or a safe temporary-copy reproduction with command output.
- The live engine and unrelated fleet records remain unmodified except for intended T-TAS lifecycle artifacts.
human_review_required: false
```

- [ ] **Step 5: Complete T-TAS-003 generated fields**

Use `apply_patch` with this content:

```yaml
dependencies: []
scope:
- Evaluate locking, shared-worktree isolation, generated-board contention, verification environments, packaging, logging, recovery, and observability.
- Assess the difference between single-machine locking and multi-machine fleet coordination.
- Use temporary copies for any concurrency or failure-injection experiment.
definition_of_done:
- feedback/EVALUATION_T-TAS-003_OPERATIONS.md exists with Executive verdict, Scope and evidence, Confirmed strengths, Findings, Prior feedback disposition, Recommendations, and Domain verdict sections.
- Operational claims are supported by current code references, command output, or safe temporary-copy experiments.
- No restricted-zone file or unrelated task artifact is modified by the evaluation.
human_review_required: false
```

- [ ] **Step 6: Validate and render**

Run:

```bash
./bin/fleet lint
./bin/fleet render
rg -n "T-TAS-001|T-TAS-002|T-TAS-003" TASKS.md
```

Expected: lint exit 0 and all three OPEN tasks appear on the board.

- [ ] **Step 7: Review and commit only Scout artifacts**

Run:

```bash
git diff --check -- tasks/active/T-TAS-001.yaml tasks/active/T-TAS-002.yaml tasks/active/T-TAS-003.yaml
git add tasks/active/T-TAS-001.yaml tasks/active/T-TAS-002.yaml tasks/active/T-TAS-003.yaml
git commit -m "fleet: create self-evaluation tasks"
```

Expected: commit contains exactly the three T-TAS task records; `TASKS.md`, `logs/`, and `T-MIN-*` remain unstaged.

### Task 3: PM audits all evaluation tasks

**Files:**
- Modify through CLI: `tasks/active/T-TAS-001.yaml`
- Modify through CLI: `tasks/active/T-TAS-002.yaml`
- Modify through CLI: `tasks/active/T-TAS-003.yaml`

- [ ] **Step 1: Dispatch one PM subagent**

The prompt must require validation of every scope and verification command against the current branch, forbid Worker evaluation, and require use of `fleet audit` for transitions.

- [ ] **Step 2: Capture the audit SHA**

Run:

```bash
git rev-parse HEAD
```

Expected: a 40-character commit SHA. Use this same returned value for all three audit commands.

- [ ] **Step 3: Audit T-TAS-001**

Run `fleet audit` with this verification command:

```text
test -f feedback/EVALUATION_T-TAS-001_PROTOCOL.md && rg -q '^## Executive verdict' feedback/EVALUATION_T-TAS-001_PROTOCOL.md && rg -q '^## Findings' feedback/EVALUATION_T-TAS-001_PROTOCOL.md && rg -q '^## Prior feedback disposition' feedback/EVALUATION_T-TAS-001_PROTOCOL.md && rg -q '^## Recommendations' feedback/EVALUATION_T-TAS-001_PROTOCOL.md
```

Auditor name: `PM-Self-Evaluation`.

- [ ] **Step 4: Audit T-TAS-002**

Run `fleet audit` with this verification command:

```text
test -f feedback/EVALUATION_T-TAS-002_STATE_MACHINE.md && rg -q '^## Executive verdict' feedback/EVALUATION_T-TAS-002_STATE_MACHINE.md && rg -q '^## Findings' feedback/EVALUATION_T-TAS-002_STATE_MACHINE.md && rg -q '^## Prior feedback disposition' feedback/EVALUATION_T-TAS-002_STATE_MACHINE.md && rg -q '^## Recommendations' feedback/EVALUATION_T-TAS-002_STATE_MACHINE.md
```

Auditor name: `PM-Self-Evaluation`.

- [ ] **Step 5: Audit T-TAS-003**

Run `fleet audit` with this verification command:

```text
test -f feedback/EVALUATION_T-TAS-003_OPERATIONS.md && rg -q '^## Executive verdict' feedback/EVALUATION_T-TAS-003_OPERATIONS.md && rg -q '^## Findings' feedback/EVALUATION_T-TAS-003_OPERATIONS.md && rg -q '^## Prior feedback disposition' feedback/EVALUATION_T-TAS-003_OPERATIONS.md && rg -q '^## Recommendations' feedback/EVALUATION_T-TAS-003_OPERATIONS.md
```

Auditor name: `PM-Self-Evaluation`.

- [ ] **Step 6: Validate and commit only PM artifacts**

Run:

```bash
./bin/fleet lint
git add tasks/active/T-TAS-001.yaml tasks/active/T-TAS-002.yaml tasks/active/T-TAS-003.yaml
git commit -m "fleet: audit self-evaluation tasks"
```

Expected: all three tasks are `AUDITED`; commit excludes `TASKS.md`, `logs/`, and all `T-MIN-*` files.

### Task 4: Execute and review T-TAS-001

**Files:**
- Create: `feedback/EVALUATION_T-TAS-001_PROTOCOL.md`
- Modify through CLI: `tasks/active/T-TAS-001.yaml`
- Create through CLI: `handoffs/T-TAS-001_handoff.yaml`
- Create through CLI: `reviews/T-TAS-001_review.yaml`

- [ ] **Step 1: Dispatch a protocol Worker subagent**

Require `pwd`, `fleet claim T-TAS-001 --owner Codex-Protocol-Worker`, read-only inspection, the report headings specified in the task, explicit evidence, no engine edits, and a commit containing only the report and T-TAS-001 task record.

- [ ] **Step 2: Verify and submit the Worker report**

After the report commit, run:

```bash
./bin/fleet verify T-TAS-001 --model GPT-5
git rev-parse HEAD
```

Use `apply_patch` to replace `REQUIRED_PLEASE_FILL` in `handoffs/T-TAS-001_handoff.yaml` with the returned commit SHA. Then run:

```bash
./bin/fleet submit T-TAS-001
git add tasks/active/T-TAS-001.yaml handoffs/T-TAS-001_handoff.yaml
git commit -m "fleet: submit protocol evaluation"
```

Expected: T-TAS-001 is `PEER_REVIEW`, with a schema-valid handoff tied to the report commit.

- [ ] **Step 3: Dispatch an independent protocol Reviewer subagent**

The Reviewer must run `fleet start-review T-TAS-001 --reviewer Codex-Protocol-Reviewer --model GPT-5`, inspect the report and handoff, replace the generated verdict/findings through `apply_patch`, run `fleet record-review T-TAS-001`, and commit only the task and review artifact. The Reviewer may use `PASS`, `PASS_WITH_CORRECTIONS`, or `FAIL` based on evidence.

- [ ] **Step 4: Check task result**

Run:

```bash
./bin/fleet lint
rg -n '^status:' tasks/active/T-TAS-001.yaml
```

Expected after a passing review: `status: DONE`. If `IN_PROGRESS`, dispatch a fresh Worker to correct only the report, then repeat verification and independent review.

### Task 5: Execute and review T-TAS-002

**Files:**
- Create: `feedback/EVALUATION_T-TAS-002_STATE_MACHINE.md`
- Modify through CLI: `tasks/active/T-TAS-002.yaml`
- Create through CLI: `handoffs/T-TAS-002_handoff.yaml`
- Create through CLI: `reviews/T-TAS-002_review.yaml`

- [ ] **Step 1: Dispatch a state-machine Worker subagent**

Require `pwd`, `fleet claim T-TAS-002 --owner Codex-State-Worker`, a temporary copy for every mutating adversarial test, the task's exact report headings, command transcripts for current defects, no live engine edits, and a commit containing only the report and T-TAS-002 task record.

- [ ] **Step 2: Verify and submit the Worker report**

Run:

```bash
./bin/fleet verify T-TAS-002 --model GPT-5
git rev-parse HEAD
```

Patch the returned SHA into `handoffs/T-TAS-002_handoff.yaml`, then run:

```bash
./bin/fleet submit T-TAS-002
git add tasks/active/T-TAS-002.yaml handoffs/T-TAS-002_handoff.yaml
git commit -m "fleet: submit state-machine evaluation"
```

Expected: T-TAS-002 is `PEER_REVIEW` with a schema-valid handoff.

- [ ] **Step 3: Dispatch an independent state-machine Reviewer subagent**

Require `fleet start-review T-TAS-002 --reviewer Codex-State-Reviewer --model GPT-5`, evidence review, `apply_patch` completion of the review artifact, `fleet record-review T-TAS-002`, and a task/review-only commit.

- [ ] **Step 4: Check task result**

Run `fleet lint` and inspect the task status. A passing review must produce `DONE`; a failed review returns to `IN_PROGRESS` and triggers report-only correction before resubmission.

### Task 6: Execute and review T-TAS-003

**Files:**
- Create: `feedback/EVALUATION_T-TAS-003_OPERATIONS.md`
- Modify through CLI: `tasks/active/T-TAS-003.yaml`
- Create through CLI: `handoffs/T-TAS-003_handoff.yaml`
- Create through CLI: `reviews/T-TAS-003_review.yaml`

- [ ] **Step 1: Dispatch an operations Worker subagent**

Require `pwd`, `fleet claim T-TAS-003 --owner Codex-Operations-Worker`, static inspection plus temporary-copy experiments, the exact report headings, evidence for local versus distributed coordination claims, no engine edits, and a report/task-only commit.

- [ ] **Step 2: Verify and submit the Worker report**

Run:

```bash
./bin/fleet verify T-TAS-003 --model GPT-5
git rev-parse HEAD
```

Patch the returned SHA into `handoffs/T-TAS-003_handoff.yaml`, then run:

```bash
./bin/fleet submit T-TAS-003
git add tasks/active/T-TAS-003.yaml handoffs/T-TAS-003_handoff.yaml
git commit -m "fleet: submit operations evaluation"
```

Expected: T-TAS-003 is `PEER_REVIEW` with a schema-valid handoff.

- [ ] **Step 3: Dispatch an independent operations Reviewer subagent**

Require `fleet start-review T-TAS-003 --reviewer Codex-Operations-Reviewer --model GPT-5`, evidence review, `apply_patch` completion of the review artifact, `fleet record-review T-TAS-003`, and a task/review-only commit.

- [ ] **Step 4: Check task result**

Run `fleet lint` and inspect the task status. A passing review must produce `DONE`; a failed review returns to `IN_PROGRESS` and triggers report-only correction before resubmission.

### Task 7: Archive completed evaluation tasks safely

**Files:**
- Move through CLI: `tasks/active/T-TAS-001.yaml` to `tasks/archive/T-TAS-001.yaml`
- Move through CLI: `tasks/active/T-TAS-002.yaml` to `tasks/archive/T-TAS-002.yaml`
- Move through CLI: `tasks/active/T-TAS-003.yaml` to `tasks/archive/T-TAS-003.yaml`

- [ ] **Step 1: Confirm no unrelated active task is terminal**

Run:

```bash
rg -n '^id:|^status:' tasks/active/*.yaml
```

Expected: only T-TAS-001, T-TAS-002, and T-TAS-003 have `DONE`, `CANCELLED`, or `DEFERRED`. If any `T-MIN-*` task is terminal, do not run the global archive command; leave T-TAS tasks at `DONE` and record why.

- [ ] **Step 2: Archive through the CLI when safe**

Run:

```bash
./bin/fleet archive
./bin/fleet lint
```

Expected: three T-TAS files move to `tasks/archive/`; unrelated active tasks remain in place.

- [ ] **Step 3: Commit only T-TAS moves**

Run:

```bash
git add -A -- tasks/active/T-TAS-001.yaml tasks/active/T-TAS-002.yaml tasks/active/T-TAS-003.yaml tasks/archive/T-TAS-001.yaml tasks/archive/T-TAS-002.yaml tasks/archive/T-TAS-003.yaml
git commit -m "fleet: archive self-evaluation tasks"
```

Expected: commit contains only the three task moves. If archival was unsafe, skip this commit.

### Task 8: Synthesize the final self-evaluation

**Files:**
- Read: the three Worker reports, handoffs, and review artifacts.
- Create: `feedback/SELF_EVALUATION[Codex-GPT-5-20260810T175405-0600].md`.

- [ ] **Step 1: Write the synthesis with required sections**

Use `apply_patch`. Required headings:

```markdown
## Executive verdict
## Evaluation method and lifecycle outcome
## Confirmed strengths
## Critical findings
## Major findings
## Minor findings
## Prior feedback disposition
## Dogfooding findings
## Prioritized future task backlog
## Verification record
```

Every current defect must cite a Worker report and its supporting command or file evidence. Historical claims not retested must be labeled as such.

- [ ] **Step 2: Commit the final synthesis only**

Stage the exact filename and commit with:

```bash
git add 'feedback/SELF_EVALUATION[Codex-GPT-5-20260810T175405-0600].md'
git commit -m "docs: add task coordinator self-evaluation"
```

Expected: one new final Markdown document; no unrelated artifact is staged.

### Task 9: Final verification

**Files:**
- Verify: all T-TAS task, report, handoff, review, and final synthesis artifacts.

- [ ] **Step 1: Validate fleet state and regenerate the board**

Run:

```bash
./bin/fleet lint
./bin/fleet render
```

Expected: lint exit 0; render completes. Leave the shared `TASKS.md` unstaged.

- [ ] **Step 2: Verify artifacts and restricted-zone cleanliness**

Run:

```bash
git diff --check
git diff --name-only aa2a1de -- bin schemas README.md .github AGENTS.md
rg --files feedback handoffs reviews tasks/archive | rg 'T-TAS-00[1-3]|SELF_EVALUATION\[Codex-GPT-5-20260810T175405-0600\]'
git status --short
```

Expected: no restricted-zone path changed after `aa2a1de`; all three reports, handoffs, reviews, task records, and final synthesis are present; only known unrelated user artifacts and the generated board remain unstaged.

- [ ] **Step 3: Review commits**

Run:

```bash
git log --oneline aa2a1de..HEAD
```

Expected: discrete commits for task creation, audit, each Worker submission, each peer review, archival when safe, and final synthesis.
