"""Offline tests for fetch_c4.py (parsing) and c4_crowding.py (the census).

Licensed under Apache-2.0. Made with AI agents working for MV2 of Munim, Inc.
"""
import csv
import datetime as dt
import json
import os
import tempfile
import unittest
from unittest import mock

import c4_crowding
import fetch_c4

REPORT = """---
sponsor: "Rubicon"
slug: "2023-04-rubicon"
date: "2025-02-17"
title: "Rubicon v2"
findings: "https://github.com/code-423n4/2023-04-rubicon-findings/issues"
contest: 229
---

# Overview

The audit took place between April 5 — April 13 2023.

## Wardens

194 Wardens contributed reports to the Rubicon v2:

## Summary

The C4 analysis yielded an aggregated total of 45 unique vulnerabilities. Of these vulnerabilities, 17 received a risk rating in the category of HIGH severity and 28 received a risk rating in the category of MEDIUM severity.
"""

README = """# Rubicon contest details
- Total Prize Pool: $60,500 USDC
  - HM awards: $46,550 USDC
- Starts April 05, 2023 20:00 UTC
- Ends April 13, 2023 20:00 UTC

Total nSLOC: 1577 - [calculated with this plugin.]
"""


class DateTest(unittest.TestCase):
    def test_month_num(self):
        self.assertEqual(fetch_c4.month_num("April"), 4)
        self.assertEqual(fetch_c4.month_num("Sept."), 9)
        self.assertEqual(fetch_c4.month_num("Dec"), 12)
        self.assertIsNone(fetch_c4.month_num("to"))
        self.assertIsNone(fetch_c4.month_num("and"))

    def test_parse_span_formats(self):
        d = dt.date
        cases = {
            "April 5 — April 13 2023": (d(2023, 4, 5), d(2023, 4, 13)),
            "January 7—13, 2022": (d(2022, 1, 7), d(2022, 1, 13)),
            "November 11 to November 25, 2024": (d(2024, 11, 11), d(2024, 11, 25)),
            "Dec 28, 2023 - Jan 5, 2024": (d(2023, 12, 28), d(2024, 1, 5)),
            "December 28 — January 5, 2024": (d(2023, 12, 28), d(2024, 1, 5)),
        }
        for text, want in cases.items():
            self.assertEqual(fetch_c4.parse_span(text), want, text)
        self.assertIsNone(fetch_c4.parse_span("no dates here"))

    def test_parse_date(self):
        self.assertEqual(fetch_c4.parse_date("April 05, 2023"), dt.date(2023, 4, 5))
        self.assertEqual(fetch_c4.parse_date("Nov 11 2024"), dt.date(2024, 11, 11))
        self.assertIsNone(fetch_c4.parse_date("Foo 11 2024"))


class ReportTest(unittest.TestCase):
    def test_front_matter(self):
        fm = fetch_c4.front_matter(REPORT)
        self.assertEqual(fm["slug"], "2023-04-rubicon")
        self.assertEqual(fm["contest"], "229")
        self.assertEqual(fm["findings"], "https://github.com/code-423n4/2023-04-rubicon-findings/issues")

    def test_parse_report(self):
        rep = fetch_c4.parse_report(REPORT)
        self.assertTrue(rep["present"])
        self.assertEqual(rep["contest"], 229)
        self.assertEqual(rep["title"], "Rubicon v2")
        self.assertEqual((rep["start"], rep["end"]), ("2023-04-05", "2023-04-13"))
        self.assertEqual((rep["unique_total"], rep["unique_high"], rep["unique_medium"]), (45, 17, 28))
        self.assertEqual(rep["wardens"], 194)

    def test_parse_report_late_2024_wording(self):
        text = ("---\nslug: \"2024-11-nibiru\"\ncontest: 453\n---\n"
                "The audit took place from November 11 to November 25, 2024.\n"
                "The C4 analysis yielded an aggregated total of 16 unique vulnerabilities. "
                "Of these vulnerabilities, 6 received a risk rating in the category of HIGH severity "
                "and 10 received a risk rating in the category of MEDIUM severity.\n")
        rep = fetch_c4.parse_report(text)
        self.assertEqual((rep["start"], rep["end"]), ("2024-11-11", "2024-11-25"))
        self.assertEqual((rep["unique_high"], rep["unique_medium"]), (6, 10))
        self.assertIsNone(rep["wardens"])

    def test_parse_report_missing(self):
        self.assertEqual(fetch_c4.parse_report(None), {"present": False})


