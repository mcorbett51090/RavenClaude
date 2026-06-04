# Data Governance & Privacy

The **data-governance-privacy** plugin — making data discoverable, trustworthy, and lawfully used — a data catalog with lineage, classification of sensitive data and PII, privacy mechanics (GDPR/CCPA subject rights, consent, minimization), and access governance/DLP — the engineering of governance, not legal advice.

## Agents

- **`data-governance-architect`** — The governance operating model: data ownership and stewardship, the classification scheme (public/internal/confidential/restricted + PII tagging), governance policies, the council/RACI, and the maturity roadmap
- **`privacy-compliance-engineer`** — Privacy mechanics as engineering: data-subject rights (access/erasure/portability) pipelines, consent + lawful-basis tracking, data minimization, retention/deletion automation, and pseudonymization vs anonymization
- **`data-catalog-lineage-engineer`** — The data catalog and lineage: sensitive-data/PII discovery and tagging, automated lineage capture, business glossary, metadata management, and access governance/DLP at the data layer

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install data-governance-privacy@ravenclaude
```

## Seams

- **Financial-regulatory obligations (AML/KYC, regulator reporting, jurisdiction-specific rules)** → `regulatory-compliance`; this team does general data governance/privacy engineering, not financial-regulatory.
- **Warehouse row-/column-level security and masking implementation** → `data-platform` (RLS/embed-JWT) and the warehouse; we set the classification + policy they enforce.
- **Microsoft Purview / data governance inside Fabric** → `microsoft-fabric`; we're the tool-neutral governance lane.
- **The security verdict, DLP enforcement, and breach response** → `security-engineering` → `ravenclaude-core/security-reviewer`.
- **Lawful interpretation / contracts / DPAs** → route to legal (out of marketplace scope); we engineer the capability, not the legal opinion.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
