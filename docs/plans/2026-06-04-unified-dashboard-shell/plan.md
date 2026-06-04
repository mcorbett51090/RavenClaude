# Plan — Unified Dashboard Shell (one front door)

**Slug:** `unified-dashboard-shell` · **Depth:** quick · **Date:** 2026-06-04 · **Route:** stays local (pending G7)
**Synthesized from:** `plan-A.md` (Opus, system-architect), `plan-B.md` (Sonnet, frontend-coder), `gap-delta.md`. Resolutions applied per gap-delta column 5.

---

## Why we're doing this

Today RavenClaude exposes **three separate HTML surfaces** at three URLs: `index.html` (the polished marketing/landing surface), `plugins/ravenclaude-core/dashboard.html` (8.6MB, the comfort-posture + Norse tabs), and `repo-guide.html` (5.4MB, the "I want to…" use-case lookup across all plugins). Per `feedback_dashboards_over_slash_commands` (memory): "every tool, setting, AND activity metric visible in a dashboard; no memorized commands." Three URLs is two too many.

This plan makes **`index.html` the single front door**, keeping its visual treatment as the canonical shell, and lazy-loads the other two via `<iframe src>` under hash routes. `dashboard.html` and `repo-guide.html` remain on disk as the per-section content payloads (no generator changes; freshness Gates 11 + 13 unchanged). Bookmarks to those URLs still resolve.

---

## Phases

### Phase 0 — Verification gate (done in-session — see `claims-table.md` + the two panels' P0 sections)

Both panels independently verified the two BLOCK-tier outside-repo claims:

| Claim | Verdict | Evidence |
|---|---|---|
| **#8 CORS** | **Static-host is degraded-by-design.** GitHub-Pages-hosted `index.html` cannot fetch `127.0.0.1/__heimdall`. `_local_request_ok` (`plugins/ravenclaude-core/scripts/serve-dashboards.py`) checks Sec-Fetch-Site / Origin / Host and **emits no `Access-Control-Allow-Origin` header anywhere**. This is correct & load-bearing for DNS-rebinding + cross-origin write protection — do NOT add ACAO headers. | Panel A + Panel B both read `_local_request_ok` (slight line-number drift between two reads of the same function). |
| **#9 lazy-load mechanism** | **`<iframe src>` is the ONLY viable mechanism.** `innerHTML` does NOT execute `<script>` elements — the dashboard's entire interactive behavior (comfort-posture editor at line 7170+, router at line 8950+, plus ~10 other inline IIFE blocks) is inline-script-driven; a fetch+DOMParser+innerHTML approach would inject the scripts as inert text nodes. `<iframe srcdoc>` defeats lazy-loading (must fetch + serialize first). `<iframe src>` reparses in own browsing context → scripts execute natively, scope isolated, same-origin → postMessage works in/out. | Both panels independently agreed; Panel B cited dashboard.html:7170, 5221, 5932, 6452, 7044, 8950 inline-script lines. |

Phase 0 verdicts also resolve **Claim #11** (hand-maintained vs generated shell): hand-maintained for MVP because the shell is small + payload-agnostic + has no payload-internal enumeration to drift on.

### Phase 1 — Shell scaffold + router contract (1d)

**Pre-build gate:** Phase 0 verdicts adopted; `prettier --check .` + `audit-gates.sh` Gates 11/13 green pre-edit; document existing `index.html` route table (`#/home`, `#/team`, `#/marketplace`, `#/configuration`, `#/resources` — lines 1710-1716) to confirm no collisions.

**Work:** edit `/workspaces/RavenClaude/index.html` to add:
- **Top-level nav** — extend the existing `NAV` array (line ~1080) with two new entries: `Dashboard` and `Catalog` (repo-guide). Match the existing icon style.
- **Hash router that owns the URL** — extends the existing `route()` function (line ~1709) with new `case` branches and a **fixed lookup table** mapping top-level route prefixes to their payload iframe (per gap-delta D1, Panel A wins):
  ```
  heimdall|vidarr|norns|nidhoggr|bifrost|mimir|sleipnir|saga|activity|
  learn|plugin-*|web-access|pipeline|comfort-posture → dashboard.html
  repo-guide|repo-guide/* → repo-guide.html
  landing|home|team|marketplace|configuration|resources → shell-native
  unknown → fall to home
  ```
