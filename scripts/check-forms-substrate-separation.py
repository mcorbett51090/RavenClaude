#!/usr/bin/env python3
"""Gate 219 - forms-engineering: substrate separation + CITE-DON'T-RESTATE.

`plugins/forms-engineering/` is a SEAM between three existing owners. Two
properties have to stay true for that framing to be honest, and neither one
survives on author discipline:

  1. SEPARABILITY. The RavenPower-specific substrate layer is exactly two
     allowlisted files. Vendor-specific machinery may not leak into the neutral
     body, so deleting those two files leaves a plugin that still passes the
     full suite (`audit-gates.sh`). `plugins/*/substrate/**` is DENIED by
     enforce-layout.sh, so the split is file-level and mechanically checked
     rather than expressed as a folder.
  2. CITE, DON'T RESTATE. `ravenclaude-core/rules/security.md` already owns
     upload hardening and `ravenclaude-core/knowledge/concepts/
     cloudflare-who-gets-in.md` already owns challenge-widget mechanics - the
     latter dated, sourced, and carrying a `refresh_when:` clause. A second copy
     in this plugin silently rots the moment the upstream moves.

## Sub-checks

  A  ALLOWLIST + FILENAME. A vendor token in the PATH of a non-allowlisted file
     is a violation on the path alone.
  B  CITATION FORM. A vendor token on a line of a non-allowlisted file is a
     violation unless that line carries a markdown link that RESOLVES into
     `plugins/ravenclaude-core/`, or the line sits inside a `## Routes to`
     section.
  C  NO RESTATED CONSTITUTION. The distinctive phrases owned upstream may
     appear only on a resolving core-link line. `single-use` is scoped by
     CO-OCCURRENCE with a challenge/widget mention inside a small line window:
     bare "single-use" is generic English and the plugin's own double-submit
     rule is legitimately about one-shot submit tokens. A term list that
     false-positives on owned content is a term list that gets trimmed to fit.
  D  CITE-OR-BE-SILENT (the positive requirement). Any file whose body mentions
     uploads, a challenge widget, CAPTCHA or a challenge token must carry at
     least one markdown link that RESOLVES into `plugins/ravenclaude-core/`.
  E  ANCHOR ROT. Each upstream file this plugin cites must still contain the
     stable anchor text it is cited for. Line numbers rot silently; a quoted
     sentence does not.
  F  ONE-WAY DEPENDENCY. The substrate layer may link into the neutral bank; a
     NEUTRAL file may not link into the substrate layer. This is what makes the
     separability test real: delete the two allowlisted files and the full
     suite must stay green, which a dangling neutral -> substrate link would
     break. The gate deliberately does NOT assert that an allowlisted path
     exists - an allowlist is a permission list, and requiring the permitted
     file to be present is exactly the coupling separability forbids.

## ⛔ LIMITATION, STATED RATHER THAN OVERSOLD

Sub-checks B and C are LITERAL-STRING matches. A restatement in different words
- the actual failure mode - evades them. This was measured: a paragraph saying
"read the leading bytes of the upload itself ... store it under an identifier
you generated, never under the name the browser sent" contains none of the
guarded literals and passes B and C green. A paraphrase fixture is committed
alongside the verbatim ones so the boundary stays visible in the test suite
rather than in a memo.

Sub-check D is the half that WORKS on a paraphrase: a positive requirement
cannot be evaded by word choice, because discussing the topic at all obliges a
pointer home. B and C raise the floor against verbatim copy-paste, which is the
common case. A human read at authoring time is still required and is a named
step in the build plan.

## FILE-TYPE SCOPE

A/B/C/D apply to `plugins/forms-engineering/**/*.md` ONLY. `hooks/`, `scripts/`
and `tests/fixtures/` are out of scope BY CONSTRUCTION: a hook's detection
strings are code, not prose, and a shell line can never be a markdown link. An
anti-pattern hook cannot detect a challenge widget without matching the widget's
own class name in its source. Scoping was decided before any content existed to
pressure it; a `.sh` must-pass fixture regression-locks it.

Exit codes: 0 = clean; 2 = a finding, an unreadable tree, or an empty scope
(fail-closed). Exit 1 is never used - a non-blocking exit on a blocking gate is
the silent fail-open this repo has shipped before.

Usage:
    python3 scripts/check-forms-substrate-separation.py
    python3 scripts/check-forms-substrate-separation.py --self-test
    python3 scripts/check-forms-substrate-separation.py --must-fail
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
FORMS = ROOT / "plugins" / "forms-engineering"
CORE = ROOT / "plugins" / "ravenclaude-core"

# The two files that are allowed to be vendor-specific. Everything else in the
# plugin is neutral. Growing this list past two re-opens ruling R3.
SUBSTRATE_ALLOWLIST = (
    "knowledge/ravenpower-form-substrate.md",
    "skills/wire-form-substrate/SKILL.md",
)

# Vendor tokens. `R2` / `D1` are matched case-SENSITIVELY with word boundaries:
# lowercase "r2"/"d1" occur inside ordinary words and identifiers, and a
# case-insensitive match here would flood on content that is not vendor-specific
# at all.
VENDOR_TOKENS = (
    ("cloudflare", re.compile(r"cloudflare", re.IGNORECASE)),
    ("turnstile", re.compile(r"turnstile", re.IGNORECASE)),
    ("astro", re.compile(r"\bastro\b", re.IGNORECASE)),
    ("wrangler", re.compile(r"wrangler", re.IGNORECASE)),
    ("R2", re.compile(r"\bR2\b")),
    ("D1", re.compile(r"\bD1\b")),
    ("resend", re.compile(r"\bresend\b", re.IGNORECASE)),
    ("stripe", re.compile(r"\bstripe\b", re.IGNORECASE)),
    ("web3forms", re.compile(r"web3forms", re.IGNORECASE)),
    ("siteverify", re.compile(r"siteverify", re.IGNORECASE)),
    ("pages functions", re.compile(r"pages\s+functions", re.IGNORECASE)),
)

# Sub-check C. Phrases the constitution owns. `single-use` is deliberately NOT
# here: it is handled as a co-occurrence rule below.
RESTATEMENT_PHRASES = (
    re.compile(r"magic[-\s]bytes?", re.IGNORECASE),
    re.compile(r"server-generated\s+filename", re.IGNORECASE),
    re.compile(r"resolve\s+to\s+absolute", re.IGNORECASE),
    re.compile(r"\b300[-\s]second", re.IGNORECASE),
    re.compile(r"\b(?:5|five)[-\s]minute", re.IGNORECASE),
    re.compile(r"siteverify", re.IGNORECASE),
)
SINGLE_USE_RE = re.compile(r"single[-\s]use", re.IGNORECASE)
CHALLENGE_RE = re.compile(r"turnstile|captcha|challenge\s+token|challenge\s+widget", re.IGNORECASE)
SINGLE_USE_WINDOW = 5

# Sub-check D. Topics that oblige a pointer home.
TOPIC_RE = re.compile(r"\bupload(?:s|ed|ing)?\b|turnstile|captcha|challenge\s+token", re.IGNORECASE)

# Sub-check E. Cite by stable anchor text, never by line number.
ANCHORS = (
    (
        "plugins/ravenclaude-core/rules/security.md",
        "Uploads: validate type by content (magic bytes), not extension",
    ),
    ("plugins/web-design/agents/accessibility-auditor.md", "zero-exception"),
    ("plugins/ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md", "Secret key"),
    ("plugins/web-design/agents/frontend-implementer.md", "native HTML form patterns first"),
)

MD_LINK_RE = re.compile(r"\[[^\]]*\]\(\s*([^)\s]+)\s*\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
ROUTES_TO_RE = re.compile(r"^#{1,6}\s+routes?\s+to\b", re.IGNORECASE)


class Finding(NamedTuple):
    check: str
    path: str
    line: int
    detail: str

    def render(self) -> str:
        where = f"{self.path}:{self.line}" if self.line else self.path
        return f"  [{self.check}] {where}: {self.detail}"


def _link_targets(line: str) -> list[str]:
    return MD_LINK_RE.findall(line)


def resolves_into_core(target: str, md_file: Path, core_dir: Path, repo_root: Path) -> bool:
    """True iff `target` resolves to an EXISTING path under `core_dir`.

    A dangling link is a violation, not a pass - "link-shaped" is not the
    property being asserted.
    """
    path_part = target.split("#", 1)[0].strip()
    if not path_part or "://" in path_part or path_part.startswith("<"):
        return False
    if path_part.startswith("/"):
        candidate = (repo_root / path_part.lstrip("/")).resolve()
    else:
        candidate = (md_file.parent / path_part).resolve()
    if not candidate.exists():
        return False
    try:
        candidate.relative_to(core_dir.resolve())
    except ValueError:
        return False
    return True


def _is_citation_line(line: str, md_file: Path, core_dir: Path, repo_root: Path) -> bool:
    return any(
        resolves_into_core(t, md_file, core_dir, repo_root) for t in _link_targets(line)
    )


def _routes_to_lines(lines: list[str]) -> set[int]:
    """0-based indices of lines inside a `## Routes to` section."""
    inside: set[int] = set()
    active_level = 0
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            if ROUTES_TO_RE.match(line):
                active_level = level
                inside.add(i)
                continue
            if active_level and level <= active_level:
                active_level = 0
            if active_level:
                inside.add(i)
            continue
        if active_level:
            inside.add(i)
    return inside


def analyse_file(
    md_file: Path,
    rel: str,
    allowlisted: bool,
    core_dir: Path,
    repo_root: Path,
) -> list[Finding]:
    findings: list[Finding] = []
    try:
        text = md_file.read_text(encoding="utf-8")
    except OSError as exc:
        return [Finding("A", rel, 0, f"unreadable: {exc}")]
    lines = text.splitlines()
    routes_to = _routes_to_lines(lines)

    # ── A: vendor token in the PATH of a non-allowlisted file ────────────────
    if not allowlisted:
        for name, pat in VENDOR_TOKENS:
            if pat.search(rel):
                findings.append(
                    Finding("A", rel, 0, f"vendor token '{name}' in the file path of a neutral file")
                )

    # ── B: vendor token on a non-citation line ───────────────────────────────
    if not allowlisted:
        for i, line in enumerate(lines):
            hits = [name for name, pat in VENDOR_TOKENS if pat.search(line)]
            if not hits:
                continue
            if i in routes_to:
                continue
            if _is_citation_line(line, md_file, core_dir, repo_root):
                continue
            findings.append(
                Finding(
                    "B",
                    rel,
                    i + 1,
                    "vendor token(s) %s on a line that is neither a resolving "
                    "link into plugins/ravenclaude-core/ nor inside a `## Routes to` "
                    "section" % ", ".join(sorted(set(hits))),
                )
            )

    # ── C: restated constitution, on any line that is not a core-link line ───
    for i, line in enumerate(lines):
        if _is_citation_line(line, md_file, core_dir, repo_root):
            continue
        for pat in RESTATEMENT_PHRASES:
            m = pat.search(line)
            if m:
                findings.append(
                    Finding(
                        "C",
                        rel,
                        i + 1,
                        "restates a phrase owned by ravenclaude-core (%r) off a link line"
                        % m.group(0),
                    )
                )
        if SINGLE_USE_RE.search(line):
            lo = max(0, i - SINGLE_USE_WINDOW)
            hi = min(len(lines), i + SINGLE_USE_WINDOW + 1)
            if any(CHALLENGE_RE.search(lines[j]) for j in range(lo, hi)):
                findings.append(
                    Finding(
                        "C",
                        rel,
                        i + 1,
                        "'single-use' co-occurs with a challenge/widget mention off a "
                        "link line - the replay rule is owned by ravenclaude-core",
                    )
                )

    # ── D: cite-or-be-silent (positive, paraphrase-proof) ────────────────────
    body_topics = TOPIC_RE.search(text)
    if body_topics:
        has_core_link = any(
            resolves_into_core(t, md_file, core_dir, repo_root)
            for line in lines
            for t in _link_targets(line)
        )
        if not has_core_link:
            findings.append(
                Finding(
                    "D",
                    rel,
                    0,
                    "discusses %r but carries no markdown link that RESOLVES into "
                    "plugins/ravenclaude-core/ - cite the owner or say nothing"
                    % body_topics.group(0),
                )
            )
    return findings


def scan_tree(
    scan_root: Path,
    allowlist: tuple[str, ...],
    core_dir: Path,
    repo_root: Path,
) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    files = sorted(p for p in scan_root.rglob("*.md") if p.is_file())
    for md_file in files:
        rel = md_file.relative_to(scan_root).as_posix()
        findings.extend(
            analyse_file(md_file, rel, rel in allowlist, core_dir, repo_root)
        )
    return findings, len(files)


def check_one_way(
    scan_root: Path, allowlist: tuple[str, ...], repo_root: Path
) -> list[Finding]:
    """Sub-check F - the substrate dependency is ONE-WAY.

    The substrate layer may link into the neutral bank. A NEUTRAL file may not
    link into the substrate layer, because that is what makes ruling R3's
    separability test real rather than asserted: delete the two allowlisted
    files and the full suite must stay green. A neutral -> substrate markdown
    link would leave `check-md-links.py` with a dangling target the moment the
    substrate layer is removed, so "separable" would be false while this gate
    reported clean.

    ⛔ Deliberately NOT asserted here: that an allowlisted path exists. An
    allowlist is a permission list; requiring the permitted file to be present
    is exactly the coupling that would break separability.
    """
    findings: list[Finding] = []
    targets = {(scan_root / rel).resolve() for rel in allowlist}
    if not targets:
        return findings
    for md_file in sorted(p for p in scan_root.rglob("*.md") if p.is_file()):
        rel = md_file.relative_to(scan_root).as_posix()
        if rel in allowlist:
            continue
        for i, line in enumerate(md_file.read_text(encoding="utf-8").splitlines()):
            for target in _link_targets(line):
                path_part = target.split("#", 1)[0].strip()
                if not path_part or "://" in path_part or path_part.startswith("<"):
                    continue
                if path_part.startswith("/"):
                    cand = (repo_root / path_part.lstrip("/")).resolve()
                else:
                    cand = (md_file.parent / path_part).resolve()
                if cand in targets:
                    findings.append(
                        Finding(
                            "F",
                            rel,
                            i + 1,
                            "a NEUTRAL file links into the substrate layer (%s) - the "
                            "dependency must run one way only, or deleting the substrate "
                            "files breaks the link checker and R3's separability test "
                            "fails. Reference the path as a code span, not a link."
                            % path_part,
                        )
                    )
    return findings


def check_anchors(anchors: tuple[tuple[str, str], ...], repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for rel, anchor in anchors:
        target = repo_root / rel
        if not target.is_file():
            findings.append(Finding("E", rel, 0, "cited file is missing"))
            continue
        if anchor not in target.read_text(encoding="utf-8"):
            findings.append(
                Finding(
                    "E",
                    rel,
                    0,
                    "cited anchor text is gone: %r - a citation in forms-engineering "
                    "now points at a property this file no longer states" % anchor,
                )
            )
    return findings


def audit() -> tuple[list[Finding], int]:
    if not FORMS.is_dir():
        return [Finding("A", "plugins/forms-engineering", 0, "plugin tree is missing")], 0
    findings, n = scan_tree(FORMS, SUBSTRATE_ALLOWLIST, CORE, ROOT)
    if n == 0:
        findings.append(
            Finding("A", "plugins/forms-engineering", 0, "no markdown files found - empty scope")
        )
    findings.extend(check_anchors(ANCHORS, ROOT))
    findings.extend(check_one_way(FORMS, SUBSTRATE_ALLOWLIST, ROOT))
    return findings, n


# ── Self-test: prove every sub-check distinguishes pass from fail ────────────

FIXTURES = ROOT / "tests" / "fixtures" / "forms-engineering" / "gate219"

# (fixture filename, sub-checks that MUST fire, sub-checks that MUST NOT fire)
FIXTURE_EXPECTATIONS = (
    ("must-fail-a-turnstile-in-the-filename.md", ("A",), ()),
    ("must-fail-b-vendor-token-with-no-link.md", ("B",), ()),
    ("must-fail-c-restated-constitution.md", ("C",), ()),
    # ⛔ THE MEASURED BLIND SPOT. The paraphrase says the same thing in different
    # words. It must NOT trip B or C - that is the documented limitation - and it
    # MUST trip D, which is the half that works.
    ("must-fail-d-paraphrase.md", ("D",), ("B", "C")),
    ("must-pass-linked-citation.md", (), ("A", "B", "C", "D")),
)


def self_test() -> int:
    problems: list[str] = []
    if not FIXTURES.is_dir():
        print(f"✗ fixture directory missing: {FIXTURES}", file=sys.stderr)
        return 2

    for name, must_fire, must_not_fire in FIXTURE_EXPECTATIONS:
        path = FIXTURES / name
        if not path.is_file():
            problems.append(f"fixture missing: {name}")
            continue
        found = {f.check for f in analyse_file(path, name, False, CORE, ROOT)}
        for check in must_fire:
            if check not in found:
                problems.append(
                    f"{name}: sub-check {check} did NOT fire (fired: {sorted(found) or 'none'}) "
                    "- the must-fail half asserts nothing"
                )
        for check in must_not_fire:
            if check in found:
                problems.append(
                    f"{name}: sub-check {check} fired but must not (fired: {sorted(found)})"
                )

    # File-type scope: a .sh carrying a widget class name must never be read.
    sh_fixture = FIXTURES / "must-pass-scope-fixture.sh"
    if not sh_fixture.is_file():
        problems.append("fixture missing: must-pass-scope-fixture.sh")
    else:
        scoped, _ = scan_tree(FIXTURES, (), CORE, ROOT)
        if any(f.path.endswith(".sh") for f in scoped):
            problems.append("scope rot: a .sh file was scanned by the **/*.md sweep")
        if "cf-turnstile" not in sh_fixture.read_text(encoding="utf-8"):
            problems.append(
                "scope fixture no longer contains a widget class name - it proves nothing"
            )

    # Sub-check F teeth: a neutral file linking into the substrate layer must be
    # caught, and the same link FROM a substrate file must not be.
    with tempfile.TemporaryDirectory() as td:
        tree = Path(td)
        (tree / "knowledge").mkdir(parents=True)
        (tree / "knowledge" / "sub.md").write_text("# substrate\n", encoding="utf-8")
        (tree / "neutral.md").write_text(
            "See [sub](./knowledge/sub.md).\n", encoding="utf-8"
        )
        (tree / "knowledge" / "other-substrate.md").write_text(
            "See [sub](./sub.md).\n", encoding="utf-8"
        )
        allow = ("knowledge/sub.md", "knowledge/other-substrate.md")
        got = {f.path for f in check_one_way(tree, allow, tree)}
        if "neutral.md" not in got:
            problems.append("sub-check F did not fire on a neutral -> substrate link")
        if "knowledge/other-substrate.md" in got:
            problems.append("sub-check F fired on a substrate -> substrate link")
        if check_one_way(tree, (), tree):
            problems.append("sub-check F fired with an empty allowlist")

    # Sub-check E teeth: delete the anchor upstream and the check must redden.
    with tempfile.TemporaryDirectory() as td:
        tmp_root = Path(td)
        rel = "plugins/ravenclaude-core/rules/security.md"
        (tmp_root / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_root / rel).write_text("# security\n\nnothing here\n", encoding="utf-8")
        anchor = ANCHORS[0][1]
        if not check_anchors(((rel, anchor),), tmp_root):
            problems.append("sub-check E did not fire on a file with the anchor removed")
        (tmp_root / rel).write_text(f"# security\n\n{anchor}\n", encoding="utf-8")
        if check_anchors(((rel, anchor),), tmp_root):
            problems.append("sub-check E fired on a file that DOES carry the anchor")

    if problems:
        print("✗ check-forms-substrate-separation self-test FAILED:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2
    print("✓ self-test: A/B/C/D/E/F each distinguish pass from fail; .md scope holds")
    return 0


def must_fail() -> int:
    """Plant a violation in a copy of the tree and prove the audit reddens.

    Exits 2 when the planted violation IS caught (teeth proven), 0 when it is
    not - which is what the suite's `must_fail` assertion reads.
    """
    if not FORMS.is_dir():
        print("plugin tree missing - cannot plant", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory() as td:
        planted = Path(td) / "knowledge"
        planted.mkdir(parents=True)
        (planted / "planted.md").write_text(
            "# planted\n\nTurnstile tokens are verified by calling siteverify.\n",
            encoding="utf-8",
        )
        findings, _ = scan_tree(Path(td), (), CORE, ROOT)
    kinds = {f.check for f in findings}
    if {"B", "C", "D"} & kinds:
        print(
            "✓ must-fail: a planted bare vendor/constitution restatement IS caught "
            f"(sub-checks {sorted(kinds)})"
        )
        return 2
    print("✗ must-fail: the planted violation was NOT caught - the gate has no teeth")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true", help="prove each sub-check has teeth")
    ap.add_argument("--must-fail", action="store_true", help="plant a violation; exit 2 if caught")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.must_fail:
        return must_fail()

    findings, n = audit()
    if findings:
        print(
            f"✗ forms-engineering substrate/citation separation: {len(findings)} finding(s) "
            f"across {n} markdown file(s)",
            file=sys.stderr,
        )
        for f in findings:
            print(f.render(), file=sys.stderr)
        return 2
    print(
        f"✓ forms-engineering substrate/citation separation clean "
        f"({n} markdown files, {len(SUBSTRATE_ALLOWLIST)} allowlisted substrate files)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
