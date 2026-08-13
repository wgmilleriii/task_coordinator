# Feedback: T-PTG-014 (Worker-AdminReply3, claude-sonnet-5, 2026-08-13)

## Task outcome

Built `journalgpt/admin_reply.php` (a small reusable admin tool letting any
authenticated pilot user post a `role=assistant` message into an existing
conversation) plus `journalgpt/tests/AdminReplyTest.php`. Verified locally
(`./bin/fleet verify` passed), manually tested end-to-end via the `/browse`
skill against a local PHP dev server, merged `test-T-PTG-014` into `main`,
pushed, and submitted via `./bin/fleet submit` — task is now in
`PEER_REVIEW` (head_sha `03f07bf18dbe3b092cea9980ac8719fe84deb563`).

**The real-production step (posting into conversation_id=51) was NOT
completed.** This environment has no usable production DB credentials:
`journalgpt/.env` only has local test-DB creds (`127.0.0.1:8889` /
`journal_ai_test`), and I found a second candidate config file,
`journalgpt/journalptg_config/secrets.json`, but every field in it
(`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`) is a literal placeholder string
(`REPLACE_WITH_PRODUCTION_REAL_VALUE`) — not real credentials. I did not
fake or simulate this step. **The product owner (Chip) needs to log into
`admin_reply.php` on the live site himself, once this branch is deployed to
production, to send the notification to conversation 51.**

Suggested exact message text (warm, brief, accurate, matches what T-PTG-012
actually shipped — 4 themes, picker on every page; I did not invent detail
beyond that):

> Hi! Quick update — the color scheme option you asked about is live. You
> can now switch between four themes (Light, Dark, Sepia, and PTG) using
> the picker in the top corner of every page. Thanks again for the
> suggestion — it shipped because you asked for it.

Conversation URL to confirm target before submitting: `https://newmexicoptg.org/journalgpt/index.php?c=51`.

## System-Level Feedback (fleet coordinator engine)

1. **Resumed-claim ambiguity is real and should be a first-class flow.**
   I was told explicitly not to run `./bin/fleet claim` because two prior
   Worker instances had already claimed T-PTG-014 (killed by an unrelated
   infra issue, not by any fault in the work). The task YAML's `owner`
   field still reads `Worker-AdminReply1` and the generated handoff's
   `agent` field also defaulted to `Worker-AdminReply1` (apparently derived
   from the task's current `owner`, not from my session identity). This
   worked fine here because the instructions were explicit, but a fleet
   command like `./bin/fleet resume T-XXX --owner <name>` (or at least a
   flag on `verify`/`submit` to stamp the *acting* worker identity
   separately from the task's `owner` of record) would make this
   observable in the audit trail instead of silently attributing the work
   to a dead session.
2. **`./bin/fleet verify` evidence capture is excellent** — the full
   stdout/stderr of the verification command landed in the handoff
   automatically, no manual copy-paste needed. No complaints there.
3. **No mechanism to flag a task as "blocked on a step I can't fully
   complete."** T-PTG-014 has two of three "the tool must be built AND
   used against production" halves; the fleet status vocabulary
   (`CLAIMED` → `PEER_REVIEW` → ...) doesn't distinguish "fully done" from
   "done except an explicitly-anticipated environment-access gap." I
   handled this by writing it clearly into this feedback file and leaving
   `human_action_required` untouched in the handoff (it's `null`) — it
   might be worth having Workers set that field explicitly when a
   human-only follow-up step remains, so it surfaces on the task board
   without requiring someone to read feedback files.

## Repository-Level Feedback (newmexicoptg.org / journalgpt)

1. **Access-control precedent held up well.** `admin_migrate.php`'s
   `Authorization::requireRole(null)` comment made the intended pattern
   unambiguous; I matched it exactly in `admin_reply.php` and did not
   second-guess it. Flagging again per the task's explicit ask: this
   remains a real, acknowledged tradeoff — any logged-in member can post
   into any other member's conversation via this tool. That was already
   true of the underlying capability once a "reply" tool of any kind
   exists; if it becomes a problem in practice, the fix should be creating
   a real `administrator`-role account in production (not gating this one
   tool differently from the rest of the admin surface).
2. **Test convention: `tests/CsrfRefreshTest.php` is the right model for
   endpoint-level tests**, not `tests/AskEndpointTest.php`. AskEndpointTest
   only exercises the underlying service/Csrf/Auth calls directly, not the
   actual endpoint file. CsrfRefreshTest's `runChild()` pattern (spin up a
   real PHP CLI subprocess with a seeded session file, `require` the
   target script, capture `http_response_code()` via a shutdown function)
   is what actually proves the shipped file behaves correctly end-to-end,
   and it's what I used for `AdminReplyTest.php`. Worth calling out in a
   CONTRIBUTING note so future admin-page tests default to that pattern
   instead of AskEndpointTest's lighter-weight one.
3. **One CLI-SAPI gotcha worth documenting:** `headers_list()` does not
   reliably reflect `header('Location: ...')` calls when a script is
   `require`'d from a bare `php` CLI subprocess (as opposed to running
   under `php -S`). `http_response_code()` DOES correctly reflect the
   redirect (PHP auto-sets 302 when a `Location:` header is set), so tests
   needing to assert "this unauthenticated request got redirected to
   login.php" should check `http_response_code() === 302`, not try to
   inspect `headers_list()`. I initially wrote the test against
   `headers_list()` and it silently returned an empty array in the child
   process; switching to the status-code check fixed it immediately.
4. **`journalgpt/journalptg_config/secrets.json` exists in this checkout
   but is fully templated with `REPLACE_WITH_PRODUCTION_REAL_VALUE`
   placeholders** (confirmed programmatically, not just DB_HOST — all four
   DB_* fields and OPENAI_API_KEY too, most likely). If this file is meant
   to be a real secrets drop point for local production-adjacent work, it
   is currently non-functional; if it's meant purely as a template/example,
   it might be worth a `.example` suffix or a comment header saying so, so
   future agents don't spend time investigating it as I did.
5. **Recommended next step for Chip specifically:** once `main` is
   deployed to production, visit `https://newmexicoptg.org/journalgpt/admin_reply.php`
   logged in as his member account, enter conversation ID `51`, paste in
   (or write his own version of) the message text above, and submit. That
   completes the one remaining definition_of_done item this session could
   not reach.

## Evidence

- Branch: `test-T-PTG-014`, merged into `main` via merge commit, pushed.
- Head sha of the feature commit: `03f07bf18dbe3b092cea9980ac8719fe84deb563`
- `./bin/fleet verify T-PTG-014 --model claude-sonnet-5` → passed, full
  evidence captured in `handoffs/T-PTG-014_handoff.yaml`.
- `./bin/fleet submit T-PTG-014 --model claude-sonnet-5` → task moved to
  `PEER_REVIEW`.
- Manual `/browse` QA: logged in as a seeded local test user, loaded
  `admin_reply.php`, posted a real test message into a local test
  conversation (new message id observed: `498` in the local test DB — not
  production), confirmed it appeared in the conversation transcript via
  `index.php?c=<id>`, and confirmed the non-existent-conversation-id error
  path shows a clear inline error and does not insert a row. No console
  errors observed; theme picker and layout matched `admin_migrate.php`'s
  existing visual pattern.
