#!/usr/bin/env python3
"""check-review-2026-10-20-core.py — regression cases for the 2026-10-20 repo review,
package PK-3 (ravenclaude-core skills, monitors, launcher template).

One case per finding id. Each case drives the REAL shipped file (a workflow script under
a stub runtime, a shell script under a scratch HOME, a Python module imported by path) and
asserts the fixed behavior. The workflow cases count real agent() calls through a stub
runtime: the Workflow tool itself cannot run in CI, so the stub is the closest observable.

Teeth: every case is written so it FAILS against the pre-fix tree. Point --root at a tree
exported from the base commit and the case for each finding goes red:

    git archive -o base.tar <base-sha> -- plugins/ravenclaude-core scripts .claude/workflows
    mkdir base && tar -xf base.tar -C base
    python3 scripts/check-review-2026-10-20-core.py --root base --only C-1

Usage:
    python3 scripts/check-review-2026-10-20-core.py [--root DIR] [--only ID[,ID...]] [--list]

Exit 0 = every selected case passed. Exit 1 = a case failed. Exit 2 = a case could not run
(for example node is not on PATH). Exit 2 is NOT a pass.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

WF_REL = "plugins/ravenclaude-core/skills/repo-review/workflows/repo-sweep.workflow.js"


class _Fail(Exception):
    pass


class _NotRun(Exception):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise _Fail(msg)
    print(f"    ok  {msg}")


# ─── Stub Workflow runtime ────────────────────────────────────────────────────
# Loads the workflow body as an async function by writing it into a temp ES module and
# importing it (no eval / new Function). agent() answers by label from a scenario object
# and counts every call; a call past scen.cap throws, like the real 1,000-call cap.
_SWEEP_HARNESS = r"""
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";
const [, , scriptPath, argsJson, scenJson] = process.argv;
const scen = JSON.parse(scenJson);
const src = fs.readFileSync(scriptPath, "utf8").replace(/^export const meta =/m, "const meta =");
const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rc-sweep-"));
const mod = path.join(dir, "wf.mjs");
fs.writeFileSync(mod, "export default async function run(agent, parallel, pipeline, phase, log, args, budget) {\n" + src + "\n}\n");
const { default: run } = await import(pathToFileURL(mod).href);
const cap = scen.cap ?? 1000;
let calls = 0;
let capErrors = 0;
const labels = [];
const logs = [];
const prompts = [];
const batchIds = Array.from({ length: scen.batches ?? 5 }, (_, i) => "b" + String(i + 1).padStart(3, "0"));
const survivors = scen.survivors || [];
async function agent(prompt, opts = {}) {
  calls += 1;
  const label = opts.label || "(nolabel)";
  labels.push(label);
  prompts.push(String(prompt));
  if (calls > cap) {
    capErrors += 1;
    throw new Error("WorkflowAgentCapError: agent() call cap reached");
  }
  if (label.startsWith("preflight:")) return scen.findingsDir === undefined ? { exists: false, shard_count: 0 } : scen.findingsDir;
  if (label === "map:repo-map")
    return { plan_path: "p.json", batch_ids: batchIds, coverage: { batches_planned: batchIds.length, files_covered: batchIds.length * 5, files_deferred: 0 } };
  if (label === "map:estimate-cost") return { estimate_summary: "stub" };
  if (label.startsWith("cache:")) return { allCached: false, count: 0, files: ["a.py"] };
  if (label.startsWith("review:")) return { artifact: "x.json", count: 0 };
  if (label === "merge:findings-merge") {
    if (scen.mergeThrows) throw new Error("merge agent failed");
    return { artifact: "merged.json", survivors_count: survivors.length, over_cap_count: 0, by_priority: { P0: survivors.length, P1: 0, P2: 0, P3: 0 } };
  }
  if (label === "verify:enumerate") return scen.enumerate === undefined ? { findings: survivors } : scen.enumerate;
  if (label.startsWith("verify:")) {
    if (scen.verify === "null") return null;
    if (scen.verify === "throw") throw new Error("verify agent failed");
    const file = label.slice("verify:".length);
    let mine = survivors.filter((s) => s.file === file);
    if (scen.verify === "short") mine = mine.slice(0, 1);
    return { file, verdicts: mine.map((s) => ({ id: s.id, verdict: "PLAUSIBLE", evidence: "e", fixable_in_place: false })) };
  }
  if (label === "report:write") return "ok";
  return {};
}
async function parallel(thunks) {
  return Promise.all(thunks.map(async (t) => { try { return await t(); } catch (e) { return null; } }));
}
async function pipeline(items, ...stages) {
  return Promise.all(items.map(async (it, i) => {
    try { let p = it; for (const s of stages) p = await s(p, it, i); return p; } catch (e) { return null; }
  }));
}
let ret;
let err;
try {
  ret = await run(agent, parallel, pipeline, () => {}, (m) => logs.push(String(m)), JSON.parse(argsJson), { total: null, spent: () => 0, remaining: () => Infinity });
} catch (e) {
  err = String((e && e.message) || e);
}
fs.rmSync(dir, { recursive: true, force: true });
const runDirLine = logs.find((l) => l.includes("runDir=")) || "";
console.log(JSON.stringify({
  calls,
  capErrors,
  reviewCalls: labels.filter((l) => l.startsWith("review:") || l.startsWith("cache:")).length,
  labels,
  err: err === undefined ? null : err,
  ret: ret === undefined ? null : ret,
  runDir: (runDirLine.match(/runDir=(\S+)/) || [])[1] || null,
  logs,
  reportBody: prompts.find((p) => p.includes("---BEGIN---")) || null,
}));
"""

_TMP = Path(tempfile.mkdtemp(prefix="rc-review-core-"))


def _node() -> str:
    node = shutil.which("node")
    if not node:
        raise _NotRun("node is not on PATH")
    return node


def _harness(name: str, body: str) -> Path:
    p = _TMP / name
    if not p.exists():
        p.write_text(body, encoding="utf-8")
    return p


def _run_sweep(root: Path, args: dict, scen: dict | None = None) -> dict:
    wf = root / WF_REL
    if not wf.is_file():
        raise _NotRun(f"{wf} is missing")
    cp = subprocess.run(
        [
            _node(),
            str(_harness("sweep.mjs", _SWEEP_HARNESS)),
            str(wf),
            json.dumps(args),
            json.dumps(scen or {}),
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if cp.returncode != 0 or not cp.stdout.strip():
        raise _Fail(f"sweep harness crashed: {cp.stderr.strip()[-400:]}")
    return json.loads(cp.stdout.strip().splitlines()[-1])


def _err(res: dict) -> str:
    ret = res.get("ret") or {}
    return str(ret.get("error") or "") if isinstance(ret, dict) else ""


# ─── C-1: the default run id was the constant repo-sweep-1001 ────────────────
def case_c1(root: Path) -> None:
    res = _run_sweep(root, {"effort": "high"}, {"batches": 3})
    _check("args.runId" in _err(res), "no args.runId -> {error} naming args.runId")
    _check(res["calls"] == 0, f"no args.runId -> 0 agent() calls (got {res['calls']})")

    a = _run_sweep(root, {"effort": "high", "runId": "sweep-a"}, {"batches": 3})
    b = _run_sweep(root, {"effort": "high", "runId": "sweep-b"}, {"batches": 3})
    _check(
        a["runDir"] == ".ravenclaude/runs/sweep-a" and b["runDir"] == ".ravenclaude/runs/sweep-b",
        f"distinct runIds -> distinct run dirs ({a['runDir']} vs {b['runDir']})",
    )

    full = _run_sweep(
        root,
        {"effort": "high", "runId": "rerun"},
        {"batches": 3, "findingsDir": {"exists": True, "shard_count": 4}},
    )
    _check("already holds" in _err(full), "non-block rerun into a populated findings/ -> {error}")
    _check("map:repo-map" not in full["labels"], "the refused rerun dispatched no Map agent")

    blind = _run_sweep(
        root, {"effort": "high", "runId": "blind"}, {"batches": 3, "findingsDir": None}
    )
    _check(
        "could not confirm" in _err(blind),
        "a preflight with no usable answer refuses (fails closed)",
    )

    block = _run_sweep(
        root,
        {"effort": "high", "runId": "blk", "batchIds": ["b001"]},
        {"batches": 3, "findingsDir": {"exists": True, "shard_count": 4}},
    )
    ret = block.get("ret") or {}
    _check(
        isinstance(ret, dict) and (ret.get("block") or {}).get("mode") == "review-only",
        "block mode into a populated findings/ is NOT refused (the dir is shared on purpose)",
    )
    _check(
        "preflight:findings-dir" not in block["labels"], "block mode skips the fresh-run preflight"
    )


# ─── C-2: max/ultra default budgets demanded more agent() calls than the cap ──
def case_c2(root: Path) -> None:
    big = _run_sweep(root, {"effort": "max", "runId": "c2-max"}, {"batches": 80})
    ret = big.get("ret") or {}
    _check("refuses to start Review" in _err(big), "max/80 -> {error} before Review")
    _check(
        big["reviewCalls"] == 0,
        f"max/80 -> 0 review/cache agent() calls (got {big['reviewCalls']})",
    )
    _check(big["calls"] <= 3, f"max/80 -> only the pre-review calls were made (got {big['calls']})")
    _check("block_planner.py" in _err(big), "the refusal names block mode (block_planner.py)")
    fit = ret.get("largest_budget_batches")
    _check(
        isinstance(fit, int) and fit >= 1,
        f"the refusal names the largest budgetBatches that fits ({fit})",
    )
    ok = _run_sweep(root, {"effort": "max", "runId": "c2-fit"}, {"batches": fit})
    _check(
        "refuses to start Review" not in _err(ok) and ok["capErrors"] == 0 and ok["calls"] <= 900,
        f"max at the named budget ({fit} batches) runs under the ceiling ({ok['calls']} calls)",
    )
    ultra = _run_sweep(root, {"effort": "ultra", "runId": "c2-ultra"}, {"batches": 160})
    _check(
        "refuses to start Review" in _err(ultra) and ultra["reviewCalls"] == 0,
        "ultra/160 -> {error} before Review",
    )

    high = _run_sweep(root, {"effort": "high", "runId": "c2-high"}, {"batches": 20})
    hret = high.get("ret") or {}
    _check(
        isinstance(hret, dict) and "report_md" in hret and high["capErrors"] == 0,
        f"high/20 runs to the report ({high['calls']} calls)",
    )

    merge = _run_sweep(
        root, {"effort": "high", "runId": "c2-merge"}, {"batches": 3, "mergeThrows": True}
    )
    mret = merge.get("ret") or {}
    _check(merge.get("err") is None, "a throwing Merge agent does not abort the script uncaught")
    _check(
        isinstance(mret, dict)
        and mret.get("findings_dir") == ".ravenclaude/runs/c2-merge/findings",
        "a throwing Merge returns {error, findings_dir}",
    )


# ─── C-11: the per-repo launcher killed every project's dashboard ────────────
# The launcher runs with a pkill shim first on PATH: the shim applies the REAL pgrep -f
# matching to the launcher's pattern but only signals this test's own fake servers, so a
# pre-fix launcher can never kill a real dashboard on the machine running the test.
_PKILL_SHIM = """#!/bin/sh
[ "$1" = "-f" ] || exit 2
hit=1
for pid in $(pgrep -f "$2"); do
  case " $FAKE_PIDS " in *" $pid "*) kill "$pid" && hit=0 ;; esac
