#!/usr/bin/env python3
"""
serve-dashboards.py — local HTTP server for the per-plugin dashboards.

Serves the marketplace repo as static files (same as `python3 -m http.server`)
AND adds a POST `/__save` endpoint so dashboards can write YAML / JSON
directly into the project's `.ravenclaude/` directory without a copy-paste
step.

Designed for:
  - Local development in a GitHub Codespace (port-forwarded URL is HTTPS,
    which means File System Access API + clipboard work natively). On start
    we print a QR code of the forwarded URL so you can open the dashboard —
    and run "Save & apply" for real — from your phone. (The README/Pages link
    is a static host and CANNOT apply; it returns 405 on the save POST.)
  - Local development on a developer machine (open http://localhost:PORT/)

NOT designed for:
  - Multi-user deployment (no auth, no rate limiting, no audit)
  - Production hosting (use GitHub Pages or any static host for read-only)

Save flow:
  Browser POSTs to /__save with a JSON body:
    {
      "path": ".ravenclaude/comfort-posture.yaml",   // relative to repo root
      "content": "schema_version: 3\\n..."
    }
  Server validates the path is in the whitelist + within REPO_ROOT,
  creates parent directories, writes the file, returns 200 + the absolute
  path it wrote to.

Path whitelist (security: prevents arbitrary write):
  - .ravenclaude/comfort-posture.yaml
  - .ravenclaude/environment-context.md
  Add new entries to ALLOWED_TARGETS below as new YAML dashboards ship.

Usage:
    python3 scripts/serve-dashboards.py            # default port 8000
    python3 scripts/serve-dashboards.py --port 8080
    python3 scripts/serve-dashboards.py --bind 0.0.0.0   # accept from LAN
"""

from __future__ import annotations

