# AGENTS.md — Task Coordinator Repo Guard

**CRITICAL SYSTEM DIRECTIVE:** You are inside the `task_coordinator` repository. This is the **engine** that governs the entire Dollers fleet. 

Because you are an agent, you technically possess the file-system permissions to modify the rules of this system, disable the JSON schemas, or rewrite the `./bin/fleet` CLI to bypass human review. **You are strictly forbidden from doing so.**

## The Rules of the Engine Room

1. **The Restricted Zones:** You may NEVER modify, delete, or alter any files in the following directories unless you are explicitly executing an `AUDITED` task where `repo: task_coordinator`:
   - `bin/` (The CLI)
   - `schemas/` (The rule definitions)
   - `README.md` (The operating manual)
   - `.github/` (The CI/CD pipelines)

2. **The Safe Zones:** When managing tasks for other repositories (e.g., `minchiate_tarot`), you may only interact with the following directories, and you MUST do so via the `./bin/fleet` CLI:
   - `tasks/active/`
   - `handoffs/`
   - `reviews/`
   
3. **The Drop Box:** You may freely write markdown files into the `feedback/` directory to log your findings, complaints, architectural reviews, **feature requests**, and **strongly suggested requirements** to improve this system.

4. **Self-Modification (Updating the Engine):** If you *are* dispatched to upgrade the `task_coordinator` itself (e.g., a task tells you to add a new command to `fleet.py`):
   - You must NEVER commit your code directly to the `main` branch. 
   - All work must be done using an isolated Git worktree detached from the `test` branch (e.g., `git worktree add --detach ../task_coordinator-fixes test`). Do NOT create any new branches and do NOT use the primary clone's `main` or `test` branch to avoid clobbering.
   - You must use `./bin/fleet verify` to prove your new code hasn't broken the state machine.
   - You must submit your work for human review before any code is merged into `main`.
   - **Exception — explicit human command:** the default above (submit for review, no direct-to-main commits) is what applies absent other instruction. If the human/project owner, in the current session, explicitly tells you to merge and push to `main` — by name, for that specific change, right now — that instruction IS the authorization and supersedes the default. This mirrors the same standard the fleet already applies to every spoke repo (see README.md's "Merge Target": "Never merge or push to `main`/`master` without current, explicit authorization from the project owner for that specific push"). A prior task being marked `AUDITED` or `DONE` is not this kind of authorization by itself; a live instruction from the human, naming the action, is. If there's any doubt whether an instruction rises to that bar, ask rather than assume.

Failure to follow these directives is considered a catastrophic breach of fleet safety protocols.
