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
        install_html=_render_install_tab(),
        simulator_html=_render_simulator_tab(),
        learn_html=_render_learn_tab(plugin_dir),
        commands_html=_render_stub_tab("Commands", "v0.2.0"),
        trees_html=_render_stub_tab("Decision trees", "v0.2.0"),
        activity_html=_render_stub_tab("Activity", "v0.2.0"),
        schema_json=json.dumps(schema, indent=2),
        concepts_json=_concepts_json(plugin_dir),
        pattern_explanations_json=json.dumps(
            PATTERN_EXPLANATIONS, indent=2, sort_keys=True
        ),
        js=_JS,
    )


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
        "install",
        "Install (wire the bridge)",
        "bash scripts/ravenclaude install",
    ),
    (
        "launch",
        "Launch Copilot with the plugin",
        "copilot --plugin-dir plugins/ravenclaude-core/copilot",
    ),
    (
        "update",
        "Update (re-sync after a marketplace pull)",
        "bash scripts/ravenclaude update",
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

    return _SETTINGS_TAB_TEMPLATE.format(
        preset_buttons="".join(preset_buttons),
        design_checkins=design_checkins_html,
        thing_preview=_render_thing_preview(),
        command_review_panel=_render_command_review_panel(),
        category_groups="".join(group_html_parts),
        security_deny=security_deny_html,
    )


def _render_thing_preview() -> str:
    """Render the 'Command review (the Thing)' panel.

    Live (tribunal T3) for three categories — shell_readonly, shell_remote_mutate,
    shell_code_exec — with the full panel (three seats + a tie-breaker) and the
    EDIT verdict. The copy stays honest about cost and about which categories are
    clickable vs. still disabled previews.
    """
    return (
        '<div class="thing-preview">'
        '<div class="thing-preview-head">'
        '<h3>&#9878; Command review <span class="thing-aka">(the Thing)</span>'
        '<span class="preview-pill">Early access</span></h3>'
        "</div>"
        "<p>When turned on for a category, commands that would otherwise stop to "
        "<strong>ask you</strong> get adjudicated by reviewer agents instead &mdash; a "
        "security seat (Forseti), a correctness seat (Mímir), and an injection-watch seat "
        "(Heimdall) with an architect tie-breaker (Thor), voting "
        "<strong>allow / edit / deny</strong>. A seat may <em>rewrite</em> a risky command into a "
        "safe one (the rewrite is re-validated against the concern catalog before it runs). You are "
        "only interrupted if they can&rsquo;t decide, and every verdict is logged. It can only ever "
        "resolve the <em>ask</em> cases &mdash; it never relaxes the Danger Zone floor.</p>"
        '<p class="thing-preview-note"><strong>Live for three categories &mdash; '
        "<code>shell_readonly</code>, <code>shell_remote_mutate</code>, and "
        "<code>shell_code_exec</code>.</strong> Their toggles below are clickable; the rest stay "
        "disabled previews. The panel runs its seats in parallel, so a typical verdict lands in "
        "<strong>seconds &mdash; but it spends credits on every reviewed command</strong>, so treat "
        "it as a high-stakes guard, not a daily setting &mdash; off by default. Tune the seat models "
        "and confidence below. Design: "
        '<a href="../../docs/tribunal-review-feature-design.md" target="_blank" '
        'rel="noopener">tribunal-review-feature-design.md</a> &middot; the rules it enforces: '
        '<a href="knowledge/concerns-catalog.md" target="_blank" rel="noopener">concern catalog</a>.</p>'
        "</div>"
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
    """Render the GLOBAL command-review panel config (per-seat model + threshold).

    Modeled on the global `design_checkins` flag (not the per-category override
    map): the JS keeps a single `state.command_review` object, persists it to
    localStorage, and serializes a top-level `command_review:` block into the
    emitted comfort-posture.yaml — which the tribunal backend reads with higher
    precedence than a hand-edited thing.yaml. There is no YAML parse-back, so on
    a fresh load the controls show defaults until the user saves (identical to
    the per-category `thing:` toggle's behavior).
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
    return (
        '<div class="command-review-panel" id="command-review-panel">'
        '<div class="crp-head"><h3>&#9878; Command-review panel</h3>'
        '<p class="crp-sub">Which model fills each seat, and how unsure a seat may be before the '
        "tie-breaker is convened. Applies wherever a category&rsquo;s review toggle (above) is on.</p>"
        '<span class="crp-hydrated" id="crp-hydrated-indicator" hidden>'
        "&#10003; Loaded from <code>.ravenclaude/comfort-posture.yaml</code></span>"
        "</div>"
        + _render_gate_floor()
        + f'<div class="crp-seats">{seats_html}</div>'
        '<label class="crp-threshold" for="cr-threshold">'
        "<span class=\"crp-threshold-label\">Confidence threshold</span>"
        '<input type="number" id="cr-threshold" min="0" max="1" step="0.05" value="0.5">'
        '<span class="crp-hint">A seat that votes below this convenes Thor.</span>'
        "</label>"
        + _render_tier_panel()
        + "</div>"
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
            f"</div>"
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
        f"</details>"
    )


def _render_layer_radios(name: str, layer: str, default_value: str = "inherit") -> str:
    """Render one layer row (User / Local / Project) inside an expanded card.

    Each row is a WAI-ARIA radiogroup with four options: allow / ask / deny / inherit.
    Arrow keys cycle within the group; Space selects (native radio behavior).
    """
    layer_id = f"layer-{name}-{layer}"
    values = [
        ("allow", "allow"),
        ("ask", "ask"),
        ("deny", "deny"),
        ("inherit", "inherit"),
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
        f"</div>"
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
        f'</summary>'
        f'<div class="cat-card-body">'
        f'<div class="cat-project-warn" data-warn-for="{html.escape(name)}" hidden>'
        f'<span class="warn-icon" aria-hidden="true">&#9888;</span> '
        f'Project-layer allows are granted to the whole team and cannot be relaxed by personal layers.'
        f'</div>'
        + user_row
        + local_row
        + project_row
        + _render_pattern_overrides(name)
        + _render_thing_toggle(name)
        + "</div>"
        f"</details>"
    )


# Categories whose command-review orchestrator is wired end-to-end, so the
# toggle is clickable (not a button that lies). T2 ships shell_readonly only.
THING_LIVE_CATEGORIES = {"shell_readonly", "shell_remote_mutate", "shell_code_exec"}


def _render_thing_toggle(name: str) -> str:
    """Render the per-category 'Command review' toggle.

    Clickable for the categories proven end-to-end (T2: shell_readonly) — it
    writes `thing: on` into the category's YAML; a disabled 'Preview' switch
    elsewhere keeps the 'coming soon' status legible where the control will live.
    """
    if name in THING_LIVE_CATEGORIES:
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
        f'<section class="danger-zone">'
        f'<header class="danger-zone-header">'
        f'<h3 class="danger-zone-title">Danger Zone'
        f'<button type="button" class="info-btn info-btn-section" '
        f'data-info-section="security_deny" '
        f'aria-label="Explain the Danger Zone" '
        f'title="Explain the Danger Zone">?</button>'
        f'</h3>'
        f'<p class="danger-zone-subtitle">'
        f'The following patterns are ALWAYS denied, regardless of category levels. '
        f'Unblock individual rules at your own risk.'
        f'</p>'
        f'<div class="danger-zone-note">'
        f'<p><strong>These are preventive guardrails, not a malware scanner.</strong> '
        f'They block the common <em>routes</em> malware and damage travel through &mdash; '
        f'running remote scripts (<code>curl | sh</code>), gaining root (<code>sudo</code>), '
        f'wiping files, and reading secrets &mdash; and they stop the command <em>before</em> it runs.</p>'
        f'<p><strong>What they don&rsquo;t do:</strong> inspect a file&rsquo;s contents &mdash; so they cannot '
        f'catch malware hidden inside something you explicitly approve. Treat the floor as a seatbelt, '
        f'not a reason to skip reviewing what Claude produced.</p>'
        f'<p class="danger-zone-note-maint">The floor and the hooks behind it '
        f'(<code>guard-destructive</code> blocks destructive shell commands, <code>enforce-layout</code> '
        f'blocks off-pattern file writes) are maintained in the RavenClaude marketplace and periodically '
        f're-reviewed by the Researcher meta-skill, which adds new dangerous patterns here as they emerge. '
        f'Learn more: '
        f'<a href="https://code.claude.com/docs/en/settings" target="_blank" rel="noopener">Claude Code permissions</a> &middot; '
        f'<a href="https://code.claude.com/docs/en/hooks" target="_blank" rel="noopener">how hooks work</a> &middot; '
        f'<a href="rules/security.md" target="_blank" rel="noopener">this plugin&rsquo;s security rules</a>.</p>'
        f'</div>'
        f'</header>'
        f'<div class="danger-zone-list">'
        + "".join(rows)
        + "</div>"
        f"</section>"
    )


def _label_for(value: str) -> str:
    """Render an enum value as a short pill label (Title Case, spaces not hyphens)."""
    return " ".join(part.capitalize() for part in value.replace("_", " ").split("-"))


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
.preset-btn.preset-ask { border-left-color: var(--warn); }
.preset-btn.preset-allow { border-left-color: var(--accent); }
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

/* ── v5 Per-layer expandable cards ──────────────────────────────── */
.cat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  margin: 0 0 8px;
  overflow: hidden;
}
.cat-card[open] {
  border-color: var(--accent);
}
.cat-card-summary {
  display: grid;
  grid-template-columns: 20px 1fr auto auto;
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
.cat-card-badge.badge-allow { border-color: #22c55e; color: #22c55e; background: rgba(34,197,94,0.08); }
.cat-card-badge.badge-ask { border-color: var(--warn); color: var(--warn); background: rgba(251,191,36,0.08); }
.cat-card-badge.badge-deny { border-color: var(--danger); color: var(--danger); background: rgba(239,68,68,0.08); }
.cat-card-badge.badge-inherit { border-color: var(--border); color: var(--muted); }

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
.install-prereqs,
.install-wiring {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text);
}
.install-prereqs li::marker,
.install-wiring li::marker { color: var(--accent); }
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
.run-result-badge.badge-ok { color: var(--bg); background: var(--accent); }
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
.sim-tier-badge.tier-low { border-color: #22c55e; color: #22c55e; background: rgba(34, 197, 94, 0.08); }
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
  border-radius: var(--radius); padding: 16px 18px; scroll-margin-top: 16px;
}
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

@keyframes rc-flash {
  0% { box-shadow: 0 0 0 2px var(--accent); }
  100% { box-shadow: 0 0 0 0 transparent; }
}
.concept-card.rc-flash { animation: rc-flash 1.2s ease-out; }
@media (prefers-reduced-motion: reduce) {
  .concept-card.rc-flash { animation: none; }
  .concept-cat-head::before { transition: none; }
}
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
    {category_groups}
    {command_review_panel}
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
        Save-to-repo needs the local server. Start it with <code>python3 scripts/serve-dashboards.py</code> and open the forwarded URL. Until then, the alternatives below work.
      </p>
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
    <h2>Wire RavenClaude into GitHub Copilot CLI</h2>
    <p>
      This bridges the RavenClaude plugins &mdash; their agents, skills, hooks, and
      MCP servers &mdash; into the <code>copilot</code> CLI so they work the same way
      they do in Claude Code.
    </p>
    <h3>Prerequisites</h3>
    <ul class="install-prereqs">
      <li>A local checkout of this marketplace (you are looking at its dashboard).</li>
      <li>The <code>copilot</code> CLI on your <code>PATH</code>.</li>
    </ul>
    <h3>What gets wired</h3>
    <ul class="install-wiring">
      <li><strong>Agents</strong> &mdash; launched via <code>copilot --plugin-dir plugins/ravenclaude-core/copilot</code>.</li>
      <li><strong>Skills</strong> &mdash; linked into <code>.claude/skills</code>.</li>
      <li><strong>Hooks</strong> &mdash; linked into <code>.github/hooks</code>.</li>
      <li><strong>MCP servers</strong> &mdash; merged into <code>~/.copilot/mcp-config.json</code>.</li>
    </ul>
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


_SIMULATOR_TAB_TEMPLATE = """
<div class="sim-layout">
  <section class="sim-intro">
    <h2>Test a command</h2>
    <p>
      Type any shell command and see <strong>what the Thing would do with it</strong> &mdash;
      which category it lands in, the risk tier, which reviewer seats convene, the concerns
      it cites, and whether it would be surfaced to you, auto-decided, or denied outright.
      This runs the <strong>real command-review engine</strong> (no execution, no model calls
      &mdash; just the deterministic screen + routing), so it matches what the hook does.
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
    forseti: "claude-opus-4-7",
    mimir: "claude-haiku-4-5",
    heimdall: "claude-haiku-4-5",
    thor: "claude-opus-4-7",
    confidence_threshold: 0.5,
    gate_floor: "high",
  });
  const CR_SEATS = ["forseti", "mimir", "heimdall", "thor"];
  const CR_MODELS = ["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5"];

  /* gate_floor headline control — enum medium | high | extreme, default high. */
  const GATE_FLOORS = ["medium", "high", "extreme"];

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
    command_review: Object.assign({}, CR_DEFAULT, { tiers: freshTiers() }),
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
      /* command-review panel: keep only known seats/models + a valid threshold */
      if (parsed.command_review && typeof parsed.command_review === "object") {
        const pcr = parsed.command_review;
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
  }
  syncDomToState();

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
  }

  /* ── YAML emit (v5 schema) ───────────────────────────────────────── */
  function quoteYamlKey(s) {
    return `"${s.replace(/\\/g, "\\\\").replace(/"/g, "\\\"")}"`;
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
    const crChanged = CR_SEATS.some(s => cr[s] !== CR_DEFAULT[s])
      || cr.confidence_threshold !== CR_DEFAULT.confidence_threshold
      || cr.gate_floor !== CR_DEFAULT.gate_floor
      || tiersChanged;
    if (crChanged) {
      lines.push("# Command-review tribunal panel (the Thing). Overrides .ravenclaude/thing.yaml.");
      lines.push("command_review:");
      lines.push("  panel:");
      for (const s of CR_SEATS) {
        lines.push(`    ${s}:`);
        lines.push(`      model: ${cr[s]}`);
      }
      lines.push(`  confidence_threshold: ${cr.confidence_threshold}`);
      lines.push(`  gate_floor: ${cr.gate_floor}`);
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
      flagUnsaved();
      render();
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
      if (j.applied) {
        setStatus(`saved & applied to settings.json`, "status-saved");
        toast(`Saved ${j.saved} and applied to .claude/settings.json`);
        if (j.apply_summary) console.info("set-posture:\n" + j.apply_summary);
      } else if (j.apply_error) {
        // The YAML saved, but the translator failed — surface it, don't swallow it.
        setStatus(`saved, but apply failed — see console`, "status-error");
        toast(`Saved ${j.saved}, but settings.json was NOT updated`);
        console.error("set-posture apply failed:", j.apply_error);
      } else {
        setStatus(`saved to ${j.saved}`, "status-saved");
        toast(`Saved to ${j.saved} (${j.bytes} bytes)`);
      }
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
        const range = document.createRange();
        range.selectNodeContents(code);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
        toast("Select-all + Cmd/Ctrl+C to copy");
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
        headers: { "Content-Type": "application/json" },
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
        headers: { "Content-Type": "application/json" },
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
      simGateText.textContent = "Could not reach the engine — see console.";
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
  const validTabs = ["settings", "install", "simulator", "learn", "commands", "trees", "activity"];
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
  function applyHash() {
    const seg = (location.hash || "#/settings").replace(/^#\//, "").split("/");
    const tab = validTabs.includes(seg[0]) ? seg[0] : "settings";
    document.querySelectorAll(".tab-btn").forEach(b => {
      const sel = b.dataset.tab === tab;
      b.setAttribute("aria-selected", sel ? "true" : "false");
    });
    document.querySelectorAll(".tab-panel").forEach(p => {
      p.classList.toggle("active", p.dataset.tab === tab);
    });
    if (tab === "learn" && seg[1]) openConcept(seg[1]);
  }
  document.querySelectorAll(".tab-btn").forEach(b => {
    b.addEventListener("click", () => {
      location.hash = "/" + b.dataset.tab;
    });
  });
  window.addEventListener("hashchange", applyHash);
  applyHash();

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
    <button class="tab-btn" data-tab="install" role="tab" aria-selected="false">Install &amp; Update</button>
    <button class="tab-btn" data-tab="simulator" role="tab" aria-selected="false">Test a command</button>
    <button class="tab-btn" data-tab="learn" role="tab" aria-selected="false">Learn</button>
    <button class="tab-btn" data-tab="commands" role="tab" aria-selected="false">Commands</button>
    <button class="tab-btn" data-tab="trees" role="tab" aria-selected="false">Trees</button>
    <button class="tab-btn" data-tab="activity" role="tab" aria-selected="false">Activity</button>
  </nav>
</header>

<main>
  <section class="tab-panel active" data-tab="settings" role="tabpanel" aria-label="Settings">
{settings_html}
  </section>
  <section class="tab-panel" data-tab="install" role="tabpanel" aria-label="Install and Update">
{install_html}
  </section>
  <section class="tab-panel" data-tab="simulator" role="tabpanel" aria-label="Test a command">
{simulator_html}
  </section>
  <section class="tab-panel" data-tab="learn" role="tabpanel" aria-label="Learn">
{learn_html}
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
