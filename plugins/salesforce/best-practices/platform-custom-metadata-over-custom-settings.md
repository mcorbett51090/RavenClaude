# Prefer Custom Metadata Types over Custom Settings for environment-varying configuration

**Status:** Pattern
**Domain:** Platform configuration
**Applies to:** `salesforce`

---

## Why this exists

Custom Settings (List and Hierarchy) store configuration as org data — records that do not travel through the release pipeline and must be manually re-entered after a sandbox refresh or a deployment to a new org. Custom Metadata Types (CMTs) are **metadata records** — they deploy with packages and Change Sets, can be source-tracked, and are version-controlled alongside the code that reads them. The house opinion #15 ("bundle metadata in 2GP packages; deploy in dependency order; never click-deploy to prod") is impossible to honor if configuration lives in Custom Settings, because Custom Settings records are not metadata. For any configuration that varies by environment or that must be reproducible across sandboxes, CMTs are the correct primitive.

## How to apply

| Use case | Correct type |
|---|---|
| Feature flags, per-environment URLs, integration endpoints | Custom Metadata Type |
| Per-user / per-profile overrides (truly user-specific) | Hierarchy Custom Setting |
| Global configuration that is 100% identical in every environment and never promoted | Custom Setting (list) is acceptable |

Creating a CMT:
```apex
// Reading a Custom Metadata Type record in Apex
My_Config__mdt config = [
    SELECT Api_Endpoint__c, Retry_Count__c
    FROM My_Config__mdt
    WHERE DeveloperName = 'Production_Config'
    LIMIT 1
];
```

Deployment:
```bash
# CMT records deploy with the package or source deploy
sf project deploy start --source-dir force-app/main/default/customMetadata
```

**Do:**
- Store CMT records in `force-app/main/default/customMetadata/` so they are source-tracked and version-controlled.
- Use a per-environment naming convention (`Dev_Config`, `QA_Config`, `Prod_Config`) for CMT records so the correct record is selected at runtime.
- Use `CMDT.getInstance()` or `[SELECT ... FROM My_Config__mdt WHERE DeveloperName = :env LIMIT 1]` — not hard-coded `DeveloperName` strings — when the environment name is parameterized.

**Don't:**
- Store API secrets or credentials in CMT records — CMT records are deployable metadata and visible to anyone with metadata access; use Named Credentials for secrets.
- Migrate a Hierarchy Custom Setting to a CMT if per-user/per-profile overrides are genuinely needed — Hierarchy Settings handle that; CMTs do not.
- Use CMTs for large volumes of records (> 10,000) — CMTs are for configuration, not a data store; query performance degrades at volume.

## Edge cases / when the rule does NOT apply

Per-user overrides that must differ by user profile, role, or individual user are the canonical use case for Hierarchy Custom Settings. CMTs cannot express user-scoped configuration; use Hierarchy Custom Settings there.

## See also

- [`../agents/salesforce-platform-architect.md`](../agents/salesforce-platform-architect.md) — owns data model and configuration architecture decisions
- [`./platform-config-as-metadata-not-data.md`](./platform-config-as-metadata-not-data.md) — the broader "configuration as metadata" rule this extends

## Provenance

Codifies house opinion #15 and the CLAUDE.md §2 ("bundle metadata in 2GP packages") applied to the Custom Settings vs Custom Metadata Types choice; Salesforce Custom Metadata Types documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
