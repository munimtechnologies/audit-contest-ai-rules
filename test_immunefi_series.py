"""Tests for immunefi_series.py (Apache-2.0).

UnitTest runs on a small made-up file. DataTest pins every Immunefi number in the README
to data/immunefi_contests.csv (checked by hand against the census job's IMMUNEFI.md).
"""
import csv
import os
import tempfile
import unittest

import immunefi_series as im

FIELDS = ["slug", "kind", "start", "end", "start_half", "days", "pool_usd", "token", "lines_of_code",
          "assets_in_scope", "poc_required", "ai_mentions", "ranked_whitehats", "rank_method"]


def row(slug, kind, start, half, pool, ranked, method):
    return {"slug": slug, "kind": kind, "start": start, "end": "", "start_half": half, "days": "",
            "pool_usd": pool, "token": "USDC", "lines_of_code": "", "assets_in_scope": "",
            "poc_required": "True", "ai_mentions": "0", "ranked_whitehats": ranked, "rank_method": method}


class UnitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "im.csv")
        with open(self.path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS)
            writer.writeheader()
            for r in [
                row("a", "audit_comp", "2024-07-01", "2024H2", "100000.0", "10", "bare"),
                row("b", "iop", "2024-08-01", "2024H2", "", "", ""),
                row("c", "attackathon", "2024-09-01", "2024H2", "500000.0", "40", "bare"),
                row("d", "mitigation_audit", "2024-10-01", "2024H2", "20000.0", "4", "bare"),
                row("e", "audit_comp", "2025-08-01", "2025H2", "30000.0", "90", "hash"),
            ]:
                writer.writerow(r)

    def tearDown(self):
        self.tmp.cleanup()

    def test_table(self):
        cells = {c["period"]: c for c in im.table(im.load(self.path))}
        h = cells["2024H2"]
        self.assertEqual((h["competitions"], h["audit_type"], h["pool_usd"], h["audit_type_pool_usd"]),
                         (4, 3, 620000.0, 120000.0))
        self.assertEqual(h["median_audit_type_pool_usd"], 60000.0)  # b has no pool
        self.assertEqual((h["leaderboards_read"], h["median_leaderboard"]), (2, 7.0))  # attackathon left out

    def test_summary(self):
        s = im.summary(self.path)
        self.assertEqual((s["competitions"], s["audit_type"]), (5, 4))
        self.assertEqual(s["rank_methods"], {"bare": 3, "hash": 1, "none": 1})
        self.assertEqual((s["first_hash_start"], s["last_bare_start"]), ("2025-08-01", "2024-10-01"))


class DataTest(unittest.TestCase):
    """The README's Immunefi numbers, pinned to data/immunefi_contests.csv."""

    @classmethod
    def setUpClass(cls):
        cls.s = im.summary()
        cls.cells = {c["period"]: c for c in cls.s["half_yearly"]}

    def test_totals(self):
        s = self.s
        self.assertEqual((s["competitions"], s["audit_type"]), (62, 52))
        self.assertEqual((s["first_start"], s["last_start"]), ("2023-11-20", "2026-08-18"))
        self.assertEqual(s["rank_methods"], {"bare": 39, "hash": 14, "none": 9})
        self.assertEqual((s["first_hash_start"], s["last_bare_start"]), ("2025-07-07", "2025-09-18"))

    def test_half_years(self):
        expected = {
            # period: (competitions, audit_type, pool_usd, audit_type_pool_usd, median_audit_type_pool_usd,
            #          leaderboards_read, median_leaderboard)
            "2023H2": (1, 1, 50000, 50000, 50000, 1, 35),
            "2024H1": (8, 7, 1609000, 609000, 87500, 6, 17.5),
            "2024H2": (22, 20, 4650000, 2900000, 72500, 18, 7.5),
            "2025H1": (13, 11, 1331000, 681000, 30000, 8, 9.5),
            "2025H2": (12, 7, 830000, 270000, 30000, 6, 50.5),
            "2026H1": (3, 3, 1275000, 1275000, 250000, 3, 95),
            "2026H2": (3, 3, 110000, 110000, 20000, 3, 133),
        }
        self.assertEqual(sorted(self.cells), sorted(expected))
        for period, want in expected.items():
            c = self.cells[period]
            got = (c["competitions"], c["audit_type"], c["pool_usd"], c["audit_type_pool_usd"],
                   c["median_audit_type_pool_usd"], c["leaderboards_read"], c["median_leaderboard"])
            self.assertEqual(got, want, period)


if __name__ == "__main__":
    unittest.main()
