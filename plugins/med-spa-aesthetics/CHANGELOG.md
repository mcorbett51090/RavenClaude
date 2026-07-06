# Changelog — med-spa-aesthetics

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-04

Initial release.

### Added

- **3 agents** — `med-spa-operations-lead` (injector/room utilization, service mix across injectables/devices/skincare/memberships, device payback, pricing per provider-hour, membership economics), `patient-coordinator-lead` (consult-to-treatment conversion, booking, no-show / deposit policy, rebooking on the clinical cadence, membership enrollment), `aesthetics-compliance-advisor` (scope of practice, good-faith exam / supervision structure, consent & adverse-event protocols, product handling, marketing claims — flags to a professional).
- **4 skills** — `consult-to-treatment-conversion`, `treatment-room-and-injector-utilization`, `service-mix-injectables-devices-memberships`, `scope-of-practice-and-supervision`.
- **Knowledge bank** — `med-spa-decision-trees.md` (4 Mermaid trees: add a service/device, design the membership, rebook on the treatment cadence, scope & supervision structure) and `med-spa-reference-2026.md` (dated reference: injector/room utilization, service mix & device payback, consult conversion / no-show / membership, and compliance-structure concepts — each with source placeholder + retrieval date + verify-at-use).
- **5 best-practices** — the consult is the conversion point, rebook on the treatment cadence, injectables are perishable provider-hours, membership smooths cash but breakage is a liability, scope of practice is a medical-director call.
- **2 templates** — med-spa-kpi-dashboard, service-and-device-pro-forma.
- **2 commands** — `/model-device-payback`, `/design-membership`.

### Scope & verify-at-use

- **Operations and financial decision-support, not legal, tax, or medical advice.** The agents make no clinical or legal determinations and store no patient PHI/PII.
- All benchmarks in `med-spa-reference-2026.md` (injector productivity, service margins, consult conversion, no-show rates, membership norms) are volatile and market-/practice-specific — each carries a retrieval date + `[verify-at-use]`; re-confirm against a current source and the practice's own baseline before quoting or acting.
- Scope of practice, good-faith exam / supervision, consent sufficiency, corporate-practice-of-medicine / MSO structure, worker classification, wage/tax, lease, and deposit/membership payment-processor / consumer-protection rules are flagged for the medical director and a licensed professional; the agents map the structure and model the economics and do not render the legal/medical call. The clinical treatment plan and cadence are the provider's call.
