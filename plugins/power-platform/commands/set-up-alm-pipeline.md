---
description: Set up a Power Platform ALM pipeline — source-control the unpacked solution tree, one build artifact promoted unchanged across dev→test→prod, connection references + environment variables + Key Vault secrets, managed solutions downstream, and a fresh-import smoke test before release.
argument-hint: "[the solution name and target environments]"
---

# Set up an ALM pipeline

You are running `/power-platform:set-up-alm-pipeline`. Stand up a disciplined ALM pipeline for the solution the user named (`$ARGUMENTS`), following this plugin's `solution-alm-engineer` discipline. The goal is reproducible, environment-portable releases — not a chain of manual exports.

## When to use this

A solution is moving beyond one environment, or an ad-hoc export/import habit needs to become a real pipeline.

## Steps

1. **Source-control the unpacked solution** (`alm-source-control-the-unpacked-solution-tree`): commit the unpacked tree (pac solution unpack), not the zip — so diffs are reviewable.
2. **One publisher prefix per repo** (`alm-pin-one-publisher-prefix-per-repo`); **managed vs unmanaged discipline** (`managed-vs-unmanaged-solution-discipline`): unmanaged in dev, **managed downstream**.
3. **One build artifact promoted unchanged** (`alm-one-build-artifact-promoted-unchanged`) through **dev → test → prod** (`alm-pipeline-stages-dev-test-prod`) — never rebuild per environment.
4. **Externalize all config** (`alm-connection-references-not-hardcoded-connections`, `alm-environment-variables-not-hardcoded-config`, `alm-secrets-in-key-vault-not-env-var-defaults`): connection references, environment variables, and Key Vault for secrets — set per environment, never baked into the artifact.
5. **Upgrade by default, patch only for hotfixes** (`alm-upgrade-by-default-patch-only-for-hotfixes`).
6. **Fresh-import smoke test before release** (`alm-fresh-import-smoke-test-before-release`): import into a clean environment and smoke-test before promoting to prod.

## Guardrails

- Never click-deploy to prod; the artifact flows through the pipeline.
- Never bake an environment-specific connection or secret into the managed solution.
- Tee up the `pac`/pipeline commands; leave the prod promotion as the human's confirm step.
