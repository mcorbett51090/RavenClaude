# Parameterize all connection strings and OneLake paths in pipelines — never hard-code stage-specific values

**Status:** Absolute rule
**Domain:** Data Factory pipelines / ALM
**Applies to:** `microsoft-fabric`

---

## Why this exists

A Fabric Data Factory pipeline that hard-codes a source URL, a lakehouse item ID, or a storage path will fail when it is promoted from dev to test to prod via a deployment pipeline. Fabric deployment pipelines can only substitute values that are registered as deployment-pipeline parameters — hard-coded strings are transparent to the promotion mechanism and arrive in prod pointing at dev resources. This is the Fabric equivalent of the Power Platform "environment variables for everything that varies across environments" rule (CLAUDE.md §3 #2), and it is enforced by the same deployment-pipeline mechanism.

## How to apply

In every pipeline definition:

1. **Use pipeline parameters** for values that vary: source URLs, file paths, schedule triggers, sink lakehouse IDs.
2. **Register deployment-pipeline rule overrides** for each parameter in the Fabric portal → Deployment pipeline → Rules.
3. **Use `@pipeline().parameters.sinkWorkspaceId`** (not hard-coded item IDs) in Copy activity sinks and Dataflow sources.

```json
{
  "parameters": {
    "sourceUrl": { "type": "String", "defaultValue": "https://dev.blob.core.windows.net/bronze" },
    "sinkLakehouseId": { "type": "String", "defaultValue": "00000000-0000-0000-0000-000000000001" }
  },
  "activities": [{
    "type": "Copy",
    "source": { "type": "AzureBlobSource", "storeSettings": { "url": "@pipeline().parameters.sourceUrl" } },
    "sink": { "type": "LakehouseTable", "lakehouseId": "@pipeline().parameters.sinkLakehouseId" }
  }]
}
```

**Do:**
- Define a naming convention for parameters (e.g., `p_<purpose>_<env>`) so deployment-rule overrides are easy to identify.
- Test parameter substitution end-to-end in the test stage before assuming prod will be correct.
- Use the `fab` CLI `fabric-cicd` library to manage deployment-rule overrides in CI/CD rather than clicking them in the portal.

**Don't:**
- Store a prod lakehouse GUID in the pipeline's default parameter value — the default value is deployed as-is if no rule override exists.
- Use the same lakehouse item ID across dev/test/prod — each stage has a distinct item, and the IDs differ.
- Assume OneLake paths are stable across stages: `abfss://<workspace>@onelake.dfs.fabric.microsoft.com/<item>` embeds workspace and item GUIDs that change per stage.

## Edge cases / when the rule does NOT apply

A pipeline that exclusively reads from and writes to resources within the same deployment pipeline stage (e.g., a lakehouse and a warehouse in the same workspace) may omit the item-ID parameterization if the deployment pipeline propagates both items together — but the source URL still requires parameterization.

## See also

- [`../agents/data-factory-engineer.md`](../agents/data-factory-engineer.md) — owns pipeline design and the data-movement decision
- [`./alm-deploy-via-pipelines-parameterize-sources.md`](./alm-deploy-via-pipelines-parameterize-sources.md) — the broader deployment-pipeline ALM rule this extends

## Provenance

Codifies the Fabric ALM discipline from CLAUDE.md §3 #7 ("ALM is Git + deployment pipelines") applied specifically to pipeline parameters; Microsoft Learn Fabric deployment-pipeline rules documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
