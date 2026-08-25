#!/usr/bin/env python3
import os
import sys
import json
import ftplib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Exclusion patterns
EXCLUDES = [
    ".git/", ".github/", "docs/", "tasks/", "node_modules/", ".gitignore"
]

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
TEST_SUITE_CANDIDATES = ["journalgpt/tests/security_and_eval_suite.php"]


def run_test_gate(repo_dir):
    """Run this repo's test suite before anything goes out over FTP. Returns
    (passed: bool, output: str, suite: str|None). A repo with no recognized
    suite returns (True, '', None) -- deploy proceeds ungated, same as before
    this existed, rather than blocking on a convention it doesn't have."""
    suite = None
    for candidate in TEST_SUITE_CANDIDATES:
        if (Path(repo_dir) / candidate).exists():
            suite = candidate
            break
    if not suite:
        return True, "", None

    cmd = f"php {suite}" if suite.endswith(".php") else f"python3 {suite}"
    result = subprocess.run(cmd, shell=True, cwd=repo_dir, capture_output=True, text=True)
    return result.returncode == 0, result.stdout + result.stderr, suite


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

def should_exclude(filepath):
    if filepath.endswith(".md"):
        return True
    for ex in EXCLUDES:
        if ex in filepath or filepath.startswith(ex):
            return True
    return False

def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def main():
    if len(sys.argv) < 3:
        print("Usage: deploy.py <repo_dir> <environment (test|prod)> [--seed <sha>]")
        sys.exit(1)

    repo_dir = os.path.abspath(sys.argv[1])
    repo_name = os.path.basename(repo_dir)
    env = sys.argv[2]
    
    if env not in ["test", "prod"]:
        print("Environment must be test or prod")
        sys.exit(1)
        
    seed_sha = None
    if len(sys.argv) == 5 and sys.argv[3] == "--seed":
        seed_sha = sys.argv[4]

    load_env()
    
    host_var = f"FTP_HOST_{env.upper()}"
    user_var = f"FTP_USER_{env.upper()}"
    pass_var = f"FTP_PASS_{env.upper()}"
    dir_var = f"FTP_DIR_{env.upper()}"

    host = os.environ.get(host_var)
    user = os.environ.get(user_var)
    passwd = os.environ.get(pass_var)
    ftp_dir = os.environ.get(dir_var, "/")

    if not all([host, user, passwd]):
        print(f"Missing FTP credentials for {env}. Check .env file.")
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
    
    if last_sha == current_sha:
        print("Everything is up to date!")
        sys.exit(0)

    print(f"Deploying changes from {last_sha} to {current_sha}...")
    diff_output = run_cmd(f"git diff --name-status {last_sha} {current_sha}", cwd=repo_dir)
    
    files_to_upload = []
    files_to_delete = []

    for line in diff_output.split("\n"):
        if not line: continue
        parts = line.split("\t")
        status = parts[0]
        filepath = parts[-1]
        
        if should_exclude(filepath):
            continue
            
        if status.startswith("D"):
            files_to_delete.append(filepath)
        else:
            files_to_upload.append(filepath)

    if not files_to_upload and not files_to_delete:
        print("No deployable files changed. Updating state.")
        state[repo_name][env] = current_sha
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
        sys.exit(0)

    print("Running test gate before deploy...")
    tests_passed, test_output, suite = run_test_gate(repo_dir)
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

    print("Connecting to FTP...")
    ftp = ftplib.FTP(host)
    ftp.login(user, passwd)
    ftp.cwd(ftp_dir)

    for fpath in files_to_delete:
        print(f"Deleting {fpath}...")
        try:
            ftp.delete(fpath)
        except Exception as e:
            print(f"Could not delete {fpath}: {e}")

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

    ftp.quit()
    
    state[repo_name][env] = current_sha
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)
        
    print(f"Deployed successfully to {env}!")

if __name__ == "__main__":
    main()
