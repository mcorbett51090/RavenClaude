#!/usr/bin/env python3
"""concepts.py — single-source loader/validator for the Learn-tab concepts.

Reads `plugins/ravenclaude-core/knowledge/concepts/*.md` — one concept per file:
YAML frontmatter + a markdown body + a ```mermaid full diagram and an optional
```mermaid-mini tooltip diagram. Validates the schema and emits the
byte-deterministic portal contract `plugins/ravenclaude-core/concepts.json`.

This is also the import surface for `generate-dashboards.py` (Learn tab +
tooltip registry) and `generate-concepts-doc.py` (docs export): call
`load_concepts(root)` to get validated concept dicts.

Usage:
    concepts.py [--root DIR]            # (re)generate concepts.json
    concepts.py --check [--root DIR]    # schema + staleness + freshness gate
                                        #   (exit 1 on any violation or drift)

The `--check` mode is the CI gate: it re-derives the registry in memory and
diffs it against the committed concepts.json, enforces the schema, and fails
platform-fact concepts whose `last_verified` is older than STALE_DAYS.
"""

from __future__ import annotations

import argparse
import datetime
import glob
import hashlib
import json
import re
import sys
from pathlib import Path

CONCEPTS_GLOB = "plugins/ravenclaude-core/knowledge/concepts/*.md"
REGISTRY_PATH = "plugins/ravenclaude-core/concepts.json"
VISUALS_DIR = "plugins/ravenclaude-core/knowledge/concepts/visuals"
SVG_REL_PREFIX = "knowledge/concepts/visuals"
SCHEMA_VERSION = 1
STALE_DAYS = 90  # platform-fact concepts older than this fail --check

# ── P3: the staleness gate, and why it now has TWO axes ────────────────────
#
# ⛔ THE DOUBLE EXEMPTION THIS CLOSES. The gate used to read:
#     if c["kind"] != "platform-fact" or not c["last_verified"]: continue
# A concept escaped if it was EITHER not a platform-fact OR simply lacked the
# field. Both escapes mattered, and the corpus made the first dominant: 41
# ravenclaude-built against 17 platform-fact, so the gate covered the MINORITY
# kind. Every inventory entry would be ravenclaude-built and inherit zero
# staleness pressure. Fixing only the kind check leaves the second escape wide
# open — an entry with no last_verified at all is still skipped, and "unverified"
# then looks identical to "verified recently". That is the silent-green shape.
#
# ⛔ CONTENT DRIFT IS THE PRIMARY AXIS; CALENDAR AGE IS SECONDARY.
# The arithmetic decides it. At 162 entries on a 180-day clock, steady state needs
# ~0.9 re-verifications every day, forever; at 30 days it is ~5.4/day and the gate
# is red essentially always, so it gets disabled within a month. Worse, entries
# authored in waves EXPIRE IN WAVES on the same day, turning every open PR in the
# repo red — including PRs touching nothing related. That is not a deadline; it is
# a periodic repo-wide outage with a documentation task as the only exit.
#
# Content drift fires when the fact CAN ACTUALLY HAVE BECOME FALSE, not when a
# calendar rolls, and it is the same computation covers_digest already needs.
#
#   axis                           PR CI      scheduled sweep (--sweep)
#   content drift (covers_digest)  BLOCKING   blocking
#   absent last_verified           BLOCKING   blocking
#   kind: platform-fact, 90 days   BLOCKING   blocking   (small, serviceable population)
#   calendar age, inventory        WARNING    BLOCKING
INVENTORY_STALE_DAYS = 180  # calendar window for entry_class: inventory
ENTRY_CLASS_INVENTORY = "inventory"
VALID_ENTRY_CLASSES = (ENTRY_CLASS_INVENTORY,)
RESTAMP_LOG = "tests/fixtures/inventory-restamp-log.jsonl"
RESTAMP_REASON_MIN = 30  # chars; a restamp is a re-READ, not an edit
_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

