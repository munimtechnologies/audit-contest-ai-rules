# Revert v4lend (Cantina): the "Findings submitted" counter, read 104 times

Data for section 3.5 of `paper/audit-contest-census.md` (version 1.9). Made with AI agents working for MV2 of
Munim, Inc. Data: CC BY 4.0. Code: Apache-2.0.

## Files
- `v4lend_findings_count.csv`: 104 readings, 14 Oct 2026 09:55 UTC to 6 Nov 2026 07:10 UTC. Columns:
  `row, read_at_utc, time_is_approx, findings_submitted, reads`.
  - `time_is_approx = yes`: the time is the run's start stamp plus a few minutes (error of a few minutes).
  - `reads = 2`: the value was read twice (the page, then the page with `?view=details`). Two early pairs differed
    by one (rows 78 and 83, minutes apart); the file keeps the first read. Rows 85-104 were read twice and agreed.
- `v4lend_rates.py`: checks the file (row numbers, times increasing, count never falling) and writes the
  rate between consecutive readings (`windows.csv`), a day table built from the reading nearest each 00:00 UTC
  (`day_table_nearest.csv`) and `summary.json`. Standard library only, no network.
- `test_v4lend_rates.py`, `test_v4lend_rates_late.py`: tests pinned before the late data existed. They read the CSV
  in this folder, so run them from here: `python -m unittest -v test_v4lend_rates test_v4lend_rates_late`.
  All 12 passed on 6 Nov 2026 (python:3.12, no network).
- Reproduce the day table: `python v4lend_rates.py --csv v4lend_findings_count.csv --out-dir out --first-day
  2026-10-15 --last-day 2026-11-03`. On 6 Nov 2026 this gave 19 rows, 4.71 to 24.86 findings an hour.

## Source and limits
- Every value is the public counter on https://cantina.xyz/competitions/e275368c-547d-4d91-a418-053ad31082a8 as a
  page-reading tool reported it, not an API value. Cantina's API (`cantina.xyz/api/v0/competitions`) agreed where we
  compared: 1,369 at 14 Oct 20:03 UTC (between rows 1 and 2), 6,906 at 5 Nov 09:45 UTC (row 101), 7,079 with status
  "judging" at 6 Nov ~07:10 UTC (row 104).
- End time: 2026-11-03 18:30 UTC (Cantina's API; the page shows only the date). The count at the end lies between
  row 99 (6,327, 2 h 38 min before) and row 100 (6,726, 18 h 45 min after).
- The counter kept rising after the end while the page said "Live" (rows 100-103, +353). Page and API switched to
  "Judging" between rows 103 and 104, at 7,079. What the post-end additions are is not known.
- No reading fell near 00:00 UTC on 1, 2 or 3 Nov, so the day-table rows for 31 Oct, 1 Nov and 2 Nov span 16.8, 35.7
  and 9.5 hours, not one day.
- Pre-registered next check (not yet read when this was published): a reading at least 24 hours after 6 Nov 07:10 UTC
  will still show 7,079.
- Aggregate only: no handles, names or per-person data. The page shows no judged or valid count.
