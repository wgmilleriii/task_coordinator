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

  # T-PTG-1012: ship article_html bundles (the pages members READ) by csv.
  # SCOPE-LOCKED to corpus/article_html/<csv>.json for exactly the csvs named;
  # <ref> is a bare ref (no A..B): the files are read from that frozen tree.
  corpus_train.py <repo_dir> <ref> --bundles 78,215 --env test [--execute]
  corpus_train.py <repo_dir> <ref> --bundles 78,215 --reviewed-by r.json --execute  # prod

  # T-PTG-1012 (R-132-3): ship files PRESENT in the frozen tree but ABSENT on
  # the server (the tool ships git diffs, so an unchanged file whose directory
  # never reached the server cannot otherwise ship). Never overwrites.
  corpus_train.py <repo_dir> <ref> --paths journalgpt/corpus/articles/PTJ-2022-10/3825.md

NOTES. The ledger is written to the repo ROOT, not beside the script (a worktree
run would otherwise strand it). A PARTIAL upload (some files stored, then a
problem) is still ledgered as shipped and exits 1 -- pre-existing on the .md
path; read the PROBLEMS list before trusting the ledger entry.

reviews.json shape: a JSON list of {"reviewer": "...", "sha": "...",
"verdict": "APPROVE"} objects. At least three DISTINCT reviewer names
must APPROVE the exact SHA being executed.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

CORPUS_PREFIX = "journalgpt/corpus/articles/"
STATE_FILE_NAME = "corpus_deploy_state.json"
STATE_FILE_NAME_TEST = "corpus_deploy_state_test.json"
ENV = "prod"  # set from --env; "test" uses FTP_*_TEST and its own ledger, no review gate
REPO_KEY = "NEWMEXICOPTG_ORG"  # this tool only ever targets newmexicoptg.org's corpus


BUNDLE_PREFIX = "journalgpt/corpus/article_html/"
_BUNDLE_RE = re.compile(r"^journalgpt/corpus/article_html/(\d+)\.json$")
# Set from --bundles / --paths in main(). Empty by default, so the upload loop
# refuses every bundle path unless a flag named it.
ALLOWED_BUNDLES = frozenset()   # csv numbers, as strings
ALLOWED_PATHS = frozenset()     # exact paths named by --paths


def _normalized_relative(path):
    """normpath, or None if the path is absolute or escapes via '..'."""
    normalized = os.path.normpath(path)
    if os.path.isabs(normalized):
        return None
    if normalized == ".." or normalized.startswith(f"..{os.sep}"):
        return None
    if f"{os.sep}..{os.sep}" in normalized or normalized.endswith(f"{os.sep}.."):
        return None
    return normalized


def bundle_path(csv):
    """corpus/article_html/<csv>.json for a purely numeric csv, else ValueError."""
    if not re.fullmatch(r"\d+", str(csv)):
        raise ValueError(f"not a csv number: {csv!r}")
    return f"{BUNDLE_PREFIX}{csv}.json"


def is_bundle_in_scope(path, csvs):
    """True only for journalgpt/corpus/article_html/<csv>.json where <csv> is
    one of `csvs`. Normalized first, and the normalized form must equal the
    input, so nothing that normpath would rewrite ever reaches STOR."""
    normalized = _normalized_relative(path)
    if normalized is None or normalized != path:
        return False
    m = _BUNDLE_RE.match(normalized)
    return bool(m) and m.group(1) in csvs


def is_shippable(path):
    """The scope every upload/delete call site asserts: a corpus .md, a bundle
    named by --bundles, or a path named EXACTLY by --paths that is itself a
    corpus .md or an article_html bundle. Nothing else, ever (deploy.py's own
    exclusion stays untouched)."""
    if is_in_scope(path):
        return True
    if is_bundle_in_scope(path, ALLOWED_BUNDLES):
        return True
    if path in ALLOWED_PATHS and path_class_ok(path):
        return True
    return False


def path_class_ok(path):
    """A --paths entry must be a corpus .md or ANY article_html/<csv>.json."""
    if is_in_scope(path):
        return True
    normalized = _normalized_relative(path)
    return normalized == path and bool(_BUNDLE_RE.match(normalized))


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


CSV_INDEX_PATH = "journalgpt/corpus/articles/csv_number_index.json"


