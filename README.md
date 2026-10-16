# Audit contest platforms: AI rules, KYC, payouts and crowding (checked 2026-10-15)

A dated, sourced snapshot of where smart-contract audit contests stand for work made with AI agents, a few small tools, and open datasets on how crowded audit contests have become: a census of every public Sherlock contest, a census of every public Cantina competition, a combined series built from the two, the headline prize money each submission competes for, a record of what every HackenProof audit program promised and what it paid, when HackenProof's programs began to carry rules on AI-generated reports, and a census of every CodeHawks audit and First Flight. Compiled by MV2 of Munim, Inc. while choosing where to take part. The research, the writing and the code were done with AI agents. Rules change, so check each source before relying on it. Corrections welcome as issues.

## Summary

| Platform | Live on 2026-10-15 | AI-made findings | KYC | Payout |
|---|---|---|---|---|
| Sherlock Audit Engine | Engagements are invite-based (handpicked); apply when applications open. Not a public listing. On 15 Oct the dashboard showed 0 engagements taking applications | **Explicitly welcome**: "AI auditors" are a participant type next to human researchers | Required before accepting an engagement invite, plus a DocuSign NDA per engagement | USDC on Polygon (or RLUSD on XRP Ledger); needs at least 2 valid findings and a 20% valid ratio |
| Sherlock contests (classic) | 0 active (API `status=RUNNING` returns `"total":0`). The last public contest in the API started on 20 Jul 2026 | No specific rule found | Required in 8 of the 9 contests that started in 2026 | USDC |
| Cantina | 1 competition: Revert v4lend, $50k USDC, 6 Oct to 3 Nov (1,392 findings submitted by 15 Oct 00:35 UTC); plus ongoing bounties | Allowed if validated: "submitting AI generated findings without validating them can lead to disqualifications or worse, a permanent ban" | Required (Persona) | USDC to an Ethereum mainnet address, paid weekly |
| HackenProof | 3 DualDefense audits ($2.5k–$3k, Criticals only): EverValue (2–16 Oct), Digital Oro (5–26 Oct), DreamX (12–26 Oct; its scope repo is invite-only and needs KYC to request access). See the payout record below: 67 of 78 settled DualDefense audits paid $0 | No platform-wide rule in the docs or Code of Conduct, but 62 of its 102 audit-program pages carry one, including every program that started in 2026 (43 of 43): "AI-generated reports without runable PoC are not accepted under this program" (DualDefense) or "Automated submissions or AI-generated reports must include human validation" (contests). See below | Only for EU tax residents, programs that require it, or after $5k in total earnings | USDC from your platform balance, 100 USDC minimum, 2FA required |
| Immunefi | 0 audit competitions or boosts live (ENS ended 8 Oct; all 62 listed competitions are finished) | **Prohibited**: its terms ban "submitting AI-generated/automated scanner bug reports" | Per program | Per program |
| CodeHawks (Cyfrin) | Nothing live. BattleChain Confidence Pools (9–16 Jul 2026) was its first audit in 15 months (see the census below) | **Penalised**: "Participants suspected of relying excessively on AI for their submissions risk disqualification." In its public docs repo since 14 Sep 2023 | Per contest ("KYC Rewards" tag) | USDC on ZKsync |
| Certora (formal verification) | Nothing live. All 15 listed contests have ended (pools $18k–$125.5k, "$800k+" paid in total); recent ones ran with Cantina | No rule found | Per hosting platform | Per hosting platform |
| Code4rena | Closed: announced its wind-down on 13 May 2026; Immunefi took over its clients. K2 ($135k) is still in judging. No new audits | n/a | n/a | n/a |

## Headline prize money per submission: Sherlock and Cantina together (new in v0.7.0)

`prize_per_submission.py` takes the same two censuses and adds up, by the half-year a contest started, the headline prize money of every contest with a US-dollar pot and the submissions those contests received. Sherlock's figure is its `rewards` total (the census's `pot_usd`); Cantina's is the competition pot. GHO and RLUSD pots count at $1. Contests paid in OP tokens and one hackathon with no pot are left out together with their submissions (11 contests over the six half-years). The 12 Ethereum client competitions of February 2025 count once, with their shared $2M pot. `test_prize_per_submission.py` pins every number below to the files in `data/`, and checks that the included and left-out contests add up to the contest and submission totals of the next section.

