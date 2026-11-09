# Fewer contests, more submissions, less money each: a census of public smart-contract audit contests on six platforms, 2021-2026

Preprint, version 2.0 (9 November 2026). Not peer reviewed.

MV2 of Munim, Inc. (mv2@munimtech.com). The data collection, analysis, code and this text were made with AI agents working
for MV2. Text: CC BY 4.0. Code: Apache-2.0. Data and code: https://github.com/munimtechnologies/audit-contest-ai-rules
(release v0.10.0). Corrections are welcome as issues on that repository.

**Changes from version 1.9 (6 November 2026).** Entries 1-8 of `paper/CORRECTIONS.md` are folded in. Section 3.5 now
reports the pre-registered test of whether Revert v4lend's findings count moved in judging (it did not; entry 7) and
later readings. A new section 3.8 reports a pre-registered census of how long Cantina takes to judge a competition,
which failed its gate: the Internet Archive is too thin to answer the question (entries 6 and 8). Section 2 now says
that the census can miss public contests run outside the endpoint it was built from (entry 1). Section 4.1 adds
Sherlock's payout criteria and its documentation's notice that Audit Engine is replacing audit contests (entries 2
and 3). No census number from version 1.9 changes.

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

One contest was also measured as it ran. Cantina's Revert v4lend competition ($50,000 USDC) showed 7,079 submitted
findings when it moved to judging, about $7.06 of pot per submitted finding, and its public counter kept rising for at
least 56 hours after the contest's end time while the page still said "Live". A test written down before it was read
predicted that the count would not move in judging, and it held: the count still read 7,079 more than five days after
the end. We also pre-registered a census of how long Cantina's judging takes, read from the Internet Archive's copies
of its competition pages. It failed its gate (0 of 142 competitions eligible, at least 20 needed): the archive cannot
date the end of judging to within 14 days for any competition, so that question stays open.

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
duplicate and spam reports. Private contests and invite-only engagements (Cantina private contests, CodeHawks private
and invite-only audits, and most Sherlock Audit Engine engagements) are not in the public series. Not every Audit
Engine engagement is private, though: at least one was a public $400k contest (Aerodrome, section 6), and Sherlock's
contest API, which our Sherlock series is built from, does not list it. So the census can miss public contests that a
platform runs outside the endpoint it was built from (correction 1).

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

Aerodrome's public Audit Engine contest (section 6) started in 2026 Q3, so it would add a third contest to the 2026 Q3
row, but its submission count is not public and it cannot enter the submission or per-contest columns. It does not
touch the 2024 H1 to 2026 H1 comparisons.

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
includes lead-auditor and judging pay, and some pots pay in full only if a High is found. Aerodrome's $400k Audit
Engine contest (section 6) is not in the 2026 H2 row, because its submission count is not public.

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

### 3.5 A live contest, measured as it fills and into judging (Cantina, Revert v4lend)

Cantina's Revert v4lend competition (6 Oct-3 Nov 2026, $50,000 USDC, KYC to join) shows a public "Findings submitted"
counter. We read it 104 times between 14 Oct and 6 Nov 2026 (`v4lend/v4lend_findings_count.csv`); each of the last 20
values was read twice, and the two reads agreed. The counter never fell. The contest page gives only the end date;
Cantina's API gives the end time, 2026-11-03 18:30 UTC. Every value is the counter as a page-reading tool reported it,
not an API value; the one API value we took during the contest (14 Oct, 1,369) falls between the two page readings
around it.

- **Up to the end.** The count rose from 1,282 (14 Oct 09:55 UTC) to between 6,327 and 6,726 at the end: those are the
  last reading before it (2 h 38 min earlier) and the first after it (18 h 45 min later). That is about 10 to 11 an hour
  overall. Day-long windows, each from the reading nearest one 00:00 UTC to the reading nearest the next (15 Oct to
  3 Nov), ran between about 4.7 and 24.9 an hour. The pace rose in the second half instead of fading: about 4.7 to 6.8
  an hour from 15 to 23 Oct, about 13 to 14 an hour on 28 to 30 Oct, and 788 findings in the 25.2 hours to 3 Nov
  15:52 UTC (about 31 an hour), the fastest window between consecutive readings in the series. No reading fell near
  00:00 UTC on 1, 2 or 3 Nov, so the day-table rows for 31 Oct, 1 Nov and 2 Nov span 16.8, 35.7 and 9.5 hours, not one
  day; the highest day-table rate, 24.9, is the 9.5-hour row. An earlier hand-built version of this table mixed two
  anchor rules for three days; the published table uses the nearest-reading rule throughout.
- **Two predictions written before the late data.** (P1) The last 72 hours before 3 Nov 00:00 UTC would run faster per
  hour than the three days before. It held: about 18.2 against 14.4 an hour, both windows anchored on the reading of
  31 Oct 00:35 UTC. It was graded on the reading of 2 Nov 14:40 UTC, 9 h 20 min early, because the planned reading slot
  was missed; that reading had already cleared the bar. With the real end time, the last 72 hours (31 Oct to 3 Nov,
  18:30 UTC) ran between about 18 and 28 an hour (not pre-registered). (P2) The final count would land between about
  3,940 and 4,490. It failed on 31 Oct (4,503). The projection assumed a 00:00 UTC close and the pace of the time, and
  it missed both the extra 18.5 hours and the late rush.
- **After the end.** The page and the API kept saying "Live", and the counter kept rising: 6,726, 6,906, 6,909 and
  7,079 at about 19, 39, 43 and 56 hours after the end, in bursts (3 in one 4-hour stretch, 170 in the next 13 hours).
  Two more pre-registered checks failed: that the count would stay at 6,726 (it did not), and that the rate after the
  end would fall below about 8.9 an hour (it was about 10 an hour over 17 hours). Between about 56 and 61 hours after
  the end, the page and the API switched to "Judging", at 7,079. So between 353 and 752 findings were added after the
  end. The counter cannot tell late submissions from judge-created duplicates or escalations, and Cantina's
  documentation does not say what it includes.
