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
import datetime as dt
import html
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"

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
    # Preset bar
    preset_buttons: list[str] = []
    for preset_name in sorted(presets.keys()):
        preset = presets[preset_name]
        preset_desc = preset.get("_description", "")
        preset_buttons.append(
            f'<button type="button" class="preset-btn" data-preset="{html.escape(preset_name)}" '
            f'title="{html.escape(preset_desc)}">{html.escape(preset_name.capitalize())}</button>'
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
        rows = [
            _render_segmented(name, sch, f"cat-{name}", group=group_name)
            for name, sch in groups[group_name]
        ]
        group_html_parts.append(
            f'<fieldset class="cat-group"><legend>{html.escape(group_name)}</legend>'
            + "".join(rows)
            + "</fieldset>"
        )

    return _SETTINGS_TAB_TEMPLATE.format(
        preset_buttons="".join(preset_buttons),
        global_default=global_default_html,
        category_groups="".join(group_html_parts),
    )


def _render_segmented(name: str, schema: dict, id_prefix: str, group: str | None = None) -> str:
    """Render one segmented-radiogroup row from a schema property."""
    title = schema.get("title", name)
    description = schema.get("description", "")
    enum_values = schema.get("enum", ["cautious", "default", "productive"])
    default_value = schema.get("default", enum_values[len(enum_values) // 2])
    group_attr = f' data-group="{html.escape(group)}"' if group else ""

    radios = []
    for v in enum_values:
        rid = f"{id_prefix}-{v}"
        checked = "checked" if v == default_value else ""
        radios.append(
            f'<input type="radio" id="{html.escape(rid)}" name="{html.escape(name)}" '
            f'value="{html.escape(v)}" {checked}>'
            f'<label for="{html.escape(rid)}" class="seg-label seg-{html.escape(v)}">'
            f"{html.escape(v.capitalize())}</label>"
        )

    return (
        f'<div class="cat-row" data-category="{html.escape(name)}"{group_attr}>'
        f'<div class="cat-meta">'
        f'<div class="cat-title">{html.escape(title)}</div>'
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
  padding: 8px 16px;
  border-radius: 6px;
  font: inherit;
  cursor: pointer;
  font-weight: 500;
}
.preset-btn:hover { border-color: var(--accent); }
.preset-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
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
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
  align-items: center;
}
.cat-row:last-child { border-bottom: none; }
.cat-title { font-weight: 500; font-size: 14px; margin-bottom: 2px; }
.cat-desc { font-size: 12px; color: var(--muted); max-width: 480px; }

/* Segmented control (radiogroup with pill buttons) */
.seg-control {
  display: inline-flex;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 2px;
  gap: 0;
}
.seg-control input[type="radio"] {
  position: absolute;
  opacity: 0;
  width: 1px;
  height: 1px;
  overflow: hidden;
}
.seg-label {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 500;
  color: var(--muted);
  border-radius: 6px;
  cursor: pointer;
  transition: background 80ms ease, color 80ms ease;
  user-select: none;
  min-width: 78px;
  text-align: center;
}
.seg-control input[type="radio"]:checked + .seg-label {
  background: var(--accent);
  color: var(--bg);
  font-weight: 600;
}
.seg-control input[type="radio"]:focus-visible + .seg-label {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
.seg-label:hover { color: var(--text); }

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
.yaml-actions {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid var(--border);
  background: var(--surface-2);
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
  </div>

  <aside class="yaml-preview">
    <h3>
      <span>comfort-posture.yaml</span>
      <span id="yaml-status" style="color: var(--muted); font-weight: 400; font-size: 12px;">unsaved</span>
    </h3>
    <pre id="yaml-output"></pre>
    <div class="yaml-actions">
      <button class="btn" id="copy-btn">Copy YAML</button>
      <button class="btn secondary" id="download-btn">Download</button>
    </div>
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

  /* ── State ───────────────────────────────────────────────────────── */
  const state = {
    schema_version: SCHEMA.schema_version || 1,
    global_default: (props.global_default || {}).default || "default",
    categories: {}
  };
  for (const k of Object.keys(catProps).sort()) {
    state.categories[k] = catProps[k].default
      || (catProps[k].enum && catProps[k].enum[Math.floor(catProps[k].enum.length / 2)])
      || "default";
  }

  /* Read initial state from the DOM (checked radios reflect schema defaults) */
  for (const inp of document.querySelectorAll('input[type="radio"]:checked')) {
    if (inp.name === "global_default") {
      state.global_default = inp.value;
    } else if (catProps[inp.name]) {
      state.categories[inp.name] = inp.value;
    }
  }

  /* ── YAML emit ───────────────────────────────────────────────────── */
  function emitYaml() {
    const lines = [
      "# Comfort-posture for Claude Code agents.",
      "# Save to .ravenclaude/comfort-posture.yaml in your project root.",
      "# The /set-posture skill translates this into .claude/settings.json rules.",
      `schema_version: ${state.schema_version}`,
      `global_default: ${state.global_default}`,
      "categories:"
    ];
    for (const k of Object.keys(state.categories).sort()) {
      lines.push(`  ${k}: ${state.categories[k]}`);
    }
    return lines.join("\n") + "\n";
  }

  function render() {
    document.getElementById("yaml-output").textContent = emitYaml();
  }

  /* ── Form change wiring ─────────────────────────────────────────── */
  document.querySelectorAll('input[type="radio"]').forEach(inp => {
    inp.addEventListener("change", () => {
      if (inp.name === "global_default") {
        state.global_default = inp.value;
      } else if (catProps[inp.name]) {
        state.categories[inp.name] = inp.value;
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
        `This will overwrite all per-category values.\n\n` +
        (preset._description || "")
      );
      if (!ok) return;
      state.global_default = preset.global_default || state.global_default;
      Object.assign(state.categories, preset.categories || {});
      /* Sync DOM */
      for (const inp of document.querySelectorAll('input[type="radio"]')) {
        if (inp.name === "global_default") {
          inp.checked = inp.value === state.global_default;
        } else if (catProps[inp.name]) {
          inp.checked = inp.value === state.categories[inp.name];
        }
      }
      flagUnsaved();
      render();
      toast(`Applied "${btn.dataset.preset}" preset`);
    });
  });

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
  function flagUnsaved() {
    document.getElementById("yaml-status").textContent = "unsaved";
    document.getElementById("yaml-status").style.color = "var(--warn)";
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

<footer class="page-footer">
  Generated by <code>scripts/generate-dashboards.py</code>.
  Source schema: <code>plugins/{plugin_name}/dashboard-schema.json</code>.
  Design: <a href="https://github.com/mcorbett51090/RavenClaude/blob/main/docs/proposals/2026-05-22-003-per-plugin-dashboard.md">proposal 003</a>.
</footer>

<script type="application/json" id="schema-data">
{schema_json}
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
