#!/usr/bin/env node
/* check-host-context-render.mjs — XSS floor for Host & context (#/host-context).
 * Own sentinel HOST-CONTEXT:START..END (split from Gate 144 / Prompt Builder).
 */
import { readFileSync } from "node:fs";

const htmlPath = process.argv[2] || "plugins/ravenclaude-core/dashboard.html";
let failures = 0;
function ok(msg) {
  console.log("  ✓ " + msg);
}
function fail(msg) {
  console.error("  ✗ " + msg);
  failures++;
}

const html = readFileSync(htmlPath, "utf8");
const START = "/* HOST-CONTEXT:START";
const END = "/* HOST-CONTEXT:END */";
const si = html.indexOf(START);
const ei = html.indexOf(END);
if (si === -1 || ei === -1 || ei < si) {
  fail("HOST-CONTEXT:START..END sentinels not found in " + htmlPath);
  process.exit(1);
}
const region = html.slice(si, ei + END.length);

const SINK_RE = /\.(?:inner|outer)HTML\s*\+?=(?!=)|insertAdjacentHTML|\bdocument\.write\b/;
function firstSink(src) {
  const m = SINK_RE.exec(src);
  if (!m) return null;
  return { match: m[0], line: src.slice(0, m.index).split("\n").length };
}
if (firstSink(region)) fail("HTML-string sink in HOST-CONTEXT region");
else ok("no HTML-string sink in HOST-CONTEXT region");

if (region.indexOf("function initHostContext(") === -1)
  fail("initHostContext missing from HC region");
else ok("initHostContext present in HC region");

if (html.indexOf('id="hc-root"') === -1) fail("missing #hc-root mount");
else ok("#hc-root mount present");

const tampered = region.replace(END, "el.innerHTML = x;\n" + END);
if (firstSink(tampered)) ok("must-fail half: HC innerHTML sink caught");
else fail("must-fail half: HC sink not caught");

if (failures) {
  console.error(`\nhost-context render gate: ${failures} failure(s)`);
  process.exit(1);
}
console.log("\nhost-context render gate: all checks passed");
