"""Offline tests for audit_contest_feed. No network is used. Apache-2.0.
Made with AI agents working for MV2 of Munim, Inc."""
import datetime as dt
import json

import audit_contest_feed as f

SNAP_DAY = dt.date(2026, 11, 8)


def test_snapshot_rows_are_well_formed():
    required = {"platform", "name", "status", "ai_findings", "kyc", "payout", "fee"}
    for row in f.SNAPSHOT:
        assert required <= set(row), f"missing keys in {row.get('name')}"
        assert isinstance(row["fee"], bool)
        assert row["ai_findings"] in {
            "welcome", "if_validated", "allowed", "varies", "human_only", "prohibited", "unknown",
        }
        assert row["status"] in set(f.STATUS_LABELS), row["name"]


def test_label_tuples_are_consistent():
    assert set(f.AI_EXCLUDED) <= set(f.AI_LABELS)
    assert set(f.AI_EXCLUDED) == {"prohibited", "human_only"}


def test_snapshot_dates_parse_and_order():
    for row in f.SNAPSHOT:
        starts, ends = row.get("starts"), row.get("ends")
        if starts and ends:
            assert dt.date.fromisoformat(starts) <= dt.date.fromisoformat(ends), row["name"]
        if row["status"] in ("live", "judging"):
            assert ends, f"{row['status']} row without an end date: {row['name']}"


def test_snapshot_date_is_iso():
    assert dt.date.fromisoformat(f.SNAPSHOT_DATE) == SNAP_DAY


def test_snapshot_age_days():
    assert f.snapshot_age_days(SNAP_DAY) == 0
    assert f.snapshot_age_days(dt.date(2026, 11, 23)) == 15
    assert f.snapshot_age_days(dt.date(2026, 11, 23)) > f.STALE_AFTER_DAYS


def test_normalize_sherlock_empty():
    assert f.normalize_sherlock({"items": [], "total": 0}) == []
    assert f.normalize_sherlock({}) == []


def test_normalize_sherlock_maps_fields():
    payload = {
        "items": [
            {"id": "abc", "title": "Demo Protocol", "prize_pool": "25000", "ends_at": "2026-12-01"},
            {"slug": "xyz", "name": "Other", "rewards": None},
        ],
        "total": 2,
    }
    rows = f.normalize_sherlock(payload)
    assert len(rows) == 2
    assert rows[0]["platform"] == "Sherlock"
    assert rows[0]["name"] == "Demo Protocol"
    assert rows[0]["prize_usd"] == 25000
    assert rows[0]["ends"] == "2026-12-01"
    assert "abc" in rows[0]["url"]
    assert rows[0]["source"] == "sherlock-api"
    # Non-numeric / missing prize degrades to None, never raises.
    assert rows[1]["prize_usd"] is None


def test_fetch_sherlock_swallows_errors():
    def boom(url):
        raise OSError("no network in tests")

    assert f.fetch_sherlock(opener=boom) == []


def test_fetch_sherlock_with_fake_opener():
    body = json.dumps({"items": [{"id": "1", "title": "Live One", "prize_pool": 1000}], "total": 1})
    rows = f.fetch_sherlock(opener=lambda url: body)
    assert len(rows) == 1
    assert rows[0]["name"] == "Live One"


def test_build_feed_offline_is_snapshot_only():
    feed = f.build_feed(include_live=False)
    assert len(feed) == len(f.SNAPSHOT)
    assert all(r["source"].startswith("snapshot:") for r in feed)


def test_build_feed_merges_live_rows():
    fake = lambda: [{"platform": "Sherlock", "name": "Live", "source": "sherlock-api"}]
    feed = f.build_feed(include_live=True, fetch=fake)
    assert len(feed) == len(f.SNAPSHOT) + 1
    assert feed[-1]["name"] == "Live"
    assert feed[-1]["days_left"] is None


def test_build_feed_does_not_mutate_snapshot():
    f.build_feed(include_live=False, today=SNAP_DAY)
    assert all("days_left" not in row for row in f.SNAPSHOT)


def test_days_left():
    today = dt.date(2026, 10, 14)
    assert f.days_left({"ends": "2026-10-16"}, today) == 2
    assert f.days_left({"ends": "2026-11-03T12:00:00Z"}, today) == 20
    assert f.days_left({"ends": "2026-10-01"}, today) == -13
    assert f.days_left({"ends": None}, today) is None
    assert f.days_left({}, today) is None
    assert f.days_left({"ends": "soon"}, today) is None


def test_filter_no_fee_and_ai_ok():
    feed = [
        {"platform": "A", "fee": True, "ai_findings": "welcome"},
        {"platform": "B", "fee": False, "ai_findings": "prohibited"},
        {"platform": "C", "fee": False, "ai_findings": "if_validated"},
        {"platform": "D", "fee": False, "ai_findings": "human_only"},
        {"platform": "E", "fee": False, "ai_findings": "varies"},
    ]
    assert len(f.filter_feed(feed, no_fee=True)) == 4
    assert [r["platform"] for r in f.filter_feed(feed, ai_ok=True)] == ["A", "C", "E"]
    kept = f.filter_feed(feed, no_fee=True, ai_ok=True)
    assert [r["platform"] for r in kept] == ["C", "E"]


def test_filter_ends_within():
    feed = [
        {"platform": "Soon", "days_left": 2},
        {"platform": "Later", "days_left": 20},
        {"platform": "Over", "days_left": -3},
        {"platform": "Open", "days_left": None},
    ]
    assert [r["platform"] for r in f.filter_feed(feed, ends_within=7)] == ["Soon"]
    assert [r["platform"] for r in f.filter_feed(feed, ends_within=30)] == ["Soon", "Later"]


def test_ends_within_on_snapshot():
    feed = f.build_feed(include_live=False, today=SNAP_DAY)
    assert f.filter_feed(feed, ends_within=7) == []
    soon = f.filter_feed(feed, ends_within=8)
    assert [r["name"] for r in soon] == ["Uniswap Audit Engine", "Plether"]


def test_nothing_open_to_ai_made_work_on_snapshot_day():
    # On 2026-11-08 both open contests were closed to AI-made work (human-only / banned).
    feed = f.build_feed(include_live=False, today=SNAP_DAY)
    open_now = f.filter_feed(feed, ends_within=8)
    assert open_now
    assert f.filter_feed(open_now, ai_ok=True) == []
    assert [r["name"] for r in f.filter_feed(open_now, no_fee=True)] == ["Uniswap Audit Engine"]


def test_v4lend_is_judging():
    rows = [r for r in f.SNAPSHOT if r["name"] == "Revert v4lend"]
    assert len(rows) == 1 and rows[0]["status"] == "judging"


def test_audit_engine_uniswap_is_human_only():
    rows = [r for r in f.SNAPSHOT if r["name"] == "Uniswap Audit Engine"]
    assert len(rows) == 1
    assert rows[0]["ai_findings"] == "human_only"
    assert "human researchers" in rows[0]["ai_note"]


def test_immunefi_marked_prohibited():
    immunefi = [r for r in f.SNAPSHOT if r["platform"] == "Immunefi"]
    assert immunefi and immunefi[0]["ai_findings"] == "prohibited"
