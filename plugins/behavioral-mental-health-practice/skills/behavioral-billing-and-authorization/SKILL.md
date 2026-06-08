---
name: behavioral-billing-and-authorization
description: "Navigate the behavioral health billing and authorization lifecycle: prior auth request and tracking, CPT code and units framing for common outpatient BH services, 42 CFR Part 2 vs HIPAA consent-to-disclose mechanics, denial triage, and the authorization-burn calculation. Not a substitute for a qualified biller, compliance officer, or attorney."
---

# Behavioral Billing and Authorization

**Purpose:** give the practice a structured approach to the billing and authorization mechanics
unique to behavioral health — so claims are clean, authorizations don't expire unnoticed, and
Part 2 disclosures are handled correctly.

---

## The authorization lifecycle

```
Intake → Eligibility + Auth Requirement Check → Initial Auth Submission →
Auth Granted (units + dates) → Session Tracking → Renewal Trigger →
Renewal Submission → Auth Granted or Peer-to-Peer → Exhaustion Protocol
```

**Step-by-step:**

1. **At intake:** confirm whether the payer requires a prior authorization for the service type.
   Document the auth requirement in the EHR. If auth is required, do NOT schedule the first session
   until the auth is in process (some payers retroactively cover if submitted within 3–5 business
   days; verify per payer).

2. **Initial auth submission:** typically requires DSM/ICD-10 diagnosis, treatment plan summary,
   clinical summary, CPT codes to be authorized, frequency requested, and clinician NPI + credential.
   Some payers accept electronic submission; others require a portal or fax.

3. **Auth granted — record in EHR:** auth number, authorized units, authorized dates, covered CPT
   codes, any restrictions. Calculate authorized sessions remaining using `scripts/bh_calc.py
   auth-burn`.

4. **Session tracking:** decrement authorized units with each session. Flag when units fall to 20%
   remaining (or a defined trigger — e.g., 3 sessions remaining). Do not wait until zero.

5. **Renewal submission:** submit the renewal request with the current treatment plan update,
   updated MBC scores, progress summary, and justification for continued medical necessity. Submit
   at least 10–14 business days before the current auth expires.

6. **Peer-to-peer:** if a renewal is denied on initial review, the clinician (not the biller) has
   the right to request a peer-to-peer review with the payer's medical reviewer. This is the most
   effective first-line appeal for medical-necessity denials.

7. **Authorization exhausted without renewal:** do NOT schedule sessions. Contact the patient about
   the gap and the remediation plan (out-of-pocket, delay, appeal).

---

## Authorization-burn calculation

Use `scripts/bh_calc.py auth-burn` with:
- Total authorized sessions
- Sessions used to date
- Sessions per week

Output: sessions remaining, weeks of coverage remaining, renewal trigger date.

---

## CPT code framing (outpatient behavioral health — public CPT descriptions)

> These are public CPT code descriptions. Code selection is the responsibility of the billing
> professional and the rendering clinician. This table provides framing only.

| CPT Code | Service | Time threshold |
| --- | --- | --- |
| 90791 | Psychiatric diagnostic evaluation (non-prescriber) | No strict time threshold; typically 60–90 min |
| 90792 | Psychiatric diagnostic evaluation with medical services (prescriber) | No strict time threshold |
| 90832 | Individual psychotherapy | 16–37 minutes of psychotherapy |
| 90834 | Individual psychotherapy | 38–52 minutes of psychotherapy |
| 90837 | Individual psychotherapy | 53+ minutes of psychotherapy |
| 90839 | Psychotherapy for crisis — first 60 min | First 30–74 minutes |
| 90840 | Psychotherapy for crisis — each additional 30 min | Add-on to 90839 |
| 90847 | Family psychotherapy with patient present | No strict time threshold; typically 50 min |
| 90846 | Family psychotherapy without patient present | Typically 50 min |
| 90853 | Group psychotherapy | Typically 60–90 min |
| 90785 | Interactive complexity add-on | Add to 90832, 90834, 90837, 90847, 90853 when applicable |

**Time-based billing rule:** the documented session duration drives the CPT code for 90832/90834/
90837. The documented time must match the billed code. A 50-minute session billed as 90837 (53+
min) is an overcoding error.

---

## 42 CFR Part 2 vs HIPAA — the critical distinction

| | HIPAA | 42 CFR Part 2 |
| --- | --- | --- |
| **What it covers** | Protected health information broadly | Records of patients with SUD diagnosis/treatment at a federally assisted program |
| **Consent to disclose** | Not required for TPO (treatment, payment, operations) | Specific written consent required for EVERY disclosure (with narrow exceptions) |
| **TPO carve-out** | YES — disclosure for treatment, payment, or operations without consent | NO — TPO does NOT apply to Part 2 records |
| **Re-disclosure** | Recipient can re-disclose under HIPAA | Prohibited re-disclosure; recipient bound by Part 2 |
| **Who triggers it** | Any covered entity | Any federally assisted program providing SUD diagnosis, treatment, or referral |

**Part 2 consent requirements (written, patient-specific):**

- Name/description of the program or person making the disclosure
- Name/description of the recipient
- Name of the patient
- Purpose of the disclosure
- Nature of the information to be disclosed
- Patient signature and date
- Expiration date or condition
- Statement that the patient may revoke consent

**2020 Part 2 amendment (42 CFR Part 2, final rule):** partially aligned Part 2 with HIPAA for
certain uses (e.g., research, audit) — but the specific-written-consent requirement for most
disclosures remains stricter than HIPAA. Verify current regulatory status at use [verify-at-use].

---

## Denial triage framework

| Denial category | Common root cause | First-line fix |
| --- | --- | --- |
| Medical necessity | Note lacks explicit medical-necessity statement | Escalate to `clinical-documentation-advisor`; update note + appeal |
| Authorization | Session billed without active auth, or auth for wrong CPT | Check auth record; retroactive auth if payer allows; appeal |
| Eligibility | Patient not covered on DOS (terminated coverage, wrong plan ID) | Verify eligibility for DOS; patient contact; correct claim |
| Coding error | Wrong CPT, modifier missing/incorrect, time mismatch | Review documented time vs. CPT; correct and resubmit |
| Timely filing | Claim submitted after payer's filing deadline | Appeal with proof of timely filing or accept write-off |

---

## Anti-patterns

- Scheduling sessions after authorization units are exhausted.
- Waiting for authorization renewal until zero units remain.
- Disclosing SUD records under HIPAA TPO without a Part 2-compliant consent.
- Billing 90837 when the note documents less than 53 minutes of psychotherapy.
- Submitting an authorization renewal without an updated treatment plan.

---

## Output

An authorization tracking log (per patient), a CPT code mapping for the practice's service mix,
a denial triage spreadsheet with root cause and status, and a Part 2 consent form checklist.
Reference `templates/intake-packet.md` for the consent-to-disclose form structure.
