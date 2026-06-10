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

## Decision Tree: Is this group an ACA Applicable Large Employer, and what does it owe?

The ALE test gates the employer mandate, affordability, minimum value, and 1095-C/1094-C reporting. Verify the current-year figures.

```mermaid
graph TD
  A[Employer mandate / ACA reporting question] --> B{50+ full-time-equivalent employees? verify-at-build}
  B -- No --> C[Not an ALE - no employer-shared-responsibility; reporting limited unless self-funded]
  B -- Yes --> D[Applicable Large Employer - mandate applies]
  C --> E{Self-funded plan?}
  E -- Yes --> F[Still owes minimum essential coverage reporting for covered individuals verify-at-build]
  E -- No --> G[Fully-insured small employer - carrier handles much of the reporting]
  D --> H{Offer affordable, minimum-value coverage to full-time employees + dependents?}
  H -- No --> I[Exposure to employer-shared-responsibility payment - model the penalty risk; escalate to counsel]
  H -- Yes --> J{Affordability tested on the LOWEST-cost self-only plan? indexed % verify-at-build}
  J -- No --> K[Re-test affordability vs the current-year safe harbor before locking contributions]
  J -- Yes --> L[Compliant - file 1095-C/1094-C on the current-year deadline verify-at-build]
```

_The ALE count, affordability %, and minimum-value floor are all indexed/dated — `[verify-at-build]` against the current IRS source. Educational scaffolding; ERISA counsel confirms the obligation._

## Decision Tree: HDHP+HSA or a traditional plan for this member/population?

A funded HDHP can be a genuine benefit or a cost-shift dressed as one — the employer HSA contribution and the member's utilization decide which.

```mermaid
graph TD
  A[HDHP+HSA vs traditional plan?] --> B{Employer funds the HSA with real seed money?}
  B -- No --> C[Cost-shift risk - a bare HDHP is a premium cut paid by members at the deductible]
  B -- Yes --> D{Workforce utilization mix?}
  C --> E{Hard budget cap forcing it?}
  E -- Yes --> F[At minimum add a modest HSA seed + offer a traditional choice; model member OOP first]
  E -- No --> G[Reconsider - the savings come straight out of high-utilizers' pockets]
  D -- Mostly healthy, low utilizers --> H[Funded HDHP+HSA fits - lower premium + tax-advantaged savings]
  D -- Mixed / chronic conditions / families --> I[Offer a CHOICE - funded HDHP alongside a PPO/traditional option]
  H --> J[Verify HDHP min-deductible + max-OOP + HSA caps - all indexed verify-at-build]
  I --> J
  F --> J
```

_An HDHP with no employer HSA contribution is a cost-shift, not a benefit. Model member total cost across a realistic claims distribution; give a mixed workforce a choice. `[verify-at-build]` the indexed HDHP/HSA limits._

## Decision Tree: A qualifying life event hit mid-year — is there a special-enrollment right?

QLE / special-enrollment windows are precise and date-driven; a missed window is a real member harm. Write the rules down.

```mermaid
graph TD
  A[Mid-year coverage-change request] --> B{Qualifying life event? marriage/birth/adoption, loss of other coverage, etc.}
  B -- No --> C[No special-enrollment right - changes wait for open enrollment unless plan allows otherwise]
  B -- Yes --> D{Within the special-enrollment window? typically 30-60 days, verify plan + current rules}
  D -- No --> E[Window missed - document; check any narrow exceptions; escalate hardship cases]
  D -- Yes --> F{Change consistent with the event? consistency rule for pre-tax cafeteria plans}
  F -- No --> G[Limit the change to what the event supports - the cafeteria-plan consistency rule applies]
  F -- Yes --> H[Permit the election change - capture proof of the event + the effective date]
  C --> I{Did the employee also LOSE eligibility? hours drop, termination}
  I -- Yes --> J[COBRA / continuation rights may trigger - run the notice timing verify-at-build]
  I -- No --> K[No action beyond standard enrollment]
```

_Eligibility and special-enrollment windows are rules and a calendar, not vibes — write them down and verify current-year timing. A coverage loss can trigger COBRA; run the notice clock. Educational scaffolding._

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
