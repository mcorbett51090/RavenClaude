#!/usr/bin/env node
// Gate 137 — command-review master-switch cascade is NARROWED (FORGE P4a).
//
// The KB (kb-tribunal-seats-abstaining §2/§8.2) traced the "every call goes through a
// degraded panel" blast radius to the dashboard master switch enabling ALL 12 review
// categories on one click. This gate extracts the REAL master-switch change handler
// (plus the dashboard's own CR_HIGH_STAKES list) from the generated dashboard.html and
// EXECUTES it against a DOM-free mock (the Gate-35 extract-and-run precedent — the code
// is our own generated artifact, not untrusted input), asserting the ON-flip enables
// EXACTLY the 4 high-stakes categories, never clears an existing individual selection,
// and the OFF-flip clears all.
//
// Usage: node scripts/check-cr-master-cascade.mjs            (exit 0 clean)
//        node scripts/check-cr-master-cascade.mjs --must-fail (exit 0 iff the old
//          all-12 cascade would be caught — proves the teeth)
import { readFileSync } from "node:fs";

const HTML = "plugins/ravenclaude-core/dashboard.html";
const CATS = [
  "shell_readonly",
  "shell_code_exec",
  "shell_remote_mutate",
  "shell_package_install",
  "shell_local_mutate",
  "file_edit_project",
  "file_edit_global",
  "file_read_project",
  "file_read_global",
  "network_read",
  "network_write",
  "mcp_tools",
];
const HIGH = [
  "shell_code_exec",
  "shell_remote_mutate",
  "shell_package_install",
  "shell_local_mutate",
];

function extractHandlerBody(src) {
  const anchor = 'masterCb.addEventListener("change", () => {';
  const i = src.indexOf(anchor);
  if (i < 0) throw new Error("master-switch change handler not found in dashboard.html");
  let depth = 0;
  const open = i + anchor.length - 1; // index of the body's opening brace
  let k = open;
  for (; k < src.length; k++) {
    if (src[k] === "{") depth++;
    else if (src[k] === "}") {
      depth--;
      if (depth === 0) break;
    }
  }
  return src.slice(open + 1, k);
}

function extractHighStakes(src) {
  const m = src.match(/const CR_HIGH_STAKES = \[[\s\S]*?\];/);
  return m ? m[0] : ""; // faithfully use the dashboard's OWN list
}

// Run a cascade body against a mock. preChecked = categories individually checked first.
function runCascade(fullBody, masterChecked, preChecked) {
  const boxes = CATS.map((c) => ({
    checked: preChecked.includes(c),
    disabled: false,
    dataset: { thingCategory: c },
  }));
  const seen = new Set();
  const uniq = boxes.filter((b) =>
    seen.has(b.dataset.thingCategory) ? false : seen.add(b.dataset.thingCategory),
  );
  const state = {
    command_review: { enabled: true },
    categories: Object.fromEntries(CATS.map((c) => [c, { thing: preChecked.includes(c) }])),
  };
  const masterCb = { checked: masterChecked };
  const document = {
    querySelectorAll: (sel) => (sel.includes("data-thing-category") ? uniq : []),
  };
  const noop = () => {};
  // eslint-disable-next-line no-new-func
  const fn = new Function(
    "masterCb",
    "document",
    "state",
    "syncMasterEnable",
    "updateReviewIcons",
    "flagUnsaved",
    "render",
    fullBody,
  );
  fn(masterCb, document, state, noop, noop, noop, noop);
  return uniq;
}

function realBody(src) {
  return extractHighStakes(src) + "\n" + extractHandlerBody(src);
}

function eq(a, b) {
  return JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());
}

function main() {
  const src = readFileSync(HTML, "utf8");
  const body = realBody(src);
  const fails = [];

  // 1. ON-flip from all-off -> exactly the 4 high-stakes checked
  const on = runCascade(body, true, []);
  const onChecked = on.filter((b) => b.checked).map((b) => b.dataset.thingCategory);
  if (!eq(onChecked, HIGH))
    fails.push(`ON-flip checked [${onChecked}] != the 4 high-stakes [${HIGH}]`);

  // 2. ON-flip must NOT clear a pre-checked non-high-stakes category
  const on2 = runCascade(body, true, ["mcp_tools"]);
  if (!on2.find((b) => b.dataset.thingCategory === "mcp_tools").checked)
    fails.push("ON-flip cleared a pre-checked non-high-stakes category (mcp_tools)");

  // 3. OFF-flip clears everything
  const off = runCascade(body, false, HIGH);
  if (off.some((b) => b.checked)) fails.push("OFF-flip did not clear all categories");

  if (fails.length) {
    console.log("Gate 137 FAILED — cr-master cascade:");
    fails.forEach((f) => console.log("  - " + f));
    process.exit(1);
  }
  console.log(
    "Gate 137 OK — master ON enables exactly the 4 high-stakes, preserves existing selections; OFF clears all.",
  );
}

function mustFail() {
  // The pre-P4a behavior: an unconditional all-12 cascade. The gate's assertion #1
  // (exactly 4 on ON-flip) MUST reject it.
  const allTwelveBody =
    "state.command_review.enabled = masterCb.checked;" +
    "document.querySelectorAll('input[data-thing-category]').forEach(cb => {" +
    "  cb.checked = masterCb.checked;" +
    "  if (state.categories[cb.dataset.thingCategory]) state.categories[cb.dataset.thingCategory].thing = masterCb.checked;" +
    "});" +
    "syncMasterEnable(); updateReviewIcons(); flagUnsaved(); render();";
  const boxes = runCascade(allTwelveBody, true, []);
  const n = boxes.filter((b) => b.checked).length;
  if (n === HIGH.length) {
    console.log(
      "Gate 137 --must-fail FAILED: the all-12 mutant checked only the 4 (not reproduced).",
    );
    process.exit(1);
  }
  console.log(
    `Gate 137 --must-fail OK: the reverted all-12 cascade checks ${n} (!= 4) — the ON-flip assertion catches it.`,
  );
}

if (process.argv.includes("--must-fail")) mustFail();
else main();
