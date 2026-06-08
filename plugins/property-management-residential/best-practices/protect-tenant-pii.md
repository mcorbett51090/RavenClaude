# Protect tenant PII

**Status:** Absolute rule
**Domain:** Data privacy / risk management
**Applies to:** `property-management-residential`

---

## Why this exists

Residential leasing generates concentrated, high-value personally identifiable information: Social
Security numbers, full date of birth, income documents (pay stubs, tax returns, bank statements),
employer information, credit and background reports, and payment details. A data breach or careless
handling of this information creates regulatory, reputational, and civil liability for the property
manager and the owner.

The FTC Safeguards Rule (16 C.F.R. Part 314) applies to businesses — including property management
companies — that receive consumer financial information (credit reports, income verification) as
part of a covered application process. State data breach notification laws apply in every
jurisdiction. The Fair Credit Reporting Act governs the handling and disposal of consumer report
information.

The simplest protection: PII stays in the PM software. It is not emailed in plaintext, not pasted
into chat, not stored on personal phones or paper files outside the secure system.

## How to apply

- Collect SSNs, income documents, and authorization-to-pull forms through the PM software's
  integrated application portal (AppFolio, Buildium, Yardi, RentSpree) — not via email attachments.
- Do not email SSNs, full credit reports, background reports, or income documents. If a document
  must be transmitted, use the PM software's secure messaging or a documented secure file-transfer
  tool.
- Store all tenant PII in the PM software's tenant record, not in local drives, chat threads, or
  email folders.
- Dispose of physical copies (printouts of applications, reports) per FCRA disposal requirements —
  shred before discarding.
- Limit access to tenant PII to staff with a need to access it (leasing agents see applications;
  maintenance coordinators do not need SSNs).
- Retain consumer reports and PII per FCRA's retention requirements; dispose after the retention
  period following the end of tenancy.

**Do:**

- Use the PM software's application portal for all PII collection and storage.
- Apply role-based access controls in the PM software so PII is accessible only to authorized roles.
- Audit who has accessed sensitive records in the PM software when a dispute arises.
- Train leasing staff on PII handling at onboarding and annually.

**Don't:**

- Email a credit report, background report, SSN, or income document as an attachment.
- Paste a Social Security number or full date of birth into a chat message, email, or notes field
  visible to unauthorized users.
- Store a copy of an application on a personal phone or a shared drive without access controls.
- Print and retain paper copies of applications or reports beyond operational necessity.

## Edge cases / when the rule does NOT apply

This rule has no exception for convenience. The PM software is the secure system of record; there
is no legitimate operational reason to handle PII outside it. When a resident insists on submitting
documents via email, instruct them to use the portal; if the portal is unavailable, use a
documented secure file-transfer tool and move the document to the PM software immediately.

## See also

- [`./document-everything-in-the-tenant-file.md`](./document-everything-in-the-tenant-file.md)
- [`./screen-every-applicant-by-the-same-criteria.md`](./screen-every-applicant-by-the-same-criteria.md)
- `ravenclaude-core/security-reviewer` — escalate any potential PII breach or exposure to this agent

## Provenance

Grounded in the Fair Credit Reporting Act (15 U.S.C. §1681 et seq.), the FTC Safeguards Rule
(16 C.F.R. Part 314), and state data breach notification laws. Not legal advice — verify
applicable federal and state requirements with qualified counsel, especially for PM companies
operating in multiple states.

---

_Last reviewed: 2026-06-08 by `claude`._
