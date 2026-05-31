---
description: Run a technical SEO + AEO audit on the rendered HTML — verify the metadata baseline (title, description, canonical, OG/Twitter), one clean heading tree with no level skips, descriptive link text, validating JSON-LD with a connected entity graph, and answer-ready content structure.
argument-hint: "[the site/page, e.g. 'the marketing site' or a URL; omit for the current page]"
---

# Run a technical SEO audit

You are running `/web-design:run-technical-seo-audit`. Audit discoverability for the site or page the user named (`$ARGUMENTS`), following this plugin's `web-architect` + `content-strategist` discipline. Discoverability now spans classic search rank *and* citation inside AI-synthesized answers — and both read the rendered HTML, which is the same semantic surface accessibility needs (SEO + a11y converge).

## When to use this

A pre-launch SEO gate, a ranking-drop investigation, or a content/discoverability audit. Not for off-page link-building or paid-search work (out of this team's lane).

## Steps

1. **Verify the metadata baseline on every page** (`seo-semantic-structure-and-metadata`): a unique `<title>` and `<meta name="description">`, a `canonical`, and OG/Twitter cards on shareable pages. Catch the mechanical failures the hook flags — a missing title/description, a `noindex` accidentally shipped to production, a `robots.txt` disallowing `/`, broken OG cards.
2. **Confirm one clean heading tree and descriptive link text** (`content-readability-and-hierarchy`): one `<h1>`, no heading-level skips (h1 → h3 is a styling job for tokens, not a semantics hack); link text says where it goes, never "click here"/"read more" — which serves a11y at the same time.
3. **Add JSON-LD schema that validates, in a connected entity graph** (`seo-semantic-structure-and-metadata`): `FAQPage` is the highest-impact type for AI citation; build `Organization` → `Person` → `sameAs` connections — a lone schema block doesn't earn citations. Validate it.
4. **Lead with answer-ready structure** (`content-readability-and-hierarchy`): each section opens with a direct, self-contained answer (inverted pyramid), short declarative paragraphs, H2/H3 phrased as the questions users ask — the structure crawlers and LLMs lift. Hold one reading level per audience.
5. **Confirm crawlers read the rendered content** (`seo-semantic-structure-and-metadata`): static-first / progressive enhancement so the content is in the rendered HTML, not only after hydration; fix trailing-slash/case inconsistency that splits a URL into duplicates.

## Guardrails

- Intentionally non-indexed pages (staging, thank-you, gated) *should* carry `noindex` — the anti-pattern is the *accidental* one on a page you want indexed.
- AEO tactics are emergent — lead with the durable moves (strong SEO foundation, answer-ready structure, real E-E-A-T authority) and measure the rest; don't oversell `llms.txt` (adoption is uneven as of 2026).
- Finance / regulatory content in metadata or schema (claims, disclosures) routes through `regulatory-compliance` / `finance` before shipping.
