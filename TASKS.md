# 📋 Task Board

*(Auto-generated. Do not edit manually. Use `./bin/fleet` commands to transition tasks.)*

## 🕸️ Task Dependency Graph

```mermaid
graph TD
    classDef done fill:#d4edda,stroke:#28a745,color:#000;
    classDef blocked fill:#f8d7da,stroke:#dc3545,color:#000;
    classDef review fill:#fff3cd,stroke:#ffc107,color:#000;
    classDef active fill:#cce5ff,stroke:#007bff,color:#000;
    T-PTG-012["T-PTG-012<br/>Finish and ship the color-schemes feature — Tasks 3-9 of the existing plan are unstarted, nothing member-facing has shipped"]:::done
    T-PTG-004["T-PTG-004<br/>Audit citation metadata accuracy: volume/issue-number mismatches between issue_label and title"]:::review
    T-PTG-008["T-PTG-008<br/>Tag-triggered feature-request conversation lane, parallel to the citation-grounded RAG pipeline"]:::done
    T-MIN-017["T-MIN-017<br/>Apply D4 — Cavalier/Knight naming policy (write policy + audit four cavalier registry rows)"]:::done
    T-MIN-016 --> T-MIN-017
    T-MIN-001["T-MIN-001<br/>Initialize the Virtual Master Sheet Web Grid"]:::done
    T-MIN-016["T-MIN-016<br/>Apply D3 — rename TRUMP-FOOL to SPECIAL-FOOL, sort_order 0, permanent alias"]:::done
    T-PTG-009["T-PTG-009<br/>Feature-request tag router misses no-space variant, misrouting real member intent into RAG"]:::done
    T-PTG-005["T-PTG-005<br/>Voicing-technique continuity + citation-format test matrix (all preset x tier combos)"]:::review
    T-PTG-013["T-PTG-013<br/>Theme picker doesn't visibly recolor changelog.php (and 5 other pages) due to uncached-bust journal-chat.css links"]:::done
    T-MIN-020["T-MIN-020<br/>Fix grep-A20 verification-window fragility on SPECIAL-FOOL's aliases field in the master registry JSON"]:::done
    T-INTY-021["T-INTY-021<br/>Local dev DB fallback hardcodes nonexistent caut_sfusd, breaking phpunit baseline"]:::done
    T-MIN-011["T-MIN-011<br/>Author the arie batch fresh — five celestial trump personality studies (TRUMP-36..40)"]:::done
    T-MIN-007["T-MIN-007<br/>Triage the eleven GUIDEBOOK files from the fleet sweep"]:::review
    T-PTG-014["T-PTG-014<br/>Add an admin 'reply to conversation' tool, then use it to notify conversation 51 that color schemes shipped"]:::review
    T-PTG-002["T-PTG-002<br/>Stop citing every retrieved chunk — only cite what the model actually referenced"]
    T-PTG-001 --> T-PTG-002
    T-INTY-017["T-INTY-017<br/>Piano Dossier Data Entry Interface (Modern EAV)"]:::review
    T-PTG-003["T-PTG-003<br/>Lock in citation-numbering fix with a real-shape regression fixture"]
    T-PTG-001 --> T-PTG-003
    T-PTG-002 --> T-PTG-003
    T-PTG-015["T-PTG-015<br/>JournalGPT v3 Phase 0: build the 30-50 example benchmark of disappointing interactions (gates all later v3 phases)"]
    T-MIN-006["T-MIN-006<br/>Triage the fleet sweep's untouched personality drafts (rulers, Fool, arie)"]:::done
    T-INTY-020["T-INTY-020<br/>Design (not build) nightly sync of Gazelle service history keyed on gazelle_id"]:::review
    T-INTY-018 --> T-INTY-020
    T-INTY-019["T-INTY-019<br/>'Open in Gazelle' deep-link button on the Piano Dossier page"]
    T-INTY-018 --> T-INTY-019
    T-MIN-013["T-MIN-013<br/>Design the light-tier suit-card study format (spec + two pilot cards)"]:::review
    T-MIN-009["T-MIN-009<br/>Verify the zodiac batch's UNVERIFIED doctrine locators"]:::done
    T-MIN-005 --> T-MIN-009
    T-PTG-016["T-PTG-016<br/>SECURITY: admin_reply.php lets any logged-in member post fake assistant messages into ANY member's conversation (IDOR)"]
    T-PTG-001["T-PTG-001<br/>Fix footnote list numbering to match inline citation markers"]:::review
    T-MIN-008["T-MIN-008<br/>Pin down Bernardi's verzicola boundary from the 1790 rules directly"]
    T-MIN-012["T-MIN-012<br/>Author the Papi/Fool batch — TRUMP-01/02/04 and the Fool fresh, TRUMP-03 corrections applied"]:::done
    T-INTY-018["T-INTY-018<br/>Add dedicated gazelle_id column, decoupled from piano_code"]:::review
    T-MIN-019["T-MIN-019<br/>Apply the Bernardi verzicola reconciliation queue — hedge-phrase citation fix only"]:::done
    T-PTG-006["T-PTG-006<br/>Enhanced multi-turn conversational-quality testing system (Golden Hammer deep dive)"]:::done
    T-PTG-010["T-PTG-010<br/>Contributor index — answer authorship count/ranking questions from a real entity index instead of hedging"]:::review
    T-MIN-003["T-MIN-003<br/>Apply the 93 pending card renames already recorded in ledger.json"]:::review
    T-MIN-015["T-MIN-015<br/>Reconcile the Papi/Fool batch's deferred arie edges now that T-MIN-011 is merged"]:::done
    T-MIN-014["T-MIN-014<br/>Write back resolved dispositions into the Quarantine Register (CW-5/6/7/10 and their QC rows)"]:::done
    T-MIN-002["T-MIN-002<br/>Add card-identification write path to minchiate_reviewer.py"]:::done
    T-PTG-011["T-PTG-011<br/>'Good Answer' upvote click fails in production with 'Invalid or missing CSRF security token'"]:::done
    T-PTG-007["T-PTG-007<br/>Aggregate/statistical question handling (5th cognitive mode) — frequent contributors scenario"]:::done
    T-MIN-018["T-MIN-018<br/>Attempt direct web access to Bernardi 1790 (archive.org) to resolve the verzicola boundary before requiring a human download — supersedes T-MIN-008"]:::done
```

---


## Repo: `intypiano`

### ✅ T-INTY-021 · P0 · ANY · DONE
**Local dev DB fallback hardcodes nonexistent caut_sfusd, breaking phpunit baseline**
**Owner:** Worker-DBFallback1

**Scope:**
- Confirmed by reading classes/core/DatabaseManager.php lines 251-294 directly (not by inference): the localhost/127.0.0.1 branch (line 251) enters a sub-branch at line 267 (`if (isset($this->app->app) && $this->app->app== "cauttools")`) that is NOT a rare edge case -- `classes/redditlite_base.php` line 8 sets `public $app="cauttools";` as the class default, and essentially every entry point in the app (`admin_header_base.php` line 15, `admin/v2/_guard.php` line 17, `scripts/migrate.php`, most of `api/*.php`, and the PHPUnit `Integration` tests) explicitly re-sets `$r->app = "cauttools"` anyway. This branch is the normal path for local dev and CI, not an exception.
- Within that sub-branch (lines 272-291), `$_SERVER['SERVER_PORT']` selects the database: ports 8001-8010 map to `caut_demo01`..`caut_demo10` (the demo-pool infrastructure from the 2026-08-11 multi-tenant work, commit 8dbcaeb9) -- this part is legitimate and working. Every other port, including 2027 (the port CLAUDE.md and the whole PHPUnit suite standardize on, and the port `php -S localhost:2027 -t .` binds), falls into the `else` at line 278 and hardcodes `$db = "caut_sfusd"`. `config.php`'s `$db_configs['sfusd']` override (checked at lines 283-290) also resolves to `caut_sfusd` -- confirmed by reading config.php, so it provides no escape hatch locally.
- Confirmed `caut_sfusd` does not exist as a local database and nothing in the repo suggests it ever should on port 2027 -- `git blame` on lines 267-291 attributes the entire cauttools sub-branch to commit 8dbcaeb9 (2026-08-11, "Demo pool: ten pre-built slots, hostname mapping, and a 14-day reset"), i.e. the `caut_sfusd` hardcoded else-default was introduced at the same time as the demo-pool port logic, not inherited from older working code. There is no earlier commit where this fallback pointed anywhere else. CLAUDE.md is explicit that the local dev server should hit `intypiano_demo` ("The server hits `intypiano_demo`... Local login for the v2 admin: `cmiller` / `localdev1` on `intypiano_demo`"), and `intypiano_demo` does exist locally per the same doc.
- Confirmed this is NOT v2-admin-scoped: `admin_header_base.php` (the V1 admin gate) sets `$r->app = "cauttools"` and calls `$r->init()` exactly the same as `admin/v2/_guard.php` does, so V1 admin pages hit the identical broken fallback on port 2027. Blast radius is the whole local/CI test run, which matches the observed jump from the documented baseline (259 tests, 0 failures) to the current run (330 tests, 18 errors, 114 failures, 6 skipped) and the literal `Unknown database 'caut_sfusd'` fatal thrown from `classes/core/DatabaseManager.php:307` when hitting `admin/v2/piano.php` directly.
- The fix must be minimal and targeted: change ONLY the else-branch default at line 278-280 (and, if needed, whether the config.php sfusd override at lines 283-290 should still apply on this port) so that the standard local dev port (2027, and any non-demo-pool port covered by this branch) resolves to `intypiano_demo` instead of the hardcoded `caut_sfusd`. Do NOT rip out or restructure the `if (isset($this->app->app) && $this->app->app=="cauttools")` gate itself, and do NOT touch the `$server_port >= 8001 && $server_port <= 8010` demo-pool dispatch (lines 274-277) -- that is working multi-tenant infrastructure serving a different, unrelated purpose (the ten `demo01`..`demo10` slots) and must be left exactly as-is.
- Credentials: the demo-pool branch uses `root`/`root` (lines 268-269, set before the port check, so it already applies to the else-branch too) -- confirm during implementation whether `intypiano_demo` uses those same local credentials or needs its own, and set username/password/db together rather than leaving a mismatched combination.
- Out of scope: do not touch the non-localhost branches (sfusd.cauttools.com, unm.cauttools.com, demo01.cauttools.com, uh-test.cauttools.com, etc. -- lines 152-249), do not touch config.php or config_template.php, and do not investigate or fix the separate MAMP-port fallback at line 316 unless it turns out to be entangled with this fix.

