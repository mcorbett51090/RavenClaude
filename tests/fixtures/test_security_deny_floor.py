#!/usr/bin/env python3
"""
Unit test: security_deny floor is non-removable.

Regression test for the v0.101.0 fix in apply-comfort-posture.py.
A user (or the dashboard, or an attacker exploiting a typo) MUST NOT be
able to wipe the DEFAULT_SECURITY_DENY baseline by setting:

    security_deny: []           # explicit empty list
    # security_deny omitted entirely
    security_deny:
      - "Bash(some-custom-rule:*)"   # custom-only, no baseline entries

In all three cases, the emitted Claude Code permissions.deny bucket must
include every DEFAULT_SECURITY_DENY entry.

Run from repo root:
    python3 -m pytest tests/fixtures/test_security_deny_floor.py
or:
    python3 tests/fixtures/test_security_deny_floor.py
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "plugins" / "ravenclaude-core" / "scripts" / "apply-comfort-posture.py"


def _load_module():
    """Import apply-comfort-posture.py as a module despite the hyphen in its name."""
    spec = importlib.util.spec_from_file_location("apply_comfort_posture", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["apply_comfort_posture"] = mod
    spec.loader.exec_module(mod)
    return mod


ACP = _load_module()


class TestSecurityDenyFloor(unittest.TestCase):
    def setUp(self):
        self.baseline = list(ACP.DEFAULT_SECURITY_DENY)
        assert len(self.baseline) >= 5, "baseline is implausibly small — fixture stale?"

    def _emit(self, posture: dict) -> dict:
        # compute_emission expects a posture dict and returns
        # {"allow": [...], "ask": [...], "deny": [...]}.
        return ACP.compute_emission(posture)

    def _emit_layered(self, posture: dict) -> dict:
        return ACP.compute_emission_v5(posture)

    def test_empty_list_does_not_wipe_floor(self):
        out = self._emit({"categories": {}, "security_deny": []})
        for rule in self.baseline:
            self.assertIn(rule, out["deny"], f"baseline rule wiped by empty list: {rule!r}")

    def test_missing_field_keeps_floor(self):
        out = self._emit({"categories": {}})
        for rule in self.baseline:
            self.assertIn(rule, out["deny"], f"baseline rule missing when field absent: {rule!r}")

    def test_custom_only_still_unions_baseline(self):
        custom = "Bash(some-custom-rule:*)"
        out = self._emit({"categories": {}, "security_deny": [custom]})
        for rule in self.baseline:
            self.assertIn(rule, out["deny"], f"baseline rule missing alongside custom: {rule!r}")
        self.assertIn(custom, out["deny"], "custom rule not honored")

    def test_layered_empty_list_does_not_wipe_floor(self):
        out = self._emit_layered({"categories": {}, "security_deny": []})
        project_deny = out["project"]["deny"]
        for rule in self.baseline:
            self.assertIn(rule, project_deny, f"layered: baseline wiped by empty list: {rule!r}")

    def test_baseline_is_first_in_deny(self):
        out = self._emit({"categories": {}, "security_deny": ["Bash(extra:*)"]})
        first_n = out["deny"][: len(self.baseline)]
        self.assertEqual(
            first_n,
            self.baseline,
            "baseline must precede custom rules so the floor is visually obvious in settings.json",
        )

    def test_non_list_security_deny_raises(self):
        with self.assertRaises(ValueError):
            self._emit({"categories": {}, "security_deny": "not-a-list"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
