#!/usr/bin/env python3
"""cantina_crowding.py -- how crowded have Cantina competitions become? (full census)

Reads the JSONL written by fetch_cantina.py (one record per competition, straight from
Cantina's public API) and reports, for ended competitions with a findings count:

  * findings submitted per contest day and per $1,000 of pot (stablecoin pots only),
    with medians by the year a competition started, and the same for pots <= $60k;
  * competitions and findings per quarter (the time series);
  * KYC vs non-KYC competitions, compared within the same start year;
  * a breakdown by Cantina's own kind (public contest, private contest, ...);
  * optionally, a cross-check against the hand-read v0.3.0 sample CSV.

"Findings submitted" is Cantina's totalFindings: every submission, valid or not, so this
measures crowding, not quality. Competitions that share one pot (for example the Pectra
client set) are left out of the per-dollar figures. Private contests appear only in the
by-kind aggregates, never as rows. No third-party dependencies.

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
SMALL_POT_USD = 60000.0
CSV_FIELDS = (
    "id", "name", "company", "kind", "start", "end", "days", "pot", "currency", "pot_usd",
    "shared_pot", "kyc_required", "total_findings", "per_day", "per_1k_usd",
)


def parse_time(value) -> Optional[_dt.datetime]:
    """ISO 8601 with a trailing Z (Cantina's format) -> aware UTC datetime; None if unusable."""
    if not isinstance(value, str) or not value:
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        out = _dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if out.tzinfo is None:
        out = out.replace(tzinfo=_dt.timezone.utc)
    return out.astimezone(_dt.timezone.utc)


def load(path: str) -> List[Dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def is_private(rec: Dict) -> bool:
    return str(rec.get("kind") or "").startswith("private")


def pot_usd(rec: Dict) -> Optional[float]:
    """Headline pot in USD for stablecoin pots; None otherwise."""
    if str(rec.get("currency") or "").upper() not in STABLECOINS:
        return None
    pot = rec.get("pot")
    if isinstance(pot, (int, float)) and not isinstance(pot, bool) and pot > 0:
        return float(pot)
    return None


def shared_pot_ids(records: List[Dict]) -> set:
    """Ids of public competitions whose (company, start, end, pot) is shared with another one."""
    groups: Dict[tuple, List] = {}
    for rec in records:
        if is_private(rec) or not rec.get("company"):
            continue
        key = (rec.get("company"), rec.get("start"), rec.get("end"), rec.get("pot"))
        groups.setdefault(key, []).append(rec.get("id"))
    return {cid for ids in groups.values() if len(ids) > 1 for cid in ids}


def enrich(rec: Dict, now: _dt.datetime, shared: set) -> Optional[Dict]:
    """Typed row for an ended competition with a positive findings count, else None."""
    findings = rec.get("total_findings")
    start, end = parse_time(rec.get("start")), parse_time(rec.get("end"))
    if isinstance(findings, bool) or not isinstance(findings, int) or findings <= 0:
        return None
    if start is None or end is None or end <= start or end > now:
        return None
    days = max((end - start).total_seconds() / 86400.0, 0.5)
    is_shared = rec.get("id") in shared
    usd = None if is_shared else pot_usd(rec)
    return {
        "id": rec.get("id"),
        "name": rec.get("name"),
        "company": rec.get("company"),
        "kind": rec.get("kind") or "",
        "private": is_private(rec),
        "start": start.date(),
        "end": end.date(),
        "days": round(days, 2),
        "pot": rec.get("pot"),
        "currency": rec.get("currency"),
        "pot_usd": usd,
        "shared_pot": is_shared,
        "kyc_required": bool(rec.get("kyc_required")),
        "total_findings": findings,
        "per_day": findings / days,
        "per_1k_usd": None if usd is None else findings / (usd / 1000.0),
    }


def reference_time(records: List[Dict]) -> _dt.datetime:
    """When the records were fetched (latest fetched_on), else now."""
    stamps = [parse_time(r.get("fetched_on")) for r in records]
    stamps = [s for s in stamps if s is not None]
    return max(stamps) if stamps else _dt.datetime.now(_dt.timezone.utc)


def all_rows(records: List[Dict]) -> List[Dict]:
    now = reference_time(records)
    shared = shared_pot_ids(records)
    rows = [r for r in (enrich(rec, now, shared) for rec in records) if r is not None]
    return sorted(rows, key=lambda r: (r["start"], str(r["id"])))


def public_rows(records: List[Dict]) -> List[Dict]:
    return [r for r in all_rows(records) if not r["private"]]


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
         "findings": sum(r["total_findings"] for r in grp),
         "median_per_day": round(statistics.median(r["per_day"] for r in grp), 2)}
        for key, grp in sorted(groups.items())
    ]