- **In judging (pre-registered test held).** Version 1.9 wrote down a test before it was read: a reading at least 24
  hours after 6 Nov 2026, 07:10 UTC, predicted to equal 7,079. On 7 Nov 2026 Cantina's API showed status `judging` and
  7079 findings at 12:14:30 UTC (machine-recorded by a job), and a second API read and two reads of the page, at about
  12:45-12:50 UTC, showed "Judging" and "7,079". **The prediction held** (correction 7). Later page readings showed the
  same, "Judging" and "7,079", at about 23:25 UTC on 8 Nov and about 01:15 UTC on 9 Nov 2026, about 5.3 days after the
  end (page-reading tool, approximate times). So all of the 353 to 752 findings added after the end came in before
  judging began, and none had been added in judging by these readings. These later readings are not in the 104-reading
  data set (`v4lend/` is unchanged). The competition had not reached "complete" by 9 Nov 2026, so how long its judging
  takes is not yet known; section 3.8 explains why the archive could not answer that for earlier competitions either.
- **Money.** $50,000 over 7,079 is about $7.06 of pot per submitted finding (between $7.43 and $7.90 on the count at the
  end). A submitted finding is not a valid one: the page shows no judged count, so this is the pot averaged over every
  submission, not what a valid finding earns.
- **Reading an end time off a relative label.** Before we found the API's end time, we inferred it from the contest
  list's countdown label ("Ends in 7 days" ... "Ends in 3 hours", 13 reads from 28 Oct to 4 Nov) under three display
  rules. Only rounding to the nearest day fitted every read, and it put the end between 18:25 and about 18:38 UTC on
  3 Nov, which contains the API's 18:30. The same end value was already in our own published 14 Oct API snapshot
  (`data/cantina_census.jsonl`), which we did not consult while inferring it, so the method was tested blind by
  accident. Of the two checks written down for it, one held (the label changed from 4 to 3 days inside the window
  predicted for 31 Oct) and one was never read (a reading in the 3 Nov 00:00-03:00 UTC slot); we report the second as not tested.

The contest requires a coded proof of concept for every Critical, High and Medium finding, from every researcher. One
web search (2 Nov 2026) found no other public series of submission counts taken during an audit contest, and one more
(5 Nov 2026) found no source on counters that keep rising after a contest's end; two searches are not a survey.

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

A re-read of the audit list on 6 Nov 2026 still showed 45 audits, the newest being Cyfrin's BattleChain Confidence Pools
(July 2026), so the 2026 H2 row is unchanged.

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

### 3.8 How long does Cantina's judging take? A pre-registered census the archive could not answer

Section 3.5 follows one competition into judging. Whether its pace is typical needs the judging time of many
competitions, and Cantina's API gives only each competition's current status, not when it changed. After version 1.9
we pre-registered a census of judging duration (`paper/cantina-judging-duration-PREREGISTRATION.md`, 6 Nov 2026,
23:51 UTC): five predictions (P1-P5), a rule that a competition is eligible only if the change to `complete` can be
placed inside a bracket of at most 14 days, and a gate of at least 20 eligible competitions, below which P1-P5 are
reported as not testable. Three addenda, each public before the step it governs, moved the source and fixed the
reading rules; none changed a prediction, the 14-day rule or the gate.

| Stage | Source | Result |
|---|---|---|
| Primary | Internet Archive captures of Cantina's competitions API | **0** captures found (7 Nov 2026): 0 eligible, not testable from this source |
| 1, timing bound (addendum 1) | capture times of archived competition pages, no content | 131 of 142 ended competitions have a capture after their end; at most **68** could be eligible |
| 2, page format | all 882 main-page captures taken after an end, counts only | 528 show a readable status (461 `completed`, 67 not yet complete); **354 (40%) show none** |
| 3, census (addenda 2 and 3) | the cached stage-2 pages, inputs matched to the published counts | **0 of 142 eligible**; narrowest completion bracket 18.07 days; gate failed |

**Outcome: P1-P5 are not testable** (corrections 6 and 8). 125 competitions have a readable `complete` capture after
their end, so a completion bracket exists for them, but none is 14 days wide or less: the five narrowest are 18.1,
18.5, 19.5, 22.3 and 22.3 days. The stage-1 figure of 68 counted any short gap between capture times. A competition
is eligible only if the short gap holds the change to `complete` and both sides of it show a readable status. 40% of
the captures show none, readable captures of any Cantina competition fall on only 1 to 5 days a month, and none is
dated after July 2026 (all 52 captures served from August 2026 on show no status). The census ran as job
`cantina-pages-census-v2` on 8 Nov 2026, 19:52:20-19:53:43 UTC. Its offline tests passed first, and it checked that its
inputs reproduced the published stage-2 counts exactly (882 selected, 882 cached, 528 with a status), so its grade is
the pre-registered census.

Reading checks: 521 captures were read (354 had no status, 6 duplicated another capture's served time, 1 was served
from a time not after the end). In all 521 the visible status and the embedded JSON status agree, and in all 427
captures that show both a visible and a JSON findings count, the two are equal. No competition went back from
`complete` to another status in a later capture.

Descriptive only, because the gate failed, so none of these grades a prediction:

- In all 27 competitions whose earliest non-`complete` capture after the end shows a findings count above 0, that
  count equals the count in Cantina's API today. This fits section 3.5's reading that v4lend's count stopped moving
  once judging began, but it is not a test of it.
