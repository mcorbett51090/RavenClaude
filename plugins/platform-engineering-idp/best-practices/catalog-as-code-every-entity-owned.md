# Catalog as code — and every entity has an owner

**Status:** Absolute rule
**Domain:** IDP / software catalog
**Applies to:** `platform-engineering-idp`

---

## Why this exists

A software catalog maintained by hand in a portal UI is stale within days — nobody updates it, so
nobody trusts it, so it dies. And an entity with no owner is, by definition, unmaintained: when it
breaks or needs a decision, there's no one to ask. Both failure modes destroy the catalog's only job:
being the authoritative answer to "who owns this and what depends on it."

## How to apply

- Keep `catalog-info.yaml` **as code, in the repo it describes**; discover via the VCS processor;
  validate in CI.
- Require an `owner` (a group) on every entity — Component, API, Resource, System. Fail CI on an
  unowned entity.
- Model from the questions developers ask (ownership, dependencies, how-to-create), not the org chart.

**Do:**

- One catalog descriptor per repo, reviewed like code.
- Enforce owner-present in CI and in the advisory hook.
- Treat the catalog as the source of truth that other tooling reads.

**Don't:**

- Edit the catalog by hand in the portal UI.
- Allow unowned entities.
- Model the whole org before anyone has a question the catalog answers.

## Edge cases / when the rule does NOT apply

A short bootstrapping period may seed the catalog via discovery/import; the rule is that the *steady
state* is as-code and owned.

## See also

- [`../templates/backstage-catalog-info.yaml`](../templates/backstage-catalog-info.yaml)
- [`./buy-or-adopt-before-you-build.md`](./buy-or-adopt-before-you-build.md)

## Provenance

Codifies Backstage's catalog-as-code model (backstage.io software-catalog docs) and the platform-
engineering consensus that ownership metadata is the catalog's load-bearing field.

---

_Last reviewed: 2026-06-08 by `claude`._
