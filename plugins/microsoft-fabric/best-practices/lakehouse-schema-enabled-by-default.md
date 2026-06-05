# Enable schema-aware lakehouses by default for namespace hygiene and OneLake security preview

**Status:** Absolute rule
**Domain:** Lakehouse / OneLake governance
**Applies to:** `microsoft-fabric`

---

## Why this exists

Fabric lakehouses created before mid-2024 used a flat namespace: every table lived directly under `Tables/`. Schema-enabled lakehouses add a namespace layer (`Tables/<schema>/<table>`), which is required for the OneLake-security **data preview** feature to work and is the foundation for any meaningful table organization beyond a handful of tables. Disabling schemas means all future tables pile into one flat namespace — a maintenance problem that grows with the medallion — and the OneLake security data-preview capability (which shows row/column previews in the Fabric portal, filtered by the viewer's access) becomes unavailable.

## How to apply

When creating a new lakehouse via the Fabric portal or `fab` CLI, enable the schema option at creation time (it cannot be changed after creation on an existing lakehouse without migration):

```python
# Via Fabric REST API (Python example)
import requests
body = {
  "displayName": "my_lakehouse",
  "type": "Lakehouse",
  "definition": {
    "parts": [{
      "path": "lakehouse.metadata.json",
      "payload": '{"defaultSchema":"dbo","schemaEnabled":true}',
      "payloadType": "InlineBase64"
    }]
  }
}
requests.post(f"{FABRIC_API}/workspaces/{WS_ID}/items", json=body, headers=headers)
```

Schema layout:
- `raw` — bronze landing zone
- `curated` — silver cleaned layer
- `gold` — business-ready, Direct Lake-ready

**Do:**
- Name schemas to match the medallion layer (`raw`, `curated`, `gold`) or the business domain (`sales`, `finance`, `hr`).
- Keep schema names lower-snake-case — schema names are case-sensitive in the SQL endpoint.
- On existing flat lakehouses being migrated, move tables in batches and update all downstream notebook paths before cutting over.

**Don't:**
- Create schemas ad-hoc in the SQL endpoint (`CREATE SCHEMA`) without also creating the matching folder in OneLake — they must be in sync.
- Use schema names longer than 128 characters — the SQL engine's limit is lower than the OneLake folder-name limit.
- Treat schema names as security boundaries — they are namespace organization; OneLake security (workspace roles, RLS/CLS) is the data plane.

## Edge cases / when the rule does NOT apply

A lakehouse used purely for Eventstream landing (streaming bronze) and immediately succeeded by a transformation notebook may remain flat if it is never accessed via the SQL endpoint and schema-enabled preview is not needed.

## See also

- [`../agents/lakehouse-engineer.md`](../agents/lakehouse-engineer.md) — owns lakehouse creation and table organization
- [`./workspace-domain-governance-boundary.md`](./workspace-domain-governance-boundary.md) — the security-plane model this rule supports

## Provenance

Codifies CLAUDE.md house opinion #14 ("schema-enabled lakehouses by default"); aligned with the OneLake security data-preview prerequisite from Microsoft Learn Fabric 2026 documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
