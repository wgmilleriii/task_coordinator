# Feedback: Reviewer-F25 (claude-sonnet-5) — 2026-08-12

Task reviewed: T-MIN-017 (Cavalier/Knight naming policy, D4). Verdict: **PASS**. Task moved to DONE.

## System-Level Feedback

1. **`record-review` schema rejects `LOW` severity.** The schema only accepts
   `INFO`, `MINOR`, `MAJOR`, `CRITICAL`. I initially wrote a `LOW` finding (for an
   out-of-scope observation) and `fleet record-review` failed with a schema error
   before I corrected it to `MINOR`. Not a blocker, but worth noting since "LOW" is
   a natural word to reach for and the error message, while accurate, only surfaces
   after the fact — a `fleet lint`-style pre-check on review files before running
   `start-review`/`record-review`, or documenting the exact severity enum in the
   `start-review` template output, would save a retry.

2. **YAML gotcha in review templates.** A plain (unquoted) multi-line block scalar
   in a `description:` field breaks if the prose contains something that looks like
   a YAML mapping colon, e.g. writing `("aliases": ["Knight"])` inside a description
   produced `mapping values are not allowed here` from `yaml.safe_load`. I fixed it
   by rephrasing to avoid embedded colons/quotes rather than switching to a `>-`
   block scalar for that entry, but the `start-review` template doesn't warn about
   this and it's an easy trap when a review is specifically about JSON key names
   (colons are all over such descriptions). Consider having `record-review` catch
   this class of YAML error with a clearer hint ("your description text likely
   contains a literal `key: value` pattern — quote the field or avoid embedded
   colons"), since the raw yaml.scanner traceback is not obviously self-explanatory
   to point back at the review file's prose.

3. Everything else about the review workflow (`start-review` → hand-fill →
   `record-review`) worked cleanly and the generated template made the required
   fields unambiguous. `git worktree add <sha>` for isolated review verification
   without touching the shared checkout's branch worked well and I'd recommend it
   stay the standard reviewer pattern.

## Repository-Level Feedback (minchiate_tarot)

T-MIN-017 asked Worker-F20 to apply editorial decision D4 (Cavalier is the public
heading for the four cavalier court cards; Knight is a subordinate search alias),
building on T-MIN-016's generic `aliases` field. I verified all six required checks
from the review brief and all passed:

- **Verification command**: re-ran the audited `verification_command` from the task
  YAML in a fresh worktree at the submitted head sha (`a113400...`) — PASS, exit 0.
- **The grep -A20 bug and fix are both real.** In the base state (`de0861c`), each
  of the four cavalier JSON entries in `Stage5_Master_Card_Registry.json` runs 25
  lines from `"card_id"` to its closing `}`, and none of the four had an `aliases`
  field pre-task (only `SPECIAL-FOOL` did, from T-MIN-016). If the worker had
  appended `aliases` naturally near the end of the object (next to `notes`, as
  T-MIN-016 did for `SPECIAL-FOOL`), a `grep -A20 "card_id"` check would miss it —
  this is a real, demonstrable fragility in the audited verification command, not
  a hypothetical. The worker's fix inserts the new `aliases` key at relative line
  4-6 from `card_id` (right after `historical_names`) in all four entries, which is
  comfortably inside the 20-line window. `git diff de0861c..HEAD` on the JSON shows
  this is a clean, minimal 3-line insertion per entry (`"aliases": ["Knight"]`) —
  no other line in any of the four objects changed. I parsed the full post-change
  JSON file with Python's `json.load` (not just visual inspection) and it is valid.
  This was a good, well-diagnosed fix and the worker correctly treated it as
  "content-preserving" even though technically it was a *new field insertion at an
  early position* rather than a reorder of a pre-existing key — worth being precise
  about that distinction in task language going forward ("repositioning" implies
  the field already existed; here it didn't yet on these four rows).
- **Policy doc** (`research/04-dossier-spec/NAMING_POLICY.md`): genuinely new,
  specific prose (not boilerplate). Covers all three required points: historical
  accuracy governs `canonical_name` with the Page precedent explicitly cited;
  common terms like Knight are retained only as `aliases`, never as headings; and
  an explicit "no URL/slug routing system exists yet" scope-limiting section. Also
  usefully explains *why* `aliases` was reused rather than inventing a second field
  (mirrors the FOOL former-id use case), which the task asked for.
- **Four-row consistency**: checked all four cavalier rows in both the CSV (via
  `csv.DictReader`) and JSON. `canonical_name`, `historical_names`, and `url_slug`
  are byte-identical to base; `aliases` uniformly contains `"Knight"` in the same
  shape across all four rows in both files.
- **Scope**: `git diff --name-only de0861c..a1134002504adb8e2ef34920fbfcd9b0b8dc250b`
  touches exactly `NAMING_POLICY.md`, the registry CSV, and the registry JSON. The
  pilot/draft content files (`Pilot2_SUIT-CUPS-12_Cavalier_of_Cups.md` and its
  dossier JSON) are untouched, as required.

**Follow-up worth scouting (not a blocker for this task):** the same grep-window
fragility likely already lives in T-MIN-016's merged `SPECIAL-FOOL` entry — I
checked the current registry JSON and `SPECIAL-FOOL`'s `aliases` field sits at
relative line 25 from its `card_id` line (field order there is `historical_names`,
`names_to_avoid`, ... `notes`, then `aliases` appended last), i.e. past a 20-line
grep window, the exact class of bug T-MIN-017's worker found and fixed for the four
cavalier rows. T-MIN-016 already passed via real regression testing, which is a
stronger correctness signal than any single grep check, so I'm not flagging this as
broken — just noting it's worth a small scout task to check whether any consumer of
that registry actually depends on a `grep -A<n>`-style shallow read near
`SPECIAL-FOOL`, and if so, either widen the window or move `aliases` earlier there
too for consistency with the pattern T-MIN-017 just established.

**Recommended next step:** none required for T-MIN-017 itself — it is DONE. Suggest
a low-priority scout task for the `SPECIAL-FOOL` grep-window follow-up described
above.
