#!/usr/bin/env python3
"""c4_crowding.py -- how crowded were Code4rena audits, and how much of what was sent was new?

Reads the JSONL written by fetch_c4.py (one record of contest-level facts per public
"-findings" repository) and reports, by the year and half-year an audit started:

  * audits, High+Medium submissions and all submissions (QA, gas and analysis reports
    count one each), with medians per audit, per contest day and per $1,000 of pot;
  * the "signal rate": the report's unique High+Medium findings divided by the
    High+Medium submissions (how much of what was sent was a distinct valid bug);
  * a cross-check of the 2023 totals against Code4rena's own year-in-review figures.

Two eras. Until late 2024 a findings repo's data/ folder holds every submission ("full").
From late 2024 submissions went to a separate validation repo first, and data/ holds only
the ones promoted from it ("validated"): those audits are reported apart, with the total
estimated from the highest validation issue number. Mitigation reviews are kept as rows but
left out of the audit series. Risk labels are as submitted, not as judged.

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

# Code4rena, "Welcome to 2024 at Code4rena" (Medium, January 2024):
# https://medium.com/code4rena/welcome-to-2024-at-code4rena-f0929a6ae3a8
C4_2023 = {"audits": 114, "submissions": 31512, "assessed_high": 3005, "assessed_medium": 4003}

CSV_FIELDS = (
    "repo", "slug", "contest", "title", "sponsor", "kind", "era", "start", "end", "days", "pot_usd",
    "nsloc", "submissions", "high_subs", "medium_subs", "hm_subs", "qa_subs", "gas_subs",
    "analysis_subs", "other_subs", "max_issue_id", "max_original_issue_id", "est_total_submissions",
    "submitters", "wardens_in_report", "unique_high", "unique_medium", "signal_rate", "hm_per_day",
    "hm_per_1k_usd",
)


def load(path: str) -> List[Dict]:
    """Last good record per repo wins (fetch_c4.py appends). Cut-off lines are skipped."""
    by_repo: Dict[str, Dict] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            repo = rec.get("repo")
            if rec.get("error") and repo in by_repo and not by_repo[repo].get("error"):
                continue
            by_repo[repo] = rec
    return [by_repo[k] for k in sorted(by_repo)]


def _date(value) -> Optional[_dt.date]:
    if not isinstance(value, str) or not value:
        return None
    try:
        return _dt.date.fromisoformat(value[:10])
    except ValueError:
        return None


def dates(rec: Dict):
    """(start, end, source): the audit README first, then the report's sentence."""
    readme = rec.get("readme") or {}
    report = rec.get("report") or {}
    start, end = _date(readme.get("start")), _date(readme.get("end"))
    if start and end and end >= start:
        return start, end, "readme"
    start, end = _date(report.get("start")), _date(report.get("end"))
    if start and end and end >= start:
        return start, end, "report"
    return None, None, None


def kind_of(repo: str) -> str:
    return "mitigation" if "mitigation" in repo.lower() else "audit"