class ReadmeTest(unittest.TestCase):
    def test_parse_readme(self):
        rd = fetch_c4.parse_readme(README)
        self.assertEqual(rd["pot_usd"], 60500.0)
        self.assertEqual(rd["pot_text"], "- Total Prize Pool: $60,500 USDC")
        self.assertEqual((rd["start"], rd["end"]), ("2023-04-05", "2023-04-13"))
        self.assertEqual(rd["nsloc"], 1577)

    def test_pot_variants(self):
        self.assertEqual(fetch_c4.parse_readme("Total Prize Pool: $70,000 in USDC")["pot_usd"], 70000.0)
        self.assertEqual(fetch_c4.parse_readme("Prize Pool: $50K USDC")["pot_usd"], 50000.0)
        self.assertEqual(fetch_c4.parse_readme("Prize Pool: $1,000 MATIC")["pot_usd"], 1000.0)
        self.assertIsNone(fetch_c4.parse_readme("no pot")["pot_usd"])


class DataTest(unittest.TestCase):
    def test_risk_class(self):
        self.assertEqual(fetch_c4.risk_class("3"), "high")
        self.assertEqual(fetch_c4.risk_class(2), "medium")
        self.assertEqual(fetch_c4.risk_class("G"), "gas")
        self.assertEqual(fetch_c4.risk_class("Q"), "qa")
        self.assertEqual(fetch_c4.risk_class("A"), "analysis")
        self.assertEqual(fetch_c4.risk_class(None), "other")

    def test_summarize_data_counts_without_handles(self):
        names = ["README.md", "report.md", "data/a-1.json", "data/b-2.json", "data/b-3.json",
                 "data/a-Q.md", "data/c-4.json", "data/x-G.md"]
        docs = {
            "data/a-1.json": {"contest": 229, "handle": "Alice", "address": "0xabc", "risk": "3", "issueId": 1},
            "data/b-2.json": {"contest": 229, "handle": "bob", "risk": "2", "issueId": 2},
            "data/b-3.json": {"contest": 229, "handle": "Bob", "risk": "Q", "issueId": 3},
            "data/c-4.json": None,
        }
        out = fetch_c4.summarize_data(names, docs)
        self.assertEqual(out["json_records"], 3)
        self.assertEqual(out["json_bad"], 1)
        self.assertEqual((out["risk"]["high"], out["risk"]["medium"], out["risk"]["qa"]), (1, 1, 1))
        self.assertEqual((out["md_files"]["qa"], out["md_files"]["gas"]), (1, 1))
        self.assertEqual(out["submitters"], 2)
        self.assertEqual(out["max_issue_id"], 3)
        self.assertEqual(out["with_original_id"], 0)
        self.assertEqual(out["contest_ids"], [229])
        text = json.dumps(out)
        for secret in ("Alice", "bob", "Bob", "0xabc", "handle", "address"):
            self.assertNotIn(secret, text)

    def test_validated_era_ids(self):
        docs = {"data/a-17.json": {"risk": "2", "issueId": 17, "originalIssueId": 161}}
        out = fetch_c4.summarize_data(["data/a-17.json"], docs)
        self.assertEqual((out["with_original_id"], out["max_original_issue_id"]), (1, 161))

    def test_repo_names(self):
        self.assertTrue(fetch_c4.is_findings_repo("2022-01-insure-findings"))
        self.assertFalse(fetch_c4.is_findings_repo("2022-01-insure"))
        self.assertEqual(fetch_c4.audit_slug("2022-01-insure-findings", {}), "2022-01-insure")
        self.assertEqual(fetch_c4.audit_slug("x-findings", {"slug": "y"}), "y")


class FetchLoopTest(unittest.TestCase):
    def test_pending_skips_done_and_limits(self):
        repos = [{"repo": "a-findings"}, {"repo": "b-findings"}, {"repo": "c-findings"}]
        self.assertEqual([r["repo"] for r in fetch_c4.pending(repos, {"b-findings"})], ["a-findings", "c-findings"])
        self.assertEqual([r["repo"] for r in fetch_c4.pending(repos, set(), 2)], ["a-findings", "b-findings"])

    def test_fetch_one_turns_exceptions_into_error_records(self):
        with mock.patch.object(fetch_c4, "inspect_repo", side_effect=RuntimeError("boom")):
            rec = fetch_c4.fetch_one({"repo": "a-findings", "created_at": None}, "/tmp", "now", 0)
        self.assertEqual(rec["repo"], "a-findings")
        self.assertIn("RuntimeError", rec["error"])

    def test_main_parallel_writes_one_line_per_repo(self):
        repos = [{"repo": f"r{i}-findings", "created_at": None} for i in range(5)]
        facts = {"json_records": 1, "risk": {"high": 1}, "report": {}}
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "facts.jsonl")
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(json.dumps({"repo": "r0-findings", "json_records": 1}) + "\n")
            with mock.patch.object(fetch_c4, "list_findings_repos", return_value=repos), \
                    mock.patch.object(fetch_c4, "inspect_repo", return_value=dict(facts)), \
                    mock.patch.object(fetch_c4, "fetch_readme", return_value=None):
                code = fetch_c4.main(["--out", out, "--workdir", os.path.join(tmp, "w"),
                                      "--pause", "0", "--workers", "3"])
            self.assertEqual(code, 0)
            with open(out, encoding="utf-8") as fh:
                got = [json.loads(line)["repo"] for line in fh if line.strip()]
        self.assertEqual(len(got), 5)
        self.assertEqual(sorted(got), [f"r{i}-findings" for i in range(5)])


