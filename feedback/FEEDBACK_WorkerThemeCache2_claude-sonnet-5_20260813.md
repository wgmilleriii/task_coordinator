# Feedback: Worker-ThemeCache2 / claude-sonnet-5 / 2026-08-13

## Task outcome: SUBMITTED — T-PTG-013 now in PEER_REVIEW

Claimed successfully once the Fleet Coordinator removed the redundant
`dependencies: [T-PTG-012]` entry. Implemented the fix, verified it, merged to
`main` (`604d1be..aba832b`), and ran `./bin/fleet submit T-PTG-013`. Task is now
`PEER_REVIEW`, awaiting human close.

## Caching hypothesis: CONFIRMED (mechanism-level + partial live reproduction)

- `curl -sI https://newmexicoptg.org/journalgpt/assets/journal-chat.css` reconfirmed
  no `Cache-Control` header in production (only `last-modified`/`etag`), matching
  the Scout's original finding.
- Pulled the pre-T-PTG-012 revision of `journal-chat.css`
  (`git show 6e11fdd~1:journalgpt/assets/journal-chat.css`) and confirmed it has
  **zero** `data-theme` rules (`grep -c data-theme` = 0) — structural proof that a
  browser holding that cached copy would see `data-theme` change with no matching
  CSS rule to apply, exactly the reported symptom.
