# Default to "no PCF" — reach for a custom control only when a cheaper surface genuinely can't deliver the UI

**Status:** Pattern — strong default; build a PCF only with a written reason the cheaper surfaces were ruled out.

**Domain:** PCF / Canvas + Model-driven apps

**Applies to:** `power-platform`

---

## Why this exists

A PCF control is the most expensive UI mechanism on the platform to build, test, version, and maintain: TypeScript, a manifest API contract, an npm/webpack build, a solution-packaging step, and a bundle that loads on every form render. Roughly 70% of "we need a custom control" asks are delivered faster by a Custom Page or a canvas/modern Fluent control. The constitution's house rule §3 #7 ("lowest-tier mechanism that does the job") applies directly: a PCF that re-implements something a canvas component could build in an afternoon is wasted engineering and a permanent maintenance tax. The right question is never "can a PCF do this?" (it usually can) but "is a PCF the *cheapest* surface that can?"

## How to apply

Walk the cost ladder before writing manifest XML. Build a PCF only when the requirement lands on its genuine sweet spot.

```text
Need a custom UI? Ask, cheapest first:
  1. Modern/Fluent canvas control (no code)      → simple themed input
  2. Custom Page / canvas component              → most interactive UIs, reusable in-app
  3. JS web resource (model-driven)              → MDA form-context logic JS can do
  4. PCF control                                 → ONLY when 1–3 genuinely can't
```

PCF is the right answer when you need: complex visualizations a no-code control can't render (D3, charts, Mermaid), specialized inputs (signature pad, constrained rich-text, code editor), or one control reused across many apps with identical behavior and a versioned contract.

**Do:**

- State, in the PR, which cheaper surfaces you ruled out and why.
- Prefer a Custom Page or canvas component for in-app interactive UI; prefer a quick-view form / business rule for related-record peeks and show/hide logic.
- Reserve PCF for genuine visualization/specialized-input/cross-app-reuse cases.
- Keep the bundle under ~2 MB — it loads on every form render; tree-shake and lazy-load heavy deps.

**Don't:**

- Build a PCF "because it's the pro-code way" when a Custom Page ships the same UI in an afternoon.
- Use `pac pcf push` as a release mechanism — it's a dev-loop tool; ship through a managed solution import.
- `fetch()` the Dataverse Web API directly — use `context.webAPI`, which respects the platform's auth/quota.

## Edge cases / when the rule does NOT apply

- **Reuse across many apps with a stable contract** — the maintenance tax amortizes; PCF wins even for moderately simple controls when the same behavior is needed in 5+ apps.
- **Power Pages** — React virtual controls / platform libraries are **not supported** there; a *standard* (non-virtual) PCF or a web template is the mechanism, not a Custom Page. See the cross-surface decision tree.
- **Hard accessibility or theming requirement** a no-code control can't meet — a Fluent v9 virtual control may be the cleanest path even where a Custom Page nominally works.

## See also

- [`../skills/dataverse-web-resources/resources/ux-decision-guide.md`](../skills/dataverse-web-resources/resources/ux-decision-guide.md) — "Custom Page vs Web Resource" + "Prefer built-in controls over Custom PCF"
- [`../knowledge/pcf-react-fluent-platform-libraries.md`](../knowledge/pcf-react-fluent-platform-libraries.md) — `## Decision Tree: PCF — Which React surface?`
- [`../knowledge/apps-decision-trees.md`](../knowledge/apps-decision-trees.md) — `Decision Tree: App UI surface — PCF vs web resource vs canvas component vs Custom Page`
- [`./apps-pcf-lifecycle-and-cleanup.md`](./apps-pcf-lifecycle-and-cleanup.md)
- [`../agents/pcf-developer.md`](../agents/pcf-developer.md) — "Defaults to 'no PCF' until convinced"

## Provenance

From `pcf-developer.md` Personality + Opinions ("Default to Custom Page or canvas component before reaching for PCF", "~70% of cases") and constitution §3 #7 (lowest-tier mechanism). Power Pages exception cross-checked against `knowledge/pcf-react-fluent-platform-libraries.md`.

---

_Last reviewed: 2026-05-30 by `claude`_
