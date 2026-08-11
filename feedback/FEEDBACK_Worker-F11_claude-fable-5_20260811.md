# Feedback — Worker-F11 (claude-fable-5), 11 August 2026, T-MIN-011

## System-Level Feedback

1. **The audited verification command's glob is well-designed but worth documenting as a
   pattern.** `ls research/pilots/*[Aa]rie*erification*.md` cannot accidentally match
   `ARIE_BATCH_BRIEF.md` (no "erification" substring), and the five-token grep plus the
   "failed-runs" grep make the report's two hardest-to-fake properties (per-card coverage,
   archive-diff evidence) mechanically checkable. Future PMs writing report-shaped DoDs
   should copy this trio: filename glob + coverage token count + required-evidence keyword.
2. **`fleet claim` regenerated TASKS.md with other tasks' state churn in my working
   tree** (deleted review files and task YAMLs from concurrently archived tasks showed as
   unstaged deletions). I staged only my own files, but a worker less careful with
   `git add -A` would have committed another agent's archive operation. Suggest `fleet
   claim`/`submit` either commit their own render or print an explicit "stage only these
   files" list.
3. **`fleet verify` writes the handoff stub with `REQUIRED_PLEASE_FILL` — good — but
   nothing validates that head_sha exists on the named branch.** `fleet submit` accepted
   the sha without checking it against the spoke repo. A `git cat-file -e` in the target
   repo would close a fabrication loophole.
4. **Wave-commit discipline interacts oddly with cross-wave fixes.** My wave-2 adversarial
   pass caught a defect in a wave-1 file (ordinal-convention mismatch) after wave 1 was
   already committed. I fixed it before the wave-2 commit and recorded the finding in the
   batch report (F-1), which I think is the right pattern; the coordinator docs could
   bless it explicitly: fixes discovered by later-wave passes go in the later wave's
   commit with the finding named in the report, never squashed backward.
5. **Feature request:** the onboarding janitor check printed "496239.9 hours since the
   last doc update" — a cosmetic bug (epoch fallback) that makes the threshold logic
   unreadable. Harmless this run, but it would mask a real janitor trigger.

## Repository-Level Feedback

**How the work was accomplished.** The five arie studies were written to
`ARIE_BATCH_BRIEF.md` in two waves (Star/Moon/Sun, then World/Trumpets), each wave
followed by an adversarial self-pass recorded in
`research/pilots/Arie_Batch_Verification_Report.md`. Before writing a line I read the
brief, the virtue brief it incorporates, the zodiac batch's two best format models
(Libra, Gemini — verified and locator-resolved), the three verification reports, the
triage report's X-1..X-7 defect list, all seventeen register rows plus CW-10, the five
registry rows, the Stage 3 workbook rows (openpyxl), and the five archived failed drafts.
The brief's hard rules turned out to be exactly the right guardrails: every trap it named
(pricing amounts, printed numerals, the summons frame, collective-row double-disposition,
withdrawn "origins" coinage) is a thing the archived drafts actually did.

Key decisions worth recording:

- **Scoring.** The zodiac's nil-reading formula does not transfer to the arie: sorts
  93–97 are *outside* Bernardi's transcription (bounded at XXVII), not inside it
  unpriced. All five files therefore say "no tier reading available in either direction"
  rather than "unpriced," and carry Minucci's in-kind special value (the five arie named
  outright as a group, no amounts) as the positive fact. This distinction is, I think,
  the single most important thing a future verifier should re-check.
- **Doctrine was fetched, not remembered.** Luminary contrariety (Tetrabiblos I.4, I.7),
  Isidore's borrowed-light report (III.53) and stella/sidus/astrum (III.60), and
  Sacrobosco's machina mundi (cap. I) were all opened in the same editions T-MIN-009
  logged, so the batch inherits the zodiac batch's edition base. The Moon file labels
  Isidore III.53 as *reported* doctrine (Isidore records competing views) — a nuance the
  fetch surfaced that memory would have flattened.
- **TRUMP-40.** The territory ("precedence that does not explain itself") is built
  entirely from secure facts: highest sort, the family's only Moderate naming, and
  SYM-TRUMPET being the only arie symbol row with direct catalog evidence (BM
  P_1896-0501-34). The three committed transformation pairings are reciprocated in the
  committed form — pairing confirmed, higher card uncharacterized — and the World↔Trumpets
  pair is typed companion with the transformation type declined on the record on both
  sides, because the archived draft's "totality gives way to cessation" typing was the
  CW-10 structure wearing a legal type.
- **GEM-C016** (the one committed offer awaiting an answer) is accepted and retyped
  predecessor on the Air/Libra model, closing the asymmetry the Gemini file recorded.

**Lessons learned.** (a) The committed corpus's second-pass withdrawal notes are the real
authority map — reading the register alone would have led me to "resolve" rows the
committed studies deliberately left as untyped structural notes. (b) A within-batch
convention (ascending vs descending family ordinals) can be internally consistent per
file and still wrong across files; only a cross-file sweep catches it. (c) The archive
diff is cheap (`comm -12` on sorted lines) and should be standard for every
rewrite-over-archived-failure task.

**Concerns / next steps for the human.** (1) The register itself still carries no STATUS
lines for QC-077..089, QC-107, CW-10 — the batch report's §5 queues the exact claim IDs;
a small register-maintenance task should close them on acceptance. (2) The high-trump
scoring schedule (Bernardi beyond XXVII; Minucci amounts) is now the corpus's most
valuable single gap — five files queue the same §5 item; a source task against the
naibi.net Minucci transcription and a full RULE-1790 scan would resolve ten hedges at
once. (3) The Fool/papi batch (parallel brief) should answer the Trumpets file's queued
Fool↔XL question and the Star file's clean field. (4) An independent verifier pass over
this batch is still owed: my report is a self-pass by design and says so.
