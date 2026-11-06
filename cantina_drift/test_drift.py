"""Offline tests for drift.py (no network). Apache-2.0. Made with AI agents working for MV2 of Munim, Inc."""
import unittest

import drift


def rec(i, n, status="complete", kind="public_contest", end="2025-01-01T00:00:00Z", name=None):
    return {"id": i, "name": name or f"c{i}", "kind": kind, "status": status, "end": end, "total_findings": n}


class ParseTime(unittest.TestCase):
    def test_forms(self):
        self.assertEqual(drift.parse_time("2026-11-03T18:30:00Z").hour, 18)
        self.assertEqual(drift.parse_time("2026-10-14T20:03Z").minute, 3)
        self.assertIsNotNone(drift.parse_time("2026-09-21T09:21:19.160847Z"))
        self.assertIsNone(drift.parse_time(None))
        self.assertIsNone(drift.parse_time("not a date"))


class TrimApi(unittest.TestCase):
    def test_private_has_no_name(self):
        item = {"id": "x", "name": "secret", "kind": "private_contest", "status": "complete",
                "timeframe": {"start": "a", "end": "b"}, "totalFindings": 5}
        t = drift.trim_api(item)
        self.assertIsNone(t["name"])
        self.assertEqual(t["end"], "b")
        self.assertEqual(t["total_findings"], 5)

    def test_bare_array_and_wrapped(self):
        item = {"id": "y", "name": "n", "kind": "public_contest", "totalFindings": 1}
        self.assertEqual(len(drift.records_from_api([item])), 1)
        self.assertEqual(len(drift.records_from_api({"items": [item]})), 1)
        self.assertEqual(drift.records_from_api("junk"), [])


class Compare(unittest.TestCase):
    def test_classification_and_grades(self):
        base = [rec(str(i), 100) for i in range(40)]
        base.append(rec("live1", 1369, status="live"))
        base.append(rec("priv", 7, kind="private_contest"))
        base.append(rec("gone", 50))
        cur = [rec(str(i), 100) for i in range(39)] + [rec("39", 103)]
        cur.append(rec(drift.V4LEND_ID, 6950, status="live"))
        cur.append(rec("live1", 2000, status="live"))
        cur.append(rec("priv", 7, kind="private_contest"))
        out = drift.compare(base, cur, "2026-10-14T20:03Z", "2026-11-05T10:00:00Z")
        s = out["summary"]
        self.assertEqual(s["S_size"], 40)            # live, private and missing are excluded
        self.assertEqual(s["S_unchanged"], 39)
        self.assertEqual(s["S_increased"], 1)
        self.assertEqual(s["S_sum_delta"], 3)
        self.assertEqual(s["missing_now"], 1)
        self.assertEqual(s["D1"], "HELD")            # 39/40 = 0.975
        self.assertEqual(s["D2"], "HELD")
        self.assertEqual(s["D3"], "HELD")            # 3 / 4000 < 0.5%
        self.assertEqual(s["new_ids_since_baseline"], [drift.V4LEND_ID])
        self.assertEqual(len(s["S_changed"]), 1)

    def test_failures(self):
        base = [rec(str(i), 100) for i in range(10)]
        cur = [rec(str(i), 100) for i in range(8)] + [rec("8", 90), rec("9", 150)]
        cur.append(rec(drift.V4LEND_ID, 6000, status="live"))
        s = drift.compare(base, cur, "2026-10-14T20:03Z", "x")["summary"]
        self.assertEqual(s["D1"], "FAILED")          # 8/10
        self.assertEqual(s["D2"], "FAILED")          # 6000 < 6906
        self.assertEqual(s["D3"], "FAILED")          # |40| / 1000 = 4%
        self.assertEqual(s["S_decreased"], 1)

    def test_not_gradable_without_v4lend(self):
        s = drift.compare([rec("a", 1)], [rec("a", 1)], "2026-10-14T20:03Z", "x")["summary"]
        self.assertEqual(s["D2"], "NOT GRADABLE")

    def test_days_ended(self):
        out = drift.compare([rec("a", 1, end="2026-10-13T20:03:00Z")], [rec("a", 1)], "2026-10-14T20:03Z", "x")
        self.assertEqual(out["rows"][0]["days_ended_at_baseline"], 1.0)


if __name__ == "__main__":
    unittest.main()
