#!/usr/bin/env python3
"""check-skill-descriptions.py — P2 (succinct-skill-descriptions plan) linter.

The cheap, deterministic, on-disk floor for skill descriptions — the ONLY
component of the plan that survives RT-1 (the confirmed usage-gated rendering
finding) being true, because it operates on the corpus regardless of what
actually renders into any given session.

⛔ SCOPE, PER G-P2.3 (claim-6 conditionality). P1's claim-6 effect-size study
closed INCONCLUSIVE-BY-CONSTRUCTION (docs/plans/2026-09-03-succinct-skill-
descriptions/p1-status.md) — it was never earned. Per the plan's own rule,
the PRESERVATION half (category budgets enforced as a structural boundary
check, an IDF-token-preservation guard, an exemplar bank comparison) is
**NOT implemented here**. Only the linter half plan.md names as built
"regardless": category caps, filler-phrase detection, name-restatement
detection, RT-8 charset validation, and the corpus-total ratchet check.
AT-P2.2/AT-P2.3 (the preservation-half teeth tests) are SKIPPED, not failed —
`--self-test` reports them as `skip`, named, never silently dropped.

⛔ UPDATE (2026-09-08, post-P8-closure): category-cap enforcement is now REAL,
not informational. `cap_gate_check()` blocks on a NEW cap violation or a
WORSENED existing one, against a grandfather list
(`description-cap-exemptions.json`, seeded from the 104 files already over
cap when this enforcement was added). See that function's own docstring for
why grandfathering -- not a corpus-wide rewrite, and not a blanket block --
is the correct shape given P8's ruling that a semantic rewrite of the
existing corpus was never earned (claim 6 closed inconclusive-by-
construction; no eval apparatus exists to validate a rewrite is safe).

Checks implemented:
  - category cap (chars AND tokens), category = leaf | disambiguating | router,
    a deterministic classifier (see `classify_category`) -- ENFORCED, per
    `cap_gate_check()`, above
  - filler-phrase detection, calibrated from the real corpus (measured this
    session: "this skill" appears 60/956 times; zero hits for several other
    guessed phrases from the style-contract draft — NOT flagged, since a
    detector calibrated against zero real occurrences cannot be verified to
    fire correctly. The style contract still PROHIBITS them; this linter
    enforces what is measurably present.)
  - name-restatement detection (the skill's own name/slug appears in its own
    description — measured 60/956 real hits, spot-checked, real pattern)
  - RT-8 charset validation — the same 5-character-class set P0's own
    AT-P0.7 charset-round-trip teeth already established (colon, hash,
    leading dash, pipe, greater-than), plus tab and trailing whitespace,
    each with a specific named message (AT-P2.7)
  - corpus-total ratchet check against description-budget.json (the P3
    artifact this same PR seeds; full derived-ceiling/posture-drift
    semantics documented there, not duplicated here)
  - `--fix` for provably-safe mechanical strips ONLY (currently: trailing
    whitespace, a literal tab replaced with a single space) — never a
    content rewrite, per the plan's own "no silent content decisions" bar

Usage:
    check-skill-descriptions.py [--root ROOT] [--check] [--fix]
    check-skill-descriptions.py --self-test
    check-skill-descriptions.py --must-fail
"""

from __future__ import annotations

import argparse

# ⛔ Python module names can't contain '-'; load the sibling P0 instrument by
# explicit file path.
import importlib.util as _ilu
import json
import re
import sys
from pathlib import Path

_spec = _ilu.spec_from_file_location("_sdb", Path(__file__).parent / "skill-description-baseline.py")
_sdb = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_sdb)

