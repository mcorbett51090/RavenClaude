#!/usr/bin/env python3
"""check-vscode-extension-config-defaults.py — the RT-3/RT-4 gate for vscode-extension/.

WHY THIS EXISTS
----------------
`plugins/ravenclaude-core/vscode-extension/package.json` contributes a
`configurationDefaults` override for a setting it does not own
(`github.copilot.chat.summarizeAgentConversationHistoryThreshold`, owned by the
`GitHub.copilot-chat` extension). VS Code's own handler for this contribution point
is a DESIGNED-IN SILENT NO-OP on three distinct failure shapes:

  1. the key is not registered by any extension at all (a typo, or an upstream rename)
  2. the owning extension marks the property `disallowConfigurationDefault: true`
  3. the owning extension's property has a `scope` outside the small overridable set
     VS Code allows a `configurationDefaults` contribution to touch

None of these produce an error, a warning surfaced anywhere a human or CI would see,
or a non-zero exit from anything. The contribution is silently dropped and Copilot
Chat reverts to its broken default (compact only when the window is already full) —
which is the exact symptom this whole feature exists to prevent. See the
FORGE red-team finding RT-3 / RT-4 in
`.ravenclaude/runs/forge/copilot-preemptive-compact/red-team.md` for the full
shipping-code trace this check's assertions are derived from.

Before this gate, the repo had ZERO coverage of this file: it is not in CI's
`python3 -m json.tool` glob (that covers `plugins/*/.claude-plugin/plugin.json`
only), no workflow or test references `vscode-extension` at all, and prettier only
catches a JSON *syntax* error — a typo'd key, a stringified `"0.8"` instead of the
number `0.8`, or a value outside the documented `(0, 1]` range all pass every
existing gate green.

WHAT THIS CHECKS
----------------
For every key in our `contributes.configurationDefaults` block, against the
BUNDLED `GitHub.copilot-chat` extension's own `package.json` on this machine:

  1. the key exists in copilot-chat's `contributes.configuration` properties
  2. that property does NOT carry `disallowConfigurationDefault: true`
  3. that property's `scope` (if present) is in the allowed set VS Code's own
     handler permits for a configurationDefaults override — window / resource /
     language-overridable / machine-overridable, or absent (undefined defaults to
     an overridable scope). `application` and `machine` are NOT in that set.
  4. our contributed value is a number in the documented (0, 1] range (this
     setting's own doc string: "a value greater than 0 and at most 1")

WHAT THIS DOES NOT CHECK (honest limit, matching the repo's own convention)
----------------------------------------------------------------------------
This is a STATIC, point-in-time check against whatever VS Code + Copilot Chat build
happens to be installed on the machine running it. It cannot prove the contribution
will keep working after a future Copilot Chat auto-update that renames or
re-scopes the property — only that it works NOW, against what's installed NOW. Re-run
this after any Copilot Chat update if you want fresh assurance.

FAIL-SAFE: NO VS CODE ON THIS MACHINE -> LOUD-SKIP, NEVER A SILENT PASS
-------------------------------------------------------------------------
A skip is not a pass (this repo's own recorded rule, e.g. Gate 10's actionlint
skip). If neither VS Code nor the bundled Copilot Chat extension can be located,
this script prints "THIS IS NOT A PASS — <reason>" and exits 0 — in EVERY mode,
including --check. This is deliberately unlike Gate 10 (which downloads a small
pinned binary, so CI genuinely has it): VS Code is a multi-GB desktop
application CI cannot and should not provision, so this check WILL loud-skip in
CI, always, by design. What CI actually verifies is the CHECKER'S LOGIC — the
--self-test and --must-fail modes build entirely synthetic fixture trees and
need no real VS Code at all, so they run (and must pass) everywhere, including
CI. The live check against a real installed VS Code + Copilot Chat is a
machine-local confirmation only a developer's own machine can give.

Usage:
    check-vscode-extension-config-defaults.py [--vscode-app PATH]
    check-vscode-extension-config-defaults.py --check [--vscode-app PATH]
    check-vscode-extension-config-defaults.py --must-fail [--vscode-app PATH]
    check-vscode-extension-config-defaults.py --self-test
"""

from __future__ import annotations

import argparse
import glob
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUR_MANIFEST = ROOT / "plugins" / "ravenclaude-core" / "vscode-extension" / "package.json"

