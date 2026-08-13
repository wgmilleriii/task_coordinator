# Feedback: T-PTG-010 Peer Review (Reviewer-ContributorIndex1)

## System-Level Feedback

- `fleet verify`'s recurring gap (running verification_command against the shared main
  checkout instead of the Worker's isolated worktree) is now a 3rd occurrence
  (T-INTY-018, T-PTG-008, T-PTG-010). Worth fixing: accept a `--worktree-path` override
  or infer it from the `CLAIM` event's known branch-naming convention
  (`test-<task_id>`). Reviewers currently have to redo the worktree-add step from
  scratch each time, which is fine but is pure duplicated setup cost across three tasks
  now.
- `start-review`/`record-review` worked cleanly, and the review schema (findings list +
  verdict) was easy to fill out with specific, falsifiable evidence per item rather than
  a vague pass/fail. No complaints about the review mechanics themselves.
- The instruction to independently reproduce claims (rather than trust the handoff) was
  the right call here and caught nothing wrong — but it's worth noting the exercise is
  only as cheap as it was because the Worker's handoff was unusually precise (exact SQL,
  exact file:line references, exact error strings). A vaguer handoff would have made this
  review much more expensive to do properly.

## Repository-Level Feedback

**Verdict: PASS.** Task moved to `HUMAN_REVIEW` per `human_review_required: true`; a
human must still run `./bin/fleet close T-PTG-010 --human <name>`.

Reviewed in an isolated worktree (`../newmexicoptg.org-t010-review`, separate from both
the shared checkout and the Worker's own `../newmexicoptg.org-t010`) at head_sha
`41734cd`. All 6 claimed commits present. Independently re-ran every test file rather
than trusting the handoff's pasted output — all green, zero regressions:
`ContributorNormalizerTest.php` 14/14, `CorpusIndexerTest.php` 8/8,
`ContributorStatsServiceTest.php` 8/8, `AskEndpointTest.php` 3/3, `UsagePolicyTest.php`
5/5, `JournalAnswerServiceTest.php` full suite, `FeatureRequestServiceTest.php` 6/6.

Each of the 5 claimed deviations/fixes was independently re-verified, not taken on
trust:

1. **Driver-aware `resolveAndLink()`** — read the code directly; the MySQL/SQLite branch
   only changes the ignore-duplicate-link SQL dialect (`INSERT IGNORE` vs `INSERT OR
   IGNORE`), while the exact-match-or-pending logic is identical on both drivers, so the
   never-auto-merge guarantee holds on both.
2. **`CorpusIndexerTest.php` was genuinely unrunnable before** — checked out parent
   commit `7a7c621` and ran the old test file directly: it produced zero output and
   exited 0, confirming it silently did nothing. The Worker's reflection-based CLI
   runner is legitimate and the new contributor-linking test passes for real.
3. **`recordDebugLog()` double-placeholder bug** — wrote a standalone script against
   `journal_ai_test` with this repo's actual `PDO::ATTR_EMULATE_PREPARES=false` setting,
   reproduced `SQLSTATE[HY093]` from a duplicate named placeholder. The fix (distinct
   `:raw_answer`/`:clean_answer`) is real and necessary — without it, every
   `debug_logs` row for this lane would have silently failed to write.
4. **`manual_conversation_matrix.php` router mirror** — diffed both files: the harness
   change only affects the harness's own dispatch, and `api/ask.php`'s diff is a clean,
   self-contained insertion with the pre-existing RAG code below it confirmed
   byte-identical to the parent commit.
5. **Turn 2/3 pre-existing 404** — independently re-ran the full manual matrix scenario
   myself: turn 1 landed a fresh `debug_logs` row (`preset='contributor_index'`, real
   templated ranking, not a hedge); turn 2 hit the same `vs_default_mock_store` 404.
   Confirmed via `git diff --stat` that `JournalAnswerService.php`/`OpenAIClient.php`
   aren't touched by this task at all, and confirmed `JournalAnswerServiceTest.php`
   always constructs its `OpenAIClient` in mock mode — genuinely unaffected by this
   change, not a disguised regression.

Load-bearing constraints (no vector-store call, no LLM-generated numbers, fixed-phrase
router, pending-never-auto-merge, router-miss-falls-through) were all re-checked by
reading the diff and grepping the new files directly, not inferred from tests passing
alone.

**No issues found.** This was the most architecturally novel task in the session and
held up under adversarial re-verification of every specific claim. Next step is human
sign-off via `fleet close`.