- **Two `<iframe>` slots** (initially `src=""` — no fetch until first activation). `title=` for a11y, `loading="lazy"`, `border: 0; display: block; width: 100%; height: 100vh`.
- **`loadIframe(target)` function** — memoized; sets `src` lazily on first navigation, shows/hides without re-fetching on subsequent route changes.
- **Hash-sync ownership (per gap-delta D5):** shell sets iframe `src="dashboard.html#/<route>"` on top-level route activation (entry point); the dashboard's internal router takes over from there. **Sub-routes inside the iframe are iframe-private** — clicking a tab inside the iframe does NOT update the shell URL. Document this explicitly as a known limitation; postMessage bidirectional sync is parked (RM2 mitigation, V2-only-if-triggered).

**Acceptance:**
- Fresh page load with no hash → renders landing, no iframe `src` set (verify via `iframe.src === ""`).
- `#/heimdall` deep-link → dashboard iframe gets `src="plugins/ravenclaude-core/dashboard.html#/heimdall"`, dashboard's own router activates Heimdall.
- Click Catalog nav → repo-guide iframe lazily loads with `src="repo-guide.html"`.
- Switching between Dashboard and Catalog hides/shows iframes WITHOUT re-setting `src` (cache preserved).
- Existing index.html routes (`#/home`, `#/team`, etc.) unbroken.
- Keyboard nav (arrow keys on nav-item) cycles through all items; Tab enters iframe; iframe focus ring visible.
- **No `dashboard.html` / `repo-guide.html` generator changes.** Gate 11 + 13 untouched.

**Agents:** `frontend-coder` (primary — shell HTML + router JS), `architect` (review the lookup-table contract + hash-sync ownership rules).

### Phase 2 — Smart-fallback + mode banner (1d)

**Pre-build gate:** Phase 1 merged; iframe load works on served + static hosts manually.