import argparse
import errno
import json
import os
import subprocess
import sys
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Pipeline-tab editable config files. JSON-validated before write (a malformed
# write to .repo-layout.json would brick the layout gate, so we never persist
# unparseable JSON or a structurally-wrong layout file).
JSON_EDIT_TARGETS = {
    ".repo-layout.json",
    ".ravenclaude/task-scope.json",
}
ALLOWED_TARGETS = {
    ".ravenclaude/comfort-posture.yaml",
    ".ravenclaude/environment-context.md",
} | JSON_EDIT_TARGETS

# Saving the comfort posture immediately re-runs the translator so
# .claude/settings.json reflects the new YAML without a manual /set-posture.
POSTURE_TARGET = ".ravenclaude/comfort-posture.yaml"
APPLY_SCRIPT = (
    REPO_ROOT / "plugins" / "ravenclaude-core" / "scripts" / "apply-comfort-posture.py"
)

# POST /__run lets the dashboard's "Install & Update" buttons run the Copilot
# bridge installer/updater with ONE click (Codespace / local dev only — this
# server is never public). Security: only these FIXED actions are runnable, each
# maps to a fixed `ravenclaude <action>` subcommand with NO caller-supplied args
# or shell, so there is no arbitrary-command surface (same spirit as the /__save
# allow-list). Mirrors the path whitelist above.
RAVENCLAUDE_SCRIPT = REPO_ROOT / "scripts" / "ravenclaude"
ALLOWED_ACTIONS = {"install", "update", "status"}

# GET /__read lets the dashboard HYDRATE its controls from the project's actual
# committed config on load (so it reflects reality, not just defaults/localStorage).
# Allow-list mirrors /__save. For YAML we also return a server-side PARSED form
# (the server has Python+yaml) so the dashboard needs no JS YAML parser.
ALLOWED_READ = {
    ".ravenclaude/comfort-posture.yaml",
    ".ravenclaude/environment-context.md",
} | JSON_EDIT_TARGETS

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


# POST /__classify powers the dashboard's "Test a command" simulator: it runs the
# REAL deterministic classifier (thing-decision.py) on the typed string so the
# preview can't drift from the engine. It does NOT execute the command — the
# string is analysed only (passed as a single argv to a read-only classifier).
THING_DECISION = (
    REPO_ROOT / "plugins" / "ravenclaude-core" / "scripts" / "thing-decision.py"
)

# ── Tier helpers for /__saga enrichment ─────────────────────────────────────
# Loaded once at module start (not per-request) using the same importlib pattern
# generate-dashboards.py uses for EMISSIONS. The tier map and escalation function
# are imported directly from thing-decision.py — single source of truth so the
# dashboard tab never drifts from the engine's own logic.
_THING_CONCERNS_SCRIPT = (
    REPO_ROOT / "plugins" / "ravenclaude-core" / "scripts" / "thing-concerns.py"
)


def _load_tier_helpers() -> tuple[dict, object, object, object]:
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

    # Load category→tier map + escalation function from thing-decision.py.
    try:
        spec = _ilu.spec_from_file_location("_td_srv", str(THING_DECISION))
        if spec and spec.loader:
            mod = _ilu.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
            cat_map = dict(getattr(mod, "_DEFAULT_CATEGORY_TIER_MAP", {}))
            escalate_fn = getattr(mod, "_escalate_tier", None)
    except Exception:
        pass

    # Load severity function + catalog from thing-concerns.py.
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


def _compute_saga_tiers(category: str, concerns_cited: list) -> tuple[str, str]:
    """Return (base_tier, final_tier) for one /__saga log entry.

    base_tier  — from the engine's category→tier map; defaults to "medium".
    final_tier — base_tier bumped by the max severity of concerns_cited using
                 the engine's own _escalate_tier function.
    """
    base = _SAGA_CAT_TIER_MAP.get(category, "medium")
    if not concerns_cited:
        return base, base

    # Find max severity among cited concerns via the catalog.
    max_sev: str | None = None
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


# Populated in main(). The write/read/run/classify endpoints check these so a
# malicious web page the user is viewing can't drive this server cross-origin: a
# 127.0.0.1 bind does NOT stop a browser from POSTing to localhost (CSRF), and a
# forged Host enables DNS-rebinding. We reject any request whose Origin (always
# sent by browsers on cross-origin POST) isn't ours, or whose Host isn't known.
_ALLOWED_HOSTS: set[str] = set()
_ALLOWED_ORIGINS: set[str] = set()


def _summarize_run(d: Path) -> dict:
    """Summarize one .ravenclaude/runs/<id>/ directory for the Activity feed.
    Reads summary.md (truncated), the structured-result status, the events line
    count, and which artifact files are present. Reads only under `d` (no root
    reference), so this is byte-identical in the root and the bundled plugin
    server — keep the two copies in sync (the parity gate guards the endpoints,
    not this helper)."""
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


class DashboardHandler(SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler + POST /__save for dashboard writes."""

    def log_message(self, format, *args):
        sys.stderr.write(
            "[%s] %s\n" % (self.log_date_time_string(), format % args)
        )

    def _local_request_ok(self) -> bool:
        """Refuse cross-origin / DNS-rebinding requests to the dashboard endpoints."""
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

    def do_HEAD(self):
        if self.path in ("/__save", "/__run", "/__classify") or self.path.startswith("/__read") or self.path.startswith("/__saga") or self.path.startswith("/__runs"):
            self.send_response(200)
            self.send_header("Allow", "GET, POST, HEAD")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        super().do_HEAD()

    def do_GET(self):
        # NOTE: static GETs are intentionally ungated. Any NEW data-returning GET
        # endpoint added here MUST call self._local_request_ok() first (as
        # _handle_read does) — do not let it ride the static path.
        if self.path in ("/", ""):
            # Redirect bare root to the dashboard page so VS Code's
            # onAutoForward: openBrowser lands on the dashboard, not a directory
            # listing.  The target path is injected by main() after it resolves
            # the actual dash_path.
            target = getattr(self.server, "_dash_path", "/plugins/ravenclaude-core/dashboard.html")
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
        if self.path.startswith("/__runs"):
            self._handle_runs()
            return
        super().do_GET()

    def _handle_read(self):
        """GET /__read?path=<allow-listed> — return a committed config file so the
        dashboard can hydrate its controls from reality. For YAML, also return a
        server-parsed JSON form (`parsed`). 404 when the file is absent."""
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(self.path).query)
        target = (qs.get("path") or [""])[0]
        if target not in ALLOWED_READ:
            self.send_error(403, f"path not in read allow-list: {target!r}")
            return
        out = (REPO_ROOT / target).resolve()
        try:
            out.relative_to(REPO_ROOT)
        except ValueError:
            self.send_error(403, "path escapes repo root")
            return
        if not out.is_file():
            self._json(404, {"path": target, "exists": False})
            return
        content = out.read_text(encoding="utf-8")
        payload = {"path": target, "exists": True, "content": content, "parsed": None}
        if target.endswith((".yaml", ".yml")):
            try:
                import yaml  # present in the devcontainer
                payload["parsed"] = yaml.safe_load(content)
            except Exception:
                payload["parsed"] = None  # dashboard falls back to defaults
        elif target.endswith(".json"):
            try:
                payload["parsed"] = json.loads(content)
            except Exception:
                payload["parsed"] = None  # dashboard falls back to defaults
        self._json(200, payload)

    def _handle_saga(self):
        """GET /__saga[?limit=N] — return the last N command-review verdicts from
        .ravenclaude/runs/thing/*.json (newest-first, capped at 500, default 200).
        Only the top-level thing-*.json files are read; the decisions/ subdir is
        ignored. Malformed files are skipped without erroring. Read-only; guarded
        by the same Origin/Host CSRF check as /__read."""
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        from urllib.parse import urlparse, parse_qs
        import glob as _glob
        import os as _os

        qs = parse_qs(urlparse(self.path).query)
        try:
            limit = max(1, min(500, int((qs.get("limit") or ["200"])[0])))
        except (ValueError, TypeError):
            limit = 200

        runs_dir = REPO_ROOT / ".ravenclaude" / "runs" / "thing"
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

    def _handle_runs(self):
        """GET /__runs[?limit=N] — recent multi-step runs from
        .ravenclaude/runs/<id>/ (newest-first by mtime, capped 500, default 200).
        The thing/ verdict dir is owned by /__saga and skipped here. Read-only;
        same Origin/Host CSRF guard as /__read."""
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        from urllib.parse import urlparse, parse_qs

        qs = parse_qs(urlparse(self.path).query)
        try:
            limit = max(1, min(500, int((qs.get("limit") or ["200"])[0])))
        except (ValueError, TypeError):
            limit = 200

        runs_dir = REPO_ROOT / ".ravenclaude" / "runs"
        records = []
        if runs_dir.is_dir():
            run_dirs = [
                d for d in runs_dir.iterdir() if d.is_dir() and d.name != "thing"
            ]
            run_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
            for d in run_dirs[:limit]:
                records.append(_summarize_run(d))
        self._json(200, records)

    def do_OPTIONS(self):
        if self.path in ("/__save", "/__run"):
            self.send_response(204)
            self.send_header("Allow", "POST, HEAD, OPTIONS")
            self.end_headers()
            return
        self.send_error(405)

    def do_POST(self):
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        if self.path == "/__run":
            self._handle_run()
            return
        if self.path == "/__classify":
            self._handle_classify()
            return
        if self.path != "/__save":
            self.send_error(404, "endpoint not found")
            return

        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 5 * 1024 * 1024:
            self.send_error(413, "request body required, max 5 MB")
            return

        body_raw = self.rfile.read(length)
        try:
            body = json.loads(body_raw.decode("utf-8"))
            target = body["path"]
            content = body["content"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as e:
            self.send_error(400, f"invalid JSON body: {e}")
            return

        # Path-traversal defense + allow-list check.
        if target not in ALLOWED_TARGETS:
            self.send_error(403, f"path not in allow-list: {target}")
            return
        out = (REPO_ROOT / target).resolve()
        try:
            out.relative_to(REPO_ROOT)
        except ValueError:
            self.send_error(403, "path escapes repo root")
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

        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8", newline="\n")

        payload = {"saved": str(out.relative_to(REPO_ROOT)), "bytes": len(content)}
        # Auto-apply: saving the posture re-runs the translator so the change
        # lands in .claude/settings.json instantly (no manual /set-posture).
        if target == POSTURE_TARGET:
            payload.update(self._apply_posture())

        response_body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def _apply_posture(self) -> dict:
        """Re-run apply-comfort-posture.py after a posture save.

        Returns a small status dict merged into the /__save JSON response so the
        dashboard can tell the user whether settings.json was updated. The file
        is already written by the time this runs, so an apply failure is reported
        (not fatal): the YAML saved, only the translation to settings.json failed.
        """
        if not APPLY_SCRIPT.is_file():
            return {"applied": False, "apply_error": "apply-comfort-posture.py not found"}
        try:
            proc = subprocess.run(
                [sys.executable, str(APPLY_SCRIPT), "--project-root", str(REPO_ROOT)],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (subprocess.SubprocessError, OSError) as e:
            return {"applied": False, "apply_error": f"could not run translator: {e}"}
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "non-zero exit").strip()
            return {"applied": False, "apply_error": err[:500]}
        # Trim the long session-mode footer; keep the "Applied ... bucket counts" head.
        summary = (proc.stdout or "").split("\nNote:")[0].strip()
        return {"applied": True, "apply_summary": summary[:1000]}

    def _handle_run(self):
        """POST /__run — run a FIXED, allow-listed `ravenclaude <action>` for the
        dashboard's one-click Install/Update buttons. No caller-supplied args or
        shell; the action name is validated against ALLOWED_ACTIONS, so this is not
        an arbitrary-command surface. Local-only server (see module docstring)."""
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 64 * 1024:
            self.send_error(413, "small JSON body required")
            return
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            action = body["action"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as e:
            self.send_error(400, f"invalid JSON body: {e}")
            return
        if action not in ALLOWED_ACTIONS:
            self.send_error(403, f"action not in allow-list: {action!r}")
            return
        if not RAVENCLAUDE_SCRIPT.is_file():
            self._json(500, {"ok": False, "action": action, "error": "ravenclaude script not found"})
            return
        # Fixed argv — no shell, no interpolation of caller input beyond the
        # validated action name. `install`/`status` target the repo root.
        argv = ["bash", str(RAVENCLAUDE_SCRIPT), action]
        if action in ("install", "status"):
            argv += ["--project", str(REPO_ROOT)]
        try:
            proc = subprocess.run(
                argv, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120
            )
        except (subprocess.SubprocessError, OSError) as e:
            self._json(500, {"ok": False, "action": action, "error": f"could not run: {e}"})
            return
        output = ((proc.stdout or "") + (proc.stderr or "")).strip()
        self._json(200, {"ok": proc.returncode == 0, "action": action,
                         "exit_code": proc.returncode, "output": output[:8000]})

    def _handle_classify(self):
        """POST /__classify {command} — run the real thing-decision classifier on
        the string (no execution) so the 'Test a command' simulator matches the
        engine. Returns the decision JSON (category/tier/seats/concerns/gate)."""
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 64 * 1024:
            self.send_error(413, "small JSON body required")
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
                [sys.executable, str(THING_DECISION), "--root", str(REPO_ROOT),
                 "preview", "--", command[:4000]],
                cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=15,
            )
            decision = json.loads(proc.stdout) if proc.stdout.strip() else {"category": None}
        except (subprocess.SubprocessError, OSError, json.JSONDecodeError) as e:
            self._json(500, {"error": f"classify failed: {e}"})
            return
        self._json(200, decision)

    def _json(self, code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _lan_ip() -> str | None:
    """Best-effort LAN IP for building a phone-reachable URL when bound to
    0.0.0.0. No packets are sent — connecting a UDP socket just selects the
    outbound route so we can read the local address. Returns None if it can't
    be determined (no route, offline, etc.)."""
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()


def _print_qr(url: str) -> bool:
    """Print a scannable QR code of `url` to the terminal so it can be opened
    on a phone. Returns False if the optional `qrcode` library isn't installed
    (the caller then prints an install hint). ASCII output only — no Pillow /
    image dependency."""
    try:
        import qrcode  # optional; pure-Python for the ASCII renderer
    except ImportError:
        return False
    qr = qrcode.QRCode(border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii(invert=True)
    return True


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--port", type=int, default=8000)
    p.add_argument(
        "--bind",
        default=None,
        help="bind address; auto 0.0.0.0 in a Codespace (so the forwarded port is reachable), else 127.0.0.1; pass 0.0.0.0 to accept from LAN. An explicit value always wins.",
    )
    p.add_argument(
        "--no-open",
        action="store_true",
        default=False,
        help="skip auto-opening the browser on start (auto-open is ON by default for local/desktop runs)",
    )
    args = p.parse_args()

    codespace = os.environ.get("CODESPACE_NAME")
    domain = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
    # In a Codespace the port-forwarder can't reach a 127.0.0.1-only socket, so default
    # to 0.0.0.0 there — kept safe by the Private forwarded port + the Origin/Host CSRF
    # guard below. Off-Codespace stay loopback-only. An explicit --bind always wins.
    bind = args.bind or ("0.0.0.0" if codespace else "127.0.0.1")

    os.chdir(REPO_ROOT)

    # Stable port: try the requested port and up to 5 successive ones to find a
    # free socket.  This avoids "address already in use" errors when the server
    # is relaunched quickly or another process holds the default port.
    server = None
    actual_port = args.port
    for candidate in range(args.port, args.port + 6):
        try:
            server = ThreadingHTTPServer((bind, candidate), DashboardHandler)
            actual_port = candidate
            break
        except OSError as exc:
            if exc.errno == errno.EADDRINUSE:
                continue
            raise
    if server is None:
        sys.exit(
            f"serve-dashboards: could not bind on ports {args.port}–{args.port + 5} "
            f"(all in use). Free one of those ports and retry."
        )

    # Build the Origin/Host allow-lists the CSRF/rebinding guard checks against.
    global _ALLOWED_HOSTS, _ALLOWED_ORIGINS
    _ALLOWED_HOSTS = {f"127.0.0.1:{actual_port}", f"localhost:{actual_port}", "127.0.0.1", "localhost"}
    _ALLOWED_ORIGINS = {f"http://127.0.0.1:{actual_port}", f"http://localhost:{actual_port}"}
    if codespace:
        _fwd = f"{codespace}-{actual_port}.{domain}"
        _ALLOWED_HOSTS.add(_fwd)
        _ALLOWED_ORIGINS.add(f"https://{_fwd}")
    if bind == "0.0.0.0":
        _ip = _lan_ip()
        if _ip:
            _ALLOWED_HOSTS.add(f"{_ip}:{actual_port}")
            _ALLOWED_ORIGINS.add(f"http://{_ip}:{actual_port}")

    dash_path = "/plugins/ravenclaude-core/dashboard.html"
    # Attach dash_path to the server so do_GET's root redirect can read it
    # without a global variable.
    server._dash_path = dash_path  # type: ignore[attr-defined]

    print(f"serve-dashboards: serving {REPO_ROOT} at http://127.0.0.1:{actual_port}/  (bound to {bind})")
    print(f"  POST /__save  - writes a whitelisted file under .ravenclaude/")
    print(f"  allow-list   - {sorted(ALLOWED_TARGETS)}")
    print(f"  POST /__run   - runs an allow-listed ravenclaude action (Install/Update buttons)")
    print(f"  actions      - {sorted(ALLOWED_ACTIONS)}")
    print(f"  GET  /__read  - reads an allow-listed config file so the dashboard hydrates from it")
    print(f"  read-list    - {sorted(ALLOWED_READ)}")
    print(f"  POST /__classify - runs the real command-review classifier on a string (Test-a-command simulator)")
    print(f"  GET  /__saga     - read-only list of Thing verdicts from .ravenclaude/runs/thing/ (?limit=N, default 200)")
    print(f"  GET  /__runs     - read-only list of multi-step runs from .ravenclaude/runs/<id>/ (?limit=N, default 200)")

    # Work out a phone-reachable URL (if any). localhost is NOT reachable from a
    # phone, so it gets no QR. The QR lets you open the live dashboard on a phone
    # — where "Save & apply" actually works, because it POSTs back to THIS server
    # (unlike the static README/Pages link, which 405s on the save POST).
    local_url = f"http://127.0.0.1:{actual_port}{dash_path}"
    phone_url = None
    security_note = None
    if codespace:
        phone_url = f"https://{codespace}-{actual_port}.{domain}{dash_path}"
        print("\n  Codespace forwarded URL (open THIS on your phone — not the README/Pages link):")
        print(f"  {phone_url}")
        security_note = (
            "  Security: keep this forwarded port PRIVATE (the default) and stay signed\n"
            "  into GitHub on the phone — /__save writes files and runs the translator."
        )
    elif bind == "0.0.0.0":
        lan_ip = _lan_ip()
        if lan_ip:
            phone_url = f"http://{lan_ip}:{actual_port}{dash_path}"
            print("\n  LAN URL (reachable from a phone on the SAME Wi-Fi):")
            print(f"  {phone_url}")
            security_note = (
                "  Security: bound to 0.0.0.0 — anyone on this network can reach /__save\n"
                "  (no auth). Use only on a trusted network."
            )

    if phone_url:
        print()
        if _print_qr(phone_url):
            print("  ^ scan with your phone camera to open the dashboard there.")
        else:
            print("  (For a scannable QR code here, run: pip install qrcode)")
        if security_note:
            print(security_note)

    # Auto-open the browser on local/desktop runs.  In a Codespace the container
    # has no display, and VS Code's onAutoForward: openBrowser (wired in
    # devcontainer.json) handles the open via the forwarded port — so we skip it
    # there.  The --no-open flag lets scripts/CI suppress this behaviour.
    if not args.no_open and not codespace:
        print(f"\n  Opening your browser at {local_url} …")
        try:
            webbrowser.open(local_url)
        except Exception:
            pass  # silently fall back to the printed URL

    print("\n  Ctrl+C to stop.")
    sys.stdout.flush()  # ensure the banner (incl. the QR) appears even when piped/redirected
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
