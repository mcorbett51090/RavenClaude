import contextlib
import io
import json
import os
import re
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import atlas_nudge  # noqa: E402


class NudgeCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.home = self.root / "home"
        self.project = self.root / "project"
        (self.home / ".claude" / "sessions").mkdir(parents=True)
        self.data = (
            self.project / "docs" / "research" / "2026-10-04-coding-agent-harness-atlas" / "data"
        )
        self.data.mkdir(parents=True)
        self.write_snapshot("2.1.289")

    def write_snapshot(self, version):
        (self.data / "snapshot.json").write_text(
            json.dumps({"columns": [{"surface": "claude-code", "version": version}]}),
            encoding="utf-8",
        )

    def session(self, name, version, age=0):
        path = self.home / ".claude" / "sessions" / name
        path.write_text(json.dumps({"version": version}), encoding="utf-8")
        stamp = time.time() - age
        os.utime(path, (stamp, stamp))

    def nudge(self):
        return atlas_nudge.nudge(self.project, self.home)


class NudgeTests(NudgeCase):
    def test_equal_versions_say_nothing(self):
        self.session("a.json", "2.1.289")
        self.assertIsNone(self.nudge())

    def test_a_different_version_gives_one_line_naming_both_and_the_command(self):
        self.session("a.json", "2.1.300")
        line = self.nudge()
        self.assertIn("2.1.289", line)
        self.assertIn("2.1.300", line)
        self.assertIn("watch.py check", line)
        self.assertIn("no watch baseline yet", line)
        self.assertNotIn("\n", line)

    def test_a_baseline_date_is_quoted_when_there_is_one(self):
        self.session("a.json", "2.1.300")
        (self.data / "watch-baseline.json").write_text(
            json.dumps({"accepted": "2026-10-05"}), encoding="utf-8"
        )
        self.assertIn("docs last checked 2026-10-05", self.nudge())

    def test_the_newest_session_wins(self):
        self.session("old.json", "2.1.289", age=500)
        self.session("new.json", "2.1.300", age=1)
        self.assertIn("2.1.300", self.nudge())

    def test_a_session_file_with_no_usable_version_is_skipped(self):
        self.session("new.json", "not-a-version", age=1)
        (self.home / ".claude" / "sessions" / "broken.json").write_text("{", encoding="utf-8")
        self.session("old.json", "2.1.300", age=500)
        self.assertIn("2.1.300", self.nudge())

    def test_no_sessions_no_snapshot_or_a_broken_snapshot_say_nothing(self):
        self.assertIsNone(self.nudge())  # no session yet
        self.session("a.json", "2.1.300")
        (self.data / "snapshot.json").write_text("{", encoding="utf-8")
        self.assertIsNone(self.nudge())
        (self.data / "snapshot.json").unlink()
        self.assertIsNone(self.nudge())
        self.assertIsNone(atlas_nudge.nudge(self.root / "elsewhere", self.home))

    def test_a_snapshot_without_a_version_says_nothing(self):
        self.session("a.json", "2.1.300")
        (self.data / "snapshot.json").write_text(json.dumps({"columns": []}), encoding="utf-8")
        self.assertIsNone(self.nudge())


class ReadmeTests(unittest.TestCase):
    def test_the_documented_hook_entry_is_valid_json_and_points_at_this_script(self):
        readme = (TOOLS.parent / "README.md").read_text(encoding="utf-8")
        match = re.search(r"```json\n(.*?)```", readme, re.S)
        group = json.loads(match.group(1))
        command = group["hooks"][0]["command"]
        self.assertEqual(group["hooks"][0]["type"], "command")
        self.assertLessEqual(group["hooks"][0]["timeout"], 10)
        path = command.split('"')[1].replace("${CLAUDE_PROJECT_DIR}", str(TOOLS.parents[3]))
        self.assertEqual(Path(path).resolve(), (TOOLS / "atlas_nudge.py").resolve())


class MainTests(NudgeCase):
    def run_main(self):
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink):
            code = atlas_nudge.main(self.project, self.home)
        return code, sink.getvalue()

    def test_it_prints_the_session_start_envelope_only_when_there_is_a_line(self):
        self.session("a.json", "2.1.289")
        self.assertEqual(self.run_main(), (0, ""))
        self.session("b.json", "2.1.300", age=-5)
        code, out = self.run_main()
        self.assertEqual(code, 0)
        payload = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(payload["hookEventName"], "SessionStart")
        self.assertIn("2.1.300", payload["additionalContext"])

    def test_any_error_still_exits_zero_and_prints_nothing(self):
        with mock.patch.object(atlas_nudge, "nudge", side_effect=RuntimeError("boom")):
            self.assertEqual(self.run_main(), (0, ""))

    def test_it_starts_no_process_and_makes_no_network_call(self):
        source = (TOOLS / "atlas_nudge.py").read_text(encoding="utf-8")
        for banned in ("subprocess", "urllib", "socket", "http.client", "os.system"):
            self.assertNotIn(banned, source)


if __name__ == "__main__":
    unittest.main()
