# Feedback — Scout-F2 (claude-fable-5), 2026-08-11

Role: Scout, minchiate_tarot lane. Assignment: mint three OPEN tasks converting the
11 Aug triage output (arie brief, Papi/Fool brief, venture-plan suit-card dependency)
into board work. Minted T-MIN-011, T-MIN-012, T-MIN-013.

## System-Level Feedback

- `./bin/fleet lint` passed with zero warnings this session, including the archived
  T-INTY yamls. The pre-briefed expectation that lint might fail on other repos'
  broken yamls did not materialize — either they were fixed or archive files are not
  linted. If the latter, that is a small loophole: a broken task could be "fixed" by
  archiving it.
- There is no `./bin/fleet create` or scaffold command for Scouts; task authoring is
  raw YAML against schemas/task.schema.json. It works, but a `fleet new T-MIN-011`
  stub generator would remove the most likely Scout failure mode (schema drift in
  hand-written YAML, wrong timestamp format).
- Id allocation is convention-only: nothing stops two concurrent Scouts minting the
  same next id. A `fleet next-id MIN` helper (or lint rejecting duplicate ids across
  active+archive) would close that race. I checked tasks/archive/ manually to avoid
  reusing T-MIN-004/005/010.
- The onboarding janitor line reports "496239.8 hours since the last doc update" —
  clearly an epoch-default artifact. Cosmetic, but it undermines trust in the janitor
  gate's arithmetic.
- Board render is good. One gap: OPEN tasks appear without their verification_command,
  so a PM must open the yaml to see the Scout's suggestion. Rendering it (marked
  "suggested, pre-audit") would speed PM triage.

## Repository-Level Feedback

How the tasks were scoped: I did not paraphrase the triage output from memory. I read
both replacement briefs (ARIE_BATCH_BRIEF.md, PAPI_FOOL_BATCH_BRIEF.md) in full on
branch test @ f8bb1b8, plus the venture brief's §2.7 tier decision, and lifted the
binding traps into the task scopes with their citation anchors (JUS-C005/C006,
DEA-C004, CW-5, CW-10, QC row ranges) so a Worker who reads only the yaml still hits
the load-bearing constraints before opening the brief. The scopes deliberately repeat
the briefs' three fabrication classes from the failed fleet run — invented amounts,
invented titles, structurally smuggled withdrawn readings — because the triage showed
those survive a "no X" instruction unless the ban names the specific enactment.

Lessons learned: the archived failed drafts are a hazard precisely because they are
fluent; both new authoring tasks therefore require a diff-against-archive step in
their DoD, matching the Justice-clone precedent. The zodiac batch's per-wave
adversarial verification is the one pattern that has survived independent
verification, so both P1 tasks mandate it rather than a single end-of-batch pass.

Concerns / next steps for the human: (1) T-MIN-013 is the venture plan's critical
path — until the light-tier format is decided, "research complete" has no reachable
definition for 56 of 97 cards; I set human_review_required: true because the tier
trade-off (what honesty apparatus the cheap format drops) is a product decision, not
a research one. (2) The two authoring batches cross-reference each other
(offered-not-imposed edges); if the PM audits only one, the Worker should be told the
sibling batch is unlaunched so edges stay offered. (3) T-MIN-008 (verzicola boundary)
is still OPEN and would retire a hedge both new batches must otherwise carry —
auditing it before or alongside T-MIN-011/012 would let the arie batch cite a
transcription instead of the pilot L92 hedge.
