# M&A valuation & deal economics

The reference the agents use to value a target, size synergies, and choose a structure.
All multiples and market data below are **illustrative of method, not current values** —
never quote a multiple from memory; pull it from a dated source before it enters a
deliverable (§3 #8).

---

## The valuation identity

```
Maximum defensible price
  = Standalone value
  + (defensible share of) buyer-created synergies (present value)
  − one-time cost to achieve synergies
  − expected dis-synergies (attrition / disruption, PV)
  − control premium already embedded in precedent multiples
```

The seller's floor is their standalone value plus what another bidder would pay. You
capture value only in the gap between your synergy-inclusive ceiling and that floor —
so **don't hand the seller synergies your team will earn** (§3 #2).

## Triangulation — the three methods

| Method | What it captures | Trap |
|---|---|---|
| **DCF** | Intrinsic standalone value from projected cash flows | Garbage-in on WACC and terminal value; sensitivity-test the two biggest drivers |
| **Trading comparables** | What the public market pays for similar businesses *without* control | Peer set must be defensible; multiples move — cite source + date |
| **Precedent transactions** | What acquirers actually paid, *including* a control premium | Deals are cycle- and buyer-specific; don't double-count the control premium against DCF |

Cross all three. Convergence = confidence; divergence = the finding to explain (§3 #4).

## Synergy math

- **Cost synergies** — headcount, facilities, procurement, systems. Higher confidence, faster, easier to own. Weight them first.
- **Revenue synergies** — cross-sell, pricing, new markets. Lower confidence, later, often overstated. Discount them and phase them.
- Every synergy = **owner × date × cost-to-achieve** (§3 #3). Synergy PV nets the run-rate benefit against the one-time cost and the ramp.
- **Dis-synergies** are real: customer overlap churn, employee attrition, distraction. Underwrite them or pay for them post-close (§3 #6).

## Deal structure — matching risk to instrument

| Instrument | Use when | Watch |
|---|---|---|
| **Cash** | Confidence high, financing available | Accretion/dilution and leverage impact (→ `treasury-management`) |
| **Stock** | Sharing risk/upside, preserving cash | Relative-value risk; dilution; exchange ratio |
| **Earnout** | Valuation gap on future performance | Post-close friction; define metrics/period tightly (→ counsel) |
| **Escrow / indemnity** | Diligence red flags to price around | Caps, baskets, survival periods (→ counsel) |

## Accretion / dilution (quick read)

A deal is EPS-accretive when the earnings yield acquired exceeds the after-tax cost of the
consideration used to buy them. Accretion is a *screen*, not a thesis — a value-destructive
deal can be accretive and a value-creating one dilutive (§3 #1). The full definition and the
other metrics are in [`ma-kpi-glossary.md`](ma-kpi-glossary.md).