# ── Category cap thresholds ─────────────────────────────────────────────────
# ⛔ G-P2.1: calibrated against the MEASURED distribution (description-baseline
# .json, 956 skills), not guessed. Set at each category's own p90 — this puts
# ~10% of the CURRENT corpus over cap per category, matching the plan's
# top-decile-only wave-1 framing (tiebreaks.md T2) rather than an arbitrary
# number. Measured 2026-09-08:
#   leaf            (n=719): p50=252  p75=349  p90=472  max=865
#   disambiguating  (n=176): p50=424  p75=622  p90=757  max=1016
#   router          (n=61):  p50=381  p75=486  p90=557  max=879
# Projected over-cap at these caps: leaf 67/719 (9.3%), disambiguating 17/176
# (9.7%), router 6/61 (9.8%) by chars; 74/719 (10.3%), 23/176 (13.1%), 7/61
# (11.5%) by chars-OR-tokens combined (AT-P2.1 asserts these exact counts).
CAP_CHARS = {"leaf": 480, "disambiguating": 760, "router": 560}
CAP_TOKENS = {"leaf": 105, "disambiguating": 165, "router": 120}

# ── Category classifier (deterministic) ─────────────────────────────────────
_DISAMBIG_RE = re.compile(r"\bNOT\s+for\b|\bNOT\s+the\b|→|->\s*[a-z]", re.I)
_ROUTER_RE = re.compile(
    r"\b(use when|triggers? on|invoke(d)? (by|when)|read this skill|escalat|routes? to)\b",
    re.I,
)


def classify_category(description: str, skill_name: str, all_names: set[str]) -> str:
    """leaf | disambiguating | router. Overridable via frontmatter
    `description_category:` with a reason (not yet wired to a real frontmatter
    reader here — SKILL.md authors can request an override; the override
    plumbing is a P2-follow-up, not blocking this gate's floor)."""
    d_lower = description.lower()
    mentions_sibling = any(
        n != skill_name and len(n) > 4 and n in d_lower for n in all_names
    )
    if _DISAMBIG_RE.search(description) or mentions_sibling:
        return "disambiguating"
    if _ROUTER_RE.search(description):
        return "router"
    return "leaf"


# ── Filler-phrase detection (calibrated, not guessed) ───────────────────────
# ⛔ Only "this skill" is ACTIVELY detected — it is the one guessed-filler
# pattern from the style contract draft that measurably occurs in the real
# corpus (60/956). The others named in the style contract ("use this skill/
# agent to", "helps you", "in order to", "spawn for '...'") measured ZERO
# real occurrences this session — a detector with no positive-control hit
# cannot be verified to fire correctly, so it is documented as PROHIBITED
# style (in the contract) but not wired as an active linter check here.
_FILLER_PATTERNS = {
    "this skill": re.compile(r"\bthis skill\b", re.I),
}


def find_filler(description: str) -> list[str]:
    return [label for label, pat in _FILLER_PATTERNS.items() if pat.search(description)]


def is_name_restated(description: str, skill_name: str) -> bool:
    name_spaced = skill_name.replace("-", " ")
    d_lower = description.lower()
    return skill_name.lower() in d_lower or name_spaced.lower() in d_lower


# ── RT-8 charset validation ──────────────────────────────────────────────────
# Same 5 character classes P0's own AT-P0.7 charset-round-trip teeth already
# established as the reference set (colon, hash, leading dash, pipe,
# greater-than), plus tab and trailing whitespace. Each check names the
# specific character in its message (AT-P2.7).
def charset_violations(description: str) -> list[str]:
    """⛔ Found LIVE, not hypothesized: this exact check (` #`, a space
    immediately before a hash) caught two real, live silent-truncation bugs
    in this marketplace while building this linter (2026-09-08) --
    `applied-statistics:choose-statistical-test` (truncated at "...data type
    →" mid-sentence, losing the entire rest of the description) and
    `ravenclaude-core:spec-reread-ritual` (truncated right before its own
    cited bug-study issue number). Both were UNQUOTED plain YAML scalars
    containing a mid-string ` #word` sequence, which PyYAML (and therefore
    Claude Code's own plugin loader) parses as a comment start -- not a
    parse ERROR, silent data loss. Both are fixed in this same PR (single-
    quoted). This is why RT-8 is a real floor and not decorative: the
    corpus-wide raw-source scan this defect prompted found exactly these 2
    of 1042 real skill files (grep, independent of this script, so the
    scan itself isn't relying on the buggy extraction path it's checking)."""
    violations = []
    if description.startswith("-"):
        violations.append("leading '-' (YAML block-sequence marker)")
    if "\t" in description:
        violations.append("literal tab character")
    if description != description.rstrip():
        violations.append("trailing whitespace")
    if ": " in description:
        violations.append("': ' (colon-space, breaks a YAML plain scalar mid-string)")
    if description.lstrip().startswith("#"):
        violations.append("leading '#' (YAML comment marker)")
    elif re.search(r"\s#", description):
        violations.append(
            "' #' (space-hash mid-string, PyYAML treats this as a comment start in a "
            "plain scalar and SILENTLY TRUNCATES the rest -- not a parse error; caught "
            "2 real live cases in this corpus, see this function's docstring)"
        )
    if description.lstrip().startswith("|") or description.lstrip().startswith(">"):
        violations.append("leading '|' or '>' (YAML block-scalar indicator)")
    return violations


