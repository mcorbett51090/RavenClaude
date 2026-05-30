# Avoid ownership and lookup skew — keep any one parent/owner under the skew threshold

**Status:** Primary diagnostic — when DML on a high-volume object is slow or row-locks, check for ownership/lookup skew first.

**Domain:** Data / LDV

**Applies to:** `salesforce`

---

## Why this exists

**Data skew** is when too many child records point at a single parent (lookup/master-detail skew) or are owned by a single user (ownership skew). Two failure modes follow. First, **sharing-recalculation cost**: when a record's owner or a parent's sharing changes, Salesforce recalculates access for every related child; a single owner or parent holding hundreds of thousands of children turns a routine ownership change into a long-running recalculation that can lock and time out. Second, **record-lock contention**: concurrent updates to children of the same skewed parent contend for a lock on the parent, producing `UNABLE_TO_LOCK_ROW` errors under load. Skew also defeats query selectivity — a filter on a lookup that resolves to a huge share of the object's rows is no longer selective. The fix is structural: distribute ownership and parentage so no single node exceeds the skew threshold (commonly cited around 10,000 children, but verify).

## How to apply

Spread children across many parents/owners. For integration or system-owned data, don't park everything on one integration user or one catch-all parent; distribute across a pool, or use a dedicated low-hierarchy owner so recalculation touches a small subtree.

```text
DO — distribute ownership and parentage
- Many child records  -> spread across many parent records (no single parent >> threshold)
- Integration-created rows -> round-robin across an owner pool, OR a user low/outside the role
  hierarchy so an owner change recalculates a SMALL sharing subtree
- Bucket "unassigned" rows across N placeholder parents, not one "Default" parent

DON'T — concentrate
- All children pointing at one "Default"/"Master" parent record  -> lookup skew
- All integration rows owned by one high-in-hierarchy integration user  -> ownership skew
  (an owner change there recalculates sharing for the whole subtree below them)
```

```apex
// DO — round-robin owner assignment during a bulk load to avoid ownership skew
Integer i = 0;
for (Lead l : newLeads) {
    l.OwnerId = ownerPool[Math.mod(i++, ownerPool.size())];  // spread, don't concentrate
}
```

**Do:**
- Keep any single parent's child count and any single owner's record count under the skew threshold.
- Distribute integration/system-created records across an owner pool or a placeholder-parent set.
- Place a high-volume integration owner **low in or outside the role hierarchy** so ownership changes recalc a small subtree.
- Diagnose `UNABLE_TO_LOCK_ROW` and slow ownership changes as skew until proven otherwise.

**Don't:**
- Funnel hundreds of thousands of children to one "Default" parent or one integration user.
- Reassign a skewed owner's records in one large transaction — that is exactly the expensive recalc.
- Assume an indexed lookup is selective when the value points at a skew parent.

## Edge cases / when the rule does NOT apply

A genuinely small object (well below the LDV/skew threshold) can concentrate freely — skew is a high-volume concern. Some designs require a real "house account" parent; mitigate with placeholder-parent bucketing or by keeping that parent's children read-mostly. The exact skew thresholds (children-per-parent, records-per-owner) and the precise recalculation cost are version-sensitive — verify against current LDV/skew guidance `[verify-at-build]`. When a large reassignment is unavoidable, combine **Defer Sharing Calculation** (`./data-defer-sharing-recalculation-on-large-loads.md`) with off-hours batching.

## See also

- [`./data-selective-soql-on-indexed-fields.md`](./data-selective-soql-on-indexed-fields.md) — why a skewed lookup defeats selectivity
- [`./data-defer-sharing-recalculation-on-large-loads.md`](./data-defer-sharing-recalculation-on-large-loads.md) — taming the recalculation cost during loads
- [`../knowledge/large-data-volume-design.md`](../knowledge/large-data-volume-design.md) — the LDV levers and sharing-recalc note
- [`../knowledge/sharing-and-security-model.md`](../knowledge/sharing-and-security-model.md) — the sharing layers recalculation walks
- [`../knowledge/integration-data-decision-trees.md`](../knowledge/integration-data-decision-trees.md) — the LDV-query and sharing-model trees

## Provenance

Extends house opinion #13 and the sharing-recalculation note in [`../knowledge/large-data-volume-design.md`](../knowledge/large-data-volume-design.md) ("Sharing recalculation at volume is expensive") and the layered model in [`../knowledge/sharing-and-security-model.md`](../knowledge/sharing-and-security-model.md). Ownership/lookup skew, the skew thresholds, and lock contention are Salesforce LDV platform behaviors; exact thresholds tagged `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
