#!/usr/bin/env python3
"""G3b — the FORGE premise gate. Deterministic; no model judgment.

Fails closed when a build phase depends on an INFERENCE that was never disconfirmed.

⛔ THE INCIDENT. A probe of a Cloudflare email-obfuscation href returned 404. From that
one negative result an agent concluded "the decoder is broken, every visitor is
affected" and built 16 files on it. That URL is a placeholder nothing fetches — it is
SUPPOSED to 404; the real decoder returned 200 and a real browser showed zero mangled
spans. The disconfirming probe cost ten seconds; the construction cost hours.

The wrong hypothesis was cheap and normal. The damage came from it being silently
promoted to a premise BY BEING WRITTEN DOWN, after which everything cited it instead of
re-testing it.

⛔ WHY G1 DOESN'T CATCH IT. G1 keys on PROVENANCE ("is it sourced?") and the false claim
WAS sourced — an in-session curl. The observation (404) was true; the inference drawn
from it was false. Grounding an observation is not grounding an inference drawn from it.

TRIGGER — three conjuncts, every one read off ARTIFACTS, never off the author's
confidence (at the moment of the incident the author was confident, so any gate keyed on
self-reported doubt would not have fired):
  1. the cited claims-table row is `kind: inference`
  2. it is cited by a build phase via `depends_on_claims:` — the friction collapse
  3. that phase's blast radius is over the floor

⛔ CONJUNCT 2 IS THE ONE THAT GETS SILENTLY BROKEN. This gate READS `depends_on_claims`.
If the G2/G3 plan contract stops EMITTING it, the gate runs, finds no edges, and passes
green while checking nothing. That defect shipped in a draft of this design, and its
gate supplied the field in a synthetic fixture so it went green while inert. Hence
`--require-edges`: a plan with phases but ZERO claim edges is reported as UNWIRED, not
clean. A fixture is not a wiring proof.

EXIT CODES ARE A CONTRACT:
  0  clean    — no unsettled inference is load-bearing
  2  tripped  — take one of the three exits (see reference/premise-gate.md)
  1  COULD NOT RUN — malformed/absent inputs. NEVER conflate with clean: "I looked and
     found nothing" and "I could not look" are indistinguishable afterward, which is
     exactly how a green gate ends up protecting nothing.

Python 3.9 compatible (stock macOS ships 3.9.6). Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile

CHEAP_FLOOR_SECONDS = 300
BLAST_FLOOR_FILES = 3

# `kind: inference` rows are unsettled unless the settling column says otherwise.
_SETTLED = ("settled", "falsified", "partially-settled", "owner-gated")

_EDGE_RE = re.compile(r"depends_on_claims\s*:\s*\[([^\]]*)\]", re.I)
_PHASE_RE = re.compile(r"^\s{0,3}#{2,4}\s*(?:Phase\s*)?(P?-?\d+[a-z]?)\b(.*)$", re.I | re.M)


# ⛔ TWO DEFECTS FIXED HERE 2026-08-20, both measured with fixtures before the change.
#
# 1. The pattern was `^[A-Za-z]*[-_ ]?(\d+)$` — anchored with no room for a trailing
#    suffix, so `C4a` / `C9b` / `4b` returned "". parse_claims does `if not rid: continue`,
#    so a suffixed ROW was silently dropped from the table, while parse_phases keeps an
#    unmatched edge VERBATIM. Measured: a table with `C4a` cited by an over-floor phase
#    parsed claims:1 of 2 rows and tripped "cites a claims-table row that does not exist",
#    exit 2. That is fail-CLOSED — loud and safe, but it accused the plan of citing a
#    phantom when the real fault was the parser. Suffixed ids are now first-class: `C4a`
#    normalises to `4a`, so it matches an edge citing `C4a` and trips for the RIGHT reason.
#
# 2. ⛔ THE ACTUAL FAIL-OPEN, and it is NOT the suffix. `[A-Za-z]*` collapses every prefix:
#    `C4`, `D4`, `X4` and `4` ALL normalise to `4`. The dict assignment then let a LATER row
#    silently OVERWRITE an earlier one. Measured: a table carrying `C4` (unsettled
#    inference, load-bearing) followed by `D4` (settled observation) parsed claims:2 of 3
#    with inferences:0 — the inference was gone — and a phase citing `C4` resolved to the
#    settled row and returned `trips: [] exit 0`. The gate reported CLEAN over an unsettled
#    premise. Collisions now RAISE, which main() turns into exit 1 (could-not-run), matching
#    this file's existing rule: cannot see -> cannot report clean.
_RID_RE = re.compile(r"^[A-Za-z]*[-_ ]?(\d+[a-z]?)$", re.IGNORECASE)


def _norm_rid(raw):
    """Normalise a claims-row id to its bare digits, or '' if it is not one.

    ⛔ Both SIDES of this gate must use this. The claims table and the plans are written
    by different authors (a human, then two independent panels), and nothing in the SKILL
    specifies the id format. Before this existed, rows had to match `^\\d+$` while edges
    were taken VERBATIM — so a table using `C1` and a plan citing `C1` agreed with each
    other and matched nothing, and the gate reported `{"claims":0,"trips":[]}` exit 0.
    control 2026-08-17: same table with `C`-prefixed ids -> claims:0 CLEAN; renumbered to
    bare ints -> claims:16, inferences:3. The id format was the only variable.
    """
    m = _RID_RE.match(str(raw).strip().lstrip("#").strip())
    # .lower() so `C4A` and `c4a` are one row, not two that then collide.
    return m.group(1).lower() if m else ""


def _cells(line: str):
    """Split one markdown table row into stripped cells."""

    if "|" not in line:
        return []
    parts = line.strip().strip("|").split("|")
    return [p.strip() for p in parts]


def parse_claims(path: str):
    """Parse claims-table.md -> {row_id: {"kind":..., "settled":bool, "text":...}}.

    Tolerant by design: a claims table is hand-authored prose. But tolerance stops at
    the point where it would let an unreadable file look like an empty-and-clean one —
    an unreadable table raises, and main() turns that into exit 1, never exit 0.
    """
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    header_idx = None
    cols = []
    for i, line in enumerate(lines):
        c = [x.lower() for x in _cells(line)]
        if c and any(x.startswith("claim") for x in c):
            header_idx = i
            cols = c
            break
    if header_idx is None:
        raise ValueError("no claims table header found (need a column starting 'claim')")

    def col(name, default=None):
        for j, c in enumerate(cols):
            if c.startswith(name):
                return j
        return default

    i_kind = col("kind")
    i_settle = col("settling", col("settle"))
    claims = {}
    for line in lines[header_idx + 1:]:
        cells = _cells(line)
        if not cells or set("".join(cells)) <= set("-: "):
            continue
        if len(cells) < 2:
            continue
        rid = _norm_rid(cells[0])
        if not rid:
            continue
        kind = (cells[i_kind].lower() if i_kind is not None and i_kind < len(cells) else "")
        kind = "inference" if "inference" in kind else ("observation" if "observation" in kind else "")
        settle = (cells[i_settle].lower() if i_settle is not None and i_settle < len(cells) else "")
        # ⛔ Collision = fail CLOSED. Silently overwriting is how an unsettled inference
        # disappears behind a settled row that merely shares its number (see _RID_RE).
        if rid in claims:
            raise ValueError(
                "duplicate claims-row id %r after normalisation (row %r collides with an "
                "earlier row). Prefixes are stripped, so C4 / D4 / 4 are the SAME id — "
                "renumber one of them. Refusing to report clean over an ambiguous table."
                % (rid, cells[0])
            )
        claims[rid] = {
            "kind": kind or "observation",
            "settled": any(s in settle for s in _SETTLED),
            "text": cells[1][:120] if len(cells) > 1 else "",
        }
    # ⛔ A header with ZERO parsed rows is unreadable, not empty-and-clean. Without this
    # the docstring invariant above was false: parse_claims returned {} silently, and a
    # plan whose phases legitimately declare `depends_on_claims: []` (which the SKILL
    # explicitly permits) then produced `{"claims":0,"trips":[]}` exit 0 — the gate
    # reporting CLEAN having resolved nothing. It guarded the no-EDGES case and not the
    # no-CLAIMS case; the guard was asymmetric. Cannot see -> cannot report clean.
    if not claims:
        raise ValueError(
            "claims table header found but ZERO rows parsed — unreadable, not empty. "
            "Row ids must be digits, optionally with a letter prefix (1, C1, c-1)."
        )
    return claims


def parse_phases(text: str):
    """Extract phases and their depends_on_claims edges from a plan's markdown."""
    phases = []
    marks = list(_PHASE_RE.finditer(text))
    for n, m in enumerate(marks):
        start = m.end()
        end = marks[n + 1].start() if n + 1 < len(marks) else len(text)
        body = text[start:end]
        edges = []
        for em in _EDGE_RE.finditer(body):
            raw = em.group(1)
            # Normalise ids the same way the claims table does, so `C4` and `4` are the
            # same row. A token that is not id-shaped is kept VERBATIM on purpose: it
            # must still trip "cites a row that does not exist" rather than vanish.
            edges += [(_norm_rid(x) or x.strip().strip("\"'#"))
                      for x in raw.split(",") if x.strip()]
        # Blast radius: count distinct path-ish tokens; a new-module phase is over floor.
        files = set(re.findall(r"[\w./-]+\.(?:py|sh|ts|tsx|js|mjs|astro|go|rs|rb|java|c|h|cpp|cs|php)", body))
        creates = bool(re.search(r"\b(create|new file|new module|add)\b", body, re.I))
        phases.append({
            "id": m.group(1),
            "edges": edges,
            "files": len(files),
            "creates": creates,
            "has_edge_decl": bool(_EDGE_RE.search(body)),
        })
    return phases


