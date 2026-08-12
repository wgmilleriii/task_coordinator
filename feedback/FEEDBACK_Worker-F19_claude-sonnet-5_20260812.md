# Feedback — Worker-F19 (claude-sonnet-5), 12 August 2026

**Task:** T-MIN-018 (minchiate_tarot) — resolve the Bernardi 1790 verzicola boundary via
direct archive.org access before falling back to human acquisition.

**Note on this session:** this task was resumed after an earlier instance of Worker-F19 was
killed by a connection error mid-research, before writing anything to disk or making any
commit. Confirmed on resume that branch `test-T-MIN-018` was still at the unmodified base
`09f857d` with zero commits and zero uncommitted local changes — the crash left no mess to
clean up, consistent with the coordinator's "Subagents die cheaply" safety note. The dead
instance's last message ("Good, confirms the RULE-1790 identity matches...") was treated as
an unverified claim, not fact, and the archive.org identity check was redone from scratch
rather than trusted.

---

## System-Level Feedback

1. **`WebFetch`'s AI-summarization pass is unsafe for exact-transcription tasks.** The tool
   description says it "converts HTML to markdown" and "processes the content with the
   prompt using a small, fast model." For a task requiring verbatim transcription of 18th-
   century OCR text with exact numerals, this is actively dangerous: my first WebFetch call
   against the djvu.txt derivative returned a *paraphrased summary* dressed up as quotation
   (fabricated-looking chapter breakdowns, invented section labels like "Definition and Basic
   Rules (Cap. V)" that do not appear in the source, and at least one clearly wrong page
   number). It read as confident and citation-formatted, which is exactly the failure mode
   most likely to get trusted and copied verbatim into a research note. I caught it only
   because the task's own instructions demanded exact locators, which made me cross-check the
   summarization pass against raw bytes. I switched to `curl` via the Bash tool to pull the
   raw `djvu.txt` (63.5 KB, 2,416 lines) and read it directly with line numbers, which is what
   actually let me transcribe safely. **Recommendation:** any future task instructing an agent
   to "transcribe exactly" or "quote verbatim" from a fetched web source should explicitly warn
   against trusting WebFetch's summarized output for that purpose, or should explicitly permit/
   require raw retrieval (curl, or a WebFetch prompt that asks for a byte-range echo rather
   than an interpretation) as the actual transcription-grade method. The Zodiac_Locator note
   this task was modeled on doesn't flag this risk either, and probably should.
2. **archive.org's download redirect target is non-deterministic per request** (observed both
   `dn760106.eu.archive.org` and `dn710907.ca.archive.org` for the identical URL on different
   requests, minutes apart). Not a coordinator defect, but worth knowing if any future task
   hardcodes a specific node hostname as a "confirmed" locator — it will rot. Cite the
   `archive.org/download/...` canonical URL, never the redirect target, as the stable locator.
3. **Shared `main` in `task_coordinator` had other agents' staged-but-uncommitted changes**
   (`tasks/active/T-MIN-016.yaml`, `reviews/T-MIN-016_review.yaml` already `git add`-ed; several
   `T-PTG-007`/`T-PTG-008` files untracked) sitting in the working tree when I went to commit.
   I used `git commit <pathspec>` (listing exactly `tasks/active/T-MIN-018.yaml
   handoffs/T-MIN-018_handoff.yaml TASKS.md`) rather than a bare `git commit -a` or `git add -A`,
   which committed only my files and left the others' staged/untracked state untouched and
   intact for them to commit themselves. This worked cleanly, but it's easy to get wrong — a
   worker following the README's literal "commit handoff+yaml+TASKS.md" instruction with a
   careless `git add .` would have force-committed another agent's in-progress review on their
   behalf. Worth calling out explicitly in the README's git-discipline section: **always commit
   by explicit pathspec on shared branches, never `git add -A`/`git commit -a`.**

## Repository-Level Feedback (minchiate_tarot)

