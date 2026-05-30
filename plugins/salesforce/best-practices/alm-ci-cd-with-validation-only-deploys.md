# Validate check-only on every PR — the real deploy must never be the first time tests run against prod

**Status:** Absolute rule — a prod deploy that wasn't validated check-only first is a bug in the pipeline.

**Domain:** ALM / CI-CD

**Applies to:** `salesforce`

---

## Why this exists

A Metadata API / SFDX deploy is **transactional per component type but not atomic across a half-finished run that fails the test gate**: a deploy that fails partway can leave the org in a partial state, and a deploy that fails the 75% coverage gate fails *after* it has tried to commit. The `sf project deploy validate` (a.k.a. check-only) operation runs the entire deploy — including Apex tests — against the target org and **commits nothing**. Running it on every pull request turns "the prod deploy failed at 2 a.m." into "the PR was red before merge." The two recurring failure modes it catches: (1) a class referencing a field that doesn't exist in the target, and (2) coverage that passed in a sandbox subset but drops below 75% org-wide in prod. Without a CI validation gate, the first time anyone learns the deploy is broken is when it is breaking production.

## How to apply

Make the PR gate a check-only validation against a prod-like org, and reuse the validated deploy's Quick Deploy ID for the real promotion so prod isn't re-tested under change-freeze pressure.

```yaml
# .github/workflows/salesforce-validate.yml — runs on every PR
name: validate
on: pull_request
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install --global @salesforce/cli
      - name: Auth (JWT, no interactive login in CI)
        run: |
          sf org login jwt --client-id "$CONSUMER_KEY" \
            --jwt-key-file server.key --username "$DEPLOY_USER" --alias prod
      - name: Check-only validation — runs tests, commits nothing
        run: |
          sf project deploy validate --target-org prod \
            --test-level RunLocalTests --wait 60
```

```bash
# After merge, promote WITHOUT re-running tests by reusing the validated job:
sf project deploy quick --job-id "$VALIDATED_JOB_ID" --target-org prod
```

**Do:**
- Validate (`deploy validate`) on every PR against a prod-shaped org; block merge on failure.
- Use `RunLocalTests` for prod (excludes managed-package tests) — `NoTestRun` is rejected by the prod gate.
- Authenticate CI with **JWT bearer flow** (`sf org login jwt`), never an interactive login or a stored password.
- Reuse the validated job's ID with `deploy quick` to promote without re-testing inside a change window.

**Don't:**
- Let `sf project deploy start` to prod be the first place tests run.
- Store the JWT private key or consumer secret in the repo — inject them as masked CI secrets.
- Deploy with `--test-level NoTestRun` to production (the platform rejects it; don't try to engineer around the gate).

## Edge cases / when the rule does NOT apply

`deploy validate` results expire (validated deploys are only Quick-Deployable for a limited window `[verify-at-build]`), so a validation that's gone stale must be re-run before `deploy quick`. A genuine emergency hotfix may deploy a minimal source set directly under incident process — but it is back-ported into the pipeline immediately, never left as a manual edit. Destructive changes (`destructiveChanges.xml`) still need ordering care: validation confirms the deploy *parses*, not that the deletion is safe to a downstream dependency.

## See also

- [`package-and-deploy-in-dependency-order.md`](./package-and-deploy-in-dependency-order.md) — the dependency-ordered deploy this gates
- [`alm-scratch-orgs-and-source-tracking.md`](./alm-scratch-orgs-and-source-tracking.md) — the source of truth CI deploys from
- [`../knowledge/packaging-and-deployment.md`](../knowledge/packaging-and-deployment.md) — the coverage gate and pipeline
- [`../skills/salesforce-release-pipeline/SKILL.md`](../skills/salesforce-release-pipeline/SKILL.md) — step 5 (validate before deploy)

## Provenance

Codifies the `salesforce-release-pipeline` skill's "validate (check-only) before the real deploy" step and house opinion #15. Grounded in [`../knowledge/packaging-and-deployment.md`](../knowledge/packaging-and-deployment.md) and Salesforce's Metadata-API-deployment best-practices. CLI flag names and Quick-Deploy expiry windows are version-sensitive — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
