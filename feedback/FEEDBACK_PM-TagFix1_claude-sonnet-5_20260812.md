# Feedback: PM-TagFix1 (Scout + PM combined pass, T-PTG-009)

## System-Level Feedback

- **YAML block-scalar footgun with plain multi-line strings containing `: `.** Writing
  a `details:`/scope-item value as an unquoted multi-line plain scalar that happens
  to contain a colon-space sequence (e.g. "confirmed the exact root cause: the regex...")
  breaks the YAML parser with an unhelpful `mapping values are not allowed here` pointing
  at the wrong logical location. Cost two failed `./bin/fleet lint` round trips this
  session. Suggestion: `bin/fleet`'s task-authoring guidance (or a `fleet new-task`
  scaffold command, if one existed) could recommend single-quoting every long scope/DoD/details
  string by default, since PM/Scout prose routinely contains colons.
- **Embedding a real PHP verification one-liner as a plain YAML scalar is fragile.**
  My first draft of `verification_command` used inline PHP with `$`, `\`, nested single
  quotes, and `=>` — technically escapable in YAML but a real time sink to get right
  in a plain scalar. I switched to a literal block scalar (`|-`) and, better, decided
  the cleanest fix was to have the audited scope require the Worker to create a dedicated
  `FeatureRequestServiceTest.php` file and reference just its path in `verification_command`,
  keeping the YAML itself simple. Recommend documenting "prefer a `|-` block scalar,
  or better, point at a test file path rather than inlining a one-off script" as house
  style for `verification_command`.
- **Unrelated pre-existing lint failure (`T-INTY-017.yaml`, `dod` unexpected property)**
  blocks a full store-wide `./bin/fleet lint` from ever reporting all-green right now.
  It predates this session and is outside `newmexicoptg.org`'s lane — flagging so a
  human or the INTY lane's next PM fixes it (schema evidently wants `definition_of_done`,
  not `dod`), since a chronically-red `lint` output trains agents to skim past it instead
  of investigating.

## Repository-Level Feedback (newmexicoptg.org / JournalGPT)

**What happened:** Chip reported, mid-session, live production evidence that T-PTG-008's
just-shipped feature-request router (`FeatureRequestService::isTagged()`) failed on
its very first real user attempt: a member typed `/featurerequest different color
schemes` (no space) and got routed into the RAG pipeline instead of the triage lane,
producing a nonsensical "corpus does not contain information about color schemes"
answer. I read `journalgpt/api/ask.php` and `journalgpt/lib/FeatureRequestService.php`
directly to confirm root cause before writing anything: `isTagged()`'s regex is
`'/^\/feature[- ]request(?=[\s]|$)/i'` — the character class `[- ]` requires *exactly
one* separator character (a space or a hyphen) between "feature" and "request", with
no zero-width alternative, so a concatenated `/featurerequest` can never match. The
identical gap exists in `stripTag()`, though it's currently unreachable in practice
since `isTagged()` gates the call. Leading-whitespace tolerance already works correctly
today (`ltrim()` before the anchored regex) — I called that out explicitly in scope
so the Worker doesn't "fix" something already working.

I also confirmed there is zero existing test coverage of tag-matching: grepped
`AskEndpointTest.php` for `isTagged`/`stripTag`/`FeatureRequestService` (zero hits —
it only tests anonymous access, CSRF, and basic JSON shape) and confirmed no
`FeatureRequestServiceTest.php` or equivalent exists anywhere under `journalgpt/tests/`.
This matches T-PTG-008's own PM audit notes: the happy-path multi-turn conversation
was proven against a running server, but tag-matching edge cases were never asserted.

**Task written:** `T-PTG-009`, `priority: P1` (actively misrouting real user intent
in production), scoped tightly to a mechanical regex fix (`[- ]` → `[- ]?` in both
`isTagged()` and `stripTag()`) plus a new `FeatureRequestServiceTest.php`. Explicitly
excluded fuzzy/typo matching and anywhere-in-body detection per Chip's direction, and
made the T-PTG-008 false-positive-avoidance case (a technical question mentioning
"feature request" mid-sentence must stay in RAG) an explicit required regression test
in the DoD, not just prose.

**Why I audited it myself in the same pass (Scout+PM combined), mirroring how
`T-INTY-021`/caut_sfusd was handled earlier:** this is a single-file, single-regex,
mechanical fix with a fully understood root cause (confirmed by reading the exact
line, not inferred), a pre-existing test harness and DB-backed verification convention
already proven working by T-PTG-008's own PM audit, and a scope tight enough that I
could write concrete before/after test assertions myself. There's no schema change,
no new architecture, no ambiguous product decision left open (Chip already specified
the exact variant set and explicitly ruled out the two things that would have made
this risky). Audited against repo SHA `04842d7e9120bd559464f6cc1586e8c52c72c5f1` with
`./bin/fleet audit T-PTG-009 --auditor PM-TagFix1 --repo-sha 04842d7e9120bd559464f6cc1586e8c52c72c5f1 --command "..."`.
Set `human_review_required: false` since the fix is mechanical and the DoD is fully
machine-verifiable (test assertions, not subjective visual/product judgment).

**Recommended next step for a Worker:** claim `T-PTG-009`, change `[- ]` to `[- ]?`
in both methods, write `journalgpt/tests/FeatureRequestServiceTest.php` covering the
six cases enumerated in the task's scope/DoD (space, no-space, hyphen, mixed-case,
leading-double-space, and the mid-sentence false-positive case), and confirm the full
existing suite (`AskEndpointTest`, `UsagePolicyTest`, `JournalAnswerServiceTest`)
still passes via the `DB_HOST=127.0.0.1` pattern before submitting.
