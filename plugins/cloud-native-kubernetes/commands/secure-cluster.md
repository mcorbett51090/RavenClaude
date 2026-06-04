---
description: "Lock down a cluster: namespaces + scoped RBAC, default-deny NetworkPolicies, quotas, and admission policy."
argument-hint: "[tenants + constraints]"
---

You are running `/cloud-native-kubernetes:secure-cluster`. Use `k8s-platform-operator` + the `k8s-platform-ops` skill.

## Steps
1. Lay out namespaces per tenant + scoped RBAC (no workload cluster-admin).
2. Apply default-deny NetworkPolicies + explicit allows.
3. Add ResourceQuota/LimitRange + admission policy (reject privileged/missing-limits/:latest).
4. Route security verdicts to security-engineering.
5. Emit manifests (from the rbac/networkpolicy templates) + Structured Output block.
