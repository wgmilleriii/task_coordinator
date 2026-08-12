## System-Level Feedback

- **`fleet verify` does not run in the worker's worktree.** It re-ran `verification_command`
  against the shared `/Users/willismiller/Documents/GitHub/intypiano` checkout, not
  `../intypiano-t018`, and collided with a leftover `php -S localhost:2027` process from
  my own testing, producing a bogus 330/1/74 result instead of the true 330/1/68. This is
  the same gap T-INTY-021's Worker flagged. I hand-built a schema-valid handoff with
  real captured evidence instead, per the task instructions and the T-INTY-021 precedent.
  Recommend either parameterizing `fleet verify` with a repo path, or changing
  `verification_command` conventions to grep for "no NEW failures beyond baseline" so a
  tolerated non-zero phpunit exit doesn't auto-fail the harness.
- Installing `jsonschema` for local schema validation hit PEP 668 (externally-managed
  Python) and needed `--break-system-packages` I didn't want to force; I validated the
  handoff by hand (required/extra keys, regex, non-empty string) instead of via
  `jsonschema.validate`. A vendored/no-install validator (or a `fleet lint-handoff`
  subcommand) would remove this friction for every worker that hits it.
- The onboarding instructions reference `./bin/fleet onboard <repo_name>` and a
  Janitor Protocol for `.fleet_context.md` "DOCUMENTATION UPDATE REQUIRED" warnings; I
  did not find or run onboarding since the task prompt handed me a fully-formed
  worktree/claim flow directly. Worth confirming whether Workers are expected to run
  onboarding every session or only once per repo.

## Repository-Level Feedback

Did the work in an isolated worktree (`../intypiano-t018`) branched from the `test`
branch tip (`8b4bcec5`, the T-INTY-021 DB-fallback fix), not from `master`'s
`3cf4775d` — `master` alone still 500s on `admin/v2/*` locally, and the task's own
framing ("your local dev server should work cleanly now") only holds true off `test`.

The most consequential finding was that the PM audit's factual premise was wrong:
the scope note claimed "all 126 inventory.piano_code values already look like Gazelle
Piano ID strings," citing 3 examples. Querying the full table in `intypiano_demo`
found only 42/126 are actually all-digit; the other 84 (`ALUMNI`, `YAMAHA`, `B22644`,
`PJH567`, `WURLIT`, `HODGIN`, `UNMHOS`, ...) are hand-assigned legacy codes that were
never issued by Gazelle. The 3 cited examples were real but not representative — a
small sample masked the true distribution. Had I trusted the audit note and done a
blanket `UPDATE gazelle_id = piano_code`, I'd have fabricated 84 Gazelle identifiers
that don't exist. This is exactly the "prefer running over reading" rule in
`CLAUDE.md` earning its keep — I queried the live demo DB before writing DDL rather
than trusting the audit's prose, and the backfill (`ddl/146/003` and `004`) filters
on `piano_code REGEXP '^[0-9]+$'`, not "every row." I also documented this correction
in `docs/experts/schema-catalog.md` under a new Landmine so the next agent doesn't
repeat the sampling mistake.

Also confirmed (still true): `inventory` and v2 `pianos` have no ongoing sync beyond
the one-time `ddl/132/004_map_pianos.sql`. Since `import_sfusd.php` writes only to
`inventory`, I added `gazelle_id` to both tables — `pianos`-only would have left the
import script's DoD requirement unsatisfiable.

Product decision, stated per the task's explicit request: `piano_code` keeps
mirroring the raw Gazelle Piano ID on new SFUSD imports, unchanged from today, for
continuity with the already-deployed QR label scheme; `gazelle_id` is populated
alongside it with the same value so `piano_code` can eventually be treated as an
opaque QR key independent of Gazelle identity, without touching existing prints.

Proof `piano_code` is untouched: captured `SELECT id, piano_code FROM pianos` and the
`inventory` equivalent before and after `ddl/146`, `diff`'d them — zero lines of
output, both tables, then re-verified a third time after the phpunit run. Spot-checked
3 real codes (one Gazelle-numeric, two hand-assigned) through a running server against
`piano/index.php` — all HTTP 200.

phpunit: 330 tests / 1 error / 68 failures before and after, and I went one step
further than a count comparison — extracted every failing test's name from this run
and from the T-INTY-021 handoff's evidence, sorted and diffed them: zero differences.
Same exact tests, nothing shifted.

**Recommended next steps:** file a follow-up task for the admin/v2 pages missing
`<meta name="viewport">` (accounts for most of the 68 pre-existing failures) — it's
a one-line fix repeated across ~15 pages and would meaningfully shrink the noisy
baseline everyone has to compare against. Also worth a small follow-up task deciding
whether v2 `pianos` should eventually get an ongoing sync from `inventory` (or from
future imports directly), since today anything imported via `import_sfusd.php`-style
scripts is invisible to the v2 booking/admin surface until someone runs a manual remap.
