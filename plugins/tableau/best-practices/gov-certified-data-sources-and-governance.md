# Certify a governed published data source; build workbooks on it, not on private extracts

**Status:** Pattern — a certified, published data source is the strong default governed grain; an embedded per-workbook extract is the deviation you justify.

**Domain:** Governance / data management

**Applies to:** `tableau`

---

## Why this exists

When every author embeds their own extract, you get ten copies of "Sales," ten subtly different definitions of "Net Revenue," and no single place to put RLS or fix a join. The governed alternative is a **published data source** — modeled once, with the grain, calculations, and RLS settled — that authors connect to instead of re-importing raw tables. **Certifying** it marks it as the blessed version: it sorts to the top of search, carries a certification badge, and tells authors "use this, not your own copy." This is what makes the rest of governance possible — RLS lives on the certified source once (not re-implemented per workbook), permissions are managed on one object, and "what does Net Revenue mean?" has one answer. A pile of embedded extracts has none of those properties.

## How to apply

Publish the modeled data source separately, certify it, and lock down who can certify. Authors connect to the published source.

```
# 1. Publish the data source on its own (Server/Cloud), with the model + RLS baked in.
# 2. Certify it (Site/Project Leader action) — adds the badge + search boost:
PUT /api/3.x/sites/{site-id}/datasources/{datasource-id}
{
  "datasource": {
    "isCertified": true,
    "certificationNote": "Owner: FP&A. Grain: one row per invoice line. RLS: region entitlements."
  }
}
# 3. Authors: Connect → Tableau Server → search → pick the CERTIFIED source (not raw tables).
# 4. Restrict "Certify" to Project Leaders so the badge stays meaningful.
```

**Do:**
- Publish data sources **separately** and have workbooks connect to them (not embed their own extracts).
- **Certify** the blessed source and write a certification note (owner, grain, refresh cadence, RLS).
- Put RLS / data policies on the **certified source once** so every workbook inherits them.
- Restrict who can certify (Project Leaders) so certification signals real governance, not noise.

**Don't:**
- Let "Net Revenue" be redefined in every workbook because each has its own embedded extract.
- Certify everything — if every source is certified, none is; the badge must mean something.
- Implement RLS per workbook when it belongs on the shared certified source.

## Edge cases / when the rule does NOT apply

- **One-off / exploratory analysis** — a private embedded extract is fine for a personal sandbox that will never be shared; promote it to a published source when it gets an audience.
- **Highly bespoke single-use data** — not every dataset deserves a published source; reserve certification for sources with real reuse.
- **Live-only governed connections** — a published *live* data source is still the governed object; certification applies regardless of extract-vs-live.

## See also

- [`./server-publish-with-separated-data-sources.md`](./server-publish-with-separated-data-sources.md) — the mechanics of separating data sources from workbooks
- [`./gov-rls-as-a-data-policy-not-a-hidden-filter.md`](./gov-rls-as-a-data-policy-not-a-hidden-filter.md) — RLS belongs on the certified source, once
- [`./gov-permissions-via-locked-projects-not-per-workbook.md`](./gov-permissions-via-locked-projects-not-per-workbook.md) — the content-permission half
- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — owns this rule
- Tableau Help, "Use certification to help users find trusted data" `[verify-at-build]`

## Provenance

Codifies the `tableau-admin` disciplines #4 ("Publish with separated, certified data sources") and #2 (RLS lives once on the governed source). Grounded in Tableau's published/certified data source model — re-verify the REST certification fields and badge behavior against current Tableau Help.

---

_Last reviewed: 2026-05-30 by `claude`_
