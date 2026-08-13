---
title: "End of Session Feedback: Scout-F7 — minchiate_tarot suit-card pip batches"
created_at: "2026-08-13T00:00:00Z"
last_modified: "2026-08-13T00:00:00Z"
author: "Scout-F7 (claude-sonnet-5)"
status: "active"
category: "00-Meta"
---

# End of Session Feedback: Scout-F7 (minchiate_tarot)

## System-Level Feedback

- **T-MIN-021 was a coordinator bookkeeping gap.** `tasks/active/` and
  `tasks/archive/` on the `test-engine-fixes` branch (the PRIMARY checkout's
  current, dirty branch) had no `T-MIN-021.yaml` at all, and neither did
  `main` at the commit I first fetched from `origin/main`... except it did,
  once I actually created a clean worktree from `origin/main` rather than
  trusting the PRIMARY checkout's working tree. The PRIMARY checkout was
  sitting on an unrelated branch (`test-engine-fixes`, with a large pile of
  other agents' uncommitted T-PTG changes) and was not a reliable source for
  "what's the next free task ID" even for read-only inspection. Recommend the
  README's ID-allocation guidance explicitly say: never infer the next free
  ID from the PRIMARY checkout's working tree or its current branch — always
  check a fresh `git worktree add <tmp> main` (or `git ls-tree
  origin/main -- tasks/`) instead, and cross-check against the *target repo's*
  own commit history (a task ID can be "used" — merged into the spoke's `test`
  branch — before the coordinator's own YAML for it is ever committed to
  `main`, as happened here).
- The onboarding (`./bin/fleet onboard minchiate_tarot`) and `.fleet_context.md`
  Janitor Protocol check worked cleanly and quickly ruled out any documentation
  gate blocking this session — good.
- No local `.venv` exists inside a freshly created `git worktree add` checkout
  (it's gitignored, as expected), so `./bin/fleet` fails immediately with
  `python: command not found` / missing `activate` script until you either
  `pip install -r requirements.txt` into a new venv or `source` an existing
  sibling checkout's `.venv`. Recommend the onboarding output or the worktree
  instructions mention this explicitly — it's a predictable first-run trap
  for any agent using the worktree pattern for coordinator YAML work (the
  README's HARD REQUIREMENT section documents the worktree pattern for git
  safety but not this Python-environment wrinkle).

## Repository-Level Feedback (minchiate_tarot)

**What was scoped:** Four OPEN tasks (T-MIN-022 Swords, T-MIN-023 Batons,
T-MIN-024 Cups, T-MIN-025 Coins) authoring the pip (non-court) suit cards to
`research/pilots/SUIT_CARD_FORMAT_SPEC.md`'s light "standard" tier, the format
merged after the Four of Coins / Cavalier of Cups pilot comparison
(T-MIN-013) settled it.

**Facts established from the registry, not assumed** (per
`research/05-registry-and-audit/Stage5_Master_Card_Registry.csv` at
`test`@`0ff3c97`):

- All four suits (Swords, Batons, Cups, Coins) are **exactly 14 cards each**,
  a contiguous `sort_order` block (Swords 1-14, Batons 15-28, Cups 29-42,
  Coins 43-56), split **10 pips + 4 courts** in every suit — not a variable
  split. The task brief's working assumption of "9 or 10 pips depending on
  suit" undersold this: every suit has *ten* pip ranks (Ace-Ten); the only
  reason Coins' batch is nine cards instead of ten is that Four of Coins
  (`SUIT-COINS-04`) already has a finished light-tier study (it's the format's
  own pilot), not because Coins has fewer pip ranks than the other suits.
  Swords/Batons/Cups batches are ten cards each; Coins is nine. Total: 39
  cards across the four tasks.
- **Pip rank labels are plain English ordinals, not a separate Minchiate
  vocabulary**: the registry's `historical_names` column for every pip card
  reads simply "Ace / One", "Two", "Three" ... "Ten" — canonical names are
  literally "Ace of Swords" through "Ten of Swords" etc., Italian "Asso di
  Spade" through "Dieci di Spade". I went in expecting the brief's warned
  possibility of a different historical naming scheme and did not find one on
  the registry; that absence is itself worth recording so nobody re-litigates
  it per-batch.
- **Court rank labels do differ by suit-family, and this matters for
  exclusion correctness**: the long suits (Swords, Batons) use "Fante"
  (Jack/Page, male) for their 11th card; the round suits (Cups, Coins)
  substitute "**Fantina**" (Maid, explicitly female page) instead — not
  "Fante" — confirmed directly from each suit's `rank_or_number` and
  `historical_names` columns (`SUIT-CUPS-11`/`SUIT-COINS-11` both read
  "Fantina / Maid / female page"; `SUIT-SWORDS-11`/`SUIT-BATONS-11` read
  "Fante / Jack / Knave / Page"). All four courts per suit (Fante-or-Fantina,
  Cavalier, Queen, King — sort ranks 11-14 within each suit) are already
  handled by the middle court tier (T-MIN-013 pilot 2 of 2, formalized and
  closed by T-MIN-021, DONE per `main`'s `f250f08`) — I excluded them
  explicitly by card id in each task, including flagging the existing
  Cavalier of Cups pilot by name in the Cups task so nobody re-authors it.
- Confirmed the sourced-or-absent Bernardi scoring discipline is already
  settled by the format spec itself (SS3): Kings get 5 points, the other
  thirteen cards of every suit get none (RULE-1790 pp. 5-6), every captured
  card contributes exactly one to the card-count, and no verzicola
  (combination) value is demonstrated for any suit numeral on the record. I
  did not re-open the Justice pilot's transcription myself — the spec already
  states the rule and its exact source chain (via the Four of Coins pilot's
  `CL-SC04-010/-011` and the Justice pilot's hedged verzicola-boundary line),
  so each new task cites that existing chain rather than inventing a fresh
  sourcing pass.
- One nuance I built into the task text rather than leaving implicit: the
  round-suit inverse-numeral trick order (RULE-1790 cap. II) is sourced
  *generally* for both round suits (Coins and Cups) via the Four of Coins
  pilot's transcription — so the Cups task can cite it directly rather than
  re-deriving it — but the long suits (Swords, Batons) have **no** long-suit
  trick-order witness transcription on the corpus that I could find evidence
  of; I explicitly warned both long-suit tasks not to silently import the
  round-suit's inverse rule and to mark the long-suit ordering `[UNVERIFIED]`
  instead. This is the kind of scoring-invention risk the spec's SS5
  "unsourced amounts" prohibition is aimed at, and it's the sharpest way a
  worker could quietly violate the sourced-or-absent discipline across all
  40 new pip cards, so I called it out per-suit rather than once generically.

**Verification commands**: each of the four tasks' `verification_command` is
a self-contained `python3 -c` script (same idiom as T-MIN-019) that (1) globs
`research/pilots/drafts/STANDARD_SUIT-<SUIT>-*.md`, (2) requires each expected
card id to appear exactly once per file and requires five minimum content
markers (`Maturity state`, `IMG-001`, `Claims table`, `Rank in suit`,
`Scoring (sourced or absent)`) to be present, (3) requires a batch report file
to exist and name every expected card id. I dry-ran all four against the
current `test`-branch content and confirmed all four **fail now** (`MISSING
CARDS [...]`, full list) since no pip drafts exist yet beyond the two format
pilots; I also built a synthetic fixture with ten dummy Swords files + a dummy
report and confirmed the same command **passes** against it, to rule out a
logic bug that always fails regardless of content.

**Next steps for the human / next PM**: audit these four tasks (they need
`audited_repo_sha` before any worker can claim them — I left them `status:
OPEN` deliberately, per the Scout role boundary). They're independent of each
other (no `dependencies`) and could run as four parallel worker batches.
Recommend auditing in suit order Swords → Batons → Cups → Coins so any
format-drift issue the workers find in the first batch (e.g. a
`Rank in suit` heading text mismatch, or a claim-namespace collision) gets
caught before all four are in flight. Also worth deciding, before these are
audited, whether the same 3-of-14 adversarial-sampling verification rate the
format spec proposes (SS6) should be spelled out as an explicit follow-up
verification task per suit, the way the zodiac/element batches got a
dedicated verifier task (T-MIN-005) — I left that decision to the PM/human
rather than pre-scoping a fifth task, since the spec itself marks the
verification workflow "PROPOSED — human decides."
