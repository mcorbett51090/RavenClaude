# Keep application source and environment config in separate repositories

**Status:** Pattern
**Domain:** GitOps
**Applies to:** `devops-cicd`

---

## Why this exists

When application source code and Kubernetes manifests live in the same repository, every commit triggers a full pipeline run including the CI build — even if only a Helm values file changed. More importantly, the audit trail is muddied: you cannot tell at a glance whether a config repo commit is an app change or an environment promotion. Separation means the config repo is a pure, auditable record of desired state; its history is the deployment history.

## How to apply

Maintain two repositories: the **app repo** contains source code, tests, and the Dockerfile/build definition; the **config repo** (or "gitops repo") contains Kubernetes manifests, Helm values overlays, and Kustomize patches organized by environment.

```
# Config repo layout (environment-per-directory)
config-repo/
├── base/
│   └── my-service/
│       ├── deployment.yaml
│       └── service.yaml
├── overlays/
│   ├── dev/
│   │   └── my-service/
│   │       └── values.yaml      # image: my-service@sha256:<dev-digest>
│   ├── staging/
│   │   └── my-service/
│   │       └── values.yaml      # image: my-service@sha256:<staging-digest>
│   └── prod/
│       └── my-service/
│           └── values.yaml      # image: my-service@sha256:<prod-digest>
```

CI in the app repo builds the image and opens a PR in the config repo to bump the digest in the dev overlay. Promotion to staging/prod is a second PR in the config repo, gated on the health signal.

**Do:**
- Grant CI a scoped token to open PRs in the config repo only — not push directly to main.
- Use image digests (not tags) in the config repo — tags are mutable, digests are immutable.
- Treat config repo PRs as production changes — require review + CI checks.
- Keep one config repo for all services rather than one per service (easier to see cross-service promotions).

**Don't:**
- Run `kubectl apply` from CI directly; the reconciler applies from Git.
- Commit generated manifests into the app repo alongside source code.
- Use the same token for app CI and config repo writes — scope the trust boundary.

## Edge cases / when the rule does NOT apply

Very small projects with a single environment can start monorepo until the config-repo separation pays for itself (typically when more than one environment or more than two services exist).

## See also

- [`../agents/gitops-engineer.md`](../agents/gitops-engineer.md) — owns the config repo structure and GitOps workflow.
- [`./gitops-app-of-apps-for-environment-promotion.md`](./gitops-app-of-apps-for-environment-promotion.md) — the config repo is the input to app-of-apps.

## Provenance

Codifies the GitOps separation-of-concerns principle from the Argo CD and Flux documentation and the Weaveworks GitOps v2 specification.

---

_Last reviewed: 2026-06-05 by `claude`_
