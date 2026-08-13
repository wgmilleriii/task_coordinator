# Feedback — Worker-F21 (claude-sonnet-5) — 2026-08-12

Task: T-MIN-019 — Apply the Bernardi verzicola boundary reconciliation queue (hedge-phrase
citation fix only), repo `minchiate_tarot`. Submitted for PEER_REVIEW at head_sha
`7e2c71cc16323956f88107b5a6bd99c1b3fd3d27` on branch `test-T-MIN-019` (base `d0052dc`).

## System-Level Feedback

1. **Claim/audit YAML is large and mixes two audiences.** T-MIN-019's `scope` and
   `definition_of_done` blocks are effectively a full incident report (SCOUT-F5's findings,
   PM-F9's correction, a worked judgment call with cited precedent commits). This is exactly
   the right level of rigor for a citation-precision task with real landmines (Hedge-A vs.
   Hedge-B, false-positive line locators), and it worked — I did not need to re-derive any of
   that reasoning myself, I just had to verify it against the current checkout. But it means
   the YAML is ~250 lines for a 16-line diff. Worth considering a convention where long
   PM/Scout reasoning lives in a linked doc and the YAML keeps only the operative queue +
   the verification command, if this pattern recurs at this size again.
2. **`fleet verify` ran the audited command against my dirty-branch checkout without
   complaint about branch mismatch** — I never had to tell it which branch I was on; it just
   inspected the working tree in `minchiate_tarot`. That's the correct behavior and worth
   noting as working as designed (no defect, just confirming the mechanism).
3. **No loopholes hit.** Claim → verify → submit was a clean single pass; verification
   passed on the first attempt after the fix (`TOTAL 0`) because I ran the exact audited
   command locally before calling `fleet verify`, which I'd recommend as standard practice
   for any citation/regex-style verification command — cheap to self-check before spending a
   `fleet verify` invocation.

## Repository-Level Feedback

**What I found and how I worked it.** The resolution note
(`research/pilots/Bernardi_1790_Verzicola_Boundary_Resolution_Note.md`, T-MIN-018) is
thorough and its §5 reconciliation queue is the right source of truth, but it is a superset —
it lists file/line locators from a broader sweep than T-MIN-019 actually scopes. SCOUT-F5's
dry run (scope bullet 3) and PM-F9's file-count correction (definition_of_done bullet 1)
narrowed that queue down to the 12 files / 16 occurrences that are both (a) currently
present in the test-branch content and (b) covered by this task's audited verification
command. I re-verified that narrowing myself with a fresh `grep -rniE
'(around|about|~)\s*XXVIII' research/pilots/` before touching anything, and it confirmed the
12-file, 16-occurrence count exactly.

**Important finding for a human/PM to see:** that same grep also turned up roughly two dozen
*additional* occurrences of the identical Hedge-A phrasing in files that are **not** in this
task's scope or its verification command — full zodiac and virtue personality drafts
(`PERSONALITY_TRUMP-08_Justice.md` [draft, distinct from the pilot], -16 through -19, -24
through -40 covering Prudence, Hope, Faith, Charity, Libra, Scorpio, Sagittarius, Capricorn,
Aquarius, Pisces, Aries, Taurus, Gemini, Cancer, Leo, Virgo, Star, Moon, Sun, World,
Trumpets, Wheel of Fortune). I did **not** touch any of these — they are out of scope for
T-MIN-019 per its explicit file list, and the task's own discipline says to flag rather than
resolve anything outside the enumerated scope. But they are real, textually identical hedge
occurrences citing the same now-superseded Justice-pilot L92 language, so a follow-up task
(T-MIN-020 or similar) scoped specifically to that larger set would close the loop the
resolution note actually opened. I'd flag this to a PM before assuming T-MIN-019 fully
"fixes" the corpus's verzicola hedge — it fixes the 12-file queue this task was audited
against, which is a meaningful but partial subset.

**Execution notes:**
- Fire (`FIR-C021`), Water (both its prose sentence and its numbered open-question item),
  and Earth (`EAR-C020`) each had their hedge fixed in both the prose location and the
  claims-table/numbered-item location in the same commit, per the dual-location requirement.
- Justice pilot L92 was updated narrowly to just the hedge clause plus citation, leaving the
  "does not claim VIII can never occur..." sentence, JUS-C005/C006/C015, and the `citeturn1view0`
  marker untouched, per the PM-confirmed judgment call in the yaml.
- JSON line ~525 (`JUS-C006`'s `source_links[0].note`, the Hedge-B point-value-schedule text)
  and the `qualifications` field were confirmed as false positives in the resolution note's
  queue and left untouched, as instructed.
- All 12 diffs are single-clause edits (quoted-phrase text + an inline citation to the
  resolution note); no claim, grading, confidence label, or conclusion was altered anywhere.
  `git diff --stat` confirms exactly 12 files / 18 insertions / 17 deletions for the whole
  task.

**Recommended next step:** scope a follow-up task against the ~24 additional
`PERSONALITY_TRUMP-*` files identified above if the project wants the corpus fully
reconciled to the T-MIN-018 boundary fact, using this task's same Hedge-A/Hedge-B
discipline and dual-location (prose + claims-table) check.
