# Phase 2 plan — hybrid Catalog on the shipped dashboard (mode diet)

**Date:** 2026-11-12  
**Status:** done  
**Decision:** [`docs/decisions/2026-11-12-one-product-portal-dashboard.md`](../decisions/2026-11-12-one-product-portal-dashboard.md) Phase 2  
**Predecessor:** Phase 1 chrome already on `main` (teal accent; standalone `ds-label` = Catalog; Gate 200/51 maps accept `catalog`)

## Verdict

Ship **lean consumer `dashboard.html` by default** (`include_catalog=False`). Make Catalog *browse* hybrid-capable via a **runtime payload presence check** (inline `__RC_DATA__` **or** lazy fetch). Keep marketplace hybrid on **`index.html`** for Phase 2. Do **not** retarget root `serve-dashboards.py` / `open-dashboard.sh` yet (Phase 3). Do **not** bake marketplace Catalog shell DOM / `#dt-store` into the consumer ship — Gate 132 is at **zero slack** on both surfaces.

---

## 1. How portal Catalog works today

### Routes

| Hash | Dispatch (`scripts/_index_dashboard_template.py` → `route()`) | Host |
|---|---|---|
| `#/catalog`, `#/discover`, `#/discover/<cat>` | `showHost("view"); viewMarketplace(sub)` | `#view` (shell) |
| `#/plugin-<name>` | `window.__openPlugin(name)` after `hydrateDetail` | `#view` |
| `#/team` | `SECTION_ALIAS.team → catalog` then marketplace path | `#view` |
| `#/learn` | `viewResources()` (shell Templates/knowledge; **not** `learn-payload`) | `#view` |
| `#/trees` | `DASH_OWNER.trees → catalog` → `viewDashboard("trees")` | `#dash-root` |
| `#/help`, `#/plugin-vars`, … | `DASH_OWNER` → Catalog-owned dashboard tabs | `#dash-root` |

Control-first: empty/unknown hash → `viewDashboard("settings")`.

### Key symbols (portal shell)

| Symbol | File | Role |
|---|---|---|
| `NAV` | `_index_dashboard_template.py` | Four destinations incl. `{ id: "catalog", … }` |
| `navChildren("catalog")` | same | JS-built accordion: Specialists + Guidance + All plugins + **18** category links (from `D.categories`) |
| `renderNav` | same | Rewrites `#primary-nav` at route time (seed is 4 static `<a>`s only) |
| `viewMarketplace(catId)` | same | Browse grid + use-case table + featured cards; filters `D.plugins` |
| `hydrateDetail` / `__loadDetailIsland` | same | Merges `#plugin-detail-payload` into eager plugin records before `__openPlugin` |
| `__openPlugin` | same | Rich per-plugin reference (agents/scenarios/indexes + `#dt-store` trees) |
| `SECTION_ALIAS` / `DASH_OWNER` / `SHELL_ROUTE_HOME` | same | Homes marketplace/learn/help under Catalog |
| `scan_repo` / `render_html` | `generate-index-dashboard.py` | Builds `__RC_DATA__` + island + folds dashboard fragment |

### Payload IDs and measured sizes (main tip, this session)

| ID / blob | Surface | Size | Gate 132? |
|---|---|---|---|
| `window.__RC_DATA__` | `index.html` only | **~1.46 MB** (184 plugins, 18 cats, 2186 use_cases) | JSON in `<script>` text → **not** element-counted |
| `#plugin-detail-payload` | `index.html` only | **~1.44 MB** | +1 `<script>` element; content CDATA |
| `#trees-payload` | both (portal keeps it) | **~4.00 MB** | island pattern (+2 with mount) |
| `#learn-payload` | `dashboard.html` only | **~4.32 MB** | stripped from portal |
| `#concepts-data` | `dashboard.html` only | **~0.47 MB** | stripped from portal |
| `#dt-store` + `.dt-item` | `index.html` only | **799** static empty stubs | **+799 counted elements** |

Totals: `index.html` ≈ 9.57 MB; `dashboard.html` ≈ 10.95 MB.

### Standalone Catalog today (post–Phase 1)

`generate-dashboards.py` `_PAGE_TEMPLATE` sidebar:

```text
Catalog → Learn (#/learn) · Guidance (#/trees) · Help (#/help) · Plugins (#/plugin-vars)
```

