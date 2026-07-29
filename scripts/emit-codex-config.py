#!/usr/bin/env python3
"""emit-codex-config.py — project the comfort posture onto Codex's OS sandbox.

MH-16 part 2. Until this existed, the dashboard's headline product (posture
editing) moved NOTHING on a Codex machine: `apply-comfort-posture.py` emits only
`.claude/settings.json` permission rules, and Codex does not read those. A user
could set every category to `deny`, save, and their Codex session would still be
running at the default `workspace-write`.

WHAT THIS IS NOT: a claim that the posture now bounds Codex the way it bounds
Claude Code. It does not, and the mapping says so out loud — a 12-category matrix
does not have 12 degrees of freedom against two enum keys. This is a coarse,
honest projection onto the two controls Codex actually has.

--------------------------------------------------------------------------------
THE GOVERNING RULE (owner decision, 2026-07-28): NEVER SILENTLY WEAKEN.
--------------------------------------------------------------------------------
  * absent key        -> write it
  * posture STRICTER  -> tighten it
  * posture LOOSER    -> REFUSE, and print the exact line to change by hand

Rationale: the failure direction is always toward safety, and a tightening is
trivially reversible. The alternative — mirroring the posture in both directions —
would let a saved dashboard click silently widen a sandbox somebody had
deliberately locked down, with no warning to the person who locked it.

`danger-full-access` and `approval_policy = "never"` are NEVER emitted, at any
posture. There is no posture that means "turn the OS boundary off"; if somebody
wants that they can type it themselves and own it.

--------------------------------------------------------------------------------
VERIFIED CONTRACT `[docs-verified 2026-07-28 — learn.chatgpt.com/docs/config-file/config-reference]`
--------------------------------------------------------------------------------
  * `sandbox_mode` and `approval_policy` are TOP-LEVEL keys (not under a table).
  * `sandbox_mode`    : "read-only" | "workspace-write" | "danger-full-access"
  * `approval_policy` : "untrusted" | "on-request" | "never" | granular object
  * `[sandbox_workspace_write]` carries `network_access`, `writable_roots`,
    `exclude_slash_tmp`, `exclude_tmpdir_env_var`.
  * Project config lives at `<project>/.codex/config.toml` and layers OVER
    `~/.codex/config.toml` — but **loads only in TRUSTED projects**, and cannot
    override `profile`/`profiles`/auth/provider/telemetry keys.

THE TRUST CAVEAT IS LOAD-BEARING and is printed to the user: like MH-17's
hash-trusted hooks, an emitted project config that Codex has not been told to
trust does nothing. Writing a file is not the same as bounding a session, and
this tool must never imply otherwise.

--------------------------------------------------------------------------------
WHY A HAND-ROLLED TOML READER, AND WHY IT REFUSES INSTEAD OF GUESSING
--------------------------------------------------------------------------------
`tomllib` is stdlib only on Python 3.11+; stock macOS ships 3.9, and this repo has
spent a whole release on stock-macOS portability (the bash-3.2 / timeout / grep -P
doors). So reading uses a deliberately tiny line scanner that understands exactly
one shape: `key = "value"` at a known table context.

Anything it cannot confidently parse — the key present with a non-simple value, a
duplicate, a multi-line string — makes it REFUSE and report, never assume. A
sandbox config is the wrong place to be clever: a misparse here silently weakens
an OS boundary, which is precisely the failure this whole audit exists to close.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ── strictness ladders ──────────────────────────────────────────────────────
# Higher rank == stricter. The never-weaken rule is a rank comparison, so these
# orderings ARE the security policy; changing one changes what can be loosened.
SANDBOX_RANK = {"danger-full-access": 0, "workspace-write": 1, "read-only": 2}
APPROVAL_RANK = {"never": 0, "on-request": 1, "untrusted": 2}
# network_access: False is stricter than True.
NETWORK_RANK = {"true": 0, "false": 1}

# Never emitted, at any posture. Present so the refusal is explicit in code, not
# merely an emergent property of the mapping table.
NEVER_EMIT = {"sandbox_mode": {"danger-full-access"}, "approval_policy": {"never"}}

# Keys whose TOML value is a BOOLEAN, not a string. This distinction is
# load-bearing: `network_access = "false"` is a TOML *string*, and a quoted
# "false" is not the boolean Codex expects. The bug shipped first in the TIGHTEN
# path specifically — i.e. the security-relevant direction produced the broken
# value — so the renderer is type-aware rather than assuming everything quotes.
BOOL_KEYS = {"network_access"}


def render_value(key: str, val: str) -> str:
    return val if key in BOOL_KEYS else f'"{val}"'


_SIMPLE_KV = re.compile(r'^\s*([A-Za-z0-9_-]+)\s*=\s*(.+?)\s*$')
_TABLE = re.compile(r'^\s*\[([^\]]+)\]\s*$')
_LEVEL = re.compile(r'^\s*(user|local|project)\s*:\s*([A-Za-z]+)\s*$')


class Refuse(Exception):
    """Raised when the safe action is to change nothing and tell the human."""


# ── posture reading ─────────────────────────────────────────────────────────
def read_posture_categories(path: Path) -> dict:
    """Minimal reader for the `categories:` block of comfort-posture.yaml.

    Deliberately NOT PyYAML: apply-comfort-posture.py already ships a fallback
    parser precisely because a consumer environment may not have PyYAML, and this
    tool runs in the same environments.

    Returns {category: effective_level}, where effective_level is the STRICTEST
    non-`inherit` level across the user/local/project layers.

    ON THE STRICTEST-WINS CHOICE — this is a deliberate simplification and is NOT
    a faithful reproduction of the permission engine's layering. It is chosen
    because this output configures an OS SANDBOX: taking the strictest layer is
    the only aggregation that cannot produce a too-permissive boundary. A faithful
    layering could, and the failure would be silent.
    """
    if not path.is_file():
        return {}
    order = {"allow": 0, "ask": 1, "deny": 2}
    out: dict = {}
    in_cats = False
    current = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")):
            in_cats = line.strip() == "categories:"
            current = None
            continue
        if not in_cats:
            continue
        stripped = line.strip()
        if stripped.endswith(":") and ":" not in stripped[:-1]:
            current = stripped[:-1]
            continue
        m = _LEVEL.match(line)
        if m and current:
            level = m.group(2).lower()
            if level == "inherit":
                continue
            if level not in order:
                continue
            prev = out.get(current)
            if prev is None or order[level] > order[prev]:
                out[current] = level
    return out


def map_posture(cats: dict) -> dict:
    """Comfort-posture categories -> the three Codex keys we manage.

    COARSE BY CONSTRUCTION, and the installer/docs say so. Two enum keys cannot
    express twelve categories; pretending otherwise would be the same false
    assurance the Pipeline tab used to give (MH-04).

    The question each key answers:
      sandbox_mode    -- may the agent write outside a read-only view at all?
      approval_policy -- must it ask before anything that can mutate?
      network_access  -- may sandboxed commands reach the network?
    """
    def allowed(name: str) -> bool:
        # Absent == not opted in. A category nobody configured must never be read
        # as permission; that assumption is how "everywhere" defaults happen.
        return cats.get(name) == "allow"

    writes_locally = any(
        allowed(c) for c in ("file_edit_project", "shell_local_mutate", "shell_code_exec")
    )
    # Outbound/global reach never buys more than workspace-write here. There is no
    # posture that maps to danger-full-access.
    net = allowed("network_write")

    if writes_locally:
        return {
            "sandbox_mode": "workspace-write",
            "approval_policy": "on-request",
            "network_access": "true" if net else "false",
        }
    return {
        "sandbox_mode": "read-only",
        "approval_policy": "untrusted",
        "network_access": "false",
    }


# ── the tiny, refuse-on-ambiguity TOML scanner ──────────────────────────────
def scan_toml(text: str) -> dict:
    """Return {(table, key): (value, lineno)} for SIMPLE quoted/bare scalars only.

    `table` is "" for the root. A key whose value we cannot confidently read is
    recorded with value None, which forces a refusal upstream rather than a guess.
    """
    found: dict = {}
    table = ""
    for i, raw in enumerate(text.splitlines()):
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        m = _TABLE.match(line)
        if m:
            table = m.group(1).strip()
            continue
        m = _SIMPLE_KV.match(line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val.startswith('"""') or val.startswith("'''") or val.endswith("\\"):
            found[(table, key)] = (None, i)  # multi-line / continuation: refuse
            continue
        if len(val) >= 2 and val[0] in "\"'" and val[-1] == val[0]:
            found[(table, key)] = (val[1:-1], i)
        elif val in ("true", "false"):
            found[(table, key)] = (val, i)
        else:
            found[(table, key)] = (None, i)  # array/table/number: not ours to touch
    return found


