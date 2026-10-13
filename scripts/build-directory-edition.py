#!/usr/bin/env python3
"""build-directory-edition.py - build the Anthropic-Directory edition of a plugin from the source plugin.

WHY
    ravenclaude-core cannot be submitted to the Directory as it is: 1,871 files (limit is 512 before a
    reviewer hold), an 11 MB dashboard (hard block at 5 MiB), 57 registered hooks several of which are
    always on, `bin/` that edits shell rc files, and an `experimental` key that must not declare
    components. This builds a SMALLER, REVIEWABLE edition from the same source - one source of truth,
    not a fork - by copying files UNMODIFIED and applying a short, fixed transform list.

    The set of files that ships is a human-reviewed manifest (docs/directory-edition/<name>/manifest.json):
    every agent, skill, command and hook is allow-listed with a REASON. Everything those reference is
    pulled in by closure; anything they reference that the manifest denies is a build failure, not a
    silent dangling reference.

TRANSFORMS (the whole list)
    plugin.json          rebuilt from the source one: `experimental` dropped, homepage/repository set,
                         description replaced, version kept equal to the source (the single source of truth)
    hooks/hooks.json     filtered to the allow-listed hooks
    commands overrides   a command the manifest overrides is replaced by the override file
    README / PRIVACY / LICENSE / .claude-plugin/marketplace.json   generated from templates

USAGE
    build-directory-edition.py --out DIR            build the edition into DIR (must not exist or be empty)
    build-directory-edition.py --check              build twice -> identical; file list matches the committed list
    build-directory-edition.py --report             print limits, closure and network report for a fresh build
    build-directory-edition.py --write-file-list    refresh the committed file list
    build-directory-edition.py --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO / "docs" / "directory-edition" / "ravenclaude-core" / "manifest.json"

TEXT_EXT = {
    ".md",
    ".sh",
    ".py",
    ".json",
    ".js",
    ".mjs",
    ".yaml",
    ".yml",
    ".txt",
    ".html",
    ".css",
    ".toml",
}
EXEC_EXT = {".sh", ".py", ".js", ".mjs"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico"}
REF_DIRS = (
    "hooks",
    "scripts",
    "knowledge",
    "templates",
    "rules",
    "skills",
    "agents",
    "commands",
    "schemas",
    "scenarios",
    "best-practices",
    # directories the edition denies: a reference INTO one of these must be seen, not missed
    "bin",
    "monitors",
    "dashboard-assets",
    "copilot",
    "codex",
    "vscode-extension",
)
_REF_DIR = re.compile(
    r"(?<![\w.-])((?:\.\./)*(?:" + "|".join(REF_DIRS) + r")/[\w.@+-]+(?:/[\w.@+-]+)*)"
)
_REF_SIB = re.compile(r"/([\w-]+\.(?:sh|py|js|mjs|json))\b")
_NEVER_COPY = ("__pycache__", ".DS_Store", "node_modules", ".pytest_cache")

GATE_PATH = "hooks/posture-gate.sh"
GATE_PREFIX = 'bash "${CLAUDE_PLUGIN_ROOT}/hooks/posture-gate.sh" '

# The edition's single on/off switch. Every shipped hook except the one-line setup prompt is invoked
# THROUGH this file, so "does nothing without a posture file" is true by construction: the wrapped hook
# never starts. Kept to a handful of lines on purpose - a reviewer should be able to read all of it.
POSTURE_GATE_SH = """#!/usr/bin/env bash
# posture-gate.sh - the on/off switch for this plugin's hooks.
#
# hooks.json invokes every hook as:  bash posture-gate.sh <the hook command...>
# The wrapped hook runs ONLY if .ravenclaude/comfort-posture.yaml exists in the project. Without that
# file this exits 0 immediately: no output, no files written, no network, and the wrapped hook never
# starts. Creating the file is how you opt in; deleting it turns everything off again.
#
# It reads nothing from the file (the wrapped hook does, if it runs) and fails toward doing nothing.
[ "$#" -gt 0 ] || exit 0
[ -f "${CLAUDE_PROJECT_DIR:-$PWD}/.ravenclaude/comfort-posture.yaml" ] || exit 0
exec "$@"
"""


class BuildError(Exception):
    """A build precondition failed. Always carries an actionable message."""


# ── glob helpers ─────────────────────────────────────────────────────────────


def _glob_re(pattern: str) -> re.Pattern[str]:
    out, i = "", 0
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out += r"(?:.*/)?"
            i += 3
        elif pattern.startswith("**", i):
            out += r".*"
            i += 2
        elif c == "*":
            out += r"[^/]*"
            i += 1
        elif c == "?":
            out += r"[^/]"
            i += 1
        else:
            out += re.escape(c)
            i += 1
    return re.compile("^" + out + "$")


def glob_match(path: str, pattern: str) -> bool:
    return _glob_re(pattern).match(path) is not None


# ── manifest ────────────────────────────────────────────────────────────────


def load_manifest(path: Path) -> dict:
    m = json.loads(path.read_text())
    m["_dir"] = str(path.resolve().parent)  # templates/ and overrides/ are relative to the manifest
    problems = validate_manifest(m)
    if problems:
        raise BuildError("manifest invalid:\n  - " + "\n  - ".join(problems))
    return m


def validate_manifest(m: dict) -> list[str]:
    p: list[str] = []
    for k in (
        "schema_version",
        "plugin",
        "source_plugin_dir",
        "target",
        "plugin_json",
        "limits",
        "components",
        "deny_globs",
    ):
        if k not in m:
            p.append(f"missing key: {k}")
    comps = m.get("components", {})
    for kind in ("agents", "skills", "commands", "hooks"):
        if kind not in comps:
            p.append(f"components.{kind} missing")
            continue
        seen = set()
        for i, e in enumerate(comps[kind]):
            key = e.get("id") if kind == "hooks" else e.get("name")
            if not key:
                p.append(f"components.{kind}[{i}] has no {'id' if kind == 'hooks' else 'name'}")
                continue
            if key in seen:
                p.append(f"components.{kind}: duplicate {key}")
            seen.add(key)
            if not str(e.get("reason", "")).strip():
                p.append(
                    f"components.{kind}.{key}: a REASON is required (the manifest is the review record)"
                )
            if kind == "hooks" and not str(e.get("summary", "")).strip():
                p.append(f"components.hooks.{key}: a README summary is required")
            if (
                kind == "hooks"
                and e.get("ungated")
                and not str(e.get("ungated_reason", "")).strip()
            ):
                p.append(f"components.hooks.{key}: ungated needs an ungated_reason")
    for i, e in enumerate(m.get("extra_roots", [])):
        if not e.get("glob") or not str(e.get("reason", "")).strip():
            p.append(f"extra_roots[{i}] needs glob and reason")
    for i, d in enumerate(m.get("deny_globs", [])):
        if not d.get("glob") or not str(d.get("reason", "")).strip():
            p.append(f"deny_globs[{i}] needs glob and reason")
    return p


# ── source scanning ─────────────────────────────────────────────────────────


def list_source(src: Path) -> list[str]:
    out = []
    for dirpath, dirs, files in os.walk(src):
        dirs[:] = sorted(d for d in dirs if d not in _NEVER_COPY)
        for f in sorted(files):
            if f in _NEVER_COPY or f.endswith(".pyc"):
                continue
            out.append(os.path.relpath(os.path.join(dirpath, f), src).replace(os.sep, "/"))
    return out


def denied_by(path: str, deny: list[dict], roots: frozenset[str] = frozenset()) -> dict | None:
    """First deny entry that matches. A manifest ROOT is an explicit decision and is never denied by a glob;
    an entry may carry `except` globs for the files a broad deny deliberately lets through."""
    if path in roots:
        return None
    for d in deny:
        if glob_match(path, d["glob"]) and not any(
            glob_match(path, e) for e in d.get("except", [])
        ):
            return d
    return None


def _scannable(text: str, rel: str) -> str:
    """Executable files: drop whole-line comments, which are the dominant source of false references."""
    suffix = Path(rel).suffix
    if suffix in (".sh", ".py"):
        return "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
    if suffix in (".js", ".mjs"):
        return "\n".join(
            l for l in text.splitlines() if not l.lstrip().startswith(("//", "*", "/*"))
        )
    return text


def references(rel: str, text: str, plugin_name: str, exists) -> tuple[set[str], set[str]]:
    """Return (resolved plugin-relative file refs, unresolved-but-denial-checkable refs)."""
    body = _scannable(text, rel)
    here = str(Path(rel).parent).replace("\\", "/")
    here = "" if here == "." else here
    found: set[str] = set()
    cands: list[str] = []
    for m in _REF_DIR.finditer(body):
        cands.append(m.group(1).rstrip(".,;:)"))
    is_exec = Path(rel).suffix in EXEC_EXT or rel.endswith("hooks.json")
    if is_exec:
        for m in _REF_SIB.finditer(body):
            name = m.group(1)
            for base in (here, "hooks", "scripts", "knowledge", "templates"):
                cands.append(f"{base}/{name}" if base else name)
    for c in cands:
        options = []
        if c.startswith("../"):
            options.append(os.path.normpath(os.path.join(here, c)).replace(os.sep, "/"))
        else:
            options.append(c)
            if here:
                options.append(os.path.normpath(os.path.join(here, c)).replace(os.sep, "/"))
            prefix = f"plugins/{plugin_name}/"
            if c.startswith(prefix):
                options.append(c[len(prefix) :])
        for o in options:
            if not o.startswith("..") and exists(o):
                found.add(o)
                break
    return found, set()


def hook_script_paths(command: str) -> list[str]:
    return list(re.findall(r"\$\{?CLAUDE_PLUGIN_ROOT\}?/([\w./-]+)", command))


def registrations(hooks_json: dict) -> list[tuple[str, str | None, dict]]:
    rows = []
    for event, groups in hooks_json.get("hooks", hooks_json).items():
        for g in groups:
            for h in g.get("hooks", []):
                rows.append((event, g.get("matcher"), h))
    return rows


def hook_id(command: str) -> str:
    """Script basename plus its trailing args (same rule as directory-edition-hook-audit.py), ignoring the
    posture-gate prefix and the injected file-path argument."""
    paths = [
        m
        for m in re.findall(r"\$\{?CLAUDE_PLUGIN_ROOT\}?/([\w./-]+)", command)
        if m != "hooks/posture-gate.sh"
    ]
    if not paths:
        return command.strip()
    script = paths[0]
    tail = command.split(script, 1)[1]
    args = [a for a in re.findall(r"[^\s\"']+", tail) if "CLAUDE_TOOL_FILE_PATH" not in a]
    return Path(script).name + ((" " + " ".join(args)) if args else "")


# ── the build ───────────────────────────────────────────────────────────────


class Plan:
    """Everything decided before a byte is written, so --report and the gate share one truth."""

    def __init__(self) -> None:
        self.files: dict[str, str] = {}  # dist path -> "copy:<src rel>" | "gen:<name>"
        self.closure_breaks: list[tuple[str, str, str]] = []  # (from, to, why)  executable surface
        self.prose_denied: list[tuple[str, str, str]] = []  # informational
        self.generated: dict[str, str] = {}  # dist path -> text
        self.hook_rows: list[dict] = []
        self.via: dict[str, str] = {}  # file -> first referrer (why it is in the closure)


def plan_build(manifest: dict, repo: Path = REPO, overrides_root: Path | None = None) -> Plan:
    src = repo / manifest["source_plugin_dir"]
    name = manifest["plugin"]
    deny = manifest["deny_globs"]
    comps = manifest["components"]
    allow_break = manifest.get("closure_allow", [])
    prose_depth = int(manifest.get("closure", {}).get("prose_depth", 1))
    overrides = {k: (Path(manifest["_dir"]) / v) for k, v in manifest.get("overrides", {}).items()}
    all_src = set(list_source(src))
    plan = Plan()

    def exists(p: str) -> bool:
        return p in all_src or p in overrides

    def read(p: str) -> str:
        if p in overrides:
            return overrides[p].read_text()
        return (src / p).read_text(errors="replace")

    roots: list[str] = []
    for a in comps["agents"]:
        roots.append(f"agents/{a['name']}.md")
    for c in comps["commands"]:
        roots.append(f"commands/{c['name']}.md")
    for s in comps["skills"]:
        prefix = f"skills/{s['name']}/"
        got = [p for p in all_src if p.startswith(prefix)]
        if not got:
            raise BuildError(f"skill {s['name']}: no files under {prefix}")
        roots += sorted(got)
    for er in manifest.get("extra_roots", []):
        got = sorted(p for p in all_src if glob_match(p, er["glob"]))
        if not got:
            raise BuildError(f"extra_roots {er['glob']} matches no source file")
        roots += got
    hooks_json = json.loads((src / "hooks" / "hooks.json").read_text())
    want = {h["id"] for h in comps["hooks"]}
    seen_ids = set()
    kept = []
    for event, matcher, h in registrations(hooks_json):
        hid = hook_id(h["command"])
        if hid in want:
            seen_ids.add(hid)
            kept.append((event, matcher, h))
            roots += hook_script_paths(h["command"])
            plan.hook_rows.append({"id": hid, "event": event, "matcher": matcher or "*"})
    missing = want - seen_ids
    if missing:
        raise BuildError(
            "manifest hooks not registered in the source hooks.json: " + ", ".join(sorted(missing))
        )

    root_set = frozenset(roots)
    # BFS closure. budget: exec surfaces propagate fully; prose surfaces stop after prose_depth hops.
    included: dict[str, int] = {}
    queue: list[tuple[str, int, str]] = [(r, prose_depth, "<root>") for r in roots]
    while queue:
        rel, budget, frm = queue.pop(0)
        if rel in included and included[rel] >= budget:
            continue
        d = denied_by(rel, deny, root_set)
        if d is None and rel not in root_set:
            # A skill, agent or command ships ONLY through the manifest, never because some prose mentions it.
            parts = rel.split("/")
            if parts[0] in ("skills", "agents", "commands") and len(parts) > 1:
                d = {
                    "glob": f"{parts[0]}/** (not allow-listed)",
                    "reason": f"{parts[0]} ship only through the manifest allow-list",
                }
        if d:
            is_exec_src = frm != "<root>" and (
                Path(frm).suffix in EXEC_EXT or frm.endswith("hooks.json")
            )
            if frm == "<root>":
                raise BuildError(
                    f"{rel} is a manifest root but is denied by {d['glob']} ({d['reason']})"
                )
            allowed = any(
                glob_match(frm, a["from"]) and glob_match(rel, a["to"]) for a in allow_break
            )
            if is_exec_src and not allowed:
                plan.closure_breaks.append((frm, rel, d["reason"]))
            elif not is_exec_src:
                plan.prose_denied.append((frm, rel, d["reason"]))
            continue
        if not exists(rel):
            raise BuildError(f"{rel} (from {frm}) does not exist in the source plugin")
        included[rel] = max(included.get(rel, -1), budget)
        plan.via.setdefault(rel, frm)
        if Path(rel).suffix not in TEXT_EXT:
            continue
        is_exec = Path(rel).suffix in EXEC_EXT
        if not is_exec and budget <= 0 and frm != "<root>":
            continue
        refs, _ = references(rel, read(rel), name, exists)
        nb = prose_depth if is_exec else budget - 1
        for r in sorted(refs):
            if r != rel:
                queue.append((r, nb if is_exec else max(nb, 0) if budget > 0 else -1, rel))
    for rel in sorted(included):
        plan.files[rel] = "override:" + rel if rel in overrides else "copy:" + rel

    # generated files
    sp = json.loads((src / ".claude-plugin" / "plugin.json").read_text())
    pj = {
        "name": sp["name"],
        "displayName": manifest["plugin_json"].get(
            "displayName", sp.get("displayName", sp["name"])
        ),
        "description": manifest["plugin_json"]["description"],
        "version": sp["version"],
        "author": sp.get("author", {}),
        "homepage": manifest["target"]["homepage"],
        "repository": manifest["target"]["repository"],
        "license": sp.get("license", "MIT"),
        "keywords": manifest["plugin_json"].get("keywords", sp.get("keywords", [])),
    }
    plan.generated[".claude-plugin/plugin.json"] = (
        json.dumps(pj, indent=2, ensure_ascii=False) + "\n"
    )
    mk = {
        "name": manifest["target"]["marketplace_name"],
        "description": pj["description"],  # `claude plugin validate --strict` warns without one
        "owner": sp.get("author", {}),
        "plugins": [
            {
                "name": sp["name"],
                "source": "./",
                "description": pj["description"],
                "version": sp["version"],
            }
        ],
    }
    plan.generated[".claude-plugin/marketplace.json"] = (
        json.dumps(mk, indent=2, ensure_ascii=False) + "\n"
    )
    filtered: dict = {k: v for k, v in hooks_json.items() if k != "hooks"}
    filtered["hooks"] = {}
    ungated = {h["id"]: bool(h.get("ungated")) for h in comps["hooks"]}
    for event, groups in hooks_json["hooks"].items():
        ngroups = []
        for g in groups:
            hs = []
            for h in g.get("hooks", []):
                hid = hook_id(h["command"])
                if hid not in want:
                    continue
                h2 = dict(h)
                if not ungated[hid]:
                    h2["command"] = GATE_PREFIX + h["command"]
                hs.append(h2)
            if hs:
                ng = dict(g)
                ng["hooks"] = hs
                ngroups.append(ng)
        if ngroups:
            filtered["hooks"][event] = ngroups
    plan.generated["hooks/hooks.json"] = json.dumps(filtered, indent=2, ensure_ascii=False) + "\n"
    plan.generated[GATE_PATH] = POSTURE_GATE_SH
    plan.files.pop("hooks/hooks.json", None)
    for gp in plan.generated:
        plan.files[gp] = "gen:" + gp
    return plan


def render_templates(manifest: dict, plan: Plan, repo: Path = REPO) -> dict[str, str]:
    """README / PRIVACY / LICENSE from templates; tables are generated so parity is by construction."""
    tdir = Path(manifest["_dir"]) / "templates"
    version = json.loads(plan.generated[".claude-plugin/plugin.json"])["version"]
    comps = manifest["components"]
    hook_rows = []
    by_id: dict[str, list[dict]] = {}
    for r in plan.hook_rows:
        by_id.setdefault(r["id"], []).append(r)
    for h in comps["hooks"]:
        evs = "<br>".join(
            f"`{r['event']}`" + (f" `{r['matcher']}`" if r["matcher"] != "*" else "")
            for r in by_id.get(h["id"], [])
        )
        hook_rows.append(f"| `{h['id']}` | {evs} | {h['summary']} |")
    hook_table = (
        "| Hook | Fires on | What it does (only once a posture file exists, unless stated) |\n|---|---|---|\n"
        + "\n".join(hook_rows)
    )
    lists = {
        "AGENT_LIST": "\n".join(f"- `{a['name']}` - {a['reason']}" for a in comps["agents"]),
        "SKILL_LIST": "\n".join(f"- `{s['name']}` - {s['reason']}" for s in comps["skills"]),
        "COMMAND_LIST": "\n".join(f"- `/{c['name']}` - {c['reason']}" for c in comps["commands"]),
        "HOOK_TABLE": hook_table,
        "VERSION": version,
        "EXEC_LIST": ", ".join(f"`{x}`" for x in sorted(manifest.get("hook_audit", {}).get("allowed_execs", []))),
        "N_AGENTS": str(len(comps["agents"])),
        "N_SKILLS": str(len(comps["skills"])),
        "N_COMMANDS": str(len(comps["commands"])),
        "N_HOOKS": str(len(comps["hooks"])),
        "N_GATED_HOOKS": str(sum(1 for h in comps["hooks"] if not h.get("ungated"))),
        "N_FILES": str(len(set(plan.files) | {"README.md", "PRIVACY.md", "LICENSE"})),
        "REPO": manifest["target"]["repository"],
        "HOMEPAGE": manifest["target"]["homepage"],
        "PORTAL": manifest["target"]["portal_url"],
        "SUPPORT": manifest["target"]["support"],
    }
    out = {}
    for fname in ("README.md", "PRIVACY.md", "LICENSE"):
        t = (repo / "LICENSE").read_text() if fname == "LICENSE" else (tdir / fname).read_text()
        for k, v in lists.items():
            t = t.replace("{{" + k + "}}", v)
        left = re.findall(r"\{\{[A-Z_]+\}\}", t)
        if left:
            raise BuildError(f"{fname}: unresolved placeholders {sorted(set(left))}")
        out[fname] = t
    return out


def fill_placeholders(text: str, manifest: dict) -> str:
    """The few manifest values an override file may use."""
    tgt = manifest["target"]
    for k, v in (("PORTAL", tgt["portal_url"]), ("REPO", tgt["repository"]), ("SUPPORT", tgt["support"])):
        text = text.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z_]+\}\}", text)
    if left:
        raise BuildError(f"override has unresolved placeholders {sorted(set(left))}")
    return text


def write_dist(manifest: dict, plan: Plan, out: Path, repo: Path = REPO) -> None:
    src = repo / manifest["source_plugin_dir"]
    overrides = {k: (Path(manifest["_dir"]) / v) for k, v in manifest.get("overrides", {}).items()}
    if out.exists() and any(out.iterdir()):
        raise BuildError(f"{out} exists and is not empty")
    out.mkdir(parents=True, exist_ok=True)
    gen = dict(plan.generated)
    gen.update(render_templates(manifest, plan, repo))
    for dist_path, how in sorted(plan.files.items()):
        dest = out / dist_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if how.startswith("gen:"):
            dest.write_text(gen[dist_path])
            if dist_path.startswith("hooks/") and dist_path.endswith(".sh"):
                os.chmod(dest, 0o755)
        elif how.startswith("override:"):
            dest.write_text(fill_placeholders(overrides[dist_path].read_text(), manifest))
            os.chmod(dest, 0o644)
        else:
            shutil.copyfile(src / dist_path, dest)
            shutil.copymode(src / dist_path, dest)
    for name, text in gen.items():
        if name in plan.files:
            continue
        dest = out / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)


def all_dist_paths(plan: Plan, manifest: dict, repo: Path = REPO) -> list[str]:
    extra = set(render_templates(manifest, plan, repo))
    return sorted(set(plan.files) | extra)


# ── analyses of a built tree ────────────────────────────────────────────────


def tree_files(root: Path) -> list[str]:
    out = []
    for dirpath, dirs, files in os.walk(root):
        dirs.sort()
        for f in sorted(files):
            out.append(os.path.relpath(os.path.join(dirpath, f), root).replace(os.sep, "/"))
    return out


def limits_report(root: Path, limits: dict) -> dict:
    files = tree_files(root)
    big_nonimage, huge, symlinks, binaries, total = [], [], [], [], 0
    for rel in files:
        p = root / rel
        if p.is_symlink():
            symlinks.append(rel)
            continue
        size = p.stat().st_size
        total += size
        if size > limits["max_file_bytes"]:
            huge.append((rel, size))
        if Path(rel).suffix.lower() not in IMAGE_EXT and size > limits["max_file_bytes_nonimage"]:
            big_nonimage.append((rel, size))
        if Path(rel).suffix.lower() not in IMAGE_EXT:
            try:
                head = p.read_bytes()[:4096]
            except OSError:
                head = b""
            if b"\x00" in head:
                binaries.append(rel)
    violations = []
    if len(files) > limits["max_files"]:
        violations.append(
            f"{len(files)} files > max_files {limits['max_files']} (reviewer hold on every version)"
        )
    for rel, s in huge:
        violations.append(f"{rel}: {s} bytes > {limits['max_file_bytes']} (blocks)")
    for rel, s in big_nonimage:
        violations.append(
            f"{rel}: {s} bytes > {limits['max_file_bytes_nonimage']} non-image (reviewer hold)"
        )
    for rel in symlinks:
        violations.append(f"{rel}: symlink")
    for rel in binaries:
        violations.append(f"{rel}: binary/NUL content that is not an image")
    if total > limits.get("max_total_bytes", 1 << 60):
        violations.append(f"total {total} bytes > max_total_bytes")
    largest = sorted(
        (((root / r).stat().st_size, r) for r in files if not (root / r).is_symlink()), reverse=True
    )[:5]
    return {"files": len(files), "total_bytes": total, "largest": largest, "violations": violations}


_NET_PRIM = re.compile(
    r"\b(curl|wget|urllib|http\.client|requests\.|aiohttp|socket\.|fetch\(|nc |ncat|ssh |scp )"
)
_URL = re.compile(r"https?://([\w.-]+)")


def network_scan(root: Path) -> dict[str, dict]:
    """Executable files that contain a network primitive or a URL host (comments excluded)."""
    hits: dict[str, dict] = {}
    for rel in tree_files(root):
        if Path(rel).suffix not in EXEC_EXT:
            continue
        text = _scannable((root / rel).read_text(errors="replace"), rel)
        prims = sorted({m.group(1).strip() for m in _NET_PRIM.finditer(text)})
        hosts = sorted({m.group(1) for m in _URL.finditer(text)})
        if prims or hosts:
            hits[rel] = {"primitives": prims, "hosts": hosts}
    return hits


def network_findings(root: Path, manifest: dict) -> list[str]:
    classified = manifest.get("network_classification", {})
    problems = []
    for rel, h in network_scan(root).items():
        c = classified.get(rel)
        if (
            not c
            or not str(c.get("reason", "")).strip()
            or c.get("kind")
            not in (
                "none-runtime",
                "user-configured",
                "local-loopback",
                "user-session",
                "text-only",
            )
        ):
            problems.append(
                f"{rel}: network primitive/URL ({', '.join(h['primitives'] + h['hosts'])[:90]}) "
                "has no network_classification entry with a kind and a reason"
            )
    for rel in classified:
        if rel not in set(tree_files(root)):
            problems.append(
                f"network_classification names {rel}, which does not ship (stale entry)"
            )
    return problems


def readme_parity(root: Path, manifest: dict) -> list[str]:
    """README must list exactly the shipped hooks (by id), and nothing else that looks like a hook."""
    readme = (root / "README.md").read_text()
    shipped = {h["id"] for h in manifest["components"]["hooks"]}
    hooks_dir = {
        p
        for p in tree_files(root)
        if p.startswith("hooks/") and p.endswith(".sh") and "/_" not in "/" + p[6:]
    }
    problems = []
    for hid in sorted(shipped):
        if f"`{hid}`" not in readme:
            problems.append(f"README does not list shipped hook `{hid}`")
    for rel in sorted(hooks_dir):
        base = Path(rel).name
        if rel == GATE_PATH:
            continue
        if not any(h.split()[0] == base for h in shipped):
            problems.append(
                f"{rel} ships but is not a manifest hook (unregistered script in hooks/)"
            )
    return problems


def structure_findings(root: Path, manifest: dict) -> list[str]:
    problems = []
    pj = json.loads((root / ".claude-plugin" / "plugin.json").read_text())
    if "experimental" in pj:
        problems.append("plugin.json declares `experimental` (must not declare components)")
    if pj.get("name") != manifest["plugin"]:
        problems.append(f"plugin.json name {pj.get('name')} != {manifest['plugin']}")
    for forbidden in (
        "bin",
        "monitors",
        "CLAUDE.md",
        "dashboard.html",
        "copilot",
        "codex",
        "vscode-extension",
    ):
        if (root / forbidden).exists():
            problems.append(f"{forbidden} must not ship in the directory edition")
    hj = json.loads((root / "hooks" / "hooks.json").read_text())
    for _event, _matcher, h in registrations(hj):
        for sp in hook_script_paths(h["command"]):
            if not (root / sp).is_file():
                problems.append(f"hooks.json registers {sp}, which does not ship")
    ungated = {h["id"] for h in manifest["components"]["hooks"] if h.get("ungated")}
    if not (root / GATE_PATH).is_file():
        problems.append(f"{GATE_PATH} is missing")
    elif (root / GATE_PATH).read_text() != POSTURE_GATE_SH:
        problems.append(f"{GATE_PATH} differs from the reviewed shim")
    for event, _matcher, h in registrations(hj):
        gated = h["command"].startswith(GATE_PREFIX)
        hid = hook_id(h["command"])
        if hid in ungated and gated:
            problems.append(f"{hid} is declared ungated but is wrapped in the gate")
        if hid not in ungated and not gated:
            problems.append(
                f"{event}: {hid} is not wrapped in {GATE_PATH} (it would run with no posture file)"
            )
    for rel in tree_files(root):
        if rel.startswith("hooks/") and rel.endswith(".sh") and not os.access(root / rel, os.X_OK):
            problems.append(f"{rel} is not executable")
    return problems


def claude_validate(root: Path) -> tuple[str, str]:
    exe = shutil.which("claude")
    if not exe:
        return "unavailable", "claude CLI not on PATH"
    try:
        cp = subprocess.run(
            [exe, "plugin", "validate", "--strict", str(root)],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except Exception as e:  # noqa: BLE001
        return "unavailable", f"could not run: {e}"
    out = (cp.stdout + cp.stderr).strip()
    return ("pass" if cp.returncode == 0 else "fail"), out[-1500:]


def file_list_text(paths: list[str]) -> str:
    return "\n".join(paths) + "\n"


def file_list_path(manifest: dict, repo: Path = REPO) -> Path:
    return Path(manifest["_dir"]) / "file-list.txt"


def digest_tree(root: Path) -> str:
    h = hashlib.sha256()
    for rel in tree_files(root):
        h.update(rel.encode())
        h.update(b"\0")
        h.update((root / rel).read_bytes())
        h.update(b"\0")
        h.update(str(oct((root / rel).stat().st_mode & 0o111)).encode())
    return h.hexdigest()


def full_build(manifest: dict, out: Path, repo: Path = REPO) -> Plan:
    plan = plan_build(manifest, repo)
    if plan.closure_breaks:
        lines = [f"  {a} -> {b}  ({why})" for a, b, why in plan.closure_breaks]
        raise BuildError(
            "closure broken: an executable file references a denied file. Add the file to the "
            "manifest, change the source, or allow-list the pair in closure_allow with a reason:\n"
            + "\n".join(lines)
        )
    write_dist(manifest, plan, out, repo)
    return plan


# ── commands ────────────────────────────────────────────────────────────────


SECRET_RULES = {
    "aws-access-key": r"\b(AKIA|ASIA)[0-9A-Z]{16}\b",
    "github-token": r"\bgh[pousr]_[A-Za-z0-9]{36,}\b",
    "github-fine-grained": r"\bgithub_pat_[A-Za-z0-9_]{50,}\b",
    "slack-token": r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b",
    "stripe-live": r"\b[sr]k_live_[A-Za-z0-9]{16,}\b",
    "google-api-key": r"\bAIza[0-9A-Za-z_-]{35}\b",
    "npm-token": r"\bnpm_[A-Za-z0-9]{36}\b",
    "hf-token": r"\bhf_[A-Za-z0-9]{30,}\b",
    "private-key-block": r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----",
    "jwt": r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{20,}\b",
    "url-with-credentials": r"[a-z][a-z0-9+.-]*://[^\s/:@'\"]{3,}:[^\s/@'\"]{3,}@[A-Za-z0-9.-]+",
    "anthropic-key": r"\bsk-ant-[A-Za-z0-9_-]{20,}\b",
    "openai-key": r"\bsk-[A-Za-z0-9]{32,}\b",
    "assigned-secret": r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token)\b\s*[:=]\s*[\"'][A-Za-z0-9/+_=-]{16,}[\"']",
}
_SECRET_RX = {k: re.compile(v) for k, v in SECRET_RULES.items()}


def secret_findings(root: Path, allow: list[dict] | None = None) -> list[str]:
    """Secret-shaped strings in the built tree. Two independent passes: a gitleaks-style regex set, and the
    plugin's own hooks/_scrub.sh (a file is flagged when scrubbing would change it). Findings are reported as
    file:line:rule, never the matched text. An `allow` entry (file + reason) explains a finding that is the
    scrubber's own pattern literal; an allow entry that matches nothing is itself a problem (stale)."""
    allow = allow or []
    scrub = root / "hooks" / "_scrub.sh"
    found: dict[str, list[str]] = {}
    for rel in tree_files(root):
        p = root / rel
        data = p.read_bytes()
        if b"\x00" in data[:4096]:
            continue
        hits = []
        for i, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
            for name, rx in _SECRET_RX.items():
                if rx.search(line):
                    hits.append(f"{i}:{name}")
        if scrub.is_file():
            cp = subprocess.run(
                ["bash", "-c", 'source "$1"; a="$(cat "$2")"; b="$(_scrub_reason "$a")"; [ "$a" = "$b" ]', "_", str(scrub), str(p)],
                capture_output=True,
                text=True,
            )
            if cp.returncode != 0:
                hits.append("0:repo-scrub.sh-would-redact")
        if hits:
            found[rel] = hits
    problems = []
    allowed = {a["file"] for a in allow if str(a.get("reason", "")).strip()}
    for a in allow:
        if not str(a.get("reason", "")).strip():
            problems.append(f"secret_scan_allow {a.get('file')}: a reason is required")
        elif a["file"] not in found:
            problems.append(f"secret_scan_allow names {a['file']}, which has no finding (stale entry)")
    for rel, hits in sorted(found.items()):
        if rel not in allowed:
            problems.append(f"secret-shaped string in {rel}: " + ", ".join(hits[:4]))
    return problems


