# Life / Health / Employee-Benefits — Decision Trees

_Decision trees + a dated reference map. Every quantitative row is `[verify-at-build]` — ACA thresholds, MLR percentages, COBRA/ERISA timing, and form numbers shift year to year; re-check against the current IRS / DOL / CMS source before quoting. **Educational scaffolding, not legal, tax, or actuarial advice** — a licensed broker, credentialed actuary, or ERISA counsel signs off. Last reviewed: 2026-06-08._

Traverse before choosing a funding model or reading a renewal.

## Decision Tree: Fully-insured, level-funded, or self-funded?

Funding is a risk posture sized to the group — not a reaction to one bad renewal.

```mermaid
graph TD
  A[Choosing a funding model] --> B{Group size + ability to absorb a bad claims year?}
  B -- Small, low cash-flow tolerance --> C[Fully-insured - fixed premium, carrier holds the risk, simplest compliance]
  B -- Mid-size, some tolerance --> D{Want self-funded upside without full variance?}
  D -- Yes --> E[Level-funded - fixed monthly with stop-loss + potential surplus return; a stepping stone]
  D -- No --> C
  B -- Large, can absorb variance --> F{Stop-loss in place + multi-year risk appetite?}
  F -- No --> G[Not yet - secure specific & aggregate stop-loss and a cash-flow cushion first]
  F -- Yes --> H[Self-funded / ASO - keep the risk and the upside; model specific + aggregate attachment]
  C --> I[Re-evaluate at renewal - a +X% renewal alone is NOT a reason to self-fund]
  E --> I
  H --> I
```

_Self-funding is a multi-year risk decision, not a one-year escape hatch. A group too small to absorb claims variance, or with no stop-loss / cash cushion, should not self-fund to dodge a renewal._

## Decision Tree: How is this group rated, and is the renewal defensible?

Credibility decides whether the group's own experience drives its rate; a renewal is a sum of parts.

```mermaid
graph TD
  A[Rating / renewal question] --> B{Is the group credible - enough lives + claim volume?}
  B -- Low credibility, small group --> C[Manual / pooled rate - one large claim is mostly noise; don't over-react]
  B -- Partial --> D[Blended / credibility-weighted - carrier assigns a weight to own experience]
  B -- High credibility, large group --> E[Experience-rated - own claims drive the rate]
  C --> F{Decompose the renewal}
  D --> F
  E --> F
  F --> G[Trend + own experience + pooling + demographic drift + plan change]
  G --> H{Carrier can explain the decomposition?}
  H -- No --> I[Re-market - opacity is itself a reason to test the market]
  H -- Yes --> J{Loss ratio supports the increase? Check vs ACA MLR floor separately}
  J -- Below MLR floor --> K[Possible over-rating / MLR rebate signal - information for next negotiation]
  J -- Supports it --> L[Defensible - pull levers: plan change, funding move, contribution shift]
```

_Underwriting loss ratio (claims ÷ premium) is NOT the ACA medical-loss-ratio regulatory test — don't conflate them. Decompose every renewal; "+X%" is not a finding._

---

## Reference map (2026, `[verify-at-build]`)

| Topic | Reference point | Notes |
|---|---|---|
| ALE threshold (ACA employer mandate) | 50+ full-time-equivalent employees → applicable large employer | Triggers employer-shared-responsibility + 1095-C/1094-C reporting `[verify-at-build]` |
| ACA affordability | Employee self-only premium ≤ a set % of household income (indexed annually) | The % is re-indexed each year — verify the current-year figure `[verify-at-build]` |
| ACA minimum value | Plan pays ≥ 60% of total allowed costs | Bronze-equivalent floor for the employer mandate `[verify-at-build]` |
| Medical-loss-ratio (MLR) thresholds | 80% individual / small-group, 85% large-group | Below the floor → rebate to policyholders; distinct from the underwriting loss ratio `[verify-at-build]` |
| COBRA continuation | Generally 18 months (up to 29 with disability, 36 for certain events); 20+ employee employers | Notice/election timing is precise — verify current rules `[verify-at-build]` |
| ERISA Form 5500 | Annual filing for ERISA plans (plus Summary Annual Report); small-plan exemptions apply | Deadline and schedules shift — verify current-year `[verify-at-build]` |
| SPD / SBC distribution | Summary Plan Description (ERISA) + Summary of Benefits and Coverage (ACA) required disclosures | Distribution timing rules apply `[verify-at-build]` |
| HSA / HDHP | HDHP must meet minimum deductible + max OOP limits (indexed); HSA contribution caps indexed annually | Pair an HDHP with employer HSA funding or it's a cost-shift `[verify-at-build]` |
| Plan types | HMO, PPO, EPO, POS, HDHP+HSA | Trade network breadth vs cost-share vs premium `[verify-at-build]` |
| Funding models | Fully-insured, level-funded, self-funded (ASO + specific/aggregate stop-loss) | Sized to group size + risk tolerance + cash flow `[verify-at-build]` |
| Lines of coverage | Medical, dental, vision, group term life + AD&D, short-term & long-term disability | Choose as a system; disability income is the most under-bought `[verify-at-build]` |

_All figures, thresholds, and deadlines above are indexed/revised periodically by the IRS, DOL, and CMS. Re-verify every quantitative value against the authoritative current-year source before relying on it. This is educational scaffolding, not legal, tax, or actuarial advice._
