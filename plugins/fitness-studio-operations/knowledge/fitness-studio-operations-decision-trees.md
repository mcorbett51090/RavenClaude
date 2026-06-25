# Fitness Studio Operations — Decision Trees

> Reference decision trees for the `fitness-studio-operations` team. Agents **traverse the relevant tree top-to-bottom before choosing** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> _Last reviewed: 2026-06-25 by `claude`. Principles are durable; specific platform/fee/benchmark names live (dated) in [`fitness-studio-operations-reference-2026.md`](fitness-studio-operations-reference-2026.md)._

---

## Decision Tree: which membership model?

```mermaid
graph TD
    A[Choosing a membership model] --> B{Member visit frequency + commitment}
    B -- "low / one-off / tourist" --> C[Drop-in<br/>high margin, volatile, no retention]
    B -- "mid / flexibility-seeking" --> D[Class packs<br/>cash pulled forward, expiry churn cliff]
    B -- "high / committed regular" --> E{Is churn managed?}
    E -- no --> F[Fix retention first<br/>recurring fails on churn]
    E -- yes --> G[Unlimited recurring<br/>predictable MRR — the engine]
    A --> H{Pre-open or launch phase?}
    H -- yes --> I[Founding-member rate<br/>CAP the cohort + SUNSET the terms]
    H -- no --> B
```

**Rule:** name the cash-flow and retention *shape* before the price. Drop-in is volatile high margin; packs pull cash forward but hide an expiry churn cliff; unlimited recurring is the predictable engine but only if churn is managed; founding-member pricing funds the launch at the cost of capped lifetime value, so cap the cohort and sunset the terms.

---

## Decision Tree: retention intervention (at-risk member)

```mermaid
graph TD
    A[Member flagged at-risk] --> B{What's the leading signal?}
    B -- "failed / declined payment" --> C[Involuntary churn<br/>dunning + card update — cheapest save]
    B -- "visit frequency dropping" --> D{First 90 days?}
    D -- yes --> E[Onboarding re-engage<br/>highest-ROI window]
    D -- no --> F[Re-engagement / value nudge<br/>not a price cut]
    B -- "no future booking" --> F
    B -- "pack nearly used up" --> G[Convert to recurring<br/>before last class]
    C --> H{Cost of save < P save × saved LTV?}
    E --> H
    F --> H
    G --> H
    H -- yes --> I[Intervene — almost always < CAC]
    H -- no --> J[Let go; redirect to win-back later]
```

**Rule:** at-risk is a *leading* signal (frequency drop, failed payment, no future booking, pack ending), not the cancel itself. Match the intervention to the signal; lead with value/re-engagement, not a default price cut. Intervene when cost of save < P(save) × saved LTV — which is almost always cheaper than CAC.

---

## Decision Tree: class capacity (prune / hold / grow)

```mermaid
graph TD
    A[A class slot] --> B[Fill rate = avg attendance / capacity]
    B --> C{Fill rate vs target band}
    C -- "below band" --> D{Is it an anchor class?}
    D -- yes --> E[Protect — clear any cut with retention first]
    D -- no --> F[Move time / merge / change format / cut]
    C -- "in band" --> G[Hold]
    C -- "at cap / waitlisted" --> H{Waitlist consistently deep?}
    H -- yes --> I[Add a slot / upsize room / add capacity]
    H -- no --> G
    F --> J[Check margin-per-class first<br/>instructor cost still burns]
```

**Rule:** capacity is utilization per *slot*, not headcount. Below the target fill band and not an anchor class → move/merge/cut, but put margin-per-class (instructor cost still burns on an empty class) on the table first. At cap with a deep waitlist → unmet demand, add capacity before members leave.

---

## Decision Tree: instructor pay model

```mermaid
graph TD
    A[Paying an instructor] --> B{Who controls the draw?}
    B -- "named talent brings own following" --> C[Per-head can work<br/>instructor carries attendance risk]
    B -- "studio-branded class" --> D{Want aligned incentive?}
    D -- yes --> E[Rev-share WITH a per-class floor]
    D -- no --> F[Flat hourly<br/>studio carries attendance risk]
    C --> G[Work example at LOW and HIGH attendance]
    E --> G
    F --> G
    G --> H{Survives a slow week AND a packed week?}
    H -- no --> I[Re-tune floor / rate]
    H -- yes --> J[Adopt — then check 1099 vs W2]
```

**Rule:** pick the pay model on who carries attendance risk and who controls the draw — hourly (studio), per-head (instructor), rev-share (shared, usually needs a floor). Always work an example at low *and* high attendance; the model must survive both. Then run the classification check.

---

## Decision Tree: no-show / late-cancel & the 1099-vs-W2 flag

```mermaid
graph TD
    A[Staff & policy] --> B{Setting a no-show policy?}
    B -- yes --> C[Define WINDOW + PENALTY + ENFORCEMENT in booking system]
    C --> D{Enforced automatically?}
    D -- no --> E[Decoration — waitlist rots, ghost capacity]
    D -- yes --> F[Protects capacity — done]
    A --> G{Classifying an instructor?}
    G --> H{High behavioral + financial control,<br/>ongoing relationship?}
    H -- yes --> I[Lean W2 — misclassification is expensive]
    H -- no --> J[Possibly 1099]
    I --> K[FLAG only — binding call to people-operations-hr + counsel]
    J --> K
```

**Rule:** a no-show policy needs a window, a penalty, and an *enforcement mechanism* wired into booking, or it's decoration. For classification, more control + a permanent, integral relationship leans W2 — but **flag** the risk; the binding determination belongs to `people-operations-hr` and counsel, and the filing to `accounting-bookkeeping`.

---

## See also

- [`fitness-studio-operations-reference-2026.md`](fitness-studio-operations-reference-2026.md) — dated tooling/benchmark map (re-verify before quoting platforms, fees, or benchmarks).
- Skills: [`../skills/design-membership-model/SKILL.md`](../skills/design-membership-model/SKILL.md), [`../skills/compute-studio-unit-economics/SKILL.md`](../skills/compute-studio-unit-economics/SKILL.md), [`../skills/analyze-retention-and-churn/SKILL.md`](../skills/analyze-retention-and-churn/SKILL.md), [`../skills/optimize-class-schedule/SKILL.md`](../skills/optimize-class-schedule/SKILL.md), [`../skills/design-instructor-pay-model/SKILL.md`](../skills/design-instructor-pay-model/SKILL.md).
