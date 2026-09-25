#!/usr/bin/env python3
"""Fixture tests for deploy.py's three guards: ancestry, no-queuing, --list-only.

NOTHING HERE DEPLOYS ANYTHING.
  * The repo under test is a throwaway git repo with a `git init --bare` remote
    in a tempdir. No real repo, branch or remote is touched.
  * deploy.py is exercised through an "engine dir" whose bin/ SYMLINKS the real
    bin/deploy.py, bin/gate_lock.py and bin/deploy_common.py. deploy.py derives
    its deploy_state.json from dirname(__file__)/.., so the state file under
    test is a temp file and the checkout's deploy_state.json is never read or
    written.
  * Every child process runs with a sitecustomize.py on PYTHONPATH that makes
    socket.socket and socket.create_connection raise. An FTP connection is
    therefore impossible, not merely unreached -- and
    test_socket_blocker_actually_blocks proves the blocker discriminates, so a
    green run is not green because the probe cannot fail.
  * The gate lock always lives at a tempdir path via $NEWMEXICOPTG_GATE_LOCK.
    ~/.cache/newmexicoptg-gate.lock is never opened, read or deleted.

Each guard is proved in BOTH states (allowed and refused), in-process where a
function can be called directly, and end-to-end through a real subprocess run
of deploy.py at least once per guard.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))
import deploy      # noqa: E402
import gate_lock   # noqa: E402

# Makes any socket in a child process an assertion failure. Imported
# automatically by CPython at startup when it is on PYTHONPATH.
#
# socket.socket is SUBCLASSED rather than replaced with a function: ssl.py does
# `class SSLSocket(socket)` at import time, and a plain function there makes
# `import ftplib` itself explode with a TypeError -- which would "pass" these
# tests for entirely the wrong reason.
SITECUSTOMIZE = """
import socket

_MSG = "TEST GUARD: a socket connection was attempted. deploy guard tests must never connect."


class _NoConnect(socket.socket):
    def connect(self, *a, **k):
        raise AssertionError(_MSG)

    def connect_ex(self, *a, **k):
        raise AssertionError(_MSG)


def _blocked(*a, **k):
    raise AssertionError(_MSG)


