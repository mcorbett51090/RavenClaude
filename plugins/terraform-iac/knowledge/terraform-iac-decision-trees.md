# Terraform & IaC — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before splitting state or drawing a module boundary.

## Decision Tree: How to isolate state

Isolate by blast radius and change cadence, not by team org-chart.

```mermaid
graph TD
  A[An estate to manage] --> B{Does everything change at the same rate & risk?}
  B -- Yes, tiny estate --> C[Single state is fine - for now]
  B -- No --> D[Split by LIFECYCLE/blast radius]
  D --> E[Network/foundational state - rarely changes, high blast]
  D --> F[Data state - stateful, careful]
  D --> G[App state - changes often, low blast]
  E --> H{Multiple environments?}
  F --> H
  G --> H
  H -- Yes --> I[Per-environment state too: dir/workspace/Terragrunt]
```

_Cross-state references via remote-state data sources or outputs — keep them few._

## Decision Tree: Module boundary — extract or inline?

Extract a module when it's reused or is a coherent single responsibility; don't over-abstract.

```mermaid
graph TD
  A[A chunk of config] --> B{Reused in 2+ places?}
  B -- Yes --> C[Extract a versioned module]
  B -- No --> D{Single coherent responsibility worth a contract?}
  D -- Yes --> E[Extract - typed I/O + README]
  D -- No --> F{Just grouping a few resources for readability?}
  F -- Yes --> G[Keep inline or a thin local module]
  F -- No --> H[Inline it - premature module = indirection tax]
```


## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Terraform | GA (BSL license since 1.6) | Verify licensing fit |
| OpenTofu | GA (MPL, Linux Foundation fork) | Drop-in for many; verify provider/module parity |
| State locking backends | mature (S3+DynamoDB/GCS/azurerm/TFC) | Locking is non-negotiable |
| Terragrunt | mature | DRY + explicit; extra tool |
| OPA/Conftest, Sentinel | mature | Evaluate plan JSON; preventive guardrails |
| terraform test | GA | Native module testing |
