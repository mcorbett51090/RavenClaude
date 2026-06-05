# Use app-of-apps (or ApplicationSets) to govern environment promotion in GitOps

**Status:** Pattern
**Domain:** GitOps / Argo CD
**Applies to:** `devops-cicd`

---

## Why this exists

When each environment (dev, staging, prod) is a separate Argo CD Application managed individually, promotion becomes a manual, error-prone act: someone must remember to update the right manifest in the right repo. The app-of-apps pattern (or its modern successor, ApplicationSets) makes environment promotion a Git operation — diff a single overlay file, open a PR, merge. The reconciler does the rest, drift is visible, and rollback is a `git revert`.

## How to apply

Structure the config repo so a root Application points to a directory of child Application manifests. Each child Application selects an overlay (Helm values file or Kustomize overlay) pinned to an image digest. Promotion is a PR that bumps the digest in the target environment's overlay.

```yaml
# apps/root-app.yaml — the app-of-apps root, one per cluster
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/config-repo
    targetRevision: HEAD
    path: apps/          # directory of child Application manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

```yaml
# apps/my-service-prod.yaml — a child Application for prod
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-service-prod
spec:
  source:
    repoURL: https://github.com/org/config-repo
    path: overlays/prod/my-service
    targetRevision: HEAD
  ...
```

Promotion from staging to prod = PR that copies/updates the image digest in `overlays/prod/my-service/values.yaml`.

**Do:**
- Pin images by digest (`image@sha256:…`), not by mutable tags like `latest` or `main`.
- Gate the promotion PR with the staging SLO health signal from `observability-sre`.
- Keep app and environment config repos separate: app source code in one, desired-state manifests in another.

**Don't:**
- Use `targetRevision: HEAD` for prod if you want explicit, auditable promotion — pin the tag or digest.
- Grant CI direct `kubectl apply` access; let the reconciler apply from Git.
- Mix application source and config repo to avoid having to maintain two repos — the promotion audit trail is worth it.

## Edge cases / when the rule does NOT apply

Very small teams with a single environment can start with a flat Application-per-service layout and migrate to app-of-apps when the number of Applications exceeds what's manageable manually (typically around 10–15 Applications).

## See also

- [`../agents/gitops-engineer.md`](../agents/gitops-engineer.md) — owns app-of-apps design and ApplicationSet configuration.
- [`./gitops-drift-detection-must-alert.md`](./gitops-drift-detection-must-alert.md) — drift detection is the companion to automated sync.

## Provenance

Codifies the Argo CD app-of-apps pattern (argo-cd.readthedocs.io) and the GitOps principle that Git is the sole source of desired state. ApplicationSets are the GA successor in Argo CD v2.3+.

---

_Last reviewed: 2026-06-05 by `claude`_
