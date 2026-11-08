# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working for MV2 of Munim, Inc.
"""Stage 3 of the archived-page route: the Cantina judging-duration census itself (v2).

Pre-registration: paper/cantina-judging-duration-PREREGISTRATION.md (a7589cc), first addendum
paper/cantina-judging-duration-pages-ADDENDUM.md (3afce4e), second addendum
paper/cantina-judging-duration-pages-ADDENDUM-2.md (3175183, the fixed extraction rule) and third
addendum paper/cantina-judging-duration-pages-ADDENDUM-3.md (the input-rebuild rule) in
github.com/munimtechnologies/audit-contest-ai-rules. This job refuses to compute anything (exit 3)
until the second and third addenda are both public on GitHub.

Route "stage-2 cache" (the host that ran stages 1 and 2): reads the stage-1 inputs and the stage-2
page cache in /data, fetches no archived page, applies the rule exactly, grades P1-P5.

Route "rebuilt" (v1 landed on a host whose /data volume lacks those inputs): rebuilds them as the
third addendum says, i.e. the competition list from the published stage-1 table (pinned by its git
blob sha), the capture index from the Wayback CDX cut off at the stage-1 read time, and the pages with
stage 2's own fetcher, then checks the rebuild against the published stage-1 and stage-2 counts. Only
a matching rebuild is graded as the pre-registered census; otherwise the output is descriptive only.
The extraction rule, brackets and grading are unchanged from v1.
"""
import argparse
import base64
import collections
import csv
import gzip
import hashlib
import io
import json
import math
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

CONTENTS = "https://api.github.com/repos/munimtechnologies/audit-contest-ai-rules/contents/"
ADDENDA = {
    "addendum_2": CONTENTS + "paper/cantina-judging-duration-pages-ADDENDUM-2.md",
    "addendum_3": CONTENTS + "paper/cantina-judging-duration-pages-ADDENDUM-3.md",
}
# cantina_judging/bound/bounds_by_id.csv as published with stage 1 (commit d0ff01d)
BOUND_BLOB_SHA = "b7d84243f3a20ebe129061b4ca6f77d39337e09d"
BOUND_BLOB = "https://api.github.com/repos/munimtechnologies/audit-contest-ai-rules/git/blobs/" + BOUND_BLOB_SHA
CDX = "https://web.archive.org/cdx/search/cdx"
WAYBACK = "https://web.archive.org/web/%sid_/%s"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com; judging-duration census, Apache-2.0)"
UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
MAIN_RE = re.compile(r"^/competitions/(%s)/?$" % UUID, re.I)
ANY_RE = re.compile(r"^/competitions/(%s)(/.*)?$" % UUID, re.I)
STAMP_DEFAULT = "20261107T121430Z"
DAY = 86400.0
COMPLETION_MAX_DAYS = 14.0
START_MAX_DAYS = 3.0
P3_UPPER_DAYS = 7.0
GATE = 20
SKIP_TAGS = {"script", "style", "noscript", "template", "svg"}
STATUS_RE = re.compile(r"^status\s*:?\s*(.*)$")
COUNT_LABELS = {"findings submitted", "findings submitted:"}
INT_RE = re.compile(r"^(\d{1,3}(,\d{3})+|\d+)$")
JSON_STATUS_RE = re.compile(r'\\*"status\\*"\s*:\s*\\*"([^"\\]{1,40})\\*"')
JSON_TOTAL_RE = re.compile(r'\\*"totalFindings\\*"\s*:\s*(\d+)')
JSON_KNOWN = {"live": "live", "complete": "complete", "completed": "complete", "judging": "post-live",
              "escalations": "post-live", "escalations_ended": "post-live"}
# Published stage-1 and stage-2 counts the rebuild must reproduce (ADDENDUM-3).
STAGE1_CDX_ROWS = 1689
STAGE2 = {"captures_selected": 882, "cached": 882, "status_read": 528, "json_status": 528, "redirected": 11}
PAUSE_S = 4.0
_sleep = time.sleep


# ---------------------------------------------------------------- gate: addenda public

