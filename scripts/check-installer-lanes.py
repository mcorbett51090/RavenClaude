#!/usr/bin/env python3
"""check-installer-lanes.py — end-to-end lane tests for `scripts/ravenclaude`.

Before this file, no gate drove the gemini / cursor / aider / codex install
lanes end to end (repo-review 2026-10-19: only status/update/copilot-repair and
the per-generator `--check` gates existed). Every case below runs the REAL
installer — a byte copy of it — against a SCRATCH marketplace and a SCRATCH
project, with HOME, TMPDIR and every host config dir redirected into a
`mktemp -d`. The real ~/.bashrc / ~/.zshrc are hashed before and after the run
and the check fails if either changed: a test that edits the operator's own
dotfiles is the exact incident this suite exists after (a validator once ran a
real installer and wrote into /root/.bashrc).

THE SCRATCH MARKETPLACE. `scripts/ravenclaude` derives MARKET from its own
location, so the copy at <scratch>/market/scripts/ravenclaude believes
<scratch>/market is the marketplace. The real generators are symlinked in (they
resolve their own manifest through `Path(__file__).resolve()`, i.e. the real
repo, read-only), the real hooks/templates/copilot/codex dirs are symlinked in
read-only, and the skills/commands are two FAKE skills and one fake command, so
nothing a lane writes can land in the real tree.

Cases (item ids from the 2026-10-19 review):
  scripts-1   a valid / BOM / trailing-comma / // comment .gemini/settings.json:
              valid + BOM merge and keep the user keys; the other two are
              REFUSED with the file byte-identical, and emit-gemini-config.py
              refuses the same file with a non-zero exit.
  scripts-2   three consecutive Cursor-lane runs leave the scratch marketplace
              skill tree unchanged (no cyclic <skill>.rc-old link).
  scripts-3   a user's own same-named skill / command survives as .rc-bak with a
              warning; a byte-identical copy is refreshed with no backup; an
              idempotent re-run creates no new backup (copilot + codex lanes).
  scripts-4   a customised .aider.conf.yml / .cursor/hooks.json /
              .codex/hooks.json is backed up once; an identical re-run makes no
              second backup.
  scripts-5   a failed Copilot hooks projection prints no green "wired" line
              and ends with "NOT fully installed".
  scripts-6   a typo'd flag exits 2, a flag without its value exits 2, a bare
              word is the project, `setup` still works with empty install_args,
              and installing into the marketplace checkout itself is refused.
  scripts-7   a first-run `setup` on the codex and gemini hosts projects the
              sandbox posture (the seed now runs BEFORE install).
  scripts-13  a .cursorignore with a BEGIN marker and no END marker is reported
              and left unchanged, and the rest of the Cursor lane still runs.
  door 5      (Linux proxy for check-macos-portability.sh door 5) no here-doc
              opened inside a $( ) command substitution contains an apostrophe.

Exit codes: 0 every case passed; 1 a case failed; 2 usage. `--must-fail`
builds one mutant installer per load-bearing fix, runs the case that should
catch it, and exits 3 (the declared teeth code, see `--must-fail-convention`)
only when EVERY mutant was caught. 0/1/2 are reachable by success, a failure or
a crash, so none of them may stand for "teeth proven".

Python 3.9+, stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INSTALLER = REPO / "scripts" / "ravenclaude"
CORE = REPO / "plugins" / "ravenclaude-core"

GENERATORS = (
    "emit-codex-config.py",
    "emit-gemini-config.py",
    "generate-aider-conventions.py",
    "generate-codex-hooks.py",
    "generate-copilot-hooks.py",
    "generate-cursor-agents.py",
    "generate-cursor-hooks.py",
    "generate-gemini-hooks.py",
    "install-codex-mcp.py",
    "install-copilot-mcp.py",
)
CORE_LINKS = ("hooks", "templates", "copilot", "codex")
DROP_ENV = (
    "ZDOTDIR",
    "RC_FROM_SETUP",
    "RC_WITH_MCP",
    "CODESPACES",
    "CODESPACE_NAME",
    "CLAUDE_PROJECT_DIR",
    "CLAUDE_SESSION_ID",
    "RC_CODEX_SESSIONSTART_LEGACY",
    "COPILOT_HOME",
    "CODEX_HOME",
)
ANSI = re.compile(r"\x1b\[[0-9;]*m")
TEETH_EXIT = 3


# ── scratch fixtures ────────────────────────────────────────────────────────
def build_market(root: Path, installer_text: str) -> Path:
    m = root / "market"
    (m / "scripts").mkdir(parents=True)
    inst = m / "scripts" / "ravenclaude"
    inst.write_text(installer_text, encoding="utf-8")
    inst.chmod(0o755)
    for g in GENERATORS:
        src = REPO / "scripts" / g
        if src.is_file():
            os.symlink(src, m / "scripts" / g)
    shutil.copy(REPO / ".repo-layout.json", m / ".repo-layout.json")
    core = m / "plugins" / "ravenclaude-core"
    (core / "scripts").mkdir(parents=True)
    for name in CORE_LINKS:
        os.symlink(CORE / name, core / name)
    os.symlink(
        CORE / "scripts" / "apply-comfort-posture.py",
        core / "scripts" / "apply-comfort-posture.py",
    )
    for skill in ("alpha", "beta"):
        d = core / "skills" / skill
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(
            f"---\nname: {skill}\ndescription: lane-test skill {skill}\n---\nbody {skill}\n",
            encoding="utf-8",
        )
    (core / "commands").mkdir()
    (core / "commands" / "hello.md").write_text(
        "---\ndescription: lane-test command\n---\nhello\n", encoding="utf-8"
    )
    return m


def make_env(root: Path, extra_bin: Path | None = None, strip_hosts: bool = False) -> dict:
    home = root / "home"
    home.mkdir(exist_ok=True)
    tmp = root / "tmp"
    tmp.mkdir(exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k not in DROP_ENV}
    env.update(
        HOME=str(home),
        TMPDIR=str(tmp),
        SHELL="/bin/bash",
        XDG_CONFIG_HOME=str(home / ".config"),
        XDG_CACHE_HOME=str(home / ".cache"),
    )
    path = env.get("PATH", "")
    if strip_hosts:
        keep = []
        for part in path.split(os.pathsep):
            if any((Path(part) / h).exists() for h in ("copilot", "codex")):
                continue
            keep.append(part)
        path = os.pathsep.join(keep)
    if extra_bin is not None:
        path = str(extra_bin) + os.pathsep + path
    env["PATH"] = path
    return env


def run(market: Path, args: list, env: dict, cwd: Path, timeout: int = 240):
    p = subprocess.run(
        ["bash", str(market / "scripts" / "ravenclaude"), *args],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return p.returncode, ANSI.sub("", p.stdout), ANSI.sub("", p.stderr)


def snapshot(path: Path) -> list:
    out = []
    for dirpath, dirnames, filenames in os.walk(path, followlinks=False):
        for n in dirnames + filenames:
            p = Path(dirpath) / n
            rel = str(p.relative_to(path))
            if p.is_symlink():
                out.append((rel, "link", os.readlink(p)))
            elif p.is_file():
                out.append((rel, "file", hashlib.sha256(p.read_bytes()).hexdigest()))
            else:
                out.append((rel, "dir", ""))
    return sorted(out)


def backups(directory: Path, name: str) -> list:
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.iterdir() if p.name.startswith(name + ".rc-bak."))


def _project(root: Path) -> Path:
    p = root / "proj"
    p.mkdir()
    return p


def _seed_posture(project: Path) -> None:
    (project / ".ravenclaude").mkdir(exist_ok=True)
    shutil.copy(
        CORE / "templates" / "comfort-posture-balanced.yaml",
        project / ".ravenclaude" / "comfort-posture.yaml",
    )


class Case:
    def __init__(self, scratch: Path, installer_text: str):
        self.root = Path(tempfile.mkdtemp(prefix="lane-", dir=str(scratch)))
        self.market = build_market(self.root, installer_text)
        self.project = _project(self.root)
        self.env = make_env(self.root)
        self.fails: list = []

    def check(self, cond: bool, msg: str) -> None:
        if not cond:
            self.fails.append(msg)

    def install(self, *args, cwd: Path | None = None, env: dict | None = None):
        return run(self.market, ["install", *args], env or self.env, cwd or self.project)


# ── cases ───────────────────────────────────────────────────────────────────
def case_gemini_settings(scratch: Path, text: str) -> list:
    """scripts-1: valid + BOM merge; trailing comma + comment refused untouched."""
    fails = []
    user = {"model": "gemini-x", "theme": "Dracula", "mcpServers": {"mine": {"command": "x"}}}
    variants = {
        "valid": json.dumps(user, indent=2).encode("utf-8"),
        "bom": b"\xef\xbb\xbf" + json.dumps(user).encode("utf-8"),
        "trailing-comma": b'{"model": "gemini-x", "theme": "Dracula",}\n',
        "comment": b'{\n  // my model\n  "model": "gemini-x"\n}\n',
    }
    for label, raw in variants.items():
        c = Case(scratch, text)
        _seed_posture(c.project)
        (c.project / ".gemini").mkdir()
        dest = c.project / ".gemini" / "settings.json"
        dest.write_bytes(raw)
        rc, out, err = c.install("--host", "gemini", "--project", str(c.project))
        both = out + err
        if label in ("valid", "bom"):
            c.check(rc == 0, f"gemini {label}: install exited {rc}")
            try:
                got = json.loads(dest.read_text(encoding="utf-8-sig"))
            except Exception as exc:  # noqa: BLE001
                c.fails.append(f"gemini {label}: result is not JSON ({exc})")
                got = {}
            for k in ("model", "theme", "mcpServers"):
                c.check(k in got, f"gemini {label}: user key {k!r} was dropped by the merge")
            c.check("hooks" in got, f"gemini {label}: no hooks were merged in")
            c.check("merge FAILED" not in both, f"gemini {label}: a valid file was refused")
        else:
            c.check(dest.read_bytes() == raw, f"gemini {label}: settings.json was MODIFIED")
            c.check("merge FAILED" in both, f"gemini {label}: no merge-failed warning")
            c.check("unparseable" in both, f"gemini {label}: the reason was not shown")
            c.check(
                "merged, not clobbered" not in both,
                f"gemini {label}: printed the 'merged, not clobbered' success line",
            )
            c.check(
                "comfort posture NOT projected" in both,
                f"gemini {label}: the posture emitter failure was not reported",
            )
            c.check("NOT fully installed" in both, f"gemini {label}: no NOT-fully-installed line")
            # emit-gemini-config.py on its own: non-zero, file untouched.
            p = subprocess.run(
                [
                    sys.executable,
                    str(REPO / "scripts" / "emit-gemini-config.py"),
                    "--project",
                    str(c.project),
                ],
                capture_output=True,
                text=True,
                timeout=60,
                env=c.env,
            )
            c.check(
                p.returncode != 0, f"emit-gemini-config {label}: exited 0 on an unparseable file"
            )
            c.check(dest.read_bytes() == raw, f"emit-gemini-config {label}: file was MODIFIED")
        fails += c.fails
    return fails


def case_cursor_three_runs(scratch: Path, text: str) -> list:
    """scripts-2: three runs leave the marketplace skill tree unchanged."""
    c = Case(scratch, text)
    src = c.market / "plugins" / "ravenclaude-core" / "skills"
    before = snapshot(src)
    for i in range(3):
        rc, _out, err = c.install("--host", "cursor", "--project", str(c.project))
        c.check(rc == 0, f"cursor run {i + 1}: install exited {rc}: {err[-300:]}")
    c.check(snapshot(src) == before, "cursor x3: the MARKETPLACE skill tree changed")
    skills = c.project / ".cursor" / "skills"
    names = sorted(p.name for p in skills.iterdir()) if skills.is_dir() else []
    c.check(names == ["alpha", "beta"], f"cursor x3: unexpected .cursor/skills entries {names}")
    for n in ("alpha", "beta"):
        c.check((skills / n).is_symlink(), f"cursor x3: .cursor/skills/{n} is not a symlink")
    return c.fails


def case_cursor_malformed_ignore(scratch: Path, text: str) -> list:
    """scripts-13: a BEGIN-without-END .cursorignore is reported, lane continues."""
    c = Case(scratch, text)
    raw = "keep-me\n# BEGIN RAVENCLAUDE\nhand-trimmed\n"
    (c.project / ".cursorignore").write_text(raw, encoding="utf-8")
    rc, out, err = c.install("--host", "cursor", "--project", str(c.project))
    both = out + err
    c.check(rc == 0, f"malformed .cursorignore: install exited {rc} (the lane aborted)")
    c.check(
        (c.project / ".cursorignore").read_text(encoding="utf-8") == raw,
        "malformed .cursorignore: the file was modified",
    )
    c.check(".cursorignore was NOT updated" in both, "malformed .cursorignore: no warning")
    c.check(
        (c.project / ".cursor" / "skills" / "alpha").exists(),
        "malformed .cursorignore: the rest of the Cursor lane did not run",
    )
    c.check("NOT fully installed" in both, "malformed .cursorignore: no NOT-fully-installed line")
    return c.fails


def case_user_content_preserved(scratch: Path, text: str) -> list:
    """scripts-3: own skill/command backed up; identical copy refreshed; idempotent."""
    c = Case(scratch, text)
    skills = c.project / ".claude" / "skills"
    (skills / "alpha").mkdir(parents=True)
    (skills / "alpha" / "SKILL.md").write_text("MY OWN SKILL\n", encoding="utf-8")
    shutil.copytree(c.market / "plugins" / "ravenclaude-core" / "skills" / "beta", skills / "beta")
    cmds = c.project / ".claude" / "commands"
    cmds.mkdir(parents=True)
    (cmds / "hello.md").write_text("MY OWN CMD\n", encoding="utf-8")

    rc, _out, err = c.install("--host", "copilot", "--project", str(c.project))
    c.check(rc == 0, f"own content: install exited {rc}: {err[-300:]}")
    c.check((skills / "alpha").is_symlink(), "own content: alpha was not wired as a link")
    bak = backups(skills, "alpha")
    c.check(len(bak) == 1, f"own content: expected 1 alpha backup, got {len(bak)}")
    if bak:
        c.check(
            (bak[0] / "SKILL.md").read_text(encoding="utf-8") == "MY OWN SKILL\n",
            "own content: the alpha backup does not hold the user's skill",
        )
    c.check("kept your own alpha" in err, "own content: no 'kept your own alpha' warning")
    c.check((skills / "beta").is_symlink(), "own content: identical beta copy was not refreshed")
    c.check(not backups(skills, "beta"), "own content: an identical copy was backed up")
    cbak = backups(cmds, "hello.md")
    c.check(len(cbak) == 1, f"own content: expected 1 hello.md backup, got {len(cbak)}")
    if cbak:
        c.check(
            cbak[0].read_text(encoding="utf-8") == "MY OWN CMD\n",
            "own content: the command backup does not hold the user's command",
        )
    rc, _out, _err = c.install("--host", "copilot", "--project", str(c.project))
    c.check(rc == 0, f"own content: re-run exited {rc}")
    c.check(len(backups(skills, "alpha")) == 1, "own content: the re-run made a new skill backup")
    c.check(
        len(backups(cmds, "hello.md")) == 1, "own content: the re-run made a new command backup"
    )

    # Codex lane: .agents/skills + .codex/hooks.json.
    c2 = Case(scratch, text)
    ag = c2.project / ".agents" / "skills"
    (ag / "alpha").mkdir(parents=True)
    (ag / "alpha" / "SKILL.md").write_text("MY CODEX SKILL\n", encoding="utf-8")
    (c2.project / ".codex").mkdir()
    (c2.project / ".codex" / "hooks.json").write_text('{"hooks": {"mine": []}}\n', encoding="utf-8")
    for i in range(2):
        rc, _out, err = c2.install("--host", "codex", "--project", str(c2.project))
        c2.check(rc == 0, f"codex run {i + 1}: install exited {rc}: {err[-300:]}")
    c2.check((ag / "alpha").is_symlink(), "codex: alpha was not wired as a link")
    c2.check(len(backups(ag, "alpha")) == 1, "codex: expected exactly 1 alpha backup after 2 runs")
    hb = backups(c2.project / ".codex", "hooks.json")
    c2.check(
        len(hb) == 1, f"codex: expected exactly 1 hooks.json backup after 2 runs, got {len(hb)}"
    )
    if hb:
        c2.check(
            '"mine"' in hb[0].read_text(encoding="utf-8"), "codex: hooks.json backup lost content"
        )
    return c.fails + c2.fails


def case_config_backups(scratch: Path, text: str) -> list:
    """scripts-4: a customised .aider.conf.yml / .cursor/hooks.json is backed up once."""
    c = Case(scratch, text)
    conf = c.project / ".aider.conf.yml"
    conf.write_text("model: gpt-x\nauto-commits: false\n", encoding="utf-8")
    for i in range(2):
        rc, _out, err = c.install("--host", "aider", "--project", str(c.project))
        c.check(rc == 0, f"aider run {i + 1}: install exited {rc}: {err[-300:]}")
    bak = backups(c.project, ".aider.conf.yml")
    c.check(len(bak) == 1, f"aider: expected exactly 1 .aider.conf.yml backup, got {len(bak)}")
    if bak:
        c.check(
            "model: gpt-x" in bak[0].read_text(encoding="utf-8"), "aider: backup lost the user keys"
        )
    c.check(
        "read:" in conf.read_text(encoding="utf-8"), "aider: .aider.conf.yml lacks the read: opt-in"
    )

    c2 = Case(scratch, text)
    (c2.project / ".cursor").mkdir()
    hooks = c2.project / ".cursor" / "hooks.json"
    hooks.write_text(
        '{"version": 1, "hooks": {"beforeShellExecution": [{"command": "my-own-hook.sh"}]}}\n',
        encoding="utf-8",
    )
    for i in range(2):
        rc, _out, err = c2.install("--host", "cursor", "--project", str(c2.project))
        c2.check(rc == 0, f"cursor hooks run {i + 1}: install exited {rc}: {err[-300:]}")
    hb = backups(c2.project / ".cursor", "hooks.json")
    c2.check(len(hb) == 1, f"cursor: expected exactly 1 hooks.json backup, got {len(hb)}")
    if hb:
        c2.check(
            "my-own-hook.sh" in hb[0].read_text(encoding="utf-8"),
            "cursor: the hooks.json backup lost the user hook",
        )
    return c.fails + c2.fails


def case_copilot_hooks_failure(scratch: Path, text: str) -> list:
    """scripts-5: a failed hooks projection prints no green 'wired' line."""
    c = Case(scratch, text)
    (c.project / ".github" / "hooks" / "ravenclaude.json").mkdir(parents=True)
    rc, out, err = c.install("--host", "copilot", "--project", str(c.project))
    both = out + err
    c.check(rc == 0, f"hooks failure: install exited {rc} (setup would abort)")
    c.check(
        "wired hooks into .github/hooks/ravenclaude.json" not in both,
        "hooks failure: printed the green 'wired hooks' line after the projection failed",
    )
    c.check("guardrails NOT wired" in both, "hooks failure: no 'guardrails NOT wired' warning")
    c.check("NOT fully installed" in both, "hooks failure: no NOT-fully-installed line")
    c.check("install complete" not in both, "hooks failure: still printed 'install complete'")
    return c.fails


def case_parser(scratch: Path, text: str) -> list:
    """scripts-6: typo flag / missing value exit 2; bare word; setup; marketplace refusal."""
    c = Case(scratch, text)
    rc, _o, _e = c.install("--projcet", str(c.project), "--host", "copilot")
    c.check(rc == 2, f"parser: a typo'd flag exited {rc}, not 2")
    rc, _o, err = c.install("--project")
    c.check(rc == 2, f"parser: --project with no value exited {rc}, not 2")
    c.check(
        "unbound variable" not in err, "parser: a missing value still dies with 'unbound variable'"
    )
    elsewhere = c.root / "elsewhere"
    elsewhere.mkdir()
    rc, _o, err = c.install("--host", "copilot", str(c.project), cwd=elsewhere)
    c.check(rc == 0, f"parser: a bare project path exited {rc}: {err[-300:]}")
    c.check(
        (c.project / ".claude" / "skills").is_dir(), "parser: the bare project path was ignored"
    )
    c.check(
        not (elsewhere / ".claude").exists(), "parser: installed into $PWD instead of the bare path"
    )
    rc, _o, _e = c.install("--host", "copilot", cwd=c.market)
    c.check(rc == 2, f"parser: installing into the marketplace checkout exited {rc}, not 2")
    c.check(not (c.market / ".claude").exists(), "parser: the marketplace checkout was wired")

    c2 = Case(scratch, text)
    rc, out, err = run(c2.market, ["setup", "--project", str(c2.project)], c2.env, c2.project)
    c2.check(rc == 0, f"parser: setup with empty install_args exited {rc}: {(out + err)[-300:]}")
    c2.check(
        (c2.project / ".ravenclaude" / "comfort-posture.yaml").is_file(),
        "parser: setup did not seed the posture",
    )
    return c.fails + c2.fails


def case_setup_first_run(scratch: Path, text: str) -> list:
    """scripts-7: first-run setup projects the posture on codex and gemini."""
    fails = []
    # codex, reached the way a real Codex user reaches it: detect_host picks codex
    # when a `codex` binary is on PATH and `copilot` is not.
    c = Case(scratch, text)
    fake = c.root / "fakebin"
    fake.mkdir()
    (fake / "codex").write_text("#!/bin/sh\necho 'codex-cli 0.0.0'\n", encoding="utf-8")
    (fake / "codex").chmod(0o755)
    env = make_env(c.root, extra_bin=fake, strip_hosts=True)
    rc, out, err = run(c.market, ["setup", "--project", str(c.project)], env, c.project)
    both = out + err
    c.check(rc == 0, f"setup codex: exited {rc}: {both[-300:]}")
    c.check("host: codex" in both, "setup codex: host detection did not pick codex")
    cfg = c.project / ".codex" / "config.toml"
    c.check(cfg.is_file(), "setup codex: .codex/config.toml was not written on the FIRST run")
    if cfg.is_file():
        c.check("sandbox_mode" in cfg.read_text(encoding="utf-8"), "setup codex: no sandbox_mode")
    c.check(
        "no comfort-posture.yaml here" not in both,
        "setup codex: still printed the 'no comfort-posture.yaml here' line",
    )
    fails += c.fails

    c2 = Case(scratch, text)
    rc, out, err = run(
        c2.market, ["setup", "--host", "gemini", "--project", str(c2.project)], c2.env, c2.project
    )
    c2.check(rc == 0, f"setup gemini: exited {rc}: {(out + err)[-300:]}")
    st = c2.project / ".gemini" / "settings.json"
    got = {}
    if st.is_file():
        try:
            got = json.loads(st.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            got = {}
    c2.check(
        "general" in got or "tools" in got,
        "setup gemini: no posture keys in .gemini/settings.json after the first run",
    )
    fails += c2.fails
    return fails


HEREDOC_OPEN = re.compile(r"<<-?\s*'?\"?([A-Za-z_][A-Za-z0-9_]*)'?\"?")


def door5_findings(text: str) -> list:
    """Every here-doc opened on a line that also opens a $( ) substitution must be
    apostrophe-free: bash 3.2 re-lexes such a body for quotes even under a quoted
    tag, and one unpaired apostrophe stops the whole installer parsing (PR #828)."""
    out = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        m = HEREDOC_OPEN.search(line)
        if m and "$(" in line.split("<<", 1)[0]:
            tag = m.group(1)
            j = i + 1
            while j < len(lines) and lines[j].strip() != tag:
                if "'" in lines[j]:
                    out.append(
                        f"line {j + 1}: apostrophe inside the {tag} here-doc opened in $( ) "
                        f"at line {i + 1}"
                    )
                j += 1
            i = j
        i += 1
    return out


def case_door5(scratch: Path, text: str) -> list:
    fails = [f"door 5: {f}" for f in door5_findings(text)]
    # Teeth on the scanner itself: plant one apostrophe in the PY2 body.
    planted = text.replace(
        "dest, src = pathlib.Path", "# it" + "'" + "s planted\ndest, src = pathlib.Path", 1
    )
    if planted == text:
        fails.append("door 5: the plant anchor was not found — the scanner teeth cannot run")
    elif not door5_findings(planted):
        fails.append("door 5: the scanner missed a planted apostrophe")
    return fails


CASES = {
    "gemini-settings": case_gemini_settings,
    "cursor-three-runs": case_cursor_three_runs,
    "cursor-malformed-ignore": case_cursor_malformed_ignore,
    "user-content-preserved": case_user_content_preserved,
    "config-backups": case_config_backups,
    "copilot-hooks-failure": case_copilot_hooks_failure,
    "parser": case_parser,
    "setup-first-run": case_setup_first_run,
    "door5": case_door5,
}

# One mutant per load-bearing fix: (label, anchor, replacement, case that must catch it).
MUTANTS = (
    (
        "scripts-1 gemini refusal neutered",
        "        sys.exit(3)\n    if not isinstance(cur, dict):",
        "        cur = {}\n    if not isinstance(cur, dict):",
        "gemini-settings",
    ),
    (
        "scripts-2 cursor rotation restored",
        '    # user content once, under a fresh name.\n    _rc_place_link "$d" "$dest" || continue\n',
        '    old="${dest}.rc-old"\n'
        '    [ -e "$dest" ] || [ -L "$dest" ] && mv "$dest" "$old" 2>/dev/null || true\n'
        '    ln -s "$d" "$dest" 2>/dev/null || cp -r "$d" "$dest"\n'
        '    [ -e "$old" ] && mv "$old" "${old}.trash" 2>/dev/null || true\n',
        "cursor-three-runs",
    ),
    (
        "scripts-3 own content deleted",
        '    if diff -rq "$src" "$dest" >/dev/null 2>&1; then',
        "    if true; then",
        "user-content-preserved",
    ),
    (
        "scripts-4 no backup before overwrite",
        '  if [ -f "$dest" ] && ! cmp -s "$dest" "$tmp"; then',
        "  if false; then",
        "config-backups",
    ),
    (
        "scripts-5 wired line unconditional",
        '  if [ "$hooks_ok" = 1 ]; then',
        "  if true; then",
        "copilot-hooks-failure",
    ),
    (
        "scripts-6 unknown flag swallowed",
        '      -*)\n        warn "unknown flag for install: $1"',
        '      -*) shift ;;\n      --never-a-real-flag)\n        warn "unknown flag for install: $1"',
        "parser",
    ),
    (
        "scripts-13 lane aborts on a bad .cursorignore",
        '    warn ".cursorignore was NOT updated',
        '    exit 1\n    warn ".cursorignore was NOT updated',
        "cursor-malformed-ignore",
    ),
)


def _real_rc_digest() -> dict:
    home = Path(os.path.expanduser("~"))
    out = {}
    for name in (".bashrc", ".zshrc", ".bash_profile", ".profile"):
        p = home / name
        out[name] = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    return out


def run_cases(text: str, only: list | None = None) -> list:
    scratch = Path(tempfile.mkdtemp(prefix="rc-installer-lanes-"))
    fails = []
    try:
        for name, fn in CASES.items():
            if only and name not in only:
                continue
            try:
                got = fn(scratch, text)
            except Exception as exc:  # noqa: BLE001 — a crashed case is a failed case
                got = [f"{name}: crashed: {type(exc).__name__}: {exc}"]
            fails += [f"[{name}] {f}" for f in got]
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return fails


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description="end-to-end lane tests for scripts/ravenclaude")
    ap.add_argument("--check", action="store_true", help="run every case (the default)")
    ap.add_argument("--case", action="append", help="run only the named case (repeatable)")
    ap.add_argument("--installer", help="test this installer file instead of scripts/ravenclaude")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    args = ap.parse_args(argv[1:])

    if args.must_fail_convention:
        print(f"must-fail-teeth-exit: {TEETH_EXIT}")
        return 0

    real_before = _real_rc_digest()
    src = Path(args.installer) if args.installer else INSTALLER
    text = src.read_text(encoding="utf-8")

    if args.must_fail:
        missed = []
        for label, anchor, repl, case in MUTANTS:
            n = text.count(anchor)
            if n != 1:
                missed.append(f"{label}: anchor found {n}x (want 1) — mutant not built")
                continue
            fails = run_cases(text.replace(anchor, repl, 1), only=[case])
            status = "caught" if fails else "NOT CAUGHT"
            print(f"  {status:<11} {label}  ({case}: {len(fails)} finding(s))")
            if not fails:
                missed.append(label)
        if _real_rc_digest() != real_before:
            print("FAIL: the operator's real shell rc files changed during the run")
            return 1
        if missed:
            print("installer-lanes --must-fail: teeth NOT proven:")
            for m in missed:
                print(f"  - {m}")
            return 1
        print(
            f"installer-lanes --must-fail: all {len(MUTANTS)} mutants caught. "
            f"Exiting {TEETH_EXIT}, the declared teeth code."
        )
        return TEETH_EXIT

    fails = run_cases(text, only=args.case)
    if _real_rc_digest() != real_before:
        fails.append("ISOLATION: the operator's real ~/.bashrc / ~/.zshrc changed during the run")
    names = args.case or list(CASES)
    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        print(f"\ninstaller lanes: {len(fails)} failure(s) across {len(names)} case(s)")
        return 1
    print(f"installer lanes OK — {len(names)} case(s) passed: {', '.join(names)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
