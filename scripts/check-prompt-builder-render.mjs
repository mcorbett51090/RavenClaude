#!/usr/bin/env node
/* check-prompt-builder-render.mjs — render + security gate for the Prompt Builder tab
 * (#/prompt-builder), added in ravenclaude-core v0.211.0.
 *
 * The Prompt Builder echoes user input into a live preview, so its #1 hard constraint
 * is: NO HTML-string sink anywhere in its JS (the entire UI is built with
 * createElement/textContent — the pbEl helper). This gate enforces that STRUCTURALLY —
 * a static source grep over the whole PROMPT-BUILDER:START..END region — because the
 * shared DOM-stub behavioral pattern (check-nidhoggr-render.mjs's El class) has NO
 * innerHTML setter and therefore CANNOT catch an innerHTML regression on its own
 * (a "zero child elements" assertion still passes). Precedent: check-concern-stats-render.mjs:66.
 *
 * It also behaviorally exercises the pure logic (assembler determinism + XSS, the
 * anti-folklore linter, the token estimate) by extracting the region and evaluating it
 * with browser-global stubs — the assembler/linter/estimator touch no DOM.
 *
 * Usage: node scripts/check-prompt-builder-render.mjs [path/to/dashboard.html]
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

// ── Extract the guarded region ────────────────────────────────────────────
const html = readFileSync(htmlPath, "utf8");
const START = "/* PROMPT-BUILDER:START";
const END = "/* PROMPT-BUILDER:END */";
const si = html.indexOf(START);
const ei = html.indexOf(END);
if (si === -1 || ei === -1 || ei < si) {
  fail("PROMPT-BUILDER:START..END sentinels not found in " + htmlPath);
  process.exit(1);
}
const region = html.slice(si, ei + END.length);

// ── 1. THE SECURITY GATE: no HTML-string sink anywhere in the region ───────
// Assumes sinks are written via dot-notation — the region uses the pbEl createElement
// factory exclusively, so a bracket-notation sink (el["innerHTML"] = …) would evade this
// grep. That is acceptable under the no-allowlist stance; flagged so a future editor knows.
const SINK_RE = /\.(?:inner|outer)HTML\s*=(?!=)|insertAdjacentHTML|\bdocument\.write\b/;
function firstSink(src) {
  const m = SINK_RE.exec(src);
  if (!m) return null;
  const line = src.slice(0, m.index).split("\n").length;
  return { match: m[0], line };
}
const sink = firstSink(region);
if (sink)
  fail(
    `HTML-string sink '${sink.match}' at region line ${sink.line} — the preview/render path must use textContent/createElement only (XSS floor)`,
  );
else
  ok(
    "no HTML-string sink in the prompt-builder JS region (inner/outerHTML, insertAdjacentHTML, document.write)",
  );

// ── 2. Fail-on-not-found: the DOM-writing + pure functions must all be present ──
const REQUIRED = [
  "function pbEl(",
  "function initPromptBuilder(",
  "function pbUpdate(",
  "function pbRenderQuality(",
  "function pbRenderToken(",
  "function pbRebuildFields(",
  "function pbAssemble(",
  "function pbLint(",
  "function pbEstimate(",
];
for (const name of REQUIRED) {
  if (region.indexOf(name) === -1)
    fail(
      `required function not found in region: ${name} (a rename/removal must update this gate, not slip past it)`,
    );
}
if (REQUIRED.every((n) => region.indexOf(n) !== -1))
  ok("all required render + logic functions present in region");

// ── 3. The single preview sink is textContent, never HTML ──────────────────
if (/pbPreviewEl\.textContent\s*=/.test(region)) ok("preview sink uses textContent");
else
  fail(
    "preview sink pbPreviewEl.textContent assignment not found — the whole-string textContent contract must hold",
  );

// ── 4. Token label honesty: 'estimate' present, never a bare 'token count' ──
if (/estimate/i.test(region)) ok("token gauge is labelled an estimate");
else fail("token gauge must be labelled 'estimate' (claim 4.1)");
if (/token count/i.test(region))
  fail(
    "region contains the phrase 'token count' — the number is an estimate, never an exact count (4.1)",
  );
