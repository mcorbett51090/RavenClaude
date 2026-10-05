import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ["ATLAS_TEST_ALLOW_ANY_TREE"] = "1"
TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import probe_flags  # noqa: E402
from atlas_common import DATA_DIR, dump_json, load_json  # noqa: E402

HELP = "Usage: claude [options]\nOptions:\n  --help  show help\n  --effort <level>\n  --plan-mode\n"
LEVERS = [
    {"surface": "claude-code", "location_kind": "cli_flag", "literal": "--effort=LEVEL"},
    {"surface": "claude-code", "location_kind": "cli_flag", "literal": "--plan"},
    {"surface": "claude-code", "location_kind": "cli_flag", "literal": "--gone, -g"},
    {"surface": "claude-code", "location_kind": "settings_key", "literal": "--ignored"},
    {"surface": "codex-cli", "location_kind": "cli_flag", "literal": "--other"},
]


def runner(version="claude 2.0.0", help_text=HELP):
    def run(argv):
        return 0, (version if argv[-1] == "--version" else help_text)

    return run


def which_only(*names):
    return lambda name: f"/bin/{name}" if name in names else None


class FlagTokenTests(unittest.TestCase):
    def test_tokens_cover_the_shapes_the_atlas_records(self):
        cases = {
            "-f, --force": ["--force", "-f"],
            "--mode <mode>": ["--mode"],
            "--mode=plan": ["--mode"],
            "--effort=LEVEL": ["--effort"],
            "agent models": [],
            "model": [],
            None: [],
            "--a --b": ["--a", "--b"],
        }
        for literal, expected in cases.items():
            self.assertEqual(probe_flags.flag_tokens(literal), expected, literal)


class ProbeTests(unittest.TestCase):
    def probe(self, **kwargs):
        which = kwargs.pop("which", which_only("claude"))
        return probe_flags.probe_surface("claude-code", LEVERS, which, runner(**kwargs))

    def test_found_and_not_found_flags_are_listed_with_the_honest_note(self):
        result = self.probe()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["found_in_help"], ["--effort"])
        self.assertEqual(result["not_in_top_level_help"], ["--gone", "--plan", "-g"])
        self.assertIn("not evidence that the flag was removed", result["note"])

    def test_a_flag_is_not_found_inside_a_longer_flag(self):
        # --plan must not match --plan-mode
        self.assertIn("--plan", self.probe()["not_in_top_level_help"])

    def test_only_cli_flag_records_for_this_column_count(self):
        self.assertEqual(self.probe()["flags_recorded"], 4)

    def test_a_column_whose_cli_is_not_installed_is_not_checked_never_a_pass(self):
        result = self.probe(which=which_only())
        self.assertEqual(
            result, {"surface": "claude-code", "status": "not-installed", "note": "not checked"}
        )

    def test_a_help_text_that_does_not_name_the_product_fails_the_control(self):
        result = self.probe(version="mystery 1.0", help_text="Usage: x\n--help\n")
        self.assertEqual(result["status"], "probe-invalid")
        self.assertNotIn("not_in_top_level_help", result)

    def test_output_that_is_not_a_help_text_fails_the_control(self):
        result = self.probe(help_text="claude: command crashed")
        self.assertEqual(result["status"], "probe-invalid")

    def test_a_command_that_cannot_run_fails_the_control(self):
        def broken(_argv):
            return None, ""

        result = probe_flags.probe_surface("claude-code", LEVERS, which_only("claude"), broken)
        self.assertEqual(result["status"], "probe-invalid")

    def test_no_note_when_every_flag_was_found(self):
        levers = [LEVERS[0]]
        result = probe_flags.probe_surface("claude-code", levers, which_only("claude"), runner())
        self.assertEqual((result["status"], result["note"]), ("ok", ""))


class CliTests(unittest.TestCase):
    def test_unknown_surface_is_a_usage_error(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = probe_flags.main(["--out", "x", "--surface", "grok-bot"])
        self.assertEqual(code, 2)
        self.assertIn("grok-bot", err.getvalue())

    def test_it_writes_json_and_markdown_and_never_into_the_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            dump_json(data / "levers.json", {"levers": LEVERS})
            out = Path(tmp) / "out"
            sink = io.StringIO()
            with contextlib.redirect_stdout(sink):
                code = probe_flags.main(
                    ["--out", str(out), "--data-dir", str(data), "--surface", "codex-cli"]
                )
            self.assertEqual(code, 0)
            written = load_json(out / "flag-probes.json")
            self.assertEqual(written["results"][0]["surface"], "codex-cli")
            self.assertTrue((out / "flag-probes.md").exists())
            self.assertIn("codex-cli:", sink.getvalue())

    def test_unreadable_levers_are_a_usage_error(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = probe_flags.main(["--out", "x", "--data-dir", "/nonexistent"])
        self.assertEqual(code, 2)

    def test_selftest_prints_ok(self):
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink):
            self.assertEqual(probe_flags.main(["--selftest"]), 0)
        self.assertEqual(sink.getvalue().strip(), "OK")


class RealDataTests(unittest.TestCase):
    def test_every_known_cli_is_a_real_column_and_has_recorded_flags(self):
        surfaces = {s["id"] for s in load_json(DATA_DIR / "surfaces.json")["surfaces"]}
        self.assertTrue(set(probe_flags.PRODUCTS) <= surfaces)
        levers = load_json(DATA_DIR / "levers.json")["levers"]
        for sid in probe_flags.PRODUCTS:
            names = {
                t
                for r in levers
                if r["surface"] == sid and r["location_kind"] == "cli_flag"
                for t in probe_flags.flag_tokens(r.get("literal"))
            }
            self.assertTrue(names, sid)

    def test_a_missing_cli_everywhere_reports_not_installed_for_all(self):
        results = probe_flags.probe_all(DATA_DIR, which=which_only())
        self.assertEqual({r["status"] for r in results}, {"not-installed"})


if __name__ == "__main__":
    unittest.main()
