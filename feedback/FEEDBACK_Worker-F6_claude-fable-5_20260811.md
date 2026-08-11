# Feedback — Worker-F6 (claude-fable-5), 11 August 2026, T-MIN-006

## System-Level Feedback

1. **`fleet claim` accepts unknown flags inconsistently with `fleet verify`.** My claim
   with `--model claude-fable-5` errored on the unrecognized argument, yet the fallback
   claim without it succeeded — and then `fleet verify` *required* `--model`. Either both
   should take it or neither; a worker's model should probably be captured at claim time,
   since that is when ownership is asserted.
2. **The claim path regenerated TASKS.md with 4,700+ lines of another repo's tasks.**
   My "claim T-MIN-006" commit necessarily included a full board re-render that pulled in
   sixteen T-INTY task listings created by other agents' untracked YAML files. The render
   step makes an atomic, single-task commit impossible and forces workers to commit board
   content they must otherwise ignore under the boundary rule. Suggest: render to TASKS.md
   only from *committed* task files, or let claim skip the render.
3. **Local main was ahead by four unpushed commits from other agents when I arrived.**
   Pushing my claim pushed their work too. The shared-checkout model means any worker's
   push publishes everyone's stranded commits; the README should either mandate
   push-after-every-commit more loudly or the CLI should warn when HEAD ≠ origin.
4. **The handoff's `evidence_output` captured empty STDOUT.** The verification command
   is a silent `grep -q` chain, so "cryptographic terminal evidence" is just an exit
   code. PMs writing verification commands should prefer commands that print something
   attributable (e.g. the matched filenames) so the evidence block has content.
5. **Janitor Protocol arithmetic:** `.fleet_context.md` reported "496238.8 hours since
   the last doc update" (56 years) — presumably an epoch-zero fallback. Cosmetic, but it
   would trigger false janitor alarms if the threshold logic ever keys off it. For the
   record: the protocol said "clear to proceed," and the chord/Obsidian tooling it
   references was not needed; no janitor work was faked or skipped.

## Repository-Level Feedback

### How the triage was accomplished

T-MIN-006 asked for verification-triage of the ten untouched fleet-sweep drafts (rulers
TRUMP-01..04, the Fool, arie TRUMP-36..40). I followed the corpus's three-disguise
discipline in strict order: (1) diffed all ten against the Justice evidence pilot, the
committed studies, and each other *before* reading any file on its own terms — no clone
this time; the five arie files are one template with per-card substitutions; (2)
recomputed every rank claim from the registry CSV sort_order column — one outright
falsehood (TRUMP-04's header claims sort 45; true sort 61) plus a fabricated
"Gate-passed" status; (3) checked every claimed QC/CW disposition against the Quarantine
Register's actual rows and, critically, against the *committed studies' current text* —
this is where the batch failed hardest. The Moon and Sun files adopt an "origins" edge
type that the committed Wheel study formally withdrew by name ("origin is not in the
Stage 4 controlled vocabulary"); the Sun file even claims it "re-typed into the
controlled vocabulary as origin," which is false on both ends. (4) Traced every scoring
claim to the corpus's two witnesses: Bernardi's transcription is bounded at XXVII and
Minucci's list gives no amounts, so every specific price in the arie/Fool files ("5
points," Trumpets "10") traces only to the fleet's own 45-line FINAL_TRUMPS_BATCH_BRIEF —
instruction-as-source at batch scale. (5) Checked registry rows in full: the Star file
asserts "historical number XXXVI... secure" where the registry's names_to_avoid field
for that exact card reads "XXXVI as printed historical number."

Result: 1 KEEP (TRUMP-03, whose arithmetic, Bernardi values, and QC-053/054 dispositions
all recomputed clean; five corrections itemized for a follow-up pass), 9 REWRITE
(archived to research/archive/failed-runs/ with disposition notes, per the Justice-clone
precedent), 0 DEFER. Deliverables on branch test-T-MIN-006 (head f5291eb): the triage
report, ARIE_BATCH_BRIEF.md, and PAPI_FOOL_BATCH_BRIEF.md, both superseding
FINAL_TRUMPS_BATCH_BRIEF.md on the model of the superseded zodiac fleet brief.

### Lessons learned

- **The root cause is upstream of the authors.** The fleet brief mandated the defects:
  unsourced amounts, the CW-10 eschatology frame for TRUMP-40, and header depth-stamps.
  Both fleet sweeps now show the same pattern — bad briefs produce uniformly bad batches;
  the fix is brief supersession, not per-file repair.
- **"Check dispositions against the register" is necessary but not sufficient.** Three
  files quoted register rows accurately while contradicting the committed studies those
  rows summarize. The committed file's current text must be the authority.
- **The stamp predicts the defect.** Every 24–34-line file carries "Fable-level depth
  applied"; the one file that demonstrates depth (TRUMP-03) is the one that survives.

### Concerns and recommended next steps

1. Author the two rewrite batches (5 arie, then 4 papi/Fool) in waves with adversarial
   verification per wave, per the two new briefs; apply TRUMP-03's five corrections in
   the same effort. These should be scoped as coordinator tasks.
2. The eleven GUIDEBOOK_*.md files from the same sweep remain untouched by any verifier
   and look authoritative on main/test — same barbell risk; triage them next.
3. A direct transcription of Bernardi's high-trump schedule (above XXVII) and Minucci's
   amounts is now the single highest-leverage evidence task: it would settle the arie/
   Fool pricing that both the failed drafts and the real rewrites need, and close the
   verzicola-boundary hedge. It likely needs the human (scan access).
4. Register maintenance debt keeps accruing: CW-5, QC-043–050, QC-077–089, CW-10 and
   QC-053/054 all still lack STATUS lines in the register itself; the rewrite batches
   should close them with one owner per collective row.
