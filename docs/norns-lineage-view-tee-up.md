# Norns — Urðr / Verðandi / Skuld lineage view: tee-up

> **Status:** TEE-UP (design, not started). Drafted 2026-05-30 after Heimdall (#142, v0.67.0) and Víðarr (#143, v0.68.0) established the substrate-reader pattern. The **third and last** of the event-substrate readers — it reads the scenario `events.jsonl` (P0.6) the way Heimdall read hook-events and Víðarr read posture-events. Reconciles build-plan §3.5 against current reality. Docs-only → commits to `main`, no PR.
>
> **Build only after #143 (Víðarr) merges** — Norns touches the same files (`generate-dashboards.py`, both `serve-dashboards.py`, `audit-gates.sh`, version), so building it before #143 lands would couple them or create conflicts.

## What Norns is

A **per-plugin lineage view** with three columns — past / present / future — answering "where has this plugin been, where is it, where is it going?":

| Column | Norse (display) | Plain-language | Content |
|---|---|---|---|
| Past | Urðr | "Lessons & history" | last 5 scenario surfaces (`events.jsonl`, `type:scenario_surfaced`), last 5 decision-log entries, last 10 commits |
| Present | Verðandi | "Current" | current `version`, active hook count, active rule count, last release date |
| Future | Skuld | "Proposed" | `next_version` + `roadmap[]` (P0.1) + open proposals in `docs/proposals/` |

Build-plan reference: §3.5 (lines 535–591). Effort estimate there: 12–16 h.

## ⚠ The load-bearing trap: git data + the exact-match freshness gate

**This is the single most important finding and it changes the architecture.** Build-plan §3.5 step 1 says to read `git log --oneline -10` and "last release date from `git log`" and **inline it into the dashboard at generator time** (`window.__norns`). That is a **direct conflict with Gate 13**:

- `dashboard.html` is **committed** and freshness-gated by **exact byte match** — `generate-dashboards.py --check` compares the regenerated HTML byte-for-byte against the committed file (unlike `check-guide-fresh.sh`, which strips volatile lines first).
- **git-log output is not stable across environments.** A full local clone and CI's shallow checkout produce different commit lists / dates. The repo-guide generator already hit exactly this — see `check-guide-fresh.sh`, which `grep -Ev`'s out `Generated …` and `Last updated</span>` before diffing *precisely because* "CI uses shallow checkout so the value differs from a full-history local clone."
- **Therefore: any git-derived data inlined into `dashboard.html` at generator time makes the dashboard perpetually fail Gate 13 in CI.** The generator currently shells out to git **zero** times (verified) — Norns would be the first, and naively it breaks the freshness gate.

### Resolution (the architecture decision)

Norns' git/scenario/decision data is **per-consumer, live, and environment-varying** — exactly the profile of Heimdall's hook-events and Víðarr's posture-events, which we already solved with a **served endpoint, not generator-time inlining.** So:

**Read Norns' dynamic data via a served `/__norns` endpoint, NOT `window.__norns` inlined at generator time.** Only the genuinely-static, committed-state parts (current `version`, hook/rule counts from the committed tree, `next_version`/`roadmap` from `plugin.json`) may be inlined as a `norns-data` JSON block — those don't vary by environment. The git log, scenario surfaces, and decision/proposal files are read live by the endpoint (served-mode only; honest empty state on a static host).

This **supersedes** §3.5's `window.__norns` + generator-time-git design, for the same reason Víðarr's tee-up superseded its `window.__vidarr` design: the spec predates the freshness gate's exact-match reality. It also keeps Norns consistent with the two readers already shipped.

## Other reconciliations (spec vs. reality)

| §3.5 says | Reality | Decision |
|---|---|---|
| "collapsible section inside the **Settings** tab, NOT a new tab (designer's gate)" | Heimdall + Víðarr both shipped as top-level tabs. But the designer's gate here is **explicit and reasoned** (lineage is reference material, not a frequent surface). | **Open question — see below.** Unlike Víðarr (where I'd recommend a tab), Norns has an explicit designer gate for Settings-collapsible. Lean toward honoring it, but confirm. |
| `dashboard-assets/norns.css` (new file) | No external-CSS mechanism; all CSS inline in `_CSS`. | CSS in `_CSS` (as Heimdall/Víðarr did). |
| `window.__norns` inlined per-plugin | See the trap above. | Served `/__norns` for dynamic data; inline JSON block only for committed-static fields. |
| Skuld reads `next_version` (P0.1) | **P0.1 never shipped** — no plugin declares `next_version` (verified). `roadmap[]` likewise absent. | **v1 ships Urðr + Verðandi only.** Skuld renders the spec's gated empty state ("No proposed version. Add a `next_version` field…"). This is exactly what §3.5 says to do when P0.1 is absent — not a descope, the planned v1. |
| Urðr reads `docs/decisions/<plugin>-*.md` | `docs/decisions/` **does not exist**; `docs/proposals/` **does**. | Urðr's decision-log source is absent → that sub-list shows its empty state. Scenarios (`events.jsonl`) + commits carry Urðr in v1. |

## Recommended shape (mirrors Heimdall/Víðarr, with the git caveat)

