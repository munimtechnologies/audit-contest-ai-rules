#!/usr/bin/env python3
"""fetch_c4.py -- count the submissions to every public Code4rena audit.

Code4rena (C4) publishes a "<slug>-findings" repository on GitHub for most of its audits.
Its data/ folder holds one small JSON record per submission (contest number, risk label,
issue number), and its report.md holds the published report. This script:

  1. lists the public repositories of the code-423n4 GitHub organization (GitHub REST API,
     about ten unauthenticated GETs; falls back to repository search) and keeps the
     "-findings" ones;
  2. makes a shallow, blob-less clone of each, then checks out ONLY report.md and the
     data/*.json records (never the QA/gas report bodies);
  3. reads the audit's own README (raw.githubusercontent.com) for dates, pot and nSLOC;
  4. writes one line of contest-level facts per repository.

Kept: counts by risk label, highest issue numbers, the number of distinct submitters
(a count only), and the report's headline numbers. Never kept: handles, wallet
addresses, finding titles or text.

Polite: a few repositories at a time (--workers, default 1), each followed by a pause;
git clones and raw files are not API calls.
v3: --workers. v1 and v2 took about a minute per repository one at a time and were cut
off after 167 and 186 of 376 repositories.
Licensed under Apache-2.0. Made with AI agents working for MV2 of Munim, Inc.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Dict, Iterable, List, Optional, Tuple

ORG = "code-423n4"
API_REPOS = "https://api.github.com/orgs/code-423n4/repos?per_page=100&type=public&page={page}"
API_SEARCH = "https://api.github.com/search/repositories?q=org:code-423n4+findings+in:name&per_page=100&page={page}"
RAW = "https://raw.githubusercontent.com/code-423n4/{repo}/{branch}/README.md"
GIT = "https://github.com/code-423n4/{repo}.git"
USER_AGENT = "MV2-Munim-research/1.0 (mv2@munimtech.com)"

MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december"]

UNIQUE_RE = re.compile(r"aggregated total of\s+(\d+)\s+unique vulnerabilit", re.I)
HIGH_RE = re.compile(r"(\d+)\s+received a risk rating in the category of\s+HIGH", re.I)
MEDIUM_RE = re.compile(r"(\d+)\s+received a risk rating in the category of\s+MEDIUM", re.I)
WARDENS_RE = re.compile(r"(\d+)\s+Wardens?\s+contributed\s+reports", re.I)
PLACE_RE = re.compile(r"took place (?:between|from|on)\s+([^\n]{3,200})", re.I)
DATE_TEXT = r"([A-Za-z]{3,9}\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+20\d\d)"
STARTS_RE = re.compile(r"\bStarts?\b[\s:*|\-–—]*" + DATE_TEXT, re.I)
ENDS_RE = re.compile(r"\bEnds?\b[\s:*|\-–—]*" + DATE_TEXT, re.I)
POT_RE = re.compile(
    r"(?:Prize\s+Pool|Total\s+Awards?|Award\s+Pool)[^\n$]{0,60}\$\s?([\d,]+(?:\.\d+)?)\s*([KkMm](?![A-Za-z]))?", re.I)
NSLOC_RE = re.compile(r"nSLOC[^\d\n]{0,40}([\d,]+)", re.I)


# ---------------------------------------------------------------- parsing (pure)

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
    """'April 05, 2023' / 'Nov 11 2024' / 'January 7th, 2022' -> date."""
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


def parse_span(text: str) -> Optional[Tuple[_dt.date, _dt.date]]:
    """A report's date range -> (start, end).

    Handles 'April 5 — April 13 2023', 'January 7—13, 2022',
    'November 11 to November 25, 2024' and 'Dec 28, 2023 - Jan 5, 2024'.
    """
    years = [int(y) for y in re.findall(r"\b(20\d\d)\b", text or "")]
    if not years:
        return None
    stripped = re.sub(r"\b20\d\d\b", " ", text)
    parts: List[Tuple[int, int]] = []
    month = None
    for word, day in re.findall(r"([A-Za-z]+)?\.?\s*\b(\d{1,2})(?:st|nd|rd|th)?\b", stripped):
        found = month_num(word) if word else None
        if found:
            month = found
        if month is None:
            continue
        parts.append((month, int(day)))
    if len(parts) < 2:
        return None
    (m1, d1), (m2, d2) = parts[0], parts[-1]
    y2 = years[-1]
    y1 = years[0] if len(years) > 1 else (y2 - 1 if m1 > m2 else y2)
    try:
        start, end = _dt.date(y1, m1, d1), _dt.date(y2, m2, d2)
    except ValueError:
        return None
    return (start, end) if end >= start else None


def front_matter(text: str) -> Dict[str, str]:
    """The YAML-ish header of a C4 report.md (sponsor, slug, date, title, contest)."""
    m = re.match(r"\s*---\s*\n(.*?)\n---", text or "", re.S)
    if not m:
        return {}
    out: Dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def _first_int(regex: "re.Pattern", text: str) -> Optional[int]:
    m = regex.search(text or "")
    return int(m.group(1)) if m else None


def parse_report(text: Optional[str]) -> Dict:
    """Headline numbers of a published C4 report. Missing pieces stay None."""
    if not text:
        return {"present": False}
    front = front_matter(text)
    span = None
    place = PLACE_RE.search(text)
    if place:
        sentence = re.split(r"\.(?:\s|$)", place.group(1))[0]
        span = parse_span(sentence)
    contest = front.get("contest")
    return {
        "present": True,
        "contest": int(contest) if contest and contest.isdigit() else None,
        "slug": front.get("slug") or None,
        "title": front.get("title") or None,
        "sponsor": front.get("sponsor") or None,
        "report_date": front.get("date") or None,
        "start": span[0].isoformat() if span else None,
        "end": span[1].isoformat() if span else None,
        "unique_total": _first_int(UNIQUE_RE, text),
        "unique_high": _first_int(HIGH_RE, text),
        "unique_medium": _first_int(MEDIUM_RE, text),
        "wardens": _first_int(WARDENS_RE, text),
    }


def parse_readme(text: Optional[str]) -> Dict:
    """Dates, headline pot and nSLOC from an audit repo's README. Missing pieces stay None."""
    if not text:
        return {"present": False}
    starts, ends = STARTS_RE.search(text), ENDS_RE.search(text)
    pot_usd = None
    pot_text = None
    pot = POT_RE.search(text)
    if pot:
        try:
            pot_usd = float(pot.group(1).replace(",", ""))
        except ValueError:
            pot_usd = None
        unit = (pot.group(2) or "").lower()
        if pot_usd is not None and unit == "k":
            pot_usd *= 1000.0
        elif pot_usd is not None and unit == "m":
            pot_usd *= 1000000.0
        line_start = text.rfind("\n", 0, pot.start()) + 1
        line_end = text.find("\n", pot.end())
        pot_text = text[line_start: line_end if line_end >= 0 else len(text)].strip()[:160]
    found = NSLOC_RE.search(text)
    digits = found.group(1).replace(",", "") if found else ""
    nsloc = int(digits) if digits.isdigit() else None
    start = parse_date(starts.group(1)) if starts else None
    end = parse_date(ends.group(1)) if ends else None
    return {
        "present": True,
        "start": start.isoformat() if start else None,
        "end": end.isoformat() if end else None,
        "pot_usd": pot_usd,
        "pot_text": pot_text,
        "nsloc": nsloc,
    }


