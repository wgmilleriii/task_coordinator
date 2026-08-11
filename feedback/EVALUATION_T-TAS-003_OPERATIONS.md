# T-TAS-003 Operational and Concurrency Safety Evaluation

## Executive verdict

**DONE_WITH_CONCERNS.** At repository SHA `0fc849c6e987b52bef3e49f7811052dfa076d081`, the coordinator provides a useful but narrow local safety property: cooperative fleet commands using the same POSIX checkout are serialized by one command-wide `fcntl.flock`, and an individual task file or generated board replacement is atomic on a local filesystem. The same-checkout lock was reproduced successfully, including automatic kernel-lock release after the holder exited.

The implementation is not a safe distributed fleet authority. A second checkout on the same host proceeded while the first checkout's lock was held; independent machines/clones therefore have no mutual exclusion. Fleet commands never fetch, commit, push, or perform compare-and-swap against Git. Every canonical task/state mutation still rewrites tracked `TASKS.md`, so branches and clones retain a shared merge hotspot. Shared spoke checkouts also remain vulnerable to branch/worktree interference that the coordinator lock does not cover.

Deployment and recovery are also incomplete. A clean clone's documented wrapper exits `127` because `.venv` is absent. This evaluation worktree's `.venv` is a symlink to the primary checkout's virtualenv, so it resolves to the shared primary-checkout interpreter; verification then inherits that coordinator environment instead of selecting the target repository's environment. A worktree test showed that verification for `repo: task_coordinator` resolves the primary sibling checkout rather than the current worktree. A forced render failure returned nonzero only after the new task and its global event had already been persisted, proving transitions are not multi-file transactions and have no rollback/recovery journal.

The reported PM blocker—`fleet audit` having silently left T-TAS-003 `OPEN`—was not retested or worked around because this evaluation was forbidden to audit or transition the task. Audit dispatch and transition-effect enforcement belong to **T-TAS-002**. Documentation and guarantee-language inconsistencies belong to **T-TAS-001**.

## Scope and evidence

**Repository SHA:** `0fc849c6e987b52bef3e49f7811052dfa076d081`

**Evaluation timestamp:** `2026-08-10T18:23:48-06:00`

**Evaluation checkout:** `/private/tmp/task_coordinator_self_evaluation/task_coordinator`

**Initial dirty state:** tracked `TASKS.md` modified; `.venv/` and `logs/` untracked. These were pre-existing and were not altered intentionally by the evaluation.

**Write scope:** only this report was created in the evaluation checkout. No fleet task was claimed, audited, or transitioned; no restricted file was modified; no commit was made.

Inspected implementation and state:

- `AGENTS.md`, `README.md`, `.gitignore`, `requirements.txt`, `bin/fleet`, and all of `bin/fleet.py`;
- all three schemas; active T-TAS task records; current `TASKS.md`; global event log; current archived task, handoff, and review examples;
- Git SHA/history/remotes/branch/worktree metadata and the presence or absence of tests/CI;
- exactly the seven prior-feedback files named in T-TAS-003.

Executed read-only commands included `pwd`, `git rev-parse HEAD`, `git status --short`, `git log`, `git remote -v`, `git worktree list --porcelain`, `git ls-files`, `rg`, `find`, `nl`, `.venv/bin/python --version`, and package/interpreter introspection. Mutating and concurrency experiments used only these unique fixtures:

- `/private/tmp/tas003-bootstrap.kyEX9U`
- `/private/tmp/tas003-lock.LrguCk`
- `/private/tmp/tas003-worktree.jVz3IC`
- `/private/tmp/tas003-failure.xxEruB`

