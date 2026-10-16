#!/usr/bin/env python3
"""fetch_immunefi.py -- save and read the public pages of every Immunefi audit competition.

Immunefi's /audit-competition/ listing shows each finished competition with its pool and a
date, but that date is NOT when the competition ran (ENS is listed "Oct 8, 2026" and ran
18 Aug - 14 Sep 2026; Firedancer V1 is listed "Jul 10, 2026" and ran 9 Apr - 9 May 2026).
Each competition's /information/ page gives "Start Date", "End Date", "Primary Pool",
"All Stars Pool", "Podium Pool", "Rewards Token" and "Lines of Code"; its results page is a
ranked leaderboard. This script:

  1. reads the listing for competition slugs;
  2. saves the information and results page of each one under <data-dir>/raw/ (one at a
     time, paused; pages already saved are not fetched again);
  3. reads competition-level facts from the saved pages into <data-dir>/facts.jsonl, and
     writes immunefi_contests.csv and IMMUNEFI.md (counts by start half-year) to --out-dir.

--parse-only repeats step 3 without any network. Kept: competition-level facts and up to
three short lines of page text that mention AI. Never kept: handles, earnings, finding text.

Leaderboards come in two styles (v2): from mid-2025 ranks are written "#4".."#N" with medal
icons for the top three; earlier ones write bare numbers "1".."N" in their own cell. v1 read
only the first style; v2 falls back to the second (see bare_rank_top).

robots.txt (checked 2026-10-15) allows all paths. Licensed under Apache-2.0.
Made with AI agents working for MV2 of Munim, Inc.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import html as _html
import json
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.request
from typing import Dict, Iterable, List, Optional, Tuple

BASE = "https://immunefi.com"
LISTING = "/audit-competition/"
PAGES = {"information": "information/", "results": ""}
USER_AGENT = "MV2-Munim-research/1.0 (munimversion2@gmail.com)"

MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december"]

SLUG = r"[a-z0-9][a-z0-9_.\-]*"
HREF_RE = re.compile(r'href="(?:https://immunefi\.com)?/audit-competition/(' + SLUG + r")/", re.I)
NOT_SLUGS = {"findings", "information", "results", "leaderboard", "page"}
DATE = r"(\d{1,2})\s+([A-Za-z]{3,9})\.?,?\s+(20\d\d)"
LABEL_DATE = {k: re.compile(k + r"\s+" + DATE) for k in ("Start Date", "End Date")}
MONEY = r"\$\s?([\d,]+(?:\.\d+)?)"
POOLS = ("Primary Pool", "All Stars Pool", "Podium Pool", "Reward Pool")
POOL_RE = {k: re.compile(k + r"\s+" + MONEY) for k in POOLS}
TOKEN_RE = re.compile(r"Rewards Token\s+([A-Z][A-Z0-9]{1,9})\b")
LOC_RE = re.compile(r"Lines of Code\s+([\d,]+)\b")
ASSETS_RE = re.compile(r"Total Assets in Scope\s+(\d+)\b")
RANK_RE = re.compile(r"(?:^|\s)#\s?(\d{1,4})(?=\s|$)")
BARE_INT_RE = re.compile(r"\d{1,4}")
AI_RE = re.compile(r"\bAI\b|\bA\.I\.|artificial intelligence|\bLLMs?\b|ChatGPT|GPT-\d|machine[- ]generated")
POC_RE = re.compile(r"proof of concept is (?:always )?required|PoC (?:is )?required", re.I)
TITLE_RE = re.compile(r"(?is)<title[^>]*>(.*?)</title>")
# Name prefixes on the listing, longest first; the slug is the fallback.
KINDS = (("Bug Bounty Comp", "bug_bounty_comp"), ("Mitigation Audit", "mitigation_audit"),
         ("Audit Competition", "audit_comp"), ("Audit Comp", "audit_comp"),
         ("Attackathon", "attackathon"), ("IOP", "iop"))
AUDIT_KINDS = ("audit_comp", "iop", "mitigation_audit")

SAMPLE_SLUGS = ("audit-competition-ens", "firedancer-v1-audit-comp", "xrpl-ripple-attackathon",
                "audit-comp-yeet")
SNIPPET_KEYS = ("Start Date", "End Date", "Pool", "Rewards Token", "Lines of Code",
                "Assets in Scope", "#1", "#2")
MAX_SAMPLES = 12


# ---------------------------------------------------------------- parsing (pure)

def month_num(word: str) -> Optional[int]:
    """'August', 'Aug', 'Sept.' -> month number; None for anything else."""
    w = (word or "").lower().rstrip(".")
    if len(w) < 3:
        return None
    for i, name in enumerate(MONTHS, 1):
        if name.startswith(w):
            return i
    return None


def make_date(day: str, month_word: str, year: str) -> Optional[_dt.date]:
    month = month_num(month_word)
    if month is None:
        return None
    try:
        return _dt.date(int(year), month, int(day))
    except ValueError:
        return None


def html_to_lines(html: Optional[str]) -> List[str]:
    """Visible text of a page, one text node per line (scripts and styles dropped)."""
    s = re.sub(r"(?is)<(script|style)\b.*?</\1\s*>", "\n", html or "")
    s = re.sub(r"(?s)<!--.*?-->", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", "\n", s)
    s = _html.unescape(s)
    out = []
    for line in s.split("\n"):
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            out.append(line)
    return out


def page_title(html: Optional[str]) -> Optional[str]:
    m = TITLE_RE.search(html or "")
    return re.sub(r"\s+", " ", _html.unescape(m.group(1))).strip() or None if m else None


def to_number(text: Optional[str]) -> Optional[float]:
    try:
        return float(text.replace(",", ""))
    except (AttributeError, ValueError):
        return None


def kind_of(slug: str, lines: List[str]) -> str:
    """Competition type from an 'Audit Comp | X'-style line, else from the slug."""
    for line in lines[:400]:
        for prefix, kind in KINDS:
            if line.startswith(prefix + " |") or line.startswith(prefix + " -"):
                return kind
    s = slug.lower()
    if "attackathon" in s:
        return "attackathon"
    if "bug-bounty" in s or "bbc" in s.split("-"):
        return "bug_bounty_comp"
    if "mitigation" in s:
        return "mitigation_audit"
    if s.startswith("iop") or "-iop" in s:
        return "iop"
    return "audit_comp"


def parse_information(html: Optional[str], slug: str = "") -> Dict:
    """Dates, pools, token, lines of code and AI/PoC wording of an /information/ page."""
    if not html:
        return {"present": False}
    lines = html_to_lines(html)
    text = " ".join(lines)
    out: Dict = {"present": True, "title": page_title(html), "kind": kind_of(slug, lines)}
    for label, regex in LABEL_DATE.items():
        m = regex.search(text)
        d = make_date(*m.group(1, 2, 3)) if m else None
        out[label.split()[0].lower()] = d.isoformat() if d else None
    pools = {}
    for label, regex in POOL_RE.items():
        m = regex.search(text)
        pools[label] = to_number(m.group(1)) if m else None
    tiers = [pools[k] for k in POOLS[:3] if pools[k] is not None]
    out["pools"] = pools
    out["pool_usd"] = sum(tiers) if tiers else pools["Reward Pool"]
    token = TOKEN_RE.search(text)
    loc = LOC_RE.search(text)
    assets = ASSETS_RE.search(text)
    out["token"] = token.group(1) if token else None
    out["lines_of_code"] = int(loc.group(1).replace(",", "")) if loc else None
    out["assets_in_scope"] = int(assets.group(1)) if assets else None
    out["poc_required"] = bool(POC_RE.search(text))
    ai_lines = [ln[:240] for ln in lines if AI_RE.search(ln)]
    out["ai_mentions"] = len(ai_lines)
    out["ai_lines"] = ai_lines[:3]
    return out


def is_cell_value(line: str) -> bool:
    """A count, an amount or an empty-cell dash: what follows a count cell, never a rank cell."""
    return bool(BARE_INT_RE.fullmatch(line)) or line.startswith("$") or line in ("-", "—")


def bare_rank_candidates(lines: List[str]) -> List[int]:
    """Bare numbers followed by a non-number line (a handle): rank cells, plus a few counts."""
    return [int(ln) for i, ln in enumerate(lines[:-1])
            if BARE_INT_RE.fullmatch(ln) and not is_cell_value(lines[i + 1])]


def bare_rank_top(lines: List[str]) -> Tuple[Optional[int], int]:
    """(leaderboard size, candidates) for bare-number leaderboards.

    Walks the candidates in page order, counting up from 1 (or from 4 when the top three
    are medal icons with no number); a stray count only matches by luck and cannot stop
    the walk. A walk of fewer than three ranks is not a leaderboard.
    """
    cands = bare_rank_candidates(lines)
    best = 0
    for start in (1, 4):
        expected = start
        for value in cands:
            if value == expected:
                expected += 1
        if expected - start >= 3:
            best = max(best, expected - 1)
    return (best or None), len(cands)


def parse_results(html: Optional[str]) -> Dict:
    """Leaderboard size: the highest '#N' rank if ranks 1..N are mostly there, else bare ranks."""
    if not html:
        return {"present": False}
    lines = html_to_lines(html)
    ranks = {int(x) for x in RANK_RE.findall(" ".join(lines))}
    ranks.discard(0)
    top = max(ranks) if ranks else None
    if top and len([r for r in ranks if r <= top]) >= 0.8 * top:
        return {"present": True, "max_rank": top, "ranks_seen": len(ranks), "rank_method": "hash"}
    bare, cands = bare_rank_top(lines)
    return {"present": True, "max_rank": bare, "ranks_seen": len(ranks), "bare_candidates": cands,
            "rank_method": "bare" if bare else None}


def line_shape(lines: List[str], limit: int = 48) -> str:
    """Handle-free shape of the leaderboard rows: numbers kept, '$' for amounts, 'T' for text."""
    cands = [i for i, ln in enumerate(lines[:-1])
             if BARE_INT_RE.fullmatch(ln) and not is_cell_value(lines[i + 1])]
    if not cands:
        return ""
    out = []
    for ln in lines[cands[0]:cands[0] + limit]:
        out.append(ln if BARE_INT_RE.fullmatch(ln) else "$" if ln.startswith("$") else "T")
    return " ".join(out)


def listing_slugs(html: Optional[str]) -> List[str]:
    return sorted({s.lower() for s in HREF_RE.findall(html or "")} - NOT_SLUGS)


def half_year(iso: Optional[str]) -> Optional[str]:
    if not iso:
        return None
    return f"{iso[:4]}H{1 if int(iso[5:7]) <= 6 else 2}"


def competition_facts(slug: str, pages: Dict[str, Optional[str]]) -> Dict:
    info = parse_information(pages.get("information"), slug)
    return {
        "slug": slug,
        "information": info,
        "results": parse_results(pages.get("results")),
        "is_competition": bool(info.get("start")),
        "page_bytes": {k: len(v) if v else 0 for k, v in pages.items()},
    }


def contest_row(rec: Dict) -> Dict:
    info = rec["information"]
    days = None
    if info.get("start") and info.get("end"):
        days = (_dt.date.fromisoformat(info["end"]) - _dt.date.fromisoformat(info["start"])).days
    return {
        "slug": rec["slug"],
        "kind": info.get("kind"),
        "start": info.get("start"),
        "end": info.get("end"),
        "start_half": half_year(info.get("start")),
        "days": days,
        "pool_usd": info.get("pool_usd"),
        "token": info.get("token"),
        "lines_of_code": info.get("lines_of_code"),
        "assets_in_scope": info.get("assets_in_scope"),
        "poc_required": info.get("poc_required"),
        "ai_mentions": info.get("ai_mentions"),
        "ranked_whitehats": rec["results"].get("max_rank"),
        "rank_method": rec["results"].get("rank_method"),
    }


def by_half(rows: List[Dict]) -> List[Dict]:
    """Per start half-year: competitions (all kinds and audit-type only), pools, leaderboards."""
    halves: Dict[str, List[Dict]] = {}
    for row in rows:
        if row["start_half"]:
            halves.setdefault(row["start_half"], []).append(row)
    out = []
    for half in sorted(halves):
        group = halves[half]
        audit = [r for r in group if r["kind"] in AUDIT_KINDS]
        ranked = [r["ranked_whitehats"] for r in group if r["ranked_whitehats"]]
        ranked_audit = [r["ranked_whitehats"] for r in audit if r["ranked_whitehats"]]
        out.append({
            "half": half,
            "competitions": len(group),
            "audit_type": len(audit),
            "pool_usd": sum(r["pool_usd"] or 0 for r in group),
            "median_ranked_whitehats": statistics.median(ranked) if ranked else None,
            "ranked_n": len(ranked),
            "median_ranked_audit_type": statistics.median(ranked_audit) if ranked_audit else None,
        })
    return out


def render_md(rows: List[Dict], halves: List[Dict], fetched_on: str) -> str:
    out = ["# Immunefi audit competitions by start half-year", "",
           f"Read from immunefi.com on {fetched_on}. One row per competition page with a Start Date.",
           "audit_type = Audit Comp + IOP + Mitigation Audit (no Attackathons or Bug Bounty Comps).",
           "Ranked whitehats = size of the results leaderboard ('#N' or bare-number ranks; check the samples).",
           "Pools are the USD amounts the pages state; some are paid in other tokens (see token).", "",
           "| Start half | Competitions | Audit-type | Pools (USD) | Median ranked whitehats | Leaderboards read "
           "| Median ranked, audit-type |",
           "|---|---:|---:|---:|---:|---:|---:|"]
    for h in halves:
        med = "" if h["median_ranked_whitehats"] is None else f"{h['median_ranked_whitehats']:g}"
        med_a = "" if h.get("median_ranked_audit_type") is None else f"{h['median_ranked_audit_type']:g}"
        out.append(f"| {h['half']} | {h['competitions']} | {h['audit_type']} | {h['pool_usd']:,.0f} | {med} "
                   f"| {h.get('ranked_n', '')} | {med_a} |")
    out += ["", f"Competitions: {len(rows)}; leaderboards read: "
            f"{sum(1 for r in rows if r.get('ranked_whitehats'))}; PoC required: "
            f"{sum(1 for r in rows if r.get('poc_required'))}; information pages with AI wording anywhere "
            f"(project text or rules; see ai_lines): {sum(1 for r in rows if r.get('ai_mentions'))}.", ""]
    return "\n".join(out)


def snippets(lines: List[str], keys=SNIPPET_KEYS, before: int = 1, after: int = 2,
             cap: int = 60) -> List[str]:
    keep = set()
    for i, line in enumerate(lines):
        if any(k in line for k in keys):
            keep.update(range(max(0, i - before), min(len(lines), i + after + 1)))
    return [lines[i] for i in sorted(keep)][:cap]


def needs_sample(rec: Dict) -> bool:
    info = rec["information"]
    return (rec["slug"] in SAMPLE_SLUGS or info.get("start") is None or info.get("pool_usd") is None
            or rec["results"].get("max_rank") is None)


def safe_name(slug: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.\-]", "_", slug)


# ---------------------------------------------------------------- network

def get(url: str, retries: int = 3, pause: float = 5.0):
    """(status, bytes); bytes is None on 404 or if it never succeeds."""
    err: object = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return 404, None
            err = exc
            if exc.code in (403, 429):
                time.sleep(30.0)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            err = exc
        time.sleep(pause * (attempt + 1))
    print(f"giving up on {url}: {err}", file=sys.stderr)
    return getattr(err, "code", None) or -1, None


def read_text(path: str) -> Optional[str]:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


def cached(url: str, path: str, pause: float, index: Dict, offline: bool) -> Optional[str]:
    """The saved copy of url if there is one; otherwise fetch it (unless offline) and save it."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        index[url] = {"status": "cached", "bytes": os.path.getsize(path)}
        return read_text(path)
    if offline:
        index[url] = {"status": "missing"}
        return None
    status, body = get(url)
    index[url] = {"status": status, "bytes": len(body) if body else 0}
    time.sleep(pause)
    if body is None:
        return None
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(body)
    return body.decode("utf-8", errors="replace")


