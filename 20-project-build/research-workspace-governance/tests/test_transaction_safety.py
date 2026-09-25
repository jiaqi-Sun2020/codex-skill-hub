from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_engineering_records.py"
SPEC = importlib.util.spec_from_file_location("transaction_record_validator", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class TransactionSafetyTests(unittest.TestCase):
    def test_qwct_241_to_259_regression_and_new_budget(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            parent = Path(raw)
            name_length = 241 - len(str(parent)) - 1
            final = parent / ("o" * name_length)
            legacy = final.with_name(final.name + ".prepare-123456789")
            identity = hashlib.sha256(str(final).encode("utf-8")).hexdigest()
            current = parent / validator.transaction_sibling_name("p", identity, "12345678")
            self.assertEqual(len(str(final)), 241)
            self.assertEqual(len(str(legacy)), 259)
            self.assertLess(len(str(current)), len(str(final)))
            self.assertEqual(current.parent, final.parent)
            self.assertNotIn(final.name, current.name)

    def test_stale_collision_legacy_and_exact_ownership_are_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            parent = Path(raw)
            final = parent / "result"
            identity = "a" * 64
            candidate = parent / validator.transaction_sibling_name("p", identity, "12345678")
            candidate.mkdir()
            current = {"target_identity_sha256": identity, "attempt_id": "attempt-1"}
            collision = {"target_identity_sha256": "a" * 16 + "b" * 48, "attempt_id": "attempt-1"}
            stale = {"target_identity_sha256": identity, "attempt_id": "attempt-0"}
            self.assertEqual(validator.classify_transaction_candidate(candidate, final, identity, "attempt-1", current), "current")
            self.assertEqual(validator.classify_transaction_candidate(candidate, final, identity, "attempt-1", collision), "identity_collision")
            self.assertEqual(validator.classify_transaction_candidate(candidate, final, identity, "attempt-1", stale), "stale")
            self.assertFalse(validator.transaction_cleanup_allowed(candidate, final, identity, "attempt-1", current, set()))
            self.assertTrue(validator.transaction_cleanup_allowed(candidate, final, identity, "attempt-1", current, {candidate}))

            legacy = parent / f"{final.name}.prepare-123456789"
            legacy.mkdir()
            self.assertEqual(validator.classify_transaction_candidate(legacy, final, identity, "attempt-1", None), "legacy")
            self.assertFalse(validator.transaction_cleanup_allowed(legacy, final, identity, "attempt-1", None, {legacy}))

    def test_link_or_junction_candidate_is_never_cleanup_eligible(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            parent = Path(raw)
            final = parent / "result"
            identity = "a" * 64
            candidate = parent / validator.transaction_sibling_name("p", identity, "12345678")
            candidate.mkdir()
            manifest = {"target_identity_sha256": identity, "attempt_id": "attempt-1"}
            with mock.patch.object(validator, "is_link_like", return_value=True):
                self.assertEqual(validator.classify_transaction_candidate(candidate, final, identity, "attempt-1", manifest), "unsafe_type")
                self.assertFalse(validator.transaction_cleanup_allowed(candidate, final, identity, "attempt-1", manifest, {candidate}))

    def test_single_and_campaign_names_share_one_contract(self) -> None:
        identity = "c" * 64
        single = validator.transaction_sibling_name("single", identity, "nonce0001")
        campaign = validator.transaction_sibling_name("campaign", identity, "nonce0001")
        self.assertRegex(single, validator.TRANSACTION_NAME)
        self.assertRegex(campaign, validator.TRANSACTION_NAME)
        self.assertIn(identity[:16], single)
        self.assertIn(identity[:16], campaign)


if __name__ == "__main__":
    unittest.main()
