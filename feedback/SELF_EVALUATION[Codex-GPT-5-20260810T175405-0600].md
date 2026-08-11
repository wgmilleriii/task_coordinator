# Task Coordinator Self-Evaluation

- **Agent:** Codex
- **Model:** GPT-5
- **Session timestamp:** `20260810T175405-0600`
- **Evaluation branch:** `test/self-evaluation-execution-20260810T175405-0600`
- **Isolated worktree:** `/private/tmp/task_coordinator_self_evaluation/task_coordinator`
- **Audited implementation baseline:** `0fc849c6e987b52bef3e49f7811052dfa076d081`
- **Scope:** Evaluation only; no engine fixes

## Executive verdict

`task_coordinator` is **not ready to act as the authoritative coordinator for a parallel or distributed agent fleet**. Its architecture is directionally strong—a file-backed task store, schema-controlled artifacts, explicit roles, lifecycle vocabulary, evidence capture, peer-review records, a same-checkout process lock, and unusually clear engine-room safeguards—but the executable guarantees do not yet match the operating claims.

The self-evaluation found a release-blocking defect in the only documented `OPEN → AUDITED` path: `fleet audit --command ...` overwrites the parser's subcommand selector, exits `0` without output, and performs no transition. The coordinator therefore reports shell success while leaving tasks unchanged. This blocked all three evaluation tasks at `OPEN` and prevented legitimate claim, verification, handoff, peer-review, or archival steps.

The deeper adversarial review confirmed four additional critical safety failures:

- fabricated or stale handoffs can submit work that was never successfully verified;
- peer and human review artifacts are not bound to the task, reviewed SHA, or an authorized independent reviewer;
- legal `block → claim another task → unblock` commands can create two simultaneous `CLAIMED` tasks for one repository;
- the local `fcntl` lock coordinates only cooperating processes in one checkout, while a second clone or machine can act concurrently.

The appropriate current posture is **limited local experimentation and task tracking only**. Do not rely on this version for autonomous execution, evidence authority, peer/human approval, or multi-checkout coordination until the critical findings and effect-level regression tests are addressed.

## Evaluation method and lifecycle outcome

The evaluation deliberately dogfooded the repository's own process:

1. A dedicated design and execution plan were written and approved.
2. Chip's newly added `fleet create` command created three `OPEN` tasks:
   - `T-TAS-001` — protocol and role consistency;
   - `T-TAS-002` — state-machine and evidence enforcement;
   - `T-TAS-003` — operational and concurrency safety.
3. A Scout completed the generated scope/definition fields, ran strict lint, and committed only the three task records at `30dea3b`.
4. Independent off-fleet/session-level specification and quality reviewers identified weak completion criteria. The Scout hardened all three tasks at `0fc849c`; both session-level review gates then passed.
5. A fresh PM ran the exact three planned `fleet audit` commands. Every command exited `0` with no stdout/stderr, wrote no audit fields/events, and left the task `OPEN`.
6. The PM stopped rather than fixing the engine, hand-editing status, or using a dispatch workaround. This preserved the evaluation-only boundary and the truth of the state machine.
7. Because Workers cannot lawfully claim an `OPEN` task, three independent Auditor subagents completed the substantive domains through the permitted `feedback/` drop box. All mutating experiments used unique temporary copies.
8. Every report underwent independent off-fleet/session-level specification review, correction, evidence/quality review, and re-review. No Critical or Important report-quality issue remained.

The lifecycle outcome is intentionally incomplete:

| Task | Created | Scout review | PM audit | Claimed | Handoff/review | Final state |
|---|---:|---:|---:|---:|---:|---|
| `T-TAS-001` | Yes | Passed | Silent no-op | No | None | `OPEN` |
| `T-TAS-002` | Yes | Passed | Silent no-op | No | None | `OPEN` |
| `T-TAS-003` | Yes | Passed | Silent no-op | No | None | `OPEN` |

The three reviewed evidence reports are:

- [Protocol and role consistency](EVALUATION_T-TAS-001_PROTOCOL.md)
- [State-machine and evidence enforcement](EVALUATION_T-TAS-002_STATE_MACHINE.md)
- [Operational and concurrency safety](EVALUATION_T-TAS-003_OPERATIONS.md)

## Confirmed strengths

