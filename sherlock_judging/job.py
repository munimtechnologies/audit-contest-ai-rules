# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working for MV2 of Munim, Inc.
"""Sherlock judging-duration test (pre-registered, P1-P5).

Pre-registration: paper/sherlock-judging-duration-PREREGISTRATION.md in
github.com/munimtechnologies/audit-contest-ai-rules. This job refuses to fetch contest data or
compute anything (exit 3) until that file is public on GitHub, and it records the commit that
added it, so anyone can check that every number was fetched after the predictions were public.

Source: Sherlock's public contest API (https://mainnet-contest.sherlock.xyz), list endpoint
/contests?status=FINISHED&page=N and detail endpoint /contests/<id>. Only numeric/date fields,
the status/flags and the contest title are kept; no handles, avatars or other personal fields.

Measures (days unless noted):
  J = escalation_started_at - ends_at   (contest end to preliminary results / escalations open)
  S = judging_stopped_at   - ends_at    (contest end to the API's "judging stopped" time)
  W = escalation_ends_at - escalation_started_at   (escalation window, seconds)
  D(N) = max(2, ceil(N/100)) + max(2, ceil(N/200))  (documented days to preliminary results)
"""
import argparse
import csv
import json
import math
import os
import statistics
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone

REPO_API = "https://api.github.com/repos/munimtechnologies/audit-contest-ai-rules"
PREREG_PATH = "paper/sherlock-judging-duration-PREREGISTRATION.md"
API = "https://mainnet-contest.sherlock.xyz"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com; Sherlock judging-duration test, Apache-2.0)"
DAY = 86400.0
# Contests whose list fields were seen before registration (page 1 of status=FINISHED, read
# 2026-11-10) and the one whose detail record was seen (1209). Excluded from grading.
SEEN_IDS = frozenset({1140, 333, 38, 1260, 205, 677, 1209, 1028, 59, 6})
WINDOW_24H_S = 86400
WINDOW_TOL_S = 60
P1_TOL_DAYS = 1.0
P1_SHARE = 0.5
P2_SHARE = 0.9
P3_DAYS = 7.0
P4_RHO = 0.3
GATE = 20
GATE_YEAR = 10
PAUSE_S = 0.5
KEEP = ("id", "title", "status", "private", "is_judging_v3", "num_competition_issues", "starts_at",
        "ends_at", "escalation_started_at", "escalation_ends_at", "judging_stopped_at")
_sleep = time.sleep


# ---------------------------------------------------------------- pure functions (tested)