def check_problems(manifest: dict, repo: Path = REPO) -> tuple[list[str], list[str], Path | None]:
    """Everything the gate checks that needs no hook execution. Returns (problems, dist file list, None).
    The built tree is deleted on return; callers that need it (the hook audit) call full_build themselves."""
    problems: list[str] = []
    with tempfile.TemporaryDirectory(prefix="rc-edition-") as td:
        a, b = Path(td) / "a", Path(td) / "b"
        full_build(manifest, a, repo)
        full_build(manifest, b, repo)
        if digest_tree(a) != digest_tree(b):
            problems.append("two builds from the same source differ (non-deterministic)")
        problems += limits_report(a, manifest["limits"])["violations"]
        problems += structure_findings(a, manifest)
        problems += readme_parity(a, manifest)
        problems += network_findings(a, manifest)
        problems += secret_findings(a, manifest.get("secret_scan_allow", []))
        paths = tree_files(a)
        want = file_list_text(paths)
        lp = file_list_path(manifest, repo)
        have = lp.read_text() if lp.exists() else ""
        if want != have:
            ws, hs = set(want.split()), set(have.split())
            problems.append(
                f"file list is stale ({len(ws - hs)} added, {len(hs - ws)} removed): "
                "run build-directory-edition.py --write-file-list"
            )
    return problems, paths, None


