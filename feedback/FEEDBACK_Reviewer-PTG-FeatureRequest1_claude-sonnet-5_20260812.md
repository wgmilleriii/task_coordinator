---
title: "T-PTG-008 Peer Review: Feature-Request Triage Lane"
task: T-PTG-008
repo: newmexicoptg.org
reviewer: Reviewer-PTG-FeatureRequest1
model: claude-sonnet-5
date: 2026-08-12
verdict: PASS_WITH_CORRECTIONS
---

## System-Level Feedback (task_coordinator itself)

- **`fleet verify` worktree gap confirmed a third time.** This is the same defect the
  Worker flagged (and T-INTY-018 flagged before that): `fleet verify` runs
  `verification_command` against the shared main checkout at the audited
  `base_sha`, not the agent's isolated worktree, so it silently "passes" without
  ever touching the diff under review. I did not rely on it — I built my own
  isolated worktree (`git worktree add ../newmexicoptg.org-t008-review <head_sha>`)
  and ran every verification step there myself. Recommend `fleet verify` grow a
  `--worktree-path` flag or infer the path from the CLAIMED task's known
  `../<repo>-t<NNN>` convention. Three independent sessions hitting the same gap is
  enough signal to fix the tool rather than keep working around it by hand.
- **`requires_doc_update` is not a gate, it's a timer.** I initially expected this
  field to block a PEER_REVIEW→HUMAN_REVIEW transition when unmet. Reading
  `bin/fleet.py` directly, it only feeds the Janitor Protocol's 24-hour sweep
  trigger, checked at `onboard` time against tasks already `DONE`. That's a
  reasonable design but worth documenting explicitly in the README's task
  lifecycle section — a reviewer (or PM) skimming the field name alone would
  assume it blocks, and could waste time treating a non-blocking gap as a FAIL
  condition.
- `start-review` / `record-review` / the review schema worked exactly as
  documented — no friction there.

## Repository-Level Feedback (newmexicoptg.org / T-PTG-008)

**What I verified, independently, in a clean worktree with my own fresh DB (not
the Worker's):**

- Read the full diff (4 files, 694 insertions, 0 deletions: `api/ask.php`,
  new `lib/FeatureRequestService.php`, `lib/OpenAIClient.php::converse()`,
  `migrations/010_feature_request_conversations.sql`). The router sits after CSRF
  validation and before tier/preset resolution in `api/ask.php`, exactly as
  scoped — a tagged message never reaches `JournalAnswerService` at all.
- `FeatureRequestService::isTagged()` is `/^\/feature[- ]request(?=[\s]|$)/i` on
  `ltrim($message)` — first-token-only, case-insensitive. `converse()` builds a
  bare `{model, messages}` payload to `/chat/completions`; no `tools`, no
  `vector_store_id`, no `/assistants` or `/threads` call anywhere in the new code.
- Applied migration 010 to a brand-new DB myself via `cli/migrate.php` — all 11
  migrations (001–010) applied cleanly, no collisions, `tier` (008) correctly
  left untouched/unconflated.
- Ran all three suites myself against my own migrated DB: `AskEndpointTest.php`
  3/3, `UsagePolicyTest.php` 5/5, `JournalAnswerServiceTest.php` all ~24
  sub-assertions — all exited 0, matching the Worker's claim exactly.
- Stood up a real `php -S` server (`OPENAI_MOCK_MODE=true`), logged in as a real
  member-role user via `login.php`, and drove the whole flow over real HTTP with
  curl — not asserted from code:
  - Untagged question → real `citations[]` + `is_grounded:true`, unaffected.
  - Tagged 4-turn triage → closes on full who/how_often/what coverage; DB rows
    (`conversations.conversation_type`, `feature_request_details`, `messages`
    with `citations_json IS NULL`, `usage_events.event_type='feature_request'`,
    `debug_logs.is_grounded=0`) all matched the claim exactly.
  - `/Feature-Request` (hyphen + mixed case) routed correctly; "...or is that a
    feature request gap?" (mid-sentence, not first token) correctly stayed in
    the RAG lane with real citations — no false positive.
  - Explicit early close-out ("that is everything, thanks") with zero dimensions
    answered closed immediately, `closed_reason='user_closed'`, all
    `*_covered=0` — reproduced exactly as claimed.
  - Quota split verified against live rows I generated: `getMonthlyUserQuestionCount()`
    excluded 7 `feature_request` rows, counted only the 1 `query` row;
    `getMonthlyOrgSpend()` summed all rows including the feature-request cost.
    `UsagePolicy.php` untouched, its own test suite still green.

**No correctness bugs found.** This is a genuinely thorough, independently
reproducible implementation — every DoD bullet checked against my own evidence,
not the handoff's.

**One MAJOR finding, non-blocking:** no `journalgpt/docs/` file, `changelog.json`
entry, or `version.json` bump was added despite `requires_doc_update: true` and
this being a clear new architectural lane (new table, new service, new router
branch). This repo has a strong existing pattern of a changelog entry per
feature-sized change (2.1.0 through 2.3.0). It doesn't block this review per the
Janitor Protocol's actual mechanics, but the human closing this task should make
a conscious call — either add a doc/changelog entry before `fleet close`, or
explicitly accept the Janitor Protocol will catch it later.

**Next steps for the human:** the extraction script (feature_request_details →
task_coordinator YAML) is correctly out of scope for this task and was not
built — that's a natural follow-on task, and the storage schema here (structured
per-dimension TEXT columns + `status`/`closed_reason`) is sufficient for it.
