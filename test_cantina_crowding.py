"""Offline tests for fetch_cantina.trim and cantina_crowding (Apache-2.0)."""
import csv
import datetime as dt
import json
import os
import tempfile
import unittest

import cantina_crowding as cc
import fetch_cantina

FETCHED = "2026-10-14T15:50Z"
S2025, E2025 = "2025-03-01T20:00:00Z", "2025-03-11T20:00:00Z"   # 10 days
S2026, E2026 = "2026-04-13T00:00:00Z", "2026-04-20T00:00:00Z"   # 7 days


def rec(**kw):
    base = {
        "id": "a", "name": "x", "url": "https://cantina.xyz/competitions/a", "company": "Co",
        "kind": "public_contest", "status": "complete", "start": S2025, "end": E2025,
        "currency": "USDC", "pot": 100000.0, "kyc_required": False, "total_findings": 500,
        "fetched_on": FETCHED,
    }
    base.update(kw)
    return base


def enrich(r, shared=frozenset()):
    return cc.enrich(r, cc.parse_time(FETCHED), set(shared))


class FetchTest(unittest.TestCase):
    def test_trim_public_keeps_facts_drops_text_and_handles(self):
        item = {
            "id": "e275", "name": "Revert v4lend Competition", "url": "https://cantina.xyz/competitions/e275",
            "company": {"id": "c1", "name": "Revert Finance", "handle": "revert", "twitter": "t"},
            "timeframe": {"start": "2026-10-06T18:30:00Z", "end": "2026-11-03T18:30:00Z"},
            "status": "live", "currencyCode": "USDC", "totalRewardPot": "50000",
            "instructions": "long markdown", "kycRequired": True, "totalFindings": 1339,
            "createdAt": "2026-09-21T09:21:19Z", "kind": "public_contest", "joined": False,
            "allowedSeverities": ["high", "medium"], "cantinaTriaged": True,
        }
        out = fetch_cantina.trim(item)
        self.assertEqual(out["company"], "Revert Finance")
        self.assertEqual(out["pot"], 50000.0)
        self.assertEqual(out["total_findings"], 1339)
        self.assertEqual(out["start"], "2026-10-06T18:30:00Z")
        self.assertTrue(out["kyc_required"])
        for dropped in ("instructions", "joined", "handle", "twitter"):
            self.assertNotIn(dropped, out)
        self.assertNotIn("revert", json.dumps(out).replace("Revert", ""))

    def test_trim_private_hides_identity(self):
        out = fetch_cantina.trim({"id": "p1", "name": None, "url": "https://cantina.xyz/x",
                                  "company": {"name": "Secret Co"}, "kind": "private_contest",
                                  "totalRewardPot": None, "totalFindings": 8})
        self.assertIsNone(out["name"])
        self.assertIsNone(out["url"])
        self.assertIsNone(out["company"])
        self.assertIsNone(out["pot"])
        self.assertIsNone(out["start"])

    def test_records_from_list_or_wrapped(self):
        self.assertEqual(len(fetch_cantina.records_from([{"id": 1}, {"id": 2}, "junk"])), 2)
        self.assertEqual(len(fetch_cantina.records_from({"items": [{"id": 1}]})), 1)
        self.assertEqual(fetch_cantina.records_from(None), [])


class ParseTest(unittest.TestCase):
    def test_parse_time(self):
        self.assertEqual(cc.parse_time("2026-10-06T18:30:00Z"),
                         dt.datetime(2026, 10, 6, 18, 30, tzinfo=dt.timezone.utc))
        self.assertIsNotNone(cc.parse_time("2025-03-19T10:00:00.000Z"))
        self.assertIsNotNone(cc.parse_time(FETCHED))
        self.assertIsNone(cc.parse_time("not a date"))
        self.assertIsNone(cc.parse_time(None))


class EnrichTest(unittest.TestCase):
    def test_rates(self):
        row = enrich(rec())
        self.assertAlmostEqual(row["per_day"], 50.0)
        self.assertAlmostEqual(row["per_1k_usd"], 5.0)   # 500 findings / $100k
        self.assertEqual(row["start"].year, 2025)

    def test_non_stablecoin_pot_has_no_usd_rate(self):
        row = enrich(rec(currency="OP"))
        self.assertIsNone(row["pot_usd"])
        self.assertIsNone(row["per_1k_usd"])

    def test_excluded_rows(self):
        self.assertIsNone(enrich(rec(end="2026-11-03T18:30:00Z")))   # still running at fetch time
        self.assertIsNone(enrich(rec(total_findings=0)))
        self.assertIsNone(enrich(rec(total_findings=None)))
        self.assertIsNone(enrich(rec(total_findings=True)))
        self.assertIsNone(enrich(rec(start=None)))
        self.assertIsNone(enrich(rec(end=S2025)))

    def test_short_contest_floor(self):
        row = enrich(rec(end="2025-03-01T21:00:00Z", total_findings=10))
        self.assertAlmostEqual(row["per_day"], 20.0)  # floored at half a day

    def test_shared_pot_excluded_from_per_dollar(self):
        records = [rec(id="c1"), rec(id="c2"), rec(id="c3", pot=5000.0)]
        shared = cc.shared_pot_ids(records)
        self.assertEqual(shared, {"c1", "c2"})
        self.assertIsNone(enrich(records[0], shared)["per_1k_usd"])
        self.assertTrue(enrich(records[0], shared)["shared_pot"])
        self.assertAlmostEqual(enrich(records[2], shared)["per_1k_usd"], 100.0)


