# EXPLAIN analysis worksheet

**Query:** <sql>

```
EXPLAIN (ANALYZE, BUFFERS) <query>;
```

| Plan node | Time | Rows (est vs actual) | Problem |
|---|---|---|---|

**Diagnosis:** seq scan / bad estimate / sort / N+1 / non-sargable
**Fix:** <right index OR sargable rewrite OR ANALYZE>
**Write-cost check:** <indexes added & their cost>
