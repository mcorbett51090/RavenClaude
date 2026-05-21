#!/usr/bin/env python3
"""
generate-repo-guide.py — render docs/repo-guide.html from manifests + plugin content.

Reads .claude-plugin/marketplace.json, each plugin's plugin.json, and the agent/
skill/hook/rule/template files under plugins/*/. Emits a single self-contained
HTML page (inline CSS + JS, no external CDN) at docs/repo-guide.html.

Designed to be re-run on every release. CI uses scripts/check-guide-fresh.sh to
fail the build if the committed HTML is out of date relative to the sources.

Usage:
    python3 scripts/generate-repo-guide.py [--output PATH] [--check]

    --output PATH   Write to PATH instead of docs/repo-guide.html.
    --check         Print the rendered HTML to stdout instead of writing a file.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "repo-guide.html"

# Map plugin name → accent color (for visual differentiation).
PLUGIN_COLORS = {
    "ravenclaude-core": "#14b8a6",
    "power-platform": "#8b5cf6",
    "finance": "#f59e0b",
    "regulatory-compliance": "#ef4444",
    "web-design": "#3b82f6",
}
DEFAULT_COLOR = "#64748b"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
YAML_KV_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")


@dataclass
class Item:
    name: str
    description: str = ""
    extra: dict[str, str] = field(default_factory=dict)
    path: str = ""


@dataclass
class Plugin:
    name: str
    version: str
    description: str
    requires: str = ""
    keywords: list[str] = field(default_factory=list)
    agents: list[Item] = field(default_factory=list)
    skills: list[Item] = field(default_factory=list)
    hooks: list[Item] = field(default_factory=list)
    rules: list[Item] = field(default_factory=list)
    templates: list[Item] = field(default_factory=list)
    bundled_mcp: list[Item] = field(default_factory=list)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse the subset of YAML we use in frontmatter: single-line key: value pairs
    plus block scalars introduced by `>` (folded) or `|` (literal). Indented
    continuation lines are joined; folded mode collapses whitespace to a space."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm: dict[str, str] = {}
    lines = m.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        kv = YAML_KV_RE.match(line)
        if not kv:
            i += 1
            continue
        key, raw = kv.group(1), kv.group(2)
        marker = raw.strip()
        if marker in (">", "|"):
            # Collect indented continuation lines.
            i += 1
            buf: list[str] = []
            while i < len(lines):
                nxt = lines[i]
                if nxt.strip() == "":
                    buf.append("")
                    i += 1
                    continue
                if nxt[:1] in (" ", "\t"):
                    buf.append(nxt.strip())
                    i += 1
                    continue
                break
            joined = " ".join(b for b in buf if b) if marker == ">" else "\n".join(buf)
            fm[key] = joined.strip()
        else:
            fm[key] = raw.strip().strip('"').strip("'")
            i += 1
    return fm, text[m.end():]


def first_line(text: str, max_chars: int = 240) -> str:
    """Return the first non-empty, non-heading, non-blockquote, non-list-marker line."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("#", ">", "---", "```", "<!--")):
            continue
        # Skip pure list markers with no text
        if stripped in {"-", "*", "+"}:
            continue
        # Strip leading list / quote markers
        cleaned = re.sub(r"^[-*+>\s]+", "", stripped)
        if cleaned:
            return cleaned[:max_chars]
    return ""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def parse_agent(path: Path) -> Item:
    text = read_text(path)
    fm, _ = parse_frontmatter(text)
    return Item(
        name=fm.get("name", path.stem),
        description=fm.get("description", ""),
        extra={"tools": fm.get("tools", ""), "model": fm.get("model", "")},
        path=str(path.relative_to(REPO_ROOT)),
    )


