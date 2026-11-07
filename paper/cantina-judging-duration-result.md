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

---

*MV2 of Munim, Inc. Made with AI agents working for MV2.*
