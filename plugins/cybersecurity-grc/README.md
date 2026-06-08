# Cybersecurity GRC

The **cybersecurity-grc** plugin — the security governance, risk & compliance craft: the framework / control / evidence / audit program layer that turns "we have some security controls" into an attestable, audit-ready compliance program — distinct from the secure code, the cloud config, the privacy mechanic, and the financial regulator's rule themselves.

## Agents

- **`grc-architect`** — Program shape and operating model: framework selection (SOC 2 Trust Services Criteria, ISO 27001 + Annex A, NIST CSF 2.0, NIST 800-53) right-sized to org size/risk/customer demand, scoping the audit boundary, standing up the ISMS, crosswalking controls across frameworks so one evidenced control attests many, and the Statement of Applicability. Designs the program as a product of real security, not an auditor-pleasing checklist.
- **`control-and-evidence-engineer`** — Controls made real and proven: control implementation + operating effectiveness, policy/procedure authoring, evidence collection + continuous control monitoring (CCM), the control-testing cadence, and Type I vs Type II readiness. Tracks every control across the three states — designed, implemented, operating-effectively.
- **`audit-and-third-party-risk-lead`** — Audit readiness and vendor risk: gap assessments, auditor liaison + the PBC list, and third-party risk management (TPRM) — vendor tiering by data/access, proportional assessment (SIG/CAIQ, reading a vendor's SOC 2 exceptions), the shared-responsibility boundary, and ongoing monitoring.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install cybersecurity-grc@ravenclaude
```

## Seams

- **AppSec / secure-coding / threat-modeling judgments** → `security-engineering`; this team says a control objective requires a secure SDLC, they judge the code and the design.
- **Financial-regulator rules (SEC, FINRA, banking, AML/KYC)** → `regulatory-compliance`; we own security/IT frameworks (SOC 2 / ISO 27001 / NIST), they own financial-regulator rule interpretation.
- **Data-subject rights, DPIAs, consent, retention mechanics** → `data-governance-privacy`; we name the privacy/data-handling control objective, they implement the mechanic.
- **Cloud control configuration (encryption, logging, IAM baseline, network)** → `aws-cloud` / `azure-cloud` / `gcp-cloud`; we specify the control objective, they configure and evidence it.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `security-engineering`, `data-governance-privacy`, `regulatory-compliance`, and the cloud plugins.