def csv_index_staleness(repo_dir, ref):
    """T-PTG-678: compare csv_number_index.json AT ref with the csv_number
    frontmatter of every journalgpt/corpus/articles/*/*.md AT ref (git
    plumbing only, no working tree). Returns None when ref has no index,
    else {"added": [...], "removed": [...], "repointed": [...]} of csv
    numbers (strings). The index is not shipped by this tool (it is .json,
    deploy.py carries it), but Stage 1 review, source.php and the quiz read
    it, so a train that moves or mints articles without regenerating it
    leaves those pages pointing at files that are no longer there."""
    shown = subprocess.run(["git", "show", f"{ref}:{CSV_INDEX_PATH}"], cwd=repo_dir,
                           capture_output=True, text=True)
    if shown.returncode != 0:
        return None
    try:
        index = {str(k): v for k, v in json.loads(shown.stdout).items()}
    except (ValueError, AttributeError):
        index = {}
    grep = subprocess.run(
        ["git", "grep", "-E", r"^csv_number:[[:space:]]*[0-9]+[[:space:]]*$", ref, "--",
         "journalgpt/corpus/articles/*/*.md"],
        cwd=repo_dir, capture_output=True, text=True)
    truth = {}
    prefix = f"{ref}:{CORPUS_PREFIX}"
    for line in grep.stdout.splitlines():
        if not line.startswith(prefix):
            continue
        path, _, value = line[len(prefix):].rpartition(":csv_number:")
        truth[value.strip()] = path
    return {
        "added": sorted(set(truth) - set(index), key=int),
        "removed": sorted((k for k in set(index) - set(truth)), key=lambda k: int(k) if k.isdigit() else -1),
        "repointed": sorted((k for k in set(index) & set(truth) if index[k] != truth[k]), key=int),
    }


def warn_if_csv_index_stale(repo_dir, ref):
    """Prints a WARNING (never blocks) when the train ref's index disagrees
    with its own frontmatter. Returns True when a warning was printed."""
    diff = csv_index_staleness(repo_dir, ref)
    if diff is None or not any(diff.values()):
        return False
    print(f"WARNING: {CSV_INDEX_PATH} at {ref} is stale against corpus frontmatter: "
          f"{len(diff['added'])} missing, {len(diff['removed'])} extra, "
          f"{len(diff['repointed'])} repointed"
          + (f" (e.g. csv {diff['repointed'][0]})" if diff["repointed"] else "") + ".")
    print("  Regenerate on the train branch before shipping: "
          "php journalgpt/cli/build_article_markdown_index.php, commit, deploy via deploy.py (T-PTG-678).")
    return True


STATE_DIR_OVERRIDE = None  # --state-dir


def resolve_state_dir(script_dir=None):
    """Where the ledger lives: the REAL repo root, never a worktree's copy.
    Review of kestrel-1012: the ledger was written beside the script, so a run
    from a worktree stranded its record outside the root's corpus_deploy_state*.json
    and the next bare-ref train would have diffed from a stale base. The root is
    the parent of `git rev-parse --git-common-dir` (the same for every worktree
    of the repo). Refuses (SystemExit) when it cannot be determined."""
    if STATE_DIR_OVERRIDE:
        return Path(STATE_DIR_OVERRIDE)
    script_dir = script_dir or os.path.dirname(os.path.abspath(__file__))
    r = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                       cwd=script_dir, capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        print("Refused: cannot resolve the task_coordinator repo root for the ledger; "
              "pass --state-dir <dir>.")
        sys.exit(1)
    return Path(r.stdout.strip()).parent


def state_file_path():
    name = STATE_FILE_NAME_TEST if ENV == "test" else STATE_FILE_NAME
    return resolve_state_dir() / name


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
        assert is_shippable(path), f"scope violation: {path}"
        remote_path = ftp_dir.rstrip("/") + "/" + path
        prod_size, prod_mdtm = ftp_stat(ftp, remote_path)

        if status == "P":
            # --paths: ship ONLY what the server lacks; never overwrite.
            local_sha = local_blob_sha(repo_dir, ref, path)
            action = "upload" if prod_size is None else "skip-present"
        elif status == "D":
            local_sha = None
            action = "delete" if prod_size is not None else "skip-absent"
        else:
            local_sha = local_blob_sha(repo_dir, ref, path)
            local_path = Path(repo_dir) / path
            local_size = local_path.stat().st_size if local_path.exists() else None
            if prod_size is None:
                action = "upload"
            elif local_size is not None and local_size == prod_size:
                # Size match is a floor, not identity. 2026-09-26: the
                # ASPT-1950-01 repair train carried a one-digit OCR fix
                # (.80888 -> .80883) that left the file the same size, and
                # this branch marked it skip-identical -- the fix would never
                # have reached prod. So a size match now costs one RETR and a
                # byte comparison; only a truly identical file is skipped. A
                # fake ftp without retrbinary (tests) keeps the old floor.
                action = "skip-identical"
                if hasattr(ftp, "retrbinary") and local_path.exists():
                    remote_bytes = bytearray()
                    ftp.retrbinary(f"RETR {remote_path}", remote_bytes.extend)
                    if bytes(remote_bytes) != local_path.read_bytes():
                        action = "upload"
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


