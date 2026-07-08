---
description: "Turn a travel brief into a structured, documented, transparently-quoted itinerary — structure first, then itemized quote (net/commissionable + service fee + taxes), with the per-supplier cancellation schedule flagged verify-at-use."
argument-hint: "[destinations + dates + party size + budget + must-haves]"
---

You are running `/travel-agency-tour-operations:build-itinerary-quote`. Use `itinerary-and-booking-specialist` + the `itinerary-design-and-quoting` skill.

> Advisory, not legal or insurance advice. Every fare rule, penalty, and supplier policy is `[verify-at-use]`. **No traveler PII** — work in placeholders (Party of N), never names or payment data.

## Steps
1. Capture the brief: destinations, dates, party (placeholders), budget band, must-haves.
2. **Structure before pricing** — fix routing, sequencing, pace; sanity-check feasibility. If the party warrants it, traverse the **group-vs-FIT structuring** tree in `knowledge/travel-agency-decision-trees.md`.
3. Decide the **revenue model** (commission / service fee / markup on net) via the revenue-model tree — escalate the fee-posture question to `travel-agency-operations-lead` if unsure.
4. Build the **itemized quote**: net/commissionable supplier cost, service fee, taxes, insurance offered — no hidden markup.
5. Attach the **per-supplier cancellation/penalty schedule** and final-payment dates, each flagged `[verify-at-use]`.
6. Emit using `templates/itinerary-and-quote.md` + the Structured Output block, and log expected commission to `templates/supplier-commission-tracker.md`.
