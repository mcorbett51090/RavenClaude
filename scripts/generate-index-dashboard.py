#!/usr/bin/env python3
"""Generate the redesigned RavenClaude landing dashboard (index.html).

This is the NEW top-level experience: a single self-contained page with a
collapsible sidebar, a top bar (logo / search / quick actions), and five
client-side-routed sections — Home, Discover, Configure, Observe, Learn. It is generated from the live repo so it never drifts from the
catalog:

  - .claude-plugin/marketplace.json          → plugin catalog + versions
  - plugins/*/.claude-plugin/plugin.json      → per-plugin metadata
  - plugins/*/agents/*.md                      → specialist roster (frontmatter)
  - plugins/*/{skills,hooks,commands,...}      → asset tallies
  - plugins/ravenclaude-core/dashboard-schema.json → comfort-posture v5 model

It is the single portal: the comfort-posture dashboard (plugins/ravenclaude-core/
dashboard.html) is folded in natively, and the former repo-guide's catalog
content (per-plugin reference + the 'I want to…' use-case table) is redistributed
into the Marketplace + Resources sections. One document, no iframes.

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
import importlib.util
import json
import re
import sys
from pathlib import Path

# Sibling module holding the self-contained HTML/CSS/JS shell. Importable because
# Python puts this script's directory (scripts/) on sys.path[0] at launch.
from _index_dashboard_template import TEMPLATE as _TEMPLATE

_SCRIPTS_DIR = Path(__file__).resolve().parent


def _load_sibling(filename: str, module_name: str):
    """Import a hyphenated sibling generator (e.g. generate-dashboards.py) as a
    module so we can reuse its render_fragment() to fold its content natively
    into index.html — no iframes, one document."""
    spec = importlib.util.spec_from_file_location(module_name, _SCRIPTS_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod  # register so dataclasses resolve their module
    spec.loader.exec_module(mod)
    return mod

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
        scenarios_raw = fm.get("scenarios") or []
        triggers = []
        scenarios = []
        if isinstance(scenarios_raw, list):
            for sc in scenarios_raw:
                if not isinstance(sc, dict):
                    continue
                if sc.get("trigger_phrase"):
                    triggers.append(sc["trigger_phrase"])
                if sc.get("intent") or sc.get("trigger_phrase"):
                    scenarios.append({
                        "intent": sc.get("intent", ""),
                        "trigger_phrase": sc.get("trigger_phrase", ""),
                        "outcome": sc.get("outcome", ""),
                        "difficulty": sc.get("difficulty", "starter"),
                    })
        quickstart_raw = fm.get("quickstart") or []
        quickstart = [q for q in quickstart_raw if isinstance(q, str)] if isinstance(quickstart_raw, list) else []
        agents.append({
            "name": name,
            "label": _humanize(name),
            "description": _first_sentence(fm.get("description", "")),
            "model": fm.get("model", ""),
            "audience": fm.get("audience", []),
            "works_with": works,
            "triggers": triggers[:3],
            "scenarios": scenarios,
            "quickstart": quickstart,
        })
    return agents


def _heading_desc(path: Path) -> str:
    """First markdown heading text, else first non-marker line — the one-liner the
    catalog cards show for a rule / template / best-practice file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#"):
            return s.lstrip("# ").strip()
    for line in text.splitlines():
        s = line.strip()
        if s and not s.startswith(("---", "```", "<!--", ">")):
            return s[:200]
    return ""


def _scan_md_items(plugin_dir: Path, sub: str, exclude_readme: bool = False) -> list[dict]:
    """[{name, description}] for *.md under plugin_dir/<sub> (rules, best-practices)."""
    d = plugin_dir / sub
    if not d.exists():
        return []
    out = []
    for p in sorted(d.glob("*.md")):
        if not p.is_file():
            continue
        if exclude_readme and p.name.lower() == "readme.md":
            continue
        out.append({"name": p.stem, "description": _heading_desc(p)})
    return out


def _scan_templates(plugin_dir: Path) -> list[dict]:
    """[{name, description}] for templates/ entries (files + folders)."""
    d = plugin_dir / "templates"
    if not d.exists():
        return []
    out = []
    for p in sorted(d.iterdir()):
        if p.is_dir():
            out.append({"name": p.name + "/", "description": "(template folder)"})
        elif p.is_file():
            out.append({"name": p.name, "description": _heading_desc(p) if p.suffix == ".md" else ""})
    return out


