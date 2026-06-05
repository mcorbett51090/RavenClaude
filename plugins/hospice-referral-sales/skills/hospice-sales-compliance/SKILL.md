---
name: hospice-sales-compliance
description: "Veteran playbook for hospice referral-marketing compliance — the Anti-Kickback Statute and its hospice-relevant safe harbors, Stark, the beneficiary-inducement CMP, the gift/meal nominal-value discipline, OIG hospice risk areas, truthful-marketing rules, and HIPAA for a liaison. Consulted by hospice-sales-compliance-advisor. Frames the question and names the rule and safe harbor; routes the RULING to the compliance officer / counsel."
---

# Hospice Sales Compliance Skill

**Purpose:** help `hospice-sales-compliance-advisor` frame the compliance question correctly — name the rule, flag the risk, give the safe-harbor structure — and route the **ruling** to the agency compliance officer and counsel.

## The line (applies to everything below)

**Frame the question; never issue the ruling.** The correct output is "here is the rule, here is the line, here is the safe-harbor structure, here is the question to put to your compliance officer" — not "yes, that's fine." Hospice is high-enforcement (OIG work plans, False Claims Act settlements); when in doubt, _stop and ask the compliance officer_. Every threshold here is `[example — confirm against the current rule / your compliance officer]`. (`../CLAUDE.md` §3 #2, §5, §10.)

## When to use

- Any gift, meal, sponsorship, free service, staffing, or space arrangement involving a referral source.
- Any inducement that reaches a patient/family.
- Any marketing piece or outreach message.
- Any handling of PHI.

## 1. Anti-Kickback Statute (AKS)

The federal criminal prohibition on knowingly offering/paying/soliciting/receiving **remuneration** to induce referrals of items or services payable by a federal healthcare program. **Intent-based** and broad — "remuneration" includes anything of value. Hospice referral-source relationships are squarely in scope. Safe harbors protect specific structures **only if every element is met** — see `resources/aks-safe-harbors.md`. The relevant ones for a liaison's world:

- **Personal services & management contracts** — a written agreement, ≥1-year term, aggregate compensation set in advance at fair market value, **not** determined by the volume or value of referrals.
- **Space / equipment rental** — written, ≥1-year, fair market value, not volume-based.
- **Employees** — bona fide employees are protected (this is why a hospice's own W-2 liaisons are not the AKS problem; arrangements with _outside_ sources are).

## 2. Stark (physician self-referral)

A strict-liability civil law: a physician may not refer designated health services to an entity with which the physician (or an immediate family member) has a financial relationship, unless an exception is met. Where a referral source is a **physician**, Stark applies **in addition to** AKS — and Stark has no intent requirement, so a technical violation is still a violation. Route physician arrangements to counsel.

## 3. Beneficiary-inducement CMP

Prohibits offering remuneration to a Medicare/Medicaid beneficiary that is likely to influence their choice of provider. Gifts to patients/families must fit the **nominal-value** exception (small per-item and annual caps — `[example — confirm the current CMS figures]`) and never be cash or cash-equivalents.

## 4. Gifts, meals, sponsorships (the nominal-value discipline)

"Small and infrequent" is a **documented structure**, not a feeling:

- **Non-cash, never cash or cash-equivalents** (no gift cards).
- **Within the published per-item and annual nominal-value limits** — cite them; treat any remembered figure as `[example — confirm]`.
- **Not tied to referral volume or value** in any way.
- **Documented.** An undocumented pattern of meals is a pattern, and a pattern is what OIG looks at.

## 5. Truthful marketing

No eligibility or coverage guarantee, no misleading or unsubstantiated claim, no competitor disparagement with unverified facts, no pressure on a vulnerable family. Read every piece for those four failures.

## 6. OIG hospice risk areas

The published enforcement themes that make referral-source arrangements high-scrutiny: ineligible patients / inappropriately long lengths of stay, improper financial relationships with nursing facilities and physicians, and GIP (general inpatient) misuse. These are why the default posture is caution.

## 7. HIPAA / PHI for a liaison

A liaison handles real patient data. **Minimum-necessary**, a **HIPAA-safe boundary**, and **nothing patient-identifying in a CRM note shared out, an email, an example, or a scenario.** Route any PHI question beyond minimum-necessary framing to the privacy officer.

## The output pattern

For any ask: **name the rule → locate the line → give the safe-harbor structure (if any) → state the specific question to put to the compliance officer → never green-light.** Run the `## Decision Tree: Gift / meal / arrangement anti-kickback gate` in the knowledge bank; it ends at "route to compliance officer."

## Hand-offs

- The actual ruling → the **agency compliance officer / healthcare counsel** (always).
- A revised rule / OIG advisory opinion / safe-harbor change → `ravenclaude-core` `deep-researcher`.
- PHI handling beyond framing → `ravenclaude-core` `security-reviewer` + the privacy officer.
- The eligibility accuracy a marketing piece relies on → `hospice-eligibility-criteria` skill / `hospice-eligibility-educator`.
