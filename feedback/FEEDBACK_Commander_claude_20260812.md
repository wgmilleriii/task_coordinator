# Fleet session feedback — T-INTY-018 (business-card QR sheet, intypiano)

**Agent:** Commander (Fleet Coordinator, acting also as PM and Worker)
**Date:** 2026-08-12
**Task:** T-INTY-018 — Avery 8371 business-card QR sheet as a second QR report
**Spoke branch:** `intypiano@claude/qr-report-business-cards-bq6mb2`
**Final task state:** CLAIMED (not submitted — see "Why this task is not at PEER_REVIEW")

---

## System-Level Feedback

### 1. `bin/fleet` is unusable on a fresh checkout — the venv is not part of setup

`bin/fleet` is a bash wrapper that unconditionally sources `../.venv/bin/activate`.
A fresh clone has no `.venv`, so **every** fleet command dies before reaching
`fleet.py`:

```
./bin/fleet: line 3: /home/user/task_coordinator/bin/../.venv/bin/activate: No such file or directory
ModuleNotFoundError: No module named 'jsonschema'
```

The README's step 3 says "install the exact dependencies via `pip install -r
requirements.txt`" but never says to create the venv the wrapper requires. Every
agent dispatched to a clean container has to rediscover this. Two fixes, either
is fine:

- Have the wrapper create the venv on first run if it is missing, or
- Make the wrapper fall back to the system interpreter when `.venv` is absent,
  and say `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
  in the README's startup steps.

### 2. An audited task's `verification_command` cannot be corrected

`audit` rejects any task that is not `OPEN`, so once a task is `AUDITED` its
verification command is frozen. If the command turns out to be wrong — wrong
cwd, wrong flag, a missing environment prerequisite — there is no forward path.
The only options are hand-editing the YAML (which `AGENTS.md` forbids) or
cancelling and recreating the task, which throws away its event history.

