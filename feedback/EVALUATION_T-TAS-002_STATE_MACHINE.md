# T-TAS-002 State-Machine and Evidence-Integrity Evaluation

## Executive verdict

**FAIL — not safe as a lifecycle or evidence authority.** The audit entry point is completely inert: all three evaluation audit invocations returned exit status 0, printed nothing, and left T-TAS-001 through T-TAS-003 `OPEN`. The cause is an `argparse` destination collision: the subparser name and audit's `--command` option both write `args.command`; dispatch consequently sees the verification string rather than `"audit"` and executes no branch.

That defect blocks every lawful new CLI lifecycle at `OPEN`. Directly seeded later-state fixtures in isolated copies revealed additional fail-open behavior: unmet dependencies and stale audit SHAs are claimable; a non-Git directory can be “verified”; fully fabricated, cross-task handoffs and reviews pass shape validation; stale success evidence survives a later verification failure; non-human-review tasks can skip peer review; human approval defaults to actor `Unknown`; block/unblock can violate the one-claim-per-repository invariant; malformed YAML does not fail lint or stop mutation; failed multi-file transitions can commit state while returning nonzero; and archive can silently overwrite prior history.

No live task was claimed, audited, transitioned, or archived. No engine, schema, documentation, task, handoff, review, log, virtual-environment, or generated-board file was edited. All mutation/adversarial tests ran in unique `mktemp -d` repository copies. The evaluation itself adds only this report.

## Scope and evidence

- Repository SHA: `0fc849c6e987b52bef3e49f7811052dfa076d081`
- Evaluation timestamp: `2026-08-10T18:27:30-06:00`
- Evaluation branch: `test/self-evaluation-execution-20260810T175405-0600`
- Initial expected dirty state: `M TASKS.md`, `?? .venv`, `?? logs/`
- Primary implementation inspected: all 696 lines of `bin/fleet.py`; `bin/fleet`; all three JSON Schemas; `README.md`; `AGENTS.md`; `requirements.txt`; active/archive task examples; current handoff/review examples; Git history; and the exact seven-file prior-feedback corpus.
- Disposable copies: `/private/tmp/tas002-audit.ZXVVci/task_coordinator`, `/private/tmp/tas002-lifecycle.3mlnjl/task_coordinator`, `/private/tmp/tas002-integrity.bLOWdb/task_coordinator`, `/private/tmp/tas002-corrupt.Y15Kgb/task_coordinator`, and `/private/tmp/tas002-archive.FCPvOU/task_coordinator`.
- Direct fixture setup was used only after demonstrating that `fleet audit` cannot transition `OPEN`. Such setup is identified below and never treated as proof that audit works.

