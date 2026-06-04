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


## Decision Tree: Logs, metrics, or traces — which pillar for this question?

Each pillar answers a different shape of question; reach for the one built for yours instead of forcing the wrong tool.

```mermaid
graph TD
  A[A question about the system] --> B{Asking 'how often / how much' over time?}
  B -- Yes --> C[Metric: cheap, aggregatable, dashboards + alerts]
  B -- No --> D{Asking 'where in the request path / which hop is slow'?}
  D -- Yes --> E[Trace: per-request, spans across services]
  D -- No --> F{Asking 'why did THIS specific event happen'?}
  F -- Yes --> G[Log: high-cardinality detail for one event]
  F -- No --> H{Need to pivot spike -> example -> detail?}
  H -- Yes --> I[Use all three, correlated by trace context]
```

_If you're tempted to put a per-request id on a metric label, you actually wanted a trace or a log._

## Decision Tree: On-call — page, ticket, or dashboard?

Route a condition to the response it deserves; paging on the non-urgent is how real pages get ignored.

```mermaid
graph TD
  A[A condition you detected] --> B{Needs human action within minutes?}
  B -- No --> C{Needs action eventually?}
  C -- Yes --> D[Ticket: tracked, async, owned]
  C -- No --> E[Dashboard/log only: context, not a notification]
  B -- Yes --> F{Is there a runbook + a clear action?}
  F -- No --> G[Write the runbook first; if you can't, it isn't pageable]
  F -- Yes --> H{User-visible symptom or SLO burn?}
  H -- Yes --> I[Page now]
  H -- No --> D
```

_Page = act now; ticket = act soon; dashboard = look when investigating. Most conditions are not pages._

## Decision Tree: Cardinality — label or attribute?

A new dimension is either a bounded metric label or unbounded telemetry detail; choosing wrong is how the TSDB falls over.

```mermaid
graph TD
  A[A new dimension to record] --> B{Is its value set bounded and small?}
  B -- No --> C{Is the value user- or attacker-controlled?}
  C -- Yes --> D[Never a label. Trace attribute / log field; or template/bucket it]
  C -- No --> E{Can you safely bucket/template it?}
  E -- Yes --> F[Bucket it, then use as a bounded label]
  E -- No --> D
  B -- Yes --> G{Will you filter/aggregate metrics by it?}
  G -- Yes --> H[OK as a metric label - within the cardinality budget]
  G -- No --> D
```

_Series count = product of every label's distinct values. If you can't name the upper bound, it isn't a label._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| OpenTelemetry traces+metrics | GA | Logs maturing; OTLP is the portable wire format |
| OTel semantic conventions | stabilizing per-domain | HTTP/DB stable; check your domain |
| Tail sampling (collector) | GA | Keep errored/slow traces; cost control |
| Multi-window burn-rate alerts | standard practice (Google SRE) | Fast + slow window AND-ed |
| Exemplars (metric->trace links) | supported in Prometheus/OTel | Jump from a spike to a trace |
| Managed backends | CloudWatch / Azure Monitor / Cloud Monitoring | OTel keeps app code portable across them |
