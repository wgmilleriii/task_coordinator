#!/usr/bin/env python3
import os
import re
import sys
import json
import types
import ftplib
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Exclusion patterns. Per-repo overrides let a repo's local deploy match its
# own CI workflow's filter instead of inheriting one shaped around another
# repo's conventions (e.g. intypiano's deploy.yml excludes only README.md,
# not every .md -- docs/experts/*.md and DEPLOY_CHANGELOG.md are real content
# there, not throwaway notes).
DEFAULT_EXCLUDES = [
    ".git/", ".github/", "docs/", "tasks/", ".fleet/", "node_modules/", ".gitignore",
    "graphify-out/", "scratch/",
    "protected_assets/article_images/", "journalgpt/corpus/article_html/",
    # Agent + editor tooling. Found live on production 2026-08-29: .mcp.json
    # was publicly downloadable WITH a real CHORD_TOKEN in it, alongside
    # .claude/skills/** and .impeccable/. None of this is site content and
    # all of it is useful reconnaissance (or, in .mcp.json's case, a
    # credential). The FTP root is the webroot here, so anything tracked at
    # repo root is served unless excluded.
    ".claude/", ".cursor/", ".impeccable/", ".chord/", ".vscode/", ".idea/",
    ".mcp.json", ".fleet_doc_last_updated", "DEPLOY_QUEUE.txt",
    # Full mysqldump output. Found live on production 2026-08-29: a 7.4 MB
    # dump containing users (with password_hash), conversations and messages
    # was anonymously downloadable. Backups must never live in a webroot.
    "databasebackups/", "databasedumps/", ".sql.gz", "dbbackup",
    # Developer tooling that CANNOT execute on this host and is served as
    # PLAINTEXT if it reaches the webroot. Shared hosting runs PHP, not Python
    # or shell, so a .py/.sh in the tree is pure liability.
    #
    # Found live 2026-08-30: journalgpt/cli/live_page_renderer.py carries a
    # hardcoded FTP host, user and password (found by Walter). It returns 404
    # today ONLY because it has not been deployed yet -- it IS in the
    # deployable set, so the next full sync would have published a live
    # credential at a public URL as readable text.
    #
    # NOT excluding .sql: migrations/*.sql must reach the server because
    # admin_migrate.php reads them off disk. That is a "deploy but do not
    # serve" case and needs a serving rule, not an exclusion -- see
    # T-PTG-220. Excluding them would break the only migration route we have.
    ".py", ".sh",
    "bin/", "tests/", ".venv/", "__pycache__/", ".DS_Store",
]
DEFAULT_EXCLUDE_ALL_MD = True  # generic default: skip every *.md file

REPO_EXCLUDES = {
    "intypiano": {
        "patterns": [
            ".git/", ".github/", "docs/", "graphify-out/", "node_modules/",
            ".gitignore", "databasedumps/", ".fleet/", "scratch/",
        ],
        "exclude_all_md": False,  # only README.md is excluded, matched below
        "extra_exact": ["README.md"],
    },
    "newmexicoptg.org": {
        # Keeps the generic exclude-all-.md default (this repo has ~90 planning/
        # doc .md files under docs/, journalgpt/docs/, root, etc. that must never
        # ship) but carves out journalgpt/corpus/articles/ -- the ONLY .md path
        # that is real site content, not documentation. Found the hard way: a
        # 1533-file corpus re-extraction (T-PTG-152 follow-up, 2026-08-27) FTP'd
        # only extraction_report.json and the two .py scripts -- every single
        # regenerated/new corpus/articles/*.md file was silently dropped by the
        # blanket .md exclusion, so the "deployed successfully" fix never
        # actually reached prod/test until this override was added.
        # research_workspace/ is agents' committed working state (drafts,
        # phase notes), never site content. Project dirs are all named
        # NNN-slug, so excluding the digit-prefixed paths keeps the content
        # out while letting the directory's deny .htaccess itself deploy --
        # the deny rule must reach the server precisely because earlier
        # deploys already shipped files there.
        "patterns": DEFAULT_EXCLUDES + [
            "journalgpt/research_workspace/0",
            "journalgpt/research_workspace/1",
            "journalgpt/research_workspace/2",
            "journalgpt/research_workspace/3",
            "journalgpt/research_workspace/4",
            "journalgpt/research_workspace/5",
            "journalgpt/research_workspace/6",
            "journalgpt/research_workspace/7",
            "journalgpt/research_workspace/8",
            "journalgpt/research_workspace/9",
            # Agent working state for the article-cleanup pipeline (diffs,
            # ledgers, verdicts). 613 such files were pending on 2026-09-05.
            "journalgpt/corpus/qc_staging/",
        ],
        "exclude_all_md": True,
        "extra_exact": [],
        "md_allow_prefixes": [
            # journalgpt/corpus/articles/ was allowed here 2026-08-27..2026-09-05.
            # Chip, 2026-09-05: corpus .md is excluded from deploys; article
            # conversion is handled manually from now on.
            # T-PTG-302 translations are site content exactly like the
            # articles they translate. Added 2026-09-01 after the SAME silent
            # drop the comment above warns about: 20 translation .md files
            # "deployed successfully" while zero reached prod (caught by FTP
            # read-back, not by the deploy's own verify -- it verifies only
            # what it chose to upload).
            "journalgpt/corpus/translations/",
            # journalgpt/specs/ is MEMBER-FACING: doc.php's allow-list serves
            # these paths to logged-in members, so a spec that does not deploy
            # is a page that 404s for a reader. Added 2026-09-03 after the
            # THIRD instance of the silent drop the two comments above warn
            # about: a member-facing explainer of the answer engine was written
            # to docs/, linked from help.php, and deployed "successfully" while
            # the file itself was excluded twice over -- shipping a live link
            # to a 404. If doc.php can serve it, deploy.py must be able to ship
            # it; those two lists have to agree.
            "journalgpt/specs/",
        ],
    },
}


# --------------------------------------------------------------------------
# ANCESTRY GUARD (2026-09-25)
#
# deploy.py ships the DIFF between deploy_state's last sha and HEAD, and every
# path the diff calls D becomes an FTP DELETE. So deploying a tree that does
# not CONTAIN the environment's tip does not merely "skip" the missing
# commits -- it actively deletes their files off the server. That has now been
# caught by a human twice in two days: once as a branch that had never merged
# the environment's tip, and once as a second deploy.py queued on the gate
# lock behind a running one, whose tree predated the version-bump commit the
# first deploy was about to make. Both were caught by eye, seconds before the
# upload. This belongs in the tool.
#
# Per repo+env, the ref whose tip HEAD must contain, as (remote, branch):
#   newmexicoptg.org     Chip's ruling Q-8a-8 (see the prod fast-forward at the
#                        bottom of this file): main IS production, test is test.
#   resources_was_pmtnm  .github/workflows/deploy.yml: a push to `test` deploys
#                        the test site; production is a workflow_dispatch on
#                        `main`.
#   intypiano            .github/workflows/deploy.yml deploys on push to
#                        `master` ONLY. The repo has an origin/test branch but
#                        no configured test deploy, so no test mapping is
#                        claimed here -- an unverified mapping would be worse
#                        than none, because it would be enforced.
# A repo/env absent from this table is NOT checked, and deploy.py says so
# rather than implying it looked.
TRACKING_REFS = {
    "newmexicoptg.org": {"test": ("origin", "test"), "prod": ("origin", "main")},
    "resources_was_pmtnm": {"test": ("origin", "test"), "prod": ("origin", "main")},
    "intypiano": {"prod": ("origin", "master")},
}