1. **The core decomposition is sound.** Per-task YAML, a generated human view, separate handoff/review records, and explicit states are a much stronger foundation than a monolithic task board.
2. **The engine guard is concrete.** `AGENTS.md` names restricted paths, requires an audited self-modification task, prohibits branch switching in the live coordinator checkout for upgrades, and mandates worktree isolation.
3. **Schema strictness has materially improved.** Controlled fields, conditional audit/owner requirements, RFC 3339 validation, filename/duplicate/dangling-dependency linting, and separate handoff/review schemas close several early prototype gaps.
4. **The CLI surface is broad enough to express most intended lifecycle operations.** Create, audit, claim, verify, submit, peer review, block/unblock, close, and archive commands now exist.
5. **Basic same-checkout serialization works.** A nonblocking `fcntl` lock prevented two cooperating CLI processes in one checkout from mutating concurrently and released on process exit.
6. **Individual task and board destinations use temporary files plus `os.replace`.** This reduces partial-file truncation, although it is not a multi-file transaction.
7. **Verification captures useful evidence fields.** Exit status, stdout/stderr, model, and detected branch are recorded; completed verification attempts log success/failure.
8. **Prior feedback has driven real progress.** Git history, exact dependencies, `.gitignore`, date validation, claim timestamps, handoff/review validation, review transitions, block/unblock, and archive mechanics all exist because earlier audits were acted upon.
9. **The new `create` command is a valuable direction.** It gives Scouts a CLI entrypoint and deterministic active-namespace allocation, even though its current contract remains incomplete.

## Critical findings

### C-01 — `audit` silently succeeds without dispatching

The root subparser and audit's `--command` option both use `args.command`. The verification string replaces the subcommand name before dispatch. There is no fail-closed unknown-dispatch branch, so the program returns `0` without running `cmd_audit`.

Impact: the documented lifecycle cannot leave `OPEN`, and automation receives false success. This was independently reproduced on all three self-evaluation tasks and in temporary copies. See T-TAS-002 F-01.

### C-02 — Submit accepts fabricated or superseded verification evidence

Submit validates handoff shape but does not bind task ID, repository, audit/base SHA, owner, command/run, live head, or current successful verification. A schema-valid handoff naming a different task/repository submitted successfully. A later failed verification also left an earlier successful handoff reusable.

Impact: `PEER_REVIEW` does not prove that the submitted code or report passed the task's verification command. See T-TAS-002 F-02.

### C-03 — Review and human approval artifacts are unbound and unauthenticated

A task owner can review their own task; review task ID and reviewed head may be unrelated; findings may be empty; human closure can be attributed to the default `Unknown`. Non-human tasks can also close directly from `PEER_REVIEW` without a recorded review PASS.

Impact: peer/human gates are labels and mutable files, not evidence-bound authority boundaries. See T-TAS-002 F-03.

### C-04 — Block/unblock can create duplicate repository ownership

When claimed task A becomes `BLOCKED`, it stops excluding new claims. Task B can claim the same repository. Unblocking A restores its prior `CLAIMED` state without rechecking exclusion, leaving both tasks claimed.

Impact: the coordinator can serialize commands that create an internally invalid ownership state. See T-TAS-002 F-04 and T-TAS-003 O-05.

### C-05 — Coordination is limited to one checkout

The `fcntl` lock path is checkout-local. A second clone/worktree has its own lock file and can execute concurrently; no remote push arbitration, central service, compare-and-swap revision, or distributed lock exists.

Impact: the README's fleet-wide parallelism guarantee is unsupported. See T-TAS-003 O-01.

## Major findings

### Protocol and interface

