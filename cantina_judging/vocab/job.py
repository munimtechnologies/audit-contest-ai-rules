# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working for MV2 of Munim, Inc.
"""Stage 2 of the archived-page route for the Cantina judging-duration census: format vocabulary.

Pre-registration: paper/cantina-judging-duration-PREREGISTRATION.md (6 Nov 2026) and
paper/cantina-judging-duration-pages-ADDENDUM.md (7 Nov 2026) in
github.com/munimtechnologies/audit-contest-ai-rules. Stage 1 (cantina-pages-bound-v1) found an
upper bound of 68 >= gate 20, so this stage runs.

What it does: fetches raw Wayback captures (/web/<timestamp>id_/<original>) of competition MAIN
pages captured after each competition's current API end, one request at a time with a pause,
caches them gzipped in /data for stage 3, and reports ONLY label vocabulary and readability
counts. It never outputs a status or a findings count paired with a capture time or a
competition id: every output is a count over captures. Capture-level detail stays in /data.
"""
import argparse
import collections
import gzip
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

WAYBACK = "https://web.archive.org/web/%sid_/%s"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com; label-vocabulary check, Apache-2.0)"
UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
MAIN_RE = re.compile(r"^/competitions/(%s)/?$" % UUID, re.I)
STAMP_DEFAULT = "20261107T121430Z"  # stage 1 inputs saved in /data
PAUSE_S = 4.0
MAX_TOKEN = 60
TOP_N = 150
STATUS_WORDS = ["live", "judging", "complete", "completed", "ended", "upcoming", "escalation", "escalations",
                "finalized", "final", "results", "in review", "awarded", "paused", "closed", "open"]
SKIP_TAGS = {"script", "style", "noscript", "template", "svg"}
NUMBER_RE = re.compile(r"^[\d][\d,\.]*\s*[kKmM]?$")
JSON_STATUS_RE = re.compile(r'\\*"status\\*"\s*:\s*\\*"([^"\\]{1,40})\\*"')
JSON_FKEY_RE = re.compile(r'\\*"([A-Za-z_]*(?:[Ff]inding|[Ss]ubmission)[A-Za-z_]*)\\*"\s*:\s*(\\*"|-?\d|\{|\[|null|true|false)?')


# ---------------------------------------------------------------- inputs (stage 1 copies in /data)

def parse_ts(ts):
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


def main_id(original):
    try:
        parts = urllib.parse.urlsplit(original or "")
    except ValueError:
        return None
    if (parts.hostname or "").lower() not in ("cantina.xyz", "www.cantina.xyz"):
        return None
    m = MAIN_RE.match(parts.path or "")
    return m.group(1).lower() if m else None


def ends_from_api(data):
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list) and v and isinstance(v[0], dict) and "id" in v[0]:
                data = v
                break
        else:
            data = []
    out = {}
    for c in data if isinstance(data, list) else []:
        if isinstance(c, dict) and c.get("id"):
            tf = c.get("timeframe") or {}
            e = parse_iso(tf.get("end")) if isinstance(tf, dict) else None
            if e is not None:
                out[str(c["id"]).lower()] = e
    return out


def select_captures(cdx_rows, ends, read_at):
    """[(id, ts14, original)] for HTTP-200 main-page captures strictly after the competition's end,
    for competitions that had ended by read_at. One original per (id, timestamp)."""
    if not cdx_rows:
        return []
    head = cdx_rows[0]
    seen = {}
    for r in cdx_rows[1:]:
        row = dict(zip(head, r))
        if row.get("statuscode") != "200":
            continue
        cid = main_id(row.get("original"))
        t = parse_ts(row.get("timestamp"))
        if not cid or not t or cid not in ends:
            continue
        e = ends[cid]
        if e > read_at or t <= e:
            continue
        key = (cid, row["timestamp"][:14])
        if key not in seen:
            seen[key] = row["original"]
    return sorted((k[0], k[1], v) for k, v in seen.items())


# ---------------------------------------------------------------- extraction (vocabulary only)

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