| Scoped topic | Method / files / commands | Result | Evidence | Tested status |
|---|---|---|---|---|
| Runtime isolation | Static inspection of `bin/fleet.py:606-693`; same-checkout and second-checkout lock fixtures | One global command lock exists per checkout; it does not isolate target-repo files, branches, or other checkouts | `lock_path = BASE_DIR/.fleet.lock`; every command dispatch occurs inside the lock, but the path is checkout-local | Tested, static + execution |
| Single-process guarantees | Inspected save/render/log and every multi-file command | Individual task/board replacement is atomic; whole operations are not transactional or durable against power loss | `save_task` and render use temp + `os.replace`; handoff/review/log writes are direct; there is no explicit file `fsync`, directory `fsync`, journal, revision, rollback, or durable multi-file commit | Tested, static + failure injection |
| Same-host multi-process | Held `.fleet.lock` with one process, then ran `fleet.py lint` in the same fixture | Second command failed immediately with exit `1`; after holder exit, lint succeeded | Output: `Could not acquire lock`; then `All ... passed strict schema validation` | Tested |
| Shared-filesystem behavior | Inspected `fcntl` design and tested only local APFS/temp filesystem | Same exact checkout should serialize cooperative POSIX processes when the filesystem honors advisory locks; NFS/SMB/container-volume semantics are neither specified nor tested | `fcntl.flock(LOCK_EX \| LOCK_NB)` is advisory and POSIX-specific; no filesystem capability check | Partially tested; remote/shared FS not tested |
| Multi-machine coordination | Held first clone's lock and ran lint in a second clone; inspected all Git calls | Second clone succeeded while first lock was held. No central transaction, remote lease, fetch/push, or serialized bot exists | Independent `.fleet.lock` paths; Git is used only inside verify to ask for branch | Tested, same-host independent-clone proxy + static |
| Current `fcntl` behavior | Lock holder/crash-release fixture; `bin/fleet.py:659-666` | Correctly excludes a concurrent cooperative command in one checkout and releases on process exit. It is nonblocking, has no queue/retry/holder metadata, and covers even a 300-second verify | Lock rejection is immediate; a later lint succeeds despite the empty lock file remaining | Tested |
| Shared worktree / branch risks | Read `AGENTS.md`, `README.md`, Worker-1 evidence; inspected repo-lock states in `cmd_claim` | Engine self-modification now mandates a worktree, but spoke workers are still told to create a generic `test` branch. The coordinator does not create/record a worker worktree or protect the spoke checkout from branch switches | `README.md` step 3; Worker-1 recorded an actual branch switch and mid-edit file replacement; claim exclusion ends at `PEER_REVIEW` | Static + prior executed incident; not destructively retested |
| Worktrees versus verify sibling resolution | Created isolated Git worktree and imported its `fleet.py` path calculation | In `task_coordinator_upgrade`, `repo: task_coordinator` resolved to the primary `.../task_coordinator`, not the active upgrade worktree | `BASE_DIR=.../task_coordinator_upgrade`; `VERIFY_TARGET=.../task_coordinator`; code at `bin/fleet.py:343-344` | Tested |
| `.venv` interpreter behavior | Inspected wrapper, `.venv` symlink, and primary-checkout `pyvenv.cfg`; ran interpreter introspection | Wrapper unconditionally sources checkout `.venv`; in this worktree that path is a symlink to the primary checkout's virtualenv, so verify inherits the shared primary-checkout PATH | `readlink .venv` returned `/Users/willismiller/Documents/GitHub/task_coordinator/.venv`; `sys.executable` resolved there; Worker-1 observed target dependency failure | Tested + prior executed incident |
| Requirements / bootstrap | Inspected `requirements.txt` and README; ran wrapper in clean local clone | Exact version pins and RFC3339 dependency exist, but no venv creation step, Python version, hashes, package metadata, or actionable wrapper fallback exists. Clean clone exited `127` | Missing `.venv/bin/activate`, then `python: command not found` | Tested |
| Atomic individual writes | Inspected `save_task` and render | Task and board destination replacement is locally atomic and protected from same-checkout temp-name collisions by the global lock | `bin/fleet.py:39-45`, `153-237` | Static |
| Multi-file writes / failure recovery | Blocked `TASKS.md.tmp` in a fixture, then ran `create` | Command exited `1` after printing success; task YAML and global log existed while `TASKS.md` lacked the task | `T-FIX-001.yaml` and log event persisted; render raised `IsADirectoryError` | Tested |
| Generated-board contention | Inspected every canonical task/state mutator and Git tracking | Same-checkout writes are serialized, but every canonical task/state mutation renders tracked `TASKS.md`; independent branches/clones can conflict and publish stale boards | `cmd_render` calls at create/audit/claim/submit/record-review/block/unblock/close/archive; verify and start-review mutate artifacts/logs without rendering; `git ls-files TASKS.md` | Static + independent-clone lock test |
| TASKS.md/log contention | Inspected render and `log_global_event`; current Git state | Local fleet writes share the lock, but board is tracked while `logs/fleet.jsonl` is untracked and append-only. Independent checkouts create divergent boards/logs | `.gitignore` ignores `.fleet.lock` but not logs; current logs are untracked | Static |
| Logging and event observability | Inspected log functions, task events, current three-line log | UTC JSONL/task events are useful beginnings, but lack transition ID, prior/new state, checkout/host/PID/session, branch/SHA, duration, result, and error details. Render/lint/archive/lock rejection are not logged | `bin/fleet.py:47-70`; current log contains only three `CREATE` events | Static |
| Stale OS locks / recovery | Lock holder exited; reran lint | Kernel lock releases automatically, so an empty stale lock file does not block. There is no crash journal or reconciliation for partial writes | Post-holder lint exit `0`; partial-create fixture remained inconsistent | Tested |
| Claim leases / stale task locks | Inspected schema and claim/review/block/unblock commands | `claimed_at` is recorded, but no heartbeat, lease expiry, unclaim/release, stale warning, or recovery exists. Claim exclusion ignores review and BLOCKED ownership; unblock restores the prior status without reacquiring exclusion | `schemas/task.schema.json:22`; `cmd_claim` checks only `CLAIMED`/`IN_PROGRESS`; `cmd_block` stores `previous_status`, while `cmd_unblock` restores it without a repo-lock recheck | Static |
| Archive operational scope | Inspected `cmd_archive`, active-dependency lint, archived T-MIN-004 and its artifacts | Archive is an all-repo sweep with no task/repo filter, dry run, event, collision check, batch transaction, or artifact bundling. `os.replace` can overwrite an existing same-ID archive; active dependency lookup excludes archives | `bin/fleet.py:589-604`; T-MIN-004 task is archived while its handoff/review remain in top-level directories | Static |
| Cost observability | Inspected handoff schema/data and render | Burn-rate sum exists, but token/cost are nullable, manual, unconstrained, and currently null; malformed handoffs are silently skipped; no budgets or breakdowns exist | `schemas/handoff.schema.json:17-18`; `bin/fleet.py:157-182`; both current handoffs have null cost/token | Static |
| Automated operational regression coverage | Searched for standalone tests/config and `.github` files; inspected inline lint self-test | No standalone coordinator test suite, operational regression coverage, test configuration, or CI workflow exists beyond `cmd_lint`'s inline RFC3339 self-test | `find` returned no standalone test/config/CI files outside `.venv`; `bin/fleet.py:82-88` contains the inline date-format guard | Tested by inventory + static inspection |