def enrich(rec: Dict) -> Optional[Dict]:
    """Typed row for a repo that was read without error, else None."""
    if rec.get("error") or not isinstance(rec.get("risk"), dict):
        return None
    risk = rec["risk"]
    report = rec.get("report") or {}
    readme = rec.get("readme") or {}
    start, end, source = dates(rec)
    days = None
    if start and end:
        days = max((end - start).days, 1)
    hm = int(risk.get("high", 0)) + int(risk.get("medium", 0))
    submissions = int(rec.get("json_records") or 0)
    era = "validated" if int(rec.get("with_original_id") or 0) > 0 else "full"
    est_total = rec.get("max_original_issue_id") if era == "validated" else submissions
    uh, um = report.get("unique_high"), report.get("unique_medium")
    unique_hm = uh + um if isinstance(uh, int) and isinstance(um, int) else None
    pot = readme.get("pot_usd")
    pot = float(pot) if isinstance(pot, (int, float)) and not isinstance(pot, bool) and pot > 0 else None
    return {
        "repo": rec["repo"],
        "slug": rec.get("slug"),
        "contest": report.get("contest"),
        "title": report.get("title"),
        "sponsor": report.get("sponsor"),
        "kind": kind_of(rec["repo"]),
        "era": era,
        "start": start,
        "end": end,
        "date_source": source,
        "days": days,
        "pot_usd": pot,
        "nsloc": readme.get("nsloc"),
        "submissions": submissions,
        "high_subs": int(risk.get("high", 0)),
        "medium_subs": int(risk.get("medium", 0)),
        "hm_subs": hm,
        "qa_subs": int(risk.get("qa", 0)),
        "gas_subs": int(risk.get("gas", 0)),
        "analysis_subs": int(risk.get("analysis", 0)),
        "other_subs": int(risk.get("other", 0)),
        "max_issue_id": rec.get("max_issue_id"),
        "max_original_issue_id": rec.get("max_original_issue_id"),
        "est_total_submissions": est_total,
        "submitters": rec.get("submitters"),
        "wardens_in_report": report.get("wardens"),
        "unique_high": uh,
        "unique_medium": um,
        "unique_hm": unique_hm,
        "signal_rate": (unique_hm / hm) if (unique_hm is not None and hm > 0 and era == "full") else None,
        "hm_per_day": (hm / days) if (days and era == "full") else None,
        "hm_per_1k_usd": (hm / (pot / 1000.0)) if (pot and era == "full") else None,
    }


def rows_of(records: List[Dict]) -> List[Dict]:
    rows = [r for r in (enrich(rec) for rec in records) if r is not None]
    return sorted(rows, key=lambda r: (r["start"] or _dt.date.max, r["repo"]))


def audits(rows: List[Dict], era: Optional[str] = "full") -> List[Dict]:
    """Dated audits (no mitigation reviews), optionally of one era, with at least one submission."""
    return [r for r in rows if r["kind"] == "audit" and r["start"] is not None and r["submissions"] > 0
            and (era is None or r["era"] == era)]


def _median(values: List) -> Optional[float]:
    vals = [v for v in values if v is not None]
    return round(statistics.median(vals), 3) if vals else None


def _block(group: List[Dict]) -> Dict:
    return {
        "audits": len(group),
        "submissions": sum(r["submissions"] for r in group),
        "hm_subs": sum(r["hm_subs"] for r in group),
        "high_subs": sum(r["high_subs"] for r in group),
        "medium_subs": sum(r["medium_subs"] for r in group),
        "median_submissions": _median([r["submissions"] for r in group]),
        "median_hm_subs": _median([r["hm_subs"] for r in group]),
        "median_hm_per_day": _median([r["hm_per_day"] for r in group]),
        "median_hm_per_1k_usd": _median([r["hm_per_1k_usd"] for r in group]),
        "median_signal_rate": _median([r["signal_rate"] for r in group]),
        "signal_n": sum(1 for r in group if r["signal_rate"] is not None),
        "pooled_signal_rate": _pooled_signal(group),
        "median_submitters": _median([r["submitters"] for r in group]),
        "median_days": _median([r["days"] for r in group]),
        "median_pot_usd": _median([r["pot_usd"] for r in group]),
    }


def _pooled_signal(group: List[Dict]) -> Optional[float]:
    have = [r for r in group if r["signal_rate"] is not None]
    hm = sum(r["hm_subs"] for r in have)
    return round(sum(r["unique_hm"] for r in have) / hm, 4) if hm else None


def period(day: _dt.date, unit: str) -> str:
    if unit == "year":
        return str(day.year)
    if unit == "half":
        return f"{day.year}H{1 if day.month <= 6 else 2}"
    return f"{day.year}Q{(day.month - 1) // 3 + 1}"


def series(rows: List[Dict], unit: str) -> Dict[str, Dict]:
    groups: Dict[str, List[Dict]] = {}
    for row in rows:
        groups.setdefault(period(row["start"], unit), []).append(row)
    return {key: _block(grp) for key, grp in sorted(groups.items())}


