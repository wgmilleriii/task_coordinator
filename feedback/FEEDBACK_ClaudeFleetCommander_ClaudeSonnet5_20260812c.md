---
title: "T-PTG-007: Aggregate/Ranking Question Handling Fixed"
created_at: "2026-08-12T19:00:00Z"
last_modified: "2026-08-12T19:00:00Z"
author: "Claude-FleetCommander"
status: "active"
category: "00-Meta"
---

## Repository-Level Feedback (newmexicoptg.org / journalgpt)

Found via the new `reviewing-production-conversations` skill, pulling the last 10 real
conversations from `api/debug_logs.php` (now public, per Chip's request): conversation 47
asked "who writes the most articles?" -> "enuermate the top 10 most frequent
contributoprs" -> "list the names of their articles along with them" — a genuinely new
5th cognitive mode beyond T-PTG-006's four (factual retrieval / synthesis / speculative /
sentiment aggregation): **aggregate/statistical questions requiring a count or ranking
across the whole corpus**, which single-pass semantic retrieval (~20 chunks) can never
establish — it returns a similarity-ranked sample, not an exhaustive scan.

### Pre-fix behavior was inconsistent, not just occasionally wrong

Built `tests/scenarios/frequent_contributors_aggregate.json` using the exact real question
wording (typos preserved) and ran it across 3 preset/tier combos before touching any code.
Findings:
- `gpt-4o` (scholarly/medium): turn 1 correctly declined ("does not contain information
  regarding the author with the most articles"). Turn 2, the immediate follow-up asking for
  a top-10 ranking, printed a fully confident, **completely unhedged** numbered list of 10
  names with zero caveat — same model, same short conversation, opposite honesty.
- `gpt-4o-mini` (quick/quick): stated as unqualified fact that "Ed Sutton, RPT, is noted for
  having contributed over 60 articles" in answer to "who writes the most articles" — a
  single prominently-retrieved bio treated as a verified corpus-wide superlative.

This is worse than a simple refusal-vs-answer inconsistency: it's confident, specific,
false-precision content (a named individual, a specific count, a clean top-10 list) that a
member would reasonably trust as verified.

### Fix: additive system-prompt rule, not a retrieval architecture change

Considered increasing retrieval breadth or building a precomputed author-frequency index for
true aggregate queries — rejected as disproportionate for a pilot; the actual production
harm is the model's overconfident PHRASING of partial-sample results, not the sample size
itself. Added mandate 6 to `JournalAnswerService::getSystemInstruction()`: state the sampling
limitation before any name or list, describe findings as "mentioned in the retrieved
excerpts" rather than a verified ranking. Mirrored into `docs/answer-policy.md` §2.3, marked
explicitly as **pending Steering Group re-approval** rather than assumed — the doc's
"Approved by" line was left untouched; I don't have the authority to re-approve it and said
so directly in the doc.

**Verified**: re-ran the same scenario, same 3 combos, post-fix. 9/9 turns now state the
sampling limitation before any list (up from ~2/9 pre-fix), and the two worst cases
(`gpt-4o`'s unhedged top-10, `gpt-4o-mini`'s "Ed Sutton... over 60 articles") are both
directly fixed. Purely additive to the system prompt — full automated regression suite
still passes, no existing rule was loosened.
