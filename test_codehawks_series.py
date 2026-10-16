"""Tests for codehawks_series.py (Apache-2.0).

UnitTest checks the arithmetic and the practice-copy rule on a tiny CSV. DataTest pins every
number quoted in the README's CodeHawks section to data/codehawks_contests.csv, and checks
the file against CodeHawks' own listings (45 audits on /contests, First Flights #1-#59 on
/first-flights, both read 2026-10-16).
"""
import csv
import os
import tempfile
import unittest

import codehawks_series as ch

FIELDS = ["slug", "kind", "access", "start", "prize_amount", "prize_unit", "submissions", "unique_valid"]


def row(slug, kind, access, start, prize, unit, subs, valid):
    return {"slug": slug, "kind": kind, "access": access, "start": start, "prize_amount": prize,
            "prize_unit": unit, "submissions": subs, "unique_valid": valid}


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


class UnitTest(unittest.TestCase):
    def test_half_and_practice_rule(self):
        self.assertEqual(ch.half("2025-06-30"), "2025H1")
        self.assertEqual(ch.half("2025-07-01"), "2025H2")
        self.assertIsNone(ch.half(""))
        self.assertTrue(ch.is_practice_copy("thunder-loan-cm7owpv0f0000fv3uq12azah5"))
        self.assertTrue(ch.is_practice_copy("beatland-festival-clk83mi5b0004jp08axr82nq1"))
        for slug in ("2023-11-Thunder-Loan", "2025-07-beatland-festival", "2024-12-christmas-dinner",
                     "algo-ssstablecoinsss", "2025-10-company-simulator", "openeden"):
            self.assertFalse(ch.is_practice_copy(slug), slug)

    def test_summary(self):
        rows = [
            row("2024-02-a", "audit", "Public", "2024-02-01", "10000.0", "USDC", "100", "5"),
            row("2024-03-b", "audit", "Public", "2024-03-01", "30000.0", "USDC", "100", "3"),
            row("2024-08-c", "audit", "Public", "2024-08-01", "5000.0", "OP", "50", "1"),
            row("2024-09-d", "audit", "Private", "2024-09-01", "50000.0", "USDC", "", ""),
            row("2024-01-e", "first_flight", "", "2024-01-10", "", "", "40", "2"),
            row("x-cm7owpv0f0000fv3uq12azah5", "first_flight", "", "2025-01-01", "", "", "9", ""),
            row("y-clk83mi5b0004jp08axr82nq1", "first_flight", "", "", "", "", "", ""),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "c.csv")
            write_csv(path, rows)
            s = ch.summary(path)
        h1 = s["audits_by_start_half"]["2024H1"]
        self.assertEqual((h1["audits"], h1["public"], h1["submissions"], h1["unique_valid"]), (2, 2, 200, 8))
        self.assertEqual((h1["median_submissions"], h1["pooled_signal_rate"]), (100.0, 0.04))
        self.assertEqual((h1["usdc_audits"], h1["usdc_prize"], h1["usdc_per_submission"],
                          h1["median_usdc_per_submission"]), (2, 40000.0, 200.0, 200.0))
        h2 = s["audits_by_start_half"]["2024H2"]
        self.assertEqual((h2["audits"], h2["public"], h2["submissions"], h2["usdc_audits"]), (2, 1, 50, 0))
        self.assertIsNone(h2["usdc_per_submission"])
        self.assertIsNone(h2["median_usdc_per_submission"])
        a = s["audits"]
        self.assertEqual((a["audits"], a["public"], a["submissions"], a["unique_valid"], a["pooled_signal_rate"]),
                         (4, 3, 250, 9, 0.036))
        self.assertEqual(s["audit_starts"], ["2024-02-01", "2024-03-01", "2024-08-01", "2024-09-01"])
        f = s["flights"]
        self.assertEqual((f["flights"], f["submissions"], f["unique_valid"], f["pooled_signal_rate"]), (1, 40, 2, 0.05))
        self.assertEqual(list(s["flights_by_start_half"]), ["2024H1"])
        self.assertEqual(s["last_flight_start"], "2024-01-10")
        self.assertEqual(s["practice_copies"], {"rows": 2, "submissions": 9, "by_start_year": {"2025": 1, "none": 1}})
        text = ch.tables(s)
        self.assertIn("| 2024H1 | 2 | 2 | 200 | 100 | 0.04 | 2 | $200.00 | $200.00 |", text)
        self.assertIn("| 2024H2 | 2 | 1 | 50 | 50 | 0.02 | 0 | - | - |", text)
        self.assertIn("| all | 1 | 40 | 40 | 0.05 |", text)

    def test_bad_kind_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "c.csv")
            write_csv(path, [row("z", "bounty", "", "2025-01-01", "", "", "", "")])
            with self.assertRaises(ValueError):
                ch.load(path)


