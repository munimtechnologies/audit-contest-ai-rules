# Corrections and additions to the preprint

For `paper/audit-contest-census.md`, "Fewer contests, more submissions, less money each". Each entry is dated and names
the version it corrects. Entries are folded into the next full version of the paper. Text: CC BY 4.0.

**Status (9 November 2026): entries 1-8 are folded into version 2.0 of the paper.** They stay here unchanged as the
record of what was corrected and when. Two details differ in v2.0 because the sources were re-read on 9 Nov 2026 before
folding: Sherlock's blog post "Why We Built Sherlock Audit Engine" now shows the date 19 Aug 2026 (entry 2 gives
20 Aug), and Revert v4lend's later readings (8 and 9 Nov, still "Judging" and "7,079") are added to entry 7's result.
New corrections to version 2.0 will start at entry 9.

## 18 October 2026, to version 1.8 (16 October 2026)

### 1. Not every Sherlock Audit Engine engagement is private (correction)

Section 2 says that private contests and invite-only engagements, "Sherlock Audit Engine" among them, are not in the public
series. That holds for the series, but it describes Audit Engine wrongly: at least one Audit Engine engagement was public.

- Aero (Aerodrome Finance) announced on 16 Jul 2026 that a three-week, Sherlock-run public audit contest of its Aero
  upgrade would follow its formal audits, with "The prize pot will be set at $400k" (then planned for 24 Aug-11 Sep).
- Press reports of 21 Aug 2026 describe it as "the first open-participant engagement using Sherlock's Audit Engine",
  starting 31 Aug. Aero's own post names Sherlock but not Audit Engine, and we found no Sherlock page for the engagement,
  so the Audit Engine link rests on the press reports.
- It is not in Sherlock's contest API, which our Sherlock series is built from. The API's total was 301 contests both in
  our 14 Oct fetch and on 18 Oct 2026, and its first page, sorted by pot, has no $400,000 entry. We found no public
  submission count for it.

Effect on the paper:
- It would add one contest to the "2026 Q3" row of section 3.1 (2 contests, Sherlock + Cantina) and to the "2026 H2 (to
  date)" row of section 3.3. Its submissions cannot enter either table, because no count is public, so every submission
  and per-submission figure stands as published.
- The 2024 H1 to 2026 H1 comparisons (contests -83%, submissions +24%, money per submission -81%) do not change: the
  contest started in 2026 H2.
- Sherlock's public contest count for 2026 is ten, not nine, if Audit Engine's open engagements are counted as contests.
- The census can miss public contests that a platform runs outside the endpoint it was built from. Section 6 will say so.

### 2. Sherlock's own pages disagree on whether Audit Engine replaces contests (addition)

- Sherlock's documentation page "Meeting the Payout Criteria" (undated) carries a notice that the option to "unlock past
  unearned audit contest payouts will end after February 6th, 2027", and gives as the reason that Audit Engine is
  replacing audit contests.
- Sherlock's blog post "Why We Built Sherlock Audit Engine" (20 Aug 2026) says Audit Engine "sits alongside Sherlock's
  Collaborative Audits, Audit Contests, and Blackthorn reviews".
- On 18 Oct 2026 the contest API listed no running and no scheduled contest. The newest contest in our data started on
  20 Jul 2026 (Tare).

Read together with the CEO's reply quoted in section 1, the documentation notice fits section 4's point that the question
is how many platforms still hold public contests. Code4rena announced a wind-down in May 2026. Sherlock's documentation
now dates the end of a part of its contest system. We don't claim that Sherlock has ended contests: its blog says
otherwise, and the notice concerns payouts.

### 3. Sherlock's rule against invalid submissions (addition, for section 4.1)

The same documentation page sets two "Audit Contest Payout Criteria". An account receives no USDC payouts until it has
submitted 2 valid issues, and its lifetime "issues ratio" (valid issues / all issues submitted, counted over contests that
started on or after 1 Jul 2023) must be at least 20%. These criteria replaced an earlier USDC penalty for invalid issues.
Payouts withheld under them are paid in full once both criteria are met. The rule says nothing about AI, so on the
rubric of section 4.1 Sherlock's contest stance stays "silent". It is the only platform-wide rule in our sources that
ties pay to an account's valid-submission ratio, and it dates from 2023, before the 2025-2026 contest collapse.

Separately, Sherlock's bug-bounty product (not an audit contest, so outside this census) uses "a stake-to-submit model
where researchers stake $250 USDC per report, refunded if the issue is valid" (Sherlock blog, 31 Aug 2026).

### Sources (read 18 Oct 2026)

- Aero, "Aero is on the Horizon" (16 Jul 2026): https://aero.xyz/articles/aero-is-on-the-horizon/
- Crypto Briefing, "Aerodrome Finance launches $400K public audit contest with Sherlock ahead of major upgrade"
  (21 Aug 2026): https://cryptobriefing.com/aerodrome-finance-400k-audit-contest-sherlock/
