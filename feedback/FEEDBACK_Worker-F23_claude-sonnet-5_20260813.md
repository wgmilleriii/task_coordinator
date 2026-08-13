# Feedback: Worker-F23 (claude-sonnet-5) — 2026-08-13 — T-MIN-021

## System-Level Feedback

`fleet.py` resolves a task's target repo as a hardcoded sibling of `BASE_DIR`
(`os.path.join(BASE_DIR, '..', repo_name)`), in `onboard`, `verify`, `sweep-docs`,
and related commands. That collides directly with the README's own HARD REQUIREMENT
to do all work in an isolated `git worktree add ../<repo>-<TASK-ID>` — a worktree by
definition is *not* named `minchiate_tarot`, so `fleet verify` cannot find it unless
the coordinator's own checkout is also relocated into a directory whose sibling is
literally named `minchiate_tarot`. I worked around this by (1) running `onboard` from
the primary `task_coordinator` checkout, whose real sibling *is* `minchiate_tarot`
(read-only, so safe even though that checkout is mid-dirty on `test-engine-fixes`),
and (2) for `verify`, creating a fresh `task_coordinator` worktree in a scratch
directory and adding a symlink named `minchiate_tarot` beside it, pointing at my task
worktree — `os.path.exists()` and `subprocess(cwd=...)` both follow symlinks fine, so
`verify` ran and captured evidence correctly. This works but is not obvious, and nothing
in the README documents it. Recommend either: (a) add a `--repo-path` override flag to
`verify`/`onboard`, or (b) have the README's worktree instructions explicitly cover the
verify step (e.g. "temporarily symlink `../<repo_name>` to your task worktree before
running `fleet verify`, then remove the symlink after"). I did not modify `fleet.py`
itself since the task didn't call for engine changes and another agent's uncommitted
edits to `bin/fleet.py` are already sitting in the primary checkout's dirty
`test-engine-fixes` state — possibly they're addressing exactly this.

Also confirming the now-established pattern from the last two agents: `git worktree add
<tmp> main` for coordinator YAML/commit work, with the worktree removed afterward, worked
cleanly and left the primary `task_coordinator` checkout (on `test-engine-fixes`, with
substantial other agents' uncommitted work) completely untouched. No new lessons there,
just confirming the pattern holds for a third consecutive worker.

## Repository-Level Feedback

Task: design the middle-tier court-card study format (T-MIN-021), implementing D2's
"branch-based comparative canon" decision as the direct follow-up to T-MIN-013's
suit-card format work. Deliverables: `research/pilots/COURT_CARD_FORMAT_SPEC.md`
(extends `SUIT_CARD_FORMAT_SPEC.md` verbatim on skeleton/legend/claim-namespace/
FORBIDDEN, adding one bounded §4a "Pattern-variation findings" subsection), a
middle-tier `SUIT-CUPS-12` pilot at `research/pilots/drafts/COURT_SUIT-CUPS-12_
Cavalier_of_Cups.md` (third treatment of the same card alongside the existing light
and full pilots), and `research/pilots/COURT_TIER_COMPARISON_T-MIN-021.md` comparing
all three tiers by filename.

The core design decision was how to let a card show two mutually exclusive,
both-authentic historical forms (hybrid-bodied vs BM 1896,0501.35/.103 ordinary-rider
Cavaliers) without either merging them into one blended description or silently
preferring one — D2 already decided *that* both get shown; my job was the mechanics.
§4a's answer is a per-form register: each form gets its own label, evidentiary basis,
confidence grade, and explicit statement of what that evidence proves vs doesn't
(existence/non-universality is a much weaker claim than frequency/independence, and
BM .35/.103 being a *related* pack family rather than independent witnesses is
exactly the kind of qualification that's easy to lose if forms aren't separated).
I also added a "rank-vs-pattern separation" line as a required §4a element — stating
explicitly which attributes are identity-defining (stable across all forms) vs
pattern-selectable (the thing the forms disagree on) — because without that, "show
both forms" risks reading as "the card has an ambiguous identity" rather than "one
card, one identity, one selectable attribute."

The comparison note's honest finding: the middle tier reproduces the full dossier's
per-form separation *structurally*, but its evidentiary chain for the underlying BM
catalog claims still terminates at `Pilot2_SUIT-CUPS-12_Cavalier_of_Cups.md` — the
middle-tier pilot carries the hybrid/ordinary-rider claims at `[UNVERIFIED]`, exactly
as the light tier did at `CU12-C06`, because neither tier re-opens the BM records
itself. This is disclosed, not papered over. I flagged two real open edge cases rather
than assuming this pilot resolves them: (1) SUIT-CUPS-12 is the *best* case for the
middle tier because it already has a full dossier to lean on — the other 15 courts
don't, and the format alone doesn't manufacture evidence nobody has opened yet;
(2) this pilot has exactly two documented forms, and whether §4a's "no silent
preference" rule still reads cleanly at three-plus forms with asymmetric evidence is
untested.

Local dry-run of the exact `verification_command` passed before committing, and
`fleet verify` confirmed PASS against the pushed branch. Submitted to `PEER_REVIEW`
at head `353abdc56fcb3d11b3a8b4afdf3239f35be35fe0` on `test-T-MIN-021`, pushed to
origin.

Next steps for the human: this task deliberately stayed in scope (format + one pilot
+ comparison note; no rollout to the other 15 courts, no prompt/art-direction work, no
Visual Canon policy update — all correctly out of scope per D2's own follow-up list).
The comparison note's open edge case #1 is the real decision point before rollout:
someone needs to either write lightweight dossiers (or at least open the relevant
institutional sources) for the other 15 courts before their middle-tier cards can cite
pattern-variation findings at more than `[UNVERIFIED]`-with-nothing-behind-it, or accept
that most of the 15 will have "no documented pattern variation on the record" (which
§3.1 of the new spec treats as a valid, distinct answer from "not checked").
