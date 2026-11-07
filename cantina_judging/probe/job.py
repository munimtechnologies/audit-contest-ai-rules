# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working for MV2 of Munim, Inc.
"""Feasibility probe: how often has the Internet Archive captured Cantina's public
competitions API and its competition pages?

Purpose: Cantina's API has no completion timestamp (only createdAt and timeframe
start/end), so a census of how long judging takes needs a second source. This job
ONLY counts Wayback CDX capture rows (timestamps, URLs, HTTP status). It downloads
no archived page bodies and reads no contest status, so it measures nothing about
judging durations; any census is pre-registered separately after this.
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

CDX = "https://web.archive.org/cdx/search/cdx"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com; feasibility count, Apache-2.0)"
ID_RE = re.compile(r"/competitions/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", re.I)
V4LEND = "e275368c-547d-4d91-a418-053ad31082a8"

QUERIES = {
    "api": {"url": "cantina.xyz/api/v0/competitions", "matchType": "prefix"},
    "pages": {"url": "cantina.xyz/competitions/", "matchType": "prefix"},
}


def build_url(q, limit):
    params = dict(q)
    params.update({"output": "json", "fl": "timestamp,original,statuscode,mimetype,length",
                   "limit": str(limit)})
    return CDX + "?" + urllib.parse.urlencode(params)


def fetch_json(url, tries=4, timeout=120):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read().decode("utf-8", "replace").strip()
            return json.loads(body) if body else []
        except Exception as e:  # network errors are reported, never hidden
            last = repr(e)
            time.sleep(10 * (i + 1))
    raise RuntimeError("CDX fetch failed after %d tries: %s" % (tries, last))


def parse_rows(rows):
    """CDX json output: first row is the header. Returns list of dicts."""
    if not rows:
        return []
    head = rows[0]
    return [dict(zip(head, r)) for r in rows[1:]]


def competition_id(original):
    m = ID_RE.search(original or "")
    return m.group(1).lower() if m else None


def day(ts):
    return "%s-%s-%s" % (ts[0:4], ts[4:6], ts[6:8]) if ts and len(ts) >= 8 else ""


def summarise_api(rows):
    ok = [r for r in rows if r.get("statuscode") == "200"]
    days = sorted({day(r["timestamp"]) for r in ok})
    return {
        "rows": len(rows),
        "status_200": len(ok),
        "distinct_days_200": len(days),
        "first_200": days[0] if days else None,
        "last_200": days[-1] if days else None,
        "days_200": days,
    }


def summarise_pages(rows):
    per = {}
    for r in rows:
        cid = competition_id(r.get("original"))
        if not cid:
            continue
        d = per.setdefault(cid, {"captures": 0, "captures_200": 0, "days_200": set()})
        d["captures"] += 1
        if r.get("statuscode") == "200":
            d["captures_200"] += 1
            d["days_200"].add(day(r["timestamp"]))
    table = []
    for cid, d in sorted(per.items()):
        days = sorted(d["days_200"])
        table.append({"id": cid, "captures": d["captures"], "captures_200": d["captures_200"],
                      "distinct_days_200": len(days),
                      "first_200": days[0] if days else "", "last_200": days[-1] if days else ""})
    multi = [t for t in table if t["distinct_days_200"] >= 2]
    return table, {
        "rows": len(rows),
        "rows_with_id": sum(t["captures"] for t in table),
        "distinct_ids": len(table),
        "ids_with_200": sum(1 for t in table if t["captures_200"] > 0),
        "ids_with_2plus_days_200": len(multi),
        "ids_with_5plus_days_200": sum(1 for t in table if t["distinct_days_200"] >= 5),
        "v4lend": next((t for t in table if t["id"] == V4LEND), None),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--limit", type=int, default=50000)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    summary = {"note": "Counts of Wayback CDX capture rows only; no archived bodies read.",
               "queries": {}, "errors": []}
    api_rows, page_rows = [], []
    for name, q in QUERIES.items():
        url = build_url(q, a.limit)
        summary["queries"][name] = url
        try:
            rows = parse_rows(fetch_json(url))
        except Exception as e:
            summary["errors"].append({name: str(e)})
            rows = []
        if name == "api":
            api_rows = rows
        else:
            page_rows = rows
        time.sleep(5)
    summary["api"] = summarise_api(api_rows)
    table, summary["pages"] = summarise_pages(page_rows)
    summary["limit_hit"] = {"api": len(api_rows) >= a.limit, "pages": len(page_rows) >= a.limit}
    with open(os.path.join(a.out_dir, "api_captures.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "original", "statuscode", "length"])
        for r in api_rows:
            w.writerow([r.get("timestamp"), r.get("original"), r.get("statuscode"), r.get("length")])
    with open(os.path.join(a.out_dir, "page_captures_by_id.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "captures", "captures_200", "distinct_days_200",
                                          "first_200", "last_200"])
        w.writeheader()
        w.writerows(table)
    with open(os.path.join(a.out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in summary.items() if k != "queries"}, indent=1, sort_keys=True)[:6000])
    return 0 if not summary["errors"] else 2


if __name__ == "__main__":
    sys.exit(main())