**Definition of Done:**
- A fresh `./vendor/bin/phpunit` run (against `php -S localhost:2027 -t .` serving `intypiano_demo`, per CLAUDE.md) shows the error/failure count drop substantially from the current 18 errors / 114 failures -- the DoD is not satisfied by a partial improvement that still leaves `Unknown database` as a live cause of failures.
- Directly hitting `admin/v2/piano.php` (or any other admin/v2/* page) on localhost:2027 no longer throws `Uncaught mysqli_sql_exception: Unknown database`.
- The demo-pool ports (8001-8010) are verified unaffected: the fix did not alter `$server_port >= 8001 && $server_port <= 8010` or the `caut_demoNN` mapping it produces.
- The four "original localhost" ports/hosts in the outer branch (lines 251) that are not port 2099/8888/3031 -- confirm the fix does not regress the pre-existing `game_people` DB path used by those, since the cauttools sub-branch only fires when `$this->app->app=="cauttools"`, which is not every caller.

*Audited against SHA:* `3cf4775d3561b3746c6e55586921beb4492ec57d`

---
### ⏳ T-INTY-018 · P1 · ANY · HUMAN_REVIEW
**Add dedicated gazelle_id column, decoupled from piano_code**
**Owner:** Worker-Gazelle1

**Scope:**
- Verified live in intypiano_demo (which is anonymized production data, so this is not hypothetical) - all 126 inventory.piano_code values already look like Gazelle "Piano ID" strings (e.g. '110641', '110801', '152964'), not QR-specific codes. import_sfusd.php lines 31, 41-44 confirm the mechanism - it reads the Gazelle CSV's 'Piano ID' column and writes it straight into inventory.piano_code on import. So piano_code is silently overloaded today - it is simultaneously the QR lookup key AND the raw Gazelle identifier - and the user has rejected reusing it further, wanting a dedicated gazellecode (gazelle_id) column instead.
- CRITICAL - piano_code is not just a database key, it is physically printed on QR labels already deployed on real pianos. qr_report_generator.php, qr_avery5162_poc.php and piano/index.php all resolve piano_code to a piano via '/piano/{piano_code}' links baked into printed/laminated QR codes (see PIANO_QR_SETUP.md, 'Test 2 - View Piano Landing Page'). Do NOT regenerate or overwrite existing piano_code values - that breaks every QR code already taped to an instrument. The correct migration is additive - backfill the new gazelle_id column by COPYING the current piano_code value (since today they are identical for existing rows), not by moving/renaming the column.
- There are two tables that both currently carry piano_code and need the same treatment - v1 inventory (VARCHAR, no visible unique constraint found in this scout pass - confirm before writing DDL) and v2 pianos (ddl/132/001_v2_schema.sql line 37, VARCHAR(24) NULL, with UNIQUE KEY uniq_piano_code line 49). Note also that ddl/132/004_map_pianos.sql is the ONE-TIME migration that originally populated pianos.piano_code from inventory - this scout pass found no ongoing sync job between the two tables, so confirm whether new inventory rows (e.g. from a future SFUSD-style import) ever reach v2 pianos at all, and whether gazelle_id needs backfilling on both tables or whether v2 pianos is the only target that matters going forward (see docs/experts/schema-catalog.md v2 row).
- New ddl migration - next sequential directory after ddl/145 (currently ddl/145/001_piano_floor.sql + 002_verify.php is the highest). Follow that file's exact pattern - one ALTER TABLE per .sql file, a companion NNN_verify.php, comment block explaining why. Add 'gazelle_id VARCHAR(24) NULL' (match piano_code's width unless investigation shows Gazelle IDs run longer) to pianos (and inventory if the sync question above resolves that inventory still matters), with an index - decide UNIQUE vs plain KEY based on whether Gazelle IDs are confirmed globally unique (a duplicate/failed unique constraint would break future imports, so verify before choosing UNIQUE).
- Per CLAUDE.md - never use DatabaseManager::dosql() in migration code, use getConnection()->query(). Strict SQL mode stays on - do not add SET SESSION sql_mode='' to make a coercion pass. Never target unm_piano, unm_piano_readonly or unm_piano_test.
- Update import_sfusd.php to populate the new gazelle_id column with $piano_id going forward. Decide and document explicitly what piano_code should hold for NEW rows once gazelle_id exists (options - leave piano_code populated with the same Gazelle ID as before for continuity with the existing QR scheme, or start assigning piano_code independently at label-printing time - this is a product decision, not just a schema one, so state the chosen behavior in the PR/commit rather than silently picking one).
- Backfill existing rows - UPDATE gazelle_id = piano_code for all rows where piano_code looks like a Gazelle ID pattern (investigate whether any current piano_code values are NOT Gazelle IDs - e.g. hand-assigned QR codes for pianos with no Gazelle record - before blanket-copying every row).

**Definition of Done:**
- New ddl/<next>/001_*.sql adds gazelle_id to pianos (and inventory if in scope per the sync investigation above), with a verify script following the ddl/145 pattern, runnable via scripts/migrate.php against intypiano_demo (never unm_piano/unm_piano_readonly/unm_piano_test).
- Existing piano_code values are provably unchanged after migration - a before/after diff of SELECT id, piano_code FROM pianos shows zero modified rows, and qr_avery5162_poc.php / piano/index.php still resolve every existing piano_code to the same piano (spot-check at least 3 real codes from intypiano_demo).
- gazelle_id is populated for all rows where the investigation confirms piano_code currently holds a Gazelle ID (expected ~126/126 in demo data today, but confirm rather than assume 100%).
- import_sfusd.php writes gazelle_id going forward; the chosen behavior for piano_code on new imports is explicitly documented in the commit message.
- ./vendor/bin/phpunit does not introduce NEW failures/errors beyond the PM-captured baseline below. PM AUDIT NOTE (2026-08-12, repo-sha 3cf4775d) - CLAUDE.md's documented "259 tests, 0 failures" baseline is currently STALE and NOT reproducible. A clean run on this exact SHA (php -S localhost:2027 -t ., then ./vendor/bin/phpunit) produced Tests=330, Assertions=564, Errors=18, Failures=114, Skipped=6. This is a pre-existing regression, unrelated to Gazelle/gazelle_id - traced to admin/v2/* pages 500ing locally ("Uncaught mysqli_sql_exception - Unknown database 'caut_sfusd'" out of classes/core/DatabaseManager.php:307) since the new multi-tenant config.php/ DatabaseManager dispatch landed 2026-08-11 (commits 40d00b89..4751c925). Reproduced 3 independent ways (fresh php -S process, direct curl to admin/v2/piano.php, and a standalone PHP CLI simulation) - this is not an artifact of a stale/duplicate local server process. Do NOT let a Worker "fix" this DatabaseManager/config.php regression as part of this task - it is a separate, unrelated bug; file it as its own task instead. The Worker's bar for this task is - the SAME 330/18/114/6 shape (or better) after adding gazelle_id, not the stale 259/0 figure in CLAUDE.md.

*Audited against SHA:* `3cf4775d3561b3746c6e55586921beb4492ec57d`

---
### ⏳ T-INTY-017 · P1 · ANY · PEER_REVIEW
**Piano Dossier Data Entry Interface (Modern EAV)**
**Owner:** TaskForce

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
- m
- o
- d
- e
- r
- n
- i
- z
- e
- d
-  
- E
- A
- V
-  
- a
- r
- c
- h
- i
- t
- e
- c
- t
- u
- r
- e
-  
- f
- o
- r
-  
- c
- o
- l
- l
- e
- c
- t
- i
- n
- g
-  
- d
- e
- t
- a
- i
- l
- e
- d
-  
- P
- i
- a
- n
- o
-  
- c
- o
- n
- d
- i
- t
- i
- o
- n
-  
- d
- o
- s
- s
- i
- e
- r
- s
- ,
-  
- b
- a
- s
- e
- d
-  
- o
- n
-  
- t
- h
- e
-  
- S
- t
- a
- n
- f
- o
- r
- d
-  
- T
- e
- m
- p
- l
- a
- t
- e
-  
- P
- D
- F
- .
- 

- I
- n
- c
- l
- u
- d
- e
- s
-  
- s
- c
- h
- e
- m
- a
-  
- (
- `
- d
- o
- s
- s
- i
- e
- r
- _
- f
- i
- e
- l
- d
- _
- d
- e
- f
- i
- n
- i
- t
- i
- o
- n
- s
- `
- ,
-  
- `
- p
- i
- a
- n
- o
- _
- d
- o
- s
- s
- i
- e
- r
- s
- `
- ,
-  
- `
- p
- i
- a
- n
- o
- _
- d
- o
- s
- s
- i
- e
- r
- _
- v
- a
- l
- u
- e
- s
- `
- )
- ,
-  
- 

- a
-  
- m
- o
- b
- i
- l
- e
- -
- f
- i
- r
- s
- t
-  
- d
- a
- t
- a
-  
- e
- n
- t
- r
- y
-  
- i
- n
- t
- e
- r
- f
- a
- c
- e
-  
- (
- `
- a
- d
- m
- i
- n
- /
- v
- 2
- /
- d
- o
- s
- s
- i
- e
- r
- _
- e
- d
- i
- t
- .
- p
- h
- p
- `
- )
-  
- w
- i
- t
- h
-  
- s
- e
- g
- m
- e
- n
- t
- e
- d
-  
- t
- o
- u
- c
- h
- -
- f
- r
- i
- e
- n
- d
- l
- y
-  
- g
- r
- a
- d
- i
- n
- g
-  
- b
- u
- t
- t
- o
- n
- s
- ,
-  
- 

- a
- n
- d
-  
- i
- n
- t
- e
- g
- r
- a
- t
- i
- o
- n
-  
- i
- n
- t
- o
-  
- t
- h
- e
-  
- e
- x
- i
- s
- t
- i
- n
- g
-  
- V
- 2
-  
- p
- i
- a
- n
- o
-  
- v
- i
- e
- w
-  
- (
- `
- a
- d
- m
- i
- n
- /
- v
- 2
- /
- p
- i
- a
- n
- o
- .
- p
- h
- p
- `
- )
- .
- 


**Definition of Done:**

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
### ⏳ T-INTY-020 · P3 · ANY · HUMAN_REVIEW
**Design (not build) nightly sync of Gazelle service history keyed on gazelle_id**
**Owner:** Worker-GazelleSync1

**Scope:**
- This is a research/design task, not a build task. Do not write a sync job or cron script under this task. The original proposal (a prior Gemini/ Antigravity session, endorsed by the user in principle) wants a nightly sync of volatile Gazelle data - service history, tuning dates, condition reports - pulled into intypiano and keyed on the new pianos.gazelle_id column from T-INTY-018.
- PM AUDIT CORRECTION (2026-08-12) - the scout's framing that "Gazelle API access was never confirmed to exist" is WRONG and stale as of this repo-sha. classes/integration/GazelleAPI.php (added in commit 1ea83713, the same commit the scout cites) is a working private GraphQL client (https://gazelleapp.io/graphql/private) with a confirmed READ query (allPianos) and a confirmed WRITE mutation (updatePiano), already wired up and used in production by admin/v2/normalization.php's "Mass Edit" tool. API access is confirmed to exist. Do NOT scope this task as "determine whether an API exists" - go read those two files first.
- The REAL open question this design doc should answer instead - today's GazelleAPI usage takes a per-request, admin-pasted `gazelle_api_key` typed into a form field (see admin/v2/normalization.php lines ~18-83); there is no stored/persisted service-account credential anywhere in the repo. A nightly cron job has no admin sitting at a keyboard to paste a key each run, so the design doc must cover where that credential would live (config_local.php- style gitignored file? a new `gazelle_credentials` table? an env var?) and how it avoids the fate of the API-token bearer-secret pattern already used by api/v1/admin/logRefill.php (config/api_token.php, gitignored, INTYPIANO_API_TOKEN env override).
- Also flag explicitly - the existing GraphQL API is NOT read-only. It has a live `updatePiano` mutation capable of overwriting Gazelle's own data. A nightly sync job pulling FROM Gazelle should almost certainly restrict itself to the read-only `allPianos`-style query and never call the mutation path, but this is a design decision the doc must state explicitly, not something to leave implicit - a future Worker copy-pasting GazelleAPI.php usage could otherwise wire up writes by accident.
- The deliverable is a written design doc (per this repo's expert-page convention, likely docs/experts/gazelle-sync.md or under task_coordinator's Dewey Decimal 20-Architecture/ per that repo's own doc rules) covering - what data Gazelle can realistically expose beyond GazelleAPI.php's current make/model fields (does allPianos or a sibling query already return service history / tuning dates / condition reports, or only the make/model fields the Normalization tool uses - check the GraphQL schema, don't assume), how conflicts are resolved when both intypiano and Gazelle have edited the same piano's data since last sync (the original proposal's "detecting remote edits" item was deliberately NOT scoped as a task here - flag it as an open question this design doc should surface, not solve), what fields sync one-way vs. need human reconciliation, and what a minimal V1 sync would touch (proposed - only pianos rows where gazelle_id IS NOT NULL, from T-INTY-018).
- Do not scope pushing intypiano invoices/data back to Gazelle - that is a separate, more speculative future phase explicitly deferred by this scout pass (see feedback file), not by accident.

**Definition of Done:**
- A written design doc exists (exact location per whichever repo's doc convention applies - confirm intypiano has no equivalent Dewey rule before defaulting to task_coordinator's). It must not re-litigate whether Gazelle API access exists (confirmed - classes/integration/GazelleAPI.php, a working private GraphQL client already used in production by admin/v2/normalization.php). It must state clearly (a) what fields that API actually exposes today vs. what a nightly sync would need, (b) where a persisted service-account credential for an unattended cron job would live, since today's only working credential flow is an admin pasting a key per request, and (c) that the sync must be read-only against Gazelle even though the client library exposes a write mutation.
- The doc names which specific fields (service history, tuning dates, condition reports) are in scope for a V1 sync and which are deferred.
- The doc explicitly notes conflict/remote-edit detection as unsolved and out of scope for V1, so a future PM does not assume it was silently handled.
- No production code, migration, or cron job is added under this task - if the investigation finds enough clarity to justify a build, that becomes a new task, not scope creep on this one.

*Audited against SHA:* `3cf4775d3561b3746c6e55586921beb4492ec57d`

---

## Repo: `minchiate_tarot`

### ✅ T-MIN-001 · P1 · ANY · DONE
**Initialize the Virtual Master Sheet Web Grid**
**Owner:** Worker-1

**Scope:**
- Create the base minchiate_reviewer.py application.
- Load the 97 extracted images and sort them geographically by their filename prefix.
- Serve a dynamic web grid layout reflecting the original master sheet.

**Definition of Done:**
- Server runs locally without errors.
- Renders a grid of 97 images in their stitched order in the browser.

*Audited against SHA:* `b51d4e4`

---
### ✅ T-MIN-011 · P1 · ANY · DONE
**Author the arie batch fresh — five celestial trump personality studies (TRUMP-36..40)**
**Owner:** Worker-F11

**Scope:**
- Write five personality studies fresh — TRUMP-36 Star, TRUMP-37 Moon, TRUMP-38 Sun, TRUMP-39 World, TRUMP-40 Trumpets — to research/pilots/ARIE_BATCH_BRIEF.md (read it in full first; its required-reading list is binding). The archived fleet drafts in research/archive/failed-runs/ are inputs at most, NEVER base text; every card is written fresh to the brief.
- Work in waves (one or two) with an adversarial per-wave verification pass, on the ZODIAC_BATCH_BRIEF pattern that produced the verified 12-study zodiac batch; within-wave symmetry must be flagged for the verifier.
- Known trap (binding): the arie are unnumbered — registry historical_number is "unnumbered arie" for all five; XXXVI-XL and rank 36-40 are project bookkeeping (editorial only), stated in the secure core and never presented as printed fact.
- Known trap (binding): TRUMP-40 naming is Moderate confidence with Trombe / Trumpets / Fame / Fama / Last Judgment as recorded variants — disclose all of them, but never assert "Judgement as universal original title" and never smuggle the withdrawn summons/eschatology reading in structurally (CW-10 requires a §0 disposition that keeps the naming question open).
- Known trap (binding): NO pricing amounts for the arie. Bernardi 1790 transcription is bounded at XXVII (JUS-C006, pilot L80) — the arie are outside it; Minucci 1688 gives special value with no amounts (DEA-C004, exemplary list). Any specific amount must cite a real opened source or not appear; otherwise [UNVERIFIED] and queued in §5.
- The Quarantine Register rows QC-077 through QC-089 and CW-10 must each be dispositioned per card, with one owner per collective row (QC-077..080) and siblings citing the owner; committed studies' current text is the authority over register summary rows. Answer Gemini GEM-C016 (Star) on the record.
- Claim namespaces STA-/MOO-/SUN-/WOR-/TRO- only; never mint QC-### ids; no methodology stamps or YAML frontmatter; match the committed header format.

**Definition of Done:**
- Five files exist at research/pilots/drafts/PERSONALITY_TRUMP-36_Star.md, PERSONALITY_TRUMP-37_Moon.md, PERSONALITY_TRUMP-38_Sun.md, PERSONALITY_TRUMP-39_World.md, and PERSONALITY_TRUMP-40_Trumpets.md, each meeting the brief's output spec (~250-450 lines, §0 register disposition, secure core with recomputed ranks and two-witness scoring record, unnumbered-arie disclosure, project reading, §3 relationships, §4 open questions, §5 reviewer checklist, claims table with split confidence).
- No file contains an arie pricing amount without a real opened-source citation; no file presents XXXVI-XL as a printed number; TRUMP-40 contains no summons reading and no Judgement-as-original-title claim.
- A batch verification report in research/pilots/ records the adversarial per-wave pass, including diffs against the archived failed drafts confirming no clone text.

*Audited against SHA:* `f8bb1b8`

---
### ✅ T-MIN-012 · P1 · ANY · DONE
**Author the Papi/Fool batch — TRUMP-01/02/04 and the Fool fresh, TRUMP-03 corrections applied**
**Owner:** Worker-F12

**Scope:**
- Write four personality studies fresh — TRUMP-01 Ganellino, TRUMP-02 Ruler, TRUMP-04 Ruler, and TRUMP-FOOL — to research/pilots/PAPI_FOOL_BATCH_BRIEF.md (read it in full first; its required-reading list is binding). The archived fleet drafts in research/archive/failed-runs/ are inputs at most, NEVER base text.
- TRUMP-03 is NOT rewritten: it was the triage KEEP. Apply its five queued corrections from the brief in place (re-source RUL3-C004/C005 to pilot L92 and JUS-C006/DEA-C004; resolve the Papi-membership wobble into sourced usage facts; add the Minucci record with the exemplary-list caveat; regrade the capture/sacrifice claim [F] to [SI]; extend toward the committed 210-271-line standard), matching its existing style and keeping its RUL3- namespace.
- Known trap (binding): naming confidence is the block's defining fact — Low for II-IV, Low-Moderate for I (Ganellino/Papino/Bagatto/Little Juggler), High for the Fool. Disclose per card in the secure core, carry each card's names_to_avoid, and invent no titles — the archived drafts minted "Papa Due" and "Papo"; the registry says Sovrano for II-IV.
- Known trap (binding): the Fool's special value has NO amount in any real source — Minucci 1688 gives special value with no amount (DEA-C004); "5 points" has no corpus source and must not appear except as [UNVERIFIED]. Fool rewrite confronts CW-5 rather than inheriting it: disposition QC-043 through QC-050 row by row against each committed study's current text, and keep unranked-in-play / unnumbered-on-card / sort-57-bookkeeping as three distinct statements.
- Known trap (binding): respect the VI-XII Papi terminology rule — Bernardi calls VI-XII Papi by number too (JUS-C005), and prices I at five points, II-V at three (JUS-C006, pilot L80; transcription bounded at XXVII); the Papi-block boundary is usage-dependent and stays partly open. No identity claims (gender, regalia, posture) above [U] until crops exist — IMG-001 blocks G2 deck-wide; no "Gate-passed" claims.
- Claim namespaces GAN-/RUL2-/RUL4-/FOO- only; never mint QC-### ids; reciprocate or dispute the committed Love→Rulers rival edge (QC-053/054) with one owner for the collective row; edges to the arie (parallel batch, T-MIN-011) are offered-not-imposed on the AIR-C011 model. Waves of 2-3 with adversarial per-wave verification.

**Definition of Done:**
- Four fresh files exist at research/pilots/drafts/ for TRUMP-01, TRUMP-02, TRUMP-04, and the Fool, each meeting the brief's output spec (~250-450 lines, §0 register disposition, secure core with recomputed ranks and two-witness scoring record, naming-confidence disclosure, project reading, §3 relationships, §4 open questions, §5 reviewer checklist, claims table with split confidence).
- The existing PERSONALITY_TRUMP-03 file carries all five queued corrections, verified line by line against the brief's correction list.
- No file contains an invented Italian title, a Fool point amount stated as fact, or a Gate-passed claim; the VI-XII Papi terminology facts appear sourced, not asserted.
- A batch verification report in research/pilots/ records the adversarial per-wave pass, including diffs against the archived failed drafts confirming no clone text.

*Audited against SHA:* `f8bb1b8`

---
### ✅ T-MIN-002 · P1 · ANY · DONE
**Add card-identification write path to minchiate_reviewer.py**
**Owner:** Worker-F14

**Scope:**
- On branch test-T-MIN-001, minchiate_reviewer.py was rewritten from Flask to stdlib http.server (commits 1eb6550, 0509f69). The rewrite dropped the old Flask app's /api/update and /api/confirm POST routes entirely — the new ReviewerHandler implements only do_GET, no do_POST — so the running server is now read-only.
- CARD_REVIEW_PROCESS_AND_IDENTIFYING.md Step 2-4 and its "Next Steps" section explicitly define the reviewer app's purpose as letting a user click a card in the grid, assign its identity (Suit/Rank or Trump number), persist that judgment to ledger.json, and rename the underlying file to its archival name (e.g. Cups_03.jpg). None of that is implemented in the current read-only build.
- Add a do_POST handler (or equivalent) to ReviewerHandler exposing at least an update-identity endpoint that accepts an original_name/current_name plus type+value, validates against a target filename collision, renames the file under research/evidence/cards_raw/, updates ledger.json (identified, type, value, current_name), and returns JSON — matching the semantics the old Flask /api/update route had, but implemented stdlib-only per this branch's existing "no Flask/Jinja2" design constraint stated in the module docstring.
- Wire minimal client-side interaction in render_grid_html's output (a click handler / small inline form per card, or a simple prompt-based flow) so the identification can actually be entered from the browser, not only via curl.

**Definition of Done:**
- POST request to the new endpoint with a valid original_name/type/value updates ledger.json's identified/type/value fields and renames the file on disk, verified by re-reading ledger.json and os.path.exists on the new name.
- A request naming a target filename that already exists on disk is rejected (no rename performed, no file clobbered) with a non-200 response.
- Grid page loaded after an update reflects the new identity without manual ledger editing.
- python3 minchiate_reviewer.py --check still exits 0 (existing read-path behavior is not broken).

*Audited against SHA:* `0509f6914e201ba192717c7a90c3c4154e5120fc`

---
### ⏳ T-MIN-003 · P1 · ANY · HUMAN_REVIEW
**Apply the 93 pending card renames already recorded in ledger.json**
**Owner:** Worker-F17

**Scope:**
- Verified by inspection of ledger.json on branch test-T-MIN-001 (worktree checkout of commit 0509f69): 93 of the 97 cards already carry identified: true, human_confirmed: true, and a populated type/value (Trump/Cups/Swords/ Batons/Coins + rank), but current_name still equals original_name for all 93 — meaning research/evidence/cards_raw/ still holds them under their raw geographic extraction filenames (e.g. 830124001_card_05.jpg) instead of their standardized archival names (e.g. Swords_6.jpg). Only 4 of 97 cards have actually been renamed.
- CARD_REVIEW_PROCESS_AND_IDENTIFYING.md Step 4 ("Final Standardization") defines this rename as the completion step of the identification workflow. The identification judgment work is already done and sitting unused in the ledger; this task is purely to apply it.
- Write a small one-shot script (e.g. finalize_identifications.py, following the pattern of the existing single-purpose scripts in the repo root such as dedupe_cards.py) that, for every ledger entry where identified is true and current_name == original_name, computes the target archival filename (Trump_N.jpg / <Suit>_N.jpg per the existing /api/update naming convention in git history at 2c233c4^:minchiate_reviewer.py), renames the file under research/evidence/cards_raw/, and updates current_name in ledger.json.
- Must refuse (log and skip, not crash) any rename whose target filename already exists, and must be safely re-runnable (a second run against an already-finalized ledger is a no-op).

**Definition of Done:**
- Running the script against the current ledger.json + cards_raw/ renames all 93 pending files to their archival names and updates ledger.json's current_name for each.
- Re-running the script immediately afterward makes zero further changes (idempotent), verified by hashing ledger.json / directory listing before and after the second run.
- No target-name collision silently overwrites an existing file.
- python3 minchiate_reviewer.py --check still exits 0 afterward (renamed files still resolve to their sheet geography via original_name's 9-digit prefix, which the sort key already reads from original_name rather than current_name).

*Audited against SHA:* `0509f6914e201ba192717c7a90c3c4154e5120fc`

---
### ✅ T-MIN-016 · P2 · codex · DONE
**Apply D3 — rename TRUMP-FOOL to SPECIAL-FOOL, sort_order 0, permanent alias**
**Owner:** Worker-F18

**Scope:**
- PM-F7 ARCHITECTURAL DECISION (audit 2026-08-12, confirmed against branch test @09f857d): verified zero hits for "alias" in research/05-registry-and-audit/ and research/04-dossier-spec/ — the gap is real, not a scout false positive. Fix: add a new OPTIONAL field named `aliases` (a list of strings) to (1) Stage5_Master_Card_Registry.csv as a new trailing column `aliases` (semicolon-separated if multiple, e.g. "TRUMP-FOOL"), (2) the corresponding key in each row object of Stage5_Master_Card_Registry.json, and (3) `administrative_identity.aliases` (type array of strings, optional, NOT in the schema's `required` list) in research/04-dossier-spec/Stage4_Card_Dossier_Schema.json and the matching Card_Dossier_Skeletons.json entries. This ONE mechanism is used for both D3's former-id alias here (SPECIAL-FOOL row gets aliases: ["TRUMP-FOOL"]) and D4's Knight search-alias in T-MIN-017 (which depends on this task and reuses the same field) — do not invent a second, differently-shaped mechanism in either task. Document the field's meaning (one sentence) inline in Stage4_Card_Dossier_Schema.json via a JSON Schema `description` on the new property, and in the registry's own notes/header if the CSV format supports a comment; if not, document it in the same alias note this task already requires.
- PM-F7 FINDING (audit 2026-08-12): Stage4_Card_Dossier_Schema.json's `administrative_identity.sort_order` is constrained `"minimum": 1, "maximum": 97`. Setting sort_order to 0 in Card_Dossier_Skeletons.json's TRUMP-FOOL/SPECIAL-FOOL entry (per this task's own instruction below) will violate that schema constraint as currently written. Required fix: change `"minimum": 1` to `"minimum": 0` on that one property in Stage4_Card_Dossier_Schema.json (a one-line, backward-compatible widening — every other card's sort_order stays >=1 in practice, only the Fool's special-family exception uses 0) so the skeleton entry remains schema-valid. Do this as part of this task, not a follow-up.
- PM-F7 CORRECTION (audit 2026-08-12): PERSONALITY_TRUMP-40_Trumpets.md was spot-checked and contains ZERO literal "TRUMP-FOOL" token occurrences on branch test @09f857d (grep -c returns 0). Its TRO-C002/TRO-C006/TRO-C018 citations and the L272-282 reciprocal-edge prose reference "the Fool" (bare prose) and "FOO-C014" (the Fool study's own claim-id prefix, already independent of the dossier/file id "TRUMP-FOOL"), never the token "TRUMP-FOOL" itself. No id-token edit is needed or expected in this file — do not hunt for one. Leave it completely untouched; it will still satisfy the zero-occurrence verification check trivially. The other ten files in the list below were spot-checked (TRUMP-01, TRUMP-19 read in full; all ten confirmed via `grep -c "TRUMP-FOOL"` returning >=1) and are real, live citations requiring the rename.
- Editorial decision D3 (tasks/human/editorial_decisions_2026-08-12.md) sets the card id to SPECIAL-FOOL, sort_order 0, with a permanent alias from TRUMP-FOOL for backward compatibility. Scout blast-radius grep (branch test) found TRUMP-FOOL as a live PRIMARY identifier in these files, which is the full rename surface: research/05-registry-and-audit/Stage5_Master_Card_Registry.csv (row col 1, card_id), Stage5_Master_Card_Registry.json ("card_id": "TRUMP-FOOL"), and Card_Dossier_Skeletons.json ("dossier_id": "TRUMP-FOOL", "database_id": "TRUMP-FOOL", and the two question_id values TRUMP-FOOL-Q-IMG-001 / TRUMP-FOOL-Q-NAME-001, which must become SPECIAL-FOOL-Q-IMG-001 / SPECIAL-FOOL-Q-NAME-001).
- Rename the id everywhere it is the primary identifier: the registry CSV and JSON rows, the Card_Dossier_Skeletons.json entry (dossier_id, database_id, question_id prefixes), and the committed study file research/pilots/drafts/PERSONALITY_TRUMP-FOOL_Fool.md — including its filename (rename to PERSONALITY_SPECIAL-FOOL_Fool.md) and every place inside it where TRUMP-FOOL is used as the card's own id (e.g. the "Card:" line, FOO-C001/FOO-C003/FOO-C006 evidence-column citations of "TRUMP-FOOL row"/"TRUMP-FOOL blocking_issue").
- Set sort_order to 0 in the registry CSV and JSON and in Card_Dossier_Skeletons.json. Before writing this, re-read FOO-C003 in PERSONALITY_TRUMP-FOOL_Fool.md (soon SPECIAL-FOOL): it already separates three distinct statements — unnumbered on the card, outside the ranked trump ladder (family Special), and sort 57 as project bookkeeping convention ("registry key, may be 0"). Sort_order=0 does not contradict any of the three as currently worded (the file already anticipates sort key 0). Update the sort-order number in FOO-C001/FOO-C003 prose from 57 to 0 while preserving the three-statement distinction verbatim in substance — do not merge or drop any of the three. If, on closer reading, you find sort=0 DOES contradict one of the three statements as written, do not resolve the contradiction yourself: leave the prose as-is, set sort_order=0 in the registry only, and add a one-line flag in this task's scope-file notes (or a TODO comment) naming the contradiction for human/PM attention.
- Add a documented permanent alias TRUMP-FOOL -> SPECIAL-FOOL. Scout finding: as of 09f857d, NEITHER the registry CSV/JSON schema NOR research/04-dossier-spec/Stage4_Card_Dossier_Schema.json has any alias/former-id/redirect field — grep for "alias" across research/05-registry-and-audit/ and research/04-dossier-spec/ returns zero hits. There is no existing aliasing mechanism to hook into. Do not silently invent a new schema field to paper over this. Required output: add a plain-language, clearly-labeled note (e.g. a "former_id"/"aliases" column added to the registry CSV+JSON+skeleton schema, OR — if a schema change feels too invasive for a rename task — a documented note in the registry's notes field plus a short paragraph in REORGANIZATION_PLAN.md or a new short note under research/05-registry-and-audit/ stating plainly "no alias field exists in the schema; TRUMP-FOOL must be tracked as a former id by [wherever you put it] until a real alias/redirect mechanism is built." Either path is acceptable; but the absence must be visible in the deliverable, not worked around invisibly.
- Update every OTHER committed study file that cites the Fool by its registry row as an evidence source (id-as-citation, not just narrative prose about "the Fool"). Full list found by scout grep on branch test: research/pilots/drafts/PERSONALITY_TRUMP-01_Ganellino.md (GAN-C012), PERSONALITY_TRUMP-02_Ruler.md (RUL2-C012), PERSONALITY_TRUMP-04_Ruler.md (RUL4-C012), PERSONALITY_TRUMP-05_Love.md (LOV-C017), PERSONALITY_TRUMP-09_Wheel_of_Fortune.md (WHE-C014), PERSONALITY_TRUMP-11_Old_Man_Time.md (OLD-C015), PERSONALITY_TRUMP-13_Death.md (DEA-C014), PERSONALITY_TRUMP-14_Devil.md (DEV-C019), PERSONALITY_TRUMP-15_House_of_the_Devil.md (HOU-C018), PERSONALITY_TRUMP-19_Charity.md (CHA-C005, references "TRUMP-FOOL and TRUMP-19" symbol sharing in prose too), and PERSONALITY_TRUMP-40_Trumpets.md (TRO-C002, TRO-C006, TRO-C018 — this file also has a typed reciprocal edge, "Fool -> Trumpets (XL): opposite", in its narrative prose around L272-282 that names the Fool's own claim FOO-C014; update its id citations to SPECIAL-FOOL but do not alter the typed-edge conclusion, grading, or direction). In every one of these files, change only the id token (TRUMP-FOOL -> SPECIAL-FOOL) in citation/evidence columns and any bare id mentions; do not touch surrounding claim text, grading, or conclusions.
- Do NOT touch: research/archive/failed-runs/* (archived/superseded, historical record — leave TRUMP-FOOL as-is there), research/pilots/Papi_Fool_Batch_Verification_Report.md, Quarantine_Register_Outside_Set_Claims.md, Fleet_Sweep_Personality_Triage_Report.md, Wave2_Virtue_Verification_Report.md, SIGNOFF_OPUS5.md, REORGANIZATION_PLAN.md's own body text, tasks/human/*, tasks/agent/*, or any other audit-trail/report/planning document that narrates project history using the old id — these are point-in-time records, not live identifiers, and rewriting them would falsify the audit trail. Also do not touch build_graph_contract.py or research/01-strategy/graph_contract_v1.json / VISUALIZATION_GAPS_IDENTIFIED.md unless doing so is trivially required to keep the id rename internally consistent within this same commit — if unsure, leave code/contract files alone and flag them instead of guessing.
- Do not touch the prose content or claims of any study beyond identifier and sort-order fields — this is a rename, not a rewrite.

**Definition of Done:**
- An optional `aliases` field (list of strings) exists on the SPECIAL-FOOL row in Stage5_Master_Card_Registry.csv and Stage5_Master_Card_Registry.json, and as `administrative_identity.aliases` in Stage4_Card_Dossier_Schema.json (optional, not required) and the SPECIAL-FOOL entry in Card_Dossier_Skeletons.json, containing "TRUMP-FOOL".
- Stage4_Card_Dossier_Schema.json's administrative_identity.sort_order minimum is 0 (widened from 1) so the SPECIAL-FOOL skeleton entry with sort_order 0 validates against the schema.
- Zero occurrences of "TRUMP-FOOL" remain as a primary identifier (card_id/dossier_id/database_id/ question_id prefix/filename/citation token) in Stage5_Master_Card_Registry.csv, Stage5_Master_Card_Registry.json, Card_Dossier_Skeletons.json, and the eleven listed committed drafts files plus the renamed Fool study file; the ONLY acceptable remaining occurrences of the literal string "TRUMP-FOOL" in those specific files are inside a clearly labeled alias/former-id note.
- The registry (CSV + JSON) and Card_Dossier_Skeletons.json all show sort_order/sort key 0 for the Fool/SPECIAL-FOOL row.
- A documented former-id/alias note for TRUMP-FOOL -> SPECIAL-FOOL exists and is discoverable from the registry or its accompanying docs; if no schema aliasing field was added, the absence is explicitly stated in that same note, not silently omitted.
- research/archive/failed-runs/*, the named audit/report/planning files, and any file not explicitly listed in scope are byte-for-byte unchanged (git diff --name-only against the audited sha touches only the files named in scope).
- No claim text, grading, or conclusion in any of the eleven cross-referencing drafts changed beyond the id token itself.

*Audited against SHA:* `09f857d`

---
### ✅ T-MIN-006 · P2 · ANY · DONE
**Triage the fleet sweep's untouched personality drafts (rulers, Fool, arie)**
**Owner:** Worker-F6

**Scope:**
- Verification-triage the ten fleet-sweep personality drafts no verifier has touched; the four ruler studies (PERSONALITY_TRUMP-01 through TRUMP-04, 24-102 lines), the Fool (63 lines), and the five arie (PERSONALITY_TRUMP-36 through TRUMP-40, 31-63 lines).
- Assume the barbell found in the 10 Aug sweep; expect stubs-with-labels, wrong-but- fluent rank claims, and clones. Diff every file against the evidence pilot, the committed studies, and each other before reading on its own terms.
- Sort each file into one of three bins: KEEP (verify and correct to the committed standard), REWRITE (fail it, archive to research/archive/failed-runs/, and write a batch brief on the ZODIAC_BATCH_BRIEF model), or DEFER (record why).
- Mind the standing cautions - registry family field reads Trump for all trumps; the arie are commonly unnumbered so XXXVI-XL are editorial ranks; TRUMP-40 naming is only Moderate confidence (Trombe/Fame/Judgment variants; no Judgement-as-original-title).
- Do not rewrite the studies inside this task; produce the triage report and any needed batch briefs so authoring can be scoped as follow-up tasks.

**Definition of Done:**
- A triage report in research/pilots/ assigns every one of the ten files a bin with evidence (diffs run, ranks recomputed, citations spot-fetched).
- Any file failed as a clone or stub is archived with a disposition note, matching the Justice-clone precedent.

*Audited against SHA:* `c4f389f`

---
### ✅ T-MIN-019 · P2 · ANY · DONE
**Apply the Bernardi verzicola reconciliation queue — hedge-phrase citation fix only**
**Owner:** Worker-F21

**Scope:**
- SCOUT-F5 SOURCE: this task applies the reconciliation queue listed in §5 of research/pilots/Bernardi_1790_Verzicola_Boundary_Resolution_Note.md (T-MIN-018, merged/DONE at commit 4705b31). That note resolved the verzicola upper-sequence boundary to exactly XXVIII (independently confirmed twice from raw archive.org OCR of Bernardi 1790, cap. V/VI + two worked examples in cap. XV and Part II cap. VIII). This task is a CITATION-PRECISION update only: replace the old hedge phrasing with the resolved boundary plus a citation to the resolution note. Do NOT re-litigate, reinterpret, or change any other claim, grading, confidence label, or conclusion in any touched file. If you find yourself wanting to change anything beyond the hedge phrase itself (plus its citation) and, where present, the matching claims-table cell, stop and leave a TODO/flag instead — do not resolve it yourself.
- SCOUT-F5 FINDING — there are TWO textually distinct hedges in this corpus that both mention nearby Roman numerals around XXVII/XXVIII, and only ONE of them is resolved by T-MIN-018. Do not conflate them:
  HEDGE A (IN SCOPE — resolved by T-MIN-018): the verzicola UPPER-SEQUENCE-BOUNDARY hedge, i.e. claims about where Bernardi's higher-trump verzicola examples begin. Phrasings found verbatim in the current test-branch content include "beginning around XXVIII", "about XXVIII upward"/"from about XXVIII upward", "around XXVIII upward", "~XXVIII up"/"from about XXVIII up". Replace these with wording stating the boundary is exactly XXVIII, citing research/pilots/Bernardi_1790_Verzicola_Boundary_Resolution_Note.md (T-MIN-018) as the source.
  HEDGE B (OUT OF SCOPE — NOT resolved by T-MIN-018, do not touch): the Bernardi POINT-VALUE-SCHEDULE transcription-extent caveat (Cap. III — which cards have confirmed point values, e.g. "transcription bounded at XXVII", "Bernardi's transcription stops at XXVII", "Bernardi covers only XXIV–XXVII of the block"). This is a different topic (point pricing, not verzicola sequence membership) that T-MIN-018's note never examined — its transcription covered cap. V, VI, XV and Part II cap. VIII, not a re-read of cap. III's point table. Leave every Hedge-B occurrence exactly as written. If unsure which hedge a given line is, read the surrounding paragraph before editing — do not pattern-match on the numeral alone.
- SCOUT-F5 VERIFIED FILE-BY-FILE (dry run against branch test @d0052dc, 2026-08-12) — these are the files from the resolution note's §5 queue confirmed to currently contain a genuine Hedge-A occurrence, with line numbers AS OF d0052dc (re-check on your own checkout, lines may have drifted): research/pilots/Pilot3_TRUMP-08_Justice.md (L92), research/pilots/ARIE_BATCH_BRIEF.md (L86), research/pilots/ELEMENT_BATCH_BRIEF.md (L58–59), research/pilots/Element_Batch_Verification_Report.md (L41–42), research/pilots/Arie_Batch_Verification_Report.md (L82), research/pilots/Justice_Personality_Verification_Report_2.md (L183, "~XXVIII up"), research/pilots/Wave1_Virtue_Verification_Report.md (L218), research/pilots/Zodiac_Batch_Verification_Report.md (L108 and L282 — two occurrences), research/pilots/ZODIAC_BATCH_BRIEF.md (L80–81, wraps across two lines — use a search that isn't line-bounded), research/pilots/drafts/PERSONALITY_TRUMP-20_Fire.md (L363–364 and L442 — two occurrences, prose + FIR-C021 claims-table row), research/pilots/drafts/PERSONALITY_TRUMP-21_Water.md (L21 and L69–70 — two occurrences), research/pilots/drafts/PERSONALITY_TRUMP-22_Earth.md (L345–347 and L419 — two occurrences, prose + EAR-C020 claims-table row).
- SCOUT-F5 VERIFIED — files listed in the queue that, on inspection, do NOT currently contain a Hedge-A occurrence (either they only carry Hedge B language, or a plain unhedged mention of "XX–XXIII"/verzicola with no boundary numeral hedge attached): research/pilots/PAPI_FOOL_BATCH_BRIEF.md, research/pilots/Papi_Fool_Batch_Verification_Report.md, research/pilots/Fleet_Sweep_Personality_Triage_Report.md, research/pilots/Wave2_Virtue_Verification_Report.md, research/pilots/Quarantine_Register_Outside_Set_Claims.md, research/pilots/drafts/GUIDEBOOK_TRUMP-03_Ruler.md, research/pilots/drafts/GUIDEBOOK_TRUMP-04_Ruler.md, research/pilots/drafts/PERSONALITY_TRUMP-23_Air.md. Do not force an edit into these files if, on your own re-check, they still have no Hedge-A text — an empty diff in a file is an acceptable, correct outcome of this task. (Their queue listing in T-MIN-018's note was evidently keyed off Hedge-B language or the still-open "XX–XXIII unconfirmed by named example" question, per §4(B) of the resolution note — that open question is NOT resolved by T-MIN-018 either and must not be flattened to "resolved" anywhere; leave §4(B)-type language exactly as it stands.)
- research/archive/failed-runs/PERSONALITY_TRUMP-04_Ruler_FLEET-STUB_archived-2026-08-11.md is explicitly OUT OF SCOPE. It is an archived failed run, listed in the resolution note "for completeness only"; do not edit it.
- SCOUT-F5 JUDGMENT CALL ON research/pilots/Pilot3_TRUMP-08_Justice.md (read in full before touching — this is the most sensitive file in the queue): the task's authoring context raised an explicit concern that this file, as the ORIGIN document every other queue file's hedge citation points back to ("Justice pilot L92"), might be an audit-trail record that should stay historically accurate to what was known when it was written, per the established T-MIN-016 precedent (see commits 3ac0db7 and, especially, 02092c3, which reconciled stale "sort_order 57" prose in PERSONALITY_SPECIAL-FOOL_Fool.md to the resolved sort_order 0, while explicitly leaving alone one line quoting another unrevised source's own text and one line citing a historical Stage-2 inventory snapshot, on the reasoning that those two were accurate descriptions of other out-of-scope, unrevised sources, not live claims resting on the fact being corrected).
  SCOUT-F5's reasoned call, after reading Pilot3_TRUMP-08_Justice.md L92 in full: **UPDATE it**, narrowly. Reasoning: (1) L92 is not a quotation of another file's text and not a dated historical snapshot reference — it is the pilot's own live descriptive paraphrase of what Bernardi's source says ("Bernardi says a verzicola is made from consecutive cards and then gives explicit low-Papi examples from I–V and higher-trump examples beginning around XXVIII"), directly analogous to the SPECIAL-FOOL study's own stale sort_order prose that 02092c3 corrected, not to the two lines 02092c3 deliberately preserved. (2) The resolution note's own §5 queue and §6 supersession statement already treat L92 as "the hedge itself, source of truth all other files point back to" — i.e. the T-MIN-018 author's own view was that it should eventually be corrected, not preserved as a monument. (3) The claim the hedge sits inside, JUS-C006 ("Trump VIII has no special intrinsic point value"), does not rest on the exact verzicola boundary numeral for its own truth — fixing the hedge phrase changes no claim's validity, confidence, or evidence label. THEREFORE: edit ONLY the specific clause "higher-trump examples beginning around XXVIII" → wording stating the boundary is exactly XXVIII with a citation to Bernardi_1790_Verzicola_Boundary_Resolution_Note.md. Do not touch anything else on that line or in that paragraph (not the "does not claim that VIII can never occur…" sentence, not the citeturn marker, not JUS-C006 or JUS-C015 elsewhere in the file).
- SCOUT-F5 FINDING — the resolution note's queue entry for Pilot3_TRUMP-08_Justice.md also cites "line 525 (JSON claim register echoing the 'I-XXVII... II-V' bound)" as needing an update. This is a FALSE POSITIVE relative to this task: as of d0052dc, JSON line 525 is JUS-C006's `source_links[0].note` field, which reads "Bernardi assigns five points to I, X, XIII and XX among I-XXVII and three points to II-V; VIII is not assigned a special value" — this is Hedge B (the Cap. III point-value schedule), textually unrelated to the verzicola sequence boundary, and must NOT be edited under this task. The JSON's actual echo of the verzicola hedge is three lines later, at the `qualifications` field ("This does not resolve every possible role of VIII in consecutive-card combinations") — but that sentence does not itself contain the numeral hedge text and needs no literal edit; leave it as-is too. Do not edit JSON line 525 or the qualifications field.
- CLAIMS-TABLE + PROSE SYNC (applies to research/pilots/drafts/PERSONALITY_TRUMP-20_Fire.md, _21_Water.md, and _22_Earth.md, and any verification report with a claims table touched by this task): every one of these files carries the Hedge-A phrase in BOTH a prose passage AND a claims-table row (e.g. Fire's FIR-C021, Earth's EAR-C020). Fixing one without the other is a defect this project's discipline explicitly forbids — update both in the same commit, keeping the wording of what's now confirmed ("exactly XXVIII, per the T-MIN-018 resolution note") consistent between the prose and the table cell. Do not upgrade the separate, still-open §4(B) question ("can XX–XXIII itself form a verzicola") to resolved anywhere — that remains "covered by the general rule, unconfirmed by named example" per the resolution note; only the specific boundary-numeral hedge is in scope here.

**Definition of Done:**
- PM-F9 CORRECTION (2026-08-12): SCOUT-F5's file-by-file list in scope (bullet 3) actually names 12 distinct files, not 11 — re-count: Pilot3_TRUMP-08_Justice.md, ARIE_BATCH_BRIEF.md, ELEMENT_BATCH_BRIEF.md, Element_Batch_Verification_Report.md, Arie_Batch_Verification_Report.md, Justice_Personality_Verification_Report_2.md, Wave1_Virtue_Verification_Report.md, Zodiac_Batch_Verification_Report.md, ZODIAC_BATCH_BRIEF.md, PERSONALITY_TRUMP-20_Fire.md, PERSONALITY_TRUMP-21_Water.md, PERSONALITY_TRUMP-22_Earth.md = 12 files. Re-verified directly against test-branch content @d0052dc via a dry run of the verification_command below: it reports exactly 16 occurrences across exactly these 12 files (1 each in 8 of them, 2 each in Zodiac_Batch_Verification_Report.md, Fire, Water, and Earth), matching every claimed location. The "11 files" figure below and in the task title/PM-assignment shorthand is a miscount; treat 12 as authoritative for the definition of done.
- Every confirmed Hedge-A occurrence listed in the scope above (16 occurrences across 12 files — see correction above; SCOUT-F5's dry run undercounted the file total by one) is replaced with wording stating the verzicola upper-sequence boundary is exactly XXVIII, each with an explicit citation to research/pilots/Bernardi_1790_Verzicola_Boundary_Resolution_Note.md.
- No Hedge-B (point-value-schedule transcription-extent) text is altered anywhere.
- No claim, confidence label, grading, or conclusion other than the hedge phrase itself changes in any touched file; a reviewer diffing before/after should see only the hedge-phrase-plus-citation edits (and, where present, the matching claims-table cell) and nothing else.
- The still-open §4(B) question (whether XX–XXIII itself can form a verzicola) is not flattened to resolved anywhere it appears; it stays framed as "covered by the general rule, unconfirmed by named example" per the resolution note.
- For every file where a Hedge-A fix touches prose that has a matching claims-table row (at minimum PERSONALITY_TRUMP-20_Fire.md/FIR-C021 and PERSONALITY_TRUMP-22_Earth.md/EAR-C020), both the prose and the claims-table row are updated in sync.
- research/pilots/Pilot3_TRUMP-08_Justice.md line 92's hedge clause is updated per the judgment call above (narrowly — the hedge clause and its citation only); JSON line 525 and the qualifications field are left untouched.
- research/archive/failed-runs/PERSONALITY_TRUMP-04_Ruler_FLEET-STUB_archived-2026-08-11.md is not modified.
- Files verified to have no current Hedge-A text (PAPI_FOOL_BATCH_BRIEF.md, Papi_Fool_Batch_Verification_Report.md, Fleet_Sweep_Personality_Triage_Report.md, Wave2_Virtue_Verification_Report.md, Quarantine_Register_Outside_Set_Claims.md, GUIDEBOOK_TRUMP-03_Ruler.md, GUIDEBOOK_TRUMP-04_Ruler.md, PERSONALITY_TRUMP-23_Air.md) are re-checked by the worker and left untouched if still empty of Hedge-A text — do not force an edit into a file that has none.

*Audited against SHA:* `d0052dc`

---
### ✅ T-MIN-015 · P2 · ANY · DONE
**Reconcile the Papi/Fool batch's deferred arie edges now that T-MIN-011 is merged**
**Owner:** Worker-F16

**Scope:**
- Read the four explicit deferral notes first, exact claim IDs: GAN-C012 (research/pilots/drafts/PERSONALITY_TRUMP-01_Ganellino.md, claims table + its Sec.3 prose "no typed edge — arie batch in flight, reconciliation deferred"), RUL2-C012 (PERSONALITY_TRUMP-02_Ruler.md, same pattern), RUL4-C013 (PERSONALITY_TRUMP-04_Ruler.md, "no committed text to reconcile against"), and FOO-C014 (PERSONALITY_TRUMP-FOOL_Fool.md, "arie batch in flight (T-MIN-011, unmerged), AIR-C011 offered-not-imposed model noted"). All four cite T-MIN-011 as the blocker; T-MIN-011 is now merged to test (five files: PERSONALITY_TRUMP-36_Star.md through -40_Trumpets.md).
- Ganellino/Rulers side (GAN-C012, RUL2-C012, RUL4-C013): check all five committed arie files for any mention of Ganellino, Papi, or Rulers — as of the merge, none of the five arie files assert or imply such an edge (confirmed absent by grep). Per the scope-forbid clause below, this means the correct close is most likely an explicit mutual decline with stated grounds, not an invented edge; but re-verify the arie files yourself before concluding that, since study text can have moved.
- Fool/Trumpets side (FOO-C014 and the Trumpets file's TRO-C018): TRO-C018 reads "No Fool edge: the Fool/papi batch is briefed in parallel; the structural contrast is queued (Sec.4) and left to that batch to offer" — this is a live, still-open invitation on the arie side, not a decline. Decide whether the Fool study now types this edge (the AIR-C011 offered-not-imposed model FOO-C014 names is the precedent: one side asserts, offered to the other, asymmetry recorded until reciprocated) or explicitly declines it with grounds. If typed, update BOTH PERSONALITY_TRUMP-FOOL_Fool.md and PERSONALITY_TRUMP-40_Trumpets.md claims tables and prose in sync (matching type, direction, grading); TRO-C018's "left to that batch to offer" language must not survive unchanged either way — replace it with the resolution.
- Scope forbids inventing any relationship not implied by either existing file's current text — no new thematic reading connecting the low block to the celestial arie may be introduced; if no textual hook exists, record the mutual decline and say so plainly rather than manufacturing a connection.
- Do not touch TRUMP-02/TRUMP-04's other claims, TRUMP-36/37/38/39's files, or any other study file beyond the four named plus TRUMP-40 (only if the Fool/Trumpets edge is typed).

**Definition of Done:**
- GAN-C012, RUL2-C012, and RUL4-C013 no longer read as open deferrals; each carries either a typed low-block-to-arie edge (updated in sync with the relevant arie file) or an explicit mutual decline with stated grounds.
- FOO-C014 and PERSONALITY_TRUMP-40_Trumpets.md's TRO-C018 are resolved in sync with each other, not just on the Fool side.
- No new relationship is asserted that is not implied by the existing text of either side; any decline states its grounds rather than being a silent removal.
- git diff --name-only against the audited sha touches only PERSONALITY_TRUMP-01_Ganellino.md, PERSONALITY_TRUMP-02_Ruler.md, PERSONALITY_TRUMP-04_Ruler.md, PERSONALITY_TRUMP-FOOL_Fool.md, and (only if the Fool/Trumpets edge is typed) PERSONALITY_TRUMP-40_Trumpets.md.

*Audited against SHA:* `19c26db`

---
### ✅ T-MIN-014 · P2 · ANY · DONE
**Write back resolved dispositions into the Quarantine Register (CW-5/6/7/10 and their QC rows)**
**Owner:** Worker-F15

**Scope:**
- Full sweep first: read research/pilots/Quarantine_Register_Outside_Set_Claims.md CW-1 through CW-10 in full (L809-962) and confirm which already carry a "STATUS —" paragraph (CW-1, CW-2, CW-3, CW-4, CW-8, CW-9 already do — read them as the exact pattern to match) and which do not (CW-5, CW-6, CW-7, CW-10 currently have none, despite being resolved in committed studies). CW-11 (Courts) and CW-12 (Pips) have no verified study yet and must be left untouched/still open.
- For each of CW-5, CW-6, CW-7, CW-10, write a "STATUS —" paragraph in the same format as the existing CW-8/CW-9 blocks, citing the study file, section, and claim ID(s) that resolved it: CW-5 (the Fool split it into a substantiated structural half and a refused mechanical half — PERSONALITY_TRUMP-FOOL_Fool.md Sec.0, FOO-C007); CW-6 (elements replaced it with a mode-of-energy reading — AIR-C006, and per Element_Batch_Verification_Report.md M-2, Fire owns the Death-edge sub-disposition at FIR-C017, cited by EAR-/WAT-/AIR-); CW-7 (all twelve zodiac cards dispositioned it card-by-card, rejecting the "origin family" slogan — see Zodiac_Batch_Verification_Report.md L127, L232, and its n-4 finding); CW-10 (the Trumpets file confronted and rejected the "summons" convergence structurally, not just lexically — PERSONALITY_TRUMP-40_Trumpets.md Sec.0, TRO-C012, and the Arie_Batch_Verification_Report.md CW-10 structure sweep).
- Write a disposition annotation (matching the register's existing per-claim citation style) against every QC row named as resolved-but-undispositioned in the three batch verification reports' own "register maintenance queued" notes: Element_Batch_Verification_Report.md (QC-055 through QC-066, esp. the M-2 consolidation under Fire's FIR-C017 and the M-4 Water-only QC-066); Zodiac_Batch_Verification_Report.md n-4 (QC-070, QC-072, QC-075, QC-076, plus the twelve per-card CW-7 dispositions); Arie_Batch_Verification_Report.md "Register maintenance queued" note (QC-077 through QC-089 and QC-107, with the one-owner-per-collective-row table in that report Sec.2 as the exact citation map); Papi_Fool_Batch_Verification_Report.md (QC-043 through QC-054, including the QC-049 "immune party" heading the report flags as stale).
- Do NOT edit any file under research/pilots/drafts/ or any study file — this task only writes into Quarantine_Register_Outside_Set_Claims.md. Verify by diff that no other tracked file changed.
- If two verified studies assert incompatible dispositions for the same row (e.g. a claim resolved one way by one batch and cited differently by another), do NOT resolve it yourself — add a "STATUS — FLAGGED, needs human adjudication" note quoting both readings, and leave the row otherwise as-is.

**Definition of Done:**
- Quarantine_Register_Outside_Set_Claims.md carries a STATUS paragraph for CW-5, CW-6, CW-7, and CW-10, each citing the specific study file, section, and claim ID(s) that produced the resolution, formatted like the existing CW-8/CW-9 blocks.
- Every QC row named in the four batches' verification-report "register maintenance queued" sections (QC-043 through QC-054, QC-055 through QC-066, QC-070/QC-072/QC-075/QC-076, QC-077 through QC-089, QC-107) carries an inline disposition or STATUS annotation citing its resolving claim ID.
- Any genuinely conflicting dispositions are flagged for human review, not silently resolved.
- git diff --name-only against the audited sha shows only Quarantine_Register_Outside_Set_Claims.md changed.

*Audited against SHA:* `19c26db`

---
### ✅ T-MIN-018 · P2 · codex · DONE
**Attempt direct web access to Bernardi 1790 (archive.org) to resolve the verzicola boundary before requiring a human download — supersedes T-MIN-008**
**Owner:** Worker-F19

**Scope:**
- This task supersedes T-MIN-008 (still OPEN, unaudited — audited_at/audited_by/audited_repo_sha all null as of this writing) pending a PM decision on which of the two stays open. T-MIN-008 was scoped assuming the Bernardi 1790 source (RULE-1790) had to be manually acquired because it exists only as a bibliographic pointer to https://archive.org/details/bub_gb_4_rdG3SVa48C (68 pages), not physically stored in the repo. This task preserves T-MIN-008's original scope and definition_of_done in full (see below, verbatim) but adds an explicit, mandatory FIRST step: attempt direct WebFetch/WebSearch of archive.org's own OCR/plaintext exposure for that item before concluding a human must download anything.
- Precedent: T-MIN-009 (DONE) resolved a structurally similar problem — hedged zodiac locators — entirely via WebFetch/WebSearch against public web editions (LacusCurtius, Perseus/Scaife, Thorndike, Topostext), with zero local repo storage of the sources. Read research/pilots/Zodiac_Locator_Resolution_Note.md in full before starting; its "Method" section and "Sources opened" table are the standard this task is held to (open the actual source, cite exact locators, downgrade to [UNVERIFIED] rather than inventing).
- MANDATORY FIRST STEP: attempt to open archive.org item bub_gb_4_rdG3SVa48C via its public endpoints before doing anything else. Try, in order, and document what was tried and what each attempt returned (HTTP status, content found or not): (a) the item's metadata API, https://archive.org/metadata/bub_gb_4_rdG3SVa48C, to discover available derivative files (djvu.txt, _text.pdf, etc.); (b) the plaintext/OCR view, typically https://archive.org/stream/bub_gb_4_rdG3SVa48C/bub_gb_4_rdG3SVa48C_djvu.txt (the exact filename segment must be confirmed from the metadata API response, not assumed); (c) the item's own details/download page for a full-text or PDF derivative; (d) a general WebSearch for the same Bernardi 1790 rules text hosted on any other public digitization (Google Books, a library digital collection, etc.) if archive.org's own OCR is unusable (e.g. garbled, paywalled, or the derivative does not exist for this item).
- Only if (a) through (d) are genuinely attempted and fail — not merely found inconvenient — is it acceptable to conclude a human must acquire a physical/PDF copy. "Genuinely fail" means: endpoints 404/error, or the OCR text is present but too degraded to locate/read the verzicola passage with confidence, or no readable derivative exists at all. Document exactly what was tried and what each attempt returned before falling back to that conclusion; a bare "could not find it" without documented attempts is not acceptable.
- If direct access succeeds: transcribe every verzicola combination example from Bernardi's 1790 text directly, replacing the Justice pilot's hedge ("I-V and beginning around XXVIII", pilot line 92) with an exact list, with exact locators (chapter and printed page, or the archive.org page/leaf number if no printed page number is legible). Record whether the examples are exhaustive or exemplary in Bernardi's own text; do not convert examples into rules — the deliverable is the transcription plus locators, not an interpretation.
- Thirteen committed studies currently lean on the hedge; the zodiac batch flags it as acutely open at XXVII (one numeral below) and XXVIII (the numeral the hedge names), and the element batch left "whether XX-XXIII can form a verzicola" as a standing open question in all four files. If the boundary resolves, list the follow-up amendments needed (zodiac files XXVII/XXVIII sections 2 and 4, element files' open questions, Justice pilot cross-references) as a reconciliation queue; apply the amendments only if the audit that unlocks this task scopes that in — do not silently apply them un-audited.
- If direct web access genuinely fails after documented attempts: write the same conclusion T-MIN-008 anticipated (a human must acquire a physical/PDF copy of archive.org item bub_gb_4_rdG3SVa48C) but back it with the documented attempt log from this task, not with an unexamined assumption.

**Definition of Done:**
- A documented attempt log exists (in the same output note) showing what was tried against archive.org (metadata API, stream/OCR view, details page) and any fallback WebSearch, with outcomes for each — win or fail.
- A sourced note in research/02-source-audit/ or research/pilots/ either (a) transcribes the verzicola examples with exact locators and states what the record can and cannot support, using direct web access as the source, or (b) states plainly that direct web access was attempted and genuinely failed, with the attempt log as evidence, before recommending human acquisition.
- The reconciliation queue of affected files is listed with per-file line references, if the boundary resolved.
- The hedge is superseded only by direct transcription or a documented failed-attempt log, never by memory or assumption.
- This task's output note explicitly states it supersedes/replaces T-MIN-008's rationale; it does not archive or delete T-MIN-008 itself (that is a PM/human decision).

*Audited against SHA:* `09f857d`

---
### ⏳ T-MIN-007 · P2 · ANY · HUMAN_REVIEW
**Triage the eleven GUIDEBOOK files from the fleet sweep**
**Owner:** Worker-F7

**Scope:**
- Verification-triage all eleven GUIDEBOOK_*.md files in research/pilots/drafts/ (TRUMP-01 through -05, -08, -36 through -40), which sit on main and test looking authoritative but are unverified fleet output.
- Establish first what a GUIDEBOOK file is supposed to be - no committed spec appears to exist; check the sweep's originating brief and whether the format duplicates, summarizes, or contradicts the personality studies.
- Check each file for the three known disguises (wrong-but-fluent, stub-with-a-label, clone-with-a-costume) with diffs against the personality studies and each other; recompute any rank or scoring claims against the registry.
- Recommend a disposition for the format itself - keep as a distinct deliverable (write the missing spec), fold into the personality studies, or archive - and per-file bins consistent with that recommendation.

**Definition of Done:**
- A triage report in research/pilots/ covers all eleven files with per-file bins and a reasoned recommendation on the GUIDEBOOK format's future.
- No GUIDEBOOK file remains uninspected; any clone or stub is archived with a disposition note.

*Audited against SHA:* `c4f389f`

---
### ⏳ T-MIN-013 · P2 · ANY · HUMAN_REVIEW
**Design the light-tier suit-card study format (spec + two pilot cards)**
**Owner:** Worker-F13

**Scope:**
- Write research/pilots/SUIT_CARD_FORMAT_SPEC.md defining a compact per-card study format for the 56 suit cards. Required sections: registry facts (restated, never improved), rank-in-suit arithmetic (recomputed inline), Bernardi scoring where sourced (bounded-transcription caveat carried), iconography baseline, a brief project reading, and a mini claims table — every claim provenance-graded with the same [F]/[SI]/[U]/[UNVERIFIED] discipline as the trump studies.
- This is the venture plan's dependency: teamwork/VENTURE_BRIEF.md §2 line 7 (trumps at full verified depth, 56 suit cards at a lighter standard tier so "research complete" is a reachable pre-launch milestone). The format must be cheap enough to produce 56 times but carry the same honesty discipline — [UNVERIFIED] over invention, no padding to look thorough.
- Write TWO pilot cards to the new format — suggested SUIT-COINS-04 (Four of Coins) and SUIT-CUPS-12 (Cavalier of Cups), which have existing full pilot dossiers (research/pilots/Pilot1_SUIT-COINS-04_* and Pilot2_SUIT-CUPS-12_*) to cross-check against. This redundancy is intentional: the light-tier pilots must not contradict the full dossiers, and any divergence found is itself a finding to record.
- Deliver a short comparison of the two light-tier pilots against their two existing full dossiers, stating what the light tier keeps, what it drops, and whether anything dropped is load-bearing for reader honesty (the visible Verified/Draft/Stub maturity mechanic in the venture brief).
- The format decision itself is the human's — this task produces the proposal and evidence, not a fleet-wide rollout; do not begin authoring the remaining 54 cards.

**Definition of Done:**
- research/pilots/SUIT_CARD_FORMAT_SPEC.md exists and defines the compact format with all required sections and the provenance-grading rules.
- Two pilot suit-card studies written to the spec exist in research/pilots/ (or a drafts/ subpath the spec designates), each internally consistent with its existing full pilot dossier or with divergences explicitly recorded.
- A short comparison document (or a comparison section in the spec) evaluates the light tier against the two full dossiers and states the trade-offs for the human's format decision.
- human_review_required is honored — the task ends at HUMAN_REVIEW with the format proposal, not with additional suit cards authored.

*Audited against SHA:* `f8bb1b8`

---
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
### ✅ T-MIN-017 · P3 · codex · DONE
**Apply D4 — Cavalier/Knight naming policy (write policy + audit four cavalier registry rows)**
**Owner:** Worker-F20

**Scope:**
- PM-F7 ARCHITECTURAL DECISION (audit 2026-08-12): this task depends on T-MIN-016, which adds an optional `aliases` field (list of strings) to Stage5_Master_Card_Registry.csv, Stage5_Master_Card_Registry.json, Stage4_Card_Dossier_Schema.json (`administrative_identity.aliases`), and Card_Dossier_Skeletons.json. Claim T-MIN-016 first (or confirm it is already DONE/merged) before starting this task, so the field exists once, not twice with two different shapes. RESOLUTION of the two-option choice below in the original scope: use the `aliases` field — add "Knight" to the `aliases` list for all four cavalier rows (SUIT-SWORDS-12, SUIT-BATONS-12, SUIT-CUPS-12, SUIT-COINS-12) in both the registry CSV and JSON. This is the SAME mechanism T-MIN-016 uses for TRUMP-FOOL's former-id alias — one consistent field for both a former-id alias and a search alias. Do not also add a second, differently-named field. Leave Knight in historical_names as well (do not remove it from there); `aliases` is additive, a machine-readable pointer, not a replacement for the historical_names prose. State this resolution explicitly in the naming policy doc so a reader does not have to re-derive it from the registry alone.
- Editorial decision D4 (tasks/human/editorial_decisions_2026-08-12.md) sets: Cavalier (Cavallo) is the public heading for the four cavalier court cards; Knight is a subordinate search alias. This extends the existing "names to avoid" precedent already on the Page row. No live URL/slug system exists yet — this is policy + registry data-consistency only, NOT a routing or slug-generation change.
- Scout audit of the four cavalier rows in research/05-registry-and-audit/Stage5_Master_Card_Registry.csv (branch test, commit 09f857d) found: SUIT-SWORDS-12, SUIT-BATONS-12, SUIT-CUPS-12, SUIT-COINS-12 all already carry canonical_name = "Cavalier of <Suit>" (already correct per D4) and historical_names = "Cavallo / Cavaliere / Knight / Horse" (Knight is already present, but folded into historical_names rather than called out as a search alias — the registry schema has no distinct field for 'search alias' or 'subordinate alias', only historical_names and names_to_avoid). All four rows' names_to_avoid column currently reads only "Page" — this is the existing precedent D4 explicitly extends.
- Write the naming policy itself, once, in a discoverable location. Prefer research/04-dossier-spec/ (the existing dossier-spec home) if a suitable file exists there to extend; otherwise create a short new file research/04-dossier-spec/NAMING_POLICY.md (or research/pilots/NAMING_POLICY.md only if 04-dossier-spec is a worse fit on inspection — pick one, do not create both). The policy statement must cover: (1) historical accuracy governs the public heading (canonical_name) — e.g. Cavalier not Knight, matching the existing Page exclusion precedent; (2) familiar/common English terms (Knight, etc.) are retained as search aliases, not headings; (3) explicitly state this is a naming/data-consistency policy only — no URL/slug routing system exists yet to implement it.
- Audit and, if needed, update the four cavalier registry rows (SUIT-SWORDS-12, SUIT-BATONS-12, SUIT-CUPS-12, SUIT-COINS-12 in Stage5_Master_Card_Registry.csv and the corresponding entries in Stage5_Master_Card_Registry.json) for heading/alias consistency with the new policy: confirm canonical_name stays "Cavalier of <Suit>" for all four (already correct — do not change if already correct), and make Knight's status as an explicit search alias unambiguous in the record — either by adding it to a clearly-labeled alias representation (if you add a new column/field, add it consistently to all four rows, document the new field's meaning inline or in the naming policy doc, and do not invent per-row inconsistent formats), or by leaving Knight inside historical_names but adding one explicit sentence to the naming policy doc stating that, for these four rows specifically, historical_names doubles as the search-alias list until a dedicated field exists. Either approach is acceptable; pick one and apply it uniformly across all four rows, and say in the policy doc which approach was taken and why.
- Do NOT invent a URL-slug or routing system. The url_slug column already exists and already reads cavalier-of-<suit> for all four rows (e.g. cavalier-of-cups) — leave url_slug values untouched; this task is naming/heading policy and registry alias-consistency only.
- Do not touch Pilot2_SUIT-CUPS-12_Cavalier_of_Cups.md or the STANDARD_SUIT-CUPS-12_Cavalier_of_Cups.md draft's prose/claims content — those are content files, not registry/policy files, and out of scope for this task.

**Definition of Done:**
- A single naming-policy document exists at a discoverable path (research/04-dossier-spec/ preferred) stating the Cavalier-heading / Knight-alias rule, citing the Page precedent, explicitly noting no URL/slug system exists yet, and stating that Knight's alias status is recorded via the `aliases` field added by T-MIN-016.
- All four cavalier rows in both Stage5_Master_Card_Registry.csv and Stage5_Master_Card_Registry.json have canonical_name "Cavalier of <Suit>" and have "Knight" recorded in an `aliases` field/column (the same field T-MIN-016 introduces for TRUMP-FOOL), consistent across all four rows, with historical_names left unchanged (Knight remains there too — additive, not a replacement).
- url_slug values for the four cavalier rows are unchanged from cavalier-of-swords / cavalier-of-batons / cavalier-of-cups / cavalier-of-coins.
- git diff --name-only against the audited sha touches only the new/edited policy file and the two registry files (CSV + JSON) — no pilot/draft study content files are touched.

*Audited against SHA:* `09f857d`

---
### ✅ T-MIN-020 · P3 · ANY · DONE
**Fix grep-A20 verification-window fragility on SPECIAL-FOOL's aliases field in the master registry JSON**
**Owner:** Worker-F22

**Scope:**
- SCOUT-F5 SOURCE: T-MIN-017's worker (Worker-F20) and an independent reviewer both found that `grep -A20 "card_id"` doesn't reliably reach fields positioned late in a JSON card object in research/05-registry-and-audit/Stage5_Master_Card_Registry.json (each card object has ~26 fields). Worker-F20 fixed this locally for the four cavalier rows (SUIT-SWORDS-12, SUIT-BATONS-12, SUIT-CUPS-12, SUIT-COINS-12) by repositioning the `aliases` key to sit immediately after `historical_names` (key-order-only change, no value changes). T-MIN-016's own SPECIAL-FOOL row, which introduced the `aliases` field in the first place, was never checked or fixed for the same issue.
- SCOUT-F5 CONFIRMED THE PROBLEM IS REAL (dry run against branch test @d0052dc, 2026-08-12): in research/05-registry-and-audit/Stage5_Master_Card_Registry.json, the SPECIAL-FOOL card object starts at `"card_id": "SPECIAL-FOOL"` and its `aliases` key (holding `["TRUMP-FOOL"]`) is the LAST key in the object, 25 lines later — outside a `grep -A20` window. Verified directly: `grep -n -A20 '"card_id": "SPECIAL-FOOL"' Stage5_Master_Card_Registry.json | grep -c aliases` returns 0 (fails to find it); `grep -n -A30 ...` does find it, 26 lines after the `-A` start. This is the exact same class of failure T-MIN-017 fixed for the cavalier rows, unfixed here.
- Fix: reposition the `aliases` key in the SPECIAL-FOOL card object ONLY, in research/05-registry-and-audit/Stage5_Master_Card_Registry.json, to sit immediately after `historical_names` and before `names_to_avoid` — the exact same position T-MIN-017 used for the four cavalier rows (see e.g. the SUIT-CUPS-12 row for the reference ordering: card_id, canonical_name, italian_name, historical_names, aliases, names_to_avoid, family, ...). This is a KEY-ORDER-ONLY change: do not add, remove, rename, or change the value of `aliases` (must remain exactly `["TRUMP-FOOL"]`) or any other field in the SPECIAL-FOOL object.
- Do NOT touch Stage5_Master_Card_Registry.csv — the fragility is specific to `grep -A<N>` windowing over the multi-line JSON representation; a CSV row is a single line and is not affected. Do NOT touch any other card row's key order (the cavalier rows are already fixed by T-MIN-017; leave every other row exactly as-is).
- Do not touch Card_Dossier_Skeletons.json, Stage4_Card_Dossier_Schema.json, or any personality/dossier study file — this task's blast radius is the one SPECIAL-FOOL object in Stage5_Master_Card_Registry.json only.

**Definition of Done:**
- In research/05-registry-and-audit/Stage5_Master_Card_Registry.json, the SPECIAL-FOOL card object's `aliases` key is repositioned to immediately follow `historical_names` (and precede `names_to_avoid`), matching the cavalier-row convention T-MIN-017 established.
- The SPECIAL-FOOL object's `aliases` value is unchanged (`["TRUMP-FOOL"]`), and no other field or value in that object, or in any other object in the file, changes.
- The full file remains valid JSON, confirmed by an actual JSON parser (not just visual inspection).
- A `grep -A20 "\"card_id\": \"SPECIAL-FOOL\""` window over the fixed file now contains the string `"aliases"`.

*Audited against SHA:* `d0052dc`

---
### ✅ T-MIN-009 · P3 · ANY · DONE
**Verify the zodiac batch's UNVERIFIED doctrine locators**
**Owner:** Worker-F9

**Scope:**
- The twelve zodiac studies deliberately hedge their classical-doctrine citations rather than invent locators. Resolve each to a real locator or downgrade the claim; 'Ptolemy Tetrabiblos Book I aspects-of-the-signs chapter (used for all six diametrical opposite edges); Aratus Phaenomena lines for the Chelae/Claws material (Libra/Scorpio) and the Parthenos grain-ear (Virgo); Sacrobosco De sphaera cap. II zodiac description and the tropics (Capricorn/Cancer); Isidore Etymologiae III day-equals-night gloss (Libra); the sun-domicile scheme (Leo); Hydrochoos and winter-rains (Aquarius); Dioscuri star-lore (Gemini).'
- Every resolution must come from an opened source with a page/line/chapter locator, never from memory - the citation audit's 208 untraceable references are the cautionary tale.
- PM scope clarification (PM-F3, 2026-08-11): external source access IS in scope and required - workers may open web editions and library APIs (e.g. archive.org, Perseus/Scaife, LacusCurtius, digitized incunabula of Sacrobosco/Isidore) to read Ptolemy, Aratus, Sacrobosco, and Isidore; resolving locators from memory remains forbidden.
- PM scope clarification (PM-F3, 2026-08-11): write the locator-resolution note as research/pilots/Zodiac_Locator_Resolution_Note.md (matching Zodiac_Locator_Resolution*.md) and name each of the twelve ids TRUMP-24 through TRUMP-35 in it.
- Update the twelve claims tables and prose gradings in place (Moderate-pending- locators to High, or downgrade to [UNVERIFIED] wholesale where the source does not bear the claim); keep prose and tables in sync.

**Definition of Done:**
- No zodiac study contains the phrase 'locator UNVERIFIED' without either a resolved citation or an explicit downgrade recorded in its claims table.
- A short locator-resolution note records which sources were opened and what each yielded.

*Audited against SHA:* `274b981`

---

## Repo: `newmexicoptg.org`

### 📋 T-PTG-016 · P0 · ANY · AUDITED
**SECURITY: admin_reply.php lets any logged-in member post fake assistant messages into ANY member's conversation (IDOR)**
**Owner:** None

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
### ✅ T-PTG-012 · P1 · ANY · DONE
**Finish and ship the color-schemes feature — Tasks 3-9 of the existing plan are unstarted, nothing member-facing has shipped**
**Owner:** Worker-ColorSchemes1

**Scope:**
- BACKGROUND: T-PTG-009 fixed the `/featurerequest` tag router so a real member's "different color schemes" request was correctly triaged. A full design spec (docs/superpowers/plans/2026-08-12-color-schemes.md, docs/superpowers/specs/2026-08-12-color-schemes-design.md) and 9-task implementation plan already exist on `main` (committed as c85cf52 and 4f3d681). The product owner (Chip) reported today that the feature "hasn't been implemented" and asked the Fleet Coordinator to investigate.
- CONFIRMED STATE (via direct inspection, not the plan's own checkbox state, which is unreliable/unmodified): a git worktree exists at `.claude/worktrees/color-schemes` on branch `worktree-color-schemes` (pushed to origin, currently `git worktree list`-locked), 3 commits ahead of the `c85cf52`/`4f3d681` plan-doc commits. Of those 3 commits, only 2 are this plan's work: `6e11fdd feat: add Dark/Sepia/PTG theme variable overrides to journal-chat.css` (= plan Task 1) and `37656cf feat: add theme-switcher.js with getStoredTheme/applyTheme/setTheme` (= plan Task 2). The third commit, `183e5fb Add v3 whitepaper teaser to changelog and featured pages`, is UNRELATED to this feature (it touches changelog.php/featured.php for a different reason) -- do not mistake it for plan Task 6 or Task 8 progress.
- CONFIRMED GAP: `grep -rn 'data-theme-picker\|theme-switcher.js' .claude/worktrees/color-schemes/journalgpt/*.php` returns ZERO matches. No page -- not `index.php`, not any of the six utility pages -- links `theme-switcher.js`, sets the flash-prevention inline snippet, or renders a `<select data-theme-picker>` control. This means Tasks 3 through 9 of the plan (wiring `index.php`, migrating `source.php`/`admin_migrate.php`/`changelog.php`/`login.php` off their own hardcoded dark-only `:root` blocks onto the shared variables, adding pickers to `featured.php`/`help.php` which already share the variables, and the final manual cross-theme visual pass) are entirely unstarted, despite Task 1/2's underlying plumbing already existing on the branch. Nothing here is reachable by a member today -- there is no UI control anywhere to change the theme, which fully explains the "hasn't been implemented" report.
- WHY THIS IS NOT A NEW SCOUT/PM DESIGN TASK: the plan at docs/superpowers/plans/2026-08-12-color-schemes.md is already complete, self-reviewed (see its own "Self-Review Notes" section confirming full spec coverage), and written to the level of literal diffs and exact verification commands per task. This fleet task's job is EXECUTION of the plan's remaining Tasks 3-9 exactly as written, continuing on the existing `worktree-color-schemes` branch/worktree (do not start a fresh worktree or branch) -- not re-planning or re-designing the feature.
- HOW TO EXECUTE: the plan document itself instructs "Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task." The Worker should follow that instruction directly, working inside `.claude/worktrees/color-schemes` on the `worktree-color-schemes` branch, starting at Task 3 (Task 1 and 2 are already done and must not be redone or reverted). Each task's own commit step in the plan should be followed as written (one commit per task, matching the plan's prescribed commit messages) so history stays legible.
- SCOPE BOUNDARY: this task covers finishing Tasks 3-9 of the existing plan AND merging the resulting `worktree-color-schemes` branch to `main` once Task 9's manual verification passes clean -- the feature is not "done" from the product owner's perspective until it is live in production, matching the bar T-PTG-009 and T-PTG-008 were held to. Do not leave the finished work stranded on the branch again.
- EXPLICITLY OUT OF SCOPE (per the plan's own Global Constraints, do not relitigate): more than the 4 specified themes (light/dark/sepia/ptg); server-side persisted theme preference; `prefers-color-scheme` auto-detection; any new CSS variable names beyond the plan's specified set; any `mcp__claude-in-chrome__*` tool use for the manual verification in Task 9 -- use the `/browse` skill per this project's CLAUDE.md, exactly as the plan itself already states.

**Definition of Done:**
- Plan Tasks 3 through 8 are each implemented exactly as specified in docs/superpowers/plans/2026-08-12-color-schemes.md (index.php wired with flash-prevention script + picker in the engine-controls-bar; source.php, admin_migrate.php, changelog.php, and login.php migrated off their own hardcoded `:root` blocks onto the shared journal-chat.css variables per each task's variable-mapping table, each with a picker added; featured.php and help.php get the flash-prevention snippet + switcher script + picker without needing variable migration). Each task's own Step-N verification command (grep counts, `php -l`) in the plan passes as specified before moving to the next task.
- Plan Task 9's automated regression check passes: `cd journalgpt && php tests/JournalAnswerServiceTest.php && php tests/AskEndpointTest.php` both report full pass with 0 failures.
- Plan Task 9's manual cross-theme visual verification is performed via the `/browse` skill (never `mcp__claude-in-chrome__*` tools directly, per this project's CLAUDE.md) across all 4 themes on index.php and all 6 migrated utility pages, confirming readable contrast and no leftover hardcoded-dark elements, with any issues found fixed and re-verified per the plan's own Task 9 Step 4.
- The `worktree-color-schemes` branch is merged into `main` and pushed, after all of the above passes clean -- the feature is verified live in production (a member visiting index.php sees a working Theme picker and can switch themes) before this task is submitted for review.
- The handoff notes explicitly confirm which of Tasks 3-9 were newly completed by this task (all of them, per the confirmed gap above) and that Tasks 1-2's existing work was left untouched, not redone.

*Audited against SHA:* `c85cf52974abea992b872003706bb4cb7bc1dc33`

---
### ✅ T-PTG-009 · P1 · ANY · DONE
**Feature-request tag router misses no-space variant, misrouting real member intent into RAG**
**Owner:** Worker-TagFix1

**Scope:**
- PROBLEM (confirmed via live production evidence, not re-derived): T-PTG-008 shipped the tag-triggered feature-request lane in journalgpt/api/ask.php and journalgpt/lib/FeatureRequestService.php, and it was pushed to origin/main earlier today. Within 40 minutes, a real member's first attempt to use it failed. They typed `/featurerequest different color schemes` (no space between "feature" and "request"). Confirmed via https://newmexicoptg.org/journalgpt/api/debug_logs.php?id=22: because the router requires an exact `/feature request` (or `/feature-request`) string with a separator character present, this message fell through to the normal RAG pipeline (JournalAnswerService), searched the piano-journal corpus for "color schemes", found nothing relevant, and returned a confusing non-answer ("The pilot Journal corpus does not contain information regarding different color schemes."). The member's actual intent -- reporting a feature idea -- was never triaged.
- EXACT ROOT CAUSE (read directly from journalgpt/lib/FeatureRequestService.php, the sole place the tag is detected): `public static function isTagged(string $message): bool { return (bool)preg_match('/^\/feature[- ]request(?=[\s]|$)/i', ltrim($message)); }`. The character class `[- ]` matches exactly one of a hyphen or a space between "feature" and "request" -- it has no zero-width/optional alternative. `/feature request ...` matches (space consumed by `[- ]`) and `/feature-request ...` matches (hyphen consumed), but `/featurerequest ...` does NOT match: there is no character between "feature" and "request" for `[- ]` to consume, so the whole preg_match fails and the message falls through to `$tier`/`$preset` resolution and JournalAnswerService::ask() in journalgpt/api/ask.php exactly as any ordinary technical question would. `FeatureRequestService::stripTag()` has the identical `[- ]` (non-optional) pattern and would have the same no-space gap if it were ever reached for this input, though in practice it is never called because `isTagged()` gates the call to `stripTag()`/`ask()` in api/ask.php.
- LEADING WHITESPACE: already handled correctly today -- both `isTagged()` and `stripTag()` call `ltrim($message)` before the regex, and the regex itself is anchored with `^` against that ltrimmed string. No change needed there; call this out in the Worker's diff review so they do not "fix" something that already works and accidentally regress it.
- NO EXISTING TEST COVERAGE (confirmed by direct search, not assumed): journalgpt/tests/AskEndpointTest.php has zero references to isTagged, stripTag, FeatureRequestService, or feature-request tag variants anywhere in the file -- it only tests anonymous-access denial, CSRF validation, and basic valid-JSON-response shape for the RAG lane, and never instantiates FeatureRequestService at all. There is also no FeatureRequestServiceTest.php or equivalent file anywhere under journalgpt/tests/ (directory listing confirmed). T-PTG-008's DoD proved the happy-path multi-turn conversation flow end-to-end against a running server, but never exercised tag-matching edge cases (no-space, hyphen-vs-space equivalence, or the false-positive-avoidance case) with an assertion -- this is a real coverage gap, not a process failure by that task, since first-token exact-string matching was explicitly the simplest option chosen at the time.
- FIX SCOPE, per the product owner's (Chip) explicit direction: the router must match ALL of `/feature request ...` (space), `/featurerequest ...` (no space), and `/feature-request ...` (hyphen), all case-insensitively, tolerant of a leading space or two before the leading slash (already handled via ltrim -- do not touch that part). This is a small, mechanical regex change to the separator between "feature" and "request" (e.g. making `[- ]` optional/zero-or-one, such as `[- ]?`) in BOTH `isTagged()` and `stripTag()` in journalgpt/lib/FeatureRequestService.php -- the same character-class fix belongs in both methods since they must stay in agreement about what counts as tagged, and `stripTag()`'s current pattern has the identical gap even though it happens not to be reachable for this exact failure today.
- EXPLICITLY OUT OF SCOPE, per the same conversation with the product owner: fuzzy/typo matching (e.g. tolerating `/feture request` or other misspellings) and detecting the tag phrase anywhere in the message body (rather than as the first token). Both were deliberately ruled out because they would reopen the false-positive risk that T-PTG-008's own PM audit closed: a genuine technical question that happens to mention "feature request" mid-sentence (e.g. "is a feature request needed to change the pinblock spec, or is that already covered?") must keep routing to the citation-grounded RAG lane, not the triage lane. The Worker must keep the match to this short, fixed set of normalized-first-token variants -- do not generalize into intent detection, Levenshtein-distance matching, or a substring search of the full message.
- REGRESSION SURFACE: journalgpt/api/ask.php's router calls `FeatureRequestService::isTagged($question)` once, before tier/preset/model resolution -- confirm the fix does not change that call site's shape (still a single boolean-returning static call). journalgpt/lib/FeatureRequestService.php's `ask()` method also calls `stripTag()` internally to compute `$cleanedText` from `$rawMessage` -- confirm a no-space or hyphenated tag still strips cleanly, leaving the member's actual message content (e.g. "different color schemes") in `$cleanedText`, not leftover tag fragments.

**Definition of Done:**
- A new automated test file, journalgpt/tests/FeatureRequestServiceTest.php (does not exist yet -- confirmed by directory listing), CLI-runnable via `php journalgpt/tests/FeatureRequestServiceTest.php` following this repo's existing tests/ convention (see AskEndpointTest.php's self-runner pattern), reproduces the real production failure and proves it fixed: `FeatureRequestService::isTagged('/featurerequest different color schemes')` returns true after the fix (it returns false today -- confirm the test fails against the pre-fix code before implementing, per this repo's TDD convention). This file is referenced directly in this task's verification_command.
- All three variants route correctly and case-insensitively: `/feature request ...`, `/featurerequest ...`, and `/feature-request ...` (and at least one mixed-case example, e.g. `/FeatureRequest ...` or `/Feature-Request ...`) all make `isTagged()` return true.
- The T-PTG-008 false-positive-avoidance guarantee still holds and is covered by an explicit regression test: a message where "feature request" (or a no-space/hyphenated variant) appears mid-sentence rather than as the first token -- e.g. "Is a feature request needed to change the pinblock spec, or is that already covered?" -- must still make `isTagged()` return false and route to the RAG pipeline, not the triage lane. This is the exact case T-PTG-008's PM audit was careful about and this fix must not reopen it.
- `stripTag()` is fixed consistently with `isTagged()` (same separator-matching change) and a test confirms a no-space or hyphenated tag strips cleanly, leaving the member's actual message content intact (e.g. `stripTag('/featurerequest different color schemes')` yields `'different color schemes'`, not a leftover fragment like `'request different color schemes'` or `'different color schemes'` with stray tag remnants).
- Leading-whitespace tolerance (already working via ltrim) is confirmed still working post-fix with at least one test case (e.g. `'  /featurerequest different color schemes'` with two leading spaces still routes to the triage lane) -- a guard against an accidental regression while touching this code, not new functionality to build.
- The existing test suite still passes in full -- journalgpt/tests/AskEndpointTest.php, journalgpt/tests/UsagePolicyTest.php, and journalgpt/tests/JournalAnswerServiceTest.php all run clean (0 failures) via the DB_HOST=127.0.0.1 DB_NAME=journal_ai_test DB_USER=root DB_PASS=root php journalgpt/tests/<File>.php pattern, confirming no regression to the RAG lane or the existing feature-request happy path.
- No fuzzy/typo matching and no anywhere-in-message-body detection was introduced -- the fix is confirmed (by reading the diff) to be limited to making the existing fixed-separator character class optional/zero-or-one in isTagged() and stripTag(), not a rewrite into general intent detection.

*Audited against SHA:* `04842d7e9120bd559464f6cc1586e8c52c72c5f1`

---
### ✅ T-PTG-013 · P1 · ANY · DONE
**Theme picker doesn't visibly recolor changelog.php (and 5 other pages) due to uncached-bust journal-chat.css links**
**Owner:** Worker-ThemeCache2

**Scope:**
- PROBLEM (reported directly by the product owner, Chip, live in production): selecting a different theme from the Theme picker on https://newmexicoptg.org/journalgpt/changelog.php does not visibly change the page's colors.
- CONFIRMED VIA CODE READING (not yet reproduced live -- see DoD; could not log in during Scout investigation, no test credentials available to the Fleet Coordinator): `journalgpt/index.php:162` links its stylesheet with a cache-busting query param -- `<link rel="stylesheet" href="assets/journal-chat.css?v=<?= htmlspecialchars($gitCommitHash, ENT_QUOTES, 'UTF-8') ?>">` -- so every deploy that changes `$gitCommitHash` forces browsers to fetch a fresh copy. ALL SIX other pages that link this same stylesheet (`journalgpt/changelog.php:44`, `source.php:209` (line shifted after T-PTG-012's edits, re-grep to confirm), `admin_migrate.php:63`, `login.php:69`, `featured.php:94` (`help.php`, confirm exact line via grep)) link the PLAIN, un-versioned URL: `<link rel="stylesheet" href="assets/journal-chat.css">`. Confirmed via `curl -sI https://newmexicoptg.org/journalgpt/assets/journal-chat.css` that the server sends no `Cache-Control` header at all for this file (only `last-modified` and `etag`), so browsers fall back to HTTP heuristic caching and may keep serving a stale cached copy of `journal-chat.css` indefinitely for any browser that first fetched it before T-PTG-012's Dark/Sepia/PTG `[data-theme="..."]` blocks (or before today's final page-wiring deploy) were added.
- WHY THIS MATCHES THE REPORTED SYMPTOM: the picker's `setTheme()`/`applyTheme()` logic (in `theme-switcher.js`, confirmed correct and unit-tested by T-PTG-012) only sets `document.documentElement.dataset.theme` -- it does not touch any CSS. If a visitor's browser is serving a cached pre-T-PTG-012 copy of `journal-chat.css` (one with no `[data-theme="dark"]`/`[data-theme="sepia"]`/`[data-theme="ptg"]` blocks at all), the `data-theme` attribute changes correctly but there is no matching CSS rule to apply, so the page visually never changes -- exactly the reported behavior. `changelog.php` specifically was also touched by an EARLIER, unrelated commit today (`183e5fb Add v3 whitepaper teaser to changelog and featured pages`, which predates T-PTG-012's picker-wiring work), making it plausible the product owner loaded this exact page in his browser earlier today (to check the new whitepaper teaser banner) and has been holding a stale cached `journal-chat.css` ever since.
- NOT YET CONFIRMED -- REQUIRES REPRODUCTION: this is the Scout's leading hypothesis from code reading, not a live-reproduced root cause. The Worker must first ask the product owner (or reproduce directly) whether a hard refresh (Cmd+Shift+R / disabling cache in DevTools) on changelog.php makes the picker work correctly. If a hard refresh fixes it, this confirms the caching theory and the fix below is sufficient. If a hard refresh does NOT fix it, there is a second, currently-unknown bug and the Worker must investigate further (check `theme-switcher.js` wiring specifically on this page, check for a JS error in the console, check whether the picker's `<option>` values actually match `VALID_THEMES`) before assuming the caching fix alone resolves the report.
- FIX SCOPE: add the same cache-busting query param pattern index.php already uses to the `journal-chat.css` `<link>` tag on all six pages that currently lack it (`changelog.php`, `source.php`, `admin_migrate.php`, `login.php`, `featured.php`, `help.php`). Reuse whatever mechanism produces `$gitCommitHash` in `index.php` (grep for its definition/computation in index.php or a shared lib -- likely `lib/Config.php` or similar) so the version string stays consistent across all seven pages rather than each page computing its own. If `$gitCommitHash` is only computed inline in index.php today, factor it into a small shared helper (e.g. a function in an existing lib file) so all seven pages call the same source of truth -- do not duplicate the git-hash-lookup logic seven times.
- EXPLICITLY OUT OF SCOPE: do not add a `Cache-Control` header to journal-chat.css itself as an alternative fix -- the cache-busting query param is the pattern this codebase already established for index.php and is the smaller, more consistent change. Do not touch theme-switcher.js unless the reproduction step in the DoD reveals a second bug beyond caching.

**Definition of Done:**
- Before writing the fix, the Worker either gets direct confirmation from the product owner that a hard refresh resolves the reported symptom on changelog.php, or independently reproduces the stale-cache behavior (e.g. by loading the page, then reverting journal-chat.css locally to a pre-T-PTG-012 version, restarting a local PHP server, loading the page once to seed a browser cache, restoring the real file, then reloading normally without a hard refresh, and confirming the picker fails to visibly recolor the page) -- and records which method was used and what was found in the handoff.
- All seven pages (`index.php`, `changelog.php`, `source.php`, `admin_migrate.php`, `login.php`, `featured.php`, `help.php`) link `journal-chat.css` with an identical cache-busting query-param pattern, sourced from one shared helper (not seven independent computations).
- php -l passes on all seven modified/verified files.
- The existing test suite still passes in full -- journalgpt/tests/AskEndpointTest.php, journalgpt/tests/UsagePolicyTest.php, and journalgpt/tests/JournalAnswerServiceTest.php all run clean (0 failures).
- The handoff explicitly states whether the caching theory was confirmed as the actual root cause, or whether a second bug was found and fixed -- so the human reviewer can judge whether the reported symptom is actually resolved, not just whether a plausible-sounding fix shipped.

*Audited against SHA:* `604d1be6492f4f2ec8b477bae4f65b55fcd5d146`

---
### ✅ T-PTG-006 · P1 · ANY · DONE
**Enhanced multi-turn conversational-quality testing system (Golden Hammer deep dive)**
**Owner:** Claude-FleetCommander

**Scope:**
- journalgpt/tests/manual_conversation_matrix.php (new) — generalizes manual_voicing_continuity_matrix.php into a scenario-driven harness: runs an arbitrary N-turn conversation loaded from a JSON scenario file (not hardcoded to one Q&A pair), tagging each turn with a cognitive-mode `type` (factual_retrieval / synthesis / speculative / sentiment_aggregation) and an `expect_grounded` flag so type-appropriate quality checks can be applied.
- journalgpt/tests/scenarios/golden_hammer_deep_dive.json (new) — Chip's 4-turn scenario: 'Who won the Golden Hammer award over the last five years?' -> 'Tell me about their biographies. Do they have anything in common?' -> 'Imagine that you were in a room with all of them. What do you think they would talk about?' -> 'What are some of the concerns for this organization that have been voiced in the last five years?'. Deliberately mixes a purely factual turn, a cross-referencing synthesis turn, an EXPLICITLY SPECULATIVE turn (should never be treated as a grounded corpus claim), and a sentiment-aggregation turn requiring synthesis across many scattered sources.
- Purpose: go beyond 'does it cite correctly' (T-PTG-005) into 'does the conversation feel like a genuinely capable assistant, not a rigid grounding-rule robot' — specifically whether the strict corpus-grounding system instruction causes the speculative turn to refuse or produce a stilted non-answer instead of engaging naturally while drawing on the real biographical facts established earlier in the conversation.

**Definition of Done:**
- Scenario executed against at least 3 preset/tier combinations covering the speed spectrum (e.g. scholarly/quick, scholarly/medium, scholarly/deep).
- For each combination, record whether the speculative turn (turn 3) refused, gave a stilted 'I cannot speculate' non-answer, or engaged naturally while staying grounded in the real facts from turns 1-2 — this is the key quality signal this scenario is built to surface.
- For each combination, verify turns 1/2/4 (the grounded ones) still produce correct, well-formed citations per the existing T-PTG-001/002 checks.
- Findings written up identifying any combination where the speculative turn behaves poorly, with a concrete recommendation (e.g. system-instruction wording change) if a pattern emerges — not just raw JSON dumps.

*Audited against SHA:* `700b5e56fd49ea8ac74666d0a5580c6bbc99d3f2`

---
### ✅ T-PTG-011 · P1 · ANY · DONE
**"Good Answer" upvote click fails in production with "Invalid or missing CSRF security token"**
**Owner:** Worker-CSRF1

**Scope:**
- PROBLEM (reported directly by the product owner, Chip, live in production): clicking the "Good Answer" upvote button on an assistant message in journalgpt returns the JSON error `{"status":"error","error":"Invalid or missing CSRF security token."}` with HTTP 403, instead of toggling the upvote. Confirmed by reading journalgpt/api/upvote.php:66 -- this exact string is only emitted from the `Csrf::validate($csrfToken)` failure branch.
- CONFIRMED VIA CODE READING (not yet reproduced against a live failing session -- see DoD): journalgpt/assets/journal-chat.js:14 caches `csrfTokenInput` ONCE at page-load time via `document.querySelector('input[name="csrf_token"]')`, and the upvote click handler (journal-chat.js:456-473) reads `csrfTokenInput.value` and POSTs it unchanged to api/upvote.php. This value is never refreshed for the lifetime of the page. journalgpt/lib/Csrf.php::validate() compares that submitted value against `$_SESSION['journalgpt_csrf_token']` via `hash_equals` -- if the server-side session no longer contains the same token the page was rendered with, validation fails regardless of what the browser sends.
- LEADING HYPOTHESIS FOR WHY THE SESSION-SIDE TOKEN GOES STALE (confirmed by absence, not yet confirmed as the actual trigger -- see DoD): journalgpt/lib/Auth.php::startSession() sets the session cookie with `'lifetime' => 0` (i.e. the PHPSESSID cookie persists client-side until the browser/tab is closed) but sets no corresponding `session.gc_maxlifetime` or `session.cookie_lifetime` ini override anywhere in the codebase (grep of journalgpt/lib/Config.php and journalgpt/lib/Auth.php confirms no session.* ini_set calls exist). This means the server-side session DATA (including the CSRF token) expires according to the HOST'S default `session.gc_maxlifetime` (commonly as short as 1440s / 24 minutes on shared hosting), while the cookie referencing that session ID lives on in the browser much longer. A member who opens a conversation, reads a long AI answer for more than ~24 minutes (very plausible for a technical piano-repair answer), and then clicks "Good Answer" would be POSTing a csrf_token value tied to session data the server has already garbage-collected -- producing exactly this symptom. Ruled out as unrelated: response headers on https://newmexicoptg.org/journalgpt/index.php show `cache-control: no-store, no-cache, must-revalidate` and no CDN (`server: Apache`, no cf-/x-cache headers), so this is NOT a page-caching bug serving a stale token from a shared cache to multiple sessions.
- NO SERVER-SIDE LOGGING OF THIS FAILURE EXISTS TODAY: journalgpt/api/debug_logs.php only logs entries from the ask/RAG pipeline (question, model, retrieved_chunks_count, etc.) -- confirmed by inspecting a live pull of that endpoint, which contains zero fields related to upvote, csrf, or 403s. There is no production evidence log to point to for this specific failure the way T-PTG-009 had debug_logs.php?id=22 -- the PM/Worker must reproduce this locally (e.g. by starting a session, letting it idle past the host's session.gc_maxlifetime or manually clearing the session store entry server-side, then attempting the upvote with the original page's stale token) rather than relying on a production log line.
- REGRESSION SURFACE: the same "read csrfTokenInput.value once at page load, never refresh" pattern is also used by the chat-send flow (journal-chat.js:134) and the conversation-delete-or-similar flow (journal-chat.js:548) -- both POST the same cached token to their respective endpoints. If the fix introduces a token-refresh-and-retry mechanism, consider (but do not require without explicit scoping below) whether it should be shared plumbing rather than upvote-only, since the same idle-session failure mode could in principle hit those flows too -- though only the upvote button has been reported as broken so far, so do not silently change the other two flows' behavior without a corresponding DoD item covering them.
- FIX SCOPE: (1) Add a small authenticated endpoint (e.g. journalgpt/api/csrf_refresh.php) that calls `Csrf::generate()` and returns the current session-bound token as JSON -- this works whether or not the old session data was GC'd, since `Csrf::generate()` creates a fresh token in `$_SESSION` if none exists. (2) In journal-chat.js's upvote click handler, on receiving a 403 response whose body error matches the CSRF failure message, transparently fetch a fresh token from the new endpoint, update the cached `csrfTokenInput.value` (so subsequent actions on the same page also use the refreshed token), and retry the original upvote POST exactly once before surfacing an error to the user. Only if the retry also fails should the existing `alert(resData.error ...)` fire. (3) Confirm `Auth::user()` (the auth check at upvote.php:22, which runs BEFORE the CSRF check) still correctly reports the user as logged in during this scenario -- if PHP session GC evicted the CSRF token, it also evicted `journalgpt_user_id`, meaning the user is fully logged out server-side even though the cookie is still present. If that is the actual behavior, the auth-required branch (upvote.php:19-27) would fire first with a 401, not the CSRF branch with a 403 -- the Worker MUST verify which failure mode actually reproduces before assuming the CSRF-retry fix alone is sufficient. If it turns out to be the 401/logged-out case instead of (or in addition to) the CSRF case, the DoD below must be revised and the task returned to AUDITED with corrected scope rather than shipping a fix for the wrong branch.
- EXPLICITLY OUT OF SCOPE: do not change `session.gc_maxlifetime` or the cookie `lifetime` globally as a first-line fix -- that only narrows the reproduction window, it does not eliminate the underlying race between client-cached token and server session state (e.g. a user with two tabs open, or a server restart clearing in-memory session storage, would still hit it). The retry-on-403 pattern in FIX SCOPE item (2) is the required durable fix; a longer session lifetime may be proposed as a supplementary feedback item but is not required DoD.

**Definition of Done:**
- Before writing any fix, the Worker reproduces the exact failure locally and records in this task's events log (or the handoff) which HTTP status/branch actually fires first when a session's server-side data is evicted while the client still holds the old cookie and cached CSRF token: the 401 auth-required branch (upvote.php:19-27) or the 403 CSRF branch (upvote.php:56-63) or both in sequence. This determines whether the fix in the next item needs to also handle a 401-then-relogin case.
- journalgpt/api/csrf_refresh.php (new file) exists, requires an authenticated session (returns 401 JSON if not logged in, matching the existing pattern in upvote.php), and returns `{"status":"success","csrf_token":"<64-char-hex>"}` by calling `Csrf::generate()`.
- The upvote click handler in journal-chat.js retries exactly once on a CSRF-specific 403, using a freshly fetched token, before falling back to the existing error alert. A successful retry updates the button/badge UI exactly as a normal successful upvote does -- no visible error flashes to the user on the retried success path.
- A new automated test file, journalgpt/tests/CsrfRefreshTest.php (or added coverage in an existing relevant test file if the Worker judges that cleaner -- state the choice and reasoning in the handoff), following this repo's existing tests/ self-runner convention (see AskEndpointTest.php), proves: (a) csrf_refresh.php returns a valid token for an authenticated session, (b) it returns 401 for an unauthenticated session, and (c) upvote.php still correctly rejects a request whose csrf_token does not match the current session token (i.e. the existing security guarantee is unchanged, only the client-side recovery behavior is new).
- The existing test suite still passes in full -- journalgpt/tests/AskEndpointTest.php, journalgpt/tests/UsagePolicyTest.php, and journalgpt/tests/JournalAnswerServiceTest.php all run clean (0 failures).
- The handoff explicitly states which failure mode (401, 403, or both) was confirmed as the actual production trigger, so the PM/human reviewer can judge whether the shipped fix actually covers the reported bug rather than a plausible-but-wrong theory.

*Audited against SHA:* `c85cf52974abea992b872003706bb4cb7bc1dc33`

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
### 📋 T-PTG-015 · P2 · ANY · AUDITED
**JournalGPT v3 Phase 0: build the 30-50 example benchmark of disappointing interactions (gates all later v3 phases)**
**Owner:** None

**Scope:**
- BACKGROUND: journalgpt/v3/v3.md (currently untracked, not yet committed) is a full PRD for JournalGPT v2/v3 -- a 6-phase, ~15-25 developer-day rearchitecture of the answer pipeline (understand -> plan -> search -> evaluate evidence -> reason -> answer -> verify citations, replacing the current simple question -> File Search -> answer flow). Chip confirmed via AskUserQuestion that the fleet should proceed with ONLY Phase 0 for now, not the full project -- re-evaluate scope after Phase 0 lands. Nothing else in this PRD has been started (confirmed: no matching git branches, no lib files like ResearchPlanner.php/EvidenceRetriever.php exist, no other fleet tasks reference it).
- WHAT PHASE 0 IS, PER THE PRD ITSELF (journalgpt/v3/v3.md section 24 "Evaluation Dataset" and section 32 "Phase 0 -- Establish benchmark"): "Before changing production behavior, construct a benchmark of approximately 30-50 actual disappointing JournalGPT interactions... Do not begin tuning without baseline examples." Each benchmark entry must include: original user question; prior conversation context; existing JournalGPT answer; citations returned; why the answer was disappointing; characteristics of a better answer. Required category coverage: simple questions; vague questions; follow-ups; comparisons; technical reasoning; historical questions; questions with no Journal answer; multi-source questions; attempted content extraction.
- REAL PRODUCTION EVIDENCE GATHERED BY SCOUT (via debug_logs.php, the existing public debugging endpoint): as of this Scout pass, exactly 29 total logged interactions exist in production (this is a low-traffic pilot -- confirm the current count yourself, it will have grown by the time you work this). Of those 29, 10 show clear disappointing signals (status uncertain/error, model_declined=1, or zero parsed_citations_count on a nominally "success" response): log ids 2, 3, 4, 5, 7, 9, 10, 12, 13, 22. Notably: log ids 2/3/5 are three SEPARATE attempts at the literal one-word question "why?" (a broken follow-up -- the member almost certainly meant it as a continuation of a prior turn, and the system has no persistent conversation state to resolve that, exactly the Primary Problem section 4 describes); log ids 4/6/7/1 show FOUR attempts at "have voicing technique changed over the years?" with alternating success/uncertain outcomes for what looks like the same underlying question (retrieval-quality inconsistency); log ids 9/10/12/13 are real technical piano-repair questions returning uncertain/error. This is real, valuable seed data but far short of 30-50 -- do not fabricate additional entries to LOOK like they came from debug_logs.php; clearly separate real production examples from synthetic ones in the benchmark file (see FIX SCOPE below).
- WHY REAL DATA ALONE ISN'T ENOUGH: 10 real examples cannot cover the PRD's required category diversity (simple/vague/follow-up/comparison/technical-reasoning/historical/no-Journal-answer/multi-source/attempted-extraction -- 9 categories, and the 10 real examples cluster heavily in only 2-3 of them: broken follow-ups and technical-reasoning uncertainty). The benchmark must be supplemented with hand-authored synthetic examples covering the missing categories, written using genuine piano-technician domain knowledge (not vague placeholders) so they're realistic stand-ins for what a member might actually ask.
- THIS IS A JUDGMENT-HEAVY TASK, NOT A MECHANICAL ONE: "why was this disappointing" and "what would a better answer look like" require actual reasoning about each example, not boilerplate. For the real examples, ground the "why disappointing" explanation in the actual logged metadata (status, model_declined, is_grounded, retrieved_chunks_count, parsed_citations_count) plus a plausible reconstruction of what happened (you do not have access to the full answer TEXT via debug_logs.php, only metadata -- state this limitation explicitly per entry rather than inventing answer text you don't actually have).

**Definition of Done:**
- A new file journalgpt/v3/benchmark.md contains 30-50 entries, each as its own `### ` markdown heading (e.g. `### Entry 1 [REAL, debug_logs id 22]` or `### Entry 17 [SYNTHETIC, category: comparison]`), each with: original question, prior conversation context (or "none" if a fresh conversation), the existing answer or a clear statement that the raw answer text isn't available (for real entries sourced only from debug_logs.php metadata), citations returned (or "0, confirmed via parsed_citations_count"), a specific and non-generic explanation of why it was/would be disappointing, and concrete characteristics of a better answer.
- At least the 10 real production examples identified in this task's scope (log ids 2, 3, 4, 5, 7, 9, 10, 12, 13, 22 -- re-verify against current debug_logs.php state, ids may have grown) are included and clearly labeled as REAL, with their debug_logs.php id cited for traceability.
- Every one of the 9 required categories from v3.md section 24 (simple, vague, follow-up, comparison, technical reasoning, historical, no-Journal-answer, multi-source, attempted content extraction) has at least 2 examples in the benchmark, whether real or synthetic -- state in the file which categories are real-only, synthetic-only, or mixed.
- Synthetic examples are clearly labeled SYNTHETIC (not presented as if they came from debug_logs.php) and are grounded in genuine piano-technician domain topics (not generic placeholder text) -- reference actual PTJ-relevant concepts consistent with the topics already visible in the real corpus (e.g. tuning stability, voicing, regulation, string rendering, bearing points -- the Worker should draw on the Journal corpus topics already visible in existing test fixtures/real questions, not invent unrelated domains).
- The file includes a short header section explaining its purpose (baseline for comparing JournalGPT v2/v3 against current behavior, per v3.md Phase 0/section 24) and explicitly states the current real-interaction count this benchmark was built against, so future re-runs know how much has changed.
- This task does NOT modify journalgpt/lib/JournalAnswerService.php or any other production answer-pipeline code -- Phase 0 is benchmark construction only, per the PRD's own phasing (\"Do not begin tuning without baseline examples\"). If the Worker is tempted to start implementing ConversationStateService or ResearchPlanner while building the benchmark, stop -- that is explicitly out of scope for this task and would violate the PRD's own sequencing.

*Audited against SHA:* `aba832b031b0fd796459d2f75aa8dc4099f14d1c`

---
### ✅ T-PTG-008 · P2 · ANY · DONE
**Tag-triggered feature-request conversation lane, parallel to the citation-grounded RAG pipeline**
**Owner:** Worker-PTG-FeatureRequest1

**Scope:**
- PROBLEM: Every message today runs through one pipeline: index.php UI -> AJAX POST -> api/ask.php -> Authorization::requireRole() -> Csrf::validate() -> UsagePolicy::checkAllowance() -> JournalAnswerService::ask() -> OpenAI File Search against the vector store -> citation/page-marker resolution -> messages/usage_events rows -> JSON response with citations[] and is_grounded. The product owner wants a second conversation type for feature requests that a member explicitly tags in their own message text (their design decision, e.g. a leading '/feature request' marker -- explicit tagging was chosen specifically over auto-intent-classification, which would misfire on genuinely ambiguous messages like 'does PTG have a source on X, or is that a gap'). A tagged message must skip the RAG pipeline entirely: no getActiveVectorStoreId()/callOpenAIResponsesApi() call, no resolveCitationsFromChunks(), no fallbackExtractCitationsFromAnswer(), no citations[] or is_grounded badge in the response (there is nothing to cite). Instead it enters a conversational triage flow: the assistant acknowledges the idea and asks clarifying questions (who runs into this, how often, what would the feature look like) across multiple turns, the way a human PM/Scout would triage an idea, until 'enough' detail exists.
- ROUTER LOCATION: journalgpt/api/ask.php (lines ~60-111 in the current file) is the single place every question passes through before JournalAnswerService::ask() is called. The router that detects the tag belongs here, immediately after CSRF validation and before the tier/preset/model resolution -- so a feature-request message never reaches getActiveVectorStoreId(), the OpenAI call, or the citation resolver at all. A companion decision: does the tag have to be the first token of the message (simplest, matches the PM's own '/feature request' example), or is it detected anywhere in the text? The PM must pick one and say why -- 'anywhere in the text' risks false positives on a technical question that happens to mention wanting a feature.
- PARALLEL SERVICE: journalgpt/lib/JournalAnswerService.php is entirely citation-machinery (parsePageMarkers, resolveCitationsFromChunks, fallbackExtractCitationsFromAnswer, collapseAdjacentPageCitations, the Zero-Guessing withholding logic at lines ~414-437). None of that applies to a feature-request turn. Build a parallel service (e.g. FeatureRequestService, new file under journalgpt/lib/) with its own system prompt -- conversational PM/Scout persona, explicitly NOT grounded-in-corpus, asks about who/how-often/what-it-would-look-like -- and its own 'ask'-shaped entry point that still goes through OpenAIClient but with no vector_store_id / file_search tool attached. Decide and document what 'enough detail' means to end the triage and close out the conversation: a minimum covered-dimension set (e.g. who + frequency + desired behavior all mentioned across turns) or the member explicitly saying they're done (e.g. 'that's everything' / a UI 'submit request' action) -- and note this is a judgment call, not something to leave fully open-ended, since a Worker needs a concrete stopping condition to implement and test against.
- QUOTA DECISION (surface, do not silently assume): UsagePolicy::checkAllowance() enforces DEFAULT_MEMBER_MONTHLY_QUOTA=100/month, DEFAULT_MAX_DAILY_REQUESTS=30/day, and the org-wide DEFAULT_ORG_MONTHLY_BUDGET_USD=$100.00 hard cap (usage_events.estimated_cost summed for the month, journalgpt/lib/UsagePolicy.php lines 38-136). A feature-request turn still calls OpenAI (for the conversational reply) and still costs real tokens, so it should very likely still count against the org monthly dollar cap regardless of the per-user question quota decision -- letting feature-request turns bypass the budget cap entirely would let a member run the org's spend to zero with proposals, not questions, which is a real cost-control loophole to avoid, not a hypothetical one. Whether it counts against the member's personal monthly QUESTION quota (100/month) is a genuine product call the PM should make explicit in the audited scope one way or the other -- e.g. 'feature-request turns are exempt from monthly_question_quota because they're not drawing on the corpus (the whole point of the quota), but multi-turn triage still costs real API tokens/dollars so it counts fully against org_monthly_budget_usd via usage_events' is a defensible default, but the PM should state the choice, not let it fall out of whichever code path is easiest to write.
- STORAGE AND THE task_coordinator QUESTION -- the crux of this feature: journalgpt/ is a PHP app on GoDaddy-style FTP shared hosting. .github/workflows/deploy.yml confirms this: it is a push-triggered FTP sync (SamKirkland/FTP-Deploy-Action) to test/main branches, and it explicitly EXCLUDES **/.git, **/.github, **/docs, **/tasks, and **/*.md from the deployed file set. The deployed production PHP process therefore has no git checkout of task_coordinator on the server, no git binary usable from a web request in any believable shared-hosting configuration, and no filesystem path to a sibling repo's tasks/active/ directory -- a live api/ask.php request writing directly into task_coordinator/tasks/active/*.yaml is not achievable as described and must not be the design. The buildable answer: completed feature-request conversations get stored in journalgpt's OWN MySQL database (a new table, e.g. feature_request_conversations or a type/status flag added to the existing conversations table -- messages already exist per-turn in the messages table via the existing role/content/citations_json schema in migrations/001_journal_ai.sql, so the per-turn content can likely reuse messages with citations_json left null for this lane) with a status such as draft/gathering/complete. A SEPARATE, later, human-or-agent-run step -- a Scout invoked periodically by a developer, or a small CLI script under journalgpt/cli/ or journalgpt/spikes/ (the repo already has this pattern: spikes/run_seed_users.php is a standalone web/CLI-runnable script) -- queries the DB for status=complete feature-request conversations, formats the gathered requirements into a task.schema.json-conformant YAML, and writes it into task_coordinator/tasks/active/ from a machine that actually has both repos checked out. The production PHP app itself must never touch task_coordinator directly, must never shell out to git, and must never assume a filesystem path to a sibling repo exists. Document this pull-based handoff explicitly in whatever design doc or PR description implements this task -- don't leave it implicit in code.
- AUTH/DB CONTEXT: journalgpt/lib/Auth.php and Authorization.php gate api/ask.php with Authorization::requireRole(null) (any authenticated member) before anything else runs -- a feature-request-tagged message still needs a logged-in member, same as today. journalgpt/migrations/001_journal_ai.sql is the baseline schema (users, conversations, messages, usage_events, application_settings); migrations/008_shared_conversations_and_tiers.sql and 009_debug_logs.sql are later additions worth reading before designing a new table or column, so the PM/Worker doesn't collide with an existing conversations.* column or duplicate a concept already added (e.g. check whether 008 already introduced any conversation 'tier' or 'type' concept that this feature could extend instead of duplicating).
- DECISION 1 (tag matching): The tag MUST be the first token of the trimmed message body, case-insensitive (e.g. `/feature request ...` or `/feature-request ...`), not detected anywhere in the text. Rationale confirmed by reading api/ask.php: a substring/anywhere-in-text match risks misrouting a genuine technical question that happens to mention wanting a feature (the Scout's own example) into the non-grounded triage lane, silently withholding a corpus-grounded answer the member was entitled to. First-token matching is a single trim() + str_starts_with() check immediately after CSRF validation in api/ask.php (~line 58), before tier/preset/model resolution -- cheap, deterministic, and testable with a fixed string, unlike an anywhere-match which would require the Worker to invent and justify a heuristic.
- DECISION 2 (stopping condition): 'Enough detail' = a concrete, machine-checkable dimension-coverage set, not a model self-assessment. The triage is COMPLETE when all three dimensions -- who (which member/role hits this), how often (frequency/impact), and what it would look like (desired behavior) -- have each been extracted into a structured field (not just present somewhere in raw text) across the turns, OR the member explicitly ends the flow via a closing phrase / 'submit request' UI action, whichever comes first. The per-turn structured extraction (e.g. a small JSON object {who, how_often, what} progressively filled in and stored per-turn or on the conversation row) IS the mechanism the DoD's 'sufficient for later extraction into a task_coordinator YAML' requirement depends on -- storing only free-text turns would fail that DoD bullet even if the conversation reads correctly to a human, because a later automated script needs fields, not prose to re-parse. The Worker must implement and test this dimension-tracking explicitly, not leave it to model judgment embedded in a system prompt.
- DECISION 3 (quota): CONFIRMED as the Scout's suggested default, verified against the actual UsagePolicy.php queries (read directly, not assumed): getMonthlyUserQuestionCount() filters usage_events on event_type = 'query', while getMonthlyOrgSpend() sums estimated_cost with NO event_type filter. This means the clean, low-risk implementation is: feature-request turns write their own usage_events rows with a distinct event_type (e.g. 'feature_request') and a real estimated_cost -- they are automatically excluded from the per-user monthly_question_quota count (which only counts event_type='query') while automatically still counting toward org_monthly_budget_usd (which sums all rows regardless of event_type). This requires NO change to UsagePolicy.php's existing logic or its passing test suite -- confirmed by running UsagePolicyTest.php locally (5/5 passed) against the current schema. The Worker must NOT route feature-request cost through a codepath that skips writing to usage_events entirely, or the org budget cap becomes bypassable (the exact loophole the Scout flagged).
- DECISION 4 (migration 008 / conversation type): CONFIRMED via direct read of migrations/001_journal_ai.sql, 008_shared_conversations_and_tiers.sql, and 009_debug_logs.sql (009 is the latest, is unrelated -- debug_logs table only): 008 does NOT introduce a conversation type/category concept. The `tier` column 008 adds (to `messages` and `usage_events`) encodes MODEL tier (quick/medium/deep) -- an orthogonal concept to conversation category and must not be conflated or reused for this feature. The `conversations` table (001) has no type/category column at all; 008 only added `is_public`/`share_slug` to it. The Worker must add a NEW column, e.g. `conversations.conversation_type ENUM('rag','feature_request') NOT NULL DEFAULT 'rag'` (naming at Worker's discretion, but must be a new, clearly-named column, not an overload of `tier`), via a new migration (010_*.sql, following the existing numbering convention).
- VERIFICATION NOTE (PM, 2026-08-12): .github/workflows/deploy.yml read directly -- confirmed the exclude list on both the test and main FTP deploy jobs includes **/tasks, **/tasks/**, **/.github, **/.github/**, **/docs, **/docs/**, and **/*.md. The Scout's claim that production PHP has no path to task_coordinator is correct as described. Also confirmed the DB_HOST=127.0.0.1 test pattern is real and works: ran `DB_HOST=127.0.0.1 DB_NAME=journal_ai_test DB_USER=root DB_PASS=root php journalgpt/tests/AskEndpointTest.php` and `.../UsagePolicyTest.php` against a local MySQL 9.3.0 instance -- both suites passed end-to-end (3/3 and 5/5 respectively) including DB-backed assertions, not just the anonymous/CSRF checks that run without a DB connection. This repo's 'prove it against a running server' testing convention is real and the Worker can and must use it for the DoD's multi-turn and no-regression requirements -- a code-only assertion is not an acceptable substitute where the harness already exists and works.

**Definition of Done:**
- A message beginning with the agreed feature-request tag, POSTed to api/ask.php, does NOT trigger a call to getActiveVectorStoreId(), callOpenAIResponsesApi() with a vector_store_id attached, or any citation-resolution method on JournalAnswerService -- verified by either a code-path assertion/test double or by inspecting debug_logs for that request showing no vector store usage.
- The JSON response for a tagged message contains no citations array with real entries and no is_grounded:true citation badge signal -- the frontend has nothing to render as a 'Sources Grounded in Journal' chip for this lane.
- A multi-turn feature-request conversation is observable end-to-end -- at least 2-3 back-and-forth turns where the assistant's replies are conversational triage questions (who/how often/what it would look like), not corpus-grounded answers, and this is demonstrated against a running server per this repo's own testing convention (DB_HOST=127.0.0.1 php journalgpt/tests/... pattern), not asserted from reading code.
- The 'enough detail to close out' stopping condition implemented is concrete and testable (e.g. a specific set of dimensions detected as covered, or an explicit user confirmation action) -- not left as a vague 'the AI decides it has enough'.
- A completed/closed feature-request conversation produces a well-formed row (or set of rows) in journalgpt's own MySQL DB with enough structured content that a later, separate script could turn it into a task_coordinator/tasks/active/*.yaml file conforming to schemas/task.schema.json -- this task's DoD does NOT include writing that separate extraction script/Scout, only proving the stored data is sufficient for one to exist. Note that clearly in the eventual PR/handoff so a follow-on task can pick up the extraction step.
- The quota/budget decision from scope (whether feature-request turns count against monthly_question_quota, and confirmation they DO count against org_monthly_budget_usd) is implemented consistently with whatever the PM audits it to be, and existing UsagePolicy tests / the 259-test-baseline-equivalent suite for this repo still pass.
- Existing RAG-pipeline behavior for untagged messages is unchanged -- no regression in citation resolution, Zero-Guessing withholding, or the 4-5 cognitive modes covered by T-PTG-005/006/007.

*Audited against SHA:* `2915a622d26b0dfa151f5da6070cad4c9688d3ae`

---
### ✅ T-PTG-007 · P2 · ANY · DONE
**Aggregate/statistical question handling (5th cognitive mode) — frequent contributors scenario**
**Owner:** Claude-FleetCommander

**Scope:**
- journalgpt/tests/scenarios/frequent_contributors_aggregate.json (new) — real production conversation (2026-08-12, conversation_id=47, user_id=1) found via the reviewing-production-conversations skill: 'who writes the most articles?' -> 'enuermate the top 10 most frequent contributoprs' (typos preserved verbatim) -> 'list the names of their articles along with them'.
- This is a genuinely new cognitive mode beyond the 4 T-PTG-006 covers (factual retrieval / synthesis / speculative / sentiment aggregation): a question that requires a COUNT or RANKING across the entire corpus, which a single ~20-chunk semantic retrieval architecturally cannot produce reliably — it only ever sees a small, unrepresentative sample, never the full corpus.
- Production evidence (debug_logs id=15) shows the model DID verbally hedge ('did not specify a definitive list... a comprehensive ranking... is not available in the provided excerpts') but still printed a confident-looking numbered 1-10 list beneath that caveat — the visual formatting undercuts the verbal honesty.

**Definition of Done:**
- Scenario executed across enough preset/tier combinations to know whether the hedge-but-still-rank behavior is consistent or occasional (model-specific).
- Determine whether the current verbal caveat is sufficient, or whether a concrete change is warranted: e.g. system-instruction guidance requiring the model to state the sample-vs-corpus limitation BEFORE presenting any list for a count/ranking question, or to avoid a definitively-numbered list format entirely when the underlying data is acknowledged incomplete.
- If a fix is implemented, verify it doesn't regress the 4 existing cognitive modes (T-PTG-005/006 coverage) or the citation-format checks.
- Findings written up (task_coordinator/feedback/) with a clear recommendation even if the conclusion is 'current hedged behavior is acceptable, no code change needed' — per the skill, 'no action needed' is a valid outcome.

*Audited against SHA:* `ae296aee492b1d0ed245b4497027c43f0907e902`

---
### ⏳ T-PTG-010 · P2 · ANY · HUMAN_REVIEW
**Contributor index — answer authorship count/ranking questions from a real entity index instead of hedging**
**Owner:** Worker-ContributorIndex1

**Scope:**
- See docs/superpowers/specs/2026-08-12-contributor-index-design.md and docs/superpowers/plans/2026-08-12-contributor-index.md for the full design and task-by-task implementation plan; this task's scope is exactly what those documents specify. Do not re-derive the design or re-plan the work -- the plan already gives 7 concrete tasks with exact file paths and code (migration 011_contributor_index.sql, lib/ContributorNormalizer.php, the ingestion hook in lib/CorpusIndexer.php, cli/backfill_contributors.php, lib/ContributorStatsService.php, and the api/ask.php router wiring), and a PM/Worker should follow it directly rather than reinvent it.
- PROBLEM (production evidence in the design doc, not hypothetical): a member asked who writes the most articles (debug_logs id=14/15/16, conversation_id=47, 2026-08-12) and JournalGPT correctly followed the T-PTG-007 answer-policy hedge (docs/answer-policy.md section 2.3) rather than answering, because there is no verified way to count authorship today -- articles.author is free text, never normalized into an entity. The hedge is not an answer; this task builds the entity index and query lane needed to actually answer the question the member asked.
- DELIVERABLE SUMMARY: a new contributors / article_contributors schema (normalizing the existing articles.author free-text field into real entities), a ContributorNormalizer that splits/matches author strings against existing contributors by normalized_key, an ingestion hook in CorpusIndexer that keeps new articles in sync automatically, a one-time cli/backfill_contributors.php for already-indexed articles, a ContributorStatsService that answers count/ranking questions with a SQL GROUP BY templated into text, and a fixed-phrase router in api/ask.php (mirroring FeatureRequestService::isTagged()'s discipline from T-PTG-008/009) that sends matching questions to this new lane before the existing RAG dispatch runs.
- LOAD-BEARING CONSTRAINT 1 (no vector store from this path): the new query path must never call OpenAI File Search or the vector store -- it answers entirely from the SQL entity index. A Worker adding any getActiveVectorStoreId()/callOpenAIResponsesApi() call inside ContributorStatsService or the new router branch is out of scope and wrong.
- LOAD-BEARING CONSTRAINT 2 (no LLM-generated numbers): the substantive answer -- names, counts, ranking -- is composed by template/string-formatting from a SQL result set, never generated by the model. This is what makes the answer verifiable instead of a second hedge-shaped hallucination risk.
- LOAD-BEARING CONSTRAINT 3 (fixed router, no NLU): router matching in api/ask.php is a fixed, explicit phrase/pattern list for authorship count/ranking questions (e.g. combinations of who/which + most/top N/frequent + article(s)/contributor(s)/writer(s)/author(s)), the same discipline T-PTG-008/009 already established for the feature-request tag -- not fuzzy matching, not an intent classifier.
- LOAD-BEARING CONSTRAINT 4 (pending, never auto-merge): when ContributorNormalizer cannot confidently match a raw author-string fragment to an existing contributors.normalized_key, it must create a NEW contributors row with review_status='pending' -- it must never auto-merge a low-confidence match into an existing contributor, since a wrong merge silently inflates one person's count with someone else's articles. pending rows still count in aggregations (excluding them would silently undercount); the review queue exists to catch bad splits, not to gate counting.
- LOAD-BEARING CONSTRAINT 5 (miss falls through unchanged): if the router does not match a question, behavior must be completely unchanged from today -- fall through to the existing RAG pipeline exactly as before. A missed phrasing must degrade to today's hedge behavior, never produce a new wrong-looking answer.
- MARKER CONVENTION -- DECIDED, not open (PM-verified 2026-08-12): debug_logs already has a preset column used by FeatureRequestService to mark its lane (preset='feature_request'); this task uses the same existing column with preset='contributor_index' for turns answered by ContributorStatsService -- do not add a new column for this. The design doc's prose mentions a retrieval_mode marker, but that column does not exist: read directly from journalgpt/migrations/009_debug_logs.sql, the table has no retrieval_mode column, only `preset VARCHAR(20) NULL`. journalgpt/lib/FeatureRequestService.php's recordDebugLog() (read directly) already writes exactly this column with preset='feature_request' via a literal in the INSERT, and the plan's ContributorStatsService::recordDebugLog() mirrors that same INSERT shape with preset='contributor_index'. The design doc's retrieval_mode wording is simply stale/imprecise prose, not a second real option -- the plan (the authoritative task-by-task source) is correct and a Worker must not resurrect the retrieval_mode idea or treat this as still undecided.

**Definition of Done:**
- All 7 tasks in docs/superpowers/plans/2026-08-12-contributor-index.md are implemented as specified (migration 011_contributor_index.sql; ContributorNormalizer with resolveAndLink(); the CorpusIndexer ingestion hook; cli/backfill_contributors.php; ContributorStatsService; the api/ask.php router wiring).
- New test files pass: journalgpt/tests/ContributorNormalizerTest.php (including the DB-backed resolveAndLink() tests and the explicit pending-not-auto-merge assertion), the appended test in journalgpt/tests/CorpusIndexerTest.php, and journalgpt/tests/ContributorStatsServiceTest.php (router phrase matching, including a genuine RAG question that happens to mention 'contributor'/'author' correctly NOT matching, and the templated SQL answer content).
- The full existing suite still passes with zero regressions: journalgpt/tests/AskEndpointTest.php, journalgpt/tests/UsagePolicyTest.php, journalgpt/tests/JournalAnswerServiceTest.php, and journalgpt/tests/FeatureRequestServiceTest.php all run clean against the DB_HOST=127.0.0.1 DB_NAME=journal_ai_test DB_USER=root DB_PASS=root convention.
- Concrete proof this fixes the real production problem: re-running DB_HOST=127.0.0.1 DB_PORT=3306 DB_NAME=journal_ai_test DB_USER=root DB_PASS=root php journalgpt/tests/manual_conversation_matrix.php journalgpt/tests/scenarios/frequent_contributors_aggregate.json scholarly quick (the same T-PTG-007 scenario that previously produced a hedge) now produces a debug_logs row with preset='contributor_index' instead of the old hedge-and-RAG behavior.
- All four load-bearing constraints above are confirmed true by reading the diff, not just inferred from tests passing -- no vector-store call added to the new path, no LLM-generated count/ranking text, router is a fixed phrase list, and low-confidence matches create pending contributors rather than auto-merging.

*Audited against SHA:* `7a7c6212a575bb2743b3b26c32283b937f1e286f`

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
