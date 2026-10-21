# c4-readme-sections-v1: result (for paper v1.9, section 4)

Written 19 Oct 2026 from the job's outputs (sandbox run 18:40-18:45Z 19 Oct 2026; `Ran 11 tests ... OK`; all four
known-answer checks "ok"; 481 CSV rows = 481 repositories). Pre-registration: `paper/c4-readme-sections-PREREGISTRATION.md`
(written before the run, unchanged). One wording fix on 21 Oct 2026, before publication: the last audit whose README links
a 4naly3er report is GTE Perps (28 Aug 2025), not Monad; Monad (15 Sep 2025) is the last with the heading (see below).
Made with AI agents working for MV2 of Munim, Inc. CC BY 4.0.

## One-line result

**The paper's section-4 prediction is contradicted on every reading, including the pre-registered one.** Code4rena's
"Automated Findings" section began in January 2023 (not April 2023) and outlived the bot race by 18 months: 60 audits that
started after 30 Jun 2024 still have it, 51 of them linking a 4naly3er static-analysis report (last: GTE Perps,
28 Aug 2025; the last with the heading at all is Monad, 15 Sep 2025). V12 reached 15 of the 16 Solidity audits from
6 Oct 2025 on, not all 16 (Brix Money, 26 Nov 2025, has none).

## What was read

481 public `code-423n4` repositories named `YYYY-MM-*` and not ending `-findings`: 442 audits, 39 mitigation reviews
(excluded). READMEs as they stood at 18:40Z 19 Oct 2026; 0 missing, 0 fetch errors; 384 dated from the README's
`Starts` line, 58 from the repository name's month.

## Verdicts (rules fixed in the pre-registration before the run)

| Test | Verdict | Count | Decisive cases |
|---|---|---:|---|
| P1 as written ("Automated Findings" heading OR bot-race phrase) | **CONTRADICTED** | 179 marked | 60 start after 30 Jun 2024 (Jul 2024 DittoETH ... Sep 2025 Monad); 12 before 1 Apr 2023 |
| P1 post hoc (bot-race phrase, or "automated findings output" without 4naly3er; NOT pre-registered) | **CONTRADICTED** | 84 marked | 0 after 30 Jun 2024; 11 before 1 Apr 2023 (first Canto Identity, 31 Jan 2023; last Coinbase, 14 Mar 2024) |
| P2 (every Solidity audit from 6 Oct 2025 has V12) | **CONTRADICTED** | 16 Solidity audits, 15 with V12 | 2025-11-brix-money (starts 26 Nov 2025): 15 `.sol` files in scope, no "V12" anywhere |

Disclosed before the run: SecondSwap (9 Dec 2024) had been seen by hand, so P1-as-written was expected to fail; the
post hoc reading was defined after that peek. P2 was blind and also failed.

## Spot checks after the run (raw READMEs, 19 Oct ~19:25Z)

- **2025-11-brix-money**: "Starts November 26, 2025 20:00 UTC"; "Files in scope" names 15 Solidity files; no "V12";
  no automated-findings section at all (only a Zellic manual audit is cited). The P2 contradiction is real, not a
  parser slip.
- **2023-01-canto-identity**: "Starts January 31, 2023 20:00 UTC"; heading "Automated Findings / Publicly Known
  Issues"; "Automated findings output for the contest can be found here within an hour of contest opening." No
  "bot race" phrase. So the automated-findings section predates Frankencoin (12 Apr 2023) by about ten weeks.
- **2022-01-dev-test-repo**: a misnamed repository. Its README is the "Contest details are not available" notice of
  the invite-only Panoptic audit (Nov 2023) with a 4naly3er link. By the pre-registered rule it is dated by name
  (2022-01) and counted "before 1 Apr 2023". Dropping it changes no verdict: 11 other audits (Jan-Mar 2023) still
  fall before the cut-off and 60 after it. Flagged here as a data-quality caveat, not corrected post hoc.

## The 60 marked audits after 30 Jun 2024 (checked 21 Oct 2026 against `data/c4_readme_sections.csv`)

- 51 have the heading and a 4naly3er link. The last is 2025-08-gte-perps (28 Aug 2025).
- 9 have the heading without a 4naly3er link: 2024-09-kakarot, 2024-11-nibiru, 2024-11-mantra-dex, 2024-12-unruggable,
  2025-01-pump-science, 2025-02-initia-cosmos, 2025-02-blend, 2025-04-cabal and 2025-09-monad. Eight of the nine are
  audits of non-Solidity code or of Solidity next to another language (Cairo, Go, Rust, Move, or no file type named);
  Unruggable (Solidity only) is the exception.

## What the half-year table says (audits only)

| Half | Audits | Auto. Findings heading | Bot-race phrase | 4naly3er | Solidity | Solidity with V12 |
|---|---:|---:|---:|---:|---:|---:|
| 2022H2 | 50 | 0 | 0 | 0 | 48 | 0 |
| 2023H1 | 43 | 31 | 10 | 0 | 41 | 0 |
| 2023H2 | 47 | 45 | 41 | 15 | 47 | 0 |
| 2024H1 | 58 | 41 | 13 | 39 | 41 | 0 |
| 2024H2 | 55 | 34 | 0 | 30 | 32 | 0 |
| 2025H1 | 23 | 20 | 0 | 16 | 15 | 0 |
| 2025H2 | 22 | 6 | 0 | 5 | 16 | 10 |
| 2026H1 | 7 | 0 | 0 | 0 | 5 | 5 |

(2021H1-2022H1: 137 audits, one heading (the misnamed dev-test repo), no bot-race phrase, no V12.)

Reading: the bot-race *phrase* does trace the shape the paper described (appears 2023H1, peaks 2023H2, gone after
2024H1, last Coinbase 14 Mar 2024). But the *section* the paper used as its marker did not go away with the bot
race: from 2024H2 it mostly carried 4naly3er static-analysis reports instead, in 34 of 55, then 20 of 23, then 6 of 22
audits, and only reaches zero in 2026H1. V12 appears in 2025H2 (10 of 16 Solidity audits; all 10 start on or after
6 Oct 2025) and 5 of 5 Solidity audits in 2026H1; one non-Solidity audit (2026-04-k2) also carries V12.

## Files

- `data/c4_readme_sections.csv` (481 rows + header; columns: repo, kind, start, date_source, half, auto_heading,
  bot_words, auto_output, analyzer_4naly3er, p1_marker, bot_race_post_hoc, v12, v12_heading, solidity, exts,
  readme_present, sha256). Counts and flags only, no README text.
- `data/c4_sections_summary.json`: every count above.
- `paper/c4-readme-sections-PREREGISTRATION.md` and `paper/c4-readme-sections-C4_SECTIONS.md`: the pre-registration
  and the job's own report.
- Code: `fetch_c4_readmes.py`, `c4_sections.py`, `test_c4_readme_sections.py` (11 offline tests).

Limits (unchanged from the pre-registration): READMEs as they stand today; `.sol` must be named in the README;
private or deleted repositories are invisible; dates by repository-name month for 58 audits; one misnamed repository.
