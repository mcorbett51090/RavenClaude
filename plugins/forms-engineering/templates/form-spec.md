# Form spec — `<form name>`

**Owner:** `<named person, not a role>` · **Date:** `<YYYY-MM-DD>` · **Status:** draft / agreed / live

One form, one spec. Produced by [`../skills/form-intake-and-triage-design/SKILL.md`](../skills/form-intake-and-triage-design/SKILL.md), with §4 filled by [`../skills/harden-a-form-submission/SKILL.md`](../skills/harden-a-form-submission/SKILL.md) and §5 by [`../skills/form-telemetry-and-control/SKILL.md`](../skills/form-telemetry-and-control/SKILL.md).

---

## 1. What this form is the entry point to

| | |
| --- | --- |
| **The process behind it** | `<what happens after submit, in one sentence>` |
| **Who acts on a submission** | `<team or named queue>` |
| **What a submission is worth** | `<why this form exists at all>` |
| **What happens if it goes down** | `<the fallback channel, or "none — say so">` |

## 2. Request taxonomy and routing

| Request type | Predicate | Destination | Clock starts | Target | Escalation trigger |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

- **"Other" share, last period:** `<%>` — the health metric for this taxonomy.
- **A type with no routing row is a defect**, not a default.

## 3. Fields

One row per field. A field with nothing in the "who uses the answer" column does not ship.

| Field | Type | Required for which types | Who uses the answer | Client constraint | Server constraint (authoritative) | Personal data? | Retention |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |

⛔ **Validation parity is a property of this table**: every client constraint has a server constraint on the same row, and the server's is authoritative. A blank server cell is a finding.

## 4. Trust boundary

| Control | Decision | Fail direction | Signal emitted when degraded |
| --- | --- | --- | --- |
| Anti-forgery | | | |
| Duplicate guard | | | |
| Rate limit | | | |
| Honeypot | | | |
| Challenge widget | | | |
| Attachment handling | | | |
| Outbound webhook verification | | | |

- **Fail direction is ruled per route, in writing.** Both directions are legitimate; an unstated one is not. See [`../best-practices/degraded-bot-defense-must-be-loud.md`](../best-practices/degraded-bot-defense-must-be-loud.md).
- **Attachment handling is owned upstream** — [`../../ravenclaude-core/rules/security.md`](../../ravenclaude-core/rules/security.md) §File handling. Record the decision here; do not restate the rule.
- **Challenge-widget mechanics are owned upstream** — [`../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md`](../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md).

### 4b. Deliberately not defended

| What | Why it is acceptable here | Who accepted it |
| --- | --- | --- |
| | | |

⛔ **The binding verdict on this section is not this document's.** Route it to [`../../ravenclaude-core/agents/security-reviewer.md`](../../ravenclaude-core/agents/security-reviewer.md) — zero-exception.

## 5. Measurement

| | |
| --- | --- |
| **Denominator** | `<written so a second analyst implements it identically>` |
| **Completion** | `<numerator> / <the denominator above>` |
| **Abandonment** | `1 − completion`, same denominator |
| **Defect classes counted** | validation / delivery / triage — `<which, and their operational definitions>` |
| **Events instrumented** | |
| **What would falsify the expected improvement** | |

Full plan: [`./form-telemetry-plan.md`](./form-telemetry-plan.md).

## 6. Accessibility

The audit and every criterion-level verdict belong to [`../../web-design/agents/accessibility-auditor.md`](../../web-design/agents/accessibility-auditor.md). Record here only the three journey-level questions a single-page audit cannot answer — see [`../best-practices/wcag-2-2-added-five-criteria-that-land-on-forms.md`](../best-practices/wcag-2-2-added-five-criteria-that-land-on-forms.md):

- **Redundant entry:** anything asked twice across the whole process? `<yes/no + where>`
- **Sign-in in front of the form:** paste allowed, password manager works, no cognitive test as the only route? `<yes/no>`
- **Consistent help:** the route to a human in the same relative place on every step? `<yes/no>`

## 7. Open questions and unverified claims

| Claim | Marker | The step that settles it |
| --- | --- | --- |
| | `[unverified — <reason>]` | |
