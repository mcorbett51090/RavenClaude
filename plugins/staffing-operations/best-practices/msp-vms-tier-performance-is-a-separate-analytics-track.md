# MSP/VMS Tier Performance Is a Separate Analytics Track

**Status:** Pattern
**Domain:** Staffing operations
**Applies to:** `staffing-operations`

---

## Why this exists

An MSP-managed program has fundamentally different performance dynamics than a direct-client relationship. Fill-rate targets, submittal speed requirements, rate caps, and reporting obligations are all defined by the MSP contract rather than negotiated bilaterally. A firm's overall fill rate may look healthy while its MSP-tier fill rate is below the SLA threshold that triggers a tier demotion — a commercial risk that is invisible in blended reporting. MSP and direct-client performance must be tracked as separate analytics tracks to manage the real commercial exposure.

## How to apply

Segregate MSP/VMS orders from direct-client orders in every operational dashboard:

```
MSP vs. Direct-Client Performance Split
─────────────────────────────────────────
Period:  ________________
Division / segment:  ________________

Channel        | Orders | Fill rate | TTF (days) | Margin % | SLA threshold | SLA status
───────────────|--------|-----------|------------|----------|---------------|────────────
MSP Tier 1     |        |           |            |          | ≥ 85%         | [ ] Met  [ ] Below
MSP Tier 2     |        |           |            |          | ≥ 75%         |
Direct clients |        |           |            |          | Contractual   |
Internal/house |        |           |            |          | N/A           |

MSP tier concentration risk:
  % of total orders from MSP channels:  ___%  [flag if >50% — concentration risk]
  MSP contracts with tier-demotion clauses:  ___  (names / IDs)
  Next tier review date:  ________________

MSP margin analysis:
  MSP blended margin:  ___%  vs. direct-client margin:  ___%
  Rate-cap impact (estimated):  $______ revenue foregone vs. open-market rate
```

**Do:**
- Track MSP-tier fill rate and TTF against the contractually defined SLA — not against the firm's internal target.
- Identify any MSP contracts with tier-demotion or volume-reduction clauses and flag them in the exec readout if performance is within 5 points of the threshold.
- Compare MSP-channel margin to direct-client margin quarterly — MSP rate caps structurally compress margin; the comparison makes the trade-off visible.

**Don't:**
- Blend MSP-channel orders into the overall fill rate without disclosure — it obscures tier performance and can mask an SLA breach.
- Use the direct-client margin as the benchmark for MSP-channel deals without acknowledging the rate-cap difference — they are structurally different channels.
- Treat MSP concentration above 50% as neutral; diversification away from MSP dependency is a standard risk-management recommendation in staffing operations [unverified — training knowledge].

## Edge cases / when the rule does NOT apply

Firms that operate exclusively through direct-client relationships have no MSP/VMS tier track. For them, the relevant split is contract-client vs. on-demand/per-diem.

## See also

- [`../agents/staffing-operations-analyst.md`](../agents/staffing-operations-analyst.md) — owns the MSP/VMS analytics track and SLA compliance monitoring.
- [`../agents/workforce-market-analyst.md`](../agents/workforce-market-analyst.md) — frames the MSP/VMS consolidation trend in the market context.

## Provenance

Codifies CLAUDE.md §3 #1 (every KPI ships with a definition, a window, and a baseline) and §3 #2 (fill rate and TTF are a pair) applied to the MSP-channel context where SLAs define the relevant baselines. MSP/VMS tier management is a standard operating requirement for staffing firms with significant institutional health system clients [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
