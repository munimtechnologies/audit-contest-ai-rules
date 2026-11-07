# Result: Cantina judging-duration census, primary source (archived API captures)

Written 7 November 2026, about 04:10 UTC, by AI agents working for MV2 of Munim, Inc. Text: CC BY 4.0.
Pre-registration: `paper/cantina-judging-duration-PREREGISTRATION.md` (commit a7589cc, 6 Nov 2026, 23:51 UTC).

## Outcome: infeasible from this source (negative result)

The Internet Archive holds **no capture** of Cantina's public competitions API that our query could find, so the
pre-registered census cannot be run from it.

| Check | Value |
|---|---|
| Probe job | `cantina-wayback-probe-v1`, ran 7 Nov 2026 03:04:40-03:05:59 UTC (after the pre-registration was public) |
| Query | Wayback CDX, `url=cantina.xyz/api/v0/competitions`, `matchType=prefix`, `limit=50000` |
| Capture rows found | **0** (no error; the same job's second query returned 1,689 rows, so the CDX service answered) |
| Eligible competitions | **0** (gate: at least 20) |
| P1, P2, P3, P4, P5 | **not testable**, exactly as the pre-registration's gate requires |

No archived body was fetched by the probe; it counts capture rows only.

## Descriptive: archived competition pages (counts only)

The same probe's second query (`cantina.xyz/competitions/`, prefix) found 1,689 capture rows; 1,625 carry a
competition id, for 137 distinct ids. 134 ids have at least one HTTP-200 capture, 131 have HTTP-200 captures on at
least 2 distinct days, and 105 on at least 5 (these counts include subpaths such as a leaderboard tab). The earliest
HTTP-200 capture in the per-id table is from 4 March 2024. Revert v4lend, the competition the paper followed in
104 readings, has a single capture (7 October 2026, about four weeks before its 3 November end). Per-id counts:
`cantina_judging/probe/page_captures_by_id.csv` (CC BY 4.0).

Many ids share their last capture day (for example 16-17 June 2026 and 11 September 2026), which suggests site-wide
crawls on a few days rather than regular visits. Such captures can only date a status change if one happens to fall
close to it.

## Limits

- One CDX query form (prefix on `cantina.xyz/api/v0/competitions`). The archive normalises `www.` and the scheme,
  but captures of other API paths or versions, if any exist, were not looked for.
- "No capture found" is a statement about the archive's index on 7 Nov 2026, not about Cantina.

## What happens next

The question is kept open through archived competition pages instead, under
`paper/cantina-judging-duration-pages-ADDENDUM.md`: first a bound computed from capture times alone (no page bodies)
decides whether at least 20 competitions could even be eligible; only then are page bodies read. P1-P5 stay exactly
as pre-registered.

## Code and data

`cantina_judging/probe/`: `job.py`, `test_job.py` (6 offline tests; all passed in the job run), `summary.json`,
`page_captures_by_id.csv`, `api_captures.csv` (header only: no rows). Code Apache-2.0, data CC BY 4.0.

## Stage 1 of the archived-page route: timing bound (added 7 November 2026, about 13:00 UTC)

Job `cantina-pages-bound-v1` ran on 7 Nov 2026, 12:13:47-12:14:57 UTC, after confirming that the addendum was public
on GitHub (first poll). Its 7 offline tests passed first. It read capture **times** from the Wayback CDX index
(1,689 rows, the same query as the probe) and each competition's current end time from Cantina's API (read 12:14:30
UTC). It read no archived page and no archived status.

| Count | Value |
|---|---|
| Competitions in Cantina's API | 145 (3 without an end time, 0 ending in the future, 142 ended) |
| Ended, with an HTTP-200 main-page capture after the end | 131 |
| **Upper bound on eligible competitions** (some gap of 14 days or less between consecutive points: end, then captures after it) | **68** (all 68 show `complete` in today's API) |
| Of those, with some gap of 3 days or less (most that could enter P3) | 39 |
| Same bound counting subpaths too (descriptive only, not the rule) | 107 |
| Gate | 20, so the gate **can** pass |

The bound counts only whether a short enough gap exists. A competition counts toward the gate only if, in stage 3,
its archived pages show the status change inside such a gap, so the real eligible count can be anywhere from 0 to 68.

Next, as the addendum fixes: stage 2 reads archived main pages captured after each end and reports only which labels
and status words occur, never a status paired with a time or a competition. A second short addendum then fixes the
extraction rule before any duration is computed.

`cantina_judging/bound/`: `job.py`, `test_job.py`, `summary.json`, `bounds_by_id.csv` (one row per ended competition:
current API status, end and findings count, plus capture-gap figures). Code Apache-2.0, data CC BY 4.0.

---

*MV2 of Munim, Inc. Made with AI agents working for MV2.*
