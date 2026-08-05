#!/usr/bin/env python3
"""check-codex-save-path.py — Gate 168 (audit MH-16 part 2, dashboard half).

Asserts that saving a comfort posture in the dashboard also reaches Codex, and —
the part that needs a machine — that it reaches it *honestly*.

THE DEFECT THIS CLOSES. `emit-codex-config.py` shipped, but it was invoked from
exactly ONE place: `scripts/ravenclaude`, the installer. Nothing on the
dashboard's save path called it, and `apply-comfort-posture.py` has no Codex
awareness at all. So a user could set every category to `deny`, click Save,
watch the dashboard report success, and still be running at Codex's default
`workspace-write`. The product's headline feature silently did nothing there.

WHY THE HONESTY HALF NEEDS A GATE, not just review. The emitter's governing rule
is NEVER SILENTLY WEAKEN: a posture looser than what is already on disk is
REFUSED. But a refusal **exits 0** (it tightened what it could and declined the
rest), so the naive wrapper reports unqualified success while some settings were
deliberately not applied. That is the same false assurance the fix removes, just
moved one layer out — so "refusals are surfaced" is asserted, with teeth.

Assertions:

  1. SKIP   — a project with no `.codex/` is left alone (no config is created).
              Writing an OS-sandbox file into every repo that ever saves a
              posture would be a surprising side effect.
  2. APPLY  — a Codex project gets the posture projected.
  3. HONEST — when the on-disk config is STRICTER than the posture, the stricter
              value survives AND the refusal is reported, not swallowed.
  4. SAFE   — the emitter never emits `danger-full-access` or
              `approval_policy = "never"`, at any posture.

Usage:
    python3 scripts/check-codex-save-path.py
    python3 scripts/check-codex-save-path.py --must-fail   # teeth self-test
"""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SERVER = REPO_ROOT / "scripts" / "serve-dashboards.py"
PLUGIN_SERVER = (
    REPO_ROOT / "plugins" / "ravenclaude-core" / "scripts" / "serve-dashboards.py"
)

_STRICT_POSTURE = textwrap.dedent(
    """\
    schema_version: 5
    categories:
      shell_remote_mutate:
        user: deny
        local: deny
        project: inherit
      file_edit_global:
        user: deny
        local: deny
        project: inherit
    """
)

_LOOSE_POSTURE = textwrap.dedent(
    """\
    schema_version: 5
    categories:
      shell_readonly:
        user: allow
        local: allow
        project: allow
      file_edit_project:
        user: allow
        local: allow
        project: allow
    """
)


def make_project(root: Path, name: str, posture: str, codex: str | None) -> Path:
    """codex=None -> not a Codex project; codex='' -> .codex/ but no config."""
    p = root / name
    (p / ".ravenclaude").mkdir(parents=True)
    (p / ".ravenclaude" / "comfort-posture.yaml").write_text(posture, encoding="utf-8")
    if codex is not None:
        (p / ".codex").mkdir()
        if codex:
            (p / ".codex" / "config.toml").write_text(codex, encoding="utf-8")
    return p


