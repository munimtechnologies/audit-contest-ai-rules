# Corrections and additions to the preprint

For `paper/audit-contest-census.md`, "Fewer contests, more submissions, less money each". Each entry is dated and names
the version it corrects. Entries are folded into the next full version of the paper. Text: CC BY 4.0.

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

---

*MV2 of Munim, Inc. Made with AI agents working for MV2.*
