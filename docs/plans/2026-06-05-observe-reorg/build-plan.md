# Build plan — Observe category reorganization

**Date:** 2026-06-05 · **Status:** tactical (how) · **Synthesized from:** Panel 1 (architect · security · ops/gates · devil's-advocate) over `strategic-plan.md`.

## The load-bearing fact (de-risks everything)

The six render gates (`check-{heimdall,vidarr,norns,nidhoggr,sleipnir,mimir}-render.mjs`) and the round-trip gate **extract render functions by `function NAME(` header text from the largest `<script>` body** and assert against the **DOM ids those fns write to** (`heimdall-hooks`, `heimdall-drift`, `vidarr-content`, `heimdall-debt`, …). They do **not** anchor on tab id or panel container. **Golden rule for this whole change: regroup tabs/panels; never rename or inline-delete a render fn; keep the existing DOM ids even when a card moves tabs.** Obey that and gates 37/38/40/41/43/49 + round-trip stay green with **zero `.mjs` edits**.

## Resolved decisions (PO calls + panel reconciliations)

| # | Decision (yours) | Implementation (panel-recommended) | Reconciliation note |
|---|---|---|---|
| 1 | Run feed — **keep** | No change. | — |
| 2 | Perimeter alerts + Security log — **merge** | Keep tab id `heimdall` as the merged **"Guardrails & security"** tab; fold Víðarr's `vidarr-content`/`vidarr-filters` markup in under a **view toggle**; keep **both** `renderHookEvents`/`renderGjallarhorn` **and** `renderVidarrTable` verbatim, **both** loaders (`loadHeimdall`+`loadVidarr`), **both** endpoints. `#/vidarr` → `viewDashboard("heimdall","audit")`. | **Security guard (load-bearing):** the *audit* view must SOURCE from `/__vidarr` (the `_vidarr_hook_is_security` deny-only predicate — warns excluded), NOT a client-side filter of Heimdall's all-tiers stream. Preserve the red/amber/grey tiering, posture-change rows, and the visual `vidarr-kind--*` split. The toggle switches **data source**, not just a row filter. |
| 3 | Review log (Sága) — **move to Configure, below the tribunal** | Shell-only: `DASH_OWNER.saga: "observe"→"configure"`; append **"Review log"** last in `SECTION_TABS.configure` (under "Posture", where the tribunal toggles live). Keep `saga` a real dashboard tab (render fn untouched). | **Flagged tension (devil's-advocate):** this puts a read-only log into the *Configure* section, against the "Configure = change / Observe = read-only" rule we just set. You chose it explicitly, so we honor it. *Alternative if you reconsider:* keep Sága in Observe and add a "View recent verdicts →" deep-link from the tribunal block (cheaper, rule-consistent). **Decision point — confirm at build.** |
| 4 | Session (Mímir) — **keep, relabel "Session"** | Tab-bar label change only; `mimir*` fns untouched; single `/__mimir` source (the secret-scrub lives on that endpoint). | — |
| 5 | Plugin lineage (Norns) — **move to Discover** | **Deep-link**, not embed: add a "Plugin lineage →" link on the Discover per-plugin page pointing at `#/norns`; **keep the Norns dashboard tab rendered** (so its 4 render fns persist → Gate 40 safe). `__openPlugin` stays **fetch-free / offline-safe**. | **Reconciliation:** the decision was "move to Discover"; the panel implements it as *reachable from Discover* (a link) rather than embedding the served `/__norns` fetch into the static catalog — unanimous across all four lenses (avoids breaking Discover's offline-safety + the Gate-40 deletion trap). Per-plugin `#/norns/<plugin>` parametrization is a small follow-up. |
| 6 | Marketplace-health cards — **split out** | New tab `marketplace-health`: move the 5 card `<section>`s (`hm-drift/hm-debt/hm-hooks/hm-ci/hm-kh`) + their render fns (`renderVersionDrift`/`renderNidhoggr`/`renderKnowledgeHealth`/`renderCiStatus`) **verbatim**, **keeping the `heimdall-*` DOM ids** (avoids editing 4 gates). Split `loadHeimdall` → new `loadMarketplaceHealth`. No new endpoints (`/__nidhoggr`, `/__knowledge-health` exist; drift is inlined). | — |
| 7 | Marketplace health — **new Observe sub-tab** | Add `marketplace-health` to `DASH_SECTIONS` + `SECTION_TABS.observe`; `DASH_OWNER["marketplace-health"]="observe"`; `DASH_TAB_ALIAS.nidhoggr="marketplace-health"`. | **Refinement (devil's-advocate + architect):** every signal reads the *marketplace* repo → **empty on consumer installs**. **Dev-gate the tab** behind the existing dev-repo signal (owner `mcorbett51090/RavenClaude` / `dev_repo_exempt`) so consumers never see an empty quadrant; the maintainer sees it. **Decision point — confirm at build.** |

### Resulting Observe sub-nav (4 tabs)
`Run feed` · `Guardrails & security` · `Marketplace health`* · `Session` — (*dev-gated).
**Relocations:** Review log → Configure (last); Plugin lineage → linked from Discover.

## The routing/alias edits (`_index_dashboard_template.py`)

```
DASH_OWNER:   saga: observe→configure;  add "marketplace-health": "observe";  (norns stays observe — tab kept)
DASH_TAB_ALIAS: add vidarr→heimdall (+ forced sub "audit");  nidhoggr→marketplace-health  (keep sleipnir→activity, concepts→learn)
DASH_SECTIONS: add "marketplace-health"  (keep saga/norns/vidarr/nidhoggr for back-compat)
SECTION_TABS.observe:  [Run feed #/activity, Guardrails & security #/heimdall, Marketplace health #/marketplace-health, Session #/mimir]
SECTION_TABS.configure: append { Review log, #/saga } last
Discover per-plugin page: add "Plugin lineage →" href #/norns
```

### Deep-link back-compat (the contract — must all resolve)
| Legacy | Resolves to |
|---|---|
| `#/heimdall` | Guardrails (live view) |
| `#/vidarr` | Guardrails (**audit** view, via `sub="audit"`) |
| `#/saga` | Configure → Review log |
| `#/norns` | Observe → Lineage tab (kept; also linked from Discover) |
| `#/nidhoggr` | Marketplace health |
| `#/mimir` | Observe → Session |
| `#/activity`, `#/sleipnir` | Run feed |

**The `sub`-carrier gap (architect P0):** `DASH_TAB_ALIAS` is a flat `route→tab` string and can't express "`vidarr`→tab `heimdall`, view `audit`". `viewDashboard(section,sub)`→`__dashApp.show(tab,sub)`→`activate(tab,sub)` already threads `sub`. **Fix:** special-case `vidarr` in `viewDashboard` to pass `sub:"audit"` (or make `DASH_TAB_ALIAS` values `{tab, sub}`). Specify this concretely before Slice 2.

## Gate 51 edits (the breaker — same commit as the template)

`check-shell-router.mjs` hardcodes expectations the regroup invalidates:
- **`:205`** asserts the literal `"Perimeter alerts"` label → change to `"Guardrails & security"` (+ add `"Marketplace health"`, `"Review log"` under configure).
- **`:143`** `expectedOwners` asserts `saga:"observe"` → `saga:"configure"`; add `"marketplace-health":"observe"`; add `nidhoggr`'s tab-alias check.
- **`:99-113`** keep `saga`/`norns`/`nidhoggr` in `DASH_SECTIONS` (don't delete — back-compat). Add `"marketplace-health"`.
- Re-verify the **three must-fail halves** still trip after editing expectations (don't defang).

## Gate / regen checklist (ops)
- Render gates 37/38/40/41/43/49 + round-trip 35: **no `.mjs` edits** *iff* no render fn is renamed/deleted and DOM ids preserved. (If any fn is renamed, update its `extract(app,"function …")` anchor atomically — `extract()` throws on a missing header.)
- Parity (Gate 32): green — **no `/__*` endpoint renamed**; mirror any reader edit into **both** `serve-dashboards.py` copies.
- Freshness: regenerate **both** `dashboard.html` (Gate 13) and `index.html` (Gate 97) from the generators; never hand-edit the HTML; git-derived data stays server-side (never inlined → determinism).
- **Version bump** `plugins/ravenclaude-core/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` lockstep (Gate 8) → **0.125.0**; **migration note** (consumer dashboard tabs move on `/plugin marketplace update`).
- CLAUDE.md milestone (`## Observe reorg … (added 2026-06-05, v0.125.0)`).

## Phasing (panel-recommended cut line)

**Slice 1 — split + relabels + shell moves (low risk, no render-fn-body edits):**
- Marketplace-health split (cards + fns moved verbatim, `heimdall-*` ids kept) → new dev-gated tab.
- Heimdall **header relabel** → "Guardrails & security" (no merge yet).
- Sága → Configure and Norns → Discover-link: **shell-only** (`DASH_OWNER`/`SECTION_TABS` + the matching Gate 51 expected-map edits).
- Version bump + migration + milestone. Touches `generate-dashboards.py` templates + shell maps + Gate 51; leaves every render-fn body + endpoint byte-identical.

**Slice 2 — the Heimdall+Víðarr view-toggle merge (the only genuinely risky step):**
- Fold `vidarr-content` skeleton into the heimdall template under a toggle; wire the `sub="audit"` carrier; keep both loaders/fns; enforce the security source-switch guard.
- Add a render-gate assertion that the merged tab still renders (i) the red/amber/grey tier in live view, (ii) excludes `warn` from the audit view, (iii) renders `posture-change` rows.

Isolating Slice 2 means Slice 1 ships ~80% of the clarity with near-zero gate risk, and a Slice-2 regression can't strand the rest.

## Open decision points for you (before build)
1. **Sága placement:** honor "in Configure below the tribunal" (re-own, as decided) — or the rule-consistent **deep-link** alternative (keep in Observe, link from the tribunal)?
2. **Marketplace-health visibility:** **dev-gate** it (hidden on consumer installs, recommended) — or ship it to all consumers (empty quadrant)?

---

## Panel 1 gap-fill summary

- **G-OB1 (architect/security/ops):** the merge keeps **both** render fns + **both** endpoints under one tab; the audit view sources `/__vidarr` (deny-only predicate), never a client-filter of the all-tiers Heimdall stream. *(decision #2)*
- **G-OB2 (all four):** Norns → **deep-link** to the kept tab, not an embedded `/__norns` fetch in the static `__openPlugin` (offline-safety + Gate-40 deletion trap). *(decision #5)*
- **G-OB3 (devil's-advocate/architect):** dev-gate "Marketplace health" so consumers don't see an empty tab. *(decision #7 refinement)*
- **G-OB4 (devil's-advocate):** Sága-in-Configure vs the Observe↔Configure rule — flagged; deep-link offered as the rule-consistent alternative. *(decision #3)*
- **G-OB5 (architect):** the `vidarr→{heimdall, audit}` sub-carrier — `DASH_TAB_ALIAS` can't express it today; specify the `viewDashboard` special-case. *(Slice 2)*
- **G-OB6 (ops):** Gate 51's literal `"Perimeter alerts"` + `saga:"observe"` expectations break on the regroup — edit in the same commit + re-verify must-fail halves. *(P0)*

## P0 / P1 recommendations (Panel 2 cold-review)
_(appended in Phase 5)_
