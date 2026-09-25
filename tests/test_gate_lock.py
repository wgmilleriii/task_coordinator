#!/usr/bin/env python3
"""Tests for bin/gate_lock.py, the machine-wide test-gate lock, and deploy.py's use of it.

Never runs a real gate or deploy: the "gate" is a python sleep that records
start/end times. Every test uses its own lock path under a tempdir via
$NEWMEXICOPTG_GATE_LOCK, so the real ~/.cache/newmexicoptg-gate.lock is never
touched, and $NEWMEXICOPTG_GATE_LOCK_HELD is scrubbed from the child env.
"""
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

BIN = Path(__file__).resolve().parent.parent / "bin"
sys.path.insert(0, str(BIN))
import gate_lock  # noqa: E402

GATE_LOCK = str(BIN / "gate_lock.py")


def fake_gate(log, name, seconds):
    """A command that appends 'name start/end <time>' around a sleep."""
    code = (
        "import sys,time\n"
        "log,name,secs=sys.argv[1],sys.argv[2],float(sys.argv[3])\n"
        "open(log,'a').write(f'{name} start {time.time()}\\n')\n"
        "time.sleep(secs)\n"
        "open(log,'a').write(f'{name} end {time.time()}\\n')\n"
    )
    return [sys.executable, "-c", code, log, name, str(seconds)]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.lock = os.path.join(self.tmp.name, "gate.lock")
        self.log = os.path.join(self.tmp.name, "events.log")
        self.env = dict(os.environ, NEWMEXICOPTG_GATE_LOCK=self.lock)
        self.env.pop(gate_lock.HELD_ENV, None)
        self.devnull = open(os.devnull, "w")
        self._saved_held = os.environ.pop(gate_lock.HELD_ENV, None)

    def tearDown(self):
        os.environ.pop(gate_lock.HELD_ENV, None)
        if self._saved_held is not None:
            os.environ[gate_lock.HELD_ENV] = self._saved_held
        self.devnull.close()
        self.tmp.cleanup()

    def spawn(self, name, seconds, env_name, timeout_min=1, cmd=None):
        return subprocess.Popen(
            [sys.executable, GATE_LOCK, "run", "--env", env_name,
             "--timeout-min", str(timeout_min), "--"] + (cmd or fake_gate(self.log, name, seconds)),
            env=self.env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )

    def wait_for(self, pred, limit=10):
        deadline = time.time() + limit
        while time.time() < deadline:
            if pred():
                return
            time.sleep(0.05)
        self.fail("condition not reached")

    def started(self, name):
        return lambda: os.path.exists(self.log) and f"{name} start" in Path(self.log).read_text()

    def events(self):
        out = {}
        if not os.path.exists(self.log):
            return out
        for line in Path(self.log).read_text().splitlines():
            name, kind, t = line.split()
            out[(name, kind)] = float(t)
        return out


