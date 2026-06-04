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

## Decision Tree: Which remote state backend?

Locking is non-negotiable; pick the backend that's native to where you already operate.

```mermaid
graph TD
  A[Need remote state] --> B{Want a managed run/state platform with policy + RBAC?}
  B -- Yes --> C[Terraform/Tofu Cloud or Spacelift/Scalr]
  B -- No, self-managed --> D{Primary cloud?}
  D -- AWS --> E[S3 with native lockfile or DynamoDB lock]
  D -- GCP --> F[GCS - built-in locking]
  D -- Azure --> G[azurerm - blob lease lock]
  D -- Multi/none --> H[Pick one cloud's object store as the home + its lock]
  E --> I[Enable versioning + encryption + restrict access]
  F --> I
  G --> I
```

_Whatever the backend, it must give locking, versioning, encryption, and access control — or it isn't a backend, it's a liability._

## Decision Tree: How to model environments (promotion)

DRY versus explicit. Pick by blast-radius risk and how much config diverges per environment.

```mermaid
graph TD
  A[Multiple environments] --> B{Environments nearly identical, tiny estate?}
  B -- Yes --> C{Accept one workspace = shared backend + risk of wrong-env apply?}
  C -- Yes --> D[Workspaces - lightest, but easy to apply to the wrong env]
  C -- No --> E[Separate directories per env - explicit, isolated state]
  B -- No, config diverges / strong isolation needed --> E
  E --> F{Lots of repeated backend/provider boilerplate across dirs?}
  F -- Yes --> G[Terragrunt - DRY the wiring, keep dirs isolated]
  F -- No --> H[Plain directories]
```

_Workspaces share a backend and a module — fine for ephemeral copies, risky as the prod/dev boundary. Directories are the safer default._

## Decision Tree: Drift found — codify, import, or revert?

When a plan shows divergence, decide deliberately; never let `apply` silently revert a hand-fix.

```mermaid
graph TD
  A[Plan shows unexpected diff] --> B{Was the real-world change intentional and correct?}
  B -- Yes --> C{Is the resource managed by this state?}
  C -- Yes --> D[Update config to match - codify the intent]
  C -- No, created out-of-band --> E[terraform import + write matching config]
  B -- No, accidental/unauthorized --> F{Safe to apply the revert now?}
  F -- Yes --> G[Apply - config is the source of truth]
  F -- No, prod-risky --> H[Investigate + schedule reverting apply with review]
```

_The wrong move is a reflexive `apply` that reverts an emergency console fix and re-breaks prod._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Terraform | GA (BSL license since 1.6) | Verify licensing fit |
| OpenTofu | GA (MPL, Linux Foundation fork) | Drop-in for many; verify provider/module parity |
| State locking backends | mature (S3+DynamoDB/GCS/azurerm/TFC) | Locking is non-negotiable |
| Terragrunt | mature | DRY + explicit; extra tool |
| OPA/Conftest, Sentinel | mature | Evaluate plan JSON; preventive guardrails |
| terraform test | GA | Native module testing |
