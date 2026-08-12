---
title: "PM-F7 Audit Session — T-MIN-016/017/018"
created_at: "2026-08-12T12:00:00Z"
last_modified: "2026-08-12T12:00:00Z"
author: "PM-F7"
status: "active"
category: "00-Meta"
---

# System-Level Feedback

- `fleet audit --command` fully **overwrites** `verification_command`, discarding whatever is hand-written
  in the YAML beforehand. That's fine once understood, but it means a PM who hand-tunes the
  verification command in the YAML file (as instructed) must re-extract and re-pass the exact same
  string via `--command`, or the CLI's copy silently wins and the YAML edit is wasted. Worth a README
  callout for future PMs: "the string you pass to `--command` is the one that ships, not the one in the
  file."
- No `pyyaml` in the ambient `python3` — I had to build a throwaway venv (`python3 -m venv /tmp/vv &&
  pip install pyyaml`) just to safely extract multi-line `verification_command` strings out of YAML for
  dry-running. `bin/fleet` already activates `.venv` internally; a `fleet dump-field <task_id>
  verification_command` helper (or similar) would remove this friction for every future PM doing
  fail-first verification.
- The registry/dossier schema had a real, confirmed gap: **no alias/former-id field anywhere**
  (`grep -ri alias research/05-registry-and-audit/ research/04-dossier-spec/` = zero hits before this
  session). Two independent tasks (D3, D4) both needed one. Scout-F4 flagged it but left it for the PM
  to decide, which is the right call — but it's the kind of decision that should get made once, in one
  place, not independently by two future codex workers who'd likely invent two incompatible schemas.

# Repository-Level Feedback

## What I did
Audited T-MIN-016 (D3: TRUMP-FOOL → SPECIAL-FOOL rename), T-MIN-017 (D4: Cavalier/Knight naming
policy), and T-MIN-018 (Bernardi 1790 direct-web-access attempt), all `lane: codex`. All three are now
`AUDITED` against `test` @ `09f857d` with fail-first verification commands confirmed to actually FAIL
against current committed content before any work is done.

## Architectural decision: the alias field
Confirmed the gap myself (zero `alias` hits in the registry/schema directories). Decision: add one new
**optional** field, `aliases` (list of strings), to `Stage5_Master_Card_Registry.csv` (new trailing
column), `Stage5_Master_Card_Registry.json` (per-row key), `Stage4_Card_Dossier_Schema.json`
(`administrative_identity.aliases`, not in `required`), and `Card_Dossier_Skeletons.json` entries. Baked
this into T-MIN-016's scope as the concrete fix (not left to the worker's judgment), and made T-MIN-017
**depend on T-MIN-016** so the same field gets built once, then reused for Knight's search-alias rather
than two workers inventing two shapes in parallel. If T-MIN-016 lands first, T-MIN-017's verification
command checks for the field's existence and fails loudly ("T-MIN-016 not applied first") if it's
missing.

## T-MIN-016 additional findings (beyond the alias gap)
1. **Schema conflict caught before it could bite**: `Stage4_Card_Dossier_Schema.json`'s
   `administrative_identity.sort_order` has `"minimum": 1, "maximum": 97`. The task instructs setting
   sort_order to 0 for SPECIAL-FOOL — that would have silently produced a schema-invalid skeleton entry.
   Added an explicit scope item requiring the schema's minimum be widened to 0 (one-line, backward
   compatible — every other card still uses `>=1` in practice) as part of this same task.
2. **11-file citation claim — 10 confirmed real, 1 false positive**: spot-checked TRUMP-01 and TRUMP-19
   in full (both contain live `TRUMP-FOOL` citation tokens — confirmed genuine), then ran
   `grep -c "TRUMP-FOOL"` across all 11 listed files. Ten return >=1 (real). **PERSONALITY_TRUMP-40_Trumpets.md
   returns 0** — its TRO-C002/006/018 citations and the L272-282 reciprocal-edge prose reference "the
   Fool" and "FOO-C014" (the Fool's own claim-id prefix, already independent of the dossier id), never
   the literal token "TRUMP-FOOL". Flagged this explicitly in the task scope so the worker doesn't waste
   time hunting for a citation that isn't there — file needs zero edits under this task.
3. Confirmed FOO-C003 already anticipates sort key 0 ("registry key, may be 0") — no contradiction to
   flag, matches the scout's original finding.

## T-MIN-018 vs T-MIN-008
Per instruction: left **T-MIN-008 OPEN and untouched** (did not audit it, did not archive it — that's a
human/PM call the task itself defers). Audited only **T-MIN-018**, which supersedes T-MIN-008's scope
with a mandatory direct-web-access-first step. Confirmed the fail-first verification genuinely fails now
(no committed note anywhere combines "attempt log" and "archive.org" alongside "verzicola").

## Recommended next steps
- Whoever claims T-MIN-016 should do the schema/CSV/JSON edits in one pass to avoid a half-migrated
  `aliases` field.
- T-MIN-017's claimant must wait for T-MIN-016 to reach DONE (enforced by `dependencies` + the fleet
  claim gate) — don't let a codex worker jump the queue by editing the schema themselves.
- After T-MIN-016/017 land, the reconciliation queue in T-MIN-018 should be revisited once (if ever)
  the verzicola boundary resolves — not touched in this session.