# ── Linter core ──────────────────────────────────────────────────────────────
def lint(root: Path) -> tuple[list[dict], dict]:
    """Returns (findings, summary)."""
    data = _sdb.build(root)
    all_names = {s["skill"] for s in data["skills"]}
    findings = []
    counts = {"leaf": 0, "disambiguating": 0, "router": 0}

    for s in data["skills"]:
        desc = s["description"]
        cat = classify_category(desc, s["skill"], all_names)
        counts[cat] += 1

        if s["chars"] > CAP_CHARS[cat]:
            findings.append(
                {
                    "skill": s["path"],
                    "check": "category-cap-chars",
                    "detail": f"{s['chars']} chars > {cat} cap {CAP_CHARS[cat]}",
                }
            )
        if s["tokens"] is not None and s["tokens"] > CAP_TOKENS[cat]:
            findings.append(
                {
                    "skill": s["path"],
                    "check": "category-cap-tokens",
                    "detail": f"{s['tokens']} tokens > {cat} cap {CAP_TOKENS[cat]}",
                }
            )
        for label in find_filler(desc):
            findings.append(
                {"skill": s["path"], "check": "filler-phrase", "detail": f'contains "{label}"'}
            )
        if is_name_restated(desc, s["skill"]):
            findings.append(
                {
                    "skill": s["path"],
                    "check": "name-restatement",
                    "detail": f"description restates its own name/slug ({s['skill']})",
                }
            )
        for v in charset_violations(desc):
            findings.append({"skill": s["path"], "check": "charset", "detail": v})

    summary = {
        "skill_count": len(data["skills"]),
        "category_counts": counts,
        "finding_count": len(findings),
    }
    return findings, summary