class GateLockTests(Base):
    def test_second_gate_waits_for_first(self):
        a = self.spawn("A", 3, "test")
        self.wait_for(self.started("A"))
        holder = json.loads(Path(self.lock).read_text())
        self.assertEqual(holder["pid"], a.pid)
        self.assertEqual(holder["env"], "test")
        b = self.spawn("B", 0.2, "prod")  # a PROD deploy must wait on a TEST gate too
        a_out, _ = a.communicate(timeout=30)
        b_out, _ = b.communicate(timeout=30)
        self.assertEqual(a.returncode, 0, a_out)
        self.assertEqual(b.returncode, 0, b_out)
        ev = self.events()
        self.assertGreaterEqual(ev[("B", "start")], ev[("A", "end")], f"overlap: {ev}")
        self.assertIn("is HELD", b_out)
        self.assertIn(f"pid={a.pid}", b_out)
        self.assertIn("env=test", b_out)
        self.assertNotIn("is HELD", a_out)

    def test_waiter_times_out_clearly_and_runs_nothing(self):
        a = self.spawn("A", 4, "test")
        self.wait_for(self.started("A"))
        b = self.spawn("B", 0, "test", timeout_min=0.02)  # ~1.2 s
        b_out, _ = b.communicate(timeout=30)
        a.communicate(timeout=30)
        self.assertEqual(b.returncode, gate_lock.TIMEOUT_EXIT_CODE, b_out)
        self.assertIn("Timed out", b_out)
        self.assertIn(f"pid={a.pid}", b_out)
        self.assertNotIn(("B", "start"), self.events())

    def test_lock_held_while_orphaned_gate_child_lives(self):
        a = self.spawn("A", 3, "test")
        self.wait_for(self.started("A"))
        a.kill()
        a.wait()
        a.stdout.close()  # not communicate(): the orphaned fake gate keeps the pipe open
        self.assertNotIn(("A", "end"), self.events())
        self.assertTrue(gate_lock.probe(self.lock)[0],
                        "lock freed while the orphaned gate child is still running")
        self.wait_for(lambda: ("A", "end") in self.events(), limit=10)
        self.wait_for(lambda: not gate_lock.probe(self.lock)[0], limit=5)

    def test_waiter_blocks_after_holder_sigkilled_mid_gate(self):
        # Reader's adversarial case: kill -9 the holder while its gate sleeps,
        # then start a second gate. It must wait for the orphan, not overlap it.
        a = self.spawn("A", 3, "test")
        self.wait_for(self.started("A"))
        a.kill()
        a.wait()
        a.stdout.close()
        b = self.spawn("B", 0.2, "prod")
        b_out, _ = b.communicate(timeout=30)
        self.assertEqual(b.returncode, 0, b_out)
        ev = self.events()
        self.assertGreaterEqual(ev[("B", "start")], ev[("A", "end")],
                                f"B's gate overlapped the orphaned A gate: {ev}")
        self.assertIn("is HELD", b_out)
        self.assertIn("NOT RUNNING", b_out)  # recorded pid is the dead wrapper

    def test_run_does_not_unlock_for_background_worker(self):
        # The command exits at once, leaving a background worker that inherited
        # the fd. run must close its copy WITHOUT LOCK_UN, so the worker keeps
        # the lock until it exits.
        worker = shlex.join(fake_gate(self.log, "W", 3))
        a = self.spawn("A", 0, "test", cmd=["sh", "-c", f"{worker} >/dev/null 2>&1 &"])
        a_out, _ = a.communicate(timeout=30)
        self.assertEqual(a.returncode, 0, a_out)
        self.wait_for(self.started("W"))
        self.assertNotIn(("W", "end"), self.events())
        self.assertTrue(gate_lock.probe(self.lock)[0],
                        "run released the lock while its background worker still runs")
        self.wait_for(lambda: ("W", "end") in self.events(), limit=10)
        self.wait_for(lambda: not gate_lock.probe(self.lock)[0], limit=5)

    def test_deploy_shell_gate_holds_lock_after_deploy_sigkilled(self):
        # deploy.run_test_gate uses shell=True (sh -c "python3 <suite>" here,
        # "php <suite>" for real). Prove sh forwards the fd.
        repo = os.path.join(self.tmp.name, "repo")
        os.makedirs(repo)
        Path(repo, "fake_suite.py").write_text(
            "import time\n"
            f"open({self.log!r},'a').write(f'S start {{time.time()}}\\n')\n"
            "time.sleep(3)\n"
            f"open({self.log!r},'a').write(f'S end {{time.time()}}\\n')\n")
        driver = (
            "import sys\n"
            f"sys.path.insert(0, {str(BIN)!r})\n"
            "import deploy, gate_lock\n"
            "deploy.TEST_SUITE_CANDIDATES = ['fake_suite.py']\n"
            "lock = gate_lock.acquire_gate_lock('prod', sys.argv[1], 'deploy.py', 0.1)\n"
            "deploy.run_test_gate(sys.argv[1], lock)\n"
        )
        d = subprocess.Popen([sys.executable, "-c", driver, repo], env=self.env,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.wait_for(self.started("S"))
        d.kill()
        d.wait()
        self.assertNotIn(("S", "end"), self.events())
        self.assertTrue(gate_lock.probe(self.lock)[0],
                        "sh did not forward the lock fd: lock freed mid-suite")
        self.wait_for(lambda: ("S", "end") in self.events(), limit=10)
        self.wait_for(lambda: not gate_lock.probe(self.lock)[0], limit=5)

    def test_stale_pid_text_does_not_block(self):
        dead = subprocess.Popen([sys.executable, "-c", "pass"])
        dead.wait()
        self.assertFalse(gate_lock.pid_alive(dead.pid))
        Path(self.lock).write_text(json.dumps({
            "pid": dead.pid, "env": "prod", "tool": "deploy.py",
            "worktree": "/gone", "started": "2026-09-14T00:00:00-06:00"}) + "\n")
        held, rec = gate_lock.probe(self.lock)
        self.assertFalse(held)
        self.assertEqual(rec["pid"], dead.pid)
        t0 = time.monotonic()
        with gate_lock.GateLock("test", "/here", "unittest", timeout_s=5, path=self.lock,
                                out=self.devnull):
            self.assertLess(time.monotonic() - t0, 1.0)
            rec = json.loads(Path(self.lock).read_text())
            self.assertEqual(rec["pid"], os.getpid())
            self.assertEqual(rec["worktree"], "/here")

    def test_legacy_pid_text_does_not_block(self):
        Path(self.lock).write_text("pid=30323 since=2026-09-14T07:00:00\n")
        with gate_lock.GateLock("test", "/here", "unittest", timeout_s=2, path=self.lock,
                                out=self.devnull):
            pass

    def test_status_cli(self):
        r = subprocess.run([sys.executable, GATE_LOCK, "status"], env=self.env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("FREE", r.stdout)
        a = self.spawn("A", 2, "prod")
        self.wait_for(self.started("A"))
        r = subprocess.run([sys.executable, GATE_LOCK, "status"], env=self.env,
                           capture_output=True, text=True)
        a.communicate(timeout=30)
        self.assertEqual(r.returncode, 1)
        self.assertIn("HELD", r.stdout)
        self.assertIn(f"pid={a.pid}", r.stdout)


class ReentrancyTests(Base):
    CHILD = (
        "import os, sys, time\n"
        "sys.path.insert(0, sys.argv[1])\n"
        "import gate_lock\n"
        "t0 = time.monotonic()\n"
        "lock = gate_lock.acquire_gate_lock('test', '/child', 'child deploy.py', 0.05)\n"
        "print('INHERITED' if lock.inherited else 'ACQUIRED', lock.fileno() is not None,\n"
        "      round(time.monotonic() - t0, 1), flush=True)\n"
    )

    def test_descendant_under_run_does_not_wait_on_its_parent(self):
        # deploy.py/sync.py launched under `gate_lock.py run` used to wait on
        # its own parent until the timeout, then exit 75.
        a = self.spawn("A", 0, "manual", cmd=[sys.executable, "-c", self.CHILD, str(BIN)])
        out, _ = a.communicate(timeout=30)
        self.assertEqual(a.returncode, 0, out)
        self.assertIn("already held by ancestor", out)
        line = [l for l in out.splitlines() if l.startswith(("INHERITED", "ACQUIRED"))][0]
        kind, has_fd, secs = line.split()
        self.assertEqual(kind, "INHERITED")
        self.assertEqual(has_fd, "True")  # fd verified against the lock file, passable to a gate
        self.assertLess(float(secs), 2.0)

    def test_grandchild_through_shell_also_reuses(self):
        inner = shlex.join([sys.executable, "-c", self.CHILD, str(BIN)])
        a = self.spawn("A", 0, "manual", cmd=["sh", "-c", f"{inner}; true"])
        out, _ = a.communicate(timeout=30)
        self.assertEqual(a.returncode, 0, out)
        self.assertIn("INHERITED", out)

    def test_non_descendant_with_copied_env_still_waits(self):
        # A sibling that merely has the env var (pid alive, but NOT an ancestor)
        # gets no bypass.
        self.env["LOG"] = self.log  # the holder's child publishes its HELD value here
        a = subprocess.Popen(
            [sys.executable, GATE_LOCK, "run", "--timeout-min", "1", "--", sys.executable, "-c",
             "import os,time; open(os.environ['LOG'],'w').write(os.environ['"
             + gate_lock.HELD_ENV + "']); time.sleep(8)"],
            env=self.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.wait_for(lambda: os.path.exists(self.log) and Path(self.log).read_text())
        sib_env = dict(self.env)
        sib_env[gate_lock.HELD_ENV] = Path(self.log).read_text()
        r = subprocess.run([sys.executable, "-c", self.CHILD, str(BIN)], env=sib_env,
                           capture_output=True, text=True, timeout=30)
        a.wait(timeout=30)
        self.assertEqual(r.returncode, gate_lock.TIMEOUT_EXIT_CODE, r.stdout + r.stderr)
        self.assertIn("is HELD", r.stdout)
        self.assertNotIn("already held by ancestor", r.stdout)
        self.assertIn("Timed out", r.stdout)

    def _unrelated_holder(self, seconds=10):
        """A real holder that is NOT an ancestor of the children we spawn."""
        h = self.spawn("H", seconds, "test")
        self.wait_for(self.started("H"))
        return h

    def _child_with_held_env(self, held_value, pass_fds=()):
        env = dict(self.env)
        env[gate_lock.HELD_ENV] = held_value
        return subprocess.run([sys.executable, "-c", self.CHILD, str(BIN)], env=env,
                              capture_output=True, text=True, timeout=60, pass_fds=pass_fds)

    def assertWaitedNoBypass(self, r):
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, gate_lock.TIMEOUT_EXIT_CODE, out)
        self.assertIn("is HELD", out)
        self.assertNotIn("already held by ancestor", out)
        self.assertNotIn("INHERITED", out)

    def test_bypass3_case1_live_ancestor_closed_fd_waits(self):
        # Reader's [1]: HELD names a LIVE ANCESTOR (this test process) but the
        # fd is closed, while an unrelated process really holds the lock.
        h = self._unrelated_holder()
        closed_fd = 200
        try:
            os.close(closed_fd)
        except OSError:
            pass
        r = self._child_with_held_env(f"{os.getpid()}:{closed_fd}:{self.lock}")
        h.communicate(timeout=30)
        self.assertWaitedNoBypass(r)

    def test_bypass3_case2_live_ancestor_open_unlocked_fd_waits(self):
        # Reader's [2]: same dev/inode, fd really open and inherited, but it is
        # NOT the descriptor holding the lock. flock proves that; must wait.
        h = self._unrelated_holder()
        with open(self.lock, "a+") as unlocked:
            fd = unlocked.fileno()
            r = self._child_with_held_env(f"{os.getpid()}:{fd}:{self.lock}", pass_fds=(fd,))
        h.communicate(timeout=30)
        self.assertWaitedNoBypass(r)

    def test_dead_holder_pid_in_env_gives_no_bypass(self):
        dead = subprocess.Popen([sys.executable, "-c", "pass"])
        dead.wait()
        env = dict(self.env)
        env[gate_lock.HELD_ENV] = f"{dead.pid}:3:{self.lock}"
        r = subprocess.run([sys.executable, "-c", self.CHILD, str(BIN)], env=env,
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ACQUIRED", r.stdout)  # lock was free: acquired for real, no bypass


class DeployTests(Base):
    def test_v1_loads_v3_style_sync_even_if_v3_deploy_py_is_broken(self):
        # v1 deploy.py imports sync.py from SYNC_BIN. sync.py must reach the
        # shared helpers via deploy_common, never via that checkout's deploy.py.
        sync_bin = os.path.join(self.tmp.name, "v3bin")
        os.makedirs(sync_bin)
        for name in ("gate_lock.py", "deploy_common.py"):
            Path(sync_bin, name).write_bytes((BIN / name).read_bytes())
        Path(sync_bin, "deploy.py").write_text("raise RuntimeError('broken uncommitted deploy.py')\n")
        Path(sync_bin, "sync.py").write_text(
            "import sys\nfrom pathlib import Path\n"
            "sys.path.insert(0, str(Path(__file__).resolve().parent))\n"
            "from deploy_common import get_repo_excludes, should_exclude, run_test_gate\n"
            "from gate_lock import acquire_gate_lock, find_test_suite\n"
            "LOADED = True\n")
        driver = (
            "import sys\n"
            f"sys.path.insert(0, {str(BIN)!r})\n"
            "import deploy\n"
            "deploy.SYNC_BIN = sys.argv[1]\n"
            "s = deploy.require_sync(False)\n"
            "print('SYNC_LOADED', getattr(s, 'LOADED', False), 'deploy' in sys.modules and "
            "getattr(sys.modules['deploy'], '__file__', '').startswith(sys.argv[1]))\n"
        )
        r = subprocess.run([sys.executable, "-c", driver, sync_bin], env=self.env,
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("SYNC_LOADED True False", r.stdout)


    def test_deploy_cli_parses_flags(self):
        # parse_args returns a namespace since the ancestry-guard flags landed
        # (2026-09-25); it used to return a 5-tuple.
        import deploy
        self.assertEqual(deploy.parse_args(["/r", "test"]).gate_lock_timeout_min, 60)
        o = deploy.parse_args(["/r", "prod", "--gate-lock-timeout", "5"])
        self.assertEqual((o.repo_dir, o.env, o.seed_sha, o.gate_lock_timeout_min,
                          o.allow_no_sync), ("/r", "prod", None, 5.0, False))
        self.assertEqual((o.allow_non_ancestor, o.wait_for_gate, o.list_only),
                         (None, False, False))
        o = deploy.parse_args(["/r", "test", "--gate-lock-timeout=2", "--seed", "abc",
                               "--allow-no-sync"])
        self.assertEqual((o.repo_dir, o.env, o.seed_sha, o.gate_lock_timeout_min,
                          o.allow_no_sync), ("/r", "test", "abc", 2.0, True))

    def test_missing_sync_fails_closed(self):
        import deploy
        with mock.patch.object(deploy, "_load_sync", return_value=None), \
                mock.patch("builtins.print") as p:
            with self.assertRaises(SystemExit) as cm:
                deploy.require_sync(False)
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("REFUSING TO DEPLOY", " ".join(str(c) for c in p.call_args_list))
        with mock.patch.object(deploy, "_load_sync", return_value=None), \
                mock.patch("builtins.print"):
            self.assertIsNone(deploy.require_sync(True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
