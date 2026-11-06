# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working for MV2 of Munim, Inc.
"""Re-check the hand-computed arrival rates of the Revert v4lend (Cantina) findings counter.

Reads v4lend_findings_count.csv (row, read_at_utc, time_is_approx, findings_submitted, reads),
checks it is well formed, and writes:
  - windows.csv: rate between each pair of consecutive readings
  - day_table_hand.csv: the day table as built by hand (README anchors), recomputed
  - day_table_nearest.csv: the day table using, for each UTC day, the reading nearest 00:00Z
  - summary.json: totals, $ per finding, anchors where the two tables differ
Standard library only. No network.
"""
import argparse
import csv
import json
import os
from datetime import datetime, timedelta, timezone

POT_USD = 50000

# Anchor rows used by the hand-built day table in README-v4lend-data.md (runs 209-215).
HAND_ANCHORS = [2, 11, 23, 29, 35, 41, 46, 52, 57, 61, 66, 70, 73, 76, 80]


def parse_time(text):
    return datetime.strptime(text, "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = []
        for rec in csv.DictReader(f):
            rows.append({
                "row": int(rec["row"]),
                "at": parse_time(rec["read_at_utc"]),
                "approx": rec["time_is_approx"],
                "count": int(rec["findings_submitted"]),
                "reads": int(rec["reads"]),
            })
    return rows


def check_rows(rows):
    """Return a list of problems (empty if the series is well formed)."""
    problems = []
    for i, r in enumerate(rows):
        if r["row"] != i + 1:
            problems.append("row %d: expected number %d" % (r["row"], i + 1))
        if r["approx"] not in ("yes", "no"):
            problems.append("row %d: time_is_approx %r" % (r["row"], r["approx"]))
        if r["reads"] not in (1, 2):
            problems.append("row %d: reads %d" % (r["row"], r["reads"]))
        if i:
            prev = rows[i - 1]
            if r["at"] <= prev["at"]:
                problems.append("row %d: time not after row %d" % (r["row"], prev["row"]))
            if r["count"] < prev["count"]:
                problems.append("row %d: count fell below row %d" % (r["row"], prev["row"]))
    return problems


def span(a, b):
    hours = (b["at"] - a["at"]).total_seconds() / 3600.0
    new = b["count"] - a["count"]
    return {
        "from_row": a["row"], "to_row": b["row"],
        "from_utc": a["at"].strftime("%Y-%m-%dT%H:%MZ"),
        "to_utc": b["at"].strftime("%Y-%m-%dT%H:%MZ"),
        "hours": hours, "new": new, "per_hour": new / hours,
    }


def windows(rows):
    return [span(rows[i - 1], rows[i]) for i in range(1, len(rows))]


def nearest_anchor(rows, midnight):
    """Row number of the reading nearest midnight (ties go to the earlier reading)."""
    best = min(rows, key=lambda r: (abs((r["at"] - midnight).total_seconds()), r["at"]))
    return best["row"]


def nearest_anchors(rows, first_day, last_day):
    day = parse_time(first_day + "T00:00Z")
    end = parse_time(last_day + "T00:00Z")
    out = []
    while day <= end:
        out.append((day.strftime("%Y-%m-%d"), nearest_anchor(rows, day)))
        day += timedelta(days=1)
    return out


def day_table(rows, anchor_rows):
    by_num = {r["row"]: r for r in rows}
    return [span(by_num[a], by_num[b]) for a, b in zip(anchor_rows, anchor_rows[1:])]


def write_csv(path, spans):
    cols = ["from_row", "to_row", "from_utc", "to_utc", "hours", "new", "per_hour"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for s in spans:
            w.writerow([s["from_row"], s["to_row"], s["from_utc"], s["to_utc"],
                        "%.2f" % s["hours"], s["new"], "%.2f" % s["per_hour"]])


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--first-day", default="2026-10-15")
    p.add_argument("--last-day", default="2026-10-29")
    a = p.parse_args(argv)

    rows = load_rows(a.csv)
    problems = check_rows(rows)
    os.makedirs(a.out_dir, exist_ok=True)

    near = nearest_anchors(rows, a.first_day, a.last_day)
    near_rows = [n for _, n in near]
    hand_days = dict(zip([d for d, _ in near], HAND_ANCHORS)) if len(near) == len(HAND_ANCHORS) else {}
    differ = [{"day": d, "hand_row": hand_days[d], "nearest_row": n}
              for d, n in near if d in hand_days and hand_days[d] != n]

    hand = day_table(rows, HAND_ANCHORS)
    nearest = day_table(rows, near_rows)
    write_csv(os.path.join(a.out_dir, "windows.csv"), windows(rows))
    write_csv(os.path.join(a.out_dir, "day_table_hand.csv"), hand)
    write_csv(os.path.join(a.out_dir, "day_table_nearest.csv"), nearest)

    first, last = rows[0], rows[-1]
    overall = span(first, last)
    summary = {
        "rows": len(rows),
        "problems": problems,
        "first": {"row": first["row"], "utc": overall["from_utc"], "count": first["count"]},
        "last": {"row": last["row"], "utc": overall["to_utc"], "count": last["count"]},
        "overall_per_hour": round(overall["per_hour"], 3),
        "pot_usd_per_finding": round(POT_USD / last["count"], 2),
        "nearest_anchors": near,
        "anchors_differing_from_hand_table": differ,
        "hand_table_sum": sum(s["new"] for s in hand),
        "nearest_table_sum": sum(s["new"] for s in nearest),
        "hand_table_per_hour_range": [round(min(s["per_hour"] for s in hand), 2),
                                      round(max(s["per_hour"] for s in hand), 2)],
        "nearest_table_per_hour_range": [round(min(s["per_hour"] for s in nearest), 2),
                                         round(max(s["per_hour"] for s in nearest), 2)],
    }
    with open(os.path.join(a.out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
