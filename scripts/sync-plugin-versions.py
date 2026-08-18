#!/usr/bin/env python3
"""sync-plugin-versions.py — one hand-edited version per plugin, derived everywhere else.

A plugin's version used to be hand-maintained in two committed files that CI
compares against each other (AGENTS.md § "Modifying an existing plugin"):

    plugins/<name>/.claude-plugin/plugin.json   ->  version
    .claude-plugin/marketplace.json             ->  plugins[].version

Two hand-edited copies of one fact is a merge-conflict generator, not a check.
Measured 2026-08-17: one PR was re-bumped THREE times (0.273.0 -> 0.274.0 ->
0.275.0) purely because concurrent PRs serialised on those two files, and two
further PRs needed manual conflict resolution for the same reason.

This script makes `plugins/<name>/.claude-plugin/plugin.json` the SINGLE SOURCE
OF TRUTH and DERIVES the marketplace catalog entry from it. Only the manifest is
edited by hand; the catalog is regenerated. `plugins/ravenclaude-core/copilot/
plugin.json` is a third copy and is already generated — by
`scripts/generate-copilot-plugin.py`, which still has to be re-run after a bump
(deliberately NOT called from here: that generator projects the whole agent tree,
not just a version, and folding it in would make a version sync a tree rewrite).

⛔ BYTE-STABILITY. `.claude-plugin/marketplace.json` is NOT in `.prettierignore`,
so the whole-tree `prettier --check .` in CI reads it. A `json.dump()` round-trip
would reformat 252 KB of catalog and turn every version bump into a formatting
failure. So the write path is a LINE-LOCAL substitution of the version literal
only: every other byte of the file is untouched by construction. The line scan is
cross-checked against `json.load()` of the same text before any write, and a
disagreement between the two readers is an ambiguity, not something to guess at.

⛔ FAILS LOUDLY, NEVER GUESSES. Silently "fixing" a mismatch it does not
understand is the failure mode this script exists to avoid. Each of these is a
reported finding, not a repair:
  * a marketplace entry with no plugins/<name>/.claude-plugin/plugin.json
  * a plugins/<name>/.claude-plugin/plugin.json with no marketplace entry
  * a plugins/<name>/ directory carrying no manifest at all
  * unparseable or unreadable JSON on either side
  * a missing / blank / non-string `version` on either side
  * a duplicate plugin name in the catalog
  * a plugin.json whose `name` disagrees with its own directory
  * a line scan that cannot account for every catalog entry

Exit codes:
    0  clean — or, in write mode, written successfully
    2  a finding of ANY kind: drift, structural ambiguity, or an unreadable file

Exit 1 is deliberately never used for a finding. This repo has shipped
non-blocking exit-1 gates before, and the audit suite asserts `rc -eq 2` here so
that a fail-closed exit is itself regression-locked.

Usage:
    python3 scripts/sync-plugin-versions.py             # write derived versions
    python3 scripts/sync-plugin-versions.py --check     # report drift, write nothing
    python3 scripts/sync-plugin-versions.py --self-test # prove each finding class distinguishes
    python3 scripts/sync-plugin-versions.py --must-fail # plant real drift, prove it reddens
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE_REL = ".claude-plugin/marketplace.json"
MANIFEST_TAIL = Path(".claude-plugin") / "plugin.json"

# prettier prints the catalog at 2-space indent, so a plugins[] entry's OWN keys
# sit at exactly 6 spaces. Anything nested inside an entry ("author", "keywords")
# sits at 8+, and the root/metadata keys sit at 2/4. Both patterns are anchored,
# so neither can match a nested or top-level key. This is still only a heuristic,
# which is why scan_version_lines() cross-checks it against json.load().
NAME_LINE_RE = re.compile(r'^ {6}"name": "([^"]*)",$')
VERSION_LINE_RE = re.compile(r'^( {6}"version": ")([^"]*)(",?)$')


# ── Readers ──────────────────────────────────────────────────────────────────


def _read_json(path: Path) -> tuple[object | None, str | None]:
    """Parse one JSON file. Returns (document, error); exactly one is None."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"unreadable ({exc})"
    try:
        return json.loads(raw), None
    except json.JSONDecodeError as exc:
        return None, f"unparseable JSON ({exc})"


