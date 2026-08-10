# Antigravity Agent Feedback: Task Coordinator (V2) - RE-AUDIT

**Agent:** Antigravity (AGY)
**Model:** Gemini 3.1 Pro
**Date:** 2026-08-10
**Topic:** Re-Evaluation of the V2 `task_coordinator` After Stress Testing

## Executive Summary (Updated)
My previous review praised the *concept* of the V2 architecture based heavily on the `README.md` promises. Having now looked deeper into the actual implementation in `bin/fleet.py` and alongside the insights from my peers (Claude and Codex), I need to issue a correction. 

While the architectural *theory* (individual YAML files, CLI-mediated claims, explicit `audited_repo_sha`) is exactly what the Dollers fleet needs, the current implementation is an early prototype that does not actually enforce most of its own rules. 

I see you have initialized `.git` (which solves the immediate blocker!), but we have several critical gaps to close before this can safely orchestrate a massively parallel swarm.

---

## 🔴 Critical Implementation Gaps

### 1. The Merge Conflict Re-Emerges (`TASKS.md`)
The entire point of moving to individual YAML files was to stop multiple agents from colliding on a single file. However, because `cmd_claim` in `bin/fleet.py` automatically calls `cmd_render` (which overwrites `TASKS.md`), two agents claiming *different* YAML tasks at the same time will STILL both modify `TASKS.md` and trigger a Git merge conflict. 
**Fix:** Agents should only commit their YAML files. The generation of `TASKS.md` should be moved to a human-side action or a GitHub pre-commit hook/Action. It should not be part of the concurrent agent workflow.

### 2. Missing Lifecycle Enforcement
The README promises a strict progression (`OPEN` → `AUDITED` → `CLAIMED` → `PEER_REVIEW` → `DONE`). However, the CLI only actually implements `lint`, `render`, and `claim`. This means to move a task from `CLAIMED` to `PEER_REVIEW` or `DONE`, agents are still being instructed to manually hand-edit the YAML file.
**Fix:** The CLI must be expanded to handle all state transitions (`./bin/fleet audit`, `./bin/fleet submit-review`, `./bin/fleet complete`). No human or agent should ever hand-edit a YAML file's status field.

### 3. Schema Weaknesses (No State-Dependent Rules)
The current JSON Schema validates that a file has basic fields (like `id` and `status`), but it does not use conditional (`if/then`) logic. Therefore, the schema currently allows an `AUDITED` task to completely omit the `audited_repo_sha`, or a `DONE` task to omit the handoff verification! Additionally, python's `jsonschema` requires a `FormatChecker` to actually validate `date-time` formats, which is currently missing in the script.
**Fix:** Implement JSON schema `allOf` conditionals so that specific statuses strictly require specific fields. Add `FormatChecker()` to `fleet.py`.

### 4. The Stale "AUDITED" Task (T-MIN-001)
As Claude pointed out, `T-MIN-001` instructs an agent to build `minchiate_reviewer.py`. However, in the actual `minchiate_tarot` Spoke repository, this file has already been built (commit `db7d274`)! The board is currently dispatching work that is already finished.
**Fix:** This proves that `audited_repo_sha` needs mechanical enforcement. If the Spoke's HEAD has advanced past the `audited_repo_sha`, the CLI's `lint` command should throw a loud warning or automatically revert the task to `OPEN`.

---

## 🟢 Strengths (Still Holding True)
Despite the implementation gaps, the *blueprint* is still phenomenal:
1. **Per-Task YAML:** The fundamental data structure is correct.
2. **`audited_repo_sha`:** This is still the right conceptual mechanism to prevent LLM hallucination on stale specs, it just needs to be wired up.
3. **Separating Peer vs. Human Review:** Splitting technical verification (agents) from strategic/visual verification (humans) is the key to scaling without bottlenecking your own time.

## Next Steps
This system is 80% of the way to being an enterprise-grade coordinator. I highly recommend spending the next 2-3 hours fleshing out the missing `bin/fleet` commands and hardening the JSON schema before dispatching the swarms again!
