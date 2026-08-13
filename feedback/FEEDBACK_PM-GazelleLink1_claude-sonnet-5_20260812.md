# Feedback: PM-GazelleLink1 (claude-sonnet-5, 2026-08-12)

## Task: T-INTY-019 audit (intypiano)

**Outcome: Audited (OPEN -> AUDITED).** Both stated blockers were independently
re-verified before touching status:

1. **T-INTY-021 (admin/v2 caut_sfusd fatal) — confirmed fixed, not taken on
   faith.** Started `php -S localhost:2027 -t .` on repo-sha 6d955d99,
   logged into the local demo DB, and hit `admin/v2/piano.php` directly for
   a piano with `gazelle_id` set and one with it NULL. Both returned HTTP
   200 with real content and zero occurrences of "caut_sfusd", "Fatal",
   "Uncaught", or "Exception" in either body. Getting to that login required
   more than the documented steps — see System-Level Feedback below.

2. **T-INTY-018 (adds `pianos.gazelle_id`) — the prompt's premise that this
   is DONE was false.** It is `HUMAN_REVIEW` (peer review passed, awaiting a
   human `fleet close`). I did not take the framing at face value; I read
   the YAML directly. This doesn't block *auditing* T-INTY-019 —
   `cmd_audit` in `bin/fleet.py` has no dependency check, only `cmd_claim`
   does — so I audited now to save a round-trip, but flagged in the task's
   scope that `fleet claim` will (correctly) still refuse T-INTY-019 until
   T-INTY-018's status is exactly `DONE`.

3. **Gazelle web URL pattern — re-confirmed genuinely unknown.** Grepped the
   full repo including `classes/integration/GazelleAPI.php` (added by
   T-INTY-020's cited commit) and `admin/v2/normalization.php`. The only
   Gazelle URL anywhere is the private GraphQL API endpoint
   `https://gazelleapp.io/graphql/private` — a machine endpoint, not a
   browser-facing URL. T-INTY-020 (Gazelle sync design, concurrently claimed
   by another Worker while I was auditing) is scoped to the same GraphQL
   API and doesn't touch the web UI either. Rather than leave this as an
   open-ended "confirm before hardcoding" note that a Worker could
   rationalize past, I rewrote the DoD as a hard either/or: either the
   Worker gets explicit confirmation of the real URL and states the source
   in the commit, or they submit nothing and hand the task back with the
   specific blocking question. A guessed URL that silently 404s was called
   out as an explicit non-goal, not just a risk.

## System-Level Feedback

- **`cmd_audit` has zero dependency-status awareness**, which is correct
  behavior (audit != claim), but it means a PM must manually check dependency
  status by hand every time, since the prompt/task text can't be trusted to
  state it accurately (T-INTY-018 was asserted DONE here and was not). Might
  be worth a `fleet status <task>` convenience that prints resolved
  dependency states inline so this isn't a manual YAML read every time.
- **Local auth is currently a trap for anyone following TESTING-LOCALLY.md
  literally.** The 2026-08-11 auth migration moved login to email-based
  lookup against a `users` table with bcrypt, but the demo DB's `users` row
  for `cmiller` has a NULL `email`, and the doc's `tuner.tpassword` MD5 reset
  instructions are for a table the login path no longer primarily checks.
  cmiller/localdev1 fails with "Invalid email or password" until *both*
  `tuner.tpassword` and `users.email`/`users.password_hash` are fixed up.
  Recommend a doc/task to update TESTING-LOCALLY.md and/or seed the demo DB
  correctly — I did not consider this the intypiano-side project's problem
  to silently absorb into T-INTY-019's scope, so I left a note in the task
  instead and did not touch the doc.
- **Lint is currently red for an unrelated reason**: `tasks/active/T-INTY-017.yaml`
  has a `dod` key instead of `definition_of_done`, which fails schema
  validation. Not caused by this session (pre-existing, from an earlier
  commit) and not touched, but worth someone fixing so `fleet lint` is green
  again as a baseline.

## Repository-Level Feedback (intypiano)

- Confirmed `./vendor/bin/phpunit` currently produces `Tests=330,
  Assertions=666, Errors=1, Failures=68` on repo-sha 6d955d99 — neither
  CLAUDE.md's stale 259/0 baseline nor T-INTY-018's captured
  330/564/18/114/6 snapshot. This is *better* than T-INTY-018's snapshot
  (fewer errors/failures), consistent with T-INTY-021 landing in between,
  but still not clean. I recorded this new shape in T-INTY-019's DoD as the
  bar a Worker must not regress below, rather than let them chase unrelated
  pre-existing failures. Recommend someone update CLAUDE.md's baseline once
  the remaining 68 failures are triaged — three different sessions now have
  captured three different counts, which will keep confusing whoever reads
  CLAUDE.md next unless it's refreshed off a clean run.
- `pianos.gazelle_id` (from T-INTY-018's actual code, already in the repo
  even though the task isn't formally closed) is populated and correct in
  `intypiano_demo` — spot-checked `SELECT id, piano_code, gazelle_id FROM
  pianos`, 126 non-null rows match `piano_code` exactly as designed.