def parse_skill(path: Path) -> Item:
    """Skills can be a flat file (skills/foo.md) or a folder (skills/foo/SKILL.md)."""
    if path.is_dir():
        skill_md = path / "SKILL.md"
        if not skill_md.exists():
            return Item(name=path.name, description="", path=str(path.relative_to(REPO_ROOT)))
        text = read_text(skill_md)
        rel = skill_md
    else:
        text = read_text(path)
        rel = path
    fm, body = parse_frontmatter(text)
    desc = fm.get("description") or first_line(body)
    return Item(
        name=fm.get("name", path.stem),
        description=desc,
        path=str(rel.relative_to(REPO_ROOT)),
    )


def parse_hook(path: Path) -> Item:
    """Hook description is the first contiguous comment block after the shebang."""
    text = read_text(path)
    lines = text.splitlines()
    desc_lines: list[str] = []
    started = False
    for line in lines:
        if line.startswith("#!"):
            continue
        if line.startswith("#"):
            started = True
            stripped = line.lstrip("# ").rstrip()
            if stripped:
                desc_lines.append(stripped)
        elif started:
            break
    description = " ".join(desc_lines)[:400]
    return Item(name=path.name, description=description, path=str(path.relative_to(REPO_ROOT)))


def parse_rule(path: Path) -> Item:
    """Rule description is the first heading or first non-empty line."""
    text = read_text(path)
    desc = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            desc = stripped.lstrip("# ").strip()
            break
    if not desc:
        desc = first_line(text)
    return Item(name=path.stem, description=desc, path=str(path.relative_to(REPO_ROOT)))


def parse_template(path: Path) -> Item:
    """Templates: just file/folder name + first heading if it's a .md file."""
    if path.is_dir():
        return Item(name=path.name + "/", description="(template folder)", path=str(path.relative_to(REPO_ROOT)))
    text = read_text(path)
    desc = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            desc = stripped.lstrip("# ").strip()
            break
    return Item(name=path.name, description=desc, path=str(path.relative_to(REPO_ROOT)))


def load_plugin(plugin_dir: Path, manifest_entry: dict) -> Plugin:
    manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
    plugin_json = {}
    if manifest_path.exists():
        plugin_json = json.loads(manifest_path.read_text())

    plugin = Plugin(
        name=manifest_entry["name"],
        version=plugin_json.get("version", manifest_entry.get("version", "?")),
        description=manifest_entry.get("description", plugin_json.get("description", "")),
        requires=str(plugin_json.get("requires", "")) if plugin_json.get("requires") else "",
        keywords=manifest_entry.get("keywords", []),
    )

    agents_dir = plugin_dir / "agents"
    if agents_dir.is_dir():
        plugin.agents = sorted(
            (parse_agent(p) for p in agents_dir.glob("*.md") if p.is_file()),
            key=lambda x: x.name,
        )

    skills_dir = plugin_dir / "skills"
    if skills_dir.is_dir():
        skill_items: list[Item] = []
        for entry in sorted(skills_dir.iterdir()):
            if entry.is_file() and entry.suffix == ".md":
                skill_items.append(parse_skill(entry))
            elif entry.is_dir():
                skill_items.append(parse_skill(entry))
        plugin.skills = skill_items

    hooks_dir = plugin_dir / "hooks"
    if hooks_dir.is_dir():
        plugin.hooks = sorted(
            (parse_hook(p) for p in hooks_dir.glob("*.sh") if p.is_file()),
            key=lambda x: x.name,
        )

    rules_dir = plugin_dir / "rules"
    if rules_dir.is_dir():
        plugin.rules = sorted(
            (parse_rule(p) for p in rules_dir.glob("*.md") if p.is_file()),
            key=lambda x: x.name,
        )

    templates_dir = plugin_dir / "templates"
    if templates_dir.is_dir():
        plugin.templates = sorted(
            (parse_template(p) for p in templates_dir.iterdir()),
            key=lambda x: x.name,
        )

    mcp = plugin_json.get("mcpServers", {})
    if mcp:
        plugin.bundled_mcp = [Item(name=k, description=str(v)) for k, v in mcp.items()]

    return plugin


