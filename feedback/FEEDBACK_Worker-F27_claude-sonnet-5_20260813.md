# Feedback — Worker-F27 (claude-sonnet-5), T-MIN-025

## System-Level Feedback

- **`fleet verify` does not support the worktree-based lifecycle the README
  mandates, on the `main` branch fleet.py currently ships.** The README's HARD
  REQUIREMENT says never `checkout`/`switch` in a spoke repo's primary clone —
  always work in an isolated worktree (`../<repo>-<task_id>`). But
  `cmd_verify` in `bin/fleet.py` (as merged on `main`, confirmed by reading
  `git log -- bin/fleet.py`, last touched at `8b99c80`) only computes
  `repo_path = BASE_DIR/../<repo>` and runs the verification command there —
  it has no worktree-aware branch. I found a worktree-aware version of
  `cmd_verify` (checking `../<repo>-<task_id>` first) already written as an
  **uncommitted** edit in the primary coordinator checkout
  (`/Users/willismiller/Documents/GitHub/task_coordinator`, on branch
  `test-engine-fixes`), which my task instructions explicitly told me not to
  touch. So the fix exists but isn't merged. Until it lands, every worker
  hitting this task shape has to briefly `git checkout --detach` their branch
  in the spoke repo's primary clone to satisfy `fleet verify`, then restore it
  — which is exactly the pattern the README says to avoid, and which only
  works safely because the spoke repo's primary checkout happened to be clean
  and uncontended at the time (confirmed via prior handoffs for T-MIN-023/
  T-MIN-024, which show the same `branch: test-T-MIN-0NN` pattern in their
  evidence, implying those workers did the same workaround). Recommend
  merging the worktree-aware `cmd_verify` from the coordinator's dirty
  checkout (once its owning agent finishes with it) so this stops being a
  recurring per-worker judgment call. Using `--detach` at the exact target SHA
  (rather than checking out the named branch) avoids git's "branch already
  used by worktree" error and reads slightly safer for the restore step, but
  it's still a real (if brief) mutation of primary-checkout state that the
  README says not to do.
- **Worktrees don't inherit `.venv`**, and `bin/fleet` hardcodes
  `source "$DIR/../.venv/bin/activate"`. Every fresh coordinator worktree
  needs a manual `ln -s <primary>/.venv .venv` before `./bin/fleet` will run
  at all (`ModuleNotFoundError: No module named 'jsonschema'` otherwise). This
  is a one-line workaround but it's not documented anywhere in the README's
  onboarding steps, and it's easy to lose 10+ minutes rediscovering it. A note
  in the README's "Instructions for Agents" section, or a `.gitignore`d venv
  bootstrap step in `bin/fleet` itself, would save every future worker this
  detour.
- **Claim-namespace phrasing drift between the task YAML's prose and the
  binding spec.** T-MIN-025's own scope text describes claim IDs as
  `CO-NN-C-NN` (e.g. `CO-01-C-01`), but the actual binding format spec
  (`SUIT_CARD_FORMAT_SPEC.md` §4) and the sibling Four-of-Coins pilot both use
  `CO04-C01` (no internal dashes). I followed the spec/sibling, not the task
  prose, since the task itself says the spec is binding — but a PM auditing
  future suit-card tasks should double check the scope-text paraphrase
  against the spec before it's copy-pasted into another batch's task file and
  causes a worker to genuinely follow the wrong (nonexistent) namespace.

## Repository-Level Feedback (minchiate_tarot)

**What was done:** Authored the nine remaining Coins pip cards (Ace, Two,
Three, Five, Six, Seven, Eight, Nine, Ten of Coins) to
`research/pilots/SUIT_CARD_FORMAT_SPEC.md`'s light tier, completing the
suit-card pip format rollout across all four suits (Swords T-MIN-022, Batons
T-MIN-023, Cups T-MIN-024, Coins T-MIN-025). Four of Coins (`SUIT-COINS-04`)
was left untouched — it's the suit's pre-existing pilot and the format's
origin card.