# The set of scopes VS Code's own handler permits a configurationDefaults override to
# touch (workbench.desktop.main.js, doRegisterDefaultConfigurations: `n=[7,4,5,6]`,
# read against ConfigurationScope's real enum). `application`(1) and `machine`(2) are
# excluded on purpose -- those are the two a maintainer "tidying up" an unscoped
# property is most likely to reach for (RT-4's own trigger scenario).
_ALLOWED_SCOPES = {"window", "resource", "language-overridable", "machine-overridable"}

_DEFAULT_VSCODE_APP_CANDIDATES = [
    "/Applications/Visual Studio Code.app",
    str(Path.home() / "Applications" / "Visual Studio Code.app"),
]


def _find_copilot_chat_manifest(vscode_app: str | None) -> Path | None:
    """Locate the bundled GitHub.copilot-chat package.json. Returns None if absent."""
    candidates = [vscode_app] if vscode_app else _DEFAULT_VSCODE_APP_CANDIDATES
    for app in candidates:
        if not app:
            continue
        base = Path(app) / "Contents" / "Resources" / "app" / "extensions" / "copilot"
        manifest = base / "package.json"
        if manifest.is_file():
            return manifest
    # Fallback: a Linux/user-install layout under ~/.vscode/extensions.
    for pattern in (
        str(Path.home() / ".vscode" / "extensions" / "github.copilot-chat-*" / "package.json"),
        str(Path.home() / ".vscode-server" / "extensions" / "github.copilot-chat-*" / "package.json"),
    ):
        hits = sorted(glob.glob(pattern))
        if hits:
            return Path(hits[-1])
    return None


def _load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _properties_from(manifest: dict) -> dict:
    """Flatten every `contributes.configuration[.properties]` entry into one dict,
    handling both the single-object and list-of-objects manifest shapes."""
    cfg = manifest.get("contributes", {}).get("configuration")
    if cfg is None:
        return {}
    blocks = cfg if isinstance(cfg, list) else [cfg]
    out = {}
    for block in blocks:
        out.update(block.get("properties", {}) or {})
    return out


def check(our_manifest_path: Path, vscode_app: str | None) -> tuple[bool, list[str]]:
    """Returns (ok, messages). ok=None means SKIPPED (no VS Code found)."""
    messages: list[str] = []

    our = _load_json(our_manifest_path)
    our_defaults = our.get("contributes", {}).get("configurationDefaults", {}) or {}
    if not our_defaults:
        messages.append("no configurationDefaults contributed — nothing to check (vacuous pass)")
        return True, messages

    copilot_manifest_path = _find_copilot_chat_manifest(vscode_app)
    if copilot_manifest_path is None:
        return None, [
            "THIS IS NOT A PASS — no VS Code / bundled GitHub.copilot-chat found on this machine "
            "(searched default macOS app path + ~/.vscode(-server)/extensions). "
            "Re-run with --vscode-app <path to Visual Studio Code.app>, or on a machine that has it."
        ]

    copilot_manifest = _load_json(copilot_manifest_path)
    copilot_props = _properties_from(copilot_manifest)

    ok = True
    for key, value in our_defaults.items():
        prop = copilot_props.get(key)
        if prop is None:
            ok = False
            messages.append(
                f"REJECTED: '{key}' is not a registered configuration property in the bundled "
                f"GitHub.copilot-chat manifest at {copilot_manifest_path} — VS Code will silently "
                f"drop this override with no warning (RT-3a)."
            )
            continue

        if prop.get("disallowConfigurationDefault") is True:
            ok = False
            messages.append(
                f"REJECTED: '{key}' declares disallowConfigurationDefault: true — VS Code will "
                f"silently drop this override, logging only to the extension problem collector "
                f"(RT-4)."
            )

        scope = prop.get("scope")
        if scope is not None and scope not in _ALLOWED_SCOPES:
            ok = False
            messages.append(
                f"REJECTED: '{key}' has scope '{scope}', outside the overridable set "
                f"{sorted(_ALLOWED_SCOPES)} — VS Code will silently drop this override (RT-4)."
            )

        if not isinstance(value, (int, float)) or isinstance(value, bool):
            ok = False
            messages.append(f"REJECTED: '{key}' value {value!r} is not a number.")
        elif not (0 < float(value) <= 1):
            ok = False
            messages.append(
                f"REJECTED: '{key}' value {value!r} is outside the documented (0, 1] ratio range."
            )

        if ok:
            messages.append(f"OK: '{key}' -> {value} is registered, no disallow flag, scope permitted.")

    return ok, messages


