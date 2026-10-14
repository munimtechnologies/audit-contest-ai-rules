#!/usr/bin/env python3
"""cross_platform.py -- fewer contests, same submissions? Sherlock and Cantina together.

Reads the two census CSVs in data/ (one row per finished public contest with a
submission count) and adds them up by the quarter and half-year a contest started:

  * public contests started, per platform and combined;
  * submissions to them (Sherlock's num_competition_issues, Cantina's totalFindings:
    every submission, valid or not), per platform and combined;
  * submissions per contest, combined.

Cantina competitions that share one pot (the 12 Ethereum client competitions of
Feb 2025) are counted as ONE contest with their findings summed, since they were
one event with one prize. Everything else is counted as listed. No third-party
dependencies.

Licensed under Apache-2.0. Data it reads is CC BY 4.0.
Made with AI agents working for MV2 of Munim, Inc.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import os
from typing import Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
SHERLOCK_CSV = os.path.join(HERE, "data", "sherlock_contests.csv")
CANTINA_CSV = os.path.join(HERE, "data", "cantina_census.csv")


def _date(text: str) -> _dt.date:
    return _dt.date.fromisoformat(text.strip()[:10])


def load_sherlock(path: str) -> List[Dict]:
    """[{platform, start, submissions}] from sherlock_contests.csv."""
    with open(path, encoding="utf-8", newline="") as fh:
        return [{"platform": "sherlock", "start": _date(row["start"]),
                 "submissions": int(row["num_competition_issues"])}
                for row in csv.DictReader(fh)]


def load_cantina(path: str) -> List[Dict]:
    """[{platform, start, submissions}] from cantina_census.csv, shared-pot groups merged."""
    rows: List[Dict] = []
    groups: Dict[tuple, Dict] = {}
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            item = {"platform": "cantina", "start": _date(row["start"]),
                    "submissions": int(row["total_findings"])}
            if row.get("shared_pot") == "True":
                key = (row["company"], row["start"], row["end"], row["pot"])
                if key in groups:
                    groups[key]["submissions"] += item["submissions"]
                    continue
                groups[key] = item
            rows.append(item)
    return rows


def quarter(day: _dt.date) -> str:
    return f"{day.year}Q{(day.month - 1) // 3 + 1}"


def half(day: _dt.date) -> str:
    return f"{day.year}H{1 if day.month <= 6 else 2}"


def table(rows: List[Dict], period=quarter, since: Optional[str] = None) -> List[Dict]:
    """Contests and submissions per period, per platform and combined."""
    out: Dict[str, Dict] = {}
    for row in rows:
        key = period(row["start"])
        if since is not None and key < since:
            continue
        cell = out.setdefault(key, {"period": key, "sherlock_contests": 0, "sherlock_submissions": 0,
                                    "cantina_contests": 0, "cantina_submissions": 0})
        cell[row["platform"] + "_contests"] += 1
        cell[row["platform"] + "_submissions"] += row["submissions"]
    result = []
    for key in sorted(out):
        cell = out[key]
        cell["contests"] = cell["sherlock_contests"] + cell["cantina_contests"]
        cell["submissions"] = cell["sherlock_submissions"] + cell["cantina_submissions"]
        cell["per_contest"] = round(cell["submissions"] / cell["contests"], 1)
        result.append(cell)
    return result


def first_full(since: str) -> tuple:
    """First half-year and year that both platforms cover in full, given the first quarter."""
    year, q = int(since[:4]), int(since[-1])
    first_half = {1: f"{year}H1", 2: f"{year}H2", 3: f"{year}H2", 4: f"{year + 1}H1"}[q]
    first_year = str(year if q == 1 else year + 1)
    return first_half, first_year


def summary(sherlock_path: str = SHERLOCK_CSV, cantina_path: str = CANTINA_CSV) -> Dict:
    sherlock, cantina = load_sherlock(sherlock_path), load_cantina(cantina_path)
    since = quarter(min(r["start"] for r in cantina))
    first_half, first_year = first_full(since)
    rows = sherlock + cantina
    return {
        "sherlock_contests": len(sherlock),
        "cantina_contests": len(cantina),
        "combined_since": since,
        "quarterly": table(rows, quarter, since),
        "half_yearly": table(rows, half, first_half),
        "yearly": table(rows, lambda d: str(d.year), first_year),
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sherlock", default=SHERLOCK_CSV)
    parser.add_argument("--cantina", default=CANTINA_CSV)
    parser.add_argument("--table", action="store_true", help="print the quarterly table as text")
    args = parser.parse_args(argv)
    result = summary(args.sherlock, args.cantina)
    if args.table:
        print(f"{'period':8} {'Sherlock':>14} {'Cantina':>14} {'contests':>9} {'submissions':>12} {'per contest':>12}")
        for cell in result["quarterly"] + result["half_yearly"] + result["yearly"]:
            print(f"{cell['period']:8} {cell['sherlock_contests']:>4} {cell['sherlock_submissions']:>9,} "
                  f"{cell['cantina_contests']:>4} {cell['cantina_submissions']:>9,} {cell['contests']:>9} "
                  f"{cell['submissions']:>12,} {cell['per_contest']:>12,.1f}")
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