- Four competitions that ended inside the archive's coverage still showed a non-complete status 60 days or more after
  their end; the longest showed `reviewing escalations` 233.7 days after its end. That is what the archived page
  displayed; we cannot tell from it whether the page was up to date.
- Five competitions have a judging-start bracket of at most 3 days, and in all five the first capture past `live` came
  within 2.6 days of the end. Section 3.5's v4lend switched between 56 and 61 hours (about 2.3-2.5 days) after its end.
- All 86 captures with a findings count of 0 got it from embedded JSON, in captures dated 17 Apr 2024 to 26 Mar 2025,
  and 64 of them are on pages already showing `completed`. We read those zeros as an unfilled field, not a count; that
  is our interpretation, not part of the rule.

So nothing about how long Cantina's judging takes can be concluded from the archive. P1-P5 are not re-tested on
another source without a new, separately published pre-registration. The lesson for anyone attempting the same: a
bound computed from capture times alone (68) badly overstated what the pages could support (0), because 40% of the
pages carry no status and crawls cluster on a few days. A gate should count captures with a readable status, not
capture times. The one source that can answer the question is direct reading of live competitions over time, as with
v4lend in section 3.5. Full result, every bracket and every capture: `paper/cantina-judging-duration-result.md` and
`cantina_judging/`.

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

Sherlock's own pages point the same way, though they disagree with each other. Its documentation page "Meeting the
Payout Criteria" (undated, read 9 Nov 2026) says that the option to "unlock past unearned audit contest payouts will
end after February 6th, 2027", "due to Audit Engine replacing audit contests". Its blog post "Why We Built Sherlock
Audit Engine" (dated 19 Aug 2026 on the page as read 9 Nov 2026; correction 2 gave 20 Aug) says instead that Audit
Engine "sits alongside Sherlock's Collaborative Audits, Audit Contests, and Blackthorn reviews". Sherlock's contest
API has listed no running or scheduled contest in any of our readings from 14 Oct to 9 Nov 2026, and the newest
contest in it started on 20 Jul 2026. We don't claim that Sherlock has ended contests: its blog says otherwise, and the
notice concerns payouts (correction 2).

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
| Code4rena (Bot Races, historical) | "Code4rena initially made the decision to ban all submissions appearing to have been written by AI", then dropped the ban; 10% of each pool went to Bot Races, a first-hour track for automated tools whose winning report "will be considered the official source for known findings" | Not an intake rule: automated tools admitted as a separate paid track | 4 Apr 2023 (C4's post; first race 12 Apr 2023, Frankencoin). Paused by about Q2 2024, per one bot operator's portfolio; the last README with bot-race wording is Coinbase's (14 Mar 2024) |
| Code4rena (V12) | Submission guidelines, "V12 findings considered known issues": "Code4rena runs V12 on all code in C4 competitions"; "V12 findings will be judged as known issues", and "both V12's submissions and any duplicates are ineligible for awards" | Not an intake rule: the platform runs its owner's AI auditor and removes what it finds from the prize pool | 25 Sep 2025 (Zellic's announcement). No C4 audit started between then and 6 Oct 2025; the first two that did (Hybra Finance, 6 Oct; Sequence, 7 Oct) carry the section |
| CodeHawks | Disqualification criteria: "Participants suspected of relying excessively on AI for their submissions risk disqualification." | Discouraged (penalty, no stated path) | No later than 14 Sep 2023 (the commit that added the page to Cyfrin's public docs repo) |
| Cantina | Competition docs: "submitting AI generated findings without validating them can lead to disqualifications or worse, a permanent ban" | Conditional, human in the loop | Undated (no date, version or changelog on the page) |
| HackenProof | Per program, not platform-wide: "AI-generated reports without runable PoC are not accepted" / "...must include human validation" | Conditional, human in the loop | Contests from 16 Jul 2025 (OpenEden), DualDefense audits from 14 Aug 2025 (Coindepo); 61 of 62 programs since 14 Aug 2025 |
| Sherlock | Contest judging criteria: no AI wording. Audit Engine docs: "This page is for AI auditors and security researchers selected for Audit Engine engagements." | Contests: silent. Audit Engine: AI auditors admitted as participants (no category in the rubric), but set per engagement: the first open engagement we saw (Uniswap, Nov 2026) was "only for human researchers, not purposefully built AI tools" (section 6) | Both pages undated |

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

**A rule on invalid submissions that says nothing about AI.** Sherlock's "Meeting the Payout Criteria" page (read
9 Nov 2026) sets two "Audit Contest Payout Criteria": "Until you've submitted 2 valid issues with your Watson account,
you will not receive USDC payouts", and an account's "issues ratio" (valid issues over all issues submitted) "must be
>=20%", counting only "contests that started on or after July 1st, 2023". Payouts withheld under them are paid "in
full" once both criteria are met, and the page says they replaced an earlier "USDC penalty" for invalid issues. The
rule names no AI, so on the rubric Sherlock's contest stance stays silent. It is the only platform-wide rule in our
sources that ties pay to an account's share of valid submissions, and it dates from 2023, before the contest collapse
(correction 3).