def norm(s):
    """Shape of a token: lower case, digits -> '#', whitespace collapsed, capped length."""
    s = re.sub(r"\d", "#", " ".join(s.split()).lower())
    return s[:MAX_TOKEN]


def capture_vocab(html):
    """Per-capture sets of vocabulary items (each counted once per capture) and readability flags."""
    chunks = text_chunks(html)
    v = {"after_status_label": set(), "finding_or_submission_labels": set(), "after_findings_label_shape": set(),
         "status_words_in_text": set(), "json_status_values": set(), "json_finding_keys": set(),
         "json_finding_key_numeric": set()}
    status_read = False
    count_read = False
    for i, c in enumerate(chunks):
        lc = c.lower()
        m = re.match(r"^status\s*:?\s*(.*)$", lc)
        if m:
            rest = m.group(1).strip()
            nxt = rest or (chunks[i + 1] if i + 1 < len(chunks) else "")
            if nxt:
                v["after_status_label"].add(norm(nxt))
                status_read = True
        if ("finding" in lc or "submission" in lc) and len(c) <= 80:
            v["finding_or_submission_labels"].add(norm(c))
            if len(c) <= 40 and i + 1 < len(chunks):
                nxt = chunks[i + 1]
                shape = "number" if NUMBER_RE.match(nxt.strip()) else "other:" + norm(nxt)[:30]
                v["after_findings_label_shape"].add(norm(c) + " -> " + shape)
                if shape == "number":
                    count_read = True
    text = " \n ".join(chunks).lower()
    for w in STATUS_WORDS:
        if re.search(r"\b%s\b" % re.escape(w), text):
            v["status_words_in_text"].add(w)
    for m in JSON_STATUS_RE.finditer(html):
        v["json_status_values"].add(norm(m.group(1)))
    for m in JSON_FKEY_RE.finditer(html):
        v["json_finding_keys"].add(m.group(1)[:MAX_TOKEN])
        if m.group(2) and (m.group(2)[0].isdigit() or m.group(2)[0] == "-"):
            v["json_finding_key_numeric"].add(m.group(1)[:MAX_TOKEN])
    flags = {"text_chunks": len(chunks), "status_read": status_read, "count_read": count_read,
             "json_status": bool(v["json_status_values"]),
             "json_count": bool(v["json_finding_key_numeric"])}
    return v, flags


class Tally:
    """Counts over captures only; holds no id, no timestamp."""

    def __init__(self):
        self.vocab = collections.defaultdict(collections.Counter)
        self.n = collections.Counter()

    def add(self, v, flags):
        self.n["parsed"] += 1
        for k, items in v.items():
            for it in items:
                self.vocab[k][it] += 1
        if flags["text_chunks"] == 0:
            self.n["no_visible_text"] += 1
        for f in ("status_read", "count_read", "json_status", "json_count"):
            if flags[f]:
                self.n[f] += 1
        if flags["status_read"] and flags["count_read"]:
            self.n["status_and_count_read_text"] += 1
        if flags["json_status"] and flags["json_count"]:
            self.n["status_and_count_read_json"] += 1
        if not (flags["status_read"] or flags["json_status"]):
            self.n["no_status_either_way"] += 1

    def report(self):
        return {"counts_over_captures": dict(sorted(self.n.items())),
                "vocabulary": {k: dict(c.most_common(TOP_N)) for k, c in sorted(self.vocab.items())},
                "vocabulary_distinct_sizes": {k: len(c) for k, c in sorted(self.vocab.items())}}


# ---------------------------------------------------------------- fetching (cache in /data)

def cache_path(pages_dir, cid, ts):
    return os.path.join(pages_dir, "%s_%s.html.gz" % (cid, ts))


