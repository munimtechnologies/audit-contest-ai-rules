"""Offline tests for fetch_c4_readmes.py and c4_sections.py (no network). Apache-2.0.
Made with AI agents working for MV2 of Munim, Inc."""
import json
import os
import tempfile
import unittest

import c4_sections as cs
import fetch_c4_readmes as fc

# Shortened from the real READMEs (wording of the lines the parser keys on kept as published).
HYBRA = """# Hybra Finance audit details
- Total Prize Pool: $33,000 in USDC
- Starts October 6, 2025 20:00 UTC
- Ends October 16, 2025 20:00 UTC

## V12 findings

[V12](https://v12.zellic.io/) is [Zellic](https://zellic.io)'s in-house AI auditing tool.

## Publicly known issues

... due to the fact that both projects utilize distinct `pragma` versions.

| [ve33/contracts/GaugeV2.sol](https://github.com/code-423n4/2025-10-hybra-finance/blob/main/ve33/contracts/GaugeV2.sol) | 300 |
"""

CHAINLINK = """# Chainlink Payment Abstraction V2 audit details
| AUCTION_WORKER_ROLE | Starts and expires auctions by calling performUpkeep. |
- Starts March 18, 2026 20:00 UTC
- Ends March 27, 2026 20:00 UTC
## V12 findings
| [src/Auction.sol](https://example.invalid/src/Auction.sol) |
"""

FRANKENCOIN = """# Frankencoin contest details
- Starts April 12, 2023 20:00 UTC
- Ends April 17, 2023 20:00 UTC

## Automated Findings / Publicly Known Issues

Automated findings output for the contest can be found [here](https://gist.example.invalid/x) within an hour of contest opening.

You'll find the most important links & communication channels at the bottom.
| [contracts/Frankencoin.sol](contracts/Frankencoin.sol) | 120 |
"""

SECONDSWAP = """# SecondSwap audit details
- Starts December 9, 2024 20:00 UTC
- Ends December 19, 2024 20:00 UTC

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://github.com/code-423n4/2024-12-secondswap/blob/main/4naly3er-report.md).
| [contracts/SecondSwap_Marketplace.sol](contracts/SecondSwap_Marketplace.sol) | 300 |
"""

BOTRACE = """# Some audit details
- Starts August 1, 2023 20:00 UTC
## Automated Findings / Publicly Known Issues
The [winning bot race report](https://example.invalid/bot.md) was submitted by a bot crew.
| src/Vault.sol | 100 |
"""

MOVE = """# A Sui audit
- Starts September 20, 2025 20:00 UTC
| sources/endpoint.move | 900 |
"""


def rec(repo, text, fetched_on="2026-10-19T18:30Z"):
    return {"repo": repo, "kind": fc.repo_kind(repo), "name_month": fc.name_month(repo),
            "created_at": None, "archived": False, "fetched_on": fetched_on,
            "readme": fc.parse_readme(text)}


class RepoNameTests(unittest.TestCase):
    def test_audit_repos_only(self):
        self.assertTrue(fc.is_audit_repo("2025-10-hybra-finance"))
        self.assertTrue(fc.is_audit_repo("2026-03-swafe-mitigation-round2"))
        self.assertFalse(fc.is_audit_repo("2025-10-hybra-finance-findings"))
        self.assertFalse(fc.is_audit_repo("Kite-AI-bug-bounty"))
        self.assertFalse(fc.is_audit_repo("succinct-bug-bounty-submissions-tmp-1777660924"))
        self.assertFalse(fc.is_audit_repo("2025-13-nothing"))
        self.assertFalse(fc.is_audit_repo(None))

    def test_kind_and_month(self):
        self.assertEqual(fc.repo_kind("2026-03-swafe-mitigation"), "mitigation")
        self.assertEqual(fc.repo_kind("2026-03-chainlink"), "audit")
        self.assertEqual(fc.name_month("2025-10-hybra-finance"), "2025-10")
        self.assertIsNone(fc.name_month("Kite-AI-bug-bounty"))