**A charge per report: a different response to crowding.** Two platforms now ask for money with each report. Each
Immunefi audit competition that started from 12 Aug 2026 (Firelight, Quantus, ENS) says on its information page: "A
submission fee, set and managed by Immunefi, applies to each report and is shown at submission time." The pages state no
amount, and the two latest competitions before them (Firedancer V1 and Base Azul, both April 2026) carry no such
sentence. The sponsor of Firedancer V1, Jump Crypto, wrote afterwards that for that contest it "introduced a $100 fee per
submission alongside a platform-enforced rate limit of one submission per researcher per day" (part of a longer
sentence, read 4 Nov 2026), and that "The 809 submissions show that the fee was obviously not a problem."
Sherlock asks for a $250 stake with each bug-bounty report, refunded if the issue is valid (Sherlock post of 31 Aug 2026).
Neither charge applies to the contests in the crowding series: Immunefi's competitions are not in that series, and
Sherlock's stake is for its bug bounties. A charge puts a price on duplicate and low-effort submissions whoever wrote
them; the rules in the table instead regulate what may be submitted. Immunefi's article of 23 Sep 2026 explains its fee as
paying for triage, which costs the same for a duplicate as for a first report (read through a search excerpt). Jump's
post on Firedancer V1 gives the one sponsor-published view of the AI share we found: 809 reports from 162 researchers in
30 days, 127 unique non-insight security submissions (about 6.4 reports per unique one, our arithmetic), "nearly half of
valid submissions were duplicates", and "we believe nearly every submission was either discovered or written by an
agent". That last figure is the sponsor's belief, not a measurement, and it is one contest. Jump's new standing program
asks for a 1 SOL burn per submission and caps each section at 3,000 characters.

The V12 rule is a different kind of answer to AI, and it reverses Bot Races. The other platforms regulate what
researchers may submit. In 2023 the winning bot's report set the known issues and its crew was paid from the pool. From
September 2025 Code4rena's owner, Zellic (which acquired it in August 2024), ran its own AI auditor on every contest's
code and published the output in the contest repo, "typically within the first two days". Anything V12 found, and every
duplicate of it, could no longer earn money, and nobody in the contest was paid for finding it. Zellic's announcement gave
the aims as deterring AI spam, getting better-quality submissions and saving clients money. The rule started cleanly at
a contest boundary. The two audits we read that were running on 25 Sep 2025 (Monad and Succinct, neither of them
Solidity code, which is what V12 was announced for) did not add a V12 section. No audit started in the next ten days, and
the first two to start after that, both Solidity, carry the section from day one (15 of the 16 Solidity audits from then
on do; Brix Money does not). The public Code4rena data in section 3.7 ends in December 2024, before the rule, so we make
no before/after comparison.

Cantina's dated competition pages don't settle its rule's date. None of the four we read mentions AI: size-solidity
(26 Feb-12 Mar 2025), PumpSwap (21 Mar-4 Apr 2025), Liquity V2 (21 Mar-27 Apr 2025) and Revert v4lend (6 Oct-3 Nov 2026).
Each sets its own proof-of-concept rule instead: a coded PoC for every High and Medium (size-solidity), for every Critical
and High (PumpSwap), a "mandatory POC rule" that names no severities (Liquity V2), and a coded PoC for every Critical,
High and Medium from every researcher, with no reputation exemption (v4lend). Two of the 2025 pages put another tool's
automated findings (a Lightchaser report) out of scope: the same known-issues mechanism as Bot Races and V12, applied per
contest. Four pages are not a series, so we don't claim a trend from them.

**A prediction we wrote down, then tested, and that failed.** Paper v1.8 predicted that Code4rena audit READMEs with a
winning-bot report or an "Automated Findings" section would begin in April 2023 (Frankencoin first) and stop by about
mid-2024, and that every Solidity audit from Hybra Finance (6 Oct 2025) on would carry a V12 section. We then
pre-registered a test (`paper/c4-readme-sections-PREREGISTRATION.md`) and read all 481 public `code-423n4`
repositories named by month: 442 audits and 39 mitigation reviews, which we left out (`data/c4_readme_sections.csv`).
Both parts were contradicted.

