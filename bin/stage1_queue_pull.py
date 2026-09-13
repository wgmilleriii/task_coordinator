#!/usr/bin/env python3
"""T-PTG-663 part B: pull human review output (PASS/FAIL verdicts and stage-1 edit
proposals) from prod and test into the repository, hourly, from a private worktree,
and apply APPROVED edits as git commits on test (part C) instead of on the server.
Nothing here reads or writes the shared checkout.

  python3 stage1_queue_pull.py            # one run (launchd calls this)
  python3 stage1_queue_pull.py --dry-run  # pull and diff, no commit/push/apply

State ~/.config/journalgpt/stage1_queue_state.json: per env {verdict_since_id,
batch_since_id, proposal_since_id, verdict_hashes (legacy dedupe until since_id
exists on the server)}. Token ~/.config/journalgpt/ops.token. Worktree
~/.cache/newmexicoptg-queue-wt on origin/test.

Repo output (append-only JSONL, one object per line):
  journalgpt/corpus/qc_staging/human_review/<env>/verdicts.jsonl
  journalgpt/corpus/qc_staging/human_review/<env>/proposals.jsonl   (batches and
  proposals interleaved, each with "kind": "batch" | "proposal")

Apply step (only when journalgpt/cli/stage1_apply_batch.php exists in the worktree):
for every batch that has approved, unapplied proposals and no applied_commit_sha,
run the cli against the worktree, commit by path, push, then POST
mark_applied_external {batch_id, commit_sha}. Stale batches (exit 2) are logged and
left for the reviewer. Cursors and hashes advance only after a successful push.
"""
import hashlib, json, os, subprocess, sys, time, urllib.request, urllib.error, pathlib

HOME = pathlib.Path.home()
TOKEN_FILE = HOME / ".config/journalgpt/ops.token"
STATE_FILE = HOME / ".config/journalgpt/stage1_queue_state.json"
WT = HOME / ".cache/newmexicoptg-queue-wt"
REPO_URL = "https://github.com/wgmilleriii/newmexicoptg.org.git"
REPO_LOCAL = HOME / "Documents/GitHub/newmexicoptg.org"  # clone source for objects only; its tree is never read
SITES = {"prod": "https://newmexicoptg.org", "test": "https://test.newmexicoptg.org"}
OUT_PREFIX = "journalgpt/corpus/qc_staging/human_review"
APPLY_CLI = "journalgpt/cli/stage1_apply_batch.php"
DRY = "--dry-run" in sys.argv
PHP = "/opt/homebrew/bin/php"


def log(msg):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} {msg}", flush=True)


def api(url, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET",
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def run(cmd, cwd=None, check=True):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"{' '.join(map(str, cmd))}: {p.stderr.strip()[:300]}")
    return p


def ensure_worktree():
    if not (WT / ".git").exists():
        WT.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "-q", "--branch", "test", "--single-branch", str(REPO_LOCAL), str(WT)])
        run(["git", "remote", "set-url", "origin", REPO_URL], cwd=WT)
    run(["git", "fetch", "-q", "origin", "test"], cwd=WT)
    run(["git", "reset", "-q", "--hard", "origin/test"], cwd=WT)
    run(["git", "clean", "-qfd", OUT_PREFIX], cwd=WT)