- Sherlock, "Why We Built Sherlock Audit Engine" (20 Aug 2026): https://sherlock.xyz/post/why-we-built-sherlock-audit-engine
- Sherlock docs, "Meeting the Payout Criteria": https://docs.sherlock.xyz/audits/watsons/meeting-the-payout-criteria
- Sherlock, "Best Web3 Bug Bounties in 2026" (31 Aug 2026):
  https://sherlock.xyz/post/best-web3-bug-bounties-in-2026-the-highest-paying-programs-on-every-platform
- Sherlock contest API: https://mainnet-contest.sherlock.xyz/contests (total; `status=RUNNING` and `status=CREATED`)

The quotations were read through a page-reading tool that returns excerpts, not the raw HTML. Before they go into the
paper, check them against the pages.

## 19 October 2026, to version 1.8 (16 October 2026)

### 4. Section 4 prediction contradicted (correction)

Section 4 predicted that Code4rena audit READMEs with an "Automated Findings" section would begin in April 2023
(Frankencoin) and end by mid-2024, and that every Solidity audit from 6 Oct 2025 (Hybra Finance) on would carry a V12
section. A test written down before it ran (`paper/c4-readme-sections-PREREGISTRATION.md`) read all 442 audit READMEs of
Code4rena's public GitHub organization (`data/c4_readme_sections.csv`). It contradicts both parts:

- The section first appears on 31 Jan 2023 (Canto Identity), about ten weeks before Frankencoin.
- 60 audits that started after 30 Jun 2024 still have it. 51 of them link a 4naly3er static-analysis report (the last,
  GTE Perps, started 28 Aug 2025); the last audit with the heading at all is Monad (15 Sep 2025).
- Brix Money (26 Nov 2025) is a Solidity audit without V12. 15 of the 16 Solidity audits from 6 Oct 2025 on have it.

A narrower reading that counts only bot-race wording was defined after one README had been seen before the run, so it
is post hoc. It matches the predicted end (last 14 Mar 2024, Coinbase) but not the start. The prediction was wrong about
what the section is: it held automated pre-audit output of any kind, not the bot race alone. Section 4 will be rewritten
in version 1.9. Full result: `paper/c4-readme-sections-result.md`.

## 21 October 2026, to the repository's feed tool (v0.9.1) and for section 4.1

### 5. Immunefi audit competitions charge a fee per report (correction)

`audit_contest_feed.py` (v0.9.1) marked every platform `"fee": false`, where `fee` means that taking part requires
moving money. That is wrong for Immunefi. The information page of each of its three latest audit competitions says:
"A submission fee, set and managed by Immunefi, applies to each report and is shown at submission time." It adds: "If
a researcher disagrees with a closure decision, initiating a mediation also requires a fee set by Immunefi."

| Competition (census slug) | Ran | Fee sentence on its page (read 21 Oct 2026) |
|---|---|---|
| Firedancer V1 (`firedancer-v1-audit-comp`) | 9 Apr - 9 May 2026 | no |
| Base Azul (`audit-comp-base-azul`) | 21 Apr - 4 May 2026 | no |
| Firelight (`audit-comp-firelight-1`) | 12 - 25 Aug 2026 | yes |
| Quantus (`audit-comp-quantus`) | 12 - 25 Aug 2026 | yes |
| ENS (`audit-competition-ens`) | 18 Aug - 14 Sep 2026 | yes |

No competition in our Immunefi census started between 21 Apr and 12 Aug 2026, so the fee arrived with the August
restart, or was written onto those pages later. The pages state no amount. Immunefi's article of 23 Sep 2026 (already
cited in the paper) explains the fee as paying for triage, which costs the same for a duplicate as for a first report,
and says fees should come down as triage improves. That reading comes from the article as a web search engine indexed
it, because x.com refused our fetcher.

Fixed in v0.9.2: the Immunefi row is now `"fee": true`, so `--no-fee` drops it, and `test_feed_fee.py` checks this.
Immunefi was already dropped by `--ai-ok`, because its terms ban AI-generated reports.

For the paper (section 4.1): together with Sherlock's $250 stake per bug-bounty report (entry 3, refunded if the issue
is valid; described in a post of 31 Aug 2026), two platforms now ask for money with each report. Neither charge applies
to the contests the crowding series measures: Immunefi's competitions aren't in that series, and Sherlock's stake is for
its bug bounties. A charge per report puts a price on duplicate and low-effort submissions directly. That is a different response to crowding from the AI rules
the paper codes, and version 1.9 will list it next to them. The census numbers don't change.

### Sources (read 21 Oct 2026)

- https://immunefi.com/audit-competition/audit-competition-ens/information/
- https://immunefi.com/audit-competition/audit-comp-firelight-1/information/
- https://immunefi.com/audit-competition/audit-comp-quantus/information/
- https://immunefi.com/audit-competition/audit-comp-base-azul/information/
- https://immunefi.com/audit-competition/firedancer-v1-audit-comp/information/
- Immunefi, "What We're Learning About Audit Competitions" (23 Sep 2026): https://x.com/immunefi/status/2102715623218557375

As for entries 1-3, the pages were read through a page-reading tool that returns excerpts, not the raw HTML.

