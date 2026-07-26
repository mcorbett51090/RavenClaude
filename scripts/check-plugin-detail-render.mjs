#!/usr/bin/env node
/* check-plugin-detail-render.mjs — Gate 141: the H4 "zero content loss" oracle
 * for the P2 detail-field islanding (plan §1.4).
 *
 * P2 moves the detail-only fields read SOLELY by window.__openPlugin —
 * agents[].scenarios/.quickstart/.works_with and plugins[].scripts_index /
 * .scenarios_index / .templates_index / .best_practices_index — out of the eager
 * window.__RC_DATA__ blob into a lazy island (<script type="application/json"
 * id="plugin-detail-payload">). The hazard (H4) is that __openPlugin can then
 * count `(p.scripts_index||[]).length` and `.filter(s => s.body)` on data that is
 * NOT hydrated yet — whole sections vanish with ZERO count and NO error, invisible
 * to any render-only / no-console-errors test. THIS gate is the DoD for "zero
 * content loss": it re-derives the nine section counts structurally (no eval, like
 * the sibling check-*-render.mjs gates) from the freshly-rendered $IDX_HTML.
 *
 * KEY PRESENCE is the hydration sentinel (plan §1.4): the eager record must NOT
 * carry the islanded keys at all (absent == not hydrated), the island record MUST
 * carry all four (present == hydrated; [] == genuinely zero — 77 plugins really
 * have scripts_index: [], so "assert non-empty" would be wrong on 46% of them).
 *
 * Usage: node scripts/check-plugin-detail-render.mjs [path/to/index.html]
 */
import { readFileSync } from "node:fs";

const htmlPath = process.argv[2] || "index.html";
const html = readFileSync(htmlPath, "utf8");

let failures = 0;
function ok(cond, msg) {
  if (cond) console.log("  ✓ " + msg);
  else {
    console.log("  ✗ " + msg);
    failures++;
  }
}
function fatal(msg) {
  console.log("  ✗ " + msg);
  console.log(`\nplugin-detail render: FAILED (${failures + 1} assertion(s))`);
  process.exit(1);
}

const ISLANDED_PLUGIN_KEYS = [
  "scripts_index",
  "scenarios_index",
  "templates_index",
  "best_practices_index",
];
const ISLANDED_AGENT_KEYS = ["scenarios", "quickstart", "works_with"];

/* ── The committed ravenclaude-core baseline — the ONLY plugin of 167 with all
 * eight data-backed sections non-empty, so it is the sole valid must-pass
 * fixture. Altering any one of these is must-fail (c). ─────────────────────── */
const RC = "ravenclaude-core";
const RC_BASELINE = {
  agents: 15,
  skills: 48,
  tools: 17,
  scenarios: 4,
  hooks: 22,
  rules: 5,
  templates: 23,
  practices: 34,
  trees: 4,
};

/* ── Extract the detail island (must exist, must parse). Renaming its id — the
 * literal H4 scenario, must-fail (a) — makes this regex miss and the gate red. ── */
const islandM = html.match(
  /<script type="application\/json" id="plugin-detail-payload">([\s\S]*?)<\/script>/,
);
if (!islandM) {
  fatal(
    "detail island <script type=application/json id=plugin-detail-payload> not found " +
      "(renamed/removed id → the H4 hydration break)",
  );
}
let island;
try {
  island = JSON.parse(islandM[1]);
} catch (e) {
  fatal("detail island is not valid JSON → __openPlugin would render NOTHING: " + e.message);
}
ok(island && typeof island.plugins === "object", "island parses to { plugins: {…} }");

/* ── The shell's hydrateDetail must reference the SAME element id — catches the
 * mirror of must-fail (a): the JS lookup renamed while the element is intact. ── */
ok(
  html.includes('getElementById("plugin-detail-payload")'),
  "shell hydrateDetail() looks up the island by its committed id",
);

/* ── Extract the eager __RC_DATA__ blob (now sharing the shell <script>). ────── */
const eagerM = html.match(
  /window\.__RC_DATA__ = ([\s\S]*?);\s*\n\s*const D = window\.__RC_DATA__;/,
);
if (!eagerM) fatal("eager window.__RC_DATA__ assignment not found");
let eager;
try {
  eager = JSON.parse(eagerM[1]);
} catch (e) {
  fatal("eager window.__RC_DATA__ is not valid JSON: " + e.message);
}
ok(Array.isArray(eager.plugins), "eager __RC_DATA__ parses with a plugins[] array");

const eagerByName = {};
for (const p of eager.plugins) eagerByName[p.name] = p;

/* ── Decision-tree count for a plugin from the hidden #dt-store (trees section). */
function treeCount(name) {
  const re = new RegExp(
    'class="dt-item" data-plugin="' + name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + '"',
    "g",
  );
  return (html.match(re) || []).length;
}

