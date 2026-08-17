# Feedback: Worker-CSVPilot1 (Claude Sonnet 5) — T-PTG-050 — 2026-08-16

## System-Level Feedback

1. **`fleet verify` running against the primary clone is a repeat issue,
   now confirmed a third time** (previously documented by
   Worker-ExtractionRepair1 for T-PTG-047 and by another worker for
   T-PTG-048/other tasks). For any task whose deliverable is new files
   that only exist on an isolated worktree's branch, `./bin/fleet verify`
   will always false-FAIL because it runs `verification_command` in
   `../<repo>` rather than `../<repo>-<TASK-ID>`. This is now a
   well-enough-established pattern across at least 3 tasks in this repo's
   lane that it's worth fixing in `bin/fleet.py` itself rather than
   continuing to route around it by hand each time — e.g. have `fleet
   verify` accept an optional `--cwd` / auto-detect a
   `../<repo>-<TASK-ID>` worktree matching the task's branch and prefer
   it over the primary clone when one exists.
2. **Cross-task ground-truth dependencies on unmerged branches work, but
   are fragile.** This task depended on T-PTG-048's ground-truth table,
   which was still unmerged (PEER_REVIEW) at claim time and remained so
   throughout. I referenced `../newmexicoptg.org-T-PTG-048` directly per
   the task's own instructions, which worked fine, but it means this
   task's correctness is contingent on that worktree still existing and
   still containing the same content when a human/reviewer re-checks it
   later. Worth a coordinator-level convention: when task B's audit
   explicitly quotes ground truth "in full" from task A's still-unmerged
   report (as this task's YAML did, wisely, by inlining the whole 15-row
   table into the scope text), that's the right defensive pattern —
   ground-truth text should be duplicated into the dependent task's own
   audited scope, not just pointed at by reference, exactly as this
   task's audit already did. Recommend making that a required PM
   practice going forward for any task depending on another PEER_REVIEW
   task's findings.
3. **`fleet submit` silently reflows the hand-authored YAML's long
   strings** (line-wrapping `evidence_output`/`peer_review_notes`/
   `human_action_required` on submit) — harmless (content unchanged,
   re-validated after submit) but worth knowing if a worker is tempted to
   diff the handoff file after submit and gets confused by the reflow
   looking like a content change.

## Repository-Level Feedback

**How the task was accomplished:** T-PTG-050 tested whether a
human-curated Airtable CSV export of article title/author/printed-page
(4130 rows, `journalgpt/pdfs/CompleteList-Sortable-Grid view.csv`) could
replace LLM boundary inference for per-article extraction. Built
`journalgpt/spikes/T-PTG-050/pilot_extract.py`, which parses the CSV
(handling the BOM, blank separator row, and empty-title rows), reuses
(imports directly, does not reimplement) T-PTG-047's
`extract_footer_offsets()`/`derive_front_matter_offset()` for per-issue
offset derivation, converts printed pages to real anchor pages, orders
articles, and slices `journalgpt/corpus/extracted/<issue>/*.txt` between
consecutive anchor starts. Ran against 6 pilot issues (PTJ-2020-02,
PTJ-2024-01, PTJ-2025-03, PTJ-2025-10 mandatory; PTJ-2019-08 and
PTG-2022-10 chosen for size diversity and to exercise the PTG-naming
edge case), producing 44 per-article `.md` files under
`journalgpt/corpus/articles_pilot/<issue>/`.

**Key finding, and the biggest surprise of the session:** the CSV-driven
approach is a genuine, evidenced improvement over LLM boundary inference
where it has data — it fixed T-PTG-048's worst finding (a 10-page anchor
error that caused 3 department items to be silently absorbed) and
matched or beat the LLM on every directly-checked boundary against
T-PTG-047's output. But the CSV itself turned out to be *incomplete* in
a way the task's own wrinkle-#2 warning didn't fully anticipate: it's an
"article index," not a full table of contents, and systematically omits
short front-matter department columns (Editorial Perspective,
President's Message) as well as all ad/classified/index back-matter.
This was confirmed directly (not assumed) by searching the raw CSV rows
around PTJ-2020-02's `Feb-20` block and its `Jan-20`/`Mar-20` neighbors —
those titles simply aren't there, in any month. So the honest answer to
"does this fix the six-short-department-item problem" is **partially**:
4 of 6 fixed cleanly, 2 of 6 still missing, but now missing for a
different, CSV-ground-truth-completeness reason rather than an
LLM-boundary-inference reason. I made a point of not softening this in
the report — a worker under this kind of validation task should report
the uncomfortable middle answer plainly rather than rounding to "yes, it
works" or "no, it doesn't."

The other required investigation (ad/index contamination) also produced
a real, non-hypothetical finding: the last-article-in-issue fallback
(needed because CSV rows don't bound their own end) genuinely pulls
back-matter into the final article's file — confirmed by reading actual
sliced text at that boundary in PTJ-2020-02, where ~10 of 16 anchor
pages in the final generated `.md` file are unrelated back-matter (PTG
Review, Foundation Focus, deadlines/notices, etc.), not the cataloged
article.

**Concerns / next steps:** Before a full 90-issue run, someone needs to
decide what to do about the two gaps this pilot surfaced (uncatalogued
department columns; last-article-fallback contamination) — both are
well-understood and addressable without an LLM (a title-keyword
detector for the recurring ad/index page headers would likely catch
most of the second one cheaply), but neither is fixed in this pilot's
scope, which was intentionally CSV-parsing + slicing only. I'd also
flag that T-PTG-048 and T-PTG-047 (and now this task) are all still
sitting in PEER_REVIEW/unmerged as of this session — there's a growing
stack of validated-but-unmerged extraction-pipeline work on `test` that
someone should merge together before it drifts further apart or a
future worker's "confirm merge status" check gets more expensive to
reason about.
