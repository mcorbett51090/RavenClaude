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


## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Feature-flag platforms (LaunchDarkly/Flagsmith/OSS) | GA | Targeting, kill switches, SDKs |
| CDP (Segment/RudderStack) | GA | Instrument once, fan out |
| Product analytics (Amplitude/PostHog/Mixpanel) | GA | Funnels, retention, experiments |
| SRM checks | standard practice | Catch broken assignment |
| Sequential testing | available | Valid peeking (with applied-statistics) |
| Server-side experimentation | recommended | Avoid client-side flicker/leak |