No `viewMarketplace`, no `__RC_DATA__`, no `#plugin-detail-payload`, no `#dt-store`. That is the intentional lean consumer Catalog until mode diet lands.

---

## 2. How generators strip / flag payloads today

### `generate-index-dashboard.py` (portal)

| Mechanism | Behavior |
|---|---|
| `_PORTAL_ONLY_PAYLOAD_IDS = ("learn-payload", "concepts-data")` | `_strip_portal_only_payloads(frag["dash"]["body"])` removes those two islands from the folded fragment (**fail-loud** if count ≠ 1) |
| `trees-payload` | **Not** stripped (G4 restore) — portal keeps consolidated Guidance |
| `_extract_detail_island` | Pops `_ISLANDED_PLUGIN_KEYS` + `_ISLANDED_AGENT_KEYS` out of eager `__RC_DATA__` into `#plugin-detail-payload` |
| `_load_fragments` → `gd.render_fragment(...)` | Folds dashboard body/css/js into shell |

### `generate-dashboards.py` (standalone + fragment)

| Symbol | Flags today | Notes |
|---|---|---|
| `_page_kwargs(..., include_trees=True)` | `include_trees` only | Controls `_render_trees_tab` inventory |
| `render_dashboard` | full page, trees on | Ships `plugins/ravenclaude-core/dashboard.html` |
| `render_fragment` | hard-codes `include_trees=True` | Docstring historically said portal used `False`; **code + G4 restored True** — docstring drift to fix in Phase 2 |
| `main()` CLI | `--plugin`, `--check`, `--stdout` | **No** `include_catalog` yet |

There is **no** `include_catalog` flag today. Catalog browse lives only in the portal shell template, not in the dashboard generator.

---

## 3. Smallest viable Phase 2 (recommended)

### Shape: lean ship + runtime hybrid, keep `index.html` as marketplace hybrid

```text
Consumer install / rc dashboard
  dashboard.html  (include_catalog=False)
  Catalog = Learn · Guidance · Help · Plugins
  if marketplace payload appears at runtime → enable Browse

Marketplace Pages / root serve-dashboards.py
  index.html      (already hybrid — KEEP for Phase 2)
  Catalog = marketplace browse + folded Control/Activity/Guardrails
```

### Keep / Update / Deny

| Item | Decision | Why |
|---|---|---|
| Lean shipped `dashboard.html` (no `__RC_DATA__` / no `#plugin-detail-payload` / no `#dt-store`) | **Keep** | Non-goal of the decision: do not ship full marketplace Catalog into every consumer install before mode diet |
| `index.html` as marketplace hybrid entry | **Keep** (Phase 2) | Already has Catalog browse; Gate 97/51/132 already bound to it |
| Generator flag `include_catalog` (default **False**) on dashboard path | **Update** | Mode diet knob; True only for an explicit marketplace hybrid build artifact (optional) or tests |
| Runtime detect + lazy fetch of catalog JSON when in marketplace tree | **Update** | Makes `rc dashboard` inside the marketplace checkout hybrid without bloating the consumer ship |
| Static Catalog category accordion / `#dt-store` on standalone | **Deny** | Gate 132 zero slack; +19–20 (cats) or +~800 (`dt-store`) without owned raise |
| Retarget root `serve-dashboards.py` / `open-dashboard.sh` → `dashboard.html` + catalog mode | **Deny for Phase 2** → Phase 3 | Decision Phase 3 owns single artifact + `dash_path` / Pages host; Phase 2 is mode diet only |
| Inline 2.9 MB catalog data into every `dashboard.html` | **Deny** | Byte ceiling + consumer install weight; contradicts decision non-goal |

### Implementation steps (ordered)

1. **Extract / share Catalog browse capability (JS)**  
   - Port `viewMarketplace` + `hydrateDetail` + the `__openPlugin` browse/detail path into dashboard `_JS` behind a capability gate:  
     `const catalogMode = !!(window.__RC_DATA__ && window.__RC_DATA__.plugins);`  
   - When false: existing Catalog tabs only. When true (or after successful fetch): show Browse host.

2. **Add generator flag `include_catalog: bool = False`**  
   - Thread through `_page_kwargs` / `render_dashboard` / optional CLI `--include-catalog`.  
   - When False (default): emit **no** catalog islands; optionally emit empty `#catalog-mount` (0–1 static) for JS to fill.  
   - When True: splice `__RC_DATA__` + `#plugin-detail-payload` (reuse `scan_repo` / `_extract_detail_island` from index generator — import sibling, do not duplicate). **Still omit `#dt-store`** unless a separate owned Gate 132 raise is approved (prefer lazy tree fetch via existing `__rcTreeBase` packs).

