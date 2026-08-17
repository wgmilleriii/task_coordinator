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
    T-PTG-045["T-PTG-045<br/>Phase 4: Member Knowledge Profiles"]
    T-PTG-004["T-PTG-004<br/>Audit citation metadata accuracy: volume/issue-number mismatches between issue_label and title"]:::review
    T-PTG-053["T-PTG-053<br/>Coverage Atlas Phase 1b: coverage radar dashboard + empty-wedge nudge"]
    T-PTG-052 --> T-PTG-053
    T-PTG-049["T-PTG-049<br/>Transcribe Airtable ground-truth screenshots (27 issues, Nov-2023 to Jan-2026) and cross-check against T-PTG-047 extraction output"]
    T-PTG-047 --> T-PTG-049
    T-PTG-024["T-PTG-024<br/>JournalGPT v3 Phase 4: ClaimValidator (claim-level citation verification)"]
    T-PTG-023 --> T-PTG-024
    T-PTG-025["T-PTG-025<br/>JournalGPT v3 Phase 5: IP hardening review (public sharing, bulk-extraction, source authorization)"]
    T-PTG-024 --> T-PTG-025
    T-PTG-048["T-PTG-048<br/>Article/editorial completeness QC pass beyond page-coverage checking, ground-truthed against PTJ-2020-02's own table of contents"]:::review
    T-PTG-047 --> T-PTG-048
    T-PTG-052["T-PTG-052<br/>Coverage Atlas Phase 1a: member_article_activity log + signal hooks + issue-to-article resolver"]
    T-PTG-051 --> T-PTG-052
    T-PTG-005["T-PTG-005<br/>Voicing-technique continuity + citation-format test matrix (all preset x tier combos)"]:::review
    T-PTG-044["T-PTG-044<br/>Phase 3: Citation Analytics & Logging"]
    T-PTG-022["T-PTG-022<br/>JournalGPT v3 Phase 2b: EvidenceRanker"]
    T-PTG-020 --> T-PTG-022
    T-PTG-043["T-PTG-043<br/>Phase 2: RAG Pipeline Optimization"]
    T-PTG-014["T-PTG-014<br/>Add an admin 'reply to conversation' tool, then use it to notify conversation 51 that color schemes shipped"]:::review
    T-PTG-002["T-PTG-002<br/>Stop citing every retrieved chunk — only cite what the model actually referenced"]
    T-PTG-001 --> T-PTG-002
    T-PTG-055["T-PTG-055<br/>Coverage Atlas Phase 2b: LLM tour/thread draft-proposal CLI (machine proposes, curator disposes)"]
    T-PTG-054 --> T-PTG-055
    T-INTY-017["T-INTY-017<br/>Piano Dossier Data Entry Interface (Modern EAV)"]:::review
    T-PTG-054["T-PTG-054<br/>Coverage Atlas Phase 2a: tours/threads schema + curator admin page"]
    T-PTG-051 --> T-PTG-054
    T-PTG-003["T-PTG-003<br/>Lock in citation-numbering fix with a real-shape regression fixture"]
    T-PTG-001 --> T-PTG-003
    T-PTG-002 --> T-PTG-003
    T-PTG-042["T-PTG-042<br/>Phase 1: Metadata Index"]
    T-PTG-023["T-PTG-023<br/>JournalGPT v3 Phase 3: AnswerSynthesizer + Journal-vs-explanation distinction"]
    T-PTG-022 --> T-PTG-023
    T-PTG-019["T-PTG-019<br/>JournalGPT v3 Phase 1b: ResearchPlanner + contextual follow-up understanding"]:::done
    T-PTG-018 --> T-PTG-019
    T-INTY-019["T-INTY-019<br/>'Open in Gazelle' deep-link button on the Piano Dossier page"]
    T-INTY-018 --> T-INTY-019
    T-PTG-020["T-PTG-020<br/>JournalGPT v3 Phase 2: intelligent retrieval (EvidenceRetriever, multi-query search, dedup)"]
    T-PTG-019 --> T-PTG-020
    T-PTG-016["T-PTG-016<br/>SECURITY: admin_reply.php lets any logged-in member post fake assistant messages into ANY member's conversation (IDOR)"]:::review
    T-PTG-017["T-PTG-017<br/>Implement member feature request (conversation 53): better mobile screen real estate management for the engine-controls-bar"]:::review
    T-PTG-001["T-PTG-001<br/>Fix footnote list numbering to match inline citation markers"]:::review
    T-PTG-056["T-PTG-056<br/>Coverage Atlas Phase 2c: member-facing tour pages with closing quiz + radar integration"]
    T-PTG-054 --> T-PTG-056
    T-PTG-052 --> T-PTG-056
    T-MIN-008["T-MIN-008<br/>Pin down Bernardi's verzicola boundary from the 1790 rules directly"]
    T-PTG-021["T-PTG-021<br/>Fix stale JournalChatRenderTest assertion breaking the golden hammer suite (pre-existing, not caused by today's tasks)"]
    T-PTG-051["T-PTG-051<br/>Coverage Atlas foundation: run migration 018 + article-index import on the shared DB and verify the tagging matrix live"]
    T-PTG-047["T-PTG-047<br/>Build and test page-range coverage-validation + repair pass for per-article extraction spike"]:::done
    T-PTG-026["T-PTG-026<br/>JournalGPT v3 Phase 6: replay benchmark and tune (final evaluation pass)"]
    T-PTG-025 --> T-PTG-026
    T-PTG-015 --> T-PTG-026
    T-PTG-046["T-PTG-046<br/>Fix broken citation links in history viewer for article_id=0"]:::done
    T-PTG-050["T-PTG-050<br/>CSV-driven per-article extraction pilot (5-8 issues) using human-curated Airtable ground truth instead of LLM boundary inference"]:::done
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

### 📋 T-MIN-008 · P2 · ANY · OPEN
**Pin down Bernardi's verzicola boundary from the 1790 rules directly**
**Owner:** None

