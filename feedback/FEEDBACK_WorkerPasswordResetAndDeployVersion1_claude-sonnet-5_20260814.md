# Feedback: Worker-PasswordResetAndDeployVersion1 (claude-sonnet-5), 2026-08-14

Session summary: NOT dispatched through `./bin/fleet` at any point — a human
(Chip) talked to me directly in the `intypiano` repo across a single long
conversation, no task claim, no worktree, no `fleet submit`. Work done, in
order: (1) audited production report data for the `sfusd` tenant via the
read-only `api/v1/admin/query.php` endpoint, found and fixed three report
bugs; (2) built a deploy-time version/changelog system; (3) root-caused and
fixed a `password_resets` schema/code column-name mismatch that has silently
broken password reset since `ddl/140` shipped. Items 1 and 2 are committed
and pushed. Item 3 is verified locally but **left uncommitted** at the
user's "exit according to the rules of the task_coordinator project"
instruction, which I'm interpreting as "write the required feedback," not
"silently commit pending work first" — see Repository-Level Feedback for the
exact uncommitted state.

## System-Level Feedback

1. **This entire session happened completely outside the fleet's visibility.**
   No task was claimed, no worktree was created, no `handoffs/` entry exists
   for any of this work — three real fixes (one of them a password-reset
   outage affecting every tenant) landed on `master` with no fleet task
   record at all. This isn't a complaint about the tool; it's a structural
   gap worth naming: the README's protocol only has teeth when an agent
   actually enters through `./bin/fleet onboard`. A human who opens a
   terminal and talks to an agent directly in a spoke repo — which is a
   completely ordinary way to use Claude Code, not a misuse — produces work
   the coordinator has no record of. If the project wants the task board to
   be a reliable single source of truth for "what happened to this repo,"
   it may need either (a) a lightweight way to *retroactively* register
   ad-hoc work as a task/handoff after the fact, or (b) an explicit
   acknowledgment that direct human-agent sessions are a second, legitimate,
   untracked channel and the fleet board is a partial view, not the whole
   picture.

2. **Confirmed directly: this repo has multiple concurrent sessions editing
   the same primary clone's `master` in real time, exactly as the README's
   HARD REQUIREMENT warns about.** While I had local uncommitted changes to
   `.github/workflows/deploy.yml`, `git fetch` showed the human (or another
   agent working with them) had already pushed a fix for a real bug I'd
   introduced in that same file minutes earlier (a bare `${{ }}` inside a
   `run:` step's shell *comment* — GitHub Actions scans `run:` blocks for
   `${{ }}` expressions even inside `#` comments, and an empty one is
   invalid syntax, which silently blocked every workflow run repo-wide,
   `workflow_dispatch` included, with no visible failure — the run simply
   never appears). Two more commits landed on `origin/master` after that
   (`391fcdf1`, `8a3882f5`) extending the exact feature I'd just built,
   before I ever got to `git push` again. I never touched the primary
   clone's branch pointer directly (no `checkout`/`switch`), only
   `fetch`/`rebase`/`push`, so nothing broke, but this is a live
   demonstration of why the HARD REQUIREMENT about worktrees exists — this
   session should probably have been in one too, and wasn't, because no
   fleet task ever put it there.

3. **Worth flagging for whoever owns `${{ }}`-in-comments as a general
   hazard, not just an `intypiano` one:** any workflow YAML with a `run:`
   block containing a shell comment that happens to mention GitHub Actions'
   own `${{ }}` syntax (e.g., documenting "don't use `${{ }}` here for
   security reasons," which is exactly what I was doing) will break that
   workflow. `python3 -c "import yaml; yaml.safe_load(...)"` does **not**
   catch this — the file is syntactically valid YAML; the parse failure
   happens in GitHub's own expression-scanning pass over `run:` strings,
   which no offline tool I had access to could check. If any other spoke
   repo's workflows follow the same "explain the safe pattern in a comment"
   convention that `security-guidance` plugin nudges toward, they're at
   risk of the identical silent breakage.

## Repository-Level Feedback (intypiano)

### 1. SFUSD report audit + fix (committed, pushed: `a9d3f5b5`)

Asked to audit production reports for the `sfusd` tenant. Given a
short-lived read-only diagnostic bearer token by the human (kept in-memory
only, never written to a file). Ran each report's exact SQL from
`classes/core/report_queries.php` against live `caut_sfusd` and found:
`inventory_status` and `unserviced_pianos` both still read the legacy v1
`inventory` table, which is empty (0 rows) for this tenant (162 rows exist
in `pianos` instead) — silently rendering zero rows while reporting success.
`weekly_status` `INNER JOIN`ed the legacy `tuner` table (also 0 rows for
this tenant, and structurally *can never* be populated for a pure-v2
tenant, since assignment now flows through `users`). Root cause: this file
had drifted out of sync with `classes/get_report.php`, which a **prior**
session had already fixed to be fully v2-native — `report_queries.php`'s
own header comment claimed the two files were kept identical by
construction, and they weren't. Ported the corrected SQL over. Verified
against live `caut_sfusd` (0 rows → 137 rows) and against `intypiano_demo`
(a tenant where the legacy tables happen to still agree with v2 data, to
prove no behavior change there: 39 rows both before and after). Full suite
unaffected (confirmed via `git stash` diff of failure counts).

### 2. Deploy version + changelog system (committed, pushed: `6882aecf`,
   since patched by another session at `2c708ea9`, extended further at
   `391fcdf1`/`8a3882f5`)