- Reproduced the request-level half end-to-end locally: `php -S` against the test
  DB, a real test user inserted via `Auth::hashPassword()` (same pattern as
  `AskEndpointTest.php`), a cookie-jar curl login session, swapped the pre-theme
  CSS onto disk, fetched `changelog.php` as the logged-in user (served the 0-rule
  CSS, matching a browser's first cached fetch), then restored the current CSS and
  confirmed all seven pages now emit an identical `?v=<hash>` query string tied to
  the git commit.
- Could **not** do a full real-browser cache-persistence reproduction (curl and
  `php -S` don't implement HTTP heuristic caching the way an actual browser does,
  and there was no way to reach the product owner directly for a live hard-refresh
  confirmation in this environment). Per the task's explicit fallback instruction,
  I documented this gap and relied on the no-`Cache-Control`-header fact plus the
  structural CSS-content proof as sufficient mechanism-level evidence, stated
  explicitly in `peer_review_notes` in the handoff.
- No second bug found. Fix scope matches the task exactly.

## What changed

- New `journalgpt/lib/AssetVersion.php` — `JournalGPT\AssetVersion::gitCommitHash()`,
  a single shared implementation of the `version.json` → `git rev-parse --short HEAD`
  → hardcoded-fallback chain that `index.php` used to compute inline.
- `index.php` refactored to call the shared helper instead of its own inline copy
  (net logic unchanged, just deduplicated).
- `changelog.php`, `source.php`, `admin_migrate.php`, `login.php`, `featured.php`,
  `help.php` — each now `require_once`s `AssetVersion.php`, computes
  `$gitCommitHash = AssetVersion::gitCommitHash();`, and links
  `assets/journal-chat.css?v=<?= htmlspecialchars($gitCommitHash, ...) ?>` instead
  of the plain unversioned URL. `theme-switcher.js` was left untouched (out of
  scope per the task; no second bug found there).
- All seven pages now emit an identical `?v=` hash per request, verified via a
  logged-in curl session hitting each page directly.

## System-Level Feedback (Fleet Coordinator engine)

1. **The prior Worker's claim-rejection diagnosis was independently verified
   false, and this is worth flagging as a recurring risk pattern.**
   Worker-ThemeCache1 was correctly rejected by `fleet claim`'s dependency check
   (T-PTG-012 was `PEER_REVIEW`, not `DONE`), but then reasoned from that
   rejection to a *stronger* claim — "T-PTG-012's actual work lives only on the
   unmerged `worktree-color-schemes` branch, not on `main`" — based on a
   `git worktree list` snapshot, without re-checking `main` itself at time of
   writing that feedback. By the time T-PTG-013 was re-audited (`604d1be`,
   *after* T-PTG-012's merge commit), that claim was already false, but it had
   been written into a feedback file as established fact. I only avoided
   repeating it because this task's briefing explicitly told me to re-verify
   directly (`git log --oneline -3 main` + the `data-theme-picker` grep across
   all 7 files) before proceeding — I would not have otherwise had a strong
   reason to doubt a prior Worker's specific, evidenced-looking claim. **Lesson
   for the coordinator/future workers: a dependency-claim rejection proves only
   that the dependency's *status field* isn't `DONE` yet — it says nothing about
   whether the dependency's code has already landed on `main` by the time you
   read the rejection. Treat "is the code on main" as its own question requiring
   its own fresh `git log`/`grep`, never inferred from a claim-gate error message
   or from another Worker's snapshot of `git worktree list` taken at an earlier
   moment.** This also argues for Worker-ThemeCache1's suggestion (audit-time
   dependency validation, or at least a `TASKS.md` blocked-marker) so that a
   rejected claim doesn't get over-interpreted by the human or a future agent
   reading the feedback file later without re-verifying.
2. The `./bin/fleet verify` → fill `head_sha` → `submit` flow worked cleanly
   end-to-end once unblocked. `fleet verify` captured full stdout/stderr
   evidence automatically, which was useful.
3. `peer_review_notes` was a good place to put the explicit root-cause
   confirmation/fallback narrative the DoD required — worth documenting as the
   canonical field for that in the coordinator's own docs, since I had to infer
   it wasn't schema-restricted by trial.

## Repository-Level Feedback (newmexicoptg.org)

1. Confirmed `main` at session start (`604d1be`) already had T-PTG-012's picker
   markup and Dark/Sepia/PTG CSS blocks live on all 7 pages
   (`grep -c data-theme-picker` = 1 for every file) — the prior Worker's
   diagnosis describing `main` as pre-T-PTG-012 was stale/wrong by the time this
   session ran.
2. The git-hash cache-busting pattern was previously duplicated only in
   `index.php`; now centralized in `journalgpt/lib/AssetVersion.php` alongside
   the other single-purpose lib classes (`Auth.php`, `Csrf.php`, etc.) — same
   namespace/style convention as `Database.php`/`Auth.php` (`namespace
   JournalGPT;`), not the `JournalGPT\Lib` namespace `Config.php` uses, since
   `Config.php` serves a different purpose (secrets loading) and the sibling
   files this helper is peer to (`Auth`, `Database`, `Csrf`) all use the bare
   `JournalGPT` namespace.
3. `journal-chat.css` still has no `Cache-Control` header in production — this
   was explicitly out of scope per the task (cache-busting query param was the
   established pattern to extend, not a new server header), but worth a human
   noting for a future hygiene pass: a `Cache-Control: public, max-age=<N>`
   header alongside the existing cache-busting query param would let browsers
   cache the *current* asset confidently between deploys instead of relying on
   undefined heuristic caching, while the `?v=` param still forces a fresh fetch
   on every deploy either way.
4. Test artifacts: created one test user (`theme_cache_test@test.local`) in the
   local `journal_ai_test` DB via `journalgpt/tests/create_test_user_tmp.php`,
   which was deleted before finishing (never committed — `git status` confirms
   clean). The DB row itself was left in the local test DB (harmless, same DB
   used and reset by the existing test suite's own `DELETE FROM users WHERE
   email = ...` pattern).

## Recommended next step for the human

Task is in `PEER_REVIEW` at `newmexicoptg.org@aba832b`. The handoff
(`task_coordinator/handoffs/T-PTG-013_handoff.yaml`) `peer_review_notes` field
has the full confirmation narrative. Worth a final live spot-check on
`https://newmexicoptg.org/journalgpt/changelog.php` after this deploys, ideally
from a browser that actually had the site loaded before today, to close the loop
on the one gap this session couldn't cover (a real, persistent browser HTTP
cache).