def _version_of(obj: dict, label: str, findings: list[str]) -> str | None:
    value = obj.get("version")
    if value is None:
        findings.append(f"{label}: no `version` field")
        return None
    if not isinstance(value, str) or not value.strip():
        findings.append(f"{label}: `version` is not a non-empty string ({value!r})")
        return None
    return value


def collect(root: Path) -> tuple[dict, dict, list[str]]:
    """Read both sides. Returns (source_versions, catalog_versions, findings)."""
    findings: list[str] = []
    mp_path = root / MARKETPLACE_REL
    doc, err = _read_json(mp_path)
    if err is not None:
        return {}, {}, [f"{MARKETPLACE_REL}: {err}"]
    if not isinstance(doc, dict) or not isinstance(doc.get("plugins"), list):
        return {}, {}, [f"{MARKETPLACE_REL}: no top-level `plugins` array"]

    catalog: dict[str, str | None] = {}
    for index, entry in enumerate(doc["plugins"]):
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
            findings.append(f"{MARKETPLACE_REL}: plugins[{index}] has no string `name`")
            continue
        name = entry["name"]
        if name in catalog:
            findings.append(f"{MARKETPLACE_REL}: duplicate catalog entry for '{name}'")
            continue
        catalog[name] = _version_of(entry, f"{MARKETPLACE_REL} '{name}'", findings)

    source: dict[str, str | None] = {}
    plugins_dir = root / "plugins"
    if not plugins_dir.is_dir():
        findings.append("plugins/: not a directory")
        return source, catalog, findings

    for child in sorted(plugins_dir.iterdir()):
        if not child.is_dir():
            continue
        manifest = child / MANIFEST_TAIL
        rel = f"plugins/{child.name}/.claude-plugin/plugin.json"
        if not manifest.is_file():
            findings.append(f"plugins/{child.name}/ is a plugin directory with no {rel}")
            continue
        obj, err = _read_json(manifest)
        if err is not None:
            findings.append(f"{rel}: {err}")
            source[child.name] = None
            continue
        if not isinstance(obj, dict):
            findings.append(f"{rel}: top level is not a JSON object")
            source[child.name] = None
            continue
        declared = obj.get("name")
        if declared != child.name:
            findings.append(f"{rel}: `name` is {declared!r} but its directory is '{child.name}'")
        source[child.name] = _version_of(obj, rel, findings)

    for name in sorted(set(catalog) - set(source)):
        findings.append(
            f"'{name}' is listed in {MARKETPLACE_REL} but has no "
            f"plugins/{name}/.claude-plugin/plugin.json to derive a version from"
        )
    for name in sorted(set(source) - set(catalog)):
        findings.append(
            f"plugins/{name}/.claude-plugin/plugin.json exists but '{name}' has no "
            f"entry in {MARKETPLACE_REL}"
        )
    return source, catalog, findings


# ── The byte-stable write path ───────────────────────────────────────────────


