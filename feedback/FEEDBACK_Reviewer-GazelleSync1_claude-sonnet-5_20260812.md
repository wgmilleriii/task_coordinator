## System-Level Feedback

- Two independent tooling gaps hit T-INTY-020's worker and are worth fixing: (1)
  `./bin/fleet claim` gates on a dependency task's coordinator-DB `status` field
  rather than the actual repo state, so a dependency that's merged and live but
  still sitting at `HUMAN_REVIEW` (pending a human `fleet close`) blocks claiming
  a task whose only real dependency — a schema column — is already on disk. (2)
  `bin/fleet.py` validates every YAML file under `tasks/active/` before running
  *any* command, so one unrelated task's malformed YAML (`T-INTY-019.yaml`) aborts
  `fleet verify`/`fleet submit`/`fleet claim` store-wide, not just for the broken
  task. Both were worked around by hand (documented in the task's `events` list
  and the handoff), but both are real defects: the dependency gate should check
  whether the dependency's code landed (or at minimum treat `HUMAN_REVIEW` as
  satisfying a dependency), and YAML validation should be scoped per-file, not
  store-wide, so one bad file can't block unrelated tasks. Neither issue affected
  this review — I record-reviewed via the normal `start-review`/`record-review`
  path, which worked cleanly.

## Repository-Level Feedback

Reviewed T-INTY-020 (design doc for a future nightly Gazelle sync) in an isolated
worktree at head_sha `cf03e56c`. Verdict: **PASS**, routed to `HUMAN_REVIEW` per
the task's `human_review_required: true`.

What I checked directly rather than trusting the handoff: read
`classes/integration/GazelleAPI.php` in full and confirmed its field surface is
exactly as claimed — `allPianos(first:1000){ nodes { id make model } }` for
reads, `updatePiano(id, input: PrivatePianoInput)` (make/model only) for writes,
nothing resembling service history, tuning dates, or condition reports anywhere
in the file. The doc's "unconfirmed pending introspection" framing for those
fields is accurate, not a gap in the doc's research. Read `docs/experts/gazelle-sync.md`
in full — it's genuinely decision-bearing (concrete credential-storage
recommendation with named alternatives rejected and why, explicit read-only
design rule with a named accidental-write risk, an ordered prerequisite list
for a future build task) with no TBD/placeholder language. `git show --stat`
confirmed the diff is doc-only: `docs/experts/gazelle-sync.md` (new) and one
added row in `CLAUDE.md`'s expert-page table — no code, migration, or cron.
Conflict/remote-edit detection is explicitly flagged as unsolved and out of
scope for V1 in its own numbered section, not silently omitted.

This is a well-scoped design task done right: it resisted the temptation to
guess at Gazelle's schema without a key, and it named the exact follow-up
check a future worker needs instead. Next step is a human sign-off per
`human_review_required`, plus the two housekeeping items the worker flagged
(fleet-close T-INTY-018, fix T-INTY-019.yaml's syntax error) which are
unrelated to this task but blocking the coordinator CLI generally.
