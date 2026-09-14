#!/usr/bin/env python3
"""Unit tests for bin/stage1_queue_pull.py's account-identity guards (T-PTG-684).

No network, no git, no state file: only the pure helpers are exercised.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))
import stage1_queue_pull as qp  # noqa: E402


class StripAccountFieldsTest(unittest.TestCase):
    def test_account_name_fields_are_dropped(self):
        rec = {"env": "prod", "id": 7, "reviewer_name": "Chip",
               "reviewed_by_account": "Account Name", "submitted_by": "Account Name",
               "reviewed_by": "Approver Name"}
        out = qp.strip_account_fields(rec)
        self.assertEqual(out, {"env": "prod", "id": 7, "reviewer_name": "Chip"})

    def test_email_shaped_decided_by_becomes_reviewer(self):
        out = qp.strip_account_fields({"id": 1, "decided_by": "someone@example.org"})
        self.assertEqual(out["decided_by"], "reviewer")

    def test_typed_and_null_decided_by_pass_through(self):
        self.assertEqual(qp.strip_account_fields({"decided_by": "Chip (relayed)"})["decided_by"], "Chip (relayed)")
        self.assertIsNone(qp.strip_account_fields({"decided_by": None})["decided_by"])

    def test_input_record_is_not_mutated(self):
        rec = {"submitted_by": "Account Name"}
        qp.strip_account_fields(rec)
        self.assertIn("submitted_by", rec)


class BatchCommitReviewerTest(unittest.TestCase):
    def test_typed_reviewer_name_is_used(self):
        self.assertEqual(qp.batch_commit_reviewer({"reviewer_name": "Mostyn", "submitted_by": "Account Name"}), "Mostyn")

    def test_null_reviewer_name_never_falls_back_to_submitted_by(self):
        for name in (None, "", "   "):
            who = qp.batch_commit_reviewer({"reviewer_name": name, "submitted_by": "Account Name"})
            self.assertEqual(who, "reviewer")

    def test_email_shaped_reviewer_name_is_not_used(self):
        self.assertEqual(qp.batch_commit_reviewer({"reviewer_name": "a@b.org"}), "reviewer")


if __name__ == "__main__":
    unittest.main()
