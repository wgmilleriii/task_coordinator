# Feedback: Scout-F6 (claude-sonnet-5), 2026-08-13

**Session:** scoped one OPEN task, T-MIN-021, into `minchiate_tarot` lane per direct
assignment (D2's recorded consequence: court cards need a middle-tier format spec).
Scout role only — no code or research content written.

## System-Level Feedback (task_coordinator itself)

1. **Primary checkout was dirty on a non-`main` branch mid-session** — `task_coordinator`'s
   primary clone was checked out on `test-engine-fixes` with ~15 modified tracked files
   and ~30 untracked files (other agents' in-progress `T-PTG-*`/`T-INTY-*`/dashboard work).
   The README's boundary rule says "checkout main for commits, restore what you found,"
   but with a dirty tree that instruction is ambiguous about whether `git checkout main`
   in the primary clone is safe (it can fail or silently carry uncommitted changes across
   branches if paths don't conflict). I did not attempt it. Instead I used
   `git worktree add <scratch>/tc-main main` to get a clean `main` checkout, did all
   YAML/feedback writing there, ran `lint`/`render` there (via
   `source .venv/bin/activate && python bin/fleet.py ...`, since `bin/fleet`'s
   `source "$DIR/../.venv/bin/activate"` line assumes a sibling `.venv` next to `bin/`,
   which the worktree doesn't have — worth noting for anyone else who worktrees this repo),
   then committed and pushed from the worktree, leaving the primary clone's dirty
   `test-engine-fixes` state completely untouched. **Suggestion:** the README's
   boundary rule should explicitly recommend `git worktree add` for the *hub* repo
   too when the primary clone isn't on `main` and/or is dirty, not just for spoke
   repos — the current wording ("checkout main for commits") reads as "run checkout
   in place," which is exactly the risky move the spoke-repo HARD REQUIREMENT
   elsewhere in the same README warns against.
2. **`./bin/fleet lint` surfaced one pre-existing, out-of-lane failure**:
   `T-INTY-017.yaml: Schema Error - Additional properties are not allowed ('dod'
   was unexpected)`. Not touched (T-INTY-* is explicitly out of the minchiate_tarot
   lane per the boundary rule) — flagging here so it isn't missed since I noticed it
   while confirming my own task passed lint cleanly.
3. Everything else about the Scout flow (`onboard`, `render`, hand-writing a
   fail-first `verification_command`, `lint`) worked exactly as documented. No
   loopholes found in the schema or CLI for this session's task type.

## Repository-Level Feedback (minchiate_tarot)

**What was scoped:** `T-MIN-021` — design a middle-tier court-card study format
(`research/pilots/COURT_CARD_FORMAT_SPEC.md`, extending the merged light tier
`SUIT_CARD_FORMAT_SPEC.md`) plus one pilot card written to it, `SUIT-CUPS-12`
(Cavalier of Cups) — the same card already covered by the light-tier pilot
(`drafts/STANDARD_SUIT-CUPS-12_Cavalier_of_Cups.md`) and the full dossier
(`Pilot2_SUIT-CUPS-12_Cavalier_of_Cups.md` + JSON), giving three treatments of one
card for direct comparison, plus a short note comparing all three tiers.

**How this was grounded:** read, in order, `SUIT_CARD_FORMAT_SPEC.md` (light tier),
`SUIT_TIER_COMPARISON_T-MIN-013.md` (the evidence base — its actual §4 finding:
*"CUPS-12 (court) is tighter than comfortable: the hybrid-anatomy finding, its
relatedness qualification, the gender-presentation caution, and the suit-by-suit
grid dependency ... are all load-bearing pattern findings that the light format
holds only by leaning on an existing full dossier. The other 15 courts have no
such dossier to lean on"*), the existing light-tier Cavalier pilot, the full
`Pilot2` dossier (specifically its negative-concepts list and the BM 1896,0501.35
vs .103 ordinary-rider-vs-hybrid finding), and `editorial_decisions_2026-08-12.md`'s
D2 section (the human decision this task implements). This is why the task's scope
lines quote the comparison doc and D2 verbatim rather than paraphrasing — the
assignment specifically asked for the real evidence, not a summary of a summary.

**Key scoping decisions:**
- The spec must *extend* the light tier (inherit skeleton/legend/claim-namespace/FORBIDDEN
  list) and add only a bounded pattern-variation subsection — this mirrors the
  comparison doc's own §4 recommendation almost exactly, so the worker has a
  concrete target rather than an open-ended redesign.
- Explicitly fenced off relitigating D2 itself ("show both forms" is decided; the
  spec only implements the mechanics of stating each form's evidentiary basis and
  confidence) — this was the sharpest risk I saw in scoping a task this close to a
  human policy decision: a worker with wide latitude could easily drift into
  re-arguing whether branch canon is right, which isn't this task's job.
- Fenced out the two other D2 follow-up items (Visual Canon policy doc, prompt/art-direction
  guidance) since they're separately listed in D2's own "Affected artifacts" checklist
  and are real, but different-shaped work (policy + pipeline, not format design).
- `human_review_required: true`, P2/ANY — matches T-MIN-013's own precedent exactly,
  since this is the same kind of format-decision task T-MIN-013 was.

**Verification command:** hand-written, fail-first-verified by dry-running it
against the current `test`-branch content (`82721eb`) before writing it into the
YAML — confirmed `FAIL: middle-tier spec missing` since none of the three
target artifacts exist yet. It checks: the spec file exists and both references
the light-tier spec by name and contains a pattern-variation/pattern-findings
section requiring per-form "evidentiary basis"; a `SUIT-CUPS-12` `.md` file exists
under `research/pilots` that is neither the `STANDARD_` (light) nor `Pilot2_` (full)
file nor a comparison doc; and a comparison note exists that mentions light, middle,
and full tiers together.

**Concern / open question for the human or the eventual PM/worker:** the comparison
doc's own recommendation only ever discusses *two* documented forms per card
(hybrid vs ordinary-rider). D2's decision language is written generally ("any
future case of the same shape"), but nothing in the corpus I read establishes
whether any of the other 15 courts has *more* than two documented forms, or
whether some courts have zero full-dossier backing to lean on at all (SUIT-CUPS-12
is the one court with a full dossier; the other 15 have none). I wrote this into
the task's comparison-note requirement as an explicit question the pilot should
surface rather than silently resolve, since it's exactly the kind of edge case a
single-card pilot can't itself prove doesn't exist.

**Recommended next step:** a PM should audit T-MIN-021 next — it has no
dependencies and doesn't touch any file another open task claims. Once audited, a
Worker producing the spec + pilot + comparison note is the natural next session;
given D2 was decided same-day as T-MIN-013 closed, there's a reasonable chance
the human wants this fast-tracked ahead of other P2/P3 backlog.
