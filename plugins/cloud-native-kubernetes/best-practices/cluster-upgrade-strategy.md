# Upgrade Kubernetes clusters incrementally — one minor version at a time

**Status:** Pattern
**Domain:** Kubernetes / platform operations
**Applies to:** `cloud-native-kubernetes`

---

## Why this exists

Kubernetes API versions are deprecated and removed on a predictable schedule (typically 3 minor versions after deprecation). Skipping minor versions during an upgrade (e.g., 1.26 → 1.29) is not supported and can leave workloads relying on removed API versions broken in ways that are not caught until apply time. Upgrading one minor version at a time gives each step a clear rollback point, surfaces one version's API removals at a time, and matches the managed Kubernetes services' (AKS, EKS, GKE) supported upgrade paths.

## How to apply

**Pre-upgrade checklist:**

```bash
# 1. Check for deprecated API usage in the cluster before upgrading
kubectl convert -f manifests/   # convert old API versions
# Or use pluto (https://github.com/FairwindsOps/pluto):
pluto detect-all-in-cluster --target-versions k8s=v1.29.0

# 2. Check deprecated APIs in Helm releases:
pluto detect-helm --target-versions k8s=v1.29.0

# 3. Review the Kubernetes changelog for the target version's removed APIs:
# https://kubernetes.io/docs/reference/using-api/deprecation-guide/

# 4. Upgrade the cluster control plane first (managed: let the provider do it)
# AKS:
az aks upgrade --resource-group rg-prod --name aks-prod --kubernetes-version 1.29

# EKS:
aws eks update-cluster-version --name prod --kubernetes-version 1.29

# GKE:
gcloud container clusters upgrade prod --master --cluster-version 1.29

# 5. Upgrade node pools ONE POOL AT A TIME after control plane
# 6. Confirm workloads are healthy after each pool upgrade
```

**Upgrade plan template:**

| Step | Action | Validate |
|---|---|---|
| 1 | Run `pluto` — fix any deprecated API manifests | All manifests use current APIs |
| 2 | Upgrade control plane to N+1 | API server responds; existing pods running |
| 3 | Upgrade first node pool (non-critical) | Pod eviction/reschedule works; HPA fires |
| 4 | Upgrade second node pool | Load balanced normally |
| 5 | Run smoke tests | Functional checks pass |
| 6 | Update `kubectl` and CI tools to match server version | No client/server skew warnings |

**Do:**
- Upgrade through each minor version (1.26 → 1.27 → 1.28 → 1.29) — don't skip.
- Keep `kubectl` within 1 minor version of the server — wider skew is unsupported.
- Drain and cordon nodes during pool upgrades; ensure PDBs allow the evictions.
- Test in staging against the same target version before upgrading prod.

**Don't:**
- Skip minor versions — it is unsupported by Kubernetes upstream and most managed services.
- Upgrade node pools before the control plane — the control plane must be newer or equal.
- Upgrade on a Friday or before a known traffic peak.
- Leave workloads using deprecated API versions until upgrade day — fix them proactively.

## Edge cases / when the rule does NOT apply

- **Managed Kubernetes services** (AKS, EKS, GKE): the provider handles control plane upgrades and may enforce a skip-version restriction automatically. Node pool upgrade sequencing still applies.
- **End-of-life versions** that require multi-step jumps: if the current version is 2+ years old, work through each minor version in a test cluster to identify API changes before tackling the full jump in prod.

## See also

- [`../agents/k8s-platform-operator.md`](../agents/k8s-platform-operator.md) — owns cluster and add-on upgrades.
- [`./admission-control-over-manual-review.md`](./admission-control-over-manual-review.md) — admission controllers must be compatible with the target version before upgrading.

## Provenance

Codifies the `k8s-platform-operator` remit in `CLAUDE.md` §1: "cluster/add-on upgrades." Standard Kubernetes cluster lifecycle management from the Kubernetes upgrade documentation and the managed service upgrade guides for AKS, EKS, and GKE.

---

_Last reviewed: 2026-06-05 by `claude`_
