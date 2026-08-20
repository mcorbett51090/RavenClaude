#!/usr/bin/env python3
"""inventory-sweep.py — the path-keyed efficacy harness. Plan P4 (⛔ R2, R8).

⛔ THE CENTRAL DESIGN CHANGE: PROBES ARE KEYED BY ARTIFACT PATH, NOT CONCEPT ID.

Both panel plans drove probes off inventory entries ("the registry IS
concepts.json"). That coupling is a choice, not a necessity, and it is what put
a check that finds real defects TODAY behind authoring 54 skill entries first.
Here the registry is keyed by path: the sweep runs across every hook, skill,
agent, command and script on day one with ZERO entries authored. When an
inventory entry exists it INHERITS the verdict for its covers[] paths; it never
gates the probe running.

⛔ R8 — THE HARNESS MUST NOT COUNT ITSELF. Three assertions after every run, all
against inventory-census.py, whose source is `git ls-files` — not concepts.json,
not concepts.py, and not any file this sweep writes:

  1. census == artifacts_enumerated   (a divergence by one is the sweep going blind)
  2. probes_registered == probes_executed  (a class typo, or a class with no runner)
  3. every registered class is invoked by this sweep  (a probe nobody calls is
     flagged exactly like an unwired hook — this repo has already paid for the
     general form: 39 of 49 gates invoked by no workflow)

⛔ THE TELL WHEN THE SWEEP GOES BLIND: any of the three numbers moving DOWN with
no corresponding artifact deletion in the same diff. All three are reported every
run for exactly that reason.

⛔ THE PERMANENTLY-RED CANARY. tests/fixtures/inventory-canary/ holds an artifact
whose probe is WRONG ON PURPOSE — it asserts a sentinel arrives on a channel
measured to be undelivered, mirroring the advisory-hook incident. If a run ever
reports it PASSING, the sweep is broken and its own gate fails loud. Every
"trust the harness" argument routes through that one fixture staying red.

── SECURITY OVERLAY — the probe IS the risk surface ────────────────────────
  · effect probes run against a mktemp project root, never the live repo
  · run records store DERIVED LABELS ONLY: path, class, verdict, duration.
    Never stdout, stderr, command text, or payloads
  · records land in .ravenclaude/runs/inventory-sweep/ — gitignored, per the
    storage contract. ⛔ Do not "helpfully" commit them; that reverses a
    deliberate decision about other people data
  · the planted-secret canary proves the scrubber BITES: a fixture payload
    carries a fake token and the written record must not contain it

⛔ THE TEETH-BIT EXIT IS 3, AND THE NUMBER IS LOAD-BEARING.
0 is ordinary success, 1 is an uncaught Python exception, and 2 is an argparse
error — every one of them reachable WITHOUT the canary biting. Measured
2026-08-20: an adversarial mutation that introduced an IndentationError exited 1,
which was the declared teeth code at the time, so a CRASHED teeth run was
indistinguishable from a PASSING one. That is the silent-green shape, inside the
mechanism built to detect it. 3 is returned only where this file returns it.

Usage:
    inventory-sweep.py                       # T0 report
    inventory-sweep.py --check               # gate
    inventory-sweep.py --tier T1             # + side-effect/adapter probes
    inventory-sweep.py --capping-table       # the claim-14 per-class capping run
    inventory-sweep.py --must-fail
    inventory-sweep.py --must-fail-convention
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib

_census_mod = importlib.import_module("inventory-census".replace("-", "_")) if False else None

PLUGIN = "plugins/ravenclaude-core"
RUN_DIR = ".ravenclaude/runs/inventory-sweep"
CANARY_DIR = "tests/fixtures/inventory-canary"
PLANTED_TOKEN = "sk-CANARY-0000-not-a-real-secret-0000"  # fixture only, never a credential

# ⛔ HOOKS THAT TAKE MACHINE-GLOBAL LOCKS ARE NOT EXECUTED BY THIS SWEEP.
# Measured 2026-08-19: hook-benign-passthrough ran every real hook inside a
# mktemp root with HOME and CLAUDE_PROJECT_DIR redirected — and worktree-guard.sh
# still wrote a lease into the REAL store, because it anchors that store at a path
# the HOME redirection does not cover. The lease then blocked this session own
# writes for nine minutes, held by a PID that had already exited.
#
# The lesson generalises: a sandbox is only as good as the paths it actually
# covers, and "I redirected HOME" is an assumption until something proves it. So
# these are SKIPPED and REPORTED AS SKIPPED — never silently passed, and never
# counted as evidence that they behave.
GLOBAL_LOCK_HOOKS = {
    "worktree-guard.sh": "writes a machine-global lease outside the sandboxed HOME",
    "dashboard-autostart.sh": "starts a long-lived server process",
    "thing-orchestrator.sh": "convenes the tribunal panel; can invoke a model",
    "route-decision-review.sh": "routes to the tribunal; can invoke a model",
}

# Verdict vocabulary. ⛔ CLOSED SET. A record may never carry free text derived
# from probe output — that is how payloads leak into a durable store.
PASS, FAIL, UNKNOWN, SKIP = "pass", "fail", "unknown", "skip"

# Detail labels: also a closed set, for the same reason.
LABELS = {
    "ok", "unregistered", "frontmatter-unparseable", "missing-description", "dangling-reference", "empty-tools", "orphan",
    "selftest-failed", "convention-mismatch", "no-selftest-declared",
    "denies-benign-payload", "hook-not-executable", "canary-red-as-designed",
    "canary-UNEXPECTEDLY-GREEN", "no-cheap-observable", "probe-timeout",
    "global-lock-hook", "self-probe-would-recurse",
}

_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)")
_FENCE = re.compile(r"```.*?```", re.DOTALL)
# ⛔ A TEMPLATE IS NOT A BROKEN LINK. Measured while building this probe: the
# first version reported `../skills/<pattern-name>.md` and `...` as dangling
# references. Both are AUTHORING TEMPLATES — one a named placeholder, one an
# ellipsis inside an example. Reporting them is the recorded "a grep is satisfied
# by the thing being described" failure, and two false findings in the first run
# is how a new detector gets switched off in week two. Fenced code is stripped
# before scanning for the same reason.
_PLACEHOLDER = re.compile(r"[<>{}]|^\.+$|\$\{|%s")


def _real_link_targets(text: str) -> list[str]:
    body = _FENCE.sub("", text)
    out = []
    for target in _MD_LINK.findall(body):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if _PLACEHOLDER.search(target):
            continue
        out.append(target)
    return out


# ── census import (the filename has a hyphen, so load it by path) ──────────
def _load_census():
    import importlib.util

    p = Path(__file__).resolve().parent / "inventory-census.py"
    spec = importlib.util.spec_from_file_location("inventory_census", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ══ PROBE CLASSES ═══════════════════════════════════════════════════════════
# Each class names its OWN observable, its OWN control, and its tier. ⛔ There is
# no universal probe shape — claim 14 is CAPPED here, not assumed. A class with
# no cheap observable says so and renders as `strength: static` or `tier: none`,
# rather than borrowing a stronger label than it earned.

CLASSES: dict[str, dict] = {}


def probe_class(name, *, tier, strength, population, control, requires="T0"):
    def deco(fn):
        CLASSES[name] = {
            "name": name, "tier": tier, "strength": strength,
            "population": population, "control": control, "requires": requires,
            "run": fn,
        }
        return fn

    return deco


@probe_class(
    "hook-registration", tier="reachability", strength="static",
    population="every hook in the census",
    control="a fixture hook absent from hooks.json must be reported unregistered",
)
def _hook_registration(root: Path, paths: list[str], ctx: dict) -> dict:
    # ⛔ THREE WAYS A HOOK IS REACHABLE, AND ONLY ONE IS hooks.json.
    #   1. registered on an event in hooks.json / .claude/settings.json
    #   2. SOURCED or invoked by another hook — every `_`-prefixed file here is a
    #      shared helper (_advise.sh, _scrub.sh, _emit-event.sh). It ships, it
    #      executes, and it can break, so the census counts it; but it is reached
    #      through its caller, never through an event registration.
    #   3. registered in ANOTHER HOST config — the codex / copilot / cursor /
    #      gemini adapters are wired into .codex/hooks.json and .github/hooks,
    #      not into Claude Code hooks.json.
    # The first version of this probe knew only (1) and reported 11 false
    # unregistrations, 7 of them shared helpers. A reachability probe that does
    # not model how the artifact is actually reached measures its own ignorance.
    registered = ctx["registered_hooks"]
    called = ctx["hook_call_haystack"]
    out = {}
    for p in paths:
        name = Path(p).name
        if name in registered:
            out[p] = (PASS, "ok")
        elif name in called:
            out[p] = (PASS, "ok")
        else:
            out[p] = (FAIL, "unregistered")
    return out


@probe_class(
    "skill-static", tier="reachability", strength="static",
    population="every SKILL.md in the census",
    control="a fixture skill with a dangling markdown link must be reported",
)
def _skill_static(root: Path, paths: list[str], ctx: dict) -> dict:
    return {p: _static_doc_verdict(root, p, need_tools=False) for p in paths}


@probe_class(
    "agent-static", tier="reachability", strength="static",
    population="every agent .md in the census",
    control="a fixture agent with an empty tools: line must be reported",
)
def _agent_static(root: Path, paths: list[str], ctx: dict) -> dict:
    return {p: _static_doc_verdict(root, p, need_tools=True) for p in paths}


@probe_class(
    "command-static", tier="reachability", strength="static",
    population="every command .md in the census",
    control="a fixture command with a dangling markdown link must be reported",
)
def _command_static(root: Path, paths: list[str], ctx: dict) -> dict:
    """⛔ ADDED BECAUSE THE R8 ASSERTION CAUGHT ITS ABSENCE. The first run reported
    census=308 against enumerated=299 — a divergence of exactly the 9 commands,
    which the census counted and no probe class covered. That is the assertion
    doing its job: it found a COVERAGE hole, not a counting bug, and it found it
    before any entry was authored."""
    out = {}
    for p in paths:
        fp = root / p
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError:
            out[p] = (FAIL, "frontmatter-unparseable")
            continue
        bad = [t for t in _real_link_targets(text) if not (fp.parent / t).resolve().exists()]
        out[p] = (FAIL, "dangling-reference") if bad else (PASS, "ok")
    return out


@probe_class(
    "script-callgraph", tier="reachability", strength="static",
    population="every script in the census",
    control="a planted orphan script must be reported unreachable",
)
def _script_callgraph(root: Path, paths: list[str], ctx: dict) -> dict:
    hay = ctx["callgraph_haystack"]
    out = {}
    for p in paths:
        name = Path(p).name
        # A python module is imported by MODULE name, never by filename, so a
        # filename-only search reports every helper module as an orphan.
        stem = Path(p).stem
        imported = p.endswith(".py") and re.search(rf"(?:import|from)\s+{re.escape(stem)}\b", hay)
        out[p] = (PASS, "ok") if (name in hay or imported) else (FAIL, "orphan")
    return out


@probe_class(
    "script-selftest", tier="effect", strength="executed",
    population="scripts whose SOURCE contains --must-fail-convention (grep, then run)",
    control="the tool OWN declared teeth-bit exit — divergent per tool, never hard-coded",
)
def _script_selftest(root: Path, paths: list[str], ctx: dict) -> dict:
    out = {}
    _self = Path(__file__).name
    for p in paths:
        # ⛔ THE SWEEP DOES NOT PROBE ITSELF. Measured: script-selftest ran
        # `inventory-sweep.py --must-fail`, whose teeth run performs a full sweep,
        # whose script-selftest runs `inventory-sweep.py --must-fail`… unbounded
        # recursion, visible only as a hang. Its own teeth are exercised directly
        # by audit-gates rc_mustfail, which is the right place: a harness that
        # grades itself inside its own run cannot report an independent verdict
        # anyway. Reported as a SKIP with a reason, never silently dropped.
        if Path(p).name == _self:
            out[p] = (SKIP, "self-probe-would-recurse")
            continue
        # ⛔ READ BEFORE YOU EXECUTE. The first version invoked all 183 scripts with
        # --must-fail-convention to find out whether they implemented it. Two
        # problems, and the second is the serious one: it took 5+ minutes, and a
        # script that does NOT parse arguments simply RUNS — so asking
        # generate-dashboards.py whether it declares a convention would have
        # regenerated the dashboard. A probe must not have side effects on the
        # thing it is probing. The declaration is a literal string in the file, so
        # grep for it and only then execute.
        try:
            src = (root / p).read_text(encoding="utf-8", errors="replace")
        except OSError:
            out[p] = (SKIP, "no-selftest-declared")
            continue
        if "--must-fail-convention" not in src:
            out[p] = (SKIP, "no-selftest-declared")
            continue
        runner = "python3" if p.endswith(".py") else "bash"
        decl = _run(root, [runner, p, "--must-fail-convention"], timeout=30)
        if decl.returncode != 0 or "must-fail-teeth-exit:" not in decl.stdout:
            out[p] = (SKIP, "no-selftest-declared")
            continue
        want = decl.stdout.split("must-fail-teeth-exit:")[1].strip().split()[0]
        # ⛔ A GENEROUS TIMEOUT, AND A TIMEOUT IS NOT A MISMATCH. Measured: the
        # sweep probing ITSELF (and the judge, which may attempt model calls) blew
        # a 120s budget and returned 124, which the comparison then read as
        # "declared 1, observed 124 — convention-mismatch". Two false findings from
        # a clock, not from a contract. A timeout is reported as UNKNOWN.
        _r = _run(root, [runner, p, "--must-fail"], timeout=420)
        if _r.returncode == 124:
            out[p] = (UNKNOWN, "probe-timeout")
            continue
        got = _r.returncode
        out[p] = (PASS, "ok") if str(got) == want else (FAIL, "convention-mismatch")
    return out


@probe_class(
    "hook-benign-passthrough", tier="effect", strength="executed",
    population="every hook in the census",
    control="TWO-SIDED: a hook that denies this benign payload is caught. A prober "
            "that reports every hook fine is caught by the permanently-red canary.",
    requires="T1",
)
def _hook_benign(root: Path, paths: list[str], ctx: dict) -> dict:
    """⛔ WHAT THIS DOES AND DOES NOT PROVE.

    It proves a hook does NOT deny an unrelated, benign tool call — the
    deny-everything failure mode, which is real and which a one-sided probe
    cannot see. It does NOT prove the hook denies what it is supposed to deny:
    that needs a per-hook trigger, which is per-hook knowledge this generic
    runner does not have. Labelled honestly rather than sold as full effect
    coverage of the guard contract.
    """
    out = {}
    # ⛔ EVERY EXECUTION HAPPENS IN A THROWAWAY PROJECT ROOT, NEVER THE LIVE REPO.
    # These are real shipping guards: they append ledgers, emit events, and write
    # posture state. The first version of this probe passed the live repo path and
    # had to be killed mid-run — it was doing exactly what the security overlay of
    # this file forbids. HOME is redirected too, because several hooks anchor
    # their state under ~/.ravenclaude rather than under the project.
    with tempfile.TemporaryDirectory() as td:
        sandbox = Path(td)
        (sandbox / "README.md").write_text("fixture\n", encoding="utf-8")
        (sandbox / ".ravenclaude").mkdir(exist_ok=True)
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(sandbox),
            "CLAUDE_PROJECT_DIR": str(sandbox),
            "CLAUDE_PLUGIN_ROOT": str(root / PLUGIN),
        }
        payload = json.dumps({
            "tool_name": "Read",
            "tool_input": {"file_path": str(sandbox / "README.md")},
            "session_id": "inventory-sweep-benign",
            "cwd": str(sandbox),
        })
        for p in paths:
            name = Path(p).name
            if name in GLOBAL_LOCK_HOOKS:
                out[p] = (SKIP, "global-lock-hook")
                continue
            fp = root / p
            r = _run(sandbox, ["bash", str(fp), str(sandbox)], stdin=payload,
                     timeout=8, env=env)
            if r.returncode == 124:
                # ⛔ A TIMEOUT IS UNKNOWN, NEVER A PASS. "did not deny within 8s"
                # and "does not deny" are different facts, and recording the second
                # from the first is the manufactured-clean shape.
                out[p] = (UNKNOWN, "probe-timeout")
                continue
            # ⛔ Exit 2 is the DENY channel. Anything else (0, 1, even a crash) is
            # not a denial — claim 8: a failing Bash tool_response carries no
            # exit-code field, so the emitted envelope is authoritative, never an
            # inferred code.
            out[p] = (FAIL, "denies-benign-payload") if r.returncode == 2 else (PASS, "ok")
    return out


@probe_class(
    "canary-permanently-red", tier="effect", strength="executed",
    population="the single fixture under tests/fixtures/inventory-canary/",
    control="IT IS the control. It asserts a sentinel on a channel measured to be "
            "undelivered, so it must stay red. A green run means the sweep is broken.",
)
def _canary(root: Path, paths: list[str], ctx: dict) -> dict:
    out = {}
    for p in paths:
        fp = root / p
        if not fp.is_file():
            out[p] = (UNKNOWN, "no-cheap-observable")
            continue
        # The canary hook writes its sentinel to STDERR at exit 0 — a channel
        # measured to reach the model on NO event. Asserting it arrives on the
        # delivered channel therefore CANNOT succeed. If it ever does, something
        # has rewritten either the canary or the assertion.
        r = _run(root, ["bash", str(fp)], stdin="{}", timeout=20)
        delivered = "additionalContext" in (r.stdout or "")
        out[p] = (FAIL, "canary-UNEXPECTEDLY-GREEN") if delivered else (PASS, "canary-red-as-designed")
    return out


# ── helpers ─────────────────────────────────────────────────────────────────
def _run(root: Path, cmd: list[str], stdin: str | None = None, timeout: int = 60,
         env: dict | None = None):
    """⛔ LIST FORM, NEVER shell=True. A probe that interpolates a repo path into a
    shell is the injection surface this whole initiative is trying to close."""
    try:
        return subprocess.run(
            cmd, cwd=str(root), input=stdin, capture_output=True, text=True,
            timeout=timeout, env=env,
        )
    except subprocess.TimeoutExpired:
        class _T:
            returncode, stdout, stderr = 124, "", ""
        return _T()
    except (OSError, subprocess.SubprocessError):
        class _R:
            returncode, stdout, stderr = 127, "", ""
        return _R()


def _static_doc_verdict(root: Path, rel: str, need_tools: bool):
    fp = root / rel
    try:
        text = fp.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return (FAIL, "frontmatter-unparseable")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return (FAIL, "frontmatter-unparseable")
    fm = m.group(1)
    # ⛔ `name:` IS NOT GATED, AND THE REASON MATTERS. A skill with no `name:`
    # still loads — the host derives it from the directory. 6 of 54 skills here
    # omit it and work. Failing on it would report a CONVENTION INCONSISTENCY as a
    # reachability defect, which inflates the finding count with things that are
    # not broken. `description:` IS gated: it is the only field a model reads when
    # deciding whether to load the skill at all, so an absent one is genuine
    # unreachability.
    if not re.search(r"^description\s*:\s*\S", fm, re.M):
        return (FAIL, "missing-description")
    if need_tools and not re.search(r"^tools\s*:\s*\S", fm, re.M):
        return (FAIL, "empty-tools")
    for target in _real_link_targets(text):
        if not (fp.parent / target).resolve().exists():
            return (FAIL, "dangling-reference")
    return (PASS, "ok")


def dangling_references(root: Path, rel: str) -> list[str]:
    """Every markdown-link target in a doc that does not resolve.

    ⛔ MARKDOWN LINKS ONLY — deliberately. A backticked prose mention of a
    since-removed file is a DESCRIPTION of a path, not a reference to one, and
    flagging it is the recorded "a grep is satisfied by the thing being
    described" failure. A link promises resolution; prose does not.
    """
    fp = root / rel
    text = fp.read_text(encoding="utf-8", errors="replace")
    return [t for t in _real_link_targets(text) if not (fp.parent / t).resolve().exists()]


def _registered_hook_names(root: Path) -> set[str]:
    names: set[str] = set()
    for cfg in (root / PLUGIN / "hooks" / "hooks.json", root / ".claude" / "settings.json"):
        if not cfg.is_file():
            continue
        blob = cfg.read_text(encoding="utf-8", errors="replace")
        names.update(re.findall(r"([A-Za-z0-9_.-]+\.sh)", blob))
    return names


def _hook_call_haystack(root: Path) -> str:
    """Everything that could NAME a hook: sibling hooks (source/exec), other-host
    configs, and the installer that wires them."""
    parts = []
    for pat in (f"{PLUGIN}/hooks/*.sh", f"{PLUGIN}/hooks/hooks.json", f"{PLUGIN}/codex/**/*",
                f"{PLUGIN}/copilot/**/*", ".claude/settings.json", ".codex/*", ".github/hooks/*",
                "scripts/ravenclaude", "scripts/*.py"):
        for f in root.glob(pat):
            if f.is_file():
                try:
                    parts.append(f.read_text(encoding="utf-8", errors="replace"))
                except OSError:
                    pass
    return "\n".join(parts)


def _callgraph_haystack(root: Path) -> str:
    parts = []
    for pat in (".github/workflows/*.yml", f"{PLUGIN}/hooks/*.sh", f"{PLUGIN}/skills/*/SKILL.md",
                f"{PLUGIN}/commands/*.md", "scripts/*", f"{PLUGIN}/scripts/*", f"{PLUGIN}/bin/*",
                f"{PLUGIN}/CLAUDE.md", "AGENTS.md", "CLAUDE.md"):
        for f in root.glob(pat):
            if f.is_file():
                try:
                    parts.append(f.read_text(encoding="utf-8", errors="replace"))
                except OSError:
                    pass
    return "\n".join(parts)


def _derive(rel: str, cls: str, verdict: str, label: str, ms: int) -> dict:
    """⛔ THE SCRUBBER. Only these five fields ever reach a durable record, and
    `label` is validated against a CLOSED vocabulary. There is no code path that
    can put probe stdout, stderr, a command line, or a payload into the store."""
    return {
        "artifact": rel,
        "class": cls,
        "verdict": verdict if verdict in (PASS, FAIL, UNKNOWN, SKIP) else UNKNOWN,
        "label": label if label in LABELS else "no-cheap-observable",
        "duration_ms": int(ms),
    }


def build_populations(root: Path, c: dict) -> dict[str, list[str]]:
    scripts = c["root-script"] + c["plugin-script"]
    canary = [str(p.relative_to(root)) for p in sorted((root / CANARY_DIR).glob("*.sh"))] \
        if (root / CANARY_DIR).is_dir() else []
    return {
        "hook-registration": c["hook"],
        "skill-static": c["skill"],
        "agent-static": c["agent"],
        "command-static": c["command"],
        "script-callgraph": scripts,
        "script-selftest": scripts,
        "hook-benign-passthrough": c["hook"],
        "canary-permanently-red": canary,
    }


def sweep(root: Path, tier: str = "T0") -> dict:
    cm = _load_census()
    c = cm.census(root)
    census_total = sum(len(v) for v in c.values())

    ctx = {
        "registered_hooks": _registered_hook_names(root),
        "callgraph_haystack": _callgraph_haystack(root),
        "hook_call_haystack": _hook_call_haystack(root),
    }
    pops = build_populations(root, c)

    records: list[dict] = []
    enumerated: set[str] = set()
    executed: list[str] = []
    deferred: list[str] = []

    for name, spec in CLASSES.items():
        paths = pops.get(name, [])
        # ⛔ TIER GATING HAPPENS BEFORE THE RUN, AND A DEFERRED CLASS IS NAMED.
        # hook-benign-passthrough EXECUTES 47 real shipping guards; that belongs on
        # the nightly sweep, not on every PR. But a class that silently vanished
        # from the tier would make assertion 2 (registered == executed) pass by
        # shrinking BOTH sides — the exact self-counting defect R8 exists to stop.
        # So a deferred class is listed by name and excluded from the denominator
        # explicitly, never dropped.
        if tier == "T0" and spec["requires"] != "T0":
            deferred.append(name)
            continue
        t0 = time.time()
        results = spec["run"](root, paths, ctx)
        ms_each = int((time.time() - t0) * 1000 / max(1, len(paths)))
        executed.append(name)
        for rel, (verdict, label) in results.items():
            records.append(_derive(rel, name, verdict, label, ms_each))
            if name != "canary-permanently-red":
                enumerated.add(rel)

    # ── The three R8 assertions, against the INDEPENDENT census ──
    assertions = {
        "census_vs_enumerated": {
            "census": census_total,
            "enumerated": len(enumerated),
            "ok": census_total == len(enumerated),
        },
        "registered_vs_executed": {
            "registered": len(CLASSES),
            "executed": len(executed),
            "deferred_to_higher_tier": sorted(deferred),
            "ok": len(CLASSES) == len(executed) + len(deferred),
        },
        "every_class_invoked": {
            "uninvoked": sorted(set(CLASSES) - set(executed) - set(deferred)),
            "ok": not (set(CLASSES) - set(executed) - set(deferred)),
        },
    }
    return {"records": records, "assertions": assertions, "census": c, "tier": tier,
            "classes": {k: {kk: vv for kk, vv in v.items() if kk != "run"}
                        for k, v in CLASSES.items()}}


def write_records(root: Path, result: dict, stamp: str) -> Path:
    d = root / RUN_DIR
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{stamp}.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for rec in result["records"]:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--tier", default="T0", choices=("T0", "T1"))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--capping-table", action="store_true")
    ap.add_argument("--stamp", default="latest", help="record filename stem (no clock in-process)")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    args = ap.parse_args()

    if args.must_fail_convention:
        print("must-fail-teeth-exit: 3")
        return 0

    root = Path(args.root).resolve()

    if args.must_fail:
        return _must_fail(root)

    if args.capping_table:
        return _capping_table(root)

    result = sweep(root, tier=args.tier)
    rec_path = write_records(root, result, args.stamp)

    if args.json:
        print(json.dumps({"assertions": result["assertions"],
                          "records": result["records"]}, indent=2, sort_keys=True))
        return 0

    by_class: dict[str, dict[str, int]] = {}
    for rec in result["records"]:
        by_class.setdefault(rec["class"], {}).setdefault(rec["verdict"], 0)
        by_class[rec["class"]][rec["verdict"]] += 1

    print("── inventory sweep (path-keyed; ZERO inventory entries required) ──")
    print(f"  records : {rec_path.relative_to(root)}  (gitignored, derived labels only)")
    print()
    print(f"  {'CLASS':<26} {'TIER':<13} {'STRENGTH':<13} VERDICTS")
    for name, spec in CLASSES.items():
        counts = by_class.get(name, {})
        # ⛔ "(empty population)" and "deferred to a higher tier" are DIFFERENT
        # facts. Printing the first for the second reads as "there are no hooks",
        # which is the manufactured-clean shape one line lower than usual.
        if not counts:
            summary = ("deferred to --tier T1" if spec["requires"] != "T0"
                       else "(EMPTY POPULATION — not a clean result)")
        else:
            summary = "  ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        print(f"  {name:<26} {spec['tier']:<13} {spec['strength']:<13} {summary}")

    print()
    print("── ⛔ R8: the sweep-of-the-sweep (source: git ls-files, NOT concepts.json) ──")
    a = result["assertions"]
    print(f"  independent census      : {a['census_vs_enumerated']['census']}")
    print(f"  artifacts enumerated    : {a['census_vs_enumerated']['enumerated']}"
          f"  {'✓' if a['census_vs_enumerated']['ok'] else '✗ DIVERGENCE — the sweep is going blind'}")
    print(f"  probes registered       : {a['registered_vs_executed']['registered']}")
    print(f"  probes executed         : {a['registered_vs_executed']['executed']}"
          f"  {'✓' if a['registered_vs_executed']['ok'] else '✗'}")
    _def = a["registered_vs_executed"]["deferred_to_higher_tier"]
    print(f"  deferred to a T1 sweep  : {', '.join(_def) if _def else 'none'}"
          "   (NAMED, never silently dropped)")
    print(f"  classes never invoked   : {a['every_class_invoked']['uninvoked'] or 'none'}"
          f"  {'✓' if a['every_class_invoked']['ok'] else '✗'}")
    print()
    print("  ⛔ THE TELL: any of these three moving DOWN with no artifact deletion")
    print("     in the same diff. That is the sweep losing sight, not the repo shrinking.")

    failures = [r for r in result["records"] if r["verdict"] == FAIL]
    canary = [r for r in result["records"] if r["class"] == "canary-permanently-red"]
    canary_red = all(r["label"] == "canary-red-as-designed" for r in canary) and bool(canary)

    print()
    if canary:
        print(f"  permanently-red canary  : {'RED (correct)' if canary_red else '⛔ GREEN — THE SWEEP IS BROKEN'}")
    else:
        print("  permanently-red canary  : ⛔ ABSENT — every result above is untrusted")

    real_failures = [r for r in failures if r["class"] != "canary-permanently-red"]
    if real_failures:
        print()
        print(f"  ⛔ {len(real_failures)} artifact-level finding(s):")
        for r in sorted(real_failures, key=lambda x: (x["class"], x["artifact"]))[:40]:
            print(f"    ✗ [{r['class']}] {r['artifact']} — {r['label']}")
        if len(real_failures) > 40:
            print(f"    … and {len(real_failures) - 40} more (see the records file)")

    if args.check:
        bad = (not all(v["ok"] for v in a.values())) or (not canary_red) or bool(real_failures)
        return 1 if bad else 0
    return 0


def _capping_table(root: Path) -> int:
    """⛔ CLAIM 14, CAPPED RATHER THAN ASSUMED. Row per class: does the observable
    exist, and DOES ITS CONTROL FIRE. Exit condition from the plan: any class whose
    control does not fire is demoted to tier: none with a written rationale. A
    probe with no working control does not ship."""
    result = sweep(root, tier="T1")
    print("── claim-14 capping table: one probe AND its control, per class ──")
    print(f"  {'CLASS':<26} {'TIER':<13} {'OBSERVABLE':<12} CONTROL FIRED?")
    controls = _control_results(root)
    demote = []
    for name, spec in CLASSES.items():
        pop = len([r for r in result["records"] if r["class"] == name])
        obs = "yes" if pop else "EMPTY"
        fired = controls.get(name)
        mark = "yes" if fired else ("NO — demote to tier: none" if fired is False else "n/a (is the control)")
        print(f"  {name:<26} {spec['tier']:<13} {obs:<12} {mark}")
        if fired is False:
            demote.append(name)
    print()
    for name, spec in CLASSES.items():
        print(f"  {name}:")
        print(f"    control: {spec['control']}")
    if demote:
        print()
        print(f"  ⛔ {len(demote)} class(es) have a control that does not fire: {', '.join(demote)}")
        print("     Per the plan exit condition these are tier: none until fixed.")
        return 1
    return 0


def _control_results(root: Path) -> dict[str, bool | None]:
    """Run each class control against a planted fixture in a temp tree."""
    out: dict[str, bool | None] = {}
    with tempfile.TemporaryDirectory() as td:
        fake = Path(td)
        ctx = {"registered_hooks": set(), "callgraph_haystack": "", "hook_call_haystack": ""}

        # hook-registration: a hook absent from hooks.json must be unregistered.
        out["hook-registration"] = (
            _hook_registration(fake, ["a/unregistered.sh"], ctx)["a/unregistered.sh"][0] == FAIL
        )

        # skill-static: a skill with a dangling markdown link must be reported.
        sk = fake / "skills" / "bad"
        sk.mkdir(parents=True)
        (sk / "SKILL.md").write_text(
            "---\nname: bad\ndescription: fixture\n---\n[gone](./nope.md)\n", encoding="utf-8"
        )
        out["skill-static"] = _skill_static(fake, ["skills/bad/SKILL.md"], ctx)["skills/bad/SKILL.md"][0] == FAIL

        # agent-static: an agent with no tools: must be reported.
        ag = fake / "agents"
        ag.mkdir(parents=True)
        (ag / "bad.md").write_text("---\nname: bad\ndescription: fixture\n---\nbody\n", encoding="utf-8")
        out["agent-static"] = _agent_static(fake, ["agents/bad.md"], ctx)["agents/bad.md"][0] == FAIL

        # script-callgraph: a planted orphan must be reported unreachable.
        out["script-callgraph"] = (
            _script_callgraph(fake, ["scripts/orphan.py"], ctx)["scripts/orphan.py"][0] == FAIL
        )

        # script-selftest: a tool declaring one exit and returning another.
        sc = fake / "scripts"
        sc.mkdir(parents=True, exist_ok=True)
        liar = sc / "liar.sh"
        liar.write_text(
            "#!/usr/bin/env bash\n"
            'if [ "${1:-}" = "--must-fail-convention" ]; then echo "must-fail-teeth-exit: 1"; exit 0; fi\n'
            'if [ "${1:-}" = "--must-fail" ]; then exit 0; fi\n',
            encoding="utf-8",
        )
        out["script-selftest"] = (
            _script_selftest(fake, ["scripts/liar.sh"], ctx)["scripts/liar.sh"][0] == FAIL
        )

        # hook-benign-passthrough: a hook that denies everything must be caught.
        hk = fake / "hooks"
        hk.mkdir(parents=True, exist_ok=True)
        (fake / "README.md").write_text("fixture\n", encoding="utf-8")
        (hk / "denies-all.sh").write_text("#!/usr/bin/env bash\nexit 2\n", encoding="utf-8")
        out["hook-benign-passthrough"] = (
            _hook_benign(fake, ["hooks/denies-all.sh"], ctx)["hooks/denies-all.sh"][0] == FAIL
        )

        cm = fake / "commands"
        cm.mkdir(parents=True, exist_ok=True)
        (cm / "bad.md").write_text("# bad\n\n[gone](./nope.md)\n", encoding="utf-8")
        out["command-static"] = _command_static(fake, ["commands/bad.md"], ctx)["commands/bad.md"][0] == FAIL

        out["canary-permanently-red"] = None  # it IS the control
    return out


def _must_fail(root: Path) -> int:
    """TEETH, on three separate mechanisms. ⛔ Exits with the DECLARED teeth code
    when every canary bites, so audit-gates can compare rather than hard-code."""
    controls = _control_results(root)
    dead = [k for k, v in controls.items() if v is False]
    if dead:
        print(f"✗ must-fail: control(s) did not fire: {', '.join(dead)}")
        print("  A clean sweep is not evidence while any class control is inert.")
        return 0

    # 2. The scrubber must bite: a planted secret must not reach a record.
    rec = _derive("a/b.sh", "hook-registration", PASS, PLANTED_TOKEN, 1)
    if PLANTED_TOKEN in json.dumps(rec):
        print("✗ must-fail: the planted token reached a derived record — the scrubber")
        print("  is not actually constraining the label vocabulary.")
        return 0

    # 3. The permanently-red canary must be RED on the real tree.
    result = sweep(root, tier="T0")
    canary = [r for r in result["records"] if r["class"] == "canary-permanently-red"]
    if not canary:
        print("✗ must-fail: the permanently-red canary is ABSENT. Without it, a long")
        print("  green streak and a blind sweep are the same observation.")
        return 0
    if any(r["label"] != "canary-red-as-designed" for r in canary):
        print("✗ must-fail: the permanently-red canary reported GREEN.")
        return 0

    print("✓ must-fail: every class control fires, the scrubber constrains the label")
    print("  vocabulary, and the permanently-red canary is red.")
    print("  Exiting 3, the DECLARED teeth code, so the auditor can compare.")
    return 3


if __name__ == "__main__":
    sys.exit(main())
