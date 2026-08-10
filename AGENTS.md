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
   
3. **The Drop Box:** You may freely write markdown files into the `feedback/` directory to log your findings, complaints, or architectural reviews of the system.

4. **Self-Modification (Updating the Engine):** If you *are* dispatched to upgrade the `task_coordinator` itself (e.g., a task tells you to add a new command to `fleet.py`):
   - You must NEVER commit your code directly to the `main` branch. 
   - You must create a `test` branch.
   - You must use `./bin/fleet verify` to prove your new code hasn't broken the state machine.
   - You must submit your work for human review before any code is merged into `main`.

Failure to follow these directives is considered a catastrophic breach of fleet safety protocols.
