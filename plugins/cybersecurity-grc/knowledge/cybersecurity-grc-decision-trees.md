# Cybersecurity GRC — Decision Trees

_Decision trees + a dated framework/reference map. Framework rows are `[verify-at-build]` — re-check the current edition of each framework before quoting control text or counts to a consumer. Last reviewed: 2026-06-08._

Traverse the relevant tree before choosing a framework, committing to a report type, assessing a vendor, scoping the audit boundary, or treating a risk. Five trees: which-framework-first, Type I vs Type II, vendor-assessment-depth, audit-boundary scoping, and risk-treatment selection.

## Decision Tree: Which framework do we pursue first?

Right-size the framework to the org's size, risk, and who's actually asking — not to ambition.

```mermaid
graph TD
  A[Need a security-compliance program] --> B{Is a customer/contract demanding a specific attestation?}
  B -- Yes, US B2B SaaS buyers asking --> C[SOC 2 Type II - the common North-American B2B ask]
  B -- Yes, global/enterprise/EU buyers asking --> D[ISO 27001 - the international certifiable ISMS standard]
  B -- No named demand --> E{Selling to US federal / handling federal data?}
  E -- Yes --> F[NIST 800-53 / FedRAMP baseline - the control catalogue the contract requires]
  E -- No --> G[Adopt NIST CSF 2.0 as the org-wide language; defer certification until demand or risk warrants it]
  C --> H{Also need ISO later?}
  D --> H
  H -- Yes --> I[Pick one primary, crosswalk the other to it - map once, attest many]
```

_Don't cargo-cult a heavyweight framework. SOC 2 for B2B SaaS, ISO 27001 for global/enterprise, NIST CSF as the language, full 800-53 only when the contract/risk demands it._

## Decision Tree: Type I vs Type II (am I ready to be audited)?

A report is only as good as the evidence window behind it.

```mermaid
graph TD
  A[Auditor asks Type I or Type II] --> B{Have the controls actually been operating?}
  B -- No, just designed/written --> C[Not ready - design state only; close the design-to-operating gap first]
  B -- Yes, but <observation period --> D{Need a report NOW for a deal?}
  D -- Yes --> E[Type I - point-in-time design opinion; commit to Type II next cycle]
  D -- No --> F[Wait - run the controls through the full observation period, then Type II]
  B -- Yes, full observation period with evidence --> G{Any control with no evidence / known exceptions?}
  G -- Yes --> H[Remediate or scope it out before fieldwork - it becomes an exception otherwise]
  G -- No --> I[Type II - operating-effectiveness over the period; the stronger report]
```

_Type I is a point-in-time design opinion; Type II proves the controls operated across a period. Don't chase the report date past the evidence window._

## Decision Tree: How deeply do I assess this vendor?

Third-party risk is your risk — but assess proportionally, not uniformly. Tier by what the vendor holds, then match the assessment depth to the tier.

```mermaid
graph TD
  A[New or renewing vendor] --> B{Does it hold/process production customer data or PII?}
  B -- Yes --> C{Production access or a critical dependency?}
  C -- Yes --> D[Tier 1 - critical: full SIG/CAIQ + a real read of the SOC 2/ISO scope, period, exceptions, CUECs]
  C -- No --> E[Tier 2 - moderate: SIG-Lite + the vendor's current attestation + CUEC mapping]
  B -- No --> F{Any access to internal systems or non-public data?}
  F -- Yes --> E
  F -- No --> G[Tier 3 - low: lightweight attestation on file; re-confirm at renewal]
  D --> H{Clean opinion but exceptions in YOUR critical control area?}
  H -- Yes --> I[Not assurance - treat the exception as a residual risk you own + implement your CUECs]
  H -- No --> J[Rely + monitor; map every CUEC to a control you evidence; set a tier-driven re-assessment cadence]
  E --> J
```

_Tier by data + access + criticality. A filed PDF is not an assessment; the exceptions page and the CUECs matter more than the opinion page. Re-assess on a tier-driven cadence, not once at onboarding._

## Decision Tree: Is this in the audit boundary?

Scope is the highest-leverage decision — what's in the boundary drives cost, effort, and risk more than any control choice. Scope to what you can attest honestly, then expand.

```mermaid
graph TD
  A[A system / location / team / data store] --> B{Does it store, process, or transmit in-scope customer data, OR support a control that does?}
  B -- No --> C[Out of scope - document the carve-out + the boundary that keeps it out]
  B -- Yes --> D{Can you actually evidence its controls over the observation period?}
  D -- No --> E{Can you stand up collectible evidence at the source before the clock starts?}
  E -- Yes --> F[In scope - wire evidence at the source first, then start the window]
  E -- No --> G[Carve it out for THIS cycle with a documented boundary; bring it in next cycle]
  D -- Yes --> H{Is it segmented from out-of-scope systems by a defensible boundary?}
  H -- Yes --> I[In scope - attestable; include it]
  H -- No --> J[Either segment it or expand scope to include what it touches - no half-boundaries]
```

