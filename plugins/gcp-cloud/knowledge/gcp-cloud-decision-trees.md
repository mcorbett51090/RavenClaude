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

## Decision Tree: How to lay out the hierarchy?

Folders bound blast radius and inherit policy; projects are the unit of isolation.

```mermaid
graph TD
  A[New GCP estate] --> B{More than one team or environment?}
  B -- No, single tiny app --> C[One project - revisit as you grow]
  B -- Yes --> D[Organization + folders]
  D --> E{Group folders by env or by department?}
  E -- Env --> F[Folders: prod / nonprod / shared]
  E -- Dept --> G[Folders per dept, env folders beneath]
  F --> H[One project per app/workload under the folder]
  G --> H
  H --> I[Set org-policy constraints at org/folder for inheritance]
```

_One project per workload is the GCP equivalent of an account boundary; a flat pile of resources in one project has no isolation and no clean billing._

## Decision Tree: How to connect projects/networks?

Shared VPC for centrally-managed multi-project; PSC for private service exposure; peering only for simple non-transitive links.

```mermaid
graph TD
  A[Connect networks] --> B{Many projects sharing one central network + central admin?}
  B -- Yes --> C[Shared VPC - host + service projects]
  B -- No --> D{Just consume ONE service privately?}
  D -- Yes --> E[Private Service Connect]
  D -- No, link two VPCs --> F{Simple, non-transitive, distinct CIDRs?}
  F -- Yes --> G[VPC Network Peering]
  F -- No, hub/transitive/on-prem --> H[Network Connectivity Center / Cloud VPN/Interconnect]
```

_Peering isn't transitive; Shared VPC centralizes network control across projects; PSC exposes a service without joining networks._

## Decision Tree: Which IAM grant?

Match the role to the job and bind it at the right hierarchy level; primitive roles are almost never the answer.

```mermaid
graph TD
  A[Need to grant access] --> B{A predefined role matches the job?}
  B -- Yes --> C{Need to scope further by resource/condition?}
  C -- Yes --> D[Predefined role + IAM Condition]
  C -- No --> E[Predefined role]
  B -- No, no clean fit --> F[Author a custom role - minimum permissions]
  E --> G{Bind to a person or a workload?}
  D --> G
  F --> G
  G -- Workload --> H[Dedicated service account via Workload Identity - no key]
  G -- People --> I[Group, bound at folder/project - not per user]
```

_Owner/Editor 'to make it work' is the most common over-grant; reach for predefined first, custom when none fits, primitive essentially never in prod._

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
