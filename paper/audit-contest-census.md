# Fewer contests, more submissions, less money each: a census of public smart-contract audit contests on six platforms, 2021-2026

Preprint, version 1.8 (16 October 2026). Not peer reviewed.

MV2 of Munim, Inc. (mv2@munimtech.com). The data collection, analysis, code and this text were made with AI agents working
for MV2. Text: CC BY 4.0. Code: Apache-2.0. Data and code: https://github.com/munimtechnologies/audit-contest-ai-rules
(release v0.9.0). Corrections are welcome as issues on that repository.

---

## Abstract

Public smart-contract audit contests pay security researchers to review a project's code for a fixed time and split a
prize pot among the valid findings. We built per-contest censuses from each platform's own public pages, APIs and
repositories: every public Sherlock contest (259 with submission counts, 2022-2026), every public Cantina competition (125
ended with counts), every Immunefi competition (62), every HackenProof audit program (102), every CodeHawks audit (45) and
First Flight (59), and 372 of the 376 public Code4rena findings repositories (2021-2024). From the first half of 2024 to
the first half of 2026, public contests on Sherlock and Cantina fell 83% (76 to 13) while the submissions they received
rose 24% (15,787 to 19,614), so each contest drew 7.3 times as many. Immunefi's audit-type competitions fell 85% over a
similar span (20 in 2024 H2 to 3 in 2026 H1). CodeHawks started no competitive audit for 15 months (3 Apr 2025 to 9 Jul
2026). Headline prize money per submission on Sherlock and Cantina fell 81% (pooled, $450.85 to $85.25) and 84% for the
median contest ($260.25 to $41.54). On HackenProof, the only platform that publishes what each program actually paid,
money paid per submission fell 90% in a year ($145.18 in 2025 H1 to $14.21 in 2026 H1). This crowding is not new in
kind. Code4rena went through it in 2022-2023: its median audit drew 29 High/Medium submissions in 2021 H1 and 356 in
2023 H2, and the pooled share of them that became a distinct valid finding fell from 38.4% to 3.4%. What is new in
2025-2026 is that the supply of contests fell at the same time. We also code the platform-wide rules on AI-generated
reports of six audit platforms with a rubric published for general bug-bounty programs. All four general platforms in
that rubric's census accept AI-assisted reports under a condition. The audit platforms are spread much more widely,
from an unqualified prohibition in Immunefi's researcher terms, through penalties with no stated path to acceptance
(CodeHawks, Code4rena), to Sherlock's Audit Engine, which admits AI auditors as participants. Code4rena did something
similar earlier: from April 2023 to about early 2024 it paid 10% of each pool to a race between automated tools (Bot
Races). Most of the
rules date from 2022-2023, before the contest collapse. Two changes fall inside it: HackenProof's per-program rules from
July 2025, as its paid money per submission starts to fall, and from 25 September 2025 Code4rena's owner ran its own AI
auditor on every contest and ruled its findings known issues. A contest-count decline was already reported by Immunefi
(Sep 2026), and contemporary posts describe early Code4rena's growth in participants. As far as we can find, the
submission, signal-rate, money-per-submission and AI-rule series are new. All data and code are open.

## 1. Why this matters

For a researcher deciding where to spend review time, the number of contests matters less than the money each submission
competes for. For platforms and clients, a falling ratio of prize money to submissions means more judging load per dollar.
Answering researchers' criticism of Sherlock's move away from its classic contest platform, Sherlock CEO and co-founder
Jack Sanford said the company prioritizes high-signal reports and pointed to cases where "high volumes of false positives
have overloaded judges and damaged client relationships" (as reported by The Breach Ledger, 13 Oct 2026). This paper
measures that pressure from public data.

## 2. Data

All sources are public pages, public GitHub repositories, or the JSON endpoints the platforms' own sites read. Fetches were
read-only, one page at a time with pauses (Code4rena: six parallel shallow clones of public repositories). Only
contest-level facts are kept: no researcher handles, per-person earnings or wallets.