Guarantee boundary:

| Execution model | Current guarantee |
|---|---|
| Single process | Sequential Python execution; individual task and board replacement is atomic, but multi-file state/log/view changes can partially commit. |
| Same-host, multiple cooperative fleet processes, same checkout | Mutually exclusive due to `fcntl.flock`; losers fail immediately. Manual file edits, Git branch switches, and target-repo mutations are outside the lock. |
| Shared filesystem, same checkout | Potentially the same as above only if the mounted filesystem correctly supports POSIX advisory locks for all clients. This is undocumented and untested; non-cooperating writers bypass it. |
| Same host or shared filesystem, different checkouts/worktrees | No mutual exclusion because each checkout has its own `.fleet.lock`; tracked board and task state diverge. |
| Multiple machines / independent clones | No coordination guarantee. Git remote presence supplies history only; fleet commands do not synchronize or arbitrate transitions. |

## Confirmed strengths

- The global lock is held around the complete command dispatch, so the original same-checkout claim TOCTOU race is closed for cooperative local processes. The kernel releases the lock on process exit; a leftover `.fleet.lock` pathname is not itself a stale lock.
- Task YAML and `TASKS.md` use same-directory temporary files followed by `os.replace`, protecting the destination from ordinary partial truncation on a local filesystem.
- Per-task YAML materially reduces canonical-record conflicts compared with one monolithic board, even though the generated tracked board still limits that benefit.
- `claimed_at`, embedded task events, global UTC JSONL events, handoff token/cost fields, and the rendered burn-rate total are useful primitives for future recovery and observability.
- `requirements.txt` now pins the coordinator dependencies and includes `rfc3339-validator`; the installed evaluation interpreter matched the listed PyYAML/jsonschema/RFC3339 versions.
- `AGENTS.md` now explicitly requires isolated worktrees for engine changes, a meaningful improvement over switching branches in the primary coordinator checkout.

## Findings

### CRITICAL O-01 — Coordination stops at one checkout; independent clones and machines can both act