- README describes a database-backed, massively parallel, cryptographic, automated-review system that the file/CLI implementation does not provide. (T-TAS-001 P-01; `README.md:5,29,43`; `bin/fleet.py:39-59,375-397,459-477`.)
- Agent roles and lanes are caller-supplied strings, not enforceable authority. Reviewer/Auditor responsibilities are incomplete. (T-TAS-001 P-02; `README.md:51-56`; `bin/fleet.py:273-275,289-294,319-320,459-477`.)
- `create` uses a three-character repository prefix, scans only active tasks, collides across similar repository names, and reuses archived IDs. (T-TAS-001 P-03; `bin/fleet.py:242-258`; two temporary-copy reproductions.)
- `create` writes before validation, reports success for invalid titles, and creates placeholder scope/DoD values that strict lint accepts. (T-TAS-001 P-04; `bin/fleet.py:242-275`; invalid-title and placeholder-lint reproductions.)
- README omits six executable workflows and gives a `verify` example that fails because `--model` is required. (T-TAS-001 P-05; `README.md:83,94-96`; `bin/fleet.py:630-635`.)
- Board freshness is manual, inconsistently specified, unenforced, and unverifiable. This run observed `TASKS.md` diverging from hardened task YAML. (T-TAS-001 P-06; `tasks/active/T-TAS-001.yaml:9-25`; `TASKS.md:47-56` at the audited baseline.)

### State and evidence

- Dependencies, audit SHA, lane, and repository identity are recorded but not enforced at claim time; repository cleanliness is neither recorded nor checked. (T-TAS-002 F-05; `bin/fleet.py:301-327`.)
- YAML parse errors are printed and skipped; lint and mutators can continue against an incomplete store. (T-TAS-002 F-06; `bin/fleet.py:24-37,90-119`; malformed-store reproduction.)
- Task, artifact, event-log, and board writes are not one recoverable transaction. Failure injection left task/log state committed while render failed. (T-TAS-002 F-07 and T-TAS-003 O-04; `bin/fleet.py:39-59,278-298`.)
- Archive is a global sweep and can overwrite an existing same-name archived task. (T-TAS-002 F-08; `bin/fleet.py:589-604`; archive-collision reproduction.)

### Operations and concurrency

- Worktree-aware execution is absent. `verify` derives `BASE_DIR/../repo`, which can point from an evaluation worktree back to the live primary checkout. (T-TAS-003 O-02; `bin/fleet.py:337-344`; worktree-path reproduction.)
- The wrapper assumes a local `.venv`; a clean clone exited `127`. Verification inherits the coordinator environment rather than selecting the target repository's runner. (T-TAS-003 O-03; `bin/fleet:1-4`; `bin/fleet.py:349-360`; clean-clone reproduction.)
- Claims have timestamps but no lease, heartbeat, release/transfer, expiry, or stale-owner recovery. Ownership also releases too early at review. (T-TAS-003 O-05; `bin/fleet.py:301-327,505-515,524-562`.)
- `TASKS.md` remains a tracked cross-branch/clone contention surface. (T-TAS-003 O-06; canonical state handlers call `cmd_render` while the board remains tracked.)
- Archive is global, destructive, unlogged, non-transactional, and separates tasks from their handoff/review history. (T-TAS-003 O-07; `bin/fleet.py:589-604`; current archive/handoff/review layout.)
- Apart from one inline RFC 3339 guard, there is no standalone lifecycle/operational test suite or CI. (T-TAS-003 O-08; `bin/fleet.py:82-88`; no test configuration or `.github` workflow.)

## Minor findings

- DRAFT is accepted by the audit handler but omitted from the documented lifecycle and contradicted by the error message. (T-TAS-001 P-07; `bin/fleet.py:278-284`.)
- Subcommand help rarely explains prerequisite/generated artifacts or the next command. (T-TAS-001 P-08; full subcommand-help sweep.)
- `create`, block/unblock, and optional human identity use `Unknown`, weakening auditability. (T-TAS-001 P-02; `bin/fleet.py:273-275,530-557,581-582,653`.)
- The fixed five-minute verification timeout is held under the global local lock and timeout failures are not logged. (T-TAS-003 O-05 and T-TAS-002 verification coverage; `bin/fleet.py:349-355,659-666`.)
- Logging lacks old/new state, task revision, checkout/host/process/session, duration, failure category, and recovery linkage. (T-TAS-003 O-09; `bin/fleet.py:47-75`.)
- Token/cost fields are nullable self-reported values, not auditable accounting. (T-TAS-003 O-09; handoff schema and current handoffs.)
- `fcntl` portability, advisory-lock assumptions, supported filesystems, and availability behavior are undocumented. (T-TAS-003 O-10; `bin/fleet.py:659-666`.)
- State ownership remains incomplete: no start/defer/cancel commands exist, and authority for `IN_PROGRESS`, `DEFERRED`, and `CANCELLED` is unclear. (T-TAS-002 F-10; schema state list versus CLI help.)

