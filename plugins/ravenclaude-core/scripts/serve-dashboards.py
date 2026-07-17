#!/usr/bin/env python3
"""
serve-dashboards.py — local server for the comfort-posture dashboard (consumer build).

This is the version that ships INSIDE the installed ravenclaude-core plugin so a
consumer can run the *fully-functioning* dashboard (one-click Save & apply) without
cloning the marketplace repo. The `/dashboard` slash command launches it.

How it differs from the marketplace-repo server (`<repo>/scripts/serve-dashboards.py`):
  - **Static files are served from the PLUGIN install dir** (so `/dashboard.html`
    resolves to the version-matched dashboard that shipped with the plugin).
  - **Reads/writes target the CONSUMER's project** (the directory the server is
    launched from = `Path.cwd()`), so `.ravenclaude/comfort-posture.yaml` and
    `.claude/settings.json` land in their project, not in the plugin cache.
  - **No `/__run` endpoint.** The marketplace server exposes a one-click
    `ravenclaude install/update` (shell) for Copilot-bridge dev; that has no place
    in a posture editor a client launches, so it is intentionally absent here. The
    only endpoints are `/__save`, `/__read` (allow-listed to `.ravenclaude/` files)
    and `/__classify` (read-only command-review preview).

Security posture (see also the `security-reviewer` notes in the PR):
  - Binds **127.0.0.1** by default. In a Codespace the forwarded port is **Private**
    by default — keep it that way; `/__save` writes files and runs the translator.
  - `/__save` is allow-listed AND path-traversal-guarded to stay within the project.
  - Static serving is read-only and limited to the plugin dir (public marketplace
    content the user already has). No auth, no multi-user — local single-user only.

Usage (normally via `/dashboard`):
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/serve-dashboards.py"          # port 8000
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/serve-dashboards.py" --port 8080
"""

from __future__ import annotations

import argparse
import errno
import functools
import hmac
import json
import os
import secrets
import signal
import subprocess
import sys
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# The plugin install dir (…/ravenclaude-core/<version>/) — static files come from here.
PLUGIN_DIR = Path(__file__).resolve().parent.parent
# The marketplace checkout root (the dir that contains plugins/). A CONSUMER launcher must
# never target this — the guard in main() refuses an explicit --project-root pointing here,
# so a consumer-repo dashboard can only edit its own repo, never the marketplace.
MARKETPLACE_ROOT = PLUGIN_DIR.parent.parent
# The consumer's project — captured at startup, BEFORE any chdir. Reads/writes go here.
# Overridable with --project-root (the repo-local launcher pins it explicitly so the
# dashboard is correctly scoped regardless of the launch directory).
PROJECT_ROOT = Path.cwd().resolve()

# Pipeline-tab editable config files. JSON-validated before write (a malformed
# write to .repo-layout.json would brick the layout gate, so we never persist
# unparseable JSON or a structurally-wrong layout file).
JSON_EDIT_TARGETS = {
    ".repo-layout.json",
    ".ravenclaude/task-scope.json",
}
# Plain YAML-mapping config files (validated as a mapping before write).
WEB_ACCESS_TARGET = ".ravenclaude/web-access.yaml"
YAML_MAPPING_TARGETS = {WEB_ACCESS_TARGET}
ALLOWED_TARGETS = {
    ".ravenclaude/comfort-posture.yaml",
    ".ravenclaude/environment-context.md",
    WEB_ACCESS_TARGET,
} | JSON_EDIT_TARGETS
ALLOWED_READ = {
    ".ravenclaude/comfort-posture.yaml",
    ".ravenclaude/environment-context.md",
    WEB_ACCESS_TARGET,
} | JSON_EDIT_TARGETS

# Per-plugin variable files written by the dashboard's Plugins tab. The plugin
# name is variable, so these are matched by SHAPE (not an exact whitelist entry):
# .ravenclaude/plugins/<slug>.yaml where <slug> is lowercase alphanumeric+hyphen.
# This stays inside .ravenclaude/plugins/ (no traversal) and is YAML-validated as
# a mapping before write, mirroring the JSON-target defense.
_PLUGIN_CFG_PREFIX = ".ravenclaude/plugins/"


def _is_plugin_config_target(target: str) -> bool:
    if not target.startswith(_PLUGIN_CFG_PREFIX) or not target.endswith(".yaml"):
        return False
    slug = target[len(_PLUGIN_CFG_PREFIX):-len(".yaml")]
    return bool(slug) and all(c.islower() or c.isdigit() or c == "-" for c in slug) \
        and slug[0] != "-" and "/" not in slug and ".." not in slug


def _validate_plugin_config(content: str) -> str | None:
    """Plugin-config files must parse as a YAML mapping (or be empty). Returns an
    error string (→ HTTP 400) or None when safe to persist. If PyYAML isn't
    available, skip validation (don't block the write) — same posture as the
    /__read parsed-form, which treats yaml as optional."""
    if not content.strip():
        return None
    try:
        import yaml  # present in the devcontainer; optional elsewhere
    except ImportError:
        return None
    try:
        doc = yaml.safe_load(content)
    except yaml.YAMLError as e:
        return f"not valid YAML ({e})"
    if doc is not None and not isinstance(doc, dict):
        return "plugin config must be a YAML mapping (key: value pairs)"
    return None


def _validate_json_target(target: str, content: str) -> str | None:
    """Structural pre-write validation for a JSON_EDIT_TARGETS file. Returns an
    error string (→ HTTP 400) or None when the content is safe to persist.

    .repo-layout.json IS the layout security gate, so we require valid JSON whose
    `allowed_globs` is a list — a malformed write would brick layout enforcement.
    task-scope.json must be a JSON object; `in_scope`, when present, must be a list.
    """
    try:
        doc = json.loads(content)
    except (json.JSONDecodeError, TypeError) as e:
        return f"{target}: not valid JSON ({e})"
    if not isinstance(doc, dict):
        return f"{target}: top-level value must be a JSON object"
    if target == ".repo-layout.json":
        if not isinstance(doc.get("allowed_globs"), list):
            return ".repo-layout.json: 'allowed_globs' must be a list"
    if target == ".ravenclaude/task-scope.json":
        if "in_scope" in doc and not isinstance(doc["in_scope"], list):
            return "task-scope.json: 'in_scope', when present, must be a list"
    return None


# Saving the comfort posture immediately re-runs the translator so the consumer's
# .claude/settings.json reflects the new YAML without a manual /set-posture.
POSTURE_TARGET = ".ravenclaude/comfort-posture.yaml"
APPLY_SCRIPT = PLUGIN_DIR / "scripts" / "apply-comfort-posture.py"

# The knowledge-health card under the Look back / Heimdall tab invokes this
# script via subprocess and forwards its JSON. Single source of truth — the same
# script is used by the /knowledge-health skill and the `ravenclaude doctor`
# 7-check.
KNOWLEDGE_HEALTH_SCRIPT = PLUGIN_DIR / "scripts" / "knowledge-health.py"

# POST /__classify powers the dashboard's "Test a command" simulator: it runs the
# REAL deterministic classifier on the typed string (no execution) so the preview
# can't drift from the engine.
THING_DECISION = PLUGIN_DIR / "scripts" / "thing-decision.py"

# ── Tier helpers for /__saga enrichment ─────────────────────────────────────
# Imported once at module start from the plugin's own thing-decision.py /
# thing-concerns.py (single source of truth) so the Review-log tab's tier column
# never drifts from the engine. Any failure degrades gracefully (base "medium").
_THING_CONCERNS_SCRIPT = PLUGIN_DIR / "scripts" / "thing-concerns.py"


def _load_tier_helpers() -> tuple:
    """Return (cat_tier_map, escalate_fn, severity_fn, catalog).

    cat_tier_map  — category → base tier string (from thing-decision.py).
    escalate_fn   — _escalate_tier(base, max_severity) from thing-decision.py.
    severity_fn   — severity(catalog, ids) from thing-concerns.py.
    catalog       — parsed concern catalog dict (from thing-concerns.py).

    Any failure returns a partial result with None for the missing pieces;
    _compute_saga_tiers() falls back gracefully.
    """
    import importlib.util as _ilu

    cat_map: dict = {}
    escalate_fn = None
    severity_fn = None
    catalog = None

    try:
        spec = _ilu.spec_from_file_location("_td_srv", str(THING_DECISION))
        if spec and spec.loader:
            mod = _ilu.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
            cat_map = dict(getattr(mod, "_DEFAULT_CATEGORY_TIER_MAP", {}))
            escalate_fn = getattr(mod, "_escalate_tier", None)
    except Exception:
        pass

    try:
        spec2 = _ilu.spec_from_file_location("_tc_srv", str(_THING_CONCERNS_SCRIPT))
        if spec2 and spec2.loader:
            mod2 = _ilu.module_from_spec(spec2)
            spec2.loader.exec_module(mod2)  # type: ignore[union-attr]
            severity_fn = getattr(mod2, "severity", None)
            load_cat = getattr(mod2, "_load_catalog", None)
            if load_cat:
                try:
                    catalog = load_cat()
                except Exception:
                    catalog = None
    except Exception:
        pass

    return cat_map, escalate_fn, severity_fn, catalog


_SAGA_CAT_TIER_MAP, _SAGA_ESCALATE, _SAGA_SEVERITY, _SAGA_CATALOG = _load_tier_helpers()

# Severity rank used to find max severity among cited concerns.
_SAGA_SEV_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def _compute_saga_tiers(category: str, concerns_cited: list) -> tuple:
    """Return (base_tier, final_tier) for one /__saga log entry.

    base_tier  — from the engine's category→tier map; defaults to "medium".
    final_tier — base_tier bumped by the max severity of concerns_cited using
                 the engine's own _escalate_tier function.
    """
    base = _SAGA_CAT_TIER_MAP.get(category, "medium")
    if not concerns_cited:
        return base, base

    max_sev = None
    if _SAGA_CATALOG is not None:
        by_id: dict = {}
        by_id.update({c["id"]: c for c in (_SAGA_CATALOG.get("cross_cutting") or [])})
        for lst in (_SAGA_CATALOG.get("categories") or {}).values():
            if isinstance(lst, list):
                by_id.update({c["id"]: c for c in lst})
        max_rank = -1
        for cid in concerns_cited:
            rank = _SAGA_SEV_RANK.get(by_id.get(cid, {}).get("severity", ""), -1)
            if rank > max_rank:
                max_rank = rank
                max_sev = by_id[cid].get("severity") if cid in by_id else None

    if _SAGA_ESCALATE is not None:
        try:
            final = _SAGA_ESCALATE(base, max_sev)
        except Exception:
            final = base
    else:
        final = base

    return base, final


DASH_PATH = "/dashboard.html"

