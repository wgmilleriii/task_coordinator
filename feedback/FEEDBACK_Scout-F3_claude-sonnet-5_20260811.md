# Feedback — Scout-F3 (claude-sonnet-5), 2026-08-11 (session 2)

Role: Scout, minchiate_tarot lane. Assignment: mint two OPEN tasks closing a gap that
three independent fleet runs (T-MIN-005 zodiac, T-MIN-011 arie, T-MIN-012 Papi/Fool)
kept surfacing but never actioned: dispositions the authors correctly worked out were
recorded in the study files but never written back into
`research/pilots/Quarantine_Register_Outside_Set_Claims.md`, and T-MIN-012's authors
explicitly deferred reconciling arie-touching edges against T-MIN-011 while it was
unmerged. Minted **T-MIN-014** and **T-MIN-015**.

## System-Level Feedback

- **Both target repos were being actively mutated by other agents during this session.**
  `minchiate_tarot`'s working tree sat on `test-T-MIN-002` (another worker's branch),
  and files under `research/pilots/drafts/` visibly changed content and line counts
  *between consecutive Bash calls in the same session* — a grep that matched at one
  point returned zero matches thirty seconds later with no action from me. I do not
  believe this corrupted my output because I switched to reading everything via
  `git show test:<path>` (the merged branch a fixed ref, not the mutable working tree)
  once I noticed the discrepancy, but a Scout who trusts `Read`/`grep` against the raw
  checkout in a live concurrent fleet can silently cite content that already changed
  under it. Recommend the README's boundary-rule section say explicitly: *for spoke
  repos, read via `git show <ref>:<path>`, never the working tree, unless you are the
  agent that owns that checkout's current branch.*
- The coordinator repo itself showed the same symptom: `git branch --show-current`
  returned `fix/agent-feedback-improvements` on one call and `main` (with `ahead of
  origin/main by 1`, someone else's uncommitted-then-committed work) moments later,
  and `git status` picked up an unrelated modified `tasks/active/T-PTG-001.yaml` and
  three untracked files from another agent's in-flight T-INTY-017 work mid-session.
  I did not touch or stage any of it (verified `git add` only named my two yaml files,
  TASKS.md, and this feedback file), but `./bin/fleet render` unavoidably bakes
  *whatever is on disk* into `TASKS.md` at render time — including other agents'
  uncommitted task files. My committed `TASKS.md` may therefore render a task
  (T-INTY-017) that isn't actually committed anywhere yet. This is a real race: two
  Scouts/PMs rendering and committing `TASKS.md` concurrently will produce
  contents neither of them fully intended. A `fleet render --only-committed` mode,
  or having `render` diff against `git show HEAD:tasks/active/` instead of the working
  tree, would close it.
- Confirmed the previous Scout's (Scout-F2) id-race observation still stands: nothing
  stops two concurrent Scouts minting the same next id. I re-checked archived ids
  manually (T-MIN-004/005/010) before allocating T-MIN-014/015.

## Repository-Level Feedback (minchiate_tarot)

**How the two tasks were scoped.** I did not paraphrase — I read the actual register
(`Quarantine_Register_Outside_Set_Claims.md` L780-1028) to see the existing STATUS-block
pattern (CW-1/2/3/4/8/9 already have one; CW-5/6/7/10 do not; CW-11/12 correctly have
none because no verified study touches Courts/Pips yet), then cross-referenced all four
batch verification reports on `test` (Element, Zodiac, Arie, Papi/Fool), each of which
turned out to contain an explicit "register maintenance queued, out of scope for study
files" note naming exact QC rows and claim IDs (e.g. Arie report: "the register's
QC-077–089, QC-107, and CW-10 entries should gain STATUS/disposition lines citing
STA-C012/…"). T-MIN-014's scope lines quote those citation maps directly rather than
re-deriving them, so a PM/Worker who reads only the yaml still lands on the right rows.
I hand-verified (via `git show test:<path>` since the working tree was unreliable, see
above) that none of CW-5/6/7/10 currently carry a STATUS paragraph and that the named
QC rows currently carry no disposition annotation, and dry-ran the exact
`verification_command` bash logic against that content to confirm it FAILs now (it does,
on the first check: CW-5 has no STATUS line).

For T-MIN-015, I found and quoted the four exact deferral claim IDs the coordinator
prompt named (GAN-C012, RUL2-C012, RUL4-C013, FOO-C014) plus one the prompt didn't name
but is load-bearing: **TRO-C018**, the Trumpets file's own side of the Fool↔Trumpets
question ("left to that batch to offer") — the arie side left this specific edge open
rather than declining it, which is the one case in this pair of tasks where "type the
edge on both sides" is plausible rather than "mutual decline." I also checked all five
arie files for any mention of Ganellino/Papi/Rulers and found none — so the low-block
deferrals (GAN-C012/RUL2-C012/RUL4-C013) most likely resolve as an explicit mutual
decline, and I wrote the scope to say so as a hypothesis while still requiring the
Worker to re-check rather than take my word for it, and forbidding invented edges either
way. I dry-ran T-MIN-015's verification_command against saved copies of the `test`-branch
file content; it correctly FAILs on the current (unresolved) state.

**Concerns / next steps for the human.** (1) Both tasks are mechanical writeback/
reconciliation against already-completed research, hence `human_review_required: false`
— but T-MIN-015's Fool↔Trumpets decision (type vs. decline) is an interpretive call
inside an otherwise mechanical task; if the PM disagrees that's a Worker-level judgment
call, they should tighten the scope further before audit. (2) CW-11 and CW-12 (Courts,
Pips) remain genuinely open in the register — no task should claim to resolve them until
those families get their own personality batches; I deliberately did not include them
in T-MIN-014's scope. (3) The live-concurrency issue above (state changing mid-session
in both repos) is worth a human's attention independent of these two tasks — it suggests
either more agents than the coordinator intends are running against the same checkouts
simultaneously, or checkouts aren't being isolated per-agent (worktrees) the way the
README's Instructions-for-Workers section implies they should be.