## Prior feedback disposition

The domain reports inventory the complete seven-document pre-evaluation corpus. The most important current dispositions are:

### Confirmed fixed

- The coordinator is now a Git repository with history and a remote.
- RFC 3339 validation is installed and guarded by an inline known-invalid-date self-test.
- Task/handoff/review schemas use controlled properties; unknown fields are rejected.
- Task lint now detects active duplicate IDs, filename mismatch, and dangling dependencies.
- `claimed_at`, block/unblock fields, task events, global events, review artifacts, and archive mechanics exist.
- Handoff and review shape validation is connected to submit/record-review/lint.
- Human-required tasks no longer close directly from `PEER_REVIEW`; the separate unauthenticated-human and non-human bypasses remain.
- The earlier `datetime.UTC` review crash and deprecated `datetime.utcnow()` use are fixed.

### Partially fixed

- Claim races are closed only for cooperating processes in one checkout, not clones or machines.
- Atomic replacement protects individual task/board files, not an entire transition.
- Verification captures model/branch/output but does not bind the evidence to repository state or choose the correct checkout/environment.
- `claimed_at` exists without lease or recovery semantics.
- Archive exists without collision protection, selection, provenance, rollback, or artifact bundling.
- The generated board is serialized locally but remains a tracked merge/staleness surface across branches and clones.
- Exact Python requirements exist, but clean-clone bootstrap still fails.

### Still present

- No authoritative distributed coordination model has been selected.
- Audit freshness, dependency readiness, lane authorization, repository identity, and dirty-worktree provenance are not enforced.
- Multi-file transitions are not atomic or recoverable.
- Verification uses unrestricted `shell=True`, inherited environment, fixed timeout, and mutable evidence files.
- No standalone end-to-end lifecycle/failure-injection test suite or CI exists.
- Shared checkout/worktree isolation, stale claim recovery, board contention, and verification-interpreter ambiguity remain operational hazards.

## Dogfooding findings

1. **`fleet create` made task creation possible but not complete.** The Scout still had to edit generated YAML directly, and the board became stale after task hardening because post-edit render is not enforced.
2. **The new auto-ID contract immediately exposed namespace design.** `task_coordinator` became `T-TAS-*`; temporary testing showed similar repository names share that namespace and archived IDs are reused.
3. **The PM stage produced the most important finding.** The exact documented audit commands exited `0` but did nothing. A green shell status was therefore weaker than inspecting effect/state.
4. **The process correctly prevented laundering the blocker.** No agent patched the engine, manually changed status, or used a parser/PATH workaround. The tasks remain honestly `OPEN`.
5. **Branch collision occurred during planning.** Another assistant switched the live checkout while work was underway, exactly validating the newly added worktree rule. The evaluation moved to an isolated temporary worktree.
6. **Worktree isolation exposed path assumptions.** A normally named sibling worktree would make self-verification resolve the primary checkout. The temporary layout had to place the worktree at `.../task_coordinator` so `BASE_DIR/../task_coordinator` resolved to itself.
7. **Generated artifacts complicated clean commits.** `create` and transitions changed shared `TASKS.md` and an untracked global log; commits had to stage only task/report files.
8. **The fleet's own structured peer-review stage was unreachable.** External independent spec and quality reviewers were used for the reports, but no handoff/review artifact was fabricated to pretend the lifecycle completed.

## Prioritized future task backlog

### P0 — Restore and prove the lifecycle

1. Separate argparse destinations for the subcommand and verification command; add a fail-closed dispatch fallback and an exact audit effect regression test. (C-01 / T-TAS-002 F-01.)
2. Bind verification handoffs to task/repo/owner/base/head/command/run/time and invalidate them on any later failure or repository change. (C-02 / T-TAS-002 F-02.)
3. Bind review artifacts to task and submitted head, require reviewer independence/authority, reject empty or stale reviews, and require a recorded PASS before any completion. (C-03 / T-TAS-002 F-03.)
4. Preserve repository ownership through relevant BLOCKED/review states or atomically revalidate/reacquire exclusion on unblock/review failure. (C-04 / T-TAS-002 F-04 / T-TAS-003 O-05.)
5. Immediately document and enforce a one-authoritative-checkout deployment restriction; reject claims from unregistered checkouts until distributed authority exists. (C-05 / T-TAS-003 O-01.)

