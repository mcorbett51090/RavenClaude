#!/usr/bin/env python3
"""Thing harden-transform registry — apply + verify (design A+C / H3).

harden_ok(orig, rev) ≡
  registry_match(orig, rev)
  ∧ classify(rev) == classify(orig)
  ∧ ¬screen_always(rev)
  ∧ concerns(rev) ⊆ concerns(orig)
  ∧ rank(tier(rev)) < rank(gate_floor)
  ∧ rev ≠ orig

Transforms are AppSec-signed; adding one is the same bar as a catalog concern.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PLUGIN = _HERE.parent
_REGISTRY_PATH = _PLUGIN / "knowledge" / "thing-harden-transforms.yaml"

_TIER_ORDER = ("low", "medium", "high", "extreme")
_TIER_RANK = {t: i for i, t in enumerate(_TIER_ORDER)}

_SYSTEM_PATH_PREFIXES = (
    "/etc",
    "/usr",
    "/bin",
    "/sbin",
    "/boot",
    "/dev",
    "/proc",
    "/sys",
)


def registry_version(reg: dict | None = None) -> str:
    reg = reg if reg is not None else load_registry()
    return str((reg or {}).get("registry_version") or "0")


def load_registry(path: Path | None = None) -> dict:
    p = path or _REGISTRY_PATH
    text = p.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None
    if yaml is not None:
        data = yaml.safe_load(text) or {}
        if isinstance(data, dict):
            return data
    # Minimal fallback: not expected in-plugin (PyYAML available in CI/dev).
    return {"schema_version": 1, "registry_version": "1", "transforms": []}


def registry_ids(reg: dict | None = None) -> list[str]:
    reg = reg if reg is not None else load_registry()
    out = []
    for t in (reg or {}).get("transforms") or []:
        if isinstance(t, dict) and isinstance(t.get("id"), str):
            out.append(t["id"])
    return out


# ── Transform appliers ────────────────────────────────────────────────────────


def _split_argv(command: str) -> list[str] | None:
    try:
        return shlex.split(command, posix=True)
    except ValueError:
        return None


def apply_git_force_with_lease(orig: str) -> str | None:
    """git push with -f/--force (not already --force-with-lease) → --force-with-lease."""
    if not re.search(r"\bgit\b", orig, re.I):
        return None
    if not re.search(r"\bpush\b", orig, re.I):
        return None
    # Already lease?
    if re.search(r"--force-with-lease\b", orig, re.I):
        return None
    # Must have force form: --force or short -f (possibly clustered), or +refspec.
    has_long = bool(re.search(r"--force\b", orig, re.I))
    has_short = bool(re.search(r"(?<![\w-])-[A-Za-z]*f[A-Za-z]*(?:\s|$)", orig))
    has_plus = bool(re.search(r"\bgit\s+push\b[^|&;\n]*\s\+\S", orig, re.I))
    if not (has_long or has_short or has_plus):
        return None

    rev = orig
    if has_long:
        rev = re.sub(r"--force\b", "--force-with-lease", rev, count=1, flags=re.I)
    elif has_short:
        # Replace standalone -f or strip f from a cluster; prefer inserting long flag.
        def _strip_f(m: re.Match) -> str:
            flags = m.group(0)
            body = flags[1:].replace("f", "").replace("F", "")
            return f"-{body}" if body else ""

        rev2, n = re.subn(
            r"(?<![\w-])-[A-Za-z]*f[A-Za-z]*(?=\s|$)", _strip_f, rev, count=1
        )
        if n == 0:
            return None
        rev2 = re.sub(r"\s{2,}", " ", rev2).strip()
        # Insert --force-with-lease after `push`
        rev = re.sub(r"(\bpush\b)", r"\1 --force-with-lease", rev2, count=1, flags=re.I)
    elif has_plus:
        # git push origin +main → git push --force-with-lease origin main
        rev = re.sub(
            r"(\bgit\s+push\b)([^|&;\n]*)\s\+(\S+)",
            lambda m: f"{m.group(1)} --force-with-lease{m.group(2)} {m.group(3)}",
            rev,
            count=1,
            flags=re.I,
        )
    if rev == orig:
        return None
    return rev


def apply_git_clean_dry_run(orig: str) -> str | None:
    if not re.search(r"\bgit\s+clean\b", orig, re.I):
        return None
    # Already dry-run / interactive
    if re.search(r"(?<![\w-])-[A-Za-z]*n[A-Za-z]*\b|--dry-run\b|(?<![\w-])-[A-Za-z]*i[A-Za-z]*\b|--interactive\b", orig, re.I):
        return None
    # Require -fd or -fdx style (force + dirs, optional x)
    if not re.search(r"(?<![\w-])-[A-Za-z]*f[A-Za-z]*d[A-Za-z]*x?[A-Za-z]*\b", orig, re.I):
        # also allow separate -f -d
        argv = _split_argv(orig)
        if not argv:
            return None
        flags = set()
        for a in argv:
            if a.startswith("-") and not a.startswith("--"):
                flags.update(a[1:])
            elif a in ("--force",):
                flags.add("f")
            elif a in ("-d", "--directories"):
                flags.add("d")
            elif a in ("-x", "--ignored"):
                flags.add("x")
        if "f" not in flags or "d" not in flags:
            return None
    # Insert -n after `clean`
    rev = re.sub(r"(\bgit\s+clean\b)", r"\1 -n", orig, count=1, flags=re.I)
    return rev if rev != orig else None


def _curl_method(argv: list[str]) -> str:
    method = "GET"
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-X", "--request") and i + 1 < len(argv):
            method = argv[i + 1].upper()
            i += 2
            continue
        if a.startswith("-X") and len(a) > 2:
            method = a[2:].upper()
        if a.startswith("--request="):
            method = a.split("=", 1)[1].upper()
        # body flags imply POST if method still GET
        if a in (
            "-d",
            "--data",
            "--data-raw",
            "--data-binary",
            "--data-urlencode",
            "-F",
            "--form",
            "-T",
            "--upload-file",
        ) or a.startswith("--data") or a.startswith("--form"):
            if method == "GET":
                method = "POST"
        i += 1
    return method


def apply_curl_add_fail(orig: str) -> str | None:
    argv = _split_argv(orig)
    if not argv:
        return None
    # find curl token
    try:
        idx = next(i for i, a in enumerate(argv) if Path(a).name == "curl" or a == "curl")
    except StopIteration:
        return None
    if any(a in ("--fail", "--fail-with-body") or a.startswith("--fail=") for a in argv):
        return None
    method = _curl_method(argv)
    if method in ("POST", "PUT", "PATCH", "DELETE"):
        return None
    if method not in ("GET", "HEAD"):
        return None
    # Require an HTTP(S) URL somewhere
    urls = [a for a in argv if re.match(r"https?://", a, re.I)]
    if not urls:
        # curl allows -O / bare host? require explicit http(s)
        return None
    # Insert --fail immediately after curl
    new_argv = list(argv)
    new_argv.insert(idx + 1, "--fail")
    return shlex.join(new_argv)


def apply_wget_add_fail(orig: str) -> str | None:
    """v1: no wget fail-fast flag proves tier descent → no match (AppSec gated)."""
    _ = orig
    return None


_CHMOD_WORLD = re.compile(
    r"(?:"
    r"(?<![0-7])777(?![0-7])"
    r"|a\+rwx\b|a=rwx\b|ugo\+rwx\b|ugo=rwx\b"
    r"|(?:^|[,\s])a\+[rwxst]*w[rwxst]*\b"  # conservative; primary modes above
    r")"
)


def _chmod_path_ok(path: str) -> bool:
    if not path or path in ("/", "/*", "/**"):
        return False
    if any(ch in path for ch in "*?[]") and path.startswith("/"):
        # root globs
        if path == "/*" or path.startswith("/*") or path.startswith("/."):
            return False
    abs_like = path.startswith("/") or path.startswith("~")
    if abs_like:
        if path.startswith("~"):
            # treat as HOME-relative — allow
            return not any(
                path == p or path.startswith(p + "/") for p in _SYSTEM_PATH_PREFIXES
            )
        for p in _SYSTEM_PATH_PREFIXES:
            if path == p or path.startswith(p + "/"):
                return False
        # absolute under /home, /workspace, /tmp, /var/tmp, or similar — allow non-system
        return True
    # relative path — allow
    if path.startswith("../") or path == "..":
        return False
    return True


def apply_chmod_no_world_write(orig: str) -> str | None:
    argv = _split_argv(orig)
    if not argv:
        return None
    try:
        idx = next(i for i, a in enumerate(argv) if Path(a).name == "chmod" or a == "chmod")
    except StopIteration:
        return None
    recursive = False
    mode = None
    paths: list[str] = []
    i = idx + 1
    while i < len(argv):
        a = argv[i]
        if a in ("-R", "--recursive"):
            recursive = True
            i += 1
            continue
        if a.startswith("-") and not a.startswith("--") and set(a[1:]) <= set("Rf") and "R" in a:
            recursive = True
            i += 1
            continue
        if a == "--":
            paths.extend(argv[i + 1 :])
            break
        if mode is None and not a.startswith("-"):
            mode = a
            i += 1
            continue
        if mode is not None:
            paths.append(a)
        i += 1
    if mode is None or not paths:
        return None
    if not _CHMOD_WORLD.search(mode) and mode not in ("777", "0777", "a+rwx", "a=rwx", "ugo+rwx", "ugo=rwx"):
        return None
    if len(paths) != 1:
        # path-bound: single path only
        return None
    path = paths[0]
    if not _chmod_path_ok(path):
        return None
    parts = ["chmod"]
    if recursive:
        parts.append("-R")
    parts.extend(["u+rwX,go+rX", "--", path])
    return shlex.join(parts)


def apply_npm_drop_global(orig: str) -> str | None:
    argv = _split_argv(orig)
    if not argv:
        return None
    try:
        idx = next(
            i
            for i, a in enumerate(argv)
            if Path(a).name in ("npm", "pnpm", "yarn") or a in ("npm", "pnpm", "yarn")
        )
    except StopIteration:
        return None
    # Need an install-like verb
    verbs = {"install", "i", "add", "ci"}
    if not any(a in verbs for a in argv[idx + 1 :]):
        # yarn global add is a different shape
        if Path(argv[idx]).name == "yarn" or argv[idx] == "yarn":
            # yarn global add pkg
            if len(argv) > idx + 1 and argv[idx + 1] == "global":
                # drop `global`
                new_argv = list(argv)
                del new_argv[idx + 1]
                return shlex.join(new_argv) if new_argv != argv else None
        return None
    if not any(a in ("-g", "--global") for a in argv):
        return None
    new_argv = [a for a in argv if a not in ("-g", "--global")]
    return shlex.join(new_argv) if new_argv != argv else None


_APPLIERS = {
    "git-force-with-lease": apply_git_force_with_lease,
    "git-clean-dry-run": apply_git_clean_dry_run,
    "curl-add-fail": apply_curl_add_fail,
    "wget-add-fail": apply_wget_add_fail,
    "chmod-no-world-write": apply_chmod_no_world_write,
    "npm-drop-global": apply_npm_drop_global,
}


def apply_all(orig: str) -> list[tuple[str, str]]:
    """Return list of (transform_id, revised) for every matching transform."""
    out: list[tuple[str, str]] = []
    for tid, fn in _APPLIERS.items():
        try:
            rev = fn(orig)
        except Exception:
            rev = None
        if rev and rev != orig:
            out.append((tid, rev))
    return out


def apply_first(orig: str) -> tuple[str | None, str | None]:
    matches = apply_all(orig)
    if not matches:
        return None, None
    return matches[0][0], matches[0][1]


def registry_match(orig: str, rev: str) -> tuple[bool, list[str]]:
    """True iff rev equals T(orig) for at least one signed transform."""
    ids = []
    for tid, produced in apply_all(orig):
        if produced == rev:
            ids.append(tid)
    return bool(ids), ids


# ── harden_ok ─────────────────────────────────────────────────────────────────


def _import_concerns():
    import importlib.util

    path = _HERE / "thing-concerns.py"
    spec = importlib.util.spec_from_file_location("thing_concerns_mod", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _import_decision():
    import importlib.util

    path = _HERE / "thing-decision.py"
    spec = importlib.util.spec_from_file_location("thing_decision_mod", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _tier_for(command: str, category: str | None, concerns_mod, decision_mod) -> str:
    catalog = concerns_mod._load_catalog()
    ev = concerns_mod.evaluate(catalog, command, category)
    base = "medium"
    if category and hasattr(decision_mod, "_DEFAULT_CATEGORY_TIER_MAP"):
        base = decision_mod._DEFAULT_CATEGORY_TIER_MAP.get(category, "medium")
    return decision_mod._escalate_tier(base, ev.get("max_severity"))


def harden_ok(
    orig: str,
    rev: str,
    category: str | None,
    gate_floor: str,
    *,
    concerns_mod=None,
    decision_mod=None,
) -> dict:
    if concerns_mod is None:
        concerns_mod = _import_concerns()
    if decision_mod is None:
        decision_mod = _import_decision()

    result: dict = {
        "ok": False,
        "transform_ids": [],
        "reason": "",
        "registry_match": False,
        "category_equal": False,
        "screen_always_clear": False,
        "concerns_subset": False,
        "tier_descent": False,
        "tier_orig": None,
        "tier_rev": None,
        "classify_orig": None,
        "classify_rev": None,
    }

    if not rev or rev == orig:
        result["reason"] = "revision empty or identical to original"
        return result

    matched, ids = registry_match(orig, rev)
    result["registry_match"] = matched
    result["transform_ids"] = ids
    if not matched:
        result["reason"] = "revision is not a registered transform of the original"
        return result

    c_orig = decision_mod.classify(orig)
    c_rev = decision_mod.classify(rev)
    result["classify_orig"] = c_orig
    result["classify_rev"] = c_rev
    # Category equality: use classify(); if caller supplied category, also require
    # classify(rev) == classify(orig) (both may be None).
    cat_equal = c_orig == c_rev
    result["category_equal"] = cat_equal
    if not cat_equal:
        result["reason"] = f"category migrated ({c_orig!r} → {c_rev!r})"
        return result

    cat = category if category not in (None, "", "null") else c_orig

    catalog = concerns_mod._load_catalog()
    screen = concerns_mod.screen_always(catalog, rev)
    screen_clear = not screen.get("self_disable_deny") and not screen.get("hard_rule_deny")
    result["screen_always_clear"] = screen_clear
    if not screen_clear:
        result["reason"] = (
            f"revision trips screen_always "
            f"({screen.get('hard_rule_concern') or screen.get('self_disable_concern')})"
        )
        return result

    orig_ids = set(concerns_mod.evaluate(catalog, orig, cat)["concerns"])
    rev_ids = set(concerns_mod.evaluate(catalog, rev, cat)["concerns"])
    subset = rev_ids <= orig_ids
    result["concerns_subset"] = subset
    result["concerns_orig"] = sorted(orig_ids)
    result["concerns_rev"] = sorted(rev_ids)
    if not subset:
        result["reason"] = f"revision introduces new concerns: {sorted(rev_ids - orig_ids)}"
        return result

    gf = gate_floor if gate_floor in _TIER_RANK else "high"
    t_orig = _tier_for(orig, cat, concerns_mod, decision_mod)
    t_rev = _tier_for(rev, cat, concerns_mod, decision_mod)
    result["tier_orig"] = t_orig
    result["tier_rev"] = t_rev
    descent = _TIER_RANK[t_rev] < _TIER_RANK[gf]
    result["tier_descent"] = descent
    if not descent:
        result["reason"] = f"tier {t_rev} does not descend below gate_floor {gf}"
        return result

    result["ok"] = True
    result["reason"] = ""
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_v = sub.add_parser("version", help="print registry_version")
    ap_v.add_argument("--json", action="store_true")

    ap_a = sub.add_parser("apply", help="apply matching transforms to a command")
    ap_a.add_argument("command")
    ap_a.add_argument("--json", action="store_true")

    ap_h = sub.add_parser("harden", help="check harden_ok(orig, rev)")
    ap_h.add_argument("--original", required=True)
    ap_h.add_argument("--revised", required=True)
    ap_h.add_argument("--category", default=None)
    ap_h.add_argument("--gate-floor", default="high")

    args = ap.parse_args()
    if args.cmd == "version":
        reg = load_registry()
        payload = {
            "registry_version": registry_version(reg),
            "ids": registry_ids(reg),
            "path": str(_REGISTRY_PATH),
        }
        if args.json:
            json.dump(payload, sys.stdout)
            sys.stdout.write("\n")
        else:
            sys.stdout.write(payload["registry_version"] + "\n")
        return 0
    if args.cmd == "apply":
        matches = [{"id": i, "revised": r} for i, r in apply_all(args.command)]
        json.dump({"matches": matches}, sys.stdout)
        sys.stdout.write("\n")
        return 0
    # harden
    result = harden_ok(args.original, args.revised, args.category, args.gate_floor)
    json.dump(result, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