| Topic | Method | Files / commands | Result | Supporting evidence | Tested status |
|---|---|---|---|---|---|
| Create | Dynamic in lifecycle copy; static | Five `fleet create`; `fleet lint`; `bin/fleet.py:242-276`; task schema lines 18-19 | Creates unique sequential OPEN files, logs globally, and renders; placeholder scope/DoD are accepted by lint | `T-FIX-001` contained `REQUIRED_PLEASE_FILL`; lint exited 0 | Tested |
| Audit | Three exact-shape dynamic invocations; static parser trace | `fleet audit T-TAS-001..003 --auditor Self-Evaluation-PM --repo-sha 0fc849c... --command 'test -f ...'`; `bin/fleet.py:608,619-623,668-675` | Silent no-op, exit 0, all tasks remain OPEN | Each transcript was only `exit=0`; before/after `status: OPEN` | Tested; central blocker |
| Claim | Dynamic negative and direct-AUDITED positive fixture; static | `claim T-FIX-001`; `claim T-FIX-002`; `bin/fleet.py:301-327` | OPEN status is rejected, but readiness/audit/repository controls are absent | OPEN exited 1; dependent stale-audit task exited 0 and became CLAIMED | Tested with direct setup |
| Dependency readiness | Dynamic | `T-FIX-002.dependencies=[T-FIX-001]`, dependency OPEN; `claim T-FIX-002` | Unmet dependency does not block claim | Claim printed success and exited 0 | Tested with direct setup |
| Stale audit | Dynamic with real fixture Git repo; static | Fixture HEAD `e82d6182...`; task `audited_repo_sha: deadbeef`; claim and verify; `bin/fleet.py:290,338-345` | Neither claim nor verify compares audited SHA with actual HEAD | Claim and verify both exited 0; handoff copied `base_sha: deadbeef` | Tested with direct setup |
| Repository identity | Dynamic non-Git sibling directory; static | `verify T-NOT-001`; `repo: not_git`; `bin/fleet.py:343-360`; task schema line 8 | Any existing sibling path is accepted; Git identity is optional | Verification exited 0 with `branch: Unknown`, `base_sha: definitely-not-a-sha` | Tested with direct setup |
| Verify | Dynamic success and failure; static | `verify T-FIX-002`; `verify T-NOT-001` after command changed to `false`; `bin/fleet.py:329-398` | Status/nonzero gates work; provenance and invalidation do not | Success created handoff; later failure exited 1 but handoff hash remained `58c712d...` | Tested with direct setup |
| Handoff provenance / fabrication | Dynamic fabricated artifact and stale-artifact reuse; static | `handoffs/T-NON-001_handoff.yaml`; `submit`; handoff schema; `bin/fleet.py:409-430` | Schema shape is enforced, origin and task/repo/SHA identity are not | A handoff naming `T-FAKE-999`, attacker, different repo/base, made-up status, one-character SHA submitted | Tested with direct setup |
| Submit | Dynamic missing-placeholder negative, fabricated positive, stale-success positive | `submit T-FIX-002`; `submit T-NON-001`; `submit T-NOT-001`; `bin/fleet.py:400-442` | Placeholder check works; full fake or superseded evidence transitions to PEER_REVIEW | Placeholder exited 1; both bypasses exited 0 | Tested with direct setup |
| Start-review | Dynamic; static | `start-review T-NON-002 --reviewer worker-b --model same-model`; `bin/fleet.py:444-478` | Status gate/template work; owner may self-review and handoff is not validated/bound here | Template used forged handoff head `y`; command exited 0 | Tested with direct setup |
| Record-review | Dynamic fabricated PASS; static | Review changed to `task_id: T-FAKE-997`, unrelated head, empty findings, PASS; `record-review T-NON-002`; `bin/fleet.py:480-522`; review schema | Shape validation works; no cross-record, head, reviewer-separation, or nonempty-findings gate | Lint and record-review exited 0; task reached HUMAN_REVIEW | Tested with direct setup |
| Human review | Dynamic; static | `close T-NON-002` without `--human`; `bin/fleet.py:564-587` | Required status is enforced, but approval is unauthenticated and actor defaults to `Unknown` | Human-required task closed DONE; task/global events record actor `Unknown` | Tested with direct setup |
| Block / unblock | Dynamic; static | block T-FIX-002; claim T-FIX-003; unblock T-FIX-002; repeated block T-FIX-001; `bin/fleet.py:524-562` | Arbitrary-state block and unvalidated restore break invariants | Two same-repo tasks ended CLAIMED; double-block/unblock left status BLOCKED with null reason/history | Tested with direct setup |
| Close | Dynamic; static | `close T-NON-001 --human not-a-reviewer`; `bin/fleet.py:570-585` | For `human_review_required: false`, PEER_REVIEW can go directly to DONE without any review artifact | Close exited 0 before start-review/record-review existed | Tested with direct setup |
| Archive | Dynamic collision; static | Active DONE duplicate of archived `T-MIN-004`; `fleet lint`; `fleet archive`; `bin/fleet.py:589-604` | Archive sweeps terminal states but overwrites an existing archive path and emits no transition event | Archived hash changed `5db9806...` to `7be5b2a...`; title became attacker fixture | Tested with direct setup |
| Lint failure behavior | Dynamic malformed YAML and null audit metadata; static | `BROKEN.yaml`; `T-NULL-001.yaml`; `fleet lint`; `bin/fleet.py:21-37,78-151`; task schema lines 14-20,42-49 | Parse errors are printed then dropped; null conditional metadata passes; mutations continue in known-corrupt store | Malformed lint printed error then green success/exit 0; claim also exited 0; null audit lint exited 0 | Tested |
| Transition logging / atomicity | Dynamic render failure after submit; log inspection; static | Parseable task missing title; `submit T-COR-001`; `bin/fleet.py:39-70,430-442`; event sites throughout | Per-file task replacement is atomic, but transition, artifacts, board, and logs are not one transaction; logging is incomplete | Submit printed success then crashed `KeyError: 'title'`, exit 1, while task+handoff+global log were already PEER_REVIEW/SUBMIT and `TASKS.md.tmp` remained | Tested with direct setup |

