# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working for MV2 of Munim, Inc.
"""Tests for v4lend_rates.py.

The expected values below were written by hand BEFORE the job ran (run 216, 29 Oct 2026):
HAND_TABLE is the day table in README-v4lend-data.md (one decimal), and NEAREST_* is the
hand prediction of the nearest-to-midnight table. A failure means the hand arithmetic or the
prediction was wrong; that is reported as is, not edited away.
"""
import os
import unittest
from datetime import datetime, timezone

import v4lend_rates as v

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "v4lend_findings_count.csv")

# (hours, new findings, per hour) as printed in the README day table.
HAND_TABLE = [
    (24.7, 134, 5.4), (24.9, 139, 5.6), (22.4, 165, 7.4), (23.7, 150, 6.3),
    (27.0, 175, 6.5), (21.0, 108, 5.2), (25.2, 131, 5.2), (22.1, 104, 4.7),
    (23.6, 118, 5.0), (24.0, 201, 8.4), (25.5, 244, 9.6), (22.1, 168, 7.6),
    (26.7, 205, 7.7), (24.1, 341, 14.2),
]

# Predicted anchors (reading nearest 00:00Z) for 15-29 Oct.
NEAREST_ANCHORS = [2, 10, 22, 29, 35, 40, 46, 52, 57, 61, 66, 70, 73, 76, 80]
NEAREST_FIRST_SIX = [(22.8, 128, 5.61), (24.2, 142, 5.87), (25.05, 168, 6.71),
                     (23.7, 150, 6.33), (23.17, 158, 6.82), (24.78, 125, 5.04)]

TOL = 0.06  # one-decimal table values; 20.95 h prints as 21.0


def row(n, at, count, approx="yes", reads=1):
    return {"row": n, "at": v.parse_time(at), "approx": approx, "count": count, "reads": reads}


class TestSeries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = v.load_rows(CSV)

    def test_csv_well_formed(self):
        self.assertEqual(v.check_rows(self.rows), [])
        self.assertGreaterEqual(len(self.rows), 83)

    def test_anchor_values(self):
        by = {r["row"]: r["count"] for r in self.rows}
        self.assertEqual(by[1], 1282)
        self.assertEqual(by[2], 1392)
        self.assertEqual(by[80], 3775)
        self.assertEqual(by[82], 3970)

    def test_hand_table_reproduced(self):
        spans = v.day_table(self.rows, v.HAND_ANCHORS)
        self.assertEqual(len(spans), len(HAND_TABLE))
        for s, (h, n, ph) in zip(spans, HAND_TABLE):
            self.assertAlmostEqual(s["hours"], h, delta=TOL, msg=s)
            self.assertEqual(s["new"], n, msg=s)
            self.assertAlmostEqual(s["per_hour"], ph, delta=TOL, msg=s)
        self.assertEqual(sum(s["new"] for s in spans), 3775 - 1392)

    def test_nearest_anchors_predicted(self):
        near = v.nearest_anchors(self.rows, "2026-10-15", "2026-10-29")
        self.assertEqual([n for _, n in near], NEAREST_ANCHORS)
        differ = [d for (d, n), h in zip(near, v.HAND_ANCHORS) if n != h]
        self.assertEqual(differ, ["2026-10-16", "2026-10-17", "2026-10-20"])

    def test_nearest_table_predicted(self):
        spans = v.day_table(self.rows, NEAREST_ANCHORS)
        for s, (h, n, ph) in zip(spans, NEAREST_FIRST_SIX):
            self.assertAlmostEqual(s["hours"], h, delta=0.02, msg=s)
            self.assertEqual(s["new"], n, msg=s)
            self.assertAlmostEqual(s["per_hour"], ph, delta=0.02, msg=s)
        self.assertEqual(sum(s["new"] for s in spans), 3775 - 1392)
        rates = [s["per_hour"] for s in spans]
        self.assertAlmostEqual(min(rates), 4.71, delta=0.02)
        self.assertAlmostEqual(max(rates), 14.16, delta=0.02)


class TestHelpers(unittest.TestCase):
    def test_check_rows_flags_problems(self):
        rows = [row(1, "2026-10-14T09:55Z", 10), row(3, "2026-10-14T09:50Z", 9, reads=3)]
        problems = v.check_rows(rows)
        self.assertEqual(len(problems), 4)

    def test_nearest_tie_goes_earlier(self):
        rows = [row(1, "2026-10-14T23:30Z", 1), row(2, "2026-10-15T00:30Z", 2)]
        midnight = datetime(2026, 10, 15, tzinfo=timezone.utc)
        self.assertEqual(v.nearest_anchor(rows, midnight), 1)

    def test_span(self):
        s = v.span(row(1, "2026-10-14T00:00Z", 100), row(2, "2026-10-14T04:00Z", 120))
        self.assertEqual((s["hours"], s["new"], s["per_hour"]), (4.0, 20, 5.0))


if __name__ == "__main__":
    unittest.main()
