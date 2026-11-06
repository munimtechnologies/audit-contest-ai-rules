#!/usr/bin/env python3
"""drift.py -- do Cantina's per-contest finding counts change after a contest ends?

Compares MV2's published 14 Oct 2026 snapshot of https://cantina.xyz/api/v0/competitions
(data/cantina_census.jsonl in munimtechnologies/audit-contest-ai-rules) with one fresh GET
of the same API, matched by contest id, and grades the pre-registered checks D1-D3
(cantina-drift-prereg.md). Contest-level facts only: no handles, no private-contest names.

Licensed under Apache-2.0. Made with AI agents working for MV2 of Munim, Inc.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional

API = "https://cantina.xyz/api/v0/competitions"
BASELINE_URL = ("https://raw.githubusercontent.com/munimtechnologies/audit-contest-ai-rules/"
                "main/data/cantina_census.jsonl")
USER_AGENT = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
V4LEND_ID = "e275368c-547d-4d91-a418-053ad31082a8"
V4LEND_FLOOR = 6906          # D2: two page reads + two API reads, 5 Nov 2026 ~09:25-09:40Z
D1_SHARE = 0.95              # D1: share of S unchanged must be >= this
D3_REL = 0.005               # D3: |sum now - sum then| must be < this * sum then


def fetch(url: str, retries: int = 4, pause: float = 3.0) -> Optional[bytes]:
    err: object = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            err = exc
        time.sleep(pause * (attempt + 1))
    print(f"giving up on {url}: {err}", file=sys.stderr)
    return None


def parse_time(value: Optional[str]) -> Optional[datetime]:
    """Accepts '2026-11-03T18:30:00Z', '2026-10-14T20:03Z' and fractional-second forms."""
    if not value or not isinstance(value, str):
        return None
    text = value.strip().replace("Z", "+00:00")
    for candidate in (text, text.replace("+00:00", ":00+00:00")):
        try:
            dt = datetime.fromisoformat(candidate)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def trim_api(item: Dict) -> Dict:
    """Same fields as fetch_cantina.py (run 2026-10-14); private contests keep no name."""
    kind = item.get("kind") or ""
    private = kind.startswith("private")
    tf = item.get("timeframe") if isinstance(item.get("timeframe"), dict) else {}
    return {
        "id": item.get("id"),
        "name": None if private else item.get("name"),
        "kind": kind,
        "status": item.get("status"),
        "start": tf.get("start"),
        "end": tf.get("end"),
        "total_findings": item.get("totalFindings"),
    }


def records_from_api(doc: object) -> List[Dict]:
    if isinstance(doc, dict):
        doc = doc.get("items") or doc.get("data") or []
    if not isinstance(doc, list):
        return []
    return [trim_api(x) for x in doc if isinstance(x, dict)]


def load_jsonl(text: str) -> List[Dict]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def is_count(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def compare(baseline: List[Dict], current: List[Dict], baseline_at: str, current_at: str) -> Dict:
    now_by_id = {r.get("id"): r for r in current}
    base_ids = {r.get("id") for r in baseline}
    rows = []
    for b in baseline:
        c = now_by_id.get(b.get("id"))
        then_n = b.get("total_findings")
        now_n = c.get("total_findings") if c else None
        delta = (now_n - then_n) if (is_count(then_n) and is_count(now_n)) else None
        end = parse_time(b.get("end"))
        b_at = parse_time(baseline_at)
        rows.append({
            "id": b.get("id"),
            "name": b.get("name") if (b.get("kind") or "").startswith("public") else None,
            "kind": b.get("kind"),
            "status_then": b.get("status"),
            "status_now": c.get("status") if c else "MISSING",
            "end": b.get("end"),
            "days_ended_at_baseline": round((b_at - end).total_seconds() / 86400, 2) if (end and b_at) else None,
            "findings_then": then_n,
            "findings_now": now_n,
            "delta": delta,
            "change": ("missing" if c is None else "no_count" if delta is None else
                       "unchanged" if delta == 0 else "increased" if delta > 0 else "decreased"),
        })
    s_rows = [r for r in rows if r["kind"] == "public_contest" and r["status_then"] == "complete"
              and r["change"] not in ("missing", "no_count")]
    n_s = len(s_rows)
    unchanged = sum(1 for r in s_rows if r["change"] == "unchanged")
    sum_then = sum(r["findings_then"] for r in s_rows)
    sum_now = sum(r["findings_now"] for r in s_rows)
    v4 = next((r for r in current if r.get("id") == V4LEND_ID), None)
    v4_now = v4.get("total_findings") if v4 else None
    d1 = (unchanged / n_s >= D1_SHARE) if n_s else None
    d3 = (abs(sum_now - sum_then) < D3_REL * sum_then) if sum_then else None
    d2 = (v4_now >= V4LEND_FLOOR) if is_count(v4_now) else None
    word = {True: "HELD", False: "FAILED", None: "NOT GRADABLE"}
    changed = [r for r in s_rows if r["change"] != "unchanged"]
    summary = {
        "baseline_fetched_on": baseline_at,
        "current_fetched_on": current_at,
        "baseline_records": len(baseline),
        "current_records": len(current),
        "new_ids_since_baseline": sorted(str(r.get("id")) for r in current if r.get("id") not in base_ids
                                         and (r.get("kind") or "").startswith("public")),
        "new_private_since_baseline": sum(1 for r in current if r.get("id") not in base_ids
                                          and not (r.get("kind") or "").startswith("public")),
        "missing_now": sum(1 for r in rows if r["change"] == "missing"),
        "S_size": n_s,
        "S_unchanged": unchanged,
        "S_increased": sum(1 for r in s_rows if r["change"] == "increased"),
        "S_decreased": sum(1 for r in s_rows if r["change"] == "decreased"),
        "S_sum_then": sum_then,
        "S_sum_now": sum_now,
        "S_sum_delta": sum_now - sum_then,
        "S_changed": [{k: r[k] for k in ("name", "status_now", "end", "days_ended_at_baseline",
                                         "findings_then", "findings_now", "delta")} for r in changed],
        "v4lend": {"status_now": v4.get("status") if v4 else None, "end": v4.get("end") if v4 else None,
                   "findings_now": v4_now},
        "D1": word[d1], "D1_share_unchanged": round(unchanged / n_s, 4) if n_s else None,
        "D2": word[d2],
        "D3": word[d3], "D3_rel_delta": round(abs(sum_now - sum_then) / sum_then, 6) if sum_then else None,
    }
    return {"rows": rows, "summary": summary}


def main(argv: Optional[Iterable[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args(list(argv) if argv is not None else None)
    os.makedirs(args.out_dir, exist_ok=True)

    raw_base = fetch(BASELINE_URL)
    if raw_base is None:
        return 2
    baseline = load_jsonl(raw_base.decode("utf-8"))
    base_at = sorted({str(r.get("fetched_on")) for r in baseline})
    raw_now = fetch(API)
    current_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if raw_now is None:
        return 3
    current = records_from_api(json.loads(raw_now.decode("utf-8")))
    if not current:
        print("API returned no records", file=sys.stderr)
        return 4

    result = compare(baseline, current, base_at[0] if base_at else "", current_at)
    result["summary"]["baseline_fetched_on_values"] = base_at

    with open(os.path.join(args.out_dir, "cantina_now.jsonl"), "w", encoding="utf-8") as fh:
        for r in current:
            fh.write(json.dumps(dict(r, fetched_on=current_at), sort_keys=True) + "\n")
    cols = ["id", "name", "kind", "status_then", "status_now", "end", "days_ended_at_baseline",
            "findings_then", "findings_now", "delta", "change"]
    with open(os.path.join(args.out_dir, "drift_rows.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in result["rows"]:
            w.writerow(r)
    with open(os.path.join(args.out_dir, "drift_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result["summary"], fh, indent=2, sort_keys=True)
    s = result["summary"]
    print(f"S={s['S_size']} unchanged={s['S_unchanged']} increased={s['S_increased']} "
          f"decreased={s['S_decreased']} sum {s['S_sum_then']}->{s['S_sum_now']}")
    print(f"v4lend now: {s['v4lend']}")
    print(f"D1 {s['D1']} ({s['D1_share_unchanged']})  D2 {s['D2']}  D3 {s['D3']} ({s['D3_rel_delta']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
