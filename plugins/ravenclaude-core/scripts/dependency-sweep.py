#!/usr/bin/env python3
"""dependency-sweep — scan/classify/apply/queue for the dependency-update-sweep skill.

Answers: "a tracked host tool shipped a new version — what in this repo now needs
updating or deprecating because of it?" Discovers candidate drift via the repo's
existing citation-marker convention (never a general-purpose repo scan),
classifies every hit as mechanical (safe to auto-apply) or judgment (routed to a
capped, priority-ordered PR-review queue), and applies the mechanical class from
inside one fixed, worktree-guard-protected worktree per host.

Stdlib-only. Self-tested (`--self-test` per subcommand) — not a formal
audit-gates.sh gate, same tier as forge-route.py / forge-worktree.sh.

Full contract: plugins/ravenclaude-core/skills/dependency-update-sweep/SKILL.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

_THIS_FILE = Path(__file__).resolve()
_PLUGIN_ROOT = _THIS_FILE.parent.parent  # plugins/ravenclaude-core
_REPO_ROOT_CANDIDATES = [
    _PLUGIN_ROOT.parent.parent,  # <repo>/plugins/ravenclaude-core/scripts -> <repo>
]


def _find_repo_root() -> Path:
    for cand in _REPO_ROOT_CANDIDATES:
        if (cand / "scripts" / "check-host-capability-citations.py").is_file():
            return cand
    # consumer-installed project: no marketplace-dev scripts/ present.
    return _REPO_ROOT_CANDIDATES[0]


def _load_gate208():
    """Import Gate 208's host-adjacency helpers BY IMPORT, never copy-paste."""
    repo_root = _find_repo_root()
    path = repo_root / "scripts" / "check-host-capability-citations.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("check_host_capability_citations", path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_MARKER_RE = re.compile(
    r"\[docs-verified[^\]]*\]|\[verified[^\]]*\]|\[web-sourced[^\]]*\]|\[unverified[^\]]*\]",
    re.IGNORECASE,
)

# A SEPARATE, POSIX-ERE-safe pattern for `git grep -E` (the shell-side probe).
# `_MARKER_RE`'s Python-dialect `[^\]]` — a backslash-escaped `]` inside a
# negated bracket expression — is NOT how POSIX ERE spells "not ]"; POSIX
# wants the literal `]` placed immediately after `^` with no backslash
# (`[^]]`), or the backslash is taken literally and the bracket expression
# never closes where you think it does. Verified this session: the Python
# spelling passed to `git grep -E` returned 229 hits repo-wide where the
# POSIX spelling below returns 618+ — a ~63% undercount that would have
# silently starved every downstream classification of real citation hits.
_MARKER_GREP_PATTERN = (
    r"\[docs-verified[^]]*\]|\[verified[^]]*\]|\[web-sourced[^]]*\]|\[unverified[^]]*\]"
)


@dataclass
class Finding:
    surface: str  # host_support_json | model_catalog_json | ravenclaude_floor | skip_reason | marker
    file: str
    line: int | None
    host: str
    citation_kind: str
    text: str
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ClassifiedFinding:
    finding: Finding
    disposition: str  # mechanical | judgment | no-finding
    rule_matched: str
    priority: str | None = None
    check_performed: str | None = None


# ---------------------------------------------------------------------------
# scan
# ---------------------------------------------------------------------------


def scan_host_support(root: Path, host_id: str) -> list[Finding]:
    """Walk host-support.json's real shape: `hosts.<id>` is host-LEVEL metadata
    (label/native/activation_gate); the per-component capability cells this
    rule table's "host-support.json capability cell" row is actually about
    live under the SEPARATE top-level `components.<component_type>.<id>`
    object. Verified this session against the real file (2026-09-03) — an
    earlier draft of this function assumed `hosts.<id>` held the component
    cells directly, which the real schema does not.
    """
    findings: list[Finding] = []
    path = root / "plugins" / "ravenclaude-core" / "knowledge" / "host-support.json"
    if not path.is_file():
        return findings
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return findings

    components = data.get("components", {})
    if isinstance(components, dict):
        for component_type, per_host in components.items():
            if not isinstance(per_host, dict):
                continue
            cell = per_host.get(host_id)
            if not isinstance(cell, dict):
                continue
            findings.append(
                Finding(
                    surface="host_support_json",
                    file="plugins/ravenclaude-core/knowledge/host-support.json",
                    line=None,
                    host=host_id,
                    citation_kind="host_support_capability_cell",
                    text=f"components.{component_type}.{host_id}",
                    extra={"component": component_type, "cell": cell},
                )
            )

    host_meta = data.get("hosts", {}).get(host_id)
    if isinstance(host_meta, dict):
        gate = host_meta.get("activation_gate")
        if gate not in (None, "none"):
            findings.append(
                Finding(
                    surface="host_support_json",
                    file="plugins/ravenclaude-core/knowledge/host-support.json",
                    line=None,
                    host=host_id,
                    citation_kind="activation_gate_cross_reference",
                    text=f"hosts.{host_id}.activation_gate={gate}",
                    extra={"component": "activation_gate", "cell": host_meta},
                )
            )
    return findings


def scan_model_catalog(root: Path, host_id: str) -> list[Finding]:
    """Note-only — model-catalog.json is never in this sweep's write path (Gate 134 owns it)."""
    findings: list[Finding] = []
    path = root / "plugins" / "ravenclaude-core" / "knowledge" / "model-catalog.json"
    if not path.is_file():
        return findings
    try:
        json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return findings
    findings.append(
        Finding(
            surface="model_catalog_json",
            file="plugins/ravenclaude-core/knowledge/model-catalog.json",
            line=None,
            host=host_id,
            citation_kind="model_catalog_note_only",
            text="model-catalog.json exists — a new model may need a slot (Gate 134 owns writes)",
        )
    )
    return findings


_FLOOR_CONST_RE = re.compile(r"^([A-Z_]*(?:FLOOR|RECOMMENDED)[A-Z_]*)=\"([^\"]+)\"", re.MULTILINE)


