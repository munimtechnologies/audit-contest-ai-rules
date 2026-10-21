# c4-readme-sections-v1: test of a prediction written down before testing

Written 2026-10-19 ~18:00Z, before the job runs. Made with AI agents working for MV2 of Munim, Inc. CC BY 4.0.

## The prediction (paper v1.8, section 4, published 16 Oct 2026, unchanged since)

> If Code4rena's audit READMEs are read section by section, audits whose README links a winning bot report or an
> "Automated Findings" section should begin in April 2023 (Frankencoin first) and stop by about March-April 2024, with
> none after mid-2024; and every Solidity audit from Hybra Finance (6 Oct 2025) on should carry a V12 section.
> [...] A bot-race section after June 2024, or a Solidity audit after 6 Oct 2025 without a V12 section, would
> contradict it.

Source: https://github.com/munimtechnologies/audit-contest-ai-rules/blob/main/paper/audit-contest-census.md

## What is read

Every public repository of the `code-423n4` GitHub organization named `YYYY-MM-<name>` and not ending in `-findings`
(the audit repositories), its `README.md` at the default branch as it stands on the day of the run. Repositories with
"mitigation" in the name are mitigation reviews: counted separately, left out of both tests.

## Operational definitions (fixed now)

- **Start date**: the README's `Starts <Month> <day>, <year>` line. If it has none, the repository name's month
  (`YYYY-MM`) is used, and a test treats the audit as undetermined whenever that month straddles the test's cut-off.
- **P1 marker (as written)**: the README has a Markdown heading containing "Automated Findings", OR mentions "bot race",
  "winning bot" or "bot report" anywhere.
- **P1 verdict**: CONTRADICTED if any audit with the marker starts after 30 Jun 2024 or before 1 Apr 2023. HOLDS if
  none does, none is undetermined, and the earliest marked audit starts in April 2023. Otherwise UNDETERMINED.
  Whether the earliest is Frankencoin is reported but is not part of the verdict.
- **Solidity audit**: the README names at least one `.sol` file.
- **V12 section**: the README contains "V12" (case-sensitive, as a whole word).
- **P2 verdict**: among Solidity audits starting on or after 6 Oct 2025, CONTRADICTED if any lacks V12. HOLDS if there
  is at least one, all have V12 and none is undetermined. Otherwise UNDETERMINED.

## Known-answer checks (must come out as stated, or the parser is wrong)

- 2025-10-hybra-finance: Solidity, V12, start 2025-10-06.
- 2026-03-chainlink: Solidity, V12, start 2026-03-18.
- 2023-04-frankencoin: "Automated Findings" heading, start 2023-04-12.
- 2024-12-secondswap: "Automated Findings" heading and a 4naly3er report, start 2024-12-09.

## Disclosed before the run (honest limits)

While checking the parser's patterns against real READMEs this run, four READMEs were read by hand (the four above).
The SecondSwap README (audit starting 9 Dec 2024) has a heading "## Automated Findings / Publicly Known Issues" that
links a **4naly3er** report, not a bot-race report. On the wording above, that alone makes P1 CONTRADICTED. So the
P1 result is not a blind test any more. It is reported as written anyway, because the paper wrote it that way.
The job also reports a **secondary reading, defined after seeing SecondSwap and so not pre-registered**: a "bot-race"
marker = a bot-race phrase above, or "automated findings output" in a README that does not mention 4naly3er. Its
result is labelled post hoc wherever it is quoted.

P2 has not been seen beyond the two V12 READMEs above (both on the predicted side), so P2 is still a real test.

Other limits: READMEs are read as they stand now, so a section added or removed after the contest is invisible; the
`.sol` rule can't see Solidity code that the README never names by file; repositories that are private or deleted
can't be seen.
