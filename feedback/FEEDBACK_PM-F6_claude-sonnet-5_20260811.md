# Feedback — PM-F6 (claude-sonnet-5), 2026-08-11

Role: PM, minchiate_tarot lane. Assignment: audit the two OPEN tasks Scout-F3 minted
this session — T-MIN-014 (Quarantine Register disposition writeback for CW-5/6/7/10
and their QC rows) and T-MIN-015 (reconcile the Papi/Fool batch's deferred arie edges,
including TRO-C018). Both AUDITED against `test` HEAD `19c26db`.

## System-Level Feedback

- **Confirms the "read via `git show <ref>:<path>`" recommendation from Scout-F3's
  feedback.** I onboarded into a checkout that, per the boundary rule warning, other
  agents were actively mutating (`.fleet_context.md` and an `INITIAL_VISION/` directory
  appeared untracked in the minchiate_tarot working tree; the coordinator repo carried
  uncommitted `T-PTG-*.yaml` edits, a stray `T-INTY-017.yaml`, and orphaned handoff/review
  files from other agents mid-session). I verified my working directory's copy of
  `Quarantine_Register_Outside_Set_Claims.md` matched `git show test:<path>` byte-for-byte
  before trusting it (`git diff test -- <path>` was empty), but did all dry-run
  fixture-editing in scratch copies under `/private/tmp/...`, never in the real
  checkout, specifically to avoid adding my own noise to an already-mutating tree.
  Seconding the ask: the README's boundary-rule section should say explicitly to
  diff the working tree against the target ref before trusting `Read`/`grep` output,
  every time, not just when a discrepancy is noticed.
- **`fleet lint` reports a real schema violation on another lane's task
  (`T-INTY-017.yaml`, unexpected `dod` property)** that is not mine to fix (outside
  the minchiate_tarot lane, uncommitted, presumably another agent's in-flight Scout
  output). I left it untouched per the boundary rule and only verified my own two
  files pass. A `fleet lint --paths <glob>` or `--lane` flag would let a PM confirm
  "my files are clean" without the overall lint exit code being polluted by
  concurrent agents' in-progress work — as it stands, a PM has to manually read past
  unrelated errors to confirm their own files, which is exactly the kind of
  cross-lane noise the README says to ignore but the tooling doesn't help filter.
- **`audit` has no dry-run/verify-now mode.** I had to hand-build scratch fixtures
  (copy the real file content out via `git show`, then Python-patch it to a
  "DoD satisfied" state) to prove each `verification_command` is fail-red today and
  pass-green once the DoD is genuinely met, entirely outside the CLI. A
  `fleet audit --dry-run <task_id>` that ran the candidate command against the
  current repo state and printed pass/fail (without unlocking) would let a PM
  confirm the fail-red half in one command instead of a hand-rolled harness.

## Repository-Level Feedback (minchiate_tarot)

**T-MIN-014 — AUDITED.** Read the full task YAML and the register
(`research/pilots/Quarantine_Register_Outside_Set_Claims.md`, via `git show
test:<path>`) end to end. Spot-checked more than the required 3: confirmed CW-1,
CW-2, CW-3 (deliberately left "UNRESOLVED" — Justice's null personality layer, a
correctly-absent STATUS block that is not a bug), CW-4, CW-8, and CW-9 all carry
`**STATUS — ...**` paragraphs, and that CW-5, CW-6, CW-7, and CW-10 currently carry
none (CW-11/CW-12 correctly also have none — no verified study touches Courts/Pips).
Verified all four cited resolving claim IDs exist with the described content:
`FOO-C007` (Fool file, CW-5 split disposition), `AIR-C006` (Air file, CW-6
mode-of-energy replacement), `FIR-C017` (Fire file, owns the CW-6/QC-060 Death-edge
sub-disposition cited by the other three elements), and `TRO-C012` (Trumpets file,
CW-10 "summons" contaminant withdrawal). Also independently confirmed the Zodiac
Batch Verification Report's L127/L232 region documents the twelve-card CW-7
disposition sweep the scope describes. Tightened nothing in the scope text (Scout-F3's
citation map was already accurate on inspection) but did validate the
`verification_command` is genuinely fail-first: dry-ran it verbatim against a scratch
copy of the actual `test`-branch register and it failed immediately (`FAIL: CW-5 has
no STATUS line in register`), then built a synthetic fixture with STATUS
paragraphs inserted for all four CWs and disposition annotations appended for all
named QC rows and confirmed the identical command exits 0 with `PASS` — so the
command discriminates real completion from the current state rather than being
vacuously true. Audited against `test` HEAD `19c26db` with the command unchanged
from Scout-F3's draft (it was already tight).

