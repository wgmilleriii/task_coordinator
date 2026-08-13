# Feedback — Worker-F26 (claude-sonnet-5) — T-MIN-024 — 2026-08-13

## Task summary

Authored all ten Cups pip cards (`SUIT-CUPS-01` through `SUIT-CUPS-10`, Ace of
Cups through Ten of Cups) to `minchiate_tarot`'s light-tier
`SUIT_CARD_FORMAT_SPEC.md` skeleton, plus
`research/pilots/Cups_Pip_Batch_Verification_Report.md`. Branch
`test-T-MIN-024`, head `309e235672e6bf5db9be45d469e9706207d250eb`, pushed to
`origin/test-T-MIN-024`. `fleet verify` passed locally (audited command found
all 10 cards + report, exit 0); task submitted to `PEER_REVIEW`.

---

## System-Level Feedback (task_coordinator itself)

1. **`fleet verify`/`fleet claim` resolve the target repo relative to the
   *script's own* directory (`BASE_DIR/..`), not cwd.** This means the
   coordinator worktree used for `claim`/`verify`/`submit` must be created as
   a *sibling* of the spoke repo (e.g. `.../GitHub/task_coordinator-verify`
   next to `.../GitHub/minchiate_tarot`), not in a scratch/tmp directory —
   otherwise `verify` fails with "Target repo path does not exist" even
   though the actual spoke repo is checked out correctly elsewhere. I hit
   this: my first worktree (created per the coordinator README's suggested
   pattern, in a scratch directory) worked fine for `claim` but broke
   `verify`, which silently needs the sibling-directory assumption satisfied.
   Recommend either documenting this constraint explicitly in the README's
   "Isolated Worktrees" section, or making `fleet.py` accept an explicit
   `--repo-path` override so agents aren't forced to guess directory layout.
2. **`.venv` isn't portable across worktrees.** `bin/fleet` shells into
   `$DIR/../.venv/bin/activate`, which doesn't exist in a freshly created
   worktree (worktrees share git history, not untracked files like `.venv`).
   I worked around this by symlinking the primary checkout's `.venv` into
   each temp worktree. This is a minor papercut every worker will hit;
   consider either committing a lightweight `requirements.txt`-based
   auto-bootstrap into `bin/fleet`, or noting the symlink workaround directly
   in the README's worktree instructions.
3. **The coordinator README's "HARD REQUIREMENT" (detached worktree from
   `test`, push straight to `test`, never create a new branch) directly
   contradicts the established practice on `minchiate_tarot`**, where every
   prior task (T-MIN-001 through T-MIN-023, all visible in `git branch -a`)
   used a dedicated `test-T-MIN-NNN` branch, and my own task brief explicitly
   instructed the same. I followed the task-brief/established-practice path
   (branch `test-T-MIN-024`, pushed as its own branch) since that's what
   every predecessor task actually did and it's what a PM/reviewer will
   expect to find, but the README should be reconciled with reality — right
   now a new agent reading only the README would do something no other task
   in the repo's history has done.

## Repository-Level Feedback (minchiate_tarot)

1. **The open research question the task flagged — is Cups' round-suit trick
   order actually sourced, or was that assumed by suit-family analogy from
   Coins? — resolves cleanly to "sourced, independently, twice."** RULE-1790
   cap. II (pp. 5–6) inverts numeral order for *both* round suits per the Four
   of Coins pilot's transcription (`CL-SC04-008/-009`), and — critically — the
   existing Cavalier of Cups pilot **independently states the Cups-specific
   application** of the same rule ("the suit runs 10…Ace, then Fantina <
   Cavallo < Regina < Re," `C-CUPS12-002`), naming Cups explicitly rather than
   leaning on suit-family resemblance. That gave me two independent
   transcription chains to cite per card, so every Cups pip's §2 carries a
   fully sourced, non-hedged trick-order sentence — a real contrast with the
   Swords/Batons pip batches (T-MIN-022/023), which had to leave long-suit
   order `[UNVERIFIED]` for lack of any witness transcription. This is worth
   flagging to whoever eventually writes the Coins pips (if that batch
   remains): the same double-sourcing should apply there too, just with the
   Cups pilot supplying the general rule instead of the reverse.
2. **Self-verification caught one real defect before submission, not after.**
   An early authoring pass phrased §2's registry-confirmation sentence as
   "confirmed row-by-row against SUIT-CUPS-01 through -14" in *every* card —
   which silently injected a second `SUIT-CUPS-01` token into cards 2 through
   10. The audited verification script requires exactly one `SUIT-CUPS-NN` id
   per file (`len(ids) != 1` → skip/fail), so this would have failed 9 of 10
   cards silently (the script reports nothing for a skipped file, it just
   never counts it — a worker who doesn't independently re-run the exact
   regex logic could easily miss why "10 cards found" came back as fewer).
   Caught by mechanically re-grepping `SUIT-CUPS-[0-9]{2}` per file rather
   than eyeballing prose. Worth a note for future suit-card batches: **always
   grep your own card-ID regex per file before running `fleet verify`**, not
   just the forbidden-terms list — self-referential registry-range prose is
   an easy way to leak a second ID.
3. Also caught: one boundary-section sentence in the Five of Cups draft used
   the literal word "upright" descriptively (inside a *negative*,
   RWS-exclusion sentence: "no spilled/upright cup trio"). Not a real
   violation of intent (it's describing what the card does *not* show), but
   it's exactly the kind of token a naive grep-based mechanical pass would
   flag, so I reworded it to "toppled-versus-standing" to keep the batch
   clean even under a literal-string check.
4. Recommend next steps for a human/PM: (a) the Coins pip batch (Ace–Ten of
   Coins) is the natural next task if not already scoped — it can now cite
   the Cups pilot's confirmation the same way this batch cited Coins'; (b) if
   a PM ever scopes the Bernardi verzicola boundary reconciliation sweep
   listed in `Bernardi_1790_Verzicola_Boundary_Resolution_Note.md` §5, none
   of this batch's files are on that reconciliation queue (they were authored
   after the note existed and cite it directly), so no follow-up edit is
   needed here.