The fixed prior-feedback corpus read in full was:

1. `feedback/AUDIT_ClaudeFable_20260810T1640-0600.md`
2. `feedback/AUDIT_Codex_GPT5_20260810T164505-0600.md`
3. `feedback/FEEDBACK_Antigravity.md`
4. `feedback/FEEDBACK_ClaudeFable.md`
5. `feedback/FEEDBACK_ClaudeFable_claude-fable-5_20260810.md`
6. `feedback/FEEDBACK_Codex_GPT5_20260810T163242-0600.md`
7. `feedback/FEEDBACK_Worker1_ClaudeSonnet5_20260810.md`

## Confirmed strengths

- Task and generated-board destination replacement uses a same-directory temp path plus `os.replace` (`bin/fleet.py:39-45,173-237`). This protects each destination from basic partial truncation, though not whole transitions.
- A process-wide nonblocking `fcntl.flock` wraps dispatch (`bin/fleet.py:659-666`). It closes the original same-checkout concurrent CLI race; distributed/shared-worktree concerns belong to T-TAS-003.
- Basic status gates reject obvious illegal entry points: claim refuses OPEN, verify refuses states outside CLAIMED/IN_PROGRESS, submit refuses states outside CLAIMED/IN_PROGRESS, and start/record review require PEER_REVIEW.
- Verification executes in a resolved sibling target path, enforces a 300-second timeout, captures exit code/stdout/stderr, refuses nonzero commands, and records model and detected branch. Completed subprocesses emit VERIFY_PASS or VERIFY_FAIL globally; a timeout returns before recording a failure event or persisted result (`bin/fleet.py:329-398`).
- Submit and lint now load the handoff schema; record-review and lint load the review schema (`bin/fleet.py:120-146,421-428,497-503`). This fixes the earlier complete schema disconnection, even though semantic binding remains absent.
- Peer-review PASS routes human-required tasks to HUMAN_REVIEW and non-human tasks to DONE; FAIL routes back to IN_PROGRESS (`bin/fleet.py:505-515`). The earlier `datetime.UTC` crash is fixed with `timezone.utc` (`bin/fleet.py:8,466`).
- RFC 3339 validation support is installed and guarded by a startup self-test (`requirements.txt:7`; `bin/fleet.py:82-88`). An independent invalid-date validation exited 1 with `'NOT-A-DATE' is not a 'date-time'`.
- Task events and a global JSONL event stream provide useful dual visibility for many transitions. Atomicity, completeness, and actor identity still need hardening.

## Findings

### CRITICAL — F-01: `audit --command` overwrites the dispatch selector, producing silent false success

The root subparser is declared with `dest="command"` (`bin/fleet.py:608`), and the audit option is also `--command` with the default destination `command` (`bin/fleet.py:623`). Dispatch later compares that overwritten attribute to `"audit"` (`bin/fleet.py:668-675`). There is no final unknown-dispatch error, so `main()` returns normally with exit 0.

Isolated reproduction, repeated for T-TAS-001, T-TAS-002, and T-TAS-003:

```text
BEFORE status: OPEN
$ ./bin/fleet audit T-TAS-002 --auditor Self-Evaluation-PM \
    --repo-sha 0fc849c6e987b52bef3e49f7811052dfa076d081 \
    --command 'test -f feedback/EVALUATION_T-TAS-002_STATE_MACHINE.md'
exit=0
AFTER status: OPEN
```