def kyc_within_year(rows: List[Dict]) -> Dict[int, Dict]:
    """Median findings/day for KYC and non-KYC competitions that started in the same year."""
    out: Dict[int, Dict] = {}
    for year in sorted({r["start"].year for r in rows}):
        yr = [r for r in rows if r["start"].year == year]
        kyc = [r["per_day"] for r in yr if r["kyc_required"]]
        open_ = [r["per_day"] for r in yr if not r["kyc_required"]]
        out[year] = {"kyc": _median_block(kyc), "no_kyc": _median_block(open_)}
    return out


def by_kind(rows: List[Dict]) -> Dict[str, Dict]:
    groups: Dict[str, List[Dict]] = {}
    for row in rows:
        groups.setdefault(row["kind"] or "(none)", []).append(row)
    return {
        kind: dict(_median_block([r["per_day"] for r in grp]),
                   findings=sum(r["total_findings"] for r in grp))
        for kind, grp in sorted(groups.items())
    }


def sample_check(records: List[Dict], sample_path: str) -> Dict:
    """Compare the API's totalFindings with the counts read by hand off each page (v0.3.0)."""
    by_id = {str(r.get("id")): r for r in records}
    checked = []
    with open(sample_path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            cid = row["url"].rstrip("/").rsplit("/", 1)[-1]
            api = by_id.get(cid)
            hand = int(row["findings_submitted"])
            got = api.get("total_findings") if api else None
            checked.append({"id": cid, "name": row["name"], "status": row["status"],
                            "hand": hand, "api": got,
                            "match": got == hand})
    done = [c for c in checked if c["status"] != "live"]
    return {
        "rows": len(checked),
        "found_in_api": sum(1 for c in checked if c["api"] is not None),
        "ended_rows": len(done),
        "ended_exact_matches": sum(1 for c in done if c["match"]),
        "mismatches": [c for c in checked if not c["match"]],
    }


def summary(records: List[Dict], sample_path: Optional[str] = None) -> Dict:
    every = all_rows(records)
    rows = [r for r in every if not r["private"]]

    def small(row: Dict) -> bool:
        return row["pot_usd"] is not None and row["pot_usd"] <= SMALL_POT_USD

    out = {
        "records": len(records),
        "records_public": sum(1 for r in records if not is_private(r)),
        "status_counts": _counts(records, "status"),
        "kind_counts": _counts(records, "kind"),
        "ended_public_with_counts": len(rows),
        "findings_total_public": sum(r["total_findings"] for r in rows),
        "first_start": rows[0]["start"].isoformat() if rows else None,
        "last_start": rows[-1]["start"].isoformat() if rows else None,
        "per_day_by_year": by_year(rows, "per_day"),
        "per_day_by_year_small_pots": by_year(rows, "per_day", where=small),
        "findings_by_year": by_year(rows, "total_findings"),
        "per_1k_usd_by_year": by_year(rows, "per_1k_usd"),
        "pot_usd_by_year": by_year(rows, "pot_usd"),
        "days_by_year": by_year(rows, "days"),
        "kyc_within_year": kyc_within_year(rows),
        "per_day_by_kind_incl_private": by_kind(every),
        "shared_pot_rows": sum(1 for r in rows if r["shared_pot"]),
        "quarterly": quarterly(rows),
    }
    if sample_path:
        out["sample_check_v030"] = sample_check(records, sample_path)
    return out


def _counts(records: List[Dict], key: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for rec in records:
        label = str(rec.get(key) or "(none)")
        out[label] = out.get(label, 0) + 1
    return dict(sorted(out.items()))


def write_csv(rows: List[Dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = dict(row)
            for key in ("per_day", "per_1k_usd"):
                if out[key] is not None:
                    out[key] = round(out[key], 3)
            writer.writerow(out)


def write_public_jsonl(records: List[Dict], path: str) -> int:
    """Every public record (live ones too), for anyone who wants to recompute."""
    kept = [r for r in records if not is_private(r)]
    with open(path, "w", encoding="utf-8") as fh:
        for rec in kept:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return len(kept)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--in", dest="inp", required=True, help="JSONL from fetch_cantina.py")
    parser.add_argument("--out-dir", default=None,
                        help="write cantina_contests.csv, cantina_contests.jsonl and summary.json here")
    parser.add_argument("--sample", default=None, help="v0.3.0 hand-read CSV to cross-check against")
    args = parser.parse_args(argv)
    records = load(args.inp)
    result = summary(records, args.sample)
    text = json.dumps(result, indent=2, default=str)
    print(text)
    if args.out_dir:
        os.makedirs(args.out_dir, exist_ok=True)
        write_csv(public_rows(records), os.path.join(args.out_dir, "cantina_contests.csv"))
        write_public_jsonl(records, os.path.join(args.out_dir, "cantina_contests.jsonl"))
        with open(os.path.join(args.out_dir, "summary.json"), "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
