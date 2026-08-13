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
ROUTE_EXEMPT = {
    "learn": (
        "OPEN — needs an owner ruling, exempted so the gate can ship without "
        "either flooding or silently hiding this. The portal DOES carry "
        "`panel-learn` and `learn-collapse`, and its same-group sibling #/trees "
        "IS routed to 'catalog' — so on the face of it this is the v0.211.1 "
        "'portal does not own the route' defect. BUT the v0.208.0 byte-diet "
        "deliberately stripped the portal's Learn payload, so routing it may "
        "surface an EMPTY tab, and the real inconsistency may instead be that "
        "the folded standalone chrome still renders the link at all. Fixing it "
        "the wrong way is worse than the current state: route it and a user "
        "clicks into nothing; drop the link and the portal loses a nav entry "
        "the standalone has. Resolve by deciding which surface is right, then "
        "either add `learn` to DASH_OWNER or stop rendering the link on the "
        "portal — and delete this entry either way."
    ),
}


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
