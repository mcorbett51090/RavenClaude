---
description: "Run a full F&I performance and compliance review: PVR decomposition (finance reserve + product gross), product penetration rate analysis by product type, menu-selling process assessment (100% presentation rate, full disclosure), lender-mix optimization, and a compliance gate checklist (no payment packing, RISC accuracy, adverse action, OFAC, Red Flags). Always clears compliance before recommending any PVR improvement action."
---

# F&I and Compliance

**Purpose:** systematically improve F&I per-vehicle retailed (PVR) through a compliant
menu process and optimized product mix — and simultaneously verify that no improvement
action introduces a payment-packing or disclosure violation.

## Entry point

Use this skill when the question is: "Improve F&I PVR", "Review our menu process",
"Optimize lender mix", "Audit F&I compliance", or "How do we train F&I managers?"

Primary agents: `fni-advisor` (performance), `dealership-compliance-advisor` (compliance gate).
Supporting agents: `dealership-ops-lead` (F&I contribution to store P&L),
`inventory-and-desking-analyst` (deal-structure handoff).

## Steps

### 1. PVR decomposition

Collect for the period:
- Total F&I gross
- Total units retailed
- Finance reserve gross (total rate-markup income, net of chargebacks)
- Product gross by product type (VSC, GAP, maintenance, tire/wheel, appearance, other)
- Chargebacks (reserve + product)

Calculate:
```
PVR = Total F&I gross ÷ Units retailed
Reserve PVR = Finance reserve gross ÷ Units retailed
Product PVR = Total product gross ÷ Units retailed
```

Benchmark PVR against 20-group averages (mark [verify-at-use]). Flag reserve vs product
split — a high reserve / low product PVR indicates dependency on rate markup and vulnerability
to rate compression.

### 2. Product penetration analysis

For each F&I product, calculate:
```
Penetration rate = Units with product sold ÷ Total units retailed (as %)
Average product front = Product gross ÷ Units with product sold
```

Common benchmarks [verify-at-use]:
| Product | Target penetration range |
|---|---|
| VSC (vehicle service contract) | 35–55% |
| GAP | 30–50% |
| Maintenance agreement | 20–40% |
| Tire/wheel protection | 15–30% |
| Appearance protection | 10–25% |

Identify the product with the largest penetration gap × average front as the highest-PVR lever.

### 3. Compliance gate (REQUIRED before any process recommendation)

Traverse the **F&I product-presentation compliance** decision tree in
[`../../knowledge/automotive-dealership-decision-trees.md`](../../knowledge/automotive-dealership-decision-trees.md).

Verify each item before proceeding:

| Check | Pass criteria |
|---|---|
| Payment packing | No product included in payment without explicit customer acknowledgment on menu |
| 100% menu presentation | All products shown simultaneously with individual prices on every deal |
| RISC accuracy | Contract terms match deal structure; no post-signing product insertion |
| Adverse action notice | Documented process for AA notices on declined applications |
| OFAC screening | SDN check completed and documented before funding |
| Red Flags | Identity-verification step completed per ITPP |
| Credit application accuracy | Customer-provided data transcribed accurately; no alteration |

**If any payment-packing check fails, STOP.** Do not proceed to PVR improvement. Route to
`dealership-compliance-advisor` for remediation before any process coaching.

### 4. Menu process assessment

Evaluate the current menu-selling process against best practice:

1. **100% presentation rate:** does every customer see a menu? (Target: 100%)
2. **Full simultaneous disclosure:** are all products shown at once, with individual prices?
3. **Payment-inclusive AND payment-exclusive presentation:** does the menu show both?
4. **No payment manipulation:** is the customer shown the payment with and without each product?
5. **Objection-handling:** does the process handle "I don't want any of that" with
   product-value explanation, not payment re-quoting?
6. **Documentation:** is the signed/declined menu retained in the deal jacket?

Rate each on a 3-point scale (fully implemented / partially / not implemented).

### 5. Lender mix and approval optimization

Collect:
- Total submitted deals by lender and tier
- Approval rates by tier (prime / near-prime / subprime)
- Average reserve by lender and tier
- Contracts-in-transit (CIT) aging by lender

Identify:
- **Lender concentration risk:** >50% of volume in one lender is a risk if that relationship tightens.
- **Reserve opportunity:** tiers or lenders where buy-rate spread is available but not being captured.
- **Approval-rate gaps:** high submission rate + low approval rate = stip/criteria mismatches.
- **CIT aging:** deals >15 days in transit create cash-flow and chargeback risk.

Recommend: minimum three-lender coverage across prime/near-prime/subprime [verify-at-use].

### 6. PVR improvement plan

Rank improvement actions by dollar opportunity:
- **Quick wins (≤30 days):** presentation rate fix (train to 100%), highest-penetration-gap
  product focus, lender stip resolution.
- **Structural (30–90 days):** full menu redesign, lender tier expansion, F&I manager
  development.
- For each action: estimated monthly PVR impact × units = monthly gross improvement.

Use `scripts/dealer_calc.py` mode `pvr` for the arithmetic.

## Anti-patterns

- Recommending any PVR improvement before clearing the compliance gate (step 3).
- Confusing "PVR" with "reserve" — the full metric includes product gross.
- Reporting penetration rates on a "per-customer-who-sat-with-F&I" basis rather than
  per-unit-retailed (the standard denominator).
- Recommending lender concentration as a "relationship building" strategy without flagging the risk.
- Menu processes that present products as a bundle without individual prices.

## Output

A compliance-gated F&I performance report: PVR decomposition with reserve/product split,
product penetration by product with gap vs benchmark, compliance gate checklist (pass/fail),
menu process assessment score, lender mix analysis, and a ranked PVR improvement plan with
monthly dollar estimates. Output is blocked if any compliance gate fails.
