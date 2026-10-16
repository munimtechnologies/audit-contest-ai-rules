"""Offline tests for fetch_immunefi.py (no network). Apache-2.0.
Made with AI agents working for MV2 of Munim, Inc."""
import json
import os
import tempfile
import unittest

import fetch_immunefi as fi

LISTING = """<html><body>
<a href="/audit-competition/audit-competition-ens/information/">Audit Competition | ENS</a>
<a href="/audit-competition/audit-competition-ens/">View results</a>
<a href="https://immunefi.com/audit-competition/firedancer-v1-audit-comp/">View results</a>
<a href="/audit-competition/xrpl-ripple-attackathon/information/">Attackathon | XRPL</a>
<a href="/audit-competition/findings/">View all Findings</a>
<a href="/bug-bounty/ens/">not a competition</a>
</body></html>"""

INFO_ENS = """<html><head><title>ENS Audit Competition | Immunefi</title>
<script>self.__next_f.push([1,"Start Date 01 January 2020"])</script></head><body>
<h1>Audit Competition | ENS</h1><span>Finished</span>
<div><p>Start Date</p><p>18 August 2026</p></div>
<div><p>End Date</p><p>14<!-- --> September 2026</p></div>
<div><p>Primary Pool</p><p>$49,000</p></div>
<div><p>All Stars Pool</p><p>$14,000</p></div>
<div><p>Podium Pool</p><p>$7,000</p></div>
<div><p>Rewards Token</p><p>USDC</p></div>
<div><p>Lines of Code</p><p>137,845</p></div>
<div><p>Total Assets in Scope</p><p>5</p></div>
<p>If no bugs are found, the reward pool is $3k USD.</p>
<li>Proof of concept is always required for all severities</li>
<li>Reports generated with AI tools without verification will be closed.</li>
</body></html>"""

INFO_ATTACK = """<html><body><h1>Attackathon | XRPL Lending Protocol</h1>
<p>Start Date</p><p>26 Jan 2026</p><p>End Date</p><p>23 Feb 2026</p>
<p>Reward Pool</p><p>$200,000</p></body></html>"""

RESULTS = """<html><body><table>
<tr><td>#<!-- -->1</td><td>alice</td><td>$8,013</td></tr>
<tr><td>#<!-- -->2</td><td>bob</td><td>$6,461</td></tr>
<tr><td>#3</td><td>carol</td><td>$0</td></tr>
</table></body></html>"""

# Pre-mid-2025 style: bare rank, handle, earnings, then counts (valid, critical, high, med/low, insights).
RESULTS_BARE = """<html><body><table>
<tr><td>1</td><td><img src="a.png"/></td><td>dave</td><td>$900</td><td>3</td><td>0</td><td>2</td><td>1</td><td>0</td></tr>
<tr><td>2</td><td>erin</td><td>$450</td><td>2</td><td>0</td><td>1</td><td>1</td><td>0</td></tr>
<tr><td>3</td><td>frank</td><td>-</td><td>1</td><td>0</td><td>0</td><td>1</td><td>0</td></tr>
</table><footer>2026 Immunefi</footer></body></html>"""

# Medal icons for the top three, bare ranks from 4.
RESULTS_MEDALS = """<table>
<tr><td><img alt="gold"/></td><td>gina</td><td>$5</td><td>1</td></tr>
<tr><td><img alt="silver"/></td><td>hank</td><td>$4</td><td>1</td></tr>
<tr><td><img alt="bronze"/></td><td>ivy</td><td>$3</td><td>1</td></tr>
<tr><td>4</td><td>jon</td><td>$2</td><td>1</td></tr>
<tr><td>5</td><td>kim</td><td>$1</td><td>1</td></tr>
<tr><td>6</td><td>lee</td><td>$1</td><td>1</td></tr>
</table>"""


