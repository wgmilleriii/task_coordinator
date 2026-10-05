#!/usr/bin/env python3
"""T-PTG-1012: tests for corpus_train.py's scope-locked --bundles / --paths.

No network. FakeFTP and TinyGitRepo come from test_corpus_train.py. The
negative controls feed an out-of-scope path straight to build_manifest()/
execute() (the CALL SITES), because a predicate test alone proves only that a
function rejects a string, not that the upload loop cannot reach the path.
"""
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))
import corpus_train as ct  # noqa: E402
from test_corpus_train import FakeFTP, TinyGitRepo  # noqa: E402

B = "journalgpt/corpus/article_html/"
FRESH = '{"generated_at": "2099-01-01T00:00:00+00:00", "paragraphs": ["fixture"]}'
OLD = '{"generated_at": "2000-01-01T00:00:00+00:00"}'
MD = "journalgpt/corpus/articles/PTJ-2022-10/3825.md"


class ScopeReset(unittest.TestCase):
    def setUp(self):
        self._o = (ct.ALLOWED_BUNDLES, ct.ALLOWED_PATHS, ct.ENV, ct.state_file_path)
        ct.ALLOWED_BUNDLES = frozenset()
        ct.ALLOWED_PATHS = frozenset()
        self.tmp = tempfile.mkdtemp(prefix="ct_bundles_")
        fp = Path(self.tmp) / "state.json"
        ct.state_file_path = lambda: fp
        self.addCleanup(self.restore)

    def restore(self):
        ct.ALLOWED_BUNDLES, ct.ALLOWED_PATHS, ct.ENV, ct.state_file_path = self._o
        __import__("shutil").rmtree(self.tmp, ignore_errors=True)


class BundleScopeTests(ScopeReset):
    def test_named_csv_is_in_scope(self):
        self.assertTrue(ct.is_bundle_in_scope(f"{B}78.json", {"78"}))

    def test_unnamed_csv_refused(self):
        self.assertFalse(ct.is_bundle_in_scope(f"{B}79.json", {"78"}))

    def test_refuses_everything_outside_article_html(self):
        for p in (f"{B}78.json.bak", f"{B}sub/78.json", f"{B}../articles/78.json",
                  f"{B}../../../etc/78.json", "/abs/" + B + "78.json",
                  "journalgpt/api/78.json", "journalgpt/corpus/article_html_x/78.json",
                  f"{B}78.md", f"{B}abc.json", f"{B}.json", "deploy.py", MD):
            self.assertFalse(ct.is_bundle_in_scope(p, {"78", "abc", ""}), p)

    def test_bundle_path_rejects_non_numeric_csv(self):
        for bad in ("78/../x", "abc", "", "7 8", "78.json"):
            with self.assertRaises(ValueError, msg=bad):
                ct.bundle_path(bad)
        self.assertEqual(ct.bundle_path("78"), f"{B}78.json")

    def test_is_shippable_defaults_to_md_only(self):
        self.assertTrue(ct.is_shippable(MD))
        self.assertFalse(ct.is_shippable(f"{B}78.json"))  # no --bundles named it

    def test_is_shippable_with_bundles_named(self):
        ct.ALLOWED_BUNDLES = frozenset({"78"})
        self.assertTrue(ct.is_shippable(f"{B}78.json"))
        self.assertFalse(ct.is_shippable(f"{B}215.json"))

    def test_is_shippable_paths_exact_and_scoped(self):
        ct.ALLOWED_PATHS = frozenset({MD, "deploy.py"})  # deploy.py must still fail
        self.assertTrue(ct.is_shippable(MD))
        self.assertFalse(ct.is_shippable("deploy.py"))


class ChangesTests(ScopeReset):
    def setUp(self):
        super().setUp()
        self.repo = TinyGitRepo()
        self.addCleanup(self.repo.cleanup)
        for c in ("78", "215", "9"):
            self.repo.write(f"{B}{c}.json", FRESH)
        self.repo.write(MD, "x")
        self.repo.write("deploy.py", "x")
        self.sha = self.repo.commit("seed")

    def test_bundle_changes_lists_exactly_the_named(self):
        ch = ct.bundle_changes(self.repo.dir, self.sha, ["78", "215"])
        self.assertEqual(ch, [("A", f"{B}78.json"), ("A", f"{B}215.json")])

    def test_bundle_missing_at_ref_refused(self):
        with self.assertRaises(SystemExit):
            ct.bundle_changes(self.repo.dir, self.sha, ["78", "4034"])

    def test_bundle_bad_csv_refused(self):
        with self.assertRaises(SystemExit):
            ct.bundle_changes(self.repo.dir, self.sha, ["78/../../deploy"])

    def test_path_changes_accepts_md_and_bundle_only(self):
        ch = ct.path_changes(self.repo.dir, self.sha, [MD, f"{B}9.json"])
        self.assertEqual(ch, [("P", MD), ("P", f"{B}9.json")])

    def test_path_changes_refuses_outside_scope(self):
        for p in ("deploy.py", f"{B}../x.json", "journalgpt/corpus/articles/a.txt"):
            with self.assertRaises(SystemExit, msg=p):
                ct.path_changes(self.repo.dir, self.sha, [p])

    def test_path_missing_at_ref_refused(self):
        with self.assertRaises(SystemExit):
            ct.path_changes(self.repo.dir, self.sha,
                            ["journalgpt/corpus/articles/PTJ-2022-10/nope.md"])


