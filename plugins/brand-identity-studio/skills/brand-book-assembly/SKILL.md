---
name: brand-book-assembly
description: "Compile the finished brand system into a dynamic brand-book hub (logo rules, color tokens, type, voice, imagery, usage do/don'ts), DELEGATE the token build to web-design:design-tokens-scaffolding, spec the favicon/OG asset set, and enforce the legal-sign-off precondition (can't mark client-ready without the curation + authorship log and every IP/font claim routed to security-reviewer). Hands the finished system to web-design:visual-designer."
---

# Brand Book Assembly

The last mile: compile everything into a brand book a client can actually use, wire the tokens into the site
via delegation, and gate the "client-ready" flag on curation + legal sign-off. A brand book is a **dynamic
hub**, not a rotting PDF.

> **Precondition (legal-sign-off gate):** this skill CANNOT mark a brand book **client-ready** until (a) the
> [`curation-and-authorship-log.md`](../../templates/curation-and-authorship-log.md) exists (human curation +
> documented authorship), and (b) **every** IP/registrability/font-license claim has been routed to
> `ravenclaude-core:security-reviewer`. Not legal advice. Prices `[unverified]`.

## Workflow

1. **Check the gates.** Strategy brief exists · curation + authorship log exists · WCAG pairs validated ·
   font-license classes recorded · IP/font claims routed to `security-reviewer`. If any is missing, **do not
   mark client-ready** — list what's pending.
2. **Compile the book** from [`../../templates/brand-book-outline.md`](../../templates/brand-book-outline.md):
   strategy/positioning + archetype, logo suite rules, color tokens, type + web-license class, voice &
   messaging (from `brand-voice-and-messaging`), imagery direction, usage do/don'ts, governance + AI-content
   rules + accessibility notes.
3. **Delegate the token build.** Hand the color roles + type decisions to
   **`web-design:design-tokens-scaffolding`** — it produces the DTCG token JSON → Style Dictionary → CSS
   vars / Tailwind `@theme`. **Build no token code here.** If `web-design` is absent, ship the book with the
   palette/type decisions and a note that the token build needs `web-design`.
4. **Spec the collateral asset set.** The favicon/OG manifest
   ([`../../templates/favicon-og-asset-manifest.md`](../../templates/favicon-og-asset-manifest.md)) is v1-deep;
   business cards / email signature / social kit are lighter templates.
5. **Hand off to the site.** The finished system (curated logo files + delegated DTCG token file + brand book)
   goes to **`web-design:visual-designer`** for site application. Do not apply it to the site here.

## Brand-book anatomy (the 10 parts — v1 depth flags)

| # | Section | v1 depth |
|---|---|---|
| 1 | Strategy / positioning + archetype + voice | **deep** (from brand-strategist) |
| 2 | Logo suite / lockups / clear-space / min-size / mono / B&W | **deep** |
| 3 | Color system — roles + HEX/RGB/OKLCH + WCAG pairs | **deep** |
| 4 | Type system + scale + pairing + web-license class | **deep** |
| 5 | Grid / spacing | direction |
| 6 | Iconography | direction (not full production) |
| 7 | Imagery direction | direction (indemnity via media) |
| 8 | Voice & messaging (tagline / tone / do-say-don't) | **deep** |
| 9 | Usage do/don'ts | **deep** |
| 10 | The brand book itself (dynamic hub; +AI-content rules, a11y, governance) | **deep** |

Declare what's deep vs direction so the client isn't sold "shallow everywhere." Motion and extensive
stationery are explicitly **out of v1** (or lighter templates) — say so.

## Dynamic hub, not a static PDF

2025+ brand books are living: a hub (site/Notion/Storybook-adjacent) where the color tokens shown ARE the
delegated tokens, the logo files are downloadable, and the do/don'ts render. A PDF rots the day the palette
changes; the hub re-reads the token source. Add an **AI-content usage** section (how the brand may/may not be
used in generated media) and an **accessibility** section (the validated pairs, reduced-motion posture).

## The favicon / OG asset set (2026 minimum)

Spec via [`../../templates/favicon-og-asset-manifest.md`](../../templates/favicon-og-asset-manifest.md):
`favicon.svg` (dark-mode via media query), `favicon.ico` (16/32/48), `apple-touch-icon` 180×180,
PWA 192/512, OG image 1200×630, Twitter/X card 1200×675. Generation of these routes through
`generative-web-media` (or the prompt-pack); this skill specs the manifest and checks completeness.

## Anti-patterns

- Marking a brand book "client-ready" with a pending curation/authorship log or an un-routed IP claim.
- Re-implementing the token pipeline instead of delegating to `web-design:design-tokens-scaffolding`.
- Shipping a static PDF that drifts from the token source.
- "Deep everywhere" claims when icon/imagery/motion are direction-only in v1.
- Applying the brand to the site here instead of handing off to `web-design:visual-designer`.

## See also

- Template: [`../../templates/brand-book-outline.md`](../../templates/brand-book-outline.md),
  [`../../templates/favicon-og-asset-manifest.md`](../../templates/favicon-og-asset-manifest.md)
- Delegation: `web-design:design-tokens-scaffolding` (tokens), `web-design:visual-designer` (site application)
- Skill: [`../brand-legal-and-licensing/SKILL.md`](../brand-legal-and-licensing/SKILL.md) (the legal-sign-off inputs)
- Knowledge: [`../../knowledge/brand-identity-anatomy-2026.md`](../../knowledge/brand-identity-anatomy-2026.md)
