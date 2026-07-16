#!/usr/bin/env python3
"""check-pipeline-lanes.py — Gate 133: the pipeline-map drift gate.

═══════════════════════════════════════════════════════════════════════════════
WHY THIS EXISTS
═══════════════════════════════════════════════════════════════════════════════
The Pipeline tab (panel-pipeline) is a HAND-MAINTAINED map of the guardrails an
agent passes through (`_PIPELINE_LANES` in scripts/generate-dashboards.py). Its
tooltips, ordering and 5th-grade copy have no source in hooks/hooks.json, so it
cannot be auto-generated. Before this gate, nothing asserted the curated map
still matched the actual registered hook set — and it had DRIFTED: two SHIPPED
hooks (`delegation-nudge.sh`, `guard-web-access.sh`) were missing from the map a
user reads, while the map's own comment claimed it was "grounded in hooks.json".

This gate makes that claim TRUE by construction. It reconciles the map against
hooks/hooks.json bidirectionally:

  1. `_PIPELINE_STAGE_HOOKS` keys == the stage ids actually in `_PIPELINE_LANES`
     (you cannot add/rename a stage without declaring the hook it represents).
  2. every mapped hook (non-None) is a REAL registered hook  (no phantom lanes).
  3. every registered hook is EITHER mapped into a lane OR in
     `_PIPELINE_EXCLUDED_HOOKS`  (a shipped hook in NEITHER list fails the build —
     the exact live-drift bug that hid `delegation-nudge`).
  4. `_PIPELINE_EXCLUDED_HOOKS` names only real, currently-registered hooks and
     never a hook that is also in a lane  (no stale / contradictory exclusions).
  5. the RENDERED artifact (dashboard.html) exposes a `data-stage` for exactly the
     lane stage ids  (the map that ships == the map in source).

Two stages map to None on purpose: `parallel-workers` and `claude-orchestrator`
are BEHAVIORAL guardrails (comfort-posture knobs read by spawn-team, not hooks).

Stdlib only — no node, no new dependency. Python 3.9 compatible.

═══════════════════════════════════════════════════════════════════════════════
Usage:
    python3 scripts/check-pipeline-lanes.py             # gate the real map
    python3 scripts/check-pipeline-lanes.py --must-fail  # teeth: assert a drifted
                                                         # map is caught (exit 0 if
                                                         # caught, 1 if it slips by)
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATOR = REPO_ROOT / "scripts" / "generate-dashboards.py"
HOOKS_JSON = REPO_ROOT / "plugins" / "ravenclaude-core" / "hooks" / "hooks.json"
DASHBOARD = REPO_ROOT / "plugins" / "ravenclaude-core" / "dashboard.html"
INDEX = REPO_ROOT / "index.html"


def load_generator():
    """Import generate-dashboards.py (its __main__ guard prevents generation).

    scripts/ must be on sys.path first — the generator does `from _html_merge
    import ...` relative to its own directory.
    """
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("generate_dashboards", GENERATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def registered_hooks(hooks_json_path: Path) -> set:
    """Every hook script basename registered in hooks.json.

    Walks every `command` string for a `hooks/<name>.sh` reference. Sourced
    helpers (`_`-prefixed) are never registered as hook entries and are dropped
    defensively.
    """
    data = json.loads(hooks_json_path.read_text(encoding="utf-8"))
    found = set()

    def walk(obj):
        if isinstance(obj, dict):
            cmd = obj.get("command")
            if isinstance(cmd, str):
                m = re.search(r"hooks/([A-Za-z0-9._-]+\.sh)", cmd)
                if m:
                    found.add(m.group(1))
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(data)
    return {h for h in found if not h.startswith("_")}


def validate(stage_ids, stage_hooks, excluded, registered) -> list:
    """Pure validator. Returns a list of human-readable error strings ([] == clean).

    This is the whole contract, factored out so the --must-fail half can drive it
    against a deliberately-drifted dataset without touching disk.
    """
    errors = []

    # (1) the map covers exactly the stages that exist — no more, no less.
    stage_id_set = set(stage_ids)
    map_keys = set(stage_hooks)
    for sid in sorted(map_keys - stage_id_set):
        errors.append(f"_PIPELINE_STAGE_HOOKS names a stage that is not in _PIPELINE_LANES: {sid}")
    for sid in sorted(stage_id_set - map_keys):
        errors.append(f"pipeline stage has no hook mapping (add it to _PIPELINE_STAGE_HOOKS): {sid}")

    lane_hooks = {h for h in stage_hooks.values() if h}

    # (2) every lane hook is a real registered hook.
    for h in sorted(lane_hooks - registered):
        errors.append(f"pipeline lane maps to a NON-EXISTENT hook (not in hooks.json): {h}")

    # (3) every registered hook is either in a lane or explicitly excluded.
    for h in sorted(registered - lane_hooks - excluded):
        errors.append(
            f"registered hook is MISSING from the pipeline map and not excluded: {h} "
            "(add a stage to _PIPELINE_LANES + _PIPELINE_STAGE_HOOKS, or list it in "
            "_PIPELINE_EXCLUDED_HOOKS with a reason)"
        )

    # (4) exclusions are honest: real hooks, not also shown in a lane.
    for h in sorted(excluded - registered):
        errors.append(f"_PIPELINE_EXCLUDED_HOOKS lists a hook that is not registered (stale): {h}")
    for h in sorted(excluded & lane_hooks):
        errors.append(f"hook is BOTH excluded and shown in a lane (contradiction): {h}")

    return errors


def rendered_stage_ids(html_path: Path) -> set:
    """The `data-stage` ids actually emitted into a generated surface."""
    if not html_path.exists():
        return set()
    text = html_path.read_text(encoding="utf-8")
    return set(re.findall(r'data-stage="([^"]+)"', text))


def run_real(mod) -> int:
    stage_ids = [st["id"] for lane in mod._PIPELINE_LANES for st in lane["stages"]]
    stage_hooks = dict(mod._PIPELINE_STAGE_HOOKS)
    excluded = set(mod._PIPELINE_EXCLUDED_HOOKS)
    registered = registered_hooks(HOOKS_JSON)

    errors = validate(stage_ids, stage_hooks, excluded, registered)

    # (5) the shipped artifact matches the source map (belt-and-suspenders with
    # Gate 13's byte-exact regen check, and what ties this gate to "rendered").
    for surface in (DASHBOARD, INDEX):
        emitted = rendered_stage_ids(surface)
        if not emitted:
            continue  # surface not present (e.g. index.html absent) — skip, not fail
        if emitted != set(stage_ids):
            miss = set(stage_ids) - emitted
            extra = emitted - set(stage_ids)
            errors.append(
                f"{surface.name}: rendered pipeline stages != _PIPELINE_LANES "
                f"(missing from render: {sorted(miss)}; extra in render: {sorted(extra)}) "
                "— regenerate the dashboards"
            )

    if errors:
        print("FAIL: pipeline map has drifted from hooks/hooks.json:")
        for e in errors:
            print(f"  - {e}")
        return 1

    lane_hooks = {h for h in stage_hooks.values() if h}
    print(
        f"OK: {len(stage_ids)} stages · {len(lane_hooks)} mapped hooks + "
        f"{len(excluded)} excluded == {len(registered)} registered hooks · "
        "rendered artifact matches source"
    )
    return 0


def run_must_fail(mod) -> int:
    """Teeth: reproduce the exact live-drift bug (a shipped hook dropped from BOTH
    the lanes and the exclusion list) and assert the validator catches it."""
    registered = registered_hooks(HOOKS_JSON)
    victim = "delegation-nudge.sh"
    if victim not in registered:
        print(f"MUST-FAIL SETUP ERROR: {victim} is not a registered hook — cannot stage the drift")
        return 1

    # Drop the victim's stage from BOTH the lanes and the mapping — i.e. simulate
    # the pre-fix state where a shipped hook was simply absent from the curation.
    stage_hooks = {k: v for k, v in mod._PIPELINE_STAGE_HOOKS.items() if v != victim}
    stage_ids = list(stage_hooks)  # keys stay in sync with the mutation
    excluded = set(mod._PIPELINE_EXCLUDED_HOOKS)  # NOT excluded either

    errors = validate(stage_ids, stage_hooks, excluded, registered)
    caught = any("MISSING from the pipeline map" in e and victim in e for e in errors)
    if caught:
        print(f"OK (teeth): validator caught the dropped hook '{victim}' as drift")
        return 0
    print(f"TEETH BROKEN: validator did NOT catch '{victim}' missing from the map")
    print(f"  errors seen: {errors}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--must-fail",
        action="store_true",
        help="teeth: assert a drifted map is caught (exit 0 if caught)",
    )
    args = ap.parse_args()

    mod = load_generator()
    if args.must_fail:
        return run_must_fail(mod)
    return run_real(mod)


if __name__ == "__main__":
    sys.exit(main())