class ParseTests(unittest.TestCase):
    def test_listing_slugs_dedupes_and_skips_non_competitions(self):
        self.assertEqual(fi.listing_slugs(LISTING),
                         ["audit-competition-ens", "firedancer-v1-audit-comp", "xrpl-ripple-attackathon"])

    def test_information_page_facts(self):
        info = fi.parse_information(INFO_ENS, "audit-competition-ens")
        self.assertEqual(info["start"], "2026-08-18")   # the script's 2020 date is ignored
        self.assertEqual(info["end"], "2026-09-14")     # React comment split is joined
        self.assertEqual(info["pool_usd"], 70000.0)     # 49k + 14k + 7k
        self.assertEqual(info["token"], "USDC")
        self.assertEqual(info["lines_of_code"], 137845)
        self.assertEqual(info["assets_in_scope"], 5)
        self.assertTrue(info["poc_required"])
        self.assertEqual(info["kind"], "audit_comp")
        self.assertEqual(info["ai_mentions"], 1)
        self.assertIn("AI tools", info["ai_lines"][0])

    def test_attackathon_uses_reward_pool_and_short_month(self):
        info = fi.parse_information(INFO_ATTACK, "xrpl-ripple-attackathon")
        self.assertEqual(info["kind"], "attackathon")
        self.assertEqual((info["start"], info["end"]), ("2026-01-26", "2026-02-23"))
        self.assertEqual(info["pool_usd"], 200000.0)
        self.assertEqual(info["ai_mentions"], 0)
        self.assertFalse(info["poc_required"])

    def test_kind_falls_back_to_slug(self):
        self.assertEqual(fi.kind_of("lido-v3-bug-bounty-comp", []), "bug_bounty_comp")
        self.assertEqual(fi.kind_of("flare-fassets-mitigation-audit", []), "mitigation_audit")
        self.assertEqual(fi.kind_of("iop-paradex", []), "iop")
        self.assertEqual(fi.kind_of("belong-audit-comp", []), "audit_comp")

    def test_results_leaderboard_size(self):
        self.assertEqual(fi.parse_results(RESULTS),
                         {"present": True, "max_rank": 3, "ranks_seen": 3, "rank_method": "hash"})
        sparse = "<p>#1</p><p>#40</p>"
        self.assertIsNone(fi.parse_results(sparse)["max_rank"])
        self.assertIsNone(fi.parse_results(sparse)["rank_method"])
        self.assertEqual(fi.parse_results(None), {"present": False})

    def test_bare_number_leaderboard(self):
        res = fi.parse_results(RESULTS_BARE)
        self.assertEqual((res["max_rank"], res["rank_method"]), (3, "bare"))
        # rank cells 1, 2, 3 and the last insights cell before the footer
        self.assertEqual(fi.bare_rank_candidates(fi.html_to_lines(RESULTS_BARE)), [1, 2, 3, 0])

    def test_medal_top_three_then_bare_ranks(self):
        # the count cells of rows 1-2 sit before a handle, so they are candidates too
        self.assertEqual(fi.bare_rank_candidates(fi.html_to_lines(RESULTS_MEDALS)), [1, 1, 4, 5, 6])
        self.assertEqual(fi.parse_results(RESULTS_MEDALS)["max_rank"], 6)

    def test_short_walk_is_not_a_leaderboard(self):
        self.assertEqual(fi.bare_rank_top(["1", "x", "2", "y"]), (None, 2))

    def test_row_shape_keeps_no_handles(self):
        shape = fi.line_shape(fi.html_to_lines(RESULTS_BARE), limit=10)
        self.assertEqual(shape, "1 T $ 3 0 2 1 0 2 T")
        self.assertEqual(fi.line_shape(["no", "numbers"]), "")

    def test_missing_page(self):
        self.assertEqual(fi.parse_information(None), {"present": False})
        rec = fi.competition_facts("x", {"information": None, "results": None})
        self.assertFalse(rec["is_competition"])

    def test_half_year_and_rows(self):
        self.assertEqual(fi.half_year("2026-04-09"), "2026H1")
        self.assertEqual(fi.half_year("2026-07-01"), "2026H2")
        self.assertIsNone(fi.half_year(None))
        rec = fi.competition_facts("audit-competition-ens", {"information": INFO_ENS, "results": RESULTS})
        row = fi.contest_row(rec)
        self.assertEqual((row["start_half"], row["days"], row["ranked_whitehats"], row["rank_method"]),
                         ("2026H2", 27, 3, "hash"))

    def test_by_half_counts(self):
        rows = [
            {"start_half": "2026H1", "kind": "audit_comp", "pool_usd": 100.0, "ranked_whitehats": 10},
            {"start_half": "2026H1", "kind": "attackathon", "pool_usd": 50.0, "ranked_whitehats": 30},
            {"start_half": "2026H2", "kind": "iop", "pool_usd": None, "ranked_whitehats": None},
            {"start_half": None, "kind": "audit_comp", "pool_usd": 1.0, "ranked_whitehats": 1},
        ]
        halves = fi.by_half(rows)
        self.assertEqual([h["half"] for h in halves], ["2026H1", "2026H2"])
        self.assertEqual((halves[0]["competitions"], halves[0]["audit_type"], halves[0]["pool_usd"]), (2, 1, 150.0))
        self.assertEqual(halves[0]["median_ranked_whitehats"], 20)
        self.assertEqual((halves[0]["ranked_n"], halves[0]["median_ranked_audit_type"]), (2, 10))
        self.assertEqual((halves[1]["audit_type"], halves[1]["median_ranked_whitehats"]), (1, None))
        self.assertIn("| 2026H1 | 2 | 1 | 150 | 20 | 2 | 10 |", fi.render_md(rows[:3], halves, "2026-10-15T00:00Z"))


class OfflineMainTest(unittest.TestCase):
    def test_parse_only_end_to_end_keeps_no_handles(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = os.path.join(tmp, "data", "raw")
            pages = {"_listing.html": LISTING,
                     "audit-competition-ens/information.html": INFO_ENS,
                     "audit-competition-ens/results.html": RESULTS,
                     "xrpl-ripple-attackathon/information.html": INFO_ATTACK,
                     "xrpl-ripple-attackathon/results.html": RESULTS_BARE}
            for name, body in pages.items():
                path = os.path.join(raw, name)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(body)
            out = os.path.join(tmp, "out")
            code = fi.main(["--data-dir", os.path.join(tmp, "data"), "--out-dir", out,
                            "--samples-dir", os.path.join(out, "samples"), "--parse-only",
                            "--fetched-on", "2026-10-15T19:33Z"])
            self.assertEqual(code, 0)
            with open(os.path.join(out, "immunefi_summary.json"), encoding="utf-8") as fh:
                summary = json.load(fh)
            self.assertEqual((summary["slugs"], summary["competitions"]), (3, 2))
            self.assertEqual(summary["not_competitions"], ["firedancer-v1-audit-comp"])
            self.assertEqual([h["half"] for h in summary["by_half"]], ["2026H1", "2026H2"])
            self.assertEqual(summary["rank_methods"], {"hash": 1, "bare": 1, "none": 0})
            self.assertEqual(summary["fetched_on"], "2026-10-15T19:33Z")
            written = ""
            for root, _dirs, files in os.walk(out):
                for name in files:
                    with open(os.path.join(root, name), encoding="utf-8") as fh:
                        written += fh.read()
            for handle in ("alice", "bob", "carol", "dave", "erin", "frank", "$8,013", "$900"):
                self.assertNotIn(handle, written)


if __name__ == "__main__":
    unittest.main()