All three commands produced no CLI output beyond the harness's `exit=0`. This is worse than a clean rejection: automation and a PM can interpret success while no audit metadata, task event, global event, board update, or state transition occurs. It also makes the documented OPEN→AUDITED path impossible from the CLI.

### CRITICAL — F-02: Submit accepts fabricated or superseded verification evidence

`cmd_submit` checks the expected filename, rejects only the exact head placeholder, and validates schema shape (`bin/fleet.py:409-428`). It never cross-checks handoff `task_id`, `agent`, `target_repo`, `base_sha`, `head_sha`, `status`, verification command/run, or live repository. The schema itself permits arbitrary status and any nonempty SHA-like string (`schemas/handoff.schema.json:9-14`).

```text
task T-NON-001: id=T-NON-001, repo=nonexistent_repo, base=expected-base, owner=worker-a
handoff file: task_id=T-FAKE-999, target_repo=different_repo, base_sha=wrong-base,
              agent=attacker, status=MADE_UP, head_sha=x,
              evidence_output='fabricated evidence, never verified'
$ ./bin/fleet lint                         # exit=0
$ ./bin/fleet submit T-NON-001             # exit=0
✅ Task T-NON-001 submitted for PEER_REVIEW.
```

A separate test first generated a legitimate success handoff, then changed repository behavior so the next verify failed. The failed run left the prior handoff byte-for-byte unchanged:

```text
successful handoff hash: 58c712d19c2fafd332414cf7f10cab23dda00dac
$ ./bin/fleet verify T-NOT-001 --model fixture
❌ Verification failed (exit code 1).
exit=1
handoff hash afterward: 58c712d19c2fafd332414cf7f10cab23dda00dac
$ ./bin/fleet submit T-NOT-001             # after manual head fill
✅ Task T-NOT-001 submitted for PEER_REVIEW.
exit=0
```

Thus even a coordinator-recorded later failure does not invalidate earlier success evidence.

### CRITICAL — F-03: Peer and human approval artifacts are not bound to the task or an authorized reviewer

`start-review` accepts the task owner as reviewer and copies a head from an unvalidated handoff (`bin/fleet.py:453-474`). `record-review` validates only review shape, then trusts its verdict (`bin/fleet.py:489-520`). The review schema permits an empty findings array and arbitrary nonempty head (`schemas/review.schema.json:9-24`). No task ID, head SHA, reviewer separation, artifact freshness, unresolved-finding, or review-origin comparison occurs.

```text
$ ./bin/fleet start-review T-NON-002 --reviewer worker-b --model same-model
exit=0
# worker-b was also task owner; review was then set to:
task_id: T-FAKE-997
reviewed_head_sha: unrelated-head
verdict: PASS
findings: []
$ ./bin/fleet lint                         # exit=0
$ ./bin/fleet record-review T-NON-002      # exit=0, HUMAN_REVIEW
$ ./bin/fleet close T-NON-002              # no --human
✅ Task T-NON-002 manually closed by Unknown.
exit=0
```

For the default/non-human route, `close` explicitly accepts PEER_REVIEW (`bin/fleet.py:574-576`). `T-NON-001` moved directly from PEER_REVIEW to DONE without start-review or record-review. The human-required path at least requires HUMAN_REVIEW status, but `--human` defaults to `Unknown` (`bin/fleet.py:653`), so it does not prove human action.

### CRITICAL — F-04: Block/unblock can create two simultaneous CLAIMED tasks for one repository

Claim considers repository locks only in CLAIMED/IN_PROGRESS (`bin/fleet.py:309-313`). Block accepts every status, records the prior state, and changes the task to BLOCKED (`bin/fleet.py:524-540`). Unblock restores the saved state without re-running claim locks or any other current-state invariant (`bin/fleet.py:542-562`).

