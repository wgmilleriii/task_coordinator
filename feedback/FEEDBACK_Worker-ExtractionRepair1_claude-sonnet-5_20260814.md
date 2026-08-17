# Feedback: Worker-ExtractionRepair1 (T-PTG-047)

## System-Level Feedback

1. **`./bin/fleet verify` still runs `verification_command` against the
   primary clone, not the worktree — same defect already reported by
   `FEEDBACK_WorkerLoginFix1_claude-sonnet-5_20260813.md` item 1, still
   unfixed.** I hit it identically: `cmd_verify` in `bin/fleet.py` computes
   `repo_path = BASE_DIR/../task['repo']` unconditionally, so any task whose
   deliverable only exists on a worktree branch (which is every task,
   per the HARD REQUIREMENT) gets a false FAIL against the primary clone's
   unrelated checked-out state. I worked around it exactly the way the prior
   worker did: ran the verification command by hand inside the worktree,
   confirmed a real pass (exit 0), and wrote the handoff YAML directly
   rather than trusting `fleet verify`'s auto-generated stub (which never
   even gets created on a failed run — `cmd_verify` returns before writing
   anything if `result.returncode != 0`). This means on a verify failure
   there's no stub to edit at all; a worker has to hand-author the full
   handoff YAML from the schema (`schemas/handoff.schema.json`) from
   scratch. That's a second-order consequence of the same bug worth fixing
   alongside it — either `fleet verify` should accept an explicit
   `--repo-path` override (and default to `../<repo>-<task_id>` if that
   worktree exists), or it should still write a (failure-flagged) handoff
   stub so workers aren't reconstructing the YAML schema by hand under time
   pressure.

2. **`fleet verify` requires `--model` but the README's own documented
   command (`./bin/fleet verify T-XXX-123`) doesn't mention it.** Minor,
   but cost a retry — the README's step 4.1 example is out of date with the
   actual CLI's required args.

## Repository-Level Feedback

**What I built:** a local/offline coverage-validation + repair pass for
T-PTG-047 in `journalgpt/spikes/T-PTG-047/` (worktree
`../newmexicoptg.org-T-PTG-047`, branch `test-T-PTG-047`, commit
`65ab465`) — a page-coverage gap/overlap checker, a TOC-anchor-offset repair
step that reuses `articles.pdf_page_offset`'s concept, a "continued on/from
page X" text-scan signal, and (added beyond the two required repair
mechanisms) a small ordering-based end_page overlap trim needed to actually
close overlaps. Also attempted the optional vision-model stretch goal on 1
real PDF page. Full writeup:
`docs/30-Engineering/2026-08-14-page-coverage-validation-repair-pass.md`.

**How it went / lessons learned:**

- The original spike's exact extraction output was never committed to the
  repo (it lived in an earlier session's scratch state), so "re-run the
  pipeline" necessarily meant a *fresh* LLM call with a re-derived prompt,
  not a replay. I made this explicit in the report rather than letting
  readers assume this run's raw numbers are directly comparable to the
  original baseline table row-for-row — they're not, and conflating "new
  LLM run variance" with "repair pass effect" would have produced a
  misleading headline number. Future tasks that need to "re-run and
  compare" a prior spike should consider committing the prior spike's raw
  output (even to a scratch/spikes dir) specifically so re-runs have a
  faithful baseline to diff against, not just a summary table.
- The most useful actual finding: the TOC-offset repair mechanism is
  solid and directly validated (the required PTJ-2025-10 case reproduces
  and repairs correctly), and every one of the 8 sample issues'
  footer-derived front-matter offset came out to exactly 2 at 100%
  confidence — i.e. `pdf_page_offset`'s DB default is empirically correct,
  not just assumed, across this whole sample. That's a small but real piece
  of validated confidence for whoever designs the piece-level schema next.
- The least comfortable, most important finding: **the repair pass makes
  measured gap counts worse, not better** (151 → 164 total across the 8
  issues), because correcting a mis-anchored piece's location removes a
  spurious claim on pages it never should have owned, which un-masks a gap
  that was previously hidden by that overlap. I want to flag this loudly
  for whoever reviews this task: it would be easy to eyeball "overlaps: 15
  → 7, nice" and miss that gaps got worse in the same pass. The report has
  a dedicated section walking through why this happens mechanically — read
  it before deciding pass/fail on this task.
- The "continued on/from page X" signal (Addendum proposal #2) is correctly
  implemented and validated against a positive control outside the sample,
  but it turns out to have near-zero recall on this specific corpus — only
  3 of 90 total extracted issues use that exact phrasing, and none of them
  are in this task's 8-issue sample. It's cheap to keep as an independent
  cross-check but shouldn't be relied on as meaningful validation coverage
  going forward.
- Vision stretch goal: 1 page tested (`PTJ-2020-04` p.3, the sparse ad page
  from the original findings doc's finding #3). It correctly recovered the
  full advertiser name ("Schaff Piano Supply Co.") that text extraction
  truncated to "PIANO SUPPLY CO.", for ~$0.003. Promising single data
  point, not proof it generalizes — I was explicit about that limit in the
  report rather than oversell one successful call.
- Practical worktree note: this repo's `journalgpt/pdfs/` (real PDFs) and
  `journalgpt/.env` (OpenAI key) are both gitignored, so a fresh worktree
  starts with neither — `git worktree add` only checks out tracked files.
  I copied `.env` in and symlinked `pdfs/` from the primary clone
  (`journalgpt/pdfs_real` in the worktree) rather than duplicating ~real
  PDF bytes; both are untracked/gitignored so neither got committed. Worth
  documenting in the fleet README's worktree instructions for the next task
  that needs real secrets or large gitignored assets inside an isolated
  worktree — it's not obvious the first time.

**Recommendation for next steps (also in the report):** don't proceed to
schema design on the strength of this pass alone. The dominant remaining
problem is unclaimed (gap) pages, which neither required repair mechanism
addresses — a gap-page fallback classifier (possibly vision-based, given
the one promising data point) and/or a `review_status`/`needs_review` field
per piece are both still needed before piece-level ranges should be
trusted.
