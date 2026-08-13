# Feedback: Worker-ContributorIndex1 (T-PTG-010, 2026-08-12)

## System-Level Feedback (task_coordinator itself)

- **`fleet verify` still runs against the wrong checkout.** For a Worker operating
  in an isolated `git worktree add ../repo-tXXX`, `fleet verify` re-runs the
  verification_command against the *main* checkout (`../newmexicoptg.org`, on
  `main`, at the audited base_sha) instead of the worker's worktree. On this task
  it failed immediately with "Could not open input file" since none of the new
  files exist on main at all. This is the third handoff in a row to flag exactly
  this gap (T-INTY-018, T-PTG-008, now T-PTG-010) — it seems worth fixing at the
  tool level rather than every worker re-discovering and hand-documenting it.
  Suggestion unchanged from prior feedback: accept a `--worktree-path` override,
  or have `fleet claim` record the worker's intended worktree path in the task
  YAML so `verify` can find it automatically.
- **Handoff YAML round-trips through some formatter/linter on write** that
  reflows multi-line block strings into quoted flow style with `\n` escapes —
  harmless (content unchanged, confirmed by diff) but worth knowing so future
  workers don't panic when their handoff file looks different immediately after
  `fleet submit`.

## Repository-Level Feedback (newmexicoptg.org / JournalGPT)

Executed all 7 tasks from `docs/superpowers/plans/2026-08-12-contributor-index.md`
in an isolated worktree (`../newmexicoptg.org-t010`, branch `test-T-PTG-010`).
The plan was unusually complete — every file had working, pasteable code — but
three real bugs/gaps only surfaced by actually running things, not by reading:

1. **`ContributorNormalizer::resolveAndLink()`'s literal `INSERT IGNORE` breaks
   under SQLite.** `CorpusIndexerTest.php` runs `indexArticle()` (and therefore
   my new hook) against an in-memory `PDO('sqlite::memory:')`, not
   `journal_ai_test`. MySQL's `INSERT IGNORE` isn't valid SQLite syntax. Made
   `resolveAndLink()` driver-aware (checks `PDO::ATTR_DRIVER_NAME`, uses
   `INSERT OR IGNORE` + an inline `CREATE TABLE IF NOT EXISTS` for the SQLite
   branch). Worth flagging as a pattern for any future feature whose ingestion
   hook needs to run inside `CorpusIndexerTest.php`'s existing SQLite fixture.

2. **`CorpusIndexerTest.php` was silently unrunnable before this task.** It's a
   PHPUnit-style `TestCase` subclass (`public function testX(): void` methods),
   but no PHPUnit is installed anywhere in this environment (no `vendor/`, no
   `phpunit` binary, no `composer.json`) and — unlike every other standalone
   CLI-runnable test file in `journalgpt/tests/` (`AskEndpointTest.php`,
   `ContributorNormalizerTest.php`, etc., which all use a
   `ClassName::run()` + bottom-of-file self-invocation convention) — it had no
   invocation block at all. `php tests/CorpusIndexerTest.php` ran zero tests and
   exited 0, silently. It also never `require_once`'d `OpenAIClient.php` or
   `CorpusIndexer.php` themselves. This means the file has likely never
   actually executed in this local-dev environment since it was written (see
   `docs/superpowers/plans/2026-07-21-journal-ai-prototype.md` and
   `2026-07-23-...corpus-integrity.md`, both of which instruct running it the
   same broken way). Added a small reflection-based CLI runner mirroring this
   repo's own convention, plus the two missing `require_once` lines, so the
   file can actually run and prove something — this task's DoD required it to
   pass, which forced the fix. This is a pre-existing repo gap, not introduced
   by the contributor-index feature; worth a dedicated follow-up task to check
   whether any other test file in `journalgpt/tests/` has the same silent-no-op
   problem.

3. **`ContributorStatsService::recordDebugLog()`'s draft in the plan reused the
   `:answer` named PDO placeholder twice** in one INSERT. Under this repo's
   `PDO::ATTR_EMULATE_PREPARES => false` (`lib/Database.php`), that throws
   `SQLSTATE[HY093] Invalid parameter number` — silently swallowed by the
   surrounding `try/catch`, so the templated ranking answer was returned to the
   caller correctly but the `debug_logs` row (the entire proof mechanism this
   design doc depends on) never got written. Fixed by binding
   `:raw_answer`/`:clean_answer` as distinct params, matching
   `FeatureRequestService::recordDebugLog()`'s own working pattern for the same
   two columns. This would have been very easy to ship broken — the `ask()`
   response looked completely fine; only a direct `SELECT ... FROM debug_logs`
   revealed the row was missing.

4. **`tests/manual_conversation_matrix.php` — the exact harness this task's DoD
   names for the regression proof — calls `JournalAnswerService::ask()`
   directly and has never gone through `api/ask.php`'s router at all.** This
   isn't new to this task: T-PTG-008's `FeatureRequestService` tag routing has
   the identical gap (the harness would misroute a `/feature request`-tagged
   scenario the same way, if one existed). Without patching this harness to
   mirror `api/ask.php`'s router, the DoD's literal verification command
   (`manual_conversation_matrix.php ... frequent_contributors_aggregate.json
   scholarly quick`) could never have produced a `preset='contributor_index'`
   row, no matter how correct the `api/ask.php` wiring was — the harness simply
   never reaches it. Added the same `isCountRankingQuestion()` check to the
   harness. This is worth fixing centrally (a shared "route like api/ask.php
   would" helper) before a fourth parallel lane makes this harness diverge
   further from production behavior.

5. **The regression harness's RAG fallback is broken in this local environment
   independent of anything in this task**: `JournalAnswerService::
   getActiveVectorStoreId()` falls back to a hardcoded `'vs_default_mock_store'`
   that returns a live 404 from OpenAI (not a mocked failure — this harness
   makes real API calls). This blocked turns 2-3 of the regression scenario
   (which intentionally don't match the fixed contributor-index phrase list and
   correctly fall through to RAG) from completing. Turn 1's routing and
   `debug_logs` proof are unaffected and stand on their own, but a human
   verifying this task by literally re-running the full 3-turn scenario will
   hit the same fatal error and should not read it as a regression in this
   diff — `JournalAnswerServiceTest.php` (mocked) passes clean.

**Recommended next steps for a human:** (a) confirm whether
`vs_default_mock_store` should be replaced with a real configured vector store
ID for this local/test environment so `manual_conversation_matrix.php` can run
end-to-end without a live-API 404 on unrelated turns; (b) consider a follow-up
task auditing every file in `journalgpt/tests/` for the same "PHPUnit-shaped
but never actually invoked" problem found in `CorpusIndexerTest.php`; (c) this
task's `human_review_required: true` is warranted and was not waived — a new
entity index and a new parallel query lane in `api/ask.php`, same bar as
T-PTG-008/T-INTY-018.