def risk_class(value) -> str:
    """C4's per-submission risk label -> high / medium / qa / gas / analysis / other."""
    v = str(value).strip().upper() if value is not None else ""
    if v in ("3", "H", "HIGH"):
        return "high"
    if v in ("2", "M", "MED", "MEDIUM"):
        return "medium"
    if v in ("Q", "QA", "1", "0", "L", "LOW", "N", "NC"):
        return "qa"
    if v in ("G", "GAS"):
        return "gas"
    if v in ("A", "ANALYSIS"):
        return "analysis"
    return "other"


def md_class(name: str) -> str:
    base = name.rsplit("/", 1)[-1]
    if base.endswith("-Q.md"):
        return "qa"
    if base.endswith("-G.md"):
        return "gas"
    if base.lower().endswith("-analysis.md"):
        return "analysis"
    return "other"


def _int(value) -> Optional[int]:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def summarize_data(names: List[str], json_docs: Dict[str, object]) -> Dict:
    """Counts over a findings repo's data/ folder. json_docs maps data/*.json path -> parsed doc
    (or None if it would not parse). Handles are counted, never returned."""
    risk = {"high": 0, "medium": 0, "qa": 0, "gas": 0, "analysis": 0, "other": 0}
    md = {"qa": 0, "gas": 0, "analysis": 0, "other": 0}
    handles = set()
    bad = 0
    issue_ids: List[int] = []
    original_ids: List[int] = []
    contests = set()
    for name in names:
        if not name.startswith("data/"):
            continue
        if name.endswith(".md"):
            md[md_class(name)] += 1
            continue
        if not name.endswith(".json"):
            continue
        doc = json_docs.get(name)
        if not isinstance(doc, dict):
            bad += 1
            continue
        risk[risk_class(doc.get("risk"))] += 1
        if doc.get("handle"):
            handles.add(str(doc["handle"]).strip().lower())
        iid = _int(doc.get("issueId"))
        if iid is not None:
            issue_ids.append(iid)
        oid = _int(doc.get("originalIssueId"))
        if oid is not None:
            original_ids.append(oid)
        cid = _int(doc.get("contest"))
        if cid is not None:
            contests.add(cid)
    return {
        "json_records": sum(risk.values()),
        "json_bad": bad,
        "risk": risk,
        "md_files": md,
        "submitters": len(handles),
        "max_issue_id": max(issue_ids) if issue_ids else None,
        "with_original_id": len(original_ids),
        "max_original_issue_id": max(original_ids) if original_ids else None,
        "contest_ids": sorted(contests),
    }