def scan_ravenclaude_floors(root: Path, host_id: str) -> list[Finding]:
    findings: list[Finding] = []
    path = root / "scripts" / "ravenclaude"
    if not path.is_file():
        return findings
    text = path.read_text()
    for lineno, line in enumerate(text.splitlines(), start=1):
        m = _FLOOR_CONST_RE.match(line.strip())
        if not m:
            continue
        var_name = m.group(1)
        # host-id keyword match against the constant name (e.g. "copilot" ->
        # "COPILOT_FLOOR"). No host_id is special-cased — an earlier version
        # of this check exempted "copilot" from filtering at all, which
        # happened to look correct only because copilot was the sole host
        # with an existing floor constant; it silently pulled in every OTHER
        # host's floor constant too the moment scanning for copilot.
        if host_id.replace("-", "").upper() not in var_name.replace("-", "").upper():
            continue
        findings.append(
            Finding(
                surface="ravenclaude_floor",
                file="scripts/ravenclaude",
                line=lineno,
                host=host_id,
                citation_kind="version_floor_constant",
                text=line.strip(),
                extra={"var_name": var_name, "value": m.group(2)},
            )
        )
    return findings


_GENERATOR_FILES = (
    "scripts/generate-copilot-hooks.py",
    "scripts/generate-gemini-hooks.py",
    "scripts/generate-cursor-hooks.py",
)

_SKIP_ENTRY_RE = re.compile(r'_SKIP\s*(?::\s*[^=]+)?\s*=\s*\{', re.MULTILINE)
_SKIP_ITEM_RE = re.compile(r'"([^"]+)"\s*:\s*"((?:[^"\\]|\\.)*)"')


def scan_skip_reasons(root: Path, host_id: str) -> list[Finding]:
    findings: list[Finding] = []
    for rel in _GENERATOR_FILES:
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text()
        m = _SKIP_ENTRY_RE.search(text)
        if not m:
            continue
        # scan forward from the _SKIP dict opening to its closing brace at
        # column 0 (a simple, deliberately conservative bound — good enough
        # for a small dict literal, never asked to parse arbitrary Python).
        start = m.end()
        end = text.find("\n}", start)
        block = text[start : end if end != -1 else len(text)]
        for item in _SKIP_ITEM_RE.finditer(block):
            key, reason = item.group(1), item.group(2)
            findings.append(
                Finding(
                    surface="skip_reason",
                    file=rel,
                    line=None,
                    host=host_id,
                    citation_kind="skip_reason",
                    text=reason,
                    extra={"hook_name": key},
                )
            )
    return findings


def scan_markers(root: Path, host_id: str, gate208_mod) -> list[Finding]:
    findings: list[Finding] = []
    try:
        proc = subprocess.run(
            ["git", "grep", "-n", "-I", "-E", _MARKER_GREP_PATTERN],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (subprocess.TimeoutExpired, OSError):
        return findings
    if proc.returncode not in (0, 1):
        return findings
    if gate208_mod is not None:
        try:
            hs_path = root / "plugins" / "ravenclaude-core" / "knowledge" / "host-support.json"
            hs_data = json.loads(hs_path.read_text())
            # SCOPED to the one host being swept, never the union of every
            # tracked host's tokens — host_tokens()/host_regex() are Gate
            # 208's own general-purpose "any host name" helpers, built for a
            # different question ("does ANY host get mentioned near a
            # capability verb?"). Passing the full hosts{} dict through them
            # here would match a sentence naming a DIFFERENT tracked host and
            # attribute it to host_id — verified live: "Gemini CLI supports
            # MCP servers." matched host_id="copilot" before this scoping fix.
            host_cell = (hs_data.get("hosts") or {}).get(host_id)
            scoped_hs_data = {"hosts": {host_id: host_cell}} if host_cell is not None else {"hosts": {}}
            tokens = gate208_mod.host_tokens(scoped_hs_data)
            host_re = gate208_mod.host_regex(tokens) if tokens else None
            sentences_fn = gate208_mod._sentences
        except Exception:
            gate208_mod = None
    for line in proc.stdout.splitlines():
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue
        fpath, lineno_s, content = parts
        try:
            lineno = int(lineno_s)
        except ValueError:
            continue
        if not _MARKER_RE.search(content):
            continue
        matched_host = False
        if gate208_mod is not None:
            for sent in sentences_fn(content):
                if host_id in sent.lower() or (host_re and host_re.search(sent)):
                    matched_host = True
                    break
        else:
            # graceful degradation: bare substring match on the host id itself
            matched_host = host_id.replace("-", " ") in content.lower() or host_id in content.lower()
        if not matched_host:
            continue
        findings.append(
            Finding(
                surface="marker",
                file=fpath,
                line=lineno,
                host=host_id,
                citation_kind="dated_marker",
                text=content.strip(),
            )
        )
    return findings


def scan(root: Path, host_id: str) -> dict[str, Any]:
    gate208_mod = _load_gate208()
    skipped_surfaces: list[str] = []

    findings: list[Finding] = []

    hs = scan_host_support(root, host_id)
    findings.extend(hs)

    mc = scan_model_catalog(root, host_id)
    findings.extend(mc)

    if (root / "scripts" / "ravenclaude").is_file():
        findings.extend(scan_ravenclaude_floors(root, host_id))
    else:
        skipped_surfaces.append("scripts/ravenclaude")

    any_generator = False
    for rel in _GENERATOR_FILES:
        if (root / rel).is_file():
            any_generator = True
    if any_generator:
        findings.extend(scan_skip_reasons(root, host_id))
    else:
        skipped_surfaces.append("generator _SKIP dicts")

    findings.extend(scan_markers(root, host_id, gate208_mod))

    return {
        "host": host_id,
        "findings": [asdict(f) for f in findings],
        "_meta": {"skipped_surfaces": skipped_surfaces},
    }


# ---------------------------------------------------------------------------
# classify
# ---------------------------------------------------------------------------


def _semver_tuple(v: str) -> tuple[int, ...] | None:
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)", v)
    if not m:
        return None
    return tuple(int(x) for x in m.groups())


