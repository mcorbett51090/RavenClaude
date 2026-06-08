# automotive-dealership

Specialist team for **automotive retail operations** — the full dealership P&L from fixed ops and
inventory to F&I and compliance. This plugin helps dealer principals, GMs, and department heads
diagnose KPI gaps, desk deals, chase absorption, manage floor-plan cost, and keep the store
compliant with GLBA Safeguards, OFAC, and advertising regulations.

> **The one-line philosophy:** fixed ops pays the bills, days-supply drives floor-plan cost, and
> F&I PVR must be earned through a fully-disclosed menu process — never through payment packing.

## When to use this plugin (vs. its neighbours)

| You're asking... | Use |
|---|---|
| "Walk me through our store P&L / DOR / 20-group benchmarks" | **automotive-dealership** (`dealership-ops-lead`) |
| "Improve our absorption rate / ELR / tech productivity / CSI" | **automotive-dealership** (`fixed-ops-analyst`) |
| "Improve F&I PVR / menu process / lender mix — compliantly" | **automotive-dealership** (`fni-advisor`) |
| "Manage days-supply / floor-plan / recon / desk this deal" | **automotive-dealership** (`inventory-and-desking-analyst`) |
| "GLBA Safeguards, NPI, advertising disclosures, Red Flags" | **automotive-dealership** (`dealership-compliance-advisor`) |
| "Manage a commercial/non-retail fleet" | `fleet-logistics` |
| "Dealership acquisition financing / corporate capital structure" | `finance` |
| "Design and optimize digital ad campaigns" | `marketing-operations-demand-gen` |

## What's inside

- **5 agents** — `dealership-ops-lead`, `fixed-ops-analyst`, `fni-advisor`,
  `inventory-and-desking-analyst`, `dealership-compliance-advisor`.
- **3 skills** — `fixed-ops-service-and-parts`, `inventory-and-desking`, `fni-and-compliance`.
- **3 commands** — `/automotive-dealership:optimize-fixed-ops`,
  `:plan-inventory-and-desking`, `:review-fni-compliance`.
- **2 templates** — `desking-worksheet.md`, `fixed-ops-kpi-dashboard.md`.
- **Knowledge bank** — `knowledge/automotive-dealership-decision-trees.md`: Mermaid trees for
  absorption improvement, hold-vs-wholesale a used unit, F&I compliance; plus a 2026 capability
  map of DMS/desking/CRM/inventory tools.
- **6 best-practices**, **1 advisory hook** (flags payment packing, plaintext NPI, undated
  rate figures, ads lacking disclosure), and **1 dealer calculator script**.

## House opinions (the short list)

1. Fixed ops pays the bills — chase absorption above all else.
2. Days-supply drives floor-plan cost; right-size to your turn rate.
3. F&I must clear compliance — no payment packing, ever.
4. Desk to the gross (front + back), not just to the close.
5. Recon time is holding cost; SLA it like a profit lever.
6. Protect customer NPI like a fiduciary.

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
