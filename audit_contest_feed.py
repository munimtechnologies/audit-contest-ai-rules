#!/usr/bin/env python3
"""audit_contest_feed.py -- one normalized JSON feed of smart-contract audit contests.

Combines two sources:
  * a live call to Sherlock's public classic-contest API
    (https://mainnet-contest.sherlock.xyz/contests?status=RUNNING), and
  * a hand-kept, dated snapshot of the other platforms (Cantina, HackenProof,
    Immunefi, CodeHawks, Certora, Sherlock Audit Engine) whose live listings are
    behind JavaScript or logins and have no open JSON API.

The snapshot is a claim about one day, not a live listing. Rules about AI-made
findings change (the Sherlock Audit Engine row changed between the 2026-10-14
and 2026-11-08 snapshots), so always read the contest's own rules page before
taking part. When the snapshot is more than STALE_AFTER_DAYS old, main() prints
a warning to stderr.

No third-party dependencies; Python 3.8+. The network call is isolated in one
function and injectable, so the tests run fully offline.

Licensed under Apache-2.0.
Made with AI agents working for MV2 of Munim, Inc.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
import urllib.request
from typing import Callable, Dict, List, Optional

SNAPSHOT_DATE = "2026-11-08"
STALE_AFTER_DAYS = 14
SHERLOCK_API = "https://mainnet-contest.sherlock.xyz/contests?status=RUNNING"

# ai_findings labels:
#   "welcome"       the platform or contest invites AI auditors / AI-made findings
#   "if_validated"  allowed if a human validates them (PoC, review); unvalidated ones are penalised
#   "allowed"       allowed, no extra condition found
#   "varies"        set per program or engagement: read each one's own page
#   "human_only"    only human researchers may take part
#   "prohibited"    the platform's terms ban AI-generated or automated reports
#   "unknown"       no rule found
AI_LABELS = ("welcome", "if_validated", "allowed", "varies", "human_only", "prohibited", "unknown")
# Labels that --ai-ok drops: work made with AI agents cannot honestly be entered there.
AI_EXCLUDED = ("prohibited", "human_only")

# status labels: "live" (open for submissions; needs an end date), "judging" (closed,
# being judged), "invite_only", "none_live" (nothing open on the listing that day).
STATUS_LABELS = ("live", "judging", "invite_only", "none_live")

# Dated snapshot of platforms without an open live API. Each row was read at its
# source on SNAPSHOT_DATE (or on the date given in its ai_note).
# fee: True only if taking part requires moving money (an entry/submission fee).
SNAPSHOT: List[Dict] = [
    {
        "platform": "Sherlock Audit Engine",
        "name": "Engagements (application- and invite-based)",
        "status": "invite_only",
        "prize_usd": None,
        "starts": None,
        "ends": None,
        "url": "https://audit-engine.sherlock.xyz/",
        "ai_findings": "varies",
        "ai_note": "In Oct 2026 the platform listed 'AI auditors' as a participant type; the "
                   "Uniswap engagement posted 2026-11-04 is for human researchers only (row below). "
                   "Read each engagement's own rules.",
        "kyc": "required before accepting an engagement",
        "payout": "USDC on Polygon (or RLUSD on XRP Ledger)",
        "fee": False,
    },
    {
        "platform": "Sherlock Audit Engine",
        "name": "Uniswap Audit Engine",
        "status": "live",
        "prize_usd": 20000,
        "starts": "2026-11-06",
        "ends": "2026-11-16",
        "url": "https://audit-engine.sherlock.xyz/",
        "ai_findings": "human_only",
        "ai_note": "Engagement page (signed-in dashboard, read 2026-11-06): 'This application is only "
                   "for human researchers, not purposefully built AI tools'. prize_usd is the stated "
                   "guaranteed amount; applications, 40 spots.",
        "kyc": "none shown on the engagement page (2026-11-06)",
        "payout": "USDC on Polygon (or RLUSD on XRP Ledger)",
        "fee": False,
    },
    {
        "platform": "Cantina",
        "name": "Revert v4lend",
        "status": "judging",
        "prize_usd": 50000,
        "starts": "2026-10-06",
        "ends": "2026-11-03",
        "url": "https://cantina.xyz/competitions/e275368c-547d-4d91-a418-053ad31082a8",
        "ai_findings": "if_validated",
        "ai_note": "Cantina: unvalidated AI findings 'can lead to disqualifications or worse, a permanent ban'. "
                   "No other public competition listed on 2026-11-08.",
        "kyc": "required (Persona)",
        "payout": "USDC to an Ethereum mainnet address, weekly",
        "fee": False,
    },
    {
        "platform": "HackenProof",
        "name": "Audit programs",
        "status": "none_live",
        "prize_usd": None,
        "starts": None,
        "ends": None,
        "url": "https://hackenproof.com/audit-programs",
        "ai_findings": "varies",
        "ai_note": "AI rules are set per program (62 of 102 programs had one in Oct 2026). "
                   "Newest listed programs all finished by 2026-10-26.",
        "kyc": "only EU residents / programs that require it / after $5k",
        "payout": "USDC from platform balance, 100 USDC min, 2FA",
        "fee": False,
    },
    {
        "platform": "Immunefi",
        "name": "Plether",
        "status": "live",
        "prize_usd": 80000,
        "starts": "2026-11-02",
        "ends": "2026-11-16",
        "url": "https://immunefi.com/audit-competition/plether/information/",
        "ai_findings": "prohibited",
        "ai_note": "Immunefi's terms ban 'submitting AI-generated/automated scanner bug reports'. "
                   "Ends 2026-11-16 10:00 UTC.",
        "kyc": "not required for payout (competition page)",
        "payout": "USDC on Ethereum",
        # Per-report submission fee, "shown at submission time" (competition page, 2026-11-08).
        "fee": True,
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
        "ai_note": "Most recent listing: BattleChain Confidence Pools (July 2026).",
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
        "ai_note": "All listed contests completed; most recent: Aquarius.",
        "kyc": "per hosting platform",
        "payout": "per hosting platform",
        "fee": False,
    },
]


def _default_opener(url: str, timeout: float = 20.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "audit-contest-feed/1.1"})
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


def snapshot_age_days(today: _dt.date) -> int:
    """Whole days between SNAPSHOT_DATE and today."""
    return (today - _dt.date.fromisoformat(SNAPSHOT_DATE)).days


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
    """Optionally drop fee-gated platforms, ones closed to AI-made findings
    (prohibited or human-only), and (with ends_within) anything not ending in
    the next N days.

    ends_within keeps only records with a known end date 0..N days away, so
    finished contests and open-ended listings are dropped.
    """
    result = feed
    if no_fee:
        result = [r for r in result if not r.get("fee")]
    if ai_ok:
        result = [r for r in result if r.get("ai_findings") not in AI_EXCLUDED]
    if ends_within is not None:
        result = [
            r for r in result
            if r.get("days_left") is not None and 0 <= r["days_left"] <= ends_within
        ]
    return result


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--offline", action="store_true", help="snapshot only, no network call")
    parser.add_argument("--no-fee", action="store_true", help="drop platforms that require a fee to enter")
    parser.add_argument("--ai-ok", action="store_true",
                        help="drop contests that prohibit AI-made findings or admit human researchers only")
    parser.add_argument("--ends-within", type=int, metavar="DAYS",
                        help="keep only contests ending within DAYS days")
    args = parser.parse_args(argv)

    today = _dt.datetime.now(_dt.timezone.utc).date()
    age = snapshot_age_days(today)
    if age > STALE_AFTER_DAYS:
        print(
            f"warning: snapshot is {age} days old (from {SNAPSHOT_DATE}); "
            "re-check each platform's own page before relying on it",
            file=sys.stderr,
        )
    feed = build_feed(include_live=not args.offline, today=today)
    feed = filter_feed(feed, no_fee=args.no_fee, ai_ok=args.ai_ok, ends_within=args.ends_within)
    print(json.dumps(feed, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
