#!/usr/bin/env node
// Gate 138 — behavioral-flags-vs-permissions legibility (FORGE P5a).
//
// Operators conflate permission categories (allow/ask/deny) with behavioral flags
// (design_checkins / orchestrator / decision_review) and crank every permission to
// Allow expecting the behavioral prompts to go quiet (intake doc
// 2026-07-16-comfort-posture-behavioral-flags-vs-permissions). P5a marks the
// behavioral controls with a ⚙ "Behavior, not permission" badge on BOTH surfaces.
//
// This gate asserts the badge appears at least once inside the Settings-tab span AND
// at least once inside the Pipeline-tab span — two LOCATION-scoped assertions, not a
// single global grep (so removing it from one surface is caught). Pure text-based, no
// eval. Usage: node scripts/check-posture-legibility.mjs [--must-fail]
import { readFileSync } from "node:fs";

const HTML = "plugins/ravenclaude-core/dashboard.html";
const BADGE = "behavioral-flag-badge";

// Span of a panel = from its id="panel-X" to the NEXT id="panel-…"/…-payload boundary.
function panelSpan(html, panelId) {
  const anchor = `id="${panelId}"`;
  const start = html.indexOf(anchor);
  if (start < 0) return null;
  const rest = html.slice(start + anchor.length);
  const nextBoundary = rest.search(/id="(panel-[a-z-]+|[a-z0-9-]+-payload)"/);
  const end = nextBoundary < 0 ? rest.length : nextBoundary;
  return rest.slice(0, end);
}

function assertSpans(html) {
  const fails = [];
  for (const [label, pid] of [
    ["Settings", "panel-settings"],
    ["Pipeline", "panel-pipeline"],
  ]) {
    const span = panelSpan(html, pid);
    if (span === null) {
      fails.push(`${label}: ${pid} not found in dashboard.html`);
    } else if (!span.includes(BADGE)) {
      fails.push(
        `${label}: no '${BADGE}' inside the ${pid} span (behavioral flag not marked there)`,
      );
    }
  }
  return fails;
}

function main() {
  const html = readFileSync(HTML, "utf8");
  const fails = assertSpans(html);
  if (fails.length) {
    console.log("Gate 138 FAILED — posture legibility:");
    fails.forEach((f) => console.log("  - " + f));
    process.exit(1);
  }
  console.log(
    "Gate 138 OK — behavioral-flag badge present in BOTH the Settings and Pipeline spans.",
  );
}

function mustFail() {
  // Strip the badge from the Pipeline span ONLY; the per-location check must catch it
  // (a single global grep would still pass on the Settings occurrence — that's the bug
  // this gate's per-location scoping exists to prevent).
  const html = readFileSync(HTML, "utf8");
  const anchor = 'id="panel-pipeline"';
  const at = html.indexOf(anchor);
  if (at < 0) {
    console.log("Gate 138 --must-fail FAILED: panel-pipeline not found to mutate.");
    process.exit(1);
  }
  const head = html.slice(0, at);
  const tail = html.slice(at).split(BADGE).join("BADGE_STRIPPED_PIPELINE");
  const mutated = head + tail;
  const fails = assertSpans(mutated);
  const pipelineCaught = fails.some((f) => f.startsWith("Pipeline"));
  const settingsStillOk = !fails.some((f) => f.startsWith("Settings"));
  if (pipelineCaught && settingsStillOk) {
    console.log(
      "Gate 138 --must-fail OK: badge stripped from Pipeline only -> Pipeline assertion fails, Settings still passes (per-location scoping has teeth).",
    );
    process.exit(0);
  }
  console.log(
    `Gate 138 --must-fail FAILED: pipelineCaught=${pipelineCaught} settingsStillOk=${settingsStillOk}`,
  );
  process.exit(1);
}

if (process.argv.includes("--must-fail")) mustFail();
else main();
