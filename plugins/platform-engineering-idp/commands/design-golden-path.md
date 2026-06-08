---
description: "Author a golden path / paved road: scope the supported create-build-deploy-run journey, bake in defaults (CI, observability, security baseline, ownership), make it the easiest way, and design the escape hatch."
argument-hint: "[the common service shape, e.g. 'stateless Node HTTP service deployed to our EKS cluster']"
---

You are running `/platform-engineering-idp:design-golden-path`. Use the `golden-path-engineer`
discipline and the `golden-path-design` skill.

## Steps

1. Confirm there's an ~80% common shape worth paving (if all bespoke, gather the common shape first).
2. Traverse the golden-path-scoping tree; scope create -> build -> deploy -> run.
3. Bake in defaults: CI wiring, observability, security baseline, owner + catalog entry.
4. Verify the supported way is the *easiest* way; remove friction until it is.
5. Design the escape hatch (allowed + unsupported) and the rule for folding recurring escapes into new
   variants.
6. Fill `templates/golden-path-spec.md`; hand the create step to idp-portal-engineer, the pipeline to
   devops-cicd, the modules to terraform-iac/cloud-native-kubernetes; emit the Structured Output block.
