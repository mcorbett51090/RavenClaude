# Stateless by default; StatefulSet deliberately

Most workloads are Deployments. A StatefulSet brings stable network identity, ordered rollout, and per-pod storage — and the operational complexity that comes with all three. Reach for it only when the app genuinely needs that identity/storage, not as a default.
