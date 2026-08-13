# FEEDBACK: PM-ContributorIndex1 (claude-sonnet-5, 2026-08-12)

## System-Level Feedback

- The Scout→PM handoff pattern for T-PTG-010 worked well: the Scout wrote the task to
  point at pre-existing, committed design/plan docs instead of duplicating them into
  the YAML, and explicitly flagged the one real open question (design doc prose vs.
  plan's concrete mechanism for the `debug_logs` marker) rather than silently picking
  a side. That made the PM audit fast and mechanical: verify one specific claim against
  two files, not re-derive the whole design.
- `./bin/fleet lint` currently fails repo-wide on a pre-existing, unrelated defect
  (`T-INTY-017.yaml` has an `Additional properties are not allowed ('dod' was
  unexpected)` schema error — looks like a typo'd `dod` key instead of
  `definition_of_done`, from a different repo lane, untouched by this session). This
  makes `fleet lint`'s exit code useless as a gate for an individual PM's own change
  unless they diff which file failed. Worth a `--task <id>` scoping flag on `lint` so
  a PM can confirm their own file is clean without a repo-wide failure masking it.
- No functional complaints about `fleet audit` itself — straightforward, did what the
  README described.

## Repository-Level Feedback (newmexicoptg.org)

Audited T-PTG-010 (contributor index / authorship count-ranking lane) from OPEN to
AUDITED against SHA `7a7c6212a575bb2743b3b26c32283b937f1e286f`. Did not write
application code (PM role only).

**The debug_logs marker question:** confirmed by direct read that
`journalgpt/migrations/009_debug_logs.sql` has no `retrieval_mode` column — only
`preset VARCHAR(20) NULL` — and that `journalgpt/lib/FeatureRequestService.php`'s
`recordDebugLog()` already writes `preset = 'feature_request'` as a literal in its
INSERT, which is exactly the pattern the plan's `ContributorStatsService` mirrors with
`preset = 'contributor_index'`. The design doc's `retrieval_mode` wording is simply
stale prose from before the plan settled on reusing `preset` — not a live second
option. Edited the task YAML's scope bullet so this reads as a decided fact with the
verification trail attached, not an open question a Worker might re-litigate.

**Real author-data spot-check (the part I was most worried would break the plan):**
queried the local `newmexicoptg_journal_ai` DB directly (92 articles). 90 of 92 share
one generic institutional byline, `"Piano Technicians Guild Authors"` (no comma,
ampersand, semicolon, or "and"). The only two comma-containing author values are
single-person `"Name, RPT"` rows — zero genuine comma-separated co-author bylines
exist anywhere in the real corpus. The plan's `ContributorNormalizer::splitAuthors()`
design (comma is never treated as a person-separator, only ampersand/semicolon/"and"
are) holds cleanly against real data. No correction needed here.

**Other spot-checks:** `CorpusIndexer::indexArticle()`'s hook point
(`$articleDbId = $this->upsertArticleInDb(...)`, line 114) is real and matches the
plan's claimed insertion point exactly; the class's PDO property is `$this->pdo` as
the plan assumed (both confirmed by reading the file, not inferred). Compared
scope/DoD shape against `T-PTG-008` (DONE, same repo, same shape — new migration + new
service + router wiring + new test file) and judged this a consistent single-task
size, not a split candidate.

**No plan corrections were needed** — the implementation plan held up against every
real-code and real-data check I ran. Left `human_review_required: true` as the Scout
set it (new architectural surface: a new entity index and a new query lane in
`api/ask.php`) — this audit unlocks the task for a Worker but does not waive final
human sign-off.

**Recommended next step:** a Worker should claim T-PTG-010 and follow
`docs/superpowers/plans/2026-08-12-contributor-index.md` task-by-task
(`superpowers:subagent-driven-development` or `superpowers:executing-plans`, per the
plan's own header). No blockers identified.
