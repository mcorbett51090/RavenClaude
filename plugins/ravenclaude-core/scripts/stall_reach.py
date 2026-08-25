#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stall_reach.py — the reach layer for stall_watch.

THREE MEASURED CONSTRAINTS SHAPE THIS FILE.

RT-1 — the secret cannot travel in the environment. A real bootstrapped
LaunchAgent sees 12 env vars with PATH=/usr/bin:/bin:/usr/sbin:/sbin, and an
exported RAVENCLAUDE_NOTIFY_WEBHOOK is simply ABSENT (positive control: HOME,
USER, TMPDIR, SSH_AUTH_SOCK all arrive). `launchctl setenv` is worse — readable
by any fully env-scrubbed process and gone at logout. So the URL lives in a
0600 file and reaches curl through `--config`, never through argv, where
`ps -Ao args` would expose it 288 times a day.

RT-4 — a receipt must survive. The repo's own scripts/notify.sh does
`curl -fsS ... >/dev/null 2>&1 || true`, which silences the status and swallows
the failure. Reusing it would destroy the HTTP receipt that is the entire
justification for choosing a webhook. We capture %{http_code} and record it.
`-k` is never passed: it turns a captive portal's login page into a recorded 200.

CE-2 — no untrusted text is ever interpolated. A project directory name is
attacker-influenceable (a cloned repo names its own directory). Everything in a
payload is a fixed template string, a validated integer, or a salted hash.

WHAT A 2xx MEANS, STATED HONESTLY: "accepted by the sink". Not "pushed", not
"delivered to the device", and certainly not "a human saw it" — an ntfy topic
with zero subscribers returns 200. The word `delivered` is deliberately not
used anywhere in this file.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple

HOME = os.path.expanduser("~")
STATE_DIR = os.path.join(HOME, ".claude", "stall-watch")
SINKS_PATH = os.path.join(STATE_DIR, "sinks.json")

# Anything placed in a payload must match this. Belt-and-braces on top of the
# fact that every field is already derived: a hash, an int, or a fixed string.
_SAFE = re.compile(r"^[A-Za-z0-9 ,.:%()\[\]/_@=+-]*$")

DEFAULT_CONNECT_TIMEOUT = 5
DEFAULT_MAX_TIME = 15


def load_sinks() -> Dict:
    try:
        with open(SINKS_PATH, "r") as fh:
            return json.load(fh)
    except IOError:
        return {"sinks": []}
    except ValueError:
        return {"sinks": [], "error": "sinks.json unparseable"}


def _assert_safe(value: str, field: str) -> str:
    if not _SAFE.match(value or ""):
        raise ValueError("unsafe characters in payload field %r" % field)
    return value or ""


def build_message(alerts: List[Dict]) -> Tuple[str, str]:
    """Fixed template + validated integers + salted hashes. Nothing else."""
    if not alerts:
        return ("Claude stall watchdog", "No stalled sessions.")
    first = alerts[0]
    title = "Claude session stalled"
    parts = []
    for a in alerts:
        session = _assert_safe(str(a.get("session", ""))[:8], "session")
        project = _assert_safe(str(a.get("project", ""))[:16], "project")
        silent = int(round(float(a.get("silent_min") or 0)))
        masked = a.get("masked_min")
        pid = int(a.get("pid") or 0)
        line = "session %s (pid %d, project %s): no assistant output for %d min" % (
            session, pid, project, silent)
        if masked is not None:
            line += "; %d min of that was masked by non-progress writes" % int(round(float(masked)))
        compactions = a.get("compactions")
        if isinstance(compactions, int):
            line += "; %d completed compactions" % compactions
        parts.append(line)
    if len(alerts) > 1:
        title = "%d Claude sessions stalled" % len(alerts)
    return (title, "\n".join(parts))


def _curl_config(sink: Dict, title: str, body: str, cfg: Dict) -> str:
    """Build a curl --config document. The URL lives HERE, not in argv."""
    url = sink.get("url") or ""
    lines = [
        'url = "%s"' % url.replace('\\', '\\\\').replace('"', '\\"'),
        'request = "POST"',
        'silent',
        'show-error',
        'connect-timeout = %d' % int(cfg.get("connect_timeout_sec", DEFAULT_CONNECT_TIMEOUT)),
        'max-time = %d' % int(cfg.get("max_time_sec", DEFAULT_MAX_TIME)),
        'write-out = "%{http_code}"',
    ]
    kind = (sink.get("kind") or "").lower()
    if kind == "slack":
        payload = json.dumps({"text": "*%s*\n%s" % (title, body)})
        lines.append('header = "Content-Type: application/json"')
        lines.append('data = "%s"' % payload.replace('\\', '\\\\').replace('"', '\\"'))
    else:  # ntfy and generic text sinks
        lines.append('header = "Title: %s"' % title)
        lines.append('header = "Priority: high"')
        lines.append('header = "Tags: warning"')
        lines.append('data = "%s"' % body.replace('\\', '\\\\').replace('"', '\\"'))
    return "\n".join(lines) + "\n"


def send_one(sink: Dict, title: str, body: str, cfg: Dict) -> Dict:
    """Returns a receipt. `http_code` is the only evidence of anything."""
    name = sink.get("name") or sink.get("kind") or "sink"
    if not sink.get("enabled") or not sink.get("url"):
        return {"sink": name, "skipped": "not configured"}
    doc = _curl_config(sink, title, body, cfg)
    fd, path = tempfile.mkstemp(prefix="stall-curl-", dir=STATE_DIR)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w") as fh:
            fh.write(doc)
        proc = subprocess.run(["curl", "--config", path],
                              capture_output=True, text=True, timeout=30)
        code = (proc.stdout or "").strip()[-3:]
        receipt = {"sink": name, "http_code": code or None,
                   "curl_rc": proc.returncode}
        if proc.returncode != 0:
            # 6=DNS, 7=connect refused, 28=timeout, 60=TLS. Recorded, not hidden.
            receipt["error"] = (proc.stderr or "").strip()[:200]
        receipt["accepted"] = bool(code[:1] == "2")
        return receipt
    except Exception as exc:
        return {"sink": name, "error": "%s: %s" % (type(exc).__name__, exc),
                "accepted": False}
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def dispatch(alerts: List[Dict]) -> Dict:
    """Send to every enabled sink. Returns receipts and whether ANY sink
    accepted — the ladder advances on receipt, never on attempt, because the
    attempt branch reintroduces exactly the silent miss this tool exists to
    prevent."""
    cfg = load_sinks()
    title, body = build_message(alerts)
    receipts = [send_one(s, title, body, cfg) for s in cfg.get("sinks", [])]
    return {
        "title": title,
        "receipts": receipts,
        "any_accepted": any(r.get("accepted") for r in receipts),
        "configured_sinks": sum(1 for s in cfg.get("sinks", []) if s.get("enabled") and s.get("url")),
    }


if __name__ == "__main__":
    import sys
    demo = [{"session": "TESTONLY", "project": "0" * 16, "pid": 0,
             "silent_min": 42.0, "masked_min": 7.0, "compactions": 0}]
    out = dispatch(demo if "--test" in sys.argv else [])
    json.dump(out, sys.stdout, indent=1, sort_keys=True)
    sys.stdout.write("\n")
    sys.exit(0 if out["any_accepted"] or not out["configured_sinks"] else 1)