def cap_gate_check(root: Path, data: dict) -> list[str]:
    """Per-file category-cap enforcement, GRANDFATHERED against
    description-cap-exemptions.json (seeded 2026-09-08 from the 104 files
    already over cap when this check was written -- see that file's own
    `status`/`note` fields). Blocks on exactly two shapes, never a third:

      (a) a cap-violating file NOT in the exemption list -- a brand-new
          violation this gate did not inherit.
      (b) a listed file whose CURRENT chars/tokens exceed the value
          RECORDED in its exemption entry -- an already-non-compliant file
          made WORSE.

    A listed file that improves (even while still over cap), or a file
    that clears its cap entirely, is never blocked -- this list is a floor
    under existing debt, not a target to hit. It is deliberately NOT the
    `check-frontmatter.py` agent-description gate's shape (hard cap, no
    grandfather) because that gate has always applied to every agent file
    uniformly; this one inherits 956 pre-existing skill descriptions this
    linter did not author, and P8's own closure (docs/plans/2026-09-03-
    succinct-skill-descriptions/p8-decision.md) ruled out a corpus-wide
    semantic rewrite to bring them into compliance first -- so grandfathering
    is not a compromise here, it is the only version of this gate that does
    not immediately red 104 already-shipped files with no sanctioned fix.

    An absent exemptions file is NOT "everything is exempt" -- it means the
    exemption list has never been seeded, so EVERY current cap violation
    reads as shape (a) and blocks. That is the correct fail-closed default
    for a fresh corpus; this repo's own exemptions file is seeded, so this
    path is exercised only by --self-test's scratch fixtures.
    """
    exemptions_path = (
        root / "docs/plans/2026-09-03-succinct-skill-descriptions/description-cap-exemptions.json"
    )
    exemptions: dict = {}
    if exemptions_path.exists():
        try:
            loaded = json.loads(exemptions_path.read_text(encoding="utf-8"))
            exemptions = loaded.get("exemptions", {})
            if not isinstance(exemptions, dict):
                return ["description-cap-exemptions.json's 'exemptions' key is not an object"]
        except Exception:
            return ["description-cap-exemptions.json exists but is not valid JSON"]

    all_names = {s["skill"] for s in data["skills"]}
    out: list[str] = []
    for s in data["skills"]:
        desc = s["description"]
        cat = classify_category(desc, s["skill"], all_names)
        over_chars = s["chars"] > CAP_CHARS[cat]
        over_tokens = s["tokens"] is not None and s["tokens"] > CAP_TOKENS[cat]
        if not (over_chars or over_tokens):
            continue  # compliant -- never blocked regardless of exemption status

        entry = exemptions.get(s["path"])
        if entry is None:
            out.append(
                f"{s['path']}: NEW cap violation ({s['chars']} chars / {s['tokens']} tokens vs "
                f"{cat} cap {CAP_CHARS[cat]}/{CAP_TOKENS[cat]}) -- not in "
                f"description-cap-exemptions.json. Either shorten the description under cap, or "
                f"if this is a legitimate router/disambiguating case that cannot compress, add a "
                f"reasoned entry to the exemptions file in the same PR."
            )
            continue

        exempt_chars = entry.get("chars")
        exempt_tokens = entry.get("tokens")
        worsened_chars = isinstance(exempt_chars, int) and s["chars"] > exempt_chars
        worsened_tokens = (
            isinstance(exempt_tokens, int)
            and s["tokens"] is not None
            and s["tokens"] > exempt_tokens
        )
        if worsened_chars or worsened_tokens:
            out.append(
                f"{s['path']}: cap violation WORSENED ({s['chars']} chars / {s['tokens']} tokens, "
                f"exempted at {exempt_chars} chars / {exempt_tokens} tokens) -- an edit made an "
                f"already-over-cap description longer, not shorter. Revert the growth, or update "
                f"the exemption entry in the same PR with a stated reason."
            )
    return out


def ratchet_check(
    root: Path, corpus_total_chars: int, corpus_total_tokens: int | None, skill_count: int
) -> list[str]:
    """P3's ratchet: gate condition is over-cap OR total-above-committed-
    ceiling (RT-2, binding -- NOT the gameable AND-condition A used). The
    ceiling is DERIVED at check time (re-read from the committed artifact,
    never recomputed/re-stamped by this script) and moves upward only via a
    dedicated, explicitly-labelled budget-raise PR (AT-P3.4) -- see
    description-budget.json's own `note` field and
    description-budget-raises.md in the same directory.

    Also runs the posture-drift check (AT-P3.5, X11): fails when the CURRENT
    skill_count differs from the PINNED population the ceiling was measured
    against, rather than silently comparing two different corpora. Scoped
    narrower than full per-plugin-version pinning (see the artifact's own
    `pinned_posture.note`) -- a deliberate, disclosed scope decision, not an
    oversight: this repo bumps plugin versions on nearly every PR, and
    pinning at that granularity would make the drift check fire constantly
    regardless of whether any description actually changed.
    """
    budget_path = root / "docs/plans/2026-09-03-succinct-skill-descriptions/description-budget.json"
    if not budget_path.exists():
        return []  # not yet seeded; P3 owns creation, not a P2 linter failure
    try:
        budget = json.loads(budget_path.read_text(encoding="utf-8"))
    except Exception:
        return ["description-budget.json exists but is not valid JSON"]

    out: list[str] = []

    pinned = budget.get("pinned_posture", {})
    pinned_count = pinned.get("skill_count")
    if isinstance(pinned_count, int) and pinned_count != skill_count:
        out.append(
            f"posture drift (AT-P3.5): pinned skill_count={pinned_count}, "
            f"current skill_count={skill_count} -- re-seed description-budget.json's "
            f"pinned_posture (and re-stamp the ceiling in the same PR) before trusting "
            f"a ratchet comparison against this population"
        )
        return out  # a drifted population makes the ceiling comparison below meaningless

    ceiling = budget.get("ceiling", {}).get("committed")
    if not isinstance(ceiling, dict):
        return out  # not yet in the P3 shape; nothing further to check
    cc = ceiling.get("chars")
    if isinstance(cc, int) and corpus_total_chars > cc:
        out.append(f"corpus total {corpus_total_chars} chars > committed ceiling {cc}")
    ct = ceiling.get("tokens")
    if isinstance(ct, int) and corpus_total_tokens is not None and corpus_total_tokens > ct:
        out.append(f"corpus total {corpus_total_tokens} tokens > committed ceiling {ct}")
    return out