def _scan_skills(plugin_dir: Path) -> list[dict]:
    """Index a plugin's skills via SKILL.md frontmatter.

    Returns [{name, label, description}]. Deterministic: sorted glob,
    explicit utf-8. Graceful fallback when frontmatter missing.
    """
    skills_dir = plugin_dir / "skills"
    if not skills_dir.exists():
        return []
    out = []
    for sdir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill_md = sdir / "SKILL.md"
        if not skill_md.exists():
            continue
        block = _split_frontmatter(skill_md.read_text(encoding="utf-8", errors="replace"))
        fm = _parse_frontmatter(block) if block else {}
        name = fm.get("name") or sdir.name
        out.append({
            "name": name,
            "label": _humanize(name),
            "description": _first_sentence(fm.get("description", ""), 200),
        })
    return out


def _scan_hooks(plugin_dir: Path) -> list[dict]:
    """Index a plugin's hooks via hooks.json descriptions.

    Returns [{name, description, event}] from `hooks.json` entries.
    Graceful fallback when hooks.json missing. Deterministic via
    explicit sort on (event, name).
    """
    hooks_json = plugin_dir / "hooks" / "hooks.json"
    if not hooks_json.exists():
        return []
    try:
        data = json.loads(hooks_json.read_text(encoding="utf-8"))
    except Exception:
        return []
    out = []
    hooks_block = data.get("hooks", {})
    for event_name, event_list in hooks_block.items():
        if not isinstance(event_list, list):
            continue
        for entry in event_list:
            for hook in entry.get("hooks", []) or []:
                cmd = hook.get("command", "")
                hook_name = Path(cmd).stem if cmd else ""
                if not hook_name:
                    continue
                out.append({
                    "name": hook_name,
                    "description": hook.get("description", ""),
                    "event": event_name,
                })
    out.sort(key=lambda h: (h["event"], h["name"]))
    return out


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
        skills_idx = _scan_skills(pdir)
        hooks_idx = _scan_hooks(pdir)
        rules_idx = _scan_md_items(pdir, "rules")
        templates_idx = _scan_templates(pdir)
        best_practices_idx = _scan_md_items(pdir, "best-practices", exclude_readme=True)
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
            "skills_index": skills_idx,
            "hooks_index": hooks_idx,
            "rules_index": rules_idx,
            "templates_index": templates_idx,
            "best_practices_index": best_practices_idx,
            "counts": {
                "agents": len(agents),
                "skills": skills,
                "hooks": hooks,
                "commands": commands,
                "templates": templates,
                "knowledge": knowledge,
            },
        })

    # "I want to…" use-case rows — every agent scenario's intent, mapped to the
    # agent + plugin that serves it. Surfaced as a browse-by-intent lookup at the
    # top of the Marketplace section (replaces the retired repo-guide table).
    # Starters first, then alphabetical by intent.
    use_cases: list[dict] = []
    for p in plugins:
        for a in p["agents"]:
            for sc in a.get("scenarios", []):
                intent = (sc.get("intent") or "").strip()
                if not intent:
                    continue
                use_cases.append({
                    "intent": intent,
                    "agent": a["name"],
                    "plugin": p["name"],
                    "plugin_label": p["label"],
                    "difficulty": sc.get("difficulty", "starter"),
                    "audience": ", ".join(a.get("audience", []) or []),
                })
    use_cases.sort(key=lambda r: (r["difficulty"] != "starter", r["intent"].lower()))

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
                "controls": cdef.get("x-controls", ""),
                "rec_individual": cdef.get("x-rec-individual", ""),
                "rec_team": cdef.get("x-rec-team", ""),
                "examples": cdef.get("x-examples", []),
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
        "use_cases": use_cases,
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
             "icon": "sliders", "route": "#/configure"},
            {"id": "use-cases", "label": "Browse by use case",
             "desc": "The 'I want to…' lookup — intent → which agent & plugin",
             "icon": "book", "route": "#/discover"},
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

# Brand mark — inlined at generate-time. Drop the real artwork at this path
# (same filename) and it's picked up automatically on the next build.
_RAVEN_LOGO_PATH = (
    Path(__file__).resolve().parent.parent
    / "plugins" / "ravenclaude-core" / "dashboard-assets" / "brand" / "raven-logo.svg"
)


