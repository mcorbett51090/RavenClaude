#!/usr/bin/env python3
"""check-parallelism-posture.py — Gate 223.

Proves the two engines behind "parallelism defaults to MAXIMUM" actually
discriminate, rather than merely existing:

  A. conserve-tokens.py — all THREE triggers, each with a POSITIVE CONTROL in
     the opposite direction, plus the documented precedence.
  B. parallelism-detector.py — a serial dispatch pattern and a parallel one must
     produce DIFFERENT numbers.

⛔ EVERY assertion here is paired. A "conserve engages on the phrase" check that
is not paired with "and does NOT engage on an unrelated prompt" is satisfied by
an engine that engages on everything; a "pressure engages at 88%" check without
"and not at 50%" is satisfied by one that always engages. The pairs are what
make this a measurement instead of a smoke test — the same reason
check-dom-budget derives its must-fail bar from the live count instead of a
literal.

Teeth (each `--must-fail-*` mutant neuters ONE mechanism and EXITS 0 only when
the suite reddens, so a green gate cannot come from an assertion that never
fires):
  --must-fail-precedence  RELEASE_PHRASES emptied  -> the release phrase can no
                          longer beat a posture switch.
  --must-fail-window      BATCH_WINDOW_S = 0       -> a parallel burst is
                          miscounted as N serial singles.
  --must-fail-pressure    the auto threshold is ignored -> pressure never fires.

Usage:
  python3 scripts/check-parallelism-posture.py [--must-fail-<name>]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "plugins" / "ravenclaude-core" / "scripts"


def load(filename: str, modname: str):
    target = SCRIPTS / filename
    if not target.is_file():
        raise SystemExit(f"missing engine: {target}")
    spec = importlib.util.spec_from_file_location(modname, target)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load: {target}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _posture(root: Path, body: str) -> None:
    (root / ".ravenclaude").mkdir(parents=True, exist_ok=True)
    (root / ".ravenclaude" / "comfort-posture.yaml").write_text(body, encoding="utf-8")


def _pressure_fixture(meter, root: Path, home: Path, sid: str, used: int, window: int) -> dict:
    """Build a real context-usage-meter session dir. The meter is NOT stubbed —
    a stubbed meter would prove only that this file can fake a number."""
    sd = home / "sessions" / meter.encode_cwd(str(root)) / sid
    sd.mkdir(parents=True, exist_ok=True)
    (sd / "signals.json").write_text(json.dumps({"contextWindowTokens": window}), encoding="utf-8")
    (sd / "updates.jsonl").write_text(
        json.dumps({"params": {"_meta": {"totalTokens": used}}}) + "\n", encoding="utf-8"
    )
    return {"session_id": sid, "cwd": str(root)}


def run_checks(ct, pd, meter) -> list[tuple[str, bool]]:
    res: list[tuple[str, bool]] = []

    def ck(name: str, ok: bool) -> None:
        res.append((name, bool(ok)))

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "proj"
        home = Path(td) / "grokhome"
        root.mkdir(parents=True)
        home.mkdir(parents=True)
        os.environ["GROK_HOME"] = str(home)

        # ── A0. The DEFAULT. An absent parallelism block must read as maximum.
        _posture(root, "schema_version: 5\n")
        p = ct.read_posture(root)
        ck("default: absent parallelism block reads as max", p["parallelism"] == "max")
        ck("default: conserve is off", p["conserve_tokens"] is False)
        ck("default: auto_pct is 80", p["auto_pct"] == 80)

        # explicit forms are unchanged — the migration claim, asserted not assumed
        _posture(root, "schema_version: 5\nparallelism:\n  enabled: false\n  max_workers: 4\n")
        ck("explicit enabled:false still reads sequential",
           ct.read_posture(root)["parallelism"] == "sequential")
        _posture(root, "schema_version: 5\nparallelism:\n  enabled: true\n  max_workers: 3\n")
        p3 = ct.read_posture(root)
        ck("explicit max_workers:N still reads capped", p3["parallelism"] == "capped")
        ck("explicit max_workers:N keeps N", p3["max_workers"] == 3)
        _posture(root, "schema_version: 5\nparallelism: off\n")
        ck("scalar `parallelism: off` reads sequential",
           ct.read_posture(root)["parallelism"] == "sequential")

        # ── A1. Trigger 2 (posture switch), both directions.
        _posture(root, "schema_version: 5\nconserve_tokens: true\n")
        r = ct.resolve({}, root, "t-posture-on", None)
        ck("trigger2: posture switch engages", r["engaged"] is True and r["source"] == "posture")
        _posture(root, "schema_version: 5\n")
        r = ct.resolve({}, root, "t-posture-off", None)
        ck("trigger2 control: absent switch does NOT engage", r["engaged"] is False)

        # ── A2. Trigger 1 (prompt phrase), both directions + stickiness.
        _posture(root, "schema_version: 5\n")
        r = ct.resolve({}, root, "t-phrase", "please conserve tokens here")
        ck("trigger1: phrase engages", r["engaged"] is True and r["source"] == "phrase")
        r = ct.resolve({}, root, "t-phrase", "now do the next unrelated thing")
        ck("trigger1: phrase is sticky across turns", r["engaged"] is True)
        r = ct.resolve({}, root, "t-phrase-neg", "refactor the token parser and check the budget")
        ck("trigger1 control: an unrelated prompt does NOT engage", r["engaged"] is False)

        # ── A3. PRECEDENCE: the release phrase beats a posture switch set true.
        #        This is the one ordering that, if wrong, leaves a session with
        #        NO exit from conserve mode short of editing a config file.
        _posture(root, "schema_version: 5\nconserve_tokens: true\n")
        r = ct.resolve({}, root, "t-prec", "go maximum parallelism please")
        ck("precedence: release phrase beats posture:true",
           r["engaged"] is False and r["source"] == "phrase-release")
        r = ct.resolve({}, root, "t-prec", "carry on")
        ck("precedence: the release is sticky too", r["engaged"] is False)

        # ── A4. Trigger 3 (context pressure), both directions + the 0 disable.
        _posture(root, "schema_version: 5\n")
        pay = _pressure_fixture(meter, root, home, "hot", 880_000, 1_000_000)
        r = ct.resolve(pay, root, "t-hot", "do the thing")
        ck("trigger3: 88% of window engages",
           r["engaged"] is True and r["source"] == "context-pressure")
        ck("trigger3: percent is really measured (not fabricated)", r["percent"] == 88.0)
        pay = _pressure_fixture(meter, root, home, "cool", 500_000, 1_000_000)
        r = ct.resolve(pay, root, "t-cool", "do the thing")
        ck("trigger3 control: 50% of window does NOT engage", r["engaged"] is False)
        _posture(root, "schema_version: 5\nconserve_tokens_auto_pct: 0\n")
        pay = _pressure_fixture(meter, root, home, "hot", 880_000, 1_000_000)
        r = ct.resolve(pay, root, "t-hot-disabled", "do the thing")
        ck("trigger3: auto_pct 0 disables the automatic trigger", r["engaged"] is False)
        # An UNMEASURABLE window must fail toward silent, never toward 0%.
        _posture(root, "schema_version: 5\n")
        r = ct.resolve({"session_id": "nowhere", "cwd": str(root)}, root, "t-blind", "go")
        ck("trigger3: an unmeasurable window is None, not 0%", r["percent"] is None)
        ck("trigger3: an unmeasurable window does NOT engage", r["engaged"] is False)

        # ── B. The detector must produce DIFFERENT numbers for serial vs parallel.
        droot = Path(td) / "dproj"
        (droot / ".ravenclaude").mkdir(parents=True)
        signals = 0
        for t in (1000, 1030, 1060, 1090):          # 4 singles, 30s apart
            if pd.observe(droot, "ser", t):
                signals += 1
        ser = pd.summarize(droot, "ser")
        for t in (2000, 2001, 2002, 2003, 2030, 2031, 2032, 2033):  # 2 bursts of 4
            pd.observe(droot, "par", t)
        par = pd.summarize(droot, "par")

        ck("detector: serial run counts 4 agents", ser["agents"] == 4)
        ck("detector: serial run is 4 single batches", ser["batches"] == 4 and ser["singles"] == 4)
        ck("detector: serial ratio is 1.0", ser["serial_ratio"] == 1.0)
        ck("detector: serial run emits a signal", signals >= 1)
        ck("detector: signals are capped", signals <= pd.MAX_SIGNALS)
        ck("detector: parallel run counts 8 agents", par["agents"] == 8)
        ck("detector: parallel run is 2 batches, 0 singles",
           par["batches"] == 2 and par["singles"] == 0)
        ck("detector: parallel ratio is 0.0", par["serial_ratio"] == 0.0)
        ck("detector: parallel widest batch is 4", par["max_batch"] == 4)
        # THE discriminating assertion: the two patterns must not look alike.
        ck("detector: serial and parallel ratios DIFFER",
           ser["serial_ratio"] != par["serial_ratio"])
        # An empty project reports "no batches", never a fabricated ratio.
        empty = Path(td) / "eproj"
        (empty / ".ravenclaude").mkdir(parents=True)
        e = pd.summarize(empty)
        ck("detector: no dispatches -> ratio None (not 0, not 1)", e["serial_ratio"] is None)
        ck("detector: output states its own limits", "not 'perfectly parallel'" in e["limits"])

    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Gate 223 — parallelism posture + detector")
    ap.add_argument("--must-fail-precedence", action="store_true")
    ap.add_argument("--must-fail-window", action="store_true")
    ap.add_argument("--must-fail-pressure", action="store_true")
    args = ap.parse_args(argv)

    ct = load("conserve-tokens.py", "_g223_conserve")
    pd = load("parallelism-detector.py", "_g223_detector")
    meter = load("context-usage-meter.py", "_g223_meter")

    mutant = None
    if args.must_fail_precedence:
        mutant = "precedence"
        ct.RELEASE_PHRASES = ()
    elif args.must_fail_window:
        mutant = "window"
        pd.BATCH_WINDOW_S = 0
    elif args.must_fail_pressure:
        mutant = "pressure"
        # Ignore the configured threshold entirely: pressure can never fire.
        ct.CONSERVE_AUTO_PCT_DEFAULT = 0

        _orig = ct.read_posture

        def _no_threshold(root):
            p = _orig(root)
            p["auto_pct"] = 0
            return p

        ct.read_posture = _no_threshold

    results = run_checks(ct, pd, meter)
    failed = [n for n, ok in results if not ok]

    if mutant:
        # Teeth: the mutant must REDDEN the suite. Exit 0 only when it does.
        if failed:
            print(f"must-fail-{mutant}: OK — {len(failed)} assertion(s) reddened:")
            for n in failed[:6]:
                print(f"    - {n}")
            return 0
        print(f"must-fail-{mutant}: NO ASSERTION FIRED — the gate is toothless here", file=sys.stderr)
        return 1

    for n in failed:
        print(f"  x {n}", file=sys.stderr)
    if failed:
        print(f"parallelism posture: {len(failed)}/{len(results)} FAILED", file=sys.stderr)
        return 1
    print(f"parallelism posture: {len(results)} assertions pass "
          "(3 conserve triggers + precedence, each with a control; detector discriminates)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
