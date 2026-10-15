"""Tests for hackenproof_payouts.py (Apache-2.0).

UnitTest checks the arithmetic on a tiny CSV. DataTest pins every number quoted in the
README's HackenProof section to data/hackenproof_programs.csv, so the text cannot drift
from the data, and checks the file against the listing's own header counts
(All 102, Contest 19, Dual Defense 83 on 2026-10-15).
"""
import csv
import datetime as dt
import os
import tempfile
import unittest

import hackenproof_payouts as hp

FIELDS = ["name", "kind", "status", "end_date", "up_to_usd", "paid_usd", "listing_page"]


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


class UnitTest(unittest.TestCase):
    def test_block_and_summary(self):
        rows = [
            {"name": "A", "kind": "contest", "status": "finished", "end_date": "2025-03-01",
             "up_to_usd": "10000", "paid_usd": "10000", "listing_page": "1"},
            {"name": "B", "kind": "contest", "status": "finished", "end_date": "2025-06-01",
             "up_to_usd": "20000", "paid_usd": "5000", "listing_page": "1"},
            {"name": "C", "kind": "dualdefense", "status": "finished", "end_date": "2024-12-01",
             "up_to_usd": "30000", "paid_usd": "private", "listing_page": "2"},
            {"name": "D", "kind": "dualdefense", "status": "live", "end_date": "2026-10-26",
             "up_to_usd": "2500", "paid_usd": "0", "listing_page": "1"},
            {"name": "E", "kind": "dualdefense", "status": "finished", "end_date": "2026-01-15",
             "up_to_usd": "4000", "paid_usd": "0", "listing_page": "1"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "p.csv")
            write_csv(path, rows)
            loaded = hp.load(path)
            s = hp.summary(path)
        self.assertEqual([r["paid_ratio"] for r in loaded], [1.0, 0.25, None, 0.0, 0.0])
        self.assertEqual([r["end_year"] for r in loaded], [2025, 2025, 2024, 2026, 2026])

        a = s["all"]
        self.assertEqual((a["programs"], a["live"], a["paid_private"], a["settled"]), (5, 1, 1, 3))
        self.assertEqual((a["up_to_usd_all"], a["up_to_usd_settled"], a["paid_usd"]), (66500, 34000, 15000))
        self.assertAlmostEqual(a["paid_share"], 15000 / 34000, places=4)
        self.assertEqual((a["paid_nothing"], a["paid_full"]), (1, 1))
        self.assertEqual(a["median_up_to_usd"], 10000)
        self.assertEqual(a["median_paid_ratio"], 0.25)

        c = s["by_kind"]["contest"]
        self.assertEqual((c["programs"], c["settled"], c["paid_usd"], c["paid_share"]), (2, 2, 15000, 0.5))
        self.assertEqual(c["median_up_to_usd"], 15000)
        d = s["by_kind"]["dualdefense"]
        self.assertEqual((d["programs"], d["live"], d["paid_private"], d["settled"]), (3, 1, 1, 1))
        self.assertEqual((d["up_to_usd_settled"], d["paid_usd"], d["paid_share"]), (4000, 0, 0.0))
        self.assertEqual(sorted(s["by_kind_and_end_year"]["dualdefense"]), ["2024", "2026"])
        self.assertEqual(s["by_kind_and_end_year"]["dualdefense"]["2024"]["settled"], 0)
        self.assertIsNone(s["by_kind_and_end_year"]["dualdefense"]["2024"]["paid_share"])
        self.assertEqual(s["by_kind_and_end_year"]["contest"]["2025"]["paid_usd"], 15000)
        text = hp.table(s)
        self.assertIn("| contest | 2 | 2 | $30,000 | $15,000 | 50.0% | 0 | 1 | $15,000 |", text)
        self.assertIn("| all | 5 | 3 | $34,000 | $15,000 | 44.1% | 1 | 1 | $10,000 |", text)

    def test_bad_kind_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "p.csv")
            write_csv(path, [{"name": "X", "kind": "bounty", "status": "finished", "end_date": "2025-01-01",
                              "up_to_usd": "1", "paid_usd": "0", "listing_page": "1"}])
            with self.assertRaises(ValueError):
                hp.load(path)


