---
name: brand-legal-and-licensing
description: "State the load-bearing brand-IP facts (AI-logo copyright ≠ trademark; documented human authorship; font web-license class OFL/Adobe/Monotype; provider indemnity) and route EVERY client-facing IP / registrability / font-license claim to ravenclaude-core:security-reviewer and counsel. Not legal advice — states facts, never conclusions; recommends a TM clearance search before promising trademarkability."
---

# Brand Legal & Licensing

The brand-creation engagement runs straight into IP law: who owns an AI-generated logo, whether it can be
trademarked, whether a font can legally ship on the client's site, and whether a resold asset is indemnified.
This skill **states the facts** and **routes every client-facing claim to counsel** — it never renders a legal
conclusion.

> **NOT LEGAL ADVICE.** This skill and this plugin state general facts as of a retrieval date; they do not
> advise on a specific matter. **Every client-facing IP / copyright / trademark / registrability /
> font-license / indemnity claim MUST be routed to `ravenclaude-core:security-reviewer` (and, through it,
> qualified counsel) before the brand book or a proposal ASSERTS it.** Legal facts carry a retrieval date +
> `[verify-at-use]`; the primary sources live in
> [`../../knowledge/legal-and-licensing-2026.md`](../../knowledge/legal-and-licensing-2026.md).

## The four facts (state them plainly)

### 1. AI-logo copyright ≠ trademark

- A **purely AI-generated** logo is **not copyrightable** in the US — no human authorship; mere prompting is
  insufficient (USCO guidance, 29 Jan 2025). `[verify-at-use]`
- BUT it **can be trademarked** — USPTO evaluates the source-identifier function, not authorship.
- **Safeguard:** a documented **substantial human modification/arrangement** can restore copyrightability of
  the human-authored contribution. This is why the pipeline has a **documented-human-authorship gate** — log it
  in [`../../templates/curation-and-authorship-log.md`](../../templates/curation-and-authorship-log.md).
- **Recommend a TM clearance search** (USPTO) before promising trademarkability, and an **IP-assignment
  clause** transferring rights to the client. Both are counsel's to execute — route to `security-reviewer`.

### 2. Font web-license ≠ desktop license

- **OFL / Apache** (most Google Fonts): self-host + commercial use OK, no attribution required → **preferred**.
- **Adobe Fonts:** **forbids self-hosting** — embed-code only; the font dies if the Creative Cloud sub lapses.
- **Monotype webfonts:** **pageview-metered** — cost scales with traffic.
- **Desktop license ≠ web license** — buying a desktop font does not license it for a website.
- **Gate:** a **non-self-hostable** font is **blocked from the token export**; record every family's class in
  [`../../templates/font-license-tracker.md`](../../templates/font-license-tracker.md).

### 3. Provider indemnity (for generated imagery)

- **Adobe Firefly** is the default for client-facing **imagery** specifically because it offers **IP
  indemnification** — a real risk-reducer when reselling deliverables. `[verify-at-use]`
- Some providers (e.g. Grok/xAI) offer **no IP indemnity**.
- **But this plugin does NOT decide the provider** — it sets `indemnity_required` in the generation brief and
  **`generative-web-media`**'s license gate makes the **per-asset** call. Logos/wordmarks are the curated
  vector, not a Firefly regen; Firefly-default applies to fill/photographic imagery.

### 4. WCAG is a legal-adjacent constraint

Accessibility (WCAG 2.x AA) is increasingly a legal exposure (ADA/EAA). The color system carries validated
contrast pairs — see `logo-and-visual-system-direction` and `check-brand-a11y.py`. Flag accessibility-law
questions to counsel via `security-reviewer`.

## The routing rule (non-negotiable)

Any of the following in a client-facing artifact → **route to `security-reviewer` first:**

- "You own the copyright / the IP transfers to you"
- "This is trademarkable" / "This name is available"
- "This font is licensed for your site"
- "This asset is indemnified"

State the underlying **fact** with its source + date; let counsel convert it into a **claim** about the
specific matter.

## Anti-patterns

- Asserting trademarkability, copyright ownership, or IP transfer without a counsel route.
- Promising a name/mark is "available" without a clearance search.
- Shipping a brand book that reads as legal advice (conclusions, not facts).
- Letting a non-self-hostable font into the token export.
- Restating `generative-web-media`'s per-asset indemnity decision as this plugin's own.

## See also

- Knowledge (primary sources, dated): [`../../knowledge/legal-and-licensing-2026.md`](../../knowledge/legal-and-licensing-2026.md)
- Template: [`../../templates/font-license-tracker.md`](../../templates/font-license-tracker.md),
  [`../../templates/curation-and-authorship-log.md`](../../templates/curation-and-authorship-log.md)
- Best-practices: [`../../best-practices/ai-logo-copyright-is-not-trademark-document-human-authorship.md`](../../best-practices/ai-logo-copyright-is-not-trademark-document-human-authorship.md),
  [`../../best-practices/font-web-license-is-not-desktop-license.md`](../../best-practices/font-web-license-is-not-desktop-license.md)
- Escalation: `ravenclaude-core:security-reviewer` (mandatory for every client-facing IP claim)
