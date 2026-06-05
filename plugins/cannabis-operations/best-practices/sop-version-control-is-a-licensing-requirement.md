# Treat SOP version control as a licensing requirement, not documentation hygiene

**Status:** Absolute rule
**Domain:** Cannabis operations / compliance / SOPs
**Applies to:** `cannabis-operations`

---

## Why this exists

Cannabis regulators in most states require that Standard Operating Procedures be maintained, accessible to employees, and current — and they inspect the version history during audits. An undated, unversioned, or superseded SOP that staff are actually following is a compliance deficiency finding: it signals that the operator's documented processes diverged from operations, which is the basis for a license suspension or revocation in aggravated cases. Version control is not the same thing as bureaucratic thoroughness; it is the evidentiary chain that proves the operator has been operating as represented.

## How to apply

Every SOP must carry a version header before it is distributed to staff:

```
SOP:         [name]
Version:     [1.0 | 1.1 | 2.0 ...]
Effective:   [YYYY-MM-DD]
Supersedes:  [prior version or "initial"]
Owner:       [title, not personal name — roles turn over]
Approved by: [title] on [YYYY-MM-DD]
```

Maintain the archive of superseded versions with at least the same retention window the state requires for track-and-trace records (typically 3–7 years; confirm state-specifically).

**Do:**
- Bump the version number and effective date on every substantive change — even a one-line correction.
- Attach the SOP version in use to any corrective-action record — regulators will ask "what SOP governed this when it happened?"
- Train staff on new versions before the effective date, with sign-off dated on or before the effective date.
- Keep superseded versions in a read-only archive, not deleted — inspectors ask for the prior version.

**Don't:**
- Edit a live SOP in place without bumping the version — undocumented mid-document edits are harder to defend than a clean supersession.
- Distribute only the current version to staff; the archive must be locatable by the compliance lead within minutes of an audit opening.
- Use personal names as SOP owners — ownership should survive turnover without triggering a revision.

## Edge cases / when the rule does NOT apply

- Informal internal checklists (shift prep, opening/closing tasks) that are not submitted to the state are lower-stakes, but adopting the same discipline prevents them from being confused with regulated SOPs.
- Some states accept a general-operations manual rather than individual SOPs — the same version-control discipline applies; it just travels as a document set.

## See also

- [`../agents/seed-to-sale-compliance-specialist.md`](../agents/seed-to-sale-compliance-specialist.md) — SOP authoring and audit-readiness are this specialist's core lane.
- [`./seed-to-sale-traceability-is-the-license-reconcile-it-daily.md`](./seed-to-sale-traceability-is-the-license-reconcile-it-daily.md) — traceability SOPs are the most inspector-scrutinized class.

## Provenance

Standard cannabis compliance practice distilled from multi-state licensing requirements and audit observation. Marked `[unverified — training knowledge]`; validate specific retention periods and SOP requirements against the operator's state license conditions.

---

_Last reviewed: 2026-06-05 by `claude`_
