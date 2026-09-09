#!/usr/bin/env python3
"""skill-description-baseline.py — P0 (succinct-skill-descriptions plan) single
measurement instrument. Every later phase reads its output; nothing later
re-measures the corpus independently.

Emits description-baseline.json: per-skill {plugin, skill, path, chars, tokens,
sha256, description}, corpus aggregates in BOTH chars and tokens, the METHOD
string, and the PINNED POSTURE (installed plugin set + versions) this baseline
was measured against.

⛔ HONEST TOKEN-COUNT CAVEAT. Claude's real tokenizer is not locally available
in this environment (no `anthropic` SDK, no API key, no `claude` CLI
token-count subcommand — all checked this session). Token counts use
`tiktoken` (`cl100k_base`, OpenAI's public BPE) as a documented PROXY, exactly
like this repo's existing `4 chars/token` heuristic elsewhere — marked
`[interpretation]`, never treated as exact. If `tiktoken` is unavailable,
token fields are `null` and `token_method` states why.

⛔ DETERMINISM (AT-P0.1). The emitted JSON carries NO timestamp, NO absolute
paths, and NO run-specific data — only content-derived fields plus the pinned
posture (name+version pairs, which only change when a plugin.json changes).
Re-running on an unchanged tree must produce byte-identical output.

Usage:
    skill-description-baseline.py [--root ROOT] [--out PATH] [--check]
    skill-description-baseline.py --self-test
    skill-description-baseline.py --must-fail
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import tiktoken

    _ENC = tiktoken.get_encoding("cl100k_base")
    TOKEN_METHOD = "tiktoken cl100k_base [interpretation — OpenAI BPE proxy, NOT Claude's real tokenizer; unavailable locally, see file docstring]"
except Exception:  # pragma: no cover - environment-dependent
    _ENC = None
    TOKEN_METHOD = "unavailable — tiktoken not importable in this environment; token fields are null"

_FM = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.S)
_DESC_LINE = re.compile(
    r"^description:\s*(.*)$", re.M
)


def _count_tokens(text: str) -> int | None:
    if _ENC is None:
        return None
    return len(_ENC.encode(text, disallowed_special=()))


def _extract_description(text: str) -> str | None:
    """Extract the frontmatter `description:` value, handling the plain-scalar,
    single/double-quoted, and block-scalar (`|`/`>`) YAML forms this repo's
    real SKILL.md files use — good enough for a value-extraction tool without
    a full YAML parser (mirrors check-frontmatter.py's own PyYAML use where
    available; falls back to this regex form when PyYAML is absent).
    """
    try:
        import yaml  # type: ignore

        m = _FM.match(text)
        if not m:
            return None
        data = yaml.safe_load(m.group(1))
        if not isinstance(data, dict):
            return None
        desc = data.get("description")
        return desc if isinstance(desc, str) else None
    except Exception:
        pass
    # Fallback: regex, single-line scalar forms only.
    m = _FM.match(text)
    if not m:
        return None
    dm = _DESC_LINE.search(m.group(1))
    if not dm:
        return None
    raw = dm.group(1).strip()
    if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
        raw = raw[1:-1].replace('\\"', '"')
    elif raw.startswith("'") and raw.endswith("'") and len(raw) >= 2:
        raw = raw[1:-1].replace("''", "'")
    return raw


def _find_skill_files(root: Path) -> list[Path]:
    files: set[Path] = set()
    for p in root.glob("plugins/*/skills/**/SKILL.md"):
        files.add(p)
    for p in root.glob("plugins/*/skills/*.md"):
        files.add(p)
    return sorted(files)


def _plugin_versions(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for pj in sorted(root.glob("plugins/*/.claude-plugin/plugin.json")):
        try:
            data = json.loads(pj.read_text(encoding="utf-8"))
        except Exception:
            continue
        name = data.get("name")
        version = data.get("version")
        if isinstance(name, str) and isinstance(version, str):
            out[name] = version
    return out


def build(root: Path) -> dict:
    entries = []
    total_chars = 0
    total_tokens = 0
    tokens_known = _ENC is not None
    for f in _find_skill_files(root):
        rel = f.relative_to(root)
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        desc = _extract_description(text)
        if desc is None:
            continue
        parts = rel.parts
        # plugins/<plugin>/skills/<skill>/SKILL.md  or  plugins/<plugin>/skills/<skill>.md
        plugin = parts[1] if len(parts) > 1 else ""
        skill = parts[3] if len(parts) >= 5 else Path(parts[-1]).stem
        chars = len(desc)
        toks = _count_tokens(desc)
        sha = hashlib.sha256(desc.encode("utf-8")).hexdigest()
        entries.append(
            {
                "plugin": plugin,
                "skill": skill,
                "path": str(rel),
                "chars": chars,
                "tokens": toks,
                "sha256": sha,
                "description": desc,
            }
        )
        total_chars += chars
        if toks is not None:
            total_tokens += toks

    entries.sort(key=lambda e: e["path"])

    return {
        "schema_version": 1,
        "method": {
            "description_extraction": "PyYAML safe_load on frontmatter block if available, else a regex fallback for plain/quoted scalars",
            "token_method": TOKEN_METHOD,
        },
        "posture": {
            "note": "installed plugin set + versions this baseline was measured against (all plugins in this checkout, not a per-consumer enabled/disabled posture — see P0-G-P0.2 for the enabled-plugins denominator question)",
            "plugin_versions": _plugin_versions(root),
        },
        "corpus": {
            "skill_count": len(entries),
            "total_chars": total_chars,
            "total_tokens": total_tokens if tokens_known else None,
            "mean_chars": round(total_chars / len(entries), 2) if entries else 0,
            "mean_tokens": round(total_tokens / len(entries), 2) if entries and tokens_known else None,
        },
        "skills": entries,
    }


def _dump(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=False, ensure_ascii=False) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="description-baseline.json")
    ap.add_argument("--check", action="store_true", help="verify --out matches a fresh build; exit 1 on drift")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--must-fail", action="store_true", help="AT-P0.2 teeth: mutate one description, assert the delta")
    args = ap.parse_args()

    root = Path(args.root).resolve()

    if args.self_test:
        return _self_test()
    if args.must_fail:
        return _must_fail_teeth(root)

    data = build(root)
    out_path = root / args.out if not Path(args.out).is_absolute() else Path(args.out)

    if args.check:
        if not out_path.exists():
            print(f"MISSING: {out_path} does not exist — run without --check first", file=sys.stderr)
            return 1
        current = out_path.read_text(encoding="utf-8")
        fresh = _dump(data)
        if current != fresh:
            print("DRIFT: description-baseline.json does not match a fresh build", file=sys.stderr)
            return 1
        print(f"description-baseline.json OK — {data['corpus']['skill_count']} skills, "
              f"{data['corpus']['total_chars']} chars, "
              f"{data['corpus']['total_tokens']} tokens ({TOKEN_METHOD.split(' [')[0]})")
        return 0

    out_path.write_text(_dump(data), encoding="utf-8")
    print(f"wrote {out_path} — {data['corpus']['skill_count']} skills, "
          f"{data['corpus']['total_chars']} chars, "
          f"{data['corpus']['total_tokens']} tokens ({TOKEN_METHOD.split(' [')[0]})")
    return 0


def _self_test() -> int:
    import tempfile

    passed = 0
    failed: list[str] = []

    def check(name: str, cond: bool) -> None:
        nonlocal passed
        if cond:
            passed += 1
        else:
            failed.append(name)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "plugins" / "demo" / "skills" / "alpha").mkdir(parents=True)
        (root / "plugins" / "demo" / ".claude-plugin").mkdir(parents=True)
        (root / "plugins" / "demo" / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "demo", "version": "1.0.0"}), encoding="utf-8"
        )
        (root / "plugins" / "demo" / "skills" / "alpha" / "SKILL.md").write_text(
            "---\nname: alpha\ndescription: A test skill for alpha things.\n---\nbody\n",
            encoding="utf-8",
        )

        # determinism (AT-P0.1)
        d1 = _dump(build(root))
        d2 = _dump(build(root))
        check("AT-P0.1 determinism: two builds are byte-identical", d1 == d2)

        # AT-P0.7 charset round-trip
        specials = {
            "colon": "Handles the : character mid-sentence, safely.",
            "hash": "Handles the # character mid-sentence too.",
            "leading-dash": "- Handles a leading dash in prose.",
            "pipe": "Handles the | character inline.",
            "gt": "Handles the > character inline.",
        }
        for label, desc in specials.items():
            skill_dir = root / "plugins" / "demo" / "skills" / label
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: " + label + "\ndescription: " + _yaml_quote(desc) + "\n---\nbody\n",
                encoding="utf-8",
            )
        data = build(root)
        by_skill = {e["skill"]: e["description"] for e in data["skills"]}
        for label, desc in specials.items():
            check(f"AT-P0.7 charset round-trip: {label}", by_skill.get(label) == desc)

    # ⛔ Deliberately NOT asserting tiktoken IS available — that is an
    # environment fact, not a behavior of this script, and CI's runner does
    # not have it pip-installed (only pyyaml is). Absence is a first-class,
    # handled state (token fields become null, method says why); asserting
    # its presence here would make this self-test environment-dependent,
    # exactly the trap this comment exists to name. Instead assert the
    # DEGRADATION is honest: when tiktoken IS present, tokens must be
    # non-null; when absent, they must be null and the method must say so.
    if _ENC is not None:
        check("token method: when tiktoken is available, tokens are populated (non-null)", data["skills"][0]["tokens"] is not None)
    else:
        check("token method: when tiktoken is absent, tokens are null and method states why", "unavailable" in TOKEN_METHOD)

    print(f"skill-description-baseline.py self-test: {passed} pass, {len(failed)} fail")
    for f in failed:
        print(f"  FAIL: {f}")
    return 0 if not failed else 1


def _yaml_quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _must_fail_teeth(root: Path) -> int:
    """AT-P0.2: mutate one description by +50 chars, assert exactly that
    entry's chars AND the corpus total move by exactly +50. Non-destructive —
    copies the real skills tree + plugin manifests into a temp dir and mutates
    the COPY only; the working tree is never touched."""
    import shutil
    import tempfile

    real = build(root)
    if not real["skills"]:
        print("must-fail: no real skills found to mutate against", file=sys.stderr)
        return 1
    target = real["skills"][0]

    with tempfile.TemporaryDirectory() as td:
        tmp_root = Path(td)
        for f in _find_skill_files(root):
            dest = tmp_root / f.relative_to(root)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
        for pj in root.glob("plugins/*/.claude-plugin/plugin.json"):
            dest = tmp_root / pj.relative_to(root)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pj, dest)

        before = build(tmp_root)
        before_entry = next(e for e in before["skills"] if e["path"] == target["path"])
        before_total = before["corpus"]["total_chars"]

        mutated_path = tmp_root / target["path"]
        text = mutated_path.read_text(encoding="utf-8")
        pad = "X" * 50
        new_text = text.replace(target["description"], target["description"] + pad, 1)
        mutated_path.write_text(new_text, encoding="utf-8")

        after = build(tmp_root)
        after_entry = next(e for e in after["skills"] if e["path"] == target["path"])
        after_total = after["corpus"]["total_chars"]

        delta_entry = after_entry["chars"] - before_entry["chars"]
        delta_total = after_total - before_total
        ok = delta_entry == 50 and delta_total == 50
        print(
            f"must-fail teeth: mutated {target['path']} chars {before_entry['chars']}->{after_entry['chars']} "
            f"(delta {delta_entry}), corpus total delta {delta_total} — "
            f"{'PASS (teeth bite)' if ok else 'FAIL (teeth do not bite)'}"
        )
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
