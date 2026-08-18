#!/usr/bin/env python3
"""Gate 220 — form_metrics.py numeric correctness + the SPC round-trip, EXECUTED.

`plugins/forms-engineering/scripts/form_metrics.py` is the only executable the
forms plugin ships, and it carries the plugin's only claim with no prior art:
that a form's completion series can be handed to statistical process control. A
claim with no literature has to be mechanically testable or it is just prose, so
this gate RUNS the script rather than reading it.

Four things are asserted, each against a committed fixture with HAND-COMPUTED
expectations (25 sessions: 20 completers whose durations repeat 60/62/58/64/56
four times — mean 60.00, median 60.00; 5 abandoned; email errors on 5 of 25 =
20.00%; phone on 2 of 25 = 8.00%; last-touch phone 3/5 = 60.00%, message 2/5 =
40.00%). The expectations are auditable on paper, so the gate is not re-running
the implementation against itself.

  (i)   ROUND-TRIP. `lss_calc.py imr --values "$(form_metrics.py --emit-imr F)"`
        exits 0 and its stdout carries both UCL and LCL.
        ⛔ COMMAND SUBSTITUTION, NOT A PIPE. `lss_calc.py imr` declares
        `--values` required and has no stdin path anywhere in the module; the
        piped form discards the left side and exits 2. This was measured.
  (ii)  STREAM CONTRACT. `--emit-imr` stdout is NUMERIC-ONLY.
        ⛔ Written as a COUNT of violating lines, never as `grep -q -v`. On this
        host `grep -v P` returns rc 0 where `grep -qv P` returns rc 1 — adding
        `-q` inverts the answer TOWARD CLEAN, and a first draft of this
        assertion passed a deliberately-bad fixture because of it.
  (iii) THE MARKER IS PRINTED. The verbatim novel-synthesis marker appears in
        captured STDERR of a plain run AND of `--emit-imr`.
        ⛔ This assertion lives here, not in Gate 221, because only an EXECUTION
        assertion proves a label reaches a user. A file-level string check is
        satisfied identically by a marker sitting in a docstring, a comment, or
        an unexercised branch — the recorded "a grep is satisfied by the thing
        being described" defect.
  (iv)  NEGATIVE CONTROLS. A malformed CSV, a CSV whose completions outnumber
        its starts, and a series below the 20-observation charting floor each
        exit non-zero.
        ⛔ The floor matters: `lss_calc.py imr` accepts n >= 2, so without it
        this gate could certify "valid control limits" on a two-point series —
        exactly what the plugin's own best-practice rule forbids. A gate must
        not bless what the plugin prohibits.

Exit codes: 0 = clean; 2 = a finding (fail-closed). Exit 1 is never used.

Usage:
    python3 scripts/check-form-metrics.py
    python3 scripts/check-form-metrics.py --self-test
    python3 scripts/check-form-metrics.py --must-fail
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METRICS = ROOT / "plugins" / "forms-engineering" / "scripts" / "form_metrics.py"
LSS = ROOT / "plugins" / "process-improvement" / "scripts" / "lss_calc.py"
FIXTURES = ROOT / "tests" / "fixtures" / "forms-engineering" / "form-metrics"
SAMPLE = FIXTURES / "sample-sessions.csv"

MARKER = (
    "[NOVEL SYNTHESIS — applying SPC to form telemetry is our synthesis, not "
    "established practice. We found no published work joining web-form telemetry to "
    "SPC/DMAIC (open-web search, 2026-08-17); the negative finding is bounded by that "
    "method and is not proof of universal absence.]"
)

MIN_OBSERVATIONS = 20

# Hand-computed from the committed fixture. Each is a literal that must appear in
# the plain run's stdout.
EXPECTED_STDOUT = (
    "starts: 25",
    "submits: 20",
    "completion rate: 80.00%",
    "abandonment rate: 20.00%",
    "median: 60.00 s",
    "mean: 60.00 s",
    "email: 20.00%",
    "phone: 8.00%",
    "message: 40.00%",
    "phone: 60.00%",
    "form starts = sessions in which any field received a FIRST INTERACTION",
    "PROXY — last field touched is NOT the field that caused the exit",
)

# A line is conforming when it holds nothing but digits, signs, separators and
# whitespace. Mirrors the shell form the plan binds:
#   bad=$(printf '%s\n' "$out" | grep -c -v -E '^[0-9eE+.,[:space:]-]*$'); [ "$bad" -eq 0 ]
NUMERIC_LINE_RE = re.compile(r"^[0-9eE+.,\s-]*$")

NEGATIVE_CONTROLS = (
    ("malformed-missing-column.csv", ()),
    ("completions-exceed-starts.csv", ()),
    ("below-charting-floor.csv", ("--emit-imr",)),
)


def _run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    return proc.returncode, proc.stdout, proc.stderr


def assess(
    metrics_script: Path,
    expected_stdout: tuple[str, ...] = EXPECTED_STDOUT,
) -> list[str]:
    """Run every assertion against `metrics_script`. Returns a list of failures."""
    problems: list[str] = []
    py = sys.executable or "python3"

    if not metrics_script.is_file():
        return [f"{metrics_script} is missing"]
    if not LSS.is_file():
        return [f"{LSS} is missing — the SPC seam has no far side"]
    if not SAMPLE.is_file():
        return [f"{SAMPLE} is missing — the fixture is the gate's only ground truth"]

    # ── plain run: hand-computed values + marker on stderr ───────────────────
    rc, out, err = _run([py, str(metrics_script), str(SAMPLE)])
    if rc != 0:
        problems.append(f"plain run exited {rc} (stderr: {err.strip()[:200]})")
    for literal in expected_stdout:
        if literal not in out:
            problems.append(f"plain run stdout is missing the hand-computed value {literal!r}")
    if MARKER not in err:
        problems.append("(iii) the verbatim novel-synthesis marker is ABSENT from a plain run's stderr")
    if MARKER in out:
        problems.append("(iii) the marker reached STDOUT on a plain run — it belongs on stderr only")

    # ── --emit-imr: numeric-only stdout, marker still on stderr ──────────────
    rc, imr_out, imr_err = _run([py, str(metrics_script), "--emit-imr", str(SAMPLE)])
    if rc != 0:
        problems.append(f"--emit-imr exited {rc} (stderr: {imr_err.strip()[:200]})")
    if MARKER not in imr_err:
        problems.append("(iii) the marker is ABSENT from --emit-imr stderr")
    # (ii) COUNT of violating lines — never `grep -q -v`.
    bad = sum(1 for line in imr_out.splitlines() if not NUMERIC_LINE_RE.match(line))
    if bad != 0:
        problems.append(f"(ii) --emit-imr stdout has {bad} non-numeric line(s) — the pipe is poisoned")
    values = [v for v in imr_out.split() if v]
    if len(values) < MIN_OBSERVATIONS:
        problems.append(
            f"(iv) the fixture yields {len(values)} observations; the charting floor is "
            f"{MIN_OBSERVATIONS} and the gate must not certify limits below it"
        )

    # ── (i) the round-trip, EXECUTED, by command substitution ────────────────
    if bad == 0 and values:
        rc, rt_out, rt_err = _run([py, str(LSS), "imr", "--values", " ".join(values)])
        if rc != 0:
            problems.append(f"(i) round-trip into lss_calc.py imr exited {rc}: {rt_err.strip()[:200]}")
        if "UCL" not in rt_out or "LCL" not in rt_out:
            problems.append("(i) round-trip stdout carries no UCL/LCL — no control limits were produced")
    else:
        problems.append("(i) round-trip not attempted: --emit-imr stdout was unusable")

    # ── (iv) negative controls ───────────────────────────────────────────────
    for name, extra in NEGATIVE_CONTROLS:
        fixture = FIXTURES / name
        if not fixture.is_file():
            problems.append(f"negative-control fixture missing: {name}")
            continue
        rc, _, _ = _run([py, str(metrics_script), *extra, str(fixture)])
        if rc == 0:
            problems.append(f"(iv) negative control {name} exited 0 — it must fail closed")
    return problems


# ── mocks used by --self-test ────────────────────────────────────────────────

_GOOD_MOCK = """import sys
vals = [str(v) for v in range(60, 80)]
sys.stderr.write({marker!r} + "\\n")
if "--emit-imr" in sys.argv:
    sys.stdout.write("\\n".join(vals) + "\\n")