def _int(v):
    """Integer value of an API field, or None (booleans are not integers here)."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, str):
        s = v.strip()
        if s[:1] == "-":
            return -int(s[1:]) if s[1:].isdigit() else None
        return int(s) if s.isdigit() else None
    return None


def doc_days(n):
    """Documented days from contest end to preliminary results (Real-Time Judging docs):
    phase 1 lasts max(2, N/100) days and the Lead Judge gets max(2, N/200) days, rounded up."""
    n = int(n)
    return max(2, -(-n // 100)) + max(2, -(-n // 200))


def measures(rec):
    end = _int(rec.get("ends_at"))
    es = _int(rec.get("escalation_started_at"))
    ee = _int(rec.get("escalation_ends_at"))
    js = _int(rec.get("judging_stopped_at"))
    out = {"J_days": None, "S_days": None, "W_s": None}
    if end is not None and es is not None:
        out["J_days"] = (es - end) / DAY
    if end is not None and js is not None:
        out["S_days"] = (js - end) / DAY
    if es is not None and ee is not None:
        out["W_s"] = ee - es
    return out


def eligibility(rec):
    if rec.get("status") != "FINISHED":
        return False, "not_finished"
    if rec.get("private") is not False:
        return False, "private_or_unknown"
    n = _int(rec.get("num_competition_issues"))
    if n is None or n <= 0:
        return False, "no_issue_count"
    for k in ("ends_at", "escalation_started_at", "escalation_ends_at"):
        if _int(rec.get(k)) is None:
            return False, "missing_" + k
    return True, "eligible"


def row_from(rec):
    ok, why = eligibility(rec)
    end = _int(rec.get("ends_at"))
    row = {
        "id": _int(rec.get("id")),
        "title": str(rec.get("title") or "")[:120],
        "n": _int(rec.get("num_competition_issues")),
        "v3": rec.get("is_judging_v3") is True,
        "end": end,
        "year": datetime.fromtimestamp(end, timezone.utc).year if end is not None else None,
        "eligible": ok,
        "reason": why,
    }
    row.update(measures(rec))
    return row


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(xs, ys):
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    rx, ry = ranks(list(xs)), ranks(list(ys))
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    if sxx == 0 or syy == 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def _med(xs):
    xs = list(xs)
    return statistics.median(xs) if xs else None


def grade(rows, exclude=SEEN_IDS):
    """Grade P1-P5 exactly as pre-registered. held is True/False, or None = not testable."""
    el = [r for r in rows if r["eligible"] and r["id"] not in exclude]
    v3 = [r for r in el if r["v3"]]
    s_rows = [r for r in el if r["S_days"] is not None]
    res = {"n_eligible": len(el), "n_v3": len(v3), "n_with_S": len(s_rows)}

    if len(v3) >= GATE:
        within = sum(1 for r in v3 if r["J_days"] <= doc_days(r["n"]) + P1_TOL_DAYS)
        share = within / float(len(v3))
        res["P1"] = {"n": len(v3), "within_doc_plus_1d": within, "share": share,
                     "held": share >= P1_SHARE}
    else:
        res["P1"] = {"n": len(v3), "held": None, "note": "not testable: fewer than %d" % GATE}

    if len(v3) >= GATE:
        exact = sum(1 for r in v3 if abs(r["W_s"] - WINDOW_24H_S) <= WINDOW_TOL_S)
        share = exact / float(len(v3))
        res["P2"] = {"n": len(v3), "window_24h": exact, "share": share, "held": share < P2_SHARE}
    else:
        res["P2"] = {"n": len(v3), "held": None, "note": "not testable: fewer than %d" % GATE}

    if len(s_rows) >= GATE:
        med = _med(r["S_days"] - r["J_days"] for r in s_rows)
        res["P3"] = {"n": len(s_rows), "median_S_minus_J_days": med, "held": med > P3_DAYS}
    else:
        res["P3"] = {"n": len(s_rows), "held": None, "note": "not testable: fewer than %d" % GATE}

    if len(el) >= GATE:
        rho = spearman([r["n"] for r in el], [r["J_days"] for r in el])
        res["P4"] = {"n": len(el), "spearman_N_J": rho, "held": (rho is not None and rho > P4_RHO)}
    else:
        res["P4"] = {"n": len(el), "held": None, "note": "not testable: fewer than %d" % GATE}

    y24 = [r["S_days"] for r in s_rows if r["year"] == 2024]
    y26 = [r["S_days"] for r in s_rows if r["year"] == 2026]
    if len(y24) >= GATE_YEAR and len(y26) >= GATE_YEAR:
        m24, m26 = _med(y24), _med(y26)
        res["P5"] = {"n_2024": len(y24), "n_2026": len(y26), "median_S_2024": m24,
                     "median_S_2026": m26, "held": m26 > m24}
    else:
        res["P5"] = {"n_2024": len(y24), "n_2026": len(y26), "held": None,
                     "note": "not testable: fewer than %d in a year" % GATE_YEAR}
    return res


def describe(rows):
    """Descriptive only; grades nothing."""
    el = [r for r in rows if r["eligible"]]
    out = {"reasons": dict(Counter(r["reason"] for r in rows))}
    by_year = {}
    for y in sorted({r["year"] for r in el if r["year"] is not None}):
        ys = [r for r in el if r["year"] == y]
        s = [r["S_days"] for r in ys if r["S_days"] is not None]
        by_year[str(y)] = {"n": len(ys), "median_N": _med(r["n"] for r in ys),
                           "median_J_days": _med(r["J_days"] for r in ys),
                           "n_with_S": len(s), "median_S_days": _med(s),
                           "n_v3": sum(1 for r in ys if r["v3"])}
    out["by_year"] = by_year
    out["J_le_0"] = sum(1 for r in el if r["J_days"] <= 0)
    out["S_lt_J"] = sum(1 for r in el if r["S_days"] is not None and r["S_days"] < r["J_days"])
    out["window_seconds_top"] = [[w, c] for w, c in Counter(r["W_s"] for r in el).most_common(8)]
    v3 = [r for r in el if r["v3"]]
    out["v3_median_J_minus_doc_days"] = _med(r["J_days"] - doc_days(r["n"]) for r in v3)
    out["escalations_closed_within_21d_of_end"] = sum(
        1 for r in el if r["J_days"] + r["W_s"] / DAY <= 21.0)
    out["n_eligible_all"] = len(el)
    return out


# ---------------------------------------------------------------- network

def http_json(url, tries=4):
    last = None
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 404):
                return None
            last = "HTTP %d" % e.code
        except Exception as e:  # reported, never hidden
            last = repr(e)
        _sleep(5 * (a + 1))
    raise RuntimeError("fetch failed: %s: %s" % (url, last))


def prereg_commit(polls=45, wait_s=120):
    """Wait until the pre-registration is public; return the oldest commit that touched it."""
    url = REPO_API + "/commits?path=" + PREREG_PATH + "&per_page=100"
    last = None
    for i in range(polls):
        try:
            data = http_json(url)
        except RuntimeError as e:
            data, last = None, str(e)
        if isinstance(data, list) and data:
            first = data[-1]
            commit = first.get("commit") or {}
            return {"public": True, "sha": first.get("sha"),
                    "date": (commit.get("committer") or {}).get("date"), "polls": i + 1}
        if i < polls - 1:
            _sleep(wait_s)
    return {"public": False, "polls": polls, "last_error": last}


def fetch_ids():
    ids, page, total = [], 1, None
    while page <= 200:
        d = http_json(API + "/contests?status=FINISHED&page=%d" % page)
        if not d:
            break
        total = d.get("total")
        for it in d.get("items") or []:
            i = _int(it.get("id"))
            if i is not None:
                ids.append(i)
        if not d.get("has_next"):
            break
        page += 1
        _sleep(PAUSE_S)
    return sorted(set(ids)), total


def fetch_details(ids):
    recs, missing = [], []
    for i in ids:
        d = http_json(API + "/contests/%d" % i)
        if not isinstance(d, dict):
            missing.append(i)
        else:
            recs.append({k: d.get(k) for k in KEEP})
        _sleep(PAUSE_S)
    return recs, missing


def iso(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if ts is not None else ""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--polls", type=int, default=45)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    summary = {"job": "sherlock-judging-duration", "prereg_path": PREREG_PATH}

    gate = prereg_commit(polls=args.polls)
    summary["prereg"] = gate
    if not gate["public"]:
        summary["outcome"] = "stopped: pre-registration not public; nothing fetched or computed"
        with open(os.path.join(args.out_dir, "summary.json"), "w") as fh:
            json.dump(summary, fh, indent=1, sort_keys=True)
        print(summary["outcome"])
        return 3

    summary["fetch_started_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids, total = fetch_ids()
    recs, missing = fetch_details(ids)
    summary["fetch_finished_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    summary["api_total_finished"] = total
    summary["ids_listed"] = len(ids)
    summary["details_fetched"] = len(recs)
    summary["details_missing"] = missing

    rows = [row_from(r) for r in recs]
    rows = [r for r in rows if r["id"] is not None]
    summary["grade_confirmatory"] = grade(rows, exclude=SEEN_IDS)
    summary["grade_including_seen"] = grade(rows, exclude=frozenset())
    summary["descriptive"] = describe(rows)
    summary["outcome"] = "graded"

    cols = ["id", "title", "eligible", "reason", "seen_before_registration", "v3", "n", "doc_days",
            "ends_at_utc", "J_days", "W_s", "S_days", "year"]
    with open(os.path.join(args.out_dir, "contests.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in sorted(rows, key=lambda x: x["id"]):
            w.writerow([r["id"], r["title"], r["eligible"], r["reason"], r["id"] in SEEN_IDS, r["v3"],
                        r["n"] if r["n"] is not None else "",
                        doc_days(r["n"]) if (r["n"] or 0) > 0 else "",
                        iso(r["end"]),
                        "" if r["J_days"] is None else "%.4f" % r["J_days"],
                        "" if r["W_s"] is None else r["W_s"],
                        "" if r["S_days"] is None else "%.4f" % r["S_days"],
                        r["year"] if r["year"] is not None else ""])
    with open(os.path.join(args.out_dir, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    print(json.dumps(summary["grade_confirmatory"], indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