VALID_KINDS = ("platform-fact", "ravenclaude-built")
STEP_CAPTION_MAX = 120  # a step caption is a one-liner, not a paragraph
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
# The (?![\w-]) after the tag keeps this from also matching ```mermaid-step
# fences (which are collected separately, in document order, below).
_MERMAID_RE = re.compile(r"```(mermaid(?:-mini)?)(?![\w-])[^\n]*\n(.*?)```", re.DOTALL)
_MINI_MARKER_RE = re.compile(r"<!--\s*mini\s*-->\s*", re.IGNORECASE)
# Step diagrams (optional, ordered): each ```mermaid-step block is one frame of a
# step-by-step "stepper" in the Learn tab; an optional <!-- step: caption --> just
# before a block sets that frame's caption (default "Step N").
_STEP_FENCE_RE = re.compile(r"```mermaid-step[^\n]*\n(.*?)```", re.DOTALL)
_STEP_MARKER_RE = re.compile(r"<!--\s*step:\s*(.*?)\s*-->", re.IGNORECASE | re.DOTALL)


class ConceptError(Exception):
    """A schema/validation failure tied to a specific concept file."""


def _today() -> datetime.date:
    return datetime.date.today()


def digest_inputs(root: Path, covers: list[str], refresh_when) -> list[str]:
    """The repo-relative paths whose CONTENT the entry stands on, sorted.

    covers[] is the declared set. A LIST-valued refresh_when is the structured
    form of the same idea — extra path globs evaluated by the same drift check —
    so its expansion joins the digest input. Free-text refresh_when stays prose
    and contributes nothing computable, which is why it renders in the failure
    message instead.

    ⛔ plan-B proposed `git log -1 --format=%cI` timestamps as the drift axis. The
    IDEA is adopted; that implementation is rejected — a git-log timestamp is
    fragile to squash, rebase and shallow clones, where a content hash is not.
    """
    paths = set(covers)
    if isinstance(refresh_when, list):
        rroot = root.resolve()
        for pat in refresh_when:
            for hit in glob.glob(str(root / pat), recursive=True):
                hp = Path(hit)
                if hp.is_file():
                    paths.add(hp.resolve().relative_to(rroot).as_posix())
    return sorted(paths)


def compute_covers_digest(root: Path, covers: list[str], refresh_when=None) -> str:
    """sha256 over the sorted concat of every covered file, path-delimited.

    ⛔ The digest is over the WHOLE FILE INCLUDING COMMENTS, deliberately: in this
    repo the comments ARE where the mechanism nuance lives. The cost is that a
    comment typo trips the same tripwire as a mechanism change. That is what
    --restamp-cosmetic is for: it re-stamps the digest WITHOUT advancing
    last_verified, so a cosmetic edit does not buy 180 days of false freshness.
    """
    h = hashlib.sha256()
    for rel in digest_inputs(root, covers, refresh_when):
        fp = root / rel
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(fp.read_bytes() if fp.is_file() else b"<MISSING>")
        h.update(b"\0")
    return "sha256:" + h.hexdigest()


