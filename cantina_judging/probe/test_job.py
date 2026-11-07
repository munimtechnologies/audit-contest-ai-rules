# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
import unittest

import job

ID = "e275368c-547d-4d91-a418-053ad31082a8"
OTHER = "fe8e03b1-f8db-4698-8a21-44b3a862e434"
HEAD = ["timestamp", "original", "statuscode", "mimetype", "length"]


class T(unittest.TestCase):
    def test_parse_rows_header(self):
        rows = job.parse_rows([HEAD, ["20261101000000", "https://x", "200", "a", "1"]])
        self.assertEqual(rows, [{"timestamp": "20261101000000", "original": "https://x",
                                 "statuscode": "200", "mimetype": "a", "length": "1"}])
        self.assertEqual(job.parse_rows([]), [])

    def test_competition_id(self):
        self.assertEqual(job.competition_id("https://cantina.xyz/competitions/%s?view=x" % ID.upper()), ID)
        self.assertIsNone(job.competition_id("https://cantina.xyz/competitions"))

    def test_day(self):
        self.assertEqual(job.day("20261106183700"), "2026-11-06")
        self.assertEqual(job.day(""), "")

    def test_summarise_api(self):
        rows = job.parse_rows([HEAD,
                               ["20261001000000", "u", "200", "j", "1"],
                               ["20261001120000", "u", "200", "j", "1"],
                               ["20261005000000", "u", "404", "j", "1"],
                               ["20261009000000", "u", "200", "j", "1"]])
        s = job.summarise_api(rows)
        self.assertEqual((s["rows"], s["status_200"], s["distinct_days_200"]), (4, 3, 2))
        self.assertEqual((s["first_200"], s["last_200"]), ("2026-10-01", "2026-10-09"))

    def test_summarise_pages(self):
        base = "https://cantina.xyz/competitions/"
        rows = job.parse_rows([HEAD,
                               ["20261010000000", base + ID, "200", "h", "1"],
                               ["20261011000000", base + ID + "/leaderboard", "200", "h", "1"],
                               ["20261011050000", base + ID, "302", "h", "1"],
                               ["20250101000000", base + OTHER, "200", "h", "1"],
                               ["20250101000000", base, "200", "h", "1"]])
        table, s = job.summarise_pages(rows)
        self.assertEqual(s["distinct_ids"], 2)
        self.assertEqual(s["rows_with_id"], 4)
        self.assertEqual(s["ids_with_2plus_days_200"], 1)
        self.assertEqual(s["v4lend"]["captures"], 3)
        self.assertEqual(s["v4lend"]["distinct_days_200"], 2)

    def test_build_url(self):
        u = job.build_url(job.QUERIES["api"], 10)
        self.assertIn("matchType=prefix", u)
        self.assertIn("limit=10", u)
        self.assertTrue(u.startswith(job.CDX))


if __name__ == "__main__":
    unittest.main()