- The section is older than the bot race and outlived it. It first appears on 31 Jan 2023 (Canto Identity: "Automated
  findings output for the contest can be found here within an hour of contest opening"), about ten weeks before
  Frankencoin, and 60 audits that started after 30 Jun 2024 still have it. From 2024 on it mostly carried 4naly3er
  static-analysis reports instead: 34 of 55 audits in 2024H2, 20 of 23 in 2025H1 and 6 of 22 in 2025H2 have the
  section, and none of the 7 in 2026H1. The last README linking a 4naly3er report is GTE Perps (28 Aug 2025); the last
  with the heading at all is Monad (15 Sep 2025).
- V12 reached 15 of the 16 Solidity audits that started on or after 6 Oct 2025, not all of them. Brix Money (26 Nov
  2025) names 15 Solidity files in scope and has no V12 section or mention.

A narrower reading that counts only the bot-race wording (plus "automated findings output" without 4naly3er) matches
the end date: its last audit is Coinbase (14 Mar 2024), and none starts after June 2024. But we defined it after
looking at one README by hand (SecondSwap, 9 Dec 2024), so it is post hoc, and it still starts in January 2023, not
April. The prediction got wrong what the section is. It marked automated pre-audit output of any kind, not the bot
race alone. Correction 4 in `paper/CORRECTIONS.md` records this.

| Half | Audits | "Automated Findings" heading | Bot-race wording | 4naly3er | Solidity | Solidity with V12 |
|---|---:|---:|---:|---:|---:|---:|
| 2022H2 | 50 | 0 | 0 | 0 | 48 | 0 |
| 2023H1 | 43 | 31 | 10 | 0 | 41 | 0 |
| 2023H2 | 47 | 45 | 41 | 15 | 47 | 0 |
| 2024H1 | 58 | 41 | 13 | 39 | 41 | 0 |
| 2024H2 | 55 | 34 | 0 | 30 | 32 | 0 |
| 2025H1 | 23 | 20 | 0 | 16 | 15 | 0 |
| 2025H2 | 22 | 6 | 0 | 5 | 16 | 10 |
| 2026H1 | 7 | 0 | 0 | 0 | 5 | 5 |

2021H1-2022H1: 137 audits, one heading (a misnamed repository, below), no bot-race wording, no V12. Halves use the
README's `Starts` line (384 audits) or else the repository name's month (58).

Limits of this coding: one coder, platform rule text only (program briefs are left out, except HackenProof's, which carry
the rule); the stance for Immunefi depends on which of its two documents is taken as the intake policy, and Code4rena's
is borderline, so both readings are given. Git and post dates show when wording was published, not when it was enforced.
The V12 date is the announcement's: Zellic's own newsletter gives 25 Sep 2025, and a repost of the blog post is dated
24 Sep; we use Zellic's. We read the READMEs of the four C4 audits around that date as they stand today, so a section
added and later removed would not show. The third audit running on 25 Sep (LayerZero Endpoint V2 on Sui, Move code,
started 17 Sep) has a README that is no longer public, so it was not read. The Bot Races post is quoted as a web search
engine indexed it, because medium.com refused our fetcher, and the end of Bot Races comes from one participant's
portfolio, not from Code4rena. The README test reads READMEs as they stand today, so a section added and later removed
would not show; a Solidity audit counts only if its README names a `.sol` file; private or deleted repositories are
invisible. One repository, `2022-01-dev-test-repo`, holds the notice of an invite-only Panoptic audit from November
2023; the pre-registered rule dates it by its name (January 2022). Leaving it out changes no verdict (11 other audits
before 1 Apr 2023 and 60 after 30 Jun 2024 remain).

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
- "Web3 Audit Contest Aggregator", a paid community Actor on Apify (`tactful_anvil/web3-audit-contest-aggregator`,
  changelog 0.1.1 dated 16 Sep 2026; page re-read 4 Nov 2026): returns contests from Code4rena, Sherlock, CodeHawks and
  Cantina in one schema, priced per result. It is a feed of contest listings, like this repository's
  `audit_contest_feed.py`, and has no submission counts, prize-per-submission figures or AI-report rules. We note it so
  the feed tool is not read as the first of its kind; the census, not the feed, is what this paper adds.
- m3dython.com, "Cantina Review 2026": seen only as a search-result title; the site returned HTTP 522 to our fetcher three
  times on 16 Oct 2026, so we have not read it.
- Five 2025-2026 papers measure what AI agents can do on smart-contract security tasks, rather than counting contests or
  their rules. EVMbench (Wang, Bigger, Xu, Lin, Applebaum, Patwardhan, Yukseloglu, Watkins; arXiv:2603.04915, 5 Mar 2026;
  authors at OpenAI, Paradigm and OtterSec) scores agents on detecting, patching and exploiting 117 curated high-severity
  vulnerabilities from 40 audits in a local Ethereum environment and reports that frontier agents can find and exploit
  bugs end to end. Its paper body says the majority were taken from public Code4rena audit reports, dropping anything
  found before July 2023 and keeping only permissively licensed or redistribution-cleared repositories; the other three
  audits are Tempo-blockchain scenarios. Its Table 4 lists the 40 audits by slug, from 2023-07-pooltogether to
  2025-10-sequence, and all 37 Code4rena audits appear in the 481-repository README dataset of section 4.1: 36 under the
  same slug, and one, which Table 4 writes as 2025-04-virtuals, under its repository name 2025-04-virtuals-protocol
  (`data/evmbench_c4_alias.csv`). The benchmark's Code4rena task set is therefore a subset of the Code4rena audits read
  here. Only 26 of the 37 also have a findings repository in the section-3.7 census: NextGen's is one of the four that
  timed out, two from 2024 (2024-03-canto and 2024-12-secondswap) are not among the 376 repositories it found, and the
  eight from 2025 come after the public findings record stops. A re-evaluation by Peng, Wu and Zhou (arXiv:2603.10795, 11 Mar 2026) argues that this reliance on audit-contest
  data published before every model's release risks training-data contamination, widens the study to 26 agent
  configurations, and adds 22 real-world incidents dated after every model's release, on which no agent completes an
  end-to-end exploit across 110 agent-incident pairs despite detecting up to 65% of the vulnerabilities. CyberChainBench
  (Huang, Jiang, Poovendran, Lin; arXiv:2606.26216, 24 Jun 2026) builds on 541 real exploit incidents from DeFiHackLabs
  across 9 EVM chains, scores exploits by economic impact on mainnet forks, and reports best scores of 37.5% detection,
  43.7% exploitation and 23.4% patching, with patching the hardest task. "Demystifying Agent Skills for Smart Contract
  Auditing" (Gao, Zhong, Chen, Wang, Wu; arXiv:2609.29454, 24 Sep 2026) tests 83 publicly shared audit "skills" for
  coding agents on EVMbench across seven agent-model pairs and finds the gain depends more on the model than on the agent
  harness, with the largest lift (detection +22.8%, captured award +43.2%) for one Codex configuration. PoCo (Andersson,
  Bobadilla, Hobbelhagen, Monperrus; ACM TOSEM, published online 25 May 2026; arXiv:2511.02780 v3, 23 Feb 2026) is an
  agent that turns an auditor's plain-language description of a bug into a runnable Foundry proof-of-concept, evaluated
  on 23 real vulnerability reports; it bears directly on the "coded PoC required" rules in section 4.1 and on Cantina's
  v4lend contest (section 3.5), where every High/Medium needs a coded PoC. These papers measure agent ability on past or
  curated bugs; they are context for the AI-report rules in section 4.1, not measurements of contests. Only EVMbench
  (and, through it, its re-evaluation) draws on a contest platform, and none reports contest-level submission counts or
  payouts, which is what this census adds.
- Superteam Earn, a Solana bounty board, marks each listing HUMAN_ONLY, AGENT_ALLOWED or AGENT_ONLY. Its one security
  listing restricted to agents, "Audit & Fix Open-Source Solana Repositories for Vulnerabilities" (sponsor Superteam,
  3,000 USDG split 1,500/1,000/500, published 9 February 2026, deadline 15 February 2026, winners announced 19 March 2026
  after a scheduled 9 March), drew 116 submissions, about $25.86 of prize per submission (USDG taken at $1), with the
  same proof-of-concept and fix-PR requirements that human contests impose. Of the 10 listings open on 6 Nov 2026
  (public feed, no key), 9 were HUMAN_ONLY, 1 AGENT_ALLOWED and 0 AGENT_ONLY, and none of them was security work; on
  9 Nov 2026 all 8 open listings were HUMAN_ONLY and none was security work. So agent-only audit work there is a one-off
  so far, not a lane. (Pre-build readings: 14 listings, all HUMAN_ONLY, 23 Oct 2026; the first AGENT_ALLOWED listing in
  our readings, a trading-research bounty, appeared on 28 Oct 2026.)
- Judging duration (section 3.8): web searches on 6 Nov 2026 found no published measurement of how long audit-contest
  judging takes on any platform. That was not a systematic survey.

New here, as far as we can find: per-platform contest AND submission series from primary pages; headline prize money per
submission, pooled and per contest; money actually paid per submission (HackenProof); a Code4rena series of submissions,
distinct submitters and signal rate across 2021-2024, with the April 2024 validation-repository break documented; a
complete CodeHawks census checked against the platform's own listings, with the practice-copy pitfall documented; a dated
per-program record of AI-report rules on an audit-contest platform; a rubric-coded, dated comparison of AI-report rules
across six audit platforms, with the first contest under Code4rena's V12 rule pinned down; a pre-registered README-level
test of Code4rena's automated-findings and V12 sections, which contradicted our own prediction; a live contest's
arrival curve, with a public counter that kept rising for days after the contest's end and then held still in judging,
as predicted in advance; and a pre-registered, negative feasibility result for measuring judging duration from the
Internet Archive, with the capture-level data published.

## 6. Limits

Counts include invalid, duplicate and spam submissions (and, on CodeHawks, lows). Code4rena's risk labels are as
submitted, not as judged, and QA reports can be promoted, so its signal rate is approximate; its "distinct submitters"
counts handles, so a team counts once and bot-race entries count too. Headline pots are not payouts. Private and
invite-only work is invisible.

Four platforms outside the six were checked once, on 17 October 2026, and are not counted. The newest public repository
in Hats Finance's GitHub organisation, sorted by creation date, was created on 23 September 2025 (read 21 October and
4 November 2026), and none was created in 2026;
Secure3's contest app redirects to its marketing site; AuditOne lists curated team audits and four standing bug bounties;
Remedy (Hexens) lists bug bounties and capture-the-flag events. None showed a public prize-pool audit contest in 2026.
These were single fetches of home pages and repository lists, not censuses, and a Hats competition run without a public
GitHub repository would not appear. Remedy also runs an open-ended $50,000 contest backed by the Ethereum Foundation
(from 6 Nov 2025, no end date) that pays per detection query accepted into its Glider query database (tiers up to
$2,000 per query on its triage page, read 4 Nov 2026). The public mirror of that database has had no new commit since
10 Apr 2026 (checked 9 Nov 2026). It pays for reusable detection rules rather than for findings in a contest's scope,
so it is not counted. Its documentation stated a spam rule ("Spam submissions (low-effort or AI nonsense) may lead to
suspension of your Remedy account", read October 2026) that no longer appears on its contest pages (4 Nov 2026).
Two further venues were seen and excluded for the same reason: MixBytes Camp
(camp.mixbytes.io) lists no contests and takes "participation applications" only from auditors who completed the
MixBytes Farm course, and The Web3 Security Labs (github.com/theweb3-security-labs) lists three finished contests as PDF
reports with no prize pools and no entry process, last updated 14 July 2026 (both read 20 October 2026).

Sherlock's public API listed 301 finished contests on 14 Oct 2026: 259 public contests with submission counts (the
census rows) and 42 private contests without them. None ended after 29 Jul 2026 (Tare), and it has listed none as
running or scheduled in any reading from 14 Oct 2026 (running) and 15 Oct 2026 (scheduled) to 9 Nov 2026. Sherlock
Audit Engine engagements are not
served by that API. They are participant-selected and confidential by default (docs.sherlock.xyz/audit-engine/
for-protocol-teams), and a participant's dashboard lists only its own engagements. At least one was a large public
contest: Aerodrome's $400k, three-week, Sherlock-run audit contest for the Aero upgrade (aero.xyz, 16 Jul 2026; complete
by 25 Sep 2026), reported to have run on Audit Engine from 24 or 31 Aug 2026 (secondary sources only: a press report
of 21 Aug 2026 calls it "the first open-participant engagement using Sherlock's Audit Engine"; Aero's own post names
Sherlock but not Audit Engine). Its findings and
payouts are not public, so the census undercounts Sherlock's 2026 H2 contest pool by at least $400k. An account that
MV2 holds on Audit Engine, Sherlock's venue for AI auditors, had not been invited to or joined any engagement through
6 Nov 2026 (dashboard readings on 15, 21, 24, 27 and 30 Oct and 2 and 6 Nov 2026; the 15 Oct reading covered only
engagements taking applications). Until 2 Nov the dashboard listed no engagement at all. On 6 Nov it showed its first,
open for applications (Uniswap, $20,000 guaranteed, 6-16 Nov 2026), with the rule "This application is only for human
researchers, not purposefully built AI tools" (one logged-in read; we found no public page for it). So admission of AI
auditors on Audit Engine is set per engagement, and the first one we saw excluded them.

