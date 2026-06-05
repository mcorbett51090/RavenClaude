# devops-cicd — best-practice docs

Named, citable rules for the `devops-cicd` plugin's specialists. Each file is **one rule**.

---

## Index

_26 rules._

| Doc | Status | Use when |
|---|---|---|
| [`build-build-once-promote-the-same-artifact.md`](./build-build-once-promote-the-same-artifact.md) | Absolute rule | Deciding whether to rebuild per environment |
| [`secure-oidc-not-static-keys.md`](./secure-oidc-not-static-keys.md) | Absolute rule | Authenticating a pipeline to a cloud provider |
| [`secure-rotate-and-scope-short-lived-credentials.md`](./secure-rotate-and-scope-short-lived-credentials.md) | Absolute rule | Any credential used in CI/CD |
| [`build-cache-keys-must-encode-every-input.md`](./build-cache-keys-must-encode-every-input.md) | Absolute rule | Setting up build or test caches |
| [`deploy-rollback-before-you-ship.md`](./deploy-rollback-before-you-ship.md) | Absolute rule | Planning any production deployment |
| [`operate-change-freezes-are-policy-not-vibes.md`](./operate-change-freezes-are-policy-not-vibes.md) | Pattern | Deciding when to freeze or restrict deploys |
| [`build-monorepo-pipelines-must-be-change-scoped.md`](./build-monorepo-pipelines-must-be-change-scoped.md) | Absolute rule | Designing CI for a monorepo |
| [`deploy-separate-deploy-from-release.md`](./deploy-separate-deploy-from-release.md) | Pattern | Planning a progressive-delivery strategy |
| [`build-fast-gates-first.md`](./build-fast-gates-first.md) | Absolute rule | Ordering pipeline stages |
| [`deploy-ephemeral-preview-environment-per-pr.md`](./deploy-ephemeral-preview-environment-per-pr.md) | Pattern | Choosing a PR review workflow |
| [`gitops-no-plaintext-secrets.md`](./gitops-no-plaintext-secrets.md) | Absolute rule | Handling secrets in a GitOps config repo |
| [`design-trunk-based-over-long-lived-branches.md`](./design-trunk-based-over-long-lived-branches.md) | Pattern | Choosing a branching strategy |
| [`pipeline-test-your-pipeline.md`](./pipeline-test-your-pipeline.md) | Pattern | Modifying CI/CD pipeline definitions |
| [`gitops-drift-detection-must-alert.md`](./gitops-drift-detection-must-alert.md) | Absolute rule | Setting up GitOps drift detection |
| [`release-semver-is-a-contract.md`](./release-semver-is-a-contract.md) | Absolute rule | Versioning artifacts or APIs |
| [`artifact-sign-every-release.md`](./artifact-sign-every-release.md) | Absolute rule | Publishing any production artifact |
| [`pipeline-stage-idempotency.md`](./pipeline-stage-idempotency.md) | Absolute rule | Designing pipeline stages that may retry |
| [`release-changelog-is-machine-generated.md`](./release-changelog-is-machine-generated.md) | Pattern | Setting up release automation |
| [`gitops-app-of-apps-for-environment-promotion.md`](./gitops-app-of-apps-for-environment-promotion.md) | Pattern | Structuring Argo CD for multi-environment promotion |
| [`artifact-image-layer-hygiene.md`](./artifact-image-layer-hygiene.md) | Absolute rule | Writing or reviewing a production Dockerfile |
| [`pipeline-required-checks-gate-the-merge.md`](./pipeline-required-checks-gate-the-merge.md) | Absolute rule | Configuring branch protection rules |
| [`deploy-database-migrations-before-code.md`](./deploy-database-migrations-before-code.md) | Absolute rule | Deploying a change that includes a schema migration |
| [`release-feature-flags-are-not-free.md`](./release-feature-flags-are-not-free.md) | Pattern | Adding or reviewing a feature flag |
| [`gitops-separate-app-and-env-repos.md`](./gitops-separate-app-and-env-repos.md) | Pattern | Structuring repositories for GitOps |
| [`pipeline-no-manual-steps-in-the-happy-path.md`](./pipeline-no-manual-steps-in-the-happy-path.md) | Pattern | Auditing or redesigning a deployment pipeline |
| [`artifact-reproducible-builds-via-lockfiles.md`](./artifact-reproducible-builds-via-lockfiles.md) | Absolute rule | Setting up dependency management in any language |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
