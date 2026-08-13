---
title: "PM-F9 Session Feedback — T-MIN-019 / T-MIN-020 Audit"
created_at: "2026-08-12T21:00:00-06:00"
last_modified: "2026-08-12T21:00:00-06:00"
author: "PM-F9"
status: "active"
category: "00-Meta"
---

# Feedback: PM-F9 (claude-sonnet-5), 2026-08-12

## Scope of session

Audited two OPEN tasks in the `minchiate_tarot` lane: T-MIN-019 (apply the Bernardi
verzicola hedge-phrase reconciliation queue produced by T-MIN-018) and T-MIN-020 (fix
a `grep -A20` verification-window fragility on SPECIAL-FOOL's `aliases` field in the
Stage5 master registry JSON, mirroring the T-MIN-017 precedent). Both were checked
out on branch `test` at `d0052dc` (matching the sha both tasks' scouting was performed
against) and both were unlocked to `AUDITED`.

## System-Level Feedback (task_coordinator itself)

1. **No built-in cross-check between a task's claimed occurrence/file counts and its
   own file list.** T-MIN-019's `definition_of_done` asserted "16 occurrences across
   11 files" while its own scope bullet 3 enumerated 12 distinct files. Nothing in
   `fleet lint` or the schema catches an arithmetic mismatch inside free-text YAML
   fields — it's structurally valid YAML/schema, just internally inconsistent. A PM
   has to manually recount. Worth considering a lightweight lint rule (or at least a
   scout-side self-check) that greps a task's own scope text for stated counts vs.
   enumerated list length before it's ever handed to a PM.
2. **`fleet audit --command` with a multi-line Python one-liner is fragile to shell
   quoting.** I had to round-trip the stored `verification_command` through a YAML
   parser to a temp file and re-inject it via `$(cat ...)` rather than retyping it, to
   avoid a transcription error changing the actual audited command from what I'd
   dry-run tested. This worked, but it's not obvious a less careful agent would do the
   same — an `audit --command-file <path>` flag would remove the retype-risk entirely
   and make "the command I tested is byte-identical to the command that got audited"
   a structural guarantee instead of an agent discipline.
3. Otherwise the audit workflow (onboard → read scope → dry-run verification_command
   against current branch state → `fleet audit` → `fleet lint` → `fleet render`) was
   smooth and the CLI's error messages (e.g. the pre-existing `T-INTY-017.yaml` schema
   error on `dod`, which is out of my lane and untouched) were clear enough to
   confidently ignore what wasn't mine.

## Repository-Level Feedback (minchiate_tarot)

