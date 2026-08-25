#!/usr/bin/env python3
"""
Run pending DB migrations on newmexicoptg.org's test environment via
journalgpt/admin_migrate.php -- no shell/SSH access needed.

deploy.py only FTPs files; it never touches the database (test shares prod's
DB, so this deliberately isn't automatic). Any deploy that includes a new
migrations/*.sql file needs this run afterward, by a human or by this script.

Usage:
    run_test_migration.py                # apply any pending migrations
    run_test_migration.py --status-only  # just report what's pending, no run

Credentials come from task_coordinator/.env: TEST_MEMBER_EMAIL, TEST_MEMBER_PASSWORD
(any authenticated member account works -- admin_migrate.php has no separate
admin role, see its own docblock).
"""
import os
import re
import sys
import html
import http.cookiejar
import urllib.request
import urllib.parse
from pathlib import Path

BASE_URL = "https://test.newmexicoptg.org/journalgpt"


def load_env():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()


def extract_csrf(page_html):
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', page_html)
    if not m:
        raise RuntimeError("Could not find csrf_token in response -- login likely failed")
    return m.group(1)


def main():
    load_env()
    email = os.environ.get("TEST_MEMBER_EMAIL")
    password = os.environ.get("TEST_MEMBER_PASSWORD")
    if not email or not password:
        print("Missing TEST_MEMBER_EMAIL/TEST_MEMBER_PASSWORD in task_coordinator/.env")
        sys.exit(1)

    status_only = "--status-only" in sys.argv

    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    login_page = opener.open(f"{BASE_URL}/login.php").read().decode()
    csrf = extract_csrf(login_page)
    login_data = urllib.parse.urlencode({
        "email": email, "password": password, "csrf_token": csrf
    }).encode()
    opener.open(f"{BASE_URL}/login.php", data=login_data)

    migrate_page = opener.open(f"{BASE_URL}/admin_migrate.php").read().decode()
    if "Logged in as:" not in migrate_page:
        print("Login did not reach admin_migrate.php as an authenticated session -- check credentials.")
        sys.exit(1)

    rows = re.findall(
        r'<tr>\s*<td><code>([^<]+)</code></td>\s*<td[^>]*>\s*<span class="badge (badge-applied|badge-pending)">',
        migrate_page,
    )
    pending = [name for name, cls in rows if cls == "badge-pending"]
    print(f"Pending migrations: {pending if pending else 'none'}")

    if status_only or not pending:
        sys.exit(0)

    csrf = extract_csrf(migrate_page)
    run_data = urllib.parse.urlencode({"csrf_token": csrf}).encode()
    result_page = opener.open(f"{BASE_URL}/admin_migrate.php", data=run_data).read().decode()

    log_match = re.search(r'<div class="log-box">(.*?)</div>', result_page, re.S)
    if log_match:
        print(html.unescape(log_match.group(1)).strip())

    if "alert-success" in result_page:
        print("Migration run complete.")
        sys.exit(0)
    else:
        print("Migration run reported an error -- see log above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
