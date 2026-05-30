# Test the import on a fresh environment before declaring a release done

**Status:** Absolute rule — export success is not import success. A release you've only exported is a release you've never deployed.

**Domain:** ALM

**Applies to:** `power-platform`

---

## Why this exists

The thing that breaks at the customer is almost never the export — it's the *import into an environment that doesn't already have everything the source environment had*. Dev has the connections, the env-var values, the dependency solutions, the publisher already registered, the prerequisite tables already present. A managed `.zip` that exports perfectly can still fail to import into a clean environment because of a missing dependency, an unbound connection reference, an empty required environment variable, or a managed-layer conflict — and the *only* place to discover that cheaply is a throwaway sandbox, before real users are involved. A fresh-import smoke test costs minutes; finding the same failure in the customer's PROD costs an emergency rollback and a credibility hit. The test is a release gate, not a nice-to-have.

## How to apply

Before signing off a release, import the exact managed artifact into a clean, disposable sandbox using the target environment's deployment settings, then exercise the critical path. Tear the sandbox down after.

```bash
# Spin up (or reset) a throwaway sandbox — isolated from anything real
pac admin create --name "smoke-$(date +%s)" --type Sandbox --domain mc-smoke-$(date +%s) --region unitedstates

# Import the SAME managed artifact the pipeline will ship to prod (not a fresh export)
pac auth select --name smoke
pac solution import --path ./out/MySolution_managed_${BUILD_SHA}.zip \
    --settings-file ./deploymentSettings-prod.json

# Then exercise the critical path: open the app, run the key flow, confirm a write lands.
# If it fails HERE, it will fail at the customer. Cost of finding it now: minutes.

# Tear down when green
pac admin delete --environment "smoke-..."
```

**Do:**
- Import the **same byte-for-byte artifact** the pipeline promotes (per [`./alm-one-build-artifact-promoted-unchanged.md`](./alm-one-build-artifact-promoted-unchanged.md)) — a fresh export defeats the test.
- Use the **target environment's** settings file so missing env-var values and unbound connection refs surface here.
- Actually run the critical path — a clean import that no one exercised can still have a broken flow waiting for first trigger.

**Don't:**
- Declare a release done on export success alone.
- Smoke-test in an environment that already has the prior version installed — an upgrade over an existing solution hides the missing-dependency failures a *fresh* import would catch.
- Reuse a long-lived "test" env that's accumulated connections and env-var values over months — it's no longer a clean target and lies to you about import success.

## Edge cases / when the rule does NOT apply

- **In-product Power Platform Pipelines** import into a real TEST stage as part of every deploy — that stage *is* an import test, but it's an upgrade over the prior version, so a separate clean-env test still catches first-install dependency gaps the TEST upgrade masks.
- **Patches** are validated by importing the patch over its parent in a clean env that has the parent — the "fresh" baseline is parent-installed, not empty.
- **Throwaway spike solutions** never destined for a customer don't need the gate; the rule is about anything on a release path.

## See also

- [`./alm-pipeline-stages-dev-test-prod.md`](./alm-pipeline-stages-dev-test-prod.md) — where this gate sits in the pipeline
- [`./alm-one-build-artifact-promoted-unchanged.md`](./alm-one-build-artifact-promoted-unchanged.md) — test the artifact you'll actually ship
- [`../agents/solution-alm-engineer.md`](../agents/solution-alm-engineer.md) — "Test the import on a fresh environment before declaring a release done"
- [`../skills/alm-pipeline-design/SKILL.md`](../skills/alm-pipeline-design/SKILL.md) §8 — the fresh-import smoke test

## Provenance

Codifies house opinion §3 #13 ("Test the import, not just the export") and the `solution-alm-engineer` opinion of the same name, plus `alm-pipeline-design` skill §8. `pac admin create/delete --type Sandbox` and `pac solution import --settings-file` verified against Microsoft Learn (`pac admin`, `pac solution` references), retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
