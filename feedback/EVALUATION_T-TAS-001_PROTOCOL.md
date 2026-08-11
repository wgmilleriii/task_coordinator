# T-TAS-001 Protocol and Role-Consistency Evaluation

## Executive verdict

The protocol domain is **not ready to serve as an authoritative fleet contract**. The repository has a useful file-backed task model, a substantially broader CLI than the early prototype, explicit self-modification guardrails, structured handoff/review artifacts, and an intelligible lifecycle vocabulary. However, the documentation, role model, CLI contract, generated board, and new `create` workflow do not currently describe one coherent system.

The highest protocol-owned risks are: role names are untrusted strings rather than enforceable authority; `create` can report success after writing an invalid task, treats placeholders as valid scope, derives collision-prone IDs from only three repository characters, and reuses archived IDs; README omits six executable workflows and gives a `verify` command that cannot parse; and board freshness depends on manual, unenforced render discipline that a reader cannot verify from the board itself.

The self-evaluation lifecycle is separately blocked by the **CRITICAL audit no-op documented as T-TAS-002 F-01**. T-TAS-001 remains `OPEN`; this report does not claim, audit, or transition it.

Evaluation status: **DONE_WITH_CONCERNS**. Protocol verdict: **FAIL / substantial correction required before the README or CLI can be treated as the fleet's governing interface**.

## Scope and evidence

- Repository: `/private/tmp/task_coordinator_self_evaluation/task_coordinator`
- Repository SHA: `0fc849c6e987b52bef3e49f7811052dfa076d081`
- Evaluation timestamp: `2026-08-11T00:23:18Z`
- Live-repository method: read-only inspection only. The sole live write is this report.
- Baseline working-tree state before the report: pre-existing `M TASKS.md`, `?? .venv`, and `?? logs/`.
- Temporary-copy experiments:
  - `/private/tmp/tas-protocol.6EPsWn/repo`
  - `/private/tmp/tas-protocol-reuse.lzxTHt/repo`
- Governing files read in full: `AGENTS.md`, `README.md`, `bin/fleet`, `bin/fleet.py`, all three schemas, all active tasks, current handoffs/reviews/archive artifacts, the self-evaluation design/plan, and the exact seven-file prior-feedback corpus required by T-TAS-001.
- Commands included `pwd`; `git rev-parse HEAD`; `git status --short`; `git diff -- TASKS.md`; `git log`; `rg`; numbered file inspection; `./bin/fleet --help`; and `./bin/fleet <subcommand> --help` for `lint`, `render`, `create`, `audit`, `claim`, `verify`, `submit`, `start-review`, `record-review`, `block`, `unblock`, `close`, and `archive`.
- I did not run live `lint`, `render`, `create`, `audit`, `claim`, `verify`, `submit`, review, block, close, or archive commands because command dispatch opens/writes `.fleet.lock` and the assignment limits live writes to this report. Mutating tests ran only in the two unique `mktemp -d` copies above.

