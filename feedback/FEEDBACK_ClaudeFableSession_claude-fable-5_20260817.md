# Feedback — Coverage Atlas filing + board cleanup session (2026-08-17)

## System-Level Feedback

1. **T-PTG-046..049 are real ID collisions.** Two parallel swarms each minted the
   same ids for unrelated tasks (the "Phase N corrected re-implementation" series
   vs. the extraction/QC series). Both records were preserved: the internal `id:`
   fields are unchanged (external references in handoffs, specs, and commit
   messages stay valid), and the later-filed tasks live in `tasks/archive/` under
   disambiguated FILENAMES (`T-PTG-046-citation-history-links.yaml`,
   `T-PTG-047-page-coverage-validation.yaml`, `T-PTG-049-airtable-transcription.yaml`).
   Feature request: `fleet` should allocate ids centrally (e.g. `fleet next-id
   PTG`) or lint duplicate ids across active+archive so this cannot recur.
2. **The working tree held ~200 uncommitted fleet records** (archive moves,
   handoffs, reviews, feedback, task files) spanning 2026-08-13..16. Sessions are
   dying between doing the work and committing the records. Feature request: make
   `fleet` CLI actions auto-commit (the atomicity claim in the README assumes the
   git commit happens).
3. **Schema drift:** 5 legacy task files used a `description:` field the schema
   forbids and lacked the required `scope:`. Fixed mechanically (description folded
   into scope as a single item). 12 additional active files were stale earlier
   copies of tasks already DONE in archive; deleted in favor of the archive record.
4. Left deliberately uncommitted for a human decision: `fix.py`, `fix2.py`,
   `fix_docs.py`, `dashboard/`, `bin/serve-dashboard` — experimental code of
   unknown provenance, not fleet records.

## Repository-Level Feedback (newmexicoptg.org)

Filed T-PTG-051..056: the Coverage Atlas epic delivering
`docs/superpowers/specs/2026-08-17-coverage-atlas-design.md` (coverage radar over
the topic taxonomy + curated tours/threads + the existing quiz engine; supersedes
the prerequisite-skill-tree learning-paths spec). The article-index foundation
(migration 018, 4,120-row CSV import, editable article x topic tagging matrix) is
already merged and pushed on `test` (a8f88e1, a8048ba, a2bb4d7); T-PTG-051 is only
the shared-DB rollout, which is gated on Chip's explicit go because
test.newmexicoptg.org shares production's database. The epic's known technical
risk is concentrated in T-PTG-052's resolver (issue-level article ids -> per-article
index rows via issue label + page range); it was scoped as TDD-first for that
reason. Recommended next step: PM-audit 051 first (it unblocks both branches of
the dependency graph), then 052 and 054 can proceed in parallel.