def fetch(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.geturl(), r.headers.get("Content-Type", ""), r.read()


def get_capture(pages_dir, index_f, cid, ts, original, stats, sleep=time.sleep):
    """Returns html text or None. Never logs id/ts to stdout; the index line goes to /data only."""
    p = cache_path(pages_dir, cid, ts)
    if os.path.exists(p):
        stats["from_cache"] += 1
        with gzip.open(p, "rb") as f:
            return f.read().decode("utf-8", "replace")
    url = WAYBACK % (ts, original)
    for attempt in range(5):
        try:
            code, final, ctype, body = fetch(url)
            stats["http_%d" % code] += 1
            final_ts = None
            m = re.search(r"/web/(\d{14})", final or "")
            if m:
                final_ts = m.group(1)
            if final_ts and final_ts != ts:
                stats["redirected_to_other_timestamp"] += 1
            stats["ctype:" + (ctype.split(";")[0].strip().lower() or "none")] += 1
            with gzip.open(p, "wb") as f:
                f.write(body)
            index_f.write(json.dumps({"id": cid, "ts": ts, "final_ts": final_ts, "bytes": len(body),
                                      "ctype": ctype}) + "\n")
            index_f.flush()
            stats["fetched"] += 1
            stats["bytes"] += len(body)
            sleep(PAUSE_S)
            return body.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            stats["http_error_%d" % e.code] += 1
            if e.code in (429, 503, 502, 504):
                sleep(30 * (attempt + 1))
                continue
            sleep(PAUSE_S)
            return None
        except Exception:
            stats["network_error"] += 1
            sleep(15 * (attempt + 1))
    return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--stamp", default=STAMP_DEFAULT)
    ap.add_argument("--budget-minutes", type=float, default=200.0)
    ap.add_argument("--max-fetch", type=int, default=3000)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    started = time.time()
    summary = {"note": "Counts over captures only. No status or findings count is paired with a capture time "
                       "or a competition. Capture-level data stays in the job's /data volume for stage 3.",
               "started": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "inputs_stamp": a.stamp}
    cdx_p = os.path.join(a.data_dir, "cdx_pages_%s.json" % a.stamp)
    api_p = os.path.join(a.data_dir, "api_competitions_%s.json" % a.stamp)
    if not (os.path.exists(cdx_p) and os.path.exists(api_p)):
        summary["stopped"] = "stage 1 inputs missing in /data"
        _write(a.out_dir, summary)
        return 4
    with open(cdx_p, "rb") as f:
        cdx_rows = json.loads(f.read().decode("utf-8", "replace").strip() or "[]")
    with open(api_p, "rb") as f:
        ends = ends_from_api(json.loads(f.read().decode("utf-8", "replace")))
    read_at = datetime.strptime(a.stamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    caps = select_captures(cdx_rows, ends, read_at)
    summary["captures_selected"] = len(caps)
    summary["competitions_with_selected_captures"] = len({c[0] for c in caps})
    pages_dir = os.path.join(a.data_dir, "pages")
    os.makedirs(pages_dir, exist_ok=True)
    stats = collections.Counter()
    tally = Tally()
    done = 0
    in_a_row = 0
    with open(os.path.join(pages_dir, "index.jsonl"), "a") as index_f:
        for cid, ts, original in caps:
            if time.time() - started > a.budget_minutes * 60 or stats["fetched"] >= a.max_fetch:
                summary["stopped_early"] = "time or fetch budget reached"
                break
            if in_a_row >= 20:
                summary["stopped_early"] = "20 failures in a row (archive refusing or unreachable)"
                break
            html = get_capture(pages_dir, index_f, cid, ts, original, stats)
            done += 1
            if html is None:
                stats["failed"] += 1
                in_a_row += 1
                continue
            in_a_row = 0
            v, flags = capture_vocab(html)
            tally.add(v, flags)
            if done % 50 == 0:
                print("progress: %d of %d captures handled" % (done, len(caps)), flush=True)
    summary["captures_handled"] = done
    summary["complete"] = done == len(caps)
    summary["fetch_stats"] = dict(sorted(stats.items()))
    summary.update(tally.report())
    summary["finished"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write(a.out_dir, summary)
    print(json.dumps({k: summary[k] for k in ("captures_selected", "captures_handled", "complete",
                                              "counts_over_captures")}, indent=1, sort_keys=True))
    return 0


def _write(out_dir, summary):
    with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)


if __name__ == "__main__":
    sys.exit(main())
