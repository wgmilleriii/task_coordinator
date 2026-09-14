#!/usr/bin/env python3
"""Machine-wide lock for the journalgpt test gate (shared MAMP DB journal_ai_test).

This file is kept BYTE-IDENTICAL in task_coordinator/bin and
task_coordinator_v3/bin. v1 deploy.py, v3 deploy.py and v3 sync.py all queue on
the one lock it defines. Edit both copies together.

WHY (2026-09-14): deploy.py ran run_suite.php BEFORE taking its per-env deploy
lock, and that lock is keyed per repo+env anyway. Two deploys started seconds
apart ran their gates concurrently against the one shared test DB. Tests such
as V6PipelineEndToEndTest and AsyncHubActionAuthzTest delete and recreate the
same fixture rows, so each gate corrupted the other (FK violations on
conversations.user_id, "Research project not found"). A seat's "is a gate
running?" check came four seconds before the second gate started.

DESIGN
  * One flock on a fixed path (default ~/.cache/newmexicoptg-gate.lock,
    override with $NEWMEXICOPTG_GATE_LOCK). Same path for test AND prod: both
    gate against the same local DB.
  * The kernel lock is the ONLY thing that excludes. The JSON text in the file
    (pid, env, worktree, tool, started) is written by the holder after it
    acquires and is purely informational. flock is released by the OS when the
    last descriptor copy closes, so a dead holder can never block anyone and
    stale text is simply overwritten by the next acquirer. Nobody should ever
    delete this file; deleting it would let a new process lock a different
    inode while the old holder still runs.
  * Callers never unlock. deploy.py, sync.py and `run` all hold the lock until
    their process exits (or, for `run`, close their own descriptor WITHOUT
    LOCK_UN). LOCK_UN would drop the lock for EVERY copy of the descriptor,
    including a gate child or background worker still using the shared DB.
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
  * Re-entrant for descendants. The acquirer exports
    NEWMEXICOPTG_GATE_LOCK_HELD=<pid>:<fd>:<lock path>. acquire_gate_lock()
    in a descendant (e.g. deploy.py or sync.py launched under
    `gate_lock.py run`) does not wait on its own ancestor: it proceeds only
    when the path matches, that pid is alive AND is one of its ancestors, AND
    flock(LOCK_EX|LOCK_NB) succeeds on the inherited fd -- proof that this
    descriptor is the one holding the lock. It then passes that fd on to its
    own gate child. Anyone else (a sibling, a leaked env var, a dead pid, a
    closed or open-but-unlocked fd) gets no bypass and waits normally.
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
HELD_ENV = "NEWMEXICOPTG_GATE_LOCK_HELD"

# Suites that run against the shared local DB. Union of what v1 deploy.py and
# v3 deploy.py gate on; taking the lock for a repo with either is always safe.
SHARED_DB_SUITES = [
    "journalgpt/tests/run_suite.php",
    "journalgpt/tests/security_and_eval_suite.php",
]


def lock_path():
    return Path(os.environ.get("NEWMEXICOPTG_GATE_LOCK") or DEFAULT_LOCK_PATH)


def find_test_suite(repo_dir, candidates=None):
    """First candidate suite present under repo_dir, or None."""
    for candidate in (SHARED_DB_SUITES if candidates is None else candidates):
        if (Path(repo_dir) / candidate).exists():
            return candidate
    return None


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


def _parent_pid(pid):
    if pid == os.getpid():
        return os.getppid()
    try:
        out = subprocess.run(["ps", "-o", "ppid=", "-p", str(pid)],
                             capture_output=True, text=True, timeout=5).stdout.strip()
        return int(out) if out else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def is_ancestor(pid):
    """True if pid is a (live) ancestor of this process."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 1 or pid == os.getpid():
        return False
    cur = os.getpid()
    for _ in range(64):
        cur = _parent_pid(cur)
        if not cur or cur <= 1:
            return False
        if cur == pid:
            return True
    return False


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
        # the text is stale/racing: an orphaned gate child (or a worker it
        # spawned) still holds the passed-through descriptor, or a new holder
        # has not written its record yet. Keep waiting, never delete.
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
    """The lock, really acquired. Hold for gate + upload + remote migrate.

    Released by the OS when the process exits. release() (LOCK_UN) exists for
    in-process tests; production callers use abandon() or just exit.
    """

    inherited = False

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
        # Descendants inherit this and do not wait on us (see held_by_ancestor).
        os.environ[HELD_ENV] = f"{os.getpid()}:{self.fh.fileno()}:{self.path}"
        waited = time.monotonic() - start
        self._say(f"  gate lock acquired ({self.path}, waited {waited:.0f}s)")
        return self

    def fileno(self):
        """The held lock's fd. Pass it to the gate child via
        subprocess pass_fds=(lock.fileno(),) so a SIGKILLed parent does not free
        the lock while its gate is still running."""
        return self.fh.fileno()

    def abandon(self):
        """Close OUR descriptor without LOCK_UN. Any child or background worker
        that inherited the fd keeps the lock until it exits too."""
        if self.fh is not None:
            self.fh.close()
            self.fh = None

    def release(self):
        """LOCK_UN: frees the lock for EVERY descriptor copy. Tests only."""
        if self.fh is None:
            return
        try:
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


