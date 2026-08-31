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
  - The verdict carries driver-derived primitives (booleans, counts, numeric
    scores/thresholds, fixed-vocabulary status/next_action strings, driver-authored
    notes) plus, for the parity gate, allowlist-sanitized schema-vocabulary tokens
    from the input visual.json — specifically visualType, queryState role names,
    and objects keys, each filtered through `_safe_token`/`_safe_tokens` (`\\A…\\Z`
    + fullmatch over `[A-Za-z0-9_-]{1,40}`) before output. It NEVER echoes raw
    console text, Lighthouse audit titles, JSON value content, or page prose — a
    malicious page can write fake "instructions" to the console, and this verdict
    is read back by the model as trusted context. We read numbers out of runtime
    evidence; from visual.json we read only schema tokens, filtered.
"""

from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys

DRIVER_VERSION = "0.2.0"
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
    "ssim_min": 0.90,  # SSIM is 0-1; a candidate must be >= this to verify visual fidelity
    "design_ratio_tolerance": 0.05,  # type-scale ratio match tolerance (design-schema floor)
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
    """Reject '..' components and paths resolving outside the repo root.

    Uses os.path.realpath (NOT abspath) on BOTH the input and the root — abspath
    does not resolve symlinks, so an in-repo path that is a SYMLINK to a file
    outside the repo passes a commonpath check on its own (symlink) path while
    open() follows the link out of the sandbox. realpath collapses the link first,
    so the containment check sees the true target. This restores the sandbox parity
    with pbir-layout-engine/lint.py that driver.py's docstring claims (2026-08 review;
    Gate 100 gained a symlink-escape fixture to enforce the parity)."""
    if ".." in input_path.split(os.sep):
        raise InputError(f"path component '..' is not allowed: {input_path!r}")
    resolved = os.path.realpath(input_path)
    root = os.path.realpath(_repo_root())
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
        raise InputError(f"{what} exceeds size ceiling ({size} > {MAX_EVIDENCE_BYTES} bytes)")
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
    errors = sum(1 for m in data["messages"] if isinstance(m, dict) and m.get("level") == "error")
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
        if not isinstance(cat, dict):
            continue  # category not present in this run — simply not judged
        raw = cat.get("score")
        # Domain clamp (parity with the SSIM gate): a Lighthouse category score is a
        # native 0-1 float. Reject bool, non-finite (NaN/inf), and out-of-domain — a
        # hostile page can write a 5.0 that rescales to 500 and passes every threshold.
        # Such a value is NOT judged (skipped), never a silent pass. The prior
        # isinstance-only guard let 5.0/NaN through — this closes that inherited hole.
        if (
            not isinstance(raw, (int, float))
            or isinstance(raw, bool)
            or not math.isfinite(raw)
            or not (0.0 <= float(raw) <= 1.0)
        ):
            continue
        score = round(float(raw) * 100)
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


# ── Gate: structural parity vs. a known-good exemplar ────────────────────────
# Honest framing (per the adversarial review of this gate): this is a structural
# DIFF SURFACER against a chosen exemplar, NOT a render oracle. It flags where the
# candidate's render skeleton DIVERGES from a working exemplar of the same kind in
# the render-RISK direction: the candidate is MISSING something the exemplar has —
# a query role (Values/Data/Indicator), an objects key (e.g. a `card` that dropped
# `labels` and substituted `calloutValue` → blank), or a per-item `$id` the
# exemplar carries (the `cardVisual` blank cause). It is ASYMMETRIC on purpose:
# the candidate ADDING a benign extra (a cosmetic object key, an optional role)
# is NOT a fail — only what it LOSES relative to the exemplar is render-risk. It
# can only be as good as the exemplar, so the exemplar is validated first
# (non-degenerate, not the candidate itself). PBIR `visual.json` shape; any other
# shape → not_captured (the technique generalizes; this differ is PBIR-first).
_TOKEN_RE = re.compile(r"\A[A-Za-z0-9_-]{1,40}\Z")


def _safe_token(s: object) -> str:
    """A schema-vocabulary token (role/object-key/visualType) is echo-safe only
    when it matches the closed allowlist charset — otherwise it could be an
    attacker-authored string in a visual.json, so we replace it with a fixed
    placeholder (the verdict is read back by the model as trusted context).
    `\\A…\\Z` + fullmatch (not `^…$` + match) so a trailing newline can't slip a
    line-injection token through — `$`/`match` accept a string ending in `\\n`."""
    return s if isinstance(s, str) and _TOKEN_RE.fullmatch(s) else "<non-standard>"


def _safe_tokens(items) -> list[str]:
    return sorted(_safe_token(x) for x in items)


def _pbir_skeleton(visual_obj: object) -> dict | None:
    """Render-relevant skeleton of a PBIR visual.json: visualType, the set of
    query role names, the set of `objects` keys, and which keys are FULLY `$id`-ed
    (every item carries `$id` — the cardVisual schema requires it on each item, so
    a key with one item missing `$id` is NOT fully-ed and will be flagged). None
    if it is not a PBIR-visual shape (no .visual.visualType)."""
    if not isinstance(visual_obj, dict):
        return None
    v = visual_obj.get("visual")
    if not isinstance(v, dict) or not isinstance(v.get("visualType"), str):
        return None
    roles: set[str] = set()
    q = v.get("query")
    if isinstance(q, dict) and isinstance(q.get("queryState"), dict):
        roles = {r for r in q["queryState"].keys() if isinstance(r, str)}
    object_keys: set[str] = set()
    id_keys: set[str] = set()
    objs = v.get("objects")
    if isinstance(objs, dict):
        for k, items in objs.items():
            if not isinstance(k, str):
                continue
            object_keys.add(k)
            # Fully-$id'd iff the key has items AND every item carries `$id`
            # (the schema requires it per item — `all`, never `any`).
            if (
                isinstance(items, list)
                and items
                and all(isinstance(it, dict) and "$id" in it for it in items)
            ):
                id_keys.add(k)
    return {
        "visualType": v["visualType"],
        "roles": roles,
        "object_keys": object_keys,
        "id_keys": id_keys,
    }


def _gate_parity(candidate_path: str, reference_path: str) -> dict:
    """Diff the candidate visual's skeleton against a confirmed-working reference
    of the SAME kind. FAIL on render-RISK divergence — the candidate is MISSING a
    query role, an objects key, or a per-item `$id` that the exemplar carries.
    Benign additions on the candidate (extra cosmetic key / optional role) are NOT
    a fail. A different visualType, a non-PBIR shape, the candidate AS its own
    reference, or a degenerate exemplar (no query role) → `not_captured` (note),
    never a false fail."""
    record: dict = {"gate": "parity", "source_skill": "visual-feedback-loop"}
    # Self-referential guard: a file can't be its own confirmed-working exemplar.
    if os.path.realpath(candidate_path) == os.path.realpath(reference_path):
        record["status"] = "not_captured"
        record["note"] = "parity-reference-is-candidate"
        return record
    cand = _load_json_bounded(candidate_path, what="parity candidate")
    ref = _load_json_bounded(reference_path, what="parity reference")
    cs = _pbir_skeleton(cand)
    rs = _pbir_skeleton(ref)
    if cs is None or rs is None:
        record["status"] = "not_captured"
        record["note"] = (
            "parity-candidate-non-pbir-shape" if cs is None else "parity-reference-non-pbir-shape"
        )
        return record
    if cs["visualType"] != rs["visualType"]:
        record["status"] = "not_captured"
        record["note"] = "parity-visualtype-mismatch-not-comparable"
        record["candidate_visual_type"] = _safe_token(cs["visualType"])
        record["reference_visual_type"] = _safe_token(rs["visualType"])
        return record
    # Exemplar validation: a reference with no query role has no data binding and
    # cannot be a "confirmed-working" exemplar — refuse to launder it into a pass.
    if not rs["roles"]:
        record["status"] = "not_captured"
        record["note"] = "parity-reference-not-a-valid-exemplar"
        return record

    record["visual_type"] = _safe_token(cs["visualType"])
    deltas: list[dict] = []
    # Render-risk is what the candidate is MISSING relative to the exemplar
    # (asymmetric — an extra role/key the candidate adds is benign, not a fail).
    missing_roles = rs["roles"] - cs["roles"]
    if missing_roles:  # e.g. a card missing Values, a kpi missing Indicator → blank
        deltas.append(
            {
                "dimension": "missing-query-role",
                "candidate": _safe_tokens(cs["roles"]),
                "reference": _safe_tokens(rs["roles"]),
            }
        )
    missing_keys = rs["object_keys"] - cs["object_keys"]
    if missing_keys:  # e.g. a card that dropped `labels` (substituting calloutValue)
        deltas.append(
            {
                "dimension": "missing-object-key",
                "missing": _safe_tokens(missing_keys),
                "reference": _safe_tokens(rs["object_keys"]),
            }
        )
    # $id drift, directional: the exemplar carries a fully-$id'd key but the
    # candidate's same key is not fully-$id'd (a partial/absent $id → blank).
    id_drift = [
        k
        for k in (cs["object_keys"] & rs["object_keys"])
        if (k in rs["id_keys"]) and (k not in cs["id_keys"])
    ]
    if id_drift:  # cardVisual object items missing the required $id
        deltas.append({"dimension": "id-presence", "object_keys": _safe_tokens(id_drift)})

    record["status"] = "fail" if deltas else "pass"
    if deltas:
        record["deltas"] = deltas
    # Advisory only (not a fail): keys the candidate ADDS beyond the exemplar
    # (cosmetic/benign) — surfaced for diagnostics, never gated on.
    extra = cs["object_keys"] - rs["object_keys"]
    if extra:
        record["advisory_candidate_only_object_keys"] = _safe_tokens(extra)
    return record


# ── Gate: SSIM visual-fidelity (agent-captured browser evidence) ─────────────
def _ssim_in_domain(x: float) -> bool:
    """A valid SSIM score is a finite real number in [0,1]. NaN/inf/∉[0,1] → False.
    SECURITY: the score is computed OUT-OF-PAGE over harness-controlled screenshot
    buffers (never `page.evaluate` in the measured page) and read here as a number
    only — this clamp is what stops a page-controllable value (a 5.0 that would
    rescale to a fake pass, a NaN that dodges the comparison) from becoming fidelity."""
    return math.isfinite(x) and 0.0 <= float(x) <= 1.0


def _gate_ssim(data: object, thresholds: dict) -> dict:
    """Ingest an agent-captured {"ssim_score": <float>} (the lighthouse-evidence
    pattern). `pass` iff score >= τ. An absent/non-numeric field is genuine absence
    → `not_captured`. A captured-but-out-of-domain value (NaN/inf/∉[0,1]) is
    corrupt/hostile evidence → determinate `error` (the loop must fix its capture),
    NEVER a pass. Never echoes page text — reads the number only."""
    record: dict = {"gate": "compare-ssim"}
    score = data.get("ssim_score") if isinstance(data, dict) else None
    if not isinstance(score, (int, float)) or isinstance(score, bool):
        record["status"] = "not_captured"
        record["note"] = "ssim-evidence-unrecognized-shape"
        return record
    if not _ssim_in_domain(score):
        record["status"] = "error"
        record["note"] = "ssim-score-out-of-domain"
        return record
    threshold = float(thresholds.get("ssim_min", DEFAULTS["ssim_min"]))
    record["score"] = float(score)
    record["threshold"] = threshold
    record["status"] = "pass" if float(score) >= threshold else "fail"
    return record


# ── Gate: design-schema structural floor (offline "same design system?" sanity) ─
# HONEST FRAMING: this is NOT fidelity. It is an offline, per-dimension ASYMMETRIC
# diff over two design-schema.json instances — "does the candidate declare the same
# design system as the reference?" It fires on what the candidate is MISSING relative
# to the reference (a different base unit, a type ratio outside tolerance, fewer
# elevation levels, missing breakpoints, missing components) and passes benign
# additions (asymmetric, like the parity gate). Visual fidelity is the SSIM gate's job.
def _design_skeleton(obj: object) -> dict | None:
    """Comparable dimensions of a design-schema.json. None when it is not a
    design-schema shape (no `spacing`/`type_scale` object)."""
    if not isinstance(obj, dict):
        return None
    spacing = obj.get("spacing")
    type_scale = obj.get("type_scale")
    if not isinstance(spacing, dict) or not isinstance(type_scale, dict):
        return None
    grid = obj.get("grid") if isinstance(obj.get("grid"), dict) else {}
    elevation = obj.get("elevation") if isinstance(obj.get("elevation"), dict) else {}
    components = obj.get("components") if isinstance(obj.get("components"), list) else []

    def _num_or_none(v: object) -> float | None:
        return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None

    shadows = elevation.get("shadows")
    breakpoints = grid.get("breakpoints")
    return {
        "base_unit": _num_or_none(spacing.get("base_unit")),
        "ratio": _num_or_none(type_scale.get("ratio")),
        "shadow_count": len(shadows) if isinstance(shadows, list) else 0,
        "breakpoints": {str(b) for b in breakpoints} if isinstance(breakpoints, list) else set(),
        "component_names": {
            c["name"] for c in components if isinstance(c, dict) and isinstance(c.get("name"), str)
        },
    }


def _check_design_schema(candidate_path: str, reference_path: str, thresholds: dict) -> dict:
    """Offline structural diff of a candidate design-schema vs. a reference. FAIL on
    render-of-a-different-system divergence (asymmetric — the candidate MISSING what
    the reference declares); benign additions pass. Missing/unparseable/non-schema
    evidence → `not_captured` (absence is not failure). `..`/outside-repo → exit 2.
    NEVER echoes raw file content: numeric dimensions are driver-derived, and the
    breakpoint/component tokens are filtered through the same `_safe_tokens` allowlist
    the parity gate uses."""
    record: dict = {"gate": "design-schema", "source_skill": "visual-feedback-loop"}
    # Path guard (parity with Gate 100): '..'/outside-repo raises → exit 2.
    cand_resolved = _resolve_safe(candidate_path)
    ref_resolved = _resolve_safe(reference_path)
    if not os.path.exists(cand_resolved) or not os.path.exists(ref_resolved):
        record["status"] = "not_captured"
        record["note"] = "design-schema-evidence-not-captured"
        return record
    try:
        cand = _load_json_bounded(candidate_path, what="design-schema candidate")
        ref = _load_json_bounded(reference_path, what="design-schema reference")
    except InputError:
        record["status"] = "not_captured"
        record["note"] = "design-schema-unparseable"
        return record
    cs = _design_skeleton(cand)
    rs = _design_skeleton(ref)
    if cs is None or rs is None:
        record["status"] = "not_captured"
        record["note"] = (
            "design-schema-candidate-non-schema-shape"
            if cs is None
            else "design-schema-reference-non-schema-shape"
        )
        return record

    tol = float(thresholds.get("design_ratio_tolerance", DEFAULTS["design_ratio_tolerance"]))
    diffs: list[dict] = []
    # spacing base-unit — compare only when the reference declares one (asymmetric).
    if rs["base_unit"] is not None and cs["base_unit"] != rs["base_unit"]:
        diffs.append(
            {"dimension": "spacing-base-unit", "expected": rs["base_unit"], "actual": cs["base_unit"]}
        )
    # type-scale ratio — must be within tolerance of the reference ratio.
    if rs["ratio"] is not None and (cs["ratio"] is None or abs(cs["ratio"] - rs["ratio"]) > tol):
        diffs.append({"dimension": "type-ratio", "expected": rs["ratio"], "actual": cs["ratio"]})
    # elevation ramp — candidate MISSING levels the reference has (more is benign).
    if cs["shadow_count"] < rs["shadow_count"]:
        diffs.append(
            {
                "dimension": "elevation-ramp-count",
                "expected": rs["shadow_count"],
                "actual": cs["shadow_count"],
            }
        )
    # breakpoints — candidate MISSING declared breakpoints (extra ones are benign).
    if rs["breakpoints"] - cs["breakpoints"]:
        diffs.append(
            {
                "dimension": "breakpoint-set",
                "expected": _safe_tokens(rs["breakpoints"]),
                "actual": _safe_tokens(cs["breakpoints"]),
            }
        )
    # components — candidate MISSING recognized component recipes.
    if rs["component_names"] - cs["component_names"]:
        diffs.append(
            {
                "dimension": "component-missing-key",
                "expected": _safe_tokens(rs["component_names"]),
                "actual": _safe_tokens(cs["component_names"]),
            }
        )

    record["status"] = "fail" if diffs else "pass"
    if diffs:
        record["deltas"] = diffs
    return record


# ── Verdict synthesis ────────────────────────────────────────────────────────
_DETERMINATE = {"pass", "fail", "error"}


def _synthesize(surface: str, gates: list[dict]) -> dict:
    """passed is a pure function of the determinate gates. not_captured /
    degraded gates are excluded (absence-of-evidence is not failure)."""
    determinate = [g for g in gates if g.get("status") in _DETERMINATE]
    any_fail = any(g["status"] in ("fail", "error") for g in determinate)
    has_runtime_evidence = any(
        g["gate"].startswith(("console", "lighthouse", "compare-ssim"))
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
                elif g["gate"] == "parity":
                    next_action = "match-reference-exemplar"
                elif g["gate"] == "console-errors":
                    next_action = "fix-console-errors"
                elif g["gate"] == "compare-ssim":
                    next_action = "improve-visual-fidelity"
                elif g["gate"] == "design-schema":
                    next_action = "match-design-schema"
                elif g["gate"].startswith("lighthouse-"):
                    next_action = f"improve-{g['gate'].split('-', 1)[1]}"
                break
        return {"passed": False, "next_action": next_action, "notes": notes}

    # All determinate gates pass.
    # LOUD fidelity degradation (P4): the offline design-schema diff is only a
    # "declares the same design system" floor — NOT a fidelity measurement. If it
    # passed but no browser-captured SSIM verified visual fidelity, a green verdict
    # must READ as "fidelity unverified", never a bare ship.
    structural_passed = any(
        g.get("gate") == "design-schema" and g.get("status") == "pass" for g in gates
    )
    ssim_verified = any(
        g.get("gate") == "compare-ssim" and g.get("status") == "pass" for g in gates
    )
    if structural_passed and not ssim_verified:
        return {
            "passed": True,
            "next_action": "capture-ssim-evidence",
            "notes": notes + ["visual fidelity not verified — no browser tool"],
        }
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

    if config.get("parity"):
        parity = config["parity"]
        if not isinstance(parity, dict):
            raise InputError("'parity' must be an object {candidate, reference}")
        cand_p, ref_p = parity.get("candidate"), parity.get("reference")
        if not isinstance(cand_p, str) or not isinstance(ref_p, str):
            raise InputError("'parity.candidate' and 'parity.reference' must be path strings")
        gates.append(_gate_parity(cand_p, ref_p))

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

    if config.get("design_schema"):
        ds = config["design_schema"]
        if not isinstance(ds, dict):
            raise InputError("'design_schema' must be an object {candidate, reference}")
        cand_p, ref_p = ds.get("candidate"), ds.get("reference")
        if not isinstance(cand_p, str) or not isinstance(ref_p, str):
            raise InputError(
                "'design_schema.candidate' and 'design_schema.reference' must be path strings"
            )
        gates.append(_check_design_schema(cand_p, ref_p, thresholds))

    if config.get("ssim"):
        if not isinstance(config["ssim"], str):
            raise InputError("'ssim' must be a path string")
        data = _load_json_bounded(config["ssim"], what="ssim evidence")
        gates.append(_gate_ssim(data, thresholds))

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