ANCESTRY_EXIT_CODE = 3   # HEAD does not contain the environment's tip
GATE_BUSY_EXIT_CODE = 4  # another deploy.py holds the gate lock


def resolve_repo_identity(repo_dir, repo_name, out=None):
    """The name to look up in TRACKING_REFS.

    deploy.py takes its repo name from the DIRECTORY BASENAME, and deploys are
    increasingly run from worktrees named for the task rather than the repo
    (train-45, leipzig-783). Keying the ancestry guard on the basename alone
    would report "no tracking ref configured" for exactly the case the guard
    exists to cover. So when the basename has no mapping, fall back to the
    basename of origin's URL -- and say out loud which name was used, because
    a guard that silently picks a different subject is worse than one that
    does not run.

    Only the ANCESTRY mapping is resolved this way. The deploy_state key and
    the exclusion rules still come from the directory basename, unchanged."""
    if repo_name in TRACKING_REFS:
        return repo_name
    r = _git("git remote get-url origin", repo_dir)
    if r.returncode != 0:
        return repo_name
    cand = r.stdout.strip().rstrip("/").rsplit("/", 1)[-1].rsplit(":", 1)[-1]
    if cand.endswith(".git"):
        cand = cand[:-4]
    if cand in TRACKING_REFS:
        print(f"  directory is named {repo_name!r}, which has no tracking-ref mapping; "
              f"origin's URL says this is {cand!r} -- using that mapping",
              file=out or sys.stdout, flush=True)
        return cand
    return repo_name


def get_tracking_ref(repo_name, env):
    """(remote, branch, 'remote/branch') for this repo+env, or None."""
    entry = TRACKING_REFS.get(repo_name, {}).get(env)
    if not entry:
        return None
    remote, branch = entry
    return remote, branch, f"{remote}/{branch}"


def _git(cmd, cwd):
    """A git command that is ALLOWED to fail -- run_cmd() exits the process on
    a nonzero status, which is wrong for a probe whose failure is the answer."""
    return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)


def fetch_tracking_ref(repo_dir, remote, branch, out=None):
    """Refresh the remote-tracking ref. Returns True if the fetch succeeded.

    A failed fetch is NOT fatal by itself -- the check then runs against the
    local copy of the ref, which can only be older than the truth, so it can
    still refuse and can still pass a tree that has since fallen behind. Said
    out loud rather than swallowed."""
    out = out or sys.stdout
    r = _git(f"git fetch {remote} {branch}", repo_dir)
    if r.returncode != 0:
        print(f"  ! git fetch {remote} {branch} FAILED ({r.stderr.strip()[:200]}); "
              f"comparing against the local copy of {remote}/{branch}, which may be "
              f"stale -- a pass here is weaker than a fetched one", file=out, flush=True)
        return False
    return True


def ancestry_status(repo_dir, ref, head="HEAD"):
    """(resolved, is_ancestor, missing_count).

    resolved False means the ref does not exist in this worktree, so NOTHING
    was checked -- the caller must treat that as a refusal, not a pass."""
    if _git(f"git rev-parse --verify --quiet {ref}^{{commit}}", repo_dir).returncode != 0:
        return False, False, None
    ok = _git(f"git merge-base --is-ancestor {ref} {head}", repo_dir).returncode == 0
    if ok:
        return True, True, 0
    cnt = _git(f"git rev-list --count {head}..{ref}", repo_dir)
    txt = cnt.stdout.strip()
    return True, False, int(txt) if cnt.returncode == 0 and txt.isdigit() else None


def check_ancestry(repo_dir, repo_name, env, allow_reason=None, fetch=True,
                   enforce=True, out=None, when=""):
    """Refuse a deploy from a tree that does not CONTAIN the environment's tip.

    Returns (tracking_ref|None, verdict) where verdict is one of 'verified',
    'overridden: <reason>', 'not_configured' or 'REFUSED'. With enforce=True a
    refusal exits ANCESTRY_EXIT_CODE instead of returning it."""
    out = out or sys.stdout
    repo_name = resolve_repo_identity(repo_dir, repo_name, out)
    mapping = get_tracking_ref(repo_name, env)
    if not mapping:
        print(f"  no tracking ref configured for {repo_name}/{env}; ancestry not checked",
              file=out, flush=True)
        return None, "not_configured"
    remote, branch, ref = mapping
    if fetch:
        fetch_tracking_ref(repo_dir, remote, branch, out)
    resolved, ok, missing = ancestry_status(repo_dir, ref)
    head = _git("git rev-parse --short HEAD", repo_dir).stdout.strip()

    if resolved and ok:
        print(f"  ancestry OK{when}: HEAD ({head}) contains {ref}.", file=out, flush=True)
        return ref, "verified"

    if not resolved:
        problem = (f"{ref} does not resolve in this worktree, so whether HEAD contains "
                   f"the {env} tip is UNKNOWN. An unknown is not a pass.")
        missing_txt = "unknown"
    else:
        problem = (f"HEAD ({head}) does NOT contain {ref}: "
                   f"{'an unknown number of' if missing is None else missing} commit(s) "
                   f"on {ref} are missing from this tree.")
        missing_txt = "unknown" if missing is None else str(missing)

    if allow_reason:
        print(f"  ! --allow-non-ancestor{when}: {problem}", file=out)
        print(f"  ! proceeding on the stated reason, which is recorded in "
              f"deploy_state.json: {allow_reason}", file=out, flush=True)
        return ref, f"overridden: {allow_reason}"

    print("", file=out)
    print(f"REFUSING TO DEPLOY {repo_name} to {env}{when}.", file=out)
    print(f"  {problem}", file=out)
    print(f"  tracking ref: {ref}   commits missing from HEAD: {missing_txt}", file=out)
    print("  deploy.py ships the DIFF between the last deployed sha and HEAD, and a file "
          "those commits ADDED appears in that diff as a DELETION -- deploying this tree "
          "would REMOVE their files from the server, not merely skip them.", file=out)
    print(f"  Fix: `git fetch {remote} {branch} && git merge {ref}` (or rebase onto it), "
          f"then re-run. Nothing was run, locked, bumped or uploaded.", file=out)
    print('  Override, if you know why this tree is right: '
          '--allow-non-ancestor "<reason>" (printed and recorded).', file=out, flush=True)
    if enforce:
        sys.exit(ANCESTRY_EXIT_CODE)
    return ref, "REFUSED"