def write_sample(samples_dir: str, rec: Dict, pages: Dict[str, Optional[str]]) -> None:
    os.makedirs(samples_dir, exist_ok=True)
    out = [f"# {rec['slug']}"]
    for page, html in pages.items():
        raw_has = {k: (k in (html or "")) for k in ("Start Date", "Primary Pool", "Lines of Code", "__next_f")}
        out.append(f"== {page}: {len(html or '')} bytes; raw html contains {raw_has}")
        lines = html_to_lines(html)
        # Leaderboard rows carry handles: only the label lines of the information page are kept,
        # and the results page is reduced to rank-like numbers and a handle-free row shape.
        if page == "information":
            out.extend(snippets(lines))
        else:
            out.append(f"rank-like tokens: {sorted({int(x) for x in RANK_RE.findall(' '.join(lines))})[:40]}")
            out.append(f"results parse: {rec['results']}")
            out.append(f"row shape: {line_shape(lines)}")
    with open(os.path.join(samples_dir, safe_name(rec["slug"]) + ".txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", required=True, help="raw pages go to <data-dir>/raw, facts to facts.jsonl")
    parser.add_argument("--out-dir", default="", help="write immunefi_contests.csv, IMMUNEFI.md, summary here")
    parser.add_argument("--samples-dir", default="", help="write label snippets for a few competitions here")
    parser.add_argument("--pause", type=float, default=2.0, help="seconds after each fetched page")
    parser.add_argument("--parse-only", action="store_true", help="no network: read saved pages only")
    parser.add_argument("--fetched-on", default="", help="when the saved pages were fetched (parse-only re-runs)")
    args = parser.parse_args(list(argv) if argv is not None else None)

    raw = os.path.join(args.data_dir, "raw")
    os.makedirs(raw, exist_ok=True)
    index: Dict[str, Dict] = {}
    listing = cached(BASE + LISTING, os.path.join(raw, "_listing.html"), args.pause, index, args.parse_only)
    slugs = listing_slugs(listing)
    print(f"{len(slugs)} slugs on the listing", flush=True)
    if not slugs:
        return 1

    fetched_on = args.fetched_on or time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
    samples = 0
    records = []
    with open(os.path.join(args.data_dir, "facts.jsonl"), "w", encoding="utf-8") as fh:
        for n, slug in enumerate(slugs, 1):
            pages = {page: cached(f"{BASE}/audit-competition/{slug}/{suffix}",
                                  os.path.join(raw, safe_name(slug), page + ".html"),
                                  args.pause, index, args.parse_only)
                     for page, suffix in PAGES.items()}
            rec = competition_facts(slug, pages)
            rec["fetched_on"] = fetched_on
            records.append(rec)
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            if args.samples_dir and samples < MAX_SAMPLES and needs_sample(rec):
                write_sample(args.samples_dir, rec, pages)
                samples += 1
            info = rec["information"]
            print(f"{n:4d} {slug} [{info.get('kind')}]: {info.get('start')} -> {info.get('end')}, "
                  f"pool {info.get('pool_usd')}, ranked {rec['results'].get('max_rank')} "
                  f"({rec['results'].get('rank_method')})", flush=True)
    index_name = "parse_index.json" if args.parse_only else "fetch_index.json"
    with open(os.path.join(args.data_dir, index_name), "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=1, sort_keys=True)

    if args.out_dir:
        os.makedirs(args.out_dir, exist_ok=True)
        rows = [contest_row(r) for r in records if r["is_competition"]]
        rows.sort(key=lambda r: (r["start"] or "", r["slug"]))
        with open(os.path.join(args.out_dir, "immunefi_contests.csv"), "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["slug"])
            writer.writeheader()
            writer.writerows(rows)
        halves = by_half(rows)
        with open(os.path.join(args.out_dir, "IMMUNEFI.md"), "w", encoding="utf-8") as fh:
            fh.write(render_md(rows, halves, fetched_on))
        summary = {
            "slugs": len(slugs), "competitions": len(rows),
            "not_competitions": [r["slug"] for r in records if not r["is_competition"]],
            "missing_pool": [r["slug"] for r in rows if r["pool_usd"] is None],
            "missing_rank": [r["slug"] for r in rows if r["ranked_whitehats"] is None],
            "rank_methods": {str(m).lower(): sum(1 for r in rows if r["rank_method"] == m)
                             for m in ("hash", "bare", None)},
            "ai_lines": {r["slug"]: r["information"]["ai_lines"] for r in records
                         if r["information"].get("ai_mentions")},
            "by_half": halves, "fetched_on": fetched_on,
        }
        with open(os.path.join(args.out_dir, "immunefi_summary.json"), "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
