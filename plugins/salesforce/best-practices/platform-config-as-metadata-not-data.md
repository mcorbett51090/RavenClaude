# Store configuration as deployable metadata (Custom Metadata Types), not as data records or hard-coded values

**Status:** Absolute rule for environment-varying configuration — a hard-coded ID or a config-bearing data record is a bug.

**Domain:** Platform architecture / configuration management

**Applies to:** `salesforce`

---

## Why this exists

Configuration that lives as a **data record** (a row in a custom object, or a List Custom Setting) does not travel through the release pipeline — it has to be re-created or data-loaded into every org by hand, which means prod config drifts from the repo and "works in UAT" stops predicting prod. Configuration that lives as a **hard-coded value** (a record ID, a profile name, an endpoint, a threshold baked into Apex or a Flow) breaks the moment the metadata is deployed to an org where that ID doesn't exist — and house opinion #5 forbids it outright. **Custom Metadata Types (CMDT)** solve both: CMDT records are *metadata*, so they deploy with the package, are version-controlled, and are queryable from Apex and Flow **without** consuming a SOQL query against the governor limit. The recurring failure this prevents: a sandbox-validated deploy that fails in prod because a class queried a hard-coded RecordType Id, or a feature that silently misbehaves because its config rows were never migrated.

## How to apply

Put environment-varying configuration in a Custom Metadata Type, deploy it with the package, and read it by name — never query for a hard-coded Id.

```apex
// DON'T — hard-coded Id breaks on deploy to any other org (house opinion #5)
Id rt = '012090000009abcXYZ'; // RecordType Id from sandbox — wrong everywhere else

// DO — read deployable config metadata by developer name, no SOQL consumed
Billing_Setting__mdt cfg = Billing_Setting__mdt.getInstance('Default');
Decimal threshold = cfg.Late_Fee_Threshold__c;
// RecordType by developer name, not a hard-coded Id:
Id rt = Schema.SObjectType.Case.getRecordTypeInfosByDeveloperName()
          .get('Escalation').getRecordTypeId();
```

```bash
# CMDT records are metadata — they retrieve/deploy with the project like any other component
sf project deploy start --metadata CustomMetadata:Billing_Setting.Default --target-org uat
```

**Do:**
- Model feature flags, thresholds, endpoint keys, and mapping tables as **Custom Metadata Types** so they ship with the package.
- Resolve RecordTypes, profiles, and queues by **developer name / API name**, never by Id.
- Use `getInstance()` / `getAll()` in Apex (no SOQL governor cost) and the CMDT data source in Flow.

**Don't:**
- Hard-code record/RecordType/profile/queue Ids in Apex, Flow, formulas, or named credentials (house opinion #5).
- Store config that must travel between orgs as **data** (custom-object rows or List Custom Settings) — it won't deploy.
- Put secrets in CMDT in plain text — secrets belong in Named Credentials / Protected CMDT / a secrets store, not the package source.

## Edge cases / when the rule does NOT apply

**Per-user or per-profile runtime configuration** is the legitimate home of **Hierarchy Custom Settings** — they vary by running user, which CMDT can't do, and that is a genuine exception. Genuinely **transactional, user-edited data at volume** is data, not config — it belongs in a custom object. And **secrets** (API keys, passwords) never belong in package source at all: use Named Credentials or an external secret store, with CMDT holding only the non-secret reference. CMDT also has size/row limits for very large mapping tables — at extreme scale a custom object plus a deployed seed-data plan may be the pragmatic choice `[verify-at-build]`.

## See also

- [`integration-named-credentials-not-hardcoded-endpoints.md`](./integration-named-credentials-not-hardcoded-endpoints.md) — the endpoint/secret half of "no hard-coded values"
- [`package-and-deploy-in-dependency-order.md`](./package-and-deploy-in-dependency-order.md) — why config-as-metadata flows through the pipeline cleanly
- [`alm-scratch-orgs-and-source-tracking.md`](./alm-scratch-orgs-and-source-tracking.md) — keeping repo and org config honest
- [`../knowledge/packaging-and-deployment.md`](../knowledge/packaging-and-deployment.md) — what is and isn't packageable

## Provenance

Codifies house opinion #5 ("no hard-coded IDs — query or use custom metadata") and the `salesforce-platform-architect`'s "if it isn't in a package and a pipeline, it isn't real." Grounded in [`../knowledge/packaging-and-deployment.md`](../knowledge/packaging-and-deployment.md) and Salesforce's Custom Metadata Types vs Custom Settings guidance. CMDT limits and the SOQL-free access guarantee are version-sensitive — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