Certora's formal-verification contests ran inside host contests (Aquarius on Cantina, May-June 2025; Blend v2 on
Code4rena, Feb-Mar 2025), each with a $20,000 USDC FV pool paid by the host. In our census the FV pool is part of the
host contest's pot (Cantina's Aquarius pot of $110,000 includes it); Blend v2 falls outside our Code4rena window. Certora
reports 21 and 26 participants, so these pools were far less crowded per entrant than the bug-finding contests above.
We found no later Certora contest (checked 5 Nov 2026).

Half-years with few contests (2026 H1: 12-13 on Sherlock+Cantina, 3 on Immunefi; every
CodeHawks half-year after 2024; Code4rena 2024 H2) give rough medians. Token pots (OP, HAI, JTO, ETH and others) are left
out of dollar figures or taken at the USD the page states, never converted silently. Contests are grouped by start date.
Every census figure is a snapshot of pages as fetched on 14-16 Oct 2026. Immunefi's leaderboard sizes change meaning in
mid-2025 (section 3.2). Code4rena's 2024 figures after April are not comparable with earlier ones, and four of its
repositories could not be read. AI-report rules are dated only through start dates (HackenProof), a git commit
(CodeHawks) and dated posts (Immunefi, Code4rena, Zellic). Sitemaps can list pages that are not contests: CodeHawks'
lists 228 self-paced practice copies of two First Flights, which a naive scrape would count as 210 First Flights in 2026
instead of 4. We filter them by their slug form and check the result against the platform's listing pages. Compute hosts
matter too: one parse-only re-run of the Immunefi census found none of the pages saved by the first run, because they
were on another host's volume. It ended with 0 records instead of wrong ones, which is how a re-run should fail. The
first attempt at the section-3.8 census stopped the same way (exit 4, nothing computed), and a published addendum fixed
how inputs are rebuilt before the rerun. Reposts
can carry a different date from the original: the V12 post's repost is a day earlier than Zellic's own date, and
Sherlock's Audit Engine post now shows 19 Aug 2026 where we first read 20 Aug. Several
sources (the Immunefi article on X, the Code4rena Bot Races post, the Medium essay) were read only through search
excerpts, because their sites refused our fetcher; we say so wherever we use them. Quotations from Sherlock's
documentation and blog were read through a page-reading tool that returns excerpts, not raw HTML.