**How the task was actually accomplished:** Followed the task's mandatory attempt sequence in
order. (a) `GET https://archive.org/metadata/bub_gb_4_rdG3SVa48C` → HTTP 200, confirmed the
item's title/creator/date match Bernardi 1790 exactly and enumerated available derivatives
(`_djvu.txt`, `.pdf`, `_abbyy.gz`, `_djvu.xml`). (b) Followed the confirmed `_djvu.txt`
filename via `archive.org/download/...` → HTTP 302 to a load-balanced content node → HTTP 200,
63.5 KB of raw OCR retrieved via `curl` (not WebFetch's summarizer, see System-Level feedback
above) and inspected line-by-line. (c)/(d) not needed — (b) succeeded outright, so I did not
need the details page or a WebSearch fallback. Total direct-access time was a few minutes;
the "human must acquire it" fallback in T-MIN-008 turned out to be unnecessary.

The OCR text is legible and internally consistent enough to resolve the specific hedge cleanly:
Bernardi's own table of contents gives exact printed-page locators for Cap. V ("Delle
Verzicole regolari," p. 9) and Cap. VI ("Delle Verzicole irregolari," p. 11), and three
independent passages (Cap. V's worked examples, Cap. XV's strategy discussion, and a fully
worked scoring dispute in Part II Cap. VIII) all agree that the upper-range verzicola boundary
opens at **XXVIII (28), never XXVII (27)** — the one place XXVII appears near this context, it
names an unrelated low-value discard card, not a verzicola opener. That resolves the "one
numeral below" ambiguity the zodiac batch had flagged as its sharpest open point. The
element batch's separate question — whether XX–XXIII can form a verzicola — is *not* fully
resolved by a named example (Bernardi's concrete examples genuinely skip that span), but I was
able to narrow it precisely: Bernardi's own general rule ("three or more cards in sequence")
textually covers it with no stated exception, so the honest status is "covered by the general
rule, unconfirmed by named example," which is more specific than the prior blanket "unchecked."
I deliberately did not upgrade this to "resolved" — the task's method model (T-MIN-009's note)
is explicit that unattested claims stay `[UNVERIFIED]` rather than get inferred into fact, and
I held that line here even though I think the general-rule argument is fairly strong.

**Deliverable:** `research/pilots/Bernardi_1790_Verzicola_Boundary_Resolution_Note.md` on branch
`test-T-MIN-018` (head `2b48367`), containing the full attempt log, verbatim chapter
transcriptions with locators, the exhaustive-vs-exemplary finding (exemplary — Bernardi's own
"per esempio... ec." framing says so explicitly), and a reconciliation queue of ~20 files
(Justice pilot, both zodiac/element batch briefs and verification reports, four element
personality drafts, the Ruler guidebook drafts, the fleet sweep triage report, etc.) with
line-level references, listed but **not amended** — per this task's scope, applying those
amendments is left for a separately-scoped PM/human decision. `./bin/fleet verify` passed on
the first try; handoff filed at `handoffs/T-MIN-018_handoff.yaml`; task submitted to
`PEER_REVIEW`.

**Concerns / recommended next steps for the human:**
1. T-MIN-008 is still `OPEN` and unaudited, and now carries a stale assumption (that human
   acquisition is required) that this task's note explicitly supersedes. Recommend a PM either
   closes/archives T-MIN-008 or re-scopes it now that direct access is proven to work — leaving
   both open invites a future agent to redo the same manual-acquisition legwork unnecessarily.
2. The reconciliation queue this note produced is sizeable (~20 files, some already-committed
   personality studies). Recommend scoping it as its own audited task rather than folding it
   silently into a future unrelated task — the queue mixes "just update a hedge sentence" edits
   (zodiac/element batch reports) with "this is the load-bearing citation of a committed claim"
   edits (Justice pilot L92 itself), and those probably deserve different review weight.
3. The XX–XXIII general-rule-but-no-named-example finding is a genuinely new, narrower category
   of uncertainty that didn't exist in the corpus before this note. Whoever picks up the
   reconciliation queue should preserve that distinction rather than flattening it to a plain
   "yes" or "still open" when updating the four element personality files.
