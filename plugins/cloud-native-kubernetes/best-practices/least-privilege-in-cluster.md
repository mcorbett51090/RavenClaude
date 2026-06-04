# Apply least privilege inside the cluster

Namespaced RBAC scoped to each tenant, no cluster-admin for workloads, default-deny NetworkPolicies, non-root and unprivileged containers with dropped capabilities. A pod is a tenant and a potential foothold; a flat, open, privileged cluster turns one compromise into total east-west access.
