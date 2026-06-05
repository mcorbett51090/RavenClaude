# Separate Helm values by environment — never hardcode env-specific config in chart defaults

**Status:** Pattern
**Domain:** Kubernetes / Helm packaging
**Applies to:** `cloud-native-kubernetes`

---

## Why this exists

A Helm chart with production values in `values.yaml` means every environment that doesn't override them inherits production settings by default — the wrong default direction. Dev should fail cheaply, not silently run with production replica counts and resource limits. The house opinion #5 ("pin and declare everything") extends to Helm: each environment's values are declared explicitly in a named values file, overrides are intentional, and the base `values.yaml` contains safe development defaults, not production ones.

## How to apply

**Chart structure:**
```
charts/my-app/
├── Chart.yaml
├── values.yaml              # dev/safe defaults
├── values-staging.yaml      # staging overrides
├── values-prod.yaml         # production overrides
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    └── hpa.yaml
```

```yaml
# values.yaml — safe development defaults (not production)
replicaCount: 1
image:
  repository: myregistry.example.com/app
  tag: dev
  pullPolicy: IfNotPresent

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi

autoscaling:
  enabled: false

podDisruptionBudget:
  enabled: false
```

```yaml
# values-prod.yaml — production overrides
replicaCount: 3   # baseline before HPA

resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 60

podDisruptionBudget:
  enabled: true
  minAvailable: 2
```

Deploy with environment-specific values:
```bash
# Dev
helm upgrade --install my-app ./charts/my-app \
  --namespace dev \
  --values charts/my-app/values.yaml

# Production
helm upgrade --install my-app ./charts/my-app \
  --namespace production \
  --values charts/my-app/values.yaml \
  --values charts/my-app/values-prod.yaml
  # values-prod.yaml overrides take precedence (last wins)
```

**Do:**
- Make `values.yaml` safe to deploy in dev with no arguments — it should not require any `-f` override to function.
- Use `--values` layering (base + environment); avoid `--set` in CI for anything more than a single image tag override.
- Store environment values files in the same Git repo as the chart — reviewed and version-controlled.

**Don't:**
- Put production replica counts, resource limits, or secrets in the base `values.yaml`.
- Use `--set` to pass entire complex structures — the override is invisible to reviewers and not version-controlled.
- Commit the Helm release secret into the repo — it's in-cluster only.

## Edge cases / when the rule does NOT apply

- **GitOps with Argo CD ApplicationSets**: the values layering may be expressed in the `ApplicationSet` template rather than separate values files; the principle (explicit env-specific config) still applies.
- **Simple single-environment deployments**: a single values override file alongside the chart is sufficient.

## See also

- [`../agents/kubernetes-architect.md`](../agents/kubernetes-architect.md) — owns Helm/Kustomize packaging shape.
- [`./pin-everything.md`](./pin-everything.md) — pin the chart version (`Chart.yaml` dependencies + registry tags) alongside the image.

## Provenance

Codifies the `kubernetes-architect` remit from `CLAUDE.md` §1: "Helm/Kustomize packaging shape." Extends the house opinion #5 on pinning and declaring everything to Helm values configuration. Standard Helm production deployment practice.

---

_Last reviewed: 2026-06-05 by `claude`_
