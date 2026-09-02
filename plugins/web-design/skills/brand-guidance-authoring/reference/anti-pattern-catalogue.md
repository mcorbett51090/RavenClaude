# Anti-pattern catalogue — the observable "AI slop" list

**Owning skill:** [`brand-guidance-authoring`](../SKILL.md). Read by [`brand-polish-checklist.md`](brand-polish-checklist.md) and copied into every project's own `brand-guidance.md` (§7) via [`../templates/brand-guidance.md`](../templates/brand-guidance.md).

Ten rows. Every row is an ID + a **default-banned pattern** + an **observable form** (never adjectival —
something a checklist pass or a grep can actually match) + why it reads as generic + the positive
replacement + a per-project `override` block. This file ships every row `enforced`; a project's own
generated `brand-guidance.md` is where a project relaxes one, with a required rationale.

**Absorbs, does not duplicate,** four rows from [`design-references.md`](../../../knowledge/design-references.md)'s
existing §"Avoid — 2024 tropes that already look dated" — that file now points here as the canonical,
per-project-overridable version (`web-design/CLAUDE.md` §3 rule 12: one source of truth per design
decision).

> A future automated gate over "banned patterns" must exempt this file's own path from any
> pattern-matching scan — its job is to *state* the banned patterns, so a naive grep over "the whole
> repo" would flag this file for containing the very words it defines. This is the repo's own recurring
> source-scan-gates-match-prose failure mode; naming it here is the exemption.

## The override mechanism

Every row a project inherits into its own `brand-guidance.md` carries:

```yaml
override:
  status: enforced | relaxed | replaced
  rationale: "<one line — required when status != enforced>"
```

- `enforced` (the default) — the pattern stays banned for this project.
- `relaxed` — the project deliberately allows it, with a one-line reason. A `relaxed` row with an empty
  `rationale` is a structural fail at the pipeline's G3 gate.
- `replaced` — the project substitutes its own equivalent rule in place of this row (rare; still needs a
  rationale naming the substitute).

A `relaxed` or `replaced` row never trips [`brand-polish-checklist.md`](brand-polish-checklist.md) — the
checklist cannot overrule an explicit, rationalized project decision.

## The catalogue

