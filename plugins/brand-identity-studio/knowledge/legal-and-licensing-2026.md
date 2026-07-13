# Brand Legal & Licensing Reference — 2026

> **NOT LEGAL ADVICE.** This document states general facts as of a retrieval date for orientation only; it is
> not advice on any specific matter and creates no attorney-client relationship. **Every row below routes a
> client-facing claim to `ravenclaude-core:security-reviewer` and qualified counsel before this plugin ASSERTS
> it.** Legal facts carry a retrieval date + `[verify-at-use]`.
>
> _Last reviewed: 2026-07-13 by `claude`. Retrieval date 2026-07-13._

---

## 1. AI-logo copyright ≠ trademark (the load-bearing fact)

| Fact | Source (retrieval 2026-07-13) | Confidence | Route client-facing claim to |
|---|---|---|---|
| A **purely AI-generated** logo is **NOT copyrightable** in the US — no human authorship; mere prompting is insufficient | USCO AI policy guidance, 29 Jan 2025 (copyright.gov/ai/ai_policy_guidance.pdf) | **High** | counsel via security-reviewer |
| The same logo **CAN be trademarked** — USPTO evaluates the source-identifier function, not authorship | USPTO practice; tish.law; jonesday.com | Med-High | counsel via security-reviewer |
| **Documented substantial human modification/arrangement** can restore copyrightability of the human contribution | USCO guidance (human-authorship threshold) | Med-High | the documented-human-authorship gate + counsel |
| A **TM clearance search** (USPTO) is required before promising trademarkability | USPTO TESS workflow (not deep-dived here) | — | counsel via security-reviewer |
| An **IP-assignment clause** should transfer rights to the client on a commissioned brand | standard commissioning practice | — | counsel via security-reviewer |

**What this means for the pipeline:** the **documented-human-authorship gate** (`/curate-concepts` logs a
substantial human modification) is what makes the resale deliverable ownable/assignable. Without it, a pure-AI
mark carries no copyright. State this fact; **do not conclude** the client "owns" or "can trademark" anything —
route that claim to counsel.

## 2. Font web-licensing (the silent landmine)

| Class | Rule | Self-host? | Resale-safe? | Source (retrieval 2026-07-13) |
|---|---|---|---|---|
| **OFL / Apache** (most Google Fonts) | Commercial use OK, no attribution | ✅ yes | ✅ yes → **preferred** | developers.google.com/fonts/faq |
| **Adobe Fonts** | **Forbids self-hosting** — embed-code only; dies if CC sub lapses | ❌ no | ⚠️ embed-only, sub-dependent | helpx.adobe.com/fonts |
| **Monotype webfonts** | **Pageview-metered** — cost scales with traffic | ⚠️ per license | ⚠️ metered | foundrysupport.monotype.com |
| **Desktop license** | Licenses desktop use, **NOT web** | ❌ web not covered | ❌ | foundry EULAs |

**Confidence: High.** **Gate:** a **non-self-hostable** font (Adobe, Monotype without a self-host license) is
**BLOCKED from the token export**. Record every family's class in the font-license-tracker template. Route any
"this font is licensed for your site" claim to `security-reviewer`.

## 3. Provider indemnity (generated imagery)

| Provider | IP indemnity? | Use | Source (retrieval 2026-07-13) |
|---|---|---|---|
| **Adobe Firefly** | ✅ IP-indemnified | Default for client-facing **imagery** (fill/photographic) | licenseorg.com/blog/adobe-firefly-indemnification |
| **Grok / xAI** | ❌ no IP indemnity | Avoid for resold client assets | run-1 research strand |
| **Recraft / Ideogram** | vendor-specific `[verify-at-use]` | Logos/wordmarks (the **curated vector** deliverable) | vendor terms |

**Confidence: Med-High.** **This plugin does NOT decide the provider** — it sets `indemnity_required` in the
brief and **`generative-web-media`**'s license gate makes the **per-asset** decision. Logos/wordmarks are the
curated vector (never a Firefly regen); Firefly-default applies to fill/photographic imagery only. Route any
"this asset is indemnified" claim to `security-reviewer`.

## 4. Accessibility as legal-adjacent

WCAG 2.x AA contrast is increasingly a legal exposure (ADA in the US; the EU Accessibility Act). The color
system carries **validated** contrast pairs (see `check-brand-a11y.py`). Flag accessibility-law questions to
counsel via `security-reviewer` (w3.org/WAI/WCAG21/Understanding/contrast-minimum; retrieval 2026-07-13, High
on the WCAG thresholds).

---

## The one rule this file exists to enforce

> **State the fact with its source + date. Never render the legal conclusion.** Any of these in a
> client-facing artifact routes to `security-reviewer` (and counsel) FIRST: "you own the copyright",
> "this is trademarkable", "this name/mark is available", "this font is licensed for your site", "this asset is
> indemnified". Counsel converts a fact into a claim about the specific matter — this plugin does not.

## Verification debts

- USCO/USPTO guidance is a lawyer-summary + one primary USCO PDF — **route client-facing IP/registrability +
  font-license claims to security-reviewer/counsel before asserting trademarkability or IP transfer.**
- USPTO TESS clearance-search workflow not deep-dived — required before promising trademarkability.
- Provider indemnity terms are vendor-volatile `[verify-at-use]`.