| Platform | Source | Fetched | Records | Validation |
|---|---|---|---|---|
| Sherlock | `mainnet-contest.sherlock.xyz/contests` (`num_competition_issues`) | 2026-10-14 | 301 records; 259 finished with a count, 86,058 issues | 3 contests spot-checked against the live API (dates, pot, count) |
| Cantina | `cantina.xyz/api/v0/competitions` (`totalFindings`) | 2026-10-14 20:03Z | 145 (126 public, 19 private); 125 ended public with a count, 58,193 findings | all 20 counts read earlier by hand off contest pages match |
| Immunefi | each competition's information and results pages | 2026-10-15 19:23-19:33Z | 62 (52 audit-type, 8 Attackathons, 2 bug-bounty competitions) | 2 competitions (ENS, Firedancer V1) checked by hand; category totals match; every half-year figure re-derived by hand from the data file |
| HackenProof | listing pages 1-11 and all 102 program pages | 2026-10-15 (hand read; scripted fetch 21:51Z) | 102 (19 contests, 83 DualDefense) | scripted fetch matched the hand-read listing on every row, both max and paid |
| CodeHawks | each contest page and the sitemap | 2026-10-16 07:28-07:58Z | 332 pages: 45 audits (35 public with counts, 31,728 submissions), 59 First Flights (21,695 submissions), 228 practice copies (excluded) | audits match the 45 on /contests; First Flights match #1-#59 on /first-flights |
| Code4rena | every public `code-423n4/<audit>-findings` repository: one JSON record per submission, plus the published report | 2026-10-16 10:57-12:44Z | 376 repositories listed, 372 read (347 audits, 25 mitigation reviews; 9 undated) | 2024 H2 re-derived by hand row by row; Code4rena's own 2023 total lies between our two 2023 totals; submitter counts match a 2022 participant's figures (section 3.7) |

Contests are placed in the half-year they **started**. Submission counts are the platforms' own and include invalid,
duplicate and spam reports. Private contests and invite-only engagements (Sherlock Audit Engine, Cantina private
contests, CodeHawks private and invite-only audits) are not in the public series.

## 3. Results

### 3.1 Fewer contests, not fewer submissions (Sherlock + Cantina)

| Started in | Contests | Submissions | Per contest |
|---|---:|---:|---:|
| 2024 H1 | 76 | 15,787 | 208 |
| 2024 H2 | 69 | 24,444 | 354 |
| 2025 H1 | 71 | 33,076 | 466 |
| 2025 H2 | 37 | 23,897 | 646 |
| 2026 H1 | 13 | 19,614 | 1,509 |
| 2026 Q3 | 2 | 4,507 | 2,254 |

The 12 Ethereum client competitions of February 2025 (one shared $2M pot) count as one contest. Contests fell 83% from
2024 H1 to 2026 H1; submissions rose 24%. From the 2025 H1 peak, contests fell 82% and submissions only 41%. Per-contest
crowding rose for both platforms separately: Sherlock's median issues per contest day went 25.6 (2024) -> 55.3 (2025) ->
142.0 (2026); Cantina's median findings per contest day 17.0 -> 20.7 -> 158.2. On Sherlock the median 2026 contest ran
longer (10 days vs 6) and had a larger pot ($60k vs $30k) than in 2024, so the rise isn't shorter or cheaper contests.

### 3.2 The same contest decline on Immunefi

| Started in | All competitions | Audit-type | Audit-type pools (USD stated) | Median audit-type pool | Median audit-type leaderboard entries |
|---|---:|---:|---:|---:|---:|
| 2023 H2 | 1 | 1 | $50,000 | $50,000 | 35 |
| 2024 H1 | 8 | 7 | $609,000 | $87,500 | 17.5 |
| 2024 H2 | 22 | 20 | $2,900,000 | $72,500 | 7.5 |
| 2025 H1 | 13 | 11 | $681,000 | $30,000 | 9.5 |
| 2025 H2 | 12 | 7 | $270,000 | $30,000 | 50.5 |
| 2026 H1 | 3 | 3 | $1,275,000 | $250,000 | 95 |
| 2026 H2 (to 15 Oct) | 3 | 3 | $110,000 | $20,000 | 133 |

Audit-type means Audit Competitions and Boosts, IOPs and Mitigation Audits. Audit-type competitions fell 85% from 2024 H2
to 2026 H1. 2026 H1's pool total is mostly one $1M competition (Firedancer V1); without it the half has $275k across 2
competitions. Pools are the amounts the pages state, in several tokens, never converted.

Leaderboards got much longer, but that column is **not** like-for-like. Until mid-2025 the results page lists only
entries with earnings: all 8 rows on Acre (Aug 2024) and all 72 on Yeet (Mar 2025) show an amount. The layout used from
July 2025 (the last old-style page we read is from 18 Sep 2025) also lists entries that earned $0: 31 of the 183 ranked
entries on Alchemix V3 (Oct 2025). The longest 2024 leaderboard had 58 paid entries (Alchemix, Apr 2024), and every 2026
leaderboard is at least that long. So more people are probably being listed per competition, but these figures cannot
say how many more of them were paid. A paid-only recount of the 14 new-layout boards from the saved pages would settle
it; we have not run it yet.

### 3.3 Headline prize money per submission (Sherlock + Cantina)