`bin/fleet.py:659-666` locks `BASE_DIR/.fleet.lock`. In the concurrency fixture, a second process in that checkout was rejected, but a process in `task_coordinator_second` completed lint successfully while the first clone's lock was held. Fleet code contains no fetch, push, remote compare-and-swap, central API, database transaction, or distributed lease. The only Git subprocess (`bin/fleet.py:358-360`) asks for the verification target's branch.

Consequently, the lock is not “single-machine” in the broad sense; it is **single-checkout**. Two checkouts on one host, two worktrees, or two machines can read the same remote snapshot and make incompatible transitions. Later Git conflicts are detection after mutation, not repository-wide claim arbitration, and different task files can merge despite violating the one-active-task-per-repo invariant.

### MAJOR O-02 — Worktree-aware execution is absent, and verify can target the wrong checkout

Verification derives its target solely as `abspath(BASE_DIR/../task.repo)` (`bin/fleet.py:343-344`). In an isolated worktree named `task_coordinator_upgrade`, the computed path for `repo: task_coordinator` was the primary sibling `task_coordinator`, not the current worktree. The two directories were on different branches (`tas003-worktree-test` versus `test/self-evaluation-execution-...`). A verification run could therefore test the untouched primary checkout and report success for changes present only in the worktree, or interfere with another agent's primary checkout.

For ordinary spokes, this convention also fails when a coordinator worktree is placed under a temporary parent without matching sibling repositories. There is no registered repo path, claimed worktree path, branch policy, or worktree identity in task/handoff state. This compounds Worker-1's prior observed branch switch and mid-edit replacement in a shared spoke checkout.

### MAJOR O-03 — The wrapper and verification environment are neither clean-clone-safe nor target-repo-aware

`bin/fleet` unconditionally sources `$checkout/.venv/bin/activate` and then invokes `python`, without `set -e` or an existence/actionability check. A clean isolated clone printed both “No such file or directory” and “python: command not found” and exited `127`. README says to install requirements but does not instruct agents to create `.venv`, state a Python version, or explain worktree setup.

The evaluation worktree's `.venv` symlinks directly to `/Users/willismiller/Documents/GitHub/task_coordinator/.venv`; after activation, `sys.executable` resolved to that shared primary-checkout interpreter. `cmd_verify` then runs `shell=True` with the inherited environment (`bin/fleet.py:351-353`). It does not select the target repo's venv or a task-declared runner. Worker-1 already reproduced the result: code passed manually in the spoke environment but fleet verification failed because Flask was absent from the coordinator venv. The CLI also neither prints nor records the actual executable/environment.

### MAJOR O-04 — Commands can report and persist partial success with no transaction or recovery path

Individual `os.replace` calls do not make task, handoff/review, global event, embedded event, and board updates atomic as a unit. In the failure fixture, a directory at `TASKS.md.tmp` forced render to fail. `fleet create` first printed `Created new task T-FIX-001`, then exited `1` with `IsADirectoryError`; `tasks/active/T-FIX-001.yaml` and its JSONL event existed, while `TASKS.md` had no T-FIX-001 entry.

Other transitions often append the global event before replacing the task and then render afterward (`audit` at lines 293-298; claim at 319-324; submit at 430-441). Handoff/review files are written directly rather than via atomic replacement. No transition ID, write-ahead journal, rollback, reconciliation command, unique temp file, file/directory `fsync`, or task revision exists. A crash can therefore leave phantom events, stale views, or task/artifact status disagreement.

### MAJOR O-05 — Task ownership has no lease/recovery and is released at the wrong lifecycle boundary

The hardening pass added `claimed_at`, but no command reads it. There is no heartbeat, lease expiry, stale-claim warning, session ID, unclaim/release, ownership transfer, or abandoned-work recovery. A CLAIMED/IN_PROGRESS task can lock its repo indefinitely until someone manually changes state.

Conversely, `cmd_claim` treats only `CLAIMED` and `IN_PROGRESS` as repo locks (`bin/fleet.py:310-313`). It releases exclusion at `PEER_REVIEW`, although a failed review returns the original task to `IN_PROGRESS`; another task may already have claimed and mutated the same spoke checkout.