done
exit $hit
"""


def case_c11(root: Path) -> None:
    launcher = root / "plugins/ravenclaude-core/templates/dashboard-launcher/dashboard.sh"
    if not shutil.which("pgrep"):
        raise _NotRun("pgrep is not on PATH")
    w = Path(tempfile.mkdtemp(prefix="c11-", dir=_TMP))
    srv = w / "market/plugins/ravenclaude-core/scripts/serve-dashboards.py"
    srv.parent.mkdir(parents=True)
    srv.write_text("import time\ntime.sleep(600)\n")
    (w / "bin").mkdir()
    for name, body in (
        ("pkill", _PKILL_SHIM),
        ("curl", "#!/bin/sh\nexit 0\n"),
        ("browser", "#!/bin/sh\nexit 0\n"),
    ):
        (w / "bin" / name).write_text(body)
        (w / "bin" / name).chmod(0o755)
    repo_b = w / "B"
    (repo_b / ".ravenclaude").mkdir(parents=True)
    shutil.copy(launcher, repo_b / ".ravenclaude/dashboard.sh")
    procs: dict[str, subprocess.Popen] = {}
    try:
        # A is another project; "B.x+" has B as a string prefix and regex metacharacters.
        for name, port in (("A", "8000"), ("B.x+", "8002"), ("B", "8001")):
            procs[name] = subprocess.Popen(
                [sys.executable, str(srv), "--project-root", str(w / name), "--port", port],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        env = dict(os.environ)
        env.update(
            PATH=f"{w / 'bin'}:{env.get('PATH', '')}",
            RAVENCLAUDE_DIR=str(w / "market"),
            BROWSER=str(w / "bin/browser"),
            FAKE_PIDS=" ".join(str(p.pid) for p in procs.values()),
        )
        env.pop("CODESPACE_NAME", None)
        cp = subprocess.run(
            ["bash", str(repo_b / ".ravenclaude/dashboard.sh"), "8001"],
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        _check(
            cp.returncode == 0,
            f"launcher for B exits 0 (rc={cp.returncode}, {cp.stderr.strip()[-200:]})",
        )
        for p in procs.values():
            try:
                p.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                pass
        _check(
            procs["A"].poll() is None, "another project's dashboard (A) survives the launcher for B"
        )
        _check(procs["B.x+"].poll() is None, "a repo whose path has B as a prefix survives")
        _check(procs["B"].poll() is not None, "B's own previous dashboard is stopped")
        _check(
            "pkill -f serve-dashboards.py " not in cp.stdout
            and "--project-root" in cp.stdout.splitlines()[-1],
            "the printed stop command is scoped to this repo",
        )
    finally:
        for p in procs.values():
            if p.poll() is None:
                p.kill()
        out = subprocess.run(["pgrep", "-f", str(w)], capture_output=True, text=True).stdout
        for pid in out.split():
            try:
                os.kill(int(pid), 9)
            except (OSError, ValueError):
                pass


# ─── C-3: survivors with no verdict vanished from the open count ─────────────
_THREE_P0 = [
    {"id": "f-a", "file": "x.py", "severity": "blocking"},
    {"id": "f-b", "file": "x.py", "severity": "blocking"},
    {"id": "f-c", "file": "y.py", "severity": "blocking"},
]


def case_c3(root: Path) -> None:
    res = _run_sweep(
        root,
        {"effort": "high", "runId": "c3-null", "converge": True},
        {"batches": 3, "verify": "null", "survivors": _THREE_P0},
    )
    ret = res.get("ret") or {}
    conv = ret.get("converge") or {}
    report = res.get("reportBody") or ""
    _check(
        conv.get("converged") is False,
        "3 P0 survivors, every verify agent returns null -> not converged",
    )
    _check(conv.get("open_after") == 3, f"open_after == 3 (got {conv.get('open_after')})")
    _check(
        not any("Converge: CONVERGED" in line for line in res["logs"])
        and "CONVERGED — 0 open" not in report,
        "no CONVERGED claim in the log or the report",
    )
    _check(
        ret.get("unverified_by_error") == ["f-a", "f-b", "f-c"] and "f-a, f-b, f-c" in report,
        "the ids with no verdict are returned and listed in the report",
    )

    short = _run_sweep(
        root,
        {"effort": "high", "runId": "c3-short", "converge": True},
        {"batches": 3, "verify": "short", "survivors": _THREE_P0},
    )
    sret = short.get("ret") or {}
    _check(
        sret.get("unverified_by_error") == ["f-b"]
        and (sret.get("converge") or {}).get("open_after") == 3,
        "a verify agent that omits a verdict -> that id is unverified-by-error and still open",
    )

    thrown = _run_sweep(
        root,
        {"effort": "high", "runId": "c3-throw"},
        {"batches": 3, "verify": "throw", "survivors": _THREE_P0},
    )
    counts = (thrown.get("ret") or {}).get("counts") or {}
    _check(
        counts.get("unverified") == 3,
        f"single pass, verify agents throw -> counts.unverified == 3 (got {counts.get('unverified')})",
    )

    lost = _run_sweep(
        root,
        {"effort": "high", "runId": "c3-enum", "converge": True},
        {"batches": 3, "enumerate": None, "survivors": _THREE_P0},
    )
    lconv = (lost.get("ret") or {}).get("converge") or {}
    _check(
        lconv.get("converged") is False and lconv.get("open_after") == 3,
        "an enumerate step that returns nothing -> the 3 survivors stay open, no CONVERGED",
    )


# ─── C-7: monitors dropped each new log's first event and flapped across sessions
RUNSTATE_REL = "plugins/ravenclaude-core/monitors/watch-run-state.sh"
SPECTATE_REL = "plugins/ravenclaude-core/monitors/watch-spectate.sh"


def _hook_event(rule: str) -> str:
    return (
        json.dumps(
            {
                "verdict": "deny",
                "hook": "guard-x.sh",
                "tool": "Bash",
                "rule": rule,
                "path": "/secret/p",
            }
        )
        + "\n"
    )


def _append(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line)


def _watch(script: Path, project: Path, steps, session: str | None = None) -> str:
    """Run a monitor against `project`, perform the timed `steps`, return its stdout."""
    out = project / "monitor.out"
    env = dict(os.environ)
    env.update(
        CLAUDE_PROJECT_DIR=str(project),
        RC_MONITOR_POLL_SECONDS="1",
        RC_SPECTATE_MONITOR_POLL_SECONDS="1",
    )
    env.pop("CLAUDE_SESSION_ID", None)
    if session:
        env["CLAUDE_SESSION_ID"] = session
    with out.open("w") as fh:
        proc = subprocess.Popen(
            ["bash", str(script)],
            env=env,
            stdout=fh,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        try:
            time.sleep(1.5)
            for action, pause in steps:
                action()
                time.sleep(pause)
        finally:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except OSError:
                pass
            proc.wait(timeout=10)
    return out.read_text(encoding="utf-8")


def case_c7(root: Path) -> None:
    script = root / RUNSTATE_REL
    # A log already present at startup is joined at its end; a log created after
    # startup is read from line 1, so the event that created it is notified.
    p1 = Path(tempfile.mkdtemp(prefix="c7a-", dir=_TMP))
    _append(p1 / ".ravenclaude/runs/old/hook-events.jsonl", _hook_event("backlog-event"))
    new_log = p1 / ".ravenclaude/runs/sess1/hook-events.jsonl"
    got = _watch(
        script,
        p1,
        [
            (lambda: _append(new_log, _hook_event("first-event")), 3.0),
            (lambda: _append(new_log, _hook_event("second-event")), 2.5),
        ],
    )
    _check("rule: first-event" in got, "the first event of a log created after startup is notified")
    _check("rule: second-event" in got, "later events of that log are notified")
    _check("backlog-event" not in got, "the backlog of the log present at startup is not replayed")
    _check("/secret/p" not in got, "the path field is never echoed")

    # Two concurrent sessions, CLAUDE_SESSION_ID=sessA: only sessA's events, no flapping.
    p2 = Path(tempfile.mkdtemp(prefix="c7b-", dir=_TMP))
    a = p2 / ".ravenclaude/runs/sessA/hook-events.jsonl"
    b = p2 / ".ravenclaude/runs/sessB/hook-events.jsonl"
    steps = []
    for i in range(1, 4):
        steps.append((lambda i=i: _append(a, _hook_event(f"a{i}")), 1.3))
        steps.append((lambda i=i: _append(b, _hook_event(f"b{i}")), 1.3))
    got = _watch(script, p2, steps + [(lambda: None, 1.5)], session="sessA")
    a_hits = [r for r in ("a1", "a2", "a3") if f"rule: {r})" in got]
    b_hits = [r for r in ("b1", "b2", "b3") if f"rule: {r})" in got]
    _check(
        a_hits == ["a1", "a2", "a3"], f"every event of this session's log is notified ({a_hits})"
    )
    _check(b_hits == [], f"no event of the other session's log is notified ({b_hits})")

    # The spectate monitor: a new spectate log's session.start (its creating event) is notified.
    p3 = Path(tempfile.mkdtemp(prefix="c7c-", dir=_TMP))
    spec = p3 / ".ravenclaude/runs/s1/spectate-events.jsonl"
    got = _watch(
        root / SPECTATE_REL,
        p3,
        [
            (
                lambda: _append(
                    spec, json.dumps({"kind": "session.start", "session_id": "s1"}) + "\n"
                ),
                3.0,
            )
        ],
    )
    _check(
        "spectate session.start" in got,
        "watch-spectate: the session.start that created a new log is notified",
    )


# ─── C-8: rc probe dns blamed the probe target when there was no network ─────
# Deterministic resolvers: a PATH holding only the tools the dns probe needs (so dig/host
# on the test machine cannot shadow the branch under test), plus a perl module injected
# with PERL5OPT that makes Socket::getaddrinfo answer per host, and a stub `host`.
PROBE_REL = "plugins/ravenclaude-core/bin/probe-kit.sh"
_STUB_RESOLVER = r"""package RcStubResolver;
use strict;
use warnings;
use Scalar::Util qw(dualvar);
require Socket;
my %mode = map { split /=/, $_, 2 } grep { length } split /,/, ($ENV{RC_STUB_GAI} || "");
my $real = \&Socket::getaddrinfo;
no warnings "redefine";
*Socket::getaddrinfo = sub {
  my $m = $mode{$_[0]} // $mode{"*"} // "real";
  return (dualvar(Socket::EAI_AGAIN(), "Temporary failure in name resolution")) if $m eq "again";
  return (dualvar(Socket::EAI_NONAME(), "Name or service not known")) if $m eq "noname";
  return ("", { family => Socket::AF_INET(), addr => Socket::pack_sockaddr_in(0, Socket::inet_aton("192.0.2.7")) }) if $m eq "ok";
  return $real->(@_);
};
1;
"""
_STUB_HOST = """#!/bin/sh
name="$3"
case "$RC_STUB_HOST" in
  unreach) echo ';; connection timed out; no servers could be reached'; exit 1 ;;
  split)
    if [ "$name" = "$RC_STUB_SUBJECT" ]; then echo "Host $name not found: 3(NXDOMAIN)"; exit 1; fi
    echo "$name has address 192.0.2.7"; exit 0 ;;
