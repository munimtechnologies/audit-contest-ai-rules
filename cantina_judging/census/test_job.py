# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working for MV2 of Munim, Inc.
"""Offline tests for the stage 3 census job, v2 (no network: every fetch is replaced)."""
import base64
import csv
import gzip
import io
import json
import os
import shutil
import tempfile
import unittest
import urllib.error
from datetime import datetime, timedelta, timezone

import job

A = "aaaaaaaa-1111-2222-3333-444444444444"
B = "bbbbbbbb-5555-6666-7777-888888888888"
C = "cccccccc-9999-0000-1111-222222222222"
D = "dddddddd-1234-1234-1234-123456789012"
E0 = datetime(2025, 1, 1, tzinfo=timezone.utc)
STAMP = "20261107T121430Z"
URL = "https://cantina.xyz/competitions/%s"
CDX_HEAD = ["timestamp", "original", "statuscode", "mimetype", "length"]


def page(status=None, count=None, json_status=None, total=None):
    parts = ["<html><head><script>var s = {\"status\":\"script_only\"};</script></head><body>"]
    if status is not None:
        parts.append("<div><span>Status</span><span>%s</span></div>" % status)
    if count is not None:
        parts.append("<div><span>Findings submitted</span><span>%s</span></div>" % count)
    js = {"other": {"status": "success"}}
    if json_status is not None:
        js["status"] = json_status
    if total is not None:
        js["totalFindings"] = total
    parts.append('<script id="__NEXT_DATA__">%s</script></body></html>' % json.dumps(js))
    return "".join(parts)


def at(d):
    return E0 + timedelta(days=d)


def cdx_rows_fixture():
    return [CDX_HEAD,
            ["20241201000000", (URL % A) + "/leaderboard", "200", "text/html", "1"],
            ["20250103000000", URL % A, "200", "text/html", "1"],
            ["20250106000000", URL % A, "200", "text/html", "1"],
            ["20250110000000", URL % A, "200", "text/html", "1"],
            ["20250302000000", URL % B, "200", "text/html", "1"],
            ["20250305000000", URL % B, "200", "text/html", "1"],
            ["20250320000000", URL % B, "200", "text/html", "1"],
            ["20250321000000", URL % B, "302", "text/html", "1"],
            ["20260101000000", URL % C, "200", "text/html", "1"]]


BODIES = {(A, "20250103000000"): page("Judging", "100", "judging", 100),
          (A, "20250106000000"): page("Completed", "150", "complete", 150),
          (A, "20250110000000"): page("Completed", "160", "complete", 160),
          (B, "20250302000000"): page("Completed", "50", "complete", 50),
          (B, "20250320000000"): "<html><body><p>Overview</p></body></html>"}


def bound_csv():
    """Stage-1 table as stage 1 wrote it (ended competitions only)."""
    f = io.StringIO()
    w = csv.DictWriter(f, fieldnames=["id", "kind", "status_now", "end", "totalFindings", "main_captures_200",
                                      "main_after_end"])
    w.writeheader()
    w.writerow({"id": A, "kind": "public_contest", "status_now": "complete", "end": "2025-01-01T00:00:00Z",
                "totalFindings": 160, "main_captures_200": 3, "main_after_end": 3})
    w.writerow({"id": B, "kind": "public_contest", "status_now": "complete", "end": "2025-03-01T00:00:00Z",
                "totalFindings": 50, "main_captures_200": 3, "main_after_end": 3})
    return f.getvalue().encode()


class Patch:
    """Replace module attributes for one test and put them back."""

    def __init__(self, **kw):
        self.kw = kw
        self.old = {}

    def __enter__(self):
        for k, v in self.kw.items():
            self.old[k] = getattr(job, k)
            setattr(job, k, v)
        return self

    def __exit__(self, *exc):
        for k, v in self.old.items():
            setattr(job, k, v)


PUBLIC = lambda polls, wait_s: {"public": True, "polls": 1}  # noqa: E731


