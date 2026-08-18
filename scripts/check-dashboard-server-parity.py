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

# `\w` does NOT match `-`, so the old `/__\w+` silently TRUNCATED every
# hyphenated endpoint: `/__concern-stats` was compared as `/__concern`, and
# `/__knowledge-health` as `/__knowledge` (multi-host audit MH-33). Two endpoints
# differing only after a hyphen therefore compared as identical, which is exactly
# the drift this gate exists to catch — and the truncation was visible in the
# gate's own PASS output the whole time, reading as if those were the real names.
_ENDPOINT_RE = re.compile(r"/__[\w-]+")

# Names that legitimately differ between the two copies — the root server uses
# REPO_ROOT (the marketplace clone), the plugin server uses PROJECT_ROOT (the
# consumer repo). Every Mímir-style "byte-identical helper" docstring in
# serve-dashboards.py cites this as the one allowed variance. The body-diff
# check normalizes these out before comparing.
_ALLOWED_VARIANCE = [("REPO_ROOT", "PROJECT_ROOT")]

# Functions whose bodies the SKILL contracts mark as "duplicated byte-identically
# in both server copies." The body-diff check enforces that contract directly,
# not just the endpoint-name surface (Gate 32 historically caught a renamed
# endpoint but not a per-card behaviour drift inside a helper). Pattern: every
# `_read_<card>` and the cross-card `_mimir_*` helpers (the universal scrubber +
# encoded-path resolver — the contract surfaces them as load-bearing).
_BODY_DIFF_PREFIXES = ("_read_", "_mimir_")

# Exact-name body-diff contract (FORGE dashboard-consumption, PB-1). The launch
# lane rewrites the port/reclaim/bind/lifetime path in BOTH server copies; those
# functions are NOT `_read_*`/`_mimir_*`, so the prefix filter above cannot see
# them, and a one-copy edit to (say) `_reclaim_port` would ship different bind
# behaviour to consumers silently — the exact drift class behind the v0.205.3
# incident. These three are already byte-identical today, so naming them is green
# at zero cost. CODE-SHAPE RULE (binding on the L lane): any NEW port/bind/idle
# logic must ship as a module-level named function present in BOTH copies and be
# added here — logic left inline in `main()` is by construction ungated. When the
# L lane lands `_default_bind()` and the idle-expiry reaper, append their names.
_BODY_DIFF_NAMES = (
    "_port_holder_pids",
    "_holder_cwd",
    "_reclaim_port",
    "_default_bind",
    "_idle_reaper",
)

# NOT compared — `main()` legitimately DIVERGES between the two copies in seven
# documented ways, so byte-diffing it is unkeepable (this is why the contract is a
# named-function list, not a whole-main diff): (1) the root serves the repo root +
# a landing path while the plugin serves PLUGIN_DIR/DASH_PATH; (2) the root accepts
# --project-root/--validate, the plugin does not; (3) the root carries the
# marketplace-write refusal guard; (4) root-only LAN/QR `_lan_ip` phone-URL block;
# (5) plugin-only `_bind_server` helper; (6) the `/__run` banner wording differs;
# (7) Codespace-refusal wording differs. New drift-prone logic goes in a named
# function above, never inline in main().

_DEF_RE = re.compile(r"^def\s+(\w+)\s*\(", re.MULTILINE)
# Module-level boundaries: `def NAME(` OR `class NAME(`. The body-extractor uses
# this to stop at the NEXT top-level boundary (not just the next def), so a
# `_read_*` helper followed by `class DashboardHandler` slices correctly instead
# of swallowing the entire class block (which would conflate every method drift
# into one false-positive on the preceding reader helper).
_BOUNDARY_RE = re.compile(r"^(?:def\s+\w+\s*\(|class\s+\w+\b)", re.MULTILINE)


def endpoints(path: Path) -> set[str]:
    """Every distinct /__<name> token that appears anywhere in the file."""
    return set(_ENDPOINT_RE.findall(path.read_text(encoding="utf-8")))