GOOD_TEXT = "the quick brown fox jumps over the lazy dog while the band plays on and on tonight " * 5
STALE_TEXT = GOOD_TEXT + " haedrich obituary memorial service will be held at the chapel on friday afternoon " * 4


def bundle(text):
    return json.dumps({"generated_at": "2026-01-01T00:00:00+00:00", "paragraphs": [text]})


class StateDirTests(unittest.TestCase):
    def test_worktree_resolves_to_the_root_not_itself(self):
        repo = TinyGitRepo()
        self.addCleanup(repo.cleanup)
        repo.write("a", "x")
        repo.commit("seed")
        wt = Path(tempfile.mkdtemp(prefix="ct_wt_")) / "wt"
        repo._run(f"git worktree add -q -b side {wt}")
        self.addCleanup(lambda: __import__("shutil").rmtree(wt.parent, ignore_errors=True))
        self.assertEqual(ct.resolve_state_dir(str(wt)).resolve(), Path(repo.dir).resolve())
        self.assertEqual(ct.resolve_state_dir(repo.dir).resolve(), Path(repo.dir).resolve())

    def test_unresolvable_root_refuses(self):
        with self.assertRaises(SystemExit):
            ct.resolve_state_dir(tempfile.mkdtemp(prefix="ct_nogit_"))

    def test_override_wins(self):
        ct.STATE_DIR_OVERRIDE = "/tmp/x"
        self.addCleanup(lambda: setattr(ct, "STATE_DIR_OVERRIDE", None))
        self.assertEqual(ct.resolve_state_dir(), Path("/tmp/x"))


class StalenessTests(ScopeReset):
    """R-132-9: a bundle holding text its .md no longer has must not ship."""
    def setUp(self):
        super().setUp()
        self.repo = TinyGitRepo()
        self.addCleanup(self.repo.cleanup)

    def _seed(self, bundle_json, md_text=GOOD_TEXT, md_has_csv=True):
        self.repo.write(f"{B}78.json", bundle_json)
        if md_has_csv:
            self.repo.write("journalgpt/corpus/articles/PTJ-1980-01/a.md",
                            f"---\ncsv_number: 78\n---\n{md_text}")
        return self.repo.commit("seed")

    def test_bundle_with_text_the_md_lacks_is_refused(self):
        sha = self._seed(bundle(STALE_TEXT))
        stale, note = ct.bundle_staleness(self.repo.dir, sha, "78")
        self.assertTrue(stale, note)
        with self.assertRaises(SystemExit):
            ct.bundle_changes(self.repo.dir, sha, ["78"])

    def test_matching_bundle_passes_and_note_states_the_number(self):
        sha = self._seed(bundle(GOOD_TEXT))
        stale, note = ct.bundle_staleness(self.repo.dir, sha, "78")
        self.assertFalse(stale, note)
        self.assertIn("0.0%", note)
        self.assertEqual(ct.bundle_changes(self.repo.dir, sha, ["78"]), [("A", f"{B}78.json")])

    def test_old_generated_at_alone_does_not_refuse(self):
        """The date proxy was discarded: bundles legitimately predate their md's commit."""
        sha = self._seed(bundle(GOOD_TEXT))
        self.assertFalse(ct.bundle_staleness(self.repo.dir, sha, "78")[0])

    def test_unindexed_sibling_text_counts_when_it_carries_the_csv(self):
        self.repo.write(f"{B}78.json", bundle(STALE_TEXT))
        self.repo.write("journalgpt/corpus/articles/PTJ-1980-01/a.md", f"---\ncsv_number: 78\n---\n{GOOD_TEXT}")
        self.repo.write("journalgpt/corpus/articles/PTJ-1980-01/a-unindexed-back-matter.md",
                        f"---\ncsv_number: 78\n---\n{STALE_TEXT}")
        sha = self.repo.commit("seed")
        self.assertFalse(ct.bundle_staleness(self.repo.dir, sha, "78")[0])

    def test_no_md_is_noted_not_refused(self):
        sha = self._seed(bundle(STALE_TEXT), md_has_csv=False)
        stale, note = ct.bundle_staleness(self.repo.dir, sha, "78")
        self.assertFalse(stale)
        self.assertIn("not checkable", note)

    def test_paths_mode_cannot_smuggle_a_stale_bundle(self):
        sha = self._seed(bundle(STALE_TEXT))
        with self.assertRaises(SystemExit):
            ct.path_changes(self.repo.dir, sha, [f"{B}78.json"])

    def test_bundle_without_paragraphs_refused(self):
        sha = self._seed("{}")
        self.assertTrue(ct.bundle_staleness(self.repo.dir, sha, "78")[0])