### Server side (BOTH `serve-dashboards.py` copies — byte-identical, Gate 32)
- `_read_norns(repo_root, plugin, days)` returning `{urdr:{scenarios, decisions, commits}, verdandi:{version, hooks, rules, last_release}, skuld:{next_version, roadmap, proposals}}`.
- **Urðr scenarios:** glob `.ravenclaude/runs/*/events.jsonl`, filter `type == "scenario_surfaced"` AND `scenario_path` under `plugins/<plugin>/scenarios/`, newest 5.
- **Urðr commits + Verðandi last_release:** `subprocess` `git log` — **this is why it must be server-side, not generator-time.** Guard every git call (wrap in try/except, tolerate no-git / shallow / non-repo → empty list). Never let a git failure 500 the endpoint.
- **Verðandi counts:** read the committed tree (hooks = `plugins/<plugin>/hooks/*.sh` minus `_`-prefixed, matching the repo-guide rule; rules = `plugins/<plugin>/rules/*`).
- **Skuld:** read `plugin.json` `next_version`/`roadmap` (absent → gated empty state); `docs/proposals/*.md` name-matched.
- Add `/__norns` to `do_GET` + `do_HEAD` in both copies; re-run the parity check.

### Generator side (`scripts/generate-dashboards.py`)
- `_render_norns_section()` — IF Settings-collapsible: a `<details>`/`<summary>` block injected into the Settings tab template; IF own tab: a tab following the Heimdall/Víðarr template. (Depends on the open question.)
- Plain-language legend always shown: "Urðr (Lessons & history) · Verðandi (Current) · Skuld (Proposed)."
- `loadNorns()` + `renderNorns()` in `_JS`, DOM-safe, served-vs-static probe; CSS in `_CSS` (three columns wide, stacked narrow).
- **No git data inlined into the committed HTML.** A `norns-data` JSON block, if used, carries only environment-invariant committed fields.

### Tests / gates
- **Gate 39** (bidirectional) + `scripts/check-norns-render.mjs`: extract the real `renderNorns`, assert the three columns render from a fixture, the Skuld gated-empty-state shows when `next_version` absent, and Urðr renders scenarios (must-fail: break a column). Plus a server-reader assertion (`_read_norns` returns the three keys; git failure → empty commits, not a throw) and a both-copies-present check.
- **Critically: confirm `generate-dashboards.py --check` (Gate 13) stays green** — i.e. prove no environment-varying data reached the committed HTML. The render test running against the committed `dashboard.html` is itself part of that proof.
- Keep green: Gate 13 / 32 / 35 / 37 (Heimdall) / 38 (Víðarr).

### Version + artifacts
- Core `0.68.0 → 0.69.0` (assuming #143 merged at 0.68.0); regenerate `dashboard.html` + `repo-guide.html` + `copilot/plugin.json`.
- `CLAUDE.md` Norns section.

## Acceptance (from §3.5, restated against the real shape)

1. The dashboard includes a "Plugin lineage (The Norns)" surface (tab or Settings-collapsible per the open question) with the three columns + always-visible plain-language legend.
2. Urðr renders ≥1 of: surfaced scenarios / decisions / commits (served mode).
3. Verðandi renders current version + active hook/rule counts + last release date (or "—").
4. Skuld shows the **gated empty state** (no plugin declares `next_version` today).
5. Norse names render with diacritics (Urðr / Verðandi / Skuld); a11y collapsible/keyboard order honored.
6. Served-only data degrades to an honest empty state on a static host.
7. **Gate 13 stays green** — no environment-varying git data in the committed HTML.

## Open questions for the build session

1. **Own tab vs. Settings-collapsible?** Heimdall + Víðarr set a tab precedent, BUT §3.5 has an **explicit, reasoned designer's gate** for Settings-collapsible (lineage is occasional reference, not a frequent operational surface). This is a genuine UX call and the spec's gate cuts the opposite way from Víðarr's. **Recommendation: honor the designer's gate — Settings-collapsible** (it's the one place the three readers should diverge), but confirm with Matt; it changes where the render code mounts.
2. **Per-plugin scope.** §3.5 is "per-plugin lineage" but the dashboard is generated per-plugin already (`plugins/<plugin>/dashboard.html`) — only `ravenclaude-core` actually ships a dashboard today. Confirm v1 = Norns on the **core** dashboard showing **core's** lineage (the other plugins have no dashboard to host it). Multi-plugin lineage is a later concern.
3. **Skuld now or later?** P0.1 (`next_version`) never shipped. Options: (a) ship Urðr+Verðandi, Skuld = gated empty state (the spec's v1 — recommended); (b) also land P0.1 (add `next_version` to `plugin.json` + a CI cross-check) so Skuld has data. (b) is a separate, larger piece — recommend (a) for this PR and track P0.1 separately.
4. **Git in the endpoint — acceptable?** The server already shells out (`apply-comfort-posture.py`, `thing-decision.py` via subprocess), so a guarded `git log` in `/__norns` is consistent. Confirm OK (it's the only way to get commit history without breaking Gate 13).

## Why this is the right "next"

Norns is the **last** substrate reader — it closes the loop by reading the third and final emission source (`events.jsonl`, P0.6), so after it ships **all three** substrate streams (hook-events / posture-events / scenario-events) have a UI reader and the v0.66.0 substrate is fully realized end-to-end. It's also the one with a real architectural gotcha (the git/freshness trap), which is exactly why it's worth teeing up carefully rather than discovering mid-build.