def _normalize(body: str) -> str:
    """Apply the documented variance whitelist so the byte-diff doesn't lie
    about the one allowed difference (REPO_ROOT vs PROJECT_ROOT)."""
    out = body
    for root_name, plugin_name in _ALLOWED_VARIANCE:
        # Normalize both directions to a single token so the diff is symmetric.
        out = out.replace(root_name, "__VAR_ROOT__").replace(plugin_name, "__VAR_ROOT__")
    return out


def extract_functions(
    src: str, prefixes: tuple[str, ...], names: tuple[str, ...] = ()
) -> dict[str, str]:
    """Return {name: body_text} for every top-level `def NAME(...)` whose name
    starts with one of the given prefixes OR is an exact member of `names`. The
    body is the slice from the `def`
    line up to (but not including) the next top-level `def` / `class` line, or
    end-of-file. Returns the literal source, including the `def` signature line
    — enough for a meaningful byte-diff.

    Top-level here means "starts at column 0", which excludes method `def`s
    inside the handler class (they're indented). That's correct for this use
    case: the contract surface is the module-level reader helpers, not the
    HTTP-handler methods (those are separately covered by the endpoint-name
    check above + Gate 49's both-copies-present assertion).
    """
    out: dict[str, str] = {}
    boundaries = [m.start() for m in _BOUNDARY_RE.finditer(src)]
    for m in _DEF_RE.finditer(src):
        name = m.group(1)
        if not (any(name.startswith(p) for p in prefixes) or name in names):
            continue
        start = m.start()
        # Find the next module-level boundary STRICTLY after this def's start
        # (defs OR class definitions — a `_read_*` followed by `class Handler`
        # must slice at the class, not at the next module def far below).
        end = next((b for b in boundaries if b > start), len(src))
        # Trim trailing blank lines so cosmetic whitespace drift doesn't false-
        # positive.
        body = src[start:end].rstrip() + "\n"
        out[name] = body
    return out


