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


class ReviewAnswerRecordTest(unittest.TestCase):
    """Conversion review answers (review_answers.jsonl): allowlist + '@' scrub."""

    ROW = {"id": 3, "record_id": "a1b2c3d4e5f60718", "issue": "PTJ-1986-07", "csv_number": 55600,
           "answer_kind": "custom", "answer_text": "1 7/8", "note": "write to fred@example.org",
           "reviewer_name": "fred@example.org", "answered_at": "2026-11-14 12:00:00", "answer_revision": 2,
           "status": "pending", "applied_commit_sha": None,
           # NOT allowlisted: account identity and anything else a server might add
           "answered_by_user_id": 7, "answered_by_email": "fred@example.org", "account": {"email": "x@y.org"},
           "marked_span": "1 7/8 [under review: fraction, see scan page 16]"}

    def test_negative_control_raw_row_carries_identity(self):
        # The fixture must discriminate: written as-is (the old {"env": env, **r}), identity reaches git.
        raw = qp.json.dumps({"env": "prod", **self.ROW})
        self.assertIn("@", raw)
        self.assertIn("answered_by_user_id", raw)

    def test_only_allowlisted_fields_are_written(self):
        out = qp.review_answer_record("prod", self.ROW)
        self.assertEqual(set(out), {"env", *qp.REVIEW_ANSWER_FIELDS})
        for k in ("answered_by_user_id", "answered_by_email", "account", "marked_span"):
            self.assertNotIn(k, out)

    def test_any_email_shaped_string_is_replaced(self):
        out = qp.review_answer_record("prod", self.ROW)
        self.assertEqual(out["reviewer_name"], "reviewer")
        self.assertEqual(out["note"], qp.EMAIL_WITHHELD)
        self.assertNotIn("@", qp.json.dumps(out))

    def test_clean_values_pass_through_and_input_is_not_mutated(self):
        out = qp.review_answer_record("prod", self.ROW)
        self.assertEqual((out["answer_text"], out["answer_revision"], out["record_id"]), ("1 7/8", 2, "a1b2c3d4e5f60718"))
        self.assertIsNone(out["applied_commit_sha"])
        self.assertEqual(self.ROW["reviewer_name"], "fred@example.org")

    def test_pull_writes_scrubbed_records(self):
        orig = qp.api
        qp.api = lambda url, token, body=None: {"answers": [dict(self.ROW)]}
        try:
            recs, _ = qp.pull_review_answers("prod", "https://x", "t", {})
        finally:
            qp.api = orig
        self.assertEqual(len(recs), 1)
        self.assertNotIn("@", qp.json.dumps(recs))
        self.assertNotIn("answered_by_user_id", recs[0])


if __name__ == "__main__":
    unittest.main()
