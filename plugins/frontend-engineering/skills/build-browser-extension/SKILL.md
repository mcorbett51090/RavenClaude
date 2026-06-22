---
name: build-browser-extension
description: "Build a Manifest V3 browser extension: decide which context owns each piece of logic (content script vs MV3 service worker vs injected page script vs popup/options), wire messaging between contexts, request the narrowest permissions (activeTab -> optional -> host -> all_urls), and pass the Chrome/Edge/Firefox store review. The popup/options UI seams to the React/state/perf agents."
---

# Build a Browser Extension (Manifest V3)

A browser extension is a multi-context distributed system: its UI is a frontend app, but its execution model (ephemeral service worker, isolated content scripts, a strict permission/store regime) is what makes it distinctive. Traverse the trees in [`knowledge/browser-extension-engineering.md`](../../knowledge/browser-extension-engineering.md) **before** placing logic or requesting a permission.

## 1. Architecture — where does each piece of logic live?

Pick the **least-privileged context that works** ("Where should this logic live?" tree):

| Need | Context |
|---|---|
| Read/modify a page's **DOM** (not its JS) | **Content script** (isolated world) |
| Reach the page's **own JS / window globals** | **Injected page script** (main world) — untrusted, bridge via `postMessage` |
| Privileged `chrome.*` APIs (tabs, alarms, network), background work | **Service worker** (MV3 background) — ephemeral, no DOM |
| Toolbar UI | **Popup** (`action.default_popup`) — transient |
| Settings / full page | **Options / extension page** |

**Never assume two contexts share memory.** Cross-context state lives in `chrome.storage` or is passed by message.

## 2. Service worker discipline

MV3's background is **event-driven and terminated when idle** — re-think any "long-running/stateful" design:

- Register **all** event listeners at the **top level**, synchronously, on every load — not inside an async callback, or the wake-up event is missed.
- Hold **no** in-memory state you can't lose; persist to `chrome.storage`, re-hydrate on wake.
- No DOM, no `localStorage` — it's a worker. (See [`keep-the-mv3-service-worker-stateless-and-ephemeral.md`](../../best-practices/keep-the-mv3-service-worker-stateless-and-ephemeral.md).)

## 3. Messaging

- Content script ↔ service worker ↔ popup/options → `chrome.runtime.sendMessage` / `onMessage`, or a long-lived `chrome.runtime.connect` `Port`; service worker → a tab → `chrome.tabs.sendMessage`.
- Content script (isolated) ↔ injected page script (main world) → `window.postMessage` is the **only** bridge — **validate `origin`, `source`, and message shape**; treat it as untrusted input.
- Return `true` from an `onMessage` listener that responds asynchronously, and remember the worker may have been asleep (don't rely on prior in-memory state).

See [`isolate-content-scripts-from-the-page.md`](../../best-practices/isolate-content-scripts-from-the-page.md).

## 4. Least-privilege permissions

Walk the permissions tree narrowest-first — escalate only when a concrete feature forces it, and justify each escalation in the listing:

1. **`activeTab`** — temporary current-tab access on a user gesture; no install warning. The default for user-initiated, current-tab actions.
2. **Specific API perms** — exactly the `chrome.*` APIs you use (`storage`, `alarms`, `scripting`).
3. **Narrow `host_permissions`** — specific match patterns (`https://api.example.com/*`), never `<all_urls>` reflexively.
4. **`optional_permissions` / `optional_host_permissions`** — request broad access at runtime with `chrome.permissions.request()` on a user action.
5. **`<all_urls>`** — only when running on arbitrary sites *is* the core function; expect stricter review.

Re-audit at every release; drop unused permissions. See [`request-the-narrowest-extension-permissions.md`](../../best-practices/request-the-narrowest-extension-permissions.md).

## 5. Store submission checklist

- [ ] `manifest_version: 3`, version bumped.
- [ ] **No remotely-hosted code** — all executable JS ships in the package (fetch data, not code).
- [ ] Permissions minimized and **re-audited**; each (and any broad host access) justified.
- [ ] Privacy policy + accurate data-use disclosures.
- [ ] Icons, screenshots, listing copy.
- [ ] Tested on each target: Chrome, **Edge** (Chromium — usually drop-in), **Firefox** (`browser.*`/Promise differences, `webextension-polyfill`, `browser_specific_settings.gecko.id`, every version signed).
- [ ] `declarativeNetRequest` rules (if any) validated; content-script match patterns as narrow as the feature allows.
- [ ] After publish: staged/percentage rollout where supported; monitor reviews + error telemetry.

## Seam — the UI is a frontend app

The **popup / options UI** is an ordinary frontend and routes to the existing specialists, **not** this skill:

- **Components, forms, accessibility** → [`react-implementation-engineer`](../../agents/react-implementation-engineer.md).
- **State / data** → [`frontend-state-and-data-engineer`](../../agents/frontend-state-and-data-engineer.md) — note `chrome.storage` (+ `onChanged`) is the persistence/sync layer; don't bolt a global store onto an already-transient popup.
- **Popup open speed / bundle** → [`frontend-performance-engineer`](../../agents/frontend-performance-engineer.md) — a popup must open fast, so bundle discipline matters *more*, not less.

This skill owns only the MV3-distinctive layer (context placement, service-worker lifetime, messaging, permissions, store review). Full reference + the two Mermaid decision trees: [`knowledge/browser-extension-engineering.md`](../../knowledge/browser-extension-engineering.md). MV3 specifics are volatile — verify at use against the Chrome/MDN/Firefox docs.