def _blob_exists(repo_dir, ref, path):
    return local_blob_sha(repo_dir, ref, path) is not None


def bundle_changes(repo_dir, ref, csvs):
    """[("A", path)] for each named csv's bundle as it exists at ref. A csv that
    is not numeric, or whose bundle is absent at ref, refuses the whole run."""
    out = []
    for csv in csvs:
        try:
            path = bundle_path(csv)
        except ValueError as ex:
            print(f"--bundles refused: {ex}")
            sys.exit(1)
        if not _blob_exists(repo_dir, ref, path):
            print(f"--bundles refused: {path} does not exist at {ref}.")
            sys.exit(1)
        stale, note = bundle_staleness(repo_dir, ref, csv)
        if stale:
            print(f"--bundles refused: csv {csv}: {note}. Regenerate the bundle from the .md "
                  f"the train ships first (R-132-9).")
            sys.exit(1)
        print(f"  stale-check csv {csv}: {note}")
        out.append(("A", path))
    return out


def path_changes(repo_dir, ref, paths):
    """[("P", path)] for each --paths entry. Refuses a path that is not a corpus
    .md or an article_html/<csv>.json, or that is absent from the tree at ref."""
    out = []
    for path in paths:
        if not path_class_ok(path):
            print(f"--paths refused: {path} is outside corpus/articles/*.md and "
                  f"corpus/article_html/<csv>.json.")
            sys.exit(1)
        if not _blob_exists(repo_dir, ref, path):
            print(f"--paths refused: {path} does not exist at {ref}.")
            sys.exit(1)
        m = _BUNDLE_RE.match(path)
        if m:
            stale, note = bundle_staleness(repo_dir, ref, m.group(1))
            if stale:
                print(f"--paths refused: {path}: {note}. Regenerate the bundle first (R-132-9).")
                sys.exit(1)
        out.append(("P", path))
    return out


def verify_tree_matches_ref(repo_dir, ref, changes):
    """The manifest compares, and execute() uploads, the WORKING-TREE file, while
    the review gate and the ledger name the sha at ref. A dirty or stale checkout
    would therefore ship bytes nobody reviewed. Refuse unless every named file's
    working-tree content hashes to its blob at ref (run from a clean worktree)."""
    bad = []
    for _status, path in changes:
        want = local_blob_sha(repo_dir, ref, path)
        r = subprocess.run(["git", "hash-object", "--", path], cwd=repo_dir,
                           capture_output=True, text=True)
        if r.returncode != 0 or r.stdout.strip() != want:
            bad.append(path)
    if bad:
        print(f"Refused: working tree differs from {ref} for: {bad}. "
              f"Run from a clean worktree checked out at the ref.")
        sys.exit(1)


DRIFT_LIMIT = 0.03  # unmatched share of the bundle's word 6-grams; good bundles measured 0.004-0.018


