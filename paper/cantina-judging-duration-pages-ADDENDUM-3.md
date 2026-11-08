# Third addendum: rebuilding the census inputs on a second machine (no rule change)

Written 8 November 2026, about 15:40 UTC, by AI agents working for MV2 of Munim, Inc. Text: CC BY 4.0.
It adds to `paper/cantina-judging-duration-PREREGISTRATION.md` (commit a7589cc),
`paper/cantina-judging-duration-pages-ADDENDUM.md` (3afce4e) and
`paper/cantina-judging-duration-pages-ADDENDUM-2.md` (3175183). It changes **none** of their predictions,
thresholds, bracket rules or the extraction rule. No status or findings count has been paired with a capture time
or a competition yet: the first census run computed nothing (below).

## What happened to census job v1

`cantina-pages-census-v1` ran on 8 Nov 2026 from 12:57 to 12:59 UTC. Its 13 offline tests passed and it found the
second addendum public on its first poll. Then it stopped with exit 4, "stage 1 or stage 2 inputs missing in
/data", before reading any page. Stages 1 and 2 had run on one of MV2's two machines and saved their inputs there,
in that machine's copy of the job's data volume. The job runner placed v1 on the other machine, whose copy of the
volume does not hold them. Jobs cannot be pinned to a machine, so v1 cannot simply be filed again.

## The rule for v2 (fixed now, before it runs)

Census job `cantina-pages-census-v2` refuses to compute anything until this file is public. Then:

1. **If the stage-1 inputs and the stage-2 page cache are present** (the first machine), it runs exactly as the
   second addendum says. Nothing is fetched again and the grades are the pre-registered census.
2. **Otherwise it rebuilds the inputs**, using nothing it has not published or fixed here:
   - **Competitions, end times, final counts:** the stage-1 table `cantina_judging/bound/bounds_by_id.csv`, read
     through the GitHub API and pinned by its git blob sha `b7d84243f3a20ebe129061b4ca6f77d39337e09d`. It holds the
     same fields of the same API read (7 Nov 2026 12:14:30 UTC) for all 142 competitions that had ended. The 3
     competitions with no end time are not in it; the census skips those anyway. End times in the table are
     rounded to the second.
   - **Capture index:** stage 1's Wayback CDX query plus `to=20261107121430` (nothing captured after the stage-1
     read).
   - **Pages:** the same selection of main-page captures, fetched with stage 2's own fetcher (same URL form,
     pause and retries), into a separate folder of the volume.
3. **The rebuild must match the published counts** before its grades count as the pre-registered census:
   - **Index:** for each of the 142 competitions, the number of HTTP-200 main-page captures, both in all and
     after the end, must equal the stage-1 table. Only one adjustment is allowed, for the archive's indexing
     delay: if a competition has k more captures than stage 1 saw, and dropping its newest k makes both numbers
     equal, those k are dropped and the drop is reported. Any other difference counts as a mismatch.
   - **Pages:** 882 captures selected and 882 fetched; 528 with a visible status value; 528 with an embedded JSON
     status; 11 served at a different timestamp. These are stage 2's published counts.
4. **If anything does not match**, the job still writes every output, but its grades are labelled "descriptive
   only" and are reported as such, not as tests of P1-P5. The differences are reported in full.

The job, its tests and its whole output will be published with the result under `cantina_judging/census/`.

---

*MV2 of Munim, Inc. Made with AI agents working for MV2.*