def decide(key: str, table: str, want: str, existing: dict, ranks: dict) -> tuple:
    """Return (action, detail). action ∈ skip-absent-ok | write | tighten | refuse."""
    if want in NEVER_EMIT.get(key, set()):
        raise Refuse(f"refusing to emit {key} = {want!r} — never emitted at any posture")
    cur = existing.get((table, key))
    if cur is None:
        return ("write", None)
    val, lineno = cur
    if val is None:
        raise Refuse(
            f"{key} exists at line {lineno + 1} in a form this tool will not parse. "
            f"Set it by hand to {want!r} if that is what you want."
        )
    if val == want:
        return ("skip-absent-ok", None)
    cur_rank = ranks.get(val)
    if cur_rank is None:
        raise Refuse(
            f"{key} is currently {val!r}, which is not a value this tool recognises "
            f"(line {lineno + 1}). Leaving it alone."
        )
    if ranks[want] >= cur_rank:
        return ("tighten", (val, lineno))
    return ("refuse-loosen", (val, lineno))


MANAGED_HEADER = (
    "# ── RavenClaude: projected from .ravenclaude/comfort-posture.yaml ──\n"
    "# Managed by `ravenclaude install --host codex`. Re-run it to refresh.\n"
    "# This tool NEVER weakens an existing value and never emits\n"
    "# danger-full-access or approval_policy = \"never\".\n"
    "# NOTE: a project-scoped .codex/config.toml loads only in TRUSTED projects.\n"
)


