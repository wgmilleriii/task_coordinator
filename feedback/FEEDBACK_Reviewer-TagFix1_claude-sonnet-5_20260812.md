---
title: "Peer Review: T-PTG-009 (feature-request tag separator fix)"
created_at: "2026-08-12T22:00:00Z"
author: "Reviewer-TagFix1"
status: "active"
category: "00-Meta"
---

# System-Level Feedback

- `./bin/fleet verify` resolves the verification_command against a hardcoded/default
  checkout path for the repo rather than the worktree registered for the task's
  branch. This is the second time this session (also on T-PTG-008) a Worker had to
  manually explain a spurious verify failure caused by running the command in the
  wrong tree. Recommend `verify`/`submit` take or infer the worktree path from the
  task's active claim, or at minimum print which directory it ran in so the
  Worker/Reviewer doesn't have to reverse-engineer it from the error text.
- `record-review` schema rejects `LOW` as a finding severity (only INFO/MINOR/MAJOR/CRITICAL
  are valid) — not documented anywhere I found before hitting the error. Minor, but
  the schema should be surfaced to reviewers before they draft findings, not after.
- Otherwise the review flow (start-review → edit YAML → record-review) was smooth
  and the schema validation caught my mistake immediately with a clear message.

# Repository-Level Feedback (newmexicoptg.org, T-PTG-009)

Verdict: **PASS**, task now **DONE** (human_review_required was false, so no
human-sign-off stage follows).

Verified independently, not by trusting the handoff:
- Full diff at head_sha (05c03c9) is exactly the two claimed one-line regex changes
  (`[- ]` → `[- ]?`) in `isTagged()`/`stripTag()` plus the new 145-line test file —
  nothing else touched.
- Read the new `FeatureRequestServiceTest.php` in full; assertions are real (call
  the actual static methods, throw on mismatch), not tautological.
- Reproduced the TDD claim myself: isolated the pre-fix version of just
  `FeatureRequestService.php` via `git checkout <parent-sha> -- <file>`, reran the
  test file, got the exact claimed failure (`REGRESSION NOT FIXED`, exit 1).
  Restored the fix, reran, exit 0. Worktree left clean.
- Ran all four suites myself with real output: `FeatureRequestServiceTest.php`
  6/6 OK, `AskEndpointTest.php` 3/3 OK, `UsagePolicyTest.php` 5/5 OK,
  `JournalAnswerServiceTest.php` all sub-tests OK. No regressions.
- Independently reproduced both the fix and the false-positive guard with a
  standalone script calling `FeatureRequestService` directly (not just the
  Worker's own test file): no-space variant now tags true and strips cleanly to
  `'different color schemes'`; a genuine mid-sentence "feature request" mention
  still tags false.
- Battery-tested the regex change for new false-positive surface
  (`/featureXrequest`, `/feature_request`, double-space, no-boundary-after-request)
  — all behave correctly; `?` only makes the existing separator class optional,
  no new match surface introduced.
- Confirmed the `ask.php` call site shape is unchanged (single boolean static
  call at line 113) and `stripTag()` is still invoked internally by `ask()`.

One thing I did not re-verify: the Worker's claimed full mock-OpenAI-server + DB
row insert end-to-end run. I judged the unit-level reproduction plus the three
passing DB-backed suites as sufficient independent evidence — this is a two-line
regex change with unambiguous unit coverage, so the full server path wasn't
load-bearing for the verdict. Noted as a MINOR finding in the review record, not
a blocker.

Lesson for future reviewers on this repo: the `[- ]?` optional-separator pattern
is small enough to fully characterize by hand (I ran ~9 adjacent strings through
it directly) — worth doing rather than trusting "the diff is minimal" on faith,
since regex changes are exactly the kind of thing that look safe and aren't.
