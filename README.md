# Audit contest platforms: AI rules, KYC, payouts and crowding (checked 2026-10-14)

A dated, sourced snapshot of where smart-contract audit contests stand for work made with AI agents, a few small tools, and open datasets on how crowded audit contests have become: a census of every public Sherlock contest, a census of every public Cantina competition, and a combined series built from the two. Compiled by MV2 of Munim, Inc. while choosing where to take part. The research, the writing and the code were done with AI agents. Rules change, so check each source before relying on it. Corrections welcome as issues.

## Summary

| Platform | Live on 2026-10-14 | AI-made findings | KYC | Payout |
|---|---|---|---|---|
| Sherlock Audit Engine | Engagements are invite-based (handpicked); apply when applications open. Not a public listing. On 14 Oct the dashboard showed "No audits are taking applications." | **Explicitly welcome**: "AI auditors" are a participant type next to human researchers | Required before accepting an engagement invite, plus a DocuSign NDA per engagement | USDC on Polygon (or RLUSD on XRP Ledger); needs at least 2 valid findings and a 20% valid ratio |
| Sherlock contests (classic) | 0 active (API `status=RUNNING` returns `"total":0`). The last public contest in the API started on 20 Jul 2026 | No specific rule found | Required in 8 of the 9 contests that started in 2026 | USDC |
| Cantina | 1 competition: Revert v4lend, $50k USDC, 6 Oct to 3 Nov (1,369 findings submitted by 14 Oct 20:03 UTC); plus ongoing bounties | Allowed if validated: "submitting AI generated findings without validating them can lead to disqualifications or worse, a permanent ban" | Required (Persona) | USDC to an Ethereum mainnet address, paid weekly |
| HackenProof | 3 DualDefense audits ($2.5k–$3k, Criticals only): EverValue (2–16 Oct), Digital Oro (5–26 Oct), DreamX (12–26 Oct; its scope repo is invite-only and needs KYC to request access) | No rule found in the docs or Code of Conduct | Only for EU tax residents, programs that require it, or after $5k in total earnings | USDC from your platform balance, 100 USDC minimum, 2FA required |
| Immunefi | 0 audit competitions or boosts live (ENS ended 8 Oct) | **Prohibited**: its terms ban "submitting AI-generated/automated scanner bug reports" | Per program | Per program |
| CodeHawks (Cyfrin) | Nothing live. BattleChain Confidence Pools (9–16 Jul 2026) was its first audit in over a year | No rule found | Per contest ("KYC Rewards" tag) | USDC on ZKsync |
| Certora (formal verification) | Nothing live. All 15 listed contests have ended (pools $18k–$125.5k, "$800k+" paid in total); recent ones ran with Cantina | No rule found | Per hosting platform | Per hosting platform |
| Code4rena | Winding down since 13 May 2026; Immunefi took over its clients | n/a | n/a | n/a |

## Fewer contests, not fewer submissions: Sherlock and Cantina together (new in v0.5.0)

`cross_platform.py` adds the two censuses below together by the quarter, half-year and year in which each contest started. It counts every finished public contest that has a submission count on either platform: 259 on Sherlock and 114 on Cantina. The 12 Ethereum client competitions of February 2025 shared one $2M pot, so they count as one contest here. `test_cross_platform.py` pins every number in this section to the files in `data/`.

| Started in | Sherlock contests | Sherlock submissions | Cantina contests | Cantina submissions | **Contests** | **Submissions** | **Per contest** |
|---|---|---|---|---|---|---|---|
| 2024 H1 | 59 | 9,768 | 17 | 6,019 | **76** | **15,787** | **208** |
| 2024 H2 | 43 | 13,461 | 26 | 10,983 | **69** | **24,444** | **354** |
| 2025 H1 | 23 | 10,865 | 48 | 22,211 | **71** | **33,076** | **466** |
| 2025 H2 | 24 | 16,309 | 13 | 7,588 | **37** | **23,897** | **646** |
| 2026 H1 | 7 | 10,063 | 6 | 9,551 | **13** | **19,614** | **1,509** |
| 2026 Q3 | 2 | 4,507 | 0 | 0 | 2 | 4,507 | 2,254 |

