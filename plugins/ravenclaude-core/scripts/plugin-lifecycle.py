#!/usr/bin/env python3
"""plugin-lifecycle.py — the read/write engine for the plugin-lifecycle ledger.

Owns ``.ravenclaude/plugin-lifecycle.json`` (M6: gitignored / local-only) — a
per-project record of which installed RavenClaude plugins are actually being
USED, so a session can surface "these N plugins have been unused for >=90 days"
and (opt-in, default OFF) act on it. The engine is the load-bearing, fully
self-testable core; two thin bash hook bodies wire it into Claude Code events
(scripts/plugin-lifecycle-telemetry.sh, scripts/plugin-lifecycle-sweep.sh).

Schema (schema_version 1):

    {
      "schema_version": 1,
      "plugins": {
        "name@marketplace": {
          "last_used_at": "2026-09-15T00:00:00Z",
          "last_used_signal": "skill|agent|slash|install|seed",
          "status": "active|deprecated",
          "pinned": false
        }
      },
      "sweep": { "last_run_at": null, "last_actions": [] }
    }

── The Matthew locks (HARD — every one is baked in here, non-overridable) ──────
  M1  unused_days default 90.
  M2  auto_uninstall default OFF (absent => off).
  M3  ravenclaude-core is NEVER auto-removed — not even with auto_uninstall on
      AND empty pins. This is a code constant, not a posture value.
  M4  auto-install allowlist is the `ravenclaude` marketplace ONLY.
  M5  ask-first default — auto_install is `off | ask | auto`; absent/unknown => off.
      `auto` is honored ONLY when explicitly set (Option A follow-on 0.323.17);
      empty-cited auto install remains forbidden (AppSec #6).
  M6  the ledger is gitignored / local-only.
  M7  tracking defaults ON once a comfort-posture file is present.

── AppSec SHIP-WITH-CONDITIONS (DIGEST-appsec-plugin-lifecycle-2026-09-15) ─────
  1  core pin is HARD (M3).
  2  a plugin used mid-flight (this session) is skipped from uninstall
     (fail-closed).
  4  the install allowlist is the marketplace name PLUS, when available, an
     installPath under the ravenclaude plugin cache.
  6  no empty-cited install — ask/confirm, explicit auto+cited need, or Bifröst CTA.
  7  the sweep NEVER runs the cache-reset disaster-recovery command in its
     destructive mode (this file contains no such call, by construction).
  8  uninstall execute (opt-in): when auto_uninstall ON, sweep-hook may shell
     `claude plugin uninstall <name@marketplace> -y` (CLI inject via
     PLUGIN_LIFECYCLE_CLAUDE). Fail-soft on missing CLI / non-zero exit.
     Never ragnarok.

Stdlib only. Fail-safe: a corrupt/absent ledger reads as the default; a path
outside the project's ``.ravenclaude/`` is refused (path jail, no symlink
escape). Writes are atomic (tmp + rename).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA_VERSION = 1

# ── The hard constants (M3/M4/M1) — never sourced from posture ────────────────
CORE_PLUGIN = "ravenclaude-core"
CORE_MARKETPLACE = "ravenclaude"
CORE_KEY = f"{CORE_PLUGIN}@{CORE_MARKETPLACE}"
ALLOWED_MARKETPLACE = "ravenclaude"  # M4: auto-install allowlist is this marketplace only
DEFAULT_UNUSED_DAYS = 90  # M1

# Signals that count as a real "use" (bump last_used_at to now, flip -> active).
# SessionStart presence and dashboard open are DELIBERATELY not in this set.
USE_SIGNALS = ("skill", "agent", "slash")
# First-sighting markers (do not clobber a real use).
SEED_SIGNALS = ("install", "seed")
ALL_SIGNALS = USE_SIGNALS + SEED_SIGNALS

LEDGER_NAME = "plugin-lifecycle.json"


class LifecycleError(Exception):
    """Raised for a path-jail violation or an unrecoverable engine error."""


# ── time helpers ──────────────────────────────────────────────────────────────
def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(value: str):
    if not value:
        return None
    v = value.strip()
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(v)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


# ── path jail (M6 + AppSec: no symlink escape) ────────────────────────────────
def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_ledger_path(project_dir: str) -> Path:
    """Return the jailed ledger path under <project>/.ravenclaude/.

    Refuses if .ravenclaude or the ledger file is a symlink, or resolves
    outside the project root — a hostile symlink must not redirect a write.
    """
    proj = Path(project_dir).resolve()
    rc_dir = proj / ".ravenclaude"
    if rc_dir.is_symlink():
        raise LifecycleError("path jail: .ravenclaude is a symlink (refusing)")
    if rc_dir.exists() and not _is_within(rc_dir.resolve(), proj):
        raise LifecycleError("path jail: .ravenclaude escapes the project root")
    target = rc_dir / LEDGER_NAME
    if target.is_symlink():
        raise LifecycleError("path jail: ledger file is a symlink (refusing)")
    # Belt-and-suspenders: the resolved target must still sit under .ravenclaude.
    resolved_parent = target.parent.resolve() if target.parent.exists() else rc_dir
    if not _is_within(resolved_parent, proj):
        raise LifecycleError("path jail: ledger parent escapes the project root")
    return target


# ── ledger load/save ──────────────────────────────────────────────────────────
def default_ledger() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "plugins": {},
        "sweep": {"last_run_at": None, "last_actions": []},
    }


def load_ledger(path: Path) -> dict:
    if not path.exists():
        return default_ledger()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        # Fail-safe: a corrupt ledger reads as default rather than crashing a hook.
        return default_ledger()
    if not isinstance(data, dict):
        return default_ledger()
    data.setdefault("schema_version", SCHEMA_VERSION)
    if not isinstance(data.get("plugins"), dict):
        data["plugins"] = {}
    sweep = data.get("sweep")
    if not isinstance(sweep, dict):
        data["sweep"] = {"last_run_at": None, "last_actions": []}
    else:
        sweep.setdefault("last_run_at", None)
        if not isinstance(sweep.get("last_actions"), list):
            sweep["last_actions"] = []
    return data


def save_ledger(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".plugin-lifecycle.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
            fh.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass


# ── key helpers ───────────────────────────────────────────────────────────────
def make_key(plugin: str, marketplace: str) -> str:
    plugin = (plugin or "").strip()
    marketplace = (marketplace or ALLOWED_MARKETPLACE).strip() or ALLOWED_MARKETPLACE
    return f"{plugin}@{marketplace}"


def plugin_of(key: str) -> str:
    return key.split("@", 1)[0]


def is_core_key(key: str) -> bool:
    return plugin_of(key) == CORE_PLUGIN


# ── minimal posture parse (no PyYAML in a consumer env) ───────────────────────
def _coerce_bool(value: str, default: bool) -> bool:
    v = (value or "").strip().strip('"').strip("'").lower()
    if v in ("on", "true", "yes", "1"):
        return True
    if v in ("off", "false", "no", "0"):
        return False
    return default


def read_posture_lifecycle(project_dir: str) -> dict:
    """Read the `plugin_lifecycle:` block from .ravenclaude/comfort-posture.yaml.

    Returns a normalized dict with the M-locked defaults applied:
        tracking      bool  (M7: default True when a posture file is present)
        unused_days   int   (M1: default 90)
        auto_uninstall bool (M2: default False)
        auto_install  str   (M5: "off"|"ask"|"auto"; unknown/absent -> "off")
        pins          list[str]

    No posture file -> tracking False (opt-in by presence, like every other knob).
    """
    result = {
        "posture_present": False,
        "tracking": False,
        "unused_days": DEFAULT_UNUSED_DAYS,
        "auto_uninstall": False,
        "auto_install": "off",
        "pins": [],
    }
    cfg = Path(project_dir) / ".ravenclaude" / "comfort-posture.yaml"
    if not cfg.exists():
        return result
    result["posture_present"] = True
    result["tracking"] = True  # M7: default ON once a posture exists
    try:
        lines = cfg.read_text(encoding="utf-8").splitlines()
    except OSError:
        return result

    in_block = False
    block_indent = 0
    in_pins = False
    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()
        if not in_block:
            if stripped.startswith("plugin_lifecycle:") and not stripped.startswith("#"):
                in_block = True
                block_indent = len(line) - len(line.lstrip())
            continue
        if stripped == "" or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= block_indent:
            break  # dedented out of the block
        if in_pins:
            item = stripped
            if item.startswith("- "):
                val = item[2:].strip().strip('"').strip("'")
                if val:
                    result["pins"].append(val)
                continue
            else:
                in_pins = False  # fall through to key handling
        if ":" not in stripped:
            continue
        key, _, val = stripped.partition(":")
        key = key.strip()
        val = val.strip()
        if val and not val.startswith("[") and "#" in val:
            val = val.split("#", 1)[0].strip()
        if key == "tracking":
            result["tracking"] = _coerce_bool(val, True)
        elif key == "unused_days":
            try:
                result["unused_days"] = max(0, int(val))
            except ValueError:
                pass
        elif key == "auto_uninstall":
            result["auto_uninstall"] = _coerce_bool(val, False)
        elif key == "auto_install":
            v = val.strip().strip('"').strip("'").lower()
            # M5 follow-on: off|ask|auto. Unknown -> off (never invent auto).
            result["auto_install"] = v if v in ("off", "ask", "auto") else "off"
        elif key == "pins":
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1]
                result["pins"] = [
                    p.strip().strip('"').strip("'") for p in inner.split(",") if p.strip()
                ]
            elif val == "":
                in_pins = True
    return result


def _pin_matches(pin: str, key: str) -> bool:
    pin = (pin or "").strip()
    if not pin:
        return False
    return pin == key or pin == plugin_of(key)


# ── record (telemetry) ────────────────────────────────────────────────────────
def cmd_record(args) -> int:
    if args.signal not in ALL_SIGNALS:
        _err(f"unknown signal: {args.signal!r} (expected one of {', '.join(ALL_SIGNALS)})")
        return 2
    path = resolve_ledger_path(args.project)
    data = load_ledger(path)
    key = make_key(args.plugin, args.marketplace)
    plugins = data["plugins"]
    existing = plugins.get(key)

    if args.signal in SEED_SIGNALS:
        # First-sighting marker: never clobber a real prior use.
        if existing is None:
            plugins[key] = {
                "last_used_at": (args.installed_at or now_iso()),
                "last_used_signal": args.signal,
                "status": "active",
                "pinned": is_core_key(key),  # core is always pinned (M3)
            }
    else:
        # A real use: bump timestamp, flip active, preserve pinned.
        row = existing or {"pinned": is_core_key(key)}
        row["last_used_at"] = now_iso()
        row["last_used_signal"] = args.signal
        row["status"] = "active"
        row.setdefault("pinned", is_core_key(key))
        if is_core_key(key):
            row["pinned"] = True
        plugins[key] = row

    save_ledger(path, data)

    # Mid-flight session marker (AppSec #2): a plugin used THIS session is skipped
    # from uninstall by the sweep. Only real uses are recorded here.
    if args.signal in USE_SIGNALS and args.session_marker:
        _append_session_used(args.session_marker, key)

    if args.json:
        print(json.dumps({"recorded": key, "signal": args.signal}))
    return 0


def _append_session_used(marker_path: str, key: str) -> None:
    try:
        p = Path(marker_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        existing = set()
        if p.exists():
            existing = {
                ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()
            }
        if key not in existing:
            with p.open("a", encoding="utf-8") as fh:
                fh.write(key + "\n")
    except OSError:
        pass  # fail-safe: a missing marker just means no mid-flight skips from here


def _read_session_used(marker_path: str) -> set:
    if not marker_path:
        return set()
    try:
        p = Path(marker_path)
        if not p.exists():
            return set()
        return {ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()}
    except OSError:
        return set()


# ── seed (explicit, bulk) ─────────────────────────────────────────────────────
def cmd_seed(args) -> int:
    path = resolve_ledger_path(args.project)
    data = load_ledger(path)
    plugins = data["plugins"]
    names = [p.strip() for p in (args.plugins or "").split(",") if p.strip()]
    seeded = []
    for name in names:
        key = make_key(name, args.marketplace)
        if key not in plugins:
            plugins[key] = {
                "last_used_at": (args.installed_at or now_iso()),
                "last_used_signal": "seed",
                "status": "active",
                "pinned": is_core_key(key),
            }
            seeded.append(key)
    save_ledger(path, data)
    if args.json:
        print(json.dumps({"seeded": seeded}))
    else:
        print(f"seeded {len(seeded)} new row(s)")
    return 0


# ── telemetry (parse a hook payload from stdin) ───────────────────────────────
def cmd_telemetry(args) -> int:
    """Read a Claude Code hook payload on stdin, derive (plugin, signal), record.

    Agent/Task -> signal=agent, plugin = prefix of subagent_type before ':'.
    Skill      -> signal=skill, plugin = prefix of skill/command before ':'.
    prompt     -> signal=slash, plugin = prefix of a leading '/ns:cmd' token.
    Anything without a resolvable plugin prefix is a silent no-op (built-in
    agents like general-purpose / claude carry no plugin namespace).
    """
    posture = read_posture_lifecycle(args.project)
    if not posture["tracking"]:
        return 0  # tracking off -> never bump
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    if not isinstance(payload, dict):
        return 0

    tool = payload.get("tool_name") or payload.get("toolName") or ""
    tool_input = payload.get("tool_input") or payload.get("toolArgs") or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except json.JSONDecodeError:
            tool_input = {}
    if not isinstance(tool_input, dict):
        tool_input = {}

    plugin = None
    signal = None
    if tool in ("Agent", "Task"):
        signal = "agent"
        plugin = _prefix_before_colon(
            tool_input.get("subagent_type") or tool_input.get("subagentType")
        )
    elif tool == "Skill":
        signal = "skill"
        plugin = _prefix_before_colon(tool_input.get("skill") or tool_input.get("command"))
    else:
        prompt = payload.get("prompt") or payload.get("user_prompt") or ""
        if isinstance(prompt, str) and prompt.lstrip().startswith("/"):
            token = prompt.lstrip().split()[0][1:]  # drop leading '/'
            plugin = _prefix_before_colon(token)
            signal = "slash"

    if not plugin or not signal:
        return 0

    key = make_key(plugin, args.marketplace)
    path = resolve_ledger_path(args.project)
    data = load_ledger(path)
    row = data["plugins"].get(key) or {"pinned": is_core_key(key)}
    row["last_used_at"] = now_iso()
    row["last_used_signal"] = signal
    row["status"] = "active"
    row.setdefault("pinned", is_core_key(key))
    if is_core_key(key):
        row["pinned"] = True
    data["plugins"][key] = row
    save_ledger(path, data)

    if args.session_marker:
        _append_session_used(args.session_marker, key)
    return 0


def _prefix_before_colon(value):
    if not value or not isinstance(value, str):
        return None
    v = value.strip()
    if ":" in v:
        return v.split(":", 1)[0].strip() or None
    return None  # no namespace => not a plugin-scoped invocation


# ── deprecation / sweep planning ──────────────────────────────────────────────
def compute_deprecated(data: dict, unused_days: int, now: datetime) -> list:
    cutoff = now - timedelta(days=unused_days)
    out = []
    for key, row in data["plugins"].items():
        if is_core_key(key):
            continue  # M3: core is never deprecated
        if not isinstance(row, dict):
            continue
        if row.get("pinned"):
            continue
        last = _parse_iso(row.get("last_used_at", ""))
        if last is None:
            # No parseable timestamp -> treat as unused (deprecated candidate).
            out.append(key)
            continue
        if last < cutoff:
            out.append(key)
    return sorted(out)


def build_sweep_plan(args, data, posture, now, session_used) -> dict:
    unused_days = posture["unused_days"]
    auto_uninstall = posture["auto_uninstall"]
    pins = list(posture["pins"])
    deprecated = compute_deprecated(data, unused_days, now)

    skipped = {"core": [], "pinned": [], "mid_flight": [], "unknown_requires": []}
    would_uninstall = []

    # Core is never in `deprecated` (compute_deprecated excludes it), but surface
    # the hard pin explicitly so the plan documents M3 even if core is present.
    if CORE_KEY in data["plugins"]:
        skipped["core"].append(CORE_KEY)

    # A reverse-dependency map, when supplied, lets a plugin with no dependents be
    # eligible; absent it, EVERY plugin is `unknown_requires` (fail-closed).
    requires_map = _load_requires_map(args.requires_map)

    for key in deprecated:
        if is_core_key(key):
            skipped["core"].append(key)
            continue
        if any(_pin_matches(p, key) for p in pins) or data["plugins"][key].get("pinned"):
            skipped["pinned"].append(key)
            continue
        if key in session_used:
            skipped["mid_flight"].append(key)  # AppSec #2
            continue
        dep_clear = args.assume_no_deps or (requires_map is not None and not requires_map.get(key))
        if not dep_clear:
            skipped["unknown_requires"].append(key)  # fail-closed on unknown requires
            continue
        would_uninstall.append(key)

    # M2/M3: uninstall only ever populated when auto_uninstall is ON; core can
    # never reach it regardless (excluded above and by compute_deprecated).
    if not auto_uninstall:
        would_uninstall = []

    for bucket in skipped.values():
        bucket[:] = sorted(set(bucket))

    return {
        "tracking": posture["tracking"],
        "auto_uninstall": auto_uninstall,
        "auto_install": posture["auto_install"],
        "unused_days": unused_days,
        "deprecated": deprecated,
        "would_uninstall": sorted(would_uninstall),
        "skipped": skipped,
    }


def _load_requires_map(path):
    if not path:
        return None
    try:
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def cmd_deprecated(args) -> int:
    posture = read_posture_lifecycle(args.project)
    unused_days = args.unused_days if args.unused_days is not None else posture["unused_days"]
    now = _parse_iso(args.now) or datetime.now(timezone.utc)
    path = resolve_ledger_path(args.project)
    data = load_ledger(path)
    dep = compute_deprecated(data, unused_days, now)
    if args.json:
        print(json.dumps({"deprecated": dep, "unused_days": unused_days}))
    else:
        for k in dep:
            print(k)
    return 0


def cmd_sweep_plan(args) -> int:
    posture = read_posture_lifecycle(args.project)
    now = _parse_iso(args.now) or datetime.now(timezone.utc)
    path = resolve_ledger_path(args.project)
    data = load_ledger(path)
    session_used = _read_session_used(args.session_used_file)
    if args.session_used:
        session_used |= {s.strip() for s in args.session_used.split(",") if s.strip()}
    plan = build_sweep_plan(args, data, posture, now, session_used)
    if args.json:
        print(json.dumps(plan))
    else:
        _print_plan_human(plan)
    return 0


def _print_plan_human(plan: dict) -> None:
    n = len(plan["deprecated"])
    if n == 0:
        print(f"plugin-lifecycle: no plugins unused for >= {plan['unused_days']} days.")
        return
    print(
        f"plugin-lifecycle: {n} plugin(s) unused for >= {plan['unused_days']} days: "
        + ", ".join(plan["deprecated"])
    )
    if plan["auto_uninstall"]:
        if plan["would_uninstall"]:
            print("  would uninstall (auto_uninstall on): " + ", ".join(plan["would_uninstall"]))
        else:
            print(
                "  auto_uninstall on, but 0 eligible (fail-closed on unknown deps / pins / mid-flight)."
            )
    else:
        print("  auto_uninstall off -> notice only, 0 uninstalls.")


def cmd_record_sweep(args) -> int:
    now = args.now or now_iso()
    path = resolve_ledger_path(args.project)
    data = load_ledger(path)
    actions = []
    if args.actions:
        try:
            parsed = json.loads(args.actions)
            if isinstance(parsed, list):
                actions = parsed
        except json.JSONDecodeError:
            actions = []
    data["sweep"]["last_run_at"] = now
    data["sweep"]["last_actions"] = actions
    save_ledger(path, data)
    if args.json:
        print(json.dumps({"last_run_at": now, "last_actions": actions}))
    return 0


def _claude_bin() -> str:
    """Host CLI for plugin install/uninstall. Tests inject via PLUGIN_LIFECYCLE_CLAUDE."""
    return os.environ.get("PLUGIN_LIFECYCLE_CLAUDE", "claude").strip() or "claude"


def _run_plugin_cli(argv: list, timeout: float = 120.0) -> dict:
    """Run ``claude plugin …`` (or injected mock). Never shells ragnarok/cache-reset.

    Returns {ok, exit_code, reason, argv, stdout, stderr}.
    """
    result = {
        "ok": False,
        "exit_code": None,
        "reason": "",
        "argv": list(argv),
        "stdout": "",
        "stderr": "",
    }
    # Hard refuse: never allow DR cache-reset tokens through this helper.
    joined = " ".join(argv).lower()
    if "ragnarok" in joined or "reset-plugin-cache" in joined:
        result["reason"] = "refused_ragnarok_or_cache_reset"
        return result
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        result["reason"] = "cli_missing"
        return result
    except subprocess.TimeoutExpired:
        result["reason"] = "timeout"
        return result
    except OSError as exc:
        result["reason"] = f"os_error:{exc}"
        return result
    result["exit_code"] = proc.returncode
    result["stdout"] = (proc.stdout or "")[-2000:]
    result["stderr"] = (proc.stderr or "")[-2000:]
    if proc.returncode == 0:
        result["ok"] = True
        result["reason"] = "ok"
    else:
        result["reason"] = f"exit_{proc.returncode}"
    return result


def execute_uninstall(key: str) -> dict:
    """Opt-in uninstall via ``claude plugin uninstall <key> -y`` (non-interactive)."""
    if is_core_key(key):
        return {
            "key": key,
            "action": "uninstall",
            "executed": False,
            "reason": "core_hard_pin",
            "argv": [],
        }
    bin_ = _claude_bin()
    argv = [bin_, "plugin", "uninstall", key, "-y"]
    ran = _run_plugin_cli(argv)
    return {
        "key": key,
        "action": "uninstall",
        "executed": bool(ran["ok"]),
        "exit_code": ran["exit_code"],
        "reason": ran["reason"],
        "argv": ran["argv"],
    }


def execute_install(key: str) -> dict:
    """Opt-in install via ``claude plugin install <key> -y`` (ravenclaude allowlist upstream)."""
    bin_ = _claude_bin()
    argv = [bin_, "plugin", "install", key, "-y"]
    ran = _run_plugin_cli(argv)
    return {
        "key": key,
        "action": "install",
        "executed": bool(ran["ok"]),
        "exit_code": ran["exit_code"],
        "reason": ran["reason"],
        "argv": ran["argv"],
    }


def cmd_sweep_hook(args) -> int:
    """SessionStart sweep: mark deprecated, plan, and (opt-in) execute uninstalls.

    When ``auto_uninstall`` is OFF (default), records an empty execute list /
    plan-only notice and never shells uninstall (M2).

    When ON, executes fail-closed ``would_uninstall`` via
    ``claude plugin uninstall <name@marketplace> -y`` (PLUGIN_LIFECYCLE_CLAUDE
    inject for tests). NEVER runs cache-reset DR / ragnarok (AppSec #7).
    ``--plan-only`` forces the pre-0.323.17 record-only path (tests / dry).
    """
    posture = read_posture_lifecycle(args.project)
    if not posture["tracking"]:
        return 0
    now = _parse_iso(args.now) or datetime.now(timezone.utc)
    path = resolve_ledger_path(args.project)
    data = load_ledger(path)
    session_used = _read_session_used(args.session_used_file)

    # Refresh status labels off the age computation (benign; a later use flips back).
    dep_set = set(compute_deprecated(data, posture["unused_days"], now))
    for key, row in data["plugins"].items():
        if not isinstance(row, dict) or is_core_key(key):
            continue
        row["status"] = "deprecated" if key in dep_set else "active"

    plan = build_sweep_plan(args, data, posture, now, session_used)
    plan_only = bool(getattr(args, "plan_only", False))
    actions = []
    executed_any = False

    if plan["auto_uninstall"] and plan["would_uninstall"] and not plan_only:
        for k in plan["would_uninstall"]:
            actions.append(execute_uninstall(k))
            if actions[-1].get("executed"):
                executed_any = True
    else:
        # Plan-only rows (OFF path, --plan-only, or empty eligible set).
        for k in plan["would_uninstall"]:
            actions.append(
                {
                    "key": k,
                    "action": "would_uninstall",
                    "executed": False,
                    "reason": (
                        "plan_only_flag"
                        if plan_only
                        else ("auto_uninstall_off" if not plan["auto_uninstall"] else "no_execute")
                    ),
                }
            )

    data["sweep"]["last_run_at"] = now_iso()
    data["sweep"]["last_actions"] = actions
    save_ledger(path, data)

    plan_out = dict(plan)
    plan_out["actions"] = actions
    plan_out["executed_any"] = executed_any

    if args.json:
        print(json.dumps(plan_out))
    else:
        _print_plan_human(plan)
        if executed_any:
            print("  executed uninstall(s); run /reload-plugins before relying on plugin set.")
        elif plan["auto_uninstall"] and plan["would_uninstall"] and not plan_only:
            # ON but every attempt failed soft
            reasons = sorted({a.get("reason", "?") for a in actions})
            print("  auto_uninstall on but 0 executed (" + ", ".join(reasons) + ").")
    return 0


# ── allowlist / ask-install (P3) ──────────────────────────────────────────────
def _install_path_ok(install_path: str) -> bool:
    norm = str(Path(install_path)).replace("\\", "/")
    # Accept ".../plugins/cache/ravenclaude/..." or ".../ravenclaude/<plugin>/...".
    return "/cache/ravenclaude/" in norm or "/plugins/cache/ravenclaude/" in norm


def cmd_allowlist_check(args) -> int:
    """M4/AppSec #4: allow only the `ravenclaude` marketplace, and (when an
    installPath is supplied) require it to live under a ravenclaude plugin
    cache. Exit 0 = allowed, exit 3 = rejected.
    """
    marketplace = (args.marketplace or "").strip() or ALLOWED_MARKETPLACE
    allowed = marketplace == ALLOWED_MARKETPLACE
    reason = (
        "ok"
        if allowed
        else f"marketplace {marketplace!r} is not the allowlisted {ALLOWED_MARKETPLACE!r}"
    )

    if allowed and args.install_path and not _install_path_ok(args.install_path):
        allowed = False
        reason = f"install path {args.install_path!r} is not under a ravenclaude plugin cache"

    result = {
        "allowed": allowed,
        "reason": reason,
        "plugin": args.plugin,
        "marketplace": marketplace,
    }
    print(json.dumps(result))
    return 0 if allowed else 3


def cmd_ask_install(args) -> int:
    """P3: plan (and optionally execute) an install of a needed ravenclaude plugin.

    Modes (M5 follow-on):
      off  -> Bifröst CTA only (default / absent)
      ask  -> confirm plan when cited need present; else CTA (AppSec #6)
      auto -> when explicitly set + cited need: mode auto; optional --execute
             runs ``claude plugin install <key> -y``. Uncited auto -> CTA.

    Rejects a non-ravenclaude plugin outright (M4). Never claims Bifröst executed.
    """
    posture = read_posture_lifecycle(args.project)
    marketplace = (args.marketplace or "").strip() or ALLOWED_MARKETPLACE

    # M4 allowlist gate first.
    if marketplace != ALLOWED_MARKETPLACE:
        print(
            json.dumps(
                {
                    "mode": "rejected",
                    "allowed": False,
                    "reason": f"{marketplace!r} is not the allowlisted {ALLOWED_MARKETPLACE!r} marketplace",
                    "plugin": args.plugin,
                }
            )
        )
        return 3

    if args.install_path and not _install_path_ok(args.install_path):
        print(
            json.dumps(
                {
                    "mode": "rejected",
                    "allowed": False,
                    "reason": f"install path {args.install_path!r} is not under a ravenclaude cache",
                    "plugin": args.plugin,
                }
            )
        )
        return 3

    key = make_key(args.plugin, marketplace)
    install_cmd = f"/plugin install {key}"
    reload_cmd = "/reload-plugins"
    mode = posture["auto_install"]
    do_execute = bool(getattr(args, "execute", False))

    if mode == "ask":
        if not args.need:
            # AppSec #6: no empty-cited install — downgrade to CTA when uncited.
            print(
                json.dumps(
                    {
                        "mode": "cta",
                        "allowed": True,
                        "plugin": args.plugin,
                        "marketplace": marketplace,
                        "confirm_required": False,
                        "install_cmd": install_cmd,
                        "reload_cmd": reload_cmd,
                        "note": "no cited need -> Bifröst CTA only (no confirm path without a citation).",
                    }
                )
            )
            return 0
        print(
            json.dumps(
                {
                    "mode": "ask",
                    "allowed": True,
                    "plugin": args.plugin,
                    "marketplace": marketplace,
                    "cited_need": args.need,  # AppSec #6: never an empty-cited install
                    "confirm_required": True,
                    "install_cmd": install_cmd,
                    "reload_cmd": reload_cmd,  # AppSec #5: reload before claiming usable
                    "note": "ask-first: confirm with the user, run install, then reload BEFORE use.",
                }
            )
        )
        return 0

    if mode == "auto":
        if not args.need:
            print(
                json.dumps(
                    {
                        "mode": "cta",
                        "allowed": True,
                        "plugin": args.plugin,
                        "marketplace": marketplace,
                        "confirm_required": False,
                        "install_cmd": install_cmd,
                        "reload_cmd": reload_cmd,
                        "note": "auto_install auto but no cited need -> Bifröst CTA only (AppSec #6).",
                    }
                )
            )
            return 0
        payload = {
            "mode": "auto",
            "allowed": True,
            "plugin": args.plugin,
            "marketplace": marketplace,
            "cited_need": args.need,
            "confirm_required": False,
            "install_cmd": install_cmd,
            "cli_install_argv": [_claude_bin(), "plugin", "install", key, "-y"],
            "reload_cmd": reload_cmd,
            "note": "auto_install auto + cited need: may execute claude plugin install -y; reload BEFORE use.",
        }
        if do_execute:
            ran = execute_install(key)
            payload["execution"] = ran
            if ran.get("executed"):
                payload["note"] = (
                    "auto install executed; run /reload-plugins before claiming usable."
                )
            else:
                payload["note"] = (
                    f"auto install not executed ({ran.get('reason')}); "
                    "fall back to ask/Bifröst. Never ragnarok."
                )
        print(json.dumps(payload))
        return 0

    # auto_install off (default) -> Bifröst CTA only.
    print(
        json.dumps(
            {
                "mode": "cta",
                "allowed": True,
                "plugin": args.plugin,
                "marketplace": marketplace,
                "install_cmd": install_cmd,
                "reload_cmd": reload_cmd,
                "note": "auto_install off -> open the dashboard Bifröst tab (#/bifrost) to install manually.",
            }
        )
    )
    return 0


# ── list / init / posture-get ─────────────────────────────────────────────────
def cmd_list(args) -> int:
    path = resolve_ledger_path(args.project)
    data = load_ledger(path)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        for key in sorted(data["plugins"]):
            row = data["plugins"][key]
            print(
                f"{key}\t{row.get('status', '?')}\t{row.get('last_used_signal', '?')}\t"
                f"{row.get('last_used_at', '?')}\tpinned={row.get('pinned', False)}"
            )
    return 0


def cmd_init(args) -> int:
    path = resolve_ledger_path(args.project)
    if not path.exists():
        save_ledger(path, default_ledger())
    print(str(path))
    return 0


def cmd_posture_get(args) -> int:
    print(json.dumps(read_posture_lifecycle(args.project)))
    return 0


def _err(msg: str) -> None:
    print(f"plugin-lifecycle: {msg}", file=sys.stderr)


# ── argparse ──────────────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="plugin-lifecycle ledger engine")
    p.add_argument("--project", default=os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_common(sp):
        sp.add_argument("--marketplace", default=ALLOWED_MARKETPLACE)
        sp.add_argument("--json", action="store_true")

    sp = sub.add_parser("init")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("record")
    add_common(sp)
    sp.add_argument("--plugin", required=True)
    sp.add_argument("--signal", required=True)
    sp.add_argument("--installed-at", dest="installed_at", default=None)
    sp.add_argument("--session-marker", dest="session_marker", default=None)
    sp.set_defaults(func=cmd_record)

    sp = sub.add_parser("seed")
    add_common(sp)
    sp.add_argument("--plugins", required=True, help="comma-separated plugin names")
    sp.add_argument("--installed-at", dest="installed_at", default=None)
    sp.set_defaults(func=cmd_seed)

    sp = sub.add_parser("telemetry")
    add_common(sp)
    sp.add_argument("--session-marker", dest="session_marker", default=None)
    sp.set_defaults(func=cmd_telemetry)

    sp = sub.add_parser("deprecated")
    add_common(sp)
    sp.add_argument("--unused-days", dest="unused_days", type=int, default=None)
    sp.add_argument("--now", default=None)
    sp.set_defaults(func=cmd_deprecated)

    sp = sub.add_parser("sweep-plan")
    add_common(sp)
    sp.add_argument("--now", default=None)
    sp.add_argument("--session-used", dest="session_used", default=None)
    sp.add_argument("--session-used-file", dest="session_used_file", default=None)
    sp.add_argument("--assume-no-deps", dest="assume_no_deps", action="store_true")
    sp.add_argument("--requires-map", dest="requires_map", default=None)
    sp.set_defaults(func=cmd_sweep_plan)

    sp = sub.add_parser("sweep-hook")
    add_common(sp)
    sp.add_argument("--now", default=None)
    sp.add_argument("--session-used-file", dest="session_used_file", default=None)
    sp.add_argument("--assume-no-deps", dest="assume_no_deps", action="store_true")
    sp.add_argument("--requires-map", dest="requires_map", default=None)
    sp.add_argument(
        "--plan-only",
        dest="plan_only",
        action="store_true",
        help="record plan only; never shell claude plugin uninstall (tests / dry)",
    )
    sp.set_defaults(func=cmd_sweep_hook)

    sp = sub.add_parser("record-sweep")
    add_common(sp)
    sp.add_argument("--now", default=None)
    sp.add_argument("--actions", default=None)
    sp.set_defaults(func=cmd_record_sweep)

    sp = sub.add_parser("allowlist-check")
    add_common(sp)
    sp.add_argument("--plugin", required=True)
    sp.add_argument("--install-path", dest="install_path", default=None)
    sp.set_defaults(func=cmd_allowlist_check)

    sp = sub.add_parser("ask-install")
    add_common(sp)
    sp.add_argument("--plugin", required=True)
    sp.add_argument("--install-path", dest="install_path", default=None)
    sp.add_argument("--need", default=None, help="cited need (AppSec #6: no empty-cited install)")
    sp.add_argument(
        "--execute",
        action="store_true",
        help="when auto_install: auto + cited need, run claude plugin install -y",
    )
    sp.set_defaults(func=cmd_ask_install)

    sp = sub.add_parser("list")
    add_common(sp)
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("posture-get")
    sp.set_defaults(func=cmd_posture_get)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except LifecycleError as exc:
        _err(str(exc))
        return 4
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    sys.exit(main())
