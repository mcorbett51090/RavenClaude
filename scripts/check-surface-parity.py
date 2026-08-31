#!/usr/bin/env python3
"""Gate 200 — where two surfaces must agree, assert them against EACH OTHER.

A gate that checks each surface independently against a hardcoded constant
cannot catch the surfaces disagreeing. That shape has shipped here three times:
the portal router not owning a route; the portal owning it but homing it
somewhere else; and a hand-maintained twin server drifting in the half nothing
compared. In each case both surfaces passed their own assertion.

The engine is a pair of functions per instance:

    derive_fn  — read the EXPECTATION out of one surface
    assert_fn  — check the OTHER surface against exactly that

Neither side is a constant, so neither can quietly become the wrong answer.

One instance is registered:

  route-placement (P11) — for EVERY nav route, the destination the standalone
    `ds-nav` chrome homes it under must equal the destination the portal's
    router homes it under. Gate 144 already does this for ONE route; a
    placement bug on any other route is invisible until a user hits a dead end.

⛔ WHAT THIS DELIBERATELY DOES NOT COVER, and why.

A twin-server instance was built and REMOVED. It asserted that the two
`serve-dashboards.py` copies expose the same CLI flags and request routes.
Every finding it produced was BY DESIGN, and the bundled copy says so in its
own source: `- **No /__run endpoint.**` (its `/__runs` is a different,
plural endpoint), while `--project-root` and `--validate` are consumer-scoping
features the root dev server has no use for. The two copies are deliberately
NOT surface-identical, so surface-equality is the WRONG ASSERTION — it floods
on intentional differences, and a flooding gate gets switched off.

The real twin defect (the bundled copy once lacked port fallback, `--no-open`,
browser auto-open and the root redirect while the docs described all four) is
still ungated. It needs a TARGETED check of the specific features each copy's
docs claim — not a blanket equality assertion — and that is its own build unit.
Recorded here so nobody "completes" this gate by adding the wrong half back.

Exit codes: 0 = the surfaces agree; 2 = a disagreement, or a surface could not
be read. Never 1.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

STANDALONE = Path("plugins/ravenclaude-core/dashboard.html")
PORTAL = Path("index.html")


class Mismatch(NamedTuple):
    instance: str
    subject: str
    detail: str

    def render(self) -> str:
        return f"  [{self.instance}] {self.subject}\n      {self.detail}"


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise SystemExit(f"surface-parity: cannot read {p}: {exc} — refusing to pass vacuously")


# ── Instance 1: route placement (P11) ───────────────────────────────────────
# derive: the standalone `ds-nav` chrome is carried by BOTH surfaces (the portal
# folds the standalone payload), so it is a single source of truth rather than a
# hardcoded expectation.

# The real chrome shape, read out of the generator's output rather than guessed:
# a `<div class="ds-label">Group</div>` opens a group, and every `ds-sub` link
# until the next label belongs to it. Gate 144 uses the same anchors for one
# route; this generalises it to all of them.
DS_LABEL = re.compile(r'<div class="ds-label">(.*?)</div>', re.S)
DS_SUB = re.compile(r'<a class="ds-sub" href="#/([a-z0-9-]+)"')

# The sidebar shows human labels; the router uses destination ids. This map is
# the one place the two vocabularies meet, and it is asserted non-empty below.
GROUP_TO_DESTINATION = {
    "control": "control",
    "activity": "activity",
    "guardrails": "guardrails",
    "learn & help": "catalog",
}


def derive_routes_and_homes(standalone: str) -> dict[str, str]:
    """route -> the destination the standalone sidebar homes it under."""
    homes: dict[str, str] = {}
    labels = list(DS_LABEL.finditer(standalone))
    for n, m in enumerate(labels):
        label = m.group(1).replace("&amp;", "&").strip().lower()
        dest = GROUP_TO_DESTINATION.get(label)
        if not dest:
            continue
        end = labels[n + 1].start() if n + 1 < len(labels) else len(standalone)
        for link in DS_SUB.finditer(standalone[m.end():end]):
            homes.setdefault(link.group(1), dest)
    return homes


# ── Declared exemptions ─────────────────────────────────────────────────────
# A route may legitimately be absent from the portal's router. Each entry states
# WHY, in the shape of _PIPELINE_EXCLUDED_HOOKS. An entry with no reason is not
# an exemption, it is a silenced finding — which is how a gate becomes decoration.
# ⛔ EMPTY ON PURPOSE, and it must stay that way.
#
# This dict previously carried `learn` with a stated open question: does the portal
# route it, or stop rendering the link? A FORGE run answered it -- and the answer was
# that BOTH options were wrong, because the premise was:
#
#   * "the portal does not route #/learn"        -- FALSE. route() has an explicit
#     `else if (section === "learn") { viewResources(); }` branch; the route renders
#     a full Resources page.
#   * "routing it would surface an empty tab"    -- FALSE of today; true only of the
#     option that adds `learn` to DASH_OWNER, which is tested FIRST and would have
#     STOLEN the route from the working branch and orphaned viewResources().
#   * "the portal still renders a Learn nav link" -- FALSE. `#dash-root .dash-sidebar`
#     is `display:none !important`, so the folded sidebar link is not rendered at all.
#
# The real defect was a nav-HIGHLIGHT mismatch, now fixed at source by
# SHELL_ROUTE_HOME, and this gate now reads the whole router (see
# `_shell_route_homes`) instead of DASH_OWNER alone.
#
# An entry here suppresses a genuine surface disagreement. If you are about to add
# one, the bar is a DECIDED divergence with a stated reason -- never an open question
# parked behind an exemption, which is what the `learn` entry was and why it took a
# full adversarial run to discover the question itself rested on three false premises.
ROUTE_EXEMPT: dict[str, str] = {}


def _shell_route_homes(portal: str) -> dict[str, str]:
    """Routes the portal serves from a shell branch rather than a dashboard tab.

    A route is counted only when BOTH halves are present, because either alone is
    a different defect and conflating them is what made this gate's one finding
    misleading:

      * `route()` dispatches it  -- `else if (section === "<r>")` -- so the route
        actually renders something; and
      * `SHELL_ROUTE_HOME` names the nav item that lights up for it.

    A dispatched route with no home entry still falls to the `control` default and
    IS a real finding, so it is deliberately NOT returned here.
    """
    dispatched = set(re.findall(r'section\s*===\s*["\']([a-z0-9-]+)["\']', portal))
    i = portal.find("const SHELL_ROUTE_HOME")
    if i == -1:
        return {}
    end = portal.find("};", i)
    block = portal[i:end if end != -1 else i + 2000]
    homes = dict(re.findall(
        r'["\']?([a-z0-9-]+)["\']?\s*:\s*["\']([a-z0-9-]+)["\']', block))
    return {r: h for r, h in homes.items() if r in dispatched}


def assert_portal_homes(portal: str, expected: dict[str, str]) -> list[Mismatch]:
    out: list[Mismatch] = []
    i = portal.find("const DASH_OWNER")
    if i == -1:
        return [Mismatch("route-placement", "DASH_OWNER",
                         "the portal has no DASH_OWNER map — no route can be homed")]
    # Bound the slice by the literal's own closing brace, not a guessed window,
    # and accept BOTH key forms: JS object keys are unquoted identifiers unless
    # they contain a hyphen (`heimdall:` vs `"web-access":`). Requiring quotes on
    # both sides matched only the hyphenated minority and reported every other
    # route as unrouted — 13 findings that were all the regex, not the routes.
    end = portal.find("};", i)
    block = portal[i:end if end != -1 else i + 8000]
    owners = dict(re.findall(
        r'["\']?([a-z0-9-]+)["\']?\s*:\s*["\']([a-z0-9-]+)["\']', block))

    # ⛔ DASH_OWNER IS NOT THE WHOLE ROUTER, and reading only it produced this
    # gate's one false finding. The portal has TWO ways to home a route:
    #   1. DASH_OWNER  -> the route is a folded dashboard TAB (viewDashboard)
    #   2. a shell-route branch in route() that renders its OWN view, whose nav
    #      highlight comes from SHELL_ROUTE_HOME
    # #/learn is shape 2: `else if (section === "learn") { viewResources(); }`.
    # Reading only DASH_OWNER, this gate reported it as "not routed at all — the
    # tab is effectively hidden". That was false: the route renders a full
    # Resources page. The finding was real (the nav highlighted the wrong item)
    # but its stated CAUSE was wrong, and acting on the stated cause would have
    # deleted a working page. A gate can be right that something is broken and
    # wrong about what is broken; assert against the whole router, not one map.
    owners.update(_shell_route_homes(portal))

    for route, home in sorted(expected.items()):
        if route in ROUTE_EXEMPT:
            continue
        got = owners.get(route)
        if got is None:
            out.append(Mismatch(
                "route-placement", f"#/{route}",
                f"the standalone sidebar homes it under '{home}', but the portal's "
                "DASH_OWNER does not route it at all — the link falls to the default "
                "section and the tab is effectively hidden",
            ))
        elif got != home:
            out.append(Mismatch(
                "route-placement", f"#/{route}",
                f"the two surfaces disagree: standalone homes it under '{home}', "
                f"portal under '{got}'. A user following one surface's navigation "
                "lands somewhere the other says it is not.",
            ))
    return out


# ── Registry ────────────────────────────────────────────────────────────────


def audit(root: Path) -> list[Mismatch]:
    out: list[Mismatch] = []

    standalone = _read(root / STANDALONE)
    portal = _read(root / PORTAL)
    expected = derive_routes_and_homes(standalone)
    if not expected:
        raise SystemExit(
            "surface-parity: derived ZERO routes from the standalone chrome — the "
            "expectation is empty, so every assertion below would pass vacuously"
        )
    out.extend(assert_portal_homes(portal, expected))
    globals()["n_routes"] = len(expected) - len(ROUTE_EXEMPT)
    return out


def self_test() -> int:
    ok = True
    import tempfile

    # M1 — the portal homes a route somewhere the standalone does not.
    # Fixtures use the REAL chrome shape — a ds-label group with ds-sub links.
    # The first draft used an invented `data-nav-group` attribute, so the
    # derivation returned nothing and every assertion below passed vacuously.
    standalone = ('<div class="ds-label">Control</div>'
                  '<a class="ds-sub" href="#/alpha">A</a>')
    portal_bad = 'const DASH_OWNER = { "alpha": "catalog" };'
    if assert_portal_homes(portal_bad, derive_routes_and_homes(standalone)):
        print("  ✓ caught: the two surfaces home a route differently")
    else:
        ok = False
        print("  ✗ MISSED: a placement disagreement")

    # M2 — the portal does not route it at all.
    if assert_portal_homes('const DASH_OWNER = { "beta": "control" };',
                           derive_routes_and_homes(standalone)):
        print("  ✓ caught: the portal does not route a standalone tab")
    else:
        ok = False
        print("  ✗ MISSED: an unrouted tab")

    # C1 — agreement must be silent, or the gate floods.
    if not assert_portal_homes('const DASH_OWNER = { "alpha": "control" };',
                               derive_routes_and_homes(standalone)):
        print("  ✓ clean:  agreeing surfaces are not flagged")
    else:
        ok = False
        print("  ✗ FLOODED on agreeing surfaces")

    # An exemption must actually suppress, and every entry must state a reason —
    # an empty reason is a silenced finding wearing an exemption's clothes.
    if all(isinstance(v, str) and len(v.strip()) > 40 for v in ROUTE_EXEMPT.values()):
        print("  ✓ clean:  every declared exemption carries a substantive reason")
    else:
        ok = False
        print("  ✗ an exemption has no real reason — that is a silenced finding")

    # An empty derivation must fail closed, never pass vacuously.
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / STANDALONE.parent).mkdir(parents=True)
        (d / STANDALONE).write_text("<nav>no groups here</nav>", encoding="utf-8")
        (d / PORTAL).write_text("const DASH_OWNER = {};", encoding="utf-8")
        try:
            audit(d)
            ok = False
            print("  ✗ MISSED: a zero-route derivation was accepted instead of failing closed")
        except SystemExit:
            print("  ✓ caught: a zero-route derivation fails closed")

    print("\nteeth verified" if ok else "\nTEETH BROKEN")
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    found = audit(Path(args.root))
    if found:
        print(f"surface-parity: {len(found)} disagreement(s) between surfaces", file=sys.stderr)
        for m in found:
            print(m.render(), file=sys.stderr)
        return 2
    print(f"surface-parity: {globals().get('n_routes', 0)} route(s) homed identically on both surfaces "
          f"({len(ROUTE_EXEMPT)} declared exemption(s), each with a stated reason)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
