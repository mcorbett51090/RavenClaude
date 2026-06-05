---
name: state-surgery
description: "Safe procedure for Terraform state manipulation — covers import, mv, rm, and state-split operations with pre/post verification steps and the rollback strategy for each operation."
---

# State Surgery

## When to Use This

Terraform's desired state diverges from actual infrastructure — resources exist but aren't in state (need import), resources moved to a refactored module (need `state mv`), resources need to be removed from management without destroying them (need `state rm`), or a monolithic state needs to be split into smaller backends.

**Never run state surgery on a shared remote backend without first:**
1. Verifying no other `apply` is in progress (the lock will prevent it, but check).
2. Taking a manual state backup.
3. Running every command as a `--dry-run` equivalent first where available.

## Pre-Surgery Checklist

```shell
# 1. Backup current state
terraform state pull > state-backup-$(date +%Y%m%d-%H%M%S).tfstate

# 2. Verify the backup is valid JSON
python3 -m json.tool state-backup-*.tfstate > /dev/null && echo "Valid"

# 3. List current resources (baseline)
terraform state list > before.txt

# 4. Confirm no in-progress apply
# (Check your backend — S3: check the DynamoDB lock table; Azure: check the blob lease)
```

## Operation 1 — Import an Existing Resource

Use when: infrastructure exists in the cloud but is not tracked in state.

```shell
# 1. Write the resource block in your .tf files first (Terraform won't import without it)
# 2. Dry run: check what will be imported
terraform plan -generate-config-out=generated.tf   # TF 1.5+ only

# 3. Import
terraform import aws_s3_bucket.my_bucket my-bucket-name

# 4. Verify: plan should show no changes
terraform plan
# Expected output: "No changes. Your infrastructure matches the configuration."
# If the plan shows changes, the .tf config doesn't match the real resource — reconcile before proceeding.
```

**Mass import:** for many resources, write a script that calls `terraform import` per resource, but verify each one individually before moving to the next.

## Operation 2 — Move a Resource (Refactoring)

Use when: renaming a resource, moving it into a module, or moving it between modules. The physical cloud resource does not change.

```shell
# Before TF 1.1: use terraform state mv
terraform state mv aws_s3_bucket.old_name aws_s3_bucket.new_name
terraform state mv aws_instance.app module.compute.aws_instance.app

# TF 1.1+: prefer the moved {} block in .tf (tracked in source control, reviewable in PR)
# In your .tf file:
moved {
  from = aws_s3_bucket.old_name
  to   = aws_s3_bucket.new_name
}
```

Prefer `moved {}` blocks — they appear in `terraform plan` output, are reviewed in a PR, and are self-documenting. `terraform state mv` is for one-off migrations not suitable for the config.

After the move:
```shell
terraform plan  # Must show: 0 to add, 0 to change, 0 to destroy
```

## Operation 3 — Remove from State (Without Destroying)

Use when: transferring management to another state file, or abandoning Terraform management of a resource that should continue to exist.

```shell
terraform state rm aws_s3_bucket.legacy_bucket
# Verify it's gone from state
terraform state list | grep legacy_bucket  # should return nothing
```

After `state rm`, the resource still exists in the cloud. If you run `terraform apply` with the resource still in your config, Terraform will try to create a new one (and likely conflict). **Remove the resource block from your config at the same time.**

## Operation 4 — Split a Monolithic State

Use when: a single state file has grown to cover too many environments or components.

```
Plan:
old-state: [vpc, eks-cluster, rds, app-1, app-2]
new-state-infra: [vpc, eks-cluster, rds]
new-state-app: [app-1, app-2]
```

Procedure:
1. Initialize new backend configurations for each target state.
2. Pull old state: `terraform state pull > old.tfstate`.
3. For each resource moving to `new-state-infra`:
   ```shell
   terraform state mv -state=old.tfstate -state-out=infra.tfstate aws_vpc.main aws_vpc.main
   ```
4. Validate each new state: `terraform state list -state=infra.tfstate`.
5. Push to new remote backends:
   ```shell
   terraform state push -force infra.tfstate  # after switching backend config
   ```
6. Do NOT push until you've verified all resources are accounted for across the new states.
7. Only then remove resources from the old state.

## Post-Surgery Verification

```shell
# After any state operation
terraform state list > after.txt
diff before.txt after.txt  # verify only intended changes

terraform plan
# Must show: "No changes" for unaffected resources
# Any unexpected diff = investigate before applying
```

## Rollback

| Operation | Rollback |
|---|---|
| Import | `terraform state rm <address>` |
| State mv | `terraform state mv` in reverse, or restore backup |
| State rm | `terraform import` to re-add the resource |
| State split | Restore from backup state; re-push to original backend |

For any operation that produces an unexpected plan, restore from backup:
```shell
terraform state push state-backup-<timestamp>.tfstate
```

## Pitfalls

- Running state surgery without a backup — the only recovery from a corrupted state is manual reconciliation of all resources.
- Using `terraform state mv` when a `moved {}` block would work — the `moved {}` block is reviewable, the CLI command is not.
- Running `state rm` without removing the resource block from config — the next plan tries to create a duplicate.
- Importing a resource without matching the `.tf` config exactly — the post-import plan will show unexpected changes; applying those can mutate the real resource.
- Doing state surgery on a backend without checking the lock — two concurrent operations can corrupt the state if the lock isn't honored.

## See Also

- [`../../agents/iac-policy-and-state-engineer.md`](../../agents/iac-policy-and-state-engineer.md) — state backend safety and drift detection
- [`../../agents/iac-architect.md`](../../agents/iac-architect.md) — state isolation by blast radius