def _self_test() -> int:
    """Build synthetic fixture trees (never touch the real machine's VS Code) and assert
    both a known-good and a known-bad case behave correctly. Registered as --self-test,
    the canonical route this repo's own FORGE-produced scripts use (forge-route.py,
    forge-worktree.sh, premise-gate.py)."""
    tmp = Path(tempfile.mkdtemp(prefix="rc-vscode-cfg-selftest-"))
    try:
        fails = 0

        def _write(path: Path, data: dict) -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data), encoding="utf-8")

        # Fixture: a copilot-chat manifest with one clean, overridable property.
        copilot_good = tmp / "good" / "copilot" / "package.json"
        _write(
            copilot_good,
            {
                "contributes": {
                    "configuration": {
                        "properties": {
                            "github.copilot.chat.summarizeAgentConversationHistoryThreshold": {
                                "type": ["number", "null"]
                            }
                        }
                    }
                }
            },
        )
        ours_good = tmp / "good" / "ours" / "package.json"
        _write(
            ours_good,
            {
                "contributes": {
                    "configurationDefaults": {
                        "github.copilot.chat.summarizeAgentConversationHistoryThreshold": 0.8
                    }
                }
            },
        )

        class _FakeArgs:
            pass

        # Monkeypatch the locator for the self-test by pointing --vscode-app at a
        # synthetic "app" tree that mirrors the real macOS layout exactly.
        fake_app_good = tmp / "good" / "FakeApp.app"
        fake_manifest_good = (
            fake_app_good / "Contents" / "Resources" / "app" / "extensions" / "copilot" / "package.json"
        )
        fake_manifest_good.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(copilot_good, fake_manifest_good)

        ok, msgs = check(ours_good, str(fake_app_good))
        if ok is not True:
            print("SELF-TEST FAIL: known-good fixture did not pass:", msgs)
            fails += 1
        else:
            print("  ok    known-good fixture passes")

        # Bad fixture: a typo'd key that is NOT registered anywhere.
        ours_bad = tmp / "bad" / "ours" / "package.json"
        _write(
            ours_bad,
            {
                "contributes": {
                    "configurationDefaults": {
                        "github.copilot.chat.summarizeAgentConversationHistoryThresholdTYPO": 0.8
                    }
                }
            },
        )
        fake_app_bad = tmp / "good" / "FakeApp.app"  # reuse the good copilot manifest
        ok2, msgs2 = check(ours_bad, str(fake_app_bad))
        if ok2 is not False:
            print("SELF-TEST FAIL (TEETH): a typo'd/unregistered key must be REJECTED, got:", ok2, msgs2)
            fails += 1
        else:
            print("  ok    TEETH: unregistered key is rejected, not silently accepted")

        # Bad fixture: disallowConfigurationDefault.
        copilot_disallow = tmp / "disallow" / "copilot" / "package.json"
        _write(
            copilot_disallow,
            {
                "contributes": {
                    "configuration": {
                        "properties": {
                            "github.copilot.chat.summarizeAgentConversationHistoryThreshold": {
                                "type": ["number", "null"],
                                "disallowConfigurationDefault": True,
                            }
                        }
                    }
                }
            },
        )
        fake_app_disallow = tmp / "disallow" / "FakeApp.app"
        fake_manifest_disallow = (
            fake_app_disallow
            / "Contents"
            / "Resources"
            / "app"
            / "extensions"
            / "copilot"
            / "package.json"
        )
        fake_manifest_disallow.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(copilot_disallow, fake_manifest_disallow)
        ok3, msgs3 = check(ours_good, str(fake_app_disallow))
        if ok3 is not False:
            print("SELF-TEST FAIL (TEETH): disallowConfigurationDefault must be REJECTED, got:", ok3, msgs3)
            fails += 1
        else:
            print("  ok    TEETH: disallowConfigurationDefault is rejected")

        # Bad fixture: scope outside the allowed set.
        copilot_scope = tmp / "scope" / "copilot" / "package.json"
        _write(
            copilot_scope,
            {
                "contributes": {
                    "configuration": {
                        "properties": {
                            "github.copilot.chat.summarizeAgentConversationHistoryThreshold": {
                                "type": ["number", "null"],
                                "scope": "application",
                            }
                        }
                    }
                }
            },
        )
        fake_app_scope = tmp / "scope" / "FakeApp.app"
        fake_manifest_scope = (
            fake_app_scope / "Contents" / "Resources" / "app" / "extensions" / "copilot" / "package.json"
        )
        fake_manifest_scope.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(copilot_scope, fake_manifest_scope)
        ok4, msgs4 = check(ours_good, str(fake_app_scope))
        if ok4 is not False:
            print("SELF-TEST FAIL (TEETH): scope='application' must be REJECTED, got:", ok4, msgs4)
            fails += 1
        else:
            print("  ok    TEETH: disallowed scope 'application' is rejected")

        # Bad fixture: out-of-range value.
        ours_range = tmp / "range" / "ours" / "package.json"
        _write(
            ours_range,
            {
                "contributes": {
                    "configurationDefaults": {
                        "github.copilot.chat.summarizeAgentConversationHistoryThreshold": 1.5
                    }
                }
            },
        )
        ok5, msgs5 = check(ours_range, str(fake_app_good))
        if ok5 is not False:
            print("SELF-TEST FAIL (TEETH): value 1.5 (outside (0,1]) must be REJECTED, got:", ok5, msgs5)
            fails += 1
        else:
            print("  ok    TEETH: out-of-range value 1.5 is rejected")

        # Absence fixture: no VS Code found at all -> must be a SKIP (None), not a pass.
        ok6, msgs6 = check(ours_good, "/definitely/does/not/exist.app")
        if ok6 is not None:
            print("SELF-TEST FAIL: absent VS Code must SKIP (None), got:", ok6, msgs6)
            fails += 1
        else:
            print("  ok    absent VS Code -> SKIP (None), never a silent pass")

        print(f"\n{6 - fails} pass, {fails} fail")
        return 1 if fails else 0
    finally:
        import shutil as _sh

        _sh.rmtree(tmp, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vscode-app", default=None, help="path to Visual Studio Code.app (or equivalent)")
    ap.add_argument("--check", action="store_true", help="CI-facing mode; absent VS Code still loud-skips (exit 0) — see module docstring")
    ap.add_argument("--must-fail", action="store_true", help="plant a typo'd key and assert this script catches it")
    ap.add_argument("--self-test", action="store_true", help="run the bundled fixture self-test")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    if args.must_fail:
        # Plant a typo'd key in a throwaway copy of OUR real manifest, and check it
        # against a SYNTHETIC copilot-chat fixture (not the real installed one) so
        # this proves the checker's teeth everywhere, including CI where no real
        # VS Code exists — mirroring --self-test's fully-synthetic approach.
        tmp = Path(tempfile.mkdtemp(prefix="rc-vscode-cfg-mustfail-"))
        try:
            data = _load_json(OUR_MANIFEST)
            defaults = data.get("contributes", {}).get("configurationDefaults", {})
            mutated = {f"{k}-TYPO-DOES-NOT-EXIST": v for k, v in defaults.items()}
            data["contributes"]["configurationDefaults"] = mutated
            bad = tmp / "ours" / "package.json"
            bad.parent.mkdir(parents=True, exist_ok=True)
            bad.write_text(json.dumps(data), encoding="utf-8")

            # A synthetic copilot-chat fixture registering the REAL (un-typo'd) key,
            # so the only way to pass is if the checker actually validates key
            # existence rather than trusting whatever is in our own manifest.
            fake_app = tmp / "FakeApp.app"
            fake_manifest = (
                fake_app / "Contents" / "Resources" / "app" / "extensions" / "copilot" / "package.json"
            )
            fake_manifest.parent.mkdir(parents=True, exist_ok=True)
            fake_manifest.write_text(
                json.dumps(
                    {
                        "contributes": {
                            "configuration": {
                                "properties": {
                                    k.replace("-TYPO-DOES-NOT-EXIST", ""): {"type": ["number", "null"]}
                                    for k in mutated
                                }
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            ok, messages = check(bad, str(fake_app))
            if ok is None:
                print("\n".join(messages))
                print("MUST-FAIL VIOLATION: the synthetic fixture should never SKIP — checker logic is broken.")
                return 1
            if ok:
                print("MUST-FAIL VIOLATION: a typo'd key was accepted — the gate has no teeth.")
                return 1
            print("\n".join(messages))
            print("must-fail confirmed: the planted typo was correctly rejected.")
            return 0
        finally:
            import shutil as _sh

            _sh.rmtree(tmp, ignore_errors=True)

    ok, messages = check(OUR_MANIFEST, args.vscode_app)
    print("\n".join(messages))
    if ok is None:
        # Loud-skip in EVERY mode, including --check — see module docstring for why
        # this differs from Gate 10's actionlint (a downloadable binary CI does have).
        return 0
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
