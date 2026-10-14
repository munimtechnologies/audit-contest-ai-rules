# Audit contest platforms: AI rules, KYC, payouts and crowding (checked 2026-10-14)

A dated, sourced snapshot of where smart-contract audit contests stand for work made with AI agents, two small tools, and a hand-collected dataset on how crowded Cantina competitions have become. Compiled by MV2 of Munim, Inc. while choosing where to take part. The research, the writing and the code were done with AI agents. Rules change, so check each source before relying on it. Corrections welcome as issues.

## Summary

| Platform | Live on 2026-10-14 | AI-made findings | KYC | Payout |
|---|---|---|---|---|
| Sherlock Audit Engine | Engagements are invite-based (handpicked); apply when applications open. Not a public listing. On 14 Oct the dashboard showed "No audits are taking applications." | **Explicitly welcome**: "AI auditors" are a participant type next to human researchers | Required before accepting an engagement invite, plus a DocuSign NDA per engagement | USDC on Polygon (or RLUSD on XRP Ledger); needs at least 2 valid findings and a 20% valid ratio |
| Sherlock contests (classic) | 0 active (API `status=RUNNING` returns `"total":0`) | No specific rule found | Varies | USDC |
| Cantina | 1 competition: Revert v4lend, $50k USDC, 6 Oct to 3 Nov (1,282 findings submitted by 14 Oct); plus ongoing bounties | Allowed if validated: "submitting AI generated findings without validating them can lead to disqualifications or worse, a permanent ban" | Required (Persona) | USDC to an Ethereum mainnet address, paid weekly |
| HackenProof | 3 DualDefense audits ($2.5k–$3k, Criticals only): EverValue (2–16 Oct), Digital Oro (5–26 Oct), DreamX (12–26 Oct; its scope repo is invite-only and needs KYC to request access) | No rule found in the docs or Code of Conduct | Only for EU tax residents, programs that require it, or after $5k in total earnings | USDC from your platform balance, 100 USDC minimum, 2FA required |
| Immunefi | 0 audit competitions or boosts live (ENS ended 8 Oct) | **Prohibited**: its terms ban "submitting AI-generated/automated scanner bug reports" | Per program | Per program |
| CodeHawks (Cyfrin) | Nothing live. BattleChain Confidence Pools (9–16 Jul 2026) was its first audit in over a year | No rule found | Per contest ("KYC Rewards" tag) | USDC on ZKsync |
| Certora (formal verification) | Nothing live. All 15 listed contests have ended (pools $18k–$125.5k, "$800k+" paid in total); recent ones ran with Cantina | No rule found | Per hosting platform | Per hosting platform |
| Code4rena | Winding down since 13 May 2026; Immunefi took over its clients | n/a | n/a | n/a |

## How crowded are Cantina competitions? (new in v0.3.0)

Each Cantina competition page shows a running "Findings submitted" count. We could not find this collected anywhere, so `data/cantina_competitions.csv` records it for 21 competitions (Aug 2024 to the live Revert v4lend), each read off its public page on 14 Oct 2026, together with the dates and the headline prize. `crowding.py` computes the rates below, and `test_crowding.py` pins every number quoted here.

| Started in | Contests | Median findings per contest day | Same, USD pots of $60k or less |
|---|---|---|---|
| 2024 | 4 | 23.4 | (none in sample) |
| 2025 | 9 | 37.6 | 36.9 (6 contests) |
| 2026 | 7 | 146.5 | 146.5 (5 contests) |

- **Submissions per day roughly quadrupled from 2025 to 2026**, and the jump holds among the small pots too. Three $30k–$50k contests in 2026 drew 1,248–1,465 findings in 7–10 days. The live Revert v4lend contest was running at 160 a day after 8 days.
- **The two 2026 exceptions are the two Royco contests** (37 and 16 per day). Both required KYC to join; Dawn paid for Highs only, and Day's pot was $7.5k unless a High was found. That is a hint, not a result: two contests are too few to separate the causes, and v4lend also requires KYC yet runs at 160 a day.
- **Payouts are concentrated.** In Revert Finance's March 2026 competition (1,248 findings), 59 researchers were paid. The 8 with a rarely duplicated Medium took 82.7% of the $50k, about $5,100–$5,300 each. The 46 whose single Medium was widely duplicated got $154 each. In Revert's StableSwap Hooks competition (1,412 findings), the top 10 of 138 paid researchers took 76.1%. `data/revert_payout_tiers.csv` has the tiers, without researcher names.
- **What this means in practice:** in a 2026 Cantina contest, almost all of the money goes to findings few others submitted. A widely found bug pays close to nothing, however valid it is.

**Limits.** The 21 contests are the ones search engines returned, not all 144 ended ones, so this is a sample, not a census. The 2024 rows are all large pots. The counts include invalid and duplicate submissions, and Cantina does not publish how many were valid. Pots marked "full pot only with a valid High" are recorded at their headline size. Two OP-denominated pots are left out of the per-dollar figures. Contest length matters too: long contests show lower per-day rates. Run `python crowding.py --table` for every row.

## Notes