def is_findings_repo(name) -> bool:
    return isinstance(name, str) and name.endswith("-findings")


def audit_slug(repo: str, report: Dict) -> str:
    return report.get("slug") or repo[: -len("-findings")]


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


def list_findings_repos() -> List[Dict]:
    found: Dict[str, Dict] = {}
    complete = False
    for page in range(1, 40):
        body = get(API_REPOS.format(page=page))
        if body is None:
            break
        items = json.loads(body.decode("utf-8"))
        if not items:
            complete = True
            break
        for item in items:
            if is_findings_repo(item.get("name")):
                found[item["name"]] = {"repo": item["name"], "created_at": item.get("created_at")}
        time.sleep(1.0)
    if not complete:
        print("org listing incomplete; adding repository search results", file=sys.stderr)
        for page in range(1, 11):
            body = get(API_SEARCH.format(page=page))
            if body is None:
                break
            items = json.loads(body.decode("utf-8")).get("items") or []
            if not items:
                break
            for item in items:
                if is_findings_repo(item.get("name")):
                    found.setdefault(item["name"], {"repo": item["name"], "created_at": item.get("created_at")})
            time.sleep(7.0)
    return [found[k] for k in sorted(found)]


def git(args: List[str], cwd: Optional[str] = None, stdin: Optional[str] = None,
        timeout: int = 900) -> subprocess.CompletedProcess:
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_LITERAL_PATHSPECS="1")
    return subprocess.run(["git", *args], cwd=cwd, input=stdin, capture_output=True,
                          text=True, timeout=timeout, env=env)


def read_text(path: str) -> Optional[str]:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