def addendum_is_public(polls=30, wait_s=120):
    """Both the second and the third addendum must be public before anything is computed."""
    out = {"public": False, "polls": 0}
    pending = dict(ADDENDA)
    last = None
    for i in range(polls):
        out["polls"] = i + 1
        for key, url in sorted(pending.items()):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                           "Accept": "application/vnd.github+json"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    meta = json.loads(r.read().decode("utf-8", "replace"))
                out[key + "_sha"] = meta.get("sha")
                del pending[key]
            except urllib.error.HTTPError as e:
                last = "HTTP %d" % e.code
            except Exception as e:  # reported, never hidden
                last = repr(e)
        if not pending:
            out["public"] = True
            return out
        if i < polls - 1:
            _sleep(wait_s)
    out["missing"] = sorted(pending)
    out["last_error"] = last
    return out


# ---------------------------------------------------------------- inputs

def parse_ts(ts):
    if not ts or len(ts) < 14 or not str(ts)[:14].isdigit():
        return None
    return datetime.strptime(str(ts)[:14], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)


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


def iso(d):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ") if d else ""


def url_id(original, regex):
    try:
        parts = urllib.parse.urlsplit(original or "")
    except ValueError:
        return None
    if (parts.hostname or "").lower() not in ("cantina.xyz", "www.cantina.xyz"):
        return None
    m = regex.match(parts.path or "")
    return m.group(1).lower() if m else None


def comps_from_api(data):
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list) and v and isinstance(v[0], dict) and "id" in v[0]:
                data = v
                break
        else:
            data = []
    out = {}
    for c in data if isinstance(data, list) else []:
        if not isinstance(c, dict) or not c.get("id"):
            continue
        tf = c.get("timeframe") or {}
        end = parse_iso(tf.get("end")) if isinstance(tf, dict) else None
        tfind = c.get("totalFindings")
        if isinstance(tfind, bool):
            tfind = None
        elif isinstance(tfind, str) and tfind.strip().isdigit():
            tfind = int(tfind.strip())
        elif not isinstance(tfind, int):
            tfind = None
        out[str(c["id"]).lower()] = {"end": end, "status_now": c.get("status"), "final_count": tfind}
    return out


def select_captures(cdx_rows, comps, read_at):
    """[(id, ts14, original)] for HTTP-200 main-page captures strictly after E, competitions ended by read_at."""
    if not cdx_rows:
        return []
    head = cdx_rows[0]
    seen = {}
    for r in cdx_rows[1:]:
        row = dict(zip(head, r))
        if row.get("statuscode") != "200":
            continue
        cid = url_id(row.get("original"), MAIN_RE)
        t = parse_ts(row.get("timestamp"))
        if not cid or not t or cid not in comps or comps[cid]["end"] is None:
            continue
        e = comps[cid]["end"]
        if e > read_at or t <= e:
            continue
        key = (cid, row["timestamp"][:14])
        if key not in seen:
            seen[key] = row["original"]
    return sorted((k[0], k[1], v) for k, v in seen.items())


def coverage_start(cdx_rows):
    """Earliest HTTP-200 capture anywhere under cantina.xyz/competitions/ (with an id)."""
    if not cdx_rows:
        return None
    head = cdx_rows[0]
    best = None
    for r in cdx_rows[1:]:
        row = dict(zip(head, r))
        if row.get("statuscode") != "200" or not url_id(row.get("original"), ANY_RE):
            continue
        t = parse_ts(row.get("timestamp"))
        if t and (best is None or t < best):
            best = t
    return best


def load_index(pages_dir):
    idx = {}
    p = os.path.join(pages_dir, "index.jsonl")
    if not os.path.exists(p):
        return idx
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("id") and d.get("ts"):
                idx[(str(d["id"]).lower(), str(d["ts"])[:14])] = d.get("final_ts")
    return idx


def cache_path(pages_dir, cid, ts):
    return os.path.join(pages_dir, "%s_%s.html.gz" % (cid, ts))


# ---------------------------------------------------------------- rebuild route (third addendum)

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
            _sleep(10 * (i + 1))
    raise RuntimeError("fetch failed after %d tries: %s: %s" % (tries, url, last))


def git_blob_sha(content):
    return hashlib.sha1(b"blob %d\0" % len(content) + content).hexdigest()


