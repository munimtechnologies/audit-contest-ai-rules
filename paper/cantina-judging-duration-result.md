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

## Stage 2: page format (added 8 November 2026, about 03:00 UTC)

Job `cantina-pages-vocab-v1` ran on 7 Nov 2026, 21:39-23:02 UTC; its 9 offline tests passed first. It fetched all
**882** HTTP-200 main-page captures taken after a competition's end (131 competitions), one at a time with a pause,
and cached them for stage 3. It reported counts over captures only.

| Readable in a capture | Captures (of 882) |
|---|---|
| Visible `Status` label with a value | 528 (60%) |
| Embedded JSON competition status | the same 528 |
| Neither | 354 (40%) |
| Visible `Findings submitted` number | 431 |
| Embedded JSON `totalFindings` number | 519 |

Status values after the visible label: `completed` 461, `judging` 27, `reviewing escalations` 18,
`escalations ended` 11, `escalations` 10, `live` 1. Only 67 of the 528 readable captures (13%) show a competition
that is not yet complete, which fits the earlier caution that most captures come long after judging ended.

The extraction rule is now fixed in `paper/cantina-judging-duration-pages-ADDENDUM-2.md`, written before any status
was paired with a time or a competition. Stage 3 (`cantina-pages-census-v1`) applies it to the cached pages, refuses
to run until that addendum is public, and grades P1-P5 exactly as pre-registered.

`cantina_judging/vocab/`: `job.py`, `test_job.py`, `summary-public.json` (counts only; the free-text label lists are
left out because they quote page text with personal handles and links). Code Apache-2.0, data CC BY 4.0.

## Stage 3, first attempt: stopped before computing anything (added 8 November 2026, about 15:40 UTC)

Job `cantina-pages-census-v1` ran on 8 Nov 2026, 12:57-12:59 UTC. Its 13 offline tests passed, and it found the second
addendum public on its first poll. It then stopped with exit 4 ("stage 1 or stage 2 inputs missing in /data"),
before reading any page. It had been placed on a different machine from the one that ran stages 1 and 2, and that
machine's copy of the data volume did not hold their inputs. **No status was paired with a time and no prediction
was graded.**

`paper/cantina-judging-duration-pages-ADDENDUM-3.md` fixes, before the next run, how job `cantina-pages-census-v2`
handles this. Where the cache is present, it runs exactly as before. Elsewhere it rebuilds the inputs from the
published stage-1 table, pinned by its git blob sha, and from the CDX index cut off at the stage-1 read. Its grades
count as the pre-registered census only if the rebuild reproduces the published stage-1 and stage-2 counts;
otherwise they are reported as descriptive only. The predictions and the extraction rule are unchanged.

## Stage 3: census (added 8 November 2026, about 23:40 UTC)

### Outcome: the gate failed, 0 of 142 competitions eligible (negative result)

Job `cantina-pages-census-v2` ran on 8 Nov 2026, 19:52:20-19:53:43 UTC. Its offline tests passed first. It found the
second and third addenda public on its first poll, and it ran on the machine that holds the stage-2 cache, so it read
the cached pages directly (no rebuild). Its check against the published stage-2 counts matched exactly (882 captures
selected, 882 cached, 528 with a status, 528 with a JSON status, 11 redirected), so its grades count as the
pre-registered census.

| Check | Value |
|---|---|
| Ended competitions | 142 |
| With at least one readable capture after the end | 130 |
| With a readable `complete` capture after the end (a completion bracket exists) | 125 |
| **Eligible** (completion bracket at most 14 days wide, end inside the archive's coverage from 4 Mar 2024) | **0** |
| Narrowest completion bracket | 18.07 days; 5 brackets are 30 days wide or less (18.1, 18.5, 19.5, 22.3, 22.3) |
| Gate | 20: **failed** |
| P1, P2, P3, P4, P5 | **not testable**, exactly as the pre-registration's gate requires |

As the pre-registration says for this case: **the Internet Archive is too thin to answer the question.** Its copies
of Cantina's pages cannot date when a competition's judging ended to within 14 days for any of the 142 competitions.
Every bracket that exists is in `cantina_judging/census/brackets_by_id.csv`.

Why far fewer than the stage-1 bound of 68: the bound counted any short gap between capture times, but a competition
is eligible only if the short gap holds the change to `complete`, and only captures with a readable status count. 354
of the 882 captures (40%) show no status. Readable captures of any Cantina competition fall on 1 to 5 distinct days a
month (`capture_days_per_month` in `summary.json`), and none is dated after July 2026: all 52 captures served from
August 2026 on show no status.

### Reading checks

- 521 of the 882 captures were read. Excluded: 354 with no status, 6 whose served time duplicates another capture of
  the same competition, 1 served from a time not after the end.
- In all 521, the visible status and the embedded JSON status agree. Where a capture shows both a visible and a JSON
  findings count (427 captures), the two are equal in all 427.
- No competition went back from `complete` to another status in a later capture (0 reversals).

### Descriptive only (not tests of P1-P5)

These figures come from the brackets that exist. The gate failed, so none of them grades a prediction.

- **Non-complete captures.** 55 competitions have a readable capture after the end that is not `complete`. In 27 of
  them the earliest such capture shows a findings count above 0, and in all 27 it equals today's count in Cantina's
  API. In one competition the count already matched about 14 hours after the end. 20 show 0, and 8 show no count.
- **Zero counts.** All 86 captures in the file with a count of 0 got it from embedded JSON, in captures dated 17 Apr
  2024 to 26 Mar 2025, and 64 of the 86 are on pages already showing `completed`. We read a 0 there as an unfilled
  field rather than a count. That is our interpretation, not part of the rule.
- **Long post-live periods.** Four competitions that ended inside the coverage still showed a non-complete status 60
  days or more after their end. The longest is 233.7 days: `reviewing escalations` on 19 Jun 2025, for a competition
  that ended on 28 Oct 2024. This is the status the archived page displayed; we can't tell from it whether the page
  was up to date.
- **Start of judging.** 5 competitions have a judging-start bracket at most 3 days wide (the brackets P3 would have
  used). In all 5, the first capture past `live` came within 2.6 days of the end.

### Limits

- One archive, one site. A Cantina page served without a status (40% of captures here) can't be read by this rule;
  we did not try other ways of reading those pages, and the rule doesn't allow them.
- Findings counts are compared with today's API, not with a count from the time of the capture.
- This says nothing about how long Cantina's judging takes. It only says that this source can't measure it.

### What happens next

The census ends here. P1-P5 stay not testable, and they are not re-tested on another source without a new,
separately published pre-registration. Revert v4lend is still followed directly: on 8 Nov 2026, about 23:25 UTC, its
page still showed "Judging" and "7,079" findings.

`cantina_judging/census/`: `job.py`, `test_job.py`, `summary.json`, `brackets_by_id.csv` (one row per ended
competition), `captures.csv` (one row per selected capture: competition id, capture times, status, findings count and
any exclusion reason; no page text). Code Apache-2.0, data CC BY 4.0.

---

*MV2 of Munim, Inc. Made with AI agents working for MV2.*
