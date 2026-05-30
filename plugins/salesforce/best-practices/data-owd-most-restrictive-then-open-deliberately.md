# Set OWD to the most restrictive default that still works — then open access deliberately

**Status:** Pattern — strong default; widening the org-wide default is a one-way door at scale, so start closed and justify every loosening.

**Domain:** Data / Sharing

**Applies to:** `salesforce`

---

## Why this exists

Org-wide defaults (OWD) set the **floor** of record visibility; the role hierarchy, sharing rules, and manual/Apex-managed shares only ever *open it up* from there. The order matters because the layers are additive and asymmetric: you can always grant more access on top of a restrictive OWD with a precise sharing rule, but you cannot claw back access that a permissive OWD already granted org-wide without a disruptive tightening that breaks every report and integration assuming the looser default. And the choice is a **data-model decision, not a config afterthought** — master-detail children *inherit* the parent's sharing while lookup children do not, so OWD and object relationships are designed together. Starting OWD Public Read/Write "to make it work" and tightening later is the expensive reversal; starting Private and opening with rules is the cheap, auditable path. (This is the design-time complement to the runtime `with sharing` / CRUD-FLS rule — see See also.)

## How to apply

Start each object's OWD at the most restrictive setting that still lets the business function (usually Private), then layer access in the documented order: hierarchy for manager rollup, sharing rules for groups/criteria, manual/Apex-managed for cases rules can't express.

```text
OWD-first sharing design (most restrictive that works, then open):
1. OWD = Private (the floor)            -> nobody but owner + hierarchy sees the record
2. Need managers to see reports' rows?  -> Grant Access Using Hierarchies
3. Share to a group/role?               -> owner-based sharing rule
4. Share by record attributes?          -> criteria-based sharing rule
5. Rules can't express it?              -> manual share or Apex managed sharing
Relationship choice is part of this:
   master-detail child INHERITS parent sharing | lookup child does NOT
```

```text
DO   -> Account OWD = Private; criteria-based rule opens "Industry = Public Sector" to the Gov team
DON'T-> Account OWD = Public Read/Write "for now"; tighten later
        -> the tightening breaks every report, list view, and integration built on the open default
```

**Do:**
- Start OWD at the most restrictive value that still works, then open up with the narrowest rule that grants the needed access.
- Design OWD **with** the object relationships — master-detail inherits sharing, lookup doesn't.
- Prefer a precise sharing rule over loosening the OWD for the whole object.
- Document why each loosening exists, so a future tightening knows what it would break.

**Don't:**
- Default to Public Read/Write to avoid thinking about sharing — that floor is hard to raise later.
- Use the role hierarchy as a sharing mechanism for peers — it grants *upward* visibility, not lateral.
- Treat OWD as a late config toggle — it's a structural, expensive-to-reverse decision.

## Edge cases / when the rule does NOT apply

Genuinely public reference data (a price book, a public knowledge object) legitimately starts at Public Read Only — restrictiveness that blocks the business is not a virtue. Some objects' OWD is constrained by their parent (master-detail children take the parent's OWD; you can't set theirs independently). External-user (Experience Cloud) sharing has its own external OWD layer that must be reasoned about separately. The **security verdict** — "is this sharing design actually secure?" — is owned by `ravenclaude-core/security-reviewer`, not this plugin; this rule is the design default, not the certification.

## See also

- [`./enforce-sharing-and-crud-fls.md`](./enforce-sharing-and-crud-fls.md) — the runtime complement (`with sharing` + CRUD/FLS in code)
- [`./data-defer-sharing-recalculation-on-large-loads.md`](./data-defer-sharing-recalculation-on-large-loads.md) — the recalculation cost of opening/changing access at volume
- [`./data-avoid-ownership-and-lookup-skew.md`](./data-avoid-ownership-and-lookup-skew.md) — how skew makes recalculation of these layers expensive
- [`../knowledge/sharing-and-security-model.md`](../knowledge/sharing-and-security-model.md) — the OWD → hierarchy → rule layering and the access decision tree
- [`../knowledge/integration-data-decision-trees.md`](../knowledge/integration-data-decision-trees.md) — the sharing-model decision tree
- [`../agents/salesforce-platform-architect.md`](../agents/salesforce-platform-architect.md) — owns the sharing-model design

## Provenance

Codifies the "start most-restrictive, open deliberately" guidance from [`../knowledge/sharing-and-security-model.md`](../knowledge/sharing-and-security-model.md) and the platform architect's house opinion ("the org-wide default should be the most restrictive thing that still works"). The master-detail-inherits / lookup-doesn't distinction is from the same knowledge doc. The security verdict escalates to `ravenclaude-core/security-reviewer` per the plugin constitution.

---

_Last reviewed: 2026-05-30 by `claude`_
