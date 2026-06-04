#!/usr/bin/env node
/* check-dispatch-evaluator-floor.mjs — Gate 52 (agent-dispatch-evaluator Phase 2)
 *
 * Guards the HARD INVARIANT of the Phase-2 workflow integration:
 *
 *   With dispatch-config absent OR enabled:false (the default), every
 *   `evaluatedAgent(prompt, opts, dispatchCfg)` call must pass `opts` through
 *   to the underlying `agent(prompt, opts)` BYTE-IDENTICALLY — no model
 *   mutation, no added/removed keys, no copy. The disabled path is the
 *   regression floor: it must be indistinguishable from the unwrapped baseline.
 *
 * Technique (mirrors Gate 35 check-dashboard-roundtrip.mjs + Gate 51's
 * structural-extraction discipline): extract the REAL copied wrapper block from
 * .claude/workflows/rc-deep-research.js (the BEGIN/END provenance fence), wrap
 * it in a tiny ESM module written to a temp file, and `import()` it (NO
 * `new Function()` / NO `eval` — per the security-guidance footgun warning;
 * dynamic import of extracted code is the safe execution path). A stub `agent()`
 * records what the wrapper forwards; we assert the recorded opts is the SAME
 * object reference the caller passed (the strongest form of byte-identical: no
 * clone happened on the disabled path). The input source is our own committed
 * workflow artifact (trusted, same-org).
 *
 * Bidirectional:
 *   (a) must-pass — the real workflow's wrapper preserves opts on the disabled
 *       path (and on the undefined-config guard).
 *   (b) must-fail — an inline mutant whose disabled short-circuit mutates
 *       opts.model is CAUGHT by the same assertion (proves the gate has teeth).
 *
 * Usage: node scripts/check-dispatch-evaluator-floor.mjs [path/to/rc-deep-research.js]
 */
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const wfPath = process.argv[2] || ".claude/workflows/rc-deep-research.js";
const src = readFileSync(wfPath, "utf8");

const BEGIN = "BEGIN copied block — agent-dispatch-evaluator wrapper";
const END = "END copied block — agent-dispatch-evaluator wrapper";

function extractWrapperBlock(text) {
  const b = text.indexOf(BEGIN);
  const e = text.indexOf(END);
  if (b === -1 || e === -1 || e <= b) {
    throw new Error(
      "could not locate the copied-wrapper provenance fence (BEGIN/END markers) — " +
        "the Phase-2 wrapper block is missing or its provenance comment was removed",
    );
  }
  const afterBegin = text.indexOf("\n", b);
  const beforeEnd = text.lastIndexOf("\n", e);
  return text.slice(afterBegin + 1, beforeEnd);
}

const TMP = mkdtempSync(join(tmpdir(), "gate52-"));
let modCounter = 0;

/* Write the extracted wrapper block (plus recording stubs) to a temp ESM module
 * and import it. The wrapper closes over `agent`, `log`, and (in
 * _appendAuditLog) `args` — declared as benign stubs in the module body.
 * `__calls` is exported so the test can inspect what the wrapper forwarded. */
async function loadEvaluatedAgent(blockSrc) {
  const file = join(TMP, `wrapper-${modCounter++}.mjs`);
  const mod = `
const __calls = [];
function agent(prompt, opts) {
  __calls.push({ prompt, opts });
  return Promise.resolve("STUB_RESULT");
}
function log() {}
const args = { _sessionId: "gate52" };

${blockSrc}

export { evaluatedAgent, __calls };
`;
  writeFileSync(file, mod, "utf8");
  return import(pathToFileURL(file).href);
}

let pass = 0;
let fail = 0;
const note = (ok, msg) => {
  if (ok) {
    pass++;
    console.log(`  ✓ ${msg}`);
  } else {
    fail++;
    console.log(`  ✗ ${msg}`);
  }
};

/* Core assertion: on the disabled / undefined-config path, evaluatedAgent must
 * forward the SAME opts object reference it received (no mutation, no clone). */
async function assertFloorPreservesOpts(evaluatedAgent, calls, dispatchCfg, label) {
  calls.length = 0;
  const baselineOpts = {
    label: "scope",
    schema: { type: "object" },
    model: "claude-sonnet-4-6",
    _run_config_phase: "scope",
  };
  const snapshot = JSON.stringify(baselineOpts);
  await evaluatedAgent("a prompt", baselineOpts, dispatchCfg);

  if (calls.length !== 1) {
    note(false, `${label}: expected exactly one agent() call, saw ${calls.length}`);
    return;
  }
  const forwarded = calls[0].opts;
  note(
    forwarded === baselineOpts,
    `${label}: opts forwarded by reference (no clone on disabled path)`,
  );
  note(
    JSON.stringify(baselineOpts) === snapshot,
    `${label}: opts not mutated in place (model/keys unchanged)`,
  );
  note(
    forwarded.model === "claude-sonnet-4-6",
    `${label}: opts.model is byte-identical to baseline`,
  );
  note(calls[0].prompt === "a prompt", `${label}: prompt forwarded unchanged`);
}

async function main() {
  console.log("── Gate 52: agent-dispatch-evaluator disabled-floor (byte-identical opts) ──");

  const block = extractWrapperBlock(src);
  note(/async function evaluatedAgent\(/.test(block), "wrapper block exports evaluatedAgent()");
  note(
    /if \(!dispatchCfg\.enabled\) return agent\(prompt, opts\);/.test(block),
    "wrapper has the enabled:false short-circuit (return agent(prompt, opts))",
  );

  // ── must-pass half: the real workflow wrapper ──────────────────────────────
  const real = await loadEvaluatedAgent(block);
  await assertFloorPreservesOpts(
    real.evaluatedAgent,
    real.__calls,
    { enabled: false, mode: "shadow" },
    "disabled-config",
  );
  await assertFloorPreservesOpts(real.evaluatedAgent, real.__calls, undefined, "undefined-config");

  // ── must-fail half: a mutant whose disabled path mutates opts.model ─────────
  const mutantBlock = block.replace(
    "if (!dispatchCfg.enabled) return agent(prompt, opts);",
    'if (!dispatchCfg.enabled) { opts = { ...opts, model: "claude-haiku-4-5-20251001" }; return agent(prompt, opts); }',
  );
  if (mutantBlock === block) {
    note(false, "must-fail: could not construct the mutant (short-circuit line not found)");
  } else {
    const mutant = await loadEvaluatedAgent(mutantBlock);
    mutant.__calls.length = 0;
    const opts = { label: "scope", model: "claude-sonnet-4-6" };
    await mutant.evaluatedAgent("p", opts, { enabled: false });
    const forwarded = mutant.__calls[0]?.opts;
    const mutated = forwarded !== opts || forwarded?.model === "claude-haiku-4-5-20251001";
    note(
      mutated,
      "must-fail teeth: a mutant that rewrites opts.model on the disabled path is detected",
    );
  }

  console.log(`  ── Gate 52 result: ${pass} passed, ${fail} failed ──`);
  rmSync(TMP, { recursive: true, force: true });
  if (fail > 0) process.exit(1);
}

main().catch((e) => {
  console.error("Gate 52 ERROR:", e.message);
  rmSync(TMP, { recursive: true, force: true });
  process.exit(2);
});
