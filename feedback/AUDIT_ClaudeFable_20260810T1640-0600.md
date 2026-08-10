# Second Audit: Task Coordinator V2 (post Phase 1–3)

**Agent:** Claude Code
**Model:** Claude Fable 5 (`claude-fable-5`)
**Date:** 2026-08-10 ~16:40 MDT
**Prior review:** `FEEDBACK_ClaudeFable.md` (this morning, against the 125-line prototype)
**This review:** the repo as of commit `69e2f6f` ("Phase 3: Add 'fleet verify'…"), fleet.py
now 322 lines. **All findings below were established by executing tests against a scratch
copy** (never the live board), using the repo's own `.venv`. Test transcripts are quoted
verbatim.

---

## What changed, and what my morning findings it resolves

| Morning finding | Status now |
|---|---|
| Not a git repository | **FIXED** — 4 commits, remote at `github.com/wgmilleriii/task_coordinator` |
| Lifecycle documented but not enforced (3 commands) | **LARGELY FIXED** — `audit`, `claim`, `verify`, `submit`, `close` now exist with status-gated transitions |
| Evidence pasted, not captured | **FIXED IN DESIGN** — `fleet verify` executes the task's `verification_command` in the sibling repo, captures exit code + stdout/stderr into a handoff file, refuses on nonzero exit, and `submit` gates on the handoff existing and `head_sha` being filled. This is the right mechanic. |
| No duplicate-ID / filename / dependency checks | **FIXED** — lint now catches duplicate IDs, filename↔ID mismatch, and dangling dependencies |
| Weak schema (no conditional invariants, open fields) | **LARGELY FIXED** — `additionalProperties: false`; AUDITED+ requires the audit quartet; CLAIMED+ requires a non-empty owner |
| Atomic writes | **FIXED** — `save_task` and `render` both write temp + `os.replace` |

This is real progress at real speed. The remaining gaps are fewer and sharper.

---

## Verified defects (each demonstrated by a test run)

### D-1 · Format checking is a silent no-op — Codex's finding is still live

```
TEST1: ACCEPTED bad date-time — format checking is a silent no-op
```

`jsonschema.FormatChecker()` only validates `date-time` if `rfc3339-validator` is
importable; it is not in `requirements.txt`, so `created_at: "NOT-A-DATE"` passes a green
lint. The Codex review demonstrated this exact acceptance this afternoon and Phase 1's
"strict" linting did not close it. **Fix: add `rfc3339-validator` to requirements.txt**
(one line), and add a lint self-test that asserts a known-bad date fails, so the no-op can
never silently return.

### D-2 · `close` skips human review even when the task demands it

```
human_review_required = True
✅ Task T-MIN-001 successfully marked as DONE.
final status: DONE
```

`cmd_close` accepts PEER_REVIEW → DONE unconditionally. The `human_review_required` flag —
present in the schema, set `true` on the only real task — **is never read by any code path**
(grep confirms: it appears only in the schema and the YAML). There is also no command that
*reaches* HUMAN_REVIEW at all. The lifecycle's entire purpose was that the human gate cannot
be skipped; currently it is skipped by default. **Fix: `close` on a task with
`human_review_required: true` must require `--human <name>` (or a separate
`fleet approve`), and PEER_REVIEW → HUMAN_REVIEW needs an explicit transition (`fleet
peer-pass`) that requires a review artifact (see D-5).**

### D-3 · Hand-edits still bypass everything, and lint cannot see them

```
TEST2: schema ACCEPTS a hand-edited jump to DONE (no transition memory)
TEST5 (lint of that state): ✅ All tasks passed strict schema validation.
```

Expected — a schema cannot hold transition memory — but now that the repo is in git, the
missing enforcement is buildable: **lint should diff each task file against HEAD and reject
any status change whose commit was not authored by the CLI** (simplest: CLI stamps a
`last_transition` field — schema change required, see D-4 — or CLI commits transitions
itself with a recognizable trailer, and lint flags dirty status edits).

### D-4 · `additionalProperties: false` now locks out the fields the system still needs

```
TEST4: claimed_at REJECTED — additionalProperties:false locks out the field
```

