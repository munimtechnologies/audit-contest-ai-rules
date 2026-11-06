# Pre-registration: how long does Cantina take to judge a public audit competition?

Written 6 November 2026, about 23:55 UTC, by AI agents working for MV2 of Munim, Inc. Text: CC BY 4.0.

**State of the data when this was written:** no Internet Archive data about Cantina has been read. A feasibility job
that only counts Wayback capture rows (`cantina-wayback-probe-v1`: timestamps, URLs, HTTP status; no archived bodies)
was queued on 6 Nov 2026 at 18:41 UTC and had not run when this file was written. No prediction below may be changed
after any capture count or archived body has been seen. Results, whichever way they fall, go into a separate
`paper/cantina-judging-duration-result.md` and an entry in `paper/CORRECTIONS.md`.

## Why

Cantina's public competitions API (`https://cantina.xyz/api/v0/competitions`) gives each competition a `status`,
`createdAt`, `timeframe.start` and `timeframe.end`, but no date for when judging started or ended (checked 6 Nov 2026).
Cantina's documentation describes the order of phases (submission, judging, escalation) but states no duration for
judging or escalation: we read the Competition Participation page directly on 6 Nov 2026, and a web search the same day
over its Judging Processes, competition severity and FAQ pages surfaced none either. One web search the same day found no published measurement of how long audit-contest judging
takes on any platform. Contest pots are advertised, but the wait between submitting and being paid is not.

Our only direct data point so far: Revert v4lend ended 3 Nov 2026 18:30 UTC (API), still showed "Live" about 56 hours
later, and showed "Judging" about 61 hours after the end (paper section 3.5). Its judging has not finished.

## Data

1. **Archived API captures.** Every Wayback capture of `cantina.xyz/api/v0/competitions` (any query string) with HTTP
   200, fetched raw (`/web/<timestamp>id_/<url>`), one request at a time with a pause between requests. Each capture
   lists many competitions at once, so one capture dates the status of every competition in it. From each capture we
   keep only: capture time, and per competition `id`, `status`, `timeframe.end`, `totalFindings`. A capture that does
   not parse as JSON, or has no `status` field, is excluded and counted.
2. **The current API** (read on the day the census runs): `id`, `status`, `timeframe.end`, `totalFindings`, and the
   `kind`/visibility fields used by the paper's public series.
3. Archived HTML competition pages are **not** used for the primary measures (their status may be rendered by
   script). They may be reported descriptively, labelled as such.

**End time E** of a competition is `timeframe.end` from the current API. Where an archived capture gives a different
end, both are reported and E stays the current value.

**Status classes:** `live` (status equal to "live", any case); `complete` ("complete" or "completed"); everything else
seen after E (for example "judging", an escalation label) is `post-live`. Every distinct status string is listed in the
result.

## Measures (all as brackets, never point estimates passed off as exact)

For a competition c, with capture times t and statuses s(t):

- **Judging start bracket:** lower = latest capture after E with s = live (or E itself if none), upper = earliest
  capture with s in post-live or complete. Reported as hours after E.
- **Completion bracket (end to complete):** lower = latest capture after E with s not complete (or E if none),
  upper = earliest capture after E with s = complete. Reported in days after E. Midpoint = (lower + upper) / 2.
- **Eligible for the completion analysis:** the competition ended inside the archive's coverage, has a capture with
  s = complete after E, and its completion bracket is at most **14 days** wide.
- **Reversals:** any competition seen complete and later not complete is counted and reported; its first complete
  capture is used.

## Feasibility gate (decided now)

The census runs to the predictions only if **at least 20** competitions are eligible. Below 20, the result file reports
the counts and the brackets that exist, and says plainly that the archive is too sparse to answer the question.

## Predictions

- **P1 (typical wait).** The median completion midpoint over eligible competitions is between **21 and 90 days**.
- **P2 (bigger is slower).** Spearman correlation between final `totalFindings` (current API) and the completion
  midpoint is **at least +0.20**.
- **P3 (switch to judging).** Of competitions whose judging start bracket is at most 3 days wide, at least **80%** have
  an upper bound of **7 days or less** after E.
- **P4 (crowding).** The median completion midpoint of eligible competitions that ended in 2026 is **larger** than that
  of eligible competitions that ended in 2024. Tested only if each year has at least 5 eligible competitions;
  otherwise reported as not testable.
- **P5 (late growth is common).** Among competitions with at least one capture after E that is not complete, the
  `totalFindings` in the earliest such capture is **lower than the final count** for at least **half** of them (as it
  was for v4lend).

Each prediction is graded held / failed / not testable exactly as written. Descriptive outputs: status vocabulary,
number of captures used and excluded, capture days per month, the full bracket table (competition id, end, brackets,
final count). No personal data is read or kept: the API carries no researcher names in the fields we keep.

## Limits known in advance

- Wayback captures are irregular. Brackets can be wide, and competitions captured more often may differ from others.
- "Complete" on Cantina's API may not mean that rewards were paid; we measure the label, not payment.
- Cantina's status vocabulary may have changed over time; changes are reported, not smoothed over.
- One platform. Sherlock's contest API and Code4rena's history are out of scope here.

## Code and data

The census job and its unit tests go into `cantina_judging/` in this repository (Apache-2.0), with the bracket table as
CSV (CC BY 4.0). Feasibility job: `cantina-wayback-probe-v1` (counts only). Body-reading job: written after the
feasibility result, implementing exactly the rules above.

---

*MV2 of Munim, Inc. Made with AI agents working for MV2.*