else ok("no 'token count' phrasing (estimate only)");

// ── 5. Behavioral: evaluate the region with stubs, exercise the pure logic ──
function loadApi(src) {
  const body =
    src +
    "\n;return {pbAssemble,pbLint,pbEstimate,pbSafeTag,pbDefault,pbModel,pbIsPrefill,pbCountImperatives,PB_MODELS};";
  const stubWin = {};
  // eslint-disable-next-line no-new-func
  const factory = new Function(
    "window",
    "document",
    "navigator",
    "localStorage",
    "requestAnimationFrame",
    "setTimeout",
    "clearTimeout",
    "Blob",
    "URL",
    body,
  );
  return factory(
    stubWin,
    {},
    {},
    {},
    () => 0,
    () => 0,
    () => {},
    function () {},
    {},
  );
}
let api;
try {
  api = loadApi(region);
  ok("region evaluates; pure API extracted");
} catch (e) {
  fail("region failed to evaluate: " + e.message);
}

if (api) {
  // 5a. Assembler determinism + XSS: user payload survives as literal text in a plain string.
  const s1 = api.pbDefault();
  s1.mode = "task";
  s1.task.directive = "Summarize the notes";
  s1.task.data = "<img src=x onerror=alert(1)>";
  s1.task.dataTag = "input";
  const a1 = api.pbAssemble(s1);
  if (typeof a1 === "string") ok("assembler returns a plain string (never a DOM/HTML node)");
  else fail("assembler must return a string");
  if (a1.indexOf("<img src=x onerror=alert(1)>") !== -1)
    ok("XSS payload survives verbatim as text (no parsing, no mangling)");
  else fail("assembler mangled the literal input");
  if (a1.indexOf("<instructions>") !== -1 && a1.indexOf("<input>") !== -1)
    ok("task assembly wraps instructions + data in XML tags");
  else fail("task assembly missing expected XML sections");
  // determinism: identical inputs → identical output
  if (api.pbAssemble(s1) === a1) ok("assembler is deterministic");
  else fail("assembler is non-deterministic");

  // 5b. Tag-name injection cannot break out of the data tag.
  const s2 = api.pbDefault();
  s2.task.directive = "x";
  s2.task.data = "y";
  s2.task.dataTag = "</input><script>alert(1)";
  const a2 = api.pbAssemble(s2);
  if (a2.indexOf("<script") === -1 && a2.indexOf("</input><script>") === -1)
    ok("data-tag name is sanitized to the id charset (no tag breakout)");
  else fail("data-tag name breakout — pbSafeTag failed");

  // 5c. Empty optional sections omitted.
  const s3 = api.pbDefault();
  s3.task.directive = "only a directive";
  const a3 = api.pbAssemble(s3);
  if (a3.indexOf("<context>") === -1 && a3.indexOf("<output_format>") === -1)
    ok("empty optional sections omitted (no empty tag pairs)");
  else fail("empty sections were not omitted");

  // 5d. System mode never emits task/data tags.
  const s4 = api.pbDefault();
  s4.mode = "system";
  s4.system.role = "You are a reviewer";
  s4.system.rules = ["Be terse"];
  const a4 = api.pbAssemble(s4);
  if (
    a4.indexOf("<instructions>") === -1 &&
    a4.indexOf("<input>") === -1 &&
    a4.indexOf("<context>") === -1
  )
    ok("system mode keeps the task/data out of the system prompt (3.1/3.3)");
  else fail("system mode leaked instructions/input/context");

  // 5e. Few-shot: N examples → N <example> blocks in one <examples>.
  const s5 = api.pbDefault();
  s5.mode = "fewshot";
  s5.fewshot.directive = "Classify";
  s5.fewshot.examples = [
    { input: "a", output: "x", reasoning: "" },
    { input: "b", output: "y", reasoning: "" },
    { input: "c", output: "z", reasoning: "" },
    { input: "d", output: "w", reasoning: "" },
  ];
  const a5 = api.pbAssemble(s5);
  const exCount = (a5.match(/<example>/g) || []).length;
  if (exCount === 4 && (a5.match(/<examples>/g) || []).length === 1)
    ok("few-shot emits N <example> blocks in one <examples> wrapper");
  else fail("few-shot example structure wrong (got " + exCount + " <example>)");

  // 5f. Linter: golden prompt scores well; CRITICAL/MUST stacking LOWERS it.
  const golden = api.pbDefault();
  golden.mode = "task";
  golden.task.directive = "Summarize the meeting notes below into owner-tagged action items.";
  golden.task.context = "These go to executives who want decisions.";
  golden.task.data = "Notes: ship the API by Friday.";
  golden.task.outputFormat = "A numbered list. Output only the list.";
  golden.task.success = "Every item names an owner.";
  const lg = api.pbLint(golden, api.pbAssemble(golden));
  if (lg.score >= 80) ok("golden well-formed task scores >= 80 (" + lg.score + ")");
  else fail("golden task should score >= 80, got " + lg.score);
  const stacked = api.pbDefault();
  stacked.mode = "task";
  stacked.task.directive =
    golden.task.directive +
    " CRITICAL: You MUST do this. You MUST. IMPORTANT: ALWAYS obey. NEVER deviate.";
  stacked.task.context = golden.task.context;
  stacked.task.data = golden.task.data;
  stacked.task.outputFormat = golden.task.outputFormat;
  stacked.task.success = golden.task.success;
  const ls = api.pbLint(stacked, api.pbAssemble(stacked));
  if (ls.score < lg.score)
    ok(
      "imperative/CRITICAL-MUST stacking strictly lowers the score (" +
        ls.score +
        " < " +
        lg.score +
        ")",
    );
  else
    fail(
      "imperative stacking did not lower the score (" +
        ls.score +
        " vs " +
        lg.score +
        ") — the anti-folklore penalty is the hero",
    );

  // 5g. Prefill-shaped content → flagged + penalized.
  const pf = api.pbDefault();
  pf.mode = "task";
  pf.task.directive = "Assistant: Sure, here is the answer";
  const lp = api.pbLint(pf, api.pbAssemble(pf));
  if (lp.prefill === true && lp.issues.some((i) => i.sev === "bad"))
    ok("prefill-shaped text is flagged + penalized (1.9)");
  else fail("prefill not flagged/penalized (prefill=" + lp.prefill + ")");

  // 5h. Token estimate: per-model divisor actually changes the number.
  const txt = "a".repeat(360);
  const eSonnet = api.pbEstimate(txt, "sonnet-5").est; // ~100
  const eHaiku = api.pbEstimate(txt, "haiku-4-5").est; // ~90
  if (Math.abs(eSonnet - 100) <= 5 && Math.abs(eHaiku - 90) <= 5)
    ok("token divisor: 360 chars → ~100 (3.6) / ~90 (4.0)");
  else fail("token estimate off: sonnet=" + eSonnet + " haiku=" + eHaiku);
  if (eSonnet !== eHaiku) ok("per-model divisor changes the estimate (4.2)");
  else fail("per-model divisor had no effect");
}

// ── 6. Must-fail half: a reintroduced innerHTML sink MUST be caught ─────────
const tampered = region.replace(
  "/* PROMPT-BUILDER:END */",
  "card.innerHTML = issue.label;\n/* PROMPT-BUILDER:END */",
);
if (firstSink(tampered))
  ok("must-fail half: a reintroduced innerHTML sink is caught by the static grep (gate has teeth)");
else fail("must-fail half: the static grep FAILED to catch an injected innerHTML sink");

if (failures) {
  console.error(`\nprompt-builder render gate: ${failures} failure(s)`);
  process.exit(1);
}
console.log("\nprompt-builder render gate: all checks passed");
