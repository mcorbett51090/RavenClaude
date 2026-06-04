---
name: brand-extraction
description: "Point at a website home page and extract every logo variant plus the brand 'schema' (design tokens — colors, typography, radii) into a ready-to-apply brand kit, so HTML documents/reports you generate for that project match the brand. Use when the user says things like 'pull the logo and brand from this site', 'extract the brand schema from <url>', 'make my reports match <company>'s style', or 'grab the colors and fonts from this homepage'."
---

# Brand extraction — homepage → reusable brand kit

Turn a website home page into a **brand kit** you can apply to any HTML you generate
for that project, so reports/documents come out in the brand's proper format.

The kit (written to `brand-kit/` by default):

| File | What it is |
|---|---|
| `logos/` | Every logo variant found, downloaded (favicon, apple-touch-icon, mask-icon, og:image, header/footer `<img>`, inline header `<svg>`, light/dark `<picture>` variants). |
| `brand.json` | The **schema** — design tokens (ranked colors with guessed roles, fonts, radii, every color CSS custom property) + the full logo inventory. Validated by [`schemas/brand-kit.schema.json`](../../../../schemas/brand-kit.schema.json). |
| `brand.css` | CSS custom properties (`--brand-primary/-accent/-bg/-text/-font-heading/-font-body/-radius` + every source `--*`) ready to `<link>` or paste. |
| `report-template.html` | A working starter report wired to `brand.css` + the primary logo — drop your content into `<main>`. |
| `brand-summary.md` | Human-readable summary of what was extracted, with confidence notes. |

## How to run it

The engine is stdlib-only Python (no installs):

```bash
python3 plugins/ravenclaude-core/skills/brand-extraction/extract_brand.py <url> --out brand-kit
```

| Flag | Effect |
|---|---|
| `--out DIR` | Output directory (default `brand-kit/`). |
| `--max-stylesheets N` | How many external stylesheets to fetch for token mining (default 8). |
| `--no-download` | Inventory the logos without downloading the bytes (fast dry run). |
| `--timeout SECONDS` | Per-request timeout (default 20). |

For a project, write the kit **into the project repo** (e.g. `--out assets/brand`) so the
generated reports and the brand tokens live together.

## What it extracts (the "schema")

**Logos — all variants, kept with their source role:**
`<link rel="icon|shortcut icon|apple-touch-icon|mask-icon">`, `og:image` / `twitter:image`,
`<img>` whose class/id/alt/src matches `logo|brand|wordmark|masthead`, inline `<svg>` in the
header/nav, and `<picture><source media="prefers-color-scheme: dark|light">` variants.
Deduped by resolved URL; each keeps a `context` string so you can tell them apart.

**Colors — ranked, most-reliable-first:**
1. CSS custom properties whose value is a color (`--color-primary`, `--brand-accent`, …) — a
   design system naming its own tokens is the strongest signal, so these are surfaced verbatim
   in `brand.json.colors.custom_properties` and role-mapped by name.
2. `<meta name="theme-color">`.
3. Frequency analysis of every `#hex` / `rgb()` / `hsl()` in the CSS, with neutrals
   (white/black/greys) filtered out of the brand-hue ranking.

**Typography:** first family of each `font-family` stack (frequency-ranked → heading/body
guess) plus families named in Google Fonts / Typekit `<link>`s.

**Radii:** the most common `border-radius` values (the brand's corner-rounding scale).

## Using the kit on generated reports

Once the kit exists, every HTML document you generate for that project should:

```html
<link rel="stylesheet" href="brand.css" />
```

and use the tokens — `color: var(--brand-text); background: var(--brand-bg);`
`font-family: var(--brand-font-heading);` headings in `var(--brand-primary)`, etc.
`report-template.html` is a copy-paste starting point. Pick the logo variant that fits
(SVG for crisp scaling, the dark variant for dark headers).

## Honesty discipline — the tokens are heuristic

The role labels (which color is "primary", which font is "heading") are **best-guess** and
marked as such per-item (`source`/`role` fields) and in `confidence_notes`. Before you treat
the kit as authoritative:

1. **Read `brand-summary.md`** — it lists every logo, the ranked colors, and the caveats.
2. **Fix any mislabeled roles in `brand.json`** (and re-run `brand.css` mentally, or just edit
   the four `--brand-*` lines) — e.g. if frequency picked a link-blue as "primary" but the real
   brand color is the custom property, prefer the custom property.
3. **Some sites defeat static extraction** — CSS-in-JS, fonts loaded at runtime, or assets on a
   blocked origin won't appear. The script records this in `confidence_notes` rather than
   guessing; when colors/fonts come back empty, fall back to **WebFetch** on the page and read
   the rendered styling, or ask the user for the brand guide.

This mirrors the marketplace's Claim Grounding discipline: the kit reports *what it actually
found* and flags what it couldn't, instead of fabricating a confident palette.

## When to reach for WebFetch instead / as well

- The script is the **deterministic** layer (download bytes, parse CSS, dedupe logos).
- **WebFetch** (with this repo's webfetch-hardening sanitizer) is the **reasoning** layer — use
  it to confirm which logo is the "real" primary mark, read a `/brand` or `/press` page for an
  official asset pack, or interpret a styling choice the regex can't. The two compose: run the
  script for the kit, then WebFetch to sanity-check the primary color/logo pick.
- Honor `.ravenclaude/web-access.yaml` allow/deny lists for the domain (the `guard-web-access.sh`
  hook governs WebFetch; the script's `urllib` fetch is a deliberate agent action on a
  user-supplied public URL).

## Provenance

- Added 2026-06-04. Engine: [`extract_brand.py`](extract_brand.py). Schema:
  [`schemas/brand-kit.schema.json`](../../../../schemas/brand-kit.schema.json).
- Domain-neutral by design (it works for any project's brand), so it lives in `ravenclaude-core`
  rather than a domain plugin — per the house rule that core stays domain-neutral.