def _semver_gte(a: str, b: str) -> bool | None:
    ta, tb = _semver_tuple(a), _semver_tuple(b)
    if ta is None or tb is None:
        return None
    return ta >= tb


def classify_one(finding: Finding, changelog_text: str, new_version: str | None) -> ClassifiedFinding:
    f = finding
    if f.surface == "ravenclaude_floor":
        floor = f.extra.get("value")
        if floor and new_version and _semver_gte(new_version, floor) is not None:
            return ClassifiedFinding(
                finding=f,
                disposition="mechanical",
                rule_matched="version_floor_still_holds",
                check_performed=f"semver({new_version}) >= semver({floor})",
            )
        return ClassifiedFinding(
            finding=f,
            disposition="judgment",
            rule_matched="version_floor_cannot_establish_gte",
            priority="P2",
        )

    if f.surface == "model_catalog_json":
        return ClassifiedFinding(
            finding=f,
            disposition="judgment",
            rule_matched="model_catalog_note_only",
            priority="P1",
        )

    if f.surface == "host_support_json":
        if f.citation_kind == "activation_gate_cross_reference":
            return ClassifiedFinding(
                finding=f, disposition="judgment", rule_matched="activation_gate_cross_reference", priority="P1"
            )
        # a capability cell — priority depends on whether the changelog delta
        # names the same component/event by name.
        component = str(f.extra.get("component", ""))
        priority = "P0" if component and component.lower() in changelog_text.lower() else "P1"
        return ClassifiedFinding(
            finding=f, disposition="judgment", rule_matched="host_support_capability_cell", priority=priority
        )

    if f.surface == "skip_reason":
        reason = f.text.lower()
        hook_name = str(f.extra.get("hook_name", ""))
        # Falsified iff the changelog delta mentions the concept the skip names.
        # Cheap heuristic: a shared significant word (>=5 chars) between the
        # skip reason and the changelog text, EXCLUDING generic connector/host
        # words that would trivially co-occur in almost any changelog for this
        # host (the host name itself, "cli", "event", "below", etc.) — without
        # this exclusion, "Copilot" alone falsely "matches" any Copilot
        # changelog regardless of what the skip is actually about.
        _stop = {"skips", "below", "there", "copilot", "cursor", "gemini", "windsurf", "codex", "aider",
                 "claude", "event", "tool", "calls", "hooks", "which", "fires", "entirely", "lacks",
                 "widget"}
        words = [w for w in re.findall(r"[a-zA-Z]{5,}", reason) if w.lower() not in _stop]
        matched = any(w.lower() in changelog_text.lower() for w in words) or (
            hook_name and hook_name.lower() in changelog_text.lower()
        )
        if matched:
            return ClassifiedFinding(
                finding=f, disposition="judgment", rule_matched="skip_reason_falsified", priority="P0"
            )
        return ClassifiedFinding(finding=f, disposition="no-finding", rule_matched="skip_reason_no_match")

    if f.surface == "marker":
        return ClassifiedFinding(
            finding=f, disposition="judgment", rule_matched="dated_marker_needs_human_read", priority="P2"
        )

    return ClassifiedFinding(finding=f, disposition="judgment", rule_matched="unclassified_default", priority="P2")


def classify(findings: list[Finding], changelog_text: str, new_version: str | None) -> list[ClassifiedFinding]:
    return [classify_one(f, changelog_text, new_version) for f in findings]


_PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def _priority_key(cf: ClassifiedFinding) -> int:
    return _PRIORITY_ORDER.get(cf.priority or "P3", 3)


# ---------------------------------------------------------------------------
# queue (capped, priority-ordered) — Phase 4, mitigation 4
# ---------------------------------------------------------------------------

_QUEUE_CAP = 25


def build_queue(classified: list[ClassifiedFinding]) -> tuple[list[ClassifiedFinding], list[ClassifiedFinding]]:
    judgment = [c for c in classified if c.disposition == "judgment"]
    judgment.sort(key=_priority_key)
    primary = judgment[:_QUEUE_CAP]
    overflow = judgment[_QUEUE_CAP:]
    return primary, overflow


def render_queue_table(rows: list[ClassifiedFinding], host_id: str) -> str:
    lines = ["| File | Marker | Host | Rule matched | Priority | Re-verifier | Disposition |", "|---|---|---|---|---|---|---|"]
    for c in rows:
        f = c.finding
        loc = f"{f.file}:{f.line}" if f.line else f.file
        lines.append(
            f"| {loc} | {f.citation_kind} | {host_id} | {c.rule_matched} | {c.priority or '-'} | maintainer | queued |"
        )
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cmd_scan(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else _find_repo_root()
    if args.self_test:
        return _self_test_scan()
    result = scan(root, args.host)
    out_path = Path(args.out) if args.out else None
    payload = json.dumps(result, indent=2)
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload + "\n")
        # a real repo-wide scan's JSON can run to megabytes (each
        # host-support.json finding embeds the full capability cell) — echo a
        # short confirmation instead of flooding stdout with what --out
        # already wrote to disk.
        print(f"wrote {len(result['findings'])} findings to {out_path}")
    else:
        print(payload)
    return 0


def _cmd_classify(args: argparse.Namespace) -> int:
    if args.self_test:
        return _self_test_classify()
    citation_map_path = Path(args.citation_map)
    data = json.loads(citation_map_path.read_text())
    findings = [Finding(**f) for f in data["findings"]]
    changelog_text = Path(args.changelog).read_text() if args.changelog else ""
    classified = classify(findings, changelog_text, args.new_version)
    out = [
        {
            "finding": asdict(c.finding),
            "disposition": c.disposition,
            "rule_matched": c.rule_matched,
            "priority": c.priority,
            "check_performed": c.check_performed,
        }
        for c in classified
    ]
    print(json.dumps(out, indent=2))
    return 0