def check_gate_not_queued(wait_for_gate, path=None, out=None):
    """Refuse to QUEUE behind another deploy.py, instead of waiting on it.

    Waiting behind a RUNNING DEPLOY is how a tree goes stale while it waits:
    the running deploy bumps version.json and COMMITS, so the moment it
    finishes, the waiting tree no longer contains the environment's tip and
    its diff would delete the files just shipped. Caught by hand with seconds
    to spare on 2026-09-24.

    Waiting behind a SUITE (a gate held by run_suite.php, `gate_lock.py run`,
    sync.py, ...) is still right: a suite does not move any ref, so the tree
    that was correct before the wait is still correct after it. The holder
    record's tool= field is what distinguishes the two; deploy.py writes
    tool="deploy.py" when it takes the lock (see acquire_gate_lock below).
    A holder whose record cannot be read is treated as a deploy -- an unknown
    is not permission."""
    out = out or sys.stdout
    if gate_lock.held_by_ancestor(path) is not None:
        return  # our own ancestor (deploy.py under `gate_lock.py run`) -- not a queue
    held, rec = gate_lock.probe(path)
    if not held:
        return
    desc = gate_lock.describe_holder(rec)
    tool = rec.get("tool") if isinstance(rec, dict) else None
    if tool and "deploy.py" not in tool:
        print(f"  gate lock is HELD by a non-deploy tool (tool={tool}); it moves no refs, "
              f"so waiting is safe -> {desc}", file=out, flush=True)
        return
    who = (f"another deploy.py (tool={tool})" if tool
           else "an unidentified holder (no readable tool= in the record)")
    if wait_for_gate:
        print(f"  ! --wait-for-gate: gate lock HELD by {who}; waiting -> {desc}", file=out)
        print("  ! ancestry will be RE-CHECKED after the lock is acquired -- the "
              "environment can move while you wait.", file=out, flush=True)
        return
    print("", file=out)
    print(f"REFUSING TO DEPLOY: the machine-wide gate lock is HELD by {who}.", file=out)
    print(f"  holder: {desc}", file=out)
    print("  Queuing behind a running deploy is how a tree goes stale WHILE IT WAITS: the "
          "running deploy bumps the version and commits, and the queued tree -- which "
          "does not contain that commit -- then DELETES the files it just shipped.", file=out)
    print("  Let it finish, merge the environment's tip, and re-run. To queue deliberately, "
          f"pass --wait-for-gate (ancestry is re-checked after the wait). Nothing was run, "
          f"locked or uploaded.", file=out, flush=True)
    sys.exit(GATE_BUSY_EXIT_CODE)


def compute_deployable(repo_dir, repo_name, last_sha, current_sha):
    """(uploads, deletes, entries) for last_sha..current_sha, after exclusion.

    The ONE place the deployable set is computed: --list-only calls this and so
    does the real run, so a preview that disagrees with the deploy is not
    possible by construction. entries is [(A|M|D, path)] in diff order."""
    diff_output = run_cmd(f"git diff --name-status {last_sha} {current_sha}", cwd=repo_dir)
    patterns, exclude_all_md, exclude_exact, md_allow_prefixes = get_repo_excludes(repo_name)
    uploads, deletes, entries = [], [], []
    for line in diff_output.split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        status = parts[0]
        filepath = parts[-1]  # for R/C this is the DESTINATION path, as before
        if should_exclude(filepath, patterns, exclude_all_md, exclude_exact, md_allow_prefixes):
            continue
        if status.startswith("D"):
            deletes.append(filepath)
            entries.append(("D", filepath))
        else:
            uploads.append(filepath)
            entries.append(("A" if status[0] in "ARC" else "M", filepath))
    return uploads, deletes, entries


def differing_from_ref(repo_dir, ref, paths):
    """Of `paths`, those whose content differs between `ref` and HEAD.

    Answers the question builders keep answering by hand before a deploy:
    'is my tree byte-identical to origin/test for the files I am shipping?'"""
    if not paths:
        return []
    r = _git(f"git diff --name-only {ref} HEAD", repo_dir)
    if r.returncode != 0:
        return None
    changed = {line for line in r.stdout.split("\n") if line}
    return [p for p in paths if p in changed]


def print_deployable_set(repo_dir, repo_name, env, last_sha, current_sha, out=None):
    """--list-only. Prints exactly what the real run would compute, then stops.

    Touches no FTP connection, no lock, no version file and no deploy_state."""
    out = out or sys.stdout
    uploads, deletes, entries = compute_deployable(repo_dir, repo_name, last_sha, current_sha)
    print(f"--list-only: {repo_name} {env}   {last_sha[:8]}..{current_sha[:8]}", file=out)
    for status, path in entries:
        print(f"{status}\t{path}", file=out)
    print(f"  {len(entries)} deployable path(s): {len(uploads)} upload, "
          f"{len(deletes)} DELETE.", file=out)

    mapping = get_tracking_ref(resolve_repo_identity(repo_dir, repo_name, out), env)
    if not mapping:
        print(f"  no tracking ref configured for {repo_name}/{env}; ancestry not checked",
              file=out)
    else:
        _remote, _branch, ref = mapping
        resolved, ok, missing = ancestry_status(repo_dir, ref)
        if not resolved:
            print(f"  tracking ref {ref}: does not resolve in this worktree -- ancestry "
                  f"NOT checked and no content comparison possible.", file=out)
        else:
            if ok:
                print(f"  tracking ref {ref}: HEAD contains it.", file=out)
            else:
                print(f"  tracking ref {ref}: HEAD does NOT contain it -- "
                      f"{'unknown' if missing is None else missing} commit(s) missing. "
                      f"A real run would REFUSE (exit {ANCESTRY_EXIT_CODE}).", file=out)
            differing = differing_from_ref(repo_dir, ref, [p for _, p in entries])
            if differing is None:
                print(f"  could not diff against {ref}; content comparison skipped.", file=out)
            else:
                print(f"  {len(differing)} of {len(entries)} path(s) differ in content from "
                      f"{ref} ({len(entries) - len(differing)} byte-identical to it).", file=out)
    print("  Nothing was uploaded, locked, bumped or recorded. A real run would ALSO carry "
          "the version.json/changelog.json it commits itself.", file=out, flush=True)
    return entries


def record_ancestry(state, repo_name, env, tracking_ref, ancestry):
    """Write the guard's verdict beside the sha it belongs to."""
    state[repo_name][f"{env}_tracking_ref"] = tracking_ref
    state[repo_name][f"{env}_ancestry"] = ancestry


# sync.py owns the sha256 manifest and the cross-agent deploy lock. It still
# lives in the v3 checkout; when v3 is retired this import is the one thing that
# has to move with it. Imported rather than reimplemented: a second copy of a
# hashing/locking routine is the same defect class as two deploy engines.
SYNC_BIN = "/Users/willismiller/Documents/GitHub/task_coordinator_v3/bin"


sys.path.insert(0, SYNC_BIN)
import deploy_guard  # noqa: E402  -- shared with the v3 engine; see its docstring

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gate_lock  # noqa: E402  -- machine-wide gate lock, see bin/gate_lock.py
# Gate runner shared (byte-identical) with v3, where sync.py also uses it. This
# file keeps its OWN exclusion rules below; deploy_common's differ (v3's).
import deploy_common  # noqa: E402


def _load_sync():
    """Returns the sync module, or None if unavailable. See require_sync() for
    what a deploy does about None."""
    try:
        if SYNC_BIN not in sys.path:
            sys.path.insert(0, SYNC_BIN)
        import sync
        return sync
    except Exception as e:
        print(f"  ! sync.py unavailable from {SYNC_BIN} ({type(e).__name__}: {e})")
        return None


def require_sync(allow_no_sync):
    """FAIL CLOSED (2026-09-14). sync.py supplies the per-repo+env DeployLock
    and the manifest write. Without it this deploy would run its FTP session
    unserialized against a concurrent sync.py and leave the manifest asserting
    stale hashes -- this used to be a warning, and the deploy went ahead.
    Now it aborts before the gate unless --allow-no-sync is given explicitly."""
    sync = _load_sync()
    if sync is None and not allow_no_sync:
        print("REFUSING TO DEPLOY: could not import sync.py from the v3 checkout "
              f"({SYNC_BIN}). Without it there is no per-env DeployLock (a concurrent "
              "sync.py could interleave with this FTP session) and no manifest "
              "update. Nothing was run or uploaded. Fix the v3 checkout, or re-run "
              "with --allow-no-sync if you accept both risks for this one deploy.")
        sys.exit(1)
    if sync is None:
        print("  ! --allow-no-sync: proceeding with NO DeployLock and NO manifest update")
    return sync