**How it was accomplished:** Treated the existing Four of Coins pilot
(`STANDARD_SUIT-COINS-04_Four_of_Coins.md` plus its full dossier
`Pilot1_SUIT-COINS-04_Four_of_Coins.md`) as the closest possible sibling,
since Coins and Cups share round-suit mechanics but Coins-to-Coins is a
tighter match. Verified independently (not assumed by suit-family analogy)
that Coins' round-suit inverse trick order is directly sourced: the Four of
Coins pilot's own dossier opens RULE-1790 cap. II (printed pp. 5–6) as a
direct witness for Coins specifically (claims `CL-SC04-008`/`-009`), so every
new card cites that transcription rather than borrowing it secondhand through
Cups. This is a genuine, independently-checked sourcing chain, not a
transferred assumption — worth noting since the task explicitly asked not to
assume round-suit rules transfer without checking.

Wrote in three waves (Ace/Two/Three, Five/Six/Seven/Eight, Nine/Ten) with a
self-verification pass after each wave: line-count band, unique
`SUIT-COINS-NN` token per file, no court-ID (`SUIT-COINS-11..14`) leakage, and
a grep for forbidden terms. The wave-1 self-check caught a live instance of
the exact stray-second-ID-token bug the Cups batch (T-MIN-024) self-reported:
citing the Four of Coins pilot by its literal ID token (`SUIT-COINS-04`) or
filename inside the new cards' prose would have made the verification
script's `set(re.findall(...))` see two IDs per file and silently skip all
three wave-1 files as invalid. Caught before wave 2 was written, fixed by
switching to purely descriptive references ("the Four of Coins pip", "the
Pilot1 Four-of-Coins dossier") that never reproduce the `SUIT-COINS-\d{2}`
substring, and the fix was carried into every subsequent card from the start.

Also caught and correctly handled a registry-recorded asymmetry: the Five of
Coins row (`SUIT-COINS-05`) carries a specimen-gap note ("card absent or
replaced in BM-1896-0501-34") that no other card in the batch has — recorded
in that card's §1 rather than silently applying the generic six-specimen
baseline to it.

**Verification:** Ran the task's exact `verification_command` locally before
touching the fleet CLI (`OK, found 9 cards`), then ran `./bin/fleet verify`
for real evidence capture (same result, exit 0). Head sha submitted:
`c1fdd61fe45f95441216bec192e67be0dde07f5e` on branch `test-T-MIN-025`, pushed
to `origin/test-T-MIN-025` (not merged to shared `test` — that's a follow-on
step for whoever reviews/merges T-MIN-025, matching the T-MIN-023/T-MIN-024
pattern of a per-task branch rather than a direct push to `test`).

**Cross-suit sanity check (last batch in the format rollout):** confirmed the
nine new claim-ID prefixes (`CO01`, `CO02`, `CO03`, `CO05`–`CO10`) do not
collide with the existing Four of Coins pilot's `CO04-C01`..`CO04-C10`
namespace, and that no two cards in this batch share a prefix.

**Concerns / next steps for the human:** All 56 suit cards' pip tier
(40 of 40 non-Four-of-Coins pips across the four suits, plus the original
Four of Coins pilot) is now written at the light tier. The 16 court cards
across all four suits remain fully out of scope of every one of these four
tasks and are not yet queued anywhere I can see in `tasks/active/` — that's
the natural next PM-scoped batch if the light-tier suit-card project is meant
to reach full 56-card coverage. Also worth a PM's attention: the spec's §6
"Generation and verification workflow" section calls for adversarial
sampling of 3 of 14 cards per suit (one numeral, one court, one random) on
top of the mechanical pass every batch (including this one) has been doing —
I don't believe that sampling pass has happened for any of the four suits
yet, and it's explicitly flagged in the spec as the gate before "Verified"
maturity state is reachable.