```text
T-FIX-002 CLAIMED in fixture_repo
$ fleet block T-FIX-002 --reason waiting    # BLOCKED, exit=0
$ fleet claim T-FIX-003 --owner second-worker
✅ Successfully claimed T-FIX-003 ...       # exit=0
$ fleet unblock T-FIX-002
✅ ... reverted to CLAIMED.                 # exit=0
final: T-FIX-002=CLAIMED; T-FIX-003=CLAIMED; same repo
```

Repeated block is also accepted. Blocking an already BLOCKED task overwrites `previous_status` with BLOCKED; unblock then “reverts” to BLOCKED while clearing both reason and previous status. Block has no actor argument and logs `Unknown`.

### MAJOR — F-05: Readiness, audit freshness, lane, and repository identity are labels rather than gates

Claim never reads dependencies, lane, audit SHA, target path, Git status, or current branch (`bin/fleet.py:301-327`). Verify constructs `../<repo>` and checks only that the path exists (`bin/fleet.py:343-347`). Audit, if reachable, would copy arbitrary strings without checking the target repository or command (`bin/fleet.py:278-299`).

```text
T-FIX-001 status=OPEN
T-FIX-002 status=AUDITED, dependencies=[T-FIX-001], audited_repo_sha=deadbeef
fixture_repo actual HEAD=e82d6182cf5ccf530849ba4d4532d07c7f2f69e4
$ fleet claim T-FIX-002 --owner worker      # success, exit=0
$ fleet verify T-FIX-002 --model test-model # success, exit=0
handoff base_sha: deadbeef
```

In the repository-identity test, `repo: not_git` resolved to a plain directory. Verification succeeded and wrote `branch: Unknown`, `base_sha: definitely-not-a-sha`. Repo path/runtime security and distributed policy belong to T-TAS-003; documented authority and CLI semantics belong to T-TAS-001.

### MAJOR — F-06: Lint and mutations fail open on an unreadable or semantically invalid store

`load_all_tasks` catches parse errors, prints them, and discards the record (`bin/fleet.py:21-37`). `cmd_lint` only sees returned records, so it can report green and exit 0 after an error. No mutator runs a strict full-store preflight.

```text
$ fleet lint
❌ BROKEN.yaml: Failed to parse YAML - ...
✅ All active tasks, handoffs, and reviews passed strict schema validation.
exit=0
$ fleet claim T-COR-001 --owner worker
❌ BROKEN.yaml: Failed to parse YAML - ...
✅ Successfully claimed T-COR-001 for worker.
exit=0
```

An AUDITED record with `audited_at`, `audited_by`, `audited_repo_sha`, and `verification_command` all null also passed lint. The conditional requires those keys but does not refine their base `string | null` types (`schemas/task.schema.json:14-20,42-49`). Cross-record lint ignores archive IDs and artifact/task identity. Render likewise does not validate before indexing required fields.

### MAJOR — F-07: Multi-file transitions and their logs are not atomic

Individual task writes use `os.replace`, but submit writes the handoff directly, appends a global log, replaces the task, and only then renders (`bin/fleet.py:430-442`). A parseable unrelated task missing `title` forced render to fail after all authoritative state changes:

```text
BEFORE task=CLAIMED, handoff=VERIFIED_LOCALLY
$ fleet submit T-COR-001
✅ Task T-COR-001 submitted for PEER_REVIEW.
Traceback ... bin/fleet.py:194 ... KeyError: 'title'
exit=1
AFTER task=PEER_REVIEW, handoff=PEER_REVIEW, global SUBMIT log exists,
      TASKS.md is stale and TASKS.md.tmp remains
```

The caller sees failure even though the transition committed. Conversely, global events are appended before task save in several commands, so later write failure can record a transition that never committed. Task events omit CREATE, VERIFY, START_REVIEW, and ARCHIVE; archive emits neither task nor global events. `last_transition` is defined in schema but never written. Log append has no durable transaction with task/artifact state (`bin/fleet.py:47-70`).

### MAJOR — F-08: Archive can silently destroy a prior canonical task record

