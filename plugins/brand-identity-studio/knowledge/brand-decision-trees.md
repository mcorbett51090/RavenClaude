# Brand Identity Studio — Decision Trees

> Reference decision trees for the `brand-identity-studio` team. Agents **traverse the relevant tree
> top-to-bottom before deciding**. Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Not legal advice; prices `[unverified]`.** Anything touching an IP/registrability/font-license claim routes
> to `ravenclaude-core:security-reviewer`; anything touching a price is `[unverified]`; provider/API facts are
> `[verify-at-use]`.
>
> _Last reviewed: 2026-07-13 by `claude`. Principles are durable; dated specifics live in
> [`brand-identity-anatomy-2026.md`](brand-identity-anatomy-2026.md) and
> [`legal-and-licensing-2026.md`](legal-and-licensing-2026.md)._

---

## Decision Tree: which engagement tier?

```mermaid
flowchart TD
    A[New brand engagement] --> B{Does the client need STRATEGY<br/>+ voice, or just a mark?}
    B -- "just a logo + basic palette/type" --> C[Starter tier<br/>logo + mini guide<br/>~$2-7K unverified]
    B -- "full identity with strategy" --> D{Does the brand feed a WEBSITE<br/>whose tokens it should source?}
    D -- "no / not yet" --> E[Mid tier<br/>identity + strategy + voice + brand book<br/>~$7-25K unverified]
    D -- "yes — brand IS the site's token source" --> F[Comprehensive tier<br/>mid + messaging + web token handoff + collateral<br/>~$25-100K+ unverified]
    C --> G[Declare deep-vs-direction scope<br/>+ mark every price unverified]
    E --> G
    F --> G
```

**Rule:** the tier is set by whether the client needs the **strategy substrate** and whether the brand **feeds
a site's tokens**. The natural studio bundle is mid/comprehensive, where the brand system IS the source of the
site's design tokens (delegated to `web-design:design-tokens-scaffolding`). All prices `[unverified]` — confirm
on the market pricing page; declare what's deep (logo/color/type/tokens/brand-book/voice) vs direction
(icon/imagery) vs out-of-v1 (motion, extensive stationery).

---

## Decision Tree: agentic pipeline vs human-only toolkit?

```mermaid
flowchart TD
    A[How to produce the identity?] --> B{Is a public generative API<br/>available for the tool?}
    B -- "Looka / Brandmark / Tailor Brands" --> C[NO public API — UI-only<br/>an agent CANNOT orchestrate these<br/>= human-only resale, out of scope]
    B -- "Recraft / Ideogram / Firefly / Gamma" --> D{Strategy brief authored?}
    D -- "no" --> E[STOP — author strategy first<br/>strategy-before-visuals gate]
    D -- "yes" --> F[Author anti-slop brief<br/>specific + negative constraints]
    F --> G[generative-web-media generates breadth<br/>or prompt-pack fallback]
    G --> H[HUMAN curates + logs authorship<br/>the curated vector is the deliverable]
    H --> I[Never regenerate the logo in Firefly]
```

**Rule:** the agentic path is Claude-orchestrator-over-Recraft/Ideogram/Firefly/Gamma (all API-callable), NOT a
Looka/Brandmark resale (no public API — UI-only). Strategy gates generation; a human curates; the curated
vector is the deliverable and is never regenerated in Firefly (regen voids the curation). Provider selection +
per-asset indemnity is `generative-web-media`'s call, not this plugin's.

---

## Decision Tree: font web-license class (can it ship self-hosted?)

```mermaid
flowchart TD
    A[Chosen font family] --> B{What is the web-license class?}
    B -- "OFL / Apache (most Google Fonts)" --> C[Self-host + resale OK, no attribution<br/>= PREFERRED — ships in token export]
    B -- "Adobe Fonts" --> D[Self-hosting FORBIDDEN — embed-only<br/>dies if CC sub lapses]
    B -- "Monotype webfont" --> E[Pageview-metered — cost scales with traffic]
    B -- "Desktop license only" --> F[Web use NOT covered]
    D --> G[BLOCK from token export<br/>route font-license claim to security-reviewer]
    E --> G
    F --> G
    C --> H[Record class in font-license-tracker]
    G --> H
```

**Rule:** OFL/Apache self-host is preferred and ships in the token export. A **non-self-hostable** font (Adobe
embed-only, Monotype metered, desktop-only) is **blocked from the export** and its license claim routes to
`security-reviewer`. Every family's class is recorded in the font-license-tracker. Desktop license ≠ web
license.

---

## Decision Tree: where does this work belong (delegate or own)?

```mermaid
flowchart TD
    A[A piece of brand work] --> B{What kind?}
    B -- "strategy / positioning / archetype / naming / voice" --> C[OWN — brand-strategist]
    B -- "logo/color/type DIRECTION + curation + brand book" --> D[OWN — identity-systems-designer]
    B -- "design TOKENS (DTCG -> CSS/Tailwind)" --> E[DELEGATE -> web-design:design-tokens-scaffolding]
    B -- "raw asset GENERATION + license/indemnity" --> F[DELEGATE -> generative-web-media]
    B -- "apply the brand to the SITE" --> G[HAND OFF -> web-design:visual-designer]
    B -- "pull brand/tokens from an EXISTING site" --> H[DELEGATE -> ravenclaude-core:brand-extraction]
    B -- "any client-facing IP / trademark / font claim" --> I[ESCALATE -> security-reviewer + counsel]
```

**Rule:** this plugin is **thin**. It OWNS strategy + identity-direction + brand book; it DELEGATES tokens
(web-design), generation + indemnity (generative-web-media), and site application (web-design:visual-designer);
it ESCALATES every client-facing IP claim to `security-reviewer`. Owning zero token code kills the
triplicated-token-contract failure mode (RT1). If a piece of work isn't in the OWN branches, delegate or
escalate it — don't re-implement it.