| ID | Banned by default | Observable form | Why it reads as generic | Positive replacement |
|---|---|---|---|---|
| `AP-01` | Generic-sans as the **brand voice / display** face — Inter, Roboto, Open Sans, Arial, `system-ui` | The display/heading typeface resolves to one of the named families. **Scope is limited to the identity-carrying face** — these families are NOT banned as a UI, data, tabular, or system-fallback face; see the "Live tension — Inter" note in `design-references.md` for the one file that still recommends Inter, and why that recommendation is not overwritten here. | Every agent-generated site defaults to the same two or three system faces when nothing else is specified; a shared display face is the fastest visual tell of an unstyled build. | A distinctive display face (a licensed or well-supported variable font) paired with a readable body face — two typefaces, never more. |
| `AP-02` | Indigo→purple (or violet→fuchsia) hero gradient; "AI shimmer / silver halo" | A multi-stop gradient whose color stops fall in the 250–300° hue band, applied to a hero or section background. | This exact gradient family is the single most-cited visual signature of default agent output — it is not a brand choice, it is the absence of one. | A flat surface color from the project's own token palette, or a gradient built from the project's own brand hue (never a generic purple/indigo pair). |
| `AP-03` | 3-column icon-over-heading-over-paragraph feature grid | A 3-column grid whose cells are each exactly `icon + h3 + p`, with no other content type mixed in. | The "three feature cards" layout is the default shape an agent reaches for when asked to list capabilities — recognizable at a glance regardless of the copy inside it. | A different page shape entirely for the same content: a bento asymmetric grid (used once, not per §Avoid), a stat-led list, a manifesto-style long paragraph, or a comparison table. |
| `AP-04` | Card-in-card / nested large-radius containers | A container with `border-radius ≥ 12px` whose direct child also has `border-radius ≥ 12px` and its own background fill. | Nesting rounded cards inside rounded cards is a shadcn-default look applied with no restyling — the tokens were never changed from the library's defaults. | One radius stance per page (sharp, one soft radius, or pills — never mixed); a nested surface uses a hairline border or no visual boundary at all instead of a second rounded fill. |
| `AP-05` | Centered `100vh` hero over a stock photograph | Hero section height ≥ 90vh, `text-align: center`, background is a photographic asset that does not depict the actual product. | The centered-hero-over-stock-photo shape (often paired with an auto-playing 3D scene) is a template default, not a considered choice — it says nothing about what the product actually is. | A type-led hero sized to its content, a real product screenshot, or no photography at all. |
| `AP-06` | Fabricated metrics / invented social proof | Any numeral presented as a customer count, uptime percentage, star rating, or "trusted by" claim with no cited source. | Invented numbers are a common agent-generated filler pattern and are actively misleading, not just generic. | Real, sourced metrics only; omit the section entirely if none exist yet. |
| `AP-07` | Bento grid applied to more than one section | Two or more sections on the same page use an asymmetric, mixed-span tile grid. | *Absorbed from `design-references.md` §Avoid.* A layout technique that is distinctive once becomes a template the moment it repeats — the second bento section reads as "the theme's grid," not a design decision. | Reserve the bento treatment for exactly one section per page; every other section uses a different shape. |
| `AP-08` | Glassmorphism outside modals and nav | `backdrop-filter: blur(...)` applied to a surface that is not a modal, dropdown, or navigation bar. | *Absorbed from `design-references.md` §Avoid.* Frosted-glass panels were a 2021–2023 template default; applied to ordinary content surfaces they read as dated rather than modern. | A flat or hairline-bordered surface using the project's own elevation scale. |
| `AP-09` | Scroll-jacked horizontal panels | Wheel or scroll events are intercepted in JavaScript to drive a horizontal panel-advance animation in place of native vertical scroll. | *Absorbed from `design-references.md` §Avoid.* Hijacking scroll breaks trackpad/keyboard/screen-reader expectations and is a recurring accessibility complaint independent of taste. | Native vertical scroll; a horizontal element (a carousel, a filmstrip) stays opt-in via explicit controls, never the page's primary scroll axis. |
| `AP-10` | Emoji used as a feature icon | An emoji code point occupies an icon slot in a feature list, nav item, or card. | *Absorbed from `design-references.md` §Avoid.* Emoji-as-icon is a fast, zero-design-cost placeholder that reads as unfinished the moment real content ships around it. | A consistent icon set (Lucide, Phosphor, or the project's own token-driven icon component) — one family, one stroke weight, throughout. |

## Hygiene checklist

- [ ] Exactly 10 rows, IDs `AP-01`–`AP-10`, no gaps or duplicates.
- [ ] Every row has all five fields (ID, banned-by-default, observable form, why-generic, replacement).
- [ ] Zero adjectival words in the "observable form" column (`clean`, `modern`, `sleek`, `polished`,
      `beautiful`, `elegant`, or any synonym) — every observable form is a checkable structural
      description, not a taste word.
- [ ] `AP-07`–`AP-10` cite `design-references.md` as origin via a markdown link, never a backticked path.
- [ ] The override YAML shape is documented once, here, and referenced (not restated) everywhere else
      this catalogue is consumed.

## See also

- [`../SKILL.md`](../SKILL.md) — the authoring procedure that resolves these rows per project
- [`brand-polish-checklist.md`](brand-polish-checklist.md) — the fresh-context self-check keyed to these IDs
- [`../templates/brand-guidance.md`](../templates/brand-guidance.md) — where a project resolves each row's `override`
- [`../../../knowledge/design-references.md`](../../../knowledge/design-references.md) — the curated reference set + the tropes list this catalogue absorbs from
