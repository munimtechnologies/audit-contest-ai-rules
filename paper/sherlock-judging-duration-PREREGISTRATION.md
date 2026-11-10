# How long does Sherlock's judging take? Pre-registration (P1-P5)

*Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com). Text CC BY 4.0, code Apache-2.0.*

Registered: 10 Nov 2026. The time of the GitHub commit that adds this file is the registration time; it is
authoritative over any time written in the text.

## Why

Section 3.8 of `paper/audit-contest-census.md` could not measure how long Cantina's judging takes, because the
Internet Archive holds too few readable pages. Sherlock is different: its public contest API carries, for each
finished contest, the time escalations opened (`escalation_started_at`), the time they closed
(`escalation_ends_at`) and a `judging_stopped_at` time, next to `ends_at` and the submission count
(`num_competition_issues`). None of these timestamps is in this repository's Sherlock data (`fetch_sherlock.py`
keeps a fixed list of fields that does not include them), and one search on 10 Nov 2026 found no published
measurement of Sherlock judging times built from them. This tests Sherlock's own published schedule against its
own data.

## What Sherlock says (read 10 Nov 2026, all pages undated)

- docs.sherlock.xyz/audits/judging, Real-Time Judging: phase 1 "Lasts a fixed number of days (# of issues / 100)
  days (for example 500 issues would be 5 days), with a minimum of 2 days." Lead Judge: "Lead Judge gets (# of
  issues / 200) days to do this preliminary judging, with a minimum of 2 days." "(so 500 issues would round up to 3
  days)". "The Lead Judge may begin judging before the official start date." Escalations: "After the preliminary
  results are announced, Watsons have 24 hours to flag any issues for re-review".
- docs.sherlock.xyz/audits/judging/community-judging: "There are only 24 hours to escalate your issue after the
  release of the preliminary results."
- docs.sherlock.xyz/audits/protocols/how-it-works-for-protocols: "the post-contest process can take a couple
  days, or it can take a few weeks, depending on the number of issues found"; the escalation period "takes 48-72
  hours in total"; teams should "not expect to deploy/launch their protocol until 2-3 weeks after the audit contest
  finishes".
- Sherlock announced Real-Time Judging on X on 11 Sep 2024 (post id 1833874610473013426).

So the documented days from contest end to preliminary results (escalations opening) are
**D(N) = max(2, ceil(N/100)) + max(2, ceil(N/200))**, with N = `num_competition_issues`.

## Data and definitions

Source: `https://mainnet-contest.sherlock.xyz/contests?status=FINISHED&page=N` (all pages) and
`/contests/<id>` for each listed id, fetched by job `sherlock_judging/job.py` (committed with this file). The job
waits until this file is public on GitHub, records the commit that added it, and only then fetches. It keeps only
dates, counts, flags, status and title (no handles or other personal fields).

- J = (`escalation_started_at` - `ends_at`) in days: contest end to preliminary results.
- S = (`judging_stopped_at` - `ends_at`) in days. The API does not document `judging_stopped_at`; we read it as the
  time judging was closed, and every claim about S is about the field as published.
- W = `escalation_ends_at` - `escalation_started_at` in seconds: the escalation window.
- v3 = `is_judging_v3` is `true` (we take this flag to mark contests judged under the current system; Sherlock does
  not document it).
- Year = UTC calendar year of `ends_at`.

**Eligible:** status `FINISHED`, `private` exactly `false`, N an integer above 0, and `ends_at`,
`escalation_started_at`, `escalation_ends_at` all present. A J of 0 or below is kept, not dropped, and counted
in the descriptive output. S-based predictions use eligible contests that also have `judging_stopped_at`.

**Seen before registration, excluded from grading:** while finding these fields on 10 Nov 2026 we read page 1 of
the FINISHED list (10 contests, ids 1140, 333, 38, 1260, 205, 677, 1209, 1028, 59, 6: their start, end and
escalation times) and the full detail record of contest 1209 (N = 975, J = 10.1, S = 51.1, W = 48 h). For eight of
them we worked out J (about 9.3 to 38.7 days) and for seven W (five at 24 h, two at 48 h). These ten are excluded
from the confirmatory grade; the job also reports the grade with them included, for information only.

## Predictions (confirmatory set: eligible contests minus the ten above)

- **P1 (the documented schedule mostly holds):** among v3 contests, at least 50% have J <= D(N) + 1 day.
- **P2 (the 24-hour window is not universal):** among v3 contests, fewer than 90% have W = 24 h (86,400 s
  +/- 60 s).
- **P3 (final judging takes much longer than preliminary results):** among contests with S, the median of S - J is
  above 7 days.
- **P4 (bigger contests wait longer):** across all eligible contests, the Spearman correlation between N and J is
  above 0.3.
- **P5 (slower in 2026 than in 2024):** the median S of contests ending in 2026 is above that of contests ending
  in 2024.

**Gates:** P1-P4 need at least 20 contests in the set they use, P5 at least 10 in each of the two years. Below a
gate the prediction is reported as **not testable**, never as held or failed. All thresholds are fixed here and
are not changed after any data is seen.

## Reporting

Results go to `paper/sherlock-judging-duration-result.md` with `sherlock_judging/contests.csv` (one row per
listed contest) and the job's `summary.json`, whatever the outcome. Descriptive figures (medians by year, J of 0
or below, S before J, the most common W values, how many contests had escalations closed within 21 days of the
end) grade nothing. If the job's code has a bug that stops it, a fix is published as a dated addendum before any
re-run; no prediction, threshold, gate, definition or exclusion changes.

Limits: one platform, Sherlock's own timestamps (not independently checked), undocumented fields (`is_judging_v3`,
`judging_stopped_at`), and the docs are undated, so the schedule they describe may not have applied to every
contest. Private contests and Audit Engine engagements are not in the API list and are not covered.
