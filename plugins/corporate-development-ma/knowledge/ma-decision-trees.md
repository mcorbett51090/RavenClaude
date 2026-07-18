# Corporate Development & M&A — decision trees

Router + three Mermaid decision trees the agents traverse. Read the matching tree in
full when the situation fits. These encode the §3 house opinions as branch logic.

---

## Skill / agent router

| If the ask is… | Route to | Skill |
|---|---|---|
| "Should we buy this / frame the thesis" | `corpdev-lead` | `frame-a-deal-thesis` |
| "What's it worth / how to structure" | `corpdev-lead` | `triangulate-a-valuation` |
| "Run diligence / what could kill it" | `ma-diligence-lead` | `run-a-diligence-plan` |
| "Plan integration / are synergies real" | `integration-pmi-strategist` | `plan-post-merger-integration` |
| Legal / reps & warranties / regulatory | → counsel (seam) | — |
| Audited numbers / accounting / fairness opinion | → accountants / banker (seam) | — |
| Financing / cash impact | → `treasury-management` (seam) | — |

---

## Tree 1 — Buy vs build vs partner

```mermaid
flowchart TD
  A[Capability / market gap identified] --> B{Can we build it in an<br/>acceptable time & cost?}
  B -- Yes --> C{Is speed-to-market the<br/>decisive factor?}
  C -- No --> Z[Build — cheaper, full control]
  C -- Yes --> D{Is the target's asset<br/>hard to replicate?}
  D -- No --> Y[Partner / license first —<br/>lower risk than acquiring]
  D -- Yes --> E[Acquisition thesis is live]
  B -- No --> F{Is the gap a team,<br/>tech, or market position?}
  F -- Team --> G[Acqui-hire — underwrite retention hard §3 #7]
  F -- Tech --> H[Bolt-on / tuck-in — integration depth matters]
  F -- Market --> I[Platform / scale deal — synergy & antitrust check]
```

Rule: if build or partner achieves the outcome cheaper or faster, the acquisition thesis is weak (§3 #1).

---

## Tree 2 — Valuation-method weighting

```mermaid
flowchart TD
  A[Need a defensible value] --> B[Build all three:<br/>DCF · trading comps · precedents]
  B --> C{Do the three ranges<br/>converge?}
  C -- Yes --> D[Tight range — high confidence.<br/>Net synergies − integration − control premium §3 #2]
  C -- No --> E{What explains the gap?}
  E -- Growth/margin outlier --> F[Weight DCF; comps mis-set]
  E -- Control premium --> G[Precedents high vs trading comps —<br/>that IS the premium; don't double-count]
  E -- Cycle / one-time comps --> H[Down-weight the distorted method,<br/>explain in the memo §3 #4]
  F --> I[Range + walk-away, divergence explained]
  G --> I
  H --> I
```

Rule: the divergence between methods is the finding — explain it, don't average it away (§3 #4).

---

## Tree 3 — Go / no-go gate (post-diligence)

```mermaid
flowchart TD
  A[Diligence complete] --> B{Did diligence confirm<br/>the core thesis assumptions?}
  B -- No --> Z[Kill or renegotiate —<br/>the thesis, not just the price, broke §3 #5]
  B -- Yes --> C{Any red flag with<br/>deal-breaker impact?}
  C -- Yes --> Y[Kill, or price/structure around it<br/>indemnity / escrow / earnout]
  C -- No --> D{Is integration cost priced<br/>into the valuation? §3 #6}
  D -- No --> X[Re-underwrite with integration<br/>cost + dis-synergy before proceeding]
  D -- Yes --> E{Is the price within the<br/>triangulated range & walk-away?}
  E -- No --> W[Walk — a thesis with no<br/>walk-away overpays]
  E -- Yes --> F[Proceed to IC memo & structure]
```
