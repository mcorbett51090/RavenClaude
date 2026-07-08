#!/usr/bin/env python3
"""Regression test for decision 2b (2026-07-08 autonomous review, finding 9).

A lone Heimdall (the injection seat) abstention must NOT let the two-seat panel
return a binding verdict with injection never screened. Instead it forces a Thor
convene that re-screens injection. This drives `_tally` directly with a
Heimdall-abstain + Forseti/Mímir unanimous-'yes' fixture and asserts the verdict
comes from Thor (here mocked to 'defer'), not the rubber-stamped 'yes'.

Run: python3 test-heimdall-abstain-injection.py   (exit 0 = pass)
"""

import importlib.util
import os
import sys
from pathlib import Path

_SCRIPT = (Path(__file__).resolve().parents[1] / "scripts" / "thing-decide.py").resolve()
# thing-decide.py lives in ../scripts relative to hooks/tests -> hooks -> plugin root.
_SCRIPT = (Path(__file__).resolve().parents[2] / "scripts" / "thing-decide.py").resolve()

spec = importlib.util.spec_from_file_location("thing_decide", _SCRIPT)
td = importlib.util.module_from_spec(spec)
spec.loader.exec_module(td)


def _voted(role, verdict):
    return {
        "verdict": verdict,
        "confidence": 0.9,
        "injection_detected": False,
        "reasoning": f"{role} {verdict}",
        "status": "voted",
    }


def _abstain():
    return dict(td._ABSTAIN)


def main() -> int:
    cfg = {"panel": {"thor": {"model": "mock"}}, "confidence_threshold": 0.55}
    # Heimdall abstains; Forseti + Mímir vote a confident unanimous 'yes' on a smuggled
    # framing. Thor is mocked to 'defer' via THING_DECIDE_MOCK_VERDICT=heimdall-abstain.
    os.environ["THING_DECIDE_MOCK_VERDICT"] = "heimdall-abstain"
    seat_results = {
        "forseti": _voted("forseti", "yes"),
        "mimir": _voted("mimir", "yes"),
        "heimdall": _abstain(),
    }
    verdict, reasoning, records = td._tally(seat_results, 0.55, cfg, "should we do X?", "", 5)

    names = [r.get("name") for r in records]
    failures = []
    if verdict == "yes":
        failures.append(
            "FAIL: Heimdall abstain + Forseti/Mímir 'yes' rubber-stamped to 'yes' "
            "(injection never screened)"
        )
    if "thor" not in names:
        failures.append("FAIL: Heimdall abstain did not force a Thor convene")
    if verdict != "defer":
        failures.append(f"FAIL: expected Thor's 'defer', got {verdict!r}")

    if failures:
        for f in failures:
            print(f)
        return 1
    print(
        "PASS: lone Heimdall abstain forced a Thor re-screen; verdict='defer' "
        "(not a rubber-stamped 'yes'). reasoning:",
        reasoning[:80],
    )

    # Teeth: Forseti+Mímir unanimous 'yes' with Heimdall PRESENT-and-voting 'yes'
    # must still resolve 'yes' (the fix must not defer every unanimous panel).
    os.environ.pop("THING_DECIDE_MOCK_VERDICT", None)
    seat_results2 = {
        "forseti": _voted("forseti", "yes"),
        "mimir": _voted("mimir", "yes"),
        "heimdall": _voted("heimdall", "yes"),
    }
    v2, _, recs2 = td._tally(seat_results2, 0.55, cfg, "should we do X?", "", 5)
    if v2 != "yes" or "thor" in [r.get("name") for r in recs2]:
        print(
            f"FAIL (teeth): unanimous panel with Heimdall present should be 'yes' "
            f"with no Thor convene, got {v2!r}"
        )
        return 1
    print("PASS (teeth): unanimous panel with Heimdall present resolves 'yes', no Thor convene.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
