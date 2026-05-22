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
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"


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

    return _PAGE_TEMPLATE.format(
        plugin_name=html.escape(plugin_name),
        title=html.escape(title),
        description=html.escape(description),
        css=_CSS,
        settings_html=_render_settings_tab(properties, presets),
        commands_html=_render_stub_tab("Commands", "v0.2.0"),
        trees_html=_render_stub_tab("Decision trees", "v0.2.0"),
        activity_html=_render_stub_tab("Activity", "v0.2.0"),
        schema_json=json.dumps(schema, indent=2),
        pattern_explanations_json=json.dumps(
            PATTERN_EXPLANATIONS, indent=2, sort_keys=True
        ),
        js=_JS,
    )


def _render_stub_tab(name: str, when: str) -> str:
    return (
        f'<div class="stub">'
        f'<h2>{html.escape(name)} tab</h2>'
        f'<p>Ships in <strong>{html.escape(when)}</strong>. '
        f'See <code>docs/proposals/2026-05-22-003-per-plugin-dashboard.md</code> for the design.</p>'
        f"</div>"
    )


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

    # Global default segmented control
    global_default_html = _render_segmented(
        "global_default",
        properties.get("global_default", {}),
        "global-default",
    )

    # Per-category controls, grouped
    categories_props = properties.get("categories", {}).get("properties", {})
    groups: dict[str, list[tuple[str, dict]]] = {}
    for cat_name in sorted(categories_props.keys()):
        cat_schema = categories_props[cat_name]
        group = cat_schema.get("x-group", "Other")
        groups.setdefault(group, []).append((cat_name, cat_schema))

    group_html_parts: list[str] = []
    for group_name in sorted(groups.keys()):
        row_blocks: list[str] = []
        for name, sch in groups[group_name]:
            row_blocks.append(
                _render_segmented(name, sch, f"cat-{name}", group=group_name)
            )
            patterns = EMISSIONS.get(name, [])
            if patterns:
                row_blocks.append(_render_pattern_details(name, patterns))
        group_html_parts.append(
            f'<fieldset class="cat-group"><legend>{html.escape(group_name)}</legend>'
            + "".join(row_blocks)
            + "</fieldset>"
        )

    security_deny_html = _render_security_deny(
        properties.get("security_deny", {})
    )

    return _SETTINGS_TAB_TEMPLATE.format(
        preset_buttons="".join(preset_buttons),
        global_default=global_default_html,
        category_groups="".join(group_html_parts),
        security_deny=security_deny_html,
    )


def _render_pattern_details(category: str, patterns: list[str]) -> str:
    """Render a collapsible <details> block with per-pattern level controls.

    Each pattern row contains: pattern name (mono code) + info button (mirrors
    the category-row title-+-info-button layout), one-line `what` detail, and
    a styled <select> dropdown with six options — "Use category default"
    (selected initially; clears the override) plus the five level enums.
    """
    select_options = [
        ("__default", "Use category default"),
        ("deny", "Deny"),
        ("always-ask", "Always Ask"),
        ("mostly-ask", "Mostly Ask"),
        ("mostly-allow", "Mostly Allow"),
        ("autopilot", "Autopilot"),
    ]
    rows: list[str] = []
    for pattern in patterns:
        explanation = PATTERN_EXPLANATIONS.get(pattern, {})
        what_text = explanation.get("what", "")
        info_btn = (
            f'<button type="button" class="info-btn info-btn-pattern" '
            f'data-info-pattern="{html.escape(pattern)}" '
            f'aria-label="Explain {html.escape(pattern)}" '
            f'title="Explain this pattern">?</button>'
            if explanation else ""
        )
        options_html = "".join(
            f'<option value="{html.escape(v)}"{" selected" if v == "__default" else ""}>'
            f'{html.escape(label)}</option>'
            for v, label in select_options
        )
        rows.append(
            f'<div class="pattern-row" data-pattern="{html.escape(pattern)}">'
            f'<div class="pattern-meta">'
            f'<code class="pattern-name" title="{html.escape(pattern)}">'
            f'{html.escape(pattern)}</code>'
            f'{info_btn}'
            f"</div>"
            f'<span class="pattern-detail">{html.escape(what_text)}</span>'
            f'<select class="pattern-select" '
            f'data-pattern="{html.escape(pattern)}" '
            f'data-category="{html.escape(category)}" '
            f'data-current="__default" '
            f'aria-label="Level for {html.escape(pattern)}">'
            + options_html
            + "</select>"
            f"</div>"
        )
    return (
        f'<details class="pattern-details" data-category="{html.escape(category)}">'
        f'<summary class="pattern-summary">'
        f'<span class="pattern-summary-text">'
        f'Per-pattern overrides <span class="pattern-count">'
        f'({len(patterns)})</span></span>'
        f'<span class="pattern-override-count" data-for="{html.escape(category)}">'
        f'0 overridden</span>'
        f'</summary>'
        f'<div class="pattern-list">'
        + "".join(rows)
        + "</div>"
        f"</details>"
    )


