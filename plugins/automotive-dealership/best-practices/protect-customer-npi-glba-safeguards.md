# Protect customer NPI — GLBA Safeguards Rule

**Status:** Absolute rule
**Domain:** Dealership compliance, data security
**Applies to:** `automotive-dealership`

---

## Why this exists

A franchise automotive dealership is a "financial institution" under the Gramm-Leach-
Bliley Act (GLBA) because it regularly extends credit (arranges financing) and collects
non-public personal information (NPI) from customers in connection with those financial
transactions. The FTC's Safeguards Rule (16 CFR Part 314, amended effective June 2023
[verify-at-use]) requires dealerships to implement a written information security program
(WISP) that protects the NPI they collect — SSNs, credit applications, income and
employment information, insurance data, account and routing numbers.

A breach is not a hypothetical risk. Dealerships are high-value targets: they hold SSNs,
income data, and credit-application information on hundreds or thousands of customers, and
many have historically handled this data with inadequate controls (plaintext email, shared
drives, paper forms in unlocked storage). The 2023 amendments added explicit requirements
for multi-factor authentication on systems that hold NPI, encryption of NPI in transit and
at rest, and a designated qualified individual. Violations can result in FTC enforcement,
state AG action, and individual consumer claims.

## How to apply

Treat customer NPI as the most sensitive data class in the store. Assume it is regulated,
assume it is targeted, and assume the default is never adequate.

**Do:**

- Designate a specific qualified individual responsible for the information security program
  (a named person, not a committee).
- Conduct and document an annual risk assessment identifying NPI risks and controls.
- Encrypt NPI at rest (credit applications, deal jackets, DMS customer records) and in
  transit (email transmission of credit applications must use encrypted channels).
- Require multi-factor authentication (MFA) for any system that accesses financial NPI.
- Implement need-to-know access controls: only staff who need NPI for their role should
  have access.
- Have written contracts with all service providers (DMS vendors, credit-app processors,
  F&I product providers) that require appropriate security standards.
- Define and document a retention and disposal policy: how long NPI is kept and how it is
  securely destroyed (shredding for paper, certified digital deletion for electronic records).
- Implement an incident-response plan: what to do if a breach is suspected, who is
  notified, what is reported to regulators and customers, and in what timeframe.

**Don't:**

- Email credit applications in plaintext — this is the single most common NPI-handling
  failure at dealerships.
- Store credit applications in shared drives without access controls or encryption.
- Use a paper-based process for NPI without locked storage and a documented disposal
  procedure (shredder policy, locked destruction bin).
- Leave the designation of "qualified individual" to a job title without a named person.
- Accept "we use a reputable DMS" as a substitute for a written service-provider security
  agreement.
- Conduct OFAC checks without documenting the result — the check must be auditable.

## Edge cases / when the rule does NOT apply

The GLBA Safeguards Rule applies to NPI collected from customers in connection with
financial product offerings. Customer contact information collected only for marketing
(not a credit transaction) is still subject to general data privacy principles but may
not trigger all Safeguards Rule obligations — consult counsel on the boundary. The rule
applies to dealerships regardless of size; there is no small-dealer exemption.

## See also

- [`./fni-must-clear-compliance-no-payment-packing.md`](./fni-must-clear-compliance-no-payment-packing.md)
- [`../agents/dealership-compliance-advisor.md`](../agents/dealership-compliance-advisor.md)
- [`../knowledge/automotive-dealership-decision-trees.md`](../knowledge/automotive-dealership-decision-trees.md)
  (F&I compliance tree)

## Provenance

FTC Safeguards Rule, 16 CFR Part 314 (amended 2023 effective date [verify-at-use]);
GLBA Title V; FTC enforcement actions against financial institutions including dealerships;
NADA compliance resources; National Automobile Dealers Association legal counsel guidance.
Specific amendment effective dates and threshold requirements should be verified against
current FTC regulatory text before implementing.

---

_Last reviewed: 2026-06-08 by `claude`._
