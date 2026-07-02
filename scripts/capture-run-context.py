#!/usr/bin/env python3
"""capture-run-context.py — emit a MINIMAL, SAFE run_context bundle for a
RavenClaude scenario contribution.

Why this exists (FORGE feedback-mechanism-eval, Phase 2): a `/wrap` scenario
today carries a hand-typed `scope` guess and three context facts, but none of
the output-shaping variables that determine whether the lesson generalizes. This
bundler attaches the few that are BOTH reliable AND non-private, so `scope` can be
*derived-then-confirmed* instead of cold-guessed.

THE PRIVACY RULE (R-PRIV — the load-bearing constraint, FM2/SA2):
  Scenario files SHIP TO EVERY INSTALLER (`.repo-layout.json` packages
  `plugins/*/scenarios/**`). An environment NAME (`active_env`, `role`,
  `auth_mechanism_name`, tenant slug) is itself a sensitive token once shipped —
  and "ban env names by regex" is unenforceable (`_scrub.sh` catches secret
  *shapes*, not arbitrary slugs like `client-acme-prod`). So this bundler does
  NOT redact env-context — it STRUCTURALLY NEVER CAPTURES IT. The allowlist
  below (`SAFE_FIELDS`) is the entire universe of fields this script can emit;
  there is no code path that reads `environment-context.md` or any env/role/
  tenant/auth source. "Never-capture" beats "detect-and-ban" because the
  bundler is the only writer. An audit-gate (R-PRIV, audit-gates.sh) asserts
  this allowlist contains zero env-context fields; a mutant that adds one is
  caught.

THE FIXED SAFE ALLOWLIST (the ONLY fields this script may emit):
  - model          — the contributing session's model id ($CLAUDE_MODEL / arg)
  - plugin_versions — {plugin: version} from each plugins/*/.claude-plugin/plugin.json
  - posture_label  — a DERIVED preset label (open|default|balanced|strict|unknown),
                     NOT the raw comfort-posture.yaml. A label is not an env name.
  - capture_method — auto | degraded  (degraded => at least one source was absent)

DEFERRED (NOT captured here — separate track):
  The session-keyed fields (agents_ran, hook_denial_count) depend on per-session
  isolation, which is broken today: `CLAUDE_SESSION_ID` is unset in native hooks,
  so every session's hook-events collide into runs/unknown/ (critic SA1 / red-team
  FM1). Capturing those now would emit 8-days-of-all-sessions noise dressed as
  this-session authority — worse than omitting. They come online once session
  isolation is fixed. `agents_ran` is gated on a real per-session source and
  defaults to omitted/degraded; there is intentionally no env-var fallback that
  would read a wrong-session log.

FAIL-SAFE CONTRACT (mirrors sanitize-webfetch-body.py's purity contract):
  - deterministic given the same on-disk sources + args
  - no network calls
  - no subprocess
  - no eval / exec / dynamic import
  - stdlib only (no PyYAML — a tiny hand-rolled read for the one posture line)
  - ANY missing source => that field is OMITTED and capture_method becomes
    `degraded`. The script NEVER raises on a missing/unreadable source.

Usage:
    # Emit the run_context YAML block to stdout (for /wrap to embed).
    python3 scripts/capture-run-context.py

    # Point at a specific project root (default: git toplevel / CWD search).
    python3 scripts/capture-run-context.py --project-root /path/to/repo

    # Provide the model explicitly (else read from $CLAUDE_MODEL, else degraded).
    python3 scripts/capture-run-context.py --model claude-opus-4-8

    # Self-test: assert the allowlist has zero env fields + the bundle is well
    # formed against a temp fixture. Exit 0 = healthy, nonzero = contract broken.
    python3 scripts/capture-run-context.py --check

Exit codes:
    0 — bundle emitted (possibly degraded), or --check passed
    1 — --check failed (the allowlist/contract is broken)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# THE FIXED SAFE ALLOWLIST.
#
# This tuple is the ENTIRE universe of fields the bundler may emit. The R-PRIV
# audit-gate asserts it contains NONE of the banned env-context field names. Do
# NOT add `active_env`, `role`, `tenant`, `auth_mechanism_name`, `env`, or any
# other environment identifier here — that is the one change the gate exists to
# stop (it would ship tenant/SPN recon to every installer, irreversibly).
SAFE_FIELDS = (
    "model",
    "plugin_versions",
    "posture_label",
    "capture_method",
)

# The env-context field names that must NEVER appear in SAFE_FIELDS. Kept here
# as the single source of truth so the audit-gate and this script agree on the
# ban list. (Substring-based: `tenant` also bans `tenant_id`, etc.)
BANNED_ENV_FIELD_SUBSTRINGS = (
    "env",          # active_env, environment, env_name
    "role",
    "tenant",
    "auth",         # auth_mechanism_name
    "active_env",
    "spn",
    "credential",
)

# DEFERRED session-keyed fields — documented so a future maintainer wiring them
# in does so deliberately (gated on a real per-session source), never by accident.
DEFERRED_SESSION_FIELDS = ("agents_ran", "hook_denial_count")

# The four canonical preset labels we DERIVE the posture down to, plus the
# honest fallback. A label is a derivation, not a serialization of the raw YAML
# (FM4) — so it carries no env name and is safe to ship.
POSTURE_LABELS = ("open", "default", "balanced", "strict", "unknown")


def allowlist_has_no_env_field() -> bool:
    """The R-PRIV invariant, also assertable from the gate: no SAFE_FIELDS entry
    contains a banned env-context substring."""
    for field in SAFE_FIELDS:
        low = field.lower()
        for banned in BANNED_ENV_FIELD_SUBSTRINGS:
            if banned in low:
                return False
    return True


def find_project_root(start: Path) -> Path:
    """Walk up from `start` to the first dir containing .git/ or .claude-plugin/."""
    p = start.resolve()
    while p != p.parent:
        if (p / ".git").is_dir() or (p / ".claude-plugin").is_dir():
            return p
        p = p.parent
    return start.resolve()


def capture_model(explicit: str | None) -> str | None:
    """The contributing session's model id. --model > $CLAUDE_MODEL > None.

    No reasoning, no derivation — a plain id string. None => omitted + degraded.
    """
    if explicit:
        return explicit.strip() or None
    env = os.environ.get("CLAUDE_MODEL", "").strip()
    return env or None


def capture_plugin_versions(root: Path) -> dict[str, str] | None:
    """Read each plugins/*/.claude-plugin/plugin.json `version`.

    Returns a {plugin_name: version} dict, or None if the plugins dir is absent
    or no manifest yielded a version (=> field omitted + degraded). A single
    unreadable manifest is skipped, never fatal.
    """
    plugins_dir = root / "plugins"
    if not plugins_dir.is_dir():
        return None
    versions: dict[str, str] = {}
    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue
        manifest = plugin_dir / ".claude-plugin" / "plugin.json"
        if not manifest.is_file():
            continue
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # skip a broken manifest; never raise
        name = data.get("name") or plugin_dir.name
        version = data.get("version")
        if isinstance(name, str) and isinstance(version, str) and version:
            versions[name] = version
    return versions or None


def _read_posture_global_default(posture_path: Path) -> str | None:
    """Stdlib-only read of the single `global_default:` scalar from the posture
    YAML. We do NOT parse the whole file (no PyYAML dependency; we want exactly
    one safe scalar, never the env-bearing structure). Returns the raw level
    string (e.g. 'allow'/'ask'/'deny') or None.
    """
    try:
        text = posture_path.read_text(encoding="utf-8")
    except OSError:
        return None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line or (len(line) - len(line.lstrip())) != 0:
            continue  # only a top-level (zero-indent) key counts
        if line.lstrip().startswith("global_default:"):
            _, _, val = line.partition(":")
            return val.strip().strip("'\"") or None
    return None


def derive_posture_label(root: Path) -> str:
    """DERIVE a coarse preset label from the posture's global_default.

    This is a label, NOT the raw YAML (FM4): open|default|balanced|strict|unknown.
    Absent posture file / unrecognized value => 'unknown' (honest, not a crash).

    Mapping rationale (the three-level canonical vocabulary from
    apply-comfort-posture.py: allow/ask/deny):
      allow  -> open     (categories run without prompting)
      ask    -> balanced (the seeded "balanced" preset's global default)
      deny   -> strict   (locked down by default)
      (none) -> unknown
    Legacy 5-level names collapse the same way the engine collapses them.
    """
    posture_path = root / ".ravenclaude" / "comfort-posture.yaml"
    if not posture_path.is_file():
        return "unknown"
    level = _read_posture_global_default(posture_path)
    if level is None:
        return "unknown"
    level = level.lower()
    if level in ("allow", "mostly-allow", "autopilot"):
        return "open"
    if level in ("ask", "always-ask", "mostly-ask"):
        return "balanced"
    if level == "deny":
        return "strict"
    if level == "default":
        return "default"
    return "unknown"


def build_bundle(root: Path, model_arg: str | None) -> dict:
    """Assemble the run_context bundle from ONLY the safe allowlist sources.

    Any absent source => its field is omitted and capture_method='degraded'.
    There is NO code path here that reads environment-context.md or any
    env/role/tenant/auth source — that exclusion is structural (R-PRIV).
    """
    bundle: dict = {}
    degraded = False

    model = capture_model(model_arg)
    if model is not None:
        bundle["model"] = model
    else:
        degraded = True

    versions = capture_plugin_versions(root)
    if versions is not None:
        bundle["plugin_versions"] = versions
    else:
        degraded = True

    label = derive_posture_label(root)
    bundle["posture_label"] = label  # always present (degrades to 'unknown')
    if label == "unknown":
        degraded = True

    bundle["capture_method"] = "degraded" if degraded else "auto"

    # Final defensive guard: emit ONLY allowlisted keys. Even if a future edit
    # accidentally set a non-safe key above, it cannot leave this function.
    return {k: v for k, v in bundle.items() if k in SAFE_FIELDS}


def _yaml_scalar(v) -> str:
    """Serialize a scalar as a YAML value, quoting ONLY when the plain form would be
    ambiguous or invalid — a leading indicator char, an embedded ': ' or ' #', a
    newline/CR/tab, or surrounding whitespace. Safe values (a model id, a semver)
    render unquoted exactly as before, so this adds no output churn."""
    s = str(v)
    needs_quote = (
        s == ""
        or s != s.strip()
        or s[:1] in "!&*?|>@`\"'%#-[]{},:"
        or ": " in s
        or " #" in s
        or any(c in s for c in "\n\r\t")
    )
    if not needs_quote:
        return s
    esc = (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
    return f'"{esc}"'


def render_yaml(bundle: dict) -> str:
    """Render the bundle as a `run_context:` YAML block (stdlib only — the shape
    is tiny and fixed, so we don't need PyYAML to serialize it)."""
    lines = ["run_context:"]
    if "model" in bundle:
        lines.append(f"  model: {_yaml_scalar(bundle['model'])}")
    if "plugin_versions" in bundle:
        lines.append("  plugin_versions:")
        for name in sorted(bundle["plugin_versions"]):
            lines.append(f"    {_yaml_scalar(name)}: {_yaml_scalar(bundle['plugin_versions'][name])}")
    if "posture_label" in bundle:
        lines.append(f"  posture_label: {_yaml_scalar(bundle['posture_label'])}")
    if "capture_method" in bundle:
        lines.append(f"  capture_method: {_yaml_scalar(bundle['capture_method'])}")
    return "\n".join(lines) + "\n"


def run_check() -> int:
    """Self-test: assert the R-PRIV allowlist invariant + a degraded-mode and a
    populated-mode bundle are both well formed against a temp fixture. Returns 0
    if healthy, 1 if the contract is broken.
    """
    import tempfile

    ok = True

    # 1. The R-PRIV invariant: the allowlist has zero env-context fields.
    if not allowlist_has_no_env_field():
        print("CHECK FAIL: SAFE_FIELDS contains a banned env-context field", file=sys.stderr)
        ok = False
    else:
        print("CHECK ok: allowlist has zero env-context fields", file=sys.stderr)

    # 2. No deferred session field has leaked into the allowlist.
    for f in DEFERRED_SESSION_FIELDS:
        if f in SAFE_FIELDS:
            print(f"CHECK FAIL: deferred session field {f!r} is in SAFE_FIELDS", file=sys.stderr)
            ok = False

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        # 3a. Fully-absent sources => degraded, posture_label unknown, never raises.
        b = build_bundle(root, model_arg=None)
        if b.get("capture_method") != "degraded":
            print("CHECK FAIL: empty fixture should be degraded", file=sys.stderr)
            ok = False
        if b.get("posture_label") != "unknown":
            print("CHECK FAIL: empty fixture posture_label should be unknown", file=sys.stderr)
            ok = False
        if set(b) - set(SAFE_FIELDS):
            print(f"CHECK FAIL: bundle emitted non-allowlisted keys: {set(b) - set(SAFE_FIELDS)}", file=sys.stderr)
            ok = False

        # 3b. Populated sources => auto, real values, only safe keys.
        (root / "plugins" / "demo-plugin" / ".claude-plugin").mkdir(parents=True)
        (root / "plugins" / "demo-plugin" / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "demo-plugin", "version": "1.2.3"}), encoding="utf-8"
        )
        (root / ".ravenclaude").mkdir(parents=True)
        (root / ".ravenclaude" / "comfort-posture.yaml").write_text(
            "schema_version: 5\nglobal_default: ask\n", encoding="utf-8"
        )
        b2 = build_bundle(root, model_arg="claude-opus-4-8")
        if b2.get("capture_method") != "auto":
            print("CHECK FAIL: populated fixture should be auto, not degraded", file=sys.stderr)
            ok = False
        if b2.get("model") != "claude-opus-4-8":
            print("CHECK FAIL: model not captured", file=sys.stderr)
            ok = False
        if b2.get("plugin_versions", {}).get("demo-plugin") != "1.2.3":
            print("CHECK FAIL: plugin_versions not captured", file=sys.stderr)
            ok = False
        if b2.get("posture_label") != "balanced":
            print(f"CHECK FAIL: posture_label should derive to 'balanced', got {b2.get('posture_label')!r}", file=sys.stderr)
            ok = False
        if set(b2) - set(SAFE_FIELDS):
            print(f"CHECK FAIL: populated bundle emitted non-allowlisted keys: {set(b2) - set(SAFE_FIELDS)}", file=sys.stderr)
            ok = False

        # 3c. render_yaml never emits a banned env field name.
        block = render_yaml(b2)
        for banned in BANNED_ENV_FIELD_SUBSTRINGS:
            if f"{banned}:" in block.lower() or f"  {banned}" in block.lower():
                print(f"CHECK FAIL: rendered block contains banned token {banned!r}:\n{block}", file=sys.stderr)
                ok = False

    if ok:
        print("CHECK PASS: capture-run-context contract healthy", file=sys.stderr)
        return 0
    return 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Emit a minimal, safe run_context YAML block for a scenario contribution.",
    )
    parser.add_argument("--project-root", help="Project root (default: git toplevel / search up from CWD).")
    parser.add_argument("--model", help="Model id to record (else $CLAUDE_MODEL, else degraded).")
    parser.add_argument("--check", action="store_true", help="Run the self-test and exit.")
    args = parser.parse_args(argv)

    if args.check:
        return run_check()

    root = Path(args.project_root) if args.project_root else find_project_root(Path.cwd())
    bundle = build_bundle(root, model_arg=args.model)
    sys.stdout.write(render_yaml(bundle))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
