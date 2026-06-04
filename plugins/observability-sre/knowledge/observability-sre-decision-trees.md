# Observability & SRE — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before designing an alert or setting an SLO target.

## Decision Tree: Should this be an alert (and how)?

Most metrics should not page. Gate ruthlessly on actionability and symptom-vs-cause.

```mermaid
graph TD
  A[A condition you might alert on] --> B{Is a human action required NOW?}
  B -- No --> C[Not a page. Dashboard or ticket.]
  B -- Yes --> D{Symptom user feels, or internal cause?}
  D -- Cause e.g. high CPU --> E{Does it reliably precede user pain?}
  E -- No --> C
  E -- Yes --> F[Alert, but prefer the symptom]
  D -- Symptom --> G{Tied to an SLO?}
  G -- Yes --> H[Multi-window burn-rate alert + runbook]
  G -- No --> I[Define the SLO first, then alert on its burn]
```

_Every page links to a runbook and a human action, or it gets deleted._

## Decision Tree: Setting an SLO target

Choose the target by user need and the cost of nines — then derive the budget.

```mermaid
graph TD
  A[New service SLO] --> B{User-facing & revenue-critical?}
  B -- Yes --> C{Hard dependency for users?}
  C -- Yes --> D[99.9%-99.95%: budget ~22-43 min/mo]
  C -- No --> E[99.5%-99.9%]
  B -- No, internal/batch --> F{Downstream pages on it?}
  F -- Yes --> E
  F -- No --> G[99%-99.5%: generous budget, spend on velocity]
  D --> H[Set error-budget policy: ship vs freeze]
  E --> H
  G --> H
```


## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| OpenTelemetry traces+metrics | GA | Logs maturing; OTLP is the portable wire format |
| OTel semantic conventions | stabilizing per-domain | HTTP/DB stable; check your domain |
| Tail sampling (collector) | GA | Keep errored/slow traces; cost control |
| Multi-window burn-rate alerts | standard practice (Google SRE) | Fast + slow window AND-ed |
| Exemplars (metric->trace links) | supported in Prometheus/OTel | Jump from a spike to a trace |
| Managed backends | CloudWatch / Azure Monitor / Cloud Monitoring | OTel keeps app code portable across them |
