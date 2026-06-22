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
| OpenTelemetry traces+metrics+logs | GA — all 3 core signals Stable | Logs Data Model + Logs API are **Stable** (no longer "maturing") — [OTel spec status](https://opentelemetry.io/docs/specs/status/) `[verify-at-build — per-language SDK logs maturity still varies]`. **Profiles** is the 4th signal, public **Alpha** (announced ~2026-03) `[verify-at-build — date per OTel spec changelog]`. OTLP is the portable wire format |
| OTel semantic conventions | stabilizing per-domain | HTTP/DB stable; check your domain |
| Tail sampling (collector) | GA | Keep errored/slow traces; cost control |
| Multi-window burn-rate alerts | standard practice (Google SRE) | Fast + slow window AND-ed |
| Exemplars (metric->trace links) | supported in Prometheus/OTel | Jump from a spike to a trace |
| Managed backends | CloudWatch / Azure Monitor / Cloud Monitoring | OTel keeps app code portable across them |

## Decision Tree: SLO target — tighten, loosen, or hold?

**When this applies:** quarterly SLO review or after an incident. The team has budget consumption data and wants to decide whether to adjust the SLO target.

**Last verified:** 2026-06-05 against Google SRE Workbook Chapter 2 and standard SLO review practice.

```mermaid
flowchart TD
    START[SLO review decision point] --> Q1{Was error budget exhausted in the last window?}
    Q1 -->|yes, repeatedly| Q2{Was the team able to act on the policy - freeze and fix?}
    Q2 -->|yes, but still exhausted| TIGHTEN_INFRA[Invest in reliability - do not loosen target yet]
    Q2 -->|no, policy was overridden| POLICY_REVIEW[Fix the policy first - then reassess target]
    Q1 -->|no, budget mostly unused| Q3{Has the system shipped risky changes freely without impact?}
    Q3 -->|yes, budget is slack| LOOSEN[Consider loosening target - invest budget in velocity]
    Q3 -->|no, team was cautious by choice| HOLD[Hold target - the caution is deliberate]
    Q1 -->|yes, one-time event| Q4{Was the event a known outlier - incident, planned migration?}
    Q4 -->|yes| HOLD
    Q4 -->|no, structural| TIGHTEN_INFRA
```

**Rationale per leaf:**
- *Invest in reliability* — repeated exhaustion means the system can't meet its target; fix the reliability gap before raising the bar.
- *Fix the policy first* — a policy that gets overridden isn't a policy; the target adjustment is premature until the policy works.
- *Consider loosening* — consistently unspent budget is over-engineering; loosen to spend more on features.
- *Hold target* — the team deliberately chose caution; the target reflects capability, not over-engineering.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Tighten target | High reliability investment | Low | EM sign-off | Structural repeated exhaustion |
| Loosen target | Frees velocity budget | Low | Team + SRE | Chronic surplus with healthy system |
| Fix the policy | Behavioral change | Low | EM sign-off | Policy is consistently overridden |
| Hold | No change | None | Team review | One-off event or deliberate caution |

## Decision Tree: Which logging level for this event?

**When this applies:** an engineer is adding a log statement and needs to choose the severity level. Wrong level choices pollute query results, inflate costs, and suppress real signal.

**Last verified:** 2026-06-05 against OTel log severity spec and syslog RFC 5424 level semantics.

```mermaid
flowchart TD
    START[A log statement to add] --> Q1{Does the event require human attention or action?}
    Q1 -->|yes| Q2{Does it indicate data loss or service unavailability?}
    Q2 -->|yes| ERROR[ERROR - requires immediate attention]
    Q2 -->|no, degraded but recoverable| WARN[WARN - attention recommended, system continues]
    Q1 -->|no, informational only| Q3{Is it useful during incident investigation?}
    Q3 -->|yes, normal business event| INFO[INFO - key lifecycle events only]
    Q3 -->|yes, only when debugging a problem| DEBUG[DEBUG - disable in production by default]
    Q3 -->|no, verbose tracing| TRACE[TRACE - dev only, never production]
```

**Rationale per leaf:**
- *ERROR* — the system cannot complete an operation; a human or automated alert response is expected.
- *WARN* — the system completed but with a degraded path or a recoverable error; worth investigating before it escalates.
- *INFO* — major lifecycle transitions (service start, connection established, job completed) that paint the activity timeline in an investigation.
- *DEBUG* — detailed diagnostic information useful only when actively debugging; too verbose for normal production volume.
- *TRACE* — raw execution path; production cost is prohibitive; development use only.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| ERROR | High cost if frequent | Triggers alerts | Alert routing | Unrecoverable failures |
| WARN | Medium cost | No alert, visible | None | Recoverable degradations |
| INFO | Low cost at cadence | None | None | Key lifecycle events |
| DEBUG | Disable in prod | None (when off) | None | Debugging a specific problem |

## Decision Tree: Postmortem action item — fix, mitigate, or accept?

**When this applies:** the blameless postmortem has produced a list of contributing factors and the team must decide how to respond to each one.

**Last verified:** 2026-06-05 against Google SRE Workbook Chapter 10 and PagerDuty incident management practice.

```mermaid
flowchart TD
    START[A contributing factor from a postmortem] --> Q1{Would recurrence cause SEV-1 or data loss?}
    Q1 -->|yes| FIX[Fix or eliminate - schedule this sprint]
    Q1 -->|no| Q2{Can the blast radius be reduced with a mitigation control?}
    Q2 -->|yes, low effort| MITIGATE[Mitigate - add the control, schedule within 30 days]
    Q2 -->|yes, high effort| Q3{Is the probability of recurrence high?}
    Q3 -->|yes| MITIGATE
    Q3 -->|no, rare event| ACCEPT[Accept - document the risk and the decision]
    Q2 -->|no, structural limit| Q4{Is this a known platform limitation?}
    Q4 -->|yes| ACCEPT
    Q4 -->|no| FIX
```

**Rationale per leaf:**
- *Fix or eliminate* — high-severity, high-probability contributing factors get a real fix with an owner and sprint commitment.
- *Mitigate* — reducing the blast radius of a factor that can't be eliminated is the next-best outcome; assign an owner.
- *Accept* — documented risk acceptance with a named decision-maker is valid; undocumented inaction is not.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Fix / eliminate | High effort | Reduces future severity | Sprint planning | SEV-1 risk or recurring factor |
| Mitigate | Medium effort | Reduces blast radius | 30-day ticket | High-probability, controllable |
| Accept | Low effort | Unchanged risk | Named decision-maker | Rare, low-blast, or structural limit |
