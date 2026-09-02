#!/usr/bin/env node
// check-repo-review-converge.mjs
//
// Structural gate for the /repo-review skill's convergence loop
// (workflows/repo-sweep.workflow.js `args.converge` mode). The workflow
// script cannot be executed in CI (it needs the real `Workflow` tool +
// dispatched agents — see the skill's own §6 "Honest status"), so this
// mirrors this repo's established precedent for gating a workflow/dashboard
// script STRUCTURALLY when it cannot be run for real (Gate 51's shell-router
// checker, Gate 144's prompt-builder XSS-floor checker): pure text-based
// assertions over the source, NO `eval`/`new Function` (the security-guidance
// hook's own footgun warning), so this checker can never itself execute
// untrusted content.
//
// What this proves: the convergence loop's SAFETY invariants are present in
// the source — it never proves the loop's runtime behavior (that needs a
// real dispatched run, same honest limit as the rest of this skill).
//
// Usage:
//   node scripts/check-repo-review-converge.mjs [--file <path>]
//   node scripts/check-repo-review-converge.mjs --self-test

import { readFileSync, writeFileSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const DEFAULT_FILE = "plugins/ravenclaude-core/skills/repo-review/workflows/repo-sweep.workflow.js";

function parseArgs(argv) {
  const out = { file: DEFAULT_FILE, selfTest: false };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--file") out.file = argv[++i];
    else if (argv[i] === "--self-test") out.selfTest = true;
  }
  return out;
}