class CallSiteNegativeControls(ScopeReset):
    """The upload loop itself must refuse a path no flag named."""
    def setUp(self):
        super().setUp()
        self.repo = TinyGitRepo()
        self.addCleanup(self.repo.cleanup)
        self.repo.write(f"{B}78.json", FRESH)
        self.repo.write(f"{B}215.json", FRESH)
        self.sha = self.repo.commit("seed")

    def test_build_manifest_refuses_unnamed_bundle(self):
        ct.ALLOWED_BUNDLES = frozenset({"78"})
        with self.assertRaises(AssertionError):
            ct.build_manifest(self.repo.dir, self.sha, [("A", f"{B}215.json")],
                              FakeFTP(), "/x")

    def test_execute_refuses_unnamed_bundle(self):
        ct.ALLOWED_BUNDLES = frozenset({"78"})
        m = [{"path": f"{B}215.json", "action": "upload"}]
        ftp = FakeFTP()
        with self.assertRaises(AssertionError):
            ct.execute(ftp, self.repo.dir, m)
        self.assertEqual(ftp.stored, {})

    def test_execute_refuses_deploy_py_even_if_a_flag_lists_it(self):
        ct.ALLOWED_PATHS = frozenset({"deploy.py"})
        m = [{"path": "deploy.py", "action": "upload"}]
        with self.assertRaises(AssertionError):
            ct.execute(FakeFTP(), self.repo.dir, m)

    def test_named_bundle_uploads_and_reads_back(self):
        ct.ALLOWED_BUNDLES = frozenset({"78"})
        ftp = FakeFTP()
        m = ct.build_manifest(self.repo.dir, self.sha, [("A", f"{B}78.json")], ftp, "/x")
        self.assertEqual(m[0]["action"], "upload")
        up, de, pr = ct.execute(ftp, self.repo.dir, m)
        self.assertEqual((up, de, pr), ([f"{B}78.json"], [], []))
        self.assertEqual(list(ftp.stored), [f"{B}78.json"])

    def test_paths_mode_ships_only_absent_never_overwrites(self):
        ct.ALLOWED_PATHS = frozenset({f"{B}78.json", f"{B}215.json"})
        ftp = FakeFTP(sizes={"/x/" + f"{B}78.json": 5})  # present on server
        m = ct.build_manifest(self.repo.dir, self.sha,
                              [("P", f"{B}78.json"), ("P", f"{B}215.json")], ftp, "/x")
        self.assertEqual([e["action"] for e in m], ["skip-present", "upload"])


class ShipLedgerTests(ScopeReset):
    def test_ship_ledger_does_not_move_the_md_base_sha(self):
        ct.write_ledger("md_base_sha", [{"path": MD, "action": "upload"}], [])
        m = [{"path": f"{B}78.json", "action": "upload"},
             {"path": f"{B}215.json", "action": "skip-identical"}]
        st = ct.write_ship_ledger("bundle_sha", "bundles", m, [])
        self.assertEqual(st["sha"], "md_base_sha")      # the .md diff base is untouched
        self.assertEqual(st["files"], [MD])
        e = st["ships"][-1]
        self.assertEqual((e["kind"], e["sha"], e["files"]), ("bundles", "bundle_sha", [f"{B}78.json"]))

    def test_ship_ledger_appends(self):
        ct.write_ship_ledger("s1", "bundles", [], [])
        st = ct.write_ship_ledger("s2", "paths", [], [])
        self.assertEqual([e["sha"] for e in st["ships"]], ["s1", "s2"])


