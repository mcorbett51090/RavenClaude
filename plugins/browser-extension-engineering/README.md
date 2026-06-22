# browser-extension-engineering plugin

> The **engineering of browser extensions** for the RavenClaude marketplace:
> building, shipping, and maintaining cross-browser extensions on **Manifest V3**.
> It answers **"how do I structure this extension, request the least permission,
> and get it through store review?"** — the extension runtime, manifest, and store
> surface that neither `frontend-engineering` (app-grade React UI) nor
> `desktop-app-engineering` (Electron/Tauri) owns.

**Designed for:** an engineer building a Chrome / Edge / Firefox extension who
needs the MV3 architecture right (service workers, content scripts, messaging),
a least-privilege permissions posture, and a clean path through the store review
pipelines.

## What this plugin gives you

- The **MV3 architecture** done right — the ephemeral service-worker background
  (and the MV2→MV3 "background page is gone" trap), content-script isolation,
  message passing, and `chrome.storage`.
- A **least-privilege permissions** posture — narrow `host_permissions`,
  `activeTab` over broad host access, optional permissions requested at runtime,
  and the review-risk each permission carries.
- A **store-submission readiness** path for the **Chrome Web Store**, **Edge
  Add-ons**, and **Firefox AMO** — the metadata, the privacy/permissions
  justification, and the common rejection reasons.
- The **cross-browser delta** — Chrome's callback APIs vs Firefox's promise-based
  `browser.*`, and where the WebExtensions surface diverges.

## The two agents

| Agent | Owns |
|---|---|
| `extension-architect` | The extension's shape: MV3 component layout (background/content/popup/options), the messaging topology, the permissions model + least-privilege posture, storage strategy, and the cross-browser/target decision. |
| `extension-implementation-engineer` | The build: the `manifest.json`, the service worker (event-driven, no global state assumptions), content scripts + injection, message passing, storage code, and packaging for each store. |

## The two skills

| Skill | What's inside |
|---|---|
| `manifest-permissions-audit` | An audit of a `manifest.json` against the least-privilege bar: every permission and host match justified, `activeTab`/optional-permissions opportunities, MV3 conformance, and the store-review risk each entry carries. |
| `store-submission-readiness` | A pre-submission checklist for Chrome Web Store / Edge Add-ons / Firefox AMO: required metadata, the privacy + permissions justification, single-purpose conformance, and the common rejection reasons to pre-empt. |

## When to use it

- You're starting an extension and need the MV3 architecture + permissions model
  right before you write code.
- Your extension was rejected (often for excessive permissions or a missing
  justification) and you need to fix the manifest and resubmit.
- You're migrating an MV2 extension to MV3 and hit the service-worker lifecycle
  and background-page removal.

## When *not* to use it

- You need app-grade React UI architecture (a popup that's basically an app) —
  that's `frontend-engineering`. This plugin owns the *extension shell* around it.
- You're building a desktop app (Electron/Tauri) — that's `desktop-app-engineering`.
- You need a security *verdict* — escalate to `security-engineering` /
  `ravenclaude-core/security-reviewer`. This plugin owns the extension-specific
  least-privilege posture and escalates verdicts.

## Seams to neighbouring plugins

- **`frontend-engineering`** — the popup/options *UI* (React/TS) inside the shell.
- **`desktop-app-engineering`** — Electron/Tauri desktop apps (the sibling, not this).
- **`api-engineering`** — the backend the extension talks to (CORS, auth, webhooks).
- **`auth-identity`** — sign-in flows inside an extension (OAuth in MV3).
- **`security-engineering`** — security verdicts on the extension's surface.
- **`ravenclaude-core`** — the domain-neutral constitution + security-reviewer.

## Requires

- `ravenclaude-core@>=0.7.0`.

See [`CLAUDE.md`](CLAUDE.md) for the team constitution and house opinions.
