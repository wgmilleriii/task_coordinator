# 📋 Task Board

*(Auto-generated. Do not edit manually. Use `./bin/fleet` commands to transition tasks.)*

## 💸 Fleet Burn Rate (All Time)
- **Total Tokens Spent:** 0
- **Total Cost (USD):** $0.05

---

## 🕸️ Task Dependency Graph

```mermaid
graph TD
    classDef done fill:#d4edda,stroke:#28a745,color:#000;
    classDef blocked fill:#f8d7da,stroke:#dc3545,color:#000;
    classDef review fill:#fff3cd,stroke:#ffc107,color:#000;
    classDef active fill:#cce5ff,stroke:#007bff,color:#000;
    T-PTG-053["T-PTG-053<br/>Coverage Atlas Phase 1b: coverage radar dashboard + empty-wedge nudge"]:::review
    T-PTG-052 --> T-PTG-053
    T-PTG-069["T-PTG-069<br/>Profile page: link 'My Research' article citations to their source PDFs (HigherLogic issue_url)"]:::review
    T-PTG-065["T-PTG-065<br/>Webhook Sync for Localhost Conversations"]:::review
    T-PTG-064["T-PTG-064<br/>Feature: Pool Ball Triangle Layout"]:::review
    T-PTG-048["T-PTG-048<br/>Article/editorial completeness QC pass beyond page-coverage checking, ground-truthed against PTJ-2020-02's own table of contents"]:::review
    T-PTG-047 --> T-PTG-048
    T-PTG-068["T-PTG-068<br/>Profile page: link to conversations, grouped by dominant topic"]
    T-PTG-066 --> T-PTG-068
    T-PTG-052["T-PTG-052<br/>Coverage Atlas Phase 1a: member_article_activity log + signal hooks + issue-to-article resolver"]:::done
    T-PTG-051 --> T-PTG-052
    T-PTG-005["T-PTG-005<br/>Voicing-technique continuity + citation-format test matrix (all preset x tier combos)"]:::review
    T-PTG-059["T-PTG-059<br/>Feature: Greet the user in JournalGPT"]:::review
    T-PTG-063["T-PTG-063<br/>Feature: Mobile-Optimized Minimalist UI"]:::review
    T-PTG-014["T-PTG-014<br/>Add an admin 'reply to conversation' tool, then use it to notify conversation 51 that color schemes shipped"]:::review
    T-PTG-055["T-PTG-055<br/>Coverage Atlas Phase 2b: LLM tour/thread draft-proposal CLI (machine proposes, curator disposes)"]:::review
    T-PTG-054 --> T-PTG-055
    T-INTY-017["T-INTY-017<br/>Piano Dossier Data Entry Interface (Modern EAV)"]:::review
    T-PTG-054["T-PTG-054<br/>Coverage Atlas Phase 2a: tours/threads schema + curator admin page"]:::review
    T-PTG-051 --> T-PTG-054
    T-PTG-003["T-PTG-003<br/>Lock in citation-numbering fix with a real-shape regression fixture"]:::review
    T-PTG-062["T-PTG-062<br/>Feature: Advanced Prompt Builder Grid UI"]:::done
    T-PTG-058["T-PTG-058<br/>Conversation Sidebar: Minimal Weighted Topic Color Bar"]:::done
    T-PTG-061["T-PTG-061<br/>Dynamic Conversation Topic Weighting Engine"]:::done
    T-INTY-019["T-INTY-019<br/>'Open in Gazelle' deep-link button on the Piano Dossier page"]
    T-INTY-018 --> T-INTY-019
    T-PTG-057["T-PTG-057<br/>Coverage Atlas Phase 2: Create v4 conversation workflow leveraging new article-based index"]
    T-PTG-051 --> T-PTG-057
    T-PTG-052 --> T-PTG-057
    T-PTG-056["T-PTG-056<br/>Coverage Atlas Phase 2c: member-facing tour pages with closing quiz + radar integration"]:::blocked
    T-PTG-054 --> T-PTG-056
    T-PTG-052 --> T-PTG-056
    T-MIN-008["T-MIN-008<br/>Pin down Bernardi's verzicola boundary from the 1790 rules directly"]:::review
    T-PTG-021["T-PTG-021<br/>Fix stale JournalChatRenderTest assertion breaking the golden hammer suite (pre-existing, not caused by today's tasks)"]
    T-PTG-060["T-PTG-060<br/>Extend Admin Reply Mechanism for 'In Progress' Status"]:::done
    T-PTG-051["T-PTG-051<br/>Coverage Atlas foundation: run migration 018 + article-index import on the shared DB and verify the tagging matrix live"]:::done
    T-PTG-067["T-PTG-067<br/>Live Engine B refresh on a cooldown, so the conversation color bar evolves as the chat continues"]
    T-PTG-066 --> T-PTG-067
    T-PTG-070["T-PTG-070<br/>Staged progress indicator while a conversation response is generating"]
    T-PTG-066["T-PTG-066<br/>Compute Engine A topic weights live on message send (fix colorless new conversations)"]:::review
```

---


## Repo: `intypiano`

### ⏳ T-INTY-017 · P1 · ANY · PEER_REVIEW
**Piano Dossier Data Entry Interface (Modern EAV)**
**Owner:** TaskForce

**Scope:**
- Implement a modernized EAV architecture for collecting detailed Piano condition dossiers, based on the Stanford Template PDF.
- Includes schema (`dossier_field_definitions`, `piano_dossiers`, `piano_dossier_values`).
- Mobile-first data entry interface (`admin/v2/dossier_edit.php`) with segmented touch-friendly grading buttons.
- Integration into the existing V2 piano view (`admin/v2/piano.php`).

**Definition of Done:**
- SQL migration script created for the new tables and base seed data.
- `dossier_edit.php` is fully functional on mobile viewports.
- `piano.php` correctly links to the new dossier view.
- Tested via PHP linting.

*Audited against SHA:* `efef90953c62f09c2e6c74e3cee15c97ddf57980`

---
### 📋 T-INTY-019 · P2 · ANY · AUDITED
**"Open in Gazelle" deep-link button on the Piano Dossier page**
**Owner:** None

