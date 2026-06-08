# Wealth Management (RIA) — Decision Trees

_Decision trees + a dated reference map. Reference rows are `[verify-at-build]` — re-check the current-year figure/rule against the IRS / SEC / a primary source before quoting. Last reviewed: 2026-06-08._

> **Not investment advice.** These are educational decision frameworks for an advisory practice, not personalized recommendations. The licensed adviser applies them to a specific client after confirming the client-specific facts; a CPA / attorney owns the tax and legal conclusions.

Traverse before deciding an account-funding order, a withdrawal strategy, a rebalancing approach, an asset-location / tax-loss-harvesting move, whether something is education vs personalized advice, or which standard applies.

## Decision Tree: What's the tax-aware account-funding order?

Capture free money first, then sort by tax treatment — but the client-specific bracket and eligibility change the answer.

```mermaid
graph TD
  A[A dollar to save] --> B{Is there an employer match available and unfunded?}
  B -- Yes --> C[Fund to the full match first - it's the one unambiguous, near-universal move]
  B -- No / already captured --> D{High-interest debt outstanding?}
  D -- Yes --> E[Pay it down - a guaranteed return that beats most allocations]
  D -- No --> F{Emergency fund in place?}
  F -- No --> G[Build the cash buffer first - it's a prerequisite, not an investment]
  F -- Yes --> H{HSA-eligible (HDHP) and not yet maxed?}
  H -- Yes --> I[Consider the HSA - triple tax advantage for eligible clients]
  H -- No --> J{Tax-advantaged space (Roth/Traditional IRA, 401k) remaining?}
  J -- Yes --> K[Fund it - Roth vs Traditional depends on now-vs-later bracket; confirm with a CPA]
  J -- No --> L[Taxable brokerage - mind asset location and tax efficiency]
```

_Capture the match → clear high-interest debt → emergency fund → HSA (if eligible) → tax-advantaged → taxable. The order is a framework; eligibility, bracket, and goals are client-specific facts to confirm._

## Decision Tree: Which retirement withdrawal strategy?

The number is less important than surviving a bad sequence of early returns.

```mermaid
graph TD
  A[Client entering / planning drawdown] --> B{Is the plan tight - little margin between assets and spending need?}
  B -- Yes --> C{Can the client tolerate variable spending year-to-year?}
  C -- Yes --> D[Dynamic guardrails - cut/raise withdrawals as the portfolio moves; protects against sequence risk]
  C -- No --> E[Floor-and-ceiling or a cash/bond buffer - cover essential spending from a stable floor]
  B -- No, comfortable margin --> F{Wants simplicity over optimization?}
  F -- Yes --> G[Fixed 4%-rule-style start, reviewed annually - a planning heuristic, not a guarantee]
  F -- No --> H[Dynamic guardrails - usually supports a higher safe starting rate than a fixed rule]
  D --> I[In all cases: name sequence-of-returns and longevity risk; pair with a review trigger]
  E --> I
  G --> I
  H --> I
```

_The 4% rule is a starting heuristic, not a guarantee. Sequence-of-returns risk (bad early years) is the retirement-planning fault line; guardrails and a cash buffer exist to survive it._

## Decision Tree: Calendar or threshold/bands rebalancing?

The value of rebalancing is removing the discretionary call — so the rule must be written into the IPS either way. Account taxability picks the flavor.

```mermaid
graph TD
  A[Need a rebalancing rule for the IPS] --> B{Are the accounts mostly taxable?}
  B -- Yes --> C[Prefer threshold/bands - trade only when drift is real; minimizes taxable trades]
  B -- No / mostly tax-advantaged --> D{Does the client/practice value operational simplicity over minimizing trades?}
  D -- Yes --> E[Calendar - rebalance on a fixed schedule, e.g. annual; simplest to operate]
  D -- No --> F[Threshold/bands - rebalance when a class drifts past a set range]
  C --> G[Add an annual max-time backstop so nothing drifts forever]
  E --> H[Add a no-trade band so tiny drifts don't trigger needless trades]
  F --> G
  G --> I[In taxable accounts: rebalance tax-aware - use new contributions and harvested losses first]
  H --> I
  I --> J[Write the chosen rule into the IPS and record it in books-and-records]
```

_Calendar = rebalance on a schedule; threshold/bands = rebalance on drift. Either way the rule is written, not a feeling. In taxable accounts prefer bands + tax-aware execution to keep trade count and tax drag down. The bracket and account mix are client-specific facts to confirm._

## Decision Tree: Asset location & tax-loss harvesting (after-tax return)

Getting the right asset in the right account type is often worth more than a marginally cheaper fund — but the wash-sale rule and the client's bracket gate it.