def emit(project: Path, dry_run: bool = False) -> int:
    posture = project / ".ravenclaude" / "comfort-posture.yaml"
    cfg_path = project / ".codex" / "config.toml"
    cats = read_posture_categories(posture)
    if not cats:
        print(f"  no categories in {posture} — nothing to project", file=sys.stderr)
        return 0
    want = map_posture(cats)

    text = cfg_path.read_text(encoding="utf-8") if cfg_path.is_file() else ""
    existing = scan_toml(text)

    plan = []
    refusals = []
    for key, table, ranks in (
        ("sandbox_mode", "", SANDBOX_RANK),
        ("approval_policy", "", APPROVAL_RANK),
        ("network_access", "sandbox_workspace_write", NETWORK_RANK),
    ):
        try:
            action, detail = decide(key, table, want[key], existing, ranks)
        except Refuse as exc:
            refusals.append(str(exc))
            continue
        if action == "refuse-loosen":
            cur, lineno = detail
            refusals.append(
                f"refusing to loosen {key}: {cur!r} -> {want[key]!r}\n"
                f"    your .codex/config.toml (line {lineno + 1}) is STRICTER than the "
                f"saved posture.\n    change it by hand if that is what you want."
            )
        elif action in ("write", "tighten"):
            plan.append((key, table, want[key], action, detail))

    for key, _table, val, action, detail in plan:
        if action == "tighten":
            print(f"  ✓ tightened {key} -> \"{val}\" (was \"{detail[0]}\")")
        else:
            print(f"  ✓ set {key} -> \"{val}\"")
    for r in refusals:
        print(f"  ! {r}", file=sys.stderr)
    if not plan and not refusals:
        print("  codex sandbox config already matches the posture")
        return 0
    if dry_run:
        return 0
    if not plan:
        return 0

    lines = text.splitlines()
    # Tightenings are in-place line rewrites; new keys append into a managed block.
    for key, _table, val, action, detail in plan:
        if action == "tighten":
            lines[detail[1]] = f"{key} = {render_value(key, val)}"
    appended_root = [
        f"{key} = {render_value(key, val)}" for key, table, val, action, _ in plan
        if action == "write" and table == ""
    ]
    appended_nested = [
        (render_value(key, val), key) for key, table, val, action, _ in plan
        if action == "write" and table == "sandbox_workspace_write"
    ]
    # ROOT-LEVEL KEYS MUST GO ABOVE THE FIRST TABLE HEADER.
    #
    # In TOML every key belongs to the most recent [table]. Appending
    # `sandbox_mode = "read-only"` to the END of a file that contains
    # `[mcp_servers.github]` does not set a top-level key — it sets
    # `mcp_servers.github.sandbox_mode`, which is valid TOML, silently wrong, and
    # looks perfectly correct in a diff. Codex would read no sandbox_mode at all
    # and fall back to its default, i.e. the tool would report success while
    # bounding nothing. Caught in testing against a realistic config; the anchor
    # below is the fix.
    if appended_root:
        anchor = next(
            (i for i, ln in enumerate(lines) if _TABLE.match(ln.split("#", 1)[0].rstrip())),
            len(lines),
        )
        block = MANAGED_HEADER.rstrip("\n").splitlines() + appended_root
        if anchor < len(lines):
            block.append("")
            lines[anchor:anchor] = block
        else:
            if lines and lines[-1].strip():
                lines.append("")
            lines.extend(block)
    if appended_nested:
        if lines and lines[-1].strip():
            lines.append("")
        if ("sandbox_workspace_write", "network_access") not in existing:
            lines.append("[sandbox_workspace_write]")
        for val, key in appended_nested:
            lines.append(f"{key} = {val}")
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    return 0


