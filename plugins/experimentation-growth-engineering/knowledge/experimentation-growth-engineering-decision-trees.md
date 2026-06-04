# Experimentation & Growth — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before reading a result or choosing a flag vs config. Significance verdicts route to applied-statistics.

## Decision Tree: Can I trust this experiment result?

Validate the plumbing before believing any metric; significance is a separate, later question for applied-statistics.

```mermaid
graph TD
  A[Experiment 'finished'] --> B{SRM check passes? observed split == intended}
  B -- No --> C[STOP: assignment is broken; result invalid - fix plumbing]
  B -- Yes --> D{Exposure logged correctly? right population?}
  D -- No --> E[Fix exposure logging; re-run]
  D -- Yes --> F{Pre-registered metric + duration honored no peeking?}
  F -- No --> G[Peeking inflates false positives - use sequential method or re-run]
  F -- Yes --> H{Guardrail metrics OK?}
  H -- No --> I[Primary win but guardrail harm = not a win]
  H -- Yes --> J[Route to applied-statistics for the significance verdict]
```

_This team certifies trustworthiness; applied-statistics certifies significance._

## Decision Tree: Feature flag vs config vs experiment?

Match the mechanism to the intent.

```mermaid
graph TD
  A[A change to control at runtime] --> B{Need to measure impact A vs B?}
  B -- Yes --> C[Experiment flag + assignment + exposure logging]
  B -- No --> D{Need to turn it OFF fast in an incident?}
  D -- Yes --> E[Ops flag / kill switch - long-lived]
  D -- No --> F{Per-user/plan entitlement?}
  F -- Yes --> G[Permission flag - permanent]
  F -- No --> H{Temporary, for a launch rollout?}
  H -- Yes --> I[Release flag - owner + removal date]
  H -- No --> J[Maybe just config, not a flag]
```

## Decision Tree: Ship, iterate, or kill after a test?

Only after the result is trustworthy AND significant; the apparatus certifies the former, applied-statistics the latter.

```mermaid
graph TD
  A[Test concluded] --> B{Trustworthy? SRM/exposure/no-peek all pass}
  B -- No --> C[Don't read it - fix plumbing and re-run]
  B -- Yes --> D{applied-statistics: significant on the PRIMARY metric?}
  D -- No, flat/inconclusive --> E{Underpowered or genuinely no effect?}
  E -- Underpowered --> F[Run longer / bigger only if pre-committed]
  E -- No effect --> G[Kill the variant - ship control]
  D -- Yes, treatment wins --> H{Guardrail metrics held?}
  H -- No --> I[Not a win - the guardrail harm is the result]
  H -- Yes --> J[Ship treatment; clean up the experiment flag]
```

_A significant primary with a tripped guardrail is a trade for the business to make, not an automatic ship._

## Decision Tree: Fixed-horizon or sequential test?

Pick the analysis regime up front; mixing them (peeking a fixed-horizon test) is the false-positive trap.

```mermaid
graph TD
  A[Designing the test] --> B{Is early stopping valuable e.g. risky change, fast learning?}
  B -- No --> C[Fixed-horizon: pre-register N + duration, hide readout till the end]
  B -- Yes --> D{Will applied-statistics support a sequential method?}
  D -- No --> C
  D -- Yes --> E{Stopping for a WIN, harm, or both?}
  E -- Harm only --> F[Guardrail/safety monitoring + fixed-horizon for the win]
  E -- Win or both --> G[Sequential: always-valid p-values / group-sequential boundary]
  C --> H[Apparatus: lock the readout until the horizon]
  G --> I[Apparatus: expose only the valid stopping boundary]
```

_Either method is valid; checking a fixed-horizon test daily is not one of them._

## Decision Tree: Is this event instrumented correctly?

Before an event feeds a funnel or a metric, validate it against the tracking plan.

```mermaid
graph TD
  A[A new/suspect event] --> B{In the tracking plan with a single canonical definition?}
  B -- No --> C[Define it once + add to the plan before firing]
  B -- Yes --> D{Fired from ONE place, not re-derived in N clients?}
  D -- No --> E[Consolidate - divergent definitions corrupt cross-analysis]
  D -- Yes --> F{Names + property types match the schema?}
  F -- No --> G[Fix to convention; validate events as code]
  F -- Yes --> H{Carries identity that stitches anon -> known?}
  H -- No --> I[Add stitching - funnels break at the login boundary]
  H -- Yes --> J[Trustworthy event - safe to build metrics on]
```

_Garbage events in means no analysis out; most 'our data is a mess' is a missing/ignored plan._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Feature-flag platforms (LaunchDarkly/Flagsmith/OSS) | GA | Targeting, kill switches, SDKs |
| CDP (Segment/RudderStack) | GA | Instrument once, fan out |
| Product analytics (Amplitude/PostHog/Mixpanel) | GA | Funnels, retention, experiments |
| SRM checks | standard practice | Catch broken assignment |
| Sequential testing | available | Valid peeking (with applied-statistics) |
| Server-side experimentation | recommended | Avoid client-side flicker/leak |