def _records():
    return [
        {"repo": "2023-04-x-findings", "json_records": 100, "with_original_id": 0, "max_issue_id": 100,
         "submitters": 60,
         "risk": {"high": 10, "medium": 30, "qa": 50, "gas": 10, "analysis": 0, "other": 0},
         "report": {"contest": 1, "unique_high": 2, "unique_medium": 6, "wardens": 70,
                    "start": "2023-04-05", "end": "2023-04-13"},
         "readme": {"start": "2023-04-05", "end": "2023-04-15", "pot_usd": 40000.0}},
        {"repo": "2023-06-x-mitigation-findings", "json_records": 1, "risk": {"high": 1}},
        {"repo": "2024-02-y-findings", "json_records": 50, "with_original_id": 0,
         "risk": {"high": 5, "medium": 15, "qa": 30},
         "report": {"unique_high": 1, "unique_medium": 3, "start": "2024-02-01", "end": "2024-02-08"}},
        {"repo": "2024-11-z-findings", "json_records": 12, "with_original_id": 10, "max_original_issue_id": 200,
         "risk": {"high": 3, "medium": 7, "qa": 2},
         "report": {"unique_high": 6, "unique_medium": 10},
         "readme": {"start": "2024-11-11", "end": "2024-11-25"}},
        {"repo": "2022-01-bad-findings", "error": "clone failed"},
    ]


class CrowdingTest(unittest.TestCase):
    def test_enrich_rates(self):
        row = c4_crowding.enrich(_records()[0])
        self.assertEqual(row["days"], 10)
        self.assertEqual(row["date_source"], "readme")
        self.assertEqual(row["hm_subs"], 40)
        self.assertAlmostEqual(row["hm_per_day"], 4.0)
        self.assertAlmostEqual(row["hm_per_1k_usd"], 1.0)
        self.assertAlmostEqual(row["signal_rate"], 0.2)
        self.assertIsNone(c4_crowding.enrich(_records()[4]))

    def test_validated_era_has_no_rates(self):
        row = c4_crowding.enrich(_records()[3])
        self.assertEqual(row["era"], "validated")
        self.assertEqual(row["est_total_submissions"], 200)
        self.assertIsNone(row["signal_rate"])
        self.assertIsNone(row["hm_per_day"])

    def test_summary(self):
        s = c4_crowding.summary(_records())
        self.assertEqual((s["records"], s["errors"], s["rows"]), (5, 1, 4))
        self.assertEqual(s["kinds"], {"audit": 3, "mitigation": 1})
        self.assertEqual(s["full_era_audits"], 2)
        self.assertEqual(s["by_year"]["2023"]["hm_subs"], 40)
        self.assertEqual(s["by_year"]["2023"]["median_signal_rate"], 0.2)
        self.assertEqual(s["by_year"]["2024"]["median_hm_per_day"], 2.857)
        self.assertEqual(s["by_half"]["2024H1"]["audits"], 1)
        self.assertEqual(s["validated_era"]["audits"], 1)
        self.assertEqual(s["validated_era"]["median_promoted_share"], 0.06)
        self.assertEqual(s["check_2023"]["ours"]["audits"], 1)
        self.assertEqual(s["check_2023"]["ours"]["submissions"], 100)

    def test_load_skips_cut_off_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "facts.jsonl")
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(_records()[0]) + "\n")
                fh.write('{"repo": "2023-05-cut-findi')  # a write stopped mid-line
            self.assertEqual([r["repo"] for r in c4_crowding.load(src)], ["2023-04-x-findings"])

    def test_main_writes_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "facts.jsonl")
            with open(src, "w", encoding="utf-8") as fh:
                for rec in _records():
                    fh.write(json.dumps(rec) + "\n")
            out = os.path.join(tmp, "out")
            self.assertEqual(c4_crowding.main(["--in", src, "--out-dir", out]), 0)
            with open(os.path.join(out, "c4_contests.csv"), encoding="utf-8", newline="") as fh:
                rows = list(csv.DictReader(fh))
            self.assertEqual(len(rows), 4)
            self.assertNotIn("handle", rows[0])
            with open(os.path.join(out, "summary.json"), encoding="utf-8") as fh:
                self.assertEqual(json.load(fh)["full_era_audits"], 2)


if __name__ == "__main__":
    unittest.main()
