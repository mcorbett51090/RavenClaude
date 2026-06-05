---
scenario_id: 2026-06-05-design-token-drift-hardcoded-hex
contributed_at: 2026-06-05
plugin: web-design
product: tailwind
product_version: "unknown"
scope: likely-general
tags: [design-tokens, drift, hardcoded-hex, dark-mode, style-dictionary]
confidence: high
reviewed: false
---

## Problem

A product site had a design system "with tokens," yet a dark-mode rollout exposed the truth: dozens of components rendered the wrong color in dark theme, a few buttons stayed light-on-light, and the "brand blue" appeared as four slightly different hex values across the codebase. The team thought they had tokens; what they had was a `tokens.css` file plus a long tail of hardcoded `#hex` values, inline `style="color: …"`, and one-off Tailwind arbitrary values (`text-[#3b82f6]`) that never flowed through the token layer. Dark mode was the forcing function that surfaced the drift — the hardcoded values had no dark variant to switch to.

## Constraints context

- **Design tokens, not hardcoded values** (constitution §3 #4) and **one source of truth per design decision** (§3 #12) — a token defined once, consumed everywhere; drift is a bug, not a style preference.
- The drift was **mechanically detectable**: the plugin's advisory hook ([`../hooks/check-web-anti-patterns.sh`](../hooks/check-web-anti-patterns.sh)) flags hardcoded hex in JSX/TSX/CSS outside `tokens.*`, but it had been treated as noise, not a gate.
- Two distinct color systems were in play: **primitive** tokens (the raw palette, `blue-500`) and **semantic** tokens (`--color-text`, `--color-surface`, `--color-brand`). Components were binding to primitives — or to raw hex — instead of to semantic tokens, which is exactly what breaks theming.
- The team wanted to "just add a dark palette," but a dark palette can't fix a component that references a literal `#3b82f6` — there's nothing for the theme switch to re-point.

## Attempts

- Tried: adding a parallel dark palette and a `.dark` class. Outcome: only fixed components that *already* read from semantic tokens; every hardcoded value and primitive-bound style stayed light. Treating the symptom (no dark palette) instead of the cause (no semantic token indirection).
- Tried: a find-and-replace of hex values to the nearest token. Outcome: brittle and incomplete — it missed arbitrary Tailwind values, inline styles, and computed colors, and it conflated "looks like brand blue" with "is semantically brand." Replace-by-appearance loses the *meaning* the semantic layer carries.
- Tried (what worked): a **two-layer token model + a drift gate.**
  - Defined **primitive** tokens (the palette) and **semantic** tokens (role-based: text/surface/border/brand/feedback) in a single source of truth (DTCG-format token JSON → Style Dictionary build → CSS custom properties + Tailwind theme), so light/dark is a swap of the *semantic* layer's values, not a per-component edit.
  - Rebound components to **semantic** tokens only; primitives became build-time inputs, not component-facing.
  - Turned the hardcoded-hex check from advisory to a **CI gate** so new drift fails the build, and ran a one-time sweep to migrate the existing literals.

## Resolution

**Tokens are an indirection layer, not a color file — and dark mode is the test that proves whether you actually have one.** The durable shape:

1. **Two layers: primitive → semantic.** Components bind to *semantic* tokens (`--color-text`, `--color-surface`), never to primitives or raw hex. Theming = re-point the semantic layer; components don't change.
2. **One source of truth, built, not hand-synced.** Author tokens once (DTCG JSON), build to every target (CSS vars, Tailwind theme, native) with Style Dictionary. Hand-maintaining parallel copies *is* the drift.
3. **Make the drift check a gate.** Hardcoded hex / inline color / arbitrary Tailwind values outside the token layer should fail CI — an advisory warning regresses, a gate holds (the same lesson as the perf budget).
4. **Verify contrast at the token, per theme.** When you darken/adjust a semantic token, re-check contrast against the surfaces it renders on, in both themes — fixing color must not break WCAG (loop the contrast arithmetic through [`../scripts/contrast_ratio.py`](../scripts/contrast_ratio.py)).

**Action for the next designer/implementer:** when "we have tokens" but theming breaks, audit whether components bind to **semantic** tokens or to primitives/literals — that's the drift. Add primitive→semantic indirection, build from one source (Style Dictionary / DTCG), and gate hardcoded values in CI. Cross-reference [`../best-practices/visual-design-tokens-not-hardcoded-values.md`](../best-practices/visual-design-tokens-not-hardcoded-values.md), [`../best-practices/css-custom-properties-bridge-tokens-to-components.md`](../best-practices/css-custom-properties-bridge-tokens-to-components.md), [`../best-practices/dark-mode-via-prefers-color-scheme.md`](../best-practices/dark-mode-via-prefers-color-scheme.md), the [`../skills/design-tokens-scaffolding/SKILL.md`](../skills/design-tokens-scaffolding/SKILL.md) drift-audit, and [`../knowledge/design-systems-and-component-architecture-2026.md`](../knowledge/design-systems-and-component-architecture-2026.md).

**Sources for the tooling cited:** the **Design Tokens Format Module reached its first stable version (2025.10) on 2025-10-28** via the W3C Design Tokens Community Group — https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/ and https://www.designtokens.org/tr/drafts/format/ ; Style Dictionary v4 ships first-class DTCG support (`$value`/`$type`/`$description`, `convertToDTCG`) — https://v4.styledictionary.com/reference/utils/dtcg/ (retrieved 2026-06-05). Tooling versions are volatile — `[verify-at-use]`.
