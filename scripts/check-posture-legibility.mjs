#!/usr/bin/env node
/* check-posture-legibility.mjs — Gate 138 (P5a).
 *
 * Operators conflate permission categories (allow/ask/deny — which gate tool-call
 * approval) with behavioral flags (design_checkins / orchestrator / decision_review
 * — which control whether Claude pauses for design/decision judgment). The
 * behavioral-flag badge (⚙ Behavior, not permission) makes the distinction legible
 * next to BOTH the design_checkins control (Settings tab) AND the orchestrator /
 * decision_review controls (Pipeline tab).
 *
 * This gate asserts the `behavioral-flag-badge` class appears at least once inside
 * the Settings-tab markup span AND at least once inside the Pipeline-tab span —
 * TWO location-scoped assertions, not one global grep (a global grep can't tell
 * whether the Pipeline side lost its badge while the Settings side kept one).
 *
 * Extraction style mirrors check-dashboard-roundtrip.mjs: pure text slicing over
 * the generated dashboard.html; no eval.
 *
 * Modes:
 *   node scripts/check-posture-legibility.mjs [path/to/dashboard.html]
 *       → assert a badge in each of the Settings + Pipeline spans. exit 0 = pass.
 *   node scripts/check-posture-legibility.mjs --must-fail [path]
 *       → strip the Pipeline-side badge ONLY and assert the per-location check
 *         catches it (Settings still passes, Pipeline now fails). exit 0 = teeth.
 */
import { readFileSync } from "node:fs";

const args = process.argv.slice(2);
const mustFail = args.includes("--must-fail");
const htmlPath = args.find((a) => !a.startsWith("--")) || "plugins/ravenclaude-core/dashboard.html";
const html = readFileSync(htmlPath, "utf8");

const BADGE_CLASS = 'class="behavioral-flag-badge"';

/* Slice the markup of one tab panel: from its `id="panel-<name>"` anchor to the
 * NEXT `id="panel-` (the following panel), or to end of document. Robust to panel
 * reordering — it always ends at the next panel boundary. */
function panelSpan(doc, id) {
  const anchor = `id="${id}"`;
  const s = doc.indexOf(anchor);
  if (s === -1) throw new Error(`panel not found: ${id} (in ${htmlPath})`);
  const next = doc.indexOf('id="panel-', s + anchor.length);
  return doc.slice(s, next === -1 ? doc.length : next);
}

const badgeCount = (span) =>
  (span.match(new RegExp(BADGE_CLASS.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "g")) || []).length;

/* Two LOCATION-scoped assertions (not one global grep). */
function checkLocations(doc) {
  const f = [];
  if (badgeCount(panelSpan(doc, "panel-settings")) < 1)
    f.push("Settings-tab (panel-settings) span carries no behavioral-flag-badge");
  if (badgeCount(panelSpan(doc, "panel-pipeline")) < 1)
    f.push("Pipeline-tab (panel-pipeline) span carries no behavioral-flag-badge");
  return f;
}

if (mustFail) {
  // Strip the badge from the Pipeline span ONLY, leaving Settings untouched.
  const pipeline = panelSpan(html, "panel-pipeline");
  const stripped = pipeline.replace(/<span class="behavioral-flag-badge"[\s\S]*?<\/span>/g, "");
  if (stripped === pipeline) {
    console.error("must-fail: no Pipeline-side badge found to strip — cannot prove teeth.");
    process.exit(1);
  }
  const mutated = html.replace(pipeline, stripped);

  const settingsStillOk = badgeCount(panelSpan(mutated, "panel-settings")) >= 1;
  const failures = checkLocations(mutated);
  const pipelineNowFails = failures.some((x) => x.includes("Pipeline"));

  if (settingsStillOk && pipelineNowFails) {
    console.log(
      "OK (must-fail): stripping the Pipeline-side badge is caught per-location — Settings still passes while Pipeline fails.",
    );
    process.exit(0);
  }
  console.error(
    "must-fail: stripping the Pipeline-side badge was NOT caught per-location — the gate has NO teeth.",
  );
  console.error(`  settingsStillOk=${settingsStillOk} pipelineNowFails=${pipelineNowFails}`);
  process.exit(1);
}

const failures = checkLocations(html);
if (failures.length) {
  console.error("posture-legibility: FAILED");
  for (const x of failures) console.error("  ✗ " + x);
  process.exit(1);
}
console.log(
  "posture-legibility: behavioral-flag-badge present in BOTH the Settings-tab and Pipeline-tab spans.",
);