This bit this task. The audited command is `./vendor/bin/phpunit --filter
QrCardSheet`, which is correct for a properly configured intypiano dev box and
wrong for a default PHP 8 container (see repository feedback #1). I left it
alone rather than edit an audited field.

Suggest a `fleet re-audit <id> --command ... --auditor ...` that appends a
`RE_AUDIT` event and requires the task to be in `AUDITED` or `CLAIMED`.

### 3. `verify` runs the command but the environment contract is undeclared

`cmd_verify` shells out with `cwd=<sibling repo>` and a 5-minute timeout. There
is nothing in the task schema that records what the command *needs* — a
database, a dev server, a PHP ini flag, a built venv. So a red `verify` cannot
be distinguished from a red *codebase*, which is the single most expensive
ambiguity in an autonomous fleet: it invites an agent to "fix" working code.

Suggest an optional `verification_requires: [...]` array on the task, echoed by
`verify` before it runs, and a distinct exit path for "prerequisite absent" vs
"assertions failed".

### 4. Verification is a single command, so partial evidence has nowhere to go

A `verification_command` is one string with one exit code. This task produced
evidence in three layers — `php -l` on eight files, a 12-test phpunit filter,
and a 300dpi rasterise-and-decode of the generated PDF — and only the middle
one fits the field. The strongest evidence I have (all 11 QR codes decoded back
to their expected URLs) is not representable in a handoff.

Suggest allowing `verification_command` to be a list, with the handoff
capturing one block of terminal evidence per entry.

### 5. `feedback/` filenames encode a model identifier

The convention is `FEEDBACK_<Agent>_<Model>_<Date>.md`. I have filled the model
slot with the lane name (`claude`) rather than a specific model id, because the
harness I run under forbids writing its model identifier into repository
artifacts. If the fleet wants model attribution to be reliable, it should come
from a field the CLI writes (it already stamps `--model` into the global event
log) rather than from a filename an agent types by hand.

---

## Repository-Level Feedback (intypiano)

### How the work was actually done

The ask was "a new QR report optimized for business card size". The first job
was working out what "QR report" names in this repo, because there are three
candidates and two of them are traps:

- `qr_report_generator.php` — documented at length in `PIANO_QR_FEATURES.md` and
  **dead**. It calls `mysql_fetch_assoc()` (removed in PHP 7), reads the frozen
  v1 `inventory` table, and gates on the client-set `istuneradmin` cookie. Its
  `?format=pdf` branch is a `TODO` that silently falls back to HTML. Anyone who
  starts from the documentation will start from this file. It is a good
  candidate for deletion or a header saying so.
- `qr_avery5162_poc.php` — a proof of concept still sitting in the web root.
- `print_labels_5162.php` — the real, working, v2-native one, rebuilt 2026-08-07.

I built on the third and left the other two alone. The new sheet mirrors it
exactly on the things that must not diverge (v2 `pianos` + `locations` source,
session gate, `?building=` filter, `schedule_tuning.php?qr=` scan target) and
differs only in geometry and in what fits.

The layout went into `classes/core/qr_card_sheet.php` rather than into the
endpoint. That was the highest-leverage decision in the task. The endpoint needs
a session and a database, so a test that drives it over HTTP skips whenever
either is missing — which is exactly what `QrLabelsTest` does, and CLAUDE.md
already records that a skipped test guards nothing. With the drawing in a plain
function, `tests/Integration/QrCardSheetTest.php` renders real PDFs from fixture
rows and runs anywhere: 12 tests, 35 assertions, no database, no dev server.

Then I actually looked at the output, which is where the value was:

1. Rendered an 11-row sheet with deliberately hostile data — a 43-character
   model, a 40-character building name, a piano with no location, one with no
   serial, one with no code — and rasterised it at 110dpi to read.
2. Rasterised again at 300dpi and ran every QR through a decoder. All 11 came
   back as `https://unm.cauttools.com/frontend/schedule_tuning.php?qr=<key>`.
   A QR report whose codes do not scan is worthless, and this is the only way to
   know they do.

The visual pass found a defect that reading would not have: the serial-only
instrument headlined `#3`, its internal database row id, while the QR beside it
encoded the serial `J1099233`. Two identifiers on one card, neither matching,
and the id meaning nothing to the person holding it. The headline is now the
scan key itself, and the `SN` line is suppressed when it would merely repeat it.

One more thing worth naming: `print_labels_5162.php` hardcodes
`https://unm.cauttools.com/`. That is fine for a label a technician scans on
campus and wrong for a card that goes in a wallet, so the card derives its base
from the tenant's `siteUrl`. `DatabaseManager` sets that inconsistently — http
for most tenants, https for the demo pool, and a bare `SERVER_NAME` with no
scheme at all on the fallback branch — so `qr_card_base_url()` normalises all
three to absolute https. A printed card cannot be reissued when a tenant gets
TLS.

### 1. CONCERN: the whole phpunit suite is red on `master` for an environment reason

On a default PHP 8.4 container, on clean `master` (`3cf4775d`), `phpunit` does
not run a single test:

```
PHP Fatal error: Uncaught ParseError: Unclosed '{' on line 535 in
classes/core/BookingManager.php:1209
```

The cause is **not** a syntax bug. `BookingManager.php` uses short open tags
(`<? echo ... ?>`, and `<? } ?>` to close a `foreach` opened inside PHP). With
`short_open_tag=Off` — the PHP 8 default — those blocks are literal HTML, so the
brace never closes. Proof:

```
$ php -l classes/core/BookingManager.php
PHP Parse error: Unclosed '{' on line 535 ... on line 1209
$ php -d short_open_tag=1 -l classes/core/BookingManager.php
No syntax errors detected
```

I verified this against a stashed, pristine tree, so it predates my changes. All
of my own results were produced with `php -d short_open_tag=1 vendor/bin/phpunit`.

Why this matters more than it looks:

- CLAUDE.md documents the test command as bare `./vendor/bin/phpunit` and claims
  a **259 tests, 0 failures** baseline. That baseline is only reachable on a box
  with `short_open_tag=On`. Any agent or CI runner on a default PHP 8 install
  sees a hard fatal and has no way to tell it apart from a broken repo.
- `short_open_tag` has been discouraged since 5.3 and its removal has been
  proposed more than once. The booking path — the revenue path — is one INI flip
  away from a fatal.

Recommended next step, in this order: add `short_open_tag=On` (or the required
PHP ini) to the documented setup in CLAUDE.md *today*, then open a task to
convert the short tags in `classes/core/BookingManager.php` to `<?php` /
`<?php echo`. It is a mechanical change and `php -l` proves each file.

### 2. Suite state, measured

With `short_open_tag=1`, on this branch: **342 tests, 2 failures, 275 skipped.**
The 275 skips are all "No database." / no dev server on 2027 — this container
has no MySQL client or server at all. I did not get to attribute the 2 failures
to a cause before the shell died; they are in suites that need a database, and I
have no evidence they are related to this change (nothing here touches booking,
auth, or workload). **Someone should confirm that on a box with a database
before this branch is merged.** I am flagging it rather than asserting it is
fine.

### 3. Documentation is a hazard in its own right

The repository root holds 50+ loose `.md` files, including eight separate
`CALENDAR_*` documents and three overlapping QR documents, one of which
(`PIANO_QR_FEATURES.md`) documents the dead generator in detail as though it
works. This is the Dewey Decimal protocol's target case. A sweep would help, but
the higher-value move is narrower: delete or mark the documents that describe
code which cannot execute. A stale doc that describes a *missing* feature costs
an agent a few minutes; one that describes a *broken* feature as working costs
it the whole task.

### 4. Why this task is not at PEER_REVIEW

The container's shell died partway through — every `Bash` invocation, down to
`true`, returns exit 1 with no output. It is not the disk (file writes still
succeed) and not the sandbox (bypassing it changes nothing); the shell cannot
spawn a process at all. That happened after the tests were green and after the
PDFs were rendered and decoded, but before `fleet verify`.

So the code was pushed with the GitHub API instead of git, and the fleet
transition was left undone. `verify` and `submit` are CLI-only by design, and
hand-writing a handoff YAML with a `head_sha` I could not obtain from `git
rev-parse` would be fabricating the cryptographic evidence the whole protocol
exists to guarantee. Leaving the task CLAIMED and saying why is the honest
option.

**To finish it, from a container with a working shell:**

```bash
cd task_coordinator
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd ../intypiano && git fetch origin claude/qr-report-business-cards-bq6mb2
git checkout claude/qr-report-business-cards-bq6mb2
php -d short_open_tag=1 vendor/bin/phpunit --filter QrCardSheet   # expect 12/12
cd ../task_coordinator
./bin/fleet verify T-INTY-018
# put the intypiano head sha in handoffs/T-INTY-018_handoff.yaml
./bin/fleet submit T-INTY-018
./bin/fleet render
```

Note that bare `./bin/fleet verify` will run the audited command *without* the
`short_open_tag` flag and will therefore fail on the `BookingManager` parse
error unless the host's php.ini sets it. That is system feedback #2 and #3
biting in practice.

### 5. Recommended next steps for the human

1. Confirm the 2 database-dependent failures on a box with MySQL, and confirm
   they are unrelated to this branch.
2. Print one sheet on real Avery 8371 stock and scan a card with a phone. The
   geometry is asserted and the codes decode from a 300dpi raster, but nothing
   substitutes for the paper.
3. Decide the `short_open_tag` question (#1). It is the largest latent risk I
   found and it is not related to this feature.
4. Delete or deprecate `qr_report_generator.php` and `qr_avery5162_poc.php`, and
   correct `PIANO_QR_FEATURES.md`. There are now three QR surfaces documented
   and two of them do not run.
