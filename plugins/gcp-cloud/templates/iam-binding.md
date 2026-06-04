# GCP IAM binding (pattern)

```
# Predefined role, scoped to the project, on a service account (no key file)
resource: project app-prod
member:   serviceAccount:svc-orders@app-prod.iam.gserviceaccount.com
role:     roles/run.invoker        # predefined, minimal — NOT roles/editor
condition: optional IAM Condition (time/resource)
```

Federate CI via Workload Identity Federation; GKE pods via Workload Identity. Route sensitive grants to security-engineering.
