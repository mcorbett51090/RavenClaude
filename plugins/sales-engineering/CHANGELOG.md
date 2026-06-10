# Changelog — sales-engineering

All notable changes to the `sales-engineering` plugin. Versioning is semver; bump on every user-visible change.

## 0.1.0 — 2026-06-10

Initial release. The pre-sales / sales-engineering team — the technical side of a B2B sale, from discovery to signature.

- **3 agents:** `sales-engineer` (MEDDPICC discovery, Great Demo! demo design, objection handling, mutual action plan), `poc-evaluation-lead` (POC go/no-go gate, signed success + exit criteria, scorecard), `rfp-security-response-specialist` (RFP go/no-go + response matrix, SIG/CAIQ security questionnaires mapped to SOC 2/ISO evidence, reusable trust-answer library).
- **5 skills:** technical-discovery, demo-design, poc-success-criteria, rfp-response, security-questionnaire-response.
- **4-doc knowledge bank** with 4 Mermaid decision trees: se-engagement-decision-trees, discovery-and-demo-playbook, poc-and-evaluation-best-practices, security-questionnaire-and-trust.
- **5 templates:** technical-discovery-notes, demo-script, poc-success-criteria, rfp-response-matrix, mutual-action-plan.
- **5 best-practices:** discovery-before-demo, honesty-over-the-fabricated-yes, poc-needs-signed-exit-criteria, no-bid-is-a-strategy, map-security-claims-to-evidence.
- **2-scenario bank:** POC sprawl with no exit criteria; security questionnaire with an unverifiable "yes."
- **1 advisory hook:** `flag-se-antipatterns.sh` (POC-with-no-exit-criteria, security-yes-with-no-evidence, overpromise absolutes, demo-with-no-pain-mapping). `SE_STRICT=1` makes it blocking.
- Seams: distinct from `sales-revops` (CRM/forecast/quota ops) and `product-management` (what to build); security claims route to `ravenclaude-core/security-reviewer`. Requires `ravenclaude-core@>=0.7.0`.
