#!/usr/bin/env python3
"""fetch_c4_readmes.py -- read the README of every public Code4rena audit repository and note
which known-issues sections it carries.

Tests a prediction the audit-contest census paper (v1.8, section 4) wrote down before any README
was read section by section (see PREREGISTRATION.md). This script:

  1. lists the public repositories of the code-423n4 GitHub organization (GitHub REST API,
     about fifteen unauthenticated GETs) and keeps the audit repositories: "YYYY-MM-<name>",
     not ending in "-findings";
  2. reads each one's README.md from raw.githubusercontent.com at its default branch;
  3. writes one line of facts per repository: dates, a flag for each section marker, the
     source-file extensions the README names, and the README's sha256.

Kept: flags, dates, counts and a hash. Never kept: README text, handles, links.
Polite: a few repositories at a time (--workers, default 1), each followed by a pause; raw
files are not API calls.
Licensed under Apache-2.0. Made with AI agents working for MV2 of Munim, Inc.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as _dt
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from typing import Dict, Iterable, List, Optional

API_REPOS = "https://api.github.com/orgs/code-423n4/repos?per_page=100&type=public&page={page}"
RAW = "https://raw.githubusercontent.com/code-423n4/{repo}/{branch}/README.md"
USER_AGENT = "MV2-Munim-research/1.0 (mv2@munimtech.com)"

MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december"]

AUDIT_RE = re.compile(r"^(20\d\d)-(0[1-9]|1[0-2])-[A-Za-z0-9._-]+$")
DATE_TEXT = r"([A-Za-z]{3,9}\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+20\d\d)"
STARTS_RE = re.compile(r"\bStarts?\b[\s:*|\-–—]*" + DATE_TEXT, re.I)
ENDS_RE = re.compile(r"\bEnds?\b[\s:*|\-–—]*" + DATE_TEXT, re.I)

AUTO_HEADING_RE = re.compile(r"^ {0,3}#{1,6}[^\n]*\bAutomated\s+Findings\b", re.I | re.M)
BOT_WORDS_RE = re.compile(r"\bbot[\s-]?races?\b|\bwinning\s+bot\b|\bbot\s+reports?\b", re.I)
AUTO_OUTPUT_RE = re.compile(r"\bautomated\s+findings\s+output\b", re.I)
ANALYZER_RE = re.compile(r"4naly3er", re.I)
V12_RE = re.compile(r"\bV12\b")
V12_HEADING_RE = re.compile(r"^ {0,3}#{1,6}[^\n]*\bV12\b", re.M)
EXT_RE = re.compile(r"[A-Za-z0-9_\-]\.(sol|rs|move|go|cairo|vy|nr|circom)\b")


# ---------------------------------------------------------------- parsing (pure)

def is_audit_repo(name) -> bool:
    return isinstance(name, str) and bool(AUDIT_RE.match(name)) and not name.endswith("-findings")


def repo_kind(name: str) -> str:
    return "mitigation" if "mitigation" in (name or "").lower() else "audit"


def name_month(name: str) -> Optional[str]:
    """'2025-10-hybra-finance' -> '2025-10'."""
    m = AUDIT_RE.match(name or "")
    return f"{m.group(1)}-{m.group(2)}" if m else None


def month_num(word: str) -> Optional[int]:
    """'April', 'Apr', 'Sept.' -> month number; None for anything else."""
    w = (word or "").lower().rstrip(".")
    if len(w) < 3:
        return None
    for i, name in enumerate(MONTHS, 1):
        if name.startswith(w):
            return i
    return None


def parse_date(text: str) -> Optional[_dt.date]:
    """'October 6, 2025' / 'Nov 11 2024' / 'January 7th, 2022' -> date."""
    m = re.match(r"\s*([A-Za-z]+)\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(20\d\d)", text or "")
    if not m:
        return None
    month = month_num(m.group(1))
    if month is None:
        return None
    try:
        return _dt.date(int(m.group(3)), month, int(m.group(2)))
    except ValueError:
        return None


def first_date(regex: "re.Pattern", text: str) -> Optional[_dt.date]:
    """The first match of `regex` that parses as a date (skips 'Starts and expires ...')."""
    for m in regex.finditer(text or ""):
        found = parse_date(m.group(1))
        if found:
            return found
    return None


def parse_readme(text: Optional[str]) -> Dict:
    """Section markers and dates from an audit README. Missing pieces stay None."""
    if text is None:
        return {"present": False}
    exts = sorted(set(m.group(1) for m in EXT_RE.finditer(text)))
    start, end = first_date(STARTS_RE, text), first_date(ENDS_RE, text)
    return {
        "present": True,
        "bytes": len(text.encode("utf-8")),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "start": start.isoformat() if start else None,
        "end": end.isoformat() if end else None,
        "auto_heading": bool(AUTO_HEADING_RE.search(text)),
        "bot_words": bool(BOT_WORDS_RE.search(text)),
        "auto_output": bool(AUTO_OUTPUT_RE.search(text)),
        "analyzer_4naly3er": bool(ANALYZER_RE.search(text)),
        "v12": bool(V12_RE.search(text)),
        "v12_heading": bool(V12_HEADING_RE.search(text)),
        "exts": exts,
        "solidity": "sol" in exts,
    }


def pending(repos: List[Dict], done: set, limit: int = 0) -> List[Dict]:
    """Repositories still to fetch, in listing order; at most `limit` of them (0 = all)."""
    todo = [item for item in repos if item.get("repo") not in done]
    return todo[:limit] if limit else todo


# ---------------------------------------------------------------- network

def get(url: str, retries: int = 4, pause: float = 5.0) -> Optional[bytes]:
    """GET bytes; None on 404 or if it never succeeds."""
    err: object = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                                   "Accept": "application/vnd.github+json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            err = exc
            if exc.code in (403, 429):
                time.sleep(60.0)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            err = exc
        time.sleep(pause * (attempt + 1))
    print(f"giving up on {url}: {err}", file=sys.stderr)
    return None


def list_audit_repos() -> List[Dict]:
    """Audit repositories of the org, sorted by name. Prints a warning if the listing stops early."""
    found: Dict[str, Dict] = {}
    complete = False
    for page in range(1, 60):
        body = get(API_REPOS.format(page=page))
        if body is None:
            break
        items = json.loads(body.decode("utf-8"))
        if not items:
            complete = True
            break
        for item in items:
            if is_audit_repo(item.get("name")):
                found[item["name"]] = {"repo": item["name"], "created_at": item.get("created_at"),
                                       "branch": item.get("default_branch") or "main",
                                       "archived": bool(item.get("archived"))}
        time.sleep(1.0)
    if not complete:
        print("ORG LISTING INCOMPLETE: the census below misses repositories", file=sys.stderr)
    return [found[k] for k in sorted(found)]


def fetch_readme(repo: str, branch: str) -> Optional[str]:
    for b in dict.fromkeys([branch, "main", "master"]):
        body = get(RAW.format(repo=repo, branch=b), retries=2, pause=2.0)
        if body is not None:
            return body.decode("utf-8", errors="replace")
    return None


def fetch_one(item: Dict, fetched_on: str, pause: float) -> Dict:
    """One repository's record (an "error" record instead of raising), then a polite pause."""
    repo = item["repo"]
    rec = {"repo": repo, "kind": repo_kind(repo), "name_month": name_month(repo),
           "created_at": item.get("created_at"), "archived": item.get("archived"),
           "fetched_on": fetched_on}
    try:
        rec["readme"] = parse_readme(fetch_readme(repo, item.get("branch") or "main"))
    except Exception as exc:  # one bad repository must not stop the census
        rec["error"] = f"{type(exc).__name__}: {exc}"[:300]
    time.sleep(pause)
    return rec


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, help="JSONL of per-repository facts (appended; done repos skipped)")
    parser.add_argument("--pause", type=float, default=1.0, help="seconds each worker waits after a repository")
    parser.add_argument("--workers", type=int, default=1, help="repositories fetched at the same time")
    parser.add_argument("--limit", type=int, default=0, help="stop after this many new repositories (0 = all)")
    args = parser.parse_args(list(argv) if argv is not None else None)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    done = set()
    if os.path.exists(args.out):
        with open(args.out, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue  # a line cut off when an earlier run was stopped
                    if not rec.get("error") and (rec.get("readme") or {}).get("present"):
                        done.add(rec.get("repo"))
    repos = list_audit_repos()
    print(f"{len(repos)} audit repositories listed; {len(done)} already done", flush=True)
    if not repos:
        return 1
    todo = pending(repos, done, args.limit)
    fetched_on = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
    new = 0
    if os.path.exists(args.out) and os.path.getsize(args.out) > 0:
        with open(args.out, "rb") as fh:
            fh.seek(-1, os.SEEK_END)
            cut_off = fh.read(1) != b"\n"
        if cut_off:
            with open(args.out, "a", encoding="utf-8") as fh:
                fh.write("\n")  # start new records on a fresh line
    # Workers only fetch; this thread alone writes, so lines never interleave.
    with open(args.out, "a", encoding="utf-8") as fh, \
            concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(fetch_one, item, fetched_on, args.pause) for item in todo]
        for fut in concurrent.futures.as_completed(futures):
            rec = fut.result()
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            new += 1
            r = rec.get("readme") or {}
            print(f"{new:4d} {rec['repo']}: start {r.get('start')}, v12 {r.get('v12')}, "
                  f"auto {r.get('auto_heading')}, bot {r.get('bot_words')}"
                  f"{' ERROR ' + rec['error'] if rec.get('error') else ''}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
