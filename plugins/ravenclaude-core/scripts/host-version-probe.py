#!/usr/bin/env python3
"""host-version-probe — bounded, per-host `--version` subprocess probe.

Direct generalization of `scripts/ravenclaude`'s `copilot_version_check()`: same
`command -v` guard, same first-x.y.z-substring extraction (tolerant of build
qualifiers and v-prefixes), same fail-to-`None`-never-throw contract.

USED ONLY BY dependency-sweep.py's manual-invocation refresh path (T4 of
dependency-update-sweep's plan.md). NEVER imported by capability-orientation.py —
that file's SessionStart banner is a zero-subprocess surface by design, and this
module's whole purpose is to keep the one place that DOES need a live version
reading isolated from it.
"""

from __future__ import annotations

import re
import shutil
import subprocess

# host_id -> the binary this repo's installer / that host's own CLI actually
# exposes on PATH. Read live from host-support.json at call time for the KEY
# SET (never hand-duplicated here); this table only supplies the binary name
# for a key that host-support.json defines. A host with no real CLI binary
# (e.g. a browser-hosted product) is intentionally absent from this table and
# probe_host_version() returns None for it via the KeyError branch below.
_HOST_BINARY = {
    "claude-code": "claude",
    "copilot": "copilot",
    "codex": "codex",
    "cursor": "cursor",
    "gemini": "gemini",
    "aider": "aider",
    # windsurf: reported renamed to Devin Desktop (2026-06-02, AGENTS.md);
    # no confirmed CLI binary name — deliberately absent, not guessed.
}

_VERSION_RE = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")


def probe_host_version(host_id: str, timeout_s: float = 2.0) -> str | None:
    """Return the installed x.y.z version string for `host_id`, or None.

    Never raises. Every failure mode (binary absent, hung process, unparseable
    output, timeout) degrades to None — the same fail-to-None-never-throw
    contract `copilot_version_check()` uses, generalized across hosts.
    """
    binary = _HOST_BINARY.get(host_id)
    if binary is None:
        return None
    if shutil.which(binary) is None:
        return None
    try:
        proc = subprocess.run(
            [binary, "--version"],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    raw = (proc.stdout or "") + (proc.stderr or "")
    first_line = raw.splitlines()[0] if raw.splitlines() else ""
    match = _VERSION_RE.search(first_line) or _VERSION_RE.search(raw)
    if match is None:
        return None
    return match.group(0)


def _self_test() -> int:
    import os
    import stat
    import sys
    import tempfile

    failures = []
    ran = []

    def check(name: str, cond: bool) -> None:
        ran.append(name)
        if not cond:
            failures.append(name)

    # 1. absent binary -> None
    check("absent-host-key", probe_host_version("not-a-real-host") is None)

    # helper: build a fake executable on a temp dir and prepend it to PATH
    def fake_binary(host_id: str, script: str):
        tmpdir = tempfile.mkdtemp(prefix="hvp-selftest-")
        binary_name = _HOST_BINARY[host_id]
        path = os.path.join(tmpdir, binary_name)
        with open(path, "w") as f:
            f.write(script)
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        return tmpdir

    orig_path = os.environ.get("PATH", "")

    try:
        # 2. plain x.y.z version
        tmpdir = fake_binary("claude-code", "#!/bin/sh\necho '1.2.3'\n")
        os.environ["PATH"] = tmpdir + os.pathsep + orig_path
        check("plain-version", probe_host_version("claude-code") == "1.2.3")

        # 3. build-qualified version -> first three components
        tmpdir = fake_binary("codex", "#!/bin/sh\necho 'codex 1.0.52.3'\n")
        os.environ["PATH"] = tmpdir + os.pathsep + orig_path
        check("build-qualified", probe_host_version("codex") == "1.0.52")

        # 4. v-prefixed + suffixed version
        tmpdir = fake_binary("gemini", "#!/bin/sh\necho 'v1.0.52-beta.1'\n")
        os.environ["PATH"] = tmpdir + os.pathsep + orig_path
        check("v-prefixed-suffixed", probe_host_version("gemini") == "1.0.52")

        # 5. unparseable output -> None, never throws
        tmpdir = fake_binary("cursor", "#!/bin/sh\necho 'no version here'\n")
        os.environ["PATH"] = tmpdir + os.pathsep + orig_path
        check("unparseable", probe_host_version("cursor") is None)

        # 6. hung binary -> times out within the bound, returns None
        tmpdir = fake_binary("aider", "#!/bin/sh\nsleep 10\n")
        os.environ["PATH"] = tmpdir + os.pathsep + orig_path
        import time

        start = time.monotonic()
        result = probe_host_version("aider", timeout_s=0.5)
        elapsed = time.monotonic() - start
        check("hung-binary-returns-none", result is None)
        check("hung-binary-bounded", elapsed < 2.0)

        # 7. non-zero exit but still parseable stderr output
        tmpdir = fake_binary("copilot", "#!/bin/sh\necho 'copilot 1.0.70' >&2\nexit 1\n")
        os.environ["PATH"] = tmpdir + os.pathsep + orig_path
        check("nonzero-exit-still-parsed", probe_host_version("copilot") == "1.0.70")

    finally:
        os.environ["PATH"] = orig_path

    if failures:
        print(f"FAIL: {failures}", file=sys.stderr)
        return 1
    print(f"host-version-probe self-test: {len(ran)} checks, 0 failures")
    return 0


if __name__ == "__main__":
    import sys

    if "--self-test" in sys.argv:
        sys.exit(_self_test())
    print("usage: host-version-probe.py --self-test", file=sys.stderr)
    sys.exit(2)
