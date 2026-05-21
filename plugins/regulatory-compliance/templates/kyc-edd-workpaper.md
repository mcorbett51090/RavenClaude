# KYC / EDD workpaper — [Customer ID]

> Standard KYC / EDD workpaper. Risk-rating logic explicit; sources cited for every verification.

**Customer ID:** [internal customer reference]
**Customer name (entity / individual):** [...]
**Workpaper version:** [v1.0 — onboarding | v1.1 — refresh | EDD trigger refresh]
**Workpaper date:** [YYYY-MM-DD]
**Preparer:** [name + role]
**Reviewer:** [name + role — must differ from preparer]
**Confidentiality:** client-confidential

---

## Section 1 — Customer identification

### For individuals

| Item | Value | Source / verification method | Document expiry |
|---|---|---|---|
| Full legal name | | [primary ID — passport / national ID] | YYYY-MM-DD |
| Date of birth | | [primary ID] | |
| Residential address | | [utility bill / bank statement < 3 months old] | |
| Nationality / citizenship(s) | | [primary ID] | |
| Tax residence + TIN | | [self-cert + corroborating] | |

### For entities

| Item | Value | Source / verification method | Document expiry |
|---|---|---|---|
| Legal name + registered name | | [certificate of incorporation / registry extract] | |
| Type / form | | [registry extract] | |
| Jurisdiction of incorporation | | [registry extract] | |
| Registered address | | [registry extract] | |
| Principal place of business | | [evidence of operations] | |
| Tax residence + TIN(s) | | [self-cert + corroborating] | |
| Date of incorporation | | [certificate] | |
| Director(s) + officer(s) | | [registry extract / board resolution] | |
| Authorized signatories | | [board resolution / signing authority document] | |

---

## Section 2 — Beneficial ownership (entities only)

Threshold: [25% per FATF — adjust to firm's documented policy]

| Beneficial owner | % Direct | % Indirect | Total % | Source of verification | PEP? | Sanctions screened? | Notes |
|---|---:|---:|---:|---|:---:|:---:|---|

**Senior managing official identification (when no individual meets the threshold):** [name + role + verification]

---

## Section 3 — Source of funds / source of wealth

### Source of funds (this engagement / account)

[Customer-declared SoF, plus independent corroboration. For higher-risk files, independent corroboration is *required*, not optional.]

- **Declared:** [customer's statement]
- **Independent corroboration:** [bank statement / sale-of-asset documentation / employment income letter / business financials]
- **Verified by:** [preparer + date]

### Source of wealth (where higher-risk EDD applies)

[Customer-declared SoW, plus independent corroboration.]

- **Declared:** [customer's statement]
- **Independent corroboration:** [tax filings / business valuation / inheritance documents / public-record asset detail]
- **Verified by:** [preparer + date]

---

## Section 4 — Sanctions, PEP, and negative-news screening

| Screening | Source list / vendor | Date run | List version | Result | Disposition | Cleared by | Cleared date | Rationale |
|---|---|---|---|---|---|---|---|---|
| Sanctions | OFAC SDN + EU + UN + UK OFSI | YYYY-MM-DD | [version] | Hit / No hit | Cleared / Escalated | [name] | YYYY-MM-DD | |
| PEP | [vendor] | YYYY-MM-DD | [version] | Hit / No hit | Cleared / Escalated | [name] | YYYY-MM-DD | |
| Negative news | [search terms + sources] | YYYY-MM-DD | n/a | Hit / No hit | Cleared / Escalated | [name] | YYYY-MM-DD | |

**Hits are cleared with documented rationale + list version, not "OK" / "No hit / similar name." Re-screening triggers: list updates, ad-hoc events, periodic refresh.**

---

## Section 5 — Risk rating

### Customer Risk Rating model inputs

| Driver | Score | Rationale |
|---|---:|---|
| Customer type / category | | |
| Product / service used | | |
| Delivery channel (in-person / remote / introducer) | | |
| Geographic risk (jurisdiction of residence + funds source + activity) | | |
| Industry / business type (entity only) | | |
| PEP status | | |
| Adverse media | | |
| Complexity (structure depth, jurisdictions) | | |

### Resulting risk tier

**Tier:** Low | Medium | High | Prohibited

**EDD applied?** Yes / No
**Senior-management approval?** [required for high risk + EDD; named approver + date]
**Refresh cadence:** [Low: 5 yrs / Medium: 2 yrs / High: 1 yr / EDD: ongoing — adjust to firm's policy]

---

## Section 6 — EDD content (high-risk only)

(Skip if not high-risk.)

- **EDD trigger:** [PEP / high-risk jurisdiction / complex structure / cash-intensive / correspondent / other]
- **Additional verification beyond CDD:**
  - [Independent source of funds verification — itemized]
  - [Site visit / customer interview record]
  - [Public-record search beyond standard]
- **Approval to proceed:** [senior management — named + date]
- **Ongoing monitoring intensity:** [thresholds / cadence beyond standard]

---

## Section 7 — Sign-off

| Role | Name | Date | Signature |
|---|---|---|---|
| Preparer | | YYYY-MM-DD | |
| Reviewer (independent) | | YYYY-MM-DD | |
| MLRO / AMLCO approval (for high-risk EDD) | | YYYY-MM-DD | |

---

## Section 8 — Refresh history

| Refresh date | Refreshed by | Reason (calendar / event-driven) | Changes from prior |
|---|---|---|---|
| YYYY-MM-DD | [name] | calendar | initial onboarding |

---

**Sources cited:** [primary IDs, registry extracts, bank statements, tax filings, screening exports, board resolutions — file paths.]
