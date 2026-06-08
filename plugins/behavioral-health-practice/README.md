# Behavioral Health Practice

The **behavioral-health-practice** plugin — the operations and documentation craft of an outpatient behavioral / mental-health practice: the intake-to-claim back office, the documentation standards, and the authorization/billing front-end that keep the practice running, documented defensibly, and paid — distinct from the clinical care itself.

> **Operational and documentation support only — NOT clinical, medical, or legal advice.** This plugin never diagnoses, recommends treatment, or replaces a licensed clinician's judgment. It is PHI-aware throughout (HIPAA + 42 CFR Part 2): no real PHI in any artifact, and consent precedes every disclosure.

## Agents

- **`practice-operations-lead`** — Practice operations: intake and scheduling, no-show / cancellation management, telehealth operations, caseload / panel management, and referral flow. Designs the intake-to-first-session path, reduces no-shows, and closes referral loops — self-service-first, with clinical steps routed to a clinician.
- **`clinical-documentation-specialist`** — Documentation standards: treatment plans, progress notes (DAP / SOAP / BIRP), medical-necessity language, and release of information (ROI). Builds note/plan templates and audits structure — **structure and standards only, never the clinical content**.
- **`billing-and-authorization-lead`** — Revenue front-end: insurance verification / eligibility, prior authorization, behavioral CPT-code selection, claims basics, and 42 CFR Part 2 + HIPAA in billing. Verifies benefits, assembles auths, picks the code that reflects the service rendered — never upcoding.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install behavioral-health-practice@ravenclaude
```

## Seams

- **A clinical decision (diagnosis, treatment, risk/safety, medication)** → **a licensed clinician**; this plugin never crosses that line.
- **Deep revenue-cycle: denials analytics, payer-contract modeling, full RCM workflow** → `medical-revenue-cycle`; this plugin owns the behavioral-health front-end of billing.
- **Senior / geriatric population specifics, facility-based care** → `senior-care-operations`.
- **HIPAA *security* controls (access controls, encryption, audit logging, BAAs, breach response)** → `cybersecurity-grc`; this plugin is PHI-*aware* operationally, the technical security program is the seam.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `medical-revenue-cycle`, `senior-care-operations`, and `cybersecurity-grc`.
