# Building sites from blocks selected by features (2026)

> **Retrieved:** 2026-10-26. Product schemas are quoted from each product's own documentation on that date;
> anything seen only through a search summary is marked `[unverified]` or `[partially verified]`. The
> **architecture** in §4 is a recommendation, not any product's documented behaviour.
>
> **Worked implementation in this owner's estate:** `RavenPower-website-factory` `blocks/` +
> `scripts/compose-site.mjs` (PR #118, 2026-10-26) — 19 blocks, a feature catalog with tier page allowances, a
> generic Astro shell, a deterministic resolver with 26 must-fail self-test rows, and drift detection. Where this
> file says "the factory does X", that is what shipped there. The [`block-composed-site`](../skills/block-composed-site/SKILL.md)
> skill is the procedure for using or building a system like it.

## 0. The short version

1. **Everyone converged on one shape.** A page is an *ordered list of typed section instances*,
   `{type, props, children?}`; each type has a declared schema, good defaults, and placement rules. Shopify,
   WordPress, Sanity, Payload, Storyblok, Puck, Builder.io and Plasmic all say this in their own words, and so do
   the newer AI-UI catalogs (Vercel Labs' json-render, Google's A2UI).
2. **The section is the unit for a marketing site.** Atoms and molecules live *inside* a block; the manifest only
   ever names sections plus item arrays. Brad Frost calls atomic design "a mental model… not a linear process";
   practitioners found the atom/molecule lines "too fuzzy" and moved to "just components".
3. **The agent writes data, never markup.** It chooses sections, variants and content in a typed manifest; a
   deterministic renderer turns that into HTML; schema validation, rendered-output gates and a screenshot loop
   close it.
4. **Upgrades decide the architecture.** Copying a template per site makes every fix an N-repo edit. Keep blocks
   and renderer versioned in one place, keep each site's *authored* surface data-only, and treat each block's
   props schema as a public API (Shopify's theme-update rules are exactly that).

## 1. Prior art: the real data models

| System | Units | Props declared as | Nesting / placement | Limits & validation | Distribution & upgrade |
|---|---|---|---|---|---|
| **Shopify OS 2.0** | template → section → theme block (nest ≤ 8); section groups for header/footer | `{% schema %}` `settings[]` typed inputs (`type`, `id`, `label`, `default`, `info`); `presets` | `blocks` targeting (`@theme`, `@app`, named); `enabled_on`/`disabled_on`; static blocks for required structure | 25 sections per template, 50 blocks per section; `limit`, `max_blocks` | An update is **manual** if a setting ID is changed or removed, a type changes, or a range narrows; an invalid merchant value "will be reset to the default" |
| **WordPress block themes** | block, pattern, template part | `block.json` `attributes`, `supports`, `variations`, `example` (a fixture) | `parent`, `ancestor`, `allowedBlocks`; `supports.multiple: false`; `templateLock: contentOnly` | editor-enforced; `theme.json` `color.custom: false` restricts to presets → `--wp--preset--*` custom properties | plugins/themes; patterns copied on insert |
| **Sanity** | array members (`_type`, `_key`) | `defineType` / `defineArrayMember` | `of` allow-list | `min`, `max`, `unique`, `custom`; **renaming a member orphans existing items** | schema in code |
| **Payload** | Blocks field → block (`blockType`) | `fields[]`; `interfaceName` emits TS types | `blocks` / `blockReferences`; `filterOptions` | `minRows`, `maxRows`, `validate` | config in code |
| **Storyblok** | content-type / nestable / universal blocks | block schema in the space | `component_whitelist`, groups, tags, denylist | `minimum`, `maximum` | SaaS schema |
| **Puck** (open-source React) | component, slot, `root` | `fields` + `defaultProps` in `config` | slot `allow` / `disallow` | `resolveData`, `resolvePermissions` | npm; Puck AI "assembles pages from the components in your config" |
| **Builder.io / Plasmic** | registered code components | `inputs[]` / `props{}` (Plasmic urges "always providing `defaultValue`") | `childRequirements` / `allowedComponents` | type-level | your code + their SaaS |
| **shadcn registry** | `registry:block`, `ui`, `page`, `theme` items | the component's own TS props | `registryDependencies` | JSON Schema for item metadata | **copy-in** ("open code"); `add --diff` to review upstream changes |
| **Webflow / Framer** | components with props, slots, variants | designer UI | slots | designer UI | Webflow Shared Libraries: each site accepts updates; a detached component stops receiving them `[partially verified]` |
| **json-render / A2UI** | catalog components | Zod schemas / a catalog | flat element map with child ids | runtime prop validation | a renderer package; "A2UI is a declarative data format, not executable code" |

Sources: shopify.dev theme architecture (templates, sections, blocks, settings, theme updates); developer.wordpress.org
block.json / supports / templateLock / theme.json; sanity.io array & page-builder course; payloadcms.com blocks field;
storyblok.com docs; puckeditor.com docs; builder.io and plasmic.app registration docs; ui.shadcn.com docs and registry
schema; github.com/vercel-labs/json-render; A2UI v0.9.1 — all retrieved 2026-10-26.

## 2. Design principles that converge

1. **Sections, not atoms, in the manifest.** Expose sections plus item arrays; keep atoms as internal implementation.
2. **A small, closed prop surface.** Every prop an enum, boolean or bounded string; **no raw colours, pixel values or
   class names**; at most ~3 designed variants per block. Shopify's `custom_css` escape hatch is precisely what breaks
   its automatic upgrades.
3. **Presets and defaults.** A block renders correctly from its required content plus zero configuration.
4. **Placement rules live in the schema:** cardinality (`limit`, `multiple:false`), position (first-only for heroes),
   adjacency, required page structure (static blocks, section groups for chrome).
5. **Facts are data the block binds to,** not prose embedded in it — the same menu feeds the menu page, a home
   teaser and JSON-LD.
6. **Empty-content behaviour is explicit** — omit the section, show a placeholder only on a draft/unindexed site, or
   fail the build. This is where truth discipline becomes mechanical: an unknown fact is an empty value, never
   plausible copy.
7. **Each block owns its responsiveness** through container queries (they need `container-type` on an ancestor).
8. **Each block owns its accessibility and performance budget:** its heading level and landmark, its client JS
   (ideally 0), its LCP role.
9. **Design tokens are the only styling input.** DTCG Format 2025.10 is stable; compile tokens to CSS custom
   properties; props may select a token **role** (`tone: "night"`), never a value.

## 3. Features → blocks

A **feature** is a sellable capability ("events calendar"); a **block** is a renderable section. A feature brings in
blocks with default placements, routes, typed content collections, JSON-LD types, integrations and env, acceptance
tests, and a minimum tier.

- **Gate tiers at build time, not with runtime flags.** A runtime flag ships the paid code to every tier and hides it;
  build-time inclusion means an unpaid feature's code, routes and JSON-LD never exist in `dist/`.
- **Blocks only arrive through features.** A block may appear only if an enabled feature brings it in (or it is in a
  small base set — heroes, headers, CTAs). That one rule stops an agent from delivering a capability the customer did
  not buy. The factory also gates *variants* this way (`cta-banner:booking` needs the booking feature).
- **A purchased feature must be delivered:** each feature lists blocks that must appear somewhere ("bought menu,
  shipped no menu" is refused).
- **The tier's page allowance is a hard limit,** mirrored from the pricing source of truth; the answer to "it does not
  fit" is a tier change, never silent over-delivery.
- **Earn JSON-LD.** `Winery`, `Event`, `Menu` are real schema.org types. Google treats reviews a business controls about
  itself as **ineligible for review stars**, so a testimonials block must not emit `AggregateRating`; Google retired the
  **FAQ rich result** in 2026 — FAQ markup is harmless description, never a sold search feature.

## 4. Recommended architecture

```
purchase / tier ─► site manifest ─► RESOLVER (deterministic) ─► lock ─► RENDERER (Astro) ─► dist/ ─► GATES ─► deploy
                  (agent: content + variant choices only)  ▲
                                     catalog: blocks/*/block.json, features, tokens
```

**`block.json` fields that earn their place:** `id` + `version` (semver as a data contract); `summary` written for an
agent choosing a block (use-when / avoid-when); `placement` (position, `maxPerPage`, `notAdjacentTo`); a closed
`props` JSON Schema; `variants` (≤ ~3); the default surface/tone; `assetProps` and `linkProps` (so references can be
resolved and copied); emitted JSON-LD; an `a11y` contract (heading level, landmark); a `perf` budget (client JS, LCP
role); a `truth` list (what must never be invented in it); and — for a larger system — content binding, fixtures and
migrations.

**Resolver steps, in order:** migrate then validate the manifest (full schema) → close over features (always-on,
requires, conflicts) and **refuse** anything above the tier → plan pages (feature skeletons, then the manifest's own
pages) → allow only blocks features bring in → check composition rules (first block is the page's only h1, max per
page, adjacency, dark bands not back to back) → validate each block's props and resolve its asset and link references
→ check every purchased feature is delivered → measure the palette's text pairs against WCAG AA → refuse
placeholder text in any rendered field → emit a lock with the catalog version, per-block version + content hash and
the manifest hash. Print **every** problem at once.

**Gates:**

| Gate | Proves |
|---|---|
| Schema (JSON Schema / Zod) on catalog, features and every manifest | shape, closed enums, no unknown keys |
| Resolver must-fail fixtures — each breaks one rule in a passing manifest | every rule can still fire (a resolver that accepts everything passes the examples too) |
| Coverage — every block used by an example that CI **builds** | every component compiles |
| Rendered-output checks on `dist/` (single h1, heading ladder, alt present, budgets, no placeholder text, JSON-LD parses) | what a visitor receives, not what the source says |
| Browser pass — overflow at 320 px, targets ≥ 24 px, focus, both themes, screenshots | what static checks cannot see |
| Visual regression per block × variant × width × theme (Playwright `toHaveScreenshot`, pinned container) | variants do not regress |
| axe (`@axe-core/playwright`, WCAG 2 A/AA tags) | the automatable subset only — "automated testing cannot detect all types of WCAG violations" |
| Drift — kit-owned files are byte-identical to what the composer wrote | re-composing (the upgrade) is lossless |

**Distribution models:**

| Model | How a fix reaches 100 sites | Drift risk | Fit |
|---|---|---|---|
| Copy-in (shadcn; Wix libraries) | 100 hand merges | High — every site a fork | An explicit escape hatch, not the default |
| Generator + lockfile (Copier; template-copy + `factory.lock`) | 3-way merge per repo | Medium–high | Bespoke builds |
| **Generator + data-only authored surface + drift check** (the factory) | re-compose each site from its own manifest at the new kit commit; drift check first | Low — the lock lists every kit-owned file's hash | Separate private site repos where a private package would need auth in every repo's CI |
| Versioned package, data-only site repos (`@org/site-kit` pinned exactly) | bump one pin per site via a fleet bot | Low | Strong when the package registry is reachable from every site's CI |
| Monorepo of all sites | one commit, N builds | Lowest | Biggest move |
| Central renderer (Duda/Webflow-style hosted) | instant | Lowest, but the blast radius is everything — Duda: "make sure the change doesn't break the widget, as it affects live sites" | Hosted per-customer renders (the factory's Essential sites) |

**Rollout:** a breaking props change (rename, removal, narrowed enum or bound) is a **major** version with a data
migration — Sanity warns renames orphan data; Shopify resets invalid values to defaults. Additive props with defaults
are minor; visual fixes patch. Roll out in rings (golden examples → demo sites → ~10% of customers → the rest), with a
per-site screenshot diff against production for anything sold. **A merge is not a deployment** — confirm what each
live site actually serves.

## 5. AI-agent practices

1. **Constrained composition.** The agent's whole output is the manifest. Generate the allowed block and variant enums
   per site from the resolved features, so an out-of-catalog choice cannot be expressed.
2. **Two schemas.** Claude structured outputs reject recursive schemas, numerical constraints (`minimum`, `maximum`,
   `multipleOf`), string constraints (`minLength`, `maxLength`) and `additionalProperties` other than `false` — an
   unsupported feature is a 400 error (Anthropic structured-outputs docs, retrieved 2026-10-26). So compile a
   **generation projection** (closed enums, bounds moved into `description`, no recursion) and keep the full schema for
   **post-generation validation**, feeding errors back. Dropping the bounds silently would remove the guarantees.
3. **Stage it:** plan (sections + variants within the allowed set) → fill (one section at a time with that block's
   projection, its truth rules and the owner's data) → validate (resolver + gates).
4. **Describe blocks for routing** (use-when / avoid-when, kept short like an agent description) and keep a **golden
   manifest per business type** to few-shot from, rather than prose specs.
5. **Bind facts to sources.** Unknown facts are empty values; the block's empty policy decides what renders;
   placeholder text never reaches an indexable site. Alt text is written while **looking at the image** — the factory's
   golden example found several inherited alts describing dishes that were not in the frame.
6. **Verification loop:** build → screenshot each page at 390 and 1440 px in both themes → critique against a rubric
   (hierarchy, contrast, crop, overflow, repetition) → change **only manifest values** → at most ~3 rounds → a human
   approves before a sold site publishes.
7. **Deterministic rendering:** the same manifest, assets and kit commit produce the same output; no LLM at build time.

## 6. Pitfalls

1. Too many variants and props — the test matrix (blocks × variants × widths × themes) explodes. Cap ~3 variants.
2. Free-form escape hatches (raw HTML, custom CSS, arbitrary classes) — sites become un-upgradeable.
3. Renaming or removing a prop without a migration — data silently lost or reset.
4. Deep nesting — breaks constrained generation and multiplies placement rules; marketing sections need two levels.
5. Treating the generation schema as the validation schema.
6. Copy-in as the default distribution.
7. Auto-pushing to live sites without gates and rings.
8. Flaky screenshots — pin the container, disable animations, mask dynamic regions, baseline from CI.
9. Reading a green axe run as "WCAG AA" — keep a written list of what is not mechanized.
10. Checking source instead of output — grep for a class proves nothing about `dist/`.
11. Unearned JSON-LD (first-party ratings, FAQ "rich results").
12. Runtime tier flags on a static site.
13. Placeholders on an indexable site.
14. Header and footer repeated in every page's section list — chrome belongs in one shared shell.
15. **A frame component that drops the parent's style scope.** In Astro's default (`attribute`) scoped-style strategy
    a parent's scope arrives as a `data-astro-cid-*` *prop*; a `<Section>` wrapper that does not spread `...rest` onto
    its root makes every block style written against the block's own root class silently never match. The factory hit
    exactly this: the hero photo painted *behind* its band until the wrapper spread the attribute.
16. **Dark bands that vanish in dark mode.** A band authored dark on purpose must point at a re-pointed token
    (`--panel` steps up, `--chrome` steps down on a dark page), never the raw night material — on a dark page that
    material *is* the canvas.

## Sources

Retrieved 2026-10-26. Shopify: theme architecture (templates, sections, theme blocks, static blocks, app blocks, section
groups, settings, theme updates). WordPress: block.json metadata, supports, templateLock, theme.json, patterns,
template parts. Sanity array type and page-builder course; Payload blocks field; Storyblok blocks and blocks field;
Contentful references; Puck config / component config / data model / slots / Puck AI; Builder.io registerComponent
and child requirements; Plasmic registerComponent; Makeswift runtime. shadcn/ui docs, registry.json and
registry-item.json schemas, components.json registries, CLI. Webflow shared libraries (search summaries); Framer
variants; Astro Starlight component overrides; Astro content collections, Container API, `astro:env`. Duda widget
builder (2018); Wix Studio design libraries. Brad Frost, *Atomic Design*; Sparkbox on atomic categories; web.dev
container queries; W3C DTCG 2025.10; Playwright visual comparisons; `@axe-core/playwright`; Lighthouse CI assertions;
Renovate configuration; Copier migrations; Anthropic structured-outputs docs; OpenAI structured outputs; json-render;
A2UI v0.9.1; schema.org `Winery`; Google review-snippet and FAQ structured-data guidance.
