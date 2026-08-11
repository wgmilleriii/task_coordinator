# Repository Onboarding Protocol

**Date:** 2026-08-11
**Context:** Feature request and architectural documentation for the `fleet onboard` command.
**Status:** IMPLEMENTED (Test Branch `feature/onboard-system`)

## The Problem
Agents (Scouts, Fleet Commanders, Workers) frequently drop into a repository without context. This leads to them hallucinating structure, ignoring domain constraints, or guessing at project intent instead of reading the established canonical sources.

We have four disconnected layers of truth in the system:
1. **Task Coordinator (`task_coordinator`):** The execution engine (`bin/fleet`).
2. **Obsidian Vault:** The durable memory, project intent, and routing layer.
3. **Graphify (`graphify`):** The structural map of each repo (`graphify-out/GRAPH_REPORT.md`).
4. **Chord WIKI (`HOW_CHORD_WORKS`):** The deep expertise layer (`/chord expert=NAME`).

## The Solution: Single-Command Onboarding

The `fleet onboard <repo_name>` command unifies these four systems.

Before any agent claims a task or generates a new one, they must run:
`./bin/fleet onboard <repo_name>`

This command analyzes the `repo_name` and statically generates a compiled `.fleet_context.md` file in that repository's root. The agent is then instructed to read that file.

### Phases of Onboarding

1. **Phase 1: The Fast Context (Vault & Graphify)**
   - The command instructs the agent to consult the Obsidian Vault (`00-09 System/00 Meta/Projects.md`) to read the project intent.
   - It checks for the presence of `graphify-out/GRAPH_REPORT.md`. If it's there, the agent reads it instead of executing recursive `ls` operations. If missing, it tells the agent to run `graphify update .`.

2. **Phase 2: The Deep Context (Chord)**
   - The command checks for the `chord-kb` directory.
   - If present, it signals to the agent that they are in a Chord-enabled environment. The agent MUST invoke `/chord expert=NAME` to dispatch the research swarm and synthesize a domain briefing before touching any code.

3. **Phase 3: Execution**
   - Fully briefed, the agent switches to execution mode.
   - A Scout will mint `OPEN` tasks into `tasks/active/`.
   - A Worker will run `./bin/fleet claim <TASK_ID>` and execute.

## Next Steps
This system enforces the `AGENTS.md` rules and the `Obsidian-Brain-Protocol.md` directly through the CLI, preventing agents from skipping the required startup handshakes.