def _render_security_deny(schema: dict) -> str:
    """Render the always-on security deny baseline as a checklist.

    Patterns are checked-by-default; unchecking a row removes the pattern
    from the YAML's security_deny list. Each row carries a one-line `what`
    detail and an info button that opens the per-pattern modal.

    The legend has its own info button that opens a section-level modal
    explaining what security_deny does and why.
    """
    defaults = schema.get("default", []) or []
    title = schema.get("title", "Always-on security deny rules")
    description = schema.get(
        "description",
        "Patterns that are ALWAYS denied regardless of category levels.",
    )
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
            f'<div class="sec-deny-row">'
            f'<input type="checkbox" id="{html.escape(cid)}" '
            f'class="sec-deny-checkbox" value="{html.escape(pattern)}" checked>'
            f'<div class="sec-deny-meta">'
            f'<label class="sec-deny-pattern-label" for="{html.escape(cid)}">'
            f'<code class="sec-deny-pattern">{html.escape(pattern)}</code>'
            f'</label>'
            f'{info_btn}'
            f"</div>"
            f'<span class="pattern-detail sec-deny-detail">{html.escape(what_text)}</span>'
            f"</div>"
        )
    return (
        f'<fieldset class="cat-group sec-deny-group">'
        f'<legend>Security baseline '
        f'<button type="button" class="info-btn info-btn-section" '
        f'data-info-section="security_deny" '
        f'aria-label="Explain the security baseline" '
        f'title="Explain the security baseline">?</button>'
        f'</legend>'
        f'<p class="sec-deny-desc">{html.escape(description)}</p>'
        f'<details class="pattern-details sec-deny-details" open>'
        f'<summary class="pattern-summary">'
        f'<span class="pattern-summary-text">{html.escape(title)} '
        f'<span class="pattern-count">({len(defaults)})</span></span>'
        f'<span class="pattern-override-count" id="sec-deny-active-count">'
        f'{len(defaults)} active</span>'
        f'</summary>'
        f'<div class="pattern-list sec-deny-list">'
        + "".join(rows)
        + "</div>"
        f"</details>"
        f"</fieldset>"
    )


def _label_for(value: str) -> str:
    """Render an enum value as a short pill label (Title Case, spaces not hyphens)."""
    return " ".join(part.capitalize() for part in value.replace("_", " ").split("-"))


