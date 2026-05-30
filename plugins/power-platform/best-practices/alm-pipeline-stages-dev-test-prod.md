# A pipeline has a test stage between dev and prod — always

**Status:** Absolute rule — exporting from dev and importing to prod with nothing in between is not a pipeline, it's a loaded gun.

**Domain:** ALM

**Applies to:** `power-platform`

---

## Why this exists

The single most common ALM failure is a "pipeline" that exports an unmanaged solution from dev and imports it straight to prod. There is no place to catch a missing dependency, an unbound connection reference, an empty environment variable, or a managed-layer conflict before it lands on real users. The fix that "worked in dev" fails in prod because dev had connections, env-var values, and dependencies that prod doesn't. A test (or UAT) stage between dev and prod is where the *managed* artifact gets imported into a prod-like environment and exercised before anyone in prod sees it. Without that stage, every release is its own first-time integration test — in production.

## How to apply

Minimum viable topology is **DEV → TEST → PROD**, with the managed artifact built once and imported (not re-exported) downstream. Larger shops add a dedicated BUILD env and a UAT stage: **DEV → BUILD → TEST → UAT → PROD**.

```bash
# DEV (authoring): export UNMANAGED, commit the unpacked tree (see alm-source-control-*)
pac auth select --name dev
pac solution export --name MySolution --managed false --path ./out/MySolution.zip

# BUILD: pack unmanaged, import to a clean build env, re-export as MANAGED (the release artifact)
pac auth select --name build
pac solution import --path ./out/MySolution.zip
pac solution export --name MySolution --managed true --path ./out/MySolution_managed.zip

# TEST: import the MANAGED artifact with TEST's deployment settings, then run smoke tests
pac auth select --name test
pac solution import --path ./out/MySolution_managed.zip --settings-file ./deploymentSettings-test.json

# PROD: same managed bytes, PROD settings, behind a human approval gate
pac auth select --name prod
pac solution import --path ./out/MySolution_managed.zip --settings-file ./deploymentSettings-prod.json
```

The five canonical ADO stages: **lint** (`pac solution check`, fail on Critical/High) → **build** (pack → import-to-build → export managed → publish artifact) → **check-in-managed** (version the artifact by commit SHA) → **deploy-to-test** → **deploy-to-uat/prod** (gated by approvals; PROD always has a human approver).

**Do:**
- Gate PROD on a human approver. UAT may auto-deploy on green TEST; PROD never auto-deploys.
- Run `pac solution check` as a *lint* stage and fail the build on Critical/High findings.
- Use `--settings-file` per stage so the same artifact carries env-specific config without re-packing.

**Don't:**
- Wire DEV directly to PROD "because it's a small solution."
- Skip `pac solution check` because it's slow — it's the cheapest stage to fail in.
- Let a customization bypass TEST by re-exporting for the PROD stage (Power Platform Pipelines actively prevent this; your custom ADO pipeline must too).

## Edge cases / when the rule does NOT apply

- **Genuine emergency hotfix** may use a dedicated hotfix pipeline (patch) that still passes through *a* test env — a faster path, not a path that skips testing.
- **In-product Power Platform Pipelines** enforce sequential stages and the same-artifact rule structurally: the solution is exported once at deploy-request time and the identical artifact passes each stage in order (verified, MS Learn pipelines FAQ, 2026-05-30) — you cannot skip QA.
- **Single-environment trial / demo tenants** with no prod aren't on a promotion path; the rule is about anything that reaches real users.

## See also

- [`./managed-vs-unmanaged-solution-discipline.md`](./managed-vs-unmanaged-solution-discipline.md) — unmanaged in dev, managed downstream
- [`./alm-one-build-artifact-promoted-unchanged.md`](./alm-one-build-artifact-promoted-unchanged.md) — why TEST and PROD run identical bytes
- [`./alm-fresh-import-smoke-test-before-release.md`](./alm-fresh-import-smoke-test-before-release.md) — the gate that proves import success
- [`../knowledge/alm-governance-decision-trees.md`](../knowledge/alm-governance-decision-trees.md) — pipeline-tooling and environment-topology decision trees
- [`../skills/alm-pipeline-design/SKILL.md`](../skills/alm-pipeline-design/SKILL.md) §3 — the canonical five-stage ADO shape

## Provenance

Codifies the `solution-alm-engineer` anti-pattern ("a pipeline that exports from dev and imports to prod with no test stage in between") and the `alm-pipeline-design` skill's five-stage shape. Same-artifact / no-QA-bypass enforcement and `--settings-file` / `--managed` flags verified against Microsoft Learn (`pac solution import`, pipelines FAQ), retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
