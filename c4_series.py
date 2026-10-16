#!/usr/bin/env python3
"""c4_series.py -- Code4rena audits by the half-year they started, 2021 to 2024.

Reads data/c4_contests.csv (one row per public Code4rena "-findings" repository on
GitHub, written by c4_crowding.py from a census of all 376 such repositories) and, for
audits only (mitigation reviews left out), reports per start half-year:

  * audits, split by era. In the "full" era a findings repo's data/ folder holds one
    record per submission. From 30 Apr 2024 most audits moved to a separate validation
    repo first and data/ holds only the submissions promoted from it ("validated" era):
    those audits are counted, but their submissions are NOT added to the series;
  * for full-era audits: all submissions (QA, gas and analysis reports count one each),
    High+Medium submissions as labelled by the submitter, the median per audit, the
    median number of distinct submitters, and the signal rate: the published report's
    unique High+Medium findings divided by the High+Medium submissions.

Code4rena's public findings repositories stop in December 2024 (later ones are not
public), so this series ends there; Code4rena wound down in May 2026. No third-party
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
import statistics
from typing import Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
C4_CSV = os.path.join(HERE, "data", "c4_contests.csv")


def _int(value: str) -> Optional[int]:
    value = (value or "").strip()
    return int(value) if value.lstrip("-").isdigit() else None


def load(path: str = C4_CSV) -> List[Dict]:
    """Every row of the census, typed. Undated rows keep start None."""
    rows: List[Dict] = []
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            start = row["start"].strip()
            rows.append({
                "repo": row["repo"],
                "kind": row["kind"],
                "era": row["era"],
                "start": _dt.date.fromisoformat(start[:10]) if start else None,
                "submissions": _int(row["submissions"]) or 0,
                "high_subs": _int(row["high_subs"]) or 0,
                "medium_subs": _int(row["medium_subs"]) or 0,
                "hm_subs": _int(row["hm_subs"]) or 0,
                "unique_high": _int(row["unique_high"]),
                "unique_medium": _int(row["unique_medium"]),
                "submitters": _int(row["submitters"]),
                "est_total_submissions": _int(row["est_total_submissions"]),
            })
    return rows


def audits(rows: List[Dict], era: Optional[str] = None) -> List[Dict]:
    """Dated audits (no mitigation reviews) with at least one submission, optionally of one era."""
    return [r for r in rows if r["kind"] == "audit" and r["start"] is not None and r["submissions"] > 0
            and (era is None or r["era"] == era)]


def signal_rate(row: Dict) -> Optional[float]:
    """Unique High+Medium in the report / High+Medium submissions; full era only."""
    if row["era"] != "full" or row["unique_high"] is None or row["unique_medium"] is None:
        return None
    if row["hm_subs"] <= 0:
        return None
    return (row["unique_high"] + row["unique_medium"]) / row["hm_subs"]


def _median(values: List) -> Optional[float]:
    vals = [v for v in values if v is not None]
    return round(statistics.median(vals), 3) if vals else None


def half(day: _dt.date) -> str:
    return f"{day.year}H{1 if day.month <= 6 else 2}"


def table(rows: List[Dict]) -> List[Dict]:
    """One cell per start half-year: audits of both eras, submission figures from full-era audits."""
    groups: Dict[str, List[Dict]] = {}
    for row in audits(rows):
        groups.setdefault(half(row["start"]), []).append(row)
    out = []
    for key in sorted(groups):
        group = groups[key]
        full = [r for r in group if r["era"] == "full"]
        rated = [r for r in full if signal_rate(r) is not None]
        rated_hm = sum(r["hm_subs"] for r in rated)
        out.append({
            "period": key,
            "audits": len(group),
            "full": len(full),
            "validated": len(group) - len(full),
            "submissions": sum(r["submissions"] for r in full),
            "hm_subs": sum(r["hm_subs"] for r in full),
            "median_hm_subs": _median([r["hm_subs"] for r in full]),
            "median_submitters": _median([r["submitters"] for r in full]),
            "median_signal_rate": _median([signal_rate(r) for r in full]),
            "signal_n": len(rated),
            "pooled_signal_rate": round(sum(r["unique_high"] + r["unique_medium"] for r in rated) / rated_hm, 4)
            if rated_hm else None,
        })
    return out


def year_totals(rows: List[Dict], year: int) -> Dict:
    """Audits that started in `year` (both eras): the figures to set beside Code4rena's own year review."""
    group = [r for r in audits(rows) if r["start"].year == year]
    return {
        "audits": len(group),
        "submissions": sum(r["submissions"] for r in group),
        "hm_subs": sum(r["hm_subs"] for r in group),
        "high_subs": sum(r["high_subs"] for r in group),
        "medium_subs": sum(r["medium_subs"] for r in group),
    }


def summary(path: str = C4_CSV) -> Dict:
    rows = load(path)
    full = audits(rows, "full")
    validated = audits(rows, "validated")
    return {
        "rows": len(rows),
        "mitigation_rows": sum(1 for r in rows if r["kind"] == "mitigation"),
        "undated_rows": sum(1 for r in rows if r["start"] is None),
        "full_audits": len(full),
        "full_submissions": sum(r["submissions"] for r in full),
        "full_first_start": min(r["start"] for r in full).isoformat() if full else None,
        "validated_audits": len(validated),
        "validated_first_start": min(r["start"] for r in validated).isoformat() if validated else None,
        "validated_promoted": sum(r["submissions"] for r in validated),
        "validated_est_total": sum(r["est_total_submissions"] or 0 for r in validated),
        "last_start": max(r["start"] for r in audits(rows)).isoformat() if audits(rows) else None,
        "half_yearly": table(rows),
        "year_2023": year_totals(rows, 2023),
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--c4", default=C4_CSV)
    parser.add_argument("--table", action="store_true", help="print the half-year table as text")
    args = parser.parse_args(argv)
    result = summary(args.c4)
    if args.table:
        print(f"{'period':8} {'audits':>7} {'full':>5} {'valid.':>7} {'all subs':>9} {'H+M subs':>9} "
              f"{'med H+M':>8} {'med subm.':>9} {'signal':>7} {'pooled':>7}")
        for c in result["half_yearly"]:
            print(f"{c['period']:8} {c['audits']:>7} {c['full']:>5} {c['validated']:>7} {c['submissions']:>9,} "
                  f"{c['hm_subs']:>9,} {c['median_hm_subs'] or 0:>8g} {c['median_submitters'] or 0:>9g} "
                  f"{c['median_signal_rate'] or 0:>7.3f} {c['pooled_signal_rate'] or 0:>7.4f}")
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
