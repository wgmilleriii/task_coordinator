# Feedback: Reviewer-F28 (claude-sonnet-5) — 2026-08-13 — T-MIN-021 peer review

## System-Level Feedback

`T-MIN-021.yaml` and its `AUDIT`/`CLAIM`/`SUBMIT` history exist on `origin/main`
but not on the `task_coordinator` primary checkout's current branch
(`test-engine-fixes`, dirty with other agents' uncommitted work, per the README's
boundary rule). `tasks/active/T-MIN-021.yaml` is absent from that checkout entirely.
Before assuming a task doesn't exist, a reviewer should check `origin/main` via
`git show origin/main:tasks/active/T-<ID>.yaml` rather than only grepping the
primary checkout's working tree — the primary checkout being mid-flight on an
unrelated branch is expected/documented behavior, not evidence the task is
missing. I did this and it resolved cleanly; flagging it because a less careful
pass could have wrongly reported the task as not found. Recommend the README's
Reviewer instructions explicitly say "check `origin/main`, not just the primary
checkout's current branch" since reviewers are dispatched with task_id/head_sha
from the database, not from whatever the primary checkout happens to have on disk.

Separately: `bin/fleet` on this checkout expects a `.venv` at
`task_coordinator/.venv` (`source "$DIR/../.venv/bin/activate"`) that did not exist
in my coordinator worktree — `git worktree add` doesn't carry over an untracked
`.venv`. I created a fresh venv and `pip install -r requirements.txt` inside the
worktree to get `./bin/fleet` running; this worked but cost a few minutes and isn't
mentioned anywhere. Same recommendation as prior workers: document this setup step
(or vendor a lighter dependency set) so each fresh reviewer/worker worktree doesn't
have to rediscover it.

`schemas/doc_frontmatter.schema.json` unrelated pre-existing lint failure noted in
passing: `./bin/fleet lint` reports `T-INTY-017.yaml: Additional properties are not
allowed ('dod' was unexpected)`. This is in the INTY lane, out of my boundary — not
touched, just surfaced here since I ran a full lint pass as part of my own sanity
check before committing.

## Repository-Level Feedback

Reviewed T-MIN-021 (Worker-F23, head `353abdc56fcb3d11b3a8b4afdf3239f35be35fe0`):
the middle-tier court-card format spec plus one `SUIT-CUPS-12` (Cavalier of Cups)
pilot written to it, plus a three-tier comparison note. Verdict: **PASS**, task
moves to `HUMAN_REVIEW` per `human_review_required: true`.

The deliverable is genuinely good work, not just passing-the-bar work. The spec
(`COURT_CARD_FORMAT_SPEC.md`) is a real extension of the light tier — I diffed it
line-by-line against `SUIT_CARD_FORMAT_SPEC.md` and found essentially zero
copy-paste overlap; every inherited rule is invoked by explicit reference
("§2/§3/§4/§5 ... applies verbatim unless this document says otherwise"), and the
one new section (§4a, the per-form pattern-variation register) is specified to a
level of detail — five required fields per form, a worked normative table for the
exact Cavalier case, an explicit "never average confidence across forms" rule —
that would let a different worker author the other 15 courts from the spec alone
without re-deriving the register's shape from scratch.

My main job was fact-checking the worker's own claimed limitation: that the
middle-tier pilot "does NOT stand fully independent of Pilot2 — its evidentiary
chain for the BM catalog claims still terminates there." I opened
`Pilot2_SUIT-CUPS-12_Cavalier_of_Cups.md` directly and traced the citations myself
rather than trusting the comparison note's self-report. It holds up exactly as
claimed: the pilot's Form B claims cite "via Pilot2 C-CUPS12-005/-006/-007" rather
than reopening the BM 1896,0501.35/.103 catalog records with their own citations —
Pilot2 is where those records were actually opened (its `citeturn32search2/3`
markers appear only there). The note is honest in both directions: it doesn't
hide this dependency, but it also correctly scopes the dependency narrowly to the
BM catalog claims specifically — the registry facts (sort order, rank-in-suit
arithmetic) really are independently sourced from the project registry, and the
note doesn't misrepresent those as Pilot2-derivative either. This is the kind of
self-reported-limitation claim that's worth an independent worker checking every
time; in this case it checked out clean, which is itself useful signal about this
worker's reporting reliability going forward.

One thing worth the human's attention at the HUMAN_REVIEW gate, not a review
blocker: the spec's "100% adversarial verification for the four Cavaliers" rule is
concrete and well-reasoned, but the deliverable doesn't exercise it — the Cavalier
of Cups pilot itself is explicitly marked "Draft... not adversarially verified."
So the human is being asked to bless a verification *policy* without seeing one
worked example of what a completed adversarial pass on a Cavalier produces. Given
this pilot is the one Cavalier already in hand, that would have been the cheapest
possible place to demonstrate it. Not disqualifying — out of this task's stated
scope — but worth Chip deciding whether to require it before rollout to the other
three Cavaliers.

Recommended next step for the human: rule on whether the middle tier format is
approved for the 16 courts generally, and separately rule on the open edge cases
the worker flagged rather than resolved (courts with no existing full dossier;
3+-form scenarios) — both are genuinely unresolved, not swept under the rug.
