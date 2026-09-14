#!/usr/bin/env python3
"""
Run pending DB migrations on newmexicoptg.org's test environment via
api/operations.php's token-gated 'migrate' job -- no shell/SSH access
needed. Same createJob/confirmJob flow deploy.py's own
trigger_remote_migration() uses, and the same one embed_prod_missing.py
uses for its own job type.

deploy.py only FTPs files; it never touches the database (test shares prod's
DB, so this deliberately isn't automatic). Any deploy that includes a new
migrations/*.sql file needs this run afterward, by a human or by this script.

Usage:
    run_test_migration.py [test|prod]     # apply any pending migrations (default: test)
    run_test_migration.py --status-only   # just report what's pending, no run

Reads JOURNALGPT_OPERATIONS_TOKEN and JOURNALGPT_OPERATIONS_URL_<ENV> from
task_coordinator/.env -- same two variables deploy.py's trigger_remote_migration()
and embed_prod_missing.py already read.

T-PTG-677 (2026-09-13): this used to log in as a member-role account and POST
admin_migrate.php's own form -- that page is now gated
Authorization::requireRole(ROLE_ADMIN), so a member-role login 403s on it as
of that change. The ops-token job flow was already this repo's own
established alternative (deploy.py has never used the browser-login path),
so this script now matches it instead of needing its own promoted account.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def load_env():
    cfg = {}
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    return cfg


def call(base, token, path, body=None, timeout=60):
    req = urllib.request.Request(
        base + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST" if body is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def main():
    cfg = load_env()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    env = args[0] if args else "test"
    if env not in ("test", "prod"):
        print(f"Unknown environment '{env}' -- expected test or prod")
        sys.exit(1)
    status_only = "--status-only" in sys.argv

    token = cfg.get("JOURNALGPT_OPERATIONS_TOKEN")
    base = cfg.get(f"JOURNALGPT_OPERATIONS_URL_{env.upper()}")
    if not token or not base:
        print(f"Missing JOURNALGPT_OPERATIONS_TOKEN/JOURNALGPT_OPERATIONS_URL_{env.upper()} in task_coordinator/.env")
        sys.exit(1)
    base = base.rstrip("/")

    try:
        created = call(base, token, "/create", {"type": "migrate", "arguments": {"dry_run": True}})
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"Status check failed: {type(e).__name__}: {e}")
        sys.exit(1)
    job = created["job"]
    confirmed = call(base, token, f"/confirm/{job['id']}", {"confirmation_secret": created["confirmation_secret"]})
    status = confirmed["job"].get("result", {}).get("status", [])
    pending = [row["migration"] for row in status if not row.get("applied")]
    print(f"Pending migrations ({env}): {pending if pending else 'none'}")

    if status_only or not pending:
        sys.exit(0)

    created = call(base, token, "/create", {"type": "migrate", "arguments": {}})
    job = created["job"]
    try:
        confirmed = call(base, token, f"/confirm/{job['id']}", {"confirmation_secret": created["confirmation_secret"]}, timeout=300)
    except (urllib.error.URLError, urllib.error.HTTPError):
        print("Confirm request timed out or errored client-side; polling job status instead.")
        confirmed = None

    if confirmed is None:
        while True:
            time.sleep(5)
            confirmed = {"job": call(base, token, f"/status/{job['id']}")["job"]}
            if confirmed["job"].get("state") in ("succeeded", "failed"):
                break

    result = confirmed["job"].get("result", {})
    for line in result.get("log", []):
        print(line)

    if confirmed["job"].get("state") == "succeeded":
        print(f"Migration run complete. Applied {result.get('applied')} migration(s).")
        sys.exit(0)
    else:
        print(f"Migration run reported an error -- state={confirmed['job'].get('state')}, "
              f"error={confirmed['job'].get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
