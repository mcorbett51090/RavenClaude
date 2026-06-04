---
description: "Design the IaC estate: module decomposition, state isolation by blast radius, promotion model, and repo layout."
argument-hint: "[environments + change cadence + pain]"
---

You are running `/terraform-iac:design-iac-structure`. Use `iac-architect` + the `iac-module-design` skill.

## Steps
1. Traverse the state-isolation tree; split by lifecycle/blast-radius.
2. Choose a promotion model (dir/workspace/Terragrunt) and name the trade.
3. Decompose modules by responsibility; decide Terraform vs OpenTofu.
4. Emit the repo layout (from `templates/iac-repo-layout.md`) + Structured Output block.