# Set by --must-fail to neuter the inference check. This is the ONLY defect the teeth
# plant, because it is the one that matters: without it the gate still walks every
# phase, still resolves every claim, still reports "CLEAN" — and detects nothing.
# ⛔ The first planted defect here was a raised blast floor, and it did NOT bite: a
# phase that CREATES a module is over-floor regardless of the file count, so the
# self-test passed with the "defect" applied and reported teeth-failed. A teeth check
# is only as good as the defect it plants — verify the plant, not just the check.
_NEUTER_INFERENCE_CHECK = False


def evaluate(claims, phases, blast_floor=BLAST_FLOOR_FILES):
    trips, unwired = [], []
    for ph in phases:
        over_floor = ph["creates"] or ph["files"] >= blast_floor
        if not ph["has_edge_decl"]:
            unwired.append(ph["id"])
            continue
        if not over_floor:
            continue
        for rid in ph["edges"]:
            c = claims.get(rid)
            if c is None:
                trips.append({"phase": ph["id"], "claim": rid,
                              "why": "cites a claims-table row that does not exist"})
                continue
            if (not _NEUTER_INFERENCE_CHECK) and c["kind"] == "inference" and not c["settled"]:
                trips.append({"phase": ph["id"], "claim": rid,
                              "why": "unsettled INFERENCE: " + c["text"]})
    return trips, unwired


