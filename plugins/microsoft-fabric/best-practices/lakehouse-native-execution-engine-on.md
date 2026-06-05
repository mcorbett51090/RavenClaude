# Enable the Native Execution Engine — the biggest free Spark performance win

**Status:** Absolute rule
**Domain:** Spark / Lakehouse performance
**Applies to:** `microsoft-fabric`

---

## Why this exists

Fabric Spark Runtime 1.3 and 2.0 include the **Native Execution Engine (NEE)** — a vectorized, columnar C++ engine that runs Spark SQL operations outside the JVM and typically cuts CPU time and shuffle by 30–70% on compatible workloads. It is enabled by default on Runtime 1.3+ but can be accidentally disabled by sessions that set `spark.ms.autotune.enabled=true` (autotune is the deprecated Runtime 1.2 path, and the two are mutually exclusive). Recommending autotune or leaving it in a notebook config block is a documented anti-pattern — it silently falls back to the slower JVM path and wastes CU budget.

## How to apply

In every notebook or Spark Job Definition, confirm NEE is active:

```python
# Verify NEE is active
print(spark.conf.get("spark.ms.nativeExecutionEngine.enabled", "default"))
# Should print "true" on Runtime 1.3 / 2.0

# Remove or invert any autotune setting if present
# spark.conf.set("spark.ms.autotune.enabled", "false")  # DO NOT enable autotune
```

For Spark Job Definitions that set Spark config, add to the SparkConf block:
```
spark.ms.nativeExecutionEngine.enabled = true
spark.ms.autotune.enabled = false
```

**Do:**
- Pin the Fabric Runtime to 1.3 or 2.0 in workspace settings — this guarantees NEE is available and removes the autotune footgun from the menu.
- Confirm NEE is active on the first run of any new notebook environment by checking `spark.conf.get`.
- Test I/O-bound workloads (large Delta scans, wide aggregations, shuffle-heavy joins) for NEE improvement — these see the largest gains.

**Don't:**
- Set `spark.ms.autotune.enabled = true` — it reverts to the Runtime 1.2 JVM path and negates NEE.
- Assume NEE is active when a notebook was copied from a Runtime 1.2 workspace — copy-paste preserves the config block, which may re-enable autotune.
- Treat NEE as a silver bullet: UDFs (Python/Scala lambdas) and non-SQL operators fall back to JVM; minimize UDF use to maximize NEE coverage.

## Edge cases / when the rule does NOT apply

Python UDF-heavy workloads (e.g., custom NLP models applied row-by-row) cannot use NEE for the UDF execution itself. However, NEE still accelerates the surrounding SQL/scan/shuffle layers — keep it enabled even in these workloads.

## See also

- [`../agents/lakehouse-engineer.md`](../agents/lakehouse-engineer.md) — owns notebook performance optimization
- [`./lakehouse-vorder-only-where-it-pays.md`](./lakehouse-vorder-only-where-it-pays.md) — the complementary write-time optimization

## Provenance

Codifies CLAUDE.md house opinion #11 ("Native Execution Engine on by default — the biggest free Spark perf/cost win; autotune is the dead Runtime-1.2 path"); Microsoft Learn Fabric Runtime 1.3 release notes.

---

_Last reviewed: 2026-06-05 by `claude`_