**The contract (load-bearing semantic):**
- **Shell makes NO `/__*` fetches.** It loads `dashboard.html` via iframe; the dashboard's per-card fetches (`/__heimdall`, `/__vidarr`, etc.) run inside the iframe at the iframe's origin.
- **Served mode (`127.0.0.1`):** iframe same-origin with the API endpoints → all `/__*` fetches succeed → live data renders. **No shell code change needed.**
- **Static mode (GitHub Pages):** iframe loads dashboard.html from `*.github.io` → `/__*` fetches hit Pages' 404 → **the dashboard's existing per-card empty-state fires unchanged** (claims-table #7).
- **The shell adds ONE thing:** an in-flow **mode banner** above the iframe (per gap-delta C4, Panel B's placement wins — less chrome than a persistent pill):
  - Live: nothing rendered (silence is correct on the live path).
  - Static: `"Live data tabs require the served dashboard — run \`rc dashboard\` or \`python3 scripts/serve-dashboards.py\` to enable them."` + a one-click copy-to-clipboard for the command.
- **Detection mechanism:** `HEAD /__csrf` with 500ms timeout from the shell. Try-catch the `TypeError: Failed to fetch` (CORS reject = static-host signal). Result cached for the session.
- **Iframe-load failure** (404 on a static host that didn't ship the payload, or generator never ran): `iframe.onerror` + 3s `onload` timeout. Renders inline empty state with copy-paste install command + Bifröst deep-link.

**Acceptance:**
- Live path: probe succeeds → no banner; iframe loads normally.
- Static path: probe fails → banner renders above iframe; iframe still loads; Norse cards inside render their existing empty states.
- Iframe load timeout: shell renders inline empty state, iframe detached.

**Agents:** `frontend-coder`, `code-reviewer`, `security-reviewer` (one-pass — confirm no CSP allowance broadens attack surface; no inline-script additions; iframe NOT sandboxed per RM3).

### Phase 3 — Visual regression DoD (0.5d, parallel with Phase 2)

**Pre-build gate:** Phase 1 merged.

**The concrete cosmetic acceptance bar** (per gap-delta D3, Panel B wins). Run a manual visual diff for each of these four surfaces — if any fail, hold Phase 1 from being declared done:

1. **Dashboard standalone** at `plugins/ravenclaude-core/dashboard.html`: screenshot Overview / Settings / Heimdall / Bifröst tabs. This is the baseline.
2. **Dashboard via shell** at `index.html#/dashboard`: compare to (1). Acceptable delta: iframe border-radius/margin from shell; scrollbar treatment. NOT acceptable: tab color wrong, tokens wrong, layout broken, Save button absent.
3. **Repo-guide standalone** vs `index.html#/repo-guide`: same comparison for Overview + Plugins tabs.
4. **Shell standalone** (Home, Team, Marketplace): visually identical before/after the change — the shell itself must not regress.
5. **Dark mode parity:** shell's `data-theme="dark"` does NOT propagate into the iframe's browsing context. Dark-mode parity is **DEFERRED scope** (not MVP). DoD requires only that the shell's dark mode does NOT break the iframe's light mode.

### Phase 4 — Gate 70 + parity-check line (0.5d, parallel with Phase 3)

**Pre-build gate:** Phase 2 contract frozen.

**Work:**
- **New Gate 70** in `scripts/audit-gates.sh` — a Node JSDOM behavioral test (`scripts/check-shell-router.mjs`) that:
  - Loads `index.html` into JSDOM.
  - Drives the router with synthetic hash changes (`#/heimdall`, `#/repo-guide`, `#/unknown`, etc.).
  - Asserts the lookup-table contract: `#/heimdall` → dashboard iframe src set; `#/repo-guide` → repo-guide iframe src set; `#/unknown` → falls to home.
  - Asserts the mode-banner state machine (mock the HEAD probe both ways).
  - **Must-fail half:** delete the lookup table → assert all dashboard routes fall to home. Proves the gate has teeth.
- **One-line addition** to `scripts/check-dashboard-server-parity.py` asserting `/__csrf` is in the endpoint set (the shell's mode probe depends on it; if that endpoint name ever changed, the banner silently falls to Static).

**Acceptance:** Gate 70 positive + must-fail half pass; parity-check addition green.

**Agents:** `tester-qa`, `architect`.

### Phase 5 — Ship: version bump + CLAUDE.md milestone + invariant comments

**Pre-build gate:** Phases 1-4 green.

**Work:**
- **Plugin version bump** — `plugins/ravenclaude-core/.claude-plugin/plugin.json` minor (user-visible behavior change). `marketplace.json` mirror lockstep.
- **CLAUDE.md milestone entry** following the established "X — Y tab (added DATE, vN.M.P)" pattern.
- **Two load-bearing invariant comments** (the RM1 + RM3 mitigations — prevents future contributor footguns):
  - In `serve-dashboards.py` near `_local_request_ok`: `# DO NOT ADD Access-Control-Allow-Origin HEADERS — the cross-origin reject is what gives the shell's mode banner its "Static" signal; adding ACAO breaks DNS-rebinding defense.`
  - In `index.html` near the iframe creation: `<!-- INVARIANT: payloads must be trusted, same-org artifacts. The shell will NEVER sandbox these iframes — sandboxing would break the dashboard's same-origin /__save CSRF flow. If a third-party payload is ever loaded here, redesign the trust boundary first. -->`
- **Migration note in PR:** "No consumer action required. `/plugin marketplace update` is safe — dashboard generators and freshness gates are unchanged. Existing bookmarks to `dashboard.html` and `repo-guide.html` resolve unchanged. The new URL is `index.html#/<route>`."

**Stretch (separate follow-on PR per gap-delta D2, not MVP):** add `<link rel="canonical" href="index.html#/dashboard">` to `dashboard.html` + `<link rel="canonical" href="index.html#/repo-guide">` to `repo-guide.html` via their generators. Helps SEO + link-previewers understand the new canonical home. Requires regen-and-commit-in-same-commit discipline (RM6).

---

## Dependency DAG

```
Phase 0 (verification — DONE in panel work)
   │
   ▼
Phase 1 (shell scaffold + router contract, 1d)
   │
   ├──────────────────────────┬──────────────────────────┐
   ▼                          ▼                          ▼
Phase 2 (smart fallback,     Phase 3 (visual regression  Phase 4 (Gate 70 +
         1d)                   DoD, 0.5d) [parallel]      parity-check, 0.5d) [parallel]
   │                          │                          │
   └────────────┬─────────────┴────────────┬─────────────┘
                ▼                          
            Phase 5 (ship: version bump + milestone + invariant comments)
```

**Critical path:** P0 → P1 → P2 → P5 ≈ **2.5-3 days serialized**, ≈ **2 days with P3+P4 parallel**.

---

## Alternatives kept on the record

| # | Decision | Chosen | Alternative(s) | Why chosen |
|---|---|---|---|---|
| A1 | Lazy-load mechanism | **`<iframe src>`** | `fetch + DOMParser + innerHTML` / `<iframe srcdoc>` | DOMParser+innerHTML doesn't execute `<script>` tags — dashboard's interactive behavior is 100% inline-script-driven (dashboard.html:7170 et al.) — HARD blocker. srcdoc defeats lazy-loading. |
| A2 | Shell maintenance | **Hand-maintained** (v1) | Generated (v2 only-if-triggered) | Shell is small + payload-agnostic + no payload-internal enumeration. No structural drift to gate. Adding a generator + Gate-N is YAGNI for two `<iframe>` elements. |
| A3 | Route namespacing | **Keep top-level** (`#/heimdall`, `#/bifrost`, etc.) — shell uses fixed lookup table | Namespace under `#/dashboard/heimdall` | Top-level preserves committed bookmarks (gjallarhorn-link, capability-banner pointers, doc references). Namespacing breaks them for zero gain. Implicit namespacing via the lookup table is cleaner. |
| A4 | Hash-sync between shell + iframe | **Entry-point only** — shell sets iframe src once on top-level route; sub-routes iframe-private | Bidirectional postMessage sync | Sidesteps the two-way binding bug factory (RM2). User reload on a deep-link works; clicking inside the iframe doesn't update shell URL — documented as known limitation. V2 mitigation = postMessage one-way (inner→outer) with debounce. |
| A5 | Mode banner placement | **In-flow above iframe** when static | Persistent top-right pill (Live/Static) | Less chrome; only renders when there's something to say (static path). |
| A6 | Canonical link via generator | **Deferred to follow-on PR** | Include in MVP | Adds Gate 11/13 regen discipline burden to a shell-only PR. Cleaner to ship the shell first, then the generator change in a small follow-up. |
| A7 | CSS scoping | **`<iframe>` isolation** (falls out of A1) | Shadow DOM + slot / `@layer` partitioning | iframe gives complete isolation by construction. Both dashboard.html and repo-guide.html define `.tab-btn` differently from index.html's nav items — would collide on innerHTML inject; iframe makes the collision moot. |

---

## Risk matrix (Panel A R1-R3 + Panel B R1-R3, merged)

| # | Risk | P × I | Mitigation | Owner |
|---|---|---|---|---|
| **RM1** | **CORS-trap-disguised-as-feature** (Panel A R1) — the mode banner probe fails on Pages → correct outcome via wrong-looking mechanism. If anyone later adds `Access-Control-Allow-Origin: https://*.github.io` "to help the banner," they shatter the DNS-rebinding defense (security floor invariant). | Medium × High | Code comment NOW on `_local_request_ok` AND on shell's `probeServedMode()` — `// DO NOT ADD CORS HEADERS — the probe failing IS the signal`. Phase 5 makes this a load-bearing invariant comment. | `security-reviewer` |
| **RM2** | **iframe + parent hash-sync two-way binding** (Panel A R2) — outer shell router + inner dashboard router both want `location.hash`. Without strict ownership: infinite hash-change cascades (Firefox/Safari sync hashchange vs Chrome batched). | Medium × Medium | **MVP: sidestep entirely** via gap-delta A4 (entry-point only; sub-routes iframe-private). Documented limitation. V2 (only-if-triggered): postMessage one-way inner→outer with debounce + cycle test. | `architect` |
| **RM3** | **iframe same-origin trust boundary** (Panel A R3) — same-origin iframe payload can `parent.document.cookie` / `parent.localStorage` the shell. Sandboxing later would break `/__save` CSRF flow. Loading third-party payloads would be unprepared. | Low × Medium | **Declare in shell contract NOW:** "payloads must be trusted, same-org artifacts; shell will NEVER sandbox." Phase 5 HTML comment + CLAUDE.md milestone make this load-bearing. | `security-reviewer` |
| **RM4** | **iframe height + double scrollbar** (Panel B R1) — `height: 100vh` inside scrolling shell = two scrollbars. Mobile Chrome `100vh` excludes browser chrome, collapses when user scrolls → iframe shifts. | Medium × Medium | `height: 100vh; border: 0; display: block` on iframe + `overflow: hidden` on `#view` when iframe route active. **Phase 3 acceptance MUST verify on mobile viewport** (Chrome Android simulator). | `frontend-coder` (P3 acceptance owner) |
| **RM5** | **iframe CSP / frame-ancestors interaction** (Panel B R2) — index.html CSP `frame-src` restriction OR serve-dashboards.py `frame-ancestors 'none'` header → iframe blocked. Neither set today; GitHub Pages defaults don't set X-Frame-Options for user content. | Low × High | Deliberate check before Phase 2 ships. Grep both files for `frame-src` / `frame-ancestors` / `X-Frame-Options`; manual browser test against both served + Pages. | `security-reviewer` |
| **RM6** | **Gate 13/11 invalidation from canonical-link generator change** (Panel B R3) — if/when canonical-link follow-up ships, dashboard.html + repo-guide.html generator change → must regen+commit artifacts in same commit. Common process failure: dev adds canonical line, forgets regen, PR fails freshness gate with cryptic "file not fresh" error. | Medium × Low (deferred from MVP) | Canonical-link is a **separate follow-on PR per gap-delta A6** — keeps shell PR clean. When that PR is authored: explicit checklist in the PR body that regen+commit happened in the same commit. | `frontend-coder` (canonical follow-up author) |

---

## Definition of Done

- [ ] **`index.html` edited** with nav + router + 2 iframe slots + lookup table + load-iframe function. No new files.
- [ ] **No `.repo-layout.json` edit** needed — `index.html` already at line 18.
- [ ] **No generator changes** in MVP — `dashboard.html` + `repo-guide.html` unchanged, Gates 11 + 13 unchanged.
- [ ] **New Gate 70** (`scripts/check-shell-router.mjs` — JSDOM behavioral test) registered in `scripts/audit-gates.sh` with must-fail half (delete lookup table → routes fall to home).
- [ ] **One-line parity-check addition** in `check-dashboard-server-parity.py` asserting `/__csrf` in endpoint set.
- [ ] **Prettier** `--write` then `--check .` exit 0.
- [ ] **Plugin version bump lockstep** — `plugins/ravenclaude-core/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` minor.
- [ ] **CLAUDE.md milestone entry** under the Norse-tab pattern alongside Heimdall/Víðarr/Norns/Níðhöggr/Bifröst/Mímir.
- [ ] **Two load-bearing invariant comments** in serve-dashboards.py and index.html (RM1 + RM3 mitigations).
- [ ] **Phase 3 visual regression DoD** — 4-surface comparison done manually + **mobile viewport** verified (RM4).
- [ ] **Backward-compat verified:** every existing URL resolves; `dashboard.html#/heimdall` and `repo-guide.html` still work standalone.
- [ ] **Migration note in PR body:** "No consumer action required; bookmarks resolve; new URL is `index.html#/<route>`."

---

## Settling steps for the unverified claims

| Claim | Settling step | Where in plan |
|---|---|---|
| #8 — CORS / cross-origin fetch behavior | **Resolved Phase 0** by both panels reading `_local_request_ok` in `serve-dashboards.py`. Static-host is degraded-by-design. | Phase 0. |
| #9 — Lazy-load mechanism | **Resolved Phase 0** by both panels reading dashboard.html inline-script lines (7170, 5221, 5932, etc.). `<iframe src>` is the only viable mechanism. | Phase 0. |
| #11 — Hand-maintained vs generated shell | **Resolved Phase 0** — hand-maintained for MVP (shell is small + payload-agnostic + no payload-internal enumeration). | Phase 0. |
| RM5 — CSP / frame-ancestors | Pre-Phase-2 grep of both files for `frame-src` / `frame-ancestors` / `X-Frame-Options` + manual browser test against both served + Pages. | Phase 2 pre-build. |
| RM4 — Mobile viewport behavior | Phase 3 acceptance — Chrome Android simulator test. | Phase 3. |

---

## Open questions parked

- **postMessage bidirectional hash-sync (RM2 V2 mitigation).** Defer until shareability of deep-shell-URLs-into-specific-iframe-tabs becomes a real ask. MVP accepts the "shell URL reflects entry tab" limitation.
- **Canonical-link addition to dashboard/repo-guide via generators (gap-delta A6).** Defer to a separate follow-on PR after MVP ships; the Gate 11/13 regen discipline is real burden and shouldn't ride along.
- **Dark-mode parity between shell + iframe payloads** (Phase 3 DoD note). Out of MVP scope; deferred until a consumer asks.
- **Cross-surface search.** Nice-to-have, not core to "one URL." Park for a follow-up.
- **Sandboxing iframes** (RM3 V2). Explicit anti-future-feature: declared in the shell contract that payloads must be trusted, same-org artifacts. If a third-party payload is ever loaded here, redesign the trust boundary first.
- **Generator-driven shell (v2)** (gap-delta C3). Only-if-triggered: if the shell's lookup table drifts from the dashboard's actual route inventory, automate via `scripts/generate-index.py`. YAGNI for now.
