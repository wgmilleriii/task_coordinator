---
Authored By: Scout-F4 (claude-sonnet-5)
Date: 2026-08-12
---

# Feedback — Scout-F4

## System-Level Feedback

- `bin/fleet lint` currently fails on `T-INTY-017.yaml` ("`dod` was unexpected") — out of my
  boundary lane (minchiate_tarot only), so I left it untouched, but flagging it since a lint
  failure in the shared board could confuse the next agent that runs a bare `./bin/fleet lint`
  and expects a clean exit for the whole fleet.
- No feature requests this session — task.schema.json and the CLI were sufficient for straightforward
  task authoring. One soft complaint: composing a verification_command as a single-quoted YAML
  scalar wrapping `bash -c '...'` with embedded double quotes gets fragile fast (see T-MIN-018's
  command). A `verification_script` field that points at a checked-in `.sh` file would be more
  robust than ever-more-nested quoting inside YAML strings.

## Repository-Level Feedback

Wrote three OPEN tasks against minchiate_tarot (branch `test`, HEAD 09f857d), applying the two
editorial decisions Chip recorded in `tasks/human/editorial_decisions_2026-08-12.md` (D3, D4), plus
an unblock attempt for the stalled T-MIN-008.

**T-MIN-016 (D3, SPECIAL-FOOL rename).** I grepped the full repo myself before scoping and the
blast radius is larger than the decision doc implies: it's not just the registry + one dossier +
the Trumpets typed edge. Eleven other committed pilot draft files (TRUMP-01, 02, 04, 05, 09, 11,
13, 14, 15, 19, 40) cite "TRUMP-FOOL" as a registry-row evidence source in their claims tables
(e.g. `Master registry TRUMP-FOOL row`), not just in narrative prose. I listed the full set
explicitly in scope rather than leaving the worker to rediscover it. I also confirmed no
contradiction: FOO-C003 in the Fool study already separates "unnumbered on card" / "outside ranked
ladder" / "sort 57 as bookkeeping (may be 0)" as three distinct statements, so sort_order=0 does not
collide with any of them — the file already anticipated this. Bigger finding: there is genuinely
**no alias/former-id field anywhere in the schema** (registry CSV/JSON or the Stage4 dossier
schema) — grep for "alias" across both locations returns zero hits. D3's "permanent alias"
requirement has no existing mechanism to attach to, so I required the worker to either add one
consistently or explicitly document the absence rather than silently working around it — this is
the single biggest ambiguity in the task and worth a PM's eyes before audit.

**T-MIN-017 (D4, Cavalier/Knight).** Lower blast radius than I expected: `canonical_name` is
already "Cavalier of <Suit>" for all four rows, and "Knight" is already present in
`historical_names` — the registry was already halfway compliant. The real gap is that there's no
distinct "search alias" field to make Knight's subordinate status explicit and machine-checkable,
so I scoped it as either a new column (used consistently across all four rows) or an explicit
policy note that historical_names doubles as the alias list for now. I did not find any existing
NAMING_POLICY.md or equivalent — the worker will be creating that file from scratch.

**T-MIN-018 (Bernardi unblock).** T-MIN-008 was genuinely still OPEN/unaudited (no audited_at,
audited_by, or sha), so nothing was overwritten. I wrote T-MIN-018 as a superseding replacement
rather than editing T-MIN-008 in place, per the instruction that scouts don't archive existing
tasks — a PM still needs to decide whether T-MIN-008 gets archived once T-MIN-018 is picked up. I
preserved T-MIN-008's original scope/DoD verbatim and added a mandatory-first-step requirement to
try archive.org's metadata API and OCR/plaintext views (with the exact endpoint pattern) before
falling back to "human must acquire a copy," modeled directly on T-MIN-009's precedent
(`Zodiac_Locator_Resolution_Note.md`), which resolved a structurally identical problem via
WebFetch/WebSearch with zero local storage of sources.

All three verification_commands were dry-run against the real current tree (via direct bash
execution after extracting the command from the parsed YAML) and confirmed to FAIL now for the
right reason (TRUMP-FOOL still present with old sort order; no NAMING_POLICY.md exists; no
attempt-log+archive.org note exists yet).

**Recommended next step for the PM:** audit T-MIN-016 first — it's the biggest blast radius and has
the schema-gap question (no alias mechanism) that a human/PM may want to resolve conclusively before
a codex worker picks arbitrary fallback behavior.
