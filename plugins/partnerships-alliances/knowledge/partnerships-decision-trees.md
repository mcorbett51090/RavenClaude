# Partnerships & Alliances — decision trees

Router + three Mermaid decision trees the agents traverse. Read the matching tree in
full when the situation fits. These encode the §3 house opinions as branch logic.

---

## Skill / agent router

| If the ask is… | Route to | Skill |
|---|---|---|
| "Should we invest in partnerships / which motion?" | `partnerships-lead` | (scoping) |
| "Design our partner tiers" | `channel-program-manager` | `build-a-partner-tiering-model` |
| "How should MDF work?" | `channel-program-manager` | `design-an-mdf-program` |
| "Build a co-sell motion" | `alliance-gtm-strategist` | `structure-a-co-sell-motion` |
| "How much pipeline is the partner driving?" | `alliance-gtm-strategist` | `size-partner-sourced-pipeline` |
| Direct-sales forecast/comp/territory | → `sales-revops` (seam) | — |
| Contract / antitrust / tax terms | → counsel (seam) | — |

---

## Tree 1 — Which partner motion?

```mermaid
flowchart TD
  A[New or unclear partner motion] --> B{Does the partner sell to<br/>a buyer we can't reach<br/>efficiently direct?}
  B -- No --> Z[Partnerships may be the wrong lever<br/>— fix direct GTM first]
  B -- Yes --> C{Does the partner want to<br/>own the transaction & margin?}
  C -- Yes --> D{Do they add delivery/<br/>services value?}
  D -- Yes --> E[Resell / SI motion<br/>margin + enablement + deal-reg]
  D -- No --> F[Reseller / VAR<br/>margin-led, watch channel conflict]
  C -- No --> G{Is value created by a<br/>product integration?}
  G -- Yes --> H[ISV / tech alliance<br/>joint value prop + marketplace + co-sell]
  G -- No --> I[Referral motion<br/>referral fee, low friction, no margin]
```

Rule: choose the motion from the **economics** ([`partnership-economics.md`](partnership-economics.md)) before designing a program (§3). Don't grant resale margin to a partner who only refers.

---

## Tree 2 — Tier design (obligation-for-benefit)

```mermaid
flowchart TD
  A[Proposed tier + benefit] --> B{Is there a concrete<br/>partner obligation for<br/>this benefit?}
  B -- No --> Z[Not a tier — it's a discount<br/>with a badge. Add an obligation<br/>or drop the benefit §3 #2]
  B -- Yes --> C{Is the obligation<br/>measurable & time-bound?}
  C -- No --> Y[Rewrite the threshold<br/>e.g. 'N certs AND $X sourced<br/>pipeline TTM']
  C -- Yes --> D{Is there a demotion rule?}
  D -- No --> X[Add demotion — a tier you<br/>never leave is an entitlement]
  D -- Yes --> E{Do the benefit costs pencil<br/>vs cost-to-serve & sourced rev?}
  E -- No --> W[Reprice the benefits]
  E -- Yes --> F[Valid tier — ship with a<br/>re-qualification cadence]
```

---

## Tree 3 — Co-sell readiness

```mermaid
flowchart TD
  A[Proposed co-sell motion] --> B{Real account overlap<br/>between the two parties?}
  B -- No --> Z[No overlap, no co-sell<br/>— stop. Build overlap first §3 #3]
  B -- Yes --> C{Is there a joint value prop<br/>— an outcome neither<br/>delivers alone?}
  C -- No --> Y[Not a co-sell, a co-brand<br/>— define the JVP §3 #4]
  C -- Yes --> D{Are individual reps named<br/>on both sides?}
  D -- No --> X[Map rep-to-rep pairings]
  D -- Yes --> E{Is there a shared incentive<br/>each rep feels?}
  E -- No --> W[Add SPIFF / quota relief /<br/>referral fee]
  E -- Yes --> F[Ready — pick first 3 accounts<br/>with owners & next actions]
```
