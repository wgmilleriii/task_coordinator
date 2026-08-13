# Feedback: Worker-MigrateSafety1 (claude-sonnet-5) — 2026-08-13

Task: T-INTY-023 (intypiano) — master_migrate.php unm_piano protection,
sql_scripts_applied tracking, dynamic system_hub.php launcher.

## System-Level Feedback (task_coordinator itself)

1. **`fleet claim` blocks correctly, but there's no wait primitive.** When
   T-INTY-022 held the intypiano repo lock, `fleet claim` just failed with a
   clear error — good — but there's no `fleet wait <task_id>` or similar to
   block until a lock clears. I ended up hand-rolling a polling loop with the
   Monitor tool, which the Fleet Coordinator then had to explicitly tell me
   to stop (per the harness's own guidance that background monitors can't
   usefully carry state across agent turns). A built-in `fleet wait-for-lock
   <repo>` (blocking, with a sane timeout) would remove this whole dance and
   let a worker just ask "let me know when I can claim."

2. **`fleet verify` runs the verification_command in the repo's primary
   clone, not the worker's isolated worktree.** This is a real gap given the
   README's own HARD REQUIREMENT to do all work in a worktree. For this task
   it happened to be harmless (`php -l` passes identically on the old and
   new file — a syntax check can't tell the difference), but for any
   verification_command that actually exercises behavior (grep for a
   specific string, run a script, hit an endpoint) this would silently
   verify the wrong code — the *primary clone's* unmodified files, not the
   worker's actual changes — and could produce a false pass. I worked around
   it by hand-editing the handoff's `evidence_output` to include the real
   verification run from the worktree with an explicit note flagging the
   discrepancy, and correcting `branch`/`base_sha`/`head_sha` (which `fleet
   verify` had also filled in from the primary clone's `master`, not my
   worktree branch). Suggest `fleet verify` accept a `--cwd`/`--worktree`
   flag, or infer the worktree path from the task's active branch
   convention (`../<repo>-<task_id>`), and run the command there.

3. **Shared, uncommitted state in this very repo made `git add` risky.**
   When I went to commit my `fleet claim`, `git status` showed a pile of
   unrelated staged changes (other in-flight PTG-lane tasks' handoffs,
   feedback files, a `dashboard/` directory) that I didn't create. I had to
   `git reset` and re-stage only my two files by explicit path to avoid
   accidentally committing someone else's in-progress work under my name.
   This is a general hazard of multiple concurrent workers sharing one
   non-worktree'd coordinator clone (the coordinator repo itself doesn't get
   the worktree treatment intypiano does) — worth considering whether
   task_coordinator should isolate its own git operations per-worker too, or
   at minimum document "always `git add <specific files>`, never `-A`" more
   loudly for the coordinator repo specifically, not just spoke repos.

4. Otherwise the claim → worktree → verify → submit flow worked exactly as
   documented and was easy to follow end to end.

## Repository-Level Feedback (intypiano)

**What I found:** `master_migrate.php` looped over every tenant in
`config.php`'s `$db_configs` (including `unm` → `dbname: unm_piano`) and ran
arbitrary SQL from `sql_scripts/*.sql` against each one via a raw PDO
connection, with zero exclusion list — unlike `scripts/bootstrap_v2_db.sh`,
`scripts/migrate.php`, and `scripts/data_quality.php --fix`, which all
refuse `unm_piano`/`unm_piano_readonly`/`unm_piano_test` by name. Any file
dropped in `sql_scripts/` and launched via `system_hub.php`'s one hardcoded
link ran against the real production-mirroring database with no record kept
anywhere of what had already been applied.

**What I changed:**
- `master_migrate.php`: added a `PROTECTED_DBNAMES` check inside the
  per-tenant loop, matched against the tenant's actual configured `dbname`
  (not the `$db_configs` array key, per the task's own reasoning that a
  tenant could be renamed/aliased). A skip prints a clear `[SKIPPED]` line
  and the tenant is counted separately from success/fail in the summary —
  never silent.
- New `sql_scripts/system/create_sql_scripts_applied.sql` — an idempotent
  `CREATE TABLE IF NOT EXISTS sql_scripts_applied` for `caut_central`.
  Deliberately placed in a `system/` subdirectory so it's invisible to both
  `system_hub.php`'s `glob('sql_scripts/*.sql')` and to
  `master_migrate.php`'s own `basename()`-based file lookup — it can't be
  accidentally launched against every tenant through the generic `?file=`
  mechanism. `master_migrate.php` runs it against `central` once per
  invocation before the main loop; failure to do so degrades gracefully
  (tracking disabled, warning printed, migration still proceeds) rather than
  blocking the run.
- `master_migrate.php` now writes one `sql_scripts_applied` row per
  *attempted* tenant (skipped/protected tenants get no row, since they were
  never run) with `applied_by` from `$_SESSION['email']` (web) or
  `get_current_user()` (CLI).
- `system_hub.php`'s hardcoded "Global Migrations" link is now a loop over
  `sql_scripts/*.sql`, cross-referenced against `sql_scripts_applied`,
  showing only files not yet successfully applied to every *effective*
  (non-protected) currently-configured tenant. A file fully applied
  everywhere it's allowed to run drops off the list.

**Design call worth flagging for review:** "every currently-configured
tenant" in the task's Part 3 wording — I interpreted this as every tenant
*except* the protected ones, since a protected tenant can now never receive
a successful row (it's permanently skipped by Part 1), which would
otherwise make every file permanently "pending" forever and defeat the
purpose of the list. This seemed like the only construction that makes both
Part 1 and Part 3 coherent together, but it's a judgment call the task
didn't spell out explicitly and a reviewer should sanity-check.

**Verification approach:** I did not trust `php -l` alone (it can't
distinguish old vs. new file content) and did not want to risk the real
`unm_piano`/`unm_piano_readonly`/`unm_piano_test` databases even locally, so
I built a gitignored `config_local.php` (never committed — confirmed
`.gitignore` line 33 already covers it) that pointed a fake `unm` tenant at
the *real* protected dbnames plus a disposable scratch tenant, and ran the
actual CLI and web flows against that. This let me directly confirm via
`SHOW TABLES` against `unm_piano`/`unm_piano_readonly`/`unm_piano_test` that
zero connections were ever opened to them (not just that the code *looks*
like it would skip them). Also ran the full phpunit suite before and after
(via `git stash`) to rule out any regression — found 68 pre-existing
failures/1 error unrelated to this change, present on the base commit either
way.

**Next steps / open items for the project owner:**
- The 68 phpunit failures / 1 error on current `master`
  (`c6ccca5e`) are pre-existing and unrelated to this task, but they mean
  the CLAUDE.md-documented "259 tests, 0 failures" baseline is now stale —
  worth a dedicated triage pass since it's currently impossible to tell a
  real regression from this pre-existing noise without a manual diff run
  like the one I did here.
- `sql_scripts_applied` is intentionally empty after this change — none of
  the 13 existing `sql_scripts/*.sql` files were auto-marked applied, per
  the task's explicit instruction not to guess at unrecorded history. That
  means `system_hub.php` will show *all 13* as pending on first load in
  production, which is accurate (their real applied-state genuinely isn't
  known) but will look alarming; worth a heads-up to whoever reviews this
  before it ships, so it doesn't read as "13 migrations suddenly appeared
  and need running."
- This task explicitly did not touch the `ddl/` + `scripts/migrate.php`
  system, per scope. Two parallel migration mechanisms with different
  safety postures continuing to coexist is still worth a future
  architectural look, just not as part of this task.
