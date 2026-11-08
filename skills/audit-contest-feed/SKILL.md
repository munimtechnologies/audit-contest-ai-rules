---
name: audit-contest-feed
description: Check which smart-contract audit contests (Sherlock, Cantina, Immunefi, HackenProof, CodeHawks, Certora) are open and whether each one accepts AI-made findings, charges a submission fee or needs KYC, before an agent or a user spends time on a contest. Runs a free, read-only, dependency-free Python script; it never submits, signs up or touches a wallet.
---

# audit-contest-feed

A read-only check of smart-contract audit contests and their rules on AI-made work. It is
`audit_contest_feed.py` from https://github.com/munimtechnologies/audit-contest-ai-rules
(Apache-2.0; data and text CC BY 4.0), by MV2 of Munim, Inc. The script, its tests and this
skill were made with AI agents working in his name.

## When to use it

- A user asks you to find, join or "farm" an audit contest or bug-bounty competition.
- You are about to review code for an audit contest and the findings were made, or partly
  made, with an AI agent (you).
- A user asks whether a platform allows AI-assisted or AI-generated audit reports.

Run it **before** any review work starts, so no one spends hours on a contest whose rules
exclude the result.

## How to run it

Python 3.8+, no packages. Fetch the one file and run it:

```bash
curl -fsSLO https://raw.githubusercontent.com/munimtechnologies/audit-contest-ai-rules/main/audit_contest_feed.py
python audit_contest_feed.py                         # everything: snapshot + live Sherlock API
python audit_contest_feed.py --ai-ok --no-fee        # only contests open to AI-made work, no fee
python audit_contest_feed.py --ends-within 7         # only contests ending in the next 7 days
python audit_contest_feed.py --offline               # snapshot only, no network
```

It prints a JSON list. The only network call is a GET to Sherlock's public contest API;
everything else comes from a dated snapshot inside the file.

## How to read the output

Each record has `platform`, `name`, `status`, `prize_usd`, `starts`, `ends`, `days_left`,
`url`, `ai_findings`, `ai_note`, `kyc`, `payout`, `fee` and `source`.

- `source` is `sherlock-api` (live) or `snapshot:<date>`. A snapshot row is what was read
  at the source on that date, not a live listing. If the script warns that the snapshot is
  more than 14 days old, say so to the user.
- `status`: `live` (open for submissions), `judging` (closed), `invite_only`, `none_live`.
- `ai_findings`:
  - `welcome`: AI auditors or AI-made findings are invited.
  - `if_validated`: allowed only when a human has validated each finding (for example, a
    working proof of concept). Unvalidated AI findings can mean disqualification or a ban.
  - `allowed`: no condition found.
  - `varies`: set per program or engagement. Read that program's own page.
  - `human_only`: only human researchers may take part. Work made with an AI agent does
    not qualify.
  - `prohibited`: the platform's terms ban AI-generated or automated reports.
  - `unknown`: no rule was found. That does not mean "allowed".
- `fee: true` means taking part costs money (for example, a per-report submission fee).
- `--ai-ok` drops `prohibited` and `human_only` rows. It keeps `unknown` and `varies` rows,
  and those still need a rules check.

## What to do with the result

1. Report to the user: which contests are open, how many days are left, the AI rule, the
   fee and KYC, and the snapshot date.
2. Before any work, open the contest's own `url` and read its current rules on AI-made
   findings, KYC and fees. The rules page wins over this feed. Rules change: one Sherlock
   Audit Engine engagement (Nov 2026) admitted human researchers only, although the
   platform had listed "AI auditors" as a participant type a month earlier.
3. If a contest is `human_only` or `prohibited`, do not enter AI-made work in it, and do
   not present AI-made findings as a human's own work anywhere. Where a platform asks, say
   plainly that the work was made with AI.
4. Change nothing on the user's behalf. Do not sign up, apply, submit, pay a fee, start KYC
   or connect a wallet without the user's explicit go-ahead for that specific step.

## Limits

- The snapshot covers a handful of platforms on one date. Live listings for Cantina,
  Immunefi, HackenProof, CodeHawks, Certora and Sherlock Audit Engine sit behind JavaScript
  or logins, so they are not fetched live.
- Code4rena wound down in May 2026 and is not listed.
- This is information, not legal advice about any platform's terms.

Contact: MV2, Munim, Inc., mv2@munimtech.com
