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
 * fixture. Altering any one of these is must-fail (c).
 * D1 (2026-08-13): this object is a deliberate hand-maintained golden. Do not
 * de-hardcode it from scan_repo — that is the forbidden tautology. ────────── */
const RC = "ravenclaude-core";
const RC_BASELINE = {
  agents: 15,
  skills: 57, // 56 -> 57: skills/analog-closeness-scorecard (Q2, analog-repos-gap-fill leftovers)
  //        55 -> 56: skills/cheap-lane-delegation (route everyday work to Grok)
  //        54 -> 55: skills/authoring-org-skills (org-skill studio, Phase 5)
  //        53 -> 54: skills/session-handoff (v0.266.0, context-quality reset)
  //        52 -> 53: skills/design-clone (v0.253.0, design-schema capture+apply)
  //        51 -> 52: skills/github-gold-standard (v0.246.0, the gold-standard scorecard)
  tools: 41, // 38 -> 41 AT MERGE (#1025 <- origin/main after #1023): this
  //   branch's cause-taxonomy tools (38 on forge/vba-impl) PLUS the three
  //   stall-watchdog scripts that landed on main via #1023 (stall_watch.py +
  //   stall_reach.py + install_stall_watch.py). COUNTED, not inferred: _scan_scripts
  //   globs 41 *.py in plugins/ravenclaude-core/scripts/. grok-delegate.sh is bash,
  //   so the *.py glob does not count it; test-stall-watch.py lives in hooks/tests/,
  //   not scripts/, so it is not counted either.
  //        37 -> 38: route-task.py (the cheap-lane deterministic router, merged
  //   in from origin/main's cheap-lane-agnostic work; grok-delegate.sh is bash, so
  //   _scan_scripts's *.py glob does not count it).
  //        35 -> 37: check-scope-key-parity.py + audit-fired-count.py
  //   (verify-before-assert Phase 10 — anti-rot. The parity check guards a block
  //   duplicated in FIVE live files where drift is a silent pass, not a bug; the
  //   fired-count audit carries both G10.1 controls so "no events" can never be
  //   read as "clean"). COUNTED on this tree.
  //        34 -> 35: check-cause-eval.py (verify-before-assert Phase 9 — the
  //   OUTCOME eval; it is the gate that found the plan's own ship gate to be
  //   unsatisfiable under its natural reading). COUNTED on this tree.
  //        32 -> 34: build-outcome-corpus.py + replay-outcome-rules.py
  //   (verify-before-assert Phase 1 — the offline replay corpus and the rule
  //   measurement harness). COUNTED on this tree, not inferred: the sibling
  //   preflight-command-review.sh lands in `hooks` below rather than here,
  //   because hooks.json registers it, so +3 files is +2 tools and +1 hook.
  //        30 -> 32: set_conservation.py + ledger.py (task-ledger Phases 0-2).
  //   set_conservation.py is the SSOT Set-Conservation Primitive, shared with the
  //   sibling verify-before-assert run (set_kind in {open_items, causes}); ledger.py
  //   is the append primitive + the projection. COUNTED on this tree, not inferred.
  //   ⛔ RECONCILED ACROSS TWO PRs: this branch was authored against a base of 29 and
  //   said 31, but #991 landed cause_taxonomy.py first and moved the base to 30. Each
  //   branch's number was correct in isolation and wrong after the other merged —
  //   taking either side verbatim would have set a silently wrong ratchet that still
  //   passes on its own branch. 30 + 2 = 32.
  //        29 -> 30: cause_taxonomy.py (the SSOT cause grammar, #991)
  //        26 -> 27: load-substrate-tier-map.py (v0.270.0)
  //         27 -> 29: conserve-tokens.py + parallelism-detector.py (v0.273.0)
  //        25 -> 26: handoff-successor-ack.py (v0.269.0)
  //        22 -> 25: context-usage-meter.py + context-handoff.py + handoff-nudge.py
  //                  (v0.266.0, session-context handoff)
  //        18 -> 19: scripts/compact-anchor.py (v0.245.0, the SessionStart(compact) pointer)
  //        19 -> 22: premise-gate.py + classify_claim.py + check-design-schema.py
  //                  (v0.263.0, PR 3b packaging move)
  scenarios: 4,
  hooks: 43, // 42 -> 43: guard-foreground-suite.sh WIRED on PreToolUse(Bash), merged
  //   in from origin/main — denies a foreground full-suite run that cannot finish
  //   inside the 600s Bash-tool ceiling.
  //        41 -> 42: guard-cause-closure.sh WIRED on PreToolUse(Write|Edit|
  //   MultiEdit) — verify-before-assert Phase 6, the SECOND fail-closed surface,
  //   shipping at `warn`. Same scripts/-plus-`bash` packaging as its siblings.
  //        40 -> 41: guard-remediation-cause.sh WIRED on PreToolUse(Bash) —
  //   verify-before-assert Phase 5, THE PRIMARY D1 GATE, shipping at `warn`. Same
  //   scripts/-plus-`bash` packaging as its sibling below, for the same reason.
  //        39 -> 40: preflight-command-review.sh WIRED on PreToolUse(Bash) —
  //   verify-before-assert Phase 4, WARN-only, one measured rule (R-3). It is a
  //   REGISTRATION, which is what this count tracks; the body lives under scripts/
  //   and is invoked via `bash` because the tribunal substrate guard denies setting
  //   the executable bit on a new hooks/*.sh, so it does NOT also raise `tools`.
  //        38 -> 39: keep-awake.sh WIRED on SessionStart — an opt-in sleep assertion
  //   (`keep_awake` in comfort-posture.yaml, shipped default off) so a closed lid cannot
  //   silently suspend a session. It is a REGISTRATION, which is what this count tracks,
  //   even though it is excluded from the Pipeline map as host-environment hygiene rather
  //   than an agent guardrail — the two lists answer different questions.
  // 37 -> 38: triage-outcome.sh WIRED on PostToolUse(Bash) after its fire
  //   rate was measured down to 2.588% over a 46,557-envelope replay corpus (the
  //   gate is 3%). ⛔ This count tracks WIRED hooks, not hook FILES: the file
  //   itself landed earlier and moved no count, because it shipped deliberately
  //   absent from the wiring. The ratchet reddening on the wiring commit — and
  //   only on it — is the gate behaving exactly as intended.
  //        36 -> 37: ask-on-ambiguity (v0.281.0, UserPromptSubmit advisory nudge).
  //   ⛔ Both hooks land in the SAME count and each side of the v0.281.0 rebase
  //   claimed 36 on its own: guard-probe-validity.sh took main 35 -> 36, and
  //   ask-on-ambiguity takes it 36 -> 37. Keeping either side's literal `36` would
  //   have left this constant one short of reality while reading as clean.
  //   COUNTED, not inferred: hooks.json on this tree holds 37 registrations.
  //   NOTE the counting rule, because it misled once: _scan_hooks() in
  //   generate-index-dashboard.py indexes hooks.json REGISTRATIONS, not files on
  //   disk. A stray .sh in hooks/ does not move this number and a registration
  //   whose body lives elsewhere does. ask-on-ambiguity's body is under scripts/
  //   (the tribunal substrate guard denies chmod +x on a new hooks/ file, and a
  //   non-executable hooks/*.sh hard-fails CI), so it is registered as
  //   `bash "${CLAUDE_PLUGIN_ROOT}/scripts/ask-on-ambiguity.sh"` and Path().stem
  //   still renders it as `ask-on-ambiguity` — verified, not assumed.
  //        35 -> 36: guard-probe-validity.sh (v0.273.0, the pv.grep-v-quiet advisory)
  //        34 -> 35: handoff-successor-ack.sh (v0.269.0, SessionStart handshake)
  //        33 -> 34: sanitize-webfetch-output.sh (v0.267.0, WebFetch result quarantine)
  //        32 -> 33: handoff-nudge.sh (v0.266.0, Stop context-hot nudge)
  //        26 -> 28: log-probe.sh + guard-premise.sh (v0.240.0, the premise gate);
  //        28 -> 29: guard-memory-compaction.sh (v0.241.0, the Rule-4 control);
  //        29 -> 30: compact-anchor.sh (v0.245.0, the post-compaction addressability pointer)
  //        30 -> 31: enforce-git-protocol.sh (v0.246.0, the in-loop git-protocol hook)
  //        31 -> 32: enforce-portability.sh (v0.255.0, the in-loop macOS-portability lint)
  rules: 5,
  templates: 25, // 24 -> 25: templates/ledger/ (task-ledger Phase 0 — the event +
  //        config JSON Schemas). Top-level scan only, so the TWO schema files
  //        inside that dir increment this by one, not by two — the same rule the
  //        worktree-lane note below records.
  //        23 -> 24: templates/worktree-lane/ (v0.268.0, one-window lane pack)
  //        (top-level scan only — the three files inside that dir do not increment)
  practices: 38,
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
