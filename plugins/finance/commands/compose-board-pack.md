---
description: Compose a board pack as a story, not a data dump — open with the headline, cash before profit, variance commentary in line with its table, 5-7 KPI cards on the front pages, explicit decisions/asks on the last body slide, detail in the appendix.
argument-hint: "[the cycle + audience, e.g. 'Q3 board pack for a founder board']"
---

# Compose a board pack

You are running `/finance:compose-board-pack`. Assemble the board / investor / lender pack the user described (`$ARGUMENTS`), following this plugin's `board-pack-composer` discipline. A pack that opens with a table is a request to skim, and a board that skims makes worse decisions.

## When to use this

A quarterly board cycle, an investor update, or a covenant-compliance reporting pack. Not for a one-number flash update between cycles (doesn't need the full arc).

## Steps

1. **Open with the narrative, not the table** (`board-open-with-the-narrative-not-the-table`): lead the executive summary with the headline + why it matters + what you're asking — not the agenda, not the team. Every slide title asserts a conclusion ("Q3 revenue beat plan on enterprise upsell"), not a label ("Q3 revenue").
2. **Cash before profit** (`board-open-with-the-narrative-not-the-table`): the cash / runway slide comes before the profit slide — cash is closer to mortal; include the "we run out here" date if applicable.
3. **Put variance commentary in line with its table** (`reconcile-before-you-narrate`, `fpa-build-the-variance-bridge-price-volume-mix`): the commentary on the financial-summary table must clear the recon gate first and carry its PVM decomposition; place it beside the number, never in a separate section that forces context-switching.
4. **Cap front-page KPIs at 5-7 as cards** (`board-open-with-the-narrative-not-the-table`): trend + single number + one-line read; push the rest to the appendix. Don't change a KPI definition between periods without a footnote.
5. **End the body with explicit decisions / asks** (`board-open-with-the-narrative-not-the-table`): the last body slide names the specific calls the board has authority over — boards remember the close, and a pack with no explicit ask leaves the board having decided nothing.
6. **Detail to the appendix; mark every page** (house opinions #7, #9, #10): evidence and back-up are the safety net, not the body; confidentiality/status mark on every page; circulate the pre-read 48-72h ahead.

## Guardrails

- Source-cite every number on the face of the pack (GL + period, model tab + cell); a figure without a source doesn't ship.
- Adapt emphasis and asks to the audience (founder vs PE vs lender) but keep the narrative-first / cash-first / ask-last spine; a lender pack leads with covenant compliance.
- Finance data is confidential by default — scrub salaries, customer-specific revenue, and M&A targets before sharing examples, even internally.
