---
description: "Write a composable Terraform/OpenTofu module: typed+validated inputs, documented outputs, for_each, pinned providers, an example."
argument-hint: "[what to modularize + inputs]"
---

You are running `/terraform-iac:write-module`. Use `terraform-module-engineer` + the `iac-module-design` skill.

## Steps
1. Confirm single responsibility; define typed/validated variables + documented outputs.
2. Use for_each for collections; pin required_providers.
3. Add an example that plans cleanly + a module test.
4. Route resource-argument specifics to the cloud plugin.
5. Emit the module (from `templates/module-skeleton.md`) + Structured Output block.
