# Feedback — PM-F3 (claude-fable-5) — 2026-08-11

Session: PM audit of T-MIN-009 (minchiate_tarot lane only, per the boundary rule).

## System-Level Feedback

1. `./bin/fleet lint` currently exits 1 due to thirteen pre-existing schema
   violations in T-INTY-* task files (non-array scope/dod strings, unexpected
   `assigned_to`/`description`/`dod` keys). The boundary rule forbids a
   minchiate PM from touching them, so every minchiate session now ends with a
   red lint it cannot fix. Suggest: a `--repo minchiate_tarot` filter on lint,
   or a Fleet Coordinator sweep of the INTY lane.
2. The audit subcommand accepted a multi-line `bash -c` verification command
   and the YAML round-trips it correctly — good. But nothing in the tooling
   discourages the failure mode T-MIN-009 shipped with: a bare `grep -c` that
   exits 0 whether or not the work is done. A lint warning for verification
   commands with no possible non-zero exit path (e.g. plain `grep -c`,
   `echo`, `ls`) would catch this class cheaply.
3. Onboarding: `fleet onboard minchiate_tarot` worked and wrote
   `.fleet_context.md` into the spoke repo. Its Janitor section reported
   "496238.8 hours since the last doc update" (about 56 years) — the timestamp
   source is clearly an epoch default, so the 24-hour Janitor trigger logic is
   effectively disarmed. No DOCUMENTATION UPDATE REQUIRED warning was present,
   so the Janitor Protocol was not invoked; note also that `/chord-tune` is not
   available in this environment, so had it been required it could not have
   been executed honestly.
4. There is also a stray untracked `.fleet_context.md` in the coordinator
   root and a large untracked T-INTY handoffs/reviews/tasks population; I left
   all of it alone.

## Repository-Level Feedback

How the audit went:

- Premises all verified against minchiate_tarot branch `test` at 274b981
  (T-MIN-005 corrections ae9bca3 merged, no branch switch): all twelve
  zodiac studies exist in `research/pilots/drafts/` (PERSONALITY_TRUMP-24
  through TRUMP-35); every one still carries at least one locator hedge
  (variants found: `[chapter locator UNVERIFIED]`, `[locators UNVERIFIED]`,
  `[chapter UNVERIFIED]`, `[line UNVERIFIED]`, `[tropic locator UNVERIFIED at
  line precision]`, plus checklist lines "locators marked UNVERIFIED");
  `research/pilots/Zodiac_Batch_Verification_Report.md` (T-MIN-005's
  deliverable) exists.
- The old verification command (`grep -c 'UNVERIFIED' ...Libra.md`) was
  vacuous — it succeeds before and after the work. Replaced with a read-only
  bash one-liner that (a) fails if any of the twelve studies still contains a
  bracketed locator hedge or a "locator(s) [marked] UNVERIFIED" phrase — while
  deliberately permitting bare `[UNVERIFIED]`, the sanctioned wholesale
  downgrade — and (b) requires a
  `research/pilots/Zodiac_Locator_Resolution*.md` note naming all twelve
  TRUMP ids. Dry-ran it before auditing: it fails now on all twelve files,
  which is the correct pre-work behavior.
- Scope tightening applied (two lines in the YAML): external source access is
  explicitly in scope (web editions and library APIs for Ptolemy, Aratus,
  Sacrobosco, Isidore; memory-resolution still forbidden) — this closes the
  same ambiguity that blocked T-MIN-008 — and the resolution note's expected
  filename is pinned so the verification command's expectation is
  discoverable by the worker.

Concerns and next steps:

- The worker who claims T-MIN-009 needs genuine web access to primary-source
  editions; if a runner without network picks it up, it should be blocked, not
  faked — the 208-untraceable-references audit is the standing cautionary tale.
- The five hedge variants above are the exact strings to hunt; the six
  Tetrabiblos I aspects-chapter edges resolve together (one locator serves
  LIB-C017/ARI-C010, CAP-C012/CAN-C010, SAG-C013/GEM-C012, AQU-C014/LEO-C011
  and kin), so the task is smaller than twelve independent lookups.
- Recommended order: Tetrabiblos I aspects chapter first (clears the most
  claims), then Sacrobosco cap. II tropics, then Aratus Chelae/Parthenos
  lines, then Isidore Etym. III, then the domicile/Hydrochoos/Dioscuri
  singletons.
