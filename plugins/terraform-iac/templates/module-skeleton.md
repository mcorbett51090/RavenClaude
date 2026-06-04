# Terraform module skeleton

```
modules/<name>/
  main.tf        # the resources (single responsibility)
  variables.tf   # typed + validated inputs
  outputs.tf     # documented outputs (no secrets)
  versions.tf    # required_providers with version constraints
  README.md      # what it does + an example
  examples/basic/main.tf  # plans cleanly
```

```hcl
variable "name" {
  type        = string
  description = "..."
  validation { condition = length(var.name) > 0, error_message = "name required" }
}
# use for_each, not count, for collections
```