@unittest.skipUnless(os.path.exists(hp.PROGRAMS_CSV), "programs file not present")
class DataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = hp.load()
        cls.s = hp.summary()

    def test_file_matches_listing_header(self):
        self.assertEqual(len(self.rows), 102)                       # "All 102"
        self.assertEqual(sum(r["kind"] == "contest" for r in self.rows), 19)      # "Contest 19"
        self.assertEqual(sum(r["kind"] == "dualdefense" for r in self.rows), 83)  # "Dual Defense 83"
        self.assertEqual(sorted({r["listing_page"] for r in self.rows}), list(range(1, 12)))
        pages = [sum(r["listing_page"] == p for r in self.rows) for p in range(1, 12)]
        self.assertEqual(pages, [10] * 10 + [2])
        for r in self.rows:
            dt.date.fromisoformat(r["end_date"])  # every end date parses
            self.assertGreater(r["up_to_usd"], 0, r["name"])
        self.assertEqual(len({r["name"] for r in self.rows}), 102)  # no duplicate names
        self.assertEqual([r["name"] for r in self.rows if r["status"] == "live"],
                         ["DreamX Marketplace & DEX SCA DualDefense Audit",
                          "Digital Oro International SCA DualDefense Audit",
                          "EverValue SCA DualDefense Audit"])
        self.assertEqual([r["name"] for r in self.rows if r["paid_usd"] is None],
                         ["EverValue Coin DualDefense Audit", "Common Wealth DualDefense Audit"])

    def test_spot_checks_against_program_pages(self):
        # Read off the programs' own pages on 2026-10-15 ("Range of bounty" / "Total rewards").
        by_name = {r["name"]: r for r in self.rows}
        self.assertEqual((by_name["Somnia Audit Contest"]["up_to_usd"], by_name["Somnia Audit Contest"]["paid_usd"]), (300000, 135000))
        self.assertEqual((by_name["Dexalot SC DualDefense Audit"]["up_to_usd"], by_name["Dexalot SC DualDefense Audit"]["paid_usd"]), (80000, 39260))
        self.assertEqual((by_name["Kinetic Audit Contest"]["up_to_usd"], by_name["Kinetic Audit Contest"]["paid_usd"]), (40000, 2000))
        self.assertEqual((by_name["ZIGChain Code DualDefense Audit"]["up_to_usd"], by_name["ZIGChain Code DualDefense Audit"]["paid_usd"]), (75000, 3987))
        self.assertEqual((by_name["Bluefin Perp Audit Contest"]["up_to_usd"], by_name["Bluefin Perp Audit Contest"]["paid_usd"]), (85000, 40500))
        self.assertEqual((by_name["Perceptron Network SC DualDefense Audit"]["up_to_usd"], by_name["Perceptron Network SC DualDefense Audit"]["paid_usd"]), (2000, 0))

    def test_all(self):
        a = self.s["all"]
        self.assertEqual((a["programs"], a["live"], a["paid_private"], a["settled"]), (102, 3, 2, 97))
        self.assertEqual(a["up_to_usd_all"], 2335650)
        self.assertEqual((a["up_to_usd_settled"], a["paid_usd"]), (2265650, 499594))
        self.assertAlmostEqual(a["paid_share"], 499594 / 2265650, places=4)   # 22.1%
        self.assertEqual((a["paid_nothing"], a["paid_full"]), (69, 7))

    def test_contests(self):
        c = self.s["by_kind"]["contest"]
        self.assertEqual((c["programs"], c["live"], c["paid_private"], c["settled"]), (19, 0, 0, 19))
        self.assertEqual((c["up_to_usd_settled"], c["paid_usd"]), (677000, 318949))
        self.assertAlmostEqual(c["paid_share"], 318949 / 677000, places=4)   # 47.1%
        self.assertEqual((c["paid_nothing"], c["paid_full"]), (2, 5))
        self.assertEqual(c["median_up_to_usd"], 14000)
        self.assertEqual(c["median_paid_ratio"], 0.5)
        years = self.s["by_kind_and_end_year"]["contest"]
        self.assertEqual(sorted(years), ["2023", "2024", "2025", "2026"])
        self.assertEqual((years["2023"]["settled"], years["2023"]["paid_usd"]), (1, 0))
        self.assertEqual((years["2024"]["settled"], years["2024"]["up_to_usd_settled"], years["2024"]["paid_usd"]), (1, 45000, 22500))
        self.assertEqual((years["2025"]["settled"], years["2025"]["up_to_usd_settled"], years["2025"]["paid_usd"]), (14, 533000, 251448))
        self.assertAlmostEqual(years["2025"]["paid_share"], 251448 / 533000, places=4)   # 47.2%
        self.assertEqual((years["2025"]["paid_nothing"], years["2025"]["paid_full"]), (0, 3))
        self.assertEqual((years["2026"]["settled"], years["2026"]["up_to_usd_settled"], years["2026"]["paid_usd"]), (3, 59000, 45001))
        self.assertAlmostEqual(years["2026"]["paid_share"], 45001 / 59000, places=4)   # 76.3%
        self.assertEqual((years["2026"]["paid_nothing"], years["2026"]["paid_full"]), (1, 2))

    def test_dualdefense(self):
        d = self.s["by_kind"]["dualdefense"]
        self.assertEqual((d["programs"], d["live"], d["paid_private"], d["settled"]), (83, 3, 2, 78))
        self.assertEqual(d["up_to_usd_all"], 1658650)
        self.assertEqual((d["up_to_usd_settled"], d["paid_usd"]), (1588650, 180645))
        self.assertAlmostEqual(d["paid_share"], 180645 / 1588650, places=4)   # 11.4%
        self.assertEqual((d["paid_nothing"], d["paid_full"]), (67, 2))
        self.assertEqual(d["median_up_to_usd"], 10000)
        self.assertEqual(d["median_paid_ratio"], 0.0)
        years = self.s["by_kind_and_end_year"]["dualdefense"]
        self.assertEqual(sorted(years), ["2024", "2025", "2026"])
        y24, y25, y26 = years["2024"], years["2025"], years["2026"]
        self.assertEqual((y24["programs"], y24["paid_private"], y24["settled"], y24["up_to_usd_settled"], y24["paid_usd"]),
                         (10, 1, 9, 203500, 0))
        self.assertEqual(y24["median_up_to_usd"], 20000)
        self.assertEqual((y24["paid_nothing"], y24["paid_full"]), (9, 0))
        self.assertEqual((y25["programs"], y25["paid_private"], y25["settled"], y25["up_to_usd_settled"], y25["paid_usd"]),
                         (32, 1, 31, 1071800, 168658))
        self.assertAlmostEqual(y25["paid_share"], 168658 / 1071800, places=4)   # 15.7%
        self.assertEqual(y25["median_up_to_usd"], 29000)
        self.assertEqual((y25["paid_nothing"], y25["paid_full"]), (23, 0))
        self.assertEqual((y26["programs"], y26["live"], y26["settled"], y26["up_to_usd_settled"], y26["paid_usd"]),
                         (41, 3, 38, 313350, 11987))
        self.assertAlmostEqual(y26["paid_share"], 11987 / 313350, places=4)   # 3.8%
        self.assertEqual(y26["median_up_to_usd"], 4000)
        self.assertEqual((y26["paid_nothing"], y26["paid_full"]), (35, 2))   # 38 settled; paid: Zendex, Overlayer, ZIGChain


if __name__ == "__main__":
    unittest.main()
