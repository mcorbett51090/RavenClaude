# Choose choice vs lookup vs customer column by who owns the value list and whether you need polymorphism

**Status:** Pattern — strong default; deviate only with a written reason recorded on the column.

**Domain:** Dataverse / Data modeling

**Applies to:** `power-platform`

---

## Why this exists

Choice, lookup, and customer columns all "pick one value from a set," so they get used interchangeably — and the wrong pick is expensive to undo because **column data type is permanent** (you must create a new column, migrate, re-point every reference, and delete the old one). A **choice** hard-codes its option list in metadata: users can't add options at runtime, the list can't be sorted, options carry no extra attributes, and deleting an in-use option leaves records showing a raw numeric ID. A **lookup** points at a real table, so the value list is *data* (sortable, user-maintainable, can carry related columns) at the cost of a relationship and a join. A **customer** column is a polymorphic lookup to Account ∪ Contact — powerful when you genuinely don't know which type a row references, and needless complexity when only one type is ever populated. Picking by habit instead of by these axes produces tables you can't refactor cheaply.

## How to apply

Decide on two axes: **who owns/maintains the value list**, and **do you need polymorphism**.

```text
Need to reference Account OR Contact, type unknown at design time?  → CUSTOMER column
List is short, fixed, owned by makers, no extra attributes per item? → CHOICE (local option set)
Same enumeration genuinely shared across ≥2 tables?                  → CHOICE (global option set)
List changes at runtime / is long (50+) / needs sorting / needs      → LOOKUP to a custom table
   extra columns per item / users self-manage it?
```

```json
// CHOICE (local) — short fixed list owned by makers. Prefer LOCAL over global.
{
  "@odata.type": "Microsoft.Dynamics.CRM.PicklistAttributeMetadata",
  "SchemaName": "cnt_Priority",
  "OptionSet": { "IsGlobal": false, "OptionSetType": "Picklist",
    "Options": [ { "Value": 100000000, "Label": { "LocalizedLabels": [{ "Label": "Low",  "LanguageCode": 1033 }] } } ] }
}

// LOOKUP — value list is DATA in a table (sortable, user-maintainable, carries attributes).
// Created as the Lookup on a 1:N relationship (cnt_category 1:N cnt_project).
{ "cnt_category@odata.bind": "/cnt_categories(<guid>)" }   // logical name, lowercase

// CUSTOMER — polymorphic Account ∪ Contact. Use ONLY when both types are genuinely possible.
{ "cnt_payer_account@odata.bind": "/accounts(<guid>)" }    // OR /contacts(<guid>) on the same column
```

| Need | Use | Why |
|---|---|---|
| Short, fixed, maker-owned list; no per-item attributes | **Choice (local)** | Cheapest; no join; but list is metadata, not user-editable |
| The **same** enumeration shared across ≥2 tables | **Choice (global)** | One definition to maintain — but global sets are harder to refactor, so only when truly shared |
| Long list, frequent changes, sorting, per-item attributes, users self-manage | **Lookup** | The value list becomes a queryable table with views and columns |
| Reference may be **Account or Contact**, unknown at design | **Customer** | One column instead of two mutually-exclusive lookups |
| User may pick **several** values | **Multi-select choice** | But can't be used in rollups, calculated/formula columns, or classic workflows |

**Do:**
- Prefer a **local** option set over global unless the enumeration is genuinely shared by multiple tables — global sets are harder to refactor.
- Reach for a **lookup to a custom table** the moment the list needs sorting, runtime additions, per-item attributes, or grows past ~50 items.
- Use **customer** only when both Account and Contact are realistically populated. If only Contact is ever used in practice, use a plain Contact lookup.
- Bind lookups with the **lowercase logical name** in `@odata.bind` — PascalCase causes a silent 400.

**Don't:**
- Model a frequently-changing or user-managed list as a choice — you'll be editing metadata (and re-publishing) on every change, and you can't sort it.
- Delete an in-use choice option — records then render the raw numeric ID, with no warning. Query usage first.
- Use a customer column when only one target type is ever populated — two clear lookups beat one ambiguous polymorphic one.
- Put a **multi-select choice** anywhere you later need a rollup, calculated/formula column, or classic-workflow condition — it's unsupported there (max 150 options too).

## Edge cases / when the rule does NOT apply

- **Boolean (Yes/No)** is its own type — don't model a two-value choice as a Picklist when a `BooleanAttributeMetadata` is clearer and supports a default.
- **Status/Status Reason** (`statecode`/`statuscode`) are system choice columns with special lifecycle semantics — don't reinvent them as custom choices for record state.
- A choice is the right call even for a longish list when it's **truly static and maker-governed** (e.g. ISO country codes) and sorting/attributes aren't needed — the cost of a lookup join isn't always justified.
- A **global** option set is correct (over local) precisely when refactor-resistance is a feature, not a bug — e.g. a regulated status enumeration that *must* stay identical across tables.

## See also

- [`../skills/dataverse-web-api/resources/columns-attributes.md`](../skills/dataverse-web-api/resources/columns-attributes.md) — local vs global choice payloads, the `@odata.bind` lowercase-logical-name rule, multi-select limits
- [`../skills/dataverse-web-api/resources/dataverse-design-rules.md`](../skills/dataverse-web-api/resources/dataverse-design-rules.md) — "When to Use Lookup Instead of Choice"; choice-deletion + no-sort gotchas; column-type permanence
- [`../skills/dataverse-web-api/resources/relationships.md`](../skills/dataverse-web-api/resources/relationships.md) — polymorphic `Targets` / customer-lookup mechanics
- [`../knowledge/dataverse-decision-trees.md`](../knowledge/dataverse-decision-trees.md) — `## Decision Tree: Data modeling — choice vs lookup vs customer column`
- [`../agents/dataverse-architect.md`](../agents/dataverse-architect.md) — owner; "prefer local over global"; "Customer only when you genuinely need polymorphism"

## Provenance

Grounded in `skills/dataverse-web-api/resources/dataverse-design-rules.md` ("When to Use Lookup Instead of Choice"; choice-deletion-shows-numeric-ID; choices-cannot-be-sorted; column-type permanence), `resources/columns-attributes.md` (local vs global option set, multi-select limitations, `@odata.bind` casing), and the `dataverse-architect` opinions ("Choice columns: prefer local over global"; "Customer column only when you genuinely need polymorphism").

---

_Last reviewed: 2026-05-30 by `claude`_