def load_marketplace() -> tuple[dict, list[Plugin]]:
    marketplace_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"
    marketplace = json.loads(marketplace_path.read_text())
    plugins: list[Plugin] = []
    for entry in marketplace.get("plugins", []):
        plugin_dir = REPO_ROOT / entry["source"].lstrip("./")
        if not plugin_dir.is_dir():
            continue
        plugins.append(load_plugin(plugin_dir, entry))
    return marketplace, plugins


# ---------- HTML rendering ----------

def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def render_item_card(item: Item, kind: str) -> str:
    extras = []
    for k, v in item.extra.items():
        if v:
            extras.append(f'<span class="extra-pill" data-kind="{esc(k)}">{esc(k)}: {esc(v)}</span>')
    extra_html = " ".join(extras)
    path_html = f'<div class="item-path">{esc(item.path)}</div>' if item.path else ""
    return (
        f'<article class="item" data-kind="{esc(kind)}" data-search="{esc((item.name + " " + item.description).lower())}">'
        f'<header><h4>{esc(item.name)}</h4>{extra_html}</header>'
        f'<p>{esc(item.description) or "<em>(no description)</em>"}</p>'
        f'{path_html}'
        f'</article>'
    )


def render_section(title: str, items: list[Item], kind: str) -> str:
    if not items:
        return ""
    cards = "\n".join(render_item_card(i, kind) for i in items)
    return (
        f'<section class="plugin-section" data-section="{esc(kind)}">'
        f'<h3>{esc(title)} <span class="count">({len(items)})</span></h3>'
        f'<div class="item-grid">{cards}</div>'
        f'</section>'
    )


def render_plugin(plugin: Plugin) -> str:
    color = PLUGIN_COLORS.get(plugin.name, DEFAULT_COLOR)
    keywords = " ".join(f'<span class="kw">{esc(k)}</span>' for k in plugin.keywords)
    requires_html = f'<div class="meta-row"><span class="meta-label">Requires</span> <code>{esc(plugin.requires)}</code></div>' if plugin.requires else ""
    counts = [
        ("Agents", len(plugin.agents)),
        ("Skills", len(plugin.skills)),
        ("Hooks", len(plugin.hooks)),
        ("Rules", len(plugin.rules)),
        ("Templates", len(plugin.templates)),
        ("MCP servers", len(plugin.bundled_mcp)),
    ]
    count_pills = "".join(
        f'<span class="count-pill"><strong>{n}</strong> {label}</span>'
        for label, n in counts if n
    )
    sections = "\n".join(
        s for s in [
            render_section("Agents", plugin.agents, "agent"),
            render_section("Skills", plugin.skills, "skill"),
            render_section("Hooks", plugin.hooks, "hook"),
            render_section("Rules", plugin.rules, "rule"),
            render_section("Templates", plugin.templates, "template"),
            render_section("Bundled MCP servers", plugin.bundled_mcp, "mcp"),
        ] if s
    )

    return f"""
    <article class="plugin-card" data-plugin="{esc(plugin.name)}" style="--accent: {color}">
      <header class="plugin-header">
        <div class="plugin-title">
          <h2>{esc(plugin.name)}</h2>
          <span class="version">v{esc(plugin.version)}</span>
        </div>
        <p class="plugin-desc">{esc(plugin.description)}</p>
        {requires_html}
        <div class="keywords">{keywords}</div>
        <div class="counts">{count_pills}</div>
      </header>
      <div class="plugin-body">
        {sections}
      </div>
    </article>
    """


def render_index(plugins: list[Plugin]) -> str:
    rows = []
    for plugin in plugins:
        for kind, items in [
            ("agent", plugin.agents),
            ("skill", plugin.skills),
            ("hook", plugin.hooks),
            ("rule", plugin.rules),
            ("template", plugin.templates),
        ]:
            for item in items:
                rows.append({
                    "plugin": plugin.name,
                    "kind": kind,
                    "name": item.name,
                    "description": item.description,
                    "path": item.path,
                })
    return json.dumps(rows)


