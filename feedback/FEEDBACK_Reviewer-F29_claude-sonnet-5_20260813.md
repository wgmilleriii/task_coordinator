---
title: "Reviewer-F29 Session Feedback — T-MIN-022 (Swords Pip Batch)"
created_at: "2026-08-13T23:35:00Z"
last_modified: "2026-08-13T23:35:00Z"
author: "Reviewer-F29"
status: "active"
category: "00-Meta"
---

# Feedback: Reviewer-F29 (claude-sonnet-5), 2026-08-13

## System-Level Feedback

- **Local `main` is routinely stale relative to `origin/main`, and `bin/fleet` has
  no built-in warning for this.** My primary coordinator checkout was 3 commits
  behind and did not even contain `tasks/active/T-MIN-022.yaml` locally. The
  instructions I was given explicitly warned about this ("run `git fetch origin
  main` before any worktree-based coordinator work, do not trust a stale local
  main ref"), which is the only reason I caught it before wasting a cycle. A
  `fleet render`/`fleet start-review` that silently operates against a stale local
  `main` (rather than erroring loudly when `origin/main` has diverged) is a real
  footgun for any reviewer who wasn't handed that exact warning. Suggest `bin/fleet`
  do a cheap `git fetch --dry-run` / ahead-behind check against `origin/main` at
  startup and print a loud warning (not just onboarding docs) if the local ref is
  behind.
- **`bin/fleet` hardcodes a `.venv` path relative to its own script location**
  (`source "$DIR/../.venv/bin/activate"`), which breaks the moment `fleet.py` is
  run from a freshly created worktree (no `.venv` there). I had to manually
  `source` the primary checkout's `.venv/bin/activate` before invoking
  `python bin/fleet.py` directly inside the coordinator worktree. This is a minor
  but real friction point for exactly the isolated-worktree workflow the README
  mandates for coordinator work — every reviewer following the HARD REQUIREMENT
  literally will hit this. Either vendor a lightweight venv-bootstrap step into
  `bin/fleet`, or document the venv-borrowing workaround directly in the README's
  worktree instructions.
- The `PEER_REVIEW` → `record-review` → `DONE` flow itself worked cleanly and
  quickly once the venv issue was worked around: `start-review` generated a
  well-shaped template, `record-review` correctly flipped status to `DONE` off a
  `PASS` verdict. No complaints about the review CLI mechanics themselves.

## Repository-Level Feedback (minchiate_tarot)

Reviewed T-MIN-022 (ten Swords pip cards, Ace–Ten, authored by Worker-F24 to the
light-tier `SUIT_CARD_FORMAT_SPEC.md` format) in an isolated worktree at
`57b6066` (base `0ff3c97`). **Verdict: PASS**, task moved to `DONE`.

What I actually did, and what held up:

1. **Verification command**: re-ran the task's own `verification_command` fresh in
   the worktree — passed cleanly, exit 0, found all 10 cards plus the batch report.
2. **Rank arithmetic**: recomputed all 10 cards' rank-in-suit directly from
   `Stage5_Master_Card_Registry.csv`'s `sort_order` column myself (not trusting the
   worker's table). Every card matched exactly — Swords occupies sort_order 1–14,
   pips are 1–10, and rank-in-suit trivially equals the card's own numeric suffix.
   No arithmetic errors, no off-by-one issues.
3. **The "no long-suit trick order sourced" claim was the highest-risk part of this
   review and it held up under independent verification.** I grepped
   `Pilot3_TRUMP-08_Justice.md` and `Bernardi_1790_Verzicola_Boundary_Resolution_Note.md`
   myself rather than trusting the worker's negative finding. The Justice pilot has
   dozens of "sword" hits, but every single one is about the literal sword object
   held by the Justice trump figure (comparative iconography against Pollaiuolo,
   Mantegna Tarocchi, Ripa, etc.) — never about a Swords-suit-as-a-whole trick
   order. The Bernardi boundary note had zero hits for sword/baton/trick
   order/long suit at all. I also independently confirmed the *opposite* fact the
   worker used as a contrast: the round-suit inverse rule (Coins/Cups numerals rank
   inversely) IS genuinely sourced, in the Four of Coins full dossier, claim
   `CL-SC04-008`, explicitly scoped to "Coins and Cups" only. This confirms the
   worker's distinction (declining to import the inverse rule into Swords/Batons)
   is a real, sourced boundary and not an invented one.
4. **Scoring discipline**: grepped all 10 files for any point/value figures. The
   only number present anywhere is "five points to each King," always cited to
   RULE-1790 pp. 5–6 and always used as background context for *why* the pip has
   zero intrinsic points — never an unsourced amount attributed to a pip itself.
5. **Format compliance**: spot-checked Ace, Five, Eight, and Ten of Swords in
   full. All had the complete 8-section skeleton, landed in the 60–120 line band
   (102–105 lines), used the `SW<NN>-C<NN>` claims namespace correctly with 7 rows
   each, and used `[UNVERIFIED]` appropriately for the trick-order gap. The Ten of
   Swords explicitly names and rejects the RWS "ruin" scene (figure face-down,
   ten swords in the back) in its Confusion Resolvers/Boundaries sections as an
   excluded import, exactly as claimed — it does not describe that scene as
   Minchiate content anywhere.
6. **Batch verification report**: genuine, not a rubber stamp — contains a real
   per-card recomputation table (which matched my own independent recomputation
   exactly) and 10 individual PASS verdicts with supporting detail on the
   trick-order and scoring source-checks.
7. **Scope**: `git diff 0ff3c97..57b6066 --stat` touches exactly 11 files — the 10
   new pip drafts plus the batch report. No edits to `SUIT_CARD_FORMAT_SPEC.md`,
   the registry, any other suit's cards, or any Swords court file.

No corrections were needed; nothing was borderline enough to warrant
PASS_WITH_CORRECTIONS. This is a clean, well-disciplined batch that correctly
distinguished "nothing sourced" from "didn't look hard enough" on the trick-order
question — that distinction is the part most likely to be faked or hand-waved in
this kind of batch task, and it was the one I scrutinized hardest.

**Next steps for the human / next PM**: Batons is presumably the natural next
target (the other long suit, same trick-order-unsourced situation likely applies)
— a PM auditing that task should expect the same [UNVERIFIED] trick-order
treatment to be correct rather than a gap to fix. Coins and Cups pip batches
(T-MIN-024/025, referenced in this task's audit block) are the round-suit
counterparts and should have the inverse rule available to source, unlike
Swords/Batons.
