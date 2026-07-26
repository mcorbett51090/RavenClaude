#!/usr/bin/env node
/* check-shell-router.selftest.mjs — the EXTERNAL teeth-check for
 * check-shell-router.mjs (Gate 51's shell-router half).
 *
 * WHY THIS EXISTS (FORGE dashboard-consumption, PB-3). check-shell-router.mjs
 * used to carry its own "must-fail halves" INLINE: it built a hardcoded bad
 * string (`navBad`/`aliasBad`/`chromeBad`) and tested it against the SAME
 * expectation the real assertion uses — it never re-invoked itself against a
 * mutated render. That block certified nothing: a weakened re-authoring of the
 * gate passed its own self-test (reproduced: the real SECTION_ALIAS assertion
 * replaced with `assert(true)` still printed "all three must-fail checks
 * detected" against an index.html with SECTION_ALIAS genuinely emptied). Gate 51
 * is deliberately re-authored in the same commit as the IA re-cut, so it needs a
 * verifier the IA commit CANNOT silently weaken.
 *
 * WHAT IT DOES. Takes a freshly-rendered index.html, applies three STRUCTURAL,
 * anchor-agnostic mutations (empty SECTION_ALIAS; rename the first NAV id at its
 * definition; strip the #dash-root chrome-hide rule), writes each to a temp copy,
 * and spawns `check-shell-router.mjs <copy>` as a SUBPROCESS, asserting a
 * NON-ZERO exit for each. If any mutation leaves the checker green, the checker
 * is BLIND to that mutation → this selftest exits non-zero and names it.
 *
 * Because the mutations are structural (they locate SECTION_ALIAS / the NAV
 * literal / the chrome-hide CSS by shape, not by a hardcoded id), the driver
 * needs NO edit across the 6→N IA re-cut — which is exactly the property that
 * lets a reviewer confirm a re-authored gate is at least as strong: this file is
 * UNCHANGED in the IA commit's diff, and it still trips the re-authored checker.
 *
 * A mutation that fails to CHANGE the source is itself a selftest failure (loud)
 * — a no-op mutation is the silent-teeth trap this file exists to kill.
 *
 * Usage:
 *   node scripts/check-shell-router.selftest.mjs [path/to/index.html]
 *   node scripts/check-shell-router.selftest.mjs --checker <alt-checker.mjs> [index.html]
 *
 * The --checker override exists ONLY for the audit-gates must-fail half, which
 * points this driver at a deliberately-weakened copy of check-shell-router.mjs
 * and asserts THIS selftest then fails — proving the selftest's own teeth.
 */
import { readFileSync, writeFileSync, mkdtempSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { tmpdir } from "node:os";
import { join } from "node:path";

/* ── args ─────────────────────────────────────────────────────────────── */
let checker = "scripts/check-shell-router.mjs";
let indexPath = "index.html";
{
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--checker") checker = argv[++i];
    else indexPath = argv[i];
  }
}

const src = readFileSync(indexPath, "utf8");
const tmp = mkdtempSync(join(tmpdir(), "shell-router-selftest-"));

/* ── the three structural mutations ───────────────────────────────────────
 * Each returns the mutated source. Each MUST change `src` — a mutation that
 * silently matches nothing is a selftest failure, not a pass. SECTION_ALIAS is
 * a flat string→string map (no nested braces), so a non-greedy `{…}` match to
 * the first `}` is exact. The NAV literal DOES nest braces, so we rename only
 * the first `id: "…"` occurrence inside it. The chrome-hide rule is matched by
 * the same shape check-shell-router.mjs's CHROME_HIDE_RE uses, consumed to its
 * closing brace so the gate's regex can no longer match. */
const mutations = [
  {
    name: "empty SECTION_ALIAS",
    trips: "the SECTION_ALIAS back-compat / alias-target assertions",
    mutate(s) {
      return s.replace(/const SECTION_ALIAS = \{[\s\S]*?\}/, "const SECTION_ALIAS = {}");
    },
  },
  {
    name: "rename the first NAV id",
    trips: "the NAV-section presence assertion",
    mutate(s) {
      const navStart = s.indexOf("const NAV = [");
      if (navStart === -1) return s; // no change → caught as a no-op failure below
      // Rename only the FIRST `id: "X"` after the NAV opener (anchor-agnostic:
      // works for whatever the current NAV's first section id is).
      const head = s.slice(0, navStart);
      const rest = s.slice(navStart);
      const renamed = rest.replace(/id:\s*"([^"]+)"/, (m, id) => m.replace(id, id + "_MUT"));
      return head + renamed;
    },
  },
  {
    name: "strip the #dash-root chrome-hide rule",
    trips: "the single-chrome (Slice B) assertion",
    mutate(s) {
      return s.replace(
        /#dash-root \.cat-bar,\s*#dash-root \.tab-bar\s*\{[^}]*\}/,
        "/* chrome-hide removed */",
      );
    },
  },
];

/* ── run each mutation through the REAL checker as a subprocess ─────────── */
const failures = [];
let i = 0;
for (const m of mutations) {
  const mutated = m.mutate(src);
  if (mutated === src) {
    failures.push(
      `mutation "${m.name}" changed nothing — the anchor is gone or the shape drifted; ` +
        `a no-op mutation cannot prove teeth (fix the mutation, do not ignore it)`,
    );
    continue;
  }
  const copy = join(tmp, `mutated-${i++}.html`);
  writeFileSync(copy, mutated, "utf8");
  const r = spawnSync("node", [checker, copy], { encoding: "utf8" });
  const rc = r.status;
  if (rc === 0) {
    failures.push(
      `checker "${checker}" stayed GREEN on mutation "${m.name}" — it is BLIND to it ` +
        `(should trip ${m.trips}). This is the self-certifying-gate failure PB-3 exists to catch.`,
    );
  }
}

if (failures.length) {
  console.error("FAIL: shell-router selftest — the checker's teeth are not proven:");
  for (const f of failures) console.error("  - " + f);
  process.exit(1);
}
console.log(
  `OK: shell-router selftest — all three structural mutations (SECTION_ALIAS, NAV id, chrome-hide) ` +
    `independently trip ${checker} as a subprocess; the gate's teeth are externally proven.`,
);
