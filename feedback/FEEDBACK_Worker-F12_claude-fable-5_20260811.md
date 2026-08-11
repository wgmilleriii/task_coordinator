# Feedback — Worker-F12 (claude-fable-5), 2026-08-11

Task: T-MIN-012 (minchiate_tarot) — the Papi/Fool batch: fresh personality studies for
TRUMP-01/02/04 and the Fool, plus the five itemized corrections to the KEEP file
PERSONALITY_TRUMP-03_Ruler.md. Verified PASS and submitted for peer review at head
103061a on branch test-T-MIN-012 (base f8bb1b8).

## System-Level Feedback

1. **The claim/verify `--model` asymmetry is still there.** Worker-F9's feedback already
   reported it; nothing changed. `fleet claim` takes only `--owner`, `fleet verify` requires
   `--model`. Either accept the model at claim time or read it from the environment — the
   current shape guarantees every worker hits it once.
2. **The audited verification command was excellent adversarial design.** The tripwires were
   the *specific convicted strings* of the failed batch ("Papa Due", `\bPapo\b`) rather than
   generic patterns, which meant the check could not be satisfied by style. One consequence
   worth documenting as intended: because the tripwire greps the fresh files for the literal
   strings, a study cannot even *quote* the archived draft's invented title to overturn it —
   I described the fabrications ("an invented two-letter Italian title") instead of quoting
   them. That is a reasonable price, but a future PM writing a similar command should decide
   consciously whether quotation-to-overturn should pass, and if so use a negated context
   pattern instead of a bare grep.
3. **Shared-checkout branch juggling is the system's most fragile spot.** The coordinator
   checkout sat on another agent's branch when I arrived and carried other agents'
   uncommitted state; the minchiate checkout is shared with a concurrent reviewer's
   worktree. The discipline (show-current before every commit; restore afterward) works but
   is pure convention. A `fleet` subcommand that wraps "commit these paths to coordinator
   main and restore prior state" would remove the most error-prone manual sequence, and
   between my first two commands the coordinator's branch changed under me (another agent
   checked out main mid-session) — evidence this is a live race, not a theoretical one.
4. **Feature request: task-scoped file claims.** T-MIN-011 (arie) and T-MIN-012 (papi/fool)
   ran in parallel against sibling files in the same directory. It worked because both briefs
   mandated deferral notes, but the coordinator has no mechanism to declare "these paths
   belong to task X until it lands"; a lightweight paths field in the task YAML that `fleet
   claim` checks for overlap would catch collisions before they cost a batch.

## Repository-Level Feedback

**How the work was done.** I read the brief, the triage report (the archived drafts'
convictions are effectively the task's negative spec), the two rule-witness anchors in the
Justice pilot (JUS-C005/C006 at its claim register, the verzicola qualification at its line
92), the committed Death study's Minucci record (DEA-C004), the Quarantine Register rows
(QC-043–054, CW-5), the registry rows and skeletons for all five cards, and — decisively —
the *current* §3 text of every committed study holding a Fool or Ruler record (Love, Wheel,
Chariot, Old Man, Hanged, Death, Devil, House, Justice, Fire). Then two waves: wave 1 =
TRUMP-03 corrections in place + TRUMP-01/02 fresh; wave 2 = TRUMP-04 + Fool fresh; a written
adversarial pass after each wave; consolidated in
`research/pilots/Papi_Fool_Batch_Verification_Report.md`.

**The batch's two structural decisions.** (a) For the Rulers, the "Papi membership" question
was resolved by refusing to resolve it: the four witness usages (Stage 2 glossary I–V;
Bernardi's 3-point tier II–V; verzicola examples I–V; numbered-Papi naming through XII) are
stated as usage facts in every file, consolidated once as RUL3-C009, with no canonical block
asserted — the failed drafts' shifting "1-4 / 1-5 / 2-5" assertions were the target defect.
(b) For the Fool, CW-5 was dispositioned by *splitting* the inherited identity: structural
placelessness (unnumbered, outside the 40-trump ladder, Minucci-valued in kind) is
substantiated and kept; mechanical immunity (cannot be captured, excuses from suit, "worth 5
points") is unsourced and refused. All eight QC rows were then ruled individually against
each committed file's current text — which mattered, because the register summary of QC-052
had already drifted from the committed Love file's wording ("worth having" vs "worth more"),
and the committed Devil file had already corrected its own register heading (QC-049).
The register is a map, not the territory; future dispositions should always open the file.

**Lessons.** (1) The committed corpus quietly self-corrects (Devil's second pass, Wheel's
"bookkeeping" flag), so reciprocation done from register summaries would re-introduce errors
the corpus already fixed. (2) The line-count standard is partly a wrapping convention —
committed studies hard-wrap at ~98 chars; content written at paragraph-width reads as half
its committed length. I wrapped to match, which is honest only because the content was
extended first (TRUMP-03 grew from 7 to 11 claims, 2 to 5 open questions, 3 to 8 checks).
(3) Writing four sibling files in one session invites template drift; I varied §0/§2
structure per card (register-confrontation shape for the Rulers, the CW-5 split for the
Fool) and flagged the deliberately-shared witness anchors in each header for the verifier.

**Concerns and next steps.** The batch leans entirely on two transcribed witnesses reached
through the Justice pilot; every §5 queues the direct RULE-1790 scan check, and nobody has
yet opened Bernardi beyond the pilot's pages, Dresden 1798, or Brunetti 1747 at the Matto's
rules — that single fetch (Fool §4, question 1) would upgrade or falsify the whole CW-5
settlement and is the highest-value next task. Second: register maintenance is now genuinely
due — QC-043–054 all have batch dispositions and QC-049's heading is stale; a small task
should add the disposition lines on acceptance. Third: the arie batch (T-MIN-011) and this
one deferred all cross-edges to each other symmetrically; once both land, a short
reconciliation pass should decide the Fool/Trumpets and low-block/arie questions from
committed text on both sides.
