# Data-platform best-practice docs

Named, citable rules for the `data-platform` plugin's four-layer dashboard engagements (DB / ELT / dashboard / embed) and the `ravenclaude-core/security-reviewer` it routes auth work through. Each file is one rule — read, applied, and cited as a whole. Grounded in this plugin's `knowledge/` briefs and security-critical skills; the cross-marketplace index lives in [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md).

---

## Index

| Doc | Status | Use when |
|---|---|---|
| [`enforce-tenant-isolation-closest-to-data.md`](./enforce-tenant-isolation-closest-to-data.md) | Absolute rule | Designing tenant isolation on any multi-tenant stack — pick the closest-to-data enforcement layer and ship a denial test |
| [`issue-short-lived-jwts-for-embeds.md`](./issue-short-lived-jwts-for-embeds.md) | Absolute rule | Writing or reviewing any embed-auth flow — server-issued, 5-15 min, signed `tenant_id` claim |

---

## See also

- [`../knowledge/multi-tenant-rls-patterns.md`](../knowledge/multi-tenant-rls-patterns.md) — the security-critical reference both rules distill
- [`../CLAUDE.md`](../CLAUDE.md) — the team constitution (house opinions §3, anti-patterns §4, hooks §7)
- [`../../../docs/best-practices/_TEMPLATE.md`](../../../docs/best-practices/_TEMPLATE.md) — the section shape every doc here follows