def get_repo_excludes(repo_name):
    cfg = REPO_EXCLUDES.get(repo_name)
    if not cfg:
        return DEFAULT_EXCLUDES, DEFAULT_EXCLUDE_ALL_MD, [], []
    return (
        cfg["patterns"], cfg["exclude_all_md"], cfg.get("extra_exact", []),
        cfg.get("md_allow_prefixes", []),
    )

# Where each repo keeps its version/changelog files, relative to repo_dir.
# Checked in order; first one that exists wins. Repos with no version.json
# convention are skipped silently (bump_version returns None).
VERSION_FILE_CANDIDATES = ["version.json", "journalgpt/version.json"]


def bump_version(repo_dir, env, new_sha, commit_subjects):
    """DEPLOY.md requires every deployment to bump version.json and update
    changelog.json -- a step every prior manual/FTP-bypass deploy skipped.
    Runs once per deploy, only when there are real files going out."""
    version_file = None
    for candidate in VERSION_FILE_CANDIDATES:
        p = Path(repo_dir) / candidate
        if p.exists():
            version_file = p
            break
    if not version_file:
        return None

    with open(version_file) as f:
        version_data = json.load(f)

    old_version = str(version_data.get("version", "0.0.0"))
    base = old_version.split("-")[0]
    parts = (base.split(".") + ["0", "0", "0"])[:3]
    parts[2] = str(int(parts[2]) + 1)
    new_base = ".".join(parts)
    suffix = "-test" if env == "test" else ""
    new_version = new_base + suffix

    now = datetime.now(timezone.utc)
    version_data["version"] = new_version
    version_data["commit"] = new_sha[:8]
    version_data["date"] = now.strftime("%Y-%m-%d %H:%M:%S")

    with open(version_file, "w") as f:
        json.dump(version_data, f, indent=2)
        f.write("\n")

    changelog_file = version_file.parent / "changelog.json"
    changelog_rel = None
    if changelog_file.exists() and commit_subjects:
        with open(changelog_file) as f:
            changelog = json.load(f)
        changelog.insert(0, {
            "version": new_base,
            "date": now.strftime("%Y-%m-%d"),
            # Auto-generated from commit subjects between the last deployed SHA
            # and this one -- terser than the hand-written entries above it,
            # but accurate. Rewrite by hand later if it needs real prose.
            "changes": commit_subjects,
        })
        with open(changelog_file, "w") as f:
            json.dump(changelog, f, indent=2)
            f.write("\n")
        changelog_rel = str(changelog_file.relative_to(repo_dir))

    return {
        "version_file": str(version_file.relative_to(repo_dir)),
        "changelog_file": changelog_rel,
        "new_version": new_version,
    }

# Test-suite entrypoints to gate a deploy on, relative to repo_dir, checked in
# order. Repos with none of these are deployed ungated (no convention to run).
#
# run_suite.php (Westerby, 2026-08-31) is the CI replacement: GitHub Actions
# has not executed a job since Aug 23 (account billing), so this local gate is
# the ONLY gate that actually runs. Exit 0 = clean or unchanged known
# failures; exit 1 = NEW failure; exit 2 = the run itself is untrustworthy
# (DB unreachable / silent SQLite fallback / baseline missing). Both nonzero
# codes block the deploy -- they mean different things, but neither is a pass.
TEST_SUITE_CANDIDATES = ["journalgpt/tests/run_suite.php"]


def find_test_suite(repo_dir):
    return gate_lock.find_test_suite(repo_dir, TEST_SUITE_CANDIDATES)


def run_test_gate(repo_dir, lock=None):
    """Run this repo's test suite before anything goes out over FTP. Returns
    (passed: bool, output: str, suite: str|None). A repo with no recognized
    suite returns (True, '', None) -- deploy proceeds ungated, same as before
    this existed, rather than blocking on a convention it doesn't have.

    lock: the held gate_lock.GateLock. Its fd is passed into the gate child
    (sh forwards it to php), so if deploy.py is SIGKILLed mid-gate the orphaned
    suite keeps the machine-wide lock until it exits and the next gate cannot
    start on top of it. Intended. Background workers the suite spawns inherit
    it too and can hold the lock until they exit: a delay, never an overlap."""
    return deploy_common.run_test_gate(repo_dir, lock, TEST_SUITE_CANDIDATES)


def load_env():
    env_path = Path(os.path.dirname(__file__)).parent / ".env"
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip()

def should_exclude(filepath, patterns, exclude_all_md, extra_exact, md_allow_prefixes=()):
    if filepath in extra_exact:
        return True
    if exclude_all_md and filepath.endswith(".md"):
        if not any(filepath.startswith(p) for p in md_allow_prefixes):
            return True
    for ex in patterns:
        if ex in filepath or filepath.startswith(ex):
            return True
    return False

def trigger_remote_migration(repo_dir, env):
    """After an FTP upload, ask the deployed site to run any pending DB
    migrations via its token-gated operations API (api/operations.php) --
    the same createJob/confirmJob flow admin_migrate.php uses, just called
    over HTTP instead of a human clicking a button. Migrations are
    idempotent (schema_migrations tracks what's applied), so calling this
    on every deploy is harmless even when nothing is pending.

    Only applies to repos using this convention (currently just
    newmexicoptg.org's journalgpt/migrations/).

    Returns a verdict the caller must surface: 'not_applicable',
    'skipped_config', 'succeeded', or 'failed'. On 2026-08-30 this step
    401'd on five consecutive prod deploys and every one still printed
    "Deployed successfully" -- migration 050 silently never applied, and the
    miss surfaced later as a schema error nobody connected to a deploy
    (found by Prideaux). The upload and the migration are BOTH the deploy;
    a banner that only reports the upload is the defect."""
    if not (Path(repo_dir) / "journalgpt" / "migrations").is_dir():
        return "not_applicable"

    token = os.environ.get("JOURNALGPT_OPERATIONS_TOKEN")
    base_url = os.environ.get(f"JOURNALGPT_OPERATIONS_URL_{env.upper()}")
    if not token or not base_url:
        print("Skipping remote migration trigger: set JOURNALGPT_OPERATIONS_TOKEN and "
              f"JOURNALGPT_OPERATIONS_URL_{env.upper()} in .env to enable it.")
        return "skipped_config"

    def call(path, payload):
        req = urllib.request.Request(
            base_url.rstrip("/") + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())

    try:
        created = call("/create", {"type": "migrate", "arguments": {}})
        job = created["job"]
        confirmed = call(f"/confirm/{job['id']}", {"confirmation_secret": created["confirmation_secret"]})
        result = confirmed["job"].get("result", {})
        state = confirmed['job'].get('state')
        print(f"Remote migration trigger: state={state} "
              f"applied={result.get('applied')} log={result.get('log')}")
        return "succeeded" if state == "succeeded" else "failed"
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError) as e:
        print(f"Remote migration trigger FAILED: {e}")
        return "failed"


def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

