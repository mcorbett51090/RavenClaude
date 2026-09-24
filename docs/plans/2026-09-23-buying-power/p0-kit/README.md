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
| `tec-premortem-findings.md`                                            | Live research on whether TEC (the closest prior-art competitor) is still operating, and why/why not.                                                                                                                                        | Done — desk research only (egress-blocked); see "Needs a human" in the file for the 6 follow-ups that would firm it up |
| `incumbent-check-findings.md`                                          | Live research on whether LearnPlatform or GovSpend already offer a comparable price benchmark.                                                                                                                                              | Done — desk research only (egress-blocked); see "Needs a human" in the file for the 4 follow-ups that would firm it up |
| `outreach-templates.md`                                                | Ready-to-send drafts for the four highest-leverage "needs a human" follow-ups: TEC founder outreach, LearnPlatform demo request, GovSpend trial request, Gluona/Colorado call request.                                                     | Drafted — edit before sending                                         |

## What the research found (short version — read the files for the real thing)

- **TEC (F11):** provisionally dormant since ~2019–2020, in a pattern consistent with a **funding-cliff**
  (Gates grants ended, revenue crashed to ~$150K/yr, both founders moved to other roles) — not an
  established demand-side failure. Does **not** trip the plan's STOP trigger, but doesn't clear it either;
  the highest-value unresolved step is a direct outreach to TEC's two founders.
- **Incumbents (criterion e):** neither LearnPlatform nor GovSpend provisionally meets "comparable depth"
  on public evidence, but **GovSpend is closer than the plan assumed** — its Agency Launchpad already
  shows buyers an average-price graph and "what comparable agencies paid" from raw PO data, just without
  per-seat/term normalization. A live demo on the pre-registered products is now a real precondition
  for trusting criterion (e), not a formality.
- **New finding, not in the original plan:** **Colorado runs a live, state-funded, buyer-side SaaS price
  benchmark + collective-negotiation program (Gluona / Colorado Empowered Learning)** — effectively TEC's
  model, still operating. It doesn't trip criterion (e) for a Texas launch, but it argues for **avoiding
  Colorado as a launch state** and treating Gluona as a possible partner/licensee lead, not a competitor
  to route around blind.

## Suggested order of operations

1. Read `plan.md` P0a in full if you haven't already (the "why" behind every threshold below).
2. Read `tec-premortem-findings.md` and `incumbent-check-findings.md` first — if TEC failed for an
   established demand-side reason, or an incumbent already does this, that's cheaper to learn now
   than after collecting 60 contracts.
3. Fill in and sign `preregistration-template.md` — lock the products, thresholds, and exclusion
   rules before collecting a single contract.
4. Send the two low-friction outreach messages in `outreach-templates.md` (TEC founders, Gluona)
   right away — they're the cheapest way to move several `[unverified]` findings, and replies take
   time regardless of when you send.
5. Start `contract-collection-playbook.md` and the two interview tracks in parallel — they don't
   depend on each other, and both take weeks (records requests especially).
6. Once contracts are in, normalize them per the pre-registration's rules, run
   `dispersion_test.py` for real, and check the result against `preregistration-template.md` §4.
7. Combine the dispersion result with the interview/TEC/incumbent/runway findings against the
   full (a)–(f) GO/PIVOT/STOP criteria in `plan.md` — the script only ever answers (a).

## Honest scope

Everything except `dispersion_test.py` and the TEC/incumbent research is a _draft_ meant to be
adapted — interview guides especially should be read once, tried on one or two people, and revised
before running the full set. Legal citations are carried forward exactly as `plan.md` states them,
including its own `[unverified]` flags — get every citation confirmed by counsel before relying on
it (that's what N1 is for).