_A boundary an auditor can't trace isn't a boundary. Scope down to the attestable, carve out the rest with a documented justification, and never claim a boundary you can't defend (no half-segmentation)._

## Decision Tree: How do I treat this risk?

Risk drives controls, not the reverse. Once a risk is scored (likelihood × impact), every risk gets exactly one of four treatment decisions — and an owner.

```mermaid
graph TD
  A[A scored risk inherent likelihood x impact] --> B{Is the residual after available controls within appetite?}
  B -- Yes --> C[Accept - document the residual + a named owner + sign-off; an un-owned acceptance is an ignored risk]
  B -- No --> D{Can a control reduce likelihood or impact cost-effectively?}
  D -- Yes --> E[Mitigate - add/strengthen a control; re-score residual; the delta is what the control bought]
  D -- No --> F{Can the loss be shifted to a third party - insurance or contract?}
  F -- Yes --> G[Transfer - insure/contract it; you still own the residual the transfer does not cover]
  F -- No --> H{Is the activity itself optional?}
  H -- Yes --> I[Avoid - stop the activity; the cleanest treatment when the value does not justify the risk]
  H -- No --> J[Accept with escalation - explicit senior sign-off; the residual is a known, owned exposure]
```

_Mitigate / accept / transfer / avoid — one decision per risk, each with an owner. Transfer and acceptance still leave a residual you own. Re-score residual after any mitigation so the control's value is visible._

## Capability / framework map (2026, `[verify-at-build]`)

| Item | What it is | Notes |
|---|---|---|
| SOC 2 (AICPA) | Attestation against the Trust Services Criteria (Security + optional Availability, Confidentiality, Processing Integrity, Privacy) | Type I = design at a point in time; Type II = operating effectiveness over a period `[verify-at-build]` |
| ISO/IEC 27001 | Certifiable ISMS standard; controls in Annex A | Annex A control count/structure changed in the 2022 revision — confirm the current edition `[verify-at-build]` |
| NIST CSF 2.0 | Risk-management framework; Functions: Govern, Identify, Protect, Detect, Respond, Recover | CSF 2.0 added the Govern function — verify the current function set `[verify-at-build]` |
| NIST SP 800-53 | Control catalogue (control families, baselines low/moderate/high) | Heavyweight; right-size — full catalogue rarely fits a small SaaS `[verify-at-build]` |
| Crosswalk | One primary framework, others mapped to it | NIST publishes informative references / mappings; a control evidenced once can attest many `[verify-at-build]` |
| Statement of Applicability (SoA) | ISO 27001 artifact: which controls apply + justification + status | Every exclusion needs an auditor-defensible reason traced to the risk register `[verify-at-build]` |
| Risk register | Assets, threats, likelihood × impact, treatment, residual risk | Risk drives controls; ISO 27005 / NIST 800-30 are common methodologies `[verify-at-build]` |
| SIG (Shared Assessments) | Standardized vendor-risk questionnaire (full + SIG-Lite/Core) | Use depth proportional to the vendor's tier `[verify-at-build]` |
| CAIQ (CSA) | Cloud-vendor assessment questionnaire mapped to the Cloud Controls Matrix | For cloud/SaaS vendors; pairs with the vendor's SOC 2/ISO `[verify-at-build]` |
| Vendor SOC 2 reliance | Read scope, period, exceptions, qualified opinions, and the CUECs you must run | A clean opinion with exceptions in your critical area is not assurance `[verify-at-build]` |
| Vendor tiering | Tier by data sensitivity + access + criticality; assessment depth follows the tier | Tier 1 = full SIG/CAIQ + SOC 2 read; Tier 3 = light attestation on file `[verify-at-build]` |
| Residual risk | Inherent risk after the treating control's effectiveness is applied | Transfer/acceptance still leave a residual you own; re-score after any mitigation `[verify-at-build]` |
| Type II observation period | The window the controls must demonstrably operate across, with unbroken evidence | Common windows are 3–12 months; back-filled evidence for a past period is not evidence `[verify-at-build]` |

**Runnable check:** [`../scripts/grc_calc.py`](../scripts/grc_calc.py) turns three of these rows into arithmetic — `risk-score` (likelihood × impact → inherent + residual band), `control-coverage` (% of applicable controls with evidence), and `audit-readiness` (Type II observation-period coverage). It is decision-support, not a verdict; the attestation/acceptance call routes to `grc-architect` + sign-off.

_Treatment options for a risk: mitigate (add/strengthen a control), accept (document + own the residual), transfer (insurance/contract), avoid (stop the activity). Likelihood × impact scoring drives prioritization. Re-verify any framework edition, control count, or questionnaire version before quoting it to a consumer._