**T-MIN-015 — AUDITED.** Confirmed all four deferral claim IDs exist with the exact
deferral language Scout-F3 quoted: `GAN-C012` and `RUL2-C012` ("arie batch in
flight (T-MIN-011), reconciliation deferred"), `RUL4-C013` ("no committed text to
reconcile against"), `FOO-C014` ("arie batch in flight (T-MIN-011, unmerged)").
Confirmed `TRO-C018` in `PERSONALITY_TRUMP-40_Trumpets.md` reads "left to that batch
to offer" — a live invitation, not a decline, matching the scope's framing. Verified
T-MIN-011 is in fact merged to `test` (all five arie files, TRUMP-36 through
TRUMP-40, present at `19c26db`) and independently re-ran the scope's claim that none
of the five arie files assert a Ganellino/Papi/Ruler edge — confirmed by grep, each
of the five explicitly states "No typed edges to ... *papi* ..." — which supports
Scout-F3's mutual-decline hypothesis for the low-block claims without treating it as
settled (the task correctly still requires the Worker to re-verify, not just take the
scout's word). Dry-ran the `verification_command` against the real `test`-branch
content of all five target files: it failed immediately and correctly
(`FAIL: ... Ganellino.md still carries an unresolved arie deferral`). Built a
synthetic "resolved" fixture and found a real gap in my first patch attempt: the
deferral language appears **twice** in each of Ganellino/Ruler-02/Ruler-04 — once in
the claims table row, once in a separate Sec.3 prose sentence ("**The *arie*: no
typed edge — arie batch in flight, reconciliation deferred.**") — and a fixture that
only fixed the table row still correctly failed the command. Only after patching both
occurrences in all three files, typing the Fool/Trumpets edge in both `FOO-C014` and
`TRO-C018`, and removing "left to that batch to offer" did the command pass. This is
a good sign for the command's rigor (it would have caught a Worker who patched only
the claims table and left the prose stale) but worth flagging explicitly for whichever
agent claims this: **the deferral language exists in two places per file for
Ganellino/Ruler-02/Ruler-04 — check Sec.3 prose, not just the claims table.** I did
not edit the task's scope text since it doesn't need to (a Worker who reads the source
files, as instructed, will find both occurrences). Audited against `test` HEAD
`19c26db` with the command unchanged from Scout-F3's draft.

**Concerns / next steps for the human.** (1) Neither task's premises showed any
conflict or fabrication — Scout-F3's citation maps were accurate on independent
re-derivation, which is a good sign for scout output quality in this lane. (2) T-MIN-015's
Fool/Trumpets typing decision remains a Worker-level interpretive call bounded by an
explicit anti-invention clause; I did not pre-decide it for the Worker, consistent
with Scout-F3's framing. (3) The concurrent-mutation problem both Scout-F3 and
Worker-F14 flagged is still live — I saw the same symptom (untracked files
appearing in the minchiate_tarot working tree, uncommitted sibling-lane task files
in the coordinator repo) this session. I did not lose any work because I never
trusted the raw working tree for content I was about to certify, but this is now the
third independent report; worktree isolation per agent (as previously suggested)
would remove the need for defensive re-verification before every command.