def unguarded_get_handlers(path: Path) -> list[str]:
    """Every `/__` GET endpoint whose handler does NOT call `_local_request_ok()`.

    The server carries this invariant as a COMMENT in do_GET:

        "Any NEW data-returning GET endpoint added here MUST call
         self._local_request_ok() first — do not let it ride the static path."

    Nothing enforced it (multi-host audit MH-33). That guard is the
    DNS-rebinding / cross-origin defense: without it, a page on any other origin
    can read the endpoint's JSON. A comment is not a control, and "the next person
    will remember" is not a security posture — especially on a surface where five
    new endpoints were added in a single day.

    Deliberately a STATIC check on the dispatch table rather than a live request:
    it runs in CI with no server, and it fails on the shape that actually recurs —
    a new handler added without the guard line.
    """
    text = path.read_text(encoding="utf-8")
    # SCOPE TO do_GET's BODY ONLY. Scanning the whole file conflates GET with POST:
    # /__classify and /__save are dispatched from do_POST and are guarded by the CSRF
    # check, not by _local_request_ok(). The first version of this check scanned
    # globally, flagged the POST-only /__classify, and looked exactly like a real
    # security hole — it was a broken check. Diagnose before concluding.
    m_get = re.search(r"\n    def do_GET\(self\):.*?(?=\n    def )", text, re.S)
    if not m_get:
        return ["do_GET not found — the dispatch table moved; this check needs updating"]
    get_body = m_get.group(0)
    # `if self.path.startswith("/__x"):` (or `== "/__x"`) followed by `self._handle_y()`
    dispatch = re.findall(
        r'self\.path(?:\.startswith|\s*==)\s*\(?\s*"(/__[\w-]+)"\)?\s*:\s*\n\s*self\.(_handle_[\w]+)\(',
        get_body,
    )
    unguarded = []
    for endpoint, handler in dispatch:
        m = re.search(rf"\n    def {re.escape(handler)}\(.*?(?=\n    def |\nclass |\Z)", text, re.S)
        if not m:
            unguarded.append(f"{endpoint} -> {handler} (handler not found)")
            continue
        if "_local_request_ok()" not in m.group(0):
            unguarded.append(f"{endpoint} -> {handler}")
    return unguarded


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--root-server",
        default=str(ROOT_SERVER),
        help="path to the root dev server (default: scripts/serve-dashboards.py)",
    )
    ap.add_argument(
        "--plugin-server", default=str(PLUGIN_SERVER), help="path to the bundled plugin server"
    )
    args = ap.parse_args()

    root_path = Path(args.root_server)
    plugin_path = Path(args.plugin_server)
    for p in (root_path, plugin_path):
        if not p.is_file():
            print(f"ERROR: server file not found: {p}", file=sys.stderr)
            return 2

    # MH-33 — enforce the do_GET invariant the server only documented.
    guard_failures = []
    for label, sp in (("root", root_path), ("plugin", plugin_path)):
        for bad in unguarded_get_handlers(sp):
            guard_failures.append(f"{label}: {bad}")

    root = endpoints(root_path)
    plugin = endpoints(plugin_path)
    expected = root - INTENTIONALLY_EXCLUDED
    missing = expected - plugin

    # The dashboard sub-app (folded natively into index.html, also shipped as the
    # standalone plugin dashboard.html) uses /__csrf for its served-vs-static
    # detection + CSRF bootstrap. If that endpoint is ever renamed or dropped,
    # the live tabs silently fall back to empty states. Fail the gate loudly
    # here so the rename surfaces immediately.
    if "/__csrf" not in plugin:
        print(
            "DRIFT: the bundled plugin dashboard server no longer exposes /__csrf — "
            "the dashboard's served-mode detection + CSRF bootstrap depend on this "
            "endpoint. If it was intentionally renamed, update both serve-dashboards.py "
            "copies AND the dashboard JS in scripts/generate-dashboards.py (search "
            "`/__csrf`).",
            file=sys.stderr,
        )
        return 1

    if guard_failures:
        print(
            "UNGUARDED ENDPOINT(S): a data-returning GET handler does not call "
            "self._local_request_ok(). That guard is the DNS-rebinding / cross-origin "
            "defense — without it any other origin can read the endpoint's JSON.",
            file=sys.stderr,
        )
        for g in guard_failures:
            print(f"  - {g}", file=sys.stderr)
        print(
            "  Fix: add `if not self._local_request_ok(): return` as the handler's "
            "FIRST statement, as _handle_read does. do_GET documents this invariant; "
            "MH-33 made it enforced.",
            file=sys.stderr,
        )
        return 1

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

    # ── Body-diff (Mímir SKILL RM6 follow-up) ────────────────────────────────
    # The endpoint-name check above catches the /__saga class of drift — an
    # endpoint that's entirely missing from the consumer build. It does NOT
    # catch per-card behavioural drift inside a "byte-identical in both copies"
    # helper. The Mímir SKILL § "SERVER-PARITY DISCIPLINE" explicitly flags
    # this as a failure mode: an asymmetric edit silently passes the name-set
    # check while the readers diverge, and the consumer's dashboard renders
    # different bytes than the dev server. Same pattern as Norns / Heimdall /
    # Víðarr — every Norse reader-helper docstring contracts byte-identity.
    #
    # This stage extracts every top-level _read_<card> + _mimir_* function
    # body from both files, normalizes the documented REPO_ROOT vs PROJECT_ROOT
    # variance, and asserts byte-identity. Functions that exist in only ONE
    # copy are flagged as drift (a new helper authored in one file but not
    # mirrored is exactly the contract violation the gate is for).
    root_src = root_path.read_text(encoding="utf-8")
    plugin_src = plugin_path.read_text(encoding="utf-8")
    root_fns = extract_functions(root_src, _BODY_DIFF_PREFIXES, _BODY_DIFF_NAMES)
    plugin_fns = extract_functions(plugin_src, _BODY_DIFF_PREFIXES, _BODY_DIFF_NAMES)

    body_drift: list[str] = []

    # CSRF-binding invariant (PB-1): both copies must key the allow-lists on the
    # ACTUALLY-BOUND port (`actual_port`), never `args.port`. A fallback bind
    # (port 8000 held → walk to 8001) makes `args.port` != the bound port, so an
    # allow-list keyed on `args.port` would reject every same-origin /__save on
    # the fallback port — the DNS-rebinding defense collapsed into a self-DoS.
    # Green today (v0.205.3 keyed both on actual_port); this pins it so a later
    # port edit cannot silently regress it in either copy.
    # FORMAT-AGNOSTIC (2026-08-18): ruff-format may reflow `_ALLOWED_HOSTS = { ... }`
    # across several physical lines, so an `args.port` member can land on a
    # continuation line that does NOT itself contain `_ALLOWED_HOSTS`. A per-line
    # scan silently missed that. Track the `{...}` brace span of each allow-list
    # assignment (plus the naming line, which covers a single-line assignment or an
    # `_ALLOWED_*.add(...)` call) and flag `args.port` anywhere inside it.
    for label, src_text in (("root", root_src), ("plugin", plugin_src)):
        brace_depth = 0  # > 0 while inside a multi-line `_ALLOWED_* = { ... }` block
        for ln in src_text.splitlines():
            names_allowlist = "_ALLOWED_HOSTS" in ln or "_ALLOWED_ORIGINS" in ln
            if (names_allowlist or brace_depth > 0) and "args.port" in ln:
                body_drift.append(
                    f"{label} serve-dashboards.py keys an allow-list on `args.port`, "
                    f"not `actual_port`: {ln.strip()!r}. A fallback bind would then "
                    f"reject every same-origin /__save (CSRF self-DoS). Use actual_port."
                )
            if names_allowlist or brace_depth > 0:
                brace_depth += ln.count("{") - ln.count("}")
                if brace_depth < 0:
                    brace_depth = 0
    only_in_root = sorted(set(root_fns) - set(plugin_fns))
    only_in_plugin = sorted(set(plugin_fns) - set(root_fns))
    if only_in_root:
        body_drift.append(
            f"functions present in root ONLY (not mirrored to plugin copy): {only_in_root}"
        )
    if only_in_plugin:
        body_drift.append(
            f"functions present in plugin ONLY (not in root dev server): {only_in_plugin}"
        )
    for name in sorted(set(root_fns) & set(plugin_fns)):
        if _normalize(root_fns[name]) != _normalize(plugin_fns[name]):
            body_drift.append(
                f"body of `{name}` differs between root and plugin copies (after "
                f"normalizing REPO_ROOT vs PROJECT_ROOT). Re-sync them — the SKILL "
                f"contracts these helpers as byte-identical."
            )

    if body_drift:
        print(
            "BODY DRIFT: the bundled plugin server's reader helpers have drifted "
            "from the root dev server's. The SKILL contracts mark these helpers as "
            "byte-identical (modulo the documented REPO_ROOT → PROJECT_ROOT rename), "
            "so an asymmetric edit silently ships different bytes to consumers.",
            file=sys.stderr,
        )
        for line in body_drift:
            print(f"  - {line}", file=sys.stderr)
        print(
            "  Fix: re-sync each named helper across both serve-dashboards.py copies "
            "and re-run this gate. If a divergence is intentional, document the new "
            "variance in scripts/check-dashboard-server-parity.py _ALLOWED_VARIANCE "
            "and update the SKILL contract.",
            file=sys.stderr,
        )
        return 1

    body_diff_count = len(set(root_fns) & set(plugin_fns))
    print(
        f"OK: plugin server exposes all {len(expected)} non-excluded root endpoint(s) "
        f"{sorted(expected)}; intentional omissions: {sorted(INTENTIONALLY_EXCLUDED)}; "
        f"{body_diff_count} reader-helper(s) body-identical."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
