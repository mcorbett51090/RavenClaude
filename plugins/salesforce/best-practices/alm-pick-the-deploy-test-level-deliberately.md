# Pick the deploy test level deliberately — RunLocalTests for prod, NoTestRun only in scratch/dev

**Status:** Pattern — strong default; the prod test level is effectively fixed by the platform.

**Domain:** ALM / CI-CD

**Applies to:** `salesforce`

---

## Why this exists

The `--test-level` flag on a Metadata API / SFDX deploy decides *which Apex tests run and whether the deploy is allowed to commit*, and the wrong choice fails one of two ways. Choose too loose (`NoTestRun`) for production and the platform rejects the deploy outright — production deploys of Apex **must** run tests and clear the 75% org-wide coverage gate. Choose too heavy (`RunAllTestsInOrg`) on every sandbox deploy and a pipeline that should take three minutes takes thirty, because you're re-running managed-package tests and unrelated suites on every push. The level also interacts with **coverage scope**: `RunSpecifiedTests` only counts the classes you name, so a deploy can pass with a class far below 75% if you didn't list a test that exercises it — a silent gap that surfaces as a prod rejection later. Matching the test level to the stage keeps CI fast where speed is safe and strict where strictness is mandatory.

## How to apply

Map the test level to the pipeline stage. Prod is fixed at `RunLocalTests`; loosen only upstream where nothing is at risk.

```
SCRATCH / DEV sandbox ... NoTestRun ............ fast inner loop; nothing downstream depends on it
INTEGRATION ............. RunLocalTests ......... catch cross-feature breakage early, exclude managed-pkg tests
UAT / staging ........... RunLocalTests ......... mirror the prod gate before sign-off
PRODUCTION .............. RunLocalTests ......... required: runs all org Apex tests EXCEPT managed-package tests
  (RunSpecifiedTests) ... only for a tightly-scoped hotfix — and you MUST name tests covering every changed class
  (RunAllTestsInOrg) .... rarely; includes managed-package tests — slow, usually unnecessary
```

```bash
# Production / UAT — the standard, prod-required level
sf project deploy validate --target-org prod --test-level RunLocalTests --wait 60

# Scratch inner loop — skip tests for speed; safe because nothing depends on this org
sf project deploy start --target-org scratch --test-level NoTestRun

# Scoped hotfix — name EVERY test that covers a changed class, or coverage silently passes short
sf project deploy validate --target-org prod --test-level RunSpecifiedTests \
  --tests BillingServiceTest --tests LateFeeHandlerTest --wait 30
```

**Do:**
- Use `RunLocalTests` for prod and prod-like stages — it excludes managed-package tests you don't own.
- Use `NoTestRun` only in scratch/dev where speed is the point and nothing downstream trusts the result.
- If you use `RunSpecifiedTests`, name a test that exercises **every** changed class, or coverage passes on an incomplete picture.

**Don't:**
- Try to deploy Apex to prod with `NoTestRun` — the platform rejects it; don't engineer around the gate.
- Default to `RunAllTestsInOrg` everywhere "to be safe" — it drags managed-package tests and slows every deploy.
- Treat clearing the 75% gate as proof of correctness — pair it with the 200-record bulk assertions.

## Edge cases / when the rule does NOT apply

A deploy containing **no Apex and no metadata that triggers a recompile** can deploy to prod without a test run — the gate only binds when Apex is involved `[verify-at-build]`. A genuine **emergency hotfix** may use `RunSpecifiedTests` to validate fast under incident pressure, but the named-test discipline above is then *more* important, not less. The exact list of metadata types that force a recompile (and therefore a test run) shifts across releases — verify rather than assume.

## See also

- [`alm-ci-cd-with-validation-only-deploys.md`](./alm-ci-cd-with-validation-only-deploys.md) — validate check-only before the real deploy
- [`package-and-deploy-in-dependency-order.md`](./package-and-deploy-in-dependency-order.md) — the coverage gate and ordered deploy this runs inside
- [`apex-test-data-with-testfactory-not-seealldata.md`](./apex-test-data-with-testfactory-not-seealldata.md) — what the tests the gate runs should look like
- [`../knowledge/packaging-and-deployment.md`](../knowledge/packaging-and-deployment.md) — the 75% gate and pipeline
- [`../skills/salesforce-release-pipeline/SKILL.md`](../skills/salesforce-release-pipeline/SKILL.md) — step 4 (gate on tests)

## Provenance

Codifies the `salesforce-release-pipeline` skill's "run Apex tests with the right test level" step and house opinion #15's coverage gate. Grounded in [`../knowledge/packaging-and-deployment.md`](../knowledge/packaging-and-deployment.md) and Salesforce's Metadata-API deployment / `runTests` documentation. Test-level names, recompile-triggering types, and managed-package exclusion behavior are version-sensitive — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
