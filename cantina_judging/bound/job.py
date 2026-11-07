# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working for MV2 of Munim, Inc.
"""Stage 1 of the archived-page route for the Cantina judging-duration census.

Pre-registration: paper/cantina-judging-duration-PREREGISTRATION.md (6 Nov 2026) and
paper/cantina-judging-duration-pages-ADDENDUM.md (7 Nov 2026) in
github.com/munimtechnologies/audit-contest-ai-rules.

This job reads NO archived page bodies and no archived status. It uses only capture
TIMES (Wayback CDX rows) and each competition's current end time from Cantina's public
API, and computes an upper bound on how many competitions could ever pass the
pre-registered eligibility rule (completion bracket at most 14 days wide). If even
that bound is below 20, the census is infeasible from this source and no bodies are
fetched by any later job.

A bracket is built from consecutive points in [E, captures after E]; a bracket can be
at most 14 days wide only if some consecutive gap is at most 14 days. So the count of
competitions with such a gap is an upper bound on the eligible count.
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

CDX = "https://web.archive.org/cdx/search/cdx"
API = "https://cantina.xyz/api/v0/competitions"
ADDENDUM = ("https://api.github.com/repos/munimtechnologies/audit-contest-ai-rules/contents/"
            "paper/cantina-judging-duration-pages-ADDENDUM.md")
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com; capture-time feasibility bound, Apache-2.0)"
UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
MAIN_RE = re.compile(r"^/competitions/(%s)/?$" % UUID, re.I)
ANY_RE = re.compile(r"^/competitions/(%s)(/.*)?$" % UUID, re.I)
COMPLETION_MAX_DAYS = 14.0
START_MAX_DAYS = 3.0
GATE = 20
DAY = 86400.0


def fetch_bytes(url, tries=4, timeout=180, accept=None):
    last = None
    for i in range(tries):
        try:
            headers = {"User-Agent": UA}
            if accept:
                headers["Accept"] = accept
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # reported, never hidden
            last = repr(e)
            time.sleep(10 * (i + 1))
    raise RuntimeError("fetch failed after %d tries: %s: %s" % (tries, url, last))


def addendum_is_public(polls=15, wait_s=120):
    """The addendum must be public on GitHub before this job computes anything."""
    for i in range(polls):
        try:
            req = urllib.request.Request(ADDENDUM, headers={"User-Agent": UA,
                                                            "Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                meta = json.loads(r.read().decode("utf-8", "replace"))
                return {"public": True, "sha": meta.get("sha"), "polls": i + 1}
        except urllib.error.HTTPError as e:
            if e.code != 404:
                last = "HTTP %d" % e.code
        except Exception as e:
            last = repr(e)
        if i < polls - 1:
            time.sleep(wait_s)
    return {"public": False, "polls": polls}


def parse_rows(rows):
    """CDX json output: first row is the header."""
    if not rows:
        return []
    head = rows[0]
    return [dict(zip(head, r)) for r in rows[1:]]


def parse_ts(ts):
    """14-digit Wayback timestamp -> aware UTC datetime (None if malformed)."""
    if not ts or len(ts) < 14 or not ts[:14].isdigit():
        return None
    return datetime.strptime(ts[:14], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)


def parse_iso(s):
    if not isinstance(s, str) or not s:
        return None
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


def capture_id(original, main_only):
    """Competition id of a capture URL, or None. main_only: path exactly /competitions/<id>[/]."""
    try:
        parts = urllib.parse.urlsplit(original or "")
    except ValueError:
        return None
    host = (parts.hostname or "").lower()
    if host not in ("cantina.xyz", "www.cantina.xyz"):
        return None
    m = (MAIN_RE if main_only else ANY_RE).match(parts.path or "")
    return m.group(1).lower() if m else None


def captures_by_id(rows, main_only):
    """{id: sorted distinct capture datetimes}, HTTP 200 rows only."""
    out = {}
    for r in rows:
        if r.get("statuscode") != "200":
            continue
        cid = capture_id(r.get("original"), main_only)
        t = parse_ts(r.get("timestamp"))
        if cid and t:
            out.setdefault(cid, set()).add(t)
    return {k: sorted(v) for k, v in out.items()}


def bound_for(end, times):
    """Gaps between consecutive points of [end] + captures after end, in days."""
    after = [t for t in times if t > end]
    points = [end] + after
    gaps = [(b - a).total_seconds() / DAY for a, b in zip(points, points[1:])]
    return {
        "n_after_end": len(after),
        "first_after_end_days": round(gaps[0], 3) if gaps else None,
        "min_gap_days": round(min(gaps), 3) if gaps else None,
        "completion_possible": any(g <= COMPLETION_MAX_DAYS for g in gaps),
        "start_possible": any(g <= START_MAX_DAYS for g in gaps),
    }


def competitions_from_api(data):
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list) and v and isinstance(v[0], dict) and "id" in v[0]:
                data = v
                break
        else:
            data = []
    out = []
    for c in data if isinstance(data, list) else []:
        if not isinstance(c, dict) or not c.get("id"):
            continue
        tf = c.get("timeframe") or {}
        out.append({"id": str(c["id"]).lower(), "status": c.get("status"), "kind": c.get("kind"),
                    "end_raw": tf.get("end") if isinstance(tf, dict) else None,
                    "end": parse_iso(tf.get("end")) if isinstance(tf, dict) else None,
                    "totalFindings": c.get("totalFindings")})
    return out


def build(comps, main_caps, any_caps, now):
    table, counts = [], {"api_competitions": len(comps), "no_end": 0, "end_in_future": 0,
                         "ended": 0, "ended_with_main_capture_after_end": 0}
    api_ids = set()
    for c in comps:
        api_ids.add(c["id"])
        if c["end"] is None:
            counts["no_end"] += 1
            continue
        if c["end"] > now:
            counts["end_in_future"] += 1
            continue
        counts["ended"] += 1
        bm = bound_for(c["end"], main_caps.get(c["id"], []))
        ba = bound_for(c["end"], any_caps.get(c["id"], []))
        if bm["n_after_end"]:
            counts["ended_with_main_capture_after_end"] += 1
        table.append({"id": c["id"], "kind": c["kind"], "status_now": c["status"],
                      "end": c["end"].strftime("%Y-%m-%dT%H:%M:%SZ"), "totalFindings": c["totalFindings"],
                      "main_captures_200": len(main_caps.get(c["id"], [])),
                      "main_after_end": bm["n_after_end"], "main_first_after_end_days": bm["first_after_end_days"],
                      "main_min_gap_days": bm["min_gap_days"],
                      "main_completion_possible": bm["completion_possible"],
                      "main_start_possible": bm["start_possible"],
                      "any_after_end": ba["n_after_end"], "any_min_gap_days": ba["min_gap_days"],
                      "any_completion_possible": ba["completion_possible"]})
    bound = sum(1 for t in table if t["main_completion_possible"])
    counts.update({
        "bound_eligible_main": bound,
        "bound_eligible_main_status_now_complete": sum(
            1 for t in table if t["main_completion_possible"] and str(t["status_now"]).lower() in ("complete", "completed")),
        "bound_start_bracket_le3d_main": sum(1 for t in table if t["main_start_possible"]),
        "bound_eligible_any_subpath_descriptive": sum(1 for t in table if t["any_completion_possible"]),
        "captured_ids_main": len(main_caps), "captured_ids_any": len(any_caps),
        "captured_ids_not_in_api": len(set(any_caps) - api_ids),
        "gate": GATE,
        "gate_can_pass": bound >= GATE,
    })
    return table, counts


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--data-dir", default="/data")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    started = datetime.now(timezone.utc)
    summary = {"note": "Capture TIMES and current API end times only; no archived bodies or archived statuses read.",
               "started": started.strftime("%Y-%m-%dT%H:%M:%SZ")}
    pre = addendum_is_public()
    summary["addendum"] = pre
    if not pre["public"]:
        summary["stopped"] = "addendum not public on GitHub; nothing computed"
        with open(os.path.join(a.out_dir, "summary.json"), "w") as f:
            json.dump(summary, f, indent=1, sort_keys=True)
        print(json.dumps(summary, indent=1))
        return 3
    q = {"url": "cantina.xyz/competitions/", "matchType": "prefix", "output": "json",
         "fl": "timestamp,original,statuscode,mimetype,length", "limit": "50000"}
    cdx_url = CDX + "?" + urllib.parse.urlencode(q)
    summary["cdx_query"] = cdx_url
    raw_cdx = fetch_bytes(cdx_url)
    rows = parse_rows(json.loads(raw_cdx.decode("utf-8", "replace").strip() or "[]"))
    time.sleep(3)
    raw_api = fetch_bytes(API, accept="application/json")
    comps = competitions_from_api(json.loads(raw_api.decode("utf-8", "replace")))
    read_at = datetime.now(timezone.utc)
    summary["api_read_at"] = read_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    try:  # keep the raw inputs for later stages (small; same data_key)
        os.makedirs(a.data_dir, exist_ok=True)
        stamp = read_at.strftime("%Y%m%dT%H%M%SZ")
        with open(os.path.join(a.data_dir, "cdx_pages_%s.json" % stamp), "wb") as f:
            f.write(raw_cdx)
        with open(os.path.join(a.data_dir, "api_competitions_%s.json" % stamp), "wb") as f:
            f.write(raw_api)
        summary["saved_to_data"] = stamp
    except OSError as e:
        summary["saved_to_data"] = "failed: %r" % e
    main_caps = captures_by_id(rows, True)
    any_caps = captures_by_id(rows, False)
    table, counts = build(comps, main_caps, any_caps, read_at)
    summary["cdx_rows"] = len(rows)
    summary["counts"] = counts
    summary["status_now_vocabulary"] = sorted({str(c["status"]) for c in comps})
    summary["kind_vocabulary"] = sorted({str(c["kind"]) for c in comps})
    fields = list(table[0].keys()) if table else ["id"]
    with open(os.path.join(a.out_dir, "bounds_by_id.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(table)
    with open(os.path.join(a.out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
    print(json.dumps(summary, indent=1, sort_keys=True)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
