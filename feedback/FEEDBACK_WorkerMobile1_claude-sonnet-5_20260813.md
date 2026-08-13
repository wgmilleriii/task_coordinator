# Feedback: Worker-Mobile1 / claude-sonnet-5 / 2026-08-13

## Task: T-PTG-017 — Mobile screen real estate for engine-controls-bar

Status: submitted for PEER_REVIEW. Handoff: `handoffs/T-PTG-017_handoff.yaml`.
Branch `test-T-PTG-017` merged to `main` and pushed (`ebf93f7..1bd4ad4`).

---

## 1. System-Level Feedback (Fleet Coordinator Engine)

**Concurrent-agent collisions in shared checkouts are a real, observed bug — not a
hypothetical.** During this session I hit two distinct forms of it:

1. **task_coordinator's own working tree got clobbered mid-task, twice.** After I
   ran `./bin/fleet claim T-PTG-017`, the on-disk YAML reverted from
   `status: CLAIMED` back to `status: AUDITED, owner: null` *without a git commit
   undoing it* — some other process was writing directly into the same
   `tasks/active/T-PTG-017.yaml` file I was working in. It happened a second time
   between `fleet verify` and `fleet submit`. Both times the fix was "commit my
   change immediately, then git-checkout back to my committed state right before
   the next fleet command" — a race-condition workaround, not a real fix. The
   README's step 2 ("Commit this claim to Git immediately") is clearly there
   *because* this is a known hazard, but the CLI itself doesn't enforce or even
   detect the collision — `fleet claim` happily reports success even though
   another live process can silently undo it seconds later. Recommend: `fleet
   claim`/`verify`/`submit` should re-read the file immediately before writing and
   fail loudly (not silently "succeed") if the on-disk state doesn't match what was
   just read, the same way optimistic-locking systems do.

2. **The newmexicoptg.org spoke repo checkout is also shared across concurrent
   agents**, and this one was worse: another process (evidently working on the
   JournalGPT v3 track — T-PTG-018 through T-PTG-026) committed directly onto
   *my* checked-out branch (`test-T-PTG-017`) while I was mid-task. I found a
   commit "Add JournalGPT v3 Phase 0 benchmark" sitting on top of my own commit,
   adding `generate_benchmark.py`, `journalgpt/v3/benchmark.md`,
   `journalgpt/v3/v3.md`, and a 5744-line `logs.json` — none of which belonged
   in my PR. I had to `git reset --hard` my own commit off that contamination,
   then manually restore the other agent's files back to disk as untracked
   content (via `git checkout <bad-commit> -- <paths>` + `git restore --staged`)
   so their in-progress work wasn't lost, before merging my *actual* diff (just
   the CSS file) to `main`. This worked out fine here because I caught it before
   pushing, but it's exactly the kind of thing that silently corrupts a PR if an
   agent doesn't double-check `git diff main..branch --stat` before merging.
   Recommend: the fleet should allocate each claimed task its own git worktree
   (`git worktree add`) rather than relying on agents happening to `cd` into a
   shared checkout — the README already mentions this as an option ("If you know
   how, prefer using `git worktree add`") but doesn't require it, and this session
   is a concrete example of why it should.

3. **`fleet lint`/`fleet verify` do full-store YAML validation and abort on ANY
   malformed task file, even ones with zero relation to the task being worked.**
   I hit `T-PTG-022.yaml` and `T-PTG-023.yaml` failing to parse (unquoted strings
   containing `: ` mid-scalar — a classic YAML gotcha, e.g. `- A new test file
   (...) covers at least: a redundant/duplicate...`) which blocked `fleet verify`
   for T-PTG-017 entirely via the "CRITICAL: Store contains malformed YAML.
   Aborting to prevent data corruption" guard. I fixed both by wrapping the
   offending list items in single quotes (pure syntax fix, no semantic change) so
   the store would parse again. This unblocked me, but it means a single
   careless YAML edit by any agent (or by whatever auto-generates these scope/DoD
   blocks) can halt every other agent's `verify`/`submit` fleet-wide until someone
   notices and fixes it. Recommend: a schema/lint pre-commit hook on
   `tasks/active/*.yaml` so malformed YAML never lands in the first place, and/or
   have `fleet verify <task-id>` only strictly validate the one task file it's
   operating on (a warning for others, not an abort).

4. Also saw `T-INTY-017.yaml` fail `fleet lint` with `Additional properties are
   not allowed ('dod' was unexpected)` — a different task, different repo,
   pre-existing before my session, untouched by me. Flagging in case nobody's
   tracking it.

---

## 2. Repository-Level Feedback (newmexicoptg.org / JournalGPT)

**What I found and fixed:** `journalgpt/index.php`'s `.engine-controls-bar` (the
row containing Preset buttons, "Thinking Tier" dropdown, and "Theme" dropdown,
just above the question textarea) had **zero mobile handling** despite living a
few lines away from a fully-responsive `@media (max-width: 768px)` block in
`journalgpt/assets/journal-chat.css`. Confirmed via `/browse` at a real 375px
viewport, logged in as a test user against the local `journal_ai_test` DB:

