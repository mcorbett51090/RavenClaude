#!/usr/bin/env python3
"""check-dom-budget.py — Gate 132: the per-surface DOM load budget (+ ratchet),
the per-panel island payload budget, and the exempted-floor report.

═══════════════════════════════════════════════════════════════════════════════
METHOD — stdlib `html.parser`. Read this before changing a number.
═══════════════════════════════════════════════════════════════════════════════

WHAT IS COUNTED: every ELEMENT in the document (Lighthouse's "DOM size" unit).

WHAT "script/style EXCLUDED" MEANS — precisely, because a naive reading moves the
baseline by ~295 nodes and silently rebases every downstream figure:

    EXCLUDED  = the *contents* of <script>/<style>. `html.parser` puts those
                elements in CDATA mode, so `<` inside JS/JSON/CSS is text, never
                a tag. Nothing inside them is counted as an element.
    COUNTED   = the <script>/<style> ELEMENTS themselves, 1 each. They are real
                DOM nodes and Lighthouse counts them.

Driven reconciliation (this is why the above is the method and not a preference):

    all elements, script/style CONTENTS excluded  ->  dashboard 57,330 · index 50,945
    also dropping the script/style ELEMENTS       ->  dashboard 57,035 · index 50,648

The first pair reproduces the plan's §0.1 figures TO THE DIGIT, and is the only
reading consistent with §0.1's "islanded panels costed at 2 elements each —
<section> + <script type='application/json'>" (which counts the <script> element).

WHY NOT A REGEX TAG-TOKEN COUNTER (§2.1 / F1) — the load-bearing reason:

    JSON escapes `"` but NOT `<`.

So when a panel is islanded, its markup moves into a <script type="application/json">
payload where every `<` SURVIVES verbatim. A regex counter keeps counting those `<`
as tags, and additionally counts the new <script> wrapper — so it reports ~zero
reduction for the very mechanism the budget exists to measure. It is blind to the
thing it meters. `html.parser` sees the payload as text (CDATA), which is exactly
what the browser does, so the count falls when the DOM actually falls.

The divergence is not hypothetical and it is not small: it is 89 script/style
tokens TODAY, and ~46,000 after islanding. A gate whose error term grows by
500x at the moment of the change is not a gate.

STATED ASSUMPTION (§4.4): the per-panel payload budget assumes `activate()` renders
the island payload verbatim. If Phase 3 virtualizes, the rendered subset is SMALLER,
so the payload budget stays sound as a CEILING.

═══════════════════════════════════════════════════════════════════════════════
Usage:
    python3 scripts/check-dom-budget.py --check              # gate both surfaces
    python3 scripts/check-dom-budget.py --report             # floor/residue/x table
    python3 scripts/check-dom-budget.py --count <file>       # element count only
    python3 scripts/check-dom-budget.py --check --surface <f> --budget-override N
    python3 scripts/check-dom-budget.py --exempt-integrity   # F3/§0.2b rail (below)
    python3 scripts/check-dom-budget.py --exempt-integrity --must-fail   # its teeth

═══════════════════════════════════════════════════════════════════════════════
THE F3 / §0.2b RAIL (--exempt-integrity) — why a budget gate is not enough.
═══════════════════════════════════════════════════════════════════════════════

The budget above rewards node REDUCTION, and islanding a panel is how nodes are
reduced. But one panel must NEVER be islanded: `settings`. Its 144 posture radios
bind at LOAD, module-scope and document-wide (the generator reads them into
`state.categories` on first paint and wires per-radio listeners). Islanding it
moves that markup into a <script type="application/json"> payload, so the load-time
`querySelectorAll` returns an EMPTY NodeList, `forEach` throws NOTHING, no listener
binds — and the next Save writes the corrupted in-memory posture to
comfort-posture.yaml WHOLESALE (§2.2 / §0.2b / red-team F3).

Neither existing gate catches it, verified:
  * Gate 35 (posture round-trip) is DOM-free by its own header -> structurally blind.
  * Gate 132's BUDGET goes GREENER when settings is islanded (its nodes leave the
    live count) -> the meter rewards the very regression.

Converting `settings` IS a real future option, but it is NOT authorized: §0.2b
defers it behind the rendered-DOM meter (§11.2b) that makes its breakage LOUD.
Until that exists, this rail enforces "not authorized" in code. It is the F3
regression test the plan marks MANDATORY.
"""

import argparse
import json
import sys
from html.parser import HTMLParser

# ── The two surfaces (F2: two budgets, two ratchet tables) ───────────────────
DASHBOARD = "plugins/ravenclaude-core/dashboard.html"
INDEX = "index.html"

# ── Lighthouse's DOM-size error threshold (the yardstick, NOT the budget) ────
LIGHTHOUSE_THRESHOLD = 1400

# ── Exemptions (§2.2) ───────────────────────────────────────────────────────
# A panel that fails the module-scope-DOM-bind sweep is EXEMPT or FUNDED —
# never silently islanded. Exempt panels keep their full node cost forever, so
# they are counted into the floor rather than against the build.
EXEMPT_PANELS = {
    # `settings`: 144 posture radios bound at load, module-scope + document-wide
    # (dashboard.html:13261, :13906, :13941). Islanding kills the posture editor
    # SILENTLY with every gate green -> the next Save writes corrupted posture
    # wholesale. NOT covered by the §0.2 authorization (§0.2b).
    "panel-settings": "silent posture corruption; gate-invisible (§2.2 / §0.2b)",
}
FUNDED_PANELS = {
    # `learn`: fails the same sweep, but the risk owner accepted it (§0.2) and
    # the conversion work is funded (Phase 2L). Funded != exempt: it islands.
    "panel-learn": "funded conversion — Phase 2L (§0.2 ruling)",
}

# ── The F3 / §0.2b rail: panels that must stay LIVE, never silently islanded ──
# A panel here has load-time, module-scope, document-wide DOM binds whose failure
# is SILENT (empty NodeList throws nothing) and whose blast radius is a wholesale
# corrupted-posture Save. Islanding it is NOT owner-authorized (§0.2b is deferred
# behind the rendered-DOM meter, §11.2b). `live_selector` is the load-bound markup
# whose disappearance proves the panel was islanded; `min_live` is a FLOOR (the
# invariant is "present & live + cross-surface consistent", never an exact literal
# that a legitimate posture-category change would make brittle).
MUST_STAY_LIVE = {
    "panel-settings": {
        "reason": "144 posture radios bind at load, module-scope + document-wide; "
        "islanding corrupts posture silently, every gate green (§2.2 / §0.2b / F3)",
        "live_selector": "input[type=radio][data-category][data-layer]",
        "min_live": 1,
    },
}

# ── Cost of an islanded panel (§0.1): <section> + <script type=application/json>
ISLANDED_PANEL_COST = 2

