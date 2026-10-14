#!/usr/bin/env python3
"""sherlock_crowding.py -- how crowded have Sherlock audit contests become?

Reads the JSONL written by fetch_sherlock.py (one record per contest, straight from
Sherlock's public API) and reports, for finished contests with a submission count:

  * issues submitted per contest day, per $1,000 of pot (stablecoin pots only)
    and per 1,000 nSLOC of scope, with medians by the year a contest started;
  * contests and issues per quarter (the time series);
  * KYC vs non-KYC contests, compared within the same start year;
  * a breakdown by Sherlock's own contest type label.

"Issues submitted" is Sherlock's num_competition_issues: every submission, valid
or not, so this measures crowding, not quality. No third-party dependencies.

Licensed under Apache-2.0. Data it writes is CC BY 4.0.
Made with AI agents working for MV2 of Munim, Inc.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import os
import statistics
from typing import Dict, List, Optional

STABLECOINS = {"USD", "USDC", "USDT", "DAI", "USDS", "RLUSD", "PYUSD", "USDC.E", "USDB", "GHO", "CRVUSD", "FRAX"}
CSV_FIELDS = (
    "id", "title", "type_label", "start", "end", "days", "prize_pool", "rewards", "token",
    "pot_usd", "nsloc", "num_competition_issues", "per_day", "per_1k_usd", "per_ksloc",
    "requires_kyc", "is_best_efforts", "bug_bounty_contest", "is_legacy_contest",
)


def _ts(value) -> Optional[_dt.datetime]:
    if not isinstance(value, (int, float)) or value <= 0:
        return None
    return _dt.datetime.fromtimestamp(value, tz=_dt.timezone.utc)


def load(path: str) -> List[Dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def pot_usd(rec: Dict) -> Optional[float]:
    """Headline pot in USD for stablecoin pots; None otherwise.

    `rewards` is the headline total Sherlock shows; fall back to `prize_pool`.
    """
    token = str(rec.get("token") or "").upper()
    if token not in STABLECOINS:
        return None
    for key in ("rewards", "prize_pool"):
        value = rec.get(key)
        if isinstance(value, (int, float)) and value > 0:
            return float(value)
    return None


def code_size(rec: Dict) -> Optional[int]:
    """nSLOC of the scope: the contest's own figure, else the sum over scope repos."""
    for key in ("nsloc", "scope_nsloc_sum"):
        value = rec.get(key)
        if isinstance(value, (int, float)) and value > 0:
            return int(value)
    return None


def enrich(rec: Dict) -> Optional[Dict]:
    """Typed row for a finished contest with a positive issue count, else None."""
    issues = rec.get("num_competition_issues")
    start, end = _ts(rec.get("starts_at")), _ts(rec.get("ends_at"))
    if rec.get("status") != "FINISHED" or not isinstance(issues, int) or issues <= 0:
        return None
    if start is None or end is None or end <= start:
        return None
    days = max((end - start).total_seconds() / 86400.0, 0.5)
    usd = pot_usd(rec)
    sloc = code_size(rec)
    return {
        "id": rec.get("id"),
        "title": rec.get("title"),
        "type_label": rec.get("type_label") or "",
        "start": start.date(),
        "end": end.date(),
        "days": round(days, 2),
        "prize_pool": rec.get("prize_pool"),
        "rewards": rec.get("rewards"),
        "token": rec.get("token"),
        "pot_usd": usd,
        "nsloc": sloc,
        "num_competition_issues": issues,
        "per_day": issues / days,
        "per_1k_usd": None if usd is None else issues / (usd / 1000.0),
        "per_ksloc": None if sloc is None else issues / (sloc / 1000.0),
        "requires_kyc": bool(rec.get("requires_kyc")),
        "is_best_efforts": bool(rec.get("is_best_efforts")),
        "bug_bounty_contest": bool(rec.get("bug_bounty_contest")),
        "is_legacy_contest": bool(rec.get("is_legacy_contest")),
    }


