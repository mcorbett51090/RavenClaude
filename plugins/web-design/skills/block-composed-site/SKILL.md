---
name: block-composed-site
description: Build or extend a website from a catalog of section blocks selected by the features a customer bought, so the agent writes a typed manifest instead of markup. Covers the block contract, feature-to-block mapping with tier page allowances, the deterministic resolver rules, rendered-output gates, drift detection and upgrade rollout. Used by web-architect and frontend-implementer.
---

# Skill: block-composed-site

**Purpose:** make per-site work *data entry* — choosing blocks, variants and real content in one manifest — while a
versioned catalog and a deterministic composer own the markup, the accessibility structure and the upgrades. Primary
agents: `web-architect` (catalog, features, tiers, distribution), `frontend-implementer` (blocks, shell, gates);
`content-strategist` fills the content; `visual-designer` owns the token roles blocks consume.

Backing knowledge: [`../../knowledge/block-based-site-composition-2026.md`](../../knowledge/block-based-site-composition-2026.md)
(prior-art data models, principles, architecture, gates, distribution, AI-agent practices, pitfalls).

## When to use

- Many sites for many small businesses share the same kinds of sections (hero, menu, services, gallery, events,
  contact, hours) — the agency/factory case.
- A customer buys features or a tier, and what gets built must match what was sold.
- A section fix has to reach sites that already shipped.

Not for: a one-off bespoke site with layouts no block covers (build it directly via `static-site-implementation`), an
app-grade frontend (`frontend-engineering`), or a CMS integration choice (`information-architecture`).

## Mode A — Use an existing catalog (the common case)

If the project has a composer (e.g. the owner's `RavenPower-website-factory`: `node scripts/compose-site.mjs catalog |
scaffold | check | build`, brief `briefs/block-site-agent-brief.md`):

1. **Read the catalog first** — features with tier minimums and status, blocks with use-when summaries. A feature marked
   template-only or planned cannot be composed: report it, do not approximate it with other blocks.
2. **Scaffold from the purchased features and tier.** Every content field starts empty, so the check fails until it is
   filled from real facts.
3. **Fill from verified facts only.** Unknowns go to the owner to-do list, never into a rendered field. Write each image's
   alt text while looking at the image. Record each image's provenance (business-own, licensed-stock, generated).
4. **Check until clean** — the composer prints every problem at once. Fix the manifest, never the composer.
5. **Build, then gate the rendered output** (floor, budget, type check, drift, provenance), then the browser pass from
   the [`interface-craft`](../interface-craft/SKILL.md) skill's Step 3 at 390 and 1440 px in both themes.
6. **Iterate only in the manifest** (copy length, variant, block order, image focal point) — at most three rounds.
   Never hand-edit a generated file; the next compose overwrites it and the drift check reports it.

## Mode B — Design or extend a catalog

### B1. The block contract (one `block.json` per block)

| Field | Why |
|---|---|
| `id`, `version` (semver) | A props change is a data-contract change; the lock records versions so a fleet scan can find old copies |
| `summary` | Written for an agent choosing a block — what it is for, when not to use it — kept short like an agent description |
| `headingLevel`, `placement` (`position`, `maxPerPage`, `notAdjacentTo`) | Exactly one level-1 block per page, first, makes the single-h1 and no-skip rules hold by construction |
| `tone` default (+ `locked` for full-bleed photography) | Surfaces are decided at page level; the resolver can refuse two dark bands back to back |
| `props` — a closed JSON Schema | No unknown keys, bounded strings, enums; **no colour, size or class props** |
| `variants` (≤ ~3, designed) | Deliberate alternatives, not a styling escape hatch |
| `assetProps`, `linkProps` | References can be resolved, copied and checked |
| `schemaOrg`, `a11y`, `perf`, `truth` | Each block states what it emits, guarantees, costs and must never invent |

Components read only semantic tokens, use `@container` queries, render inside a shared section frame (which must
**spread the parent's scope attribute** — see the pitfalls), and take the page's heading id so the section is
`aria-labelledby` its own heading.

### B2. Features and tiers

- One catalog of features: pages and blocks each brings, `mustInclude` groups (and `block:variant` gating), required
  data, minimum tier, status, and the vocabulary shared with the pricing/commerce side (same ids, so a customer's purchase
  maps to blocks without a translation table).
- A tier table with **page allowances mirrored from the pricing source of truth**, labelled as a copy.
- A small base set of blocks any site may use (heroes, headers, CTAs); every other block arrives only through a feature.

### B3. The resolver (deterministic, no LLM; prints every problem)

Refuse: unknown or not-ready features; a feature above the tier; more pages than the allowance; a block no enabled
feature brings in; a gated variant without its feature; a purchased feature not delivered; first block not level-1; max
per page; adjacency; two dark bands back to back; invalid or unknown props; dangling asset, link or font references;
palette text pairs below WCAG AA (on the hexes — composited contrast stays a browser job); placeholder text
(`TODO`, `TBD`, lorem ipsum, template braces) in any rendered field. Emit a lock with the catalog version, each block's
version and content hash, the manifest hash and a hash of every kit-owned file.

### B4. Gates (prove each can fail)

- Self-test: for every resolver rule, a must-fail row that breaks only that rule in a copy of a passing fixture and
  asserts the rule is named; catalog must-fail rows (id/dir mismatch, unknown block reference, missing component,
  unsupported schema keyword).
- Coverage: every block is used by an example **that CI builds**, or its component has never been compiled.
- CI composes and builds the examples, then runs rendered-output gates on `dist/` and a drift round-trip
  (hand-edit → detected → re-compose → clean).
- Writer and provenance gate tested against each other when they live in different languages.

### B5. Distribution and upgrades

Pick deliberately (table in the knowledge file). Where site repos are separate and a private package would need auth in
every site's CI, the factory's model works: the site's authored surface is the manifest plus its images; everything else
is regenerated from the kit at a recorded commit, so `build --site <dir>` is a lossless upgrade and the lock's kit-owned
hashes detect hand edits first. Breaking props changes are major versions with a data migration; roll out in rings; a
merge is not a deployment.

## Pitfalls (each one was hit in the factory build)

- **The frame component drops the scope attribute** → block root styles never match (the hero photo painted behind its
  band). Spread `...rest` onto the frame's root element.
- **The page renderer forces a default tone** → every block's own default surface is overridden. Pass `tone` through
  unset.
- **Dark bands vanish in dark mode** → point them at re-pointed tokens (panel steps up, chrome steps down), not the raw
  night material.
- **Lock keys named after files** → `src/styles/tokens.css` tripped a "key named like a secret" provenance rule. Store
  per-file hashes as `sha256sum`-style strings, not as object keys.
- **Case-insensitive placeholder detection** refuses real copy ("Todos Santos"). Match `TODO`/`TBD`/`XXX` as uppercase
  words.
- **Inherited alt text** describing dishes that are not in the frame. Re-write alt by looking at each photo.
- **A scaffold that adds a second CTA** before an existing one trips the adjacency rule — upgrade the existing block's
  variant instead.
