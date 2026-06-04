# Google Cloud — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before choosing compute or laying out the hierarchy.

## Decision Tree: GCP compute selection

Cloud Run is the default; GKE must earn its cluster ops.

```mermaid
graph TD
  A[A workload] --> B{Small, single-purpose event handler?}
  B -- Yes --> C[Cloud Functions]
  B -- No --> D{Stateless container / HTTP service?}
  D -- Yes --> E{Need k8s features / multi-cloud portability?}
  E -- No --> F[Cloud Run - the default]
  E -- Yes --> G[GKE - Autopilot to cut ops -> cloud-native-kubernetes]
  D -- No --> H{Legacy / specific OS/kernel?}
  H -- Yes --> I[GCE]
  H -- No --> F
```

_Don't reach for GKE when Cloud Run fits._

## Decision Tree: GCP data store selection

Pick by access pattern and the scale you actually need.

```mermaid
graph TD
  A[Data need] --> B{Relational?}
  B -- No --> C{Document / realtime mobile?}
  C -- Yes --> D[Firestore]
  C -- No, analytics --> E[BigQuery -> modeling to data-platform]
  B -- Yes --> F{Global, horizontal scale + strong consistency required?}
  F -- Yes --> G[Spanner - pay for it when you need it]
  F -- No --> H[Cloud SQL - deep modeling to database-engineering]
```


## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Cloud Run | GA | Scale-to-zero; default for services |
| GKE Autopilot | GA | Managed nodes; less ops |
| Workload Identity Federation | GA | Replace SA key files |
| Org Policy constraints | GA | Inherited preventive guardrails |
| Shared VPC | GA | Multi-project networking |
| BigQuery | GA | Service here; analytics -> data-platform |
| Spanner | GA | Global relational; cost-justify |