socket.socket = _NoConnect
socket.create_connection = _blocked
"""


def git(cwd, *args, check=True):
    return subprocess.run(["git"] + list(args), cwd=str(cwd), check=check,
                          capture_output=True, text=True)


def commit(repo, message, writes=(), deletes=()):
    for rel, text in writes:
        p = Path(repo) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        git(repo, "add", rel)
    for rel in deletes:
        git(repo, "rm", "-q", rel)
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD").stdout.strip()


class Fixture:
    """Throwaway repo + bare remote + engine dir. Built once per test class.

    History (branch `test`, pushed to the bare remote):
      c0  journalgpt/index.php, journalgpt/old.php, journalgpt/tests/run_suite.php
      c1  docs/notes.md only            -> nothing DEPLOYABLE changes c0..c1
      c2  journalgpt/a.php added, bin/tool.py added (excluded)
      c3  journalgpt/index.php modified, journalgpt/old.php deleted
      c4  docs/more.md only           -> nothing DEPLOYABLE changes c3..c4
    origin/test == c4. HEAD at c4 contains it; HEAD at c1 is 3 commits short.

    The repo directory is named `newmexicoptg.org` so the REAL TRACKING_REFS and
    REAL exclusion rules apply -- a fixture with a made-up repo name would test
    a configuration nobody deploys.
    """

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.remote = root / "newmexicoptg.org.git"
        self.repo = root / "work" / "newmexicoptg.org"
        self.engine = root / "engine"
        self.pythonpath = root / "pypath"

        git(root, "init", "-q", "--bare", "-b", "test", str(self.remote))
        self.repo.parent.mkdir(parents=True)
        git(root, "init", "-q", "-b", "test", str(self.repo))
        git(self.repo, "config", "user.email", "guardtest@example.invalid")
        git(self.repo, "config", "user.name", "guard test")
        git(self.repo, "remote", "add", "origin", str(self.remote))

        self.c0 = commit(self.repo, "c0", writes=[
            ("journalgpt/index.php", "<?php // v0\n"),
            ("journalgpt/old.php", "<?php // doomed\n"),
            ("journalgpt/tests/run_suite.php", "<?php exit(0);\n"),
        ])
        self.c1 = commit(self.repo, "c1 docs only",
                         writes=[("docs/notes.md", "notes\n")])
        self.c2 = commit(self.repo, "c2 add a.php", writes=[
            ("journalgpt/a.php", "<?php // a\n"),
            ("bin/tool.py", "# excluded\n"),
        ])
        self.c3 = commit(self.repo, "c3 modify + delete",
                         writes=[("journalgpt/index.php", "<?php // v1\n")],
                         deletes=["journalgpt/old.php"])
        self.c4 = commit(self.repo, "c4 docs only",
                         writes=[("docs/more.md", "more\n")])
        git(self.repo, "push", "-q", "origin", "test")

        (self.engine / "bin").mkdir(parents=True)
        for name in ("deploy.py", "gate_lock.py", "deploy_common.py"):
            os.symlink(BIN / name, self.engine / "bin" / name)
        self.state_file = self.engine / "deploy_state.json"

        self.pythonpath.mkdir()
        (self.pythonpath / "sitecustomize.py").write_text(SITECUSTOMIZE)

    def checkout(self, sha):
        git(self.repo, "checkout", "-q", "--detach", sha)

    def write_state(self, last_sha, env="test"):
        self.state_file.write_text(json.dumps({"newmexicoptg.org": {env: last_sha}}))

    def read_state(self):
        return json.loads(self.state_file.read_text())

    def cleanup(self):
        self.tmp.cleanup()


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fx = Fixture()

    @classmethod
    def tearDownClass(cls):
        cls.fx.cleanup()

    def setUp(self):
        self.lockdir = tempfile.TemporaryDirectory()
        self.lock = str(Path(self.lockdir.name) / "gate.lock")
        self.fx.checkout(self.fx.c4)
        self.fx.write_state(self.fx.c0)
        self._saved_held = os.environ.pop(gate_lock.HELD_ENV, None)

    def tearDown(self):
        os.environ.pop(gate_lock.HELD_ENV, None)
        if self._saved_held is not None:
            os.environ[gate_lock.HELD_ENV] = self._saved_held
        self.lockdir.cleanup()

    # --- helpers ---------------------------------------------------------
    def child_env(self, **extra):
        env = dict(os.environ)
        env.pop(gate_lock.HELD_ENV, None)
        env["NEWMEXICOPTG_GATE_LOCK"] = self.lock
        env["PYTHONPATH"] = str(self.fx.pythonpath) + os.pathsep + env.get("PYTHONPATH", "")
        # Dummy credentials: present so the run does not stop for lack of them,
        # unusable because the socket blocker makes any connection an error.
        env["FTP_HOST_TEST"] = "ftp.invalid"
        env["FTP_USER_TEST"] = "nobody"
        env["FTP_PASS_TEST"] = "nothing"
        env.update(extra)
        return env

    def run_deploy(self, *args, env=None, timeout=120):
        return subprocess.run(
            [sys.executable, str(self.fx.engine / "bin" / "deploy.py"),
             str(self.fx.repo), "test"] + list(args),
            capture_output=True, text=True, env=env or self.child_env(), timeout=timeout)

    def hold_lock(self, tool):
        """Start a separate process holding the gate lock with this tool= value.
        Returns the Popen; the caller stops it in the test's cleanup."""
        ready = Path(self.lockdir.name) / f"ready-{tool.replace('/', '_')}"
        code = (
            "import sys, time\n"
            f"sys.path.insert(0, {str(BIN)!r})\n"
            "import gate_lock\n"
            f"l = gate_lock.GateLock('test', '/fixture', {tool!r}, path={self.lock!r}).acquire()\n"
            f"open({str(ready)!r}, 'w').write('1')\n"
            "time.sleep(120)\n"
        )
        p = subprocess.Popen([sys.executable, "-c", code],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        def stop():
            p.kill()
            p.wait(timeout=10)  # reap it, or the lock outlives the test

        self.addCleanup(stop)
        for _ in range(200):
            if ready.exists():
                return p
            time.sleep(0.05)
        self.fail("holder process never acquired the fixture gate lock")

    def capture(self, fn, *a, **kw):
        """Run fn, returning (result_or_SystemExit_code, printed_text)."""
        import io
        buf = io.StringIO()
        try:
            return fn(*a, out=buf, **kw), buf.getvalue()
        except SystemExit as e:
            return e, buf.getvalue()


class SocketBlockerTest(Base):
    def test_socket_blocker_actually_blocks(self):
        """The discriminator for every 'never connected' claim below: prove the
        blocker can fail a child that DOES connect."""
        r = subprocess.run(
            [sys.executable, "-c",
             "import socket; socket.create_connection(('127.0.0.1', 9))"],
            capture_output=True, text=True, env=self.child_env())
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("TEST GUARD: a socket connection was attempted", r.stderr)


class TrackingRefTests(Base):
    def test_worktree_named_for_a_task_still_resolves_via_origin(self):
        """Deploys run from worktrees named for the task (train-45,
        leipzig-783). The basename has no mapping; origin's URL does."""
        import io
        buf = io.StringIO()
        self.assertEqual(
            deploy.resolve_repo_identity(self.fx.repo, "leipzig-783", buf),
            "newmexicoptg.org")
        self.assertIn("origin's URL says this is 'newmexicoptg.org'", buf.getvalue())
        # A name that IS mapped is used as-is, with nothing printed.
        buf = io.StringIO()
        self.assertEqual(
            deploy.resolve_repo_identity(self.fx.repo, "newmexicoptg.org", buf),
            "newmexicoptg.org")
        self.assertEqual(buf.getvalue(), "")

    def test_unknown_repo_with_no_matching_origin_stays_unknown(self):
        import io
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        git(tmp.name, "init", "-q", "unrelated")
        buf = io.StringIO()
        self.assertEqual(
            deploy.resolve_repo_identity(Path(tmp.name) / "unrelated", "unrelated", buf),
            "unrelated")
        self.assertEqual(buf.getvalue(), "")

    def test_mapping_is_the_one_we_claim(self):
        self.assertEqual(deploy.get_tracking_ref("newmexicoptg.org", "test"),
                         ("origin", "test", "origin/test"))
        self.assertEqual(deploy.get_tracking_ref("newmexicoptg.org", "prod"),
                         ("origin", "main", "origin/main"))
        self.assertEqual(deploy.get_tracking_ref("resources_was_pmtnm", "prod"),
                         ("origin", "main", "origin/main"))
        self.assertEqual(deploy.get_tracking_ref("intypiano", "prod"),
                         ("origin", "master", "origin/master"))
        # Claimed nowhere, so checked nowhere.
        self.assertIsNone(deploy.get_tracking_ref("intypiano", "test"))
        self.assertIsNone(deploy.get_tracking_ref("some-other-repo", "prod"))


class AncestryGuardTests(Base):
    def test_ancestry_status_both_states(self):
        self.assertEqual(deploy.ancestry_status(self.fx.repo, "origin/test"),
                         (True, True, 0))
        self.fx.checkout(self.fx.c1)
        self.assertEqual(deploy.ancestry_status(self.fx.repo, "origin/test"),
                         (True, False, 3))

    def test_unresolvable_ref_is_not_a_pass(self):
        resolved, ok, missing = deploy.ancestry_status(self.fx.repo, "origin/no-such-branch")
        self.assertEqual((resolved, ok, missing), (False, False, None))

    def test_ancestor_proceeds(self):
        out, text = self.capture(deploy.check_ancestry, self.fx.repo,
                                 "newmexicoptg.org", "test")
        self.assertEqual(out, ("origin/test", "verified"))
        self.assertIn("ancestry OK", text)

    def test_non_ancestor_is_refused_with_the_message(self):
        self.fx.checkout(self.fx.c1)
        out, text = self.capture(deploy.check_ancestry, self.fx.repo,
                                 "newmexicoptg.org", "test")
        self.assertIsInstance(out, SystemExit)
        self.assertEqual(out.code, deploy.ANCESTRY_EXIT_CODE)
        self.assertIn("REFUSING TO DEPLOY newmexicoptg.org to test", text)
        self.assertIn("origin/test", text)
        self.assertIn("3 commit(s)", text)

    def test_unresolvable_ref_refuses(self):
        """Unknown is not permission: a ref that does not resolve refuses."""
        out, text = self.capture(deploy.check_ancestry, self.fx.repo,
                                 "newmexicoptg.org", "prod")  # origin/main does not exist here
        self.assertIsInstance(out, SystemExit)
        self.assertEqual(out.code, deploy.ANCESTRY_EXIT_CODE)
        self.assertIn("does not resolve", text)
        self.assertIn("An unknown is not a pass", text)

    def test_override_proceeds_and_carries_the_reason(self):
        self.fx.checkout(self.fx.c1)
        out, text = self.capture(deploy.check_ancestry, self.fx.repo,
                                 "newmexicoptg.org", "test",
                                 allow_reason="tip merged by hand, verified by eye")
        self.assertEqual(out, ("origin/test", "overridden: tip merged by hand, verified by eye"))
        self.assertIn("--allow-non-ancestor", text)
        self.assertIn("tip merged by hand", text)

    def test_unmapped_repo_says_so_and_continues(self):
        # A repo with no mapping AND no origin that resolves to one. (Against
        # the fixture repo this would now resolve through origin's URL, which
        # is the worktree case tested in TrackingRefTests.)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        git(tmp.name, "init", "-q", "some-other-repo")
        other = Path(tmp.name) / "some-other-repo"
        out, text = self.capture(deploy.check_ancestry, other,
                                 "some-other-repo", "test")
        self.assertEqual(out, (None, "not_configured"))
        self.assertIn("no tracking ref configured for some-other-repo/test", text)
        self.assertIn("ancestry not checked", text)

    def test_failed_fetch_is_announced_not_swallowed(self):
        out, text = self.capture(deploy.fetch_tracking_ref, self.fx.repo,
                                 "origin", "no-such-branch")
        self.assertFalse(out)
        self.assertIn("FAILED", text)
        self.assertIn("may be", text)

    # --- end to end ------------------------------------------------------
    def test_e2e_ancestor_gets_past_the_guard(self):
        """HEAD contains origin/test and equals the recorded sha: the guard
        passes and the run stops at 'up to date' having done nothing."""
        self.fx.write_state(self.fx.c4)
        r = self.run_deploy()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ancestry OK", r.stdout)
        self.assertIn("Everything is up to date", r.stdout)

    def test_e2e_non_ancestor_is_refused(self):
        self.fx.checkout(self.fx.c1)
        r = self.run_deploy()
        self.assertEqual(r.returncode, deploy.ANCESTRY_EXIT_CODE, r.stdout + r.stderr)
        self.assertIn("REFUSING TO DEPLOY", r.stdout)
        self.assertIn("does NOT contain origin/test", r.stdout)
        self.assertIn("3 commit(s)", r.stdout)
        # Refused BEFORE anything else: no lock file, state untouched.
        self.assertFalse(Path(self.lock).exists())
        self.assertEqual(self.fx.read_state()["newmexicoptg.org"], {"test": self.fx.c0})

    def test_e2e_override_proceeds_and_is_recorded_in_state(self):
        """c0..c1 changes only docs/notes.md, which is excluded -- so the run
        reaches the state write with nothing to upload, and the override is
        recorded there."""
        self.fx.checkout(self.fx.c1)
        r = self.run_deploy("--allow-non-ancestor", "hotfix tree, tip verified by hand")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("--allow-non-ancestor", r.stdout)
        self.assertIn("No deployable files changed", r.stdout)
        rec = self.fx.read_state()["newmexicoptg.org"]
        self.assertEqual(rec["test"], self.fx.c1)
        self.assertEqual(rec["test_tracking_ref"], "origin/test")
        self.assertEqual(rec["test_ancestry"],
                         "overridden: hotfix tree, tip verified by hand")

    def test_e2e_verified_ancestry_is_recorded_in_state(self):
        """Same state-write path, no override: records 'verified'. c3..c4
        changes only docs/more.md, which is excluded, so there is nothing to
        upload and the run reaches the state write without a gate or a
        connection."""
        self.fx.write_state(self.fx.c3)
        r = self.run_deploy()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("No deployable files changed", r.stdout)
        rec = self.fx.read_state()["newmexicoptg.org"]
        self.assertEqual(rec["test"], self.fx.c4)
        self.assertEqual(rec["test_tracking_ref"], "origin/test")
        self.assertEqual(rec["test_ancestry"], "verified")


class NoQueuingTests(Base):
    def test_free_lock_proceeds(self):
        out, text = self.capture(deploy.check_gate_not_queued, False, path=self.lock)
        self.assertIsNone(out)
        self.assertEqual(text, "")

    def test_deploy_holder_is_refused(self):
        self.hold_lock("deploy.py")
        out, text = self.capture(deploy.check_gate_not_queued, False, path=self.lock)
        self.assertIsInstance(out, SystemExit)
        self.assertEqual(out.code, deploy.GATE_BUSY_EXIT_CODE)
        self.assertIn("REFUSING TO DEPLOY", text)
        self.assertIn("another deploy.py", text)
        self.assertIn("tool=deploy.py", text)

    def test_suite_holder_is_waited_on(self):
        self.hold_lock("run_suite")
        out, text = self.capture(deploy.check_gate_not_queued, False, path=self.lock)
        self.assertIsNone(out)
        self.assertIn("non-deploy tool (tool=run_suite)", text)
        self.assertIn("waiting is safe", text)

    def test_gate_lock_run_holder_is_waited_on(self):
        self.hold_lock("gate_lock.py run")
        out, text = self.capture(deploy.check_gate_not_queued, False, path=self.lock)
        self.assertIsNone(out)
        self.assertIn("waiting is safe", text)

    def test_wait_for_gate_queues_behind_a_deploy(self):
        self.hold_lock("deploy.py")
        out, text = self.capture(deploy.check_gate_not_queued, True, path=self.lock)
        self.assertIsNone(out)
        self.assertIn("--wait-for-gate", text)
        self.assertIn("RE-CHECKED", text)

    def test_unreadable_holder_record_is_treated_as_a_deploy(self):
        """An unknown holder is not permission."""
        holder = self.hold_lock("deploy.py")
        Path(self.lock).write_text("")  # wipe the informational record only
        out, text = self.capture(deploy.check_gate_not_queued, False, path=self.lock)
        self.assertIsInstance(out, SystemExit)
        self.assertEqual(out.code, deploy.GATE_BUSY_EXIT_CODE)
        self.assertIn("unidentified holder", text)
        holder.kill()

    # --- end to end ------------------------------------------------------
    def test_e2e_refuses_to_queue_behind_a_deploy(self):
        self.hold_lock("deploy.py")
        r = self.run_deploy("--allow-no-sync", "--gate-lock-timeout", "0.05")
        self.assertEqual(r.returncode, deploy.GATE_BUSY_EXIT_CODE, r.stdout + r.stderr)
        self.assertIn("gate lock is HELD by another deploy.py", r.stdout)
        self.assertIn("tool=deploy.py", r.stdout)
        self.assertNotIn("Running test gate", r.stdout)

    def test_e2e_waits_for_a_suite_holder(self):
        """A suite holder moves no refs, so deploy.py still waits -- proved by
        the wait timing out (exit 75) instead of refusing (exit 4)."""
        self.hold_lock("run_suite")
        r = self.run_deploy("--allow-no-sync", "--gate-lock-timeout", "0.05")
        self.assertEqual(r.returncode, gate_lock.TIMEOUT_EXIT_CODE, r.stdout + r.stderr)
        self.assertIn("waiting is safe", r.stdout)
        self.assertIn("Timed out", r.stdout)
        self.assertNotIn("Running test gate", r.stdout)

    def test_e2e_wait_for_gate_queues_behind_a_deploy(self):
        self.hold_lock("deploy.py")
        r = self.run_deploy("--allow-no-sync", "--wait-for-gate",
                            "--gate-lock-timeout", "0.05")
        self.assertEqual(r.returncode, gate_lock.TIMEOUT_EXIT_CODE, r.stdout + r.stderr)
        self.assertIn("--wait-for-gate", r.stdout)
        self.assertIn("Timed out", r.stdout)


class ListOnlyTests(Base):
    def test_lists_the_set_with_a_m_d(self):
        _u, _d, entries = deploy.compute_deployable(
            self.fx.repo, "newmexicoptg.org", self.fx.c0, self.fx.c3)
        self.assertEqual(sorted(entries), sorted([
            ("A", "journalgpt/a.php"),
            ("M", "journalgpt/index.php"),
            ("D", "journalgpt/old.php"),
        ]))
        # docs/notes.md (.md + docs/) and bin/tool.py (.py + bin/) are excluded
        # by the real rules, so they are absent above.

    def test_content_comparison_against_the_tracking_ref(self):
        # HEAD == origin/test: nothing differs.
        paths = ["journalgpt/index.php", "journalgpt/a.php"]
        self.assertEqual(deploy.differing_from_ref(self.fx.repo, "origin/test", paths), [])
        # A tree one commit back differs in exactly the file c3 changed.
        self.fx.checkout(self.fx.c2)
        self.assertEqual(deploy.differing_from_ref(self.fx.repo, "origin/test", paths),
                         ["journalgpt/index.php"])

    def test_print_deployable_set_opens_no_connection(self):
        with mock.patch.object(deploy.ftplib, "FTP",
                               side_effect=AssertionError("FTP must not be opened")):
            _r, text = self.capture(deploy.print_deployable_set, self.fx.repo,
                                    "newmexicoptg.org", "test", self.fx.c0, self.fx.c3)
        self.assertIn("A\tjournalgpt/a.php", text)
        self.assertIn("D\tjournalgpt/old.php", text)
        self.assertIn("3 deployable path(s): 2 upload, 1 DELETE", text)
        self.assertIn("HEAD contains it", text)
        self.assertIn("0 of 3 path(s) differ in content from origin/test", text)

    # --- end to end ------------------------------------------------------
    def test_e2e_list_only_touches_nothing(self):
        state_before = self.fx.state_file.read_bytes()
        r = self.run_deploy("--list-only")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("--list-only: newmexicoptg.org test", r.stdout)
        self.assertIn("A\tjournalgpt/a.php", r.stdout)
        self.assertIn("M\tjournalgpt/index.php", r.stdout)
        self.assertIn("D\tjournalgpt/old.php", r.stdout)
        self.assertIn("Nothing was uploaded, locked, bumped or recorded", r.stdout)
        # Touched nothing: no lock file created, state byte-identical, no
        # version.json written, and (by the socket blocker) no connection.
        self.assertFalse(Path(self.lock).exists())
        self.assertEqual(self.fx.state_file.read_bytes(), state_before)
        self.assertFalse((self.fx.repo / "version.json").exists())
        self.assertFalse((self.fx.repo / "journalgpt" / "version.json").exists())
        self.assertNotIn("TEST GUARD", r.stdout + r.stderr)

    def test_e2e_list_only_works_from_a_tree_that_would_be_refused(self):
        self.fx.checkout(self.fx.c1)
        r = self.run_deploy("--list-only")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("HEAD does NOT contain it", r.stdout)
        self.assertIn(f"A real run would REFUSE (exit {deploy.ANCESTRY_EXIT_CODE})", r.stdout)

    def test_e2e_list_only_needs_no_ftp_credentials(self):
        env = self.child_env()
        for k in ("FTP_HOST_TEST", "FTP_USER_TEST", "FTP_PASS_TEST"):
            env.pop(k)
        r = self.run_deploy("--list-only", env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("Missing FTP credentials", r.stdout)


class ArgParsingTests(Base):
    def test_new_flags(self):
        o = deploy.parse_args(["/r", "test", "--list-only", "--wait-for-gate",
                               "--allow-non-ancestor", "because I said so"])
        self.assertTrue(o.list_only)
        self.assertTrue(o.wait_for_gate)
        self.assertEqual(o.allow_non_ancestor, "because I said so")
        self.assertEqual((o.repo_dir, o.env), (os.path.abspath("/r"), "test"))
        o = deploy.parse_args(["/r", "prod", "--allow-non-ancestor=why not"])
        self.assertEqual(o.allow_non_ancestor, "why not")

    def test_reason_is_required_and_a_flag_is_not_a_reason(self):
        for argv in (["/r", "test", "--allow-non-ancestor"],
                     ["/r", "test", "--allow-non-ancestor", "--wait-for-gate"],
                     ["/r", "test", "--allow-non-ancestor="]):
            with self.subTest(argv=argv):
                with mock.patch("builtins.print"), self.assertRaises(SystemExit) as cm:
                    deploy.parse_args(argv)
                self.assertEqual(cm.exception.code, 1)


class StateRecordTests(Base):
    def test_record_ancestry_writes_both_fields(self):
        state = {"r": {}}
        deploy.record_ancestry(state, "r", "prod", "origin/main", "verified")
        self.assertEqual(state["r"], {"prod_tracking_ref": "origin/main",
                                      "prod_ancestry": "verified"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
