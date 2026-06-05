# Run terraform validate and fmt check in every CI pipeline

**Status:** Absolute rule
**Domain:** IaC / CI quality
**Applies to:** `terraform-iac`

---

## Why this exists

`terraform validate` catches configuration errors (missing required fields, invalid references, type mismatches) before a plan is run against a real cloud account. `terraform fmt -check` enforces canonical formatting so diffs are always meaningful — a pure formatting change mixed into a substantive change makes review harder. Both commands are fast (no cloud API calls), free, and catch a class of errors that waste pipeline time and reviewer attention. A pipeline that applies without validating first is a pipeline that discovers syntax errors at the worst possible moment.

## How to apply

```yaml
# GitHub Actions — validate + fmt check on every PR
name: terraform-validate
on:
  pull_request:
    paths:
      - '**.tf'
      - '**.tfvars'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "~1.8"

      - name: Terraform Init
        run: terraform init -backend=false   # no backend needed for validate
        working-directory: ${{ env.TF_WORKING_DIR }}

      - name: Terraform Format Check
        run: terraform fmt -check -recursive
        # Fails if any .tf file is not canonical format

      - name: Terraform Validate
        run: terraform validate
        working-directory: ${{ env.TF_WORKING_DIR }}
```

Fix formatting locally before pushing:
```bash
# Auto-fix all .tf files in the repo
terraform fmt -recursive
```

**Do:**
- Run `fmt -check` across the entire repo recursively — not just the module being changed.
- Run `validate` with `init -backend=false` so the check is fast and needs no cloud credentials.
- Fail the PR if either check fails — enforce, don't warn.
- Add `tflint` for provider-specific linting after validate passes.

**Don't:**
- Run `terraform fmt` with `-write=true` in CI — CI should fail on violations, not silently fix them (hides issues from reviewers).
- Skip `fmt -check` because "it's just formatting" — inconsistent formatting is a consistent source of misleading diffs.
- Run `validate` only on the root module — validate each module independently in a monorepo.

## Edge cases / when the rule does NOT apply

- **Generated Terraform code** (from tools like `terraformer` or `tf2pulumi`): auto-format generated output before committing, then apply the same rule.
- **Local-only experiments** not in a shared repo: the rule enforces before merge; pre-commit hooks are the local complement.

## See also

- [`../agents/iac-architect.md`](../agents/iac-architect.md) — owns the CI pipeline strategy for IaC.
- [`./plan-is-the-review-artifact.md`](./plan-is-the-review-artifact.md) — validate + fmt are the pre-plan checks; plan is the review gate.

## Provenance

Codifies the `terraform-iac` house opinion #4 in `CLAUDE.md` §2: "Plan is the review artifact. Never apply what you didn't read in a plan." Validate + fmt are the prerequisite gates before a plan is even run. Standard Terraform CI practice from HashiCorp's CI/CD guide.

---

_Last reviewed: 2026-06-05 by `claude`_
