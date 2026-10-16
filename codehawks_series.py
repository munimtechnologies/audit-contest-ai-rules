#!/usr/bin/env python3
"""codehawks_series.py -- CodeHawks audits and First Flights by the half-year they started.

Input: data/codehawks_contests.csv, written by MV2's CodeHawks census (codehawks-census-v2,
run 2026-10-16) from the codehawks.cyfrin.io contest pages and sitemap. One row per page:
  slug, kind (audit | first_flight), access (Public | Private | Invite-only; audits only),
  title, start, end, days, year, half, prize_amount, prize_unit, nsloc, submissions,
  submissions_source, sitemap_submissions, high, medium, low, unique_valid, unique_hm,
  signal_rate, hm_signal_rate, submissions_per_day, submissions_per_ksloc.

The sitemap also lists self-paced practice copies of two First Flights (Thunder Loan and
Beatland Festival). Their slugs end in a 25-character id ("-c" and 24 letters or digits).
They are not contests, so they are counted apart and left out of every series.

Reported per start half-year:
  audits  -- all audits; for public ones with a submission count: submissions, the median
             per audit, unique valid findings (High + Medium + Low) and the pooled signal
             rate; for public audits with a USDC pot, prize money per submission, pooled
             and for the median audit. OP and ETH pots are left out, never converted.
  flights -- First Flights (they award experience points, not money): submissions, the
             median per flight, unique valid findings and the pooled signal rate.

Standard library only. Licensed under Apache-2.0. Data CC BY 4.0.
Made with AI agents working for MV2 of Munim, Inc.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
from typing import Dict, Iterable, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
CONTESTS_CSV = os.path.join(HERE, "data", "codehawks_contests.csv")
KINDS = ("audit", "first_flight")
PRACTICE_RE = re.compile(r"-c[a-z0-9]{24}$")


def half(iso_date: str) -> Optional[str]:
    """'2025-08-14' -> '2025H2'; '' -> None."""
    if not iso_date:
        return None
    return f"{iso_date[:4]}H{1 if int(iso_date[5:7]) <= 6 else 2}"


def is_practice_copy(slug: str) -> bool:
    """'thunder-loan-cm7owpv0f0000fv3uq12azah5' -> True; '2023-11-Thunder-Loan' -> False."""
    return bool(PRACTICE_RE.search(slug))


def _int(text: str) -> Optional[int]:
    text = (text or "").strip()
    return int(float(text)) if text else None


def load(path: str = CONTESTS_CSV) -> List[Dict]:
    """Rows of the census CSV with typed fields."""
    rows: List[Dict] = []
    with open(path, encoding="utf-8", newline="") as fh:
        for raw in csv.DictReader(fh):
            if raw["kind"] not in KINDS:
                raise ValueError(f"unknown kind {raw['kind']!r} for {raw['slug']!r}")
            prize = (raw["prize_amount"] or "").strip()
            rows.append({
                "slug": raw["slug"],
                "kind": raw["kind"],
                "access": raw["access"],
                "start": raw["start"],
                "start_half": half(raw["start"]),
                "prize_amount": float(prize) if prize else None,
                "prize_unit": raw["prize_unit"],
                "submissions": _int(raw["submissions"]),
                "unique_valid": _int(raw["unique_valid"]),
                "practice_copy": raw["kind"] == "first_flight" and is_practice_copy(raw["slug"]),
            })
    return rows


def _median(values: List[float]) -> Optional[float]:
    return round(statistics.median(values), 2) if values else None


def _ratio(num: float, den: float, places: int) -> Optional[float]:
    return round(num / den, places) if den else None


def audit_block(rows: List[Dict]) -> Dict:
    """Counts, signal rate and USDC prize money per submission for one group of audits."""
    public = [r for r in rows if r["access"] == "Public" and r["submissions"]]
    usdc = [r for r in public if r["prize_unit"] == "USDC" and r["prize_amount"]]
    subs = sum(r["submissions"] for r in public)
    valid = sum(r["unique_valid"] or 0 for r in public)
    prize = sum(r["prize_amount"] for r in usdc)
    return {
        "audits": len(rows),
        "public": len(public),
        "submissions": subs,
        "median_submissions": _median([r["submissions"] for r in public]),
        "unique_valid": valid,
        "pooled_signal_rate": _ratio(valid, subs, 4),
        "usdc_audits": len(usdc),
        "usdc_prize": prize,
        "usdc_per_submission": _ratio(prize, sum(r["submissions"] for r in usdc), 2),
        "median_usdc_per_submission": _median([r["prize_amount"] / r["submissions"] for r in usdc]),
    }


def flight_block(rows: List[Dict]) -> Dict:
    """Counts and signal rate for one group of First Flights."""
    have = [r for r in rows if r["submissions"]]
    subs = sum(r["submissions"] for r in have)
    valid = sum(r["unique_valid"] or 0 for r in have)
    return {
        "flights": len(rows),
        "submissions": subs,
        "median_submissions": _median([r["submissions"] for r in have]),
        "unique_valid": valid,
        "pooled_signal_rate": _ratio(valid, subs, 4),
    }


def _by_half(rows: List[Dict], block) -> Dict[str, Dict]:
    halves = sorted({r["start_half"] for r in rows if r["start_half"]})
    return {h: block([r for r in rows if r["start_half"] == h]) for h in halves}


def summary(path: str = CONTESTS_CSV) -> Dict:
    rows = load(path)
    audits = [r for r in rows if r["kind"] == "audit"]
    flights = [r for r in rows if r["kind"] == "first_flight" and not r["practice_copy"]]
    practice = [r for r in rows if r["practice_copy"]]
    by_year: Dict[str, int] = {}
    for r in practice:
        key = r["start"][:4] if r["start"] else "none"
        by_year[key] = by_year.get(key, 0) + 1
    return {
        "source": "codehawks.cyfrin.io contest pages and sitemap, census run 2026-10-16",
        "audits": audit_block(audits),
        "audits_by_start_half": _by_half(audits, audit_block),
        "audit_starts": sorted(r["start"] for r in audits if r["start"]),
        "flights": flight_block(flights),
        "flights_by_start_half": _by_half(flights, flight_block),
        "last_flight_start": max((r["start"] for r in flights if r["start"]), default=None),
        "practice_copies": {
            "rows": len(practice),
            "submissions": sum(r["submissions"] or 0 for r in practice),
            "by_start_year": dict(sorted(by_year.items())),
        },
    }


def _fmt(value, money: bool = False) -> str:
    if value is None:
        return "-"
    if money:
        return f"${value:,.2f}"
    return f"{value:,}" if isinstance(value, int) else f"{value:g}"


def tables(s: Dict) -> str:
    lines = ["| Started in | Audits | Public | Submissions | Median per audit | Signal rate | USDC audits | USDC $ per submission | Median audit $ per submission |",
             "|---|---|---|---|---|---|---|---|---|"]
    for h, b in list(s["audits_by_start_half"].items()) + [("all", s["audits"])]:
        lines.append(f"| {h} | {b['audits']} | {b['public']} | {_fmt(b['submissions'])} | "
                     f"{_fmt(b['median_submissions'])} | {_fmt(b['pooled_signal_rate'])} | {b['usdc_audits']} | "
                     f"{_fmt(b['usdc_per_submission'], True)} | {_fmt(b['median_usdc_per_submission'], True)} |")
    lines += ["", "| Started in | First Flights | Submissions | Median per flight | Signal rate |", "|---|---|---|---|---|"]
    for h, b in list(s["flights_by_start_half"].items()) + [("all", s["flights"])]:
        lines.append(f"| {h} | {b['flights']} | {_fmt(b['submissions'])} | {_fmt(b['median_submissions'])} | "
                     f"{_fmt(b['pooled_signal_rate'])} |")
    return "\n".join(lines)


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--in", dest="path", default=CONTESTS_CSV, help="CodeHawks census CSV")
    parser.add_argument("--table", action="store_true", help="print Markdown tables instead of JSON")
    parser.add_argument("--out", help="also write the JSON summary to this file")
    args = parser.parse_args(list(argv) if argv is not None else None)
    s = summary(args.path)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(s, fh, indent=2)
    print(tables(s) if args.table else json.dumps(s, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
