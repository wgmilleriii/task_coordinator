# Feedback — PM-F5 (claude-fable-5) — 2026-08-11

Session: PM audit of T-MIN-011 / T-MIN-012 / T-MIN-013 (minchiate_tarot lane only,
per the boundary rule). All three unlocked to AUDITED against branch `test` @ f8bb1b8.

## System-Level Feedback

1. `./bin/fleet lint` exited 0 this session — the thirteen T-INTY schema violations
   PM-F3 reported earlier today are gone from active/. However, the working tree
   still carries a large population of OTHER agents' uncommitted state: deletions of
   `tasks/active/T-MIN-005.yaml`, `T-MIN-010.yaml`, and four `reviews/T-MIN-*.yaml`
   files, plus untracked T-INTY handoffs/reviews/tasks. I committed only my three
   yamls, TASKS.md, and this file. The coordinator would benefit from agents
   committing their own archive moves atomically — an uncommitted archive move means
   `fleet render` output depends on whose working tree you happen to be in.
2. The audit CLI round-trips a long single-quoted `bash -c` command correctly into
   YAML (verified after write). Same request as PM-F3: lint should flag
   verification commands that cannot exit non-zero. Scout-F2's suggested commands
   for T-MIN-011/012 were `ls`-based (red today, but green the moment files exist
   regardless of content) and T-MIN-013's was a bare `test -f && grep -qi` that
   would pass on a one-line stub. Fail-first is necessary but not sufficient;
   commands must also test content, not just existence.
3. Scout-F2's feedback asked for OPEN tasks to render their suggested
   verification_command on the board — seconded; I had to open all three yamls to
   see what I was replacing.
4. The onboarding janitor line still reports "496239.8 hours since the last doc
   update" — the epoch-default artifact both prior PMs flagged. Still cosmetic,
   still unfixed.

## Repository-Level Feedback

How the audits were done — every premise was verified against the spoke repo on
branch `test` @ f8bb1b8 (no branch switch), not taken from the task text:

- T-MIN-011: `research/pilots/ARIE_BATCH_BRIEF.md` exists and carries all three
  binding traps the scope cites — the no-amounts pricing rule (two witnesses,
  Bernardi bounded at XXVII, Minucci exemplary list, brief L74-82), the CW-10
  summons/eschatology §0 disposition duty and QC-077..089 row assignments
  (L42-63, one-owner rule L105-106), and the unnumbered-arie discipline (L24-29).
  All five archived fleet drafts (TRUMP-36..40 `_FLEET-STUB_archived-2026-08-11`)
  are in `research/archive/failed-runs/` and none exist as PERSONALITY_ files in
  `drafts/` (the GUIDEBOOK_TRUMP-36..40 files in drafts/ are the older guidebook
  series, not the failed personality drafts).
- T-MIN-012: `PAPI_FOOL_BATCH_BRIEF.md` exists; `PERSONALITY_TRUMP-03_Ruler.md`
  is present in drafts/ as the KEEP (currently 102 lines, cites
  FINAL_TRUMPS_BATCH_BRIEF twice — both facts my verification command exploits).
  The five itemized corrections exist in
  `Fleet_Sweep_Personality_Triage_Report.md` under "### TRUMP-03 Ruler — KEEP",
  subsection "Corrections the follow-up pass must apply" (items 1-5, ~L161-173),
  and match the task scope one-for-one. Quarantine Register rows QC-043..050
  (L469-494) and CW-5 (L893) verified present.
- T-MIN-013: both full dossiers exist (`Pilot1_SUIT-COINS-04_Four_of_Coins.md`,
  `Pilot2_SUIT-CUPS-12_Cavalier_of_Cups.md`, plus their .json twins);
  `teamwork/VENTURE_BRIEF.md` §2 row 7 carries the light-tier decision (LEANING);
  the Stage5 registry JSON has exactly 56 SUIT-* cards, zero missing `sort_order`,
  and each suit occupies a contiguous 14-slot block (Swords 1-14, Batons 15-28,
  Cups 29-42, Coins 43-56), so rank-in-suit arithmetic is computable. Spot checks:
  SUIT-COINS-04 sort 46, SUIT-CUPS-12 sort 40.

Verification commands: all three were replaced with fail-first `bash -c` scripts
that (a) fail today — dry-run confirmed red on the current tree before auditing —
and (b) were green/degrade-tested against scratchpad mocks of the done state. The
two batch tasks use the T-MIN-005 grep-count pattern: the verification report must
exist AND name every card in the batch (`sort -u | wc -l` = 5) AND reference
`failed-runs` (the diff-against-archive record). T-MIN-012 additionally checks the
KEEP file mechanically (brief-as-source citation gone, ≥210 lines) and greps the
fresh files for the invented titles "Papa Due"/"Papo". T-MIN-013 requires the spec
(with UNVERIFIED grading and a claims section), both light-tier pilots (found by
card id, excluding the Pilot1_/Pilot2_ full dossiers), and a comparison doc naming
both full dossiers.

requires_doc_update: not set on any of the three — all are content-authoring or
format-proposal tasks inside research/pilots/; no architecture changes.

Concerns / next steps for the human:

- Scout-F2's cross-reference warning stands: T-MIN-011 and T-MIN-012 are now BOTH
  audited, so whichever worker claims second should check whether the sibling
  batch has landed — arie<->Papi edges must stay offered-not-imposed either way.
- T-MIN-008 (verzicola boundary) is still on the board unaudited; both batches
  will carry the pilot-L92 hedge until it lands. Auditing it next would let the
  batches cite a transcription instead.
- The mechanical TRUMP-03 checks (line count, citation string) are proxies; the
  reviewer at PEER_REVIEW should still verify corrections 2-4 (Papi-membership
  wobble, Minucci record, [F]->[SI] regrade) substantively — they are not
  greppable without false positives.
- T-MIN-013 keeps human_review_required: true, correctly — the tier trade-off is
  a product decision. Do not let a worker roll the format out to the other 54
  cards on the back of this task.
