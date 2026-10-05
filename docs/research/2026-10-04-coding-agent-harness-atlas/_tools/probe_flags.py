"""Probe the command-line flags the atlas records against the coding-agent CLIs installed here.

For each column that has a CLI, run `<binary> --help` once (bounded, no input), then look for every
`cli_flag` lever literal the atlas records for that column. Two guards keep an empty result from
being read as an answer:

- a positive control: the output must name the product and look like a help text, or the whole
  probe is reported as invalid and no flag is judged;
- a column whose CLI is not installed is "not installed, not checked", never a pass.

"Not in the top-level --help" is not evidence that a flag was removed: a flag that belongs to a
subcommand, or is hidden, looks the same. The report says so. Results are what this machine's
installed version showed; they are written to --out, never merged into the atlas evidence.

Usage: python3 probe_flags.py --out DIR [--surface ID ...] [--data-dir DIR]
       python3 probe_flags.py --selftest
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from atlas_common import DATA_DIR, dump_json, load_json

# column id -> (candidate binaries in order, a word the help or version text must contain)
PRODUCTS = {
    "claude-code": (("claude",), "claude"),
    "codex-cli": (("codex",), "codex"),
    "copilot-cli": (("copilot",), "copilot"),
    "cursor": (("cursor-agent",), "cursor"),
    "gemini-cli": (("gemini",), "gemini"),
    "grok-build": (("grok",), "grok"),
}
TIMEOUT_S = 10
MAX_OUTPUT = 400_000
FLAG_TOKEN = re.compile(r"(?<![\w-])(--?[A-Za-z][\w-]*)")
HELP_HINT = re.compile(r"(?<![\w-])(--help|-h|--version|usage:|options:|commands:)", re.IGNORECASE)
NOT_FOUND_NOTE = (
    "not found in the top-level --help output; a flag that belongs to a subcommand or is hidden "
    "looks the same, so this is not evidence that the flag was removed"
)


def flag_tokens(literal):
    """The flags named in a lever literal: ``-f, --force`` and ``--mode <mode>`` each give names."""
    if not isinstance(literal, str):
        return []
    return sorted(set(FLAG_TOKEN.findall(literal.split("=")[0] if "=" in literal else literal)))


def run_command(argv):
    """(returncode, text) of one bounded command; (None, "") when it cannot run at all."""
    try:
        done = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
            stdin=subprocess.DEVNULL,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None, ""
    return done.returncode, ((done.stdout or "") + (done.stderr or ""))[:MAX_OUTPUT]


def probe_surface(sid, levers, which=shutil.which, run=run_command):
    candidates, ident = PRODUCTS[sid]
    binary = next((b for b in candidates if which(b)), None)
    if binary is None:
        return {"surface": sid, "status": "not-installed", "note": "not checked"}
    _, version_text = run([binary, "--version"])
    _, help_text = run([binary, "--help"])
    flags = sorted(
        {
            token
            for rec in levers
            if rec.get("surface") == sid and rec.get("location_kind") == "cli_flag"
            for token in flag_tokens(rec.get("literal"))
        }
    )
    first_line = (version_text.splitlines() or [""])[0][:120]
    named = ident in (help_text + version_text).lower()
    helpful = bool(HELP_HINT.search(help_text))
    result = {
        "surface": sid,
        "binary": binary,
        "version_line": first_line,
        "flags_recorded": len(flags),
    }
    if not (named and helpful):
        result["status"] = "probe-invalid"
        result["note"] = (
            "the control failed (the output does not name the product or does not look like a "
            "help text), so no flag was judged"
        )
        return result
    found = [f for f in flags if re.search(rf"(?<![\w-]){re.escape(f)}(?![\w-])", help_text)]
    missing = [f for f in flags if f not in found]
    result.update(
        {
            "status": "ok",
            "found_in_help": found,
            "not_in_top_level_help": missing,
            "note": NOT_FOUND_NOTE if missing else "",
        }
    )
    return result


def probe_all(data_dir, only=None, which=shutil.which, run=run_command):
    levers = load_json(Path(data_dir) / "levers.json")["levers"]
    return [probe_surface(sid, levers, which, run) for sid in PRODUCTS if not only or sid in only]


def render_summary(results):
    lines = ["# Flag probes", ""]
    for r in results:
        head = f"- {r['surface']}: {r['status']}"
        if r["status"] == "ok":
            head += (
                f" ({r['binary']}: {r['version_line']}) found {len(r['found_in_help'])}, "
                f"not in top-level help {len(r['not_in_top_level_help'])} of {r['flags_recorded']}"
            )
        elif r.get("note"):
            head += f" ({r['note']})"
        lines.append(head)
        for flag in r.get("not_in_top_level_help", []):
            lines.append(f"  - {flag}")
    return "\n".join(lines) + "\n"


def _selftest():
    got = flag_tokens("-f, --force")
    if got != ["--force", "-f"]:
        raise AssertionError(f"flag_tokens: {got}")
    if flag_tokens("--effort=LEVEL") != ["--effort"] or flag_tokens("agent models") != []:
        raise AssertionError("flag_tokens edge cases")
    print("OK")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out")
    parser.add_argument("--surface", action="append")
    parser.add_argument("--data-dir", default=str(DATA_DIR))
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0
    if not args.out:
        parser.error("--out is required unless --selftest is given")
    unknown = [s for s in args.surface or [] if s not in PRODUCTS]
    if unknown:
        print(f"probe_flags: no CLI known for {', '.join(unknown)}", file=sys.stderr)
        return 2
    try:
        results = probe_all(args.data_dir, args.surface)
    except (OSError, ValueError, KeyError) as exc:
        print(f"probe_flags: cannot read the lever records: {exc}", file=sys.stderr)
        return 2
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    dump_json(out / "flag-probes.json", {"schema_version": 1, "results": results})
    (out / "flag-probes.md").write_text(render_summary(results), encoding="utf-8", newline="\n")
    sys.stdout.write(render_summary(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