def _parse_one(path: Path, root: Path) -> dict:
    """Parse and schema-validate a single concept file. Raises ConceptError."""
    try:
        import yaml  # local import so a missing pyyaml degrades to a clear message
    except ImportError:
        print("concepts.py: pyyaml is required — run `pip install pyyaml`", file=sys.stderr)
        sys.exit(1)

    rel = path.name
    stem = path.stem
    text = path.read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if not m:
        raise ConceptError(f"{rel}: no YAML frontmatter (missing leading '---' block)")
    try:
        fm = yaml.safe_load(m.group(1))
    except Exception as exc:  # strict-YAML parse error
        raise ConceptError(f"{rel}: frontmatter does not parse — {type(exc).__name__}: {str(exc).splitlines()[0]}")
    if not isinstance(fm, dict):
        raise ConceptError(f"{rel}: frontmatter is not a mapping")

    def req(key: str, typ) -> object:
        if key not in fm:
            raise ConceptError(f"{rel}: missing required field '{key}'")
        val = fm[key]
        if not isinstance(val, typ) or (isinstance(val, str) and not val.strip()):
            raise ConceptError(f"{rel}: field '{key}' must be a non-empty {getattr(typ, '__name__', typ)}")
        return val

    cid = req("id", str)
    if not _ID_RE.match(cid):
        raise ConceptError(f"{rel}: id '{cid}' must be a lowercase slug (a-z, 0-9, hyphen)")
    if cid != stem:
        raise ConceptError(f"{rel}: id '{cid}' must match the filename stem '{stem}'")
    title = req("title", str)
    category = req("category", str)
    kind = req("kind", str)
    if kind not in VALID_KINDS:
        raise ConceptError(f"{rel}: kind '{kind}' must be one of {VALID_KINDS}")
    order = req("order", int)
    summary = req("summary", str)
    if len(summary) > 200:
        raise ConceptError(f"{rel}: summary is {len(summary)} chars (max 200 — it is a tooltip)")

    sources = fm.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ConceptError(f"{rel}: 'sources' must be a non-empty list of {{label, url}}")
    norm_sources = []
    for i, s in enumerate(sources):
        if not isinstance(s, dict) or not isinstance(s.get("label"), str) or not isinstance(s.get("url"), str):
            raise ConceptError(f"{rel}: sources[{i}] must have string 'label' and 'url'")
        norm_sources.append({"label": s["label"], "url": s["url"]})

    see_also = fm.get("see_also", [])
    if not isinstance(see_also, list) or not all(isinstance(x, str) for x in see_also):
        raise ConceptError(f"{rel}: 'see_also' must be a list of concept ids")

    widget = fm.get("widget")
    if widget is not None and (not isinstance(widget, str) or not widget.strip()):
        raise ConceptError(f"{rel}: 'widget' must be a non-empty string (an interactive widget name)")

    node_links = fm.get("node_links")
    if node_links is not None:
        if not isinstance(node_links, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in node_links.items()
        ):
            raise ConceptError(f"{rel}: 'node_links' must be a mapping of Mermaid node id -> concept id")
        node_links = {str(k): v for k, v in node_links.items()}
    else:
        node_links = {}

    try_it = fm.get("try_it")
    if try_it is not None:
        if (
            not isinstance(try_it, dict)
            or not isinstance(try_it.get("label"), str)
            or not isinstance(try_it.get("href"), str)
        ):
            raise ConceptError(f"{rel}: 'try_it' must be a mapping with string 'label' and 'href'")
        try_it = {"label": try_it["label"], "href": try_it["href"]}

    last_verified = fm.get("last_verified")
    if last_verified is not None:
        # PyYAML may parse an unquoted YYYY-MM-DD into a date; accept both.
        if isinstance(last_verified, datetime.date):
            last_verified = last_verified.isoformat()
        elif isinstance(last_verified, str):
            try:
                datetime.date.fromisoformat(last_verified)
            except ValueError:
                raise ConceptError(f"{rel}: last_verified '{last_verified}' must be YYYY-MM-DD")
        else:
            raise ConceptError(f"{rel}: last_verified must be a YYYY-MM-DD string")
    if kind == "platform-fact" and not last_verified:
        raise ConceptError(f"{rel}: platform-fact concepts require 'last_verified' (staleness gate)")

    # refresh_when is the field the schema already reserved for a machine-actionable
    # refresh trigger. Rather than ship two new fields beside a decorative third,
    # it carries BOTH forms: free text (renders in the failure message) or a list
    # of path globs (joins the drift computation).
    refresh_when = fm.get("refresh_when")
    if refresh_when is not None:
        if isinstance(refresh_when, list):
            if not all(isinstance(x, str) and x.strip() for x in refresh_when):
                raise ConceptError(f"{rel}: 'refresh_when' list entries must be non-empty path globs")
        elif not isinstance(refresh_when, str):
            raise ConceptError(f"{rel}: 'refresh_when' must be a string or a list of path globs")

    # ── entry_class / covers / covers_digest (P3) ──────────────────────────
    # ⛔ ABSENT entry_class MUST reproduce today behaviour exactly. The 58 existing
    # concepts carry none, and concepts.json is asserted byte-identical to HEAD.
    entry_class = fm.get("entry_class")
    if entry_class is not None and entry_class not in VALID_ENTRY_CLASSES:
        raise ConceptError(f"{rel}: entry_class '{entry_class}' must be one of {VALID_ENTRY_CLASSES}")

    covers = fm.get("covers")
    if covers is not None:
        if not isinstance(covers, list) or not covers or not all(
            isinstance(x, str) and x.strip() for x in covers
        ):
            raise ConceptError(f"{rel}: 'covers' must be a non-empty list of repo-relative paths")
        for cp in covers:
            if cp.startswith("/") or ".." in Path(cp).parts:
                raise ConceptError(f"{rel}: covers entry '{cp}' must be repo-relative with no parent segments")
            if not (root / cp).exists():
                raise ConceptError(f"{rel}: covers entry '{cp}' does not exist")
    elif entry_class == ENTRY_CLASS_INVENTORY:
        raise ConceptError(f"{rel}: entry_class: inventory requires a non-empty 'covers' list")

    covers_digest = fm.get("covers_digest")
    if covers_digest is not None:
        if not isinstance(covers_digest, str) or not _DIGEST_RE.match(covers_digest):
            raise ConceptError(f"{rel}: 'covers_digest' must look like sha256 followed by 64 hex chars")
    elif covers is not None:
        raise ConceptError(
            f"{rel}: 'covers' is declared with no 'covers_digest' — the tripwire would "
            f"never fire. Generate it with: scripts/concepts.py --restamp-cosmetic {cid}"
        )

    # Body + diagrams.
    rest = m.group(2)
    diagrams = {"mermaid": None, "mermaid-mini": None}
    for kind_tag, src in _MERMAID_RE.findall(rest):
        if diagrams.get(kind_tag):
            raise ConceptError(f"{rel}: more than one ```{kind_tag} block")
        diagrams[kind_tag] = src.strip()
    if not diagrams["mermaid"]:
        raise ConceptError(f"{rel}: missing the required ```mermaid full diagram block")

    # Ordered step frames: walk markers + fences by document position so each
    # block picks up the caption immediately preceding it.
    steps: list[dict] = []
    events: list[tuple[int, str, str]] = []
    for mm in _STEP_MARKER_RE.finditer(rest):
        events.append((mm.start(), "marker", mm.group(1).strip()))
    for mm in _STEP_FENCE_RE.finditer(rest):
        events.append((mm.start(), "block", mm.group(1).strip()))
    events.sort(key=lambda e: e[0])
    pending: str | None = None
    for _, ev_kind, val in events:
        if ev_kind == "marker":
            pending = val
            continue
        n = len(steps) + 1
        if not val:
            raise ConceptError(f"{rel}: empty ```mermaid-step block (step #{n})")
        caption = pending or f"Step {n}"
        if len(caption) > STEP_CAPTION_MAX:
            raise ConceptError(
                f"{rel}: step #{n} caption is {len(caption)} chars (max {STEP_CAPTION_MAX})"
            )
        steps.append(
            {"caption": caption, "diagram": val, "svg": f"{SVG_REL_PREFIX}/{cid}.step-{n}.svg"}
        )
        pending = None

    body_md = _MERMAID_RE.sub("", rest)
    body_md = _STEP_FENCE_RE.sub("", body_md)
    body_md = _STEP_MARKER_RE.sub("", body_md)
    body_md = _MINI_MARKER_RE.sub("", body_md).strip()
    if not body_md:
        raise ConceptError(f"{rel}: empty body (need an explanation, not just a diagram)")

    has_mini = diagrams["mermaid-mini"] is not None
    # ⛔ The new keys are added CONDITIONALLY. Emitting them as nulls on all 58
    # existing concepts would rewrite concepts.json, and "concepts.json is
    # byte-identical to HEAD" is the positive control proving this change is
    # additive. A schema change that quietly rewrites the registry is
    # indistinguishable from one that broke it.
    out = {
        "id": cid,
        "title": title,
        "category": category,
        "kind": kind,
        "order": order,
        "summary": summary,
        "see_also": list(see_also),
        "widget": widget,
        "try_it": try_it,
        "node_links": node_links,
        "last_verified": last_verified,
        "refresh_when": refresh_when,
        "sources": norm_sources,
        "body_md": body_md,
        "diagram": diagrams["mermaid"],
        "diagram_mini": diagrams["mermaid-mini"],
        "steps": steps,
        "svg": f"{SVG_REL_PREFIX}/{cid}.svg",
        "svg_mini": f"{SVG_REL_PREFIX}/{cid}.mini.svg" if has_mini else None,
    }
    if entry_class is not None:
        out["entry_class"] = entry_class
    if covers is not None:
        out["covers"] = list(covers)
        out["covers_digest"] = covers_digest
    return out


