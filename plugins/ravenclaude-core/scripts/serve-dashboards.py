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

ALLOWED_TARGETS = {
    ".ravenclaude/comfort-posture.yaml",
    ".ravenclaude/environment-context.md",
}
ALLOWED_READ = {
    ".ravenclaude/comfort-posture.yaml",
    ".ravenclaude/environment-context.md",
}

# Saving the comfort posture immediately re-runs the translator so the consumer's
# .claude/settings.json reflects the new YAML without a manual /set-posture.
POSTURE_TARGET = ".ravenclaude/comfort-posture.yaml"
APPLY_SCRIPT = PLUGIN_DIR / "scripts" / "apply-comfort-posture.py"

# POST /__classify powers the dashboard's "Test a command" simulator: it runs the
# REAL deterministic classifier on the typed string (no execution) so the preview
# can't drift from the engine.
THING_DECISION = PLUGIN_DIR / "scripts" / "thing-decision.py"

DASH_PATH = "/dashboard.html"

# Populated in main(). The state-changing/read endpoints check these so a malicious
# web page the user is viewing can't drive this server cross-origin: a 127.0.0.1
# bind does NOT stop a browser from POSTing to localhost, and a same-site cookie is
# irrelevant here, so CSRF/DNS-rebinding is the real threat. We reject any request
# whose Origin (always sent by browsers on cross-origin POST) isn't ours, or whose
# Host isn't a known local/forwarded host. The legit dashboard is same-origin → passes.
_ALLOWED_HOSTS: set[str] = set()
_ALLOWED_ORIGINS: set[str] = set()


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
        if self.path == "/__save" or self.path == "/__classify" or self.path.startswith("/__read"):
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
        self._json(200, payload)

    def _apply_posture(self) -> dict:
        """Re-run apply-comfort-posture.py against the CONSUMER's project after a save."""
        if not APPLY_SCRIPT.is_file():
            return {"applied": False, "apply_error": "apply-comfort-posture.py not found"}
        try:
            proc = subprocess.run(
                [sys.executable, str(APPLY_SCRIPT), "--project-root", str(PROJECT_ROOT)],
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
