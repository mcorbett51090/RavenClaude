# Knowledge — Design-systems tooling reference (2026)

> **Retrieval date:** 2026-07-22 · **Confidence:** Medium on specifics, High on the durable
> principles. **This doc names volatile tooling — major versions, config APIs, and spec statuses
> move. Verify each entry at use** (check the tool's current docs/release notes). The *principles*
> (token tiering, composition, semver-of-a-contract, accessibility-at-v1) are durable and don't
> need a retrieval date; the *tool specifics* below do.

This is the "what's in the 2026 landscape and how the pieces fit" companion to the decision trees.
It is a map, not an endorsement — pick tools by fit, and re-verify versions/APIs before wiring.

---

## Token pipeline

| Concern | 2026 state (verify at use) | Durable principle |
|---|---|---|
| **Token source format** | The **W3C Design Tokens Community Group (DTCG)** format (`$value`, `$type`, `$description`) is the interoperability target; still evolving — check the spec status. Figma **Variables** export toward it. | One framework-agnostic source of truth, transformed to every platform. |
| **Transform tool** | **Style Dictionary** (v4-era) is the common transformer JSON → CSS vars / JS / iOS / Android; its config/transform API changes across majors. **Terrazzo** and others also transform DTCG. | Transform, never hand-duplicate tokens across platforms. |
| **Web output** | CSS custom properties (theme-swappable) + a typed TS token map so bad names fail at build. | Type the outputs; a mistyped token should fail the build, not render wrong. |
| **Theming** | Semantic-value maps scoped by `[data-theme]`/`[data-brand]` (CSS vars) or a theme object (native). | Theming is a semantic-tier value swap — never a component fork. |

## Component library

| Concern | 2026 state (verify at use) | Durable principle |
|---|---|---|
| **Accessible primitives** | Headless/unstyled primitive libraries (e.g. Radix-style, React Aria, the framework's own) provide correct roles/focus/keyboard so you don't reinvent a listbox. Availability/API varies by framework — verify. | Accessibility is table stakes at v1; build on accessible primitives. |
| **Docs / workshop** | **Storybook** (v8-era) is the common component workshop + docs; addon ecosystem and config move across majors. Alternatives: Histoire, framework-native docs. | A component without a story of its states is under-specified. |
| **API patterns** | Compound components / slots for composable parts; controlled+uncontrolled dual APIs; `forwardRef` + prop spread for escape hatches. | Composition over a prop explosion; minimal public surface. |
| **Figma→code** | Token sync (Figma Variables → DTCG → Style Dictionary) is reliable; full *component* generation from Figma remains lossy — treat generated code as a starting point, not the source of truth. | The code library is the source of truth for behavior; Figma feeds tokens. |

## Versioning, release & adoption

| Concern | 2026 state (verify at use) | Durable principle |
|---|---|---|
| **Versioning tool** | **Changesets** is the common monorepo-friendly approach (per-PR changeset → aggregated bump + changelog); semantic-release and others exist. API/config move. | Nothing ships unversioned; the changelog derives from changesets. |
| **Breaking changes** | Codemods via **jscodeshift**/**ast-grep**-style transforms shipped as a runnable command. | Ship a codemod, not just a migration guide — make the upgrade mechanical. |
| **Deprecation** | Console/lint warnings naming the replacement; keep the old API ≥1 major. | Deprecate loudly, remove slowly; the contract is sacred. |
| **Adoption metrics** | % of surfaces on the current major; token coverage (tokenized vs hardcoded); component adoption vs bespoke; escaped-hardcoded-value lint count. | Adoption is the success metric — a system nobody uses has failed. |

## Governance

- **Contribution model** — decide who can add, and gate additions on: accessible implementation +
  a minimal public API + a story + docs + a changeset. Keep the bar high; the system is
  opinionated, not a dumping ground.
- **Promotion path** — product-local component → incubation → system, gated by Tree 1
  (reused × stable × worth-standardizing).
- **Release cadence** — on-merge is fine early; move to a scheduled release train once several
  external teams consume you (reduces upgrade churn for consumers).

---

## What this reference is *not*

- **Not a WCAG conformance source** — for audit criteria, remediation, and legal posture, route to
  `accessibility-engineering`. This team *bakes in* a11y; it does not certify it.
- **Not an app-architecture guide** — building the product that consumes the system is
  `frontend-engineering`.
- **Not a brand/visual-design source** — creating the brand is `brand-identity-studio`; visual site
  design is `web-design`. This team *systematizes* those outputs into tokens and components.

> Re-verify every tool/version/spec claim above at use. The landscape moves faster than this doc.
