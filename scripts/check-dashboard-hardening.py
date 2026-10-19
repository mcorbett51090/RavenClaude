#!/usr/bin/env python3
"""check-dashboard-hardening.py — regression suite for the dashboard servers and launchers.

Covers the WS-D hardening of the two `serve-dashboards.py` copies (root dev server and
the bundled plugin server), `bin/rc`, and the Gate 32 parity checker. Every live row
starts a REAL server on a free 127.0.0.1 port against a scratch `--project-root`, so each
expectation is checked over HTTP rather than read off the source.

Sections (all run by default; `--only` picks one):

  static   Gate 32 must flag allow-list drift and body drift in the newly named helpers.
  unit     In-process: secret-scrub rows, the /__host closed set, the ASCII slug check.
  plugin   Live bundled server. Expectations: a decoy engine planted under
           --project-root is not executed; one bad byte in a run artifact does not
           drop the /__runs feed; environment-context.md is neither readable nor
           writable; a YAML alias bomb is refused; an in-root symlink is refused; a
           normal save goes through a temp file; a malformed posture is refused before
           anything is written; wrong-typed fields and a non-ASCII CSRF header get an
           HTTP error instead of a connection reset; /__host reports a closed set; a
           non-ASCII plugin slug is refused; HEAD on a /__* path is Host-guarded;
           /__csrf carries a hashed project id.
  root     Live root server. Expectations: dot paths and directory listings are refused,
           /index.html is still served, HEAD on a /__* path is Host-guarded, /__csrf
           carries a hashed project id, /__run refuses a non-string action.
  rc       bin/rc: a two-level relative symlink chain finds the plugin dir, and
           `rc spectate` does not attach to a live server that reports another
           project's id.

Every refusal row sits beside a positive control on the same subject (a same-origin
HEAD, a plain YAML read, a normal save), so a server that refuses everything cannot
pass.

Teeth: point the suite at pre-fix files and the rows go red, e.g.

  git show HEAD:plugins/ravenclaude-core/scripts/serve-dashboards.py > /tmp/old-plugin.py
  python3 scripts/check-dashboard-hardening.py --plugin-server /tmp/old-plugin.py --only plugin

`--must-fail` is the self-contained version: it re-runs targeted rows against mutants of
the CURRENT files (each mutant reverts one fix) and fails unless every mutant is caught.

Exit: 0 every row passed; 1 a row failed; 2 could not run (missing curl, no free port
window, a server that would not start). Stdlib only, py3.9-compatible.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import importlib.util
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGIN = REPO / "plugins" / "ravenclaude-core"
ROOT_SERVER = REPO / "scripts" / "serve-dashboards.py"
PLUGIN_SERVER = PLUGIN / "scripts" / "serve-dashboards.py"
PARITY = REPO / "scripts" / "check-dashboard-server-parity.py"
RC = PLUGIN / "bin" / "rc"


def _configure(repo: Path) -> None:
    global REPO, PLUGIN, ROOT_SERVER, PLUGIN_SERVER, PARITY, RC
    REPO = repo.resolve()
    PLUGIN = REPO / "plugins" / "ravenclaude-core"
    ROOT_SERVER = REPO / "scripts" / "serve-dashboards.py"
    PLUGIN_SERVER = PLUGIN / "scripts" / "serve-dashboards.py"
    PARITY = REPO / "scripts" / "check-dashboard-server-parity.py"
    RC = PLUGIN / "bin" / "rc"


RESULTS: list[tuple[str, str, bool, str]] = []


def check(section: str, name: str, ok: bool, detail: str = "") -> bool:
    RESULTS.append((section, name, bool(ok), detail))
    mark = "ok  " if ok else "FAIL"
    line = f"  [{mark}] {section}: {name}"
    if detail and not ok:
        line += f"  -- {detail}"
    print(line)
    return bool(ok)


class CannotRun(Exception):
    """The suite could not run (not a finding)."""


# ── helpers ──────────────────────────────────────────────────────────────────


def _port_free(port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def free_window(width: int = 1, start: int = 21000, stop: int = 60000) -> int:
    """First port p such that p..p+width-1 are all bindable on 127.0.0.1."""
    p = start + (os.getpid() % 997) * 13
    while p + width < stop:
        if all(_port_free(p + i) for i in range(width)):
            return p
        p += width + 1
    raise CannotRun(f"no free {width}-port window below {stop}")


def project_id(root: Path) -> str:
    return hashlib.sha256(str(Path(root).resolve()).encode("utf-8")).hexdigest()[:12]


def build_shim_plugin(dest: Path, overrides: dict[str, Path]) -> Path:
    """A plugin tree whose entries are symlinks into the real plugin, except the
    one-level-deep `overrides` (e.g. "scripts/serve-dashboards.py"), which are COPIED,
    so PLUGIN_DIR (= the copy's parent.parent) is the shim and every sibling script
    still resolves."""
    dest.mkdir(parents=True)
    override_dirs = {Path(r).parts[0] for r in overrides}
    for entry in sorted(PLUGIN.iterdir()):
        if entry.name in override_dirs:
            sub = dest / entry.name
            sub.mkdir()
            for child in sorted(entry.iterdir()):
                rel = f"{entry.name}/{child.name}"
                if rel in overrides:
                    shutil.copy2(str(overrides[rel]), str(sub / child.name))
                else:
                    (sub / child.name).symlink_to(child)
        else:
            (dest / entry.name).symlink_to(entry)
    return dest


class Resp:
    def __init__(self, status: int, headers: dict, body: bytes, error: str = ""):
        self.status = status
        self.headers = headers
        self.body = body
        self.error = error

    def json(self):
        try:
            return json.loads(self.body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None


def req(
    port: int,
    method: str,
    path: str,
    headers: dict | None = None,
    body: bytes | None = None,
    host: str | None = None,
    timeout: float = 15.0,
) -> Resp:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    try:
        conn.putrequest(method, path, skip_host=True, skip_accept_encoding=True)
        conn.putheader("Host", host if host is not None else f"127.0.0.1:{port}")
        for k, v in (headers or {}).items():
            conn.putheader(k, v)
        if body is not None:
            conn.putheader("Content-Length", str(len(body)))
        conn.endheaders(body)
        r = conn.getresponse()
        data = r.read() if method != "HEAD" else b""
        return Resp(r.status, dict(r.getheaders()), data)
    except Exception as e:  # noqa: BLE001 — a dropped connection IS the finding
        return Resp(-1, {}, b"", type(e).__name__)
    finally:
        conn.close()


class Server:
    """A live serve-dashboards.py child process."""

    def __init__(self, argv: list[str], env: dict, log: Path, port: int):
        self.port = port
        self.log = log
        self._fh = open(log, "wb")  # closed in stop()
        self.proc = subprocess.Popen(
            argv,
            env=env,
            stdout=self._fh,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        deadline = time.time() + 20
        last = None
        while time.time() < deadline:
            if self.proc.poll() is not None:
                break
            last = req(port, "GET", "/__csrf", timeout=2)
            if last.status == 200:
                return
            time.sleep(0.2)
        exited = self.proc.poll()
        tail = log.read_text(encoding="utf-8", errors="replace")[-1500:]
        self.stop()
        probe = (
            "never probed" if last is None else f"last /__csrf: {last.status} {last.error}".strip()
        )
        state = f"exited {exited}" if exited is not None else "still running after 20s"
        raise CannotRun(f"server did not come up on {port} ({state}; {probe}): {tail}")

    def token(self) -> str:
        data = req(self.port, "GET", "/__csrf").json() or {}
        return str(data.get("token", ""))

    def post(self, path: str, payload, token: str | None = None):
        tok = self.token() if token is None else token
        h = {
            "Content-Type": "application/json",
            "Origin": f"http://127.0.0.1:{self.port}",
            "X-CSRF-Token": tok,
        }
        return req(self.port, "POST", path, headers=h, body=json.dumps(payload).encode("utf-8"))

    def stop(self) -> None:
        try:
            os.killpg(self.proc.pid, signal.SIGTERM)
        except OSError:
            pass
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(self.proc.pid, signal.SIGKILL)
            except OSError:
                pass
        self._fh.close()


def base_env(scratch: Path) -> dict:
    home = scratch / "home"
    (home / ".claude").mkdir(parents=True, exist_ok=True)
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(home),
        "RAVENCLAUDE_USAGE_DIR": str(scratch / "usage"),
        "LANG": "C.UTF-8",
        "PYTHONDONTWRITEBYTECODE": "1",
        # Unbuffered, so a server that never comes up leaves its real output in
        # the log (a buffered startup line made the macOS log read as empty).
        "PYTHONUNBUFFERED": "1",
    }


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def _tok(prefix: str, n: int, ch: str = "A") -> str:
    """Synthetic token, assembled at runtime so no literal secret shape is on disk."""
    return prefix + (ch * n)


# ── section: static (Gate 32 parity checker) ─────────────────────────────────


def section_static(parity: Path, scratch: Path) -> None:
    sec = "static"
    real = PLUGIN_SERVER.read_text(encoding="utf-8")
    counter = [0]

    def run(plugin_text: str | None) -> int:
        # Both server paths are passed explicitly, so a checker copied elsewhere
        # (the teeth run) still reads THIS tree's servers.
        plugin_path = PLUGIN_SERVER
        if plugin_text is not None:
            counter[0] += 1
            plugin_path = scratch / f"parity-mutant-{counter[0]}.py"
            plugin_path.write_text(plugin_text, encoding="utf-8")
        argv = [
            sys.executable,
            str(parity),
            "--root-server",
            str(ROOT_SERVER),
            "--plugin-server",
            str(plugin_path),
        ]
        return subprocess.run(argv, capture_output=True, text=True).returncode

    check(sec, "Gate 32 passes on the real tree (positive control)", run(None) == 0)

    anchor = "    WEB_ACCESS_TARGET,\n} | JSON_EDIT_TARGETS\nALLOWED_READ = {"
    if anchor in real:
        drift = real.replace(
            anchor,
            '    ".ravenclaude/environment-context.md",\n' + anchor,
            1,
        )
        check(
            sec, "ALLOWED_TARGETS drift (environment-context re-added) is flagged", run(drift) == 1
        )
    else:
        check(sec, "ALLOWED_TARGETS anchor present in plugin server", False, "anchor moved")

    read_anchor = '    ".ravenclaude/plugin-lifecycle.json",'
    if read_anchor in real:
        drift = real.replace(read_anchor, read_anchor + '\n    ".ravenclaude/secret-notes.md",', 1)
        check(sec, "ALLOWED_READ drift (extra read path) is flagged", run(drift) == 1)
    else:
        check(sec, "ALLOWED_READ anchor present in plugin server", False, "anchor moved")

    for fn in ("_reserve_engine", "_write_reserve_override", "_is_plugin_config_target"):
        sig = f"def {fn}("
        if sig in real:
            drift = real.replace(sig, f"def {fn}(  # ASYMMETRIC EDIT\n    ", 1)
            check(sec, f"body drift in {fn} is flagged", run(drift) == 1)
        else:
            check(sec, f"{fn} present in plugin server", False)

    # do_GET is now a catch-all wrapper around _dispatch_get. A checker that scans
    # only the wrapper sees zero routes and passes vacuously; this mutant drops the
    # guard from one GET handler, so it must be flagged.
    head = real.find("    def _handle_heimdall(self):")
    guard = "if not self._local_request_ok():"
    at = real.find(guard, head) if head >= 0 else -1
    if at >= 0:
        drift = real[:at] + "if False:" + real[at + len(guard) :]
        check(sec, "an unguarded GET handler behind the do_GET wrapper is flagged", run(drift) == 1)
    else:
        check(sec, "_handle_heimdall guard present in plugin server", False, "anchor moved")


# ── section: unit (in-process) ───────────────────────────────────────────────


def section_unit(root_server: Path, plugin_server: Path, scratch: Path) -> None:
    sec = "unit"
    # Import each copy from a layout it can resolve its siblings in (a copy outside a
    # plugin tree cannot find spectate_store.py and friends).
    repo = scratch / "rootrepo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy2(str(root_server), str(repo / "scripts" / "serve-dashboards.py"))
    (repo / "plugins").symlink_to(REPO / "plugins")
    shim = build_shim_plugin(
        scratch / "mkt" / "plugins" / "ravenclaude-core",
        {"scripts/serve-dashboards.py": plugin_server},
    )
    mods = {}
    for label, path in (
        ("root", repo / "scripts" / "serve-dashboards.py"),
        ("plugin", shim / "scripts" / "serve-dashboards.py"),
    ):
        try:
            mods[label] = load_module(path, f"_wsd_{label}_srv")
        except Exception as e:  # noqa: BLE001
            check(sec, f"{label} server imports", False, f"{type(e).__name__}: {e}")
    redacted = "[REDACTED]"
    pem_head = "-----BEGIN " + "RSA PRIVATE KEY-----"
    pem_tail = "-----END " + "RSA PRIVATE KEY-----"
    pem_body = "MIIEowIBAAKCAQEAexamplebody\nmore+base64/body=="
    for label, mod in mods.items():
        scrub = getattr(mod, "_mimir_scrub_string", None)
        if scrub is None:
            check(sec, f"{label}: _mimir_scrub_string exists", False)
            continue
        kebab = "implement ta" + "sk-management-and-planning-module now"
        check(
            sec,
            f"{label}: kebab text after 'sk-' is left alone",
            scrub(kebab) == kebab,
            scrub(kebab),
        )
        key = "key " + _tok("sk-", 24, "b")
        check(sec, f"{label}: a synthetic sk- key is redacted", redacted in scrub(key))
        for cls in ("p", "o", "u", "s", "r"):
            t = "tok " + _tok("gh" + cls + "_", 36)
            check(sec, f"{label}: gh{cls}_ token redacted", redacted in scrub(t), scrub(t))
        rows = {
            "AWS ASIA temp key": "id " + _tok("AS" + "IA", 16, "Q"),
            "sk_test_ key": "k " + _tok("sk_" + "test_", 24, "z"),
            "Google ya29 token": "t " + _tok("ya" + "29.", 30, "c"),
            "Slack xapp- token": "t " + _tok("xa" + "pp-", 20, "1"),
            "Bearer value": "Authorization: Bearer " + ("d" * 32),
            "-u user:pass": "curl -u admin:" + "Sup3rSecretPw https://x",
            "literal PASSWORD= assignment": "PGPASS" + "WORD=hunter2hunter2",
        }
        for name, s in rows.items():
            out = scrub(s)
            check(sec, f"{label}: {name} redacted", redacted in out, out)
        envref = "PGPASS" + "WORD=$PGPASS_FROM_VAULT"
        check(
            sec,
            f"{label}: env reference PASSWORD=$VAR left alone",
            scrub(envref) == envref,
            scrub(envref),
        )
        pem = f"before\n{pem_head}\n{pem_body}\n{pem_tail}\nafter"
        out = scrub(pem)
        check(
            sec,
            f"{label}: PEM block body + END line redacted",
            "MIIEow" not in out and pem_tail not in out and "before" in out and "after" in out,
            out,
        )
        unterminated = f"x {pem_head}\n{pem_body}"
        out = scrub(unterminated)
        check(sec, f"{label}: unterminated PEM redacted to end of input", "MIIEow" not in out, out)

        read_host = getattr(mod, "_read_host", None)
        saved = os.environ.get("THING_HOST")
        try:
            os.environ["THING_HOST"] = "<img src=x onerror=alert(1)>"
            h = read_host()["host"] if read_host else None
            check(sec, f"{label}: arbitrary THING_HOST reported as 'other'", h == "other", repr(h))
            os.environ["THING_HOST"] = "codex"
            h = read_host()["host"] if read_host else None
            check(
                sec,
                f"{label}: a known THING_HOST passes through (positive control)",
                h == "codex",
                repr(h),
            )
        finally:
            if saved is None:
                os.environ.pop("THING_HOST", None)
            else:
                os.environ["THING_HOST"] = saved

        is_cfg = mod._is_plugin_config_target
        check(
            sec,
            f"{label}: ASCII slug accepted (positive control)",
            is_cfg(".ravenclaude/plugins/good-1.yaml") is True,
        )
        for bad in (".ravenclaude/plugins/é.yaml", ".ravenclaude/plugins/².yaml"):
            check(sec, f"{label}: non-ASCII slug {bad!r} refused", is_cfg(bad) is False)
        try:
            ok = is_cfg(["x"]) is False
            detail = ""
        except Exception as e:  # noqa: BLE001
            ok, detail = False, type(e).__name__
        check(sec, f"{label}: non-string target refused without raising", ok, detail)


# ── section: plugin (live bundled server) ────────────────────────────────────

_ALIAS_BOMB = "a0: &a0 [x, x, x, x, x, x, x, x, x]\n" + "".join(
    f"a{i}: &a{i} [{', '.join([f'*a{i - 1}'] * 9)}]\n" for i in range(1, 7)
)


def _decoys(proj: Path, markers: Path) -> None:
    base = proj / "plugins" / "ravenclaude-core"
    (base / "scripts").mkdir(parents=True)
    (base / "hooks").mkdir(parents=True)
    m = str(markers)
    (base / "scripts" / "thing-concern-stats.py").write_text(
        "import pathlib\n"
        f"pathlib.Path({m!r}, 'PWNED-concern-stats').write_text('ran')\n"
        "def compute(root):\n"
        "    return {'schema_version': 1, 'total_reviews': 0, 'concerns': [], 'decoy': True}\n",
        encoding="utf-8",
    )
    (base / "scripts" / "routine-reserve.py").write_text(
        "import pathlib\n"
        f"pathlib.Path({m!r}, 'PWNED-reserve').write_text('ran')\n"
        "def load_config(root):\n    return {}\n"
        "def compute_and_save(now, cfg, save=True):\n    return {'decoy': True}\n",
        encoding="utf-8",
    )
    hook = base / "hooks" / "worktree-guard.sh"
    hook.write_text(
        f"#!/usr/bin/env bash\ntouch {m}/PWNED-worktree-guard\necho '{{}}'\n", encoding="utf-8"
    )
    hook.chmod(0o755)


def section_plugin(plugin_server: Path, scratch: Path) -> None:
    sec = "plugin"
    shim = build_shim_plugin(
        scratch / "mkt" / "plugins" / "ravenclaude-core",
        {"scripts/serve-dashboards.py": plugin_server},
    )
    proj = scratch / "proj"
    rc_dir = proj / ".ravenclaude"
    (rc_dir / "plugins").mkdir(parents=True)
    markers = scratch / "markers"
    markers.mkdir()
    _decoys(proj, markers)
    (rc_dir / "comfort-posture.yaml").write_text(
        "schema_version: 5\ncategories: {}\n", encoding="utf-8"
    )
    (rc_dir / "environment-context.md").write_text("# Environment Context\n", encoding="utf-8")
    runx = rc_dir / "runs" / "runX"
    runx.mkdir(parents=True)
    (runx / "summary.md").write_bytes(b"truncated mid-codepoint \xe2\x82")
    (runx / "events.jsonl").write_bytes(b'{"a": 1}\n\xff\n')
    sess = rc_dir / "runs" / "sessA"
    sess.mkdir(parents=True)
    (sess / "hook-events.jsonl").write_bytes(
        b'{"ts": "2099-01-01T00:00:00Z", "hook": "x.sh", "verdict": "deny", "rule": "caf\xe9"}\n'
    )
    (rc_dir / "plugins" / "bomb.yaml").write_text(_ALIAS_BOMB, encoding="utf-8")
    (rc_dir / "plugins" / "plain.yaml").write_text("k: v\n", encoding="utf-8")
    victim = proj / "victim.txt"
    victim.write_text("original\n", encoding="utf-8")
    (rc_dir / "plugins" / "pwn.yaml").symlink_to(Path("..") / ".." / "victim.txt")

    port = free_window(1)
    env = base_env(scratch)
    env["THING_HOST"] = "<img src=x onerror=alert(1)>"
    argv = [
        sys.executable,
        str(shim / "scripts" / "serve-dashboards.py"),
        "--project-root",
        str(proj),
        "--port",
        str(port),
        "--bind",
        "127.0.0.1",
        "--no-open",
        "--max-idle",
        "0",
        "--no-reclaim",
    ]
    srv = Server(argv, env, scratch / "plugin-server.log", port)
    try:
        _plugin_rows(sec, srv, proj, markers, victim)
    finally:
        srv.stop()


def _plugin_rows(sec: str, srv: Server, proj: Path, markers: Path, victim: Path) -> None:
    port = srv.port
    rc_dir = proj / ".ravenclaude"

    # dashboard-1: a decoy engine under --project-root must not be executed.
    for ep in ("/__concern-stats", "/__reserve", "/__sleipnir"):
        r = req(port, "GET", ep)
        check(
            sec,
            f"GET {ep} answers OK (positive control)",
            r.status == 200,
            f"status {r.status} {r.error}",
        )
        check(sec, f"GET {ep} carries no decoy payload", b'"decoy"' not in r.body)
    planted = sorted(p.name for p in markers.iterdir())
    check(
        sec,
        "no decoy engine/hook from the project tree was executed",
        not planted,
        ", ".join(planted),
    )

    # dashboard-4: one bad byte must not drop the feed.
    for ep in ("/__runs", "/__heimdall", "/__vidarr"):
        r = req(port, "GET", ep)
        check(
            sec,
            f"GET {ep} with a non-UTF-8 byte answers OK",
            r.status == 200,
            f"{r.status} {r.error}",
        )
    # A type error no reader anticipates must come back as JSON, not a reset.
    with (rc_dir / "runs" / "sessA" / "hook-events.jsonl").open("ab") as fh:
        fh.write(b'{"ts": 5, "hook": "y.sh", "verdict": "deny"}\n')
    r = req(port, "GET", "/__heimdall")
    body = r.json() or {}
    check(
        sec,
        "an unexpected GET handler exception is a JSON server error, not a dropped connection",
        r.status == 500 and isinstance(body, dict) and "error" in body,
        f"{r.status} {r.error} {r.body[:120]!r}",
    )

    # dashboard-5: environment-context.md must be unreachable through the server.
    # control: the pre-fix plugin server answered 200 to both requests below.
    r = req(port, "GET", "/__read?path=.ravenclaude/environment-context.md")
    check(sec, "GET /__read of environment-context.md is refused", r.status == 403, f"{r.status}")
    r = srv.post("/__save", {"path": ".ravenclaude/environment-context.md", "content": "x"})
    check(sec, "POST /__save of environment-context.md is refused", r.status == 403, f"{r.status}")

    # dashboard-7: alias bomb refused quickly; plain YAML still parses.
    t0 = time.time()
    r = req(port, "GET", "/__read?path=.ravenclaude/plugins/bomb.yaml")
    dt = time.time() - t0
    check(
        sec,
        "GET /__read of a YAML alias bomb is a small, fast client error",
        400 <= r.status < 500 and len(r.body) < 4096 and dt < 5,
        f"{r.status} {len(r.body)}B {dt:.2f}s",
    )
    r = req(port, "GET", "/__read?path=.ravenclaude/plugins/plain.yaml")
    check(
        sec,
        "GET /__read of plain YAML parses (positive control)",
        r.status == 200 and (r.json() or {}).get("parsed") == {"k": "v"},
        f"{r.status}",
    )
    r = srv.post("/__save", {"path": ".ravenclaude/plugins/bomb2.yaml", "content": _ALIAS_BOMB})
    check(sec, "POST /__save of a YAML alias bomb is refused", r.status == 400, f"{r.status}")

    # dashboard-2 / dashboard-8: in-root symlink refused; a normal save is atomic.
    r = srv.post("/__save", {"path": ".ravenclaude/plugins/pwn.yaml", "content": "owned: true\n"})
    check(sec, "POST /__save through an in-root symlink is refused", r.status == 403, f"{r.status}")
    check(
        sec,
        "the symlink target keeps its bytes",
        victim.read_text(encoding="utf-8") == "original\n",
    )
    r = req(port, "GET", "/__read?path=.ravenclaude/plugins/pwn.yaml")
    check(sec, "GET /__read through an in-root symlink is refused", r.status == 403, f"{r.status}")
    plain = rc_dir / "plugins" / "plain.yaml"
    ino_before = plain.stat().st_ino
    r = srv.post("/__save", {"path": ".ravenclaude/plugins/plain.yaml", "content": "k: w\n"})
    check(
        sec,
        "POST /__save of a plain plugin config succeeds (positive control)",
        r.status == 200,
        f"{r.status}",
    )
    check(sec, "the saved bytes landed", plain.read_text(encoding="utf-8") == "k: w\n")
    check(
        sec,
        "the save replaced the file (temp file + os.replace: new inode)",
        plain.stat().st_ino != ino_before,
    )
    leftovers = [p.name for p in (rc_dir / "plugins").iterdir() if p.name.endswith(".tmp")]
    check(sec, "no temp file left behind", not leftovers, ", ".join(leftovers))

    # dashboard-6: malformed posture refused before writing; a backup is kept.
    posture = rc_dir / "comfort-posture.yaml"
    good = "schema_version: 5\ncategories: {}\n"
    for name, content in (
        ("unparseable YAML", "::: [ {{{ not yaml"),
        ("empty content", ""),
        ("a mapping without schema_version", "categories: {}\n"),
        ("a YAML list", "- a\n- b\n"),
    ):
        r = srv.post("/__save", {"path": ".ravenclaude/comfort-posture.yaml", "content": content})
        check(
            sec,
            f"posture save of {name} is refused as unprocessable",
            r.status == 422,
            f"{r.status}",
        )
        check(
            sec, f"posture file unchanged after {name}", posture.read_text(encoding="utf-8") == good
        )
    newer = good + "# edited\n"
    r = srv.post("/__save", {"path": ".ravenclaude/comfort-posture.yaml", "content": newer})
    check(
        sec,
        "a valid posture save succeeds (positive control)",
        r.status == 200,
        f"{r.status} {r.body[:200]!r}",
    )
    check(sec, "the valid posture landed", posture.read_text(encoding="utf-8") == newer)
    bak = rc_dir / "runs" / "comfort-posture.yaml.bak"
    check(
        sec,
        "the previous posture is kept at .ravenclaude/runs/comfort-posture.yaml.bak",
        bak.is_file() and bak.read_text(encoding="utf-8") == good,
    )

    # 1005-P3-18 / dashboard-12: wrong types get an HTTP error, never a reset.
    for name, path in (("list", ["x"]), ("object", {"a": 1}), ("int", 7), ("null", None)):
        r = srv.post("/__save", {"path": path, "content": "y"})
        check(
            sec,
            f"POST /__save with a {name} path is a bad request",
            r.status == 400,
            f"{r.status} {r.error}",
        )
    r = srv.post(
        "/__save", {"path": ".ravenclaude/plugins/x.yaml", "content": "k: v\n"}, token="café"
    )
    check(
        sec,
        "a non-ASCII X-CSRF-Token is refused, not reset",
        r.status == 403,
        f"{r.status} {r.error}",
    )

    # 1005-P3-20: /__host emits a closed set.
    host = (req(port, "GET", "/__host").json() or {}).get("host")
    check(sec, "/__host reports 'other' for an arbitrary THING_HOST", host == "other", repr(host))

    # dashboard-14: a non-ASCII slug is refused.
    r = srv.post("/__save", {"path": ".ravenclaude/plugins/é.yaml", "content": "k: v\n"})
    check(sec, "POST /__save of a non-ASCII plugin slug is refused", r.status == 403, f"{r.status}")

    # dashboard-15: HEAD /__* is Host-guarded; the legitimate probe still works.
    r = req(port, "HEAD", "/__csrf", host="evil.test")
    check(sec, "HEAD /__csrf with a foreign Host is refused", r.status == 403, f"{r.status}")
    r = req(port, "HEAD", "/__save", host="evil.test")
    check(sec, "HEAD /__save with a foreign Host is refused", r.status == 403, f"{r.status}")
    r = req(port, "HEAD", "/__csrf")
    check(
        sec,
        "HEAD /__csrf same-origin answers OK (positive control)",
        r.status == 200,
        f"{r.status}",
    )

    # dashboard-9: /__csrf names the project (hashed); the token is unchanged.
    data = req(port, "GET", "/__csrf").json() or {}
    check(sec, "/__csrf still returns the token", bool(data.get("token")))
    check(
        sec,
        "/__csrf project_id == sha256(project root)[:12]",
        data.get("project_id") == project_id(proj),
        f"{data.get('project_id')!r} vs {project_id(proj)!r}",
    )


# ── section: root (live root dev server) ─────────────────────────────────────


def section_root(root_server: Path, scratch: Path) -> None:
    sec = "root"
    repo = scratch / "rootrepo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy2(str(root_server), str(repo / "scripts" / "serve-dashboards.py"))
    (repo / "plugins").symlink_to(REPO / "plugins")
    (repo / "index.html").write_text("<!doctype html><title>x</title>\n", encoding="utf-8")
    (repo / ".env").write_text("API_KEY=dummy\n", encoding="utf-8")
    (repo / ".git").mkdir()
    (repo / ".git" / "config").write_text("[core]\n", encoding="utf-8")
    (repo / "docs").mkdir()
    (repo / "docs" / "a.md").write_text("# a\n", encoding="utf-8")
    (repo / ".ravenclaude").mkdir()
    (repo / ".ravenclaude" / "comfort-posture.yaml").write_text(
        "schema_version: 5\n", encoding="utf-8"
    )

    port = free_window(1)
    argv = [
        sys.executable,
        str(repo / "scripts" / "serve-dashboards.py"),
        "--port",
        str(port),
        "--bind",
        "127.0.0.1",
        "--no-open",
        "--max-idle",
        "0",
        "--no-reclaim",
    ]
    srv = Server(argv, base_env(scratch), scratch / "root-server.log", port)
    try:
        for path, want in (
            ("/index.html", 200),
            ("/docs/a.md", 200),
            ("/.env", 404),
            ("/.git/config", 404),
            ("/.ravenclaude/comfort-posture.yaml", 404),
            ("/docs/", 404),
            ("/scripts/", 404),
        ):
            r = req(port, "GET", path)
            check(sec, f"GET {path} answers {want}", r.status == want, f"{r.status} {r.error}")
        r = req(port, "HEAD", "/.env")
        check(sec, "HEAD /.env is refused as not found", r.status == 404, f"{r.status}")
        r = req(port, "HEAD", "/__csrf", host="evil.test")
        check(sec, "HEAD /__csrf with a foreign Host is refused", r.status == 403, f"{r.status}")
        r = req(port, "HEAD", "/__csrf")
        check(
            sec,
            "HEAD /__csrf same-origin answers OK (positive control)",
            r.status == 200,
            f"{r.status}",
        )
        data = req(port, "GET", "/__csrf").json() or {}
        check(
            sec,
            "/__csrf project_id == sha256(repo root)[:12]",
            data.get("project_id") == project_id(repo),
            f"{data.get('project_id')!r}",
        )
        r = srv.post("/__run", {"action": ["install"]})
        check(
            sec,
            "POST /__run with a non-string action is a bad request",
            r.status == 400,
            f"{r.status} {r.error}",
        )
    finally:
        srv.stop()


# ── section: rc (bin/rc launcher) ────────────────────────────────────────────


_FAKE_DASH = r"""
import http.server, json, sys
pid = sys.argv[2]
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def do_GET(self):
        if self.path.startswith("/__spectate/capabilities"):
            body = b'{"ok": true}'
        elif self.path == "/__csrf":
            body = json.dumps({"token": "t", "project_id": pid}).encode()
        else:
            self.send_response(404); self.end_headers(); return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
http.server.HTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
"""


def _kill_servers_for(proj: Path) -> None:
    """Stop any serve-dashboards.py child launched for `proj` (rc spectate detaches it)."""
    try:
        out = subprocess.run(["ps", "-eo", "pid=,args="], capture_output=True, text=True).stdout
    except OSError:
        return
    needle = f"--project-root {proj}"
    for line in out.splitlines():
        line = line.strip()
        if needle in line and "serve-dashboards.py" in line:
            try:
                os.kill(int(line.split(None, 1)[0]), signal.SIGTERM)
            except (OSError, ValueError):
                pass


def section_rc(rc: Path, plugin_server: Path, scratch: Path) -> None:
    sec = "rc"
    if shutil.which("curl") is None:
        raise CannotRun("curl not found (bin/rc probes with curl)")
    shim = build_shim_plugin(
        scratch / "rcmkt" / "plugins" / "ravenclaude-core",
        {"bin/rc": rc, "scripts/serve-dashboards.py": plugin_server},
    )
    # corescripts-17: a two-level RELATIVE symlink chain resolves the plugin dir.
    links = scratch / "rcmkt" / "home"
    (links / "bin").mkdir(parents=True)
    (links / "links").mkdir()
    (links / "bin" / "rc-rel").symlink_to(
        Path("..") / ".." / "plugins" / "ravenclaude-core" / "bin" / "rc"
    )
    (links / "links" / "rc-chain").symlink_to(Path("..") / "bin" / "rc-rel")
    elsewhere = scratch / "elsewhere"
    elsewhere.mkdir()
    env = base_env(scratch)
    for label, link in (
        ("one-level relative link", links / "bin" / "rc-rel"),
        ("two-level relative chain", links / "links" / "rc-chain"),
    ):
        r = subprocess.run(
            ["bash", str(link), "streams", "status"],
            cwd=str(elsewhere),
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        check(
            sec,
            f"rc via a {label}, run from another dir, finds the plugin",
            r.returncode == 0 and "streams:" in r.stdout,
            (r.stdout + r.stderr).strip()[:200],
        )

    # dashboard-9: `rc spectate` must not attach to another project's live server.
    base = free_window(12)
    sp = scratch / "spproj"
    sp.mkdir()
    fake_py = scratch / "fake_dash.py"
    fake_py.write_text(_FAKE_DASH, encoding="utf-8")
    fake = subprocess.Popen(
        [sys.executable, str(fake_py), str(base), "f0f0f0f0f0f0"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        deadline = time.time() + 10
        while time.time() < deadline and req(base, "GET", "/__csrf", timeout=1).status != 200:
            time.sleep(0.1)
        r = subprocess.run(
            ["bash", str(shim / "bin" / "rc"), "spectate", "--no-open", "--port", str(base)],
            cwd=str(sp),
            env=env,
            capture_output=True,
            text=True,
            timeout=90,
        )
        lines = r.stdout.strip().splitlines()
        url = lines[-1] if lines else ""
        bound = ""
        if url.startswith("http://127.0.0.1:"):
            bound = url[len("http://127.0.0.1:") :].split("/", 1)[0]
        check(
            sec,
            "rc spectate skips a live server reporting another project's id",
            bound != "" and bound != str(base),
            f"url={url!r} stderr={r.stderr.strip()[:200]!r}",
        )
        if bound and bound != str(base):
            data = req(int(bound), "GET", "/__csrf").json() or {}
            check(
                sec,
                "the server rc spectate attached to reports this project's id",
                data.get("project_id") == project_id(sp),
                f"{data.get('project_id')!r}",
            )
    finally:
        try:
            os.killpg(fake.pid, signal.SIGTERM)
        except OSError:
            pass
        _kill_servers_for(sp)


# ── --must-fail: mutants of the CURRENT files must each be caught ─────────────

_MUTANTS = (
    # (label, which file, old text, new text, section, row-substring that must go red)
    (
        "reserve engine resolved from the project tree again",
        "plugin",
        '        script = _TRUSTED_PLUGIN_ROOT / "scripts" / "routine-reserve.py"\n',
        '        script = project_root / "plugins" / "ravenclaude-core" / "scripts" / "routine-reserve.py"\n'
        "        if not script.is_file():\n"
        '            script = _TRUSTED_PLUGIN_ROOT / "scripts" / "routine-reserve.py"\n',
        "plugin",
        "no decoy engine/hook from the project tree was executed",
    ),
    (
        "symlink walk removed from /__save",
        "plugin",
        '        if _target_has_symlink(PROJECT_ROOT, target):\n            self.send_error(403, "path traverses a symlink")\n            return\n        if not isinstance(content, str):',
        "        if not isinstance(content, str):",
        "plugin",
        "POST /__save through an in-root symlink is refused",
    ),
    (
        "HEAD /__* Host guard removed",
        "plugin",
        '        if path_base.startswith("/__") and not self._local_request_ok():\n',
        '        if False and path_base.startswith("/__") and not self._local_request_ok():\n',
        "plugin",
        "HEAD /__csrf with a foreign Host is refused",
    ),
    (
        "root dot-path refusal removed",
        "root",
        '        if any(part.startswith(".") for part in parts):\n',
        "        if False:\n",
        "root",
        "GET /.env answers 404",
    ),
)


def must_fail(scratch: Path) -> int:
    caught = 0
    for i, (label, key, old, new, section, row) in enumerate(_MUTANTS):
        src = PLUGIN_SERVER if key == "plugin" else ROOT_SERVER
        text = src.read_text(encoding="utf-8")
        if old not in text:
            print(f"  [FAIL] must-fail: mutant {label!r} did not apply (anchor moved)")
            continue
        mdir = scratch / f"mutant-{i}"
        mdir.mkdir()
        mut = mdir / "serve-dashboards.py"
        mut.write_text(text.replace(old, new, 1), encoding="utf-8")
        RESULTS.clear()
        work = mdir / "work"
        work.mkdir()
        try:
            if section == "plugin":
                section_plugin(mut, work)
            else:
                section_root(mut, work)
        except CannotRun as e:
            print(f"  [FAIL] must-fail: mutant {label!r} could not run: {e}")
            continue
        failed = [n for (_s, n, ok, _d) in RESULTS if not ok]
        if any(row in n for n in failed):
            caught += 1
            print(f"  [ok  ] must-fail: mutant {label!r} is caught by {row!r}")
        else:
            print(f"  [FAIL] must-fail: mutant {label!r} was NOT caught (row {row!r} stayed green)")
    RESULTS.clear()
    print(f"must-fail: {caught}/{len(_MUTANTS)} mutants caught")
    return 0 if caught == len(_MUTANTS) else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--repo", default=None, help="repo root (default: this script's parent dir)")
    ap.add_argument("--root-server", default=None)
    ap.add_argument("--plugin-server", default=None)
    ap.add_argument("--rc", default=None)
    ap.add_argument("--parity-checker", default=None)
    ap.add_argument("--only", choices=("static", "unit", "plugin", "root", "rc"))
    ap.add_argument("--must-fail", action="store_true", help="prove the live rows have teeth")
    ap.add_argument("--keep", action="store_true", help="keep the scratch dir (prints its path)")
    args = ap.parse_args()
    if args.repo:
        _configure(Path(args.repo))
    root_server = Path(args.root_server) if args.root_server else ROOT_SERVER
    plugin_server = Path(args.plugin_server) if args.plugin_server else PLUGIN_SERVER
    rc = Path(args.rc) if args.rc else RC
    parity = Path(args.parity_checker) if args.parity_checker else PARITY

    scratch = Path(tempfile.mkdtemp(prefix="rc-dash-hardening-")).resolve()
    try:
        if args.must_fail:
            return must_fail(scratch)
        sections = [args.only] if args.only else ["static", "unit", "plugin", "root", "rc"]
        for s in sections:
            sdir = scratch / s
            sdir.mkdir()
            print(f"── {s}")
            if s == "static":
                section_static(parity, sdir)
            elif s == "unit":
                section_unit(root_server, plugin_server, sdir)
            elif s == "plugin":
                section_plugin(plugin_server, sdir)
            elif s == "root":
                section_root(root_server, sdir)
            elif s == "rc":
                section_rc(rc, plugin_server, sdir)
    except CannotRun as e:
        print(f"COULD NOT RUN: {e}", file=sys.stderr)
        return 2
    finally:
        if args.keep:
            print(f"scratch kept at {scratch}")
        else:
            shutil.rmtree(str(scratch), ignore_errors=True)
    failed = [r for r in RESULTS if not r[2]]
    print(f"\n{len(RESULTS) - len(failed)} pass, {len(failed)} fail")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
