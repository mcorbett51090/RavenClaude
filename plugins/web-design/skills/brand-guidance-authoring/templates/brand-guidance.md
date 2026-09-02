<!--
brand-guidance.md — generation-time brand-voice contract.

This file is loaded into context BEFORE EVERY PAGE-GENERATION CALL, alongside the project's
design-tokens.json. It answers "how does an agent reliably apply the tokens" — the tokens answer
"what are the values." See ../SKILL.md for the authoring procedure and
../../../knowledge/design-md-token-interop.md for why this is NOT the same file as the Google-Labs
DESIGN.md token-export format (same-filename-different-job, disambiguated there).

Fill in every section below. Do not ship a section with placeholder text — an unresolved
"<TODO>" anywhere in this file fails the pipeline's G3 structural bar.
-->

project: <project-name>
last_reviewed: <YYYY-MM-DD>
token_source: <path-to-design-tokens.json>

<!-- This file is read into context on every page-generation call in this project. -->

## 1. Named aesthetic

<One line — a proper noun or noun phrase, never "modern and clean." Name 2–3 concrete reference
points (real sites/products, not adjectives) that anchor the direction.>

Example shape (replace entirely, do not keep): "Editorial technical — Stripe docs' type rhythm crossed
with a print-magazine grid. References: Stripe Docs, Are.na, Basecamp's Shape Up site."

## 2. Typography

<!-- typeface_count: 2 — this field is machine-read by the pipeline's G3 structural bar; a third face
     ships in this section fails that check. Keep the count in sync with the table below by hand. -->

| Role | Typeface | Loaded weights | Fallback stack |
|---|---|---|---|
| Display / heading | `<face>` | `<weights>` | `<system fallback>` |
| Body | `<face>` | `<weights>` | `<system fallback>` |

At most two typefaces. A UI/data/tabular face pulled from the token system's own scale does not count
against this limit — this row covers only the two identity-carrying faces above.

## 3. Palette

<!-- Reference the project's own DTCG semantic tokens — never raw hex here. See
     web-design/CLAUDE.md §3 rule 4 ("design tokens, not hardcoded values") and
     design-tokens-scaffolding/SKILL.md for the primitive/semantic split this section assumes. -->

- **Brand hue:** `color.accent.default` (references the token, does not restate the value)
- **Neutral ramp:** `color.background.*` / `color.text.*`
- **Functional (≤3):** `color.success.default`, `color.warning.default`, `color.danger.default` — name
  only the ones this project actually uses.

## 4. Spacing

A 4px-based scale, enumerated. No off-scale value ships anywhere in the built output.

`4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96` (adjust to the project's actual token scale — keep it
geometric, keep it enumerated, never "roughly 4px increments").

## 5. Radius & elevation

<One stance, not a menu.> Example shape (replace, do not keep): "Sharp corners throughout (`radius:
none` everywhere except a single `sm` value on form inputs). Elevation is expressed by a 1px hairline
border, never a drop shadow."

## 6. Motion philosophy

<One sentence on what moves and why.> Duration tokens: `<name the scale, e.g. instant/fast/default/
slow>`. Easing tokens: `<name the scale>`. `prefers-reduced-motion: reduce` re-points every duration
token to `instant` and every transform to an opacity-only fade — state this explicitly, do not assume
it's implied.

## 7. Anti-pattern catalogue — this project's resolution

<!-- Every AP-nn row from ../reference/anti-pattern-catalogue.md MUST appear here, resolved for THIS
     project. Copy the ID and the one-line "banned by default" text; do not restate the full row —
     the catalogue file is the source of truth for the WHY and the replacement guidance. A row missing
     from this section, or a section missing an ID, fails the pipeline's G3 structural bar (both
     directions checked). -->

| ID | Banned by default | `override.status` | `override.rationale` (required unless `enforced`) |
|---|---|---|---|
| `AP-01` | Generic-sans as the brand voice / display face | enforced | |
| `AP-02` | Indigo→purple hero gradient / "AI shimmer" | enforced | |
| `AP-03` | 3-column icon-over-heading-over-paragraph feature grid | enforced | |
| `AP-04` | Card-in-card / nested large-radius containers | enforced | |
| `AP-05` | Centered 100vh hero over a stock photograph | enforced | |
| `AP-06` | Fabricated metrics / invented social proof | enforced | |
| `AP-07` | Bento grid applied to more than one section | enforced | |
| `AP-08` | Glassmorphism outside modals and nav | enforced | |
| `AP-09` | Scroll-jacked horizontal panels | enforced | |
| `AP-10` | Emoji used as a feature icon | enforced | |

A `relaxed` or `replaced` status requires a non-empty, project-specific `rationale` — "we like it" is
not a rationale. See `../SKILL.md` §5 for the override procedure.
