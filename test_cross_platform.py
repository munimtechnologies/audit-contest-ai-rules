"""Tests for cross_platform.py (Apache-2.0).

The DataTest class pins every combined number quoted in the README to the census
files in data/, so the README cannot drift from the data.
"""
import csv
import datetime as dt
import os
import tempfile
import unittest

import cross_platform as cp


def write_csv(path, fields, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


class UnitTest(unittest.TestCase):
    def test_periods(self):
        self.assertEqual(cp.quarter(dt.date(2025, 3, 31)), "2025Q1")
        self.assertEqual(cp.quarter(dt.date(2025, 10, 1)), "2025Q4")
        self.assertEqual(cp.half(dt.date(2025, 6, 30)), "2025H1")
        self.assertEqual(cp.half(dt.date(2025, 7, 1)), "2025H2")
        self.assertEqual(cp.first_full("2023Q4"), ("2024H1", "2024"))
        self.assertEqual(cp.first_full("2023Q1"), ("2023H1", "2023"))
        self.assertEqual(cp.first_full("2023Q2"), ("2023H2", "2024"))

    def test_shared_pot_merged_and_combined(self):
        with tempfile.TemporaryDirectory() as tmp:
            sh, ca = os.path.join(tmp, "s.csv"), os.path.join(tmp, "c.csv")
            write_csv(sh, ["start", "num_competition_issues"], [
                {"start": "2025-01-10", "num_competition_issues": "100"},
                {"start": "2025-04-01", "num_competition_issues": "300"},
            ])
            fields = ["company", "start", "end", "pot", "shared_pot", "total_findings"]
            write_csv(ca, fields, [
                {"company": "EF", "start": "2025-02-21", "end": "2025-03-27", "pot": "2000000.0",
                 "shared_pot": "True", "total_findings": "30"},
                {"company": "EF", "start": "2025-02-21", "end": "2025-03-27", "pot": "2000000.0",
                 "shared_pot": "True", "total_findings": "20"},
                {"company": "X", "start": "2025-02-01", "end": "2025-02-08", "pot": "50000.0",
                 "shared_pot": "False", "total_findings": "250"},
            ])
            cantina = cp.load_cantina(ca)
            self.assertEqual([r["submissions"] for r in cantina], [50, 250])
            s = cp.summary(sh, ca)
        self.assertEqual(s["combined_since"], "2025Q1")
        q1 = s["quarterly"][0]
        self.assertEqual((q1["period"], q1["sherlock_contests"], q1["cantina_contests"]), ("2025Q1", 1, 2))
        self.assertEqual((q1["contests"], q1["submissions"], q1["per_contest"]), (3, 400, 133.3))
        self.assertEqual(s["quarterly"][1]["cantina_contests"], 0)
        self.assertEqual(s["yearly"][0]["submissions"], 700)


@unittest.skipUnless(os.path.exists(cp.SHERLOCK_CSV) and os.path.exists(cp.CANTINA_CSV),
                     "census files not present")
class DataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = cp.summary()

    def cell(self, key, period):
        return next(c for c in self.s[key] if c["period"] == period)

    def check(self, key, period, sh, ca):
        cell = self.cell(key, period)
        self.assertEqual((cell["sherlock_contests"], cell["sherlock_submissions"]), sh, period)
        self.assertEqual((cell["cantina_contests"], cell["cantina_submissions"]), ca, period)
        self.assertEqual(cell["contests"], sh[0] + ca[0])
        self.assertEqual(cell["submissions"], sh[1] + ca[1])
        self.assertAlmostEqual(cell["per_contest"], (sh[1] + ca[1]) / (sh[0] + ca[0]), places=1)

    def test_sizes(self):
        self.assertEqual(self.s["sherlock_contests"], 259)
        self.assertEqual(self.s["cantina_contests"], 114)   # 125 rows, 12 shared-pot rows -> 1
        self.assertEqual(self.s["combined_since"], "2023Q4")

    def test_quarterly(self):
        expected = {
            "2023Q4": ((12, 1829), (4, 1841)),
            "2024Q1": ((35, 5315), (9, 4073)),
            "2024Q2": ((24, 4453), (8, 1946)),
            "2024Q3": ((20, 6380), (8, 3916)),
            "2024Q4": ((23, 7081), (18, 7067)),
            "2025Q1": ((12, 5428), (27, 9116)),
            "2025Q2": ((11, 5437), (21, 13095)),
            "2025Q3": ((17, 10636), (12, 6862)),
            "2025Q4": ((7, 5673), (1, 726)),
            "2026Q1": ((4, 4559), (3, 2784)),
            "2026Q2": ((3, 5504), (3, 6767)),
            "2026Q3": ((2, 4507), (0, 0)),
        }
        self.assertEqual([c["period"] for c in self.s["quarterly"]], list(expected))
        for period, (sh, ca) in expected.items():
            self.check("quarterly", period, sh, ca)

    def test_half_yearly(self):
        self.check("half_yearly", "2024H1", (59, 9768), (17, 6019))
        self.check("half_yearly", "2024H2", (43, 13461), (26, 10983))
        self.check("half_yearly", "2025H1", (23, 10865), (48, 22211))
        self.check("half_yearly", "2025H2", (24, 16309), (13, 7588))
        self.check("half_yearly", "2026H1", (7, 10063), (6, 9551))
        h1_2024, h1_2026 = self.cell("half_yearly", "2024H1"), self.cell("half_yearly", "2026H1")
        self.assertEqual((h1_2024["contests"], h1_2024["submissions"]), (76, 15787))
        self.assertEqual((h1_2026["contests"], h1_2026["submissions"]), (13, 19614))
        self.assertEqual(h1_2026["per_contest"], 1508.8)
        self.assertEqual(h1_2024["per_contest"], 207.7)

    def test_yearly(self):
        self.check("yearly", "2024", (102, 23229), (43, 17002))
        self.check("yearly", "2025", (47, 27174), (61, 29799))
        self.check("yearly", "2026", (9, 14570), (6, 9551))
        self.assertEqual([c["period"] for c in self.s["yearly"]], ["2024", "2025", "2026"])


if __name__ == "__main__":
    unittest.main()