# Populated in main(). The state-changing/read endpoints check these so a malicious
# web page the user is viewing can't drive this server cross-origin: a 127.0.0.1
# bind does NOT stop a browser from POSTing to localhost, and a same-site cookie is
# irrelevant here, so CSRF/DNS-rebinding is the real threat. Any request whose Origin
# isn't ours, or whose Host isn't a known local/forwarded host, is rejected; on top of
# that a state-changing request must carry an Origin at all (see
# _state_change_origin_ok — a browser always sends one on a POST, so only a non-browser
# client can omit it). The legit dashboard is same-origin → passes.
_ALLOWED_HOSTS: set[str] = set()
_ALLOWED_ORIGINS: set[str] = set()

# Per-process random CSRF token. Generated in main() once the server is bound.
# Second layer under the Origin check on every state-changing POST: the token is
# exposed via GET /__csrf, which a cross-origin page cannot read (this server sends
# no CORS headers, and the guard rejects a foreign Origin) — so a malicious page can
# neither forge an allowed Origin nor steal the token.
#
# It does NOT stop a local scripted client, and must not be described as if it did.
# Such a client fetches the token from GET /__csrf itself: that bootstrap is a
# same-origin GET, which per the Fetch standard carries no Origin header at all, so
# it cannot be Origin-gated without breaking the dashboard. Any "a scripted client
# that omits Origin still has to present this token" reasoning is CIRCULAR — the
# same open door supplies the key. The honest boundary is in _state_change_origin_ok().
_CSRF_TOKEN: str = ""


def _summarize_run(d: Path) -> dict:
    """Summarize one .ravenclaude/runs/<id>/ directory for the Activity feed.
    Reads summary.md (truncated), the structured-result status, the events line
    count, and which artifact files are present. Reads only under `d` (no root
    reference), so this is byte-identical with the root dev server — keep the two
    copies in sync (the parity gate guards the endpoints, not this helper)."""
    import datetime as _dt

    rec = {"id": d.name, "timestamp": "", "status": "", "summary": "",
           "artifacts": [], "event_count": 0}
    try:
        rec["timestamp"] = _dt.datetime.utcfromtimestamp(
            d.stat().st_mtime
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
    except OSError:
        pass
    for name in ("summary.md", "SUMMARY.md"):
        p = d / name
        if p.is_file():
            rec["artifacts"].append(name)
            try:
                txt = p.read_text(encoding="utf-8").strip()
                rec["summary"] = txt[:400] + ("…" if len(txt) > 400 else "")
            except OSError:
                pass
            break
    for name in ("structured-output.json", "structured-result.json", "result.json"):
        p = d / name
        if p.is_file():
            rec["artifacts"].append(name)
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(obj, dict) and isinstance(obj.get("status"), str):
                    rec["status"] = obj["status"][:40]
            except (OSError, json.JSONDecodeError, ValueError):
                pass
            break
    for name in ("events.jsonl", "actions.log"):
        p = d / name
        if p.is_file():
            rec["artifacts"].append(name)
            try:
                with p.open(encoding="utf-8") as f:
                    rec["event_count"] = sum(1 for line in f if line.strip())
            except OSError:
                pass
            break
    return rec


# Heimdall hook-event tiering. The destructive-guard denials are the
# irrecoverable-action class (red); other denials are amber; warns are grey.
# Kept as a module constant so both server copies classify identically.
_HEIMDALL_RED_RULES = {"destructive-pattern"}


def _heimdall_tier(ev: dict):
    """Map one hook event to a Gjallarhorn tier: red | amber | grey | None.
    red = irrecoverable deny (destructive-guard), amber = other deny,
    grey = warn. allow/unknown verdicts carry no banner (None)."""
    verdict = ev.get("verdict")
    if verdict == "deny":
        return "red" if ev.get("rule") in _HEIMDALL_RED_RULES else "amber"
    if verdict == "warn":
        return "grey"
    return None


def _read_hook_events(runs_dir: Path, days: int = 30, per_hook: int = 10) -> dict:
    """Read .ravenclaude/runs/*/hook-events.jsonl under `runs_dir`, window to the
    last `days`, classify each event's tier, group by hook (cap `per_hook` newest
    each), and surface the highest tier present as the Gjallarhorn banner state.

    Reads only under `runs_dir` (no root reference) so this is byte-identical in
    the root and bundled plugin server — keep the two copies in sync (the parity
    gate guards endpoint NAMES; this helper is duplicated, so edit both). Tolerant
    of torn/garbage lines and missing timestamps (best-effort observability)."""
    import datetime as _dt

    cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=days)

    def _in_window(ev: dict) -> bool:
        ts = ev.get("ts", "")
        try:
            parsed = _dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=_dt.timezone.utc
            )
            return parsed >= cutoff
        except (ValueError, TypeError):
            return True  # keep events we can't date rather than silently drop them

    rows: list[dict] = []
    if runs_dir.is_dir():
        for log in sorted(runs_dir.glob("*/hook-events.jsonl")):
            try:
                with log.open(encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            ev = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if isinstance(ev, dict):
                            rows.append(ev)
            except OSError:
                continue

    rows = [e for e in rows if _in_window(e)]
    rows.sort(key=lambda e: e.get("ts", ""), reverse=True)

    order = {"red": 3, "amber": 2, "grey": 1}
    top = None
    by_hook: dict[str, list] = {}
    for e in rows:
        tier = _heimdall_tier(e)
        if tier and (top is None or order[tier] > order[top]):
            top = tier
        hook = e.get("hook", "unknown")
        bucket = by_hook.setdefault(hook, [])
        if len(bucket) < per_hook:
            enriched = dict(e)
            enriched["tier"] = tier
            bucket.append(enriched)

    return {
        "by_hook": by_hook,
        "total": len(rows),
        "gjallarhorn_tier": top,
        "window_days": days,
    }


# Víðarr — which hook denials count as SECURITY events (vs. operational noise).
# Posture-events are always security-relevant; among hook-events only the deny
# verdicts are (a warn is advisory — it lives in Heimdall's grey tier, not the
# security audit log).
def _vidarr_hook_is_security(ev: dict) -> bool:
    """A hook event belongs in the security log iff it is a deny verdict.
    (destructive-pattern, off-allow-list, forbidden-pattern, task-scope, … —
    every deny is a security-relevant block; warns are excluded.)"""
    return ev.get("verdict") == "deny"


def _read_vidarr_events(runs_dir: Path, posture_log: Path, days: int = 30) -> dict:
    """Build the Víðarr posture/security event log: posture changes
    (`posture-events.jsonl`) interleaved with security-relevant hook denials
    (`hook-events.jsonl`, deny-only), normalized to one chronological shape and
    sorted newest-first. Read-only mirror — surfaces what the substrate emitted.

    Each returned event has: {ts, kind, category, summary, source} where `kind`
    is "posture-change" | "security-deny". Reads only under the given paths (no
    root reference) so this is byte-identical in the root and bundled plugin
    server — keep the two copies in sync (the parity gate guards endpoint NAMES;
    this helper is duplicated, so edit both). Tolerant of torn lines / missing ts.
    """
    import datetime as _dt

    cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=days)

    def _in_window(ts: str) -> bool:
        try:
            parsed = _dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=_dt.timezone.utc
            )
            return parsed >= cutoff
        except (ValueError, TypeError):
            return True

    def _iter_jsonl(path: Path):
        try:
            with path.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(obj, dict):
                        yield obj
        except OSError:
            return

    events: list[dict] = []

    # Posture changes — every one is security-relevant. Summarize the diff.
    if posture_log.is_file():
        for ev in _iter_jsonl(posture_log):
            ts = ev.get("ts", "")
            if not _in_window(ts):
                continue
            sd = ev.get("security_deny_diff") or {}
            ov = ev.get("override_diff") or {}
            parts = []
            for label, diff in (("deny", sd), ("override", ov)):
                added = diff.get("added") or []
                removed = diff.get("removed") or []
                if added:
                    parts.append(f"+{len(added)} {label}")
                if removed:
                    parts.append(f"-{len(removed)} {label}")
            events.append(
                {
                    "ts": ts,
                    "kind": "posture-change",
                    "category": ev.get("scope", ""),
                    "summary": ", ".join(parts) or "posture re-applied",
                    "source": ev.get("source", "unknown"),
                }
            )

    # Security-relevant hook denials.
    if runs_dir.is_dir():
        for log in sorted(runs_dir.glob("*/hook-events.jsonl")):
            for ev in _iter_jsonl(log):
                ts = ev.get("ts", "")
                if not _in_window(ts) or not _vidarr_hook_is_security(ev):
                    continue
                events.append(
                    {
                        "ts": ts,
                        "kind": "security-deny",
                        "category": ev.get("hook", ""),
                        "summary": (ev.get("rule", "") or "deny")
                        + (f" · {ev.get('path')}" if ev.get("path") else ""),
                        "source": ev.get("tool", "") or "hook",
                    }
                )

    events.sort(key=lambda e: e.get("ts", ""), reverse=True)
    return {
        "events": events,
        "total": len(events),
        "window_days": days,
    }


def _norns_git_lines(args: list, cwd: Path) -> list:
    """Run `git <args>` under cwd, returning stdout lines (empty on ANY failure:
    no git, shallow clone, non-repo, timeout). Norns inlines NOTHING git-derived
    into the committed dashboard.html — this runs live in the served endpoint —
    so a git failure must degrade to an empty list, never raise."""
    import subprocess as _sp

    try:
        out = _sp.run(
            ["git"] + args, cwd=str(cwd), capture_output=True, text=True, timeout=10
        )
        if out.returncode != 0:
            return []
        return [ln for ln in out.stdout.splitlines() if ln.strip()]
    except (OSError, _sp.SubprocessError):
        return []


