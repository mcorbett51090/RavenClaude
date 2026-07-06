# Incident-response-dfir — best-practice docs

Named, citable rules for the `incident-response-dfir` plugin's two agents. Each file is **one rule**, grounded in this plugin's knowledge bank and the agents' house opinions — read, applied, and cited as a whole.

These complement, and do not restate, the cross-cutting house opinions in the team constitution ([`../CLAUDE.md`](../CLAUDE.md)) or the automated smell checks in the advisory hook. They take one opinion each and make it a standalone, exception-documented rule.

---

## Index

_5 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`contain-before-you-eradicate.md`](./contain-before-you-eradicate.md) | Absolute rule | Running a live incident — stop the spread before removing the root cause; the phases have an order. |
| [`preserve-evidence-before-you-remediate.md`](./preserve-evidence-before-you-remediate.md) | Absolute rule | Before any destructive remediation — capture volatile evidence (memory) first; a power-off destroys it. |
| [`severity-drives-the-response-not-the-noise.md`](./severity-drives-the-response-not-the-noise.md) | Absolute rule | Triaging an alert — classify by business impact × scope, not by how alarming the alert looks. |
| [`every-detection-maps-to-attack-and-has-a-tuning-plan.md`](./every-detection-maps-to-attack-and-has-a-tuning-plan.md) | Pattern (strong default) | Writing a detection — map it to ATT&CK and ship a false-positive tuning plan, or it dies in the noise. |
| [`notification-timelines-are-legal-deadlines-not-guidelines.md`](./notification-timelines-are-legal-deadlines-not-guidelines.md) | Absolute rule | A breach of regulated/personal data — the clock (GDPR 72h etc.) starts at awareness; flag legal review. |
