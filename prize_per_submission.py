#!/usr/bin/env python3
"""prize_per_submission.py -- how much headline prize money each submission competes for.

Reads the Sherlock and Cantina census CSVs in data/ and adds them up by the
half-year a contest started:

  * contests with a US-dollar pot (stablecoin pots; contests paid in OP tokens and
    events with no pot are left out, together with their submissions, and counted
    in `left_out`);
  * the headline prize money of those contests (Sherlock's `rewards` total, as in
    the census's pot_usd; Cantina's pot);
  * the submissions they received (every submission, valid or not), and headline
    dollars per submission;
  * the same without mega pots of $1M or more, which dominate the totals;
  * per contest (v0.7.1): the median of each contest's own prize money per
    submission, and how many contests offered under $100 per submission.

Cantina's 12 Ethereum client competitions of Feb 2025 shared one $2M USDC pot.
They count as one contest, with the pot counted once and their findings summed.
The census leaves their pot_usd empty, so that pot is read from `pot`.
No third-party dependencies.

Licensed under Apache-2.0. Data it reads is CC BY 4.0.
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

HERE = os.path.dirname(os.path.abspath(__file__))
SHERLOCK_CSV = os.path.join(HERE, "data", "sherlock_contests.csv")
CANTINA_CSV = os.path.join(HERE, "data", "cantina_census.csv")
STABLE = {"USDC", "USDT", "DAI", "GHO", "RLUSD"}
MEGA = 1_000_000
UNDER = 100  # per-contest dollars per submission counted as "under"
SINCE = "2024H1"  # first half-year both censuses cover in full


def _date(text: str) -> _dt.date:
    return _dt.date.fromisoformat(text.strip()[:10])


def _money(text: Optional[str]) -> Optional[float]:
    text = (text or "").strip()
    return float(text) if text else None


def half(day: _dt.date) -> str:
    return f"{day.year}H{1 if day.month <= 6 else 2}"


def load_sherlock(path: str) -> List[Dict]:
    """[{platform, start, usd, submissions}] from sherlock_contests.csv (usd None if not a USD pot)."""
    with open(path, encoding="utf-8", newline="") as fh:
        return [{"platform": "sherlock", "start": _date(row["start"]), "usd": _money(row["pot_usd"]),
                 "submissions": int(row["num_competition_issues"])}
                for row in csv.DictReader(fh)]


def load_cantina(path: str) -> List[Dict]:
    """[{platform, start, usd, submissions}] from cantina_census.csv, shared-pot groups merged."""
    rows: List[Dict] = []
    groups: Dict[tuple, Dict] = {}
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            usd = _money(row["pot_usd"])
            shared = row.get("shared_pot") == "True"
            if usd is None and shared and row["currency"].strip() in STABLE:
                usd = _money(row["pot"])
            item = {"platform": "cantina", "start": _date(row["start"]), "usd": usd,
                    "submissions": int(row["total_findings"])}
            if shared:
                key = (row["company"], row["start"], row["end"], row["pot"])
                if key in groups:
                    groups[key]["submissions"] += item["submissions"]
                    continue
                groups[key] = item
            rows.append(item)
    return rows


def table(rows: List[Dict], since: str = SINCE, cap: Optional[float] = None) -> List[Dict]:
    """Per half-year: USD-pot contests, their prize money and submissions, dollars per submission."""
    out: Dict[str, Dict] = {}
    for row in rows:
        key = half(row["start"])
        if key < since:
            continue
        cell = out.setdefault(key, {"period": key, "contests": 0, "usd": 0.0, "submissions": 0,
                                    "left_out": 0, "left_out_submissions": 0})
        if row["usd"] is None:
            cell["left_out"] += 1
            cell["left_out_submissions"] += row["submissions"]
            continue
        if cap is not None and row["usd"] >= cap:
            continue
        cell["contests"] += 1
        cell["usd"] += row["usd"]
        cell["submissions"] += row["submissions"]
    result = []
    for key in sorted(out):
        cell = out[key]
        cell["usd"] = int(round(cell["usd"]))
        cell["per_submission"] = round(cell["usd"] / cell["submissions"], 2) if cell["submissions"] else None
        result.append(cell)
    return result


def per_contest(rows: List[Dict], since: str = SINCE, under: float = UNDER) -> List[Dict]:
    """Per half-year: median of each USD-pot contest's own dollars per submission, and how many are under `under`."""
    ratios: Dict[str, List[float]] = {}
    for row in rows:
        key = half(row["start"])
        if key < since or row["usd"] is None or not row["submissions"]:
            continue
        ratios.setdefault(key, []).append(row["usd"] / row["submissions"])
    result = []
    for key in sorted(ratios):
        values = ratios[key]
        below = sum(1 for value in values if value < under)
        result.append({"period": key, "contests": len(values),
                       "median_per_submission": round(statistics.median(values), 2),
                       "under": below, "under_share": round(below / len(values), 3)})
    return result


def summary(sherlock_path: str = SHERLOCK_CSV, cantina_path: str = CANTINA_CSV) -> Dict:
    rows = load_sherlock(sherlock_path) + load_cantina(cantina_path)
    return {
        "since": SINCE,
        "all_usd_pots": table(rows),
        "pots_under_1m": table(rows, cap=MEGA),
        "per_contest": per_contest(rows),
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sherlock", default=SHERLOCK_CSV)
    parser.add_argument("--cantina", default=CANTINA_CSV)
    parser.add_argument("--table", action="store_true", help="print the half-year tables as text")
    args = parser.parse_args(argv)
    result = summary(args.sherlock, args.cantina)
    if args.table:
        for name in ("all_usd_pots", "pots_under_1m"):
            print(name)
            print(f"{'period':8} {'contests':>9} {'prize USD':>12} {'submissions':>12} {'USD/submission':>15}")
            for cell in result[name]:
                print(f"{cell['period']:8} {cell['contests']:>9} {cell['usd']:>12,} {cell['submissions']:>12,} "
                      f"{cell['per_submission'] or 0:>15,.2f}")
        print("per_contest")
        print(f"{'period':8} {'contests':>9} {'median USD/submission':>22} {'under $' + str(UNDER):>11}")
        for cell in result["per_contest"]:
            print(f"{cell['period']:8} {cell['contests']:>9} {cell['median_per_submission']:>22,.2f} "
                  f"{cell['under']:>5} ({cell['under_share']:.0%})")
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
