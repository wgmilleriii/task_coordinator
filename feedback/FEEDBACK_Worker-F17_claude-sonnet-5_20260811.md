# Feedback — Worker-F17 (claude-sonnet-5), T-MIN-003

Executed T-MIN-003 ("Apply the 93 pending card renames already recorded in
ledger.json") through claim → branch → implement → dry-run → real-run →
verify. Verification failed for a legitimate, discovered data reason (not a
script bug), so the task was `fleet block`-ed rather than force-submitted.
Head sha of the committed work: `ad18b35ca2bac83a60b169f76b3e69fc93343a6d`
on `minchiate_tarot` branch `test-T-MIN-003` (pushed to origin).

## System-Level Feedback

1. **Confirms Worker-F14's base-branch finding on T-MIN-002, same root
   cause, third occurrence.** T-MIN-003 was audited against
   `0509f6914e201ba192717c7a90c3c4154e5120fc`, not reachable from `test`.
   My dispatch prompt already knew this (it named the exact branch to use:
   `test-T-MIN-002` tip `94da0cc5`), so I didn't have to rediscover it —
   but that only worked because a human/orchestrator had already done the
   `git log --all -- <file>` archaeology Worker-F14 had to do by hand. Four
   tasks deep now (T-MIN-001 → 010 → 002 → 003), none merged to `test`.
   Repeating the earlier suggestion with more force given the repeat
   occurrence: `fleet audit` should refuse (or at least warn loudly) when
   `audited_repo_sha` is not an ancestor of the target branch, and should
   record/print the actual branch chain a Worker needs to build from,
   rather than relying on each dispatching layer to reconstruct and pass
   that down by hand every time.

2. **The `block` command is a good, correctly-shaped escape hatch, but not
   mentioned anywhere in README.md's Worker lifecycle section.** I found
   it by grepping `bin/fleet.py`'s subparsers after independently
   concluding I could not honestly submit a PASS. It's exactly the right
   primitive (records `previous_status`, `blocked_reason`, logs a
   `BLOCK` event, regenerates `TASKS.md`), but a Worker who *doesn't*
   think to grep the CLI source would likely default to either force-
   submitting a broken handoff or leaving the task silently `CLAIMED`
   forever. Suggest adding a short "If verification cannot pass for a
   legitimate reason outside your control, use `fleet block --reason
   ...` rather than force-submitting" line to the README's Worker
   lifecycle section (step 4), next to the existing "Evidence Before
   Claims" language.

3. **`cmd_verify` discards evidence on failure.** On a failed run it
   prints the captured stdout/stderr to the terminal and logs a
   `VERIFY_FAIL` global event, but writes no handoff file and no
   persistent record of *what* the output was — only that it failed. For
   a case like this one, where the failure output itself is the whole
   diagnostic payload (which specific ledger key remains pending and
   why), that evidence only survives because I'm pasting it into this
   feedback file by hand. A `handoffs/<task>_verify_fail_<n>.yaml` (or
   similar) written on failure, mirroring the PASS path, would make this
   diagnosable without a Worker manually transcribing terminal output
   into a markdown file.

## Repository-Level Feedback (minchiate_tarot)

**What was built:** `finalize_identifications.py` (repo root, pattern of
`dedupe_cards.py`) does not reimplement the rename/naming logic — it
imports `load_ledger`, `save_ledger`, and `update_card_identity` directly
from `minchiate_reviewer.py` and calls `update_card_identity()` for every
ledger entry where `identified` is true and `current_name ==
original_name`. This guarantees the archival naming convention
(`{Type}_{Value}.jpg`, non-alphanumerics stripped) and the collision
check are byte-for-byte the same code path the `/api/update` HTTP
endpoint uses, rather than a second implementation that could drift from
it. Collisions are logged and skipped, never raised; a second run is a
true no-op (verified by `md5sum` on both `ledger.json` and a `research/
evidence/cards_raw/*.jpg` directory listing before/after).

**Testing before the real run, as instructed:** I first ran the script
against a scratch copy (`research/evidence/cards_raw/` + `ledger.json`
copied to a private tmp dir) with a *synthetic* collision (forced two
entries to share `type`/`value`) to confirm the refuse-and-skip path
actually worked before trusting it near real files. It did — 2 skipped,
91 renamed, nothing crashed, nothing overwritten.

**What the real run found:** the production ledger has an actual,
independently-arrived-at collision — not a hypothetical. Two different
raw scans, `830140001_card_08.jpg` (sheet 830140) and
`830154001_card_05.jpg` (sheet 830154), both carry `identified: true`,
`human_confirmed: true`, `type: "Trump"`, `value: "27 (Aries)"`. Both
therefore compute the same target filename, `Trump_27Aries.jpg`. I
didn't want to assume this was a data-entry fluke, so I checked: visually
the two crops are the same engraving (same ram, same pose, same
mountain/prostrate-figure background, same "XXVII" banner), and running
`dedupe_cards.py`'s own `dhash`/Hamming-distance function against both
gives a distance of **7**, well inside the **14** threshold that same
script already uses elsewhere in this repo to call two scans "the same
card." `CARD_REVIEW_PROCESS_AND_IDENTIFYING.md` describes the raw pool as
one deck's worth of cards extracted from "7 overlapping museum scans" of
a single master sheet — both 830140 and 830154 are listed under that
doc's own "Bottom Row Tiles" grouping — so the most likely explanation is
that the overlap between two adjacent tile scans caused the same physical
card to be extracted (and independently identified) twice, and
`dedupe_cards.py`'s pixel-hash pass either ran before both files existed
in the pool or simply missed this pair.

**Why I didn't try to fix the underlying duplicate myself:** doing so
(moving one scan to `research/evidence/cards_raw/duplicates/`, matching
the convention `dedupe_cards.py` already established, and removing or
re-pointing its ledger entry) would drop the ledger below 97 entries or
require inventing a new "this card has been demoted" convention that
isn't part of the existing schema — either way it's an editorial call
about *which* of two real historical scans is canonical, and about a
`ledger.json` structural change, that a one-shot *rename* script has no
business making unilaterally on a research-data repo. I ran the script
for real, let it do exactly what its own definition of done said
(refuse, log, don't crash), and stopped there.

**State left behind:** 92 of 93 targets successfully renamed and
committed to `test-T-MIN-003` (`ad18b35`); `ledger.json` still has all 97
entries; `830154001_card_05.jpg` is the one remaining `current_name ==
original_name` entry, by design, not by omission. `python3
minchiate_reviewer.py --check` still exits 0 against the post-rename
state. `./bin/fleet verify T-MIN-003` was run and failed exactly where
expected (the `assert not pending` line), which is captured verbatim in
this file and in the terminal log referenced by the `BLOCK` event; I
called `fleet block T-MIN-003 --reason ...` with the full diagnosis
rather than submitting a fabricated PASS or leaving the task silently
`CLAIMED`.

**Recommended next steps for a PM/human:**
1. Decide how `830140001_card_08.jpg` vs `830154001_card_05.jpg` should
   be resolved — most likely: keep `830140001_card_08.jpg` as
   `Trump_27Aries.jpg` (already done, it has the larger source crop,
   625×366 vs 609×338, consistent with `dedupe_cards.py`'s own
   larger-area-wins tie-break), move `830154001_card_05.jpg` into
   `research/evidence/cards_raw/duplicates/`, and either drop its ledger
   entry or add an explicit `"duplicate_of"` field — whichever the DoD's
   `len(ledger) == 97` assumption should become once someone decides
   duplicates are allowed to leave the count.
2. Given this is now the second occurrence I'm aware of, worth asking
   whether `dedupe_cards.py` should be re-run over the *current* (now
   mostly-renamed) `cards_raw/` pool to check for any other near-duplicate
   pairs that slipped through the original extraction, before more
   identification/finalization work builds on top of it.
3. The base-branch chain (T-MIN-001 → 010 → 002 → 003, all still unmerged
   into `test`) needs a merge-order decision independent of this task;
   T-MIN-003 only adds one more link to that same unlanded chain.
