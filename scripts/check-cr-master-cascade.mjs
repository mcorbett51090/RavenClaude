#!/usr/bin/env node
/* check-cr-master-cascade.mjs — Gate 137 (P4a).
 *
 * Guards the command-review MASTER-ENABLE cascade against the "one click enables
 * ALL 12 categories" blast-radius bug (the KB incident). The master ON-flip must
 * check ONLY the 4 high-stakes shell categories; the other 8 stay per-category
 * opt-in, and a category the user already checked individually must NOT be cleared
 * by an ON-flip. Turning the master OFF still clears everything (no asymmetry).
 *
 * Extraction style mirrors check-dashboard-roundtrip.mjs: pull the REAL master
 * handler out of the generated dashboard.html by text (NO eval of untrusted input;
 * the extracted-by-name handler is run in a DOM-free Function sandbox against a
 * mock of 12 data-thing-category checkboxes).
 *
 * Modes:
 *   node scripts/check-cr-master-cascade.mjs [path/to/dashboard.html]
 *       → assert the REAL handler narrows to exactly the 4 high-stakes cats and
 *         never clears a pre-checked non-high-stakes category. exit 0 = pass.
 *   node scripts/check-cr-master-cascade.mjs --must-fail [path]
 *       → revert the narrowing to the all-12 cascade and assert THIS check catches
 *         it (the assertions must fail on the reverted handler). exit 0 = teeth.
 */
import { readFileSync } from "node:fs";

const args = process.argv.slice(2);
const mustFail = args.includes("--must-fail");
const htmlPath = args.find((a) => !a.startsWith("--")) || "plugins/ravenclaude-core/dashboard.html";
const html = readFileSync(htmlPath, "utf8");

// The app JS is the script containing activate() (mirrors the roundtrip gate's
// heuristic for the folded index.html, which has several large scripts).
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
const app =
  scripts.find((s) => s.includes("function activate(")) ||
  scripts.reduce((a, b) => (b.length > a.length ? b : a), "");

// The 12 live command-review categories (THING_LIVE_CATEGORIES) + the 4 the
// narrowed master ON-flip must select.
const CATS = [
  "shell_readonly",
  "shell_remote_mutate",
  "shell_code_exec",
  "shell_local_mutate",
  "shell_package_install",
  "file_edit_project",
  "file_edit_global",
  "file_read_project",
  "file_read_global",
  "network_read",
  "mcp_tools",
  "network_write",
];
const HIGH_STAKES = [
  "shell_code_exec",
  "shell_remote_mutate",
  "shell_package_install",
  "shell_local_mutate",
];
const eqSet = (a, b) => JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());

/* Pull the brace-balanced body of masterCb.addEventListener("change", () => { … }). */
function extractHandlerBody(src) {
  const anchor = 'masterCb.addEventListener("change", () => {';
  const start = src.indexOf(anchor);
  if (start === -1) throw new Error("master-switch change handler not found in " + htmlPath);
  let i = start + anchor.length - 1; // sits on the opening {
  let depth = 0;
  let bodyStart = i + 1;
  for (; i < src.length; i++) {
    const c = src[i];
    if (c === "{") depth++;
    else if (c === "}") {
      depth--;
      if (depth === 0) return src.slice(bodyStart, i);
    }
  }
  throw new Error("unbalanced braces in master-switch handler");
}

const highStakesConstSrc =
  (app.match(/const CR_MASTER_HIGH_STAKES = \[[^\]]*\];/) || [])[0] ||
  `const CR_MASTER_HIGH_STAKES = ${JSON.stringify(HIGH_STAKES)};`;

const realBody = extractHandlerBody(app);

// The pre-P4a all-12 cascade — used only in --must-fail mode to prove the check
// distinguishes the narrowed handler from the un-narrowed one.
const REVERTED_ALL12_BODY = `
  state.command_review.enabled = masterCb.checked ? true : false;
  document.querySelectorAll('input[type="checkbox"][data-thing-category]').forEach(cb => {
    if (cb.disabled) return;
    cb.checked = masterCb.checked;
    const cat = cb.dataset.thingCategory;
    if (state.categories[cat]) state.categories[cat].thing = masterCb.checked;
  });
  syncMasterEnable();
  updateReviewIcons();
  flagUnsaved();
  render();
`;