def scan_version_lines(text: str, catalog: dict) -> tuple[dict, list[str]]:
    """Locate each catalog entry's version literal as (line_index, prefix, value, suffix).

    The scan is cross-checked against `catalog`, which came from json.load() of
    the SAME text. That cross-check is the positive control on this parser: it
    can only stay silent when the two independent readers agree on every name
    AND every value.
    """
    findings: list[str] = []
    lines = text.split("\n")
    found: dict[str, tuple[int, str, str, str]] = {}
    seen_names: list[str] = []
    current: str | None = None

    for index, line in enumerate(lines):
        name_match = NAME_LINE_RE.match(line)
        if name_match is not None:
            current = name_match.group(1)
            seen_names.append(current)
            continue
        version_match = VERSION_LINE_RE.match(line)
        if version_match is None:
            continue
        if current is None:
            findings.append(
                f"line {index + 1}: an entry-level `version` line with no `name` above it"
            )
            continue
        if current in found:
            findings.append(f"'{current}': two entry-level `version` lines (line {index + 1})")
            continue
        found[current] = (
            index,
            version_match.group(1),
            version_match.group(2),
            version_match.group(3),
        )

    if len(seen_names) != len(set(seen_names)):
        findings.append("the line scan saw duplicate entry-level `name` lines")

    scanned = {name: value[2] for name, value in found.items()}
    expected = {name: version for name, version in catalog.items() if version is not None}
    if scanned != expected:
        unscanned = sorted(set(expected) - set(scanned))
        unexpected = sorted(set(scanned) - set(expected))
        mismatched = sorted(n for n in set(scanned) & set(expected) if scanned[n] != expected[n])
        findings.append(
            "the line scan of the catalog disagrees with json.load() of the same file "
            f"(unscanned={unscanned}, unexpected={unexpected}, value-mismatch={mismatched}) "
            "— refusing to write"
        )
    return found, findings


def plan_and_apply(
    root: Path, source: dict, catalog: dict, write: bool
) -> tuple[list[tuple[str, str, str]], list[str]]:
    """Compute drift and, when `write`, substitute the version literals in place."""
    mp_path = root / MARKETPLACE_REL
    try:
        text = mp_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [], [f"{MARKETPLACE_REL}: unreadable ({exc})"]

    found, findings = scan_version_lines(text, catalog)
    if findings:
        return [], findings

    lines = text.split("\n")
    drift: list[tuple[str, str, str]] = []
    for name in sorted(catalog):
        expected = source.get(name)
        actual = catalog.get(name)
        if expected is None or actual is None or expected == actual:
            continue
        drift.append((name, expected, actual))
        index, prefix, _old, suffix = found[name]
        lines[index] = prefix + expected + suffix

    if write and drift:
        # "\n".join over a "\n".split round-trips byte-for-byte, trailing newline
        # included, so nothing but the substituted literals can change.
        mp_path.write_text("\n".join(lines), encoding="utf-8")
    return drift, []


def evaluate(root: Path, write: bool = False) -> tuple[int, list[str]]:
    """Run one pass. Returns (exit_code, report_lines). Prints nothing."""
    source, catalog, findings = collect(root)
    if findings:
        return 2, ["AMBIGUITY: refusing to guess. Fix these by hand first:"] + [
            f"  - {f}" for f in findings
        ]

    drift, findings = plan_and_apply(root, source, catalog, write=write)
    if findings:
        return 2, ["AMBIGUITY: refusing to guess. Fix these by hand first:"] + [
            f"  - {f}" for f in findings
        ]

    if not drift:
        return 0, [
            f"in sync: {MARKETPLACE_REL} versions are derived from all "
            f"{len(catalog)} plugin manifests"
        ]

    width = max(len(name) for name, _, _ in drift)
    if write:
        return 0, [f"synced {len(drift)} catalog version(s) from plugin.json:"] + [
            f"  {name.ljust(width)}  {have} -> {want}" for name, want, have in drift
        ]
    return 2, [
        f"DRIFT: {MARKETPLACE_REL} is not derived from plugin.json "
        f"({len(drift)} of {len(catalog)} plugins):",
        *[f"  {name.ljust(width)}  expected {want}  found {have}" for name, want, have in drift],
        "Fix: python3 scripts/sync-plugin-versions.py",
    ]


# ── Self-test: prove every finding class actually distinguishes ──────────────


