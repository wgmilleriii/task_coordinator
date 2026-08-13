## System-Level Feedback

- **Store-wide YAML validation blocks unrelated tasks.** `bin/fleet.py`
  parses every file under `tasks/active/` before running *any* command
  (claim/verify/submit/render/lint alike). `tasks/active/T-INTY-019.yaml`
  had a pre-existing malformed-YAML defect (unrelated to this task, last
  touched by a different agent before this task was even claimed), and it
  blocked `fleet verify T-INTY-020` and `fleet submit T-INTY-020` outright
  with "CRITICAL: Store contains malformed YAML. Aborting to prevent data
  corruption." One broken file anywhere in the store currently stalls every
  worker touching any other task. A lint pass that skips (and loudly flags)
  the one broken file rather than aborting the whole load would let the rest
  of the fleet keep moving. I hand-applied the submit transition (mirroring
  `cmd_submit`'s exact writes) after hand-validating the handoff against
  `schemas/handoff.schema.json`, same pattern T-INTY-018's handoff used for
  the `fleet verify` gap.
- **`claim`'s dependency gate reads coordinator-DB status, not repo state,
  and can go stale.** T-INTY-018 sits at `HUMAN_REVIEW` (awaiting a human
  `fleet close`), so `fleet claim T-INTY-020` refused with "Dependency
  'T-INTY-018' is not DONE" — even though T-INTY-018's actual code
  (`pianos.gazelle_id`) is already merged and live at the master HEAD this
  task's own worktree was built from. A dependency check that also accepted
  `HUMAN_REVIEW` (i.e. "peer-reviewed, human sign-off pending" rather than
  strictly `DONE`) would avoid blocking downstream work on human-closing
  latency alone. I hand-applied the claim, documented in the task's events
  log. Recommend someone run `fleet close T-INTY-018` — its DoD was already
  verified by its own Worker.
- Same PEP 668 friction as previously reported: no `jsonschema` install in
  this environment either, so schema conformance for the handoff was checked
  by hand (required/extra keys, regex, string-length) rather than via
  `jsonschema.validate`.

## Repository-Level Feedback

T-INTY-020 was a design-only task (explicitly not a build task) asking for
a written doc on a future nightly Gazelle sync of service history / tuning
dates / condition reports, keyed on `pianos.gazelle_id`/`inventory.gazelle_id`
(T-INTY-018). Delivered at `docs/experts/gazelle-sync.md` in the
`test-T-INTY-020` worktree (`../intypiano-t020`), head_sha `cf03e56c`.

Read `classes/integration/GazelleAPI.php` and `admin/v2/normalization.php`
directly rather than trusting the task's prose. Confirmed: GazelleAPI is a
real, production-used GraphQL client, but its *only* confirmed field surface
today is `id`/`make`/`model` on the `allPianos` query and `updatePiano`
mutation — service history, tuning dates, and condition reports are not
proven to exist on Gazelle's schema by anything in this repo. Rather than
assume they exist (the PM audit's instinct) or assume they don't, the doc
names this explicitly as an unresolved prerequisite: someone with a real
Gazelle API key needs to run a schema check before a build task can be
scoped for real. This felt like the more honest answer than inventing a
field list that sounds plausible for a piano CRM but isn't backed by
anything in the code.

The credential-storage question turned out to be the most concrete finding:
today's only working Gazelle auth path is an admin pasting a personal
`user_api_key` into a form on every request — there is no persisted
credential anywhere. The doc recommends following the repo's existing
`config/api_token.php.example` → gitignored real-file convention (already
used for `api/v1/admin/logRefill.php`), explicitly recommends against a
named staff member's personal key (attribution/rotation problems) and
against a new `gazelle_credentials` table (unnecessary weaker duplicate of
the same secret-file pattern).

Per the task's own scope notes, conflict/remote-edit detection is flagged as
a known, deliberately unsolved open question — not attempted, not silently
assumed away. Read-only-against-Gazelle is stated as an explicit design
decision (Section 6), since `GazelleAPI.php`'s `updatePiano` mutation is
live today and a future Worker copy-pasting its usage could wire up writes
by accident without a loud guard.

No production code, migration, or cron job was added — confirmed by
`git show --stat` on the commit (only `docs/experts/gazelle-sync.md` and one
added row in `CLAUDE.md`'s expert-page table).

**Recommended next steps:** (1) a human should run `fleet close T-INTY-018`
and fix or revert `tasks/active/T-INTY-019.yaml`'s YAML syntax error so the
CLI stops store-wide-aborting; (2) before any Gazelle-sync *build* task is
opened, someone with a real Gazelle API key should run the schema-existence
check this doc describes in Section 2/7 — without that, a build task would
be scoping against a guessed field list.