def _read_norns(repo_root: Path, plugin: str) -> dict:
    """Build the Norns lineage view for one plugin: Urðr (past — scenario
    surfaces + decisions + commits), Verðandi (present — version + hook/rule
    counts + last release), Skuld (future — next_version + roadmap + proposals).

    Reads live (git log, events.jsonl, plugin.json, docs/proposals/) — this is
    why it lives in the served endpoint, NOT inlined at generator time: git
    output varies between a full clone and CI's shallow checkout and would break
    the exact-match dashboard freshness gate. Duplicated byte-identically in both
    server copies (parity gate guards endpoint NAMES; edit both). Every source is
    guarded — a missing file / git failure yields an empty section, never raises.
    """
    pdir = f"plugins/{plugin}"
    manifest: dict = {}
    pj = repo_root / pdir / ".claude-plugin" / "plugin.json"
    try:
        manifest = json.loads(pj.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        manifest = {}

    # ── Urðr (past) ──────────────────────────────────────────────────────────
    # Scenario surfaces from events.jsonl, filtered to this plugin's scenarios.
    scenarios: list = []
    runs = repo_root / ".ravenclaude" / "runs"
    if runs.is_dir():
        for ev_file in sorted(runs.glob("*/events.jsonl")):
            try:
                with ev_file.open(encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            ev = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if not isinstance(ev, dict):
                            continue
                        if ev.get("type") == "scenario_surfaced" and str(
                            ev.get("scenario_path", "")
                        ).startswith(f"{pdir}/scenarios/"):
                            scenarios.append(ev)
            except OSError:
                continue
    scenarios.sort(key=lambda e: e.get("ts", ""), reverse=True)
    scenarios = scenarios[:5]

    # Decision-log entries (docs/decisions/<plugin>-*.md) — absent today; guarded.
    decisions: list = []
    dec_dir = repo_root / "docs" / "decisions"
    if dec_dir.is_dir():
        matches = sorted(
            dec_dir.glob(f"{plugin}-*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        decisions = [p.name for p in matches[:5]]

    commits = _norns_git_lines(["log", "--oneline", "-10", "--", pdir], repo_root)

    # ── Verðandi (present) ─────────────────────────────────────────────────────
    # Hooks exclude leading-underscore sourced helpers (matches the repo-guide
    # rule); rules = any file under rules/.
    hooks_dir = repo_root / pdir / "hooks"
    hook_count = 0
    if hooks_dir.is_dir():
        hook_count = sum(
            1
            for p in hooks_dir.glob("*.sh")
            if p.is_file() and not p.name.startswith("_")
        )
    rules_dir = repo_root / pdir / "rules"
    rule_count = (
        sum(1 for p in rules_dir.iterdir() if p.is_file()) if rules_dir.is_dir() else 0
    )
    rel = _norns_git_lines(
        ["log", "-1", "--format=%cs", "--", f"{pdir}/.claude-plugin/plugin.json"],
        repo_root,
    )

    # ── Skuld (future) ─────────────────────────────────────────────────────────
    # next_version / roadmap (P0.1 — absent today → gated empty state in the UI);
    # open proposals naming this plugin (README excluded).
    proposals: list = []
    prop_dir = repo_root / "docs" / "proposals"
    if prop_dir.is_dir():
        for md in sorted(prop_dir.glob("*.md")):
            if md.name == "README.md":
                continue
            try:
                body = md.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                body = ""
            if plugin in md.name or plugin in body:
                proposals.append(md.name)

    return {
        "plugin": plugin,
        "urdr": {"scenarios": scenarios, "decisions": decisions, "commits": commits},
        "verdandi": {
            "version": manifest.get("version", ""),
            "hooks": hook_count,
            "rules": rule_count,
            "last_release": rel[0] if rel else "",
        },
        "skuld": {
            "next_version": manifest.get("next_version", ""),
            "roadmap": manifest.get("roadmap", []) or [],
            "proposals": proposals[:5],
        },
    }


def _read_nidhoggr(repo_root: Path) -> dict:
    """Níðhöggr "Debt watch" — marketplace-wide debt signals for the Heimdall tab.
    Four cheap, low-noise signals, each read live (NOT inlined at generator time:
    two are git-derived and vary by clone depth, which would break the exact-match
    dashboard freshness gate — same reason Norns is served). Duplicated
    byte-identically in both server copies (parity gate guards endpoint NAMES;
    edit both). Every source is guarded — a git failure / missing dir yields an
    empty signal, never raises.

    Signals: stale_plugins (no version-manifest commit in >=120d), ungated_hooks
    (a hooks/*.sh referenced by neither a workflow nor audit-gates.sh — the real
    gate harness), superseded_decisions (docs/decisions entries with a successor
    via `supersedes:` frontmatter — absent today), todo_commits (TODO/FIXME in
    commit subjects).
    """
    import datetime as _dt

    out = {
        "stale_plugins": [],
        "ungated_hooks": [],
        "superseded_decisions": [],
        "todo_commits": [],
        "stale_threshold_days": 120,
    }

    # 1) Plugins with no plugin.json commit in >=120 days.
    cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=120)
    plugins_dir = repo_root / "plugins"
    if plugins_dir.is_dir():
        for pj in sorted(plugins_dir.glob("*/.claude-plugin/plugin.json")):
            rel = pj.relative_to(repo_root).as_posix()
            iso = _norns_git_lines(["log", "-1", "--format=%cI", "--", rel], repo_root)
            if not iso:
                continue
            try:
                when = _dt.datetime.fromisoformat(iso[0].strip())
                # Guard the COMPARISON too (not just the parse): a tz-naive `when`
                # vs the tz-aware `cutoff` raises TypeError. %cI always emits an
                # offset so this is defensive, but it keeps the docstring's
                # "a git failure yields an empty signal, never raises" honest.
                is_stale = when < cutoff
            except (ValueError, TypeError):
                continue
            if is_stale:
                out["stale_plugins"].append(
                    {"plugin": pj.parent.parent.name, "last_bump": iso[0][:10]}
                )

    # 2) Hooks referenced by neither a workflow nor audit-gates.sh.
    refs = ""
    wf_dir = repo_root / ".github" / "workflows"
    if wf_dir.is_dir():
        for wf in wf_dir.glob("*.yml"):
            try:
                refs += wf.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                pass
    audit = repo_root / "scripts" / "audit-gates.sh"
    if audit.is_file():
        try:
            refs += audit.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            pass
    if plugins_dir.is_dir() and refs:
        for h in sorted(plugins_dir.glob("*/hooks/*.sh")):
            name = h.name
            if name.startswith("_"):
                continue
            if name not in refs:
                out["ungated_hooks"].append(
                    {"hook": name, "plugin": h.parent.parent.name}
                )

    # 3) Superseded decision-log entries (docs/decisions/, `supersedes:` frontmatter).
    dec_dir = repo_root / "docs" / "decisions"
    if dec_dir.is_dir():
        superseded: set = set()
        for md in dec_dir.glob("*.md"):
            try:
                head = md.read_text(encoding="utf-8", errors="ignore")[:1000]
            except OSError:
                continue
            for line in head.splitlines():
                s = line.strip()
                if s.lower().startswith("supersedes:"):
                    target = s.split(":", 1)[1].strip().strip("\"'")
                    if target:
                        superseded.add(target)
        out["superseded_decisions"] = sorted(superseded)[:10]

    # 4) TODO/FIXME in commit subjects.
    for line in _norns_git_lines(["log", "--all", "--format=%h %s"], repo_root):
        up = line.upper()
        if "TODO" in up or "FIXME" in up:
            out["todo_commits"].append(line[:120])
        if len(out["todo_commits"]) >= 10:
            break

    out["total"] = (
        len(out["stale_plugins"])
        + len(out["ungated_hooks"])
        + len(out["superseded_decisions"])
        + len(out["todo_commits"])
    )
    return out


# ── Mímir scrub patterns ─────────────────────────────────────────────────────
# Python mirror of plugins/ravenclaude-core/hooks/_scrub.sh _secret_patterns.
# Source of truth is _scrub.sh — KEEP IN SYNC. Same shape priorities:
#   - cloud-provider API key prefixes (AWS / Anthropic / Stripe / GitHub /
#     GitLab / Slack / Google / npm / HuggingFace / Azure)
#   - JWTs (third segment {20,} not {6,} — real HMAC-SHA256 sigs are 43 chars;
#     a shorter floor invites prose false positives)
#   - PEM private keys
#   - CLI secret flags (--password=, --token=, short -p with {16,} tail and
#     refuses pure-digit values so `ssh -p 22222` / port maps don't trip)
#   - embedded credentials in URLs (basic-auth user:pass@host, conn strings)
# Applied UNIVERSALLY to every string value in /__mimir's response at the
# JSON-encoding boundary (RM7 / gap-delta C7+C8). Failure is fail-safe:
# any regex error falls through to returning the original string unchanged.
_MIMIR_SECRET_PATTERNS = [
    # Cloud API key prefixes
    r"AKIA[0-9A-Z]{12,}",
    r"sk-(?:ant-)?[A-Za-z0-9-]{20,}",
    r"sk_live_[A-Za-z0-9]{24,}",
    r"rk_live_[A-Za-z0-9]{24,}",
    r"ghp_[A-Za-z0-9]{30,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"glpat-[A-Za-z0-9_-]{15,}",
    r"xox[baprs]-[A-Za-z0-9-]{10,}",
    r"AIza[0-9A-Za-z_-]{30,}",
    r"npm_[A-Za-z0-9]{30,}",
    r"hf_[A-Za-z0-9]{30,}",
    r"AccountKey=[A-Za-z0-9+/=]{20,}",
    # JWTs (third segment tightened to {20,})
    r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{20,}",
    # PEM private keys
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    # CLI secret flags
    r"--password[=\s]\S+",
    r"--token[=\s]\S+",
    # Short -p: tightened to {16,} and refuses pure-digit values.
    r"(?:^|\s)-p[^\s\d]\S{15,}",
    # Embedded credentials in URLs (basic-auth + connection strings).
    r"(?:https?|postgres(?:ql)?|mysql|mongodb|redis|amqp|smtp)s?://[A-Za-z0-9._-]{2,}:[A-Za-z0-9._%+-]{4,}@",
]

# Pre-compile once (lazy — populated on first scrub call).
_MIMIR_SECRET_RES: list = []


def _mimir_scrub_string(s):
    """Mirror of _scrub.sh _scrub_reason() in Python. Replace secret-shaped
    tokens with [REDACTED]. Fail-safe: any error returns the original string.
    Non-strings pass through unchanged so it is safe to call at the
    JSON-encoding boundary on every value."""
    if not isinstance(s, str) or not s:
        return s
    try:
        import re as _re
        global _MIMIR_SECRET_RES
        if not _MIMIR_SECRET_RES:
            _MIMIR_SECRET_RES = [_re.compile(p) for p in _MIMIR_SECRET_PATTERNS]
        out = s
        for pat in _MIMIR_SECRET_RES:
            try:
                out = pat.sub("[REDACTED]", out)
            except Exception:
                continue  # one bad pattern must not wipe accumulated scrubs
        return out
    except Exception:
        return s


def _mimir_scrub_tree(obj):
    """Walk a dict/list/scalar tree and scrub every string value (and every
    string key). Applied once at the JSON-encoding boundary so individual
    field readers don't have to remember to scrub — RM7 universal-scrub."""
    if isinstance(obj, dict):
        return {
            (_mimir_scrub_string(k) if isinstance(k, str) else k):
                _mimir_scrub_tree(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_mimir_scrub_tree(v) for v in obj]
    if isinstance(obj, str):
        return _mimir_scrub_string(obj)
    return obj


# Per-JSONL bounded read cap — never load more than this many bytes from any
# single per-project session JSONL file (RM2 / Panel-A R2). The mtime+5
# newest files are tail-scanned only for cheap per-session counts.
_MIMIR_JSONL_READ_CAP = 50 * 1024  # 50 KiB


def _mimir_encode_key(project_root) -> str:
    """Stage 1 of the encoded-path algorithm (skill §"The encoded-path
    algorithm + fallback"). Strip leading "/" and replace every "/" with "-".
    Worktree-aware: feed $CLAUDE_PROJECT_DIR verbatim — never normalized."""
    s = str(project_root)
    return s.lstrip("/").replace("/", "-")


def _mimir_resolve_project_dir(claude_home, project_root):
    """Two-stage resolve per the skill: compute the documented key; on miss,
    glob ~/.claude/projects/* and reverse-decode each candidate. Returns the
    resolved Path or None. Defense against Anthropic ABI drift (RM1)."""
    from pathlib import Path as _Path
    claude_home = _Path(claude_home)
    projects = claude_home / "projects"
    if not projects.is_dir():
        return None
    computed = projects / _mimir_encode_key(project_root)
    try:
        computed_resolved = computed.resolve()
        projects_resolved = projects.resolve()
        # Path-traversal defense in depth (RM8): resolved candidate MUST sit
        # under claude_home/projects/. Reject anything that escapes.
        computed_resolved.relative_to(projects_resolved)
        if computed.is_dir():
            return computed
    except (ValueError, OSError):
        pass
    # Fallback: reverse-decode candidates.
    target = str(project_root)
    try:
        for candidate in projects.glob("*"):
            if not candidate.is_dir():
                continue
            decoded = "/" + candidate.name.replace("-", "/")
            if decoded == target:
                import sys as _sys
                print(
                    f"[mimir] encoded-path fallback resolved {candidate.name!r}"
                    f" -> {target!r}",
                    file=_sys.stderr,
                )
                return candidate
    except OSError:
        pass
    return None


def _mimir_iter_jsonl_bounded(path, cap_bytes: int = _MIMIR_JSONL_READ_CAP):
    """Yield dicts from a JSONL file, capping the read at `cap_bytes`. Per-line
    json.loads is try/except wrapped so a torn final line silently drops
    (RM2 / gap-delta C4). Never raises — OSError yields nothing."""
    try:
        with path.open("rb") as fh:
            chunk = fh.read(cap_bytes)
        text = chunk.decode("utf-8", errors="replace")
    except OSError:
        return
    # If we hit the cap mid-line, drop the truncated tail to avoid feeding
    # a partial line to json.loads (which would just be torn-write equivalent).
    if len(chunk) >= cap_bytes:
        nl = text.rfind("\n")
        if nl >= 0:
            text = text[:nl]
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(ev, dict):
            yield ev


def _read_streams(project_root) -> dict:
    """Build the Streams tab payload from .ravenclaude/streams/ (Agentic Work-Streams).

    Returns:
      {
        "served": True,                  # this endpoint only runs in served mode
        "count": int,                    # number of streams
        "active": str | None,            # active-stream id (validated slug) or None
        "streams": [                     # newest-updated first
          {"id","name","description","created","updated","event_count","active"}, ...
        ],
        "active_history": [ <derived event>, ... ],  # last N derived events of the active
                                                       # stream (whitelisted fields ONLY)
      }

    DERIVED-ONLY (the no-prompt-egress invariant — defense in depth): every event field
    surfaced is taken from a fixed whitelist of derived keys
    (kind/label/terms/word_count/summary/session_id/score/ts/stream_id) — NEVER a raw
    prompt/text/content field. The store already refuses to persist those (stream-ops
    append_event), and this reader whitelists again so even a hand-corrupted history line
    cannot leak an unexpected field into the dashboard. Gate 113 greps the rendered payload
    for a distinctive prompt phrase → must be absent.

    SERVER-PARITY DISCIPLINE: this function is duplicated BYTE-IDENTICALLY in both
    serve-dashboards.py copies (root + bundled plugin). It takes project_root as a
    parameter, so there is NO REPO_ROOT/PROJECT_ROOT variance — the two copies are
    literally identical. Gate 32 checks endpoint NAMES, not body bytes; EDIT BOTH.
    """
    from pathlib import Path as _Path

    base = {"served": True, "count": 0, "active": None, "streams": [], "active_history": []}
    sroot = _Path(project_root) / ".ravenclaude" / "streams"
    reg_path = sroot / "registry.json"
    try:
        if not reg_path.is_file():
            return base
        with reg_path.open("r", encoding="utf-8") as fh:
            reg = json.load(fh)
    except (OSError, ValueError):
        return base
    if not isinstance(reg, dict):
        return base
    streams_obj = reg.get("streams")
    if not isinstance(streams_obj, dict) or not streams_obj:
        return base

    import re as _re

    _slug_ok = _re.compile(r"\A[a-z0-9-]{1,64}\Z")

    # Active pointer — validate it is a known, safe slug.
    active = None
    try:
        ap = sroot / "active-stream"
        if ap.is_file():
            cand = ap.read_text(encoding="utf-8").strip()
            if _slug_ok.match(cand) and cand in streams_obj:
                active = cand
    except OSError:
        active = None

    rows = []
    for sid in streams_obj:
        if not _slug_ok.match(sid):
            continue  # skip a malformed registry key defensively
        meta = streams_obj.get(sid) or {}
        rows.append({
            "id": sid,
            "name": str(meta.get("name", sid))[:120],
            "description": str(meta.get("description", ""))[:240],
            "created": str(meta.get("created", "")),
            "updated": str(meta.get("updated", "")),
            "event_count": int(meta.get("event_count", 0)) if isinstance(meta.get("event_count"), int) else 0,
            "active": sid == active,
        })
    # newest-updated first; stable tiebreak on id
    rows.sort(key=lambda r: (r["updated"], r["id"]), reverse=True)

    # Last N DERIVED events of the active stream (whitelisted fields only).
    _allowed_event_keys = ("kind", "label", "terms", "word_count", "summary",
                           "session_id", "score", "ts", "stream_id", "schema_version")
    active_history = []
    if active:
        hist_path = sroot / active / "history.jsonl"
        try:
            lines = hist_path.read_text(encoding="utf-8").splitlines() if hist_path.is_file() else []
        except OSError:
            lines = []
        for raw in lines[-25:]:
            raw = raw.strip()
            if not raw:
                continue
            try:
                ev = json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                continue
            if not isinstance(ev, dict):
                continue
            # WHITELIST — copy ONLY known-derived keys; drop anything else.
            clean = {k: ev[k] for k in _allowed_event_keys if k in ev}
            active_history.append(clean)

    base["count"] = len(rows)
    base["active"] = active
    base["streams"] = rows
    base["active_history"] = active_history
    return base


def _read_mimir(project_root, claude_home) -> dict:
    """Build the Mímir session-state payload from on-disk Claude Code sources.

    Five cards: settings (theme + configured/last-used model + permission_mode),
    session (live-session probe via ~/.claude/sessions/<pid>.json), activity
    (~/.claude/stats-cache.json with `as_of` staleness disclosure), recent
    sessions (top 5 per-project JSONLs by mtime, bounded read), and the
    unreachable-fields list for the honest empty state. See the `mimir` skill
    for the full reachability map + scrubbing contract + worktree rule.

    Empty-state contract (Panel-A): if ~/.claude/projects/<encoded>/ does not
    exist (first-time host) → {"exists": False, ...} with empties; never 500.

    Universal scrub (RM7 / gap-delta C7+C8): all string values pass through
    _mimir_scrub_tree at the JSON-encoding boundary in _handle_mimir.

    SERVER-PARITY DISCIPLINE (RM6 / Panel-B R3): this function is duplicated
    BYTE-IDENTICALLY in both serve-dashboards.py copies. Gate 32 checks
    endpoint NAMES, not body bytes — an asymmetric edit silently passes Gate
    32 while the copies diverge. EDIT BOTH or surface a follow-up.

    NEVER reads `type=user` content (gap-delta C8): only metadata
    (timestamp / gitBranch / entrypoint) from user events; `type=assistant`
    events are used for token sums + last-used model.
    """
    from pathlib import Path as _Path

    project_root = _Path(project_root)
    claude_home = _Path(claude_home)

    base = {
        "exists": False,
        "settings": {
            "theme": None,
            "model": {"configured": None, "last_used": None},
            "permission_mode": None,
        },
        "session": {
            "session_id": None,
            "version": None,
            "started_at": None,
            "pid": None,
            "found": False,
        },
        "activity": {
            "as_of": None,
            "total_sessions": None,
            "total_messages": None,
            "daily_activity_7d": [],
            "model_usage": None,
        },
        "recent_sessions": [],
        "unreachable": ["effort_dial", "plan_tier", "status_live_cache"],
    }

    # ── settings.theme (user-level) ──────────────────────────────────────────
    user_settings_path = claude_home / "settings.json"
    if user_settings_path.is_file():
        try:
            us = json.loads(user_settings_path.read_text(encoding="utf-8"))
            if isinstance(us, dict):
                t = us.get("theme")
                if isinstance(t, str):
                    base["settings"]["theme"] = t
        except (OSError, json.JSONDecodeError, ValueError):
            pass

    # ── settings.model.configured (project-level) ───────────────────────────
    proj_settings_path = project_root / ".claude" / "settings.json"
    if proj_settings_path.is_file():
        try:
            ps = json.loads(proj_settings_path.read_text(encoding="utf-8"))
            if isinstance(ps, dict):
                m = ps.get("model")
                if isinstance(m, str):
                    base["settings"]["model"]["configured"] = m
        except (OSError, json.JSONDecodeError, ValueError):
            pass

    # ── resolve per-project JSONL directory ─────────────────────────────────
    proj_dir = _mimir_resolve_project_dir(claude_home, project_root)
    if proj_dir is None:
        # Honest empty-state (Panel-A): first-time host or missing dir.
        return base
    base["exists"] = True

    # ── newest JSONLs (mtime-desc), bounded; drive last-used model,
    #    permission-mode, recent-sessions card ──────────────────────────────
    try:
        jsonls = sorted(
            (p for p in proj_dir.glob("*.jsonl") if p.is_file()),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
    except OSError:
        jsonls = []

    # last-used model: newest JSONL's most-recent assistant event.
    if jsonls:
        try:
            newest_events = list(_mimir_iter_jsonl_bounded(jsonls[0]))
        except Exception:
            newest_events = []
        last_model = None
        first_perm_mode = None
        for ev in newest_events:
            if ev.get("type") == "assistant":
                m = ev.get("model")
                if isinstance(m, str):
                    last_model = m  # overwrite — keep newest seen in scanned slice
            if first_perm_mode is None and ev.get("type") == "permission-mode":
                pm = ev.get("permissionMode")
                if isinstance(pm, str):
                    first_perm_mode = pm
        if last_model:
            base["settings"]["model"]["last_used"] = last_model
        if first_perm_mode:
            base["settings"]["permission_mode"] = first_perm_mode

    # recent_sessions card (top 5 per the skill source-map).
    for jf in jsonls[:5]:
        try:
            mtime = jf.stat().st_mtime
        except OSError:
            continue
        import datetime as _dt
        try:
            last_active = _dt.datetime.fromtimestamp(
                mtime, tz=_dt.timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
        except (OSError, ValueError, OverflowError):
            last_active = ""

        event_count = 0
        output_tokens = 0
        git_branch = None
        # NEVER reads type=user content — only metadata from user events
        # (gitBranch), and assistant events for token/count.
        for ev in _mimir_iter_jsonl_bounded(jf):
            t = ev.get("type")
            if t == "assistant":
                event_count += 1
                usage = ev.get("usage")
                if isinstance(usage, dict):
                    ot = usage.get("output_tokens")
                    if isinstance(ot, int):
                        output_tokens += ot
            if git_branch is None:
                gb = ev.get("gitBranch")
                if isinstance(gb, str) and gb:
                    git_branch = gb

        sid = jf.stem  # filename is the session UUID; truncate to 8 for display.
        base["recent_sessions"].append({
            "session_id": sid[:8] if isinstance(sid, str) else "",
            "last_active": last_active,
            "event_count": event_count,
            "output_tokens": output_tokens,
            "git_branch": git_branch,
        })

    # ── activity card (~/.claude/stats-cache.json) ──────────────────────────
    stats_path = claude_home / "stats-cache.json"
    if stats_path.is_file():
        try:
            stats = json.loads(stats_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError):
            stats = None
        if isinstance(stats, dict):
            # as_of pill MUST always be set when stats-cache exists (RM4).
            aof = stats.get("lastComputedDate")
            base["activity"]["as_of"] = aof if isinstance(aof, str) else None
            ts = stats.get("totalSessions")
            if isinstance(ts, int):
                base["activity"]["total_sessions"] = ts
            tm = stats.get("totalMessages")
            if isinstance(tm, int):
                base["activity"]["total_messages"] = tm
            da = stats.get("dailyActivity")
            if isinstance(da, list):
                base["activity"]["daily_activity_7d"] = da[-7:]
            mu = stats.get("modelUsage")
            if isinstance(mu, dict):
                base["activity"]["model_usage"] = mu

    # ── live-session probe (~/.claude/sessions/<pid>.json) ──────────────────
    sessions_dir = claude_home / "sessions"
    if sessions_dir.is_dir():
        target_cwd = str(project_root)
        try:
            session_files = list(sessions_dir.glob("*.json"))
        except OSError:
            session_files = []
        for sf in session_files:
            try:
                sd = json.loads(sf.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, ValueError):
                continue
            if not isinstance(sd, dict):
                continue
            if sd.get("cwd") != target_cwd or sd.get("status") != "busy":
                continue
            sid = sd.get("sessionId")
            base["session"]["session_id"] = (
                sid[:8] if isinstance(sid, str) else None
            )
            ver = sd.get("version")
            base["session"]["version"] = ver if isinstance(ver, str) else None
            st = sd.get("startedAt")
            base["session"]["started_at"] = st if isinstance(st, str) else None
            pid = sd.get("pid")
            base["session"]["pid"] = pid if isinstance(pid, int) else None
            base["session"]["found"] = True
            break

    return base


def _read_knowledge_health(repo_root: Path) -> dict:
    """Knowledge-health card — bucket-counts + drill-down for files under
    plugins/*/knowledge/*.md, by last-verified age. Delegates to the canonical
    knowledge-health.py script (single source of truth — same script also
    backs the /knowledge-health skill + the doctor 7-check). Read-only.
    Duplicated byte-identically in both server copies (parity gate guards
    endpoint NAMES; this helper is duplicated, so edit both). A subprocess
    failure / missing script yields an empty payload with `error`, never
    raises."""
    empty = {
        "schema_version": 1,
        "counts": {"stale": 0, "due_soon": 0, "untracked": 0, "fresh": 0, "total": 0},
        "stale": [],
        "due_soon": [],
        "untracked": [],
        "fresh_paths": [],
        "today": "",
        "threshold_days": 90,
    }
    if not KNOWLEDGE_HEALTH_SCRIPT.is_file():
        empty["error"] = "knowledge-health.py not found"
        return empty
    try:
        proc = subprocess.run(
            [sys.executable, str(KNOWLEDGE_HEALTH_SCRIPT), "--json"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (subprocess.SubprocessError, OSError) as e:
        empty["error"] = f"subprocess failed: {e}"
        return empty
    if proc.returncode != 0:
        empty["error"] = f"knowledge-health.py exit {proc.returncode}"
        return empty
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        empty["error"] = f"invalid JSON: {e}"
        return empty


def _read_worktree_guard(project_root: Path) -> dict | None:
    """Worktree-hygiene guard status for THIS checkout — whether it is the repo's
    anchor, how many live Claude sessions share this working tree, and whether
    there is contention (a latecomer joined a tree already in use). The SINGLE
    SOURCE OF TRUTH is worktree-guard.sh `status --json`; this reader never
    reimplements anchor/staleness detection in Python — it only shells the hook
    and parses its JSON. Read-only and fail-open: a missing hook, a non-git
    checkout, a missing git/jq/shasum, a timeout, or non-JSON output all yield
    None (the Sleipnir widget simply omits the guard block), never raises.
    Duplicated byte-identically in both server copies — keep them in sync (the
    parity gate guards endpoint NAMES; this helper is duplicated, so edit both)."""
    hook = project_root / "plugins" / "ravenclaude-core" / "hooks" / "worktree-guard.sh"
    if not hook.is_file():
        # Bundled-plugin install ships the hook alongside this server (../hooks).
        hook = Path(__file__).resolve().parent.parent / "hooks" / "worktree-guard.sh"
    if not hook.is_file():
        return None
    try:
        proc = subprocess.run(
            ["bash", str(hook), "status", "--json"],
            cwd=str(project_root),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    out = (proc.stdout or "").strip()
    if not out:
        return None
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _read_sleipnir(project_root: Path) -> dict:
    """Sleipnir's stables — the current git worktrees under .claude/worktrees/,
    plus the worktree-hygiene guard status for THIS checkout (is_anchor /
    live_sessions / contention, via worktree-guard.sh status --json — the single
    source of truth). The directory listing reads only under project_root; the
    guard block is fail-open (absent on any git/hook failure). Byte-identical in
    the root and bundled plugin server — keep the two copies in sync (the parity
    gate guards endpoint NAMES; this helper is duplicated, so edit both). Any
    failure (missing dir, unreadable) degrades to an empty stable, never raises."""
    out: dict = {"worktrees": [], "count": 0}
    wt_dir = project_root / ".claude" / "worktrees"
    if wt_dir.is_dir():
        try:
            names = sorted(d.name for d in wt_dir.iterdir() if d.is_dir())
        except OSError:
            names = []
        out["worktrees"] = names
        out["count"] = len(names)
    guard = _read_worktree_guard(project_root)
    if guard is not None:
        out["guard"] = guard
    return out


# Module-level cache of the loaded analyzer — avoid re-importing on every request.
_CONCERN_STATS_MOD = None


def _read_concern_stats(project_root: Path) -> dict:
    """Per-concern false-positive signals computed from the Sága log
    (.ravenclaude/runs/thing/*.json). Powers the Pipeline tab's "Concern
    reliability" card. Delegates to thing-concern-stats.py's compute() so the
    CLI tool and the dashboard endpoint share a single source of truth.

    In-process (no subprocess) — matches the Heimdall/Vidarr/Norns/Sleipnir
    reader pattern in this file. Duplicated byte-identically in both server
    copies — keep them in sync (the parity gate guards endpoint NAMES). Every
    failure (missing analyzer, import error, malformed Sága entry) degrades to
    an empty payload with an `error` field, never raises."""
    global _CONCERN_STATS_MOD
    empty = {"schema_version": 1, "total_reviews": 0, "concerns": []}
    if _CONCERN_STATS_MOD is None:
        import importlib.util
        script = project_root / "plugins" / "ravenclaude-core" / "scripts" / "thing-concern-stats.py"
        if not script.is_file():
            # Bundled-plugin install ships the analyzer alongside this server.
            script = Path(__file__).resolve().parent / "thing-concern-stats.py"
        if not script.is_file():
            return {**empty, "error": "analyzer not found"}
        try:
            spec = importlib.util.spec_from_file_location("thing_concern_stats", script)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _CONCERN_STATS_MOD = mod
        except Exception as e:  # noqa: BLE001 — best-effort observability tool
            return {**empty, "error": f"analyzer import failed: {str(e)[:200]}"}
    try:
        return _CONCERN_STATS_MOD.compute(project_root)
    except Exception as e:  # noqa: BLE001 — single Sága entry failure → empty, never raises
        return {**empty, "error": str(e)[:200]}


class DashboardHandler(SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler (serving the plugin dir) + the dashboard endpoints."""

    def log_message(self, format, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), format % args))

    def _local_request_ok(self) -> bool:
        """Refuse cross-origin / DNS-rebinding requests to the write/read/classify
        endpoints. Checked on every state-changing or read request.

        CRITICAL INVARIANT (unified dashboard shell, v0.114.0):
        DO NOT add `Access-Control-Allow-Origin` headers to this server to
        "help" the shell's served-mode probe in index.html. The shell HEAD-
        probes `/__csrf` from `index.html` and treats the cross-origin reject
        as the static-host signal — the FAILURE IS THE SIGNAL the banner
        renders on. Adding ACAO headers would shatter that signal AND the
        DNS-rebinding defense below. If a future contributor wants the
        banner to behave differently on a public host, change the SHELL's
        probe (in index.html near `probeServedMode`), never relax this guard.
        """
        sfs = self.headers.get("Sec-Fetch-Site")
        if sfs is not None and sfs not in ("same-origin", "none"):
            return False
        origin = self.headers.get("Origin")
        if origin is not None and origin not in _ALLOWED_ORIGINS:
            return False
        # Fail CLOSED on Host: a browser (HTTP/1.1) always sends Host, so the legit
        # dashboard never trips this — but a header-absent non-browser request must
        # not slip through. Host must be present AND a known local/forwarded host.
        host = self.headers.get("Host")
        if host is None or host not in _ALLOWED_HOSTS:
            return False
        return True

    def _state_change_origin_ok(self) -> bool:
        """Require a PRESENT and allow-listed Origin on state-changing requests.

        This is the browser-CSRF / DNS-rebinding defense, and it is the one check
        on this path a hostile web page cannot satisfy. Per the Fetch standard
        (§"append a request `Origin` header"), the browser appends Origin to every
        request whose method is neither GET nor HEAD, and a page can neither forge
        nor suppress it. So a same-origin dashboard POST always carries
        `Origin: http://127.0.0.1:<port>`, while an opaque origin (sandboxed iframe,
        data: URL) sends the literal `null` — not in _ALLOWED_ORIGINS, so rejected.

        Why this is separate from _local_request_ok() instead of folded into it:
        that guard also runs on GETs, and the Fetch standard appends Origin to a GET
        only when the request is CROSS-origin. The dashboard's own same-origin
        `GET /__csrf` token bootstrap therefore carries no Origin at all — requiring
        it there would break the token fetch and the entire dashboard with it.

        Sec-Fetch-Site is deliberately NOT required to be present: it is absent on
        Safari < 16.4 and other older browsers, so requiring it would break real
        dashboard saves to buy a defense Origin already provides. _local_request_ok()
        still rejects it when it IS present and says cross-site.

        WHAT THIS DOES NOT STOP — do not overstate it: a local scripted process (the
        coding agent included) can send any header it likes, so it satisfies this
        check trivially — and it can write the target file directly with its own
        tools regardless of this server. Every discriminator available here is
        client-asserted, so there is NO design in which "the human can flip this but
        a local script cannot." The threat this closes is the browser one: a
        malicious page the user is viewing, or a DNS-rebinding attack, driving this
        server on their behalf.
        """
        origin = self.headers.get("Origin")
        return origin is not None and origin in _ALLOWED_ORIGINS

    def _csrf_ok(self) -> bool:
        """Second layer under the Origin guard, NOT an independent defense.

        Do not read this as "even a client with no Origin still needs the token" —
        that is circular. A client that can reach GET /__csrf can read the token,
        and that bootstrap cannot be Origin-gated (see the _CSRF_TOKEN comment).
        Its real value is against the BROWSER threat, where it is redundant with
        _state_change_origin_ok() by design: a cross-origin page cannot read the
        token because this server sends no CORS headers.

        State-changing POSTs must carry the X-CSRF-Token header with the
        per-process token; constant-time compared so a scripted client can't
        side-channel-leak the value. Fails CLOSED on an empty server token (a
        startup race) — only the bootstrap GET /__csrf is allowed to run before
        the token is populated.
        """
        if not _CSRF_TOKEN:
            return False
        presented = self.headers.get("X-CSRF-Token", "")
        return hmac.compare_digest(presented, _CSRF_TOKEN)

    def _parse_content_length(self, max_bytes: int) -> int | None:
        """Parse Content-Length defensively; respond 400/413 on failure.

        Returns the parsed length, or None if the handler already responded
        with an error (the caller must return immediately). A non-numeric
        Content-Length used to raise ValueError and surface as a 500 with a
        traceback — replaced with a controlled 400.
        """
        raw = self.headers.get("Content-Length", "0")
        try:
            length = int(raw)
        except (ValueError, TypeError):
            self.send_error(400, "invalid Content-Length")
            return None
        if length <= 0 or length > max_bytes:
            self.send_error(413, f"request body required, max {max_bytes} bytes")
            return None
        return length

    def do_HEAD(self):
        if (
            self.path == "/__save"
            or self.path == "/__classify"
            or self.path == "/__csrf"
            or self.path.startswith("/__read")
            or self.path.startswith("/__saga")
            or self.path.startswith("/__heimdall")
            or self.path.startswith("/__vidarr")
            or self.path.startswith("/__norns")
            or self.path.startswith("/__nidhoggr")
            or self.path.startswith("/__mimir")
            or self.path.startswith("/__streams")
            or self.path.startswith("/__knowledge-health")
            or self.path.startswith("/__sleipnir")
            or self.path.startswith("/__runs")
            or self.path.startswith("/__concern-stats")
        ):
            self.send_response(200)
            self.send_header("Allow", "GET, POST, HEAD")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        super().do_HEAD()

    def do_GET(self):
        # NOTE: static GETs are intentionally ungated (serving the read-only plugin
        # dir). Any NEW data-returning GET endpoint added here MUST call
        # self._local_request_ok() first (as _handle_read does) — do not let it ride
        # the static path.
        if self.path in ("/", ""):
            # Redirect bare root to the dashboard page. PLUGIN_DIR has no
            # index.html, so without this SimpleHTTPRequestHandler renders a
            # directory listing of the plugin — the "it opened the directory,
            # not the dashboard" report. main() injects the target.
            target = getattr(self.server, "_dash_path", DASH_PATH)
            self.send_response(302)
            self.send_header("Location", target)
            self.end_headers()
            return
        if self.path.startswith("/__read"):
            self._handle_read()
            return
        if self.path.startswith("/__saga"):
            self._handle_saga()
            return
        if self.path.startswith("/__heimdall"):
            self._handle_heimdall()
            return
        if self.path.startswith("/__vidarr"):
            self._handle_vidarr()
            return
        if self.path.startswith("/__norns"):
            self._handle_norns()
            return
        if self.path.startswith("/__nidhoggr"):
            self._handle_nidhoggr()
            return
        if self.path.startswith("/__mimir"):
            self._handle_mimir()
            return
        if self.path.startswith("/__streams"):
            self._handle_streams()
            return
        if self.path.startswith("/__knowledge-health"):
            self._handle_knowledge_health()
            return
        if self.path.startswith("/__sleipnir"):
            self._handle_sleipnir()
            return
        if self.path.startswith("/__runs"):
            self._handle_runs()
            return
        if self.path.startswith("/__concern-stats"):
            self._handle_concern_stats()
            return
        if self.path == "/__csrf":
            self._handle_csrf()
            return
        super().do_GET()

    def _handle_csrf(self):
        """GET /__csrf — return the per-process CSRF token to the same-origin
        dashboard JS. Gated by the Origin/Host check, so a cross-origin page
        cannot read the token (browser CORS would also block reading the JSON
        response, but the explicit guard fails closed)."""
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        if not _CSRF_TOKEN:
            self.send_error(503, "csrf token not yet initialized")
            return
        body = json.dumps({"token": _CSRF_TOKEN}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        if self.path in ("/__save", "/__classify"):
            self.send_response(204)
            self.send_header("Allow", "POST, HEAD, OPTIONS")
            self.end_headers()
            return
        self.send_error(405)

    def do_POST(self):
        # do_POST is the single chokepoint for every state-changing endpoint
        # (/__save, /__classify), so the strict Origin requirement goes here rather
        # than in _local_request_ok() — which also gates read-only GETs that
        # legitimately carry no Origin. See _state_change_origin_ok.
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        if not self._state_change_origin_ok():
            self.send_error(403, "refused: state-changing request requires a present, allowed Origin")
            return
        if not self._csrf_ok():
            self.send_error(403, "missing or invalid CSRF token")
            return
        if self.path == "/__classify":
            self._handle_classify()
            return
        if self.path != "/__save":
            self.send_error(404, "endpoint not found")
            return

        length = self._parse_content_length(5 * 1024 * 1024)
        if length is None:
            return
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            target = body["path"]
            content = body["content"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as e:
            self.send_error(400, f"invalid JSON body: {e}")
            return

        is_plugin_cfg = _is_plugin_config_target(target)
        if target not in ALLOWED_TARGETS and not is_plugin_cfg:
            self.send_error(403, f"path not in allow-list: {target}")
            return
        out = (PROJECT_ROOT / target).resolve()
        try:
            out.relative_to(PROJECT_ROOT)
        except ValueError:
            self.send_error(403, "path escapes project root")
            return
        if not isinstance(content, str):
            self.send_error(400, "content must be a string")
            return

        # JSON-validate the layout / task-scope targets BEFORE writing — never
        # persist unparseable JSON or a structurally-broken layout file.
        if target in JSON_EDIT_TARGETS:
            err = _validate_json_target(target, content)
            if err:
                self.send_error(400, err)
                return

        # YAML-validate per-plugin variable files + the web-access list (must be a
        # mapping) before write.
        if is_plugin_cfg or target in YAML_MAPPING_TARGETS:
            err = _validate_plugin_config(content)
            if err:
                self.send_error(400, f"{target}: {err}")
                return

        out.parent.mkdir(parents=True, exist_ok=True)
        # write_bytes, not write_text(newline=): Python 3.9 compat (LF preserved)
        out.write_bytes(content.encode("utf-8"))

        payload = {"saved": str(out.relative_to(PROJECT_ROOT)), "bytes": len(content)}
        if target == POSTURE_TARGET:
            payload.update(self._apply_posture())
        self._json(200, payload)

    def _handle_read(self):
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        from urllib.parse import parse_qs, urlparse
        qs = parse_qs(urlparse(self.path).query)
        target = (qs.get("path") or [""])[0]
        if target not in ALLOWED_READ and not _is_plugin_config_target(target):
            self.send_error(403, f"path not in read allow-list: {target!r}")
            return
        out = (PROJECT_ROOT / target).resolve()
        try:
            out.relative_to(PROJECT_ROOT)
        except ValueError:
            self.send_error(403, "path escapes project root")
            return
        if not out.is_file():
            self._json(404, {"path": target, "exists": False})
            return
        content = out.read_text(encoding="utf-8")
        payload = {"path": target, "exists": True, "content": content, "parsed": None}
        if target.endswith((".yaml", ".yml")):
            try:
                import yaml
                payload["parsed"] = yaml.safe_load(content)
            except Exception:
                payload["parsed"] = None
        elif target.endswith(".json"):
            try:
                payload["parsed"] = json.loads(content)
            except Exception:
                payload["parsed"] = None
        self._json(200, payload)

    def _handle_saga(self):
        """GET /__saga[?limit=N] — return the last N command-review verdicts from
        the CONSUMER project's .ravenclaude/runs/thing/*.json (newest-first, capped
        at 500, default 200). Only the top-level thing-*.json files are read; the
        decisions/ subdir is ignored. Malformed files are skipped without erroring.
        Read-only; guarded by the same Origin/Host CSRF check as /__read."""
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        import glob as _glob
        import os as _os
        from urllib.parse import parse_qs, urlparse

        qs = parse_qs(urlparse(self.path).query)
        try:
            limit = max(1, min(500, int((qs.get("limit") or ["200"])[0])))
        except (ValueError, TypeError):
            limit = 200

        runs_dir = PROJECT_ROOT / ".ravenclaude" / "runs" / "thing"
        pattern = str(runs_dir / "thing-*.json")
        paths = sorted(_glob.glob(pattern), reverse=True)  # filename sort ≈ timestamp sort

        records = []
        for path in paths:
            if len(records) >= limit:
                break
            try:
                raw = Path(path).read_text(encoding="utf-8").strip()
                if not raw:
                    continue
                d = json.loads(raw)
            except (OSError, json.JSONDecodeError, ValueError):
                continue  # skip malformed / unreadable files

            # Derive the human "action" string — never expose file content.
            tool_input = d.get("tool_input") or {}
            tool_name = d.get("tool_name", "")
            if isinstance(tool_input, dict):
                if "command" in tool_input:
                    cmd = str(tool_input["command"])
                    action = cmd[:160] + ("…" if len(cmd) > 160 else "")
                elif "file_path" in tool_input:
                    basename = _os.path.basename(str(tool_input.get("file_path", "")))
                    bytes_val = tool_input.get("bytes", "?")
                    action = f"{basename} ({bytes_val}b)"
                elif "description" in tool_input:
                    desc = str(tool_input["description"])
                    action = desc[:160] + ("…" if len(desc) > 160 else "")
                else:
                    action = str(list(tool_input.keys()))[:80]
            else:
                action = ""

            # Normalise seats — the schema evolved: some records have a singular
            # "seat" key (T2 single-seat), others have "seats" (T3+ panel / empty).
            raw_seats = d.get("seats")
            if raw_seats is None:
                single = d.get("seat")
                raw_seats = [single] if isinstance(single, dict) else []
            compact_seats = []
            for s in (raw_seats or []):
                if not isinstance(s, dict):
                    continue
                compact_seats.append({
                    "name": s.get("name", ""),
                    "verdict": s.get("verdict") or s.get("status", ""),
                    "confidence": s.get("confidence", 0),
                })

            # Rewrite field: only for edit verdicts, truncated, command text only.
            rewrite = None
            if d.get("final_verdict") == "edit":
                upd = d.get("updated_input")
                if isinstance(upd, dict):
                    rw_text = upd.get("command") or str(upd)
                elif upd is not None:
                    rw_text = str(upd)
                else:
                    rw_text = None
                if rw_text:
                    rewrite = rw_text[:200] + ("…" if len(rw_text) > 200 else "")

            entry_cited = d.get("concerns_cited") or []
            entry_cat = d.get("category", "")
            base_t, final_t = _compute_saga_tiers(entry_cat, entry_cited)
            records.append({
                "id": d.get("id", ""),
                "timestamp": d.get("timestamp", ""),
                "tool_name": tool_name,
                "action": action,
                "category": entry_cat,
                "phase": d.get("phase", ""),
                "final_verdict": d.get("final_verdict", ""),
                "duration_ms": d.get("duration_ms", 0),
                "concerns_cited": entry_cited,
                "seats": compact_seats,
                "rewrite": rewrite,
                "base_tier": base_t,
                "final_tier": final_t,
            })

        self._json(200, records)

    def _apply_posture(self) -> dict:
        """Re-run apply-comfort-posture.py against the CONSUMER's project after a save."""
        if not APPLY_SCRIPT.is_file():
            return {"applied": False, "apply_error": "apply-comfort-posture.py not found"}
        try:
            proc = subprocess.run(
                [sys.executable, str(APPLY_SCRIPT), "--project-root", str(PROJECT_ROOT), "--source", "dashboard-save"],
                capture_output=True, text=True, timeout=30,
            )
        except (subprocess.SubprocessError, OSError) as e:
            return {"applied": False, "apply_error": f"could not run translator: {e}"}
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "non-zero exit").strip()
            return {"applied": False, "apply_error": err[:500]}
        summary = (proc.stdout or "").split("\nNote:")[0].strip()
        return {"applied": True, "apply_summary": summary[:1000]}

    def _handle_classify(self):
        length = self._parse_content_length(64 * 1024)
        if length is None:
            return
        try:
            command = json.loads(self.rfile.read(length).decode("utf-8"))["command"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as e:
            self.send_error(400, f"invalid JSON body: {e}")
            return
        if not isinstance(command, str) or not command.strip():
            self._json(200, {"category": None})
            return
        if not THING_DECISION.is_file():
            self._json(500, {"error": "thing-decision.py not found"})
            return
        try:
            proc = subprocess.run(
                [sys.executable, str(THING_DECISION), "--root", str(PROJECT_ROOT),
                 "preview", "--", command[:4000]],
                cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=15,
            )
            decision = json.loads(proc.stdout) if proc.stdout.strip() else {"category": None}
        except (subprocess.SubprocessError, OSError, json.JSONDecodeError) as e:
            self._json(500, {"error": f"classify failed: {e}"})
            return
        self._json(200, decision)

    def _handle_runs(self):
        """GET /__runs[?limit=N] — recent multi-step runs from
        .ravenclaude/runs/<id>/ (newest-first by mtime, capped 500, default 200).
        The thing/ verdict dir is owned by /__saga and skipped here. Read-only;
        same Origin/Host CSRF guard as /__read. (Mirror of the root dev server's
        /__runs, with REPO_ROOT → PROJECT_ROOT — kept in lockstep per the
        dashboard-server-parity gate.)"""
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        from urllib.parse import parse_qs, urlparse

        qs = parse_qs(urlparse(self.path).query)
        try:
            limit = max(1, min(500, int((qs.get("limit") or ["200"])[0])))
        except (ValueError, TypeError):
            limit = 200

        runs_dir = PROJECT_ROOT / ".ravenclaude" / "runs"
        records = []
        if runs_dir.is_dir():
            run_dirs = [
                d for d in runs_dir.iterdir() if d.is_dir() and d.name != "thing"
            ]
            def _safe_mtime(d):
                # A run dir deleted between iterdir() and sort() (concurrent run
                # cleanup) must not crash the /__runs handler with OSError —
                # mirrors the try/except OSError guard in _summarize_run.
                try:
                    return d.stat().st_mtime
                except OSError:
                    return 0.0

            run_dirs.sort(key=_safe_mtime, reverse=True)
            for d in run_dirs[:limit]:
                records.append(_summarize_run(d))
        self._json(200, records)

    def _handle_heimdall(self):
        """GET /__heimdall[?days=N] — the Heimdall tab's hook-event card. Globs
        .ravenclaude/runs/*/hook-events.jsonl (last N days, default 30), groups by
        hook, tier-classifies each event, and returns the Gjallarhorn banner tier.
        Read-only; same Origin/Host CSRF guard as /__read. (Mirror of the root dev
        server's /__heimdall with REPO_ROOT → PROJECT_ROOT — kept in lockstep per
        the dashboard-server-parity gate.)"""
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        from urllib.parse import parse_qs, urlparse

        qs = parse_qs(urlparse(self.path).query)
        try:
            days = max(1, min(365, int((qs.get("days") or ["30"])[0])))
        except (ValueError, TypeError):
            days = 30
        self._json(200, _read_hook_events(PROJECT_ROOT / ".ravenclaude" / "runs", days=days))

    def _handle_vidarr(self):
        """GET /__vidarr[?days=N] — the Víðarr Security-log tab. Interleaves
        posture changes (.ravenclaude/posture-events.jsonl) with security-relevant
        hook denials (.ravenclaude/runs/*/hook-events.jsonl, deny-only) into one
        newest-first chronological log. Read-only; same Origin/Host CSRF guard as
        /__read. (Mirror of the root dev server's /__vidarr with REPO_ROOT →
        PROJECT_ROOT — kept in lockstep per the dashboard-server-parity gate.)"""
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        from urllib.parse import parse_qs, urlparse

        qs = parse_qs(urlparse(self.path).query)
        try:
            days = max(1, min(36500, int((qs.get("days") or ["30"])[0])))
        except (ValueError, TypeError):
            days = 30
        rc = PROJECT_ROOT / ".ravenclaude"
        self._json(200, _read_vidarr_events(rc / "runs", rc / "posture-events.jsonl", days=days))

    def _handle_norns(self):
        """GET /__norns?plugin=<name> — the Norns lineage view (Urðr/Verðandi/
        Skuld) for one plugin. Reads live git log + events.jsonl + plugin.json +
        docs/proposals (NOT inlined at generator time — git output varies by
        clone depth and would break the exact-match dashboard freshness gate).
        Read-only; same Origin/Host CSRF guard as /__read. (Mirror of the root dev
        server's /__norns with REPO_ROOT → PROJECT_ROOT — kept in lockstep per the
        dashboard-server-parity gate.)"""
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        from urllib.parse import parse_qs, urlparse

        qs = parse_qs(urlparse(self.path).query)
        plugin = (qs.get("plugin") or ["ravenclaude-core"])[0]
        if not plugin or "/" in plugin or "\\" in plugin or ".." in plugin:
            self.send_error(400, "invalid plugin name")
            return
        self._json(200, _read_norns(PROJECT_ROOT, plugin))

    def _handle_nidhoggr(self):
        """GET /__nidhoggr — Níðhöggr "Debt watch" marketplace-wide debt signals
        for the Heimdall tab. Reads live git log + workflow/audit refs + decisions
        (NOT inlined at generator time — git output varies by clone depth and
        would break the exact-match dashboard freshness gate). Read-only; same
        Origin/Host CSRF guard as /__read. (Mirror of the root dev server's
        /__nidhoggr with REPO_ROOT → PROJECT_ROOT — kept in lockstep per the
        dashboard-server-parity gate.)"""
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        self._json(200, _read_nidhoggr(PROJECT_ROOT))

    def _handle_mimir(self):
        """GET /__mimir — the Mímir Session tab payload (settings / live
        session / activity / recent sessions). NO QUERY PARAMS ACCEPTED:
        claude_home + project_root are fixed at server start per the
        path-traversal defense (RM8). Universal-scrubbed at the JSON-encoding
        boundary (RM7). Empty state {"exists": False, ...} when the
        per-project dir is missing — never 500.

        Read-only; same Origin/Host CSRF guard as /__read. The only
        legitimate variance between this method's two copies is the
        repo-root constant (REPO_ROOT here, PROJECT_ROOT in the bundled
        plugin server) — kept in lockstep per the dashboard-server-parity
        gate. Reminder: Gate 32 checks endpoint NAMES, not body bytes;
        edit BOTH copies when this method or _read_mimir changes."""
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        from pathlib import Path as _Path
        claude_home = _Path(os.path.expanduser("~/.claude"))
        payload = _read_mimir(PROJECT_ROOT, claude_home)
        self._json(200, _mimir_scrub_tree(payload))

    def _handle_streams(self):
        """GET /__streams — the Streams tab payload (Agentic Work-Streams): the
        stream list + active pointer + the active stream's recent DERIVED history.
        DERIVED-ONLY (no prompt text — _read_streams whitelists event fields).
        Read-only; same Origin/Host CSRF guard as /__read. (Mirror of the root
        server's /__streams — _read_streams takes project_root, so the two copies
        are byte-identical; Gate 32 checks endpoint NAMES, edit BOTH.)"""
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        self._json(200, _read_streams(PROJECT_ROOT))

    def _handle_knowledge_health(self):
        """GET /__knowledge-health — knowledge-health card under the Heimdall
        tab. Delegates to knowledge-health.py via subprocess and forwards its
        JSON (counts + bucketed lists). Read-only; same Origin/Host CSRF guard
        as /__read. (Mirror of the root dev server's /__knowledge-health with
        REPO_ROOT → PROJECT_ROOT — kept in lockstep per the dashboard-server-
        parity gate.)"""
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        self._json(200, _read_knowledge_health(PROJECT_ROOT))

    def _handle_sleipnir(self):
        """GET /__sleipnir — Sleipnir's stables: the current git worktrees under
        .claude/worktrees/ (names + count). Read-only; same Origin/Host CSRF guard
        as /__read. (Mirror of the root dev server's /__sleipnir with REPO_ROOT →
        PROJECT_ROOT — kept in lockstep per the parity gate.)"""
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        self._json(200, _read_sleipnir(PROJECT_ROOT))

    def _handle_concern_stats(self):
        """GET /__concern-stats — per-concern false-positive signals computed
        from .ravenclaude/runs/thing/*.json (the Sága log). Powers the
        "Concern reliability" card on the Pipeline tab — surfaces concerns the
        tribunal is over-citing so the operator can tune them. Read-only; same
        Origin/Host CSRF guard as /__read. (Mirror of the root dev server's
        /__concern-stats with REPO_ROOT → PROJECT_ROOT — kept in lockstep per
        the parity gate.)"""
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        self._json(200, _read_concern_stats(PROJECT_ROOT))

    def _json(self, code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _print_qr(url: str) -> bool:
    try:
        import qrcode
    except ImportError:
        return False
    qr = qrcode.QRCode(border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii(invert=True)
    return True


# ── Port acquisition ────────────────────────────────────────────────────────
# This replaced a bare ThreadingHTTPServer((bind, port)) that raised an OSError
# traceback the moment port 8000 was busy — while commands/dashboard.md already
# advertised a fallback that did not exist. Two recovery paths, in order:
#   1. the holder is one of OUR OWN dashboard servers -> stop it, reuse the port
#      (a relaunch is the common case; keeps the URL stable)
#   2. anything else -> walk up to the next free port
# A process we have not positively identified as ours is NEVER signalled.


def _port_holder_pids(port: int) -> list[int]:
    """PIDs listening on `port`, excluding this process. Never raises: no lsof
    (or any failure) yields [], and the caller falls back to a port walk."""
    try:
        out = subprocess.run(
            ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    pids = []
    for tok in out.split():
        try:
            pid = int(tok)
        except ValueError:
            continue
        if pid != os.getpid():
            pids.append(pid)
    return pids


def _holder_cwd(pid: int) -> str | None:
    """`pid`'s working directory, or None. Never raises."""
    try:
        out = subprocess.run(
            ["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    for line in out.splitlines():
        if line.startswith("n"):
            return line[1:]
    return None


def _is_our_dashboard(pid: int) -> bool:
    """True only when `pid` is a serve-dashboards.py serving THIS project.

    Both halves matter. The name check alone would also match a dashboard
    another repo has open right now — reclaiming that would kill a live
    session in an unrelated project to free a port we can just as easily
    step around. So "ours" means "this project's own stale server"; every
    other dashboard is treated like any foreign process (fall back instead).

    Fail-closed — any doubt (no ps/lsof, a failure, an unreadable cwd, a
    mismatch) is False, so a process we haven't positively identified is
    never signalled."""
    try:
        out = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    if "serve-dashboards.py" not in out:
        return False
    cwd = _holder_cwd(pid)
    if cwd is None:
        return False
    try:
        return Path(cwd).resolve() == PROJECT_ROOT.resolve()
    except OSError:
        return False


def _reclaim_port(port: int) -> bool:
    """SIGTERM our own stale dashboard server(s) on `port` and wait for the
    socket to free. False if the holder isn't ours (or won't let go) — the
    caller then walks to another port rather than escalating."""
    pids = [p for p in _port_holder_pids(port) if _is_our_dashboard(p)]
    if not pids:
        return False
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            return False
    for _ in range(20):  # ~2s: SIGTERM + socket teardown is not instant
        time.sleep(0.1)
        if not _port_holder_pids(port):
            return True
    return False


def _bind_server(bind, port, handler, span=10):
    """Bind `port`, reclaiming it from our own stale server or falling back to
    the next free one. Returns (server, actual_port)."""
    try:
        return ThreadingHTTPServer((bind, port), handler), port
    except OSError as exc:
        if exc.errno != errno.EADDRINUSE:
            raise

    if _reclaim_port(port):
        try:
            srv = ThreadingHTTPServer((bind, port), handler)
            print(f"  port {port} was held by a stale RavenClaude dashboard — stopped it, rebound {port}")
            return srv, port
        except OSError as exc:
            if exc.errno != errno.EADDRINUSE:
                raise

    for candidate in range(port + 1, port + span + 1):
        try:
            srv = ThreadingHTTPServer((bind, candidate), handler)
            print(f"  port {port} is held by another process — bound {candidate} instead")
            return srv, candidate
        except OSError as exc:
            if exc.errno != errno.EADDRINUSE:
                raise
    raise SystemExit(
        f"serve-dashboards: ports {port}-{port + span} are all in use. Free one, or pass --port N."
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--port", type=int, default=8000)
    p.add_argument(
        "--no-open",
        action="store_true",
        help="do not auto-open a browser (for scripts/CI). Matches the root dev server.",
    )
    p.add_argument(
        "--bind",
        default=None,
        help="bind address; auto 0.0.0.0 in a Codespace (so the forwarded port is reachable), else 127.0.0.1. An explicit value always wins.",
    )
    p.add_argument(
        "--project-root",
        default=None,
        help="Pin the repo whose .ravenclaude/ is edited (default: current dir). The "
        "repo-local launcher passes this so the dashboard can never target the wrong repo.",
    )
    p.add_argument(
        "--validate",
        action="store_true",
        help="Resolve + guard-check the project root, print it, and exit without serving.",
    )
    args = p.parse_args()

    global PROJECT_ROOT
    if args.project_root is not None:
        root = Path(args.project_root).resolve()
        # Hard guard: a CONSUMER launcher (which always passes --project-root) must never
        # edit the marketplace checkout itself. The marketplace's own /dashboard launches
        # WITHOUT --project-root (cwd-based), so it is unaffected by this check.
        if root == MARKETPLACE_ROOT or MARKETPLACE_ROOT in root.parents:
            sys.stderr.write(
                f"ERROR: refusing to run — --project-root ({root}) is inside the RavenClaude "
                f"marketplace checkout ({MARKETPLACE_ROOT}).\n"
                "A consumer dashboard must edit a consumer repo, never the marketplace. "
                "Launch it from your own repo.\n"
            )
            return 2
        if not root.is_dir():
            sys.stderr.write(f"ERROR: --project-root {root} is not a directory.\n")
            return 2
        PROJECT_ROOT = root

    if args.validate:
        print(f"project root OK: {PROJECT_ROOT}")
        return 0

    # Serve static files from the PLUGIN dir (dashboard.html lives there); do NOT
    # chdir, so PROJECT_ROOT (the consumer's project, captured above) stays intact
    # for .ravenclaude/ reads/writes and the translator.
    handler = functools.partial(DashboardHandler, directory=str(PLUGIN_DIR))

    codespace = os.environ.get("CODESPACE_NAME")
    domain = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
    # In a Codespace the port-forwarder can't reach a 127.0.0.1-only socket, so default
    # to 0.0.0.0 there — kept safe by the Private forwarded port + the Origin/Host CSRF
    # guard below. Off-Codespace stay loopback-only. An explicit --bind always wins.
    bind = args.bind or ("0.0.0.0" if codespace else "127.0.0.1")

    # Refuse 0.0.0.0 when the Codespace forwarded port is set to Public — the
    # /__save surface would be reachable from the public internet on a path the
    # server doesn't expect to be public. See the marketplace-server twin and
    # docs/security/2026-06-dashboard-and-posture-apply-review.md (finding #3).
    # GITHUB_CODESPACES_PORT_VISIBILITY is not currently exported by Codespaces
    # (verified 2026-06-02), so this is defensive future-proofing; the real
    # authoritative check is `gh codespace ports list`.
    if bind == "0.0.0.0" and os.environ.get("GITHUB_CODESPACES_PORT_VISIBILITY", "").lower() == "public":
        sys.stderr.write(
            "serve-dashboards: refusing to bind 0.0.0.0 with the Codespace port set to Public.\n"
            "  /__save would be reachable from the public internet.\n"
            "  Fix one of:\n"
            "    gh codespace ports visibility <port>:private\n"
            "    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/serve-dashboards.py --bind 127.0.0.1\n"
        )
        return 2

    server, actual_port = _bind_server(bind, args.port, handler)
    # The redirect target for bare "/" — read by do_GET. Without it the plugin
    # dir (which has no index.html) renders as a directory listing.
    server._dash_path = DASH_PATH

    # Generate the per-process CSRF token + build the Origin/Host allow-lists
    # before the server can take a single request. State-changing POSTs require
    # the token in the X-CSRF-Token header (belt-and-suspenders on the Origin
    # guard); the dashboard JS fetches it from GET /__csrf on load.
    # NOTE: keyed on actual_port, not args.port — a fallback bind would
    # otherwise allow-list a port we are not listening on and reject every POST.
    global _ALLOWED_HOSTS, _ALLOWED_ORIGINS, _CSRF_TOKEN
    _CSRF_TOKEN = secrets.token_urlsafe(32)
    _ALLOWED_HOSTS = {f"127.0.0.1:{actual_port}", f"localhost:{actual_port}", "127.0.0.1", "localhost"}
    _ALLOWED_ORIGINS = {f"http://127.0.0.1:{actual_port}", f"http://localhost:{actual_port}"}
    if codespace:
        _fwd = f"{codespace}-{actual_port}.{domain}"
        _ALLOWED_HOSTS.add(_fwd)
        _ALLOWED_ORIGINS.add(f"https://{_fwd}")

    local_url = f"http://127.0.0.1:{actual_port}{DASH_PATH}"
    print(f"serve-dashboards (plugin): serving {PLUGIN_DIR}")
    print(f"  project root (writes here): {PROJECT_ROOT}")
    print(f"  local URL: {local_url}  (bound to {bind})")
    print("  POST /__save  - writes an allow-listed file under .ravenclaude/ + auto-applies")
    print("  GET  /__read  - hydrates the dashboard from your committed config")
    print("  GET  /__saga  - read-only Review-log feed from .ravenclaude/runs/thing/ (?limit=N, default 200)")
    print("  GET  /__runs  - read-only Activity feed from .ravenclaude/runs/<id>/ (?limit=N, default 200)")
    print("  POST /__classify - command-review 'Test a command' simulator (read-only)")

    phone_url = None
    if codespace:
        phone_url = f"https://{codespace}-{actual_port}.{domain}{DASH_PATH}"
        print("\n  Codespace forwarded URL — open it via the Ports panel -> Open in Browser")
        print("  (that handles the GitHub auth; a raw paste needs you already signed in):")
        print(f"  {phone_url}")
        print("  Security: keep this forwarded port PRIVATE — /__save writes files + applies the posture.")
        print(f"  Verify with: gh codespace ports list -c {codespace}  (visibility column must read 'private')")
    if phone_url:
        print()
        if _print_qr(phone_url):
            print("  ^ scan with your phone camera to open the dashboard there.")
        else:
            print("  (For a scannable QR code here, run: pip install qrcode)")

    # Auto-open the browser on local/desktop runs (parity with the root dev
    # server). In a Codespace the container has no display and VS Code's
    # onAutoForward: openBrowser handles the forwarded port, so skip it there.
    # Opens DASH_PATH, never "/" — the point is to land on the dashboard.
    if not args.no_open and not codespace:
        print(f"\n  Opening your browser at {local_url} ...")
        try:
            webbrowser.open(local_url)
        except Exception:
            pass  # silently fall back to the printed URL

    print("\n  Ctrl+C to stop.")
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