def rows_from(records: List[Dict]) -> List[Dict]:
    rows = [r for r in (enrich(rec) for rec in records) if r is not None]
    return sorted(rows, key=lambda r: (r["start"], r["id"] or 0))


def _median_block(values: List[float]) -> Dict:
    return {"n": len(values), "median": round(statistics.median(values), 2) if values else None}


def by_year(rows: List[Dict], metric: str, where=None) -> Dict[int, Dict]:
    groups: Dict[int, List[float]] = {}
    for row in rows:
        if where is not None and not where(row):
            continue
        value = row.get(metric)
        if value is None:
            continue
        groups.setdefault(row["start"].year, []).append(value)
    return {year: _median_block(vals) for year, vals in sorted(groups.items())}


def quarterly(rows: List[Dict]) -> List[Dict]:
    groups: Dict[str, List[Dict]] = {}
    for row in rows:
        key = f"{row['start'].year}Q{(row['start'].month - 1) // 3 + 1}"
        groups.setdefault(key, []).append(row)
    return [
        {"quarter": key, "contests": len(grp),
         "issues": sum(r["num_competition_issues"] for r in grp),
         "median_per_day": round(statistics.median(r["per_day"] for r in grp), 2)}
        for key, grp in sorted(groups.items())
    ]


def kyc_within_year(rows: List[Dict]) -> Dict[int, Dict]:
    """Median issues/day for KYC and non-KYC contests that started in the same year."""
    out: Dict[int, Dict] = {}
    for year in sorted({r["start"].year for r in rows}):
        yr = [r for r in rows if r["start"].year == year]
        kyc = [r["per_day"] for r in yr if r["requires_kyc"]]
        open_ = [r["per_day"] for r in yr if not r["requires_kyc"]]
        out[year] = {"kyc": _median_block(kyc), "no_kyc": _median_block(open_)}
    return out


def by_type(rows: List[Dict]) -> Dict[str, Dict]:
    groups: Dict[str, List[float]] = {}
    for row in rows:
        groups.setdefault(row["type_label"] or "(none)", []).append(row["per_day"])
    return {label: _median_block(vals) for label, vals in sorted(groups.items())}


def summary(records: List[Dict]) -> Dict:
    rows = rows_from(records)
    return {
        "records": len(records),
        "finished_with_counts": len(rows),
        "issues_total": sum(r["num_competition_issues"] for r in rows),
        "first_start": rows[0]["start"].isoformat() if rows else None,
        "last_start": rows[-1]["start"].isoformat() if rows else None,
        "per_day_by_year": by_year(rows, "per_day"),
        "issues_by_year": by_year(rows, "num_competition_issues"),
        "per_1k_usd_by_year": by_year(rows, "per_1k_usd"),
        "per_ksloc_by_year": by_year(rows, "per_ksloc"),
        "pot_usd_by_year": by_year(rows, "pot_usd"),
        "days_by_year": by_year(rows, "days"),
        "kyc_within_year": kyc_within_year(rows),
        "per_day_by_type": by_type(rows),
        "quarterly": quarterly(rows),
    }


def write_csv(rows: List[Dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = dict(row)
            for key in ("per_day", "per_1k_usd", "per_ksloc"):
                if out[key] is not None:
                    out[key] = round(out[key], 3)
            writer.writerow(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--in", dest="inp", required=True, help="JSONL from fetch_sherlock.py")
    parser.add_argument("--out-dir", default=None, help="write sherlock_contests.csv and summary.json here")
    args = parser.parse_args(argv)
    records = load(args.inp)
    result = summary(records)
    text = json.dumps(result, indent=2, default=str)
    print(text)
    if args.out_dir:
        os.makedirs(args.out_dir, exist_ok=True)
        write_csv(rows_from(records), os.path.join(args.out_dir, "sherlock_contests.csv"))
        with open(os.path.join(args.out_dir, "summary.json"), "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
