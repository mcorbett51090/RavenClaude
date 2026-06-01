#!/usr/bin/env python3
"""Generate the redesigned RavenClaude landing dashboard (index.html).

This is the NEW top-level experience: a single self-contained page with a
collapsible sidebar, a top bar (logo / search / quick actions), and five
client-side-routed sections — Home, Team, Marketplace, Configuration,
Resources. It is generated from the live repo so it never drifts from the
catalog:

  - .claude-plugin/marketplace.json          → plugin catalog + versions
  - plugins/*/.claude-plugin/plugin.json      → per-plugin metadata
  - plugins/*/agents/*.md                      → specialist roster (frontmatter)
  - plugins/*/{skills,hooks,commands,...}      → asset tallies
  - plugins/ravenclaude-core/dashboard-schema.json → comfort-posture v5 model

It deliberately does NOT replace the deep tools that already exist
(repo-guide.html, the comfort-posture dashboard at plugins/ravenclaude-core/
dashboard.html). The redesigned shell links through to them where the heavy,
already-built functionality lives. This keeps all existing functionality intact
while delivering the new information architecture.

Usage:
    python3 scripts/generate-index-dashboard.py            # writes ./index.html
    python3 scripts/generate-index-dashboard.py --check    # verify up to date
    python3 scripts/generate-index-dashboard.py -o out.html

No third-party dependencies are required; PyYAML is used opportunistically for
agent-frontmatter parsing and falls back to a tolerant line parser when absent.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

# Sibling module holding the self-contained HTML/CSS/JS shell. Importable because
# Python puts this script's directory (scripts/) on sys.path[0] at launch.
from _index_dashboard_template import TEMPLATE as _TEMPLATE

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
SCHEMA_PATH = PLUGINS_DIR / "ravenclaude-core" / "dashboard-schema.json"
DEFAULT_OUT = REPO_ROOT / "index.html"

# ----------------------------------------------------------------------------
# Marketplace category taxonomy (the Marketplace section's left sub-nav).
# Any plugin not listed here falls through to "Specialized".
# ----------------------------------------------------------------------------
CATEGORIES: list[dict] = [
    {
        "id": "core-orchestration",
        "label": "Core & Orchestration",
        "icon": "hub",
        "blurb": "The domain-neutral foundation every other plugin builds on — "
        "the Team Lead, delivery management, and the protocols.",
        "plugins": ["ravenclaude-core", "project-management"],
    },
    {
        "id": "microsoft",
        "label": "Microsoft Ecosystem",
        "icon": "windows",
        "blurb": "Power Platform, Azure, Fabric, Graph, and M365 Copilot "
        "specialist teams.",
        "plugins": [
            "power-platform",
            "azure-cloud",
            "microsoft-fabric",
            "microsoft-graph",
            "microsoft-365-copilot",
        ],
    },
    {
        "id": "enterprise",
        "label": "Enterprise Platforms",
        "icon": "building",
        "blurb": "Salesforce delivery craft and Claude application engineering.",
        "plugins": ["salesforce", "claude-app-engineering"],
    },
    {
        "id": "web-design",
        "label": "Web & Design",
        "icon": "palette",
        "blurb": "Design, build, accessibility, performance, and SEO for the web.",
        "plugins": ["web-design"],
    },
    {
        "id": "data-analytics",
        "label": "Data & Analytics",
        "icon": "chart",
        "blurb": "Embedded analytics, BI, and the statistics layer that asks "
        "'is it real?'",
        "plugins": ["data-platform", "tableau", "applied-statistics"],
    },
    {
        "id": "finance-compliance",
        "label": "Finance & Compliance",
        "icon": "shield",
        "blurb": "Corporate finance / FP&A and the financial-regulatory lane.",
        "plugins": ["finance", "regulatory-compliance"],
    },
    {
        "id": "specialized",
        "label": "Specialized",
        "icon": "sparkle",
        "blurb": "Vertical and cross-tool plugins that don't fit the buckets above.",
        "plugins": ["edtech-partner-success", "ai-coding-model-guidance"],
    },
]

# Comfort-posture preset profiles surfaced in the Configuration section. Each
# maps the 12 v5 categories to a deny/ask/allow level. Faithful to the v5 model
# read from dashboard-schema.json; the four named profiles requested by the
# product brief.
POSTURE_PRESETS: list[dict] = [
    {
        "id": "strict_production",
        "label": "Strict Production",
        "blurb": "Maximum guardrails. Reads inside the project run free; every "
        "mutation and anything that leaves the repo pauses or is blocked.",
        "design_checkins": True,
        "global_default": "ask",
        "levels": {
            "file_read_project": "allow",
            "file_read_global": "ask",
            "file_edit_project": "ask",
            "file_edit_global": "deny",
            "shell_readonly": "allow",
            "shell_local_mutate": "ask",
            "shell_remote_mutate": "deny",
            "shell_code_exec": "ask",
            "shell_package_install": "ask",
            "network_read": "allow",
            "network_write": "deny",
            "mcp_tools": "ask",
        },
    },
    {
        "id": "client_delivery",
        "label": "Client Delivery",
        "blurb": "The recommended balance. Local development runs without "
        "prompts; anything reaching outside the repo prompts first.",
        "design_checkins": True,
        "global_default": "ask",
        "levels": {
            "file_read_project": "allow",
            "file_read_global": "ask",
            "file_edit_project": "allow",
            "file_edit_global": "ask",
            "shell_readonly": "allow",
            "shell_local_mutate": "allow",
            "shell_remote_mutate": "ask",
            "shell_code_exec": "ask",
            "shell_package_install": "ask",
            "network_read": "allow",
            "network_write": "ask",
            "mcp_tools": "ask",
        },
    },
    {
        "id": "exploratory",
        "label": "Exploratory",
        "blurb": "Fast iteration on a throwaway or solo repo. Most actions run "
        "freely; only writes that leave the repo still pause.",
        "design_checkins": False,
        "global_default": "allow",
        "levels": {
            "file_read_project": "allow",
            "file_read_global": "allow",
            "file_edit_project": "allow",
            "file_edit_global": "ask",
            "shell_readonly": "allow",
            "shell_local_mutate": "allow",
            "shell_remote_mutate": "ask",
            "shell_code_exec": "allow",
            "shell_package_install": "allow",
            "network_read": "allow",
            "network_write": "ask",
            "mcp_tools": "allow",
        },
    },
    {
        "id": "maximum_autonomy",
        "label": "Maximum Autonomy",
        "blurb": "Hands-off. Every category is ALLOW — the always-on security "
        "floor is the only thing left blocking. Use with care.",
        "design_checkins": False,
        "global_default": "allow",
        "levels": dict.fromkeys([
            "file_read_project", "file_read_global", "file_edit_project",
            "file_edit_global", "shell_readonly", "shell_local_mutate",
            "shell_remote_mutate", "shell_code_exec", "shell_package_install",
            "network_read", "network_write", "mcp_tools",
        ], "allow"),
    },
]

# Always-on deny floor (layer-independent). Mirrors the balanced seed +
# .claude/settings.json deny rules; shown read-only in the editor so users see
# what a preset can never relax.
SECURITY_FLOOR: list[str] = [
    "Bash(rm -rf:*)", "Bash(git push --force:*)", "Bash(git push -f:*)",
    "Bash(git reset --hard:*)", "Bash(git clean -fd:*)", "Bash(npm publish:*)",
    "Bash(curl * | sh)", "Bash(curl * | bash)", "Bash(sudo:*)",
    "Bash(mkfs:*)", "Bash(shred:*)", "Bash(git branch -D:*)",
    "Read(.env)", "Read(.env.*)", "Read(**/*.pem)", "Read(**/*.key)",
    "Read(**/credentials*)", "Read(**/secrets*)", "Read(~/.ssh/**)",
    "Read(~/.aws/**)", "Read(~/.azure/**)", "Read(~/.kube/config)",
]

# Collaboration / house rules summarized for the Team section.
COLLAB_RULES: list[dict] = [
    {"title": "Core stays domain-neutral",
     "body": "The ravenclaude-core plugin never absorbs domain specifics. "
     "Power Platform, finance, Salesforce, web, and data each live in their "
     "own plugin and extend core via skills + knowledge, not parallel agents."},
    {"title": "Team Lead dispatches, specialists execute",
     "body": "Requests route through the Team Lead, which selects the "
     "smaller-blast-radius specialist using the dispatch playbooks rather than "
     "keyword-matching the task to a method."},
    {"title": "Structured Output Protocol on every handoff",
     "body": "Agents hand off with a structured envelope so the next agent — "
     "or the human — gets a predictable summary, decisions, and open questions."},
    {"title": "Capability Grounding before 'I can't'",
     "body": "A command-not-found, a 401/403, or an unloaded MCP tool is "
     "evidence about one route — never proof a capability is absent. Load the "
     "sanctioned route and try ≥2 alternatives before reporting blocked."},
    {"title": "Claim grounding & source honesty",
     "body": "Consequential claims cite the this-session check that backs them "
     "or are marked unverified. Confident reasoning errors are treated as as "
     "dangerous as hallucinations."},
    {"title": "Gates are the source of truth",
     "body": "Format, lint, test, layout, and frontmatter gates enforce the "
     "rules. Agents don't restate what CI / hooks already guarantee."},
]


# ----------------------------------------------------------------------------
# Frontmatter parsing
# ----------------------------------------------------------------------------
def _split_frontmatter(text: str) -> str | None:
    """Return the YAML frontmatter block (without the --- fences), or None."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[3:end].lstrip("\n")


