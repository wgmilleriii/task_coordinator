#!/usr/bin/env python3
"""Machine-wide lock for the journalgpt test gate (shared MAMP DB journal_ai_test).

WHY (2026-09-14): deploy.py ran run_suite.php BEFORE taking its per-env deploy
lock, and that lock is keyed per repo+env anyway. Two deploys started seconds
apart ran their gates concurrently against the one shared test DB. Tests such
as V6PipelineEndToEndTest and AsyncHubActionAuthzTest delete and recreate the
same fixture rows, so each gate corrupted the other (FK violations on
conversations.user_id, "Research project not found"). A seat's "is a gate
running?" check came four seconds before the second gate started.

DESIGN
  * One flock on a fixed path (default ~/.cache/newmexicoptg-gate.lock,
    override with $NEWMEXICOPTG_GATE_LOCK). Same path for test AND prod
    deploys: both gate against the same local DB.
  * The kernel lock is the ONLY thing that excludes. The JSON text in the file
    (pid, env, worktree, tool, started) is written by the holder after it
    acquires and is purely informational. flock is released by the OS when the
    holding process dies, so a dead holder can never block anyone, and stale
    text is simply overwritten by the next acquirer. Nobody should ever delete
    this file; deleting it would let a new process lock a different inode
    while the old holder still runs.
  * The gate child is started with the lock fd passed through (pass_fds), so
    the child holds the lock too. If the deploy process is SIGKILLed while its
    gate is still running, the orphaned gate keeps the lock until it exits.
    That is intended: the orphan is still writing to the shared DB. The fd is
    forwarded by `sh -c` (deploy.py's shell=True path) to php as well. Any
    background worker the suite spawns without closing fds also inherits it
    and can hold the lock until that worker exits. That can only DELAY the
    next gate, never let two overlap. `status` shows the recorded holder pid;
    if it says NOT RUNNING while HELD, an orphaned gate child is the holder
    (find it with `lsof <lockfile>`).
  * Waiters print the holder (marking a recorded pid that is no longer alive),
    poll, and give up after a timeout with a clear message and exit code 75.

CLI (for seats running a suite by hand, and for "is a gate running?"):
  gate_lock.py status
      Prints FREE or HELD plus the holder record. Exit 0 free, 1 held.
      This is a real non-blocking flock probe, not a pid-file read.
  gate_lock.py run [--env ENV] [--timeout-min N] -- CMD [ARGS...]
      Waits for the lock, runs CMD while holding it, exits with CMD's code.
      e.g. gate_lock.py run --env manual -- php journalgpt/tests/run_suite.php
"""
import argparse
import errno
import fcntl
import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

DEFAULT_LOCK_PATH = Path.home() / ".cache" / "newmexicoptg-gate.lock"
DEFAULT_TIMEOUT_MIN = 60  # a prod deploy has been recorded at ~50 min
TIMEOUT_EXIT_CODE = 75  # EX_TEMPFAIL: try again later, nothing was done


def lock_path():
    return Path(os.environ.get("NEWMEXICOPTG_GATE_LOCK") or DEFAULT_LOCK_PATH)


class GateLockTimeout(Exception):
    pass


def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # exists, owned by someone else
    except (ValueError, TypeError, OverflowError):
        return False
    return True


def read_holder(path):
    """Parse the informational holder record. Never used to decide exclusion."""
    try:
        text = Path(path).read_text().strip()
    except OSError:
        return None
    if not text:
        return None
    try:
        rec = json.loads(text)
        if isinstance(rec, dict):
            return rec
    except ValueError:
        pass
    return {"raw": text}  # legacy / foreign text


def describe_holder(rec):
    if not rec:
        return "holder record not written yet"
    if "raw" in rec:
        return f"unparsed holder text: {rec['raw'][:200]!r}"
    pid = rec.get("pid")
    alive = pid_alive(pid) if pid is not None else False
    s = (f"pid={pid}{'' if alive else ' (NOT RUNNING)'} env={rec.get('env')} "
         f"tool={rec.get('tool')} worktree={rec.get('worktree')} "
         f"started={rec.get('started')} host={rec.get('host')}")
    if not alive:
        # The flock is held by SOME live process (or we would have got it), so
        # the text is stale/racing: the new holder has not written its record
        # yet, or an orphaned gate child (or a worker it spawned) still holds
        # the passed-through descriptor. Keep waiting, never delete.
        s += (" -- recorded pid is dead but the kernel lock is held: an orphaned "
              "gate child (or its worker) still holds it, or a new holder has "
              "not written its record yet; waiting on the real holder")
    return s


