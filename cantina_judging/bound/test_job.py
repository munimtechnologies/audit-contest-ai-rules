# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working for MV2 of Munim, Inc. Offline tests (no network).
import unittest
from datetime import datetime, timezone, timedelta

import job

ID = "e275368c-547d-4d91-a418-053ad31082a8"
OTHER = "fe8e03b1-f8db-4698-8a21-44b3a862e434"
HEAD = ["timestamp", "original", "statuscode", "mimetype", "length"]
UTC = timezone.utc


def dt(*a):
    return datetime(*a, tzinfo=UTC)


class T(unittest.TestCase):
    def test_parse_ts(self):
        self.assertEqual(job.parse_ts("20261107031500"), dt(2026, 11, 7, 3, 15, 0))
        self.assertIsNone(job.parse_ts("2026"))
        self.assertIsNone(job.parse_ts("2026110703150x"))

    def test_parse_iso(self):
        self.assertEqual(job.parse_iso("2026-11-03T18:30:00Z"), dt(2026, 11, 3, 18, 30))
        self.assertEqual(job.parse_iso("2025-03-07T18:00:00.123456Z").replace(microsecond=0), dt(2025, 3, 7, 18))
        self.assertIsNone(job.parse_iso(None))
        self.assertIsNone(job.parse_iso("not a date"))

    def test_capture_id(self):
        b = "https://cantina.xyz/competitions/"
        self.assertEqual(job.capture_id(b + ID.upper(), True), ID)
        self.assertEqual(job.capture_id(b + ID + "/", True), ID)
        self.assertEqual(job.capture_id(b + ID + "?view=details", True), ID)
        self.assertEqual(job.capture_id("http://www.cantina.xyz:80/competitions/" + ID, True), ID)
        self.assertIsNone(job.capture_id(b + ID + "/leaderboard", True))
        self.assertEqual(job.capture_id(b + ID + "/leaderboard", False), ID)
        self.assertIsNone(job.capture_id("https://evil.example/competitions/" + ID, False))
        self.assertIsNone(job.capture_id(b, False))
        self.assertIsNone(job.capture_id(b + ID + "x", True))

    def test_captures_by_id(self):
        b = "https://cantina.xyz/competitions/"
        rows = job.parse_rows([HEAD,
                               ["20261010000000", b + ID, "200", "h", "1"],
                               ["20261010000000", b + ID + "/", "200", "h", "1"],
                               ["20261011000000", b + ID, "302", "h", "1"],
                               ["20261012000000", b + ID + "/leaderboard", "200", "h", "1"],
                               ["20250101000000", b + OTHER, "200", "h", "1"]])
        main = job.captures_by_id(rows, True)
        self.assertEqual(main[ID], [dt(2026, 10, 10)])
        anyc = job.captures_by_id(rows, False)
        self.assertEqual(anyc[ID], [dt(2026, 10, 10), dt(2026, 10, 12)])
        self.assertEqual(len(anyc[OTHER]), 1)

    def test_bound_for(self):
        end = dt(2026, 1, 1)
        # captures before the end are ignored; gaps 20 d then 10 d -> completion possible
        b = job.bound_for(end, [dt(2025, 12, 1), end + timedelta(days=20), end + timedelta(days=30)])
        self.assertEqual(b["n_after_end"], 2)
        self.assertTrue(b["completion_possible"])
        self.assertFalse(b["start_possible"])
        self.assertEqual(b["min_gap_days"], 10.0)
        self.assertEqual(b["first_after_end_days"], 20.0)
        # only one capture 40 d after: no bracket <= 14 d
        b = job.bound_for(end, [end + timedelta(days=40)])
        self.assertFalse(b["completion_possible"])
        # a capture 2 d after the end: both possible
        b = job.bound_for(end, [end + timedelta(days=2)])
        self.assertTrue(b["completion_possible"] and b["start_possible"])
        # nothing after the end
        b = job.bound_for(end, [])
        self.assertEqual((b["n_after_end"], b["min_gap_days"], b["completion_possible"]), (0, None, False))
        # exactly 14 days counts
        self.assertTrue(job.bound_for(end, [end + timedelta(days=14)])["completion_possible"])

    def test_competitions_from_api(self):
        item = {"id": ID.upper(), "status": "complete", "kind": "public",
                "timeframe": {"start": "2026-10-01T00:00:00Z", "end": "2026-11-03T18:30:00Z"},
                "totalFindings": 7079}
        out = job.competitions_from_api([item, {"name": "no id"}])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["id"], ID)
        self.assertEqual(out[0]["end"], dt(2026, 11, 3, 18, 30))
        self.assertEqual(len(job.competitions_from_api({"data": [item]})), 1)
        self.assertEqual(job.competitions_from_api({"x": 1}), [])
        nt = job.competitions_from_api([{"id": OTHER, "timeframe": None}])
        self.assertIsNone(nt[0]["end"])

    def test_build_gate(self):
        now = dt(2026, 11, 7)
        comps = job.competitions_from_api([
            {"id": ID, "status": "judging", "kind": "k", "timeframe": {"end": "2026-11-03T18:30:00Z"}, "totalFindings": 5},
            {"id": OTHER, "status": "complete", "kind": "k", "timeframe": {"end": "2026-01-01T00:00:00Z"}, "totalFindings": 9},
            {"id": "00000000-0000-0000-0000-000000000000", "status": "live", "kind": "k",
             "timeframe": {"end": "2026-12-01T00:00:00Z"}},
            {"id": "11111111-1111-1111-1111-111111111111", "status": "complete", "timeframe": {}}])
        main = {ID: [dt(2026, 11, 5)], OTHER: [dt(2026, 3, 1)]}
        table, c = job.build(comps, main, main, now)
        self.assertEqual((c["ended"], c["end_in_future"], c["no_end"]), (2, 1, 1))
        self.assertEqual(c["bound_eligible_main"], 1)
        self.assertEqual(c["bound_eligible_main_status_now_complete"], 0)
        self.assertEqual(c["bound_start_bracket_le3d_main"], 1)
        self.assertFalse(c["gate_can_pass"])
        self.assertEqual(c["captured_ids_not_in_api"], 0)
        self.assertEqual(len(table), 2)


if __name__ == "__main__":
    unittest.main()