def _render_segmented(name: str, schema: dict, id_prefix: str, group: str | None = None) -> str:
    """Render one segmented-radiogroup row from a schema property.

    Emits an info-icon button next to the title that the JS layer opens
    into a modal with the category's controls / examples / guidance.
    """
    title = schema.get("title", name)
    description = schema.get("description", "")
    enum_values = schema.get("enum", ["deny", "always-ask", "mostly-ask", "mostly-allow", "autopilot"])
    default_value = schema.get("default", enum_values[len(enum_values) // 2])
    has_modal_content = bool(schema.get("x-controls") or schema.get("x-examples") or schema.get("x-guidance"))
    group_attr = f' data-group="{html.escape(group)}"' if group else ""

    recommended_value = schema.get("x-recommended")
    radios = []
    for v in enum_values:
        rid = f"{id_prefix}-{v}"
        checked = "checked" if v == default_value else ""
        rec_marker = (
            f'<span class="rec-badge" aria-label="Recommended for this category">Recommended</span>'
            if v == recommended_value else ""
        )
        radios.append(
            f'<input type="radio" id="{html.escape(rid)}" name="{html.escape(name)}" '
            f'value="{html.escape(v)}" {checked}>'
            f'<label for="{html.escape(rid)}" class="seg-label seg-{html.escape(v)}" '
            f'title="{html.escape(v)}">'
            f"{html.escape(_label_for(v))}{rec_marker}</label>"
        )

    info_btn = (
        f'<button type="button" class="info-btn" data-info-for="{html.escape(name)}" '
        f'aria-label="Explain {html.escape(title)}" title="Explain this setting">?</button>'
        if has_modal_content else ""
    )

    return (
        f'<div class="cat-row" data-category="{html.escape(name)}"{group_attr}>'
        f'<div class="cat-meta">'
        f'<div class="cat-title-row"><span class="cat-title">{html.escape(title)}</span>{info_btn}</div>'
        f'<div class="cat-desc">{html.escape(description)}</div>'
        f"</div>"
        f'<div class="seg-control" role="radiogroup" aria-label="{html.escape(title)}">'
        + "".join(radios)
        + "</div>"
        f"</div>"
    )


# ── HTML, CSS, JS templates ──────────────────────────────────────────────
# Theme variables mirror repo-guide.html so the read-only catalog and the
# editable dashboard look like the same product family.

_CSS = """
:root {
  color-scheme: light dark;
  --bg: #0b1120;
  --surface: #111827;
  --surface-2: #1f2937;
  --border: #334155;
  --text: #f1f5f9;
  --muted: #94a3b8;
  --accent: #14b8a6;
  --accent-dim: #0d9488;
  --warn: #fbbf24;
  --danger: #ef4444;
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  --radius: 8px;
}
@media (prefers-color-scheme: light) {
  :root {
    --bg: #f8fafc;
    --surface: #ffffff;
    --surface-2: #e2e8f0;
    --border: #cbd5e1;
    --text: #0f172a;
    --muted: #475569;
    --accent: #0d9488;
    --accent-dim: #14b8a6;
  }
}
@media (prefers-reduced-motion: reduce) {
  * { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; }
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  font-size: 15px;
  line-height: 1.5;
  min-height: 100vh;
}
.page-header {
  padding: 24px 32px 0;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}
.page-header h1 {
  margin: 0 0 4px 0;
  font-size: 22px;
  letter-spacing: -0.01em;
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
}
.tab-btn {
  background: transparent;
  border: none;
  color: var(--muted);
  font: inherit;
  padding: 10px 16px;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-weight: 500;
}
.tab-btn[aria-selected="true"] {
  color: var(--text);
  border-bottom-color: var(--accent);
}
.tab-btn:hover { color: var(--text); }
.tab-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 4px; }
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
.preset-btn.preset-always-ask { border-left-color: var(--warn); }
.preset-btn.preset-mostly-ask { border-left-color: var(--accent); }
.preset-btn.preset-mostly-allow { border-left-color: var(--accent); }
.preset-btn.preset-autopilot { border-left-color: var(--warn); }
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
  margin: -10px 0 8px 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  overflow: hidden;
}
.pattern-summary {
  cursor: pointer;
  padding: 4px 8px;
  font-size: 11px;
  color: var(--muted);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  user-select: none;
  list-style: none;
  opacity: 0.75;
  transition: opacity 80ms ease, color 80ms ease;
}
.pattern-summary::-webkit-details-marker { display: none; }
.pattern-summary::before {
  content: "▸";
  color: var(--muted);
  font-size: 10px;
  display: inline-block;
  width: 10px;
  margin-right: 4px;
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
  padding: 4px 8px 8px;
  border-top: 1px dotted var(--border);
  background: var(--surface);
  border-radius: 4px;
}
/* Per-pattern row: 3 columns — [code + ? meta] [detail] [select] */
.pattern-row {
  display: grid;
  grid-template-columns: minmax(180px, 260px) 1fr auto;
  gap: 14px;
  padding: 7px 6px;
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

/* Per-pattern level dropdown (styled <select>) */
.pattern-select {
  background: var(--surface-2);
  color: var(--text);
  border: 1px solid var(--border);
  border-left-width: 3px;
  border-radius: 6px;
  padding: 5px 10px;
  font: inherit;
  font-size: 11.5px;
  cursor: pointer;
  min-width: 170px;
  appearance: none;
  -webkit-appearance: none;
  background-image: linear-gradient(45deg, transparent 50%, var(--muted) 50%),
                    linear-gradient(135deg, var(--muted) 50%, transparent 50%);
  background-position: calc(100% - 14px) 50%, calc(100% - 9px) 50%;
  background-size: 5px 5px, 5px 5px;
  background-repeat: no-repeat;
  padding-right: 26px;
  transition: border-color 80ms ease, background-color 80ms ease;
}
.pattern-select:hover { border-color: var(--accent); }
.pattern-select:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
/* Color-tinted left border by current selection */
.pattern-select[data-current="__default"] {
  border-left-color: var(--border);
  color: var(--muted);
  font-style: italic;
}
.pattern-select[data-current="deny"] { border-left-color: var(--danger); color: var(--danger); }
.pattern-select[data-current="always-ask"] { border-left-color: var(--warn); }
.pattern-select[data-current="mostly-ask"] { border-left-color: var(--accent); }
.pattern-select[data-current="mostly-allow"] { border-left-color: var(--accent); }
.pattern-select[data-current="autopilot"] { border-left-color: var(--warn); }
.pattern-select option { background: var(--surface); color: var(--text); }

/* Security-deny baseline block */
.sec-deny-group { border-left: 3px solid var(--danger); }
.sec-deny-group legend { color: var(--danger); }
.sec-deny-desc {
  font-size: 12px;
  color: var(--muted);
  margin: 4px 0 12px;
  max-width: 640px;
}
.sec-deny-list { max-height: 360px; }
.sec-deny-row {
  display: grid;
  grid-template-columns: auto minmax(200px, 260px) 1fr;
  align-items: center;
  gap: 10px;
  padding: 5px 0;
}
.sec-deny-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
.sec-deny-pattern-label { cursor: pointer; min-width: 0; overflow: hidden; }
.sec-deny-checkbox { accent-color: var(--danger); cursor: pointer; }
.sec-deny-pattern {
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--text);
  background: transparent;
  padding: 0;
}
.sec-deny-detail {
  font-size: 11.5px;
  color: var(--muted);
  line-height: 1.4;
}
@media (max-width: 1200px) {
  .sec-deny-detail { display: none; }
}
.sec-deny-row:has(.sec-deny-checkbox:not(:checked)) .sec-deny-pattern {
  text-decoration: line-through;
  color: var(--muted);
}
.sec-deny-row:has(.sec-deny-checkbox:not(:checked)) .sec-deny-detail {
  opacity: 0.5;
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
.yaml-status.status-saved { color: var(--accent); }
.yaml-status.status-error { color: var(--danger); }
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
""".strip()


_SETTINGS_TAB_TEMPLATE = """
<div class="settings-layout">
  <div class="settings-form">
    <div class="preset-bar">
      <h3>Apply a preset</h3>
      <p>Sets every category at once. You can still override individual rows below.</p>
      <div class="preset-buttons">{preset_buttons}</div>
    </div>

    <div class="global-default">
      {global_default}
    </div>

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
        <span class="btn-main">Save to repo</span>
        <span class="btn-sub" id="save-repo-target">.ravenclaude/comfort-posture.yaml</span>
      </button>
      <p class="primary-help" id="save-repo-help" hidden>
        Saves directly to <code>.ravenclaude/comfort-posture.yaml</code> in this repo. The agent reads from there.
      </p>
      <p class="primary-help muted" id="no-server-help" hidden>
        Save-to-repo needs the local server. Start it with <code>python3 scripts/serve-dashboards.py</code> and open the forwarded URL. Until then, the alternatives below work.
      </p>
    </div>
    <details class="yaml-alt-actions">
      <summary>Alternative ways to save</summary>
      <div class="yaml-actions">
        <button class="btn secondary" id="connect-btn" hidden>Auto-save to file…</button>
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


_JS = r"""
/* generate-dashboards.py output — Settings tab JS
 * Vanilla; no dependencies. Reads the inline JSON Schema at #schema-data,
 * watches form changes, emits live YAML preview + clipboard copy + download.
 */
(() => {
  const SCHEMA = JSON.parse(document.getElementById("schema-data").textContent);
  const presets = SCHEMA.presets || {};
  const props = SCHEMA.properties || {};
  const catProps = (props.categories && props.categories.properties) || {};
  /* Pattern explanations loaded from a sibling JSON block. Used by the
   * per-pattern modal opened from each pattern row's info button. */
  let PATTERN_EXPLANATIONS = {};
  try {
    const el = document.getElementById("pattern-explanations-data");
    PATTERN_EXPLANATIONS = el ? JSON.parse(el.textContent) : {};
  } catch (e) {
    console.error("Failed to parse pattern-explanations:", e);
  }
  /* Section-level explanations rendered by clicking the legend's info button. */
  const SECTION_EXPLANATIONS = {
    "security_deny": {
      "title": "Security baseline",
      "what": "A list of patterns that are ALWAYS denied regardless of your category levels. The deny rules survive every preset — applying \"Autopilot\" doesn't relax them, applying \"Always Ask\" doesn't elevate them. They're the floor.",
      "why": "Some actions are dangerous enough that no productivity tradeoff justifies them in a normal session: reading credential files (.env, .pem, AWS credentials), recursive force-deletes (rm -rf), force-pushing git history (git push --force), and the 'curl | sh' install pattern. Uncheck any row to remove it from the baseline; the change persists to your comfort-posture.yaml after you save. Recheck to restore. Add new patterns directly to the YAML if you want to extend the floor."
    }
  };

  /* ── State ───────────────────────────────────────────────────────── */
  /* Each category's value is { default: <level>, overrides: { <pattern>: <level> } }.
   * The YAML emitter outputs the plain-string form `cat: <level>` when overrides
   * is empty, and the object form { default, overrides } otherwise. */
  const state = {
    schema_version: SCHEMA.schema_version || 1,
    global_default: (props.global_default || {}).default || "default",
    categories: {},
    /* security_deny: full array kept in state; checkbox toggles inclusion */
    security_deny: ((props.security_deny || {}).default || []).slice(),
    security_deny_baseline: ((props.security_deny || {}).default || []).slice(),
  };
  for (const k of Object.keys(catProps).sort()) {
    const def = catProps[k].default
      || (catProps[k].enum && catProps[k].enum[Math.floor(catProps[k].enum.length / 2)])
      || "default";
    state.categories[k] = { default: def, overrides: {} };
  }

  /* Read initial state from the DOM (checked radios reflect schema defaults) */
  for (const inp of document.querySelectorAll('input[type="radio"]:checked')) {
    if (inp.name === "global_default") {
      state.global_default = inp.value;
    } else if (catProps[inp.name]) {
      state.categories[inp.name].default = inp.value;
    }
  }

  /* ── YAML emit ───────────────────────────────────────────────────── */
  function quoteYamlKey(s) {
    /* Patterns contain `(:*)` characters that YAML treats as special — always
     * quote them to keep the output round-trippable. */
    return `"${s.replace(/\\/g, "\\\\").replace(/"/g, "\\\"")}"`;
  }
  function emitYaml() {
    const lines = [
      "# Comfort-posture for Claude Code agents.",
      "# Save to .ravenclaude/comfort-posture.yaml in your project root.",
      "# The /set-posture skill translates this into .claude/settings.json rules.",
      `schema_version: ${state.schema_version}`,
      `global_default: ${state.global_default}`,
      "",
    ];
    /* security_deny — emit only patterns currently checked (preserve baseline order) */
    const activeDeny = state.security_deny_baseline.filter(
      p => state.security_deny.indexOf(p) !== -1
    );
    if (activeDeny.length) {
      lines.push("# Always-on deny rules. Survive every preset.");
      lines.push("security_deny:");
      for (const p of activeDeny) lines.push(`  - ${quoteYamlKey(p)}`);
      lines.push("");
    }
    lines.push("categories:");
    for (const k of Object.keys(state.categories).sort()) {
      const cat = state.categories[k];
      const overrideKeys = Object.keys(cat.overrides);
      if (overrideKeys.length === 0) {
        lines.push(`  ${k}: ${cat.default}`);
      } else {
        lines.push(`  ${k}:`);
        lines.push(`    default: ${cat.default}`);
        lines.push("    overrides:");
        for (const pat of overrideKeys.sort()) {
          lines.push(`      ${quoteYamlKey(pat)}: ${cat.overrides[pat]}`);
        }
      }
    }
    return lines.join("\n") + "\n";
  }

  function render() {
    document.getElementById("yaml-output").textContent = emitYaml();
    updateOverrideCounters();
  }

  /* Update the "N overridden" badge in each pattern-details summary. */
  function updateOverrideCounters() {
    document.querySelectorAll(".pattern-override-count[data-for]").forEach(el => {
      const cat = el.getAttribute("data-for");
      if (!state.categories[cat]) return;
      const n = Object.keys(state.categories[cat].overrides).length;
      el.textContent = n === 0 ? "0 overridden" : `${n} overridden`;
      el.classList.toggle("has-overrides", n > 0);
    });
    const secEl = document.getElementById("sec-deny-active-count");
    if (secEl) {
      const active = state.security_deny.length;
      const total = state.security_deny_baseline.length;
      secEl.textContent = `${active}/${total} active`;
      secEl.classList.toggle("has-overrides", active < total);
    }
  }

  /* ── Form change wiring ─────────────────────────────────────────── */
  document.querySelectorAll('input[type="radio"]').forEach(inp => {
    inp.addEventListener("change", () => {
      if (inp.name === "global_default") {
        state.global_default = inp.value;
      } else if (catProps[inp.name]) {
        state.categories[inp.name].default = inp.value;
      }
      flagUnsaved();
      render();
    });
  });

  /* Per-pattern dropdown change handlers */
  document.querySelectorAll(".pattern-select").forEach(sel => {
    sel.addEventListener("change", () => {
      const cat = sel.getAttribute("data-category");
      const pattern = sel.getAttribute("data-pattern");
      if (cat && pattern && state.categories[cat]) {
        if (sel.value === "__default") {
          delete state.categories[cat].overrides[pattern];
        } else {
          state.categories[cat].overrides[pattern] = sel.value;
        }
      }
      sel.setAttribute("data-current", sel.value);
      flagUnsaved();
      render();
    });
  });

  /* security_deny checkboxes */
  document.querySelectorAll(".sec-deny-checkbox").forEach(cb => {
    cb.addEventListener("change", () => {
      const pat = cb.value;
      if (cb.checked) {
        if (state.security_deny.indexOf(pat) === -1) state.security_deny.push(pat);
      } else {
        state.security_deny = state.security_deny.filter(p => p !== pat);
      }
      flagUnsaved();
      render();
    });
  });

  /* ── Preset application ─────────────────────────────────────────── */
  document.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const preset = presets[btn.dataset.preset];
      if (!preset) return;
      const ok = confirm(
        `Apply the "${btn.dataset.preset}" preset?\n\n` +
        `This will overwrite all per-category values AND clear any per-pattern overrides.\n\n` +
        (preset._description || "")
      );
      if (!ok) return;
      state.global_default = preset.global_default || state.global_default;
      const presetCats = preset.categories || {};
      for (const k of Object.keys(state.categories)) {
        if (presetCats[k]) state.categories[k].default = presetCats[k];
        state.categories[k].overrides = {};
      }
      /* Sync DOM: category radios + reset every per-pattern select to default */
      for (const inp of document.querySelectorAll('input[type="radio"]')) {
        if (inp.name === "global_default") {
          inp.checked = inp.value === state.global_default;
        } else if (catProps[inp.name]) {
          inp.checked = inp.value === state.categories[inp.name].default;
        }
      }
      for (const sel of document.querySelectorAll(".pattern-select")) {
        sel.value = "__default";
        sel.setAttribute("data-current", "__default");
      }
      flagUnsaved();
      render();
      toast(`Applied "${btn.dataset.preset}" preset`);
    });
  });

  /* ── Save to repo via server-side /__save endpoint ──────────────── */
  /* The primary save target: writes directly into .ravenclaude/<file> in
   * the agent's project. Only available when the page is served by
   * scripts/serve-dashboards.py (which exposes POST /__save). When the
   * page is served by `python3 -m http.server` or opened via file://,
   * the endpoint is absent; we hide the button and surface the
   * "start the local server" help line. */
  const REPO_TARGET = ".ravenclaude/comfort-posture.yaml";
  const saveRepoBtn = document.getElementById("save-repo-btn");
  const saveRepoHelp = document.getElementById("save-repo-help");
  const noServerHelp = document.getElementById("no-server-help");

  async function probeRepoEndpoint() {
    try {
      const res = await fetch("/__save", { method: "HEAD" });
      return res.ok;
    } catch (e) {
      return false;
    }
  }

  async function saveToRepo() {
    saveRepoBtn.disabled = true;
    setStatus("saving to repo…", "status-unsaved");
    try {
      const res = await fetch("/__save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: REPO_TARGET, content: emitYaml() })
      });
      if (!res.ok) {
        const errText = await res.text().catch(() => "");
        setStatus(`save failed: ${res.status}`, "status-error");
        console.error("Save-to-repo failed:", res.status, errText);
        return;
      }
      const j = await res.json();
      setStatus(`saved to ${j.saved}`, "status-saved");
      toast(`Saved to ${j.saved} (${j.bytes} bytes)`);
    } catch (err) {
      setStatus("save failed - see console", "status-error");
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
      setStatus("save failed — see console", "status-error");
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
      setStatus("connect failed — see console", "status-error");
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

  /* ── Info modal ──────────────────────────────────────────────────── */
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
    let sch;
    if (catName === "global_default") {
      sch = props.global_default;
    } else {
      sch = catProps[catName];
    }
    if (!sch) return;
    modalTitle.textContent = sch.title || catName;
    modalDesc.textContent = sch.description || "";
    modalControls.textContent = sch["x-controls"] || "(no explanation provided)";
    /* Examples as a list */
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

  /* Wire all info buttons. Categories open the category modal; per-pattern
   * and section info buttons open the pattern modal. */
  document.querySelectorAll(".info-btn").forEach(btn => {
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
    }
  });

  /* ── Tab routing ─────────────────────────────────────────────────── */
  const validTabs = ["settings", "commands", "trees", "activity"];
  function applyHash() {
    const hash = (location.hash || "#/settings").replace(/^#\//, "");
    const tab = validTabs.includes(hash) ? hash : "settings";
    document.querySelectorAll(".tab-btn").forEach(b => {
      const sel = b.dataset.tab === tab;
      b.setAttribute("aria-selected", sel ? "true" : "false");
    });
    document.querySelectorAll(".tab-panel").forEach(p => {
      p.classList.toggle("active", p.dataset.tab === tab);
    });
  }
  document.querySelectorAll(".tab-btn").forEach(b => {
    b.addEventListener("click", () => {
      location.hash = "/" + b.dataset.tab;
    });
  });
  window.addEventListener("hashchange", applyHash);
  applyHash();

  /* Initial render */
  render();
})();
""".strip()


_PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>

<header class="page-header">
  <h1>{title}</h1>
  <p class="page-desc">{description}</p>
  <p class="page-desc"><span class="plugin-name">{plugin_name}</span> &middot; static dashboard, no backend. Edits stay in your browser until you click Download.</p>
  <nav class="tab-bar" role="tablist" aria-label="Dashboard tabs">
    <button class="tab-btn" data-tab="settings" role="tab" aria-selected="true">Settings</button>
    <button class="tab-btn" data-tab="commands" role="tab" aria-selected="false">Commands</button>
    <button class="tab-btn" data-tab="trees" role="tab" aria-selected="false">Trees</button>
    <button class="tab-btn" data-tab="activity" role="tab" aria-selected="false">Activity</button>
  </nav>
</header>

<main>
  <section class="tab-panel active" data-tab="settings" role="tabpanel" aria-label="Settings">
{settings_html}
  </section>
  <section class="tab-panel" data-tab="commands" role="tabpanel" aria-label="Commands">
{commands_html}
  </section>
  <section class="tab-panel" data-tab="trees" role="tabpanel" aria-label="Decision trees">
{trees_html}
  </section>
  <section class="tab-panel" data-tab="activity" role="tabpanel" aria-label="Activity">
{activity_html}
  </section>
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
