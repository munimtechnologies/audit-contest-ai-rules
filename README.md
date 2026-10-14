# Audit contest platforms: AI rules, KYC and payouts (checked 2026-10-13)

A dated, sourced snapshot of where smart-contract audit contests stand for work made with AI agents, plus a small tool (`audit_contest_feed.py`) that turns the live Sherlock contest API and this snapshot into one normalized JSON feed. Compiled by MV2 of Munim, Inc. while choosing where to take part. The research, the writing and the code were done with AI agents. Rules change, so check each source before relying on it. Corrections welcome as issues.

## Summary

| Platform | Live on 2026-10-13 | AI-made findings | KYC | Payout |
|---|---|---|---|---|
| Sherlock Audit Engine | Engagements are invite-based (handpicked); apply when applications open. Not a public listing. | **Explicitly welcome**: "AI auditors" are a participant type next to human researchers | Not stated in the public docs | USDC on Polygon (or RLUSD on XRP Ledger); needs an Issues Ratio of at least 20% and at least 2 valid findings |
| Sherlock contests (classic) | 0 active (API `status=RUNNING` returns `"total":0`) | No specific rule found | Varies | USDC |
| Cantina | 1 competition: Revert v4lend, $50k USDC, 6 Oct to 3 Nov, ~1,244 findings by 13 Oct; plus ~51 bounties | Allowed if validated: "submitting AI generated findings without validating them can lead to disqualifications or worse, a permanent ban" | Required (Persona) | USDC to an Ethereum mainnet address, paid weekly |
| HackenProof | 3 DualDefense audits ($2.5k–$3k): EverValue (ends 16 Oct), Digital Oro & DreamX (end 26 Oct) | No rule found in the docs or Code of Conduct | Only for EU tax residents, programs that require it, or after $5k in total earnings | USDC from your platform balance, 100 USDC minimum, 2FA required |
| Immunefi | 0 audit competitions or boosts live (ENS ended 8 Oct) | **Prohibited**: its terms ban "submitting AI-generated/automated scanner bug reports" | Per program | Per program |
| CodeHawks (Cyfrin) | Nothing live. BattleChain Confidence Pools (9–16 Jul 2026) was its first audit in over a year | No rule found | Per contest ("KYC Rewards" tag) | USDC on ZKsync |
| Code4rena | Winding down since 13 May 2026; Immunefi took over its clients | n/a | n/a | n/a |

## Notes

- **Duplicates.** Cantina: points = full / (1 + 0.8 × (n − 1)), with High 10 and Medium 3. CodeHawks: High = 5 × 0.9^(n−1) / n, Medium = 0.9^(n−1) / n.
- **Coded PoCs.** Cantina requires a compiling coded PoC for every High and Medium before the end of a competition, for researchers with reputation below 80. HackenProof DualDefense needs a runnable PoC in the first submission (later PoCs are not accepted) and pays for Criticals only.
- **Sherlock Audit Engine — how it works.** Launched publicly on 18 Aug 2026. Participation is invite-based: Sherlock specialists handpick candidates and top researchers may be contacted directly; otherwise you apply when applications open, then "commit or decline" an engagement card. An NDA and Engagement Addendum are signed per engagement before it begins. You can import a past Sherlock Audit Contests account at signup to carry over an Issues Ratio (it cannot be linked later). An AI judge gives feedback, often within minutes.
  - **Issues Ratio** (public docs): accepted ÷ total submitted. Accepted counts +1/1, Dismissed +0/1, Neutral is excluded. "Rewrite and Resubmit" adds +0.5 to the denominator each time (and +0.5 to the numerator if accepted), commonly up to 5 rewrites per issue chain. No payout below a 20% ratio, and you need at least 2 valid findings across all engagements.
  - **Credits** (shown on the signup dashboard, Aug 2026): a valid finding earns +4 and an invalid one costs −1; if credits drop below 0, payouts lock. When an engagement closes, 20% of its findings are counted right away. An engagement that earns more credits than it burns pays out on its own; one that burns more is held, and releasing it costs credits. The public Issues Ratio counts every finding, held or not.
- **HackenProof.** Its Code of Conduct bans "sharing account access, submitting other hackers' work". Submit only your own work, from your own account.

## Tool: `audit_contest_feed.py`

A dependency-free (Python 3.8+) helper that produces one normalized JSON list of audit contests:

```
python audit_contest_feed.py            # live Sherlock classic API + this dated snapshot
python audit_contest_feed.py --offline  # only the dated snapshot, no network
python audit_contest_feed.py --no-fee --ai-ok   # drop fee-gated and AI-hostile platforms
```

Each record has `platform`, `name`, `status`, `prize_usd`, `ends`, `url`, `ai_findings`, `kyc`, `payout`, `source`. The snapshot rows are dated and marked `"source": "snapshot:2026-10-13"`; the Sherlock classic rows come live from the API and are marked `"source": "sherlock-api"`. Run tests with `python -m pytest test_audit_contest_feed.py` (no network needed).

## Sources

- Cantina competitions: https://cantina.xyz/competitions
- Cantina severity and AI rule: https://docs.cantina.security/standards/severity/competition
- Cantina KYC and payments: https://docs.cantina.xyz/for-security-researchers/joining-cantina/kyc and https://docs.cantina.security/researchers/joining/payout-schedule
- Sherlock Audit Engine for participants: https://docs.sherlock.xyz/audit-engine/for-participants
- Sherlock Audit Engine overview: https://docs.sherlock.xyz/audit-engine/about-audit-engine
- Sherlock Audit Engine launch: https://chainwire.org/2026/08/18/sherlock-unveils-audit-engine-as-ai-security-race-accelerates/
- Sherlock contests API: https://mainnet-contest.sherlock.xyz/contests?status=RUNNING
- HackenProof audit programs: https://hackenproof.com/audit-programs
- HackenProof KYC: https://docs.hackenproof.com/dashboard/hacker-dashboard/kyc.md
- HackenProof withdrawals: https://docs.hackenproof.com/dashboard/hacker-dashboard/withdraw-bounty.md
- HackenProof DualDefense rules: https://docs.hackenproof.com/dualdefense-audit/general-guidelines.md
- HackenProof Code of Conduct: https://docs.hackenproof.com/welcome/code-of-conduct.md
- Immunefi audit competitions: https://immunefi.com/audit-competition/
- Immunefi rules: https://immunefi.com/rules/
- CodeHawks payouts: https://docs.codehawks.com/judging/payouts-and-rewards
- Code4rena wind-down: https://coinalertnews.com/news/2026/05/13/code4rena-shutdown-immunefi-takeover
- Contest calendar: https://bbradar.io/contests

MIT licensed. MV2 of Munim, Inc. (munimversion2@gmail.com).
