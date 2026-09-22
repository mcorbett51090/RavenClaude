#!/usr/bin/env python3
"""runes.py — Runes ready-queue CLI over the append-only task ledger.

Product one-liner (CoS/Matthew SSOT 2026-09-15, Longship amend):
  Runes are the work; `rc runes ready` is the queue; claim/sling binds the
  Oath-hook; strands instantiate formulas (PE packs); Longships batch delivery
  to Sage (never auto-merge).

Names LOCKED — do NOT reuse Thing / Huginn-Muninn / Thor-Forseti / Hliðskjálf /
Norns panel as the queue. Verðandi/Skuld are facet labels only.
No Gas Town / Beads UX names. No BMA. Sage sole SCM.
Dashboard opt-in: comfort-posture `runes: off|on` (absent⇒off). On = SessionStart
hanging+ready+auto-claim next ungated; never auto Longship merge.
Flat Runes + strands only; kind is an optional tag (fix|feature|chore), not hierarchy.

Cosmology: docs/norse-mythology-feature-map.md
Design SSOT: DIGEST-norse-ready-queue-design-2026-09-15.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Import sibling ledger module without requiring install.
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import ledger as L  # noqa: E402

HUMAN_GATES = ("none", "cos", "matthew", "appsec", "sage", "money")
# Optional kind TAG only — not a hierarchy level. Flat Runes + strands; no epics.
KIND_TAGS = ("fix", "feature", "chore")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
LONGSHIP_DIR = ".ravenclaude/longships"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _actor(args: argparse.Namespace) -> str:
    return getattr(args, "actor", None) or os.environ.get("RC_ACTOR") or "unknown"


def _project_items(repo_root: Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    config = L.resolve_config(repo_root)
    ledger_dir = L._confined_path(repo_root, config["ledger_dir"], "ledger_dir")
    if not ledger_dir.exists():
        raise L.LedgerUnknown(f"ledger not initialised at {ledger_dir}")
    raw, parse_errors, _empty = L.read_ledger(ledger_dir)
    ordered, collisions = L.sort_then_dedupe(raw)
    fold_errors: list[dict[str, Any]] = list(parse_errors)
    items, _non, unrecognized = L.fold(ordered, fold_errors)
    now = _now()
    if ordered:
        try:
            now = L.parse_ts(str((ordered[-1].obj.get("machine") or {}).get("ts") or ""))
        except Exception:
            pass
    L.derive(items, now, config)
    for item in items.values():
        _annotate_rune(item)
    return items, fold_errors + unrecognized + collisions, config


def _annotate_rune(item: dict[str, Any]) -> None:
    """Derive Verðandi/Skuld facet labels ONLY — never overload the Norns panel."""
    gate = item.get("human_gate") or "none"
    blocked = bool(item.get("blocked"))
    state = item.get("state")
    if state == "done":
        item["facet"] = None
        item["ready_now"] = False
        return
    gated = gate != "none"
    if gated or blocked:
        item["facet"] = "skuld"  # owed / backlog / human-gated
        item["ready_now"] = False
        return
    # Verðandi = ready-now: unblocked, ungated, not done, not already claimed.
    if item.get("hook_owner"):
        item["facet"] = "verdandi"
        item["ready_now"] = False  # on someone's hook — Oath-hook surface, not ready queue
        return
    if state in ("proposed", "ready"):
        item["facet"] = "verdandi"
        item["ready_now"] = True
        return
    if state == "in_progress":
        item["facet"] = "verdandi"
        item["ready_now"] = False
        return
    item["facet"] = "skuld"
    item["ready_now"] = False


def _ready_items(items: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    ready = [i for i in items.values() if i.get("ready_now")]
    ready.sort(key=lambda i: (L._as_priority(i.get("priority")), i.get("first_ts") or "", i["item_id"]))
    return ready


def _hanging_on_hook(items: dict[str, dict[str, Any]], owner: str) -> list[dict[str, Any]]:
    out = []
    for item in items.values():
        if item.get("hook_owner") != owner:
            continue
        if item.get("state") in ("ready", "in_progress", "proposed"):
            out.append(item)
    out.sort(key=lambda i: (i.get("last_event_ts") or "", i["item_id"]))
    return out


def read_runes_posture(repo_root: Path) -> str:
    """Comfort-posture SSOT key `runes:` → off|on. Absent ⇒ off.

    Also accepts legacy alias `oath_hook:` on READ only (emitYaml writes `runes:`).
    Same opt-in absent semantics as dashboard_autostart / keep_awake.
    """
    cfg = repo_root / ".ravenclaude" / "comfort-posture.yaml"
    if not cfg.is_file():
        return "off"
    try:
        lines = cfg.read_text(encoding="utf-8").splitlines()
    except OSError:
        return "off"
    found: str | None = None
    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        for key in ("runes:", "oath_hook:"):
            if s.startswith(key):
                rest = s[len(key) :].strip().split("#", 1)[0].strip().strip("'\"")
                val = (rest.split() or [""])[0].lower()
                if key == "runes:":
                    return "on" if val == "on" else "off"
                if found is None:
                    found = "on" if val == "on" else "off"
                break
    return found or "off"


def runes_posture_on(repo_root: Path) -> bool:
    return read_runes_posture(repo_root) == "on"


def auto_claim_next_ungated(repo_root: Path, actor: str) -> dict[str, Any] | None:
    """Claim the next Verðandi (ungated/unblocked/unclaimed) ready Rune for actor.

    REFUSES gated human_gate (matthew|appsec|cos|sage|money|any != none) by
    never selecting them (_ready_items already filters). Never touches Longship.
    Returns claimed item dict or None if queue empty / claim failed.
    """
    try:
        items, _errors, _cfg = _project_items(repo_root)
    except Exception:
        return None
    ready = _ready_items(items)
    if not ready:
        return None
    nxt = ready[0]
    gate = nxt.get("human_gate") or "none"
    if gate != "none":
        return None
    ns = argparse.Namespace(rune_id=nxt["item_id"], actor=actor, force=False)
    code = _claim(repo_root, ns, op_label="auto-claimed")
    if code != 0:
        return None
    items2, _, _ = _project_items(repo_root)
    return items2.get(nxt["item_id"])


def _ensure_ledger(repo_root: Path, actor: str) -> None:
    config = L.resolve_config(repo_root)
    ledger_dir = L._confined_path(repo_root, config["ledger_dir"], "ledger_dir")
    if not ledger_dir.exists() or not any(ledger_dir.glob("*.jsonl")):
        # init if missing — keep stdout clean (callers print only the Rune id)
        ns = argparse.Namespace(actor=actor)
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = L.cmd_init(repo_root, ns)
        for line in buf.getvalue().splitlines():
            print(line, file=sys.stderr)
        if code != 0:
            raise L.LedgerError(f"ledger init failed with exit {code}")


def _append(repo_root: Path, etype: str, item_id: str | None, asserted: dict[str, Any], actor: str) -> dict[str, Any]:
    config = L.resolve_config(repo_root)
    ledger_dir = L._confined_path(repo_root, config["ledger_dir"], "ledger_dir")
    event = L.build_event(repo_root, etype, item_id, asserted, actor)
    L.append_record(ledger_dir, event, int(config["max_record_bytes"]))
    return event


def _fmt_rune(item: dict[str, Any], verbose: bool = False) -> str:
    facet = item.get("facet") or "-"
    gate = item.get("human_gate") or "none"
    owner = item.get("hook_owner") or "-"
    blockers = ",".join(item.get("unresolved_blockers") or []) or "-"
    line = (
        f"{item['item_id']}  [{item.get('state')}/{facet}]  "
        f"gate={gate}  hook={owner}  p{item.get('priority', 3)}  {item.get('subject', '')}"
    )
    if verbose:
        line += (
            f"\n    blockers={blockers}  strand={item.get('strand_id') or '-'}  "
            f"longship={item.get('longship_id') or '-'}  "
            f"formula={item.get('formula_ref') or '-'}  mist={bool(item.get('mist'))}"
        )
    return line


# ── commands ────────────────────────────────────────────────────────────────


def cmd_ready(repo_root: Path, args: argparse.Namespace) -> int:
    items, errors, _cfg = _project_items(repo_root)
    ready = _ready_items(items)
    if args.json:
        payload = {
            "ready": [
                {
                    "item_id": i["item_id"],
                    "subject": i.get("subject"),
                    "state": i.get("state"),
                    "facet": i.get("facet"),
                    "human_gate": i.get("human_gate") or "none",
                    "priority": i.get("priority"),
                    "strand_id": i.get("strand_id"),
                    "longship_id": i.get("longship_id"),
                }
                for i in ready
            ],
            "count": len(ready),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        if not ready:
            print("rc runes ready: (empty) — no Verðandi Runes unblocked/ungated/unclaimed")
        else:
            print(f"rc runes ready: {len(ready)} Verðandi Rune(s)")
            for i in ready:
                print(_fmt_rune(i, verbose=args.verbose))
    return 0 if not errors else 0  # projection noise is not a queue failure


def cmd_show(repo_root: Path, args: argparse.Namespace) -> int:
    items, _errors, _cfg = _project_items(repo_root)
    item = items.get(args.rune_id)
    if item is None:
        print(f"REFUSED: unknown Rune {args.rune_id}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(item, indent=2, sort_keys=True, default=str))
    else:
        print(_fmt_rune(item, verbose=True))
    return 0


def cmd_open(repo_root: Path, args: argparse.Namespace) -> int:
    actor = _actor(args)
    _ensure_ledger(repo_root, actor)
    config = L.resolve_config(repo_root)
    ledger_dir = L._confined_path(repo_root, config["ledger_dir"], "ledger_dir")
    ts = L.utcnow_iso()
    machine = L.machine_block(repo_root, actor, ts)
    item_id = L.mint_item_id(machine["source"], ts, args.title, L._existing_item_ids(ledger_dir))
    asserted: dict[str, Any] = {"subject": args.title[:140]}
    gate = args.gate or "none"
    if gate not in HUMAN_GATES:
        print(f"REFUSED: bad --gate {gate!r}", file=sys.stderr)
        return 1
    asserted["human_gate"] = gate
    if args.strand_id:
        asserted["strand_id"] = args.strand_id
    if args.longship_id:
        asserted["longship_id"] = args.longship_id
    if args.formula_ref:
        asserted["formula_ref"] = args.formula_ref
    if args.mist:
        asserted["mist"] = True
    if args.priority:
        asserted["priority"] = args.priority
    kind = getattr(args, "kind", None)
    if kind:
        if kind not in KIND_TAGS:
            print(f"REFUSED: bad --kind {kind!r} (fix|feature|chore tag only)", file=sys.stderr)
            return 1
        asserted["kind"] = kind  # tag only — not a hierarchy / epic level
    event = L.build_event(repo_root, "open", item_id, asserted, actor, ts)
    L.append_record(ledger_dir, event, int(config["max_record_bytes"]))

    for dep in args.dep or []:
        _append(repo_root, "link", item_id, {"op": "add", "ref": dep}, actor)

    # Ungated + no deps → mark ready (Verðandi surface).
    if gate == "none" and not (args.dep or []):
        _append(
            repo_root,
            "state",
            item_id,
            {"state": "ready", "prev_state": "proposed"},
            actor,
        )
    print(item_id)
    return 0


def _claim(repo_root: Path, args: argparse.Namespace, *, op_label: str) -> int:
    actor = _actor(args)
    items, _errors, _cfg = _project_items(repo_root)
    item = items.get(args.rune_id)
    if item is None:
        print(f"REFUSED: unknown Rune {args.rune_id}", file=sys.stderr)
        return 1
    gate = item.get("human_gate") or "none"
    if gate != "none":
        print(
            f"REFUSED: Rune {args.rune_id} has human_gate={gate} — "
            f"Matthew/CoS/AppSec/Sage wall; never auto-claim",
            file=sys.stderr,
        )
        return 1
    if item.get("blocked"):
        print(
            f"REFUSED: Rune {args.rune_id} still blocked on "
            f"{item.get('unresolved_blockers')}",
            file=sys.stderr,
        )
        return 1
    if item.get("state") == "done":
        print(f"REFUSED: Rune {args.rune_id} is done", file=sys.stderr)
        return 1
    existing = item.get("hook_owner")
    if existing and existing != actor and not args.force:
        print(
            f"REFUSED: Rune {args.rune_id} already on hook_owner={existing} "
            f"(pass --force to steal; Oath-hook still binds the new owner)",
            file=sys.stderr,
        )
        return 1

    _append(repo_root, "hook", args.rune_id, {"op": "claim", "hook_owner": actor}, actor)
    if item.get("state") != "in_progress":
        _append(
            repo_root,
            "state",
            args.rune_id,
            {"state": "in_progress", "prev_state": item.get("state")},
            actor,
        )
    print(f"{op_label}: {args.rune_id} → hook_owner={actor}")
    return 0


def cmd_claim(repo_root: Path, args: argparse.Namespace) -> int:
    return _claim(repo_root, args, op_label="claimed")


def cmd_sling(repo_root: Path, args: argparse.Namespace) -> int:
    return _claim(repo_root, args, op_label="slung")


def cmd_release(repo_root: Path, args: argparse.Namespace) -> int:
    actor = _actor(args)
    items, _errors, _cfg = _project_items(repo_root)
    item = items.get(args.rune_id)
    if item is None:
        print(f"REFUSED: unknown Rune {args.rune_id}", file=sys.stderr)
        return 1
    owner = item.get("hook_owner")
    if not owner:
        print(f"REFUSED: Rune {args.rune_id} has no hook_owner", file=sys.stderr)
        return 1
    if owner != actor and not args.force:
        print(
            f"REFUSED: hook_owner={owner} != actor={actor} (pass --force)",
            file=sys.stderr,
        )
        return 1
    _append(repo_root, "hook", args.rune_id, {"op": "release", "hook_owner": None}, actor)
    # Return to ready if still ungated/unblocked.
    if (item.get("human_gate") or "none") == "none" and not item.get("blocked"):
        if item.get("state") == "in_progress":
            _append(
                repo_root,
                "state",
                args.rune_id,
                {"state": "ready", "prev_state": "in_progress"},
                actor,
            )
    print(f"released: {args.rune_id}")
    return 0


def cmd_hanging(repo_root: Path, args: argparse.Namespace) -> int:
    """List Runes hanging on an actor's Oath-hook (GUPP surface)."""
    actor = args.owner or _actor(args)
    items, _errors, _cfg = _project_items(repo_root)
    hanging = _hanging_on_hook(items, actor)
    if args.json:
        print(
            json.dumps(
                {
                    "hook_owner": actor,
                    "hanging": [
                        {
                            "item_id": i["item_id"],
                            "subject": i.get("subject"),
                            "state": i.get("state"),
                        }
                        for i in hanging
                    ],
                    "must_run": bool(hanging),
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        if not hanging:
            print(f"oath-hook: no hanging Runes for {actor}")
        else:
            print(
                f"OATH-HOOK MUST-RUN: {len(hanging)} Rune(s) hang on hook_owner={actor}"
            )
            for i in hanging:
                print(_fmt_rune(i, verbose=True))
    return 0


# ── strand (v1.1) ───────────────────────────────────────────────────────────


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")[:48]
    return s or "strand"


def cmd_strand_apply(repo_root: Path, args: argparse.Namespace) -> int:
    """Expand a PE pack / formula into child Runes under a strand id."""
    actor = _actor(args)
    _ensure_ledger(repo_root, actor)
    pack = Path(args.formula)
    if not pack.is_file():
        print(f"REFUSED: formula/pack not found: {pack}", file=sys.stderr)
        return 1
    body = pack.read_text(encoding="utf-8", errors="replace")
    # Extract checklist / numbered / bullet work lines as child Rune subjects.
    subjects: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^\s*(?:[-*]|\d+[.)])\s+\[.\]\s+(.+)$", line)
        if not m:
            m = re.match(r"^\s*(?:[-*]|\d+[.)])\s+(.+)$", line)
        if m:
            subj = m.group(1).strip()
            # Skip headings-as-bullets that are too structural
            if len(subj) >= 8 and not subj.lower().startswith(("http://", "https://")):
                subjects.append(subj[:140])
    subjects = subjects[:24]  # hard cap
    if not subjects:
        # Fallback: one Rune for the pack title
        title = pack.stem.replace("-", " ").replace("_", " ")
        subjects = [f"Apply formula: {title}"[:140]]

    strand_id = args.strand_id or f"strand-{_slugify(pack.stem)}"
    if not SLUG_RE.match(strand_id):
        print(f"REFUSED: bad strand_id {strand_id!r}", file=sys.stderr)
        return 1

    minted: list[str] = []
    for subj in subjects:
        ns = argparse.Namespace(
            title=subj,
            gate="none",
            dep=[],
            strand_id=strand_id,
            longship_id=None,
            formula_ref=str(pack),
            mist=False,
            priority=None,
            actor=actor,
        )
        # Capture printed id
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cmd_open(repo_root, ns)
        if code != 0:
            return code
        rid = buf.getvalue().strip().splitlines()[-1]
        minted.append(rid)

    print(
        json.dumps(
            {
                "strand_id": strand_id,
                "formula_ref": str(pack),
                "runes": minted,
                "count": len(minted),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


# ── longship (v1.1) — Sage-facing batch; NEVER auto-merge ───────────────────


def _longship_path(repo_root: Path, longship_id: str) -> Path:
    return repo_root / LONGSHIP_DIR / f"{longship_id}.json"


def _load_longship(repo_root: Path, longship_id: str) -> dict[str, Any]:
    path = _longship_path(repo_root, longship_id)
    if not path.is_file():
        raise L.LedgerError(f"unknown Longship {longship_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def _save_longship(repo_root: Path, doc: dict[str, Any]) -> Path:
    path = _longship_path(repo_root, doc["longship_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def cmd_longship_open(repo_root: Path, args: argparse.Namespace) -> int:
    actor = _actor(args)
    title = args.title or "delivery"
    longship_id = args.longship_id or f"ls-{_slugify(title)}"
    if not SLUG_RE.match(longship_id):
        print(f"REFUSED: bad longship_id {longship_id!r}", file=sys.stderr)
        return 1
    path = _longship_path(repo_root, longship_id)
    if path.exists() and not args.force:
        print(f"REFUSED: Longship {longship_id} exists (pass --force)", file=sys.stderr)
        return 1
    doc = {
        "longship_id": longship_id,
        "title": title[:140],
        "created_by": actor,
        "created_at": L.utcnow_iso(),
        "rune_ids": [],
        "land_requested": False,
        "land_requested_at": None,
        "auto_merge": False,  # HARD — Sage sole; never auto-merge
        "notes": "Sage sole land/merge. No factory auto-merge. No BMA.",
    }
    saved = _save_longship(repo_root, doc)
    print(f"longship open: {longship_id} -> {saved}")
    return 0


def cmd_longship_add(repo_root: Path, args: argparse.Namespace) -> int:
    actor = _actor(args)
    doc = _load_longship(repo_root, args.longship_id)
    items, _errors, _cfg = _project_items(repo_root)
    for rid in args.rune_ids:
        if rid not in items:
            print(f"REFUSED: unknown Rune {rid}", file=sys.stderr)
            return 1
        if rid not in doc["rune_ids"]:
            doc["rune_ids"].append(rid)
        _append(
            repo_root,
            "meta",
            rid,
            {"longship_id": args.longship_id},
            actor,
        )
    _save_longship(repo_root, doc)
    print(
        json.dumps(
            {"longship_id": doc["longship_id"], "rune_ids": doc["rune_ids"]},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def cmd_longship_land_request(repo_root: Path, args: argparse.Namespace) -> int:
    """Request Sage land — NEVER merges. Emits a receipt only."""
    actor = _actor(args)
    doc = _load_longship(repo_root, args.longship_id)
    if not doc.get("rune_ids"):
        print("REFUSED: Longship has no Runes; add some first", file=sys.stderr)
        return 1
    doc["land_requested"] = True
    doc["land_requested_at"] = L.utcnow_iso()
    doc["land_requested_by"] = actor
    doc["auto_merge"] = False
    _save_longship(repo_root, doc)
    print(
        json.dumps(
            {
                "longship_id": doc["longship_id"],
                "land_requested": True,
                "rune_ids": doc["rune_ids"],
                "auto_merge": False,
                "message": "Land request recorded for Sage. No merge performed.",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def cmd_longship_show(repo_root: Path, args: argparse.Namespace) -> int:
    doc = _load_longship(repo_root, args.longship_id)
    print(json.dumps(doc, indent=2, sort_keys=True))
    return 0


# ── self-test ───────────────────────────────────────────────────────────────


def _self_test() -> int:
    import shutil
    import tempfile

    failures: list[str] = []

    def check(cond: bool, msg: str) -> None:
        if not cond:
            failures.append(msg)

    tmp = Path(tempfile.mkdtemp(prefix="rc-runes-"))
    try:
        # Minimal git repo so ledger machine_block / check_committable can work.
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "runes@test"],
            cwd=tmp,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "runes"],
            cwd=tmp,
            check=True,
            capture_output=True,
        )
        # Ensure ledger path is NOT gitignored (committable canary).
        (tmp / ".gitignore").write_text(".ravenclaude/runs/\n", encoding="utf-8")
        subprocess.run(["git", "add", ".gitignore"], cwd=tmp, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=tmp,
            check=True,
            capture_output=True,
        )

        actor = "test-agent"
        ns_init = argparse.Namespace(actor=actor)
        check(L.cmd_init(tmp, ns_init) == 0, "ledger init")

        # open ungated → ready
        import io
        from contextlib import redirect_stdout

        def capture(fn, ns):
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = fn(tmp, ns)
            return code, buf.getvalue().strip()

        code, rid_a = capture(
            cmd_open,
            argparse.Namespace(
                title="Implement ready filter",
                gate="none",
                dep=[],
                strand_id=None,
                longship_id=None,
                formula_ref=None,
                mist=False,
                kind=None,
                priority=2,
                actor=actor,
            ),
        )
        check(code == 0 and rid_a.startswith("rc-"), f"open a got {code} {rid_a!r}")

        code, rid_gate = capture(
            cmd_open,
            argparse.Namespace(
                title="Spend money action",
                gate="matthew",
                dep=[],
                strand_id=None,
                longship_id=None,
                formula_ref=None,
                mist=False,
                kind=None,
                priority=1,
                actor=actor,
            ),
        )
        check(code == 0 and rid_gate.startswith("rc-"), "open gated")

        # dep chain: B blocked on A
        code, rid_b = capture(
            cmd_open,
            argparse.Namespace(
                title="Depends on A",
                gate="none",
                dep=[rid_a],
                strand_id=None,
                longship_id=None,
                formula_ref=None,
                mist=False,
                kind=None,
                priority=3,
                actor=actor,
            ),
        )
        check(code == 0, "open b with dep")

        items, _, _ = _project_items(tmp)
        ready_ids = {i["item_id"] for i in _ready_items(items)}
        check(rid_a in ready_ids, "A should be ready")
        check(rid_gate not in ready_ids, "matthew-gated must NOT be ready")
        check(rid_b not in ready_ids, "B blocked must NOT be ready")
        check(items[rid_gate].get("facet") == "skuld", "gated facet skuld")
        check(items[rid_a].get("facet") == "verdandi", "A facet verdandi")

        # claim / sling
        code, out = capture(
            cmd_claim,
            argparse.Namespace(rune_id=rid_a, actor=actor, force=False),
        )
        check(code == 0 and "claimed" in out, f"claim failed {code} {out}")

        items, _, _ = _project_items(tmp)
        check(items[rid_a].get("hook_owner") == actor, "hook_owner set")
        check(items[rid_a].get("state") == "in_progress", "state in_progress")
        check(rid_a not in {i["item_id"] for i in _ready_items(items)}, "claimed leaves ready")

        # human_gate blocks claim
        code, _out = capture(
            cmd_claim,
            argparse.Namespace(rune_id=rid_gate, actor=actor, force=False),
        )
        check(code == 1, "gated claim must refuse")

        # Oath-hook hanging
        hanging = _hanging_on_hook(items, actor)
        check(any(h["item_id"] == rid_a for h in hanging), "oath-hook sees hanging")

        # sling synonym
        code, rid_c = capture(
            cmd_open,
            argparse.Namespace(
                title="Sling target",
                gate="none",
                dep=[],
                strand_id=None,
                longship_id=None,
                formula_ref=None,
                mist=False,
                kind=None,
                priority=3,
                actor=actor,
            ),
        )
        code, out = capture(
            cmd_sling,
            argparse.Namespace(rune_id=rid_c, actor=actor, force=False),
        )
        check(code == 0 and "slung" in out, "sling")

        # release
        code, out = capture(
            cmd_release,
            argparse.Namespace(rune_id=rid_c, actor=actor, force=False),
        )
        check(code == 0 and "released" in out, "release")
        items, _, _ = _project_items(tmp)
        check(items[rid_c].get("hook_owner") is None, "hook cleared")

        # Longship batch (no auto-merge)
        code, _ = capture(
            cmd_longship_open,
            argparse.Namespace(
                title="Ship runes queue",
                longship_id="ls-runes-test",
                force=False,
                actor=actor,
            ),
        )
        check(code == 0, "longship open")
        check("longship_id" in _load_longship(tmp, "ls-runes-test"), "longship_id key present")
        code, _ = capture(
            cmd_longship_add,
            argparse.Namespace(
                longship_id="ls-runes-test",
                rune_ids=[rid_a],
                actor=actor,
            ),
        )
        check(code == 0, "longship add")
        items, _, _ = _project_items(tmp)
        check(items[rid_a].get("longship_id") == "ls-runes-test", "longship_id on rune")
        code, out = capture(
            cmd_longship_land_request,
            argparse.Namespace(longship_id="ls-runes-test", actor=actor),
        )
        check(code == 0 and "No merge performed" in out, "land-request no merge")
        doc = _load_longship(tmp, "ls-runes-test")
        check(doc.get("auto_merge") is False, "auto_merge false")

        # strand apply
        pack = tmp / "PACK-demo.md"
        pack.write_text(
            "# Demo pack\n\n- [ ] First child work item here\n- [ ] Second child work item\n",
            encoding="utf-8",
        )
        code, out = capture(
            cmd_strand_apply,
            argparse.Namespace(
                formula=str(pack),
                strand_id="strand-demo",
                actor=actor,
            ),
        )
        check(code == 0 and "strand-demo" in out, f"strand apply {out[:200]}")
        payload = json.loads(out)
        check(payload.get("count", 0) >= 2, "strand minted children")

        # --- dashboard opt-in posture + auto-claim B (2026-09-15) ---
        posture_dir = tmp / ".ravenclaude"
        posture_dir.mkdir(parents=True, exist_ok=True)
        check(read_runes_posture(tmp) == "off", "absent posture => off")
        check(not runes_posture_on(tmp), "absent not on")
        (posture_dir / "comfort-posture.yaml").write_text(
            "schema_version: 5\nrunes: off\n", encoding="utf-8"
        )
        check(read_runes_posture(tmp) == "off", "explicit off")
        (posture_dir / "comfort-posture.yaml").write_text(
            "schema_version: 5\nrunes: on\n", encoding="utf-8"
        )
        check(runes_posture_on(tmp), "explicit on")

        code, rid_money = capture(
            cmd_open,
            argparse.Namespace(
                title="Spend money wall",
                gate="money",
                dep=[],
                strand_id=None,
                longship_id=None,
                formula_ref=None,
                mist=False,
                kind="chore",
                priority=1,
                actor=actor,
            ),
        )
        check(code == 0 and rid_money.startswith("rc-"), "open money-gated")
        code, _out = capture(
            cmd_claim,
            argparse.Namespace(rune_id=rid_money, actor=actor, force=False),
        )
        check(code == 1, "money gate must refuse claim")
        auto_claim_next_ungated(tmp, actor)
        items, _, _ = _project_items(tmp)
        check(not items[rid_money].get("hook_owner"), "money never auto-claimed")

        code, rid_auto = capture(
            cmd_open,
            argparse.Namespace(
                title="Auto claim candidate",
                gate="none",
                dep=[],
                strand_id=None,
                longship_id=None,
                formula_ref=None,
                mist=False,
                kind="fix",
                priority=2,
                actor=actor,
            ),
        )
        check(code == 0, "open auto candidate")
        claimed = auto_claim_next_ungated(tmp, actor)
        check(claimed is not None and claimed.get("hook_owner") == actor, "auto-claim ungated")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print("SELF-TEST FAIL:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("SELF-TEST PASS: ready, claim/sling, oath-hook, human_gate, longship, strand, runes-posture, auto-claim-B")
    return 0


def _normalize_argv(argv: list[str] | None) -> list[str] | None:
    """Allow global flags after the subcommand (`rc ready --repo-root DIR`)."""
    if not argv:
        return argv
    args = list(argv)
    globals_out: list[str] = []
    rest: list[str] = []
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("--repo-root", "--actor") and i + 1 < len(args):
            globals_out.extend([a, args[i + 1]])
            i += 2
            continue
        if a == "--self-test":
            globals_out.append(a)
            i += 1
            continue
        if a.startswith("--repo-root=") or a.startswith("--actor="):
            globals_out.append(a)
            i += 1
            continue
        rest.append(a)
        i += 1
    return globals_out + rest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rc runes",
        description="Runes ready-queue (ledger projection). Longship = delivery batch.",
    )
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--actor", default=os.environ.get("RC_ACTOR", "unknown"))
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")

    p_ready = sub.add_parser("ready", help="list Verðandi (unblocked/ungated/unclaimed) Runes")
    p_ready.add_argument("--json", action="store_true")
    p_ready.add_argument("-v", "--verbose", action="store_true")
    p_ready.set_defaults(func=cmd_ready)

    p_show = sub.add_parser("show", help="show one Rune")
    p_show.add_argument("rune_id")
    p_show.add_argument("--json", action="store_true")
    p_show.set_defaults(func=cmd_show)

    p_open = sub.add_parser("open", help="mint a Rune")
    p_open.add_argument("title")
    p_open.add_argument("--dep", action="append", default=[])
    p_open.add_argument(
        "--gate",
        choices=list(HUMAN_GATES),
        default="none",
        help="human_gate wall (matthew/appsec/sage/cos never auto)",
    )
    p_open.add_argument("--strand-id", dest="strand_id")
    p_open.add_argument("--longship-id", dest="longship_id")
    p_open.add_argument("--formula-ref", dest="formula_ref")
    p_open.add_argument("--mist", action="store_true")
    p_open.add_argument("--priority", type=int, choices=[1, 2, 3, 4])
    p_open.add_argument(
        "--kind",
        choices=list(KIND_TAGS),
        default=None,
        help="optional kind TAG (fix|feature|chore) — not a hierarchy; flat Runes + strands only",
    )
    p_open.set_defaults(func=cmd_open)

    p_claim = sub.add_parser("claim", help="claim Rune onto Oath-hook")
    p_claim.add_argument("rune_id")
    p_claim.add_argument("--force", action="store_true")
    p_claim.set_defaults(func=cmd_claim)

    p_sling = sub.add_parser("sling", help="sling Rune onto Oath-hook (claim synonym)")
    p_sling.add_argument("rune_id")
    p_sling.add_argument("--force", action="store_true")
    p_sling.set_defaults(func=cmd_sling)

    p_rel = sub.add_parser("release", help="release Rune from Oath-hook")
    p_rel.add_argument("rune_id")
    p_rel.add_argument("--force", action="store_true")
    p_rel.set_defaults(func=cmd_release)

    p_hang = sub.add_parser("hanging", help="Runes hanging on an Oath-hook (GUPP)")
    p_hang.add_argument("--owner", help="hook_owner to inspect (default: --actor)")
    p_hang.add_argument("--json", action="store_true")
    p_hang.set_defaults(func=cmd_hanging)

    # strand
    p_strand = sub.add_parser("strand", help="strand (formula instance) helpers")
    strand_sub = p_strand.add_subparsers(dest="strand_cmd")
    p_sa = strand_sub.add_parser("apply", help="expand PE pack/formula → Runes")
    p_sa.add_argument("formula", help="path to PE pack / formula file")
    p_sa.add_argument("--strand-id", dest="strand_id")
    p_sa.set_defaults(func=cmd_strand_apply)

    # longship (also reachable via top-level rc longship)
    p_ls = sub.add_parser("longship", help="Longship delivery batch (Sage sole; no auto-merge)")
    ls_sub = p_ls.add_subparsers(dest="longship_cmd")
    p_lso = ls_sub.add_parser("open", help="open a Longship")
    p_lso.add_argument("--title", default="delivery")
    p_lso.add_argument("--longship-id", dest="longship_id")
    p_lso.add_argument("--force", action="store_true")
    p_lso.set_defaults(func=cmd_longship_open)
    p_lsa = ls_sub.add_parser("add", help="add Runes to a Longship")
    p_lsa.add_argument("longship_id")
    p_lsa.add_argument("rune_ids", nargs="+")
    p_lsa.set_defaults(func=cmd_longship_add)
    p_lsl = ls_sub.add_parser("land-request", help="request Sage land (never merges)")
    p_lsl.add_argument("longship_id")
    p_lsl.set_defaults(func=cmd_longship_land_request)
    p_lss = ls_sub.add_parser("show", help="show Longship doc")
    p_lss.add_argument("longship_id")
    p_lss.set_defaults(func=cmd_longship_show)

    raw = list(argv) if argv is not None else sys.argv[1:]
    args = parser.parse_args(_normalize_argv(raw))
    if args.self_test:
        return _self_test()
    if not getattr(args, "func", None):
        parser.print_help()
        return 1
    repo_root = Path(args.repo_root).resolve() if args.repo_root else L.find_repo_root()
    try:
        return args.func(repo_root, args)
    except L.LedgerUnknown as exc:
        print(f"UNKNOWN (exit 2): {exc}", file=sys.stderr)
        return 2
    except L.LedgerError as exc:
        print(f"REFUSED (exit 1): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
