# property-management-residential

The **residential property management** operations layer. This plugin's team helps you run a
residential portfolio: keeping units leased, maintaining properties to code and SLA, collecting rent
and managing delinquency, and staying on the right side of fair-housing and habitability law.

> **The one-line philosophy:** a well-run residential portfolio is a system — consistent screening,
> disciplined turns, timely maintenance, and proactive delinquency management. Every failure to
> document, every listing with careless language, and every work order without an SLA is a liability.

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
| --- | --- |
| "Run / analyze my residential rental portfolio — NOI, occupancy, owner reports" | **property-management-residential** (`pm-ops-lead`) |
| "Build a leasing strategy, review screening criteria, reduce turnover" | **property-management-residential** (`leasing-strategist`) |
| "Design a work-order SLA, plan a make-ready, optimize maintenance ops" | **property-management-residential** (`maintenance-operations-analyst`) |
| "Review listing for fair-housing compliance, check screening consistency" | **property-management-residential** (`pm-compliance-advisor`) |
| "Underwrite / acquire a commercial or multifamily investment" | `commercial-real-estate` |
| "Scope a major repair, negotiate a trade contract, evaluate a contractor" | `skilled-trades-contracting` |
| "Route field crews across multiple service locations" | `field-service-management` |

## What's inside

- **4 agents** — `pm-ops-lead`, `leasing-strategist`, `maintenance-operations-analyst`,
  `pm-compliance-advisor`.
- **3 skills** — `leasing-and-tenant-lifecycle`, `maintenance-and-work-orders`,
  `rent-collection-and-delinquency`.
- **3 commands** — `/property-management-residential:optimize-leasing-funnel`,
  `:design-maintenance-sla`, `:plan-rent-collection`.
- **2 templates** — `make-ready-turn-checklist.md`, `work-order-sla-matrix.md`.
- **Knowledge bank** — `knowledge/pm-residential-decision-trees.md`: Mermaid trees for renew-vs-turn,
  repair-vs-replace in make-ready, and the delinquency action ladder, plus a dated 2026 PM software
  capability map.
- **6 best-practices** and **1 advisory hook** (flags fair-housing risky language, plaintext tenant
  PII, inconsistent screening, and work orders without an SLA).
- **`scripts/pm_calc.py`** — stdlib calculator: occupancy/vacancy %, NOI, economic vs physical
  occupancy gap, delinquency rate, turn cost, rent-to-income ratio.

## House opinions (the short list)

1. Fair housing is not optional — every listing and every screening decision must be consistent and
   policy-grounded.
2. Document everything in the tenant file — if it isn't written, it didn't happen.
3. The turn is where NOI is won or lost — days-to-ready drives portfolio performance.
4. Screen consistently — set criteria once, apply identically to every applicant.
5. Every work order carries an SLA — emergency / urgent / routine with hour/day commitments.
6. Protect tenant PII — SSN and background reports stay in the PM software, not in email.

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
