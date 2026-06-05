# Validate input variables with validation blocks

**Status:** Pattern
**Domain:** IaC / module authoring
**Applies to:** `terraform-iac`

---

## Why this exists

Without validation, a module caller can pass an invalid value — a region name with a typo, an environment name outside the allowed set, a CIDR block that's too large — and the error only surfaces when Terraform tries to apply a resource that fails with a cloud API error. Validation blocks check inputs before any cloud call happens, returning a clear, actionable error message to the caller. This converts a cryptic AWS/Azure/GCP API error at apply time into a "your input is wrong for this reason" error at plan time.

## How to apply

```hcl
# variables.tf — with validation blocks
variable "environment" {
  type        = string
  description = "Deployment environment. One of: dev, staging, prod."

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod. Got: '${var.environment}'."
  }
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC. Must be a /16 to /24."

  validation {
    condition     = can(cidrnetmask(var.vpc_cidr))
    error_message = "vpc_cidr must be a valid IPv4 CIDR block (e.g. 10.0.0.0/16)."
  }

  validation {
    condition = (
      tonumber(split("/", var.vpc_cidr)[1]) >= 16 &&
      tonumber(split("/", var.vpc_cidr)[1]) <= 24
    )
    error_message = "vpc_cidr prefix must be between /16 and /24. Got: /${split("/", var.vpc_cidr)[1]}."
  }
}

variable "instance_count" {
  type        = number
  description = "Number of EC2 instances. Must be 1–20."

  validation {
    condition     = var.instance_count >= 1 && var.instance_count <= 20
    error_message = "instance_count must be between 1 and 20. Got: ${var.instance_count}."
  }
}

variable "name_prefix" {
  type        = string
  description = "Resource name prefix. 3–20 lowercase alphanumeric and hyphens only."

  validation {
    condition     = can(regex("^[a-z0-9-]{3,20}$", var.name_prefix))
    error_message = "name_prefix must be 3–20 characters, lowercase letters, numbers, and hyphens only."
  }
}
```

**Do:**
- Include the invalid value in the error message (`Got: '${var.X}'`) so the caller knows what they passed.
- Write multiple validation blocks per variable when there are independent checks (valid CIDR format AND valid prefix length).
- Use `can()` to safely test functions that can fail (like `cidrnetmask`) without erroring.
- Validate before a resource-level check would catch the same error — plan-time > apply-time.

**Don't:**
- Write validations that duplicate what the cloud API checks (e.g., unique resource names) — those belong in documentation, not validation blocks.
- Make validation blocks so complex they require reading the module source to understand what they test.
- Validate optional variables with default values — only validate values the caller must provide correctly.

## Edge cases / when the rule does NOT apply

- **Very thin root modules** where the values are hard-coded or come from a single tfvars file reviewed by the author: validation adds little over code review. Apply validation to shared/reused modules first.
- **Cross-variable validations** (e.g., "subnet CIDRs must be inside the VPC CIDR"): these require a `precondition` block on a resource, not a variable `validation` block — use `lifecycle { precondition {} }` for multi-variable checks.

## See also

- [`../agents/terraform-module-engineer.md`](../agents/terraform-module-engineer.md) — owns typed variables with validation as a module-authoring principle.
- [`./module-is-a-versioned-contract.md`](./module-is-a-versioned-contract.md) — validation blocks are part of the module's public interface; changing them can be breaking.

## Provenance

Codifies the `terraform-module-engineer` remit in `CLAUDE.md` §1: "typed variables with validation." Standard Terraform module authoring practice per the HashiCorp module development guide and the Terraform variable validation documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
