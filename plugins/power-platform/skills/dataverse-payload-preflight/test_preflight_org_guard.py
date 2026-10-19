#!/usr/bin/env python3
"""Regression test: preflight.py never sends DATAVERSE_TOKEN to a non-Dataverse --org.

repo-review 2026-10-19 (domainplugins-12): fetch_metadata attached the bearer token to
whatever --org it was given (plain http included) and urllib followed redirects with it.
Stdlib only. Run:  python3 test_preflight_org_guard.py   (exit 0 = all pass)

A loopback sink records every request it receives; the CLI is pointed at it over http and
must exit 2 having sent nothing. A token value is synthetic and built at runtime.
"""

from __future__ import annotations

import http.server
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PREFLIGHT = os.path.join(HERE, "preflight.py")
results: list[tuple[str, bool]] = []


def check(name: str, ok: bool) -> None:
    results.append((name, bool(ok)))
    print(("  PASS " if ok else "  FAIL ") + name)


def load_module():
    spec = importlib.util.spec_from_file_location("preflight_under_test", PREFLIGHT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _Sink(http.server.BaseHTTPRequestHandler):
    hits: list[str] = []

    def do_GET(self):  # noqa: N802
        _Sink.hits.append(self.headers.get("Authorization", ""))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *_args):
        pass


def run_cli(org: str, token: str, workdir: str) -> subprocess.CompletedProcess:
    payload = os.path.join(workdir, "payload.json")
    with open(payload, "w", encoding="utf-8") as fh:
        json.dump({"name": "x"}, fh)
    env = dict(os.environ, DATAVERSE_TOKEN=token)
    return subprocess.run(
        [sys.executable, PREFLIGHT, "--entity", "account", "--payload", payload, "--org", org],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )


def main() -> int:
    token = "eyJ" + "synthetic" + "-test-token"
    server = http.server.HTTPServer(("127.0.0.1", 0), _Sink)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with tempfile.TemporaryDirectory() as d:
            print("preflight --org guard — refused before any request")
            r = run_cli(f"http://127.0.0.1:{port}", token, d)
            check("http:// loopback org exits 2", r.returncode == 2)
            check("the sink received no request (token never sent)", _Sink.hits == [])
            r = run_cli("https://attacker.example", token, d)
            check("non-Dataverse https host exits 2", r.returncode == 2)
            check("the refusal is explained on stderr", "refusing --org" in r.stderr)
    finally:
        server.shutdown()

    print("validate_env_url — commercial + sovereign hosts allowed, the rest refused")
    mod = load_module()
    for url in (
        "https://org.crm.dynamics.com",
        "https://org.crm4.dynamics.com/",
        "https://org.api.crm.dynamics.com",
        "https://org.crm.microsoftdynamics.us",
        "https://org.crm.appsplatform.us",
        "https://org.crm.dynamics.cn",
    ):
        try:
            mod.validate_env_url(url)
            check(f"allows {url}", True)
        except ValueError:
            check(f"allows {url}", False)
    for url in (
        "http://org.crm.dynamics.com",
        "https://u:p@org.crm.dynamics.com",
        "https://org.crm.dynamics.com:8443",
        "https://org.crm.dynamics.com.evil.example",
        "https://attacker.example",
    ):
        try:
            mod.validate_env_url(url)
            check(f"refuses {url}", False)
        except ValueError:
            check(f"refuses {url}", True)

    print("redirect guard — a cross-host 3xx is refused")
    opener = mod._build_opener()
    guard = next(h for h in opener.handlers if isinstance(h, urllib.request.HTTPRedirectHandler))
    req = urllib.request.Request("https://org.crm.dynamics.com/api/data/v9.2/x")
    try:
        guard.redirect_request(req, None, 302, "Found", {}, "https://attacker.example/steal")
        check("cross-host redirect raises", False)
    except urllib.error.HTTPError:
        check("cross-host redirect raises", True)
    same = guard.redirect_request(
        req, None, 302, "Found", {}, "https://org.crm.dynamics.com/api/data/v9.2/y"
    )
    check("same-host redirect is followed", same is not None)

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} checks passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