Closing the schema was right, but it froze the schema one field too early. `claim` still
records no timestamp, so stale claims (the V1 disease: agents "DISPATCHED" six weeks ago)
remain undetectable — and now the fix requires a schema release, not just a CLI patch.
**Fix: add `claimed_at` (and `last_transition`, per D-3) to the schema in the same change,
and a lint rule flagging CLAIMED/IN_PROGRESS tasks older than N days.**

### D-5 · PEER_REVIEW still has no mechanism, and handoffs are never schema-validated

`submit` moves the task to PEER_REVIEW but nothing defines what the peer review *does*,
who runs it, or what artifact it produces; `peer_review_notes` is an optional free string.
Meanwhile `handoff.schema.json` exists but **no code path ever validates a handoff against
it** — `submit` checks only that `head_sha` isn't the placeholder; lint ignores
`handoffs/` entirely. And `cmd_verify` writes `model: "Unknown"` and `branch: "test"`
hardcoded, so the handoff's provenance fields — the ones that let me triage this morning's
mixed-quality fleet sweep in `minchiate_tarot` by author — are dead on arrival. **Fixes:
lint validates every handoff; `verify` takes `--model` (required) and reads the branch
from the spoke repo (`git -C <repo> branch --show-current`); a `review.schema.json`
(findings, severity, verdict, corrections) becomes the required artifact for
PEER_REVIEW → HUMAN_REVIEW.** For what the peer-review playbook should contain, see the
worked examples in `minchiate_tarot/research/pilots/*_Verification_Report.md` — five of
them now, which collectively caught a false central claim, a rank inversion, invented
relationship vocabulary, and citation mis-pins that authors' self-review missed.

### D-6 · The claim race is unchanged

`cmd_claim` is still read-all → check → write. `os.replace` makes the *write* atomic, not
the *transaction* — two concurrent claims interleave and both print success (the second
silently wins the file). Now that a remote exists, the cheap arbiter is: claim = commit +
push; on push rejection, pull and re-check. Locally, an `os.open(..., O_CREAT|O_EXCL)`
lockfile around the read-check-write would close the same hole in five lines.

---

## Smaller findings

- **README is now behind the CLI** — it still instructs agents to hand-edit YAML to
  PEER_REVIEW (line 58) and never mentions `audit`/`verify`/`submit`/`close`. Doc drift
  begets protocol drift; regenerate the agent instructions from `--help` or update now.
- `cmd_audit` accepts DRAFT but its error message says "must be OPEN" — pick one.
- `datetime.utcnow()` is deprecated (Python 3.12+); use `datetime.now(timezone.utc)`.
- No `archive`, `unclaim`, or `block` commands yet; `tasks/archive/` and DONE-bloat of
  `render` remain unhandled (carried over from my morning review).
- `verify`'s 300s timeout will be too short for real research-verification commands;
  make it a task field with a default.
- The working tree has an uncommitted modification to `FEEDBACK_Antigravity.md` — with git
  now live, keep the board's own hygiene rule: commit or discard before the next phase.
- T-MIN-001 remains the only task and remains stale relative to `minchiate_tarot` reality
  (my morning finding #6, unaddressed): its scope asks for an app that already exists at
  `tools/reviewer_app/`, and it has now additionally been through my scratch tests'
  wringer conceptually — re-audit it against spoke HEAD before anyone claims it.

## Priority order

1. **D-2** (human gate skippable — this is the one that defeats the system's purpose)
2. **D-1** (one-line dependency + a self-test; a validator that silently no-ops is worse
   than none because it *launders* confidence)
3. **D-4 + D-3 together** (one schema release: `claimed_at`, `last_transition`; lint rules
   for staleness and un-CLI'd transitions)
4. **D-5** (handoff validation now; review schema + playbook next — this is what converts
   PEER_REVIEW from a status into the AUDITOR stage that actually unclogs the human lane)
5. **D-6** (lockfile now; push-arbitration when multi-machine becomes real)

The trajectory is exactly right: four commits in one afternoon closed roughly half of two
agents' findings. What remains is concentrated in one theme — **the gates exist but do not
yet bite** — and every fix above is small. When `close` refuses a human-gated task, lint
fails on a fake date, and a handoff won't submit without provenance, this coordinator will
enforce more discipline than any system I've reviewed this weekend, V1 included.

— Claude Fable 5, 2026-08-10, with executed test evidence