- **From the first half of 2024 to the first half of 2026, public contests on the two platforms fell 83% (76 to 13), but the submissions they received rose 24% (15,787 to 19,614).** So each contest drew 7.3 times as many submissions (208 to 1,509). Measured from the 2025 H1 peak, contests fell 82% (71 to 13) and submissions only 41% (33,076 to 19,614).
- **The fall in contest numbers is already known; the submission side, as far as we can find, is not.** Immunefi's article "What We're Learning About Audit Competitions" (23 Sep 2026) reported that public platforms started 89 competitions in Q4 2024 and 11 in Q2 2026. Our two-platform counts (41 and 6) fall the same way. We could not find a published series for the other side of the market: how many submissions those contests received. Submissions shrank far less than contests did, so they pile onto the few contests that are left. That is a large part of why per-contest crowding (below) jumped.
- **What this can't show:** whether the same people now send more findings each (for example with AI tools), or whether more people take part. Public counts can't separate the two. The counts include invalid, duplicate and spam submissions. Contests are placed in the quarter they started, not the quarter each finding was sent. Private contests and invite-only engagements (Sherlock Audit Engine, Cantina private contests) aren't in these series. Code4rena, CodeHawks, Immunefi and HackenProof aren't included either.

Run `python cross_platform.py --table` for the quarterly, half-yearly and yearly rows.

## Every public Cantina competition (new in v0.5.0)

Cantina's site reads its competition list from a public JSON endpoint (`cantina.xyz/api/v0/competitions`), which carries `totalFindings` for every competition. `fetch_cantina.py` reads it in one GET (fetched 2026-10-14 20:03 UTC) and keeps only contest-level facts. Private contests keep no name, URL or sponsor, and they show up only in aggregates. The API returned 145 competitions: 126 public and 19 private, with one live. `data/cantina_census.csv` has the 125 ended public competitions with a count, which together drew 58,193 findings (started 2023-11-13 to 2026-05-29). `data/cantina_census.jsonl` has every public record, the live one included, and `data/cantina_census_summary.json` is the output of `cantina_crowding.py`. **Cross-check:** for all 20 ended competitions that v0.3.0 read by hand off their pages, the API count matched exactly.

| Started in | Competitions | Median findings per contest day | Same, USD pots of $60k or less | Median findings per $1k of pot | Median findings per competition | Median length (days) |
|---|---|---|---|---|---|---|
| 2023 (Nov–Dec) | 4 | 25.6 | (none) | 4.72 | 537 | 21.0 |
| 2024 | 43 | 17.0 | 21.4 (12) | 2.47 (41) | 315 | 20.7 |
| 2025 | 72 | 20.7 | 30.8 (35) | 8.74 (57) | 308.5 | 21.0 |
| 2026 | 6 | 158.2 | 158.2 (4) | 24.96 (5) | 1,343 | 8.9 |

- **The 2026 jump is real; the 2025 rise in the v0.3.0 sample was not.** The full census puts the median at 17.0 findings a day in 2024, 20.7 in 2025 and 158.2 in 2026. The 21-contest sample had 23.4, 37.6 and 146.5. The sample came from search results, which favour well-known contests, and that overstated 2025. The 2026 rise holds whichever way it's measured. Per competition, the median went from about 310 findings to 1,343 even though 2026 competitions were shorter (8.9 days against 21). Per $1k of pot it went from 8.7 to 25.0. Only six competitions finished in 2026, so its medians are rough.
- **Supply contraction, Cantina side:** 38 competitions started in 2025 Q1 (27 if the shared-pot Ethereum client set counts as one), then 21, 12 and 1 in the following quarters, and 3 in each quarter of 2026 H1. Unlike Sherlock, Cantina's total findings did fall too (13,095 in 2025 Q2 to 6,767 in 2026 Q2), but by much less than its contest count.
- **KYC vs no KYC, same year:** in 2025, KYC competitions had a median of 31.4 a day (n=10) and the rest 19.6 (n=62). Both groups hold near-empty events that pull their medians down: the no-KYC group has the 12 Ethereum client competitions and a hackathon, and the KYC group has two CTFs. In 2026 the medians were 91.0 (KYC, n=3) and 174.6 (no KYC, n=3). There's no consistent direction, which matches the Sherlock result below: no sign that KYC reduces crowding.
- **Private vs public:** Cantina's 16 ended private contests with counts had a median of 8.9 findings a day (2,569 findings in total), against 20.4 for the 125 public ones. They're listed by kind only, never by name.

