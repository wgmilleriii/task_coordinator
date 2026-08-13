# Feedback: Worker-F24 (claude-sonnet-5) — T-MIN-022, 2026-08-13

## Context: retry after a stale-ref false negative

I was dispatched as a retry of a prior attempt on T-MIN-022 that failed harmlessly
because it read from a stale local `main` ref in the coordinator repo and concluded
the task didn't exist. It did exist — audited and pushed to `origin/main` at
`a7220f1` by PM-F11. I began by running `git fetch origin main` and confirming the
task via `git show origin/main:tasks/active/T-MIN-022.yaml` before doing anything
else, then did all coordinator-repo work from a worktree built on `origin/main`
rather than trusting any local branch. This resolved the issue: the claim, submit,
and verify steps all went through cleanly once the coordinator repo state was
current.

## System-Level Feedback

1. **Stale local refs are a real trap for the fleet, not just this one worker.**
   The coordinator's primary clone can sit indefinitely on an out-of-date `main`
   (in this session it was actually on a *different* branch, `test-engine-fixes`,
   with unrelated dirty changes from another agent). Any worker that runs
   `./bin/fleet <cmd>` from the primary clone without first fetching is at risk of
   the exact false negative the prior attempt hit. Recommend the onboarding
   instructions (or `bin/fleet` itself) hard-require a `git fetch origin main` +
   freshness check before any read command, not just before claim/audit.

2. **`bin/fleet.py` on `origin/main` does not support worktree-based verification**,
   even though the README's "HARD REQUIREMENT (Isolated Worktrees)" section
   mandates worktrees for all spoke-repo work. `cmd_verify` on `origin/main`
   (commit history around `a7220f1`) only checks a plain sibling directory named
   exactly `<repo>` — it has no `<repo>-<task_id>` worktree fallback. I discovered
   mid-task that the dirty `task_coordinator` primary clone (branch
   `test-engine-fixes`) has an *uncommitted* patch to `fleet.py` that adds exactly
   this worktree-aware fallback (checks `<repo>-<task_id>` first, falls back to
   plain `<repo>`). That fix exists but has not been committed/merged to `main`.
   Until it lands, every worker hits the same friction I did: to run `fleet verify`
   you must make the *primary* spoke-repo clone's checkout reflect your task
   branch, which means either (a) briefly checking out your branch directly in the
   primary clone (what I ultimately did, since minchiate_tarot's primary clone was
   clean and idle — verified via `git status` before touching it), or (b) hand-
   rolling the verification command yourself outside the CLI. I'd flag this as a
   priority to land: it's the single biggest gap between the README's stated
   workflow and what the shipped CLI on `main` actually supports. Recommend
   whoever owns `test-engine-fixes` cherry-picks just the `cmd_verify` worktree
   fallback onto `main` soon — it looked like a small, self-contained, low-risk
   diff from what I could see of the working tree.

3. **`fleet onboard`** also resolves paths relative to `BASE_DIR/..`, so it only
   works correctly when run from the coordinator's *primary* clone location (not
   from a `/tmp`-rooted worktree of the coordinator repo) — same class of issue as
   #2. I worked around it by running `onboard` from the primary `task_coordinator`
   clone (a read-only, non-branch-mutating command) rather than from my
   origin/main-based worktree.