def load_concepts(root: Path) -> list[dict]:
    """Parse + validate every concept. Raises ConceptError on the first problem
    (cross-reference checks run after all files parse). Returns the canonical
    sort order: by (category-min-order, category, order, id)."""
    files = sorted(glob.glob(str(root / CONCEPTS_GLOB)))
    if not files:
        return []
    concepts = [_parse_one(Path(f), root) for f in files]

    ids = {c["id"] for c in concepts}
    for c in concepts:
        for ref in c["see_also"]:
            if ref not in ids:
                raise ConceptError(f"{c['id']}: see_also references unknown concept '{ref}'")
        for node, ref in c["node_links"].items():
            if ref not in ids:
                raise ConceptError(f"{c['id']}: node_links['{node}'] references unknown concept '{ref}'")

    cat_min = {}
    for c in concepts:
        cat_min[c["category"]] = min(cat_min.get(c["category"], c["order"]), c["order"])
    concepts.sort(key=lambda c: (cat_min[c["category"]], c["category"], c["order"], c["id"]))
    return concepts


def build_registry(root: Path) -> dict:
    concepts = load_concepts(root)
    cat_min: dict[str, int] = {}
    for c in concepts:
        cat_min[c["category"]] = min(cat_min.get(c["category"], c["order"]), c["order"])
    categories = [
        {"name": name, "order": order}
        for name, order in sorted(cat_min.items(), key=lambda kv: (kv[1], kv[0]))
    ]
    return {"schema_version": SCHEMA_VERSION, "categories": categories, "concepts": concepts}


