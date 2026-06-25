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
| Manifest | **MV3 only** (MV2 fully sunset — see below) | MV3 **and** MV2 (Mozilla still supports MV2) |
| Request modification | **`declarativeNetRequest`** only (no blocking `webRequest`) | **`declarativeNetRequest`** *and* MV2-style **blocking `webRequest`** |
| Extension id | Assigned by store | Often explicit via `browser_specific_settings.gecko.id` |

### MV2 is fully sunset on Chrome — Firefox still supports MV2-style blocking `webRequest`

This is the load-bearing divergence for a cross-browser content blocker / privacy
extension:

- **Chrome:** MV2 is **fully sunset** — disabled on **all channels**, the
  `ExtensionManifestV2Availability` enterprise exemption **ended with Chrome 139
  (mid-2025)**, and users **cannot re-enable** it. Chrome offers **only**
  `declarativeNetRequest` for request modification; there is no blocking
  `webRequest` and no "stay on MV2" option. _(Retrieved 2026-06-25,
  [MV2 deprecation timeline](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline).)_
- **Firefox:** remains the **only major engine still supporting MV2-style blocking
  `webRequest`** (alongside `declarativeNetRequest`), and Mozilla continues to
  support MV2 itself. An extension that genuinely needs to *inspect/modify/block*
  requests at runtime (rather than via static `declarativeNetRequest` rules) can
  do so **on Firefox but not on Chrome**.

**Design consequence:** don't assume a blocking-`webRequest` design ports to
Chrome. For Chrome, express the behavior as `declarativeNetRequest` rules (or
accept the feature is Firefox-only); branch the request-handling layer per engine
when the two genuinely diverge. `[verify policy specifics at use]`

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

- Chromium MV3 (the **only** Chrome target — MV2 is fully sunset): background
  **service worker**.
- Firefox: supports MV3 service workers; historically also supported an
  event-page-style background, and still supports MV2 backgrounds. Confirm the
  current Firefox MV3 background model against AMO docs before relying on
  engine-specific behavior `[verify at use]`.

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
2. **Chrome is MV3-only** — MV2 is fully sunset (disabled on all channels, the
   enterprise exemption ended with Chrome 139 / mid-2025, no user re-enable). Build
   MV3 for Chrome + Edge; there is no MV2 fallback to author or migrate back to.
3. **Write to `browser.*` + promises via the polyfill** if targeting Firefox.
4. **Watch the blocking-`webRequest` divergence** — a runtime request-blocking
   design works on Firefox but not Chrome (Chrome = `declarativeNetRequest` only);
   branch the request layer per engine where they genuinely diverge.
5. **Keep one MV3 package** for Chrome + Edge; branch only where an API genuinely
   diverges.
6. **Audit per store** with [`store-submission-readiness`](../skills/store-submission-readiness/SKILL.md)
   — the permissions bar is the same, the metadata/forms differ.

> Re-verification note: the most likely facts to drift here are each store's
> review requirements and per-browser API availability. Confirm against current
> store developer documentation and update the retrieval date before quoting a
> specific policy in a deliverable.