Cantina's `totalFindings` is not frozen at a contest's end time while the contest still shows "Live": Revert v4lend
(end 2026-11-03 18:30 UTC, per Cantina's API) rose by at least 353 between about 19 and 56 hours after its end, in
bursts (3 in one 4-hour stretch, 170 in the next 13 hours). A pre-registered prediction that the post-close rate would
decay below about 8.9 per hour failed (about 10 per hour over 17 hours). Between about 56 and 61 hours after the end,
the page and the API switched from "Live" to "Judging", at 7,079 findings, and the count did not move in judging
through 9 Nov 2026 (pre-registered test held; section 3.5). For the 125 public contests already
"complete" on 14 October 2026, a fresh read on 5 November 2026 found every count unchanged (sum 58,193 both times;
pre-registered check, all three predictions held; `cantina_drift/`). The most recent of these had ended 124 days
before the first read, so the census counts are stable for long-finished contests. In the archive (section 3.8), the
27 competitions with a non-zero count on a non-complete page all show today's count; that is descriptive, not a
test. Cantina's documentation does not say what
the counter includes after the end (late submissions, judge-created duplicates or escalations were not distinguishable
here). Section 3.8's census rests on one archive of one site; a page served without a status cannot be read by its
rule, and the rule allows no other way of reading it.

## 7. Reproduce

Repository: https://github.com/munimtechnologies/audit-contest-ai-rules (v0.10.0).

| Section | Script (each has a `test_*.py` that pins the numbers) | Data (CC BY 4.0) |
|---|---|---|
| 3.1 | `cross_platform.py`, `sherlock_crowding.py`, `cantina_crowding.py` | `data/sherlock_contests.csv`, `data/cantina_census.csv` |
| 3.2 | `immunefi_series.py` (census: `fetch_immunefi.py`) | `data/immunefi_contests.csv` |
| 3.3 | `prize_per_submission.py` | as 3.1 |
| 3.4 | `hackenproof_payouts.py`, `hackenproof_trends.py` | `data/hackenproof_programs.csv`, `data/hackenproof_programs_fetched.csv` |
| 3.5 | `v4lend/v4lend_rates.py` (tests: `v4lend/test_v4lend_rates.py`, `v4lend/test_v4lend_rates_late.py`) | `v4lend/v4lend_findings_count.csv` |
| 3.6 | `codehawks_series.py` | `data/codehawks_contests.csv` |
| 3.7 | `c4_series.py` (census: `fetch_c4.py`, `c4_crowding.py`) | `data/c4_contests.csv`, `data/c4_summary.json` |
| 3.8 | `cantina_judging/{probe,bound,vocab,census}/job.py` (each with `test_job.py`) | `cantina_judging/bound/bounds_by_id.csv`, `cantina_judging/census/brackets_by_id.csv`, `cantina_judging/census/captures.csv`, each stage's summary file (`summary.json`; `summary-public.json` in `vocab/`) |
| 4.1 | | `data/platform_ai_rules.csv` (one row per platform document: URL, verbatim clause, stance, date and date source) |
| 4.1 README test | `c4_sections.py` (census: `fetch_c4_readmes.py`; tests: `test_c4_readme_sections.py`) | `data/c4_readme_sections.csv`, `data/c4_sections_summary.json`, `data/evmbench_c4_alias.csv` |
| 6 (Cantina drift) | `cantina_drift/drift.py` (test: `cantina_drift/test_drift.py`) | `cantina_drift/drift_rows_20261105.csv`, `cantina_drift/drift_summary_20261105.json` |

Each top-level script prints its table with `--table`. The `v4lend/`, `cantina_drift/` and `cantina_judging/` folders
hold pre-registered checks exactly as they ran, with their data next to them; run their tests from inside the folder
(`python -m unittest`). `v4lend_rates.py` recomputes section 3.5's windows and day table from the 104 readings. The
section-3.8 jobs fetch from the Internet Archive and need network access; their tests run offline. The
pre-registration and its three addenda are in `paper/` (`cantina-judging-duration-PREREGISTRATION.md` and
`cantina-judging-duration-pages-ADDENDUM*.md`).

## Sources

Read 14-16 Oct 2026 unless noted. "Search excerpt" means the page refused our fetcher and the text comes from a web
search engine's copy.

- Sherlock contest API: https://mainnet-contest.sherlock.xyz/contests (last read 9 Nov 2026) ; judging guidelines:
  https://docs.sherlock.xyz/audits/judging/guidelines ; Audit Engine: https://docs.sherlock.xyz/audit-engine/for-participants
  and https://docs.sherlock.xyz/audit-engine/for-protocol-teams (21 Oct 2026) ; bug-bounty stake: "Best Web3 Bug
  Bounties in 2026" (31 Aug 2026):
  https://sherlock.xyz/post/best-web3-bug-bounties-in-2026-the-highest-paying-programs-on-every-platform (18 Oct 2026) ;
  payout criteria: https://docs.sherlock.xyz/audits/watsons/meeting-the-payout-criteria (18 Oct and 9 Nov 2026) ;
  "Why We Built Sherlock Audit Engine": https://sherlock.xyz/post/why-we-built-sherlock-audit-engine (18 Oct and
  9 Nov 2026)
