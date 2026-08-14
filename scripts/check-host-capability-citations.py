#!/usr/bin/env python3
"""Gate 208 — host-capability citation lint (P17 / MH-03 uncited-claim shape).

Scans generator output and hand-written ``knowledge/`` prose for a host name
(from host-support.json — never a hand-typed list) adjacent to a
supported / unsupported / natively verb without a dated basis or a
``host-support.json`` cross-ref.

Hard-fail (exit 2) ONLY where a host-support.json cell exists to gate against
(generator output + ``knowledge/`` + the root AGENTS.md host table + the
agent-ready template that writes that table into new repos). An unmarked claim
in free-form ``docs/`` prose is an ADVISORY nudge, not a build failure.

Honors ``[docs-verified <date>]`` / ``[unverified]`` / ``[verify-at-use]`` as
exempt (PR 9 provenance-marker convention). A same-sentence ISO date or a
``host-support.json`` mention is also exempt. Bare ``native`` is not a verb —
it flooded on "native notifications" / "native regex" (M5 dry-run).

SNR: a sentence *retracting* a false claim (``was false`` / ``was WRONG``)
is exempt; fenced code, YAML frontmatter, and this script's own source are
out of scope. Residual docs/ matches stay advisory.

Exit 0 = pass (advisory notes may print). Exit 2 = a hard finding.
Exit 1 is never used for a finding.

Usage:
    python3 scripts/check-host-capability-citations.py
    python3 scripts/check-host-capability-citations.py --self-test
    python3 scripts/check-host-capability-citations.py --must-fail
    python3 scripts/check-host-capability-citations.py --root <dir>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_MAP = _REPO / "plugins" / "ravenclaude-core" / "knowledge" / "host-support.json"

# Capability verbs. Bare "native" is deliberately omitted (M5: 8/11 dry-run
# hits were "native notifications" / "native regex" / "no native way").
_VERB = re.compile(r"\b((?:un)?supported|natively)\b", re.IGNORECASE)

# Provenance / SSOT exempt signals — any one on the same sentence is enough.
_EXEMPT = re.compile(
    r"\[docs-verified"
    r"|\[unverified"
    r"|\[verify-at-use"
    r"|host-support\.json"
    r"|\b20\d\d-\d\d-\d\d\b",
    re.IGNORECASE,
)

# Retracting a false claim is not asserting one (the supersession-note SNR).
_RETRACT = re.compile(
    r"\bwas\s+(?:false|wrong|incorrect)\b|\bfalse\s+claim\b|\bthis\s+was\s+the\s+false\b",
    re.IGNORECASE,
)

# Quoted / italic spans document a claim; they do not assert one.
_QUOTED = re.compile(r'\*[^*]*\*|"[^"]*"|`[^`]*`')

_FENCE = re.compile(r"```.*?```", re.DOTALL)
_FRONTMATTER = re.compile(r"^---\r?\n.*?\r?\n---", re.DOTALL)
_SENTENCE = re.compile(r"(?<=[.!?])\s+")

# How close host-token and verb must sit. Measured: the MH-03 shape is
# "Aider … natively" inside one clause; 120 chars covers that without
# bridging unrelated sentences that the splitter failed to cut.
_ADJACENT = 120

# Generated *prose* that can carry a host-capability claim. dashboard.html /
# index.html inline the entire host-support.json payload — scanning them is
# matching the SSOT against itself (M5: 22/29 dry-run hits). Gate 154 already
# pins that those files derive from the map.
_GENERATED_PREFIXES = (
    "plugins/ravenclaude-core/copilot/",
    "plugins/ravenclaude-core/codex/agents/",
)

_HARD_EXTRAS = (
    "AGENTS.md",
    "plugins/ravenclaude-core/templates/agent-ready-repo/AGENTS.md.template",
)

_TEXT_SUFFIXES = frozenset({".md", ".html", ".json", ".template", ".txt"})


def _fail(msg: str) -> int:
    print(f"host-capability-citations: {msg}", file=sys.stderr)
    return 2


def load_map(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"unreadable/invalid host-support.json at {path}: {exc}") from exc
    hosts = data.get("hosts") or {}
    if not hosts:
        raise ValueError(f"no hosts declared in {path}")
    return data


def host_tokens(data: dict) -> list[str]:
    """Labels + keys from the SSOT. Never a hand-typed host list.

    Split labels only on ``/`` (Windsurf / Devin Desktop). Do NOT split on
    spaces — that produced a generic ``code`` token from ``Claude Code``.
    """
    names: set[str] = set()
    for key, info in (data.get("hosts") or {}).items():
        names.add(key)
        names.add(key.replace("-", " "))
        label = ""
        if isinstance(info, dict):
            label = str(info.get("label") or "")
        if label:
            names.add(label.lower())
            for part in re.split(r"\s*/\s*", label):
                part = part.strip().lower()
                if len(part) >= 5:
                    names.add(part)
    return sorted(names, key=len, reverse=True)


def host_regex(tokens: list[str]) -> re.Pattern[str]:
    if not tokens:
        raise ValueError("no host tokens derived from host-support.json")
    body = "|".join(re.escape(t) for t in tokens)
    return re.compile(r"\b(" + body + r")\b", re.IGNORECASE)


def _sentences(text: str) -> list[str]:
    text = _FENCE.sub(" ", text)
    text = _FRONTMATTER.sub(" ", text)
    return [s.replace("\n", " ") for s in _SENTENCE.split(text) if s.strip()]


def findings_in(text: str, host_re: re.Pattern[str]) -> list[str]:
    """Return snippet list for unmarked host+capability sentences."""
    out: list[str] = []
    for sent in _sentences(text):
        if not host_re.search(sent) or not _VERB.search(sent):
            continue
        if _EXEMPT.search(sent) or _RETRACT.search(sent):
            continue
        # Mask quoted/italic spans before the adjacency test so a documented
        # false claim ("supported zero times") is not itself a finding.
        masked = _QUOTED.sub(" ", sent)
        if not host_re.search(masked) or not _VERB.search(masked):
            continue
        hosts = list(host_re.finditer(masked))
        verbs = list(_VERB.finditer(masked))
        if not any(abs(h.start() - v.start()) <= _ADJACENT for h in hosts for v in verbs):
            continue
        out.append(re.sub(r"\s+", " ", sent).strip()[:180])
    return out


def _iter_md(dirpath: Path) -> list[Path]:
    if not dirpath.is_dir():
        return []
    files: list[Path] = []
    for p in dirpath.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        if "visuals" in p.parts or "tree-visuals" in p.parts:
            continue
        if p.name == "host-support.json":
            continue
        files.append(p)
    return files


def collect_paths(root: Path) -> tuple[list[Path], list[Path]]:
    """Return (hard_paths, advisory_paths)."""
    hard: list[Path] = []
    for extra in _HARD_EXTRAS:
        p = root / extra
        if p.is_file():
            hard.append(p)
    for prefix in _GENERATED_PREFIXES:
        p = root / prefix
        if p.is_file():
            hard.append(p)
        elif p.is_dir():
            hard.extend(_iter_md(p))
    # Only ravenclaude-core/knowledge: other plugins' "Copilot" / "Gemini" /
    # "cursor" hits are Microsoft 365 Copilot, the Gemini *model*, or
    # pagination cursors (M5: 7/29 dry-run hits, none about this SSOT).
    hard.extend(_iter_md(root / "plugins" / "ravenclaude-core" / "knowledge"))
    # Dedup, keep order.
    seen: set[Path] = set()
    hard_u: list[Path] = []
    for p in hard:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            hard_u.append(p)

    advisory: list[Path] = []
    docs = root / "docs"
    if docs.is_dir():
        for p in _iter_md(docs):
            if p.resolve() not in seen:
                advisory.append(p)
    return hard_u, advisory


def scan(root: Path, host_re: re.Pattern[str]) -> tuple[list[str], list[str], int]:
    """Return (hard_findings, advisory_notes, hard_files_read)."""
    hard_paths, advisory_paths = collect_paths(root)
    hard_findings: list[str] = []
    for path in hard_paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            hard_findings.append(f"{path}: unreadable ({exc})")
            continue
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        for snip in findings_in(text, host_re):
            hard_findings.append(f"{rel}: {snip}")

    advisory: list[str] = []
    for path in advisory_paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        for snip in findings_in(text, host_re):
            advisory.append(f"{rel}: {snip}")
    return hard_findings, advisory, len(hard_paths)


def _write_map(dest: Path, data: dict) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data), encoding="utf-8")


def self_test() -> int:
    """Plant the MH-03 shape and the three exempt/advisory companions."""
    try:
        live = load_map(_MAP)
    except ValueError as exc:
        return _fail(f"self-test cannot load the live map: {exc}")
    host_re = host_regex(host_tokens(live))
    # Pick a real host+label from the SSOT so the fixture is not a constant.
    host_key = next(iter(live["hosts"]))
    label = live["hosts"][host_key].get("label") or host_key

    bad: list[str] = []
    claim = f"{label} natively reads AGENTS.md with no basis at all."
    if not findings_in(claim, host_re):
        bad.append(f"MISSED the uncited MH-03 shape: {claim!r}")
    marked = f"{label} natively reads AGENTS.md [docs-verified 2026-07-28]."
    if findings_in(marked, host_re):
        bad.append(f"FALSE POSITIVE on a [docs-verified] claim: {marked!r}")
    xref = f"{label} natively reads AGENTS.md — see host-support.json."
    if findings_in(xref, host_re):
        bad.append(f"FALSE POSITIVE on a host-support.json cross-ref: {xref!r}")
    unver = f"{label} natively reads AGENTS.md [unverified]."
    if findings_in(unver, host_re):
        bad.append(f"FALSE POSITIVE on [unverified]: {unver!r}")
    retract = (
        f"the previous claim that {label} read this file natively was false."
    )
    if findings_in(retract, host_re):
        bad.append(f"FALSE POSITIVE on a retraction: {retract!r}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_map(
            root / "plugins" / "ravenclaude-core" / "knowledge" / "host-support.json",
            live,
        )
        know = root / "plugins" / "ravenclaude-core" / "knowledge" / "planted.md"
        know.write_text(claim + "\n", encoding="utf-8")
        hard, _, n = scan(root, host_re)
        if not hard:
            bad.append("planted uncited knowledge/ claim was NOT caught")
        if n < 1:
            bad.append("planted tree reported zero hard surfaces")

        # Same claim in docs/ must stay advisory (exit 0 path).
        docs = root / "docs" / "plans" / "planted.md"
        docs.parent.mkdir(parents=True, exist_ok=True)
        docs.write_text(claim + "\n", encoding="utf-8")
        know.unlink()
        hard2, adv, _ = scan(root, host_re)
        if hard2:
            bad.append(f"docs/-only claim became a hard finding: {hard2}")
        if not adv:
            bad.append("docs/-only uncited claim produced no advisory note")

    if bad:
        print("SELF-TEST FAILED:", file=sys.stderr)
        for line in bad:
            print(f"  - {line}", file=sys.stderr)
        return 2
    print(
        "self-test OK: uncited knowledge/ claim caught; "
        "[docs-verified]/[unverified]/host-support.json/retraction spared; "
        "docs/ stays advisory"
    )
    return 0


def drive_must_fail() -> int:
    """Plant an uncited knowledge/ claim against the live map. Must exit 2."""
    try:
        live = load_map(_MAP)
    except ValueError as exc:
        return _fail(str(exc))
    host_re = host_regex(host_tokens(live))
    host_key = next(iter(live["hosts"]))
    label = live["hosts"][host_key].get("label") or host_key
    claim = f"{label} natively reads AGENTS.md with no basis at all."
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_map(
            root / "plugins" / "ravenclaude-core" / "knowledge" / "host-support.json",
            live,
        )
        planted = root / "plugins" / "ravenclaude-core" / "knowledge" / "planted.md"
        planted.write_text(claim + "\n", encoding="utf-8")
        hard, _, _ = scan(root, host_re)
        if not hard:
            print("must-fail: planted claim was NOT caught", file=sys.stderr)
            return 0
    print("must-fail: planted uncited knowledge/ claim caught")
    return 2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument(
        "--must-fail",
        action="store_true",
        help="plant an uncited knowledge/ claim and exit 2 if caught",
    )
    ap.add_argument("--root", default=str(_REPO), help="repo root to scan")
    ap.add_argument(
        "--advisory",
        action="store_true",
        help="print each docs/ advisory note (default: count only)",
    )
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.must_fail:
        return drive_must_fail()

    root = Path(args.root)
    map_path = root / "plugins" / "ravenclaude-core" / "knowledge" / "host-support.json"
    if not map_path.is_file():
        map_path = _MAP
    try:
        data = load_map(map_path)
    except ValueError as exc:
        return _fail(str(exc))
    try:
        host_re = host_regex(host_tokens(data))
    except ValueError as exc:
        return _fail(str(exc))

    hard, advisory, n_hard = scan(root, host_re)
    if n_hard == 0:
        return _fail(
            "read ZERO hard surfaces — the scope collapsed "
            "(wrong --root, or knowledge/ moved). Failing closed."
        )
    if args.advisory:
        for note in advisory:
            print(f"advisory (docs/, not a build failure): {note}")
    if hard:
        print(
            f"{len(hard)} uncited host-capability claim(s) "
            f"on a host-support.json-backed surface:\n",
            file=sys.stderr,
        )
        for line in hard:
            print(f"  - {line}", file=sys.stderr)
        print(
            "Add [docs-verified <date>], [unverified], or a host-support.json "
            "cross-ref.",
            file=sys.stderr,
        )
        return 2
    print(
        f"host-capability-citations: {n_hard} hard surface(s) clean; "
        f"{len(advisory)} docs/ advisory note(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
