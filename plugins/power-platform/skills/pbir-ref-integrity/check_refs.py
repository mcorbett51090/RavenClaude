#!/usr/bin/env python3
"""PBIR cross-file referential-integrity validator.

Where ravenclaude-core's `pbir-layout-engine/lint.py` checks ONE page's
geometry + per-visual schema, this validator answers the report-wide question
that single-page linting structurally cannot: **do the cross-file references
in a PBIR Enhanced report's `definition/` tree actually resolve?**  Dangling
references are the failure class that pbir-utils' `validate` / `sanitize`
commands and pbir.tools' `validate` target — a bookmark that points at a
deleted visual, a `visualInteractions` entry naming a visual that no longer
exists, a page-order list that omits or invents a page, an `activePageName`
that names a missing page.  These deploy "clean" (no schema error) and then
misbehave at render time, so they are exactly the silent-failure class this
marketplace's PBIR knowledge bank keeps cataloguing.

Mimicked from (researched 2026-06-08):
  * akhilannan/pbir-utils — `validate` / `sanitize` ("removes invalid bookmarks
    referencing deleted pages/visuals, and unreferenced bookmarks"),
    `set-page-order`, `set-active-page`.
    https://akhilannan.github.io/pbir-utils/cli/  (retrieved 2026-06-08)
  * maxanatsko/pbir.tools — `validate` ("run `pbir validate` before you consider
    the edit finished"), the `Report/Page/Visual` path model.
    https://github.com/maxanatsko/pbir.tools/blob/main/cli/README.md
    (retrieved 2026-06-08)

We re-implement the *idea* (deterministic referential-integrity validation over
the PBIR folder model) in our own stdlib-only code against the PBIR file facts
documented in
`plugins/power-platform/knowledge/pbir-enhanced-reference.md`.  We do NOT use,
vendor, or shell out to either tool.

PBIR `definition/` folder model this validator reads
----------------------------------------------------
    <Report>.Report/definition/
      report.json                              report-level settings + filters
      pages/
        pages.json                             { pageOrder: [...], activePageName }
        <pageId>/
          page.json                            { name, displayName, displayOption,
                                                 visualInteractions[], filterConfig }
          visuals/
            <visualId>/visual.json             { name, position, visual{...} }
      bookmarks/
        bookmarks.json                         { items: [...] }   (optional)
        <bookmarkId>.bookmark.json             { name, displayName,
                                                 explorationState{ activeSection,
                                                 sections{ <pageName>: { visualContainers } } } }

Real-world tolerance: the layout of `pages.json` / `bookmarks.json` and the
exact bookmark `explorationState` shape have varied across schema majors, so
every reader here is defensive — a missing/renamed key degrades to "nothing to
check for that reference class", never a crash.  The validator reports what it
*could* resolve; it never invents a finding from an unparseable file (that is a
`parse` finding instead).

Checks
------
  ref-1  bookmark -> page          a bookmark's target page must exist
  ref-2  bookmark -> visual        a bookmark's referenced visuals must exist on
                                   that page
  ref-3  interaction -> visual     page.json visualInteractions source/target
                                   must be visuals on that same page
  ref-4  page-order integrity      pages.json pageOrder must be a permutation of
                                   the on-disk page ids (no missing, no invented,
                                   no duplicate)
  ref-5  active-page -> page       pages.json activePageName (and each bookmark's
                                   activeSection) must name an existing page
  ref-6  unique visual name        a visual `name` must be unique across the
                                   whole report (PBIR requires report-wide
                                   uniqueness; a collision corrupts bookmarks /
                                   interactions that key on the name)

Purity / dependency contract (identical posture to lint.py)
-----------------------------------------------------------
Stdlib-only, no network, no subprocess.  Reads ONLY under the supplied
`<report-root>`, which MUST NOT contain ".." and MUST resolve inside the
repository root (else exit 2).

Exit codes
----------
  0   no findings (or only info)
  1   one or more error findings (or warning under --strict)
  2   I/O error, parse error, or argv path rejection
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from typing import Literal

VALIDATOR_VERSION = "0.1.0"
SCHEMA_VERSION = "1.0.0"  # contract version of the --format=json envelope

Severity = Literal["info", "warning", "error"]
CheckId = Literal["ref-1", "ref-2", "ref-3", "ref-4", "ref-5", "ref-6", "parse"]

CHECK_DEFINITIONS = [
    ("ref-1", "Bookmark -> page resolves", "error"),
    ("ref-2", "Bookmark -> visual resolves", "warning"),
    ("ref-3", "Interaction -> visual resolves", "error"),
    ("ref-4", "Page-order is a permutation of on-disk pages", "error"),
    ("ref-5", "Active-page / activeSection resolves", "error"),
    ("ref-6", "Visual name unique across report", "error"),
]


@dataclass(frozen=True)
class Finding:
    check_id: CheckId
    severity: Severity
    location: str  # page id / bookmark id / "report"
    message: str
    fix_hint: str


class InputError(Exception):
    """I/O, parse, or path-rejection failure (exit 2)."""


# ── Repo-root + path safety (mirrors lint.py's contract) ─────────────────────
def _repo_root() -> str:
    # check_refs.py lives at
    # plugins/power-platform/skills/pbir-ref-integrity/check_refs.py
    here = os.path.abspath(__file__)
    return os.path.abspath(os.path.join(os.path.dirname(here), "..", "..", "..", ".."))


def _resolve_safe(input_path: str) -> str:
    if ".." in input_path.split(os.sep):
        raise InputError(f"path component '..' is not allowed: {input_path!r}")
    # realpath (not abspath) so an in-repo symlink whose leaf points outside the repo
    # is rejected — abspath doesn't resolve symlinks, so open() would follow it out of
    # the sandbox. Mirror the sibling linters (declarative-visualization, svg-report-lint).
    resolved = os.path.realpath(input_path)
    root = os.path.realpath(_repo_root())
    if os.path.commonpath([resolved, root]) != root:
        raise InputError(f"path resolves outside repo root: {resolved!r}")
    return resolved


# ── Defensive JSON read ──────────────────────────────────────────────────────
def _read_json(path: str, findings: list[Finding], location: str) -> dict | None:
    """Read+parse a JSON object, recording a `parse` finding on failure.

    Returns the dict, or None if the file is absent (silently) or unparseable
    (with a finding). Never raises — a torn/renamed file degrades that
    reference class rather than crashing the whole validation.
    """
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(
            Finding(
                check_id="parse",
                severity="error",
                location=location,
                message=f"could not parse {os.path.relpath(path)}: {exc}",
                fix_hint="Fix the JSON syntax; a torn definition file fails the report at load.",
            )
        )
        return None
    return data if isinstance(data, dict) else None


# ── Report-tree model ────────────────────────────────────────────────────────
@dataclass
class ReportModel:
    pages_dir: str
    page_ids: list[str]  # on-disk page directory names
    # page id -> { "page": <page.json dict>, "visual_names": set[str] }
    pages: dict
    visual_name_owner: dict  # visual name -> list of "pageId/visualDir" it appears in
    bookmarks: list  # list of (bookmark_id, dict)
    pages_index: dict | None  # pages.json content (pageOrder / activePageName)


def _find_definition_root(report_root: str) -> str | None:
    """Locate the `definition/` directory.

    Accepts either a path to a `*.Report` folder (definition is a child) or a
    path that already IS the `definition/` dir.
    """
    cand = os.path.join(report_root, "definition")
    if os.path.isdir(cand):
        return cand
    if os.path.basename(report_root) == "definition" and os.path.isdir(report_root):
        return report_root
    return None


def load_report(report_root: str, findings: list[Finding]) -> ReportModel | None:
    definition = _find_definition_root(report_root)
    if definition is None:
        findings.append(
            Finding(
                check_id="parse",
                severity="error",
                location="report",
                message=f"no `definition/` directory found under {os.path.relpath(report_root)}",
                fix_hint="Point the validator at a `*.Report` folder or its `definition/` directory.",
            )
        )
        return None

    pages_dir = os.path.join(definition, "pages")
    page_ids: list[str] = []
    pages: dict = {}
    visual_name_owner: dict = {}

    def _scan_visuals(page_path: str, entry: str) -> set:
        """Collect a page's visual names into visual_name_owner (report-wide) — run for
        EVERY page dir with a visuals/ subtree, regardless of whether page.json is
        readable. A page whose page.json is absent but which HAS visuals must still
        contribute to ref-6 report-wide uniqueness and the bookmark visual set; the prior
        `continue`-before-scan silently dropped them, so a name collision with a visual
        on another page went undetected as exit 0 (2026-07-13 review). Visual identity is
        visual.json `name`, folder-name fallback (PBIR requires them to match)."""
        names: set[str] = set()
        visuals_dir = os.path.join(page_path, "visuals")
        if os.path.isdir(visuals_dir):
            for vdir in sorted(os.listdir(visuals_dir)):
                vpath = os.path.join(visuals_dir, vdir)
                if not os.path.isdir(vpath):
                    continue
                vjson = _read_json(
                    os.path.join(vpath, "visual.json"),
                    findings,
                    f"pages/{entry}/visuals/{vdir}",
                )
                vname = vjson.get("name") if vjson is not None else None
                vname = str(vname or vdir)
                names.add(vname)
                visual_name_owner.setdefault(vname, []).append(f"{entry}/{vdir}")
        return names

    if os.path.isdir(pages_dir):
        for entry in sorted(os.listdir(pages_dir)):
            page_path = os.path.join(pages_dir, entry)
            if not os.path.isdir(page_path):
                continue  # pages.json is a file, not a page dir
            page_json = _read_json(os.path.join(page_path, "page.json"), findings, f"pages/{entry}")
            page_ids.append(entry)
            # Always scan visuals — even when page.json is absent/unreadable (page_json
            # is None), so those visuals still enter report-wide uniqueness (ref-6).
            visual_names = _scan_visuals(page_path, entry)
            pages[entry] = {
                "page": page_json if page_json is not None else {},
                "visual_names": visual_names,
            }

    pages_index = _read_json(os.path.join(pages_dir, "pages.json"), findings, "pages/pages.json")

    bookmarks: list = []
    bookmarks_dir = os.path.join(definition, "bookmarks")
    if os.path.isdir(bookmarks_dir):
        for entry in sorted(os.listdir(bookmarks_dir)):
            if not entry.endswith(".bookmark.json"):
                continue
            bpath = os.path.join(bookmarks_dir, entry)
            bjson = _read_json(bpath, findings, f"bookmarks/{entry}")
            if bjson is not None:
                bookmarks.append((entry, bjson))

    return ReportModel(
        pages_dir=pages_dir,
        page_ids=page_ids,
        pages=pages,
        visual_name_owner=visual_name_owner,
        bookmarks=bookmarks,
        pages_index=pages_index,
    )


# ── Bookmark target extraction (defensive across schema shapes) ──────────────
def _bookmark_sections(bjson: dict) -> dict:
    """Return the bookmark's per-page section map, tolerating shape drift.

    The canonical shape is:
        explorationState.sections = { "<pageName>": { "visualContainers": {...} } }
    Older / variant shapes nest differently; we read the most common ones and
    degrade to {} when none match.
    """
    state = bjson.get("explorationState")
    if not isinstance(state, dict):
        return {}
    sections = state.get("sections")
    if isinstance(sections, dict):
        return sections
    return {}


def _bookmark_active_section(bjson: dict) -> str | None:
    state = bjson.get("explorationState")
    if isinstance(state, dict):
        act = state.get("activeSection")
        if isinstance(act, str):
            return act
    return None


def _visual_containers(section_body: dict) -> list[str]:
    """Return the visual names a bookmark section pins state for."""
    if not isinstance(section_body, dict):
        return []
    vc = section_body.get("visualContainers")
    if isinstance(vc, dict):
        return [str(k) for k in vc.keys()]
    if isinstance(vc, list):
        names = []
        for item in vc:
            if isinstance(item, dict):
                nm = item.get("name") or item.get("visualName")
                if nm is not None:
                    names.append(str(nm))
        return names
    return []


# ── The six referential-integrity checks ─────────────────────────────────────
def check_bookmarks(model: ReportModel) -> list[Finding]:
    """ref-1 (bookmark->page) + ref-2 (bookmark->visual) + ref-5 (activeSection)."""
    findings: list[Finding] = []
    valid_pages = set(model.page_ids)
    for bid, bjson in model.bookmarks:
        name = bjson.get("displayName") or bjson.get("name") or bid
        sections = _bookmark_sections(bjson)
        for page_name, section_body in sections.items():
            if page_name not in valid_pages:
                findings.append(
                    Finding(
                        check_id="ref-1",
                        severity="error",
                        location=f"bookmarks/{bid}",
                        message=(
                            f"Bookmark '{name}' references page '{page_name}', "
                            "which does not exist on disk."
                        ),
                        fix_hint=(
                            "Delete the stale bookmark or repoint it at an existing page "
                            "(pbir-utils `sanitize` removes bookmarks referencing deleted pages)."
                        ),
                    )
                )
                continue  # can't check visuals on a page that doesn't exist
            page_visuals = model.pages.get(page_name, {}).get("visual_names", set())
            for vname in _visual_containers(section_body):
                if vname not in page_visuals:
                    findings.append(
                        Finding(
                            check_id="ref-2",
                            severity="warning",
                            location=f"bookmarks/{bid}",
                            message=(
                                f"Bookmark '{name}' pins state for visual '{vname}' on page "
                                f"'{page_name}', but that visual no longer exists."
                            ),
                            fix_hint=(
                                "Remove the dangling visual entry from the bookmark, or "
                                "re-capture the bookmark after the layout change."
                            ),
                        )
                    )
        active = _bookmark_active_section(bjson)
        if active is not None and active not in valid_pages:
            findings.append(
                Finding(
                    check_id="ref-5",
                    severity="error",
                    location=f"bookmarks/{bid}",
                    message=(
                        f"Bookmark '{name}' has activeSection '{active}', "
                        "which is not an existing page."
                    ),
                    fix_hint="Set activeSection to a page that exists, or remove the bookmark.",
                )
            )
    return findings


def check_interactions(model: ReportModel) -> list[Finding]:
    """ref-3: page.json visualInteractions source/target must be on-page visuals."""
    findings: list[Finding] = []
    for page_id in model.page_ids:
        page = model.pages.get(page_id, {})
        page_json = page.get("page", {})
        page_visuals = page.get("visual_names", set())
        interactions = page_json.get("visualInteractions")
        if not isinstance(interactions, list):
            continue
        for inter in interactions:
            if not isinstance(inter, dict):
                continue
            for role in ("source", "target"):
                ref = inter.get(role)
                if ref is None:
                    continue
                if str(ref) not in page_visuals:
                    findings.append(
                        Finding(
                            check_id="ref-3",
                            severity="error",
                            location=f"pages/{page_id}",
                            message=(
                                f"visualInteractions {role} '{ref}' is not a visual on "
                                f"page '{page_id}'."
                            ),
                            fix_hint=(
                                "Remove the stale interaction entry, or correct the visual name "
                                "(it must match a visual's `name` on this page)."
                            ),
                        )
                    )
    return findings


def check_page_order(model: ReportModel) -> list[Finding]:
    """ref-4: pages.json pageOrder must be a permutation of on-disk page ids."""
    findings: list[Finding] = []
    if not isinstance(model.pages_index, dict):
        return findings  # no pages.json -> nothing to validate (older trees)
    order = model.pages_index.get("pageOrder")
    if not isinstance(order, list):
        return findings
    order_str = [str(p) for p in order]
    on_disk = set(model.page_ids)
    in_order = set(order_str)

    missing = on_disk - in_order  # on disk but not ordered
    invented = in_order - on_disk  # ordered but not on disk
    duplicates = sorted({p for p in order_str if order_str.count(p) > 1})

    if missing:
        findings.append(
            Finding(
                check_id="ref-4",
                severity="error",
                location="pages/pages.json",
                message=f"pageOrder omits on-disk page(s): {sorted(missing)}.",
                fix_hint="Add the missing page id(s) to pageOrder (pbir-utils `set-page-order`).",
            )
        )
    if invented:
        findings.append(
            Finding(
                check_id="ref-4",
                severity="error",
                location="pages/pages.json",
                message=f"pageOrder names page(s) that are not on disk: {sorted(invented)}.",
                fix_hint="Remove the stale page id(s) from pageOrder, or restore the page folder.",
            )
        )
    if duplicates:
        findings.append(
            Finding(
                check_id="ref-4",
                severity="error",
                location="pages/pages.json",
                message=f"pageOrder lists duplicate page id(s): {duplicates}.",
                fix_hint="Each page id must appear exactly once in pageOrder.",
            )
        )
    return findings


def check_active_page(model: ReportModel) -> list[Finding]:
    """ref-5: pages.json activePageName must name an existing page."""
    findings: list[Finding] = []
    if not isinstance(model.pages_index, dict):
        return findings
    active = model.pages_index.get("activePageName")
    if active is None:
        return findings
    if str(active) not in set(model.page_ids):
        findings.append(
            Finding(
                check_id="ref-5",
                severity="error",
                location="pages/pages.json",
                message=f"activePageName '{active}' is not an existing page.",
                fix_hint="Set activePageName to a page id that exists on disk.",
            )
        )
    return findings


def check_visual_name_uniqueness(model: ReportModel) -> list[Finding]:
    """ref-6: a visual `name` must be unique across the whole report."""
    findings: list[Finding] = []
    for vname, owners in sorted(model.visual_name_owner.items()):
        if len(owners) > 1:
            findings.append(
                Finding(
                    check_id="ref-6",
                    severity="error",
                    location="report",
                    message=(
                        f"Visual name '{vname}' is used by {len(owners)} visuals "
                        f"({', '.join(owners)}); PBIR requires report-wide uniqueness."
                    ),
                    fix_hint=(
                        "Rename one visual (and its folder) so every `name` is unique; "
                        "bookmarks and interactions key on the name."
                    ),
                )
            )
    return findings


# ── Orchestration ────────────────────────────────────────────────────────────
def validate_report(report_root: str) -> list[Finding]:
    findings: list[Finding] = []
    model = load_report(report_root, findings)
    if model is None:
        return findings
    findings += check_bookmarks(model)
    findings += check_interactions(model)
    findings += check_page_order(model)
    findings += check_active_page(model)
    findings += check_visual_name_uniqueness(model)
    return findings


# ── CLI ──────────────────────────────────────────────────────────────────────
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="check_refs.py",
        description="PBIR cross-file referential-integrity validator.",
    )
    p.add_argument(
        "report_root",
        nargs="?",
        help="Path to a `*.Report` folder or its `definition/` directory.",
    )
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.add_argument("--strict", action="store_true", help="Exit nonzero on >= warning.")
    p.add_argument("--list-checks", action="store_true", help="Print checks and exit.")
    p.add_argument("--version", action="store_true", help="Print version and exit.")
    return p


def _print_list_checks() -> None:
    print("PBIR referential-integrity checks:")
    for cid, name, sev in CHECK_DEFINITIONS:
        print(f"  {cid}  {name:<46} default-severity={sev}")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.list_checks:
        _print_list_checks()
        return 0
    if args.version:
        print(f"check_refs.py {VALIDATOR_VERSION} (envelope {SCHEMA_VERSION})")
        return 0
    if not args.report_root:
        print("error: report-root is required", file=sys.stderr)
        return 2

    try:
        resolved = _resolve_safe(args.report_root)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    findings = validate_report(resolved)

    summary = {"info": 0, "warning": 0, "error": 0}
    for f in findings:
        summary[f.severity] = summary.get(f.severity, 0) + 1

    has_error = summary["error"] > 0
    has_warning = summary["warning"] > 0
    exit_code = 0
    if has_error or (args.strict and has_warning):
        exit_code = 1

    if args.format == "json":
        envelope = {
            "schema_version": SCHEMA_VERSION,
            "validator_version": VALIDATOR_VERSION,
            "report_root": resolved,
            "exit_code": exit_code,
            "summary": summary,
            "findings": [asdict(f) for f in findings],
        }
        print(json.dumps(envelope, indent=2))
    else:
        if not findings:
            print(f"OK — {os.path.relpath(resolved)}: no dangling references.")
        else:
            for f in findings:
                print(f"[{f.severity}] {f.check_id} {f.location}: {f.message}")
                print(f"    fix: {f.fix_hint}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
