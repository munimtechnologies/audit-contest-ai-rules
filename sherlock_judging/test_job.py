# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working for MV2 of Munim, Inc.
"""Offline tests for the Sherlock judging-duration job (no network)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import job  # noqa: E402

DAY = 86400


def rec(i, n=300, end=1735732800, j_days=5.0, w=86400, s_days=None, v3=True, private=False,
        status="FINISHED"):
    es = end + int(j_days * DAY)
    r = {"id": i, "title": "t%d" % i, "status": status, "private": private, "is_judging_v3": v3,
         "num_competition_issues": n, "starts_at": end - 20 * DAY, "ends_at": end,
         "escalation_started_at": es, "escalation_ends_at": es + w,
         "judging_stopped_at": None if s_days is None else end + int(s_days * DAY)}
    return r


class DocDays(unittest.TestCase):
    def test_examples_from_docs(self):
        # 500 issues: phase 1 = 5 days, lead judge 500/200 "would round up to 3 days"
        self.assertEqual(job.doc_days(500), 8)

    def test_minimums(self):
        self.assertEqual(job.doc_days(1), 4)
        self.assertEqual(job.doc_days(150), 4)
        self.assertEqual(job.doc_days(200), 4)

    def test_rounding_up(self):
        self.assertEqual(job.doc_days(201), 5)
        self.assertEqual(job.doc_days(250), 5)
        self.assertEqual(job.doc_days(975), 15)


class Measures(unittest.TestCase):
    def test_aave_v4_detail_values(self):
        # values read from the API detail record of contest 1209 before registration
        m = job.measures({"ends_at": 1768230000, "escalation_started_at": 1769103178,
                          "escalation_ends_at": 1769275978, "judging_stopped_at": 1772646718})
        self.assertAlmostEqual(m["J_days"], 873178 / 86400.0)
        self.assertAlmostEqual(m["S_days"], 4416718 / 86400.0)
        self.assertEqual(m["W_s"], 172800)

    def test_missing_fields(self):
        m = job.measures({"ends_at": 100})
        self.assertEqual(m, {"J_days": None, "S_days": None, "W_s": None})

    def test_int_parsing(self):
        self.assertEqual(job._int("123"), 123)
        self.assertEqual(job._int("-5"), -5)
        self.assertEqual(job._int(4.0), 4)
        self.assertIsNone(job._int(True))
        self.assertIsNone(job._int("x"))
        self.assertIsNone(job._int(None))


class Eligibility(unittest.TestCase):
    def test_eligible(self):
        self.assertEqual(job.eligibility(rec(1)), (True, "eligible"))

    def test_reasons(self):
        self.assertEqual(job.eligibility(rec(1, status="RUNNING"))[1], "not_finished")
        self.assertEqual(job.eligibility(rec(1, private=True))[1], "private_or_unknown")
        r = rec(1)
        del r["private"]
        self.assertEqual(job.eligibility(r)[1], "private_or_unknown")
        self.assertEqual(job.eligibility(rec(1, n=0))[1], "no_issue_count")
        self.assertEqual(job.eligibility(rec(1, n=None))[1], "no_issue_count")
        r = rec(1)
        r["escalation_started_at"] = None
        self.assertEqual(job.eligibility(r)[1], "missing_escalation_started_at")


class Spearman(unittest.TestCase):
    def test_perfect(self):
        self.assertAlmostEqual(job.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
        self.assertAlmostEqual(job.spearman([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)

    def test_ties_and_degenerate(self):
        self.assertEqual(job.ranks([5, 1, 5, 2]), [3.5, 1.0, 3.5, 2.0])
        self.assertIsNone(job.spearman([1, 1, 1], [1, 2, 3]))
        self.assertIsNone(job.spearman([1, 2], [1, 2]))


class Grade(unittest.TestCase):
    def rows(self, recs):
        return [job.row_from(r) for r in recs]

    def test_gate(self):
        g = job.grade(self.rows([rec(1000 + i) for i in range(5)]))
        for p in ("P1", "P2", "P3", "P4", "P5"):
            self.assertIsNone(g[p]["held"], p)

    def test_seen_ids_excluded(self):
        recs = [rec(i) for i in sorted(job.SEEN_IDS)] + [rec(1000 + i) for i in range(19)]
        g = job.grade(self.rows(recs))
        self.assertEqual(g["n_eligible"], 19)
        self.assertIsNone(g["P1"]["held"])
        g2 = job.grade(self.rows(recs), exclude=frozenset())
        self.assertEqual(g2["n_eligible"], 29)
        self.assertIsNotNone(g2["P1"]["held"])

    def test_p1_p2_values(self):
        # n=300 -> doc 3+2=5 days; 12 contests at 5.5 d (within +1 d), 8 at 7 d (outside)
        recs = [rec(1000 + i, j_days=5.5) for i in range(12)]
        recs += [rec(2000 + i, j_days=7.0, w=172800) for i in range(8)]
        g = job.grade(self.rows(recs))
        self.assertEqual(g["P1"]["within_doc_plus_1d"], 12)
        self.assertTrue(g["P1"]["held"])
        self.assertEqual(g["P2"]["window_24h"], 12)
        self.assertTrue(g["P2"]["held"])  # 60% < 90%

    def test_p2_fails_when_all_24h(self):
        g = job.grade(self.rows([rec(1000 + i, w=86400 + 30) for i in range(20)]))
        self.assertFalse(g["P2"]["held"])

    def test_p3_p4_p5(self):
        recs = []
        for i in range(12):  # 2024 ends, smaller contests, quicker
            recs.append(rec(1000 + i, n=100 + i, end=1717200000, j_days=4 + i * 0.1, s_days=10 + i))
        for i in range(12):  # 2026 ends, larger, slower
            recs.append(rec(2000 + i, n=900 + i, end=1770000000, j_days=12 + i * 0.1, s_days=40 + i))
        g = job.grade(self.rows(recs))
        self.assertTrue(g["P3"]["held"])
        self.assertTrue(g["P4"]["held"])
        self.assertGreater(g["P4"]["spearman_N_J"], 0.9)
        self.assertEqual(g["P5"]["n_2024"], 12)
        self.assertTrue(g["P5"]["held"])

    def test_v3_only_for_p1(self):
        recs = [rec(1000 + i, v3=False) for i in range(25)]
        g = job.grade(self.rows(recs))
        self.assertIsNone(g["P1"]["held"])
        self.assertIsNotNone(g["P4"]["held"])

    def test_describe_runs(self):
        d = job.describe(self.rows([rec(1000 + i, s_days=9) for i in range(3)] + [rec(5, n=0)]))
        self.assertEqual(d["n_eligible_all"], 3)
        self.assertEqual(d["reasons"]["no_issue_count"], 1)
        self.assertEqual(d["J_le_0"], 0)


if __name__ == "__main__":
    unittest.main()