def load_server():
    """Import the ROOT server module without running main()."""
    spec = importlib.util.spec_from_file_location("_codex_save_under_test", SERVER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def call_helper(mod, project: Path, *, drop_refusal_detection: bool = False) -> dict:
    """Invoke the real _apply_codex_posture against `project`.

    The helper reads module-level constants and touches nothing else on `self`,
    so it is called unbound with the constants repointed at the fixture. That
    exercises the SHIPPED code rather than a paraphrase of it.
    """
    handler = None
    for name in dir(mod):
        obj = getattr(mod, name)
        if isinstance(obj, type) and hasattr(obj, "_apply_codex_posture"):
            handler = obj
            break
    if handler is None:
        raise SystemExit("FATAL: no handler class defines _apply_codex_posture")

    mod.PROJECT_TARGET = project
    if drop_refusal_detection:
        # THE MUTANT: report the emitter's exit code verbatim and never look for
        # a refusal — i.e. the naive wrapper. A loosening attempt then reads as a
        # clean success, which is the bug assertion 3 exists to catch.
        def naive(_self) -> dict:
            proc = subprocess.run(
                [sys.executable, str(mod.CODEX_EMITTER), "--project", str(project)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            out = ((proc.stdout or "") + (proc.stderr or "")).strip()
            return {"codex_applied": proc.returncode == 0, "codex_summary": out[:800]}

        return naive(None)
    return handler._apply_codex_posture(None)


def run(mod, *, mutate: bool = False) -> int:
    failures = 0

    def bad(msg: str) -> None:
        nonlocal failures
        failures += 1
        print(f"  FAIL: {msg}", file=sys.stderr)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        # 1 — SKIP: no .codex/ means leave the project alone entirely.
        plain = make_project(tmp, "plain", _STRICT_POSTURE, codex=None)
        res = call_helper(mod, plain, drop_refusal_detection=mutate)
        if not mutate:
            if res.get("codex_applied"):
                bad("non-Codex project: helper applied anyway (should skip)")
            if not res.get("codex_skipped"):
                bad(f"non-Codex project: no skip reason given ({res})")
        if (plain / ".codex").exists():
            bad("non-Codex project: a .codex/ directory was created — do not litter")

        # 2 — APPLY: a Codex project gets the posture projected.
        fresh = make_project(tmp, "fresh", _STRICT_POSTURE, codex="")
        res = call_helper(mod, fresh, drop_refusal_detection=mutate)
        cfg = fresh / ".codex" / "config.toml"
        if not res.get("codex_applied"):
            bad(f"Codex project: not applied ({res})")
        if not cfg.is_file() or not cfg.read_text(encoding="utf-8").strip():
            bad("Codex project: config.toml not written")
        else:
            body = cfg.read_text(encoding="utf-8")
            if "sandbox_mode" not in body:
                bad("Codex project: sandbox_mode absent from the emitted config")
            # 4 — SAFE: the two values that must never be emitted, at any posture.
            #
            # Checked against LIVE config lines only. The emitted file carries a
            # header comment that *names* both forbidden values while promising
            # never to emit them — so a naive substring scan over the whole file
            # matches the guarantee and reports it as a violation. The first draft
            # of this gate did exactly that and failed on a correct emitter.
            live = "\n".join(
                ln for ln in body.splitlines() if not ln.lstrip().startswith("#")
            )
            for forbidden in ("danger-full-access", 'approval_policy = "never"'):
                if forbidden in live:
                    bad(f"SAFETY: emitted {forbidden!r} — never permitted at any posture")

        # 3 — HONEST: on-disk stricter than posture -> survives AND is reported.
        tight = make_project(
            tmp,
            "tightened",
            _LOOSE_POSTURE,
            codex='sandbox_mode = "read-only"\napproval_policy = "untrusted"\n',
        )
        res = call_helper(mod, tight, drop_refusal_detection=mutate)
        body = (tight / ".codex" / "config.toml").read_text(encoding="utf-8")
        if "read-only" not in body:
            bad("WEAKENED: a hand-set read-only sandbox_mode was loosened")
        refusals = res.get("codex_refusals") or []
        if not refusals:
            bad(
                "SILENT PARTIAL: settings were refused but the result reports plain "
                f"success with no codex_refusals — {res.get('codex_applied')!r}"
            )

        # Both server copies must carry the helper; the plugin copy is what
        # consumers actually run, so a root-only fix would ship nothing.
        for label, path in (("root", SERVER), ("plugin", PLUGIN_SERVER)):
            if "_apply_codex_posture" not in path.read_text(encoding="utf-8"):
                bad(f"{label} serve-dashboards.py does not define _apply_codex_posture")

    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--must-fail", action="store_true")
    args = ap.parse_args()
    mod = load_server()

    if args.must_fail:
        import contextlib
        import io

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            failures = run(mod, mutate=True)
        text = err.getvalue()
        if failures == 0:
            print("MUST-FAIL: the naive wrapper produced NO failures — no teeth",
                  file=sys.stderr)
            return 1
        if "SILENT PARTIAL" not in text:
            print("MUST-FAIL: failed, but not on the silent-partial assertion — the "
                  "refusal check is not what caught it", file=sys.stderr)
            print(text, file=sys.stderr)
            return 1
        print(f"  ok: teeth — a wrapper that ignores refusals reports a loosening as "
              f"clean success, and is caught ({failures} failure(s))")
        print("Codex save path: MUST-FAIL half behaved correctly")
        return 0

    failures = run(mod)
    if failures:
        print(f"FAIL: {failures} assertion(s) failed", file=sys.stderr)
        return 1
    print("  ok: non-Codex projects are skipped (no .codex/ created)")
    print("  ok: a Codex project gets the posture projected")
    print("  ok: a stricter on-disk value survives AND the refusal is reported")
    print("  ok: danger-full-access / approval_policy=never are never emitted")
    print("Codex save path: ALL ASSERTIONS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