@unittest.skipUnless(os.path.exists(ch.CONTESTS_CSV), "census file not present")
class DataTest(unittest.TestCase):
    AUDIT_HALVES = ["2023H2", "2024H1", "2024H2", "2025H1", "2026H2"]
    FLIGHT_HALVES = ["2023H2", "2024H1", "2024H2", "2025H1", "2025H2", "2026H1"]

    @classmethod
    def setUpClass(cls):
        cls.rows = ch.load()
        cls.s = ch.summary()

    def audit_column(self, key):
        return [self.s["audits_by_start_half"][h][key] for h in self.AUDIT_HALVES]

    def flight_column(self, key):
        return [self.s["flights_by_start_half"][h][key] for h in self.FLIGHT_HALVES]

    def test_file_matches_codehawks_listings(self):
        self.assertEqual(len(self.rows), 332)
        self.assertEqual(sum(r["kind"] == "audit" for r in self.rows), 45)          # /contests lists 45
        self.assertEqual(sum(r["kind"] == "first_flight" for r in self.rows), 287)
        practice = [r for r in self.rows if r["practice_copy"]]
        self.assertEqual(len(practice), 228)
        self.assertTrue(all(r["slug"].startswith(("thunder-loan-", "beatland-festival-")) for r in practice))
        self.assertEqual(self.s["flights"]["flights"], 59)                          # First Flights #1-#59
        self.assertEqual(len({r["slug"] for r in self.rows}), 332)

    def test_audits_by_start_half(self):
        self.assertEqual(sorted(self.s["audits_by_start_half"]), self.AUDIT_HALVES)
        self.assertEqual(self.audit_column("audits"), [9, 9, 15, 11, 1])
        self.assertEqual(self.audit_column("public"), [8, 9, 12, 5, 1])
        self.assertEqual(self.audit_column("submissions"), [8072, 2260, 10530, 9895, 971])
        self.assertEqual(self.audit_column("median_submissions"), [905.5, 184, 883, 998, 971])
        self.assertEqual(self.audit_column("unique_valid"), [273, 132, 235, 357, 9])
        self.assertEqual(self.audit_column("pooled_signal_rate"), [0.0338, 0.0584, 0.0223, 0.0361, 0.0093])
        self.assertEqual(self.audit_column("usdc_audits"), [8, 9, 10, 4, 0])
        self.assertEqual(self.audit_column("usdc_prize"), [227500, 523940, 328750, 212280, 0])
        b = self.s["audits_by_start_half"]
        self.assertAlmostEqual(b["2023H2"]["usdc_per_submission"], 227500 / 8072, places=2)   # $28.18
        self.assertAlmostEqual(b["2024H1"]["usdc_per_submission"], 523940 / 2260, places=2)   # $231.83
        self.assertAlmostEqual(b["2024H2"]["usdc_per_submission"], 328750 / 8770, places=2)   # $37.49
        self.assertAlmostEqual(b["2025H1"]["usdc_per_submission"], 212280 / 9466, places=2)   # $22.43
        self.assertIsNone(b["2026H2"]["usdc_per_submission"])                                  # 7.25 ETH only
        self.assertAlmostEqual(b["2023H2"]["median_usdc_per_submission"], 30.91, places=2)     # Sparkn / Escrow
        self.assertAlmostEqual(b["2024H1"]["median_usdc_per_submission"], 155.84, places=2)    # Beanstalk DIB
        self.assertAlmostEqual(b["2024H2"]["median_usdc_per_submission"], 40.07, places=2)     # TempleGold / Flow
        self.assertAlmostEqual(b["2025H1"]["median_usdc_per_submission"], 33.86, places=2)     # DIVA / Gamma

    def test_audits_all_and_the_gap(self):
        a = self.s["audits"]
        self.assertEqual((a["audits"], a["public"], a["submissions"], a["median_submissions"]), (45, 35, 31728, 733))
        self.assertEqual((a["unique_valid"], a["pooled_signal_rate"]), (1006, 0.0317))
        self.assertEqual((a["usdc_audits"], a["usdc_prize"]), (31, 1292470))
        self.assertAlmostEqual(a["usdc_per_submission"], 1292470 / 28568, places=2)            # $45.24
        self.assertAlmostEqual(a["median_usdc_per_submission"], 45.82, places=2)
        # No audit started between 3 Apr 2025 (Starknet Staking Part 2) and 9 Jul 2026 (BattleChain).
        self.assertEqual(self.s["audit_starts"][-2:], ["2025-04-03", "2026-07-09"])

    def test_flights_by_start_half(self):
        self.assertEqual(sorted(self.s["flights_by_start_half"]), self.FLIGHT_HALVES)
        self.assertEqual(self.flight_column("flights"), [6, 12, 13, 11, 13, 4])
        self.assertEqual(self.flight_column("submissions"), [3399, 3138, 3876, 5447, 4721, 1114])
        self.assertEqual(self.flight_column("median_submissions"), [509, 216.5, 291, 525, 285, 265.5])
        self.assertEqual(self.flight_column("unique_valid"), [54, 124, 104, 99, 111, 52])
        self.assertEqual(self.flight_column("pooled_signal_rate"), [0.0159, 0.0395, 0.0268, 0.0182, 0.0235, 0.0467])
        f = self.s["flights"]
        self.assertEqual((f["flights"], f["submissions"], f["median_submissions"], f["unique_valid"],
                          f["pooled_signal_rate"]), (59, 21695, 314, 544, 0.0251))
        self.assertEqual(self.s["last_flight_start"], "2026-04-16")                             # #59 SNARKeling

    def test_practice_copies(self):
        self.assertEqual(self.s["practice_copies"],
                         {"rows": 228, "submissions": 745, "by_start_year": {"2025": 18, "2026": 206, "none": 4}})


if __name__ == "__main__":
    unittest.main()
