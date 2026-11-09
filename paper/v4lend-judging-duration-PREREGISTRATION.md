# Pre-registration: how long does judging of Cantina's Revert v4lend competition take, against Cantina's stated "1–2 weeks"?

Registered 9 Nov 2026, about 07:40 UTC, while the competition still shows "Judging". Nothing below may be changed after
this file is committed; anything learned later goes in `paper/CORRECTIONS.md` or a dated addendum, never here.

Made with AI agents working in the name of MV2 of Munim, Inc. Text CC BY 4.0. Part of
https://github.com/munimtechnologies/audit-contest-ai-rules (paper sections 3.5 and 3.8).

## Why

Section 3.8 of the paper found that the Internet Archive is too sparse to date the end of judging for any earlier
Cantina competition (0 of 142 eligible). Section 3.5 follows one live competition, Revert v4lend, into judging. The only
duration Cantina itself states is on its page for clients, "How Cantina Audits Work"
(https://docs.cantina.security/security-teams/services/how-audits-work, "Last reviewed: March 2026", read 9 Nov 2026):

> "Most competitive audits run 1–4 weeks." ... "Judging and report delivery add 1–2 weeks post-review."

Cantina's page for researchers (https://docs.cantina.security/researchers/participation/competitions, read 9 Nov 2026)
lists the phases after a competition (judging, escalation if applicable, payment) and gives no durations. One web search
on 9 Nov 2026 found no other figure published by Cantina. This file fixes, before the outcome is known, how one competition's
judging will be measured and compared with the stated 1–2 weeks. It is one competition (n = 1): it can show whether
one large competition fits the stated range, not what is typical.

## What is already known (before registration)

- Competition: Revert v4lend, `cantina.xyz/competitions/e275368c-547d-4d91-a418-053ad31082a8`, $50,000 USDC.
- End: 2026-11-03 18:30 UTC (Cantina's API, paper section 3.5). Call this E.
- Judging began between about E + 56 h and E + 61 h (6 Nov 2026, about 02:30-07:30 UTC), at 7,079 findings submitted.
- Readings showing "Judging" and "7,079" since then: 7 Nov 12:14:30 UTC (API, machine-recorded), about 12:45-12:50 UTC
  on 7 Nov (API and page), about 23:25 UTC on 8 Nov, about 01:15 and 02:50 UTC on 9 Nov, and about 07:25 UTC on 9 Nov
  2026 (page-reading tool; the competitions listing showed the same status at the same time).

## Measurement

- Source: the competition page above, read with a page-reading tool, about once a day at least until it shows
  "Complete" (or until 31 Dec 2026, whichever comes first). Each reading records the UTC time (approximate, to about
  15 minutes), the status label exactly as shown, and the "Findings submitted" number. Readings are logged in a new
  file `v4lend/judging_readings.csv` (time_utc, status, findings, source), published with the result.
- Statuses seen in earlier work (paper sections 3.5 and 3.8) include live, judging and complete/completed; Cantina's
  documentation also names an escalation phase. Any label is recorded exactly as shown. "Complete" below means either
  "complete" or "completed".
- **T_judged**: the end of judging, bracketed by the last reading showing "Judging" and the first reading showing any
  later status (for example "Escalations" or "Complete").
- **T_complete**: bracketed by the last reading not showing "Complete" and the first reading showing it.
- Each bracket is reported with its width. Durations are reported both from E (the end of the competition) and from
  the start of judging.

## How the stated "1–2 weeks post-review" is read

"Post-review" is read as after the end of the competition (E), since the competition is the review. The stated range
then puts the end of judging and report delivery at or before E + 14 days = **2026-11-17 18:30 UTC** (the "mark").

## Predictions (fixed now)

- **P1.** The first reading taken at or after the mark (17 Nov 2026, 18:30 UTC) still shows "Judging". That is, judging
  of this competition takes longer than the stated upper bound of 2 weeks after the end.
- **P2.** The first reading taken at or after E + 21 days (24 Nov 2026, 18:30 UTC) does not show "Complete".

Reasoning, written down so it can be judged later: 7,079 submissions on a $50,000 pot is a heavy judging load (about
$7 of pot per submission); judging started about 2.5 days after the end, and no status change and no count change
appeared in the first 3 days of judging. This is a guess from one competition's readings, not from any model.

## Grading rules

- P1 and P2 are each graded on the first reading at or after its own date. If that reading is more than 24 hours after
  the date and shows a later status than the one predicted, and no reading inside that gap showed the predicted
  status, the prediction is reported as **not gradable** (the change might have happened before or after the date),
  not as failed.
- If the page cannot be read (error, missing status) at a reading, that reading is logged as unreadable and does not
  count; the next readable one is used, under the 24-hour rule above.
- If Cantina changes the competition's end date, or the page stops showing a status, this is reported in
  `paper/CORRECTIONS.md` before any grading.
- Whatever happens, the result is published, including a failed or ungradable prediction, in a short result file
  `paper/v4lend-judging-duration-result.md` and as a correction entry, with the readings CSV.

## Limits

- n = 1. One very large competition says nothing on its own about Cantina's typical judging time.
- The client page describes Cantina's services in general and is undated beyond "Last reviewed: March 2026"; reading
  "post-review" as "after the competition's end" is our interpretation. If judging is measured from the start of
  judging instead of E, the mark moves about 2.5 days later; both durations will be reported.
- Readings are taken by a page-reading tool at irregular times, so each bracket can be up to about a day wide (wider
  if a day is missed). Bracket widths are always reported.
- A status label is what the public page shows. It may lag or lead Cantina's internal process; payments and the
  final report are not observed.

MV2, Munim, Inc., mv2@munimtech.com
