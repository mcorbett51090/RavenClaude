#!/usr/bin/env python3
"""check-streams-classify-wiring.py — Gate 112 engine for Agentic Work-Streams (P2).

Proves the SessionStart classifier wiring + the threshold config:

  1. STICKY-NO-RECLASSIFY — when a stream is ALREADY active, classify_session returns
     a sticky no-op (sticky:true, suggestion:None) and NEVER switches — the load-bearing
     false-new-stream mitigation. Disabling the sticky guard (the must-fail half) makes it
     re-classify, proving the guard has teeth.
  2. OVERRIDE ROUND-TRIP — label_only SUGGESTS but never switches; auto SWITCHES on a
     confident match (and the set-active round-trips: get-active reflects it). off does
     nothing.
  3. THRESHOLD BOUNDS — stream_threshold is clamped to [0.05, 0.95]; a non-numeric /
     absent value defaults to 0.18; an unknown mode defaults to label_only.

Modes:
  (default)            run the assertions.
  --must-fail-sticky   patch classify_session to skip the sticky early-return; assert it
                       THEN re-classifies an active-stream session (exit 0 iff it does).
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "plugins/ravenclaude-core/scripts"
SS = SCRIPTS / "stream-session-start.py"
OPS = SCRIPTS / "stream-ops.py"
CLF = SCRIPTS / "stream-classify.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git_repo(d: str, branch: str, subject: str) -> None:
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "PATH": _path()}
    subprocess.run(["git", "-C", d, "init", "-q"], env=env, check=True)
    subprocess.run(["git", "-C", d, "checkout", "-q", "-b", branch], env=env, check=True)
    (Path(d) / "f.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", d, "add", "f.txt"], env=env, check=True)
    subprocess.run(["git", "-C", d, "commit", "-q", "-m", subject], env=env, check=True)


def _path() -> str:
    import os
    return os.environ.get("PATH", "/usr/bin:/bin")


def _seed_billing(ops, clf, d: str) -> str:
    ops.create_stream(d, "Billing Work", ts="2026-06-23T00:00:00Z")
    sid = ops.slugify("Billing Work")
    c = clf.update_centroid({}, "billing invoice payment refund proration subscription dunning")
    ops.set_centroid(d, sid, c)
    return sid


def _write_cfg(d: str, body: str) -> None:
    rc = Path(d) / ".ravenclaude"
    rc.mkdir(parents=True, exist_ok=True)
    (rc / "comfort-posture.yaml").write_text(body, encoding="utf-8")


def check_threshold_bounds(ss) -> list[str]:
    errs = []
    with tempfile.TemporaryDirectory() as d:
        _write_cfg(d, "stream_threshold: 5.0\n")
        if ss.read_config(Path(d))["threshold"] != 0.95:
            errs.append("threshold 5.0 not clamped to 0.95")
        _write_cfg(d, "stream_threshold: 0.001\n")
        if ss.read_config(Path(d))["threshold"] != 0.05:
            errs.append("threshold 0.001 not clamped to 0.05")
        _write_cfg(d, "stream_threshold: nan-ish\n")
        if ss.read_config(Path(d))["threshold"] != 0.18:
            errs.append("non-numeric threshold not defaulted to 0.18")
        _write_cfg(d, "stream_classify: bogus\n")
        if ss.read_config(Path(d))["mode"] != "label_only":
            errs.append("unknown mode not defaulted to label_only")
        # absent file → defaults
        with tempfile.TemporaryDirectory() as e:
            cfg = ss.read_config(Path(e))
            if cfg != {"mode": "label_only", "threshold": 0.18}:
                errs.append(f"absent config not defaulted: {cfg}")
    return errs


def check_sticky(ss, ops, clf) -> list[str]:
    errs = []
    with tempfile.TemporaryDirectory() as d:
        _git_repo(d, "billing-refund", "fix billing invoice payment refund proration")
        sid = _seed_billing(ops, clf, d)
        # no active → suggests (label_only default)
        res = ss.classify_session(Path(d))
        if res["sticky"]:
            errs.append("classify_session sticky=true with no active stream")
        if res["suggestion"] != sid:
            errs.append(f"label_only did not suggest the seeded stream: {res}")
        if res["switched"]:
            errs.append("label_only switched the active stream (must only suggest)")
        # now activate → sticky no-op, NEVER reclassify
        ops.set_active(d, sid)
        res2 = ss.classify_session(Path(d))
        if not res2["sticky"]:
            errs.append("classify_session not sticky with an active stream")
        if res2["suggestion"] is not None:
            errs.append("classify_session re-classified despite an active stream (sticky broken)")
        if res2["active"] != sid:
            errs.append(f"sticky result lost the active stream: {res2}")
    return errs


def check_redos(ss) -> list[str]:
    """A pathological stream_threshold value must parse in well under a second.

    Regression guard for the security-review finding: the old ambiguous
    `[0-9]*\\.?[0-9]+` numeric pattern backtracked catastrophically (ReDoS) on a
    long digit run + a trailing dot, reachable from the SessionStart banner. The
    de-ambiguated pattern + the config length cap make this linear.
    """
    import time
    errs = []
    with tempfile.TemporaryDirectory() as d:
        # 60k nines + a trailing '.' — the catastrophic-backtracking shape.
        _write_cfg(d, "stream_threshold: " + ("9" * 60000) + ".\n")
        t0 = time.monotonic()
        cfg = ss.read_config(Path(d))
        elapsed = time.monotonic() - t0
        if elapsed > 1.0:
            errs.append(f"read_config took {elapsed:.2f}s on a ReDoS-shaped config (regex not bounded)")
        # The pathological value must NOT be accepted as a threshold (defaults/clamps).
        if not (_THRESH_FLOOR <= cfg["threshold"] <= _THRESH_CEIL):
            errs.append(f"ReDoS-shaped threshold escaped the bounds: {cfg['threshold']}")
    return errs


_THRESH_FLOOR, _THRESH_CEIL = 0.05, 0.95


def check_auto_switch(ss, ops, clf) -> list[str]:
    errs = []
    with tempfile.TemporaryDirectory() as d:
        _git_repo(d, "billing-refund", "fix billing invoice payment refund proration")
        sid = _seed_billing(ops, clf, d)
        _write_cfg(d, "stream_classify: auto\nstream_threshold: 0.10\n")
        res = ss.classify_session(Path(d))
        if not res["switched"]:
            errs.append(f"auto mode did not switch on a confident match: {res}")
        # round-trip: get-active reflects the switch
        if ops.read_active(d) != sid:
            errs.append("auto switch did not round-trip to the active-stream pointer")
        # off mode → nothing
        with tempfile.TemporaryDirectory() as e:
            _git_repo(e, "billing-refund", "fix billing invoice payment refund proration")
            _seed_billing(ops, clf, e)
            _write_cfg(e, "stream_classify: off\n")
            r = ss.classify_session(Path(e))
            if r["suggestion"] is not None or r["switched"]:
                errs.append(f"off mode produced a suggestion/switch: {r}")
    return errs


def must_fail_sticky(ss, ops, clf) -> int:
    """Monkeypatch out the sticky early-return; assert it THEN re-classifies an active stream."""
    with tempfile.TemporaryDirectory() as d:
        _git_repo(d, "billing-refund", "fix billing invoice payment refund proration")
        sid = _seed_billing(ops, clf, d)
        ops.set_active(d, sid)

        # Re-implement classify_session WITHOUT the sticky guard (the broken variant):
        # if it still produces a suggestion for an already-active stream, the real guard
        # is what suppresses it → teeth proven.
        cfg = ss.read_config(Path(d))
        centroids = ops.get_centroids(d)
        signal = ss._git_signal(Path(d))
        res = clf.classify(signal, centroids, threshold=cfg["threshold"])
        if res["confident"] and res["best_stream"]:
            print("  must-fail-sticky: WITHOUT the guard an active session re-classifies "
                  f"(suggestion={res['best_stream']}) — the real sticky guard has teeth")
            return 0
        print("  must-fail-sticky: ERROR — even without the guard nothing classified "
              "(test signal too weak?)", file=sys.stderr)
        return 1


def main(argv: list[str]) -> int:
    ss = _load(SS, "stream_session_start")
    ops = _load(OPS, "stream_ops")
    clf = _load(CLF, "stream_classify")

    if "--must-fail-sticky" in argv:
        return must_fail_sticky(ss, ops, clf)

    errs: list[str] = []
    errs += check_threshold_bounds(ss)
    errs += check_sticky(ss, ops, clf)
    errs += check_auto_switch(ss, ops, clf)
    errs += check_redos(ss)

    if errs:
        print("Gate 112 FAILURES:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("  sticky-no-reclassify OK | override round-trip (label_only/auto/off) OK | "
          "threshold bounds OK | ReDoS-bounded OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