# ── --fix: provably-safe mechanical strips only ─────────────────────────────
def fix_description(description: str) -> str:
    fixed = description.replace("\t", " ")
    fixed = fixed.rstrip()
    return fixed


def apply_fix(root: Path) -> int:
    """Rewrites SKILL.md files in place, fixing ONLY trailing whitespace and
    literal tabs in the description value. Never touches content. Returns
    the count of files changed."""
    changed = 0
    for f in _sdb._find_skill_files(root):
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        desc = _sdb._extract_description(text)
        if desc is None:
            continue
        fixed = fix_description(desc)
        if fixed == desc:
            continue
        # Only safe to mechanically rewrite when the description is a plain
        # or double-quoted single-line scalar the P0 extractor round-trips
        # byte-for-byte; anything else is left untouched rather than risking
        # a content-shape guess.
        m = _sdb._FM.match(text)
        if not m:
            continue
        dm = _sdb._DESC_LINE.search(m.group(1))
        if not dm:
            continue
        raw = dm.group(1).strip()
        if raw.startswith('"') and raw.endswith('"'):
            new_raw = '"' + fixed.replace('"', '\\"') + '"'
        elif raw.startswith("'") and raw.endswith("'"):
            new_raw = "'" + fixed.replace("'", "''") + "'"
        else:
            new_raw = fixed
        new_line = dm.group(0).replace(dm.group(1), new_raw, 1)
        new_fm = m.group(1)[: dm.start()] + new_line + m.group(1)[dm.end() :]
        new_text = text[: m.start(1)] + new_fm + text[m.end(1) :]
        if new_text != text:
            f.write_text(new_text, encoding="utf-8")
            changed += 1
    return changed


# ── CLI ──────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()

    if args.self_test:
        return _self_test()
    if args.must_fail:
        return _must_fail_teeth(root)

    if args.fix:
        n = apply_fix(root)
        print(f"--fix: {n} file(s) mechanically fixed (trailing whitespace / tabs only)")
        return 0

    findings, summary = lint(root)
    data = _sdb.build(root)
    ratchet_findings = ratchet_check(
        root,
        data["corpus"]["total_chars"],
        data["corpus"]["total_tokens"],
        data["corpus"]["skill_count"],
    )
    cap_findings = cap_gate_check(root, data)

    print(
        f"check-skill-descriptions: {summary['skill_count']} skills, "
        f"categories {summary['category_counts']}, {summary['finding_count']} finding(s) (informational)"
    )
    if args.check:
        # ⛔ filler/name-restatement/charset findings stay INFORMATIONAL ONLY
        # -- 406 of them exist today (measured 2026-09-08: 286 charset, 60
        # filler, 60 name-restatement) across pre-existing
        # descriptions this gate did not author, and this repo's own recorded
        # failure mode is "a gate that fires on everything gets disabled."
        # The category CAP findings are DIFFERENT: they are enforced below,
        # via cap_gate_check()'s grandfather list -- see that function's own
        # docstring for why a grandfather, not a blanket block, is correct
        # here. The corpus-total ratchet (P3) is unchanged, seeded AT today's
        # total.
        for f in findings[:30]:
            print(f"  · [{f['check']}] {f['skill']}: {f['detail']}")
        if len(findings) > 30:
            print(f"  ... and {len(findings) - 30} more (informational, not blocking)")
        blocking = False
        if cap_findings:
            for c in cap_findings:
                print(f"  ✗ [cap] {c}")
            blocking = True
        if ratchet_findings:
            for r in ratchet_findings:
                print(f"  ✗ [ratchet] {r}")
            blocking = True
        if blocking:
            return 1
        print("  cap gate: clean (no new or worsened category-cap violations)")
        print("  ratchet: clean")
        return 0

    return 0


