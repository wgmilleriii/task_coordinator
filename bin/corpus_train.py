#!/usr/bin/env python3
"""corpus_train.py -- the manual prod delivery path for
newmexicoptg.org's journalgpt/corpus/articles/*.md, since deploy.py
permanently excluded that path (commit 5fd26e8, Chip 2026-09-05:
"the md files can be excluded from the deploy process as article
conversion is going to be handled manually").

WHY THIS EXISTS. T-PTG-629 (Leamas, read-only investigation, 2026-09-12)
found deploy.py's corpus exclusion is CODE-LEVEL, not a branch or worktree
setting: no worktree cut against deploy.py, however it's built, can make
it ship a journalgpt/corpus/articles/*.md file. Direct FTP LIST against
prod confirmed the practical consequence: prod's corpus was frozen since
Aug 30 - Sep 2, 2026 (before the ruling took effect), and every stage-1
corpus commit made since has been unreachable. This tool is the "manual"
route the ruling asked for -- it never touches deploy.py's exclusion
list; it is a separate, narrowly-scoped uploader for exactly one path.

Deliberately different from deploy.py:
  - SCOPE-LOCKED to journalgpt/corpus/articles/*.md only. Every path this
    tool ever reads, diffs, uploads or deletes is asserted against
    CORPUS_PREFIX before use -- this is the one thing it must never get
    wrong, since it exists specifically to route around deploy.py's own
    safety net for every other path.
  - Comparison against prod is LIST-only: ftp.size() (SIZE) and MDTM,
    never RETR. A same-size different-content file cannot be told apart
    from an identical one this way -- exactly the same "floor, not a
    guarantee" caveat deploy.py's own post-upload size check carries.
  - Requires three DISTINCT --reviewed-by approvals, all on the exact SHA
    being executed, before --execute will touch anything. corpus/articles/
    is the one path class that has already burned prod twice by silent
    drop (T-PTG-152, 2026-08-27) and by destructive rewrite
    (T-PTG-650's reconcile_boundary_if_needed) -- this tool enforces the
    review discipline the old ad hoc "corpus train" worktrees used
    (mechanical / content / deploy reviewers) in code, not just process.
  - --dry-run is the default. Nothing uploads without an explicit
    --execute AND a passing review file.

Same conventions as deploy.py on purpose: .env / FTP_* credential
lookup, and a state file (corpus_deploy_state.json, sibling to
deploy_state.json) recording the last shipped SHA so the next train has
a base to diff from.

USAGE
  # Dry run against an explicit range -- always safe, no FTP writes:
  corpus_train.py <repo_dir> <SHA_A>..<SHA_B>

  # Dry run against a bare ref (base = corpus_deploy_state.json's last sha):
  corpus_train.py <repo_dir> test

  # Seed the ledger once, with no upload, so the next bare-ref run has a base:
  corpus_train.py <repo_dir> --seed-sha <sha>

  # Execute, after three reviewers have approved the exact target SHA:
  corpus_train.py <repo_dir> <range> --reviewed-by reviews.json --execute

reviews.json shape: a JSON list of {"reviewer": "...", "sha": "...",
"verdict": "APPROVE"} objects. At least three DISTINCT reviewer names
must APPROVE the exact SHA being executed.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

CORPUS_PREFIX = "journalgpt/corpus/articles/"
STATE_FILE_NAME = "corpus_deploy_state.json"
REPO_KEY = "NEWMEXICOPTG_ORG"  # this tool only ever targets newmexicoptg.org's corpus


def is_in_scope(path):
    """True only for a genuine journalgpt/corpus/articles/*.md path.

    A plain `path.startswith(CORPUS_PREFIX)` string check (what every call
    site used before this) is foolable by a traversal segment BEFORE the
    prefix reasserts itself, e.g. "journalgpt/corpus/articles/../../../etc/passwd"
    or an absolute path that happens to contain the prefix substring
    somewhere in the middle. Normalize first (os.path.normpath collapses
    '..' and '.' segments and is what actually gets handed to STOR/DELE/
    open() downstream), then re-check both the prefix and that no '..'
    segment or absolute form survived normalization -- a path that still
    escapes after normalizing was never in scope to begin with. This is
    the hardening item from feat-corpus-train's safety review (Mostyn +
    independent reader, 2026-09-12): everywhere else in this file already
    asserts against CORPUS_PREFIX, but a raw startswith() alone is not
    sufficient once a caller (a hand-edited --reviewed-by file cannot
    inject paths, but a future caller of build_manifest/execute directly
    could) hands in something adversarial."""
    normalized = os.path.normpath(path)
    if os.path.isabs(normalized):
        return False
    if normalized == ".." or normalized.startswith(f"..{os.sep}"):
        return False
    if f"{os.sep}..{os.sep}" in normalized or normalized.endswith(f"{os.sep}.."):
        return False
    return normalized.startswith(CORPUS_PREFIX) and normalized.endswith(".md")


def load_env():
    env_path = Path(os.path.dirname(__file__)).parent / ".env"
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()


def state_file_path():
    return Path(os.path.dirname(__file__)).parent / STATE_FILE_NAME


def load_state():
    p = state_file_path()
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return {}


def resolve_range(git_range_arg, state):
    """A range containing '..' is used verbatim. A bare ref is turned into
    '<last recorded corpus_deploy_state sha>..<ref>' -- mirrors deploy.py's
    own last_sha convention, so a corpus train and a code train answer
    "what changed since we last shipped" the same way."""
    if ".." in git_range_arg:
        return git_range_arg
    base = state.get("sha")
    if not base:
        print("No prior corpus_deploy_state.json sha recorded. Pass an explicit "
              "A..B range, or run --seed-sha <sha> first.")
        sys.exit(1)
    return f"{base}..{git_range_arg}"


def target_ref(git_range_arg):
    """The ref being deployed -- the right-hand side of a range, or the bare
    ref itself. This is what gets git-rev-parsed to the SHA reviews must
    name, and what local_blob_sha reads files at."""
    return git_range_arg.split("..")[-1] if ".." in git_range_arg else git_range_arg


def changed_corpus_files(repo_dir, git_range):
    """Returns [(status, path)] for journalgpt/corpus/articles/*.md paths
    only, relative to repo_dir. A rename/copy is split into a delete of the
    old path and an add of the new one, so the manifest's action logic
    (which only knows plain add/modify/delete) does not need to special-case
    it. Every path is scope-checked against CORPUS_PREFIX before being kept
    -- this is the first of several redundant scope checks in this file."""
    out = run_cmd(f"git diff --name-status {git_range} -- {CORPUS_PREFIX}", cwd=repo_dir)
    changes = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        if status[0] in ("R", "C") and len(parts) >= 3:
            old_path, new_path = parts[1], parts[2]
            if is_in_scope(old_path):
                changes.append(("D", old_path))
            if is_in_scope(new_path):
                changes.append(("A", new_path))
            continue
        path = parts[-1]
        if not is_in_scope(path):
            continue
        changes.append((status[0], path))
    return changes


def local_blob_sha(repo_dir, ref, path):
    """git's own blob hash for path as it exists at ref -- the manifest's
    'local sha'. A path deleted at ref has none."""
    result = subprocess.run(
        f"git rev-parse {ref}:{path}", shell=True, cwd=repo_dir,
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def ftp_stat(ftp, remote_path):
    """LIST-only remote probe: (size:int|None, mdtm:str|None). Never RETR --
    this tool has no code path that downloads a corpus file's content."""
    size = None
    mdtm = None
    try:
        ftp.voidcmd("TYPE I")
        size = ftp.size(remote_path)
    except Exception:
        size = None
    try:
        resp = ftp.sendcmd(f"MDTM {remote_path}")
        parts = resp.split()
        if len(parts) >= 2:
            mdtm = parts[-1]
    except Exception:
        mdtm = None
    return size, mdtm


def build_manifest(repo_dir, ref, changes, ftp, ftp_dir):
    """The only network calls here are ftp_stat's, so a fake ftp object
    exposing .size()/.sendcmd()/.voidcmd() is all a test needs -- no real
    connection required to exercise this function."""
    manifest = []
    for status, path in changes:
        assert is_in_scope(path), f"scope violation: {path}"
        remote_path = ftp_dir.rstrip("/") + "/" + path
        prod_size, prod_mdtm = ftp_stat(ftp, remote_path)

        if status == "D":
            local_sha = None
            action = "delete" if prod_size is not None else "skip-absent"
        else:
            local_sha = local_blob_sha(repo_dir, ref, path)
            local_path = Path(repo_dir) / path
            local_size = local_path.stat().st_size if local_path.exists() else None
            if prod_size is None:
                action = "upload"
            elif local_size is not None and local_size == prod_size:
                # Size match is a floor, not identity (same caveat as
                # deploy.py's own post-upload check) -- this tool is LIST-only
                # by design, so this is as far as it can verify without an
                # RETR/download the task explicitly rules out.
                action = "skip-identical"
            else:
                action = "upload"

        manifest.append({
            "path": path,
            "git_status": status,
            "local_sha": local_sha,
            "prod_size": prod_size,
            "prod_mdtm": prod_mdtm,
            "action": action,
        })
    return manifest


def print_manifest(manifest):
    print(f"{'ACTION':<15} {'PATH':<70} {'LOCAL SHA':<10} {'PROD SIZE':<10} PROD MDTM")
    for e in manifest:
        local_sha_short = (e["local_sha"] or "-")[:8]
        prod_size_str = str(e["prod_size"]) if e["prod_size"] is not None else "-"
        print(f"{e['action']:<15} {e['path']:<70} {local_sha_short:<10} "
              f"{prod_size_str:<10} {e['prod_mdtm'] or '-'}")


def load_reviews(reviewed_by_path):
    with open(reviewed_by_path) as f:
        return json.load(f)


def validate_reviews(reviews, expected_sha):
    """Three DISTINCT named reviewers, all APPROVE, all on the exact SHA
    being executed -- an approval on any other SHA (an earlier revision of
    the same train included) does not count. Returns (ok, reason)."""
    if not isinstance(reviews, list):
        return False, "--reviewed-by file must be a JSON list of {reviewer, sha, verdict}"
    approvals = [r for r in reviews
                 if isinstance(r, dict)
                 and r.get("verdict") == "APPROVE"
                 and r.get("sha") == expected_sha]
    reviewers = {r.get("reviewer") for r in approvals if r.get("reviewer")}
    if len(reviewers) < 3:
        return False, (f"need 3 distinct APPROVE reviewers on sha {expected_sha}, "
                        f"found {len(reviewers)}: {sorted(reviewers)}")
    return True, f"{len(reviewers)} distinct APPROVE reviewers on {expected_sha}: {sorted(reviewers)}"


def execute(ftp, repo_dir, manifest):
    """STOR uploads, DELE deletions, size read-back for every touched file.
    Returns (uploaded, deleted, problems)."""
    uploaded, deleted, problems = [], [], []
    for e in manifest:
        path = e["path"]
        assert is_in_scope(path), f"scope violation: {path}"
        if e["action"] == "delete":
            try:
                ftp.delete(path)
                deleted.append(path)
            except Exception as ex:
                problems.append(f"{path}: delete failed ({ex})")
        elif e["action"] == "upload":
            local_path = Path(repo_dir) / path
            if not local_path.exists():
                problems.append(f"{path}: missing locally, cannot upload")
                continue
            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {path}", f)
            uploaded.append(path)
        # skip-identical / skip-absent: nothing to do.

    ftp.voidcmd("TYPE I")
    for path in uploaded:
        expected = (Path(repo_dir) / path).stat().st_size
        try:
            actual = ftp.size(path)
        except Exception as ex:
            problems.append(f"{path}: could not stat after upload ({ex})")
            continue
        if actual != expected:
            problems.append(f"{path}: uploaded {expected} bytes, server has {actual}")
    for path in deleted:
        try:
            actual = ftp.size(path)
            if actual is not None:
                problems.append(f"{path}: still present after delete (size {actual})")
        except Exception:
            pass  # SIZE raising on a deleted path is the expected outcome.

    return uploaded, deleted, problems


def write_ledger(sha, manifest, reviews):
    state = load_state()
    state["sha"] = sha
    state["deployed_at"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    state["files"] = [e["path"] for e in manifest if e["action"] in ("upload", "delete")]
    state["manifest"] = manifest
    state["reviewed_by"] = reviews
    with open(state_file_path(), "w") as f:
        json.dump(state, f, indent=2)
    return state


def connect_ftp(host, user, passwd, ftp_dir):
    import ftplib
    ftp = ftplib.FTP(host)
    ftp.login(user, passwd)
    ftp.cwd(ftp_dir)
    return ftp


def ftp_credentials():
    def var(field):
        specific = f"FTP_{field}_{REPO_KEY}_PROD"
        generic = f"FTP_{field}_PROD"
        return os.environ.get(specific) or os.environ.get(generic)
    return var("HOST"), var("USER"), var("PASS"), (var("DIR") or "/")


def main():
    parser = argparse.ArgumentParser(
        description="Manual journalgpt/corpus/articles/ -> prod uploader, "
                    "the ONLY route since deploy.py permanently excluded that "
                    "path (Chip, 2026-09-05, commit 5fd26e8).")
    parser.add_argument("repo_dir")
    parser.add_argument("git_range", nargs="?",
                         help="A..B explicit range, or a bare ref (resolved "
                              "against corpus_deploy_state.json's last sha)")
    parser.add_argument("--reviewed-by",
                         help="JSON file: list of {reviewer, sha, verdict}. "
                              "Three distinct APPROVE entries on the exact "
                              "target SHA are required before --execute will "
                              "upload or delete anything.")
    parser.add_argument("--execute", action="store_true",
                         help="Actually upload/delete. Default is dry-run: "
                              "print the manifest and exit 0, no FTP writes.")
    parser.add_argument("--seed-sha",
                         help="Record this sha as corpus_deploy_state.json's "
                              "base with no upload, so the next bare-ref run "
                              "has something to diff against.")
    args = parser.parse_args()

    repo_dir = os.path.abspath(args.repo_dir)

    if args.seed_sha:
        state = load_state()
        state["sha"] = args.seed_sha
        with open(state_file_path(), "w") as f:
            json.dump(state, f, indent=2)
        print(f"Seeded corpus_deploy_state.json with {args.seed_sha}.")
        return

    if not args.git_range:
        parser.error("git_range is required unless --seed-sha is given")

    state = load_state()
    git_range = resolve_range(args.git_range, state)
    ref = target_ref(args.git_range)
    target_sha = run_cmd(f"git rev-parse {ref}", cwd=repo_dir)

    changes = changed_corpus_files(repo_dir, git_range)
    if not changes:
        print(f"No {CORPUS_PREFIX}*.md changes in {git_range}.")
        return

    load_env()
    host, user, passwd, ftp_dir = ftp_credentials()
    if not all([host, user, passwd]):
        print(f"Missing FTP_*_{REPO_KEY}_PROD (or generic FTP_*_PROD) credentials in .env.")
        sys.exit(1)

    ftp = connect_ftp(host, user, passwd, ftp_dir)
    try:
        manifest = build_manifest(repo_dir, ref, changes, ftp, ftp_dir)
        print_manifest(manifest)

        actionable = [e for e in manifest if e["action"] in ("upload", "delete")]
        if not actionable:
            print("Nothing to upload or delete (all skip-identical / skip-absent).")
            return

        if not args.execute:
            print(f"\nDRY RUN -- {len(actionable)} file(s) would change on prod "
                  f"at target sha {target_sha}. Re-run with --reviewed-by <file> "
                  f"--execute to apply.")
            return

        if not args.reviewed_by:
            print(f"--execute requires --reviewed-by <file> naming three APPROVE "
                  f"reviews on sha {target_sha}.")
            sys.exit(1)
        reviews = load_reviews(args.reviewed_by)
        ok, reason = validate_reviews(reviews, target_sha)
        if not ok:
            print(f"Review gate FAILED: {reason}")
            sys.exit(1)
        print(f"Review gate passed: {reason}")

        uploaded, deleted, problems = execute(ftp, repo_dir, manifest)
        write_ledger(target_sha, manifest, reviews)
        print(f"Uploaded {len(uploaded)}, deleted {len(deleted)}.")
        if problems:
            print("PROBLEMS:")
            for p in problems:
                print(f"  {p}")
            sys.exit(1)
        print(f"corpus_deploy_state.json updated: sha={target_sha}")
    finally:
        try:
            ftp.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
