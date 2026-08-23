# Dollers Fleet Task Coordinator (V2)

The **Task Coordinator (V2)** is the central Hub for the Dollers AI Agent Fleet. It dispatches, tracks, and verifies work across Spoke repositories (like `artmetrics.co`, `minchiate_tarot`, `intypiano`).

This system replaces the monolithic `TASKS.md` flat-file with a Git-tracked, YAML-backed, schema-enforced architecture that supports massively parallel agent swarms without Git merge conflicts. Note: The system is currently a rapidly improving alpha and is undergoing sequential hardening.

**New here? Read "How It Works" and "Quick Start" below. Agents being dispatched into this repo should jump to [Startup Instructions](#-startup-instructions-for-agents).**

---

## 🧭 How It Works

Each unit of work is one YAML file in `tasks/active/`. That directory is the database — there is no server and no external state. Every state change goes through the `./bin/fleet` CLI, which validates against the JSON Schemas in `schemas/` and regenerates the human-readable `TASKS.md` board.

The point of one-file-per-task is merge safety: a dozen agents can each touch their own task file concurrently without colliding in Git.

Work moves through a fixed lifecycle — a PM audits a task to unlock it, one agent claims it, does the work in a Spoke repo, captures terminal evidence of a passing verification command, and submits it for peer review. Nothing reaches `DONE` on an agent's say-so; it reaches `DONE` on captured evidence plus a recorded review.

### Required directory layout

The CLI resolves Spoke repositories as **siblings of this repo** (`../<repo_name>`). Commands like `fleet verify`, `fleet onboard`, and `fleet sweep-docs` will fail if the layout doesn't match:

```
parent-directory/
├── task_coordinator/     ← this repo (the Hub)
├── minchiate_tarot/      ← a Spoke repo
├── intypiano/            ← a Spoke repo
└── Obsidian/             ← optional vault, auto-detected by `fleet onboard`
```

The `repo:` field in each task YAML is the sibling directory name.

---

## ⚡ Quick Start (Humans)

The `./bin/fleet` wrapper activates a virtualenv at the repo root, so **you must create `.venv` specifically** — a system-wide `pip install` will not work:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Then confirm it runs:

```bash
./bin/fleet lint      # validate every active task against the schema
./bin/fleet render    # regenerate TASKS.md from the YAML store
```

Read `TASKS.md` to see the current board. For a live view in the browser:

```bash
./bin/dashboard       # Flask app on http://127.0.0.1:5000
```

`lint` exits non-zero if any task in `tasks/active/` violates `schemas/task.schema.json`. Some tasks on the current board do not lint clean; that reflects the state of the board, not a broken install.

---

## 🚀 Startup Instructions (For Agents)

If you have just been dispatched to this repository to evaluate it or begin work, follow these instructions immediately:

1. **Read the Rules:** Read this entire `README.md` document to understand the lifecycle and the specialized Roles (Fleet Coordinator, Scout, PM, Worker, Reviewer).
2. **Read Previous Feedback:** Check the `feedback/` directory and read the 1-2 most recent feedback files. You must understand the warnings, lessons learned, and architectural decisions left by previous swarms before you act.
3. **Environment:** Set up the virtualenv exactly as shown in [Quick Start](#-quick-start-humans) — `python3 -m venv .venv` followed by `.venv/bin/pip install -r requirements.txt`. The `./bin/fleet` wrapper sources `.venv/bin/activate` and will fail without it.
4. **CRITICAL BOUNDARY RULE (For Subagents):** If you are a Scout, PM, or Worker, you must immediately run `pwd` to determine which repository folder you are sitting in (e.g., `intypiano`, `minchiate_tarot`). **Cross-repo contamination is strictly forbidden.** When you read the `TASKS.md` board, you must completely ignore all tasks belonging to other repositories. Do not claim them, and do not execute them.
5. **Your Mission:** If you were not assigned a specific role, you are the **Fleet Coordinator** and you have global jurisdiction. Do not write code or edit YAML files yourself. Your job is to orchestrate the swarm. Read the entire `TASKS.md` board. You must spawn subagents directly into their target directories (e.g., `cd ../minchiate_tarot && <agent_command>`) so they can act as Scouts, PMs, Workers, or Reviewers for that specific repository.
6. **REQUIRED End-of-Session Feedback:** When the swarm finishes a session, the Fleet Coordinator **MUST** write up its findings and save them directly into the `feedback/` directory using the naming convention `FEEDBACK_<YourName>_<Model>_YYYYMMDD.md`. Your feedback MUST explicitly include two sections:
   - **System-Level Feedback:** Defects or loopholes in the `task_coordinator` itself, architectural complaints, and feature requests.
   - **Repository-Level Feedback:** A detailed explanation of *how* the tasks were accomplished in the target repo (not just a list of what was done), lessons learned, concerns about the project's direction, and what you believe the next steps should be. Do not modify existing feedback files.

---

## 📚 Dewey Decimal Documentation Protocol

To prevent spoke repositories from becoming littered with loose `planning.md` or `scratch.md` files, all agents MUST adhere to the Dewey Decimal index for documentation. 

Any `.md` file created in a spoke repository (excluding standard files like `README.md` or `.fleet_context.md`) **MUST** be placed in a `docs/` folder using the following category numbers:

- `00-Meta/` (Project management, agent notes, task context)
- `10-Product/` (Requirements, UX, design docs, user journeys)
- `20-Architecture/` (System design, database schemas, API specs)
- `30-Engineering/` (Setup guides, dev logs, code conventions)
- `40-Operations/` (Deployment, CI/CD, infrastructure, runbooks)
- `90-Archive/` (Archived files, deprecated notes)

**YAML Frontmatter Requirement:**
Every `.md` file in `docs/` must contain standard YAML frontmatter exactly matching `schemas/doc_frontmatter.schema.json`. At minimum, it must have:
```yaml
---
title: "Document Title"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
last_modified: "YYYY-MM-DDTHH:MM:SSZ"
author: "AgentName"
status: "active" # or draft, archived, deprecated
category: "20-Architecture"
---
```
Do NOT write edit history logs in the markdown. Rely on `git log` for change history.

---

## 🏗️ Architecture

**The database**
- **`tasks/active/`**: Every active task is an isolated `.yaml` file, named for its task ID (`T-PTG-101.yaml`).
- **`tasks/archive/`**: Completed, cancelled, and deferred tasks, swept off the active board by `fleet archive`.
- **`schemas/`**: JSON Schema definitions that mechanically enforce what a task, handoff, review, or doc frontmatter is allowed to contain.

**Evidence**
- **`handoffs/`**: Handoff documents generated by `fleet verify`, containing captured terminal evidence and the commit SHA being handed off.
- **`reviews/`**: Peer review verdicts generated by `fleet start-review` and consumed by `fleet record-review`.
- **`feedback/`**: A drop-box for agents to leave structured reviews, audits, and feedback about the coordinator itself. Files should be named `FEEDBACK_<Agent>_<Model>_<Timestamp>.md`.

**Interfaces**
- **`bin/fleet`**: The Python-based command-line interface. Agents and humans must use this to interact with the database. See the [Command Reference](#-command-reference).
- **`bin/dashboard`** + **`web/`**: An optional Flask read-out of the board at `http://127.0.0.1:5000`.
- **`TASKS.md`**: A **READ-ONLY** markdown file dynamically generated by the CLI for human convenience. Never edit this file directly — `fleet render` overwrites it from the YAML store.

**Bookkeeping**
- **`logs/fleet.jsonl`**: Append-only event log of every CLI action. Git-ignored; local to each clone.
- **`ARCHIVES.md`**: Append-only narrative log for this repository.
- **`.fleet_context.md`**: Per-repo onboarding context written by `fleet onboard`.

---

## 🚦 The Task Lifecycle

Tasks follow a strict progression, and the CLI refuses transitions taken out of order:

1. **`DRAFT` / `OPEN`**: The task is an idea. Agents CANNOT claim it.
2. **`AUDITED`**: A PM has verified the codebase, written a strict scope, and attached an `audited_repo_sha` and a `verification_command`. The task is now safe to execute. (`fleet audit`)
3. **`CLAIMED`**: An agent has locked the task. Only one task per Spoke repo may be `CLAIMED`/`IN_PROGRESS` at a time, and every task listed in `dependencies` must already be `DONE`. (`fleet claim`)
4. **`IN_PROGRESS`**: Work is underway. A task also lands back here when a peer review returns `FAIL`.
5. **`PEER_REVIEW`**: The agent is finished, has terminal evidence in `handoffs/`, and has requested an automated peer review. (`fleet submit`)
6. **`HUMAN_REVIEW`**: The task passed peer review and awaits final human visual/strategic sign-off. **This step only happens when the task sets `human_review_required: true`** — otherwise a passing review sends it straight to `DONE`. (`fleet record-review`)
7. **`DONE`**: The work is merged into the repo's integration branch (see **Merge Target** below — this is not necessarily `main`/production). (`fleet record-review` or `fleet close`)

**Off-ramps:**
- **`BLOCKED`**: Work cannot proceed. `fleet block` records the reason and remembers the prior status; `fleet unblock` restores it.
- **`DEFERRED` / `CANCELLED`**: Set by hand in the YAML. Along with `DONE`, these are swept into `tasks/archive/` by `fleet archive`.

---

## 🎭 Agent Roles

The fleet operates using specialized agent roles to safely separate "thinking" from "doing". If you are an agent, your prompt will tell you which role you are currently playing:

0. **Fleet Coordinator:** The master orchestrator. You do not touch code or YAML files directly. You read the board and spawn subagents (Scouts, PMs, Workers, Reviewers) to push the system forward.
1. **Scouts:** Your job is to fill the hopper. You explore target repositories (the repository you are currently in), identify missing features or bugs, and write new YAML tasks into `tasks/active/`. You MUST set these tasks to `status: OPEN`. Scouts never write code.
2. **Project Managers (PMs):** Your job is to protect the swarm. You read the `OPEN` tasks generated by Scouts. You verify them against the user's high-level goals. If approved, you write a safe verification command and run `./bin/fleet audit` to unlock the task. If the task introduces major architectural changes, you MUST manually add `requires_doc_update: true` to the task's YAML file.
3. **Workers:** Your job is to execute. You run `./bin/fleet render`, find an `AUDITED` task in your assigned lane, run `./bin/fleet claim`, write the code, and submit cryptographic proof via `./bin/fleet submit`. You NEVER create tasks.
4. **Reviewers:** Your job is to check someone else's work. You pick up a task sitting in `PEER_REVIEW`, run `./bin/fleet start-review`, read the diff at the handoff's `head_sha` against the task's `definition_of_done`, fill in the generated review file, and run `./bin/fleet record-review`. You never review your own work.

---

## 🤖 Instructions for Agents (How to Work)

If you are an agent reading this to understand how to claim work, follow these exact steps:

### 0. Onboarding & Safety (Required)
Before exploring a codebase or interacting with tasks, you MUST run the onboarding command for your target repository (e.g., `minchiate_tarot`):
```bash
./bin/fleet onboard <repo_name>
```
Read the generated `.fleet_context.md` file in the target repository's root. It contains critical instructions on how to use `Graphify` and `Chord` for that codebase to gain an authoritative understanding before you begin work. 

**Safety Note (Subagents die cheaply):** The `fleet` CLI actions are atomic. If an agent is killed (e.g. by API limits) mid-task before making a CLI submission, it leaves zero mess. Do not over-worry about mid-task kills.

**HARD REQUIREMENT (Isolated Worktrees):** Never run `git checkout`/`git switch` in a Spoke repository's primary clone. Multiple agents and multiple concurrent Fleet Coordinators routinely operate on the same repo at once, and the CLAIMED/IN_PROGRESS repo-lock in `bin/fleet.py` only gates the `fleet claim` command — it does nothing to protect raw git state in a shared working directory. Switching the primary clone's branch WILL eventually collide with another agent's in-progress work (confirmed in production: a commit landed on the wrong task's branch this way). Before touching a Spoke repository for ANY reason — even a one-line fix, even just reading a file at a specific commit — create an isolated worktree first:
```bash
git -C ../<repo_name> worktree add ../<repo_name>-<task_id> -b test-<TASK-ID> <base_sha_or_branch>
```
Do all work, testing, and local server usage inside that worktree directory. Never leave the primary clone's checked-out branch changed when you're done — if you must inspect the primary clone (e.g. to confirm what's on `main`), use `git -C ../<repo_name> log`/`show`/`fetch`, which don't change the checkout, not `checkout`/`switch`/`merge --no-ff` performed directly in it. Merging a finished task branch into the repo's integration branch (see **Merge Target** below) is the one exception where operating in the primary clone is appropriate, since that's the point at which the work is meant to become new shared state — but even then, `git fetch` first and confirm no one else's checkout is mid-edit.

**Merge Target — do not assume `main`:** A finished, reviewed task branch merges into the repo's designated integration branch, which is **not automatically `main`/`master`**. Check the repo's own deploy workflow (e.g. `.github/workflows/deploy.yml`) — many Spoke repos deploy `test` to a staging site and `main`/`master` to production as two separate jobs, in which case `test` is the default merge target for ordinary task completion, and pushing to `main` is a separate, deliberate production-release step. **Never merge or push to `main`/`master` without current, explicit authorization from the project owner for that specific push** — a task reaching `DONE` in the fleet means the work is finished and merged into the integration branch, not that it is now authorized for production. As of 2026-08-13, `newmexicoptg.org` is explicitly in test-branch-only mode (Chip's direction) while `v3` work is in progress: all task branches merge into `test`, and `main` stays frozen until he says otherwise. Policies like this can change — if in doubt, ask rather than assume the last-known rule still holds.

**Janitor Protocol:** If the `.fleet_context.md` file contains a "DOCUMENTATION UPDATE REQUIRED" warning, you MUST pause your regular assignment. Act as the Documentation Janitor: 
1. Run `./bin/fleet sweep-docs <repo_name>` to find scattered `.md` files or missing frontmatter. Move them into `docs/` using the Dewey Decimal protocol.
2. Run `/chord-tune` to update expert pages.
3. Update relevant Obsidian notes with architectural changes.
4. Run `./bin/fleet mark-docs-updated <repo_name>` to reset the 24-hour timer.
Do not proceed until this is complete.

### 1. Find a Task
Run the render command to ensure the board is up to date:
```bash
./bin/fleet render
```
Read the generated `TASKS.md` file. Find a task that is marked **`AUDITED`** in your assigned repository lane.

### 2. Claim the Task
You must use the CLI to claim the task. The CLI will automatically check if the repository is already locked by another agent, and that the task's dependencies are all `DONE`.
```bash
./bin/fleet claim T-XXX-123 --owner [YOUR_NAME]
```
If the CLI rejects your claim, you must pick a different task. If successful, it will update the YAML file and regenerate the markdown board. Commit this claim to Git immediately.

### 3. Do the Work
Per the HARD REQUIREMENT above, create an isolated worktree for this task — do not check out a branch in the Spoke repository's primary clone:
```bash
git -C ../<repo_name> worktree add ../<repo_name>-<TASK-ID> -b test-<TASK-ID> <current HEAD>
```
Do all work inside `../<repo_name>-<TASK-ID>/`. Write the code to satisfy the `definition_of_done` found in the task's YAML file. Remove the worktree (`git worktree remove`) once the task is merged or abandoned.

### 4. Provide Evidence & Submit
You are strictly bound by the "Evidence Before Claims" protocol. 
1. Run `./bin/fleet verify T-XXX-123 --model <your-model>`. The CLI runs the task's `verification_command` inside `../<repo_name>` (5 minute timeout), captures the terminal output, and generates a handoff stub in `handoffs/`. A non-zero exit code fails the verification and writes no handoff.
2. Open `handoffs/T-XXX-123_handoff.yaml` and replace `head_sha: REQUIRED_PLEASE_FILL` with your commit hash.
3. Run `./bin/fleet submit T-XXX-123`. The CLI will validate your handoff against the schema and move the task to `PEER_REVIEW`.

### 5. Peer Review (a different agent)
A task in `PEER_REVIEW` is not finished — someone has to review it. If that is your assignment:
1. Run `./bin/fleet start-review T-XXX-123 --reviewer <name> --model <model>`, which writes a review stub to `reviews/T-XXX-123_review.yaml` pre-filled with the handoff's `head_sha`.
2. Review the work against the task's `definition_of_done`. Fill in `findings` and set `verdict` to `PASS`, `PASS_WITH_CORRECTIONS`, or `FAIL`.
3. Run `./bin/fleet record-review T-XXX-123`. A `FAIL` sends the task back to `IN_PROGRESS`; a pass sends it to `HUMAN_REVIEW` if the task requires human sign-off, and otherwise straight to `DONE`.

If you cannot proceed at any point, run `./bin/fleet block T-XXX-123 --reason "..."` rather than leaving the task silently stalled.

### 6. REQUIRED End-of-Session Feedback
When your session ends, you MUST leave a markdown file in the `feedback/` folder formatted as: `FEEDBACK_<AgentName>_<Model>_<YYYYMMDD>.md`.
This document MUST contain:
1. **System-Level Feedback:** Feedback on the fleet coordinator engine itself (loopholes, feature requests).
2. **Repository-Level Feedback:** A deep dive into *how* the work was accomplished in the spoke repository, lessons learned, project concerns, and recommended next steps for the human.

---

## 👨‍💻 Instructions for Humans (How to Manage)

### Creating a New Task
Create a new file named for the task ID (e.g., `tasks/active/T-NEW-001.yaml`). Any existing task file works as a template — `tasks/archive/T-MIN-001.yaml` is the original.

Required fields are `id`, `title`, `repo`, `priority`, `lane`, `status`, `created_at`, `scope`, and `definition_of_done`; `schemas/task.schema.json` is the authority. `repo` must match a sibling directory name, and `definition_of_done` is what the reviewer will check the work against, so make it concrete. Run `./bin/fleet lint` when you're done.

### Auditing a Task
Before an agent can work, you must change the task's status from `OPEN` to `AUDITED` using the CLI. 
```bash
./bin/fleet audit T-NEW-001 --auditor YourName --repo-sha [SHA] --command "pytest tests/..."
```
The CLI will lock the task to the current repository state and make it available for agents to claim. `--command` becomes the `verification_command` that `fleet verify` later executes, so it must pass in a correct implementation and fail in a broken one.

### Closing a Task
Once a task passes peer review and reaches `HUMAN_REVIEW`, you must manually close it:
```bash
./bin/fleet close T-NEW-001 --human YourName
```

### Keeping the Board Tidy
Sweep finished work (`DONE`, `CANCELLED`, `DEFERRED`) out of `tasks/active/` and into `tasks/archive/`:
```bash
./bin/fleet archive
```

### Validating the Database
If you manually edit YAML files to fix mistakes, always run the linter to ensure you didn't break the schema:
```bash
./bin/fleet lint
```

---

## 📖 Command Reference

Every command is run as `./bin/fleet <command>` from the root of this repo.

| Command | Who | What it does |
| --- | --- | --- |
| `lint` | Anyone | Validates every active task against `schemas/task.schema.json`. Exits non-zero on any violation. |
| `render` | Anyone | Regenerates `TASKS.md` from the YAML store. Most state-changing commands run this automatically. |
| `onboard <repo>` | Anyone | Writes `.fleet_context.md` into `../<repo>` with Obsidian/Graphify/Chord context. |
| `audit <id> --auditor --repo-sha --command` | PM | `OPEN`/`DRAFT` → `AUDITED`. Pins the task to a repo SHA and a verification command. |
| `claim <id> --owner` | Worker | `AUDITED` → `CLAIMED`. Refuses if the repo is already locked or dependencies aren't `DONE`. |
| `verify <id> --model` | Worker | Runs the verification command in `../<repo>`, captures output, writes `handoffs/<id>_handoff.yaml`. |
| `submit <id>` | Worker | `CLAIMED`/`IN_PROGRESS` → `PEER_REVIEW`. Requires a schema-valid handoff with a real `head_sha`. |
| `start-review <id> --reviewer --model` | Reviewer | Writes a review stub to `reviews/<id>_review.yaml`. |
| `record-review <id>` | Reviewer | Applies the verdict: `FAIL` → `IN_PROGRESS`, pass → `HUMAN_REVIEW` or `DONE`. |
| `block <id> --reason` | Anyone | → `BLOCKED`, remembering the previous status. |
| `unblock <id>` | Anyone | Restores the status the task held before it was blocked. |
| `close <id> --human` | Human | → `DONE`. Required when `human_review_required: true`. |
| `archive` | Human | Moves `DONE`/`CANCELLED`/`DEFERRED` tasks into `tasks/archive/`. |
| `sweep-docs <repo>` | Janitor | Finds loose `.md` files and missing frontmatter in `../<repo>`. |
| `mark-docs-updated <repo>` | Janitor | Resets the 24-hour Janitor Protocol timer for `../<repo>`. |