BLOCKED has the same hazard with an additional restoration race. If task A moves from CLAIMED to BLOCKED, `cmd_block` stores `previous_status: CLAIMED` but the BLOCKED task no longer excludes claims (`bin/fleet.py:524-540`). Task B can then claim the same repository. `cmd_unblock` restores A directly to CLAIMED without rechecking or reacquiring repository exclusion (`bin/fleet.py:542-562`), leaving two CLAIMED tasks for one repo despite each command individually holding the process lock. The process lock therefore serializes the creation of an invalid ownership state rather than preventing it. It is also held during the entire verification subprocess (up to 300 seconds), so unrelated local commands fail immediately rather than queue, and the rejection gives no holder/PID/task or retry guidance.

### MAJOR O-06 — Tracked `TASKS.md` remains a cross-branch/clone contention and stale-view surface

Every canonical task/state mutation command calls `cmd_render`, and `TASKS.md` is tracked by Git. (`verify` and `start-review` mutate evidence/review artifacts and logs but do not mutate canonical task state or render the board.) The checkout-local lock prevents simultaneous local writers, and temp+replace prevents partial file contents, but neither prevents different branches/clones from regenerating the same tracked artifact. Agents changing distinct task YAML files can still conflict on the board, while a partial transition can leave it stale as reproduced in O-04. The README's claim that per-task files support massive parallelism therefore exceeds the implementation; documentation ownership belongs to T-TAS-001.

### MAJOR O-07 — Archive is a destructive, global, non-transactional sweep rather than recoverable history

`cmd_archive` (`bin/fleet.py:589-604`) moves every active `DONE`, `CANCELLED`, or `DEFERRED` task across all repositories. It has no task/repo selector, dry run, authorization/actor, event, collision guard, rollback, or atomic batch boundary. `os.replace(source, dest)` overwrites an existing same-name archive. Since ID generation scans active tasks only, the related ID-reuse risk is owned by T-TAS-001, but archive provides no last line of defense.

Archive also moves only the task YAML. T-MIN-004 demonstrates that its task is under `tasks/archive/` while handoff/review artifacts remain in shared top-level directories with no stable references in the task. Active dependency validation considers only active IDs (`bin/fleet.py:113-118`), so archiving a completed dependency can make an active dependent appear dangling. A failure during the loop leaves a partially archived batch and stale board; no archive action is recorded in the global log.

### MAJOR O-08 — Core operational guarantees lack standalone regression and CI coverage

The repository has one inline test-like guard: `cmd_lint` deliberately validates a known-invalid RFC3339 timestamp and fails if the optional format checker is inactive (`bin/fleet.py:82-88`). Beyond that guard, there is no standalone coordinator test suite, pytest/tox/pyproject test configuration, operational regression coverage, or `.github` CI workflow. The lock, worktree resolution, wrapper bootstrap, interruption recovery, deterministic render, archive collision, lease behavior, BLOCKED ownership restoration, and distributed-boundary assumptions therefore have no executable safety net. The prior review-bridge crash and current audit silent no-op show why smoke-testing command existence is not sufficient; effects and failure semantics need assertions. Transition-effect testing belongs jointly with T-TAS-002.

### MINOR O-09 — Logging and cost telemetry are not yet an auditable operational record

Global JSONL events include only timestamp/action/actor and optional task/details. They omit transition ID, old/new state, result/exit code for most commands, checkout/host/PID/session, branch/SHA, duration, and error/recovery linkage. Lint/render/archive/lock rejection and most exceptions are not logged. Logs are currently untracked, with no rotation, query command, retention, redaction, or centralized sink; separate clones produce separate histories.

`token_spend` and `cost_usd` are nullable manual handoff fields with no nonnegative constraint or provenance. Both current handoffs contain nulls. Render silently skips malformed handoffs while labeling the aggregate “All Time,” and provides no repo/model/time breakdown, budget, or alert. This is presentation telemetry, not cost accounting.

### MINOR O-10 — Lock portability and availability semantics are undocumented

`fcntl` is POSIX-only and advisory. There is no Windows fallback, filesystem capability check, shared-mount validation, blocking/wait mode, timeout, fairness, or stale-holder diagnostic. Local crash release is sound, but the code and README do not distinguish that kernel lock from indefinite task ownership. These limits should be explicit before shared-filesystem deployment.

Transition/evidence enforcement findings encountered during operations—malformed-store fail-open behavior, audit no-op/effect enforcement, evidence binding, review transitions, and audited-SHA freshness—are intentionally cross-referenced to **T-TAS-002** rather than duplicated. Role/README/CLI guarantee inconsistencies are cross-referenced to **T-TAS-001**.

