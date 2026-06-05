# terraform-iac — best-practice docs

Named, citable rules for the `terraform-iac` plugin's specialists. Each file is **one rule**, grounded in this plugin's house opinions ([`../CLAUDE.md`](../CLAUDE.md)) and the decision trees in [`../knowledge/terraform-iac-decision-trees.md`](../knowledge/terraform-iac-decision-trees.md). Read a doc whole and cite it; don't paraphrase a fragment.

---

## Index

_22 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`depends-on-only-when-implicit-wont-work.md`](./depends-on-only-when-implicit-wont-work.md) | Pattern | Reviewing a Terraform resource that uses depends_on — confirm it is necessary |
| [`detect-drift-on-a-cadence.md`](./detect-drift-on-a-cadence.md) | Pattern | Scheduling drift detection to catch out-of-band changes before they compound |
| [`for-each-over-count.md`](./for-each-over-count.md) | Pattern | Creating multiple instances of a resource — use for_each to avoid reorder destroys |
| [`guardrails-as-policy-as-code.md`](./guardrails-as-policy-as-code.md) | Pattern | Encoding "no public buckets, no wildcard IAM" as preventive checks on the plan |
| [`isolate-state-by-blast-radius.md`](./isolate-state-by-blast-radius.md) | Pattern | Designing state layout — separate by lifecycle and blast radius, not org chart |
| [`keep-modules-provider-agnostic.md`](./keep-modules-provider-agnostic.md) | Pattern | Authoring a module — avoid hard-coding provider config inside the module |
| [`least-privilege-for-the-runner.md`](./least-privilege-for-the-runner.md) | Absolute rule | Configuring the IAM permissions for the Terraform runner in CI |
| [`lifecycle-prevent-destroy-for-stateful.md`](./lifecycle-prevent-destroy-for-stateful.md) | Pattern | Provisioning stateful resources — add prevent_destroy as a plan-time guard |
| [`module-is-a-versioned-contract.md`](./module-is-a-versioned-contract.md) | Absolute rule | Publishing or consuming a Terraform module — version and document the interface |
| [`moved-blocks-for-safe-refactoring.md`](./moved-blocks-for-safe-refactoring.md) | Pattern | Renaming or restructuring resources in state — use moved blocks, not state mv |
| [`never-edit-state-by-hand.md`](./never-edit-state-by-hand.md) | Absolute rule | Any state surgery — use terraform commands, never edit the JSON file directly |
| [`no-secrets-in-state.md`](./no-secrets-in-state.md) | Absolute rule | Any resource that might write a secret value into state |
| [`oidc-for-ci-no-long-lived-keys.md`](./oidc-for-ci-no-long-lived-keys.md) | Absolute rule | Configuring a CI/CD pipeline to run Terraform — use OIDC, no stored cloud keys |
| [`outputs-document-the-contract.md`](./outputs-document-the-contract.md) | Pattern | Authoring a module — every output needs a description and sensitivity declaration |
| [`pin-providers-and-modules.md`](./pin-providers-and-modules.md) | Absolute rule | Pinning module source versions to avoid unexpected upgrades |
| [`plan-is-the-review-artifact.md`](./plan-is-the-review-artifact.md) | Absolute rule | Any apply to a shared environment — the plan must be reviewed first |
| [`remote-state-with-locking.md`](./remote-state-with-locking.md) | Absolute rule | Any shared Terraform state — remote backend with locking is non-negotiable |
| [`required-providers-with-constraints.md`](./required-providers-with-constraints.md) | Absolute rule | Every Terraform configuration — declare required_providers with version constraints |
| [`sensitive-variables-never-in-tfvars.md`](./sensitive-variables-never-in-tfvars.md) | Absolute rule | Passing credentials or secrets to Terraform — never in committed tfvars files |
| [`terraform-test-for-module-correctness.md`](./terraform-test-for-module-correctness.md) | Pattern | Publishing a non-trivial module — write terraform test files before tagging |
| [`validate-and-format-in-ci.md`](./validate-and-format-in-ci.md) | Absolute rule | Every CI pipeline that applies Terraform — validate + fmt check are pre-plan gates |
| [`variable-validation-blocks.md`](./variable-validation-blocks.md) | Pattern | Authoring module inputs — validate allowed values and formats at plan time |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution + the house opinions these docs codify.
- [`../knowledge/terraform-iac-decision-trees.md`](../knowledge/terraform-iac-decision-trees.md) — decision trees for state isolation, module boundaries, backend selection, environment promotion, and tool choice.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