def check_2023(rows: List[Dict]) -> Dict:
    """Our 2023 totals (audits that started in 2023, every era) next to C4's published ones."""
    yr = [r for r in audits(rows, era=None) if r["start"].year == 2023]
    ours = {
        "audits": len(yr),
        "submissions": sum(r["submissions"] for r in yr),
        "high_subs_as_labelled": sum(r["high_subs"] for r in yr),
        "medium_subs_as_labelled": sum(r["medium_subs"] for r in yr),
    }
    ratio = ours["submissions"] / C4_2023["submissions"] if C4_2023["submissions"] else None
    return {"ours": ours, "code4rena_published": C4_2023,
            "submissions_ratio": round(ratio, 4) if ratio is not None else None,
            "note": "C4's High/Medium figures are judged severities; ours are the labels as submitted."}


def validated_block(rows: List[Dict]) -> Dict:
    grp = audits(rows, era="validated")
    shares = [r["submissions"] / r["est_total_submissions"] for r in grp
              if r["est_total_submissions"] and r["est_total_submissions"] > 0]
    return {
        "audits": len(grp),
        "first_start": min(r["start"] for r in grp).isoformat() if grp else None,
        "last_start": max(r["start"] for r in grp).isoformat() if grp else None,
        "promoted_records": sum(r["submissions"] for r in grp),
        "est_total_submissions": sum(r["est_total_submissions"] or 0 for r in grp),
        "median_est_total": _median([r["est_total_submissions"] for r in grp]),
        "median_promoted_share": _median(shares),
    }


def summary(records: List[Dict]) -> Dict:
    rows = rows_of(records)
    full = audits(rows, era="full")
    return {
        "records": len(records),
        "errors": sum(1 for r in records if r.get("error")),
        "rows": len(rows),
        "kinds": {k: sum(1 for r in rows if r["kind"] == k) for k in ("audit", "mitigation")},
        "undated": sum(1 for r in rows if r["start"] is None),
        "date_sources": {s: sum(1 for r in rows if r["date_source"] == s) for s in ("readme", "report")},
        "with_pot": sum(1 for r in rows if r["pot_usd"] is not None),
        "full_era_audits": len(full),
        "full_era_first_start": full[0]["start"].isoformat() if full else None,
        "full_era_last_start": full[-1]["start"].isoformat() if full else None,
        "full_era_submissions": sum(r["submissions"] for r in full),
        "by_year": series(full, "year"),
        "by_half": series(full, "half"),
        "by_quarter": {k: {"audits": v["audits"], "submissions": v["submissions"], "hm_subs": v["hm_subs"],
                           "median_hm_per_day": v["median_hm_per_day"]}
                       for k, v in series(full, "quarter").items()},
        "validated_era": validated_block(rows),
        "check_2023": check_2023(rows),
    }


def write_csv(rows: List[Dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = dict(row)
            for key in ("signal_rate", "hm_per_day", "hm_per_1k_usd"):
                if out[key] is not None:
                    out[key] = round(out[key], 4)
            for key in ("start", "end"):
                out[key] = out[key].isoformat() if out[key] else ""
            writer.writerow(out)


def write_jsonl(records: List[Dict], path: str) -> int:
    """The fetched facts (contest-level only), for anyone who wants to recompute."""
    with open(path, "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return len(records)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--in", dest="inp", required=True, help="JSONL from fetch_c4.py")
    parser.add_argument("--out-dir", default=None,
                        help="write c4_contests.csv, c4_contests.jsonl and summary.json here")
    args = parser.parse_args(argv)
    records = load(args.inp)
    result = summary(records)
    text = json.dumps(result, indent=2, default=str)
    print(text)
    if args.out_dir:
        os.makedirs(args.out_dir, exist_ok=True)
        write_csv(rows_of(records), os.path.join(args.out_dir, "c4_contests.csv"))
        write_jsonl(records, os.path.join(args.out_dir, "c4_contests.jsonl"))
        with open(os.path.join(args.out_dir, "summary.json"), "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
