#!/usr/bin/env python3
"""hackenproof_payouts.py -- what HackenProof audit programs promised, and what they paid.

HackenProof's public listing (https://hackenproof.com/audit-programs, 11 pages) shows,
for every audit contest and DualDefense audit it has run, an "Up to: $X" maximum reward
and a "Paid: $Y" figure (the program page calls it "Total rewards"). No other contest
platform publishes paid-out totals next to the headline pot, so this is the one place
where "promised" and "paid" can be compared program by program.

Input: data/hackenproof_programs.csv, one row per program:
  name, kind (contest | dualdefense), status (finished | live), end_date (ISO),
  up_to_usd, paid_usd (an integer, or "private" where the site shows "Paid: Private"),
  listing_page (which page of the listing the row was read from).

A program is "settled" when it is finished and its paid figure is public. Shares are
paid / up_to over settled programs only; live programs and private payouts are counted
but excluded from the money totals. "paid_full" means paid >= 99% of the maximum.

Standard library only. Licensed under Apache-2.0. Data CC BY 4.0.
Made with AI agents working for MV2 of Munim, Inc.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
from typing import Dict, Iterable, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
PROGRAMS_CSV = os.path.join(HERE, "data", "hackenproof_programs.csv")
FULL_PAY = 0.99
KINDS = ("contest", "dualdefense")
STATUSES = ("finished", "live")


def load(path: str = PROGRAMS_CSV) -> List[Dict]:
    """Rows of the programs CSV with typed fields and a paid_ratio (None if private)."""
    rows: List[Dict] = []
    with open(path, encoding="utf-8", newline="") as fh:
        for raw in csv.DictReader(fh):
            paid_raw = raw["paid_usd"].strip().lower()
            if raw["kind"] not in KINDS:
                raise ValueError(f"unknown kind {raw['kind']!r} for {raw['name']!r}")
            if raw["status"] not in STATUSES:
                raise ValueError(f"unknown status {raw['status']!r} for {raw['name']!r}")
            row = {
                "name": raw["name"],
                "kind": raw["kind"],
                "status": raw["status"],
                "end_date": raw["end_date"],
                "end_year": int(raw["end_date"][:4]),
                "up_to_usd": int(raw["up_to_usd"]),
                "paid_usd": None if paid_raw == "private" else int(paid_raw),
                "listing_page": int(raw["listing_page"]),
            }
            row["paid_ratio"] = (None if row["paid_usd"] is None
                                 else round(row["paid_usd"] / row["up_to_usd"], 4))
            rows.append(row)
    return rows


def settled(rows: Iterable[Dict]) -> List[Dict]:
    """Finished programs whose paid figure is public."""
    return [r for r in rows if r["status"] == "finished" and r["paid_usd"] is not None]


def block(rows: List[Dict]) -> Dict:
    """Counts and money totals for one group of programs."""
    s = settled(rows)
    up_to = sum(r["up_to_usd"] for r in s)
    paid = sum(r["paid_usd"] for r in s)
    return {
        "programs": len(rows),
        "live": sum(1 for r in rows if r["status"] == "live"),
        "paid_private": sum(1 for r in rows if r["status"] == "finished" and r["paid_usd"] is None),
        "settled": len(s),
        "up_to_usd_all": sum(r["up_to_usd"] for r in rows),
        "up_to_usd_settled": up_to,
        "paid_usd": paid,
        "paid_share": round(paid / up_to, 4) if up_to else None,
        "paid_nothing": sum(1 for r in s if r["paid_usd"] == 0),
        "paid_full": sum(1 for r in s if r["paid_usd"] >= FULL_PAY * r["up_to_usd"]),
        "median_up_to_usd": statistics.median([r["up_to_usd"] for r in s]) if s else None,
        "median_paid_ratio": round(statistics.median([r["paid_ratio"] for r in s]), 4) if s else None,
    }


def summary(path: str = PROGRAMS_CSV) -> Dict:
    rows = load(path)
    kinds = [k for k in KINDS if any(r["kind"] == k for r in rows)]
    years = sorted({r["end_year"] for r in rows})
    by_year: Dict[str, Dict[str, Dict]] = {}
    for kind in kinds:
        by_year[kind] = {}
        for year in years:
            group = [r for r in rows if r["kind"] == kind and r["end_year"] == year]
            if group:
                by_year[kind][str(year)] = block(group)
    return {
        "source": "hackenproof.com/audit-programs listing, read 2026-10-15",
        "all": block(rows),
        "by_kind": {kind: block([r for r in rows if r["kind"] == kind]) for kind in kinds},
        "by_kind_and_end_year": by_year,
    }


def fmt_usd(value: Optional[float]) -> str:
    return "-" if value is None else f"${value:,.0f}"


def fmt_pct(value: Optional[float]) -> str:
    return "-" if value is None else f"{100 * value:.1f}%"


def table(s: Dict) -> str:
    lines = ["| Group | Programs | Settled | Max reward (settled) | Paid | Paid share | Paid nothing | Paid in full | Median max |",
             "|---|---|---|---|---|---|---|---|---|"]

    def row(label: str, b: Dict) -> str:
        return (f"| {label} | {b['programs']} | {b['settled']} | {fmt_usd(b['up_to_usd_settled'])} | "
                f"{fmt_usd(b['paid_usd'])} | {fmt_pct(b['paid_share'])} | {b['paid_nothing']} | "
                f"{b['paid_full']} | {fmt_usd(b['median_up_to_usd'])} |")

    for kind, b in s["by_kind"].items():
        lines.append(row(kind, b))
        for year, yb in s["by_kind_and_end_year"][kind].items():
            lines.append(row(f"  {kind} ended {year}", yb))
    lines.append(row("all", s["all"]))
    return "\n".join(lines)


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--in", dest="path", default=PROGRAMS_CSV, help="programs CSV")
    parser.add_argument("--table", action="store_true", help="print a Markdown table instead of JSON")
    parser.add_argument("--out", help="also write the JSON summary to this file")
    args = parser.parse_args(list(argv) if argv is not None else None)
    s = summary(args.path)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(s, fh, indent=2)
    print(table(s) if args.table else json.dumps(s, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