class MainDryRunTests(ScopeReset):
    """main() end to end with a fake FTP: dry-run lists exactly the named files."""
    def setUp(self):
        super().setUp()
        self.repo = TinyGitRepo()
        self.addCleanup(self.repo.cleanup)
        for c in ("78", "215", "9"):
            self.repo.write(f"{B}{c}.json", FRESH)
        self.sha = self.repo.commit("seed")
        self.ftp = FakeFTP()
        self._o2 = (ct.connect_ftp, ct.load_env, ct.ftp_credentials, sys.argv)
        ct.connect_ftp = lambda *a: self.ftp
        ct.load_env = lambda: None
        ct.ftp_credentials = lambda: ("h", "u", "p", "/x")
        self.addCleanup(self.restore2)

    def restore2(self):
        ct.connect_ftp, ct.load_env, ct.ftp_credentials, sys.argv = self._o2

    def run_main(self, *argv):
        sys.argv = ["corpus_train.py", *argv]
        out = io.StringIO()
        code = 0
        try:
            with redirect_stdout(out):
                ct.main()
        except SystemExit as e:
            code = e.code
        return code, out.getvalue()

    def test_dry_run_lists_exactly_named_files_and_writes_nothing(self):
        code, out = self.run_main(self.repo.dir, self.sha, "--bundles", "78,215", "--env", "test")
        self.assertIn(f"{B}78.json", out)
        self.assertIn(f"{B}215.json", out)
        self.assertNotIn(f"{B}9.json", out)
        self.assertIn("DRY RUN", out)
        self.assertEqual(self.ftp.stored, {})
        self.assertFalse(ct.state_file_path().exists())

    def test_env_test_selects_test_credentials_and_ledger(self):
        self.run_main(self.repo.dir, self.sha, "--bundles", "78", "--env", "test")
        self.assertEqual(ct.ENV, "test")

    def test_prod_execute_without_reviews_refused_and_uploads_nothing(self):
        code, out = self.run_main(self.repo.dir, self.sha, "--bundles", "78", "--execute")
        self.assertEqual(code, 1)
        self.assertIn("--reviewed-by", out)
        self.assertEqual(self.ftp.stored, {})

    def test_prod_execute_with_two_approvals_refused(self):
        rv = Path(self.tmp) / "r.json"
        rv.write_text(json.dumps([{"reviewer": r, "sha": self.sha, "verdict": "APPROVE"} for r in "ab"]))
        code, out = self.run_main(self.repo.dir, self.sha, "--bundles", "78",
                                  "--execute", "--reviewed-by", str(rv))
        self.assertEqual(code, 1)
        self.assertEqual(self.ftp.stored, {})

    def test_prod_execute_with_three_approvals_on_sha_ships_only_named(self):
        rv = Path(self.tmp) / "r.json"
        sha = ct.run_cmd(f"git rev-parse {self.sha}", cwd=self.repo.dir)
        rv.write_text(json.dumps([{"reviewer": r, "sha": sha, "verdict": "APPROVE"} for r in "abc"]))
        code, out = self.run_main(self.repo.dir, self.sha, "--bundles", "78",
                                  "--execute", "--reviewed-by", str(rv))
        self.assertEqual(code, 0, out)
        self.assertEqual(list(self.ftp.stored), [f"{B}78.json"])

    def test_test_env_execute_needs_no_reviews(self):
        code, out = self.run_main(self.repo.dir, self.sha, "--bundles", "78",
                                  "--env", "test", "--execute")
        self.assertEqual(code, 0, out)
        self.assertEqual(list(self.ftp.stored), [f"{B}78.json"])

    def test_dirty_working_tree_refused(self):
        (Path(self.repo.dir) / f"{B}78.json").write_text('{"edited": true}')
        code, out = self.run_main(self.repo.dir, self.sha, "--bundles", "78", "--env", "test")
        self.assertEqual(code, 1)
        self.assertIn("working tree differs", out)
        self.assertEqual(self.ftp.stored, {})

    def test_second_file_dirty_refused(self):
        """Reviewer's survivor mutation: a first-file-only tree check passes the first test."""
        (Path(self.repo.dir) / f"{B}215.json").write_text('{"edited": true}')
        code, out = self.run_main(self.repo.dir, self.sha, "--bundles", "78,215", "--env", "test")
        self.assertEqual(code, 1)
        self.assertIn("working tree differs", out)
        self.assertIn("215.json", out)
        self.assertEqual(self.ftp.stored, {})

    def test_range_refused_in_bundles_mode(self):
        code, _ = self.run_main(self.repo.dir, "a..b", "--bundles", "78", "--env", "test")
        self.assertNotEqual(code, 0)

    def test_bad_csv_refused_by_main(self):
        code, _ = self.run_main(self.repo.dir, self.sha, "--bundles", "78,../x", "--env", "test")
        self.assertNotEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