def _self_test() -> int:
    import tempfile

    passed = 0
    failed: list[str] = []
    skipped: list[str] = []

    def check(name: str, cond: bool) -> None:
        nonlocal passed
        if cond:
            passed += 1
        else:
            failed.append(name)

    # AT-P2.7 charset teeth — the same 5 characters P0's AT-P0.7 established,
    # plus tab/trailing-whitespace.
    cases = {
        "leading-dash": ("- starts with a dash", "leading '-'"),
        "tab": ("has a\ttab", "tab"),
        "trailing-ws": ("trailing space ", "trailing whitespace"),
        "colon-space": ("a value: with colon-space", "colon-space"),
        "hash": ("# a comment-shaped start", "'#'"),
        "space-hash-mid-string": ("data type → #groups → paired?", "space-hash"),
        "pipe-lead": ("|piped start", "'|'"),
        "gt-lead": (">quoted start", "'>'"),
    }
    for label, (text, expect_substr) in cases.items():
        violations = charset_violations(text)
        check(
            f"AT-P2.7 charset: {label} flagged",
            any(expect_substr in v for v in violations),
        )

    # A clean description has none of these.
    clean = "Author Vega-Lite specs for a stated intent across web and BI surfaces."
    check("AT-P2.7 charset: clean description has zero violations", charset_violations(clean) == [])

    # Regression pin: the real 2026-09-08 incident shape (choose-statistical-
    # test's actual pre-fix text), so a future edit to this detector cannot
    # silently stop catching the exact bug that motivated it.
    real_incident_text = (
        "Pick the right hypothesis test for a described scenario by traversing "
        "the test-selection decision tree (data type → #groups → paired? "
        "→ assumption gate → test)"
    )
    check(
        "regression pin: the real 2026-09-08 choose-statistical-test incident shape is caught",
        any("space-hash" in v for v in charset_violations(real_incident_text)),
    )

    # Category classifier — real shapes.
    names = {"alpha-skill", "beta-skill"}
    check(
        "classifier: NOT-for pattern -> disambiguating",
        classify_category("Do X. NOT for Y -> beta-skill.", "alpha-skill", names) == "disambiguating",
    )
    check(
        "classifier: sibling mention -> disambiguating",
        classify_category("Do X, complements beta-skill.", "alpha-skill", names) == "disambiguating",
    )
    check(
        "classifier: trigger language -> router",
        classify_category("Use when the user asks about X.", "alpha-skill", names) == "router",
    )
    check(
        "classifier: plain description -> leaf",
        classify_category("Compute the total for a report.", "alpha-skill", names) == "leaf",
    )

    # Filler + name-restatement.
    check("filler: 'this skill' detected", find_filler("This skill does X.") == ["this skill"])
    check("filler: clean text has no filler", find_filler("Compute the total.") == [])
    check(
        "name-restatement: own slug present -> flagged",
        is_name_restated("Alpha-skill computes the total.", "alpha-skill"),
    )
    check(
        "name-restatement: absent -> not flagged",
        not is_name_restated("Computes the total for a report.", "alpha-skill"),
    )

    # AT-P2.4 --fix idempotence + AT-P2.1-style determinism, on a scratch tree.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "plugins" / "demo" / "skills" / "alpha").mkdir(parents=True)
        (root / "plugins" / "demo" / ".claude-plugin").mkdir(parents=True)
        (root / "plugins" / "demo" / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "demo", "version": "1.0.0"}), encoding="utf-8"
        )
        (root / "plugins" / "demo" / "skills" / "alpha" / "SKILL.md").write_text(
            '---\nname: alpha\ndescription: "Trailing space present.  "\n---\nbody\n',
            encoding="utf-8",
        )
        n1 = apply_fix(root)
        check("AT-P2.4 --fix: first run changes the file", n1 == 1)
        n2 = apply_fix(root)
        check("AT-P2.4 --fix: idempotent, second run changes nothing", n2 == 0)
        fixed_text = (root / "plugins" / "demo" / "skills" / "alpha" / "SKILL.md").read_text()
        check(
            "AT-P2.4 --fix: trailing whitespace actually removed",
            '"Trailing space present."' in fixed_text,
        )

    # AT-P3.1 / AT-P3.2 / AT-P3.5 — ratchet + posture-drift, on a scratch tree.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for name, desc in [("alpha", "Alpha does a thing."), ("beta", "Beta does another thing.")]:
            skill_dir = root / "plugins" / "demo" / "skills" / name
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                f'---\nname: {name}\ndescription: "{desc}"\n---\nbody\n', encoding="utf-8"
            )
        (root / "plugins" / "demo" / ".claude-plugin").mkdir(parents=True)
        (root / "plugins" / "demo" / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "demo", "version": "1.0.0"}), encoding="utf-8"
        )
        data = _sdb.build(root)
        budget_dir = root / "docs" / "plans" / "2026-09-03-succinct-skill-descriptions"
        budget_dir.mkdir(parents=True)
        budget_path = budget_dir / "description-budget.json"
        budget_path.write_text(
            json.dumps(
                {
                    "pinned_posture": {"skill_count": data["corpus"]["skill_count"]},
                    "ceiling": {
                        "committed": {
                            "chars": data["corpus"]["total_chars"],
                            "tokens": data["corpus"]["total_tokens"],
                        }
                    },
                }
            ),
            encoding="utf-8",
        )

        # AT-P3.1 — silent on an unmodified tree.
        r1 = ratchet_check(
            root, data["corpus"]["total_chars"], data["corpus"]["total_tokens"], data["corpus"]["skill_count"]
        )
        check("AT-P3.1: ratchet silent on unmodified tree", r1 == [])

        # AT-P3.2 — single-PR must-fail teeth: total pushed over ceiling.
        r2 = ratchet_check(
            root, data["corpus"]["total_chars"] + 500, data["corpus"]["total_tokens"], data["corpus"]["skill_count"]
        )
        check("AT-P3.2: ratchet fires when corpus total exceeds committed ceiling", len(r2) == 1)

        # AT-P3.5 — posture drift: skill_count changed, no ceiling re-stamp.
        r3 = ratchet_check(
            root, data["corpus"]["total_chars"], data["corpus"]["total_tokens"], data["corpus"]["skill_count"] + 1
        )
        check("AT-P3.5: posture-drift check fires on skill_count mismatch", any("posture drift" in x for x in r3))

    # Cap-gate teeth (2026-09-08 enforcement upgrade) — grandfather + block
    # new/worsened, on a scratch tree so the real corpus's 104 exemptions
    # never touch this test.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        skills_dir = root / "plugins" / "demo" / "skills"
        for name, desc in [
            ("alpha", "Short and fine, well under any cap for a leaf skill."),
            ("beta", "B " * 300),  # long leaf, deliberately over the leaf cap
            ("gamma", "G " * 300),  # long leaf, will be "exempted" below
        ]:
            d = skills_dir / name
            d.mkdir(parents=True)
            (d / "SKILL.md").write_text(
                f'---\nname: {name}\ndescription: "{desc.strip()}"\n---\nbody\n', encoding="utf-8"
            )
        (root / "plugins" / "demo" / ".claude-plugin").mkdir(parents=True)
        (root / "plugins" / "demo" / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "demo", "version": "1.0.0"}), encoding="utf-8"
        )
        data = _sdb.build(root)
        by_path = {s["path"]: s for s in data["skills"]}
        gamma_path = next(p for p in by_path if p.endswith("gamma/SKILL.md"))
        beta_path = next(p for p in by_path if p.endswith("beta/SKILL.md"))

        budget_dir = root / "docs" / "plans" / "2026-09-03-succinct-skill-descriptions"
        budget_dir.mkdir(parents=True)
        exemptions_path = budget_dir / "description-cap-exemptions.json"

        # Case 1: no exemptions file at all -> both over-cap skills block
        # (fail-closed default for a never-seeded list).
        cap1 = cap_gate_check(root, data)
        check(
            "cap-gate: absent exemptions file blocks EVERY current cap violation",
            len(cap1) == 2 and any(beta_path in c for c in cap1) and any(gamma_path in c for c in cap1),
        )

        # Case 2: gamma is exempted at its CURRENT size, beta is not listed.
        exemptions_path.write_text(
            json.dumps(
                {
                    "exemptions": {
                        gamma_path: {
                            "category": "leaf",
                            "chars": by_path[gamma_path]["chars"],
                            "tokens": by_path[gamma_path]["tokens"],
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        cap2 = cap_gate_check(root, data)
        check(
            "cap-gate: exempted-at-current-size violation does NOT block",
            not any(gamma_path in c for c in cap2),
        )
        check(
            "cap-gate: NOT-in-exemption-list violation (new) DOES block",
            any(beta_path in c and "NEW cap violation" in c for c in cap2),
        )

        # Case 3: gamma's exemption entry is stale (a smaller recorded size)
        # -- simulates an edit that WORSENED an already-over-cap file.
        exemptions_path.write_text(
            json.dumps(
                {
                    "exemptions": {
                        gamma_path: {
                            "category": "leaf",
                            "chars": by_path[gamma_path]["chars"] - 50,
                            "tokens": by_path[gamma_path]["tokens"],
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        cap3 = cap_gate_check(root, data)
        check(
            "cap-gate: exempted-but-worsened violation DOES block",
            any(gamma_path in c and "WORSENED" in c for c in cap3),
        )

        # Case 4: a clean, under-cap skill is never blocked regardless of
        # exemption-file state.
        check(
            "cap-gate: an under-cap skill is never in the violation list",
            not any(name in c for c in cap1 + cap2 + cap3 for name in ["alpha"]),
        )

    # AT-P2.2 / AT-P2.3 — preservation-half teeth. NOT built (G-P2.3: P1
    # closed inconclusive-by-construction, never earned). Reported as an
    # explicit, named skip — never silently dropped.
    skipped.append("AT-P2.2 (preservation: NOT-for clause deletion) — preservation half not built, P1 not earned")
    skipped.append("AT-P2.3 (RT-3 structural/keyword-tail) — preservation half not built, P1 not earned")

    print(f"check-skill-descriptions.py self-test: {passed} pass, {len(failed)} fail, {len(skipped)} skip")
    for s in skipped:
        print(f"  SKIP: {s}")
    for f in failed:
        print(f"  FAIL: {f}")
    return 0 if not failed else 1


def _must_fail_teeth(root: Path) -> int:
    """A fixture description with a real charset violation must be caught;
    the same description with the violation removed must NOT be."""
    bad = "- Starts with a dash and has: a colon-space too"
    good = "Starts fine and describes the task without hostile characters"
    bad_hit = len(charset_violations(bad)) > 0
    good_hit = len(charset_violations(good)) > 0
    ok = bad_hit and not good_hit
    print(
        f"must-fail teeth: bad description flagged={bad_hit}, good description flagged={good_hit} — "
        f"{'PASS (teeth bite)' if ok else 'FAIL (teeth do not bite)'}"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
