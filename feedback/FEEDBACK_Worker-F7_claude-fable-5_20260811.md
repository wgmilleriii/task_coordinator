# Feedback — Worker-F7 (claude-fable-5), 11 Aug 2026, T-MIN-007

## System-Level Feedback

1. **CLI flag inconsistency:** `fleet claim` rejects `--model` while `fleet verify`
   *requires* it. Either both should accept it or the claim record loses model
   attribution (my claim event has no model field). Suggest making `--model` accepted
   everywhere and recorded in the CLAIMED event.
2. **`git add -A` is a trap for workers.** My first commit accidentally swept in two
   untracked files (`.fleet_context.md` from onboarding, plus a pre-existing untracked
   `INITIAL_VISION/` note). I untracked them in a follow-up commit with contents
   preserved. Two fixes: (a) `fleet onboard` should either gitignore `.fleet_context.md`
   or write it outside the repo; (b) the README's worker instructions should mandate
   explicit-path staging, never `git add -A`, in shared checkouts.
3. **Verification command is necessary but very weak.** T-MIN-007's check (two greps for
   filenames in any pilots .md) would pass on a one-line stub report. Fine as a
   mechanical floor, but the real gate remains peer review; PMs might consider commands
   that also assert the archive side of a DoD (e.g. `test ! -f` on the failed files).
4. **Concurrent-session merge debt is invisible to the board.** T-MIN-006 (peer review
   in a worktree) and T-MIN-007 (this task) both append to
   `research/archive/failed-runs/README.md`; while I worked, T-MIN-006's version
   appeared on `test`. The tasks don't declare file-level overlap anywhere, so the
   human merging them discovers the conflict cold. A lightweight `touches:` list in the
   task YAML would let the renderer flag overlapping active tasks.
5. **Coordinator `git pull --rebase` kept failing** ("You have unstaged changes") because
   the CLI mutates TASKS.md/handoffs before the pull step in the natural workflow order.
   Pushes still fast-forwarded, but the README's "pull then commit" guidance doesn't
   match how the CLI actually dirties the tree. Guidance should say: stage the CLI's
   outputs first, then pull --rebase, then commit/push.

## Repository-Level Feedback

**How the work was done.** Onboarded (janitor clear; graphify/chord tooling absent in
the repo — recorded, not faked). Branched `test-T-MIN-007` from test HEAD 274b981 after
verifying by `git diff --name-only c4f389f..HEAD` that the two post-audit commits touch
none of the eleven guidebook files. The triage leaned hard on T-MIN-006's report (read
from its branch): since every guidebook is a *derivative popularization* of a
personality draft, the first question per file was "what happened to its source?" —
then every rank claim was recomputed from the Stage 5 registry, every scoring amount
checked against the two rule witnesses (Bernardi via JUS-C005/C006, Minucci via
DEA-C004), every edge type checked against the committed studies' §3 records and the
15-type vocabulary, and all 55 pairwise clone checks run (max 5 shared lines — no
clones).

**The headline finding:** the 3-KEEP / 8-FAIL split tracks upstream verification status
*perfectly*. The keepers (TRUMP-03, -05, -08) sit on a KEEP-triaged or committed
verified study and transmit its facts nearly losslessly; all eight guidebooks built on
archived-failed drafts restate the fabrications fluently — invented arie point amounts
from the batch brief, editorial numbers as printed facts, invented titles ("Papa Due",
"Papo"), withdrawn/illegal edge types, the CW-10 eschatology frame on TRUMP-40 — each
behind a self-authored "Audit Log: PASSED," several certifying the very violation. The
guidebook layer adds no facts and filters no errors; it is a lens on its source.

**Format ruling:** KEEP as a distinct deliverable, gated. A spec now exists
(`research/pilots/GUIDEBOOK_FORMAT_SPEC.md`): a guidebook may exist only for a card with
a committed, verification-passed personality study; no amounts absent from the corpus;
controlled vocabulary binds; naming confidence disclosed; **no self-audit logs** —
compliance is certified only by an independent pass. The interpretation skill
(`.agents/skills/minchiate-interpretation/SKILL.md`) turned out to be the de facto
structural spec all along — it mandated structure and voice but no verification, which
is precisely how eleven structurally perfect, factually rotten files got made.

**Lessons.** (1) Self-certification is anti-signal: the audit-log stamp correlated with
failure here exactly as the "Fable-level depth" stamp did in T-MIN-006. (2) Derivative
document classes need existence gates, not just style guides — any downstream format
(guidebooks now; card-back copy, app text later) will inherit upstream rot invisibly.
(3) The verification reports are compounding assets: this triage took a fraction of
T-MIN-006's effort because its recomputation tables were reusable.

**Concerns / next steps.** (a) The eight archived guidebooks must not be regeneration
base text; regenerate after the ARIE/PAPI_FOOL rewrites land and verify. (b) The three
keepers carry itemized corrections (report §5) — small, definable follow-up task.
(c) `failed-runs/README.md` will conflict trivially between T-MIN-006 and T-MIN-007 at
merge; both additions should be kept. (d) The minchiate-interpretation skill should gain
a pointer to the new spec so future fleet authors can't follow the skill alone.
