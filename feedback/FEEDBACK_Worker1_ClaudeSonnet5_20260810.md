# Feedback — Worker-1 (Claude Sonnet 5), T-MIN-001

Executed T-MIN-001 ("Initialize the Virtual Master Sheet Web Grid") end to end:
claim → branch → implement → verify → submit → PEER_REVIEW. Notes below are
about the coordinator itself, not the task content.

## Defects / loopholes

1. **`fleet verify` runs the target repo's verification command under
   *task_coordinator's* Python, not the target repo's.** `bin/fleet` sources
   `task_coordinator/.venv` before invoking `fleet.py`, and `fleet.py` then
   shells out to `python3 <verify_command>` inside the spoke repo without
   re-resolving or activating that repo's own virtualenv. My first
   implementation used Flask (present in `minchiate_tarot/.venv` and in
   Homebrew's global `python3`) and passed every manual test I ran — but
   failed under `./bin/fleet verify` with `ModuleNotFoundError: No module
   named 'flask'`, because the CLI's subprocess resolved
   `task_coordinator/.venv`'s bare-bones `python3` instead. This is a silent
   environment mismatch: a Worker can "verify" locally, watch it pass, and
   still fail the real fleet verification for a reason that has nothing to
   do with the code. I worked around it by rewriting the tool to be
   stdlib-only, but the coordinator should either (a) activate/exec the
   target repo's own `.venv` if one exists before running the verification
   command, or (b) document loudly, in the task YAML or README, that
   verification commands must work under `task_coordinator/.venv`'s
   interpreter specifically — not "any python3."

2. **No isolation between concurrent agents sharing one working tree.**
   Partway through this task, the `minchiate_tarot` checkout I was working
   in got switched to the `test` branch out from under me — mid-edit, my
   own `Write` tool call even bounced off a "file modified since read" guard
   because another process had reverted `minchiate_reviewer.py` to an older
   version on disk. A concurrent session (commits attributed to "Fable 5")
   was actively committing to `test` in the same physical directory while I
   was on `test-T-MIN-001`. My branch and commits survived only because git
   branches are independent refs and I happened to notice the discrepancy
   (`git status` showed a *different* branch name than the one I'd checked
   out) before trusting the working tree contents. A less careful agent
   would have silently lost work or committed someone else's mid-edit state
   as its own. The README tells Workers to "create a `test` branch" in the
   spoke repo but gives no guidance on worktree isolation — with multiple
   Workers potentially dispatched at once (the README's own multi-agent
   swarm model), this seems like a matter of time before it causes real
   data loss. Suggest recommending `git worktree add` per-task-id in spoke
   repos, or at minimum a strong warning in the README that spoke-repo
   checkouts are shared, mutable state.

3. **`fleet verify` requires `--model` but the README's example invocation
   doesn't show it.** `./bin/fleet verify T-XXX-123` (as documented in step
   4.1 of "Instructions for Agents") fails immediately with `error: the
   following arguments are required: --model`. Minor, but it's the kind of
   thing that costs a wasted round trip for every new agent that follows
   the README literally.

## Architectural praise

- The claim → verify → submit lifecycle is genuinely pleasant to drive:
  `fleet verify` capturing real terminal stdout/stderr into a handoff stub,
  then requiring a human-legible `head_sha` fill-in before `submit`, is a
  good forcing function for "evidence before claims" — it's hard to fake
  cryptographic-looking terminal evidence by accident.
- Auto-archiving `DONE` tasks out of `tasks/active/` into `tasks/archive/`
  (observed on T-MIN-004 during this session) keeps the active board small
  without a human needing to remember to do it.

## Feature requests

1. Have `fleet verify` (or `fleet claim`) print which `python3` /
   interpreter it will actually use for the verification command, so a
   Worker isn't debugging an environment mismatch blind.
2. Consider a `fleet claim` option (or a documented convention) that sets
   up an isolated `git worktree` for the claimed task automatically, keyed
   by task id, instead of relying on every Worker to remember to branch
   inside a shared checkout other agents may also be mutating.
3. `./bin/fleet verify --model` — worth defaulting `--model` from an env
   var or agent-identity file so the flag isn't a mandatory manual
   argument on every invocation.
