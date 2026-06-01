#!/usr/bin/env node
// check-concern-stats-render.mjs — render gate for the Pipeline tab's
// "Concern reliability" card.
//
// Extracts the real renderConcernStats() from the generated dashboard.html and
// drives it against three fixtures inside a stub DOM:
//
//   1. populated   — non-zero rows render as <tr>+<td> elements, no innerHTML.
//   2. empty       — zero rows AND non-zero reviews emit the "no concerns cited"
//                    state string and the table stays hidden.
//   3. cold        — zero reviews emits the "no command-review data yet" state.
//
// PLUS the must-fail half: a tampered render function that drops the empty-state
// branch is detected — proves the gate has teeth and isn't auto-passing.
//
// Also asserts a structural property: the render function MUST NOT contain the
// string `.innerHTML =` after our security-plugin warning (XSS hygiene — pure
// DOM construction only). A future refactor that reintroduces innerHTML fails.

import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DASH = path.join(__dirname, "..", "plugins", "ravenclaude-core", "dashboard.html");

function fail(msg) {
  process.stderr.write("FAIL: " + msg + "\n");
  process.exit(1);
}

function ok(msg) {
  process.stdout.write("ok: " + msg + "\n");
}

const html = fs.readFileSync(DASH, "utf-8");

// Extract renderConcernStats from the dashboard. The function is declared
// `function renderConcernStats(payload) { ... }`. We pull the source by
// matching the declaration through its closing brace (brace-counted).
function extractFn(name, source) {
  const decl = "function " + name + "(";
  const start = source.indexOf(decl);
  if (start === -1) return null;
  // find the opening brace of the function body
  let i = source.indexOf("{", start);
  if (i === -1) return null;
  let depth = 1;
  i += 1;
  for (; i < source.length && depth > 0; i++) {
    const c = source[i];
    if (c === "{") depth += 1;
    else if (c === "}") depth -= 1;
  }
  return depth === 0 ? source.slice(start, i) : null;
}

const fnSrc = extractFn("renderConcernStats", html);
if (!fnSrc) fail("renderConcernStats not found in dashboard.html");

// Structural hygiene: no `.innerHTML =` writes in the render function.
if (/\.innerHTML\s*=/.test(fnSrc)) {
  fail("renderConcernStats writes innerHTML — refactor to textContent/createElement (XSS hygiene)");
}
ok("no innerHTML writes in renderConcernStats");

// Minimal DOM stub. Element.appendChild + removeChild + textContent + className
// are all we need.
function makeEl(tag) {
  const el = {
    tagName: tag.toUpperCase(),
    children: [],
    className: "",
    textContent: "",
    hidden: false,
    _firstChild() {
      return this.children[0] || null;
    },
    get firstChild() {
      return this._firstChild();
    },
    appendChild(c) {
      this.children.push(c);
      c.parentNode = this;
      return c;
    },
    removeChild(c) {
      const i = this.children.indexOf(c);
      if (i >= 0) {
        this.children.splice(i, 1);
        c.parentNode = null;
      }
      return c;
    },
  };
  return el;
}

function setupDom() {
  const state = makeEl("div");
  state.id = "concern-stats-state";
  const tbl = makeEl("table");
  tbl.id = "concern-stats-table";
  const tb = makeEl("tbody");
  tb.id = "concern-stats-tbody";
  const byId = {
    "concern-stats-state": state,
    "concern-stats-table": tbl,
    "concern-stats-tbody": tb,
  };
  const document = {
    getElementById: (id) => byId[id] || null,
    createElement: (tag) => makeEl(tag),
  };
  return { document, state, tbl, tb };
}

function runRender(fnSource, payload) {
  const { document, state, tbl, tb } = setupDom();
  const sandbox = { document, window: {}, Number };
  vm.createContext(sandbox);
  // The render function references esc() in the populated path — but only
  // through a code-path our refactor eliminated; we still stub it for any
  // older variants.
  const wrapped = `var esc = s => String(s);\n${fnSource}\nrenderConcernStats(${JSON.stringify(payload)});`;
  vm.runInContext(wrapped, sandbox);
  return { state, tbl, tb };
}

// 1) Populated
{
  const payload = {
    total_reviews: 10,
    concerns: [
      {
        id: "xc.outside-project-tree",
        cited_total: 3,
        stripped: 2,
        heimdall_disagreed: 1,
        final_deny: 0,
        fp_ratio: 1.0,
      },
      {
        id: "xc.no-undo",
        cited_total: 2,
        stripped: 0,
        heimdall_disagreed: 0,
        final_deny: 2,
        fp_ratio: 0.0,
      },
    ],
  };
  const { state, tbl, tb } = runRender(fnSrc, payload);
  if (tbl.hidden) fail("populated: table stayed hidden");
  if (tb.children.length !== 2) fail("populated: expected 2 rows, got " + tb.children.length);
  if (!state.textContent.includes("2 concerns over 10 reviews")) {
    fail("populated: state line missing summary, got: " + state.textContent);
  }
  // First row should be hot (fp_ratio 1.0), second cold (0.0).
  if (tb.children[0].className !== "concern-row-hot") fail("populated: row 0 not hot");
  if (tb.children[1].className !== "concern-row-cold") fail("populated: row 1 not cold");
  ok("populated render");
}

// 2) Empty with reviews
{
  const { state, tbl } = runRender(fnSrc, { total_reviews: 7, concerns: [] });
  if (!tbl.hidden) fail("empty-with-reviews: table should be hidden");
  if (!/7 reviews/.test(state.textContent)) {
    fail("empty-with-reviews: review count missing from state, got: " + state.textContent);
  }
  ok("empty-with-reviews render");
}

// 3) Cold (zero reviews)
{
  const { state, tbl } = runRender(fnSrc, { total_reviews: 0, concerns: [] });
  if (!tbl.hidden) fail("cold: table should be hidden");
  if (!/tribunal has not run/i.test(state.textContent)) {
    fail("cold: state line missing 'tribunal has not run', got: " + state.textContent);
  }
  ok("cold render");
}

// 4) Must-fail half — a tampered render that drops the empty branch should
//    flunk fixture #3 (cold). We patch the source to skip the empty guard.
{
  const tampered = fnSrc.replace(/if \(!rows\.length\)\s*\{[\s\S]*?return;\s*\}/, "/* dropped */ ");
  if (tampered === fnSrc)
    fail("must-fail prep: could not strip the empty guard (source shape changed?)");
  let caught = false;
  try {
    runRender(tampered, { total_reviews: 0, concerns: [] });
    // If we reached here, the state.textContent should NOT contain the
    // "tribunal has not run" line — that branch is gone.
    const { state } = runRender(tampered, { total_reviews: 0, concerns: [] });
    if (/tribunal has not run/i.test(state.textContent)) caught = false;
    else caught = true;
  } catch (e) {
    caught = true;
  }
  if (!caught)
    fail(
      "must-fail half: tampered render still produced the cold-state string (gate has no teeth)",
    );
  ok("must-fail half: tampered render detected");
}

process.stdout.write("\nconcern-stats render gate: passed\n");
