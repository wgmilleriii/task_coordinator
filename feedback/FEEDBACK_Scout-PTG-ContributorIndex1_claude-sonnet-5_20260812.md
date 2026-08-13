# Feedback — Scout-PTG-ContributorIndex1 (claude-sonnet-5, 2026-08-12)

## System-Level Feedback

- No loopholes or defects hit this session. The task lifecycle and schema were
  straightforward for this case: unlike T-PTG-008/009, this Scout was handed an
  *already-approved* design doc and a *complete* task-by-task implementation plan
  from a prior planning session, so the job was narrower than usual Scouting — write
  a task whose `scope` points at those documents rather than re-deriving the design.
  Worth naming as a pattern: when `docs/superpowers/specs/*` and
  `docs/superpowers/plans/*` already exist and are approved, a Scout's job shrinks to
  "summarize the deliverable + load-bearing constraints + point at the docs," and the
  temptation to copy the plan's code/detail into the YAML (bloating `scope` into a
  duplicate of a 1200-line plan file) should be resisted — I kept `scope` to the
  boundaries and constraints, not the SQL/PHP itself.
- `./bin/fleet lint` currently reports a pre-existing schema error on
  `T-INTY-017.yaml` (`'dod' was unexpected` — looks like a typo'd key that should be
  `definition_of_done`). Not something I touched or fixed (out of my repo/role), but
  flagging it since it means `fleet lint`'s exit status is already non-clean before
  any new task is added — a PM/Fleet Coordinator auditing tasks should not assume a
  lint failure is caused by the newest file without checking which file it names.

## Repository-Level Feedback

- Wrote `T-PTG-010.yaml` (`newmexicoptg.org`, P2, `status: OPEN`,
  `human_review_required: true`, `requires_doc_update: false`). Deliberately did not
  re-derive the design: `scope` opens by pointing directly at
  `docs/superpowers/specs/2026-08-12-contributor-index-design.md` and
  `docs/superpowers/plans/2026-08-12-contributor-index.md` as the authoritative
  source, then summarizes the deliverable (new `contributors`/`article_contributors`
  entity index, `ContributorNormalizer`, the `CorpusIndexer` ingestion hook,
  `cli/backfill_contributors.php`, `ContributorStatsService`, and the `api/ask.php`
  router wiring) and the five load-bearing constraints a PM/Worker needs without
  opening both other files: no vector-store call from the new path, answers are
  SQL-templated never LLM-generated, router is a fixed phrase list (mirroring
  `FeatureRequestService::isTagged()`'s T-PTG-008/009 discipline), low-confidence
  author matches create `pending` contributors rather than auto-merging, and a
  router miss falls through unchanged to RAG.
- One discrepancy I found and resolved by picking the more authoritative source: the
  design doc's prose says the marker for a contributor-index turn is a
  `retrieval_mode='contributor_index'` field, but the implementation plan (the
  task-by-task, code-level document, and the one this task's DoD directly quotes
  from the user's own words) says to reuse the *existing* `debug_logs.preset` column
  with `preset='contributor_index'` — the same column `FeatureRequestService`
  already uses for `preset='feature_request'`. I followed the plan (the more
  concrete, more recently-operative document) and said so explicitly in `scope` so a
  PM auditing this doesn't silently pick the design doc's wording instead and
  introduce a new column that duplicates `preset`.
- Used `T-PTG-008.yaml` as the structural precedent (closest in shape: new
  migration + new service class + new router branch + new test files, same repo),
  and `T-PTG-009.yaml` for the fixed-phrase-router discipline this task's router
  must match.
- Did not audit or unlock this task — left it `OPEN` per the Scout role boundary.
  Next step is a PM reading both docs plus this YAML, independently confirming the
  `preset` vs `retrieval_mode` call I flagged, and running `./bin/fleet audit`.
- Ran `./bin/fleet lint` after writing the file and confirmed T-PTG-010 produces no
  schema errors (the one lint failure present, on `T-INTY-017.yaml`, predates this
  session and belongs to a different repo lane).
