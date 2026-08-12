---
title: "T-PTG-004 Citation Metadata Audit Findings"
created_at: "2026-08-12T04:25:00Z"
last_modified: "2026-08-12T04:25:00Z"
author: "Claude-Worker"
status: "active"
category: "00-Meta"
---

## System-Level Feedback

- No general complaints about the coordinator engine itself in this session.
  One workflow friction point worth noting: a task with `dependencies` can be
  fully implemented in code (same commit, same PR) but cannot be formally
  `claim`ed/`verify`ed/`submit`ted through the CLI until its dependency reaches
  `DONE` — and `DONE` requires human close when `human_review_required: true`.
  That's the correct safety behavior, but there's no first-class way to record
  "implementation landed, blocked on a dependency's human close" other than
  hand-editing the YAML `events` list directly (which I did for T-PTG-002 and
  T-PTG-003). A `fleet note <task_id> --text "..."` command would make this a
  supported operation instead of a manual YAML edit.

## Repository-Level Feedback (newmexicoptg.org / journalgpt)

**T-PTG-004 audit result**: Ran `journalgpt/cli/audit_citation_metadata.php`
(new script, committed alongside T-PTG-001/002 in
`23eb6e0ab653ed3f96139cfed558011a098a6712`) against the local dev DB
(`journal_ai_test`, 92 seeded articles). **Zero mismatches found.** All 92
local titles follow the well-formed pattern
`"Piano Technicians Journal — <Month> <Year> Issue (Vol. X No. Y)"` with
volume/issue_number columns agreeing with the embedded title text, and none
match the generic-placeholder pattern (`"... Issue Content"`) seen in the
production bug report.

**This does not mean the bug doesn't exist** — it means the local pilot
subset (92 articles, evidently a curated/clean slice) doesn't reproduce it.
The original report came from a live production answer citing
`'2022-10-01 Vol. 69 No. 10 — "Piano Technicians Journal — October 2022 Issue
(Vol. 65 No. 10)"'` for `article_id=145` — a volume/issue-number mismatch
(69 vs 65) for the same physical issue — plus several citations to titles
like `"Piano Technicians PTJ 2025-05 Issue Content"`, which read like a
synthesized fallback title rather than a real one.

**Recommended next step for a human or a session with production DB
access**: run `journalgpt/cli/audit_citation_metadata.php` directly against
production (it's read-only, exits 1 and prints every offending row when it
finds mismatches — safe to run anytime). If it reproduces the Vol. 69/65
mismatch, the next question is which value is authoritative: the `title`
string (likely hand-written or scraped from the actual PDF cover) or the
`volume`/`issue_number` columns (likely derived during import). My guess
without seeing the actual mismatched rows is that `title` is more trustworthy
since it was probably transcribed per-issue, while `volume`/`issue_number`
may have been computed by a single import script that could have an
off-by-N bug across a range of issues — but this needs to be confirmed
against actual mismatched rows, not assumed.

I was not able to close this task's loop entirely (find + fix real
mismatches) in this session because I only have access to the local dev
database, which doesn't contain the affected rows.