- **Before:** `document.body.scrollWidth` = 620px on a 375px viewport — the page
  had ~245px of horizontal overflow, entirely driven by `.engine-controls-bar`
  (measured at 596px wide) trying to fit three flex items
  (`justify-content: space-between`) on one line with no wrapping and no
  shrink allowance.
- **After my fix:** `document.body.scrollWidth` = 375px exactly. Zero horizontal
  scroll.

**The member feedback this addresses** — conversation_id=53, `/featurerequest`
triage lane, quoted verbatim from the task's scope block:
- idea: **"better mobile support"**
- who/context: **"for when you're in the car"**
- how_often: **"once a week"**
- what_it_would_look_like: **"better screen real estate management"**

This is a low-frequency, quick-glance mobile use case (once a week, in a car) —
not sustained mobile work. The engine-controls-bar sits directly above the
question input, so it's one of the first things visible on every mobile page
load. Before this fix, that row alone pushed the *entire page* into horizontal
scroll on a phone, meaning even the greeting/instructions text and the question
textarea were partially off-screen and had to be scrolled sideways to read fully
— about as literal an example of "wasted screen real estate" as a member could
describe without knowing CSS. My fix directly targets that: the row now wraps,
each dropdown gets its own full-width line with a clear label, and nothing on
the page requires horizontal scrolling anymore. For a once-a-week glance from a
car, "open the app, tap Send, no fighting with sideways-scrolling controls" is
exactly the win described.

**My design call and why:** I stacked `.model-select-group` and
`.theme-select-group` into their own full-width rows (`flex: 1 1 100%` +
`flex-wrap: wrap` on the parent) rather than going icon-only/abbreviated-label,
because (a) it required no changes to `index.php` markup at all — pure CSS,
lowest risk — and (b) it keeps the existing text labels ("Thinking Tier:",
"Theme:") fully legible instead of introducing new iconography a once-a-week
user would have to relearn. Both `<select>` elements get `min-height: 44px`,
matching the existing `.sidebar-toggle-btn` convention in the same media query.

**The non-obvious part of this fix, worth flagging for future CSS work here:**
just wrapping `.engine-controls-bar` and capping the `<select>` width wasn't
enough to actually reach 375px with zero overflow. The real root cause was one
level up: `.main-chat-panel` is a flex child of `.app-container`
(`display: flex`), and flex items default to `min-width: auto`, which blocks a
flex child from shrinking below the *min-content* width of its own descendants.
Since nothing in the existing codebase had ever set `min-width: 0` anywhere in
this flex chain, `.main-chat-panel` was refusing to shrink below whatever its
widest descendant wanted — which, before my fix, was the unwrapped
596px-wide `.engine-controls-bar`. I added a single `min-width: 0` to the
existing `.main-chat-panel` mobile rule (already present in the same media
query for `height`/`max-height`) to fix this. **This same latent bug likely
affects any other wide/unwrappable content added to the chat panel in the
future** — worth a proactive follow-up task to audit the rest of the flex chain
(`.app-container` → `.main-chat-panel` → children) for other `min-width: auto`
landmines, rather than re-discovering this one class at a time.

**Verification performed:**
- `php -l journalgpt/index.php` — clean.
- Full existing suite (`AskEndpointTest.php`, `UsagePolicyTest.php`,
  `JournalAnswerServiceTest.php`) — all passing, 0 regressions.
- `/browse` screenshots at 375px (before/after) confirming the overflow fix and
  both dropdowns functional (`select` commands actually changed `#tierSelect`
  and `[data-theme-picker]` values, confirmed via `.value` reads).
- `/browse` screenshot at 1280px confirming desktop layout is byte-for-byte
  unchanged (computed `flex-wrap: nowrap`, `flex-basis: auto` at that width —
  the media query simply doesn't apply, as expected).
- `/browse` spot-checks confirming other mobile rules in the same media query
  (`.sidebar-toggle-btn` 44px target, `.chat-header` padding, `.messages-container`
  padding, `.btn-send` min-height) were untouched and still correct.

**Recommended next steps for the human:**
1. Peer review this diff — it's small (32 lines, one CSS file) and self-contained.
2. Consider the `min-width: auto` flex-chain audit mentioned above as a small
   follow-up task before more content gets added to `.main-chat-panel`.
3. No automated feature-request → fleet-task conversion script exists yet
   (confirmed absent from `journalgpt/cli/` by the Scout on this task) — this is
   the first request to go through that pipeline and get shipped; worth
   building that script if this triage lane keeps producing real, actionable
   requests.
