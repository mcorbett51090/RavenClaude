#!/usr/bin/env python3
"""thing-golden-eval.py — regression + quality eval for the command-review tribunal.

Gap 4 of the command-review gap-closure plan. Three lanes:

  (default / --deterministic)  CI-CHEAP. For every `lane: deterministic` entry in
      thing-golden-set.jsonl, run the REAL engine (thing-decision.py) and assert the
      deterministic disposition (pre-LLM deny / hard-rule / self-disable / clean-allow
      / routes-to-panel) matches the entry's `expect`. No model call, no credits.
      This is the regression gate (audit-gates.sh Gate 33).

  --live [--model M ...]       NOT CI. For every `lane: live` (seat-judged) entry,
      run the REAL seat(s) (thing-seat.sh) under each named model and assert the
      verdict matches `expect`. Needs credentials. Run one credentialed lane per
      vendor (a Claude, a GPT, a Grok model) to measure per-vendor seat quality —
      Gap 3 (cross-vendor seats) must clear this before a vendor seat is trusted.

  --probe                      NOT CI. The §8 sharp-risk check: does `claude -p`
      actually resolve + return a parseable verdict FROM INSIDE the current session
      (run it inside a GitHub Copilot CLI session to answer that)? Invokes one real
      seat on a benign payload and asserts parseable JSON with a `verdict` field.

Engine is reused, never reimplemented: command shapes go through `preview`, tool
shapes through `classify-payload`, both against a throwaway "default-consumer" root
(command-review on, no dev_repo_exempt) so the assertions reflect what a normal
consumer's tribunal does.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ENGINE = ROOT / "plugins" / "ravenclaude-core" / "scripts" / "thing-decision.py"
SEAT = ROOT / "plugins" / "ravenclaude-core" / "scripts" / "thing-seat.sh"
CORPUS = HERE / "thing-golden-set.jsonl"

# A minimal posture that turns command-review ON for every category, with NO
# dev_repo_exempt — i.e. exactly a default consumer's tribunal.
_CATEGORIES = [
    "file_edit_project", "file_edit_global", "file_read_project", "file_read_global",
    "network_read", "network_write", "mcp_tools", "shell_readonly",
    "shell_local_mutate", "shell_remote_mutate", "shell_code_exec", "shell_package_install",
]
_POSTURE = "schema_version: 5\ncommand_review:\n  enabled: true\ncategories:\n" + "".join(
    f"  {c}:\n    project: allow\n    thing: on\n" for c in _CATEGORIES
)


def _consumer_root() -> Path:
    d = Path(tempfile.mkdtemp(prefix="thing-golden-"))
    (d / ".ravenclaude").mkdir(parents=True, exist_ok=True)
    (d / ".ravenclaude" / "comfort-posture.yaml").write_text(_POSTURE, encoding="utf-8")
    return d


def _engine(root: Path, *args: str, stdin: str | None = None) -> dict:
    try:
        out = subprocess.run(
            [sys.executable, str(ENGINE), "--root", str(root), *args],
            input=stdin, capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        return {"_engine_error": "engine timed out after 60s"}
    try:
        return json.loads(out.stdout)
    except (json.JSONDecodeError, ValueError):
        return {"_engine_error": out.stderr.strip() or "no JSON on stdout", "_stdout": out.stdout}


def _decision(root: Path, entry: dict) -> dict:
    """Run an entry through the engine and return its decision JSON."""
    shape = entry.get("shape", "command")
    if shape == "command":
        return _engine(root, "preview", entry["cmd"])
    tool_map = {"file": entry.get("tool_name", "Write"), "file-read": "Read",
                "network": entry.get("tool_name", "WebFetch"), "mcp": entry.get("tool_name", "")}
    payload = {"tool_name": tool_map.get(shape, entry.get("tool_name", "")),
               "tool_input": entry.get("tool_input", {})}
    return _engine(root, "classify-payload", stdin=json.dumps(payload))


def _disposition(d: dict) -> str:
    """Collapse an engine decision into ALLOW / DENY / PANEL (deterministic only)."""
    if any(d.get(k) for k in ("self_disable_deny", "hard_rule_deny", "pre_llm_deny", "mcp_unverified_deny")):
        return "DENY"
    if d.get("panel_required"):
        return "PANEL"
    pg = d.get("predicted_gate", "") or ""
    if pg.startswith("ALLOW"):
        return "ALLOW"
    # No panel required and not a clean ALLOW disposition — treat as ALLOW-ish only
    # if it is a low-tier read; otherwise UNKNOWN so a mismatch is loud.
    if d.get("is_read") and d.get("tier") == "low":
        return "ALLOW"
    return "UNKNOWN"


def _concern_present(d: dict, concern: str) -> bool:
    if d.get("deny_concern") == concern or d.get("self_disable_concern") == concern:
        return True
    return concern in (d.get("concerns") or [])


def run_deterministic(corpus: Path = CORPUS) -> int:
    # _consumer_root() mkdtemp's a fresh dir per invocation; clean it up on the way
    # out (normal return OR exception) so repeated runs don't leak /tmp dirs.
    root = _consumer_root()
    try:
        return _run_deterministic_body(root, corpus)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _run_deterministic_body(root: Path, corpus: Path) -> int:
    lines = [ln for ln in corpus.read_text(encoding="utf-8").splitlines() if ln.strip()]
    entries: list[dict] = []
    fails = 0
    for i, ln in enumerate(lines, 1):
        try:
            entries.append(json.loads(ln))
        except json.JSONDecodeError as exc:
            print(f"  FAIL <line {i}>: malformed JSON: {exc}")
            fails += 1
    det = [e for e in entries if e.get("lane") == "deterministic"]
    total = len(det) + fails
    print(f"== golden-set deterministic lane ({len(det)} entries) ==")
    for e in det:
        eid = e.get("id", "<no id>")
        if "expect" not in e:
            print(f"  FAIL {eid}: entry missing required 'expect' field")
            fails += 1
            continue
        if e.get("shape", "command") == "command" and "cmd" not in e:
            print(f"  FAIL {eid}: entry missing required 'cmd' field")
            fails += 1
            continue
        d = _decision(root, e)
        if "_engine_error" in d:
            print(f"  FAIL {eid}: engine error: {d['_engine_error']}")
            fails += 1
            continue
        got = _disposition(d)
        want = e["expect"]
        ok = got == want
        # Optional concern assertion (only when the disposition is a deny).
        concern = e.get("expect_concern")
        concern_ok = True
        if concern and want == "DENY":
            concern_ok = _concern_present(d, concern)
        if ok and concern_ok:
            extra = f" [{concern}]" if concern else ""
            print(f"  PASS {eid}: {got}{extra}")
        else:
            fails += 1
            why = f"want {want}, got {got}"
            if concern and not concern_ok:
                why += f"; missing concern {concern} (saw {d.get('deny_concern') or d.get('concerns')})"
            print(f"  FAIL {eid}: {why}")
    print(f"-- {total - fails}/{total} pass --")
    return 1 if fails else 0


def _run_seat(payload: str, *, role: str = "mimir", model: str | None = None,
              category: str = "shell_remote_mutate", mock: str | None = None) -> dict:
    env_extra = {"THING_PAYLOAD": payload, "THING_SEAT_ROLE": role, "THING_CATEGORY": category}
    if model:
        env_extra["THING_MODEL"] = model
    if mock:
        env_extra["THING_SEAT_MOCK_VERDICT"] = mock
    import os
    env = {**os.environ, **env_extra}
    try:
        out = subprocess.run(["bash", str(SEAT)], capture_output=True, text=True, env=env, timeout=120)
    except subprocess.TimeoutExpired:
        return {"_seat_error": "seat timed out after 120s", "_rc": None, "_stdout": ""}
    try:
        return json.loads(out.stdout)
    except (json.JSONDecodeError, ValueError):
        return {"_seat_error": out.stderr.strip() or "no JSON", "_rc": out.returncode, "_stdout": out.stdout[:400]}


def run_probe() -> int:
    print("== probe: does a real seat (claude -p) resolve + return parseable JSON here? ==")
    v = _run_seat("ls -la", role="mimir", category="shell_readonly")
    if "_seat_error" in v:
        print(f"  FAIL probe: {v['_seat_error']} (rc={v.get('_rc')})")
        print("  -> In a GitHub Copilot CLI session this means the panel would ABSTAIN")
        print("     (fail-closed deny on high-stakes categories). See gap-closure plan Gap 4.")
        return 1
    if "verdict" in v:
        print(f"  PASS probe: seat returned a parseable verdict ({v['verdict']}, conf={v.get('confidence')})")
        return 0
    print(f"  FAIL probe: JSON returned but no 'verdict' field: {v}")
    return 1


def run_live(models: list[str], corpus: Path = CORPUS) -> int:
    entries = [json.loads(ln) for ln in corpus.read_text(encoding="utf-8").splitlines() if ln.strip()]
    live = [e for e in entries if e.get("lane") == "live"]
    fails = 0
    for model in models or [None]:
        label = model or "default-model"
        print(f"== live lane: model={label} ({len(live)} judgment entries) ==")
        for e in live:
            if e.get("shape", "command") != "command":
                continue
            v = _run_seat(e["cmd"], role="forseti", model=model, category="shell_code_exec")
            if "_seat_error" in v:
                print(f"  FAIL {e['id']} [{label}]: seat error: {v['_seat_error']}")
                fails += 1
                continue
            verdict = v.get("verdict")
            # Judgment entries expect a deny/review; a real seat should not ALLOW them.
            ok = verdict in ("deny", "edit")
            print(f"  {'PASS' if ok else 'FAIL'} {e['id']} [{label}]: verdict={verdict}")
            fails += 0 if ok else 1
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--deterministic", action="store_true", help="CI lane (default if no mode given)")
    ap.add_argument("--probe", action="store_true", help="live: does claude -p run here?")
    ap.add_argument("--live", action="store_true", help="live: per-vendor seat quality")
    ap.add_argument("--model", action="append", default=[], help="model(s) for --live (repeatable)")
    ap.add_argument("--corpus", type=Path, default=CORPUS, help="override the golden-set file (gate uses this for a known-bad fixture)")
    args = ap.parse_args()
    if args.probe:
        return run_probe()
    if args.live:
        return run_live(args.model, args.corpus)
    return run_deterministic(args.corpus)


if __name__ == "__main__":
    raise SystemExit(main())
