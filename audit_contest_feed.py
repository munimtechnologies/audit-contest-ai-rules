#!/usr/bin/env python3
"""audit_contest_feed.py -- one normalized JSON feed of smart-contract audit contests.

Combines two sources:
  * a live call to Sherlock's public classic-contest API
    (https://mainnet-contest.sherlock.xyz/contests?status=RUNNING), and
  * a hand-kept, dated snapshot of the other platforms (Cantina, HackenProof,
    Immunefi, CodeHawks, Certora, Sherlock Audit Engine) whose live listings are
    behind JavaScript or logins and have no open JSON API.

No third-party dependencies; Python 3.8+. The network call is isolated in one
function and injectable, so the tests run fully offline.

Made with AI agents working for MV2 of Munim, Inc.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import urllib.request
from typing import Callable, Dict, List, Optional

SNAPSHOT_DATE = "2026-10-14"
SHERLOCK_API = "https://mainnet-contest.sherlock.xyz/contests?status=RUNNING"

# Dated snapshot of platforms without an open live API. Keep in sync with README.
# ai_findings: "welcome" | "if_validated" | "allowed" | "prohibited" | "unknown"
# fee: True only if taking part requires moving money (an entry/submission fee).
SNAPSHOT: List[Dict] = [
    {
        "platform": "Sherlock Audit Engine",
        "name": "Engagements (invite-based)",
        "status": "invite_only",
        "prize_usd": None,
        "starts": None,
        "ends": None,
        "url": "https://audit-engine.sherlock.xyz/",
        "ai_findings": "welcome",
        "kyc": "not stated in public docs",
        "payout": "USDC on Polygon (or RLUSD on XRP Ledger)",
        "fee": False,
    },
    {
        "platform": "Cantina",
        "name": "Revert v4lend",
        "status": "live",
        "prize_usd": 50000,
        "starts": "2026-10-06",
        "ends": "2026-11-03",
        "url": "https://cantina.xyz/competitions",
        "ai_findings": "if_validated",
        "kyc": "required (Persona)",
        "payout": "USDC to an Ethereum mainnet address, weekly",
        "fee": False,
    },
    {
        "platform": "HackenProof",
        "name": "EverValue SCA DualDefense Audit",
        "status": "live",
        "prize_usd": 2500,
        "starts": "2026-10-02",
        "ends": "2026-10-16",
        "url": "https://hackenproof.com/audit-programs",
        "ai_findings": "unknown",
        "kyc": "only EU residents / programs that require it / after $5k",
        "payout": "USDC from platform balance, 100 USDC min, 2FA",
        "fee": False,
    },
    {
        "platform": "HackenProof",
        "name": "Digital Oro International SCA DualDefense Audit",
        "status": "live",
        "prize_usd": 3000,
        "starts": "2026-10-05",
        "ends": "2026-10-26",
        "url": "https://hackenproof.com/audit-programs",
        "ai_findings": "unknown",
        "kyc": "only EU residents / programs that require it / after $5k",
        "payout": "USDC from platform balance, 100 USDC min, 2FA",
        "fee": False,
    },
    {
        "platform": "HackenProof",
        "name": "DreamX Marketplace & DEX SCA DualDefense Audit",
        "status": "live",
        "prize_usd": 2500,
        "starts": "2026-10-12",
        "ends": "2026-10-26",
        "url": "https://hackenproof.com/audit-programs",
        "ai_findings": "unknown",
        "kyc": "only EU residents / programs that require it / after $5k",
        "payout": "USDC from platform balance, 100 USDC min, 2FA",
        "fee": False,
    },
    {
        "platform": "Immunefi",
        "name": "Audit competitions",
        "status": "none_live",
        "prize_usd": None,
        "starts": None,
        "ends": None,
        "url": "https://immunefi.com/audit-competition/",
        "ai_findings": "prohibited",
        "kyc": "per program",
        "payout": "per program",
        "fee": False,
    },
    {
        "platform": "CodeHawks",
        "name": "Competitions",
        "status": "none_live",
        "prize_usd": None,
        "starts": None,
        "ends": None,
        "url": "https://codehawks.cyfrin.io/",
        "ai_findings": "unknown",
        "kyc": "per contest",
        "payout": "USDC on ZKsync",
        "fee": False,
    },
    {
        "platform": "Certora",
        "name": "Formal verification contests",
        "status": "none_live",
        "prize_usd": None,
        "starts": None,
        "ends": None,
        "url": "https://www.certora.com/contests",
        "ai_findings": "unknown",
        "kyc": "per hosting platform",
        "payout": "per hosting platform",
        "fee": False,
    },
]


def _default_opener(url: str, timeout: float = 20.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "audit-contest-feed/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - public read-only API
        return resp.read().decode("utf-8")


def normalize_sherlock(payload: Dict) -> List[Dict]:
    """Map Sherlock's classic-contest API payload to normalized records.

    The API returns {"items": [...], "total": n, ...}. Item field names are
    read defensively with .get() because the list is empty when nothing runs.
    """
    out: List[Dict] = []
    for item in payload.get("items", []) or []:
        name = item.get("title") or item.get("name") or item.get("short_description") or "Sherlock contest"
        prize = item.get("prize_pool") or item.get("prizePool") or item.get("rewards")
        try:
            prize_usd: Optional[int] = int(prize) if prize is not None else None
        except (TypeError, ValueError):
            prize_usd = None
        slug = item.get("id") or item.get("slug")
        out.append(
            {
                "platform": "Sherlock",
                "name": name,
                "status": "live",
                "prize_usd": prize_usd,
                "starts": item.get("starts_at") or item.get("startDate") or item.get("starts"),
                "ends": item.get("ends_at") or item.get("endDate") or item.get("ends"),
                "url": f"https://audits.sherlock.xyz/contests/{slug}" if slug else "https://audits.sherlock.xyz/contests",
                "ai_findings": "unknown",
                "kyc": "per contest",
                "payout": "USDC",
                "fee": False,
                "source": "sherlock-api",
            }
        )
    return out


def fetch_sherlock(opener: Callable[[str], str] = _default_opener) -> List[Dict]:
    """Fetch live Sherlock classic contests. Returns [] on any network/parse error."""
    try:
        raw = opener(SHERLOCK_API)
        payload = json.loads(raw)
    except Exception:
        return []
    return normalize_sherlock(payload)


def days_left(record: Dict, today: _dt.date) -> Optional[int]:
    """Whole days from today until the record's end date, or None if unknown.

    Accepts "YYYY-MM-DD" or an ISO timestamp; anything unparseable gives None.
    """
    ends = record.get("ends")
    if not ends:
        return None
    try:
        end_date = _dt.date.fromisoformat(str(ends)[:10])
    except ValueError:
        return None
    return (end_date - today).days


def build_feed(
    include_live: bool = True,
    fetch: Callable[..., List[Dict]] = fetch_sherlock,
    today: Optional[_dt.date] = None,
) -> List[Dict]:
    """Return the merged feed: dated snapshot plus (optionally) live Sherlock rows.

    Each record gets a "days_left" field computed against today (UTC by default).
    """
    today = today or _dt.datetime.now(_dt.timezone.utc).date()
    feed: List[Dict] = []
    for row in SNAPSHOT:
        record = dict(row)
        record.setdefault("source", f"snapshot:{SNAPSHOT_DATE}")
        feed.append(record)
    if include_live:
        feed.extend(fetch())
    for record in feed:
        record["days_left"] = days_left(record, today)
    return feed


def filter_feed(
    feed: List[Dict],
    no_fee: bool = False,
    ai_ok: bool = False,
    ends_within: Optional[int] = None,
) -> List[Dict]:
    """Optionally drop fee-gated platforms, ones hostile to AI-made findings,
    and (with ends_within) anything not ending in the next N days.

    ends_within keeps only records with a known end date 0..N days away, so
    finished contests and open-ended listings are dropped.
    """
    result = feed
    if no_fee:
        result = [r for r in result if not r.get("fee")]
    if ai_ok:
        result = [r for r in result if r.get("ai_findings") != "prohibited"]
    if ends_within is not None:
        result = [
            r for r in result
            if r.get("days_left") is not None and 0 <= r["days_left"] <= ends_within
        ]
    return result


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="snapshot only, no network call")
    parser.add_argument("--no-fee", action="store_true", help="drop platforms that require a fee to enter")
    parser.add_argument("--ai-ok", action="store_true", help="drop platforms that prohibit AI-made findings")
    parser.add_argument("--ends-within", type=int, metavar="DAYS",
                        help="keep only contests ending within DAYS days")
    args = parser.parse_args(argv)

    feed = build_feed(include_live=not args.offline)
    feed = filter_feed(feed, no_fee=args.no_fee, ai_ok=args.ai_ok, ends_within=args.ends_within)
    print(json.dumps(feed, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
