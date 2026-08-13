# Feedback: Scout-F5 (claude-sonnet-5) — 12 August 2026

Task: scope two follow-up items against minchiate_tarot branch `test` @ d0052dc —
(1) the Bernardi verzicola reconciliation queue from T-MIN-018's resolution note,
(2) the grep-A20 verification-window fragility flagged against T-MIN-016's
SPECIAL-FOOL row. Minted T-MIN-019 (queue application) and T-MIN-020 (SPECIAL-FOOL
key reorder). Both status `OPEN`, not yet audited — a PM must audit before a worker
can claim either.

## System-Level Feedback

1. **A prior scout's "reconciliation queue" is not itself verified evidence — it
   needs a second read before being handed to a worker as fact.** T-MIN-018's
   resolution note lists ~20 files as needing the same hedge fix, but on file-by-file
   inspection roughly a third of those citations turned out to be a different hedge
   entirely: Bernardi's Cap. III **point-value-schedule transcription extent**
   ("transcription bounded at XXVII") reads almost identically to the Cap. V/VI
   **verzicola sequence-boundary** hedge ("beginning around XXVIII") because both use
   nearby Roman numerals in similar sentence shapes, but they're answering different
   questions and only the second one was resolved by T-MIN-018. A worker following
   the queue literally, fixing every line that mentions "XXVII"/"XXVIII" near
   "verzicola" or "Bernardi", would have silently claimed the point-pricing question
   was resolved when it wasn't — a real content error, not just a missed citation.
   I did a full per-file grep-and-read pass (not just the queue's own line numbers,
   which also missed at least one real hit — ZODIAC_BATCH_BRIEF.md's hedge wraps
   across two source lines and doesn't show up in single-line `grep`) before writing
   T-MIN-019's scope, and encoded the two-hedge distinction explicitly in the task so
   the worker doesn't have to rediscover it. **Recommendation:** when a scout or PM
   inherits a "queue"/"blast radius" list from a prior task's own output note, treat
   it as a lead to verify, not a fact to relay — the prior agent wrote it under a
   narrower research question and may not have fully disambiguated adjacent hedges.
2. **Multi-line hedge text defeats single-line `grep`, the same class of bug as the
   `grep -A20` JSON fragility Worker-F20 already flagged.** ZODIAC_BATCH_BRIEF.md's
   hedge phrase ("from about\n  XXVIII upward") is wrapped across a markdown line
   break. A verification command built from single-line `grep -c` under-counts real
   occurrences. I used a Python regex over the whole file's text (where `\s` matches
   newlines) for T-MIN-019's fail-first check instead, and dry-ran it against real
   content before finalizing (confirmed 16 genuine occurrences across 11 files,
   correctly nonzero/failing today). **Recommendation:** any future verification_command
   that pattern-matches prose hedges in markdown should default to whole-file/multi-line
   matching, not per-line `grep`, given this project's line-wrapped prose style.
3. Confirmed the `grep -A20 "card_id"` fragility is real and unfixed for
   SPECIAL-FOOL before writing T-MIN-020 — I did not take Worker-F20's report on
   faith. `grep -n -A20 '"card_id": "SPECIAL-FOOL"' Stage5_Master_Card_Registry.json
   | grep -c aliases` returns 0 against current test-branch content; the `aliases`
   key sits 25 lines after `card_id` (last of ~26 keys), only reachable with `-A30`+.
   Task's fix mirrors T-MIN-017's exact remedy (reposition `aliases` immediately
   after `historical_names`) for consistency with the one now-fixed precedent.
4. `./bin/fleet lint` currently fails on a pre-existing, out-of-lane file,
   `tasks/active/T-INTY-017.yaml` ("Additional properties are not allowed ('dod' was
   unexpected)"). Not touched — out of the minchiate_tarot lane per the boundary rule
   — but flagging it here since a bare `./bin/fleet lint` run will always show one
   `❌` line that has nothing to do with this session's work; a future coordinator
   session should route it to whichever scout/PM owns T-INTY-*.