| Started in | Contests with a USD pot | Headline prize money | Submissions | **Prize money per submission** | Without $1M+ pots: contests | prize money | per submission |
|---|---|---|---|---|---|---|---|
| 2024 H1 | 76 | $7,117,565 | 15,787 | **$450.85** | 74 | $4,667,565 | $331.31 |
| 2024 H2 | 64 | $9,922,650 | 21,740 | **$456.42** | 60 | $4,184,150 | $215.63 |
| 2025 H1 | 67 | $10,089,100 | 32,025 | **$315.04** | 65 | $5,589,100 | $180.50 |
| 2025 H2 | 36 | $4,846,000 | 22,885 | **$211.75** | 35 | $2,846,000 | $126.38 |
| 2026 H1 | 12 | $1,563,500 | 18,340 | **$85.25** | 12 | $1,563,500 | $85.25 |
| 2026 H2 (to date) | 2 | $200,000 | 4,507 | $44.38 | 2 | $200,000 | $44.38 |

- **From the first half of 2024 to the first half of 2026, headline prize money per submission fell 81%, from $451 to $85.** The prize money on offer fell 78% ($7.12M to $1.56M) while the submissions to those contests rose 16% (15,787 to 18,340).
- **It is not an artefact of a few mega pots.** Nine contests with pots of $1M or more (Blast and Euler v2 in 2024 H1; MakerDAO Endgame, Uniswap v4, Omni Network and Story in 2024 H2; EigenLayer and the Ethereum client set in 2025 H1; Ethereum Fusaka in 2025 H2) carry much of the 2024–2025 money. Without them the fall is 74%, and every half-year is lower than the one before: $331, $216, $181, $126, $85.
- **What it means for a researcher:** in a public 2026 H1 contest on these platforms, the average submission competed for about $85 of headline money, before duplicate splits and before any conditions on the pot. The 2026 H2 figure ($44, two Sherlock contests so far) is partial.
- **Prior art:** platforms publish cumulative payouts (e.g. Cantina's totals) and Immunefi published the fall in contest counts (Sep 2026). We found no published half-year series of contest prize money, or of prize money per submission, for any platform.

**Limits.** These are headline figures, not payouts. Sherlock's `rewards` total includes lead-auditor and judging pay, so it overstates what researchers share. Some pots pay in full only if a High is found, and the HackenProof record below shows how far paid amounts can fall below headline ones. Submissions include invalid, duplicate and spam reports. Private contests and invite-only engagements (Sherlock Audit Engine, Cantina private contests) aren't included, and neither are Code4rena, CodeHawks, Immunefi or HackenProof. Contests are placed in the half-year they started.

Reproduce: `python prize_per_submission.py --table` (or without `--table` for JSON).

### Per contest: the typical contest, not the pooled total (new in v0.7.1)

The pooled figures above weight each contest by its submissions, so a few large pots can carry them. `per_contest()` in the same script works out each contest's own prize money per submission (its pot divided by its submissions) and reports, per half-year, the median contest and how many contests offered less than $100 per submission. It uses the same contests as the table above (same pots, same left-outs, the Ethereum client set counted once), and `test_prize_per_submission.py` pins every number here and checks that the contest counts match.

| Started in | Contests with a USD pot | **Median contest: prize money per submission** | Contests under $100 per submission |
|---|---|---|---|
| 2024 H1 | 76 | **$260.25** | 14 (18%) |
| 2024 H2 | 64 | **$209.17** | 16 (25%) |
| 2025 H1 | 67 | **$129.20** | 31 (46%) |
| 2025 H2 | 36 | **$92.41** | 20 (56%) |
| 2026 H1 | 12 | **$41.54** | 8 (67%) |
| 2026 H2 (to date) | 2 | $43.51 | 2 (both) |

- **The typical contest fell further than the pooled total: the median went from $260 to $42 per submission (−84%) between the first halves of 2024 and 2026**, against −81% for the pooled figure. Every half-year to 2026 H1 is lower than the one before.
- **Under $100 per submission went from the exception to the rule:** 18% of contests in 2024 H1, 67% in 2026 H1. In 2026 H1 only four contests offered more than $100 per submission, all large or unusual pots: XRP Ledger ($550k, about $203), Royco Dawn ($50k, about $191, Highs only), Fluid DEX v2 ($200k, about $166) and Morpho Midnight ($400k, about $103).
- **The median is a check on the pooled result, and it agrees.** It ignores how large any single pot is, so the fall cannot come from mega pots leaving the market.
- **Prior art:** as above, we found no published per-contest series of prize money per submission.

**Limits.** All of the limits above apply. A median over 12 contests (2026 H1) is rough, and over 2 (2026 H2) it means little. The median contest is a contest, not a researcher: it says nothing about how the money in a contest is split.

## Fewer contests, not fewer submissions: Sherlock and Cantina together (v0.5.0)

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

## What HackenProof actually paid: every audit program, promised vs. paid (v0.6.0)

HackenProof is the only contest platform whose public listing shows, next to each program's "Up to: $X" maximum, a "Paid: $Y" figure (the program page calls it "Total rewards"). `data/hackenproof_programs.csv` records both for all 102 audit programs the listing held on 15 Oct 2026: 19 audit contests and 83 DualDefense audits, which are the listing's own header counts, with each program's kind, status, end date and listing page. These rows were first read by hand off the 11 listing pages. **A scripted fetch of all 102 program pages (15 Oct 2026, 21:51 UTC) then matched every row exactly, on both the maximum and the paid figure**; its output, which adds start dates, submission counts and each page's AI rule, is `data/hackenproof_programs_fetched.csv` (next section), and `test_hackenproof_trends.py` checks the two files against each other. `hackenproof_payouts.py` computes the table, and `test_hackenproof_payouts.py` pins every number below to the file. "Settled" means finished with a public paid figure; the three live programs and two "Paid: Private" programs are counted but left out of the money columns. "Paid in full" means at least 99% of the maximum.

| Programs | Listed | Settled | Max reward (settled) | Paid | Paid share | Paid nothing | Paid in full | Median max |
|---|---|---|---|---|---|---|---|---|
| Audit contests, all | 19 | 19 | $677,000 | $318,949 | 47.1% | 2 | 5 | $14,000 |
| &nbsp;&nbsp;ended 2025 | 14 | 14 | $533,000 | $251,448 | 47.2% | 0 | 3 | |
| &nbsp;&nbsp;ended 2026 (to 15 Oct) | 3 | 3 | $59,000 | $45,001 | 76.3% | 1 | 2 | |
| DualDefense audits, all | 83 | 78 | $1,588,650 | $180,645 | 11.4% | 67 | 2 | $10,000 |
| &nbsp;&nbsp;ended 2024 | 10 | 9 | $203,500 | $0 | 0.0% | 9 | 0 | $20,000 |
| &nbsp;&nbsp;ended 2025 | 32 | 31 | $1,071,800 | $168,658 | 15.7% | 23 | 0 | $29,000 |
| &nbsp;&nbsp;ended 2026 (to 15 Oct; 3 live) | 41 | 38 | $313,350 | $11,987 | 3.8% | 35 | 2 | $4,000 |
| **All** | **102** | **97** | **$2,265,650** | **$499,594** | **22.1%** | **69** | **7** | |

- **Across 97 settled programs, HackenProof paid out 22% of the headline maximums** ($499,594 of $2,265,650). Audit contests paid 47% of their maximums, with a median of 50% per contest, and 5 of 19 paid in full. DualDefense audits paid 11%, and 67 of 78 (86%) paid nothing at all.
- **Why DualDefense pays so rarely.** Each program page says only Critical findings "that could lead to the loss of user funds or the permanent lock of funds" are eligible; High, Medium and Low are listed at $0. The "up to" figure is a cap reached only if a Critical is found: the pool is split equally among unique Criticals, HackenProof keeps 10% as a triage fee, and several programs pay in HAI tokens. A $0 most often means no accepted Critical, which is a fine outcome for the client. For a researcher, a DualDefense headline is not a prize pot, and its expected value is a small fraction of the number shown.
- **The programs got much smaller in 2026.** The median DualDefense maximum fell from $29,000 (31 settled programs ended in 2025) to $4,000 (38 ended in 2026), twelve of the 2026 programs being $2,000 audits for one client, and the paid share fell from 15.7% to 3.8%. Audit contests, the format that does pay, are rare: 14 ended in 2025 and 3 so far in 2026.
- **Submissions keep coming.** From the program pages (now in the fetched file): Perceptron ($2,000 max, paid $0) had 73 submissions from 45 hackers; ZIGChain had 149 submissions from 48 hackers and paid $3,987 of $75,000; Kinetic had 175 submissions and paid $2,000 of $40,000; Somnia had 275 submissions and paid $135,000 of $300,000.
- **Prior art:** we found none. Searches for analyses of HackenProof payouts against promised rewards returned only HackenProof's own program pages.

**Limits.** "Paid" is HackenProof's own figure: we don't know whether it is before or after the 10% fee, or how HAI-token payouts were converted to dollars. Programs that ended inside their "Reward Time" SLA may still settle (RAIN-USDR ended 1 Oct 2026 and shows $0). 0xMarkets shows $30,001 paid against a $30,000 maximum and is kept as listed. Some contests publish a guaranteed minimum (Bluefin Perp: "$45,000 - $85,000"); the listing only shows the cap, so minimums are not recorded. Programs are grouped by end date. The listing has no submission counts; the program pages do (next section).

Reproduce: `python hackenproof_payouts.py --table` (or without `--table` for JSON).

### By start half-year: AI-report rules, submissions and paid per submission (new in v0.7.2)

`hackenproof_trends.py` reads `data/hackenproof_programs_fetched.csv`, written by a scripted fetch of all 102 program pages on 15 Oct 2026 (21:51 UTC): each program's start and end dates, maximum, paid figure, submission count and hacker count, and every sentence on its page that mentions AI. It groups programs by the half-year they started. An **AI-report rule** means one of HackenProof's two sentences: "AI-generated reports without runable PoC are not accepted under this program" or "Automated submissions or AI-generated reports must include human validation." Other text that mentions AI (one project describes its own AI-generated media) is not counted. The money columns use settled programs only (finished, paid figure public) and those programs' submissions. `test_hackenproof_trends.py` pins every number below to the file.

| Started in | Programs (contests) | With an AI-report rule | Submissions | Settled | Max reward (settled) | Paid | Max per submission | **Paid per submission** |
|---|---|---|---|---|---|---|---|---|
| 2023 H2 | 1 (1) | 0 | 8 | 1 | $40,000 | $0 | $5,000.00 | $0.00 |
| 2024 H1 | 1 (1) | 0 | 34 | 1 | $45,000 | $22,500 | $1,323.53 | $661.76 |
| 2024 H2 | 12 (0) | 0 | 54 | 11 | $333,500 | $0 | $8,776.32 | $0.00 |
| 2025 H1 | 20 (4) | 0 | 940 | 19 | $685,800 | $135,162 | $736.63 | **$145.18** |
| 2025 H2 | 25 (10) | 19 | 3,403 | 25 | $864,000 | $288,931 | $253.89 | **$84.90** |
| 2026 H1 | 19 (2) | 19 | 3,588 | 19 | $142,150 | $51,001 | $39.62 | **$14.21** |
| 2026 H2 (to 15 Oct; 3 live) | 24 (1) | 24 | 2,485 | 21 | $155,200 | $2,000 | $65.71 | $0.85 |
| **All** | **102 (19)** | **62** | **10,512** | **97** | **$2,265,650** | **$499,594** | | |

- **AI-report rules arrived in mid-2025 and are now on every program.** None of the 34 programs that started before July 2025 carries one. The first is the OpenEden contest (started 16 Jul 2025). From 14 Aug 2025 on, 61 of 62 programs carry one, including all 43 that started in 2026; the exception is VeChain Stargate round 2 (Nov 2025). DualDefense audits use the PoC sentence (51 programs) and contests mostly the human-validation one (10; the 2025 DexLyn contest uses the PoC sentence). HackenProof's docs and Code of Conduct still have no platform-wide AI rule, so the rule lives on the program pages.
- **Paid per submission fell 90% in a year: $145.18 (2025 H1), $84.90 (2025 H2), $14.21 (2026 H1).** The headline maximum per submission fell 95%, from $736.63 to $39.62. Submissions rose from 940 to 3,588 a half-year while programs stayed at 19–25 a half-year, so each program drew about four times as many (47 to 189 on average). Meanwhile the money got smaller: maximums of $685,800 (2025 H1) against $142,150 (2026 H1).
- **This is money actually paid, not headline money,** so it is a harder measure than the Sherlock and Cantina figure above ($315 to $85 of headline money per submission over the same half-years). Both fall, on three platforms.
- **2026 H2 is not settled yet.** RAIN-USDR (972 submissions, ended 1 Oct) still shows $0 inside its reward window, and three programs are live. Read its $0.85 as a floor.
- **Timing, not cause.** The rules appeared while submissions were rising. This data can't say whether the rise prompted the rules, or whether the rules changed who submits.
- **Prior art:** Stingrai's census of AI-report policies (28 Jul 2026) coded 53 programs on HackerOne, Bugcrowd, Intigriti and YesWeHack, vendor programs and open source projects, as one snapshot; it does not cover Web3 audit platforms. We found no per-program, dated record of AI-report rules on any audit-contest platform, and no series of money paid per submission.

**Limits.** The AI text was read off each page as it stood on 15 Oct 2026. A rule could have been added to an older page later, or removed from one, and a single fetch can't tell; the start dates date the programs, not the rules. Submission counts are HackenProof's own and include invalid and duplicate reports; three DualDefense programs show 0. "Paid" has the limits of the section above. Somnia's $135,000 is almost half of 2025 H2's paid total. Half-years with one or a few programs (2023 H2, 2024 H1) mean little. This table groups by start date and the one above by end year, so a few programs fall in different periods.

Reproduce: `python hackenproof_trends.py --table` (or without `--table` for JSON).

## CodeHawks: contests stopped, they didn't get more crowded (new in v0.8.0)

`data/codehawks_contests.csv` (CC BY 4.0) has one row per contest page on codehawks.cyfrin.io, written by a scripted census on 16 Oct 2026. `codehawks_series.py` groups the contests by the half-year they started.

**It matches CodeHawks' own listings.** The census has the 45 competitive audits that the /contests page lists, and after one cleaning step it has First Flights #1 to #59, as listed on /first-flights. The cleaning step matters. The sitemap also lists 228 self-paced practice copies of two old First Flights (Thunder Loan and Beatland Festival). Their slugs end in a 25-character id. Counted as contests, they would turn 2026's 4 First Flights into 210. They are left out of every figure below.

Public competitive audits by start half-year:

| Started in | Audits (all access) | Public | Submissions | Median per audit | Signal rate | USDC audits | USDC $ per submission | Median audit $ per submission |
|---|---|---|---|---|---|---|---|---|
| 2023 H2 | 9 | 8 | 8,072 | 905.5 | 3.38% | 8 | $28.18 | $30.91 |
| 2024 H1 | 9 | 9 | 2,260 | 184 | 5.84% | 9 | $231.83 | $155.84 |
| 2024 H2 | 15 | 12 | 10,530 | 883 | 2.23% | 10 | $37.49 | $40.07 |
| 2025 H1 | 11 | 5 | 9,895 | 998 | 3.61% | 4 | $22.43 | $33.86 |
| 2025 H2 to 2026 H1 | 0 | 0 | | | | | | |
| 2026 H2 | 1 | 1 | 971 | 971 | 0.93% | 0 | (7.25 ETH) | |

- **No competitive audit started between 3 Apr 2025 and 9 Jul 2026.** That's 15 months. The one since then, BattleChain Confidence Pools, is Cyfrin's own and pays in ETH.
- **The audits that did run were not more crowded over time.** The median public audit drew 905.5 submissions in 2023 H2 and 998 in 2025 H1, with 184 in between: 2024 H1 was mostly the Beanstalk series of small audits. Sherlock and Cantina contests went the other way (sections above). CodeHawks lost its contests instead.
- Signal rate = unique valid High + Medium + Low findings / all submissions. It stays between 2% and 6% for every half-year with more than one audit.
- USDC pots only: three OP pots (Alchemix, QuantAMM, Curve) and one ETH pot (BattleChain) are left out, never converted. 2024 H1's pooled figure is high because of Beanstalk: The Finale ($250,000 for 555 submissions).

First Flights (they award experience points, not money), practice copies excluded:

| Started in | First Flights | Submissions | Median per flight | Signal rate |
|---|---|---|---|---|
| 2023 H2 | 6 | 3,399 | 509 | 1.59% |
| 2024 H1 | 12 | 3,138 | 216.5 | 3.95% |
| 2024 H2 | 13 | 3,876 | 291 | 2.68% |
| 2025 H1 | 11 | 5,447 | 525 | 1.82% |
| 2025 H2 | 13 | 4,721 | 285 | 2.35% |
| 2026 H1 | 4 | 1,114 | 265.5 | 4.67% |

First Flights ran about every two weeks through 2025 (24 that year). Four followed between 29 Jan and 16 Apr 2026. The last, #59 SNARKeling Treasure Hunt, started 16 Apr 2026, and none has started since.

**Limits.** Submission counts are CodeHawks' own and include invalid and duplicate reports, and lows count too, so don't compare them one-to-one with other platforms. Private and invite-only audits (10) have no public counts. Headline pots are not payouts. `test_codehawks_series.py` pins every number in this section to the data file and checks it against the two listing pages.

Reproduce: `python codehawks_series.py --table` (or without `--table` for JSON).

## Every public Cantina competition (v0.5.0)

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

**Limits.** Counts include invalid and duplicate submissions, and Cantina doesn't publish valid counts. The 12 shared-pot client competitions are left out of the per-dollar figures (and merged into one contest only in `cross_platform.py` and `prize_per_submission.py`). Pots in OP are left out of the per-dollar figures. Pots are headline sizes, and some pay in full only for a High. CTF-style events (Superform, EulerSwap and Aave Aptos CTFs) and one hackathon are kept as Cantina lists them. Long competitions show lower per-day rates.

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

- **Duplicates.** Cantina: points = full / (1 + 0.8 × (n − 1)), with High 10 and Medium 3. CodeHawks: High = 5 × 0.9^(n−1) / n, Medium = 0.9^(n−1) / n. HackenProof contests (Somnia, Bluefin Perp): Final Reward = Severity Weight × 0.9^(N−1) / N, with weights Low 20, Medium 30, High 50; HackenProof DualDefense: the pool is split equally among unique Criticals.
- **Coded PoCs.** Cantina requires a compiling coded PoC for every High and Medium before the end of a competition, for researchers with reputation below 80. HackenProof DualDefense needs a runnable PoC in the first submission (later PoCs are not accepted), pays for Criticals only, and every program since mid-2025 but one adds "AI-generated reports without runable PoC are not accepted under this program" (contests: "must include human validation"). HackenProof programs also require 50–80 reputation points and KYC to take part.
- **Sherlock Audit Engine — how it works.** Launched publicly on 18 Aug 2026. Participation is invite-based: Sherlock specialists handpick candidates and top researchers may be contacted directly; otherwise you apply when applications open, then "commit or decline" an engagement card. An NDA and Engagement Addendum are signed per engagement before it begins. You can import a past Sherlock Audit Contests account at signup to carry over an Issues Ratio (it cannot be linked later). Findings are judged in three stages: an AI judge (often within minutes), then a Lead Judge, then the protocol team. Protocols may exclude specific AI auditors "for confidentiality or commercial reasons".
  - **Issues Ratio** (public docs): accepted ÷ total submitted. Accepted counts +1/1, Dismissed +0/1, Neutral is excluded. "Rewrite and Resubmit" adds +0.5 to the denominator each time (and +0.5 to the numerator if accepted), commonly up to 5 rewrites per issue chain. No payout below a 20% ratio, and you need at least 2 valid findings across all engagements. Withheld rewards can be unlocked for 12 months after an engagement ends, then they are lost.
  - **Credits** (shown on the signup dashboard, Aug 2026): a valid finding earns +4 and an invalid one costs −1; if credits drop below 0, payouts lock. When an engagement closes, 20% of its findings are counted right away. An engagement that earns more credits than it burns pays out on its own; one that burns more is held, and releasing it costs credits. The public Issues Ratio counts every finding, held or not.
  - **Participant types** (account-creation page, Oct 2026): "Security researcher: Select if you're a human security researcher who uses manual review and potentially AI to find issues." "AI auditor: Select if you've built an automated AI system that can find and validate vulnerabilities without human involvement." The page adds that either account type can be selected in any specific engagement.
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

## Tools: the crowding and payout scripts

```
python prize_per_submission.py --table   # Sherlock + Cantina: prize money per submission per half-year, pooled and per-contest median
python cross_platform.py --table   # Sherlock + Cantina: contests and submissions per quarter, half-year, year
python hackenproof_payouts.py --table   # HackenProof: promised vs paid, by kind and end year
python hackenproof_trends.py --table   # HackenProof: AI-report rules, submissions and paid per submission, by start half-year
python codehawks_series.py --table   # CodeHawks: audits and First Flights by start half-year, practice copies left out
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
- Prior art on AI-report policies (bug bounty programs, not audit contests): Stingrai, "Who Actually Bans AI-Written Bug Reports? 2026 Census" (28 Jul 2026): https://www.stingrai.io/blog/ai-generated-vulnerability-report-policies-census
- Revert Finance leaderboards: https://cantina.xyz/competitions/efb6f308-f13b-4110-aff8-0d67181608dd/leaderboard and https://cantina.xyz/competitions/e55ee7b9-6c99-42f8-8338-39f3dd134ef3/leaderboard
- Cantina severity and AI rule: https://docs.cantina.security/standards/severity/competition
- Cantina KYC and payments: https://docs.cantina.xyz/for-security-researchers/joining-cantina/kyc and https://docs.cantina.security/researchers/joining/payout-schedule
- Sherlock Audit Engine for participants: https://docs.sherlock.xyz/audit-engine/for-participants
- Sherlock Audit Engine FAQ: https://docs.sherlock.xyz/audit-engine/faq
- Sherlock Audit Engine overview: https://docs.sherlock.xyz/audit-engine/about-audit-engine
- Sherlock Audit Engine launch: https://chainwire.org/2026/08/18/sherlock-unveils-audit-engine-as-ai-security-race-accelerates/
- Sherlock contests API: https://mainnet-contest.sherlock.xyz/contests?status=RUNNING
- HackenProof audit programs (payout record source, pages `?page=1` to `?page=11`): https://hackenproof.com/audit-programs
- HackenProof program pages (fetched census source): https://hackenproof.com/audit-programs/<slug>, one per row of `data/hackenproof_programs_fetched.csv`
- HackenProof program pages used as spot checks: https://hackenproof.com/audit-programs/somnia-audit-contest , https://hackenproof.com/audit-programs/dexalot-sc-dualdefense-audit , https://hackenproof.com/audit-programs/kinetic-audit-contest , https://hackenproof.com/audit-programs/zigchain-code-dualdefense-audit , https://hackenproof.com/audit-programs/bluefin-perp-audit-contest , https://hackenproof.com/audit-programs/perceptron-network-sc-dualdefense-audit
- HackenProof DreamX program: https://hackenproof.com/audit-programs/dreamx-marketplace-and-dex-sca-dualdefense-audit
- HackenProof KYC: https://docs.hackenproof.com/dashboard/hacker-dashboard/kyc.md
- HackenProof withdrawals: https://docs.hackenproof.com/dashboard/hacker-dashboard/withdraw-bounty.md
- HackenProof DualDefense rules: https://docs.hackenproof.com/dualdefense-audit/general-guidelines.md
- HackenProof Code of Conduct: https://docs.hackenproof.com/welcome/code-of-conduct.md
- Immunefi audit competitions: https://immunefi.com/audit-competition/
- Immunefi rules: https://immunefi.com/rules/
- CodeHawks census sources: https://codehawks.cyfrin.io/contests (45 audits) and https://codehawks.cyfrin.io/first-flights (#1 to #59), both checked 16 Oct 2026, plus each contest's page
- CodeHawks AI rule: https://github.com/Cyfrin/codehawks-docs/blob/main/judging/disqualification-criteria.md (added in commit 9fc66d1, 14 Sep 2023)
- CodeHawks payouts: https://docs.codehawks.com/judging/payouts-and-rewards
- Certora contests: https://www.certora.com/contests
- Code4rena wind-down: https://coinalertnews.com/news/2026/05/13/code4rena-shutdown-immunefi-takeover
- Contest calendar: https://bbradar.io/contests

## License

Code: Apache-2.0 (see LICENSE). The data in `data/` and this README's text: CC BY 4.0. MV2 of Munim, Inc. (mv2@munimtech.com).