/* Run the extracted handler body once against a DOM-free mock. */
function runScenario(bodySrc, highStakesSrc, { masterChecked, preChecked }) {
  const harness = `
${highStakesSrc}
const _CATS = ${JSON.stringify(CATS)};
const _pre = ${JSON.stringify(preChecked)};
const _boxes = _CATS.map(name => ({ checked: _pre.includes(name), disabled: false, dataset: { thingCategory: name } }));
const document = { querySelectorAll() { return _boxes; } };
const masterCb = { checked: ${JSON.stringify(masterChecked)} };
const state = {
  command_review: { enabled: true },
  categories: Object.fromEntries(_CATS.map(n => [n, { thing: _pre.includes(n) }])),
};
function syncMasterEnable() {}
function updateReviewIcons() {}
function flagUnsaved() {}
function render() {}
const _handler = () => { ${bodySrc} };
_handler();
return {
  checked: _boxes.filter(b => b.checked).map(b => b.dataset.thingCategory),
  stateThing: _CATS.filter(n => state.categories[n].thing),
};
`;
  return new Function(harness)();
}

/* Return the list of assertion failures for a given handler body. */
function checkHandler(bodySrc, highStakesSrc) {
  const f = [];

  // A — ON from all-off: exactly the 4 high-stakes end up checked.
  const a = runScenario(bodySrc, highStakesSrc, { masterChecked: true, preChecked: [] });
  if (!eqSet(a.checked, HIGH_STAKES))
    f.push(
      `ON-flip from all-off checked {${a.checked.sort()}}, expected exactly the 4 high-stakes {${[...HIGH_STAKES].sort()}}`,
    );
  if (!eqSet(a.stateThing, HIGH_STAKES))
    f.push(`ON-flip state.thing = {${a.stateThing.sort()}}, expected exactly the 4 high-stakes`);

  // B — ON with a pre-checked NON-high-stakes category: it must STAY checked
  //     (the ON-flip only ever ADDS the 4, never removes an existing selection).
  const b = runScenario(bodySrc, highStakesSrc, {
    masterChecked: true,
    preChecked: ["network_read"],
  });
  if (!b.checked.includes("network_read"))
    f.push("ON-flip cleared a pre-checked non-high-stakes category (network_read)");
  if (!eqSet(b.checked, [...HIGH_STAKES, "network_read"]))
    f.push(
      `ON-flip with network_read pre-checked = {${b.checked.sort()}}, expected the 4 + network_read`,
    );

  // C — OFF from all-on: everything clears (no blast-radius asymmetry).
  const c = runScenario(bodySrc, highStakesSrc, { masterChecked: false, preChecked: CATS });
  if (c.checked.length !== 0) f.push(`OFF-flip left {${c.checked.sort()}} checked, expected none`);

  return f;
}

if (mustFail) {
  const failures = checkHandler(REVERTED_ALL12_BODY, highStakesConstSrc);
  if (failures.length === 0) {
    console.error(
      "must-fail: the reverted all-12 cascade PASSED the narrowing assertions — the gate has NO teeth.",
    );
    process.exit(1);
  }
  console.log(
    `OK (must-fail): the reverted all-12 cascade was caught (${failures.length} assertion(s) fired).`,
  );
  process.exit(0);
}

const failures = checkHandler(realBody, highStakesConstSrc);
if (failures.length) {
  console.error("cr-master-cascade: FAILED");
  for (const x of failures) console.error("  ✗ " + x);
  process.exit(1);
}
console.log(
  "cr-master-cascade: master ON-flip narrows to exactly the 4 high-stakes categories; a pre-checked non-high-stakes category survives; OFF clears all.",
);
