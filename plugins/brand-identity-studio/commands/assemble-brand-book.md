---
description: "Compile the finished brand system into a dynamic brand-book hub and delegate the token build to web-design:design-tokens-scaffolding — REFUSES to mark it client-ready until the curation + authorship log exists AND every IP/registrability/font-license claim has been routed to security-reviewer (the legal-sign-off gate). Hands the finished system to web-design:visual-designer."
argument-hint: "[project name + confirmation the curation, WCAG, and font-license gates are done]"
---

You are running `/brand-identity-studio:assemble-brand-book`. Use `identity-systems-designer` + the
`brand-book-assembly` skill (+ `brand-legal-and-licensing` for the sign-off inputs).

> **Gate (hard precondition):** the brand book cannot be marked **client-ready** until (a) the
> `curation-and-authorship-log.md` exists, (b) the WCAG pairs validated and font-license classes are recorded,
> and (c) **every** IP/registrability/font-license claim has been routed to `security-reviewer`. Not legal
> advice. Token build is DELEGATED — build no token code here.

## Steps

1. **Check the gates.** Verify: strategy brief · curation + authorship log · WCAG pairs validated
   (`scripts/check-brand-a11y.py`) · font-license classes recorded · IP/font claims routed to
   `security-reviewer`. **List any pending gate and do NOT mark client-ready if one is missing.**
2. **Compile the book** from `templates/brand-book-outline.md` (the 10-part anatomy; declare deep vs
   direction), pulling voice from `brand-voice-and-messaging` and the logo/color/type specs from
   `logo-and-visual-system-direction`.
3. **Delegate the tokens.** Hand the color roles + type decisions to
   **`web-design:design-tokens-scaffolding`** to produce the DTCG token JSON → Style Dictionary → CSS
   vars / Tailwind. If `web-design` is absent, ship the book with the decisions + a "needs web-design for the
   token build" note. Build no token code here.
4. **Spec the collateral** — the favicon/OG manifest (`templates/favicon-og-asset-manifest.md`); generation
   routes through `generative-web-media` / the prompt-pack.
5. **Hand off to the site.** The finished system → **`web-design:visual-designer`** for site application.
6. **Emit** the brand book + its client-ready state (ready / pending-gates with the list) + the delegations
   made + the Structured Output block.