def run(run_dir, blast_floor=BLAST_FLOOR_FILES, require_edges=True):
    ct = os.path.join(run_dir, "claims-table.md")
    if not os.path.isdir(run_dir):
        return 1, {"error": "run dir not found: " + run_dir}
    if not os.path.exists(ct):
        return 1, {"error": "no claims-table.md in run dir (cannot see -> cannot report clean)"}
    try:
        claims = parse_claims(ct)
    except Exception as exc:  # noqa: BLE001 - any parse failure is could-not-run, not clean
        return 1, {"error": f"claims-table.md unreadable: {exc}"}

    plans = [p for p in ("plan.md", "plan-A.md", "plan-B.md")
             if os.path.exists(os.path.join(run_dir, p))]
    if not plans:
        return 1, {"error": "no plan.md / plan-A.md / plan-B.md in run dir"}

    phases, trips, unwired = [], [], []
    for p in plans:
        with open(os.path.join(run_dir, p), encoding="utf-8") as fh:
            ph = parse_phases(fh.read())
        phases += ph
        t, u = evaluate(claims, ph, blast_floor)
        trips += t
        unwired += u

    result = {
        "claims": len(claims),
        "inferences": sum(1 for c in claims.values() if c["kind"] == "inference"),
        "phases": len(phases),
        "trips": trips,
        "unwired_phases": unwired,
    }
    if trips:
        return 2, result
    # ⛔ A plan with phases but no claim edges anywhere means conjunct 2 can never fire.
    # Report UNWIRED rather than clean — this is the exact silent-green shape that
    # shipped in a draft of this design.
    if require_edges and phases and not any(p["has_edge_decl"] for p in phases):
        result["error"] = ("no phase declares depends_on_claims -> conjunct 2 is "
                           "unsatisfiable; the gate would pass while checking nothing")
        return 1, result
    return 0, result


# ── self-test ────────────────────────────────────────────────────────────────────
_CLAIMS_FIX = """# claims

| # | claim | kind | tier | source | settling gate |
|---|---|---|---|---|---|
| 1 | GET /cdn-cgi/l/email-protection returned 404 | observation | WARN | in-session curl | settled |
| 5 | the decoder is broken, every visitor affected | inference | — | drawn from #1 | G3b |
| 7 | /cdn-cgi/trace returned 200 | observation | WARN | in-session curl | settled |
"""

