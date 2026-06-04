#!/usr/bin/env python3
"""
generate-dashboards.py — emit per-plugin interactive HTML dashboards.

Sibling to generate-repo-guide.py. Per plugin with a dashboard-schema.json
present, emits plugins/<plugin>/dashboard.html — a self-contained static
page (no CDN, no external assets) with:

  - Settings tab: schema-driven form for the comfort-posture YAML
  - Commands tab: stub (v0.2.0)
  - Trees tab: stub (v0.2.0)
  - Activity tab: stub (v0.2.0)

The Settings tab implements the architect's recommendations from the
2026-05-22 dashboard-UX research (docs/research/2026-05-22-dashboard-ux/):

  - Segmented `radiogroup` per category (NOT a slider — WAI-ARIA correct)
  - Root-level `presets:` block (single source of truth; per-field
    annotation rejected per architect S1)
  - Preset bar at top with preview-diff confirmation before applying
  - Live YAML preview pane on the right
  - Copy YAML / Download .ravenclaude/comfort-posture.yaml actions
  - Theme matches scripts/generate-repo-guide.py: dark-navy base
    (#0b1120) with teal accent (#14b8a6), prefers-color-scheme honored

No external dependencies. Generates pure HTML5+CSS+vanilla-JS.

Usage:
    python3 scripts/generate-dashboards.py             # all plugins with a schema
    python3 scripts/generate-dashboards.py --plugin ravenclaude-core   # one plugin
    python3 scripts/generate-dashboards.py --check     # exit 1 if outputs are stale
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"

# Shared design tokens — single source of truth at
# plugins/ravenclaude-core/dashboard-assets/shared-tokens.css. Read at
# generate-time, inlined into the <style> block via the
# /*__SHARED_TOKENS__*/ marker substitution at the end of render_dashboard().
_SHARED_TOKENS_PATH = (
    REPO_ROOT / "plugins" / "ravenclaude-core" / "dashboard-assets" / "shared-tokens.css"
)

_RAVEN_LOGO_PATH = (
    REPO_ROOT / "plugins" / "ravenclaude-core" / "dashboard-assets" / "brand" / "raven-logo.svg"
)


def _load_raven_logo() -> str:
    """Return brand-mark MARKUP: the inline SVG if raven-logo.svg exists (drop
    the real artwork there to swap it), else an <img> of the bundled PNG.

    SVG `<!-- ... -->` comments are stripped before inlining. Here the asset
    lands in static HTML, but the sibling generate-index-dashboard.py also
    inlines it inside a JS template literal (the onboarding-card render fn) —
    a backtick or ${...} in an SVG comment would close that literal early and
    kill the entire script block. Comments never render visually; stripping
    them insulates both generators from whatever artwork lands here.
    """
    try:
        raw = _RAVEN_LOGO_PATH.read_text(encoding="utf-8")
    except OSError:
        return f'<img src="{_RAVEN_MARK_DATA_URI}" width="28" height="28" alt="" aria-hidden="true">'
    return re.sub(r"<!--.*?-->", "", raw, flags=re.DOTALL).strip()


def _load_shared_tokens_root() -> str:
    """Inline the WHOLE shared-tokens.css at generate-time.

    See `generate-index-dashboard.py:_load_shared_tokens_root` for the
    rationale — the previous extract-only-:root behavior silently dropped
    dark-mode CSS, component classes, and keyframes. Function name kept for
    template substitution marker compatibility (`/*__SHARED_TOKENS__*/`).

    Deterministic: explicit utf-8; source order preserved.
    """
    return _SHARED_TOKENS_PATH.read_text(encoding="utf-8")


def _load_emissions() -> dict[str, list[str]]:
    """Import EMISSIONS from apply-comfort-posture.py so the dashboard and the
    translator share one source of truth for which patterns belong to which
    category. Falls back to an empty mapping if the script is missing or
    fails to import — the dashboard then renders without per-pattern rows.
    """
    script_path = (
        REPO_ROOT
        / "plugins"
        / "ravenclaude-core"
        / "scripts"
        / "apply-comfort-posture.py"
    )
    if not script_path.is_file():
        return {}
    try:
        spec = importlib.util.spec_from_file_location(
            "_acp_emissions", script_path
        )
        if spec is None or spec.loader is None:
            return {}
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        emissions = getattr(mod, "EMISSIONS", {}) or {}
        return {k: list(v) for k, v in emissions.items()}
    except (ImportError, OSError, SyntaxError):
        return {}


def _load_pattern_explanations(plugin_dir: Path) -> dict[str, dict[str, str]]:
    """Load the per-pattern explanations file if present.

    Lives at plugins/<plugin>/pattern-explanations.json. Each value carries
    `what` and `why`. Returns an empty dict if the file is absent.
    """
    path = plugin_dir / "pattern-explanations.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("patterns", {}) or {}
    except (json.JSONDecodeError, OSError):
        return {}


EMISSIONS = _load_emissions()
# Pattern explanations are loaded per-plugin in render_dashboard().
PATTERN_EXPLANATIONS: dict[str, dict[str, str]] = {}

# ── Generated-output discipline (matches generate-repo-guide.py) ─────
# - byte-identical across OSes: no os.path.sep usage, no os.linesep, only \n
# - no timestamps in committed output (use sentinel "GENERATED" marker only)
# - sorted iteration: every dict iteration over plugin contents is sorted


def find_plugins_with_schema() -> list[Path]:
    """Return sorted plugin directories that have a dashboard-schema.json."""
    return sorted(
        p.parent
        for p in PLUGINS_DIR.glob("*/dashboard-schema.json")
        if p.is_file()
    )


def load_schema(plugin_dir: Path) -> dict:
    schema_path = plugin_dir / "dashboard-schema.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


def render_dashboard(plugin_dir: Path, schema: dict) -> str:
    """Compose the full dashboard.html string for one plugin."""
    global PATTERN_EXPLANATIONS
    PATTERN_EXPLANATIONS = _load_pattern_explanations(plugin_dir)

    plugin_name = plugin_dir.name
    title = schema.get("title", f"{plugin_name} dashboard")
    description = schema.get("description", "")
    presets = schema.get("presets", {})
    properties = schema.get("properties", {})

    plugins_tabs, plugins_panels = _render_plugins_category(_all_plugin_dirs())

    result = _PAGE_TEMPLATE.format(
        plugins_tabs=plugins_tabs,
        plugins_panels=plugins_panels,
        plugin_name=html.escape(plugin_name),
        title=html.escape(title),
        description=html.escape(description),
        raven_mark=_load_raven_logo(),
        css=_CSS,
        overview_html=_render_overview_tab(),
        settings_html=_render_settings_tab(properties, presets),
        install_html=_render_install_tab(),
        simulator_html=_render_simulator_tab(),
        web_access_html=_render_web_access_page(),
        learn_html=_render_learn_tab(plugin_dir),
        saga_html=_render_saga_tab(),
        commands_html=_render_commands_tab(),
        trees_html=_render_trees_tab(),
        activity_html=_render_activity_tab(),
        heimdall_html=_render_heimdall_tab(),
        vidarr_html=_render_vidarr_tab(),
        norns_html=_render_norns_tab(),
        mimir_html=_render_mimir_tab(),
        bifrost_html=_render_bifrost_tab(),
        about_html=_render_about_tab(description, plugin_name),
        pipeline_html=_render_pipeline_tab(),
        schema_json=json.dumps(schema, indent=2),
        heimdall_json=json.dumps(
            {"versionDrift": _compute_version_drift()}, indent=2, sort_keys=True
        ),
        concepts_json=_concepts_json(plugin_dir),
        pattern_explanations_json=json.dumps(
            PATTERN_EXPLANATIONS, indent=2, sort_keys=True
        ),
        js=_JS,
    )
    return result.replace("/*__SHARED_TOKENS__*/", _load_shared_tokens_root())


def _render_simulator_tab() -> str:
    """Render the 'Test a command' simulator tab.

    Answers "what would the Thing do with this command?" against the REAL engine
    via POST /__classify (served mode only). The classification is NOT
    reimplemented in JS — the tab always calls the endpoint. Availability is
    probed with HEAD /__classify, mirroring the Settings tab's HEAD /__save and
    the Install tab's HEAD /__run idioms; on a static host the button is disabled
    and a help line points the user at scripts/serve-dashboards.py.
    """
    return _SIMULATOR_TAB_TEMPLATE


def _render_stub_tab(name: str, when: str) -> str:
    return (
        f'<div class="stub">'
        f'<h2>{html.escape(name)} tab</h2>'
        f'<p>Ships in <strong>{html.escape(when)}</strong>. '
        f'See <code>docs/proposals/2026-05-22-003-per-plugin-dashboard.md</code> for the design.</p>'
        f"</div>"
    )


def _render_about_tab(description: str, plugin_name: str) -> str:
    """About & help page. Holds the full explainer that used to sit in the global
    page header (relocated so it stops crowding the top of every tab) plus a guide
    to how the pages are grouped into categories."""
    desc = html.escape(description)
    name = html.escape(plugin_name)
    return f"""
    <div class="about-wrap">
      <h2>About this dashboard</h2>
      <p class="about-lead">{desc}</p>
      <p class="about-note"><span class="plugin-name">{name}</span> &middot; static dashboard, no backend. Your edits stay in your browser until you click <strong>Download</strong>.</p>
      <h3>How the pages are organized</h3>
      <p class="about-note">Pick a category in the top bar, then a page within it.</p>
      <ul class="about-cats">
        <li><strong>Set&nbsp;up</strong> — Overview, Settings (what Claude may do), Pipeline (the safety checks every command passes through), and Preview&nbsp;a&nbsp;review.</li>
        <li><strong>Look&nbsp;back</strong> — Review&nbsp;log, Run&nbsp;feed, Perimeter&nbsp;alerts, Security&nbsp;log, and Lineage.</li>
        <li><strong>Learn</strong> — plain-English explainers, ready-to-run command playbooks, and decision-tree guidance.</li>
        <li><strong>Install&nbsp;&amp;&nbsp;help</strong> — two install &amp; update guides, one per tool: Claude&nbsp;Code (the Bifröst bridge) and GitHub&nbsp;Copilot&nbsp;CLI &mdash; plus this page.</li>
      </ul>
    </div>
    """


def _render_saga_tab() -> str:
    """Render the 'Review log' tab — a live, filterable table of Thing verdicts.

    Fetches GET /__saga on open/refresh. Falls back gracefully when the server
    is not running (static file / GitHub Pages). The fetch and render logic lives
    entirely in _JS so the generated HTML is a static skeleton.
    """
    return _SAGA_TAB_TEMPLATE


def _compute_version_drift() -> list:
    """Compute plugin-version drift: each plugin's plugin.json version vs the
    marketplace.json catalog entry. Pure committed-repo state, so this card works
    in BOTH GitHub Pages and locally-served modes. Inlined at generator time."""
    rows = []
    try:
        catalog = json.loads(
            (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        cat = {p.get("name", ""): p.get("version", "") for p in catalog.get("plugins", [])}
    except (OSError, json.JSONDecodeError, ValueError):
        return rows
    for pj in sorted((REPO_ROOT / "plugins").glob("*/.claude-plugin/plugin.json")):
        try:
            d = json.loads(pj.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        name = d.get("name", "")
        plugin_ver = d.get("version", "")
        catalog_ver = cat.get(name, "")
        rows.append(
            {
                "plugin": name,
                "marketplace_version": catalog_ver,
                "plugin_version": plugin_ver,
                "drift": plugin_ver != catalog_ver,
            }
        )
    return rows


def _render_heimdall_tab() -> str:
    """Render the 'Heimdall' tab — a read-only perimeter-alarm surface.

    Four cards: recent hook denials (fetched from /__heimdall, served-only),
    recent CI runs (fetched client-side from the GitHub API), plugin version
    drift (inlined from committed manifests, works on a static host too), and the
    Gjallarhorn banner (derived from the hook-event tiers). Heimdall WRITES
    nothing — it mirrors what the hooks/manifests already emit. The fetch/render
    logic lives in _JS; this returns a static skeleton the JS hydrates on open.
    """
    return _HEIMDALL_TAB_TEMPLATE


def _render_mimir_tab() -> str:
    """Render the 'Session' (Mímir's well) tab — a read-only surface that
    answers "what does Claude Code know about *this* session?" by surfacing
    the on-disk state under ~/.claude/ + <project>/.claude/.

    Five card hosts hydrated by JS from /__mimir on open: settings (theme +
    configured/last-used model + permission mode), live session (matched by
    cwd + status=busy), activity (stats-cache.json with mandatory `as of`
    pill), recent project sessions (top 5 mtime-desc), and the honest
    unreachable-fields list. Served-only — on a static host the cards show
    an "open the served dashboard" empty state; in-process-only fields
    (/effort, /status) render with an explanatory pill, never a dash.

    See plugins/ravenclaude-core/skills/mimir/SKILL.md for the reachability
    contract; the JS fetch + render live in _JS (loadMimir / renderMimir*).
    The static skeleton is intentionally bytes-free of any dynamic content
    so the dashboard.html freshness gate (Gate 13) stays exact-match.
    """
    return _MIMIR_TAB_TEMPLATE


def _render_vidarr_tab() -> str:
    """Render the 'Security log' (Víðarr) tab — a read-only, filterable,
    chronological log of posture changes + security-relevant hook denials.

    Data is fetched from /__vidarr (served-only — posture-events.jsonl and the
    consumer's hook-events.jsonl are git-ignored, per-consumer, so a generator
    run in the marketplace cannot see them). On a static host the tab degrades to
    an honest empty state. The fetch/render/filter logic lives in _JS; this
    returns a static skeleton the JS hydrates on open.
    """
    return _VIDARR_TAB_TEMPLATE


def _render_norns_tab() -> str:
    """Render the 'Lineage' (Norns) tab — a read-only three-column past/present/
    future view (Urðr / Verðandi / Skuld) for the core plugin.

    Data is fetched from /__norns (served-only — it reads live git log + scenario
    events.jsonl, which vary by clone depth and so must NOT be inlined at
    generator time or they would break the exact-match dashboard freshness gate).
    On a static host the tab degrades to an honest empty state. The fetch/render
    logic lives in _JS; this returns a static skeleton the JS hydrates on open.
    """
    return _NORNS_TAB_TEMPLATE


def _render_bifrost_tab() -> str:
    """Render the 'Install a plugin (Bifröst)' tab — a guided 4-step copy-paste
    wizard for installing a marketplace plugin into a Claude Code project (§3.6).

    Fully client-side and static: the wizard NEVER executes a slash command — the
    user runs each in their own session and pastes the output back; the JS only
    parses that output (per-step success/failure regex) to advance the bridge and
    auto-expand the matching failure-mode accordion. No server endpoint, no fetch.
    Distinct from the 'Install & Update' tab (which wires RavenClaude into Copilot
    CLI). The verify/copy/accordion logic lives in _JS.
    """
    return _BIFROST_TAB_TEMPLATE


def _render_activity_tab() -> str:
    """Render the 'Activity' tab — a newest-first feed of multi-step runs.

    Generalizes the Review-log (Saga) tab from tribunal verdicts to ALL run
    artifacts under `.ravenclaude/runs/<id>/` (summary.md, structured-result
    status, events count). Fetches GET /__runs on open/refresh; degrades
    gracefully on a static host (file:// / GitHub Pages) exactly like Saga. The
    fetch + render logic lives in _JS so the generated HTML is a static skeleton;
    it reuses the Saga tab's CSS (.saga-empty/.saga-refresh/.saga-count) plus a
    small .activity-* card block.
    """
    return _ACTIVITY_TAB_TEMPLATE


# ── Pipeline tab ─────────────────────────────────────────────────────────────
# A visual map of EVERY guardrail an agent passes through (SessionStart →
# PreToolUse → PostToolUse → Stop), grounded in hooks/hooks.json. Each stage
# carries a live ON/OFF badge, a 5th-grade tooltip, and (where tunable) inline
# editors. Posture-backed knobs round-trip the SAME comfort-posture.yaml the
# Settings tab uses (shared `state` + emitYaml + /__save). The two file-backed
# stages (.repo-layout.json, .ravenclaude/task-scope.json) round-trip via
# /__read + /__save with server-side JSON validation. All JS lives in _JS; this
# returns a static skeleton the JS hydrates on tab open.
_PIPELINE_LANES = [
    {
        "event": "SessionStart",
        "when": "When a session starts",
        "tip": "Right when the robot wakes up, it loads your settings and reminds itself what it's allowed to do.",
        "stages": [
            {"id": "reapply-posture", "title": "Re-apply settings", "badge": "always",
             "tip": "Loads your saved safety settings so they're on from the very first step.",
             "detail": {
                 "steps": ["Reads your saved settings file (.ravenclaude/comfort-posture.yaml).",
                           "Turns each rule into a real Claude Code permission.",
                           "Writes them into .claude/settings.json so they're active right away."],
                 "trip": "If there's no settings file, it does nothing — no harm done.",
                 "set": "Change these in the Settings tab; the Save button writes the file."}},
            {"id": "ensure-default-mode", "title": "Safe starting mode", "badge": "always",
             "tip": "Picks a safe mode to start the session in.",
             "detail": {
                 "steps": ["Checks what mode the session is starting in.",
                           "If nothing was chosen, picks a safe default."],
                 "trip": "Only steps in when no mode was set — otherwise it leaves your choice alone.",
                 "set": "Built in — nothing to tune."}},
            {"id": "capability-orientation", "title": "Capability check", "badge": "always",
             "tip": "Reminds the robot what tools and access it already has, so it doesn't say “I can't” by mistake.",
             "detail": {
                 "steps": ["Looks at what tools, logins, and permissions are available.",
                           "Writes a short summary into the session so the robot knows what it can do.",
                           "Adds a line about recent guardrail activity (how many things were blocked, when settings last changed)."],
                 "trip": "Read-only — it never changes anything, it only informs.",
                 "set": "Built in."}},
        ],
    },
    {
        "event": "PreToolUse",
        "when": "Before the robot runs a command or edits a file",
        "tip": "This is the busiest checkpoint. Every command and every file edit goes through these in order before it's allowed to happen.",
        "stages": [
            {"id": "guard-destructive", "title": "Danger guard", "badge": "always",
             "tip": "Stops really dangerous commands (like deleting everything) before they can run.",
             "detail": {
                 "steps": ["Looks at the command about to run.",
                           "Matches it against a list of never-allowed patterns (delete everything, force-push, wipe history).",
                           "Blocks it before it can run if it matches."],
                 "trip": "Blocks the command and writes a note in the alert log (Perimeter alerts tab).",
                 "set": "Built-in safety floor — always on, can't be turned off."}},
            {"id": "thing", "title": "Command review (the Thing)", "badge": "dynamic", "controls": "thing",
             "tip": "A panel of robot reviewers votes yes / no / fix on a command before it runs. You choose how strict it is.",
             "detail": {
                 "steps": ["Runs quick free checks first, so the obvious-dangerous ones are caught with no waiting.",
                           "If the command is risky enough, a panel of reviewers reads it.",
                           "They vote: allow, fix (rewrite it to be safe), or block.",
                           "Low-risk reads skip the panel completely — no waiting."],
                 "trip": "A block stops the command; a fix rewrites it; anything safe just runs.",
                 "set": "Turn it on (and on/off per command type) and tune the panel in Settings — quick toggles below."}},
            {"id": "runaway-brake", "title": "Runaway brake", "badge": "dynamic", "controls": "runaway",
             "tip": "Counts the robot's steps. If it loops forever or takes way too many steps, it pauses so it can't run away.",
             "detail": {
                 "steps": ["Counts every tool the robot uses this session.",
                           "Watches for the same command repeated over and over.",
                           "Pauses if it loops, or if it passes your step limit."],
                 "trip": "Pauses the robot so it can't run away with your time or money.",
                 "set": "Turn the brake off, or set the two limits, in the boxes below."}},
            {"id": "enforce-layout", "title": "Folder & task limits", "badge": "dynamic", "controls": "files",
             "tip": "Makes sure new files go in the right folders, and that the robot only touches the files this task is allowed to.",
             "detail": {
                 "steps": ["Checks where a new file is about to be written.",
                           "Compares it to your allowed-folders list (.repo-layout.json).",
                           "If a task-file list is set, checks the file is part of this task (.ravenclaude/task-scope.json)."],
                 "trip": "Blocks the write and suggests the correct folder.",
                 "set": "Edit the two file lists in the boxes below."}},
            {"id": "route-decision-review", "title": "Decision routing", "badge": "dynamic", "controls": "decision",
             "tip": "When the robot would ask you a yes/no question, a panel answers the easy ones so you're not interrupted.",
             "detail": {
                 "steps": ["Notices when the robot is about to ask you a yes/no question.",
                           "Sends the simple, low-risk ones to a small panel.",
                           "Big or risky questions always come to you."],
                 "trip": "In binding mode the panel answers the easy ones; risky ones still reach you.",
                 "set": "Pick off / advisory / binding in the box below."}},
        ],
    },
    {
        "event": "PostToolUse",
        "when": "Right after a command runs or a file is saved",
        "tip": "After something happens, these tidy up and double-check the work.",
        "stages": [
            {"id": "format-on-write", "title": "Auto-tidy", "badge": "always",
             "tip": "Tidies up a file's formatting right after it's saved.",
             "detail": {
                 "steps": ["Runs right after a file is saved.",
                           "Runs the formatter for that kind of file.",
                           "Saves the tidied version."],
                 "trip": "Skips files it doesn't have a formatter for — never blocks.",
                 "set": "Built in."}},
            {"id": "guard-recursive-spawn", "title": "Copy guard", "badge": "always",
             "tip": "Stops the robot from making endless copies of itself.",
             "detail": {
                 "steps": ["Watches for the robot launching copies of itself.",
                           "Warns if those copies nest too deep."],
                 "trip": "Warns (it doesn't hard-block) so you can step in.",
                 "set": "Built in."}},
            {"id": "claim-grounding-lint", "title": "Fact check", "badge": "advisory",
             "tip": "Reminds the robot to say where a fact came from when it writes one into a document.",
             "detail": {
                 "steps": ["Reads facts written into knowledge / docs files.",
                           "Checks each big claim says where it came from.",
                           "Nudges if a source is missing."],
                 "trip": "Advisory only — it nudges, it never blocks.",
                 "set": "Active once command review is turned on."}},
        ],
    },
    {
        "event": "Stop",
        "when": "When the robot thinks it's done",
        "tip": "Before the robot is allowed to stop, it proves the work is really finished.",
        "stages": [
            {"id": "dod-gate", "title": "Done check", "badge": "dynamic", "controls": "dod",
             "tip": "Before the robot says “done,” it runs your tests. If they fail, it keeps working.",
             "detail": {
                 "steps": ["Fires when the robot tries to stop.",
                           "Runs your test / build command.",
                           "If it fails, the robot keeps working instead of stopping."],
                 "trip": "Blocks the stop until tests pass (up to a retry limit, then it lets the robot stop with a warning).",
                 "set": "Set your test command and the retry limit in the boxes below."}},
            {"id": "remind-tests", "title": "Test reminder", "badge": "advisory",
             "tip": "A gentle nudge to run the tests when there's no done-check set up.",
             "detail": {
                 "steps": ["Fires on stop when no done-check is set.",
                           "Prints a friendly reminder to run the tests."],
                 "trip": "Advisory only — just a nudge.",
                 "set": "Becomes unnecessary once you set a done-check above."}},
        ],
    },
]

_PIPELINE_CONTROLS = {
    "thing": (
        '<label class="pipe-ctl"><input type="checkbox" id="pipe-thing-enabled"> '
        "Command review is on</label>"
        '<label class="pipe-ctl"><input type="checkbox" id="pipe-dev-exempt"> '
        "Dev-repo exemption (maintainer only — lets an over-slow panel ask instead of blocking)</label>"
        '<label class="pipe-ctl">Ask me when risk is at or above '
        '<select id="pipe-gate-floor"><option value="medium">medium</option>'
        '<option value="high">high</option><option value="extreme">extreme</option></select></label>'
        '<p class="pipe-hint">Turn individual command types on/off, and tune the reviewer panel, in the '
        '<a href="#/settings">Settings</a> tab.</p>'
    ),
    "runaway": (
        '<label class="pipe-ctl"><input type="checkbox" id="pipe-runaway-off"> Turn the brake off</label>'
        '<label class="pipe-ctl">Most steps in one session '
        '<input type="number" id="pipe-runaway-total" min="1" step="1"></label>'
        '<label class="pipe-ctl">Most identical tries in a row '
        '<input type="number" id="pipe-runaway-consec" min="1" step="1"></label>'
    ),
    "decision": (
        '<label class="pipe-ctl">Mode '
        '<select id="pipe-decision-review">'
        '<option value="off">off — you answer every yes/no</option>'
        '<option value="advisory">advisory — panel suggests, you still answer</option>'
        '<option value="binding">binding — panel answers the easy ones</option>'
        "</select></label>"
    ),
    "dod": (
        '<label class="pipe-ctl">Test / build command '
        '<input type="text" id="pipe-dod-cmd" placeholder="npm test &amp;&amp; npm run lint"></label>'
        '<label class="pipe-ctl">Times it may re-try before giving up '
        '<input type="number" id="pipe-dod-maxblocks" min="1" step="1"></label>'
        '<p class="pipe-hint">Leave the command empty to turn the done-check off.</p>'
    ),
    "files": (
        '<div class="pipe-file" data-file=".repo-layout.json">'
        '<div class="pipe-file-head"><strong>Allowed folders</strong> '
        '<code>.repo-layout.json</code>'
        '<button type="button" class="pipe-file-load" data-target=".repo-layout.json">Load</button>'
        '<button type="button" class="pipe-file-save" data-target=".repo-layout.json">Save</button></div>'
        '<textarea class="pipe-file-text" data-target=".repo-layout.json" spellcheck="false" '
        'aria-label="repo-layout.json contents"></textarea>'
        '<span class="pipe-file-status" data-target=".repo-layout.json"></span></div>'
        '<div class="pipe-file" data-file=".ravenclaude/task-scope.json">'
        '<div class="pipe-file-head"><strong>This task’s files</strong> '
        '<code>.ravenclaude/task-scope.json</code>'
        '<button type="button" class="pipe-file-load" data-target=".ravenclaude/task-scope.json">Load</button>'
        '<button type="button" class="pipe-file-save" data-target=".ravenclaude/task-scope.json">Save</button></div>'
        '<textarea class="pipe-file-text" data-target=".ravenclaude/task-scope.json" spellcheck="false" '
        'aria-label="task-scope.json contents" '
        'placeholder=\'{ "in_scope": ["src/**"], "spec": "SPEC.md" }\'></textarea>'
        '<span class="pipe-file-status" data-target=".ravenclaude/task-scope.json"></span></div>'
    ),
}


_PIPELINE_CSS = """<style>
.pipeline-tab { max-width: 920px; }
.pipe-note { margin: .5rem 0 1rem; padding: .6rem .8rem; border-radius: var(--rc-radius-sm);
  background: var(--surface-2); border: 1px solid var(--border);
  color: var(--muted); font-size: .9rem; }
/* Flow strip — the at-a-glance order an agent moves through. */
.pipe-flow { display: flex; flex-wrap: wrap; align-items: center; gap: .4rem .5rem;
  margin: .6rem 0; padding: .7rem .8rem; border: 1px solid var(--border);
  border-radius: var(--rc-radius-lg); background: var(--surface); box-shadow: var(--rc-shadow-sm); }
.pipe-flow-step { font-size: .82rem; font-weight: 600; color: var(--text);
  background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--rc-radius-pill);
  padding: .2rem .7rem; white-space: nowrap; }
.pipe-flow-step.pipe-flow-loop { border-color: var(--accent); }
.pipe-flow-arr { color: var(--accent); font-weight: 700; }
.pipe-readme { font-size: .86rem; }
.pipe-lane { border: 1px solid var(--border); border-radius: var(--rc-radius-lg);
  padding: .85rem 1rem; margin: 0; background: var(--surface); box-shadow: var(--rc-shadow-sm); }
.pipe-lane-head { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; }
.pipe-lane-when { font-weight: 600; color: var(--text, #eee); }
.pipe-lane-event { font-family: ui-monospace, monospace; font-size: .78rem;
  color: var(--muted, #999); background: var(--bg, #111); padding: .1rem .4rem;
  border-radius: 4px; }
.pipe-lane-tip { margin: .3rem 0 .7rem; color: var(--muted, #aaa); font-size: .88rem; }
.pipe-row { display: flex; flex-wrap: wrap; gap: .6rem; }
.pipe-stage { flex: 1 1 240px; min-width: 210px; border: 1px solid var(--border);
  border-radius: var(--rc-radius); padding: .6rem .7rem; background: var(--surface-2); }
.pipe-stage-head { display: flex; align-items: center; justify-content: space-between; gap: .5rem; }
.pipe-stage-title { font-weight: 600; font-size: .92rem; }
.pipe-tip { margin: .35rem 0 0; font-size: .82rem; color: var(--muted, #aaa); line-height: 1.35; }
.pipe-badge { font-size: .7rem; font-weight: 600; padding: .12rem .42rem; border-radius: 10px;
  white-space: nowrap; }
.pipe-badge-on { background: var(--rc-ok-bg); color: var(--rc-ok-fg); }
.pipe-badge-off { background: var(--rc-danger-bg); color: var(--rc-danger-fg); }
.pipe-badge-advisory { background: var(--rc-neutral-bg); color: var(--rc-neutral-fg); }
.pipe-badge-dynamic { background: var(--rc-neutral-bg); color: var(--rc-neutral-fg); }
.pipe-controls { margin-top: .55rem; display: flex; flex-direction: column; gap: .4rem; }
.pipe-ctl { display: flex; align-items: center; gap: .4rem; flex-wrap: wrap; font-size: .84rem; }
.pipe-ctl input[type=number] { width: 6rem; }
.pipe-ctl input[type=text] { flex: 1 1 12rem; min-width: 10rem; }
.pipe-hint { margin: .1rem 0 0; font-size: .78rem; color: var(--muted, #888); }
/* Expandable "How it works" subprocess detail (native <details>, accessible). */
.pipe-more { margin: .4rem 0 0; }
.pipe-more > summary { cursor: pointer; font-size: .8rem; font-weight: 600; color: var(--accent);
  list-style: none; display: inline-flex; align-items: center; gap: .3rem; user-select: none; }
.pipe-more > summary::-webkit-details-marker { display: none; }
.pipe-more > summary::before { content: "▸"; font-size: .7rem; transition: transform .15s ease; }
.pipe-more[open] > summary::before { transform: rotate(90deg); }
.pipe-steps { margin: .4rem 0 .3rem; padding-left: 1.15rem; font-size: .82rem; color: var(--muted);
  line-height: 1.4; display: flex; flex-direction: column; gap: .2rem; }
.pipe-more-line { margin: .25rem 0 0; font-size: .8rem; color: var(--muted); line-height: 1.4; }
.pipe-more-lbl { font-weight: 700; color: var(--text); }
.pipe-arrow { text-align: center; font-size: 1.2rem; color: var(--accent); margin: .15rem 0; }
.pipe-file { margin-top: .5rem; }
.pipe-file-head { display: flex; align-items: center; gap: .4rem; flex-wrap: wrap; font-size: .82rem; }
.pipe-file-text { width: 100%; min-height: 6rem; font-family: ui-monospace, monospace;
  font-size: .78rem; margin-top: .3rem; box-sizing: border-box; }
.pipe-file-status { font-size: .78rem; color: var(--muted, #999); }
.pipe-savebar { display: flex; align-items: center; gap: .8rem; margin: 1.2rem 0 .5rem;
  position: sticky; bottom: 0; padding: .6rem 0; background: linear-gradient(transparent, var(--bg, #111) 40%); }
.pipe-save-status { font-size: .85rem; color: var(--muted, #aaa); }
.concern-stats { margin-top: 1.8rem; padding: 1rem 1.1rem; border: 1px solid var(--border, #2a2a2a);
  border-radius: 8px; background: var(--surface, #161616); }
.concern-stats h3 { margin: 0 0 .4rem; font-size: 15px; }
.concern-stats-state { font-size: 12.5px; color: var(--muted, #999); padding: .6rem 0; }
.concern-stats-table { width: 100%; border-collapse: collapse; margin-top: .4rem; font-size: 12.5px; }
.concern-stats-table th, .concern-stats-table td {
  text-align: left; padding: .35rem .5rem; border-bottom: 1px solid var(--border, #2a2a2a);
}
.concern-stats-table th { color: var(--muted, #999); font-weight: 600; font-size: 11.5px;
  text-transform: uppercase; letter-spacing: .03em; }
.concern-stats-table td.num, .concern-stats-table th.num { text-align: right; font-variant-numeric: tabular-nums; }
.concern-stats-table tr.concern-row-hot td { color: var(--warn, #fbbf24); }
.concern-stats-table tr.concern-row-cold td { color: var(--text, #ddd); }
.concern-stats-table code { font-family: ui-monospace, monospace; font-size: 12px; }
</style>"""


def _render_pipeline_tab() -> str:
    """Render the Pipeline tab — the all-events guardrail flow with live state,
    5th-grade tooltips, and inline editors. JS (in _JS) hydrates it on open."""
    lanes_html = []
    for lane in _PIPELINE_LANES:
        cards = []
        for st in lane["stages"]:
            badge = st["badge"]
            if badge == "always":
                badge_html = '<span class="pipe-badge pipe-badge-on">Always on</span>'
            elif badge == "advisory":
                badge_html = '<span class="pipe-badge pipe-badge-advisory">Advisory</span>'
            else:  # dynamic — JS fills it
                badge_html = (
                    f'<span class="pipe-badge pipe-badge-dynamic" '
                    f'data-pipe-badge="{html.escape(st["id"])}">…</span>'
                )
            controls = st.get("controls")
            controls_html = (
                f'<div class="pipe-controls">{_PIPELINE_CONTROLS[controls]}</div>'
                if controls else ""
            )
            detail = st.get("detail")
            detail_html = ""
            if detail:
                steps = "".join(f"<li>{html.escape(s)}</li>" for s in detail.get("steps", []))
                detail_html = (
                    '<details class="pipe-more"><summary>How it works, step by step</summary>'
                    f'<ol class="pipe-steps">{steps}</ol>'
                    f'<p class="pipe-more-line"><span class="pipe-more-lbl">If it trips:</span> '
                    f'{html.escape(detail.get("trip", ""))}</p>'
                    f'<p class="pipe-more-line"><span class="pipe-more-lbl">Where it’s set:</span> '
                    f'{html.escape(detail.get("set", ""))}</p>'
                    "</details>"
                )
            cards.append(
                f'<div class="pipe-stage" data-stage="{html.escape(st["id"])}">'
                f'<div class="pipe-stage-head">'
                f'<span class="pipe-stage-title">{html.escape(st["title"])}</span>'
                f"{badge_html}</div>"
                f'<p class="pipe-tip">{html.escape(st["tip"])}</p>'
                f"{detail_html}"
                f"{controls_html}</div>"
            )
        arrow = '<div class="pipe-arrow" aria-hidden="true">↓</div>'
        lanes_html.append(
            '<section class="pipe-lane">'
            '<div class="pipe-lane-head">'
            f'<span class="pipe-lane-when">{html.escape(lane["when"])}</span>'
            f'<span class="pipe-lane-event">{html.escape(lane["event"])}</span></div>'
            f'<p class="pipe-lane-tip">{html.escape(lane["tip"])}</p>'
            f'<div class="pipe-row">{"".join(cards)}</div>'
            "</section>"
        )
    body = arrow.join(lanes_html)
    return f"""{_PIPELINE_CSS}
<div class="pipeline-tab">
  <h2>Guardrail pipeline</h2>
  <p class="page-desc">Everything an AI agent passes through, top to bottom. Each box shows whether it's on right now, what it does (in plain words), the step-by-step of how it works, and the knobs you can turn. Changes save to your <code>.ravenclaude/comfort-posture.yaml</code>.</p>
  <div class="pipe-flow" role="img" aria-label="Flow: session starts, then before-each-step and after-each-step checkpoints loop for every command, then a final check when it tries to stop.">
    <span class="pipe-flow-step">Session starts</span>
    <span class="pipe-flow-arr">→</span>
    <span class="pipe-flow-step pipe-flow-loop">Before each step</span>
    <span class="pipe-flow-arr">→</span>
    <span class="pipe-flow-step">the tool runs</span>
    <span class="pipe-flow-arr">→</span>
    <span class="pipe-flow-step pipe-flow-loop">After each step</span>
    <span class="pipe-flow-arr" title="repeats for every command or edit">↺</span>
    <span class="pipe-flow-arr">→</span>
    <span class="pipe-flow-step">When it tries to stop</span>
  </div>
  <p class="page-desc pipe-readme">The two middle checkpoints repeat for <em>every</em> command and file edit — that's the ↺ loop. Open <strong>“How it works, step by step”</strong> on any box to see exactly what it checks and what happens if it trips. Badges: <span class="pipe-badge pipe-badge-on">Always on</span> can't be turned off · <span class="pipe-badge pipe-badge-advisory">Advisory</span> only nudges, never blocks · <span class="pipe-badge pipe-badge-dynamic">On / Off</span> depends on your settings (filled in live below).</p>
  <div id="pipeline-server-note" class="pipe-note" hidden>This page has no server behind it, so the live state and editors are read-only. Launch the dashboard with <code>ravenclaude dashboard --project &lt;repo&gt;</code> to edit and apply.</div>
  {body}
  <div class="pipe-savebar">
    <button type="button" id="pipeline-save-btn" class="btn-primary">Save &amp; apply</button>
    <span id="pipeline-save-status" class="pipe-save-status"></span>
  </div>

  <section class="concern-stats" id="concern-stats-card" aria-labelledby="concern-stats-h">
    <h3 id="concern-stats-h">Concern reliability</h3>
    <p class="page-desc">
      Per-concern false-positive signals from the command-review S&aacute;ga log. <strong>Stripped</strong> means the orchestrator deterministically caught a cite the seat shouldn&rsquo;t have made (e.g. <code>xc.outside-project-tree</code> on a file the path-classifier already proved is in-tree). <strong>Heimdall-disagreed</strong> means another seat cited the concern and voted deny while Heimdall (injection-only) voted allow &mdash; a behavioural false-positive signal. A high <strong>FP ratio</strong> is the queue of concerns worth tuning. Read live from <code>.ravenclaude/runs/thing/</code> via <code>/__concern-stats</code>; static hosts show an empty state.
    </p>
    <div id="concern-stats-state" class="concern-stats-state" role="status">Loading&hellip;</div>
    <table id="concern-stats-table" class="concern-stats-table" hidden>
      <thead>
        <tr>
          <th scope="col">Concern</th>
          <th scope="col" class="num">Cited</th>
          <th scope="col" class="num">Stripped</th>
          <th scope="col" class="num">Heimdall&nbsp;≠</th>
          <th scope="col" class="num">Final&nbsp;deny</th>
          <th scope="col" class="num">FP ratio</th>
        </tr>
      </thead>
      <tbody id="concern-stats-tbody"></tbody>
    </table>
  </section>
</div>"""


# ── Learn tab ──────────────────────────────────────────────────────────────
# Built from the generated concept registry (scripts/concepts.py) + the
# pre-rendered, theme-normalized SVGs (scripts/render-concepts.py). The dashboard
# inlines both at build time so the tab is fully offline. See concepts.py.

import re as _re

_MD_LINK_RE = _re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+|[^\s):]+)\)")
_MD_CODE_RE = _re.compile(r"`([^`]+)`")
_MD_BOLD_RE = _re.compile(r"\*\*([^*]+)\*\*")
_MD_ITALIC_RE = _re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")


def _md_to_html(text: str) -> str:
    """Minimal, safe markdown→HTML for concept bodies: paragraphs, **bold**,
    *italic*, `code`, and [label](url) (http(s) or relative only — `:` is
    excluded from bare paths so `javascript:` can't slip through). HTML is
    escaped first, so no raw markup from the source survives."""
    out = []
    for para in _re.split(r"\n\s*\n", text.strip()):
        s = html.escape(para)
        s = _MD_LINK_RE.sub(
            lambda m: f'<a href="{m.group(2)}" rel="noopener">{m.group(1)}</a>', s
        )
        s = _MD_CODE_RE.sub(r"<code>\1</code>", s)
        s = _MD_BOLD_RE.sub(r"<strong>\1</strong>", s)
        s = _MD_ITALIC_RE.sub(r"<em>\1</em>", s)
        out.append("<p>" + s.replace("\n", " ") + "</p>")
    return "".join(out)


_CONCEPT_ICONS = {
    # color + SHAPE dual channel (passes the color-blind / squint test)
    "platform-fact": (
        "Platform fact",
        '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">'
        '<circle cx="8" cy="8" r="5" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
    ),
    "ravenclaude-built": (
        "RavenClaude-built",
        '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">'
        '<path d="M8 1.5 14.5 8 8 14.5 1.5 8Z" fill="currentColor"/></svg>',
    ),
}


def _inline_concept_svg(plugin_dir: Path, rel: str | None) -> str:
    if not rel:
        return ""
    p = plugin_dir / rel
    return p.read_text(encoding="utf-8").strip() if p.is_file() else ""


# Named interactive widgets a concept can embed via its `widget:` frontmatter.
# Markup only — the behavior is wired in _JS (initConceptWidgets). Pure
# client-side: no endpoint, so it works identically offline and served.
_PERMISSION_RESOLVER_ROWS = [
    ("managed", "Managed (enterprise)"),
    ("project", "Project · .claude/settings.json"),
    ("local", "Local · .claude/settings.local.json"),
    ("user", "User · ~/.claude/settings.json"),
]
_CONCEPT_WIDGETS = {
    "permission-resolver": (
        '<div class="concept-widget" data-widget="permission-resolver">'
        '<div class="cw-title">Try it: which layer wins?</div>'
        '<p class="cw-hint">Set a rule in each layer and watch the cross-layer merge decide. '
        "A deny in any layer always wins; you can't override it down.</p>"
        '<div class="cw-rows">'
        + "".join(
            f'<label class="cw-row"><span class="cw-layer">{html.escape(name)}</span>'
            f'<select class="cw-select" data-layer="{key}" aria-label="{html.escape(name)} rule">'
            '<option value="inherit">— none —</option>'
            '<option value="allow">allow</option>'
            '<option value="ask">ask</option>'
            '<option value="deny">deny</option>'
            "</select></label>"
            for key, name in _PERMISSION_RESOLVER_ROWS
        )
        + "</div>"
        '<div class="cw-result"><span class="cw-verdict" data-verdict>—</span>'
        '<span class="cw-why" data-why></span></div>'
        "</div>"
    ),
}


def _try_it_html(try_it: dict | None) -> str:
    if not try_it:
        return ""
    return (
        f'<a class="concept-tryit" href="{html.escape(try_it["href"])}">'
        f'{html.escape(try_it["label"])} <span aria-hidden="true">&rarr;</span></a>'
    )


def _render_concept_card(plugin_dir: Path, c: dict, titles: dict[str, str]) -> str:
    kind = c["kind"]
    badge_label, badge_icon = _CONCEPT_ICONS.get(kind, ("", ""))
    badge_cls = "fact" if kind == "platform-fact" else "built"

    svg = _inline_concept_svg(plugin_dir, c.get("svg"))
    well = (
        f'<div class="concept-diagram-well" role="img" '
        f'aria-label="{html.escape(c["title"])} diagram">{svg}</div>'
        if svg
        else ""
    )

    see_also = "".join(
        f'<a class="concept-chip" href="#/learn/{html.escape(ref)}">'
        f'{html.escape(titles.get(ref, ref))}</a>'
        for ref in c.get("see_also", [])
        if ref in titles
    )
    see_also_block = f'<div class="concept-seealso">{see_also}</div>' if see_also else ""

    sources = "".join(
        f'<a class="concept-source" href="{html.escape(s["url"])}" rel="noopener">'
        f'{html.escape(s["label"])}</a>'
        for s in c.get("sources", [])
    )
    verified = ""
    if c.get("last_verified"):
        verified = f'<span class="concept-verified">verified {html.escape(c["last_verified"])}</span>'

    search_blob = html.escape(
        f"{c['title']} {c['summary']} {c['body_md']}".lower(), quote=True
    )

    return (
        f'<article class="concept-card" id="learn-{html.escape(c["id"])}" '
        f'data-concept="{html.escape(c["id"])}" data-search="{search_blob}" tabindex="-1">'
        f'<div class="concept-eyebrow">{html.escape(c["category"])}</div>'
        f'<div class="concept-head">'
        f'<h3 class="concept-title">{html.escape(c["title"])}</h3>'
        f'<span class="concept-badge {badge_cls}">{badge_icon}{html.escape(badge_label)}</span>'
        f"</div>"
        f'<p class="concept-deck">{html.escape(c["summary"])}</p>'
        f"{well}"
        f'<div class="concept-body">{_md_to_html(c["body_md"])}</div>'
        f'{_CONCEPT_WIDGETS.get(c.get("widget") or "", "")}'
        f'{_try_it_html(c.get("try_it"))}'
        f"{see_also_block}"
        f'<div class="concept-sources-row">{sources}{verified}</div>'
        f"</article>"
    )


def _render_learn_tab(plugin_dir: Path) -> str:
    reg_path = plugin_dir / "concepts.json"
    if not reg_path.is_file():
        return _render_stub_tab("Learn", "next")
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    concepts = reg.get("concepts", [])
    if not concepts:
        return _render_stub_tab("Learn", "next")

    titles = {c["id"]: c["title"] for c in concepts}
    groups: dict[str, list[dict]] = {}
    order: list[str] = []
    for c in concepts:
        if c["category"] not in groups:
            groups[c["category"]] = []
            order.append(c["category"])
        groups[c["category"]].append(c)

    cats_html = []
    for cat in order:
        cards = "".join(_render_concept_card(plugin_dir, c, titles) for c in groups[cat])
        cats_html.append(
            f'<details class="concept-cat" open>'
            f'<summary class="concept-cat-head">'
            f'<span class="concept-cat-name">{html.escape(cat)}</span>'
            f'<span class="concept-cat-count">{len(groups[cat])}</span></summary>'
            f'<div class="concept-grid">{cards}</div></details>'
        )

    return (
        '<div class="learn-tab">'
        '<div class="learn-toolbar">'
        '<input type="search" id="learn-search" class="learn-search" '
        'placeholder="Search concepts…" aria-label="Search concepts" '
        'autocomplete="off" spellcheck="false">'
        f'<span class="learn-count" id="learn-count">{len(concepts)} concepts</span>'
        '<span class="learn-toolbar-spacer"></span>'
        '<button type="button" class="learn-linkbtn" id="learn-expand">Expand all</button>'
        '<button type="button" class="learn-linkbtn" id="learn-collapse">Collapse all</button>'
        "</div>"
        '<div class="learn-legend" aria-hidden="true">'
        '<span class="learn-legend-item"><span class="learn-swatch fact"></span>Platform fact</span>'
        '<span class="learn-legend-item"><span class="learn-swatch built"></span>RavenClaude-built</span>'
        "</div>"
        + "".join(cats_html)
        + '<div class="stub learn-noresults" id="learn-noresults" hidden>'
        '<h2>No matching concepts</h2><p>Try a different search term.</p></div>'
        + "</div>"
    )


def _concepts_json(plugin_dir: Path) -> str:
    """The concept registry, embedded verbatim for the Learn tab's search/tooltip
    JS. Empty object until scripts/concepts.py has generated it."""
    reg_path = plugin_dir / "concepts.json"
    return reg_path.read_text(encoding="utf-8").strip() if reg_path.is_file() else "{}"


# Copy-to-clipboard command blocks for the Install & Update tab. Each is a
# fixed, non-interpolated command — they work on ANY host (GitHub Pages, file://,
# served), since they only feed the clipboard. The one-click buttons below them
# (served mode only) POST to /__run instead.
_INSTALL_COMMANDS = [
    (
        "setup",
        "Set up (one-shot: install + balanced posture + rc alias)",
        "bash scripts/ravenclaude setup",
    ),
    (
        "install",
        "Install (one-time wiring only)",
        "bash scripts/ravenclaude install",
    ),
    (
        "launch",
        "Launch Copilot with the plugin",
        "copilot --plugin-dir plugins/ravenclaude-core/copilot",
    ),
    (
        "update",
        "Update (git pull + re-sync, then /skills reload in Copilot)",
        "bash scripts/ravenclaude update",
    ),
    (
        "status",
        "Status (show what is wired)",
        "bash scripts/ravenclaude status",
    ),
    (
        "alias",
        "One-command alias (update, then launch)",
        "alias rc='bash scripts/ravenclaude update "
        "&& copilot --plugin-dir plugins/ravenclaude-core/copilot'",
    ),
]


def _render_command_block(key: str, label: str, command: str) -> str:
    """Render one copy-to-clipboard command block: a labeled <code> + Copy button.

    Works on every host — the Copy button only writes to the clipboard, so the
    block is the universal fallback when the one-click /__run buttons are absent
    (GitHub Pages, file://, or `python3 -m http.server`).
    """
    return (
        '<div class="cmd-block">'
        f'<span class="cmd-label">{html.escape(label)}</span>'
        '<div class="cmd-row">'
        f'<code class="cmd-code" id="cmd-{html.escape(key)}">{html.escape(command)}</code>'
        f'<button type="button" class="btn secondary cmd-copy" '
        f'data-copy-for="cmd-{html.escape(key)}">Copy</button>'
        "</div>"
        "</div>"
    )


# ── Commands tab ─────────────────────────────────────────────────────────
# A domain-neutral card grid of every slash command shipped by ANY plugin in
# the marketplace, discovered at generator time from plugins/*/commands/*.md
# (name = filename stem; description = frontmatter `description:`; owner =
# plugin dir). The core generator must DISCOVER sibling plugins, never hard-code
# domain names (House Rule 1). Each card carries the canonical /name in a
# copy-to-clipboard block reusing the universal `.cmd-copy[data-copy-for]`
# handler, so it works on every host (file://, GitHub Pages, or served) — there
# is no live IPC to launch a command from a browser, so Copy is the reliable
# mechanic (the plan's deep-link tier needs a desktop handler we can't assume).

_FRONTMATTER_DESC_RE = _re.compile(r"(?m)^description:\s*(.+?)\s*$")


def _commands_inventory() -> list[dict]:
    """Discover slash commands across all plugins. Returns dicts sorted by
    (owner, name): {"name", "owner", "description"}."""
    cmds: list[dict] = []
    for cmd_path in sorted(PLUGINS_DIR.glob("*/commands/*.md")):
        owner = cmd_path.parent.parent.name
        name = cmd_path.stem
        desc = ""
        try:
            text = cmd_path.read_text(encoding="utf-8")
        except OSError:
            continue
        if text.startswith("---"):
            fm_end = text.find("\n---", 3)
            frontmatter = text[3:fm_end] if fm_end > 0 else ""
            m = _FRONTMATTER_DESC_RE.search(frontmatter)
            if m:
                desc = m.group(1).strip().strip("\"'")
        cmds.append({"name": name, "owner": owner, "description": desc})
    return cmds


# Commands map to one of three execution classes (see docs/dashboard-ux-build-plan.md §4).
# All 4 shipped commands are Claude Code slash commands → Class B (copy + run-in-Claude).
# A command becomes Class A only when its effect maps to an EXISTING /__run action
# (install/update/status) — none do today, so no new /__run action is introduced here
# (PR-1 keeps the security delta at zero). The classifier is data-driven so a future
# shell-shaped command lights up a Run button without touching this renderer.
_CLASS_A_RUN_ACTION = {
    # command-name -> an action in serve-dashboards.py RUN_ACTIONS (fixed argv,
    # non-destructive, served-dev-server only). The slash command still copies
    # for in-Claude use; the Run button executes the equivalent shell effect.
    # /set-posture's effect = apply comfort-posture.yaml -> .claude/settings.json,
    # the same fixed argv /__save already runs (PR-2: entry point, not capability).
    "set-posture": "set-posture",
}

# Human-readable form of each Class-A/C action's fixed server argv (RUN_ACTIONS
# in serve-dashboards.py), for the card's "Run executes:" line. Display only.
_RUN_ACTION_LITERAL = {
    "install": "ravenclaude install",
    "update": "ravenclaude update",
    "status": "ravenclaude status",
    "set-posture": "apply-comfort-posture.py",
}


def _render_command_card(cmd: dict) -> str:
    # Plugin commands are invoked NAMESPACED as /<plugin>:<command> — that form is
    # always correct and can never collide with another plugin's command (verified
    # against Claude Code's skills/commands docs, 2026-05). The bare /<command>
    # form is not guaranteed for an installed plugin, so the dashboard shows and
    # copies the namespaced form.
    slash = f"/{cmd['owner']}:{cmd['name']}"
    cid = f"cmd-card-{html.escape(cmd['owner'])}-{html.escape(cmd['name'])}"
    desc = cmd["description"] or "No description provided."
    run_action = _CLASS_A_RUN_ACTION.get(cmd["name"])

    if run_action:
        # Class C — a slash command whose shell EFFECT maps to a fixed /__run
        # action. Offer both: Run (the shell effect, served only) + Copy (the
        # slash command, runs in Claude). The literal shown is the human form of
        # the fixed argv the server runs — kept in sync with RUN_ACTIONS.
        runs_literal = _RUN_ACTION_LITERAL.get(run_action, run_action)
        what_runs = (
            '<p class="cmd-what" '
            f'title="The green Run button does one fixed, safe thing right here in the page: it runs {html.escape(runs_literal)}. Or copy the command and paste it into Claude Code to do the same thing in your chat.">'
            "<span class=\"cmd-what-label\">Run does:</span> "
            f'<code>{html.escape(runs_literal)}</code>'
            f' &middot; <span class="cmd-what-label">or in Claude:</span> <code>{html.escape(slash)}</code></p>'
        )
        actions = (
            f'<button type="button" class="btn cmd-run" data-run-action="{html.escape(run_action)}" '
            f'title="Press to run {html.escape(runs_literal)} now. Only works when you opened this page with the dev server; on a plain web page it stays greyed out." '
            "disabled>&#9654; Run</button>"
            f'<code class="cmd-code" id="{cid}">{html.escape(slash)}</code>'
            f'<button type="button" class="btn secondary cmd-copy" data-copy-for="{cid}" '
            f'title="Copies {html.escape(slash)}. Paste it into Claude Code and press enter to run the whole thing.">Copy</button>'
        )
        pill = '<span class="cmd-pill" title="The Run button works here; the slash command works inside Claude Code. Both do the same safe thing.">Run here · or in Claude</span>'
    else:
        # Class B — a Claude Code slash command. A browser CANNOT launch it (there
        # is no way for a web page to type into your Claude chat — verified against
        # Claude Code's docs). So the honest, working UX is: copy it, paste it into
        # Claude Code, and the command runs the whole multi-step job there.
        what_runs = (
            '<p class="cmd-what" '
            f'title="This is a Claude Code command. A web page can&#39;t run it for you. Press Copy, then paste {html.escape(slash)} into Claude Code and press enter — Claude does the whole job for you there.">'
            "<span class=\"cmd-what-label\">How to run it:</span> "
            f'copy it, then paste into Claude Code &mdash; <code>{html.escape(slash)}</code></p>'
        )
        actions = (
            f'<code class="cmd-code" id="{cid}">{html.escape(slash)}</code>'
            f'<button type="button" class="btn cmd-copy" data-copy-for="{cid}" '
            f'title="Copies {html.escape(slash)}. Paste it into Claude Code and press enter — that runs the whole command.">Copy</button>'
        )
        pill = '<span class="cmd-pill" title="A web page can&#39;t run this for you. Copy it and paste it into Claude Code, where it runs the whole job.">Copy &rarr; paste into Claude</span>'

    return (
        '<article class="cmd-card">'
        '<header class="cmd-card-head">'
        f'<h3 class="cmd-card-title">{html.escape(slash)}</h3>'
        f'<span class="cmd-card-badge" '
        f'title="Shipped by the {html.escape(cmd["owner"])} plugin">'
        f'{html.escape(cmd["owner"])}</span>'
        f"{pill}"
        "</header>"
        f'<p class="cmd-card-desc">{html.escape(desc)}</p>'
        f"{what_runs}"
        f'<div class="cmd-row">{actions}</div>'
        "</article>"
    )


def _render_overview_tab() -> str:
    """Marketplace-wide Overview / 'Start here' tab — the default landing surface.
    Build-time, generator-discovered (House Rule 1 — never hard-code counts/names),
    so it renders identically on a static host and when served. The only live
    element is the served/static banner (toggled by the HEAD /__save probe in JS)."""
    plugin_dirs = sorted(
        p for p in PLUGINS_DIR.glob("*/.claude-plugin/plugin.json")
    )
    n_plugins = len(plugin_dirs)
    n_agents = len(list(PLUGINS_DIR.glob("*/agents/*.md")))
    n_skills = len(
        [p for p in PLUGINS_DIR.glob("*/skills/*") if p.is_dir()]
        + [p for p in PLUGINS_DIR.glob("*/skills/*.md") if p.is_file()]
    )
    n_commands = len(_commands_inventory())
    n_trees = len(_decision_trees_inventory())
    n_practices = len(_best_practices_inventory())

    stat = lambda n, label: (
        f'<div class="ov-stat"><strong>{n}</strong><span>{html.escape(label)}</span></div>'
    )
    stats = "".join([
        stat(n_plugins, "plugins"),
        stat(n_agents, "agents"),
        stat(n_skills, "skills"),
        stat(n_commands, "commands"),
        stat(n_trees, "decision trees"),
        stat(n_practices, "best practices"),
    ])

    def card(title, body, target, cta):
        return (
            f'<a class="ov-card" href="#/{target}">'
            f'<h4>{html.escape(title)}</h4>'
            f'<p>{html.escape(body)}</p>'
            f'<span class="ov-card-cta">{html.escape(cta)} &rarr;</span>'
            "</a>"
        )

    systems = "".join([
        card("Comfort posture",
             "Tune how autonomous your agents are — per-category deny / ask / allow, "
             "and the security floor that never relaxes.",
             "settings", "Open Settings"),
        card("Guardrail pipeline",
             "See every guard an action passes through — from session start, through "
             "command review, to completion — with live on/off badges.",
             "pipeline", "Open Pipeline"),
        card("Command-review tribunal",
             "The Thing — RavenClaude's command-review engine — checks risky "
             "commands and logs an allow / edit / deny verdict you can browse.",
             "saga", "Open Review log"),
        card("Install & update",
             "Two guides, one per tool: install &amp; update RavenClaude in Claude Code "
             "(the Bifröst bridge) or in GitHub Copilot CLI.",
             "bifrost", "Open install guides"),
    ])

    steps_required = "".join([
        '<li><a href="#/settings">Pick a posture preset</a> — set how much your agents do without asking.</li>',
        '<li>Wire it into your tool — <a href="#/bifrost">Claude&nbsp;Code</a> or <a href="#/install">Copilot&nbsp;CLI</a>. One-time setup, then updates are a git pull.</li>',
    ])
    steps_optional = "".join([
        '<li><a href="#/pipeline">See what the guardrails do</a> — the map of every check, in plain language.</li>',
        '<li><a href="#/trees">Browse the guidance</a> — the decision trees + best practices each plugin gives your agents.</li>',
    ])

    return (
        '<div class="ov-wrap">'
        '<div class="ov-hero">'
        "<h2>RavenClaude &mdash; your control surface</h2>"
        "<p>RavenClaude is your private Claude Code <strong>plugin marketplace</strong>. "
        "This dashboard is where you <strong>tune how autonomous your agents are</strong>, "
        "watch the guardrails every action passes through, and wire the plugin into your tools. "
        "(Looking for the public catalog of every agent &amp; skill? That's "
        "<code>repo-guide.html</code> &mdash; this dashboard is the <em>controls</em>, not the catalog.)</p>"
        '<div id="ov-mode-banner" class="ov-banner ov-banner-static">'
        "<strong>Preview</strong> &mdash; this is a read-only view. Run the served dashboard "
        "(<code>rc dashboard</code> or <code>python3 scripts/serve-dashboards.py</code>) to save changes to your repo."
        "</div>"
        "</div>"
        f'<p class="ov-stats-lead">You have <strong>{n_plugins}</strong> plugins installed &mdash; '
        f"<strong>{n_agents}</strong> specialist agents and <strong>{n_trees}</strong> decision trees "
        "ready to help your agents stay in bounds.</p>"
        f'<div class="ov-stats">{stats}</div>'
        '<h3 class="ov-h3">The big systems</h3>'
        f'<div class="ov-cards">{systems}</div>'
        '<h3 class="ov-h3">Start here</h3>'
        '<p class="ov-steps-lead">New here? The two <strong>required</strong> steps take about five minutes. '
        "The rest you can explore whenever.</p>"
        '<p class="ov-steps-cap">Required</p>'
        f'<ol class="ov-steps">{steps_required}</ol>'
        '<p class="ov-steps-cap ov-steps-cap-optional">Optional &mdash; when you want to go deeper</p>'
        f'<ol class="ov-steps ov-steps-optional" start="3">{steps_optional}</ol>'
        "</div>"
    )


def _render_commands_tab() -> str:
    """Render the Commands tab: a card grid of every marketplace slash command.
    Empty-state when no plugin ships a command."""
    cmds = _commands_inventory()
    if not cmds:
        return (
            '<div class="stub"><h2>Commands</h2>'
            "<p>No slash commands are shipped by the installed plugins yet.</p></div>"
        )
    cards = "".join(_render_command_card(c) for c in cmds)
    plural = "s" if len(cmds) != 1 else ""
    n_run = sum(1 for c in cmds if _CLASS_A_RUN_ACTION.get(c["name"]))
    run_note = (
        f" {n_run} can run from here when the dashboard is served; the rest are "
        "Claude Code slash commands."
        if n_run else
        " Each card shows exactly what it runs. Copy a command and paste it into your "
        "Claude Code session to run it — a browser can't launch a slash command."
    )
    intro = (
        '<div class="cmd-intro">'
        "<h2>Commands</h2>"
        f"<p>{len(cmds)} command{plural} shipped by the marketplace plugins.{run_note}</p>"
        "</div>"
    )
    return intro + f'<div class="cmd-grid">{cards}</div>'


# ── Guidance tab (marketplace-wide decision trees + best practices) ──────────
# The dashboard is a marketplace-wide control surface, not a single-plugin view:
# this tab discovers EVERY plugin's canonical `## Decision Tree:` sections and
# its best-practices/ docs (House Rule 1 — discover siblings, never hard-code
# domain names) and embeds them at build time, so the surface works identically
# on a static host (GitHub Pages / file://) and a served dashboard — there is no
# fetch. It answers "what priors + rules does each installed plugin give my
# agents?" in one place.

_DT_HEADER_RE = _re.compile(r"(?m)^##\s+Decision Tree:\s*(.+?)\s*$")
_DT_WHEN_RE = _re.compile(r"\*\*When this applies:\*\*\s*(.+)")
_DT_MERMAID_RE = _re.compile(r"```mermaid\s*\n(.*?)\n```", _re.DOTALL)
_DT_NEXT_HEADER_RE = _re.compile(r"(?m)^##\s")
_BP_STATUS_RE = _re.compile(r"(?mi)^\*\*Status:\*\*\s*(.+?)\s*$")
_SLUG_STRIP_RE = _re.compile(r"[^a-z0-9]+")


def _tree_slug(text: str) -> str:
    """Stable, filesystem-safe slug from a tree title (id survives re-renders so
    long as the title is stable). Lowercase, non-alnum → '-', trimmed, capped."""
    s = _SLUG_STRIP_RE.sub("-", text.lower()).strip("-")
    return s[:60] or "tree"


def _decision_trees_inventory() -> list[dict]:
    """Discover canonical '## Decision Tree: <title>' sections across all plugins
    (knowledge/ + skills/). Returns {id, owner, title, when, mermaid, path} sorted
    by (owner, title). `id` is stable (owner + title slug, deduped) and `mermaid`
    is the FIRST mermaid fence inside the section (empty string if none) — both are
    consumed by render-trees.py to pre-render an inline SVG per tree."""
    out: list[dict] = []
    paths = sorted(PLUGINS_DIR.glob("*/knowledge/**/*.md")) + sorted(
        PLUGINS_DIR.glob("*/skills/**/*.md")
    )
    seen_ids: dict[str, int] = {}
    for md in paths:
        try:
            owner = md.relative_to(PLUGINS_DIR).parts[0]
            text = md.read_text(encoding="utf-8")
        except (OSError, ValueError):
            continue
        for m in _DT_HEADER_RE.finditer(text):
            title = m.group(1).strip()
            # Section body = from this header to the next '## ' (or EOF).
            nxt = _DT_NEXT_HEADER_RE.search(text, m.end())
            section = text[m.end(): nxt.start() if nxt else len(text)]
            wm = _DT_WHEN_RE.search(section[:600])
            when = wm.group(1).strip() if wm else ""
            mm = _DT_MERMAID_RE.search(section)
            mermaid = mm.group(1).strip() if mm else ""
            base = f"{owner}--{_tree_slug(title)}"
            n = seen_ids.get(base, 0)
            seen_ids[base] = n + 1
            tid = base if n == 0 else f"{base}-{n + 1}"
            out.append({
                "id": tid,
                "owner": owner,
                "title": title,
                "when": when,
                "mermaid": mermaid,
                "path": str(md.relative_to(REPO_ROOT)),
            })
    out.sort(key=lambda d: (d["owner"], d["title"].lower()))
    return out


_MD_LINK_RE = _re.compile(r"\[([^\]]+)\]\([^)]*\)")


def _bp_preview(text: str) -> str:
    """Extract a short preview for the Guidance tab: the first paragraph of the
    '## Why this exists' section (or the first body paragraph), with inline
    markdown links flattened to their text and capped. Net-new parse — the rest
    of the inventory only reads the title + Status."""
    m = _re.search(r"(?ms)^##\s+Why this exists\s*\n+(.+?)(?:\n##|\Z)", text)
    body = ""
    if m:
        body = m.group(1)
    else:
        # Fall back to the first non-heading, non-blank, non-metadata paragraph.
        for para in _re.split(r"\n\s*\n", text):
            s = para.strip()
            if not s or s.startswith("#") or s.startswith("**") or s.startswith("---"):
                continue
            body = s
            break
    body = _MD_LINK_RE.sub(r"\1", " ".join(body.split()))
    return body[:280] + ("…" if len(body) > 280 else "")


def _best_practices_inventory() -> list[dict]:
    """Discover best-practices/*.md (excluding README) across all plugins.
    Returns {owner, title, status, preview, path} sorted by (owner, title)."""
    out: list[dict] = []
    for md in sorted(PLUGINS_DIR.glob("*/best-practices/*.md")):
        if md.name.lower() == "readme.md":
            continue
        try:
            owner = md.relative_to(PLUGINS_DIR).parts[0]
            text = md.read_text(encoding="utf-8")
        except (OSError, ValueError):
            continue
        title = md.stem
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("# "):
                title = s[2:].strip()
                break
        sm = _BP_STATUS_RE.search(text)
        out.append({
            "owner": owner,
            "title": title,
            "status": sm.group(1).strip() if sm else "",
            "preview": _bp_preview(text),
            "path": str(md.relative_to(REPO_ROOT)),
        })
    out.sort(key=lambda d: (d["owner"], d["title"].lower()))
    return out


# Pre-rendered decision-tree SVGs (scripts/render-trees.py). Loaded lazily + cached
# so the generator stays fast when the dir is absent (graceful: no diagram, just
# the source link). Path mirrors render-trees.py VISUALS_DIR.
TREE_VISUALS_DIR = PLUGINS_DIR / "ravenclaude-core" / "knowledge" / "tree-visuals"
_TREE_SVG_CACHE: dict[str, str] = {}


def _load_tree_svg(tree_id: str) -> str:
    """Return the committed, themed SVG for a tree id, or '' if not rendered yet."""
    if tree_id in _TREE_SVG_CACHE:
        return _TREE_SVG_CACHE[tree_id]
    svg_path = TREE_VISUALS_DIR / f"{tree_id}.svg"
    try:
        svg = svg_path.read_text(encoding="utf-8")
    except OSError:
        svg = ""
    _TREE_SVG_CACHE[tree_id] = svg
    return svg


def _render_trees_tab() -> str:
    """Marketplace-wide Guidance tab: every plugin's decision trees + best practices.
    Static (build-time embed) — no server needed, works on any host. Each tree's
    pre-rendered SVG (scripts/render-trees.py) is inlined inside a native <details>
    so it expands without JS and stays collapsed (page-weight-friendly) by default."""
    trees = _decision_trees_inventory()
    practices = _best_practices_inventory()
    owners = sorted({t["owner"] for t in trees} | {p["owner"] for p in practices})
    if not owners:
        return _render_stub_tab("Guidance", "next")

    intro = (
        '<div class="cmd-intro">'
        "<h2>Guidance — decision trees &amp; best practices</h2>"
        f"<p>{len(trees)} decision tree{'s' if len(trees) != 1 else ''} and "
        f"{len(practices)} best-practice doc{'s' if len(practices) != 1 else ''} "
        f"across {len(owners)} marketplace plugin{'s' if len(owners) != 1 else ''}. "
        "These are the decision trees (when-this-applies guidance) and named best-practice "
        "rules each installed plugin gives your agents. Click a best-practice "
        "<strong>preview</strong> to read its rationale inline, or the title to open its source file.</p>"
        "</div>"
    )

    blocks = []
    for owner in owners:
        ot = [t for t in trees if t["owner"] == owner]
        op = [p for p in practices if p["owner"] == owner]
        tree_parts = []
        for t in ot:
            link = (
                '<a href="../../{path}" class="guide-link">'
                '<span class="guide-kind guide-kind-tree">tree</span>'
                '<span class="guide-title">{title}</span></a>'.format(
                    path=html.escape(t["path"]), title=html.escape(t["title"])
                )
            )
            when = f'<p class="guide-when">{html.escape(t["when"])}</p>' if t["when"] else ""
            svg = _load_tree_svg(t["id"])
            if svg:
                # Native <details> — opens without JS, collapsed by default so the
                # page stays light with 150+ inlined diagrams. SVG is pre-themed.
                diagram = (
                    '<details class="guide-tree-diagram">'
                    '<summary class="guide-tree-summary">Diagram</summary>'
                    f'<div class="guide-tree-svg">{svg}</div>'
                    "</details>"
                )
            else:
                diagram = ""
            tree_parts.append(f'<li class="guide-item">{link}{when}{diagram}</li>')
        tree_items = "".join(tree_parts)
        bp_parts = []
        for idx, p in enumerate(op):
            pid = f"bp-prev-{html.escape(p['owner'])}-{idx}"
            preview = p.get("preview") or ""
            toggle = (
                f'<button type="button" class="guide-bp-toggle" '
                f'data-bp-toggle="{pid}" aria-expanded="false">preview</button>'
                if preview else ""
            )
            preview_html = (
                f'<p class="guide-bp-preview" id="{pid}" hidden>{html.escape(preview)}</p>'
                if preview else ""
            )
            bp_parts.append(
                '<li class="guide-item"><a href="../../{path}" class="guide-link">'
                "<span class=\"guide-kind guide-kind-bp\">{status}</span>"
                "<span class=\"guide-title\">{title}</span></a>{toggle}{preview}</li>".format(
                    path=html.escape(p["path"]),
                    title=html.escape(p["title"]),
                    status=html.escape(p["status"] or "rule"),
                    toggle=toggle,
                    preview=preview_html,
                )
            )
        bp_items = "".join(bp_parts)
        tree_section = (
            f'<h4 class="guide-subhd">Decision trees <span class="guide-count">{len(ot)}</span></h4>'
            f"<ul class=\"guide-list\">{tree_items}</ul>"
            if ot else ""
        )
        bp_section = (
            f'<h4 class="guide-subhd">Best practices <span class="guide-count">{len(op)}</span></h4>'
            f"<ul class=\"guide-list\">{bp_items}</ul>"
            if op else ""
        )
        blocks.append(
            '<details class="guide-plugin" open>'
            f'<summary class="guide-plugin-name">{html.escape(owner)}'
            f'<span class="guide-plugin-counts">{len(ot)} trees · {len(op)} practices</span>'
            "</summary>"
            f'<div class="guide-plugin-body">{tree_section}{bp_section}</div>'
            "</details>"
        )
    return intro + '<div class="guide-wrap">' + "".join(blocks) + "</div>"


def _render_install_tab() -> str:
    """Render the 'Install & Update' tab.

    Guides a GitHub Copilot CLI user to wire RavenClaude's agents/skills/hooks/MCP
    into Copilot. Copy-to-clipboard command blocks work on any host; the one-click
    Install / Update / Status buttons light up only when the page is served by
    scripts/serve-dashboards.py (probed via HEAD /__run, mirroring the Settings
    tab's HEAD /__save probe). Clicking a button POSTs {"action":...} to /__run.
    """
    command_blocks = "".join(
        _render_command_block(key, label, command)
        for key, label, command in _INSTALL_COMMANDS
    )
    return _INSTALL_TAB_TEMPLATE.format(command_blocks=command_blocks)


def _render_settings_tab(properties: dict, presets: dict) -> str:
    """Render the Settings tab body from the schema's properties + presets."""
    # Preset bar — iterate in schema order (NOT sorted), so the order matches
    # the segmented-control level order. Each preset button picks up a color
    # tint matching the level it maps to.
    preset_buttons: list[str] = []
    for preset_name in presets.keys():
        preset = presets[preset_name]
        preset_desc = preset.get("_description", "")
        # Custom label (e.g. "★ Recommended") if set, else derive from key.
        button_label = preset.get("_label") or _label_for(preset_name)
        # CSS class for color tinting (matches .seg-label.seg-<level> palette)
        preset_buttons.append(
            f'<button type="button" class="preset-btn preset-{html.escape(preset_name)}" '
            f'data-preset="{html.escape(preset_name)}" '
            f'title="{html.escape(preset_desc)}">{html.escape(button_label)}</button>'
        )

    # Per-category expandable cards, grouped
    categories_props = properties.get("categories", {}).get("properties", {})
    groups: dict[str, list[tuple[str, dict]]] = {}
    for cat_name in sorted(categories_props.keys()):
        cat_schema = categories_props[cat_name]
        group = cat_schema.get("x-group", "Other")
        groups.setdefault(group, []).append((cat_name, cat_schema))

    group_html_parts: list[str] = []
    for group_name in sorted(groups.keys()):
        card_blocks: list[str] = []
        for name, sch in groups[group_name]:
            card_blocks.append(_render_category_card(name, sch))
        group_html_parts.append(
            f'<fieldset class="cat-group"><legend>{html.escape(group_name)}</legend>'
            + "".join(card_blocks)
            + "</fieldset>"
        )

    security_deny_html = _render_security_deny(
        properties.get("security_deny", {})
    )

    design_checkins_html = _render_design_checkins(
        properties.get("design_checkins", {})
    )

    category_intro_html = (
        '<div class="category-intro"><p>'
        "Each row below is a <strong>type of action</strong> Claude might take "
        "&mdash; for example, <code>shell_code_exec</code> means &ldquo;run code "
        "such as <code>python -c &hellip;</code>&rdquo;. For each one you pick "
        "<strong>Deny</strong> (never), <strong>Ask</strong> (check with me first), "
        "or <strong>Allow</strong> (go ahead). Start from the "
        "<strong>&#9733; Recommended</strong> preset above and loosen or tighten "
        "from there as you build trust."
        "</p></div>"
    )

    return _SETTINGS_TAB_TEMPLATE.format(
        preset_buttons="".join(preset_buttons),
        design_checkins=design_checkins_html,
        thing_preview=_render_thing_preview(),
        category_intro=category_intro_html,
        category_groups="".join(group_html_parts),
        security_deny=security_deny_html,
    )


def _scales_svg(state_key: str, aria_label: str) -> str:
    """Return an inline SVG scales-of-justice icon for a given review state.

    state_key must be one of: reviewed | off | paused
    The element carries role="img", aria-label, and data-review-state so that
    CSS and JS can both read the effective state without relying on colour alone.
    """
    return (
        f'<svg class="review-scales-icon" data-review-state="{html.escape(state_key)}" '
        f'role="img" aria-label="{html.escape(aria_label)}" '
        'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" '
        'width="18" height="18" fill="none" aria-hidden="false">'
        # Beam / crossbar
        '<line x1="2" y1="5" x2="18" y2="5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>'
        # Central pillar
        '<line x1="10" y1="5" x2="10" y2="16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>'
        # Base
        '<line x1="6" y1="16" x2="14" y2="16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>'
        # Left pan arc
        '<path d="M2 5 L4 10 Q5 12 6 10 L8 5" stroke="currentColor" stroke-width="1.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        # Right pan arc
        '<path d="M12 5 L14 10 Q15 12 16 10 L18 5" stroke="currentColor" stroke-width="1.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        "</svg>"
    )


def _render_cr_category_summary() -> str:
    """Return a read-only grid of all 12 live categories with their scales icon.

    The icons are initialised server-side to 'off' (default); JS updates them
    to the effective state (reviewed | off | paused) after restore + on every
    change via updateReviewIcons().
    """
    cells: list[str] = []
    for cat in sorted(THING_LIVE_CATEGORIES):
        icon_html = _scales_svg("off", f"Command review: off — {cat}")
        cells.append(
            f'<div class="cr-summary-cell" data-cr-summary-cat="{html.escape(cat)}">'
            f'<span class="cr-summary-icon">{icon_html}</span>'
            f'<span class="cr-summary-label"><code>{html.escape(cat)}</code></span>'
            f'<span class="cr-summary-micro" data-cr-micro-for="{html.escape(cat)}">off</span>'
            "</div>"
        )
    return (
        '<div class="cr-summary-grid" aria-label="Command review status per category">'
        + "".join(cells)
        + "</div>"
    )


def _render_thing_preview() -> str:
    """Render the consolidated 'Command review (the Thing)' block.

    Now delegates to _render_command_review_block(). This name is kept so
    existing call-sites in _render_settings_tab() keep working unchanged; the
    template slot {thing_preview} is the canonical position for this block.
    """
    return _render_command_review_block()


def _render_command_review_block() -> str:
    """Single consolidated command-review block.

    Order:
      (a) header + scales icon + master enable switch
      (b) one-paragraph explainer + credits-cost warning
      (c) gate_floor segmented control
      (d) read-only per-category status summary (informational mirror of toggle state)
      (e) Advanced <details>: seat model selects, confidence, MCP allowlist, per-tier panel
    """
    rows = []
    for seat, label, default_model in _THING_SEAT_META:
        opts = "".join(
            f'<option value="{html.escape(v)}"'
            f'{" selected" if v == default_model else ""}>{html.escape(t)}</option>'
            for v, t in _THING_MODEL_CHOICES
        )
        rows.append(
            f'<label class="cr-seat-row" for="cr-seat-{seat}">'
            f'<span class="cr-seat-name">{html.escape(label)}</span>'
            f'<select id="cr-seat-{seat}" class="cr-seat-select" data-cr-seat="{html.escape(seat)}">{opts}</select>'
            "</label>"
        )
    seats_html = "".join(rows)

    # (a) Header row: title + scales icon + master switch
    header = (
        '<div class="crb-head">'
        '<div class="crb-title-row">'
        + _scales_svg("off", "Command review: master off")
        + '<h3 id="crb-heading">&#9878; Command review <span class="thing-aka">(the Thing)</span>'
        '<span class="preview-pill">Early access</span></h3>'
        "</div>"
        '<div class="crb-master-row">'
        '<label class="crb-master-label" for="cr-master-enable">'
        "Master enable &mdash; when off, all per-category toggles are paused (not cleared)"
        "</label>"
        '<label class="dc-switch" title="Master enable for command review. '
        "When off, review is paused globally; per-category settings are preserved."
        '">'
        '<input type="checkbox" id="cr-master-enable" checked '
        'aria-label="Command review master enable" aria-describedby="crb-master-state">'
        '<span class="dc-track"><span class="dc-thumb"></span></span>'
        "</label>"
        "</div>"
        '<p class="crb-master-state" id="crb-master-state"></p>'
        "</div>"
    )

    # (b) Explainer paragraph
    explainer = (
        "<p>When turned on for a category, a command that would normally stop to "
        "<strong>ask you</strong> is instead checked by a panel of AI reviewers "
        "before it runs. Each one looks for a different problem: "
        "<strong>Forseti</strong> checks for security risks, "
        "<strong>Mímir</strong> checks the command is correct, and "
        "<strong>Heimdall</strong> watches for hidden instructions trying to trick "
        "the system (a &ldquo;prompt injection&rdquo;). <strong>Thor</strong> breaks "
        "a tie if they disagree. They vote <strong>allow / edit / deny</strong>, and "
        "a reviewer may <em>rewrite</em> a risky command into a safe one (re-checked "
        "before it runs). You are interrupted only when the panel can&rsquo;t decide; "
        "every verdict is logged. It can only resolve the <em>ask</em> cases &mdash; "
        "it can never unblock the always-denied &ldquo;danger zone&rdquo; commands "
        "(like force-pushing or wiping a folder). "
        '<strong class="crb-cost-warn">Costs credits on every reviewed command</strong> '
        "&mdash; treat it as a high-stakes guard, not a daily setting. "
        'Design: <a href="../../docs/tribunal-review-feature-design.md" target="_blank" '
        'rel="noopener">tribunal-review-feature-design.md</a> &middot; '
        '<a href="knowledge/concerns-catalog.md" target="_blank" rel="noopener">concern catalog</a>.</p>'
        '<p class="crb-live-note"><strong>Live for twelve categories:</strong> '
        "the five <strong>shell</strong> categories plus <code>network_write</code> "
        "(allow / edit / deny); six <strong>tool-shape</strong> categories "
        "(<code>file_edit_*</code>, <code>file_read_*</code>, <code>network_read</code>, "
        "<code>mcp_tools</code>) are allow / deny only. "
        "Turn each on via its toggle inside the category card below.</p>"
    )

    # (b2) Scope disclaimer — when command review is for you, and when it's optional.
    disclaimer = (
        '<details class="crb-disclaimer">'
        '<summary>Is command review for me? (scope &amp; when it&rsquo;s optional)</summary>'
        "<p>Command review exists to put <strong>portable, model-agnostic</strong> "
        "guardrails on agentic AI that routes across <strong>multiple model vendors</strong> "
        "(e.g. GitHub Copilot CLI using Claude + ChatGPT + Grok), where Claude Code&rsquo;s "
        "native <code>auto</code> permission mode is unavailable (it is Anthropic-API/Claude-only). "
        "There it is the only layer giving you a deterministic catastrophe floor, a self-tamper "
        "guard, secret-egress prevention, cross-vendor anti-correlated review, and low-touch "
        "allow / edit / deny disposition.</p>"
        "<p><strong>If you run <em>only</em> Claude Code, native <code>auto</code> mode may be "
        "enough</strong> &mdash; it adds a hardened classifier plus a non-configurable "
        "3-consecutive / 20-total runaway brake. On pure Claude Code, prefer <code>auto</code> for "
        "containment and treat command review as an <em>optional</em> add-on for its domain "
        "concerns, audit trail, and yes/no decision-routing. The tribunal earns its credits cost "
        "most clearly where <code>auto</code> cannot run.</p>"
        "</details>"
    )

    # (d) Per-category status summary (read-only mirror)
    summary = (
        '<div class="crb-summary-section">'
        '<span class="crb-summary-title">Per-category review status</span>'
        + _render_cr_category_summary()
        + "</div>"
    )

    # (e) Advanced details
    advanced = (
        '<details class="crb-advanced pattern-details">'
        '<summary class="pattern-summary">'
        '<span class="pattern-summary-text">Advanced &mdash; seat models, confidence &amp; per-tier panel</span>'
        "</summary>"
        '<div class="crb-advanced-body">'
        '<p class="crb-adv-sub">Which model fills each seat and how unsure a seat may be before the '
        "tie-breaker is convened. Applies wherever a category&rsquo;s review toggle is on.</p>"
        '<span class="crp-hydrated" id="crp-hydrated-indicator" hidden>'
        "&#10003; Loaded from <code>.ravenclaude/comfort-posture.yaml</code></span>"
        + _render_gate_floor()
        + f'<div class="crp-seats">{seats_html}</div>'
        '<label class="crp-threshold" for="cr-threshold">'
        "<span class=\"crp-threshold-label\">Confidence threshold</span>"
        '<input type="number" id="cr-threshold" min="0" max="1" step="0.05" value="0.5">'
        '<span class="crp-hint">A seat that votes below this convenes Thor.</span>'
        "</label>"
        + _render_mcp_allowlist()
        + _render_tier_panel()
        + "</div>"
        "</details>"
    )

    return (
        '<div class="command-review-block" id="command-review-panel" '
        'aria-labelledby="crb-heading">'
        + header
        + explainer
        + disclaimer
        + summary
        + advanced
        + "</div>"
    )


# Per-seat model choices offered by the dashboard's command-review panel section.
_THING_MODEL_CHOICES = [
    ("claude-opus-4-7", "Opus 4.7 — most capable"),
    ("claude-sonnet-4-6", "Sonnet 4.6 — balanced"),
    ("claude-haiku-4-5", "Haiku 4.5 — fast / cheap"),
]
# (seat key, display label, default model) — mirrors thing-decision.py defaults.
_THING_SEAT_META = [
    ("forseti", "Forseti — Security", "claude-opus-4-7"),
    ("mimir", "Mímir — Correctness", "claude-haiku-4-5"),
    ("heimdall", "Heimdall — Injection watch", "claude-haiku-4-5"),
    ("thor", "Thor — Tie-breaker", "claude-opus-4-7"),
]

# gate_floor headline control — enum medium | high | extreme, default high.
# (value, label, recommended-suffix, tooltip). Copy is the exact directive copy.
_GATE_FLOOR_META = [
    (
        "medium",
        "Medium",
        "",
        "Most oversight. Reads still run free, but every change at medium risk "
        "or above — file edits, local mutations, package installs, web writes — "
        "is surfaced to you for confirmation after the tribunal clears it.",
    ),
    (
        "high",
        "High",
        "Recommended",
        "Balanced (recommended). Reads and low-risk mutations resolve "
        "automatically; higher-risk commands — writing outside the project, git "
        "push, arbitrary code execution — are surfaced to you. The tribunal still "
        "blocks or rewrites dangerous commands at every tier.",
    ),
    (
        "extreme",
        "Extreme",
        "",
        "Most autonomy. Only extreme commands — arbitrary code execution, plus "
        "anything a concern escalates to extreme — are surfaced to you; "
        "everything below resolves automatically. Irreversible (high-blast) "
        "actions always surface regardless.",
    ),
]
_GATE_FLOOR_DEFAULT = "high"

# Per-tier panel defaults — mirror thing-decision.py's built-in tier table.
# Seat keys are exactly forseti | mimir | heimdall (thor is the tie-breaker and
# never sits in a tier's `seats`). The `low` tier runs no panel and is omitted.
# (tier, label, seats, mandatory_seats, confidence_threshold, caption).
_TIER_SEATS = ["forseti", "mimir", "heimdall"]
_TIER_SEAT_LABELS = {
    "forseti": "Forseti",
    "mimir": "Mímir",
    "heimdall": "Heimdall",
}
_TIER_META = [
    (
        "medium",
        "Medium",
        ["mimir", "heimdall"],
        ["heimdall"],
        0.5,
        "By default Mímir + Heimdall convene; Heimdall is required.",
    ),
    (
        "high",
        "High",
        ["forseti", "mimir", "heimdall"],
        ["heimdall"],
        0.6,
        "By default Forseti + Mímir + Heimdall convene; Heimdall is required.",
    ),
    (
        "extreme",
        "Extreme",
        ["forseti", "mimir", "heimdall"],
        ["forseti", "heimdall"],
        0.7,
        "By default Forseti + Mímir + Heimdall convene; Forseti + Heimdall are required.",
    ),
]


def _render_command_review_panel() -> str:
    """Removed — content is now part of _render_command_review_block() (via _render_thing_preview).

    Returns empty string so any accidental legacy call-site is a no-op rather
    than a crash. The {command_review_panel} template slot has been removed from
    _SETTINGS_TAB_TEMPLATE; this stub is kept only for safety.
    """
    return ""


def _render_mcp_allowlist() -> str:
    """Render the MCP server allowlist input (§MCP identity, v0.41.0).

    A free-text field of trusted MCP server names (the `<server>` in
    `mcp__<server>__<verb>`). When non-empty, the JS serializes
    `command_review.mcp.allowed_servers: [...]`, which the tribunal reads: a WRITE
    verb from a server NOT on the list is denied pre-LLM. Opt-in — empty means the
    server-identity concerns stay seat-judged (nothing newly blocked). Only takes
    effect while the `mcp_tools` category's review toggle is on.
    """
    return (
        '<label class="crp-mcp-allow" for="cr-mcp-allow">'
        '<span class="crp-mcp-allow-label">Trusted MCP servers '
        '<span class="crp-mcp-allow-opt">(optional allowlist)</span></span>'
        '<input type="text" id="cr-mcp-allow" class="crp-mcp-allow-input" '
        'placeholder="e.g. github, atlassian, sentry" '
        'aria-describedby="cr-mcp-allow-hint">'
        '<span class="crp-hint" id="cr-mcp-allow-hint">Comma-separated server names '
        "(the <code>&lt;server&gt;</code> in <code>mcp__&lt;server&gt;__&lt;verb&gt;</code>). "
        "When set, a <strong>write</strong> call from a server not listed here is denied before any "
        "model runs (reads and listed servers still go to the panel). Leave empty to let the panel "
        "judge every MCP call. Applies when <code>mcp_tools</code> review is on.</span>"
        "</label>"
    )


def _render_gate_floor() -> str:
    """Render the headline `gate_floor` segmented control (medium | high | extreme).

    The comfort knob: it decides which risk tier and above is surfaced to the
    human after the tribunal clears it. Default High. Each option carries the
    directive tooltip via title=, matching the rest of the panel's tooltip idiom.
    """
    opts: list[str] = []
    for value, label, rec, tip in _GATE_FLOOR_META:
        checked = " checked" if value == _GATE_FLOOR_DEFAULT else ""
        rec_badge = (
            f'<span class="rec-badge">{html.escape(rec)}</span>' if rec else ""
        )
        opts.append(
            f'<input type="radio" id="gate-floor-{value}" name="gate-floor" '
            f'value="{value}"{checked} data-gate-floor="{value}">'
            f'<label for="gate-floor-{value}" class="seg-label gate-floor-{value}" '
            f'title="{html.escape(tip)}">{html.escape(label)}{rec_badge}</label>'
        )
    return (
        '<div class="crp-gate-floor">'
        '<span class="crp-gate-floor-label">Comfort level &mdash; which commands you confirm</span>'
        '<div class="seg-control gate-floor-seg" role="radiogroup" '
        'aria-label="Comfort level (which risk tier and above is surfaced to you)">'
        + "".join(opts)
        + "</div>"
        '<p class="crp-gate-floor-note">Reads are never interrupted, and the tribunal '
        "always blocks or rewrites dangerous commands &mdash; this only changes which "
        "safe-looking commands you confirm.</p>"
        "</div>"
    )


def _render_tier_panel() -> str:
    """Render the advanced per-tier expansion (medium | high | extreme).

    Behind a <details> like the per-permission overrides. Each tier card shows a
    seat checkbox per forseti/mimir/heimdall (mandatory seats render checked +
    disabled with a 'required' marker) and a per-tier confidence input. `low`
    runs no panel and gets no card — only a note.
    """
    cards: list[str] = []
    for tier, label, seats, mandatory, threshold, caption in _TIER_META:
        seat_rows: list[str] = []
        for seat in _TIER_SEATS:
            in_seats = seat in seats
            is_mandatory = seat in mandatory
            cid = f"tier-{tier}-seat-{seat}"
            checked = " checked" if (in_seats or is_mandatory) else ""
            disabled = " disabled" if is_mandatory else ""
            mandatory_attr = ' data-mandatory="1"' if is_mandatory else ""
            req_marker = (
                '<span class="tier-seat-req">required</span>' if is_mandatory else ""
            )
            seat_rows.append(
                f'<label class="tier-seat" for="{cid}">'
                f'<input type="checkbox" id="{cid}" class="tier-seat-cb" '
                f'data-tier="{tier}" data-tier-seat="{seat}"'
                f'{mandatory_attr}{checked}{disabled}>'
                f'<span class="tier-seat-name">{html.escape(_TIER_SEAT_LABELS[seat])}</span>'
                f"{req_marker}"
                "</label>"
            )
        cards.append(
            f'<div class="tier-card" data-tier="{tier}">'
            f'<div class="tier-card-head">'
            f'<span class="tier-card-title">{html.escape(label)} risk</span>'
            f'</div>'
            f'<div class="tier-seats" role="group" '
            f'aria-label="Seats that convene at {html.escape(label)} risk">'
            + "".join(seat_rows)
            + "</div>"
            f'<label class="tier-threshold" for="tier-{tier}-threshold">'
            f'<span class="tier-threshold-label">Confidence threshold</span>'
            f'<input type="number" id="tier-{tier}-threshold" '
            f'class="tier-threshold-input" data-tier-threshold="{tier}" '
            f'min="0" max="1" step="0.05" value="{threshold}">'
            f"</label>"
            f'<p class="tier-caption">{html.escape(caption)}</p>'
            f"</div>"
        )
    return (
        '<details class="pattern-details tier-details">'
        '<summary class="pattern-summary">'
        '<span class="pattern-summary-text">Per-tier panel '
        '<span class="pattern-count">(advanced)</span></span>'
        "</summary>"
        '<div class="tier-list">'
        '<p class="tier-intro">Override which seats convene and how confident the '
        "panel must be at each risk tier. A required seat (set by the tier&rsquo;s "
        "mandatory list) is always checked and can&rsquo;t be removed.</p>"
        + "".join(cards)
        + '<p class="tier-low-note"><strong>Low risk</strong> runs no panel &mdash; clean '
        "reads pass the deterministic screen for free and are never sent to the tribunal.</p>"
        "</div>"
        "</details>"
    )


def _render_design_checkins(prop: dict) -> str:
    """Render the design-check-in toggle (a behavioral flag, NOT a permission).

    This control is deliberately separate from the per-category permission cards:
    the permission scale governs whether tool *actions* need approval, while this
    flag governs whether Claude pauses to confirm design / architecture decisions.
    The checkbox renders `checked` (default ON); the JS corrects it from persisted
    state on load and serializes `design_checkins: <bool>` into the emitted YAML.
    Returns "" if the schema has no `design_checkins` property.
    """
    if not prop:
        return ""
    title = html.escape(prop.get("title", "Design check-ins"))
    desc = html.escape(prop.get("description", ""))
    return (
        '<div class="design-checkins-bar">'
        '<div class="dc-row">'
        f'<div class="dc-text"><h3>{title}</h3><p>{desc}</p></div>'
        '<label class="dc-switch" title="Toggle design check-ins">'
        '<input type="checkbox" id="design-checkins-toggle" checked>'
        '<span class="dc-track"><span class="dc-thumb"></span></span>'
        "</label>"
        "</div>"
        '<p class="dc-state" id="design-checkins-state"></p>'
        "</div>"
    )


def _render_pattern_overrides(category: str) -> str:
    """Render the collapsible per-permission, per-layer overrides block (v0.19.0).

    Each permission in the category gets its own User / Local / Project control
    (a compact <select> of Default | allow | ask | deny). "Default" (value
    "inherit") defers to the category-wide layer value for that permission; any
    other value overrides just that one permission at just that one layer. The
    JS serializes non-inherit selections into the category's `overrides:` map,
    matching the schema's `pattern_layer_object` and the translator's
    per-permission resolution. Returns "" when the category emits no patterns.
    """
    patterns = EMISSIONS.get(category, [])
    if not patterns:
        return ""
    # Vocabulary matches the per-layer category radios (allow | ask | deny |
    # inherit); "inherit" is surfaced as "Default" so the override semantics
    # ("leave this to the category") read plainly.
    opts_spec = [
        ("inherit", "Default"),
        ("allow", "allow"),
        ("ask", "ask"),
        ("deny", "deny"),
    ]
    rows: list[str] = []
    for idx, pattern in enumerate(patterns):
        explanation = PATTERN_EXPLANATIONS.get(pattern, {})
        what_text = explanation.get("what", "")
        info_btn = (
            f'<button type="button" class="info-btn info-btn-pattern" '
            f'data-info-pattern="{html.escape(pattern)}" '
            f'aria-label="Explain {html.escape(pattern)}" '
            f'title="Explain this pattern">?</button>'
            if explanation else ""
        )
        layer_controls: list[str] = []
        for layer in ("user", "local", "project"):
            sid = f"ov-{category}-{idx}-{layer}"
            options = "".join(
                f'<option value="{html.escape(value)}"'
                f'{" selected" if value == "inherit" else ""}>{html.escape(label)}</option>'
                for value, label in opts_spec
            )
            layer_controls.append(
                f'<label class="ov-layer" for="{html.escape(sid)}">'
                f'<span class="ov-layer-name">{layer.capitalize()}</span>'
                f'<select id="{html.escape(sid)}" class="ov-select" '
                f'data-category="{html.escape(category)}" '
                f'data-pattern="{html.escape(pattern)}" '
                f'data-ov-layer="{layer}">{options}</select>'
                f"</label>"
            )
        rows.append(
            f'<div class="pattern-row" data-pattern="{html.escape(pattern)}">'
            f'<div class="pattern-meta">'
            f'<code class="pattern-name" title="{html.escape(pattern)}">'
            f'{html.escape(pattern)}</code>'
            f'{info_btn}'
            f"</div>"
            f'<span class="pattern-detail">{html.escape(what_text)}</span>'
            f'<div class="pattern-layers" role="group" '
            f'aria-label="Per-layer override for {html.escape(pattern)}">'
            + "".join(layer_controls)
            + "</div>"
            "</div>"
        )
    return (
        f'<details class="pattern-details" data-category="{html.escape(category)}">'
        f'<summary class="pattern-summary">'
        f'<span class="pattern-summary-text">'
        f'Per-permission overrides <span class="pattern-count">'
        f'({len(patterns)})</span></span>'
        f'<span class="pattern-override-count" data-for="{html.escape(category)}">'
        f'0 overridden</span>'
        f'</summary>'
        f'<div class="pattern-list">'
        + "".join(rows)
        + "</div>"
        "</details>"
    )


def _render_layer_radios(name: str, layer: str, default_value: str = "inherit") -> str:
    """Render one layer row (User / Local / Project) inside an expanded card.

    Each row is a WAI-ARIA radiogroup with four options: allow / ask / deny / inherit.
    Arrow keys cycle within the group; Space selects (native radio behavior).
    """
    layer_id = f"layer-{name}-{layer}"
    # "inherit" is displayed as "Default" (value unchanged) so it reads the same as
    # the per-permission override selects that already use "Default" for inherit.
    values = [
        ("allow", "allow"),
        ("ask", "ask"),
        ("deny", "deny"),
        ("inherit", "Default"),
    ]
    radios: list[str] = []
    for value, label in values:
        rid = f"{layer_id}-{value}"
        checked = "checked" if value == default_value else ""
        radios.append(
            f'<input type="radio" id="{html.escape(rid)}" '
            f'name="{html.escape(layer_id)}" value="{html.escape(value)}" {checked} '
            f'data-category="{html.escape(name)}" data-layer="{html.escape(layer)}">'
            f'<label for="{html.escape(rid)}" class="layer-opt layer-opt-{html.escape(value)}" '
            f'title="{html.escape(value)}">{html.escape(label)}</label>'
        )
    label_text = layer.capitalize()
    return (
        f'<div class="layer-row" role="radiogroup" '
        f'aria-label="{html.escape(label_text)} layer for {html.escape(name)}">'
        f'<span class="layer-label">{html.escape(label_text)}</span>'
        f'<div class="layer-radios">'
        + "".join(radios)
        + "</div>"
        "</div>"
    )


def _render_category_card(name: str, schema: dict) -> str:
    """Render one expandable category card with three per-layer radiogroups.

    Collapsed state: title + description + effective badge.
    Expanded state: User / Local / Project rows, each with allow/ask/deny/inherit radios.
    The card is a <details> element for native keyboard expand/collapse.
    """
    title = schema.get("title", name)
    description = schema.get("description", "")
    recommended = schema.get("x-recommended", "")
    has_modal_content = bool(schema.get("x-controls") or schema.get("x-examples") or schema.get("x-guidance"))

    # Map a category's x-recommended level to the 4-value layer set for the
    # Local-layer default. v0.19.0 recommendations are already deny/ask/allow
    # (1:1); the legacy 5-level keys stay so an older schema still maps cleanly.
    rec_to_layer: dict[str, str] = {
        "deny": "deny",
        "ask": "ask",
        "allow": "allow",
        # legacy 5-level (pre-0.19.0 schemas):
        "always-ask": "ask",
        "mostly-ask": "ask",
        "mostly-allow": "allow",
        "autopilot": "allow",
    }
    local_default = rec_to_layer.get(recommended, "inherit")

    info_btn = (
        f'<button type="button" class="info-btn" data-info-for="{html.escape(name)}" '
        f'aria-label="Explain {html.escape(title)}" title="Explain this setting">?</button>'
        if has_modal_content else ""
    )

    # Build layer rows (User=inherit, Local=recommended, Project=inherit)
    user_row = _render_layer_radios(name, "user", "inherit")
    local_row = _render_layer_radios(name, "local", local_default)
    project_row = _render_layer_radios(name, "project", "inherit")

    return (
        f'<details class="cat-card" data-category="{html.escape(name)}">'
        f'<summary class="cat-card-summary">'
        f'<span class="cat-card-arrow" aria-hidden="true">&#9658;</span>'
        f'<span class="cat-card-title-group">'
        f'<span class="cat-card-title">{html.escape(title)}</span>'
        f'{info_btn}'
        f'</span>'
        f'<span class="cat-card-desc">{html.escape(description)}</span>'
        f'<span class="cat-card-badge" data-badge-for="{html.escape(name)}" '
        f'aria-label="Effective level for {html.escape(title)}"></span>'
        + _render_thing_header_toggle(name)
        + f'</summary>'
        f'<div class="cat-card-body">'
        f'<div class="cat-project-warn" data-warn-for="{html.escape(name)}" hidden>'
        f'<span class="warn-icon" aria-hidden="true">&#9888;</span> '
        f'Project-layer allows are granted to the whole team and cannot be relaxed by personal layers.'
        f'</div>'
        + user_row
        + local_row
        + project_row
        + _render_pattern_overrides(name)
        + "</div>"
        "</details>"
    )


# Categories whose command-review orchestrator is wired end-to-end, so the
# toggle is clickable (not a button that lies).
THING_LIVE_CATEGORIES = {
    "shell_readonly",
    "shell_remote_mutate",
    "shell_code_exec",
    "shell_local_mutate",
    "shell_package_install",
    # Track B Phase 1 (v0.38.0) — first non-shell shape. ALLOW/DENY-only.
    "file_edit_project",
    # Track B Phases 2-4 (v0.39.0) — file reads + file_edit_global + network +
    # MCP. All ALLOW/DENY-only.
    "file_edit_global",
    "file_read_project",
    "file_read_global",
    "network_read",
    "mcp_tools",
    # Track B (v0.40.0) — the final category. Bash-shaped (curl/wget/gh), so
    # ALLOW/EDIT/DENY like the shell categories, not ALLOW/DENY-only.
    "network_write",
}


def _render_thing_header_toggle(name: str) -> str:
    """Render a compact command-review toggle for the always-visible card header.

    For live categories: scales icon + switch only; the full label and cost note
    are in the ``title=`` tooltip so the header row stays tidy.  For non-live
    categories: a disabled switch with a 'Preview' pill, also compact.

    The ``data-thing-category`` input attribute and
    ``.cat-thing-scales[data-scales-for=…]`` span are preserved exactly so the
    existing JS change handler and ``updateReviewIcon`` keep working without
    modification.  The surrounding ``<span class="cat-hdr-thing">`` wrapper is
    used for CSS positioning; the ``cat-hdr-thing-live`` modifier class is added
    when the category is live.

    Click isolation (preventing the click from also toggling the ``<details>``)
    is handled entirely in JS — see the 'Header command-review switch isolation'
    block wired after the standard change handler.
    """
    if name in THING_LIVE_CATEGORIES:
        icon_html = _scales_svg("off", f"Command review: off — {html.escape(name)}")
        return (
            '<span class="cat-hdr-thing cat-hdr-thing-live">'
            f'<span class="cat-thing-scales" data-scales-for="{html.escape(name)}">{icon_html}</span>'
            '<label class="dc-switch thing-switch-live cat-hdr-switch" '
            f'title="Command review (the Thing) — route {html.escape(name)} commands through a '
            'one-seat reviewer (allow/deny) instead of asking you. ~10–15s &amp; credits / command. '
            'Off by default." '
            f'aria-label="Command review for {html.escape(name)}">'
            f'<input type="checkbox" data-thing-category="{html.escape(name)}" '
            f'aria-label="Command review for {html.escape(name)}">'
            '<span class="dc-track"><span class="dc-thumb"></span></span>'
            "</label>"
            "</span>"
        )
    return (
        '<span class="cat-hdr-thing">'
        '<label class="dc-switch thing-switch cat-hdr-switch" '
        f'title="Preview — command review for {html.escape(name)} ships in a later release; not active yet.">'
        '<input type="checkbox" disabled aria-disabled="true">'
        '<span class="dc-track"><span class="dc-thumb"></span></span>'
        "</label>"
        '<span class="preview-pill">Preview</span>'
        "</span>"
    )


def _render_thing_toggle(name: str) -> str:
    """Render the per-category 'Command review' toggle inside the card body.

    Clickable for the categories proven end-to-end (T2: shell_readonly) — it
    writes `thing: on` into the category's YAML; a disabled 'Preview' switch
    elsewhere keeps the 'coming soon' status legible where the control will live.

    .. deprecated::
        The body toggle has been replaced by the compact header toggle
        (``_render_thing_header_toggle``).  This function is retained so that
        call-sites can be removed cleanly one at a time without a broken import.
        Do not call it for new cards.
    """
    if name in THING_LIVE_CATEGORIES:
        icon_html = _scales_svg("off", f"Command review: off — {html.escape(name)}")
        return (
            '<div class="cat-thing-row cat-thing-live">'
            '<span class="cat-thing-label">&#9878; Command review <span class="thing-aka">(the Thing)</span></span>'
            '<label class="dc-switch thing-switch-live" '
            f'title="Route {html.escape(name)} commands through a one-seat reviewer (allow/deny) '
            'instead of asking you. Costs ~10–15s and credits per command — a validation switch, '
            'not a daily setting. Off by default.">'
            f'<input type="checkbox" data-thing-category="{html.escape(name)}" '
            f'aria-label="Command review for {html.escape(name)}">'
            '<span class="dc-track"><span class="dc-thumb"></span></span>'
            "</label>"
            f'<span class="cat-thing-scales" data-scales-for="{html.escape(name)}">{icon_html}</span>'
            '<span class="cat-thing-cost">~10–15s &amp; credits / command</span>'
            "</div>"
        )
    return (
        '<div class="cat-thing-row">'
        '<span class="cat-thing-label">&#9878; Command review <span class="thing-aka">(the Thing)</span></span>'
        '<label class="dc-switch thing-switch" '
        f'title="Preview — command review for {html.escape(name)} ships in a later release; not active yet.">'
        '<input type="checkbox" disabled aria-disabled="true">'
        '<span class="dc-track"><span class="dc-thumb"></span></span>'
        "</label>"
        '<span class="preview-pill">Preview</span>'
        "</div>"
    )


def _render_security_deny(schema: dict) -> str:
    """Render the always-on security-deny baseline as a GitHub-style Danger Zone.

    Each pattern is its own card: title + ? on the left (with description
    below), Blocked toggle on the right. Section has a red border, bold
    'Danger Zone' header in red, and a section-level info button.
    """
    defaults = schema.get("default", []) or []
    rows: list[str] = []
    for idx, pattern in enumerate(defaults):
        cid = f"sec-deny-{idx}"
        explanation = PATTERN_EXPLANATIONS.get(pattern, {})
        what_text = explanation.get("what", "")
        info_btn = (
            f'<button type="button" class="info-btn info-btn-pattern" '
            f'data-info-pattern="{html.escape(pattern)}" '
            f'aria-label="Explain {html.escape(pattern)}" '
            f'title="Explain this pattern">?</button>'
            if explanation else ""
        )
        rows.append(
            f'<div class="danger-zone-row">'
            f'<div class="danger-zone-info">'
            f'<div class="danger-zone-row-title">'
            f'<code class="danger-zone-pattern">{html.escape(pattern)}</code>'
            f'{info_btn}'
            f"</div>"
            f'<p class="danger-zone-row-desc">{html.escape(what_text)}</p>'
            f"</div>"
            f'<label class="danger-toggle">'
            f'<input type="checkbox" id="{html.escape(cid)}" '
            f'class="sec-deny-checkbox" value="{html.escape(pattern)}" checked>'
            f'<span class="danger-toggle-on">Blocked</span>'
            f'<span class="danger-toggle-off">Allowed (unsafe)</span>'
            f"</label>"
            f"</div>"
        )
    return (
        '<section class="danger-zone">'
        '<header class="danger-zone-header">'
        '<h3 class="danger-zone-title">Danger Zone'
        '<button type="button" class="info-btn info-btn-section" '
        'data-info-section="security_deny" '
        'aria-label="Explain the Danger Zone" '
        'title="Explain the Danger Zone">?</button>'
        '</h3>'
        '<p class="danger-zone-subtitle">'
        'The following patterns are ALWAYS denied, regardless of category levels. '
        'Unblock individual rules at your own risk.'
        '</p>'
        '<div class="danger-zone-note">'
        '<p><strong>These are preventive guardrails, not a malware scanner.</strong> '
        'They block the common <em>routes</em> malware and damage travel through &mdash; '
        'running remote scripts (<code>curl | sh</code>), gaining root (<code>sudo</code>), '
        'wiping files, and reading secrets &mdash; and they stop the command <em>before</em> it runs.</p>'
        '<p><strong>What they don&rsquo;t do:</strong> inspect a file&rsquo;s contents &mdash; so they cannot '
        'catch malware hidden inside something you explicitly approve. Treat the floor as a seatbelt, '
        'not a reason to skip reviewing what Claude produced.</p>'
        '<p class="danger-zone-note-maint">The floor and the hooks behind it '
        '(<code>guard-destructive</code> blocks destructive shell commands, <code>enforce-layout</code> '
        'blocks off-pattern file writes) are maintained in the RavenClaude marketplace and periodically '
        're-reviewed by the Researcher meta-skill, which adds new dangerous patterns here as they emerge. '
        'Learn more: '
        '<a href="https://code.claude.com/docs/en/settings" target="_blank" rel="noopener">Claude Code permissions</a> &middot; '
        '<a href="https://code.claude.com/docs/en/hooks" target="_blank" rel="noopener">how hooks work</a> &middot; '
        '<a href="rules/security.md" target="_blank" rel="noopener">this plugin&rsquo;s security rules</a>.</p>'
        '</div>'
        '</header>'
        '<div class="danger-zone-list">'
        + "".join(rows)
        + "</div>"
        "</section>"
    )


def _label_for(value: str) -> str:
    """Render an enum value as a short pill label (Title Case, spaces not hyphens)."""
    return " ".join(part.capitalize() for part in value.replace("_", " ").split("-"))


# ── HTML, CSS, JS templates ──────────────────────────────────────────────
# Theme variables mirror repo-guide.html so the read-only catalog and the
# editable dashboard look like the same product family.

_CSS = """
/*__SHARED_TOKENS__*/

:root {
  color-scheme: light;
  /* Dashboard palette — light beige + gold (Norse identity preserved).
     Tokens alias the shared design system at plugins/ravenclaude-core/
     dashboard-assets/shared-tokens.css. */
  --bg: var(--rc-bg);
  --surface: var(--rc-surface);
  --surface-2: var(--rc-surface-2);
  --border: var(--rc-border);
  --text: var(--rc-text);
  --muted: var(--rc-muted);
  --accent: var(--rc-gold);
  --accent-dim: var(--rc-gold);
  --accent-2: var(--rc-gold-soft);
  --accent-soft: rgba(168, 136, 46, 0.14);
  --accent-glow: rgba(168, 136, 46, 0.28);
  /* Semantic status colors — kept SEPARATE from the gold brand accent so
     "allow / ok / safe" reads green, "ask" amber, "deny" red, regardless of
     the navigation's gold theme. */
  --ok: var(--rc-ok);
  --ok-soft: rgba(31, 122, 63, 0.10);
  --warn: var(--rc-warn);
  --danger: var(--rc-danger);
  --font-sans: var(--rc-font-sans);
  --font-display: var(--rc-font-sans);
  --font-mono: var(--rc-font-mono);
  --radius: var(--rc-radius);
  --radius-sm: var(--rc-radius-sm);
}
@media (prefers-reduced-motion: reduce) {
  * { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; }
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  /* Faint gold hero glow + the site's subtle graph-paper grid texture. */
  background:
    radial-gradient(60% 45% at 55% -8%, rgba(201, 162, 73, 0.06), transparent 60%),
    var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  font-size: 15px;
  line-height: 1.5;
  min-height: 100vh;
}
h1, h2, h3 { font-family: var(--font-display); font-weight: 600; letter-spacing: -0.02em; }
::selection { background: var(--accent); color: #000; }
.page-header {
  position: relative;
  padding: 24px 32px 0;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}
/* Gold hairline along the top edge — the site's signature section accent. */
.page-header::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, var(--accent) 50%, transparent 100%);
}
.brand-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 4px 0;
}
.brand-mark {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  /* Inline raven SVG: body uses currentColor (dark on light, light on dark),
     bolt is the gold accent. A PNG fallback is sized the same. */
  color: var(--text);
  filter: drop-shadow(0 0 6px var(--accent-glow));
}
.brand-mark svg,
.brand-mark img {
  width: 28px;
  height: 28px;
  display: block;
  object-fit: contain;
}
.page-header h1 {
  margin: 0;
  font-size: 22px;
  letter-spacing: -0.02em;
}
.page-header .plugin-name {
  color: var(--accent);
  font-family: var(--font-mono);
  font-weight: 500;
}
.page-header .page-desc {
  color: var(--muted);
  font-size: 13px;
  margin: 0 0 16px 0;
  max-width: 800px;
}
.tab-bar {
  display: flex;
  gap: 4px;
  margin-top: 8px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  /* Prevent line-wrapping that would break the tablist role */
  flex-wrap: nowrap;
  /* Hide scrollbar on browsers that support it; keeps it functional */
  scrollbar-width: none;
}
.tab-bar::-webkit-scrollbar { display: none; }
.tab-btn {
  background: transparent;
  border: none;
  color: var(--muted);
  font: inherit;
  padding: 10px 16px;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-weight: 500;
  /* Prevent flex from shrinking tabs below their natural width when the bar overflows */
  flex-shrink: 0;
  white-space: nowrap;
}
.tab-btn[aria-selected="true"] {
  color: var(--text);
  border-bottom-color: var(--accent);
}
.tab-btn:hover { color: var(--text); }
.tab-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 4px; }
/* Visual-only section grouping inside the tablist. Both are role="presentation"
   + aria-hidden, so they never enter the a11y tree or the roving-tabindex set. */
.tab-section-label {
  align-self: center;
  flex-shrink: 0;
  white-space: nowrap;
  /* No opacity: --muted (#9aa3b2) on the Raven dark --bg (#07080a) is ~7.7:1,
     which passes WCAG AA for this 11px non-large text; an earlier opacity:0.7
     blended it down below AA. Keep the muted look via the token, not a blend. */
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0 6px 0 8px;
  user-select: none;
}
.tab-divider {
  flex-shrink: 0;
  width: 1px;
  align-self: stretch;
  margin: 6px 2px;
  background: var(--border);
}
/* ── Two-tier nav: top-level CATEGORIES reveal their pages (website-style) ── */
.cat-bar {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin: 4px 0 2px;
}
.cat-btn {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--muted);
  font: inherit;
  font-family: var(--font-display, inherit);
  font-weight: 600;
  font-size: 13px;
  letter-spacing: -0.01em;
  padding: 7px 15px;
  border-radius: 999px;
  cursor: pointer;
  white-space: nowrap;
}
.cat-btn:hover { color: var(--text); border-color: var(--accent-2, var(--accent)); }
.cat-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.cat-btn[aria-pressed="true"] {
  color: #000;
  background: var(--accent);
  border-color: var(--accent);
  box-shadow: 0 0 16px var(--accent-glow, transparent);
}
/* Only the active category's page tabs are shown in the tablist. */
.tab-bar .tab-btn:not(.in-cat) { display: none; }
.header-about-link { white-space: nowrap; }
.about-wrap { max-width: 760px; }
.about-lead { font-size: 15px; color: var(--text); line-height: 1.6; }
.about-note { color: var(--muted); font-size: 13px; }
.about-cats { line-height: 1.7; padding-left: 20px; margin: 8px 0 0; }
.about-cats li { margin: 4px 0; }
.category-intro {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 16px;
  margin-bottom: 16px;
}
.category-intro p { margin: 0; font-size: 13px; color: var(--muted); line-height: 1.5; }
.tab-panel { display: none; padding: 24px 32px; }
.tab-panel.active { display: block; }
.stub {
  background: var(--surface);
  border: 1px dashed var(--border);
  border-radius: var(--radius);
  padding: 32px;
  text-align: center;
}
.stub h2 { margin-top: 0; color: var(--muted); }
.stub p { color: var(--muted); }
.stub code { background: var(--surface-2); padding: 2px 6px; border-radius: 4px; font-size: 13px; }

/* Settings tab layout */
.settings-layout {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 24px;
  align-items: start;
}
@media (max-width: 900px) {
  .settings-layout { grid-template-columns: 1fr; }
}
/* Phone widths: the 32px side padding left ~311px of content on a 375px screen.
   Tighten the page/panel/modal chrome so content keeps its breathing room. */
@media (max-width: 600px) {
  .page-header { padding: 16px 16px 0; }
  .tab-panel { padding: 16px 16px; }
  .stub { padding: 16px; }
  .modal-backdrop { padding: 12px; }
  .modal { padding: 16px; }
}
.preset-bar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 20px;
  margin-bottom: 16px;
}
.preset-bar h3 { margin: 0 0 4px 0; font-size: 14px; }
.preset-bar p { margin: 0 0 12px 0; color: var(--muted); font-size: 13px; }
.preset-buttons { display: flex; gap: 8px; flex-wrap: wrap; }
.preset-btn {
  background: var(--surface-2);
  color: var(--text);
  border: 1px solid var(--border);
  border-left-width: 3px;
  padding: 8px 16px;
  border-radius: 6px;
  font: inherit;
  cursor: pointer;
  font-weight: 500;
}
.preset-btn:hover { border-color: var(--accent); }
.preset-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
/* Left-border tint matching the level color for visual link */
.preset-btn.preset-deny { border-left-color: var(--danger); }
.preset-btn.preset-ask { border-left-color: var(--warn); }
.preset-btn.preset-allow { border-left-color: var(--ok); }
/* Design check-ins toggle — a behavioral flag, visually distinct from the
   permission cards below (left accent edge, switch on the right). */
.design-checkins-bar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: var(--radius);
  padding: 14px 16px;
  margin-bottom: 16px;
}
.design-checkins-bar .dc-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}
.design-checkins-bar h3 { margin: 0 0 4px 0; font-size: 14px; }
.design-checkins-bar .dc-text p { margin: 0; color: var(--muted); font-size: 13px; line-height: 1.5; }
.dc-switch { position: relative; flex: 0 0 auto; cursor: pointer; }
.dc-switch input { position: absolute; opacity: 0; width: 0; height: 0; }
.dc-track {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  border-radius: 12px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  transition: background 0.15s ease;
}
.dc-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--muted);
  transition:
    transform 0.15s ease,
    background 0.15s ease;
}
.dc-switch input:checked + .dc-track { background: var(--accent); border-color: var(--accent); }
.dc-switch input:checked + .dc-track .dc-thumb { transform: translateX(20px); background: var(--bg); }
.dc-switch input:focus-visible + .dc-track { outline: 2px solid var(--accent); outline-offset: 2px; }
.dc-state { margin: 10px 0 0 0; font-weight: 600; font-size: 12.5px; color: var(--text); }
/* Command review (the Thing) — T1 preview panel + disabled per-category toggle. */
.thing-preview {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--warn);
  border-radius: var(--radius);
  padding: 14px 16px;
  margin-bottom: 16px;
}
.thing-preview-head h3 {
  margin: 0 0 8px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.thing-preview p {
  margin: 0 0 8px;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.55;
}
.thing-preview p:last-child { margin-bottom: 0; }
.thing-preview-note { color: var(--text) !important; }
.thing-preview a { color: var(--accent); }
.thing-aka { color: var(--muted); font-weight: 400; }
.preview-pill {
  display: inline-block;
  font-size: 10.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--bg);
  background: var(--warn);
  padding: 1px 7px;
  border-radius: 10px;
}
.cat-thing-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed var(--border);
}
.cat-thing-label { font-size: 13px; color: var(--muted); }
.dc-switch.thing-switch { cursor: not-allowed; opacity: 0.55; }
.dc-switch.thing-switch input { cursor: not-allowed; }
.dc-switch.thing-switch-live { cursor: pointer; }
.cat-thing-row.cat-thing-live .cat-thing-label { color: var(--text); }
.cat-thing-cost { font-size: 11px; color: var(--muted); white-space: nowrap; }
/* Command-review panel — global per-seat model + confidence config (T3). */
.command-review-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: var(--radius);
  padding: 16px 20px;
  margin: 0 0 16px;
}
.command-review-panel .crp-head h3 { margin: 0 0 4px 0; font-size: 14px; }
.command-review-panel .crp-sub { margin: 0 0 12px 0; color: var(--muted); font-size: 12.5px; line-height: 1.5; }
.crp-hydrated {
  display: inline-block;
  margin: 0 0 12px 0;
  font-size: 11.5px;
  color: var(--accent);
}
.crp-hydrated code {
  font-family: var(--font-mono);
  font-size: 11px;
  background: var(--surface-2);
  padding: 1px 5px;
  border-radius: 4px;
}
.crp-seats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}
.cr-seat-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.cr-seat-name { font-size: 13px; color: var(--text); }
.cr-seat-select,
.crp-threshold input {
  background: var(--bg);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 12.5px;
}
.crp-threshold {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed var(--border);
}
.crp-threshold-label { font-size: 13px; color: var(--text); }
.crp-threshold input { width: 72px; }
.crp-hint { font-size: 11px; color: var(--muted); }
/* MCP server allowlist (§MCP identity) — a wide text field, stacked label/input/hint. */
.crp-mcp-allow {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed var(--border);
}
.crp-mcp-allow-label { font-size: 13px; color: var(--text); }
.crp-mcp-allow-opt { font-size: 11px; color: var(--muted); font-weight: normal; }
.crp-mcp-allow-input {
  background: var(--bg);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 5px 8px;
  font-size: 12.5px;
  font-family: var(--mono, monospace);
}
.crp-mcp-allow .crp-hint code { font-size: 10.5px; }
/* gate_floor — headline comfort knob (segmented control + always-visible note). */
.crp-gate-floor {
  margin: 4px 0 16px;
  padding-bottom: 14px;
  border-bottom: 1px dashed var(--border);
}
.crp-gate-floor-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 8px;
}
.seg-control.gate-floor-seg { margin-bottom: 8px; }
.seg-control input[type="radio"]:checked + .seg-label.gate-floor-medium { background: var(--warn); color: var(--bg); }
.seg-control input[type="radio"]:checked + .seg-label.gate-floor-extreme { background: var(--danger); color: white; }
.crp-gate-floor-note { margin: 0; font-size: 11.5px; color: var(--muted); line-height: 1.5; }
/* Per-tier advanced expansion — tier cards with seat checkboxes + threshold. */
.tier-details { margin: 14px 0 0; }
.tier-list { padding: 12px 8px 8px; }
.tier-intro { margin: 0 0 12px; font-size: 12px; color: var(--muted); line-height: 1.5; }
.tier-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px 14px;
  margin-bottom: 10px;
}
.tier-card-head { margin-bottom: 8px; }
.tier-card-title { font-size: 13px; font-weight: 600; color: var(--text); }
.tier-seats { display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 10px; }
.tier-seat {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  color: var(--text);
  cursor: pointer;
}
.tier-seat input[type="checkbox"] { accent-color: var(--accent); cursor: pointer; }
.tier-seat input[type="checkbox"]:disabled { cursor: not-allowed; }
.tier-seat:has(input:disabled) { color: var(--muted); cursor: default; }
.tier-seat-req {
  font-size: 9.5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--accent);
}
.tier-threshold {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.tier-threshold-label { font-size: 12px; color: var(--muted); }
.tier-threshold-input {
  width: 72px;
  background: var(--bg);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 12.5px;
}
.tier-caption { margin: 0; font-size: 11.5px; color: var(--muted); line-height: 1.45; }
.tier-low-note {
  margin: 12px 0 0;
  font-size: 11.5px;
  color: var(--muted);
  line-height: 1.5;
}
/* ── Consolidated command-review block (replaces separate thing-preview +
   command-review-panel; rendered once above category cards) ─────────── */
.command-review-block {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--warn);
  border-radius: var(--radius);
  padding: 14px 16px;
  margin-bottom: 16px;
}
.crb-head { margin-bottom: 12px; }
.crb-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}
.crb-title-row h3 {
  margin: 0;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.crb-master-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.crb-master-label {
  font-size: 13px;
  color: var(--muted);
  cursor: pointer;
}
.crb-master-state {
  margin: 6px 0 0;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text);
}
.command-review-block p {
  margin: 0 0 8px;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.55;
}
.command-review-block p:last-of-type { margin-bottom: 0; }
.command-review-block a { color: var(--accent); }
.crb-cost-warn { color: var(--warn); }
.crb-live-note { color: var(--text) !important; }
/* Per-category read-only summary grid */
.crb-summary-section {
  margin: 12px 0;
  padding: 10px 0;
  border-top: 1px dashed var(--border);
  border-bottom: 1px dashed var(--border);
}
.crb-summary-title {
  display: block;
  font-size: 11.5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
  margin-bottom: 8px;
}
.cr-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 6px 8px;
}
.cr-summary-cell {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 3px 4px;
  border-radius: 4px;
}
.cr-summary-cell .cr-summary-label {
  font-size: 11px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}
.cr-summary-micro {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: var(--muted);
  white-space: nowrap;
}
/* Advanced details wrapper */
.crb-advanced { margin-top: 10px; }
.crb-advanced-body { padding: 10px 4px 4px; }
.crb-adv-sub { margin: 0 0 12px; color: var(--muted); font-size: 12.5px; line-height: 1.5; }
/* ── Scales-of-justice icon — 3 effective review states ──────────── */
.review-scales-icon { flex-shrink: 0; display: inline-block; vertical-align: middle; }
/* reviewed: master on AND per-category thing on */
.review-scales-icon[data-review-state="reviewed"] {
  color: var(--accent);
}
/* off: per-category thing off (regardless of master) */
.review-scales-icon[data-review-state="off"] {
  color: var(--border);
}
/* paused: thing on but master off — greyed with dashed outline affordance */
.review-scales-icon[data-review-state="paused"] {
  color: var(--muted);
  outline: 1.5px dashed var(--muted);
  border-radius: 3px;
}
/* Micro-label matching each state */
.cr-summary-micro[data-state="reviewed"] { color: var(--accent); }
.cr-summary-micro[data-state="off"] { color: var(--border); }
.cr-summary-micro[data-state="paused"] { color: var(--muted); }
/* Card-level scales icon (in cat-thing-row) */
.cat-thing-scales { display: inline-flex; align-items: center; }
/* The "★ Recommended" preset gets a stronger visual to mark it as primary */
.preset-btn.preset-recommended {
  background: var(--accent);
  color: var(--bg);
  border-left-color: var(--accent);
  font-weight: 600;
}
.preset-btn.preset-recommended:hover {
  background: var(--accent-dim);
  border-color: var(--accent);
}
.cat-group {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 20px 8px;
  margin: 0 0 16px;
}
.cat-group legend {
  color: var(--accent);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
  padding: 0 8px;
}
.cat-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 16px;
  padding: 18px 0 24px;
  border-bottom: 1px solid var(--border);
  align-items: center;
}
@media (max-width: 1100px) {
  .cat-row { grid-template-columns: 1fr; }
  .cat-row .seg-control { justify-self: start; }
}
.cat-row:last-child { border-bottom: none; }
.cat-title-row { display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }
.cat-title { font-weight: 500; font-size: 14px; }
.cat-desc { font-size: 12px; color: var(--muted); max-width: 480px; }
.info-btn {
  background: var(--surface-2);
  color: var(--muted);
  border: 1px solid var(--border);
  width: 18px;
  height: 18px;
  font-size: 11px;
  font-weight: 700;
  border-radius: 50%;
  cursor: pointer;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}
.info-btn:hover { color: var(--accent); border-color: var(--accent); }
.info-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

/* Segmented control (radiogroup with pill buttons) */
.seg-control {
  display: inline-flex;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 2px;
  gap: 0;
  flex-wrap: nowrap;
}
.seg-control input[type="radio"] {
  position: absolute;
  opacity: 0;
  width: 1px;
  height: 1px;
  overflow: hidden;
}
.seg-label {
  position: relative;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6px 12px 10px;
  font-size: 12.5px;
  font-weight: 500;
  color: var(--muted);
  border-radius: 6px;
  cursor: pointer;
  transition: background 80ms ease, color 80ms ease;
  user-select: none;
  min-width: 82px;
  text-align: center;
  white-space: nowrap;
}
.rec-badge {
  position: absolute;
  bottom: -16px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 9.5px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--accent);
  background: transparent;
  white-space: nowrap;
  pointer-events: none;
}
@media (prefers-color-scheme: light) {
  .rec-badge { color: var(--accent-dim); }
}
.seg-control input[type="radio"]:checked + .seg-label {
  background: var(--accent);
  color: var(--bg);
  font-weight: 600;
}
/* Restrictive levels get warning-tinted selection */
.seg-control input[type="radio"]:checked + .seg-label.seg-deny { background: var(--danger); color: white; }
.seg-control input[type="radio"]:checked + .seg-label.seg-ask { background: var(--warn); color: var(--bg); }
.seg-control input[type="radio"]:checked + .seg-label.seg-allow { background: var(--ok); color: #04210f; }
.seg-control input[type="radio"]:checked + .seg-label.seg-always-ask { background: var(--warn); color: var(--bg); }
.seg-control input[type="radio"]:checked + .seg-label.seg-autopilot { background: var(--warn); color: var(--bg); }
.seg-control input[type="radio"]:focus-visible + .seg-label {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
.seg-label:hover { color: var(--text); }

/* Per-pattern controls (collapsible details under each category row).
 * Visually deliberately quiet — the dominant control is the category-level
 * segmented control; the per-pattern overrides are an "expand for advanced"
 * affordance. */
.pattern-details {
  margin: 18px 0 8px 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  overflow: hidden;
}
.pattern-summary {
  cursor: pointer;
  padding: 10px 14px;
  font-size: 12.5px;
  color: var(--muted);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  user-select: none;
  list-style: none;
  min-height: 36px;
  border-radius: 6px;
  transition: opacity 80ms ease, color 80ms ease, background-color 80ms ease;
}
.pattern-summary::-webkit-details-marker { display: none; }
.pattern-summary::before {
  content: "▸";
  color: var(--muted);
  font-size: 11px;
  display: inline-block;
  width: 12px;
  margin-right: 6px;
}
.pattern-details[open] > .pattern-summary::before { content: "▾"; color: var(--accent); }
.pattern-details[open] > .pattern-summary { opacity: 1; }
.pattern-summary:hover { color: var(--text); opacity: 1; }
.pattern-summary-text { flex: 1; }
.pattern-count {
  font-family: var(--font-mono);
  font-size: 10.5px;
  color: var(--muted);
  margin-left: 2px;
}
.pattern-override-count {
  font-size: 10.5px;
  color: var(--muted);
  font-family: var(--font-mono);
  white-space: nowrap;
  opacity: 0.75;
}
.pattern-override-count.has-overrides {
  color: var(--accent);
  font-weight: 600;
  opacity: 1;
}
.pattern-list {
  max-height: 360px;
  overflow-y: auto;
  padding: 12px 8px 8px;
  border-top: 1px dotted var(--border);
  background: var(--surface);
  border-radius: 4px;
}
/* Per-pattern row: 3 columns — [code + ? meta] [detail] [seg-control] */
.pattern-row {
  display: grid;
  grid-template-columns: minmax(180px, 240px) 1fr auto;
  gap: 14px;
  padding: 4px 6px;
  border-bottom: 1px dotted var(--border);
  align-items: center;
}
.pattern-row:last-child { border-bottom: none; }
.pattern-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
.pattern-name {
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--text);
  background: transparent;
  padding: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
  flex: 1 1 auto;
}
.pattern-detail {
  font-size: 11.5px;
  color: var(--muted);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
@media (max-width: 1200px) {
  .pattern-detail { display: none; }
  .pattern-row { grid-template-columns: 1fr auto; }
}
.info-btn-pattern {
  width: 16px;
  height: 16px;
  font-size: 10px;
  flex-shrink: 0;
}
.info-btn-section {
  width: 16px;
  height: 16px;
  font-size: 10px;
  margin-left: 6px;
  vertical-align: middle;
}

/* Per-permission, per-layer overrides (v0.19.0): each permission row carries
 * three compact <select>s — User / Local / Project. "Default" (value
 * "inherit") defers to the category-wide layer value; any other value
 * overrides just that one permission at just that one layer. A select that
 * holds a non-default value gets the .ov-set tint so overrides are scannable. */
.pattern-layers {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-self: end;
}
.ov-layer {
  display: inline-flex;
  flex-direction: column;
  gap: 2px;
  font-size: 9.5px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted);
}
.ov-layer-name { padding-left: 2px; }
.ov-select {
  font: inherit;
  font-size: 11.5px;
  text-transform: none;
  letter-spacing: 0;
  color: var(--text);
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 3px 6px;
  cursor: pointer;
  min-width: 72px;
}
.ov-select:hover { border-color: var(--accent); }
.ov-select:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
.ov-select.ov-set { border-color: var(--accent); color: var(--accent); font-weight: 600; }
@media (max-width: 1200px) {
  .pattern-layers { justify-self: start; }
}

/* Danger Zone — modeled on GitHub's destructive-actions section.
 * Red border, prominent red title, each pattern as a card with the rule
 * description on the left and a Blocked/Allowed toggle on the right. */
.danger-zone {
  border: 1px solid var(--danger);
  border-radius: var(--radius);
  background: var(--surface);
  margin: 24px 0 0;
  overflow: hidden;
}
.danger-zone-header {
  padding: 14px 18px 12px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}
.danger-zone-title {
  margin: 0;
  color: var(--danger);
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}
.danger-zone-title .info-btn-section {
  border-color: var(--danger);
  color: var(--danger);
}
.danger-zone-title .info-btn-section:hover {
  background: rgba(239, 68, 68, 0.1);
}
.danger-zone-subtitle {
  margin: 6px 0 0;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
  max-width: 720px;
}
/* Honest "what this is / isn't" note at the top of the Danger Zone. */
.danger-zone-note {
  margin: 12px 0 0;
  padding: 12px 14px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  max-width: 720px;
}
.danger-zone-note p {
  margin: 0 0 8px;
  font-size: 13px;
  color: var(--text);
  line-height: 1.55;
}
.danger-zone-note p:last-child { margin-bottom: 0; }
.danger-zone-note .danger-zone-note-maint { color: var(--muted); font-size: 12.5px; }
.danger-zone-note code {
  background: var(--bg);
  padding: 1px 5px;
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 11.5px;
}
.danger-zone-note a { color: var(--accent); }
.danger-zone-list { padding: 0; }
.danger-zone-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 16px;
  padding: 14px 18px;
  border-top: 1px solid var(--border);
  align-items: center;
}
.danger-zone-row:first-child { border-top: none; }
.danger-zone-info { min-width: 0; }
.danger-zone-row-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  min-width: 0;
}
.danger-zone-row-title .info-btn-pattern {
  border-color: var(--danger);
  color: var(--danger);
}
.danger-zone-row-title .info-btn-pattern:hover {
  background: rgba(239, 68, 68, 0.1);
}
.danger-zone-pattern {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  background: transparent;
  padding: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}
.danger-zone-row-desc {
  margin: 0;
  font-size: 12.5px;
  color: var(--muted);
  line-height: 1.45;
  max-width: 640px;
}

/* The Blocked / Allowed toggle */
.danger-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border: 1px solid var(--danger);
  border-radius: 6px;
  color: var(--danger);
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
  background: transparent;
  white-space: nowrap;
  user-select: none;
  transition: background 80ms ease, color 80ms ease, border-color 80ms ease;
}
.danger-toggle:hover { background: rgba(239, 68, 68, 0.1); }
.danger-toggle input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  pointer-events: none;
  width: 1px;
  height: 1px;
}
.danger-toggle .danger-toggle-off { display: none; }
.danger-toggle:has(input:not(:checked)) {
  border-color: var(--border);
  color: var(--muted);
  background: transparent;
}
.danger-toggle:has(input:not(:checked)) .danger-toggle-on { display: none; }
.danger-toggle:has(input:not(:checked)) .danger-toggle-off { display: inline; }
.danger-toggle:has(input:not(:checked)):hover {
  border-color: var(--warn);
  color: var(--warn);
  background: rgba(251, 191, 36, 0.08);
}
.danger-zone-row:has(.sec-deny-checkbox:not(:checked)) .danger-zone-pattern {
  text-decoration: line-through;
  color: var(--muted);
}
.danger-zone-row:has(.sec-deny-checkbox:not(:checked)) .danger-zone-row-desc {
  opacity: 0.6;
}

/* Per-pattern info modal (smaller than the category modal) */
.modal.pattern-modal { max-width: 480px; }
.modal.pattern-modal h2 {
  font-family: var(--font-mono);
  font-size: 15px;
  word-break: break-all;
}

/* Modal (info-icon popup) */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 24px;
}
.modal-backdrop.open { display: flex; }
.modal {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  max-width: 640px;
  width: 100%;
  max-height: 85vh;
  overflow: auto;
  padding: 24px;
}
.modal h2 { margin-top: 0; font-size: 18px; color: var(--accent); }
.modal h3 { font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); margin: 20px 0 8px; }
.modal .modal-subhead { color: var(--muted); font-size: 13px; margin: 4px 0 0; }
.modal p { font-size: 14px; line-height: 1.55; margin: 0 0 4px; }
.modal .example-list {
  margin: 4px 0 0;
  padding-left: 18px;
  font-family: var(--font-mono);
  font-size: 12.5px;
  line-height: 1.7;
}
.modal .example-list li { color: var(--text); margin-bottom: 2px; }
.modal .example-list li::marker { color: var(--accent); }
.modal .rec-rows { display: flex; flex-direction: column; gap: 8px; margin: 6px 0 0; }
.modal .rec-row {
  background: var(--surface-2);
  border-left: 3px solid var(--accent);
  padding: 8px 12px;
  border-radius: 4px;
}
.modal .rec-context {
  display: block;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--accent);
  margin-bottom: 2px;
}
.modal .rec-text { font-size: 13px; line-height: 1.55; color: var(--text); }
.modal .close-btn {
  float: right;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text);
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  padding: 0;
}
.modal .close-btn:hover { border-color: var(--accent); color: var(--accent); }

/* Global-default row gets a slight surface emphasis */
.global-default {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: var(--radius);
  padding: 16px 20px;
  margin-bottom: 16px;
}
.global-default .cat-meta { padding-right: 16px; }

/* Live YAML preview pane */
.yaml-preview {
  position: sticky;
  top: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}
.yaml-preview h3 {
  margin: 0;
  padding: 12px 16px;
  background: var(--surface-2);
  border-bottom: 1px solid var(--border);
  font-size: 13px;
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.yaml-preview pre {
  margin: 0;
  padding: 16px;
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.6;
  color: var(--text);
  max-height: 60vh;
  overflow: auto;
  white-space: pre;
}
.yaml-primary-action {
  padding: 14px 14px 8px;
  border-top: 1px solid var(--border);
  background: var(--surface);
}
.btn-primary {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 16px;
  background: var(--accent);
  color: var(--bg);
  font-weight: 600;
  font-size: 14px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
.btn-primary:hover { background: var(--accent-dim); }
.btn-primary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.btn-primary[disabled] { opacity: 0.5; cursor: not-allowed; }
.btn-primary .btn-sub {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 400;
  opacity: 0.85;
  margin-top: 2px;
}
.primary-help {
  margin: 8px 0 0;
  font-size: 11px;
  color: var(--muted);
  text-align: center;
}
.primary-help.muted { color: var(--warn); }
.primary-help.warn { color: var(--warn); font-weight: 600; }
.primary-help code {
  background: var(--surface-2);
  padding: 1px 5px;
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 11px;
}
.yaml-alt-actions {
  border-top: 1px solid var(--border);
  background: var(--surface-2);
}
.yaml-alt-actions summary {
  padding: 8px 14px;
  font-size: 12px;
  color: var(--muted);
  cursor: pointer;
  user-select: none;
}
.yaml-alt-actions summary:hover { color: var(--text); }
.yaml-alt-actions[open] summary { border-bottom: 1px solid var(--border); color: var(--text); }
.yaml-actions {
  display: flex;
  gap: 8px;
  padding: 12px;
  background: var(--surface-2);
}
.yaml-status {
  color: var(--muted);
  font-weight: 400;
  font-size: 12px;
}
.yaml-status.status-unsaved { color: var(--warn); }
.yaml-status.status-saved { color: var(--ok); }
.yaml-status.status-error { color: var(--danger); }
/* Apply-error inline block — shown when YAML saved but settings.json translation failed */
.apply-error-block {
  margin: 8px 0 0;
  padding: 10px 12px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid var(--danger);
  border-radius: var(--radius);
  font-size: 12px;
  color: var(--danger);
  text-align: left;
}
.apply-error-block strong { font-weight: 700; }
.apply-error-detail {
  margin: 6px 0 4px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text);
  background: var(--surface-2);
  padding: 6px 8px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-break: break-word;
}
.apply-error-hint {
  margin: 4px 0 0;
  color: var(--muted);
  font-size: 11px;
}
.yaml-connected-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px 10px;
  background: var(--surface-2);
  font-size: 12px;
}
.connected-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--accent);
}
.connected-pill code {
  background: transparent;
  font-family: var(--font-mono);
  color: var(--text);
}
.connected-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 6px var(--accent);
}
.link-btn {
  background: none;
  border: none;
  color: var(--muted);
  font: inherit;
  font-size: 12px;
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
}
.link-btn:hover { color: var(--danger); }
.yaml-help {
  padding: 8px 12px 12px;
  margin: 0;
  font-size: 11px;
  color: var(--muted);
  border-top: 1px solid var(--border);
}
.yaml-help code {
  background: transparent;
  font-family: var(--font-mono);
  color: var(--text);
}
.btn {
  background: var(--accent);
  color: var(--bg);
  border: none;
  padding: 8px 14px;
  border-radius: 6px;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  flex: 1;
}
.btn:hover { background: var(--accent-dim); }
.btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.btn.secondary {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text);
  font-weight: 500;
}
.btn.secondary:hover { border-color: var(--accent); color: var(--accent); }

.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%) translateY(40px);
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--accent);
  border-radius: 6px;
  padding: 10px 18px;
  font-size: 13px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 160ms ease, transform 160ms ease;
  z-index: 1000;
}
.toast.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

footer.page-footer {
  padding: 16px 32px;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 12px;
  text-align: center;
  background: var(--surface);
}
footer.page-footer a { color: var(--accent); text-decoration: none; }
footer.page-footer a:hover { text-decoration: underline; }

/* ── v5 Per-layer expandable cards ──────────────────────────────── */
.cat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--rc-radius-lg);
  margin: 0 0 10px;
  overflow: hidden;
  box-shadow: var(--rc-shadow-sm);
  transition: box-shadow 0.18s ease, border-color 0.18s ease;
}
.cat-card:hover {
  box-shadow: var(--rc-shadow-md);
}
.cat-card[open] {
  border-color: var(--accent);
}
.cat-card-summary {
  display: grid;
  grid-template-columns: 20px 1fr auto auto auto;
  gap: 10px;
  padding: 14px 16px;
  cursor: pointer;
  align-items: center;
  list-style: none;
  user-select: none;
  min-height: 52px;
  transition: background 80ms ease;
}
.cat-card-summary::-webkit-details-marker { display: none; }
.cat-card-summary:hover { background: var(--surface-2); }
.cat-card[open] > .cat-card-summary { background: var(--surface-2); border-bottom: 1px solid var(--border); }
.cat-card-arrow {
  color: var(--muted);
  font-size: 11px;
  transition: transform 120ms ease;
  display: inline-block;
  line-height: 1;
}
.cat-card[open] > .cat-card-summary .cat-card-arrow {
  transform: rotate(90deg);
  color: var(--accent);
}
.cat-card-title-group {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}
.cat-card-title {
  font-weight: 500;
  font-size: 14px;
  white-space: nowrap;
}
.cat-card-desc {
  font-size: 12px;
  color: var(--muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
/* Effective badge: small pill on the right of the summary */
.cat-card-badge {
  white-space: nowrap;
  font-size: 12px;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--muted);
  min-width: 80px;
  text-align: center;
}
.cat-card-badge.badge-allow { border-color: var(--ok); color: var(--ok); background: var(--ok-soft); }
.cat-card-badge.badge-ask { border-color: var(--warn); color: var(--warn); background: rgba(251,191,36,0.08); }
.cat-card-badge.badge-deny { border-color: var(--danger); color: var(--danger); background: rgba(239,68,68,0.08); }
.cat-card-badge.badge-inherit { border-color: var(--border); color: var(--muted); }

/* Compact command-review toggle in the always-visible card header */
.cat-hdr-thing {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 0 0 auto;
  /* Stop the summary's user-select: none from swallowing pointer events on
     the switch — the JS click isolation handles the details-toggle prevention. */
  user-select: none;
}
/* Dimmed when the category is not yet live (preview state) */
.cat-hdr-thing:not(.cat-hdr-thing-live) { opacity: 0.55; }
.cat-hdr-thing:not(.cat-hdr-thing-live) .cat-hdr-switch { cursor: not-allowed; }
/* The scales icon sits to the left of the switch; keep it tightly packed */
.cat-hdr-thing .cat-thing-scales { display: inline-flex; align-items: center; }
/* Preview pill inside the header is slightly smaller than the body variant */
.cat-hdr-thing .preview-pill { font-size: 9.5px; padding: 1px 5px; }

/* Body of the expanded card */
.cat-card-body {
  padding: 12px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* Project-allow caution banner */
.cat-project-warn {
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid var(--warn);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 12px;
  color: var(--warn);
  font-weight: 500;
  margin-bottom: 4px;
}
.cat-project-warn .warn-icon { margin-right: 4px; }

/* Layer row: label + 4-option radiogroup */
.layer-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 0;
  border-bottom: 1px dotted var(--border);
}
.layer-row:last-child { border-bottom: none; }
.layer-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
  min-width: 56px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.layer-radios {
  display: inline-flex;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 2px;
  gap: 0;
}
.layer-radios input[type="radio"] {
  position: absolute;
  opacity: 0;
  width: 1px;
  height: 1px;
  overflow: hidden;
}
.layer-opt {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 11px;
  font-size: 12px;
  font-weight: 500;
  color: var(--muted);
  border-radius: 5px;
  cursor: pointer;
  transition: background 80ms ease, color 80ms ease;
  user-select: none;
  min-width: 58px;
  text-align: center;
  white-space: nowrap;
}
.layer-radios input[type="radio"]:checked + .layer-opt { background: var(--accent); color: var(--bg); font-weight: 600; }
.layer-radios input[type="radio"]:checked + .layer-opt-deny { background: var(--danger); color: white; }
.layer-radios input[type="radio"]:checked + .layer-opt-ask { background: var(--warn); color: var(--bg); }
.layer-radios input[type="radio"]:checked + .layer-opt-inherit { background: var(--surface); color: var(--text); }
.layer-radios input[type="radio"]:focus-visible + .layer-opt {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
.layer-opt:hover { color: var(--text); }

/* Layers info modal */
.modal.layers-modal { max-width: 520px; }
.modal.layers-modal h2 { color: var(--accent); }
.modal.layers-modal .layer-file-row {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 8px 12px;
  align-items: start;
  margin-bottom: 8px;
}
.modal.layers-modal .layer-file-label {
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--accent);
  padding-top: 2px;
}
.modal.layers-modal .layer-file-desc {
  font-size: 13px;
  color: var(--text);
  line-height: 1.5;
}
.modal.layers-modal .layer-file-desc code {
  background: var(--surface-2);
  padding: 1px 5px;
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 11.5px;
}

/* ── Install & Update tab ───────────────────────────────────────── */
.install-layout {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 820px;
}
.install-guide,
.install-commands,
.install-oneclick {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
}
.install-oneclick {
  border-left: 3px solid var(--accent);
}
.install-guide h2 { margin: 0 0 8px; font-size: 18px; }
.install-guide h3,
.install-commands h3,
.install-oneclick h3 {
  margin: 16px 0 6px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--accent);
}
.install-oneclick .oneclick-head h3 { margin: 0; }
.install-commands h3 { margin-top: 0; }
.install-guide p,
.install-commands-sub {
  margin: 0 0 6px;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.55;
}
.install-pillar {
  border-left: 3px solid var(--accent);
  background: var(--surface-2);
  padding: 10px 12px;
  border-radius: 0 var(--radius) var(--radius) 0;
  margin: 4px 0 6px;
}
.install-cross-tool {
  border-left: 3px solid var(--warn);
  background: var(--surface-2);
  padding: 10px 12px;
  border-radius: 0 var(--radius) var(--radius) 0;
  margin: 14px 0 6px;
  font-size: 12.5px;
  line-height: 1.55;
}
.install-prereqs,
.install-wiring,
.install-plugin-list {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text);
}
.install-prereqs li::marker,
.install-wiring li::marker,
.install-plugin-list li::marker { color: var(--accent); }
.install-intro {
  font-size: 13.5px;
  line-height: 1.55;
  margin: 4px 0 14px;
  color: var(--text);
}
.install-explain {
  font-size: 13px;
  line-height: 1.6;
  color: var(--text);
  margin: 6px 0 12px;
}
.install-situation {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0;
  margin: 10px 0 14px;
  background: var(--surface-2);
  overflow: hidden;
}
.install-situation > summary {
  cursor: pointer;
  padding: 12px 14px;
  font-size: 13.5px;
  list-style: none;
  position: relative;
  user-select: none;
}
.install-situation > summary::before {
  content: "\\25B8  ";
  color: var(--muted);
}
.install-situation[open] > summary::before { content: "\\25BE  "; }
.install-situation[open] > summary {
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}
.install-situation-body { padding: 12px 16px 16px; }
.install-steplist {
  margin: 4px 0 8px;
  padding-left: 22px;
  font-size: 13px;
  line-height: 1.6;
}
.install-steplist > li { margin: 10px 0; }
.install-steplist > li::marker {
  color: var(--accent);
  font-weight: 700;
}
.install-after {
  margin-top: 12px;
  padding: 8px 12px;
  background: var(--ok-soft, rgba(34, 197, 94, 0.08));
  border-left: 3px solid var(--ok, #22c55e);
  border-radius: 0 var(--radius) var(--radius) 0;
  font-size: 12.5px;
  line-height: 1.55;
}
.install-rebuild-table {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0 16px;
  font-size: 12.5px;
  line-height: 1.5;
}
.install-rebuild-table th,
.install-rebuild-table td {
  text-align: left;
  padding: 8px 10px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}
.install-rebuild-table th {
  color: var(--muted);
  font-weight: 600;
  font-size: 11.5px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.install-rebuild-table td.reb-yes { color: var(--danger, #ef4444); }
.install-rebuild-table td.reb-no { color: var(--ok, #22c55e); }
.install-rebuild-table td.reb-maybe { color: var(--warn, #fbbf24); }
.install-trouble {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  margin: 6px 0;
  background: var(--surface-2);
  overflow: hidden;
}
.install-trouble > summary {
  cursor: pointer;
  padding: 10px 12px;
  font-size: 13px;
  list-style: none;
  user-select: none;
}
.install-trouble > summary::before {
  content: "\\25B8  ";
  color: var(--muted);
}
.install-trouble[open] > summary::before { content: "\\25BE  "; }
.install-trouble[open] > summary {
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}
.install-trouble-body { padding: 10px 14px 12px; font-size: 12.5px; line-height: 1.55; }
.install-design-note { margin-top: 22px; }
.install-guide code,
.install-commands-sub code,
.oneclick-sub code,
.status-output strong {
  background: var(--surface-2);
  padding: 1px 5px;
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 12px;
}
.status-output strong { background: transparent; padding: 0; }
.cmd-block { margin: 0 0 12px; }
.cmd-block:last-child { margin-bottom: 0; }
.cmd-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
  margin-bottom: 4px;
}
.cmd-row {
  display: flex;
  align-items: stretch;
  gap: 8px;
}
.cmd-code {
  flex: 1;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 12px;
  font-family: var(--font-mono);
  font-size: 12.5px;
  color: var(--text);
  overflow-x: auto;
  white-space: pre;
  display: flex;
  align-items: center;
}
.cmd-copy { flex: 0 0 auto; }
/* Commands tab — card grid of marketplace slash commands */
.cmd-intro { margin: 0 0 18px; }
.cmd-intro h2 { margin: 0 0 6px; }
.cmd-intro p { margin: 0; color: var(--muted); max-width: 64ch; }

/* ── Guidance tab (marketplace-wide trees + best practices) ── */
.guide-wrap { display: flex; flex-direction: column; gap: 10px; }
.guide-plugin { border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface); overflow: hidden; }
.guide-plugin-name { cursor: pointer; padding: 12px 16px; font-weight: 600; display: flex; align-items: baseline; justify-content: space-between; gap: 10px; }
.guide-plugin-name:hover { background: var(--surface-2); }
.guide-plugin-counts { font-size: 12px; color: var(--muted); font-weight: 400; white-space: nowrap; }
.guide-plugin-body { padding: 4px 16px 14px; border-top: 1px solid var(--border); }
.guide-subhd { margin: 12px 0 6px; font-size: 13px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }
.guide-count { display: inline-block; margin-left: 6px; font-size: 11px; color: var(--muted); background: var(--surface-2); border-radius: 10px; padding: 0 7px; }
.guide-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 4px; }
.guide-item { padding: 4px 0; }
.guide-link { display: flex; align-items: baseline; gap: 8px; text-decoration: none; color: var(--text); }
.guide-link:hover .guide-title { text-decoration: underline; }
.guide-kind { flex: none; font-size: 10px; text-transform: uppercase; letter-spacing: 0.03em; border-radius: 4px; padding: 1px 6px; white-space: nowrap; }
.guide-kind-tree { background: color-mix(in srgb, var(--accent) 22%, transparent); color: var(--accent); }
.guide-kind-bp { background: var(--surface-2); color: var(--muted); }
.guide-title { font-size: 14px; }
.guide-when { margin: 2px 0 0 56px; font-size: 12px; color: var(--muted); max-width: 70ch; }
/* Inline decision-tree diagram (pre-rendered SVG, collapsed by default) */
.guide-tree-diagram { margin: 6px 0 0 56px; }
.guide-tree-summary {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  font-size: 11.5px;
  font-weight: 600;
  color: var(--accent);
  list-style: none;
  user-select: none;
}
.guide-tree-summary::-webkit-details-marker { display: none; }
.guide-tree-summary::before { content: "▸"; font-size: 10px; transition: transform 0.12s; }
.guide-tree-diagram[open] .guide-tree-summary::before { transform: rotate(90deg); }
.guide-tree-svg {
  margin-top: 8px;
  padding: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow-x: auto;
}
.guide-tree-svg svg { max-width: 100%; height: auto; }
.cmd-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}
.cmd-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--rc-radius-lg);
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: var(--rc-shadow-sm);
  transition: box-shadow 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
}
.cmd-card:hover {
  box-shadow: var(--rc-shadow-md);
  border-color: var(--border-strong, var(--border));
  transform: translateY(-2px);
}
.cmd-card-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
}
.cmd-card-title {
  margin: 0;
  font-family: var(--font-mono);
  font-size: 15px;
  color: var(--accent);
  word-break: break-all;
}
.cmd-card-badge {
  flex: 0 0 auto;
  font-size: 11px;
  font-weight: 600;
  color: var(--muted);
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 2px 8px;
  white-space: nowrap;
}
.cmd-card-desc {
  margin: 0;
  flex: 1;
  font-size: 13px;
  line-height: 1.5;
  color: var(--text);
}
/* Commands tab — always-visible "what this runs" line + Class-B pill */
.cmd-what {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  color: var(--muted);
}
.cmd-what-label { font-weight: 600; color: var(--text); }
.cmd-what code {
  font-family: var(--font-mono);
  font-size: 11.5px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1px 5px;
  word-break: break-all;
}
.cmd-pill {
  flex: 0 0 auto;
  font-size: 10.5px;
  font-weight: 600;
  color: var(--muted);
  background: var(--surface-2);
  border: 1px dashed var(--border);
  border-radius: 999px;
  padding: 2px 8px;
  white-space: nowrap;
}
.cmd-run { flex: 0 0 auto; }
/* Overview tab */
.ov-wrap { display: flex; flex-direction: column; gap: 22px; max-width: 980px; }
.ov-hero h2 { margin: 0 0 8px; }
.ov-hero p { margin: 0; color: var(--text); line-height: 1.6; max-width: 72ch; }
.ov-banner {
  margin-top: 14px;
  padding: 10px 14px;
  border-radius: var(--radius);
  font-size: 13px;
  line-height: 1.5;
  border: 1px solid var(--border);
}
.ov-banner-static { background: var(--surface-2); color: var(--muted); }
.ov-banner-live {
  background: color-mix(in srgb, var(--accent) 14%, var(--surface));
  border-color: var(--accent);
  color: var(--text);
}
.ov-banner code {
  font-family: var(--font-mono);
  font-size: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1px 5px;
}
.ov-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}
.ov-stat {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.ov-stat strong { font-size: 24px; color: var(--accent); line-height: 1; }
.ov-stat span { font-size: 12px; color: var(--muted); }
.ov-h3 { margin: 4px 0 0; font-size: 15px; }
.ov-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 14px;
}
.ov-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-decoration: none;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--rc-radius-lg);
  padding: 18px;
  color: var(--text);
  box-shadow: var(--rc-shadow-sm);
  transition: border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
}
.ov-card:hover { border-color: var(--border-strong, var(--border)); transform: translateY(-2px); box-shadow: var(--rc-shadow-md); }
.ov-card h4 { margin: 0; font-size: 14px; color: var(--accent); }
.ov-card p { margin: 0; font-size: 12.5px; line-height: 1.5; color: var(--muted); }
.ov-card-cta { margin-top: auto; font-size: 12px; font-weight: 600; color: var(--accent); }
.ov-steps { margin: 0; padding-left: 22px; display: flex; flex-direction: column; gap: 8px; }
.ov-steps li { font-size: 13px; line-height: 1.5; color: var(--text); }
.ov-steps a { color: var(--accent); font-weight: 600; }
.ov-stats-lead { margin: 0 0 10px; font-size: 14px; color: var(--text); }
.ov-steps-lead { margin: 6px 0 10px; font-size: 13px; color: var(--muted); line-height: 1.5; }
.ov-steps-cap { margin: 12px 0 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); }
/* Optional steps stay present but visually recede so the required path leads. */
.ov-steps-optional { opacity: 0.92; }
.ov-steps-optional li { color: var(--muted); }
/* Guidance — best-practice preview-on-click */
.guide-bp-preview {
  margin: 4px 0 2px 22px;
  font-size: 12px;
  line-height: 1.5;
  color: var(--muted);
  border-left: 2px solid var(--border);
  padding-left: 10px;
}
.guide-bp-toggle {
  background: none;
  border: none;
  color: var(--accent);
  font-size: 11.5px;
  cursor: pointer;
  padding: 0 0 0 6px;
}
.guide-bp-toggle:hover { text-decoration: underline; }
.oneclick-head {
  display: flex;
  align-items: center;
  gap: 10px;
}
.live-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--accent);
}
.oneclick-sub {
  margin: 6px 0 12px;
  font-size: 12.5px;
  color: var(--muted);
  line-height: 1.5;
}
.oneclick-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.oneclick-buttons .btn { flex: 0 0 auto; }
.run-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: rc-spin 0.7s linear infinite;
}
@keyframes rc-spin { to { transform: rotate(360deg); } }
.run-result {
  margin-top: 14px;
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}
.run-result-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 12px;
  background: var(--surface-2);
  border-bottom: 1px solid var(--border);
}
.run-result-title { font-size: 12.5px; font-weight: 600; color: var(--text); }
.run-result-badge {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 2px 8px;
  border-radius: 10px;
}
.run-result-badge.badge-ok { color: #04210f; background: var(--ok); }
.run-result-badge.badge-fail { color: white; background: var(--danger); }
.run-result-output,
.status-output {
  margin: 0;
  padding: 12px;
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.5;
  color: var(--text);
  max-height: 320px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
}
.status-panel {
  margin-top: 16px;
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}
.status-panel h4 {
  margin: 0;
  padding: 8px 12px;
  background: var(--surface-2);
  border-bottom: 1px solid var(--border);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
}
.status-output { color: var(--muted); }

/* ── Test-a-command simulator tab ────────────────────────────────── */
.sim-layout {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 820px;
}
.sim-intro,
.sim-result {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
}
.sim-intro h2 { margin: 0 0 8px; font-size: 18px; }
.sim-intro p {
  margin: 0 0 12px;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.55;
}
.sim-intro code {
  background: var(--surface-2);
  padding: 1px 5px;
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 12px;
}
.sim-input-row {
  display: flex;
  gap: 8px;
  align-items: stretch;
}
.sim-input {
  flex: 1;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 12px;
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--text);
}
.sim-input:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
.sim-analyze { flex: 0 0 auto; }
.sim-analyze[disabled] { opacity: 0.5; cursor: not-allowed; }
.sim-disabled-help {
  margin: 10px 0 0;
  font-size: 12px;
  color: var(--warn);
}
.sim-disabled-help code {
  background: var(--surface-2);
  padding: 1px 5px;
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--text);
}
.sim-result { display: flex; flex-direction: column; gap: 16px; }
.sim-deny-banner {
  background: var(--danger);
  color: white;
  border-radius: 6px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 700;
}
.sim-deny-banner span { font-weight: 500; }
.sim-result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}
.sim-field { display: flex; flex-direction: column; gap: 6px; }
.sim-field-label,
.sim-gate-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
}
.sim-field-value {
  font-family: var(--font-mono);
  font-size: 14px;
  color: var(--text);
}
.sim-field-value.sim-no-category { color: var(--muted); font-style: italic; }
.sim-tier-badge {
  align-self: flex-start;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 3px 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--muted);
}
.sim-tier-badge.tier-low { border-color: var(--ok); color: var(--ok); background: var(--ok-soft); }
.sim-tier-badge.tier-medium { border-color: var(--warn); color: var(--warn); background: rgba(251, 191, 36, 0.08); }
.sim-tier-badge.tier-high { border-color: #fb923c; color: #fb923c; background: rgba(251, 146, 60, 0.1); }
.sim-tier-badge.tier-extreme { border-color: var(--danger); color: var(--danger); background: rgba(239, 68, 68, 0.1); }
.sim-seats-block,
.sim-concerns-block { display: flex; flex-direction: column; gap: 8px; }
.sim-seats,
.sim-concerns { display: flex; flex-wrap: wrap; gap: 8px; }
.sim-seat-pill {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 12px;
  border: 1px solid var(--accent);
  color: var(--accent);
  background: rgba(20, 184, 166, 0.08);
}
.sim-no-panel {
  font-size: 12.5px;
  color: var(--muted);
  font-style: italic;
}
.sim-concern-pill {
  font-family: var(--font-mono);
  font-size: 11.5px;
  padding: 3px 10px;
  border-radius: 10px;
  border: 1px solid var(--warn);
  color: var(--warn);
  background: rgba(251, 191, 36, 0.08);
}
.sim-gate {
  border-top: 1px dashed var(--border);
  padding-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.sim-gate-text {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  line-height: 1.5;
}

/* ── Learn tab ──────────────────────────────────────────────────────── */
.learn-tab { max-width: 1100px; margin: 0 auto; }
.learn-toolbar {
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 12px;
}
.learn-search {
  flex: 1 1 260px; min-width: 200px; padding: 8px 12px;
  background: var(--bg); color: var(--text);
  border: 1px solid var(--border); border-radius: 6px; font-size: 14px;
}
.learn-search:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
.learn-count { color: var(--muted); font-size: 13px; font-variant-numeric: tabular-nums; }
.learn-toolbar-spacer { flex: 1 1 auto; }
.learn-linkbtn {
  background: none; border: none; color: var(--accent); cursor: pointer;
  font-size: 13px; padding: 4px 6px; font-family: inherit;
}
.learn-linkbtn:hover { text-decoration: underline; }
.learn-linkbtn:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; border-radius: 4px; }
.learn-legend { display: flex; gap: 18px; margin-bottom: 18px; font-size: 12px; color: var(--muted); }
.learn-legend-item { display: inline-flex; align-items: center; gap: 7px; }
.learn-swatch { width: 13px; height: 13px; display: inline-block; }
.learn-swatch.fact { border: 2px solid var(--muted); border-radius: 50%; }
.learn-swatch.built {
  background: var(--accent);
  clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%);
}

.concept-cat { margin-bottom: 14px; }
.concept-cat[hidden] { display: none; }
.concept-cat-head {
  display: flex; align-items: center; gap: 10px; cursor: pointer;
  padding: 8px 0; list-style: none; user-select: none;
  border-bottom: 1px solid var(--border);
}
.concept-cat-head::-webkit-details-marker { display: none; }
.concept-cat-head::before {
  content: "\\25B8"; color: var(--accent); font-size: 12px;
  transition: transform 0.12s ease;
}
.concept-cat[open] > .concept-cat-head::before { transform: rotate(90deg); }
.concept-cat-name {
  text-transform: uppercase; letter-spacing: 0.06em; font-size: 12px;
  font-weight: 700; color: var(--accent);
}
.concept-cat-count {
  margin-left: auto; color: var(--muted); font-size: 12px;
  font-variant-numeric: tabular-nums;
}
.concept-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 16px; padding: 16px 0;
}
@media (max-width: 900px) { .concept-grid { grid-template-columns: 1fr; } }

.concept-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--rc-radius-lg); padding: 18px 20px; scroll-margin-top: 16px;
  box-shadow: var(--rc-shadow-sm);
  transition: box-shadow 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
}
.concept-card:hover { box-shadow: var(--rc-shadow-md); transform: translateY(-2px); }
.concept-card[hidden] { display: none; }
.concept-card:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.concept-eyebrow {
  text-transform: uppercase; letter-spacing: 0.05em; font-size: 11px;
  color: var(--muted); margin-bottom: 4px;
}
.concept-head { display: flex; align-items: flex-start; gap: 10px; justify-content: space-between; }
.concept-title { font-size: 16px; margin: 0; color: var(--text); }
.concept-badge {
  display: inline-flex; align-items: center; gap: 5px; flex: none;
  font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 999px;
  border: 1px solid; white-space: nowrap;
}
.concept-badge svg { width: 11px; height: 11px; }
.concept-badge.fact { color: var(--muted); border-color: var(--muted); background: rgba(148, 163, 184, 0.1); }
.concept-badge.built { color: var(--accent); border-color: var(--accent); background: rgba(20, 184, 166, 0.1); }
.concept-deck { font-size: 13.5px; color: var(--muted); margin: 8px 0 12px; line-height: 1.5; }
.concept-diagram-well {
  background: var(--surface-2); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 12px; margin-bottom: 12px;
  overflow: auto; text-align: center;
}
.rc-concept-diagram { max-width: 100%; height: auto; }
.concept-body { font-size: 14px; line-height: 1.6; color: var(--text); }
.concept-body p { margin: 0 0 10px; }
.concept-body p:last-child { margin-bottom: 0; }
.concept-body code {
  background: var(--surface-2); padding: 1px 5px; border-radius: 4px;
  font-family: var(--font-mono); font-size: 12.5px;
}
.concept-seealso { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.concept-chip {
  font-size: 12px; color: var(--text); text-decoration: none;
  background: var(--surface-2); border: 1px solid var(--border);
  border-radius: 999px; padding: 2px 10px;
}
.concept-chip:hover { border-color: var(--accent); color: var(--accent); }
.concept-sources-row {
  display: flex; flex-wrap: wrap; align-items: center; gap: 14px;
  margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border);
}
.concept-source { font-family: var(--font-mono); font-size: 11.5px; color: var(--accent); }
.concept-verified { margin-left: auto; font-size: 11px; color: var(--muted); }

.concept-tryit {
  display: inline-block; margin-top: 12px; font-size: 13px;
  color: var(--accent); text-decoration: none; font-weight: 600;
}
.concept-tryit:hover { text-decoration: underline; }
.concept-tryit:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 4px; }

/* interactive concept widgets (e.g. the permission-layer resolver) */
.concept-widget {
  margin-top: 14px; padding: 14px; background: var(--surface-2);
  border: 1px solid var(--border); border-radius: var(--radius);
}
.cw-title { font-size: 13px; font-weight: 700; color: var(--accent); margin-bottom: 4px; }
.cw-hint { font-size: 12.5px; color: var(--muted); margin: 0 0 12px; line-height: 1.5; }
.cw-rows { display: grid; gap: 8px; margin-bottom: 12px; }
.cw-row { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.cw-layer { font-family: var(--font-mono); font-size: 12px; color: var(--text); }
.cw-select {
  background: var(--bg); color: var(--text); border: 1px solid var(--border);
  border-radius: 5px; padding: 4px 8px; font-size: 12px; flex: none;
}
.cw-select:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
.cw-result {
  display: flex; flex-wrap: wrap; align-items: baseline; gap: 10px;
  padding-top: 10px; border-top: 1px solid var(--border);
}
.cw-verdict {
  font-weight: 700; font-size: 13px; padding: 2px 10px; border-radius: 999px;
  border: 1px solid var(--border); color: var(--muted); white-space: nowrap;
}
.cw-verdict[data-v="deny"] { color: var(--danger); border-color: var(--danger); }
.cw-verdict[data-v="ask"] { color: var(--warn); border-color: var(--warn); }
.cw-verdict[data-v="allow"] { color: var(--ok); border-color: var(--ok); }
.cw-why { font-size: 12.5px; color: var(--muted); flex: 1 1 200px; line-height: 1.5; }

/* clickable diagram nodes (node_links) — cross-jump to a related concept */
.concept-diagram-well .rc-node-link { cursor: pointer; }
.concept-diagram-well .rc-node-link:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.concept-diagram-well .rc-node-link:hover rect,
.concept-diagram-well .rc-node-link:hover polygon,
.concept-diagram-well .rc-node-link:focus rect,
.concept-diagram-well .rc-node-link:focus polygon { stroke: var(--accent) !important; stroke-width: 2.5px !important; }

@keyframes rc-flash {
  0% { box-shadow: 0 0 0 2px var(--accent); }
  100% { box-shadow: 0 0 0 0 transparent; }
}
.concept-card.rc-flash { animation: rc-flash 1.2s ease-out; }
@media (prefers-reduced-motion: reduce) {
  .concept-card.rc-flash { animation: none; }
  .concept-cat-head::before { transition: none; }
}

/* ── Mobile touch-target fixes ─────────────────────────────── */
/* Lift .layer-opt pill buttons and .info-btn to ≥44px tap targets on
   coarse-pointer (touch) devices so allow/ask/deny pills aren't a
   fat-finger hazard. Desktop layout is unaffected. */
@media (pointer: coarse), (max-width: 900px) {
  .layer-opt {
    min-height: 44px;
    padding: 10px 14px;
    font-size: 13px;
  }
  .layer-radios {
    gap: 2px;
  }
  .info-btn {
    width: 44px;
    height: 44px;
    font-size: 14px;
  }
}

/* ── Review log (saga) tab ──────────────────────────────────── */
.saga-layout { padding: 20px; }
.saga-hdr { display: flex; align-items: baseline; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.saga-hdr h2 { margin: 0; }
.saga-filters { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
.saga-filters label { font-size: 13px; color: var(--muted); }
.saga-filters select {
  background: var(--surface-2); color: var(--text); border: 1px solid var(--border);
  border-radius: 4px; padding: 4px 8px; font-size: 13px; cursor: pointer;
}
.saga-refresh {
  background: transparent; color: var(--accent); border: 1px solid var(--accent);
  border-radius: 4px; padding: 4px 10px; font-size: 13px; cursor: pointer;
}
.saga-refresh:hover { background: var(--accent); color: var(--bg); }
.saga-refresh:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.saga-count { font-size: 12px; color: var(--muted); }
.saga-table-wrap { overflow-x: auto; }
.saga-table {
  width: 100%; border-collapse: collapse; font-size: 13px;
}
.saga-table th, .saga-table td {
  padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border);
  vertical-align: top;
}
.saga-table th { font-weight: 600; color: var(--muted); white-space: nowrap; position: sticky; top: 0; background: var(--surface); }
.saga-table tr:hover td { background: var(--surface-2); }
.saga-action { font-family: var(--font-mono); font-size: 11.5px; word-break: break-word; max-width: 260px; }
.saga-verdict-pill {
  display: inline-block; padding: 2px 8px; border-radius: 10px;
  font-size: 11.5px; font-weight: 600; white-space: nowrap;
}
.saga-verdict-allow { background: var(--ok-soft); color: var(--ok); border: 1px solid var(--ok); }
.saga-verdict-ask   { background: #fbbf2420; color: var(--warn);   border: 1px solid var(--warn); }
.saga-verdict-deny  { background: #ef444420; color: var(--danger); border: 1px solid var(--danger); }
.saga-verdict-edit  { background: #3b82f620; color: #60a5fa;       border: 1px solid #3b82f6; }
.saga-seat-chip {
  display: inline-flex; align-items: center; gap: 3px;
  padding: 1px 6px; border-radius: 8px; font-size: 11px;
  background: var(--surface-2); border: 1px solid var(--border);
  margin: 1px 2px 1px 0; white-space: nowrap;
}
.saga-seat-allow { border-color: var(--ok); color: var(--ok); }
.saga-seat-deny  { border-color: var(--danger); color: var(--danger); }
.saga-seat-ask   { border-color: var(--warn);   color: var(--warn); }
.saga-seat-det   { color: var(--muted); font-style: italic; }
.saga-concerns   { font-size: 11.5px; color: var(--muted); word-break: break-word; }
.saga-rewrite summary { cursor: pointer; font-size: 11.5px; color: var(--accent); }
.saga-rewrite pre { margin: 4px 0 0; font-size: 11px; font-family: var(--font-mono); white-space: pre-wrap; word-break: break-all; color: var(--text); }
.saga-empty {
  text-align: center; padding: 40px 20px;
  background: var(--surface); border-radius: var(--radius);
  border: 1px solid var(--border); color: var(--muted);
}
.saga-empty p { margin: 8px 0 0; font-size: 13px; }

/* ── Activity tab — run feed (reuses .saga-layout/.saga-hdr/.saga-empty) ── */
.activity-intro { color: var(--muted); font-size: 13px; margin: 0 20px 16px; max-width: 72ch; }
/* Sleipnir's stables — one-row worktree widget at the top of the Activity tab. */
.sleipnir-stables { display: flex; align-items: center; gap: 8px; margin: 0 20px 14px; padding: 8px 12px; background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px; font-size: 12.5px; }
.sleipnir-glyph { font-size: 15px; }
.sleipnir-label { font-weight: 700; color: var(--text); }
.sleipnir-body { color: var(--muted); font-family: var(--font-mono); font-size: 12px; word-break: break-word; }
#activity-content { padding: 0 20px 20px; display: flex; flex-direction: column; gap: 12px; }
.activity-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px 16px;
}
.activity-card-head { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }
.activity-id { margin: 0; font-family: var(--font-mono); font-size: 13.5px; color: var(--text); word-break: break-all; flex: 1; }
.activity-time { font-size: 12px; color: var(--muted); white-space: nowrap; }
.activity-status {
  flex: 0 0 auto; font-size: 11px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.03em; border-radius: 999px; padding: 2px 9px; border: 1px solid var(--border);
}
.activity-status-ok      { background: var(--ok-soft); color: var(--ok); border-color: var(--ok); }
.activity-status-warn    { background: #fbbf2420; color: var(--warn);   border-color: var(--warn); }
.activity-status-bad     { background: #ef444420; color: var(--danger); border-color: var(--danger); }
.activity-status-neutral { background: var(--surface-2); color: var(--muted); }
.activity-summary { margin: 8px 0 0; font-size: 12.5px; line-height: 1.5; color: var(--text); white-space: pre-wrap; word-break: break-word; }
.activity-arts { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.activity-art {
  font-size: 11px; font-family: var(--font-mono); color: var(--muted);
  background: var(--surface-2); border: 1px solid var(--border); border-radius: 4px; padding: 1px 7px;
}

/* ── Heimdall tab — perimeter alerts (reuses .saga-hdr/.saga-empty/.activity-intro) ── */
.heimdall-layout { padding: 20px; }
.heimdall-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px; padding: 0 20px 20px;
}
.heimdall-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px 16px;
}
.heimdall-card h3 { margin: 0 0 2px; font-size: 14px; color: var(--text); }
.heimdall-sub { margin: 0 0 12px; font-size: 12px; color: var(--muted); line-height: 1.4; }
.hm-hookgroup { margin-bottom: 12px; }
.hm-hookname { margin: 0 0 5px; font-family: var(--font-mono); font-size: 12.5px; color: var(--text); }
.hm-evt {
  display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 8px;
  padding: 5px 8px; border-radius: 5px; border-left: 3px solid var(--border);
  background: var(--surface-2); margin-bottom: 4px; font-size: 12px;
}
.hm-evt--red   { border-left-color: var(--danger); }
.hm-evt--amber { border-left-color: var(--warn); }
.hm-evt--grey  { border-left-color: var(--muted); }
.hm-badge {
  font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em;
  border-radius: 999px; padding: 1px 8px; white-space: nowrap;
}
.hm-badge--red   { background: #ef444420; color: var(--danger); border: 1px solid var(--danger); }
.hm-badge--amber { background: #fbbf2420; color: var(--warn);   border: 1px solid var(--warn); }
.hm-badge--grey  { background: var(--surface); color: var(--muted); border: 1px solid var(--border); }
.hm-verdict { color: var(--muted); font-size: 11.5px; }
.hm-path { font-family: var(--font-mono); font-size: 11px; color: var(--text); word-break: break-all; grid-column: 2 / 4; }
.hm-ts { font-size: 10.5px; color: var(--muted); white-space: nowrap; }
.hm-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.hm-table th { text-align: left; padding: 4px 8px; color: var(--muted); font-weight: 600; border-bottom: 1px solid var(--border); }
.hm-table td { padding: 4px 8px; border-bottom: 1px solid var(--border); font-family: var(--font-mono); }
.hm-row--drift { background: #ef444412; }
.hm-stat--ok    { color: var(--ok); }
.hm-stat--drift { color: var(--danger); font-weight: 700; }
.hm-ci-row { display: flex; align-items: center; gap: 8px; padding: 6px 4px; text-decoration: none; border-bottom: 1px solid var(--border); }
.hm-ci-row:hover { background: var(--surface-2); }
.hm-ci-dot { width: 9px; height: 9px; border-radius: 999px; flex: 0 0 auto; }
.hm-ci-dot--ok   { background: var(--ok); }
.hm-ci-dot--fail { background: var(--danger); }
.hm-ci-dot--run  { background: var(--warn); }
.hm-ci-name { flex: 1; font-size: 12px; color: var(--text); }
.hm-ci-meta { font-size: 11px; color: var(--muted); white-space: nowrap; }
/* Gjallarhorn banner — fixed, tiered, hidden until a signal fires. */
.gjallarhorn {
  position: fixed; top: 0; left: 0; right: 0; z-index: 200;
  display: flex; align-items: center; gap: 12px; padding: 10px 18px;
  font-size: 13.5px; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}
.gjallarhorn[hidden] { display: none; }
.gjallarhorn-glyph { font-size: 18px; }
.gjallarhorn-text { flex: 1; }
.gjallarhorn-link { color: inherit; text-decoration: underline; font-weight: 600; white-space: nowrap; }
.gjallarhorn--red   { background: var(--danger); color: #fff; }
.gjallarhorn--amber { background: var(--warn);   color: #1a1205; }
.gjallarhorn--grey  { background: var(--surface-2); color: var(--text); border-bottom: 1px solid var(--border); }
/* Níðhöggr "Debt watch" card (lives inside the Heimdall grid). */
.heimdall-card--wide { grid-column: 1 / -1; }
.heimdall-card--wide #heimdall-debt { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; }
.nid-section { background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; }
.nid-hdr { margin: 0 0 6px; font-size: 12px; font-weight: 700; color: var(--text); }
.nid-clean { margin: 0; font-size: 12px; color: var(--accent); }
.nid-list { margin: 0; padding-left: 16px; display: flex; flex-direction: column; gap: 3px; }
.nid-list li { font-size: 11.5px; font-family: var(--font-mono); color: var(--text); word-break: break-word; }
/* Idunn "Knowledge health" card (also a wide card inside Heimdall). */
.heimdall-card--wide #heimdall-kh { display: flex; flex-direction: column; gap: 12px; }
.kh-tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; }
.kh-tile { background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; text-align: left; cursor: pointer; font: inherit; color: var(--text); transition: border-color 120ms ease, box-shadow 120ms ease; }
.kh-tile:hover, .kh-tile:focus-visible { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent) inset; outline: none; }
.kh-tile[aria-pressed="true"] { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent) inset; }
.kh-tile--stale[aria-pressed="true"] { border-color: var(--danger); box-shadow: 0 0 0 1px var(--danger) inset; }
.kh-tile--soon[aria-pressed="true"]  { border-color: var(--warn); box-shadow: 0 0 0 1px var(--warn) inset; }
.kh-tile-count { font-size: 22px; font-weight: 700; line-height: 1.05; color: var(--text); }
.kh-tile--stale .kh-tile-count { color: var(--danger); }
.kh-tile--soon  .kh-tile-count { color: var(--warn); }
.kh-tile--fresh .kh-tile-count { color: var(--accent); }
.kh-tile-label { display: block; margin-top: 4px; font-size: 11.5px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.03em; }
.kh-meta { font-size: 11.5px; color: var(--muted); }
.kh-drill { background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; }
.kh-drill[hidden] { display: none; }
.kh-drill-hdr { margin: 0 0 6px; font-size: 12px; font-weight: 700; color: var(--text); }
.kh-drill-list { margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 4px; max-height: 320px; overflow-y: auto; }
.kh-drill-list li { font-size: 11.5px; font-family: var(--font-mono); color: var(--text); word-break: break-word; }
.kh-drill-list li .kh-drill-age { color: var(--muted); margin-left: 6px; font-family: var(--font-sans, inherit); }
.kh-clean { margin: 0; font-size: 12px; color: var(--accent); }
.kh-error { margin: 0; font-size: 12px; color: var(--danger); }

/* ── Bifröst tab — install-bridge wizard (§3.6) ── */
.bifrost-layout { padding: 20px; }
.bifrost-steps { list-style: none; margin: 0 20px 20px; padding: 0; display: flex; flex-direction: column; gap: 14px; }
.bifrost-step { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 14px 16px; }
.bifrost-step--ready { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent) inset; }
.bifrost-step-head { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.bifrost-step-title { margin: 0; font-size: 14px; color: var(--text); }
.bifrost-badge { font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; border-radius: 999px; padding: 2px 9px; white-space: nowrap; }
.bifrost-badge--grey  { background: var(--surface-2); color: var(--muted); border: 1px solid var(--border); }
.bifrost-badge--green { background: var(--ok-soft); color: var(--ok); border: 1px solid var(--ok); }
.bifrost-badge--amber { background: #fbbf2420; color: var(--warn);   border: 1px solid var(--warn); }
.bifrost-badge--red   { background: #ef444420; color: var(--danger); border: 1px solid var(--danger); }
.bifrost-explain { margin: 8px 0; font-size: 12.5px; color: var(--muted); line-height: 1.5; }
.bifrost-cmd { display: flex; align-items: center; gap: 8px; background: var(--surface-2); border: 1px solid var(--border); border-radius: 6px; padding: 6px 8px; }
.bifrost-cmd code { flex: 1; font-family: var(--font-mono); font-size: 12px; color: var(--text); word-break: break-all; }
.bifrost-copy { flex: 0 0 auto; font: inherit; font-size: 11.5px; padding: 3px 10px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text); cursor: pointer; }
.bifrost-copy:hover { border-color: var(--accent); }
.bifrost-update { margin-top: 22px; padding-top: 18px; border-top: 1px solid var(--border); max-width: 820px; }
.bifrost-update h3 { margin: 0 0 8px; font-size: 15px; }
.bifrost-update > p { font-size: 13px; color: var(--muted); line-height: 1.55; margin: 0 0 12px; }
.bifrost-paste-label { display: block; margin: 10px 0 2px; font-size: 12px; font-weight: 600; color: var(--text); }
.bifrost-paste-hint { margin: 0 0 4px; font-size: 11.5px; color: var(--muted); }
.bifrost-paste { width: 100%; box-sizing: border-box; font-family: var(--font-mono); font-size: 12px; padding: 6px 8px; border: 1px solid var(--border); border-radius: 6px; background: var(--surface-2); color: var(--text); resize: vertical; }
.bifrost-verify { margin-top: 8px; font: inherit; font-size: 12px; font-weight: 600; padding: 5px 14px; border-radius: 6px; border: 1px solid var(--accent); background: var(--accent); color: var(--rc-text); cursor: pointer; }
.bifrost-faults { margin: 0 20px 20px; }
.bifrost-faults > h3 { font-size: 13px; color: var(--text); margin: 0 0 8px; }
.bifrost-fault { border: 1px solid var(--border); border-radius: 6px; margin-bottom: 6px; overflow: hidden; }
.bifrost-fault-toggle { width: 100%; text-align: left; font: inherit; font-size: 12.5px; font-weight: 600; padding: 8px 12px; background: var(--surface-2); color: var(--text); border: 0; cursor: pointer; }
.bifrost-fault-toggle::before { content: "\\25B8  "; color: var(--muted); }
.bifrost-fault-toggle[aria-expanded="true"]::before { content: "\\25BE  "; }
.bifrost-fault-body { padding: 8px 12px; font-size: 12px; color: var(--muted); line-height: 1.5; }

/* ── Víðarr tab — posture/security event log (reuses .saga-hdr/.saga-empty) ── */
.vidarr-layout { padding: 20px; }
.vidarr-myth em { color: var(--muted); font-style: italic; }
.vidarr-filters {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  padding: 0 20px 14px; margin: 0 0 4px;
}
.vidarr-filters label { font-size: 12px; color: var(--muted); }
.vidarr-filters select {
  font: inherit; font-size: 12px; padding: 4px 8px; border-radius: 6px;
  border: 1px solid var(--border); background: var(--surface); color: var(--text);
}
.vidarr-typechips { display: inline-flex; gap: 6px; flex-wrap: wrap; }
.vidarr-chip {
  font: inherit; font-size: 11.5px; padding: 3px 11px; border-radius: 999px;
  border: 1px solid var(--border); background: var(--surface); color: var(--muted); cursor: pointer;
}
.vidarr-chip--active { background: var(--accent); color: var(--rc-text); border-color: var(--accent); font-weight: 600; }
#vidarr-content { padding: 0 20px 20px; }
.vidarr-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.vidarr-table th {
  text-align: left; padding: 6px 8px; color: var(--muted); font-weight: 600;
  border-bottom: 1px solid var(--border); white-space: nowrap;
}
.vidarr-table td { padding: 6px 8px; border-bottom: 1px solid var(--border); vertical-align: top; }
.vidarr-table td:nth-child(1) { font-family: var(--font-mono); font-size: 11px; color: var(--muted); white-space: nowrap; }
.vidarr-table td:nth-child(4) { font-family: var(--font-mono); font-size: 11px; word-break: break-all; }
.vidarr-kind {
  font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em;
  border-radius: 999px; padding: 1px 8px; white-space: nowrap;
}
.vidarr-kind--posture-change { background: #3b82f620; color: #3b82f6; border: 1px solid #3b82f6; }
.vidarr-kind--security-deny  { background: #ef444420; color: var(--danger); border: 1px solid var(--danger); }
.vidarr-row--security-deny td:nth-child(1) { border-left: 3px solid var(--danger); }

/* ── Norns tab — plugin lineage, three columns (reuses .saga-hdr/.saga-empty) ── */
.norns-layout { padding: 20px; }
.norns-legend { margin: 0 20px 14px; font-size: 13px; color: var(--text); }
.norns-sub { color: var(--muted); font-size: 0.9em; font-weight: 400; }
.norns-cols {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px; padding: 0 20px 20px;
}
.norns-col {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px 16px;
}
.norns-col h3 { margin: 0 0 12px; font-size: 15px; color: var(--text); }
.norns-grouphdr {
  margin: 12px 0 4px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em;
  color: var(--muted); font-weight: 700;
}
.norns-grouphdr:first-child { margin-top: 0; }
.norns-itemlist { margin: 0; padding-left: 16px; display: flex; flex-direction: column; gap: 3px; }
.norns-itemlist li { font-size: 12px; font-family: var(--font-mono); color: var(--text); word-break: break-word; }
.norns-dl { margin: 0; display: grid; grid-template-columns: auto 1fr; gap: 4px 12px; }
.norns-dl dt { font-size: 12px; color: var(--muted); }
.norns-dl dd { margin: 0; font-size: 12px; font-family: var(--font-mono); color: var(--text); }
.norns-nextver { margin: 0 0 8px; font-size: 13px; font-weight: 600; color: var(--accent); }

/* ── Mímir's well: Claude Code session-state surface ── */
.mimir-layout { padding: 20px; }
.mimir-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px; padding: 0 20px 20px;
}
.mimir-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px 16px;
}
.mimir-card--full { grid-column: 1 / -1; }
.mimir-card h3 { margin: 0 0 12px; font-size: 15px; color: var(--text); }
.mimir-pill {
  display: inline-block; padding: 2px 8px; border-radius: 10px;
  font-size: 11.5px; border: 1px solid var(--border);
  background: var(--surface-2); color: var(--muted);
}
.mimir-pill--inproc { font-style: italic; }
.mimir-pill--asof { margin-bottom: 8px; }
.mimir-days {
  margin: 0; padding-left: 16px; display: flex; flex-direction: column; gap: 3px;
}
.mimir-days li { font-size: 12px; font-family: var(--font-mono); color: var(--text); }
.mimir-recent-list {
  margin: 0; padding-left: 16px; display: flex; flex-direction: column; gap: 4px;
}
.mimir-recent-list li {
  font-size: 12px; font-family: var(--font-mono); color: var(--text); word-break: break-word;
}
.mimir-unreach-list {
  margin: 0; padding-left: 16px; display: flex; flex-direction: column; gap: 3px;
}
.mimir-unreach-list li { font-size: 12.5px; color: var(--muted); }

/* ── Review log: plain-language reason + expandable decision panel ── */
.saga-reason {
  font-size: 12px; color: var(--text); line-height: 1.45;
  display: flex; flex-direction: column; gap: 4px;
}
.saga-expand-btn {
  background: none; border: none; color: var(--accent);
  font: inherit; font-size: 11.5px; cursor: pointer;
  padding: 0; text-decoration: underline; text-align: left;
  width: fit-content;
}
.saga-expand-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 3px; }
.saga-detail-row { display: none; }
.saga-detail-row.open { display: table-row; }
.saga-detail-panel {
  background: var(--surface-2); border-radius: var(--radius);
  padding: 14px 16px; margin: 4px 0 8px;
  border-left: 3px solid var(--accent);
}
.saga-detail-steps {
  display: grid; grid-template-columns: auto 1fr; gap: 6px 14px;
  align-items: baseline;
}
.saga-detail-label {
  font-size: 11.5px; font-weight: 600; color: var(--muted);
  text-transform: uppercase; letter-spacing: 0.04em;
  white-space: nowrap;
}
.saga-detail-val {
  font-size: 12.5px; color: var(--text); line-height: 1.5;
}
.saga-detail-val code {
  font-family: var(--font-mono); font-size: 11.5px;
  background: var(--surface); padding: 1px 5px; border-radius: 3px;
}
.saga-detail-panel pre {
  margin: 6px 0 0; font-size: 11px; font-family: var(--font-mono);
  white-space: pre-wrap; word-break: break-all;
  color: var(--text); background: var(--surface);
  border: 1px solid var(--border); border-radius: 4px;
  padding: 8px 10px;
}

/* ── Risk tier badges (saga + simulator shared) ──────────────── */
.saga-tier-badge {
  display: inline-block; padding: 2px 8px; border-radius: 10px;
  font-size: 11.5px; font-weight: 600; white-space: nowrap;
  border: 1px solid var(--border); color: var(--muted);
  background: var(--surface-2);
}
.saga-tier-badge-low     { border-color: var(--ok); color: var(--ok); background: var(--ok-soft); }
.saga-tier-badge-medium  { border-color: var(--warn);   color: var(--warn);   background: #fbbf2410; }
.saga-tier-badge-high    { border-color: #f97316;       color: #f97316;       background: #f9731610; }
.saga-tier-badge-extreme { border-color: var(--danger); color: var(--danger); background: #ef444410; }

/* ── Plugins category: per-plugin variable + content pages ── */
.plugin-page, .web-access-page { max-width: 880px; }
.pp-title { margin: 0 0 4px; font-family: var(--font-display); }
.pp-sub { color: var(--muted); font-size: 13px; margin: 0 0 20px; }
.pp-section { margin: 0 0 24px; }
.pp-section > h3 { margin: 0 0 10px; font-size: 15px; }
.pp-count { display: inline-block; min-width: 20px; padding: 0 7px; margin-left: 6px; border-radius: 999px; background: var(--ok-soft); color: var(--ok); font-size: 12px; font-weight: 600; }
.pp-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.pp-list { margin: 0; padding-left: 18px; }
.pp-list li { margin: 2px 0; font-size: 13px; }
.pp-empty { color: var(--muted); font-size: 13px; font-style: italic; }
.pv-curated { display: flex; flex-direction: column; gap: 14px; }
.pv-row { display: grid; grid-template-columns: 200px 1fr; gap: 6px 14px; align-items: center; }
.pv-label { font-size: 13px; font-weight: 600; }
.pv-control { padding: 6px 9px; border: 1px solid var(--border); border-radius: 7px; background: var(--panel); color: var(--text); font: inherit; font-size: 13px; min-width: 180px; }
.pv-help { grid-column: 2; margin: 0; color: var(--muted); font-size: 12px; line-height: 1.45; }
.pv-freeform { margin-top: 18px; }
.pv-freeform h4 { margin: 0 0 4px; font-size: 13px; }
.pv-extra { width: 100%; box-sizing: border-box; padding: 9px 11px; border: 1px solid var(--border); border-radius: 8px; background: var(--panel); color: var(--text); font-family: var(--font-mono, ui-monospace, monospace); font-size: 12.5px; resize: vertical; }
.pp-actions { display: flex; align-items: center; gap: 10px; margin-top: 16px; flex-wrap: wrap; }
.pp-save, .pp-download { padding: 7px 14px; border-radius: 8px; border: 1px solid var(--border); background: var(--panel); color: var(--text); font: inherit; font-size: 13px; font-weight: 600; cursor: pointer; }
.pp-save { background: var(--accent, #d4a017); color: #1a1408; border-color: transparent; }
.pp-save:hover, .pp-download:hover { filter: brightness(1.08); }
.pp-status { font-size: 12px; color: var(--muted); }
.pp-status.status-ok { color: var(--ok); }
.pp-status.status-error { color: var(--danger); }
.pp-status.status-unsaved { color: var(--warn); }
.pp-noserver { margin: 12px 0 0; padding: 10px 12px; border: 1px solid var(--border); border-radius: 8px; background: var(--ok-soft); color: var(--muted); font-size: 12.5px; line-height: 1.5; }
@media (max-width: 720px) { .pv-row { grid-template-columns: 1fr; } .pv-help { grid-column: 1; } .pp-cols { grid-template-columns: 1fr; } }
""".strip()


_SETTINGS_TAB_TEMPLATE = """
<div class="settings-layout">
  <div class="settings-form">
    <div class="preset-bar">
      <h3>Apply a preset
        <button type="button" class="info-btn info-btn-section" id="layers-info-btn"
          aria-label="How layers merge" title="How layers merge">&#9432;</button>
      </h3>
      <p>Sets every category&#39;s <strong>Local</strong> layer at once — your personal default. User and Project layers are untouched.</p>
      <div class="preset-buttons">{preset_buttons}</div>
    </div>

    {design_checkins}
    {thing_preview}
    {category_intro}
    {category_groups}
    {security_deny}
  </div>

  <aside class="yaml-preview">
    <h3>
      <span>comfort-posture.yaml</span>
      <span id="yaml-status" class="yaml-status status-unsaved">unsaved</span>
    </h3>
    <pre id="yaml-output"></pre>
    <div class="yaml-primary-action">
      <button class="btn btn-primary" id="save-repo-btn" hidden>
        <span class="btn-main">Save &amp; apply all layers</span>
        <span class="btn-sub" id="save-repo-target">.ravenclaude/comfort-posture.yaml &rarr; user/local/project settings</span>
      </button>
      <p class="primary-help" id="save-repo-help" hidden>
        Saves to <code>.ravenclaude/comfort-posture.yaml</code> <strong>and immediately applies it to all three layers</strong> &mdash; re-runs the translator so your <code>settings.json</code> permission rules update right away.
      </p>
      <p class="primary-help warn" id="save-repo-warn" hidden>
        &#9888; This overwrites the <code>allow</code> / <code>ask</code> / <code>deny</code> rules in all three settings files. Hand-edits to those rules are replaced. The three files are: <code>~/.claude/settings.json</code> (User), <code>.claude/settings.local.json</code> (Local, gitignored), and <code>.claude/settings.json</code> (Project, committed/shared).
      </p>
      <p class="primary-help muted" id="no-server-help" hidden>
        <strong>No local server behind this page.</strong> The published / static dashboard (e.g. on <code>github.io</code>) can&rsquo;t write to your repo, so <em>Save &amp; apply</em> won&rsquo;t work here. Start the local dashboard with <code>ravenclaude dashboard --project &lt;repo&gt;</code> (or <code>bash .ravenclaude/dashboard.sh</code>, or VS Code &rarr; Run Task &rarr; &ldquo;RavenClaude: Comfort-posture dashboard&rdquo;) and open the URL it prints &mdash; Save &amp; apply works there. Meanwhile, use <strong>Download</strong> below and drop the file into <code>.ravenclaude/comfort-posture.yaml</code>.
        In a Codespace? Make sure you opened the <strong>forwarded</strong> URL the server printed (Ports panel &rarr; Open in Browser), not the static GitHub Pages copy.
      </p>
      <div class="primary-help apply-error-block" id="apply-error-block" hidden>
        <strong>&#9888; YAML saved &mdash; settings.json was not updated.</strong>
        <p id="apply-error-detail" class="apply-error-detail"></p>
        <p class="apply-error-hint">Your YAML file is saved; only the automatic settings.json translation failed. Re-open the dashboard and try again, or use <strong>Download</strong> and place the file at <code>.ravenclaude/comfort-posture.yaml</code> manually.</p>
      </div>
    </div>
    <details class="yaml-alt-actions">
      <summary>Alternative ways to save</summary>
      <div class="yaml-actions">
        <button class="btn secondary" id="connect-btn" hidden>Auto-save to file&hellip;</button>
        <button class="btn secondary" id="copy-btn">Copy</button>
        <button class="btn secondary" id="download-btn">Download</button>
      </div>
      <div class="yaml-connected-row" id="connected-row" hidden>
        <span class="connected-pill">
          <span class="connected-dot"></span>
          Auto-saving to <code id="connected-filename">comfort-posture.yaml</code>
        </span>
        <button type="button" class="link-btn" id="disconnect-btn" title="Disconnect from file">disconnect</button>
      </div>
      <p class="yaml-help" id="no-api-help" hidden>
        Auto-save to a chosen file needs Chrome, Edge, or Opera. Use Copy or Download instead.
      </p>
    </details>
  </aside>
</div>
""".strip()


_INSTALL_TAB_TEMPLATE = """
<div class="install-layout">
  <section class="install-guide">
    <h2>Install RavenClaude &mdash; GitHub Copilot CLI</h2>
    <p class="install-intro">
      Follow these steps in order. Every command has a <strong>Copy</strong> button &mdash; you don&rsquo;t
      need to type anything. Each step tells you what to expect <em>after</em> you run it.
      <strong>Using Claude Code instead?</strong> See the <a href="#/bifrost">Claude&nbsp;Code</a> page.
    </p>

    <h3>What is this?</h3>
    <p class="install-explain">
      <strong>RavenClaude</strong> is a kit of AI agents (architect, coder, reviewer, and friends) you can use
      inside coding tools. <strong>GitHub Copilot CLI</strong> is GitHub&rsquo;s command-line chatbot &mdash;
      you type <code>copilot</code> in a terminal and it answers like a chat. This page shows how to plug
      the RavenClaude kit into Copilot so the agents are there when you chat.
    </p>

    <h3>Before you start &mdash; what you need</h3>
    <p>Run each of these three checks. They print a version number if you have the thing already.</p>
    <div class="cmd-block">
      <span class="cmd-label">a. Node.js 22 or higher</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-check-node">node --version</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-check-node">Copy</button>
      </div>
    </div>
    <div class="cmd-block">
      <span class="cmd-label">b. GitHub Copilot CLI</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-check-copilot">copilot --version</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-check-copilot">Copy</button>
      </div>
    </div>
    <div class="cmd-block">
      <span class="cmd-label">c. GitHub CLI (for cloning the RavenClaude repo)</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-check-gh">gh auth status</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-check-gh">Copy</button>
      </div>
    </div>
    <p><strong>Missing the Copilot CLI?</strong> Install it:</p>
    <div class="cmd-block">
      <span class="cmd-label">Install GitHub Copilot CLI</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-install-copilot">npm install -g @github/copilot</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-install-copilot">Copy</button>
      </div>
    </div>
    <p>
      <strong>Not signed into Copilot?</strong> Run <code>copilot</code> once. When it opens, type
      <code>/login</code> and follow the prompts &mdash; you sign in with your GitHub account.
    </p>

    <h3>Step 1: Get RavenClaude onto your machine</h3>
    <p>
      RavenClaude lives in a GitHub repo. You <em>clone</em> (download) it once, into your home folder.
      <em>The squiggly line <code>~</code> means &ldquo;your home folder&rdquo; &mdash; on a Mac that&rsquo;s
      <code>/Users/yourname</code>, on Linux it&rsquo;s <code>/home/yourname</code>, and in a Codespace
      it&rsquo;s <code>/home/codespace</code>.</em>
    </p>
    <div class="cmd-block">
      <span class="cmd-label">Clone the RavenClaude repo (one time only)</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-clone-rc">gh repo clone mcorbett51090/RavenClaude ~/RavenClaude</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-clone-rc">Copy</button>
      </div>
    </div>
    <p>
      <strong>After this:</strong> You have a folder at <code>~/RavenClaude</code> with all the agent kits.
      Every command below points back to this folder.
    </p>
    <p>
      <strong>If the clone fails with &ldquo;permission denied&rdquo;:</strong> the repo is private &mdash;
      make sure you ran <code>gh auth login</code> first and signed in with your GitHub account, then try the
      clone again.
    </p>

    <h3>Step 2: Pick how you&rsquo;re working</h3>
    <p>Two situations. Pick the one that matches you. (Click to expand.)</p>

    <details class="install-situation" open>
      <summary><strong>Situation A:</strong> I&rsquo;m using a brand-new GitHub Codespace</summary>
      <div class="install-situation-body">
        <p>
          A <strong>Codespace</strong> is a cloud computer GitHub gives you for a repo &mdash; it opens
          in your browser and looks like VS Code. If that&rsquo;s you, follow these four steps to make
          RavenClaude set itself up automatically every time the Codespace opens.
        </p>
        <ol class="install-steplist">
          <li>
            <strong>Inside your Codespace&rsquo;s terminal</strong>, run this once. It copies two
            setup files into your project&rsquo;s <code>.devcontainer/</code> folder.
            <div class="cmd-block">
              <div class="cmd-row">
                <code class="cmd-code" id="cmd-cs-init">bash ~/RavenClaude/scripts/ravenclaude init-codespace --project .</code>
                <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-cs-init">Copy</button>
              </div>
            </div>
          </li>
          <li>
            <strong>Wire up THIS session right now</strong> (so you don&rsquo;t have to rebuild to test).
            Pick the plugins you want here &mdash; see <a href="#install-step-3">Step 3</a> for what each one does.
            <div class="cmd-block">
              <span class="cmd-label">Just the base kit (core only)</span>
              <div class="cmd-row">
                <code class="cmd-code" id="cmd-cs-setup-core">bash ~/RavenClaude/scripts/ravenclaude setup --project .</code>
                <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-cs-setup-core">Copy</button>
              </div>
            </div>
            <div class="cmd-block">
              <span class="cmd-label">Core + power-platform (example: a Microsoft Power Platform project)</span>
              <div class="cmd-row">
                <code class="cmd-code" id="cmd-cs-setup-pp">bash ~/RavenClaude/scripts/ravenclaude setup --project . --with-plugin power-platform</code>
                <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-cs-setup-pp">Copy</button>
              </div>
            </div>
          </li>
          <li>
            <strong>Reload your shell</strong> so the new <code>rc</code> command works.
            <div class="cmd-block">
              <div class="cmd-row">
                <code class="cmd-code" id="cmd-cs-source">source ~/.bashrc</code>
                <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-cs-source">Copy</button>
              </div>
            </div>
          </li>
          <li>
            <strong>Commit and push the <code>.devcontainer/</code> files</strong> so future
            Codespace builds are fully automatic.
            <div class="cmd-block">
              <div class="cmd-row">
                <code class="cmd-code" id="cmd-cs-commit">git add .devcontainer &amp;&amp; git commit -m "Add RavenClaude Codespace auto-setup" &amp;&amp; git push</code>
                <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-cs-commit">Copy</button>
              </div>
            </div>
          </li>
        </ol>
        <p class="install-after">
          <strong>After this:</strong> Every time you (or anyone on your team) opens a Codespace for this
          repo, RavenClaude sets itself up automatically. The dashboard URL opens by itself in a new
          browser tab. You just type <code>rc</code> to launch Copilot.
        </p>
      </div>
    </details>

    <details class="install-situation">
      <summary><strong>Situation B:</strong> I&rsquo;m on my own computer (no Codespace)</summary>
      <div class="install-situation-body">
        <p>Three steps. Pretty similar to Situation A, just without the Codespace auto-setup file.</p>
        <ol class="install-steplist">
          <li>
            <strong>Go to your project folder</strong> in a terminal. Replace the path with your
            actual folder.
            <div class="cmd-block">
              <div class="cmd-row">
                <code class="cmd-code" id="cmd-local-cd">cd /path/to/your/project</code>
                <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-local-cd">Copy</button>
              </div>
            </div>
          </li>
          <li>
            <strong>Wire RavenClaude into this project.</strong> Pick the plugins you want &mdash; see
            <a href="#install-step-3">Step 3</a> for what each one does.
            <div class="cmd-block">
              <span class="cmd-label">Just the base kit (core only)</span>
              <div class="cmd-row">
                <code class="cmd-code" id="cmd-local-setup-core">bash ~/RavenClaude/scripts/ravenclaude setup --project .</code>
                <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-local-setup-core">Copy</button>
              </div>
            </div>
            <div class="cmd-block">
              <span class="cmd-label">Core + power-platform</span>
              <div class="cmd-row">
                <code class="cmd-code" id="cmd-local-setup-pp">bash ~/RavenClaude/scripts/ravenclaude setup --project . --with-plugin power-platform</code>
                <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-local-setup-pp">Copy</button>
              </div>
            </div>
          </li>
          <li>
            <strong>Reload your shell</strong> so the new <code>rc</code> command works.
            <div class="cmd-block">
              <span class="cmd-label">If you use bash</span>
              <div class="cmd-row">
                <code class="cmd-code" id="cmd-local-source-bash">source ~/.bashrc</code>
                <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-local-source-bash">Copy</button>
              </div>
            </div>
            <div class="cmd-block">
              <span class="cmd-label">If you use zsh (most Macs)</span>
              <div class="cmd-row">
                <code class="cmd-code" id="cmd-local-source-zsh">source ~/.zshrc</code>
                <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-local-source-zsh">Copy</button>
              </div>
            </div>
          </li>
        </ol>
        <p class="install-after">
          <strong>After this:</strong> RavenClaude is wired into THIS project on this computer.
          You type <code>rc</code> in a terminal (from this project&rsquo;s folder) to launch Copilot.
        </p>
      </div>
    </details>

    <h3 id="install-step-3">Step 3: Pick your plugins</h3>
    <p>
      RavenClaude is split into <strong>plugins</strong> &mdash; separate kits for different jobs. Step 2
      above showed how to pick them with the <code>--with-plugin</code> flag. Add the flag once per plugin
      &mdash; for example: <code>--with-plugin power-platform --with-plugin finance</code>.
    </p>
    <p><strong>What&rsquo;s in each plugin?</strong></p>
    <ul class="install-plugin-list">
      <li><strong>ravenclaude-core</strong> &mdash; <em>Always on.</em> The base kit of generalist agents
        (architect, coder, reviewer, etc.) and the team-lead dispatch pattern. You never have to ask
        for this one.</li>
      <li><strong>power-platform</strong> &mdash; Microsoft Power Platform specialists (Dataverse,
        Power Automate, Power Apps). Use this for any Microsoft project.</li>
      <li><strong>finance</strong> &mdash; Finance-domain specialists for accounting workflows.</li>
      <li><strong>web-design</strong> &mdash; Web design specialists (UX, visual, accessibility,
        performance).</li>
      <li><strong>data-platform</strong> &mdash; Data engineering, ELT, dashboards, multi-tenant.</li>
      <li><em>and 12 others</em> &mdash; see the <a href="#/learn">Learn tab</a> for the full list.</li>
    </ul>
    <p>
      <strong>Already installed and want to add a plugin later?</strong> Re-run the setup command with
      the new plugin name. It&rsquo;s safe to run again &mdash; it just adds the new skills alongside
      what&rsquo;s already there.
    </p>
    <div class="cmd-block">
      <span class="cmd-label">Add power-platform to an already-installed project</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-add-plugin-later">bash ~/RavenClaude/scripts/ravenclaude setup --project . --with-plugin power-platform</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-add-plugin-later">Copy</button>
      </div>
    </div>
    <p>Then, inside your running Copilot session:</p>
    <div class="cmd-block">
      <span class="cmd-label">Pick up the new skills without restarting Copilot</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-skills-reload-step3">/skills reload</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-skills-reload-step3">Copy</button>
      </div>
    </div>

    <h3>Step 4: Launch Copilot with RavenClaude</h3>
    <p>One word from any terminal:</p>
    <div class="cmd-block">
      <span class="cmd-label">Launch Copilot with all your wired-up agents</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-launch-rc">rc</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-launch-rc">Copy</button>
      </div>
    </div>
    <p>
      <strong>What <code>rc</code> does:</strong> It pulls the latest RavenClaude (so you always have the
      newest version), then launches Copilot with the agents and skills loaded. <em>(<code>rc</code> is
      short for &ldquo;ravenclaude&rdquo; &mdash; <code>ravenclaude setup</code> added it to your shell&rsquo;s
      <code>~/.bashrc</code> or <code>~/.zshrc</code>.)</em>
    </p>

    <h3>Updating later</h3>
    <p>
      <code>rc</code> auto-updates every time you launch &mdash; so usually you don&rsquo;t do anything
      extra. A few common variants:
    </p>

    <p><strong>1. Update and relaunch in one step</strong> &mdash; the everyday move:</p>
    <div class="cmd-block">
      <span class="cmd-label">Update + launch (the rc alias)</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-update-rc">rc</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-update-rc">Copy</button>
      </div>
    </div>

    <p><strong>2. Update <em>without</em> launching Copilot</strong> &mdash; e.g. from a scratch shell or a script:</p>
    <div class="cmd-block">
      <span class="cmd-label">Update only (no launch)</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-update-only">bash ~/RavenClaude/scripts/ravenclaude update</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-update-only">Copy</button>
      </div>
    </div>
    <p>Then, inside your running Copilot session, pick up changed skills:</p>
    <div class="cmd-block">
      <span class="cmd-label">Inside Copilot</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-skills-reload-update">/skills reload</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-skills-reload-update">Copy</button>
      </div>
    </div>

    <p><strong>3. Verify what&rsquo;s wired in this project</strong> &mdash; lists the version, the wired skills, the hook adapter, and the MCP entry:</p>
    <div class="cmd-block">
      <span class="cmd-label">Status check</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-status-check-update">bash ~/RavenClaude/scripts/ravenclaude status --project .</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-status-check-update">Copy</button>
      </div>
    </div>

    <p><strong>4. Relaunch from a running Copilot session</strong> &mdash; needed when you changed a hook or an MCP server (skills alone don&rsquo;t need this; <code>/skills reload</code> is enough). Press <kbd>Ctrl</kbd>+<kbd>C</kbd> twice to quit, then:</p>
    <div class="cmd-block">
      <span class="cmd-label">Quit + relaunch</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-quit-relaunch">rc</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-quit-relaunch">Copy</button>
      </div>
    </div>
    <p class="install-cross-tool">
      <strong>Using Claude Code on the same machine?</strong> <code>ravenclaude update</code> only refreshes
      the Copilot side &mdash; it does not touch Claude Code&rsquo;s plugin cache at
      <code>~/.claude/plugins/cache/</code>. To update that side too, run
      <code>/plugin marketplace update ravenclaude</code> and <code>/reload-plugins</code> <em>inside Claude
      Code</em>. See the <a href="#bifrost-verify-cache">Bifröst cache-verification steps</a>.
    </p>

    <h3>When do I need to rebuild my Codespace?</h3>
    <p>
      A <strong>rebuild</strong> tears down the Codespace and creates a new one. It&rsquo;s slow &mdash;
      a few minutes. Most things <em>don&rsquo;t</em> need one.
    </p>
    <table class="install-rebuild-table">
      <thead>
        <tr><th scope="col">What you did</th><th scope="col">Rebuild?</th><th scope="col">What instead</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>Added or changed files in <code>.devcontainer/</code></td>
          <td class="reb-yes"><strong>Yes</strong></td>
          <td>The <code>.devcontainer/</code> files only take effect when the Codespace is built. Command Palette &rarr; &ldquo;Codespaces: Rebuild Container&rdquo;.</td>
        </tr>
        <tr>
          <td>Ran <code>ravenclaude update</code> (or <code>rc</code>)</td>
          <td class="reb-no"><strong>No</strong></td>
          <td>Skills read live from disk. Inside Copilot, type <code>/skills reload</code>.</td>
        </tr>
        <tr>
          <td>Added a new plugin with <code>--with-plugin</code></td>
          <td class="reb-no"><strong>No</strong></td>
          <td>Inside Copilot, type <code>/skills reload</code> (or quit and re-run <code>rc</code>).</td>
        </tr>
        <tr>
          <td>Changed settings on the dashboard</td>
          <td class="reb-no"><strong>No</strong></td>
          <td>Dashboard&rsquo;s <em>Save &amp; apply</em> updates <code>.claude/settings.json</code> immediately. The engine reads it on each command.</td>
        </tr>
        <tr>
          <td>Changed hooks or MCP servers</td>
          <td class="reb-maybe"><strong>No, but relaunch</strong></td>
          <td>Hooks and MCP servers load when Copilot starts. Press <code>Ctrl+C</code> twice to quit, then type <code>rc</code> again.</td>
        </tr>
        <tr>
          <td>Just opened the Codespace after pausing it</td>
          <td class="reb-no"><strong>No</strong></td>
          <td>That&rsquo;s a <em>resume</em>, not a build. The dashboard auto-launch fires on resume too.</td>
        </tr>
      </tbody>
    </table>

    <h3>Common problems</h3>
    <details class="install-trouble">
      <summary><strong>&ldquo;rc: command not found&rdquo;</strong></summary>
      <div class="install-trouble-body">
        <p>Your shell hasn&rsquo;t loaded the new <code>rc</code> alias yet. Reload it:</p>
        <div class="cmd-block">
          <div class="cmd-row">
            <code class="cmd-code" id="cmd-trouble-source">source ~/.bashrc</code>
            <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-trouble-source">Copy</button>
          </div>
        </div>
        <p>If you use zsh (most Macs), use <code>source ~/.zshrc</code> instead. Or just close and reopen your terminal.</p>
      </div>
    </details>
    <details class="install-trouble">
      <summary><strong>&ldquo;gh: command not found&rdquo; during the clone step</strong></summary>
      <div class="install-trouble-body">
        <p>GitHub CLI isn&rsquo;t installed. In a Codespace, it&rsquo;s already there &mdash; if you see this,
        you&rsquo;re probably on a local computer. Install it:</p>
        <ul>
          <li>Mac: <code>brew install gh</code></li>
          <li>Ubuntu/Debian: see <a href="https://github.com/cli/cli#installation">github.com/cli/cli</a></li>
          <li>Windows: <code>winget install --id GitHub.cli</code></li>
        </ul>
        <p>After installing: <code>gh auth login</code>.</p>
      </div>
    </details>
    <details class="install-trouble">
      <summary><strong>Copilot says it doesn&rsquo;t know about an agent</strong></summary>
      <div class="install-trouble-body">
        <p>Either Copilot was launched without <code>--plugin-dir</code> (the <code>rc</code> alias
        handles this for you), or you need to reload skills. Inside Copilot, type
        <code>/skills reload</code>. If that doesn&rsquo;t work, press <code>Ctrl+C</code> twice to quit
        Copilot, then type <code>rc</code> again.</p>
      </div>
    </details>
    <details class="install-trouble">
      <summary><strong>Dashboard didn&rsquo;t open automatically in my Codespace</strong></summary>
      <div class="install-trouble-body">
        <p>Open the <strong>Ports</strong> panel in VS Code (View menu &rarr; Ports), find port 8000 labeled
        &ldquo;RavenClaude dashboard&rdquo;, right-click &rarr; <strong>Open in Browser</strong>.
        <strong>Don&rsquo;t</strong> use the VS Code Simple Browser &mdash; it blocks parts of the dashboard.</p>
      </div>
    </details>
    <details class="install-trouble">
      <summary><strong>I want to check what&rsquo;s wired in my project</strong></summary>
      <div class="install-trouble-body">
        <div class="cmd-block">
          <div class="cmd-row">
            <code class="cmd-code" id="cmd-status-check">bash ~/RavenClaude/scripts/ravenclaude status --project .</code>
            <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-status-check">Copy</button>
          </div>
        </div>
        <p>Prints what&rsquo;s in <code>.claude/skills</code>, <code>.github/hooks</code>, and
        <code>~/.copilot/mcp-config.json</code>.</p>
      </div>
    </details>

    <p class="install-pillar install-design-note">
      <strong>Under the hood:</strong> RavenClaude reads everything <em>live from disk</em>. The plugin
      loads via <code>--plugin-dir</code>, skills from <code>.claude/skills</code>, hooks from
      <code>.github/hooks</code>, MCP from <code>~/.copilot/mcp-config.json</code>. So
      <code>ravenclaude update</code> is just a <code>git pull</code> on the marketplace clone &mdash;
      no re-install, ever. There&rsquo;s no plugin cache to invalidate, no version registry to update.
      The hooks land at <em>repo</em> level (not plugin level) as a workaround for
      <a href="https://github.com/github/copilot-cli/issues/2540">copilot-cli#2540</a> &mdash; plugin-level
      <code>preToolUse</code> hooks don&rsquo;t fire in Copilot today.
    </p>
  </section>

  <section class="install-commands">
    <h3>Commands</h3>
    <p class="install-commands-sub">
      Copy any of these and run them in your checkout. They work everywhere, even
      when this page is opened from GitHub Pages or a file.
    </p>
    {command_blocks}
  </section>

  <section class="install-oneclick" id="install-oneclick">
    <div class="oneclick-head">
      <h3>One-click run</h3>
      <span class="live-badge" id="run-live-badge" hidden>&#9679; live</span>
    </div>
    <p class="oneclick-sub" id="run-oneclick-sub">
      Run <code>python3 scripts/serve-dashboards.py</code> for one-click, or use the copy
      buttons above.
    </p>
    <div class="oneclick-buttons">
      <button type="button" class="btn" id="run-install-btn" data-run-action="install" disabled>Install</button>
      <button type="button" class="btn" id="run-update-btn" data-run-action="update" disabled>Update now</button>
      <button type="button" class="btn secondary" id="run-status-btn" data-run-action="status" disabled>Status</button>
      <span class="run-spinner" id="run-spinner" hidden aria-hidden="true"></span>
    </div>
    <div class="run-result" id="run-result" hidden>
      <div class="run-result-head">
        <span class="run-result-title" id="run-result-title">Result</span>
        <span class="run-result-badge" id="run-result-badge"></span>
      </div>
      <pre class="run-result-output" id="run-result-output"></pre>
    </div>
    <div class="status-panel" id="status-panel">
      <h4>Bridge status</h4>
      <pre class="status-output" id="status-output">Click <strong>Status</strong> to check which pieces (skills, hooks, MCP, package) are wired. Needs the local server.</pre>
    </div>
  </section>
</div>
""".strip()


_SAGA_TAB_TEMPLATE = """
<div class="saga-layout">
  <div class="saga-hdr">
    <h2>&#9878; Review log</h2>
    <button type="button" class="saga-refresh" id="saga-refresh-btn">Refresh</button>
    <span class="saga-count" id="saga-count"></span>
  </div>
  <div class="saga-filters">
    <label for="saga-verdict-filter">Verdict:</label>
    <select id="saga-verdict-filter" aria-label="Filter by verdict">
      <option value="">All</option>
      <option value="allow">allow</option>
      <option value="ask">ask</option>
      <option value="deny">deny</option>
      <option value="edit">edit</option>
    </select>
    <label for="saga-cat-filter">Category:</label>
    <select id="saga-cat-filter" aria-label="Filter by category">
      <option value="">All</option>
    </select>
  </div>
  <div id="saga-content">
    <div class="saga-empty" id="saga-loading">
      <p>Loading review log&hellip;</p>
    </div>
  </div>
</div>
""".strip()


_ACTIVITY_TAB_TEMPLATE = """
<div class="saga-layout">
  <div class="saga-hdr">
    <h2>&#128220; Run feed</h2>
    <button type="button" class="saga-refresh" id="activity-refresh-btn">Refresh</button>
    <span class="saga-count" id="activity-count"></span>
  </div>
  <p class="activity-intro">Run history from <code>.ravenclaude/runs/</code> &mdash; newest first. Each card is one multi-step run (its summary, structured-result status, and event count). Command-review verdicts live in the <strong>Review log</strong> tab.</p>
  <div class="sleipnir-stables" id="sleipnir-stables" aria-label="Sleipnir's stables — active worktrees">
    <span class="sleipnir-glyph" aria-hidden="true">&#128014;</span>
    <span class="sleipnir-label">Sleipnir&rsquo;s stables</span>
    <span class="sleipnir-body" id="sleipnir-body">&hellip;</span>
  </div>
  <div id="activity-content">
    <div class="saga-empty" id="activity-loading"><p>Loading activity&hellip;</p></div>
  </div>
</div>
""".strip()

_HEIMDALL_TAB_TEMPLATE = """
<div class="gjallarhorn" id="gjallarhorn-banner" role="status" tabindex="-1" hidden>
  <span class="gjallarhorn-glyph" aria-hidden="true">&#9888;</span>
  <span class="gjallarhorn-text" id="gjallarhorn-text"></span>
  <a class="gjallarhorn-link" id="gjallarhorn-link" href="#/heimdall">View event detail</a>
</div>
<div class="heimdall-layout">
  <div class="saga-hdr">
    <h2><span aria-hidden="true">&#128737;</span> Perimeter alerts</h2>
    <button type="button" class="saga-refresh" id="heimdall-refresh-btn">Refresh</button>
  </div>
  <p class="activity-intro">Perimeter alerts &mdash; a <strong>read-only mirror</strong> of what your guardrails already flagged. Heimdall never blocks anything itself; it shows the most recent hook denials, CI runs, and version drift so you can answer &ldquo;what tripped, when, and why?&rdquo; in one glance.</p>
  <div class="heimdall-grid">
    <section class="heimdall-card" aria-labelledby="hm-hooks-h">
      <h3 id="hm-hooks-h">Recent hook denials</h3>
      <p class="heimdall-sub">When did a guardrail say &ldquo;no&rdquo;? (red = irrecoverable, amber = blocked, grey = advisory)</p>
      <div id="heimdall-hooks">
        <div class="saga-empty" id="heimdall-hooks-loading"><p>Loading hook events&hellip;</p></div>
      </div>
    </section>
    <section class="heimdall-card" aria-labelledby="hm-ci-h">
      <h3 id="hm-ci-h">Recent CI runs</h3>
      <p class="heimdall-sub">The last few GitHub Actions runs on this marketplace.</p>
      <div id="heimdall-ci">
        <div class="saga-empty" id="heimdall-ci-loading"><p>Loading CI status&hellip;</p></div>
      </div>
    </section>
    <section class="heimdall-card" aria-labelledby="hm-drift-h">
      <h3 id="hm-drift-h">Plugin version drift</h3>
      <p class="heimdall-sub">Does each plugin&rsquo;s version match the marketplace catalog?</p>
      <div id="heimdall-drift"></div>
    </section>
    <section class="heimdall-card" aria-labelledby="hm-alarm-h">
      <h3 id="hm-alarm-h">Active alarms (Gjallarhorn)</h3>
      <p class="heimdall-sub">The highest-severity signal currently flagged.</p>
      <div id="heimdall-alarm"></div>
    </section>
    <section class="heimdall-card heimdall-card--wide" aria-labelledby="hm-debt-h">
      <h3 id="hm-debt-h">Debt watch (Níðhöggr)</h3>
      <p class="heimdall-sub">Slow-rotting bits at the foundations &mdash; low-noise marketplace maintenance signals.</p>
      <div id="heimdall-debt">
        <div class="saga-empty" id="heimdall-debt-loading"><p>Loading debt signals&hellip;</p></div>
      </div>
    </section>
    <section class="heimdall-card heimdall-card--wide" aria-labelledby="hm-kh-h">
      <h3 id="hm-kh-h">Knowledge health (Idunn)</h3>
      <p class="heimdall-sub">How current is the marketplace&rsquo;s knowledge layer? Click a bucket to drill into the files in it.</p>
      <div id="heimdall-kh">
        <div class="saga-empty" id="heimdall-kh-loading"><p>Loading knowledge health&hellip;</p></div>
      </div>
    </section>
  </div>
</div>
""".strip()

_VIDARR_TAB_TEMPLATE = """
<div class="vidarr-layout">
  <div class="saga-hdr">
    <h2><span aria-hidden="true">&#128095;</span> Security log</h2>
    <button type="button" class="saga-refresh" id="vidarr-refresh-btn">Refresh</button>
    <span class="saga-count" id="vidarr-count"></span>
  </div>
  <p class="activity-intro vidarr-myth">Posture &amp; security event log <em>(Víðarr&rsquo;s shoe)</em> &mdash; a <strong>read-only</strong> chronological record of how your security posture changed and which guardrails blocked an action. Víðarr&rsquo;s shoe was assembled from leather scraps across all of time; this log is the same &mdash; small events accumulating against the day someone needs to know exactly what happened.</p>
  <div class="vidarr-filters" role="group" aria-label="Filter the security log">
    <label for="vidarr-range">Time range:</label>
    <select id="vidarr-range" aria-label="Time range">
      <option value="1">Last 24 hours</option>
      <option value="7">Last 7 days</option>
      <option value="30" selected>Last 30 days</option>
      <option value="36500">All time</option>
    </select>
    <span class="vidarr-typechips" id="vidarr-typechips">
      <button type="button" class="vidarr-chip vidarr-chip--active" data-kind="all" aria-pressed="true">All</button>
      <button type="button" class="vidarr-chip" data-kind="posture-change" aria-pressed="false">Posture changes</button>
      <button type="button" class="vidarr-chip" data-kind="security-deny" aria-pressed="false">Security denials</button>
    </span>
  </div>
  <div id="vidarr-content">
    <div class="saga-empty" id="vidarr-loading"><p>Loading security log&hellip;</p></div>
  </div>
</div>
""".strip()

_NORNS_TAB_TEMPLATE = """
<div class="norns-layout">
  <div class="saga-hdr">
    <h2><span aria-hidden="true">&#127795;</span> Lineage</h2>
    <button type="button" class="saga-refresh" id="norns-refresh-btn">Refresh</button>
  </div>
  <p class="activity-intro">Plugin lineage <em>(The Norns)</em> for <code>ravenclaude-core</code> &mdash; past, present, and proposed future, drawn live from git history, surfaced scenarios, and the manifest.</p>
  <p class="norns-legend">Urðr <span class="norns-sub">(Lessons &amp; history)</span> &middot; Verðandi <span class="norns-sub">(Current)</span> &middot; Skuld <span class="norns-sub">(Proposed)</span></p>
  <div class="norns-cols">
    <section class="norns-col" aria-labelledby="norns-urdr-h">
      <h3 id="norns-urdr-h">Urðr <span class="norns-sub">Lessons &amp; history</span></h3>
      <div id="norns-urdr"><div class="saga-empty"><p>Loading&hellip;</p></div></div>
    </section>
    <section class="norns-col" aria-labelledby="norns-verdandi-h">
      <h3 id="norns-verdandi-h">Verðandi <span class="norns-sub">Current</span></h3>
      <div id="norns-verdandi"><div class="saga-empty"><p>Loading&hellip;</p></div></div>
    </section>
    <section class="norns-col" aria-labelledby="norns-skuld-h">
      <h3 id="norns-skuld-h">Skuld <span class="norns-sub">Proposed</span></h3>
      <div id="norns-skuld"><div class="saga-empty"><p>Loading&hellip;</p></div></div>
    </section>
  </div>
</div>
""".strip()

_MIMIR_TAB_TEMPLATE = """
<div class="mimir-layout">
  <div class="saga-hdr">
    <h2><span aria-hidden="true">&#127769;</span> Session</h2>
    <button type="button" class="saga-refresh" id="mimir-refresh-btn">Refresh</button>
  </div>
  <p class="activity-intro">Claude Code session state for this project <em>(M&iacute;mir&rsquo;s well)</em> &mdash; drawn live from <code>~/.claude/</code> and <code>.claude/settings.json</code>. Read-only; in-process-only fields render with an explainer, never a dash.</p>
  <div class="mimir-grid">
    <section class="mimir-card" aria-labelledby="mimir-settings-h">
      <h3 id="mimir-settings-h">Settings</h3>
      <div id="mimir-settings"><div class="saga-empty"><p>Loading&hellip;</p></div></div>
    </section>
    <section class="mimir-card" aria-labelledby="mimir-session-h">
      <h3 id="mimir-session-h">Current session</h3>
      <div id="mimir-session"><div class="saga-empty"><p>Loading&hellip;</p></div></div>
    </section>
    <section class="mimir-card" aria-labelledby="mimir-activity-h">
      <h3 id="mimir-activity-h">Activity summary</h3>
      <div id="mimir-activity"><div class="saga-empty"><p>Loading&hellip;</p></div></div>
    </section>
    <section class="mimir-card" aria-labelledby="mimir-recent-h">
      <h3 id="mimir-recent-h">Recent project sessions</h3>
      <div id="mimir-recent"><div class="saga-empty"><p>Loading&hellip;</p></div></div>
    </section>
    <section class="mimir-card mimir-card--full" aria-labelledby="mimir-unreach-h">
      <h3 id="mimir-unreach-h">In-process only</h3>
      <div id="mimir-unreach"><div class="saga-empty"><p>Loading&hellip;</p></div></div>
    </section>
  </div>
</div>
""".strip()


# Bifröst — the install-bridge wizard (§3.6). A guided 4-step copy-paste flow for
# installing a marketplace plugin into a Claude Code project. The wizard NEVER
# executes a slash command — the user runs each in their own session and pastes
# the output back; the JS only parses that output to advance the bridge. Distinct
# from the "Install & Update" tab (which wires RavenClaude into GitHub Copilot CLI).
_BIFROST_STEPS = [
    (
        "1",
        "Add the marketplace",
        "Point Claude Code at the RavenClaude marketplace (a URL or a local path to a clone).",
        "/plugin marketplace add &lt;url-or-path&gt;",
        "Paste what Claude Code printed (e.g. “marketplace added” or an error).",
    ),
    (
        "2",
        "Install the plugin",
        "Install a plugin from the marketplace into your project. The name must match an entry in <code>marketplace.json</code>’s <code>plugins[]</code>.",
        "/plugin install &lt;plugin-name&gt;@ravenclaude",
        "Paste the install result.",
    ),
    (
        "3",
        "Reload plugins",
        "Make Claude Code pick up the newly-installed plugin.",
        "/reload-plugins",
        "Confirm you can see the plugin in your <code>/plugin</code> menu, then paste anything it printed (or type “I see it”).",
    ),
    (
        "4",
        "Verify the bridge",
        "Confirm the project is agent-ready with the plugin wired in.",
        "/init-agent-ready --check",
        "Paste the check output — green means the bridge holds.",
    ),
]

_BIFROST_FAILURES = [
    (
        "Marketplace add failed",
        "Check the URL or path. Common causes: a typo, a missing <code>.claude-plugin/marketplace.json</code> at that location, or no read permission. For a local clone, pass the absolute path to the repo root.",
    ),
    (
        "Plugin install failed",
        "Check that the plugin name exactly matches an entry in the marketplace’s <code>marketplace.json</code> <code>plugins[]</code> array, and that you added the marketplace in step 1 (the <code>@ravenclaude</code> suffix is the marketplace name).",
    ),
    (
        "Reload failed",
        "Try fully restarting Claude Code — the plugin cache can be stale. If it still doesn’t appear, re-run step 2; a partial install won’t show in the <code>/plugin</code> menu.",
    ),
    (
        "Verify failed",
        "Open <code>plugins/&lt;plugin&gt;/CLAUDE.md</code> for the plugin’s required environment (env vars, CLIs, MCP servers). A red check usually means a missing prerequisite, not a broken install.",
    ),
]


def _bifrost_step_html(num, title, explain, command, paste_hint):
    return f"""    <li class="bifrost-step" id="bifrost-step-{num}" data-step="{num}">
      <div class="bifrost-step-head">
        <span class="bifrost-badge bifrost-badge--grey" id="bifrost-badge-{num}" role="status">Not started</span>
        <h3 class="bifrost-step-title">Step {num}. {title}</h3>
      </div>
      <p class="bifrost-explain">{explain}</p>
      <div class="bifrost-cmd">
        <code id="bifrost-cmd-{num}">{command}</code>
        <button type="button" class="bifrost-copy" data-copy-target="bifrost-cmd-{num}" aria-label="Copy the step {num} command to the clipboard">Copy</button>
      </div>
      <label class="bifrost-paste-label" for="bifrost-paste-{num}">What I see now</label>
      <p class="bifrost-paste-hint">{paste_hint}</p>
      <textarea class="bifrost-paste" id="bifrost-paste-{num}" rows="2" aria-label="Paste the step {num} output here"></textarea>
      <button type="button" class="bifrost-verify" data-verify-step="{num}">Verify step {num}</button>
    </li>"""


def _bifrost_failure_html(idx, title, body):
    return f"""      <div class="bifrost-fault" id="bifrost-fault-{idx}">
        <button type="button" class="bifrost-fault-toggle" aria-expanded="false" aria-controls="bifrost-fault-body-{idx}">{title}</button>
        <div class="bifrost-fault-body" id="bifrost-fault-body-{idx}" hidden>
          <p>{body}</p>
        </div>
      </div>"""


_BIFROST_TAB_TEMPLATE = (
    """
<div class="bifrost-layout">
  <div class="saga-hdr">
    <h2><span aria-hidden="true">&#127752;</span> Install &amp; Update &mdash; Claude Code</h2>
  </div>
  <p class="activity-intro">Bifröst is the rainbow bridge between the marketplace and your Claude Code project. Follow these four steps to install a plugin, then see <a href="#bifrost-update">Updating an installed plugin</a> below. Each step is <strong>copy-paste only</strong> &mdash; Bifröst guides you, but you cross the bridge yourself. Nothing here runs a command for you; you run each in your Claude Code session and paste the result back so Bifröst can light the next step. <strong>Using GitHub Copilot CLI instead?</strong> See the <a href="#/install">Copilot&nbsp;CLI</a> page.</p>
  <ol class="bifrost-steps">
"""
    + "\n".join(_bifrost_step_html(*s) for s in _BIFROST_STEPS)
    + """
  </ol>
  <section class="bifrost-faults" aria-label="If the bridge is down">
    <h3>If the bridge is down&hellip;</h3>
"""
    + "\n".join(_bifrost_failure_html(i + 1, t, b) for i, (t, b) in enumerate(_BIFROST_FAILURES))
    + """
  </section>
  <section class="bifrost-update" id="bifrost-update" aria-label="Updating an installed plugin">
    <h3>Updating an installed plugin</h3>
    <p>Once a plugin is installed you don&rsquo;t re-run the wizard to update it &mdash; just refresh the marketplace catalog and reload. Run both in your Claude Code session:</p>
    <div class="cmd-block">
      <span class="cmd-label">1. Pull the latest marketplace catalog</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-claude-update">/plugin marketplace update ravenclaude</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-claude-update">Copy</button>
      </div>
    </div>
    <div class="cmd-block">
      <span class="cmd-label">2. Apply it in your session</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-claude-reload">/reload-plugins</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-claude-reload">Copy</button>
      </div>
    </div>
    <p>Plugin versions bump on every user-visible change, so the catalog update is what surfaces a new version. Re-run <code>/init-agent-ready --check</code> (step&nbsp;4) afterward to confirm the bridge still holds.</p>
    <h3 id="bifrost-verify-cache">Verify the cache actually advanced</h3>
    <p>Claude Code reads installed plugins from <code>~/.claude/plugins/cache/&lt;marketplace&gt;/&lt;plugin&gt;/&lt;version&gt;/</code>, indexed by <code>~/.claude/plugins/installed_plugins.json</code>. If a reload doesn&rsquo;t seem to take, check the cache directly &mdash; the most common failure mode is a stale entry. Run these in a shell (not in Claude Code):</p>
    <div class="cmd-block">
      <span class="cmd-label">a. Cached version for ravenclaude-core</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-claude-cache-version">jq -r '.plugins[&quot;ravenclaude-core@ravenclaude&quot;][0].version' ~/.claude/plugins/installed_plugins.json</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-claude-cache-version">Copy</button>
      </div>
    </div>
    <div class="cmd-block">
      <span class="cmd-label">b. Versions on disk in the cache</span>
      <div class="cmd-row">
        <code class="cmd-code" id="cmd-claude-cache-list">ls ~/.claude/plugins/cache/ravenclaude/ravenclaude-core/</code>
        <button type="button" class="btn secondary cmd-copy" data-copy-for="cmd-claude-cache-list">Copy</button>
      </div>
    </div>
    <p>The cached version should match the marketplace&rsquo;s current <code>version</code> in <code>plugins/ravenclaude-core/.claude-plugin/plugin.json</code>. If they differ, re-run the two commands above (catalog update + reload). If they still differ, <strong>fully restart Claude Code</strong> &mdash; the cache lookup is read once at startup and the running session won&rsquo;t pick up a newly-extracted version mid-flight.</p>
  </section>
</div>
""".rstrip()
).strip()

_SIMULATOR_TAB_TEMPLATE = """
<div class="sim-layout">
  <section class="sim-intro">
    <h2>Preview a command's review</h2>
    <p>
      Type any shell command to see how command review (the Thing) would handle it &mdash;
      which category it lands in, its risk tier, which reviewers weigh in, and whether it
      would be allowed, auto-fixed, surfaced to you, or denied. It runs the
      <strong>real review engine</strong> &mdash; no command is run and no AI is called &mdash;
      so it matches what happens for real.
    </p>
    <div class="sim-input-row">
      <input type="text" id="sim-command" class="sim-input"
        placeholder="e.g. git push --force origin main"
        aria-label="Command to analyze" autocomplete="off" spellcheck="false">
      <button type="button" class="btn sim-analyze" id="sim-analyze-btn">Analyze</button>
    </div>
    <p class="sim-disabled-help" id="sim-disabled-help" hidden>
      Run <code>python3 scripts/serve-dashboards.py</code> to simulate against the live engine.
    </p>
  </section>

  <section class="sim-result" id="sim-result" hidden>
    <div class="sim-deny-banner" id="sim-deny-banner" hidden>
      &#9940; DENIED before any model runs<span id="sim-deny-reason"></span>
    </div>
    <div class="sim-result-grid">
      <div class="sim-field">
        <span class="sim-field-label">Category</span>
        <span class="sim-field-value" id="sim-category">&mdash;</span>
      </div>
      <div class="sim-field">
        <span class="sim-field-label">Risk tier</span>
        <span class="sim-tier-badge" id="sim-tier-badge">&mdash;</span>
      </div>
    </div>
    <div class="sim-seats-block">
      <span class="sim-field-label">Seats convened</span>
      <div class="sim-seats" id="sim-seats"></div>
    </div>
    <div class="sim-concerns-block" id="sim-concerns-block" hidden>
      <span class="sim-field-label">Concerns cited</span>
      <div class="sim-concerns" id="sim-concerns"></div>
    </div>
    <div class="sim-gate" id="sim-gate">
      <span class="sim-gate-label">Predicted outcome</span>
      <p class="sim-gate-text" id="sim-gate-text"></p>
    </div>
  </section>
</div>
""".strip()


_JS = r"""
/* generate-dashboards.py output — Settings tab JS (v5 schema: per-layer cards)
 * Vanilla; no dependencies. Reads the inline JSON Schema at #schema-data,
 * watches form changes, emits live v5 YAML preview + clipboard copy + download.
 *
 * v5 state shape per category:
 *   { user: "allow"|"ask"|"deny"|"inherit",
 *     local: "allow"|"ask"|"deny"|"inherit",
 *     project: "allow"|"ask"|"deny"|"inherit",
 *     overrides: { "<pattern>": { user, local, project } } }
 *
 * "inherit" means the layer emits no rule.  The effective badge is computed as
 *   deny > ask > allow; "all inherit" -> "inherit (Claude default)".
 *
 * `overrides` is the v0.19.0 per-permission, per-layer feature: one permission
 * can be tightened/relaxed at one layer independently of its category. An entry
 * whose three layers are all "inherit" is dropped (no override).
 *
 * Presets apply to the LOCAL layer only.
 */
(() => {
  const SCHEMA = JSON.parse(document.getElementById("schema-data").textContent);
  const presets = SCHEMA.presets || {};
  const props = SCHEMA.properties || {};
  const catProps = (props.categories && props.categories.properties) || {};

  const PLUGIN_KEY = "ravenclaude-dashboard-v5";

  /* Command-review panel defaults — mirror thing-decision.py's built-in panel.
   * The dashboard only authors per-seat models + the confidence threshold; the
   * timers / audit dir / timeout posture live in thing.yaml or the defaults. */
  const CR_DEFAULT = Object.freeze({
    /* enabled: master AND-gate. true = reviews fire when a category's thing is on.
     * false = all per-category reviews are paused (thing values preserved, not cleared).
     * Absent in storage / YAML ⇒ true (enabled). We only persist/emit when false. */
    enabled: true,
    forseti: "claude-opus-4-7",
    mimir: "claude-haiku-4-5",
    heimdall: "claude-haiku-4-5",
    thor: "claude-opus-4-7",
    confidence_threshold: 0.5,
    gate_floor: "high",
    /* Dev-repo lockout fix (v0.60.0): when true (and the gh-owner + marketplace.json
     * AND-gate passes) an abstaining panel defers (ASK) instead of failing closed.
     * Owner-gated — inert in any consumer repo. Emitted only when true. */
    dev_repo_exempt: false,
  });
  const CR_SEATS = ["forseti", "mimir", "heimdall", "thor"];
  const CR_MODELS = ["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5"];

  /* gate_floor headline control — enum medium | high | extreme, default high. */
  const GATE_FLOORS = ["medium", "high", "extreme"];

  /* Pipeline-stage guardrail config (model-free hooks; see the Pipeline tab).
   * Each mirrors the hook's own defaults so emitYaml only writes a block when the
   * user changed it — preserving "absent ⇒ default" so a consumer's untouched
   * posture is never bloated and nothing changes on /plugin marketplace update. */
  const RUNAWAY_DEFAULT = Object.freeze({ max_total: 1200, max_consecutive: 8, off: false });
  const DOD_DEFAULT = Object.freeze({ cmd: "", max_blocks: 8 });
  const DECISION_REVIEW_VALUES = ["off", "advisory", "binding"];
  const DECISION_REVIEW_DEFAULT = "off";

  /* Per-tier panel defaults — mirror thing-decision.py's built-in tier table.
   * Seats are forseti | mimir | heimdall (thor is the tie-breaker, never a seat).
   * The `low` tier runs no panel and is never authored here. */
  const TIER_SEATS = ["forseti", "mimir", "heimdall"];
  const TIERS = ["medium", "high", "extreme"];
  const TIER_DEFAULT = Object.freeze({
    medium: Object.freeze({ seats: ["mimir", "heimdall"], mandatory_seats: ["heimdall"], confidence_threshold: 0.5 }),
    high: Object.freeze({ seats: ["forseti", "mimir", "heimdall"], mandatory_seats: ["heimdall"], confidence_threshold: 0.6 }),
    extreme: Object.freeze({ seats: ["forseti", "mimir", "heimdall"], mandatory_seats: ["forseti", "heimdall"], confidence_threshold: 0.7 }),
  });
  /* mandatory_seats are fixed by the engine — the dashboard renders them
   * checked + disabled and never lets the user change them, so we clone the
   * defaults verbatim into the working tier state. */
  function freshTiers() {
    const out = {};
    for (const t of TIERS) {
      const d = TIER_DEFAULT[t];
      out[t] = {
        seats: d.seats.slice(),
        mandatory_seats: d.mandatory_seats.slice(),
        confidence_threshold: d.confidence_threshold,
      };
    }
    return out;
  }

  /* Pattern explanations loaded from a sibling JSON block. */
  let PATTERN_EXPLANATIONS = {};
  try {
    const el = document.getElementById("pattern-explanations-data");
    PATTERN_EXPLANATIONS = el ? JSON.parse(el.textContent) : {};
  } catch (e) {
    console.error("Failed to parse pattern-explanations:", e);
  }

  const SECTION_EXPLANATIONS = {
    "security_deny": {
      "title": "Danger Zone",
      "what": "Patterns that are ALWAYS denied regardless of your category levels. The deny rules survive every preset — applying any preset doesn't relax them. They're the floor.",
      "why": "Some actions are dangerous enough that no productivity tradeoff justifies them: reading credential files (.env, .pem, AWS credentials), recursive force-deletes (rm -rf), force-pushing git history (git push --force), and the 'curl | sh' install pattern. Click \"Blocked\" to flip a rule — the change persists after you save."
    }
  };

  /* 5-level names -> 4-value set used in v5 layers */
  function levelToLayerValue(level) {
    if (!level || level === "inherit") return "inherit";
    if (level === "deny") return "deny";
    if (level === "always-ask" || level === "mostly-ask") return "ask";
    if (level === "mostly-allow" || level === "autopilot") return "allow";
    if (level === "allow" || level === "ask") return level; /* already 4-value */
    return "inherit";
  }

  /* ── State ───────────────────────────────────────────────────────── */
  /* Each category: { user, local, project } all start as "inherit" except
   * local which is seeded from x-recommended (mapped to 4-value). */
  const state = {
    schema_version: 5,
    categories: {},
    security_deny: ((props.security_deny || {}).default || []).slice(),
    security_deny_baseline: ((props.security_deny || {}).default || []).slice(),
    /* Behavioral flag (NOT a permission): pause for design decisions? Default ON. */
    design_checkins: (typeof ((props.design_checkins || {}).default) === "boolean")
      ? props.design_checkins.default : true,
    command_review: Object.assign({}, CR_DEFAULT, { tiers: freshTiers(), mcp_allowed_servers: [] }),
    /* Pipeline-stage guardrails (model-free hooks). Cloned from the *_DEFAULT
     * constants; emitYaml writes each block only when it differs from default. */
    runaway: Object.assign({}, RUNAWAY_DEFAULT),
    decision_review: DECISION_REVIEW_DEFAULT,
    definition_of_done: Object.assign({}, DOD_DEFAULT),
    expanded: {},   /* category -> boolean */
  };

  /* Seed from DOM (which reflects schema defaults already rendered) */
  for (const k of Object.keys(catProps).sort()) {
    const sch = catProps[k];
    const rec = sch["x-recommended"] || "";
    const localDefault = levelToLayerValue(rec);
    state.categories[k] = { user: "inherit", local: localDefault, project: "inherit", overrides: {}, thing: false };
  }

  /* Read actual checked radios from DOM to pick up any rendered defaults */
  document.querySelectorAll('input[type="radio"][data-category][data-layer]').forEach(inp => {
    if (inp.checked) {
      const cat = inp.dataset.category;
      const layer = inp.dataset.layer;
      if (state.categories[cat] && ["user","local","project"].includes(layer)) {
        state.categories[cat][layer] = inp.value;
      }
    }
  });

  /* Restore persisted state */
  try {
    const saved = localStorage.getItem(PLUGIN_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (parsed.categories) {
        for (const [k, v] of Object.entries(parsed.categories)) {
          if (state.categories[k] && v && typeof v === "object") {
            for (const L of ["user","local","project"]) {
              if (["allow","ask","deny","inherit"].includes(v[L])) {
                state.categories[k][L] = v[L];
              }
            }
            /* per-permission overrides: keep only well-formed, non-all-inherit entries */
            if (v.overrides && typeof v.overrides === "object") {
              const restored = {};
              for (const [pat, o] of Object.entries(v.overrides)) {
                if (!o || typeof o !== "object") continue;
                const rec = { user: "inherit", local: "inherit", project: "inherit" };
                for (const L of ["user","local","project"]) {
                  if (["allow","ask","deny","inherit"].includes(o[L])) rec[L] = o[L];
                }
                if (rec.user !== "inherit" || rec.local !== "inherit" || rec.project !== "inherit") {
                  restored[pat] = rec;
                }
              }
              state.categories[k].overrides = restored;
            }
            /* per-category command-review toggle */
            if (typeof v.thing === "boolean") state.categories[k].thing = v.thing;
          }
        }
      }
      if (Array.isArray(parsed.security_deny)) {
        state.security_deny = parsed.security_deny.filter(
          p => state.security_deny_baseline.includes(p)
        );
      }
      if (parsed.expanded && typeof parsed.expanded === "object") {
        Object.assign(state.expanded, parsed.expanded);
      }
      if (typeof parsed.design_checkins === "boolean") {
        state.design_checkins = parsed.design_checkins;
      }
      /* Pipeline-stage guardrails (runaway / decision_review / definition_of_done
       * / dev_repo_exempt) — restored via the shared validator. */
      applyGuardrailConfig(parsed);
      /* command-review panel: keep only known seats/models + a valid threshold */
      if (parsed.command_review && typeof parsed.command_review === "object") {
        const pcr = parsed.command_review;
        /* Master enable — absent or non-boolean ⇒ default true (enabled).
         * We store it only when false, so a missing key means enabled. */
        if (typeof pcr.enabled === "boolean") state.command_review.enabled = pcr.enabled;
        for (const s of CR_SEATS) {
          if (CR_MODELS.includes(pcr[s])) {
            state.command_review[s] = pcr[s];
          }
        }
        const t = parseFloat(pcr.confidence_threshold);
        if (!Number.isNaN(t) && t >= 0 && t <= 1) state.command_review.confidence_threshold = t;
        /* gate_floor — only one of the known enum values */
        if (GATE_FLOORS.includes(pcr.gate_floor)) state.command_review.gate_floor = pcr.gate_floor;
        /* per-tier overrides — keep well-formed entries; mandatory_seats stay
         * pinned to the engine defaults (the UI can't change them). */
        if (pcr.tiers && typeof pcr.tiers === "object") {
          for (const tier of TIERS) {
            const pt = pcr.tiers[tier];
            if (!pt || typeof pt !== "object") continue;
            const dst = state.command_review.tiers[tier];
            if (Array.isArray(pt.seats)) {
              const seats = pt.seats.filter(s => TIER_SEATS.includes(s));
              /* mandatory seats are always present regardless of what was stored */
              for (const m of dst.mandatory_seats) if (!seats.includes(m)) seats.push(m);
              dst.seats = TIER_SEATS.filter(s => seats.includes(s));
            }
            const tt = parseFloat(pt.confidence_threshold);
            if (!Number.isNaN(tt) && tt >= 0 && tt <= 1) dst.confidence_threshold = tt;
          }
        }
        /* MCP server allowlist (§MCP identity) — command_review.mcp.allowed_servers */
        if (pcr.mcp && typeof pcr.mcp === "object" && Array.isArray(pcr.mcp.allowed_servers)) {
          const seen = new Set();
          state.command_review.mcp_allowed_servers = pcr.mcp.allowed_servers
            .filter(s => typeof s === "string" && /^[A-Za-z0-9._-]+$/.test(s) && !seen.has(s) && seen.add(s));
        }
      }
    }
  } catch (e) {
    console.warn("Could not restore saved state:", e);
  }

  /* Design check-ins toggle (behavioral flag, not a permission) */
  const DC_PROP = props.design_checkins || {};
  const DC_ON_LABEL = DC_PROP["x-on-label"] || "On — pause for design decisions";
  const DC_OFF_LABEL = DC_PROP["x-off-label"] || "Off — nonstop";
  function syncDesignCheckins() {
    const cb = document.getElementById("design-checkins-toggle");
    const lbl = document.getElementById("design-checkins-state");
    if (cb) cb.checked = !!state.design_checkins;
    if (lbl) lbl.textContent = state.design_checkins ? DC_ON_LABEL : DC_OFF_LABEL;
  }

  /* Command-review master enable (AND-gate, not bulk-setter).
   * Syncs the checkbox + the status label beneath the master row.
   * Does NOT touch per-category `thing` values. */
  function syncMasterEnable() {
    const cb = document.getElementById("cr-master-enable");
    const lbl = document.getElementById("crb-master-state");
    const enabled = !!state.command_review.enabled;
    if (cb) cb.checked = enabled;
    if (lbl) {
      lbl.textContent = enabled
        ? "On — reviews fire when a category’s toggle is on"
        : "Paused — per-category toggles are preserved but no reviews will run";
    }
    /* Also update the header-level scales icon state */
    const headerIcon = document.querySelector(".command-review-block .crb-title-row .review-scales-icon");
    if (headerIcon) {
      /* header icon reflects master state only — "reviewed" if enabled, "paused" if not */
      const s = enabled ? "reviewed" : "paused";
      headerIcon.setAttribute("data-review-state", s);
      headerIcon.setAttribute("aria-label", enabled
        ? "Command review: master on"
        : "Command review: master paused");
    }
  }

  /* Sync DOM radios to state */
  function syncDomToState() {
    document.querySelectorAll('input[type="radio"][data-category][data-layer]').forEach(inp => {
      const cat = inp.dataset.category;
      const layer = inp.dataset.layer;
      if (state.categories[cat]) {
        inp.checked = inp.value === state.categories[cat][layer];
      }
    });
    /* Sync per-permission override selects + their override tint */
    document.querySelectorAll("select.ov-select[data-category][data-pattern][data-ov-layer]").forEach(sel => {
      const cat = sel.dataset.category;
      const pat = sel.dataset.pattern;
      const layer = sel.dataset.ovLayer;
      const ov = (state.categories[cat] || {}).overrides || {};
      const rec = ov[pat];
      const val = (rec && rec[layer]) ? rec[layer] : "inherit";
      sel.value = val;
      sel.classList.toggle("ov-set", val !== "inherit");
    });
    /* Restore expanded state */
    document.querySelectorAll(".cat-card[data-category]").forEach(card => {
      const cat = card.dataset.category;
      if (state.expanded[cat]) card.setAttribute("open", "");
    });
    /* Sync security_deny checkboxes */
    document.querySelectorAll(".sec-deny-checkbox").forEach(cb => {
      cb.checked = state.security_deny.includes(cb.value);
    });
    /* Sync per-category command-review (the Thing) toggles */
    document.querySelectorAll('input[type="checkbox"][data-thing-category]').forEach(cb => {
      const cat = cb.dataset.thingCategory;
      if (state.categories[cat]) cb.checked = !!state.categories[cat].thing;
    });
    /* Sync the global command-review panel controls */
    document.querySelectorAll("select.cr-seat-select[data-cr-seat]").forEach(sel => {
      const seat = sel.dataset.crSeat;
      if (state.command_review[seat]) sel.value = state.command_review[seat];
    });
    {
      const thr = document.getElementById("cr-threshold");
      if (thr) thr.value = String(state.command_review.confidence_threshold);
    }
    {
      const mcpIn = document.getElementById("cr-mcp-allow");
      if (mcpIn) mcpIn.value = (state.command_review.mcp_allowed_servers || []).join(", ");
    }
    /* Sync the gate_floor segmented control */
    document.querySelectorAll('input[type="radio"][data-gate-floor]').forEach(inp => {
      inp.checked = inp.dataset.gateFloor === state.command_review.gate_floor;
    });
    /* Sync per-tier seat checkboxes + thresholds */
    document.querySelectorAll('input[type="checkbox"][data-tier-seat]').forEach(cb => {
      const tier = cb.dataset.tier;
      const seat = cb.dataset.tierSeat;
      const tcfg = state.command_review.tiers[tier];
      if (!tcfg) return;
      if (tcfg.mandatory_seats.includes(seat)) {
        cb.checked = true;   /* required seats stay checked + disabled */
      } else {
        cb.checked = tcfg.seats.includes(seat);
      }
    });
    document.querySelectorAll("input.tier-threshold-input[data-tier-threshold]").forEach(inp => {
      const tier = inp.dataset.tierThreshold;
      const tcfg = state.command_review.tiers[tier];
      if (tcfg) inp.value = String(tcfg.confidence_threshold);
    });
    syncDesignCheckins();
    syncMasterEnable();
  }
  syncDomToState();

  /* ── Review-state icon helpers ───────────────────────────────────── */
  /* Computes the effective review state for a category:
   *   reviewed — master on AND per-category thing on
   *   paused   — master off AND per-category thing on (will resume if master re-enabled)
   *   off      — per-category thing off (regardless of master)
   * The icon is rendered server-side to 'off'; this function corrects it to
   * the live effective state after restore and on every relevant change. */
  const REVIEW_STATE_LABELS = {
    reviewed: "Command review: on",
    paused: "Command review: on, paused by master",
    off: "Command review: off",
  };
  const REVIEW_MICRO_LABELS = {
    reviewed: "on",
    paused: "paused",
    off: "off",
  };

  function effectiveReviewState(cat) {
    const enabled = !!state.command_review.enabled;
    const thing = !!(state.categories[cat] || {}).thing;
    if (!thing) return "off";
    return enabled ? "reviewed" : "paused";
  }

  function updateReviewIcon(cat) {
    /* Update the icon in the category card */
    const cardIcon = document.querySelector(`.cat-thing-scales[data-scales-for="${CSS.escape(cat)}"] .review-scales-icon`);
    /* Update the icon in the top summary grid */
    const summaryCell = document.querySelector(`.cr-summary-cell[data-cr-summary-cat="${CSS.escape(cat)}"]`);
    const summaryIcon = summaryCell && summaryCell.querySelector(".review-scales-icon");
    const summaryMicro = summaryCell && summaryCell.querySelector(".cr-summary-micro");
    const rs = effectiveReviewState(cat);
    const label = REVIEW_STATE_LABELS[rs] + " — " + cat;
    if (cardIcon) {
      cardIcon.setAttribute("data-review-state", rs);
      cardIcon.setAttribute("aria-label", label);
    }
    if (summaryIcon) {
      summaryIcon.setAttribute("data-review-state", rs);
      summaryIcon.setAttribute("aria-label", label);
    }
    if (summaryMicro) {
      summaryMicro.textContent = REVIEW_MICRO_LABELS[rs];
      summaryMicro.setAttribute("data-state", rs);
    }
  }

  function updateReviewIcons() {
    for (const cat of Object.keys(state.categories)) {
      updateReviewIcon(cat);
    }
    syncMasterEnable();
  }

  /* ── Effective badge computation ─────────────────────────────────── */
  function effectiveBucket(cat) {
    const layers = state.categories[cat];
    if (!layers) return "inherit";
    const vals = [layers.user, layers.local, layers.project];
    if (vals.includes("deny")) return "deny";
    if (vals.includes("ask")) return "ask";
    if (vals.includes("allow")) return "allow";
    return "inherit";
  }

  const BADGE_LABELS = {
    "deny":    "⛔ deny",
    "ask":     "🟡 ask",
    "allow":   "🟢 allow",
    "inherit": "— inherit (Claude default)",
  };
  const BADGE_CLASSES = {
    "deny": "badge-deny", "ask": "badge-ask",
    "allow": "badge-allow", "inherit": "badge-inherit",
  };

  function updateBadge(cat) {
    const badge = document.querySelector(`.cat-card-badge[data-badge-for="${CSS.escape(cat)}"]`);
    if (!badge) return;
    const eff = effectiveBucket(cat);
    badge.textContent = BADGE_LABELS[eff] || eff;
    badge.className = "cat-card-badge " + (BADGE_CLASSES[eff] || "badge-inherit");
    badge.setAttribute("aria-label", "Effective level: " + (eff === "inherit" ? "inherit (Claude default)" : eff));
  }

  function updateProjectWarn(cat) {
    const warn = document.querySelector(`.cat-project-warn[data-warn-for="${CSS.escape(cat)}"]`);
    if (!warn) return;
    warn.hidden = (state.categories[cat] || {}).project !== "allow";
  }

  function updateOverrideCount(cat) {
    const badge = document.querySelector(`.pattern-override-count[data-for="${CSS.escape(cat)}"]`);
    if (!badge) return;
    const ov = (state.categories[cat] || {}).overrides || {};
    const n = Object.keys(ov).length;
    badge.textContent = n === 1 ? "1 overridden" : `${n} overridden`;
    badge.classList.toggle("has-overrides", n > 0);
  }

  function updateAllBadges() {
    for (const cat of Object.keys(state.categories)) {
      updateBadge(cat);
      updateProjectWarn(cat);
      updateOverrideCount(cat);
    }
    updateReviewIcons();
  }

  /* ── YAML emit (v5 schema) ───────────────────────────────────────── */
  function quoteYamlKey(s) {
    return `"${s.replace(/\\/g, "\\\\").replace(/"/g, "\\\"")}"`;
  }

  /* Shared guardrail-config hydrator — used by BOTH the localStorage restore and
   * the live /__read path. The dashboard state and the committed YAML express
   * runaway / decision_review / definition_of_done / command_review.dev_repo_exempt
   * with the same shape, so one validator covers both. Mutates state defensively:
   * a missing / malformed key leaves the existing (default) value untouched.
   * Returns true if anything was applied. */
  function applyGuardrailConfig(src) {
    if (!src || typeof src !== "object") return false;
    let touched = false;
    const rw = src.runaway;
    if (rw && typeof rw === "object") {
      const mt = parseInt(rw.max_total, 10);
      if (Number.isFinite(mt) && mt > 0) { state.runaway.max_total = mt; touched = true; }
      const mc = parseInt(rw.max_consecutive, 10);
      if (Number.isFinite(mc) && mc > 0) { state.runaway.max_consecutive = mc; touched = true; }
      if (typeof rw.off === "boolean") { state.runaway.off = rw.off; touched = true; }
    } else if (rw === false || rw === "off") {
      /* scalar `runaway: off` form (YAML `off` parses to boolean false) */
      state.runaway.off = true; touched = true;
    }
    if (DECISION_REVIEW_VALUES.includes(src.decision_review)) {
      state.decision_review = src.decision_review; touched = true;
    }
    const dod = src.definition_of_done;
    if (dod && typeof dod === "object") {
      if (typeof dod.cmd === "string") { state.definition_of_done.cmd = dod.cmd; touched = true; }
      const mb = parseInt(dod.max_blocks, 10);
      if (Number.isFinite(mb) && mb > 0) { state.definition_of_done.max_blocks = mb; touched = true; }
    }
    const cr = src.command_review;
    if (cr && typeof cr === "object" && typeof cr.dev_repo_exempt === "boolean") {
      state.command_review.dev_repo_exempt = cr.dev_repo_exempt; touched = true;
    }
    return touched;
  }

  function emitYaml() {
    const lines = [
      "# Comfort-posture for Claude Code agents (v5 — per-layer).",
      "# Save to .ravenclaude/comfort-posture.yaml in your project root.",
      "# The /set-posture skill translates this into user/local/project settings files.",
      "schema_version: 5",
      "",
      "# Pause for design / architectural decisions? Behavioral flag, separate from permissions.",
      `design_checkins: ${state.design_checkins}`,
      "",
    ];

    /* command_review — the tribunal panel. Emitted only when the user has
     * customized it, so an untouched dashboard leaves thing.yaml / the built-in
     * defaults in control (this block has higher precedence than thing.yaml). */
    const cr = state.command_review;
    function tierChanged(tier) {
      const d = TIER_DEFAULT[tier], t = cr.tiers[tier];
      if (t.confidence_threshold !== d.confidence_threshold) return true;
      if (t.seats.length !== d.seats.length) return true;
      return t.seats.some(s => !d.seats.includes(s));
    }
    const tiersChanged = TIERS.some(tierChanged);
    /* cr.enabled === false must always be persisted so a master-OFF state survives
     * a page reload even when no other setting has changed. Absent ⇒ true (enabled). */
    const masterOff = cr.enabled === false;
    const crChanged = masterOff
      || CR_SEATS.some(s => cr[s] !== CR_DEFAULT[s])
      || cr.confidence_threshold !== CR_DEFAULT.confidence_threshold
      || cr.gate_floor !== CR_DEFAULT.gate_floor
      || cr.dev_repo_exempt === true
      || (cr.mcp_allowed_servers && cr.mcp_allowed_servers.length > 0)
      || tiersChanged;
    if (crChanged) {
      lines.push("# Command-review tribunal panel (the Thing). Overrides .ravenclaude/thing.yaml.");
      lines.push("command_review:");
      /* Only emit 'enabled: false'; omit the key entirely when true (absent ⇒ true). */
      if (masterOff) lines.push("  enabled: false");
      lines.push("  panel:");
      for (const s of CR_SEATS) {
        lines.push(`    ${s}:`);
        lines.push(`      model: ${cr[s]}`);
      }
      lines.push(`  confidence_threshold: ${cr.confidence_threshold}`);
      lines.push(`  gate_floor: ${cr.gate_floor}`);
      /* Dev-repo lockout fix — emitted only when true (owner-gated, inert in any
       * consumer repo). Lets an abstaining panel defer (ASK) instead of failing
       * closed for the verified marketplace maintainer. */
      if (cr.dev_repo_exempt === true) lines.push(`  dev_repo_exempt: true`);
      /* MCP server allowlist (§MCP identity) — emitted only when non-empty. The
       * tribunal denies a write verb from a server NOT on this list pre-LLM. */
      if (cr.mcp_allowed_servers && cr.mcp_allowed_servers.length) {
        lines.push("  mcp:");
        lines.push(`    allowed_servers: [${cr.mcp_allowed_servers.join(", ")}]`);
      }
      /* Per-tier panel — emitted only when a tier differs from its default, so
       * an untouched advanced section leaves the engine tier table in control.
       * low has no panel and is never emitted. */
      if (tiersChanged) {
        lines.push("  tiers:");
        for (const tier of TIERS) {
          const t = cr.tiers[tier];
          const seats = TIER_SEATS.filter(s => t.seats.includes(s));
          const mand = TIER_SEATS.filter(s => t.mandatory_seats.includes(s));
          lines.push(`    ${tier}:`);
          lines.push(`      seats: [${seats.join(", ")}]`);
          lines.push(`      mandatory_seats: [${mand.join(", ")}]`);
          lines.push(`      confidence_threshold: ${t.confidence_threshold}`);
        }
      }
      lines.push("");
    }

    /* ── Pipeline-stage guardrails (model-free hooks) ──────────────────────
     * Each block is emitted ONLY when it differs from the hook's built-in
     * default, so an untouched posture stays minimal and "absent ⇒ default"
     * holds — nothing changes for a consumer on /plugin marketplace update
     * unless they explicitly tune a value here. */
    const rw = state.runaway;
    if (rw.off === true) {
      lines.push("# Runaway brake — disabled for this repo.");
      lines.push("runaway: off");
      lines.push("");
    } else if (rw.max_total !== RUNAWAY_DEFAULT.max_total
            || rw.max_consecutive !== RUNAWAY_DEFAULT.max_consecutive) {
      lines.push("# Runaway brake — bounds tool-call depth (loop/runaway protection).");
      lines.push("runaway:");
      lines.push(`  max_consecutive: ${rw.max_consecutive}`);
      lines.push(`  max_total: ${rw.max_total}`);
      lines.push("");
    }

    if (DECISION_REVIEW_VALUES.includes(state.decision_review)
        && state.decision_review !== DECISION_REVIEW_DEFAULT) {
      lines.push("# Yes/no decision routing through the tribunal (off | advisory | binding).");
      lines.push(`decision_review: ${state.decision_review}`);
      lines.push("");
    }

    const dod = state.definition_of_done;
    if (dod.cmd && dod.cmd.trim()) {
      lines.push("# Definition-of-done gate — runs on Stop; blocks 'done' until it passes.");
      lines.push("definition_of_done:");
      lines.push(`  cmd: ${quoteYamlKey(dod.cmd)}`);
      lines.push(`  max_blocks: ${dod.max_blocks}`);
      lines.push("");
    }

    /* security_deny */
    const activeDeny = state.security_deny_baseline.filter(
      p => state.security_deny.includes(p)
    );
    if (activeDeny.length) {
      lines.push("# Always-on deny rules — layer-independent floor.");
      lines.push("security_deny:");
      for (const p of activeDeny) lines.push(`  - ${quoteYamlKey(p)}`);
      lines.push("");
    }

    lines.push("categories:");
    for (const k of Object.keys(state.categories).sort()) {
      const cat = state.categories[k];
      const u = cat.user, l = cat.local, p = cat.project;
      /* Per-permission overrides: only those with a non-inherit layer count. */
      const ov = cat.overrides || {};
      const ovKeys = Object.keys(ov).filter(pat => {
        const o = ov[pat] || {};
        return o.user !== "inherit" || o.local !== "inherit" || o.project !== "inherit";
      }).sort();
      lines.push(`  ${k}:`);
      lines.push(`    user: ${u}`);
      lines.push(`    local: ${l}`);
      lines.push(`    project: ${p}`);
      /* Command-review (the Thing) toggle — only emitted when on. */
      if (cat.thing === true) lines.push(`    thing: on`);
      if (ovKeys.length) {
        lines.push(`    overrides:`);
        for (const pat of ovKeys) {
          const o = ov[pat];
          lines.push(`      ${quoteYamlKey(pat)}:`);
          lines.push(`        user: ${o.user || "inherit"}`);
          lines.push(`        local: ${o.local || "inherit"}`);
          lines.push(`        project: ${o.project || "inherit"}`);
        }
      }
    }
    return lines.join("\n") + "\n";
  }

  function persistState() {
    try {
      localStorage.setItem(PLUGIN_KEY, JSON.stringify({
        categories: state.categories,
        security_deny: state.security_deny,
        design_checkins: state.design_checkins,
        command_review: state.command_review,
        runaway: state.runaway,
        decision_review: state.decision_review,
        definition_of_done: state.definition_of_done,
        expanded: state.expanded,
      }));
    } catch (e) { /* storage full — ignore */ }
  }

  function render() {
    document.getElementById("yaml-output").textContent = emitYaml();
    updateAllBadges();
    persistState();
  }

  /* ── Form change wiring ─────────────────────────────────────────── */
  /* Command-review master enable — cascades to every live per-category toggle.
   * When the master is flipped, every non-disabled data-thing-category checkbox
   * is set to match and its state entry is updated.  Per-category toggles remain
   * independently operable after the cascade. */
  {
    const masterCb = document.getElementById("cr-master-enable");
    if (masterCb) {
      masterCb.addEventListener("change", () => {
        /* enabled: true is the default; only store/emit when false */
        state.command_review.enabled = masterCb.checked ? true : false;
        /* Cascade master state down to every live per-category toggle */
        document.querySelectorAll('input[type="checkbox"][data-thing-category]').forEach(cb => {
          if (cb.disabled) return;
          cb.checked = masterCb.checked;
          const cat = cb.dataset.thingCategory;
          if (state.categories[cat]) state.categories[cat].thing = masterCb.checked;
        });
        syncMasterEnable();
        updateReviewIcons();
        flagUnsaved();
        render();
      });
    }
  }

  /* Design check-ins toggle (behavioral flag, not a permission) */
  {
    const dcToggle = document.getElementById("design-checkins-toggle");
    if (dcToggle) {
      dcToggle.addEventListener("change", () => {
        state.design_checkins = dcToggle.checked;
        syncDesignCheckins();
        flagUnsaved();
        render();
      });
    }
  }

  document.querySelectorAll('input[type="radio"][data-category][data-layer]').forEach(inp => {
    inp.addEventListener("change", () => {
      const cat = inp.dataset.category;
      const layer = inp.dataset.layer;
      if (state.categories[cat] && ["user","local","project"].includes(layer)) {
        state.categories[cat][layer] = inp.value;
      }
      flagUnsaved();
      render();
    });
  });

  /* Per-permission override selects (User / Local / Project per permission) */
  document.querySelectorAll("select.ov-select[data-category][data-pattern][data-ov-layer]").forEach(sel => {
    sel.addEventListener("change", () => {
      const cat = sel.dataset.category;
      const pat = sel.dataset.pattern;
      const layer = sel.dataset.ovLayer;
      const c = state.categories[cat];
      if (!c) return;
      const ov = c.overrides || (c.overrides = {});
      const rec = ov[pat] || (ov[pat] = { user: "inherit", local: "inherit", project: "inherit" });
      rec[layer] = sel.value;
      sel.classList.toggle("ov-set", sel.value !== "inherit");
      /* Drop the entry entirely once it overrides nothing, so emitYaml stays clean */
      if (rec.user === "inherit" && rec.local === "inherit" && rec.project === "inherit") {
        delete ov[pat];
      }
      updateOverrideCount(cat);
      flagUnsaved();
      render();
    });
  });

  /* Per-category command-review (the Thing) toggle — writes `thing: on` */
  document.querySelectorAll('input[type="checkbox"][data-thing-category]').forEach(cb => {
    cb.addEventListener("change", () => {
      const cat = cb.dataset.thingCategory;
      if (state.categories[cat]) state.categories[cat].thing = cb.checked;
      updateReviewIcon(cat);
      flagUnsaved();
      render();
    });
  });

  /* ── Header command-review switch isolation ──────────────────────────
   * A <label> or <input> inside a <summary> will, by default, both:
   *   (a) toggle the checkbox/label, AND
   *   (b) toggle the parent <details> open/closed.
   * We intercept the click on the header switch label, call
   * preventDefault() + stopPropagation() to cancel the details-toggle,
   * then manually flip the checkbox and fire a synthetic "change" event
   * so the data-thing-category change handler above still runs exactly once.
   * Guard: disabled checkboxes (Preview state) are left alone.
   * Keyboard note: Space on a focused checkbox triggers a "click" event
   * *on the checkbox itself*, not on the label, so this handler fires for
   * keyboard users too — the behavior is consistent across input methods.
   */
  document.querySelectorAll(".cat-hdr-switch").forEach(label => {
    label.addEventListener("click", e => {
      const cb = label.querySelector('input[type="checkbox"]');
      if (!cb || cb.disabled) return;
      e.preventDefault();
      e.stopPropagation();
      cb.checked = !cb.checked;
      cb.dispatchEvent(new Event("change", { bubbles: true }));
    });
  });

  /* Global command-review panel — per-seat model selects + confidence threshold */
  document.querySelectorAll("select.cr-seat-select[data-cr-seat]").forEach(sel => {
    sel.addEventListener("change", () => {
      const seat = sel.dataset.crSeat;
      if (CR_SEATS.includes(seat) && CR_MODELS.includes(sel.value)) {
        state.command_review[seat] = sel.value;
        flagUnsaved();
        render();
      }
    });
  });
  {
    const thr = document.getElementById("cr-threshold");
    if (thr) {
      thr.addEventListener("change", () => {
        let t = parseFloat(thr.value);
        if (Number.isNaN(t)) t = CR_DEFAULT.confidence_threshold;
        t = Math.min(1, Math.max(0, t));
        state.command_review.confidence_threshold = t;
        thr.value = String(t);
        flagUnsaved();
        render();
      });
    }
  }

  /* MCP server allowlist (§MCP identity) — comma/space-separated server names,
   * validated to the tool-name charset, deduped, normalized back into the field. */
  {
    const mcpIn = document.getElementById("cr-mcp-allow");
    if (mcpIn) {
      mcpIn.addEventListener("change", () => {
        const seen = new Set();
        const servers = mcpIn.value.split(/[\s,]+/)
          .map(s => s.trim())
          .filter(s => s && /^[A-Za-z0-9._-]+$/.test(s) && !seen.has(s) && seen.add(s));
        state.command_review.mcp_allowed_servers = servers;
        mcpIn.value = servers.join(", ");
        flagUnsaved();
        render();
      });
    }
  }

  /* gate_floor headline control (medium | high | extreme) */
  document.querySelectorAll('input[type="radio"][data-gate-floor]').forEach(inp => {
    inp.addEventListener("change", () => {
      if (inp.checked && GATE_FLOORS.includes(inp.dataset.gateFloor)) {
        state.command_review.gate_floor = inp.dataset.gateFloor;
        flagUnsaved();
        render();
      }
    });
  });

  /* Per-tier seat checkboxes — mandatory seats are disabled, so only optional
   * seats fire here. Keeps the tier's seat list canonically ordered. */
  document.querySelectorAll('input[type="checkbox"][data-tier-seat]').forEach(cb => {
    cb.addEventListener("change", () => {
      const tier = cb.dataset.tier;
      const seat = cb.dataset.tierSeat;
      const tcfg = state.command_review.tiers[tier];
      if (!tcfg || !TIER_SEATS.includes(seat)) return;
      if (tcfg.mandatory_seats.includes(seat)) { cb.checked = true; return; }
      const set = new Set(tcfg.seats);
      if (cb.checked) set.add(seat); else set.delete(seat);
      /* mandatory seats are always present */
      for (const m of tcfg.mandatory_seats) set.add(m);
      tcfg.seats = TIER_SEATS.filter(s => set.has(s));
      flagUnsaved();
      render();
    });
  });

  /* Per-tier confidence thresholds */
  document.querySelectorAll("input.tier-threshold-input[data-tier-threshold]").forEach(inp => {
    inp.addEventListener("change", () => {
      const tier = inp.dataset.tierThreshold;
      const tcfg = state.command_review.tiers[tier];
      if (!tcfg) return;
      let t = parseFloat(inp.value);
      if (Number.isNaN(t)) t = TIER_DEFAULT[tier].confidence_threshold;
      t = Math.min(1, Math.max(0, t));
      tcfg.confidence_threshold = t;
      inp.value = String(t);
      flagUnsaved();
      render();
    });
  });

  /* Track card expand/collapse for localStorage */
  document.querySelectorAll(".cat-card[data-category]").forEach(card => {
    card.addEventListener("toggle", () => {
      const cat = card.dataset.category;
      state.expanded[cat] = card.hasAttribute("open");
      persistState();
    });
  });

  /* security_deny checkboxes */
  document.querySelectorAll(".sec-deny-checkbox").forEach(cb => {
    cb.addEventListener("change", () => {
      const pat = cb.value;
      if (cb.checked) {
        if (!state.security_deny.includes(pat)) state.security_deny.push(pat);
      } else {
        state.security_deny = state.security_deny.filter(p => p !== pat);
      }
      flagUnsaved();
      render();
    });
  });

  /* ── Preset application (applies to LOCAL layer) ─────────────────── */
  /* Map old 5-level preset values to 4-value layer set */
  document.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const preset = presets[btn.dataset.preset];
      if (!preset) return;
      const ok = confirm(
        `Apply the "${btn.dataset.preset}" preset?\n\n` +
        `This sets every category's LOCAL layer. User and Project layers are untouched.\n\n` +
        (preset._description || "")
      );
      if (!ok) return;
      const presetCats = preset.categories || {};
      for (const k of Object.keys(state.categories)) {
        const raw = presetCats[k];
        state.categories[k].local = raw ? levelToLayerValue(raw) : "inherit";
      }
      /* Sync DOM radios for local layer */
      document.querySelectorAll('input[type="radio"][data-layer="local"]').forEach(inp => {
        const cat = inp.dataset.category;
        if (state.categories[cat]) {
          inp.checked = inp.value === state.categories[cat].local;
        }
      });
      flagUnsaved();
      render();
      toast(`Applied "${btn.dataset.preset}" preset to Local layer`);
    });
  });

  /* ── Save to repo via server-side /__save endpoint ──────────────── */
  /* CSRF bootstrap. Belt-and-suspenders on top of the server's Origin/Host
   * guard: the server emits a per-process random token; we fetch it once on
   * load via GET /__csrf and attach it as X-CSRF-Token on every state-changing
   * POST. On a static host (GitHub Pages, file://) /__csrf 404s — `csrfHeaders`
   * resolves to `{}` and the downstream POSTs end up hitting a no-server path
   * that already 404/405s with a friendly "no local server" surface. */
  const _csrfPromise = (async () => {
    try {
      const res = await fetch("/__csrf", { headers: { "Accept": "application/json" } });
      if (!res.ok) return null;
      const j = await res.json();
      return (j && typeof j.token === "string") ? j.token : null;
    } catch (e) {
      return null;
    }
  })();
  async function csrfHeaders() {
    const t = await _csrfPromise;
    return t ? { "X-CSRF-Token": t } : {};
  }

  /* The primary save target: writes directly into .ravenclaude/<file> in
   * the agent's project. Only available when the page is served by
   * scripts/serve-dashboards.py (which exposes POST /__save). When the
   * page is served by `python3 -m http.server` or opened via file://,
   * the endpoint is absent; we hide the button and surface the
   * "start the local server" help line. */
  const REPO_TARGET = ".ravenclaude/comfort-posture.yaml";
  const saveRepoBtn = document.getElementById("save-repo-btn");
  const saveRepoHelp = document.getElementById("save-repo-help");
  const saveRepoWarn = document.getElementById("save-repo-warn");
  const noServerHelp = document.getElementById("no-server-help");

  async function probeRepoEndpoint() {
    try {
      const res = await fetch("/__save", { method: "HEAD" });
      return res.ok;
    } catch (e) {
      return false;
    }
  }

  /* No local server behind this page (the published/static copy, or the local
   * server isn't running). Explain it plainly and steer to the working paths
   * instead of surfacing a raw status code. */
  function showNoServer() {
    setStatus("no local server — changes NOT saved", "status-error");
    if (saveRepoBtn) saveRepoBtn.hidden = true;
    if (saveRepoHelp) saveRepoHelp.hidden = true;
    if (saveRepoWarn) saveRepoWarn.hidden = true;
    if (noServerHelp) noServerHelp.hidden = false;
    toast("No local server to save to — run 'ravenclaude dashboard', or use Download. See the note above.");
  }

  async function saveToRepo() {
    saveRepoBtn.disabled = true;
    setStatus("saving to repo…", "status-unsaved");
    try {
      const res = await fetch("/__save", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...(await csrfHeaders()) },
        body: JSON.stringify({ path: REPO_TARGET, content: emitYaml() })
      });
      // 404/405 = there is no /__save endpoint behind this page (the published
      // static copy on github.io, or a plain file/http server). Don't leak a raw
      // status code — explain that this page has no server and offer the real paths.
      if (res.status === 404 || res.status === 405) {
        showNoServer();
        return;
      }
      if (!res.ok) {
        const errText = await res.text().catch(() => "");
        setStatus("save failed — check your connection or try restarting the dashboard server", "status-error");
        console.error("Save-to-repo failed:", res.status, errText);
        return;
      }
      const j = await res.json();
      // Hide any previous apply-error block on a fresh successful attempt
      const applyErrBlock = document.getElementById("apply-error-block");
      const applyErrDetail = document.getElementById("apply-error-detail");
      if (applyErrBlock) applyErrBlock.hidden = true;
      if (j.applied) {
        setStatus(`saved & applied to settings.json`, "status-saved");
        toast(`Saved ${j.saved} and applied to .claude/settings.json`);
        if (j.apply_summary) console.info("set-posture:\n" + j.apply_summary);
      } else if (j.apply_error) {
        // The YAML saved, but the translator failed — surface it on-page.
        setStatus("saved — settings.json not updated (see below)", "status-error");
        toast(`Saved ${j.saved}, but settings.json was NOT updated`);
        if (applyErrBlock) applyErrBlock.hidden = false;
        if (applyErrDetail) applyErrDetail.textContent = j.apply_error;
        console.error("set-posture apply failed:", j.apply_error);
      } else {
        setStatus(`saved to ${j.saved}`, "status-saved");
        toast(`Saved to ${j.saved} (${j.bytes} bytes)`);
      }
    } catch (err) {
      // A TypeError/network failure here usually also means no local server
      // (static host, or a blocked request) — treat it the same friendly way.
      showNoServer();
      console.error(err);
    } finally {
      saveRepoBtn.disabled = false;
    }
  }

  saveRepoBtn.addEventListener("click", saveToRepo);

  /* Show or hide the save-to-repo button based on endpoint availability. */
  probeRepoEndpoint().then(available => {
    if (available) {
      saveRepoBtn.hidden = false;
      saveRepoHelp.hidden = false;
      if (saveRepoWarn) saveRepoWarn.hidden = false;
    } else {
      noServerHelp.hidden = false;
    }
  });

  /* ── Auto-save via File System Access API ───────────────────────── */
  /* Chrome/Edge/Opera: user picks a file once; we persist the handle in
   * IndexedDB and write on every change (debounced). Firefox/Safari:
   * feature-detect, hide the button, show a help line. */
  const HAS_FSA = typeof window.showSaveFilePicker === "function";
  const connectBtn = document.getElementById("connect-btn");
  const disconnectBtn = document.getElementById("disconnect-btn");
  const connectedRow = document.getElementById("connected-row");
  const connectedFilename = document.getElementById("connected-filename");
  const statusEl = document.getElementById("yaml-status");
  const noApiHelp = document.getElementById("no-api-help");

  let fileHandle = null;

  function setStatus(text, cls) {
    statusEl.textContent = text;
    statusEl.className = "yaml-status " + (cls || "");
  }

  /* Minimal IndexedDB wrapper — one DB, one store, two operations.
   * IndexedDB is the only way to persist a FileSystemFileHandle across reloads. */
  function idbOpen() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open("ravenclaude-dashboard", 1);
      req.onupgradeneeded = () => req.result.createObjectStore("handles");
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }
  async function idbSet(key, val) {
    const db = await idbOpen();
    return new Promise((resolve, reject) => {
      const tx = db.transaction("handles", "readwrite");
      tx.objectStore("handles").put(val, key);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  }
  async function idbGet(key) {
    const db = await idbOpen();
    return new Promise((resolve, reject) => {
      const tx = db.transaction("handles", "readonly");
      const req = tx.objectStore("handles").get(key);
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => reject(req.error);
    });
  }
  async function idbDel(key) {
    const db = await idbOpen();
    return new Promise((resolve, reject) => {
      const tx = db.transaction("handles", "readwrite");
      tx.objectStore("handles").delete(key);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  }

  async function ensurePermission(handle, mode) {
    const opts = { mode: mode || "readwrite" };
    if ((await handle.queryPermission(opts)) === "granted") return true;
    return (await handle.requestPermission(opts)) === "granted";
  }

  async function writeToHandle() {
    if (!fileHandle) return;
    try {
      const ok = await ensurePermission(fileHandle, "readwrite");
      if (!ok) { setStatus("permission denied", "status-error"); return; }
      const writable = await fileHandle.createWritable();
      await writable.write(emitYaml());
      await writable.close();
      setStatus("auto-saved", "status-saved");
    } catch (err) {
      console.error("Auto-save failed:", err);
      setStatus("auto-save failed — try disconnecting and reconnecting the file", "status-error");
    }
  }

  /* No debounce: writes are ~10ms and skipping setTimeout preserves the
   * user-gesture chain that File System Access API permission re-grants
   * require after a page reload. */
  function scheduleAutoSave() {
    if (!fileHandle) {
      setStatus("unsaved", "status-unsaved");
      return;
    }
    setStatus("saving…", "status-unsaved");
    writeToHandle();
  }

  async function connectFile() {
    try {
      const handle = await window.showSaveFilePicker({
        suggestedName: "comfort-posture.yaml",
        types: [{ description: "YAML", accept: { "text/yaml": [".yaml", ".yml"] } }]
      });
      fileHandle = handle;
      await idbSet("comfort-posture-handle", handle);
      connectBtn.hidden = true;
      connectedRow.hidden = false;
      connectedFilename.textContent = handle.name;
      await writeToHandle();
    } catch (err) {
      if (err && err.name === "AbortError") return; /* user cancelled */
      console.error("Connect failed:", err);
      setStatus("could not connect to file — check browser permissions and try again", "status-error");
    }
  }

  async function disconnectFile() {
    fileHandle = null;
    await idbDel("comfort-posture-handle");
    connectBtn.hidden = false;
    connectedRow.hidden = true;
    setStatus("unsaved", "status-unsaved");
  }

  async function restoreHandle() {
    try {
      const handle = await idbGet("comfort-posture-handle");
      if (!handle) return;
      /* Permission may need re-granting after a page reload. queryPermission
       * returns "prompt" silently; requesting it would block on a click-gesture.
       * Show the connected UI but defer the actual write until the user
       * touches a control (which is a user gesture and allows the prompt). */
      fileHandle = handle;
      connectBtn.hidden = true;
      connectedRow.hidden = false;
      connectedFilename.textContent = handle.name || "comfort-posture.yaml";
      const granted = await handle.queryPermission({ mode: "readwrite" });
      if (granted === "granted") {
        setStatus("auto-saved", "status-saved");
      } else {
        setStatus("touch a control to re-grant access", "status-unsaved");
      }
    } catch (err) {
      console.error("Restore failed:", err);
    }
  }

  if (HAS_FSA) {
    connectBtn.hidden = false;
    connectBtn.addEventListener("click", connectFile);
    disconnectBtn.addEventListener("click", disconnectFile);
    restoreHandle();
  } else {
    noApiHelp.hidden = false;
  }

  /* ── Copy / Download ─────────────────────────────────────────────── */
  document.getElementById("copy-btn").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(emitYaml());
      toast("YAML copied to clipboard");
    } catch (e) {
      /* Fallback: select + manual copy */
      const pre = document.getElementById("yaml-output");
      const range = document.createRange();
      range.selectNodeContents(pre);
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      toast("Select-all + Cmd/Ctrl+C to copy");
    }
  });

  document.getElementById("download-btn").addEventListener("click", () => {
    const blob = new Blob([emitYaml()], { type: "text/yaml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "comfort-posture.yaml";
    a.click();
    URL.revokeObjectURL(url);
    toast("Downloaded comfort-posture.yaml — save it to .ravenclaude/ in your project");
  });

  /* ── Status / toast ──────────────────────────────────────────────── */
  /* `flagUnsaved` is the legacy hook every form-change calls. When auto-save
   * is connected, it kicks off a debounced write; otherwise it just shows
   * the unsaved badge. */
  function flagUnsaved() {
    scheduleAutoSave();
  }
  const toastEl = (() => {
    const el = document.createElement("div");
    el.className = "toast";
    el.setAttribute("role", "status");
    el.setAttribute("aria-live", "polite");
    document.body.appendChild(el);
    return el;
  })();
  let toastTimer = null;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("show"), 2200);
  }

  /* ── Info modal (category detail) ───────────────────────────────── */
  const modal = document.getElementById("info-modal");
  const modalTitle = document.getElementById("info-modal-title");
  const modalDesc = document.getElementById("info-modal-desc");
  const modalControls = document.getElementById("info-modal-controls");
  const modalExamples = document.getElementById("info-modal-examples");
  const modalRecIndividual = document.getElementById("info-modal-rec-individual");
  const modalRecTeam = document.getElementById("info-modal-rec-team");
  const modalGuidance = document.getElementById("info-modal-guidance");
  const modalClose = document.getElementById("info-modal-close");
  let lastFocus = null;

  function openModal(catName) {
    const sch = catProps[catName];
    if (!sch) return;
    modalTitle.textContent = sch.title || catName;
    modalDesc.textContent = sch.description || "";
    modalControls.textContent = sch["x-controls"] || "(no explanation provided)";
    const examples = sch["x-examples"] || [];
    modalExamples.innerHTML = "";
    for (const ex of examples) {
      const li = document.createElement("li");
      li.textContent = ex;
      modalExamples.appendChild(li);
    }
    if (examples.length === 0) {
      const li = document.createElement("li");
      li.textContent = "(no examples provided)";
      li.style.color = "var(--muted)";
      li.style.fontStyle = "italic";
      modalExamples.appendChild(li);
    }
    modalRecIndividual.textContent = sch["x-rec-individual"] || "(no recommendation provided)";
    modalRecTeam.textContent = sch["x-rec-team"] || "(no recommendation provided)";
    modalGuidance.textContent = sch["x-guidance"] || "(no guidance provided)";
    lastFocus = document.activeElement;
    modal.classList.add("open");
    modalClose.focus();
  }
  function closeModal() {
    modal.classList.remove("open");
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
  }

  /* ── Per-pattern info modal ──────────────────────────────────────── */
  const patternModal = document.getElementById("pattern-modal");
  const patternModalTitle = document.getElementById("pattern-modal-title");
  const patternModalWhat = document.getElementById("pattern-modal-what");
  const patternModalWhy = document.getElementById("pattern-modal-why");
  const patternModalClose = document.getElementById("pattern-modal-close");
  let patternLastFocus = null;
  function openPatternModal(pattern) {
    const data = (PATTERN_EXPLANATIONS && PATTERN_EXPLANATIONS[pattern]) || {};
    patternModalTitle.textContent = pattern;
    patternModalWhat.textContent = data.what || "(no explanation provided)";
    patternModalWhy.textContent = data.why || "(no rationale provided)";
    patternLastFocus = document.activeElement;
    patternModal.classList.add("open");
    patternModalClose.focus();
  }
  function closePatternModal() {
    patternModal.classList.remove("open");
    if (patternLastFocus && typeof patternLastFocus.focus === "function") patternLastFocus.focus();
  }
  function openSectionModal(sectionKey) {
    const data = SECTION_EXPLANATIONS[sectionKey] || {};
    patternModalTitle.textContent = data.title || sectionKey;
    patternModalWhat.textContent = data.what || "(no explanation provided)";
    patternModalWhy.textContent = data.why || "(no rationale provided)";
    patternLastFocus = document.activeElement;
    patternModal.classList.add("open");
    patternModalClose.focus();
  }

  /* ── Layers info modal ───────────────────────────────────────────── */
  const layersModal = document.getElementById("layers-modal");
  const layersModalClose = document.getElementById("layers-modal-close");
  let layersLastFocus = null;
  function openLayersModal() {
    layersLastFocus = document.activeElement;
    layersModal.classList.add("open");
    layersModalClose.focus();
  }
  function closeLayersModal() {
    layersModal.classList.remove("open");
    if (layersLastFocus && typeof layersLastFocus.focus === "function") layersLastFocus.focus();
  }
  const layersInfoBtn = document.getElementById("layers-info-btn");
  if (layersInfoBtn) layersInfoBtn.addEventListener("click", e => { e.preventDefault(); e.stopPropagation(); openLayersModal(); });
  layersModalClose.addEventListener("click", closeLayersModal);
  layersModal.addEventListener("click", e => { if (e.target === layersModal) closeLayersModal(); });

  /* Wire all info buttons */
  document.querySelectorAll(".info-btn").forEach(btn => {
    if (btn.id === "layers-info-btn" || btn.id === "layers-modal-close") return;
    btn.addEventListener("click", e => {
      e.preventDefault();
      e.stopPropagation();
      if (btn.dataset.infoPattern) {
        openPatternModal(btn.dataset.infoPattern);
      } else if (btn.dataset.infoSection) {
        openSectionModal(btn.dataset.infoSection);
      } else if (btn.dataset.infoFor) {
        openModal(btn.dataset.infoFor);
      }
    });
  });
  modalClose.addEventListener("click", closeModal);
  modal.addEventListener("click", e => { if (e.target === modal) closeModal(); });
  patternModalClose.addEventListener("click", closePatternModal);
  patternModal.addEventListener("click", e => { if (e.target === patternModal) closePatternModal(); });
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") {
      if (modal.classList.contains("open")) closeModal();
      if (patternModal.classList.contains("open")) closePatternModal();
      if (layersModal.classList.contains("open")) closeLayersModal();
    }
  });

  /* ── Install & Update tab ────────────────────────────────────────── */
  /* Copy-to-clipboard command blocks work on ANY host (GitHub Pages, file://,
   * served). The one-click Install/Update/Status buttons POST to /__run, which
   * only exists when scripts/serve-dashboards.py is serving the page. We detect
   * that with a HEAD /__run probe — exactly mirroring the Settings tab's
   * HEAD /__save probe. */
  document.querySelectorAll(".cmd-copy[data-copy-for]").forEach(btn => {
    btn.addEventListener("click", async () => {
      const code = document.getElementById(btn.dataset.copyFor);
      const text = code ? code.textContent : "";
      try {
        await navigator.clipboard.writeText(text);
        toast("Copied to clipboard");
      } catch (e) {
        // clipboard.writeText can reject (insecure context / permission denied).
        // Only fall back to a manual selection if the source element exists —
        // selectNodeContents(null) would otherwise throw a second time.
        if (code) {
          const range = document.createRange();
          range.selectNodeContents(code);
          const sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(range);
          toast("Select-all + Cmd/Ctrl+C to copy");
        } else {
          toast("Copy failed — select the command manually");
        }
      }
    });
  });

  const RUN_ACTIONS = ["install", "update", "status"];
  const runButtons = Array.from(document.querySelectorAll("button[data-run-action]"));
  const runLiveBadge = document.getElementById("run-live-badge");
  const runOneclickSub = document.getElementById("run-oneclick-sub");
  const runSpinner = document.getElementById("run-spinner");
  const runResult = document.getElementById("run-result");
  const runResultTitle = document.getElementById("run-result-title");
  const runResultBadge = document.getElementById("run-result-badge");
  const runResultOutput = document.getElementById("run-result-output");
  const statusOutput = document.getElementById("status-output");

  async function probeRunEndpoint() {
    try {
      const res = await fetch("/__run", { method: "HEAD" });
      return res.ok;
    } catch (e) {
      return false;
    }
  }

  function setRunBusy(busy) {
    runButtons.forEach(b => { b.disabled = busy; });
    runSpinner.hidden = !busy;
  }

  async function runAction(action) {
    if (!RUN_ACTIONS.includes(action)) return;
    setRunBusy(true);
    runResult.hidden = false;
    runResultTitle.textContent = "Running " + action + "…";
    runResultBadge.textContent = "";
    runResultBadge.className = "run-result-badge";
    runResultOutput.textContent = "";
    try {
      const res = await fetch("/__run", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...(await csrfHeaders()) },
        body: JSON.stringify({ action: action })
      });
      if (!res.ok) {
        runResultTitle.textContent = action + " failed";
        runResultBadge.textContent = "HTTP " + res.status;
        runResultBadge.classList.add("badge-fail");
        runResultOutput.textContent = (await res.text().catch(() => "")) || "(no output)";
        return;
      }
      const j = await res.json();
      runResultTitle.textContent = (j.action || action) + " — exit " + j.exit_code;
      if (j.ok) {
        runResultBadge.textContent = "ok";
        runResultBadge.classList.add("badge-ok");
      } else {
        runResultBadge.textContent = "failed";
        runResultBadge.classList.add("badge-fail");
      }
      runResultOutput.textContent = j.output || "(no output)";
      if (action === "status") {
        statusOutput.textContent = j.output || "(no output)";
      }
      toast(action + (j.ok ? " ok" : " failed"));
    } catch (err) {
      runResultTitle.textContent = action + " failed";
      runResultBadge.textContent = "error";
      runResultBadge.classList.add("badge-fail");
      runResultOutput.textContent = String(err);
      console.error("/__run failed:", err);
    } finally {
      setRunBusy(false);
    }
  }

  runButtons.forEach(b => {
    b.addEventListener("click", () => runAction(b.dataset.runAction));
  });

  probeRunEndpoint().then(available => {
    if (available) {
      runButtons.forEach(b => { b.disabled = false; });
      runLiveBadge.hidden = false;
      runOneclickSub.innerHTML =
        "One-click run is live &mdash; the local server is serving this page.";
    } else {
      runButtons.forEach(b => { b.disabled = true; });
      runLiveBadge.hidden = true;
    }
  });

  /* ── Overview served/static banner ───────────────────────────────────
   * Build-time the banner renders in its "Preview" (static) state. When the
   * page is served by serve-dashboards.py, HEAD /__save succeeds (the Settings
   * tab uses the same probe) and we flip the banner to "Live". Static hosts
   * (GitHub Pages / file://) keep the read-only Preview message. */
  (function wireOverviewBanner() {
    const banner = document.getElementById("ov-mode-banner");
    if (!banner) return;
    fetch("/__save", { method: "HEAD" }).then(res => {
      if (res && res.ok) {
        banner.classList.remove("ov-banner-static");
        banner.classList.add("ov-banner-live");
        banner.innerHTML =
          "<strong>Live</strong> &mdash; this dashboard is served locally; "
          + "changes you save are written to <em>this</em> repo.";
      }
    }).catch(() => { /* static host — keep the Preview message */ });
  })();

  /* ── Command Run buttons (Class A) — honest disabled copy ─────────────
   * Class-A command Run buttons reuse the exact /__run mechanic + button
   * wiring as the Install tab (they share the button[data-run-action]
   * selector, so they auto-enable on the same HEAD /__run probe). The only
   * addition: an honest disabled-state note. A consumer running `rc dashboard`
   * is running the BUNDLED server, which has no /__run — so the correct copy
   * is "root dev server only", never "run serve-dashboards.py". */
  (function wireCommandRunNote() {
    const runCmds = Array.from(document.querySelectorAll(".cmd-run[data-run-action]"));
    if (!runCmds.length) return;
    fetch("/__run", { method: "HEAD" }).then(res => {
      const served = res && res.ok;
      runCmds.forEach(b => {
        if (!served) {
          b.disabled = true;
          b.title = "Run is available only when served by the root dev server";
        }
      });
    }).catch(() => {
      runCmds.forEach(b => {
        b.disabled = true;
        b.title = "Run is available only when served by the root dev server";
      });
    });
  })();

  /* ── Guidance — best-practice preview-on-click ────────────────────────
   * Build-time-embedded previews (no fetch — static-host safe). Each toggle
   * shows/hides the rationale paragraph for one best-practice. */
  document.querySelectorAll(".guide-bp-toggle[data-bp-toggle]").forEach(btn => {
    btn.addEventListener("click", () => {
      const el = document.getElementById(btn.dataset.bpToggle);
      if (!el) return;
      const open = el.hidden;
      el.hidden = !open;
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.textContent = open ? "hide" : "preview";
    });
  });

  /* ── Test-a-command simulator tab ────────────────────────────────── */
  /* Answers "what would the Thing do?" using the REAL engine via POST
   * /__classify (served mode only). Classification is NEVER reimplemented in
   * JS — we always call the endpoint. Availability is probed with HEAD
   * /__classify, mirroring the Settings/Install HEAD probes. On a static host
   * the button is disabled with a help line; fetch errors fail soft. */
  const simCommand = document.getElementById("sim-command");
  const simAnalyzeBtn = document.getElementById("sim-analyze-btn");
  const simDisabledHelp = document.getElementById("sim-disabled-help");
  const simResult = document.getElementById("sim-result");
  const simDenyBanner = document.getElementById("sim-deny-banner");
  const simDenyReason = document.getElementById("sim-deny-reason");
  const simCategory = document.getElementById("sim-category");
  const simTierBadge = document.getElementById("sim-tier-badge");
  const simSeats = document.getElementById("sim-seats");
  const simConcernsBlock = document.getElementById("sim-concerns-block");
  const simConcerns = document.getElementById("sim-concerns");
  const simGateText = document.getElementById("sim-gate-text");

  const SIM_TIERS = ["low", "medium", "high", "extreme"];
  const SIM_SEAT_LABELS = {
    forseti: "Forseti — Security",
    mimir: "Mímir — Correctness",
    heimdall: "Heimdall — Injection watch",
    thor: "Thor — Tie-breaker",
  };

  async function probeClassifyEndpoint() {
    try {
      const res = await fetch("/__classify", { method: "HEAD" });
      return res.ok;
    } catch (e) {
      return false;
    }
  }

  function renderDecision(d) {
    if (simAnalyzeBtn) simAnalyzeBtn.disabled = false;
    simResult.hidden = false;

    /* Pre-LLM / self-disable deny banner. */
    const denied = d.pre_llm_deny === true || d.self_disable_deny === true;
    if (denied) {
      const reason = d.deny_concern ? (" — " + d.deny_concern) : "";
      simDenyReason.textContent = reason;
      simDenyBanner.hidden = false;
    } else {
      simDenyBanner.hidden = true;
    }

    /* Category. */
    if (d.category == null || d.category === "") {
      simCategory.textContent = "(uncategorized — no review)";
      simCategory.classList.add("sim-no-category");
    } else {
      simCategory.textContent = d.category;
      simCategory.classList.remove("sim-no-category");
    }

    /* Tier badge, color-scaled low → extreme. */
    const tier = SIM_TIERS.includes(d.tier) ? d.tier : null;
    simTierBadge.textContent = tier || "—";
    simTierBadge.className = "sim-tier-badge" + (tier ? " tier-" + tier : "");

    /* Convened seats (or "no panel — clean read"). */
    simSeats.innerHTML = "";
    const seats = Array.isArray(d.convened_seats) ? d.convened_seats : [];
    if (seats.length === 0 || d.panel_required === false) {
      const span = document.createElement("span");
      span.className = "sim-no-panel";
      span.textContent = d.is_read === true
        ? "no panel — clean read"
        : "no panel convened";
      simSeats.appendChild(span);
    } else {
      for (const seat of seats) {
        const pill = document.createElement("span");
        pill.className = "sim-seat-pill";
        pill.textContent = SIM_SEAT_LABELS[seat] || seat;
        simSeats.appendChild(pill);
      }
    }

    /* Concerns cited (ids). */
    simConcerns.innerHTML = "";
    const concerns = Array.isArray(d.concerns) ? d.concerns : [];
    if (concerns.length) {
      for (const c of concerns) {
        const pill = document.createElement("span");
        pill.className = "sim-concern-pill";
        pill.textContent = String(c);
        simConcerns.appendChild(pill);
      }
      simConcernsBlock.hidden = false;
    } else {
      simConcernsBlock.hidden = true;
    }

    /* Predicted gate — the headline sentence. */
    simGateText.textContent = d.predicted_gate || "(no prediction returned)";
  }

  async function analyzeCommand() {
    const command = (simCommand && simCommand.value || "").trim();
    if (!command) return;
    simAnalyzeBtn.disabled = true;
    simGateText.textContent = "Analyzing…";
    try {
      const res = await fetch("/__classify", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...(await csrfHeaders()) },
        body: JSON.stringify({ command: command })
      });
      if (!res.ok) {
        simResult.hidden = false;
        simDenyBanner.hidden = true;
        simGateText.textContent = "Engine error: HTTP " + res.status;
        simAnalyzeBtn.disabled = false;
        return;
      }
      const d = await res.json();
      renderDecision(d);
    } catch (err) {
      simResult.hidden = false;
      simDenyBanner.hidden = true;
      simGateText.textContent = "Could not reach the engine. Make sure the local dashboard server is running (ravenclaude dashboard --project <repo>) and the forwarded URL is open.";
      console.error("/__classify failed:", err);
      simAnalyzeBtn.disabled = false;
    }
  }

  if (simAnalyzeBtn) {
    simAnalyzeBtn.addEventListener("click", analyzeCommand);
  }
  if (simCommand) {
    simCommand.addEventListener("keydown", e => {
      if (e.key === "Enter") { e.preventDefault(); analyzeCommand(); }
    });
  }

  probeClassifyEndpoint().then(available => {
    if (available) {
      if (simAnalyzeBtn) simAnalyzeBtn.disabled = false;
      if (simDisabledHelp) simDisabledHelp.hidden = true;
    } else {
      if (simAnalyzeBtn) simAnalyzeBtn.disabled = true;
      if (simCommand) simCommand.disabled = true;
      if (simDisabledHelp) simDisabledHelp.hidden = false;
    }
  });

  /* ── Tab routing ─────────────────────────────────────────────────── */
  // Derived from the DOM so new pages (e.g. the per-plugin Plugins category)
  // route automatically without re-listing them here.
  const validTabs = Array.from(document.querySelectorAll(".tab-btn")).map(b => b.dataset.tab);
  function openConcept(id) {
    const card = document.getElementById("learn-" + id);
    if (!card) return;
    let el = card.parentElement;
    while (el) {
      if (el.tagName === "DETAILS") el.open = true;
      el = el.parentElement;
    }
    card.scrollIntoView({ block: "start", behavior: "smooth" });
    card.classList.remove("rc-flash");
    void card.offsetWidth; /* restart the animation */
    card.classList.add("rc-flash");
  }
  /* ── Review log (saga) tab state ─────────────────────────────────────
   * Declared BEFORE applyHash() is called below. A deep-link / reload on
   * #/saga makes the initial applyHash() call reach loadSaga(), which reads
   * this state; if it were still in the temporal dead zone the saga tab
   * would throw ("Cannot access 'sagaLoaded' before initialization") and
   * never render. */
  let sagaLoaded = false;
  let sagaRecords = [];

  const sagaContent  = document.getElementById("saga-content");
  const sagaCount    = document.getElementById("saga-count");
  const sagaVerdFil  = document.getElementById("saga-verdict-filter");
  const sagaCatFil   = document.getElementById("saga-cat-filter");
  const sagaRefBtn   = document.getElementById("saga-refresh-btn");

  /* ── Activity tab state ──────────────────────────────────────────────
   * Declared above applyHash() for the same TDZ reason as the saga state:
   * a #/activity deep-link makes the initial applyHash() reach loadActivity(),
   * which reads activityLoaded. */
  let activityLoaded = false;
  let heimdallLoaded = false;
  let vidarrLoaded = false;
  let nornsLoaded = false;
  let mimirLoaded = false;
  let vidarrEvents = [];
  let vidarrKindFilter = "all";
  let activityRecords = [];
  const activityContent = document.getElementById("activity-content");
  const activityCount   = document.getElementById("activity-count");
  const activityRefBtn  = document.getElementById("activity-refresh-btn");

  /* Heimdall element handles + repo coordinates for the client-side CI fetch. */
  const REPO_OWNER = "mcorbett51090";
  const REPO_NAME  = "RavenClaude";

  // Two-tier nav: derive each page's category from the DOM (data-cat on the tab
  // buttons) and remember the first page of each category (for category clicks).
  const pageCat = {};
  const catFirst = {};
  document.querySelectorAll('.tab-bar .tab-btn[data-cat]').forEach(b => {
    pageCat[b.dataset.tab] = b.dataset.cat;
    if (!(b.dataset.cat in catFirst)) catFirst[b.dataset.cat] = b.dataset.tab;
  });
  function setCategory(cat) {
    document.querySelectorAll('.cat-btn').forEach(c => {
      c.setAttribute('aria-pressed', c.dataset.cat === cat ? 'true' : 'false');
    });
    // Only the active category's page tabs are shown (CSS hides :not(.in-cat)).
    document.querySelectorAll('.tab-bar .tab-btn').forEach(b => {
      b.classList.toggle('in-cat', b.dataset.cat === cat);
    });
  }

  // Core activation — switch the visible page. Runs SYNCHRONOUSLY on click so
  // navigation never depends on the hashchange event firing (which a sandboxed
  // preview / some webviews suppress). `sub` carries a deep-link sub-segment
  // (e.g. #/learn/<concept>).
  function activate(tab, sub) {
    if (!validTabs.includes(tab)) tab = "overview";
    setCategory(pageCat[tab] || "setup");
    document.querySelectorAll(".tab-btn").forEach(b => {
      const sel = b.dataset.tab === tab;
      b.setAttribute("aria-selected", sel ? "true" : "false");
      // Roving tabindex (WAI-ARIA tabs pattern): only the selected tab is in the
      // Tab order; arrow keys move between the rest within the active category.
      b.setAttribute("tabindex", sel ? "0" : "-1");
    });
    document.querySelectorAll(".tab-panel").forEach(p => {
      p.classList.toggle("active", p.dataset.tab === tab);
    });
    if (tab === "learn" && sub) openConcept(sub);
    if (tab === "saga" && !sagaLoaded) loadSaga();
    if (tab === "activity" && !activityLoaded) loadActivity();
    if (tab === "heimdall" && !heimdallLoaded) loadHeimdall();
    if (tab === "vidarr" && !vidarrLoaded) loadVidarr();
    if (tab === "norns" && !nornsLoaded) loadNorns();
    if (tab === "mimir" && !mimirLoaded) loadMimir();
    if (tab === "pipeline") syncPipelineTab();
    if (tab.indexOf("plugin-") === 0) hydratePluginPage(tab.slice(7));
    if (tab === "web-access") hydrateWebAccess();
  }
  // Navigate: activate immediately, then reflect the page in the URL hash for
  // deep-linking + browser back/forward. (The hashchange listener re-applies on
  // back/forward; the redundant re-activate is idempotent.)
  function goTo(tab) {
    activate(tab);
    if (location.hash !== "#/" + tab) location.hash = "/" + tab;
  }
  function applyHash() {
    const seg = (location.hash || "#/overview").replace(/^#\//, "").split("/");
    activate(seg[0], seg[1]);
  }
  document.querySelectorAll(".tab-btn").forEach(b => {
    b.addEventListener("click", () => goTo(b.dataset.tab));
  });
  // Clicking a category reveals its pages and jumps to the first page in it.
  document.querySelectorAll(".cat-btn").forEach(c => {
    c.addEventListener("click", () => {
      const cat = c.dataset.cat;
      setCategory(cat);
      const first = catFirst[cat];
      if (first) goTo(first);
    });
  });
  // Header "What is this?" link → About, without depending on hashchange.
  const aboutLink = document.querySelector(".header-about-link");
  if (aboutLink) aboutLink.addEventListener("click", e => { e.preventDefault(); goTo("about"); });
  // Keyboard navigation for the tablist (WAI-ARIA Authoring Practices "Tabs"):
  // Left/Right/Home/End move between the VISIBLE (active-category) tabs only.
  const tablist = document.querySelector('.tab-bar[role="tablist"]');
  if (tablist) {
    tablist.addEventListener("keydown", e => {
      const keys = ["ArrowLeft", "ArrowRight", "Home", "End"];
      if (!keys.includes(e.key)) return;
      const tabs = Array.from(tablist.querySelectorAll('.tab-btn[role="tab"]'))
        .filter(t => t.classList.contains("in-cat"));
      if (!tabs.length) return;
      const cur = tabs.findIndex(t => t.getAttribute("aria-selected") === "true");
      let next = cur < 0 ? 0 : cur;
      if (e.key === "ArrowRight") next = (cur + 1) % tabs.length;
      else if (e.key === "ArrowLeft") next = (cur - 1 + tabs.length) % tabs.length;
      else if (e.key === "Home") next = 0;
      else if (e.key === "End") next = tabs.length - 1;
      e.preventDefault();
      const target = tabs[next];
      goTo(target.dataset.tab);
      target.focus();
    });
  }
  /* ── Plugins category: per-plugin variable editor (portal → repo file) ─── */
  const PLUGIN_LS_PREFIX = "rc-plugin-vars:";
  const pluginPagesHydrated = {};
  function pluginPanel(plugin) {
    return document.querySelector('.plugin-page[data-plugin="' + plugin + '"]');
  }
  function pluginYamlQuote(v) {
    v = String(v);
    if (v === "") return '""';
    if (/^[A-Za-z0-9_.\/$%-]+$/.test(v) && !/^(true|false|null|yes|no|on|off)$/i.test(v)) return v;
    return '"' + v.replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"';
  }
  function emitPluginYaml(plugin) {
    const panel = pluginPanel(plugin);
    if (!panel) return "";
    const lines = ["# " + plugin + " — variables managed by the RavenClaude dashboard Plugins tab"];
    panel.querySelectorAll(".pv-control[data-pvar]").forEach(c => {
      const key = c.dataset.pvar;
      const val = c.value;
      if (c.dataset.ptype === "number") {
        lines.push(key + ": " + (val === "" ? '""' : val));
      } else {
        lines.push(key + ": " + pluginYamlQuote(val));
      }
    });
    const extra = panel.querySelector(".pv-extra");
    if (extra && extra.value.trim()) {
      lines.push("# free-form");
      extra.value.split(/\r?\n/).forEach(l => { if (l.trim()) lines.push(l.replace(/\s+$/, "")); });
    }
    return lines.join("\n") + "\n";
  }
  function applyPluginConfig(plugin, text) {
    const panel = pluginPanel(plugin);
    if (!panel || !text) return;
    const curatedKeys = new Set(
      Array.from(panel.querySelectorAll(".pv-control[data-pvar]")).map(c => c.dataset.pvar)
    );
    const extraLines = [];
    text.split(/\r?\n/).forEach(line => {
      const s = line.trim();
      if (!s || s[0] === "#") return;
      const i = s.indexOf(":");
      if (i < 0) return;
      const key = s.slice(0, i).trim();
      let val = s.slice(i + 1).trim();
      if ((val[0] === '"' && val.slice(-1) === '"') || (val[0] === "'" && val.slice(-1) === "'")) {
        val = val.slice(1, -1);
      }
      if (curatedKeys.has(key)) {
        const c = panel.querySelector('.pv-control[data-pvar="' + key + '"]');
        if (c) c.value = val;
      } else {
        extraLines.push(line.replace(/\s+$/, ""));
      }
    });
    const extra = panel.querySelector(".pv-extra");
    if (extra) extra.value = extraLines.join("\n");
  }
  async function hydratePluginPage(plugin) {
    if (pluginPagesHydrated[plugin]) return;
    pluginPagesHydrated[plugin] = true;
    const panel = pluginPanel(plugin);
    if (!panel) return;
    const target = panel.dataset.target;
    try {
      const res = await fetch("/__read?path=" + encodeURIComponent(target));
      if (res.ok) {
        const j = await res.json();
        if (j && typeof j.content === "string" && j.content.trim()) {
          applyPluginConfig(plugin, j.content);
          return;
        }
      }
    } catch (e) { /* static host — fall through to localStorage */ }
    const ls = localStorage.getItem(PLUGIN_LS_PREFIX + plugin);
    if (ls) applyPluginConfig(plugin, ls);
  }
  function setPluginStatus(plugin, msg, cls) {
    const el = document.querySelector('.pp-status[data-plugin="' + plugin + '"]');
    if (!el) return;
    el.textContent = msg;
    el.className = "pp-status " + (cls || "");
  }
  document.querySelectorAll(".pp-save").forEach(btn => {
    btn.addEventListener("click", async () => {
      const plugin = btn.dataset.plugin;
      const panel = pluginPanel(plugin);
      const target = panel.dataset.target;
      const yaml = emitPluginYaml(plugin);
      localStorage.setItem(PLUGIN_LS_PREFIX + plugin, yaml);
      setPluginStatus(plugin, "saving…", "status-unsaved");
      try {
        const res = await fetch("/__save", {
          method: "POST",
          headers: { "Content-Type": "application/json", ...(await csrfHeaders()) },
          body: JSON.stringify({ path: target, content: yaml })
        });
        if (res.status === 404 || res.status === 405) {
          setPluginStatus(plugin, "saved in browser (no server)", "status-unsaved");
          const ns = document.querySelector('.pp-noserver[data-plugin="' + plugin + '"]');
          if (ns) ns.hidden = false;
          return;
        }
        if (!res.ok) { setPluginStatus(plugin, "save failed (" + res.status + ")", "status-error"); return; }
        setPluginStatus(plugin, "saved to " + target, "status-ok");
      } catch (e) {
        setPluginStatus(plugin, "saved in browser (no server)", "status-unsaved");
        const ns = document.querySelector('.pp-noserver[data-plugin="' + plugin + '"]');
        if (ns) ns.hidden = false;
      }
    });
  });
  document.querySelectorAll(".pp-download").forEach(btn => {
    btn.addEventListener("click", () => {
      const plugin = btn.dataset.plugin;
      const yaml = emitPluginYaml(plugin);
      const blob = new Blob([yaml], { type: "text/yaml" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = plugin + ".yaml";
      document.body.appendChild(a); a.click(); a.remove();
      URL.revokeObjectURL(url);
      setPluginStatus(plugin, "downloaded " + plugin + ".yaml", "status-ok");
    });
  });

  /* ── Web access allow/deny editor (portal → .ravenclaude/web-access.yaml) ── */
  let webAccessHydrated = false;
  function waPanel() { return document.querySelector(".web-access-page"); }
  function waLines(sel) {
    const p = waPanel();
    const t = p && p.querySelector(sel);
    if (!t) return [];
    return t.value.split(/\r?\n/).map(s => s.trim().toLowerCase()).filter(Boolean);
  }
  function emitWebAccessYaml() {
    const mk = (key, items) => items.length
      ? key + ":\n" + items.map(d => "  - " + d).join("\n") + "\n"
      : key + ": []\n";
    return "# Website access allow/deny lists — managed by the RavenClaude dashboard\n"
      + mk("allow", waLines(".wa-allow")) + mk("deny", waLines(".wa-deny"));
  }
  function applyWebAccess(text) {
    const panel = waPanel();
    if (!panel || !text) return;
    const allow = [], deny = [];
    let sec = null;
    text.split(/\r?\n/).forEach(line => {
      const m = line.match(/^([A-Za-z_]+):/);
      if (m) { sec = m[1].toLowerCase(); return; }
      const it = line.match(/^\s*-\s*(.+?)\s*$/);
      if (!it) return;
      const v = it[1].replace(/["']/g, "").trim();
      if (sec === "allow") allow.push(v);
      else if (sec === "deny") deny.push(v);
    });
    const a = panel.querySelector(".wa-allow"), d = panel.querySelector(".wa-deny");
    if (a) a.value = allow.join("\n");
    if (d) d.value = deny.join("\n");
  }
  async function hydrateWebAccess() {
    if (webAccessHydrated) return;
    webAccessHydrated = true;
    const panel = waPanel();
    if (!panel) return;
    try {
      const res = await fetch("/__read?path=" + encodeURIComponent(panel.dataset.target));
      if (res.ok) {
        const j = await res.json();
        if (j && typeof j.content === "string" && j.content.trim()) { applyWebAccess(j.content); return; }
      }
    } catch (e) { /* static host */ }
    const ls = localStorage.getItem("rc-web-access");
    if (ls) applyWebAccess(ls);
  }
  function waStatus(msg, cls) {
    const p = waPanel();
    const el = p && p.querySelector(".wa-status");
    if (el) { el.textContent = msg; el.className = "wa-status pp-status " + (cls || ""); }
  }
  (function wireWebAccess() {
    const panel = waPanel();
    if (!panel) return;
    const saveBtn = panel.querySelector(".wa-save");
    const dlBtn = panel.querySelector(".wa-download");
    if (saveBtn) saveBtn.addEventListener("click", async () => {
      const yaml = emitWebAccessYaml();
      localStorage.setItem("rc-web-access", yaml);
      waStatus("saving…", "status-unsaved");
      try {
        const res = await fetch("/__save", {
          method: "POST",
          headers: { "Content-Type": "application/json", ...(await csrfHeaders()) },
          body: JSON.stringify({ path: panel.dataset.target, content: yaml })
        });
        if (res.status === 404 || res.status === 405) {
          waStatus("saved in browser (no server)", "status-unsaved");
          const ns = panel.querySelector(".wa-noserver"); if (ns) ns.hidden = false;
          return;
        }
        if (!res.ok) { waStatus("save failed (" + res.status + ")", "status-error"); return; }
        waStatus("saved to " + panel.dataset.target, "status-ok");
      } catch (e) {
        waStatus("saved in browser (no server)", "status-unsaved");
        const ns = panel.querySelector(".wa-noserver"); if (ns) ns.hidden = false;
      }
    });
    if (dlBtn) dlBtn.addEventListener("click", () => {
      const yaml = emitWebAccessYaml();
      const blob = new Blob([yaml], { type: "text/yaml" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = "web-access.yaml";
      document.body.appendChild(a); a.click(); a.remove();
      URL.revokeObjectURL(url);
      waStatus("downloaded web-access.yaml", "status-ok");
    });
  })();

  window.addEventListener("hashchange", applyHash);
  applyHash();

  /* ── Pipeline tab ──────────────────────────────────────────────────────
   * Visual guardrail map. Posture-backed knobs mutate the SHARED `state` and
   * save through the same emitYaml()/saveToRepo() path as Settings (so the
   * serializer is the single source of truth). The two file-backed editors
   * round-trip .repo-layout.json / .ravenclaude/task-scope.json via /__read +
   * /__save (server-validated). Read-only on a static host. */
  let pipelineServerAvailable = false;
  let pipelineWired = false;

  function pipeBadge(id, text, cls) {
    const el = document.querySelector('[data-pipe-badge="' + id + '"]');
    if (!el) return;
    el.textContent = text;
    el.classList.remove("pipe-badge-on", "pipe-badge-off", "pipe-badge-advisory", "pipe-badge-dynamic");
    el.classList.add(cls);
  }

  function syncPipelineTab() {
    const cr = state.command_review;
    const en = document.getElementById("pipe-thing-enabled");
    if (en) en.checked = cr.enabled !== false;
    const dx = document.getElementById("pipe-dev-exempt");
    if (dx) dx.checked = cr.dev_repo_exempt === true;
    const gf = document.getElementById("pipe-gate-floor");
    if (gf) gf.value = cr.gate_floor;
    pipeBadge("thing", cr.enabled === false ? "Paused" : "On",
              cr.enabled === false ? "pipe-badge-off" : "pipe-badge-on");
    const ro = document.getElementById("pipe-runaway-off");
    if (ro) ro.checked = state.runaway.off === true;
    const rt = document.getElementById("pipe-runaway-total");
    if (rt) rt.value = state.runaway.max_total;
    const rc = document.getElementById("pipe-runaway-consec");
    if (rc) rc.value = state.runaway.max_consecutive;
    pipeBadge("runaway-brake", state.runaway.off ? "Off" : ("On · " + state.runaway.max_total + " steps"),
              state.runaway.off ? "pipe-badge-off" : "pipe-badge-on");
    const dr = document.getElementById("pipe-decision-review");
    if (dr) dr.value = state.decision_review;
    pipeBadge("route-decision-review", state.decision_review,
              state.decision_review === "off" ? "pipe-badge-off" : "pipe-badge-on");
    const dc = document.getElementById("pipe-dod-cmd");
    if (dc) dc.value = state.definition_of_done.cmd || "";
    const dm = document.getElementById("pipe-dod-maxblocks");
    if (dm) dm.value = state.definition_of_done.max_blocks;
    const dodOn = !!(state.definition_of_done.cmd && state.definition_of_done.cmd.trim());
    pipeBadge("dod-gate", dodOn ? "On" : "Off", dodOn ? "pipe-badge-on" : "pipe-badge-off");
    pipeBadge("enforce-layout", pipelineServerAvailable ? "Editable" : "Read-only",
              pipelineServerAvailable ? "pipe-badge-on" : "pipe-badge-advisory");
  }

  function cssEsc(s) { return (window.CSS && CSS.escape) ? CSS.escape(s) : s.replace(/"/g, '\\\\"'); }
  function pipeFileArea(target) {
    return document.querySelector('.pipe-file-text[data-target="' + cssEsc(target) + '"]');
  }
  function pipeFileStatus(target, msg) {
    const el = document.querySelector('.pipe-file-status[data-target="' + cssEsc(target) + '"]');
    if (el) el.textContent = msg;
  }

  async function pipeFileLoad(target) {
    pipeFileStatus(target, "loading…");
    try {
      const res = await fetch("/__read?path=" + encodeURIComponent(target));
      if (res.status === 404) {
        const a = pipeFileArea(target); if (a) a.value = "";
        pipeFileStatus(target, "no file yet — type JSON and Save to create it");
        return;
      }
      if (!res.ok) { pipeFileStatus(target, "could not load (no server?)"); return; }
      const j = await res.json();
      const a = pipeFileArea(target);
      if (a) a.value = j.content || "";
      pipeFileStatus(target, "loaded");
    } catch (e) { pipeFileStatus(target, "could not load (no server?)"); }
  }

  async function pipeFileSave(target) {
    const a = pipeFileArea(target);
    if (!a) return;
    try { JSON.parse(a.value); }
    catch (e) { pipeFileStatus(target, "not valid JSON — fix and try again"); return; }
    pipeFileStatus(target, "saving…");
    try {
      const res = await fetch("/__save", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...(await csrfHeaders()) },
        body: JSON.stringify({ path: target, content: a.value }),
      });
      if (res.status === 404 || res.status === 405) { pipeFileStatus(target, "no server — cannot save from this page"); return; }
      if (!res.ok) { const t = await res.text().catch(() => ""); pipeFileStatus(target, "rejected: " + (t || res.status)); return; }
      pipeFileStatus(target, "saved");
    } catch (e) { pipeFileStatus(target, "save failed (no server?)"); }
  }

  function wirePipelineControls() {
    if (pipelineWired) return;
    pipelineWired = true;
    function onChange(id, fn) {
      const el = document.getElementById(id);
      if (el) el.addEventListener("change", () => { fn(el); render(); syncPipelineTab(); });
    }
    function onInput(id, fn) {
      const el = document.getElementById(id);
      if (el) el.addEventListener("input", () => { fn(el); render(); });
    }
    onChange("pipe-thing-enabled", el => { state.command_review.enabled = el.checked ? true : false; syncMasterEnable(); });
    onChange("pipe-dev-exempt", el => { state.command_review.dev_repo_exempt = el.checked; });
    onChange("pipe-gate-floor", el => { if (GATE_FLOORS.includes(el.value)) state.command_review.gate_floor = el.value; });
    onChange("pipe-runaway-off", el => { state.runaway.off = el.checked; });
    onInput("pipe-runaway-total", el => { const v = parseInt(el.value, 10); if (Number.isFinite(v) && v > 0) state.runaway.max_total = v; });
    onInput("pipe-runaway-consec", el => { const v = parseInt(el.value, 10); if (Number.isFinite(v) && v > 0) state.runaway.max_consecutive = v; });
    onChange("pipe-decision-review", el => { if (DECISION_REVIEW_VALUES.includes(el.value)) state.decision_review = el.value; });
    onInput("pipe-dod-cmd", el => { state.definition_of_done.cmd = el.value; });
    onInput("pipe-dod-maxblocks", el => { const v = parseInt(el.value, 10); if (Number.isFinite(v) && v > 0) state.definition_of_done.max_blocks = v; });

    const saveBtn = document.getElementById("pipeline-save-btn");
    if (saveBtn) saveBtn.addEventListener("click", () => {
      const st = document.getElementById("pipeline-save-status");
      if (st) st.textContent = "saving…";
      saveToRepo().then(() => { if (st) st.textContent = "saved"; }).catch(() => { if (st) st.textContent = "save failed"; });
    });
    document.querySelectorAll(".pipe-file-load").forEach(b => b.addEventListener("click", () => pipeFileLoad(b.dataset.target)));
    document.querySelectorAll(".pipe-file-save").forEach(b => b.addEventListener("click", () => pipeFileSave(b.dataset.target)));
  }

  async function initPipelineTab() {
    wirePipelineControls();
    pipelineServerAvailable = await probeRepoEndpoint();
    const note = document.getElementById("pipeline-server-note");
    if (note) note.hidden = pipelineServerAvailable;
    document.querySelectorAll(".pipe-file-text, .pipe-file-save, .pipe-file-load").forEach(el => { el.disabled = !pipelineServerAvailable; });
    const sb = document.getElementById("pipeline-save-btn");
    if (sb) sb.disabled = !pipelineServerAvailable;
    syncPipelineTab();
    loadConcernStats();
  }
  initPipelineTab();

  /* ── Concern reliability card (Pipeline tab) ──────────────────────────────
   * Reads /__concern-stats (served only) and renders a per-concern FP-signal
   * table. Static hosts surface an honest empty state — never silently empty. */
  function renderConcernStats(payload) {
    const state = document.getElementById("concern-stats-state");
    const tbl = document.getElementById("concern-stats-table");
    const tb  = document.getElementById("concern-stats-tbody");
    if (!state || !tbl || !tb) return;
    const reviews = (payload && payload.total_reviews) || 0;
    const rows = (payload && payload.concerns) || [];
    if (!rows.length) {
      tbl.hidden = true;
      state.textContent = reviews
        ? "No concerns have been cited yet in " + reviews + " reviews."
        : "No command-review data yet — the tribunal has not run in this project.";
      return;
    }
    // Pure DOM construction — no innerHTML. textContent on every leaf node so
    // a hostile/buggy server payload can never inject markup.
    while (tb.firstChild) tb.removeChild(tb.firstChild);
    const numCell = v => {
      const td = document.createElement("td");
      td.className = "num";
      const n = Number(v);
      td.textContent = Number.isFinite(n) ? String(n) : "—";
      return td;
    };
    rows.forEach(r => {
      const ratio = Number(r && r.fp_ratio);
      const tr = document.createElement("tr");
      tr.className = (Number.isFinite(ratio) && ratio >= 0.5) ? "concern-row-hot" : "concern-row-cold";
      // Concern id cell — text only, wrapped in <code> for monospace.
      const tdId = document.createElement("td");
      const code = document.createElement("code");
      code.textContent = String((r && r.id) || "");
      tdId.appendChild(code);
      tr.appendChild(tdId);
      tr.appendChild(numCell(r && r.cited_total));
      tr.appendChild(numCell(r && r.stripped));
      tr.appendChild(numCell(r && r.heimdall_disagreed));
      tr.appendChild(numCell(r && r.final_deny));
      const tdRatio = document.createElement("td");
      tdRatio.className = "num";
      tdRatio.textContent = Number.isFinite(ratio) ? (ratio * 100).toFixed(0) + "%" : "—";
      tr.appendChild(tdRatio);
      tb.appendChild(tr);
    });
    state.textContent = rows.length + " concerns over " + reviews + " reviews";
    tbl.hidden = false;
  }
  window.__renderConcernStats = renderConcernStats;

  async function loadConcernStats() {
    const state = document.getElementById("concern-stats-state");
    try {
      const res = await fetch("/__concern-stats", { credentials: "same-origin" });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      renderConcernStats(data);
    } catch (e) {
      if (state) state.textContent = "No server behind this page — open via the dashboard server to see live concern stats.";
      const tbl = document.getElementById("concern-stats-table");
      if (tbl) tbl.hidden = true;
    }
  }

  /* ── Review log (saga) tab ──────────────────────────────────────── */
  /* State + element refs are declared above applyHash() (see the TDZ note). */

  /* Safe HTML-escape for every untrusted string before it touches innerHTML.
   * All user/tool data from /__saga must pass through esc() before injection.
   * Fixed-structure HTML (class names, element tags) is always hardcoded. */
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function sagaVerdictClass(v) {
    if (v === "allow") return "saga-verdict-allow";
    if (v === "ask")   return "saga-verdict-ask";
    if (v === "deny")  return "saga-verdict-deny";
    if (v === "edit")  return "saga-verdict-edit";
    return "";
  }

  function sagaSeatClass(verdict) {
    const v = (verdict || "").toLowerCase();
    if (v === "allow") return "saga-seat-allow";
    if (v === "deny")  return "saga-seat-deny";
    if (v === "ask")   return "saga-seat-ask";
    return "";
  }

  /* sagaTierClass — maps a risk tier string to the matching CSS modifier class. */
  function sagaTierClass(tier) {
    const t = (tier || "").toLowerCase();
    if (t === "low")     return "saga-tier-badge-low";
    if (t === "medium")  return "saga-tier-badge-medium";
    if (t === "high")    return "saga-tier-badge-high";
    if (t === "extreme") return "saga-tier-badge-extreme";
    return "";
  }

  /* reasonPlain — produces a plain-language (5th-grade) one-liner that explains
   * the outcome of a review entry. Keyed on phase + final_verdict + concerns.
   * Never surfaced via innerHTML; used as textContent only via the esc() path. */
  function reasonPlain(r) {
    const v = (r.final_verdict || "").toLowerCase();
    const phase = (r.phase || "").toLowerCase();
    const concerns = Array.isArray(r.concerns_cited) ? r.concerns_cited : [];
    const hasConcerns = concerns.length > 0;
    const tier = (r.final_tier || r.base_tier || "").toLowerCase();

    if (phase === "pre_llm" || phase === "deterministic") {
      if (v === "deny")  return "Blocked before any AI ran — a safety rule matched the command.";
      if (v === "allow") return "Cleared automatically — the command matched the safe-pass list.";
    }
    if (v === "allow") {
      if (!hasConcerns) return "Panel reviewed the command and found no problems. Cleared to run.";
      return "Panel reviewed the command. Concerns were noted but did not block it.";
    }
    if (v === "deny") {
      if (hasConcerns) return "Panel found concerns and blocked the command before it ran.";
      return "Panel blocked the command.";
    }
    if (v === "edit") {
      return "Panel rewrote the command into a safer form before it ran.";
    }
    if (v === "ask") {
      return "Panel could not agree, so you were asked to decide.";
    }
    if (tier === "low") return "Low-risk — passed the fast screen without a panel.";
    return "Reviewed by the panel.";
  }

  /* sagaToggleDetail — toggles the visibility of an expand panel row.
   * Keyboard-operable: the button carries aria-expanded / aria-controls.
   * Exposed on window so the inline onclick attribute can reach it from
   * inside the IIFE. */
  function sagaToggleDetail(btn, detailId) {
    const open = btn.getAttribute("aria-expanded") === "true";
    const row = document.getElementById(detailId);
    if (!row) return;
    if (open) {
      btn.setAttribute("aria-expanded", "false");
      btn.textContent = "How this was decided ▾";
      row.classList.remove("open");
    } else {
      btn.setAttribute("aria-expanded", "true");
      btn.textContent = "Hide ▴";
      row.classList.add("open");
    }
  }
  window.sagaToggleDetail = sagaToggleDetail;

  /* Build a static "offline / empty" panel using only DOM methods — no
   * innerHTML / insertAdjacentHTML so there is no XSS sink even if this
   * helper is ever called from a new code path. */
  function sagaEmptyPanel(primaryText, codeSnippet) {
    /* Renders:  <div class="saga-empty"><p>{primaryText} <code>{codeSnippet}</code></p></div>
     * codeSnippet is optional; both values are set via textContent, never innerHTML. */
    const wrap = document.createElement("div");
    wrap.className = "saga-empty";
    const p = document.createElement("p");
    p.textContent = primaryText;
    if (codeSnippet) {
      const code = document.createElement("code");
      code.textContent = codeSnippet;
      p.appendChild(document.createTextNode(" "));
      p.appendChild(code);
    }
    wrap.appendChild(p);
    return wrap;
  }

  function renderSagaTable(records) {
    if (!sagaContent) return;
    if (!records || records.length === 0) {
      const isStatic = location.protocol === "file:";
      sagaContent.replaceChildren(
        isStatic
          ? sagaEmptyPanel("Open the dashboard via", "rc dashboard")
          : sagaEmptyPanel("No command reviews yet. Turn on command review in Settings, and each command\u2019s verdict (allow / edit / deny) shows up here.")
      );
      if (sagaCount) sagaCount.textContent = "";
      return;
    }

    /* Populate category filter from data (sorted, deduplicated).
     * Category values come from /__saga; escape them when building option text. */
    if (sagaCatFil) {
      const cats = [...new Set(records.map(r => r.category).filter(Boolean))].sort();
      const cur = sagaCatFil.value;
      /* option values and text are set via textContent/value — no innerHTML. */
      const all = document.createElement("option");
      all.value = ""; all.textContent = "All";
      sagaCatFil.replaceChildren(all);
      for (const c of cats) {
        const opt = document.createElement("option");
        opt.value = c;
        opt.textContent = c;
        if (c === cur) opt.selected = true;
        sagaCatFil.appendChild(opt);
      }
    }

    filterAndRenderSaga();
  }

  function filterAndRenderSaga() {
    if (!sagaContent) return;
    const verdF = sagaVerdFil ? sagaVerdFil.value : "";
    const catF  = sagaCatFil  ? sagaCatFil.value  : "";

    const filtered = sagaRecords.filter(r =>
      (!verdF || r.final_verdict === verdF) &&
      (!catF  || r.category === catF)
    );

    if (sagaCount) sagaCount.textContent = filtered.length + " of " + sagaRecords.length + " entries";

    if (filtered.length === 0) {
      sagaContent.replaceChildren(
        sagaEmptyPanel("No entries match the current filters.")
      );
      return;
    }

    /* Build the table rows as an HTML string. Every data field is passed through
     * esc() before interpolation. Fixed class names and element tags are literals. */
    let rows = "";
    for (let idx = 0; idx < filtered.length; idx++) {
      const r = filtered[idx];
      const detailId = "saga-detail-" + idx;

      /* Time — the localized string comes from the JS engine, not server data. */
      let timeStr = r.timestamp || "";
      try {
        if (timeStr) timeStr = new Date(timeStr).toLocaleString(undefined, { dateStyle: "short", timeStyle: "short" });
      } catch (_) { /* keep raw ISO string */ }

      /* Action cell — esc() both parts before joining. */
      const fullAction = esc(r.tool_name || "") + ": " + esc(r.action || "");
      const dispAction = fullAction.length > 82 ? fullAction.slice(0, 82) + "…" : fullAction;

      /* Seats */
      let seatsHtml = "";
      if (!r.seats || r.seats.length === 0) {
        seatsHtml = '<span class="saga-seat-chip saga-seat-det">deterministic / pre-LLM</span>';
      } else {
        for (const s of r.seats) {
          const pct = s.confidence != null ? Math.round(s.confidence * 100) + "%" : "";
          const cls = sagaSeatClass(s.verdict);
          /* name and verdict are seat identifiers — esc them. */
          seatsHtml += `<span class="saga-seat-chip ${cls}">${esc(s.name)} ${esc(s.verdict)} ${esc(pct)}</span>`;
        }
      }

      /* Verdict pill — final_verdict is an enum from the engine; still esc. */
      const vv = r.final_verdict || "";
      const vPill = `<span class="saga-verdict-pill ${sagaVerdictClass(vv)}">${esc(vv) || "&mdash;"}</span>`;

      /* Reason column: plain-language summary + "How this was decided" button.
       * reasonPlain() returns a hardcoded string derived from typed fields; esc()
       * is still applied for defence-in-depth. */
      const reasonText = esc(reasonPlain(r));
      const expandBtn =
        `<button type="button" class="saga-expand-btn"` +
        ` aria-expanded="false" aria-controls="${esc(detailId)}"` +
        ` onclick="sagaToggleDetail(this,'${esc(detailId)}')"` +
        `>How this was decided &#9660;</button>`;
      const reasonCell =
        `<div class="saga-reason">${reasonText}${expandBtn}</div>`;

      /* ── Decision detail panel (6 steps) ─────────────────────────── */
      /* Step 1 — Action (full command, monospaced) */
      const stepAction = `<code>${fullAction}</code>`;

      /* Step 2 — Risk category + base_tier badge */
      const baseTier = r.base_tier || r.tier || "";
      const baseTierBadge = baseTier
        ? `<span class="saga-tier-badge ${sagaTierClass(baseTier)}">${esc(baseTier)}</span>`
        : "&mdash;";
      const stepRisk = `${esc(r.category) || "&mdash;"} &nbsp; ${baseTierBadge}`;

      /* Step 3 — Concerns cited; show which raised the tier to final_tier if different */
      const concerns = Array.isArray(r.concerns_cited) ? r.concerns_cited : [];
      const finalTier = r.final_tier || baseTier;
      let stepConcerns;
      if (concerns.length === 0) {
        stepConcerns = "None";
      } else {
        const concEsc = concerns.map(c => `<code>${esc(c)}</code>`).join(", ");
        if (finalTier && finalTier !== baseTier) {
          const finalBadge =
            `<span class="saga-tier-badge ${sagaTierClass(finalTier)}">${esc(finalTier)}</span>`;
          stepConcerns = `${concEsc} &rarr; raised tier to ${finalBadge}`;
        } else {
          stepConcerns = concEsc;
        }
      }

      /* Step 4 — What happened (phase label) */
      const phLower = (r.phase || "").toLowerCase();
      let stepWhat;
      if (phLower.includes("clean-read")) stepWhat = "Low-risk read - allowed automatically; no panel needed.";
      else if (phLower.includes("self-disable")) stepWhat = "Blocked before any panel - it tried to change the safety system itself.";
      else if (phLower.includes("single-seat")) stepWhat = "Reviewed by a single seat.";
      else if (phLower.includes("panel")) stepWhat = "Reviewed by a " + (Array.isArray(r.seats) ? r.seats.length : "?") + "-seat panel.";
      else stepWhat = esc(r.phase || "&mdash;");

      /* Step 5 — Panel votes (seat chips) */
      const stepVotes = seatsHtml || '<span class="saga-seat-chip saga-seat-det">no panel ran</span>';

      /* Step 6 — Decision: verdict + duration + rewrite */
      const finalBadge =
        `<span class="saga-verdict-pill ${sagaVerdictClass(vv)}">${esc(vv) || "&mdash;"}</span>`;
      const durationMs = r.duration_ms != null ? esc(String(Math.round(r.duration_ms))) + " ms" : "";
      let stepDecision = finalBadge;
      if (durationMs) stepDecision += ` &nbsp; <span style="font-size:11px;color:var(--muted)">${durationMs}</span>`;
      if (r.rewrite) {
        stepDecision +=
          `<details class="saga-rewrite"><summary>show rewrite</summary><pre>${esc(r.rewrite)}</pre></details>`;
      }

      const detailPanel =
        `<td colspan="7" style="padding:0 10px 10px">` +
        `<div class="saga-detail-panel">` +
        `<div class="saga-detail-steps">` +
        `<span class="saga-detail-label">Action</span><span class="saga-detail-val">${stepAction}</span>` +
        `<span class="saga-detail-label">Risk</span><span class="saga-detail-val">${stepRisk}</span>` +
        `<span class="saga-detail-label">Concerns</span><span class="saga-detail-val">${stepConcerns}</span>` +
        `<span class="saga-detail-label">What happened</span><span class="saga-detail-val">${stepWhat}</span>` +
        `<span class="saga-detail-label">Panel votes</span><span class="saga-detail-val">${stepVotes}</span>` +
        `<span class="saga-detail-label">Decision</span><span class="saga-detail-val">${stepDecision}</span>` +
        `</div></div></td>`;

      /* fullAction is already escaped above; use it directly in title attr. */
      rows +=
        `<tr>` +
        `<td>${esc(timeStr)}</td>` +
        `<td class="saga-action" title="${fullAction}">${dispAction}</td>` +
        `<td>${esc(r.category) || "&mdash;"}</td>` +
        `<td>${esc(r.phase) || "&mdash;"}</td>` +
        `<td>${seatsHtml}</td>` +
        `<td>${vPill}</td>` +
        `<td>${reasonCell}</td>` +
        `</tr>` +
        `<tr class="saga-detail-row" id="${esc(detailId)}">${detailPanel}</tr>`;
    }

    /* The outer skeleton is fixed HTML; only `rows` contains escaped data. */
    sagaContent.innerHTML =
      '<div class="saga-table-wrap"><table class="saga-table" aria-label="Review log">'
      + '<thead><tr>'
      + '<th scope="col">Time</th>'
      + '<th scope="col">Action</th>'
      + '<th scope="col">Category</th>'
      + '<th scope="col">Phase / Tier</th>'
      + '<th scope="col">Seats</th>'
      + '<th scope="col">Verdict</th>'
      + '<th scope="col">Reason</th>'
      + '</tr></thead>'
      + '<tbody>' + rows + '</tbody>'
      + '</table></div>';
  }

  async function loadSaga() {
    sagaLoaded = true;
    if (sagaContent) sagaContent.replaceChildren(
      sagaEmptyPanel("Loading review log…")
    );
    try {
      const res = await fetchT("/__saga?limit=200");
      if (!res.ok) throw new Error("HTTP " + res.status);
      sagaRecords = await res.json();
      renderSagaTable(sagaRecords);
    } catch (e) {
      sagaLoaded = false; /* allow retry on next tab visit */
      if (sagaContent) {
        /* Distinguish a static host (GitHub Pages / file://) from a genuine
         * server error by probing whether the dashboard server is up at all.
         * A failed /__saga fetch on GitHub Pages returns an HTTP-404 *Error*
         * (not a TypeError), so protocol/error-name sniffing misreports static
         * hosts as "server down" — the HEAD /__read probe is the robust signal. */
        const served = await probeReadEndpoint();
        sagaContent.replaceChildren(
          served
            ? sagaEmptyPanel("Could not reach /__saga. Is the server running?", "python3 scripts/serve-dashboards.py")
            : sagaEmptyPanel("The review log needs the served dashboard — open it via", "rc dashboard")
        );
        if (sagaCount) sagaCount.textContent = "";
      }
    }
  }

  if (sagaRefBtn) sagaRefBtn.addEventListener("click", () => { sagaLoaded = false; loadSaga(); });
  if (sagaVerdFil) sagaVerdFil.addEventListener("change", filterAndRenderSaga);
  if (sagaCatFil)  sagaCatFil.addEventListener("change", filterAndRenderSaga);

  /* ── Activity tab — generalizes the Review log over .ravenclaude/runs/<id>/ ──
   * Reuses esc() + sagaEmptyPanel() (same IIFE scope). All /__runs data passes
   * through esc() before innerHTML, exactly like renderSagaTable. */
  function activityStatusClass(s) {
    const v = (s || "").toLowerCase();
    if (v === "complete" || v === "success" || v === "passed" || v === "done") return "activity-status-ok";
    if (v === "partial"  || v === "needs_changes" || v === "warn")             return "activity-status-warn";
    if (v === "blocked"  || v === "failed" || v === "error")                   return "activity-status-bad";
    return "activity-status-neutral";
  }

  function renderActivity(records) {
    if (!activityContent) return;
    if (!records || records.length === 0) {
      const isStatic = location.protocol === "file:";
      activityContent.replaceChildren(
        isStatic
          ? sagaEmptyPanel("Open the dashboard via", "rc dashboard")
          : sagaEmptyPanel("No runs yet. When a task fans out to several specialists, they record it here automatically — start a multi-step task and come back to see it.")
      );
      if (activityCount) activityCount.textContent = "";
      return;
    }
    if (activityCount) activityCount.textContent = records.length + (records.length === 1 ? " run" : " runs");
    let html = "";
    for (const r of records) {
      let timeStr = r.timestamp || "";
      try { if (timeStr) timeStr = new Date(timeStr).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }); } catch (_) { /* keep raw */ }
      const status = r.status || "—";
      const cls = activityStatusClass(r.status);
      const arts = (Array.isArray(r.artifacts) ? r.artifacts : [])
        .map(a => '<span class="activity-art">' + esc(a) + "</span>").join("");
      const evt = r.event_count ? '<span class="activity-art">' + esc(String(r.event_count)) + " events</span>" : "";
      const summary = r.summary ? '<p class="activity-summary">' + esc(r.summary) + "</p>" : "";
      html += '<article class="activity-card">'
        + '<header class="activity-card-head">'
        + '<span class="activity-status ' + cls + '">' + esc(status) + "</span>"
        + '<h3 class="activity-id">' + esc(r.id || "") + "</h3>"
        + '<span class="activity-time">' + esc(timeStr) + "</span>"
        + "</header>"
        + summary
        + '<div class="activity-arts">' + arts + evt + "</div>"
        + "</article>";
    }
    activityContent.innerHTML = html;
  }

  /* Sleipnir's stables — the active git worktrees, shown as a one-row widget at
   * the top of the Activity tab. Served-only (reads .claude/worktrees/); on a
   * static host it shows a short "served dashboard only" note. Labeling only —
   * the worktree mechanism is unchanged. */
  function renderSleipnir(data) {
    const body = document.getElementById("sleipnir-body");
    if (!body) return;
    const n = (data && typeof data.count === "number") ? data.count : 0;
    if (n === 0) {
      body.textContent = "no active worktrees";
      return;
    }
    const names = (data.worktrees || []).slice(0, 8).join(", ");
    body.textContent = n + (n === 1 ? " worktree: " : " worktrees: ") + names;
  }

  /* fetch() has no built-in timeout — a server that accepts the connection but
   * never sends a body would hang a loader's "Loading…" state forever. Wrap the
   * read-only data loaders in an AbortController (default 15s) so a hung endpoint
   * rejects and falls into the loader's existing catch (the honest "could not
   * reach" / served-only state). Declared as a hoisted function so every loader
   * above and below can use it. */
  function fetchT(url, ms) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), ms || 15000);
    return fetch(url, { signal: controller.signal }).finally(() => clearTimeout(id));
  }

  async function loadSleipnir() {
    const body = document.getElementById("sleipnir-body");
    try {
      const res = await fetchT("/__sleipnir");
      if (!res.ok) throw new Error("HTTP " + res.status);
      renderSleipnir(await res.json());
    } catch (e) {
      const served = await probeReadEndpoint();
      if (body) body.textContent = served ? "unavailable" : "served dashboard only";
    }
  }

  async function loadActivity() {
    activityLoaded = true;
    loadSleipnir();
    if (activityContent) activityContent.replaceChildren(sagaEmptyPanel("Loading activity…"));
    try {
      const res = await fetchT("/__runs?limit=200");
      if (!res.ok) throw new Error("HTTP " + res.status);
      activityRecords = await res.json();
      renderActivity(activityRecords);
    } catch (e) {
      activityLoaded = false; /* allow retry on next tab visit */
      if (activityContent) {
        /* Same robust static-vs-server-error detection as loadSaga: a failed
         * /__runs fetch on GitHub Pages is an HTTP-404 Error, not a TypeError,
         * so probe HEAD /__read rather than sniff protocol/error-name. */
        const served = await probeReadEndpoint();
        activityContent.replaceChildren(
          served
            ? sagaEmptyPanel("Could not reach /__runs. Is the server running?", "python3 scripts/serve-dashboards.py")
            : sagaEmptyPanel("Activity needs the served dashboard — open it via", "rc dashboard")
        );
        if (activityCount) activityCount.textContent = "";
      }
    }
  }

  if (activityRefBtn) activityRefBtn.addEventListener("click", () => { activityLoaded = false; loadActivity(); });

  /* ── Heimdall — read-only perimeter-alarm surface ───────────────────────
   * Four cards: hook denials (served-only, /__heimdall), CI runs (client-side
   * GitHub API fetch), version drift (inlined at generate time, works static),
   * and the Gjallarhorn banner (derived from the hook-event tiers). Heimdall
   * never writes — it mirrors what hooks/manifests already emitted. */
  const TIER_LABEL = { red: "Irrecoverable", amber: "Blocked", grey: "Advisory" };

  function hmEmpty(primaryText, codeSnippet) { return sagaEmptyPanel(primaryText, codeSnippet); }

  function renderHookEvents(data) {
    const host = document.getElementById("heimdall-hooks");
    if (!host) return;
    const byHook = (data && data.by_hook) || {};
    const hooks = Object.keys(byHook).sort();
    if (hooks.length === 0) {
      host.replaceChildren(hmEmpty("No recent events — your perimeter has been quiet."));
      return;
    }
    const frag = document.createDocumentFragment();
    for (const hook of hooks) {
      const group = document.createElement("div");
      group.className = "hm-hookgroup";
      const h4 = document.createElement("h4");
      h4.className = "hm-hookname";
      h4.textContent = hook;
      group.appendChild(h4);
      for (const ev of byHook[hook]) {
        const row = document.createElement("div");
        const tier = ev.tier || "grey";
        row.className = "hm-evt hm-evt--" + tier;
        const badge = document.createElement("span");
        badge.className = "hm-badge hm-badge--" + tier;
        badge.textContent = TIER_LABEL[tier] || tier;
        const verdict = document.createElement("span");
        verdict.className = "hm-verdict";
        verdict.textContent = (ev.verdict || "") + (ev.rule ? " · " + ev.rule : "");
        const path = document.createElement("code");
        path.className = "hm-path";
        path.textContent = ev.path || ev.tool || "";
        const ts = document.createElement("span");
        ts.className = "hm-ts";
        ts.textContent = ev.ts || "";
        row.append(badge, verdict, path, ts);
        group.appendChild(row);
      }
      frag.appendChild(group);
    }
    host.replaceChildren(frag);
  }

  function renderVersionDrift(rows) {
    const host = document.getElementById("heimdall-drift");
    if (!host) return;
    if (!rows || rows.length === 0) {
      host.replaceChildren(hmEmpty("No plugin manifests found."));
      return;
    }
    const drifted = rows.filter(r => r.drift);
    const table = document.createElement("table");
    table.className = "hm-table";
    const thead = document.createElement("thead");
    const htr = document.createElement("tr");
    for (const label of ["Plugin", "Catalog", "Plugin.json", "Status"]) {
      const th = document.createElement("th");
      th.textContent = label;
      htr.appendChild(th);
    }
    thead.appendChild(htr);
    table.appendChild(thead);
    const tbody = document.createElement("tbody");
    for (const r of rows) {
      const tr = document.createElement("tr");
      if (r.drift) tr.className = "hm-row--drift";
      const cells = [r.plugin, r.marketplace_version, r.plugin_version];
      for (const c of cells) {
        const td = document.createElement("td");
        td.textContent = c || "—";
        tr.appendChild(td);
      }
      const stat = document.createElement("td");
      stat.textContent = r.drift ? "DRIFT" : "ok";
      stat.className = r.drift ? "hm-stat--drift" : "hm-stat--ok";
      tr.appendChild(stat);
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);
    const caption = document.createElement("p");
    caption.className = "heimdall-sub";
    caption.textContent = drifted.length === 0
      ? "All " + rows.length + " plugins in sync with the catalog."
      : drifted.length + " of " + rows.length + " plugins drift from the catalog.";
    host.replaceChildren(caption, table);
  }

  function renderGjallarhorn(tier) {
    const banner = document.getElementById("gjallarhorn-banner");
    const alarmCard = document.getElementById("heimdall-alarm");
    const txt = document.getElementById("gjallarhorn-text");
    if (alarmCard) {
      alarmCard.replaceChildren(
        tier
          ? hmEmpty((TIER_LABEL[tier] || tier) + "-tier alert active — see Recent hook denials above for what was caught and why.")
          : hmEmpty("All clear — no guardrail has blocked or warned on an action this session.")
      );
    }
    if (!banner) return;
    if (!tier) { banner.hidden = true; banner.className = "gjallarhorn"; return; }
    banner.hidden = false;
    banner.className = "gjallarhorn gjallarhorn--" + tier;
    /* a11y: red is assertive (interrupts), amber/grey polite. */
    banner.setAttribute("aria-live", tier === "red" ? "assertive" : "polite");
    if (txt) {
      txt.textContent = tier === "red"
        ? "Irrecoverable action was blocked — review the most recent hook denial."
        : tier === "amber"
          ? "A guardrail denied an action. Review recent hook denials."
          : "Advisory notice from a guardrail.";
    }
  }

  async function fetchCiStatus() {
    const host = document.getElementById("heimdall-ci");
    if (!host) return;
    /* Cache for 5 min in sessionStorage — the 60 req/hr unauth limit is generous,
     * this is defensive against tab-flipping. */
    const cacheKey = "hm-ci-" + REPO_OWNER + "-" + REPO_NAME;
    let cached = null;
    try {
      const raw = sessionStorage.getItem(cacheKey);
      if (raw) { const o = JSON.parse(raw); if (Date.now() - o.t < 300000) cached = o.d; }
    } catch (e) { /* ignore */ }
    if (cached) { renderCiStatus(cached); return; }
    try {
      const url = "https://api.github.com/repos/" + REPO_OWNER + "/" + REPO_NAME + "/actions/runs?per_page=5";
      const res = await fetch(url, { headers: { "Accept": "application/vnd.github+json" } });
      if (res.status === 403) { renderCiState("rate-limited"); return; }
      if (res.status === 404) { renderCiState("private"); return; }
      if (!res.ok) { renderCiState("offline"); return; }
      const data = await res.json();
      const runs = (data.workflow_runs || []).slice(0, 5).map(r => ({
        name: r.name, status: r.status, conclusion: r.conclusion,
        url: r.html_url, created_at: r.created_at, branch: r.head_branch
      }));
      try { sessionStorage.setItem(cacheKey, JSON.stringify({ t: Date.now(), d: runs })); } catch (e) {}
      renderCiStatus(runs);
    } catch (e) {
      renderCiState("offline");
    }
  }

  function renderCiState(kind) {
    const host = document.getElementById("heimdall-ci");
    if (!host) return;
    const msg = {
      "rate-limited": "GitHub API rate-limited — try again shortly.",
      "private": "This marketplace is private; the CI card needs a token. Run the served dashboard with gh auth to populate it.",
      "offline": "Could not reach the GitHub API (offline or blocked)."
    }[kind] || "CI status unavailable.";
    host.replaceChildren(hmEmpty(msg));
  }

  function renderCiStatus(runs) {
    const host = document.getElementById("heimdall-ci");
    if (!host) return;
    if (!runs || runs.length === 0) {
      host.replaceChildren(hmEmpty("No recent CI runs."));
      return;
    }
    const frag = document.createDocumentFragment();
    for (const r of runs) {
      const row = document.createElement("a");
      row.className = "hm-ci-row";
      row.href = r.url || "#";
      row.target = "_blank";
      row.rel = "noopener noreferrer";
      const done = r.status === "completed";
      const ok = r.conclusion === "success";
      const dot = document.createElement("span");
      dot.className = "hm-ci-dot " + (!done ? "hm-ci-dot--run" : ok ? "hm-ci-dot--ok" : "hm-ci-dot--fail");
      dot.setAttribute("aria-hidden", "true");
      const name = document.createElement("span");
      name.className = "hm-ci-name";
      name.textContent = r.name || "workflow";
      const meta = document.createElement("span");
      meta.className = "hm-ci-meta";
      meta.textContent = (r.branch ? r.branch + " · " : "") + (done ? (r.conclusion || "") : (r.status || ""));
      row.append(dot, name, meta);
      frag.appendChild(row);
    }
    host.replaceChildren(frag);
  }

  function readHeimdallInline() {
    const el = document.getElementById("heimdall-data");
    if (!el) return {};
    try { return JSON.parse(el.textContent); } catch (e) { return {}; }
  }

  async function loadHeimdall() {
    heimdallLoaded = true;
    /* Version drift + CI are mode-independent — render them immediately. */
    const inline = readHeimdallInline();
    renderVersionDrift(inline.versionDrift || []);
    fetchCiStatus();
    loadNidhoggr();
    loadKnowledgeHealth();
    /* Hook events + Gjallarhorn need the served endpoint. */
    const hookHost = document.getElementById("heimdall-hooks");
    try {
      const res = await fetchT("/__heimdall?days=30");
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      renderHookEvents(data);
      renderGjallarhorn(data.gjallarhorn_tier);
    } catch (e) {
      heimdallLoaded = false; /* allow retry on next visit */
      const served = await probeReadEndpoint();
      if (hookHost) {
        hookHost.replaceChildren(
          served
            ? hmEmpty("Could not reach /__heimdall. Is the server running?", "python3 scripts/serve-dashboards.py")
            : hmEmpty("Hook-event history needs the served dashboard — open it via", "rc dashboard")
        );
      }
      renderGjallarhorn(null);
    }
  }

  /* Níðhöggr "Debt watch" — served-only (git-derived signals vary by clone depth,
   * so never inlined). One section per signal with a count + a short list. */
  function nidhoggrSection(label, items, fmt) {
    const wrap = document.createElement("div");
    wrap.className = "nid-section";
    const h = document.createElement("h4");
    h.className = "nid-hdr";
    h.textContent = label + " (" + (items ? items.length : 0) + ")";
    wrap.appendChild(h);
    if (!items || items.length === 0) {
      const p = document.createElement("p");
      p.className = "nid-clean";
      p.textContent = "clean";
      wrap.appendChild(p);
      return wrap;
    }
    const ul = document.createElement("ul");
    ul.className = "nid-list";
    for (const it of items.slice(0, 10)) {
      const li = document.createElement("li");
      li.textContent = fmt(it);
      ul.appendChild(li);
    }
    wrap.appendChild(ul);
    return wrap;
  }

  function renderNidhoggr(data) {
    const host = document.getElementById("heimdall-debt");
    if (!host) return;
    data = data || {};
    const thr = data.stale_threshold_days || 120;
    const frag = document.createDocumentFragment();
    frag.appendChild(nidhoggrSection("Plugins not bumped in " + thr + "+ days", data.stale_plugins, (p) => p.plugin + " (last " + p.last_bump + ")"));
    frag.appendChild(nidhoggrSection("Hooks without a CI gate", data.ungated_hooks, (h) => h.hook + " — " + h.plugin));
    frag.appendChild(nidhoggrSection("Superseded decisions", data.superseded_decisions, (s) => String(s)));
    frag.appendChild(nidhoggrSection("TODO/FIXME in commits", data.todo_commits, (t) => String(t)));
    host.replaceChildren(frag);
  }

  async function loadNidhoggr() {
    const host = document.getElementById("heimdall-debt");
    try {
      const res = await fetchT("/__nidhoggr");
      if (!res.ok) throw new Error("HTTP " + res.status);
      renderNidhoggr(await res.json());
    } catch (e) {
      const served = await probeReadEndpoint();
      if (host) {
        host.replaceChildren(
          served
            ? hmEmpty("Could not reach /__nidhoggr. Is the server running?", "python3 scripts/serve-dashboards.py")
            : hmEmpty("Debt signals need the served dashboard — open it via", "rc dashboard")
        );
      }
    }
  }

  /* Idunn "Knowledge health" — served-only (the script invocation needs file-
   * system access GitHub Pages can't provide). Renders 4 click-to-drill bucket
   * tiles (stale / due_soon / untracked / fresh) over plugins/* /knowledge/*.md.
   * Click a tile → expands a sortable list of the files in that bucket. */
  const KH_BUCKETS = [
    { key: "stale",     label: "Stale",     cls: "kh-tile--stale" },
    { key: "due_soon",  label: "Due soon",  cls: "kh-tile--soon" },
    { key: "untracked", label: "Untracked", cls: "kh-tile--untracked" },
    { key: "fresh",     label: "Fresh",     cls: "kh-tile--fresh" },
  ];

  function khEscape(s) { return String(s == null ? "" : s); }

  function khDrillItems(data, bucket) {
    if (bucket === "fresh") {
      return (data.fresh_paths || []).map((p) => ({ path: p, age_days: null, plugin: null }));
    }
    return (data[bucket] || []).map((v) => ({
      path: v.path, age_days: v.age_days, plugin: v.plugin, last_verified: v.last_verified,
    }));
  }

  function renderKhDrill(data, bucket) {
    const drill = document.getElementById("heimdall-kh-drill");
    if (!drill) return;
    if (!bucket) { drill.hidden = true; drill.replaceChildren(); return; }
    const items = khDrillItems(data, bucket);
    drill.hidden = false;
    const h = document.createElement("h4");
    h.className = "kh-drill-hdr";
    const meta = KH_BUCKETS.find((b) => b.key === bucket);
    h.textContent = (meta ? meta.label : bucket) + " — " + items.length + " file" + (items.length === 1 ? "" : "s");
    drill.replaceChildren(h);
    if (items.length === 0) {
      const p = document.createElement("p");
      p.className = "kh-clean";
      p.textContent = bucket === "stale" || bucket === "due_soon" ? "nothing to re-verify" : "no files";
      drill.appendChild(p);
      return;
    }
    const ul = document.createElement("ul");
    ul.className = "kh-drill-list";
    /* Sort: stale + due_soon by oldest first; untracked + fresh alphabetically. */
    if (bucket === "stale" || bucket === "due_soon") {
      items.sort((a, b) => (b.age_days || 0) - (a.age_days || 0));
    } else {
      items.sort((a, b) => khEscape(a.path).localeCompare(khEscape(b.path)));
    }
    for (const it of items) {
      const li = document.createElement("li");
      li.textContent = khEscape(it.path);
      if (it.age_days != null) {
        const span = document.createElement("span");
        span.className = "kh-drill-age";
        span.textContent = "(" + it.age_days + "d, last verified " + (it.last_verified || "?") + ")";
        li.appendChild(span);
      }
      ul.appendChild(li);
    }
    drill.appendChild(ul);
  }

  function renderKnowledgeHealth(data) {
    const host = document.getElementById("heimdall-kh");
    if (!host) return;
    data = data || {};
    if (data.error) {
      const p = document.createElement("p");
      p.className = "kh-error";
      p.textContent = "Knowledge-health unavailable: " + khEscape(data.error);
      host.replaceChildren(p);
      return;
    }
    const counts = data.counts || {};
    const total = counts.total || 0;
    const frag = document.createDocumentFragment();
    const meta = document.createElement("p");
    meta.className = "kh-meta";
    meta.textContent =
      total + " file" + (total === 1 ? "" : "s") + " in plugins/*/knowledge/" +
      (data.today ? " · checked " + data.today : "") +
      (data.threshold_days ? " · stale threshold " + data.threshold_days + " days" : "");
    frag.appendChild(meta);
    const tiles = document.createElement("div");
    tiles.className = "kh-tiles";
    for (const b of KH_BUCKETS) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "kh-tile " + b.cls;
      btn.setAttribute("aria-pressed", "false");
      btn.setAttribute("data-bucket", b.key);
      const n = document.createElement("span");
      n.className = "kh-tile-count";
      n.textContent = String(counts[b.key] || 0);
      const lab = document.createElement("span");
      lab.className = "kh-tile-label";
      lab.textContent = b.label;
      btn.append(n, lab);
      btn.addEventListener("click", () => {
        const already = btn.getAttribute("aria-pressed") === "true";
        for (const sib of tiles.querySelectorAll(".kh-tile")) sib.setAttribute("aria-pressed", "false");
        if (already) {
          renderKhDrill(data, null);
        } else {
          btn.setAttribute("aria-pressed", "true");
          renderKhDrill(data, b.key);
        }
      });
      tiles.appendChild(btn);
    }
    frag.appendChild(tiles);
    const drill = document.createElement("div");
    drill.className = "kh-drill";
    drill.id = "heimdall-kh-drill";
    drill.hidden = true;
    frag.appendChild(drill);
    host.replaceChildren(frag);
  }

  async function loadKnowledgeHealth() {
    const host = document.getElementById("heimdall-kh");
    try {
      const res = await fetchT("/__knowledge-health");
      if (!res.ok) throw new Error("HTTP " + res.status);
      renderKnowledgeHealth(await res.json());
    } catch (e) {
      const served = await probeReadEndpoint();
      if (host) {
        host.replaceChildren(
          served
            ? hmEmpty("Could not reach /__knowledge-health. Is the server running?", "python3 scripts/serve-dashboards.py")
            : hmEmpty("Knowledge-health needs the served dashboard — open it via", "rc dashboard")
        );
      }
    }
  }

  const heimdallRefBtn = document.getElementById("heimdall-refresh-btn");
  if (heimdallRefBtn) heimdallRefBtn.addEventListener("click", () => { heimdallLoaded = false; loadHeimdall(); });

  /* ── Víðarr — read-only posture/security event log ──────────────────────
   * A chronological, filterable table of posture changes (posture-events.jsonl)
   * interleaved with security-relevant hook denials (hook-events.jsonl, deny-
   * only). Served-only (both sources are git-ignored/per-consumer); on a static
   * host it degrades to an honest empty state. Filters are client-side over the
   * fetched set for type; the time range re-fetches with a ?days= param. */
  const VIDARR_KIND_LABEL = { "posture-change": "Posture change", "security-deny": "Security denial" };

  function renderVidarrTable(events) {
    const host = document.getElementById("vidarr-content");
    const countEl = document.getElementById("vidarr-count");
    if (!host) return;
    const filtered = (events || []).filter(
      (e) => vidarrKindFilter === "all" || e.kind === vidarrKindFilter,
    );
    if (countEl) countEl.textContent = filtered.length ? filtered.length + " event" + (filtered.length === 1 ? "" : "s") : "";
    if (filtered.length === 0) {
      host.replaceChildren(hmEmpty("No security events. Your perimeter has been quiet."));
      return;
    }
    const table = document.createElement("table");
    table.className = "vidarr-table";
    const thead = document.createElement("thead");
    const htr = document.createElement("tr");
    for (const label of ["When", "Type", "Category", "Summary", "Source"]) {
      const th = document.createElement("th");
      th.textContent = label;
      htr.appendChild(th);
    }
    thead.appendChild(htr);
    table.appendChild(thead);
    const tbody = document.createElement("tbody");
    for (const e of filtered) {
      const tr = document.createElement("tr");
      tr.className = "vidarr-row vidarr-row--" + (e.kind || "");
      const cells = [
        e.ts || "",
        VIDARR_KIND_LABEL[e.kind] || e.kind || "",
        e.category || "",
        e.summary || "",
        e.source || "",
      ];
      cells.forEach((c, i) => {
        const td = document.createElement("td");
        td.textContent = c;
        if (i === 1) {
          const tag = document.createElement("span");
          tag.className = "vidarr-kind vidarr-kind--" + (e.kind || "");
          tag.textContent = c;
          td.replaceChildren(tag);
        }
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);
    host.replaceChildren(table);
  }

  async function loadVidarr() {
    vidarrLoaded = true;
    const host = document.getElementById("vidarr-content");
    const rangeSel = document.getElementById("vidarr-range");
    const days = (rangeSel && rangeSel.value) || "30";
    if (host) host.replaceChildren(hmEmpty("Loading security log…"));
    try {
      const res = await fetchT("/__vidarr?days=" + encodeURIComponent(days));
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      vidarrEvents = (data && data.events) || [];
      renderVidarrTable(vidarrEvents);
    } catch (e) {
      vidarrLoaded = false; /* allow retry on next visit */
      const served = await probeReadEndpoint();
      if (host) {
        host.replaceChildren(
          served
            ? hmEmpty("Could not reach /__vidarr. Is the server running?", "python3 scripts/serve-dashboards.py")
            : hmEmpty("The security log needs the served dashboard — open it via", "rc dashboard")
        );
      }
      const countEl = document.getElementById("vidarr-count");
      if (countEl) countEl.textContent = "";
    }
  }

  const vidarrRefBtn = document.getElementById("vidarr-refresh-btn");
  if (vidarrRefBtn) vidarrRefBtn.addEventListener("click", () => { vidarrLoaded = false; loadVidarr(); });
  const vidarrRangeSel = document.getElementById("vidarr-range");
  if (vidarrRangeSel) vidarrRangeSel.addEventListener("change", () => { vidarrLoaded = false; loadVidarr(); });
  const vidarrChips = document.getElementById("vidarr-typechips");
  if (vidarrChips) {
    vidarrChips.addEventListener("click", (ev) => {
      const btn = ev.target.closest(".vidarr-chip");
      if (!btn) return;
      vidarrKindFilter = btn.dataset.kind || "all";
      vidarrChips.querySelectorAll(".vidarr-chip").forEach((b) => {
        const on = b === btn;
        b.classList.toggle("vidarr-chip--active", on);
        b.setAttribute("aria-pressed", on ? "true" : "false");
      });
      renderVidarrTable(vidarrEvents);
    });
  }

  /* ── Norns — read-only plugin lineage (Urðr / Verðandi / Skuld) ─────────
   * Three columns drawn live from /__norns (git log + scenario events + the
   * manifest). Served-only — git/scenario data varies by clone depth so it is
   * NEVER inlined into the committed HTML (that would break the freshness gate).
   * On a static host the columns degrade to an honest empty state. */
  function nornsList(items, emptyText, fmt) {
    const wrap = document.createElement("div");
    if (!items || items.length === 0) {
      wrap.appendChild(hmEmpty(emptyText));
      return wrap;
    }
    const ul = document.createElement("ul");
    ul.className = "norns-itemlist";
    for (const it of items) {
      const li = document.createElement("li");
      li.textContent = fmt ? fmt(it) : String(it);
      ul.appendChild(li);
    }
    wrap.appendChild(ul);
    return wrap;
  }

  function renderNornsUrdr(urdr) {
    const host = document.getElementById("norns-urdr");
    if (!host) return;
    urdr = urdr || {};
    const frag = document.createDocumentFragment();
    const sc = document.createElement("h4");
    sc.className = "norns-grouphdr";
    sc.textContent = "Surfaced scenarios";
    frag.append(sc, nornsList((urdr.scenarios || []).map((s) => s.scenario_path || ""), "No surfaced scenarios in scope.", (p) => p.split("/").pop()));
    const dc = document.createElement("h4");
    dc.className = "norns-grouphdr";
    dc.textContent = "Decisions";
    frag.append(dc, nornsList(urdr.decisions || [], "No decision-log entries."));
    const cm = document.createElement("h4");
    cm.className = "norns-grouphdr";
    cm.textContent = "Recent commits";
    frag.append(cm, nornsList(urdr.commits || [], "No commits in scope (or git unavailable)."));
    host.replaceChildren(frag);
  }

  function renderNornsVerdandi(v) {
    const host = document.getElementById("norns-verdandi");
    if (!host) return;
    v = v || {};
    const rows = [
      ["Version", v.version || "—"],
      ["Active hooks", String(v.hooks != null ? v.hooks : "—")],
      ["Active rules", String(v.rules != null ? v.rules : "—")],
      ["Last release", v.last_release || "—"],
    ];
    const dl = document.createElement("dl");
    dl.className = "norns-dl";
    for (const [k, val] of rows) {
      const dt = document.createElement("dt");
      dt.textContent = k;
      const dd = document.createElement("dd");
      dd.textContent = val;
      dl.append(dt, dd);
    }
    host.replaceChildren(dl);
  }

  function renderNornsSkuld(s) {
    const host = document.getElementById("norns-skuld");
    if (!host) return;
    s = s || {};
    /* Gated empty state: no plugin declares next_version yet (P0.1 not shipped). */
    if (!s.next_version && (!s.roadmap || s.roadmap.length === 0) && (!s.proposals || s.proposals.length === 0)) {
      host.replaceChildren(
        hmEmpty("No proposed version. Add a next_version field to this plugin's plugin.json to populate Skuld."),
      );
      return;
    }
    const frag = document.createDocumentFragment();
    if (s.next_version) {
      const p = document.createElement("p");
      p.className = "norns-nextver";
      p.textContent = "Proposed version: " + s.next_version;
      frag.appendChild(p);
    }
    if (s.roadmap && s.roadmap.length) {
      const h = document.createElement("h4");
      h.className = "norns-grouphdr";
      h.textContent = "Roadmap";
      frag.append(h, nornsList(s.roadmap, "—"));
    }
    const ph = document.createElement("h4");
    ph.className = "norns-grouphdr";
    ph.textContent = "Open proposals";
    frag.append(ph, nornsList(s.proposals || [], "No proposals reference this plugin."));
    host.replaceChildren(frag);
  }

  async function loadNorns() {
    nornsLoaded = true;
    try {
      const res = await fetchT("/__norns?plugin=ravenclaude-core");
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      renderNornsUrdr(data.urdr);
      renderNornsVerdandi(data.verdandi);
      renderNornsSkuld(data.skuld);
    } catch (e) {
      nornsLoaded = false; /* allow retry on next visit */
      const served = await probeReadEndpoint();
      const msg = served
        ? ["Could not reach /__norns. Is the server running?", "python3 scripts/serve-dashboards.py"]
        : ["Plugin lineage needs the served dashboard — open it via", "rc dashboard"];
      for (const id of ["norns-urdr", "norns-verdandi", "norns-skuld"]) {
        const host = document.getElementById(id);
        if (host) host.replaceChildren(hmEmpty(msg[0], msg[1]));
      }
    }
  }

  const nornsRefBtn = document.getElementById("norns-refresh-btn");
  if (nornsRefBtn) nornsRefBtn.addEventListener("click", () => { nornsLoaded = false; loadNorns(); });

  /* ── Mímir's well — Claude Code session-state surface ────────────────────
   * Fetches /__mimir (served-only). The five card hosts mirror the
   * _read_mimir payload (settings / session / activity / recent_sessions /
   * unreachable). In-process-only fields ("effort_dial", "plan_tier",
   * "status_live_cache") render with an explainer pill, never a dash —
   * the honest empty state is the contract (per the mimir skill). */
  function mimirDash(v) {
    return v == null || v === "" ? "—" : String(v);
  }
  function mimirInProcessPill(label) {
    const pill = document.createElement("span");
    pill.className = "mimir-pill mimir-pill--inproc";
    pill.textContent = label;
    pill.title = "In-process only — run /status in Claude Code to see this live";
    return pill;
  }
  function mimirDl(rows) {
    const dl = document.createElement("dl");
    dl.className = "norns-dl";
    for (const [k, v] of rows) {
      const dt = document.createElement("dt");
      dt.textContent = k;
      const dd = document.createElement("dd");
      if (v instanceof Node) dd.appendChild(v);
      else dd.textContent = mimirDash(v);
      dl.append(dt, dd);
    }
    return dl;
  }
  function renderMimirSettings(s) {
    const host = document.getElementById("mimir-settings");
    if (!host) return;
    s = s || {};
    const m = s.model || {};
    host.replaceChildren(mimirDl([
      ["Theme", s.theme],
      ["Configured model", m.configured],
      ["Last-used model", m.last_used],
      ["Permission mode", s.permission_mode],
      ["Reasoning effort", mimirInProcessPill("in-process — /effort")],
    ]));
  }
  function renderMimirSession(sess) {
    const host = document.getElementById("mimir-session");
    if (!host) return;
    sess = sess || {};
    if (!sess.found) {
      host.replaceChildren(hmEmpty("No live Claude Code session found for this project."));
      return;
    }
    host.replaceChildren(mimirDl([
      ["Session ID", sess.session_id],
      ["PID", sess.pid != null ? String(sess.pid) : null],
      ["Started", sess.started_at],
      ["Version", sess.version],
      ["Status", mimirInProcessPill("/status — in-process only")],
    ]));
  }
  function renderMimirActivity(a) {
    const host = document.getElementById("mimir-activity");
    if (!host) return;
    a = a || {};
    const frag = document.createDocumentFragment();
    if (a.as_of) {
      const pill = document.createElement("span");
      pill.className = "mimir-pill mimir-pill--asof";
      pill.textContent = "as of " + a.as_of;
      pill.title = "stats-cache.json is pre-computed; up to 24h stale";
      frag.appendChild(pill);
    }
    frag.appendChild(mimirDl([
      ["Total sessions", a.total_sessions != null ? String(a.total_sessions) : null],
      ["Total messages", a.total_messages != null ? String(a.total_messages) : null],
    ]));
    const days = Array.isArray(a.daily_activity_7d) ? a.daily_activity_7d : [];
    if (days.length) {
      const h = document.createElement("h4");
      h.className = "norns-grouphdr";
      h.textContent = "Last 7 days";
      frag.appendChild(h);
      const ul = document.createElement("ul");
      ul.className = "mimir-days";
      for (const d of days) {
        const li = document.createElement("li");
        const date = (d && d.date) || "?";
        const msgs = (d && (d.messageCount != null ? d.messageCount : "—"));
        const sess = (d && (d.sessionCount != null ? d.sessionCount : "—"));
        li.textContent = date + " — " + msgs + " msg, " + sess + " sess";
        ul.appendChild(li);
      }
      frag.appendChild(ul);
    }
    host.replaceChildren(frag);
  }
  function renderMimirRecent(items) {
    const host = document.getElementById("mimir-recent");
    if (!host) return;
    const list = Array.isArray(items) ? items : [];
    if (!list.length) {
      host.replaceChildren(hmEmpty("No recent JSONL sessions for this project."));
      return;
    }
    const ul = document.createElement("ul");
    ul.className = "mimir-recent-list";
    for (const it of list) {
      const li = document.createElement("li");
      const sid = (it && it.session_id) || "—";
      const ts  = (it && it.last_active) || "—";
      const ec  = (it && it.event_count != null) ? it.event_count : "—";
      const ot  = (it && it.output_tokens != null) ? it.output_tokens : "—";
      const br  = (it && it.git_branch) || "—";
      li.textContent = sid + " · " + ts + " · " + ec + " events · " + ot + " output toks · " + br;
      ul.appendChild(li);
    }
    host.replaceChildren(ul);
  }
  function renderMimirUnreachable(items) {
    const host = document.getElementById("mimir-unreach");
    if (!host) return;
    const list = Array.isArray(items) ? items : [];
    const ul = document.createElement("ul");
    ul.className = "mimir-unreach-list";
    const labels = {
      "effort_dial": "Reasoning effort (/effort dial) — runtime only",
      "plan_tier": "Plan tier (Pro / Max / Team) — not stored on disk",
      "status_live_cache": "/status live cache — in-process only",
    };
    for (const k of list) {
      const li = document.createElement("li");
      li.textContent = labels[k] || k;
      ul.appendChild(li);
    }
    if (!ul.children.length) {
      host.replaceChildren(hmEmpty("Nothing currently unreachable."));
      return;
    }
    host.replaceChildren(ul);
  }
  async function loadMimir() {
    mimirLoaded = true;
    try {
      const res = await fetchT("/__mimir");
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      renderMimirSettings(data.settings);
      renderMimirSession(data.session);
      renderMimirActivity(data.activity);
      renderMimirRecent(data.recent_sessions);
      renderMimirUnreachable(data.unreachable);
    } catch (e) {
      mimirLoaded = false; /* allow retry on next visit */
      const served = await probeReadEndpoint();
      const msg = served
        ? ["Could not reach /__mimir. Is the server running?", "python3 scripts/serve-dashboards.py"]
        : ["Session state needs the served dashboard — open it via", "rc dashboard"];
      for (const id of ["mimir-settings", "mimir-session", "mimir-activity", "mimir-recent", "mimir-unreach"]) {
        const host = document.getElementById(id);
        if (host) host.replaceChildren(hmEmpty(msg[0], msg[1]));
      }
    }
  }
  const mimirRefBtn = document.getElementById("mimir-refresh-btn");
  if (mimirRefBtn) mimirRefBtn.addEventListener("click", () => { mimirLoaded = false; loadMimir(); });

  /* ── Bifröst — install-bridge wizard (§3.6) ─────────────────────────────
   * Pure client-side copy-paste flow. The wizard NEVER runs a slash command —
   * the user runs each in their session and pastes the output; we parse it with
   * a per-step success/failure regex to advance the bridge (light the next
   * step's badge) or auto-expand the matching failure-mode accordion row. No
   * fetch, no /__ endpoint, no programmatic command invocation. */
  const BIFROST_RULES = {
    "1": { ok: /marketplace\s+added|added\s+marketplace|successfully\s+added/i, bad: /failed|error|not\s+found|could\s+not/i },
    "2": { ok: /installed|install\s+complete|successfully\s+installed/i, bad: /failed|error|no\s+such\s+plugin|not\s+found/i },
    "3": { ok: /reloaded|reload\s+complete|i\s+see\s+it|plugins?\s+reloaded/i, bad: /failed|error|stale/i },
    "4": { ok: /\bgreen\b|pass(ed)?|agent[- ]ready|all\s+checks?\s+pass/i, bad: /\bred\b|fail(ed)?|missing|error/i },
  };

  function bifrostSetBadge(step, state) {
    const badge = document.getElementById("bifrost-badge-" + step);
    if (!badge) return;
    badge.className = "bifrost-badge bifrost-badge--" + state;
    badge.textContent =
      state === "green" ? "Done"
      : state === "red" ? "Needs attention"
      : state === "amber" ? "Unclear — re-check"
      : "Not started";
  }

  function bifrostExpandFault(idx) {
    const toggle = document.querySelector('#bifrost-fault-' + idx + ' .bifrost-fault-toggle');
    const body = document.getElementById("bifrost-fault-body-" + idx);
    if (toggle && body) {
      toggle.setAttribute("aria-expanded", "true");
      body.hidden = false;
    }
  }

  function bifrostVerify(step) {
    const ta = document.getElementById("bifrost-paste-" + step);
    const out = ta ? (ta.value || "") : "";
    const rules = BIFROST_RULES[step];
    if (!out.trim()) { bifrostSetBadge(step, "amber"); return; }
    if (rules && rules.bad.test(out)) {
      bifrostSetBadge(step, "red");
      bifrostExpandFault(step); /* fault rows are 1:1 with steps */
      return;
    }
    if (rules && rules.ok.test(out)) {
      bifrostSetBadge(step, "green");
      /* Light the next step's badge from grey → "ready" cue via amber-less hint:
       * we leave it "Not started" but scroll it into view for linear flow. */
      const next = document.getElementById("bifrost-step-" + (parseInt(step, 10) + 1));
      if (next) next.classList.add("bifrost-step--ready");
      return;
    }
    /* Output present but matched neither pattern → unclear. */
    bifrostSetBadge(step, "amber");
  }

  function bifrostCopy(targetId, btn) {
    const el = document.getElementById(targetId);
    if (!el) return;
    const text = el.textContent || "";
    const done = () => { if (btn) { const o = btn.textContent; btn.textContent = "Copied!"; setTimeout(() => { btn.textContent = o; }, 1200); } };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, () => {});
    } else {
      const r = document.createRange(); r.selectNodeContents(el);
      const sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r);
      try { document.execCommand("copy"); done(); } catch (e) {}
      sel.removeAllRanges();
    }
  }

  const bifrostPanel = document.querySelector('.tab-panel[data-tab="bifrost"]');
  if (bifrostPanel) {
    bifrostPanel.addEventListener("click", (ev) => {
      const copyBtn = ev.target.closest(".bifrost-copy");
      if (copyBtn) { bifrostCopy(copyBtn.dataset.copyTarget, copyBtn); return; }
      const verifyBtn = ev.target.closest(".bifrost-verify");
      if (verifyBtn) { bifrostVerify(verifyBtn.dataset.verifyStep); return; }
      const faultToggle = ev.target.closest(".bifrost-fault-toggle");
      if (faultToggle) {
        const expanded = faultToggle.getAttribute("aria-expanded") === "true";
        faultToggle.setAttribute("aria-expanded", expanded ? "false" : "true");
        const body = faultToggle.parentElement.querySelector(".bifrost-fault-body");
        if (body) body.hidden = expanded;
      }
    });
  }

  /* ── Hydrate command-review config from the committed YAML ──────────── */
  /* When the page is served by scripts/serve-dashboards.py, the committed
   * .ravenclaude/comfort-posture.yaml is the source of truth — it OVERRIDES
   * localStorage so the controls reflect what is actually on disk, not a stale
   * draft. Served mode is detected with a HEAD /__read probe, mirroring the
   * Settings tab's HEAD /__save probe. GitHub Pages / file:// / `http.server`
   * lack the endpoint, so we fail soft and keep the defaults/localStorage path.
   *
   * Scope: command_review (gate_floor + tiers + panel seats + confidence),
   * design_checkins, security_deny, and the per-category posture (per-layer
   * levels + the per-category `thing:` toggle + per-permission overrides).
   * Every field access is guarded — missing keys are skipped, never thrown. */
  const READ_TARGET = ".ravenclaude/comfort-posture.yaml";

  async function probeReadEndpoint() {
    try {
      const res = await fetch("/__read", { method: "HEAD" });
      return res.ok;
    } catch (e) {
      return false;
    }
  }

  function hydrateFromParsed(parsed) {
    let touched = false;
    const cr = (parsed && typeof parsed.command_review === "object" && parsed.command_review) || null;
    if (cr) {
      /* gate_floor → state + matching radio */
      if (GATE_FLOORS.includes(cr.gate_floor)) {
        state.command_review.gate_floor = cr.gate_floor;
        touched = true;
      }
      /* per-seat panel models */
      const panel = (typeof cr.panel === "object" && cr.panel) || null;
      if (panel) {
        for (const seat of CR_SEATS) {
          const ps = panel[seat];
          if (ps && typeof ps === "object" && CR_MODELS.includes(ps.model)) {
            state.command_review[seat] = ps.model;
            touched = true;
          }
        }
      }
      /* global confidence threshold */
      const gt = parseFloat(cr.confidence_threshold);
      if (!Number.isNaN(gt) && gt >= 0 && gt <= 1) {
        state.command_review.confidence_threshold = gt;
        touched = true;
      }
      /* per-tier seats + thresholds (mandatory_seats stay engine-pinned) */
      const tiers = (typeof cr.tiers === "object" && cr.tiers) || null;
      if (tiers) {
        for (const tier of TIERS) {
          const pt = tiers[tier];
          if (!pt || typeof pt !== "object") continue;
          const dst = state.command_review.tiers[tier];
          if (Array.isArray(pt.seats)) {
            const seats = pt.seats.filter(s => TIER_SEATS.includes(s));
            for (const m of dst.mandatory_seats) if (!seats.includes(m)) seats.push(m);
            dst.seats = TIER_SEATS.filter(s => seats.includes(s));
            touched = true;
          }
          const tt = parseFloat(pt.confidence_threshold);
          if (!Number.isNaN(tt) && tt >= 0 && tt <= 1) {
            dst.confidence_threshold = tt;
            touched = true;
          }
        }
      }
    }
    /* design_checkins behavioral flag */
    if (typeof parsed.design_checkins === "boolean") {
      state.design_checkins = parsed.design_checkins;
      touched = true;
    }
    /* Pipeline-stage guardrails — runaway / decision_review / definition_of_done
     * / command_review.dev_repo_exempt, via the shared validator (same shape as
     * the localStorage path). */
    if (applyGuardrailConfig(parsed)) touched = true;
    /* ── Per-category permission posture ─────────────────────────────── */
    /* The committed file expresses the SAME shape the dashboard authors, so we
     * map it back field-for-field, guarding every access (a key the file omits
     * leaves the existing control untouched — we never throw on a missing key).
     *
     * Coverage vs. the v5 state model:
     *   - parsed.global_default → the v5 per-layer model has no single
     *     global-default control (it sets every category's local layer via a
     *     preset, not a stored scalar), so there is no slot to hydrate; we read
     *     it defensively and skip. Per-category values below fully express the
     *     posture.
     *   - parsed.security_deny (array) → state.security_deny (intersected with
     *     the always-on baseline so unblocking only sticks for known patterns).
     *   - parsed.categories[<cat>] → each category's user/local/project layers,
     *     its `thing:` toggle, and its nested per-permission `overrides` map.
     *   - parsed.overrides (top-level v5 per-permission map) is read defensively
     *     and merged onto the matching category when the engine ever emits it at
     *     the top level; the canonical home is per-category overrides above. */
    const LAYER_VALUES = ["allow", "ask", "deny", "inherit"];
    function hydrateOverrideMap(dst, src) {
      /* dst: a category's overrides object; src: a {pattern:{user,local,project}}
       * map. Keeps only well-formed, non-all-inherit entries. Returns true if it
       * changed anything. */
      if (!src || typeof src !== "object") return false;
      let changed = false;
      for (const pat of Object.keys(src)) {
        const o = src[pat];
        if (!o || typeof o !== "object") continue;
        const rec = { user: "inherit", local: "inherit", project: "inherit" };
        for (const L of ["user", "local", "project"]) {
          if (LAYER_VALUES.includes(o[L])) rec[L] = o[L];
        }
        if (rec.user !== "inherit" || rec.local !== "inherit" || rec.project !== "inherit") {
          dst[pat] = rec;
          changed = true;
        }
      }
      return changed;
    }

    /* parsed.global_default — defensive read; no state slot in the v5 model. */
    if (typeof parsed.global_default === "string" && LAYER_VALUES.includes(parsed.global_default)) {
      /* No global-default control to drive; per-category values carry the
       * posture. Read + ignore so a present key is never a hard error. */
    }

    /* parsed.security_deny — intersect with the always-on baseline. */
    if (Array.isArray(parsed.security_deny)) {
      state.security_deny = parsed.security_deny.filter(
        p => state.security_deny_baseline.includes(p)
      );
      touched = true;
    }

    /* parsed.categories — per-layer levels + thing toggle + overrides. */
    const pcats = (typeof parsed.categories === "object" && parsed.categories) || null;
    if (pcats) {
      for (const cat of Object.keys(pcats)) {
        const dst = state.categories[cat];
        const src = pcats[cat];
        if (!dst || !src || typeof src !== "object") continue;
        for (const L of ["user", "local", "project"]) {
          if (LAYER_VALUES.includes(src[L])) {
            dst[L] = src[L];
            touched = true;
          }
        }
        /* `thing:` may be a YAML-truthy "on"/"off"/true/false. */
        if (src.thing === true || src.thing === "on") {
          dst.thing = true;
          touched = true;
        } else if (src.thing === false || src.thing === "off") {
          dst.thing = false;
          touched = true;
        }
        if (src.overrides && typeof src.overrides === "object") {
          const ov = dst.overrides || (dst.overrides = {});
          if (hydrateOverrideMap(ov, src.overrides)) touched = true;
        }
      }
    }

    /* parsed.overrides — top-level per-permission map, if the engine emits one.
     * Merge each entry onto the category that owns its pattern (best-effort). */
    if (parsed.overrides && typeof parsed.overrides === "object") {
      for (const cat of Object.keys(state.categories)) {
        const dst = state.categories[cat].overrides || (state.categories[cat].overrides = {});
        /* A flat {pattern:{...}} map carries no category; only merge patterns
         * the category already knows about so we never invent an override. */
        const subset = {};
        for (const pat of Object.keys(parsed.overrides)) {
          if (Object.prototype.hasOwnProperty.call(dst, pat)) subset[pat] = parsed.overrides[pat];
        }
        if (hydrateOverrideMap(dst, subset)) touched = true;
      }
    }
    return touched;
  }

  async function hydrateFromRepo() {
    try {
      const res = await fetch("/__read?path=" + encodeURIComponent(READ_TARGET));
      if (!res.ok) return;   /* 404 → file absent; keep defaults/localStorage */
      const j = await res.json();
      if (!j || j.exists !== true || j.parsed == null || typeof j.parsed !== "object") return;
      const touched = hydrateFromParsed(j.parsed);
      if (!touched) return;
      /* The committed file won — reflect it in the controls, the live YAML
       * preview, and localStorage so a later draft starts from disk truth. */
      syncDomToState();
      render();
      persistState();
      const indicator = document.getElementById("crp-hydrated-indicator");
      if (indicator) indicator.hidden = false;
    } catch (e) {
      /* fail soft — any fetch/parse error leaves the defaults path intact */
      console.warn("Could not hydrate from repo YAML:", e);
    }
  }

  probeReadEndpoint().then(served => {
    if (served) hydrateFromRepo();
  });

  /* ── Learn tab: search · expand/collapse · no-results ──────────────── */
  (function initLearn() {
    const panel = document.querySelector('.tab-panel[data-tab="learn"]');
    if (!panel) return;
    const search = panel.querySelector("#learn-search");
    const count = panel.querySelector("#learn-count");
    const noResults = panel.querySelector("#learn-noresults");
    const cards = Array.from(panel.querySelectorAll(".concept-card"));
    const cats = Array.from(panel.querySelectorAll(".concept-cat"));
    const total = cards.length;

    function applyFilter(raw) {
      const q = (raw || "").trim().toLowerCase();
      let shown = 0;
      cards.forEach(card => {
        const hit = !q || (card.dataset.search || "").indexOf(q) !== -1;
        card.hidden = !hit;
        if (hit) shown++;
      });
      cats.forEach(cat => {
        const any = cat.querySelector(".concept-card:not([hidden])") !== null;
        cat.hidden = !any;
        if (q && any) cat.open = true;
      });
      if (count) count.textContent = q ? shown + " of " + total : total + " concepts";
      if (noResults) noResults.hidden = shown > 0;
    }

    if (search) search.addEventListener("input", () => applyFilter(search.value));
    const expand = panel.querySelector("#learn-expand");
    const collapse = panel.querySelector("#learn-collapse");
    if (expand) expand.addEventListener("click", () => cats.forEach(c => { c.open = true; }));
    if (collapse) collapse.addEventListener("click", () => cats.forEach(c => { c.open = false; }));
    applyFilter("");
  })();

  /* ── Learn tab: interactive concept widgets ────────────────────────── */
  (function initConceptWidgets() {
    const LAYER_NAME = { managed: "Managed", project: "Project", local: "Local", user: "User" };
    const ORDER = ["managed", "project", "local", "user"];
    document.querySelectorAll('[data-widget="permission-resolver"]').forEach(w => {
      const selects = Array.from(w.querySelectorAll(".cw-select"));
      const verdict = w.querySelector("[data-verdict]");
      const why = w.querySelector("[data-why]");
      function setLayer(layer, val) {
        const s = selects.find(x => x.dataset.layer === layer);
        if (s) s.value = val;
      }
      function compute() {
        const vals = {};
        selects.forEach(s => { vals[s.dataset.layer] = s.value; });
        const denies = ORDER.filter(k => vals[k] === "deny");
        const asks = ORDER.filter(k => vals[k] === "ask");
        const allows = ORDER.filter(k => vals[k] === "allow");
        let v, text;
        if (denies.length) {
          v = "deny";
          text = LAYER_NAME[denies[0]] + " denies — a deny in any layer blocks the action, and no other layer can override it down.";
        } else if (asks.length) {
          v = "ask";
          text = LAYER_NAME[asks[0]] + " asks — with no deny anywhere, ask beats allow, so you get prompted.";
        } else if (allows.length) {
          v = "allow";
          text = allows.map(k => LAYER_NAME[k]).join(" + ") + " allow and nothing denies or asks — it runs without prompting.";
        } else {
          v = "none";
          text = "No layer sets a rule — Claude Code falls back to its default behavior.";
        }
        verdict.textContent = v === "none" ? "no rule" : v.toUpperCase();
        verdict.dataset.v = v;
        why.textContent = text;
      }
      /* open on the classic gotcha: a User allow that a Project deny overrides */
      setLayer("user", "allow");
      setLayer("project", "deny");
      selects.forEach(s => s.addEventListener("change", compute));
      compute();
    });
  })();

  /* ── Learn tab: clickable diagram nodes (node_links → deep-link) ────── */
  (function initConceptNodeLinks() {
    const data = document.getElementById("concepts-data");
    if (!data) return;
    let reg;
    try { reg = JSON.parse(data.textContent); } catch (e) { return; }
    (reg.concepts || []).forEach(c => {
      const links = c.node_links || {};
      if (!Object.keys(links).length) return;
      const card = document.getElementById("learn-" + c.id);
      const svg = card && card.querySelector(".concept-diagram-well svg");
      if (!svg) return;
      Object.keys(links).forEach(nodeId => {
        const target = links[nodeId];
        // node group ids are namespaced per-SVG: c-<concept>-flowchart-<NodeId>-<n>
        const node = svg.querySelector('[id*="-flowchart-' + nodeId + '-"]');
        if (!node) return;
        node.classList.add("rc-node-link");
        node.setAttribute("role", "link");
        node.setAttribute("tabindex", "0");
        node.setAttribute("aria-label", "Open concept: " + target);
        const go = () => { location.hash = "/learn/" + target; };
        node.addEventListener("click", go);
        node.addEventListener("keydown", e => {
          if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); }
        });
      });
    });
  })();

  /* Initial render */
  render();
})();
""".strip()


# Raven Power brand mark — the real raven-mark-dark.png from the
# RavenPower-Website repo (same asset the site nav uses), inlined as a
# base64 data URI so the static dashboard stays offline-safe / self-contained.
_RAVEN_MARK_DATA_URI = "data:image/png;base64,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"

# ──────────────────────────────────────────────────────────────────────────
# Plugins category — one page per plugin: editable variables (portal → repo
# file via /__read + /__save), plus that plugin's best-practices, decision
# trees, agents and skills. Variables are CURATED (typed, grounded knobs) PLUS
# a FREE-FORM key/value section for arbitrary project variables. Each plugin's
# values persist to .ravenclaude/plugins/<plugin>.yaml (whitelisted in
# scripts/serve-dashboards.py); the static/published dashboard falls back to
# localStorage + Download, exactly like the Settings tab.
# ──────────────────────────────────────────────────────────────────────────

# Universal knob for every plugin that ships an advisory hook (13 of 16). Maps
# to the hook's advisory(exit 0)/blocking(exit 1) toggle + its STRICT env var.
_PLUGINS_WITH_HOOK = {
    "applied-statistics", "azure-cloud", "claude-app-engineering", "data-platform",
    "edtech-partner-success", "finance", "microsoft-365-copilot", "microsoft-fabric",
    "power-platform", "ravenclaude-core", "regulatory-compliance", "salesforce",
    "web-design",
}
_HOOK_ENFORCEMENT_VAR = {
    "key": "hook_enforcement",
    "label": "Hook enforcement",
    "type": "enum",
    "options": ["advisory", "blocking"],
    "default": "advisory",
    "help": "advisory = warn on stderr, never block (exit 0); blocking = fail the edit on a violation (exit 1, the STRICT env var).",
}

# Plugin-specific curated knobs, grounded in each plugin's CLAUDE.md house
# opinions. The free-form section covers everything not enumerated here.
_PLUGIN_CURATED_VARS: dict[str, list[dict]] = {
    "power-platform": [
        {"key": "publisher_prefix", "label": "Publisher prefix", "type": "text", "default": "rvn_",
         "help": "House opinion #5 — a prefix you control (not the default cr_) so customizations are traceable."},
        {"key": "default_environment_url", "label": "Default environment URL", "type": "text", "default": "",
         "help": "Environment-variable discipline (#2) — never hard-code; set the engagement's default here."},
        {"key": "dataverse_mcp_org_url", "label": "Dataverse MCP org URL", "type": "text", "default": "",
         "help": "Per-tenant org URL for the official Dataverse MCP (CLAUDE.md §9a). e.g. https://contoso.crm.dynamics.com"},
        {"key": "pbix_mcp_enabled", "label": "pbix-mcp enabled", "type": "enum", "options": ["no", "yes"], "default": "no",
         "help": "Whether the bundled Power BI pbix-mcp server is wired (requires pip install pbix-mcp)."},
    ],
    "microsoft-fabric": [
        {"key": "default_capacity_sku", "label": "Default capacity SKU", "type": "text", "default": "F2",
         "help": "Size to average + smoothing (house opinion #5); record the engagement's default capacity."},
        {"key": "direct_lake_mode_default", "label": "Direct Lake mode", "type": "enum",
         "options": ["on-onelake", "on-sql"], "default": "on-onelake",
         "help": "House opinion #8 — on-OneLake has NO DirectQuery fallback; on-SQL falls back. Name it."},
    ],
    "data-platform": [
        {"key": "default_case", "label": "Default engagement Case", "type": "enum",
         "options": ["A", "B", "C", "D", "not-yet-determined"], "default": "not-yet-determined",
         "help": "The stack-selection Case (A/B/C/D) this engagement fits."},
        {"key": "jwt_ttl_minutes", "label": "Embed JWT TTL (minutes)", "type": "number", "default": "15",
         "help": "House opinion #4 — embed tokens are short-lived (5–15 min)."},
    ],
    "finance": [
        {"key": "materiality_threshold", "label": "Materiality threshold", "type": "text", "default": "$50K or 5%",
         "help": "House opinion #5 — materiality is a design constraint; document the threshold."},
        {"key": "confidentiality_default", "label": "Confidentiality default", "type": "enum",
         "options": ["internal", "client-confidential", "privileged"], "default": "internal",
         "help": "House opinion #10 — finance data is sensitive; set the default handling class."},
    ],
    "regulatory-compliance": [
        {"key": "default_jurisdiction", "label": "Default jurisdiction / regime", "type": "text", "default": "",
         "help": "House opinion #12 — name the regulator + regime so the same word isn't read across regimes."},
    ],
    "claude-app-engineering": [
        {"key": "default_model_tier", "label": "Default model tier", "type": "enum",
         "options": ["fast", "balanced", "frontier"], "default": "balanced",
         "help": "House opinion #3 — right-size by cost-per-resolved-task; the everyday default tier."},
    ],
    "microsoft-graph": [
        {"key": "default_cloud", "label": "Default cloud", "type": "enum",
         "options": ["global", "gcc", "gcc-high", "dod"], "default": "global",
         "help": "The Microsoft national cloud the engagement targets (endpoints differ)."},
        {"key": "use_immutable_ids", "label": "Use immutable IDs", "type": "enum",
         "options": ["yes", "no"], "default": "yes",
         "help": "Store immutable IDs for stored references (the immutable-ids best-practice)."},
    ],
    "salesforce": [
        {"key": "default_api_version", "label": "Default API version", "type": "text", "default": "",
         "help": "The Salesforce API version this org/engagement pins (e.g. v62.0)."},
    ],
    "applied-statistics": [
        {"key": "default_alpha", "label": "Default significance level (α)", "type": "number", "default": "0.05",
         "help": "The default α for hypothesis tests; document deviations."},
        {"key": "multiple_comparison_default", "label": "Multiple-comparison correction", "type": "enum",
         "options": ["none", "bonferroni", "benjamini-hochberg"], "default": "none",
         "help": "Default family-wise / FDR correction when running many tests."},
    ],
    "edtech-partner-success": [
        {"key": "health_red_threshold", "label": "Account-health RED threshold", "type": "number", "default": "",
         "help": "The score below which an account is RED in the health model."},
    ],
    "ravenclaude-core": [
        {"key": "decision_review_mode", "label": "Decision review (the Thing)", "type": "enum",
         "options": ["off", "advisory", "binding"], "default": "off",
         "help": "Canonical config is .ravenclaude/comfort-posture.yaml (Settings tab). Mirrored here for visibility."},
    ],
}


def _plugin_curated_vars(name: str) -> list[dict]:
    """Curated, typed knobs for a plugin: the universal hook_enforcement (when the
    plugin ships a hook) followed by its plugin-specific knobs."""
    out: list[dict] = []
    if name in _PLUGINS_WITH_HOOK:
        out.append(_HOOK_ENFORCEMENT_VAR)
    out.extend(_PLUGIN_CURATED_VARS.get(name, []))
    return out


def _gather_plugin_best_practices(plugin_dir: Path) -> list[str]:
    """Best-practice rule slugs for a plugin (filenames minus README/_TEMPLATE)."""
    bp_dir = plugin_dir / "best-practices"
    if not bp_dir.is_dir():
        return []
    out = []
    for f in sorted(bp_dir.glob("*.md")):
        if f.stem.lower() in {"readme", "_template"}:
            continue
        out.append(f.stem)
    return out


def _gather_plugin_trees(plugin_dir: Path) -> list[str]:
    """Decision-tree titles for a plugin (the `## Decision Tree:` headers in
    knowledge/*.md)."""
    kn = plugin_dir / "knowledge"
    if not kn.is_dir():
        return []
    titles: list[str] = []
    for f in sorted(kn.glob("*.md")):
        try:
            for line in f.read_text(encoding="utf-8").splitlines():
                s = line.strip()
                if s.startswith("## Decision Tree"):
                    t = s.lstrip("#").strip()
                    if t.lower().startswith("decision tree:"):
                        t = t[len("decision tree:"):].strip()
                    titles.append(t)
        except OSError:
            continue
    return titles


def _gather_plugin_dir_names(plugin_dir: Path, sub: str, dirs: bool = False) -> list[str]:
    base = plugin_dir / sub
    if not base.is_dir():
        return []
    if dirs:
        return sorted(p.name for p in base.iterdir() if p.is_dir())
    return sorted(p.stem for p in base.glob("*.md") if p.stem.lower() != "readme")


def _render_plugin_var_control(plugin: str, var: dict) -> str:
    """One curated-variable control (enum→select, number/text→input) carrying the
    data-* attributes the editor JS reads on save."""
    key = var["key"]
    label = html.escape(var["label"])
    help_txt = html.escape(var.get("help", ""))
    default = html.escape(str(var.get("default", "")))
    vtype = var["type"]
    cid = f"pv-{plugin}-{key}"
    if vtype == "enum":
        opts = "".join(
            f'<option value="{html.escape(o)}"{" selected" if o == var.get("default") else ""}>{html.escape(o)}</option>'
            for o in var.get("options", [])
        )
        control = (
            f'<select id="{cid}" class="pv-control" data-pvar="{html.escape(key)}" '
            f'data-ptype="enum" data-pdefault="{default}">{opts}</select>'
        )
    else:
        input_type = "number" if vtype == "number" else "text"
        control = (
            f'<input id="{cid}" class="pv-control" type="{input_type}" '
            f'data-pvar="{html.escape(key)}" data-ptype="{html.escape(vtype)}" '
            f'data-pdefault="{default}" value="{default}">'
        )
    return (
        '<div class="pv-row">'
        f'<label class="pv-label" for="{cid}">{label}</label>'
        f'{control}'
        f'<p class="pv-help">{help_txt}</p>'
        "</div>"
    )


def _render_plugin_page(plugin_dir: Path) -> str:
    """The full panel for one plugin: editable variables (curated + free-form)
    wired to the /__save portal, plus best-practices, decision trees, agents and
    skills for that plugin."""
    name = plugin_dir.name
    esc = html.escape(name)
    curated = _plugin_curated_vars(name)
    target = f".ravenclaude/plugins/{name}.yaml"

    controls = "".join(_render_plugin_var_control(name, v) for v in curated) or (
        '<p class="pv-help">No curated knobs for this plugin yet — use the free-form section below.</p>'
    )

    bps = _gather_plugin_best_practices(plugin_dir)
    trees = _gather_plugin_trees(plugin_dir)
    agents = _gather_plugin_dir_names(plugin_dir, "agents")
    skills = _gather_plugin_dir_names(plugin_dir, "skills", dirs=True)

    def _li_list(items: list[str], empty: str) -> str:
        if not items:
            return f'<p class="pp-empty">{empty}</p>'
        return '<ul class="pp-list">' + "".join(f"<li>{html.escape(i)}</li>" for i in items) + "</ul>"

    bp_html = _li_list(bps, "No best-practice docs in this plugin.")
    tree_html = _li_list(trees, "No decision trees in this plugin.")
    agents_html = _li_list(agents, "No agents in this plugin.")
    skills_html = _li_list(skills, "No skills in this plugin.")

    return f"""
    <div class="plugin-page" data-plugin="{esc}" data-target="{html.escape(target)}">
      <h2 class="pp-title">{esc}</h2>
      <p class="pp-sub">Variables for <code>{esc}</code> save to <code>{html.escape(target)}</code> via the dashboard server. On the static/published copy, edits stay in your browser — use <strong>Download</strong>.</p>

      <section class="pp-section">
        <h3>Variables</h3>
        <div class="pv-curated">{controls}</div>
        <div class="pv-freeform">
          <h4>Free-form variables</h4>
          <p class="pv-help">One <code>key: value</code> per line (YAML). For project variables not covered by the curated knobs above.</p>
          <textarea class="pv-extra" data-plugin="{esc}" rows="5" spellcheck="false" placeholder="my_key: my value&#10;another_key: 123"></textarea>
        </div>
        <div class="pp-actions">
          <button type="button" class="pp-save" data-plugin="{esc}">Save to repo</button>
          <button type="button" class="pp-download" data-plugin="{esc}">Download .yaml</button>
          <span class="pp-status" data-plugin="{esc}" role="status"></span>
        </div>
        <p class="pp-noserver" data-plugin="{esc}" hidden>No local dashboard server behind this page, so <strong>Save to repo</strong> is off. Run <code>ravenclaude dashboard</code> (or <code>bash .ravenclaude/dashboard.sh</code>) and reopen, or use <strong>Download</strong> and drop the file into <code>{html.escape(target)}</code>.</p>
      </section>

      <section class="pp-section">
        <h3>Best practices <span class="pp-count">{len(bps)}</span></h3>
        {bp_html}
      </section>
      <section class="pp-section">
        <h3>Decision trees <span class="pp-count">{len(trees)}</span></h3>
        {tree_html}
      </section>
      <section class="pp-section pp-cols">
        <div><h3>Agents <span class="pp-count">{len(agents)}</span></h3>{agents_html}</div>
        <div><h3>Skills <span class="pp-count">{len(skills)}</span></h3>{skills_html}</div>
      </section>
    </div>
    """


def _render_plugins_category(plugin_dirs: list[Path]) -> tuple[str, str]:
    """Return (tabs_html, panels_html) for the Plugins category — one tab-btn and
    one tab-panel per plugin, matching the existing two-tier nav contract."""
    tabs: list[str] = []
    panels: list[str] = []
    for pd in plugin_dirs:
        name = pd.name
        esc = html.escape(name)
        tab_id = f"plugin-{name}"
        tabs.append(
            f'<button class="tab-btn" id="tab-{html.escape(tab_id)}" data-tab="{html.escape(tab_id)}" '
            f'data-cat="plugins" role="tab" aria-selected="false" tabindex="-1" '
            f'aria-controls="panel-{html.escape(tab_id)}" title="{esc} — variables, best practices, trees">{esc}</button>'
        )
        panels.append(
            f'<section class="tab-panel" id="panel-{html.escape(tab_id)}" data-tab="{html.escape(tab_id)}" '
            f'role="tabpanel" aria-label="{esc} plugin">{_render_plugin_page(pd)}</section>'
        )
    return "\n".join(tabs), "\n".join(panels)


def _all_plugin_dirs() -> list[Path]:
    """Every plugin directory (has .claude-plugin/plugin.json), sorted by name."""
    return sorted(
        (p for p in (REPO_ROOT / "plugins").iterdir()
         if (p / ".claude-plugin" / "plugin.json").is_file()),
        key=lambda p: p.name,
    )


def _render_web_access_page() -> str:
    """The 'Web access' page (Set up category): edit the website allow/deny lists
    that guard-web-access.sh enforces, persisted to .ravenclaude/web-access.yaml
    via the /__save portal (localStorage + Download fallback on a static host)."""
    target = ".ravenclaude/web-access.yaml"
    t = html.escape(target)
    return f"""
    <div class="web-access-page" data-target="{t}">
      <h2 class="pp-title">Web access — allow &amp; deny lists</h2>
      <p class="pp-sub">Domains the agent may fetch <strong>without asking</strong> (allow) or <strong>never</strong> (deny). Saves to <code>{t}</code> via the dashboard server; the <code>guard-web-access.sh</code> hook enforces it for Claude when the plugin is installed, and any cloned CLI tool can read the same plain-YAML file. On the static/published copy edits stay in your browser — use <strong>Download</strong>. One domain per line; a rule matches the domain <em>and</em> its subdomains (e.g. <code>github.com</code> also allows <code>api.github.com</code>). Unlisted domains fall through to the agent's once / this-session / permanently / deny prompt.</p>
      <section class="pp-section">
        <h3>Allow <span class="pp-count">auto-approved</span></h3>
        <textarea class="wa-allow pv-extra" rows="6" spellcheck="false" placeholder="github.com&#10;docs.anthropic.com"></textarea>
      </section>
      <section class="pp-section">
        <h3>Deny <span class="pp-count">always blocked</span></h3>
        <textarea class="wa-deny pv-extra" rows="6" spellcheck="false" placeholder="ads.example.com"></textarea>
      </section>
      <div class="pp-actions">
        <button type="button" class="wa-save pp-save">Save to repo</button>
        <button type="button" class="wa-download pp-download">Download .yaml</button>
        <span class="wa-status pp-status" role="status"></span>
      </div>
      <p class="pp-noserver wa-noserver" hidden>No local dashboard server behind this page, so <strong>Save to repo</strong> is off. Run <code>ravenclaude dashboard</code> (or <code>bash .ravenclaude/dashboard.sh</code>) and reopen, or use <strong>Download</strong> and drop the file into <code>{t}</code>.</p>
    </div>
    """


_PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<!-- Raven Power brand fonts. Loads when online; falls back to system-ui offline (the
     --font-sans / --font-display stacks already degrade gracefully). -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap">
<style>
{css}
</style>
</head>
<body>

<header class="page-header">
  <div class="brand-row">
    <span class="brand-mark" aria-hidden="true">{raven_mark}</span>
    <h1>{title}</h1>
  </div>
  <p class="page-desc">This is your control panel for Claude&nbsp;Code's safety rails. Use it to set what Claude is allowed to do, see what it's been doing, and add plugins. <a href="#/about" class="header-about-link">What is this?</a></p>
  <nav class="cat-bar" aria-label="Dashboard categories">
    <button class="cat-btn" type="button" data-cat="setup" aria-pressed="true" title="Set up — Overview, permissions, the safety pipeline, and a review preview">Set up</button>
    <button class="cat-btn" type="button" data-cat="lookback" aria-pressed="false" title="Look back — review log, run feed, perimeter alerts, security log, lineage">Look back</button>
    <button class="cat-btn" type="button" data-cat="learn" aria-pressed="false" title="Learn — explainers, command playbooks, decision-tree guidance">Learn</button>
    <button class="cat-btn" type="button" data-cat="plugins" aria-pressed="false" title="Plugins — per-plugin variables, best practices, and decision trees">Plugins</button>
    <button class="cat-btn" type="button" data-cat="install" aria-pressed="false" title="Install &amp; help — install &amp; update RavenClaude in Claude Code or GitHub Copilot CLI, plus help">Install &amp; help</button>
  </nav>
  <nav class="tab-bar" role="tablist" aria-label="Pages in the selected category">
    <button class="tab-btn in-cat" id="tab-overview" data-tab="overview" data-cat="setup" role="tab" aria-selected="true" aria-controls="panel-overview" title="Overview — start here: what this dashboard is for">Overview</button>
    <button class="tab-btn in-cat" id="tab-settings" data-tab="settings" data-cat="setup" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-settings" title="Settings — choose what Claude can do on its own (deny / ask / allow)">Settings</button>
    <button class="tab-btn in-cat" id="tab-pipeline" data-tab="pipeline" data-cat="setup" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-pipeline" title="Pipeline — the safety checks every command passes through">Pipeline</button>
    <button class="tab-btn in-cat" id="tab-simulator" data-tab="simulator" data-cat="setup" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-simulator" title="Preview a review — see how a command would be judged before you run it">Preview a review</button>
    <button class="tab-btn in-cat" id="tab-web-access" data-tab="web-access" data-cat="setup" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-web-access" title="Web access — allow/deny which websites the agent may fetch">Web access</button>
    <button class="tab-btn" id="tab-saga" data-tab="saga" data-cat="lookback" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-saga" title="Review log — past decisions the reviewer panel made (Sága)">&#9878; Review log</button>
    <button class="tab-btn" id="tab-activity" data-tab="activity" data-cat="lookback" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-activity" title="Run feed — what Claude is doing right now: runs &amp; worktrees (Sleipnir)">Run feed</button>
    <button class="tab-btn" id="tab-heimdall" data-tab="heimdall" data-cat="lookback" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-heimdall" title="Perimeter alerts — what your guardrails caught at the edge (Heimdall)">Perimeter alerts</button>
    <button class="tab-btn" id="tab-vidarr" data-tab="vidarr" data-cat="lookback" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-vidarr" title="Security log — a record of your permission changes (Víðarr)">Security log</button>
    <button class="tab-btn" id="tab-norns" data-tab="norns" data-cat="lookback" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-norns" title="Lineage — how your plugins connect and depend on each other (Norns)">Lineage</button>
    <button class="tab-btn" id="tab-mimir" data-tab="mimir" data-cat="lookback" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-mimir" title="Session — what Claude Code knows about this session (M&iacute;mir's well)">Session</button>
    <button class="tab-btn" id="tab-learn" data-tab="learn" data-cat="learn" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-learn" title="Learn — plain-English explainers for each concept">Learn</button>
    <button class="tab-btn" id="tab-commands" data-tab="commands" data-cat="learn" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-commands" title="Commands — ready-to-run slash-command playbooks">Commands</button>
    <button class="tab-btn" id="tab-trees" data-tab="trees" data-cat="learn" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-trees" title="Guidance — decision trees and best practices">Guidance</button>
    <button class="tab-btn" id="tab-bifrost" data-tab="bifrost" data-cat="install" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-bifrost" title="Claude Code — install &amp; update a plugin in Claude Code (the Bifröst bridge)">Claude&nbsp;Code</button>
    <button class="tab-btn" id="tab-install" data-tab="install" data-cat="install" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-install" title="Copilot CLI — install &amp; update RavenClaude in GitHub Copilot CLI">Copilot&nbsp;CLI</button>
    <button class="tab-btn" id="tab-about" data-tab="about" data-cat="install" role="tab" aria-selected="false" tabindex="-1" aria-controls="panel-about" title="About &amp; help — what this dashboard is and how it's organized">About &amp; help</button>
{plugins_tabs}
  </nav>
</header>

<main>
  <section class="tab-panel active" id="panel-overview" data-tab="overview" role="tabpanel" aria-label="Overview">
{overview_html}
  </section>
  <section class="tab-panel" id="panel-settings" data-tab="settings" role="tabpanel" aria-label="Settings">
{settings_html}
  </section>
  <section class="tab-panel" id="panel-pipeline" data-tab="pipeline" role="tabpanel" aria-label="Guardrail pipeline">
{pipeline_html}
  </section>
  <section class="tab-panel" id="panel-install" data-tab="install" role="tabpanel" aria-label="Install and Update">
{install_html}
  </section>
  <section class="tab-panel" id="panel-simulator" data-tab="simulator" role="tabpanel" aria-label="Preview a command's review">
{simulator_html}
  </section>
  <section class="tab-panel" id="panel-web-access" data-tab="web-access" role="tabpanel" aria-label="Web access allow and deny lists">
{web_access_html}
  </section>
  <section class="tab-panel" id="panel-learn" data-tab="learn" role="tabpanel" aria-label="Learn">
{learn_html}
  </section>
  <section class="tab-panel" id="panel-saga" data-tab="saga" role="tabpanel" aria-label="Review log">
{saga_html}
  </section>
  <section class="tab-panel" id="panel-commands" data-tab="commands" role="tabpanel" aria-label="Commands">
{commands_html}
  </section>
  <section class="tab-panel" id="panel-trees" data-tab="trees" role="tabpanel" aria-label="Decision trees and best practices">
{trees_html}
  </section>
  <section class="tab-panel" id="panel-activity" data-tab="activity" role="tabpanel" aria-label="Run feed">
{activity_html}
  </section>
  <section class="tab-panel" id="panel-heimdall" data-tab="heimdall" role="tabpanel" aria-label="Perimeter alerts">
{heimdall_html}
  </section>
  <section class="tab-panel" id="panel-vidarr" data-tab="vidarr" role="tabpanel" aria-label="Security log">
{vidarr_html}
  </section>
  <section class="tab-panel" id="panel-norns" data-tab="norns" role="tabpanel" aria-label="Plugin lineage">
{norns_html}
  </section>
  <section class="tab-panel" id="panel-mimir" data-tab="mimir" role="tabpanel" aria-label="Session state">
{mimir_html}
  </section>
  <section class="tab-panel" id="panel-bifrost" data-tab="bifrost" role="tabpanel" aria-label="Add plugin">
{bifrost_html}
  </section>
  <section class="tab-panel" id="panel-about" data-tab="about" role="tabpanel" aria-label="About and help">
{about_html}
  </section>
{plugins_panels}
</main>

<div class="modal-backdrop" id="info-modal" role="dialog" aria-modal="true" aria-labelledby="info-modal-title" tabindex="-1">
  <div class="modal">
    <button type="button" class="close-btn" id="info-modal-close" aria-label="Close">&times;</button>
    <h2 id="info-modal-title">Setting</h2>
    <p class="modal-subhead" id="info-modal-desc"></p>
    <h3>What this controls</h3>
    <p id="info-modal-controls"></p>
    <h3>Examples</h3>
    <ul id="info-modal-examples" class="example-list"></ul>
    <h3>Recommended level</h3>
    <div class="rec-rows">
      <div class="rec-row">
        <span class="rec-context">Working as an individual</span>
        <span class="rec-text" id="info-modal-rec-individual"></span>
      </div>
      <div class="rec-row">
        <span class="rec-context">Working as a team</span>
        <span class="rec-text" id="info-modal-rec-team"></span>
      </div>
    </div>
    <h3>When to relax or tighten</h3>
    <p id="info-modal-guidance"></p>
  </div>
</div>

<div class="modal-backdrop" id="pattern-modal" role="dialog" aria-modal="true" aria-labelledby="pattern-modal-title" tabindex="-1">
  <div class="modal pattern-modal">
    <button type="button" class="close-btn" id="pattern-modal-close" aria-label="Close">&times;</button>
    <h2 id="pattern-modal-title">Pattern</h2>
    <h3>What this is</h3>
    <p id="pattern-modal-what"></p>
    <h3>Why it's here</h3>
    <p id="pattern-modal-why"></p>
  </div>
</div>

<div class="modal-backdrop" id="layers-modal" role="dialog" aria-modal="true" aria-labelledby="layers-modal-title" tabindex="-1">
  <div class="modal layers-modal">
    <button type="button" class="close-btn" id="layers-modal-close" aria-label="Close">&times;</button>
    <h2 id="layers-modal-title">How layers merge</h2>
    <p style="font-size:13px;color:var(--muted);margin:0 0 16px">Claude Code reads three settings files and merges them at runtime. The strictest rule across all three always wins &mdash; a personal &ldquo;allow&rdquo; cannot loosen a team &ldquo;ask&rdquo; or &ldquo;deny&rdquo;.</p>
    <div class="layer-file-row">
      <span class="layer-file-label">User</span>
      <span class="layer-file-desc"><code>~/.claude/settings.json</code> &mdash; applies to every project on your machine. Only you see it; it is never committed to git. Use it for personal preferences that apply everywhere.</span>
    </div>
    <div class="layer-file-row">
      <span class="layer-file-label">Local</span>
      <span class="layer-file-desc"><code>.claude/settings.local.json</code> &mdash; project-specific but gitignored. Stays on your machine. Use it for project-level tweaks you do not want to share with teammates.</span>
    </div>
    <div class="layer-file-row">
      <span class="layer-file-label">Project</span>
      <span class="layer-file-desc"><code>.claude/settings.json</code> &mdash; committed to the repo and shared with the whole team. Whatever you set here becomes the team baseline. A personal &ldquo;allow&rdquo; at User or Local cannot soften it.</span>
    </div>
    <h3 style="margin-top:20px">Merge rule</h3>
    <p style="font-size:13px;line-height:1.55"><strong>deny &gt; ask &gt; allow.</strong> For any permission pattern, Claude Code takes the strictest bucket it finds across all three files. Setting &ldquo;inherit&rdquo; at a layer means that layer emits no rule &mdash; Claude Code falls back to its built-in default for that pattern.</p>
    <h3>Dashboard convention</h3>
    <p style="font-size:13px;line-height:1.55">Presets set the <strong>Local</strong> layer &mdash; your personal default for this project. The <strong>User</strong> layer is for cross-project preferences; the <strong>Project</strong> layer is for team-wide policy. Rows set to &ldquo;inherit&rdquo; are omitted from the emitted YAML.</p>
  </div>
</div>

<footer class="page-footer">
  Generated by <code>scripts/generate-dashboards.py</code>.
  Source schema: <code>plugins/{plugin_name}/dashboard-schema.json</code>.
  Design: <a href="https://github.com/mcorbett51090/RavenClaude/blob/main/docs/proposals/2026-05-22-003-per-plugin-dashboard.md">proposal 003</a>.
</footer>

<script type="application/json" id="schema-data">
{schema_json}
</script>
<script type="application/json" id="pattern-explanations-data">
{pattern_explanations_json}
</script>
<script type="application/json" id="concepts-data">
{concepts_json}
</script>
<script type="application/json" id="heimdall-data">
{heimdall_json}
</script>
<script>
{js}
</script>
</body>
</html>
"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--plugin", help="Generate one plugin's dashboard only (e.g. 'ravenclaude-core').")
    p.add_argument("--check", action="store_true", help="Exit 1 if any dashboard.html is stale vs its schema.")
    args = p.parse_args()

    if args.plugin:
        target = PLUGINS_DIR / args.plugin
        if not (target / "dashboard-schema.json").is_file():
            print(f"ERROR: {target}/dashboard-schema.json not found", file=sys.stderr)
            return 1
        plugins = [target]
    else:
        plugins = find_plugins_with_schema()

    if not plugins:
        print("No plugins with dashboard-schema.json found. Nothing to do.")
        return 0

    exit_code = 0
    for plugin_dir in plugins:
        schema = load_schema(plugin_dir)
        new_html = render_dashboard(plugin_dir, schema)
        out_path = plugin_dir / "dashboard.html"

        if args.check:
            existing = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
            if existing != new_html:
                print(f"STALE: {out_path}", file=sys.stderr)
                exit_code = 1
            else:
                print(f"fresh: {out_path}")
        else:
            out_path.write_text(new_html, encoding="utf-8", newline="\n")
            print(f"wrote {out_path} ({len(new_html):,} bytes)")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
