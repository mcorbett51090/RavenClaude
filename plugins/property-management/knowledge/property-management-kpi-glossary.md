# Property Management Operations KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Occupancy & leasing

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Physical occupancy** | Occupied units ÷ total units | Point-in-time | Read alongside the flow, not alone (§3 #1). |
| **Economic occupancy** | Collected rent ÷ gross potential rent | Period | Captures concessions, loss, and delinquency the physical number hides. |
| **Renewal rate** | Renewals ÷ leases expiring | Rolling | The cheapest occupancy; renew before backfilling (§3 #6). |
| **Loss-to-lease** | (Market rent − in-place rent) ÷ market rent | Point-in-time | A real revenue give-back to manage (§3 #5). |

## Maintenance & turns

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Unit-turn time** | Days from move-out to rent-ready | Per turn, median | Lost rent + a retention signal (§3 #3). |
| **Work-order backlog** | Open work orders and their age | Point-in-time | A growing backlog erodes renewals (§3 #3 #6). |
| **Make-ready throughput** | Units turned per period | Period | Localizes where the turn stalls. |

## NOI & cash

| Metric | Definition | Window | Note |
|---|---|---|---|
| **EGI** | GPR − vacancy/loss + other income | Period | The revenue base for NOI (§3 #4). |
| **NOI** | EGI − operating expense | Period | The scorecard; capex sits below it (§3 #4 #7). |
| **Delinquency aging** | Outstanding balance by 0-30 / 31-60 / 60+ | Point-in-time | Weight collections by aging, not total (§3 #2). |
| **Cap rate** | NOI ÷ value | Market-derived | Translates NOI to value; source + date it (§3 #8). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