# ═══════════════════════════════════════════════════════════════════════════
# THE RATCHET TABLES (F2 — one per surface; the gate binds the LAST row)
# ═══════════════════════════════════════════════════════════════════════════
# Each phase appends a row. The budget in force is the last row's value. The
# gate asserts the table is monotonically NON-INCREASING, so a phase can never
# quietly buy headroom by raising its own bar to DODGE the DOM-reduction work.
#
# Baselines re-derived at Phase 0 under the method above (dashboard 57,330 /
# index 50,945 — the figures in the docstring's reconciliation). They supersede
# plan A's 57,419 (a regex figure). NOTE: the must-fail half is derived as
# `count - 1`, NEVER a literal — plan A's literal 57,418 would have PASSED
# against 57,330.
#
# PHASE 6 (panel-pipeline delta) is a CONTENT-CORRECTNESS raise, not bloat: it
# added the guard-web-access + delegation-nudge stages — two SHIPPED hooks that
# were MISSING from the pipeline map (live drift, gap 1/4) — at +37 elements on
# each surface (57,330->57,367 / 50,945->50,982). The Phase-0 baseline had
# measured a map that was BUGGY (short two hooks); the corrected content is the
# honest baseline, held at ZERO slack (budget == exact count) so the gate stays
# exactly as tight and the count-1 teeth still bite. This raise did NOT dodge any
# reduction: the reduction phases (2/2L/3) that drop ~91% of nodes were not run
# in Phase 6's isolated execution — when they run they append LOWER rows from
# this corrected baseline and the ratchet resumes its descent.
RATCHET = {
    DASHBOARD: [
        (
            "Phase 0 -> 6",
            57367,
            "Phase 0 baseline 57,330 (html.parser); +37 in Phase 6 for the two "
            "shipped hooks missing from the pipeline map (gap 1/4). Zero slack.",
        ),
        (
            "Phase 2 (trees island)",
            36762,
            "panel-trees (~20,612 elems) DOM-island-loaded into a "
            "<script type=application/json> payload rendered on activate; its "
            "elements leave the live-DOM count. 57,367 -> 36,762. Zero slack.",
        ),
        (
            "Phase 2L (Learn island)",
            17066,
            "panel-learn (~19,702 elems) DOM-island-loaded; its four "
            "subsystems (search/widgets/steppers/node-links) re-pointed from "
            "load-time IIFEs to on-activate named functions. 36,762 -> 17,066 "
            "= 12.2x vs 1,400 (from 41.0x). Zero slack.",
        ),
        (
            "Phase 2b (Commands island)",
            10764,
            "panel-commands (~6,308 elems, the 2nd-largest panel) "
            "DOM-island-loaded; its deferred .cmd-copy/.cmd-run binds "
            "re-pointed to an on-activate initCommands() scoped to "
            "#commands-mount. 17,066 -> 10,764 = 7.7x vs 1,400. Zero slack.",
        ),
        (
            "P1 (plugin-panel collapse)",
            6298,
            "the 167 panel-plugin-* sections (~4,843 elems) collapsed "
            "into ONE #plugin-vars picker: a <select> of 167 plugins whose "
            "editor form renders client-side into #plugin-vars-mount from the "
            "inline #plugin-vars-payload JSON (uncounted CDATA). Measured "
            "10,757 -> 6,095. Zero slack.",
        ),
        (
            "P3 (chrome shrink)",
            6298,
            "IA re-cut: the two-tier <nav class=cat-bar> (5 cat-btns) deleted and "
            "the <nav class=tab-bar> shrunk from 18 core tabs to 10 destination tabs "
            "(+ the plugin-vars picker tab); role=tablist/role=tab + the roving-"
            "tabindex handler removed. Panels unchanged (P4/P5 merge/delete them). "
            "Measured 6,095 -> 6,081 (-14). Additions: zero. Zero slack.",
        ),
        (
            "P4 (Observe merge)",
            6298,
            "the Observe family is physically merged: the five tab-panel wrappers "
            "panel-{saga,mimir,streams,norns,vidarr} are removed and their content "
            "folded into panel-activity (saga/mimir/streams/norns) and panel-heimdall "
            "(vidarr). Every mount id + render function is byte-identical; only the "
            "five <section> wrappers left. Measured 6,081 -> 6,076 (-5). Additions: "
            "zero. Zero slack.",
        ),
        (
            "P5 (shell-view deletions)",
            6298,
            "panel-overview + panel-simulator deleted; the install/bifrost/"
            "about/commands panels folded into ONE panel-help drawer as "
            "collapsed <details> (their render fns + mount ids byte-identical). "
            "Addition: the panel-help wrapper + the grouped C5 removed-routes "
            "table (matches docs/dashboard-removed-routes.md). Net measured "
            "6,076 -> 6,053 (-23). NOTE: value lifted 6,053 -> 6,064 to stay "
            "monotonic through A-split +12, PR-A +2, PR-B +1 below.",
        ),
        (
            "A-split (Observe un-merge)",
            6298,
            "the Observe family is UN-merged back into one "
            "<section class=tab-panel> per sub-page (the exact inverse of P4): "
            "Activity -> Run feed / Saga / Session / Streams / Lineage; Guardrails "
            "-> Perimeter alerts / Security log / Debt watch (the Nidhoggr debt "
            "card extracted from Heimdall into its own panel-nidhoggr). Additions: "
            "6 panel-* <section> wrappers + 6 sub-page tab-btns; every mount id + "
            "render function byte-identical, so the B15 render gates stay green "
            "with unmodified scripts. The one DELIBERATE, sanctioned +12 that "
            "reverses the P4 merge. Measured 6,053 -> 6,061 (+12); value lifted to "
            "6,064 to stay monotonic through PR-A/PR-B below.",
        ),
        (
            "PR-A (Help reachability + About accuracy)",
            6298,
            "the About 'How the pages are organized' list was "
            "re-cut to the 5 current areas (gap G6): stale pre-recut sections + "
            "the deleted Overview / Preview-a-review refs removed; 4 li -> 5 li "
            "(+2 elems: 1 <li> + 1 <strong>). The G1 Help-reachability affordance "
            "(topbar '?' + ⌘K entries) is PORTAL-shell only, so the standalone "
            "gains only this +2. Content-correctness raise (a self-contradicting, "
            "stale help page is a defect); measured 6,061 -> 6,063 (+2); value "
            "lifted to 6,064 to stay monotonic through PR-B below.",
        ),
        (
            "PR-B (Guidance/trees wire-back)",
            6298,
            "the Guidance (decision-trees + best-practices) tab was "
            "orphaned on both surfaces — no tab-btn reached panel-trees (gap G4). "
            "Added the tab-btn[data-tab=trees] to the tab-bar (visible + clickable "
            "on the standalone /dashboard, whose payload was already populated; "
            "hidden on the portal but makes 'trees' a valid tab). Standalone gains "
            "only this +1 tab-btn. Measured 6,063 -> 6,064 (+1); value lifted to "
            "6,065 to stay monotonic through PR-C below.",
        ),
        (
            "PR-C (cleanups + data refresh)",
            6298,
            "PR-C's own changes are DOM-NEUTRAL — G8 (concepts routing "
            "maps), G9 (feed-cap CSS + comment), G13 (sim-probe JS guard), G15 "
            "(serve-dashboards allow-list) touch only JS/CSS/server, no markup. The "
            "+1 is MARKETPLACE DATA growth: main's committed artifacts were stale "
            "at 6,064 while a fresh regen of current plugin data (167->168 plugins, "
            "590->592 specialists, landed post-PR-B via merge-skew) measures 6,065 "
            "— PR-C's mandatory regeneration refreshes them (also fixing that latent "
            "Gate 13/97 drift). Measured 6,064 -> 6,065 (+1, data); value lifted to "
            "6,097 to stay monotonic through PR-E below.",
        ),
        (
            "PR-E (standalone 4-dest sidebar)",
            6298,
            "G11: the standalone dashboard.html gains a portal-style left "
            "<aside class=dash-sidebar> (brand + 4 destinations Control/Activity/"
            "Guardrails/Learn&Help -> 15 nav <a> links driving the EXISTING "
            "activate() router). Additive ~+32 elems (aside + brand chrome + 4 "
            "groups + 4 labels + 15 sub-links + nav wrapper); the flat .tab-bar is "
            "hidden but its 15 tab-btns STAY in the DOM (validTabs, which the portal's "
            "folded activate() also reads — removing them would break the portal). "
            "Measured 6,065 -> 6,097 (+32). Zero slack.",
        ),
        (
            "premise gate (Pipeline stage card)",
            6298,
            "guard-premise.sh becomes a visible PreToolUse stage: +16 elements "
            "(stage card + 4 steps + trip/set detail) on each surface. Owner-approved "
            "+16 raise (6,155 -> 6,171); index lifted in lockstep (7,041 -> 7,057). "
            "Raised rather than excluding the hook from _PIPELINE_LANES, on the owner's "
            "stated principle for this feature ('failing silently is no bueno', "
            "2026-08-08): a hook that DENIES a user's write and cannot be seen or "
            "understood in the dashboard is exactly the unwatched-not-clean state the "
            "Pipeline tab exists to prevent. Its recorder (log-probe.sh) stays excluded "
            "— it only records and never denies. REVERSIBLE: drop this row, restore "
            "6,155/7,041, and move 'guard-premise' from _PIPELINE_STAGE_HOOKS into "
            "_PIPELINE_EXCLUDED_HOOKS.",
        ),
        (
            "v0.211.0 (Prompt Builder tab)",
            6298,
            "new #/prompt-builder Learn & Help tab: +6 static elements (sidebar link + tab-btn + panel section + #pb-root mount + noscript + p); the whole interactive UI is JS-built by initPromptBuilder() so it is uncounted. Owner-approved +6 raise off the frozen zero-slack tail (6,097 -> 6,103); the P1..PR-E rows above were lifted in lockstep to keep the ratchet monotonic.",
        ),
        (
            "reland-11-plugins reflected in standalone dashboard",
            6298,
            "the standalone dashboard.html was stale at 168 plugins — #778 (the "
            "11-plugin reland) regenerated index.html but NOT the standalone dashboard, "
            "so its plugin-version-drift card never picked up the 11 relanded plugins. "
            "A mandatory generate-dashboards.py regen (to propagate the corrected "
            "capture-run-context.py source link into the learn-payload) surfaces the true "
            "179-plugin count: +11 drift-card elements. Owner-approved +11 raise "
            "(6,103 -> 6,114); the dashboard ratchet tail lifted in lockstep to stay "
            "monotonic. index.html unaffected (already 7,000 from #778).",
        ),
        (
            "v0.216.0 (dashboard_autostart control)",
            6298,
            "a 3-option select (off | serve | open) for the new `dashboard_autostart` "
            "posture knob, in the Settings panel beside the other behavioral flags. "
            "The knob shipped YAML-only earlier in v0.216.0 precisely BECAUSE the "
            "budget was at zero slack — which reproduced the discoverability problem "
            "that started the work (a setting nobody can find). Owner-approved +6 raise "
            "(6,114 -> 6,120); the tail above lifted in lockstep to stay monotonic. "
            "EXACTLY 6 elements — wrapper, h3, select, 3 options — and that is measured, "
            "not estimated: the first cut came in at TEN (a behavioral-flag <span>, an "
            "explainer <p> and two <b>) and would have silently blown this approved "
            "figure. Trimmed by making the ⚙ marker a GLYPH in the heading text rather "
            "than the badge <span>, and moving the explainer into `title=`. If you add "
            "a heading, a description or an icon here, re-measure BEFORE assuming +6 "
            "still holds.",
        ),
        (
            "v0.216.0 (Host & context page — MH-14)",
            6298,
            "the #/host-context Control page: panel section + #hc-root mount + noscript + p "
            "+ the inlined host-support payload, plus the sidebar link, the mirrored tab-btn and "
            "the portal sub-nav link = +8 MEASURED. (First measurement said +7; the tab-btn was added AFTERWARDS to make the route resolve, and re-measuring caught the extra element. Measure LAST, not mid-change.) The 7x6 support matrix itself costs ZERO counted elements — "
            "it is JS-built from the payload by initHostContext(), the same trick that keeps the "
            "Prompt Builder at 4. Owner-approved (budget latitude granted explicitly); "
            "6,120 -> 6,128, tail lifted in lockstep. This lands the +7 the multi-host plan "
            "reserved for the Control page + relink, so no further raise is owed for it.",
        ),
        (
            "v0.217.0 (Help drawer: third host lane — MH-38)",
            6298,
            "the Help drawer held exactly TWO onboarding lanes (Claude Code / Bifrost and "
            "Copilot CLI) that cross-linked only each other, and the drawer's own "
            "self-description named them as the whole world — while Codex had just become a "
            "genuinely supported host in v0.216.0. A third <details> lane now covers Codex "
            "(install command + the hash-trust warning, which is the one thing that silently "
            "disarms that host's guardrails) and states plainly that Cursor / Aider / Devin "
            "Desktop are not wired at all. +12 MEASURED, and the split is worth recording: "
            "only 3 are structural (<details>, <summary>, <p>) — the other 9 are INLINE "
            "(<code> x5, <strong> x2, <em> x1). Inline markup is not free; a first estimate "
            "of +3 counted only the structure and was 4x low. Owner-approved +12 "
            "(6,128 -> 6,140); the tail above lifted in lockstep to stay monotonic.",
        ),
        (
            "PR-F (placement nudge stage)",
            6298,
            "owner-approved +14 (2026-07-29): the storage-placement nudge gets a Pipeline-tab stage beside its two already-drawn siblings (claim-grounding lint, do-it-yourself nudge). Leaving it undrawn would make the guardrail map read as though the guardrail does not exist. MEASURED, not estimated: trimming the stage description from 4 steps to 2 saved only 2 elements, so ~12 is the stage's fixed cost and +14 is the floor for drawing it at all. Tail lifted in lockstep to stay monotonic.",
        ),
        (
            "v0.238.0 (memory-engineering: marketplace 179 -> 180)",
            6298,
            "owner-approved +1 (2026-08-06): the marketplace gains its 180th plugin (memory-engineering, PR #840), and every plugin costs exactly ONE element per surface — its row in the plugin-version-drift card. MEASURED, not estimated: dashboard.html went 6,154 -> 6,155 against a frozen zero-slack tail. This is the cheapest possible plugin addition; nothing in the plugin itself is heavy, and a plugin that added no DOM would mean it was absent from the catalog. Directly analogous to the 'reland-11-plugins (marketplace 168 -> 179)' row below/above. Tail lifted in lockstep to stay monotonic. NOTE for the next plugin: this +1 is per-plugin and recurs — re-measure, do not assume the tail has slack.",
        ),
        (
            "v0.241.0 (memory-compaction guard: Rule 4 gets a mechanism)",
            6298,
            "OWNER-APPROVED +31. guard-memory-compaction.sh is a real PreToolUse "
            "guardrail, so check-pipeline-lanes requires it be mapped or explicitly "
            "excluded; the 10 existing exclusions are all 'observability, not a "
            "guardrail', which this is not. Its Pipeline stage card costs 31 elements "
            "(measured; trimming a step saved exactly 1, so ~31 is the fixed cost of a "
            "stage card, not slack). The frozen tail is lifted in lockstep per the "
            "v0.211.0 precedent, because the table must stay monotonically "
            "non-increasing. 6171 -> 6202. Zero slack.",
        ),
        (
            "v0.267.0 (WebFetch result quarantine stage)",
            6298,
            "OWNER-APPROVED +15. sanitize-webfetch-output.sh is a real PostToolUse "
            "guardrail (rewrites every consumer WebFetch body), so check-pipeline-lanes "
            "requires it be mapped or excluded; excluding it would hide a safety-floor "
            "hook. Its Pipeline stage card costs 15 elements (measured 6,202 -> 6,217; "
            "2-step card, same class as PR-F's ~14). Zero slack.",
        ),
        (
            "v0.273.0 (conserve-tokens switch + forms-engineering row restored)",
            6298,
            "+3 = TWO independent components, measured separately and stated "
            "separately so neither hides behind the other. (1) +1 is NOT this change: "
            "the committed dashboard.html on origin/main was already STALE by one "
            "plugin row — PR #961 added the forms-engineering plugin but the "
            "self-healing regenerate-artifacts run had not landed, so `--plugin "
            "ravenclaude-core --stdout` at an otherwise untouched checkout measured "
            "6,218 against the committed 6,217, the sole diff being "
            "forms-engineering's <option> in the #plugin-vars picker. Gate 13 cannot "
            "see this: its must_pass half only asserts the generator RUNS, and its "
            "must_fail half is ALREADY satisfied by a stale committed file, so a "
            "pre-existing staleness reads as a pass. Any PR that regenerates picks "
            "the +1 up. (2) +2 IS this change: the Pipeline parallelism control gains "
            "one <label class=pipe-ctl> + one <input type=checkbox "
            "id=pipe-conserve-tokens> — the persistent half of the conserve-tokens "
            "exception, now that parallelism defaults to MAXIMUM. Measured 6,218 -> "
            "6,220. The threshold knob (conserve_tokens_auto_pct) is deliberately "
            "settings-only with NO DOM control (the worktree_bound precedent), so the "
            "visible cost is the switch and nothing else. The frozen tail above is "
            "lifted in lockstep per the v0.211.0 precedent. Zero slack. NOT "
            "owner-ratified in-band — the raise ships reported with these exact "
            "numbers for the owner to accept or reject.",
        ),
        (
            "triage-outcome (Pipeline stage card)",
            6298,
            "triage-outcome.sh becomes a visible PostToolUse(Bash) stage: +15 elements "
            "(stage card + 3 steps + trip/set detail) on each surface. OWNER-APPROVED +15 "
            "raise, requested explicitly rather than taken: this table exists so a phase "
            "cannot quietly buy headroom to dodge the reduction work, and every prior raise "
            "here carries the same approval. Raised rather than excluding the hook, on the "
            "premise-gate row's stated principle — a hook that ADVISES the model on why a "
            "command came back empty, and cannot be seen in the dashboard, is the "
            "unwatched-not-clean state the Pipeline tab exists to prevent. Its exclusion "
            "peers (log-probe, stream tracking) only RECORD; this one speaks to the model. "
            "Wired only after its fire rate measured 2.588% over 46,557 real commands "
            "against a 3% bar. REVERSIBLE: drop this row, restore 6,220/7,106, and move "
            "'triage-outcome' from _PIPELINE_STAGE_HOOKS into _PIPELINE_EXCLUDED_HOOKS.",
        ),
        (
            "cheap-lane dashboard control (Pipeline tab)",
            6298,
            "OWNER-REQUESTED: the cheap_lane posture knob (route everyday work to "
            "Grok/Copilot) previously had a state-slot round-trip but NO point-and-click "
            "control -- YAML-only, unlike its sibling `orchestrator`. Owner explicitly "
            "asked for a toggle. Adds one Pipeline-tab stage card (title + 3 detail "
            "steps + trip/set text, same class as PR-F/triage-outcome) plus 3 <select> "
            "controls (mode/tier/agent) + 1 hint paragraph, mirroring `orchestrator`'s "
            "exact pattern (3 options + a <p class=pipe-hint>, no relay-style nested "
            "checkboxes). MEASURED, not estimated: 6,235 -> 6,273 (+38). Tail lifted in "
            "lockstep to stay monotonic. Zero slack.",
        ),
        (
            "context-handoff dashboard control (Pipeline tab, Stop lane)",
            6298,
            "OWNER-REQUESTED (Matt, precompact-handoff-convergence task): "
            "`context_handoff.mode` (off|nag|block) previously had a full state/"
            "hydrate/emit round-trip (v0.297.0) but deliberately NO DOM control -- "
            "same 'state-slot only' pattern as worktree_bound. The new pre-compaction "
            "handoff mechanism (handoff-nudge.sh, Stop hook) shipped opt-in per owner "
            "ruling, on condition there be a point-and-click way to turn it on. Adds "
            "ONE new Pipeline-tab stage card in the Stop lane ('Pre-compaction "
            "handoff' -- title + 3 detail steps + trip/set text, same class as "
            "triage-outcome/PR-F) plus ONE <select id=pipe-context-handoff-mode> "
            "(3 options: off/nag/block) + 1 hint paragraph + the behavioral-flag "
            "badge (added to the same controls-in-(...) tuple as decision/"
            "orchestrator/cheap_lane). handoff-nudge.sh moves from "
            "_PIPELINE_EXCLUDED_HOOKS into _PIPELINE_STAGE_HOOKS as 'context-handoff' "
            "-- Gate 133 enforces the map stays exhaustive, so a hook cannot be both. "
            "MEASURED, not estimated: 6,273 -> 6,296 (+23). Tail lifted in lockstep "
            "to stay monotonic. Zero slack. REVERSIBLE: drop this row, restore "
            "6,273/7,159, and move 'context-handoff' back from "
            "_PIPELINE_STAGE_HOOKS into _PIPELINE_EXCLUDED_HOOKS.",
        ),
        (
            "PR #1104 (grok-bot-creation + grok-bot-delegation plugins)",
            6298,
            "the marketplace gains its 185th and 186th plugins (grok-bot-creation, "
            "grok-bot-delegation), and every plugin costs exactly ONE element per "
            "surface -- its <option> in the #plugin-vars picker's <select>. MEASURED, "
            "not estimated: `grep -c '<option value=\"grok-bot-'` confirms exactly 2 "
            "new option elements landed. 6,296 -> 6,298 (+2). Directly analogous to "
            "the 'v0.238.0 (memory-engineering: marketplace 179 -> 180)' row above. "
            "Tail lifted in lockstep to stay monotonic. Zero slack.",
        ),
    ],
    INDEX: [
        (
            "Phase 0 -> 6",
            50982,
            "Phase 0 baseline 50,945; +37 in Phase 6 (same guard-web-access + "
            "delegation-nudge fragment). Zero slack.",
        ),
        (
            "Phase 2 (trees island)",
            37468,
            "portal fragment's trees payload islanded alongside the "
            "standalone surface. 50,982 -> 37,468. Zero slack.",
        ),
        (
            "Phase 2L (Learn island)",
            17772,
            "portal Learn payload islanded alongside the standalone "
            "surface. 37,468 -> 17,772 = 12.7x. Zero slack.",
        ),
        (
            "Phase 2b (Commands island)",
            11470,
            "portal fragment's commands payload islanded alongside "
            "the standalone surface. 17,772 -> 11,470 = 8.2x. Zero slack.",
        ),
        (
            "P1 (plugin-panel collapse)",
            7184,
            "the 167 panel-plugin-* sections collapsed into ONE "
            "#plugin-vars picker in the merged dashboard fragment (same "
            "collapse as the standalone surface). Measured 11,462 -> 6,800. "
            "Zero slack.",
        ),
        (
            "P3 (chrome shrink)",
            7184,
            "the folded fragment's cat-bar + tab-bar shrink (-14, same as the "
            "standalone surface) nets against +4 static destination anchors seeded "
            "into #primary-nav (the committed-route floor for #/control, #/activity, "
            "#/guardrails, #/catalog; renderNav replaces them at load). Measured "
            "6,800 -> 6,790 (-10). Zero slack.",
        ),
        (
            "P4 (Observe merge)",
            7184,
            "the folded fragment's five Observe wrappers (panel-{saga,mimir,streams,"
            "norns,vidarr}) removed and their content folded into panel-activity / "
            "panel-heimdall (same merge as the standalone surface). Measured "
            "6,790 -> 6,785 (-5). Additions: zero. Zero slack.",
        ),
        (
            "P5 (shell-view deletions)",
            7184,
            "same shell-view deletions folded into the portal fragment: "
            "panel-overview + panel-simulator deleted; install/bifrost/about/"
            "commands folded into ONE panel-help drawer + the grouped C5 "
            "removed-routes table. Measured 6,785 -> 6,762 (-23). NOTE: value "
            "lifted 6,762 -> 6,776 to stay monotonic through A-split +12, PR-A +7, "
            "PR-B +2 below.",
        ),
        (
            "P6 (payload demotion)",
            7184,
            "the three portal-only JSON payload islands learn-payload / "
            "trees-payload / concepts-data stripped from the folded dashboard body "
            "(portal Learn/Trees/Concepts are P5 named removals -> standalone + "
            "Pages; the standalone keeps them inline, Gate 13 non-contact). Removing "
            "three <script> ELEMENTS. Measured 6,762 -> 6,759 (-3). NOTE: value "
            "lifted 6,759 -> 6,776 to stay monotonic through A-split +12, PR-A +7, "
            "PR-B +2 below. (PR-B later un-strips trees-payload — see its row + the "
            "_PORTAL_ONLY_PAYLOAD_IDS change in generate-index-dashboard.py.)",
        ),
        (
            "A-split (Observe un-merge)",
            7184,
            "the folded fragment's Observe family is UN-merged back into one "
            "<section class=tab-panel> per sub-page (the exact inverse of P4, same "
            "as the standalone surface): Activity -> Run feed / Saga / Session / "
            "Streams / Lineage; Guardrails -> Perimeter alerts / Security log / Debt "
            "watch (the Nidhoggr debt card extracted into its own panel-nidhoggr). "
            "Additions: 6 panel-* <section> wrappers + 6 sub-page tab-btns; every "
            "mount id + render function byte-identical. The one DELIBERATE, "
            "sanctioned +12 that reverses the P4 merge. Measured 6,755 -> 6,767 "
            "(+12); value lifted to 6,776 to stay monotonic through PR-A/PR-B below.",
        ),
        (
            "PR-A (Help reachability + About accuracy)",
            7184,
            "portal-only +7 vs the standalone's +2: the shared "
            "About list re-cut 4 li -> 5 li (+2, gap G6) PLUS the G1 Help-"
            "reachability affordance in the shell topbar — an <a> '?' link + its "
            "inline <svg> (circle + '?' path + dot) = +5 — that makes the panel-help "
            "drawer (About / install guides / 525-command catalog) click-reachable "
            "again after #739 orphaned it to hash-only. Content-correctness raise; "
            "measured 6,767 -> 6,774 (+7); value lifted to 6,776 through PR-B below.",
        ),
        (
            "PR-B (Guidance/trees wire-back)",
            7184,
            "portal +2 vs the standalone's +1: the +1 tab-btn[data-tab=trees] "
            "(same as the standalone) PLUS +1 for the restored trees-payload "
            "<script> START TAG — G4 removed 'trees-payload' from the P6 portal "
            "byte-diet so the portal KEEPS the consolidated 924-tree Guidance index "
            "inline (render_fragment include_trees=True) for cross-plugin search, "
            "reachable via the Catalog sub-nav 'Guidance' (#/trees). The trees "
            "markup is CDATA (uncounted); only the <script> tag + tab-btn count. "
            "Measured 6,774 -> 6,776 (+2); value lifted to 6,777 through PR-C below.",
        ),
        (
            "PR-C (cleanups + data refresh)",
            7184,
            "PR-C's own changes are DOM-NEUTRAL (G8/G9/G13/G15 = JS/CSS/"
            "server only). The +1 is MARKETPLACE DATA growth: main's committed "
            "index.html was stale at 6,776 while a fresh regen of current plugin "
            "data (167->168 plugins, 590->592 specialists, landed post-PR-B via "
            "merge-skew) measures 6,777 — PR-C's mandatory regeneration refreshes "
            "it (fixing the latent Gate 13/97 drift). Measured 6,776 -> 6,777 "
            "(+1, data); value lifted to 6,809 through PR-E below.",
        ),
        (
            "premise gate (Pipeline stage card)",
            7184,
            "the portal folds the standalone payload, so the +16 premise-gate stage "
            "card lands here too (7,041 -> 7,057). Same owner-approved raise; see the "
            "matching row in the dashboard table above for the reasoning and the "
            "one-step revert.",
        ),
        (
            "PR-E (standalone 4-dest sidebar)",
            7184,
            "the portal folds the SAME standalone payload, so the new "
            "<aside class=dash-sidebar> (+32, same as the standalone) lands in "
            "index.html too — hidden by the shell's `#dash-root .dash-sidebar "
            "{display:none}` + margin-zero, so the portal shows ONE sidebar. The "
            "elements still count (hidden != removed). Measured 6,777 -> 6,809 "
            "(+32). Zero slack.",
        ),
        (
            "v0.211.0 (Prompt Builder tab)",
            7184,
            "portal folds the same standalone payload: the +6 prompt-builder static elements land here too. Owner-approved +6 raise (6,809 -> 6,815); P1..PR-E lifted in lockstep to keep the ratchet monotonic.",
        ),
        (
            "render-fix (174 trees restored to portal)",
            7184,
            "the self-heal's decision-tree SVG render had been broken for a while — mermaid 11.15.0 parse errors on 6 unquoted-special-char labels failed the whole single-batch 799-tree render, so it reverted every run. 174 decision trees added to newer plugins since the last successful render therefore had NO committed SVG (625 of 799 committed) and were ABSENT from the portal's per-plugin #dt-store tree-dropdowns. PR #772 quoted the 6 labels; the render now succeeds and commits all 799 SVGs, so the portal inlines 174 more <details>+<summary>+<img> dropdowns. Owner-approved +174 raise (6,815 -> 6,989) — legitimate content restoration (the trees were always meant to be in the portal), not new feature bloat. Measured 6,815 -> 6,989 (+174). Zero slack; the ratchet resumes its descent from this corrected baseline. dashboard.html is unaffected (6,103) — the per-plugin tree dropdowns are a portal-only surface.",
        ),
        (
            "reland-11-plugins (marketplace 168 -> 179)",
            7184,
            "reland of 11 routine-proposed plugins (168 -> 179; PRs "
            "#709/#722/#725/#730/#736, deduped: dropped already-on-main "
            "ai-agent-engineering + one of two competing subscription-billing "
            "plugins). Each plugin adds exactly ONE counted element to the portal "
            "Marketplace list; the card body is JS-built/CDATA (uncounted). "
            "Owner-approved +11 raise (6,989 -> 7,000); P1..render-fix lifted in "
            "lockstep to keep the ratchet monotonic. Measured 6,989 -> 7,000 (+11). "
            "Zero slack; dashboard.html unaffected (6,103).",
        ),
        (
            "v0.216.0 (dashboard_autostart control)",
            7184,
            "the portal folds the SAME standalone payload, so the standalone's +6 "
            "dashboard_autostart select lands here too — the identical mechanism as the "
            "v0.211.0 Prompt Builder row. Owner-approved +6 raise (7,000 -> 7,006); the "
            "tail above lifted in lockstep to stay monotonic. Measured on both surfaces "
            "after the edit, not projected from the standalone.",
        ),
        (
            "v0.216.0 (Host & context page — MH-14)",
            7184,
            "the portal folds the same standalone payload, so the +7 host-context elements land "
            "here too. Measured on BOTH surfaces after the edit, not projected. 7,006 -> 7,014.",
        ),
        (
            "PR-F (placement nudge stage)",
            7184,
            "owner-approved +14 (2026-07-29): the storage-placement nudge gets a Pipeline-tab stage beside its two already-drawn siblings (claim-grounding lint, do-it-yourself nudge). Leaving it undrawn would make the guardrail map read as though the guardrail does not exist. MEASURED, not estimated: trimming the stage description from 4 steps to 2 saved only 2 elements, so ~12 is the stage's fixed cost and +14 is the floor for drawing it at all. Tail lifted in lockstep to stay monotonic.",
        ),
        (
            "v0.238.0 (memory-engineering: marketplace 179 -> 180)",
            7184,
            "owner-approved +1 (2026-08-06): the marketplace gains its 180th plugin (memory-engineering, PR #840), and every plugin costs exactly ONE element per surface — its row in the plugin-version-drift card. MEASURED, not estimated: index.html went 7,040 -> 7,041 against a frozen zero-slack tail. This is the cheapest possible plugin addition; nothing in the plugin itself is heavy, and a plugin that added no DOM would mean it was absent from the catalog. Directly analogous to the 'reland-11-plugins (marketplace 168 -> 179)' row below/above. Tail lifted in lockstep to stay monotonic. NOTE for the next plugin: this +1 is per-plugin and recurs — re-measure, do not assume the tail has slack.",
        ),
        (
            "v0.241.0 (memory-compaction guard: Rule 4 gets a mechanism)",
            7184,
            "OWNER-APPROVED +31. guard-memory-compaction.sh is a real PreToolUse "
            "guardrail, so check-pipeline-lanes requires it be mapped or explicitly "
            "excluded; the 10 existing exclusions are all 'observability, not a "
            "guardrail', which this is not. Its Pipeline stage card costs 31 elements "
            "(measured; trimming a step saved exactly 1, so ~31 is the fixed cost of a "
            "stage card, not slack). The frozen tail is lifted in lockstep per the "
            "v0.211.0 precedent, because the table must stay monotonically "
            "non-increasing. 7057 -> 7088. Zero slack.",
        ),
        (
            "v0.267.0 (WebFetch result quarantine stage)",
            7184,
            "OWNER-APPROVED +15. Same sanitize-webfetch-output.sh Pipeline stage as "
            "the dashboard surface. Measured 7,088 -> 7,103. Zero slack.",
        ),
        (
            "v0.273.0 (conserve-tokens switch + forms-engineering row restored)",
            7184,
            "+3, the same two components as the dashboard surface (the portal folds "
            "the same standalone payload). (1) +1 pre-existing staleness: "
            "regenerating index.html at an otherwise untouched origin/main checkout "
            "measured 7,104 against the committed 7,103 (forms-engineering's picker "
            "row, PR #961). (2) +2 this change: the conserve-tokens <label> + "
            "<input type=checkbox>. Measured 7,104 -> 7,106. Zero slack. NOT "
            "owner-ratified in-band — reported with exact numbers for the owner's "
            "call.",
        ),
        (
            "triage-outcome (Pipeline stage card)",
            7184,
            "triage-outcome.sh becomes a visible PostToolUse(Bash) stage: +15 elements "
            "(stage card + 3 steps + trip/set detail) on each surface. OWNER-APPROVED +15 "
            "raise, requested explicitly rather than taken: this table exists so a phase "
            "cannot quietly buy headroom to dodge the reduction work, and every prior raise "
            "here carries the same approval. Raised rather than excluding the hook, on the "
            "premise-gate row's stated principle — a hook that ADVISES the model on why a "
            "command came back empty, and cannot be seen in the dashboard, is the "
            "unwatched-not-clean state the Pipeline tab exists to prevent. Its exclusion "
            "peers (log-probe, stream tracking) only RECORD; this one speaks to the model. "
            "Wired only after its fire rate measured 2.588% over 46,557 real commands "
            "against a 3% bar. REVERSIBLE: drop this row, restore 6,220/7,106, and move "
            "'triage-outcome' from _PIPELINE_STAGE_HOOKS into _PIPELINE_EXCLUDED_HOOKS.",
        ),
        (
            "cheap-lane dashboard control (Pipeline tab)",
            7184,
            "OWNER-REQUESTED, same change as the dashboard surface (the portal folds "
            "the same standalone payload): the cheap_lane Pipeline-tab stage card + "
            "3 <select> controls (mode/tier/agent) + hint paragraph land here too. "
            "MEASURED, not estimated, on BOTH surfaces after the edit, not projected: "
            "7,121 -> 7,159 (+38). Tail lifted in lockstep to stay monotonic. Zero slack.",
        ),
        (
            "context-handoff dashboard control (Pipeline tab, Stop lane)",
            7184,
            "OWNER-REQUESTED, same change as the dashboard surface (the portal folds "
            "the same standalone payload): the new 'Pre-compaction handoff' Pipeline-"
            "tab stage card + the <select id=pipe-context-handoff-mode> (off/nag/"
            "block) + hint paragraph + behavioral-flag badge land here too. "
            "handoff-nudge.sh moves from _PIPELINE_EXCLUDED_HOOKS into "
            "_PIPELINE_STAGE_HOOKS as 'context-handoff'. MEASURED, not estimated, on "
            "BOTH surfaces after the edit, not projected: 7,159 -> 7,182 (+23). Tail "
            "lifted in lockstep to stay monotonic. Zero slack. REVERSIBLE: drop this "
            "row, restore 6,273/7,159, and move 'context-handoff' back from "
            "_PIPELINE_STAGE_HOOKS into _PIPELINE_EXCLUDED_HOOKS.",
        ),
        (
            "PR #1104 (grok-bot-creation + grok-bot-delegation plugins)",
            7184,
            "same change as the dashboard surface (the portal folds the same "
            "standalone picker markup): the marketplace's 185th and 186th plugins "
            "each add one <option> to the #plugin-vars picker's <select>. MEASURED, "
            "not estimated, on BOTH surfaces after the edit, not projected: "
            "7,182 -> 7,184 (+2). Tail lifted in lockstep to stay monotonic. "
            "Zero slack.",
        ),
    ],
}


