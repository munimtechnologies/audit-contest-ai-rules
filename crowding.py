#!/usr/bin/env python3
"""crowding.py -- how crowded are Cantina audit competitions?

Reads two small hand-collected tables in data/ (each row checked on the
competition's public cantina.xyz page; see checked_on) and reports:

  * findings submitted per contest day, and per $1,000 of headline prize
    (USD/USDC pots only), with medians by the year a contest started;
  * how concentrated the payouts were in Revert Finance's two earlier
    competitions (share of the pool taken by the top-ranked researchers).

"Findings submitted" is Cantina's own running count of every submission,
valid or not, so this measures crowding, not quality. No third-party
dependencies; Python 3.8+.

Licensed under Apache-2.0. Data in data/ is CC BY 4.0.
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
COMPETITIONS_CSV = os.path.join(HERE, "data", "cantina_competitions.csv")
TIERS_CSV = os.path.join(HERE, "data", "revert_payout_tiers.csv")
USD_CURRENCIES = {"USD", "USDC"}


def _date(text: str) -> _dt.date:
    return _dt.date.fromisoformat(text.strip())


def load_competitions(path: str = COMPETITIONS_CSV) -> List[Dict]:
    """Load the competitions table with typed fields."""
    rows: List[Dict] = []
    with open(path, newline="", encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            row = dict(raw)
            row["start"] = _date(raw["start"])
            row["end"] = _date(raw["end"])
            row["checked_on"] = _date(raw["checked_on"])
            row["prize_amount"] = float(raw["prize_amount"])
            row["findings_submitted"] = int(raw["findings_submitted"])
            rows.append(row)
    return rows


def contest_days(row: Dict) -> int:
    """Days the contest ran; for a live contest, days elapsed up to checked_on."""
    end = row["end"]
    if row["status"] == "live":
        end = min(end, row["checked_on"])
    return max((end - row["start"]).days, 1)


def per_day(row: Dict) -> float:
    return row["findings_submitted"] / contest_days(row)


def per_1k_usd(row: Dict) -> Optional[float]:
    """Findings per $1,000 of headline prize, or None for non-USD pots."""
    if row["prize_currency"] not in USD_CURRENCIES or row["prize_amount"] <= 0:
        return None
    return row["findings_submitted"] / (row["prize_amount"] / 1000.0)


def medians_by_year(
    rows: List[Dict],
    metric=per_day,
    max_usd_prize: Optional[float] = None,
) -> Dict[int, Dict]:
    """Median of a metric over completed contests, grouped by start year.

    max_usd_prize keeps only USD pots up to that size, to compare like with like.
    """
    groups: Dict[int, List[float]] = {}
    for row in rows:
        if row["status"] != "completed":
            continue
        if max_usd_prize is not None and (
            row["prize_currency"] not in USD_CURRENCIES or row["prize_amount"] > max_usd_prize
        ):
            continue
        value = metric(row)
        if value is None:
            continue
        groups.setdefault(row["start"].year, []).append(value)
    return {
        year: {"n": len(values), "median": statistics.median(values)}
        for year, values in sorted(groups.items())
    }


def load_tiers(path: str = TIERS_CSV) -> List[Dict]:
    tiers: List[Dict] = []
    with open(path, newline="", encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            tiers.append(
                {
                    "contest": raw["contest"],
                    "rank": int(raw["rank"]),
                    "researchers": int(raw["researchers"]),
                    "reward_each_usd": float(raw["reward_each_usd"]),
                    "high": int(raw["high"]),
                    "medium": int(raw["medium"]),
                }
            )
    return tiers


def top_share(tiers: List[Dict], contest: str, max_rank: int, pool_usd: float) -> Dict:
    """Researchers in ranks 1..max_rank of a contest and their share of the pool."""
    picked = [t for t in tiers if t["contest"] == contest and t["rank"] <= max_rank]
    researchers = sum(t["researchers"] for t in picked)
    paid = sum(t["researchers"] * t["reward_each_usd"] for t in picked)
    return {"researchers": researchers, "paid_usd": round(paid, 2), "share": paid / pool_usd}


def summary(rows: List[Dict], tiers: List[Dict]) -> Dict:
    return {
        "contests": len(rows),
        "per_day_by_year": medians_by_year(rows),
        "per_day_by_year_usd_pots_up_to_60k": medians_by_year(rows, max_usd_prize=60000),
        "per_1k_usd_by_year": medians_by_year(rows, metric=per_1k_usd),
        "live": [
            {"name": r["name"], "days_elapsed": contest_days(r), "per_day": round(per_day(r), 1),
             "findings_submitted": r["findings_submitted"], "checked_on": r["checked_on"].isoformat()}
            for r in rows if r["status"] == "live"
        ],
        "revert_lend_top_ranks_1_2": top_share(tiers, "Revert Finance", 2, 50000),
        "revert_stableswap_top_10": top_share(tiers, "Revert Finance - StableSwap Hooks", 10, 50000),
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--table", action="store_true", help="print one row per contest instead of the summary")
    args = parser.parse_args(argv)
    rows = load_competitions()
    if args.table:
        for r in rows:
            usd = per_1k_usd(r)
            print(f"{r['start']}  {r['name'][:34]:34}  {r['findings_submitted']:5d} findings  "
                  f"{contest_days(r):3d} d  {per_day(r):6.1f}/day  "
                  f"{'' if usd is None else f'{usd:6.2f} per $1k'}")
        return 0
    print(json.dumps(summary(rows, load_tiers()), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