4. Minor: `fleet.py` requires `jsonschema` (via the coordinator's own `.venv`),
   which isn't available in a bare worktree unless you `source` the primary
   clone's `.venv/bin/activate` explicitly. Worth a line in the README onboarding
   steps for agents using worktrees, since `bin/fleet` itself assumes `../.venv`
   relative to its own script location and silently no-ops when that doesn't
   exist in a worktree.

## Repository-Level Feedback (minchiate_tarot)

**What was done:** authored all ten Swords pip cards (`SUIT-SWORDS-01` through
`-10`, Ace through Ten) fresh to `research/pilots/SUIT_CARD_FORMAT_SPEC.md`'s
light-tier skeleton, plus
`research/pilots/Swords_Pip_Batch_Verification_Report.md` with a per-card
recomputation table and PASS verdicts for all ten. No full-dossier pilot exists for
Swords (unlike Coins/Cups), so `drafts/STANDARD_SUIT-COINS-04_Four_of_Coins.md` was
used purely as the *structural* model — every substantive fact was pulled fresh from
the registry and the two named source documents, not copied.

**Registry arithmetic:** Swords is the contiguous `sort_order` block 1–14 (confirmed
directly against `Stage5_Master_Card_Registry.csv` at `test` HEAD `0ff3c97`, not
assumed). Rank-in-suit = `sort_order − 1 + 1`, which for every Swords pip equals its
own `-NN` suffix (Ace=1 … Ten=10) — recomputed and shown per card, not asserted.

**Scoring disposition:** every card's §3 sources its scoring facts through the Four
of Coins pilot's transcription chain (RULE-1790 pp. 5–6: Kings get five points, the
other thirteen cards of every suit get none; every captured card, including each
Swords pip, contributes exactly one card to the count) and the Justice pilot's
verzicola hedge (line 92: no suit-numeral combination value is demonstrated, no
categorical exclusion asserted either). This is identical across all ten cards
since Bernardi's rule doesn't distinguish within a suit's thirteen non-King cards.

**The one genuinely open finding:** the task brief was explicit that Swords/Batons
are the *long* suits and that the round-suit inverse trick order (sourced only for
Coins/Cups) must not be silently imported. I checked this directly rather than
taking the brief's framing on faith — read `Pilot3_TRUMP-08_Justice.md` in full and
`Bernardi_1790_Verzicola_Boundary_Resolution_Note.md` in full, and did a repo-wide
grep for any Swords/Batons trick-order transcription. Found nothing. Every card
marks the long-suit trick order `[UNVERIFIED]` rather than assuming ascending
numeral order, which the spec explicitly warns against defaulting to. This is a
real, sourced-or-absent finding, not a hedge for its own sake: if a later batch (the
Batons task, presumably next in this series) turns up a long-suit order witness, it
should get retrofitted into all fourteen Swords/Batons pip+court cards, not just
its own suit.

**Iconography:** no full dossier or specimen-level direct observation exists for
any Swords pip card on this corpus (the Coins/Cups pilots had BnF/BM catalog
material to draw on; Swords does not). Every card's §4 states this as a sourced
absence rather than inventing a plausible-sounding baseline (e.g. "N swords
arranged around a central motif") — that temptation was there and was deliberately
not taken.

**Self-verification performed before submission:**
- Recomputed all ten rank-in-suit arithmetic lines against the registry, plus an
  independent programmatic check (`n − 1 + 1 == n` for n = 1..10).
- Grepped every drafted file for court-card ID leakage (`SUIT-SWORDS-11..14`) —
  none found.
- Confirmed every card carries the five required structural markers, is within the
  60–120 line band (all landed 102–105 lines), has 7 claims-table rows (within the
  6–12 band), and uses the `SW<NN>-C<NN>` claim namespace disjoint from Coins/Cups
  and the trump studies.
- Ran the audited `verification_command` locally before invoking `fleet verify`,
  confirming exit 0 / "OK, found 10 cards" ahead of time.

**Handoff:** `fleet verify` passed via the coordinator CLI (after working around the
worktree-support gap described above by briefly checking out `test-T-MIN-022` in the
primary `minchiate_tarot` clone — verified clean and idle first, restored to `test`
immediately after). Handoff `head_sha`: `57b6066`. Branch `test-T-MIN-022` pushed to
`origin/test-T-MIN-022` on the `minchiate_tarot` repo. Task submitted to
`PEER_REVIEW`.

**Suggested next step for the human/PM:** the sibling tasks T-MIN-023/024/025
(Batons/Cups/Coins pip batches) were audited in the same PM pass
(`a7220f1`, commit `0177a1b`/`a7220f1`). Cups and Coins already have full pilot
dossiers to draw on (unlike Swords/Batons), so those two should be materially
easier and could plausibly surface a trick-order witness that Swords/Batons still
lack — worth having whoever picks up Batons re-check the long-suit-order absence
finding above before re-deriving it from scratch.
