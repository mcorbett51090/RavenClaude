# Don't put Cascade-All (delete/share/assign) on a relationship to a high-volume child table

**Status:** Pattern — strong default; deviate only with a written reason recorded on the relationship.

**Domain:** Dataverse / Data modeling

**Applies to:** `power-platform`

---

## Why this exists

A relationship's `CascadeConfiguration` decides what happens to child rows when the parent is deleted, shared, assigned, or reparented. `Cascade` means "do it to every child too." On a relationship pointing at a high-volume child table, a single innocuous parent operation becomes a mass operation across thousands of rows inside one transaction: a parent delete turns into a multi-second cascade delete that holds locks and can time out; a parent share fans out to every child and inflates the POA (Principal Object Access) table; a reassign rewrites ownership on the whole subtree. The setting looks harmless at design time and becomes an incident under production data volume. Cascade behavior is also baked into the relationship — changing it later on a populated table is itself a risky operation.

## How to apply

Choose the cascade behavior per operation deliberately. The safe default for a high-volume child is `RemoveLink` (or `Restrict`) on Delete and `NoCascade` on Share/Assign:

```json
// 1:N: account (parent) -> cnt_telemetryevent (high-volume child)
// Deleting an account must NOT trigger a mass-delete of millions of telemetry rows.
"CascadeConfiguration": {
  "Delete":   "RemoveLink",   // clear the lookup, keep the children (or "Restrict" to block the delete)
  "Share":    "NoCascade",    // don't fan share grants across every child row
  "Assign":   "NoCascade",    // don't rewrite ownership on the whole subtree
  "Reparent": "NoCascade",
  "Merge":    "Cascade",      // merge is parent-scoped and low-frequency; usually fine
  "Unshare":  "NoCascade",
  "RollupView": "NoCascade"
}
```

| Behavior | On Delete | Use when |
|---|---|---|
| `Cascade` | Deletes every child | Low-volume, truly-owned children that have no meaning without the parent (e.g. order → order lines, bounded) |
| `RemoveLink` | Clears the child lookup, keeps the row | High-volume children that should survive the parent (logs, telemetry, transactions) |
| `Restrict` | **Blocks** the parent delete while children exist | You want a human to deal with the children first (referential integrity guard) |
| `Active` | Cascades only to active children | Large child set where soft-deleted rows shouldn't be touched |
| `NoCascade` | Nothing | Default for Share/Assign on high-volume children |

**Do:**
- Default to `RemoveLink` or `Restrict` on Delete for any child table you expect to grow past a few thousand rows per parent.
- Set Share/Assign/Reparent to `NoCascade` on high-volume children — cascade sharing explodes the POA table and is a notorious performance sink.
- Decide cascade behavior at **design time**, while the table is empty — it's far cheaper to change then.

**Don't:**
- Leave `Cascade` on Delete for a parental relationship to an operational/transactional child "because it's the default-looking option." A single parent delete then becomes a mass delete inside one transaction.
- Use `Cascade` on Share for any table where a parent can be shared broadly — every share multiplies across all children.

## Edge cases / when the rule does NOT apply

- **Bounded, truly-dependent children** (an order with ≤ a few dozen lines; a survey with its questions) are fine with `Cascade` on Delete — the child genuinely has no standalone meaning and the row count per parent is small and capped.
- **N:N relationships have no `CascadeConfiguration`** — records are peers, so this rule doesn't apply; the associative concern there is whether you should have used a manual junction table instead (see the `dataverse-architect` opinion on native N:N).
- `Restrict` is the *stricter* choice and can frustrate users who legitimately need to delete a parent — pair it with a documented cleanup path or a flow that archives children first.

## See also

- [`../skills/dataverse-web-api/resources/relationships.md`](../skills/dataverse-web-api/resources/relationships.md) — full `CascadeConfiguration` matrix and the 1:N create payload
- [`../knowledge/dataverse-decision-trees.md`](../knowledge/dataverse-decision-trees.md) — `## Decision Tree: Data modeling — cascade behavior on a 1:N relationship`
- [`./dataverse-rollup-vs-calculated-vs-plugin.md`](./dataverse-rollup-vs-calculated-vs-plugin.md) — for parent aggregates that a cascade was being abused to maintain
- [`../agents/dataverse-architect.md`](../agents/dataverse-architect.md) — owner; flags "Cascade All on a parental relationship to a high-volume child table"

## Provenance

Grounded in `skills/dataverse-web-api/resources/relationships.md` (the cascade-behavior table and `CascadeConfiguration` options) and the `dataverse-architect` agent's anti-pattern list ("Cascade All on a parental relationship to a high-volume child table — a single delete becomes a multi-second mass delete and a locked transaction"). POA/share-fan-out behavior marked as the platform mechanism the rule guards against.

---

_Last reviewed: 2026-05-30 by `claude`_