else:
    sys.stdout.write("starts: 25\\n")
"""

# The measured violation: the marker on STDOUT. It poisons the round-trip and
# leaves stderr empty, so assertions (i), (ii) and (iii) must all redden.
_BAD_MOCK = """import sys
vals = [str(v) for v in range(60, 80)]
sys.stdout.write({marker!r} + "\\n")
if "--emit-imr" in sys.argv:
    sys.stdout.write("\\n".join(vals) + "\\n")
else:
    sys.stdout.write("starts: 25\\n")
"""


def _mock_stream_assertions(script: Path) -> dict[str, bool]:
    """Run only the three stream-contract assertions against a mock."""
    py = sys.executable or "python3"
    _, out, err = _run([py, str(script), "--emit-imr", str(SAMPLE)])
    marker_on_stderr = MARKER in err
    bad = sum(1 for line in out.splitlines() if not NUMERIC_LINE_RE.match(line))
    numeric_only = bad == 0
    values = [v for v in out.split() if v]
    roundtrip_ok = False
    if numeric_only and values:
        rc, rt_out, _ = _run([py, str(LSS), "imr", "--values", " ".join(values)])
        roundtrip_ok = rc == 0 and "UCL" in rt_out and "LCL" in rt_out
    return {"i": roundtrip_ok, "ii": numeric_only, "iii": marker_on_stderr}


def self_test() -> int:
    problems: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        good = Path(td) / "good_mock.py"
        bad = Path(td) / "bad_mock.py"
        good.write_text(_GOOD_MOCK.format(marker=MARKER), encoding="utf-8")
        bad.write_text(_BAD_MOCK.format(marker=MARKER), encoding="utf-8")

        g = _mock_stream_assertions(good)
        b = _mock_stream_assertions(bad)
        for key in ("i", "ii", "iii"):
            if not g[key]:
                problems.append(f"assertion ({key}) FAILED on the contract-honouring mock")
            if b[key]:
                problems.append(
                    f"assertion ({key}) PASSED on the marker-to-stdout mock — it asserts nothing"
                )

    # The hand-computed comparator must itself be able to go red.
    mutated = tuple(["starts: 26"] + [e for e in EXPECTED_STDOUT if e != "starts: 25"])
    if not assess(METRICS, mutated):
        problems.append(
            "the hand-computed comparator did not redden on a deliberately wrong expected value"
        )

    if problems:
        print("✗ check-form-metrics self-test FAILED:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2
    print("✓ self-test: (i)(ii)(iii) pass the good mock and FAIL the marker-to-stdout mock")
    return 0


def must_fail() -> int:
    """Plant a wrong expected value; exit 2 when the mismatch IS caught."""
    mutated = tuple(["completion rate: 81.00%"] + [
        e for e in EXPECTED_STDOUT if e != "completion rate: 80.00%"
    ])
    problems = assess(METRICS, mutated)
    if problems:
        print(f"✓ must-fail: a planted wrong expected value IS caught ({len(problems)} finding(s))")
        return 2
    print("✗ must-fail: the planted wrong expected value was NOT caught — the gate has no teeth")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.must_fail:
        return must_fail()

    problems = assess(METRICS)
    if problems:
        print(f"✗ form_metrics: {len(problems)} finding(s)", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2
    print(
        "✓ form_metrics: hand-checked values match, stream contract holds, "
        "the lss_calc.py I-MR round-trip EXECUTES, negative controls fail closed"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
