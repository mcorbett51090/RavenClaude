# Develop in scratch orgs with source tracking — sandboxes are not the source of truth

**Status:** Pattern — strong default for package/feature development; deviate only with a written reason.

**Domain:** ALM / packaging & release

**Applies to:** `salesforce`

---

## Why this exists

A developer sandbox is a long-lived, mutable org whose state drifts: someone clicks a setting, an admin adds a field, and now "works in the sandbox" no longer means "is in the repo." Scratch orgs are **disposable, source-defined** orgs spun up from a `scratch-def` file and torn down at the end of the work item. Because every scratch org starts identical, the org's shape lives in version control — not in an org nobody can reproduce. Source tracking (`sf project retrieve/deploy --source-tracking`) tells you exactly what diverged between org and repo, which is the whole point of a source-driven pipeline (house opinion #15). Without scratch orgs, the first failure mode is undetected config drift; the second is an onboarding cost measured in days because no one can recreate the dev environment.

## How to apply

Define the org shape once, create disposable orgs from it, and let source tracking keep repo and org honest.

```bash
# config/project-scratch-def.json defines the org shape (edition, features, settings)
sf org create scratch --definition-file config/project-scratch-def.json \
  --alias feat-billing --duration-days 7 --set-default

# Push the repo into the fresh org, then pull back ONLY what you changed in the UI
sf project deploy start --source-dir force-app          # repo -> org
sf project retrieve start --source-tracking             # org -> repo (just the diffs)

# See what diverged before you trust the org
sf project deploy preview                               # dry-run: what would deploy

sf org delete scratch --target-org feat-billing --no-prompt   # tear down when done
```

```json
// config/project-scratch-def.json — the org's shape, in version control
{
  "orgName": "Acme Billing Dev",
  "edition": "Developer",
  "features": ["EnableSetPasswordInApi", "PersonAccounts"],
  "settings": { "lightningExperienceSettings": { "enableS1DesktopEnabled": true } }
}
```

**Do:**
- Keep the `scratch-def` file in version control — it *is* the org definition.
- Use source tracking so retrieve/deploy moves only the actual diffs, not the whole org.
- Tear scratch orgs down at the end of the work item; recreate, don't preserve.
- Seed test data from a repo-tracked plan (`sf data import tree`), not by hand.

**Don't:**
- Treat a shared developer sandbox as the canonical state — it drifts the moment two people touch it.
- Make config changes only in the org and forget to `retrieve` them into the repo.
- Hard-code an org-specific ID/URL into a scratch-def or seeded data set.

## Edge cases / when the rule does NOT apply

Scratch orgs require Dev Hub and don't carry production data volume or all licenses, so **performance/LDV testing, UAT, and full-data regression** belong in a sized sandbox (Partial/Full copy), not a scratch org. Some managed-package or licensed features aren't enabled in scratch editions — verify feature availability `[verify-at-build]`. Long-lived integration/UAT environments are legitimately sandboxes; the rule is about *development* and *package authoring*, where reproducibility matters most.

## See also

- [`package-and-deploy-in-dependency-order.md`](./package-and-deploy-in-dependency-order.md) — what the source-tracked project ships into
- [`alm-2gp-unlocked-package-modularization.md`](./alm-2gp-unlocked-package-modularization.md) — the package the scratch org validates
- [`../knowledge/packaging-and-deployment.md`](../knowledge/packaging-and-deployment.md) — the pipeline this feeds
- [`../skills/salesforce-release-pipeline/SKILL.md`](../skills/salesforce-release-pipeline/SKILL.md) — step 1 (source of truth)
- [`../templates/sfdx-project-manifest.md`](../templates/sfdx-project-manifest.md) — the `sfdx-project.json` skeleton

## Provenance

Extends house opinion #15 ("prod is deployed to, never clicked in") and the `salesforce-platform-architect`'s "if it isn't in a package and a pipeline, it isn't real." Grounded in [`../knowledge/packaging-and-deployment.md`](../knowledge/packaging-and-deployment.md) and the Salesforce DX scratch-org / source-tracking documentation. Scratch-def feature lists and editions are version-sensitive — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
