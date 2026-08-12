# Feedback: Worker-TagFix1, claude-sonnet-5, 2026-08-12

Task: T-PTG-009 (newmexicoptg.org). This session was a **resume after a stall**:
the prior session on this exact task died from an infrastructure issue (not a
task-logic problem) before writing any code -- it had only just started reading
`FeatureRequestService.php`. I inherited zero code from that stall (unlike an
earlier T-PTG-008 resume this same session, which did inherit partial work).
Picked up the CLAIMED task under the same owner identity (`Worker-TagFix1`) and
worked in the pre-existing isolated worktree at
`/Users/willismiller/Documents/GitHub/newmexicoptg.org-t009` (branch
`test-T-PTG-009`), which was clean.

## System-Level Feedback

- **`./bin/fleet verify` resolves the wrong checkout when a worktree exists.**
  It ran the verification_command against
  `/Users/willismiller/Documents/GitHub/newmexicoptg.org` (the primary/default
  clone registered for `repo: newmexicoptg.org`), not the isolated worktree at
  `newmexicoptg.org-t009` where this task's branch and commit actually live.
  The primary checkout's working tree has neither the fix nor the new
  `FeatureRequestServiceTest.php`, so `verify` failed with "Could not open
  input file" -- a checkout-selection bug, not evidence against the fix. This
  is the second time this session a Worker hit this exact gap (also noted in
  `FEEDBACK_Worker-DBFallback1...` for T-INTY-021). It's now a repeated,
  predictable failure mode across at least two repos/tasks. Recommend `fleet
  verify` either (a) accept an explicit `--cwd`/`--worktree` flag, or (b) look
  up the task's claimed `branch` against `git worktree list` in the target
  repo and cd into a matching worktree automatically before running
  verification_command.
- The hand-build-the-handoff fallback path documented in the task prompt (and
  referenced against `T-INTY-021_handoff.yaml` as a working example) worked
  smoothly once I had real terminal evidence to paste in. Validating the YAML
  against `schemas/handoff.schema.json` by hand (no `jsonschema` package
  installed locally, so I checked required/additionalProperties/pattern
  fields directly in Python) caught nothing wrong, and `fleet submit`
  accepted it cleanly on the first try.

## Repository-Level Feedback

Root cause was exactly as scoped by the PM audit: `FeatureRequestService.php`
had `[- ]` (mandatory-one-of hyphen-or-space) in both `isTagged()` and
`stripTag()`, so `/featurerequest` (no separator) never matched and fell
through to the RAG pipeline. Fix was the minimal one specified: `[- ]` ->
`[- ]?` in both methods, nothing else touched.

Followed this repo's TDD convention literally: wrote
`journalgpt/tests/FeatureRequestServiceTest.php` first, confirmed via `git
stash`/`stash pop` that it fails against the pre-fix tree (`isTagged()`
returns false for the no-space case) and passes after the fix. The test file
has no DB dependency since `isTagged`/`stripTag` are pure static string
functions -- kept it that way rather than pulling in the heavier DB-setup
pattern from `AskEndpointTest.php`.

Went one step further than a pure unit test for the "reproduce against a
running server" DoD step: rather than only checking `isTagged()` in
isolation, I ran `FeatureRequestService::ask()` end-to-end against a real
`journal_ai_test` MySQL DB with the exact production string from
`debug_logs.php?id=22`, and confirmed via direct SQL query that
`feature_request_details.idea_summary` came out as `'different color
schemes'` -- no leftover tag fragment, no reliance on the DB test-fixture
convention where a fake OpenAI mock could paper over a stripTag() bug.

All three named regression suites (`AskEndpointTest`, `UsagePolicyTest`,
`JournalAnswerServiceTest`) plus the new `FeatureRequestServiceTest` pass
clean (exit 0) run together as the task's literal `verification_command`,
executed by hand in the correct worktree.

**Lessons / next steps for the human:** this is the second sibling task
(T-PTG-008, T-PTG-009) in one day where a shipped feature had a real
production incident within the hour because the DoD for the original task
didn't include tag-matching edge-case tests -- only a happy-path server
walkthrough. If more tag/router-style features are planned for JournalGPT, a
PM auditing a new one should proactively require a small matrix test (all
separator variants x case x false-positive) as part of the *original* task's
DoD, not as a follow-up bug fix after a member hits it. Also worth a fleet-
level nudge: worktree-resolution in `fleet verify` should be fixed before the
next multi-task day, since it is now costing every Worker a manual
hand-build-the-handoff detour.
