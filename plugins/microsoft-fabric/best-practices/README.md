# Microsoft Fabric best-practice docs

Named, citable rules for Microsoft Fabric engagements — each file is one rule, grounded in this plugin's own [`knowledge/`](../knowledge/) bank and enforced by its [`agents/`](../agents/). Read and apply a doc as a whole.

For the cross-tool rule format and the marketplace-wide index, see [`docs/best-practices/_TEMPLATE.md`](../../../docs/best-practices/_TEMPLATE.md) and [`docs/best-practices/README.md`](../../../docs/best-practices/README.md). For the plugin's house opinions and anti-patterns these rules sit inside, see [`../CLAUDE.md`](../CLAUDE.md) §3–§4.

---

## Index

| Doc | Status | Use when |
|---|---|---|
| [`one-copy-shortcut-before-copying.md`](./one-copy-shortcut-before-copying.md) | Pattern | Deciding how data gets into Fabric — reach for a shortcut before copying; never call Mirroring "free" without the query-billed caveat |
| [`name-your-direct-lake-mode.md`](./name-your-direct-lake-mode.md) | Absolute rule | Designing or diagnosing any Direct Lake semantic model — name on-OneLake vs on-SQL before anything else; the fallback behavior depends on it |
| [`shape-gold-for-direct-lake.md`](./shape-gold-for-direct-lake.md) | Absolute rule | Building medallion gold tables a Direct Lake model or the SQL endpoint reads — V-Order + file/row-group targets on gold, never serve bronze |

---

## See also

- [`../knowledge/`](../knowledge/) — the citation-grounded reference docs (decision trees + per-topic guides) these rules are extracted from
- [`../CLAUDE.md`](../CLAUDE.md) — the Microsoft Fabric team constitution (house opinions §3, anti-patterns §4, the seams §10)
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — the marketplace-wide best-practice index and format