- Aerodrome: https://aero.xyz/articles/aero-is-on-the-horizon/ (16 Jul 2026) and
  https://aero.xyz/articles/aero-launch-update-all-systems-go/ (25 Sep 2026), both read 21 Oct 2026 ; Crypto Briefing,
  21 Aug 2026: https://cryptobriefing.com/aerodrome-finance-400k-audit-contest-sherlock/ (18 Oct 2026)
- Cantina competitions API: https://cantina.xyz/api/v0/competitions (v4lend end time and status, 5-7 Nov 2026) ;
  competition rules: https://docs.cantina.security/standards/severity/competition ; Revert v4lend:
  https://cantina.xyz/competitions/e275368c-547d-4d91-a418-053ad31082a8 (14 Oct-9 Nov 2026)
- Internet Archive: Wayback CDX index https://web.archive.org/cdx/search/cdx and archived copies of
  `cantina.xyz/competitions/<id>` pages (7-8 Nov 2026; queries and capture list in `cantina_judging/`)
- Immunefi competitions: https://immunefi.com/audit-competition/ ; Rules: https://immunefi.com/rules/ ; researcher terms
  as served on a program's safe-harbor page ("Last Updated 07 September 2026"):
  https://immunefi.com/bug-bounty/originprotocol/safe-harbor/ ; CoinDesk, 17 Jan 2023:
  https://www.coindesk.com/tech/2023/01/17/crypto-whitehat-platform-immunefi-banned-15-chatgpt-generated-bug-reports-heres-why ;
  "What We're Learning About Audit Competitions", 23 Sep 2026 (search excerpt):
  https://x.com/immunefi/status/2102715623218557375 ; submission-fee sentence (21 Oct 2026):
  https://immunefi.com/audit-competition/audit-competition-ens/information/ ,
  https://immunefi.com/audit-competition/audit-comp-firelight-1/information/ ,
  https://immunefi.com/audit-competition/audit-comp-quantus/information/
- Jump Crypto, "Hardening Firedancer", 16 Oct 2026: https://jumpcrypto.com/resources/hardening-firedancer (23 Oct and
  4 Nov 2026)
- HackenProof audit programs: https://hackenproof.com/audit-programs (listing pages and each program page)
- CodeHawks: https://codehawks.cyfrin.io/contests (re-read 6 Nov 2026) , https://codehawks.cyfrin.io/first-flights ; AI
  rule: https://github.com/Cyfrin/codehawks-docs/blob/main/judging/disqualification-criteria.md (added in commit 9fc66d1,
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
- Apify Actor: https://apify.com/tactful_anvil/web3-audit-contest-aggregator (26 Oct and 4 Nov 2026)
- AI-agent papers (abstract pages; EVMbench also its HTML body): https://arxiv.org/abs/2603.04915 ,
  https://arxiv.org/abs/2603.10795 , https://arxiv.org/abs/2606.26216 , https://arxiv.org/abs/2609.29454 ,
  https://arxiv.org/abs/2511.02780 and https://doi.org/10.1145/3816704 (all re-opened 4-6 Nov 2026; the first four are
  still at v1, PoCo at v3)
- Superteam Earn: https://superteam.fun/earn/listing/fix-open-source-solana-repos-agents and
  https://superteam.fun/api/listings/details/fix-open-source-solana-repos-agents (20 Oct 2026); feed
  https://superteam.fun/api/listings?take=100 (6 and 9 Nov 2026)
- Certora: https://github.com/Certora/aquarius-cantina-fv ,
  https://raw.githubusercontent.com/code-423n4/2025-02-blend/main/README.md ,
  https://www.certora.com/blog/bringing-formal-verification-to-rust (17 Oct 2026)
- Remedy Glider contest: https://docs.r.xyz/glider-ide/glider-contest.md and
  https://docs.r.xyz/glider-ide/glider-contest/triage-guidelines.md (4 Nov 2026); database mirror commits:
  https://api.github.com/repos/Hexens/glider-query-db/commits?path=queries (9 Nov 2026)
- Hats Finance repositories: https://api.github.com/orgs/hats-finance/repos?sort=created&direction=desc (21 Oct and
  4 Nov 2026)

---

*MV2 of Munim, Inc. Made with AI agents working for MV2.*
