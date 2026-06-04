---
name: iac-module-design
description: "Write composable Terraform/OpenTofu modules: single responsibility, typed variables with validation, documented outputs, for_each over count to avoid reorder churn, pinned provider requirements, and a working example."
---

# IaC Module Design

## One module, one job
Typed `variable` blocks + `validation`; documented `output`s; a README with an example.

## for_each, not count
`count` keys by **index** -> removing a middle element recreates the rest. `for_each` keys by a **stable id** -> no churn on reorder.

## Pin
`required_providers` with version constraints in the module; commit the **lock file** at the root.

## No secret leakage
Mark `sensitive`, source from a manager; never put a secret in an `output` (it lands in plaintext state).

## Test
Examples that `plan` cleanly + module tests (terraform test / Terratest).
