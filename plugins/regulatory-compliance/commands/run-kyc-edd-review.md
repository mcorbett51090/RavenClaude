---
description: Run a KYC / EDD review the way an examiner reads it — risk-rate the customer first to select SDD/CDD/EDD depth, make EDD real (independent verification + senior approval + recorded rationale), screen sanctions with list-version capture and binary disposition, and document any no-action decision.
argument-hint: "[the customer + context, e.g. 'EDD on a corporate at a mid-sized insurer']"
---

# Run a KYC / EDD review

You are running `/regulatory-compliance:run-kyc-edd-review`. Review the customer file the user described (`$ARGUMENTS`), following this plugin's `aml-kyc-analyst` discipline. Due-diligence depth is an output of a risk rating, not a starting assumption — a rating the examiner cannot reproduce did not happen.

## When to use this

Onboarding due diligence, a periodic refresh, or an EDD package on a higher-risk relationship. Not for the suspicious-activity decision itself (that's the SAR command) and not for legal-conclusion questions ("is this structure lawful") — those route to counsel.

## Steps

1. **Scope the jurisdiction and regime first** (`scope-the-jurisdiction-before-you-map`): name the regulator + regime before applying any threshold word; route Bermuda specifics to `bermuda-insurance-specialist`. The applicable CDD/SDD permissions and EDD triggers are jurisdiction-specific.
2. **Risk-rate before choosing depth** (`aml-risk-rate-before-you-choose-cdd-depth`): run the customer-risk-rating model (customer type, product, geography, delivery channel) and let the tier select SDD / CDD / EDD. Record inputs, weights, output tier, and date so it is reproducible. An EDD trigger (PEP, high-risk jurisdiction, opaque ownership, large unexplained cash, correspondent/nested relationship) forces the high tier regardless of the base score.
3. **Make EDD a depth, not a document count** (`edd-is-depth-not-document-count`): the EDD package adds three things a thicker folder does not — independent verification of source of wealth/funds (a source other than the customer), named senior-management approval, and a written rationale-to-proceed — plus enhanced ongoing monitoring on a shorter refresh cadence.
4. **Screen sanctions with hygiene** (`aml-sanctions-screening-hygiene`): capture the list source + version/date, record which match logic fired, re-screen on list deltas not just at onboarding, and disposition each hit *binary* — cleared (named clearer + rationale + list version) or escalated. Keep PEP screening a separate gate; negative news is neither a clear nor an escalate.
5. **Document any no-action / reduction decision** (`aml-document-the-no-file-decision`): a cleared alert, an applied SDD reduction, or a waived EDD trigger each needs a dated, named-author basis — a reduction without a recorded basis is the same defect as no due diligence.

## Guardrails

- SDD is reduced, not no DD, and only where the regime permits it — the reduction itself needs a recorded basis.
- A PEP is enhanced controls + senior approval + ongoing monitoring, not an automatic decline; the revenue-owning relationship manager is never the sole approver.
- Real customer PII / wire details never land in a committed file (the pre-write hook flags these) — and any PII-handling change routes through `ravenclaude-core/security-reviewer`. Cite the regulator's primary source, not a summary.
