# Modularize the org into unlocked 2GP packages with declared dependencies — not one giant force-app

**Status:** Pattern — strong default for internal modular development; deviate only with a written reason.

**Domain:** ALM / packaging & release

**Applies to:** `salesforce`

---

## Why this exists

A single monolithic `force-app` directory deployed as "the org" has no internal boundaries: every change touches everything, every deploy re-tests everything, and ownership is impossible to assign. **Unlocked second-generation packages (2GP)** carve the org into versioned, independently-deployable modules (e.g. `Core`, `Billing`, `Sales`) whose **dependencies are declared** so installs order themselves. The payoff is upgradeability (a package version can be upgraded or removed cleanly), blast-radius control (a Billing change doesn't force a Sales redeploy), and a real bill of materials for what's in the org. The failure mode without modularization is the "big ball of mud" org where no one can deploy Billing without dragging the entire codebase — and where a cross-module reference no one declared breaks a downstream install.

## How to apply

Split `packageDirectories` by bounded module, declare upstream dependencies, and version each package independently.

```json
// sfdx-project.json — Billing depends on Core; the dependency makes installs order themselves
{
  "packageDirectories": [
    {
      "path": "core",
      "package": "Core",
      "versionName": "ver 1.4",
      "versionNumber": "1.4.0.NEXT",
      "default": true
    },
    {
      "path": "billing",
      "package": "Billing",
      "versionName": "ver 0.9",
      "versionNumber": "0.9.0.NEXT",
      "dependencies": [{ "package": "Core", "versionNumber": "1.4.0.LATEST" }]
    }
  ],
  "sourceApiVersion": "63.0"
}
```

```bash
# Create a versioned package artifact (runs with code coverage so the version is promotable)
sf package version create --package Billing --code-coverage \
  --installation-key-bypass --wait 30

sf package version promote --package "Billing@0.9.0-1"   # mark released = immutable
```

**Do:**
- Draw package boundaries on **bounded business capability**, with `Core` (shared objects, base classes) at the root of the dependency graph.
- Declare every cross-package reference in `dependencies` — an undeclared reference is a latent broken install.
- Use **unlocked** 2GP for internal modular dev; **managed** 2GP only for ISV/AppExchange (namespace + IP protection).
- Promote a version (`package version promote`) before it ships — a released version is immutable, which is what makes it trustworthy.

**Don't:**
- Let two packages depend on each other (a circular dependency can't install) — refactor the shared metadata down into `Core`.
- Put org-specific configuration (named credentials, remote settings) *inside* a package meant to be portable.
- Reach across a package boundary without a declared dependency.

## Edge cases / when the rule does NOT apply

Not every org needs modularization: a small org with one team and a low change rate is fine as a single source-tracked project — the dependency-ordering rule still applies, the *package split* does not. Some metadata types are **not packageable** in 2GP (`[verify-at-build]` against the current MDC coverage list); those ship as source through the same pipeline. Managed-package conversion of an existing unlocked package is a one-way decision — model it deliberately, not as a late retrofit.

## See also

- [`package-and-deploy-in-dependency-order.md`](./package-and-deploy-in-dependency-order.md) — the dependency-ordered deploy these packages feed
- [`alm-scratch-orgs-and-source-tracking.md`](./alm-scratch-orgs-and-source-tracking.md) — where package source is authored
- [`../knowledge/packaging-and-deployment.md`](../knowledge/packaging-and-deployment.md) — unlocked vs managed and versioning
- [`../templates/sfdx-project-manifest.md`](../templates/sfdx-project-manifest.md) — the `sfdx-project.json` skeleton
- [`platform-org-strategy-and-environments.md`](./platform-org-strategy-and-environments.md) — single- vs multi-org, the next decision up

## Provenance

Codifies house opinion #15 and the `salesforce-platform-architect`'s packaging discipline. Grounded in [`../knowledge/packaging-and-deployment.md`](../knowledge/packaging-and-deployment.md) and Salesforce's 2GP unlocked-package and dependency documentation. Packageable-metadata coverage and CLI flags are version-sensitive — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
