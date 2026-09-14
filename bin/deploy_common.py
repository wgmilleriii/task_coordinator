#!/usr/bin/env python3
"""Deploy helpers shared by v3 sync.py and both deploy.py copies.

Kept BYTE-IDENTICAL in task_coordinator/bin and task_coordinator_v3/bin, like
gate_lock.py. Edit both copies together.

WHY (2026-09-14, round-3 reader): sync.py used to `from deploy import
get_repo_excludes, should_exclude, run_test_gate`, and task_coordinator (v1)
deploy.py loads sync.py from the v3 checkout. So every v1 deploy executed
whatever deploy.py sat in the v3 checkout, uncommitted edits included, and a
broken v3 deploy.py would make v1 deploy.py refuse (it fails closed without
sync). sync.py now imports NOTHING from deploy; the helpers live here.

WHAT IS HERE
  * The exclusion rules and matcher sync.py has always used, moved verbatim
    from v3 deploy.py (which re-imports them, so its behaviour is unchanged).
    v1 deploy.py deliberately keeps its OWN exclusion list and matcher; the
    two sets differ today and unifying them would change what v1 ships.
  * run_test_gate(repo_dir, lock, candidates): the gate runner, with the lock
    fd passed into the gate child. Each caller passes its own suite list.

This module must not import deploy, sync, deploy_guard or deploy_allowlist.
"""
import os
import subprocess
from pathlib import Path

import gate_lock

# Exclusion patterns. Per-repo overrides let a repo's local deploy match its
# own CI workflow's filter instead of inheriting one shaped around another
# repo's conventions (e.g. intypiano's deploy.yml excludes only README.md,
# not every .md).
#
# CORRECTED 2026-09-02. This comment used to cite "docs/experts/*.md and
# DEPLOY_CHANGELOG.md" as the reason intypiano sets exclude_all_md False.
# Half of that was never true: the "docs/" directory pattern wins, so nothing
# under docs/ has ever deployed to intypiano -- correctly, since docs/ holds
# internal HANDOFF-*.md notes. The real and only justification is the root
# changelogs, which changelog.php reads off disk at the webroot.
#
# What exclude_all_md False actually does today is ship 332 .md files, of
# which 2 are the changelogs; the rest are internal planning notes
# (AI_STARTUP_PROTOCOL.md, ADMIN_PAGES_SUMMARY.md, .fleet_context.md) and
# vendor readmes. Narrowing this to md_allow_prefixes for the two changelogs
# is the obvious next step and is NOT done here -- see
# docs/40-Operations/deploy-policy.md section 2.3.
DEFAULT_EXCLUDES = [
    ".git/", ".github/", "docs/", "tasks/", ".fleet/", "node_modules/", ".gitignore",
    "graphify-out/", "scratch/", "__pycache__/", ".pyc",
    "protected_assets/article_images/", "journalgpt/corpus/article_html/",
    # Agent + editor tooling. Found live on production 2026-08-29: .mcp.json
    # was publicly downloadable WITH a real CHORD_TOKEN in it, alongside
    # .claude/skills/** and .impeccable/. None of this is site content and
    # all of it is useful reconnaissance (or, for .mcp.json, a credential).
    # The FTP root is the webroot here, so anything tracked at repo root is
    # served unless excluded.
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
    "bin/", "tests/", ".venv/", ".DS_Store",
]
DEFAULT_EXCLUDE_ALL_MD = True  # generic default: skip every *.md file