class ParseReadmeTests(unittest.TestCase):
    def test_hybra(self):
        r = fc.parse_readme(HYBRA)
        self.assertEqual((r["start"], r["end"]), ("2025-10-06", "2025-10-16"))
        self.assertTrue(r["v12"] and r["v12_heading"] and r["solidity"])
        self.assertFalse(r["bot_words"])          # "both" and "bottom" are not bot phrases
        self.assertFalse(r["auto_heading"])
        self.assertEqual(r["exts"], ["sol"])

    def test_start_skips_prose_that_is_not_a_date(self):
        r = fc.parse_readme(CHAINLINK)
        self.assertEqual(r["start"], "2026-03-18")
        self.assertTrue(r["v12"])

    def test_frankencoin_and_secondswap(self):
        f = fc.parse_readme(FRANKENCOIN)
        self.assertTrue(f["auto_heading"] and f["auto_output"])
        self.assertFalse(f["bot_words"] or f["analyzer_4naly3er"] or f["v12"])
        s = fc.parse_readme(SECONDSWAP)
        self.assertTrue(s["auto_heading"] and s["analyzer_4naly3er"])
        self.assertEqual(s["start"], "2024-12-09")

    def test_bot_race_and_move(self):
        self.assertTrue(fc.parse_readme(BOTRACE)["bot_words"])
        m = fc.parse_readme(MOVE)
        self.assertEqual(m["exts"], ["move"])
        self.assertFalse(m["solidity"])

    def test_missing_readme_and_no_text_kept(self):
        self.assertEqual(fc.parse_readme(None), {"present": False})
        r = fc.parse_readme(HYBRA)
        self.assertNotIn("Hybra", json.dumps(r))   # flags and a hash only, never README text
        self.assertEqual(len(r["sha256"]), 64)


class ScoringTests(unittest.TestCase):
    def test_after_uses_month_when_undated(self):
        self.assertTrue(cs.after({"start": "2024-07-01"}, cs.P1_LAST))
        self.assertFalse(cs.after({"start": "2024-06-30"}, cs.P1_LAST))
        self.assertTrue(cs.after({"start": None, "name_month": "2024-08"}, cs.P1_LAST))
        self.assertFalse(cs.after({"start": None, "name_month": "2024-06"}, cs.P1_LAST))
        self.assertIsNone(cs.after({"start": None, "name_month": "2025-10"}, cs.P2_FROM))

    def test_verdicts(self):
        records = [rec("2023-04-frankencoin", FRANKENCOIN), rec("2023-08-some", BOTRACE),
                   rec("2024-12-secondswap", SECONDSWAP), rec("2025-10-hybra-finance", HYBRA),
                   rec("2026-03-chainlink", CHAINLINK), rec("2025-09-sui-endpoint", MOVE),
                   rec("2026-03-swafe-mitigation", HYBRA.replace("V12", "Vx"))]
        s = cs.summarize(records)
        self.assertEqual((s["audits"], s["mitigations"]), (6, 1))
        p1 = s["p1_as_written"]
        self.assertEqual(p1["verdict"], "CONTRADICTED")
        self.assertEqual(p1["after_2024_06_30"], ["2024-12-secondswap"])
        self.assertTrue(p1["first_is_frankencoin"])
        ph = s["p1_post_hoc_bot_race"]
        self.assertEqual(ph["verdict"], "HOLDS")      # Frankencoin (output phrase) + the bot-race audit
        self.assertEqual(ph["audits_marked"], 2)
        p2 = s["p2_v12"]
        self.assertEqual(p2["verdict"], "HOLDS")      # the mitigation without V12 is left out
        self.assertEqual(p2["solidity_audits_from_2025_10_06"], 2)
        self.assertTrue(all(v["ok"] for v in s["known_answer_checks"].values()))

    def test_solidity_audit_without_v12_contradicts(self):
        s = cs.summarize([rec("2025-11-plain", HYBRA.replace("V12", "Vx").replace("October 6", "November 3"))])
        self.assertEqual(s["p2_v12"]["verdict"], "CONTRADICTED")
        self.assertEqual(s["p2_v12"]["without_v12"], ["2025-11-plain"])

    def test_main_writes_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "facts.jsonl")
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(json.dumps({"repo": "2025-10-hybra-finance", "error": "boom"}) + "\n")
                fh.write(json.dumps(rec("2025-10-hybra-finance", HYBRA)) + "\n")
                fh.write("{cut off\n")
            out = os.path.join(tmp, "out")
            self.assertEqual(cs.main(["--in", src, "--out-dir", out]), 0)
            with open(os.path.join(out, "c4_sections_summary.json"), encoding="utf-8") as fh:
                j = json.load(fh)
            with open(os.path.join(out, "C4_SECTIONS.md"), encoding="utf-8") as fh:
                md = fh.read()
            with open(os.path.join(out, "c4_readme_sections.csv"), encoding="utf-8") as fh:
                csv_lines = fh.read().splitlines()
        self.assertEqual((j["repositories"], j["errors"]), (1, 0))   # the good line replaced the error
        self.assertIn("## P2 (every Solidity audit from 6 Oct 2025 on has a V12 section)", md)
        self.assertIn("POST HOC", md)
        self.assertEqual(len(csv_lines), 2)
        self.assertTrue(csv_lines[1].startswith("2025-10-hybra-finance,audit,2025-10-06,readme,2025H2,"))


if __name__ == "__main__":
    unittest.main()