3. **Emit sidecar catalog JSON for lazy load (marketplace)**  
   - New: `python3 scripts/generate-index-dashboard.py --emit-catalog-json -o catalog-data.json` (eager + island, or two files).  
   - Root `serve-dashboards.py`: when serving marketplace root, allow `GET /catalog-data.json` (or `/__catalog`) from repo root / generated path.  
   - Dashboard JS: on first `#/catalog` browse intent, if `!window.__RC_DATA__`, `fetch('/catalog-data.json')` → assign `window.__RC_DATA__` + hydrate island; 404 → stay lean.

4. **Nav affordance with Gate 132 discipline**  
   - Preferred: **JS-injected** “Browse plugins” `.ds-sub` only when catalogMode becomes true → **+0** static Gate 132.  
   - Acceptable owned raise: **+1** static `<a class="ds-sub" href="#/catalog" data-tab="catalog-browse">Browse plugins</a>` always present, disabled/hidden until payload loads. Document in Gate 132 ratchet row.

5. **Do not change consumer `DASH_PATH`**  
   - `plugins/ravenclaude-core/scripts/serve-dashboards.py` keeps `DASH_PATH = "/dashboard.html"`.  
   - Root `scripts/serve-dashboards.py` kept `dash_path = "/index.html"` for Phase 2 (retargeted in Phase 3a).  
   - `scripts/open-dashboard.sh` kept `/index.html` URLs for Phase 2 (retargeted in Phase 3a).

6. **Gates / docs**  
   - Gate 132: raise **only** if static DOM lands; append owned ratchet reason.  
   - Gate 51 / 200: if `#/catalog` on standalone gains a real browse destination, update `tests/fixtures/routes/committed-routes.json` + surface-parity homes.  
   - Fix stale `render_fragment` / `_page_kwargs` comments that still say portal `include_trees=False`.  
   - Update `docs/dashboard-removed-routes.md` if `#/catalog` browse becomes live on standalone when payload present.  
   - Artifact byte budgets: lean ship should **not** need a dashboard.html byte raise; sidecar JSON is not the shipped plugin artifact.

### Out of scope for this Phase 2 PR

- Killing or redirecting `index.html` (Phase 3; Gate 97/51 blast radius).  
- Save on Pages.  
- Full `#dt-store` (799 stubs) on standalone.  
- Portal-parity static category accordion on standalone without an owned Gate 132 raise.

---

## 4. Gate 132 risk (concrete)

**Current (main tip):** dashboard **6,408 / 6,408**; index **7,294 / 7,294** — **zero slack** both sides.

| Change on standalone | Δ elements | Budget action |
|---|---|---|
| Runtime mode flag + JS-only Browse (createElement) | **+0** | None — preferred |
| Static “Browse plugins” `.ds-sub` | **+1** | Owned raise +1 (document: Catalog hybrid affordance) |
| Portal-parity category accordion as static `.ds-sub`s (All + 18 cats) | **+19** | Owned raise; **avoid** |
| + Specialists link | **+20** | Owned raise; **avoid** |
| Empty `#catalog-mount` + JSON island for browse markup | **+2** | Owned raise only if markup cannot be pure createElement |
| `#dt-store` with 799 `.dt-item` | **+~800** | **Reject for consumer ship** |
| Inlining `__RC_DATA__` + `#plugin-detail-payload` as `<script>` tags | **+1–2** script elements | Bytes dominate (~+2.9 MB); Gate 132 small, artifact budget large — still **Deny** for default ship |

**Index.html:** Phase 2 should not grow Catalog shell DOM further; marketplace hybrid already exists. Any shared-fragment change that adds static nodes to the folded body hits **both** ratchets.

---

## 5. Exact files + symbols for the Phase 2 PR

### Must touch

