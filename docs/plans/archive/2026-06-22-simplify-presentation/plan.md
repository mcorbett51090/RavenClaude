<!-- FORGE planning run (standard depth, cross-model panels) — 2026-06-22. Plan only; not implemented. Recommended route: consider_ultraplan. -->

# RavenClaude Presentation Simplification — One Plan (Reconciled)

## The decision, stated plainly

Matt's ask: _"as simple as possible. Having an index AND a dashboard is too much."_ Both review panels misread what "too much" means. The index and the dashboard are **already one file** — `generate-index-dashboard.py` folds `render_fragment()` from the dashboard generator natively into `index.html` (no iframe). The complexity Matt is reacting to is **not two files**; it is that the single portal is an _operator console wearing a landing page as its first tab_ — sidebar task-nav (Configure / Observe / Act), a "Live data needs the local dashboard — run rc dashboard" banner, copy-command install buttons, an onboarding checklist whose step 0 is `/plugin install`. No amount of hero rewriting changes that surrounding chrome.

**Binding context settles the framing both panels left "open for Matt":** `ravenpower.net` is the consulting front-door; RavenClaude/`index.html` is **proof-of-craft**, not the pitch. So the contact CTA is _soft_ here and _hard_ on ravenpower.net. The simple public surface is a **bridge that points at ravenpower.net**, not a competing front-door with a hard "email Matt" button.

### Decisive route: a NEW dead-simple static pitch file + the untouched portal behind one quiet door

This is the critic's two-separated-surfaces option — the inverse of Panel A's _rejected_ Alt 1. Panel A rejected it on the false belief that it "breaks every committed deep-link and Gate 51/70." That rejection is wrong **if the pitch is a new file and the generated portal keeps its exact filename and routes.** Deep-links are `index.html#/heimdall` etc.; if the portal stays where it is and the pitch links _into_ it, no deep-link moves and no freshness gate fires.

| | **Panel A (collapse NAV to 2 + drop SECTION_TABS)** | **Panel B (keep portal, reword Home + localStorage suppression)** | **CHOSEN: new static pitch + untouched portal** |
|---|---|---|---|
| Prospect surface | Operator shell, reworded hero | Operator shell, reworded hero | A clean hand-authored one-screen pitch (no router, no banners, no catalog) |
| Gate 51 (`check-shell-router.mjs`) | **HARD FAILS** — see "Why Panel A is rejected" | Passes (NAV untouched) | Passes (NAV untouched) |
| Portal-side freshness gates (13/51/70/97) | Multiple rewrites | Regen + commit `index.html` (Gate 97/13 churn) | **Zero touched** on portal side |
| Solves "operator console is the prospect's surface" | No (lipstick) | No (lipstick + a localStorage _guess_ about who you are) | **Yes** — prospect literally never sees the console |
| Matt's daily Save&apply | One extra click, risk of dead-end | Unchanged | Unchanged (`rc dashboard` / quiet door) |

### Why Panel A is rejected (verified against the gate this session)

`scripts/check-shell-router.mjs` (read 2026-06-22) makes Panel A's "net simplification" a CI-blocking regression on three independent assertions:

1. **Line 91:** `NAV_IDS = ["home","discover","configure","observe","act","learn"]` — each asserted present. Collapsing to 2 fails immediately.
2. **Alias + owner destination checks:** every `SECTION_ALIAS` value and every `DASH_OWNER` value is asserted to be a **member of NAV_IDS** (`alias target "${target}" must be a real NAV section`; `DASH_OWNER target "${owner}" must be a real NAV section`). The moment `observe`/`configure`/`act`/`learn` leave NAV, `dashboard→observe`, `configuration→configure`, `commands→act`, etc. all throw. **Panel A's "leave SECTION_ALIAS + DASH_OWNER intact" is internally contradictory** — you cannot keep them intact and remove their destinations.
3. **SECTION_TABS loop (must-pass half):** `for (const sec of ["configure","observe","act","learn"]) assert(SECTION_TABS defines a sub-nav for sec)`, plus `"Run feed"`/`"Perimeter alerts"` text and `navChildren()→SECTION_TABS[id]`. **Panel A's "drop SECTION_TABS" hard-fails Gate 51** — it is asserted present, not optional.

Panel A buried a near-total Gate 51 rewrite (the array, both must-fail fixtures, every alias/owner entry, the `gjallarhorn` `#/heimdall` link at `generate-dashboards.py:6187`, the CLAUDE.md milestone) as a one-line "re-verify" caveat. Panel B caught this correctly and is the safer _of the two as framed_ — but it still preserves the wrong artifact as the prospect surface. **We take Panel B's gate-preservation discipline and the critic's surface-separation.**

---

## What ships

### Surface 1 — `pitch.html` (NEW, hand-authored, not generated)

