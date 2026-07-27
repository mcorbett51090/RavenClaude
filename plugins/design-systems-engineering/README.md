# design-systems-engineering

A **design-systems engineering team** for RavenClaude — the team that owns the shared system every
product surface builds from: design tokens, the component library, documentation, and the
versioning/governance machinery that keeps many screens feeling like one product.

## Who this is for

- Design-system leads, staff/senior frontend engineers, and design-engineering hybrids standing up
  or scaling a design system.
- Teams with 2+ product surfaces (or brands) that have started to drift and need a single source of
  truth.
- Anyone deciding token structure, component API shape, or how to version and roll out a shared
  library without breaking consumers.

## Agents

| Agent | Owns | Reach for it when |
|-------|------|-------------------|
| **design-systems-architect** | The decisions — token tiering, theming/multi-brand, component API philosophy, system-vs-product boundaries, versioning & governance model | "How should our tokens be structured?" · "Composition or props for this component?" · "How do we support two brands?" · "What's our versioning/deprecation policy?" |
| **design-tokens-and-component-engineer** | The build — token pipelines (Style Dictionary / Figma→code), accessible component implementation, Storybook/docs, the release pipeline (semver, changesets, codemods), adoption tooling | "Build the token pipeline" · "Implement an accessible `Menu`" · "Set up changesets + the release flow" · "Ship a codemod for this breaking change" |

## Skills

- **design-token-architecture** — structure tokens across the primitive → semantic → component
  tiers, with theming/dark-mode and multi-brand as a token swap.
- **component-api-and-library-build** — design and build an accessible, composable component with a
  contract-grade public API, story, and docs.
- **design-system-versioning-and-adoption** — version the library (semver + changesets), manage
  breaking changes with codemods and deprecation, and drive adoption.

## Knowledge bank

- [`knowledge/design-systems-decision-tree.md`](knowledge/design-systems-decision-tree.md) — a
  Mermaid decision tree from "should this live in the system?" through token tier, component API
  shape, theming strategy, and versioning policy.
- [`knowledge/design-systems-reference-2026.md`](knowledge/design-systems-reference-2026.md) — a
  dated reference of the 2026 tooling landscape (Style Dictionary, Storybook, changesets, token
  formats) with retrieval-date + verify-at-use discipline.

## Boundaries

This team owns the **system**, not the surfaces that consume it. Building an app or feature →
`frontend-engineering`. A WCAG conformance audit → `accessibility-engineering`. Site/brand visual
design → `web-design`. Creating a brand from scratch → `brand-identity-studio`.

## Requires

`ravenclaude-core@>=0.7.0`. No external runtime dependencies. Tooling/version specifics are
volatile — the reference doc is retrieval-dated; verify at use.

## Install

```
/plugin marketplace update ravenclaude
/plugin install design-systems-engineering@ravenclaude
```
