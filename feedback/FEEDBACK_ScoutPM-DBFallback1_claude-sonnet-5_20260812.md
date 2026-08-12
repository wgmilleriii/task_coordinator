Scout+PM session for `intypiano`. Task: `T-INTY-021` (local dev DB fallback hardcodes nonexistent `caut_sfusd`). Wrote it OPEN, then re-read `classes/core/DatabaseManager.php` fresh as PM and audited it against `3cf4775d3561b3746c6e55586921beb4492ec57d`.

## System-Level Feedback

- `./bin/fleet lint` reports a pre-existing schema violation on `tasks/active/T-INTY-017.yaml` (`'dod' was unexpected` — presumably meant `definition_of_done`). It is not something I touched or introduced; leaving it for whoever owns that task, but the lint output is easy to misattribute to your own just-written task if you don't diff carefully. A `fleet lint <task_id>` single-task mode would have let me confirm my own file cleanly without eyeballing which error belonged to which task.
- `fleet audit` doesn't execute the `--command` at audit time — it just stores it. That's reasonable (avoids a slow/flaky PHPUnit run blocking the audit step) but means a PM can audit a task with a syntactically broken verification command and nothing complains until a Worker runs `fleet verify`. Worth a `--dry-run-command` flag or at least a warning if the command references a binary/path that doesn't exist in the repo.

## Repository-Level Feedback (intypiano)

Confirmed the reported bug and found it's substantially worse in scope than the initial framing suggested:

- `classes/redditlite_base.php:8` sets `public $app="cauttools";` as the **class default** — nearly every entry point (`admin_header_base.php`, `admin/v2/_guard.php`, `scripts/migrate.php`, most of `api/*.php`, the PHPUnit `Integration` tests) also explicitly re-sets `$r->app = "cauttools"` anyway. So the buggy branch in `DatabaseManager.php` (lines 267-291) is not an edge case — it's the normal path for essentially all local dev and CI traffic.
- `git blame` on lines 267-291 attributes the whole cauttools sub-branch, including the `caut_sfusd` hardcoded else-default, to a single commit: `8dbcaeb9` ("Demo pool: ten pre-built slots, hostname mapping, and a 14-day reset", 2026-08-11). There's no earlier commit where this fallback pointed somewhere else — it was born broken alongside the (working) demo-pool port logic, not a regression of previously-good code. `config.php`'s `sfusd` override also resolves to `caut_sfusd`, so there's no config-side escape hatch locally either.
- Confirmed **V1 admin is equally affected**, not just `admin/v2/*` as the initial bug report focused on: `admin_header_base.php` sets `$r->app = "cauttools"` and calls `init()` identically to `admin/v2/_guard.php`. This matches the magnitude of the observed PHPUnit blowup (259/0 baseline → 330 tests, 18 errors, 114 failures).
- I judged this a low-risk, well-bounded fix — a dispatch/fallback default in a `localhost`-only branch, no schema or migration involved — and audited it directly rather than leaving it OPEN for a second PM pass. Scope explicitly fences off the demo-pool port range (8001-8010) as untouchable and restricts the fix to the else-branch default plus its config.php interaction.

Recommended next step: a Worker claims `T-INTY-021`, points the else-branch default at `intypiano_demo` per `CLAUDE.md`, and confirms via a fresh `phpunit` run (server on port 2027) that the error/failure count drops substantially and no admin/v2 or V1 admin page throws `Unknown database` anymore.
