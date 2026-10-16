#!/usr/bin/env python3
"""immunefi_series.py -- Immunefi audit competitions by the half-year they started.

Reads data/immunefi_contests.csv (one row per competition page on immunefi.com that
gives a Start Date, written by fetch_immunefi.py on 15 Oct 2026) and reports per start
half-year:

  * competitions of every kind, and "audit-type" ones (Audit Comp / Boost, IOP and
    Mitigation Audit; Attackathons and Bug Bounty Comps are left out of that count);
  * the USD pools the pages state (some are paid in other tokens; see `token`), in total
    and as the median audit-type pool;
  * the size of each audit-type competition's results leaderboard.

The leaderboard is NOT a like-for-like series. Until mid-2025 the results page lists only
whitehats with earnings (bare-number ranks); from mid-2025 a new layout ("#N" ranks)
also lists entries with $0 earnings. `rank_method` records which layout a page used.
No third-party dependencies.

Licensed under Apache-2.0. Data it reads is CC BY 4.0.
Made with AI agents working for MV2 of Munim, Inc.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
from typing import Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
IMMUNEFI_CSV = os.path.join(HERE, "data", "immunefi_contests.csv")
AUDIT_KINDS = ("audit_comp", "iop", "mitigation_audit")


def _num(value: str) -> Optional[float]:
    value = (value or "").strip()
    try:
        return float(value) if value else None
    except ValueError:
        return None


def load(path: str = IMMUNEFI_CSV) -> List[Dict]:
    rows: List[Dict] = []
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            ranked = _num(row["ranked_whitehats"])
            rows.append({
                "slug": row["slug"],
                "kind": row["kind"],
                "start": row["start"].strip(),
                "half": row["start_half"].strip(),
                "pool_usd": _num(row["pool_usd"]),
                "leaderboard": int(ranked) if ranked is not None else None,
                "rank_method": row["rank_method"].strip() or None,
            })
    return rows


def _median(values: List) -> Optional[float]:
    vals = [v for v in values if v is not None]
    return statistics.median(vals) if vals else None


def table(rows: List[Dict]) -> List[Dict]:
    groups: Dict[str, List[Dict]] = {}
    for row in rows:
        if row["half"]:
            groups.setdefault(row["half"], []).append(row)
    out = []
    for key in sorted(groups):
        group = groups[key]
        audit = [r for r in group if r["kind"] in AUDIT_KINDS]
        boards = [r["leaderboard"] for r in audit if r["leaderboard"]]
        out.append({
            "period": key,
            "competitions": len(group),
            "audit_type": len(audit),
            "pool_usd": sum(r["pool_usd"] or 0 for r in group),
            "audit_type_pool_usd": sum(r["pool_usd"] or 0 for r in audit),
            "median_audit_type_pool_usd": _median([r["pool_usd"] for r in audit]),
            "leaderboards_read": len(boards),
            "median_leaderboard": _median(boards),
        })
    return out


def summary(path: str = IMMUNEFI_CSV) -> Dict:
    rows = load(path)
    methods: Dict[str, int] = {}
    for r in rows:
        methods[r["rank_method"] or "none"] = methods.get(r["rank_method"] or "none", 0) + 1
    hash_starts = [r["start"] for r in rows if r["rank_method"] == "hash"]
    bare_starts = [r["start"] for r in rows if r["rank_method"] == "bare"]
    return {
        "competitions": len(rows),
        "audit_type": sum(1 for r in rows if r["kind"] in AUDIT_KINDS),
        "first_start": min(r["start"] for r in rows) if rows else None,
        "last_start": max(r["start"] for r in rows) if rows else None,
        "rank_methods": dict(sorted(methods.items())),
        "first_hash_start": min(hash_starts) if hash_starts else None,
        "last_bare_start": max(bare_starts) if bare_starts else None,
        "half_yearly": table(rows),
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--immunefi", default=IMMUNEFI_CSV)
    parser.add_argument("--table", action="store_true", help="print the half-year table as text")
    args = parser.parse_args(argv)
    result = summary(args.immunefi)
    if args.table:
        print(f"{'period':8} {'comps':>6} {'audit':>6} {'pools $':>11} {'audit $':>11} {'med audit $':>12} "
              f"{'boards':>7} {'med board':>10}")
        for c in result["half_yearly"]:
            print(f"{c['period']:8} {c['competitions']:>6} {c['audit_type']:>6} {c['pool_usd']:>11,.0f} "
                  f"{c['audit_type_pool_usd']:>11,.0f} {c['median_audit_type_pool_usd'] or 0:>12,.0f} "
                  f"{c['leaderboards_read']:>7} {c['median_leaderboard'] or 0:>10g}")
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