Archive scans only active tasks and uses `os.replace(source, dest)` without checking whether the destination exists (`bin/fleet.py:589-600`). Lint does not compare active IDs with archive IDs. In the isolated test, a different active DONE `T-MIN-004` passed lint and overwrote the existing archived record:

```text
archive before: hash=5db980618a82..., title='Zodiac batch brief ...'
$ fleet lint       # exit=0
$ fleet archive    # 'Archived 1 tasks.', exit=0
archive after:  hash=7be5b2a1c93b..., title='Replacement record overwrites archive'
```

The prior archive was not retained elsewhere by the command, and no archive event was written. Handoffs/reviews are not cross-linked to an immutable archived task version.

### MINOR — F-09: Create produces placeholder records that strict lint certifies

Create deliberately writes `REQUIRED_PLEASE_FILL` for scope and definition of done (`bin/fleet.py:260-270`). The schema requires only nonempty string arrays, so immediate lint returns green. This is internally consistent with the prompt to edit afterward, but “strict schema validation” can certify a task that is not dispatch-ready. Direct YAML editing remains required after create; CLI/documentation design ownership belongs to T-TAS-001.

### MINOR — F-10: The declared state set still lacks coherent command ownership

The schema includes DRAFT, IN_PROGRESS, DEFERRED, and CANCELLED, but no start, defer, or cancel commands exist. IN_PROGRESS is reached only through peer-review FAIL. Block can wrap terminal DONE or any other state; unblock trusts stale `previous_status`. Close accepts non-human PEER_REVIEW directly. No command enforces lane eligibility or actor role; “PMs only” is help text. These gaps compound the concrete bypasses above.

## Prior feedback disposition

Abbreviations: **AG** = Antigravity; **CF1** = `FEEDBACK_ClaudeFable.md`; **CF2** = `AUDIT_ClaudeFable_20260810T1640-0600.md`; **CF3** = dated Claude gauntlet; **CX1** = initial Codex feedback; **CX2** = second Codex audit; **W1** = Worker-1 feedback.

