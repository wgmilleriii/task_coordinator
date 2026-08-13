# Feedback: PM-F10 (claude-sonnet-5), 2026-08-13

**Session:** audited one OPEN task, T-MIN-021, in the `minchiate_tarot` lane
(Scout-F6's assignment: design the middle-tier court-card study format). PM role
only — no card/format content written, per the fleet's Scout/PM/Worker separation.

## System-Level Feedback (task_coordinator itself)

1. **The primary `task_coordinator` checkout was on `test-engine-fixes` with a large,
   unrelated dirty tree** (many modified `T-PTG-*`, `T-INTY-017`, `bin/fleet.py`,
   `README.md`, an uncommitted `bin/serve-dashboard`, etc. — other agents'
   in-progress work). I did not touch it. Per Scout-F6's prior feedback (same
   complaint, same day) I used `git worktree add <scratch>/tc-main main` to get a
   clean checkout, did the YAML edit, `audit`, `lint`, and `render` there, and
   committed/pushed from the worktree only — the primary clone's dirty state was
   never read from or written to except via `git show`/`git log` (no checkout).
   Seconding Scout-F6's suggestion: the README's boundary rule text ("checkout
   main for commits") should say `git worktree add` explicitly for the hub repo
   too, not just spoke repos — two agents in one day independently had to reason
   past the same ambiguity.
2. **`bin/fleet`'s venv assumption breaks in a worktree** — `source
   "$DIR/../.venv/bin/activate"` looks for a `.venv` sibling of `bin/`, which a
   fresh worktree doesn't have. Workaround (same as Scout-F6 used): activate the
   primary clone's `.venv` directly (`source
   /Users/willismiller/.../task_coordinator/.venv/bin/activate && python
   bin/fleet.py ...` from inside the worktree). This works because `fleet.py`'s
   own `BASE_DIR` is computed from `__file__`, so it correctly resolves paths
   inside the worktree once the interpreter is up — only the venv discovery in
   the `bin/fleet` wrapper script is worktree-unaware. Would be a one-line fix
   (fall back to `which python3` or a `FLEET_VENV` env var) but I didn't patch
   `bin/fleet.py` myself since it's out of my lane as a PM auditing a spoke task,
   and it's shared infrastructure other in-flight agents are actively editing
   right now (see item 1).
3. **`./bin/fleet onboard <repo>` only writes into the target repo** (a
   `.fleet_context.md` sibling file), never into `task_coordinator` itself — so it
   was safe to run directly from the dirty primary clone (`cd
   task_coordinator && source .venv/bin/activate && python bin/fleet.py onboard
   minchiate_tarot`) without a worktree, unlike `lint`/`render`/`audit` which
   write into `task_coordinator`'s own tracked files. Worth documenting this
   asymmetry explicitly in the README's boundary-rule section — it would have
   saved me a false start assuming onboard needed the same worktree treatment.
4. **Pre-existing, out-of-lane lint failure confirmed still present**:
   `T-INTY-017.yaml: Schema Error - Additional properties are not allowed ('dod'
   was unexpected)`. Same failure Scout-F6 flagged earlier today; still
   unaddressed; still not mine to fix (T-INTY-* is out of the minchiate_tarot
   lane per the boundary rule). Flagging again so it doesn't silently age out of
   view.

## Repository-Level Feedback (minchiate_tarot)

**What was audited:** `T-MIN-021` — Scout-F6's task to design a middle-tier
court-card study format (`research/pilots/COURT_CARD_FORMAT_SPEC.md`, extending
the light tier) plus one `SUIT-CUPS-12` pilot at that new tier and a three-way
comparison note.

**Premise verification (all confirmed against `test`@`82721eb`):**
- `research/pilots/SUIT_CARD_FORMAT_SPEC.md` (light tier) exists.
- `research/pilots/SUIT_TIER_COMPARISON_T-MIN-013.md` exists and its §4 contains
  the cited finding verbatim: CUPS-12's load-bearing pattern findings (hybrid
  anatomy, relatedness qualification, gender-presentation caution, suit-by-suit
  grid dependency) plus the explicit recommendation for a middle tier with "the
  same skeleton plus a bounded 'pattern findings' subsection under §4 ... and
  100% rather than sampled verification for the four Cavaliers."
- Both reference pilots exist: `research/pilots/drafts/STANDARD_SUIT-CUPS-12_Cavalier_of_Cups.md`
  (light) and `research/pilots/Pilot2_SUIT-CUPS-12_Cavalier_of_Cups.md` (full).
- `tasks/human/editorial_decisions_2026-08-12.md`'s D2 section exists and states
  the branch-based-comparative-canon decision plus its verbatim consequence line
  for the court-card middle tier, matching what the task quotes.

All four premises held exactly as Scout-F6 represented them — nothing to correct.

**Verification command — tightened, fail-first confirmed both ways:**
Scout-F6's original command checked the spec file for required markers
(references `SUIT_CARD_FORMAT_SPEC`, has a pattern-variation/pattern-findings
section, requires "evidentiary basis" per form, inherits the `UNVERIFIED` grading
vocabulary) and checked that a distinct `SUIT-CUPS-12` pilot file and a
light/middle/full comparison file exist — but it never inspected the *content* of
the pilot or comparison files, only their existence/filenames. That left a real
gap versus the `definition_of_done`: a worker could satisfy the original command
with an empty middle-tier pilot file, or a comparison note that just happens to
contain the words "light", "middle", "full" without referencing either fixed-name
tier file. I tightened it to also require: the pilot file mentions "hybrid",
states a "per-form"/"per form"/"evidentiary basis" grading gesture, and carries
`UNVERIFIED` (matching the DoD's "carried at or below the full dossier's
confidence, no upgrading" requirement); and the comparison note explicitly names
both `SUIT_CARD_FORMAT_SPEC` and `Pilot2` (the light and full filenames) rather
than just containing the words light/middle/full anywhere.

I dry-ran both the original and the tightened command against the actual
`test`@`82721eb` tree: both fail red right now (`FAIL: middle-tier spec missing`,
exit 1 — none of the three deliverables exist yet). I then built throwaway
scratch fixtures (outside the repo, in my scratchpad, never committed) matching
what a genuine completion would look like — a real spec with the required
markers, a pilot with hybrid/evidentiary-basis/UNVERIFIED language, a comparison
note naming both fixed filenames — and confirmed the tightened command passes
(`PASS`, exit 0) only once all three are genuinely present with the required
content, and still fails if any one piece is missing or empty. `./bin/fleet lint`
passed clean for `T-MIN-021.yaml` after the edit.

**`requires_doc_update` — set to `true`.** This is a judgment call, and my
reasoning: the task introduces `COURT_CARD_FORMAT_SPEC.md`, a new formal tier
sitting alongside `SUIT_CARD_FORMAT_SPEC.md` in the project's research-format
architecture — not a one-off card study but a spec other future work (the
explicitly-out-of-scope rollout to the other 15 courts) will depend on and
extend. The README's PM instruction is "if the task introduces major
architectural changes, you MUST manually add `requires_doc_update: true`" — a new
sibling format tier that changes how all future court-card work gets authored
clears that bar for me, even though this task's own deliverable is scoped to one
pilot. Flagging it now means the janitor protocol will pick it up once this task
reaches `DONE`, rather than the new tier quietly existing undocumented in the
Obsidian vault / doc sweep.

**Audit outcome:** unlocked. `./bin/fleet audit T-MIN-021 --auditor PM-F10
--repo-sha 82721eb --command "<tightened command>"` succeeded; task is now
`AUDITED` against `82721eb`, `requires_doc_update: true`, `human_review_required:
true` (unchanged — matches T-MIN-013's own precedent, per Scout-F6's original
scoping).

**Anything that looked wrong on the board:** nothing else in the minchiate_tarot
lane. Scout-F6's open question (whether any of the other 15 courts has more than
two documented variant forms, or no full dossier to lean on at all) is correctly
carried forward into T-MIN-021's own `definition_of_done` as something the
worker's comparison note must surface rather than resolve — I didn't see a need
to add anything further there.

**Recommended next step:** a Worker should claim `T-MIN-021` next — it has no
dependencies, is now unlocked, and doesn't touch any file another open task
claims (the only other file the DoD touches, `SUIT_CARD_FORMAT_SPEC.md`, is
read-only reference material for this task, not edited).
