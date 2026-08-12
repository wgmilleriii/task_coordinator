# Feedback: PM-Gazelle1 (claude-sonnet-5, 2026-08-12)

Role: PM. Audited Scout-written tasks T-INTY-018, T-INTY-019, T-INTY-020 (repo: intypiano)
against the user's actual intent (dedicated `gazelle_id` column, decoupled from
`piano_code`'s QR duty). Audited T-INTY-018 and T-INTY-020 against repo-sha
`3cf4775d3561b3746c6e55586921beb4492ec57d`. Left T-INTY-019 OPEN.

## System-Level Feedback

1. **`fleet claim` genuinely enforces dependency status == DONE**, not just documentation
   convention — confirmed by reading `bin/fleet.py` lines ~296-303. This meant I could
   safely audit T-INTY-020 (depends on T-INTY-018, not yet DONE) without creating any
   risk of a Worker claiming it prematurely. Worth stating this explicitly in the README's
   "Auditing a Task" section — it currently doesn't say whether `dependencies:` is
   mechanically enforced or just informational, and a PM has to go read the CLI source
   to find out.
2. **YAML linting on `fleet audit` silently reflows prose.** My scope edits used plain
   (unquoted) block-scalar list items; any `word: word` sequence inside prose (e.g.
   `mysqli_sql_exception: Unknown database`) breaks YAML parsing with a cryptic
   "mapping values are not allowed here" error at an unrelated line/column. `fleet lint`
   catches it, but the error message doesn't point at the actual offending colon. Consider
   documenting "avoid `: ` inside scope/DoD prose, use ` - ` instead" as a house style rule
   (the Scout's own prose already avoids it everywhere, suggesting this bit someone before).
3. **`fleet lint` aborts entirely on the first malformed file** rather than reporting all
   errors across the store — I had to fix my own two files' YAML before I could see whether
   anything else was broken, and even after fixing mine, one other file (`T-INTY-017.yaml`,
   untracked, not written by me) still fails lint on an unrelated schema issue (`'dod' was
   unexpected`). Left it alone per the boundary convention, but flagging it in case no one
   else has noticed the board has a latent lint failure.

## Repository-Level Feedback (intypiano)

**T-INTY-018 (Add gazelle_id column) — AUDITED.** Independently re-verified every load-bearing
claim in the Scout's scope before unlocking it: `piano_code` really is the QR lookup key
(`qr_report_generator.php`, `piano/index.php`, `PIANO_QR_SETUP.md` all confirmed), v1
`inventory.piano_code` is `varchar(6)` with no unique constraint (MyISAM, confirmed via
`ddl/ddl73.sql`), v2 `pianos.piano_code` is `varchar(24)` with `UNIQUE KEY uniq_piano_code`
(`ddl/132/001_v2_schema.sql`), and `ddl/145` is genuinely the latest DDL slot (`002_verify.php`
pattern confirmed) — so `ddl/146` is the correct next slot. `import_sfusd.php` lines 31/41-44
confirmed exactly as described. The investigation-first framing (UNIQUE-vs-KEY, whether v1
`inventory` needs the column too, whether all `piano_code` values are actually Gazelle IDs) is
appropriately hedged rather than presenting an unverified answer as fact, so I audited as-is
rather than trying to pre-resolve those questions myself — they're genuinely open and a Worker
should investigate them with real data, not have a PM guess from a scout pass.

One real bug I fixed before auditing: the Scout's `verification_command` called
`php scripts/migrate.php --status` with no `--db=` flag, which the script requires and
would fail immediately (`Pick one of --status, --dry-run, --run` usage error, or a missing-db
fatal). Fixed to `--db=intypiano_demo`.

**The much bigger finding: the documented 259-test/0-failure baseline in CLAUDE.md does not
currently exist.** I ran a clean `php -S localhost:2027 -t .` + `./vendor/bin/phpunit` against
HEAD three separate ways (after killing a stale duplicate server process, via fresh curl to
`admin/v2/piano.php`, and via a standalone PHP CLI repro) and got the same result every time:
**330 tests, 18 errors, 114 failures, 6 skipped.** Root cause: every `admin/v2/*` page 500s
locally with `Uncaught mysqli_sql_exception: Unknown database 'caut_sfusd'` out of
`classes/core/DatabaseManager.php:307`. Traced it to the brand-new multi-tenant `config.php`/
`DatabaseManager` dispatch added 2026-08-11 (commits `40d00b89`..`4751c925`, part of the
"Valuations & Documentation system overhaul") — it introduces a `$this->app->app=="cauttools"`
branch keyed on `SERVER_PORT` that resolves to `caut_sfusd` on port 2027 unless overridden by
`config.php`'s `$db_configs['sfusd']`, and something in that path is not applying the override
that CLI-only testing of `config.php` shows works fine in isolation. This is **not** caused by
Gazelle work and predates this session; it's a live regression sitting on `master` right now,
six days after CLAUDE.md's baseline was last updated and three commits ahead of it.

I did not try to fix it (out of scope for a PM, and not part of either task), but I rewrote
T-INTY-018's DoD to hold the Worker to "no new failures beyond the captured 330/18/114/6
shape" instead of the impossible "259/0" bar, with the full repro noted inline so nobody
re-litigates it as their own bug. **I recommend filing a dedicated bug task for this
regression** — it blocks not just T-INTY-019 but presumably every other task in this repo
whose DoD references the phpunit baseline or a running admin/v2 page.

**T-INTY-019 (Open in Gazelle button) — left OPEN, not audited.** Its DoD requires manual
verification of `admin/v2/piano.php` in a running server with before/after screenshot
evidence — currently impossible, since that exact page is one of the ones 500ing (see above).
Since `fleet claim` mechanically blocks it until T-INTY-018 reaches DONE anyway, there's no
urgency; I left a PM note in the YAML explaining the blocker and recommending the DatabaseManager
regression get its own task and get fixed first, rather than silently unlocking a task whose
DoD can't currently be satisfied through no fault of the Worker.

**T-INTY-020 (Design nightly Gazelle sync) — AUDITED, with a scope correction.** The Scout's
central premise — "Gazelle API access was never confirmed to exist" — is factually wrong as of
this repo-sha. `classes/integration/GazelleAPI.php` (added in the very commit the Scout cites,
`1ea83713`) is a working private GraphQL client (`https://gazelleapp.io/graphql/private`) with
a confirmed read query (`allPianos`) and a confirmed write mutation (`updatePiano`), already
wired into production via `admin/v2/normalization.php`'s "Mass Edit" tool (I loaded both files
and traced the call chain end to end). Auditing the task as originally scoped would have sent
a Worker down a "does the API exist" investigation that's already answered in the repo. I
rewrote the scope to point directly at both files and reframed the actual open questions: (1)
today's only working credential flow is an admin pasting an API key into a form per-request —
there's no stored service-account credential for an unattended nightly cron, and the design doc
needs to say where one would live; (2) the API is not read-only (it has a live mutation), so the
doc must explicitly commit to a read-only sync rather than leaving that implicit; (3) what fields
`allPianos` (or a sibling query) actually returns beyond make/model is still unconfirmed and
should be checked against the GraphQL schema rather than assumed.

**Recommended next steps for the human:** (1) file a bug task for the `DatabaseManager`/
`config.php` regression before unlocking T-INTY-019; (2) once T-INTY-018 lands, re-run
`./vendor/bin/phpunit` to get a fresh baseline for CLAUDE.md — the current doc is stale; (3)
when T-INTY-020's Worker starts, they should introspect the actual Gazelle GraphQL schema
(via the API itself, with a real key) rather than assuming `allPianos`'s fields from the one
query already in the codebase.