USAGE = """Usage: deploy.py <repo_dir> <environment (test|prod)> [--seed <sha>] [--list-only]
       [--gate-lock-timeout MINUTES] [--allow-no-sync] [--allow-non-ancestor "<reason>"]
       [--wait-for-gate]

  --list-only                  print the deployable set (A/M/D, one path per
                               line) exactly as a real run would compute it,
                               plus how many of those paths differ in content
                               from the environment's tracking ref, then exit 0.
                               Touches no FTP, no lock, no version file and no
                               deploy_state.json.

  --allow-non-ancestor "<why>" deploy even though HEAD does not contain the
                               environment's tracking ref. The reason is printed
                               and written into deploy_state.json. Without it
                               such a deploy is REFUSED with exit 3.

  --wait-for-gate              queue on the gate lock even when the holder is
                               another deploy.py. Without it that case is
                               REFUSED immediately with exit 4 (waiting on a
                               deploy makes your tree stale while you wait).
                               Ancestry is re-checked after the lock is taken.

  --allow-no-sync              deploy even if sync.py cannot be imported from the
                               v3 checkout (no DeployLock, no manifest update).
                               Without it such a deploy aborts before the gate.

  --seed <sha>                 record <sha> as the last deployed commit and exit
  --gate-lock-timeout MINUTES  how long to wait for the machine-wide gate lock
                               (default 60; a prod deploy has taken ~50). On
                               timeout the deploy exits 75 having run and
                               uploaded nothing.

Ancestry guard: before the gate lock is taken, deploy.py fetches the
environment's tracking ref (TRACKING_REFS, e.g. newmexicoptg.org test ->
origin/test, prod -> origin/main) and refuses unless HEAD CONTAINS it. A tree
missing the environment's tip does not skip those commits -- their files appear
in this deploy's diff as deletions and would be deleted off the server. A
repo/env with no mapping prints "ancestry not checked" and continues. The check
is re-run after the gate lock is acquired, because the environment can move
while you wait.

Gate lock: before the test gate runs, deploy.py takes ONE machine-wide flock
(~/.cache/newmexicoptg-gate.lock, override $NEWMEXICOPTG_GATE_LOCK) shared by
test AND prod deploys, because every gate uses the same local MAMP DB
journal_ai_test. It is held through gate + upload + remote migrate. A waiting
deploy prints the holder (pid, env, worktree, start time). The gate child
holds the lock too, so if deploy.py is killed mid-gate the orphaned suite (and
any worker it spawned) keeps the lock until it exits: a delay, never an
overlap. The OS drops the lock when the last holder dies, so stale pid text
never blocks; never delete the file. A deploy.py launched under
`gate_lock.py run` reuses its ancestor's lock instead of waiting on it. Check it with `bin/gate_lock.py status`; run a suite by hand under it
with `bin/gate_lock.py run -- php journalgpt/tests/run_suite.php`.
The per-repo+env deploy lock (sync.DeployLock) is still taken afterwards for
the FTP session, as before."""


def _take_valued_flag(args, name):
    """Remove `--name VALUE` or `--name=VALUE` from args; returns VALUE or None.

    A VALUE that looks like another flag is an error, not a value: swallowing
    the next flag would silently disarm it (e.g. --allow-non-ancestor
    --wait-for-gate would have taken '--wait-for-gate' as the reason and then
    never waited)."""
    for i, a in enumerate(args):
        if a == name:
            if i + 1 >= len(args):
                print(f'{name} needs a value, e.g. {name} "why this tree is right"')
                sys.exit(1)
            val = args[i + 1]
            if val.startswith("--"):
                print(f"{name} needs a value, but the next argument is the flag {val!r}")
                sys.exit(1)
            del args[i:i + 2]
            return val
        if a.startswith(name + "="):
            val = a.split("=", 1)[1]
            del args[i]
            return val
    return None


def parse_args(argv):
    """Returns a namespace: repo_dir, env, seed_sha, gate_lock_timeout_min,
    allow_no_sync, allow_non_ancestor, wait_for_gate, list_only.
    Exits on bad input."""
    args = list(argv)
    if any(a in ("-h", "--help") for a in args):
        print(USAGE)
        sys.exit(0)
    allow_no_sync = "--allow-no-sync" in args
    wait_for_gate = "--wait-for-gate" in args
    list_only = "--list-only" in args
    args = [a for a in args
            if a not in ("--allow-no-sync", "--wait-for-gate", "--list-only")]
    allow_non_ancestor = _take_valued_flag(args, "--allow-non-ancestor")
    if allow_non_ancestor is not None and not allow_non_ancestor.strip():
        print('--allow-non-ancestor needs a REASON, e.g. '
              '--allow-non-ancestor "hotfix branch, tip merged by hand and verified"')
        sys.exit(1)
    timeout_val = _take_valued_flag(args, "--gate-lock-timeout")
    timeout_min = gate_lock.DEFAULT_TIMEOUT_MIN
    if timeout_val is not None:
        try:
            timeout_min = float(timeout_val)
        except ValueError:
            print(f"--gate-lock-timeout needs a number of minutes, got {timeout_val!r}")
            sys.exit(1)
    if len(args) < 2:
        print(USAGE)
        sys.exit(1)
    seed_sha = None
    if len(args) == 4 and args[2] == "--seed":
        seed_sha = args[3]
    return types.SimpleNamespace(
        repo_dir=os.path.abspath(args[0]),
        env=args[1],
        seed_sha=seed_sha,
        gate_lock_timeout_min=timeout_min,
        allow_no_sync=allow_no_sync,
        allow_non_ancestor=allow_non_ancestor,
        wait_for_gate=wait_for_gate,
        list_only=list_only,
    )


