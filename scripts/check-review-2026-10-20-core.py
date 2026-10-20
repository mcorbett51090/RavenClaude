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
import subprocess
import sys
import tempfile
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
  if (label === "verify:enumerate") return { findings: survivors };
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


CASES = {
    "C-1": case_c1,
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
