"""Host-scope chips for dashboard + index portal (dashboard-host-scope-badges).

Extends MH-18 honesty: surface whether a feature is host-agnostic (All agents)
vs a single coding host. Inventory `platform_dependency` is catalog tagging SSOT;
`knowledge/host-support.json` remains capability SSOT. Grok is reserved
(inventory-tagged; not in host-support hosts) — chip/filter only, never claim
supported.

Do NOT invent `_HOST_EQUIVALENTS` verbs here — that map stays verified-only in
generate-dashboards.py.
"""

from __future__ import annotations

import html
import json
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
_MAP_PATH = (
    REPO_ROOT
    / "plugins"
    / "ravenclaude-core"
    / "dashboard-assets"
    / "host-scope-map.json"
)

# Canonical chip table (UX DIGEST 2026-09-15). Keys = inventory platform_dependency
# (plus filter id `all-agents` for host-agnostic).
_SCOPE_META: dict[str, dict[str, str]] = {
    "host-agnostic": {
        "chip": "All agents",
        "tooltip": "All coding agents / host-agnostic",
        "mod": "host-agnostic",
        "filter": "all-agents",
    },
    "claude-code": {
        "chip": "Claude Code",
        "tooltip": "Claude Code only",
        "mod": "host-claude",
        "filter": "claude-code",
    },
    "cursor": {
        "chip": "Cursor",
        "tooltip": "Cursor",
        "mod": "host-cursor",
        "filter": "cursor",
    },
    "codex": {
        "chip": "Codex",
        "tooltip": "OpenAI Codex CLI",
        "mod": "host-codex",
        "filter": "codex",
    },
    "copilot": {
        "chip": "Copilot",
        "tooltip": "GitHub Copilot CLI",
        "mod": "host-copilot",
        "filter": "copilot",
    },
    "gemini": {
        "chip": "Gemini",
        "tooltip": "Gemini CLI",
        "mod": "host-gemini",
        "filter": "gemini",
    },
    "grok": {
        "chip": "Grok",
        "tooltip": "Grok (reserved — not in host-support.json)",
        "mod": "host-grok",
        "filter": "grok",
    },
    "multi": {
        "chip": "Multi",
        "tooltip": "Multiple hosts (see card)",
        "mod": "host-multi",
        "filter": "multi",
    },
    "aider": {
        "chip": "Aider",
        "tooltip": "Aider",
        "mod": "host-aider",
        "filter": "aider",
    },
    "windsurf": {
        "chip": "Windsurf",
        "tooltip": "Windsurf / Devin Desktop",
        "mod": "host-windsurf",
        "filter": "windsurf",
    },
}

# Filter strip order (product copy). Multi optional but included.
FILTER_STRIP: tuple[str, ...] = (
    "all-agents",
    "claude-code",
    "cursor",
    "codex",
    "copilot",
    "grok",
    "gemini",
    "multi",
)

_FILTER_TO_DEP = {v["filter"]: k for k, v in _SCOPE_META.items()}


@lru_cache(maxsize=1)
def _load_map() -> dict:
    if not _MAP_PATH.is_file():
        return {"by_evidence_path": {}, "by_plugin_item": {}}
    try:
        return json.loads(_MAP_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"by_evidence_path": {}, "by_plugin_item": {}}


def resolve_platform_dependency(
    *,
    kind: str,
    plugin: str,
    name: str,
    evidence_path: str | None = None,
    default: str = "claude-code",
) -> str:
    """Join inventory snapshot; else path heuristics; else default.

    Fallback rules (DIGEST): never invent host-agnostic. Slash/agent/skill under
    normal plugin trees default to claude-code. Host-adapter path segments
    (copilot/, codex/, cursor/, gemini/, grok-) map to that host enum.
    """
    data = _load_map()
    by_item = data.get("by_plugin_item") or {}
    by_path = data.get("by_evidence_path") or {}
    key = f"{kind}:{plugin}:{name}"
    if key in by_item:
        return by_item[key]
    if evidence_path:
        ep = evidence_path.replace("\\", "/")
        if ep in by_path:
            return by_path[ep]
        # stem variants
        for cand in (ep, ep.rstrip("/"), ep + "/SKILL.md" if kind == "skill" else ep):
            if cand in by_path:
                return by_path[cand]
        return _derive_from_path(ep, default=default)
    return default