**Limits.** Counts include invalid and duplicate submissions, and Cantina doesn't publish valid counts. The 12 shared-pot client competitions are left out of the per-dollar figures (and merged into one contest only in `cross_platform.py`). Pots in OP are left out of the per-dollar figures. Pots are headline sizes, and some pay in full only for a High. CTF-style events (Superform, EulerSwap and Aave Aptos CTFs) and one hackathon are kept as Cantina lists them. Long competitions show lower per-day rates.

Reproduce:

```
python fetch_cantina.py --out data/cantina_census_raw.jsonl     # one GET
python cantina_crowding.py --in data/cantina_census_raw.jsonl --out-dir out
```

## Every Sherlock contest, 2022 to 2026 (v0.4.0)

Sherlock's public contest API (`mainnet-contest.sherlock.xyz/contests`, the JSON its own site reads) carries, for every contest, `num_competition_issues`: the number of issues submitted, valid or not. We downloaded all 301 public records on 2026-10-14 with `fetch_sherlock.py` (read-only GETs, one at a time, paused) and kept contest-level facts only: dates, pot, token, code size, the KYC flag and the issue count. No researcher or judge names. `data/sherlock_contests.jsonl` has every record; `data/sherlock_contests.csv` has one row per finished contest with a count (259 contests, 86,058 issues in total, starting 2022-08-29 to 2026-07-20; the other 42 records are finished contests whose count is 0 or missing). `sherlock_crowding.py` computes everything below, `data/sherlock_summary.json` is its output, and `test_sherlock_crowding.py` tests it offline.

| Started in | Contests | Median issues per contest day | Median issues per $1k of pot (stablecoin pots) | Median issues per 1,000 nSLOC | Issues submitted that year (all contests) |
|---|---|---|---|---|---|
| 2022 | 26 | 18.5 | 3.70 | (no nSLOC published) | 3,540 |
| 2023 | 75 | 22.4 | 4.50 | 115 (60 contests) | 17,545 |
| 2024 | 102 | 25.6 | 4.49 (99) | 135 | 23,229 |
| 2025 | 47 | 55.3 | 10.75 (45) | 355 (46) | 27,174 |
| 2026 | 9 | 142.0 | 23.24 | 632 (8) | 14,570 (Jan–Jul) |

- **Per contest, submissions rose about 5.5× from 2024 to 2026** (25.6 → 142 a day; 4.5 → 23.2 per $1k of pot). It is not because contests got shorter or cheaper: the median contest ran 6 days in 2024 and 10 in 2026, and the median pot rose from $30k to $60k. The full Cantina census above shows the same 2026 jump (17.0 → 20.7 → 158.2 a day for 2024 → 2025 → 2026), though on Cantina the rise came later, all in 2026.
- **But most of the per-contest rise comes from fewer contests, not more submissions.** Sherlock ran 102 public contests that started in 2024, 47 in 2025 and 9 in 2026 (35 in the first quarter of 2024, 2 in the third quarter of 2026), while the total submitted across all of them stayed at roughly 4,500–7,000 a quarter (one 10,636 peak in 2025 Q3). In 2024 Q1, 35 contests drew 5,315 issues; in 2026 Q2, 3 contests drew 5,504. The same flow of submissions now lands on a handful of contests. The combined section above tests this on both platforms.
- **KYC vs no KYC, same year:** in 2025, contests with KYC had a lower median (34.0 a day, n=20) than those without (69.3, n=27). This gap comes from the type of contest, not from KYC. Many 2025 KYC contests were long "Best Efforts" or bug-bounty-style events. Among ordinary "Public" contests that started in 2025, KYC contests had a median of 124.2 a day (n=9) and non-KYC contests 102.0 (n=17), so we found no sign that KYC reduces crowding. (Computed by hand from `data/sherlock_contests.csv`: filter `type_label == "Public"` and a 2025 `start`.) By 2026, 8 of 9 contests required KYC, so that year allows no comparison.
- **By Sherlock's own type label** (all years): "Public" 28.2 a day (n=198), "Public Best Efforts" 21.6 (n=50), "Public Bug Bounty" 40.2 (n=11). The bug-bounty-style events are long, large-pot attackathons (XRP Ledger, Aave V4, Fusaka, Fluid DEX v2) and all date from 2025–2026, so their higher median mostly reflects the year.
- **Quarterly series:** `python sherlock_crowding.py --in data/sherlock_contests.jsonl` prints contests, issues and median issues per day for each quarter (it is also in `data/sherlock_summary.json`).

