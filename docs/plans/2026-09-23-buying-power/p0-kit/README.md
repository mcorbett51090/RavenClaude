# P0a kit — Buying Power

Working materials to actually execute Phase P0a of `../plan.md` (the go/pivot/stop validation gate
before any code gets written). Nothing here substitutes for reading P0a itself (`plan.md` lines
1245–1411) — these are the tools to run it.

## Files

| File                                                                   | What it's for                                                                                                                                                                                                                               | Status                                                                |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `preregistration-template.md`                                          | The `p0_preregistration` decision record — fill in, sign, freeze **before** collecting any contract data.                                                                                                                                   | Template — needs your input (products, state, dates)                  |
| `dispersion_test.py`                                                   | The actual noise-corrected statistical test (plan.md's acceptance criterion (a)). Run it once contract + noise-pair data exists. `python3 dispersion_test.py --self-test` verifies it works; `--contracts`/`--noise-pairs` run it for real. | Built + self-tested + verified against a real (synthetic) example run |
| `example-contracts.SYNTHETIC.csv`, `example-noise-pairs.SYNTHETIC.csv` | Made-up data showing the exact CSV shape the script expects. **Not real data** — replace with your own collected contracts before it means anything.                                                                                        | Reference only                                                        |
| `contract-collection-playbook.md`                                      | How to actually gather 45–60 real contracts across 2–3 products (check registers vs. board packets vs. records requests vs. NDA-shared, with a records-request letter template and a tracking-spreadsheet layout).                          | Drafted                                                               |
| `buyer-interview-guide.md`                                             | Script for the ~20–25 buyer interviews (demand, willingness-to-pay, private data-sharing, board-packet memo interest).                                                                                                                      | Drafted                                                               |
| `coop-interview-guide.md`                                              | Script for 2–4 purchasing-cooperative interviews (spend share, their own benchmark plans, licensing interest, gentle future-partnership scouting).                                                                                          | Drafted                                                               |
| `counsel-scoping-brief.md`                                             | One-pager to get a lawyer's quote for the N1 narrow check and L1 antitrust scoping (kept separate, per the plan).                                                                                                                           | Drafted                                                               |
| `tec-premortem-findings.md`                                            | Live research on whether TEC (the closest prior-art competitor) is still operating, and why/why not.                                                                                                                                        | _(filled in once the research agent reports back)_                    |
| `incumbent-check-findings.md`                                          | Live research on whether LearnPlatform or GovSpend already offer a comparable price benchmark.                                                                                                                                              | _(filled in once the research agent reports back)_                    |

## Suggested order of operations

1. Read `plan.md` P0a in full if you haven't already (the "why" behind every threshold below).
2. Read `tec-premortem-findings.md` and `incumbent-check-findings.md` first — if TEC failed for an
   established demand-side reason, or an incumbent already does this, that's cheaper to learn now
   than after collecting 60 contracts.
3. Fill in and sign `preregistration-template.md` — lock the products, thresholds, and exclusion
   rules before collecting a single contract.
4. Start `contract-collection-playbook.md` and the two interview tracks in parallel — they don't
   depend on each other, and both take weeks (records requests especially).
5. Once contracts are in, normalize them per the pre-registration's rules, run
   `dispersion_test.py` for real, and check the result against `preregistration-template.md` §4.
6. Combine the dispersion result with the interview/TEC/incumbent/runway findings against the
   full (a)–(f) GO/PIVOT/STOP criteria in `plan.md` — the script only ever answers (a).

## Honest scope

Everything except `dispersion_test.py` and the TEC/incumbent research is a _draft_ meant to be
adapted — interview guides especially should be read once, tried on one or two people, and revised
before running the full set. Legal citations are carried forward exactly as `plan.md` states them,
including its own `[unverified]` flags — get every citation confirmed by counsel before relying on
it (that's what N1 is for).
