# Feedback: Worker-Normalize1 (claude-sonnet-5) — 2026-08-13

Task: T-INTY-024, repo: intypiano. Final status: submitted, `PEER_REVIEW`,
worktree `/Users/willismiller/Documents/GitHub/intypiano-T-INTY-024` branch
`test-T-INTY-024`, commit `d4dba711792c5368808ff9a989f5307d50fb0f4c`.

## System-Level Feedback

1. **The repo-level claim lock genuinely blocked me for a while, and that's
   correct behavior, not a bug** — but it's worth flagging how it interacts
   with a multi-agent swarm working the same repo. I hit `❌ Cannot claim
   T-INTY-024. Repo 'intypiano' is locked by T-INTY-022 (Worker-LoginFix1)`
   immediately on my first claim attempt, before I'd done anything else. I
   polled with a bounded `until`/`sleep 20` loop in the background rather
   than busy-waiting in the foreground, which let me use the dead time
   productively (read the target file, read GazelleAPI.php, pulled DB
   baselines) — but a future worker without something useful to do while
   blocked would just be stuck. Worth considering whether `fleet claim`
   could optionally block-and-retry itself with a timeout, or whether the
   coordinator should proactively route new claims away from a locked repo
   lane instead of leaving each worker to discover the lock by trying and
   failing.
2. **`fleet verify`'s automated command runs in the primary clone, not the
   worktree.** This is documented behavior (T-INTY-023's feedback flagged
   the same thing) but it means the "evidence" the CLI auto-captures for
   `php -l` is trivially true on both the old and new file and proves
   nothing about the actual fix. I followed the established pattern from
   T-INTY-023's handoff: note this explicitly at the top of `evidence_output`
   and put the real evidence in a clearly-labeled manual section after it.
   This works, but it's now two workers independently reconstructing the
   same disclaimer text by hand. If this is going to keep being true for
   every worktree-based task, it might be worth `fleet verify` detecting an
   adjacent `<repo>-<TASK-ID>` worktree and running the verification command
   there instead of (or in addition to) the primary clone automatically.
3. `./bin/fleet verify` requires `--model` but the README's own step-by-step
   instructions (`### 4. Provide Evidence & Complete`) don't mention it —
   I had to discover the flag from the CLI's own usage error. Minor, but
   worth a doc update.
4. The claim → worktree → verify → submit flow worked cleanly once the lock
   cleared. `TASKS.md` regeneration correctly reflected only my task's status
   transition in the diff, which made it easy to `git add` narrowly and avoid
   stepping on other concurrent agents' uncommitted PTG-lane files sitting in
   the same working tree.

## Repository-Level Feedback (intypiano)

1. **The bug was exactly as scoped, and worse than it looked from just
   reading the code.** `admin/v2/normalization.php`'s POST handler only ever
   wrote `UPDATE inventory SET make = ?`. But I found a second, independent
   problem the task's scope didn't call out: the "Unique Piano Makes" listing
   query that drives the UI also only read from `inventory`. For a
   pianos-only tenant like `caut_sfusd` (162 pianos rows, 0 inventory rows),
   that meant the page rendered "No pianos found in inventory" with zero
   buttons to click — even after fixing the write path, a human would have
   had nothing to normalize through the UI for the exact tenant this task
   exists to fix. I unioned `pianos` + `inventory` for the makes listing and
   added a parallel "Unique Piano Models" listing sourced from `pianos`
   (blank/NULL grouped as a visible `(blank)` row), since fixing the write
   path alone would have been a fix nobody could reach.
2. **A second, unrelated pre-existing bug blocked all live verification**:
   the file called `renderV2Header()`/`renderV2Footer()`, functions that
   don't exist anywhere in the codebase (confirmed by grepping the whole
   `admin/v2/` tree — the real functions other v2 pages use are
   `v2_head()`/`v2_foot()` from `_layout.php`). This page 500'd on every
   single load before my change, for reasons having nothing to do with the
   normalization bug. I fixed the two call sites to match the rest of v2.
   This is worth a human's attention: it means this admin page has likely
   never actually been loaded successfully in production since it was
   written — the make-normalization bug this task was tracking may never
   have been *observed* by a human clicking through the UI, only found by
   reading the source.
3. **Local login for `cmiller` on `intypiano_demo` needed the exact fix
   CLAUDE.md's testing section anticipates**: `users.password_hash` was
   NULL. `users.email` was already populated (`cmiller@example.edu`), so I
   only needed to set the bcrypt hash for `localdev1`, not touch email. This
   matches the documented pattern closely enough that I'd suggest baking the
   `password_hash` reset into whatever script maintains the demo pool, so
   the next worker doesn't rediscover this by hand.
4. **Testing `caut_sfusd` through the live dev server isn't straightforward.**
   `DatabaseManager`'s tenant routing is keyed off `$_SERVER['SERVER_NAME']`
   (i.e. the `Host` header / `SERVER_NAME` string), and none of the
   `localhost`-matching branches route to `caut_sfusd` — only a real
   `sfusd.chipmiller.me`/`sfusd.cauttools.com` hostname does, and that
   branch hardcodes `caut_sfusd`'s real DB credentials which don't exist in
   my local MySQL. Rather than mess with `/etc/hosts` or grant new MySQL
   users (both out of scope for this task and both would leave residue),
   I used the same `$r->dbdb` override technique `scripts/set_password.php`
   and the Integration test suite already use to get a real `DatabaseManager`
   connection to `caut_sfusd` from a throwaway CLI script, and ran the exact
   `UPDATE pianos SET make = ? WHERE make = ?` statement the handler now
   issues against it directly — confirming `'Steinway #444'` (the task's own
   example) correctly becomes `'Steinway'`, with `inventoryAffected=0` as
   expected since that tenant genuinely has 0 inventory rows. This felt like
   solid evidence for the specific tenant scenario the task was written
   about, without needing to touch tenant-routing config. Worth documenting
   this `$r->dbdb` override pattern in `docs/experts/` somewhere if it isn't
   already, since this is now three separate contexts (this task, T-INTY-023,
   and the existing test suite) independently relying on it to reach a named
   tenant DB outside the hostname-routing path.
5. **Regression discipline**: ran the full 330-test phpunit suite twice on
   the identical worktree/commit, once with my change applied and once
   `git stash`ed back to the original file. Both runs produced the exact
   same 330 tests / 1 error / 68 failures. CLAUDE.md's documented baseline
   ("259 tests, 0 failures") is stale relative to the current `master` HEAD
   — there's real drift here worth a human's attention independent of this
   task, since a stale baseline in the project's own instructions makes it
   easy for a future agent to wrongly attribute pre-existing failures to
   their own change, or the reverse (miss a real regression because "some
   failures are expected").

## Recommended next steps for the human

1. Review `test-T-INTY-024` (`d4dba711792c5368808ff9a989f5307d50fb0f4c`) in
   `/Users/willismiller/Documents/GitHub/intypiano-T-INTY-024` — single file
   changed, `admin/v2/normalization.php`. The worktree is left in place per
   instructions.
2. Consider whether the `renderV2Header`/`renderV2Footer` fix belongs in
   this PR (I judged it in-scope since it blocked the DoD's live-verification
   requirement entirely) or should be split into its own tracked fix — it's
   a real, separate pre-existing bug that happens to live in the same file.
3. The stale phpunit baseline in `CLAUDE.md` ("259 tests, 0 failures") vs.
   the current actual state (330 tests, 1 error, 68 failures on unmodified
   `master`) is worth a follow-up task of its own — either update the
   documented baseline or investigate whether the 68 failures represent a
   real, unnoticed regression from whatever landed between those two states.
