"""Offline tests for fetch_sherlock.trim and sherlock_crowding (Apache-2.0)."""
import csv
import json
import os
import tempfile
import unittest

import fetch_sherlock
import sherlock_crowding as sc

DAY = 86400
T2023 = 1674486000  # 2023-01-23
T2026 = 1776092400  # 2026-04-13


def rec(**kw):
    base = {
        "id": 1, "title": "x", "status": "FINISHED", "type_label": "Public",
        "starts_at": T2023, "ends_at": T2023 + 10 * DAY, "prize_pool": 90000, "rewards": 100000,
        "token": "USDC", "num_competition_issues": 500, "nsloc": 2000, "scope_nsloc_sum": 0,
        "requires_kyc": False, "is_best_efforts": False, "bug_bounty_contest": False,
        "is_legacy_contest": False,
    }
    base.update(kw)
    return base


class TrimTest(unittest.TestCase):
    def test_keeps_facts_drops_handles_and_sums_scope(self):
        detail = {
            "id": 1260, "title": "XRP Ledger", "status": "FINISHED", "num_competition_issues": 2703,
            "lead_judge_handle": "someone", "lead_senior_auditor_handle": "g",
            "description": "long text", "report": "https://example.invalid/report.pdf",
            "scope": [{"total_nsloc": 1200, "files": [{}, {}]}, {"total_nsloc": None, "files": [{}]}],
            "rewards_tiers": [{"id": 9, "severity": "High", "unlock_percentage": 44.8, "min_count": 1}],
        }
        out = fetch_sherlock.trim(detail)
        self.assertEqual(out["num_competition_issues"], 2703)
        self.assertNotIn("lead_judge_handle", out)
        self.assertNotIn("lead_senior_auditor_handle", out)
        self.assertNotIn("description", out)
        self.assertEqual(out["scope_repos"], 2)
        self.assertEqual(out["scope_files"], 3)
        self.assertEqual(out["scope_nsloc_sum"], 1200)
        self.assertTrue(out["has_report"])
        self.assertEqual(out["rewards_tiers"], [{"severity": "High", "unlock_percentage": 44.8, "min_count": 1}])


class EnrichTest(unittest.TestCase):
    def test_rates(self):
        row = sc.enrich(rec())
        self.assertAlmostEqual(row["per_day"], 50.0)
        self.assertAlmostEqual(row["per_1k_usd"], 5.0)   # 500 issues / $100k headline
        self.assertAlmostEqual(row["per_ksloc"], 250.0)  # 500 / 2 kSLOC
        self.assertEqual(row["start"].year, 2023)

    def test_non_stablecoin_pot_has_no_usd_rate(self):
        row = sc.enrich(rec(token="OP"))
        self.assertIsNone(row["pot_usd"])
        self.assertIsNone(row["per_1k_usd"])

    def test_prize_pool_fallback_and_rlusd(self):
        row = sc.enrich(rec(token="RLUSD", rewards=None, prize_pool=50000))
        self.assertEqual(row["pot_usd"], 50000.0)

    def test_nsloc_fallback_to_scope_sum(self):
        self.assertEqual(sc.enrich(rec(nsloc=0, scope_nsloc_sum=4000))["nsloc"], 4000)
        self.assertIsNone(sc.enrich(rec(nsloc=0, scope_nsloc_sum=0))["per_ksloc"])

    def test_excluded_rows(self):
        self.assertIsNone(sc.enrich(rec(status="RUNNING")))
        self.assertIsNone(sc.enrich(rec(num_competition_issues=0)))
        self.assertIsNone(sc.enrich(rec(num_competition_issues=None)))
        self.assertIsNone(sc.enrich(rec(ends_at=T2023)))
        self.assertIsNone(sc.enrich(rec(starts_at=None)))

    def test_short_contest_floor(self):
        row = sc.enrich(rec(ends_at=T2023 + 3600, num_competition_issues=10))
        self.assertAlmostEqual(row["per_day"], 20.0)  # floored at half a day


class SummaryTest(unittest.TestCase):
    def setUp(self):
        self.records = [
            rec(id=1, num_competition_issues=100),                                    # 2023, 10/day
            rec(id=2, num_competition_issues=300),                                    # 2023, 30/day
            rec(id=3, starts_at=T2026, ends_at=T2026 + 7 * DAY, num_competition_issues=1400),   # 200/day
            rec(id=4, starts_at=T2026, ends_at=T2026 + 7 * DAY, num_competition_issues=140,
                requires_kyc=True, type_label="Best Efforts"),                        # 20/day
            rec(id=5, status="RUNNING"),
        ]

    def test_medians_by_year(self):
        s = sc.summary(self.records)
        self.assertEqual(s["records"], 5)
        self.assertEqual(s["finished_with_counts"], 4)
        self.assertEqual(s["issues_total"], 1940)
        self.assertEqual(s["per_day_by_year"][2023], {"n": 2, "median": 20.0})
        self.assertEqual(s["per_day_by_year"][2026], {"n": 2, "median": 110.0})

    def test_kyc_within_year(self):
        k = sc.summary(self.records)["kyc_within_year"]
        self.assertEqual(k[2026]["kyc"], {"n": 1, "median": 20.0})
        self.assertEqual(k[2026]["no_kyc"], {"n": 1, "median": 200.0})
        self.assertEqual(k[2023]["kyc"], {"n": 0, "median": None})

    def test_quarterly_and_type(self):
        s = sc.summary(self.records)
        self.assertEqual([q["quarter"] for q in s["quarterly"]], ["2023Q1", "2026Q2"])
        self.assertEqual(s["quarterly"][1]["issues"], 1540)
        self.assertEqual(s["per_day_by_type"]["Best Efforts"], {"n": 1, "median": 20.0})

    def test_main_writes_csv_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            inp = os.path.join(tmp, "in.jsonl")
            with open(inp, "w", encoding="utf-8") as fh:
                for r in self.records:
                    fh.write(json.dumps(r) + "\n")
            self.assertEqual(sc.main(["--in", inp, "--out-dir", tmp]), 0)
            with open(os.path.join(tmp, "sherlock_contests.csv"), encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            self.assertEqual(len(rows), 4)
            self.assertEqual(rows[0]["per_day"], "10.0")
            with open(os.path.join(tmp, "summary.json"), encoding="utf-8") as fh:
                self.assertEqual(json.load(fh)["finished_with_counts"], 4)


if __name__ == "__main__":
    unittest.main()
