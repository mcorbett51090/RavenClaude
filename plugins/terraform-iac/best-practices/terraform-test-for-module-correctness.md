# Write terraform test files for every non-trivial module

**Status:** Pattern
**Domain:** IaC / module testing
**Applies to:** `terraform-iac`

---

## Why this exists

Terraform modules without tests rely on `plan` output review and production apply as the feedback loop — the first failure is in a real environment. The native `terraform test` framework (GA since Terraform 1.6) runs HCL test files against real infrastructure with setup/teardown, checks assertions on resource attributes, and tears down the resources after the test. A module with a test file proves that the module applies cleanly, outputs the expected values, and handles the edge-case variable inputs. This is especially important for modules published to a private registry — a consumer who calls `module.foo` expects it to work, not to discover a missing required provider at apply time.

## How to apply

```hcl
# tests/unit.tftest.hcl — basic module test
variables {
  name   = "test-bucket"
  region = "us-east-1"
  tags   = { environment = "test" }
}

# 'run' block: apply the module and check assertions
run "creates_bucket_with_correct_name" {
  command = apply

  assert {
    condition     = aws_s3_bucket.this.bucket == "test-bucket"
    error_message = "Bucket name should match the var.name input"
  }

  assert {
    condition     = aws_s3_bucket.this.tags["environment"] == "test"
    error_message = "Environment tag should be passed through"
  }
}

run "blocks_public_access" {
  command = plan   # plan-only check — faster, doesn't create resources

  assert {
    condition     = aws_s3_bucket_public_access_block.this.block_public_acls == true
    error_message = "Public ACLs must be blocked"
  }

  assert {
    condition     = aws_s3_bucket_public_access_block.this.block_public_policy == true
    error_message = "Public policy must be blocked"
  }
}
```

```bash
# Run tests (creates + destroys real infra for 'apply' runs)
terraform test

# Run only plan-mode tests (fast, no real resources)
terraform test -filter=tests/unit.tftest.hcl
```

**Module test structure:**

```
modules/s3-bucket/
├── main.tf
├── variables.tf
├── outputs.tf
├── README.md
└── tests/
    ├── unit.tftest.hcl    # plan-mode assertions — fast
    └── e2e.tftest.hcl     # apply-mode — creates real resources
```

**Do:**
- Use `command = plan` for assertions that can be checked without creating resources (resource count, attribute values from inputs).
- Use `command = apply` for assertions that require the resource to exist (ARNs, computed attributes).
- Keep `command = apply` tests in a CI stage that runs against a dedicated test account/project.
- Write at least one plan-mode test for every module — it's fast and catches the most common errors.

**Don't:**
- Skip tests for "simple" modules — a 10-line module with an untested `for_each` expression is a subtle bug waiting.
- Use `command = apply` tests in pipelines that run against a shared production-adjacent account.
- Test only the happy path — add a test for the edge-case variable (empty list, `null` optional) that breaks a `for_each`.

## Edge cases / when the rule does NOT apply

- **Root modules** (environment-specific wiring, not reused): integration tests via plan review + a staging-environment apply are the appropriate test strategy, not `terraform test`.
- **Very thin wrapper modules** (one resource, no logic): plan-mode assertions covering the key attributes are sufficient; skip full apply tests.

## See also

- [`../agents/terraform-module-engineer.md`](../agents/terraform-module-engineer.md) — owns module authoring and testing.
- [`./module-is-a-versioned-contract.md`](./module-is-a-versioned-contract.md) — tests are part of the module contract; a semver bump without updated tests is incomplete.

## Provenance

Codifies the `terraform-module-engineer` remit in `CLAUDE.md` §1: "module testing" and the capability map entry for `terraform test` (GA since 1.6). Derives from HashiCorp's official `terraform test` documentation and the module authoring guide.

---

_Last reviewed: 2026-06-05 by `claude`_