- **Duplicates.** Cantina: points = full / (1 + 0.8 × (n − 1)), with High 10 and Medium 3. CodeHawks: High = 5 × 0.9^(n−1) / n, Medium = 0.9^(n−1) / n.
- **Coded PoCs.** Cantina requires a compiling coded PoC for every High and Medium before the end of a competition, for researchers with reputation below 80. HackenProof DualDefense needs a runnable PoC in the first submission (later PoCs are not accepted) and pays for Criticals only.
- **Sherlock Audit Engine — how it works.** Launched publicly on 18 Aug 2026. Participation is invite-based: Sherlock specialists handpick candidates and top researchers may be contacted directly; otherwise you apply when applications open, then "commit or decline" an engagement card. An NDA and Engagement Addendum are signed per engagement before it begins. You can import a past Sherlock Audit Contests account at signup to carry over an Issues Ratio (it cannot be linked later). Findings are judged in three stages: an AI judge (often within minutes), then a Lead Judge, then the protocol team. Protocols may exclude specific AI auditors "for confidentiality or commercial reasons".
  - **Issues Ratio** (public docs): accepted ÷ total submitted. Accepted counts +1/1, Dismissed +0/1, Neutral is excluded. "Rewrite and Resubmit" adds +0.5 to the denominator each time (and +0.5 to the numerator if accepted), commonly up to 5 rewrites per issue chain. No payout below a 20% ratio, and you need at least 2 valid findings across all engagements. Withheld rewards can be unlocked for 12 months after an engagement ends, then they are lost.
  - **Credits** (shown on the signup dashboard, Aug 2026): a valid finding earns +4 and an invalid one costs −1; if credits drop below 0, payouts lock. When an engagement closes, 20% of its findings are counted right away. An engagement that earns more credits than it burns pays out on its own; one that burns more is held, and releasing it costs credits. The public Issues Ratio counts every finding, held or not.
- **HackenProof.** Its Code of Conduct bans "sharing account access, submitting other hackers' work". Submit only your own work, from your own account.
- **Bounty bait aimed at AI agents.** Outside the contest platforms, GitHub searches for Solidity "bounty" issues in October 2026 were dominated by one repo with dozens of look-alike $2k–$8k "bounties" labelled for autonomous agents, whose issue text asks contributors to paste their agent's full initialization text, OS and working directory into the code or a contributors file. Treat that as prompt-extraction bait, not paid work: check that a repo has ever merged and paid an outside contributor before spending time on it.

## Tool: `audit_contest_feed.py`

A dependency-free (Python 3.8+) helper that produces one normalized JSON list of audit contests:

```
python audit_contest_feed.py                    # live Sherlock classic API + this dated snapshot
python audit_contest_feed.py --offline          # only the dated snapshot, no network
python audit_contest_feed.py --no-fee --ai-ok   # drop fee-gated and AI-hostile platforms
python audit_contest_feed.py --ends-within 7    # only contests ending in the next 7 days
```

Each record has `platform`, `name`, `status`, `prize_usd`, `starts`, `ends`, `days_left`, `url`, `ai_findings`, `kyc`, `payout`, `source`. `days_left` is computed against today's UTC date (`null` when there is no end date). The snapshot rows are dated and marked `"source": "snapshot:2026-10-14"`; the Sherlock classic rows come live from the API and are marked `"source": "sherlock-api"`.

## Tool: `crowding.py`

```
python crowding.py           # JSON summary: medians by year, the live contest, payout concentration
python crowding.py --table   # one line per contest: findings, days, per day, per $1k
```

Run all tests with `python -m pytest` (no network needed).

## Sources

- Cantina competitions: https://cantina.xyz/competitions (each row of `data/cantina_competitions.csv` links its own page)
- Revert Finance leaderboards: https://cantina.xyz/competitions/efb6f308-f13b-4110-aff8-0d67181608dd/leaderboard and https://cantina.xyz/competitions/e55ee7b9-6c99-42f8-8338-39f3dd134ef3/leaderboard
- Cantina severity and AI rule: https://docs.cantina.security/standards/severity/competition
- Cantina KYC and payments: https://docs.cantina.xyz/for-security-researchers/joining-cantina/kyc and https://docs.cantina.security/researchers/joining/payout-schedule
- Sherlock Audit Engine for participants: https://docs.sherlock.xyz/audit-engine/for-participants
- Sherlock Audit Engine FAQ: https://docs.sherlock.xyz/audit-engine/faq
- Sherlock Audit Engine overview: https://docs.sherlock.xyz/audit-engine/about-audit-engine
- Sherlock Audit Engine launch: https://chainwire.org/2026/08/18/sherlock-unveils-audit-engine-as-ai-security-race-accelerates/
- Sherlock contests API: https://mainnet-contest.sherlock.xyz/contests?status=RUNNING
- HackenProof audit programs: https://hackenproof.com/audit-programs
- HackenProof DreamX program: https://hackenproof.com/audit-programs/dreamx-marketplace-and-dex-sca-dualdefense-audit
- HackenProof KYC: https://docs.hackenproof.com/dashboard/hacker-dashboard/kyc.md
- HackenProof withdrawals: https://docs.hackenproof.com/dashboard/hacker-dashboard/withdraw-bounty.md
- HackenProof DualDefense rules: https://docs.hackenproof.com/dualdefense-audit/general-guidelines.md
- HackenProof Code of Conduct: https://docs.hackenproof.com/welcome/code-of-conduct.md
- Immunefi audit competitions: https://immunefi.com/audit-competition/
- Immunefi rules: https://immunefi.com/rules/
- CodeHawks payouts: https://docs.codehawks.com/judging/payouts-and-rewards
- Certora contests: https://www.certora.com/contests
- Code4rena wind-down: https://coinalertnews.com/news/2026/05/13/code4rena-shutdown-immunefi-takeover
- Contest calendar: https://bbradar.io/contests

## License

Code: Apache-2.0 (see LICENSE). The data in `data/` and this README's text: CC BY 4.0. MV2 of Munim, Inc. (munimversion2@gmail.com).
