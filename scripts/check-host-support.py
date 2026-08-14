#!/usr/bin/env python3
"""Gate 154 — knowledge/host-support.json is the single source of truth for which
RavenClaude components actually run on which host.

Two ways that map can rot, both SILENT, so both are checked here:

  (a) a host or component is added and the matrix is left with a hole. A missing
      cell reads as "no answer", and every surface that consumes the map would
      quietly treat that as unsupported (or crash on the KeyError). An unsupported
      cell that does not say WHY is the same defect one level down: it tells a
      reader "no" and gives them nothing to act on, which is how "Codex is
      unsupported" survived as a fact when the real answer was "nothing wires it."

  (b) the map and its consumers drift apart — which is exactly the duplication
      this file was created to remove. `generate-dashboards.py` must DERIVE its
      host list from the map, never restate it.

Extracted from an inline heredoc in `audit-gates.sh` on 2026-07-28 (MH-21
follow-up). The extraction is the point: the check previously existed twice in
that file — once as the real assertion and once, abridged, inside its own
must-fail teeth — so the teeth could drift from the thing they were proving. One
implementation, three call sites (main sequence, teeth, `--check 154`).

Usage:
    check-host-support.py                 # full gate: map + derivation + generated-output scan
    check-host-support.py <path.json>     # map completeness only, against an arbitrary copy
                                          # (this is how the must-fail teeth drive it)
    check-host-support.py --scan-generated <root>
                                          # generated-output scan only (MH-27 teeth)

Exit 0 = pass. Exit 2 = a real defect, with the reason on stderr.
Exit 1 is never used for a finding — the harness treats exit 1 as a
non-blocking error (the fail-open this gate exists to close).
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_MAP = _REPO / "plugins" / "ravenclaude-core" / "knowledge" / "host-support.json"

# PR 10 / Gate 207 — the silent-disarm class. Required on every host so a new
# --host lane cannot ship without declaring how (or whether) its guardrails
# re-arm after an update. Consumed by `_rc_rearm_notice`.
_ACTIVATION_GATES = frozenset({"hash_trust", "version_floor", "none"})


def _fail(msg: str) -> int:
    print(f"host-support: {msg}", file=sys.stderr)
    return 2


def check_activation_gates(data: dict) -> int:
    """Every host declares a valid activation_gate (PR 10 schema pin)."""
    hosts = data.get("hosts") or {}
    for name, info in hosts.items():
        if not isinstance(info, dict):
            return _fail(f"host '{name}' must be an object")
        gate = info.get("activation_gate")
        if gate not in _ACTIVATION_GATES:
            return _fail(
                f"host '{name}' missing/invalid activation_gate {gate!r} "
                f"(want hash_trust | version_floor | none)"
            )
    return 0


def check_map(path: Path) -> int:
    """Every host x component cell answered, every 'no' justified."""
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        return _fail(f"unreadable/invalid JSON at {path}: {exc}")

    hosts = set(data.get("hosts") or {})
    if not hosts:
        return _fail("no hosts declared")
    components = data.get("components") or {}
    if not components:
        return _fail("no components declared")

    ag = check_activation_gates(data)
    if ag:
        return ag

    for name, comp in components.items():
        # `what` is prose describing the component; every OTHER key must be a host.
        cells = {k for k in comp if k != "what"}
        missing = hosts - cells
        stray = cells - hosts
        if missing:
            return _fail(f"component '{name}' has no answer for: {sorted(missing)}")
        if stray:
            return _fail(f"component '{name}' has cells for unknown hosts: {sorted(stray)}")

        for host in sorted(hosts):
            cell = comp[host]
            if not isinstance(cell.get("supported"), bool):
                return _fail(f"'{name}.{host}'.supported must be a boolean answer")
            if cell["supported"] is False and not cell.get("blocked_by"):
                return _fail(f"'{name}.{host}' is unsupported but does not say WHY (blocked_by)")
    return 0


def check_generator_derives() -> int:
    """generate-dashboards.py must derive its host list, not restate it."""
    gen = _REPO / "scripts" / "generate-dashboards.py"
    try:
        spec = importlib.util.spec_from_file_location("gd", gen)
        module = importlib.util.module_from_spec(spec)
        # The generator resolves sibling paths relative to its own location, so it
        # imports cleanly regardless of cwd — but keep scripts/ importable for any
        # module-level sibling import it does.
        sys.path.insert(0, str(_REPO / "scripts"))
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 — any import failure is a gate failure
        return _fail(f"could not import generate-dashboards.py: {exc}")

    data = json.loads(_MAP.read_text())
    want = tuple(
        data["hosts"][h]["label"]
        for h in data["hosts"]
        if data["components"]["hooks"][h]["supported"] is True
    )
    got = getattr(module, "_HOOK_CAPABLE_HOSTS", None)
    if got != want:
        return _fail(f"_HOOK_CAPABLE_HOSTS is {got!r}, but the map says {want!r} — restated, not derived")
    return 0


# MH-27: a generated Copilot manifest listed "Slash commands: /a, /b" on a host
# the plugin (and host-support.json) says has none. The inventory phrase is the
# positive advertisement; a sentence that *denies* slash commands is not this
# shape. Host dirs are derived from the map's host keys — never a hand-typed list.
_SLASH_INVENTORY = re.compile(r"Slash commands:\s*/")
_GENERATED_TEXT = frozenset({".json", ".md", ".txt", ".html", ".toml"})


def check_generator_output(root: Path) -> int:
    """Generated per-host trees must not advertise a component the map forbids.

    Walks ``plugins/ravenclaude-core/<host-key>/`` for every host in
    host-support.json. A missing directory is not a finding (that host has no
    generated projection). An unreadable map fails closed.
    """
    map_path = root / "plugins" / "ravenclaude-core" / "knowledge" / "host-support.json"
    try:
        data = json.loads(map_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return _fail(f"unreadable/invalid JSON at {map_path}: {exc}")

    hosts = data.get("hosts") or {}
    if not hosts:
        return _fail("no hosts declared")
    components = data.get("components") or {}
    slash_comp = components.get("slash_commands") or {}

    findings: list[str] = []
    scanned = 0
    for host_key in hosts:
        gen_dir = root / "plugins" / "ravenclaude-core" / host_key
        if not gen_dir.is_dir():
            continue
        cell = slash_comp.get(host_key) or {}
        if cell.get("supported") is not False:
            continue
        for path in sorted(gen_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in _GENERATED_TEXT:
                continue
            scanned += 1
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as exc:
                return _fail(f"unreadable generated file {path}: {exc}")
            if _SLASH_INVENTORY.search(text):
                rel = path.relative_to(root)
                findings.append(
                    f"{rel}: advertises a slash-command inventory but "
                    f"host-support.json slash_commands.{host_key}.supported is false"
                )
    if findings:
        return _fail("; ".join(findings))
    # A root with no generated host trees is fine (teeth fixtures plant one).
    # scanned is informational only — an empty walk is not a pass-by-skip
    # because the live tree has copilot/ and the MH-27 teeth plant their own.
    del scanned
    return 0


def main(argv: list[str]) -> int:
    if "--scan-generated" in argv:
        idx = argv.index("--scan-generated")
        root = Path(argv[idx + 1]) if idx + 1 < len(argv) else _REPO
        return check_generator_output(root)
    if len(argv) > 1 and not argv[1].startswith("-"):
        # Teeth mode: validate an arbitrary (usually deliberately-broken) copy.
        return check_map(Path(argv[1]))
    rc = check_map(_MAP)
    if rc:
        return rc
    rc = check_generator_derives()
    if rc:
        return rc
    return check_generator_output(_REPO)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