### P1 — Make state authoritative and recoverable

6. Introduce a validated-store preflight for every mutator; parse/schema/cross-record errors must prevent all writes. (T-TAS-002 F-06.)
7. Enforce dependency completion, current audit SHA, registered repository identity, lane eligibility, worktree/branch cleanliness, and ownership at claim. (T-TAS-002 F-05.)
8. Add claim sessions, heartbeat/expiry, explicit release/transfer, stale diagnostics, and guarded ownership recovery. (T-TAS-003 O-05.)
9. Add task revisions and one authoritative coordination model: transactional service, serialized coordinator bot, or equivalent compare-and-swap authority. (C-05 / T-TAS-003 O-01.)
10. Make task/artifact/event/board updates one recoverable transaction or event-sourced revision; add reconciliation and failure-injection tests. (T-TAS-002 F-07 / T-TAS-003 O-04.)
11. Add a repository/worktree registry and make verify operate on the exact claimed checkout, branch, head, and runner environment. (T-TAS-003 O-02.)
12. Add clean-clone bootstrap and explicit target-runner selection; stop inheriting the coordinator virtualenv implicitly. (T-TAS-003 O-03.)

### P1 — Make creation and history safe

13. Make `create` accept complete task data, validate before writing/logging/rendering, capture creator identity, and reject semantic placeholders. (T-TAS-001 P-04.)
14. Replace three-character/max-active ID allocation with immutable collision-safe IDs checked across active/archive/artifacts/logs. (T-TAS-001 P-03.)
15. Replace global archive sweep with selected/dry-run/collision-refusing, event-logged, recoverable archival that preserves task-artifact history. (T-TAS-002 F-08 / T-TAS-003 O-07.)

### P2 — Align the operating contract

16. Publish a canonical role-to-command/authority matrix for Coordinator, Scout, PM, Worker, Reviewer/Auditor, and Human. (T-TAS-001 P-02.)
17. Reconcile README/help/schema for all commands, states, lanes, manual artifact steps, deployment limits, and accurate maturity language. (T-TAS-001 P-01/P-05/P-07/P-08 and T-TAS-002 F-10.)
18. Move generated-board publication to a serialized authority or CI; make freshness verifiable and treat `TASKS.md` as a rebuildable view. (T-TAS-001 P-06 / T-TAS-003 O-06.)
19. Add standalone end-to-end, negative, concurrency, interruption, archive, worktree, environment, and evidence-binding tests in CI. (T-TAS-003 O-08 and all T-TAS-002 critical findings.)
20. Add structured transition/run observability, stale-owner diagnostics, event reconciliation, log retention/redaction, and auditable cost provenance. (T-TAS-003 O-09.)

## Verification record

- Baseline `fleet lint`: passed before task creation.
- Scout task creation: `30dea3b`; commit contains only T-TAS-001..003.
- Hardened task definitions: `0fc849c`; off-fleet/session-level independent specification and quality reviews passed.
- PM audit SHA: `0fc849c6e987b52bef3e49f7811052dfa076d081`.
- PM audit results: three commands, each exit `0`, no output, no state/event change.
- Evaluation reports: committed together at `3275c78` after off-fleet/session-level independent spec and quality review loops.
- Report whitespace/headings/tables: passed.
- Restricted-zone diff after isolated baseline `9d48816`: none.
- Live task state: all three `T-TAS-*` tasks remain `OPEN`; no T-TAS handoff/review file, CLOSE event/state, or archived task record exists.
- Engine files changed by this evaluation: none.

## Final assessment

The repository has the right bones and a healthy feedback culture, but its safety story is presently stronger in prose and schema shape than in effect-level enforcement. The audit no-op alone makes the current lifecycle unusable; the forged-evidence, unbound-review, duplicate-ownership, and clone-concurrency findings make bypassing that blocker unsafe.

Fix the P0 cluster first, prove each transition's effects and failure semantics in an isolated end-to-end suite, then address authoritative coordination and transactionality. Until then, treat `task_coordinator` as an evolving local task registry—not yet the engine that can safely govern the full Dollers fleet.