| Started in | Contests with a USD pot | Pooled $ per submission | Median contest $ per submission | Contests under $100/submission |
|---|---:|---:|---:|---:|
| 2024 H1 | 76 | $450.85 | $260.25 | 14 (18%) |
| 2024 H2 | 64 | $456.42 | $209.17 | 16 (25%) |
| 2025 H1 | 67 | $315.04 | $129.20 | 31 (46%) |
| 2025 H2 | 36 | $211.75 | $92.41 | 20 (56%) |
| 2026 H1 | 12 | $85.25 | $41.54 | 8 (67%) |
| 2026 H2 (to date) | 2 | $44.38 | $43.51 | 2 |

Pooled: -81%. Without the nine $1M+ pots: $331.31 -> $85.25 (-74%), falling every half-year. Median contest: -84%. The
median ignores pot size, so the fall cannot come from mega pots leaving. These are headline pots: Sherlock's `rewards`
includes lead-auditor and judging pay, and some pots pay in full only if a High is found.

### 3.4 Money actually paid, and AI-report rules (HackenProof)

| Started in | Programs | With an AI-report rule | Submissions | Paid (settled) | Paid per submission |
|---|---:|---:|---:|---:|---:|
| 2025 H1 | 20 | 0 | 940 | $135,162 | $145.18 |
| 2025 H2 | 25 | 19 | 3,403 | $288,931 | $84.90 |
| 2026 H1 | 19 | 19 | 3,588 | $51,001 | $14.21 |
| 2026 H2 (to 15 Oct; 3 live) | 24 | 24 | 2,485 | $2,000 | $0.85 (unsettled floor) |

Across 97 settled programs HackenProof paid 22.1% of headline maximums ($499,594 of $2,265,650); DualDefense audits
(Criticals only) paid 11.4%, and 67 of 78 paid nothing. HackenProof uses two AI sentences, and they start on different
dates. The contest sentence, "Automated submissions or AI-generated reports must include human validation", first
appears on the OpenEden contest (started 16 Jul 2025). The DualDefense sentence, "AI-generated reports without runable
PoC are not accepted under this program", first appears on the Coindepo audit (started 14 Aug 2025); no DualDefense
program that started in July 2025 carries it. From 14 Aug 2025, 61 of 62 programs carry one of the two. Rule text was
read as it stood on 15 Oct 2026, so start dates date the programs, not the rules.

### 3.5 A live contest, measured as it fills (Cantina, Revert v4lend) [interim; the contest ends 3 Nov 2026]

Findings submitted, read off the public competition page: 1,282 (14 Oct 09:55Z) -> 1,392 (15 Oct 00:35Z) -> 1,526
(16 Oct 01:18Z) -> 1,628 (16 Oct ~14:30Z), against a $50,000 USDC pot (about $30.71 per finding so far), about 6.6 an
hour on average since 14 Oct. Rates between readings about two hours apart swing from about 1 to about 22 an hour. The
contest requires a coded proof of concept for every Critical, High and Medium finding, from every researcher. The final
count, the full arrival curve and the payout tiers (no handles) will be added in a later version, after the contest
settles.

### 3.6 CodeHawks: a platform that stopped, not one that crowded

| Started in | Audits (all access) | Public | Submissions | Median per audit | Signal rate | USDC $ per submission (pooled / median audit) |
|---|---:|---:|---:|---:|---:|---|
| 2023 H2 | 9 | 8 | 8,072 | 905.5 | 3.38% | $28.18 / $30.91 |
| 2024 H1 | 9 | 9 | 2,260 | 184 | 5.84% | $231.83 / $155.84 |
| 2024 H2 | 15 | 12 | 10,530 | 883 | 2.23% | $37.49 / $40.07 |
| 2025 H1 | 11 | 5 | 9,895 | 998 | 3.61% | $22.43 / $33.86 |
| 2025 H2, 2026 H1 | 0 | 0 | | | | |
| 2026 H2 | 1 | 1 | 971 | 971 | 0.93% | (7.25 ETH) |

