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

## Multi-site section libraries — distribution and upgrades

> Added 2026-10-26. The case: one library of page sections ("blocks" — hero, menu, gallery, contact) feeds **many small
> sites**, each in its own repo, often for different customers. The fuller treatment (block contract, feature-to-block
> mapping, resolver rules, gates) is web-design's
> [`block-based-site-composition-2026.md`](../../web-design/knowledge/block-based-site-composition-2026.md); this
> section is the versioning and distribution half, which is this team's job.

A section library is a component library whose consumers are sites, not apps — so the same contract rules apply, but
the distribution choice dominates the cost of every later fix.

| Model | How a fix reaches a shipped site | Cost | Fits when |
|---|---|---|---|
| **Copy-in** (shadcn-style) | It doesn't — each site owns its copy | Lowest to start; fixes never propagate | Sites are expected to diverge and nobody maintains them centrally |
| **Generator + lock** | Re-run the generator; the lock records what was emitted | Hand edits get overwritten unless detected | A small team owns every site |
| **Generator + data-only authored surface + drift check** | `build --site` regenerates everything except the site's data (a manifest + its images); hashes of kit-owned files in the lock detect hand edits first | Needs a deterministic generator and a drift gate | Many sites, separate repos, private kit — no package auth needed in each site's CI |
| **Versioned package** (npm, private registry) | Bump the dependency; codemod for majors | Registry auth in every site's CI; one install per site | Sites are apps with their own build and a team per site |
| **Monorepo** | One commit, every site rebuilt | Every site in one repo and one CI | One owner, sites never handed to customers |
| **Central renderer** (headless CMS / page service) | Deploy the renderer once | A runtime dependency per site; outage = every site | Content changes often; sites can tolerate a shared runtime |

**Rules that hold for every model:**

- **A block's props are a data contract.** Semver it: a new optional prop is minor; a renamed, removed or newly required
  prop is major and ships with a **data migration** (the codemod's equivalent for manifests), not a guide.
- **Record what each site was built from** — the library version, each block's version and content hash, and the
  generator commit — so a fleet scan can answer "which sites still have the old hero?" without opening each one.
- **Detect hand edits before you overwrite them.** An upgrade that silently discards a customer-requested tweak breaks
  trust faster than one that refuses and lists the edited files.
- **Roll out in rings** — an internal site, then a few customers, then the fleet — and keep the previous version
  buildable until the last ring lands.
- **Allow deliberate ejection.** A site that needs a bespoke section marks it as site-owned; the drift check then skips
  it and the upgrade report lists it, rather than the library growing a prop for one customer.
- **Merge is not deployment.** A fix merged to the library reaches no customer until each site is rebuilt and deployed;
  track that per site, not per merge.

---

## What this reference is *not*

- **Not a WCAG conformance source** — for audit criteria, remediation, and legal posture, route to
  `accessibility-engineering`. This team *bakes in* a11y; it does not certify it.
- **Not an app-architecture guide** — building the product that consumes the system is
  `frontend-engineering`.
- **Not a brand/visual-design source** — creating the brand is `brand-identity-studio`; visual site
  design is `web-design`. This team *systematizes* those outputs into tokens and components.

> Re-verify every tool/version/spec claim above at use. The landscape moves faster than this doc.
