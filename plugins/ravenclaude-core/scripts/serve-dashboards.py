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
import functools
import json
import os
import subprocess
import sys
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
ALLOWED_TARGETS = {
    ".ravenclaude/comfort-posture.yaml",
    ".ravenclaude/environment-context.md",
} | JSON_EDIT_TARGETS
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


# Saving the comfort posture immediately re-runs the translator so the consumer's
# .claude/settings.json reflects the new YAML without a manual /set-posture.
POSTURE_TARGET = ".ravenclaude/comfort-posture.yaml"
APPLY_SCRIPT = PLUGIN_DIR / "scripts" / "apply-comfort-posture.py"

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
# irrelevant here, so CSRF/DNS-rebinding is the real threat. We reject any request
# whose Origin (always sent by browsers on cross-origin POST) isn't ours, or whose
# Host isn't a known local/forwarded host. The legit dashboard is same-origin → passes.
_ALLOWED_HOSTS: set[str] = set()
_ALLOWED_ORIGINS: set[str] = set()


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


class DashboardHandler(SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler (serving the plugin dir) + the dashboard endpoints."""

    def log_message(self, format, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), format % args))

    def _local_request_ok(self) -> bool:
        """Refuse cross-origin / DNS-rebinding requests to the write/read/classify
        endpoints. Checked on every state-changing or read request."""
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
        if (
            self.path == "/__save"
            or self.path == "/__classify"
            or self.path.startswith("/__read")
            or self.path.startswith("/__saga")
            or self.path.startswith("/__runs")
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

    def do_OPTIONS(self):
        if self.path in ("/__save", "/__classify"):
            self.send_response(204)
            self.send_header("Allow", "POST, HEAD, OPTIONS")
            self.end_headers()
            return
        self.send_error(405)

    def do_POST(self):
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
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
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            target = body["path"]
            content = body["content"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as e:
            self.send_error(400, f"invalid JSON body: {e}")
            return

        if target not in ALLOWED_TARGETS:
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

        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8", newline="\n")

        payload = {"saved": str(out.relative_to(PROJECT_ROOT)), "bytes": len(content)}
        if target == POSTURE_TARGET:
            payload.update(self._apply_posture())
        self._json(200, payload)

    def _handle_read(self):
        if not self._local_request_ok():
            self.send_error(403, "refused: cross-origin or non-local Origin/Host")
            return
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(self.path).query)
        target = (qs.get("path") or [""])[0]
        if target not in ALLOWED_READ:
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
        from urllib.parse import urlparse, parse_qs
        import glob as _glob
        import os as _os

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
        from urllib.parse import urlparse, parse_qs

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
            run_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
            for d in run_dirs[:limit]:
                records.append(_summarize_run(d))
        self._json(200, records)

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


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--port", type=int, default=8000)
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
    server = ThreadingHTTPServer((bind, args.port), handler)

    # Build the Origin/Host allow-lists the CSRF/rebinding guard checks against.
    global _ALLOWED_HOSTS, _ALLOWED_ORIGINS
    _ALLOWED_HOSTS = {f"127.0.0.1:{args.port}", f"localhost:{args.port}", "127.0.0.1", "localhost"}
    _ALLOWED_ORIGINS = {f"http://127.0.0.1:{args.port}", f"http://localhost:{args.port}"}
    if codespace:
        _fwd = f"{codespace}-{args.port}.{domain}"
        _ALLOWED_HOSTS.add(_fwd)
        _ALLOWED_ORIGINS.add(f"https://{_fwd}")

    print(f"serve-dashboards (plugin): serving {PLUGIN_DIR}")
    print(f"  project root (writes here): {PROJECT_ROOT}")
    print(f"  local URL: http://127.0.0.1:{args.port}{DASH_PATH}  (bound to {bind})")
    print(f"  POST /__save  - writes an allow-listed file under .ravenclaude/ + auto-applies")
    print(f"  GET  /__read  - hydrates the dashboard from your committed config")
    print(f"  GET  /__saga  - read-only Review-log feed from .ravenclaude/runs/thing/ (?limit=N, default 200)")
    print(f"  GET  /__runs  - read-only Activity feed from .ravenclaude/runs/<id>/ (?limit=N, default 200)")
    print(f"  POST /__classify - command-review 'Test a command' simulator (read-only)")

    phone_url = None
    if codespace:
        phone_url = f"https://{codespace}-{args.port}.{domain}{DASH_PATH}"
        print("\n  Codespace forwarded URL — open it via the Ports panel -> Open in Browser")
        print("  (that handles the GitHub auth; a raw paste needs you already signed in):")
        print(f"  {phone_url}")
        print("  Security: keep this forwarded port PRIVATE — /__save writes files + applies the posture.")
    if phone_url:
        print()
        if _print_qr(phone_url):
            print("  ^ scan with your phone camera to open the dashboard there.")
        else:
            print("  (For a scannable QR code here, run: pip install qrcode)")

    print("\n  Ctrl+C to stop.")
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