def _serialize(registry: dict) -> str:
    return json.dumps(registry, indent=2, ensure_ascii=False) + "\n"


# ── Failure CLASSES, and why they are a machine marker rather than a sentence ──
#
# ⛔ regenerate-artifacts.yml decides whether a failing `--check` is survivable by
# grepping this output. It used to grep the LITERAL SENTENCE "staleness gate
# FAILED"; on no match it ran `exit "$_crc"`, killing every later self-heal step —
# concept SVGs, decision-tree SVGs, dashboard.html, index.html, BI reports, the
# Copilot package, the feedback report. The workflow comment at that site records
# the incident it re-arms: main left UN-HEALED across many merges.
#
# control: scripts/spike-selfheal-contract.sh extracts that conditional FROM the
# workflow and replays it against each output class. Measured 2026-08-19, before
# this change: a covers-digest-drift line was reported FATAL while a
# platform-fact-staleness line was reported CONTINUE.
#
# A prose string a future edit can silently reword is the wrong contract shape —
# that is how the fuse was armed. So the contract is a STABLE MARKER LINE:
#
#   RC-CONCEPTS-CLASS: human-reverify-required
#       Regeneration CANNOT clear this. Only a human re-verifying the fact and
#       moving the date can. The self-heal MUST warn and continue.
#   RC-CONCEPTS-CLASS: generator-failure
#       A real generator failure. The self-heal SHOULD abort.
CLASS_HUMAN = "human-reverify-required"
CLASS_GENERATOR = "generator-failure"
MARKER = "RC-CONCEPTS-CLASS: "