| Path | Symbols / edits |
|---|---|
| `scripts/generate-dashboards.py` | `_page_kwargs(..., include_catalog=False)`; `render_dashboard`; `render_fragment` (pass-through / docstring fix); `_PAGE_TEMPLATE` Catalog group; `_JS` catalogMode + optional `viewMarketplace` port; `main()` `--include-catalog` |
| `scripts/generate-index-dashboard.py` | `--emit-catalog-json`; keep `_PORTAL_ONLY_PAYLOAD_IDS`; optionally share `scan_repo` / `_extract_detail_island` with dashboards via import |
| `scripts/_index_dashboard_template.py` | Prefer **thin** shared helper later; Phase 2 can leave shell as source of browse UX and port symbols into `_JS` first (avoid double maintenance forever — follow-up extract) |
| `plugins/ravenclaude-core/dashboard.html` | Regen with `include_catalog=False` (lean) |
| `scripts/check-dom-budget.py` | Append ratchet row **only if** static Δ > 0 |
| `scripts/artifact-budgets.seed.json` | Only if byte/payload ceilings move (lean path should not) |
| `tests/fixtures/routes/committed-routes.json` | If standalone gains resolvable `#/catalog` browse |
| `scripts/check-surface-parity.py` (Gate 200) | Homes for new browse tab if needed |
| `docs/dashboard-removed-routes.md` | Note mode-conditional Catalog browse |
| `docs/decisions/2026-11-12-one-product-portal-dashboard.md` | Optional status note: Phase 2 in progress / done |
| `plugins/ravenclaude-core/.claude-plugin/plugin.json` + `CHANGELOG.md` | Version bump on user-visible hybrid capability |
| `python3 scripts/sync-plugin-versions.py` | Catalog version sync |

### Touch only if implementing lazy fetch server side

| Path | Symbols |
|---|---|
| `scripts/serve-dashboards.py` | Allow-list GET for `catalog-data.json` / `/__catalog` (marketplace root only) |
| `plugins/ravenclaude-core/scripts/serve-dashboards.py` | Same endpoint shape for parity **or** honest 404 in consumer installs (lean) — prefer consumer 404 |
| `scripts/check-dashboard-server-parity.py` | Endpoint parity row if both servers gain `/__catalog` |

### Do **not** touch in Phase 2

| Path | Why |
|---|---|
| `scripts/open-dashboard.sh` `url=…/index.html` | Phase 2 keep; Phase 3a retargets to `dashboard.html` |
| Root `serve-dashboards.py` `dash_path = "/index.html"` | Phase 3a retargets to `/plugins/ravenclaude-core/dashboard.html` |
| Consumer `DASH_PATH = "/dashboard.html"` | Correct lean home |
| Gate 97 retarget off `index.html` | Phase 3 |

---

## 6. Phase 2 vs Phase 3 on root serve

| Question | Answer |
|---|---|
| Should Phase 2 point root serve / `open-dashboard.sh` at `dashboard.html` with catalog mode? | **No.** That is the Phase 3 single-artifact cut. |
| What does Phase 2 do instead? | Mode diet on the **shipped** artifact + optional lazy catalog when payload exists; marketplace maintainers keep using `index.html` hybrid. |
| What unblocks Phase 3? | Proven `include_catalog` / runtime catalogMode on `dashboard.html`, Gate 51/200 parity for browse routes, then collapse generators so one HTML is canonical and retarget Gate 97/51/132 + `dash_path`. |

---

## 7. Suggested PR slice (one PR)

**Title:** `feat(ravenclaude-core): Phase 2 Catalog mode diet (lean ship + runtime hybrid)`

1. `include_catalog=False` default + docstring fixes for `include_trees`.  
2. Dashboard JS `catalogMode` + JS-injected Browse (Gate 132 Δ0).  
3. `--emit-catalog-json` + marketplace-root fetch path.  
4. Tests: Gate 132 check green at zero raise; consumer ship still lacks `__RC_DATA__`; marketplace `index.html` unchanged in behavior.  
5. Docs: this plan referenced from the decision; removed-routes note.

Optional follow-up PR: extract shared Catalog browse module so `_index_dashboard_template.py` and `_JS` do not diverge.

---

## 8. Verification checklist (when implementing)

```shell
python3 scripts/generate-dashboards.py --plugin ravenclaude-core
python3 scripts/generate-index-dashboard.py   # marketplace hybrid unchanged
python3 scripts/check-dom-budget.py --check   # expect 6408 / 7294 unless owned raise
# assert lean ship:
! grep -q 'id="plugin-detail-payload"' plugins/ravenclaude-core/dashboard.html
! grep -q 'window.__RC_DATA__' plugins/ravenclaude-core/dashboard.html
# assert portal still has catalog:
grep -q 'id="plugin-detail-payload"' index.html
grep -q 'function viewMarketplace' index.html
```
