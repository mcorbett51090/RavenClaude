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

## Decision Tree: Access request — approve, restrict, or deny?

**When this applies:** a data access request arrives for a Confidential or Restricted data asset. Observable inputs: the requestor's role and stated purpose, the classification of the requested asset, whether a steward has approved, and whether the request is time-bounded.

**Last verified:** 2026-06-05 against ISO 27001 A.9.2 access management guidelines and GDPR Article 5(1)(f).

```mermaid
flowchart TD
    START[Access request received] --> Q1{Is the requested asset Confidential or Restricted PII?}
    Q1 -->|NO - Internal or Public| AUTO[Auto-approve with logging - no steward required]
    Q1 -->|YES| Q2{Has the steward for this domain approved?}
    Q2 -->|NO| PENDING[Hold - route to domain steward for approval]
    Q2 -->|YES| Q3{Is a legitimate purpose documented?}
    Q3 -->|NO| DENY[Deny - purpose required for all PII access]
    Q3 -->|YES| Q4{Is the access time-bounded - max 90 days?}
    Q4 -->|NO or indefinite| RESTRICT[Grant masked access only - or require expiry date]
    Q4 -->|YES| Q5{Does requestor already have unmasked PII access?}
    Q5 -->|YES - additive request| REVIEW[Steward reviews cumulative access scope before granting]
    Q5 -->|NO - first grant| GRANT[Grant with expiry - log in access register]
    AUTO --> LOG[Log grant in access register]
    GRANT --> LOG
    RESTRICT --> LOG
```

**Rationale per leaf:**
- *AUTO* — Internal/Public assets have no PII sensitivity; auto-approval reduces friction for non-sensitive data without undermining governance.
- *PENDING* — steward approval is the accountability mechanism; no PII access without a named approver on record.
- *DENY* — "I just want to look at it" is not a purpose; every PII access grant requires a documented business use case.
- *RESTRICT* — an indefinite grant is an unmanaged grant; masked access is the fallback when the requestor won't accept a time boundary.
- *REVIEW* — cumulative access (a user who has three separate active grants) may add up to a broader scope than any single grant intended; steward reviews the aggregate.
- *GRANT* — time-bounded, purpose-documented, steward-approved grants are the governed baseline.

**Tradeoffs summary:**

| Grant type | Steward needed | Expiry required | Audit trail | Use when |
|---|---|---|---|---|
| Internal / Public auto-approve | No | No | Yes (log) | Non-sensitive assets |
| Masked Confidential+PII | Yes | Yes | Yes | Analysis needing behavioral data not raw PII |
| Unmasked Restricted+PII | Yes | Yes | Yes | Production data handling, DSR execution |
| Service account (BI tool) | Yes (provisioning) | No (permanent) | Yes | Operational connections — reviewed annually |

---

## Decision Tree: Governance maturity — where should we invest next?

**When this applies:** an organization is starting or advancing a governance program and must choose the next investment. Observable inputs: whether a discovery/catalog exists, whether classification is in place, whether access controls are enforced, and whether the DSR pipeline is operable.

**Last verified:** 2026-06-05 against DAMA-DMBOK data management maturity model.

```mermaid
flowchart TD
    START[Governance investment needed] --> Q1{Does a current inventory of all data assets exist?}
    Q1 -->|NO| DISCOVER[Priority 1 - Data discovery and catalog setup - you cant govern what you cant find]
    Q1 -->|YES| Q2{Are all assets classified - at minimum PII vs non-PII?}
    Q2 -->|NO| CLASSIFY[Priority 2 - Classification scheme and tagging - classification drives controls]
    Q2 -->|YES| Q3{Are access controls enforced at the data layer - not just the app layer?}
    Q3 -->|NO| ACCESS[Priority 3 - Least-privilege access + column masking at the warehouse]
    Q3 -->|YES| Q4{Is a DSR pipeline operable - can erasure and access requests be executed?}
    Q4 -->|NO| DSR[Priority 4 - DSR pipeline engineering - erasure must be executable]
    Q4 -->|YES| Q5{Is retention automated - data deleted at end of its lifecycle?}
    Q5 -->|NO| RETAIN[Priority 5 - Retention automation and lifecycle management]
    Q5 -->|YES| Q6{Is lineage tracked from source to consumption - including PII propagation?}
    Q6 -->|NO| LINEAGE[Priority 6 - End-to-end lineage with PII column tracking]
    Q6 -->|YES| MATURE[Mature - focus on stewardship quality + glossary + governance metrics]
```

**Rationale per leaf:**
- *DISCOVER* — no governance investment matters without an inventory; policy on un-inventoried data is theater.
- *CLASSIFY* — classification is the key that maps to controls; without it, every access and retention decision is manual guesswork.
- *ACCESS* — controls at the app layer can be bypassed via direct DB access; the warehouse is the enforcement layer.
- *DSR* — regulatory deadlines (GDPR 30 days, CCPA 45 days) make DSR operability non-optional for any organization handling EU/CA residents' data.
- *RETAIN* — indefinite retention of PII is unbounded risk; automated deletion is cheaper than a manual audit of every record.
- *LINEAGE* — lineage is the prerequisite for complete DSR execution and impact analysis on schema changes.
- *MATURE* — a mature program's marginal value shifts from building capabilities to improving stewardship quality and governance metrics.

