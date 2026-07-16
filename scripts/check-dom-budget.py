#!/usr/bin/env python3
"""check-dom-budget.py — Gate 132: the per-surface DOM load budget (+ ratchet),
the per-panel island payload budget, and the exempted-floor report.

═══════════════════════════════════════════════════════════════════════════════
METHOD — stdlib `html.parser`. Read this before changing a number.
═══════════════════════════════════════════════════════════════════════════════

WHAT IS COUNTED: every ELEMENT in the document (Lighthouse's "DOM size" unit).

WHAT "script/style EXCLUDED" MEANS — precisely, because a naive reading moves the
baseline by ~295 nodes and silently rebases every downstream figure:

    EXCLUDED  = the *contents* of <script>/<style>. `html.parser` puts those
                elements in CDATA mode, so `<` inside JS/JSON/CSS is text, never
                a tag. Nothing inside them is counted as an element.
    COUNTED   = the <script>/<style> ELEMENTS themselves, 1 each. They are real
                DOM nodes and Lighthouse counts them.

Driven reconciliation (this is why the above is the method and not a preference):

    all elements, script/style CONTENTS excluded  ->  dashboard 57,330 · index 50,945
    also dropping the script/style ELEMENTS       ->  dashboard 57,035 · index 50,648

The first pair reproduces the plan's §0.1 figures TO THE DIGIT, and is the only
reading consistent with §0.1's "islanded panels costed at 2 elements each —
<section> + <script type='application/json'>" (which counts the <script> element).

WHY NOT A REGEX TAG-TOKEN COUNTER (§2.1 / F1) — the load-bearing reason:

    JSON escapes `"` but NOT `<`.

So when a panel is islanded, its markup moves into a <script type="application/json">
payload where every `<` SURVIVES verbatim. A regex counter keeps counting those `<`
as tags, and additionally counts the new <script> wrapper — so it reports ~zero
reduction for the very mechanism the budget exists to measure. It is blind to the
thing it meters. `html.parser` sees the payload as text (CDATA), which is exactly
what the browser does, so the count falls when the DOM actually falls.

The divergence is not hypothetical and it is not small: it is 89 script/style
tokens TODAY, and ~46,000 after islanding. A gate whose error term grows by
500x at the moment of the change is not a gate.

STATED ASSUMPTION (§4.4): the per-panel payload budget assumes `activate()` renders
the island payload verbatim. If Phase 3 virtualizes, the rendered subset is SMALLER,
so the payload budget stays sound as a CEILING.

═══════════════════════════════════════════════════════════════════════════════
Usage:
    python3 scripts/check-dom-budget.py --check              # gate both surfaces
    python3 scripts/check-dom-budget.py --report             # floor/residue/x table
    python3 scripts/check-dom-budget.py --count <file>       # element count only
    python3 scripts/check-dom-budget.py --check --surface <f> --budget-override N
"""

import argparse
import json
import sys
from html.parser import HTMLParser

# ── The two surfaces (F2: two budgets, two ratchet tables) ───────────────────
DASHBOARD = "plugins/ravenclaude-core/dashboard.html"
INDEX = "index.html"

# ── Lighthouse's DOM-size error threshold (the yardstick, NOT the budget) ────
LIGHTHOUSE_THRESHOLD = 1400

# ── Exemptions (§2.2) ───────────────────────────────────────────────────────
# A panel that fails the module-scope-DOM-bind sweep is EXEMPT or FUNDED —
# never silently islanded. Exempt panels keep their full node cost forever, so
# they are counted into the floor rather than against the build.
EXEMPT_PANELS = {
    # `settings`: 144 posture radios bound at load, module-scope + document-wide
    # (dashboard.html:13261, :13906, :13941). Islanding kills the posture editor
    # SILENTLY with every gate green -> the next Save writes corrupted posture
    # wholesale. NOT covered by the §0.2 authorization (§0.2b).
    "panel-settings": "silent posture corruption; gate-invisible (§2.2 / §0.2b)",
}
FUNDED_PANELS = {
    # `learn`: fails the same sweep, but the risk owner accepted it (§0.2) and
    # the conversion work is funded (Phase 2L). Funded != exempt: it islands.
    "panel-learn": "funded conversion — Phase 2L (§0.2 ruling)",
}

# ── Cost of an islanded panel (§0.1): <section> + <script type=application/json>
ISLANDED_PANEL_COST = 2

