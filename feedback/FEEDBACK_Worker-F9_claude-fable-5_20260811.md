# Feedback — Worker-F9 (claude-fable-5), 2026-08-11

Task: T-MIN-009 (minchiate_tarot) — resolve the twelve zodiac studies' hedged
classical-source locators. Verified PASS, submitted for peer review at head f8bb1b8
on branch test-T-MIN-009.

## System-Level Feedback

1. **`fleet claim` rejects `--owner X --model Y` but `fleet verify` requires `--model`.**
   The asymmetry cost two round-trips. Either accept `--model` at claim time and carry it
   into the handoff, or drop the requirement at verify time (the handoff already records
   the agent name).
2. **The coordinator working tree is a hazard for `git pull --rebase`.** The shared
   checkout carried ~50 uncommitted files from other agents (T-INTY handoffs/archives,
   deleted review files), so a plain `pull --rebase` refuses to run. I used
   `--autostash`, which worked, but the system should either instruct agents to commit
   their own state promptly or document `--autostash` as the sanctioned pattern; a worker
   who reaches for `git stash`/`reset` instead could destroy other agents' pending work.
3. **The audited verification regex is well designed** — it caught both bracketed hedges
   and the §5 checklist phrasing ("locators marked UNVERIFIED"), which forced prose,
   tables, and reviewer checklists to be updated together rather than cosmetically. One
   subtlety worth documenting for future PMs: bare `[UNVERIFIED]` (no interior space)
   deliberately passes, which is exactly what makes honest downgrades expressible. That
   is a feature; a future PM tightening the regex further would break the downgrade path.
4. **`audited_repo_sha` drift.** The task was audited at 274b981 but test HEAD had
   advanced to f5291eb (T-MIN-006). The instruction to diff the advance and confirm no
   overlap with the task's files worked fine manually (`git diff --name-only` showed no
   TRUMP-24..35 files), but the CLI could offer `fleet verify --check-base` to automate
   exactly this confirmation.
5. **Feature request:** a `fleet claim --dry-run` or a machine-readable lane filter, so a
   worker can confirm boundary compliance (minchiate lane only, ignore T-INTY-*) without
   reading the whole rendered TASKS.md.

## Repository-Level Feedback

**How the work was done.** I built the worklist by grepping all twelve studies for
UNVERIFIED (the task summary was accurate but the grep found extra per-file hedges, e.g.
Aries §0's vernal-equinox convention and Cancer's crab-gait gloss). I then opened every
source in a real edition before touching any file: Ptolemy via LacusCurtius/Robbins
(Tetrabiblos I.13 "Of the Aspects of the Signs" — the chapter all six diametrical edges
hedged on — and I.17 for the sun's Leo domicile); Aratus via the Perseus/Scaife passage
API in Greek, which returns per-line references, so every line number cited (Chelae 89 and
545–546, Parthenos/Spica 96–97, Bull 167–174, Fishes/Knot 239–245, Hydrochoos 283 with
the Water at 392–399, Capricorn's solar turn 286, the drawn bow 301/305–306) was read off
the edition itself rather than remembered; Sacrobosco via Thorndike's translation
(cap. II sections "The Zodiac," "The Twelve Signs," "Tropics of Cancer and Capricorn");
Isidore via the LacusCurtius Latin Book III (III.71.23–32 turned out to carry almost the
whole encyclopedic layer: Aries first/March, Gemini as Castor and Pollux, Cancer's
backward walk, Leo's heat, Libra's equinox equality, Capricorn's rain-marking fish-tail,
Aquarius/Pisces ab imbribus); Hyginus De astronomia 2.22 via Topostext for the Dioscuri
star-names. Theoi.com 403'd and was simply not used.

Two claims failed sourcing and were downgraded per the studies' own "[UNVERIFIED] over
invention" rule instead of being forced: the Pisces contrary-swimming rendering (Aratus
says only that one fish is ever more forward) and the Taurus forepart/georgic-gloss
commonplace. Both are recorded as explicit downgrades in the resolution note and in each
file's claims table, with the genuinely-resolved neighbors (the cord/Knot; the bull image)
upgraded alongside.

**Editorial discipline.** Each study's prose citation, claims-table row, §4 open-question
item, and §5 reviewer-checklist line were changed as one unit, and the six opposite-edge
pairs were upgraded symmetrically so offer/reciprocation gradings still match across
files (the batch's reconciliation discipline would otherwise have been silently broken —
e.g. Aries' checklist asserts its grading matches Libra "exactly," so both had to move
together). A header "Locators:" line was added to all twelve files pointing at
`research/pilots/Zodiac_Locator_Resolution_Note.md`, which logs edition, URL, yield, and
per-claim disposition for TRUMP-24 through TRUMP-35.

**Lessons and concerns.** (a) Isidore III.71 is the highest-yield single page for this
deck's zodiac layer; future encyclopedic-gloss hedges should check it first. (b) The
Scaife passage API (`/library/passage/<urn>:<range>/text/`) is the reliable way to get
line-numbered classical text; the reader UI is a JS shell that WebFetch cannot see.
(c) The studies' habit of hedging rather than inventing made this task mechanical in the
good sense — every hedge was findable and each either resolved or downgraded cleanly.
The 208-untraceable-references audit is the counterfactual; the zodiac batch's discipline
should be the template for the remaining families. **Next steps I'd recommend:** run the
same locator-resolution pass over the element and virtue studies (several cite Sacrobosco
and Isidore at chapter level); and consider a small shared bibliography file so studies
cite editions once instead of re-describing them per file.
