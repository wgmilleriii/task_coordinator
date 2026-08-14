---
title: "FEEDBACK Reviewer-F32 claude-sonnet-5 20260813"
created_at: "2026-08-14T00:20:00Z"
last_modified: "2026-08-14T00:20:00Z"
author: "Reviewer-F32"
status: "active"
category: "00-Meta"
---

# Feedback: Reviewer-F32 (claude-sonnet-5) — T-MIN-025 review, 2026-08-13

## System-Level Feedback (task_coordinator itself)

1. **No `.venv` in worktrees breaks `bin/fleet` out of the box.** `bin/fleet` hard-codes
   `source "$DIR/../.venv/bin/activate"`, which only exists in the primary checkout.
   Every reviewer/worker that follows the "isolated worktree" HARD REQUIREMENT for
   coordinator-side work (not just spoke-repo work) hits `python: command not found`
   on first invocation and has to manually `source
   /path/to/task_coordinator/.venv/bin/activate` before calling `python bin/fleet.py`
   directly, bypassing the wrapper script. This is a small, repeated papercut across
   the fleet — worth either vendoring a `requirements.txt`-driven venv bootstrap into
   `bin/fleet` itself (auto-create if missing) or documenting the manual-activate
   workaround in the README's worktree section so agents aren't rediscovering it
   each session.
2. **Plain YAML scalars silently reject `: ` mid-string**, which is easy to trip on
   when a finding description quotes a source claim verbatim (e.g. a citation reading
   `"...ranks Coins and Cups numerals: ..."` or a table cell described as `"specimen
   gaps: card absent..."`). `record-review` doesn't give a helpful error — it surfaces
   a raw PyYAML traceback (`mapping values are not allowed here`) with a line/column
   that doesn't map cleanly back to which finding is at fault when the file has many
   long findings. Consider having `bin/fleet` catch `yaml.YAMLError` around review-file
   loading and print just the offending file + line, or having `start-review`'s
   generated template include a one-line comment reminding reviewers that colons need
   quoting/rephrasing in plain scalars.
3. **This task_coordinator repo's PRIMARY checkout was dirty on `test-engine-fixes`**
   with substantial uncommitted work (bin/fleet.py, README.md, AGENTS.md, multiple
   T-PTG task/handoff/review files) at the time of this review, and `T-MIN-025.yaml`
   did not exist in that checkout at all — only on `origin/main`. The boundary
   instructions anticipated this correctly ("run `git fetch origin main` before any
   worktree-based coordinator work... do NOT touch it"), and a detached worktree from
   `origin/main` was the right call. Flagging this as confirmation the instruction is
   necessary in practice, not hypothetical — an agent that skipped the fetch-and-
   isolate step and worked directly in the primary checkout would have either failed
   to find the task at all or, worse, committed review artifacts on top of another
   agent's in-flight `test-engine-fixes` work.

## Repository-Level Feedback (minchiate_tarot)

**Task reviewed:** T-MIN-025 — the fourth and final Coins pip-card batch (nine cards:
Ace, Two, Three, Five, Six, Seven, Eight, Nine, Ten of Coins; Four of Coins was
already the format's pilot card and out of scope). Author: Worker-F27, branch
test-T-MIN-025, head c1fdd61fe45f95441216bec192e67be0dde07f5e.

**Verdict: PASS** (no corrections required, all 9 findings INFO-severity).

### How the review was done

Worked in a detached worktree off c1fdd61 without touching the primary
minchiate_tarot checkout (which stayed clean on `test`). Re-ran the audited
`verification_command` fresh — passed, "OK, found 9 cards". Recomputed every
card's rank-in-suit from `Stage5_Master_Card_Registry.csv` (Coins pip block
sort_order 43–52) by hand rather than trusting the batch report's table, and it
matched exactly, including the Ace-strongest/Ten-weakest inverse asymmetry the
round-suit trick-order rule implies.

The centerpiece of this review was independently opening
`Pilot1_SUIT-COINS-04_Four_of_Coins.md` myself and reading claims `CL-SC04-008`
and `CL-SC04-009` at their source, specifically because the sibling Cups review
(T-MIN-024, Reviewer-F31) had just caught a real over-attribution one task earlier
— a claim ID (`C-CUPS12-002`) registered for a narrower fact than the batch cited
it for. I held Coins to the identical scrutiny rather than assuming "same pattern,
already passed once, must be fine." It genuinely is fine here, and for a
structurally different reason than I initially expected: `CL-SC04-008/-009` live in
the Four of Coins pilot itself, which *is* Coins' own origin dossier — there's no
cross-document reach at all, unlike the Cups case which pulled a claim ID from a
different pilot (the Cavalier of Cups court study). The rule happens to name both
Coins and Cups jointly, which is why both suits can legitimately cite it, but
Coins isn't borrowing anyone else's evidence to do so.

Also independently re-verified the self-reported stray-ID-token bug fix (grepped
all 9 files for the `SUIT-COINS-\d{2}` pattern and for the literal string
`SUIT-COINS-04`; confirmed exactly one token per file and zero leaked references),
confirmed the Five of Coins specimen-gap note against the registry, and did a
targeted cross-suit consistency pass (claims-table ID format, section-3 scoring
wording, section-7 boundaries wording) across one card each from Swords, Batons,
Cups, and Coins since this review closes out the whole 4-batch pip effort. All four
batches use the identical spec-mandated claim-namespace format
(`<SUIT2><RANK2>-C<NN>`) and near-verbatim section wording — this reads as one
disciplined execution of the format spec across four independently-authored
batches, not four drifting interpretations.

### Four-batch pip-card rollup (Swords T-MIN-022, Batons T-MIN-023, Cups T-MIN-024,
Coins T-MIN-025 — all 40 pip cards now complete)

