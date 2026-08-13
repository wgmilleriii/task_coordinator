# Feedback: Worker-F25 (claude-sonnet-5) — T-MIN-023, 2026-08-13

## Context

Dispatched to author the ten Batons pip cards (`SUIT-BATONS-01`..`-10`, Ace
through Ten) to the light-tier suit-card format. I was explicitly warned up front
that a prior agent on a sibling task (T-MIN-022) had been burned by a stale local
`main` ref in the coordinator repo, and told to fetch `origin/main` and verify the
task existed there before doing anything else. I did: `git fetch origin main`,
then `git show origin/main:tasks/active/T-MIN-023.yaml` to confirm the task
before touching any local state. This avoided the false-negative trap entirely.

## System-Level Feedback

1. **`bin/fleet.py`'s `BASE_DIR` resolves relative to the *script's own path*, not
   the caller's `cwd`.** This means `python3 /path/to/task_coordinator/bin/fleet.py
   claim ...` always operates on `task_coordinator`'s own `tasks/active/`,
   regardless of where you run it from. Concretely: I built a fresh worktree at
   `/tmp/tc-claim-min023` from `origin/main` (per the dispatch instructions) and
   tried `python3 /Users/.../task_coordinator/bin/fleet.py claim T-MIN-023 ...`
   from inside it — this silently read the *primary* coordinator clone's
   `tasks/active/` (which was on the dirty `test-engine-fixes` branch and didn't
   have `T-MIN-023.yaml` at all), and failed with "Task not found." The fix is
   simple once you know it: invoke the *worktree's own copy* of `fleet.py`
   (`python3 bin/fleet.py ...` from inside the worktree), not the primary clone's
   copy, and the worktree's `tasks/active/T-MIN-023.yaml` (freshly pulled from
   `origin/main`) is used correctly. I'd flag this as a worse trap than the stale-
   `main` issue: it doesn't fail loudly with a hint about staleness, it just says
   "not found" the same way a genuinely missing task would, and it's easy to miss
   that you invoked the wrong copy of the script. Recommend either making
   `BASE_DIR` resolve from `cwd` when a `tasks/active/` directory is present
   there, or having the "Task not found" error print which `ACTIVE_DIR` it
   actually searched, so an agent immediately sees it queried the wrong repo copy.

2. **Confirming Worker-F24's finding: `cmd_verify` on the *primary* coordinator
   clone's dirty `test-engine-fixes` branch already has the worktree-aware
   fallback** (`worktree_path = BASE_DIR/../<repo>-<task_id>`, checked before
   the plain sibling-directory fallback), and it worked perfectly once I copied
   my claimed `T-MIN-023.yaml` into that clone's `tasks/active/` temporarily
   (removed again right after, so no lasting mutation to the dirty clone). This
   meant I did **not** need the "briefly checkout the task branch in the primary
   spoke-repo clone" workaround at all — `fleet verify` found and used
   `minchiate_tarot-T-MIN-023` directly. This is a second, independent
   confirmation (after Reviewer-F29 and Worker-F24) that this fix exists,
   works, and should be cherry-picked onto `main` — every worker after me is
   still going to rediscover the same friction until it lands.

3. Minor, same as Worker-F24's note: `fleet.py` needs `jsonschema` from the
   coordinator's own `.venv`; sourcing `task_coordinator/.venv/bin/activate`
   before running any worktree-local copy of the script was required.

## Repository-Level Feedback (minchiate_tarot)

**What was done:** authored all ten Batons pip cards (`SUIT-BATONS-01` through
`-10`, Ace through Ten) fresh to `SUIT_CARD_FORMAT_SPEC.md`'s light-tier skeleton,
plus `research/pilots/Batons_Pip_Batch_Verification_Report.md` with a per-card
recomputation table and PASS verdicts for all ten. No full dossier exists for any
Batons pip (confirmed by repo search — no `Pilot*_SUIT-BATONS-*` file anywhere),
so `drafts/STANDARD_SUIT-COINS-04_Four_of_Coins.md` (working pilot) and the Swords
batch's `STANDARD_SUIT-SWORDS-01_Ace_of_Swords.md` (T-MIN-022, same-tier long-suit
precedent) were used as *structural* models only — every fact was pulled fresh
from the registry and the named source documents.

**Registry arithmetic:** Batons is the contiguous `sort_order` block **15–28**
(recomputed row-by-row against `Stage5_Master_Card_Registry.csv` at `test` HEAD
`0ff3c97`, not assumed from the task brief's summary, which turned out correct but
was independently reverified anyway). Pips are sort_order 15–24; the four courts
(Fante 25, Cavallo 26, Regina 27, Re 28) were confirmed out of scope and were not
written or restated beyond naming them for the boundary check. Rank-in-suit =
sort_order − 15 + 1, shown per card, not asserted.

**The independent long-suit-order check:** the brief was explicit that the Swords
batch (T-MIN-022) found no sourced trick order for the long suits, and warned not
to assume the same absence carries over to Batons without checking. I did check
independently rather than inheriting the finding: a repo-wide search for
"baston"/"bastoni" outside the registry and card-id scaffolding, plus a direct
re-read of `Pilot3_TRUMP-08_Justice.md` and
`Bernardi_1790_Verzicola_Boundary_Resolution_Note.md` in full. Found nothing —
same absence, now independently confirmed for Batons rather than assumed. Every
card's §2 marks the long-suit trick order `[UNVERIFIED]` and explicitly declines
to import the round-suit (Coins/Cups) inverse-numeral rule.

**Scoring disposition:** identical across all ten cards, sourced through the Four
of Coins pilot's RULE-1790 transcription chain (Kings get five points, the other
thirteen cards of every suit get none; every captured card contributes exactly one
card to the count) and the Justice pilot's verzicola hedge (line 92: no suit-
numeral combination value demonstrated, no categorical exclusion asserted either).

**Iconography:** no full dossier or specimen-level observation exists for any
Batons pip on this corpus. Every card's §4 states this as a sourced absence rather
than inventing a plausible baseline (e.g. a specific pip arrangement) — the
temptation to describe "N batons arranged diagonally" or similar was there and was
deliberately not taken.

**A note on avoiding the Justice-pilot failure mode:** this project's history
includes a study that was failed and archived for being "a verbatim pilot clone."
Because this batch is ten cards that share nearly all their scoring/rank-arithmetic
boilerplate by the format spec's own design (Bernardi's rule doesn't distinguish
within a suit's ten non-court cards), I made a point of checking that what
*varies* per card — sort_order, rank-in-suit arithmetic, pip count, the specific
RWS Wands scene named as a negative comparison, and all seven claim IDs — is
genuinely per-card, not copy-pasted with only the card name swapped. All ten
landed at an identical 106 lines, which is an artifact of the batch's structural
uniformity (documented explicitly in the verification report), not padding or a
sign of un-differentiated content.

**Self-verification performed before submission:**
- Recomputed all ten rank-in-suit arithmetic lines against the registry CSV
  directly (row-by-row), independent of the task brief's stated range.
- Grepped every drafted file for court-card ID leakage (`SUIT-BATONS-11..14`) —
  none found.
- Confirmed every card carries the five required structural markers, lands at 106
  lines (well within the 60–120 band), has 7 claims-table rows, and uses the
  `BA<NN>-C<NN>` claim namespace disjoint from Coins/Cups/Swords and the trump
  studies.
- Ran the audited `verification_command` locally before invoking `fleet verify`,
  confirming exit 0 / "OK, found 10 cards" ahead of time.

**Handoff:** `fleet verify` passed via the coordinator CLI, using the worktree-
aware fallback in the dirty coordinator clone's `bin/fleet.py` (no primary-
minchiate-checkout branch-switch workaround was needed — see System-Level
Feedback #2). Handoff `head_sha`: `183b8ce`. Branch `test-T-MIN-023` pushed to
`origin/test-T-MIN-023` on `minchiate_tarot`. Task submitted to `PEER_REVIEW`.
Both the primary `minchiate_tarot` checkout (restored to `test`) and the primary
`task_coordinator` checkout (untouched, still on `test-engine-fixes` with its
pre-existing dirty state, minus the temporary `T-MIN-023.yaml` copy I removed
after verify) were left as found.

**Suggested next step for the human/PM:** T-MIN-024/025 (Cups/Coins pip batches)
remain. Both suits already have full pilot dossiers (unlike Swords/Batons), so
whoever picks those up should have an easier time on iconography and should
re-check whether either turns up a long-suit-adjacent finding — though Cups/Coins
are round suits with a sourced inverse order, so the open question there is
different (verifying the inverse order is applied correctly per card, not an
absence check). If a future batch or source acquisition ever turns up an actual
Swords/Batons long-suit trick-order witness, it should be retrofitted into all
fourteen Swords/Batons pip-and-court cards across both batches, not just its own
suit — the same recommendation the Swords batch left for me, now confirmed still
open.