class SummaryTest(unittest.TestCase):
    def setUp(self):
        self.records = [
            rec(id="1", total_findings=100),                                   # 2025, 10/day, $100k
            rec(id="2", total_findings=300, pot=20000.0),                      # 2025, 30/day, small
            rec(id="3", start=S2026, end=E2026, total_findings=1400, pot=50000.0),   # 200/day, small
            rec(id="4", start=S2026, end=E2026, total_findings=140, pot=30000.0,
                kyc_required=True),                                            # 20/day, small, KYC
            rec(id="5", kind="private_contest", name=None, url=None, company=None,
                total_findings=50),                                            # private, 5/day
            rec(id="6", status="live", start="2026-10-06T18:30:00Z",
                end="2026-11-03T18:30:00Z", total_findings=1339),              # still running
        ]

    def test_counts_and_medians_by_year(self):
        s = cc.summary(self.records)
        self.assertEqual(s["records"], 6)
        self.assertEqual(s["records_public"], 5)
        self.assertEqual(s["ended_public_with_counts"], 4)
        self.assertEqual(s["findings_total_public"], 1940)
        self.assertEqual(s["first_start"], "2025-03-01")
        self.assertEqual(s["last_start"], "2026-04-13")
        self.assertEqual(s["per_day_by_year"][2025], {"n": 2, "median": 20.0})
        self.assertEqual(s["per_day_by_year"][2026], {"n": 2, "median": 110.0})
        self.assertEqual(s["per_day_by_year_small_pots"][2025], {"n": 1, "median": 30.0})
        self.assertEqual(s["per_day_by_year_small_pots"][2026], {"n": 2, "median": 110.0})
        self.assertEqual(s["status_counts"], {"complete": 5, "live": 1})

    def test_kyc_kind_quarterly(self):
        s = cc.summary(self.records)
        self.assertEqual(s["kyc_within_year"][2026]["kyc"], {"n": 1, "median": 20.0})
        self.assertEqual(s["kyc_within_year"][2026]["no_kyc"], {"n": 1, "median": 200.0})
        self.assertEqual(s["per_day_by_kind_incl_private"]["private_contest"],
                         {"n": 1, "median": 5.0, "findings": 50})
        self.assertEqual(s["per_day_by_kind_incl_private"]["public_contest"],
                         {"n": 4, "median": 25.0, "findings": 1940})
        self.assertEqual([q["quarter"] for q in s["quarterly"]], ["2025Q1", "2026Q2"])
        self.assertEqual(s["quarterly"][1]["findings"], 1540)

    def test_sample_check(self):
        records = [rec(id="e2cf", total_findings=451), rec(id="e275", status="live", total_findings=1339)]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sample.csv")
            with open(path, "w", encoding="utf-8", newline="") as fh:
                writer = csv.writer(fh)
                writer.writerow(["name", "url", "findings_submitted", "status"])
                writer.writerow(["uniswap-v4", "https://cantina.xyz/competitions/e2cf", "451", "completed"])
                writer.writerow(["Revert v4lend", "https://cantina.xyz/competitions/e275", "1282", "live"])
            out = cc.sample_check(records, path)
        self.assertEqual(out["rows"], 2)
        self.assertEqual(out["found_in_api"], 2)
        self.assertEqual(out["ended_rows"], 1)
        self.assertEqual(out["ended_exact_matches"], 1)
        self.assertEqual([m["id"] for m in out["mismatches"]], ["e275"])

    def test_main_writes_public_outputs_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            inp = os.path.join(tmp, "in.jsonl")
            with open(inp, "w", encoding="utf-8") as fh:
                for r in self.records:
                    fh.write(json.dumps(r) + "\n")
            self.assertEqual(cc.main(["--in", inp, "--out-dir", tmp]), 0)
            with open(os.path.join(tmp, "cantina_contests.csv"), encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            self.assertEqual(len(rows), 4)
            self.assertEqual(rows[0]["per_day"], "10.0")
            self.assertNotIn("private_contest", {r["kind"] for r in rows})
            with open(os.path.join(tmp, "cantina_contests.jsonl"), encoding="utf-8") as fh:
                self.assertEqual(sum(1 for line in fh if line.strip()), 5)
            with open(os.path.join(tmp, "summary.json"), encoding="utf-8") as fh:
                self.assertEqual(json.load(fh)["ended_public_with_counts"], 4)


if __name__ == "__main__":
    unittest.main()
