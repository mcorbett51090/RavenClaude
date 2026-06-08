# Protect client PII and account data

**Status:** Absolute rule
**Domain:** Data privacy, advisory compliance, information security
**Applies to:** `wealth-management-advisory`

---

## Why this exists

Financial advisors are custodians of extraordinarily sensitive data: Social Security numbers,
account numbers and balances, beneficiary designations, health information (relevant to insurance
and LTC planning), tax returns, estate documents, and in some cases business-ownership structures
that are material non-public information. A breach of this data — whether through an insecure
document, an email with an unmasked attachment, or a code-committed file — is simultaneously a
privacy violation, a regulatory failure, and a client-trust catastrophe from which most practices
do not recover.

The SEC's Regulation S-P (Safeguards Rule, amended 2023 [verify-at-use]) requires RIAs to adopt
written policies and procedures to protect customer information. The FTC Safeguards Rule imposes
comparable requirements on financial institutions. FINRA Rule 4370 governs business continuity
planning including data security.

Beyond the regulatory requirements, a client who learns that their SSN or account number was
exposed — even accidentally — will likely leave. Client data protection is a practice survival
matter, not just a compliance checkbox.

## How to apply

**Do:**

- Strip or mask PII (Social Security numbers, account numbers, date of birth + full name combined,
  beneficiary names + relationship + SSN) before using any client data as an example in a planning
  tool, a template, or any shared document.
- Use client initials or a pseudonym (e.g., "the Garcias") rather than full names in any document
  that may be shared beyond the immediate advisory relationship.
- Store client documents in the firm's designated secure system (custodian vault, secure CRM, or
  encrypted document management system) — not in email attachments, unencrypted desktop folders,
  or shared drives without access controls.
- Route any workflow that involves storing, transmitting, or processing client-identifying data to
  `ravenclaude-core/security-reviewer` for a data-handling review.
- Apply a confidentiality classification to every planning document: internal only (advisor eyes),
  client-shared (sent to client), or privileged (attorney/accountant coordination).

**Don't:**

- Commit client-identifying data (SSN, account numbers, full financial details tied to a named
  individual) to a code repository, a planning template file, or any version-controlled document.
- Email unencrypted account statements, tax returns, or beneficiary designations without a secure
  file transfer mechanism.
- Include real client names and account details in examples, templates, or tool inputs that may be
  logged, cached, or reviewed outside the secure advisory relationship.
- Use client data as training examples or demonstrations without explicit de-identification.

## Edge cases / when the rule does NOT apply

- Documents transmitted through the custodian's secure client portal (which has its own encryption
  and access controls) follow the custodian's data-handling standards — but the advisor is still
  responsible for what they put into those documents before uploading.
- Publicly available information about a client (e.g., their name as an officer of a public company
  in SEC filings) is not protected PII in the same way as account numbers — but combining public
  data with financial account details creates a sensitive composite that should be treated as PII.
- Attorney-client privileged communication has its own confidentiality standard — coordinate
  with the firm's legal counsel on what information can be shared with an estate attorney or CPA
  in the context of multi-advisor planning.

## See also

- [`./suitability-and-reg-bi-clear-before-any-recommendation.md`](./suitability-and-reg-bi-clear-before-any-recommendation.md) — general compliance standards
- `ravenclaude-core/security-reviewer` — for data-handling design and PII security controls
- Reg S-P (SEC) and FTC Safeguards Rule [verify-at-use for current amendment status]

## Provenance

Codifies requirements under SEC Regulation S-P (Safeguards Rule, as amended), FTC Safeguards Rule
(16 CFR Part 314), GLBA Title V, and FINRA Rule 4370. State privacy laws (e.g., CCPA for California
clients) may impose additional requirements [verify-at-use]. Consult the firm's compliance officer
and legal counsel for firm-specific and jurisdiction-specific policies. Not legal advice.

---

_Last reviewed: 2026-06-08 by `claude`._
