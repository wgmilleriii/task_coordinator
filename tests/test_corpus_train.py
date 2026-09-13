#!/usr/bin/env python3
"""Unit tests for bin/corpus_train.py's manifest/review/ledger logic.

No network: every FTP interaction goes through FakeFTP below. Nothing here
calls --execute against a real server, and nothing here needs prod
credentials. A handful of tests use a disposable throwaway git repo (created
under a tempdir, deleted on teardown) to exercise changed_corpus_files()
against real git plumbing without touching this repo or newmexicoptg.org.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))
import corpus_train as ct  # noqa: E402


class FakeFTP:
    """Stands in for ftplib.FTP: only the methods corpus_train.py calls.

    - sizes: {remote_path: int}          -- what SIZE returns (absent -> raises)
    - mdtms: {remote_path: "20260830..."} -- what MDTM returns (absent -> raises)
    - stored: {remote_path: bytes}        -- what STOR wrote, for assertions
    - deleted: [remote_path, ...]         -- what DELE was called with
    """
    def __init__(self, sizes=None, mdtms=None):
        self.sizes = dict(sizes or {})
        self.mdtms = dict(mdtms or {})
        self.stored = {}
        self.deleted = []
        self.voidcmds = []
        self.mkds = []

    def mkd(self, path):
        # A real server raises error_perm when the directory exists; the
        # fake records every attempt and raises on the second one for a path.
        if path in self.mkds:
            raise Exception("550 exists")
        self.mkds.append(path)

    def voidcmd(self, cmd):
        self.voidcmds.append(cmd)

    def size(self, path):
        if path not in self.sizes:
            raise Exception(f"550 {path}: No such file")
        return self.sizes[path]

    def sendcmd(self, cmd):
        assert cmd.startswith("MDTM ")
        path = cmd[len("MDTM "):]
        if path not in self.mdtms:
            raise Exception(f"550 {path}: No such file")
        return f"213 {self.mdtms[path]}"

    def storbinary(self, cmd, fileobj):
        assert cmd.startswith("STOR ")
        path = cmd[len("STOR "):]
        self.stored[path] = fileobj.read()
        # A real upload changes what SIZE reports afterward.
        self.sizes[path] = len(self.stored[path])

    def delete(self, path):
        if path not in self.sizes:
            raise Exception(f"550 {path}: No such file")
        del self.sizes[path]
        self.deleted.append(path)


class TinyGitRepo:
    """A disposable git repo under a tempdir, for changed_corpus_files()
    tests. Not related to this project's or newmexicoptg.org's repos."""
    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="corpus_train_test_")
        self._run("git init -q")
        self._run("git config user.email test@example.com")
        self._run("git config user.name Test")

    def _run(self, cmd):
        result = subprocess.run(cmd, shell=True, cwd=self.dir,
                                 capture_output=True, text=True)
        assert result.returncode == 0, f"{cmd}: {result.stderr}"
        return result.stdout.strip()

    def write(self, relpath, content):
        p = Path(self.dir) / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    def commit(self, message):
        self._run("git add -A")
        self._run(f'git commit -q -m "{message}"')
        return self._run("git rev-parse HEAD")

    def rm(self, relpath):
        (Path(self.dir) / relpath).unlink()

    def cleanup(self):
        import shutil
        shutil.rmtree(self.dir, ignore_errors=True)


class BuildManifestTests(unittest.TestCase):
    def setUp(self):
        self.repo = TinyGitRepo()
        self.addCleanup(self.repo.cleanup)

    def _write_and_commit_corpus_file(self, slug, body, msg):
        path = f"journalgpt/corpus/articles/PTJ-1968-02/{slug}.md"
        self.repo.write(path, body)
        sha = self.repo.commit(msg)
        return path, sha

    def test_upload_when_prod_has_no_file(self):
        path, sha = self._write_and_commit_corpus_file(
            "new-article", "---\ncsv_number: 1\n---\n\nbody text\n", "add")
        ftp = FakeFTP()  # nothing on "prod"
        manifest = ct.build_manifest(self.repo.dir, sha, [("A", path)], ftp, "/")
        self.assertEqual(len(manifest), 1)
        self.assertEqual(manifest[0]["action"], "upload")
        self.assertEqual(manifest[0]["path"], path)
        self.assertIsNotNone(manifest[0]["local_sha"])
        self.assertIsNone(manifest[0]["prod_size"])

    def test_skip_identical_when_prod_size_matches(self):
        body = "---\ncsv_number: 1\n---\n\nbody text\n"
        path, sha = self._write_and_commit_corpus_file("same-size", body, "add")
        local_size = len((Path(self.repo.dir) / path).read_bytes())
        ftp = FakeFTP(sizes={f"/{path}": local_size})
        manifest = ct.build_manifest(self.repo.dir, sha, [("M", path)], ftp, "/")
        self.assertEqual(manifest[0]["action"], "skip-identical")

    def test_upload_when_prod_size_differs(self):
        body = "---\ncsv_number: 1\n---\n\nbody text\n"
        path, sha = self._write_and_commit_corpus_file("diff-size", body, "add")
        ftp = FakeFTP(sizes={f"/{path}": 999999})
        manifest = ct.build_manifest(self.repo.dir, sha, [("M", path)], ftp, "/")
        self.assertEqual(manifest[0]["action"], "upload")

    def test_delete_when_status_d_and_prod_has_file(self):
        path = "journalgpt/corpus/articles/PTJ-1968-02/retired.md"
        ftp = FakeFTP(sizes={f"/{path}": 123})
        manifest = ct.build_manifest(self.repo.dir, "HEAD", [("D", path)], ftp, "/")
        self.assertEqual(manifest[0]["action"], "delete")
        self.assertIsNone(manifest[0]["local_sha"])

    def test_skip_absent_when_status_d_and_prod_already_missing(self):
        path = "journalgpt/corpus/articles/PTJ-1968-02/already-gone.md"
        ftp = FakeFTP()
        manifest = ct.build_manifest(self.repo.dir, "HEAD", [("D", path)], ftp, "/")
        self.assertEqual(manifest[0]["action"], "skip-absent")

    def test_scope_violation_raises(self):
        ftp = FakeFTP()
        with self.assertRaises(AssertionError):
            ct.build_manifest(self.repo.dir, "HEAD",
                               [("M", "journalgpt/cli/some_script.py")], ftp, "/")

    def test_traversal_path_raises(self):
        ftp = FakeFTP()
        with self.assertRaises(AssertionError):
            ct.build_manifest(
                self.repo.dir, "HEAD",
                [("M", "journalgpt/corpus/articles/../../../etc/passwd.md")],
                ftp, "/",
            )


class IsInScopeTests(unittest.TestCase):
    """The hardening item from feat-corpus-train's safety review: a bare
    startswith(CORPUS_PREFIX) is foolable by a '..' segment or an absolute
    path; is_in_scope() must normalize first."""

    def test_ordinary_corpus_md_path_is_in_scope(self):
        self.assertTrue(ct.is_in_scope("journalgpt/corpus/articles/PTJ-1968-02/a.md"))

    def test_harmless_internal_dotdot_still_in_scope(self):
        # Normalizes back to a real in-scope path -- not every '..' is an
        # escape attempt, only ones that survive normalization out of scope.
        self.assertTrue(ct.is_in_scope(
            "journalgpt/corpus/articles/PTJ-1968-02/../PTJ-1968-02/a.md"))

    def test_traversal_above_corpus_root_rejected(self):
        self.assertFalse(ct.is_in_scope(
            "journalgpt/corpus/articles/../../../etc/passwd"))

    def test_absolute_path_rejected(self):
        self.assertFalse(ct.is_in_scope("/etc/passwd"))

    def test_absolute_path_inside_the_prefix_string_still_rejected(self):
        # An absolute path that happens to CONTAIN the prefix substring must
        # not pass on a raw string match; is_in_scope requires a relative,
        # normalized path that starts with the prefix.
        self.assertFalse(ct.is_in_scope("/journalgpt/corpus/articles/a.md"))

    def test_prefix_lookalike_directory_rejected(self):
        # "articlesXX" starts with the same characters as "articles" but is
        # a different, sibling directory -- must not pass a boundary-blind
        # substring check.
        self.assertFalse(ct.is_in_scope("journalgpt/corpus/articlesXX/a.md"))

    def test_non_md_file_rejected(self):
        self.assertFalse(ct.is_in_scope("journalgpt/corpus/articles/PTJ-1968-02/a.txt"))

    def test_unrelated_path_rejected(self):
        self.assertFalse(ct.is_in_scope("journalgpt/cli/some_script.py"))

    def test_dotdot_alone_rejected(self):
        self.assertFalse(ct.is_in_scope("journalgpt/corpus/articles/.."))


class ChangedCorpusFilesTests(unittest.TestCase):
    def setUp(self):
        self.repo = TinyGitRepo()
        self.addCleanup(self.repo.cleanup)

    def test_only_corpus_md_paths_are_returned(self):
        self.repo.write("journalgpt/corpus/articles/PTJ-1968-02/a.md", "one\n")
        self.repo.write("journalgpt/cli/unrelated.py", "print(1)\n")
        self.repo.write("README.md", "not corpus\n")
        base = self.repo.commit("base")

        self.repo.write("journalgpt/corpus/articles/PTJ-1968-02/a.md", "one changed\n")
        self.repo.write("journalgpt/cli/unrelated.py", "print(2)\n")
        head = self.repo.commit("change")

        changes = ct.changed_corpus_files(self.repo.dir, f"{base}..{head}")
        self.assertEqual(changes, [("M", "journalgpt/corpus/articles/PTJ-1968-02/a.md")])

    def test_delete_is_reported(self):
        self.repo.write("journalgpt/corpus/articles/PTJ-1968-02/a.md", "one\n")
        base = self.repo.commit("base")
        self.repo.rm("journalgpt/corpus/articles/PTJ-1968-02/a.md")
        head = self.repo.commit("delete")
        changes = ct.changed_corpus_files(self.repo.dir, f"{base}..{head}")
        self.assertEqual(changes, [("D", "journalgpt/corpus/articles/PTJ-1968-02/a.md")])

    def test_rename_becomes_delete_plus_add(self):
        self.repo.write("journalgpt/corpus/articles/PTJ-1968-02/old-name.md",
                         "x\n" * 50)  # long enough for git to detect a rename
        base = self.repo.commit("base")
        content = (Path(self.repo.dir) / "journalgpt/corpus/articles/PTJ-1968-02/old-name.md").read_text()
        self.repo.rm("journalgpt/corpus/articles/PTJ-1968-02/old-name.md")
        self.repo.write("journalgpt/corpus/articles/PTJ-1968-02/new-name.md", content)
        head = self.repo.commit("rename")
        changes = set(ct.changed_corpus_files(self.repo.dir, f"{base}..{head}"))
        self.assertIn(("D", "journalgpt/corpus/articles/PTJ-1968-02/old-name.md"), changes)
        self.assertIn(("A", "journalgpt/corpus/articles/PTJ-1968-02/new-name.md"), changes)


class ValidateReviewsTests(unittest.TestCase):
    def test_three_distinct_approvals_on_exact_sha_pass(self):
        reviews = [
            {"reviewer": "mechanical", "sha": "abc123", "verdict": "APPROVE"},
            {"reviewer": "content", "sha": "abc123", "verdict": "APPROVE"},
            {"reviewer": "deploy", "sha": "abc123", "verdict": "APPROVE"},
        ]
        ok, reason = ct.validate_reviews(reviews, "abc123")
        self.assertTrue(ok, reason)

    def test_fewer_than_three_fails(self):
        reviews = [
            {"reviewer": "mechanical", "sha": "abc123", "verdict": "APPROVE"},
            {"reviewer": "content", "sha": "abc123", "verdict": "APPROVE"},
        ]
        ok, reason = ct.validate_reviews(reviews, "abc123")
        self.assertFalse(ok)

    def test_approval_on_wrong_sha_does_not_count(self):
        reviews = [
            {"reviewer": "mechanical", "sha": "OLD_SHA", "verdict": "APPROVE"},
            {"reviewer": "content", "sha": "abc123", "verdict": "APPROVE"},
            {"reviewer": "deploy", "sha": "abc123", "verdict": "APPROVE"},
        ]
        ok, reason = ct.validate_reviews(reviews, "abc123")
        self.assertFalse(ok)

    def test_reject_verdict_does_not_count(self):
        reviews = [
            {"reviewer": "mechanical", "sha": "abc123", "verdict": "APPROVE"},
            {"reviewer": "content", "sha": "abc123", "verdict": "REJECT"},
            {"reviewer": "deploy", "sha": "abc123", "verdict": "APPROVE"},
        ]
        ok, reason = ct.validate_reviews(reviews, "abc123")
        self.assertFalse(ok)

    def test_duplicate_reviewer_name_does_not_count_twice(self):
        reviews = [
            {"reviewer": "mechanical", "sha": "abc123", "verdict": "APPROVE"},
            {"reviewer": "mechanical", "sha": "abc123", "verdict": "APPROVE"},
            {"reviewer": "deploy", "sha": "abc123", "verdict": "APPROVE"},
        ]
        ok, reason = ct.validate_reviews(reviews, "abc123")
        self.assertFalse(ok)

    def test_non_list_input_rejected(self):
        ok, reason = ct.validate_reviews({"not": "a list"}, "abc123")
        self.assertFalse(ok)


class ExecuteTests(unittest.TestCase):
    def setUp(self):
        self.repo = TinyGitRepo()
        self.addCleanup(self.repo.cleanup)

    def test_upload_verifies_size_and_reports_no_problems(self):
        path = "journalgpt/corpus/articles/PTJ-1968-02/a.md"
        self.repo.write(path, "hello world\n")
        manifest = [{"path": path, "action": "upload"}]
        ftp = FakeFTP()
        uploaded, deleted, problems = ct.execute(ftp, self.repo.dir, manifest)
        self.assertEqual(uploaded, [path])
        self.assertEqual(deleted, [])
        self.assertEqual(problems, [])
        self.assertEqual(ftp.stored[path], b"hello world\n")

    def test_upload_flags_size_mismatch_as_a_problem(self):
        path = "journalgpt/corpus/articles/PTJ-1968-02/a.md"
        self.repo.write(path, "hello world\n")
        manifest = [{"path": path, "action": "upload"}]

        class TruncatingFTP(FakeFTP):
            def storbinary(self, cmd, fileobj):
                super().storbinary(cmd, fileobj)
                self.sizes[cmd[len("STOR "):]] = 1  # pretend it landed truncated

        ftp = TruncatingFTP()
        uploaded, deleted, problems = ct.execute(ftp, self.repo.dir, manifest)
        self.assertEqual(uploaded, [path])
        self.assertEqual(len(problems), 1)
        self.assertIn("server has 1", problems[0])

    def test_delete_verifies_absence(self):
        path = "journalgpt/corpus/articles/PTJ-1968-02/retired.md"
        manifest = [{"path": path, "action": "delete"}]
        ftp = FakeFTP(sizes={path: 42})
        uploaded, deleted, problems = ct.execute(ftp, self.repo.dir, manifest)
        self.assertEqual(deleted, [path])
        self.assertEqual(problems, [])

    def test_delete_flags_still_present_as_a_problem(self):
        path = "journalgpt/corpus/articles/PTJ-1968-02/retired.md"
        manifest = [{"path": path, "action": "delete"}]

        class StubbornFTP(FakeFTP):
            def delete(self, path):
                self.deleted.append(path)  # "succeeds" but doesn't remove it

        ftp = StubbornFTP(sizes={path: 42})
        uploaded, deleted, problems = ct.execute(ftp, self.repo.dir, manifest)
        self.assertEqual(len(problems), 1)
        self.assertIn("still present", problems[0])

    def test_missing_local_file_is_a_problem_not_a_crash(self):
        path = "journalgpt/corpus/articles/PTJ-1968-02/never-written.md"
        manifest = [{"path": path, "action": "upload"}]
        ftp = FakeFTP()
        uploaded, deleted, problems = ct.execute(ftp, self.repo.dir, manifest)
        self.assertEqual(uploaded, [])
        self.assertEqual(len(problems), 1)
        self.assertIn("missing locally", problems[0])

    def test_scope_violation_raises(self):
        manifest = [{"path": "journalgpt/cli/some_script.py", "action": "upload"}]
        ftp = FakeFTP()
        with self.assertRaises(AssertionError):
            ct.execute(ftp, self.repo.dir, manifest)

    def test_traversal_path_raises(self):
        manifest = [{"path": "journalgpt/corpus/articles/../../../etc/passwd.md",
                     "action": "upload"}]
        ftp = FakeFTP()
        with self.assertRaises(AssertionError):
            ct.execute(ftp, self.repo.dir, manifest)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="corpus_train_ledger_test_")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmpdir, ignore_errors=True))
        self._orig_state_file_path = ct.state_file_path
        fake_path = Path(self.tmpdir) / "corpus_deploy_state.json"
        ct.state_file_path = lambda: fake_path
        self.addCleanup(lambda: setattr(ct, "state_file_path", self._orig_state_file_path))

    def test_write_ledger_records_sha_files_and_reviews(self):
        manifest = [
            {"path": "journalgpt/corpus/articles/PTJ-1968-02/a.md", "action": "upload"},
            {"path": "journalgpt/corpus/articles/PTJ-1968-02/b.md", "action": "skip-identical"},
            {"path": "journalgpt/corpus/articles/PTJ-1968-02/c.md", "action": "delete"},
        ]
        reviews = [{"reviewer": "mechanical", "sha": "abc123", "verdict": "APPROVE"}]
        state = ct.write_ledger("abc123", manifest, reviews)

        self.assertEqual(state["sha"], "abc123")
        self.assertEqual(
            sorted(state["files"]),
            sorted(["journalgpt/corpus/articles/PTJ-1968-02/a.md",
                    "journalgpt/corpus/articles/PTJ-1968-02/c.md"]),
        )
        self.assertNotIn("journalgpt/corpus/articles/PTJ-1968-02/b.md", state["files"])
        self.assertEqual(state["reviewed_by"], reviews)
        self.assertIn("deployed_at", state)

        on_disk = json.loads(ct.state_file_path().read_text())
        self.assertEqual(on_disk["sha"], "abc123")

    def test_resolve_range_uses_recorded_sha_as_base(self):
        ct.write_ledger("base_sha_123", [], [])
        result = ct.resolve_range("HEAD", ct.load_state())
        self.assertEqual(result, "base_sha_123..HEAD")

    def test_resolve_range_passes_through_explicit_range(self):
        result = ct.resolve_range("aaa..bbb", {})
        self.assertEqual(result, "aaa..bbb")

    def test_resolve_range_without_base_or_range_exits(self):
        with self.assertRaises(SystemExit):
            ct.resolve_range("HEAD", {})


class TargetRefTests(unittest.TestCase):
    def test_bare_ref(self):
        self.assertEqual(ct.target_ref("test"), "test")

    def test_range(self):
        self.assertEqual(ct.target_ref("aaa..bbb"), "bbb")


if __name__ == "__main__":
    unittest.main()


class EnsureRemoteDirsTest(unittest.TestCase):
    def test_mkd_every_parent_and_tolerates_existing(self):
        ftp = FakeFTP()
        ct.ensure_remote_dirs(ftp, "journalgpt/corpus/articles/PTJ-2026-09/a.md")
        self.assertEqual(ftp.mkds, ["journalgpt", "journalgpt/corpus", "journalgpt/corpus/articles",
                                    "journalgpt/corpus/articles/PTJ-2026-09"])
        # second file in the same new folder: every MKD now raises, none escape
        ct.ensure_remote_dirs(ftp, "journalgpt/corpus/articles/PTJ-2026-09/b.md")
        self.assertEqual(len(ftp.mkds), 4)
