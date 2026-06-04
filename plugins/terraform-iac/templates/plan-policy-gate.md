# Plan policy gate (pattern)

```
terraform plan -out plan.bin
terraform show -json plan.bin > plan.json
conftest test plan.json    # OPA/Rego policies
# fail the pipeline on any violation BEFORE apply
```

Policies to start with:
- deny public storage / 0.0.0.0/0 to admin ports
- deny wildcard IAM action/resource
- require tags { owner, env, cost-center }
- require encryption at rest

Route the security verdict to security-engineering.
