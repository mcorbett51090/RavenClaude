# Víðarr — posture/security event-log panel: tee-up

> **Status:** TEE-UP (design, not started). Drafted 2026-05-30 after Heimdall (PR #142, core v0.67.0) landed the first reader of the event substrate. This doc reconciles the build-plan §3.11 Víðarr spec against the patterns Heimdall actually established, so the next session can build straight from here. Docs-only → commits to `main`, no PR (per AGENTS.md PR conventions).

## What Víðarr is

A **read-only** dashboard surface that renders the **posture/security event log** as a chronological, filterable table — the second reader of the v0.66.0 event substrate. Where Heimdall answers *"what guardrail tripped?"* (operational perimeter), Víðarr answers *"how did my security posture change over time, and what security-relevant denials happened?"* (the audit trail).

Sources (both shipped):

- **`.ravenclaude/posture-events.jsonl`** (P0.4) — one line per posture change: `{schema_version, ts, scope, source, security_deny_diff:{added,removed}, override_diff:{added,removed}}`.
- **`.ravenclaude/runs/*/hook-events.jsonl`** (P0.2) — hook deny/warn verdicts, **filtered to the security-relevant subset** (the `destructive-pattern` denials + layout/scope denials; warns are advisory, likely excluded or a separate filter).

Build-plan reference: §3.11 (lines 972–1022). Effort estimate there: 10–14 h.

## Decisions already locked by Heimdall (do NOT re-litigate)

The §3.11 spec predates the substrate build and assumes two patterns that **Heimdall superseded**. Follow Heimdall, not the literal spec text:

| §3.11 says | Reality after Heimdall (v0.67.0) | What to do |
|---|---|---|
| inline into `window.__vidarr` | The generator uses **`<script type="application/json" id="...-data">`** blocks, parsed with `JSON.parse(getElementById(...).textContent)`. There is **no `window.__` pattern** anywhere. | Use a `vidarr-data` JSON `<script>` block for the **committed/static** half (posture-events is git-ignored, so most data is served-only — see next row). |
| read `posture-events.jsonl` at **generator time** and inline it | `posture-events.jsonl` is **git-ignored and per-consumer** — the generator (run in the marketplace) cannot see a consumer's posture log. Heimdall's hook-events card is **served-only** for exactly this reason. | Read posture-events + filtered hook-events via a **new served endpoint** (`/__vidarr`), mirroring `/__heimdall`. The static/Pages mode shows an honest empty state. |
| new `dashboard-assets/vidarr.css` file | The generator **has no external-CSS mechanism** — all CSS is inline in the `_CSS` string. `dashboard-assets/` does not exist. | Add Víðarr CSS to the `_CSS` block (as Heimdall's `.hm-*`/`.gjallarhorn` styles were added). |
| "collapsible section in the **Settings** tab" | Heimdall added a **top-level tab**. A security audit log is arguably better as its own tab too, but the spec is explicit about Settings. | **Open question — see below.** Recommend its own tab for consistency + because the spec's own fallback is "its own subtab if it grows past ~50 events." |

## Recommended shape (mirrors Heimdall exactly — low-risk, gate-friendly)

A new **`/__vidarr` served endpoint** + a **`vidarr-data` inline block** (for anything committed) + a **`loadVidarr()` reader**, following the `/__heimdall` + `loadHeimdall()` template that is now proven and gated.

### Server side (BOTH `serve-dashboards.py` copies — byte-identical, Gate 32)
- Add a module-level `_read_posture_events(root, days)` helper next to `_read_hook_events` (root-independent, takes the `.ravenclaude` dir; tolerant of torn lines + missing ts, exactly like `_read_hook_events`).
- Add `_handle_vidarr()` that returns `{posture_events: [...], security_hook_events: [...], window_days: N}` where `security_hook_events` reuses `_read_hook_events` then filters to the security subset.
- Wire `/__vidarr` into `do_GET` + `do_HEAD` in **both** copies. Re-run `scripts/check-dashboard-server-parity.py`.

### Generator side (`scripts/generate-dashboards.py`)
- `_render_vidarr_tab()` returning a `_VIDARR_TAB_TEMPLATE` skeleton: the myth-cite intro, the filter UI (time-range select: 24h/7d/30d/all; event-type chips: posture-change / security_deny-match / hook-deny), and an empty table host.
- Tab button + panel + `validTabs` entry + lazy-load trigger (`if (tab === "vidarr" && !vidarrLoaded) loadVidarr();`).
- `loadVidarr()` + `renderVidarrTable()` + the filter handlers in `_JS`, DOM-safe (`createElement`/`textContent`, reuse `esc()` + `sagaEmptyPanel`), served-vs-static probe via the existing `probeReadEndpoint()`.
- Víðarr CSS in `_CSS` (chronological table, filter chips, plain-language headers).

### Tests / gates
- **Gate 38** (bidirectional) + a `scripts/check-vidarr-render.mjs` mirroring `check-heimdall-render.mjs`: extract the real `renderVidarrTable` from `dashboard.html`, assert a `security_deny` posture-event fixture renders a row, the time/type filters narrow it, and the empty range → "quiet" empty state (must-fail half: break the filter). Plus a server-reader assertion (`_read_posture_events` parses a fixture) and a both-copies-present check.
- Keep green: **Gate 13** (freshness — regenerate after every change), **Gate 32** (parity — `/__vidarr` in both servers), **Gate 35** (round-trip), **Gate 37** (Heimdall — unaffected, but the shared `_JS`/`_CSS` edits must not break it).

### Version + artifacts
- Core `0.67.0 → 0.68.0`; bump `plugin.json` + `marketplace.json`; regenerate `dashboard.html` + `repo-guide.html` + `copilot/plugin.json`.
- `CLAUDE.md` Víðarr section (read-only-mirror + serving-mode distinction + the posture-event ↔ panel mapping).

## Acceptance (from §3.11, restated against the real shape)

1. The Víðarr panel renders with a chronological event table (posture changes + security-relevant hook denials, newest first).
2. Filters work: time range (24h/7d/30d/all) **and** event type (posture-change / security_deny-match / hook-deny).
3. Read-only — no edit/dismiss affordances.
4. A controlled fixture (one `security_deny` add in `posture-events.jsonl`) appears in the panel.
5. Empty state ("No security events. Your perimeter has been quiet.") renders when both sources are empty for the selected range.
6. The myth-cite appears in the section intro.
7. Served-only data degrades to an honest empty state on a static host (Heimdall's serving-mode rule).

## Open questions for the build session

1. **Own tab vs. Settings-tab collapsible?** Spec says Settings-collapsible (with a "promote to subtab past ~50 events" escape hatch). Heimdall set the precedent of a top-level tab, and a top-level tab is simpler to gate + route. **Recommendation: own top-level tab "Víðarr" / "Security log"** — but this is a genuine UX call; confirm with Matt before building (it changes the routing + where the filter UI lives).
2. **Warns in scope?** §3.11 filters to "security_deny-related and Fenrir-related." `recursive-spawn` warns aren't security events — exclude them from Víðarr (they live in Heimdall's grey tier). Confirm the security subset = `destructive-pattern` denials + layout/scope denials + all posture-events; **exclude warns**.
3. **Overlap with Heimdall's hook-denials card.** Both read hook-events. Keep them distinct: Heimdall = *operational, last-30-day, all tiers, grouped-by-hook*; Víðarr = *security audit, filterable time range, posture-changes + security-denials interleaved chronologically*. No code shared beyond the `_read_hook_events` helper.

## Why this is the right "next"

Víðarr is the **smallest** remaining substrate reader (10–14 h, one data shape that's already emitted, a proven endpoint+render+gate template to copy). It completes the **posture** half of the observability story (Heimdall did the **perimeter** half), and it exercises the `posture-events.jsonl` half of the substrate that currently has *zero* readers — proving P0.4 end-to-end the way Heimdall proved P0.2. Norns (the knowledge worklist) is larger and reads the third source (`events.jsonl`); it should come after Víðarr.
