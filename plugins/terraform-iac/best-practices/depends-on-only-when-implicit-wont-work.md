# Use depends_on only when implicit dependency is insufficient

**Status:** Pattern
**Domain:** IaC / module authoring
**Applies to:** `terraform-iac`

---

## Why this exists

`depends_on` is an escape hatch, not a default tool. Terraform's dependency graph automatically tracks which resources depend on each other when they reference each other's attributes. Explicit `depends_on` overrides this — it adds edges to the graph that Terraform cannot validate and makes the dependency opaque. Overuse of `depends_on` produces a graph that serializes operations unnecessarily, slows `apply`, and hides actual reference chains from future maintainers. It is correct only for dependencies Terraform cannot infer from attribute references.

## How to apply

**When implicit dependency (preferred):**
```hcl
# Terraform infers the dependency because aws_subnet.this.id is referenced
resource "aws_instance" "app" {
  subnet_id = aws_subnet.this.id   # implicit dep on aws_subnet.this
  # No depends_on needed
}
```

**When depends_on is correct (infrastructure not represented by attributes):**
```hcl
# An IAM policy attachment has no attribute that the role "uses" — but the role
# must have the policy before the instance that assumes it can succeed
resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.instance.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_instance" "app" {
  iam_instance_profile = aws_iam_instance_profile.this.name

  # The instance references the profile (implicit dep), but the policy attachment
  # is NOT referenced from any attribute — Terraform would apply them in parallel
  # and the instance might start before the policy is attached
  depends_on = [aws_iam_role_policy_attachment.ssm]
}
```

```hcl
# Module-level depends_on: use sparingly; it applies to EVERY resource in the module
module "app" {
  source = "./modules/app"

  # Correct: entire module must wait for the VPC module's routing to stabilize
  depends_on = [module.vpc]
}
```

**Do:**
- Add a comment explaining WHY `depends_on` is needed — the reader cannot infer it from the code.
- Prefer refactoring to add an attribute reference over adding `depends_on` if possible.
- Audit `depends_on` in code review: each occurrence is a potential smell that deserves explanation.
- Module-level `depends_on` applies to all resources in the module and forces fully-serial execution; use it only for genuine inter-module ordering.

**Don't:**
- Use `depends_on` to "be safe" when Terraform already tracks the dependency via attribute references.
- Add `depends_on` without a comment — future maintainers will remove it assuming it is redundant.
- Use `depends_on` to work around a missing attribute reference — refactor the resource reference instead.

## Edge cases / when the rule does NOT apply

- **Provisioners**: `depends_on` is commonly and correctly used with `local-exec` provisioners that run scripts using cloud resources that were just created — the script's dependency on the resource is not represented by any Terraform attribute.
- **Data sources reading post-apply state**: a `data` source that must re-read after an apply completes (e.g., re-read a secret after it was created) may need `depends_on` on the resource that created it.

## See also

- [`../agents/terraform-module-engineer.md`](../agents/terraform-module-engineer.md) — owns module authoring and dependency design.
- [`./for-each-over-count.md`](./for-each-over-count.md) — a parallel source of graph complexity; understand both before restructuring.

## Provenance

Derived from the Terraform language documentation on `depends_on` and the `terraform-module-engineer` remit in `CLAUDE.md` §1: "single-responsibility design." The explicit/implicit dependency distinction is foundational Terraform graph theory.

---

_Last reviewed: 2026-06-05 by `claude`_
