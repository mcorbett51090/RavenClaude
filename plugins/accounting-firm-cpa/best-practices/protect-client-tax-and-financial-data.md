# Protect Client Tax and Financial Data

**Status:** Absolute rule
**Domain:** US public-accounting / CPA-firm operations
**Applies to:** accounting-firm-cpa

## Why this exists

CPA firms hold some of the most sensitive personal and business data that exists: Social Security
Numbers, Employer Identification Numbers, bank account numbers, income figures, K-1 detail,
financial statements, and payroll data. This data is a target for identity theft, tax fraud,
and business espionage. A firm that mishandles it faces civil liability, regulatory sanction
(FTC Safeguards Rule requires a written information security program for tax preparers),
professional discipline, and irreversible reputational damage.

The risk is elevated because the same data passes through multiple channels: client portals,
email, shared drives, tax software, CAS platforms, and physical documents. Each channel is a
potential leak. The discipline of protecting client data must be designed into every workflow —
not bolted on after a breach.

## How to apply

**Do:**
- Use a secure client portal (not unencrypted email) for all document exchange containing
  SSNs, EINs, financial statements, or other sensitive data.
- Encrypt files containing PII before transmitting by any channel. Tax software exports,
  workpaper packages, and financial statement drafts should never be sent as unencrypted
  email attachments.
- Retain client data only as long as required by the firm's document-retention policy
  (typically 7 years for tax records, per IRS guidance `[verify-at-use]`). Dispose of data
  securely (shredding physical, certified deletion for digital).
- Limit access to client data to staff assigned to the engagement. A firm-wide shared drive
  with open access to all client files is a data-exposure event waiting to happen.
- Train staff to recognize phishing attempts targeting tax professionals (IRS warns of
  spear-phishing seasons coinciding with busy season `[verify-at-use]`).
- Maintain a written information security program (WISP) as required by the FTC Safeguards
  Rule for tax preparers. Review annually `[verify-at-use]`.
- When providing examples, scenarios, or AI-assisted analysis: scrub all real SSNs, EINs,
  bank account numbers, and named client figures before including them in any prompt, shared
  document, or tool output.

**Don't:**
- Send tax returns, financial statements, or K-1s as unencrypted email attachments — ever.
- Store SSNs or EINs in plaintext in workpapers, spreadsheets, or notes that are not
  encrypted or access-controlled.
- Use real client data in training examples, onboarding demonstrations, or AI prompts.
- Share client data with third-party tools (including AI assistants) without reviewing the
  tool's data-use and retention policies.
- Leave physical tax returns, workpapers, or client documents unsecured after business hours.
- Rely on "it's internal" as a substitute for access controls — insider threats and accidental
  disclosure are more common than external breaches in professional services.

## Edge cases / when the rule does NOT apply

- **Aggregated / anonymized data:** data that has been genuinely anonymized (no SSN, EIN,
  client name, or unique identifying combination) may be used for firm analytics, training,
  or benchmarking. Ensure the anonymization is complete — partial scrubbing leaves re-
  identification risk.
- **Authorized disclosures:** with a valid client authorization (e.g., Form 8821 or 2848 for
  IRS matters, or a written consent for lender/investor disclosures), sharing specific client
  data with the authorized recipient is appropriate. Document the authorization in the file.

## See also

- `hooks/check-accounting-firm-cpa-anti-patterns.sh` — flags plaintext SSN/EIN patterns
- IRS Publication 4557 (Safeguarding Taxpayer Data) `[verify-at-use]`
- FTC Safeguards Rule (16 CFR Part 314) — written information security program for tax
  preparers `[verify-at-use]`
- AICPA Privacy Management Framework `[verify-at-use]`

## Provenance

FTC Safeguards Rule (16 CFR Part 314) and IRS guidance (Pub 4557, IR-2016-143 and successors)
set legal and professional requirements. The operational prescriptions reflect standard data-
security practice in professional services.

_Last reviewed: 2026-06-08 by `claude`._