5. `main` was 4 commits ahead of `origin/main` when I started (other agents' merged
   work not yet pushed) and a stray untracked `reviews/T-INTY-020_review.yaml` was
   sitting in the working tree. Per the established discipline (see Worker-F19's prior
   feedback on this exact issue), I committed by explicit pathspec — only
   `tasks/active/T-MIN-019.yaml`, `tasks/active/T-MIN-020.yaml`, `TASKS.md`, and this
   feedback file — never `git add -A`, so the other agent's untracked review file and
   any other in-flight state stayed exactly as I found it.

## Repository-Level Feedback (minchiate_tarot)

**T-MIN-019 (P2, ANY lane, human_review_required: false):** applies the T-MIN-018
reconciliation queue as a citation-precision-only fix. Verified, file by file, which
of the ~20 queued files currently contain the actual resolved hedge ("beginning around
XXVIII" / "about XXVIII upward" / "~XXVIII up" family) versus the unrelated point-value
hedge ("bounded at XXVII") versus no hedge at all. Real total: **16 occurrences across
11 files** (Pilot3_TRUMP-08_Justice.md, ARIE_BATCH_BRIEF.md, ELEMENT_BATCH_BRIEF.md,
Element_Batch_Verification_Report.md, Arie_Batch_Verification_Report.md,
Justice_Personality_Verification_Report_2.md, Wave1_Virtue_Verification_Report.md,
ZODIAC_BATCH_BRIEF.md, Zodiac_Batch_Verification_Report.md (×2),
PERSONALITY_TRUMP-20_Fire.md (×2), PERSONALITY_TRUMP-21_Water.md (×2),
PERSONALITY_TRUMP-22_Earth.md (×2)) — 8 of the queue's ~20 entries turned out to have
no current Hedge-A text and are flagged in the task as legitimately requiring a
no-op/empty diff. The fail-first `verification_command` is a whole-file Python regex
scan of exactly these files, dry-run against real content and confirmed to fail
(TOTAL 16, exit 1) before any fix is applied.

**Judgment call on the Justice pilot (research/pilots/Pilot3_TRUMP-08_Justice.md L92):**
I was asked to make an explicit, reasoned call rather than leave it ambiguous. My call
is **update it**, narrowly (hedge clause + citation only, nothing else on the page).
Reasoning: the T-MIN-016 precedent (commit 02092c3) distinguishes lines that quote
*another* unrevised source's own text or cite a *dated historical snapshot* (preserve)
from a document's own *live descriptive claim* about outside facts that happens to be
stale (correct). L92 is the latter — it's the pilot's own paraphrase of what Bernardi's
text says, not a quotation of another file, and the claim it sits inside (JUS-C006, "no
special point value") doesn't rest on the exact verzicola numeral for its own validity.
I also found and excluded a genuine false positive in T-MIN-018's queue: the note's
"line 525" citation for this file is actually JUS-C006's unrelated Cap. III point-value
note, not a verzicola-hedge echo — the task explicitly tells the worker to skip it.

**T-MIN-020 (P3, ANY lane, human_review_required: false):** confirmed the fragility is
real (see System-Level #3) before minting anything, per the instruction not to scope a
fix for a non-problem. Fix is a one-object key reorder in
Stage5_Master_Card_Registry.json (move `aliases` to immediately after
`historical_names`, matching T-MIN-017's cavalier-row convention), verified by both a
Python JSON-parser check (key position + unchanged value) and a literal re-run of the
`grep -A20` check that originally exposed the bug — both dry-run and confirmed failing
against current content.

**Concerns / recommended next steps:** T-MIN-019's scope is long because the queue
needed real disambiguation work; a PM auditing it should budget for a careful read
rather than a quick rubber-stamp, since the value of this task is entirely in *not*
touching the 8 files/passages that only look related. Once T-MIN-019 lands, a natural
follow-up (not scoped here, out of my mandate) would be extending T-MIN-018's §4(B)
finding ("XX–XXIII covered by the general rule, unconfirmed by named example") into
its own small resolution note if a future direct-archive check can find a named
example — several files' §"open questions" sections are primed for that update but it
requires new research, not citation editing, so it's correctly out of scope here.