def _is_gated(c: dict) -> bool:
    """Which concepts the freshness gate applies to.

    ⛔ BOTH ESCAPES OF THE OLD CONDITION ARE CLOSED HERE. The old line was
    `if c["kind"] != "platform-fact" or not c["last_verified"]: continue` — an OR,
    so a concept escaped on EITHER limb. This function closes the kind limb;
    _freshness_violations closes the missing-field limb by treating an absent
    last_verified as a VIOLATION rather than a skip. Closing only one leaves the
    silent-green shape intact, which is why they are asserted separately.
    """
    return c.get("entry_class") == ENTRY_CLASS_INVENTORY or c["kind"] == "platform-fact"


def _refresh_hint(c: dict) -> str:
    rw = c.get("refresh_when")
    if isinstance(rw, str) and rw.strip():
        return f"\n      refresh_when: {rw.strip()}"
    if isinstance(rw, list) and rw:
        return f"\n      refresh_when globs: {', '.join(rw)}"
    return ""


def _freshness_violations(
    root: Path, concepts: list[dict], sweep: bool = False
) -> tuple[list[str], list[str]]:
    """Return (blocking, warning). See the axis table at the top of this file.

    ⛔ CALENDAR AGE ON INVENTORY ENTRIES WARNS ON A PR AND BLOCKS ON THE SWEEP.
    A blocking calendar gate over a large corpus is a periodic repo-wide outage —
    entries authored in waves expire in waves, reddening every open PR including
    ones touching nothing related — and a gate that gets disabled protects
    nothing. Content drift carries the blocking duty because it fires when the
    fact can actually have become false.
    """
    today = _today()
    blocking: list[str] = []
    warnings: list[str] = []
    for c in concepts:
        if not _is_gated(c):
            continue
        cid = c["id"]
        lv = c.get("last_verified")

        if not lv:
            # ⛔ ESCAPE 2. An absent field is a VIOLATION, not a skip. Skipping it
            # makes "unverified" render identically to "verified recently".
            blocking.append(f"  ✗ {cid}: last_verified is ABSENT — unverified is not fresh")
        else:
            age = (today - datetime.date.fromisoformat(lv)).days
            if c["kind"] == "platform-fact":
                if age > STALE_DAYS:
                    blocking.append(
                        f"  ✗ {cid}: last_verified {lv} is {age} days old (> {STALE_DAYS})"
                    )
            elif age > INVENTORY_STALE_DAYS:
                msg = (
                    f"  ✗ {cid}: last_verified {lv} is {age} days old "
                    f"(> {INVENTORY_STALE_DAYS}){_refresh_hint(c)}"
                )
                (blocking if sweep else warnings).append(msg)

        covers = c.get("covers")
        if covers:
            actual = compute_covers_digest(root, covers, c.get("refresh_when"))
            if actual != c.get("covers_digest"):
                blocking.append(
                    f"  ✗ {cid}: covers_digest drift — a covered artifact changed after "
                    f"the entry was stamped{_refresh_hint(c)}\n"
                    f"      re-READ the entry, then:  scripts/concepts.py --restamp {cid} "
                    f"--reason '<>={RESTAMP_REASON_MIN} chars on what you re-verified>'\n"
                    f"      cosmetic edit only:       scripts/concepts.py --restamp-cosmetic {cid}\n"
                    f"      (--restamp-cosmetic moves the digest and NOT last_verified, so a "
                    f"typo fix does not buy {INVENTORY_STALE_DAYS} days of false freshness)"
                )
    return blocking, warnings