def cmd_check(manifest: dict, repo: Path = REPO) -> int:
    problems, paths, _ = check_problems(manifest, repo)
    for p in problems:
        print("  FAIL", p)
    print("directory-edition build check:", "FAILED" if problems else f"OK ({len(paths)} files)")
    return 1 if problems else 0


def cmd_explain(manifest: dict, repo: Path = REPO) -> int:
    """Every file that is in the build only because something referenced it, with the referrer."""
    plan = plan_build(manifest, repo)
    comps = manifest["components"]
    roots = {f"agents/{a['name']}.md" for a in comps["agents"]} | {
        f"commands/{c['name']}.md" for c in comps["commands"]
    }
    for rel, frm in sorted(plan.via.items()):
        if frm != "<root>" and rel not in roots:
            print(f"{rel}  <-  {frm}")
    return 0


def cmd_report(manifest: dict, repo: Path = REPO) -> int:
    with tempfile.TemporaryDirectory(prefix="rc-edition-") as td:
        out = Path(td) / "dist"
        plan = plan_build(manifest, repo)
        print(f"closure breaks (executable -> denied): {len(plan.closure_breaks)}")
        for a, b, why in plan.closure_breaks:
            print(f"  {a} -> {b}  [{why}]")
        print(f"prose references to denied files (informational): {len(plan.prose_denied)}")
        if plan.closure_breaks:
            return 1
        full_build(manifest, out, repo)
        rep = limits_report(out, manifest["limits"])
        print(f"files: {rep['files']}  bytes: {rep['total_bytes']}")
        for s, r in rep["largest"]:
            print(f"  {s:>9}  {r}")
        for v in rep["violations"]:
            print("  VIOLATION", v)
        for v in network_findings(out, manifest):
            print("  NETWORK", v)
        for v in structure_findings(out, manifest) + readme_parity(out, manifest):
            print("  STRUCTURE", v)
        by_top: dict[str, int] = {}
        for r in tree_files(out):
            by_top[r.split("/")[0]] = by_top.get(r.split("/")[0], 0) + 1
        print("by top-level:", dict(sorted(by_top.items())))
    return 0