def _parse_frontmatter(block: str) -> dict:
    """Parse a frontmatter block. Prefer PyYAML; fall back to a tolerant parser
    that recovers the scalar fields we surface (name, description, model,
    audience, works_with) even when scenarios use complex nesting."""
    try:  # opportunistic — devcontainer has PyYAML, CI may not
        import yaml  # type: ignore

        data = yaml.safe_load(block)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    out: dict = {}
    for line in block.splitlines():
        m = re.match(r"^([a-zA-Z_][\w-]*):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if key in out:
            continue
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            out[key] = [v.strip().strip("'\"") for v in inner.split(",") if v.strip()]
        elif val:
            out[key] = val.strip("'\"")
    return out


def _first_sentence(text: str, limit: int = 200) -> str:
    text = " ".join((text or "").split())
    # cut at the first sentence-ending period followed by a space + capital,
    # otherwise hard-trim.
    m = re.search(r"\.\s+[A-Z]", text)
    if m and m.start() < limit:
        return text[: m.start() + 1]
    return text[:limit].rstrip() + ("…" if len(text) > limit else "")


def _humanize(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").title()


# ----------------------------------------------------------------------------
# Scanning
# ----------------------------------------------------------------------------
def _count_dir(path: Path, kind: str) -> int:
    if not path.exists():
        return 0
    if kind == "dirs":
        return sum(1 for p in path.iterdir() if p.is_dir())
    if kind == "sh":
        return sum(1 for p in path.glob("*.sh"))
    if kind == "md":
        return sum(1 for p in path.glob("*.md"))
    return sum(1 for p in path.rglob("*") if p.is_file())


def _scan_agents(plugin_dir: Path) -> list[dict]:
    agents: list[dict] = []
    adir = plugin_dir / "agents"
    if not adir.exists():
        return agents
    for md in sorted(adir.glob("*.md")):
        block = _split_frontmatter(md.read_text(encoding="utf-8", errors="replace"))
        fm = _parse_frontmatter(block) if block else {}
        name = fm.get("name") or md.stem
        works = fm.get("works_with") or []
        if isinstance(works, str):
            works = [works]
        scenarios = fm.get("scenarios") or []
        triggers = []
        if isinstance(scenarios, list):
            for sc in scenarios:
                if isinstance(sc, dict) and sc.get("trigger_phrase"):
                    triggers.append(sc["trigger_phrase"])
        agents.append({
            "name": name,
            "label": _humanize(name),
            "description": _first_sentence(fm.get("description", "")),
            "model": fm.get("model", ""),
            "audience": fm.get("audience", []),
            "works_with": works,
            "triggers": triggers[:3],
        })
    return agents


def _category_for(plugin_name: str) -> dict:
    for cat in CATEGORIES:
        if plugin_name in cat["plugins"]:
            return cat
    return CATEGORIES[-1]  # Specialized


def scan_repo() -> dict:
    market = json.loads(MARKETPLACE.read_text(encoding="utf-8"))

    plugins: list[dict] = []
    total_agents = 0
    total_skills = 0
    total_hooks = 0

    for entry in market.get("plugins", []):
        name = entry["name"]
        pdir = PLUGINS_DIR / name
        if not pdir.exists():
            continue
        manifest_path = pdir / ".claude-plugin" / "plugin.json"
        manifest = {}
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:
                manifest = {}

        agents = _scan_agents(pdir)
        skills = _count_dir(pdir / "skills", "dirs")
        hooks = _count_dir(pdir / "hooks", "sh")
        commands = _count_dir(pdir / "commands", "md")
        templates = _count_dir(pdir / "templates", "files")
        knowledge = _count_dir(pdir / "knowledge", "files")

        total_agents += len(agents)
        total_skills += skills
        total_hooks += hooks

        cat = _category_for(name)
        plugins.append({
            "name": name,
            "label": _humanize(name),
            "version": entry.get("version") or manifest.get("version", ""),
            "description": entry.get("description", ""),
            "short": _first_sentence(entry.get("description", ""), 160),
            "keywords": (entry.get("keywords") or manifest.get("keywords") or [])[:8],
            "category": cat["id"],
            "category_label": cat["label"],
            "requires": (manifest.get("requires", {}) or {}).get("plugins", []),
            "agents": agents,
            "counts": {
                "agents": len(agents),
                "skills": skills,
                "hooks": hooks,
                "commands": commands,
                "templates": templates,
                "knowledge": knowledge,
            },
        })

    # Load comfort-posture category metadata from the live v5 schema.
    posture_categories: list[dict] = []
    if SCHEMA_PATH.exists():
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cat_props = schema.get("properties", {}).get("categories", {}).get("properties", {})
        for cid, cdef in cat_props.items():
            posture_categories.append({
                "id": cid,
                "title": cdef.get("title") or _humanize(cid),
                "group": cdef.get("x-group", "Other"),
                "description": cdef.get("description", ""),
                "guidance": cdef.get("x-guidance", ""),
                "recommended": cdef.get("x-recommended", "ask"),
            })

    featured = [
        {"title": "Microsoft delivery stack",
         "plugins": ["power-platform", "azure-cloud", "microsoft-fabric"],
         "blurb": "Build, host, and analyze across the Microsoft cloud — "
         "low-code apps, Azure infra, and Fabric data in one team."},
        {"title": "Data-driven product",
         "plugins": ["data-platform", "applied-statistics", "web-design"],
         "blurb": "Ship embedded analytics that are correct, real, and "
         "beautifully presented — engineering, statistics, and design."},
        {"title": "Claude-native application",
         "plugins": ["claude-app-engineering", "ravenclaude-core"],
         "blurb": "Architect a production app on the Claude API / Agent SDK "
         "with the orchestration core underneath."},
        {"title": "Regulated finance shop",
         "plugins": ["finance", "regulatory-compliance"],
         "blurb": "FP&A and financial modeling alongside AML/KYC and "
         "regulatory-reporting craft."},
    ]

    return {
        "generated": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "generated_date": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d"),
        "marketplace_version": market.get("metadata", {}).get("version", ""),
        "stats": {
            "plugins": len(plugins),
            "specialists": total_agents,
            "skills": total_skills,
            "hooks": total_hooks,
        },
        "categories": CATEGORIES,
        "plugins": plugins,
        "featured": featured,
        "posture": {
            "presets": POSTURE_PRESETS,
            "categories": posture_categories,
            "security_floor": SECURITY_FLOOR,
            "levels": ["deny", "ask", "allow"],
        },
        "collab_rules": COLLAB_RULES,
        "quick_actions": [
            {"id": "init-team", "label": "Initialize Team",
             "desc": "Scaffold AGENTS.md, CLAUDE.md & layout via /init-agent-ready",
             "icon": "rocket", "command": "/init-agent-ready"},
            {"id": "posture", "label": "Comfort Posture Editor",
             "desc": "Tune per-category deny / ask / allow permissions",
             "icon": "sliders", "route": "#/configuration"},
            {"id": "repo-guide", "label": "Generate Repo Guide",
             "desc": "Open the full per-agent reference & use-case lookup",
             "icon": "book", "href": "repo-guide.html"},
            {"id": "staging", "label": "Contribution Staging Loop",
             "desc": "Stage a finding into the marketplace via /wrap",
             "icon": "git", "command": "/wrap"},
        ],
    }


# ----------------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------------
_SHARED_TOKENS_PATH = (
    Path(__file__).resolve().parent.parent
    / "plugins" / "ravenclaude-core" / "dashboard-assets" / "shared-tokens.css"
)


def _load_shared_tokens_root() -> str:
    """Read the :root { ... } block from shared-tokens.css and return only
    its inner declarations + the contrast-note comment, ready to inline
    into a surface's <style> block at generate-time. The component-class
    section of shared-tokens.css is not injected here — each surface
    consumes the tokens (CSS custom properties) and applies its own
    structural CSS. Determinism: explicit utf-8, sorted-free (lines kept
    in source order), single trailing newline."""
    text = _SHARED_TOKENS_PATH.read_text(encoding="utf-8")
    # Extract everything from `:root {` through its matching `}` (the first
    # block — shared-tokens.css's authoritative root token declaration).
    start = text.find(":root {")
    if start < 0:
        raise RuntimeError(f"shared-tokens.css missing :root block at {_SHARED_TOKENS_PATH}")
    # Brace-match starting from the `{` after `:root `.
    depth = 0
    i = text.index("{", start)
    body_start = i + 1
    while i < len(text):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[body_start:i].strip("\n") + "\n"
        i += 1
    raise RuntimeError(f"shared-tokens.css :root block is unbalanced at {_SHARED_TOKENS_PATH}")


def render_html(data: dict) -> str:
    template = _TEMPLATE
    shared_tokens = _load_shared_tokens_root()
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = template.replace("/*__SHARED_TOKENS__*/", shared_tokens)
    html = html.replace("/*__RC_DATA__*/", payload)
    html = html.replace("__GENERATED__", data["generated"])
    html = html.replace("__MKT_VERSION__", data["marketplace_version"])
    return html


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate the RavenClaude landing dashboard.")
    ap.add_argument("-o", "--output", type=Path, default=DEFAULT_OUT,
                    help="Output HTML path (default: ./index.html)")
    ap.add_argument("--check", action="store_true",
                    help="Exit non-zero if the output is missing or stale.")
    args = ap.parse_args(argv)

    data = scan_repo()
    html = render_html(data)

    if args.check:
        if not args.output.exists():
            print(f"[stale] {args.output} does not exist", file=sys.stderr)
            return 1
        current = args.output.read_text(encoding="utf-8")
        # Compare everything except the volatile generated-timestamp line.
        def _strip_ts(s: str) -> str:
            return re.sub(r'"generated":"[^"]*"', '"generated":""', s)
        if _strip_ts(current) != _strip_ts(html):
            print(f"[stale] {args.output} is out of date — re-run the generator",
                  file=sys.stderr)
            return 1
        print(f"[ok] {args.output} is up to date")
        return 0

    args.output.write_text(html, encoding="utf-8")
    kb = len(html.encode("utf-8")) / 1024
    print(f"[ok] wrote {args.output} ({kb:.0f} KB) — "
          f"{data['stats']['plugins']} plugins, "
          f"{data['stats']['specialists']} specialists")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