def rec_hash(rec):
    return hashlib.sha1(json.dumps(rec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def append_jsonl(rel, recs):
    path = WT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        for r in recs:
            f.write(json.dumps(r, sort_keys=True) + "\n")


def commit_and_push(rel_paths, msg):
    """Returns the pushed commit sha, or None if the push was rejected."""
    run(["git", "add", "--", *rel_paths], cwd=WT)
    if not run(["git", "diff", "--cached", "--quiet"], cwd=WT, check=False).returncode:
        return "nochange"
    run(["git", "commit", "-q", "-m", msg], cwd=WT)
    p = subprocess.run(["git", "push", "-q", "origin", "HEAD:refs/heads/test"], cwd=WT, capture_output=True, text=True)
    if p.returncode != 0:
        log(f"push rejected, will retry next run: {p.stderr.strip()[:200]}")
        run(["git", "reset", "-q", "--hard", "origin/test"], cwd=WT)
        return None
    return run(["git", "rev-parse", "HEAD"], cwd=WT).stdout.strip()


def pull_verdicts(env, site, token, st):
    """Prefer the raw since_id stream; fall back to the latest-per-csv export with hash dedupe."""
    since = st.get("verdict_since_id")
    if since is not None:
        body = api(f"{site}/journalgpt/api/stage1_review_verdicts_export.php?since_id={since}", token)
        rows = body.get("verdicts", [])
        if rows and "id" in rows[0]:
            recs = [{"env": env, **r} for r in rows]
            return recs, {"verdict_since_id": max(r["id"] for r in rows)}
    body = api(f"{site}/journalgpt/api/stage1_review_verdicts_export.php?since_id=0", token)
    rows = body.get("verdicts", [])
    if rows and "id" in rows[0]:  # server supports since_id: adopt it, dedupe nothing (fresh stream)
        seen = set(st.get("verdict_hashes", []))
        recs = [{"env": env, **r} for r in rows]
        return recs, {"verdict_since_id": max(r["id"] for r in rows)}
    seen = set(st.get("verdict_hashes", []))
    fresh = []
    for r in rows:
        rec = {"env": env, **r}
        h = rec_hash(rec)
        if h not in seen:
            fresh.append(rec)
            seen.add(h)
    return fresh, {"verdict_hashes": sorted(seen)}


def pull_proposals(env, site, token, st):
    b, p = st.get("batch_since_id", 0), st.get("proposal_since_id", 0)
    try:
        body = api(f"{site}/journalgpt/api/stage1_edit_proposals_export.php?since_batch_id={b}&since_proposal_id={p}", token)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return [], {}, None
        raise
    batches = body.get("batches", []); props = body.get("proposals", [])
    recs = [{"env": env, "kind": "batch", **r} for r in batches] + [{"env": env, "kind": "proposal", **r} for r in props]
    adv = {}
    if batches: adv["batch_since_id"] = max(r["id"] for r in batches)
    if props: adv["proposal_since_id"] = max(r["id"] for r in props)
    return recs, adv, body


def apply_batches(env, site, token, body):
    """Part C: apply approved, unapplied batches to the worktree and report back."""
    if body is None or not (WT / APPLY_CLI).exists() or DRY:
        return
    props_by_batch = {}
    for pr in body.get("proposals", []):
        props_by_batch.setdefault(pr["batch_id"], []).append(pr)
    for batch in body.get("batches", []):
        if batch.get("applied_commit_sha"):
            continue
        approved = [pr for pr in props_by_batch.get(batch["id"], []) if pr.get("status") == "approved"]
        if not approved:
            continue
        payload = {"batch": batch, "proposals": approved}
        tmp = WT / f".stage1_batch_{env}_{batch['id']}.json"
        tmp.write_text(json.dumps(payload))
        try:
            p = subprocess.run([PHP, APPLY_CLI, str(WT), str(tmp)], cwd=WT, capture_output=True, text=True)
        finally:
            tmp.unlink(missing_ok=True)
        if p.returncode == 2:
            log(f"{env}: batch {batch['id']} STALE (file changed since proposed); left for the reviewer")
            run(["git", "checkout", "-q", "--", "."], cwd=WT); continue
        if p.returncode != 0:
            log(f"{env}: batch {batch['id']} apply error: {p.stderr.strip()[:200]}")
            run(["git", "checkout", "-q", "--", "."], cwd=WT); continue
        try:
            result = json.loads(p.stdout)
        except Exception:
            result = {"path": None}
        path = result.get("path")
        if not path:
            log(f"{env}: batch {batch['id']} applied nothing"); continue
        who = batch.get("reviewer_name") or batch.get("submitted_by") or "reviewer"
        msg = (f"stage1-edit: batch #{batch['id']} ({env}) csv {batch.get('csv_number')} applied via repository\n\n"
               f"Reviewer: {who}\nComment: {batch.get('comment', '')}\nApplied {result.get('applied')} approved proposal(s) by stage1_queue_pull.py (T-PTG-663).")
        sha = commit_and_push([path], msg)
        if not sha or sha == "nochange":
            continue
        try:
            api(f"{site}/journalgpt/api/stage1_edit_mark_applied_external.php", token, {"batch_id": batch["id"], "commit_sha": sha})
            log(f"{env}: batch {batch['id']} applied at {sha[:9]} and marked on the server")
        except Exception as e:
            log(f"{env}: batch {batch['id']} applied at {sha[:9]} but mark_applied_external failed: {type(e).__name__}; retried next run (idempotent)")


def main():
    token = TOKEN_FILE.read_text().strip()
    state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    ensure_worktree()
    touched, pending_adv, bodies = [], {}, {}
    for env, site in SITES.items():
        st = state.setdefault(env, {})
        try:
            vrecs, vadv = pull_verdicts(env, site, token, st)
        except Exception as e:
            log(f"{env}: verdicts pull failed: {type(e).__name__}: {str(e)[:120]}"); vrecs, vadv = [], {}
        try:
            precs, padv, body = pull_proposals(env, site, token, st)
        except Exception as e:
            log(f"{env}: proposals pull failed: {type(e).__name__}: {str(e)[:120]}"); precs, padv, body = [], {}, None
        bodies[env] = body
        log(f"{env}: {len(vrecs)} new verdict(s), {len(precs)} new proposal record(s)")
        if vrecs:
            append_jsonl(f"{OUT_PREFIX}/{env}/verdicts.jsonl", vrecs); touched.append(f"{OUT_PREFIX}/{env}/verdicts.jsonl")
        if precs:
            append_jsonl(f"{OUT_PREFIX}/{env}/proposals.jsonl", precs); touched.append(f"{OUT_PREFIX}/{env}/proposals.jsonl")
        pending_adv[env] = {**vadv, **padv}
    if touched:
        if DRY:
            log("dry-run: " + run(["git", "status", "--short", "--", OUT_PREFIX], cwd=WT).stdout.strip())
        else:
            sha = commit_and_push(sorted(set(touched)), "human-review: pull verdicts/proposals\n\nPulled by stage1_queue_pull.py (T-PTG-663) from the site exports; append-only JSONL.")
            if sha and sha != "nochange":
                for env, adv in pending_adv.items():
                    state[env].update(adv); state[env]["last_push"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
                STATE_FILE.write_text(json.dumps(state, indent=1))
                log(f"pushed {sha[:9]}")
            elif sha is None:
                return 1
    else:
        log("nothing new")
    for env, site in SITES.items():
        try:
            apply_batches(env, site, token, bodies.get(env))
        except Exception as e:
            log(f"{env}: apply step failed: {type(e).__name__}: {str(e)[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
