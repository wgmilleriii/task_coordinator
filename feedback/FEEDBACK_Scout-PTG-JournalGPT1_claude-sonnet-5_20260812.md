# FEEDBACK: Scout-PTG-JournalGPT1 (claude-sonnet-5, 2026-08-12)

Scouted `newmexicoptg.org` (JournalGPT) to scope a feature-request-tagging
conversation lane parallel to the existing citation-grounded RAG pipeline.
Wrote `tasks/active/T-PTG-008.yaml`, status `OPEN`. No code was written.

## System-Level Feedback

1. **The `human_review_required: true` + `requires_doc_update: true` combo
   needs a sharper README note for Scouts, not just PMs.** The README says PMs
   "MUST manually add `requires_doc_update: true`" for architectural changes,
   but doesn't say whether a Scout writing an `OPEN` task is expected to
   pre-set it as a hint for the auditing PM, or leave it for the PM entirely.
   I set both flags myself on T-PTG-008 because the feature (a second parallel
   conversation type, plus a cross-repo data handoff design) is clearly
   architectural, but I had to infer that was allowed rather than being told.
   Worth a one-line clarification: "Scouts may pre-set `requires_doc_update`
   as a recommendation; PMs make the final call at audit time."

2. **A quiet YAML footgun in `scope`/`definition_of_done` bullets: a plain
   (unquoted) list-item string containing `: ` (colon-space) anywhere in the
   first line breaks the parse**, and PyYAML's error points at a much later
   line ("could not find expected ':'" two lines after the actual offending
   colon), which cost real time to trace. E.g. `- A multi-turn conversation is
   observable end-to-end: at least 2-3 turns` silently becomes an attempted
   mapping key/value instead of a sequence item. `./bin/fleet lint` and raw
   `python3 -c "import yaml; yaml.safe_load(...)"` both report it, but the
   line number in the error is not the line with the bug. Worth a lint-time
   suggestion in `bin/fleet` ("check nearby lines for a bare colon-space in
   an unquoted scalar") since this will recur — long, prose-style `scope`
   entries are exactly where a stray "X: Y" phrasing creeps in.

3. **`./bin/fleet lint` aborts the ENTIRE store on the first malformed file**
   ("CRITICAL: Store contains malformed YAML. Aborting to prevent data
   corruption") rather than reporting all malformed files it can find. I hit
   a pre-existing unrelated error in `T-INTY-017.yaml` ("Additional
   properties are not allowed ('dod' was unexpected)") that has nothing to do
   with my task and predates this session (confirmed via `git log` — last
   touched by a different agent's commit `8518a48`, and `git status --short`
   after my change shows only `T-PTG-008.yaml` as new/untracked). I could not
   get a clean `fleet lint` pass to confirm T-PTG-008 in isolation and had to
   validate it by hand (`yaml.safe_load` succeeds; schema fields match
   `task.schema.json` by manual inspection since `jsonschema` wasn't
   installed in this environment). A human/PM should fix `T-INTY-017.yaml`'s
   stray `dod` key (probably meant `definition_of_done`) since it's currently
   blocking anyone from getting a full-store lint pass.

## Repository-Level Feedback: newmexicoptg.org

This is the first Scout pass on this repo (no prior `FEEDBACK_*` file
mentioned it, and `.fleet_context.md` confirms Graphify/Chord have never been
run here). A few things surprised me about onboarding a repo the fleet hasn't
touched before:

- **The onboarding docs are unusually good for a first-time Scout.**
  `ARCHITECTURE.md` has an ASCII data-flow diagram that matched the real code
  exactly (`api/ask.php` -> `UsagePolicy::checkAllowance()` ->
  `JournalAnswerService::ask()` -> File Search -> citation resolver -> store +
  return), and `README.md`'s "Mandated Architectural Rules" (PTJ-012 corpus
  grounding, PTJ-013 zero-guessing citations) explained *why* the code is
  shaped the way it is, not just what it does. I didn't have to reverse-engineer
  intent from comments the way I've had to on other first passes — though I
  still read the actual `JournalAnswerService.php` (1447 lines) in full rather
  than trusting the diagram, since the class's own inline comments describe
  several past incidents where reasoning-from-the-diagram-without-reading-code
  produced real bugs (mismatched footnote numbering, wrong offset sign, etc.)
  — this repo has its own internal version of "prefer running over reading."

- **The FTP-deploy-with-no-delete-and-no-`docs`-sync pattern from `intypiano`
  shows up here too**, and it directly shapes what's buildable: I initially
  assumed a Worker could have the production app write task files straight
  into `task_coordinator/tasks/active/`, and `.github/workflows/deploy.yml`
  killed that assumption in about ten seconds — the FTP action explicitly
  excludes `**/.github`, `**/docs`, `**/tasks`, and `**/*.md` from what gets
  synced, and there is no git checkout of a sibling repo on GoDaddy-style
  shared hosting for a live PHP request to write into. I scoped the task
  around a DB-store-then-separate-pull-script pattern instead (feature-request
  conversations land in JournalGPT's own MySQL, and a later CLI script or
  Scout run by a human with both repos checked out turns completed ones into
  fleet task files). This is the single biggest open design question in
  T-PTG-008 and I did not try to resolve it further than proposing the shape
  — that's PM/Worker territory, not Scout territory.

- **`JournalAnswerService.php`'s own changelog-in-comments is worth PM
  attention as a pattern to preserve.** Nearly every non-trivial method has a
  multi-paragraph comment describing a real production bug that method fixes
  (mismatched footnote numbering, an inverted offset sign, boilerplate
  masquerading as a citation, etc.), each with enough detail to explain *why*
  the current code looks unusual instead of simpler. This reads like a
  project that has been through several previous Worker/PM cycles and is
  intentionally keeping decision history close to the code instead of only in
  `task_coordinator`. Recommend PMs auditing future PTG tasks read those
  comments before touching `JournalAnswerService.php` — several of the "this
  looks like it could be simplified" spots are exactly the spots a past
  session already tried the simple version and it broke citations.

- **Recommended next step:** a PM should audit T-PTG-008 with particular
  attention to the tag-detection precision question (first-token-only vs.
  anywhere-in-text) and the quota exemption decision — both are flagged in
  the scope as judgment calls the Scout deliberately did not resolve, because
  getting either wrong changes what a Worker builds and tests against.
