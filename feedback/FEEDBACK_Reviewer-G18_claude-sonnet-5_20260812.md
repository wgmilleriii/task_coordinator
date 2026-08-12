---
title: "Reviewer Feedback: T-INTY-018 (gazelle_id column)"
created_at: "2026-08-12T19:10:00Z"
last_modified: "2026-08-12T19:10:00Z"
author: "ReviewerSonnet5"
status: "active"
category: "00-Meta"
---

## System-Level Feedback

- `fleet verify`'s automated re-run of `verification_command` runs against a
  fixed checkout location rather than the worker's own worktree, and doesn't
  guard against a stale process already bound to the port the command
  hardcodes (`localhost:2027`). This produced a spurious 1/74-shaped result
  for the Worker on this task and forced a manual override in the handoff
  (`evidence_output` had to be hand-captured with an explanation). Same gap
  T-INTY-021 already flagged. Suggest either (a) parameterizing `fleet
  verify` to run from the worktree it's told about, with a free-port probe,
  or (b) moving "no NEW failures beyond baseline X" comparisons out of a raw
  exit-code check and into something `fleet verify` can evaluate structurally
  (e.g. diffing named failures against a checked-in baseline file) instead of
  relying on worker narrative plus reviewer re-verification to catch the gap
  every time.
- The review workflow (isolated worktree, independent DB queries, independent
  phpunit run, name-for-name failure diff against a cited prior baseline) worked
  well for a schema/data-migration-class task and caught nothing wrong — but it
  is expensive (full worktree checkout, live DB connection plumbing since
  `DatabaseManager` is hostname-gated and can't be pointed at a local db via
  simple mysqli creclaudential in a CLI script, had to route through the app's
  own `Redditlite`/`DatabaseManager` bootstrap). Might be worth a documented
  reviewer helper script for this repo specifically, since this DB-connection
  friction will recur on every future intypiano DB-touching review.

## Repository-Level Feedback

Reviewed T-INTY-018 (add `gazelle_id VARCHAR(24) NULL UNIQUE` to `pianos` and
`inventory`, decoupled from `piano_code`) at head_sha `6d955d99` in an isolated
worktree (`../intypiano-t018-review`), separate from both the shared working
copy and the Worker's own worktree at `../intypiano-t018`.

Every claim in the handoff checked out under independent verification, not
just narrative review:

- All 5 `ddl/146/*` files read directly — additive only, `piano_code` is
  never written by any of them, backfill filtered on
  `piano_code REGEXP '^[0-9]+$'`, verify script asserts `missed=0` /
  `overreach=0` per table (not just row counts).
- The Worker's central corrective claim — that the PM audit's "all 126
  piano_code values are Gazelle IDs" was wrong, and only 42/126 are actually
  digit-shaped — was independently re-verified with my own live query against
  `intypiano_demo`: `total=126, digit_like=42, has_gazelle=42, fabricated=0,
  missed=0` for both tables. This matches both the Worker's number and the
  PM's own pre-dispatch spot check. This is exactly the kind of scope
  correction this fleet's audit→work→review pipeline should be catching, and
  it worked as designed here — the original scout/PM assumption was wrong,
  the Worker caught it during implementation, and both my own query and the
  PM's independent check confirm the correction rather than just trusting the
  narrative.
- `import_sfusd.php` diff confirmed `piano_code`'s own INSERT value/position
  unchanged; `gazelle_id` added alongside it with an inline comment stating
  the product decision (piano_code keeps mirroring the Gazelle ID for QR
  continuity).
- phpunit independently run from a fresh server: 330/666/1/68, and the 69
  failing/error test identifiers diffed byte-for-byte against the
  T-INTY-021 baseline (extracted via `yaml.safe_load` since the block scalar
  has escaped newlines) — zero differences.
- `docs/experts/schema-catalog.md` updated with the corrected 42/126 finding
  and the inventory/pianos non-sync landmine.

Verdict: **PASS**, verdict recorded via `./bin/fleet record-review T-INTY-018`.
Because `human_review_required: true` on the task, this moved status
`PEER_REVIEW` → `HUMAN_REVIEW` (not `DONE`) per `bin/fleet.py`'s
`record-review` logic — a human still needs to run `./bin/fleet close` for
this to land. No corrections requested; this is a clean, well-scoped,
well-evidenced schema change.