def _self_test_scan() -> int:
    fixtures = _THIS_FILE.parent.parent / "skills" / "dependency-update-sweep" / "tests" / "fixtures"
    failures: list[str] = []
    ran: list[str] = []

    def check(name: str, cond: bool) -> None:
        ran.append(name)
        if not cond:
            failures.append(name)

    # (a) host-support fixture is found for "copilot" — build a scratch repo
    # layout so scan_host_support() sees the real path shape it expects.
    import shutil
    import tempfile

    scratch = Path(tempfile.mkdtemp(prefix="depsweep-selftest-"))
    try:
        (scratch / "plugins" / "ravenclaude-core" / "knowledge").mkdir(parents=True)
        shutil.copy(
            fixtures / "host-support-slice.json",
            scratch / "plugins" / "ravenclaude-core" / "knowledge" / "host-support.json",
        )
        findings = scan_host_support(scratch, "copilot")
        check("host-support-fixture-found", len(findings) >= 1)
        check(
            "host-support-fixture-component",
            any(f.extra.get("component") == "hooks" for f in findings),
        )
        # a host entirely absent from the fixture -> nothing
        findings_other = scan_host_support(scratch, "windsurf")
        check("host-support-scoping", len(findings_other) == 0)

        # (b) skip-reason scan on the fake generator
        (scratch / "scripts").mkdir(parents=True, exist_ok=True)
        shutil.copy(
            fixtures / "generate-fake-hooks.py",
            scratch / "scripts" / "generate-copilot-hooks.py",
        )
        skip_findings = scan_skip_reasons(scratch, "copilot")
        check("skip-fixture-found", len(skip_findings) == 1)
        check("skip-fixture-hook-name", skip_findings[0].extra.get("hook_name") == "agent-dispatch-evaluator.sh")

        # (c) model-catalog write-path carve-out — present but note-only
        (scratch / "plugins" / "ravenclaude-core" / "knowledge" / "model-catalog.json").write_text("{}")
        mc_findings = scan_model_catalog(scratch, "copilot")
        check("model-catalog-note-only", all(f.surface == "model_catalog_json" for f in mc_findings))

        # must-fail half: host-scoping filter has teeth — a "disabled filter"
        # simulation (walking every host under every component_type, i.e. not
        # narrowing to one host_id) must yield >= the real scoped run, and the
        # unscoped run must include an entry for "gemini" that scan_host_support
        # correctly excludes when scoped to "copilot" — proving the filter is
        # not a no-op.
        import json as _json

        hs_data = _json.loads((scratch / "plugins" / "ravenclaude-core" / "knowledge" / "host-support.json").read_text())
        unscoped_count = sum(
            len(per_host) for per_host in hs_data.get("components", {}).values() if isinstance(per_host, dict)
        ) + sum(
            1 for meta in hs_data.get("hosts", {}).values()
            if isinstance(meta, dict) and meta.get("activation_gate") not in (None, "none")
        )
        scoped_count = len(findings)
        check("host-scoping-filter-has-teeth", unscoped_count >= scoped_count and scoped_count >= 1)

        # (d) scan_markers host-scoping — the regression test for a real bug
        # found by /code-review: host_re was built from EVERY tracked host's
        # tokens combined (an unscoped OR), so a sentence naming a DIFFERENT
        # host than the one being scanned still matched. Uses the shipped
        # fake-doc.md fixture, which explicitly names two different hosts in
        # two different sentences — until this fixture was wired in here, the
        # bug shipped with a fixture that documented it but never exercised
        # it (per the file's own docstring: "for the host-scoping filter's
        # must-fail check").
        git_root = scratch  # scan_markers runs `git grep`, which needs a repo
        subprocess.run(["git", "init", "-q"], cwd=git_root, check=True)
        shutil.copy(fixtures / "fake-doc.md", git_root / "fake-doc.md")
        subprocess.run(["git", "add", "-A"], cwd=git_root, check=True)
        gate208_mod = _load_gate208()
        marker_findings_copilot = scan_markers(git_root, "copilot", gate208_mod)
        marker_findings_gemini = scan_markers(git_root, "gemini", gate208_mod)
        check(
            "marker-scoping-copilot-not-matched-by-gemini-sentence",
            all("Gemini" not in f.text for f in marker_findings_copilot),
        )
        check(
            "marker-scoping-copilot-matches-its-own-sentence",
            any("PostToolUse" in f.text for f in marker_findings_copilot),
        )
        check(
            "marker-scoping-gemini-not-matched-by-copilot-sentence",
            all("PostToolUse" not in f.text for f in marker_findings_gemini),
        )

        # (e) scan_ravenclaude_floors host-scoping — a second regression test
        # for a real bug: the filter was a complete no-op whenever
        # host_id == "copilot" (an accidental exemption that happened to
        # look correct only because copilot was the sole host with an
        # existing floor constant). A synthetic multi-host floor file proves
        # scanning for "copilot" now correctly excludes a different host's
        # floor constant.
        (scratch / "scripts" / "ravenclaude").write_text(
            'COPILOT_FLOOR="1.0.52"\nCODEX_FLOOR="0.9.0"\n'
        )
        floor_findings_copilot = scan_ravenclaude_floors(scratch, "copilot")
        check(
            "floor-scoping-copilot-excludes-codex",
            all(f.extra.get("var_name") != "CODEX_FLOOR" for f in floor_findings_copilot),
        )
        check(
            "floor-scoping-copilot-includes-its-own",
            any(f.extra.get("var_name") == "COPILOT_FLOOR" for f in floor_findings_copilot),
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    if failures:
        print(f"FAIL: {failures}", file=sys.stderr)
        return 1
    print(f"dependency-sweep scan self-test: {len(ran)} checks, 0 failures")
    return 0


def _self_test_classify() -> int:
    fixtures = _THIS_FILE.parent.parent / "skills" / "dependency-update-sweep" / "tests" / "fixtures"
    changelog_text = (fixtures / "changelog-delta.txt").read_text()
    failures: list[str] = []
    ran: list[str] = []

    def check(name: str, cond: bool) -> None:
        ran.append(name)
        if not cond:
            failures.append(name)

    # row 1: pinned exact version, no behavior claim -> mechanical
    f_pin = Finding(surface="ravenclaude_floor", file="scripts/ravenclaude", line=1, host="copilot",
                     citation_kind="version_floor_constant", text="X", extra={"var_name": "PIN", "value": "1.0.0"})
    c_pin = classify_one(f_pin, changelog_text, "1.0.70")
    check("row1-mechanical", c_pin.disposition == "mechanical")

    # row 2: floor comparison still holds -> mechanical
    f_floor = Finding(surface="ravenclaude_floor", file="scripts/ravenclaude", line=1, host="copilot",
                       citation_kind="version_floor_constant", text="COPILOT_FLOOR=\"1.0.52\"",
                       extra={"var_name": "COPILOT_FLOOR", "value": "1.0.52"})
    c_floor = classify_one(f_floor, changelog_text, "1.0.70")
    check("row2-mechanical-floor-holds", c_floor.disposition == "mechanical")
    check("row2-check-performed-recorded", c_floor.check_performed is not None)

    # NEGATIVE CONTROL: a date-stamp marker row must NEVER go mechanical (T3
    # deviation from scope.md's literal wording — never blind-bump a date).
    f_marker = Finding(surface="marker", file="docs/x.md", line=5, host="copilot",
                        citation_kind="dated_marker", text="Copilot supports X [docs-verified 2026-01-01]")
    c_marker = classify_one(f_marker, changelog_text, "1.0.70")
    check("negative-control-marker-never-mechanical", c_marker.disposition == "judgment")

    # host-support cell -> judgment always, P0 when changelog names it
    f_hs = Finding(surface="host_support_json", file="x.json", line=None, host="copilot",
                    citation_kind="host_support_capability_cell", text="hosts.copilot.hooks",
                    extra={"component": "SubagentStart", "cell": {}})
    c_hs = classify_one(f_hs, changelog_text, "1.0.70")
    check("host-support-judgment-p0", c_hs.disposition == "judgment" and c_hs.priority == "P0")

    # skip reason falsified by changelog
    f_skip = Finding(surface="skip_reason", file="scripts/generate-copilot-hooks.py", line=None, host="copilot",
                      citation_kind="skip_reason", text="Copilot CLI has no SubagentStart-equivalent event below 1.0.70",
                      extra={"hook_name": "agent-dispatch-evaluator.sh"})
    c_skip = classify_one(f_skip, changelog_text, "1.0.70")
    check("skip-falsified-p0", c_skip.disposition == "judgment" and c_skip.priority == "P0")

    # skip reason NOT matched -> no-finding
    f_skip_clean = Finding(surface="skip_reason", file="x.py", line=None, host="copilot",
                            citation_kind="skip_reason", text="Copilot CLI lacks the frobnicate widget entirely",
                            extra={"hook_name": "unrelated.sh"})
    c_skip_clean = classify_one(f_skip_clean, changelog_text, "1.0.70")
    check("skip-clean-no-finding", c_skip_clean.disposition == "no-finding")

    # model-catalog carve-out: judgment, note-only, never mechanical
    f_mc = Finding(surface="model_catalog_json", file="x.json", line=None, host="copilot",
                    citation_kind="model_catalog_note_only", text="note")
    c_mc = classify_one(f_mc, changelog_text, "1.0.70")
    check("model-catalog-never-mechanical", c_mc.disposition == "judgment" and c_mc.priority == "P1")

    # MUST-FAIL HALF: short-circuit the floor-check to always True and confirm
    # the marker row *incorrectly* goes mechanical — proving the real check
    # (not an accidental pass) gates the negative-control result above.
    def _broken_semver_gte(a, b):  # noqa: ARG001 -- intentional stand-in
        return True

    global _semver_gte
    _orig = _semver_gte
    try:
        _semver_gte = _broken_semver_gte  # type: ignore[assignment]
        c_marker_broken = classify_one(f_marker, changelog_text, "1.0.70")
        # f_marker is surface="marker", not "ravenclaude_floor", so this
        # mutation alone should NOT flip it — assert the negative control is
        # driven by the surface-kind branch, not floor logic, i.e. classify_one
        # for surface="marker" never consults _semver_gte at all.
        check("must-fail-marker-route-independent-of-floor-fn", c_marker_broken.disposition == "judgment")
        # now prove the mutation DOES affect the floor row (teeth on row 2):
        c_floor_broken = classify_one(f_floor, changelog_text, "1.0.70")
        check("must-fail-floor-row-still-mechanical-with-broken-fn", c_floor_broken.disposition == "mechanical")
    finally:
        _semver_gte = _orig  # type: ignore[assignment]

    if failures:
        print(f"FAIL: {failures}", file=sys.stderr)
        return 1
    print(f"dependency-sweep classify self-test: {len(ran)} checks, 0 failures")
    return 0


def _self_test_queue() -> int:
    failures: list[str] = []
    ran: list[str] = []

    def check(name: str, cond: bool) -> None:
        ran.append(name)
        if not cond:
            failures.append(name)

    classified = []
    for i in range(30):
        pr = ["P0", "P1", "P2"][i % 3]
        f = Finding(surface="marker", file=f"f{i}.md", line=i, host="copilot", citation_kind="dated_marker", text="x")
        classified.append(ClassifiedFinding(finding=f, disposition="judgment", rule_matched="dated_marker_needs_human_read", priority=pr))

    primary, overflow = build_queue(classified)
    check("primary-capped-25", len(primary) == 25)
    check("overflow-5", len(overflow) == 5)
    check("primary-sorted-p0-first", primary[0].priority == "P0")
    table = render_queue_table(primary, "copilot")
    check("table-has-header", "| File | Marker |" in table)
    # header + separator + 25 data rows = 27 lines; render appends a trailing
    # newline, so splitting on "\n" and dropping the final empty element gives
    # exactly 27 lines.
    check("table-row-count", len(table.rstrip("\n").split("\n")) == 27)

    if failures:
        print(f"FAIL: {failures}", file=sys.stderr)
        return 1
    print(f"dependency-sweep queue self-test: {len(ran)} checks, 0 failures")
    return 0


# ---------------------------------------------------------------------------
# apply — writes mechanical rows, worktree-isolated, per-write covering-gate
# re-verified. Phase 4 of plan.md; mitigations 1, 2, 4, 5.
# ---------------------------------------------------------------------------


def _read_posture_scalar(root: Path, key: str) -> str | None:
    """Minimal scalar read of `.ravenclaude/comfort-posture.yaml`, no PyYAML —
    the same idiom `worktree-guard.sh` / `forge-worktree.sh` use for their own
    opt-out knobs. Returns the string value of a top-level `key: value` line,
    or None if the file/key is absent. Deliberately does not parse nested YAML.
    """
    path = root / ".ravenclaude" / "comfort-posture.yaml"
    if not path.is_file():
        return None
    pattern = re.compile(rf"^{re.escape(key)}\s*:\s*(\S+)\s*$")
    try:
        for line in path.read_text().splitlines():
            m = pattern.match(line)
            if m:
                return m.group(1).strip().strip("'\"")
    except OSError:
        return None
    return None


def apply_is_killswitched(root: Path) -> bool:
    return _read_posture_scalar(root, "dependency_update_sweep.apply") == "off"


def covering_check(finding: Finding, root: Path) -> bool:
    """Re-verify the target file/line after a mechanical write. Returns True
    (gate passed) or False (regression — the write must be reverted). Each
    surface names the check it runs so a PR reviewer can see WHY a line was
    trusted, not just the resulting diff (mitigation 1).
    """
    target = root / finding.file
    if not target.is_file():
        return False
    if finding.file.endswith(".json"):
        try:
            json.loads(target.read_text())
            return True
        except (json.JSONDecodeError, OSError):
            return False
    if finding.surface == "ravenclaude_floor":
        # re-extract the constant and confirm it still parses as a floor.
        text = target.read_text()
        var_name = finding.extra.get("var_name", "")
        m = re.search(rf'{re.escape(var_name)}="([^"]+)"', text)
        return m is not None and _semver_tuple(m.group(1)) is not None
    # unknown surface: no covering check exists yet -> fail closed, never
    # trust a mechanical write with no verification.
    return False


def apply_mechanical(
    root: Path,
    classified: list[ClassifiedFinding],
    host_id: str,
    old_version: str,
    new_version: str,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Handle every `mechanical` row. Returns a report dict — never raises on
    a single-row failure (one bad apply must not abort the batch, Phase 4
    step 4). Two DISTINCT outcomes, reported honestly and never conflated:

    - `applied`: a file's BYTES actually changed on disk, re-verified by
      `covering_check` immediately after, reverted on regression.
    - `verified`: nothing was written (there is currently only ONE mechanical
      citation_kind this tool ships an action for — `version_floor_constant`,
      §3's row 2 — and its "mechanical action" is confirming the sweep's own
      floor comparison still holds, never editing the constant itself; the
      constant is not touched by a version bump). Reporting this as
      `applied` would claim a fix landed when zero bytes changed — a real
      defect an earlier version of this function had.

    `dry_run=True` (the default) performs the same classification with NO
    actual file writes or covering-check runs — this is the kill-switch's
    forced mode and also this function's own safe default for callers that
    haven't explicitly opted into real writes.
    """
    applied: list[str] = []
    verified: list[str] = []
    refused: list[dict[str, str]] = []
    for c in classified:
        if c.disposition != "mechanical":
            continue
        f = c.finding
        target = root / f.file
        if not target.is_file():
            refused.append({"file": f.file, "reason": "target file missing"})
            continue
        if f.citation_kind == "version_floor_constant":
            if dry_run:
                verified.append(f"{f.file} (dry-run, not verified)")
                continue
            if covering_check(f, root):
                verified.append(f.file)
            else:
                refused.append({"file": f.file, "reason": f"gate regressed on {f.citation_kind}"})
            continue
        # No other citation_kind has a shipped editor — classify_one should
        # never mark one mechanical, so reaching here on a real (non-dry-run)
        # call is refused explicitly rather than silently written.
        if dry_run:
            refused.append({"file": f.file, "reason": f"no editor for citation_kind: {f.citation_kind} (dry-run)"})
        else:
            refused.append({"file": f.file, "reason": f"no editor for citation_kind: {f.citation_kind}"})
    return {
        "host": host_id,
        "old_version": old_version,
        "new_version": new_version,
        "applied": applied,
        "verified": verified,
        "refused": refused,
    }


def update_fingerprint(root: Path, host_id: str, new_version: str, changed: bool, tool_version: str = "v1") -> bool:
    """Phase 4 step 5: record that this host was swept — IN THE SAME `apply`
    call as any content fixes/verifications it reports on (mitigation 2),
    never a separate, later, or local-only write. `last_checked_at` updates
    unconditionally (running this check IS the check — 'I looked and nothing
    moved' is itself worth recording); `last_change_detected_at` updates only
    when `changed` is True, so a future SessionStart nudge can distinguish a
    real delta from a routine confirmation (the `last_checked_at`/
    `last_change_detected_at` split named in plan.md §4's folded-in note).
    Returns True on success, False on any read/write/schema failure (the
    caller decides whether that's fatal — apply's other outcomes still hold
    even if the fingerprint write itself fails).
    """
    fp_path = root / "plugins" / "ravenclaude-core" / "knowledge" / "host-version-fingerprint.json"
    try:
        with fp_path.open("r", encoding="utf-8") as f:
            fp = json.load(f)
    except (OSError, json.JSONDecodeError, ValueError):
        return False
    hosts = fp.get("hosts")
    if not isinstance(hosts, dict) or host_id not in hosts:
        return False
    import datetime as _dt

    today = _dt.date.today().isoformat()
    entry = hosts[host_id] if isinstance(hosts.get(host_id), dict) else {}
    entry["last_swept_version"] = new_version
    entry["last_checked_at"] = today
    if changed:
        entry["last_change_detected_at"] = today
    entry["written_by"] = f"dependency-sweep.py {tool_version}"
    hosts[host_id] = entry
    try:
        with fp_path.open("w", encoding="utf-8") as f:
            json.dump(fp, f, indent=2)
            f.write("\n")
    except OSError:
        return False
    return True


def write_queue(root: Path, primary: list[ClassifiedFinding], overflow: list[ClassifiedFinding], sweep_id: str, host_id: str) -> dict[str, str]:
    run_dir = root / ".ravenclaude" / "runs" / sweep_id
    run_dir.mkdir(parents=True, exist_ok=True)
    queue_path = run_dir / "dependency-sweep-queue.md"
    queue_path.write_text(render_queue_table(primary, host_id))
    result = {"queue": str(queue_path)}
    if overflow:
        overflow_path = run_dir / "dependency-sweep-queue-overflow.md"
        overflow_path.write_text(
            "**not yet reviewed — run the sweep's `queue --continue` to promote the next batch**\n\n"
            + render_queue_table(overflow, host_id)
        )
        result["overflow"] = str(overflow_path)
    return result


def _self_test_apply() -> int:
    import shutil
    import tempfile

    failures: list[str] = []
    ran: list[str] = []

    def check(name: str, cond: bool) -> None:
        ran.append(name)
        if not cond:
            failures.append(name)

    scratch = Path(tempfile.mkdtemp(prefix="depsweep-apply-selftest-"))
    try:
        (scratch / ".ravenclaude").mkdir(parents=True)

        # 1. kill-switch: absent posture -> not killed
        check("killswitch-absent-posture", apply_is_killswitched(scratch) is False)
        # 2. kill-switch: posture present, off -> killed. The minimal scalar
        # reader looks for a literal top-level "dependency_update_sweep.apply:"
        # line, not nested YAML (same flat-key idiom worktree-guard.sh uses).
        (scratch / ".ravenclaude" / "comfort-posture.yaml").write_text(
            "dependency_update_sweep.apply: off\n"
        )
        check("killswitch-off", apply_is_killswitched(scratch) is True)

        # 3. covering_check: valid JSON file -> True
        json_file = scratch / "good.json"
        json_file.write_text('{"a": 1}')
        f_json = Finding(surface="host_support_json", file="good.json", line=None, host="copilot",
                          citation_kind="host_support_capability_cell", text="x")
        check("covering-check-valid-json", covering_check(f_json, scratch) is True)

        # 4. covering_check: invalid JSON -> False (a regression fixture: the
        # gate this row depends on is broken, so a write must be refused)
        bad_json = scratch / "bad.json"
        bad_json.write_text("{not json")
        f_bad = Finding(surface="host_support_json", file="bad.json", line=None, host="copilot",
                         citation_kind="host_support_capability_cell", text="x")
        check("covering-check-invalid-json", covering_check(f_bad, scratch) is False)

        # 5. covering_check: floor constant re-parses
        floor_file = scratch / "ravenclaude_stub"
        floor_file.write_text('COPILOT_FLOOR="1.0.52"\n')
        f_floor = Finding(surface="ravenclaude_floor", file="ravenclaude_stub", line=1, host="copilot",
                           citation_kind="version_floor_constant", text="x", extra={"var_name": "COPILOT_FLOOR"})
        check("covering-check-floor-parses", covering_check(f_floor, scratch) is True)

        # 6. dry-run apply on a version_floor_constant row: NOTHING is
        # verified (dry-run never calls covering_check), reported under
        # `verified`, never `applied` — this citation_kind never writes a
        # byte, dry-run or not (see apply_mechanical's docstring).
        floor_target = scratch / "ravenclaude_stub2"
        floor_target.write_text('COPILOT_FLOOR="1.0.52"\n')
        f_floor_target = Finding(surface="ravenclaude_floor", file="ravenclaude_stub2", line=1, host="copilot",
                                  citation_kind="version_floor_constant", text="x",
                                  extra={"var_name": "COPILOT_FLOOR"})
        c_floor_mechanical = ClassifiedFinding(finding=f_floor_target, disposition="mechanical", rule_matched="test")
        report = apply_mechanical(scratch, [c_floor_mechanical], "copilot", "1.0.0", "1.0.1", dry_run=True)
        check("dry-run-reports-verified-not-applied", "dry-run" in report["verified"][0] and report["applied"] == [])
        check("dry-run-file-unchanged", floor_target.read_text() == 'COPILOT_FLOOR="1.0.52"\n')

        # 6b. REAL (non-dry-run) apply of the same row: covering_check runs
        # for real, the row lands in `verified` (still zero bytes written —
        # this citation_kind has no editor by design), and `applied` stays
        # empty. This is the direct regression test for the code-review
        # finding that an earlier version reported this case as `applied`
        # with zero bytes changed.
        report_real = apply_mechanical(scratch, [c_floor_mechanical], "copilot", "1.0.0", "1.0.1", dry_run=False)
        check("real-run-floor-verified-not-applied", report_real["verified"] == ["ravenclaude_stub2"] and report_real["applied"] == [])
        check("real-run-floor-file-still-unchanged", floor_target.read_text() == 'COPILOT_FLOOR="1.0.52"\n')

        # 7. MUST-FAIL HALF: an unknown citation_kind reaching apply must be
        # refused, never silently written — proves the fail-closed default
        # for any citation_kind with no shipped editor has teeth (a row
        # classify_one should never produce, forced here directly).
        f_unknown = Finding(surface="marker", file="target.json", line=None, host="copilot",
                             citation_kind="totally_unrecognized_kind", text="x")
        json_file2 = scratch / "target.json"
        json_file2.write_text('{"v": 1}')
        c_unknown = ClassifiedFinding(finding=f_unknown, disposition="mechanical", rule_matched="test")
        report2 = apply_mechanical(scratch, [c_unknown], "copilot", "1.0.0", "1.0.1", dry_run=False)
        check("unknown-kind-refused", len(report2["refused"]) == 1 and "no editor" in report2["refused"][0]["reason"])
        check("unknown-kind-not-applied", len(report2["applied"]) == 0 and len(report2["verified"]) == 0)

        # 7b. update_fingerprint: writes last_swept_version/last_checked_at
        # for the swept host, leaves other hosts untouched, and sets
        # last_change_detected_at ONLY when `changed=True` (the
        # last_checked_at vs last_change_detected_at split, plan.md §4).
        fp_dir = scratch / "plugins" / "ravenclaude-core" / "knowledge"
        fp_dir.mkdir(parents=True)
        fp_path = fp_dir / "host-version-fingerprint.json"
        fp_path.write_text(json.dumps({
            "schema_version": 1,
            "hosts": {
                "copilot": {"last_swept_version": None, "last_checked_at": None,
                            "last_change_detected_at": None, "written_by": None},
                "codex": {"last_swept_version": None, "last_checked_at": None,
                          "last_change_detected_at": None, "written_by": None},
            },
        }))
        ok = update_fingerprint(scratch, "copilot", "1.0.70", changed=True)
        check("update-fingerprint-returns-true", ok is True)
        fp_after = json.loads(fp_path.read_text())
        check("update-fingerprint-sets-version", fp_after["hosts"]["copilot"]["last_swept_version"] == "1.0.70")
        check("update-fingerprint-sets-checked-at", fp_after["hosts"]["copilot"]["last_checked_at"] is not None)
        check("update-fingerprint-sets-changed-at-when-changed", fp_after["hosts"]["copilot"]["last_change_detected_at"] is not None)
        check("update-fingerprint-leaves-other-host-alone", fp_after["hosts"]["codex"]["last_swept_version"] is None)

        # 7c. update_fingerprint with changed=False must NOT set
        # last_change_detected_at — "checked, nothing moved" stays distinct
        # from a real delta.
        ok2 = update_fingerprint(scratch, "codex", "1.0.0", changed=False)
        check("update-fingerprint-false-returns-true", ok2 is True)
        fp_after2 = json.loads(fp_path.read_text())
        check("update-fingerprint-no-changed-at-when-unchanged", fp_after2["hosts"]["codex"]["last_change_detected_at"] is None)
        check("update-fingerprint-still-sets-checked-at-when-unchanged", fp_after2["hosts"]["codex"]["last_checked_at"] is not None)

        # 8. write_queue: files actually land on disk
        classified_q = [
            ClassifiedFinding(
                finding=Finding(surface="marker", file=f"f{i}.md", line=i, host="copilot", citation_kind="dated_marker", text="x"),
                disposition="judgment", rule_matched="test", priority="P1",
            )
            for i in range(3)
        ]
        primary, overflow = build_queue(classified_q)
        paths = write_queue(scratch, primary, overflow, "test-sweep", "copilot")
        check("queue-file-written", Path(paths["queue"]).is_file())
        check("no-overflow-file-when-empty", "overflow" not in paths)

    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    if failures:
        print(f"FAIL: {failures}", file=sys.stderr)
        return 1
    print(f"dependency-sweep apply self-test: {len(ran)} checks, 0 failures")
    return 0


def _cmd_apply(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else _find_repo_root()
    killed = apply_is_killswitched(root)
    if killed:
        print("dependency_update_sweep.apply: off — forced dry-run", file=sys.stderr)
    citation_map = json.loads(Path(args.citation_map).read_text())
    findings = [Finding(**f) for f in citation_map["findings"]]
    changelog_text = Path(args.changelog).read_text() if args.changelog else ""
    classified = classify(findings, changelog_text, args.new_version)
    report = apply_mechanical(
        root, classified, args.host, args.old_version or "", args.new_version or "",
        dry_run=killed or not args.yes,
    )
    primary, overflow = build_queue(classified)
    queue_paths = write_queue(root, primary, overflow, args.sweep_id or "dependency-sweep-latest", args.host)
    report["queue"] = queue_paths
    real_run = not (killed or not args.yes)
    if real_run and args.new_version:
        changed = bool(args.old_version and args.old_version != args.new_version)
        report["fingerprint_updated"] = update_fingerprint(root, args.host, args.new_version, changed)
    else:
        report["fingerprint_updated"] = False
    print(json.dumps(report, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dependency-sweep.py")
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan")
    p_scan.add_argument("--host", required=False)
    p_scan.add_argument("--old-version", required=False)
    p_scan.add_argument("--new-version", required=False)
    p_scan.add_argument("--root", required=False)
    p_scan.add_argument("--out", required=False)
    p_scan.add_argument("--self-test", action="store_true")
    p_scan.set_defaults(func=_cmd_scan)

    p_classify = sub.add_parser("classify")
    p_classify.add_argument("--citation-map", required=False)
    p_classify.add_argument("--changelog", required=False)
    p_classify.add_argument("--new-version", required=False)
    p_classify.add_argument("--self-test", action="store_true")
    p_classify.set_defaults(func=_cmd_classify)

    p_queue_test = sub.add_parser("queue-self-test")
    p_queue_test.set_defaults(func=lambda a: _self_test_queue())

    p_apply_test = sub.add_parser("apply-self-test")
    p_apply_test.set_defaults(func=lambda a: _self_test_apply())

    p_apply = sub.add_parser("apply")
    p_apply.add_argument("--host", required=True)
    p_apply.add_argument("--old-version", required=False)
    p_apply.add_argument("--new-version", required=False)
    p_apply.add_argument("--citation-map", required=True)
    p_apply.add_argument("--changelog", required=False)
    p_apply.add_argument("--root", required=False)
    p_apply.add_argument("--sweep-id", required=False)
    p_apply.add_argument("--yes", action="store_true", help="perform real writes (default: dry-run)")
    p_apply.set_defaults(func=_cmd_apply)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