def main():
    opts = parse_args(sys.argv[1:])
    repo_dir, env, seed_sha = opts.repo_dir, opts.env, opts.seed_sha
    gate_lock_timeout_min, allow_no_sync = opts.gate_lock_timeout_min, opts.allow_no_sync

    repo_name = os.path.basename(repo_dir)

    if env not in ["test", "prod"]:
        print("Environment must be test or prod")
        sys.exit(1)

    load_env()

    # Repo-specific credentials (FTP_HOST_<REPO>_<ENV>) take priority over the
    # generic ones (FTP_HOST_<ENV>) so multiple repos can each target their own
    # site without colliding. A repo with no *_<REPO>_* vars set just falls
    # back to the generic pair, unchanged from before this existed.
    repo_key = repo_name.upper().replace("-", "_").replace(".", "_")

    def ftp_var(field):
        specific = f"FTP_{field}_{repo_key}_{env.upper()}"
        generic = f"FTP_{field}_{env.upper()}"
        return os.environ.get(specific) or os.environ.get(generic), specific, generic

    host, host_specific, host_generic = ftp_var("HOST")
    user, _, _ = ftp_var("USER")
    passwd, _, _ = ftp_var("PASS")
    ftp_dir, _, _ = ftp_var("DIR")
    ftp_dir = ftp_dir or "/"

    # --list-only never opens a connection, so it must not require credentials:
    # a preview you can only run on a machine configured to deploy is not a
    # preview anyone will run.
    if not all([host, user, passwd]) and not opts.list_only:
        print(f"Missing FTP credentials for {repo_name} {env}. "
              f"Set {host_specific}/FTP_USER_.../FTP_PASS_.../FTP_DIR_... "
              f"(or the generic {host_generic}/FTP_USER_.../FTP_PASS_...) in .env.")
        sys.exit(1)

    state_file = Path(os.path.dirname(__file__)).parent / "deploy_state.json"
    state = {}
    if state_file.exists():
        with open(state_file, "r") as f:
            state = json.load(f)

    if repo_name not in state:
        state[repo_name] = {}

    if seed_sha:
        state[repo_name][env] = seed_sha
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
        print(f"Seeded {repo_name} {env} state with {seed_sha}. You can now run deploy without --seed.")
        sys.exit(0)

    last_sha = state[repo_name].get(env)
    
    if not last_sha:
        print(f"No last deployed SHA found for {repo_name} {env}. Please run with --seed <sha> first.")
        sys.exit(1)

    current_sha = run_cmd("git rev-parse HEAD", cwd=repo_dir)

    # --list-only answers "what would this deploy actually send?" without being
    # a deploy. It comes FIRST, before the ancestry guard, on purpose: the tree
    # you most want to inspect is the one that would be refused.
    if opts.list_only:
        print_deployable_set(repo_dir, repo_name, env, last_sha, current_sha)
        sys.exit(0)

    # ANCESTRY GUARD -- before the gate lock, before the FTP session, before
    # anything is bumped or committed. See TRACKING_REFS at the top of this file
    # for why a non-containing tree is a deletion, not an omission.
    tracking_ref, ancestry = check_ancestry(repo_dir, repo_name, env,
                                            opts.allow_non_ancestor)

    if last_sha == current_sha:
        # "Up to date" is a claim about the DATABASE as well as the files. If
        # the last deploy's migration trigger failed, its exit 2 was loud --
        # but a re-run "to check it's fine" used to land here and print a
        # cheerful banner while the migration was still unapplied (Prideaux,
        # 2026-08-31). So retry the migration before being reassuring.
        if state[repo_name].get(f"{env}_migrations_pending"):
            print("Files are up to date, but the LAST deploy's migration trigger "
                  "failed and is still pending. Retrying it now...")
            verdict = trigger_remote_migration(repo_dir, env)
            if verdict in ("succeeded", "not_applicable"):
                state[repo_name].pop(f"{env}_migrations_pending", None)
                with open(state_file, "w") as f:
                    json.dump(state, f, indent=2)
                print("Everything is up to date (pending migration now applied)!")
                sys.exit(0)
            print("Migration trigger still failing. Run admin_migrate.php in a "
                  f"browser on {env} and confirm; this flag clears on the next "
                  "successful trigger.")
            sys.exit(2)
        print("Everything is up to date!")
        sys.exit(0)

    print(f"Deploying changes from {last_sha} to {current_sha}...")
    # Same helper --list-only prints from, so the preview cannot drift from
    # what is actually sent.
    files_to_upload, files_to_delete, _entries = compute_deployable(
        repo_dir, repo_name, last_sha, current_sha)

    if not files_to_upload and not files_to_delete:
        print("No deployable files changed. Updating state.")
        state[repo_name][env] = current_sha
        record_ancestry(state, repo_name, env, tracking_ref, ancestry)
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
        sys.exit(0)

    # MACHINE-WIDE GATE LOCK (2026-09-14). Taken BEFORE the gate and held until
    # this process exits, i.e. through gate + version bump + upload + guards +
    # remote migrate. It used to be absent: the only lock came after the gate
    # and was keyed per repo+env, so two deploys seconds apart ran run_suite.php
    # concurrently on the shared MAMP DB journal_ai_test and corrupted each
    # other's fixture rows. One path for test AND prod, because both gate on
    # that same DB. Only repos that actually have a gate suite take it -- a repo
    # without one never touches the shared DB and should not queue behind it.
    # Never released explicitly: the OS drops the flock on any exit, including
    # every sys.exit below, so it cannot be stranded.
    # sync.py first (fail closed, before any gate time is spent), then the gate
    # lock. acquire_gate_lock reuses an ancestor's lock (deploy.py under
    # `gate_lock.py run`) instead of waiting on it, and exits 75 on timeout.
    sync = require_sync(allow_no_sync)
    _gate_lock = None
    if find_test_suite(repo_dir):
        # NO QUEUING BEHIND A DEPLOY (2026-09-25). Checked at the last possible
        # moment -- immediately before we would start waiting -- because that is
        # when the answer is most accurate. A suite holder is still waited on.
        check_gate_not_queued(opts.wait_for_gate)
        _gate_lock = gate_lock.acquire_gate_lock(env, repo_dir, "deploy.py",
                                                 gate_lock_timeout_min)
        # Acquiring may have taken an hour (a prod gate has run ~50 min), and a
        # tree that contained the environment's tip when we started need not
        # contain it now. Re-check with a fresh fetch before spending gate time
        # or touching the server.
        tracking_ref, ancestry = check_ancestry(
            repo_dir, repo_name, env, opts.allow_non_ancestor,
            when=" (re-checked after acquiring the gate lock)")

    print("Running test gate before deploy...")
    tests_passed, test_output, suite = run_test_gate(repo_dir, _gate_lock)
    if suite:
        print(f"({suite})")
    if not tests_passed:
        print(test_output)
        print(f"Test gate FAILED ({suite}) -- aborting deploy. Nothing was uploaded, "
              f"version was not bumped, and deploy_state.json was not updated, so "
              f"re-running after a fix will pick up the same {last_sha}..{current_sha} diff.")
        sys.exit(1)
    print("Test gate passed.")

    commit_subjects = [
        s for s in run_cmd(f"git log --format=%s {last_sha}..{current_sha}", cwd=repo_dir).split("\n") if s.strip()
    ]
    bump = bump_version(repo_dir, env, current_sha, commit_subjects)
    if bump:
        commit_files = bump["version_file"] + (f' {bump["changelog_file"]}' if bump["changelog_file"] else "")
        run_cmd(f"git add {commit_files}", cwd=repo_dir)
        new_version = bump["new_version"]
        run_cmd(f'git commit -m "chore: bump version to {new_version} for {env} deploy"', cwd=repo_dir)
        current_sha = run_cmd("git rev-parse HEAD", cwd=repo_dir)
        for f in (bump["version_file"], bump["changelog_file"]):
            if f and f not in files_to_upload:
                files_to_upload.append(f)
        print(f"Bumped {repo_name} to {bump['new_version']} ({bump['version_file']}) and committed {current_sha[:8]}.")
    else:
        print(f"No version.json found under {VERSION_FILE_CANDIDATES} -- skipping version bump.")

    # Serialize against other agents for the WHOLE session, not just the manifest
    # write. Two deploys interleaved on 2026-08-29 and each believed it had the
    # host to itself. flock is released by the OS when this process exits, so an
    # abort or a sys.exit below cannot strand it.
    if sync is not None:
        # 3600s, not sync.py's 300s default. Once the lock covers the whole
        # session rather than just the manifest write, 300s is SHORTER THAN A
        # REAL DEPLOY -- the prod run on 2026-08-29 took ~50 minutes. A waiting
        # agent would have hard-exited with a bare timeout that reads like a
        # stuck lockfile, and the natural reaction to that is to delete a lock
        # that is working correctly. Waiting is right; timing out is not.
        #
        # Kept alongside the gate lock (not replaced): sync.py takes this same
        # per-repo+env lock on its own, without deploy.py, so it is still what
        # serializes a deploy's FTP session against a bare sync.py run. Order is
        # always gate lock -> deploy lock, here and in v3 sync.py (which takes
        # the gate lock before its DeployLock), so the two cannot deadlock.
        #
        # The old unconditional "deploy lock currently held -> pid=..." print
        # that stood here read the lock FILE, not the lock: sync.py never clears
        # its text on release, so it named a long-dead holder (pid 30323 on
        # 2026-09-14) on every deploy. DeployLock.__enter__ already prints the
        # holder when -- and only when -- it is genuinely blocked.
        _deploy_lock = sync.DeployLock(repo_name, env, 3600)
        _deploy_lock.__enter__()

    print("Connecting to FTP...")
    ftp = ftplib.FTP(host)
    ftp.login(user, passwd)
    ftp.cwd(ftp_dir)

    # Shared boundary guard -- one home, bin/deploy_guard.py in the v3 checkout,
    # imported rather than copied. Three copies is three chances for the name
    # list to drift, and the previous version of this block lived only here
    # while the engine agents are actually dispatched against went unguarded.
    if not deploy_guard.refuse_boundary_deletions(files_to_delete, env, sys.argv):
        sys.exit(1)

    # Modification check. It lives HERE rather than in sync.py because sync.py
    # already catches modifications via its manifest on test, and putting a
    # second check beside it would mean two mechanisms with different failure
    # modes in one tool. deploy.py has no manifest -- and prod has no manifest
    # at all (verified 2026-08-30: test 2,103 entries, prod 0) -- so this
    # direct-read check is the only modification protection prod has today.
    if not deploy_guard.refuse_boundary_changes(ftp, files_to_upload, repo_dir,
                                                env, sys.argv):
        sys.exit(1)

    for fpath in files_to_delete:
        print(f"Deleting {fpath}...")
        try:
            ftp.delete(fpath)
        except Exception as e:
            print(f"Could not delete {fpath}: {e}")

    uploaded = []
    for fpath in files_to_upload:
        print(f"Uploading {fpath}...")
        local_path = os.path.join(repo_dir, fpath)
        if not os.path.exists(local_path):
            print(f"File missing locally: {local_path}")
            continue
            
        # Ensure remote dir exists
        remote_dir = os.path.dirname(fpath)
        if remote_dir:
            dirs = remote_dir.split("/")
            curr = ""
            for d in dirs:
                curr += d + "/"
                try:
                    ftp.cwd(curr)
                    ftp.cwd("/")
                    ftp.cwd(ftp_dir)
                except:
                    try:
                        ftp.mkd(curr)
                    except:
                        pass
        
        with open(local_path, "rb") as f:
            ftp.storbinary(f"STOR {fpath}", f)
        uploaded.append(fpath)

    # --- Post-upload verification -------------------------------------------
    # An interrupted deploy fails by TRUNCATION and by ABSENCE, and both have
    # now bitten production on 2026-08-29: lib/ArticleIngestionService.php
    # landed at ZERO BYTES, and api/ask.php landed without lib/EnginePresets.php
    # which it require_once's. Neither is visible to the upload loop, which
    # only knows storbinary() did not raise. Note require_once on a zero-byte
    # file SUCCEEDS -- the fatal arrives later at point of use, which is why
    # that outage presented to the user as "Network error" rather than
    # anything legible.
    problems = []

    # 1. Size check. Catches truncation and zero-byte writes. Cheap: one SIZE
    #    command per uploaded file, no re-download. Size is NOT identity -- a
    #    same-length different-content file passes this -- so it is a floor,
    #    not a guarantee.
    ftp.voidcmd("TYPE I")  # SIZE is refused in ASCII mode on many servers
    for fpath in uploaded:
        expected = os.path.getsize(os.path.join(repo_dir, fpath))
        try:
            actual = ftp.size(fpath)
        except Exception as e:
            problems.append(f"{fpath}: could not stat after upload ({e})")
            continue
        if actual is None:
            problems.append(f"{fpath}: server returned no size after upload")
        elif actual != expected:
            problems.append(f"{fpath}: uploaded {expected} bytes, server has {actual}")

    # 2. Dependency check. For every PHP file just deployed, every
    #    require/include of a __DIR__-relative path must EXIST on the server --
    #    whether or not this deploy included it. This is the check that would
    #    have caught the outage: ask.php was in the diff, EnginePresets.php was
    #    not, and nothing noticed the dangling requirement.
    dep_pattern = re.compile(r"""require(?:_once)?\s*\(?\s*__DIR__\s*\.\s*['"]([^'"]+)['"]""")
    checked_deps = set()
    for fpath in uploaded:
        if not fpath.endswith(".php"):
            continue
        try:
            src = open(os.path.join(repo_dir, fpath), "r", errors="replace").read()
        except Exception:
            continue
        for rel in dep_pattern.findall(src):
            dep = os.path.normpath(os.path.join(os.path.dirname(fpath), rel.lstrip("/")))
            if dep in checked_deps or not os.path.exists(os.path.join(repo_dir, dep)):
                continue  # only assert deps that exist locally; generated paths are not our business
            checked_deps.add(dep)
            try:
                if ftp.size(dep) is None:
                    problems.append(f"{fpath} requires {dep}, which is not readable on the server")
            except Exception:
                problems.append(f"{fpath} requires {dep}, which is MISSING on the server")

    # Record content for what we just uploaded. Cheap: we hash local files we
    # already have. This asserts what we INTENDED to upload -- if FTP truncated,
    # the manifest would claim a hash the server lacks, which is precisely what
    # the size check above exists to catch. The two together are what make this
    # trustworthy; neither alone is.
    if sync is not None and uploaded:
        try:
            files_map, _ = sync.fetch_manifest(ftp)
            for fpath in uploaded:
                files_map[fpath] = sync.sha256_file(os.path.join(repo_dir, fpath))
            for fpath in files_to_delete:
                files_map.pop(fpath, None)
            sync.write_manifest(ftp, ftp_dir, files_map, env)
            print(f"Manifest updated: {len(uploaded)} entries written, {len(files_map)} total.")
        except Exception as e:
            print(f"  ! manifest update FAILED ({e}); sync.py's next run will re-upload these files")

    ftp.quit()

    if problems:
        print("")
        print(f"DEPLOY VERIFICATION FAILED -- {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        print("")
        print("Files were uploaded but the result is not trustworthy. deploy_state.json "
              "was NOT updated and migrations were NOT triggered, so re-running after a "
              "fix recomputes the same diff. Re-run the deploy; if a dependency is "
              "genuinely absent, it is missing from the diff and needs deploying too.")
        sys.exit(1)

    print(f"Verified {len(uploaded)} uploaded file(s): sizes match, "
          f"{len(checked_deps)} dependencies present on server.")

    # MIGRATIONS COMPLETENESS GUARD (2026-09-03, Tarr's proposal after TEST
    # drifted 21 migration files behind across four agents). The diff-based
    # upload only carries files in THIS deploy's commit range; a deploy that
    # failed mid-way (or advanced deploy_state past a commit without
    # uploading) silently strands migration files forever, and the remote
    # runner's Pending list cannot see a file that is not on disk. So after
    # every upload, list the server's migrations directory and diff it
    # against git's. Extra remote files are reported, not fatal (drafts and
    # collisions have their own rules); MISSING files fail the deploy loudly.
    try:
        # The upload/verify phase may have closed the original control
        # connection; the guards use their OWN connection so a stale socket
        # cannot crash them (AttributeError on a closed sock escaped the
        # ftplib.all_errors net on 2026-09-03 and killed four deploys).
        gftp = ftplib.FTP(host)
        gftp.login(user, passwd)
        gftp.cwd(ftp_dir)
        migdir_local = os.path.join(repo_dir, "journalgpt", "migrations")
        if os.path.isdir(migdir_local):
            local_migs = {f for f in os.listdir(migdir_local) if f.endswith(".sql")}
            remote_migs = set()
            for entry in gftp.nlst("journalgpt/migrations"):
                base = entry.rsplit("/", 1)[-1]
                if base.endswith(".sql"):
                    remote_migs.add(base)
            missing_remote = sorted(local_migs - remote_migs)
            if missing_remote:
                # A shared-host NLST occasionally returns a short listing; a
                # "missing" file that reappears on an immediate re-list was
                # never stranded. Twice (2026-09-02) the guard failed a deploy
                # whose retry then passed with no intervening upload.
                relisted = set()
                for entry in gftp.nlst("journalgpt/migrations"):
                    base = entry.rsplit("/", 1)[-1]
                    if base.endswith(".sql"):
                        relisted.add(base)
                if relisted - remote_migs:
                    print(f"NOTE: first listing was short by {len(relisted - remote_migs)} "
                          "file(s); trusting the re-list.")
                remote_migs |= relisted
                missing_remote = sorted(local_migs - remote_migs)
            extra_remote = sorted(remote_migs - local_migs)
            if extra_remote:
                print(f"NOTE: {len(extra_remote)} migration file(s) on server but not in git: "
                      + ", ".join(extra_remote))
            if missing_remote:
                print("")
                print(f"MIGRATIONS GUARD FAILED on {env}: {len(missing_remote)} migration "
                      "file(s) exist in git but NOT on the server (stranded by an earlier "
                      "partial deploy): " + ", ".join(missing_remote))
                print("Upload them (they are outside this deploy's diff) and re-run. "
                      "deploy_state.json was NOT updated.")
                sys.exit(1)
            print(f"Migrations guard: {len(local_migs)} local == {len(remote_migs & local_migs)} present on server.")

        # CODE-FILE STALENESS GUARD (2026-09-03, after source.php sat stale on
        # prod for days while its read-backs "passed" through a different code
        # path). Compare file SIZES for the top-level journalgpt/*.php and
        # journalgpt/lib/*.php against the server listing. A size mismatch means
        # a stranded or stale file; a file size-equal-but-content-different can
        # still slip this (stated limit -- hashes would need a server helper),
        # but every stranding found so far changed the size. Missing files fail;
        # size mismatches fail; extra remote files are reported only.
        code_problems = []
        for sub in ("journalgpt", "journalgpt/lib"):
            local_dir = os.path.join(repo_dir, sub)
            if not os.path.isdir(local_dir):
                continue
            local_sizes = {f: os.path.getsize(os.path.join(local_dir, f))
                           for f in os.listdir(local_dir)
                           if f.endswith(".php") and os.path.isfile(os.path.join(local_dir, f))}
            remote_sizes = {}
            try:
                for line in gftp.mlsd(sub):
                    name, facts = line
                    if name.endswith(".php") and facts.get("type") == "file":
                        remote_sizes[name] = int(facts.get("size", -1))
            except ftplib.all_errors:
                # MLSD unsupported -- fall back to SIZE per file (slower but rare)
                try:
                    for name in local_sizes:
                        try:
                            remote_sizes[name] = gftp.size(f"{sub}/{name}")
                        except ftplib.all_errors:
                            remote_sizes[name] = None
                except ftplib.all_errors as e:
                    print(f"CODE GUARD could not read {sub} ({e}) -- treating as FAILURE.")
                    sys.exit(1)
            for name, lsize in sorted(local_sizes.items()):
                rsize = remote_sizes.get(name)
                if rsize is None:
                    code_problems.append(f"{sub}/{name}: MISSING on server")
                elif rsize != lsize:
                    code_problems.append(f"{sub}/{name}: size {rsize} on server vs {lsize} in git (STALE)")
        if code_problems:
            print("")
            print(f"CODE-FILE GUARD FAILED on {env}: {len(code_problems)} file(s) stale or missing:")
            for p in code_problems:
                print(f"  - {p}")
            print("These are outside this deploy's diff (stranded by an earlier partial "
                  "deploy). Upload them and re-run. deploy_state.json was NOT updated.")
            sys.exit(1)
        print("Code-file guard: journalgpt/ and lib/ php files match server sizes.")
    except ftplib.all_errors + (AttributeError,) as e:
        print(f"MIGRATIONS GUARD could not list the server directory ({e}) -- treating as FAILURE, "
              "not success: a guard that cannot read its input must not pass.")
        sys.exit(1)
    else:
        try:
            gftp.quit()
        except Exception:
            pass

    migration_verdict = trigger_remote_migration(repo_dir, env)

    # State is written regardless of the migration verdict: the FILES are on
    # the server and re-running would find an empty diff anyway. The verdict
    # decides the BANNER and the exit code instead -- the two things a human
    # or a calling script actually reads.
    state[repo_name][env] = current_sha
    record_ancestry(state, repo_name, env, tracking_ref, ancestry)
    if migration_verdict in ("succeeded", "not_applicable"):
        state[repo_name].pop(f"{env}_migrations_pending", None)
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

    if migration_verdict == "failed":
        state[repo_name][f"{env}_migrations_pending"] = True
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
        print("")
        print(f"DEPLOY INCOMPLETE on {env}: files uploaded and verified, but the "
              f"migration trigger FAILED. Any pending migration in "
              f"journalgpt/migrations/ is NOT applied. Run admin_migrate.php in a "
              f"browser on {env} (or re-run this deploy) and confirm before "
              f"trusting the site. Exiting nonzero so nothing downstream reads "
              f"this as a success.")
        sys.exit(2)
    elif migration_verdict == "skipped_config":
        print(f"Deployed files to {env}, but migrations were NOT triggered "
              f"(missing .env config, see above). Verify manually via admin_migrate.php.")
    else:
        print(f"Deployed successfully to {env}!")

    # main == production, by construction rather than by discipline.
    # Chip's ruling (Q-8a-8): main is production, test is test. Before this,
    # main fell 20 commits / 59 files behind test in a day and did not contain
    # four deployed security fixes -- anyone branching from it for a hotfix
    # started from a tree missing them. It was corrected by hand, which holds
    # only until someone forgets. This attaches the ref move to the event that
    # justifies it: a deploy that PASSED verification above.
    #
    # Fast-forward only, never force. If main is not an ancestor of what we just
    # shipped, something happened that a deploy script must not paper over --
    # say so and leave it for a human.
    if env == "prod":
        ff = subprocess.run(
            f"git merge-base --is-ancestor origin/main {current_sha}",
            shell=True, cwd=repo_dir, capture_output=True, text=True,
        )
        if ff.returncode == 0:
            push = subprocess.run(
                f"git push origin {current_sha}:main",
                shell=True, cwd=repo_dir, capture_output=True, text=True,
            )
            if push.returncode == 0:
                print(f"main fast-forwarded to {current_sha[:8]} (main == production).")
            else:
                print(f"  ! could not fast-forward main: {push.stderr.strip()[:200]}")
        else:
            print("  ! main is NOT an ancestor of the deployed commit -- NOT forcing. "
                  "main and the deployed tree have diverged; a human should look before "
                  "main is moved.")

if __name__ == "__main__":
    main()