| Prior domain-relevant finding(s) | Sources | Disposition at evaluated SHA | Current evidence |
|---|---|---|---|
| Lifecycle was documented but not implemented | AG-2, CF1-2, CX1-5, CX2-H07 | **Partially fixed** | Most named commands now exist, but audit is a silent no-op; no start/defer/cancel; transitions have bypasses (F-01, F-03, F-04, F-10). |
| Date-time checking silently no-op | CF2-D1, CX1-7, CX2-H01 | **Fixed** | Dependency and self-test exist; independent invalid-date validation raised ValidationError. |
| Unknown schema fields accepted | CX1-8 | **Fixed** | Task, handoff, and review root schemas now set `additionalProperties: false` (`schemas/task.schema.json:4`, `schemas/handoff.schema.json:4`, `schemas/review.schema.json:4`); task events and review findings also close their object shapes. |
| Human-review-required task could close directly from PEER_REVIEW | CF2-D2, CX1-19, CX2-C05, CF3 retest | **Fixed** | The exact historical bypass is closed: when `human_review_required` is true, `close` rejects every status except HUMAN_REVIEW (`bin/fleet.py:570-573`); CF3 and current code confirm the gate. |
| Residual close authorization and non-human peer-review bypass | Current F-03; related to CX1-19/CX2-C05 | **Still present** | Human approval remains unauthenticated and defaults to actor `Unknown`; when `human_review_required` is false, `close` still accepts PEER_REVIEW without a recorded peer-review PASS (`bin/fleet.py:574-585`; F-03). |
| Manual status edits bypass transition memory | CF2-D3, CX1-5, CX2 lifecycle findings | **Still present** | Schema/lint validates snapshots, not legal history or CLI provenance; `last_transition` unused. |
| Missing `claimed_at`; no stale claim/lease | CF1-3, CF2-D4, CX1-15, CX2-H08 | **Partially fixed** | `claimed_at` is written and schema-known; no lease, heartbeat, expiry, release, or stale-claim lint exists. |
| Peer review had no schema/mechanism | CF1-4, CF2-D5, CX1-18, CX2-H07 | **Partially fixed** | Review schema/start/record commands exist; artifacts are not task/head/reviewer bound and can be empty fabricated PASS (F-03). |
| Handoff schema disconnected | CF1-7, CF2-D5, CX1-16, CX2-H03 | **Partially fixed** | Lint and submit validate shape; semantic/task/run cross-checks remain absent (F-02). |
| Evidence pasted/nominal; fabricated handoff bypass | CF1-5, CF2-D5, CX1-17, CX2-C04/H04/H05 | **Partially fixed** | Verify captures output/model/branch and nonzero status, but old evidence survives failure and fully fabricated cross-task evidence submits (F-02). “Cryptographic” remains inaccurate. |
| Stale audit remains claimable | AG-4, CF1-6, CF2 smaller findings, CX1-10, CX2-C06/H10 | **Still present** | `deadbeef` task claimed/verified against actual `e82d6182...` (F-05). |
| Dirty worktree/audit reality not checked | CX1-11, CX2-H10 | **Still present** | No branch, cleanliness, SHA-existence, or freshness check in audit/claim; audit itself is unreachable. |
| Dependency readiness not enforced | CX1-12, CX2-C03 | **Still present** | Task with OPEN dependency claimed successfully (F-05). |
| Lane eligibility not enforced | CX1-13, CX2-H09 | **Still present** | Claim accepts only free-form `--owner`; lane is never read. |
| Repository identity free-form | CX1-14, CX2-C06/H10 | **Still present** | Plain non-Git directory verified successfully with `branch: Unknown` (F-05). |
| Malformed YAML does not fail lint; mutations continue on corrupt store | CX1-24, CX2-C01/C02 | **Still present** | Error + green lint/exit 0; claim succeeds with malformed record present (F-06). |
| Conditional schema invariants weak/null | AG-3, CX1-6, CX2-H02 | **Partially fixed** | Conditional keys and nonempty owner exist; all-null audit quartet still lints; BLOCKED and terminal evidence invariants absent. |
| Duplicate IDs, filename mismatch, dangling dependencies, dependency cycles, and multiple active repository locks | CF2 summary, CX1-9, CX2 prior table | **Partially fixed** | Lint now detects duplicate IDs, filename/ID mismatch, and dangling dependencies among parseable active records (`bin/fleet.py:91-118`). It does not traverse dependencies for cycles or reject multiple active same-repository locks; malformed records are discarded and archive IDs are outside the checked set (F-04/F-06/F-08). |
| Claim TOCTOU race | CF1-3, CF2-D6, CX1-4, CX2-C07, CF3 retest | **Fixed for one local checkout; domain bypass remains** | Global `flock` wraps dispatch. Distributed authority is T-TAS-003. Block/unblock can nevertheless create two same-repo claims sequentially (F-04). |
| Repository lock releases in review | CX2-H11 | **Still present** | Claim locks only CLAIMED/IN_PROGRESS; PEER_REVIEW is unlocked. This is distinct from and compounded by F-04. |
| Writes not atomic; render not validated; multi-file partial transition | CF2 summary, CX1-25/26, CX2-H12/H13 | **Partially fixed / still present** | Atomic replacement protects task/board destinations, but fail-after-commit submit was reproduced (F-07). |
| Archive absent / terminal bloat | CF1-7, CF2 smaller findings, CX1-20 | **Partially fixed** | Archive exists and sweeps terminal tasks, but collision overwrites history, emits no event, and has no artifact/version binding (F-08). W1's observed “auto-archive” is not current command behavior; archive is explicit. |
| Block/unblock absent | CF1-2, CF2 smaller findings, CX2-H07 | **Partially fixed** | Commands exist, but accept arbitrary/repeated blocks and unsafe restore (F-04/F-10). |
| Deprecated `datetime.utcnow()` timestamp construction | CF2 smaller finding | **Fixed** | Current timestamp writers use `datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')` (`bin/fleet.py:52,65,267,288,317,466`); no `datetime.utcnow()` call remains. |
| Review bridge `datetime.UTC` crash | CF3 critical | **Fixed** | Current `start-review` executed successfully and uses `timezone.utc`. |
| Verify branch/model provenance hardcoded/unknown | CF2-D5, CX2-H05 | **Partially fixed** | Model is required and Git branch queried; non-Git becomes `Unknown`, head remains manual, and no dirty state/timestamps/run ID are captured. |
| Verification command trust, timeout, environment mismatch | CF2 smaller findings, CX1-30, CX2-H06, W1-1 | **Cross-reference T-TAS-003** | Runtime/environment/security/deployment ownership is operational. State impact is noted only where it enables stale/fabricated evidence. |
| Shared board conflicts, worktree isolation, multi-machine locking | AG-1, CF1-3, CF2-D6, CX1-3/4, CX2-C07/H14, W1-2 | **Cross-reference T-TAS-003** | Concurrency and deployment ownership is operational; local `flock` strength is confirmed here. |
| Git/bootstrap/tests/packaging/`.gitignore` | CF1-1, CX1-1/21/22/23, CX2-C08/H15 | **Cross-reference T-TAS-003** | Runtime and deployment ownership. No coordinator test suite was found at this SHA. |
| README/role/CLI drift, `--model` docs, database wording, manual create, dispatch view | CF1-8, CF2 smaller, CX1-2/27/28/29 and README section, CX2 docs, CF3 minor, W1-3 | **Cross-reference T-TAS-001** | Documentation/interface/role consistency ownership. F-01 is retained here because it is an executable state-machine failure. |

