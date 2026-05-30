# Defer sharing recalculation during large loads — don't pay the recalc cost per row

**Status:** Pattern — strong default for any large ownership/role/sharing-affecting load; deviate only when the load is small or sharing-neutral.

**Domain:** Data / Sharing

**Applies to:** `salesforce`

---

## Why this exists

Every time a record is inserted, an owner changes, a role moves, or a sharing rule is added, Salesforce **recalculates sharing** — it walks the OWD → role-hierarchy → sharing-rule → manual/Apex-managed layers and rewrites the share rows that grant access. During a large data load this recalculation fires **per affected record**, and on a high-volume object it dominates the load time and can trigger row-lock contention. The platform provides **Defer Sharing Calculation**: an admin suspends automatic recalculation for the load window, runs the load, then resumes — at which point Salesforce recalculates **once, in bulk**, far more efficiently than per-row. Skipping this on a multi-hundred-thousand-row load is how an overnight migration runs past the maintenance window. It pairs with the skew rules: deferral tames the recalc cost, distributing ownership keeps any single recalc subtree small.

## How to apply

For any large load that touches ownership, role assignment, or sharing-affecting fields: enable Defer Sharing Calculation, run the load (ideally with non-essential automation paused per the runbook), then resume and let the single bulk recalculation run off-hours.

```text
Load sequence for a large, sharing-affecting load:
1. Sandbox-first: validate counts + side effects (triggers, Flows, sharing recalc)
2. Back up the target (and cascade-affected children)
3. Setup -> Defer Sharing Calculation -> SUSPEND group membership / sharing rule recalc
4. Run the Bulk API 2.0 load (skills/bulk-rest-api-client), batched, off-hours
5. RESUME sharing calculation -> one bulk recalc instead of per-row
6. Verify access is correct; re-enable any paused automation
```

```text
DON'T — large ownership reassignment with recalculation live
- Reassign 500k records' OwnerId in one live run
  -> per-record sharing recalc + lock contention -> blows the window, risks UNABLE_TO_LOCK_ROW
```

**Do:**
- Suspend sharing recalculation **before** a large ownership/role/sharing-rule-affecting load; resume after.
- Wrap the deferral in the data-loader runbook (sandbox-first, backup, verify) — deferral changes *who can see what* during the window.
- Run the load and the resumed recalculation **off-hours**, and reconcile access afterward.
- Combine with ownership-skew avoidance so each recalc subtree stays small.

**Don't:**
- Run a large sharing-affecting load with recalculation live and hope the window holds.
- Forget to **resume** recalculation — access stays stale until you do.
- Defer recalculation in production without confirming the access gap during the window is acceptable.

## Edge cases / when the rule does NOT apply

A small load, or a load on a Private-OWD object with no hierarchy/rules to recalculate, gets little benefit — the recalc is cheap. Deferral is an **admin/Setup** action with org-wide effect; during the window, access reflects the pre-load state, so it's unsuitable if users must see the new access immediately mid-load. Some sharing recalculations (e.g., certain rule edits) are themselves long-running and are better scheduled directly. Defer Sharing Calculation availability, scope, and exact behavior are version-sensitive — verify against current sharing/LDV guidance `[verify-at-build]`. This is a **high-blast** production action — confirm with the human (per the data-loader runbook).

## See also

- [`../skills/data-loader-runbook/SKILL.md`](../skills/data-loader-runbook/SKILL.md) — the runbook step "disable noise deliberately" that this implements
- [`./data-avoid-ownership-and-lookup-skew.md`](./data-avoid-ownership-and-lookup-skew.md) — keeping each recalc subtree small
- [`../knowledge/large-data-volume-design.md`](../knowledge/large-data-volume-design.md) — "Defer Sharing Calculation during large loads"
- [`../knowledge/sharing-and-security-model.md`](../knowledge/sharing-and-security-model.md) — the layers recalculation walks
- [`../knowledge/integration-data-decision-trees.md`](../knowledge/integration-data-decision-trees.md) — the data-load-tool and sharing-model trees

## Provenance

Codifies the deferral lever from [`../knowledge/large-data-volume-design.md`](../knowledge/large-data-volume-design.md) ("Sharing recalculation at volume is expensive — defer with Defer Sharing Calculation during large loads") and the runbook step 4 in [`../skills/data-loader-runbook/SKILL.md`](../skills/data-loader-runbook/SKILL.md). Defer Sharing Calculation is a Salesforce Setup feature; exact scope/behavior tagged `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