**Scope:**
- PM NOTE (2026-08-12, previously left OPEN, now AUDITED) - the admin/v2 regression that blocked this task is fixed. Verified live, not by reading - started `php -S localhost:2027 -t .` against repo-sha 6d955d99, logged in as cmiller (had to reset both `tuner.tpassword` via the documented MD5 UPDATE AND set a bcrypt `users.password_hash` + `users.email` locally - the demo DB's `users` row for cmiller had a NULL email, which the email-based login added by the 2026-08-11 auth migration requires; TESTING-LOCALLY.md's cmiller/localdev1 instructions are stale on this exact point), then hit admin/v2/piano.php?id=1 (pianos.gazelle_id = '110641', NOT NULL) and ?id=6 (gazelle_id NULL) directly. Both returned HTTP 200 with real page content ("Yamaha U-1 (1978)" / "Unknown (2010)" titles), zero occurrences of "caut_sfusd", "Fatal", "Uncaught", or "Exception" in either response body. T-INTY-021 (the fix) is confirmed DONE in task_coordinator. The admin/v2 blocker is gone.
- DEPENDENCY STATUS CORRECTION - T-INTY-018 is HUMAN_REVIEW, NOT DONE, as of this audit (peer review passed, ReviewerSonnet5 verdict PASS 2026-08-12, awaiting a human `fleet close`). Do not take a prior claim that it is "DONE" at face value - checked the YAML directly. This does not block auditing (bin/fleet.py's `cmd_audit` has no dependency check at all, only `cmd_claim` does, confirmed by reading both functions), so auditing now is safe and saves a round-trip once T-INTY-018 closes. But `fleet claim` WILL still correctly refuse this task until T-INTY-018's status is exactly DONE - a Worker hitting that refusal is expected, not a bug, and should wait / ping a PM to close T-INTY-018 rather than work around it. The underlying schema work is real already, independent of the close - ddl/146 (001-004) adds `pianos.gazelle_id VARCHAR(24)` and `inventory.gazelle_id`, both backfilled - verified live in intypiano_demo (`SELECT id, piano_code, gazelle_id FROM pianos` shows populated rows for 126 pianos and NULLs for the rest).
- GAZELLE WEB URL PATTERN - STILL GENUINELY UNKNOWN, DO NOT GUESS. Re-checked per this audit's instructions - grepped the whole repo (including the new classes/integration/GazelleAPI.php from commit 1ea83713, and admin/v2/normalization.php which uses it) for any Gazelle URL. The ONLY Gazelle URL anywhere in the codebase is the private GraphQL API endpoint `https://gazelleapp.io/graphql/private` (classes/integration/GazelleAPI.php line 5) - a machine API endpoint, not a human-facing web app URL, and POSTing GraphQL queries there tells you nothing about what path a browser needs to open a piano's record (e.g. `/pianos/{id}`, a query string, a UUID-based route, etc - all unconfirmed). T-INTY-020 (the parallel Gazelle-sync design task) also does not resolve this - it is scoped to the GraphQL API, not the web UI, and its own scope text does not mention a web URL either. This repo has no way to discover the answer without a live Gazelle account/docs. Per PM instruction, this is not being left as an open-ended "confirm before hardcoding" - the Worker MUST NOT guess a URL pattern and ship it. Definition of Done below is revised accordingly.
- Small, low-risk UI addition. Add an "Open in Gazelle" button/link to admin/v2/piano.php (the Piano Dossier / instrument page shipped in T-INTY-017, integrated with dossier_edit.php) that opens the piano's record in the Gazelle CRM in a new tab, built from the new pianos.gazelle_id column added by T-INTY-018.
- STOP CONDITION, do not skip - this PM audit re-confirmed the Gazelle web URL pattern is genuinely unknown and unresolvable from this repo (see PM note above). Before writing any URL-construction code, the Worker MUST ask the user (or whoever owns the Gazelle account) for the exact URL pattern used to open a piano record in the Gazelle web app - e.g. by opening a piano in the Gazelle UI and reading the address bar - and record the confirmed pattern in the commit message. If that answer is not obtainable in this session, STOP and hand the task back with the specific blocking question ("what is the URL to view a piano record in the Gazelle web UI, given its Gazelle ID?") rather than shipping a guessed URL. A guessed URL that silently 404s is worse than an admittedly-incomplete feature.
- Render conditionally - if pianos.gazelle_id IS NULL for this piano (e.g. it predates the Gazelle integration or was hand-entered), do not show a dead link; either hide the button or show a disabled/greyed state with a tooltip explaining why.
- Follow admin/v2/piano.php's existing conventions for buttons/links (CSRF is irrelevant here since this is a pure outbound GET link, not a form post, but match the existing visual style in that file rather than introducing a new button pattern).

**Definition of Done:**
- EITHER (a) admin/v2/piano.php shows an "Open in Gazelle" link/button when the piano's gazelle_id is set, pointing at a Gazelle URL pattern the Worker has EXPLICITLY CONFIRMED (not guessed) via the user/account owner, with that confirmation source stated in the commit message, and hides or disables the button when gazelle_id is NULL; OR (b) if confirmation is not obtainable this session, the Worker submits nothing and instead returns the task to the PM/user with the specific blocking question spelled out in the PM-audit note above. Shipping a hardcoded, unconfirmed URL guess is an explicit non-goal and fails this DoD even if the code otherwise works.
- php -l admin/v2/piano.php passes.
- Manually verified in a running server (php -S localhost:2027 -t .) against at least one piano with a gazelle_id and one without, per CLAUDE.md's "prefer running over reading" rule - screenshot or terminal evidence of both states attached to the handoff. Note for the Worker - as of this audit, local login for cmiller required resetting BOTH `tuner.tpassword` (MD5, per TESTING-LOCALLY.md) AND `users.email` + `users.password_hash` (bcrypt) on intypiano_demo, because the 2026-08-11 auth migration made login email-based and the demo `users` row for cmiller had a NULL email. If login fails with "Invalid email or password" using the documented cmiller/localdev1, check `users.email` first before assuming something else broke.
- PM AUDIT NOTE ON TEST BASELINE (2026-08-12, repo-sha 6d955d99) - neither CLAUDE.md's stale "259 tests, 0 failures" nor T-INTY-018's captured "330/564/Errors=18/Failures=114/Skipped=6" is reproducible right now. A clean run on this exact sha (server up on :2027, then ./vendor/bin/phpunit) produced Tests=330, Assertions=666, Errors=1, Failures=68 - fewer errors/failures than T-INTY-018's snapshot, consistent with T-INTY-021's admin/v2 fix landing in between, but still not 0. Do NOT let a Worker chase these pre-existing failures as part of this task - they are unrelated to Gazelle. The bar for this task is - no NEW errors/failures beyond this 330/666/1/68 shape.

*Audited against SHA:* `6d955d9962a89d24af8a5d8052eb1d67b1ea0186`

---

## Repo: `minchiate_tarot`

### ⏳ T-MIN-008 · P2 · ANY · PEER_REVIEW
**Pin down Bernardi's verzicola boundary from the 1790 rules directly**
**Owner:** Antigravity

**Scope:**
- Open the RULE-1790 (Bernardi) source directly and transcribe every verzicola combination example, replacing the Justice pilot's hedge ('I-V and beginning around XXVIII', pilot line 92) with an exact list.
- Thirteen committed studies currently lean on that hedge; the zodiac batch flags it as acutely open at XXVII (one numeral below) and XXVIII (the numeral the hedge names), and the element batch left 'whether XX-XXIII can form a verzicola' as a standing open question in all four files.
- Record whether the examples are exhaustive or exemplary in Bernardi's own text; do not convert examples into rules - the deliverable is the transcription plus locators (chapter and printed page), not an interpretation.
- If the boundary resolves, list the follow-up amendments needed (zodiac files XXVII/XXVIII sections 2 and 4, element files' open questions, Justice pilot cross-references) as a reconciliation queue; apply them only if the audit scopes that in.

**Definition of Done:**
- A sourced note in research/02-source-audit/ or research/pilots/ transcribes the verzicola examples with exact locators and states what the record can and cannot support.
- The reconciliation queue of affected files is listed with per-file line references.
- The hedge is superseded only by direct transcription, never by memory.

*Audited against SHA:* `3556e682ee0493b832d0fe092b0f1d2e20e0a3d6`

---

## Repo: `newmexicoptg.org`

### 📋 T-PTG-057 · P1 · ANY · AUDITED
**Coverage Atlas Phase 2: Create v4 conversation workflow leveraging new article-based index**
**Owner:** None

**Scope:**
- Build a "v4 situation" for the conversation workflow, likely introducing `journalgpt/v4/` parallel to `v3`.
- Migrate the search and RAG context gathering to take advantage of the new `article_index` and `article_index_topics` tables introduced in T-PTG-051/052, moving away from issue-level `articles` citations.
- Run A/B tests or evaluations against Production for this v4 implementation to ensure search results remain high quality and improve the conversational experience.

**Definition of Done:**
- V4 conversation pipeline is established and uses the new article-based indexing system.
- Search results and context are derived from `article_index` rather than issue-level PDFs.
- Evaluation tests are run against Production data to validate the new v4 workflow without breaking the existing v3 production system.

*Audited against SHA:* `148499984456a86f1d1be55b74387639df92ddce`

---
### 📋 T-PTG-021 · P1 · ANY · AUDITED
**Fix stale JournalChatRenderTest assertion breaking the golden hammer suite (pre-existing, not caused by today's tasks)**
**Owner:** None

**Scope:**
- FINDING: Chip asked that no future work be pushed to main without running the full "golden hammer" regression suite (`journalgpt/tests/security_and_eval_suite.php`, which runs 8 PHP suites plus the Python eval_runner.py -- 9 suites total). Running it as a baseline check surfaced one pre-existing failure: `JournalChatRenderTest.php:115` asserts the rendered `index.php` HTML contains the exact literal substring `href="assets/journal-chat.css"` (no query string). `index.php`'s actual stylesheet link has ALWAYS included a cache-busting `?v=<hash>` query param (confirmed via git history -- this predates every task from today's session), so this exact-substring assertion has likely been failing since the test was first written (single commit in its git history, `b89a4d7`, never updated since). This is a stale/wrong test assertion, not a real product bug -- confirmed the actual rendered HTML is correct and functional (T-PTG-013 extended the same versioned-link pattern to 6 more pages earlier today specifically because it is the correct, intentional behavior).
- FIX SCOPE: update `journalgpt/tests/JournalChatRenderTest.php:115` to check for a pattern that tolerates the version query string, e.g. a regex or `strpos` on `href="assets/journal-chat.css?v=` (matching the actual, correct, intentional markup) instead of the exact stale string. Do not weaken the assertion into something that would pass regardless of correctness (e.g. do not just delete the check) -- it should still fail if the stylesheet link is missing or malformed.
- SCAN FOR SIMILAR STALENESS: since this test file has apparently never been updated since its original creation, check its other 10 required snippets (title, journal-chat.js src, csrf_token, allowanceCount, messagesContainer, questionForm, questionInput, sendButton, grounding disclaimer text, "Test Member") against the CURRENT index.php to confirm none of the others have silently drifted stale in the same way -- if any others are found stale, fix them too and note each one in the handoff.

**Definition of Done:**
- The full golden hammer suite (`DB_HOST=127.0.0.1 DB_NAME=journal_ai_test DB_USER=root DB_PASS=root php journalgpt/tests/security_and_eval_suite.php`) reports 9/9 suites passing, 0 failures.
- The fixed assertion still meaningfully verifies the stylesheet is linked correctly -- confirm by temporarily breaking the link in a local copy (e.g. renaming the href) and re-running the test to see it correctly fail, then restoring it, per this repo's existing TDD convention (see other recent tasks' handoffs this session for the pattern: prove a test can fail before trusting that it can pass).
- Any other stale snippet assertions found during the scan are fixed and listed in the handoff, or the handoff explicitly states none were found.
- php -l passes on journalgpt/tests/JournalChatRenderTest.php.

*Audited against SHA:* `ebf93f751dbe07c86f8e3c296bbe7c9e3c88465c`

---
### ✅ T-PTG-052 · P1 · ANY · DONE
**Coverage Atlas Phase 1a: member_article_activity log + signal hooks + issue-to-article resolver**
**Owner:** Worker-Agent

**Scope:**
- Spec: docs/superpowers/specs/2026-08-17-coverage-atlas-design.md section 3. New migration (019): member_article_activity (user_id, article_index_id, activity_type ENUM(read, quiz_passed, discussed), created_at; FK to article_index; append-only, no unique constraint -- repeat engagement is real signal for recency even though the radar aggregation deduplicates per (user, article, type)).
- THE KEY TECHNICAL RISK, solve first: existing engagement signals are keyed to the ISSUE-LEVEL articles table (journalgpt_citation_logs.article_id, quiz_questions.article_id both FK to articles), but the radar needs PER-ARTICLE article_index rows. Build a resolver lib (e.g. lib/ArticleIndexResolver.php) mapping (issue-level article_id, page) -> article_index_id by joining articles.issue_date/volume/pdf_filename to article_index.issue_label (format like "Jan-79") and picking the article_index row whose page range contains the cited page (rows sorted by page within an issue; a row spans from its page to the next row's page - 1). Resolver returns null on no-match; log unresolved hits, never guess. TDD the resolver against real fixture rows before wiring any hooks.
- Hooks, all thin: (1) read -- source.php PDF opens that carry an article_index context, and citation renders in answers count via (3); (2) quiz_passed -- in submit_quiz_attempt.php after scoring, for each correctly-answered question resolve its article_id+page and log; (3) discussed -- where journalgpt_citation_logs rows are written, resolve and log alongside. Hooks must be fail-open: a resolver miss or insert failure must never break the member-facing request.

**Definition of Done:**
- Migration 019 applied to the local test DB via cli/migrate.php with no errors.
- Resolver test proves correct mapping for a multi-article issue fixture (first, middle, last article by page) and returns null for an unmatchable page/issue.
- Each of the three hooks writes a correct member_article_activity row in its existing test (extend QuizTest / CitationLoggingTest rather than new suites where natural), and a forced resolver failure does not change the endpoint''s response.
- Golden hammer suite passes with zero regressions.

*Audited against SHA:* `148499984456a86f1d1be55b74387639df92ddce`

---
### ✅ T-PTG-061 · P1 · backend · DONE
**Dynamic Conversation Topic Weighting Engine**
**Owner:** Worker-Agent

**Scope:**

**Definition of Done:**

*Audited against SHA:* `148499984456a86f1d1be55b74387639df92ddce`

---
### ✅ T-PTG-051 · P1 · ANY · DONE
**Coverage Atlas foundation: run migration 018 + article-index import on the shared DB and verify the tagging matrix live**
**Owner:** Worker-Agent

**Scope:**
- Background, read first: docs/superpowers/specs/2026-08-17-coverage-atlas-design.md (the Coverage Atlas spec this epic delivers; supersedes the 2026-08-16 learning-paths skill-tree spec). The code is ALREADY MERGED into test and pushed (commit a8f88e1 "feat: editable article-index x topic matrix"): migration journalgpt/migrations/018_article_index.sql, lib/ArticleIndexImporter.php, cli/import_article_index.php, data/article_index.csv (4,120 rows), admin_article_index_matrix.php, api/toggle_article_index_topic.php, tests/ArticleIndexMatrixTest.php (22 assertions, passing locally).
- This task is ONLY the shared-database rollout: run migration 018 and cli/import_article_index.php against the deployed environment, then browser-verify admin_article_index_matrix.php on test.newmexicoptg.org (login, grid renders 4,120 articles, one checkbox toggle round-trips to article_index_topics and survives reload).
- HARD CONSTRAINT (memory + fleet README): test.newmexicoptg.org SHARES the production database. Migration 018 is additive-only (two new tables, no ALTERs), but the DB write still requires Chip's explicit go at execution time. Do not run the migration or import without that confirmation recorded in this task's events.

**Definition of Done:**
- article_index and article_index_topics tables exist in the shared DB; SELECT COUNT(*) FROM article_index returns 4120.
- Re-running cli/import_article_index.php a second time leaves the count at 4120 (idempotency verified in the real environment).
- admin_article_index_matrix.php on test.newmexicoptg.org renders the grid for a logged-in member, one checkbox toggle persists across a reload, and no PHP errors appear in debug_logs.
- Golden hammer suite still passes locally (DB_HOST=127.0.0.1 DB_NAME=journal_ai_test DB_USER=root DB_PASS=root php journalgpt/tests/security_and_eval_suite.php).

*Audited against SHA:* `148499984456a86f1d1be55b74387639df92ddce`

---
### ⏳ T-PTG-053 · P1 · ANY · PEER_REVIEW
**Coverage Atlas Phase 1b: coverage radar dashboard + empty-wedge nudge**
**Owner:** Claude-Fable-Session

**Scope:**
- Spec: sections 3 and 5 of docs/superpowers/specs/2026-08-17-coverage-atlas-design.md. Member-facing radar page (extend profile.php or new coverage.php following its pattern -- T-PTG-049 established profile.php as the member-dashboard precedent): one axis per article_topic_categories row, member score per axis = weighted distinct engagement over that territory's tagged articles (read=1, discussed=2, quiz_passed=3, deduped per (article, type)), normalized against the territory's total tagged-article count so big territories don't dominate.
- Rendering: no charting framework -- inline SVG polygon radar in the page, same no-build-step convention as admin_topic_matrix.php. Must render sanely at 0 activity (empty radar, inviting copy) and with sparse taxonomy tagging.
- The nudge: below the radar, the member's 3 weakest axes each list up to 3 suggested articles from that territory the member has NOT engaged, ranked by cross-member popularity (reuse T-PTG-049's popular-but-unread query shape, re-targeted through article_index_topics).
- HONEST-DATA GUARD: radar quality depends on human tagging coverage in admin_article_index_matrix.php (a separate, ongoing human effort). The page must surface tagging coverage ("N of 4,120 articles tagged so far") rather than presenting a thin-tag radar as truth.

**Definition of Done:**
- Radar page renders for a member with zero activity, partial activity, and for a territory with zero tagged articles, without errors.
- Axis scoring proven by test - a member with one quiz_passed on a tagged article scores exactly 3 on that territory and 0 elsewhere; dedup proven (two reads of the same article count once).
- Nudge query proven by test - suggests only untagged-by-member articles from weak territories, popularity-ordered.
- Tagging-coverage line shows the true tagged/total counts.
- Golden hammer suite passes with zero regressions; php -l clean.

---
### ⏳ T-PTG-048 · P1 · ANY · PEER_REVIEW
**Article/editorial completeness QC pass beyond page-coverage checking, ground-truthed against PTJ-2020-02's own table of contents**
**Owner:** Worker-ArticleQC1

**Scope:**
- Rescope note: this task previously covered vision-model classification of generic gap pages (mostly sparse advertisement pages). Per direct user feedback, that is NOT the priority -- the user does not care much about ad-page classification. What the user actually wants is article/editorial completeness QC: for every piece the extraction pipeline classifies as a real article, editorial, or column (not ad/classified/display-ad-index), confirm by actually reading the source text across that piece's claimed page range that nothing was left out. This is a full rewrite of the task's scope, not an addendum to the old one -- the vision/gap-page-classification framing below no longer applies and should not be pursued under this task ID.

- Background, read first, in full: docs/superpowers/specs/2026-08-14-per-article-extraction-spike-findings.md (original spike + Addendum) and docs/30-Engineering/2026-08-14-page-coverage-validation-repair-pass.md (T-PTG-047's report, now DONE -- read its Recommendation section). T-PTG-047 built a text-side page-coverage checker (coverage.py) plus TOC-anchor-offset repair and a "continued on p. X" scan, and found that a page can show zero gaps/overlaps under that checker and still be wrong: the checker only verifies every page number is claimed by exactly one piece, it cannot tell whether a piece's claimed text is actually complete, uncut, and correctly bounded. That is precisely the class of error this task targets, and it is why this task requires an agent to read real source text, not just diff page numbers.

- Setup note: as of this rewrite, T-PTG-047's code and report exist on branch `test-T-PTG-047` (worktree `../newmexicoptg.org-T-PTG-047`) and have NOT yet been merged into `test` (confirmed via `git merge-base --is-ancestor test-T-PTG-047 test`, which currently fails) even though the task_coordinator's archived copy of T-PTG-047 shows status DONE. The worker on this task must re-check merge status at task start; if still unmerged, reference `journalgpt/spikes/T-PTG-047/` (extract_pieces.py, coverage.py, toc_offset_repair.py, boundary_trim.py, continued_scan.py, run_pipeline.py, common.py) from that branch/worktree directly rather than waiting, exactly as T-PTG-047 itself had to reference material from a prior unmerged branch. Reuse extract_pieces.py and coverage.py as-is (import/call, do not reimplement) so results remain methodologically comparable.

- Primary required test case -- use this exactly, it is real ground truth derived directly from the issue's own table of contents, not invented: issue `PTJ-2020-02` (`journalgpt/corpus/extracted/PTJ-2020-02/PTJ-2020-02-A01.txt`, PDF at `journalgpt/pdfs/PTJ-2020-02.pdf`). Its own TOC (anchor pages 6-8, confirmed present via `grep '\[\[page:6\]\]'` through `'\[\[page:8\]\]'` on the extracted text) lists every piece by title, author, and printed page number. Ground truth (printed page -> anchor page via this issue's confirmed +2 offset):
| Printed p. | Anchor p. | Title | Author |
|---|---|---|---|
| 2 | 4 | Editorial Perspective | Scott Cole, RPT |
| 6 | 8 | President's Message | Paul Adams, RPT |
| 7 | 9 | TT&T | Scott Cole, RPT |
| 10 | 12 | The Piano Corner | ChiaYu Lee, RPT |
| 14 | 16 | Tight Tuning Pins, Part 1 | Larry Lobel, RPT |
| 21 | 23 | Re-Covering Hammers by Hand | Fred Sturm, RPT |
| 26 | 28 | Hunting for Education (Complete Piano Voicing) | Amy Zilk, RPT |
| 27 | 29 | Music Theory for the Piano Technician, Part 8 | Scott Cole, RPT |
| 31 | 33 | Reweighing the Original Keyboard, Part 2 | Nick Gravagne, RPT |
| 37 | 39 | PTG Review | (none) |
| 38 | 40 | Coming Events | (none) |
| 39 | 41 | Foundation Focus | (none) |
| 40 | 42 | Classified Advertisements | (none) |
| 43 | 45 | Display Advertising Index | (none) |
| 44 | 46 | Tuner's Life | Kathy Smith, RPT |
This table specifically stresses SHORT columns/editorials (Editorial Perspective, President's Message, TT&T, The Piano Corner) the original 8-issue spike sample didn't specifically target -- exactly the kind of short item likely to get silently merged into a neighboring piece or dropped, per the user's own framing of the concern ("really, any article or editorial mentioned in the columns and comments... that's what we should be concerned about").

- In scope, required: run the extraction pipeline (extract_pieces.py from journalgpt/spikes/T-PTG-047/, same gpt-4o-mini/full-text/single-call approach) against PTJ-2020-02, then diff the result against all 15 ground-truth rows above: for each row, report whether the extraction found a matching piece (same or equivalent title/author) and whether its page range plausibly starts/ends where the TOC says (allow the piece's *end* page to extend until the next item's start, since the TOC only gives start pages). Report hits, misses, and merges explicitly per row, not just an aggregate count.

- In scope, required, this is the actual QC deliverable: for every extraction-produced piece classified as `article`, `editorial`, or a column-type (i.e., anything except `advertisement`, `classifieds`, or a display/index type) across PTJ-2020-02, an agent must actually read the source text in journalgpt/corpus/extracted/PTJ-2020-02/PTJ-2020-02-A01.txt spanning that piece's claimed page range and confirm: (a) the text reads as a complete, coherent piece with a real ending, not cut off mid-sentence or mid-thought; (b) the byline matches; (c) nothing from the ground-truth table that should be a separate piece got silently absorbed into it. This must be an actual content read per piece, not a page-number diff -- the whole point is to catch errors coverage.py structurally cannot see (zero gaps/overlaps reported, but a piece is still truncated or two pieces are merged into one).

- In scope, required, single most important pass/fail signal for this task: explicitly check the short-column failure mode by name -- does the extraction correctly produce SIX separate pieces for the six short department items (Editorial Perspective, President's Message, TT&T, The Piano Corner, Tight Tuning Pins Part 1, Re-Covering Hammers by Hand), each plausibly short (roughly 1-4 pages), or does it merge some of them into a single blob, or skip any entirely? State a direct yes/no answer to "does the six-short-department-item failure mode occur in PTJ-2020-02" in the report.

- In scope, but explicitly LOW priority per the user's direct statement ("we're not really concerned about the ads"): the 5 ad/index/listing rows in the ground-truth table (PTG Review, Coming Events, Foundation Focus, Classified Advertisements, Display Advertising Index) only need the hit/miss/merge check from the diff step above -- report whether each was found, but do NOT spend deep QC-read rigor confirming their content is complete/uncut the way the 9 real article/editorial/column rows require.

- In scope, required, secondary check (not the primary deliverable): extend the same QC-read approach to a small sample from the original 8 T-PTG-047 spike issues (PTG-2022-10, PTJ-2019-02, PTJ-2019-08, PTJ-2020-04, PTJ-2022-06, PTJ-2024-01, PTJ-2025-03, PTJ-2025-10) -- worker's judgment on how many, at least 2-3 -- to see whether the short-column merge/drop failure mode found (or not found) in PTJ-2020-02 generalizes, or is specific to this issue's TOC-heavy front-matter layout. These issues do not have the same kind of hand-derived ground-truth TOC table as PTJ-2020-02; use each issue's own `[[page:N]]`-anchored TOC section as the reference instead, the same way the PTJ-2020-02 table was derived.

- In scope, required: a written report under docs/30-Engineering/ (Dewey Decimal protocol per task_coordinator/README.md), with frontmatter matching task_coordinator/schemas/doc_frontmatter.schema.json, presenting: the full PTJ-2020-02 ground-truth diff table (hit/miss/merged per row, all 15 rows), the QC-read findings for each of the 9 real article/editorial/column pieces, an explicit yes/no on whether the six-short-department-item failure mode occurs, findings from the secondary 2-3-issue sample, and a clear recommendation on whether article/editorial completeness (as distinct from generic page-range coverage) can be trusted, or what further work is still needed.

- Out of scope, do not do (carried forward from the original task, still applies): no articles/pieces schema design or database migration; no indexing the 23 missing corpus years (2019 Feb-Dec, 2025 Jan-Dec) into test/prod; no production code changes (journalgpt/corpus/extract_corpus.py or any other shipped pipeline code); no touching the shared test/prod database in any way (no migration, no backfill, no admin-page changes) -- this task is local/offline analysis only against journalgpt/pdfs/, journalgpt/corpus/extracted/, and journalgpt/spikes/T-PTG-047/ output, same framing as T-PTG-047. Also explicitly out of scope, carried forward from the old vision-classification framing this task is replacing: no vision-model/image-based page classification work under this task ID -- that framing has been dropped per the rescope above, not deferred to be picked back up here.


**Definition of Done:**
- extract_pieces.py and coverage.py from journalgpt/spikes/T-PTG-047/ are reused (imported/called, not reimplemented) to produce PTJ-2020-02's extraction output and page-coverage numbers.

- A complete diff table exists in the report covering all 15 PTJ-2020-02 ground-truth rows from the scope section above, each explicitly marked hit, miss, or merged, with the matching (or non-matching) extracted piece's title/author/page-range shown alongside.

- For each of the 9 ground-truth rows that are article/editorial/column type (i.e. excluding the 5 ad/index rows), the report shows evidence of an actual source-text read (not just a page-number comparison) confirming or refuting: complete/uncut ending, matching byline, and no silent absorption of a neighboring ground-truth piece.

- The report gives an explicit, direct yes/no answer to whether the six-short-department-item merge/drop failure mode (Editorial Perspective, President's Message, TT&T, The Piano Corner, Tight Tuning Pins Part 1, Re-Covering Hammers by Hand) occurs in PTJ-2020-02, with the specific evidence (which items merged into what, or which were dropped, if any).

- The report documents a QC-read pass (using the same read-the-source-text method, not just a coverage-checker diff) against at least 2-3 issues from the original 8 T-PTG-047 spike issues, with an explicit statement of whether the same short-column failure mode does or does not generalize beyond PTJ-2020-02.

- A written report exists under docs/30-Engineering/ with frontmatter matching task_coordinator/schemas/doc_frontmatter.schema.json, and gives a clear, explicit recommendation on whether article/editorial completeness (as distinct from T-PTG-047's generic page-coverage checking) can be trusted at this point, or what further work is still needed.

- No changes were made to journalgpt/corpus/extract_corpus.py or any other production code path, no database migration was created or run, and no test/prod admin endpoint was touched -- all work is local scripts/output under journalgpt/spikes/ (a new T-PTG-048 subdirectory or an extension of T-PTG-047's, worker's judgment, documented either way) and the docs/ report.


*Audited against SHA:* `a527e9d`

---
### ⏳ T-PTG-005 · P1 · ANY · PEER_REVIEW
**Voicing-technique continuity + citation-format test matrix (all preset x tier combos)**
**Owner:** Claude-FleetCommander

**Scope:**
- journalgpt/tests/manual_voicing_continuity_matrix.php (new) — runs a real two-turn conversation through JournalAnswerService::ask() for a given (preset, tier) combination: turn 1 asks 'Have voicing technique changed over the years? Are there different viewpoints of what should be done? Do any contradict another?'; turn 2 asks the follow-up 'Who talks about this first?' in the SAME conversation_id.
- Exercises all 6 combinations: preset in {scholarly, quick} x tier in {quick, medium, deep} (quick=gpt-4o-mini, medium=gpt-4o, deep=o3-mini). Makes REAL OpenAI API calls against the configured key — not free, not part of the automated test suite.
- Purpose: (a) verify turn 2 actually resolves 'this'/'first' against turn 1's context (conversation continuity, per Chip's question about whether follow-ups work at all), and (b) verify citation format correctness (page_verified, url/pdf_url shape, page-range collapsing, no leaked 【…】 markers) holds across every tier, not just the tiers already covered by the automated unit tests with a StubOpenAIClient.

**Definition of Done:**
- All 6 (preset, tier) combinations executed successfully (or their failure mode is understood and recorded — e.g. Deep tier timing out before the T-PTG-timeout fix).
- For each combination, record: did turn 2 correctly resolve the follow-up against turn 1's topic, or did it behave as if starting fresh?
- For each combination, record whether citations are well-formed: every citation has a real article_id + page, citation_label matches the printed_page/printed_page_end shown, url/pdf_url follow the source.php?article_id=X&page=Y shape, and the answer text carries no raw 【…】 annotation markers.
- Findings written up (this task's own execution log / a feedback file) — not just raw JSON dumps — identifying any combination that fails continuity or citation format, with a specific hypothesis for why if one fails.

*Audited against SHA:* `267ebaf267b3cd0b5b0727baa79c26b858cf32ac`

---
### ⏳ T-PTG-003 · P1 · ANY · PEER_REVIEW
**Lock in citation-numbering fix with a real-shape regression fixture**
**Owner:** Antigravity

**Scope:**
- journalgpt/tests/JournalAnswerServiceTest.php
- journalgpt/tests/eval_dataset.sample.json (or a new sibling fixture file) — add a fixture reproducing the actual reported 'Golden Hammer Award recipients' case shape as closely as possible without shipping real user data: a multi-paragraph answer with a handful of inline [n] markers, and a StubOpenAIClient retrieved_chunks payload spanning many issues/pages (2019 through 2025) so the test exercises real cross-issue volume, not just 2-3 chunks.
- This task exists because T-PTG-001 and T-PTG-002's own regression tests are necessarily synthetic/minimal; this task's job is to add a second, independent test built directly from the bug report so the fix is verified against the actual failure shape, not just a simplified version of it.

**Definition of Done:**
- New test method added asserting, end-to-end through JournalAnswerService::ask() (not just the internal resolver methods), that the final answer string's footnote count equals its inline marker count, and every footnote's citation_label refers to an article/page combination that genuinely appears in the stubbed retrieved_chunks/annotations — no orphaned or fabricated footnote.
- Test fails against the pre-T-PTG-001/002 code (verify by temporarily checking out the prior revision or reasoning through the diff) and passes after.
- Full suite (tests/JournalAnswerServiceTest.php) passes.

*Audited against SHA:* `9e74d39c82a5980f488695fb4e4e5e1dd46bdb54`

---
### ⏳ T-PTG-066 · P1 · ANY · PEER_REVIEW
**Compute Engine A topic weights live on message send (fix colorless new conversations)**
**Owner:** Claude-Sonnet-Session

**Scope:**
- Bug found live: a brand-new conversation shows no topic-color-bar at all in the sidebar until someone manually runs a full admin_conversation_weights.php batch. Root cause confirmed: index.php:237 only renders the bar `if (!empty($conv['combined_weights_json']))`, and that column is exclusively written by ConversationTopicWeightRunner::run(), which only ever runs as a manual batch job (admin_conversation_weights.php) -- nothing computes weights at conversation-creation or per-message time.
- Extract ConversationTopicWeightRunner::scoreEngineA() (journalgpt/lib/ConversationTopicWeightRunner.php) usage into a path that can run synchronously and cheaply after every message send (wherever messages are inserted -- likely journalgpt/api/ask.php or the conversation-creation handler). Engine A is pure local keyword scoring (no OpenAI call, no cost, no budget check needed) -- safe to run on every turn.
- On each message send: recompute engine_a_weights_json for the conversation from all its messages so far, and write combined_weights_json using the SAME combine() logic ConversationTopicWeightRunner uses today (Engine A alone if Engine B has never run yet, otherwise Engine A + the last computed Engine B). Do NOT touch topic_weights_attempted_at or engine_b_weights_json here -- those stay exclusively owned by ConversationTopicWeightRunner's batch job (T-PTG-061/023/024's eligibility and retry-count machinery must not be disturbed by this live path).
- A brand-new conversation must show SOME color bar in the sidebar after its first message, even before any admin batch has ever run.

**Definition of Done:**
- New test proves: creating a conversation and sending one message (with real piano-technology keywords) results in engine_a_weights_json and combined_weights_json being populated immediately, with no OpenAI/Engine B call involved.
- Existing ConversationTopicWeightRunnerTest suite (7 tests) and the topicless/retry regression tests still pass unmodified -- this task must not touch batch eligibility logic (topic_weights_attempted_at, topic_weights_attempt_count).
- The sidebar (index.php) renders a non-empty topic-color-bar for a freshly created, never-batch-processed conversation after its first message, verified via the browse skill against the local test-branch preview server.
- Golden hammer suite passes with zero regressions; php -l clean.

*Audited against SHA:* `9cce8a8c2d1b09c2b6ee30b991ea3ffad59bc6a5`

---
### 📋 T-PTG-068 · P2 · ANY · AUDITED
**Profile page: link to conversations, grouped by dominant topic**
**Owner:** None

**Scope:**
- Chip's ask: "we'll need a link from my profile to various conversations (how would you make this useful?)". Plain reasoning: profile.php already aggregates combined_weights_json across a member's conversations into the coverage bar (see its "Aggregate topic color bar" comment block) but never links back to the individual conversations that fed it. The useful version groups conversations by DOMINANT topic (the highest-weight entry in each conversation's combined_weights_json) using the SAME 15-color palette as the sidebar/homepage grid, turning the profile page into topic-based navigation rather than a dead-end stat.
- Add a section to profile.php: for each of the 15 topics the member has any coverage in, a collapsible group titled with the topic (colored swatch matching $topicColors) listing that topic's conversations (title, updated_at, link to index.php?conversation=ID or however conversations are opened today -- check index.php's existing conversation-open URL/JS pattern rather than inventing a new one). A conversation with multiple significant topic weights may need to decide whether it appears under just its top topic or every topic above some threshold (e.g. >= 15%) -- pick one, document the reasoning in a code comment.
- Depends on T-PTG-066 because grouping is only useful once new conversations actually get combined_weights_json promptly instead of sitting colorless/ungrouped until the next manual batch.
- Empty/sparse states matter: a member with zero weighted conversations, or a topic with zero conversations, must render sensibly (no empty accordion headers with nothing useful under them) -- this page already has a coverage note for partial-data honesty, follow that same pattern.

**Definition of Done:**
- Test proves conversations are correctly grouped by dominant topic from combined_weights_json fixtures, including the multi-topic-threshold decision documented above.
- Manual verification via the browse skill: profile.php renders topic groups with working links that open the correct conversation in index.php.
- No N+1 query blowup -- one query (or a small fixed number) fetches all of a member''s conversations with weights, not one query per topic.
- Golden hammer suite passes with zero regressions; php -l clean.

*Audited against SHA:* `9cce8a8c2d1b09c2b6ee30b991ea3ffad59bc6a5`

---
### 📋 T-PTG-067 · P2 · ANY · AUDITED
**Live Engine B refresh on a cooldown, so the conversation color bar evolves as the chat continues**
**Owner:** None

**Scope:**
- Chip's ask: "I want bars to evolve and change in color as the conversation continues." T-PTG-066 makes the bar appear instantly (Engine A only, free). This task adds the real LLM-scored half (Engine B) back in on a live cadence instead of only via the manual admin batch, so the bar's shape actually sharpens/shifts as more is discussed -- without calling OpenAI on every single message (cost + latency).
- Cooldown policy: recompute Engine B (ConversationTopicWeightRunner::scoreEngineB()) for a conversation when BOTH (a) at least N messages (suggest N=4, confirm with Chip or pick a sensible default and document the reasoning) have been added since the last Engine B computation, AND (b) the org monthly budget check (UsagePolicy) passes -- reuse the existing budget-skip behavior from ConversationTopicWeightRunner rather than duplicating it.
- This is a SEPARATE trigger path from the T-PTG-066 live Engine A write and from the existing batch job -- do not let all three race and double-log usage_events for the same conversation. Reuse scoreEngineB()'s existing usage_events logging (one row per real LLM call, T-PTG-030 convention) as the single source of truth; this task must not introduce a second logging path.
- The manual admin batch (admin_conversation_weights.php / topic_weights_attempted_at eligibility) keeps working as the backstop for conversations that go quiet before hitting the live cooldown threshold -- this task does not replace it, it just makes most conversations settle live instead of waiting for a manual batch click.

**Definition of Done:**
- Test proves: a conversation that accumulates >= N messages triggers exactly one live Engine B call and updates combined_weights_json; a conversation with fewer than N new messages since its last Engine B pass triggers zero live calls.
- Test proves the live path and the batch path never double-bill: a conversation whose live cooldown already ran Engine B is not re-billed by the next admin batch run for the same content (extend the existing topic_weights_attempted_at semantics rather than inventing a parallel state).
- Budget-exhausted behavior matches the batch job exactly (Engine A/live-partial result kept, Engine B silently skipped, no error surfaced to the member).
- Golden hammer suite passes with zero regressions; php -l clean.

*Audited against SHA:* `9cce8a8c2d1b09c2b6ee30b991ea3ffad59bc6a5`

---
### 📋 T-PTG-070 · P2 · ANY · AUDITED
**Staged progress indicator while a conversation response is generating**
**Owner:** None

**Scope:**
- Chip's ask: a question can take a while to answer with no feedback beyond a spinner. Wants a status line under the conversation showing real stages as they happen (e.g. "Tagging conversation... researching articles... tying concepts together...") with a rough time expectation.
- Investigated JournalAnswerService::ask() (v3_beta preset, the default path): it is NOT one OpenAI call, it is 4-6 SEQUENTIAL calls -- ResearchPlanner (1 call, decides search queries, may branch into a clarifying question instead), EvidenceRetriever (1 call PER search query the planner generated, usually 2-4), EvidenceRanker (1 call, filters/ranks retrieved chunks), AnswerSynthesizer (1 call, writes the final answer). ClaimValidator and citation resolution after that are local/instant. These are the real, honest stages to surface -- not decorative copy.
- ARCHITECTURE DECISION NEEDED (why human_review_required): ask.php currently runs synchronously -- one HTTP request, one response, no way for the frontend to see intermediate progress mid-request. Two ways to get real stage updates to the member while waiting, pick one: (a) POLLING: JournalAnswerService writes its current stage to a lightweight per-request progress row (new table or reuse an existing one) as it reaches each stage; the frontend polls a small status endpoint every ~1s while ask() is in flight. Simpler, fits the existing synchronous-PHP-request architecture, no new infrastructure. (b) STREAMING (SSE or chunked response): ask.php pushes stage-transition events directly down the same connection as they happen. No polling overhead, but nothing in this codebase uses SSE/streaming today -- new infrastructure, more invasive change. Recommend (a) given the codebase's existing patterns, but this is Chip's call.
- Time expectations: duration_ms is currently only logged as a single TOTAL per request (debug_logs.duration_ms, usage_events.request_duration_ms) -- there is no per-stage timing history to draw a real "usually takes N seconds" estimate from yet. Either (a) ship with a rough static estimate per stage for v1 and add per-stage timing logging alongside this feature so real historical estimates become possible later, or (b) add per-stage duration_ms columns/logging as part of this task itself if Chip wants real estimates from day one. Flag this choice for review too.

**Definition of Done:**
- A member watching a question generate sees the status line advance through real stages (not a generic spinner) matching what ask() is actually doing at that moment.
- Test proves stage transitions are recorded/exposed correctly for both the v3_beta pipeline (4-6 stages) and the legacy/fallback path (fewer stages) -- the indicator must not lie about a stage that didn't actually run (e.g. no "ranking evidence" stage shown for a request that degraded to the legacy path per T-PTG-026's graceful-degradation catch).
- No regression to actual answer latency -- the progress mechanism (polling or streaming) must not itself slow down ask()'s critical path.
- Golden hammer suite passes with zero regressions; php -l clean.

*Audited against SHA:* `30d1985719a9b9935dbb77fdde540a87102a23b5`

---
### 🛑 T-PTG-056 · P2 · ANY · BLOCKED
**Coverage Atlas Phase 2c: member-facing tour pages with closing quiz + radar integration**
> 🛑 **BLOCKED REASON:** Interrupted mid-implementation by an unrelated homepage redesign task in the same session. Uncommitted work (TourQuizService.php, generate_tour_quiz.php, 3 tests -- one referencing TourProgressService which was never written) stashed on branch test-T-PTG-056 in worktree ../newmexicoptg.org-tourpages (git stash list). Blocking to release the repo lock for P1 work (T-PTG-066); resume by popping the stash and continuing from TourProgressService.

**Owner:** Claude-Fable-Session

**Scope:**
- Spec: sections 4-5 of docs/superpowers/specs/2026-08-17-coverage-atlas-design.md. Member-facing shelf (tours.php: published tours/threads listed with blurb, stop count, estimated reading time) and tour detail page (tour.php?id=N: ordered stops with connective notes, links to each article's source PDF at its page, per-stop read tracking into member_article_activity via T-PTG-052's hooks).
- Closing quiz: "Finish with a quiz" generates one quiz drawn from the tour's articles. Reuse the existing engine -- generate_topic_quiz.php is the closest precedent for non-conversation quiz generation; the tour variant seeds generation from the tour's article set. Grounding rules unchanged: every question keeps its NOT NULL article FK. Passing logs quiz_passed activity for the tour's articles answered correctly, so finishing a tour visibly lands on the member's radar.
- Completion display: a tour shows per-member progress (stops engaged / total, quiz taken or not) derived from member_article_activity -- no new progress table (spec section 4 explicitly forbids one).

**Definition of Done:**
- Shelf and detail pages render for a member; draft tours are never visible.
- Tour quiz generation proven by test (mocked model) - questions ground only to the tour''s articles; ungrounded proposals discarded.
- Completing a tour (engage all stops + pass quiz) measurably moves the member''s radar axis in T-PTG-053''s scoring test harness.
- Progress derivation proven by test against member_article_activity fixtures.
- Golden hammer suite passes with zero regressions; php -l clean.

---
### ✅ T-PTG-062 · P2 · frontend · DONE
**Feature: Advanced Prompt Builder Grid UI**
**Owner:** Worker-Agent

**Scope:**

**Definition of Done:**

*Audited against SHA:* `148499984456a86f1d1be55b74387639df92ddce`

---
### ✅ T-PTG-058 · P2 · Frontend · DONE
**Conversation Sidebar: Minimal Weighted Topic Color Bar**
**Owner:** Worker-Agent

**Scope:**

**Definition of Done:**

*Audited against SHA:* `148499984456a86f1d1be55b74387639df92ddce`

---
### ✅ T-PTG-060 · P2 · frontend · DONE
**Extend Admin Reply Mechanism for 'In Progress' Status**
**Owner:** Worker-Agent

**Scope:**

**Definition of Done:**

*Audited against SHA:* `148499984456a86f1d1be55b74387639df92ddce`

---
### ⏳ T-PTG-069 · P2 · ANY · PEER_REVIEW
**Profile page: link "My Research" article citations to their source PDFs (HigherLogic issue_url)**
**Owner:** Claude-Sonnet-Session

**Scope:**
- Chip's ask: profile.php's "My Research" section (e.g. "Business & Shop Practices -- 10 / 67 articles cited -- click to expand and view links to articles") currently shows counts with no actual links to the articles. Chip asked whether we should use AWS-hosted PDF links from the recently-ingested index -- checked and corrected: `article_index.issue_url` (journalgpt/migrations/018_article_index.sql, populated from journalgpt/data/article_index.csv) is NOT AWS-hosted -- it's a `my.ptg.org` HigherLogic document-library download link (`DownloadDocumentFile.ashx?DocumentFileKey=...`). Chip confirmed 2026-08-18: use these HigherLogic links.
- Wire "click to expand" in profile.php's My Research section to list the actual cited articles per category (find the citation source -- likely journalgpt_citation_logs per journalgpt/migrations/016_journalgpt_citation_logs.sql, or wherever "N / 67 articles cited" is currently counted from) with each article title linking out to its `article_index.issue_url`.
- These are `my.ptg.org` member-portal links -- they will require the member to already be logged into my.ptg.org in their browser (separate session from this app); do not attempt to proxy or embed the PDF, just link out target="_blank" and say so in adjacent copy if it reads as unclear.
- CORRECTED DURING IMPLEMENTATION (2026-08-18): checked, and "N / 67 articles cited" is backed by issue-level `articles`/`article_topics`/`journalgpt_citation_logs` (article_id + physical page), NOT `article_index` -- no direct FK between them. Chip pointed out `ArticleIndexResolver.php` (built for T-PTG-052) already exists and does exactly this join (issue-level articles.id + PRINTED page -> article_index_id), used and tested for CoverageRadarService/TourProposer/TourService. Use it: convert journalgpt_citation_logs.page (physical) to printed via JournalAnswerService::physicalToPrintedPage($page, $article['pdf_page_offset']), call ArticleIndexResolver::resolve($articleId, $printedPage), then look up that article_index row's issue_url. On any resolver miss or null issue_url, fall back to the existing internal source.php?article_id=X&page=Y link (article_id + physical page are always available regardless of resolution) rather than showing nothing.

**Definition of Done:**
- Test proves: expanding a "My Research" category renders one link per cited article, pointed at the correct issue_url when present, and degrades gracefully (no dead link, no fatal) when an article's issue_url is null.
- Manual verification via the browse skill that clicking a category expands to real article links.
- Golden hammer suite passes with zero regressions; php -l clean.

*Audited against SHA:* `9cce8a8c2d1b09c2b6ee30b991ea3ffad59bc6a5`

---
### ⏳ T-PTG-065 · P2 · backend · PEER_REVIEW
**Webhook Sync for Localhost Conversations**
**Owner:** None

**Scope:**
- I
- m
- p
- l
- e
- m
- e
- n
- t
-  
- a
-  
- w
- e
- b
- h
- o
- o
- k
-  
- t
- o
-  
- s
- y
- n
- c
- h
- r
- o
- n
- i
- z
- e
-  
- l
- o
- c
- a
- l
- h
- o
- s
- t
-  
- c
- o
- n
- v
- e
- r
- s
- a
- t
- i
- o
- n
- s
-  
- t
- o
-  
- t
- h
- e
-  
- p
- r
- o
- d
- u
- c
- t
- i
- o
- n
-  
- d
- a
- t
- a
- b
- a
- s
- e
- .
- 

- 1
- .
-  
- C
- r
- e
- a
- t
- e
-  
- `
- j
- o
- u
- r
- n
- a
- l
- g
- p
- t
- /
- a
- p
- i
- /
- s
- y
- n
- c
- _
- c
- h
- a
- t
- .
- p
- h
- p
- `
-  
- t
- o
-  
- r
- e
- c
- e
- i
- v
- e
-  
- i
- n
- c
- o
- m
- i
- n
- g
-  
- c
- o
- n
- v
- e
- r
- s
- a
- t
- i
- o
- n
-  
- p
- a
- y
- l
- o
- a
- d
- s
- .
- 

- 2
- .
-  
- P
- r
- o
- t
- e
- c
- t
-  
- t
- h
- e
-  
- e
- n
- d
- p
- o
- i
- n
- t
-  
- w
- i
- t
- h
-  
- a
-  
- s
- h
- a
- r
- e
- d
-  
- s
- e
- c
- r
- e
- t
-  
- k
- e
- y
-  
- (
- e
- .
- g
- .
-  
- S
- Y
- N
- C
- _
- S
- E
- C
- R
- E
- T
- )
- .
- 

- 3
- .
-  
- M
- o
- d
- i
- f
- y
-  
- `
- j
- o
- u
- r
- n
- a
- l
- g
- p
- t
- /
- a
- p
- i
- /
- a
- s
- k
- .
- p
- h
- p
- `
-  
- (
- o
- r
-  
- w
- h
- e
- r
- e
- v
- e
- r
-  
- c
- o
- n
- v
- e
- r
- s
- a
- t
- i
- o
- n
- s
-  
- a
- r
- e
-  
- i
- n
- s
- e
- r
- t
- e
- d
- )
-  
- s
- o
-  
- t
- h
- a
- t
-  
- i
- f
-  
- a
-  
- S
- Y
- N
- C
- _
- E
- N
- D
- P
- O
- I
- N
- T
-  
- e
- n
- v
- i
- r
- o
- n
- m
- e
- n
- t
-  
- v
- a
- r
- i
- a
- b
- l
- e
-  
- i
- s
-  
- s
- e
- t
- ,
-  
- i
- t
-  
- f
- i
- r
- e
- s
-  
- a
-  
- b
- a
- c
- k
- g
- r
- o
- u
- n
- d
-  
- c
- u
- r
- l
-  
- P
- O
- S
- T
-  
- r
- e
- q
- u
- e
- s
- t
-  
- w
- i
- t
- h
-  
- t
- h
- e
-  
- c
- o
- n
- v
- e
- r
- s
- a
- t
- i
- o
- n
-  
- p
- a
- y
- l
- o
- a
- d
-  
- t
- o
-  
- t
- h
- e
-  
- p
- r
- o
- d
- u
- c
- t
- i
- o
- n
-  
- s
- e
- r
- v
- e
- r
- .
- 

- 4
- .
-  
- E
- n
- s
- u
- r
- e
-  
- e
- r
- r
- o
- r
-  
- h
- a
- n
- d
- l
- i
- n
- g
-  
- s
- o
-  
- t
- h
- a
- t
-  
- l
- o
- c
- a
- l
-  
- g
- e
- n
- e
- r
- a
- t
- i
- o
- n
-  
- d
- o
- e
- s
-  
- n
- o
- t
-  
- f
- a
- i
- l
-  
- i
- f
-  
- t
- h
- e
-  
- w
- e
- b
- h
- o
- o
- k
-  
- i
- s
-  
- u
- n
- r
- e
- a
- c
- h
- a
- b
- l
- e
- .

**Definition of Done:**

*Audited against SHA:* `5a022d2b7d50146a26a014098ae372ab99a7d6d2`

---
### ⏳ T-PTG-064 · P2 · frontend · PEER_REVIEW
**Feature: Pool Ball Triangle Layout**
**Owner:** Antigravity

**Scope:**

**Definition of Done:**

*Audited against SHA:* `278031af013b6aa2ba22d638534c78bff4319f51`

---
### ⏳ T-PTG-059 · P2 · frontend · PEER_REVIEW
**Feature: Greet the user in JournalGPT**
**Owner:** Worker-Agent

**Scope:**

**Definition of Done:**

*Audited against SHA:* `148499984456a86f1d1be55b74387639df92ddce`

---
### ⏳ T-PTG-063 · P2 · frontend · PEER_REVIEW
**Feature: Mobile-Optimized Minimalist UI**
**Owner:** Worker-Agent

**Scope:**

**Definition of Done:**

*Audited against SHA:* `5583f85ad5935f425c6f3a774052f742d581e69e`

---
### ⏳ T-PTG-014 · P2 · ANY · PEER_REVIEW
**Add an admin "reply to conversation" tool, then use it to notify conversation 51 that color schemes shipped**
**Owner:** Worker-AdminReply1

**Scope:**
- BACKGROUND: conversation_id=51 (https://newmexicoptg.org/journalgpt/index.php?c=51) is the exact real member conversation from T-PTG-009's evidence -- the member typed `/featurerequest different color schemes` on 2026-08-12, and because the tag router had a bug at the time (fixed same day by T-PTG-009), it fell through to the RAG pipeline and returned a confusing non-answer instead of being triaged as a feature request. Confirmed via `debug_logs.php?conversation_id=51`: exactly one log row (id 22), `status: uncertain`, `is_grounded: 0`. Since the tag never matched, this conversation's `conversation_type` is almost certainly the default `rag`, NOT `feature_request` -- confirm this directly rather than assuming (query `SELECT conversation_type FROM conversations WHERE id = 51`). There is correspondingly no `feature_request_details` row for it (that table has a UNIQUE key on `conversation_id` and is only populated by the tagged lane). The product owner (Chip) wants this member to know their request WAS heard and has now shipped (T-PTG-012, live on main as of commit 604d1be, confirmed working by Chip in production), even though the original conversation never got properly triaged at the time.
- WHY A NEW TOOL, NOT A DB SCRIPT: Chip explicitly chose to have a small reusable admin tool built (over doing this one-off via direct SQL, and over just replying himself in the UI) so this capability exists for future announcements too, per a direct conversation with the Fleet Coordinator.
- PRECEDENT ON ACCESS CONTROL -- READ CAREFULLY BEFORE CHOOSING A ROLE CHECK: `journalgpt/admin_migrate.php:26` deliberately calls `Authorization::requireRole(null)` (any authenticated user, not `Authorization::ROLE_ADMIN`), with an explicit comment: "Any authenticated pilot user may run migrations -- the only production login is a 'member'-role account, not 'administrator'." This means gating the new tool to `ROLE_ADMIN` would make it completely unusable in production today, since no admin-role account currently exists there (confirm this directly: `SELECT id, role_id FROM users` against the local test DB structure / or note that this must be verified against production separately since local test DB seed data may differ). Match `admin_migrate.php`'s existing precedent: `Authorization::requireRole(null)` for pilot-stage access. This is a real, acknowledged tradeoff (any logged-in member could, in principle, post into any conversation) -- do not silently "fix" it by adding an admin-only gate that would lock the product owner out; if you believe the security posture needs to change, say so explicitly in the handoff as a recommendation, but do not unilaterally change the access model for this one tool while every other admin-ish tool in this codebase uses the looser pattern.
- FIX SCOPE -- the tool: a new page, e.g. `journalgpt/admin_reply.php`, gated with `Authorization::requireRole(null)` (matching admin_migrate.php), CSRF-protected (`Csrf::field()`/`Csrf::enforce()` or the same pattern used elsewhere in this codebase -- check `Csrf.php` for the established helper), presenting: a form to enter a `conversation_id` and a message body, validates the conversation exists (404/clear error if not), inserts a new row into `messages` with `role = 'assistant'` and the given `content`, and shows a success confirmation with a link to view that conversation. Word the inserted message so it reads as a note from the team, not as if the AI itself generated it as an answer -- do not have the tool auto-prepend any specific wording; let the admin type the exact message text (this keeps the tool general-purpose for future announcements, per why a Chip wanted this reusable).
- FIX SCOPE -- the one-time use: after the tool exists and is verified working, use it once to post into conversation 51 a short message from Chip/the team letting the member know their color-scheme request shipped (Chip did not dictate exact wording to the Fleet Coordinator -- write something warm, brief, and accurate: mention the 4 themes (Light/Dark/Sepia/PTG) and that the picker is available on every page. Do not overclaim or invent detail beyond what T-PTG-012 actually shipped.
- EXPLICITLY OUT OF SCOPE: do not build a general-purpose "broadcast to all conversations" or bulk-messaging feature -- this is a single-conversation reply tool. Do not add the ROLE_ADMIN gate discussed above. Do not attempt to backfill a `feature_request_details` row for conversation 51 or reclassify its `conversation_type` -- that's a separate, more invasive change not requested here; a plain reply message is sufficient for what Chip asked for.

**Definition of Done:**
- A new automated test file, journalgpt/tests/AdminReplyTest.php, following this repo's existing self-runner tests/ convention, covers: (a) an authenticated member can successfully post a reply into an existing conversation and a new `role=assistant` message row is created with the exact submitted content, (b) an unauthenticated request is rejected (matching the existing `Authorization::requireRole(null)` pattern's behavior), (c) a request with a missing/invalid CSRF token is rejected, (d) a request targeting a non-existent conversation_id returns a clear error and does not insert a row.
- journalgpt/admin_reply.php exists, is reachable by any authenticated pilot user (member or administrator role), and its form successfully posts a message into a real conversation when manually tested via the `/browse` skill (never `mcp__claude-in-chrome__*` tools directly, per this project's CLAUDE.md) against a local dev server with a test user and a test conversation.
- Using the finished tool (not a raw SQL script), exactly one new message is posted into production conversation_id=51 with role=assistant, notifying the member that the color-scheme feature they requested has shipped. Confirm this by querying the message afterward (or via debug_logs.php-equivalent visibility if applicable) and record the exact message content and its new message id in the handoff.
- php -l passes on journalgpt/admin_reply.php.
- The existing test suite still passes in full -- journalgpt/tests/AskEndpointTest.php, journalgpt/tests/UsagePolicyTest.php, and journalgpt/tests/JournalAnswerServiceTest.php all run clean (0 failures).

*Audited against SHA:* `aba832b031b0fd796459d2f75aa8dc4099f14d1c`

---
### ⏳ T-PTG-055 · P2 · ANY · PEER_REVIEW
**Coverage Atlas Phase 2b: LLM tour/thread draft-proposal CLI (machine proposes, curator disposes)**
**Owner:** Claude-Fable-Session

**Scope:**
- Spec: section 4 of docs/superpowers/specs/2026-08-17-coverage-atlas-design.md. CLI (cli/propose_tours.php) that drafts candidate tours/threads as status=draft rows for curator review in admin_tours.php. Inputs: article_index summary_keywords + core_skills + issue chronology (+ article_index_topics tags where present). One LLM pass per proposal via OpenAIClient (mock-mode testable, same as QuizGenerator), cost-capped: --limit N proposals per run, estimated cost logged, UsageLedger conventions respected.
- Proposal shapes: (a) tour -- 5-8 articles sharing a theme with a one-line blurb and per-stop connective notes; (b) thread -- chronological sequence on one narrow question spanning 10+ years (the spec's "watch the craft argue with itself" shape; e.g. humidity-control advice over time). The model must only reference real article_index ids fed to it -- reject any proposal citing an id not in the candidate set (mirror QuizGenerator's grounding-enforcement discipline: discard, never repair).
- NEVER auto-publish: CLI writes drafts only. Duplicate-guard: skip proposing a tour whose title case-insensitively matches an existing tour.

**Definition of Done:**
- With a mocked OpenAIClient response, the CLI writes a valid draft tour with ordered stops and connective notes; a response citing a fabricated article id is discarded with a logged warning and writes nothing.
- Drafts appear in admin_tours.php for curation; nothing member-visible changes.
- Duplicate-title guard proven by test.
- Golden hammer suite passes with zero regressions.

---
### ⏳ T-PTG-054 · P2 · ANY · PEER_REVIEW
**Coverage Atlas Phase 2a: tours/threads schema + curator admin page**
**Owner:** Antigravity

**Scope:**
- Spec: section 4 of docs/superpowers/specs/2026-08-17-coverage-atlas-design.md. New migration (020): tours (id, title, kind ENUM(tour, thread), blurb, status ENUM(draft, published), created_by FK users, timestamps) and tour_articles (tour_id FK CASCADE, article_index_id FK, sort_order, connective_note TEXT; unique (tour_id, article_index_id)). Additive-only, mirrors 018's conventions.
- Curator admin page (admin_tours.php, following admin_article_index_matrix.php's auth + no-framework pattern): list tours with status; create/edit a tour (title, kind, blurb); add/remove/reorder articles by searching the article_index (title/ author/issue search, same client-side approach as the matrix page); edit each stop's connective_note; draft/publish toggle. Only status=published tours are ever visible to member-facing pages (enforced in queries, not just UI).
- Write endpoints follow the pure-handler + LIBRARY_ONLY + CSRF pattern (api/toggle_article_index_topic.php is the closest template).

**Definition of Done:**
- Migration 020 applies cleanly via cli/migrate.php on the local test DB.
- Handler tests prove - create tour, add three articles with order, reorder, edit connective_note, publish; CSRF rejection; draft tours excluded by the member-visibility query helper.
- Curator page browser-verified locally (create a 3-stop tour end to end).
- Golden hammer suite passes with zero regressions; php -l clean.

*Audited against SHA:* `b11317aaf5b0e0b8903c459813a1907b2f9a7ab2`

---