def _write_fixture(root: Path, manifests: dict, catalog: list) -> None:
    """Build a minimal prettier-shaped tree. `manifests` values may be raw strings."""
    (root / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    blocks = []
    for entry in catalog:
        chunk = [
            "    {",
            f'      "name": "{entry["name"]}",',
            f'      "source": "./plugins/{entry["name"]}",',
        ]
        if "version" in entry:
            chunk.append(f'      "version": "{entry["version"]}",')
        chunk += ['      "author": {', '        "name": "Fixture"', "      }", "    }"]
        blocks.append("\n".join(chunk))
    document = '{\n  "name": "fixture",\n  "plugins": [\n' + ",\n".join(blocks) + "\n  ]\n}\n"
    (root / MARKETPLACE_REL).write_text(document, encoding="utf-8")
    for name, payload in manifests.items():
        target = root / "plugins" / name / ".claude-plugin"
        target.mkdir(parents=True, exist_ok=True)
        text = payload if isinstance(payload, str) else json.dumps(payload, indent=2) + "\n"
        (target / "plugin.json").write_text(text, encoding="utf-8")


def _manifest(name: str, version: str) -> dict:
    return {"name": name, "version": version}


def _cases() -> list[tuple[str, dict, list, int]]:
    """(label, manifests, catalog, expected_check_rc). rc 0 = clean, 2 = finding."""
    good_manifests = {"alpha": _manifest("alpha", "1.2.3"), "beta": _manifest("beta", "0.4.0")}
    good_catalog = [{"name": "alpha", "version": "1.2.3"}, {"name": "beta", "version": "0.4.0"}]
    return [
        ("clean tree", good_manifests, good_catalog, 0),
        (
            "drift",
            good_manifests,
            [{"name": "alpha", "version": "1.2.2"}, {"name": "beta", "version": "0.4.0"}],
            2,
        ),
        (
            "catalog entry with no plugin.json",
            {"alpha": _manifest("alpha", "1.2.3")},
            good_catalog,
            2,
        ),
        (
            "plugin.json with no catalog entry",
            good_manifests,
            [{"name": "alpha", "version": "1.2.3"}],
            2,
        ),
        (
            "malformed plugin.json",
            {"alpha": "{ not json", "beta": _manifest("beta", "0.4.0")},
            good_catalog,
            2,
        ),
        (
            "plugin.json with no version",
            {"alpha": {"name": "alpha"}, "beta": _manifest("beta", "0.4.0")},
            good_catalog,
            2,
        ),
        (
            "plugin.json version is not a string",
            {"alpha": {"name": "alpha", "version": 3}, "beta": _manifest("beta", "0.4.0")},
            good_catalog,
            2,
        ),
        (
            "catalog entry with no version",
            good_manifests,
            [{"name": "alpha"}, {"name": "beta", "version": "0.4.0"}],
            2,
        ),
        (
            "duplicate catalog name",
            good_manifests,
            [
                {"name": "alpha", "version": "1.2.3"},
                {"name": "alpha", "version": "1.2.3"},
                {"name": "beta", "version": "0.4.0"},
            ],
            2,
        ),
        (
            "plugin.json name disagrees with its directory",
            {"alpha": _manifest("typo", "1.2.3"), "beta": _manifest("beta", "0.4.0")},
            good_catalog,
            2,
        ),
    ]


def self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)

        for number, (label, manifests, catalog, expected_rc) in enumerate(_cases()):
            root = base / f"case{number}"
            _write_fixture(root, manifests, catalog)
            rc, report = evaluate(root, write=False)
            if rc != expected_rc:
                failures.append(f"{label}: --check exited {rc}, expected {expected_rc}")
            print(f"  [{'ok ' if rc == expected_rc else 'BAD'}] {label}: rc={rc} | {report[0]}")

        # A malformed CATALOG is its own case: the fixture builder only emits
        # well-formed catalogs, so plant the damage directly.
        root = base / "badcatalog"
        _write_fixture(
            root, {"alpha": _manifest("alpha", "1.2.3")}, [{"name": "alpha", "version": "1.2.3"}]
        )
        (root / MARKETPLACE_REL).write_text("{ not json\n", encoding="utf-8")
        rc, report = evaluate(root, write=False)
        if rc != 2:
            failures.append(f"malformed marketplace.json: --check exited {rc}, expected 2")
        label = "ok " if rc == 2 else "BAD"
        print(f"  [{label}] malformed marketplace.json: rc={rc} | {report[0]}")

        # Convergence + idempotency, on a drifted fixture, byte-compared against
        # the clean fixture built from the same inputs.
        manifests = {"alpha": _manifest("alpha", "1.2.3"), "beta": _manifest("beta", "0.4.0")}
        beta = {"name": "beta", "version": "0.4.0"}
        clean = base / "converge-clean"
        _write_fixture(clean, manifests, [{"name": "alpha", "version": "1.2.3"}, beta])
        drifted = base / "converge"
        _write_fixture(drifted, manifests, [{"name": "alpha", "version": "0.0.1"}, beta])
        before = (drifted / MARKETPLACE_REL).read_bytes()

        rc, _ = evaluate(drifted, write=True)
        first = (drifted / MARKETPLACE_REL).read_bytes()
        if rc != 0:
            failures.append(f"write pass exited {rc}, expected 0")
        if first == before:
            failures.append("write pass left the drifted catalog unchanged (it is a no-op)")
        if first != (clean / MARKETPLACE_REL).read_bytes():
            failures.append("write pass did not converge byte-for-byte onto the clean fixture")

        rc, _ = evaluate(drifted, write=True)
        if rc != 0 or (drifted / MARKETPLACE_REL).read_bytes() != first:
            failures.append("second write pass was NOT a byte-identical no-op (not idempotent)")
        rc, _ = evaluate(drifted, write=False)
        if rc != 0:
            failures.append(f"--check after a write still reports rc={rc}")
        print(f"  [{'ok ' if not failures else 'BAD'}] converge + idempotent + byte-stable")

    if failures:
        print("SELF-TEST FAILED:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 2
    print("self-test ok: every finding class distinguishes, and the write converges idempotently")
    return 0


def _mirror(root: Path, work: Path) -> None:
    """Copy the REAL two surfaces (catalog + every manifest) into a scratch root."""
    (work / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / MARKETPLACE_REL, work / MARKETPLACE_REL)
    for child in sorted((root / "plugins").iterdir()):
        manifest = child / MANIFEST_TAIL
        if manifest.is_file():
            target = work / "plugins" / child.name / ".claude-plugin"
            target.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(manifest, target / "plugin.json")


def must_fail(root: Path) -> int:
    """Plant real drift in a mirror of the live tree and prove --check reddens on it."""
    with tempfile.TemporaryDirectory() as td:
        work = Path(td) / "mirror"
        _mirror(root, work)

        rc, report = evaluate(work, write=False)
        if rc != 0:
            print(
                f"MIRROR NOT CLEAN (rc={rc}) — the control failed, not the teeth:", file=sys.stderr
            )
            for line in report:
                print(line, file=sys.stderr)
            return 1

        path = work / MARKETPLACE_REL
        lines = path.read_text(encoding="utf-8").split("\n")
        planted = None
        for index, line in enumerate(lines):
            match = VERSION_LINE_RE.match(line)
            if match is not None:
                planted = (index, match.group(2))
                lines[index] = match.group(1) + "9.999.9" + match.group(3)
                break
        if planted is None:
            print("could not plant drift: no entry-level version line found", file=sys.stderr)
            return 1
        path.write_text("\n".join(lines), encoding="utf-8")

        rc, report = evaluate(work, write=False)
        for line in report:
            print(line)
        if rc == 0:
            print(
                f"TEETH FAILED: planted 9.999.9 over {planted[1]} at line {planted[0] + 1} "
                "and --check still reported clean",
                file=sys.stderr,
            )
            return 0
        print(f"teeth ok: the planted 9.999.9 was caught, --check exited {rc}")
        return rc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check", action="store_true", help="report drift and exit 2; write nothing"
    )
    parser.add_argument("--self-test", action="store_true", help="prove each finding distinguishes")
    parser.add_argument("--must-fail", action="store_true", help="plant real drift; expect exit 2")
    parser.add_argument("--root", default=str(REPO_ROOT), help="repo root (default: this checkout)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if args.self_test:
        return self_test()
    if args.must_fail:
        return must_fail(root)

    rc, report = evaluate(root, write=not args.check)
    for line in report:
        print(line, file=sys.stderr if rc != 0 else sys.stdout)
    return rc


if __name__ == "__main__":
    sys.exit(main())