def bound_table_from_blob(raw, expected_sha):
    """Rows of the published stage-1 table; refuses a blob whose git sha is not the pinned one."""
    meta = json.loads(raw.decode("utf-8", "replace"))
    content = base64.b64decode(meta.get("content") or "")
    got = git_blob_sha(content)
    if got != expected_sha:
        raise ValueError("stage-1 table blob sha %s != pinned %s" % (got, expected_sha))
    return list(csv.DictReader(io.StringIO(content.decode("utf-8", "replace"))))


def _int(s):
    s = (s or "").strip()
    return int(s) if s.isdigit() else None


def comps_from_bound(table):
    """Same fields comps_from_api gives, from the stage-1 table (ended competitions only)."""
    out = {}
    for r in table:
        cid = (r.get("id") or "").strip().lower()
        if cid:
            out[cid] = {"end": parse_iso((r.get("end") or "").strip()), "status_now": r.get("status_now") or None,
                        "final_count": _int(r.get("totalFindings"))}
    return out


def stage1_counts(table):
    return {(r.get("id") or "").strip().lower(): (_int(r.get("main_captures_200")), _int(r.get("main_after_end")))
            for r in table if (r.get("id") or "").strip()}


def cdx_query_url(read_at):
    q = {"url": "cantina.xyz/competitions/", "matchType": "prefix", "output": "json",
         "fl": "timestamp,original,statuscode,mimetype,length", "limit": "50000",
         "to": read_at.strftime("%Y%m%d%H%M%S")}
    return CDX + "?" + urllib.parse.urlencode(q)


def main_times_by_id(cdx_rows):
    out = collections.defaultdict(set)
    if not cdx_rows:
        return {}
    head = cdx_rows[0]
    for r in cdx_rows[1:]:
        row = dict(zip(head, r))
        if row.get("statuscode") != "200":
            continue
        cid = url_id(row.get("original"), MAIN_RE)
        t = parse_ts(row.get("timestamp"))
        if cid and t:
            out[cid].add(t)
    return {k: sorted(v) for k, v in out.items()}


def reconcile_cdx(cdx_rows, comps, stage1):
    """(rows to use, report). Per competition, the rebuilt main-page capture counts (all, after E) must
    equal stage 1's. The only adjustment allowed: when the rebuild has k more main-page captures and
    dropping that competition's newest k makes both counts equal (archive index lag), those k are dropped
    and counted. Any other difference means the rebuild does not match."""
    times = main_times_by_id(cdx_rows)
    drop = {}
    diffs = []
    for cid, (n_all, n_after) in sorted(stage1.items()):
        ts = times.get(cid, [])
        end = (comps.get(cid) or {}).get("end")
        if end is None or n_all is None or n_after is None:
            diffs.append({"id": cid, "why": "no end or no stage-1 count"})
            continue
        k = len(ts) - n_all
        kept = ts[:-k] if k > 0 else ts
        after = sum(1 for t in kept if t > end)
        if k >= 0 and after == n_after:
            if k > 0:
                drop[cid] = {t.strftime("%Y%m%d%H%M%S") for t in ts[-k:]}
            continue
        diffs.append({"id": cid, "stage1_main": n_all, "rebuilt_main": len(ts), "stage1_after_end": n_after,
                      "rebuilt_after_end": sum(1 for t in ts if t > end)})
    rows = cdx_rows[:1]
    head = cdx_rows[0] if cdx_rows else []
    for r in cdx_rows[1:]:
        row = dict(zip(head, r))
        cid = url_id(row.get("original"), MAIN_RE)
        if (row.get("statuscode") == "200" and cid in drop
                and str(row.get("timestamp"))[:14] in drop[cid]):
            continue
        rows.append(r)
    dropped_ts = sorted(t for v in drop.values() for t in v)
    report = {"rows_stage1": STAGE1_CDX_ROWS, "rows_rebuilt": max(len(cdx_rows) - 1, 0),
              "rows_after_drop": max(len(rows) - 1, 0), "dropped_newest_captures": len(dropped_ts),
              "dropped_competitions": len(drop), "dropped_oldest_ts": dropped_ts[0] if dropped_ts else "",
              "n_differences": len(diffs), "differences": diffs[:40], "matched": not diffs}
    return rows, report


