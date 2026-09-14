#!/usr/bin/env python3
"""Regression: schema-v5 posture apply must write settings.json atomically.

PR #1086 added _settings_lock + _write_settings_json_atomic to the v3/v4
path because Path.write_text truncates in place — a concurrent SessionStart
reapply and dashboard /__save can then observe torn JSON. run_v5() (the
live path: this marketplace's comfort-posture.yaml is schema_version 5)
was not updated. This test fails if v5 still truncates settings.json in place.

Run from repo root:
    python3 tests/fixtures/test_v5_settings_atomic_write.py
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "plugins" / "ravenclaude-core" / "scripts" / "apply-comfort-posture.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("apply_comfort_posture", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["apply_comfort_posture"] = mod
    spec.loader.exec_module(mod)
    return mod


ACP = _load_module()


class TestV5AtomicSettingsWrite(unittest.TestCase):
    def test_run_v5_uses_atomic_write_and_lock(self):
        atomic_paths: list[str] = []
        lock_paths: list[str] = []
        orig_atomic = ACP._write_settings_json_atomic
        orig_lock = ACP._settings_lock

        def spy_atomic(path, payload):
            atomic_paths.append(str(path))
            orig_atomic(path, payload)

        def spy_lock(path):
            lock_paths.append(str(path))
            return orig_lock(path)

        ACP._write_settings_json_atomic = spy_atomic  # type: ignore[method-assign]
        ACP._settings_lock = spy_lock  # type: ignore[method-assign]
        self.addCleanup(lambda: setattr(ACP, "_write_settings_json_atomic", orig_atomic))
        self.addCleanup(lambda: setattr(ACP, "_settings_lock", orig_lock))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".ravenclaude").mkdir()
            (root / ".ravenclaude" / "comfort-posture.yaml").write_text(
                "schema_version: 5\n"
                "global_default: ask\n"
                "categories:\n"
                "  file_edit_project:\n"
                "    project: allow\n",
                encoding="utf-8",
            )
            args = argparse.Namespace(
                preview_merge=False,
                scope="project",
                dry_run=False,
                source="reapply",
            )
            rc = ACP.run_v5(
                {
                    "schema_version": 5,
                    "global_default": "ask",
                    "categories": {"file_edit_project": {"project": "allow"}},
                },
                root,
                args,
            )
            self.assertEqual(rc, 0)
            settings = root / ".claude" / "settings.json"
            self.assertTrue(settings.is_file(), "project settings.json was not written")
            json.loads(settings.read_text(encoding="utf-8"))
            self.assertTrue(
                any(Path(p).name == "settings.json" for p in atomic_paths),
                f"run_v5 did not call _write_settings_json_atomic; paths={atomic_paths}",
            )
            self.assertTrue(
                any(Path(p).name == "settings.json" for p in lock_paths),
                f"run_v5 did not take _settings_lock; paths={lock_paths}",
            )


if __name__ == "__main__":
    unittest.main()