/* ══ MUST-PASS 1: ravenclaude-core renders all nine sections from the island +
 * eager blob, each at its committed baseline count, and sectionDefs.length === 9. */
const erc = eagerByName[RC];
const irc = island.plugins[RC];
ok(!!erc, `eager blob carries the ${RC} record`);
ok(!!irc, `island carries the ${RC} record`);
if (erc && irc) {
  const nine = {
    agents: (erc.agents || []).length,
    skills: (erc.skills_index || []).length,
    tools: (irc.scripts_index || []).length,
    scenarios: (irc.scenarios_index || []).length,
    hooks: (erc.hooks_index || []).length,
    rules: (erc.rules_index || []).length,
    templates: (irc.templates_index || []).length,
    practices: (irc.best_practices_index || []).length,
    trees: treeCount(RC),
  };
  for (const k of Object.keys(RC_BASELINE)) {
    ok(
      nine[k] === RC_BASELINE[k],
      `${RC} section "${k}": ${nine[k]} === baseline ${RC_BASELINE[k]}`,
    );
  }
  const nonEmpty = Object.values(nine).filter((n) => n > 0).length;
  ok(nonEmpty === 9, `${RC} has all 9 data-backed sections non-empty → sectionDefs.length === 9`);
  // The eager count fields for the agents section must agree with the eager list.
  ok(
    erc.counts && erc.counts.agents === nine.agents,
    `${RC} counts.agents agrees (${nine.agents})`,
  );
}

/* ══ MUST-PASS 2: a plugin with a GENUINELY-empty islanded section renders that
 * section ABSENT (empty body → filtered out) with NO error thrown — i.e. the key
 * is PRESENT and [] (hydrated, genuine zero), and counts.tools === 0. ────────── */
const emptyOne = eager.plugins.find((p) => {
  const rec = island.plugins[p.name];
  return rec && Array.isArray(rec.scripts_index) && rec.scripts_index.length === 0;
});
ok(!!emptyOne, "found a plugin with a genuinely-empty islanded section (scripts_index: [])");
if (emptyOne) {
  const rec = island.plugins[emptyOne.name];
  ok(
    Object.prototype.hasOwnProperty.call(rec, "scripts_index") && rec.scripts_index.length === 0,
    `${emptyOne.name}: scripts_index is PRESENT and [] (hydrated, genuine zero — not "unhydrated")`,
  );
  ok(
    emptyOne.counts.tools === 0,
    `${emptyOne.name}: counts.tools === 0 so the Tools section is absent, not errored`,
  );
}

/* ══ Key-presence sentinel: the eager blob must NOT carry any islanded key (that
 * absence is the sentinel), and every island record MUST carry all four. ─────── */
let eagerLeak = 0;
let islandMissing = 0;
let agentLeak = 0;
for (const p of eager.plugins) {
  for (const k of ISLANDED_PLUGIN_KEYS) if (k in p) eagerLeak++;
  for (const a of p.agents || []) for (const k of ISLANDED_AGENT_KEYS) if (k in a) agentLeak++;
  const rec = island.plugins[p.name];
  if (!rec || !ISLANDED_PLUGIN_KEYS.every((k) => k in rec)) islandMissing++;
}
ok(eagerLeak === 0, `no islanded plugin key leaked into the eager blob (found ${eagerLeak})`);
ok(agentLeak === 0, `no islanded agent subfield leaked into the eager blob (found ${agentLeak})`);
ok(
  islandMissing === 0,
  `every eager plugin has an island record with all 4 keys (missing ${islandMissing})`,
);

/* ══ Completeness (must-fail b): the island plugin set === the eager plugin set.
 * Deleting one plugin's island record is caught here. ───────────────────────── */
const eagerNames = new Set(eager.plugins.map((p) => p.name));
const islandNames = new Set(Object.keys(island.plugins));
const orphans = [...eagerNames].filter((n) => !islandNames.has(n));
ok(
  orphans.length === 0,
  `no eager plugin is missing from the island (orphans: ${orphans.join(",") || "none"})`,
);

/* ══ Free secondary invariant (measured: 0 mismatches / 167): eager counts agree
 * with hydrated index lengths for tools + scenarios. Also a must-fail (c) tripwire. */
let invMismatch = 0;
for (const p of eager.plugins) {
  const rec = island.plugins[p.name];
  if (!rec) continue;
  if (p.counts.tools !== (rec.scripts_index || []).length) invMismatch++;
  if (p.counts.scenarios !== (rec.scenarios_index || []).length) invMismatch++;
}
ok(
  invMismatch === 0,
  `counts.tools/scenarios === island index length across all plugins (mismatches: ${invMismatch})`,
);

console.log("");
if (failures === 0) {
  console.log("plugin-detail render: ALL ASSERTIONS PASS");
  process.exit(0);
}
console.log(`plugin-detail render: ${failures} assertion(s) FAILED`);
process.exit(1);