**T-MIN-019 audit.** SCOUT-F5's work here was careful and I could not find an actual
scouting error, only a counting slip. I independently:
- Read the full T-MIN-018 resolution note (`Bernardi_1790_Verzicola_Boundary_Resolution_Note.md`)
  §§4–6, including its own reconciliation queue, to understand what was actually
  resolved (verzicola upper boundary = exactly XXVIII) vs. what remains genuinely open
  (§4(B), whether XX–XXIII itself can form a verzicola — "covered by the general rule,
  unconfirmed by named example," explicitly not to be flattened to "resolved").
- Spot-checked 9 of the 12 claimed-present files (Justice, ARIE_BATCH_BRIEF,
  ELEMENT_BATCH_BRIEF, Element_Batch_Verification_Report, Arie_Batch_Verification_Report,
  Fire, Water, Earth, plus reading the resolution note itself) directly at the cited
  line numbers and confirmed the Hedge-A phrasing is exactly where claimed. I also
  checked all 8 files SCOUT-F5 excluded as no-longer-matching and confirmed zero
  Hedge-A hits in every one (`grep -n -iE "around XXVIII|about XXVIII|~XXVIII"` came
  back empty for all 8). I confirmed ARIE_BATCH_BRIEF L76 and Arie_Batch_Verification_Report
  L57/L68–69 are genuinely Hedge B ("transcription bounded at XXVII" — a different,
  out-of-scope claim about Cap. III's point-value schedule), so the scout's line-level
  exclusions within otherwise-included files are correct too, not just its file-level
  exclusions.
- **Found and corrected a real miscount**: the scope's own file-by-file list (bullet 3)
  names 12 files, not 11. Running the audited verification_command directly against
  current `test` content confirms 16 occurrences land across exactly those 12 files
  (8 files with 1 hit, 4 files — Zodiac_Batch_Verification_Report, Fire, Water, Earth —
  with 2 hits each = 16). "16/11" was wrong; "16/12" is correct. I added a PM-CORRECTION
  bullet to `definition_of_done` rather than silently editing the miscounted line, so
  the audit trail shows what was caught and why.
- Verified the Justice-pilot judgment call (update L92's live paraphrase; leave L525's
  JSON `note` field alone as Hedge B) against the actual T-MIN-016 precedent by reading
  the real diff at commit `02092c3` myself (not just SCOUT-F5's characterization of it).
  The precedent holds up exactly as characterized: that commit updated live prose
  asserting the *current* registry state (`sort_order 57` → `sort_order 0`) while
  explicitly leaving alone (a) a line quoting another unrevised file's own text and
  (b) a line citing a historical Stage-2 snapshot — both "accurate descriptions of
  other out-of-scope sources," not live claims resting on the corrected fact. Justice
  L92 is a live descriptive paraphrase of Bernardi analogous to case (a)'s counterpart
  in the SPECIAL-FOOL diff (the corrected live prose), not to either preserved line.
  The judgment call is sound.
- Confirmed the claims-table + prose sync finding for real: Fire (prose ~L363–364 +
  FIR-C021 table row), Earth (prose ~L345–347 + EAR-C020 table row), and Water (prose
  L21 + an open-questions list item at L69–70, though Water has no dedicated
  claims-table row for this hedge) all genuinely carry the hedge phrase in two places.
  This is the exact class of defect (`fix one location, miss its paired location`)
  this project has been bitten by before per the README's implicit lesson from prior
  sessions — good that the scout flagged it explicitly in scope rather than leaving it
  implicit.
- Dry-ran the verification_command against current `test` @ `d0052dc`: it correctly
  fails now (`TOTAL 16`, exit 1) and is structured so it can only report `TOTAL 0` /
  exit 0 once every one of the 16 occurrences across all 12 files is gone — a worker
  fixing 15/16 still fails the gate. I left it otherwise as-authored since it already
  satisfies "genuinely fail-first, all-or-nothing." One limitation worth flagging to
  whoever reviews the worker's submission: the command only checks that the *old*
  hedge phrasing is gone, not that a citation to the resolution note was actually
  *added* in its place, nor that Hedge-B text or the §4(B) framing survived unchanged.
  Those are enforced by `definition_of_done` prose and should be checked by a human/
  reviewer reading the diff, not solely by the automated gate.
- `requires_doc_update`: left `false`. This is a citation-precision content fix, not
  an architectural change — no new system, schema, or process is introduced.

**T-MIN-020 audit.** Confirmed the fragility is real against current `test` content:
`grep -n -A20 '"card_id": "SPECIAL-FOOL"' ... | grep -c aliases` returns `0`;
`-A30` finds it 26 lines in (SPECIAL-FOOL's `aliases` key is currently the very last
key in its object, after `notes`). Read the actual T-MIN-017 precedent diff
(`a113400`) and confirmed the proposed fix — move `aliases` to sit immediately after
`historical_names`, before `names_to_avoid` — is a pure key-order change identical in
shape and target position to what T-MIN-017 already did for the four cavalier rows.
Dry-ran the two-part verification_command (JSON-parser assertion on key order +
value integrity, plus the literal `grep -A20 | grep aliases` regression check) against
current content: both parts fail now as expected (`AssertionError: aliases not
immediately after historical_names`, then `FAIL_aliases_still_outside_A20_window`),
and both are structured to only pass once the fix is applied. No corrections needed
here — SCOUT-F5's scouting was accurate and narrowly scoped (SPECIAL-FOOL object
only; CSV, other rows, and other dossier files explicitly excluded and I found no
reason to widen or narrow that further). `requires_doc_update` left `false` — pure
key-order bugfix, no architectural change.

**Recommended next step for the human:** both tasks are `AUDITED` and ready for a
Worker to claim. T-MIN-018's still-`OPEN`/unaudited status (referenced throughout the
resolution note as "not archived or deleted, that decision is left to a PM/human") is
outside this session's scope but worth a human decision at some point — the note it
produced has now spawned two downstream tasks (T-MIN-019 here, plus whatever consumes
its §4(B) open question) while the originating task itself sits unaudited in the
board.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
