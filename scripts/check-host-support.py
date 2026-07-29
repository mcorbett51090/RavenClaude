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
    check-host-support.py                 # full gate: map completeness + generator derivation
    check-host-support.py <path.json>     # map completeness only, against an arbitrary copy
                                          # (this is how the must-fail teeth drive it)

Exit 0 = pass. Exit 1 = a real defect, with the reason on stderr.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_MAP = _REPO / "plugins" / "ravenclaude-core" / "knowledge" / "host-support.json"


def _fail(msg: str) -> int:
    print(f"host-support: {msg}", file=sys.stderr)
    return 1


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


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        # Teeth mode: validate an arbitrary (usually deliberately-broken) copy.
        return check_map(Path(argv[1]))
    rc = check_map(_MAP)
    if rc:
        return rc
    return check_generator_derives()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