## 7 November 2026, to version 1.9 (6 November 2026)

### 6. Cantina judging-duration census: first source infeasible, second source passes its first gate (addition)

Version 1.9 follows one competition, Revert v4lend, into judging but does not measure how long Cantina competitions
stay in judging. A census of that question was pre-registered after v1.9 (`paper/cantina-judging-duration-PREREGISTRATION.md`, 6 Nov 2026,
23:51 UTC), with five predictions (P1-P5) and a gate of at least 20 eligible competitions.

- **Primary source infeasible (negative result).** The Internet Archive holds no capture of Cantina's competitions
  API that our query found (0 rows, 7 Nov 2026, 03:05 UTC). 0 competitions are eligible, so P1-P5 are not testable
  from it. Details: `paper/cantina-judging-duration-result.md`.
- **Second source, stage 1 passed.** An addendum written before any archived page was read
  (`paper/cantina-judging-duration-pages-ADDENDUM.md`) moves the census to archived competition pages, with P1-P5,
  the 14-day rule and the gate unchanged. Its first stage uses capture times only, with no page content. On 7 Nov
  2026, 12:14 UTC, 142 of the 145 competitions in Cantina's API had ended, 131 have a main-page capture after their
  end, and **68** have at least one gap of 14 days or less between consecutive points (end, then captures), the
  most that could ever be eligible. 68 is at least 20, so the census may go ahead; whether it does depends on what
  the archived pages show, which has not been read yet. Code and table: `cantina_judging/bound/`.

No number in version 1.9 changes.

### 7. Revert v4lend: the findings count did not move in judging (pre-registered test held)

Version 1.9 (section 3.5) stated a test before it was read: a reading at least 24 hours after 6 Nov 2026, 07:10 UTC,
predicted to equal 7,079. On 7 Nov 2026 Cantina's public API showed status `judging` and 7079 findings at 12:14:30 UTC
(read by the bound job), and a second API read and two reads of the competition page, at about 12:45-12:50 UTC,
showed "Judging" and "7,079". **The prediction held.** The count has not moved since the switch to "Judging",
about 29 hours after the test's reference time and about 90 hours after the 3 Nov 18:30 UTC end. The pot is still
50,000 USDC, so section 3.5's figure of about $7.06 of pot per submitted finding stands. This says nothing about the
switch to "complete", which had not happened at these readings. The 104-reading data set is unchanged
(`v4lend/`); these four readings are recorded here only.

### Sources (read 7 Nov 2026)

- Cantina competitions API: https://cantina.xyz/api/v0/competitions
- Revert v4lend competition page: https://cantina.xyz/competitions/e275368c-547d-4d91-a418-053ad31082a8
- Wayback CDX: https://web.archive.org/cdx/search/cdx (query in `cantina_judging/bound/summary.json`)

The page and the second API read were taken through a page-reading tool that returns excerpts and no timestamp, so
their times are approximate; the bound job's API read time is machine-recorded.

## 8 November 2026, to version 1.9 (6 November 2026)

### 8. Cantina judging-duration census: the archive is too thin, P1-P5 not testable (negative result)

Entry 6 left the census at "may go ahead". It has now run (job `cantina-pages-census-v2`, 8 Nov 2026, 19:52:20-19:53:43
UTC), under the extraction rule of `paper/cantina-judging-duration-pages-ADDENDUM-2.md` and the input rule of
`paper/cantina-judging-duration-pages-ADDENDUM-3.md`, both public before it ran. Its inputs matched the published
stage-2 counts exactly, so this is the pre-registered census.

- **0 of 142** ended competitions are eligible. 125 have a readable `complete` capture after their end, but the
  narrowest bracket around the change to `complete` is 18.07 days wide, and the rule allows at most 14. The gate
  needs 20, so **P1-P5 are not testable.** The stage-1 figure of 68 was an upper bound from capture times; the real
  count is 0, mainly because 354 of 882 captures (40%) show no status and readable captures fall on only 1 to 5 days
  a month.
- Descriptive only, not a test of P5: in all 27 competitions whose earliest non-complete capture shows a findings
  count above 0, that count equals today's API count.
- Nothing about how long Cantina's judging takes can be concluded from this source. P1-P5 are not re-tested on
  another source without a new, separately published pre-registration.

Details, every bracket and every capture: `paper/cantina-judging-duration-result.md` ("Stage 3: census") and
`cantina_judging/census/`.

Revert v4lend, which the paper follows directly, still showed "Judging" and "7,079" findings on its page at about
23:25 UTC on 8 Nov 2026, about five days after its end (page-reading tool, excerpts only, approximate time).

No number in version 1.9 changes.

### Sources (read 8 Nov 2026)

- Internet Archive captures of `cantina.xyz/competitions/<id>` pages, read from the stage-2 cache (capture list in
  `cantina_judging/census/captures.csv`)
- Revert v4lend competition page: https://cantina.xyz/competitions/e275368c-547d-4d91-a418-053ad31082a8

---

*MV2 of Munim, Inc. Made with AI agents working for MV2.*