_PLAN_TRIP = """## Phase P1
Create a new component `Email.astro` and convert the call sites.
depends_on_claims: [5]
"""

_PLAN_CLEAN = """## Phase P1
Create a new component `Email.astro`.
depends_on_claims: [1, 7]
"""

_PLAN_UNWIRED = """## Phase P1
Create a new module `thing.py` and add the wiring.
"""


def _mkrun(tmp, claims, plan):
    d = os.path.join(tmp, "run")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "claims-table.md"), "w", encoding="utf-8") as fh:
        fh.write(claims)
    with open(os.path.join(d, "plan.md"), "w", encoding="utf-8") as fh:
        fh.write(plan)
    return d


def self_test(broken=False):
    global _NEUTER_INFERENCE_CHECK
    _NEUTER_INFERENCE_CHECK = broken
    ok = True

    def chk(name, got, want):
        nonlocal ok
        if got == want:
            print(f"  OK   {name}")
        else:
            ok = False
            print(f"  FAIL {name} (got {got}, want {want})")

    with tempfile.TemporaryDirectory() as tmp:
        floor = 0

        d = _mkrun(tmp, _CLAIMS_FIX, _PLAN_TRIP)
        code, res = run(d, blast_floor=floor)
        chk("the incident replay TRIPS (unsettled inference is load-bearing)", code, 2)

        d2 = os.path.join(tmp, "clean")
        os.makedirs(d2, exist_ok=True)
        for fn, body in (("claims-table.md", _CLAIMS_FIX), ("plan.md", _PLAN_CLEAN)):
            with open(os.path.join(d2, fn), "w", encoding="utf-8") as fh:
                fh.write(body)
        code, _ = run(d2, blast_floor=floor)
        chk("a phase citing only OBSERVATIONS is clean", code, 0)

        d3 = os.path.join(tmp, "unwired")
        os.makedirs(d3, exist_ok=True)
        for fn, body in (("claims-table.md", _CLAIMS_FIX), ("plan.md", _PLAN_UNWIRED)):
            with open(os.path.join(d3, fn), "w", encoding="utf-8") as fh:
                fh.write(body)
        code, _ = run(d3, blast_floor=floor)
        chk("a plan with NO claim edges is UNWIRED (1), never clean", code, 1)

        code, _ = run(os.path.join(tmp, "nope"))
        chk("a missing run dir is could-not-run (1), never clean", code, 1)

        d4 = os.path.join(tmp, "garbage")
        os.makedirs(d4, exist_ok=True)
        with open(os.path.join(d4, "claims-table.md"), "w", encoding="utf-8") as fh:
            fh.write("this is not a table at all\n")
        with open(os.path.join(d4, "plan.md"), "w", encoding="utf-8") as fh:
            fh.write(_PLAN_TRIP)
        code, _ = run(d4)
        chk("an unreadable claims table is could-not-run (1), never clean", code, 1)

    print()
    print("  premise-gate self-test: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="G3b premise gate")
    ap.add_argument("--run-dir")
    ap.add_argument("--blast-floor", type=int, default=BLAST_FLOOR_FILES)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--must-fail", action="store_true",
                    help="plant a defect (a blast floor nothing clears) and assert the "
                         "self-test CATCHES it; exits 0 only when the teeth bite")
    args = ap.parse_args()

    if args.must_fail:
        rc = self_test(broken=True)
        if rc == 0:
            print("  TEETH FAILED: a neutered gate still passed the self-test")
            return 1
        print("  teeth OK: the planted defect was caught")
        return 0
    if args.self_test:
        return self_test()

    if not args.run_dir:
        ap.error("--run-dir is required (or use --self-test / --must-fail)")

    code, res = run(args.run_dir, args.blast_floor)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        if code == 0:
            print(f"premise-gate: CLEAN — {res.get('claims')} claims, "
                  f"{res.get('phases')} phases, no unsettled inference is load-bearing")
        elif code == 2:
            print("premise-gate: TRIPPED")
            for t in res["trips"]:
                print(f"  phase {t['phase']} -> claim {t['claim']}: {t['why']}")
            print("\nTake one of the three exits (reference/premise-gate.md): run the probe, "
                  "run the cheapest partial, or owner-gate it.")
        else:
            print(f"premise-gate: COULD NOT RUN — {res.get('error')}")
            print("⛔ This is NOT a pass. A check that cannot see must not report clean.")
    return code


if __name__ == "__main__":
    sys.exit(main())