# ═══════════════════════════════════════════════════════════════════════════
# THE RATCHET TABLES (F2 — one per surface; the gate binds the LAST row)
# ═══════════════════════════════════════════════════════════════════════════
# Each phase appends a row. The budget in force is the last row's value. The
# gate asserts the table is monotonically NON-INCREASING, so a phase can never
# quietly buy headroom by raising its own bar to DODGE the DOM-reduction work.
#
# Baselines re-derived at Phase 0 under the method above (dashboard 57,330 /
# index 50,945 — the figures in the docstring's reconciliation). They supersede
# plan A's 57,419 (a regex figure). NOTE: the must-fail half is derived as
# `count - 1`, NEVER a literal — plan A's literal 57,418 would have PASSED
# against 57,330.
#
# PHASE 6 (panel-pipeline delta) is a CONTENT-CORRECTNESS raise, not bloat: it
# added the guard-web-access + delegation-nudge stages — two SHIPPED hooks that
# were MISSING from the pipeline map (live drift, gap 1/4) — at +37 elements on
# each surface (57,330->57,367 / 50,945->50,982). The Phase-0 baseline had
# measured a map that was BUGGY (short two hooks); the corrected content is the
# honest baseline, held at ZERO slack (budget == exact count) so the gate stays
# exactly as tight and the count-1 teeth still bite. This raise did NOT dodge any
# reduction: the reduction phases (2/2L/3) that drop ~91% of nodes were not run
# in Phase 6's isolated execution — when they run they append LOWER rows from
# this corrected baseline and the ratchet resumes its descent.
RATCHET = {
    DASHBOARD: [
        ("Phase 0 -> 6", 57367, "Phase 0 baseline 57,330 (html.parser); +37 in Phase 6 for the two "
                                "shipped hooks missing from the pipeline map (gap 1/4). Zero slack."),
        ("Phase 2 (trees island)", 36762, "panel-trees (~20,612 elems) DOM-island-loaded into a "
                                          "<script type=application/json> payload rendered on activate; its "
                                          "elements leave the live-DOM count. 57,367 -> 36,762. Zero slack."),
        ("Phase 2L (Learn island)", 17066, "panel-learn (~19,702 elems) DOM-island-loaded; its four "
                                           "subsystems (search/widgets/steppers/node-links) re-pointed from "
                                           "load-time IIFEs to on-activate named functions. 36,762 -> 17,066 "
                                           "= 12.2x vs 1,400 (from 41.0x). Zero slack."),
        ("Phase 2b (Commands island)", 10764, "panel-commands (~6,308 elems, the 2nd-largest panel) "
                                              "DOM-island-loaded; its deferred .cmd-copy/.cmd-run binds "
                                              "re-pointed to an on-activate initCommands() scoped to "
                                              "#commands-mount. 17,066 -> 10,764 = 7.7x vs 1,400. Zero slack."),
    ],
    INDEX: [
        ("Phase 0 -> 6", 50982, "Phase 0 baseline 50,945; +37 in Phase 6 (same guard-web-access + "
                                "delegation-nudge fragment). Zero slack."),
        ("Phase 2 (trees island)", 37468, "portal fragment's trees payload islanded alongside the "
                                          "standalone surface. 50,982 -> 37,468. Zero slack."),
        ("Phase 2L (Learn island)", 17772, "portal Learn payload islanded alongside the standalone "
                                           "surface. 37,468 -> 17,772 = 12.7x. Zero slack."),
        ("Phase 2b (Commands island)", 11470, "portal fragment's commands payload islanded alongside "
                                              "the standalone surface. 17,772 -> 11,470 = 8.2x. Zero slack."),
    ],
}


def budget_for(surface):
    return RATCHET[surface][-1][1]