No CodeHawks competitive audit started between 3 Apr 2025 and 9 Jul 2026; the one since is Cyfrin's own, paid in ETH.
(Immunefi's September 2026 article reports the same: one CodeHawks competition since mid-2025.) The audits
that did run show no crowding trend: the median public audit drew 905.5 submissions in 2023 H2 and 998 in 2025 H1 (2024
H1's 184 is mostly the Beanstalk series of small audits). Signal rate here is unique valid High + Medium + Low findings
over all submissions, between 2% and 6% in every half-year with more than one audit. CodeHawks counts lows as
submissions, so its counts and its money per submission are not comparable one-to-one with other platforms'; read them
within the platform. Its First Flights (experience points, not money) ran about every two weeks through 2025 (24 that
year), four more from 29 Jan to 16 Apr 2026, and none since:

| Started in | First Flights | Submissions | Median per flight | Signal rate |
|---|---:|---:|---:|---:|
| 2023 H2 | 6 | 3,399 | 509 | 1.59% |
| 2024 H1 | 12 | 3,138 | 216.5 | 3.95% |
| 2024 H2 | 13 | 3,876 | 291 | 2.68% |
| 2025 H1 | 11 | 5,447 | 525 | 1.82% |
| 2025 H2 | 13 | 4,721 | 285 | 2.35% |
| 2026 H1 | 4 | 1,114 | 265.5 | 4.67% |

### 3.7 Code4rena, 2021-2024: the earlier crowding

Code4rena published a findings repository on GitHub for most of its audits, with one JSON record per submission carrying
the risk label the submitter chose, and the published report, which states how many unique High and Medium findings the
judges accepted. We read 372 of the 376 public repositories; four timed out (Tapioca, Dopex and NextGen in 2023, AI Arena
in 2024). Audits are grouped by start half-year; the 25 mitigation reviews and 9 undated rows are left out.

| Started in | Audits | High + Medium submissions | Median H+M per audit | Median distinct submitters | Signal rate, median audit | Signal rate, pooled |
|---|---:|---:|---:|---:|---:|---:|
| 2021 H1 | 14 | 510 | 29 | 11.5 | 41.2% | 38.42% |
| 2021 H2 | 46 | 1,750 | 28 | 15.5 | 32.4% | 32.86% |
| 2022 H1 | 70 | 6,821 | 77 | 46 | 16.0% | 14.25% |
| 2022 H2 | 51 | 11,557 | 189 | 134 | 6.3% | 6.39% |
| 2023 H1 | 44 | 12,142 | 173 | 118.5 | 4.4% | 5.44% |
| 2023 H2 | 41 | 14,640 | 356 | 142 | 3.0% | 3.40% |
| 2024 H1 | 45 (12 validated-era) | 10,885* | 207* | 88* | 6.8%* | 4.77%* |
| 2024 H2 | 26 (19 validated-era) | 154* | 14* | 4* | 41.2%* | 40.82%* |

\* Full-era audits only (33 in 2024 H1; in 2024 H2, seven small invitational audits). Signal rate = the report's unique
High + Medium findings / High + Medium submissions, for audits whose report gives both counts (13 to 65 audits per
half-year; 5 in 2024 H2).

- **Crowding came first here.** The median audit drew 12 times as many High/Medium submissions in 2023 H2 as in 2021 H1
  (356 against 29), from 142 distinct submitters against 11.5. Over the same two and a half years the pooled share of
  High/Medium submissions that became a distinct valid finding fell from 38.4% to 3.4%. In the median 2023 H2 audit
  about 1 in 33 High/Medium submissions was a unique valid High or Medium.
- **The biggest step was 2022 H1 to 2022 H2:** median submitters 46 to 134, pooled signal rate 14.3% to 6.4%. Audits per
  half-year rose from 14 (2021 H1) to a peak of 70 (2022 H1), then ran at 41-51 to 2024 H1. So on Code4rena the
  crowding grew first while the number of audits was rising, then kept growing after it fell by about a third from the
  peak; on Sherlock and Cantina in 2025-2026 it grew while supply fell 83%.
- **A break in April 2024.** From Renzo (30 Apr 2024) most audits' submissions went first to a separate validation
  repository, and the public findings repository holds only the ones promoted from it. Each promoted record keeps its
  original issue number, so the highest one estimates how many were sent: for the 31 such audits (to Nibiru, Nov 2024),
  7,037 records against about 12,564 submissions. Counting records as submissions would understate those audits by about
  44%, so the series counts them as audits only.
- **The public record stops in December 2024.** No findings repository for a later audit is public. Code4rena kept
  running audits until it announced its wind-down on 13 May 2026, so this census cannot show its 2025-2026 numbers.
- **Cross-checks.** Christoph Michel (2 May 2022) wrote that Code4rena "averaged 10 wardens per contest" at first, "around
  25 towards the end of 2021", and that recent contests saw "as high as 59 wardens". Our median distinct submitters are
  11.5 (2021 H1), 15.5 (2021 H2) and 46 (2022 H1), the same scale. He tied the rise to an influx of new auditors from
  October 2021 and called it "bad for the auditors" because the pots had not grown. Code4rena's own review of 2023
  reports 114 projects and 31,512 bug submissions. We count 85 audits that started in 2023 with 37,187 submissions of all
  types, 26,782 of them labelled High or Medium, plus mitigation reviews and three repositories we could not read.
  Code4rena's figure lies between our two totals, but we could not read its post, so we don't know exactly what it counts.
  We treat this as a check that brackets our numbers, not one that matches them.

## 4. Discussion

Crowding in public audit contests is not new. Code4rena went through it in 2022-2023: more people sent more High/Medium
submissions to each audit, and the share that turned into distinct valid findings fell to 3-5%. That is about the same
range as CodeHawks' 2023-2025 signal rates (2-6%), though the two use different denominators. In that first episode,
Code4rena's audits per half-year first rose (14 to 70) and then settled at 41-51, about a third below the peak. The
2025-2026 episode is different because supply collapsed at the same time. Sherlock,
Cantina and HackenProof each show the same shape: public contests collapsed while the flow of submissions did not, so
each remaining contest is far more crowded and each submission competes for far less money. HackenProof's paid figures
show the same fall in money that actually changed hands, not just in headline pots. Immunefi shows the same contest
collapse. CodeHawks shows the other end of it: a platform that stopped holding contests for 15 months, so no crowding
could build there. Code4rena's wind-down in May 2026 is the extreme case of the same exit. So the platform-wide question
is not only how crowded the remaining contests are, but how many platforms still hold them.

### 4.1 AI-report rules across six audit platforms, on a published rubric

Stingrai's census of 53 general vulnerability-disclosure programs (28 Jul 2026, CC BY 4.0) codes each program's intake
policy into one stance: prohibited ("refused outright, with no stated path to acceptance"), conditional-disclosure,
conditional-human-in-the-loop (acceptance needs human verification or a working reproduction), discouraged ("warned
against or penalised, with no stated condition under which it becomes acceptable") or silent. A proof-of-concept rule
that doesn't mention AI is not coded as an AI policy. None of Stingrai's programs is a Web3 audit platform. We applied the
same definitions to the platform-wide rule text of six audit-contest platforms, read on 15-16 Oct 2026:

| Platform | Rule text (where) | Stance on Stingrai's rubric | Earliest date we can verify |
|---|---|---|---|
| Immunefi | Rules page: "Submitting AI-generated/automated scanner bug reports that lack the required information" (on impact). Researcher terms, s.5 "Prohibited Conduct", item 3, in full: "Automated testing of services without prior authorization that generates significant amounts of traffic or submitting AI-generated/automated scanner bug reports;" | Rules page: conditional (the stated path is the required impact information). The terms alone would code as prohibited | Ban announced Dec 2022; 15 people banned by 11 Jan 2023 (CoinDesk). Current wording undated (terms page "Last Updated 07 September 2026") |
| Code4rena | Submission guidelines: "Using the output of ChatGPT, GPT-3, or automated tools for audit submissions is strongly discouraged"; automated-tool findings carry "a higher burden of proof"; spam including "LLM-generated nonsense" can get an account suspended | Discouraged; conditional if the higher-burden path is read as covering LLM output | Current wording undated |
| Code4rena (Bot Races, historical) | "Code4rena initially made the decision to ban all submissions appearing to have been written by AI", then dropped the ban; 10% of each pool went to Bot Races, a first-hour track for automated tools whose winning report "will be considered the official source for known findings" | Not an intake rule: automated tools admitted as a separate paid track | 4 Apr 2023 (C4's post; first race 12 Apr 2023, Frankencoin). Paused by about Q2 2024, per one bot operator's portfolio |
| Code4rena (V12) | Submission guidelines, "V12 findings considered known issues": "Code4rena runs V12 on all code in C4 competitions"; "V12 findings will be judged as known issues", and "both V12's submissions and any duplicates are ineligible for awards" | Not an intake rule: the platform runs its owner's AI auditor and removes what it finds from the prize pool | 25 Sep 2025 (Zellic's announcement). No C4 audit started between then and 6 Oct 2025; the first two that did (Hybra Finance, 6 Oct; Sequence, 7 Oct) carry the section |
| CodeHawks | Disqualification criteria: "Participants suspected of relying excessively on AI for their submissions risk disqualification." | Discouraged (penalty, no stated path) | No later than 14 Sep 2023 (the commit that added the page to Cyfrin's public docs repo) |
| Cantina | Competition docs: "submitting AI generated findings without validating them can lead to disqualifications or worse, a permanent ban" | Conditional, human in the loop | Undated (no date, version or changelog on the page) |
| HackenProof | Per program, not platform-wide: "AI-generated reports without runable PoC are not accepted" / "...must include human validation" | Conditional, human in the loop | Contests from 16 Jul 2025 (OpenEden), DualDefense audits from 14 Aug 2025 (Coindepo); 61 of 62 programs since 14 Aug 2025 |
| Sherlock | Contest judging criteria: no AI wording. Audit Engine docs: "This page is for AI auditors and security researchers selected for Audit Engine engagements." | Contests: silent. Audit Engine: AI auditors admitted as participants (no category in the rubric) | Both pages undated |

For comparison, Stingrai coded the four general coordination platforms it covers (HackerOne, Bugcrowd, Intigriti,
YesWeHack) as conditional: three human-in-the-loop, one disclosure. None of its 53 programs prohibits AI-written reports.
The audit platforms are spread much more widely. One platform's terms carry the only unqualified prohibition wording
either census contains, although its public Rules page adds a condition. Two penalise AI use with no stated path to
acceptance, and one admits AI auditors as participants. Sherlock's Audit Engine is not the first to do that: Code4rena
admitted automated tools as a separate, paid track from April 2023 until about early 2024, after dropping an early ban
on AI-written submissions that it said it had adopted "like other peers in the open audit space". Of those peers, only
Immunefi's ban (Dec 2022) is documented in our sources.

Most of the rules (Immunefi, Code4rena, CodeHawks) trace to 2022-2023, before the 2025-2026 contest collapse; Cantina's
can't be dated. Two dated changes fall inside the collapse: HackenProof's per-program rules from July 2025, and Code4rena's
V12 rule from 25 September 2025. So AI-report rules can't be read as a single response to the collapse. HackenProof is the
only platform where they can be placed against the money series (section 3.4), and there they arrive as paid money per
submission starts to fall.

The V12 rule is a different kind of answer to AI, and it reverses Bot Races. The other platforms regulate what
researchers may submit. In 2023 the winning bot's report set the known issues and its crew was paid from the pool. From
September 2025 Code4rena's owner, Zellic (which acquired it in August 2024), ran its own AI auditor on every contest's
code and published the output in the contest repo, "typically within the first two days". Anything V12 found, and every
duplicate of it, could no longer earn money, and nobody in the contest was paid for finding it. Zellic's announcement gave
the aims as deterring AI spam, getting better-quality submissions and saving clients money. The rule started cleanly at
a contest boundary. The two audits we read that were running on 25 Sep 2025 (Monad and Succinct, neither of them
Solidity code, which is what V12 was announced for) did not add a V12 section. No audit started in the next ten days, and
the first two to start after that, both Solidity, carry the section from day one. The public Code4rena data in section
3.7 ends in December 2024, before the rule, so we make no before/after comparison.

Cantina's dated competition pages don't settle its rule's date. None of the four we read mentions AI: size-solidity
(26 Feb-12 Mar 2025), PumpSwap (21 Mar-4 Apr 2025), Liquity V2 (21 Mar-27 Apr 2025) and Revert v4lend (6 Oct-3 Nov 2026).
Each sets its own proof-of-concept rule instead: a coded PoC for every High and Medium (size-solidity), for every Critical
and High (PumpSwap), a "mandatory POC rule" that names no severities (Liquity V2), and a coded PoC for every Critical,
High and Medium from every researcher, with no reputation exemption (v4lend). Two of the 2025 pages put another tool's
automated findings (a Lightchaser report) out of scope: the same known-issues mechanism as Bot Races and V12, applied per
contest. Four pages are not a series, so we don't claim a trend from them.

**A prediction written down before testing.** If Code4rena's audit READMEs are read section by section, audits whose
README links a winning bot report or an "Automated Findings" section should begin in April 2023 (Frankencoin first) and
stop by about March-April 2024, with none after mid-2024; and every Solidity audit from Hybra Finance (6 Oct 2025) on
should carry a V12 section. Our Code4rena census read READMEs only for dates, pot and code size, so it cannot test this.
A bot-race section after June 2024, or a Solidity audit after 6 Oct 2025 without a V12 section, would contradict it.

Limits of this coding: one coder, platform rule text only (program briefs are left out, except HackenProof's, which carry
the rule); the stance for Immunefi depends on which of its two documents is taken as the intake policy, and Code4rena's
is borderline, so both readings are given. Git and post dates show when wording was published, not when it was enforced.
The V12 date is the announcement's: Zellic's own newsletter gives 25 Sep 2025, and a repost of the blog post is dated
24 Sep; we use Zellic's. We read the READMEs of the four C4 audits around that date as they stand today, so a section
added and later removed would not show. The third audit running on 25 Sep (LayerZero Endpoint V2 on Sui, Move code,
started 17 Sep) has a README that is no longer public, so it was not read. The Bot Races post is quoted as a web search
engine indexed it, because medium.com refused our fetcher, and the end of Bot Races comes from one participant's
portfolio, not from Code4rena.

What the data cannot show: whether the same researchers now send more findings each (for example with AI tools), or more
people take part. Code4rena's records allow a distinct-submitter count for 2021-2024, but none of the other platforms
publishes one in the same fields, or valid-only counts per contest. The HackenProof timeline is timing, not cause.

## 5. Prior art and what is new

- Immunefi, "What We're Learning About Audit Competitions" (23 Sep 2026, on X): cross-platform contest counts (89 started
  in Q4 2024, 11 in Q2 2026), Cantina from 40 competitions in Q1 2025 to one so far in Q3 2026, CodeHawks with one
  competition since mid-2025, and a duplicate-finding case study (Quantus: 232 submissions from 98 researchers, one High
  reported by 25 people). Our contest-count drop agrees and is not claimed as new.
- Christoph Michel, "Code4rena - First 1M$ stats" (2 May 2022): one participant's account of early Code4rena, with wardens
  per contest rising from about 10 to about 25 in 2021 and up to 59 in spring 2022, and falling hourly earnings. It has no
  series past spring 2022 and no signal rates. Our 2021-2022 submitter counts agree with it.
- `0237h/code4rena-scraper` (archived) turns Code4rena reports into per-submission tables, `0237h/code4rena-stats`
  tabulates awarded findings, and `carrotsmuggler/c4-table` builds a per-participant table for one repository at a time.
  These are Code4rena-only tools, without half-year series, signal rates or the April 2024 break.
- Stingrai (Arafat Afzalzada), "Who Actually Bans AI-Written Bug Reports: A Census of Disclosure Program Policies"
  (28 Jul 2026, data CC BY 4.0): a one-day snapshot of AI-report policies on 53 programs (4 coordination platforms, 20
  vendor programs, 29 open-source projects). No Web3 audit platform, no dates. Section 4.1 reuses its rubric and is new
  in applying it to audit platforms and in dating the rules. Stingrai sells AI security tooling.
- Zellic, "Introducing V12" (announced 25 Sep 2025): announces V12 and its use as a known-issues filter in Code4rena
  contests and bug bounties. A primary source for the V12 row, not a census. Zellic's October 2025 newsletter adds that
  the aim is for V12 to be "at least as good as the worst auditing firms" and that it "doesn't replace a proper audit".
- The Breach Ledger, "What Showed Up in the Logs After the Rewards Were Paid" (13 Oct 2026): researchers' criticism of
  Sherlock's deprecation of its old contest platform and Jack Sanford's reply about false positives; no statistics.
- Alec Novella, "Are Audit Contests Still Worth It? What 2026 Is Actually Telling Us" (Medium, 20 Feb 2026): an essay
  arguing that contests still find bugs other reviews miss and that payout design drives submission quality. Read only
  through a search excerpt (HTTP 403 to our fetcher); the excerpt has no series.
- smartcontractaudit.com, "Competitive audit platforms 2026" (updated 9 Oct 2026): a platform comparison with single
  figures; no time series and nothing on AI-report rules.
- m3dython.com, "Cantina Review 2026": seen only as a search-result title; the site returned HTTP 522 to our fetcher three
  times on 16 Oct 2026, so we have not read it.

New here, as far as we can find: per-platform contest AND submission series from primary pages; headline prize money per
submission, pooled and per contest; money actually paid per submission (HackenProof); a Code4rena series of submissions,
distinct submitters and signal rate across 2021-2024, with the April 2024 validation-repository break documented; a
complete CodeHawks census checked against the platform's own listings, with the practice-copy pitfall documented; a dated
per-program record of AI-report rules on an audit-contest platform; a rubric-coded, dated comparison of AI-report rules
across six audit platforms, with the first contest under Code4rena's V12 rule pinned down; and a live contest's arrival
curve.

## 6. Limits

Counts include invalid, duplicate and spam submissions (and, on CodeHawks, lows). Code4rena's risk labels are as
submitted, not as judged, and QA reports can be promoted, so its signal rate is approximate; its "distinct submitters"
counts handles, so a team counts once and bot-race entries count too. Headline pots are not payouts. Private and
invite-only work is invisible. Half-years with few contests (2026 H1: 12-13 on Sherlock+Cantina, 3 on Immunefi; every
CodeHawks half-year after 2024; Code4rena 2024 H2) give rough medians. Token pots (OP, HAI, JTO, ETH and others) are left
out of dollar figures or taken at the USD the page states, never converted silently. Contests are grouped by start date.
Every figure is a snapshot of pages as fetched on 14-16 Oct 2026. Immunefi's leaderboard sizes change meaning in
mid-2025 (section 3.2). Code4rena's 2024 figures after April are not comparable with earlier ones, and four of its
repositories could not be read. AI-report rules are dated only through start dates (HackenProof), a git commit
(CodeHawks) and dated posts (Immunefi, Code4rena, Zellic). Sitemaps can list pages that are not contests: CodeHawks'
lists 228 self-paced practice copies of two First Flights, which a naive scrape would count as 210 First Flights in 2026
instead of 4. We filter them by their slug form and check the result against the platform's listing pages. Compute hosts
matter too: one parse-only re-run of the Immunefi census found none of the pages saved by the first run, because they
were on another host's volume. It ended with 0 records instead of wrong ones, which is how a re-run should fail. Reposts
can carry a different date from the original: the V12 post's repost is a day earlier than Zellic's own date. Several
sources (the Immunefi article on X, the Code4rena Bot Races post, the Medium essay) were read only through search
excerpts, because their sites refused our fetcher; we say so wherever we use them.

## 7. Reproduce

Repository: https://github.com/munimtechnologies/audit-contest-ai-rules (v0.9.0).

| Section | Script (each has a `test_*.py` that pins the numbers) | Data (CC BY 4.0) |
|---|---|---|
| 3.1 | `cross_platform.py`, `sherlock_crowding.py`, `cantina_crowding.py` | `data/sherlock_contests.csv`, `data/cantina_census.csv` |
| 3.2 | `immunefi_series.py` (census: `fetch_immunefi.py`) | `data/immunefi_contests.csv` |
| 3.3 | `prize_per_submission.py` | as 3.1 |
| 3.4 | `hackenproof_payouts.py`, `hackenproof_trends.py` | `data/hackenproof_programs.csv`, `data/hackenproof_programs_fetched.csv` |
| 3.6 | `codehawks_series.py` | `data/codehawks_contests.csv` |
| 3.7 | `c4_series.py` (census: `fetch_c4.py`, `c4_crowding.py`) | `data/c4_contests.csv`, `data/c4_summary.json` |
| 4.1 | | `data/platform_ai_rules.csv` (one row per platform document: URL, verbatim clause, stance, date and date source) |

Each script prints its table with `--table`. Section 3.5's readings are not in the repository yet; they will be added
with the final count.

## Sources

Read 14-16 Oct 2026 unless noted. "Search excerpt" means the page refused our fetcher and the text comes from a web
search engine's copy.

- Sherlock contest API: https://mainnet-contest.sherlock.xyz/contests ; judging guidelines:
  https://docs.sherlock.xyz/audits/judging/guidelines ; Audit Engine: https://docs.sherlock.xyz/audit-engine/for-participants
- Cantina competitions API: https://cantina.xyz/api/v0/competitions ; competition rules:
  https://docs.cantina.security/standards/severity/competition ; Revert v4lend:
  https://cantina.xyz/competitions/e275368c-547d-4d91-a418-053ad31082a8
- Immunefi competitions: https://immunefi.com/audit-competition/ ; Rules: https://immunefi.com/rules/ ; researcher terms
  as served on a program's safe-harbor page ("Last Updated 07 September 2026"):
  https://immunefi.com/bug-bounty/originprotocol/safe-harbor/ ; CoinDesk, 17 Jan 2023:
  https://www.coindesk.com/tech/2023/01/17/crypto-whitehat-platform-immunefi-banned-15-chatgpt-generated-bug-reports-heres-why ;
  "What We're Learning About Audit Competitions", 23 Sep 2026 (search excerpt):
  https://x.com/immunefi/status/2102715623218557375
- HackenProof audit programs: https://hackenproof.com/audit-programs (listing pages and each program page)
- CodeHawks: https://codehawks.cyfrin.io/contests , https://codehawks.cyfrin.io/first-flights ; AI rule:
  https://github.com/Cyfrin/codehawks-docs/blob/main/judging/disqualification-criteria.md (added in commit 9fc66d1,
  14 Sep 2023)
- Code4rena findings repositories: https://github.com/code-423n4 ; submission guidelines:
  https://docs.code4rena.com/competitions/submission-guidelines ; audits listing: https://code4rena.com/audits ; V12
  sections: https://github.com/code-423n4/2025-10-hybra-finance and https://github.com/code-423n4/2025-10-sequence ;
  "New to Code4rena: Bot Races", 4 Apr 2023 (search excerpt):
  https://medium.com/code4rena/new-to-code4rena-bot-races-91b8f4ca0b18 ; LightChaser portfolio (Bot Races paused):
  https://github.com/ChaseTheLight01/portfolio
- Zellic acquires Code4rena, The Block, 22 Aug 2024: https://www.theblock.co/post/312583/zellic-code4rena ; Zellic
  Security Roundup, October 2025 (V12 date): https://newsletter.zellic.io/p/zellic-security-roundup-october-25 ; V12
  announcement: https://x.com/zellic_io/status/1971228712147485185 (its post ID decodes to 25 Sep 2025, 15:02 UTC); repost
  of "Introducing V12": https://securityboulevard.com/2025/09/introducing-v12/ (original
  https://www.zellic.io/blog/introducing-v12 returned 404 on 16 Oct 2026)
- Christoph Michel, "Code4rena - First 1M$ stats", 2 May 2022: https://cmichel.io/code4rena-first-1m-stats/
- Stingrai census: https://www.stingrai.io/blog/ai-generated-vulnerability-report-policies-census ; data:
  https://www.stingrai.io/data/ai-report-policy-census/policies.csv
- The Breach Ledger, 13 Oct 2026: https://thebreachledger.substack.com/p/what-showed-up-in-the-logs-after

---

*MV2 of Munim, Inc. Made with AI agents working for MV2.*
