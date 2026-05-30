# Archive cold rows to keep the hot object small — tier data before it becomes an LDV fire

**Status:** Pattern — strong default for any object whose row count grows unbounded over time; deviate only when every row stays operationally hot.

**Domain:** Data / LDV

**Applies to:** `salesforce`

---

## Why this exists

Selectivity, indexes, and skinny tables all fight the symptom; archival fights the cause. The query optimizer's selectivity thresholds are a **percentage of total rows on the object**, so the more rows the object holds, the harder every query has to work to stay selective — and sharing recalculation, storage cost, and full-copy sandbox time all scale with the row count too. Most high-growth objects (cases, events, logs, transactions) have a small **hot** working set and a large **cold** tail that is rarely read and never edited. **Data tiering** moves the cold tail off the hot object — into **Big Objects** (Salesforce-native, billions of rows, queried async via `Async SOQL`/Bulk), external storage, or an archival system — keeping the hot object small enough that ordinary selective queries stay fast. Designing tiering in from day one (house opinion #13) is far cheaper than retrofitting it once the object is already a non-selective-query fire.

## How to apply

Define a hotness boundary (a date/status cutoff), move rows past it to the cold tier on a schedule, and point operational queries at the small hot object while analytical access reads the cold tier.

```text
Tiering design:
1. Define HOT vs COLD: e.g. Cases closed > 18 months ago, or Events older than 2 years
2. Hot tier  -> the standard object, kept small -> ordinary selective SOQL stays fast
3. Cold tier -> Big Object (native, async SOQL/Bulk) | external store | archive system
4. Move on a schedule (Batch Apex / Bulk API), off-hours, then delete from the hot object
5. Operational queries hit the hot object; reporting/audit reads the cold tier
```

```apex
// DO — scheduled Batch Apex moves cold rows to a Big Object, then deletes from the hot object
public class ArchiveOldCases implements Database.Batchable<SObject> {
    public Database.QueryLocator start(Database.BatchableContext bc) {
        return Database.getQueryLocator([
            SELECT Id, CaseNumber, Subject, ClosedDate
            FROM Case
            WHERE Status = 'Closed' AND ClosedDate < :archiveCutoff   // selective, indexed
        ]);
    }
    public void execute(Database.BatchableContext bc, List<Case> scope) {
        List<Case_Archive__b> archived = new List<Case_Archive__b>();   // __b = Big Object
        for (Case c : scope) archived.add(toArchive(c));
        Database.insertImmediate(archived);   // Big Object write
        delete scope;                          // shrink the hot object
    }
    public void finish(Database.BatchableContext bc) { /* chain next slice */ }
}
```

**Do:**
- Define a hotness boundary and move cold rows off the standard object on a schedule.
- Use **Big Objects** for native, high-scale cold storage queried via Async SOQL / Bulk.
- Keep operational queries on the small hot object; route audit/analytics to the cold tier.
- Design tiering in **from day one** for unbounded-growth objects, not as a retrofit.

**Don't:**
- Let a high-growth object accumulate indefinitely and lean only on indexes to keep queries selective.
- Query a Big Object like a standard object — it has restricted query semantics (Async SOQL / Bulk), not arbitrary SOQL.
- Archive rows that are still operationally hot — define the boundary by real access patterns.

## Edge cases / when the rule does NOT apply

If every row stays operationally hot (no cold tail), archival has nothing to move — tune the hot object with selectivity and skinny tables instead. Big Objects have restricted query and indexing semantics (a defined composite index, async query) that don't fit every reporting need; sometimes an external warehouse (`azure-cloud/*`) is the better cold tier. Regulatory retention may forbid deleting rows even when cold — then the cold tier must itself be durable and auditable. Big Object query/index semantics and limits are version-sensitive — verify against current guidance `[verify-at-build]`. Large archival deletes are **high-blast** — wrap in the data-loader runbook.

## See also

- [`./data-selective-soql-on-indexed-fields.md`](./data-selective-soql-on-indexed-fields.md) — why a smaller object keeps queries selective
- [`./data-skinny-tables-and-custom-indexes.md`](./data-skinny-tables-and-custom-indexes.md) — tuning the hot object that remains
- [`./data-batch-apex-for-large-result-sets.md`](./data-batch-apex-for-large-result-sets.md) — the engine that moves the cold rows
- [`../knowledge/large-data-volume-design.md`](../knowledge/large-data-volume-design.md) — "Archival / data tiering — move cold rows out (Big Objects, external storage)"
- [`../skills/data-loader-runbook/SKILL.md`](../skills/data-loader-runbook/SKILL.md) — the reversible procedure wrapping the archival delete

## Provenance

Codifies the archival/data-tiering lever from [`../knowledge/large-data-volume-design.md`](../knowledge/large-data-volume-design.md) ("Archival / data tiering — move cold rows out (Big Objects, external storage) to keep the hot object small") and house opinion #13. Big Object semantics, Async SOQL, and storage limits are Salesforce platform features; exact numbers tagged `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
