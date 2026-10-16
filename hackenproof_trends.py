#!/usr/bin/env python3
"""hackenproof_trends.py -- HackenProof audit programs by the half-year they started.

Input: data/hackenproof_programs_fetched.csv, written by a scripted fetch of every program
page on https://hackenproof.com/audit-programs (2026-10-15 21:51 UTC). One row per program:
  slug, name, kind (contest | dualdefense), status (finished | live), start_date, end_date,
  bounty_min_usd, up_to_usd, paid_usd (an integer, or "private"), submissions, hackers,
  listing_page, ai_rule (the program page's sentences that mention AI, "" if none), missing.

For each start half-year it reports how many programs ran, how many carry an AI-report
rule, the submissions they drew, and, over settled programs only (finished, paid figure
public), the headline maximum and the amount paid per submission.

AI rules are recognised by the two sentences HackenProof uses:
  "poc"              -- "AI-generated reports without runable PoC are not accepted ..."
  "human_validation" -- "Automated submissions or AI-generated reports must include human validation."
Other text that mentions AI (a project describing itself) is not a rule.

Standard library only. Licensed under Apache-2.0. Data CC BY 4.0.
Made with AI agents working for MV2 of Munim, Inc.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from typing import Dict, Iterable, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
FETCHED_CSV = os.path.join(HERE, "data", "hackenproof_programs_fetched.csv")
KINDS = ("contest", "dualdefense")
STATUSES = ("finished", "live")
RULES = {
    "poc": "without runable PoC are not accepted",
    "human_validation": "must include human validation",
}


def half(iso_date: str) -> str:
    """'2025-08-14' -> '2025H2'."""
    return f"{iso_date[:4]}H{1 if int(iso_date[5:7]) <= 6 else 2}"


def rule_kind(text: str) -> str:
    """Which AI-report rule a page's AI text states ("" if none)."""
    for kind, phrase in RULES.items():
        if phrase in text:
            return kind
    return ""


def load(path: str = FETCHED_CSV) -> List[Dict]:
    """Rows of the fetched CSV with typed fields."""
    rows: List[Dict] = []
    with open(path, encoding="utf-8", newline="") as fh:
        for raw in csv.DictReader(fh):
            if raw["kind"] not in KINDS:
                raise ValueError(f"unknown kind {raw['kind']!r} for {raw['name']!r}")
            if raw["status"] not in STATUSES:
                raise ValueError(f"unknown status {raw['status']!r} for {raw['name']!r}")
            paid_raw = raw["paid_usd"].strip().lower()
            rows.append({
                "slug": raw["slug"],
                "name": raw["name"],
                "kind": raw["kind"],
                "status": raw["status"],
                "start_date": raw["start_date"],
                "start_half": half(raw["start_date"]),
                "end_date": raw["end_date"],
                "up_to_usd": int(raw["up_to_usd"]),
                "paid_usd": None if paid_raw == "private" else int(paid_raw),
                "submissions": int(raw["submissions"]),
                "ai_rule": rule_kind(raw["ai_rule"]),
            })
    return rows


def settled(rows: Iterable[Dict]) -> List[Dict]:
    """Finished programs whose paid figure is public."""
    return [r for r in rows if r["status"] == "finished" and r["paid_usd"] is not None]


def per_sub(amount: int, subs: int) -> Optional[float]:
    return round(amount / subs, 2) if subs else None


def block(rows: List[Dict]) -> Dict:
    """Counts, AI rules and money per submission for one group of programs."""
    s = settled(rows)
    up_to = sum(r["up_to_usd"] for r in s)
    paid = sum(r["paid_usd"] for r in s)
    subs = sum(r["submissions"] for r in s)
    return {
        "programs": len(rows),
        "contests": sum(1 for r in rows if r["kind"] == "contest"),
        "with_ai_rule": sum(1 for r in rows if r["ai_rule"]),
        "submissions": sum(r["submissions"] for r in rows),
        "settled": len(s),
        "settled_submissions": subs,
        "up_to_usd_settled": up_to,
        "paid_usd": paid,
        "max_per_submission": per_sub(up_to, subs),
        "paid_per_submission": per_sub(paid, subs),
    }


def summary(path: str = FETCHED_CSV) -> Dict:
    rows = load(path)
    halves = sorted({r["start_half"] for r in rows})
    ruled = sorted((r for r in rows if r["ai_rule"]), key=lambda r: r["start_date"])
    return {
        "source": "hackenproof.com/audit-programs program pages, fetched 2026-10-15T21:51Z",
        "all": block(rows),
        "by_start_half": {h: block([r for r in rows if r["start_half"] == h]) for h in halves},
        "ai_rules": {kind: sum(1 for r in rows if r["ai_rule"] == kind) for kind in RULES},
        "first_ai_rule": {"name": ruled[0]["name"], "start_date": ruled[0]["start_date"]} if ruled else None,
    }


def fmt_usd(value: Optional[float], cents: bool = False) -> str:
    if value is None:
        return "-"
    return f"${value:,.2f}" if cents else f"${value:,.0f}"


def table(s: Dict) -> str:
    lines = ["| Started in | Programs | With an AI-report rule | Submissions | Settled | Max reward (settled) | Paid | Max per submission | Paid per submission |",
             "|---|---|---|---|---|---|---|---|---|"]

    def row(label: str, b: Dict) -> str:
        return (f"| {label} | {b['programs']} | {b['with_ai_rule']} | {b['submissions']:,} | {b['settled']} | "
                f"{fmt_usd(b['up_to_usd_settled'])} | {fmt_usd(b['paid_usd'])} | "
                f"{fmt_usd(b['max_per_submission'], True)} | {fmt_usd(b['paid_per_submission'], True)} |")

    for h, b in s["by_start_half"].items():
        lines.append(row(h, b))
    lines.append(row("all", s["all"]))
    return "\n".join(lines)


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--in", dest="path", default=FETCHED_CSV, help="fetched programs CSV")
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