```mermaid
graph TD
  A[Placing or harvesting in a multi-account household] --> B{Placing an asset across account types?}
  B -- Yes --> C{Is the asset tax-inefficient - high ordinary income, e.g. taxable bonds, REITs?}
  C -- Yes --> D[Locate in tax-deferred - traditional IRA/401k - to shelter the income]
  C -- No --> E{Highest expected growth?}
  E -- Yes --> F[Prefer Roth - tax-free growth is most valuable on the biggest compounders]
  E -- No --> G[Tax-efficient equity index funds sit fine in taxable]
  B -- No, harvesting a loss --> H{Is there an unrealized loss worth harvesting vs the trade cost?}
  H -- No --> I[Skip - don't trade just to harvest a trivial loss]
  H -- Yes --> J{Will a substantially identical security be repurchased within the wash-sale window?}
  J -- Yes --> K[Don't - the loss is disallowed; use a non-substantially-identical replacement to stay invested]
  J -- No --> L[Harvest; track basis and the wash-sale window across ALL accounts incl. spouse/IRA]
  D --> M[Route the actual tax conclusion and bracket math to a CPA]
  F --> M
  L --> M
  K --> M
```

_Asset location: tax-inefficient assets into tax-deferred, biggest growth into Roth, tax-efficient equity into taxable. Harvesting: mind the wash-sale rule across every account (including the spouse's and IRAs), and the bracket. The tax conclusion routes to a CPA — this is an educational framework, not tax advice._

## Decision Tree: Education vs personalized advice — and which standard applies?

Two gates before responding: is this a personalized recommendation (out of scope — reframe), and if a standard is invoked, which one?

```mermaid
graph TD
  A[An advisory-shaped request] --> B{Does it ask the plugin to make a specific buy/sell/allocation call for a named client?}
  B -- Yes --> C[Out of scope - reframe to the educational/operational equivalent; surface the facts the licensed adviser must confirm]
  B -- No --> D[Educational/operational support is in scope - state the not-investment-advice disclaimer]
  C --> E{Does the request invoke a 'best interest' / fiduciary standard?}
  D --> E
  E -- No --> F[Proceed - framework + assumptions surfaced + disclaimer]
  E -- Yes --> G{What is the firm's registration?}
  G -- Registered Investment Adviser --> H[Fiduciary duty under the Advisers Act - duty of care + loyalty; disclose and manage conflicts]
  G -- Broker-dealer --> I[Regulation Best Interest - a DIFFERENT best-interest standard; never conflate with the RIA fiduciary duty]
  G -- Unclear / dual-registered --> J[Don't guess - route the firm-specific determination to compliance counsel]
  H --> K[Name the standard explicitly in the output; document the basis and route firm specifics to counsel]
  I --> K
  J --> K
```

_First gate: a personalized buy/sell call is out of scope — reframe and flag the facts to confirm. Second gate: the RIA fiduciary duty (Advisers Act) and Reg BI (broker-dealer) are different standards; which applies depends on registration. Name it explicitly, never conflate them, and route the firm-specific call to counsel._

---

## Reference map (2026, `[verify-at-build]`)

| Item | 2026 reference point | Notes |
|---|---|---|
| Withdrawal heuristic | The "4% rule" (Bengen / Trinity-study lineage) | A planning heuristic from historical US data, not a guarantee — pair with guardrails `[verify-at-build]` |
| Dynamic withdrawals | Guyton-Klinger guardrails, floor-and-ceiling, bucket/cash-buffer | Adjust spending to portfolio performance; usually supports a higher safe start `[verify-at-build]` |
| IRA / 401(k) contribution limits | Set annually by the IRS, with catch-up over age 50 | Re-check the current-year figure at the IRS before quoting any number `[verify-at-build]` |
| HSA (HDHP-linked) | Triple tax advantage; annual limit set by the IRS | Eligibility requires a qualifying HDHP — confirm before recommending `[verify-at-build]` |
| RMDs | Required minimum distributions begin at the statutory age | The starting age has changed via recent legislation — verify the current age `[verify-at-build]` |
| Wash-sale rule | Disallows the loss if a substantially identical security is bought within 30 days (±) | Gates tax-loss harvesting; route the specifics to a CPA `[verify-at-build]` |
| Adviser standard (RIA) | Fiduciary duty under the Investment Advisers Act — duty of care + loyalty | Client's interest first; conflicts disclosed and managed `[verify-at-build]` |
| Broker-dealer standard | Regulation Best Interest (Reg BI) | A *different* best-interest standard — never conflate with the RIA fiduciary duty `[verify-at-build]` |
| Form ADV | Part 1 (registration), Part 2A (brochure), Part 2B (supplement), Form CRS (relationship summary) | The disclosure documents; firm-specific filing routes to counsel `[verify-at-build]` |
| Marketing rule | The SEC marketing rule governs testimonials/endorsements, performance, substantiation | Performance/testimonial claims need substantiation and the required disclosures `[verify-at-build]` |
| Books-and-records | Advisers Act recordkeeping requirements | Retain the basis for advice, reviews, the IPS, disclosures — verify retention specifics with counsel `[verify-at-build]` |

_Every figure (contribution limits, RMD age, withdrawal rate) and every rule citation above is a `[verify-at-build]` placeholder: confirm against the IRS / SEC / a primary source for the current year before quoting it to a consumer. Tax conclusions route to a CPA; legal conclusions and firm-specific filings route to counsel. None of this is personalized investment advice._
