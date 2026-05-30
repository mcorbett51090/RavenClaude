# Frame deliberately — control when Direct Lake sees new data, don't let "auto" surprise you

**Status:** Pattern — explicit, ETL-aware framing is the strong default for any model fed by a multi-step pipeline; rely on automatic updates only when freshness-on-every-commit is genuinely wanted.

**Domain:** Direct Lake / refresh / framing

**Applies to:** `microsoft-fabric`

---

## Why this exists

A Direct Lake "refresh" is **framing** — a seconds-long metadata operation that points the model at the *latest committed Delta files*. Direct Lake has a model-level **automatic-update** setting that is **on by default**, so any OneLake commit can become visible to the report immediately. That's great for a single-writer table — and a hazard for a multi-step pipeline. If bronze→silver→gold loads commit at different times, an auto-update mid-pipeline can frame the model against a **half-loaded gold table**: facts updated, dimensions not yet, and the report shows inconsistent numbers for the minutes until the next commit. Framing exists precisely to give the model owner **point-in-time control** over what's loaded; using it deliberately is how you avoid showing transient ETL state to users.

## How to apply

Decide who triggers framing, and turn off automatic updates when an ETL job should own the moment of visibility.

```text
Single-writer / streaming-ish table, freshness wanted ASAP   → leave automatic updates ON.
Multi-step pipeline (bronze→silver→gold), consistency wanted → automatic updates OFF;
   the LAST pipeline step reframes the model once all tables are committed.
```

- **Reframe as the final pipeline step** — after every gold table is committed, trigger a programmatic refresh (XMLA `processFull` / semantic-model refresh API / `fab`) so the model flips to the new consistent state atomically.
- **Disable automatic updates** on models fed by orchestrated ELT so an in-flight commit can't frame against partial data.
- **Remember framing ≠ data copy** — it's cheap; the expensive part is the upstream load. Schedule framing to ride *after* the load, not during it.

**Do:**
- Make the final ELT step reframe the model; treat framing as the publish step.
- Turn automatic updates **off** for pipeline-fed models that need cross-table consistency.
- Keep automatic updates **on** for genuinely append-only / near-real-time single tables.

**Don't:**
- Leave automatic updates on for a multi-step pipeline and then wonder why the report briefly shows mismatched facts/dimensions.
- Confuse framing with an Import refresh — there's no data copy and no heavy CPU; it's metadata.

## Edge cases / when the rule does NOT apply

- **A single append-only table** (or a streaming-shaped lakehouse table) where "show me the latest commit immediately" is the requirement — leave auto-update on.
- **On-OneLake after a shortcut's underlying data changes** — you may need a **manual reframe** regardless of the auto setting; auto-update doesn't always catch upstream shortcut changes.
- **Import mode** doesn't frame — this is Direct-Lake-only.

## See also

- [`directlake-stay-under-guardrails.md`](./directlake-stay-under-guardrails.md) — framing fails if the table exceeds guardrails
- [`lakehouse-nondestructive-merge-for-framing.md`](./lakehouse-nondestructive-merge-for-framing.md) — how the write pattern affects what framing reloads
- [`pipeline-orchestrate-idempotent-watermarks.md`](./pipeline-orchestrate-idempotent-watermarks.md) — the pipeline whose last step should reframe
- [`../agents/fabric-semantic-model-engineer.md`](../agents/fabric-semantic-model-engineer.md)

## Provenance

Grounded in [How Direct Lake works — Framing & Automatic updates](https://learn.microsoft.com/fabric/fundamentals/direct-lake-how-it-works) ("Framing provides model owners with point-in-time control over what data is loaded"; "automatic update … enabled by default … disable when you want to control data changes by framing"; "framing can help you provide consistent query results in environments where data in Delta tables is transient … long-running ETL") and [Refresh Direct Lake semantic models](https://learn.microsoft.com/fabric/fundamentals/direct-lake-manage) — Microsoft Learn, retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
