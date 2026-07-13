# Font web-license is not desktop license

**Status:** Absolute rule
**Domain:** Type / licensing (not legal advice)
**Applies to:** `brand-identity-studio`

> **Not legal advice.** Font-license claims route to `ravenclaude-core:security-reviewer`. Specifics
> `[verify-at-use]` — vendor EULAs change.

---

## Why this exists

The silent landmine in a brand handoff is the font. A desktop license does **not** license web use; **Adobe
Fonts forbids self-hosting** (embed-only, and the font dies if the Creative Cloud subscription lapses);
**Monotype webfonts are pageview-metered** (cost scales with traffic). If a non-self-hostable font lands in the
token export, the client ships a legal + operational liability the day they self-host it. OFL/Apache fonts
(most Google Fonts) are self-host + commercial-OK, no attribution — the safe default.

## How to apply

- Record the **web-license class** for every family in `font-license-tracker.md` (OFL/Apache / Adobe / Monotype
  / desktop-only).
- **Block** a non-self-hostable font from the token export handed to `web-design:design-tokens-scaffolding`.
- Prefer **OFL/Apache** for anything that must self-host as WOFF2.
- Route any "this font is licensed for your site" claim to `security-reviewer` before asserting it.

**Do:** classify every family; block non-self-hostable fonts from export; prefer OFL.
**Don't:** carry a desktop-licensed or Adobe/Monotype font into a self-hosted token export unchecked.

## Edge cases / when the rule does NOT apply

A client with a **paid self-hosting license** from a foundry (some Monotype/commercial tiers allow it) may
self-host — but the license terms are the authority; verify them and route to `security-reviewer`, don't assume.

## See also

- Skill: [`../skills/brand-legal-and-licensing/SKILL.md`](../skills/brand-legal-and-licensing/SKILL.md)
- Template: [`../templates/font-license-tracker.md`](../templates/font-license-tracker.md)
- Knowledge: [`../knowledge/legal-and-licensing-2026.md`](../knowledge/legal-and-licensing-2026.md)

## Provenance

Codifies B6 (developers.google.com/fonts/faq; helpx.adobe.com/fonts; foundrysupport.monotype.com). Retrieval
2026-07-13.

---

_Last reviewed: 2026-07-13 by `claude`_
