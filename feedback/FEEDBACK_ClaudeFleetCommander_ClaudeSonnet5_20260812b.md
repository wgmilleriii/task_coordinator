---
title: "T-PTG-006 Golden Hammer Deep Dive: Conversational Quality Test Results"
created_at: "2026-08-12T18:15:00Z"
last_modified: "2026-08-12T18:15:00Z"
author: "Claude-FleetCommander"
status: "active"
category: "00-Meta"
---

## Repository-Level Feedback (newmexicoptg.org / journalgpt)

Built a generalized scenario-driven test harness (`tests/manual_conversation_matrix.php` +
`tests/scenarios/golden_hammer_deep_dive.json`) and ran Chip's 4-turn scenario — deliberately
mixing four different cognitive modes in one conversation:

1. **Factual retrieval**: "Who won the Golden Hammer award over the last five years?"
2. **Synthesis**: "Tell me about their biographies. Do they have anything in common?"
3. **Speculative**: "Imagine that you were in a room with all of them. What do you think
   they would talk about?"
4. **Sentiment aggregation**: "What are some of the concerns for this organization that
   have been voiced in the last five years?"

### The finding: turn 3 was being silently discarded, not refused by the model

Across all 3 tiers tested (Quick/gpt-4o-mini, Medium/gpt-4o, Deep/o3-mini), the SAME
pattern appeared before any fix: **every single model actually wrote a good, properly
hedged, appropriately speculative answer to turn 3** — e.g. gpt-4o: *"While the retrieved
documents do not detail specific conversations... based on their backgrounds... Del
Fandrich would likely discuss his patented soundboard design... Richard Davenport might
open up about overcoming his stroke..."* — but because pure speculation legitimately has
zero citations to attach, PTJ-013's "Always-Attach Citation Policy" (the safety net added
to prevent uncited assertions of fact) discarded every one of these good answers and
replaced them with the generic uncertainty phrase. Confirmed via `debug_logs.raw_answer`
that the discarded content was there the whole time — this wasn't a model refusal, it was
our own architecture throwing away a good answer.

### The fix (already committed, `e81d2887f8a63c9195752325c8576e3e3b4094c2`)

Rather than touching `docs/answer-policy.md`'s "zero-hallucination... legal compliance"
grounding policy (a formally approved document — see the tension noted below), the fix is
architectural: force `tool_choice: {"type": "file_search"}` on every turn, for every model,
not just the reasoning models the earlier T-PTG-005 fix targeted. This means the model
always has fresh corpus material in front of it to legitimately cite even when answering a
synthesis/speculative question, so a good hedge-and-cite answer survives the citation
check instead of purely reasoning from nothing and getting discarded.

**Verified**: with the fix, all 3 tiers produced `grounded=true` answers with real
citations (3-6 per turn) for the speculative turn, each one clearly framed as inference
("this remains an informed inference rather than a documented account" — o3-mini) rather
than asserted fact. Turns 1, 2, and 4 remained correctly grounded and well-cited
throughout (no regression), with zero leaked citation markers.

### A tension worth the human's attention, not something I resolved unilaterally

Del Fandrich and Richard Davenport (and Isaac Sadigursky, in some runs) are real, named
PTG members. Having the AI speculate about what they'd personally discuss — even
clearly hedged as imagination — carries a different kind of risk (reputational/
attribution) than refusing a technical question, and `answer-policy.md`'s framing
explicitly ties the strict-grounding mandate to legal compliance. I did not judge this
tradeoff myself; I fixed the architectural bug (a good answer being thrown away) without
touching the underlying policy language, and flagged the tension to Chip directly in
conversation. If the organization wants the assistant to *never* speculate about named
individuals regardless of hedging quality, that would need a policy change, not a code fix
— worth a human decision, not mine to make.

### Minor, non-blocking observation

`gpt-4o-mini` occasionally retrieves relevant chunks (confirmed 20 chunks in one case) but
doesn't emit citation markers for its response, even though the facts stated matched a
properly-cited `gpt-4o` answer to the identical question. The system correctly treats this
as ungrounded (no citations to verify against) rather than trusting unattributed content —
this is the safety net working as intended, not a bug to chase. Noting it as expected model
response variance, not a regression from this session's changes.
