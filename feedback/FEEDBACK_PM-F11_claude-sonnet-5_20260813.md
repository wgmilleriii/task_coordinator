---
title: "PM-F11 Audit Session — T-MIN-022/023/024/025 (Swords/Batons/Cups/Coins pip batches)"
created_at: "2026-08-13T00:00:00Z"
last_modified: "2026-08-13T00:00:00Z"
author: "PM-F11"
status: "active"
category: "00-Meta"
---

# System-Level Feedback

- **The primary `minchiate_tarot` checkout being dirty on `test-engine-fixes` is a real hazard** — I
  had to build my own worktree from `test` (0ff3c97, matching all four tasks' cited SHA) rather than
  touch the primary clone at all, per the explicit instruction. Worked cleanly, but a PM who forgets
  this and runs `git -C ../minchiate_tarot log` or similar in a hurry could still misread branch state
  if they're not careful to specify refs (`origin/test`, not the checked-out branch). No incident here,
  just flagging that this is a standing trap for any PM auditing this repo until that other agent's
  work lands or is cleaned up.
- **Same coordinator-venv gap PM-F7 hit**: the `bin/fleet` wrapper script hardcodes
  `source "$DIR/../.venv/bin/activate"`, which only exists in the primary coordinator clone, not in a
  `git worktree add` checkout. I worked around it by invoking
  `/path/to/primary/.venv/bin/python bin/fleet.py <args>` directly from inside the worktree. This is
  the second PM session in a row to hit this exact friction (see PM-F7's feedback on 2026-08-11) — worth
  fixing for real this time, e.g. have `bin/fleet` fall back to system `python3` with a `pyyaml`
  dependency check, or resolve the venv relative to the coordinator repo root via `git rev-parse
  --git-common-dir` instead of a hardcoded relative path, so it works from any worktree.
- **`tasks/active/T-INTY-017.yaml` fails `./bin/fleet lint`** with `Additional properties are not
  allowed ('dod' was unexpected)` — pre-existing, not touched by me or by this session, and squarely in
  the INTY lane which is outside my boundary per the README's CRITICAL BOUNDARY RULE. Flagging for
  whichever PM/coordinator owns that lane; I did not attempt a fix.
- **Found a real false-positive risk in the "grep for forbidden terms" self-verification pattern** that
  the scout wrote into all four tasks' scope items (and that recent batches, e.g. trump/element, have
  used before): the working Four-of-Coins pilot (`drafts/STANDARD_SUIT-COINS-04_Four_of_Coins.md`)
  itself legitimately contains the word "pentacles" three times, in its §7 Boundaries section, precisely
  because the spec requires naming the forbidden import being excluded ("vs 'Four of Pentacles' (RWS):
  ... not occult pentacles ... Forbidden per spec §5: RWS Four of Pentacles meanings"). A blind
  whole-file substring grep for "pentacles" (or "upright"/"reversed" in a similarly-phrased boundary
  line) would fail a compliant, well-written card. I built and dry-ran a version of the tightened
  verification command with a naive forbidden-term grep first, caught this against the real pilot
  content, and dropped it before finalizing — see the Repository-Level section for what shipped instead.
  Any future PM tightening a suit-card verification command should sanity-test the check against the
  *passing* Four of Coins pilot, not just confirm it fails against nothing, or it can silently ship a
  check that no compliant worker could ever pass.

# Repository-Level Feedback

## What I did
Read `research/pilots/SUIT_CARD_FORMAT_SPEC.md` in full and audited all four pip-card authoring batches
scoped by SCOUT-F7: **T-MIN-022** (Swords, 10 cards), **T-MIN-023** (Batons, 10 cards), **T-MIN-024**
(Cups, 10 cards), **T-MIN-025** (Coins, 9 cards — Four of Coins already complete and correctly excluded).
All four moved `OPEN` → `AUDITED` against `test` @ `0ff3c97` (confirmed current HEAD of `test`, matching
every task's cited SHA).

## Premise verification (before unlocking anything)
1. Confirmed `research/pilots/SUIT_CARD_FORMAT_SPEC.md` exists and read it end to end — its §3 skeleton,
   §4 claim-namespace rule (`<SUIT2><RANK2>-C<NN>`), and §5 forbidden-terms list all match what the four
   task scopes cite.
2. Spot-checked **three of the four suits' `sort_order` ranges** directly against
   `research/05-registry-and-audit/Stage5_Master_Card_Registry.csv` myself (not trusting the scout's
   report): Swords 1–14 (pips 01–10, courts SUIT-SWORDS-11..14 = Fante/Cavallo/Regina/Re), Cups 29–42
   (pips 01–10, courts 11..14 = Fantina/Cavallo/Regina/Re — confirmed Cups uses **Fantina**, not Fante,
   correctly distinguishing it in T-MIN-024's scope), Coins 43–56 (pips 01–10 minus 04 already done,
   courts 53–56). Also pulled Batons (15–28) while I had the CSV open — all four block boundaries and
   rank labels check out exactly as each scout-authored scope states. No corrections needed here.
3. Confirmed the excluded court `card_id`s for Swords and Cups are genuinely rank 11–14 (courts), not
   pip ranks, by reading their registry rows directly (`rank_or_number` column: Fante/Cavalier/Queen/King
   for Swords, Fantina/Cavalier/Queen/King for Cups).
4. Grepped `research/pilots/drafts/` for all 39 target pip-card ids: **zero pre-existing drafts** for
   any of the 39 target cards. Only pre-existing suit-card-format files are the two pilots
   (`STANDARD_SUIT-COINS-04_Four_of_Coins.md`, `STANDARD_SUIT-CUPS-12_Cavalier_of_Cups.md`, the latter a
   court card correctly out of scope for T-MIN-024) plus the unrelated trump/personality studies.

## Tightening the verification commands
The scout's original verification commands only checked for file existence plus five header-string
markers (`Maturity state`, `IMG-001`, `Claims table`, `Rank in suit`, `Scoring (sourced or absent)`) —
real section headers, not free-floating strings, but no check on line-count band, no check that a pip
file hadn't leaked a court card's id, and (per this task's brief) no genuine "content-marker discipline"
beyond header presence. I added two objective, false-positive-safe checks to all four commands:
- **Line-count band 60–120** (matches spec §1 and every task's DoD), and
- **Court-card-id leak check** — a pip file may not contain the literal `SUIT-<suit>-11/12/13/14` id
  strings (confirmed safe against real content: the Four of Coins pilot discusses "King" scoring by rank
  name only, never by court `card_id`, so this can't false-positive a legitimate pip card).

I deliberately **did not** add a forbidden-term (`pentacles`/`upright`/`reversed`/etc.) grep to the
automated command, for the reason detailed in the System-Level section above — it produces false
positives against exactly the kind of compliant boundaries-section language the spec requires. That
check stays a human/self-verification step (already in each task's scope item 6), not an automated gate.

**Dry-run confirmed all four tightened commands genuinely fail RED right now** against the real,
committed `test` @ `0ff3c97` tree (all report `MISSING/INVALID CARDS [...]` for every expected NN,
since none of the 39 target files exist yet). I also **sanity-tested the tightened logic against the
real, passing Four of Coins pilot** (temporarily targeting its own id `04`) to confirm the new checks
don't reject legitimately good work — it passes every content check and only fails on `NO REPORT`
(expected, since that pilot predates the batch-report requirement). Each command was executed exactly
as `subprocess.run(cmd, shell=True)` will run it (`/bin/sh -c "..."`) before being passed to
`./bin/fleet audit --command`, not just eyeballed as a string.

## Dependency / shared-state check
Confirmed all four scopes write only to suit-specific, non-overlapping paths
(`research/pilots/drafts/STANDARD_SUIT-<SUIT>-NN_*.md` and one suit-specific
`research/pilots/<Suit>_Pip_Batch_Verification_Report.md` per task) and explicitly restate registry facts
as "read, never improved" (spec §5's own rule) rather than editing
`Stage5_Master_Card_Registry.csv` or `SUIT_CARD_FORMAT_SPEC.md`. `dependencies: []` on all four is
correct — there is no real ordering constraint, and no merge-conflict risk between the four even if they
land on four different worker branches, since no two tasks touch the same file.

## `requires_doc_update`
Left `false` on all four, per instruction and my own read: this is content authoring inside an
already-established, human-approved format (T-MIN-013 pilot format, closed), not an architectural change.

## Nothing left OPEN
All four premises held; all four unlocked to AUDITED. No corrections to the scout's registry facts were
needed (all verified accurate on spot-check) — the only material change I made was tightening the
verification commands as described above.

## Recommended next steps
- A worker (or four, in parallel — no ordering dependency) can now claim T-MIN-022 through T-MIN-025.
  Since none share files, they're safe to run concurrently even from different worktrees/branches.
- Whoever runs the fleet `lint` next should also flag `T-INTY-017.yaml`'s schema error to that lane's
  owner — not fixed here, out of my boundary.
