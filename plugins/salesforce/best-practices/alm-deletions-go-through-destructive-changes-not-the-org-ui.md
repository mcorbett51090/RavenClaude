# Delete metadata through a tracked destructiveChanges manifest, applied after the additive deploy — never by clicking in the org

**Status:** Pattern — strong default; manual prod deletions are a pipeline bug.

**Domain:** ALM / CI-CD

**Applies to:** `salesforce`

---

## Why this exists

Source tracking and additive deploys move *new and changed* metadata, but a normal `deploy start` does **not** delete components that disappeared from the source — so a field, class, or Flow you removed in the repo lingers in the org as orphaned metadata, drifting prod away from the repo. The fix is a **destructive-changes manifest** (`destructiveChanges.xml` / `--predestructive-changes` / `--postdestructive-changes`) that is itself version-controlled and runs through the pipeline. Two ordering facts make this load-bearing: deletions must be applied **after** the additive deploy when something still references the component being removed, and **before** it when an addition would collide with the old component — getting the order wrong fails the deploy or, worse, deletes something still in use. Deleting by clicking in the org instead leaves no record of *what* was removed or *why*, can't be replayed into the next environment, and silently breaks any downstream reference the UI didn't warn about.

## How to apply

Express the deletion as a tracked manifest, choose pre- vs post-destructive by the dependency direction, and validate before committing.

```xml
<!-- destructiveChanges.xml — version-controlled, deployed through the pipeline -->
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
  <types>
    <members>Account.Legacy_Score__c</members>
    <name>CustomField</name>
  </types>
  <version>63.0</version>
</Package>
```

```bash
# POST-destructive: deploy the additive change first, THEN delete the now-unreferenced component
sf project deploy start --target-org uat \
  --manifest manifest/package.xml \
  --post-destructive-changes manifest/destructiveChanges.xml

# Always validate (check-only) the combined change first — confirms the deletion parses and nothing breaks
sf project deploy validate --target-org prod \
  --manifest manifest/package.xml \
  --post-destructive-changes manifest/destructiveChanges.xml --test-level RunLocalTests
```

**Do:**
- Keep `destructiveChanges.xml` in version control and deploy it through the same pipeline as additive changes.
- Use **post-destructive** when something still references the component until the additive deploy removes the reference; **pre-destructive** when the old component collides with what you're adding.
- Validate the combined (additive + destructive) deploy check-only before the real run.

**Don't:**
- Click "Delete" on prod metadata in Setup — it's invisible to the repo and unreplayable to the next environment.
- Bundle a risky deletion with a large additive deploy without validating; a failed delete can fail the whole transaction.
- Assume source tracking removes deleted components on its own — additive deploys don't delete.

## Edge cases / when the rule does NOT apply

**Data deletion** (records) is a different operation entirely — that goes through Bulk API / Data Loader with a backup, not a metadata manifest. Some component types **cannot be deleted via the Metadata API** and require a manual step or a support case `[verify-at-build]` — document the manual deletion in the work item so the chain stays auditable even when the tool can't do it. And deleting a field with data in it may require first clearing or archiving that data; the destructive deploy removes the *schema*, not the obligation to handle the rows it held.

## See also

- [`package-and-deploy-in-dependency-order.md`](./package-and-deploy-in-dependency-order.md) — additive and destructive deploys both follow dependency order
- [`alm-ci-cd-with-validation-only-deploys.md`](./alm-ci-cd-with-validation-only-deploys.md) — validate the combined change before committing
- [`alm-scratch-orgs-and-source-tracking.md`](./alm-scratch-orgs-and-source-tracking.md) — why additive source tracking alone leaves orphans
- [`../knowledge/packaging-and-deployment.md`](../knowledge/packaging-and-deployment.md) — the deploy pipeline these run in

## Provenance

Extends house opinion #15 ("never click-deploy to prod") to the deletion case, codifying the `salesforce-platform-architect`'s release discipline. Grounded in [`../knowledge/packaging-and-deployment.md`](../knowledge/packaging-and-deployment.md) and Salesforce's Metadata-API destructive-changes documentation. Pre/post-destructive flag names and the non-deletable-types list are version-sensitive — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
