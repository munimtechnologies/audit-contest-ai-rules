"""Tests for hackenproof_trends.py (Apache-2.0).

UnitTest checks the arithmetic and the AI-rule matching on a tiny CSV. DataTest pins every
number quoted in the README's HackenProof trends section to
data/hackenproof_programs_fetched.csv, and checks that the fetched file agrees with the
hand-read data/hackenproof_programs.csv on every program's maximum and paid figure.
"""
import csv
import os
import re
import tempfile
import unittest

import hackenproof_payouts as hp
import hackenproof_trends as ht

FIELDS = ["slug", "name", "kind", "status", "start_date", "end_date", "bounty_min_usd", "up_to_usd",
          "paid_usd", "submissions", "hackers", "listing_page", "ai_rule", "missing"]
POC = "AI-generated reports without runable PoC are not accepted under this program."
HUMAN = "Automated submissions or AI-generated reports must include human validation."


def prog(slug, kind, status, start, up_to, paid, subs, ai=""):
    return {"slug": slug, "name": slug.upper(), "kind": kind, "status": status, "start_date": start,
            "end_date": start, "bounty_min_usd": "0", "up_to_usd": up_to, "paid_usd": paid,
            "submissions": subs, "hackers": "", "listing_page": "1", "ai_rule": ai, "missing": ""}


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


class UnitTest(unittest.TestCase):
    def test_half_and_rule_kind(self):
        self.assertEqual(ht.half("2025-06-30"), "2025H1")
        self.assertEqual(ht.half("2025-07-01"), "2025H2")
        self.assertEqual(ht.rule_kind(POC), "poc")
        self.assertEqual(ht.rule_kind("Provide steps " + HUMAN), "human_validation")
        self.assertEqual(ht.rule_kind("We combine AI-generated media and blockchain."), "")
        self.assertEqual(ht.rule_kind("AI-generated media. | " + POC), "poc")

    def test_block_and_summary(self):
        rows = [
            prog("a", "contest", "finished", "2025-03-01", "10000", "5000", "100"),
            prog("b", "dualdefense", "finished", "2025-08-20", "4000", "0", "50", POC),
            prog("c", "dualdefense", "finished", "2025-12-31", "20000", "private", "10"),
            prog("d", "contest", "live", "2026-10-01", "14000", "0", "30", HUMAN),
            prog("e", "dualdefense", "finished", "2026-01-05", "2000", "0", "0", "An AI-generated media project"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "p.csv")
            write_csv(path, rows)
            loaded = ht.load(path)
            s = ht.summary(path)
        self.assertEqual([r["start_half"] for r in loaded], ["2025H1", "2025H2", "2025H2", "2026H2", "2026H1"])
        self.assertEqual([r["ai_rule"] for r in loaded], ["", "poc", "", "human_validation", ""])
        self.assertIsNone(loaded[2]["paid_usd"])
        self.assertEqual(sorted(s["by_start_half"]), ["2025H1", "2025H2", "2026H1", "2026H2"])

        h1 = s["by_start_half"]["2025H1"]
        self.assertEqual((h1["programs"], h1["contests"], h1["with_ai_rule"], h1["submissions"]), (1, 1, 0, 100))
        self.assertEqual((h1["max_per_submission"], h1["paid_per_submission"]), (100.0, 50.0))
        h2 = s["by_start_half"]["2025H2"]
        self.assertEqual((h2["programs"], h2["with_ai_rule"], h2["submissions"], h2["settled"],
                          h2["settled_submissions"]), (2, 1, 60, 1, 50))
        self.assertEqual((h2["up_to_usd_settled"], h2["paid_usd"]), (4000, 0))
        self.assertEqual((h2["max_per_submission"], h2["paid_per_submission"]), (80.0, 0.0))
        e = s["by_start_half"]["2026H1"]
        self.assertEqual((e["settled"], e["settled_submissions"]), (1, 0))
        self.assertIsNone(e["max_per_submission"])
        d = s["by_start_half"]["2026H2"]
        self.assertEqual((d["programs"], d["settled"], d["up_to_usd_settled"]), (1, 0, 0))
        self.assertIsNone(d["paid_per_submission"])

        a = s["all"]
        self.assertEqual((a["programs"], a["contests"], a["with_ai_rule"], a["submissions"]), (5, 2, 2, 190))
        self.assertEqual((a["settled"], a["settled_submissions"], a["up_to_usd_settled"], a["paid_usd"]),
                         (3, 150, 16000, 5000))
        self.assertEqual((a["max_per_submission"], a["paid_per_submission"]), (106.67, 33.33))
        self.assertEqual(s["ai_rules"], {"poc": 1, "human_validation": 1})
        self.assertEqual(s["first_ai_rule"], {"name": "B", "start_date": "2025-08-20"})

        text = ht.table(s)
        self.assertIn("| 2025H1 | 1 | 0 | 100 | 1 | $10,000 | $5,000 | $100.00 | $50.00 |", text)
        self.assertIn("| 2026H2 | 1 | 1 | 30 | 0 | $0 | $0 | - | - |", text)
        self.assertIn("| all | 5 | 2 | 190 | 3 | $16,000 | $5,000 | $106.67 | $33.33 |", text)

    def test_bad_status_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "p.csv")
            write_csv(path, [prog("x", "contest", "upcoming", "2025-01-01", "1", "0", "0")])
            with self.assertRaises(ValueError):
                ht.load(path)