def _words(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def _shingles(words, n=6):
    return {" ".join(words[i:i + n]) for i in range(max(0, len(words) - n + 1))}


def bundle_staleness(repo_dir, ref, csv):
    """(stale, note). R-132-9: a bundle built from a .md that was later repaired
    still carries the old text (csv 3829, PTJ-2022-10). Bundles record NO source
    hash (0 of 3,874 at origin/test), so this is a CONTENT check instead:
    the share of the bundle's word 6-grams that appear nowhere in the corpus .md
    files carrying csv_number: <csv> at ref (the .md plus any -unindexed-back-
    matter sibling that carries it). Above DRIFT_LIMIT the bundle holds text the
    shipped .md no longer has -> refuse; the note always states the number.
    A date proxy (bundle generated_at vs .md commit date) was tried and
    discarded: it flagged the four bundles built 81 seconds before their own
    .md was committed, all known good.
    CANNOT catch: text the .md has but the bundle lacks (one-directional);
    stale text smaller than ~DRIFT_LIMIT of the bundle (a few lines); a bundle
    paragraph that is tables/markup the .md renders differently (the measured
    floor for good bundles is 0.4-1.8%). A heuristic, not a hash."""
    raw = subprocess.run(["git", "show", f"{ref}:{bundle_path(csv)}"], cwd=repo_dir,
                         capture_output=True, text=True)
    if raw.returncode != 0:
        return True, f"cannot read bundle at {ref}"
    try:
        paragraphs = json.loads(raw.stdout)["paragraphs"]
    except Exception as ex:
        return True, f"bundle has no usable paragraphs ({ex})"
    g = subprocess.run(["git", "grep", "-l", "-E", f"^csv_number: {csv}$", ref, "--", CORPUS_PREFIX],
                       cwd=repo_dir, capture_output=True, text=True)
    mds = [ln.split(":", 1)[1] for ln in g.stdout.splitlines() if ":" in ln and ln.endswith(".md")]
    if not mds:
        return False, "no corpus .md carries this csv_number at the ref; staleness not checkable"
    md_text = " ".join(subprocess.run(["git", "show", f"{ref}:{md}"], cwd=repo_dir,
                                      capture_output=True, text=True).stdout for md in mds)
    bundle_sh = _shingles(_words(" ".join(p if isinstance(p, str) else json.dumps(p) for p in paragraphs)))
    if not bundle_sh:
        return False, "bundle has no text to compare"
    drift = len(_shingles_minus(bundle_sh, _shingles(_words(md_text)))) / len(bundle_sh)
    if drift > DRIFT_LIMIT:
        return True, (f"{drift:.1%} of the bundle's text is absent from its .md {mds} "
                      f"(limit {DRIFT_LIMIT:.0%}): built from a different .md")
    return False, f"{drift:.1%} of bundle text absent from its .md (limit {DRIFT_LIMIT:.0%}; heuristic, one-directional)"


def _shingles_minus(a, b):
    return a - b


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


def ensure_remote_dirs(ftp, path):
    """MKD every missing parent of a relative remote path (a new issue folder
    such as PTJ-2026-09 on its first train). MKD on an existing directory
    raises error_perm, which is the normal case and is ignored; the STOR that
    follows is what reports a real failure. Never cwd()s, so the connection
    stays rooted at ftp_dir. Also used by tests with a fake ftp exposing mkd()."""
    parts = path.split("/")[:-1]
    curr = ""
    for d in parts:
        curr = f"{curr}{d}" if not curr else f"{curr}/{d}"
        try:
            ftp.mkd(curr)
        except Exception:
            pass


def execute(ftp, repo_dir, manifest):
    """STOR uploads, DELE deletions, size read-back for every touched file.
    Returns (uploaded, deleted, problems)."""
    uploaded, deleted, problems = [], [], []
    for e in manifest:
        path = e["path"]
        assert is_shippable(path), f"scope violation: {path}"
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
            ensure_remote_dirs(ftp, path)
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


def write_ship_ledger(sha, kind, manifest, reviews):
    """Ledger entry for a --bundles/--paths ship. Appended to state["ships"];
    state["sha"]/["files"] -- the .md diff base for the NEXT bare-ref train --
    are deliberately NOT touched: moving them would make the next .md train
    diff from a sha that never shipped its .md changes."""
    state = load_state()
    state.setdefault("ships", []).append({
        "kind": kind,
        "sha": sha,
        "env": ENV,
        "deployed_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files": [e["path"] for e in manifest if e["action"] in ("upload", "delete")],
        "manifest": manifest,
        "reviewed_by": reviews,
    })
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
    suffix = ENV.upper()
    def var(field):
        specific = f"FTP_{field}_{REPO_KEY}_{suffix}"
        generic = f"FTP_{field}_{suffix}"
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
    parser.add_argument("--env", choices=["prod", "test"], default="prod",
                        help="Target server. 'test' (test.newmexicoptg.org) uses the "
                             "FTP_*_TEST credentials and corpus_deploy_state_test.json "
                             "and needs no --reviewed-by: it exists so humans can judge "
                             "re-cut files on the test review page before a prod train. "
                             "'prod' (default) keeps the three-reviewer gate.")
    parser.add_argument("--bundles",
                        help="Comma-separated csv numbers: ship ONLY "
                             "journalgpt/corpus/article_html/<csv>.json for those "
                             "csvs, read from the bare ref given as git_range "
                             "(T-PTG-1012). Same gate per env.")
    parser.add_argument("--paths",
                        help="Comma-separated corpus paths (corpus/articles/*.md or "
                             "corpus/article_html/<csv>.json) present at the ref but "
                             "ABSENT on the server; never overwrites (R-132-3).")
    parser.add_argument("--state-dir",
                        help="Directory holding corpus_deploy_state*.json. Default: the "
                             "task_coordinator repo ROOT (git common dir's parent), so a "
                             "run from a worktree still writes the root's ledger.")
    parser.add_argument("--seed-sha",
                         help="Record this sha as corpus_deploy_state.json's "
                              "base with no upload, so the next bare-ref run "
                              "has something to diff against.")
    args = parser.parse_args()
    global ENV, STATE_DIR_OVERRIDE
    ENV = args.env
    STATE_DIR_OVERRIDE = args.state_dir

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
    ship_kind = None
    if args.bundles or args.paths:
        if ".." in args.git_range:
            parser.error("--bundles/--paths take a bare ref, not an A..B range")
        ref = args.git_range
        target_sha = run_cmd(f"git rev-parse {ref}", cwd=repo_dir)
        global ALLOWED_BUNDLES, ALLOWED_PATHS
        csvs = [c.strip() for c in (args.bundles or "").split(",") if c.strip()]
        plist = [p.strip() for p in (args.paths or "").split(",") if p.strip()]
        changes = bundle_changes(repo_dir, ref, csvs) + path_changes(repo_dir, ref, plist)
        verify_tree_matches_ref(repo_dir, ref, changes)
        ALLOWED_BUNDLES = frozenset(csvs)
        ALLOWED_PATHS = frozenset(plist)
        ship_kind = "+".join(k for k, v in (("bundles", csvs), ("paths", plist)) if v)
        if not changes:
            print("--bundles/--paths named nothing.")
            return
    else:
        git_range = resolve_range(args.git_range, state)
        ref = target_ref(args.git_range)
        target_sha = run_cmd(f"git rev-parse {ref}", cwd=repo_dir)
        warn_if_csv_index_stale(repo_dir, ref)

        changes = changed_corpus_files(repo_dir, git_range)
        if not changes:
            print(f"No {CORPUS_PREFIX}*.md changes in {git_range}.")
            return

    load_env()
    host, user, passwd, ftp_dir = ftp_credentials()
    if not all([host, user, passwd]):
        print(f"Missing FTP_*_{REPO_KEY}_{ENV.upper()} (or generic FTP_*_{ENV.upper()}) credentials in .env.")
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
            print(f"\nDRY RUN -- {len(actionable)} file(s) would change on {ENV} "
                  f"at target sha {target_sha}. Re-run with "
                  f"{'--execute' if ENV == 'test' else '--reviewed-by <file> --execute'} to apply.")
            return

        if ENV == "test":
            reviews = []
            print("Target is TEST: no review gate (test corpus is for human judging, not members).")
        elif not args.reviewed_by:
            print(f"--execute requires --reviewed-by <file> naming three APPROVE "
                  f"reviews on sha {target_sha}.")
            sys.exit(1)
        else:
            reviews = load_reviews(args.reviewed_by)
            ok, reason = validate_reviews(reviews, target_sha)
            if not ok:
                print(f"Review gate FAILED: {reason}")
                sys.exit(1)
            print(f"Review gate passed: {reason}")

        uploaded, deleted, problems = execute(ftp, repo_dir, manifest)
        if ship_kind:
            write_ship_ledger(target_sha, ship_kind, manifest, reviews)
        else:
            write_ledger(target_sha, manifest, reviews)
        print(f"Uploaded {len(uploaded)}, deleted {len(deleted)}.")
        if problems:
            print("PROBLEMS:")
            for p in problems:
                print(f"  {p}")
            sys.exit(1)
        print(f"{state_file_path().name} updated: sha={target_sha}")
    finally:
        try:
            ftp.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
