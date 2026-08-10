# Task Coordinator Self-Evaluation Design

**Coordinator:** Codex  
**Model:** GPT-5  
**Approved approach:** Full dogfood lifecycle  
**Approved scope:** Evaluation only  
**Working branch:** `test/self-evaluation-20260810T175405-0600`

## Purpose

Evaluate `task_coordinator` by using its own role separation, task records, lifecycle commands, evidence capture, and review artifacts. The evaluation must test both the documented workflow and the actual enforcement behavior without changing the engine.

## Boundaries

- Do not modify `bin/`, `schemas/`, `README.md`, `.github/`, or any application logic.
- Do not implement fixes, even when a defect is confirmed.
- Limit deliverables to auto-generated `T-TAS-*` fleet records and new Markdown reports in `feedback/`.
- Preserve unrelated existing work, including all `T-MIN-*` task files and pre-existing entries in the untracked `logs/` directory. CLI-generated self-evaluation events may be appended to the log, but the user-owned log will not be staged in self-evaluation commits.
- Perform destructive or corrupt-state experiments only in temporary copies under `/tmp`.
- Use `./bin/fleet` for lifecycle transitions and generated artifacts wherever the CLI provides a command.

## Roles and sequence

1. **Fleet Coordinator:** defines scopes, dispatches roles, reviews results, and writes the final synthesis. The Coordinator does not create task YAML or perform the scoped Worker evaluations.
2. **Scout:** uses `fleet create` three times with `repo: task_coordinator`, replaces the generated `REQUIRED_PLEASE_FILL` scope and definition-of-done values as instructed by the command, then runs `fleet lint` and `fleet render`. The command's auto-ID scheme produces `T-TAS-*` IDs from the repository name. Its need for direct post-creation YAML edits is evaluation evidence.
3. **Project Manager:** inspects each task, pins it to the repository SHA, supplies a bounded verification command, and transitions it to `AUDITED` through `fleet audit`.
4. **Workers:** execute one task at a time because the coordinator enforces a repository-level claim lock. Each Worker claims through the CLI, performs read-only or temporary-copy tests, writes one report, verifies it, fills the generated handoff's required SHA, and submits it for peer review.
5. **Reviewers:** an agent other than the task's Worker starts a structured review through the CLI, inspects the report and evidence, fills the generated review artifact, and records the verdict. A passing task uses `human_review_required: false` and may advance to `DONE` without pretending to possess human authority.
6. **Fleet Coordinator:** archives completed evaluation tasks through the CLI and synthesizes all findings into the required timestamped self-evaluation document.

## Evaluation tasks

### T-TAS-001 — Protocol and role consistency

Compare `AGENTS.md`, `README.md`, CLI help, current task artifacts, and role instructions. Identify contradictions, missing commands, unsafe manual steps, ambiguous authority, and documentation drift. Confirm which instructions are executable by each role.

Deliverable: `feedback/EVALUATION_T-TAS-001_PROTOCOL.md`

### T-TAS-002 — State-machine and evidence enforcement

Use static inspection and adversarial experiments in a temporary repository copy to evaluate schema failure behavior, task creation, audit and claim gates, dependency readiness, stale audit handling, verification provenance, fabricated handoffs, peer-review transitions, human-review enforcement, and archival behavior.

Deliverable: `feedback/EVALUATION_T-TAS-002_STATE_MACHINE.md`

### T-TAS-003 — Operational and concurrency safety

Evaluate local locking, multi-agent worktree isolation, generated-file contention, verification environments, packaging and dependency assumptions, logs, recovery behavior, observability, and suitability for multi-machine coordination. Concurrency experiments must use temporary copies or read-only inspection.

Deliverable: `feedback/EVALUATION_T-TAS-003_OPERATIONS.md`

## Report requirements

Each Worker report must include:

- repository SHA and timestamp;
- files and commands inspected;
- confirmed strengths;
- findings classified as `CRITICAL`, `MAJOR`, `MINOR`, or `INFO`;
- direct evidence for every defect claim;
- disposition of relevant prior feedback: fixed, partially fixed, still present, or not retested;
- concrete recommendations framed as future work, not implemented changes;
- an overall verdict for its evaluation domain.

## Verification and review

Each task receives a bounded verification command that confirms its report exists and contains the required sections. `fleet verify --model` captures command output in a handoff. The Worker records the actual report commit SHA in that handoff, then uses `fleet submit`.

The Reviewer checks that conclusions are supported by reproducible evidence, that temporary-copy tests did not alter the live engine, and that no restricted-zone files changed. Review verdicts are recorded through `fleet record-review`. A failed review returns the task to `IN_PROGRESS` for correction of the report only.

## Final synthesis

The Coordinator will create:

`feedback/SELF_EVALUATION[Codex-GPT-5-<completion-timestamp>].md`

The synthesis will rank findings by severity, distinguish confirmed current defects from historical findings, identify process contradictions revealed by dogfooding, summarize strengths, and propose a prioritized future task backlog. It will also document how far every evaluation task progressed through the lifecycle.

## Success criteria

- Three valid `T-TAS-*` evaluation tasks are created through `fleet create` and processed through the documented role separation.
- No engine or restricted-zone file is modified.
- Every substantive defect is supported by static evidence or a safe reproduction.
- Each Worker report receives structured peer review.
- The final timestamped self-evaluation document is present in `feedback/`.
- `./bin/fleet lint`, `./bin/fleet render`, and repository diff checks complete without introducing invalid fleet state.

## Known process risks

- `fleet create` generates placeholder scope and definition-of-done values, so creation still requires a direct YAML completion step before linting.
- The live worktree contains unrelated untracked files; commits must stage only self-evaluation artifacts.
- CLI lifecycle commands mutate shared files such as `TASKS.md`; Workers therefore run sequentially.
- Because this is the coordinator evaluating itself, branch and verification provenance require special scrutiny in the final report.
