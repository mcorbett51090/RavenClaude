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

## P0 / P1 recommendations (Panel 2 cold-review — tester-QA · deep-researcher · PM · UX)

Panel 2 **verified the plan's central thesis TRUE** — regroup-don't-rename (keep render fns + DOM ids verbatim) keeps the 6 render gates + round-trip green with zero `.mjs` edits, and the planned Gate-51 edits don't defang the must-fail halves (tester-QA, against all 7 gate sources; deep-researcher, claims 1/2/4/5/6/8/9 TRUE). The exposure is concentrated in **Slice 2** and in **two under-scoped premises**. Consolidated, deduped:

### P0 — must resolve before/within the relevant slice

- **P0-1 (Slice-1 sequencing) — do NOT ship the `#/vidarr → heimdall(audit)` alias in Slice 1.** The audit view is a Slice-2 deliverable; the alias would strand `#/vidarr` on a tab with no audit toggle (PM). Keep `#/vidarr` resolving to its own relabeled tab through Slice 1; the alias + the `viewDashboard` `sub="audit"` special-case land **atomically in the Slice-2 merge commit** (also makes Slice-2 rollback clean). `#/vidarr` back-compat is *contingent* on that special-case shipping in the same slice as the merge — verified the route chain drops `sub` today (deep-researcher, tester-QA, architect).
- **P0-2 (decision #7 mechanism) — "dev-gate Marketplace/Repo health" is NOT free reuse of an existing signal.** The client-readable `REPO_OWNER` constant is a **baked literal identical on every consumer install** (`generate-dashboards.py:8060`), `dev_repo_exempt` is a **user-set posture checkbox** (a consumer can tick it), and the real gate `_maintainer_substrate_exempt` is **server-side Python** running `gh repo view` (`thing-decision.py:512-557`) — unreachable from the tab JS and unavailable on the static Pages host (deep-researcher P0; PM P0-2 confirmed `SECTION_TABS` is a static array with no visibility mechanism). **Pick a mechanism before build:** (a) a **generator-time inlined flag** — only viable if `index.html` (marketplace) and the shipped `dashboard.html` (consumer) can carry *different* flag values, which needs verifying the two generation paths can diverge; or (b) **ship-to-all + the honest empty state** (cheaper, no new code/gate). Do not assume reuse.
- **P0-3 (Slice-2 security gate) — add a gate that the audit view SOURCES `/__vidarr`, not a client-filter of Heimdall's all-tiers stream.** Every existing gate tests components in isolation; a toggle wired to a row-filter over Heimdall's stream passes them all while leaking `warn` rows into "security audit" and dropping posture-change events the all-tiers stream never fetched (security + tester-QA P0-1). A **text-level assertion** in `check-shell-router.mjs` (the audit handler invokes `loadVidarr`/`/__vidarr`) matches the gate's no-eval doctrine and needs no browser.
- **P0-4 (Slice-2 sub-carrier + gate) — specify the `vidarr→{tab:heimdall, sub:"audit"}` carrier concretely + test it.** `DASH_TAB_ALIAS` is a flat `route→tab` string and drops `sub` (`_index_dashboard_template.py:810`, verified); the fix is a `viewDashboard` special-case or a `{tab, sub}` alias shape. Pair with a text assertion in `check-shell-router.mjs` (architect P0; tester-QA P0-2).
- **P0-5 (Gate 51, same commit) — edit `check-shell-router.mjs:144` (`saga:"observe"→"configure"`) and `:205` (`"Perimeter alerts"→"Guardrails & security"`), add `"marketplace-health"`/`"repo-health"` to `expectedDashboardRoutes`, and re-verify the three must-fail halves still trip** (ops; PM P0-3; tester-QA). Editing the template without the gate red-fails CI; editing only the gate risks defanging.
- **P0-6 (UX correctness) — the Discover "Plugin lineage" link is hard-wired to `ravenclaude-core`** (`#/norns` targets core only). Shipping it on every plugin page lands them all on core's lineage (a trust bug). **Ship it core-only for Slice 1, or parametrize `#/norns/<plugin>` first** (UX P0-3).
- **P0-7 (UX control) — the Guardrails live/audit split is a `role=tablist` segmented control ("Live activity" / "Security audit"), default Live, with lazy per-view fetch** — not a hidden binary toggle and not top-level chips (chips imply "same list, fewer rows," but the audit is a *different source* with posture rows the live stream never fetched). Keep Víðarr's existing chips *inside* the audit view (UX P0-1/P0-2).

### P1 — should-fix

- **Sága: take the deep-link, not the embed.** Three lenses (devil's-advocate, PM, UX) independently recommend keeping Sága in Observe and adding a `View verdict log →` link from the tribunal block, rather than re-parenting a read-only log into the *Configure* (settings) section — which contradicts the Observe↔Configure rule the IA just set. If you keep the embed, fence it (`READ-ONLY` pill + recessed container) so it doesn't read as broken config. **This is open decision #3 — the panel's recommendation is the deep-link.**
- **Relabel "Marketplace health" → "Repo health"** (insider framing; "Repo health" reads correctly for the maintainer who'll see it) + add the disambiguating empty state ("about the marketplace, not your project"); **order the dev-gated tab last** (`Run feed · Guardrails & security · Session · Repo health*`) so consumers don't see a hole in the nav (UX).
- **Gate-51 nuances:** the "add nidhoggr tab-alias check" requires **new gate code** (`DASH_TAB_ALIAS` is not sliced by the gate today) — not an edited assertion (tester-QA P1-1); `:205` only checks presence-anywhere (per-section label additions are *optional strengthening*); add label coverage for the relabeled sub-nav items so they're not silently droppable (tester-QA P1-3).
- **Wording fix:** `vidarr-filters` is a CSS **class**, not a DOM id (`generate-dashboards.py:6046`) — correct decision #2's markup instruction (deep-researcher).
- **Doc-lockstep (sweep, not a gate):** `best-practices/check-runtime-state.md:24-25`, `skills/mimir/SKILL.md`, and `CLAUDE.md` prose name `#/vidarr`/`#/norns`/`#/saga`/`#/mimir` as live destinations — they still *resolve* but now land on a different section/view. Update prose in the same PR (no gate enforces it). The SessionStart capability banner has **no** route literals — one fewer dependency than the plan feared (deep-researcher, PM).
- **Process:** park **Slice 2 behind an explicit trigger** rather than building it speculatively (PM + devil's-advocate — Slice 1 already captures the ~80% clarity win); route the migration note through the `plugin-release-checklist` skill; re-apply the served banner on in-tab view-switch (cached probe, cheap); name the owner of the manual no-browser visual pass per slice.

### Net changes to the build plan (post-review)
1. **Decision #7 hardened into a real fork:** dev-gate via a **generator-time inlined flag** (verify the two generations can diverge) **or** ship-to-all + empty-state. The "reuse the existing signal" path is **not viable** (P0-2).
2. **Slice boundaries tightened:** the `#/vidarr` alias + sub-carrier move *out* of Slice 1 into the Slice-2 merge commit (P0-1).
3. **Two new Slice-2 gates** (audit-source, sub-carrier) — the only behaviors with no coverage today (P0-3/P0-4).
4. **Sága → deep-link** is the panel's recommendation over the Configure embed (open decision #3).
5. **UX:** segmented control (not toggle/chips), "Repo health" rename, trailing dev-gated tab, core-only lineage link (P0-6/P0-7).
6. **Slice 2 parked behind a trigger;** Slice 1 ships the cheap 80% with near-zero gate risk.

