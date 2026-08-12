# Feedback: PM-PTG-FeatureRequest1 — 2026-08-12

## Task: T-PTG-008 (newmexicoptg.org) — audited OPEN → AUDITED

### System-Level Feedback

- **Schema gap:** I initially added a top-level `pm_decisions` key to the task
  YAML to hold the four judgment-call writeups. `./bin/fleet lint` correctly
  rejected it — `schemas/task.schema.json` has no such property, only `scope`,
  `definition_of_done`, `events`, etc. Folded the content into additional
  `scope` list items instead, which is schema-legal and reads fine in
  `TASKS.md`. Suggestion: either add an explicit `pm_decisions` (or
  `pm_notes`) array to the schema for this exact purpose — "Scout flagged
  open questions, PM must resolve them explicitly" is a recurring pattern —
  or document in the README that PM judgment calls belong in `scope`, not a
  new key, so future PMs don't hit the same lint failure.
- The audit/render/lint flow itself worked cleanly once the schema issue was
  fixed. No other coordinator defects encountered this session.

### Repository-Level Feedback

**Verified independently, not taken on trust from the Scout:**
- `.github/workflows/deploy.yml` (read directly): both `test` and `main` FTP
  jobs exclude `**/tasks`, `**/.github`, `**/docs`, `**/*.md`. Scout's central
  claim — production PHP has no path to `task_coordinator` — is correct.
- `journalgpt/migrations/001` through `009` (read directly): migration 008
  adds a `tier` column to `messages`/`usage_events` (model tier:
  quick/medium/deep) and `is_public`/`share_slug` to `conversations` — **not**
  a conversation type/category concept. This feature needs a genuinely new
  `conversations.conversation_type` column via a new `010_*.sql` migration,
  not a reuse of `tier`.
- `journalgpt/lib/UsagePolicy.php` (read directly): `getMonthlyUserQuestionCount()`
  filters `usage_events` on `event_type='query'`; `getMonthlyOrgSpend()` sums
  `estimated_cost` with no `event_type` filter. This makes the Scout's
  suggested quota default (exempt from personal quota, still counts toward
  org budget) implementable with zero changes to `UsagePolicy.php` — just use
  a distinct `event_type` value for feature-request turns. Confirmed this
  interpretation is correct by reading the actual SQL, not by inference.
- **Test harness genuinely works.** Ran
  `DB_HOST=127.0.0.1 DB_NAME=journal_ai_test DB_USER=root DB_PASS=root php journalgpt/tests/AskEndpointTest.php`
  and `.../UsagePolicyTest.php` against a real local MySQL 9.3.0 instance —
  both passed fully (3/3, 5/5), including DB-backed assertions, not just the
  DB-free anonymous/CSRF checks. This means the DoD's "prove multi-turn
  behavior and no-regression against a running server" requirement is
  actually achievable today, not aspirational — a meaningful finding since a
  DoD that can't be executed against is not safe to unlock.

**Four judgment calls made explicit in the YAML (`scope`, decisions 1-4):**
1. Tag must be the first token of the trimmed message, case-insensitive — not
   detected anywhere in the text, to avoid misrouting ambiguous technical
   questions away from grounded answers.
2. "Enough detail" = structured, machine-checkable coverage of three
   dimensions (who / how-often / what-it-would-look-like) extracted per-turn
   into fields, OR explicit user close-out — not a model self-judgment. This
   is also load-bearing for the DoD's "sufficient for later extraction into a
   task YAML" bullet: free text alone would not satisfy it.
3. Confirmed the Scout's suggested default (exempt from
   `monthly_question_quota`, still counts against `org_monthly_budget_usd`)
   and specified the exact mechanism (distinct `usage_events.event_type`).
4. Confirmed migration 008 does not already introduce a conversation-type
   concept; a new column/migration is required, must not overload `tier`.

**Concern / next steps for the human:** This is a genuinely new architectural
lane (parallel non-RAG conversational flow, new storage, new quota carve-out)
touching a live production assistant. `human_review_required` and
`requires_doc_update` were already correctly set true by the Scout and left
as-is. I did not weaken the DoD's no-regression requirement — it's now
concretely testable per the harness verification above, so I judged the scope
safe to unlock rather than holding it OPEN. Recommend the Worker run the full
existing suite (not just `AskEndpointTest`/`UsagePolicyTest`) before and after
their change to catch any RAG-pipeline regression the DoD requires proving.

Repo SHA audited against: `2915a622d26b0dfa151f5da6070cad4c9688d3ae`.