def inspect_repo(repo: str, workdir: str) -> Dict:
    """Clone without blobs, check out only report.md and data/*.json, and count."""
    path = os.path.join(workdir, repo)
    shutil.rmtree(path, ignore_errors=True)
    try:
        cloned = git(["clone", "--depth", "1", "--filter=blob:none", "--no-checkout", "--quiet",
                      GIT.format(repo=repo), path])
        if cloned.returncode != 0:
            return {"error": "clone failed: " + cloned.stderr.strip()[-300:]}
        tree = git(["ls-tree", "-r", "-z", "--name-only", "HEAD"], cwd=path)
        names = [n for n in tree.stdout.split("\0") if n]
        wanted = [n for n in names if n == "report.md" or (n.startswith("data/") and n.endswith(".json"))]
        if wanted:
            git(["checkout", "HEAD", "--pathspec-from-file=-", "--pathspec-file-nul"], cwd=path,
                stdin="\0".join(wanted) + "\0")
        docs: Dict[str, object] = {}
        for name in wanted:
            if name == "report.md":
                continue
            full = os.path.join(path, name)
            text = read_text(full)
            if text is None:
                shown = git(["show", "HEAD:" + name], cwd=path, timeout=120)
                text = shown.stdout if shown.returncode == 0 else None
            try:
                docs[name] = json.loads(text) if text else None
            except json.JSONDecodeError:
                docs[name] = None
        report_text = read_text(os.path.join(path, "report.md")) if "report.md" in names else None
        if report_text is None and "report.md" in names:
            shown = git(["show", "HEAD:report.md"], cwd=path, timeout=300)
            report_text = shown.stdout if shown.returncode == 0 else None
        out = summarize_data(names, docs)
        out["data_files"] = sum(1 for n in names if n.startswith("data/"))
        out["report"] = parse_report(report_text)
        return out
    except subprocess.TimeoutExpired:
        return {"error": "git timed out"}
    finally:
        shutil.rmtree(path, ignore_errors=True)


def fetch_readme(slug: str) -> Optional[str]:
    for branch in ("main", "master"):
        body = get(RAW.format(repo=slug, branch=branch), retries=2, pause=2.0)
        if body is not None:
            return body.decode("utf-8", errors="replace")
    return None


def fetch_one(item: Dict, workdir: str, fetched_on: str, pause: float) -> Dict:
    """One repository's record (an "error" record instead of raising), then a polite pause."""
    repo = item["repo"]
    rec = {"repo": repo, "created_at": item.get("created_at"), "fetched_on": fetched_on}
    try:
        facts = inspect_repo(repo, workdir)
        rec.update(facts)
        if not facts.get("error"):
            slug = audit_slug(repo, facts.get("report") or {})
            rec["slug"] = slug
            rec["readme"] = parse_readme(fetch_readme(slug))
    except Exception as exc:  # one bad repository must not stop the census
        rec["error"] = f"{type(exc).__name__}: {exc}"[:300]
    time.sleep(pause)
    return rec


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, help="JSONL of per-repository facts (appended; done repos skipped)")
    parser.add_argument("--workdir", default="/tmp/c4-clones", help="scratch folder for clones")
    parser.add_argument("--pause", type=float, default=1.0, help="seconds each worker waits after a repository")
    parser.add_argument("--workers", type=int, default=1, help="repositories fetched at the same time")
    parser.add_argument("--limit", type=int, default=0, help="stop after this many new repositories (0 = all)")
    args = parser.parse_args(list(argv) if argv is not None else None)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    os.makedirs(args.workdir, exist_ok=True)
    done = set()
    if os.path.exists(args.out):
        with open(args.out, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue  # a line cut off when an earlier run was stopped
                    if not rec.get("error"):
                        done.add(rec.get("repo"))
    repos = list_findings_repos()
    print(f"{len(repos)} findings repositories listed; {len(done)} already done", flush=True)
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
        futures = [pool.submit(fetch_one, item, args.workdir, fetched_on, args.pause) for item in todo]
        for fut in concurrent.futures.as_completed(futures):
            rec = fut.result()
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            new += 1
            print(f"{new:4d} {rec['repo']}: {rec.get('json_records', '-')} records"
                  f"{' ERROR ' + rec['error'] if rec.get('error') else ''}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
