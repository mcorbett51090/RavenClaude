#!/usr/bin/env python3
"""test-gate91-tribunal-shadow.py — Gate 91.

Proves the Phase-4 agent-dispatch-evaluator SHADOW integration in thing-decide.py:
  (1) DISABLED by default — with no .ravenclaude/dispatch-config.json, a decision-review
      run produces seat records with NO evaluator_shadow field, and the verdict is
      whatever the panel decided (byte-identical to pre-P4 behavior).
  (2) ENABLED — with dispatch-config.json enabled:true, each seat record carries an
      evaluator_shadow {verdict, suggested_tier, would_have_changed_model_to, confidence,
      rationale}, AND the panel verdict is unchanged from the disabled run (shadow is
      observational — it never moves the verdict).
  (3) NEVER MUTATES THE SEAT MODEL — the shadow's `would_have_changed_model_to` is recorded,
      but the model the seat actually ran on (in the engine's panel config) is untouched.
      Asserted structurally: the shadow rides only in the audit record; the verdict/binding
      fields are identical between the enabled and disabled runs.

Offline: THING_DECIDE_MOCK_VERDICT stubs the seat votes; THING_DECIDE_MOCK_EVAL stubs the
shadow classifier — no `claude` / network / credits needed.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent.parent / "scripts" / "thing-decide.py"

PASS = 0
FAIL = 0


def ok(msg):
    global PASS
    PASS += 1
    print(f"  ✓ {msg}")


def bad(msg):
    global FAIL
    FAIL += 1
    print(f"  ✗ {msg}")


def run_decide(root: Path, enable_dispatch: bool) -> dict:
    rav = root / ".ravenclaude"
    rav.mkdir(parents=True, exist_ok=True)
    # decision_review: advisory so the panel actually convenes (mode != off).
    (rav / "comfort-posture.yaml").write_text("decision_review: advisory\n", encoding="utf-8")
    if enable_dispatch:
        (rav / "dispatch-config.json").write_text(
            json.dumps({"schema_version": "1", "enabled": True, "mode": "shadow",
                        "tribunal_seat_mode": "shadow", "rationale": "test"}),
            encoding="utf-8")
    env = {**os.environ, "THING_DECIDE_MOCK_VERDICT": "yes", "THING_DECIDE_MOCK_EVAL": "downgrade"}
    proc = subprocess.run(
        ["python3", str(ENGINE), "--root", str(root), "decide"],
        input=json.dumps({"question": "Should the docs-only change land?",
                          "context": "low risk", "high_blast": False}),
        capture_output=True, text=True, env=env, timeout=60,
    )
    return json.loads(proc.stdout)


def main() -> int:
    print("── Gate 91: agent-dispatch-evaluator tribunal-seat shadow (Phase 4) ──")
    if not ENGINE.is_file():
        print(f"FATAL: engine not found at {ENGINE}")
        return 2

    with tempfile.TemporaryDirectory() as td:
        root_off = Path(td) / "off"
        root_on = Path(td) / "on"
        res_off = run_decide(root_off, enable_dispatch=False)
        res_on = run_decide(root_on, enable_dispatch=True)

    seats_off = res_off.get("seats", [])
    seats_on = res_on.get("seats", [])

    # (1) Disabled -> no evaluator_shadow anywhere; seats ran.
    if seats_off and not any("evaluator_shadow" in s for s in seats_off):
        ok(f"disabled (no dispatch-config) → {len(seats_off)} seats, none carry evaluator_shadow")
    else:
        bad(f"disabled run should have seats with NO evaluator_shadow (got {len(seats_off)} seats, "
            f"shadowed={[s.get('name') for s in seats_off if 'evaluator_shadow' in s]})")

    # (2) Enabled -> every seat record carries a well-formed evaluator_shadow.
    shadowed = [s for s in seats_on if "evaluator_shadow" in s]
    if seats_on and len(shadowed) == len(seats_on):
        sample = shadowed[0]["evaluator_shadow"]
        keys_ok = all(k in sample for k in
                      ("verdict", "suggested_tier", "would_have_changed_model_to", "confidence", "rationale"))
        if keys_ok and sample["verdict"] == "downgrade":
            ok(f"enabled → all {len(seats_on)} seats carry a well-formed evaluator_shadow")
        else:
            bad(f"evaluator_shadow shape wrong: {sample}")
    else:
        bad(f"enabled run should shadow EVERY seat (got {len(shadowed)}/{len(seats_on)})")

    # (3) Shadow never moves the verdict: enabled vs disabled verdict+binding identical.
    if res_on.get("verdict") == res_off.get("verdict") and res_on.get("binding") == res_off.get("binding"):
        ok(f"verdict/binding identical with shadow on vs off (verdict={res_off.get('verdict')}) "
           f"— shadow is observational, never mutates the decision")
    else:
        bad(f"shadow changed the verdict/binding! off={res_off.get('verdict')}/{res_off.get('binding')} "
            f"on={res_on.get('verdict')}/{res_on.get('binding')}")

    # (3b) Teeth: the shadow records a downgrade target (would_have_changed_model_to set),
    # proving it COMPUTED a model change but the engine still reports the seat's real verdict
    # (not the shadow's). If shadow ever leaked into the verdict, (3) would have caught it.
    if shadowed and shadowed[0]["evaluator_shadow"].get("would_have_changed_model_to"):
        ok("shadow recorded a would_have_changed_model_to target (downgrade) without affecting the verdict")
    else:
        bad("downgrade shadow should record a would_have_changed_model_to target")

    print(f"  ── Gate 91 result: {PASS} passed, {FAIL} failed ──")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