def render(marketplace: dict, plugins: list[Plugin]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    market_version = marketplace.get("metadata", {}).get("version", "?")
    market_desc = marketplace.get("metadata", {}).get("description", "")
    total_agents = sum(len(p.agents) for p in plugins)
    total_skills = sum(len(p.skills) for p in plugins)
    total_hooks = sum(len(p.hooks) for p in plugins)
    total_templates = sum(len(p.templates) for p in plugins)
    plugin_count = len(plugins)

    nav_items = "".join(
        f'<button class="nav-btn" data-target="plugin-{esc(p.name)}" style="--accent: {PLUGIN_COLORS.get(p.name, DEFAULT_COLOR)}">{esc(p.name)} <span class="ver">v{esc(p.version)}</span></button>'
        for p in plugins
    )

    plugin_cards = "\n".join(
        f'<section id="plugin-{esc(p.name)}" class="plugin-target">{render_plugin(p)}</section>'
        for p in plugins
    )

    index_json = render_index(plugins)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>RavenClaude — Marketplace Guide</title>
  <style>
    :root {{
      --bg: #0b1120;
      --surface: #111827;
      --surface-2: #1f2937;
      --border: #334155;
      --text: #f1f5f9;
      --muted: #94a3b8;
      --accent: #14b8a6;
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{
      margin: 0; padding: 0;
      background: var(--bg); color: var(--text);
      font-family: var(--font-sans); font-size: 15px; line-height: 1.5;
    }}
    a {{ color: #5eead4; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    code {{ font-family: var(--font-mono); background: var(--surface-2); padding: 2px 6px; border-radius: 4px; font-size: 0.88em; }}
    header.site {{
      position: sticky; top: 0; z-index: 50;
      background: rgba(11,17,32,0.92); backdrop-filter: blur(8px);
      border-bottom: 1px solid var(--border);
      padding: 1rem 1.5rem;
    }}
    header.site .title-row {{ display: flex; align-items: baseline; gap: 1rem; flex-wrap: wrap; }}
    header.site h1 {{ margin: 0; font-size: 1.4rem; letter-spacing: -0.01em; }}
    header.site .version-banner {{ font-family: var(--font-mono); color: var(--muted); font-size: 0.9rem; }}
    header.site .version-banner strong {{ color: var(--accent); }}
    header.site .generated {{ font-size: 0.78rem; color: var(--muted); margin-top: 0.25rem; }}
    .stats {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 0.75rem; font-size: 0.88rem; }}
    .stats div {{ background: var(--surface); padding: 0.4rem 0.75rem; border-radius: 6px; border: 1px solid var(--border); }}
    .stats strong {{ color: var(--accent); }}
    main {{ max-width: 1280px; margin: 0 auto; padding: 1.5rem; }}
    nav.tabs {{ display: flex; gap: 0.5rem; margin-bottom: 1.5rem; flex-wrap: wrap; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }}
    .tab-btn, .nav-btn {{
      background: var(--surface); color: var(--text);
      border: 1px solid var(--border); padding: 0.5rem 1rem;
      border-radius: 6px; cursor: pointer; font-family: var(--font-sans); font-size: 0.9rem;
      transition: background 0.15s, border-color 0.15s;
    }}
    .tab-btn[aria-selected="true"] {{ background: var(--surface-2); border-color: var(--accent); color: var(--accent); }}
    .tab-btn:hover, .nav-btn:hover {{ background: var(--surface-2); border-color: var(--accent); }}
    .nav-btn {{ display: inline-flex; align-items: center; gap: 0.4rem; }}
    .nav-btn .ver {{ font-family: var(--font-mono); font-size: 0.78rem; color: var(--muted); }}
    section.panel {{ display: none; }}
    section.panel.active {{ display: block; }}
    .search-row {{ display: flex; gap: 0.5rem; margin-bottom: 1rem; }}
    .search-row input {{
      flex: 1; background: var(--surface); border: 1px solid var(--border);
      color: var(--text); padding: 0.6rem 0.9rem; border-radius: 6px; font-family: var(--font-sans);
    }}
    .search-row input:focus {{ outline: none; border-color: var(--accent); }}
    .plugin-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-left: 4px solid var(--accent);
      border-radius: 8px;
      padding: 1.25rem 1.5rem;
      margin-bottom: 1.5rem;
    }}
    .plugin-target {{ scroll-margin-top: 8rem; }}
    .plugin-title {{ display: flex; align-items: baseline; gap: 0.75rem; }}
    .plugin-title h2 {{ margin: 0; color: var(--accent); }}
    .plugin-title .version {{ font-family: var(--font-mono); color: var(--muted); font-size: 0.92rem; }}
    .plugin-desc {{ color: var(--muted); margin: 0.5rem 0; }}
    .keywords {{ display: flex; gap: 0.4rem; flex-wrap: wrap; margin: 0.5rem 0; }}
    .keywords .kw {{ background: var(--surface-2); padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.78rem; color: var(--muted); font-family: var(--font-mono); }}
    .meta-row {{ font-size: 0.85rem; color: var(--muted); margin: 0.25rem 0; }}
    .meta-row .meta-label {{ color: var(--text); font-weight: 600; }}
    .counts {{ display: flex; gap: 0.4rem; flex-wrap: wrap; margin: 0.75rem 0; }}
    .count-pill {{ background: var(--surface-2); border: 1px solid var(--border); padding: 0.25rem 0.6rem; border-radius: 12px; font-size: 0.78rem; }}
    .count-pill strong {{ color: var(--accent); margin-right: 0.25rem; }}
    .plugin-body {{ margin-top: 1rem; }}
    .plugin-section h3 {{
      font-size: 1rem; margin: 1.5rem 0 0.75rem 0; color: var(--text);
      border-bottom: 1px dashed var(--border); padding-bottom: 0.4rem;
    }}
    .plugin-section h3 .count {{ color: var(--muted); font-weight: 400; font-size: 0.88rem; }}
    .item-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 0.75rem; }}
    article.item {{
      background: var(--surface-2);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 0.85rem 1rem;
      transition: border-color 0.15s;
    }}
    article.item:hover {{ border-color: var(--accent); }}
    article.item header {{ display: flex; align-items: baseline; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.4rem; }}
    article.item h4 {{ margin: 0; font-size: 0.96rem; color: var(--text); font-family: var(--font-mono); }}
    article.item p {{ margin: 0; color: var(--muted); font-size: 0.88rem; }}
    article.item .item-path {{ margin-top: 0.5rem; font-family: var(--font-mono); font-size: 0.74rem; color: #475569; }}
    .extra-pill {{ background: var(--surface); padding: 0.1rem 0.4rem; border-radius: 4px; font-size: 0.72rem; color: var(--muted); font-family: var(--font-mono); }}
    article.item.hidden {{ display: none; }}
    .index-table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
    .index-table th {{ text-align: left; padding: 0.5rem; border-bottom: 1px solid var(--border); color: var(--muted); font-weight: 600; }}
    .index-table td {{ padding: 0.5rem; border-bottom: 1px solid var(--surface-2); }}
    .index-table tr:hover {{ background: var(--surface); }}
    .kind-tag {{ display: inline-block; padding: 0.1rem 0.5rem; border-radius: 4px; font-size: 0.74rem; font-family: var(--font-mono); background: var(--surface-2); color: var(--muted); }}
    .arch-doc {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; }}
    .arch-doc h2 {{ margin-top: 0; color: var(--accent); }}
    .arch-doc ul {{ padding-left: 1.5rem; }}
    .arch-doc li {{ margin-bottom: 0.4rem; }}
    footer.site {{ text-align: center; padding: 2rem 1rem; color: var(--muted); font-size: 0.85rem; border-top: 1px solid var(--border); margin-top: 3rem; }}
    @media (max-width: 720px) {{
      header.site h1 {{ font-size: 1.2rem; }}
      .item-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>

<header class="site">
  <div class="title-row">
    <h1>🐦‍⬛ RavenClaude — Marketplace Guide</h1>
    <span class="version-banner">marketplace <strong>v{esc(market_version)}</strong></span>
  </div>
  <div class="generated">Generated {esc(now)} by <code>scripts/generate-repo-guide.py</code></div>
  <div class="stats">
    <div><strong>{plugin_count}</strong> plugins</div>
    <div><strong>{total_agents}</strong> agents</div>
    <div><strong>{total_skills}</strong> skills</div>
    <div><strong>{total_hooks}</strong> hooks</div>
    <div><strong>{total_templates}</strong> templates</div>
  </div>
</header>

<main>
  <nav class="tabs" role="tablist">
    <button class="tab-btn" data-tab="overview" aria-selected="true">Overview</button>
    <button class="tab-btn" data-tab="plugins" aria-selected="false">Plugins</button>
    <button class="tab-btn" data-tab="architecture" aria-selected="false">Architecture</button>
    <button class="tab-btn" data-tab="index" aria-selected="false">Index / Search</button>
  </nav>

  <section class="panel active" data-panel="overview">
    <div class="arch-doc">
      <h2>What this is</h2>
      <p>{esc(market_desc)}</p>
      <h2>How to install</h2>
      <pre><code>/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ravenclaude-core@ravenclaude
# Optional:
/plugin install power-platform@ravenclaude
/plugin install finance@ravenclaude
/plugin install regulatory-compliance@ravenclaude
/plugin install web-design@ravenclaude
/reload-plugins</code></pre>
      <h2>Jump to a plugin</h2>
      <nav class="tabs" style="border:0; padding:0;">
        {nav_items}
      </nav>
    </div>
  </section>

  <section class="panel" data-panel="plugins">
    <div class="search-row">
      <input id="plugin-search" type="search" placeholder="Search agents, skills, hooks, rules, templates within plugins…" />
    </div>
    {plugin_cards}
  </section>

  <section class="panel" data-panel="architecture">
    <div class="arch-doc">
      <h2>The marketplace model</h2>
      <p>RavenClaude is a single private Claude Code plugin marketplace. The "product" of this repo is the contents of <code>plugins/</code>. Consumers run <code>/plugin install &lt;name&gt;@ravenclaude</code> from any Claude Code project to pull a plugin into their session.</p>
      <h2>Hierarchical dispatch (Team Lead → specialists)</h2>
      <ul>
        <li>The top-level Claude session is the <strong>Team Lead</strong>.</li>
        <li>Specialists never spawn other specialists — only the Team Lead dispatches. Enforced by the <code>guard-recursive-spawn</code> hook.</li>
        <li>Every specialist emits its report ending with a <code>---RESULT_START--- … ---RESULT_END---</code> JSON block (the Structured Output Protocol). The Team Lead parses the JSON to drive routing.</li>
        <li>The <code>spawn-team</code> skill in <code>ravenclaude-core</code> is the canonical dispatch playbook. Its "Cross-plugin dispatch" section names which domain plugin to route into.</li>
      </ul>
      <h2>Plugin separation</h2>
      <ul>
        <li><strong><code>ravenclaude-core</code></strong> stays domain-neutral — generic agents, dispatch playbook, gates, hooks.</li>
        <li>Domain plugins extend core. They inherit the constitution and add their own specialists, skills, hooks, and templates.</li>
        <li>A plugin's <code>CLAUDE.md</code> auto-loads when active in a consumer session.</li>
      </ul>
      <h2>Layout enforcement</h2>
      <p>A new file's path must match at least one glob in <code>.repo-layout.json</code>. Enforcement is in two layers: the <code>enforce-layout</code> hook fires PreToolUse on Write/Edit/MultiEdit; the <code>validate-layout</code> CI workflow runs on every PR. Path-scoped rule files were considered but they only load on Read, not on Write — see Claude Code issue #23478.</p>
      <h2>CI gates (validated by the gate-audit meta-test)</h2>
      <p>Each CI gate must prove bidirectionally that it fails on a known-bad input AND passes on a known-good input. <code>scripts/audit-gates.sh</code> enforces this — 21 assertions across 10 gates today. See <a href="best-practices/ci-gate-audit.md">docs/best-practices/ci-gate-audit.md</a>.</p>
    </div>
  </section>

  <section class="panel" data-panel="index">
    <div class="search-row">
      <input id="index-search" type="search" placeholder="Search across every agent, skill, hook, rule, template in every plugin…" />
    </div>
    <table class="index-table">
      <thead>
        <tr><th>Kind</th><th>Plugin</th><th>Name</th><th>Description</th><th>Path</th></tr>
      </thead>
      <tbody id="index-body"></tbody>
    </table>
  </section>
</main>

<footer class="site">
  Regenerate with <code>python3 scripts/generate-repo-guide.py</code>. CI verifies freshness via <code>scripts/check-guide-fresh.sh</code>.
</footer>

<script>
  // Tab switching
  const tabs = document.querySelectorAll('.tab-btn');
  const panels = document.querySelectorAll('section.panel');
  tabs.forEach(btn => {{
    btn.addEventListener('click', () => {{
      const target = btn.dataset.tab;
      tabs.forEach(b => b.setAttribute('aria-selected', b === btn ? 'true' : 'false'));
      panels.forEach(p => p.classList.toggle('active', p.dataset.panel === target));
    }});
  }});

  // Jump-to-plugin buttons in the overview
  document.querySelectorAll('.nav-btn[data-target]').forEach(btn => {{
    btn.addEventListener('click', () => {{
      // switch to plugins tab
      tabs.forEach(t => t.setAttribute('aria-selected', t.dataset.tab === 'plugins' ? 'true' : 'false'));
      panels.forEach(p => p.classList.toggle('active', p.dataset.panel === 'plugins'));
      // scroll to the target
      const el = document.getElementById(btn.dataset.target);
      if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }});
  }});

  // Plugin-pane search
  const pluginSearch = document.getElementById('plugin-search');
  if (pluginSearch) {{
    pluginSearch.addEventListener('input', () => {{
      const q = pluginSearch.value.toLowerCase().trim();
      document.querySelectorAll('article.item').forEach(card => {{
        const hay = card.dataset.search || '';
        card.classList.toggle('hidden', q && !hay.includes(q));
      }});
    }});
  }}

  // Index / Search panel
  const INDEX = {index_json};
  const indexBody = document.getElementById('index-body');
  function renderIndex(q) {{
    const needle = q.toLowerCase().trim();
    indexBody.innerHTML = INDEX
      .filter(r => !needle || (r.name + ' ' + r.description + ' ' + r.plugin + ' ' + r.kind).toLowerCase().includes(needle))
      .map(r => `<tr>
        <td><span class="kind-tag">${{r.kind}}</span></td>
        <td>${{r.plugin}}</td>
        <td><code>${{r.name}}</code></td>
        <td>${{r.description}}</td>
        <td><code>${{r.path}}</code></td>
      </tr>`)
      .join('');
  }}
  renderIndex('');
  document.getElementById('index-search').addEventListener('input', e => renderIndex(e.target.value));
</script>

</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--check", action="store_true", help="Print HTML to stdout, don't write file.")
    args = ap.parse_args()

    marketplace, plugins = load_marketplace()
    output = render(marketplace, plugins)

    if args.check:
        sys.stdout.write(output)
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(f"wrote {args.output.relative_to(REPO_ROOT)} ({len(output):,} bytes, {len(plugins)} plugins)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
