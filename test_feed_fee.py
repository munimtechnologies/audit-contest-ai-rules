"""Offline tests for the fee flag in audit_contest_feed.py (no network). Apache-2.0.
Made with AI agents working for MV2 of Munim, Inc."""
import datetime as _dt
import unittest

import audit_contest_feed as f


class FeeFlagTests(unittest.TestCase):
    def test_immunefi_marked_fee(self):
        rows = [r for r in f.SNAPSHOT if r["platform"] == "Immunefi"]
        self.assertEqual(len(rows), 1)
        self.assertIs(rows[0]["fee"], True)   # per-report submission fee since Aug 2026

    def test_only_immunefi_is_fee_gated(self):
        gated = {r["platform"] for r in f.SNAPSHOT if r["fee"]}
        self.assertEqual(gated, {"Immunefi"})

    def test_no_fee_drops_immunefi_only(self):
        feed = f.build_feed(include_live=False, today=_dt.date(2026, 10, 21))
        kept = f.filter_feed(feed, no_fee=True)
        self.assertNotIn("Immunefi", {r["platform"] for r in kept})
        self.assertEqual(len(kept), len(f.SNAPSHOT) - 1)


if __name__ == "__main__":
    unittest.main()
