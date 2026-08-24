#!/usr/bin/env python3
"""pack and verify — build the archive, then prove it by re-opening the bytes.

⛔ TWO CODE PATHS, NO SHARED STATE. `verify()` takes a PATH and nothing else. It does not
import a manifest from `pack()`, does not receive the source directory, and re-derives
every fact from the archive's own bytes. A packer that builds an archive and then asserts
the layout is checking its own INTENT, which is the one thing that cannot fail — it would
pass on an archive the packer built wrongly, every time, because both halves would share
the wrong belief. The one thing they do share is DATA (the `non_shippable` globs in the
rule table), never code: sharing the constraint is correct, sharing the belief that it
was applied is not. `verify()` is therefore also callable — and is tested — against an
archive produced by `zip(1)`, in a fresh process, with no packer involved at all.

⛔ THE REPORT NEVER TRAVELS INSIDE THE ARCHIVE (ZP04). A lint-clean stamp shipped in the
bundle is a credibility transfer: org-wide sharing has no approval step (S10), so that
stamp suppresses the only human review left. The packer excludes it by construction, and
ZP04 asserts that it did.

Stdlib only. Python 3.9-safe.
"""

from __future__ import annotations

import fnmatch
import os
import re
import stat
import tempfile
import zipfile
from typing import Any

# ── ZP02's tier is DERIVED, not hand-set ─────────────────────────────────────

_SETTLED_RE = re.compile(r"^settled:\s*(\S+)\s*$", re.M)
_LAYOUT_RE = re.compile(r"^accepted_layout:\s*([AB])\s*$", re.M)


def derive_zp02_tier(evidence_path: str) -> tuple[str, str | None]:
    """Return (tier, accepted_layout) for ZP02, read from the evidence file.

    ⛔ FAIL-SAFE IS `warn`, AND THAT IS NOT A HEDGE. A missing or unparseable evidence
    file means the settlement is UNKNOWN, and you cannot assert a layout is wrong while
    you do not know which one is right — asserting under uncertainty here would block a
    correct archive on a coin flip. `warn` is the honest description of "unsettled", so
    the rule keeps reporting the shape without blocking on it.

    The rule text claims the tier is derived from the file rather than hand-set. This
    function is that claim's implementation; without it the claim is decoration.
    """
    try:
        with open(evidence_path, encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError):
        return "warn", None
    m = _SETTLED_RE.search(text)
    if not m or m.group(1).lower() != "yes":
        return "warn", None
    layout = _LAYOUT_RE.search(text)
    if not layout:
        # settled: yes with no accepted_layout is a half-filled record, not a settlement.
        return "warn", None
    return "fail", layout.group(1)


def evidence_path(skill_root: str) -> str:
    return os.path.join(skill_root, "reference", "platform-constraints.md")


# ── shared DATA (not shared code): what never ships ──────────────────────────

_FALLBACK_NON_SHIPPABLE = (
    "__MACOSX/*", "__MACOSX", ".DS_Store", "._*", ".git/*", ".git",
    ".gitignore", "*.pyc", "__pycache__/*", "__pycache__",
)
REPORT_NAMES = ("orgskill-report.json", "orgskill-report.txt", "lint-report.json")


def non_shippable(table: dict[str, Any]) -> tuple[str, ...]:
    """The exclusion globs, from the rule table when present."""
    pats = table.get("non_shippable")
    if isinstance(pats, list) and all(isinstance(p, str) for p in pats) and pats:
        return tuple(pats)
    return _FALLBACK_NON_SHIPPABLE


def _excluded(rel: str, pats: tuple[str, ...]) -> bool:
    parts = rel.replace("\\", "/").split("/")
    for pat in pats:
        if fnmatch.fnmatch(rel, pat):
            return True
        if any(fnmatch.fnmatch(p, pat.rstrip("/*")) for p in parts if pat.rstrip("/*")):
            if "/" not in pat or pat.endswith("/*"):
                return True
    return False


# ── pack ──────────────────────────────────────────────────────────────────────

class PackRefused(Exception):
    """Raised when a FAIL finding or a live refusal blocks the build."""


