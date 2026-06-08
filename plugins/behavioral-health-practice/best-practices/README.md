# Behavioral-health-practice best-practices

Atomic, enforceable rules the behavioral-health-practice agents apply. Each file is one rule with a short rationale; the agents cite them by filename. Canonical decision logic lives in [`../knowledge/behavioral-health-practice-decision-trees.md`](../knowledge/behavioral-health-practice-decision-trees.md); these rules are the always-on priors. **All of it is operational and documentation support — never clinical, medical, or legal advice.**

| Rule | Gist |
|---|---|
| not-clinical-advice-route-to-clinician | Operations/documentation only; clinical calls route to a licensed clinician |
| no-phi-in-artifacts | Placeholders in every template/example; real PHI stays in the EHR |
| part-2-stricter-than-hipaa-assume-it-applies | Treat SUD records as Part 2-covered; specific consent before disclosure |
| medical-necessity-is-the-documentation-backbone | One consistent necessity story across plan, note, and claim |
| the-note-is-a-legal-record | Contemporaneous, consistent format (DAP/SOAP/BIRP), behavioral, factual |
| consent-precedes-disclosure | Verify the ROI before any record leaves the practice, every time |
| code-reflects-the-service-rendered | CPT by what happened, never to maximize reimbursement; verify auth first |
| operations-exist-to-protect-the-clinical-hour | Justify every operational change by clinician time/load returned to care |