_POSTURE_WRITES = """schema_version: 5
categories:
  file_read_project:
    project: allow
  file_edit_project:
    project: allow
  shell_local_mutate:
    project: allow
  network_write:
    project: ask
"""

_POSTURE_READS_ONLY = """schema_version: 5
categories:
  file_read_project:
    project: allow
  file_edit_project:
    project: deny
  shell_local_mutate:
    project: deny
  shell_code_exec:
    project: deny
"""

_POSTURE_LAYER_CONFLICT = """schema_version: 5
categories:
  file_edit_project:
    user: allow
    local: inherit
    project: deny
"""


def self_test() -> int:
    """Fixture-free self-test. Every case below is one that bit, or would have."""
    import tempfile

    fails = []

    def check(name, cond):
        print(("  ok   " if cond else "  FAIL ") + name)
        if not cond:
            fails.append(name)

    def setup(posture, existing=None):
        d = Path(tempfile.mkdtemp())
        (d / ".ravenclaude").mkdir()
        (d / ".ravenclaude" / "comfort-posture.yaml").write_text(posture)
        if existing is not None:
            (d / ".codex").mkdir()
            (d / ".codex" / "config.toml").write_text(existing)
        return d

    def cfg(d):
        p = d / ".codex" / "config.toml"
        return p.read_text() if p.is_file() else ""

    # 1. write-capable posture -> workspace-write, never more.
    d = setup(_POSTURE_WRITES)
    emit(d)
    t = cfg(d)
    check("writes posture -> workspace-write", 'sandbox_mode = "workspace-write"' in t)
    check("writes posture -> on-request", 'approval_policy = "on-request"' in t)
    check("network stays off unless network_write allowed", "network_access = false" in t)

    # 2. THE GOVERNING RULE: never silently weaken.
    d = setup(_POSTURE_WRITES, 'sandbox_mode = "read-only"\napproval_policy = "untrusted"\n')
    emit(d)
    t = cfg(d)
    check("never-weaken: stricter sandbox_mode preserved", 'sandbox_mode = "read-only"' in t)
    check("never-weaken: workspace-write NOT written", 'sandbox_mode = "workspace-write"' not in t)
    check("never-weaken: stricter approval_policy preserved", 'approval_policy = "untrusted"' in t)

    # 3. Tightening IS allowed — the rule is one-directional, not inert.
    d = setup(_POSTURE_READS_ONLY, 'sandbox_mode = "workspace-write"\n')
    emit(d)
    t = cfg(d)
    check("tighten: workspace-write -> read-only", 'sandbox_mode = "read-only"' in t)

    # 4. THE BUG THIS CAUGHT: a root key appended after a [table] silently becomes
    #    a member of that table. Valid TOML, wrong meaning, invisible in a diff.
    d = setup(_POSTURE_WRITES, '[mcp_servers.github]\ncommand = "gh-mcp"\n')
    emit(d)
    lines = cfg(d).splitlines()
    first_table = next((i for i, l in enumerate(lines) if l.startswith("[")), len(lines))
    sm = next((i for i, l in enumerate(lines) if l.startswith("sandbox_mode")), -1)
    ap_i = next((i for i, l in enumerate(lines) if l.startswith("approval_policy")), -1)
    check("root keys land ABOVE the first table", 0 <= sm < first_table and 0 <= ap_i < first_table)
    check("user's own table is preserved", 'command = "gh-mcp"' in cfg(d))

    # 4b. TYPE-AWARENESS. network_access is a TOML boolean; writing it quoted
    #     produces the STRING "false", which is not the boolean Codex expects.
    #     This shipped broken first in the TIGHTEN path — the security-relevant
    #     direction — so both paths are asserted, unquoted, in both directions.
    d = setup(
        "schema_version: 5\ncategories:\n  file_edit_project:\n    project: allow\n"
        "  network_write:\n    project: deny\n",
        "[sandbox_workspace_write]\nnetwork_access = true\n",
    )
    emit(d)
    t = cfg(d)
    check("tightened boolean is unquoted", "network_access = false" in t)
    check("tightened boolean is NOT a string", 'network_access = "false"' not in t)
    d = setup(_POSTURE_WRITES)
    emit(d)
    check("appended boolean is unquoted", 'network_access = "' not in cfg(d))

    # 5. Never emit the escape hatches, at any posture.
    check("danger-full-access is never emitted", "danger-full-access" in NEVER_EMIT["sandbox_mode"])
    check("approval_policy=never is never emitted", "never" in NEVER_EMIT["approval_policy"])
    all_texts = cfg(d)
    check("no danger-full-access in output", "danger-full-access" not in all_texts.replace(MANAGED_HEADER, ""))

    # 6. Idempotent — a second run must change nothing.
    d = setup(_POSTURE_WRITES)
    emit(d)
    once = cfg(d)
    emit(d)
    check("idempotent across re-runs", cfg(d) == once)

    # 7. Layer aggregation takes the STRICTEST, so a permissive user layer can
    #    never widen the sandbox past a locked-down project layer.
    cats = read_posture_categories(
        setup(_POSTURE_LAYER_CONFLICT) / ".ravenclaude" / "comfort-posture.yaml"
    )
    check("strictest layer wins (deny beats allow)", cats.get("file_edit_project") == "deny")

    # 8. Refuse rather than guess on a value shape we do not understand.
    d = setup(_POSTURE_WRITES, "sandbox_mode = { granular = 1 }\n")
    emit(d)
    check("unparseable existing value is left alone", "granular" in cfg(d))

    print(f"\n  {len(fails)} failure(s)")
    return 1 if fails else 0


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv[1:])
    if args.self_test:
        return self_test()
    if not args.project:
        ap.error("--project is required (or use --self-test)")
    try:
        return emit(Path(args.project).resolve(), dry_run=args.dry_run)
    except Refuse as exc:
        print(f"  ! {exc}", file=sys.stderr)
        return 0  # never fail the install; refusing IS the safe outcome


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