# ── self-test ───────────────────────────────────────────────────────────────


def _fixture(root: Path) -> dict:
    p = root / "plugins" / "demo"
    (p / ".claude-plugin").mkdir(parents=True)
    (p / "agents").mkdir()
    (p / "skills" / "good").mkdir(parents=True)
    (p / "skills" / "bad").mkdir(parents=True)
    (p / "commands").mkdir()
    (p / "hooks").mkdir()
    (p / "scripts").mkdir()
    (p / "knowledge").mkdir()
    (p / "bin").mkdir()
    (p / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(
            {
                "name": "demo",
                "version": "1.2.3",
                "author": {"name": "T"},
                "license": "MIT",
                "experimental": {"monitors": "./m.json"},
            }
        )
    )
    (p / "agents" / "a.md").write_text("---\nname: a\n---\nSee knowledge/k.md for detail.\n")
    (p / "knowledge" / "k.md").write_text("knowledge\n")
    (p / "skills" / "good" / "SKILL.md").write_text(
        "---\nname: good\n---\nRun scripts/helper.py.\n"
    )
    (p / "skills" / "bad" / "SKILL.md").write_text("---\nname: bad\n---\nbad\n")
    (p / "scripts" / "helper.py").write_text("print('hi')\n")
    (p / "commands" / "c.md").write_text("---\ndescription: c\n---\ncommand\n")
    (p / "hooks" / "keep.sh").write_text(
        '#!/usr/bin/env bash\nsource "$(dirname "$0")/_lib.sh"\nexit 0\n'
    )
    (p / "hooks" / "_lib.sh").write_text("#!/usr/bin/env bash\n:\n")
    (p / "hooks" / "drop.sh").write_text("#!/usr/bin/env bash\nexit 2\n")
    for h in ("keep.sh", "_lib.sh", "drop.sh"):
        (p / "hooks" / h).chmod(0o755)
    (p / "bin" / "tool").write_text("#!/bin/sh\n")
    (p / "hooks" / "hooks.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "Stop": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": '"${CLAUDE_PLUGIN_ROOT}/hooks/keep.sh"',
                                },
                                {
                                    "type": "command",
                                    "command": '"${CLAUDE_PLUGIN_ROOT}/hooks/drop.sh"',
                                },
                            ]
                        }
                    ]
                }
            }
        )
    )
    tdir = root / "docs" / "directory-edition" / "demo" / "templates"
    tdir.mkdir(parents=True)
    (root / "LICENSE").write_text("MIT License\n")
    (tdir / "README.md").write_text(
        "# demo {{VERSION}}\n{{HOOK_TABLE}}\n{{AGENT_LIST}}\n{{SKILL_LIST}}\n{{COMMAND_LIST}}\n{{REPO}} {{HOMEPAGE}} {{PORTAL}} {{SUPPORT}}\n"
    )
    (tdir / "PRIVACY.md").write_text("privacy {{VERSION}} {{SUPPORT}}\n")
    (tdir / "LICENSE").write_text("MIT {{REPO}}\n")
    return {
        "_dir": str(root / "docs" / "directory-edition" / "demo"),
        "schema_version": 1,
        "plugin": "demo",
        "source_plugin_dir": "plugins/demo",
        "target": {
            "repository": "https://example.invalid/demo",
            "homepage": "https://example.invalid/demo",
            "marketplace_name": "demo",
            "portal_url": "https://example.invalid/portal",
            "support": "https://example.invalid/issues",
        },
        "plugin_json": {"description": "Demo.", "displayName": "Demo"},
        "limits": {
            "max_files": 40,
            "max_file_bytes_nonimage": 1024,
            "max_file_bytes": 4096,
            "max_total_bytes": 100000,
        },
        "closure": {"prose_depth": 1},
        "components": {
            "agents": [{"name": "a", "reason": "agent"}],
            "skills": [{"name": "good", "reason": "skill"}],
            "commands": [{"name": "c", "reason": "cmd"}],
            "hooks": [{"id": "keep.sh", "reason": "r", "summary": "does nothing"}],
        },
        "deny_globs": [
            {"glob": "bin/**", "reason": "no bin"},
            {"glob": "hooks/drop.sh", "reason": "always on"},
        ],
        "network_classification": {},
    }


