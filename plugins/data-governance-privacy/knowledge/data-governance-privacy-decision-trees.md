# Data Governance & Privacy — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before classifying data or handling a data-subject request. This is governance engineering, not legal advice.

## Decision Tree: Classify this data

Classify by sensitivity and personal-data status; the level drives the controls.

```mermaid
graph TD
  A[A data asset] --> B{Contains personal data / PII?}
  B -- Yes --> C{Special-category / sensitive e.g. health, financial?}
  C -- Yes --> D[Restricted + PII flag: strongest controls, lawful basis required]
  C -- No --> E[Confidential + PII flag: access-controlled, retention + DSR scope]
  B -- No --> F{Harmful if disclosed?}
  F -- Yes --> G[Confidential]
  F -- No --> H{Intended for public?}
  H -- Yes --> I[Public]
  H -- No --> J[Internal]
  D --> K[Map level -> enforceable controls -> data-platform/security-engineering]
  E --> K
```

_Classification precedes control; discovery (catalog) precedes classification._

## Decision Tree: Handle a data-subject request

A DSR is an engineered pipeline that depends on knowing where the data is.

```mermaid
graph TD
  A[DSR received] --> B[Verify identity of requester]
  B --> C{Locate ALL of their data via catalog/lineage}
  C -- Can't locate all --> D[GAP: failed capability -> fix discovery/lineage first]
  C -- Located --> E{Request type?}
  E -- Access/portability --> F[Export in a portable format]
  E -- Erasure --> G{Legal basis to retain any e.g. financial record?}
  G -- Yes --> H[Retain the required minimum; erase the rest; document]
  G -- No --> I[Erase across all systems; propagate; verify]
  H --> J[Confirm to subject within the deadline]
  I --> J
  F --> J
```

_Legal interpretation of basis/retention obligations routes to legal / regulatory-compliance._


## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| GDPR | in force | DSR deadlines, lawful basis, minimization |
| CCPA/CPRA | in force | access/delete/opt-out; verify current |
| Data catalogs (OpenMetadata/DataHub/managed) | GA | discovery + lineage + glossary |
| PII discovery/classification | GA (tools + cloud-native) | column-level tagging |
| Pseudonymization vs anonymization | legal distinction | pseudonymized = still personal data |
| Microsoft Purview | GA | Fabric/M365 governance -> microsoft-fabric |