def fetch(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.geturl(), r.headers.get("Content-Type", ""), r.read()


def get_capture(pages_dir, index_f, cid, ts, original, stats):
    """Stage 2's fetcher, unchanged in behaviour: raw capture, gzipped into the cache, one index line."""
    p = cache_path(pages_dir, cid, ts)
    if os.path.exists(p):
        stats["from_cache"] += 1
        return True
    url = WAYBACK % (ts, original)
    for attempt in range(5):
        try:
            code, final, ctype, body = fetch(url)
            stats["http_%d" % code] += 1
            final_ts = None
            m = re.search(r"/web/(\d{14})", final or "")
            if m:
                final_ts = m.group(1)
            stats["ctype:" + (ctype.split(";")[0].strip().lower() or "none")] += 1
            with gzip.open(p, "wb") as f:
                f.write(body)
            index_f.write(json.dumps({"id": cid, "ts": ts, "final_ts": final_ts, "bytes": len(body),
                                      "ctype": ctype}) + "\n")
            index_f.flush()
            stats["fetched"] += 1
            stats["bytes"] += len(body)
            _sleep(PAUSE_S)
            return True
        except urllib.error.HTTPError as e:
            stats["http_error_%d" % e.code] += 1
            if e.code in (429, 503, 502, 504):
                _sleep(30 * (attempt + 1))
                continue
            _sleep(PAUSE_S)
            return False
        except Exception:
            stats["network_error"] += 1
            _sleep(15 * (attempt + 1))
    return False


def rebuild_pages(caps, pages_dir, budget_minutes):
    os.makedirs(pages_dir, exist_ok=True)
    stats = collections.Counter()
    started = time.time()
    in_a_row = 0
    done = 0
    stopped = ""
    with open(os.path.join(pages_dir, "index.jsonl"), "a") as index_f:
        for cid, ts, original in caps:
            if time.time() - started > budget_minutes * 60:
                stopped = "time budget reached"
                break
            if in_a_row >= 20:
                stopped = "20 failures in a row (archive refusing or unreachable)"
                break
            ok = get_capture(pages_dir, index_f, cid, ts, original, stats)
            done += 1
            in_a_row = 0 if ok else in_a_row + 1
            if not ok:
                stats["failed"] += 1
            if done % 100 == 0:
                print("progress: %d of %d captures handled" % (done, len(caps)), flush=True)
    return {"handled": done, "stopped_early": stopped, "fetch_stats": dict(sorted(stats.items()))}


def stage2_check(caps, pages_dir):
    """Stage 2's published counts over the selected captures, recomputed from the cache in use."""
    index = load_index(pages_dir)
    n = collections.Counter()
    for cid, ts, _ in caps:
        p = cache_path(pages_dir, cid, ts)
        if not os.path.exists(p):
            continue
        n["cached"] += 1
        f_ts = index.get((cid, ts))
        if f_ts and f_ts != ts:
            n["redirected"] += 1
        with gzip.open(p, "rb") as f:
            x = extract(f.read().decode("utf-8", "replace"))
        n["status_read"] += int(bool(x["text_status"]))
        n["json_status"] += int(bool(x["json_values"]))
    got = {"captures_selected": len(caps), "cached": n["cached"], "status_read": n["status_read"],
           "json_status": n["json_status"], "redirected": n["redirected"]}
    return {"expected": dict(STAGE2), "got": got, "matched": got == STAGE2}


# ---------------------------------------------------------------- extraction (second addendum)

class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if self.skip:
            return
        s = " ".join(data.split())
        if s:
            self.chunks.append(s)


def text_chunks(html):
    p = _Text()
    try:
        p.feed(html)
        p.close()
    except Exception:  # malformed markup: keep what was parsed
        pass
    return p.chunks


def class_of(value):
    v = " ".join((value or "").split()).lower()
    if v == "live":
        return "live"
    if v in ("complete", "completed"):
        return "complete"
    return "post-live"


def extract(html):
    chunks = text_chunks(html)
    vals = []
    for i, c in enumerate(chunks):
        m = STATUS_RE.match(c.lower())
        if m:
            rest = m.group(1).strip()
            nxt = rest or (chunks[i + 1] if i + 1 < len(chunks) else "")
            nxt = " ".join(nxt.split()).lower()
            if nxt:
                vals.append(nxt)
    text_count = None
    for i, c in enumerate(chunks):
        if " ".join(c.split()).lower() in COUNT_LABELS and i + 1 < len(chunks):
            nxt = chunks[i + 1].strip()
            if INT_RE.match(nxt):
                text_count = int(nxt.replace(",", ""))
                break
    json_vals = sorted({m.group(1) for m in JSON_STATUS_RE.finditer(html)})
    json_classes = sorted({JSON_KNOWN[v.lower()] for v in json_vals if v.lower() in JSON_KNOWN})
    totals = sorted({int(m.group(1)) for m in JSON_TOTAL_RE.finditer(html)})
    return {"text_status": sorted(set(vals)), "first_status": vals[0] if vals else None, "text_count": text_count,
            "json_values": json_vals, "json_classes": json_classes,
            "json_count": totals[0] if len(totals) == 1 else None, "json_count_distinct": len(totals)}


def read_capture(html):
    """(record, None) for a readable capture, or (None, exclusion reason)."""
    x = extract(html)
    if not x["text_status"]:
        return None, "no status", x
    if len(x["text_status"]) > 1:
        return None, "ambiguous status", x
    cls = class_of(x["text_status"][0])
    if len(x["json_classes"]) == 1 and x["json_classes"][0] != cls:
        return None, "text and JSON disagree", x
    json_check = "agree" if len(x["json_classes"]) == 1 else ("none" if not x["json_classes"] else "several")
    if x["text_count"] is not None:
        count, src = x["text_count"], "text"
    elif x["json_count"] is not None:
        count, src = x["json_count"], "json"
    else:
        count, src = None, ""
    return {"status": x["text_status"][0], "class": cls, "count": count, "count_source": src,
            "json_check": json_check}, None, x


# ---------------------------------------------------------------- brackets and grading

def days(a, b):
    return (b - a).total_seconds() / DAY


def analyse(end, caps):
    """caps: sorted [(time, class, count)] of readable captures strictly after end, distinct times."""
    r = {"n_readable_after_end": len(caps), "first_complete_days": None, "completion_lower_days": None,
         "completion_upper_days": None, "completion_width_days": None, "completion_midpoint_days": None,
         "start_lower_hours": None, "start_upper_hours": None, "start_width_days": None,
         "has_noncomplete": False, "earliest_noncomplete_count": None, "reversal": False}
    first_complete = next((t for t, c, n in caps if c == "complete"), None)
    if first_complete is not None:
        before = [t for t, c, n in caps if t < first_complete]
        lower = before[-1] if before else end
        lo, up = days(end, lower), days(end, first_complete)
        r.update({"first_complete_days": up, "completion_lower_days": lo, "completion_upper_days": up,
                  "completion_width_days": up - lo, "completion_midpoint_days": (lo + up) / 2.0,
                  "reversal": any(c != "complete" and t > first_complete for t, c, n in caps)})
    first_moved = next((t for t, c, n in caps if c in ("post-live", "complete")), None)
    if first_moved is not None:
        lives = [t for t, c, n in caps if c == "live" and t < first_moved]
        slower = lives[-1] if lives else end
        r.update({"start_lower_hours": days(end, slower) * 24.0, "start_upper_hours": days(end, first_moved) * 24.0,
                  "start_width_days": days(slower, first_moved)})
    noncomplete = [(t, c, n) for t, c, n in caps if c != "complete"]
    if noncomplete:
        r["has_noncomplete"] = True
        r["earliest_noncomplete_count"] = noncomplete[0][2]
    return r


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[order[k]] = avg
        i = j + 1
    return out


def spearman(x, y):
    if len(x) != len(y) or len(x) < 3:
        return None
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    if vx == 0 or vy == 0:
        return None
    return cov / math.sqrt(vx * vy)


def _nt(why):
    return {"grade": "not testable", "why": why}


def grade(rows):
    elig = [r for r in rows if r["eligible"]]
    g = {"eligible": len(elig), "gate": GATE, "gate_passed": len(elig) >= GATE}
    if not g["gate_passed"]:
        for p in ("P1", "P2", "P3", "P4", "P5"):
            g[p] = _nt("gate: %d eligible < %d" % (len(elig), GATE))
        return g
    mids = [r["completion_midpoint_days"] for r in elig]
    med = statistics.median(mids)
    g["P1"] = {"grade": "held" if 21.0 <= med <= 90.0 else "failed", "median_midpoint_days": round(med, 3),
               "n": len(mids), "rule": "median completion midpoint in [21, 90] days"}
    pairs = [(r["final_count"], r["completion_midpoint_days"]) for r in elig if isinstance(r["final_count"], int)]
    rho = spearman([a for a, b in pairs], [b for a, b in pairs])
    g["P2"] = (_nt("fewer than 3 pairs or no variation") if rho is None else
               {"grade": "held" if rho >= 0.20 else "failed", "spearman": round(rho, 4), "n": len(pairs),
                "rule": "Spearman(final totalFindings, midpoint) >= +0.20"})
    s = [r for r in rows if r["start_width_days"] is not None and r["start_width_days"] <= START_MAX_DAYS]
    if not s:
        g["P3"] = _nt("no judging-start bracket at most 3 days wide")
    else:
        k = sum(1 for r in s if r["start_upper_hours"] <= P3_UPPER_DAYS * 24.0)
        g["P3"] = {"grade": "held" if k / len(s) >= 0.80 else "failed", "n": len(s), "upper_le_7d": k,
                   "share": round(k / len(s), 4), "rule": ">= 80% of start brackets <= 3 d have upper <= 7 d"}
    y26 = [r["completion_midpoint_days"] for r in elig if r["end_year"] == 2026]
    y24 = [r["completion_midpoint_days"] for r in elig if r["end_year"] == 2024]
    if len(y26) < 5 or len(y24) < 5:
        g["P4"] = _nt("eligible by year: 2026 %d, 2024 %d (need 5 each)" % (len(y26), len(y24)))
    else:
        m26, m24 = statistics.median(y26), statistics.median(y24)
        g["P4"] = {"grade": "held" if m26 > m24 else "failed", "median_2026": round(m26, 3), "n_2026": len(y26),
                   "median_2024": round(m24, 3), "n_2024": len(y24), "rule": "2026 median midpoint > 2024"}
    cands = [r for r in rows if r["has_noncomplete"]]
    usable = [r for r in cands if r["earliest_noncomplete_count"] is not None and isinstance(r["final_count"], int)]
    if not usable:
        g["P5"] = _nt("no competition with a readable count in a non-complete capture after E")
    else:
        k = sum(1 for r in usable if r["earliest_noncomplete_count"] < r["final_count"])
        g["P5"] = {"grade": "held" if k / len(usable) >= 0.5 else "failed", "n": len(usable),
                   "excluded_count_unreadable": len(cands) - len(usable), "lower_than_final": k,
                   "share": round(k / len(usable), 4), "rule": ">= half show earliest non-complete count < final"}
    return g


# ---------------------------------------------------------------- main

def _r(x, nd=3):
    return "" if x is None else round(x, nd)


def run_census(cdx_rows, comps, pages_dir, read_at):
    caps = select_captures(cdx_rows, comps, read_at)
    index = load_index(pages_dir)
    cov = coverage_start(cdx_rows)
    excl = collections.Counter()
    vocab_text, vocab_json = collections.Counter(), collections.Counter()
    checks = collections.Counter()
    by_id = collections.defaultdict(dict)
    capture_rows = []
    for cid, ts, original in caps:
        end = comps[cid]["end"]
        final_ts = index.get((cid, ts))
        served = parse_ts(final_ts) if final_ts else parse_ts(ts)
        row = {"id": cid, "requested_ts": ts, "served_ts": iso(served), "status": "", "class": "", "count": "",
               "count_source": "", "excluded": ""}
        p = cache_path(pages_dir, cid, ts)
        if not os.path.exists(p):
            row["excluded"] = "not in stage-2 cache"
        elif served is None or served <= end:
            row["excluded"] = "served capture not after end"
        else:
            with gzip.open(p, "rb") as f:
                html = f.read().decode("utf-8", "replace")
            rec, why, x = read_capture(html)
            for v in x["text_status"]:
                vocab_text[v] += 1
            for v in x["json_values"]:
                vocab_json[v] += 1
            if rec is None:
                row["excluded"] = why
            elif served in by_id[cid]:
                row["excluded"] = "duplicate served time"
            else:
                by_id[cid][served] = (rec["class"], rec["count"])
                row.update({"status": rec["status"], "class": rec["class"],
                            "count": "" if rec["count"] is None else rec["count"],
                            "count_source": rec["count_source"]})
                checks["json_check_" + rec["json_check"]] += 1
                if x["text_count"] is not None and x["json_count"] is not None:
                    checks["count_text_json_both"] += 1
                    checks["count_text_json_equal"] += int(x["text_count"] == x["json_count"])
        if row["excluded"]:
            excl[row["excluded"]] += 1
        capture_rows.append(row)
    rows = []
    for cid, c in sorted(comps.items()):
        if c["end"] is None or c["end"] > read_at:
            continue
        caps_c = sorted((t, v[0], v[1]) for t, v in by_id.get(cid, {}).items())
        a = analyse(c["end"], caps_c)
        eligible = (a["completion_width_days"] is not None and a["completion_width_days"] <= COMPLETION_MAX_DAYS
                    and cov is not None and c["end"] >= cov)
        rows.append(dict(a, id=cid, end=c["end"], end_year=c["end"].year, status_now=c["status_now"],
                         final_count=c["final_count"], eligible=eligible))
    months = collections.defaultdict(set)
    for r in capture_rows:
        if not r["excluded"]:
            months[r["served_ts"][:7]].add(r["served_ts"][:10])
    info = {"captures_selected": len(caps), "captures_readable": sum(1 for r in capture_rows if not r["excluded"]),
            "excluded": dict(sorted(excl.items())), "checks": dict(sorted(checks.items())),
            "coverage_start": iso(cov), "status_values_text": dict(vocab_text.most_common()),
            "status_values_json": dict(vocab_json.most_common()),
            "capture_days_per_month": {k: len(v) for k, v in sorted(months.items())},
            "competitions_ended": len(rows),
            "competitions_with_readable_capture": sum(1 for r in rows if r["n_readable_after_end"]),
            "competitions_with_complete_capture": sum(1 for r in rows if r["first_complete_days"] is not None),
            "reversals": sum(1 for r in rows if r["reversal"])}
    return rows, capture_rows, info


BRACKET_FIELDS = ["id", "end", "end_year", "status_now", "final_count", "n_readable_after_end", "eligible",
                  "completion_lower_days", "completion_upper_days", "completion_width_days",
                  "completion_midpoint_days", "start_lower_hours", "start_upper_hours", "start_width_days",
                  "has_noncomplete", "earliest_noncomplete_count", "reversal"]
CAPTURE_FIELDS = ["id", "requested_ts", "served_ts", "status", "class", "count", "count_source", "excluded"]


def write_outputs(out_dir, rows, capture_rows, summary):
    with open(os.path.join(out_dir, "brackets_by_id.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=BRACKET_FIELDS)
        w.writeheader()
        for r in rows:
            d = {k: r.get(k) for k in BRACKET_FIELDS}
            d["end"] = iso(r["end"])
            for k in ("completion_lower_days", "completion_upper_days", "completion_width_days",
                      "completion_midpoint_days", "start_lower_hours", "start_upper_hours", "start_width_days"):
                d[k] = _r(r.get(k))
            d["final_count"] = "" if r.get("final_count") is None else r["final_count"]
            d["earliest_noncomplete_count"] = ("" if r.get("earliest_noncomplete_count") is None
                                               else r["earliest_noncomplete_count"])
            w.writerow(d)
    with open(os.path.join(out_dir, "captures.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAPTURE_FIELDS)
        w.writeheader()
        w.writerows(capture_rows)
    _write(out_dir, summary)


def _write(out_dir, summary):
    with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)


def rebuild_inputs(data_dir, stamp, read_at, budget_minutes):
    """Third-addendum route. Returns (cdx_rows, comps, pages_dir, report)."""
    table = bound_table_from_blob(fetch_bytes(BOUND_BLOB, accept="application/vnd.github+json"), BOUND_BLOB_SHA)
    comps = comps_from_bound(table)
    url = cdx_query_url(read_at)
    raw = fetch_bytes(url)
    cdx_raw = json.loads(raw.decode("utf-8", "replace").strip() or "[]")
    cdx_rows, cdx_report = reconcile_cdx(cdx_raw, comps, stage1_counts(table))
    cdx_report["query"] = url
    cdx_report["stage1_table_rows"] = len(table)
    pages_dir = os.path.join(data_dir, "rebuild-%s" % stamp, "pages")
    caps = select_captures(cdx_rows, comps, read_at)
    pages_report = rebuild_pages(caps, pages_dir, budget_minutes)
    return cdx_rows, comps, pages_dir, {"cdx": cdx_report, "pages": pages_report}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--stamp", default=STAMP_DEFAULT)
    ap.add_argument("--polls", type=int, default=30)
    ap.add_argument("--wait-s", type=float, default=120.0)
    ap.add_argument("--budget-minutes", type=float, default=200.0)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    summary = {"note": "Stage 3 (v2): the second addendum's rule; inputs from the stage-2 cache, or rebuilt as "
                       "the third addendum says when this host lacks them.",
               "started": iso(datetime.now(timezone.utc)), "inputs_stamp": a.stamp}
    pre = addendum_is_public(a.polls, a.wait_s)
    summary["addenda"] = pre
    if not pre["public"]:
        summary["stopped"] = "second or third addendum not public on GitHub; nothing computed"
        _write(a.out_dir, summary)
        print(json.dumps(summary, indent=1))
        return 3
    read_at = datetime.strptime(a.stamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    cdx_p = os.path.join(a.data_dir, "cdx_pages_%s.json" % a.stamp)
    api_p = os.path.join(a.data_dir, "api_competitions_%s.json" % a.stamp)
    pages_dir = os.path.join(a.data_dir, "pages")
    if os.path.exists(cdx_p) and os.path.exists(api_p) and os.path.isdir(pages_dir):
        summary["inputs_route"] = "stage-2 cache"
        with open(cdx_p, "rb") as f:
            cdx_rows = json.loads(f.read().decode("utf-8", "replace").strip() or "[]")
        with open(api_p, "rb") as f:
            comps = comps_from_api(json.loads(f.read().decode("utf-8", "replace")))
        rebuild = None
    else:
        summary["inputs_route"] = "rebuilt"
        try:
            cdx_rows, comps, pages_dir, rebuild = rebuild_inputs(a.data_dir, a.stamp, read_at, a.budget_minutes)
        except Exception as e:  # reported, never hidden
            summary["stopped"] = "stage 1 or stage 2 inputs missing in /data and the rebuild failed: %s" % repr(e)[:400]
            _write(a.out_dir, summary)
            print(json.dumps(summary, indent=1))
            return 4
        summary["rebuild"] = rebuild
    caps = select_captures(cdx_rows, comps, read_at)
    summary["stage2_check"] = stage2_check(caps, pages_dir)
    if rebuild is None:
        summary["inputs_match"] = None
        summary["grades_status"] = "pre-registered census (stage-2 cache)"
    else:
        summary["inputs_match"] = bool(rebuild["cdx"]["matched"] and summary["stage2_check"]["matched"])
        summary["grades_status"] = ("pre-registered census (rebuilt inputs match stage 1 and stage 2)"
                                    if summary["inputs_match"] else
                                    "descriptive only: rebuilt inputs differ from stage 1 or stage 2 (ADDENDUM-3)")
    rows, capture_rows, info = run_census(cdx_rows, comps, pages_dir, read_at)
    summary.update(info)
    summary["grades"] = grade(rows)
    summary["finished"] = iso(datetime.now(timezone.utc))
    write_outputs(a.out_dir, rows, capture_rows, summary)
    print(json.dumps({k: summary.get(k) for k in ("inputs_route", "inputs_match", "grades_status",
                                                  "captures_selected", "captures_readable", "excluded",
                                                  "competitions_with_complete_capture", "grades")},
                     indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
