"""Offline tests for crowding.py. They pin the numbers quoted in the README."""
import datetime as dt

import crowding as c

ROWS = c.load_competitions()
TIERS = c.load_tiers()


def test_table_is_well_formed():
    assert len(ROWS) == 21
    names = [r["name"] for r in ROWS]
    assert len(set(names)) == len(names)
    for r in ROWS:
        assert r["start"] <= r["end"], r["name"]
        assert r["status"] in {"completed", "live"}
        assert r["prize_currency"] in {"USD", "USDC", "OP"}
        assert r["findings_submitted"] > 0
        assert r["url"].startswith("https://cantina.xyz/competitions/")
    assert [r["name"] for r in ROWS if r["status"] == "live"] == ["Revert v4lend"]


def test_contest_days_and_rates():
    by_name = {r["name"]: r for r in ROWS}
    assert c.contest_days(by_name["daao-contracts"]) == 4
    assert c.per_day(by_name["daao-contracts"]) == 231
    assert c.contest_days(by_name["size-solidity"]) == 14
    assert abs(c.per_1k_usd(by_name["uniswap-v4"]) - 451 / 2350) < 1e-9
    assert c.per_1k_usd(by_name["gamma-univ4-limit-orders"]) is None  # OP pot


def test_live_contest_uses_elapsed_days():
    live = [r for r in ROWS if r["status"] == "live"][0]
    assert c.contest_days(live) == 8  # 6 Oct to 14 Oct 2026
    assert abs(c.per_day(live) - 160.25) < 1e-9
    later = dict(live, checked_on=dt.date(2026, 12, 1))
    assert c.contest_days(later) == 28  # capped at the end date


def test_medians_by_year_match_readme():
    m = c.medians_by_year(ROWS)
    assert {y: v["n"] for y, v in m.items()} == {2024: 4, 2025: 9, 2026: 7}
    assert abs(m[2024]["median"] - (451 / 25 + 977 / 34) / 2) < 1e-9
    assert abs(m[2025]["median"] - 790 / 21) < 1e-9
    assert m[2026]["median"] == 146.5


def test_small_pot_medians_match_readme():
    m = c.medians_by_year(ROWS, max_usd_prize=60000)
    assert 2024 not in m
    assert m[2025]["n"] == 6 and abs(m[2025]["median"] - (664 / 21 + 253 / 6) / 2) < 1e-9
    assert m[2026]["n"] == 5 and m[2026]["median"] == 146.5


def test_per_1k_medians():
    m = c.medians_by_year(ROWS, metric=c.per_1k_usd)
    assert m[2025]["n"] == 8 and m[2026]["n"] == 6
    assert abs(m[2026]["median"] - (3890 / 400 + 1248 / 50) / 2) < 1e-9


def test_revert_payout_concentration():
    lend = c.top_share(TIERS, "Revert Finance", 2, 50000)
    assert lend["researchers"] == 8
    assert lend["paid_usd"] == 41352.04
    assert round(lend["share"], 3) == 0.827
    every = c.top_share(TIERS, "Revert Finance", 99, 50000)
    assert every["researchers"] == 59
    assert abs(every["paid_usd"] - 50000) < 1  # tiers add up to the pool
    stable = c.top_share(TIERS, "Revert Finance - StableSwap Hooks", 10, 50000)
    assert stable["researchers"] == 10
    assert round(stable["share"], 3) == 0.761


def test_main_runs(capsys):
    assert c.main([]) == 0
    assert '"per_day_by_year"' in capsys.readouterr().out
    assert c.main(["--table"]) == 0
    assert "Revert v4lend" in capsys.readouterr().out