def pack(skill_dir: str, out_path: str, table: dict[str, Any],
         findings: list[dict[str, Any]], layout: str = "A") -> dict[str, Any]:
    """Write the archive. Refuses on any FAIL finding; names the rule id.

    `layout` is "A" (folder at root) or "B" (flat at root). It defaults to A and is
    driven by the evidence file's `accepted_layout:` once the probe settles — a data
    edit, not a code change.
    """
    fails = [f for f in findings if f.get("tier") == "fail"]
    if fails:
        ids = ", ".join(sorted({f["rule_id"] for f in fails}))
        raise PackRefused(
            "refusing to pack: %d FAIL finding(s) live — %s. A refusal has no override; "
            "fix the finding or, for R1-R4, use the quarantine path." % (len(fails), ids))

    name = os.path.basename(os.path.normpath(skill_dir))
    pats = non_shippable(table)
    written: list[str] = []

    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            dirs[:] = [d for d in dirs
                       if not _excluded(os.path.relpath(os.path.join(root, d), skill_dir), pats)]
            for fn in sorted(files):
                abs_p = os.path.join(root, fn)
                rel = os.path.relpath(abs_p, skill_dir).replace("\\", "/")
                if _excluded(rel, pats):
                    continue
                if os.path.basename(rel) in REPORT_NAMES:
                    continue          # ZP04, by construction
                if os.path.islink(abs_p):
                    continue          # never emit a symlink entry (ZP03)
                arc = rel if layout == "B" else "%s/%s" % (name, rel)
                zf.write(abs_p, arc)
                written.append(arc)
    return {"archive": out_path, "entries": written, "layout": layout, "root": name}


# ── verify — takes a PATH and nothing else ───────────────────────────────────

def _zp(table: dict[str, Any], rid: str, span: str, message: str,
        tier_override: str | None = None) -> dict[str, Any]:
    rule = {r["id"]: r for r in table["rules"]}.get(rid, {})
    return {
        "rule_id": rid,
        "tier": tier_override or rule.get("tier", "fail"),
        "class": rule.get("class", "ground-truth"),
        "span": span,
        "message": message,
        "remediation": rule.get("remediation", ""),
        "claim": rule.get("claim", ""),
        "fire_rate": rule.get("fire_rate"),
    }


