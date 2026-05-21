#!/usr/bin/env python3
"""
generate-repo-guide.py — render repo-guide.html from manifests + plugin content.

Reads .claude-plugin/marketplace.json, each plugin's plugin.json, and the agent/
skill/hook/rule/template files under plugins/*/. Emits a single self-contained
HTML page (inline CSS + JS, no external CDN) at repo-guide.html.

Designed to be re-run on every release. CI uses scripts/check-guide-fresh.sh to
fail the build if the committed HTML is out of date relative to the sources.

Usage:
    python3 scripts/generate-repo-guide.py [--output PATH] [--check]

    --output PATH   Write to PATH instead of repo-guide.html.
    --check         Print the rendered HTML to stdout instead of writing a file.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "repo-guide.html"

# Map plugin name → accent color (for visual differentiation).
PLUGIN_COLORS = {
    "ravenclaude-core": "#14b8a6",
    "power-platform": "#8b5cf6",
    "finance": "#f59e0b",
    "regulatory-compliance": "#ef4444",
    "web-design": "#3b82f6",
}
DEFAULT_COLOR = "#64748b"

# Audience taxonomy — fixed at 7 values per the deep-researcher recommendation.
# Documented in docs/best-practices/agent-scenario-authoring.md.
AUDIENCE_LABELS = {
    "consultant": "Consultant",
    "psm": "Partner Success",
    "dev": "Developer",
    "power-platform-maker": "Power Platform maker",
    "data-engineer": "Data engineer",
    "analyst": "Analyst",
    "compliance": "Compliance",
}

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
YAML_KV_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")
INLINE_LIST_RE = re.compile(r"^\[(.*)\]$")


@dataclass
class Item:
    name: str
    description: str = ""
    extra: dict[str, str] = field(default_factory=dict)
    path: str = ""
    # Agent-only enrichment (other Item kinds leave these empty).
    audience: list[str] = field(default_factory=list)
    works_with: list[str] = field(default_factory=list)
    scenarios: list[dict] = field(default_factory=list)
    quickstart: list[str] = field(default_factory=list)


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
    last_updated: str = ""  # YYYY-MM-DD from `git log -1 -- plugins/<name>`


def _split_inline_list(s: str) -> list[str]:
    """Split an inline YAML list body like `a, b, "c, d"` into ["a", "b", "c, d"]."""
    items: list[str] = []
    buf: list[str] = []
    in_quote: str = ""
    for ch in s:
        if in_quote:
            if ch == in_quote:
                in_quote = ""
            else:
                buf.append(ch)
        elif ch in ('"', "'"):
            in_quote = ch
        elif ch == ",":
            items.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        items.append("".join(buf).strip())
    return [item.strip().strip('"').strip("'") for item in items if item.strip()]


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse the subset of YAML we use in frontmatter:
    - single-line key: value pairs
    - block scalars introduced by `>` (folded) or `|` (literal)
    - inline lists `key: [a, b, c]`
    - block lists `key:\\n  - item1\\n  - item2`
    - block lists of mappings `key:\\n  - field1: value\\n    field2: value` (for scenarios)
    Returns a dict where values are str, list[str], or list[dict[str,str]].
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm: dict = {}
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
        # Inline list: key: [a, b, c]
        ilm = INLINE_LIST_RE.match(marker)
        if ilm:
            fm[key] = _split_inline_list(ilm.group(1))
            i += 1
            continue
        if marker in (">", "|"):
            # Collect indented continuation lines as a single scalar.
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
            continue
        if marker == "":
            # Possible block list. Look ahead at indentation.
            j = i + 1
            block_items: list = []
            block_was_mapping = False
            while j < len(lines):
                nxt = lines[j]
                if nxt.strip() == "":
                    j += 1
                    continue
                if not (nxt.startswith("  ") or nxt.startswith("\t")):
                    break
                stripped = nxt.lstrip()
                if stripped.startswith("- "):
                    item_body = stripped[2:].strip()
                    kv2 = YAML_KV_RE.match(item_body)
                    if kv2 and kv2.group(2).strip() != "":
                        # First field of a mapping inside a list.
                        block_was_mapping = True
                        item: dict[str, str] = {}
                        ik, iv = kv2.group(1), kv2.group(2).strip()
                        item[ik] = iv.strip('"').strip("'")
                        j += 1
                        # Collect additional fields at deeper indentation.
                        list_item_indent = len(nxt) - len(nxt.lstrip())
                        while j < len(lines):
                            nxt2 = lines[j]
                            if nxt2.strip() == "":
                                j += 1
                                continue
                            indent2 = len(nxt2) - len(nxt2.lstrip())
                            if indent2 <= list_item_indent:
                                break
                            kv3 = YAML_KV_RE.match(nxt2.strip())
                            if kv3:
                                item[kv3.group(1)] = kv3.group(2).strip().strip('"').strip("'")
                            j += 1
                        block_items.append(item)
                    else:
                        # Simple scalar list item.
                        block_items.append(item_body.strip('"').strip("'"))
                        j += 1
                else:
                    break
            if block_items:
                fm[key] = block_items
                i = j
                continue
            # No list found; treat as empty value.
            fm[key] = ""
            i += 1
            continue
        # Plain scalar.
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
    audience = fm.get("audience", []) or []
    works_with = fm.get("works_with", []) or []
    scenarios_raw = fm.get("scenarios", []) or []
    quickstart_raw = fm.get("quickstart", []) or []
    # Normalize types — _split_inline_list returns list[str], block list returns list[dict|str].
    if isinstance(audience, str):
        audience = [audience] if audience else []
    if isinstance(works_with, str):
        works_with = [works_with] if works_with else []
    scenarios: list[dict] = []
    for s in scenarios_raw if isinstance(scenarios_raw, list) else []:
        if isinstance(s, dict):
            scenarios.append({
                "intent": s.get("intent", ""),
                "trigger_phrase": s.get("trigger_phrase", ""),
                "outcome": s.get("outcome", ""),
                "difficulty": s.get("difficulty", "starter"),
            })
    quickstart: list[str] = []
    if isinstance(quickstart_raw, list):
        for q in quickstart_raw:
            if isinstance(q, str):
                quickstart.append(q)
    return Item(
        name=fm.get("name", path.stem),
        description=fm.get("description", ""),
        extra={"tools": fm.get("tools", ""), "model": fm.get("model", "")},
        path=str(path.relative_to(REPO_ROOT)),
        audience=audience,
        works_with=works_with,
        scenarios=scenarios,
        quickstart=quickstart,
    )


def git_last_updated(plugin_dir: Path) -> str:
    """Return the YYYY-MM-DD of the most recent commit that touched this plugin dir."""
    try:
        rel = str(plugin_dir.relative_to(REPO_ROOT))
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", rel],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        pass
    return ""


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

    plugin.last_updated = git_last_updated(plugin_dir)
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


def _render_scenarios_block(scenarios: list[dict]) -> str:
    if not scenarios:
        return ""
    starter = next((s for s in scenarios if s.get("difficulty") == "starter"), scenarios[0])
    others = [s for s in scenarios if s is not starter]

    def fmt(s: dict) -> str:
        intent = esc(s.get("intent", ""))
        trig = esc(s.get("trigger_phrase", ""))
        outcome = esc(s.get("outcome", ""))
        difficulty = esc(s.get("difficulty", "starter"))
        return (
            f'<div class="scenario" data-difficulty="{difficulty}">'
            f'<div class="scenario-intent"><strong>Intent:</strong> {intent}</div>'
            f'<div class="scenario-trigger"><strong>You type:</strong> <code>{trig}</code></div>'
            f'<div class="scenario-outcome"><strong>You get:</strong> {outcome}</div>'
            f'<span class="scenario-badge difficulty-{difficulty}">{difficulty}</span>'
            f"</div>"
        )

    starter_html = fmt(starter)
    if not others:
        return f'<div class="scenarios"><h5>Example scenario</h5>{starter_html}</div>'
    others_html = "".join(fmt(o) for o in others)
    return (
        f'<div class="scenarios"><h5>Example scenarios <span class="count">({len(scenarios)})</span></h5>'
        f"{starter_html}"
        f'<details class="more-scenarios"><summary>+ {len(others)} more</summary>{others_html}</details>'
        f"</div>"
    )


def _render_quickstart_block(quickstart: list[str]) -> str:
    if not quickstart:
        return ""
    items = "".join(f"<li>{esc(q)}</li>" for q in quickstart)
    return f'<div class="quickstart"><h5>Quickstart</h5><ol>{items}</ol></div>'


def _render_works_with_block(works_with: list[str]) -> str:
    if not works_with:
        return ""
    chips = "".join(f'<span class="ww-chip">{esc(w)}</span>' for w in works_with)
    return f'<div class="works-with"><h5>Works well with</h5>{chips}</div>'


def _render_audience_block(audience: list[str]) -> str:
    if not audience:
        return ""
    chips = "".join(
        f'<span class="aud-chip" data-audience="{esc(a)}">{esc(AUDIENCE_LABELS.get(a, a))}</span>'
        for a in audience
    )
    return f'<div class="audience">{chips}</div>'


def render_item_card(item: Item, kind: str) -> str:
    extras = []
    for k, v in item.extra.items():
        if v:
            extras.append(f'<span class="extra-pill" data-kind="{esc(k)}">{esc(k)}: {esc(v)}</span>')
    extra_html = " ".join(extras)
    path_html = f'<div class="item-path">{esc(item.path)}</div>' if item.path else ""

    # Agent-only enrichment blocks.
    audience_html = _render_audience_block(item.audience) if kind == "agent" else ""
    scenarios_html = _render_scenarios_block(item.scenarios) if kind == "agent" else ""
    quickstart_html = _render_quickstart_block(item.quickstart) if kind == "agent" else ""
    works_with_html = _render_works_with_block(item.works_with) if kind == "agent" else ""

    # Build a richer search index for agents (include intents).
    search_blob = (item.name + " " + item.description).lower()
    if item.scenarios:
        search_blob += " " + " ".join(s.get("intent", "") for s in item.scenarios).lower()
    if item.audience:
        search_blob += " " + " ".join(item.audience).lower()
    audience_attr = ",".join(item.audience) if item.audience else ""

    return (
        f'<article class="item" data-kind="{esc(kind)}" data-audience="{esc(audience_attr)}" '
        f'data-search="{esc(search_blob)}">'
        f'<header><h4>{esc(item.name)}</h4>{extra_html}</header>'
        f"{audience_html}"
        f'<p>{esc(item.description) or "<em>(no description)</em>"}</p>'
        f"{scenarios_html}"
        f"{quickstart_html}"
        f"{works_with_html}"
        f"{path_html}"
        f"</article>"
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
    last_updated_html = (
        f'<div class="meta-row"><span class="meta-label">Last updated</span> <code>{esc(plugin.last_updated)}</code></div>'
        if plugin.last_updated else ""
    )
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
        {last_updated_html}
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


def render_use_case_table(plugins: list[Plugin]) -> str:
    """Aggregate every agent's intent fields into an 'I want to...' lookup table.
    This is the headline ask per the deep-researcher's recommendation:
    let users navigate from intent → which agent + plugin to use."""
    rows: list[tuple[str, str, str, str, str]] = []  # (intent, agent, plugin, difficulty, audience)
    for plugin in plugins:
        for agent in plugin.agents:
            for s in agent.scenarios:
                intent = s.get("intent", "").strip()
                if not intent:
                    continue
                difficulty = s.get("difficulty", "starter")
                audience = ", ".join(agent.audience) if agent.audience else ""
                rows.append((intent, agent.name, plugin.name, difficulty, audience))
    if not rows:
        return ""
    rows.sort(key=lambda r: (r[3] != "starter", r[0].lower()))  # starters first, then alpha

    body = "".join(
        f"<tr>"
        f'<td class="intent-cell">{esc(intent)}</td>'
        f'<td><code>{esc(agent)}</code></td>'
        f'<td><a href="#plugin-{esc(pname)}">{esc(pname)}</a></td>'
        f'<td><span class="difficulty difficulty-{esc(diff)}">{esc(diff)}</span></td>'
        f"<td>{esc(audience)}</td>"
        f"</tr>"
        for (intent, agent, pname, diff, audience) in rows
    )
    return f"""
      <h2>I want to…</h2>
      <p class="usecase-help">Use this lookup to navigate from <em>what you're trying to do</em> to <em>which agent + plugin handles it</em>. Sorted starter-first then alphabetically. Filter via the Index / Search tab for deeper search.</p>
      <table class="usecase-table">
        <thead>
          <tr><th>I want to…</th><th>Agent</th><th>Plugin</th><th>Difficulty</th><th>Audience</th></tr>
        </thead>
        <tbody>{body}</tbody>
      </table>
    """


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

    plugin_filter_buttons = (
        f'<button class="plugin-filter-btn active" data-plugin-filter="__all__" '
        f'style="--accent: var(--accent)">All <span class="count">{plugin_count}</span></button>'
        + "".join(
            f'<button class="plugin-filter-btn" data-plugin-filter="{esc(p.name)}" '
            f'style="--accent: {PLUGIN_COLORS.get(p.name, DEFAULT_COLOR)}">{esc(p.name)} '
            f'<span class="count">{len(p.agents) + len(p.skills) + len(p.hooks) + len(p.rules) + len(p.templates)}</span></button>'
            for p in plugins
        )
    )

    plugin_cards = "\n".join(
        f'<section id="plugin-{esc(p.name)}" class="plugin-target" data-plugin="{esc(p.name)}">{render_plugin(p)}</section>'
        for p in plugins
    )

    index_json = render_index(plugins)
    usecase_table_html = render_use_case_table(plugins)

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
    .plugin-filter {{ display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 0.75rem; }}
    .plugin-filter-btn {{
      background: var(--surface); color: var(--muted);
      border: 1px solid var(--border); padding: 0.4rem 0.85rem;
      border-radius: 6px; cursor: pointer;
      font-family: var(--font-sans); font-size: 0.85rem;
      transition: background 0.15s, border-color 0.15s, color 0.15s;
    }}
    .plugin-filter-btn:hover {{ background: var(--surface-2); border-color: var(--accent); color: var(--text); }}
    .plugin-filter-btn.active {{ background: var(--surface-2); border-color: var(--accent); color: var(--accent); }}
    .plugin-filter-btn .count {{ color: var(--muted); margin-left: 0.35rem; font-family: var(--font-mono); font-size: 0.78rem; }}
    .plugin-target.hidden-by-filter {{ display: none; }}
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
    /* Agent enrichment — scenarios, quickstart, works-with, audience */
    .audience {{ display: flex; gap: 0.35rem; flex-wrap: wrap; margin: 0.35rem 0 0.5rem 0; }}
    .aud-chip {{ background: var(--surface); border: 1px solid var(--border); padding: 0.1rem 0.5rem; border-radius: 10px; font-size: 0.72rem; color: var(--muted); }}
    .aud-chip[data-audience="consultant"] {{ border-color: #14b8a6; color: #5eead4; }}
    .aud-chip[data-audience="psm"] {{ border-color: #f59e0b; color: #fbbf24; }}
    .aud-chip[data-audience="dev"] {{ border-color: #3b82f6; color: #93c5fd; }}
    .aud-chip[data-audience="power-platform-maker"] {{ border-color: #8b5cf6; color: #c4b5fd; }}
    .aud-chip[data-audience="data-engineer"] {{ border-color: #06b6d4; color: #67e8f9; }}
    .aud-chip[data-audience="analyst"] {{ border-color: #f59e0b; color: #fcd34d; }}
    .aud-chip[data-audience="compliance"] {{ border-color: #ef4444; color: #fca5a5; }}
    .scenarios, .quickstart, .works-with {{ margin: 0.65rem 0 0.35rem 0; padding-top: 0.5rem; border-top: 1px dashed var(--border); }}
    .scenarios h5, .quickstart h5, .works-with h5 {{ font-size: 0.78rem; color: var(--muted); margin: 0 0 0.35rem 0; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 600; }}
    .scenarios h5 .count {{ font-weight: 400; text-transform: none; letter-spacing: 0; }}
    .scenario {{ background: var(--surface); border: 1px solid var(--border); border-radius: 5px; padding: 0.5rem 0.65rem; margin-bottom: 0.4rem; position: relative; }}
    .scenario-intent {{ font-size: 0.85rem; color: var(--text); margin-bottom: 0.25rem; }}
    .scenario-trigger {{ font-size: 0.78rem; color: var(--muted); margin-bottom: 0.25rem; }}
    .scenario-trigger code {{ font-size: 0.78rem; padding: 1px 4px; }}
    .scenario-outcome {{ font-size: 0.78rem; color: var(--muted); }}
    .scenario-badge {{ position: absolute; top: 0.45rem; right: 0.6rem; font-size: 0.7rem; padding: 0.1rem 0.4rem; border-radius: 3px; text-transform: lowercase; }}
    .difficulty-starter, .difficulty.difficulty-starter {{ background: rgba(20,184,166,0.15); color: #5eead4; }}
    .difficulty-advanced, .difficulty.difficulty-advanced {{ background: rgba(139,92,246,0.15); color: #c4b5fd; }}
    .difficulty-troubleshooting, .difficulty.difficulty-troubleshooting {{ background: rgba(239,68,68,0.15); color: #fca5a5; }}
    details.more-scenarios {{ margin-top: 0.35rem; }}
    details.more-scenarios summary {{ cursor: pointer; font-size: 0.78rem; color: var(--muted); padding: 0.25rem 0; }}
    details.more-scenarios summary:hover {{ color: var(--accent); }}
    .quickstart ol {{ margin: 0; padding-left: 1.25rem; }}
    .quickstart li {{ font-size: 0.82rem; color: var(--muted); margin-bottom: 0.15rem; }}
    .ww-chip {{ display: inline-block; background: var(--surface); border: 1px solid var(--border); padding: 0.1rem 0.5rem; border-radius: 4px; font-size: 0.74rem; font-family: var(--font-mono); color: var(--muted); margin: 0 0.2rem 0.2rem 0; }}
    /* Use-case lookup table on Overview tab */
    .usecase-help {{ color: var(--muted); font-size: 0.88rem; margin-bottom: 0.75rem; }}
    .usecase-table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; margin: 0.5rem 0 1.5rem 0; }}
    .usecase-table th {{ text-align: left; padding: 0.55rem 0.5rem; border-bottom: 1px solid var(--border); color: var(--muted); font-weight: 600; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.03em; }}
    .usecase-table td {{ padding: 0.55rem 0.5rem; border-bottom: 1px solid var(--surface-2); vertical-align: top; }}
    .usecase-table tr:hover {{ background: var(--surface); }}
    .usecase-table .intent-cell {{ max-width: 38ch; }}
    .usecase-table .difficulty {{ display: inline-block; padding: 0.1rem 0.45rem; border-radius: 3px; font-size: 0.72rem; }}
    footer.site {{ text-align: center; padding: 2rem 1rem; color: var(--muted); font-size: 0.85rem; border-top: 1px solid var(--border); margin-top: 3rem; }}
    @media (max-width: 720px) {{
      header.site h1 {{ font-size: 1.2rem; }}
      .item-grid {{ grid-template-columns: 1fr; }}
      .usecase-table .intent-cell {{ max-width: none; }}
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
      {usecase_table_html}
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
    <div class="plugin-filter" role="tablist" aria-label="Filter by plugin">
      {plugin_filter_buttons}
    </div>
    <div class="search-row">
      <input id="plugin-search" type="search" placeholder="Search agents, skills, hooks, rules, templates within the visible plugin(s)…" />
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

  // Plugin-pane per-plugin filter buttons
  const pluginFilterBtns = document.querySelectorAll('.plugin-filter-btn');
  pluginFilterBtns.forEach(btn => {{
    btn.addEventListener('click', () => {{
      const target = btn.dataset.pluginFilter;
      pluginFilterBtns.forEach(b => b.classList.toggle('active', b === btn));
      document.querySelectorAll('.plugin-target').forEach(section => {{
        const match = (target === '__all__') || (section.dataset.plugin === target);
        section.classList.toggle('hidden-by-filter', !match);
      }});
    }});
  }});

  // Plugin-pane search (item-level filter within visible plugin cards)
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
