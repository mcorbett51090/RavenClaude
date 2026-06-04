---
name: k8s-platform-ops
description: "Operate a safe multi-tenant cluster: namespace-per-tenant with scoped RBAC (no workload cluster-admin), default-deny NetworkPolicies, resource quotas/LimitRanges, policy admission control, and tested PDB-respecting upgrades."
---

# Kubernetes Platform Ops

## Tenancy
Namespace per team/app; RBAC scoped to it. **No** workload gets cluster-admin.

## Network
**Default-deny** pod-to-pod, then allow required flows. (Pairs with mesh mTLS.)

## Fairness
ResourceQuota + LimitRange per namespace so no tenant starves the cluster.

## Enforcement
Admission **policy-as-code** rejects privileged pods, missing limits, `:latest`. Preventive > detective.

## Upgrades
Deprecated-API audit -> non-prod test -> drain respecting **PDBs** -> stay within version-skew -> rollback posture.