def self_test() -> int:
    ok = bad = 0

    def check(label: str, cond: bool) -> None:
        nonlocal ok, bad
        print(("  ok   " if cond else "  FAIL ") + label)
        ok, bad = (ok + 1, bad) if cond else (ok, bad + 1)

    def expect_error(label: str, fn, needle: str) -> None:
        try:
            fn()
        except BuildError as e:
            check(label + f" [{needle}]", needle in str(e))
            return
        check(label + " (no error raised)", False)

    with tempfile.TemporaryDirectory(prefix="rc-edition-self-") as td:
        root = Path(td)
        m = _fixture(root)
        plan = plan_build(m, root)
        shipped = set(plan.files)
        check(
            "agent, command, skill copied",
            {"agents/a.md", "commands/c.md", "skills/good/SKILL.md"} <= shipped,
        )
        check(
            "a skill that is not allow-listed does not ship", "skills/bad/SKILL.md" not in shipped
        )
        check(
            "closure pulls in a referenced knowledge file (prose, one hop)",
            "knowledge/k.md" in shipped,
        )
        check("closure pulls in a referenced script", "scripts/helper.py" in shipped)
        check("closure pulls in a hook's sibling helper", "hooks/_lib.sh" in shipped)
        check("an un-listed hook does not ship", "hooks/drop.sh" not in shipped)
        hj = json.loads(plan.generated["hooks/hooks.json"])
        cmds = [h["command"] for g in hj["hooks"]["Stop"] for h in g["hooks"]]
        check("hooks.json is filtered to the manifest", len(cmds) == 1 and "keep.sh" in cmds[0])
        pj = json.loads(plan.generated[".claude-plugin/plugin.json"])
        check("plugin.json drops `experimental`", "experimental" not in pj)
        check(
            "plugin.json version equals the source (single source of truth)",
            pj["version"] == "1.2.3",
        )

        out1, out2 = root / "o1", root / "o2"
        full_build(m, out1, root)
        full_build(m, out2, root)
        check(
            "two builds are byte-identical (deterministic)", digest_tree(out1) == digest_tree(out2)
        )
        check(
            "hook scripts keep their executable bit", os.access(out1 / "hooks" / "keep.sh", os.X_OK)
        )
        hj1 = json.loads((out1 / "hooks" / "hooks.json").read_text())
        gcmds = [h["command"] for g in hj1["hooks"]["Stop"] for h in g["hooks"]]
        check(
            "gate: a gated hook's command is wrapped in the posture gate",
            gcmds[0].startswith(GATE_PREFIX),
        )
        check(
            "gate: the shim ships, is executable and is the reviewed text",
            (out1 / GATE_PATH).read_text() == POSTURE_GATE_SH
            and os.access(out1 / GATE_PATH, os.X_OK),
        )
        check("README lists exactly the shipped hooks", not readme_parity(out1, m))
        check("structure findings are clean", not structure_findings(out1, m))
        check(
            "limits are clean for a small tree", not limits_report(out1, m["limits"])["violations"]
        )

        # ── must-fail halves: each guard has to be capable of failing ──
        mu = json.loads(json.dumps(m))
        mu["components"]["hooks"][0]["ungated"] = True
        check(
            "manifest: ungated without an ungated_reason is rejected",
            any("ungated_reason" in x for x in validate_manifest(mu)),
        )
        m2 = json.loads(json.dumps(m))
        (root / "plugins" / "demo" / "hooks" / "keep.sh").write_text(
            '#!/usr/bin/env bash\nbash "$CLAUDE_PLUGIN_ROOT/bin/tool"\n'
        )
        p2 = plan_build(m2, root)
        check(
            "closure: an executable file referencing a DENIED file is a build break",
            bool(p2.closure_breaks),
        )
        m2["closure_allow"] = [{"from": "hooks/keep.sh", "to": "bin/tool", "reason": "demo"}]
        check(
            "closure: an explicit allow-list entry clears it",
            not plan_build(m2, root).closure_breaks,
        )
        (root / "plugins" / "demo" / "hooks" / "keep.sh").write_text(
            '#!/usr/bin/env bash\nsource "$(dirname "$0")/_lib.sh"\nexit 0\n'
        )

        (root / "plugins" / "demo" / "knowledge" / "k.md").write_text("see bin/tool\n")
        check(
            "a PROSE reference to a denied file is informational, not a break",
            not plan_build(m, root).closure_breaks,
        )
        (root / "plugins" / "demo" / "knowledge" / "k.md").write_text("knowledge\n")

        m3 = json.loads(json.dumps(m))
        m3["components"]["agents"][0]["reason"] = ""
        check(
            "manifest: an entry without a reason is rejected",
            any("REASON" in x for x in validate_manifest(m3)),
        )
        m4 = json.loads(json.dumps(m))
        m4["components"]["hooks"].append({"id": "ghost.sh", "reason": "r", "summary": "s"})
        expect_error(
            "manifest: a hook that is not registered in the source fails the build",
            lambda: plan_build(m4, root),
            "ghost.sh",
        )

        big = root / "o1" / "knowledge" / "huge.md"
        big.write_text("x" * 5000)
        check(
            "limits: a non-image file over the cap is a violation",
            bool(limits_report(root / "o1", m["limits"])["violations"]),
        )
        big.unlink()
        (root / "o1" / "knowledge" / "link.md").symlink_to("k.md")
        check(
            "limits: a symlink is a violation",
            any("symlink" in v for v in limits_report(root / "o1", m["limits"])["violations"]),
        )
        (root / "o1" / "knowledge" / "link.md").unlink()
        (root / "o1" / "knowledge" / "blob.bin").write_bytes(b"\x00\x01\x02" * 10)
        check(
            "limits: non-image binary content is a violation",
            any("binary" in v for v in limits_report(root / "o1", m["limits"])["violations"]),
        )
        (root / "o1" / "knowledge" / "blob.bin").unlink()

        hjb = json.loads((root / "o1" / "hooks" / "hooks.json").read_text())
        hjb["hooks"]["Stop"][0]["hooks"][0]["command"] = '"${CLAUDE_PLUGIN_ROOT}/hooks/keep.sh"'
        (root / "o1" / "hooks" / "hooks.json").write_text(json.dumps(hjb))
        check(
            "gate: an un-wrapped registration is a structure finding",
            any("not wrapped" in x for x in structure_findings(root / "o1", m)),
        )
        (root / "o1" / "README.md").write_text("# no hook table\n")
        check("README parity: a missing hook row is caught", bool(readme_parity(root / "o1", m)))
        (root / "o1" / "hooks" / "stray.sh").write_text("#!/bin/sh\n")
        (root / "o1" / "hooks" / "stray.sh").chmod(0o755)
        (root / "o1" / "README.md").write_text("`keep.sh`\n")
        check(
            "README parity: an unregistered script in hooks/ is caught",
            any("stray.sh" in x for x in readme_parity(root / "o1", m)),
        )

        (root / "o1" / "scripts" / "helper.py").write_text(
            "import urllib.request\nurllib.request.urlopen('https://example.invalid/x')\n"
        )
        nf = network_findings(root / "o1", m)
        check(
            "network: an unclassified primitive/URL is a finding", any("helper.py" in x for x in nf)
        )
        m["network_classification"] = {
            "scripts/helper.py": {"kind": "user-configured", "reason": "demo"}
        }
        check(
            "network: a classified entry with a reason clears it",
            not network_findings(root / "o1", m),
        )
        m["network_classification"]["scripts/ghost.py"] = {"kind": "text-only", "reason": "x"}
        check(
            "network: a classification for a file that does not ship is stale",
            any("stale" in x for x in network_findings(root / "o1", m)),
        )

        planted = root / "o1" / "knowledge" / "planted.md"
        planted.write_text("token = " + "gh" + "p_" + "0123456789abcdef0123456789abcdef0123" + "\n")
        check("secrets: a planted token is a finding", any("planted.md" in x for x in secret_findings(root / "o1")))
        check(
            "secrets: an allow entry with a reason clears it",
            not secret_findings(root / "o1", [{"file": "knowledge/planted.md", "reason": "test"}]),
        )
        check(
            "secrets: an allow entry without a reason does not",
            any("reason is required" in x for x in secret_findings(root / "o1", [{"file": "knowledge/planted.md", "reason": ""}])),
        )
        planted.unlink()
        check(
            "secrets: an allow entry that matches nothing is stale",
            any("stale" in x for x in secret_findings(root / "o1", [{"file": "knowledge/planted.md", "reason": "test"}])),
        )
        check("secrets: a clean tree has no findings", not secret_findings(root / "o1"))

        (root / "plugins" / "demo" / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "demo", "version": "9.9.9", "author": {"name": "T"}})
        )
        check(
            "a source version bump flows through with no manifest edit",
            json.loads(
                plan_build(json.loads(json.dumps(m)), root).generated[".claude-plugin/plugin.json"]
            )["version"]
            == "9.9.9",
        )
    print(f"build-directory-edition self-test: {ok} passed, {bad} failed")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--repo", type=Path, default=REPO, help="repo root holding the source plugin")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument(
        "--explain",
        action="store_true",
        help="list files that ship only via closure, with their referrer",
    )
    ap.add_argument("--write-file-list", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    try:
        manifest = load_manifest(a.manifest)
        repo = a.repo.resolve()
        if a.check:
            return cmd_check(manifest, repo)
        if a.report:
            return cmd_report(manifest, repo)
        if a.explain:
            return cmd_explain(manifest, repo)
        if a.write_file_list:
            with tempfile.TemporaryDirectory(prefix="rc-edition-") as td:
                full_build(manifest, Path(td) / "d", repo)
                paths = tree_files(Path(td) / "d")
            file_list_path(manifest).write_text(file_list_text(paths))
            print(f"wrote {file_list_path(manifest)} ({len(paths)} files)")
            return 0
        if a.out:
            full_build(manifest, a.out.resolve(), repo)
            print(f"built {len(tree_files(a.out))} files into {a.out}")
            return 0
    except BuildError as e:
        print(f"BUILD ERROR: {e}", file=sys.stderr)
        return 2
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