@unittest.skipUnless(os.path.exists(ht.FETCHED_CSV), "fetched programs file not present")
class DataTest(unittest.TestCase):
    HALVES = ["2023H2", "2024H1", "2024H2", "2025H1", "2025H2", "2026H1", "2026H2"]

    @classmethod
    def setUpClass(cls):
        cls.rows = ht.load()
        cls.s = ht.summary()

    def column(self, key):
        return [self.s["by_start_half"][h][key] for h in self.HALVES]

    def test_file_matches_listing_header(self):
        self.assertEqual(len(self.rows), 102)                                     # "All 102"
        self.assertEqual(sum(r["kind"] == "contest" for r in self.rows), 19)      # "Contest 19"
        self.assertEqual(sum(r["kind"] == "dualdefense" for r in self.rows), 83)  # "Dual Defense 83"
        self.assertEqual(len({r["slug"] for r in self.rows}), 102)

    def test_matches_hand_read_file(self):
        if not os.path.exists(hp.PROGRAMS_CSV):
            self.skipTest("hand-read file not present")
        def key(name):  # the fetch compared names the same way (case, spaces, punctuation ignored)
            return re.sub(r"[^a-z0-9]", "", name.lower())

        hand = {key(r["name"]): r for r in hp.load()}
        fetched = {key(r["name"]): r for r in self.rows}
        self.assertEqual(set(hand), set(fetched))
        for name, h in hand.items():
            self.assertEqual((fetched[name]["up_to_usd"], fetched[name]["paid_usd"]),
                             (h["up_to_usd"], h["paid_usd"]), name)

    def test_by_start_half(self):
        self.assertEqual(sorted(self.s["by_start_half"]), self.HALVES)
        self.assertEqual(self.column("programs"), [1, 1, 12, 20, 25, 19, 24])
        self.assertEqual(self.column("contests"), [1, 1, 0, 4, 10, 2, 1])
        self.assertEqual(self.column("with_ai_rule"), [0, 0, 0, 0, 19, 19, 24])
        self.assertEqual(self.column("submissions"), [8, 34, 54, 940, 3403, 3588, 2485])
        self.assertEqual(self.column("settled"), [1, 1, 11, 19, 25, 19, 21])
        self.assertEqual(self.column("settled_submissions"), [8, 34, 38, 931, 3403, 3588, 2362])
        self.assertEqual(self.column("up_to_usd_settled"), [40000, 45000, 333500, 685800, 864000, 142150, 155200])
        self.assertEqual(self.column("paid_usd"), [0, 22500, 0, 135162, 288931, 51001, 2000])
        b = self.s["by_start_half"]
        self.assertAlmostEqual(b["2025H1"]["paid_per_submission"], 135162 / 931, places=2)   # $145.18
        self.assertAlmostEqual(b["2025H2"]["paid_per_submission"], 288931 / 3403, places=2)  # $84.90
        self.assertAlmostEqual(b["2026H1"]["paid_per_submission"], 51001 / 3588, places=2)   # $14.21
        self.assertAlmostEqual(b["2026H2"]["paid_per_submission"], 2000 / 2362, places=2)    # $0.85
        self.assertAlmostEqual(b["2025H1"]["max_per_submission"], 685800 / 931, places=2)    # $736.63
        self.assertAlmostEqual(b["2025H2"]["max_per_submission"], 864000 / 3403, places=2)   # $253.89
        self.assertAlmostEqual(b["2026H1"]["max_per_submission"], 142150 / 3588, places=2)   # $39.62
        self.assertAlmostEqual(b["2026H2"]["max_per_submission"], 155200 / 2362, places=2)   # $65.71

    def test_all_and_ai_rules(self):
        a = self.s["all"]
        self.assertEqual((a["programs"], a["with_ai_rule"], a["submissions"]), (102, 62, 10512))
        self.assertEqual((a["settled"], a["settled_submissions"], a["up_to_usd_settled"], a["paid_usd"]),
                         (97, 10364, 2265650, 499594))
        self.assertEqual(self.s["ai_rules"], {"poc": 52, "human_validation": 10})
        self.assertEqual(self.s["first_ai_rule"],
                         {"name": "OpenEden Smart Contract Audit Contest", "start_date": "2025-07-16"})
        since = [r for r in self.rows if r["start_date"] >= "2025-08-14"]
        before = [r for r in self.rows if r["start_date"] < "2025-08-14"]
        self.assertEqual((len(since), sum(1 for r in since if r["ai_rule"])), (62, 61))
        self.assertEqual((len(before), sum(1 for r in before if r["ai_rule"])), (40, 1))
        self.assertEqual([r["name"] for r in since if not r["ai_rule"]],
                         ["VeChain Stargate SC DualDefense Audit (RND 2)"])
        # Contests carry the human-validation rule; DualDefense audits the PoC rule.
        self.assertEqual(sum(1 for r in self.rows if r["ai_rule"] == "human_validation" and r["kind"] == "contest"), 10)
        self.assertEqual(sum(1 for r in self.rows if r["ai_rule"] == "poc" and r["kind"] == "dualdefense"), 51)


if __name__ == "__main__":
    unittest.main()
