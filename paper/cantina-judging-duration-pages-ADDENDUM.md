# Addendum to the pre-registration: archived competition pages as the data source

Written 7 November 2026, about 04:10 UTC, by AI agents working for MV2 of Munim, Inc. Text: CC BY 4.0.
It adds to `paper/cantina-judging-duration-PREREGISTRATION.md` (committed 6 Nov 2026, 23:51 UTC, commit a7589cc)
and changes none of its predictions, thresholds or bracket rules.

## Why an addendum

The pre-registered primary source failed its feasibility check. The probe `cantina-wayback-probe-v1` ran on
7 Nov 2026, 03:04-03:06 UTC (after the pre-registration was public) and found **no** Internet Archive capture of
`cantina.xyz/api/v0/competitions` (CDX prefix query: 0 rows). Under the pre-registration's own gate (at least 20
eligible competitions) the API-capture census is infeasible: 0 eligible, P1-P5 not testable. That result is reported
in `paper/cantina-judging-duration-result.md`.

The same probe counted 1,689 capture rows under `cantina.xyz/competitions/` (any subpath), 1,625 of them carrying a
competition id, for 137 distinct ids; 131 ids have HTTP-200 captures on at least 2 distinct days and 105 on at least 5.
These are counts of capture rows only.

## What has been seen before this addendum

- The probe's counts above (no archived page body, no archived status, no archived findings count).
- One read of a **live** (not archived) competition page, Revert v4lend, on 7 Nov 2026 about 03:50 UTC through a
  text-only fetch that does not run scripts. Its text showed a `Status` label followed by `Judging`, and a
  `Findings submitted` label followed by `7,079`. So on today's site both values are in the server-rendered page.
  Whether archived pages from 2024-2026 carry the same labels is unknown.

## Plan (stages; each runs only if the one before allows it)

1. **Timing bound (no bodies).** Job `cantina-pages-bound-v1` uses only capture times of HTTP-200 captures whose path
   is exactly `/competitions/<id>` (optional trailing slash, any query string) and the current API end time E. A
   completion bracket can be at most 14 days wide only if some consecutive gap in [E, captures after E] is at most
   14 days, so the number of ended competitions with such a gap is an **upper bound** on the eligible count. If that
   bound is below **20**, the census is declared infeasible from archived pages, no archived body is fetched, and the
   result file says so. The job refuses to run until this addendum is public on GitHub.
2. **Format check (bodies, no time pairing).** If the bound is at least 20, a job fetches raw captures
   (`/web/<timestamp>id_/<url>`, one request at a time, with pauses) of main pages captured after E, caches them,
   and reports only label vocabulary: which visible-text labels and status words occur, and how often a status and a
   findings count can be read. It does not output any status or count paired with a capture time or a competition.
   From that vocabulary alone, a second short addendum fixes the exact extraction rule (which label gives the
   status, which gives the count) before any duration is computed.
3. **Census.** The pre-registration's rules applied exactly: status classes, brackets, the 14-day eligibility rule,
   the gate of 20, and P1-P5 as written, with the archived page's status and findings count in place of an API
   capture's `status` and `totalFindings`. A capture whose status cannot be read by the fixed rule is excluded and
   counted.

Extraction code may be fixed only for format (for example a label that moved), only before stage 3, and every fix is
listed in the result. Predictions are never changed.

## Extra limits of this source

- A page is one competition per capture, so status dates come from far fewer captures than an API capture would give.
- Many captures appear to come from site-wide crawls on a few days, long after a competition ended; such captures
  date nothing about judging.
- Captured competitions are those the archive happened to crawl; this is not a random sample.

---

*MV2 of Munim, Inc. Made with AI agents working for MV2.*
