import os
import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import atlas_common  # noqa: E402

BYPASS = ("ATLAS_TEST_ALLOW_ANY_TREE", "ATLAS_ANY_TREE")


class AssertWorktreeTests(unittest.TestCase):
    """The pin accepts any linked worktree under .claude/worktrees/ on a feature branch."""

    def run_pin(self, top, branch, tool_top=None):
        def fake_git(*args, cwd=None):
            if args == ("rev-parse", "--show-toplevel"):
                return (0, tool_top if cwd and tool_top is not None else top)
            if args == ("branch", "--show-current"):
                return (0, branch)
            return (1, "")

        environment = {k: v for k, v in os.environ.items() if k not in BYPASS}
        with (
            mock.patch.dict(os.environ, environment, clear=True),
            mock.patch.object(atlas_common, "_git", side_effect=fake_git),
        ):
            atlas_common.assert_worktree()

    def test_any_worktree_on_a_feature_branch_passes(self):
        for name, branch in (
            ("forge-harness-atlas-md-mirror", "forge/harness-atlas-md-mirror"),
            ("anything", "feat/other"),
        ):
            self.run_pin(f"/repo/.claude/worktrees/{name}", branch)

    def test_the_primary_checkout_is_refused(self):
        with self.assertRaises(SystemExit) as caught:
            self.run_pin("/repo", "feat/x")
        self.assertIn("not a worktree", str(caught.exception))

    def test_main_and_master_are_refused_even_in_a_worktree(self):
        for branch in ("main", "master"):
            with self.assertRaises(SystemExit) as caught:
                self.run_pin("/repo/.claude/worktrees/w", branch)
            self.assertIn(branch, str(caught.exception))

    def test_a_detached_head_is_a_failure_not_a_pass(self):
        with self.assertRaises(SystemExit) as caught:
            self.run_pin("/repo/.claude/worktrees/w", "")
        self.assertIn("detached", str(caught.exception))

    def test_a_tool_file_from_another_tree_is_refused(self):
        with self.assertRaises(SystemExit) as caught:
            self.run_pin("/repo/.claude/worktrees/w", "feat/x", tool_top="/elsewhere")
        self.assertIn("different trees", str(caught.exception))

    def test_the_test_bypass_and_the_any_tree_switch_both_skip_the_pin(self):
        for name in BYPASS:
            with mock.patch.dict(os.environ, {name: "1"}):
                atlas_common.assert_worktree()


if __name__ == "__main__":
    unittest.main()
