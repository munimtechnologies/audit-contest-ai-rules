"""Tests for c4_series.py (Apache-2.0).

UnitTest runs on a small made-up file. DataTest pins every Code4rena number in the
README to data/c4_contests.csv; the values were produced by c4_crowding.py in the census
job (summary.json) and the validated-era counts were checked by hand against the file.
"""
import csv
import datetime as dt
import os
import tempfile
import unittest

import c4_series as c4

FIELDS = ["repo", "kind", "era", "start", "submissions", "high_subs", "medium_subs", "hm_subs",
          "unique_high", "unique_medium", "submitters", "est_total_submissions"]


def row(repo, kind, era, start, subs, high, medium, uh="", um="", submitters="", est=""):
    return {"repo": repo, "kind": kind, "era": era, "start": start, "submissions": str(subs),
            "high_subs": str(high), "medium_subs": str(medium), "hm_subs": str(high + medium),
            "unique_high": str(uh), "unique_medium": str(um), "submitters": str(submitters),
            "est_total_submissions": str(est)}


class UnitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "c4.csv")
        with open(self.path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS)
            writer.writeheader()
            for r in [
                row("a", "audit", "full", "2023-02-01", 300, 50, 150, 4, 6, 90, 300),
                row("b", "audit", "full", "2023-05-01", 100, 20, 20, 1, 3, 30, 100),
                row("c", "audit", "full", "2023-06-01", 50, 5, 5, "", "", 10, 50),     # no report counts
                row("m", "mitigation", "full", "2023-03-01", 40, 2, 8, 1, 1, 3, 40),  # left out
                row("z", "audit", "full", "2023-04-01", 0, 0, 0),                      # no submissions
                row("u", "audit", "full", "", 70, 10, 10, 1, 1, 9, 70),                # undated
                row("v", "audit", "validated", "2024-05-01", 30, 10, 15, 2, 3, 20, 120),
            ]:
                writer.writerow(r)

    def tearDown(self):
        self.tmp.cleanup()

    def test_audits_filter(self):
        rows = c4.load(self.path)
        self.assertEqual([r["repo"] for r in c4.audits(rows)], ["a", "b", "c", "v"])
        self.assertEqual([r["repo"] for r in c4.audits(rows, "validated")], ["v"])

    def test_signal_rate(self):
        rows = {r["repo"]: r for r in c4.load(self.path)}
        self.assertAlmostEqual(c4.signal_rate(rows["a"]), 10 / 200)
        self.assertIsNone(c4.signal_rate(rows["c"]))
        self.assertIsNone(c4.signal_rate(rows["v"]))  # validated era: no rate

    def test_table(self):
        cells = {c["period"]: c for c in c4.table(c4.load(self.path))}
        self.assertEqual(list(cells), ["2023H1", "2024H1"])
        h = cells["2023H1"]
        self.assertEqual((h["audits"], h["full"], h["validated"], h["submissions"], h["hm_subs"]),
                         (3, 3, 0, 450, 250))
        self.assertEqual(h["median_hm_subs"], 40)
        self.assertEqual(h["median_submitters"], 30)
        self.assertEqual(h["signal_n"], 2)
        self.assertEqual(h["median_signal_rate"], 0.075)   # median of 0.05 and 0.1
        self.assertEqual(h["pooled_signal_rate"], 0.0583)  # 14 / 240
        v = cells["2024H1"]
        self.assertEqual((v["audits"], v["full"], v["validated"], v["submissions"], v["hm_subs"]), (1, 0, 1, 0, 0))
        self.assertIsNone(v["median_signal_rate"])
        self.assertIsNone(v["pooled_signal_rate"])

    def test_summary(self):
        s = c4.summary(self.path)
        self.assertEqual((s["rows"], s["mitigation_rows"], s["undated_rows"]), (7, 1, 1))
        self.assertEqual((s["full_audits"], s["full_submissions"], s["validated_audits"]), (3, 450, 1))
        self.assertEqual((s["validated_promoted"], s["validated_est_total"]), (30, 120))
        self.assertEqual(s["last_start"], "2024-05-01")
        self.assertEqual(s["year_2023"], {"audits": 3, "submissions": 450, "hm_subs": 250,
                                          "high_subs": 75, "medium_subs": 175})


class DataTest(unittest.TestCase):
    """The README's Code4rena numbers, pinned to data/c4_contests.csv."""

    @classmethod
    def setUpClass(cls):
        cls.s = c4.summary()
        cls.cells = {c["period"]: c for c in cls.s["half_yearly"]}

    def test_totals(self):
        s = self.s
        self.assertEqual((s["rows"], s["mitigation_rows"], s["undated_rows"]), (372, 25, 9))
        self.assertEqual((s["full_audits"], s["full_submissions"], s["full_first_start"]), (306, 92830, "2021-04-02"))
        self.assertEqual((s["validated_audits"], s["validated_first_start"]), (31, "2024-04-30"))
        self.assertEqual((s["validated_promoted"], s["validated_est_total"]), (7037, 12564))
        self.assertEqual(s["last_start"], "2024-11-11")

    def test_half_years(self):
        expected = {
            # period: (audits, full, validated, submissions, hm_subs, median_hm_subs, median_submitters,
            #          median_signal_rate, signal_n, pooled_signal_rate)
            "2021H1": (14, 14, 0, 1573, 510, 29.0, 11.5, 0.412, 13, 0.3842),
            "2021H2": (46, 46, 0, 6761, 1750, 28.0, 15.5, 0.324, 46, 0.3286),
            "2022H1": (70, 70, 0, 13842, 6821, 77.0, 46.0, 0.16, 65, 0.1425),
            "2022H2": (51, 51, 0, 20273, 11557, 189, 134, 0.063, 51, 0.0639),
            "2023H1": (44, 44, 0, 17587, 12142, 173.0, 118.5, 0.044, 42, 0.0544),
            "2023H2": (41, 41, 0, 19600, 14640, 356, 142, 0.03, 38, 0.034),
            "2024H1": (45, 33, 12, 13018, 10885, 207, 88, 0.068, 32, 0.0477),
            "2024H2": (26, 7, 19, 176, 154, 14, 4, 0.412, 5, 0.4082),
        }
        self.assertEqual(sorted(self.cells), sorted(expected))
        for period, want in expected.items():
            c = self.cells[period]
            got = (c["audits"], c["full"], c["validated"], c["submissions"], c["hm_subs"], c["median_hm_subs"],
                   c["median_submitters"], c["median_signal_rate"], c["signal_n"], c["pooled_signal_rate"])
            self.assertEqual(got, want, period)

    def test_half_years_add_up(self):
        cells = self.s["half_yearly"]
        self.assertEqual(sum(c["full"] for c in cells), self.s["full_audits"])
        self.assertEqual(sum(c["validated"] for c in cells), self.s["validated_audits"])
        self.assertEqual(sum(c["submissions"] for c in cells), self.s["full_submissions"])

    def test_2023_against_code4renas_year_review(self):
        # Code4rena's own figures for 2023: 114 projects, 31,512 bug submissions, 3,005 High and
        # 4,003 Medium as judged. Ours are audits that started in 2023, labels as submitted.
        self.assertEqual(self.s["year_2023"], {"audits": 85, "submissions": 37187, "hm_subs": 26782,
                                               "high_subs": 9073, "medium_subs": 17709})


if __name__ == "__main__":
    unittest.main()
