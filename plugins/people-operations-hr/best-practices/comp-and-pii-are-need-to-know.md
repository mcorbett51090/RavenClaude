# Comp and PII are need-to-know

**Status:** Absolute rule
**Domain:** Data handling / confidentiality
**Applies to:** `people-operations-hr`

---

## Why this exists

Salary data, performance ratings, medical information, immigration status, and any individually
identifiable people data are among the most sensitive data a company holds. Mishandling them:

- Violates employee privacy and trust — typically irreversibly.
- Creates legal exposure under HIPAA (medical), GDPR/CCPA (personal data), state wage-
  confidentiality statutes, and employment law (retaliation protections for pay discussion).
- Can constitute an unfair labor practice if used to suppress legitimate pay discussion.
- Undermines the integrity of the comp and performance systems if employees learn that salary
  or rating data was shared beyond the intended audience.

"Need-to-know" is not a bureaucratic formality — it is the minimum distribution that enables
the work to get done without exposing individuals to harm.

## How to apply

**Classification for common people data:**

| Data type | Minimum audience | How to handle |
|-----------|-----------------|---------------|
| Individual salary / comp ratio | HR, direct manager, finance (budget roll-up) | Never in shared docs; encrypted at rest; not in Slack/Teams channels; not in email unless encrypted |
| Performance rating | HR, direct manager (before calibration); add skip-level after calibration is finalized | Not in shared Sheets; not forwarded; rating delivery is verbal first |
| Aggregate pay equity data | HR leadership, C-suite, board (compensation committee) | Aggregate only; no individual row visible unless essential for remediation |
| Medical / leave data | HR only (in jurisdictions that separate from manager notification) | Strictly need-to-know; never in performance records |
| SSN / TIN / government ID | Payroll/HR compliance only | Never in Markdown, text files, or shared docs; encrypted in HRIS |
| Offer letter comp figures | Recruiting, HM, Finance, and the candidate | Not shared with panel; not discussed in the full debrief |

**Do:**

- Store comp data in the HRIS with role-based access controls — not in shared Google Sheets
  with org-wide read access.
- Deliver performance ratings verbally before any written artifact is distributed.
- Anonymize or aggregate before sharing any people analytics report with n < 5 in a cell.
- Audit who has access to comp and performance data at least annually.
- Scrub all PII (name, email, ID, salary, rating) from any artifact before it leaves the
  intended audience (training material, external sharing, documentation).

**Don't:**

- Paste a salary figure into a Slack message, a shared doc, or a prompt to an AI assistant
  without explicit acknowledgment that the audience controls are in place.
- Include employee-level performance ratings in a management-meeting deck shared widely.
- Allow a hiring manager to access other employees' comp data "to benchmark" — they get the
  band, not the individual figures.
- Commit SSNs, salaries, or individual performance ratings to a code repository or a shared
  file store without encryption and access controls.

## Edge cases / when the rule does NOT apply

Pay transparency between employees about their own compensation (discussing salary with a
colleague) is protected by the National Labor Relations Act in the US — employees have the
right to discuss their own pay. This rule governs how *the company and its agents* handle
and distribute comp data, not employee-to-employee discussion.

## See also

- [`./people-analytics-measures-the-system-never-punishes-the-individual.md`](./people-analytics-measures-the-system-never-punishes-the-individual.md) — the analytics complement.
- [`./set-comp-bands-before-offers-not-after.md`](./set-comp-bands-before-offers-not-after.md) — comp transparency in the offer process.
- `ravenclaude-core/security-reviewer` — escalation point for HRIS integration and PII data-flow questions.

## Provenance

Reflects GDPR Article 5 (data minimization / purpose limitation), CCPA/CPRA, HIPAA (for
medical data), and the US NLRA Section 7 (employee pay discussion protection). The need-to-know
principle is a standard information-security access-control practice applied to HR data.

---

_Last reviewed: 2026-06-08 by `claude`._
