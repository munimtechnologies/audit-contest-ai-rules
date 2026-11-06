# Do Cantina's finding counts move after a contest ends? (pre-registered check, run 5 Nov 2026)

Supports the Cantina caveat in section 6 of `paper/audit-contest-census.md` (version 1.9). Made with AI agents working
for MV2 of Munim, Inc. Code: Apache-2.0. Data: CC BY 4.0.

## What it did
`drift.py` compares this repository's 14 Oct 2026 snapshot of `https://cantina.xyz/api/v0/competitions`
(`data/cantina_census.jsonl`) with one fresh read of the same API (5 Nov 2026 09:45:39 UTC), matched by contest id.
The set S is the 125 public contests that were "complete" on 14 Oct with a finding count. Three predictions were
written before the run: (D1) at least 95% of S unchanged; (D2) Revert v4lend at or above 6,906; (D3) the sum over S
moves by less than 0.5%.

## Result: all three held
- D1: 125 of 125 unchanged. D3: 58,193 then and now. D2: v4lend 6,906 (status still "live").
- 0 contests missing, 0 new public contests, 19 new private ones (counted only; no names kept).
- Limit: the most recently ended contest in S had ended 124 days before the snapshot. This shows that counts of
  long-finished contests are stable; it says nothing about the first weeks after an end.

## Files
- `drift.py`, `test_drift.py` (offline tests; run from this folder: `python -m unittest -v test_drift`).
  `python drift.py --out-dir out` makes network reads of Cantina's public API and of this repository's raw
  `data/cantina_census.jsonl`, then writes the comparison to `out/`. A re-run today compares against today's API.
- `drift_rows_20261105.csv`: one row per contest compared (public contest names and counts only; private contests
  have no name).
- `drift_summary_20261105.json`: the graded summary.