**Scope:**
- Open the RULE-1790 (Bernardi) source directly and transcribe every verzicola combination example, replacing the Justice pilot's hedge ('I-V and beginning around XXVIII', pilot line 92) with an exact list.
- Thirteen committed studies currently lean on that hedge; the zodiac batch flags it as acutely open at XXVII (one numeral below) and XXVIII (the numeral the hedge names), and the element batch left 'whether XX-XXIII can form a verzicola' as a standing open question in all four files.
- Record whether the examples are exhaustive or exemplary in Bernardi's own text; do not convert examples into rules - the deliverable is the transcription plus locators (chapter and printed page), not an interpretation.
- If the boundary resolves, list the follow-up amendments needed (zodiac files XXVII/XXVIII sections 2 and 4, element files' open questions, Justice pilot cross-references) as a reconciliation queue; apply them only if the audit scopes that in.

**Definition of Done:**
- A sourced note in research/02-source-audit/ or research/pilots/ transcribes the verzicola examples with exact locators and states what the record can and cannot support.
- The reconciliation queue of affected files is listed with per-file line references.
- The hedge is superseded only by direct transcription, never by memory.

---

## Repo: `newmexicoptg.org`

### ⏳ T-PTG-016 · P0 · ANY · HUMAN_REVIEW
**SECURITY: admin_reply.php lets any logged-in member post fake assistant messages into ANY member's conversation (IDOR)**
**Owner:** Worker-SecFix1

**Scope:**
- FINDING SOURCE: an automated post-commit security review flagged `journalgpt/admin_reply.php` (shipped by T-PTG-014, merged to `main` at commit e2edf34, already pushed -- confirm whether it has auto-deployed to production, per this repo's known git-push-auto-deploy behavior) as HIGH severity: Authorization (IDOR) -- cross-user assistant-message injection.
- THE ACTUAL BUG: `admin_reply.php` calls `Authorization::requireRole(null)` (any authenticated pilot user, member or administrator) and then looks up the target conversation with a plain `SELECT id FROM conversations WHERE id = :id` -- NOT scoped to the current user. This means ANY logged-in member can POST to this page with an arbitrary `conversation_id` and have a fake `role=assistant` message inserted into ANY OTHER member's private conversation, impersonating the AI assistant (or effectively PTG staff) in a conversation they have no relationship to.
- WHY THE FLEET COORDINATOR'S OWN GUIDANCE ON T-PTG-014 WAS WRONG AND MUST NOT BE REPEATED: T-PTG-014's scope explicitly told the Worker to match `admin_migrate.php`'s precedent of `Authorization::requireRole(null)`, reasoning that no administrator-role account exists in production. That reasoning does not transfer to this tool. `admin_migrate.php` lets any member trigger idempotent, blast-radius-limited schema migrations against the whole app -- annoying if misused, but not a content-injection or impersonation vector against a SPECIFIC OTHER MEMBER. `admin_reply.php` lets one member inject fake "assistant" content directly into another specific member's private conversation, which is a materially different and more dangerous capability (social engineering / trust manipulation against a real person, not just operational friction). Do not copy the `requireRole(null)` pattern here just because another admin-ish page in this codebase uses it -- evaluate each tool's actual blast radius on its own.
- REAL-WORLD EXPOSURE CHECK (Scout verified via `debug_logs.php`): every logged production interaction to date shows `user_id: 1` -- there is currently no second real member account visible in production activity, so this has almost certainly not been exploited against a real second party yet. This is P0 because it must be fixed BEFORE any second member is onboarded, not because there is known active exploitation today -- do not downgrade priority on the assumption it is already fine.
- FIX SCOPE, PART 1 (code): change `journalgpt/admin_reply.php` to require the real administrator role -- `Authorization::requireRole(Authorization::ROLE_ADMIN)` -- instead of `requireRole(null)`. Do NOT take the "scope to own conversations only" alternative (`WHERE id = :id AND user_id = :uid`) -- that would defeat the tool's actual purpose, which is specifically to let an admin (Chip) post into OTHER members' conversations for announcements (this is exactly how T-PTG-014 was used: Chip needed to reply into member conversation 51, which is not his own conversation).
- FIX SCOPE, PART 2 (data): since no `administrator`-role account exists in production today (confirmed during T-PTG-014's scoping), the ROLE_ADMIN gate alone would lock Chip out of his own tool unless his account is promoted. Add a small, idempotent CLI script (matching the existing convention in `journalgpt/cli/*.php`, e.g. `journalgpt/cli/promote_admin.php`) that takes an email argument and sets that user's `role_id` to the `administrator` role's id (looked up by name, not a hardcoded id, in case seed order ever changes). The Worker cannot run this against production directly (no production DB credentials are available in this environment, confirmed repeatedly this session) -- the DoD requires handing Chip the exact command to run himself against production, not attempting to run it there.
- REGRESSION CHECK: `journalgpt/tests/AdminReplyTest.php` (added by T-PTG-014) currently asserts that an authenticated MEMBER can successfully post a reply -- that assertion is now WRONG per this fix and must be updated to assert the opposite (a plain member is rejected with 403, only an administrator-role user succeeds). Do not leave the old test passing against the old, insecure behavior -- update it to actually test the fixed access control, not just keep tests green by coincidence.
- EXPLICITLY OUT OF SCOPE: do not touch `admin_migrate.php`'s own `requireRole(null)` -- that tool's tradeoff is a separate judgment call already made and not part of this security finding. Do not build a full RBAC system or per-conversation ACLs -- a single ROLE_ADMIN gate is sufficient and matches this codebase's existing two-role model (member/administrator).

**Definition of Done:**
- journalgpt/admin_reply.php requires Authorization::ROLE_ADMIN, not requireRole(null) -- a plain member account gets a 403, matching Authorization::denyAccess()'s existing behavior.
- journalgpt/tests/AdminReplyTest.php is updated so its test assertions match the new, correct access control (member rejected, administrator succeeds) -- not just left passing by accident.
- A new journalgpt/cli/promote_admin.php script exists, idempotent, looks up the administrator role id by name (not hardcoded), takes an email argument, and the handoff includes the EXACT command for Chip to run against production himself (since the Worker cannot reach production DB credentials from this environment).
- The handoff explicitly states this fix has NOT yet been applied to production role data (only the code gate ships automatically via merge) -- Chip must run the promote_admin.php command himself before he can use admin_reply.php again post-fix, and the handoff must say this plainly so it isn't missed.
- php -l passes on journalgpt/admin_reply.php and journalgpt/cli/promote_admin.php.
- The existing test suite still passes in full -- journalgpt/tests/AskEndpointTest.php, journalgpt/tests/UsagePolicyTest.php, and journalgpt/tests/JournalAnswerServiceTest.php all run clean (0 failures).

*Audited against SHA:* `e2edf343520a3418114da8997f31ae5dc3f245ec`

---
### ⏳ T-PTG-001 · P0 · ANY · HUMAN_REVIEW
**Fix footnote list numbering to match inline citation markers**
**Owner:** Claude-Worker

**Scope:**
- journalgpt/lib/JournalAnswerService.php — the ask() method, specifically the block converting raw OpenAI annotations (the file-citation tag OpenAI wraps in special bracket characters) into inline [1], [2], ... markers (the $uniqueTags map), and the separate block below it that appends a Footnotes list by enumerating $citationsOutput 1..N.
- Root cause confirmed live in production: a 'Golden Hammer Award recipients' answer had only 4 unique inline markers ([1]-[4]) in the model's prose, but the appended footnote block listed 24 numbered entries — footnote numbers 1-24 do not correspond to inline markers 1-4 at all. The two numbering systems are built independently: inline numbers come from the order unique annotation tags first appear in the raw answer text; footnote numbers come from the order $parsedCitations were resolved (chunk-derived citations from every retrieved chunk, in retrieval order, plus Tier-4 corpus-scan fallback results appended after). Nothing ties a footnote's number or content to which inline marker it is supposed to back.
- Fix must make the footnote list contain exactly the citations that correspond to inline markers, numbered identically to those markers, in the same first-appearance order — not a dump of every retrieved-but-possibly-uncited chunk.

**Definition of Done:**
- Footnote count in the rendered answer equals the count of distinct inline [n] markers actually present in the cleaned answer text (never more, never fewer).
- Footnote [n] links to the same source the model's inline [n] marker was standing in for (i.e. the annotation-to-citation mapping is preserved through the pipeline, not re-derived independently for the footnote block).
- A citation that was retrieved (present in retrieved_chunks or found by the Tier-4 corpus scan) but never actually referenced by an inline marker in the model's prose does not appear as a numbered footnote.
- New regression test added to journalgpt/tests/JournalAnswerServiceTest.php reproducing this shape: a StubOpenAIClient answer with only 4 unique annotations in the text but retrieved_chunks/corpus-scan data that would independently resolve to 15+ citations. Assert count(inline markers) === count(footnotes).
- Existing test suite (tests/JournalAnswerServiceTest.php) still passes in full, including the existing hedged-answer/citation-always-works regression tests.

*Audited against SHA:* `9e74d39c82a5980f488695fb4e4e5e1dd46bdb54`

---
### 📋 T-PTG-002 · P1 · ANY · AUDITED
**Stop citing every retrieved chunk — only cite what the model actually referenced**
**Owner:** None

**Scope:**
- journalgpt/lib/JournalAnswerService.php — resolveCitationsFromChunks() (turns EVERY entry in $retrievedChunks into a citation, one per chunk, regardless of whether the model's answer actually drew on it) and fallbackExtractCitationsFromAnswer() (Tier-4 corpus-wide phrase scan, capped at MAX_FALLBACK_CITATIONS = 6 per call but still additive on top of chunk citations).
- This is the upstream cause behind T-PTG-001's symptom: File Search / Assistants retrieval commonly returns 10-20+ chunks touching many issues/pages of the Journal for a broad query (e.g. 'Golden Hammer Award recipients' spans years of issues). Today every one of those chunks becomes its own citation entry, deduped only by (article_uid, page) — never checked against whether the model's prose contains an annotation actually pointing at that chunk.
- T-PTG-001 fixes the numbering/footnote-list symptom (footnotes must match inline markers 1:1). This task fixes the underlying data problem so citation volume itself stays sane even before T-PTG-001's filtering: adjacent-page citations to the same article should collapse into one entry with a page range rather than N separate entries, and the Tier-4 answer-text fallback should only ever supplement — never dominate — a citation list.

**Definition of Done:**
- resolveCitationsFromChunks (or its caller) collapses consecutive/adjacent pages within the same article_uid into a single citation entry with a page range (e.g. pp. 21-23) instead of 3 separate entries — verify against the real example where article_id=145 pages 23/24/25 all cited separately in one answer.
- Tier-4 fallbackExtractCitationsFromAnswer results are clearly and structurally distinguished from directly-retrieved/annotated citations (e.g. a source: 'fallback_scan' vs source: 'retrieval' field on each citation record) so downstream consumers (including T-PTG-001's inline-matching logic) can tell which citations the model actually pointed to vs. which were discovered independently by scanning corpus text for matching phrases.
- No regression in existing grounded-answer tests — a genuinely single-source answer still returns exactly one citation.
- New regression test added to journalgpt/tests/JournalAnswerServiceTest.php using a StubOpenAIClient with 10+ retrieved_chunks across multiple issues, asserting page-range collapsing and that fallback-scan citations are tagged distinctly from retrieval citations.

*Audited against SHA:* `9e74d39c82a5980f488695fb4e4e5e1dd46bdb54`

---
### 📋 T-PTG-003 · P1 · ANY · AUDITED
**Lock in citation-numbering fix with a real-shape regression fixture**
**Owner:** None

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
### 📋 T-PTG-045 · P1 · ANY · CANCELLED
**Phase 4: Member Knowledge Profiles**
**Owner:** Worker-Phase4

**Scope:**

**Definition of Done:**
- -
-  
- "
- M
- y
-  
- K
- n
- o
- w
- l
- e
- d
- g
- e
-  
- P
- r
- o
- f
- i
- l
- e
- "
-  
- p
- a
- g
- e
-  
- i
- s
-  
- a
- c
- c
- e
- s
- s
- i
- b
- l
- e
- .
- 

- -
-  
- M
- e
- t
- r
- i
- c
- s
-  
- c
- o
- m
- b
- i
- n
- e
-  
- l
- o
- g
- s
-  
- a
- n
- d
-  
- m
- e
- t
- a
- d
- a
- t
- a
-  
- t
- a
- g
- s
- .
- 

- -
-  
- Q
- u
- i
- z
-  
- b
- u
- t
- t
- o
- n
-  
- i
- n
- t
- e
- g
- r
- a
- t
- e
- s
-  
- w
- i
- t
- h
-  
- l
- e
- a
- s
- t
- -
- k
- n
- o
- w
- n
-  
- t
- a
- g
- s
- .
- 

- -
-  
- T
- e
- s
- t
- s
-  
- p
- a
- s
- s
-  
- i
- n
-  
- `
- p
- h
- p
-  
- t
- e
- s
- t
- s
- /
- s
- e
- c
- u
- r
- i
- t
- y
- _
- a
- n
- d
- _
- e
- v
- a
- l
- _
- s
- u
- i
- t
- e
- .
- p
- h
- p
- `
- .
- 


*Audited against SHA:* `32132e5bb4912764677e47cdd11bd39de9621698`

---
### 📋 T-PTG-049 · P1 · ANY · CANCELLED
**Transcribe Airtable ground-truth screenshots (27 issues, Nov-2023 to Jan-2026) and cross-check against T-PTG-047 extraction output**
**Owner:** Worker-AirtableGroundTruth1

**Scope:**
- Background, read first, in full: docs/superpowers/specs/2026-08-14-per-article-extraction-spike-findings.md, docs/30-Engineering/2026-08-14-page-coverage-validation-repair-pass.md (T-PTG-047, DONE, merged into test), and docs/30-Engineering/2026-08-14-article-editorial-completeness-qc-pass.md (T-PTG-048, currently in PEER_REVIEW on branch test-T-PTG-048 / worktree ../newmexicoptg.org-T-PTG-048 -- confirmed NOT yet merged into test as of this task's creation via `git merge-base --is-ancestor test-T-PTG-048 test`, which fails; re-check merge status at task start since it may land before this task is claimed). T-PTG-048 found that article/editorial completeness cannot be trusted from raw extraction output even with zero page-coverage gaps/overlaps -- short department columns get silently dropped or absorbed into neighboring pieces, and one article was found truncated to 1 of its 6 real pages despite a correct title/author/start_page. That finding was derived by hand from a single issue's own table of contents (PTJ-2020-02). This task's job is to widen that kind of ground-truth check using a new, independently-sourced dataset instead of hand-deriving TOCs one issue at a time.
- New resource: the user maintains a human-curated Airtable base (public share view, not part of this repo) cataloguing the Piano Technicians Journal back to 1979, one record per article, with fields Page (printed page number), Article Title, Author(s), Summary/Keywords, Core skills tags, and a link to the parent Issue (Month-Year format, e.g. "Jan-26"). The user took 10 screenshots of this Airtable grid view and saved them directly into journalgpt/pdfs/ (they are a screenshot dump sitting alongside the PDFs, not corpus data): journalgpt/pdfs/Screenshot 2026-08-14 at 6.19.33 PM.png, ...6.19.45 PM.png, ...6.19.54 PM.png, ...6.20.06 PM.png, ...6.20.19 PM.png, ...6.20.32 PM.png, ...6.20.42 PM.png, ...6.20.50 PM.png, ...6.20.59 PM.png, ...6.21.07 PM.png. These 10 screenshots are consecutive scroll captures covering Airtable record numbers approximately 3918 through 4126 (some overlap expected at the boundary of each screenshot), spanning issues Nov-2023 through Jan-2026 -- confirmed this range covers 27 issues (PTJ-2023-11 through PTJ-2026-01), all of which are present in journalgpt/corpus/manifest.json and all of which already have a PDF in journalgpt/pdfs/. This span includes 3 of the original 8 T-PTG-047 spike-sample issues -- PTJ-2024-01, PTJ-2025-03, PTJ-2025-10 -- which already have extraction output at journalgpt/spikes/T-PTG-047/output/PTJ-2024-01.result.json, PTJ-2025-03.result.json, and PTJ-2025-10.result.json (confirmed present on branch test, already merged). Page numbers in this Airtable data have already been visually spot-checked by the requester against recurring department page conventions independently found in PTJ-2020-02's own TOC (TT&T ~p.7-8, Q&A Roundtable ~p.10-12, Tuner's Life ~p.36, Foundation Focus ~p.30-31) -- a strong signal this data is reliable, though not yet proven at scale.
- Known limitation to respect: long article titles are visually truncated with an ellipsis in the Airtable grid view screenshots (fixed column width), so some transcribed titles will be partial. Short titles (TT&T, Tuner's Life: X, Q&A Roundtable: X, Foundation Focus: X) are mostly complete. Page numbers, issue month, and author are reliably legible throughout the screenshots.
- In scope, required, step 1 (transcription): read all 10 screenshot PNGs directly with the Read tool (it supports images) -- do not guess, infer, or hallucinate any field. Transcribe every row visible into a structured ground-truth JSON file, one record per row, with fields: airtable_number, issue (convert the screenshot's "Mon-YY" issue format to this repo's PTJ-YYYY-MM convention, e.g. "Jan-26" -> "PTJ-2026-01"), page, title, title_truncated (boolean -- true if the screenshot itself shows the title cut off with an ellipsis; never guess the missing portion, just flag it), author(s), and core_skills. De-duplicate rows that appear in more than one screenshot (adjacent screenshots overlap at their scroll boundary) by airtable_number. Save this file under a new directory journalgpt/spikes/T-PTG-049/ (NOT under journalgpt/corpus/ -- this is external reference data, not corpus content) as ground_truth_2023-11_2026-01.json or an equivalently clear name.
- In scope, required, step 2 (coverage check): using the transcribed ground truth, report which of the 27 issues in range (PTJ-2023-11 through PTJ-2026-01) received at least one ground-truth row, and explicitly flag any issue in that range with zero rows as a possible screenshot gap or scroll-boundary miss -- do not silently assume full coverage just because the record-number range nominally spans it.
- In scope, required, step 3 (cross-check against existing extraction): for the 3 issues where both this task's ground truth and T-PTG-047's extraction output already exist -- PTJ-2024-01, PTJ-2025-03, PTJ-2025-10 -- diff the Airtable ground-truth rows for each issue against journalgpt/spikes/T-PTG-047/output/<issue>.result.json. If T-PTG-048 is merged/available by the time this task is worked, its PTJ-2020-02-specific diff methodology under journalgpt/spikes/T-PTG-048/ should be reused or extended for this comparison rather than reimplemented from scratch; if T-PTG-048 is still unmerged, reference its worktree (../newmexicoptg.org-T-PTG-048) directly the same way T-PTG-048 itself had to reference T-PTG-047's still-unmerged branch. Report hit / miss / merged per ground-truth row, in the same explicit per-row table style T-PTG-048 used for its PTJ-2020-02 diff (not just an aggregate count).
- Explicitly NOT required: a full QC content-read pass across all 27 issues -- T-PTG-048 already established that raw page-coverage checking is insufficient and that finding does not need to be re-proven here. This task is about breadth (27 issues via a new, independently-sourced ground truth) not depth (re-reading every article's full text). If the worker has time or interest to spot-check 1-2 completeness reads against this new ground truth (similar in spirit to T-PTG-048's source-text read, but not the primary deliverable), that is a bonus, not a requirement.
- In scope, required, step 4 (report): a written report under docs/30-Engineering/ (Dewey Decimal protocol per task_coordinator/README.md), with frontmatter matching task_coordinator/schemas/doc_frontmatter.schema.json, presenting: the coverage check from step 2 (27-issue table, flagging any zero-row issues), the 3-issue cross-check diff tables from step 3 (hit/miss/merged per row), and a clear recommendation on whether this Airtable data should become the primary ground-truth source for a future piece-level schema, versus continuing to rely on LLM extraction plus repair heuristics (T-PTG-047's coverage.py / toc_offset_repair.py / boundary_trim.py / continued_scan.py approach).
- Out of scope, do not do: no articles/pieces schema design or database migration; no touching test/prod in any way (no migration, no backfill, no admin-page changes -- test.newmexicoptg.org shares prod's database, confirm before any migration/backfill/data-write on test, not just prod); no production code changes (journalgpt/corpus/extract_corpus.py or any other shipped pipeline code); no full-corpus pass -- only the 27 issues covered by the 10 screenshots, plus the 3-issue cross-check; no scraping or live-browsing the actual Airtable site -- the 10 screenshots already saved in journalgpt/pdfs/ are the only data source for this task (the user may provide better/direct Airtable access later, which would be a separate future task, not this one).

**Definition of Done:**
- All 10 screenshot PNGs in journalgpt/pdfs/ (Screenshot 2026-08-14 at 6.19.33 PM.png through ...6.21.07 PM.png) were read directly with the Read tool and transcribed -- not inferred or hallucinated -- into a single structured ground-truth JSON file under a new journalgpt/spikes/T-PTG-049/ directory, with fields airtable_number, issue (in PTJ-YYYY-MM form), page, title, title_truncated, author(s), and core_skills per row, de-duplicated across overlapping screenshots by airtable_number.
- The report explicitly states, for every one of the 27 issues PTJ-2023-11 through PTJ-2026-01, whether it received at least one ground-truth row, and calls out by name any issue with zero rows as a possible screenshot gap rather than silently omitting it.
- For each of PTJ-2024-01, PTJ-2025-03, and PTJ-2025-10, the report contains a per-row diff table (ground-truth row vs. T-PTG-047 extraction output) explicitly marking each row hit, miss, or merged, in the same style as T-PTG-048's PTJ-2020-02 diff table -- not just an aggregate hit-rate number.
- A written report exists under docs/30-Engineering/ with frontmatter matching task_coordinator/schemas/doc_frontmatter.schema.json, and ends with a clear, explicit recommendation on whether the Airtable data should become the primary ground-truth source for a future piece-level schema versus continuing to rely on LLM extraction plus repair heuristics.
- No changes were made to journalgpt/corpus/extract_corpus.py or any other production code path, no database migration was created or run, and no test/prod endpoint was touched -- all work is local files under journalgpt/spikes/T-PTG-049/ and the docs/ report.

*Audited against SHA:* `a527e9dc2cd6adf70f2df2cb756ba4b7cc705c87`

---
### 📋 T-PTG-044 · P1 · ANY · CANCELLED
**Phase 3: Citation Analytics & Logging**
**Owner:** Worker-Phase3

**Scope:**

**Definition of Done:**
- -
-  
- T
- a
- b
- l
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
- _
- c
- i
- t
- a
- t
- i
- o
- n
- _
- l
- o
- g
- s
- `
-  
- i
- s
-  
- c
- r
- e
- a
- t
- e
- d
- .
- 

- -
-  
- B
- a
- c
- k
- e
- n
- d
-  
- w
- r
- i
- t
- e
- s
-  
- r
- o
- w
- s
-  
- o
- n
-  
- a
- n
- s
- w
- e
- r
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
- .
- 

- -
-  
- A
- d
- m
- i
- n
-  
- d
- a
- s
- h
- b
- o
- a
- r
- d
-  
- s
- h
- o
- w
- s
-  
- a
- n
- a
- l
- y
- t
- i
- c
- s
- .
- 

- -
-  
- T
- e
- s
- t
- s
-  
- p
- a
- s
- s
-  
- i
- n
-  
- `
- p
- h
- p
-  
- t
- e
- s
- t
- s
- /
- s
- e
- c
- u
- r
- i
- t
- y
- _
- a
- n
- d
- _
- e
- v
- a
- l
- _
- s
- u
- i
- t
- e
- .
- p
- h
- p
- `
- .
- 


*Audited against SHA:* `32132e5bb4912764677e47cdd11bd39de9621698`

---
### 📋 T-PTG-043 · P1 · ANY · CANCELLED
**Phase 2: RAG Pipeline Optimization**
**Owner:** Worker-Phase2

**Scope:**

**Definition of Done:**
- -
-  
- `
- J
- o
- u
- r
- n
- a
- l
- A
- n
- s
- w
- e
- r
- S
- e
- r
- v
- i
- c
- e
- `
-  
- q
- u
- e
- r
- i
- e
- s
-  
- t
- h
- e
-  
- i
- n
- d
- e
- x
-  
- f
- i
- r
- s
- t
- .
- 

- -
-  
- P
- r
- o
- m
- p
- t
-  
- s
- t
- r
- u
- c
- t
- u
- r
- e
-  
- i
- s
-  
- s
- i
- m
- p
- l
- i
- f
- i
- e
- d
-  
- f
- o
- r
-  
- c
- h
- u
- n
- k
- s
- .
- 

- -
-  
- C
- i
- t
- a
- t
- i
- o
- n
-  
- b
- a
- d
- g
- e
- s
-  
- a
- r
- e
-  
- g
- e
- n
- e
- r
- a
- t
- e
- d
-  
- n
- a
- t
- i
- v
- e
- l
- y
-  
- b
- y
-  
- P
- H
- P
-  
- b
- a
- c
- k
- e
- n
- d
-  
- u
- s
- i
- n
- g
-  
- l
- o
- o
- k
- u
- p
- .
- 

- -
-  
- T
- e
- s
- t
- s
-  
- p
- a
- s
- s
-  
- i
- n
-  
- `
- p
- h
- p
-  
- t
- e
- s
- t
- s
- /
- s
- e
- c
- u
- r
- i
- t
- y
- _
- a
- n
- d
- _
- e
- v
- a
- l
- _
- s
- u
- i
- t
- e
- .
- p
- h
- p
- `
- .
- 


*Audited against SHA:* `32132e5bb4912764677e47cdd11bd39de9621698`

---
### 📋 T-PTG-042 · P1 · ANY · CANCELLED
**Phase 1: Metadata Index**
**Owner:** None

**Scope:**

**Definition of Done:**
- -
-  
- D
- a
- t
- a
- b
- a
- s
- e
-  
- t
- a
- b
- l
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
- _
- a
- r
- t
- i
- c
- l
- e
- s
- `
-  
- o
- r
-  
- m
- e
- t
- a
- d
- a
- t
- a
-  
- J
- S
- O
- N
-  
- i
- s
-  
- c
- r
- e
- a
- t
- e
- d
-  
- a
- n
- d
-  
- p
- o
- p
- u
- l
- a
- t
- e
- d
- .
- 

- -
-  
- C
- L
- I
-  
- s
- c
- r
- i
- p
- t
-  
- i
- s
-  
- w
- o
- r
- k
- i
- n
- g
-  
- t
- o
-  
- p
- a
- r
- s
- e
-  
- a
- n
- d
-  
- b
- u
- i
- l
- d
-  
- t
- h
- e
-  
- i
- n
- d
- e
- x
- .
- 

- -
-  
- T
- e
- s
- t
- s
-  
- p
- a
- s
- s
-  
- i
- n
-  
- `
- p
- h
- p
-  
- t
- e
- s
- t
- s
- /
- s
- e
- c
- u
- r
- i
- t
- y
- _
- a
- n
- d
- _
- e
- v
- a
- l
- _
- s
- u
- i
- t
- e
- .
- p
- h
- p
- `
- .
- 


*Audited against SHA:* `32132e5bb4912764677e47cdd11bd39de9621698`

---
### ✅ T-PTG-047 · P1 · ANY · DONE
**Build and test page-range coverage-validation + repair pass for per-article extraction spike**
**Owner:** Worker-ExtractionRepair1

**Scope:**
- Background: docs/superpowers/specs/2026-08-14-per-article-extraction-spike-findings.md (read in full, including the Addendum) is the entire basis for this task. An LLM (gpt-4o-mini) spike broke 8 sampled issues into per-piece title/author/type/page-range breakdowns. Title/author/type extraction was reliable. Page-range boundaries were NOT: every one of the 8 sampled issues had missing and/or overlapping page coverage. Two confirmed root causes plus one pipeline quirk are documented in the findings doc's "What didn't" section and Addendum. This task builds the validation + repair pass the findings doc's Recommendation section calls for, and re-tests it against the same 8 issues to see if it actually closes the gaps.

- In scope, required: implement a programmatic page-coverage checker that, for a given issue's LLM-produced pieces list, verifies every page from 1 to the issue's last [[page:N]] anchor belongs to exactly one piece, and reports gaps (unclaimed pages) and overlaps (pages claimed by 2+ pieces) per issue — same methodology the spike used (see the findings doc's gap table for the exact per-issue baseline numbers to compare against).

- In scope, required: implement the TOC-anchor-offset repair idea from the Addendum's proposal #1. Extract the printed page number from page-footer text on each [[page:N]] anchor page (footer text is already present in this corpus, e.g. "April 2020 / Piano Technicians Journal 1" per finding #3), diff it against the real anchor number to derive the issue's front-matter offset, and use that to detect/correct pieces where the model used a printed TOC page number instead of the real anchor number (finding #2 in the spike doc is the concrete reproduction case, PTJ-2025-10, off by 13 pages). This MUST reuse or explicitly extend the existing `articles.pdf_page_offset` mechanism (journalgpt/migrations/002_pdf_page_offset.sql, default offset 2) rather than inventing a second, parallel offset concept — read that migration file and journalgpt/lib usage of pdf_page_offset before designing this.

- In scope, required: implement "continued on p. X" / "continued from p. X" text scanning (Addendum proposal #2) as an independent, non-LLM validation signal — scan each issue's raw extracted text for this near-universal magazine convention and use matches to (a) flag pieces whose claimed end_page/start_page doesn't line up with a real "continued" marker as suspect, and (b) positively confirm genuine non-contiguous articles (the model's noncontiguous escape hatch was never used once in the spike despite being available in the prompt).

- In scope, required: re-run the full pipeline (LLM extraction + coverage check + TOC-offset repair + continued-marker validation) against the exact same 8 issues sampled in the spike: PTG-2022-10, PTJ-2019-02, PTJ-2019-08, PTJ-2020-04, PTJ-2022-06, PTJ-2024-01, PTJ-2025-03, PTJ-2025-10. Use journalgpt/corpus/extracted/*/*.txt as input (same source the spike used) unless a change is independently justified and documented.

- Stretch goal, explicitly NOT required for done: now that real PDFs exist at journalgpt/pdfs/ (78-82 of ~94 files landed via in-progress FTP transfer as of this writing, matched by PTJ-YYYY-MM.pdf / PTG-YYYY-MM.pdf naming against corpus/manifest.json's 90 issues), prototype a vision-capable model pass on 1-2 confirmed-sparse ad pages (e.g. PTJ-2020-04 page 3, the near-blank ad page from finding #3 in the spike doc — pdftotext extracts almost nothing but "PIANO SUPPLY CO." and a footer line) to see whether page-image input recovers coverage that text extraction silently drops (failure mode #3, not addressed by either required item above). This uses the real, live OpenAI API key and spends real (small) money — cost is not a hard constraint per the spike's own cost estimate (~$0.45 full-corpus text-only; a 1-2 page vision prototype is negligible), but it is real spend against a shared key, not free.

- Out of scope, do not do: full articles/pieces schema design or any database migration (explicitly deferred in the findings doc's Recommendation section, pending a separate design conversation with the user); indexing the 23 missing corpus years (2019 Feb-Dec, 2025 Jan-Dec) into test/prod (separate, already-tracked open question, see the handoff and session-handoff docs); any vision-model work beyond the 1-2 page stretch-goal prototype above (i.e. do not build a full vision-based extraction pipeline or run it across the corpus); modifying journalgpt/corpus/extract_corpus.py or any production extraction/indexing code path (this is spike/validation code per the original brief's own framing — throwaway is fine, the deliverable is an answer plus a working prototype, not shipped pipeline code); touching the shared test/prod database in any way (no migration, no backfill, no admin-page changes) — this task is local/offline analysis only against journalgpt/corpus/extracted/ and journalgpt/pdfs/.


**Definition of Done:**
- A programmatic coverage checker exists (script, not just inline notebook code) that takes an issue's pieces list and reports gap pages and overlap pages against 1..max anchor.

- The TOC-anchor-offset extraction/repair step is implemented, reuses or explicitly documents its relationship to articles.pdf_page_offset / migrations/002_pdf_page_offset.sql, and is demonstrated to correct at least the PTJ-2025-10 finding-#2 case (article start_page corrected from the TOC-reference 7-ish/printed-18 confusion to the real anchor page ~20) when re-run.

- The "continued on/from p. X" text-scan validation signal is implemented and its matches (or confirmed absence) are reported per issue in the re-run output.

- The full validation+repair pipeline is re-run against all 8 of the spike's original sampled issues (PTG-2022-10, PTJ-2019-02, PTJ-2019-08, PTJ-2020-04, PTJ-2022-06, PTJ-2024-01, PTJ-2025-03, PTJ-2025-10), and a written report (placed under docs/ per the Dewey Decimal protocol in task_coordinator/README.md, category 30-Engineering, with correct frontmatter) presents a before/after table of missing-page and overlapping-page counts per issue, directly comparable to the spike findings doc's existing table (missing/overlapping baselines: PTG-2022-10 21/13; PTJ-2019-02 11/15; PTJ-2019-08 5/3; PTJ-2020-04 12/7; PTJ-2022-06 19/4; PTJ-2024-01 23/0; PTJ-2025-03 6/4; PTJ-2025-10 11/5 — see the findings doc's own table for the authoritative source of these numbers).

- The report explicitly states whether the pass closes the gaps/overlaps (quantified, not just "looks better") and gives a clear recommendation on whether this validation+repair approach is sufficient to trust piece-level page ranges for a future schema design, or whether more work (e.g. the vision-model stretch goal, or a human-review-required state per piece) is still needed.

- If the stretch goal (vision-model prototype) was attempted, the report notes what was tried, on which page(s), the actual OpenAI cost incurred, and whether it recovered coverage text extraction missed. If not attempted, the report says so plainly rather than omitting it.

- No changes were made to production extraction code (journalgpt/corpus/extract_corpus.py), no database migration was created or run, and no test/prod admin endpoints were touched — all work is local scripts/output under a scratch or docs location.


*Audited against SHA:* `943f11cc3a1ab7d24c5a0992c86009db2320394d`

---
### ✅ T-PTG-046 · P1 · ANY · DONE
**Fix broken citation links in history viewer for article_id=0**
**Owner:** Antigravity

**Scope:**

**Definition of Done:**
- i
- n
- d
- e
- x
- .
- p
- h
- p
-  
- a
- n
- d
-  
- f
- e
- a
- t
- u
- r
- e
- d
- .
- p
- h
- p
-  
- a
- r
- e
-  
- u
- p
- d
- a
- t
- e
- d
-  
- t
- o
-  
- c
- h
- e
- c
- k
-  
- i
- f
-  
- $
- a
- r
- t
- i
- c
- l
- e
- I
- d
-  
- >
-  
- 0
-  
- b
- e
- f
- o
- r
- e
-  
- w
- r
- a
- p
- p
- i
- n
- g
-  
- t
- h
- e
-  
- c
- i
- t
- a
- t
- i
- o
- n
-  
- c
- h
- i
- p
-  
- i
- n
-  
- a
- n
-  
- <
- a
-  
- h
- r
- e
- f
- >
-  
- t
- a
- g
- .
-  
- I
- f
-  
- $
- a
- r
- t
- i
- c
- l
- e
- I
- d
-  
- i
- s
-  
- 0
- ,
-  
- i
- t
-  
- r
- e
- n
- d
- e
- r
- s
-  
- a
-  
- s
- p
- a
- n
- .

*Audited against SHA:* `aec972badc76340e73dc2334d812d18d4ae7a65f`

---
### ✅ T-PTG-050 · P1 · ANY · DONE
**CSV-driven per-article extraction pilot (5-8 issues) using human-curated Airtable ground truth instead of LLM boundary inference**
**Owner:** Worker-CSVPilot1

**Scope:**
- Background, read first, in full: docs/superpowers/specs/2026-08-14-per-article-extraction-spike-findings.md (LLM boundary inference from raw flattened text is unreliable -- every one of 8 sampled issues had page-range gaps and/or overlaps). docs/30-Engineering/2026-08-14-page-coverage-validation-repair-pass.md (T-PTG-047, DONE/merged into test -- built coverage.py and toc_offset_repair.py, found the repair pass fixes overlaps but makes measured gaps worse for a diagnosable reason, and confirmed the TOC-anchor-offset mechanism -- printed page -> real [[page:N]] anchor page via footer-derived offset diffing -- works and empirically derives offset=2 for every one of the 8 sampled issues at 100% confidence). docs/30-Engineering/2026-08-14-article-editorial-completeness-qc-pass.md (T-PTG-048, status PEER_REVIEW as of this task's creation, NOT yet merged into test -- confirm current merge status at task start via `git merge-base --is-ancestor test-T-PTG-048 test`; if still unmerged, reference its worktree ../newmexicoptg.org-T-PTG-048 directly. T-PTG-048 ground-truthed PTJ-2020-02 against its own real table of contents and found LLM extraction drops or silently absorbs 3 of 6 short front-matter department columns -- President's Message, TT&T, The Piano Corner -- into a neighboring mis-anchored article's range, a failure invisible to page-coverage checking alone. This 15-row ground-truth table is reused directly in this task's cross-check -- do not re-derive it, it is quoted in full in that doc's "PTJ-2020-02 -- full 15-row ground-truth diff" section.)
- The new resource that changes the approach: a human-curated CSV export (a real Airtable export, NOT scraped or LLM-generated) of the Piano Technicians Journal's article index exists at journalgpt/pdfs/CompleteList-Sortable-Grid view.csv. 4130 real article rows, columns: Number, "Link to \nIssue" (issue in "Mon-YY" format, e.g. "Jan-79", "Feb-26"), Page (printed page number, integer), Article Title, Author(s), Summary/Keywords, Core skills, Concatenation, "Link to Issue" (a document download URL). Covers Jan-79 through Apr-26 (568 distinct issue labels). This is authoritative, human-entered ground truth for title/author/printed-page -- NOT something to be doubted or re-validated the way LLM output was. Encoding is utf-8-sig (has a BOM); there is a blank separator row near the top of the file (row 2, all-empty except a "---" in the Concatenation column) -- handle both when parsing. Some trailing rows (e.g. "Apr-26") have empty Page/Title/Author fields (future/uncatalogued issues) -- skip rows with an empty Article Title.
- Why this changes the extraction approach entirely: previously the hard, unsolved problem was inferring article BOUNDARIES from raw text with no ground truth. Now, for any issue with CSV rows, the real title, author, and printed start page of every article are already known, in order. This converts the problem from "infer boundaries" to "look up known start pages, slice text between consecutive starts." Three specific known wrinkles must be actually solved, not hand-waved past: (1) the last article in an issue has no "next" row to bound its end -- needs an explicit documented fallback (e.g. extend to the issue's final [[page:N]] anchor, accepting some back-matter/ad content may be included as a known limitation); (2) ad/classified/index pages likely are not cataloged as their own CSV rows -- this assumption must be spot-checked directly against a real issue's raw text at a boundary, not assumed; if an ad page sits between two cataloged articles' page ranges, the naive slice will incorrectly absorb it into the preceding article -- report findings honestly whether clean or contaminated; (3) the printed-page-to-anchor-page offset must be computed per issue, not hardcoded to 2, by reusing/extending T-PTG-047's toc_offset_repair.py approach (specifically its footer-derived offset computation: extract_footer_offsets() + derive_front_matter_offset() in journalgpt/spikes/T-PTG-047/toc_offset_repair.py, which depends only on common.py's page_blocks()/get_anchor_pages() -- this part does not depend on any LLM-produced pieces and is directly reusable for this task's purpose).
- Pilot issue set (5-8 issues, NOT a full-corpus run): parse the CSV, match rows to issues in journalgpt/corpus/manifest.json by converting "Mon-YY" to "PTJ-YYYY-MM" (or "PTG-YYYY-MM" for the 2 issues using that naming convention -- PTG-2022-10 and PTG-2022-11 are the only two). The pilot set MUST include: PTJ-2020-02 (has T-PTG-048's hand-derived 15-row ground truth to cross-check against -- this is the single most important validation signal), PTJ-2024-01, PTJ-2025-03, PTJ-2025-10 (have T-PTG-047 extraction output at journalgpt/spikes/T-PTG-047/output/<issue>.result.json to compare article counts/boundaries against). Plus 1-3 more of the worker's choice from issues that have all three of: a CSV entry, a PDF in journalgpt/pdfs/, and extracted text in journalgpt/corpus/extracted/.
- Per-pilot-issue processing: compute the real per-issue page offset (reuse extract_footer_offsets() + derive_front_matter_offset() from journalgpt/spikes/T-PTG-047/toc_offset_repair.py, do not reimplement from scratch), convert each CSV row's printed Page to a real anchor page using that offset, order articles by anchor page within the issue, and slice text from journalgpt/corpus/extracted/<issue>/*.txt between each article's start anchor and the next article's start anchor minus one (last article: use the issue's final anchor page per wrinkle #1 above, documented as a known limitation).
- Output format: write ONE markdown file per article, with YAML frontmatter (issue, article_title, author(s), printed_page, anchor_page_range, core_skills, summary_keywords, source_csv_row_number) followed by the full sliced body text. Save under a NEW directory journalgpt/corpus/articles_pilot/<issue>/<slugified-title>.md -- explicitly NOT under journalgpt/corpus/extracted/ or journalgpt/spikes/, since this is new, clearly-pilot output.
- Required investigation, not optional: directly investigate wrinkle #2 (ad/index contamination) by picking at least one boundary in the pilot set and reading the actual sliced text to check whether ad/classified content bleeds into an article's extracted file. Report the finding honestly whether clean or contaminated -- do not assume either outcome going in.
- Required cross-check, not optional: for PTJ-2020-02, compare the CSV-driven output against T-PTG-048's 15-row hand-derived ground-truth table (quoted in full in docs/30-Engineering/2026-08-14-article-editorial-completeness-qc-pass.md's "PTJ-2020-02 -- full 15-row ground-truth diff" section). Specifically answer: does the CSV-driven approach correctly produce the 6 short department items (Editorial Perspective, President's Message, TT&T, The Piano Corner, Tight Tuning Pins Part 1, Re-Covering Hammers by Hand) as 6 separate, correctly-bounded pieces, where T-PTG-048 found LLM extraction dropped/absorbed 3 of the 6? This is the single most important validation signal for whether the new approach is actually better. For PTJ-2024-01/2025-03/2025-10, compare article counts/boundaries against T-PTG-047's output/<issue>.result.json.
- Required written report under docs/30-Engineering/ (Dewey Decimal protocol, correct YAML frontmatter per task_coordinator/schemas/doc_frontmatter.schema.json) presenting: the offset computed per pilot issue (and whether it matched the DB default of 2), the ad-contamination investigation findings, the PTJ-2020-02 cross-check against T-PTG-048's known ground truth (does it fix the six-short-department-item failure mode -- answer explicitly yes/no/partially with evidence), sample output (2-3 full generated .md files shown inline or excerpted), and a clear, explicit recommendation on whether this CSV-driven approach should be scaled to the full ~90-issue corpus.
- Explicitly OUT OF SCOPE for this task: no full 90-issue corpus run (pilot only, 5-8 issues). No schema/DB design or migration. No touching test/prod (this task is entirely local file reads/writes under journalgpt/corpus/articles_pilot/ and a docs/ report -- no admin endpoint, no database connection). No modifying journalgpt/corpus/extract_corpus.py. No new OpenAI/LLM API calls required -- this is CSV parsing + text slicing, not LLM extraction. If the worker finds itself wanting to make an LLM call for any reason, it must stop and flag why in the report rather than just doing it.

**Definition of Done:**
- CSV parsed correctly (utf-8-sig BOM handled, blank separator row skipped, rows with empty Article Title skipped); row counts sanity-checked (4130 total rows minus header/separator/empty-title rows).
- Pilot set of 5-8 issues chosen, explicitly including PTJ-2020-02, PTJ-2024-01, PTJ-2025-03, PTJ-2025-10 plus 1-3 more, each with a documented reason for inclusion.
- Per-issue page offset computed via journalgpt/spikes/T-PTG-047/toc_offset_repair.py's extract_footer_offsets()/derive_front_matter_offset() (reused, not reimplemented) and reported per issue, not hardcoded to 2 anywhere in the pilot code.
- One markdown file per article written under journalgpt/corpus/articles_pilot/<issue>/<slugified-title>.md with YAML frontmatter (issue, article_title, author(s), printed_page, anchor_page_range, core_skills, summary_keywords, source_csv_row_number) and full sliced body text.
- Last-article-in-issue end-of-range fallback explicitly implemented and documented (wrinkle
- Ad/index contamination at a real pilot-set boundary directly investigated by reading actual sliced text, with findings reported honestly regardless of outcome (wrinkle
- PTJ-2020-02 cross-checked article-by-article against T-PTG-048's 15-row ground-truth table, with an explicit yes/no/partially answer on whether all 6 short department items are now correctly produced as separate pieces.
- PTJ-2024-01, PTJ-2025-03, PTJ-2025-10 cross-checked against T-PTG-047's output/<issue>.result.json for article count/boundary agreement.
- Written report under docs/30-Engineering/ with correct Dewey Decimal category and YAML frontmatter matching task_coordinator/schemas/doc_frontmatter.schema.json, covering all required findings above plus 2-3 sample generated .md files and a clear scale-up recommendation.
- No changes to journalgpt/corpus/extract_corpus.py, no database migration, no test/prod admin endpoint touched, no OpenAI/LLM API calls made (or, if the worker judged one unavoidable, an explicit flag in the report explaining why before proceeding).

*Audited against SHA:* `a527e9dc2cd6adf70f2df2cb756ba4b7cc705c87`

---
### ⏳ T-PTG-004 · P1 · ANY · HUMAN_REVIEW
**Audit citation metadata accuracy: volume/issue-number mismatches between issue_label and title**
**Owner:** Claude-Worker

**Scope:**
- journalgpt articles table (volume, issue_number, title columns) and journalgpt/corpus/manifest.json (volume/number fields used by the Tier-4 fallback path).
- Found live in the reported bug example — footnote [2]: '2022-10-01 Vol. 69 No. 10 — "Piano Technicians Journal — October 2022 Issue (Vol. 65 No. 10)", p. 21'. The issue_label (built from articles.volume / articles.issue_number) says 'Vol. 69 No. 10'; the article's own title string for the same October 2022 issue says '(Vol. 65 No. 10)'. Both cannot be right for the same physical issue — this is a direct violation of the 'must give reference to the right journal number' hard requirement, independent of the footnote-numbering bug in T-PTG-001.
- Also audit for similarly generic/low-information titles like 'Piano Technicians PTJ 2025-05 Issue Content' that read as synthesized placeholders rather than real article titles — these make citations technically present but practically useless to a member trying to verify a source.

**Definition of Done:**
- Write a one-off audit script (or SQL query) that finds every article row where a volume/issue-number embedded in title disagrees with the row's own volume/issue_number columns, and report the count and sample rows.
- Root-cause how the two diverged (bad import script, manual edit, two different numbering schemes merged at some point, etc.) — write findings into a task_coordinator feedback file per the README's feedback protocol, not just fixed silently.
- For confirmed-wrong rows, correct volume/issue_number (or title, whichever is actually wrong per the source PDF) via a migration or corrective script, not a one-off manual DB edit with no record.
- Flag (but do not necessarily rewrite) titles that are generic placeholders rather than real article titles, with a recommendation for the human on how to best source the real titles.
- Note: the local dev DB (journal_ai_test, 92 seeded articles) shows zero mismatches from cli/audit_citation_metadata.php (already written; see repo) — the affected rows may only exist in the full production corpus. Run the audit against production data (or the fullest available corpus snapshot), not just the local pilot subset, before concluding there is nothing to fix.

*Audited against SHA:* `9e74d39c82a5980f488695fb4e4e5e1dd46bdb54`

---
### 📋 T-PTG-053 · P1 · ANY · OPEN
**Coverage Atlas Phase 1b: coverage radar dashboard + empty-wedge nudge**
**Owner:** None

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
### 📋 T-PTG-052 · P1 · ANY · OPEN
**Coverage Atlas Phase 1a: member_article_activity log + signal hooks + issue-to-article resolver**
**Owner:** None

**Scope:**
- Spec: docs/superpowers/specs/2026-08-17-coverage-atlas-design.md section 3. New migration (019): member_article_activity (user_id, article_index_id, activity_type ENUM(read, quiz_passed, discussed), created_at; FK to article_index; append-only, no unique constraint -- repeat engagement is real signal for recency even though the radar aggregation deduplicates per (user, article, type)).
- THE KEY TECHNICAL RISK, solve first: existing engagement signals are keyed to the ISSUE-LEVEL articles table (journalgpt_citation_logs.article_id, quiz_questions.article_id both FK to articles), but the radar needs PER-ARTICLE article_index rows. Build a resolver lib (e.g. lib/ArticleIndexResolver.php) mapping (issue-level article_id, page) -> article_index_id by joining articles.issue_date/volume/pdf_filename to article_index.issue_label (format like "Jan-79") and picking the article_index row whose page range contains the cited page (rows sorted by page within an issue; a row spans from its page to the next row's page - 1). Resolver returns null on no-match; log unresolved hits, never guess. TDD the resolver against real fixture rows before wiring any hooks.
- Hooks, all thin: (1) read -- source.php PDF opens that carry an article_index context, and citation renders in answers count via (3); (2) quiz_passed -- in submit_quiz_attempt.php after scoring, for each correctly-answered question resolve its article_id+page and log; (3) discussed -- where journalgpt_citation_logs rows are written, resolve and log alongside. Hooks must be fail-open: a resolver miss or insert failure must never break the member-facing request.

**Definition of Done:**
- Migration 019 applied to the local test DB via cli/migrate.php with no errors.
- Resolver test proves correct mapping for a multi-article issue fixture (first, middle, last article by page) and returns null for an unmatchable page/issue.
- Each of the three hooks writes a correct member_article_activity row in its existing test (extend QuizTest / CitationLoggingTest rather than new suites where natural), and a forced resolver failure does not change the endpoint''s response.
- Golden hammer suite passes with zero regressions.

---
### 📋 T-PTG-051 · P1 · ANY · OPEN
**Coverage Atlas foundation: run migration 018 + article-index import on the shared DB and verify the tagging matrix live**
**Owner:** None

**Scope:**
- Background, read first: docs/superpowers/specs/2026-08-17-coverage-atlas-design.md (the Coverage Atlas spec this epic delivers; supersedes the 2026-08-16 learning-paths skill-tree spec). The code is ALREADY MERGED into test and pushed (commit a8f88e1 "feat: editable article-index x topic matrix"): migration journalgpt/migrations/018_article_index.sql, lib/ArticleIndexImporter.php, cli/import_article_index.php, data/article_index.csv (4,120 rows), admin_article_index_matrix.php, api/toggle_article_index_topic.php, tests/ArticleIndexMatrixTest.php (22 assertions, passing locally).
- This task is ONLY the shared-database rollout: run migration 018 and cli/import_article_index.php against the deployed environment, then browser-verify admin_article_index_matrix.php on test.newmexicoptg.org (login, grid renders 4,120 articles, one checkbox toggle round-trips to article_index_topics and survives reload).
- HARD CONSTRAINT (memory + fleet README): test.newmexicoptg.org SHARES the production database. Migration 018 is additive-only (two new tables, no ALTERs), but the DB write still requires Chip's explicit go at execution time. Do not run the migration or import without that confirmation recorded in this task's events.

**Definition of Done:**
- article_index and article_index_topics tables exist in the shared DB; SELECT COUNT(*) FROM article_index returns 4120.
- Re-running cli/import_article_index.php a second time leaves the count at 4120 (idempotency verified in the real environment).
- admin_article_index_matrix.php on test.newmexicoptg.org renders the grid for a logged-in member, one checkbox toggle persists across a reload, and no PHP errors appear in debug_logs.
- Golden hammer suite still passes locally (DB_HOST=127.0.0.1 DB_NAME=journal_ai_test DB_USER=root DB_PASS=root php journalgpt/tests/security_and_eval_suite.php).

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
### 📋 T-PTG-024 · P2 · ANY · AUDITED
**JournalGPT v3 Phase 4: ClaimValidator (claim-level citation verification)**
**Owner:** None

**Scope:**
- CONTEXT FOR ANY AGENT PLATFORM PICKING THIS UP: read journalgpt/v3/v3.md section 14 (Claim Verification) and section 15 (Existing Citation System, which MUST be preserved, not replaced) before starting. Gated on T-PTG-023 (AnswerSynthesizer).
- WHAT TO BUILD, per v3.md section 14 exactly: create `journalgpt/lib/ClaimValidator.php`. Journal-derived claims (as distinguished by T-PTG-023's AnswerSynthesizer) should be validated individually, not all-or-nothing. Desired behavior per v3.md's table: supported Journal claim -> retain + cite; unsupported Journal attribution -> remove, rewrite, or regenerate; assistant explanation -> retain when appropriately framed; uncertain conclusion -> explicitly identify uncertainty. v3.md section 14 is explicit: "Do not automatically discard an entire useful answer because one citation cannot be resolved" -- this replaces today's coarser all-or-nothing grounding behavior with per-claim validation.
- MUST PRESERVE THE EXISTING CITATION RESOLVER, per v3.md section 15: continue using the existing article mappings, provider file IDs, page markers, manifest data, local corpus matching, page verification, printed-page info, and protected source URLs. ClaimValidator feeds BETTER evidence metadata to the existing resolver -- it does not replace or duplicate the resolver's job of turning a supported claim into an exact citation link.
- GOLDEN HAMMER GATE (hard requirement, per Chip's explicit direction this session): before merging to main, run `DB_HOST=127.0.0.1 DB_NAME=journal_ai_test DB_USER=root DB_PASS=root php journalgpt/tests/security_and_eval_suite.php` and confirm 9/9 PASS with zero regressions.
- EXPLICITLY OUT OF SCOPE: IP hardening / public-sharing review (Phase 5), evaluation tuning (Phase 6). Do not build a new citation-resolution mechanism -- reuse the existing resolver exactly per v3.md section 15's explicit instruction.

**Definition of Done:**
- ClaimValidator.php exists per v3.md section 14's four-way behavior table (supported/unsupported/explanation/uncertain), and integrates with the EXISTING citation resolver rather than reimplementing citation lookup.
- A new test file (journalgpt/tests/ClaimValidatorTest.php) covers all four behaviors in the table with concrete test cases, and specifically proves the "do not discard the whole answer over one bad citation" requirement -- a multi-claim answer where one claim's citation fails to resolve must still return the other, valid claims intact rather than a blanket refusal.
- Wired into the live path after T-PTG-023's synthesis step, before the response is returned to the member.
- The golden hammer suite (security_and_eval_suite.php) passes 9/9 with zero regressions, and eval_runner.py's citation-accuracy and grounding scoring specifically show no regression vs. the Phase 3 baseline (record the before/after scores in the handoff).
- php -l passes on all new/modified PHP files.

*Audited against SHA:* `ebf93f751dbe07c86f8e3c296bbe7c9e3c88465c`

---
### 📋 T-PTG-025 · P2 · ANY · AUDITED
**JournalGPT v3 Phase 5: IP hardening review (public sharing, bulk-extraction, source authorization)**
**Owner:** None

**Scope:**
- CONTEXT FOR ANY AGENT PLATFORM PICKING THIS UP: read journalgpt/v3/v3.md sections 2.1, 17-19 (Intellectual Property Protection, Bulk Extraction Protection, Public Sharing Review) before starting. Gated on T-PTG-024 (ClaimValidator) -- by this point the answer pipeline has fundamentally changed (planning, multi-query retrieval, ranking, synthesis with explanation-vs-Journal distinction, per-claim validation), so this phase re-audits the existing IP/security protections against the NEW pipeline shape, not just the old one.
- WHAT TO REVIEW/HARDEN, per v3.md exactly: (1) section 17 -- confirm the browser never receives OpenAI API keys, vector-store credentials, corpus filesystem paths, extracted corpus dumps, or private storage credentials, across ALL the new lib classes added in Phases 1-4 (ConversationStateService, ResearchPlanner, EvidenceRetriever, EvidenceRanker, AnswerSynthesizer, ClaimValidator) -- a new class is a new place a leak could be introduced. (2) section 18 -- confirm bulk-extraction refusal (already tested in security_and_eval_suite.php's TC-SEC-001/002 cases) still works correctly against the new multi-query retrieval pipeline, which by design fetches MORE passages per question than the old single-search pipeline -- verify this increased retrieval breadth has not created a new bulk-extraction loophole. (3) section 19 -- review the existing public conversation-sharing feature (find it in the codebase -- grep for "shared" conversations, `SharedConversationsTest.php` already exists) and confirm unauthenticated users still cannot gain protected PDF access via a shared conversation, even though shared conversations may now include the new explanation-vs-Journal-distinguished content and per-claim-validated citations from Phases 3-4.
- GOLDEN HAMMER GATE (hard requirement, per Chip's explicit direction this session): before merging to main, run `DB_HOST=127.0.0.1 DB_NAME=journal_ai_test DB_USER=root DB_PASS=root php journalgpt/tests/security_and_eval_suite.php` and confirm 9/9 PASS with zero regressions, including SharedConversationsTest.php and AuthAccessTest.php specifically.
- EXPLICITLY OUT OF SCOPE: Phase 6 evaluation/tuning. This is a review-and-harden task, not a new-feature task -- if the review finds everything already correctly protected against the new pipeline, the DoD is still satisfied by documenting that finding with evidence, not by inventing unnecessary new restrictions.

**Definition of Done:**
- A written review (in the handoff, not a new doc file unless the Worker judges one is needed) explicitly addresses all three v3.md areas (secret/credential exposure across the new Phase 1-4 classes, bulk-extraction refusal against the wider multi-query retrieval, and public-sharing PDF-access boundary) with concrete evidence for each -- either "confirmed already safe, here is the test/grep that proves it" or "found a gap, here is the fix."
- Any gap found is fixed, with a new or extended test proving the fix (e.g. extending SharedConversationsTest.php or security_and_eval_suite.php's existing TC-SEC-* cases).
- Add at least one NEW automated test case specifically targeting bulk-extraction attempts against the new multi-query retrieval pipeline (e.g. "give me everything you found across all your searches"), since this is a genuinely new attack surface the old single-search pipeline didn't have.
- The golden hammer suite (security_and_eval_suite.php) passes 9/9 with zero regressions.
- php -l passes on all modified PHP files.

*Audited against SHA:* `ebf93f751dbe07c86f8e3c296bbe7c9e3c88465c`

---
### 📋 T-PTG-022 · P2 · ANY · AUDITED
**JournalGPT v3 Phase 2b: EvidenceRanker**
**Owner:** None

**Scope:**
- CONTEXT FOR ANY AGENT PLATFORM PICKING THIS UP: read journalgpt/v3/v3.md section 11 (Evidence Ranking) before starting. This is the second half of Phase 2, gated on T-PTG-020 (EvidenceRetriever) being DONE.
- WHAT TO BUILD, per v3.md section 11 exactly: create `journalgpt/lib/EvidenceRanker.php`. Not every passage T-PTG-020's EvidenceRetriever collects should go directly to the final answering model. Rank evidence by: relevance to user intent, relevance to conversation context, source quality, specificity, redundancy, citation resolvability. Output a compact evidence bundle for synthesis (v3.md section 11's exact phrase).
- GOLDEN HAMMER GATE (hard requirement, per Chip's explicit direction this session): before merging to main, run `DB_HOST=127.0.0.1 DB_NAME=journal_ai_test DB_USER=root DB_PASS=root php journalgpt/tests/security_and_eval_suite.php` and confirm 9/9 PASS with zero regressions -- the current app must keep working exactly as before for members using it today while this v3 work proceeds in parallel.
- EXPLICITLY OUT OF SCOPE: AnswerSynthesizer, ClaimValidator (Phase 3-4). Do not change the live wiring T-PTG-020 established beyond inserting this ranking step between retrieval and synthesis.

**Definition of Done:**
- EvidenceRanker.php exists per v3.md section 11's six ranking criteria, and demonstrably reduces/reorders a raw evidence set into a compact bundle.
- A new test file (journalgpt/tests/EvidenceRankerTest.php) covers at least: a redundant/duplicate passage being down-ranked or dropped, and a highly relevant passage being ranked above a tangentially related one for a specific test question.
- Wired into the live path after T-PTG-020's retriever, before wherever synthesis currently happens (still the existing JournalAnswerService synthesis step at this point, since AnswerSynthesizer.php doesn't exist yet).
- The golden hammer suite (security_and_eval_suite.php) passes 9/9 with zero regressions.
- The existing test suite chain (AskEndpointTest, UsagePolicyTest, JournalAnswerServiceTest, ConversationStateServiceTest, ResearchPlannerTest, EvidenceRetrieverTest) still passes in full.
- php -l passes on all new/modified PHP files.

*Audited against SHA:* `ebf93f751dbe07c86f8e3c296bbe7c9e3c88465c`

---
### 📋 T-PTG-023 · P2 · ANY · AUDITED
**JournalGPT v3 Phase 3: AnswerSynthesizer + Journal-vs-explanation distinction**
**Owner:** None

**Scope:**
- CONTEXT FOR ANY AGENT PLATFORM PICKING THIS UP: read journalgpt/v3/v3.md sections 12-13 (Answer Synthesis, Two Kinds of Knowledge) before starting. Gated on T-PTG-022 (EvidenceRanker).
- WHAT TO BUILD, per v3.md section 12: create `journalgpt/lib/AnswerSynthesizer.php`. Receives: the member's question, recent conversation, T-PTG-018's persistent research state, T-PTG-019's research plan, and T-PTG-022's ranked evidence bundle. Produces the best useful answer possible.
- THE CORE NEW BEHAVIOR, per v3.md section 13 exactly: the synthesizer must explicitly distinguish "Journal-supported information" (requires evidence and citation, e.g. "The Journal describes friction at the bearing points as...") from "Assistant explanation" (interpretation/comparison/general reasoning, e.g. "A useful way to picture this mechanically is..." -- must NOT be falsely represented as something PTJ published). This is v3.md's stated mechanism for "how JournalGPT can become significantly more conversational without compromising citation integrity" -- the single most important behavioral change in this phase.
- GOLDEN HAMMER GATE (hard requirement, per Chip's explicit direction this session): before merging to main, run `DB_HOST=127.0.0.1 DB_NAME=journal_ai_test DB_USER=root DB_PASS=root php journalgpt/tests/security_and_eval_suite.php` and confirm 9/9 PASS with zero regressions.
- EXPLICITLY OUT OF SCOPE: ClaimValidator (Phase 4 -- validating individual claims is a separate, later step; this phase only produces the answer with the two kinds of content clearly distinguished, it does not yet verify each Journal-attributed claim against evidence). Do not weaken the existing hard requirement (v3.md section 2.2/2.3) that Journal-attributed claims must be cited and citations must resolve -- this phase adds explanation capability, it does not loosen grounding requirements.

**Definition of Done:**
- AnswerSynthesizer.php exists per v3.md section 12's inputs and produces answers that visibly/structurally distinguish Journal-supported content from assistant explanation (Worker's exact mechanism -- e.g. distinct markup, a structured field separating the two -- documented in the handoff).
- A new test file (journalgpt/tests/AnswerSynthesizerTest.php) proves the distinction works: at least one test case where the answer correctly separates a cited Journal fact from an explanatory aside, and confirms the explanatory aside is never citation-tagged as if it were a Journal claim.
- Wired into the live path, replacing/extending wherever synthesis currently happens in JournalAnswerService.
- The golden hammer suite (security_and_eval_suite.php) passes 9/9 with zero regressions, including the existing citation-grounding test cases in JournalAnswerServiceTest.php and the eval_runner.py rubric (grounding/citation/uncertainty scoring) -- this phase must not regress citation accuracy while adding explanatory capability.
- php -l passes on all new/modified PHP files.

*Audited against SHA:* `ebf93f751dbe07c86f8e3c296bbe7c9e3c88465c`

---
### 📋 T-PTG-020 · P2 · ANY · AUDITED
**JournalGPT v3 Phase 2: intelligent retrieval (EvidenceRetriever, multi-query search, dedup)**
**Owner:** None

**Scope:**
- CONTEXT FOR ANY AGENT PLATFORM PICKING THIS UP: read journalgpt/v3/v3.md sections 9-10 (Multi-Query Journal Search, Evidence Retriever) and section 32's Phase 2 description before starting. This is the first task that actually integrates prior work into the live pipeline -- v3.md section 32 says "At this point, run the benchmark again. This is the first major go/no-go checkpoint," so this task's DoD requires a benchmark comparison, not just unit tests.
- WHAT TO BUILD, per v3.md section 10 exactly: create `journalgpt/lib/EvidenceRetriever.php`. Responsibilities: execute T-PTG-019's ResearchPlanner-produced search queries (plural -- multiple targeted searches per v3.md section 9, not one literal-interpretation search) against the existing OpenAI File Search / vector store integration (reuse `journalgpt/lib/OpenAIClient.php`, do not rebuild retrieval plumbing that already works -- v3.md section 3 is explicit that existing OpenAI integration, vector-store indexing, and File Search must be preserved, not replaced); collect passages; normalize retrieval metadata; preserve source identity and page information; deduplicate overlapping chunks; prevent one source from dominating results; limit total evidence size.
- THIS TASK DOES THE FIRST LIVE INTEGRATION: unlike T-PTG-018/019, this task DOES wire ResearchPlanner + EvidenceRetriever into an actual code path -- but per v3.md section 27 (Failure Handling), it must degrade gracefully: "Planner unavailable -> use direct retrieval" and "One search fails -> continue with successful searches when sufficient." Do not make the new pipeline a hard replacement with no fallback -- if you cannot safely make it the default live path without risking a production regression, wire it behind a clearly-named feature flag/tier option instead and say so explicitly in the handoff (Worker's judgment call, but must be justified, not silently punted).
- THE GO/NO-GO CHECKPOINT, per v3.md section 32: after this task, replay T-PTG-015's benchmark against BOTH the old pipeline and the new EvidenceRetriever-based pipeline and compare retrieval quality (did it find the right Journal material for the benchmark's documented disappointing cases, especially the follow-up and multi-source categories). This comparison result belongs in the handoff and determines whether later phases (3-6) are worth continuing -- do not just claim success without this comparison.
- EXPLICITLY OUT OF SCOPE: EvidenceRanker (T-PTG-021), AnswerSynthesizer, ClaimValidator. Do not remove or bypass the existing citation resolver -- v3.md section 15 requires preserving it; this task only improves what evidence FEEDS the existing resolver, it does not replace the resolver itself.

**Definition of Done:**
- EvidenceRetriever.php exists per v3.md section 10's responsibilities, executes multi-query plans from ResearchPlanner, deduplicates, and bounds evidence size.
- A new test file (journalgpt/tests/EvidenceRetrieverTest.php) covers multi-query execution, deduplication of overlapping chunks, and graceful degradation when a single search fails.
- The new pipeline is wired into an actual reachable code path (default or behind a stated flag/tier per this task's scope), with graceful fallback to direct retrieval if the planner is unavailable, per v3.md section 27.
- The Go/No-Go benchmark comparison from this task's scope is performed and its result (better, worse, or mixed retrieval quality vs. the old pipeline, with specifics) is recorded plainly in the handoff -- this is the single most important piece of evidence for whether Phase 3+ should proceed.
- GOLDEN HAMMER GATE (hard requirement, per Chip's explicit direction this session): before merging to main, run `DB_HOST=127.0.0.1 DB_NAME=journal_ai_test DB_USER=root DB_PASS=root php journalgpt/tests/security_and_eval_suite.php` and confirm 9/9 PASS with zero regressions. This task is the FIRST to wire new code into a live path -- this gate is especially critical here, since a mistake could break the app for members using it today.
- The existing test suite still passes in full (AskEndpointTest.php, UsagePolicyTest.php, JournalAnswerServiceTest.php, ConversationStateServiceTest.php, ResearchPlannerTest.php) -- 0 regressions to the existing citation-grounded RAG lane.
- php -l passes on all new/modified PHP files.

*Audited against SHA:* `ebf93f751dbe07c86f8e3c296bbe7c9e3c88465c`

---
### 📋 T-PTG-026 · P2 · ANY · AUDITED
**JournalGPT v3 Phase 6: replay benchmark and tune (final evaluation pass)**
**Owner:** None

**Scope:**
- CONTEXT FOR ANY AGENT PLATFORM PICKING THIS UP: read journalgpt/v3/v3.md sections 24-26 (Evaluation Dataset, Evaluation Metrics, Observability) and section 32's Phase 6 description before starting. This is the final phase, gated on T-PTG-025 (IP hardening) AND T-PTG-015 (the original Phase 0 benchmark, for direct before/after comparison).
- WHAT TO DO, per v3.md section 32 exactly: "Replay benchmark and tune: prompts, retrieval breadth, model choice, evidence limits, tier behavior, latency, cost." Run T-PTG-015's full 30-50 example benchmark against the NOW-COMPLETE v2/v3 pipeline (Phases 1-5 all merged) and score it against v3.md section 25's metrics: conversational understanding, retrieval quality, answer usefulness, citation accuracy, citation relevance, continuity, uncertainty handling, IP compliance, latency, cost.
- THIS IS THE FINAL GO/NO-GO, not just a tuning pass: for every one of T-PTG-015's original disappointing examples, the handoff must state whether the new pipeline actually fixes it (e.g. does the new pipeline correctly resolve the "why?" follow-up now that ConversationStateService + ResearchPlanner exist?) or whether it does not -- do not present an average score improvement as success if specific, previously-broken cases documented in the benchmark are still broken. v3.md's own Success Criteria (section 34) is a concrete multi-turn conversation example ("What does the Journal say about false beats?" -> "What causes them?" -> "Is that different in wound strings?" -> "So what would you check first?") -- test this exact flow live as part of the evaluation.
- GOLDEN HAMMER GATE (hard requirement, per Chip's explicit direction this session): before merging any tuning changes to main, run `DB_HOST=127.0.0.1 DB_NAME=journal_ai_test DB_USER=root DB_PASS=root php journalgpt/tests/security_and_eval_suite.php` and confirm 9/9 PASS with zero regressions after every tuning iteration, not just once at the end.
- EXPLICITLY OUT OF SCOPE: building any new pipeline component -- Phases 1-5 are done by this point, this phase only tunes what exists (prompts, thresholds, retrieval breadth, model/tier choice) based on the benchmark replay results. Do not add new lib classes here.

**Definition of Done:**
- T-PTG-015's full benchmark is replayed against the complete new pipeline, and results are scored per v3.md section 25's metrics, with per-example before/after comparison (not just aggregate scores) for every originally-disappointing example.
- v3.md's section 34 success-criteria conversation flow (false beats -> causes -> wound strings comparison -> practical synthesis) is tested live and the handoff states plainly whether it now works as the PRD envisions.
- At least one tuning iteration is made based on benchmark results (prompt, retrieval breadth, evidence limit, or tier behavior adjustment) with a documented before/after score change, proving the tuning loop actually works, not just that a single pass was run.
- The golden hammer suite (security_and_eval_suite.php) passes 9/9 with zero regressions after all tuning changes.
- The handoff includes a clear final recommendation to Chip: is JournalGPT v3 ready to be the default experience for all members, or does it need further work before full rollout, with specific reasoning tied to the benchmark results.

*Audited against SHA:* `ebf93f751dbe07c86f8e3c296bbe7c9e3c88465c`

---
### ✅ T-PTG-019 · P2 · ANY · DONE
**JournalGPT v3 Phase 1b: ResearchPlanner + contextual follow-up understanding**
**Owner:** Antigravity

**Scope:**
- CONTEXT FOR ANY AGENT PLATFORM PICKING THIS UP: read journalgpt/v3/v3.md sections 4 (Primary Problem), 8-9 (Research Planner, Multi-Query Journal Search), and 28-29 (Code Organization, Target JournalAnswerService Flow) before starting. This is Phase 1's second deliverable, building on T-PTG-018's ConversationStateService (already DONE if you can claim this task -- the fleet dependency check enforces it).
- WHAT TO BUILD, per v3.md section 8 exactly: create `journalgpt/lib/ResearchPlanner.php`. Given a member's question plus recent conversation plus T-PTG-018's persistent conversation state, it must determine (structured output, NOT prose meant for the member -- v3.md is explicit: "Planner output must be structured data, not prose intended for the user" and "Do not expose private model chain-of-thought"): user intent, the underlying technical topic, relevant prior context, PTJ-likely terminology, whether multiple searches are needed, and what kind of answer is expected. v3.md gives a full example JSON shape (intent/topic/search_queries) -- read it directly.
- INTEGRATION POINT, per v3.md section 9 and the real production evidence in T-PTG-015's benchmark: this is what fixes the exact failure mode documented there -- a member typing a bare "why?" or "what about an upright?" as a follow-up, which the current pipeline treats as a standalone, context-free question. The planner must consult T-PTG-018's ConversationStateService to resolve such follow-ups against the actual prior topic.
- DO NOT WIRE THIS INTO THE LIVE ANSWER PATH YET: build ResearchPlanner.php as a standalone, independently testable unit (matching v3.md section 28's target architecture where JournalAnswerService.php becomes "primarily an orchestrator" -- that orchestration wiring is a LATER integration step, not this task). Do not modify JournalAnswerService.php's actual production `ask()` flow in this task -- that risks a live regression before the full pipeline (retrieval, ranking, synthesis, validation) exists to actually consume the planner's output correctly. Building it in isolation first, proven against the benchmark's follow-up examples via direct unit tests, is the safer sequencing.
- EXPLICITLY OUT OF SCOPE: EvidenceRetriever, EvidenceRanker, AnswerSynthesizer, ClaimValidator (all later phases). Wiring ResearchPlanner into the live `ask()` endpoint (a follow-up integration task once Phase 2's retrieval work also exists, since a planner alone with no new retrieval to consume its multi-query output isn't useful in production yet).

**Definition of Done:**
- ResearchPlanner.php exists per v3.md section 8's shape, consumes T-PTG-018's ConversationStateService output plus recent conversation, and returns structured planning data (not prose).
- A new test file (journalgpt/tests/ResearchPlannerTest.php) demonstrates, using at least 2 of T-PTG-015's benchmark follow-up examples (the "why?" and "what about an upright?"-style cases) as fixtures, that the planner correctly resolves the follow-up's intent using persistent conversation state rather than treating it as context-free.
- GOLDEN HAMMER GATE (hard requirement, per Chip's explicit direction this session): before merging to main, run `DB_HOST=127.0.0.1 DB_NAME=journal_ai_test DB_USER=root DB_PASS=root php journalgpt/tests/security_and_eval_suite.php` and confirm 9/9 PASS with zero regressions -- the current app must keep working exactly as before for members using it today while this v3 work proceeds in parallel.
- The existing test suite still passes in full (AskEndpointTest.php, UsagePolicyTest.php, JournalAnswerServiceTest.php, ConversationStateServiceTest.php) -- 0 regressions, since this task does not touch the live answer pipeline.
- php -l passes on all new/modified PHP files.
- The handoff states explicitly that ResearchPlanner is NOT yet wired into the live ask() endpoint, per this task's scope, and names which future task should do that integration (Phase 2's retrieval task, once EvidenceRetriever exists to consume multi-query plans).

*Audited against SHA:* `ebf93f751dbe07c86f8e3c296bbe7c9e3c88465c`

---
### ⏳ T-PTG-017 · P2 · ANY · HUMAN_REVIEW
**Implement member feature request (conversation 53): better mobile screen real estate management for the engine-controls-bar**
**Owner:** Worker-Mobile1

**Scope:**
- SOURCE: a real member (user_id 1, conversation_id 53) used the `/featurerequest` triage lane (shipped T-PTG-008, tag-matching fixed T-PTG-009) on 2026-08-12 21:22-21:25 and completed all three triage dimensions -- confirmed via `debug_logs.php?conversation_id=53` (log ids 26-29, `preset: feature_request`, final `status: fr_complete`): idea = "better mobile support"; who/context = "for when you're in the car"; how_often = "once a week"; what_it_would_look_like = "better screen real estate management". This is the first feature request to make it through the triage lane end-to-end successfully (conversation 51, the earlier color-schemes request, only worked after T-PTG-009's fix and was handled as a separate task). No automated script exists yet to convert `feature_request_details.status = 'complete'` rows into fleet tasks (confirmed: no such script in journalgpt/cli/) -- the Fleet Coordinator is doing this conversion manually this time.
- INTERPRETING THE VAGUE REQUEST: "better screen real estate management" plus "for when you're in the car" plus "once a week" points at quick, low-frequency mobile glances at journalgpt, where wasted horizontal/vertical space on a small screen is the actual pain point -- not a request for a native app, offline mode, or voice interface (those would be separate, much larger asks the member did not describe). Scout confirmed a concrete, scoped root cause by reading the CSS directly: `journalgpt/assets/journal-chat.css:727` has a single `@media (max-width: 768px)` breakpoint that already handles the sidebar, chat header, message bubbles, and input area responsively -- but the `.engine-controls-bar` (containing the "Thinking Tier" and "Theme" dropdowns, added inline in `journalgpt/index.php:325-350` with no dedicated CSS class rules at all, `display: flex; justify-content: space-between`) has ZERO responsive handling. On a narrow phone viewport, two label+dropdown pairs side by side with `justify-content: space-between` is a plausible source of exactly the complaint: cramped controls, wasted/overflowing horizontal space, poor screen-real-estate use.
- FIX SCOPE: add a `@media (max-width: 768px)` rule (reuse/extend the EXISTING breakpoint at journalgpt/assets/journal-chat.css:727 -- do not introduce a second, differently-valued breakpoint) that makes `.engine-controls-bar` and its two child groups (`.model-select-group`, `.theme-select-group`) lay out compactly on mobile: reduce wasted horizontal space (e.g. stack the two groups vertically, or shrink label text/hide the "Thinking Tier:"/"Theme:" text labels down to compact icon-only or abbreviated controls at this breakpoint, Worker's design call -- state the chosen approach and why in the handoff) while keeping both controls fully usable (44px minimum touch target height, matching this codebase's existing mobile touch-target convention already used elsewhere in the same media query, e.g. `.sidebar-toggle-btn`'s `min-height: 44px`).
- DO NOT MOVE THE INLINE STYLES WHOLESALE INTO CSS AS PART OF THIS TASK unless necessary for the responsive fix itself -- `.engine-controls-bar`'s current inline-style approach in index.php is pre-existing and out of scope to refactor generally; only add what's needed to make it responsive at the mobile breakpoint (a `@media` block naturally overrides inline styles via specificity/`!important` if truly needed, or the Worker may add a plain CSS class selector matching the existing class names already present in the markup -- `.engine-controls-bar`, `.model-select-group`, `.theme-select-group` -- which is the cleaner approach and should be preferred).
- EXPLICITLY OUT OF SCOPE: no native app, no offline mode, no voice interface, no changes to any other page's mobile layout (this request is specifically about the Thinking Tier/Theme controls bar on index.php, the only place this bar exists). Do not touch the already-working mobile responsive rules for sidebar/header/messages/input in the same media query block -- only add to it.

**Definition of Done:**
- A `@media (max-width: 768px)` rule targets `.engine-controls-bar`, `.model-select-group`, and `.theme-select-group` and demonstrably reduces wasted horizontal space compared to today's layout (Worker's chosen approach, documented in the handoff with before/after screenshots via the `/browse` skill -- never `mcp__claude-in-chrome__*` tools directly, per this project's CLAUDE.md -- at a 375px-wide viewport, a common phone width).
- Both the Thinking Tier and Theme dropdowns remain fully functional and reachable with at least a 44px touch target at the mobile breakpoint, matching this codebase's existing mobile touch-target convention.
- No regression to the existing desktop layout (viewport wider than 768px) -- verify via `/browse` screenshot that the engine-controls-bar looks unchanged above the breakpoint.
- No regression to any other already-working mobile responsive behavior in the same media query block (sidebar toggle, chat header, message bubbles, input area) -- confirm via `/browse` screenshot at 375px that these still look correct.
- php -l passes on journalgpt/index.php.
- The existing test suite still passes in full -- journalgpt/tests/AskEndpointTest.php, journalgpt/tests/UsagePolicyTest.php, and journalgpt/tests/JournalAnswerServiceTest.php all run clean (0 failures).
- The handoff records the exact member feedback this task addresses (conversation 53's three triage answers, quoted verbatim) so the human reviewer can judge whether the shipped fix actually addresses what was asked, not just a plausible-sounding interpretation of a vague request.

*Audited against SHA:* `e2edf343520a3418114da8997f31ae5dc3f245ec`

---
### 📋 T-PTG-055 · P2 · ANY · OPEN
**Coverage Atlas Phase 2b: LLM tour/thread draft-proposal CLI (machine proposes, curator disposes)**
**Owner:** None

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
### 📋 T-PTG-054 · P2 · ANY · OPEN
**Coverage Atlas Phase 2a: tours/threads schema + curator admin page**
**Owner:** None

**Scope:**
- Spec: section 4 of docs/superpowers/specs/2026-08-17-coverage-atlas-design.md. New migration (020): tours (id, title, kind ENUM(tour, thread), blurb, status ENUM(draft, published), created_by FK users, timestamps) and tour_articles (tour_id FK CASCADE, article_index_id FK, sort_order, connective_note TEXT; unique (tour_id, article_index_id)). Additive-only, mirrors 018's conventions.
- Curator admin page (admin_tours.php, following admin_article_index_matrix.php's auth + no-framework pattern): list tours with status; create/edit a tour (title, kind, blurb); add/remove/reorder articles by searching the article_index (title/ author/issue search, same client-side approach as the matrix page); edit each stop's connective_note; draft/publish toggle. Only status=published tours are ever visible to member-facing pages (enforced in queries, not just UI).
- Write endpoints follow the pure-handler + LIBRARY_ONLY + CSRF pattern (api/toggle_article_index_topic.php is the closest template).

**Definition of Done:**
- Migration 020 applies cleanly via cli/migrate.php on the local test DB.
- Handler tests prove - create tour, add three articles with order, reorder, edit connective_note, publish; CSRF rejection; draft tours excluded by the member-visibility query helper.
- Curator page browser-verified locally (create a 3-stop tour end to end).
- Golden hammer suite passes with zero regressions; php -l clean.

---
### 📋 T-PTG-056 · P2 · ANY · OPEN
**Coverage Atlas Phase 2c: member-facing tour pages with closing quiz + radar integration**
**Owner:** None

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
