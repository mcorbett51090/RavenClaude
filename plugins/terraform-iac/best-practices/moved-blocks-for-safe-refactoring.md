# Use moved blocks to safely rename or restructure resources in state

**Status:** Pattern
**Domain:** IaC / state management
**Applies to:** `terraform-iac`

---

## Why this exists

Renaming a resource in Terraform code without telling Terraform means the old resource is destroyed and a new one is created on the next apply — a destructive operation that can delete a production database or a security group with live traffic. A `moved` block is a one-line declaration that tells Terraform "the resource at address A is now at address B" — it updates the state without recreating any real infrastructure. This is the correct tool for refactoring resource addresses (renaming, moving into modules, restructuring for_each keys).

## How to apply

```hcl
# Before (old address):
# resource "aws_s3_bucket" "logging" { ... }

# After (new address — moved into a module):
# module "logging_bucket" { ... }
# which internally has: resource "aws_s3_bucket" "this"

# Migration declaration — add this alongside the module definition
moved {
  from = aws_s3_bucket.logging
  to   = module.logging_bucket.aws_s3_bucket.this
}

# Another common case: renaming within a module
moved {
  from = aws_security_group.worker
  to   = aws_security_group.node
}

# Moving from count to for_each (the most common source of unexpected destroys)
# Old: resource "aws_subnet" "this" { count = 3 }
# New: resource "aws_subnet" "this" { for_each = toset(["a","b","c"]) }
moved {
  from = aws_subnet.this[0]
  to   = aws_subnet.this["a"]
}
moved {
  from = aws_subnet.this[1]
  to   = aws_subnet.this["b"]
}
moved {
  from = aws_subnet.this[2]
  to   = aws_subnet.this["c"]
}
```

**After applying:**
```bash
# Plan shows 0 creates, 0 destroys — only state moves
terraform plan
# Confirm: "0 to add, 0 to change, 0 to destroy"
terraform apply

# Then remove the moved blocks from code (they're one-time declarations)
# Keep them for one release cycle if the module is published to a registry
```

**Do:**
- Always write a `moved` block when changing a resource's state address — even for "small" renames.
- Run `terraform plan` after adding the block and confirm the plan shows 0 destroys before applying.
- Keep `moved` blocks in published modules for one major version cycle so consumers can upgrade safely.
- Document the rename intent in a PR comment: "moved because..." helps reviewers validate.

**Don't:**
- Delete a `moved` block before all consumers of the module have applied it.
- Use `moved` for genuinely new resources — it is for existing state migration only.
- Use `terraform state mv` as the first resort — `moved` blocks are code-reviewed, auditable, and repeatable; `state mv` is a manual operation.

## Edge cases / when the rule does NOT apply

- **Actually deleting and recreating**: if the intent IS to destroy and recreate (e.g., a naming change that's faster to recreate than migrate), document the intent and schedule the destroy.
- **Resources that can be recreated from scratch in seconds with no blast radius** (e.g., a dev Lambda alias): a plan-reviewed destroy+create is acceptable if the team explicitly accepts the downtime.

## See also

- [`../agents/iac-policy-and-state-engineer.md`](../agents/iac-policy-and-state-engineer.md) — owns state surgery and safe refactoring operations.
- [`./never-edit-state-by-hand.md`](./never-edit-state-by-hand.md) — the complementary rule: `moved` blocks > `terraform state mv` > never edit the JSON.
- [`./for-each-over-count.md`](./for-each-over-count.md) — migrating from count to for_each is the most common use of moved blocks.

## Provenance

Codifies the `iac-policy-and-state-engineer` capability for "import/state-surgery operations" in `CLAUDE.md` §1. The `moved` block was introduced in Terraform 1.1 and is the canonical refactoring mechanism per the Terraform language documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