**Tradeoffs summary:**

| Stage | Compliance risk before | Compliance risk after | Effort | Quick win |
|---|---|---|---|---|
| Discovery + catalog | Blind to what exists | Aware | Medium | Column-name PII heuristic scan |
| Classification | Policy not applicable | Policy applicable | Low | Tier the highest-risk domain first |
| Access controls | Any analyst can see PII | PII role-gated | Medium | Column masking on one table |
| DSR pipeline | Regulatory exposure | DSR-compliant | High | Manual DSR runbook as interim |
| Retention automation | Unbounded PII accumulation | Lifecycle-managed | Medium | One automated deletion job per domain |
| Lineage | Incomplete DSR | Complete DSR | High | dbt lineage → OpenMetadata integration |

---

## Decision Tree: Anonymization technique — which method for this use case?

**When this applies:** personal data must be shared, published, or used for analytics/ML where the recipient/model should not be able to re-identify individuals. Observable inputs: dataset size (n), the number of quasi-identifiers, the required analytical utility, and whether an adversarial re-identification attack is a realistic threat.

**Last verified:** 2026-06-05 against ICO Anonymisation guidance (UK) and GDPR Recital 26.

```mermaid
flowchart TD
    START[Need to share or use personal data without identification] --> Q1{Is aggregate statistics the only output needed?}
    Q1 -->|YES - only counts/sums/averages| DP[Differential privacy - add calibrated noise - protects individuals in aggregates]
    Q1 -->|NO - individual-level records needed| Q2{How many quasi-identifiers does the dataset have?}
    Q2 -->|Few - under 5 quasi-IDs| Q3{Is k-anonymity k=5+ achievable without destroying utility?}
    Q3 -->|YES| KANON[k-anonymity - generalize quasi-IDs until k=5 or higher]
    Q3 -->|NO - dataset too sparse| SYNTH[Synthetic data generation - replace records with model-generated rows]
    Q2 -->|Many quasi-IDs - over 5| Q4{Is ML model training the use case?}
    Q4 -->|YES| DP_TRAIN[DP-SGD training - differential privacy during model training]
    Q4 -->|NO - analyst use| SYNTH
    KANON --> VERIFY[Re-identification risk assessment - confirm k=5+ survives linkage attack]
    DP --> VERIFY
    SYNTH --> VERIFY
    DP_TRAIN --> VERIFY
    VERIFY --> LABEL{Did it pass re-identification risk assessment?}
    LABEL -->|YES| ANON_OK[Treated as anonymized - document the technique and assessment]
    LABEL -->|NO| PSEUDO[Pseudonymized - still personal data - apply full privacy controls]
```

**Rationale per leaf:**
- *DP* — aggregate statistics (counts, histograms, averages) can be shared with mathematically-proven privacy via calibrated Laplace or Gaussian noise; the individual-level records are never exposed.
- *KANON* — k-anonymity (every record is indistinguishable from at least k-1 others on all quasi-identifiers) is the practical standard for small-quasi-ID datasets; k=5 is the typical floor.
- *SYNTH* — when k-anonymity destroys too much utility (sparse dataset + many quasi-IDs), synthetic data preserves statistical properties without linking to real individuals.
- *DP_TRAIN* — ML model training on individual records is the highest re-identification risk; DP-SGD (differentially private stochastic gradient descent) trains the model without memorizing individual records.
- *VERIFY* — every technique must be followed by a re-identification risk assessment; the technique choice is not a guarantee, the assessment is.
- *PSEUDO* — if the re-identification risk assessment fails, the data remains pseudonymized (not anonymized) and full privacy controls apply.

**Tradeoffs summary:**

| Technique | Analytical utility | Re-ID protection strength | Complexity | Use when |
|---|---|---|---|---|
| Differential privacy (aggregates) | Low - noise | High (mathematically proven) | Medium | Aggregate statistics only |
| k-anonymity (k=5+) | Medium | Medium (linkage attacks exist) | Low | Individual records - few quasi-IDs |
| Synthetic data | High (distribution preserved) | High (no real records) | High | Individual records - many quasi-IDs |
| DP-SGD training | n/a (model weights) | High | High | ML model training on PII |

---

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| GDPR | in force | DSR deadlines, lawful basis, minimization |
| CCPA/CPRA | in force | access/delete/opt-out; verify current |
| Data catalogs (OpenMetadata/DataHub/managed) | GA | discovery + lineage + glossary |
| PII discovery/classification | GA (tools + cloud-native) | column-level tagging |
| Pseudonymization vs anonymization | legal distinction | pseudonymized = still personal data |
| Microsoft Purview | GA | Fabric/M365 governance -> microsoft-fabric |
