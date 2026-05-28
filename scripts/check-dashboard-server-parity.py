#!/usr/bin/env python3
"""check-dashboard-server-parity.py — fail if the bundled plugin dashboard server
has drifted behind the root dev server's endpoint surface.

There are two `serve-dashboards.py` files:

  - scripts/serve-dashboards.py                          (root — the dev server)
  - plugins/ravenclaude-core/scripts/serve-dashboards.py (the locked-down copy that
                                                           ships in the plugin and is
                                                           what `/dashboard` launches)

The plugin copy is hand-maintained, NOT generated, so the two can silently diverge.
They are allowed to differ in exactly ONE documented way: the consumer build
intentionally omits `/__run` (the Copilot install/update shell action has no place in
a posture editor a client launches). Every OTHER `/__` endpoint the root server
exposes MUST also exist in the plugin server — otherwise the shipped dashboard.html
(which both servers serve) calls an endpoint the consumer's bundled server doesn't
have. That is exactly the `/__saga` gap that shipped in v0.52.0 and was fixed in
v0.53.1: the Review-log tab fetched `/__saga`, the bundled server never served it, and
every consumer saw "Could not reach /__saga". This gate makes that class of drift fail
CI instead of reaching a consumer.

The check is one-directional: root's endpoint set (minus the documented exclusions)
must be a subset of the plugin server's. A token appearing only in a comment/docstring
still counts as "present" — the realistic failure mode this guards is an endpoint that
is *entirely absent* from the plugin file, which the token-set comparison catches.

Exit 0 when parity holds, 1 (naming the missing endpoint) when it does not.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ROOT_SERVER = REPO_ROOT / "scripts" / "serve-dashboards.py"
PLUGIN_SERVER = REPO_ROOT / "plugins" / "ravenclaude-core" / "scripts" / "serve-dashboards.py"

# Endpoints the consumer build intentionally drops — documented in the plugin
# server's own module docstring. Keep this list in lockstep with that rationale.
INTENTIONALLY_EXCLUDED = {"/__run"}

_ENDPOINT_RE = re.compile(r"/__\w+")


def endpoints(path: Path) -> set[str]:
    """Every distinct /__<name> token that appears anywhere in the file."""
    return set(_ENDPOINT_RE.findall(path.read_text(encoding="utf-8")))


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--root-server", default=str(ROOT_SERVER),
                    help="path to the root dev server (default: scripts/serve-dashboards.py)")
    ap.add_argument("--plugin-server", default=str(PLUGIN_SERVER),
                    help="path to the bundled plugin server")
    args = ap.parse_args()

    root_path = Path(args.root_server)
    plugin_path = Path(args.plugin_server)
    for p in (root_path, plugin_path):
        if not p.is_file():
            print(f"ERROR: server file not found: {p}", file=sys.stderr)
            return 2

    root = endpoints(root_path)
    plugin = endpoints(plugin_path)
    expected = root - INTENTIONALLY_EXCLUDED
    missing = expected - plugin

    if missing:
        print(
            "DRIFT: the bundled plugin dashboard server is missing endpoint(s) the root "
            f"server exposes: {sorted(missing)}",
            file=sys.stderr,
        )
        print(f"  root server:   {sorted(root)}", file=sys.stderr)
        print(f"  plugin server: {sorted(plugin)}", file=sys.stderr)
        print(
            "  Mirror each missing endpoint into "
            "plugins/ravenclaude-core/scripts/serve-dashboards.py "
            "(translate REPO_ROOT -> PROJECT_ROOT; keep /__run out). "
            "This is the /__saga-drift guard — see the script docstring.",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK: plugin server exposes all {len(expected)} non-excluded root endpoint(s) "
        f"{sorted(expected)}; intentional omissions: {sorted(INTENTIONALLY_EXCLUDED)}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
