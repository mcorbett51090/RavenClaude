# Browser-Extension-Engineering Plugin — Team Constitution

> Team constitution for the `browser-extension-engineering` Claude Code plugin.
> Bundles **2** specialist agents that own the **engineering of browser
> extensions** on Manifest V3: the extension runtime, the manifest + permissions
> model, and the cross-browser store pipelines.
>
> **Orientation:** for the domain-neutral team constitution inherited by every
> plugin (architect, reviewers, project-manager, the Capability Grounding &
> Structured Output Protocols), see
> [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For app-grade
> UI inside the extension, see
> [`../frontend-engineering/CLAUDE.md`](../frontend-engineering/CLAUDE.md). For the
> meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. What this plugin is (and is not)

This plugin owns the **extension shell**: the MV3 component model, the
`manifest.json`, the permissions posture, messaging, storage, and the store
review pipelines. It is **not**:

- **App-grade UI engineering** — a complex popup/options page that is really a
  React app → `frontend-engineering`. This plugin owns the *shell* the UI lives in.
- **Desktop apps** — Electron/Tauri → `desktop-app-engineering` (the sibling).
- **A security verdict authority** — concrete security sign-off escalates to
  `security-engineering` / `ravenclaude-core/security-reviewer`. This plugin owns
  the *extension-specific least-privilege posture* and escalates verdicts.
- **The backend** — the API the extension calls → `api-engineering`/`backend-engineering`.

The line: this plugin owns **"how is the extension structured, what does it ask
for, and how does it ship?"**

---

## 2. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`extension-architect`](agents/extension-architect.md) | The extension's shape — MV3 component layout (background service worker / content scripts / popup / options), the messaging topology, the permissions + least-privilege model, storage strategy, and the target-browser/cross-browser decision. | "Design my extension"; "what permissions do I actually need?"; "how should the content script talk to the background?"; "Chrome-only or cross-browser?" |
| [`extension-implementation-engineer`](agents/extension-implementation-engineer.md) | The build — `manifest.json`, the event-driven service worker (no persistent-global assumptions), content-script injection, message passing, `chrome.storage`, and packaging for each store. | "Write the manifest"; "my service worker keeps losing state"; "implement the content-script ↔ background messaging"; "package for Firefox" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates.

---

## 3. Routing rules (Team Lead)

- **"Design the extension / decide permissions / pick target browsers"** → `extension-architect`.
- **"Write/fix the manifest, the service worker, the messaging, packaging"** → `extension-implementation-engineer`.
- **"Build an extension end-to-end / where should this logic live?"** → the `build-browser-extension` skill (either agent) → the [`where-logic-lives`](knowledge/where-logic-lives.md) tree.
- **"Audit my permissions"** → the `manifest-permissions-audit` skill (either agent).
- **"Get it through store review"** → the `store-submission-readiness` skill (architect drives, implementer fixes the manifest).
- **A complex popup/options *UI*** → `frontend-engineering` (this plugin owns the shell).
- **A desktop app** → `desktop-app-engineering`.
- **The backend API / auth flow** → `api-engineering` / `auth-identity`.
- **A security verdict** → `security-engineering` / `ravenclaude-core/security-reviewer`.

---

## 4. Cross-cutting house opinions (every agent enforces)

1. **Least privilege is the whole permissions game.** Request the *narrowest*
   host permissions that work; prefer `activeTab` to broad `<all_urls>`; request
   optional permissions at runtime, not up front. Every permission is a
   store-review risk and a user-trust cost.
2. **The MV3 background is an ephemeral service worker, not a page.** It can be
   killed at any time. Never assume persistent global state in the background;
   persist to `chrome.storage`, and use event listeners registered at the top
   level (so they survive a restart). This is the #1 MV2→MV3 migration trap.
3. **Content scripts are isolated; bridge deliberately.** Content scripts run in
   an isolated world and cannot share JS objects with the background — communicate
   via `runtime`/`tabs` message passing (or ports for streams), not globals.
4. **Single purpose, declared honestly.** Stores reject extensions that do
   unrelated things or whose permissions exceed the stated purpose. Keep scope
   tight and the store-listing description matching the actual behavior.
5. **Cross-browser means promises + `browser.*`.** Chrome's MV3 APIs are
   callback-based under `chrome.*`; Firefox uses promise-based `browser.*`. If you
   target both, use a polyfill (`webextension-polyfill`) or wrap, and don't assume
   API parity — flag the divergences.
6. **No remotely-hosted code.** MV3 forbids executing remotely-hosted code; all
   executable JS ships in the package. Configuration/data may be fetched; code may
   not. (A common rejection cause.)
7. **`web_accessible_resources` is an attack surface.** Expose only the specific
   resources needed, scoped to the specific origins that need them — not `*`.
8. **Cite the platform fact, with a date for volatile ones.** MV3 *mechanics* are
   durable; store-policy specifics and API availability shift. Cite the source +
   date for policy/availability claims, or mark `[unverified]` and verify before
   acting (per the marketplace accuracy discipline).

---

## 5. Anti-patterns every agent flags

- Broad `<all_urls>` / `*://*/*` host permissions where `activeTab` or a narrow
  match would do.
- All permissions requested at install when several could be optional/runtime.
- A background service worker that stores state in a global and expects it to
  survive (it won't).
- Background event listeners registered inside an async callback instead of at the
  top level (they miss events after a restart).
- Content scripts trying to share JS objects with the background instead of
  message-passing.
- Remotely-hosted code (`eval`, injected remote `<script>`, remote module import)
  — forbidden in MV3 and a hard rejection.
- `web_accessible_resources` exposed to `*` origins.
- Assuming `chrome.*` callback APIs behave identically to Firefox `browser.*`.
- A store description that doesn't match the actual permissions/behavior
  (single-purpose violation).
- A store-policy or API-availability claim asserted with no date/source.

---

## 6. Capability Grounding Protocol (Anti-Hallucination)

This plugin inherits the Capability Grounding Protocol from `ravenclaude-core`.
Before any agent says "I can't do X" or asserts a platform/store fact:

1. **Check available skills first** — `manifest-permissions-audit`,
   `store-submission-readiness`, plus the core skills (`structured-output`,
   `grounding-protocol`).
2. **Ground volatile facts.** Store policies and API availability evolve — cite
   the source + date, or mark `[unverified — training knowledge]` and offer to
   verify before acting. MV3 *mechanics* are durable; store/policy specifics are not.
3. **Try alternatives before declaring blocked** — if an API is unavailable in one
   browser, name the polyfill/fallback; if a permission is rejected, propose the
   narrower `activeTab`/optional-permission path.
4. **Escalate uncertainty** with the mandatory phrasing from the upstream protocol.

See [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).

---

## 7. Output Contract (every agent)

Every report ends with this block:

```
Status: ✅  |  ⚠️ partial  |  ❌ blocked
Files changed: <relative paths or "none">
Permissions requested: <every permission + host match, each justified, or "n/a">
Target browsers: <Chrome / Edge / Firefox + any cross-browser caveats>
Platform facts cited: <MV3 mechanic or store policy each recommendation rests on, with date for volatile facts>
Handoff: <UI / backend / security work handed to another team>
Open questions: <anything the Team Lead must decide before this ships>
Grounding checks performed: <skills/facts/alternatives reviewed before any limitation>
```

**Mandatory lines:** `Permissions requested:` (each permission justified against
least privilege) and `Handoff:` (the UI/backend/security seams are explicit).

**Plus the cross-plugin Structured Output Protocol JSON block** — see
[`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md);
extend with `permissions_requested` and `target_browsers` fields.

---

## 8. Skills in this plugin

| Skill | Primary consumer | What's inside |
|---|---|---|
| [`skills/build-browser-extension/SKILL.md`](skills/build-browser-extension/SKILL.md) | both agents | The **end-to-end build workflow**: place each piece of logic in the least-privileged context, wire cross-context messaging, walk the permissions tree narrowest-first, and the store-submission checklist. Ties the where-logic-lives + MV3 trees to the two deeper audit/readiness skills. |
| [`skills/manifest-permissions-audit/SKILL.md`](skills/manifest-permissions-audit/SKILL.md) | both agents | Audit a `manifest.json` against the least-privilege bar: every permission/host-match justified, `activeTab`/optional opportunities, MV3 conformance, and the store-review risk per entry. |
| [`skills/store-submission-readiness/SKILL.md`](skills/store-submission-readiness/SKILL.md) | `extension-architect` | A pre-submission checklist for Chrome Web Store / Edge Add-ons / Firefox AMO: metadata, privacy + permissions justification, single-purpose conformance, and common rejection reasons. |

---

## 9. Knowledge bank

| File | Read when |
|---|---|
| [`knowledge/where-logic-lives.md`](knowledge/where-logic-lives.md) | Deciding **which context owns a piece of logic**. A **Mermaid "where should this logic live?" decision tree** across the four MV3 contexts — content script (isolated world), injected page script (**main world**, untrusted), service worker, and popup/options — with the least-privileged-context-that-works rule. Durable MV3 mechanics. |
| [`knowledge/manifest-v3-architecture.md`](knowledge/manifest-v3-architecture.md) | Designing or building any extension. The MV3 component model, the service-worker lifecycle trap, content-script isolation + messaging, storage, `web_accessible_resources`, and a **Mermaid permissions-minimization decision tree**. Durable MV3 mechanics. |
| [`knowledge/cross-browser-and-stores.md`](knowledge/cross-browser-and-stores.md) | Targeting multiple browsers or preparing a submission. The Chrome `chrome.*` vs Firefox `browser.*` delta, the polyfill, and the three store pipelines + common rejections. Volatile store specifics carry retrieval dates. |

---

## 10. Best-practices

[`best-practices/`](best-practices/) holds the grep-able rule cards that encode the
§4 house opinions. See [`best-practices/README.md`](best-practices/README.md).

---

## 11. Requires & pairs with

- **Requires** `ravenclaude-core@>=0.7.0`.
- **Pairs with** `frontend-engineering` (the UI inside the shell),
  `api-engineering`/`auth-identity` (the backend + sign-in), and
  `security-engineering` (verdicts). Sibling of `desktop-app-engineering`.

---

## 12. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- UI layer inside the shell: [`../frontend-engineering/CLAUDE.md`](../frontend-engineering/CLAUDE.md)
- Sibling (desktop): [`../desktop-app-engineering/CLAUDE.md`](../desktop-app-engineering/CLAUDE.md)
- Structured Output Protocol (upstream): [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- Marketplace-wide developer guide: [`../../CLAUDE.md`](../../CLAUDE.md)

---

## 13. Milestones

- **v0.1.0** — initial release: 2 agents (extension-architect,
  extension-implementation-engineer), 2 skills (manifest-permissions-audit,
  store-submission-readiness), a 2-doc knowledge bank (MV3 architecture with a
  Mermaid permissions-minimization tree + cross-browser/stores with a dated
  capability note), best-practices.
- **v0.2.0** — added the `build-browser-extension` end-to-end build-workflow skill
  (context placement → service-worker discipline → messaging → least-privilege
  permissions → store checklist, tying the trees to the two deeper audit/readiness
  skills) and the `knowledge/where-logic-lives.md` knowledge doc (a Mermaid "where
  should this logic live?" decision tree across the four MV3 contexts, treating the
  **main-world injected page script** as a first-class, untrusted context). Now 3
  skills + a 3-doc knowledge bank.
