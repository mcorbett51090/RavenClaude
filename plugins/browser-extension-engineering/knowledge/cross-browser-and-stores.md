# Cross-browser & store pipelines (dated reference)

> The cross-browser API delta and the three store submission pipelines. The API
> *shape* (callbacks vs promises) is durable; **store policies and exact API
> availability are volatile** — every store-policy specific carries a retrieval
> date and a re-verify-at-use rider per the marketplace accuracy discipline.
> _Baseline retrieved 2026-06-15; confirm against each store's current developer
> docs before relying on a specific policy detail._

## The Chrome vs Firefox API delta

| | Chrome / Edge (Chromium) | Firefox |
|---|---|---|
| Namespace | `chrome.*` | `browser.*` (also aliases `chrome.*`) |
| Async style | **Callbacks** (MV3 `chrome.*`); some promise support added over time | **Promises** (native) |
| Manifest | MV3 | MV3 (with some divergences) |
| Extension id | Assigned by store | Often explicit via `browser_specific_settings.gecko.id` |

### The polyfill

Use Mozilla's **`webextension-polyfill`** to write promise-based `browser.*` code
that runs on both engines, or wrap calls yourself. Don't assume API parity — some
APIs exist on one engine and not the other, and behavior can differ. Flag the
divergences during architecture, not after.

```js
// With webextension-polyfill, this works on Chrome, Edge, and Firefox:
const { settings } = await browser.storage.local.get("settings");
```

## Background-script divergence

- Chromium MV3: background **service worker**.
- Firefox: supports MV3 service workers; historically also supported an
  event-page-style background. Confirm the current Firefox MV3 background model
  against AMO docs before relying on engine-specific behavior `[verify at use]`.

## The three store pipelines

### Chrome Web Store

- The largest audience; Chromium MV3 package.
- Developer dashboard: listing assets, the **data-use disclosure** form, and a
  **per-permission justification** (especially for broad host access).
- Review can be automated + manual; broad permissions lengthen review.
- Common rejections: excessive/unjustified permissions, broad host access without
  need, listing/behavior mismatch, obfuscated code, remotely-hosted code.

### Microsoft Edge Add-ons

- Chromium-based — the **same MV3 package usually works**.
- Partner Center listing + its own certification/review.
- Hold the same least-privilege/single-purpose bar; Edge reviews independently.

### Firefox AMO (addons.mozilla.org)

- Requires the `browser.*`/promise migration or the polyfill.
- An explicit extension `id`.
- May perform **source-code review**; run `web-ext lint`, and minified code may
  need accompanying source.
- Common rejections: minified/obfuscated code without source, undeclared remote
  resources, permission overreach.

## Cross-browser strategy summary

1. **Decide targets at architecture time** — it changes the API surface and packaging.
2. **Write to `browser.*` + promises via the polyfill** if targeting Firefox.
3. **Keep one MV3 package** for Chrome + Edge; branch only where an API genuinely
   diverges.
4. **Audit per store** with [`store-submission-readiness`](../skills/store-submission-readiness/SKILL.md)
   — the permissions bar is the same, the metadata/forms differ.

> Re-verification note: the most likely facts to drift here are each store's
> review requirements and per-browser API availability. Confirm against current
> store developer documentation and update the retrieval date before quoting a
> specific policy in a deliverable.