class T(unittest.TestCase):
    def test_class_of(self):
        self.assertEqual(job.class_of("Live"), "live")
        self.assertEqual(job.class_of("completed"), "complete")
        self.assertEqual(job.class_of(" Complete "), "complete")
        for v in ("judging", "reviewing escalations", "escalations ended", "escalations", "something new"):
            self.assertEqual(job.class_of(v), "post-live")

    def test_extract_text_and_json(self):
        x = job.extract(page("Judging", "7,079", "judging", 7079))
        self.assertEqual(x["text_status"], ["judging"])
        self.assertEqual(x["text_count"], 7079)
        self.assertEqual(x["json_classes"], ["post-live"])
        self.assertIn("success", x["json_values"])
        self.assertEqual(x["json_count"], 7079)

    def test_status_with_colon_on_same_chunk(self):
        x = job.extract("<html><body><p>Status: Completed</p></body></html>")
        self.assertEqual(x["text_status"], ["completed"])

    def test_read_capture_rules(self):
        rec, why, _ = job.read_capture(page("Completed", "12", "complete", 12))
        self.assertIsNone(why)
        self.assertEqual((rec["class"], rec["count"], rec["count_source"], rec["json_check"]),
                         ("complete", 12, "text", "agree"))
        rec, why, _ = job.read_capture(page("Completed", None, "judging", 12))
        self.assertIsNone(rec)
        self.assertEqual(why, "text and JSON disagree")
        rec, why, _ = job.read_capture(page(None, None, "complete", 12))
        self.assertEqual(why, "no status")
        two = "<html><body><p>Status</p><p>Live</p><p>Status</p><p>Judging</p></body></html>"
        self.assertEqual(job.read_capture(two)[1], "ambiguous status")
        rec, why, _ = job.read_capture(page("Judging", "7.1k", "judging", 7079))
        self.assertEqual((rec["count"], rec["count_source"]), (7079, "json"))
        many = page("Judging", "5", "judging", 5).replace('"other": {"status": "success"}',
                                                          '"other": {"status": "complete"}')
        rec, why, _ = job.read_capture(many)
        self.assertIsNone(why)
        self.assertEqual((rec["class"], rec["json_check"]), ("post-live", "several"))
        amb = page("Live", None, "live", 3).replace('"other": {"status": "success"}',
                                                    '"other": {"status": "success", "totalFindings": 9}')
        rec, why, _ = job.read_capture(amb)
        self.assertIsNone(why)
        self.assertIsNone(rec["count"])

    def test_analyse_brackets(self):
        caps = [(at(2), "post-live", 100), (at(5), "post-live", 140), (at(9), "complete", 150),
                (at(20), "complete", 150)]
        r = job.analyse(E0, caps)
        self.assertAlmostEqual(r["completion_lower_days"], 5.0)
        self.assertAlmostEqual(r["completion_upper_days"], 9.0)
        self.assertAlmostEqual(r["completion_width_days"], 4.0)
        self.assertAlmostEqual(r["completion_midpoint_days"], 7.0)
        self.assertAlmostEqual(r["start_lower_hours"], 0.0)
        self.assertAlmostEqual(r["start_upper_hours"], 48.0)
        self.assertAlmostEqual(r["start_width_days"], 2.0)
        self.assertTrue(r["has_noncomplete"])
        self.assertEqual(r["earliest_noncomplete_count"], 100)
        self.assertFalse(r["reversal"])

    def test_analyse_live_then_complete_and_reversal(self):
        caps = [(at(1), "live", 10), (at(3), "complete", 20), (at(4), "post-live", 20), (at(30), "complete", 20)]
        r = job.analyse(E0, caps)
        self.assertAlmostEqual(r["start_lower_hours"], 24.0)
        self.assertAlmostEqual(r["start_upper_hours"], 72.0)
        self.assertAlmostEqual(r["completion_lower_days"], 1.0)
        self.assertAlmostEqual(r["completion_upper_days"], 3.0)
        self.assertTrue(r["reversal"])
        self.assertEqual(r["earliest_noncomplete_count"], 10)

    def test_analyse_only_complete_and_empty(self):
        r = job.analyse(E0, [(at(40), "complete", None)])
        self.assertAlmostEqual(r["completion_lower_days"], 0.0)
        self.assertAlmostEqual(r["completion_width_days"], 40.0)
        self.assertFalse(r["has_noncomplete"])
        r = job.analyse(E0, [])
        self.assertIsNone(r["completion_width_days"])
        self.assertIsNone(r["start_upper_hours"])

    def test_spearman(self):
        self.assertAlmostEqual(job.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
        self.assertAlmostEqual(job.spearman([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)
        self.assertEqual(job.ranks([5, 1, 5, 2]), [3.5, 1.0, 3.5, 2.0])
        self.assertIsNone(job.spearman([1, 1, 1], [1, 2, 3]))
        self.assertIsNone(job.spearman([1, 2], [1, 2]))

    def _row(self, i, mid, year, final, start_w=None, start_up=None, nc=None):
        return {"eligible": True, "completion_midpoint_days": mid, "end_year": year, "final_count": final,
                "start_width_days": start_w, "start_upper_hours": start_up, "has_noncomplete": nc is not None,
                "earliest_noncomplete_count": nc}

    def test_grade_gate_fails(self):
        rows = [self._row(i, 30.0, 2026, 100) for i in range(19)]
        g = job.grade(rows)
        self.assertFalse(g["gate_passed"])
        for p in ("P1", "P2", "P3", "P4", "P5"):
            self.assertEqual(g[p]["grade"], "not testable")

    def test_grade_gate_passes(self):
        rows = []
        for i in range(10):
            rows.append(self._row(i, 30.0 + i, 2026, 1000 + i, 1.0, 72.0, 500))
        for i in range(10):
            rows.append(self._row(i, 10.0 + i, 2024, 100 + i, 2.0, 200.0 if i < 3 else 100.0, 200 + i))
        g = job.grade(rows)
        self.assertTrue(g["gate_passed"])
        self.assertEqual(g["P1"]["grade"], "held")
        self.assertAlmostEqual(g["P1"]["median_midpoint_days"], 24.5)
        self.assertEqual(g["P2"]["grade"], "held")
        self.assertEqual(g["P3"]["grade"], "held")
        self.assertEqual(g["P3"]["upper_le_7d"], 17)
        self.assertEqual(g["P4"]["grade"], "held")
        self.assertEqual(g["P5"]["grade"], "held")

    # ------------------------------------------------------------ v2: rebuild route

    def test_git_blob_sha(self):
        self.assertEqual(job.git_blob_sha(b""), "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")
        self.assertEqual(job.git_blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_bound_table_from_blob_and_comps(self):
        content = bound_csv()
        raw = json.dumps({"content": base64.encodebytes(content).decode(), "encoding": "base64"}).encode()
        table = job.bound_table_from_blob(raw, job.git_blob_sha(content))
        comps = job.comps_from_bound(table)
        self.assertEqual(sorted(comps), [A, B])
        self.assertEqual(comps[A]["end"], E0)
        self.assertEqual(comps[A]["final_count"], 160)
        self.assertEqual(job.stage1_counts(table)[B], (3, 3))
        with self.assertRaises(ValueError):
            job.bound_table_from_blob(raw, "0" * 40)

    def test_comps_from_bound_counts(self):
        comps = job.comps_from_bound([{"id": A.upper(), "end": "2025-01-01T00:00:00Z", "totalFindings": "",
                                       "status_now": "complete"},
                                      {"id": B, "end": "2025-03-01T00:00:00Z", "totalFindings": "True"}])
        self.assertIsNone(comps[A]["final_count"])
        self.assertIsNone(comps[B]["final_count"])
        self.assertIsNone(comps[B]["status_now"])

    def test_cdx_query_cut_off(self):
        u = job.cdx_query_url(datetime(2026, 11, 7, 12, 14, 30, tzinfo=timezone.utc))
        self.assertIn("to=20261107121430", u)
        self.assertIn("matchType=prefix", u)

    def test_reconcile_exact_and_newest_extra(self):
        comps = {A: {"end": E0}, B: {"end": at(59)}}
        rows = cdx_rows_fixture() + [["20261107000000", URL % A, "200", "text/html", "1"]]
        kept, rep = job.reconcile_cdx(rows, comps, {A: (3, 3), B: (3, 3)})
        self.assertTrue(rep["matched"])
        self.assertEqual(rep["dropped_newest_captures"], 1)
        self.assertEqual(rep["dropped_oldest_ts"], "20261107000000")
        self.assertEqual(len(kept), len(rows) - 1)
        self.assertNotIn("20261107000000", [r[0] for r in kept])

    def test_reconcile_mismatch(self):
        comps = {A: {"end": E0}, B: {"end": at(59)}}
        rows = [r for r in cdx_rows_fixture() if r[0] != "20250106000000"]  # one capture missing
        _, rep = job.reconcile_cdx(rows, comps, {A: (3, 3), B: (3, 3)})
        self.assertFalse(rep["matched"])
        self.assertEqual(rep["n_differences"], 1)
        # an extra capture that is not the newest cannot be dropped (E = 5 Jan: stage 1 saw 2 after E)
        extra = cdx_rows_fixture() + [["20250104000000", URL % A, "200", "text/html", "1"]]
        _, rep = job.reconcile_cdx(extra, {A: {"end": at(4)}, B: {"end": at(59)}}, {A: (3, 2), B: (3, 3)})
        self.assertFalse(rep["matched"])
        self.assertEqual(rep["differences"][0]["rebuilt_main"], 4)

    # ------------------------------------------------------------ end to end

    def _write_cache_route(self, data):
        pages = os.path.join(data, "pages")
        os.makedirs(pages)
        api = {"items": [
            {"id": A.upper(), "status": "complete", "totalFindings": 160, "timeframe": {"end": "2025-01-01T00:00:00Z"}},
            {"id": B, "status": "complete", "totalFindings": 50, "timeframe": {"end": "2025-03-01T00:00:00Z"}},
            {"id": C, "status": "live", "totalFindings": 1, "timeframe": {"end": "2027-01-01T00:00:00Z"}},
            {"id": D, "status": "complete", "totalFindings": None, "timeframe": {}}]}
        with open(os.path.join(data, "cdx_pages_%s.json" % STAMP), "w") as f:
            json.dump(cdx_rows_fixture(), f)
        with open(os.path.join(data, "api_competitions_%s.json" % STAMP), "w") as f:
            json.dump(api, f)
        index = []
        for (cid, ts), body in BODIES.items():
            with gzip.open(job.cache_path(pages, cid, ts), "wb") as f:
                f.write(body.encode())
            final = "20250228000000" if (cid, ts) == (B, "20250302000000") else ts
            index.append(json.dumps({"id": cid, "ts": ts, "final_ts": final}))
        with open(os.path.join(pages, "index.jsonl"), "w") as f:
            f.write("\n".join(index) + "\n")

    def _check_census(self, out):
        with open(os.path.join(out, "summary.json")) as f:
            s = json.load(f)
        self.assertEqual(s["captures_selected"], 6)
        self.assertEqual(s["captures_readable"], 3)
        self.assertEqual(s["excluded"], {"no status": 1, "not in stage-2 cache": 1,
                                         "served capture not after end": 1})
        self.assertEqual(s["coverage_start"], "2024-12-01T00:00:00Z")
        self.assertEqual(s["competitions_ended"], 2)
        self.assertEqual(s["competitions_with_complete_capture"], 1)
        self.assertEqual(s["status_values_text"], {"completed": 2, "judging": 1})
        self.assertEqual(s["capture_days_per_month"], {"2025-01": 3})
        self.assertFalse(s["grades"]["gate_passed"])
        self.assertEqual(s["grades"]["eligible"], 1)
        with open(os.path.join(out, "brackets_by_id.csv"), newline="") as f:
            br = {r["id"]: r for r in csv.DictReader(f)}
        self.assertEqual(sorted(br), [A, B])
        self.assertEqual(br[A]["eligible"], "True")
        self.assertEqual(br[A]["completion_lower_days"], "2.0")
        self.assertEqual(br[A]["completion_upper_days"], "5.0")
        self.assertEqual(br[A]["completion_midpoint_days"], "3.5")
        self.assertEqual(br[A]["start_upper_hours"], "48.0")
        self.assertEqual(br[A]["earliest_noncomplete_count"], "100")
        self.assertEqual(br[B]["eligible"], "False")
        self.assertEqual(br[B]["n_readable_after_end"], "0")
        with open(os.path.join(out, "captures.csv"), newline="") as f:
            self.assertEqual(len(list(csv.DictReader(f))), 6)
        return s

    def test_end_to_end_cache_route(self):
        tmp = tempfile.mkdtemp()
        try:
            data, out = os.path.join(tmp, "data"), os.path.join(tmp, "out")
            self._write_cache_route(data)

            def no_network(*a, **k):
                raise AssertionError("the cache route must not fetch")

            with Patch(addendum_is_public=PUBLIC, fetch_bytes=no_network, fetch=no_network):
                self.assertEqual(job.main(["--out-dir", out, "--data-dir", data, "--stamp", STAMP]), 0)
            s = self._check_census(out)
            self.assertEqual(s["inputs_route"], "stage-2 cache")
            self.assertIsNone(s["inputs_match"])
            self.assertTrue(s["grades_status"].startswith("pre-registered census"))
        finally:
            shutil.rmtree(tmp)

    def _rebuild_fakes(self, cdx_rows):
        content = bound_csv()
        blob = json.dumps({"content": base64.encodebytes(content).decode(), "encoding": "base64"}).encode()
        calls = []

        def fake_fetch_bytes(url, tries=4, timeout=180, accept=None):
            calls.append(url)
            if "git/blobs" in url:
                return blob
            if "cdx/search" in url:
                return json.dumps(cdx_rows).encode()
            raise AssertionError(url)

        def fake_fetch(url, timeout=120):
            calls.append(url)
            ts = url.split("/web/")[1][:14]
            cid = url.rstrip("/").split("/")[-1]
            if (cid, ts) not in BODIES:
                raise urllib.error.HTTPError(url, 404, "not found", None, None)
            final_ts = "20250228000000" if (cid, ts) == (B, "20250302000000") else ts
            return 200, "https://web.archive.org/web/%sid_/%s" % (final_ts, URL % cid), "text/html", \
                BODIES[(cid, ts)].encode()

        return content, fake_fetch_bytes, fake_fetch, calls

    def test_end_to_end_rebuild_route_matched(self):
        tmp = tempfile.mkdtemp()
        try:
            data, out = os.path.join(tmp, "data"), os.path.join(tmp, "out")
            os.makedirs(data)
            rows = cdx_rows_fixture() + [["20261107000000", URL % A, "200", "text/html", "1"]]
            content, fb, ff, calls = self._rebuild_fakes(rows)
            expect = {"captures_selected": 6, "cached": 5, "status_read": 4, "json_status": 4, "redirected": 1}
            with Patch(addendum_is_public=PUBLIC, fetch_bytes=fb, fetch=ff, _sleep=lambda s: None,
                       BOUND_BLOB_SHA=job.git_blob_sha(content), STAGE2=expect):
                self.assertEqual(job.main(["--out-dir", out, "--data-dir", data, "--stamp", STAMP]), 0)
            s = self._check_census(out)
            self.assertEqual(s["inputs_route"], "rebuilt")
            self.assertTrue(s["rebuild"]["cdx"]["matched"])
            self.assertEqual(s["rebuild"]["cdx"]["dropped_newest_captures"], 1)
            self.assertEqual(s["stage2_check"]["got"], expect)
            self.assertTrue(s["inputs_match"])
            self.assertTrue(s["grades_status"].startswith("pre-registered census"))
            self.assertTrue(any("to=20261107121430" in c for c in calls))
            self.assertTrue(os.path.isdir(os.path.join(data, "rebuild-%s" % STAMP, "pages")))
        finally:
            shutil.rmtree(tmp)

    def test_end_to_end_rebuild_route_mismatch_is_descriptive(self):
        tmp = tempfile.mkdtemp()
        try:
            data, out = os.path.join(tmp, "data"), os.path.join(tmp, "out")
            os.makedirs(data)
            content, fb, ff, _ = self._rebuild_fakes(cdx_rows_fixture())
            with Patch(addendum_is_public=PUBLIC, fetch_bytes=fb, fetch=ff, _sleep=lambda s: None,
                       BOUND_BLOB_SHA=job.git_blob_sha(content)):  # real STAGE2 counts: cannot match
                self.assertEqual(job.main(["--out-dir", out, "--data-dir", data, "--stamp", STAMP]), 0)
            with open(os.path.join(out, "summary.json")) as f:
                s = json.load(f)
            self.assertFalse(s["inputs_match"])
            self.assertTrue(s["grades_status"].startswith("descriptive only"))
        finally:
            shutil.rmtree(tmp)

    def test_exit_3_without_addenda(self):
        tmp = tempfile.mkdtemp()
        try:
            with Patch(addendum_is_public=lambda polls, wait_s: {"public": False, "polls": polls}):
                self.assertEqual(job.main(["--out-dir", os.path.join(tmp, "o"), "--data-dir", tmp]), 3)
            with open(os.path.join(tmp, "o", "summary.json")) as f:
                self.assertIn("stopped", json.load(f))
        finally:
            shutil.rmtree(tmp)

    def test_missing_inputs_and_failed_rebuild_exit_4(self):
        tmp = tempfile.mkdtemp()

        def down(*a, **k):
            raise RuntimeError("offline")

        try:
            with Patch(addendum_is_public=PUBLIC, fetch_bytes=down, fetch=down, _sleep=lambda s: None):
                self.assertEqual(job.main(["--out-dir", os.path.join(tmp, "o"), "--data-dir", tmp]), 4)
            with open(os.path.join(tmp, "o", "summary.json")) as f:
                self.assertIn("rebuild failed", json.load(f)["stopped"])
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
