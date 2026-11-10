# How long does Sherlock's judging take? Result of the pre-registered test (P1-P5)

*Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com). Text CC BY 4.0, code Apache-2.0.*

Pre-registration: [`paper/sherlock-judging-duration-PREREGISTRATION.md`](sherlock-judging-duration-PREREGISTRATION.md),
commit `ab0186ebb8ce023c962a647d034a6304b5cb0018` (10 Nov 2026 08:49:27 UTC). It is not edited here.
Data: [`sherlock_judging/contests.csv`](../sherlock_judging/contests.csv) (one row per listed contest) and
[`sherlock_judging/summary.json`](../sherlock_judging/summary.json), written by
[`sherlock_judging/job.py`](../sherlock_judging/job.py) as committed with the pre-registration.

## How it ran

- The job's 17 offline tests passed first. It then checked GitHub, found the pre-registration commit on its first poll
  and recorded it (`summary.json` -> `prereg`), and only after that fetched Sherlock's public API: 13:15:02 to
  13:20:16 UTC on 10 Nov 2026, 301 FINISHED contests listed, 301 detail records fetched, none missing.
- Eligible (rules fixed in the pre-registration): 233. Not eligible: 42 private or with an unknown submission count,
  26 with no `escalation_started_at` (all of them 2022 contests).
- Confirmatory set = eligible minus the ten contests seen before registration: 223 contests, 81 of them flagged
  `is_judging_v3`, 80 of those with `judging_stopped_at`.
- Before writing this, three contests were checked by hand against the live API (ids 31, 1222 and 1279): `ends_at`,
  `escalation_started_at`, `escalation_ends_at`, `judging_stopped_at`, the submission count and the v3 flag all gave
  exactly the J, W and S values in `contests.csv`.
- No bug, addendum or re-run.

## Grades (confirmatory set)

| | Prediction | Result | Grade |
|---|---|---|---|
| P1 | among v3 contests, at least 50% have J <= D(N) + 1 day | 42 of 81 (51.9%) | **held** (narrowly) |
| P2 | among v3 contests, fewer than 90% have a 24-hour escalation window | 78 of 81 (96.3%) are 24 h | **failed** |
| P3 | median of S - J above 7 days | 11.3 days (n = 80) | **held** |
| P4 | Spearman correlation of N and J above 0.3 | 0.459 (n = 223) | **held** |
| P5 | median S of 2026 contests above that of 2024 | 8 confirmatory 2026 contests, gate is 10 | **not testable** |

J = days from contest end to preliminary results (escalations open); S = days from contest end to
`judging_stopped_at`; W = length of the escalation window; D(N) = max(2, ceil(N/100)) + max(2, ceil(N/200)), the
days Sherlock's docs give for real-time judging plus the Lead Judge's preliminary judging, N = submissions.

**P2 failed, and the failure supports Sherlock's docs.** The docs say there are "only 24 hours to escalate", and 96%
of current-system contests had exactly that. The prediction was driven by the ten contests seen before registration,
two of which (Aave V4 and XRP Ledger - April 2026) had 48-hour windows. In the full data only 3 of the 81 confirmatory
v3 contests differ (two at 48 h, one at 56 h). This is the kind of small-peek bias the exclusion rule exists to catch.

**P5 is not testable** because two of the ten 2026 contests were in the excluded seen set. For information only (not a
grade): with the seen contests included, the median S is 17.8 days for 2024 (n = 30) and 47.6 days for 2026 (n = 10).

**Including the ten seen contests** (information only, as the pre-registration says) changes no grade except P5:
P1 44/86 (51.2%), P2 81/86 (94.2%), P3 11.9 days, P4 0.469.

## Descriptive (grades nothing)

- Median J by year of contest end (all eligible): 2023 14.1 days (n = 75), 2024 9.0 (n = 102), 2025 11.6 (n = 46),
  2026 12.1 (n = 10). The median submission count rose over the same years: 189, 164, 551, 1,212.5.
- Median S (contests with `judging_stopped_at`, which all carry the v3 flag): 2024 17.8 days (n = 30), 2025 27.9
  (n = 45), 2026 47.6 (n = 10).
- The v3 flag first appears on a contest ending 13 Sep 2024, two days after Sherlock announced Real-Time Judging
  (11 Sep 2024). Every eligible contest ending after that date carries it.
- Among v3 contests the median of J - D(N) is 0.88 days: preliminary results usually land close to the documented
  schedule, and P1's 51.9% says that "within a day of it" is a coin flip.
- No contest had J of 0 or below, and none had S before J.
- Escalation windows (all 233 eligible): 228 at 24 h, 4 at 48 h, 1 at 56 h.
- 204 of 233 eligible contests had escalations closed within 21 days of the contest end.
- Hand count from `contests.csv` (not produced by the job; recount it from the file): among the 80 confirmatory v3
  contests with S, S was 21 days or less for 23 of 30 ending in 2024, 15 of 42 ending in 2025 and 2 of 8 ending in
  2026. Sherlock's protocol docs tell teams not to expect to launch "until 2-3 weeks after the audit contest
  finishes", and its deprecated pricing page says judging is "finalized shortly after it ends". This compares an
  undocumented field with undated prose, so it is a pointer, not a finding.

## What this adds

Sherlock's preliminary-results timing follows its documented formula roughly half the time to within a day, grows
with contest size, and the 24-hour escalation window is almost universal. The `judging_stopped_at` field, if it
marks the end of judging as we read it, puts the end of judging a median 11 days after preliminary results and has
been rising year on year. One search on 10 Nov 2026 found no earlier published measurement of these timestamps.

## Limits

One platform, measured only from Sherlock's own API timestamps, not checked against any other source.
`is_judging_v3` and `judging_stopped_at` are undocumented, and our reading of them may be wrong; every claim about S
is about the field as published. Sherlock's docs are undated, so D(N) may not describe every contest. Private contests
and Audit Engine engagements are not in the list. P1 held by 1.9 percentage points (two contests). The 2026 group is
small (10 contests).
