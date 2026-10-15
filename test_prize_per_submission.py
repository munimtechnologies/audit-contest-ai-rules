"""Tests for prize_per_submission.py (Apache-2.0).

The DataTest class pins every number quoted in the README's prize-per-submission
section to the census files in data/, so the README cannot drift from the data.
It does not skip when the files are missing: those numbers must be checked.
"""
import csv
import datetime as dt
import os
import tempfile
import unittest

import prize_per_submission as pps


def write_csv(path, fields, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


SHERLOCK_FIELDS = ["start", "pot_usd", "num_competition_issues"]
CANTINA_FIELDS = ["company", "start", "end", "pot", "currency", "pot_usd", "shared_pot", "total_findings"]


class UnitTest(unittest.TestCase):
    def test_half(self):
        self.assertEqual(pps.half(dt.date(2025, 6, 30)), "2025H1")
        self.assertEqual(pps.half(dt.date(2025, 7, 1)), "2025H2")

    def test_pots_shared_left_out_and_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            sh, ca = os.path.join(tmp, "s.csv"), os.path.join(tmp, "c.csv")
            write_csv(sh, SHERLOCK_FIELDS, [
                {"start": "2023-12-30", "pot_usd": "50000.0", "num_competition_issues": "999"},  # before SINCE
                {"start": "2025-01-10", "pot_usd": "40000.0", "num_competition_issues": "100"},
                {"start": "2025-02-10", "pot_usd": "", "num_competition_issues": "70"},          # OP pot
                {"start": "2025-03-10", "pot_usd": "1000000.0", "num_competition_issues": "300"},
            ])
            write_csv(ca, CANTINA_FIELDS, [
                {"company": "EF", "start": "2025-02-21", "end": "2025-03-27", "pot": "2000000.0",
                 "currency": "USDC", "pot_usd": "", "shared_pot": "True", "total_findings": "30"},
                {"company": "EF", "start": "2025-02-21", "end": "2025-03-27", "pot": "2000000.0",
                 "currency": "USDC", "pot_usd": "", "shared_pot": "True", "total_findings": "20"},
                {"company": "H", "start": "2025-05-06", "end": "2025-05-08", "pot": "",
                 "currency": "USDC", "pot_usd": "", "shared_pot": "False", "total_findings": "4"},
                {"company": "X", "start": "2025-07-01", "end": "2025-07-08", "pot": "50000.0",
                 "currency": "USDC", "pot_usd": "50000.0", "shared_pot": "False", "total_findings": "250"},
            ])
            cantina = pps.load_cantina(ca)
            self.assertEqual([(r["usd"], r["submissions"]) for r in cantina],
                             [(2000000.0, 50), (None, 4), (50000.0, 250)])
            s = pps.summary(sh, ca)
        h1, h2 = s["all_usd_pots"]
        self.assertEqual((h1["period"], h1["contests"], h1["usd"], h1["submissions"]), ("2025H1", 3, 3040000, 450))
        self.assertEqual((h1["left_out"], h1["left_out_submissions"]), (2, 74))
        self.assertAlmostEqual(h1["per_submission"], 6755.56, places=2)
        self.assertEqual((h2["period"], h2["usd"], h2["per_submission"]), ("2025H2", 50000, 200.0))
        capped = s["pots_under_1m"][0]
        self.assertEqual((capped["contests"], capped["usd"], capped["submissions"]), (1, 40000, 100))
        self.assertEqual(capped["per_submission"], 400.0)


class DataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for path in (pps.SHERLOCK_CSV, pps.CANTINA_CSV):
            if not os.path.exists(path):
                raise AssertionError(f"census file missing: {path}")
        cls.s = pps.summary()

    def check(self, key, expected):
        self.assertEqual([c["period"] for c in self.s[key]], list(expected))
        for cell in self.s[key]:
            contests, usd, submissions, per_submission = expected[cell["period"]]
            got = (cell["contests"], cell["usd"], cell["submissions"])
            self.assertEqual(got, (contests, usd, submissions), cell["period"])
            self.assertAlmostEqual(cell["per_submission"], per_submission, places=2, msg=cell["period"])

    def test_all_usd_pots(self):
        self.check("all_usd_pots", {
            "2024H1": (76, 7117565, 15787, 450.85),
            "2024H2": (64, 9922650, 21740, 456.42),
            "2025H1": (67, 10089100, 32025, 315.04),
            "2025H2": (36, 4846000, 22885, 211.75),
            "2026H1": (12, 1563500, 18340, 85.25),
            "2026H2": (2, 200000, 4507, 44.38),
        })

    def test_pots_under_1m(self):
        self.check("pots_under_1m", {
            "2024H1": (74, 4667565, 14088, 331.31),
            "2024H2": (60, 4184150, 19404, 215.63),
            "2025H1": (65, 5589100, 30965, 180.50),
            "2025H2": (35, 2846000, 22519, 126.38),
            "2026H1": (12, 1563500, 18340, 85.25),
            "2026H2": (2, 200000, 4507, 44.38),
        })

    def test_left_out_matches_cross_platform_counts(self):
        # USD-pot contests + left-out contests = the contest and submission totals in cross_platform.py.
        totals = {"2024H1": (76, 15787), "2024H2": (69, 24444), "2025H1": (71, 33076),
                  "2025H2": (37, 23897), "2026H1": (13, 19614), "2026H2": (2, 4507)}
        left_out = {"2024H1": 0, "2024H2": 5, "2025H1": 4, "2025H2": 1, "2026H1": 1, "2026H2": 0}
        for cell in self.s["all_usd_pots"]:
            period = cell["period"]
            self.assertEqual(cell["left_out"], left_out[period], period)
            self.assertEqual((cell["contests"] + cell["left_out"], cell["submissions"] + cell["left_out_submissions"]),
                             totals[period], period)


if __name__ == "__main__":
    unittest.main()
