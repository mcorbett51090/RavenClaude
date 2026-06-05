# Assign a named data steward to every data domain — governance without ownership is theater

**Status:** Absolute rule
**Domain:** Governance operating model
**Applies to:** `data-governance-privacy`

---

## Why this exists

A data governance policy that has no named owner to enforce it is a document. Policies do not approve access requests, respond to DSR exceptions, classify new columns, or remediate quality issues — stewards do. The stewardship RACI (Responsible, Accountable, Consulted, Informed) is the operational heart of a governance program. An organization that has a governance framework but no stewards will fail its first DSR deadline, its first data quality incident, and its first audit. The data steward is the governance program's load-bearing human.

## How to apply

Define stewards at the domain level, not just at the organizational level:

```markdown
## Data Stewardship RACI — [Organization Name]

| Domain | Data Steward | Backup Steward | Governance Council contact |
|---|---|---|---|
| Customer | Jane Smith (CX) | Bob Jones (CX) | CDO |
| Finance | Carol Lee (Finance) | Tom Brown (Finance) | CFO |
| Product/Analytics | Alice Chen (Eng) | Dan Kim (Eng) | CTO |
| HR/People | Grace Park (HR) | Sam Taylor (HR) | CHRO |

## Steward responsibilities

- **Classification decisions:** approves or overrides classification for new data assets in the domain
- **Access requests:** approves/denies access requests for Confidential or Restricted data in the domain
- **DSR escalations:** handles edge cases where automated DSR pipeline requires a judgment call
- **Glossary stewardship:** owns and approves business glossary terms in the domain
- **Quality incidents:** first responder for data quality issues in the domain's marts
```

**On-boarding a new steward:**
1. Add them to the governance council's distribution list.
2. Grant them the `data_steward` role in the catalog (OpenMetadata/DataHub) for their domain.
3. Train them on the classification scheme and DSR pipeline.
4. Run one DSR drill with them before their first live request.

**Do:**
- Name a specific person (not a team) as the primary steward — accountability requires a name.
- Assign backup stewards so the governance program doesn't halt when the primary is unavailable.
- Review the RACI quarterly — stewards change roles.

**Don't:**
- Name "the Analytics team" as a steward — that is not accountability.
- Allow stewardship to default to IT or engineering by vacancy — domain stewards should come from the domain.

## Edge cases / when the rule does NOT apply

- Small organizations (fewer than 20 people) may have a single cross-domain steward; document the breadth and the triage order for the single person.

## See also

- [`../agents/data-governance-architect.md`](../agents/data-governance-architect.md) — designs the governance operating model and RACI
- [`./govern-the-highest-risk-data-first.md`](./govern-the-highest-risk-data-first.md) — the risk-prioritization rule that determines which domains need stewards first

## Provenance

Standard data governance operating model practice (DAMA-DMBOK, TOGAF data governance frameworks). Codifies data-governance-privacy CLAUDE.md §2 house opinion #1 ("Classification precedes control") — the steward is the human who makes classification decisions when the automated classifier has low confidence.

---

_Last reviewed: 2026-06-05 by `claude`_