def _set_frontmatter(path: Path, updates: dict) -> None:
    """Set/replace top-level scalar keys in a concept file frontmatter, in place.

    Line-oriented on purpose: a YAML round-trip would reformat the whole file and
    make a one-field restamp indistinguishable from a rewrite in review.
    """
    text = path.read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if not m:
        raise ConceptError(f"{path.name}: no YAML frontmatter to update")
    fm_lines = m.group(1).split("\n")
    for key, val in updates.items():
        rendered = f'{key}: "{val}"' if key == "covers_digest" else f"{key}: {val}"
        for i, ln in enumerate(fm_lines):
            if re.match(rf"^{re.escape(key)}\s*:", ln):
                fm_lines[i] = rendered
                break
        else:
            fm_lines.append(rendered)
    path.write_text("---\n" + "\n".join(fm_lines) + "\n---\n" + m.group(2), encoding="utf-8")


def _emit(freshness: list[str], generator: list[str], warnings: list[str] | None = None) -> int:
    warnings = warnings or []
    """Report EVERY collected violation class, then exit once.

    ⛔ COLLECT-ALL, NEVER SHORT-CIRCUIT. The previous shape evaluated staleness
    first and returned 1 before it ever compared concepts.json to the serialized
    registry. Adding more early-exit classes into that funnel means one stale
    entry blinds registry-freshness for the whole corpus — the masking-gate
    defect already in this repo record, where a red gate hides later ones in the
    same step. A caller must be able to see both at once.
    """
    if warnings:
        # ⛔ A WARNING IS NOT A PASS AND NOT A FAILURE. It is printed on every run
        # so a corpus drifting past its calendar window is visible on the PR that
        # would otherwise never mention it, while the SWEEP is what blocks.
        print("Concept staleness WARNING (calendar age; blocks on the scheduled sweep, not here):")
        print("\n".join(warnings))
        print()
    if freshness:
        print("Concept staleness gate FAILED — refresh last_verified after re-checking the source:")
        print("\n".join(freshness))
        print(f"{MARKER}{CLASS_HUMAN}")
    if generator:
        if freshness:
            print()
        print("Concept generator gate FAILED:")
        print("\n".join(generator))
        print(f"{MARKER}{CLASS_GENERATOR}")
    return 1 if (freshness or generator) else 0


