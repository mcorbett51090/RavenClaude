# New-unit go/no-go decision tree

> **Last reviewed:** 2026-07-07. Confidence: **high** on the framework (underwrite bottom-up, load the
> royalty, capitalize the ramp); **volatile** on any specific fee/figure. Every fee percentage, Item-19
> number, and investment figure is **[verify-at-use]** from the current FDD. This is business
> decision-support, **not** legal, financial, or investment advice — binding FDD/agreement review routes
> to `legal-ops-clm`; deep model mechanics route to `finance`.

```mermaid
flowchart TD
    A[Franchise buy or new unit?] --> B{Market & site validated?<br/>traffic, demographics, competition}
    B -->|No| X[No-go / keep looking:<br/>a great brand on a bad site loses]
    B -->|Yes| C[Build bottom-up revenue<br/>traffic x ticket - NOT the brand AUV]
    C --> D[Take fees off the top<br/>royalty + ad fund + tech - verify from FDD Item 6]
    D --> E[Layer prime cost + occupancy + opex<br/>-> unit operating profit]
    E --> F{Break-even with headroom<br/>at -20% revenue stress?}
    F -->|No| X
    F -->|Yes| G{Capitalized for the ramp?<br/>fee + build-out + working capital}
    G -->|No| Y[No-go until capitalized:<br/>undercapitalization is the #1 unit killer]
    G -->|Yes| H{FDD read clean?<br/>Item 20 churn, Item 19 cohort, Item 12 territory}
    H -->|Red flags| Z[Conditional: counsel review + more diligence<br/>-> legal-ops-clm]
    H -->|Clear| GO[GO: sign with counsel review of Item 17 terms]
```

## Reading the tree

- **Site before brand.** A validated market/site is the precondition; brand strength can't rescue a bad location.
- **Fees off the top, then the P&L.** The royalty-loaded model is the real one.
- **Ramp capital is part of the decision**, not an afterthought — model the months of negative cash.
- **Item 20 churn + Item 19 cohort + Item 12 territory** are the FDD reads that most change a go/no-go.
- **Every path to GO still routes the agreement terms (Item 17) to `legal-ops-clm`.**

## The franchise fee stack (verify each from the current FDD)

| Fee | Item | Note `[verify-at-use]` |
|---|---|---|
| Initial franchise fee | 5 | One-time, at signing |
| Royalty | 6 | Ongoing % of gross revenue — off the top |
| Ad / brand fund | 6 | Ongoing % of gross — off the top |
| Tech / other recurring | 6 | POS, software, required services |
| Required purchases | 8 | Approved suppliers — a margin (and rebate) issue |

## Re-verify each time you use this file

- The exact royalty / ad-fund / fee percentages (Items 5, 6) from the current FDD edition.
- Item 19 cohort definition and whether an FPR is even provided.
- Item 20 outlet table (openings / closures / transfers) for the last 3 years.
- State registration/relationship-law specifics (route to counsel).
