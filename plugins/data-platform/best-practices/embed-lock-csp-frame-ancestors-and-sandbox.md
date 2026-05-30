# Lock the embed boundary — explicit `frame-ancestors`, a minimal `sandbox`, and origin-checked postMessage

**Status:** Absolute rule — an embedded dashboard ships with an allow-listed CSP, a least-privilege iframe sandbox, and validated message origins. Security-sensitive: any embed/CSP change escalates to `ravenclaude-core/security-reviewer`.

**Domain:** Embed auth / CSP + iframe sandboxing

**Applies to:** `data-platform`

---

## Why this exists

A short-lived scoped token gets the right data *into* the embed; the CSP/iframe boundary controls who can put a frame *around* it and what that frame can do. Three breaks recur. **(1) `frame-ancestors *`** (or no CSP at all) lets any site embed-jack the dashboard inside their own page and harvest a logged-in viewer's data — clickjacking with a real session. **(2) An iframe with no `sandbox`** runs with full permissions; one with `allow-top-navigation` can redirect the parent page to a phishing clone. **(3) Unchecked `postMessage`** — a handler that acts on `event.data` without verifying `event.origin`, or an embed that posts to `'*'` — leaks filter state and tenant context to any listener. None of these are exotic; they're the default-insecure settings you get by *not* configuring the boundary, which is why "the host page sets no CSP" makes the whole security review skip.

## How to apply

Allow-list the embedding origins, start the sandbox minimal, and validate every message's origin and shape.

```http
# Host page CSP — explicit allow-list, never '*'. 'none' if the dashboard isn't third-party-embedded.
Content-Security-Policy:
  frame-ancestors 'self' https://client-app.example.com;
  frame-src 'self' https://dashboards.example.com;
  connect-src 'self' https://api.cube.example.com;
  script-src 'self' 'nonce-{server-generated}';
```

```html
<!-- Least-privilege sandbox: start here, add a flag only when a feature needs it. -->
<iframe src="https://dashboards.example.com/embed/abc123"
        sandbox="allow-scripts allow-same-origin"></iframe>
<!-- ❌ allow-top-navigation lets the frame redirect the parent (phishing). -->
```

```javascript
window.addEventListener('message', (event) => {
  if (event.origin !== 'https://dashboards.example.com') return;   // ALWAYS check origin
  if (typeof event.data !== 'object' || !event.data.type) return;  // ALWAYS validate shape
  /* safe to act */
});
embedFrame.contentWindow.postMessage(msg, 'https://dashboards.example.com'); // explicit target, not '*'
```

**Do:**
- Set `frame-ancestors` to an explicit origin allow-list (or `'none'` for admin-only internal dashboards).
- Start the iframe at `sandbox="allow-scripts allow-same-origin"` and add flags only as features require.
- Check `event.origin` against an allow-list **and** validate `event.data` shape in every message handler; post with an explicit target origin.
- Set the companion CSP directives (`frame-src`, `connect-src` for the Cube/JWT endpoints, nonce-based `script-src`).

**Don't:**
- Use `frame-ancestors *`, omit the CSP entirely, or run an iframe with no `sandbox`.
- Add `allow-top-navigation` (parent-redirect / phishing risk) or `unsafe-eval` "because Cube needs it" (it doesn't — verify).
- Trust `event.data` without an origin check, or `postMessage(..., '*')`.

## Edge cases / when the rule does NOT apply

- **Web-component embeds (Embeddable.com)** — no iframe; the boundary is the shadow-DOM. Keep CSP `connect-src` + the short-lived-token-attribute rule; `sandbox`/`frame-ancestors` don't apply, but a shadow-root is mandatory.
- **Cube + custom React (no iframe)** — direct API calls; the relevant directive is `connect-src` allowing the Cube origin, not `frame-ancestors`.
- **Power BI Embedded** — `powerbi-client` manages the iframe internally; CSP must allow `frame-ancestors` for the F-SKU embed origin and Microsoft requires CSP **nonce** values for the embed page's inline scripts.

## See also

- [`./embed-never-ship-the-service-key.md`](./embed-never-ship-the-service-key.md) — the token that travels through this boundary
- [`./issue-short-lived-jwts-for-embeds.md`](./issue-short-lived-jwts-for-embeds.md) — token lifetime/claims
- [`../skills/embed-csp-and-iframe-sandboxing/SKILL.md`](../skills/embed-csp-and-iframe-sandboxing/SKILL.md) — per-tool CSP/sandbox patterns + the full anti-pattern list
- MDN: [CSP `frame-ancestors`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/frame-ancestors), [iframe `sandbox`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe#sandbox), [`window.postMessage`](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)

## Provenance

Distilled from the `embed-csp-and-iframe-sandboxing` skill (the three concerns + anti-pattern list), CLAUDE.md anti-pattern "Embedding without documenting the CSP `frame-ancestors` policy", and the dashboard-builder agent's CSP discipline. CSP/iframe/postMessage semantics are stable web-platform behavior (MDN-cited). `[verify-at-build]` Power BI Embedded CSP nonce requirement — confirm against current Microsoft embed docs. Security-sensitive — escalate to `ravenclaude-core/security-reviewer`.

---

_Last reviewed: 2026-05-30 by `claude`_
