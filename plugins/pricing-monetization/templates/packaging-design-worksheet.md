# Packaging design worksheet — `<product>`

> Output of `packaging-and-tiering`. Fill every cell; an empty "Fence" cell means the
> tier isn't fenced and isn't done.

## Value metric
- **Metric (what we charge per):** `<seats | usage unit | records | …>`
- **Why it passes the three tests:** value-aligned `<…>` / expands-with-success `<…>` /
  predictable `<…>`
- **Base + expansion split (if hybrid):** base on `<metric>`, expansion on `<metric>`

## Tier table

| Tier | Fence (self-selection dimension) | Included value-metric allowance | Key included features | Target customer | List price |
|---|---|---|---|---|---|
| Starter / Good | `<scale/use-case/…>` | `<…>` | `<…>` | `<…>` | `<provisional?>` |
| Pro / Better *(intended default)* | `<…>` | `<…>` | `<…>` | `<…>` | `<…>` |
| Enterprise / Best | `<security/SLA/volume>` | `<…/custom>` | `<…>` | `<…>` | `<custom?>` |

## Add-ons (long-tail features — NOT a fourth tier)
| Add-on | Who values it | Price |
|---|---|---|
| `<…>` | `<…>` | `<…>` |

## Self-selection logic
- Why each target customer lands in the tier we intend: `<…>`
- Anchor/decoy reasoning (if any): `<…>`

## Open validation items
- [ ] WTP validated for each tier price? (else mark provisional) → `willingness-to-pay-research`
- [ ] Fence named for every boundary?
- [ ] Bottom tier doesn't cannibalize the middle?
- [ ] Dollar impact modeled? → `finance`
