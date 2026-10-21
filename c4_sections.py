#!/usr/bin/env python3
"""c4_sections.py -- score the pre-registered Code4rena README prediction (PREREGISTRATION.md).

Reads the JSONL written by fetch_c4_readmes.py and writes to --out-dir:
  c4_readme_sections.csv     one row per audit repository (flags and dates only)
  c4_sections_summary.json   counts by half-year, both verdicts, known-answer checks
  C4_SECTIONS.md             the same, for people

Licensed under Apache-2.0. Made with AI agents working for MV2 of Munim, Inc.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import datetime as _dt
import json
import os
from typing import Dict, Iterable, List, Optional

P1_LAST = _dt.date(2024, 6, 30)     # a P1 marker on an audit starting after this contradicts
P1_FIRST = _dt.date(2023, 4, 1)     # ... and so does one starting before this
P2_FROM = _dt.date(2025, 10, 6)     # Solidity audits from Hybra Finance on need V12

KNOWN = {
    "2025-10-hybra-finance": {"solidity": True, "v12": True, "start": "2025-10-06"},
    "2026-03-chainlink": {"solidity": True, "v12": True, "start": "2026-03-18"},
    "2023-04-frankencoin": {"auto_heading": True, "start": "2023-04-12"},
    "2024-12-secondswap": {"auto_heading": True, "analyzer_4naly3er": True, "start": "2024-12-09"},
}

COLUMNS = ["repo", "kind", "start", "date_source", "half", "auto_heading", "bot_words", "auto_output",
           "analyzer_4naly3er", "p1_marker", "bot_race_post_hoc", "v12", "v12_heading", "solidity", "exts",
           "readme_present", "sha256"]


def to_date(text: Optional[str]) -> Optional[_dt.date]:
    try:
        return _dt.date.fromisoformat(text) if text else None
    except ValueError:
        return None


def month_bounds(month: Optional[str]):
    """'2025-10' -> (date(2025, 10, 1), date(2025, 10, 31)); None for anything else."""
    try:
        y, m = (int(p) for p in (month or "").split("-"))
        return _dt.date(y, m, 1), _dt.date(y, m, calendar.monthrange(y, m)[1])
    except (ValueError, TypeError):
        return None


def after(row: Dict, cut: _dt.date) -> Optional[bool]:
    """True if the audit started after `cut`, False if on or before, None if the month straddles it."""
    start = to_date(row.get("start"))
    if start:
        return start > cut
    bounds = month_bounds(row.get("name_month"))
    if not bounds:
        return None
    if bounds[0] > cut:
        return True
    if bounds[1] <= cut:
        return False
    return None


def half_of(row: Dict) -> Optional[str]:
    start = to_date(row.get("start"))
    if start:
        return f"{start.year}H{1 if start.month <= 6 else 2}"
    bounds = month_bounds(row.get("name_month"))
    if bounds:
        return f"{bounds[0].year}H{1 if bounds[0].month <= 6 else 2}"
    return None


def make_row(rec: Dict) -> Dict:
    r = rec.get("readme") or {}
    present = bool(r.get("present"))
    row = {
        "repo": rec.get("repo"),
        "kind": rec.get("kind"),
        "name_month": rec.get("name_month"),
        "start": r.get("start"),
        "date_source": "readme" if r.get("start") else ("name" if rec.get("name_month") else "none"),
        "auto_heading": bool(r.get("auto_heading")),
        "bot_words": bool(r.get("bot_words")),
        "auto_output": bool(r.get("auto_output")),
        "analyzer_4naly3er": bool(r.get("analyzer_4naly3er")),
        "v12": bool(r.get("v12")),
        "v12_heading": bool(r.get("v12_heading")),
        "solidity": bool(r.get("solidity")),
        "exts": " ".join(r.get("exts") or []),
        "readme_present": present,
        "sha256": r.get("sha256") or "",
    }
    row["p1_marker"] = row["auto_heading"] or row["bot_words"]
    row["bot_race_post_hoc"] = row["bot_words"] or (row["auto_output"] and not row["analyzer_4naly3er"])
    row["half"] = half_of(row)
    return row


def sort_key(row: Dict):
    return (row.get("start") or (row.get("name_month") or "9999-99") + "-00", row.get("repo") or "")


def marker_test(rows: List[Dict], key: str) -> Dict:
    """P1-style test for one marker: first, last, and audits outside Apr 2023 - Jun 2024."""
    marked = sorted((r for r in rows if r[key]), key=sort_key)
    late = [r["repo"] for r in marked if after(r, P1_LAST) is True]
    early = [r["repo"] for r in marked if after(r, P1_FIRST - _dt.timedelta(days=1)) is False]
    unclear = [r["repo"] for r in marked
               if after(r, P1_LAST) is None or after(r, P1_FIRST - _dt.timedelta(days=1)) is None]
    first = marked[0] if marked else None
    last = marked[-1] if marked else None
    first_month = (first.get("start") or first.get("name_month") or "")[:7] if first else None
    if late or early:
        verdict = "CONTRADICTED"
    elif marked and not unclear and first_month == "2023-04":
        verdict = "HOLDS"
    else:
        verdict = "UNDETERMINED"
    return {
        "marker": key,
        "audits_marked": len(marked),
        "first": {"repo": first["repo"], "start": first.get("start"), "month": first.get("name_month")} if first else None,
        "first_is_frankencoin": bool(first and "frankencoin" in first["repo"]),
        "last": {"repo": last["repo"], "start": last.get("start"), "month": last.get("name_month")} if last else None,
        "after_2024_06_30": late,
        "before_2023_04_01": early,
        "undetermined": unclear,
        "verdict": verdict,
    }


def v12_test(rows: List[Dict]) -> Dict:
    sol = [r for r in rows if r["solidity"]]
    # "on or after 6 Oct" = "after 5 Oct"
    cut = P2_FROM - _dt.timedelta(days=1)
    inside = sorted((r for r in sol if after(r, cut) is True), key=sort_key)
    unclear = [r["repo"] for r in sol if after(r, cut) is None]
    missing = [r["repo"] for r in inside if not r["v12"]]
    if missing:
        verdict = "CONTRADICTED"
    elif inside and not unclear:
        verdict = "HOLDS"
    else:
        verdict = "UNDETERMINED"
    before_with_v12 = [r["repo"] for r in sol if after(r, cut) is False and r["v12"]]
    non_sol_after = [[r["repo"], r["v12"]] for r in rows if not r["solidity"] and after(r, cut) is True]
    return {
        "solidity_audits_from_2025_10_06": len(inside),
        "with_v12": len(inside) - len(missing),
        "without_v12": missing,
        "undetermined": unclear,
        "solidity_before_with_v12": before_with_v12,
        "non_solidity_from_2025_10_06": non_sol_after,
        "verdict": verdict,
    }


def known_checks(rows: List[Dict]) -> Dict:
    by_repo = {r["repo"]: r for r in rows}
    out = {}
    for repo, want in KNOWN.items():
        row = by_repo.get(repo)
        if row is None:
            out[repo] = {"ok": False, "problem": "not in the census"}
            continue
        bad = {k: [v, row.get(k)] for k, v in want.items() if row.get(k) != v}
        out[repo] = {"ok": not bad, "mismatch": bad}
    return out


def by_half(rows: List[Dict]) -> List[Dict]:
    halves: Dict[str, Dict] = {}
    for r in rows:
        h = r["half"] or "undated"
        c = halves.setdefault(h, {"half": h, "audits": 0, "readme": 0, "p1_marker": 0, "auto_heading": 0,
                                  "bot_words": 0, "bot_race_post_hoc": 0, "analyzer_4naly3er": 0,
                                  "solidity": 0, "v12": 0, "solidity_v12": 0})
        c["audits"] += 1
        c["readme"] += int(r["readme_present"])
        for k in ("p1_marker", "auto_heading", "bot_words", "bot_race_post_hoc", "analyzer_4naly3er",
                  "solidity", "v12"):
            c[k] += int(bool(r[k]))
        c["solidity_v12"] += int(r["solidity"] and r["v12"])
    return [halves[k] for k in sorted(halves)]


def load(path: str) -> List[Dict]:
    """Latest record per repository (a re-run appends; the last good line wins)."""
    latest: Dict[str, Dict] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("repo"):
                if rec.get("error") and rec["repo"] in latest:
                    continue
                latest[rec["repo"]] = rec
    return [latest[k] for k in sorted(latest)]


def summarize(records: List[Dict]) -> Dict:
    rows = sorted((make_row(r) for r in records), key=sort_key)
    audits = [r for r in rows if r["kind"] == "audit"]
    return {
        "rows": rows,
        "repositories": len(rows),
        "audits": len(audits),
        "mitigations": len(rows) - len(audits),
        "errors": sum(1 for r in records if r.get("error")),
        "readme_missing": sum(1 for r in audits if not r["readme_present"]),
        "dated_from_readme": sum(1 for r in audits if r["date_source"] == "readme"),
        "fetched_on": sorted({r.get("fetched_on") for r in records if r.get("fetched_on")}),
        "p1_as_written": marker_test(audits, "p1_marker"),
        "p1_post_hoc_bot_race": marker_test(audits, "bot_race_post_hoc"),
        "p1_auto_heading_only": marker_test(audits, "auto_heading"),
        "p2_v12": v12_test(audits),
        "known_answer_checks": known_checks(rows),
        "by_half": by_half(audits),
    }


def write_markdown(s: Dict, path: str) -> None:
    p1, ph, p2 = s["p1_as_written"], s["p1_post_hoc_bot_race"], s["p2_v12"]

    def show(items: List, n: int = 25) -> str:
        items = [str(i) for i in items]
        return ", ".join(items[:n]) + (f" (+{len(items) - n} more)" if len(items) > n else "") if items else "none"

    lines = [
        "# Code4rena audit READMEs, read section by section",
        "",
        f"READMEs read on {', '.join(s['fetched_on']) or 'unknown'}. {s['repositories']} repositories: {s['audits']} audits, "
        f"{s['mitigations']} mitigation reviews (left out of the tests). Audits without a README: {s['readme_missing']}; "
        f"dated from the README's Starts line: {s['dated_from_readme']} (the rest by the repository name's month). "
        f"Fetch errors: {s['errors']}.",
        "",
        "Pre-registered in PREREGISTRATION.md. Made with AI agents working for MV2 of Munim, Inc.",
        "",
        "## P1 as written (an \"Automated Findings\" heading or a bot-race phrase)",
        "",
        f"Verdict: **{p1['verdict']}**. Audits marked: {p1['audits_marked']}. First: {p1['first']} "
        f"(Frankencoin: {p1['first_is_frankencoin']}). Last: {p1['last']}.",
        f"Marked audits starting after 30 Jun 2024 ({len(p1['after_2024_06_30'])}): {show(p1['after_2024_06_30'])}.",
        f"Marked audits starting before 1 Apr 2023 ({len(p1['before_2023_04_01'])}): {show(p1['before_2023_04_01'])}.",
        f"Undetermined: {show(p1['undetermined'])}.",
        "",
        "## P1, secondary reading (POST HOC: defined after seeing one README; not pre-registered)",
        "",
        f"Bot-race phrase, or \"automated findings output\" without 4naly3er. Verdict: **{ph['verdict']}**. "
        f"Marked: {ph['audits_marked']}. First: {ph['first']}. Last: {ph['last']}.",
        f"After 30 Jun 2024 ({len(ph['after_2024_06_30'])}): {show(ph['after_2024_06_30'])}.",
        f"Before 1 Apr 2023 ({len(ph['before_2023_04_01'])}): {show(ph['before_2023_04_01'])}.",
        "",
        "## P2 (every Solidity audit from 6 Oct 2025 on has a V12 section)",
        "",
        f"Verdict: **{p2['verdict']}**. Solidity audits from 6 Oct 2025: {p2['solidity_audits_from_2025_10_06']}, "
        f"with V12: {p2['with_v12']}. Without V12: {show(p2['without_v12'])}. Undetermined: {show(p2['undetermined'])}.",
        f"Solidity audits before 6 Oct 2025 that mention V12: {show(p2['solidity_before_with_v12'])}.",
        f"Non-Solidity audits from 6 Oct 2025 (repo, V12): {show(p2['non_solidity_from_2025_10_06'])}.",
        "",
        "## Known-answer checks",
        "",
    ]
    for repo, res in s["known_answer_checks"].items():
        lines.append(f"- {repo}: {'ok' if res['ok'] else 'FAILED ' + json.dumps({k: v for k, v in res.items() if k != 'ok'})}")
    lines += ["", "## By start half-year (audits only)", "",
              "| Half | Audits | READMEs | P1 marker | Automated Findings heading | Bot-race phrase | Bot race (post hoc) "
              "| 4naly3er | Solidity | V12 | Solidity with V12 |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for c in s["by_half"]:
        lines.append(f"| {c['half']} | {c['audits']} | {c['readme']} | {c['p1_marker']} | {c['auto_heading']} | "
                     f"{c['bot_words']} | {c['bot_race_post_hoc']} | {c['analyzer_4naly3er']} | {c['solidity']} | "
                     f"{c['v12']} | {c['solidity_v12']} |")
    lines += ["", "Limits: READMEs as they stand today; `.sol` must be named in the README; private or deleted "
              "repositories are invisible.", ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--in", dest="inp", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)
    os.makedirs(args.out_dir, exist_ok=True)
    s = summarize(load(args.inp))
    with open(os.path.join(args.out_dir, "c4_readme_sections.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        for row in s["rows"]:
            w.writerow(row)
    summary = {k: v for k, v in s.items() if k != "rows"}
    with open(os.path.join(args.out_dir, "c4_sections_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    write_markdown(s, os.path.join(args.out_dir, "C4_SECTIONS.md"))
    print(json.dumps({k: summary[k] for k in ("repositories", "audits", "errors")}, sort_keys=True))
    print("P1 as written:", summary["p1_as_written"]["verdict"], "| P1 post hoc:",
          summary["p1_post_hoc_bot_race"]["verdict"], "| P2:", summary["p2_v12"]["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
