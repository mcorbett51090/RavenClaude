# Font License Tracker — <brand / date>

> Per-family **web-license class** record. The gate: a **non-self-hostable** font (Adobe Fonts embed-only,
> Monotype pageview-metered, desktop-only) is **BLOCKED from the token export**. **Not legal advice** — every
> "licensed for your site" claim routes to `ravenclaude-core:security-reviewer`. Specifics `[verify-at-use]`
> (vendor EULAs change).

## Header

- **Brand:** _____  · **Prepared:** 2026-__-__  · **Owner:** _____

## Families

| Family | Role | License class | Self-host? | Resale-safe? | Ships in token export? | Notes / source |
|---|---|---|---|---|---|---|
| _e.g. Inter_ | text | OFL | ✅ | ✅ | ✅ | Google Fonts OFL — preferred |
| | display | | | | | |
| | mono | | | | | |

**License-class legend (`[verify-at-use]`, retrieval 2026-07-13):**

- **OFL / Apache** (most Google Fonts) — self-host + commercial OK, no attribution → **preferred, ships**.
- **Adobe Fonts** — **self-hosting forbidden** (embed-only; dies if CC sub lapses) → **blocked from export**.
- **Monotype webfont** — **pageview-metered** → **blocked from export** unless a self-host license is verified.
- **Desktop-only** — web use **not** covered → **blocked from export**.

## Gate checklist

- [ ] Every family classified above
- [ ] Non-self-hostable families flagged and **excluded from the token export** handed to
      `web-design:design-tokens-scaffolding`
- [ ] Any "this font is licensed for your site" claim routed to `security-reviewer`
- [ ] Self-host format noted (WOFF2) for OFL/Apache families

## Decision

- **Fonts cleared for the self-hosted token export:** _____
- **Fonts blocked (and why):** _____
- **Substitutions proposed for blocked fonts:** _____

---
_Plus the ravenclaude-core Structured Output block. Desktop license ≠ web license; not legal advice — route to
`security-reviewer`. Backs the `font-web-license-is-not-desktop-license` best-practice._