def verify(archive_path: str, table: dict[str, Any],
           zp02_evidence: str | None = None,
           markers: list[str] | None = None) -> tuple[list[dict[str, Any]], list[str]]:
    """Re-open the archive and check it from its own bytes. Returns (findings, notes)."""
    findings: list[dict[str, Any]] = []
    notes: list[str] = []
    pats = non_shippable(table)

    try:
        zf = zipfile.ZipFile(archive_path)
    except (OSError, zipfile.BadZipFile) as exc:
        findings.append(_zp(table, "ZP01", archive_path,
                            "cannot open the archive: %s" % exc))
        return findings, notes

    with zf:
        infos = zf.infolist()
        names = [i.filename for i in infos]

        # ── ZP03: unsafe member paths and symlinks ───────────────────────────
        # Checked FIRST and returned on, because everything below extracts.
        unsafe = []
        for i in infos:
            n = i.filename
            if n.startswith("/") or n.startswith("\\") or "\\" in n:
                unsafe.append((n, "absolute or backslash-containing member name"))
            elif ".." in n.replace("\\", "/").split("/"):
                unsafe.append((n, "parent-directory traversal in the member name"))
            elif stat.S_ISLNK(i.external_attr >> 16):
                unsafe.append((n, "symlink entry"))
        for n, why in unsafe:
            findings.append(_zp(table, "ZP03", n, "%s: %s" % (why, n)))
        if unsafe:
            notes.append("extraction skipped: the archive carries unsafe member paths")
            return findings, notes

        # ── ZP05: exactly one distinct top-level path component ──────────────
        tops = sorted({n.replace("\\", "/").split("/", 1)[0] for n in names if n.strip()})
        if len(tops) != 1:
            findings.append(_zp(table, "ZP05", archive_path,
                                "%d distinct top-level entries (%s); expected exactly one"
                                % (len(tops), ", ".join(tops[:6]))))

        # ── ZP07: Finder / VCS artifacts ─────────────────────────────────────
        junk = sorted({n for n in names if _excluded(n, pats)})
        for n in junk:
            findings.append(_zp(table, "ZP07", n,
                                "non-shippable entry in the archive: %s" % n))

        # ── ZP04: the studio's own report must not travel ────────────────────
        for n in names:
            if os.path.basename(n) in REPORT_NAMES:
                findings.append(_zp(table, "ZP04", n,
                                    "the validation report is inside the archive: %s" % n))

        # ── locate SKILL.md ──────────────────────────────────────────────────
        skill_entries = [n for n in names if os.path.basename(n) == "SKILL.md"]
        if len(skill_entries) != 1:
            findings.append(_zp(table, "ZP01", archive_path,
                                "the archive contains %d SKILL.md entries; expected exactly 1"
                                % len(skill_entries)))
            return findings, notes
        skill_entry = skill_entries[0]
        depth = skill_entry.replace("\\", "/").count("/")
        observed = "B" if depth == 0 else "A"

        # ── ZP02: root shape, at the tier the EVIDENCE FILE derives ──────────
        tier, accepted = derive_zp02_tier(zp02_evidence or "")
        if accepted is None:
            notes.append("ZP02 is at %s: the zip-root question is unsettled "
                         "(reference/platform-constraints.md records no result). "
                         "Layout observed: %s." % (tier.upper(), observed))
        elif observed != accepted:
            findings.append(_zp(table, "ZP02", skill_entry,
                                "archive root layout is %s but the settled convention is %s"
                                % (observed, accepted), tier_override=tier))

        # ── ZP06: SKILL.md present and non-empty ─────────────────────────────
        try:
            body_bytes = zf.read(skill_entry)
        except (OSError, KeyError, zipfile.BadZipFile) as exc:
            findings.append(_zp(table, "ZP06", skill_entry, "cannot read SKILL.md: %s" % exc))
            return findings, notes
        if not body_bytes.strip():
            findings.append(_zp(table, "ZP06", skill_entry, "SKILL.md is empty in the archive"))
            return findings, notes
        try:
            text = body_bytes.decode("utf-8")
        except UnicodeDecodeError:
            findings.append(_zp(table, "ZP06", skill_entry, "SKILL.md is not valid UTF-8"))
            return findings, notes

        # ── ZP08: every relative link resolves to an entry IN THE ARCHIVE ────
        # Not on disk. The source tree can be complete while the archive is not, which
        # is the exact defect this catches (gap-delta D4).
        prefix = skill_entry[: -len("SKILL.md")]
        present = set(names)
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            if link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = link.split("#", 1)[0]
            if not target:
                continue
            resolved = os.path.normpath(prefix + target).replace("\\", "/")
            if resolved not in present:
                findings.append(_zp(table, "ZP08", skill_entry,
                                    "bundled reference %r is not present in the archive "
                                    "(resolved to %r)" % (link, resolved)))

        # ── ZP09: extract and re-run the linter on the extracted tree ────────
        # "Verification by attempt": the source tree is not consulted.
        try:
            import lint_rules
        except ImportError:
            notes.append("ZP09 skipped: lint_rules is not importable — THIS IS NOT A PASS")
            return findings, notes
        with tempfile.TemporaryDirectory() as td:
            try:
                zf.extractall(td)
            except (OSError, zipfile.BadZipFile) as exc:
                findings.append(_zp(table, "ZP09", archive_path,
                                    "the archive does not extract: %s" % exc))
                return findings, notes
            extracted_dir = os.path.dirname(os.path.join(td, skill_entry)) or td
            sub, amb = lint_rules.lint_skill(extracted_dir, table, markers or [])
            for f in sub:
                if f["tier"] != "fail":
                    continue
                findings.append(_zp(table, "ZP09", "%s -> %s" % (archive_path, f["span"]),
                                    "the EXTRACTED tree fails %s: %s"
                                    % (f["rule_id"], f["message"])))
            for a in amb:
                findings.append(_zp(table, "ZP09", archive_path,
                                    "the extracted tree is ambiguous: %s" % a))
    return findings, notes


# ── the zip-root probe fixtures ──────────────────────────────────────────────

_PROBE_SKILL = """---
name: zip-root-probe
description: Probes which archive root layout the platform accepts. Use when the \
zip-root question in reference/platform-constraints.md is still unsettled.
---

# zip-root-probe

A minimal, harmless skill whose only purpose is to be uploaded twice — once from
`rootA-folder.zip` and once from `rootB-flat.zip` — so the root-layout question is
settled by the platform rather than by re-reading a sentence.

Delete it after the probe. Record BOTH outcomes, including the rejection.
"""


def write_probe_fixtures(out_dir: str) -> list[str]:
    """Write rootA-folder.zip and rootB-flat.zip. Identical content, different roots.

    ⛔ The two archives must differ ONLY in the root layout. If they differed in any
    other byte, a rejection would not isolate the variable and the probe would settle
    nothing — which is the whole reason the probe exists.
    """
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for label, prefix in (("rootA-folder", "zip-root-probe/"), ("rootB-flat", "")):
        path = os.path.join(out_dir, label + ".zip")
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(prefix + "SKILL.md", _PROBE_SKILL)
        written.append(path)
    return written
