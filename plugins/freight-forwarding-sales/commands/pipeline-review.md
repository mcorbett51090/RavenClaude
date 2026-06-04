---
description: "Review a freight-sales pipeline and produce a defensible forecast — hygiene findings, coverage and velocity math, at-risk deals with the decay signal, and commit/best-case/weighted numbers. Stage = buyer behavior, not optimism."
argument-hint: "[your open deals with stage/value/next-step, or a quota + summary]"
---

# Pipeline review

You are running `/freight-forwarding-sales:pipeline-review`. Review the pipeline the user shared (`$ARGUMENTS`) with this plugin's `pipeline-forecast-coach` discipline and the `pipeline-forecasting` skill.

## Steps
1. **Hygiene sweep** — flag deals with no next step + date, stuck/no-stage-change, serial-pushed close dates, zombie (no activity), missing data, and **single-threaded** (one contact) deals.
2. **Re-stage by behavior** — for each deal, name what the buyer demonstrably did; demote any stage that fails its exit criterion.
3. **Coverage + velocity** — compute coverage (weighted pipeline ÷ remaining quota) and sales velocity ((# opps × avg value × win rate) ÷ cycle length); state the gap to quota and whether coverage is sufficient for the cycle length.
4. **Three forecast numbers** — commit, best-case, weighted — labeled, with the stage probabilities used.
5. **At-risk list** — each at-risk deal with its specific decay signal and one concrete re-engage action.
6. **Recommend the next move** — if coverage is short, route to `prospecting-outreach-strategist`; if growth is in current accounts, route to `key-account-manager`.
7. Emit in the Output Contract format + the Structured Output JSON block.

## Guardrails
- A deal with no next step + date is not "open" — flag it.
- Never report one blended forecast number; always commit / best-case / weighted.
- Single-threaded deals are a P1 risk in multi-stakeholder logistics cycles.
- Surface coverage gaps early — a 6–18 month cycle can't be fixed at quarter-end.
