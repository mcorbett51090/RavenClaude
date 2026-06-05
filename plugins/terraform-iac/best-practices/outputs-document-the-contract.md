# Document every module output with description and sensitivity

**Status:** Pattern
**Domain:** IaC / module authoring
**Applies to:** `terraform-iac`

---

## Why this exists

A module without documented outputs is a black box. Callers either guess at the output names (and get them wrong) or read the module source to understand what it produces. A `description` field on every output costs one line and eliminates the guessing. Marking outputs that contain sensitive values (`sensitive = true`) prevents them from appearing in plan output and signals to callers that they need to handle the value carefully. This is the output-side contract to complement the typed, validated input variables.

## How to apply

```hcl
# outputs.tf — document every output
output "cluster_endpoint" {
  description = "The HTTPS endpoint of the Kubernetes API server. Use this as the --server flag for kubectl."
  value       = aws_eks_cluster.this.endpoint
}

output "cluster_certificate_authority_data" {
  description = "Base64-encoded certificate authority data for the cluster. Needed by kubectl and Helm providers."
  value       = aws_eks_cluster.this.certificate_authority[0].data
  sensitive   = false   # Not a secret, but a cert — explicit is better than absent
}

output "node_role_arn" {
  description = "ARN of the IAM role attached to EKS worker nodes. Pass to aws_eks_node_group resources."
  value       = aws_iam_role.node.arn
}

output "cluster_security_group_id" {
  description = "ID of the security group controlling cluster API access. Reference when adding ingress rules."
  value       = aws_eks_cluster.this.vpc_config[0].cluster_security_group_id
}

# Sensitive output — mark it
output "kubeconfig" {
  description = "Base kubeconfig for the cluster. Handle as a secret — do not log or commit."
  value       = local.kubeconfig
  sensitive   = true
}
```

**Description guidelines:**

| Content | What to include |
|---|---|
| What it is | One sentence: the thing being returned |
| How to use it | One clause: the flag/argument/resource that consumes it |
| Sensitivity | If sensitive, say so and what the implication is |

**Do:**
- Write descriptions in the imperative: "Use this as..." or "Pass to..." rather than "The ARN of...".
- Mark `sensitive = true` for passwords, tokens, private keys, connection strings.
- Group related outputs in `outputs.tf` — don't scatter them across resource files.
- In a module README, list outputs in a table (the `terraform-docs` tool generates this automatically).

**Don't:**
- Leave outputs with no description in a shared/published module.
- Mark everything `sensitive = true` — it makes debugging harder; only mark genuinely sensitive values.
- Output everything — only export what callers need; internal implementation details stay private.
- Use generic descriptions ("The ARN") without explaining what to do with the value.

## Edge cases / when the rule does NOT apply

- **Root modules** (not reused as a library): description is still useful for future maintainers, but the strict "every output documented" bar applies most to published/reused modules.
- **Temporary debug outputs** added during development: remove before PR merge; they add noise to the module interface.

## See also

- [`../agents/terraform-module-engineer.md`](../agents/terraform-module-engineer.md) — owns module authoring including typed outputs.
- [`./module-is-a-versioned-contract.md`](./module-is-a-versioned-contract.md) — outputs are part of the module's public API; breaking them is a semver-major change.

## Provenance

Codifies the `terraform-module-engineer` remit in `CLAUDE.md` §1: "documented outputs, single-responsibility design." Extends the "typed variables with validation" principle to the output side. Standard Terraform module authoring practice from the Terraform module registry documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
