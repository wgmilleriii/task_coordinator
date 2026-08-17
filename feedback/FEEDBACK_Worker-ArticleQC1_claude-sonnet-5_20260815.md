# Feedback: Worker-ArticleQC1 (T-PTG-048)

## System-Level Feedback

1. **`./bin/fleet verify` still runs `verification_command` against the
   primary clone, not the worktree.** Third confirmed report of the same
   defect (after `FEEDBACK_WorkerLoginFix1_*` item 1 and
   `FEEDBACK_Worker-ExtractionRepair1_*` item 1). I worked around it
   exactly the same documented way: ran the command by hand inside the
   worktree, confirmed a real pass, hand-authored
   `handoffs/T-PTG-048_handoff.yaml` directly against
   `schemas/handoff.schema.json` (validated with `jsonschema.validate`
   before submitting) rather than trusting a `fleet verify`-generated
   stub. This is now three-for-three on this exact defect across three
   different tasks in this repo lane; I'd bump this from "known issue" to
   "please actually fix it next" — the fix suggested previously (default
   `--repo-path` to `../<repo>-<task_id>` when that worktree exists) still
   looks like the right minimal change.
2. **`fleet submit` silently reformats a hand-authored handoff YAML on
   save** (multi-line block scalars got re-wrapped, folded, and had
   `—` used for an em-dash) — harmless here since the content
   round-tripped correctly and schema-validated both before and after, but
   worth knowing that a hand-authored handoff isn't preserved byte-for-byte
   once submitted, in case a future worker relies on exact formatting for
   something.
3. **Minor:** the task's own scope text says "For the 9 real
   article/editorial/column rows" but the 15-row ground-truth table it
   provides actually contains 10 non-ad/index rows. Not a coordinator bug
   (it's in the task YAML, which was already AUDITED), but worth a heads-up
   for whoever reviews similarly-worded future tasks: when a PM writes a
   task with an inline ground-truth table, it's worth literally counting
   the rows against the prose summary before audit, since a worker has to
   choose whether to follow the letter (9) or the table (10) — I followed
   the table since the task explicitly frames it as the authoritative
   source ("real ground truth... not invented") and documented the
   discrepancy rather than silently picking one.

## Repository-Level Feedback

**What I built:** no new spike code was needed — T-PTG-047's
`extract_pieces.py`/`coverage.py`/`run_pipeline.py` were reused exactly as
directed. What I actually produced is the QC-read report:
`docs/30-Engineering/2026-08-14-article-editorial-completeness-qc-pass.md`
(worktree `../newmexicoptg.org-T-PTG-048`, branch `test-T-PTG-048`, commit
`b23accf8642fcb85afe7525aaa65f0857271c3b3`), plus two committed evidence
files (`journalgpt/spikes/T-PTG-047/output/PTJ-2020-02.{raw,result}.json`)
from the one new extraction call this task made.

**How it went / lessons learned:**

- The prior worker's gitignored-asset workaround (copy `.env`, symlink
  `journalgpt/pdfs/`) worked without modification — worth keeping in the
  fleet README's worktree instructions as suggested previously, since I'd
  have hit the exact same "why is the extraction failing, oh right no
  PDFs/no key" confusion without that documented precedent.
- **The most important finding, and it's a genuinely uncomfortable one:**
  this task's whole premise — that `coverage.py` reporting zero
  gaps/overlaps doesn't mean content is complete — turned out to be even
  more true than the task's framing implied. I found the failure mode
  doesn't just theoretically exist; it's the dominant, structurally
  invisible failure across every single issue I checked (1 primary + 3
  secondary, 4/4). The mechanism is consistent: a short front-matter
  column (President's Message, TT&T, board message, The Piano Corner)
  either becomes a fully unclaimed gap page (visible to `coverage.py`) or
  gets silently swallowed because its *neighbor's* claimed `start_page` is
  wrong by 8-10 pages (invisible to `coverage.py` — looks like clean
  coverage). I only found the second variant by actually reading page
  text at the anchors in question and cross-checking against each issue's
  own masthead/TOC pages, exactly as the task demanded — a pure
  page-number diff genuinely cannot see it, which is the whole point of
  this task existing.
- Independently of the short-column problem, I also found a full-length
  feature article (Reweighing the Original Keyboard, Part 2, in
  PTJ-2020-02) truncated to 1 of its real 6 pages, with title/author/start
  page all correct — meaning even a piece that looks perfectly identified
  by every structural signal can still be badly incomplete. This wasn't
  something the task specifically asked me to hunt for beyond "read and
  confirm complete/uncut," but it fell directly out of doing that read
  honestly rather than skimming.
- PTJ-2020-02's raw extraction this run was unusually degenerate — every
  piece came back as a single-page `start_page == end_page`, unlike the
  8-issue spike sample's multi-page ranges. I flagged this explicitly in
  the report rather than let it blend into the diff table silently, since
  it's a different (and in some ways more informative) failure signature
  than the original spike's gap/overlap pattern, and someone comparing raw
  `coverage.py` numbers between this run and the 8-issue baseline table
  without that context would be misled.
- Cost: one new gpt-4o-mini call for PTJ-2020-02 (35,391 prompt + 923
  completion tokens, ≈$0.006). All three secondary-issue checks reused
  already-cached `output/*.raw.json` from the T-PTG-047 merge — zero
  additional spend for those, so the generalization check came essentially
  free once the primary case was run.

**Recommendation for next steps (also in the report):** do not proceed to
piece-level schema/database design on the strength of either T-PTG-047's
coverage checking or this task's single-issue-plus-3-secondary sample
alone — both failure modes found here (short-column drop/absorption,
independent full-article truncation) are invisible to every purely
structural check built so far. Two concrete, cheap next steps proposed in
the report: (1) a structural heuristic flagging any piece with a
suspiciously short claimed range immediately next to a suspiciously wide
one, since that pattern is exactly what every absorption case I found
looks like; (2) a lightweight TOC-title cross-reference pass, since every
issue's own TOC already lists every short department item by name and a
fuzzy title match against extracted pieces would catch the pure-drop
cases directly. Both are far cheaper than continuing to scale up manual
text-read QC passes, though the manual method used here (or an
LLM-as-judge version of it) remains the only thing that actually caught
these errors and is worth keeping as a spot-check even after those
heuristics exist.
