# Feedback — Reviewer-F15 (claude-fable-5), 2026-08-11

Session: peer review of T-MIN-009 (zodiac classical-source locator resolution), minchiate_tarot lane. Verdict: PASS; the task auto-closed to DONE on record-review (human_review_required: false).

## System-Level Feedback

1. **record-review skips HUMAN_REVIEW when `human_review_required: false`.** The README's lifecycle diagram presents HUMAN_REVIEW as a mandatory stage ("PEER_REVIEW -> HUMAN_REVIEW -> DONE"), but `record-review` moved T-MIN-009 straight to DONE. That is presumably intended behavior for the flag, but the README never mentions the shortcut; a reviewer expecting to hand off to a human gets a surprise state transition. Document it, or have the CLI print which path it took and why.
2. **The review template's default verdict is FAIL with a REQUIRED_PLEASE_FILL finding.** Good fail-safe design — an unedited template cannot accidentally pass a task. Worth keeping.
3. **The shared coordinator checkout is a hazard at commit time.** At my commit, the working tree contained roughly fifty uncommitted files from other agents (a full T-INTY-* archive migration, deletions of four other review files, stray `test.py` and `logs/`). Any reviewer who runs `git add -A` out of habit will commit another lane's half-finished state. A `fleet commit --paths ...` wrapper, or per-lane staging guidance in the README, would remove the foot-gun.
4. **`start-review` has no worktree guidance.** The isolated-worktree discipline (never move the shared spoke checkout off its branch) lives only in dispatch prompts. It belongs in the README's reviewer section; a reviewer who checks out the head SHA in the shared clone will break concurrent workers.
5. **Task YAML remains in `tasks/active/` after DONE.** T-MIN-005/-010 were archived by someone else's uncommitted move, while T-MIN-009 is DONE but still active-side. Whatever the intended convention is, the CLI should perform the archive move itself so the tree cannot drift into both patterns at once.

## Repository-Level Feedback

**How the work was verified, not just what.** T-MIN-009 claimed to resolve every hedged classical locator in the twelve zodiac studies against opened editions. Because this project's citation audit found 208 untraceable references, I treated "looks resolved" as the enemy and re-opened the sources myself from the worktree at f8bb1b8:

- *Tetrabiblos* I.13 and I.17 at the exact LacusCurtius URL in the resolution note — I.13 is genuinely the aspects chapter (opposition as the diameter, 180 degrees), I.17 genuinely assigns Leo to the sun and Cancer to the moon, with the note's quotations verbatim.
- Isidore *Etymologiae* III.71 at LacusCurtius — 71.29 carries the Libra day-equals-night Latin word for word ("Libram autem vocaverunt ab aequalitate mensis ipsius... aequinoctium facit"); 71.32 (Aquarius rains), 71.25 (Castor/Pollux), 71.26 (Cancer) all check.
- Aratus via the Scaife passage API — line 89 has the mighty Claws, 96-97 the Parthenos with the gleaming Stachys, 546 the "Chelai kai Skorpios autos" sign-list. The worker's line numbers are the edition's own references, not approximations.
- Hyginus 2.22 at Topostext — the exact sentence the Gemini study quotes.

Every reopened locator bore its claim; zero new untraceable references entered the corpus. Equally important, the two DOWNGRADES are honest: Pisces' contrary-swimming convention and Taurus' forepart/georgic glosses were weakened to bare [UNVERIFIED] in prose, claims table, §4, and §5 alike, with the note explaining what the opened sources actually say instead. The six diametrical opposite edges were upgraded symmetrically (checked Scorpio SCO-C014 vs Taurus TAU-C011 end-to-end; grepped the grading on the other five pairs). The audited verification command passes in the worktree, and the diff touches exactly the 13 in-scope files.

**Lessons learned.** The Scaife passage API is the right instrument for line-precision Greek citations — it returns per-line text keyed to the edition's own numbering, which removes the translation-offset ambiguity that plagues Theoi/Mair-based citations (Theoi also 403s). LacusCurtius asterisk URLs fetch fine. The one blemish found was cosmetic: the note's Scorpio row says "Aratus 89, 545-546" where the Claws sit on 546 alone; the studies themselves cite 546 correctly, so nothing needed correction.

**Concerns and next steps.** (1) The zodiac batch is now doctrinally sourced but still G2-blocked deck-wide on IMG-001 — every iconographic claim is scaffolding until verified crops exist; that is the real bottleneck for gate passage. (2) The Sacrobosco citations remain chapter-level ("cap. II" section names in Thorndike), which the studies grade honestly, but a future pass could pin Thorndike page numbers. (3) The pattern this task establishes — hedge in the study, resolve in a dedicated locator task against opened editions, log a resolution note — is exactly the discipline that prevents another 208-reference audit failure; recommend it be written into the research brief as the standing rule for all future personality studies.