class _Counter(HTMLParser):
    """Counts elements; attributes them to the enclosing panel-* section.

    `html.parser` handles <script>/<style> as CDATA, so their contents never
    reach handle_starttag — the exclusion is structural, not a filter we apply.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.total = 0
        self.panels = {}  # panel id -> element count
        self.stack = []  # open panel ids (a panel-* nested in a panel-* is impossible today, but don't assume)
        self.islands = {}  # panel id -> [payload strings]
        self._island_of = None
        self._depth = 0
        self._panel_depths = []

    # -- elements -----------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        pid = a.get("id", "")

        self.total += 1
        for p in self.stack:
            self.panels[p] = self.panels.get(p, 0) + 1

        if tag == "section" and pid.startswith("panel-"):
            self.panels.setdefault(pid, 1)  # the <section> counts toward itself
            self.stack.append(pid)
            self._panel_depths.append(self._depth)

        # an island payload we will decode for the per-panel payload budget
        if tag == "script" and a.get("type") == "application/json" and self.stack:
            self._island_of = self.stack[-1]

        if tag not in _VOID:
            self._depth += 1

    def handle_startendtag(self, tag, attrs):
        self.total += 1
        for p in self.stack:
            self.panels[p] = self.panels.get(p, 0) + 1

    def handle_endtag(self, tag):
        if tag == "script":
            self._island_of = None
        if tag in _VOID:
            return
        self._depth -= 1
        while self._panel_depths and self._depth <= self._panel_depths[-1]:
            self._panel_depths.pop()
            if self.stack:
                self.stack.pop()

    def handle_data(self, data):
        if self._island_of:
            self.islands.setdefault(self._island_of, []).append(data)


_VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


def measure(path):
    c = _Counter()
    with open(path, encoding="utf-8") as fh:
        c.feed(fh.read())
    shell = c.total - sum(c.panels.values())
    return {
        "path": path,
        "total": c.total,
        "panels": c.panels,
        "shell": shell,
        "islands": c.islands,
    }


def active_tab_of(path):
    """The panel rendered on load (class="tab-panel active")."""
    import re

    with open(path, encoding="utf-8") as fh:
        m = re.search(r'<section class="tab-panel active" id="(panel-[^"]+)"', fh.read())
    return m.group(1) if m else None


def payload_elements(payload):
    """Decode an island payload and count the elements it will render."""
    try:
        markup = json.loads(payload)
    except json.JSONDecodeError as e:
        return None, f"payload is not valid JSON -> the panel renders NOTHING: {e}"
    if not isinstance(markup, str):
        return None, "payload must decode to a markup string"
    c = _Counter()
    c.feed(markup)
    return c.total, None


# ═══════════════════════════════════════════════════════════════════════════
def report(surfaces):
    """Item 4a — emit the EXEMPTED floor, the residue, and the x vs 1,400."""
    print("═" * 79)
    print("  Gate 132 — DOM budget report (html.parser; script/style contents excluded)")
    print("═" * 79)
    rows = []
    for path in surfaces:
        m = measure(path)
        act = active_tab_of(path)
        act_n = m["panels"].get(act, 0)
        exempt_n = sum(m["panels"].get(p, 0) for p in EXEMPT_PANELS)
        # floor = shell + active tab + SUM(exempt)   (§2.6 / P1)
        floor = m["shell"] + act_n + exempt_n
        islanded = [p for p in m["panels"] if p not in EXEMPT_PANELS and p != act]
        residue = floor + ISLANDED_PANEL_COST * len(islanded)
        rows.append((path, m, act, act_n, exempt_n, floor, islanded, residue))

        print(f"\n── {path}")
        print(f"   panels                        : {len(m['panels'])}")
        print(f"   whole-document elements       : {m['total']:>8,}   = {m['total']/LIGHTHOUSE_THRESHOLD:5.1f}x")
        print(f"   shell (total - SUM(panels))   : {m['shell']:>8,}")
        print(f"   active tab ({act})   : {act_n:>8,}")
        for p, why in EXEMPT_PANELS.items():
            print(f"   EXEMPT {p:<22s}: {m['panels'].get(p, 0):>8,}   {why}")
        for p, why in FUNDED_PANELS.items():
            print(f"   funded {p:<22s}: {m['panels'].get(p, 0):>8,}   {why}")
        print(f"   {'-'*72}")
        print(f"   EXEMPTED FLOOR (shell+active+SUM(exempt)) : {floor:>8,}   = {floor/LIGHTHOUSE_THRESHOLD:5.1f}x")
        print(f"   + {len(islanded)} islanded panels x {ISLANDED_PANEL_COST}"
              f"{'':<21s}: {ISLANDED_PANEL_COST*len(islanded):>8,}")
        print(f"   PROJECTED RESIDUE                         : {residue:>8,}   = "
              f"{residue/LIGHTHOUSE_THRESHOLD:5.1f}x vs 1,400")
        print(f"   reduction from today                      : "
              f"{(1 - residue/m['total'])*100:>7.1f}%")
        if exempt_n:
            print(f"   of the residue, SUM(exempt) is            : {exempt_n/residue*100:>7.1f}%")

    print("\n" + "─" * 79)
    print("  Per-panel island payload budget (§4.4)")
    n_islands = sum(len(m["islands"]) for _, m, *_ in rows)
    if n_islands == 0:
        print("  0 islands exist yet. The payload budget's teeth-proof is DEFERRED to")
        print("  Phase 2's first island (plan §7 Phase 0 item 4) — at Phase 0 there is")
        print("  no island to decode, and a fabricated one would prove nothing.")
    else:
        for path, m, *_ in rows:
            for pid, chunks in m["islands"].items():
                n, err = payload_elements("".join(chunks))
                print(f"  {path} {pid}: {err if err else f'{n:,} elements'}")
    print("═" * 79)
    return rows


def check(surfaces, override=None):
    rc = 0
    for path in surfaces:
        # the ratchet must never buy itself headroom
        vals = [v for _, v, _ in RATCHET[path]]
        if vals != sorted(vals, reverse=True):
            print(f"FAIL: {path}: ratchet table is not monotonically non-increasing: {vals}")
            rc = 1
        budget = override if override is not None else budget_for(path)
        n = measure(path)["total"]
        if n > budget:
            print(f"FAIL: {path}: {n:,} elements > budget {budget:,} (over by {n-budget:,})")
            rc = 1
        else:
            print(f"OK:   {path}: {n:,} elements <= budget {budget:,}")
    return rc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="gate the surfaces against their budgets")
    ap.add_argument("--report", action="store_true", help="emit the exempted floor / residue / x table")
    ap.add_argument("--count", metavar="FILE", help="print the element count for FILE and exit")
    ap.add_argument("--surface", metavar="FILE", help="restrict --check to one surface")
    ap.add_argument("--budget-override", type=int, metavar="N",
                    help="override the budget (the must-fail half derives count-1; never a literal)")
    args = ap.parse_args()

    if args.count:
        print(measure(args.count)["total"])
        return 0

    surfaces = [args.surface] if args.surface else [DASHBOARD, INDEX]

    if args.report:
        report(surfaces)
        return 0
    if args.check:
        return check(surfaces, args.budget_override)

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