| Scoped topic | Method | Files/commands | Result | Supporting evidence | Disposition |
|---|---|---|---|---|---|
| Repository and instruction boundary | Static inspection and baseline status | `pwd`; `AGENTS.md`; `git status --short`; `git rev-parse HEAD` | Correct assigned copy confirmed; restricted zones remained read-only | `pwd` returned the assigned `/private/tmp/.../task_coordinator`; AGENTS.md:9-26 defines restricted zones and worktree policy | Tested |
| README architecture claims | Line-by-line comparison with implementation | `README.md`; `bin/fleet.py`; schemas | Several maturity claims exceed executable guarantees | README.md:5,26-32 versus file-backed writes in bin/fleet.py:39-59 and generated shared board at 153-239 | Tested |
| Complete top-level CLI interface | Executed help | `./bin/fleet --help` | Thirteen subcommands exposed | Help listed `lint`, `render`, `create`, `audit`, `claim`, `verify`, `submit`, `start-review`, `record-review`, `block`, `unblock`, `close`, `archive` | Tested |
| Every subcommand help contract | Executed each subcommand's `--help` | All thirteen `./bin/fleet <name> --help` calls | Parser requirements captured; documentation gaps and sparse help confirmed | `verify` requires `--model`; `close --human` is optional; `record-review`, `submit`, `lint`, `render`, `unblock`, and `archive` expose almost no workflow guidance | Tested |
| Lifecycle vocabulary | Compared docs, schema, handlers, and help | README.md:36-45; task.schema.json:11; bin/fleet.py:278-604 | README has 6 states, schema has 11, and command reachability is not linear as documented | Schema adds `DRAFT`, `IN_PROGRESS`, `BLOCKED`, `DEFERRED`, `CANCELLED`; review failure writes `IN_PROGRESS` at bin/fleet.py:505-515 | Tested |
| Fleet Coordinator role | Role-to-interface mapping | README.md:13-16,51-56; CLI help | Coordinator duties are prose-only; no coordinator identity/authority interface exists | README says the Coordinator has global jurisdiction but must not edit YAML; parser has no actor/session/authentication concept | Tested |
| Scout role | Role-to-interface mapping and existing Scout evidence | README.md:54,94-96; bin/fleet.py:242-276; logs/fleet.jsonl:1-3; commits `30dea3b`, `0fc849c` | `create` exists but is undocumented and still requires direct YAML completion | CREATE events record actor `Unknown`; generated tasks were subsequently completed/hardened outside the CLI | Tested |
| PM role | Static parser inspection and temp-copy reproduction | README.md:55,98-103; bin/fleet.py:608-675; temp `fleet audit` | PM's only transition command is currently a silent no-op | Temp command exited 0 with empty output; T-TAS-001 stayed `status: OPEN` | Tested; owner T-TAS-002 |
| Worker role | Docs/help/source comparison | README.md:56,64-85; `claim`, `verify`, `submit` help | Workflow mostly exists, but documented `verify` invocation is invalid and lane authority is unenforced | Help requires `--model`; README.md:83 omits it; claim accepts arbitrary `--owner` at bin/fleet.py:625-627 | Tested |
| Reviewer/Auditor roles | Docs/schema/help/source comparison | README.md:49-56; task.schema.json:10; `start-review`, `record-review` help | Reviewer is mentioned but not defined; `AUDITOR` is a lane but not a documented role; review requires an undocumented manual artifact edit | README role list stops at Worker; bin/fleet.py:444-522 and 636-642 implement review commands | Tested |
| Human role | Docs/help/source comparison | README.md:92-114; `close --help`; bin/fleet.py:564-587 | Human creation docs bypass `create`; human identity defaults to `Unknown` despite an approval claim | README.md:95 directs manual file creation; bin/fleet.py:653 makes `--human` optional | Tested |
| Contradictions and missing steps | Cross-document/interface diff | `rg` across README.md, AGENTS.md, schemas, bin/fleet.py | Multiple current contradictions confirmed | Findings P-01, P-02, P-05, P-06, and P-07 below | Tested |
| Unsafe manual edits | Static and historical workflow inspection | README.md:54,84,95-96,111-115; bin/fleet.py:268-275,459-477 | Creation, handoff completion, and review completion depend on manual YAML edits; documentation does not consistently require revalidation/render | `create` prints “Please edit”; README's human creation path is entirely manual | Tested |
| Ambiguous authority | Parser/source inspection | bin/fleet.py:273-275,289-294,319-320,459-477,517-518,530-557,581-582 | Identities are caller-provided or `Unknown`; lane/role is not checked | Finding P-02 | Tested |
| New `create` workflow: normal output | Temp-copy execution | `fleet create --title 'Protocol collision test' --repo task_catalog --priority P1 --lane codex`; temp lint | Command created `T-TAS-004`; placeholders passed “strict” lint | Temp YAML contained only `REQUIRED_PLEASE_FILL` for scope and definition of done; lint exited 0 | Tested in temp copy |
| New `create` workflow: validation | Temp-copy negative execution | `fleet create --title x --repo alpha`; temp lint | Create exited 0 and rendered an invalid task; later lint exited 1 | Output said `Created new task T-ALP-001`; lint reported `'x' is too short` | Tested in temp copy |
| New `create` workflow: ID generation | Static inspection and two temp-copy reproductions | bin/fleet.py:242-258; `task_catalog` create; archived-ID reuse create | Three-character namespaces collide and archived IDs are reused | `task_catalog` received `T-TAS-004`; after moving T-TAS-003 to archive, creating for `task_coordinator` produced a new active `T-TAS-003`; lint still exited 0 | Tested in temp copies |
| Post-creation edits and board freshness | Current-state comparison plus temp output | tasks/active/T-TAS-001.yaml:9-25; TASKS.md:43-56; bin/fleet.py:272-275 | Board and canonical task disagree; create renders before the required edit and does not instruct re-render | Current board contains only the original 3 scope/3 DoD items while the task has 7 scope/7 DoD items | Tested |
| Schemas/artifacts for interface consistency | Static inspection | schemas/*.json; handoffs/*.yaml; reviews/*.yaml; tasks/archive/*.yaml | Artifacts and validators now exist, but README omits review/archive workflows and task schema exposes undocumented statuses/lanes | task.schema.json:10-25; review.schema.json:6-26; T-MIN-004 review/archive artifacts | Tested |
| Current task board | Static comparison; no live render | TASKS.md; tasks/active/*.yaml; `git diff -- TASKS.md` | Current board diverges from canonical YAML; refresh is manual and the board carries no verifiable freshness marker | Finding P-06 | Tested (render intentionally not run) |
| Existing Scout/PM evidence | Git/log/task inspection and audit reproduction | logs/fleet.jsonl; commits `30dea3b`, `0fc849c`; T-TAS tasks; temp audit | Scout creation is evidenced; PM audit failed silently; all T-TAS tasks remain OPEN | CREATE log entries at 00:05Z; no AUDIT entries; temp audit no-op reproduced | Tested |
| Prior-feedback corpus | Full read and current evidence mapping | Exact seven files listed below | Every protocol-relevant finding dispositioned; out-of-domain clusters assigned to T-TAS-002/T-TAS-003 | “Prior feedback disposition” tables | Tested |
| Runtime/deployment/concurrency | Static references only | wrapper, README, prior evidence | Not independently retested because T-TAS-003 owns this domain | Cross-referenced to T-TAS-003 | Not tested in this domain |
| Transition/evidence integrity beyond interface consistency | Static references plus audit no-op reproduction | state handlers, schemas, prior evidence | Not duplicated because T-TAS-002 owns this domain | Cross-referenced to T-TAS-002 | Not tested except audit dispatch blocker |

## Confirmed strengths

1. **The repository guard is unusually explicit.** AGENTS.md:9-26 names restricted paths, confines engine self-modification to an audited coordinator task, prohibits branch switching in the shared engine checkout, requires an isolated worktree, and preserves human review. These are concrete, legible boundaries.

2. **The CLI surface now covers most named lifecycle operations.** The current help exposes create, audit, claim, verification/submission, peer review, block/unblock, close, and archive commands. This is a major improvement over the three-command prototype described in early feedback.

3. **The schema provides a controlled vocabulary.** Task IDs, priorities, lanes, statuses, timestamps, audit metadata, ownership, blocked state, and event objects are declared with `additionalProperties: false` (task.schema.json:1-61). Separate handoff and review schemas now exist.

4. **Peer-review artifacts are real rather than merely aspirational.** `start-review` creates a structured artifact and `record-review` consumes it (bin/fleet.py:444-522); `reviews/T-MIN-004_review.yaml` demonstrates a substantive current artifact.

5. **The README correctly tells agents to establish location and respect repository lanes.** README.md:13-16 makes `pwd` and cross-repository separation prominent, while README.md:31-32 identifies the CLI as the mutation interface and the board as generated output.

6. **Help choices reduce some input ambiguity.** `create` constrains priority/lane and `verify`/`start-review` require model attribution. The T-TAS Scout run also demonstrates deterministic sequential IDs within one active three-letter namespace.

## Findings

### P-01 — MAJOR — README maturity claims do not match the executable system

README.md:5 calls the store “database-backed” and claims massively parallel operation without Git conflicts, but the authority is a directory of YAML files written by bin/fleet.py:39-45. `create` and canonical task state-changing handlers invoke the shared TASKS.md renderer (bin/fleet.py:275,298,324,441,521,539,561,586,603); artifact-only `verify` and `start-review` are exceptions. README.md:29 and 56 call evidence “cryptographic,” but the implementation writes mutable YAML and asks the user to type `head_sha` (bin/fleet.py:375-397). README.md:43 calls peer review “automated,” while the CLI only generates a template and tells a person/agent to edit it (bin/fleet.py:459-477).

These statements are unsafe protocol language because they encourage actors to rely on guarantees that are not represented by the interface. The evidence-integrity substance is owned by T-TAS-002; the parallel/runtime substance is owned by T-TAS-003. T-TAS-001 owns the inaccurate documentation.

### P-02 — MAJOR — Role names are not enforceable authority, and Reviewer/Auditor taxonomy is incomplete

README.md:51-56 defines Coordinator, Scout, PM, and Worker, mentions Reviewers only inside the Coordinator paragraph, and never defines a Reviewer role. task.schema.json:10 and `create --help` expose an `AUDITOR` lane, but README has no Auditor role or rule connecting that lane to `start-review`.

The parser accepts self-asserted identity strings: `audit --auditor` (bin/fleet.py:619-623), `claim --owner` (625-627), and `start-review --reviewer/--model` (636-639). `close --human` defaults to `Unknown` (651-653), while block/unblock and create events hard-code actor `Unknown` (273, 534-557). `claim` never compares task lane with caller identity (301-327). Thus “PMs only” is help text, HUMAN/AUDITOR lanes are labels, and the audit/review/human separation is not an executable authority boundary.

Transition/evidence consequences belong to T-TAS-002; this finding concerns the public role contract.

### P-03 — MAJOR — `create` identifiers are collision-prone and not globally unique across task history

bin/fleet.py:243-258 takes only `repo[:3].upper()`, scans only `tasks/active`, and chooses `max + 1`. It does not consult `tasks/archive`, handoffs, reviews, or a repository registry.

Two direct temporary-copy observations confirm the consequences:

- With existing `task_coordinator` IDs T-TAS-001..003, creating a task for distinct repo `task_catalog` produced `T-TAS-004`; unrelated repos share the `T-TAS` namespace.
- After moving T-TAS-003 into the temporary archive, creating another `task_coordinator` task produced a new active `T-TAS-003`. `fleet lint` still exited 0 with both the archived and active record.

Reused IDs make references in logs, handoffs, reviews, URLs, and human conversation ambiguous, and a later archive can overwrite an earlier same-named record. This is within T-TAS-001 because stable ID generation is an explicit `create` scope item; artifact-integrity enforcement beyond ID allocation belongs to T-TAS-002.

### P-04 — MAJOR — `create` can report success after writing invalid or semantically placeholder state

`create` constructs a task and saves it without schema validation (bin/fleet.py:242-275). In a temporary copy, `fleet create --title x --repo alpha` exited 0, printed success, and rendered T-ALP-001; the subsequent linter exited 1 because the schema requires a five-character title (task.schema.json:7).

The normal path is also incomplete by design: scope and definition of done are literal `REQUIRED_PLEASE_FILL` strings (bin/fleet.py:268-269). Those strings satisfy the current schema's `minItems: 1`, so a temporary task containing only both placeholders received `✅ All active tasks, handoffs, and reviews passed strict schema validation.` The command logs actor `Unknown`, renders immediately, then asks for direct file editing without instructing `lint` or `render` afterward (272-275).

The result is an interface that says “Created” before proving that its own output is valid or actionable.

### P-05 — MAJOR — README omits or contradicts much of the current CLI contract

The executable exposes thirteen subcommands, but README has no workflow for `create`, `start-review`, `record-review`, `block`, `unblock`, or `archive`. README.md:94-96 still tells humans to create YAML manually even though `create` exists, and README.md:54 tells Scouts to write YAML rather than use it. README's numbered role list contains no Reviewer instructions even though a passing review is now the route from PEER_REVIEW to HUMAN_REVIEW/DONE.

README.md:83 instructs `./bin/fleet verify T-XXX-123`, but current `verify --help` requires `--model MODEL`, so the documented command fails argument parsing. README.md:38-45 presents a strict six-state linear progression, while task.schema.json:11 permits eleven states and bin/fleet.py:505-515 introduces the undocumented PEER_REVIEW → IN_PROGRESS and PEER_REVIEW → DONE paths.

The result is not merely missing reference material: an agent following the “exact steps” at README.md:62 cannot complete the documented command, and a reviewer cannot discover their mandatory workflow from the operating manual.

### P-06 — MAJOR — Board freshness is manual, unenforced, inconsistently specified, and unverifiable

The current canonical T-TAS-001 record has seven scope items and seven definition-of-done items (tasks/active/T-TAS-001.yaml:9-25). TASKS.md:47-56 shows only three of each. Git history explains this observed divergence: commit `30dea3b` created the initial tasks; commit `0fc849c` hardened their definitions without updating the board; the pre-existing working-tree `TASKS.md` diff reflects the earlier render.

README.md:65-69 does tell Workers to render before reading, which is a useful mitigation. The freshness rule is nevertheless manual, unenforced, and inconsistently repeated: `create` renders *before* its required post-create edits, its completion prompt does not request another render, and manual-edit guidance at README.md:94-115 mentions only lint. TASKS.md contains no source hash or generated timestamp with which a reader can verify that the mitigation was followed.

The **MAJOR** rating reflects that README.md:15-16,53 and 65-69 make the board the Coordinator/Worker dispatch input: an undetectably stale view can misdirect role selection even though canonical YAML is intact. Concurrent board contention and view-generation mechanics are owned by T-TAS-003; T-TAS-001 owns the inconsistent and unverifiable freshness contract.

### P-07 — MINOR — `audit` disagrees about whether DRAFT is auditable

Top-level help says `audit` audits an OPEN task (bin/fleet.py:619). The handler permits both OPEN and DRAFT (283), but its failure text says status “must be OPEN” (284). task.schema.json:11 permits DRAFT while README's lifecycle omits it. Once audit dispatch is repaired, callers still will not know whether DRAFT → AUDITED is supported or accidental.

### P-08 — MINOR — Subcommand help is too sparse for artifact-mediated workflows

The help sweep found bare positional `task_id` entries and no examples for most commands. `record-review --help` says only “Record the verdict of a peer review”; it does not tell the caller that `start-review` first creates a FAIL/placeholder YAML file which must be manually edited. `submit --help` does not mention the handoff prerequisite; `create --help` does not expose defaults or post-create requirements; audit arguments have no descriptions; and `close --help` does not disclose that omitted `--human` records `Unknown`.

This compounds README drift because neither documentation surface is sufficient on its own.

### XR-01 — CRITICAL cross-domain PM-interface blocker, owned by T-TAS-002 F-01

The temporary-copy PM command exited 0 with no output and left T-TAS-001 `OPEN`, so the documented PM interface is unusable. See **T-TAS-002 F-01** for root cause, full reproduction, severity ownership, and corrective work; this cross-reference records only the resulting protocol blocker. The live task remains OPEN, and this evaluator did not invoke the live transition.

## Prior feedback disposition

The fixed corpus was read in full and consists exactly of:

1. `feedback/AUDIT_ClaudeFable_20260810T1640-0600.md`
2. `feedback/AUDIT_Codex_GPT5_20260810T164505-0600.md`
3. `feedback/FEEDBACK_Antigravity.md`
4. `feedback/FEEDBACK_ClaudeFable.md`
5. `feedback/FEEDBACK_ClaudeFable_claude-fable-5_20260810.md`
6. `feedback/FEEDBACK_Codex_GPT5_20260810T163242-0600.md`
7. `feedback/FEEDBACK_Worker1_ClaudeSonnet5_20260810.md`

### Protocol-domain findings

| Prior source/finding | Disposition | Current evidence |
|---|---|---|
| `FEEDBACK_ClaudeFable.md` #1, coordinator not a Git repository | **Fixed** | `git rev-parse HEAD` returned the recorded SHA and current history exists. |
| `FEEDBACK_ClaudeFable.md` #2, lifecycle documented but only three commands existed | **Partially fixed** | Thirteen subcommands now exist, but README omits six and `audit` is a silent no-op; P-05 and XR-01. Transition enforcement is T-TAS-002. |
| `FEEDBACK_ClaudeFable.md` #4, PEER_REVIEW had no mechanism/playbook | **Partially fixed** | Review schema and start/record commands now exist, but Reviewer/Auditor roles and flow are undocumented; P-02/P-05. Evidence enforcement is T-TAS-002. |
| `FEEDBACK_ClaudeFable.md` #7, archive/handoff mechanics absent | **Partially fixed** | `archive`, handoff validation, and current artifacts exist; README still omits archive/review and stable cross-artifact semantics are T-TAS-002. |
| `FEEDBACK_ClaudeFable.md` #8, README/schema drift (`DRAFT`, `IN_PROGRESS`, `CANCELLED`; unexplained `AUDITOR`) | **Still present** | README.md:36-56 versus task.schema.json:10-11; P-02/P-05/P-07. |
| `AUDIT_ClaudeFable_20260810T1640-0600.md` smaller finding, README behind CLI | **Partially fixed** | README now documents audit/verify/submit/close, but not create/review/block/archive, and its verify example is invalid; P-05. |
| Same audit, `cmd_audit` accepts DRAFT while saying OPEN | **Still present** | bin/fleet.py:283-285 and help line 619; P-07. |
| Same audit, no archive/unclaim/block commands | **Partially fixed** | archive, block, and unblock now exist; no unclaim/release interface is exposed. Lifecycle semantics are T-TAS-002. |
| Same audit D-5, no peer-review interface/model attribution | **Partially fixed** | start/record review and required reviewer/model exist; README role/workflow remains absent; P-02/P-05. |
| `AUDIT_Codex_GPT5_20260810T164505-0600.md` prior table, only three CLI commands | **Partially fixed** | Thirteen commands exist; docs and some lifecycle interfaces remain incomplete; P-05. |
| Same audit C-08/documentation, no setup instruction | **Partially fixed** | README.md:14 now says install requirements, but wrapper/bootstrap behavior belongs to T-TAS-003 and was not retested here. |
| Same audit H-07, states had no commands | **Partially fixed** | review, block/unblock, and archive were added; DRAFT/DEFERRED/CANCELLED lack explicit authoring/transition commands, while IN_PROGRESS is only an internal review-failure destination. |
| Same audit H-09, lane eligibility not enforced | **Still present** | create exposes lanes but claim accepts arbitrary owner without a lane check; P-02. |
| Same audit H-10, “PMs only” is help rather than authority | **Still present** | audit takes arbitrary `--auditor` and currently no-ops; P-02/XR-01. |
| Same audit documentation-drift list (manual workflow, missing commands, six vs eleven states, “database-backed,” massive-parallel/no-conflict, strict evidence/peer review claims) | **Partially fixed overall; several still present** | Audit/verify/submit/close are documented; all other items remain as P-01/P-05. Underlying enforcement is T-TAS-002/T-TAS-003. |
| `FEEDBACK_Antigravity.md` #2, README strict progression but only three commands | **Partially fixed** | Broader CLI exists, but docs remain incomplete and audit cannot dispatch; P-05/XR-01. |
| Same feedback #1, README no-conflict promise despite shared board | **Still present as documentation** | README.md:5 and P-01; concurrency mechanics are T-TAS-003. |
| `FEEDBACK_ClaudeFable_claude-fable-5_20260810.md` critical review-bridge datetime crash | **Fixed** | bin/fleet.py:8 and 466 use `timezone.utc`; a current T-MIN-004 review artifact exists. |
| Same feedback, README missing `start-review`/`record-review` | **Still present** | No matches in README; P-05. |
| Same feedback, required reviewer `--model` is correct | **Fixed/retained strength** | `start-review --help` requires both reviewer and model. |
| Same feedback, feedback directory convention disagreed with root-level files | **Fixed for the specified corpus** | All seven required files are now under `feedback/`. Historical moves were not reconstructed. |
| `FEEDBACK_Codex_GPT5_20260810T163242-0600.md` #2 and README corrections, “database-backed”/production maturity wording | **Still present** | README.md:5; P-01. |
| Same feedback #5, incomplete transition CLI | **Partially fixed** | Thirteen commands exist, but status/interface gaps and audit no-op remain; P-05/XR-01. |
| Same feedback #9, duplicate task IDs were not detected | **Partially fixed** | Active-store lint now tracks `seen_ids` and rejects duplicates (bin/fleet.py:90-106), but `create` scans only active tasks (246-258). The temporary-copy archive test created a new active `T-TAS-003` while archived `T-TAS-003` already existed, and lint still exited 0; P-03. |
| Same feedback #13, lane eligibility | **Still present** | P-02. |
| Same feedback #14, repository identity is only a free-form string | **Still present** | task.schema.json:8 constrains `repo` only to a non-empty string, while `create --repo` accepts arbitrary text (bin/fleet.py:243-244,615) and no repository registry or canonical identity interface exists. The protocol/ID consequence is P-03; live repository resolution and audit-state enforcement belong to T-TAS-002, while path/deployment safety belongs to T-TAS-003. |
| Same feedback #18, no peer-review artifact/verdict model | **Partially fixed** | Review schema and commands exist; role documentation and workflow are missing; P-02/P-05. |
| Same feedback #19, human-review flag unused | **Partially fixed** | Code now branches on `human_review_required` (bin/fleet.py:510-515,570-577), but `--human` defaults to `Unknown` and authority remains self-asserted; P-02. Gate integrity is T-TAS-002. |
| Same feedback #20, archive behavior absent | **Fixed at command-interface level** | `archive --help` and bin/fleet.py:589-604 exist; README still omits the workflow. Artifact preservation is T-TAS-002. |
| Same feedback #27, no authoritative `fleet next` selection interface | **Still present** | Top-level help has no `next` command. This remains a feature request, not a claimed critical defect. |
| Same feedback #28, status presentation conflates states | **Partially fixed** | Render now distinguishes BLOCKED, review, active, and DONE; OPEN/AUDITED/DRAFT/DEFERRED/CANCELLED still share generic presentation. |
| Same feedback #29, manual task creation bypasses CLI | **Partially fixed** | `create` exists, but README still instructs manual creation and create itself requires manual completion; P-04/P-05. |
| Same feedback #30, verification-command authority/security boundaries undocumented | **Still present as documentation** | README does not define who may authorize shell commands or their safety policy. Enforcement belongs to T-TAS-002 and runtime controls to T-TAS-003. |
| `FEEDBACK_Worker1_ClaudeSonnet5_20260810.md` #3, README verify example omits required `--model` | **Still present** | README.md:83 versus `verify --help`; P-05. |
| Same feedback feature request, default model identity | **Still not implemented** | `verify --help` requires explicit `--model`; no documented environment/identity source exists. This is an optional usability request, not a defect by itself. |
| Same feedback #2, README lacks shared-worktree isolation guidance | **Partially fixed narrowly** | AGENTS.md:22-26 now requires worktrees for coordinator engine upgrades, but README.md:78-80 still tells spoke Workers merely to create a branch. Operational ownership is T-TAS-003. |

### Out-of-domain prior findings

The following findings were not duplicated or re-adjudicated as T-TAS-001 defects:

| Owning task | Prior finding clusters cross-referenced | This evaluation's disposition |
|---|---|---|
| **T-TAS-002 — state machine and evidence enforcement** | Malformed-store fail-open behavior; schema condition/null gaps; date validation; dependency readiness; stale audits; hand-edited transitions; handoff/review validation and cross-binding; fabricated evidence; human-review gate enforcement; SHA/worktree provenance; lane enforcement as a transition gate; unrestricted verification-command authority; close/record-review/archive state legality. These appear throughout both Codex reports, both Claude Fable reports, and Antigravity findings #2-4. | **Not retested here**, except the audit parser no-op needed to explain the blocked PM interface (XR-01). Current static code references were supplied to the T-TAS-002 owner. |
| **T-TAS-003 — runtime, deployment, and concurrency safety** | Claim/create races; lock scope; generated-board merge contention; multi-file durability; shared-worktree interference; clean-clone/bootstrap behavior; coordinator-versus-spoke virtualenv mismatch; multi-machine arbitration; timeouts/output handling; logging/recovery/observability; absence of automated runtime smoke tests. These appear in both Codex reports, both Claude Fable reports, Antigravity #1, and Worker1 #1-2. | **Not retested here.** P-01/P-06 discuss only the documentation/freshness representations. Runtime conclusions belong to T-TAS-003. |

## Recommendations

Future work, in priority order:

1. **Unblock the lifecycle under T-TAS-002.** Give the subparser selector and verification command distinct destinations, add a regression test asserting that every dispatched subcommand either runs or exits nonzero, and do not resume PM transitions until the audit no-op is reviewed.

2. **Publish one canonical role-to-command matrix.** Define Coordinator, Scout, PM, Worker, Reviewer/Auditor, and Human; state which commands each may invoke; define identity, lane, required artifacts, prior/next states, and manual-edit authority. Generate or test this matrix against parser/schema metadata.

3. **Make task creation complete and fail closed.** Accept all required scope/definition data through the command (repeatable flags or a validated input document), capture the creator identity, validate before the first write/render/log entry, and reject placeholders as semantic task content.

4. **Replace three-character/max-active ID allocation.** Use a registry-backed immutable ID or collision-resistant identifier, check active and archived tasks plus handoff/review/log references, and make historical ID reuse impossible.

5. **Reconcile README with all thirteen commands.** Add exact examples for create, audit, claim, verify with `--model`, submit, start-review, review-artifact completion, record-review, block/unblock, close, archive, lint, and render. Document defaults and failure exit behavior.

6. **Define board freshness across the owning domains.** T-TAS-003 should own operational generation, serialization, and verifiable source revision/timestamp mechanics. T-TAS-001 should document exactly when render is required, repeat lint-and-render instructions after every supported manual edit, expose the freshness contract in CLI help, and tell consumers how to recognize or reject a stale TASKS.md.

7. **Use accurate system language until stronger guarantees exist.** Describe the store as file-backed, evidence as captured terminal output, review as artifact-mediated rather than automated, and parallel guarantees only to the level verified by T-TAS-003.

8. **Improve self-describing help.** Add meaningful descriptions for every positional/option, show defaults, identify prerequisite/generated artifacts, and include the next command. Help and README examples should be exercised in a non-mutating CLI contract test.

9. **Resolve DRAFT and terminal-state semantics across the owning domains.** T-TAS-002 should define and enforce whether DRAFT is auditable, how DEFERRED/CANCELLED are reached, and which approvals distinguish automatic from human-approved DONE. T-TAS-001 should align README, role authority, schema-facing terminology, and command help with those enforced decisions.

## Domain verdict

**FAIL — protocol and executable authority are materially inconsistent.** The architecture is promising and several earlier interface gaps are fixed, but the operating manual cannot currently guide every required role through the real CLI, role identity is not authoritative, creation does not preserve valid/global task identity, and board freshness depends on unenforced render discipline that cannot be verified from the board itself.

The evaluation deliverable itself is **DONE_WITH_CONCERNS**. The larger dogfood lifecycle remains **BLOCKED at PM audit** by XR-01, owned by T-TAS-002. No task was claimed, audited, or transitioned during this evaluation.
