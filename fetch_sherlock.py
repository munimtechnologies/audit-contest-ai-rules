#!/usr/bin/env python3
"""fetch_sherlock.py -- download every Sherlock contest record from Sherlock's public API.

Reads https://mainnet-contest.sherlock.xyz/contests (the same JSON the sherlock.xyz
site uses), then each /contests/<id>, and writes one trimmed JSON object per line.
Only contest-level facts are kept: dates, pot, token, code size, KYC flag, and
Sherlock's own count of issues submitted (num_competition_issues). No researcher or
judge handles, no issue text.

Polite: one request at a time, a pause between requests, a few retries.
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

API = "https://mainnet-contest.sherlock.xyz"
USER_AGENT = "MV2-Munim-research/1.0 (munimversion2@gmail.com)"

KEEP = (
    "id", "title", "status", "type_label", "private", "starts_at", "ends_at",
    "prize_pool", "rewards", "token", "judging_prize_pool", "lead_senior_auditor_fixed_pay",
    "lead_judge_fixed_pay", "first_blood_pool", "num_competition_issues", "nsloc",
    "requires_kyc", "is_best_efforts", "bug_bounty_contest", "is_legacy_contest",
    "uses_live_issues", "is_judging_v3", "calc_completed", "languages",
    "judging_repo_name", "template_repo_name",
)


def get_json(url: str, retries: int = 4, pause: float = 2.0) -> Optional[object]:
    """GET a JSON document; None on 403/404 (private or missing contests)."""
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403, 404):
                return None
            err = exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            err = exc
        time.sleep(pause * (attempt + 1))
    print(f"giving up on {url}: {err}", file=sys.stderr)
    return None


def list_ids(query: str, pause: float) -> List[int]:
    """Every contest id on every page of /contests?<query>page=N."""
    ids: List[int] = []
    page = 1
    while True:
        doc = get_json(f"{API}/contests?{query}page={page}")
        if not isinstance(doc, dict):
            break
        ids.extend(int(item["id"]) for item in doc.get("items", []) if "id" in item)
        if not doc.get("has_next"):
            break
        page += 1
        time.sleep(pause)
    return ids


def trim(detail: Dict) -> Dict:
    """Keep contest-level facts only, plus code size summed over the scope."""
    rec = {key: detail.get(key) for key in KEEP}
    scope = detail.get("scope") or []
    nsloc_sum = 0
    files = 0
    for repo in scope:
        if not isinstance(repo, dict):
            continue
        total = repo.get("total_nsloc")
        if isinstance(total, (int, float)):
            nsloc_sum += int(total)
        files += len(repo.get("files") or [])
    rec["scope_repos"] = len(scope)
    rec["scope_files"] = files
    rec["scope_nsloc_sum"] = nsloc_sum
    rec["has_report"] = bool(detail.get("report"))
    rec["rewards_tiers"] = [
        {"severity": t.get("severity"), "unlock_percentage": t.get("unlock_percentage"),
         "min_count": t.get("min_count")}
        for t in (detail.get("rewards_tiers") or []) if isinstance(t, dict)
    ]
    return rec


def fetch_all(out_path: str, pause: float, limit: Optional[int] = None) -> int:
    ids = sorted(set(list_ids("", pause)) | set(list_ids("status=FINISHED&", pause)))
    if limit:
        ids = ids[:limit]
    print(f"{len(ids)} contest ids")
    written = 0
    fetched_on = time.strftime("%Y-%m-%d", time.gmtime())
    tmp = out_path + ".part"
    with open(tmp, "w", encoding="utf-8") as fh:
        for cid in ids:
            detail = get_json(f"{API}/contests/{cid}")
            if isinstance(detail, dict):
                rec = trim(detail)
                rec["fetched_on"] = fetched_on
                fh.write(json.dumps(rec, sort_keys=True) + "\n")
                written += 1
            time.sleep(pause)
    os.replace(tmp, out_path)
    print(f"wrote {written} records to {out_path}")
    return written


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, help="JSONL file to write")
    parser.add_argument("--pause", type=float, default=0.4, help="seconds between requests")
    parser.add_argument("--limit", type=int, default=None, help="only the first N ids (testing)")
    parser.add_argument("--skip-if-exists", action="store_true", help="do nothing if --out already exists")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.skip_if_exists and os.path.exists(args.out) and os.path.getsize(args.out) > 0:
        print(f"{args.out} exists, not refetching")
        return 0
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    return 0 if fetch_all(args.out, args.pause, args.limit) > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
