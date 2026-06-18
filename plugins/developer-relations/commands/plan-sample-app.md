---
description: "Plan a sample app or demo that runs as shipped and teaches one thing well — scope it to a single teaching goal, define the runs-from-clean checklist (no placeholder secrets/TODOs), pick the format for the funnel stage, name the build seam and a maintenance owner."
argument-hint: "[the capability to demo + product, e.g. 'show webhook receive+verify with our API']"
---

# Plan a sample app

You are running `/developer-relations:plan-sample-app`. Produce a demo spec for `$ARGUMENTS` — the
discipline the `sample-app-and-demo-design` skill enforces.

## When to use this

You need a sample app/demo for activation or advocacy. NOT for writing the production docs (that's
`technical-writing-docs`) or implementing the real service (route to the engineering plugin).

## Steps

1. **Name the single teaching goal** — one thing the demo proves a developer can do
   ([`../knowledge/developer-experience-and-onboarding.md`](../knowledge/developer-experience-and-onboarding.md)).
2. **Pick the format for the funnel stage** ([`../knowledge/devrel-strategy-decision-trees.md`](../knowledge/devrel-strategy-decision-trees.md)).
3. **Define the runs-from-clean checklist** — clones/installs with stated prerequisites, runs
   unmodified to a visible win, no placeholder secret/`TODO` on the happy path
   (`sample-code-must-run-as-shipped.md`).
4. **Decide the build seam** — the real code is built by the relevant engineering plugin; a security
   verdict routes to `ravenclaude-core/security-reviewer`.
5. **Name a maintenance owner** — no owner, no ship.

## Guardrails

- If you can't state the one teaching goal in a sentence, the demo is too big — cut it.
- The `Runs-as-shipped check:` line is mandatory in the output.
- Don't plan a demo whose maintenance can't be committed.