esac
exit 9
"""


def _probe_dns(root: Path, bindir: Path, env_extra: dict, *argv: str) -> tuple[int, str]:
    env = {"PATH": str(bindir), "HOME": str(bindir), "NO_COLOR": "1", **env_extra}
    cp = subprocess.run(
        [shutil.which("bash") or "/bin/bash", str(root / PROBE_REL), "dns", *argv],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return cp.returncode, cp.stdout


def case_c8(root: Path) -> None:
    perl = shutil.which("perl")
    awk = shutil.which("awk")
    if not perl or not awk:
        raise _NotRun("perl or awk is not on PATH")
    w = Path(tempfile.mkdtemp(prefix="c8-", dir=_TMP))
    pbin = w / "perl-only"
    pbin.mkdir()
    (pbin / "perl").symlink_to(perl)
    (pbin / "awk").symlink_to(awk)
    (w / "lib").mkdir()
    (w / "lib/RcStubResolver.pm").write_text(_STUB_RESOLVER)
    gai = {"PERL5LIB": str(w / "lib"), "PERL5OPT": "-MRcStubResolver"}

    rc, out = _probe_dns(root, pbin, {**gai, "RC_STUB_GAI": "*=again"}, "somehost.example.org")
    _check(
        rc == 3 and "INCONCLUSIVE" in out,
        f"perl resolver, EAI_AGAIN (no network) -> exit 3 INCONCLUSIVE (got {rc})",
    )
    _check("CONTROL ALSO FAILED" not in out, "... and never 'CONTROL ALSO FAILED'")
    rc, out = _probe_dns(
        root,
        pbin,
        {**gai, "RC_STUB_GAI": "somehost.example.org=noname,example.org=ok"},
        "somehost.example.org",
    )
    _check(
        rc == 1 and "NEGATIVE" in out,
        f"perl resolver, a real NXDOMAIN with a resolving control -> CONFIRMED (got {rc})",
    )

    hbin = w / "host-only"
    hbin.mkdir()
    (hbin / "awk").symlink_to(awk)
    (hbin / "host").write_text(_STUB_HOST)
    (hbin / "host").chmod(0o755)
    rc, out = _probe_dns(root, hbin, {"RC_STUB_HOST": "unreach"}, "somehost.example.org")
    _check(
        rc == 3 and "CONTROL ALSO FAILED" not in out,
        f"host: 'no servers could be reached' -> INCONCLUSIVE (got {rc})",
    )
    rc, out = _probe_dns(
        root,
        hbin,
        {"RC_STUB_HOST": "split", "RC_STUB_SUBJECT": "somehost.example.org"},
        "somehost.example.org",
    )
    _check(
        rc == 1,
        f"host: 'not found: 3(NXDOMAIN)' still reads as a negative, CONFIRMED by control (got {rc})",
    )


CASES = {
    "C-1": case_c1,
    "C-2": case_c2,
    "C-11": case_c11,
    "C-3": case_c3,
    "C-7": case_c7,
    "C-8": case_c8,
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(REPO_ROOT), help="tree to test (default: this checkout)")
    ap.add_argument("--only", default="", help="comma-separated case ids")
    ap.add_argument("--list", action="store_true")
    ns = ap.parse_args(argv)
    if ns.list:
        print("\n".join(CASES))
        return 0
    root = Path(ns.root).resolve()
    wanted = [c.strip() for c in ns.only.split(",") if c.strip()] or list(CASES)
    unknown = [c for c in wanted if c not in CASES]
    if unknown:
        print(f"unknown case id(s): {unknown}", file=sys.stderr)
        return 2
    failed: list[str] = []
    not_run: list[str] = []
    try:
        for cid in wanted:
            print(f"── {cid}")
            try:
                CASES[cid](root)
            except _Fail as exc:
                print(f"    FAIL {exc}")
                failed.append(cid)
            except _NotRun as exc:
                print(f"    NOT RUN {exc} (this is not a pass)")
                not_run.append(cid)
    finally:
        shutil.rmtree(_TMP, ignore_errors=True)
    print(
        f"\n{len(wanted) - len(failed) - len(not_run)} passed, {len(failed)} failed, {len(not_run)} not run"
    )
    if failed:
        return 1
    return 2 if not_run else 0


if __name__ == "__main__":
    os.umask(0o077)
    sys.exit(main())