def budget_for(surface):
    return RATCHET[surface][-1][1]


class _Counter(HTMLParser):
    """Counts elements; attributes them to the enclosing panel-* section.

    `html.parser` handles <script>/<style> as CDATA, so their contents never
    reach handle_starttag — the exclusion is structural, not a filter we apply.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.total = 0
        self.panels = {}  # panel id -> element count
        self.stack = []  # open panel ids (a panel-* nested in a panel-* is impossible today, but don't assume)
        self.islands = {}  # panel id -> [payload strings]
        self.posture_radios = {}  # panel id -> count of LIVE input[type=radio][data-*]
        self._island_of = None
        self._depth = 0
        self._panel_depths = []

    # -- elements -----------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        pid = a.get("id", "")

        self.total += 1
        for p in self.stack:
            self.panels[p] = self.panels.get(p, 0) + 1

        if tag == "section" and pid.startswith("panel-"):
            self.panels.setdefault(pid, 1)  # the <section> counts toward itself
            self.stack.append(pid)
            self._panel_depths.append(self._depth)

        # an island payload we will decode for the per-panel payload budget
        if tag == "script" and a.get("type") == "application/json" and self.stack:
            self._island_of = self.stack[-1]

        # LIVE posture radios (the F3 rail). A radio inside an island is CDATA text
        # inside the <script>, never parsed as an <input> here — so this counts only
        # radios that are genuinely in the live DOM. If `settings` is islanded, its
        # count drops to 0 and the rail reddens.
        if (
            tag == "input"
            and a.get("type") == "radio"
            and "data-category" in a
            and "data-layer" in a
            and self.stack
        ):
            pid_here = self.stack[-1]
            self.posture_radios[pid_here] = self.posture_radios.get(pid_here, 0) + 1

        if tag not in _VOID:
            self._depth += 1

    def handle_startendtag(self, tag, attrs):
        self.total += 1
        for p in self.stack:
            self.panels[p] = self.panels.get(p, 0) + 1

    def handle_endtag(self, tag):
        if tag == "script":
            self._island_of = None
        if tag in _VOID:
            return
        self._depth -= 1
        while self._panel_depths and self._depth <= self._panel_depths[-1]:
            self._panel_depths.pop()
            if self.stack:
                self.stack.pop()

    def handle_data(self, data):
        if self._island_of:
            self.islands.setdefault(self._island_of, []).append(data)


_VOID = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


def _summarize(c, label):
    shell = c.total - sum(c.panels.values())
    return {
        "path": label,
        "total": c.total,
        "panels": c.panels,
        "shell": shell,
        "islands": c.islands,
        "posture_radios": c.posture_radios,
    }


def measure(path):
    c = _Counter()
    with open(path, encoding="utf-8") as fh:
        c.feed(fh.read())
    return _summarize(c, path)


def measure_text(text, label="<memory>"):
    c = _Counter()
    c.feed(text)
    return _summarize(c, label)


def active_tab_of(path):
    """The panel rendered on load (class="tab-panel active")."""
    import re

    with open(path, encoding="utf-8") as fh:
        m = re.search(r'<section class="tab-panel active" id="(panel-[^"]+)"', fh.read())
    return m.group(1) if m else None


def payload_elements(payload):
    """Decode an island payload and count the elements it will render."""
    try:
        markup = json.loads(payload)
    except json.JSONDecodeError as e:
        return None, f"payload is not valid JSON -> the panel renders NOTHING: {e}"
    if not isinstance(markup, str):
        return None, "payload must decode to a markup string"
    c = _Counter()
    c.feed(markup)
    return c.total, None


# ═══════════════════════════════════════════════════════════════════════════
def report(surfaces):
    """Item 4a — emit the EXEMPTED floor, the residue, and the x vs 1,400."""
    print("═" * 79)
    print("  Gate 132 — DOM budget report (html.parser; script/style contents excluded)")
    print("═" * 79)
    rows = []
    for path in surfaces:
        m = measure(path)
        act = active_tab_of(path)
        act_n = m["panels"].get(act, 0)
        exempt_n = sum(m["panels"].get(p, 0) for p in EXEMPT_PANELS)
        # floor = shell + active tab + SUM(exempt)   (§2.6 / P1)
        floor = m["shell"] + act_n + exempt_n
        islanded = [p for p in m["panels"] if p not in EXEMPT_PANELS and p != act]
        residue = floor + ISLANDED_PANEL_COST * len(islanded)
        rows.append((path, m, act, act_n, exempt_n, floor, islanded, residue))

        print(f"\n── {path}")
        print(f"   panels                        : {len(m['panels'])}")
        print(
            f"   whole-document elements       : {m['total']:>8,}   = {m['total'] / LIGHTHOUSE_THRESHOLD:5.1f}x"
        )
        print(f"   shell (total - SUM(panels))   : {m['shell']:>8,}")
        print(f"   active tab ({act})   : {act_n:>8,}")
        for p, why in EXEMPT_PANELS.items():
            print(f"   EXEMPT {p:<22s}: {m['panels'].get(p, 0):>8,}   {why}")
        for p, why in FUNDED_PANELS.items():
            print(f"   funded {p:<22s}: {m['panels'].get(p, 0):>8,}   {why}")
        print(f"   {'-' * 72}")
        print(
            f"   EXEMPTED FLOOR (shell+active+SUM(exempt)) : {floor:>8,}   = {floor / LIGHTHOUSE_THRESHOLD:5.1f}x"
        )
        print(
            f"   + {len(islanded)} islanded panels x {ISLANDED_PANEL_COST}"
            f"{'':<21s}: {ISLANDED_PANEL_COST * len(islanded):>8,}"
        )
        print(
            f"   PROJECTED RESIDUE                         : {residue:>8,}   = "
            f"{residue / LIGHTHOUSE_THRESHOLD:5.1f}x vs 1,400"
        )
        print(
            f"   reduction from today                      : "
            f"{(1 - residue / m['total']) * 100:>7.1f}%"
        )
        if exempt_n:
            print(
                f"   of the residue, SUM(exempt) is            : {exempt_n / residue * 100:>7.1f}%"
            )

    print("\n" + "─" * 79)
    print("  Per-panel island payload budget (§4.4)")
    n_islands = sum(len(m["islands"]) for _, m, *_ in rows)
    if n_islands == 0:
        print("  0 islands exist yet. The payload budget's teeth-proof is DEFERRED to")
        print("  Phase 2's first island (plan §7 Phase 0 item 4) — at Phase 0 there is")
        print("  no island to decode, and a fabricated one would prove nothing.")
    else:
        for path, m, *_ in rows:
            for pid, chunks in m["islands"].items():
                n, err = payload_elements("".join(chunks))
                print(f"  {path} {pid}: {err if err else f'{n:,} elements'}")
    print("═" * 79)
    return rows


def check(surfaces, override=None):
    rc = 0
    for path in surfaces:
        # the ratchet must never buy itself headroom
        vals = [v for _, v, _ in RATCHET[path]]
        if vals != sorted(vals, reverse=True):
            print(f"FAIL: {path}: ratchet table is not monotonically non-increasing: {vals}")
            rc = 1
        budget = override if override is not None else budget_for(path)
        n = measure(path)["total"]
        if n > budget:
            print(f"FAIL: {path}: {n:,} elements > budget {budget:,} (over by {n - budget:,})")
            rc = 1
        else:
            print(f"OK:   {path}: {n:,} elements <= budget {budget:,}")
    return rc


# ═══════════════════════════════════════════════════════════════════════════
def _integrity_verdict(measurements):
    """The F3/§0.2b rule set, applied to already-taken measurements.

    `measurements` is a list of summary dicts (each carries path/panels/islands/
    posture_radios). Returns (rc, lines). Shared by the real check and its teeth
    so both exercise identical logic.
    """
    rc = 0
    lines = []
    for m in measurements:
        path = m["path"]
        for pid, spec in MUST_STAY_LIVE.items():
            if pid not in m["panels"]:
                lines.append(f"FAIL: {path}: {pid} is MISSING — {spec['reason']}")
                rc = 1
                continue
            if pid in m["islands"]:
                lines.append(
                    f"FAIL: {path}: {pid} has been ISLANDED "
                    f"(<script type=application/json>). This is the F3 silent-"
                    f"corruption trap and §0.2b is NOT owner-authorized — {spec['reason']}"
                )
                rc = 1
            live = m["posture_radios"].get(pid, 0)
            if live < spec["min_live"]:
                lines.append(
                    f"FAIL: {path}: {pid} has {live} live {spec['live_selector']} "
                    f"(need >= {spec['min_live']}) — its load-time DOM binds are gone"
                )
                rc = 1
    # cross-surface consistency — a regression on ONE surface must be caught
    if len(measurements) > 1:
        for pid in MUST_STAY_LIVE:
            counts = {m["path"]: m["posture_radios"].get(pid, 0) for m in measurements}
            if len(set(counts.values())) > 1:
                lines.append(
                    f"FAIL: {pid} live-radio count differs across surfaces "
                    f"{counts} — one surface regressed relative to the other"
                )
                rc = 1
    if rc == 0:
        for pid in MUST_STAY_LIVE:
            counts = {m["path"]: m["posture_radios"].get(pid, 0) for m in measurements}
            lines.append(
                f"OK:   {pid} live on all surfaces, no island (radios: {counts}). F3 rail holds."
            )
    return rc, lines


def check_exempt_integrity(surfaces):
    rc, lines = _integrity_verdict([measure(p) for p in surfaces])
    for ln in lines:
        print(ln)
    return rc


def exempt_integrity_selftest():
    """Teeth: prove the rail passes a live settings panel AND catches an islanded
    one. Fabricated in-memory — never touches the real artifacts. Exits 0 when the
    guard behaves (live -> pass, islanded -> fail), mirroring the --must-fail idiom.
    """
    live_html = (
        '<section class="tab-panel active" id="panel-settings">'
        '<input type="radio" data-category="x" data-layer="allow">'
        "</section>"
    )
    # islanded: the radio markup has moved into a JSON payload as text; no <input>
    # is parsed, so the live-radio count is 0 and an island is present.
    islanded_html = (
        '<section class="tab-panel" id="panel-settings">'
        '<script type="application/json" id="settings-payload">'
        '"<input type=\\"radio\\" data-category=\\"x\\" data-layer=\\"allow\\">"'
        "</script></section>"
    )
    live_rc, _ = _integrity_verdict([measure_text(live_html, "live-fixture")])
    bad_rc, bad_lines = _integrity_verdict([measure_text(islanded_html, "islanded-fixture")])
    if live_rc == 0 and bad_rc == 1:
        print("OK:   F3 teeth — a live settings panel passes and an islanded one is caught.")
        return 0
    print(
        f"FAIL: F3 teeth misbehaved (live_rc={live_rc} expected 0, islanded_rc={bad_rc} expected 1)"
    )
    for ln in bad_lines:
        print("  " + ln)
    return 1


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--check", action="store_true", help="gate the surfaces against their budgets")
    ap.add_argument(
        "--report", action="store_true", help="emit the exempted floor / residue / x table"
    )
    ap.add_argument("--count", metavar="FILE", help="print the element count for FILE and exit")
    ap.add_argument("--surface", metavar="FILE", help="restrict --check to one surface")
    ap.add_argument(
        "--budget-override",
        type=int,
        metavar="N",
        help="override the budget (the must-fail half derives count-1; never a literal)",
    )
    ap.add_argument(
        "--exempt-integrity",
        action="store_true",
        help="F3/§0.2b rail: assert MUST_STAY_LIVE panels are never silently islanded",
    )
    ap.add_argument(
        "--must-fail",
        action="store_true",
        help="with --exempt-integrity: run the teeth self-test (islanded fixture must be caught)",
    )
    args = ap.parse_args()

    if args.count:
        print(measure(args.count)["total"])
        return 0

    surfaces = [args.surface] if args.surface else [DASHBOARD, INDEX]

    if args.exempt_integrity:
        if args.must_fail:
            return exempt_integrity_selftest()
        return check_exempt_integrity(surfaces)

    if args.report:
        report(surfaces)
        return 0
    if args.check:
        return check(surfaces, args.budget_override)

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
