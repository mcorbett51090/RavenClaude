---
name: module-design-checklist
description: "Pre-publish checklist and design guide for Terraform/OpenTofu modules — covers interface design, input validation, output documentation, for_each patterns, version pinning, and testability."
---

# Module Design Checklist

## When to Use This

Before publishing a new module or accepting a module PR — to verify the module meets the contract standard that allows consumers to upgrade without surprises and compose modules safely.

## 1. Interface Design

- [ ] **Single responsibility** — the module does one thing and its name states it (e.g., `s3-private-bucket`, not `data-stuff`). If the module deploys three conceptually distinct things, split it.
- [ ] **Typed variables** — every `variable` block declares a `type`. Avoid bare `any`; use `object({})` for structured inputs.
- [ ] **Defaults for optional inputs only** — required inputs have no default (Terraform will error with a clear message); optional ones have a sensible default.
- [ ] **Description on every variable and output** — the description is the API contract. It must include: what the value is, expected format/units, and any constraints.

```hcl
variable "retention_days" {
  type        = number
  description = "Log retention in days. Must be one of: 1, 3, 7, 14, 30, 60, 90."
  default     = 30

  validation {
    condition     = contains([1, 3, 7, 14, 30, 60, 90], var.retention_days)
    error_message = "retention_days must be one of: 1, 3, 7, 14, 30, 60, 90."
  }
}
```

## 2. Input Validation

- [ ] **Validate inputs at declaration time**, not at resource creation time — a `validation` block with a helpful `error_message` surfaces errors in `terraform plan`, not after 3 minutes of apply.
- [ ] **Common validations to add:**
  - CIDR blocks: `can(cidrhost(var.vpc_cidr, 0))`
  - Non-empty strings: `length(var.name) > 0`
  - Regex-constrained names: `can(regex("^[a-z0-9-]+$", var.bucket_name))`
  - Enum values: `contains(["dev", "staging", "prod"], var.environment)`

## 3. Resource Naming and Tagging

- [ ] **Expose a `name_prefix` or `name` variable** — consumers should control naming for their environment; hard-coded names break reuse.
- [ ] **Accept a `tags` variable** — always `map(string)`, merged with any module-internal required tags:
  ```hcl
  variable "tags" {
    type    = map(string)
    default = {}
  }
  # In resources:
  tags = merge(var.tags, { ManagedBy = "terraform", Module = "s3-private-bucket" })
  ```

## 4. For_each vs Count

- [ ] **Use `for_each`, not `count`, for collections** — `count` creates indexed resources; inserting or removing an item from the middle changes every subsequent index and Terraform recreates them. `for_each` keys on a stable identifier.

```hcl
# Wrong
resource "aws_iam_role" "worker" {
  count = length(var.worker_names)
  name  = var.worker_names[count.index]
}

# Right
resource "aws_iam_role" "worker" {
  for_each = toset(var.worker_names)
  name     = each.key
}
```

## 5. Outputs

- [ ] **Output every resource attribute a consumer could reasonably need** — ARN, ID, name, DNS names.
- [ ] **Never output secrets from state** — if a resource produces a secret (password, key), mark the output `sensitive = true` and document that it appears in state in plaintext.
- [ ] **Document outputs** — `description` on every `output` block.

## 6. Version Pinning

- [ ] **Pin the provider version** in `required_providers`:
  ```hcl
  terraform {
    required_version = ">= 1.5"
    required_providers {
      aws = {
        source  = "hashicorp/aws"
        version = "~> 5.0"
      }
    }
  }
  ```
- [ ] **Commit `.terraform.lock.hcl`** — ensures reproducible runs across contributors and CI.
- [ ] **Version the module itself** — callers pin to a version tag, not `main`.

## 7. Examples Directory

- [ ] **At least one `examples/` subdirectory** with a complete, runnable usage of the module.
- [ ] **The example must pass `terraform validate`** — run in CI.
- [ ] **The example should be the source for documentation** — Terraform-docs generates README from it.

## 8. Testing

- [ ] **`terraform validate`** — catches syntax and provider schema errors; zero cost; run in CI.
- [ ] **`terraform plan` against the example** — catches provider API changes and broken references.
- [ ] **Terratest or tftest** for modules with non-trivial logic — asserts that the deployed infrastructure behaves as specified (not just that the plan looks right).

## Pre-Publish Gate

```shell
# Run before opening a module PR
cd modules/<module-name>
terraform fmt -recursive -check
terraform validate
terraform-docs markdown . > README.md
cd examples/complete && terraform init && terraform validate
```

## Pitfalls

- Publishing a module with no `examples/` directory — consumers have to read the source to use it.
- Accepting `any` typed variables — callers get no editor assistance and errors are cryptic.
- Using `count` for resource sets that might have items added/removed — causes surprising resource replacement.
- Hardcoding the AWS region in a module — the consumer's provider configuration should own the region.
- Not marking sensitive outputs `sensitive = true` — the value is printed in plan/apply output and CI logs.

## See Also

- [`../../agents/terraform-module-engineer.md`](../../agents/terraform-module-engineer.md) — composable module authoring ownership
- [`../../agents/iac-architect.md`](../../agents/iac-architect.md) — module decomposition and boundaries