def _do_restamp(root: Path, registry: dict, args) -> int:
    """Re-stamp one entry. Two forms, and the difference is the whole point.

    ⛔ --restamp IS A CLAIM THAT SOMEBODY RE-READ THE ENTRY, not that a command
    ran. Left as a bare digest refresh it becomes the new advisory-hook-writing-
    to-stderr: it passes every check and nobody re-read the claim. So the
    substantive form requires --reason of >= RESTAMP_REASON_MIN chars and appends
    a committed log line carrying {entry_id, date, reason, digest_before,
    digest_after}. coverage --report then surfaces the RATIO of restamps whose
    nuance text was unchanged — a high ratio is the tell for a rubber-stamp loop.
    That ratio is REPORTED, never gated: a legitimately-unchanged nuance after a
    real re-read is normal, and gating it would manufacture false edits.

    ⛔ --restamp-cosmetic moves covers_digest and NOT last_verified, so fixing a
    typo in a covered file cannot buy the entry another full staleness window.
    """
    cid = args.restamp or args.restamp_cosmetic
    cosmetic = bool(args.restamp_cosmetic)
    by_id = {c["id"]: c for c in registry["concepts"]}
    c = by_id.get(cid)
    if c is None:
        print(f"restamp: no concept with id '{cid}'")
        return 2
    if not c.get("covers"):
        print(f"restamp: '{cid}' declares no covers[] — there is no digest to stamp")
        return 2

    if not cosmetic:
        reason = (args.reason or "").strip()
        if len(reason) < RESTAMP_REASON_MIN:
            print(
                f"restamp: --reason is {len(reason)} chars (need >= {RESTAMP_REASON_MIN}).\n"
                "  A restamp asserts you RE-READ the entry against its covered artifacts.\n"
                "  If you only fixed a typo, use --restamp-cosmetic, which does not move\n"
                "  last_verified and therefore does not buy the entry a fresh window."
            )
            return 2

    path = root / Path(CONCEPTS_GLOB).parent / f"{cid}.md"
    if not path.is_file():
        print(f"restamp: concept file not found at {path}")
        return 2

    before = c.get("covers_digest") or ""
    after = compute_covers_digest(root, c["covers"], c.get("refresh_when"))
    updates = {"covers_digest": after}
    today = _today().isoformat()
    if not cosmetic:
        updates["last_verified"] = today
    _set_frontmatter(path, updates)

    if not cosmetic:
        log = root / RESTAMP_LOG
        log.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "entry_id": cid,
            "date": today,
            "reason": args.reason.strip(),
            "digest_before": before,
            "digest_after": after,
        }
        with log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")

    kind = "cosmetic (last_verified NOT moved)" if cosmetic else f"substantive (last_verified -> {today})"
    print(f"restamped {cid}: {kind}")
    if before == after:
        print("  note: the digest did not change — nothing the entry covers had drifted.")
    print("  now regenerate: scripts/concepts.py")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="repo root")
    ap.add_argument("--check", action="store_true", help="gate mode: validate + diff, never write")
    ap.add_argument(
        "--sweep",
        action="store_true",
        help="scheduled-sweep mode: promote calendar-age WARNINGS to blocking failures",
    )
    ap.add_argument("--restamp", metavar="ID", help="re-stamp an entry after RE-READING it (needs --reason)")
    ap.add_argument(
        "--restamp-cosmetic",
        metavar="ID",
        help="re-stamp covers_digest ONLY, leaving last_verified where it is (cosmetic edits)",
    )
    ap.add_argument("--reason", help=f"why the entry was re-verified (>= {RESTAMP_REASON_MIN} chars)")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    out_path = root / REGISTRY_PATH

    try:
        registry = build_registry(root)
    except ConceptError as exc:
        # A schema failure means there is no registry to compare against, so this
        # is the one class that genuinely cannot collect further violations.
        print(f"Concept schema validation FAILED:\n  ✗ {exc}")
        print(f"{MARKER}{CLASS_GENERATOR}")
        return 1

    serialized = _serialize(registry)

    if args.restamp or args.restamp_cosmetic:
        return _do_restamp(root, registry, args)

    if args.check:
        # Three buckets, ALL filled completely before anything is printed.
        freshness, warnings = _freshness_violations(root, registry["concepts"], sweep=args.sweep)
        generator: list[str] = []

        if not out_path.exists():
            generator.append(f"  ✗ concepts.json missing at {REGISTRY_PATH} — run: scripts/concepts.py")
        elif out_path.read_text(encoding="utf-8") != serialized:
            generator.append("  ✗ concepts.json is STALE — regenerate with: scripts/concepts.py")

        rc = _emit(freshness, generator, warnings)
        if rc == 0:
            mode = "sweep" if args.sweep else "PR"
            print(
                f"Concepts OK — {len(registry['concepts'])} concept(s), registry fresh, "
                f"no stale platform-facts, no covers drift [{mode} mode, "
                f"{len(warnings)} calendar warning(s)]."
            )
        return rc

    out_path.write_text(serialized, encoding="utf-8")
    print(f"Wrote {REGISTRY_PATH} — {len(registry['concepts'])} concept(s) in {len(registry['categories'])} categor(ies).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
