---
name: build-browser-extension
description: "End-to-end workflow to build a Manifest V3 browser extension: decide which context owns each piece of logic (content script vs MV3 service worker vs injected page script vs popup/options), wire messaging between contexts, request the narrowest permissions (activeTab -> optional -> host -> all_urls), and pass Chrome/Edge/Firefox store review. Complements the manifest-permissions-audit and store-submission-readiness skills. The popup/options UI seams to frontend-engineering."
---

# Skill: Build a Browser Extension (Manifest V3)

A browser extension is a multi-context distributed system: its UI is a frontend
app, but its execution model (ephemeral service worker, isolated content scripts,
a strict permission/store regime) is what makes it distinctive. This skill is the
**end-to-end build workflow**; pair it with the deeper audit/checklist skills it
references at each step. Traverse the decision trees in
[`../../knowledge/where-logic-lives.md`](../../knowledge/where-logic-lives.md) and
[`../../knowledge/manifest-v3-architecture.md`](../../knowledge/manifest-v3-architecture.md)
**before** placing logic or requesting a permission.

## 1. Architecture — where does each piece of logic live?

Pick the **least-privileged context that works** (full tree:
[`../../knowledge/where-logic-lives.md`](../../knowledge/where-logic-lives.md)):

| Need | Context |
|---|---|
| Read/modify a page's **DOM** (not its JS) | **Content script** (isolated world) |
| Reach the page's **own JS / window globals** | **Injected page script** (main world) — untrusted, bridge via `postMessage` |
| Privileged `chrome.*` APIs (tabs, alarms, network), background work | **Service worker** (MV3 background) — ephemeral, no DOM |
| Toolbar UI | **Popup** (`action.default_popup`) — transient |
| Settings / full page | **Options / extension page** |

**Never assume two contexts share memory.** Cross-context state lives in
`chrome.storage` or is passed by message.

## 2. Service worker discipline

MV3's background is **event-driven and terminated when idle** — re-think any
"long-running/stateful" design:

- Register **all** event listeners at the **top level**, synchronously, on every
  load — not inside an async callback, or the wake-up event is missed.
- Hold **no** in-memory state you can't lose; persist to `chrome.storage`,
  re-hydrate on wake.
- No DOM, no `localStorage` — it's a worker. (See
  [`../../best-practices/treat-the-background-as-ephemeral.md`](../../best-practices/treat-the-background-as-ephemeral.md).)

## 3. Messaging

- Content script ↔ service worker ↔ popup/options → `chrome.runtime.sendMessage`
  / `onMessage`, or a long-lived `chrome.runtime.connect` `Port`; service worker →
  a tab → `chrome.tabs.sendMessage`.
- Content script (isolated) ↔ injected page script (main world) →
  `window.postMessage` is the **only** bridge — **validate `origin`, `source`, and
  message shape**; treat it as untrusted input.
- Return `true` from an `onMessage` listener that responds asynchronously, and
  remember the worker may have been asleep (don't rely on prior in-memory state).

See [`../../best-practices/message-pass-across-the-isolation-boundary.md`](../../best-practices/message-pass-across-the-isolation-boundary.md).

## 4. Least-privilege permissions

Walk the permissions tree narrowest-first — escalate only when a concrete feature
forces it, and justify each escalation in the listing:

1. **`activeTab`** — temporary current-tab access on a user gesture; no install
   warning. The default for user-initiated, current-tab actions.
2. **Specific API perms** — exactly the `chrome.*` APIs you use (`storage`,
   `alarms`, `scripting`).
3. **Narrow `host_permissions`** — specific match patterns
   (`https://api.example.com/*`), never `<all_urls>` reflexively.
4. **`optional_permissions` / `optional_host_permissions`** — request broad access
   at runtime with `chrome.permissions.request()` on a user action.
5. **`<all_urls>`** — only when running on arbitrary sites *is* the core function;
   expect stricter review.

Re-audit at every release; drop unused permissions. Run the deeper audit with
[`../manifest-permissions-audit/SKILL.md`](../manifest-permissions-audit/SKILL.md)
(and see [`../../best-practices/request-least-privilege-permissions.md`](../../best-practices/request-least-privilege-permissions.md)).

## 5. Store submission checklist

- [ ] `manifest_version: 3`, version bumped.
- [ ] **No remotely-hosted code** — all executable JS ships in the package (fetch
      data, not code). (See
      [`../../best-practices/no-remotely-hosted-code.md`](../../best-practices/no-remotely-hosted-code.md).)
- [ ] Permissions minimized and **re-audited**; each (and any broad host access)
      justified.
- [ ] `web_accessible_resources` scoped to specific files + origins, never `*`.
      (See [`../../best-practices/scope-web-accessible-resources.md`](../../best-practices/scope-web-accessible-resources.md).)
- [ ] Privacy policy + accurate data-use disclosures.
- [ ] Icons, screenshots, listing copy; single-purpose description that matches
      behavior.
- [ ] Tested on each target: Chrome, **Edge** (Chromium — usually drop-in),
      **Firefox** (`browser.*`/Promise differences, `webextension-polyfill`,
      `browser_specific_settings.gecko.id`, every version signed).
- [ ] `declarativeNetRequest` rules (if any) validated; content-script match
      patterns as narrow as the feature allows.
- [ ] After publish: staged/percentage rollout where supported; monitor reviews +
      error telemetry.

Run the full per-store readiness pass with
[`../store-submission-readiness/SKILL.md`](../store-submission-readiness/SKILL.md);
the cross-browser delta + the three pipelines live in
[`../../knowledge/cross-browser-and-stores.md`](../../knowledge/cross-browser-and-stores.md).

## Seam — the UI is a frontend app

The **popup / options UI** is an ordinary frontend and routes to
`frontend-engineering`, **not** this skill: components/forms/accessibility, client
state (note `chrome.storage` + `onChanged` is the persistence/sync layer — don't
bolt a global store onto an already-transient popup), and popup open-speed/bundle
discipline (a popup must open fast, so bundle discipline matters *more*, not
less). See [`../../CLAUDE.md`](../../CLAUDE.md) §1 and §3.

This skill owns only the MV3-distinctive layer (context placement, service-worker
lifetime, messaging, permissions, store review). Full reference + the two Mermaid
decision trees:
[`../../knowledge/where-logic-lives.md`](../../knowledge/where-logic-lives.md)
(where logic lives) and
[`../../knowledge/manifest-v3-architecture.md`](../../knowledge/manifest-v3-architecture.md)
(permissions-minimization). MV3 specifics are volatile — verify at use against the
Chrome/MDN/Firefox docs.
