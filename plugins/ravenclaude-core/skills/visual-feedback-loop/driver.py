#!/usr/bin/env python3
"""Visual-feedback-loop referee — the deterministic "are we done yet?" evaluator.

This is NOT a browser driver. It cannot navigate Chrome, take a screenshot, or
run Lighthouse — that is the agent's job, via the `chrome-devtools-mcp` server
(see SKILL.md). This script is the *referee*: given a config that points at the
evidence the agent has on hand — a layout JSON (delegated to the existing
`pbir-layout-engine` linter), an optional agent-captured `console.json`, and an
optional agent-captured `lighthouse.json` — it merges them into ONE pass/fail
verdict with an objective `next_action`, so a render→see→edit→re-render loop has
a deterministic stopping signal instead of "looks better".

It earns its existence by doing what the layout linter structurally cannot:
fan three independent evidence sources into one verdict. With only a layout JSON
it would be a thin passthrough — so the multi-source merge IS the core.

Contract (stdlib-only, no network, exit-coded — mirrors pbir-layout-engine):
  exit 0  → passed: true OR passed: null (clean, or nothing-to-judge / needs more
            evidence / manual review — absence-of-evidence is NOT a failure)
  exit 1  → passed: false (a determinate gate failed)
  exit 2  → I/O, parse, oversize, or path-rejection (the purity-contract failure)

Security invariants (see the security-review controls baked into SKILL.md):
  - Every input path is resolved through the same rule as the layout linter:
    reject ".." components and any path outside the repo root. Reimplemented
    here (not imported) to keep driver.py free of any coupling to the linter's
    internals; Gate 100 asserts the two guards reject the same traversal input
    (parity), so they cannot silently drift.
  - A byte-size ceiling is enforced BEFORE json.load on every file (a malicious
    page can write an unbounded console.json — bound it).
  - The verdict carries ONLY driver-derived primitives: booleans, counts,
    numeric scores/thresholds, fixed-vocabulary status/next_action strings, and
    driver-authored notes. It NEVER echoes raw console text, Lighthouse audit
    titles, page content, or any other untrusted string — a malicious page can
    write fake "instructions" to the console, and this verdict is read back by
    the model as trusted context. We read numbers out of evidence, never prose.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

DRIVER_VERSION = "0.1.0"
SCHEMA_VERSION = "1.0.0"  # contract version of this driver's JSON envelope

# The layout linter we delegate to (a same-plugin sibling skill). We treat it as
# a CLI with a versioned JSON envelope — subprocess, never import — so its
# internals are not our dependency.
_LINT_RELPATH = os.path.join(
    "plugins", "ravenclaude-core", "skills", "pbir-layout-engine", "lint.py"
)
# The envelope schema version of pbir-layout-engine we built against. If the
# linter bumps its envelope, the assertion below fires loudly instead of
# silently misreading the result.
_EXPECTED_LINT_SCHEMA = "1.0.0"

MAX_EVIDENCE_BYTES = 5 * 1024 * 1024  # 5 MiB ceiling per input file (fail closed)

# Objective default thresholds — the stopping signals. Overridable per-config.
DEFAULTS = {
    "lighthouse_accessibility_min": 90,  # Lighthouse score is 0-100 here
    "lighthouse_performance_min": 80,
    "lighthouse_best_practices_min": 80,
    "max_console_errors": 0,
}


class InputError(Exception):
    """I/O, parse, oversize, or path-rejection failure (exit 2)."""


# ── Repo-root + path safety (parity with pbir-layout-engine lint.py; Gate 100) ──
def _repo_root() -> str:
    """Repo root = four directories up from this file.

    driver.py lives at plugins/ravenclaude-core/skills/visual-feedback-loop/driver.py
    — the same depth as pbir-layout-engine/lint.py, so the identical four-up
    computation yields the identical root. Stdlib only, no subprocess.
    """
    here = os.path.abspath(__file__)
    return os.path.abspath(os.path.join(os.path.dirname(here), "..", "..", "..", ".."))


def _resolve_safe(input_path: str) -> str:
    """Reject '..' components and paths resolving outside the repo root."""
    if ".." in input_path.split(os.sep):
        raise InputError(f"path component '..' is not allowed: {input_path!r}")
    resolved = os.path.abspath(input_path)
    root = _repo_root()
    if os.path.commonpath([resolved, root]) != root:
        raise InputError(f"path resolves outside repo root: {resolved!r}")
    return resolved


def _load_json_bounded(path: str, *, what: str) -> object:
    """Resolve-safe + size-cap + json.load. Never echoes file content on error."""
    resolved = _resolve_safe(path)
    try:
        size = os.path.getsize(resolved)
    except OSError as exc:
        raise InputError(f"cannot stat {what}: {exc}") from exc
    if size > MAX_EVIDENCE_BYTES:
        raise InputError(
            f"{what} exceeds size ceiling ({size} > {MAX_EVIDENCE_BYTES} bytes)"
        )
    try:
        with open(resolved, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        # Deliberately do NOT include the parser's snippet of file content.
        raise InputError(f"cannot parse {what} as JSON") from exc


# ── Gate: layout (delegated to pbir-layout-engine) ───────────────────────────
def _gate_layout(layout_path: str) -> dict:
    """Subprocess the layout linter; map its 0/1/2/3 exit into a gate record.

    The linter's exit codes (verified against lint.py):
      0 → clean         → status pass
      1 → finding       → status fail
      2 → I/O/parse/path on the layout file itself → status error (real failure)
      3 → PBIR enum reference absent/unparseable (e.g. ravenclaude-core installed
          without power-platform) → status degraded (could-not-verify, NOT a fail)
    """
    resolved = _resolve_safe(layout_path)
    lint_py = os.path.join(_repo_root(), _LINT_RELPATH)
    if not os.path.exists(lint_py):
        return {
            "gate": "layout",
            "source_skill": "pbir-layout-engine",
            "status": "degraded",
            "note": "layout-linter-not-found",
        }
    proc = subprocess.run(  # noqa: S603 — fixed argv, resolved-safe path
        [sys.executable, lint_py, "--format", "json", resolved],
        capture_output=True,
        text=True,
    )
    rc = proc.returncode
    record: dict = {
        "gate": "layout",
        "source_skill": "pbir-layout-engine",
        "exit_code": rc,
    }
    # Parse the linter envelope for its summary + schema-version (drift guard).
    envelope = None
    if proc.stdout.strip():
        try:
            envelope = json.loads(proc.stdout)
        except json.JSONDecodeError:
            envelope = None
    if isinstance(envelope, dict):
        src_schema = envelope.get("schema_version")
        record["source_schema_version"] = src_schema
        record["summary"] = envelope.get("summary")
        if src_schema != _EXPECTED_LINT_SCHEMA:
            # Loud, not silent: the contract we built against moved.
            record["status"] = "degraded"
            record["note"] = "layout-linter-schema-mismatch"
            return record
    if rc == 0:
        record["status"] = "pass"
    elif rc == 1:
        record["status"] = "fail"
    elif rc == 3:
        record["status"] = "degraded"
        record["note"] = "layout-enum-reference-unavailable"
    else:  # rc == 2 or any unrecognized nonzero → real input failure on the layout
        record["status"] = "error"
        record["note"] = "layout-input-error"
    return record


# ── Gate: console errors (agent-captured evidence) ───────────────────────────
def _gate_console(data: object, max_errors: int) -> dict:
    """Count entries whose level == 'error'. Never echoes any message text."""
    record: dict = {"gate": "console-errors", "threshold": max_errors}
    if not isinstance(data, dict) or not isinstance(data.get("messages"), list):
        record["status"] = "not_captured"
        record["note"] = "console-evidence-unrecognized-shape"
        return record
    errors = sum(
        1
        for m in data["messages"]
        if isinstance(m, dict) and m.get("level") == "error"
    )
    record["count"] = errors
    record["status"] = "pass" if errors <= max_errors else "fail"
    return record


# ── Gate: lighthouse category scores (agent-captured evidence) ───────────────
_LH_CATEGORIES = (
    ("accessibility", "lighthouse_accessibility_min"),
    ("performance", "lighthouse_performance_min"),
    ("best-practices", "lighthouse_best_practices_min"),
)


def _gate_lighthouse(data: object, thresholds: dict) -> list[dict]:
    """One gate per audited category. Lighthouse native scores are 0-1 floats;
    we surface them as 0-100 integers and compare to the integer threshold."""
    out: list[dict] = []
    categories = data.get("categories") if isinstance(data, dict) else None
    if not isinstance(categories, dict):
        return [
            {
                "gate": "lighthouse",
                "status": "not_captured",
                "note": "lighthouse-evidence-unrecognized-shape",
            }
        ]
    for cat_key, thr_key in _LH_CATEGORIES:
        cat = categories.get(cat_key)
        if not isinstance(cat, dict) or not isinstance(cat.get("score"), (int, float)):
            continue  # category not present in this run — simply not judged
        score = round(float(cat["score"]) * 100)
        threshold = int(thresholds.get(thr_key, DEFAULTS[thr_key]))
        out.append(
            {
                "gate": f"lighthouse-{cat_key}",
                "score": score,
                "threshold": threshold,
                "status": "pass" if score >= threshold else "fail",
            }
        )
    if not out:
        return [
            {
                "gate": "lighthouse",
                "status": "not_captured",
                "note": "lighthouse-no-known-categories",
            }
        ]
    return out


# ── Verdict synthesis ────────────────────────────────────────────────────────
_DETERMINATE = {"pass", "fail", "error"}


def _synthesize(surface: str, gates: list[dict]) -> dict:
    """passed is a pure function of the determinate gates. not_captured /
    degraded gates are excluded (absence-of-evidence is not failure)."""
    determinate = [g for g in gates if g.get("status") in _DETERMINATE]
    any_fail = any(g["status"] in ("fail", "error") for g in determinate)
    has_runtime_evidence = any(
        g["gate"].startswith(("console", "lighthouse"))
        and g.get("status") in _DETERMINATE
        for g in gates
    )
    degraded = [g for g in gates if g.get("status") == "degraded"]

    notes: list[str] = []
    if degraded:
        notes.append("layout-could-not-be-fully-verified")

    if not determinate:
        # Nothing to judge — either no evidence at all, or only degraded/absent.
        return {
            "passed": None,
            "next_action": "manual-visual-review",
            "notes": notes or ["no-determinate-evidence-provided"],
        }

    if any_fail:
        # Name the first actionable failure for next_action.
        next_action = "fix-findings"
        for g in determinate:
            if g["status"] in ("fail", "error"):
                if g["gate"] == "layout":
                    next_action = "fix-layout"
                elif g["gate"] == "console-errors":
                    next_action = "fix-console-errors"
                elif g["gate"].startswith("lighthouse-"):
                    next_action = f"improve-{g['gate'].split('-', 1)[1]}"
                break
        return {"passed": False, "next_action": next_action, "notes": notes}

    # All determinate gates pass.
    if not has_runtime_evidence:
        # Structural checks clean, but the agent hasn't captured what only a
        # rendered browser can show. For BI (structural-first), structural-only
        # is a complete pass; for web, prompt the visual capture.
        if surface in ("pbir", "tableau", "fabric", "bi"):
            return {"passed": True, "next_action": "ship", "notes": notes}
        return {
            "passed": True,
            "next_action": "capture-runtime-evidence",
            "notes": notes + ["structural-checks-clean-capture-screenshot-and-rerun"],
        }
    return {"passed": True, "next_action": "ship", "notes": notes}


def run(config: dict) -> dict:
    surface = config.get("surface", "web")
    if not isinstance(surface, str):
        raise InputError("'surface' must be a string")
    thresholds = config.get("thresholds") or {}
    if not isinstance(thresholds, dict):
        raise InputError("'thresholds' must be an object")

    gates: list[dict] = []

    if config.get("layout"):
        if not isinstance(config["layout"], str):
            raise InputError("'layout' must be a path string")
        gates.append(_gate_layout(config["layout"]))

    if config.get("console"):
        if not isinstance(config["console"], str):
            raise InputError("'console' must be a path string")
        data = _load_json_bounded(config["console"], what="console evidence")
        max_errors = int(thresholds.get("max_console_errors", DEFAULTS["max_console_errors"]))
        gates.append(_gate_console(data, max_errors))

    if config.get("lighthouse"):
        if not isinstance(config["lighthouse"], str):
            raise InputError("'lighthouse' must be a path string")
        data = _load_json_bounded(config["lighthouse"], what="lighthouse evidence")
        gates.extend(_gate_lighthouse(data, thresholds))

    verdict = _synthesize(surface, gates)
    return {
        "schema_version": SCHEMA_VERSION,
        "driver_version": DRIVER_VERSION,
        "surface": surface,
        "passed": verdict["passed"],
        "gates": gates,
        "next_action": verdict["next_action"],
        "notes": verdict["notes"],
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] in ("--version", "-V"):
        print(f"driver.py {DRIVER_VERSION} (envelope {SCHEMA_VERSION})")
        return 0
    if len(args) != 1:
        print("usage: driver.py <config.json>", file=sys.stderr)
        return 2
    try:
        config = _load_json_bounded(args[0], what="config")
        if not isinstance(config, dict):
            raise InputError("config root must be a JSON object")
        envelope = run(config)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(envelope, indent=2))
    # passed False → 1; passed True or None → 0 (None is "needs more / manual",
    # not a failure — an absent browser tool must never read as a failed gate).
    return 1 if envelope["passed"] is False else 0


if __name__ == "__main__":
    sys.exit(main())
