# Session Feedback: ChatGPT / GPT-5.6 Sol

## System-Level Feedback

- The task coordinator rules were clear about treating `TASKS.md` as generated/read-only and creating isolated YAML task records under `tasks/active/`.
- The explicit `newmexicoptg.org` test-branch-only policy in the README is valuable and was carried into the new task scope to prevent accidental production deployment.
- The coordinator schema allows `verification_command: null` for OPEN tasks, which is appropriate here because a PM still needs to audit the exact implementation baseline and choose the final test command before the task becomes executable.
- A future improvement would be a connector-friendly task creation command/API that validates a proposed YAML task against `schemas/task.schema.json` without requiring a local checkout of `bin/fleet`.

## Repository-Level Feedback

- Added task `T-PTG-066` for `newmexicoptg.org` to capture the owner's revised JournalGPT public-launch requirements.
- The task defines a public "Continue as Guest" path with exactly three successful interactions before verified email registration is required.
- Guest identity is specified as an opaque secure cookie plus server-authoritative usage records; IP/network data is only a secondary abuse signal.
- The owner's GPS/location request is scoped to consent-based browser geolocation. The task explicitly forbids bypassing browser permission and requires graceful behavior when permission is denied.
- Email continuation is defined as a real verification flow: expiring single-use token, sent email, and confirmation-link click required before further JournalGPT access.
- Public source rights remain citation-image-only: up to 10 guest citation images tracked independently from the three-interaction allowance, with complete PDFs and backing storage identifiers forbidden.
- The task requires updating the previously written JournalGPT public-access whitepaper because its earlier 10-question anonymous-trial language has been superseded by the three-interaction verified-email model.
- Recommended next step: a PTG PM should audit `T-PTG-066` against the current `newmexicoptg.org` `test` SHA, inspect current mail-delivery facilities and source-image generation routes, set a concrete verification command, then transition the task from OPEN to AUDITED.