def probe(path=None):
    """Non-blocking check: (held: bool, holder_record|None)."""
    path = Path(path or lock_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+") as fh:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            if e.errno in (errno.EWOULDBLOCK, errno.EAGAIN):
                return True, read_holder(path)
            raise
        fcntl.flock(fh, fcntl.LOCK_UN)
        return False, read_holder(path)


class GateLock:
    """Context manager. Hold for gate + upload + remote migrate.

    Released by __exit__, or by the OS when the process exits for any reason.
    """

    def __init__(self, env, worktree, tool, timeout_s=DEFAULT_TIMEOUT_MIN * 60,
                 path=None, poll_s=2.0, out=None):
        self.path = Path(path or lock_path())
        self.env = env
        self.worktree = worktree
        self.tool = tool
        self.timeout_s = timeout_s
        self.poll_s = poll_s
        self.out = out or sys.stdout
        self.fh = None

    def _say(self, msg):
        print(msg, file=self.out, flush=True)

    def acquire(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # "a+" never truncates on open, so waiters cannot wipe the holder's record.
        self.fh = open(self.path, "a+")
        start = time.monotonic()
        announced_text = None
        while True:
            try:
                fcntl.flock(self.fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as e:
                if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
            waited = time.monotonic() - start
            desc = describe_holder(read_holder(self.path))
            if desc != announced_text:
                self._say(f"  gate lock {self.path} is HELD -> {desc}")
                self._say(f"  waiting up to {self.timeout_s / 60:g} min "
                          f"(--gate-lock-timeout to change)...")
                announced_text = desc
            if waited >= self.timeout_s:
                self.fh.close()
                self.fh = None
                raise GateLockTimeout(
                    f"Timed out after {self.timeout_s / 60:g} min waiting for the "
                    f"machine-wide gate lock {self.path}. Holder: {desc}. Another "
                    f"gate/deploy is still running against the shared test DB. "
                    f"Nothing was run or uploaded. Do NOT delete the lock file; "
                    f"re-run later or raise the timeout.")
            time.sleep(self.poll_s)
        # Ours now: replace any stale text with our record.
        rec = {
            "pid": os.getpid(),
            "env": self.env,
            "tool": self.tool,
            "worktree": self.worktree,
            "started": datetime.now().astimezone().isoformat(timespec="seconds"),
            "host": socket.gethostname(),
        }
        self.fh.seek(0)
        self.fh.truncate()
        self.fh.write(json.dumps(rec) + "\n")
        self.fh.flush()
        waited = time.monotonic() - start
        self._say(f"  gate lock acquired ({self.path}, waited {waited:.0f}s)")
        return self

    def fileno(self):
        """The held lock's fd. Pass it to the gate child via
        subprocess pass_fds=(lock.fileno(),) so a SIGKILLed parent does not free
        the lock while its gate is still running."""
        return self.fh.fileno()

    def release(self):
        if self.fh is None:
            return
        try:
            # Leave the record in place (it names the LAST holder, useful when
            # reading a failed run) but make it clear it is not live.
            self.fh.seek(0)
            self.fh.truncate()
            fcntl.flock(self.fh, fcntl.LOCK_UN)
        finally:
            self.fh.close()
            self.fh = None

    def __enter__(self):
        return self.acquire()

    def __exit__(self, *exc):
        self.release()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="report whether the gate lock is held")
    run = sub.add_parser("run", help="run a command while holding the gate lock")
    run.add_argument("--env", default="manual")
    run.add_argument("--timeout-min", type=float, default=DEFAULT_TIMEOUT_MIN)
    run.add_argument("command", nargs=argparse.REMAINDER)
    args = ap.parse_args(argv)

    if args.cmd == "status":
        held, rec = probe()
        if held:
            print(f"HELD {lock_path()} -> {describe_holder(rec)}")
            return 1
        print(f"FREE {lock_path()}")
        return 0

    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        ap.error("run needs a command after --")
    try:
        with GateLock(args.env, os.getcwd(), "gate_lock.py run",
                      timeout_s=args.timeout_min * 60) as lock:
            # The child holds the lock too, so killing this wrapper cannot free
            # it while the command is still running against the shared DB.
            return subprocess.run(command, pass_fds=(lock.fileno(),)).returncode
    except GateLockTimeout as e:
        print(str(e), file=sys.stderr)
        return TIMEOUT_EXIT_CODE


if __name__ == "__main__":
    sys.exit(main())
