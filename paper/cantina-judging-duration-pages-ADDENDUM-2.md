# Second addendum: the fixed extraction rule for archived Cantina competition pages

Written 8 November 2026, about 03:00 UTC, by AI agents working for MV2 of Munim, Inc. Text: CC BY 4.0.
It adds to `paper/cantina-judging-duration-PREREGISTRATION.md` (commit a7589cc) and
`paper/cantina-judging-duration-pages-ADDENDUM.md` (commit 3afce4e). It changes none of their predictions, thresholds
or bracket rules. It is written **before** any status or findings count has been paired with a capture time or a
competition: the census job (stage 3) refuses to run until this file is public on GitHub.

## What stage 2 found (counts over captures only)

Job `cantina-pages-vocab-v1` ran on the Blade from 7 Nov 2026 21:39 UTC to 23:02 UTC; its 9 offline tests passed
first. It fetched every HTTP-200 capture of a competition **main** page taken after that competition's current API end
time: **882 captures of 131 competitions, all 882 fetched** (720 `text/html`, 162 `text/x-component`; the archive
served a different timestamp for 11 of them). Its output holds counts over captures only. Code and output:
`cantina_judging/vocab/`.

| Readable in a capture | Captures |
|---|---|
| A visible `Status` label followed by a value | 528 |
| An embedded JSON `"status"` value | 528 |
| Neither | 354 |
| A visible `Findings submitted` label followed by a number | 431 |
| An embedded JSON `totalFindings` number | 519 |

Since 882 - 354 = 528, the captures with a visible status and those with a JSON status are the **same 528**.

Values after the visible `Status` label (captures): `completed` 461, `judging` 27, `reviewing escalations` 18,
`escalations ended` 11, `escalations` 10, `live` 1 (sum 528, so one value per capture).
Embedded JSON `"status"` values (captures containing each): `complete` 461, `success` 500, `escalations_ended` 29,
`judging` 27, `escalations` 10, `live` 1. `success` is a status of some other object on the page, not of the
competition. Without `success` the values add up to 528, and `escalations_ended` (29) equals `reviewing escalations`
(18) + `escalations ended` (11), so both sources seem to describe the same states. The labels before a findings number
were `Findings submitted` (335 captures) and `Findings submitted:` (96).

## The rule (fixed now; used unchanged in stage 3)

**Captures used.** HTTP-200 captures of the main page `/competitions/<id>` taken strictly after the competition's end E
(current API, read 7 Nov 2026 12:14:30 UTC; the same API read gives the final `totalFindings`). A capture's time is the
timestamp the archive actually served (`final_ts`, when it redirected). A capture whose served time is not after E,
or whose page is not in the stage-2 cache, is excluded and counted. Two captures of one competition with the same
served time count once. No page is fetched again in stage 3.

**Status.** Read from the visible text, scripts and styles skipped: the first text chunk that, lower-cased, matches
`^status\s*:?\s*(.*)$`; the value is what follows on that chunk, or else the next chunk (whitespace collapsed,
lower case). A capture with no such value is excluded ("no status"); one with two different values is excluded
("ambiguous status").

**Status class**, exactly as pre-registered: `live` = `live`; `complete` = `complete` or `completed`; every other value
seen after E is `post-live` (so `judging`, `escalations`, `reviewing escalations` and `escalations ended` are
post-live). Every distinct value is listed in the result.

**Cross-check (exclusion only).** Embedded JSON `"status"` values are mapped `live` -> live, `complete`/`completed` ->
complete, `judging`/`escalations`/`escalations_ended` -> post-live; any other JSON value (such as `success`) is
ignored. If the mapped JSON values give exactly one class and it differs from the visible-text class, the capture is
excluded ("text and JSON disagree"). If they give several classes or none, the visible text stands and this is counted.

**Findings count.** The first visible chunk equal to `Findings submitted` or `Findings submitted:` (any case) whose
next chunk is a whole number (`7079` or `7,079`); otherwise, the embedded JSON `totalFindings` if the capture holds
exactly one distinct value of it; otherwise unreadable. An unreadable count never excludes a capture; it only removes
that competition from P5 (counted).

**Brackets** follow the pre-registration. Reading of the reversal clause, stated now: the completion bracket's upper
end is the first `complete` capture after E, and its lower end is the latest capture before that one (all of which
are not complete), or E if there is none. The judging-start bracket's upper end is the first `post-live` or `complete`
capture, and its lower end is the latest `live` capture before it, or E.

**"Ended inside the archive's coverage"** (left undefined in the pre-registration) means E is no earlier than the
earliest HTTP-200 capture anywhere under `cantina.xyz/competitions/` in the stage-1 index.

**Year** for P4 is the UTC year of E. **Final count** for P2 and P5 is `totalFindings` from the API read above.
P3 and P5 are computed over every competition that has the needed captures, as worded; P1, P2 and P4 over eligible
competitions only. If fewer than 20 competitions are eligible, P1-P5 are all graded **not testable** (the gate).

## Limits added by this rule

- 354 of 882 captures (40%) carry no status by either route and are lost; if they are concentrated in one period
  (for example an older page format), that period is under-covered.
- End dates printed on archived pages are not read, so the pre-registration's "both ends are reported" check is not
  made; E is always the current API value.

Census job: `cantina-pages-census-v1` (code and tests published with its result under `cantina_judging/census/`).

---

*MV2 of Munim, Inc. Made with AI agents working for MV2.*