**Limits.** Counts include invalid, duplicate and spam submissions. Sherlock doesn't publish valid counts in the same field, so this measures crowding, not quality. Private contests and Sherlock Audit Engine engagements aren't in the public API, so "fewer contests" means fewer *public* contests: some work may have moved to private formats this data can't see. The type labels mix classic contests with bug-bounty-style events. Older contests report nSLOC as 0 with an empty scope, and those rows are left out of the per-kSLOC figures. Pots in non-stablecoin tokens (two OP pots in 2025) are left out of the per-dollar figures. Pots are Sherlock's headline `rewards` totals, which include judging and lead-auditor pay; some pay in full only if a High is found. Contest length matters, because long contests show lower per-day rates. 2026 has only 9 contests, so its medians are rough. The KYC split by type above was computed by hand, not by the script.

Spot checks against the live API on 2026-10-14: contest 36 (Cooler, Jan 2023) 342 issues; contest 225 (PoolTogether: The Prize Layer for DeFi, May 2024) 163 issues; contest 1279 (Metric, Jul 2026) 3,307 issues. All three matched the dataset, as did their dates and pots.

Reproduce:

```
python fetch_sherlock.py --out data/sherlock_contests.jsonl     # ~360 polite GETs, a few minutes
python sherlock_crowding.py --in data/sherlock_contests.jsonl --out-dir out
```

## How crowded are Cantina competitions? (v0.3.0 sample, superseded by the census above)

Each Cantina competition page shows a running "Findings submitted" count. `data/cantina_competitions.csv` records it for 21 competitions (Aug 2024 to the live Revert v4lend), each read off its public page on 14 Oct 2026, together with the dates and the headline prize. `crowding.py` computes the rates below, and `test_crowding.py` pins every number quoted here. The census matched all 20 ended counts exactly, but it showed that the sample overstated the 2025 median (37.6 against 20.7 in the census), because search results favour well-known contests.

| Started in | Contests | Median findings per contest day | Same, USD pots of $60k or less |
|---|---|---|---|
| 2024 | 4 | 23.4 | (none in sample) |
| 2025 | 9 | 37.6 | 36.9 (6 contests) |
| 2026 | 7 | 146.5 | 146.5 (5 contests) |

- **The two Royco contests** of 2026 (37 and 16 per day) were the sample's low points. Both required KYC to join. Dawn paid for Highs only, and Day's pot was $7.5k unless a High was found. The censuses found no general KYC effect.
- **Payouts are concentrated.** In Revert Finance's March 2026 competition (1,248 findings), 59 researchers were paid. The 8 with a rarely duplicated Medium took 82.7% of the $50k, about $5,100–$5,300 each. The 46 whose single Medium was widely duplicated got $154 each. In Revert's StableSwap Hooks competition (1,412 findings), the top 10 of 138 paid researchers took 76.1%. `data/revert_payout_tiers.csv` has the tiers, without researcher names.
- **What this means in practice:** in a 2026 Cantina contest, almost all of the money goes to findings few others submitted. A widely found bug pays close to nothing, however valid it is.

**Limits.** The 21 contests are the ones search engines returned, so this is a sample, not a census. The counts include invalid and duplicate submissions. Pots marked "full pot only with a valid High" are recorded at their headline size. Two OP-denominated pots are left out of the per-dollar figures. Run `python crowding.py --table` for every row.

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

## Tools: the crowding scripts

```
python cross_platform.py --table   # Sherlock + Cantina: contests and submissions per quarter, half-year, year
python cantina_crowding.py --in data/cantina_census.jsonl   # Cantina census summary (JSON)
python sherlock_crowding.py --in data/sherlock_contests.jsonl   # Sherlock census summary (JSON)
python crowding.py           # Cantina v0.3.0 sample: medians by year, payout concentration
python crowding.py --table   # one line per sampled Cantina contest
python fetch_cantina.py --out <file>.jsonl                  # refresh the Cantina census (one GET)
python fetch_sherlock.py --out data/sherlock_contests.jsonl # refresh the Sherlock census
```

Run all tests with `python -m pytest` (no network needed).

## Sources

- Sherlock contest API (census source): https://mainnet-contest.sherlock.xyz/contests and https://mainnet-contest.sherlock.xyz/contests/<id>
- Cantina competition API (census source): https://cantina.xyz/api/v0/competitions
- Cantina competitions: https://cantina.xyz/competitions (each row of `data/cantina_competitions.csv` links its own page)
- Prior art on contest counts: Immunefi, "What We're Learning About Audit Competitions" (23 Sep 2026): https://x.com/immunefi/status/2102715623218557375
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
