# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working for MV2 of Munim, Inc.
"""Offline tests for the stage 2 vocabulary job (no network)."""
import gzip
import json
import os
import re
import shutil
import tempfile
import unittest
from datetime import datetime, timezone

import job

A = "aaaaaaaa-1111-2222-3333-444444444444"
B = "bbbbbbbb-5555-6666-7777-888888888888"
C = "cccccccc-9999-0000-1111-222222222222"

PAGE_TEXT = """<html><head><script>var x = {"status":"secret_script_value"};</script></head>
<body><div><span>Status</span><span>Judging</span></div>
<div><span>Findings submitted</span><span>7,079</span></div>
<script id="__NEXT_DATA__">{"props":{"status":"judging","totalFindings":7079}}</script></body></html>"""

PAGE_ESCAPED = r"""<html><body><p>Overview</p>
<script>self.__next_f.push([1,"{\"status\":\"complete\",\"totalFindings\":12,\"findingsCount\":null}"])</script>
</body></html>"""


def cdx(rows):
    return [["timestamp", "original", "statuscode", "mimetype", "length"]] + rows


class T(unittest.TestCase):
    def test_main_id(self):
        self.assertEqual(job.main_id("https://cantina.xyz/competitions/%s" % A.upper()), A)
        self.assertEqual(job.main_id("http://www.cantina.xyz/competitions/%s/?x=1" % A), A)
        self.assertIsNone(job.main_id("https://cantina.xyz/competitions/%s/leaderboard" % A))
        self.assertIsNone(job.main_id("https://evil.example/competitions/%s" % A))

    def test_select_captures(self):
        ends = {A: datetime(2025, 1, 1, tzinfo=timezone.utc), B: datetime(2027, 1, 1, tzinfo=timezone.utc)}
        read_at = datetime(2026, 11, 7, 12, 14, 30, tzinfo=timezone.utc)
        rows = cdx([
            ["20241231000000", "https://cantina.xyz/competitions/%s" % A, "200", "text/html", "1"],  # before end
            ["20250105000000", "https://cantina.xyz/competitions/%s" % A, "200", "text/html", "1"],
            ["20250105000000", "https://cantina.xyz/competitions/%s/" % A, "200", "text/html", "1"],  # dup ts
            ["20250106000000", "https://cantina.xyz/competitions/%s" % A, "301", "text/html", "1"],  # not 200
            ["20250107000000", "https://cantina.xyz/competitions/%s/x" % A, "200", "text/html", "1"],  # subpath
            ["20260101000000", "https://cantina.xyz/competitions/%s" % B, "200", "text/html", "1"],  # not ended
            ["20260101000000", "https://cantina.xyz/competitions/%s" % C, "200", "text/html", "1"],  # no end
        ])
        got = job.select_captures(rows, ends, read_at)
        self.assertEqual(got, [(A, "20250105000000", "https://cantina.xyz/competitions/%s" % A)])

    def test_ends_from_api(self):
        data = [{"id": A.upper(), "timeframe": {"end": "2025-01-01T00:00:00Z"}}, {"id": B, "timeframe": {}},
                {"name": "no id"}]
        self.assertEqual(job.ends_from_api(data), {A: datetime(2025, 1, 1, tzinfo=timezone.utc)})
        self.assertEqual(job.ends_from_api({"items": data}), {A: datetime(2025, 1, 1, tzinfo=timezone.utc)})

    def test_text_chunks_skip_scripts(self):
        ch = job.text_chunks(PAGE_TEXT)
        self.assertIn("Judging", ch)
        self.assertFalse(any("secret_script_value" in c for c in ch))

    def test_capture_vocab_text_and_json(self):
        v, f = job.capture_vocab(PAGE_TEXT)
        self.assertEqual(v["after_status_label"], {"judging"})
        self.assertIn("findings submitted -> number", v["after_findings_label_shape"])
        self.assertIn("findings submitted", v["finding_or_submission_labels"])
        self.assertIn("judging", v["status_words_in_text"])
        self.assertIn("judging", v["json_status_values"])
        self.assertIn("totalFindings", v["json_finding_key_numeric"])
        self.assertTrue(f["status_read"] and f["count_read"] and f["json_status"] and f["json_count"])

    def test_capture_vocab_escaped_json(self):
        v, f = job.capture_vocab(PAGE_ESCAPED)
        self.assertEqual(v["json_status_values"], {"complete"})
        self.assertEqual(v["json_finding_keys"], {"totalFindings", "findingsCount"})
        self.assertEqual(v["json_finding_key_numeric"], {"totalFindings"})
        self.assertFalse(f["status_read"])
        self.assertTrue(f["json_status"])

    def test_norm_hides_digits(self):
        self.assertEqual(job.norm("  1,234  Findings "), "#,### findings")
        self.assertLessEqual(len(job.norm("x" * 500)), job.MAX_TOKEN)

    def test_end_to_end_no_pairing_and_cache(self):
        tmp = tempfile.mkdtemp()
        try:
            data, out = os.path.join(tmp, "data"), os.path.join(tmp, "out")
            os.makedirs(data)
            stamp = "20261107T121430Z"
            rows = cdx([["20250105000000", "https://cantina.xyz/competitions/%s" % A, "200", "text/html", "1"],
                        ["20250109123456", "https://cantina.xyz/competitions/%s" % A, "200", "text/html", "1"],
                        ["20250301000000", "https://cantina.xyz/competitions/%s" % C, "200", "text/html", "1"]])
            api = [{"id": A, "timeframe": {"end": "2025-01-01T00:00:00Z"}},
                   {"id": C, "timeframe": {"end": "2025-02-01T00:00:00Z"}}]
            with open(os.path.join(data, "cdx_pages_%s.json" % stamp), "w") as f:
                json.dump(rows, f)
            with open(os.path.join(data, "api_competitions_%s.json" % stamp), "w") as f:
                json.dump(api, f)
            calls = []

            def fake_fetch(url, timeout=120):
                calls.append(url)
                ts = re.search(r"/web/(\d{14})id_/", url).group(1)
                body = PAGE_TEXT if C not in url else PAGE_ESCAPED
                return 200, "https://web.archive.org/web/%sid_/x" % ts, "text/html; charset=utf-8", body.encode()

            old_fetch, old_pause = job.fetch, job.PAUSE_S
            job.fetch, job.PAUSE_S = fake_fetch, 0
            try:
                self.assertEqual(job.main(["--out-dir", out, "--data-dir", data, "--stamp", stamp]), 0)
                self.assertEqual(len(calls), 3)
                with open(os.path.join(out, "summary.json")) as f:
                    s = json.load(f)
                dumped = json.dumps(s)
                for forbidden in (A, C, "20250105000000", "20250109123456", "20250301000000", "2025-01-0"):
                    self.assertNotIn(forbidden, dumped)
                self.assertIsNone(re.search(job.UUID, dumped))
                self.assertIsNone(re.search(r"\d{14}", dumped))
                self.assertEqual(s["captures_selected"], 3)
                self.assertTrue(s["complete"])
                self.assertEqual(s["counts_over_captures"]["parsed"], 3)
                self.assertEqual(s["counts_over_captures"]["status_read"], 2)
                self.assertEqual(s["vocabulary"]["after_status_label"], {"judging": 2})
                js = s["vocabulary"]["json_status_values"]
                self.assertEqual((js["judging"], js["complete"]), (2, 1))
                p = job.cache_path(os.path.join(data, "pages"), A, "20250105000000")
                with gzip.open(p, "rb") as f:
                    self.assertIn(b"Judging", f.read())
                # second run is served from the cache: no new fetches
                self.assertEqual(job.main(["--out-dir", out, "--data-dir", data, "--stamp", stamp]), 0)
                self.assertEqual(len(calls), 3)
            finally:
                job.fetch, job.PAUSE_S = old_fetch, old_pause
        finally:
            shutil.rmtree(tmp)

    def test_missing_inputs_exit_4(self):
        tmp = tempfile.mkdtemp()
        try:
            self.assertEqual(job.main(["--out-dir", os.path.join(tmp, "o"), "--data-dir", tmp]), 4)
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
