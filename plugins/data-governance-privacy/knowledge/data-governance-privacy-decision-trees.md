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

## Decision Tree: Is this anonymized or pseudonymized?

Most 'anonymized' data isn't; the distinction decides whether privacy law still applies.

```mermaid
graph TD
  A[A dataset claimed de-identified] --> B{Is there any key/mapping that can re-link to individuals?}
  B -- Yes, held anywhere --> C[Pseudonymized: STILL personal data - full privacy scope]
  B -- No mapping exists --> D{Could individuals be re-identified by combining with other available data?}
  D -- Yes, singling-out/linkage/inference possible --> C
  D -- No, re-identification not reasonably possible --> E{Verified e.g. k-anonymity/differential-privacy, not just columns dropped?}
  E -- Yes --> F[Anonymized: out of privacy-law scope]
  E -- No, just removed obvious identifiers --> C
  C --> G[Apply lawful basis, DSR scope, retention - it's personal data]
```

_Dropping the name column is not anonymization. Re-identifiability via linkage/inference keeps it personal data; legal interpretation routes to legal._

## Decision Tree: What's the lawful basis for this use?

Every personal-data use needs a recorded basis before it happens; 'we already had it' is not one.

```mermaid
graph TD
  A[A new use of personal data] --> B{Is this use covered by an existing recorded lawful basis?}
  B -- Yes --> C{Is the basis consent?}
  C -- Yes --> D{Consent granular, current, and not revoked for this use?}
  D -- Yes --> E[Proceed; honor revocation propagation]
  D -- No --> F[Re-obtain consent or stop - do NOT proceed]
  C -- No, contract/legal-obligation/legitimate-interest --> G[Proceed within that basis's scope only]
  B -- No, new purpose --> H{Compatible with the original collection purpose?}
  H -- Yes --> I[Document the basis -> legal confirms interpretation]
  H -- No --> F
```

_Processing beyond the basis it was collected under is a violation. Engineer the basis/consent store; the legal interpretation routes to legal/regulatory-compliance._

## Decision Tree: Can this data be deleted now?

Retention is per-category and automated; a legal hold or retention obligation overrides deletion.

```mermaid
graph TD
  A[Retention/deletion decision for a record] --> B{Active legal hold or litigation hold?}
  B -- Yes --> C[Retain; do NOT delete - document the hold]
  B -- No --> D{A specific legal obligation to retain e.g. financial/tax record?}
  D -- Yes --> E[Retain the required minimum for the required period; isolate + restrict]
  D -- No --> F{Still within the purpose/lawful-basis lifespan?}
  F -- Yes --> G[Retain until the defined period ends]
  F -- No --> H[Delete via automated job; log + verify; propagate across copies]
  E --> I[When the obligation expires -> route back to H]
```

_Indefinite retention is unbounded risk. Carve out only what's legally required, isolate it, and let the automated job delete the rest — verified, not hoped._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| GDPR | in force | DSR deadlines, lawful basis, minimization |
| CCPA/CPRA | in force | access/delete/opt-out; verify current |
| Data catalogs (OpenMetadata/DataHub/managed) | GA | discovery + lineage + glossary |
| PII discovery/classification | GA (tools + cloud-native) | column-level tagging |
| Pseudonymization vs anonymization | legal distinction | pseudonymized = still personal data |
| Microsoft Purview | GA | Fabric/M365 governance -> microsoft-fabric |