class InheritedGateLock:
    """An ancestor holds the lock for us. Never unlocks anything."""

    inherited = True

    def __init__(self, holder_pid, fd, path):
        self.holder_pid = holder_pid
        self.fd = fd
        self.path = Path(path)

    def fileno(self):
        """The inherited fd, verified by flock to hold the lock. Never None."""
        return self.fd

    def abandon(self):
        pass

    release = abandon


def held_by_ancestor(path=None):
    """InheritedGateLock if an ancestor of this process holds the gate lock
    (per $NEWMEXICOPTG_GATE_LOCK_HELD), else None."""
    raw = os.environ.get(HELD_ENV, "")
    parts = raw.split(":", 2)
    if len(parts) != 3:
        return None
    pid_s, fd_s, held_path = parts
    path = Path(path or lock_path())
    try:
        if os.path.realpath(held_path) != os.path.realpath(path):
            return None
        pid, fd = int(pid_s), int(fd_s)
    except (ValueError, OSError):
        return None
    if not pid_alive(pid) or not is_ancestor(pid):
        return None
    # PROOF, not inference (round-3 reader). Same dev/inode only proves the
    # file is OPEN. flock(LOCK_EX|LOCK_NB) on the inherited descriptor succeeds
    # only if this exact open file description already holds the lock (or the
    # lock is free, in which case we now genuinely hold it through this fd).
    # A closed fd, another file, or an open-but-unlocked copy while someone
    # else holds the lock all fail here, and the caller acquires normally. No
    # usable fd means no bypass, so a nested deploy never runs its gate child
    # without the lock fd.
    try:
        a, b = os.fstat(fd), os.stat(path)
        if (a.st_dev, a.st_ino) != (b.st_dev, b.st_ino):
            return None
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return None
    return InheritedGateLock(pid, fd, path)


def acquire_gate_lock(env, worktree, tool, timeout_min=DEFAULT_TIMEOUT_MIN, path=None, out=None):
    """Take the machine-wide gate lock, or reuse an ancestor's, or exit 75 on
    timeout. Callers take it BEFORE any sync.DeployLock and never release it:
    the OS drops it when the process (and every fd-inheriting child) exits."""
    out = out or sys.stdout
    inherited = held_by_ancestor(path)
    if inherited is not None:
        print(f"  gate lock already held by ancestor pid={inherited.holder_pid}; "
              f"not waiting on our own parent", file=out, flush=True)
        return inherited
    try:
        return GateLock(env=env, worktree=worktree, tool=tool,
                        timeout_s=timeout_min * 60, path=path, out=out).acquire()
    except GateLockTimeout as e:
        print(str(e), file=out, flush=True)
        sys.exit(TIMEOUT_EXIT_CODE)


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
    lock = acquire_gate_lock(args.env, os.getcwd(), "gate_lock.py run",
                             timeout_min=args.timeout_min)
    fd = lock.fileno()
    try:
        # The child holds the lock too (and sees HELD_ENV, so a deploy.py or
        # sync.py it launches does not wait on us).
        return subprocess.run(command, pass_fds=(fd,) if fd is not None else ()).returncode
    finally:
        # Close without LOCK_UN: a background worker the command left running
        # still holds its inherited copy and must keep the lock until it exits.
        lock.abandon()


if __name__ == "__main__":
    sys.exit(main())
