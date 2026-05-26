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
import json
import os
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

ALLOWED_TARGETS = {
    ".ravenclaude/comfort-posture.yaml",
    ".ravenclaude/environment-context.md",
}

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
}

# POST /__classify powers the dashboard's "Test a command" simulator: it runs the
# REAL deterministic classifier (thing-decision.py) on the typed string so the
# preview can't drift from the engine. It does NOT execute the command — the
# string is analysed only (passed as a single argv to a read-only classifier).
THING_DECISION = (
    REPO_ROOT / "plugins" / "ravenclaude-core" / "scripts" / "thing-decision.py"
)

# Populated in main(). The write/read/run/classify endpoints check these so a
# malicious web page the user is viewing can't drive this server cross-origin: a
# 127.0.0.1 bind does NOT stop a browser from POSTing to localhost (CSRF), and a
# forged Host enables DNS-rebinding. We reject any request whose Origin (always
# sent by browsers on cross-origin POST) isn't ours, or whose Host isn't known.
_ALLOWED_HOSTS: set[str] = set()
_ALLOWED_ORIGINS: set[str] = set()


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
        if self.path in ("/__save", "/__run", "/__classify") or self.path.startswith("/__read"):
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
        if self.path.startswith("/__read"):
            self._handle_read()
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
        self._json(200, payload)

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
    p.add_argument("--bind", default="127.0.0.1", help="default 127.0.0.1; use 0.0.0.0 to accept from LAN")
    args = p.parse_args()

    os.chdir(REPO_ROOT)
    server = ThreadingHTTPServer((args.bind, args.port), DashboardHandler)

    codespace = os.environ.get("CODESPACE_NAME")
    domain = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")

    # Build the Origin/Host allow-lists the CSRF/rebinding guard checks against.
    global _ALLOWED_HOSTS, _ALLOWED_ORIGINS
    _ALLOWED_HOSTS = {f"127.0.0.1:{args.port}", f"localhost:{args.port}", "127.0.0.1", "localhost"}
    _ALLOWED_ORIGINS = {f"http://127.0.0.1:{args.port}", f"http://localhost:{args.port}"}
    if codespace:
        _fwd = f"{codespace}-{args.port}.{domain}"
        _ALLOWED_HOSTS.add(_fwd)
        _ALLOWED_ORIGINS.add(f"https://{_fwd}")
    if args.bind == "0.0.0.0":
        _ip = _lan_ip()
        if _ip:
            _ALLOWED_HOSTS.add(f"{_ip}:{args.port}")
            _ALLOWED_ORIGINS.add(f"http://{_ip}:{args.port}")

    dash_path = "/plugins/ravenclaude-core/dashboard.html"
    print(f"serve-dashboards: serving {REPO_ROOT} at http://{args.bind}:{args.port}/")
    print(f"  POST /__save  - writes a whitelisted file under .ravenclaude/")
    print(f"  allow-list   - {sorted(ALLOWED_TARGETS)}")
    print(f"  POST /__run   - runs an allow-listed ravenclaude action (Install/Update buttons)")
    print(f"  actions      - {sorted(ALLOWED_ACTIONS)}")
    print(f"  GET  /__read  - reads an allow-listed config file so the dashboard hydrates from it")
    print(f"  read-list    - {sorted(ALLOWED_READ)}")
    print(f"  POST /__classify - runs the real command-review classifier on a string (Test-a-command simulator)")

    # Work out a phone-reachable URL (if any). localhost is NOT reachable from a
    # phone, so it gets no QR. The QR lets you open the live dashboard on a phone
    # — where "Save & apply" actually works, because it POSTs back to THIS server
    # (unlike the static README/Pages link, which 405s on the save POST).
    phone_url = None
    security_note = None
    if codespace:
        phone_url = f"https://{codespace}-{args.port}.{domain}{dash_path}"
        print("\n  Codespace forwarded URL (open THIS on your phone — not the README/Pages link):")
        print(f"  {phone_url}")
        security_note = (
            "  Security: keep this forwarded port PRIVATE (the default) and stay signed\n"
            "  into GitHub on the phone — /__save writes files and runs the translator."
        )
    elif args.bind == "0.0.0.0":
        lan_ip = _lan_ip()
        if lan_ip:
            phone_url = f"http://{lan_ip}:{args.port}{dash_path}"
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

    print("\n  Ctrl+C to stop.")
    sys.stdout.flush()  # ensure the banner (incl. the QR) appears even when piped/redirected
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
