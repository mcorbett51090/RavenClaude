---
name: framework-selection-and-control-mapping
description: "Choose the right security-compliance framework for the org's size/risk/customer demand, scope the audit boundary, crosswalk controls across SOC 2 TSC / ISO 27001 Annex A / NIST CSF 2.0 / 800-53 so one evidenced control attests many, and author a Statement of Applicability whose every exclusion is justified against the risk register."
---

# Framework Selection & Control Mapping

## Start from who's asking and the risk
Right-size the framework to org size, risk, and named customer/contract demand — not ambition. SOC 2 Type II for US B2B SaaS buyers, ISO 27001 for global/enterprise/EU, NIST 800-53/FedRAMP for federal data, NIST CSF 2.0 as the org-wide language when no certification is yet demanded. Don't cargo-cult full 800-53 onto a 20-person SaaS.

## Scope is the highest-leverage decision
Define the audit boundary — systems, locations, people, data, third parties — and carve it to what the org can attest *honestly* this cycle. A narrow clean scope beats a broad scope with gaps the auditor will find. Defend every carve-out against the risk register; expand next cycle.

## Map once, attest many
Pick one primary framework and crosswalk the others to it. A single well-evidenced control should satisfy SOC 2's TSC, ISO 27001's Annex A, and the relevant NIST references simultaneously. Build the crosswalk first; never run parallel control sets for parallel audits. Mark any recalled control text/count `[verify-at-build]`.

## The Statement of Applicability is reasoned
Per control: applicability, justification, implementation status, and the crosswalk reference. Every exclusion needs an auditor-defensible reason traced to the risk register — "N/A" with no reason is a finding waiting to happen.

## Output
A framework + scope recommendation, a control crosswalk (SOC 2 TSC ↔ ISO 27001 Annex A ↔ NIST CSF / 800-53) with the single primary control set, and a reasoned Statement of Applicability. Hand control implementation to `control-and-evidence-engineer`, the audit to `audit-and-third-party-risk-lead`, and technical config to `security-engineering` / the cloud plugins.
