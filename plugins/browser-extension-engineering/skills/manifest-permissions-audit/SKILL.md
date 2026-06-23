---
name: manifest-permissions-audit
description: "Audit a browser extension's manifest.json against the least-privilege bar and Manifest V3 conformance: every permission and host match justified, activeTab/optional-permission opportunities, no remotely-hosted code, scoped web_accessible_resources, and the store-review risk each entry carries. Reach for this before a store submission, after a permissions rejection, or when reviewing an inherited extension."
---

# Skill: Manifest & Permissions Audit

Every permission an extension requests is a store-review risk and a user-trust
cost. This skill audits a `manifest.json` for *least privilege* and MV3
conformance, and returns a prioritized fix list. Used by both agents.

## Step 0 — One opinion up front: justify every grant, or drop it

The default verdict on any permission is "remove it." Keep it only if there's a
concrete feature that breaks without it. The narrowest grant that works is always
the right one.

## Step 1 — Host permissions

| Smell | Fix |
|---|---|
| `<all_urls>` / `*://*/*` | Narrow to specific match patterns; if interaction is user-initiated, prefer `activeTab` (grants the current tab on click, no broad grant). |
| Broad host perms for an occasional feature | Move to **optional** `host_permissions`, requested at runtime via `permissions.request()`. |
| Host perms requested at install with no immediate use | Defer to runtime/optional. |

`activeTab` is the single biggest permissions win for user-initiated extensions —
it sidesteps the "this extension can read all your data on all sites" warning.

## Step 2 — API permissions

For each entry in `permissions`:

- Name the feature that requires it. No feature → drop it.
- Prefer **`declarativeNetRequest`** over the deprecated blocking `webRequest`
  (MV3 removed blocking `webRequest` for most cases).
- Flag high-review-risk permissions (broad host access, `tabs` for URL reading,
  `scripting`, `cookies`, `nativeMessaging`) and confirm each is truly needed.
- Move anything used only occasionally to **`optional_permissions`**.

## Step 3 — MV3 conformance

- `manifest_version: 3`.
- Background is a **service worker** (`background.service_worker`), not a
  `background.page`/`scripts` with `persistent`.
- **No remotely-hosted code** — all executable JS is in the package. No
  `content_security_policy` loosened to allow remote scripts; no remote module
  import or `eval` of fetched code. (A hard rejection if present.)
- `action` (not the MV2 `browser_action`/`page_action`).

## Step 4 — `web_accessible_resources`

- Expose only the specific resources needed.
- Scope `matches` to the specific origins that need them — never `<all_urls>`/`*`.
- Each exposed resource is reachable by web pages, so treat it as an attack
  surface.

## Step 5 — Output: a prioritized fix list

1. **Rejection blockers** — remotely-hosted code, MV2 leftovers, permissions far
   exceeding the stated purpose.
2. **Least-privilege wins** — `<all_urls>`→`activeTab`/narrow match;
   install-time→optional; over-broad `web_accessible_resources`.
3. **Hardening** — drop unused permissions, tighten CSP, narrow content-script
   matches.

Each finding states the corrected manifest entry and its store-review-risk
rationale. Pair with [`store-submission-readiness`](../store-submission-readiness/SKILL.md)
before submitting. See [`../../knowledge/manifest-v3-architecture.md`](../../knowledge/manifest-v3-architecture.md)
for the permissions-minimization decision tree.