REPO_EXCLUDES = {
    "intypiano": {
        "patterns": [
            ".git/", ".github/", "docs/", "graphify-out/", "node_modules/",
            ".gitignore", "databasedumps/", ".fleet/", "scratch/",
            "__pycache__/", ".pyc",
            # Added 2026-09-02. This list was a reduced copy matching
            # intypiano's own deploy.yml, so it inherited NONE of the
            # protections added to DEFAULT_EXCLUDES after the August
            # exposures. The first allowlist audit found all of the below
            # deployable on this site. See docs/40-Operations/deploy-policy.md
            # section 2.3.
            #
            # backups/ -- 61 files: backup_*.sql database dumps plus
            # FlashDrive/{clients.tab,pianos.csv,schedule.csv,Pianos.fmp12}.
            # Client and inventory data. Same class as the 7.4 MB user dump
            # found publicly downloadable on 2026-08-29; DEFAULT_EXCLUDES
            # covers "databasebackups/" but this site names it "backups/".
            "backups/",
            # .py / .sh -- 11 and 14 files (export_dbs.sh,
            # scripts/bootstrap_*_db.sh, install_tcpdf.sh, import_central_
            # data.py). Shared hosting runs PHP; these cannot execute and are
            # served as PLAINTEXT. Database and provisioning scripts are
            # precisely where credentials sit -- the 2026-08-30 finding was a
            # .py carrying a live FTP host, user and password.
            #
            # These are EXTENSION patterns, not substrings: see
            # _is_extension_pattern(). As a substring ".sh" also matched
            # tinymce/.../skin.shadowdom.js and .min.css, which would have
            # silently broken the CRM's rich-text editor.
            ".py", ".sh",
            # Agent and editor tooling. Not site content, and useful
            # reconnaissance -- .mcp.json on a sibling site was publicly
            # downloadable WITH a live CHORD_TOKEN in it on 2026-08-29.
            # DEFAULT_EXCLUDES covers .claude/; the other two are this site's
            # local equivalents.
            ".claude/", ".playwright-cli/", ".superpowers/", ".cursorrules",
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
        "patterns": DEFAULT_EXCLUDES,
        "exclude_all_md": True,
        "extra_exact": [],
        "md_allow_prefixes": ["journalgpt/corpus/articles/"],
    },
}


def get_repo_excludes(repo_name):
    cfg = REPO_EXCLUDES.get(repo_name)
    if not cfg:
        return DEFAULT_EXCLUDES, DEFAULT_EXCLUDE_ALL_MD, [], []
    return (
        cfg["patterns"], cfg["exclude_all_md"], cfg.get("extra_exact", []),
        cfg.get("md_allow_prefixes", []),
    )


def _is_extension_pattern(ex):
    """A pattern like '.sh' or '.mcp.json' names a FILE ENDING, not a substring.

    Found 2026-09-02 while adding '.sh' to intypiano: as a substring it also
    matched crm/public/includes/tinymce/.../skin.shadowdom.js and its .min.css
    -- 8 TinyMCE editor assets that would have silently stopped deploying,
    breaking the CRM's rich-text editor. That is the SECOND failure direction
    from the policy (silent withholding), and it is the same shape as the
    1,533-file corpus drop on 2026-08-27.

    Directory patterns ('.claude/', 'backups/') keep substring behaviour --
    they must match at any depth. Bare-word patterns ('dbbackup') likewise.
    Verified on all three repos at the time of the change: this reclassifies
    nothing that was being blocked, so it is a no-op on today's trees and a
    guard against the next '.shtml'.
    """
    return ex.startswith(".") and "/" not in ex


def should_exclude(filepath, patterns, exclude_all_md, extra_exact, md_allow_prefixes=()):
    if filepath in extra_exact:
        return True
    if exclude_all_md and filepath.endswith(".md"):
        if not any(filepath.startswith(p) for p in md_allow_prefixes):
            return True
    lowered = filepath.lower()
    for ex in patterns:
        if _is_extension_pattern(ex):
            if lowered.endswith(ex.lower()):
                return True
        elif ex in filepath or filepath.startswith(ex):
            return True
    return False


# What v3 sync.py gated on before this module existed (v3 deploy.py's
# TEST_SUITE_CANDIDATES). The default when a caller passes no list.
SYNC_TEST_SUITE_CANDIDATES = ["journalgpt/tests/security_and_eval_suite.php"]


def run_test_gate(repo_dir, lock=None, candidates=None):
    """Run the repo's gate suite. Returns (passed, output, suite|None); a repo
    with no suite from `candidates` returns (True, '', None), ungated.

    lock: the held gate lock (gate_lock.GateLock or InheritedGateLock). Its fd
    is passed into the gate child (sh forwards it to php), so if the caller is
    SIGKILLed mid-gate the orphaned suite keeps the machine-wide lock until it
    exits and no second gate can start on the shared DB journal_ai_test on top
    of it. Background workers the suite spawns inherit it too and can hold the
    lock until they exit: a delay, never an overlap."""
    suite = gate_lock.find_test_suite(
        repo_dir, SYNC_TEST_SUITE_CANDIDATES if candidates is None else candidates)
    if not suite:
        return True, "", None
    cmd = f"php {suite}" if suite.endswith(".php") else f"python3 {suite}"
    fd = lock.fileno() if lock is not None else None
    pass_fds = (fd,) if fd is not None else ()
    result = subprocess.run(cmd, shell=True, cwd=repo_dir, capture_output=True, text=True,
                            pass_fds=pass_fds)
    return result.returncode == 0, result.stdout + result.stderr, suite