// Each check is {name, test(src) -> boolean}. Pure string/regex matching
// only — never `eval`/`new Function` on the checked source.
const CHECKS = [
  {
    name: "no eval() or new Function() anywhere in the workflow source",
    test: (src) => !/\beval\s*\(/.test(src) && !/new\s+Function\s*\(/.test(src),
  },
  {
    name: "CONVERGE is derived from args.converge === true",
    test: (src) => /CONVERGE\s*=\s*!!\(args\s*&&\s*args\.converge\s*===\s*true\)/.test(src),
  },
  {
    name: "MAX_ITERATIONS is clamped to [1, 20] (Math.min(20, Math.max(1, ...)))",
    test: (src) => /Math\.min\(20,\s*Math\.max\(1,/.test(src),
  },
  {
    name: "AUTOFIX derivation includes CONVERGE (converge implies autofix)",
    test: (src) =>
      /AUTOFIX\s*=\s*!!\(args\s*&&\s*\(args\.autofix\s*===\s*true\s*\|\|\s*CONVERGE\)\)/.test(src),
  },
  {
    name: "the real severity vocabulary is used (blocking/major/minor/nit), not the old mismatched one",
    test: (src) =>
      /SEVERITY_RANK\s*=\s*\{\s*blocking:\s*0,\s*major:\s*1,\s*minor:\s*2,\s*nit:\s*3\s*\}/.test(
        src,
      ),
  },
  {
    name: "the old mismatched severity vocabulary (critical/high/medium/low) is gone",
    test: (src) => !/critical:\s*0,\s*high:\s*1,\s*medium:\s*2,\s*low:\s*3/.test(src),
  },
  {
    name: "single-pass exit: `if (!CONVERGE) break;` unconditionally stops after iteration 1",
    test: (src) => /if\s*\(!CONVERGE\)\s*break;/.test(src),
  },
  {
    name: "convergence exit 1/3: converged when openAfterCount === 0",
    test: (src) => /openAfterCount\s*===\s*0\s*\)\s*\{\s*\n\s*converged\s*=\s*true;/.test(src),
  },
  {
    name: "convergence exit 2/3: stops at MAX_ITERATIONS without claiming success",
    test: (src) => /iteration\s*>=\s*MAX_ITERATIONS\s*\)\s*\{/.test(src),
  },
  {
    name: "convergence exit 3/3: plateau when appliedTotal === 0 (no infinite loop on stuck findings)",
    test: (src) => /appliedTotal\s*===\s*0\s*\)\s*\{\s*\n\s*plateaued\s*=\s*true;/.test(src),
  },
  {
    name: "convergence-honesty contract: CONVERGED line only on real 0-open",
    test: (src) => /CONVERGED — 0 open P0-P3 finding\(s\) remain/.test(src),
  },
  {
    name: "convergence-honesty contract: plateau is reported, never silently absorbed",
    test: (src) => /NOT CONVERGED — plateaued after/.test(src),
  },
  {
    name: "convergence-honesty contract: max-iterations-hit is reported, never silently absorbed",
    test: (src) => /NOT CONVERGED — hit convergeMaxIterations/.test(src),
  },
  {
    name: "openAfterCount is never allowed to go negative (Math.max(0, ...))",
    test: (src) => /Math\.max\(0,\s*counts\.confirmed\s*-\s*appliedTotal\)/.test(src),
  },
];

function runChecks(src) {
  const results = CHECKS.map((c) => ({ name: c.name, pass: c.test(src) }));
  const failed = results.filter((r) => !r.pass);
  return { results, ok: failed.length === 0 };
}

function report(results) {
  for (const r of results) {
    console.log(`  ${r.pass ? "✓" : "✗"} ${r.name}`);
  }
}

function main() {
  const { file, selfTest } = parseArgs(process.argv.slice(2));

  if (!selfTest) {
    const src = readFileSync(file, "utf8");
    const { results, ok } = runChecks(src);
    console.log(`── check-repo-review-converge.mjs — ${file} ──`);
    report(results);
    if (!ok) {
      console.error(`\nFAILED: ${results.filter((r) => !r.pass).length} check(s) did not pass.`);
      process.exit(1);
    }
    console.log("\nOK: all convergence-loop structural checks passed.");
    process.exit(0);
  }

  // ── --self-test: real file must pass every check; a mutant with the
  // plateau-break stripped (the exact shape that would silently infinite-
  // loop or drop the "remaining findings need human review" honesty line)
  // must FAIL — proving these checks have teeth, not just that they run.
  let failures = 0;
  const check = (name, cond) => {
    console.log(`[${cond ? "ok" : "FAIL"}] ${name}`);
    if (!cond) failures += 1;
  };

  const realSrc = readFileSync(DEFAULT_FILE, "utf8");
  const { ok: realOk, results: realResults } = runChecks(realSrc);
  check("real workflow file passes every structural check", realOk);
  if (!realOk) report(realResults);

  const tmp = mkdtempSync(join(tmpdir(), "repo-review-converge-"));
  try {
    // Mutant 1: strip the plateau-detection branch entirely — the shape a
    // careless refactor could produce (silently loops until MAX_ITERATIONS
    // even when nothing more can ever be fixed, burning the whole budget on
    // a repo that will never converge).
    const mutantPath = join(tmp, "mutant.workflow.js");
    const mutated = realSrc.replace(
      /if\s*\(appliedTotal\s*===\s*0\)\s*\{\s*\n\s*plateaued\s*=\s*true;[\s\S]*?\n\s*\}\n/,
      "// plateau detection removed by mutant\n",
    );
    if (mutated === realSrc) {
      check("mutant 1 actually changed the source (regex matched something)", false);
    } else {
      writeFileSync(mutantPath, mutated, "utf8");
      const { ok: mutantOk } = runChecks(mutated);
      check("mutant 1 (plateau detection stripped) is CAUGHT — checks must fail on it", !mutantOk);
    }

    // Mutant 2: revert to the old mismatched severity vocabulary — proves
    // the regression guard (check 6) actually depends on the fix, not just
    // co-exists with it.
    const mutant2Path = join(tmp, "mutant2.workflow.js");
    const mutated2 = realSrc.replace(
      "const SEVERITY_RANK = { blocking: 0, major: 1, minor: 2, nit: 3 };",
      "const SEVERITY_RANK = { critical: 0, high: 1, medium: 2, low: 3 };",
    );
    if (mutated2 === realSrc) {
      check("mutant 2 actually changed the source (string replace matched)", false);
    } else {
      writeFileSync(mutant2Path, mutated2, "utf8");
      const { ok: mutant2Ok } = runChecks(mutated2);
      check(
        "mutant 2 (old mismatched severity vocabulary restored) is CAUGHT — checks must fail on it",
        !mutant2Ok,
      );
    }
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }

  console.log(`\n${failures === 0 ? "ALL PASS" : `${failures} FAILED`}: ${failures} failing`);
  process.exit(failures === 0 ? 0 : 1);
}

main();
