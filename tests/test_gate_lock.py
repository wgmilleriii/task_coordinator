#!/usr/bin/env python3
"""Tests for bin/gate_lock.py, the machine-wide test-gate lock.

Never runs a real gate or deploy: the "gate" is `sleep` wrapped in a tiny
python command that records start/end times. Every test uses its own lock
path under a tempdir via $NEWMEXICOPTG_GATE_LOCK, so the real
~/.cache/newmexicoptg-gate.lock is never touched.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

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


class GateLockTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.lock = os.path.join(self.tmp.name, "gate.lock")
        self.log = os.path.join(self.tmp.name, "events.log")
        self.env = dict(os.environ, NEWMEXICOPTG_GATE_LOCK=self.lock)
        self.devnull = open(os.devnull, "w")

    def tearDown(self):
        self.devnull.close()
        self.tmp.cleanup()

    def spawn(self, name, seconds, env_name, timeout_min=1):
        return subprocess.Popen(
            [sys.executable, GATE_LOCK, "run", "--env", env_name,
             "--timeout-min", str(timeout_min), "--"] + fake_gate(self.log, name, seconds),
            env=self.env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )

    def wait_for(self, pred, limit=10):
        deadline = time.time() + limit
        while time.time() < deadline:
            if pred():
                return
            time.sleep(0.05)
        self.fail("condition not reached")

    def events(self):
        out = {}
        for line in Path(self.log).read_text().splitlines():
            name, kind, t = line.split()
            out[(name, kind)] = float(t)
        return out

    def test_second_gate_waits_for_first(self):
        a = self.spawn("A", 3, "test")
        # B starts only once A's fake gate is actually running (holds the lock).
        self.wait_for(lambda: os.path.exists(self.log) and "A start" in Path(self.log).read_text())
        holder = json.loads(Path(self.lock).read_text())
        self.assertEqual(holder["pid"], a.pid)
        self.assertEqual(holder["env"], "test")
        b = self.spawn("B", 0.2, "prod")  # a PROD deploy must wait on a TEST gate too
        a_out, _ = a.communicate(timeout=30)
        b_out, _ = b.communicate(timeout=30)
        self.assertEqual(a.returncode, 0, a_out)
        self.assertEqual(b.returncode, 0, b_out)
        ev = self.events()
        self.assertGreaterEqual(ev[("B", "start")], ev[("A", "end")],
                                f"B's gate overlapped A's: {ev}")
        self.assertIn("is HELD", b_out)
        self.assertIn(f"pid={a.pid}", b_out)
        self.assertIn("env=test", b_out)
        self.assertNotIn("is HELD", a_out)

    def test_waiter_times_out_clearly_and_runs_nothing(self):
        a = self.spawn("A", 4, "test")
        self.wait_for(lambda: os.path.exists(self.log) and "A start" in Path(self.log).read_text())
        b = self.spawn("B", 0, "test", timeout_min=0.02)  # ~1.2 s
        b_out, _ = b.communicate(timeout=30)
        a.communicate(timeout=30)
        self.assertEqual(b.returncode, gate_lock.TIMEOUT_EXIT_CODE, b_out)
        self.assertIn("Timed out", b_out)
        self.assertIn(f"pid={a.pid}", b_out)
        self.assertNotIn(("B", "start"), self.events())

    def test_stale_pid_text_does_not_block(self):
        dead = subprocess.Popen([sys.executable, "-c", "pass"])
        dead.wait()
        self.assertFalse(gate_lock.pid_alive(dead.pid))
        Path(self.lock).write_text(json.dumps({
            "pid": dead.pid, "env": "prod", "tool": "deploy.py",
            "worktree": "/gone", "started": "2026-09-14T00:00:00-06:00"}) + "\n")
        held, rec = gate_lock.probe(self.lock)
        self.assertFalse(held)
        self.assertEqual(rec["pid"], dead.pid)  # text still there, but not a lock
        t0 = time.monotonic()
        with gate_lock.GateLock("test", "/here", "unittest", timeout_s=5, path=self.lock,
                                out=self.devnull):
            self.assertLess(time.monotonic() - t0, 1.0)
            rec = json.loads(Path(self.lock).read_text())
            self.assertEqual(rec["pid"], os.getpid())  # stale text overwritten
            self.assertEqual(rec["worktree"], "/here")

    def test_legacy_pid_text_does_not_block(self):
        # The old sync.py format that named dead pid 30323 on 2026-09-14.
        Path(self.lock).write_text("pid=30323 since=2026-09-14T07:00:00\n")
        with gate_lock.GateLock("test", "/here", "unittest", timeout_s=2, path=self.lock,
                                out=self.devnull):
            pass

    def test_dead_holder_releases_lock(self):
        # A holder killed mid-gate (SIGKILL, no cleanup) must not strand the lock.
        a = self.spawn("A", 30, "test")
        self.wait_for(lambda: os.path.exists(self.log) and "A start" in Path(self.log).read_text())
        self.assertTrue(gate_lock.probe(self.lock)[0])
        a.kill()
        a.wait()
        a.stdout.close()  # not communicate(): the orphaned fake gate keeps the pipe open
        # Its sleep child may linger for a moment; the lock fd is not inherited.
        self.wait_for(lambda: not gate_lock.probe(self.lock)[0], limit=5)

    def test_status_cli(self):
        r = subprocess.run([sys.executable, GATE_LOCK, "status"], env=self.env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("FREE", r.stdout)
        a = self.spawn("A", 2, "prod")
        self.wait_for(lambda: os.path.exists(self.log) and "A start" in Path(self.log).read_text())
        r = subprocess.run([sys.executable, GATE_LOCK, "status"], env=self.env,
                           capture_output=True, text=True)
        a.communicate(timeout=30)
        self.assertEqual(r.returncode, 1)
        self.assertIn("HELD", r.stdout)
        self.assertIn(f"pid={a.pid}", r.stdout)

    def test_deploy_cli_parses_gate_lock_timeout(self):
        import importlib
        deploy = importlib.import_module("deploy")
        self.assertEqual(deploy.parse_args(["/r", "test"])[3], 30)
        self.assertEqual(deploy.parse_args(["/r", "prod", "--gate-lock-timeout", "5"]),
                         ("/r", "prod", None, 5.0))
        self.assertEqual(deploy.parse_args(["/r", "test", "--gate-lock-timeout=2", "--seed", "abc"]),
                         ("/r", "test", "abc", 2.0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