## Recommendations

Future work, in priority order:

1. Separate parser destinations (`subcommand` versus `verification_command`) and add a fail-closed final dispatch branch. Add a regression test invoking the exact audit syntax and asserting state, audit fields, task/global events, board output, visible success text, and nonzero on no dispatch.
2. Introduce one strict `load_validated_store()` preflight for every mutator and render. Parse/schema/cross-record/artifact errors must prevent all writes. Require non-null/nonempty audited values in audited-and-later states.
3. Make verification evidence coordinator-authoritative: generate head SHA and repository facts, record command/run IDs and timestamps, bind task/repo/base/head/model/owner, and invalidate prior success on a later failed run or repository change. Submit should accept only the current successful run.
4. Cross-check handoff and review task IDs, repository identities, tested/reviewed head SHAs, status, owner/reviewer separation, and artifact freshness. Require nonempty review coverage and record authenticated human approval; remove the `Unknown` default for mandatory human action. `close` must reject PEER_REVIEW for every task; non-human completion must occur only after a valid recorded peer-review PASS.
5. Enforce claim readiness atomically: all dependencies satisfied, registered repository identity, valid/current audit, clean/allowed branch/worktree policy, lane eligibility, and current repository lock. Define whether PEER_REVIEW retains ownership.
6. Redesign block/unblock as guarded transitions. Preserve claim reservation while blocked or revalidate repository exclusion on unblock; reject block-from-BLOCKED and terminal-state block unless explicitly modeled.
7. Treat task, handoff/review, board, and event append as one recoverable transaction or use an authoritative event/revision model that can rebuild projections. Never print transition success before all required state is durable.
8. Refuse archive destination collisions, validate active+archive ID uniqueness, record archive provenance, and preserve immutable task/artifact version links.
9. Convert every reproduction above into automated negative tests. Route runtime isolation, shell execution, distributed locking, generated-board contention, packaging, and CI to T-TAS-003; route documentation, actor authority, and interface accuracy to T-TAS-001.

## Domain verdict

**DONE_WITH_CONCERNS — domain evaluation complete; implementation verdict FAIL.** Audit's silent exit-0 no-op is a release-blocking state-machine defect and prevents the normal lifecycle from starting. Even after direct safe fixture setup, the evidence, review, block/unblock, readiness, corruption, transaction, and archive gates do not establish the provenance or exclusivity they claim. The coordinator should not be used as an autonomous completion authority until the critical findings have regression tests that prove the forbidden transitions fail.
