## ACTION NEEDED IN PRODUCTION (read this first)

This fix has **NOT yet taken effect against production role data**. The code
gate now requires `Authorization::ROLE_ADMIN` on `admin_reply.php`, but no
`administrator`-role account exists in production today. That means **Chip
will be locked out of his own tool** (403 Forbidden) until he promotes his
own account.

Chip must run this himself against production (this Worker has no production
DB credentials reachable from this environment):

```
php journalgpt/cli/promote_admin.php <his-production-email>
```

This is idempotent — safe to re-run, and it will report "already an
administrator" on subsequent runs. It looks up the `administrator` role id
from the `roles` table by name (not hardcoded), so it stays correct even if
seed order/ids change.

---

## System-Level Feedback

- The fleet workflow (claim → branch → work → verify → merge → submit →
  feedback) worked smoothly end-to-end for a single-repo, single-agent P0 fix.
  No loopholes or friction encountered this session.
- One nit: `./bin/fleet verify` regenerated `handoffs/T-PTG-016_handoff.yaml`
  with `head_sha: REQUIRED_PLEASE_FILL` even though the commit already
  existed on the branch at verify time. It would be a small ergonomic win if
  `fleet verify` could auto-populate `head_sha` from the current branch HEAD
  when the working tree is clean, since the agent has to manually copy the
  same sha it just committed.

## Repository-Level Feedback

**What was done:** `journalgpt/admin_reply.php` was reachable by any
authenticated member (`Authorization::requireRole(null)`) and looked up the
target conversation by ID with no ownership check — a member could inject a
fake `role=assistant` message into any other member's private conversation
by simply guessing/incrementing a `conversation_id`. This was an
IDOR/impersonation vector flagged by automated security review shortly after
T-PTG-014 shipped it.

Fix applied on branch `test-T-PTG-016` (merged to `main` at
`ebf93f751dbe07c86f8e3c296bbe7c9e3c88465c`, worker commit
`73e7a36e743b541452dcf3ffedd788c31403dcd1`):

1. `journalgpt/admin_reply.php` — `Authorization::requireRole(null)` →
   `Authorization::requireRole(Authorization::ROLE_ADMIN)`. Deliberately did
   *not* switch to scoping the conversation lookup to the poster's own
   `user_id`, since the entire point of this tool is letting an admin post
   into *other* members' conversations for announcements/follow-ups.
2. `journalgpt/tests/AdminReplyTest.php` — the old "member can post" success
   test now asserts the opposite: an authenticated member gets HTTP 403. A
   new administrator-role test user is seeded (role id looked up from the
   `roles` table, not hardcoded) and a new test confirms an administrator
   can still post into a conversation it doesn't own. The CSRF and
   non-existent-conversation regression tests were switched to run as the
   admin test user too, since with the tightened gate a member session now
   gets rejected at the authorization check before ever reaching those code
   paths — running them as a member would have made those tests pass for
   the wrong reason.
3. `journalgpt/cli/promote_admin.php` (new) — idempotent CLI, takes an email
   argument, resolves the `administrator` role id from `roles.name` (never
   hardcoded), and updates `users.role_id`. Follows the existing
   `journalgpt/cli/*.php` conventions (declare(strict_types=1), try/catch
   wrapping the whole body, STDERR for errors with a non-zero exit code,
   plain stdout status lines).

**Verification:** ran the full `verification_command` locally against a real
MySQL instance (`journal_ai_test` DB) — all of `AskEndpointTest.php`,
`UsagePolicyTest.php`, `JournalAnswerServiceTest.php`, and the updated
`AdminReplyTest.php` pass (0 failures), plus `php -l` on both changed/new
PHP files. Also manually exercised `promote_admin.php` against the test DB:
promotes correctly, is idempotent on a second run, and fails cleanly with a
non-zero exit code for an unknown email or a missing argument.

**Lessons / concerns for next steps:**
- The Fleet Coordinator's own prior guidance on T-PTG-014 (copy
  `admin_migrate.php`'s `requireRole(null)` precedent) was the direct cause
  of this vulnerability. The task's scope correctly flagged this and warned
  against blindly repeating access-control precedent from one admin tool to
  another without evaluating each tool's actual blast radius — worth keeping
  in mind for any future admin-ish page in this codebase.
- `admin_migrate.php` still uses `requireRole(null)` by design (out of scope
  here, per the task). That's a real but much lower-severity residual
  exposure (any member can trigger idempotent schema migrations) — worth a
  future look once there's a real second production member account to
  reason about impact with.
- Once Chip runs `promote_admin.php` in production, it would be worth
  double-checking there isn't a second, pre-existing admin-only page in this
  codebase that assumed "no admin account exists yet" as its own
  justification for a permissive gate (the same reasoning `admin_reply.php`
  used) — that assumption is about to become false.