A single-screen, static, GitHub-Pages-safe proof-of-craft page. **Not** emitted by any generator, so it cannot trip a freshness gate and has zero router/alias coupling.

- **Hero:** outcome-first headline — _"I build governed multi-agent AI systems for Microsoft-stack teams."_
- **One proof paragraph** naming the framework: the tribunal (command/decision review), the comfort-posture permission engine, the CI gate harness, the Capability Grounding Protocol.
- **3 static proof assets** — _screenshots/images_, not live renders: a captured tribunal verdict, the posture preset cards, the CI-gate list. (See prerequisite below — this is the real work both panels under-scoped.)
- **Primary CTA = soft, pointing at ravenpower.net** ("See how I work →"), consistent with ravenpower.net being the front-door. A secondary, quiet **"Developer / operator view →"** links into the existing portal (`index.html`).
- **No** router, **no** SECTION_ALIAS, **no** served-mode banner, **no** catalog, **no** onboarding checklist, **no** stat counts.
- **SEO meta authored here** for the prospect (the portal's own meta is fixed separately, see Surface 2 #4).

### Surface 2 — the existing portal (`index.html` + folded dashboard), kept and quietly demoted

`index.html`, `plugins/ravenclaude-core/dashboard.html`, `serve-dashboards.py`, `render_fragment()`, `_html_merge.py`, `#dash-root`, `window.__dashApp`, all `/__save` `/__csrf` `/__heimdall` `/__saga` endpoints, **and the entire 6-section NAV + SECTION_ALIAS + DASH_OWNER + SECTION_TABS — byte-for-byte unchanged.** Gates 13/51/70 stay green because nothing they assert changes. Reached only via the quiet "Developer / operator view" link on `pitch.html`, plus the existing `/dashboard` and `rc dashboard` launchers.

Four **small, gated** content edits to the portal (these DO require regenerating + committing `index.html`, and Gate 97 will correctly flag staleness if skipped — that is the gate working, not a bug):

1. **SEO meta for the portal** (`_index_dashboard_template.py:20-21,29`) — current `<title>`/`description`/`og:description` advertise _"Browse plugins, the specialist roster… comfort-posture permission editor"_ (catalog-browser framing the direction kills). Reframe to an outcome statement so anyone who finds the **portal** URL directly via search doesn't get the catalog snippet. (The richer prospect SEO lives on `pitch.html`.)
2. **Configure → Settings dead-end** (`_index_dashboard_template.py:1375`) — the callout links `<a href="#/settings">Settings tab</a>`, which on the static host _looks_ interactive but resolves to a non-writing editor behind the served-mode banner. Replace the hash-route link with an explicit copyable **`rc dashboard`** command so Matt's own Save&apply path is never a silent dead-end.
3. **Drop maintainer-only Home noise** (zero migration risk, no `#/` routes of their own): the `/wrap` "Contribution Staging Loop" quick action (`generate-index-dashboard.py:894-896`), and replace the static 3-line recent-activity snapshot (`_index_dashboard_template.py:1007-1011`) with a single `Last generated: {date}` pill.
4. **Fix the onboarding step-4 command** (`_index_dashboard_template.py:934`): `bash scripts/open-dashboard.sh` is the marketplace-developer command — replace with the consumer command (`/dashboard` in Claude Code, or `rc dashboard` in terminal).

> **Why not also suppress the onboarding checklist via localStorage (Panel B)?** Unnecessary under this plan. A prospect never reaches the portal's Home as their landing surface — they land on `pitch.html`. The localStorage heuristic was Panel B's workaround for _both audiences sharing one surface_; once the surfaces are separated, the heuristic (and its edge-case risk of a stale `rc-onboarding-step-0` key) is moot.

### README + docs (commit straight to main, no PR — docs rule)

- Collapse README's four near-identical opening blockquote URLs to **one** front-door link (the `pitch.html` / Pages root). Move the ~600-line inline catalog behind a collapsible section pointing at the in-portal catalog.
- Keep `GETTING_STARTED.md` as the single canonical first-run doc; fold the three-dashboard distinction into one short note. Move maintainer-only sections (eval-running block, un-glossed Norse-codename Mermaid) into `docs/`.

---

## Prerequisite both panels under-scoped (do this FIRST)

**The proof assets do not exist yet.** There is no build-time JSON of tribunal verdicts or posture presets to source a "proof tile" from, and the live versions (`/__*`-gated) render empty on static GitHub Pages by design (verified this session: only `.claude/.comfort-posture-applied.local.json` exists, nothing tribunal/verdict/preset-shaped). **A pitch with empty proof tiles is worse than no pitch.** Before `pitch.html` is worth shipping, author 3 static, Pages-safe proof assets — captured screenshots (or a small committed JSON the page renders client-side) of: (1) a representative tribunal verdict, (2) the posture preset cards, (3) the CI-gate list. This is the load-bearing work; the HTML around it is trivial by comparison.

---

## Migration safety (verified)

- **`/plugin marketplace update` (consumers):** `dashboard.html` and `serve-dashboards.py` untouched → consumer artifact, Save&apply, and every `/__*` endpoint byte-identical. Gate 13 passes unchanged.
- **Deep-links + Gate 51/70:** NAV, SECTION_ALIAS, DASH_OWNER, SECTION_TABS, DASH_SECTIONS untouched → every committed `index.html#/route` bookmark resolves; `gjallarhorn`'s `#/heimdall` link still routes. Gate 51 passes unchanged. **This is the whole point of choosing this route over Panel A.**
- **Gate 97 (index round-trip):** the four portal content edits DO change generated `index.html`, so the PR **must include a freshly regenerated `index.html` as part of the same change** — `python3 scripts/generate-index-dashboard.py && git add index.html` is a mandatory pre-push step (not optional). Skipping it leaves Gate 97 red for the next PR (FM-4). `pitch.html` is hand-authored and not under any generator, so it triggers no round-trip gate.
- **`.repo-layout.json`:** add a glob for `pitch.html` (and any `assets/` path the proof images live under) **before** pushing, or `validate-layout.yml` blocks the new file (the standard new-path discipline).
- **Pages:** `index.html` stays the canonical root artifact; `.nojekyll` already present. If `pitch.html` (not `index.html`) should be the default landing, that is a Pages-routing choice for Matt — see decisions.
- Run `scripts/audit-gates.sh` (Gates 13, 51, 97) before pushing.

## Risks carried forward

- **R1 — Proof assets are real work, not a footnote.** If they aren't authored, the pitch reads empty. Gate the build on them.
- **R2 — Visual weight.** A hand-authored pitch needs a real visual pass (`visual-feedback-loop` / `frontend-design`) before merge; "3 proof tiles" must be filled, not placeholder boxes.
- **R3 — Gate 97 staleness** if the regenerated `index.html` isn't committed with the portal edits (FM-4). Mandatory step, called out above.
- **R4 — Layout gate** on the new `pitch.html`/assets path if `.repo-layout.json` isn't updated first.
- **R5 — Standing constraint (not introduced here):** root vs plugin `serve-dashboards.py` mirror drift (Gate 32). This plan touches neither copy.

## Build order

1. Author the 3 static proof assets (the gating prerequisite).
2. Add `pitch.html` glob (+ assets) to `.repo-layout.json`.
3. Write `pitch.html` (static, soft CTA → ravenpower.net, quiet door → `index.html`).
4. Portal content edits 1-4 (`_index_dashboard_template.py` / `generate-index-dashboard.py`).
5. Regenerate + commit `index.html`; run `audit-gates.sh` (13/51/97).
6. Visual pass on `pitch.html`; eyeball the portal Home delta.
7. README/docs cleanup (straight to main).
8. One PR for the plugin-affecting changes (pitch.html + portal edits + regenerated index.html + layout glob), per the one-PR-when-possible preference.

---

## Decisions for Matt (FORGE — these are the genuine choices only you can make)

1. **Front-door architecture** — confirm: ravenpower.net is the hard consulting CTA; RavenClaude's `pitch.html` is proof-of-craft with a SOFT CTA pointing _at_ ravenpower.net (not a competing "email Matt" button). This sets how hard the pitch pushes.
2. **New file vs reword** — confirm `pitch.html` is a NEW hand-authored static file (chosen route, touches ZERO portal gates), rather than rewording the existing portal Home (Panel B, churns Gate 97/13). Same user-facing result.
3. **Pages landing** — should `pitch.html` be the _default_ landing (prospect lands there first, portal is the quiet door), or a sibling page that `index.html` links to? `index.html` stays the canonical deep-link artifact either way.
4. **Proof-asset prerequisite** — approve authoring 3 static, Pages-safe proof assets (tribunal verdict, posture presets, CI-gate list) BEFORE `pitch.html` ships. None exist today; the live versions render empty on static Pages. A pitch with empty tiles is worse than no pitch.
5. **Portal content edits** — confirm the 4 small portal edits now (SEO reframe, Configure→Settings `rc dashboard` fix, drop `/wrap` + static activity snapshot, fix onboarding step-4 command). These regenerate + commit `index.html` in the same PR.
6. **Keep the portal IA as-is** — confirm you accept the 6-section NAV / SECTION_TABS / SECTION_ALIAS / DASH_OWNER staying structurally unchanged (Panel A's collapse-to-2 is rejected — it hard-fails Gate 51 on three independent assertions, verified this session).
