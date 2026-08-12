---
title: "T-PTG-005 Voicing-Technique Continuity + Citation-Format Test Matrix Results"
created_at: "2026-08-12T15:35:00Z"
last_modified: "2026-08-12T15:35:00Z"
author: "Claude-FleetCommander"
status: "active"
category: "00-Meta"
---

## System-Level Feedback

None this session — the fleet lifecycle (claim/verify/submit) worked smoothly for a
test-execution task, not just a code-change task.

## Repository-Level Feedback (newmexicoptg.org / journalgpt)

Ran the two-turn conversation ("Have voicing technique changed over the years? Are there
different viewpoints of what should be done? Do any contradict another?" then, as a
follow-up in the same conversation, "Who talks about this first?") against all 6
preset x tier combinations the UI exposes, via `tests/manual_voicing_continuity_matrix.php`
(new, not part of the automated suite — makes real OpenAI API calls).

### Result table

| Preset | Tier | Model | Turn 1 | Turn 2 | Citations | Continuity |
|---|---|---|---|---|---|---|
| quick | quick | gpt-4o-mini | grounded, 7 citations | grounded, 6 citations | clean | resolved "this" correctly |
| quick | medium | gpt-4o | grounded, 5 citations | grounded, 3 citations | clean | resolved correctly |
| quick | deep | o3-mini | **not grounded, 0 chunks** | **not grounded, 0 chunks** | n/a | n/a |
| scholarly | quick | gpt-4o-mini | grounded, 6 citations | grounded, 7 citations | clean | resolved correctly |
| scholarly | medium | gpt-4o | grounded, 14 citations | grounded, 4 citations | clean | resolved correctly |
| scholarly | deep | o3-mini | **not grounded, 0 chunks** | **crashed: OpenAI transient server_error** | n/a | n/a |

### Finding 1 (the headline result): Deep tier is fundamentally broken, not (only) a timing issue

Chip reported "deep (maximum focus) appears to be not working" in an earlier session; I
fixed a real bug (the run-status poll loop capped at 30s while the script budgets 120s) and
pushed it, but this matrix proves that fix does NOT make Deep tier actually work end to end.

Querying `debug_logs.raw_answer` for the o3-mini runs shows the model narrating its
*intent* to search rather than ever executing the `file_search` tool call and returning a
grounded answer:

> "Let me search the Journal excerpts for this topic. One moment while I retrieve information."

> "I'll now search the provided Journal excerpts for information on voicing technique
> changes, differing viewpoints, and potential contradictions. Please hold on as I look
> that up."

> "To answer your questions, let's search for references to voicing technique evolution
> and any differing or contradictory viewpoints in the Journal excerpts. I'll now search
> within the uploaded files for relevant content."

The run then completes right there — `retrieved_chunks_count = 0` every time, so
`resolveCitationsFromChunks()`/the Tier-4 fallback have nothing to work with, and PTJ-013's
"Always-Attach Citation Policy" correctly withholds the answer rather than fabricating a
citation. This is the RIGHT behavior given zero grounding — the bug is upstream, in why
o3-mini isn't actually calling file_search before finalizing.

This was consistent across all 3 real o3-mini completions captured (2 in this matrix, 1
from an earlier smoke test) — not occasional flakiness. My working hypothesis: reasoning
models (o1/o3 series) may handle tool-calling differently in the Assistants v2 API than
gpt-4o-class models — possibly requiring a separate `requires_action` step to actually
surface/execute the tool call rather than the "auto" flow gpt-4o-mini/gpt-4o use, or the
`instructions` framing (written for a standard chat model) may cause a reasoning model to
treat "search" as narration rather than an action. I have NOT attempted a fix — this needs
research into whether the Assistants API genuinely supports file_search well for reasoning
models at all, or whether the fix is switching Deep tier to OpenAI's newer Responses API
(which has different/evolving reasoning-model + retrieval support), before writing code.

**Recommendation:** either drop "Deep (Maximum Focus)" from the tier selector until this is
properly fixed (it currently silently fails 100% of the time and returns a refusal, which
is misleading — the user did nothing wrong, the tier itself doesn't work), or file this as
its own P0/P1 task once a fix approach is decided.

### Finding 2: a transient OpenAI-side outage during scholarly/deep turn 2

`server_error: Sorry, something went wrong.` — this is OpenAI's own infrastructure having a
momentary issue, not a bug in this codebase. Confirmed api/ask.php already catches this
class of exception gracefully in production (returns a generic 500 to the user); it only
crashed my test harness because that harness doesn't wrap the `ask()` calls in try/catch
(intentional — a real crash there is useful signal, not something to swallow).

### Finding 3 (the good news): the other 4/6 combinations work correctly

Quick and Medium tiers, both presets, all passed cleanly:
- Every citation has a real `article_id`, valid `page`/`printed_page`, a well-formed
  `source.php?article_id=X&page=Y` URL, and no leaked `【…】` annotation markers.
- Page-range collapsing (T-PTG-002) worked correctly in the wild, not just in synthetic
  unit tests — e.g. "pp. 12-14" instead of three separate citations.
- Turn 2 ("Who talks about this first?") correctly resolved "this" against turn 1's
  voicing-technique discussion in every successful combination, naming specific authors
  (Stephen Brady, André Oorebeek, etc.) — **conversation continuity is NOT broken** for the
  tiers that actually complete. This directly answers Chip's earlier "why is there no
  continuity" question: the wiring (conversation_id threading, ConversationContext's last-6-
  message replay) is sound; what he was likely hitting was specifically the Deep tier's
  retrieval failure being misread as "it forgot the conversation," when actually it never
  grounded turn 1 in the first place.