## Prior feedback disposition

The required prior corpus was limited to exactly the seven named files. “Fixed” means demonstrated in the current implementation; “partially fixed” means a narrower control exists but the original fleet-level guarantee does not; “still present” means direct current evidence remains; “not retested” is used where this evaluation intentionally avoided another domain's mutation.

| Prior source and domain-relevant finding | Disposition | Current evidence |
|---|---|---|
| `FEEDBACK_Antigravity.md` — `TASKS.md` recreates merge conflicts | **Partially fixed** | Same-checkout writes are locked/atomic, but every canonical task/state mutator still rewrites tracked `TASKS.md`; clones/branches are independent. |
| `FEEDBACK_ClaudeFable.md` — coordinator was not a Git repo / had no durable history | **Fixed** | Git history and `origin` exist. Fleet commands still do not synchronize with the remote. |
| `FEEDBACK_ClaudeFable.md` — claim race and no timestamp | **Partially fixed** | Global `flock` closes cooperative same-checkout race; `claimed_at` is written. Different checkouts race, and timestamp has no lease/expiry logic. |
| `FEEDBACK_ClaudeFable.md` — stale claims cannot be detected/released | **Still present** | No heartbeat, expiry, warning, unclaim, or release command reads `claimed_at`. |
| `FEEDBACK_ClaudeFable.md` — no archive mechanics / DONE board bloat | **Partially fixed** | `archive` exists, but is global, non-transactional, unlogged, collision-prone, and leaves artifacts separate. |
| `AUDIT_ClaudeFable_20260810T1640-0600.md` — task/board atomic writes | **Partially fixed** | Both use temp+replace and same-checkout lock; no fsync or multi-file transaction. Failure injection produced task/log/view divergence. |
| `AUDIT_ClaudeFable_20260810T1640-0600.md` D-1 — RFC3339 date validator dependency missing / format check silently inactive | **Fixed** | `requirements.txt:7` pins `rfc3339-validator==0.1.4`; the installed evaluation interpreter imported version `0.1.4`, and `cmd_lint` includes a known-invalid date self-test at `bin/fleet.py:82-88`. |
| `AUDIT_ClaudeFable_20260810T1640-0600.md` D-6 — claim race | **Partially fixed** | Exactly one same-checkout fleet process enters; a second clone proceeds independently. No distributed arbitration. |
| `AUDIT_ClaudeFable_20260810T1640-0600.md` D-4 — add `claimed_at` and stale-claim handling | **Partially fixed** | Field/write added; stale detection and release remain absent. |
| `AUDIT_ClaudeFable_20260810T1640-0600.md` D-5 — model/branch provenance | **Partially fixed** | `--model` is required and branch is queried, but verify can query the wrong sibling checkout and still requires manual head SHA; evidence enforcement is T-TAS-002. |
| `AUDIT_ClaudeFable_20260810T1640-0600.md` — no archive | **Partially fixed** | Command added with O-07 limitations. |
| `AUDIT_ClaudeFable_20260810T1640-0600.md` — fixed 300-second verification timeout | **Still present** | `subprocess.run(... timeout=300)` is hard-coded and the global lock is held throughout. |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` — not a Git repository | **Fixed** | Repository and remote exist. |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` — file store lacks transactions/distributed authority | **Still present** | No journal, revision/CAS, DB/service/bot, or Git synchronization; partial-write fixture reproduced inconsistency. |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` — generated board merge hotspot | **Partially fixed** | Local writer serialization exists; cross-branch/clone conflict remains. |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` — claim TOCTOU and two-file transaction | **Partially fixed** | Local TOCTOU closed; multi-file and distributed races remain. |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` — free-form repository identity/path | **Still present** | Verify still assumes `BASE_DIR/../repo`; worktree fixture resolved the wrong checkout. |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` — a Git SHA does not capture dirty-worktree provenance | **Still present** | Audit/claim do not inspect target worktree cleanliness; verify queries only the branch and does not record dirty state (`bin/fleet.py:278-327`, `358-360`). |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` — claim leases/stale ownership absent | **Partially fixed** | `claimed_at` exists; lease, heartbeat, session, expiry, and release do not. |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` — archive absent | **Partially fixed** | Sweep exists but does not preserve a collision-safe, transactionally linked artifact bundle. |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` — no automated tests | **Still present, qualified** | An inline RFC3339 self-test exists in `cmd_lint`, but no standalone suite, operational regression coverage, test configuration, or CI was found. |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` — dependency installation unreproducible | **Partially fixed** | Exact requirements were added; clean-clone wrapper still exits `127`, with no venv/bootstrap/package metadata. |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` — `.gitignore` absent | **Fixed** | `.venv`, caches, bytecode, `.DS_Store`, and `.fleet.lock` are ignored. Logs/temp artifacts remain policy gaps. |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` — writes not atomic | **Partially fixed** | Task/board replace atomically; handoff/review/log and multi-file operations do not. |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` — status/lock/age observability weak | **Partially fixed** | Mermaid/status/blocked reason/events were added; stale locks, aging, ownership sessions, and actionable views remain absent. |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` — verification shell/environment boundaries undefined | **Still present** | `shell=True`, inherited coordinator venv/environment, unrestricted output, and no redaction/runner declaration remain. Evidence authority is T-TAS-002. |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` — choose shared-FS/service/serialized-Git arbitration | **Still present** | No deployment model or authority is selected/implemented. |
| `AUDIT_Codex_GPT5_20260810T164505-0600.md` — requirements added but clean clone fails | **Still present** | Reproduced exit `127` in a clean clone. |
| `AUDIT_Codex_GPT5_20260810T164505-0600.md` — no lock/fsync/unique temp/multi-file transaction | **Partially fixed** | Same-checkout lock added; fsync/revisions/transaction remain absent. Fixed temp names are safe only under that one lock. |
| `AUDIT_Codex_GPT5_20260810T164505-0600.md` C-07 — concurrent claims | **Partially fixed** | Same checkout excluded; second checkout unaffected. |
| `AUDIT_Codex_GPT5_20260810T164505-0600.md` C-08 — wrapper unusable in clean clone | **Still present** | Current clean-clone output matches the prior failure. |
| `AUDIT_Codex_GPT5_20260810T164505-0600.md` H-05 — capture verification provenance | **Partially fixed** | Actual branch and model now captured; target checkout may be wrong, and HEAD/dirty/timing/coordinator SHA are absent. Remaining evidence binding is T-TAS-002. |
| `AUDIT_Codex_GPT5_20260810T164505-0600.md` H-06 — unrestricted shell verification | **Still present** | `shell=True`, inherited environment, 300-second fixed timeout, and unbounded captured output remain. |
| `AUDIT_Codex_GPT5_20260810T164505-0600.md` H-08 — no claim timestamp/lease | **Partially fixed** | Timestamp added; lease/recovery absent. |
| `AUDIT_Codex_GPT5_20260810T164505-0600.md` H-11 — repo lock releases at review | **Still present** | Claim exclusion still checks only CLAIMED/IN_PROGRESS. |
| `AUDIT_Codex_GPT5_20260810T164505-0600.md` H-13 — multi-file transitions not atomic | **Still present** | Failure injection confirmed partial durable state. |
| `AUDIT_Codex_GPT5_20260810T164505-0600.md` H-14 — generated board hotspot | **Still present across branches/clones** | Every canonical task/state mutation renders the tracked board; verify and start-review are the non-state-rendering exceptions. |
| `AUDIT_Codex_GPT5_20260810T164505-0600.md` H-15 — no coordinator tests | **Still present, qualified** | `cmd_lint` has an inline RFC3339 self-test; no standalone coordinator suite, operational regression coverage, test configuration, or CI exists. |
| `FEEDBACK_ClaudeFable_claude-fable-5_20260810.md` — D-6 fixed for single machine, distributed deferred | **Partially fixed / scope corrected** | It is fixed for cooperative processes in one checkout, not every process on one machine; independent-clone execution succeeded. Distributed remains absent. |
| `FEEDBACK_ClaudeFable_claude-fable-5_20260810.md` — add an end-to-end selftest | **Still present** | The inline RFC3339 lint guard is not an end-to-end lifecycle selftest; no standalone lifecycle/operational suite exists, and the current audit no-op reinforces the need for effect assertions. |
| `FEEDBACK_Worker1_ClaudeSonnet5_20260810.md` — verify uses coordinator Python, not spoke Python | **Still present** | Wrapper activation and inherited PATH are unchanged; current worktree venv also resolves to primary checkout. |
| `FEEDBACK_Worker1_ClaudeSonnet5_20260810.md` — no concurrent-agent worktree isolation | **Partially fixed** | AGENTS mandates worktrees for engine upgrades only; README/CLI still provide no per-task spoke worktree isolation. |
| `FEEDBACK_Worker1_ClaudeSonnet5_20260810.md` — auto-archive keeps board small | **Partially fixed / prior observation not supported as automatic** | Explicit `archive` exists, but `record-review` only renders after DONE and does not invoke archive. T-MIN-004's move is not logged, so its trigger cannot be reconstructed. |
| `FEEDBACK_Worker1_ClaudeSonnet5_20260810.md` — print/select actual verification interpreter | **Still present** | Verify prints cwd/command only; handoff does not record executable/environment. |

Out-of-domain prior items were reviewed but are not duplicated here: role authority, CLI examples, README/schema lifecycle drift, `--model` documentation, and maturity wording belong to **T-TAS-001**; malformed-store fail-closed behavior, dependency readiness, stale-audit enforcement, fabricated handoffs, human/peer gates, lane authorization, manual transition bypass, and audit-command effect enforcement belong to **T-TAS-002**. The reported live audit silent no-op is **not retested** and remains a T-TAS-002 blocker.

## Recommendations

Future work, in priority order:

1. Select and document one authoritative coordination model. For real multi-machine use, route transitions through a transactional service or serialized coordinator bot. Add task revisions/expected-revision compare-and-swap; do not treat ordinary Git clones or post-hoc merge conflicts as locks.
2. Add a controlled repository/worktree registry. Record the exact claimed worktree path/identity, branch, HEAD, remote, and dirty state; make verify use that registered checkout and reject mismatches. Create per-task spoke worktrees or require them as a verified claim precondition.
3. Make installation explicit and relocatable: document supported Python, create/bootstrap `.venv`, fail before invocation with one actionable message, and execute the resolved interpreter directly. Declare each verification runner/environment rather than silently inheriting the coordinator venv.
4. Introduce transaction/recovery semantics: one transition ID, staged artifact/task/event writes, unique temp files, explicit file and directory `fsync`, a durable multi-file commit marker or journal, and a reconciliation command. Treat `TASKS.md` as a regenerable view after canonical state commits.
5. Move generated-board publication to one serialized authority/CI path and stop requiring every agent branch to commit it. Add a deterministic render check.
6. Add claim sessions, heartbeat/expiry, explicit release/transfer, stale diagnostics, and recovery policy. Retain repo/path ownership through review and any BLOCKED states that may resume owned work until correction or recovery risk is resolved. Make unblock recheck and atomically reacquire repository/path exclusion before restoring an owned status; refuse or route to an explicit conflict-recovery flow if another task holds it. Give the runtime lock bounded wait/retry and holder metadata.
7. Replace archive sweep semantics with task/repo selection, dry-run output, collision refusal, stable artifact references or bundles, archived-dependency resolution, event logging, and recoverable batch behavior.
8. Upgrade observability to structured transition/result records carrying old/new state, task revision, run ID, host/session/process, checkout/branch/SHA, start/finish/duration, failure category, and recovery linkage. Centralize/rotate logs for distributed use. Capture cost/token source and budgets rather than relying on nullable manual fields.
9. Add regression and failure-injection tests for same-checkout and cross-checkout concurrency, wrapper bootstrap, worktree target selection, interpreter selection, interruption at every write boundary, stale leases, review-lock retention, archive collisions/dependencies, deterministic board generation, and event/cost integrity. Run them in CI. T-TAS-002 should add effect-level tests for every transition, including the current audit no-op.
10. State deployment limits explicitly: POSIX-only `fcntl`, advisory-lock requirements, validated filesystem types, one-checkout scope, and the absence of multi-machine guarantees until a distributed authority ships. T-TAS-001 should align README claims with those facts.

## Domain verdict

**DONE_WITH_CONCERNS.** T-TAS-003's evaluation deliverable is complete, but the operational system is suitable only for cautious, cooperative use from one POSIX checkout, with human awareness that multi-file failures can leave inconsistent state. Same-host multi-process locking is confirmed only for that checkout. Shared-filesystem behavior is conditional and unverified. Different worktrees/checkouts and multiple machines have no arbitration. Worktree target selection, interpreter/bootstrap behavior, recovery, archive safety, and observability all require hardening before the coordinator can safely govern a parallel or distributed fleet.