def _load_raven_logo() -> str:
    # SVG comments (<!-- ... -->) are stripped before inlining: this asset is
    # inlined into BOTH static HTML (the brand-mark span) AND a JS template
    # literal (the onboarding-card render fn) — so any backtick or ${...} in
    # an SVG comment would close the template literal early and kill the entire
    # script block. The comments never render visually; dropping them costs
    # nothing and makes the loader safe regardless of what artwork lands here.
    try:
        raw = _RAVEN_LOGO_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""
    return re.sub(r"<!--.*?-->", "", raw, flags=re.DOTALL).strip()


def _load_shared_tokens_root() -> str:
    """Inline the WHOLE shared-tokens.css file at generate-time.

    Returns the file content verbatim — the `:root { ... }` token block,
    the `[data-theme="dark"]` override block, the component-class section
    (.rc-card, .rc-pill, .rc-shimmer, etc.), and the @keyframes. Each
    surface consumes the tokens directly and the components are available
    where needed (e.g., .rc-shimmer for skeleton loaders).

    Function name preserved for backward-compat with template substitution
    markers (`/*__SHARED_TOKENS__*/`). The previous behavior — extracting
    only the first `:root {}` block — silently dropped the dark-mode CSS
    and component classes (architect+code-reviewer R1, plan v0.103.0).

    Determinism: explicit utf-8; source-order preserved.
    """
    return _SHARED_TOKENS_PATH.read_text(encoding="utf-8")


def _load_fragments() -> dict:
    """Render the dashboard sub-app as a native fragment folded into the single
    index.html document (one portal — no iframes): {css, body, js} with CSS
    scoped under #dash-root, body mounted in a hidden host, JS IIFE-wrapped with
    a window.__dashApp entry point the shell router drives. See
    scripts/_html_merge.py for the mechanics. (The repo-guide/catalog sub-app was
    retired — its content was redistributed natively into the shell's Marketplace
    + Resources sections + the use-case table; see scan_repo's use_cases and the
    rich __openPlugin view.)"""
    gd = _load_sibling("generate-dashboards.py", "generate_dashboards")

    # Dashboard fragment — built from the ravenclaude-core schema (the canonical
    # comfort-posture surface; the standalone page was per-plugin but only core
    # ships a schema today).
    dash_dir = PLUGINS_DIR / "ravenclaude-core"
    dash_schema = json.loads((dash_dir / "dashboard-schema.json").read_text(encoding="utf-8"))
    dash = gd.render_fragment(dash_dir, dash_schema)

    return {"dash": dash}


def render_html(data: dict) -> str:
    template = _TEMPLATE
    shared_tokens = _load_shared_tokens_root()
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = template.replace("/*__SHARED_TOKENS__*/", shared_tokens)
    html = html.replace("/*__RC_DATA__*/", payload)
    html = html.replace("__GENERATED__", data["generated"])
    html = html.replace("__MKT_VERSION__", data["marketplace_version"])
    html = html.replace("__RAVEN_LOGO_SVG__", _load_raven_logo())
    # Fold the dashboard sub-app in natively. Done LAST so the simple __MARKER__
    # substitutions above never touch the (large) fragment payload.
    frag = _load_fragments()
    html = html.replace("/*__DASH_CSS__*/", frag["dash"]["css"])
    html = html.replace("<!--__DASH_BODY__-->", frag["dash"]["body"])
    html = html.replace("/*__DASH_JS__*/", frag["dash"]["js"])
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
        # Compare everything except the volatile generated-timestamp surfaces.
        # THREE surfaces are volatile (forge/index-generator-drift, 2026-06-04):
        #   1. the JSON "generated" field inside window.__RC_DATA__
        #   2. the JSON "generated_date" field (day precision — drifts daily)
        #   3. the footer "Updated <ts> UTC" line (minute precision — without
        #      stripping it, --check false-fails one minute after generation,
        #      turning the freshness gate into a paper tiger)
        #   4. the folded-in catalog's per-plugin "Last updated <git-date>" — a
        #      git-log date that varies between a full clone and CI's shallow
        #      checkout (same variance check-guide-fresh.sh strips). Without this
        #      the gate false-fails on a shallow-checkout CI run.
        def _strip_ts(s: str) -> str:
            s = re.sub(r'"generated":"[^"]*"', '"generated":""', s)
            s = re.sub(r'"generated_date":"[^"]*"', '"generated_date":""', s)
            s = re.sub(r"Updated \d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC", "Updated", s)
            s = re.sub(r"(Last updated</span> <code>)[^<]*(</code>)", r"\1\2", s)
            return s
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
