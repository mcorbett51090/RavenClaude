#!/usr/bin/env python3
"""check-streams-prompt-hook.py — Gate 114 engine for Agentic Work-Streams (P4).

Proves the per-prompt UserPromptSubmit hook (the highest-risk surface — security-reviewed)
holds its four invariants:

  1. FAIL-OPEN — the hook ALWAYS exits 0 and never blocks/alters the prompt: opted-out
     (no stream_hook), corrupt registry, missing python (skipped — can't unset here),
     and a normal opt-in run all exit 0. Disabling the "always exit 0" tail (must-fail
     half) makes a forced error escape nonzero, proving the guard has teeth.
  2. NO-EGRESS — with the hook on + an active stream, a distinctive multi-word prompt
     phrase is attributed as a DERIVED event; the phrase (and any 4-word window) is ABSENT
     from the stored history. Only single-token terms / counts / session_id persist.
  3. OPT-IN — default (no `stream_hook: per_prompt`) → the hook is a no-op (writes nothing),
     even with an active stream.
  4. LATENCY CEILING — the hook honors RC_STREAM_HOOK_BUDGET_S (a `timeout` wrapper bounds
     the inner work); we assert the hook completes well under a generous wall-clock bound
     on a normal run (a coarse guard that the budget path is wired).

Plus a COPILOT-PARITY check: the installer wires `userpromptsubmit` for the hook, the
adapter has a `userpromptsubmit` mode, and hooks.json declares UserPromptSubmit.

Modes:
  (default)             run the assertions.
  --must-fail-failopen  run the hook with its final `exit 0` stripped + a forced inner
                        error; assert it THEN exits nonzero (proving fail-open has teeth).
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HOOK = REPO / "plugins/ravenclaude-core/hooks/stream-prompt-attribute.sh"
ADAPTER = REPO / "plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh"
OPS = REPO / "plugins/ravenclaude-core/scripts/stream-ops.py"
PLUGIN_ROOT = REPO / "plugins/ravenclaude-core"
HOOKS_JSON = PLUGIN_ROOT / "hooks/hooks.json"
INSTALLER = REPO / "scripts/ravenclaude"

PHRASE = "the NEBULA-9 confidential billing migration rollback nobody approved tonight"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_hook(project_dir: str, prompt: str, session_id: str = "s", env_extra=None):
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = project_dir
    env["CLAUDE_PLUGIN_ROOT"] = str(PLUGIN_ROOT)
    if env_extra:
        env.update(env_extra)
    payload = json.dumps({"prompt": prompt, "session_id": session_id})
    return subprocess.run(
        ["bash", str(HOOK)], input=payload, text=True, capture_output=True, env=env, timeout=30
    )


def _seed(ops, d: str, name: str, active: bool):
    ops.create_stream(d, name, ts="2026-06-23T00:00:00Z")
    sid = ops.slugify(name)
    if active:
        ops.set_active(d, sid)
    return sid


def _write_cfg(d: str, body: str):
    rc = Path(d) / ".ravenclaude"
    rc.mkdir(parents=True, exist_ok=True)
    (rc / "comfort-posture.yaml").write_text(body, encoding="utf-8")


def check_opt_in_default(ops) -> list[str]:
    errs = []
    with tempfile.TemporaryDirectory() as d:
        _write_cfg(d, "design_checkins: true\n")  # posture present but no stream_hook
        sid = _seed(ops, d, "Billing Work", active=True)
        r = _run_hook(d, PHRASE)
        if r.returncode != 0:
            errs.append(f"opt-out: hook nonzero (exit {r.returncode})")
        hist = Path(d) / ".ravenclaude" / "streams" / sid / "history.jsonl"
        if hist.exists():
            errs.append("opt-out: hook wrote history despite no stream_hook: per_prompt")
    return errs


def check_no_egress(ops) -> list[str]:
    errs = []
    with tempfile.TemporaryDirectory() as d:
        _write_cfg(d, "stream_hook: per_prompt\n")
        sid = _seed(ops, d, "Billing Work", active=True)
        r = _run_hook(d, PHRASE)
        if r.returncode != 0:
            errs.append(f"opt-in: hook nonzero (exit {r.returncode})")
        hist_path = Path(d) / ".ravenclaude" / "streams" / sid / "history.jsonl"
        if not hist_path.exists():
            errs.append("opt-in: hook did not attribute the prompt")
            return errs
        hist = hist_path.read_text(encoding="utf-8")
        if '"kind": "prompt_attributed"' not in hist:
            errs.append("opt-in: no prompt_attributed event written")
        if PHRASE in hist:
            errs.append("NO-EGRESS VIOLATION: prompt phrase in history")
        words = PHRASE.split()
        for i in range(len(words) - 3):
            if " ".join(words[i:i + 4]) in hist:
                errs.append("NO-EGRESS VIOLATION: 4-word window in history")
                break
    return errs


def check_fail_open(ops) -> list[str]:
    errs = []
    # corrupt registry -> still exit 0, no crash
    with tempfile.TemporaryDirectory() as d:
        _write_cfg(d, "stream_hook: per_prompt\n")
        sd = Path(d) / ".ravenclaude" / "streams"
        sd.mkdir(parents=True, exist_ok=True)
        (sd / "registry.json").write_text("not json {{{", encoding="utf-8")
        (sd / "active-stream").write_text("billing-work\n", encoding="utf-8")
        r = _run_hook(d, PHRASE)
        if r.returncode != 0:
            errs.append(f"fail-open: corrupt registry made the hook nonzero (exit {r.returncode})")
    # no payload at all -> exit 0
    with tempfile.TemporaryDirectory() as d:
        _write_cfg(d, "stream_hook: per_prompt\n")
        env = dict(os.environ)
        env["CLAUDE_PROJECT_DIR"] = d
        env["CLAUDE_PLUGIN_ROOT"] = str(PLUGIN_ROOT)
        r = subprocess.run(["bash", str(HOOK)], input="", text=True, capture_output=True, env=env, timeout=30)
        if r.returncode != 0:
            errs.append(f"fail-open: empty payload made the hook nonzero (exit {r.returncode})")
    return errs


def check_latency(ops) -> list[str]:
    errs = []
    with tempfile.TemporaryDirectory() as d:
        _write_cfg(d, "stream_hook: per_prompt\n")
        _seed(ops, d, "Billing Work", active=True)
        t0 = time.monotonic()
        r = _run_hook(d, PHRASE, env_extra={"RC_STREAM_HOOK_BUDGET_S": "3"})
        elapsed = time.monotonic() - t0
        # Generous wall-clock bound — a normal run is well under a second; this proves the
        # budget path is wired and the hook returns promptly (not that the budget itself fired).
        if elapsed > 10.0:
            errs.append(f"latency: hook took {elapsed:.1f}s (budget path not bounding)")
        if r.returncode != 0:
            errs.append("latency: hook nonzero on the budgeted run")
        # The hook must reference the budget env var (the latency-ceiling mechanism).
        body = HOOK.read_text(encoding="utf-8")
        if "RC_STREAM_HOOK_BUDGET_S" not in body or "timeout" not in body:
            errs.append("latency: hook does not implement a timeout budget")
    return errs


def check_copilot_parity() -> list[str]:
    errs = []
    hj = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    ups = hj.get("hooks", {}).get("UserPromptSubmit")
    if not ups:
        errs.append("parity: hooks.json has no UserPromptSubmit entry")
    elif "stream-prompt-attribute.sh" not in json.dumps(ups):
        errs.append("parity: UserPromptSubmit does not wire stream-prompt-attribute.sh")
    adapter = ADAPTER.read_text(encoding="utf-8")
    if "userpromptsubmit)" not in adapter:
        errs.append("parity: copilot adapter has no userpromptsubmit mode")
    installer = INSTALLER.read_text(encoding="utf-8")
    if "userpromptsubmit" not in installer or "stream-prompt-attribute.sh" not in installer:
        errs.append("parity: installer does not wire the userpromptsubmit hook into .github/hooks")
    return errs


def must_fail_failopen() -> int:
    """Strip the hook's final `exit 0` + force an inner error; assert it exits nonzero."""
    body = HOOK.read_text(encoding="utf-8")
    # Build a broken variant: remove the trailing `exit 0` and append a guaranteed failure
    # AFTER the python block (so the fail-open tail is what normally swallows it).
    broken = body.replace("\nexit 0\n", "\n", 1)
    broken += "\nfalse  # forced failure with the fail-open exit-0 stripped\n"
    with tempfile.TemporaryDirectory() as d:
        bh = Path(d) / "broken-hook.sh"
        bh.write_text(broken, encoding="utf-8")
        _write_cfg(d, "stream_hook: per_prompt\n")
        ops = _load(OPS, "stream_ops")
        _seed(ops, d, "Billing Work", active=True)
        env = dict(os.environ)
        env["CLAUDE_PROJECT_DIR"] = d
        env["CLAUDE_PLUGIN_ROOT"] = str(PLUGIN_ROOT)
        r = subprocess.run(["bash", str(bh)], input=json.dumps({"prompt": "x", "session_id": "s"}),
                           text=True, capture_output=True, env=env, timeout=30)
        if r.returncode != 0:
            print("  must-fail-failopen: broken hook (no exit 0) returns nonzero — fail-open tail has teeth")
            return 0
        print("  must-fail-failopen: ERROR — broken hook still returned 0", file=sys.stderr)
        return 1


def main(argv: list[str]) -> int:
    if "--must-fail-failopen" in argv:
        return must_fail_failopen()

    ops = _load(OPS, "stream_ops")
    errs: list[str] = []
    errs += check_opt_in_default(ops)
    errs += check_no_egress(ops)
    errs += check_fail_open(ops)
    errs += check_latency(ops)
    errs += check_copilot_parity()

    if errs:
        print("Gate 114 FAILURES:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("  fail-open OK | no-egress OK | opt-in default OK | latency-ceiling wired OK | "
          "Copilot parity OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