Built at the human's request: `.github/workflows/deploy.yml` now stamps a
UTC-timestamp `VERSION` and prepends a `DEPLOY_CHANGELOG.md` entry (commit
subjects via `git log`, deliberately never via `${{ }}` template expansion
of commit-message text — see System-Level #3 for how that caution itself
caused a bug) on every deploy that ships files, commits both back to
`master` with `[skip ci]`, and ships them in the same FTP batch as the code
they describe. `changelog.php` renders it; `hub.php`'s footer links to it.
**This is now confirmed live and working**: `origin/master` shows
`d79020d8 Deploy v2026.08.14.1612 [skip ci]`, an actual auto-generated
commit from the workflow running for real. Not yet documented anywhere
(not in `CLAUDE.md`, not in `docs/`) — flagged to the human, not yet acted
on by me before the session moved to the next item.

### 3. `password_resets` schema bug — root-caused and fixed, **NOT YET
   COMMITTED**

Human reported "forgot password doesn't appear to be sending emails, but
the email test form is." Root cause, verified rather than inferred:
`ddl/140/001_password_resets.sql` created the column as `tuner_id`
(apparently a v1-naming habit — `tuner.tunerid` is the legacy staff-ID
table), but both consumers (`forgot_password.php`'s `INSERT`,
`password_reset.php`'s `SELECT ... JOIN users`) were written expecting
`user_id`, and always have been — the value inserted has always been
`users.id` (the v2 identity table), never `tuner.tunerid`. Confirmed those
two ID spaces genuinely diverge (not a same-value rename): of 6 sampled
`intypiano_demo` accounts, 3 have `users.id ≠ tuner.tunerid`, and
`ddl/147`'s `global_system_account` (seeded directly into `users`) has no
`tuner` row at all. Every `prepare()` against the nonexistent `user_id`
column throws under mysqli's PHP-8.4-default exception mode; both files
catch it silently and show the same neutral "a link is on its way" /
"this link does not work" text a real failure would show, so the bug is
invisible from the outside — exactly matching the reported symptom, while
`system_email_test.php` (the "email test form") works because it bypasses
`password_resets` entirely, sending via raw `mail()` with no DB table
involved.

Fixed with `ddl/149/001_rename_tuner_id_to_user_id.sql` (a `CHANGE COLUMN`,
zero application-code changes needed — `forgot_password.php` and
`password_reset.php` were already correct) and `ddl/149/002_verify.php`.
Applied for real via `php scripts/migrate.php --db=intypiano_demo --run`
(not just written and assumed correct). `PasswordResetTest.php` also needed
fixing — it had been asserting against the *wrong* ID space itself
(`tuner.tunerid`, `tuner_id`), which is presumably why this defect shipped
in the first place without a test catching it, plus a second, unrelated
pre-existing bug (POSTing `username` to `login_form.php`, which reads
`$_POST['email']`). Fixed both. Suite result:
`PasswordResetTest` 3/8 → 8/8 passing; full suite 68 → 63 failures (exactly
the 5 resolved, zero new regressions — confirmed by exact count, not
inspection).

**What's still open, in order of urgency:**

- **Nothing has been committed for item 3.** `ddl/149/` and the
  `PasswordResetTest.php` fix exist only in the local working tree of this
  session's `intypiano` checkout. The human ended the session (asked me to
  exit per this project's rules) before I was asked to commit. Password
  reset is still broken on every deployed tenant, including production,
  until someone (a future session, or the human directly) commits this,
  pushes it, and runs `php scripts/migrate.php --db=<tenant> --run` (or
  `admin/migrate.php`) against every tenant that has applied `ddl/140` —
  this migration was only ever run against `intypiano_demo` in this
  session.
- **A second, real, related bug flagged but not fixed:** `forgot_password.php`'s
  form label reads "Username or email," but the lookup only matches
  `users.email`. A user typing their username gets the identical silent
  no-op as an unknown account. I raised this with the human and they moved
  the conversation to ending the session before answering whether to fix
  it.
- `CLAUDE.md`'s "259 tests, 0 failures" baseline is stale (330 tests exist
  on disk; even after this session's fix, 63 fail on a clean run) — this
  matches what `FEEDBACK_WorkerLoginFix1_claude-sonnet-5_20260813.md`
  already flagged the day before. Two independent sessions hitting the same
  stale-baseline confusion a day apart is a decent signal this is worth a
  project-owner decision rather than a third session re-discovering it.

**Recommended next step for whoever picks this up:** review and commit the
uncommitted `ddl/149/` + `PasswordResetTest.php` changes in the primary
`intypiano` clone (or re-derive them — they're small and this document
describes them in full), push, then run the migration against every
non-demo tenant database before considering password reset actually fixed
anywhere real users can reach it.
