# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working for MV2 of Munim, Inc.
"""Extra tests for the v4lend-rates-v2 job: the late-October / November day rows.

PRE-REGISTERED in run 234 (2 Nov 2026, ~05:10Z), when the CSV had rows 1-96 and BEFORE the v2 job
or any later reading existed. The expected values are hand arithmetic from README-v4lend-data.md
(run 234). They cover only days whose nearest-to-midnight reading is already fixed: every reading
after row 96 is later than 2 Nov 05:08Z, so it cannot be nearer to any midnight up to 2 Nov 00:00Z.
A failure means the hand arithmetic was wrong; report it as is, never edit these numbers to pass.
This file is a draft: on build day copy it, unchanged, next to v4lend_rates.py and
test_v4lend_rates.py (v1, also unchanged) in compete/v4lend-rates-v2/.
"""
import os
import unittest

import v4lend_rates as v

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "v4lend_findings_count.csv")

# Reading nearest 00:00Z on 29 Oct .. 2 Nov (rows 80, 84, 90, 93, 96).
LATE_ANCHORS = [80, 84, 90, 93, 96]
# (hours, new findings, per hour) for 80->84, 84->90, 90->93 (31 Oct, short: missed slot),
# 93->96 (1 Nov, long: missed slot).
LATE_SPANS = [(22.70, 315, 13.88), (24.38, 320, 13.12), (16.83, 322, 19.13), (35.72, 570, 15.96)]


class TestLateRows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = v.load_rows(CSV)

    def test_rows_present(self):
        self.assertEqual(v.check_rows(self.rows), [])
        self.assertGreaterEqual(len(self.rows), 96)
        by = {r["row"]: r["count"] for r in self.rows}
        self.assertEqual((by[90], by[93], by[94], by[95], by[96]), (4410, 4732, 5038, 5124, 5302))

    def test_late_anchors_predicted(self):
        near = v.nearest_anchors(self.rows, "2026-10-29", "2026-11-02")
        self.assertEqual([n for _, n in near], LATE_ANCHORS)

    def test_late_spans_predicted(self):
        spans = v.day_table(self.rows, LATE_ANCHORS)
        self.assertEqual(len(spans), len(LATE_SPANS))
        for s, (h, n, ph) in zip(spans, LATE_SPANS):
            self.assertAlmostEqual(s["hours"], h, delta=0.02, msg=s)
            self.assertEqual(s["new"], n, msg=s)
            self.assertAlmostEqual(s["per_hour"], ph, delta=0.02, msg=s)
        self.assertEqual(sum(s["new"] for s in spans), 5302 - 3775)

    def test_full_nearest_table_sum(self):
        # 15 Oct .. 2 Nov: the day-table sum must equal the 2 Nov anchor count minus row 2's count.
        near = v.nearest_anchors(self.rows, "2026-10-15", "2026-11-02")
        spans = v.day_table(self.rows, [n for _, n in near])
        self.assertEqual(sum(s["new"] for s in spans), 5302 - 1392)


if __name__ == "__main__":
    unittest.main()