| Batch  | Cards authored | Reviewer     | Verdict              | Findings (severity) |
|--------|-----------------|--------------|-----------------------|----------------------|
| Swords | 10              | Reviewer-F29 | PASS                  | 7 (7 INFO)           |
| Batons | 10              | Reviewer-F30 | PASS                  | 7 (7 INFO)           |
| Cups   | 10              | Reviewer-F31 | PASS_WITH_CORRECTIONS | 9 (8 INFO, 1 MAJOR)  |
| Coins  | 9 (+1 pre-existing pilot) | Reviewer-F32 (this review) | PASS | 9 (9 INFO) |
| **Total** | **39 new + 1 pre-existing pilot = 40 pip cards** | — | 3 PASS / 1 PASS_WITH_CORRECTIONS | **32 findings, 1 MAJOR, 0 FAIL/CRITICAL** |

The single MAJOR across all four batches (Cups, C-CUPS12-002) was a claim-ID
precision issue, not a fabrication — the substantive numeral-run claim it
supported was independently confirmed true and sourced elsewhere in the same
document; it was flagged as a correction for a future citation-hygiene pass, not a
blocker, and did not stop that batch from landing.

**Pattern worth a follow-up task:** across all four batches, the round-suit
(Coins/Cups) trick-order rule traces cleanly to `CL-SC04-008/-009` in the Four of
Coins pilot, but the *specific atomic claim ID* each batch cites for it varies in
rigor — Coins and Batons/Swords cite `CL-SC04-008/-009` directly (correct, since
that's the only place the rule is registered), while Cups' pre-existing Cavalier
pilot has a same-topic sentence sitting outside any atomic claim ID of its own
(`C-CUPS12-002` only covers the court ordering). A small cleanup task — giving the
Cavalier of Cups pilot's numeral-run sentence (line 111) its own claim ID rather
than leaning on the adjacent `C-CUPS12-002` — would close out that one open
precision gap and give the whole suit-card claim registry a fully clean audit
trail. Low priority (it's cosmetic, not a factual error), but worth queuing for
whoever does the next citation-hygiene pass over research/pilots/.

**Concern/next-steps note for Chip:** all 40 pip cards are now DONE across four
independently-run batches with a consistent format, consistent discipline
(sourced-or-absent scoring, witness-bounded trick-order claims, forbidden-term
exclusions), and only one non-blocking precision finding total. The suit-card pip
tier looks ready to treat as a closed, stable layer — the next natural step is
likely either the remaining court-card work outside the already-closed T-MIN-013/
T-MIN-021 middle tier, or moving attention to the IMG-001 blocker that every single
one of these 40 cards' header blocks flags (no verified card-level crop exists for
any card in any specimen) — that blocker is now the single most repeated
open item across the entire suit-card corpus.
