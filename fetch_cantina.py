#!/usr/bin/env python3
"""fetch_cantina.py -- download every Cantina competition record from Cantina's public API.

Reads https://cantina.xyz/api/v0/competitions (the same JSON the cantina.xyz site uses,
one unauthenticated GET, a complete array) and writes one trimmed JSON object per line.
Only contest-level facts are kept: dates, pot, currency, kind, KYC flag and Cantina's own
running count of findings submitted (totalFindings). No instructions text, no company
or researcher handles, and no name or URL for private contests.

Polite: a single request, a few retries.
Licensed under Apache-2.0. Made with AI agents working for MV2 of Munim, Inc.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Dict, Iterable, List, Optional

API = "https://cantina.xyz/api/v0/competitions"
USER_AGENT = "MV2-Munim-research/1.0 (munimversion2@gmail.com)"


def get_json(url: str, retries: int = 4, pause: float = 3.0) -> Optional[object]:
    """GET a JSON document; None if it never succeeds."""
    err: object = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            err = exc
        time.sleep(pause * (attempt + 1))
    print(f"giving up on {url}: {err}", file=sys.stderr)
    return None


def _num(value) -> Optional[float]:
    """Cantina stores pots as strings ("50000"); None when missing or not a number."""
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def trim(item: Dict) -> Dict:
    """Keep contest-level facts only. Private contests keep no name, URL or company."""
    kind = item.get("kind") or ""
    private = kind.startswith("private")
    timeframe = item.get("timeframe") or {}
    company = item.get("company") or {}
    return {
        "id": item.get("id"),
        "name": None if private else item.get("name"),
        "url": None if private else item.get("url"),
        "company": None if private else (company.get("name") if isinstance(company, dict) else None),
        "kind": kind,
        "status": item.get("status"),
        "start": timeframe.get("start") if isinstance(timeframe, dict) else None,
        "end": timeframe.get("end") if isinstance(timeframe, dict) else None,
        "created_at": item.get("createdAt"),
        "currency": item.get("currencyCode"),
        "pot": _num(item.get("totalRewardPot")),
        "kyc_required": bool(item.get("kycRequired")),
        "total_findings": item.get("totalFindings"),
        "allowed_severities": item.get("allowedSeverities"),
        "cantina_triaged": item.get("cantinaTriaged"),
    }


def records_from(doc: object) -> List[Dict]:
    """The API returns a bare array; tolerate {"items": [...]} or {"data": [...]} too."""
    if isinstance(doc, dict):
        doc = doc.get("items") or doc.get("data") or []
    if not isinstance(doc, list):
        return []
    return [trim(item) for item in doc if isinstance(item, dict)]


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, help="JSONL file to write")
    parser.add_argument("--skip-if-exists", action="store_true", help="do nothing if --out already exists")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.skip_if_exists and os.path.exists(args.out) and os.path.getsize(args.out) > 0:
        print(f"{args.out} exists, not refetching")
        return 0
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    records = records_from(get_json(API))
    fetched_on = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
    tmp = args.out + ".part"
    with open(tmp, "w", encoding="utf-8") as fh:
        for rec in records:
            rec["fetched_on"] = fetched_on
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    os.replace(tmp, args.out)
    print(f"wrote {len(records)} records to {args.out}")
    return 0 if records else 1


if __name__ == "__main__":
    raise SystemExit(main())
