---
description: "Qualify and respond to a freight RFQ/RFP/tender — score bid/no-bid first, then build the lane rate matrix and a value-led bid narrative with a follow-up cadence. Stops you burning the week on un-winnable bids."
argument-hint: "[the tender, e.g. 'RFP, 12 lanes Asia->EU, incumbent K+N, decision in 6 weeks']"
---

# Respond to an RFQ / tender

You are running `/freight-forwarding-sales:respond-to-rfq`. Handle the tender the user described (`$ARGUMENTS`) with this plugin's `rfq-tender-strategist` discipline and the `rfq-tender-response` skill.

## Steps
1. **Classify it** — RFQ (price-led), RFP (solution-led), or RFI (intel, respond lean). This sets how much to invest and what to compete on.
2. **Qualify before pricing.** Run the qualify-or-decline scorecard (fit, volume reality, incumbent strength, our relationships/single-thread, winnable economics, criteria clarity, resourcing). Output a clear **bid / no-bid** recommendation. If no-bid, draft a polite, relationship-preserving decline and stop.
3. **If bidding, build the lane rate matrix** — one row per lane (POL→POD / mode / equipment / volume / transit / base / surcharge stack / all-in / validity / assumptions). Hand each lane's pricing to `freight-rate-quoter` (or `/build-freight-quote`).
4. **Write the bid narrative** — exec summary, understanding of their supply chain, the solution (network/visibility/SLAs/exception handling), why-us proof (labeled real vs illustrative), commercials, implementation, references.
5. **Structure any discount as a give-get** (volume, term, mode shift, scope) — never naked.
6. **Set a follow-up cadence** (receipt → clarification/value touch → decision-timeline check → win/lose debrief).
7. Emit in the Output Contract format + the Structured Output JSON block.

## Guardrails
- Qualify first — do not price an un-winnable bid.
- The response is narrative + matrix, not a price list alone.
- Know the incumbent and the decision criteria, or recommend a no-bid / a clarifying question.
- Every concession buys something.