def _derive_from_path(ep: str, *, default: str) -> str:
    low = ep.lower()
    if "/copilot/" in low or low.endswith("/copilot") or "copilot-hook" in low:
        return "copilot"
    if "/codex/" in low or low.endswith("/codex"):
        return "codex"
    if "/cursor/" in low or "cursor-hook" in low:
        return "cursor"
    if "/gemini/" in low or "gemini-hook" in low:
        return "gemini"
    if "/grok-" in low or low.endswith("/grok") or "/grok/" in low:
        return "grok"
    if "/aider/" in low:
        return "aider"
    if "/windsurf/" in low:
        return "windsurf"
    return default


def scope_tokens(dep: str) -> list[str]:
    """Tokens for data-host-scope (space-separated on the card)."""
    meta = _SCOPE_META.get(dep)
    if not meta:
        return [dep]
    return [meta["filter"]]


def render_scope_badge(dep: str) -> str:
    """One .rc-badge host-scope chip (HTML). Unknown dep → neutral Multi-style."""
    meta = _SCOPE_META.get(dep) or {
        "chip": dep,
        "tooltip": dep,
        "mod": "host-multi",
        "filter": dep,
    }
    tip = html.escape(meta["tooltip"], quote=True)
    label = html.escape(meta["chip"])
    mod = html.escape(meta["mod"])
    return (
        f'<span class="rc-badge rc-badge--{mod}" '
        f'title="{tip}" aria-label="{tip}">{label}</span>'
    )


def render_filter_strip(*, strip_id: str = "host-scope-filter") -> str:
    """Sticky/section-top filter chip strip (toggle buttons)."""
    buttons = []
    for fid in FILTER_STRIP:
        dep = _FILTER_TO_DEP[fid]
        meta = _SCOPE_META[dep]
        tip = html.escape(meta["tooltip"], quote=True)
        label = html.escape(meta["chip"])
        buttons.append(
            f'<button type="button" class="rc-host-filter__btn" '
            f'data-host-filter="{html.escape(fid)}" aria-pressed="false" '
            f'title="{tip}" aria-label="{tip}">{label}</button>'
        )
    return (
        f'<div class="rc-host-filter" id="{html.escape(strip_id)}" '
        f'role="group" aria-label="Filter by coding agent">'
        f'{"".join(buttons)}'
        f'<button type="button" class="rc-host-filter__clear" data-host-filter-clear="1" '
        f'hidden>Clear filter</button>'
        f"</div>"
        f'<p class="rc-host-filter__empty" data-host-filter-empty hidden>'
        f"No cards for this host. Clear the filter or pick <strong>All agents</strong> "
        f"for host-agnostic tools.</p>"
    )


# Small JS snippet (string) for filter wiring — inject into initCommands / index.
# Matches cards with [data-host-scope]; All agents filter = host-agnostic only.
FILTER_JS = r"""
function wireHostScopeFilter(root) {
  if (!root) return;
  const strip = root.querySelector(".rc-host-filter");
  if (!strip || strip.dataset.wired === "1") return;
  strip.dataset.wired = "1";
  const empty = root.querySelector("[data-host-filter-empty]");
  const clearBtn = strip.querySelector("[data-host-filter-clear]");
  const cards = () => Array.from(root.querySelectorAll("[data-host-scope]"));
  function selected() {
    return Array.from(strip.querySelectorAll(".rc-host-filter__btn[aria-pressed='true']"))
      .map((b) => b.getAttribute("data-host-filter"));
  }
  function apply() {
    const sel = selected();
    if (clearBtn) clearBtn.hidden = sel.length === 0;
    let visible = 0;
    cards().forEach((card) => {
      const scopes = (card.getAttribute("data-host-scope") || "").split(/\s+/).filter(Boolean);
      let show;
      if (!sel.length) {
        show = true;
      } else if (sel.includes("all-agents") && sel.length === 1) {
        show = scopes.includes("all-agents");
      } else {
        // Host chips: match that host token only (universal NOT auto-included).
        const hosts = sel.filter((s) => s !== "all-agents");
        show = hosts.some((h) => scopes.includes(h));
        if (sel.includes("all-agents")) {
          show = show || scopes.includes("all-agents");
        }
      }
      card.hidden = !show;
      if (show) visible += 1;
    });
    if (empty) empty.hidden = visible !== 0 || !sel.length;
  }
  strip.addEventListener("click", (e) => {
    const clear = e.target.closest("[data-host-filter-clear]");
    if (clear) {
      strip.querySelectorAll(".rc-host-filter__btn").forEach((b) => b.setAttribute("aria-pressed", "false"));
      apply();
      return;
    }
    const btn = e.target.closest(".rc-host-filter__btn");
    if (!btn || !strip.contains(btn)) return;
    const on = btn.getAttribute("aria-pressed") === "true";
    btn.setAttribute("aria-pressed", on ? "false" : "true");
    apply();
  });
  apply();
}
"""
