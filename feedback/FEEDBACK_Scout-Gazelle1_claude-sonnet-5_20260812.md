# Scout Session Feedback — Scout-Gazelle1 — claude-sonnet-5 — 2026-08-12

Repo: intypiano. Mission: scope Gazelle CRM integration follow-on tasks after
the user rejected reusing `inventory.piano_code` for a Gazelle piano ID and
asked for a dedicated `gazellecode` column.

## System-Level Feedback

- **YAML plain-scalar colon-space is a real trap for scope/DOD prose.** Writing
  natural-language scope items with `: ` (e.g. citing a doc section like
  `'Test 2: View Piano Landing Page'` or a commit subject like
  `'feat(integrations): build X'`) breaks `yaml.safe_load` with "mapping values
  are not allowed here," and `./bin/fleet lint` reports it as `CRITICAL: Store
  contains malformed YAML. Aborting to prevent data corruption` — an alarming
  message for what's actually a routine typo. Worth a README note for Scouts:
  avoid `: ` inside scope/DOD strings, use ` - ` instead, or the linter should
  give a gentler error for this specific case since it's going to recur every
  time an agent quotes a colon-containing title in prose.
- `T-INTY-017.yaml` (PEER_REVIEW status, not touched by me) fails
  `./bin/fleet lint` right now — additionalProperties `dod` unexpected, should
  be `definition_of_done`, and its `scope` is a string, not the array the
  schema requires. I did not fix it (out of scope for a Scout, and it's mid
  peer-review by another agent), but whoever picks it up next will hit this.

## Repository-Level Feedback (intypiano)

Created three OPEN tasks: `T-INTY-018` (P1, add `gazelle_id` to `pianos`/
`inventory`, decoupled from `piano_code`), `T-INTY-019` (P2, "Open in Gazelle"
button on the Piano Dossier page, depends on 018), `T-INTY-020` (P3, design-only
task for a nightly Gazelle sync, depends on 018).

Key things my own exploration changed versus the brief I was handed:

1. **The conflation isn't hypothetical, it's live.** Every one of the 126 rows
   in `intypiano_demo.inventory.piano_code` today already holds what is
   unmistakably a raw Gazelle Piano ID (`110641`, `110801`, `152964`, ...),
   confirmed against `import_sfusd.php`'s CSV import path. `pianos.piano_code`
   (v2) carries the same values via the one-time `ddl/132/004_map_pianos.sql`
   migration.
2. **`piano_code` is physically printed on deployed QR labels** (`piano/{code}`
   URLs baked into printed codes per `PIANO_QR_SETUP.md` and
   `qr_report_generator.php`). This means T-INTY-018 cannot rename or
   regenerate `piano_code` — it must be purely additive: add `gazelle_id`,
   backfill it by *copying* the current `piano_code` value, and leave existing
   `piano_code` untouched so no physical label goes dead. I wrote this as an
   explicit CRITICAL bullet and a DOD line requiring a before/after diff
   proving zero `piano_code` rows changed.
3. **No confirmed sync between v1 `inventory` and v2 `pianos`.** I found only
   the one-time migration script, no recurring job. T-INTY-018's scope now
   asks the PM/worker to confirm whether new inventory rows (future imports)
   ever reach v2 `pianos` at all before deciding whether `gazelle_id` needs
   backfilling on one table or both — this could turn into its own bug ticket
   if the answer is "they don't."
4. Consciously deferred (per instructions, not forgotten): pushing intypiano
   invoices to Gazelle, and detecting/reconciling remote edits made in
   Gazelle. Both need a confirmed Gazelle API surface first; T-INTY-020 (design
   only) explicitly flags remote-edit conflict handling as unsolved rather than
   silently assuming it's out of scope forever.

Next step for a human/PM: confirm whether Gazelle actually exposes any
API/export beyond the flat CSV `import_sfusd.php` already consumes — that
answer gates both T-INTY-020's real content and any future invoice-push /
webhook work.
