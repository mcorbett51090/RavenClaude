#!/usr/bin/env node
/* check-bifrost-render.mjs — behavioral test for the Bifröst install-wizard's
 * verify logic + accordion (the §3.6 install-bridge tab, added in core v0.75.0).
 *
 * Extracts the REAL bifrostVerify / bifrostSetBadge / bifrostExpandFault +
 * BIFROST_RULES from the generated dashboard.html and drives them against a tiny
 * DOM stub. Asserts the §3.6 acceptance cases:
 *   - a known-SUCCESS paste turns the step badge green
 *   - a known-FAILURE paste turns it red AND auto-expands the matching fault row
 *   - empty paste → amber (unclear), no crash
 *   - the wizard NEVER executes a command (no fetch / no slash invocation — checked
 *     structurally: the extracted code contains no fetch()/exec of commands)
 *
 * No real browser/jsdom — a minimal document stub records badge class + the
 * fault row's hidden/aria state. Mirrors check-norns-render.mjs.
 *
 * Usage: node scripts/check-bifrost-render.mjs [path/to/dashboard.html]
 */
import { readFileSync } from "node:fs";

const htmlPath = process.argv[2] || "plugins/ravenclaude-core/dashboard.html";
const html = readFileSync(htmlPath, "utf8");
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
const app = scripts.reduce((a, b) => (b.length > a.length ? b : a), "");

function extract(src, header) {
  const start = src.indexOf(header);
  if (start === -1) throw new Error(`not found in dashboard.html: ${header}`);
  let i = src.indexOf("{", start);
  let depth = 0;
  for (; i < src.length; i++) {
    if (src[i] === "{") depth++;
    else if (src[i] === "}") {
      depth--;
      if (depth === 0) break;
    }
  }
  let end = i + 1;
  while (end < src.length && /[);\s]/.test(src[end]) && src[end] !== "\n") end++;
  return src.slice(start, end);
}

class El {
  constructor(tag) {
    this.tag = tag;
    this.children = [];
    this._class = "";
    this._text = "";
    this.value = "";
    this.hidden = false;
    this.attrs = {};
    this.classList = {
      _set: new Set(),
      add: (c) => this.classList._set.add(c),
      contains: (c) => this.classList._set.has(c),
      toggle: () => {},
    };
  }
  set className(v) {
    this._class = v;
  }
  get className() {
    return this._class;
  }
  set textContent(v) {
    this._text = String(v);
  }
  get textContent() {
    return this._text;
  }
  setAttribute(k, v) {
    this.attrs[k] = String(v);
  }
  getAttribute(k) {
    return this.attrs[k];
  }
  querySelector() {
    return null;
  }
}

const registry = {};
function reg(id) {
  const e = new El("div");
  e.id = id;
  registry[id] = e;
  return e;
}
/* Build the DOM the verify path touches for steps 1..4. */
for (const n of ["1", "2", "3", "4"]) {
  reg("bifrost-badge-" + n);
  const ta = reg("bifrost-paste-" + n);
  ta.tag = "textarea";
  reg("bifrost-step-" + (parseInt(n, 10) + 1));
  reg("bifrost-fault-body-" + n);
}
/* fault toggles are found via querySelector('#bifrost-fault-N .bifrost-fault-toggle') */
const faultToggles = {};
for (const n of ["1", "2", "3", "4"]) {
  faultToggles[n] = new El("button");
  faultToggles[n].setAttribute("aria-expanded", "false");
}

global.document = {
  getElementById: (id) => registry[id] || null,
  querySelector: (sel) => {
    const m = sel.match(/#bifrost-fault-(\d+)\s/);
    return m ? faultToggles[m[1]] : null;
  },
};

const loaded = new Function(
  `${extract(app, "const BIFROST_RULES =")}
   ${extract(app, "function bifrostSetBadge(")}
   ${extract(app, "function bifrostExpandFault(")}
   ${extract(app, "function bifrostVerify(")}
   return { bifrostVerify, BIFROST_RULES };`,
)();

let failures = 0;
function ok(cond, msg) {
  if (cond) console.log("  ✓ " + msg);
  else {
    console.log("  ✗ " + msg);
    failures++;
  }
}

/* Case 1: step-1 success paste → green badge */
registry["bifrost-paste-1"].value = "Marketplace added successfully.";
loaded.bifrostVerify("1");
ok(
  registry["bifrost-badge-1"].className.includes("bifrost-badge--green"),
  "step 1 success → green badge",
);

/* Case 2: step-2 failure → red badge + fault-2 expanded */
registry["bifrost-paste-2"].value = "Error: no such plugin in marketplace.";
loaded.bifrostVerify("2");
ok(
  registry["bifrost-badge-2"].className.includes("bifrost-badge--red"),
  "step 2 failure → red badge",
);
ok(
  faultToggles["2"].getAttribute("aria-expanded") === "true",
  "step 2 failure → fault row auto-expands",
);
ok(registry["bifrost-fault-body-2"].hidden === false, "step 2 fault body un-hidden");

/* Case 3: empty paste → amber, no throw */
registry["bifrost-paste-3"].value = "";
loaded.bifrostVerify("3");
ok(registry["bifrost-badge-3"].className.includes("bifrost-badge--amber"), "step 3 empty → amber");

/* Case 4: success on step 4 */
registry["bifrost-paste-4"].value = "All checks passed — agent-ready.";
loaded.bifrostVerify("4");
ok(
  registry["bifrost-badge-4"].className.includes("bifrost-badge--green"),
  "step 4 success → green",
);

/* Case 5: structural — the verify/setBadge/expand code contains NO command execution */
const codeBlob =
  extract(app, "function bifrostVerify(") +
  extract(app, "function bifrostSetBadge(") +
  extract(app, "function bifrostExpandFault(");
ok(
  !/fetch\s*\(/.test(codeBlob) && !/execSlash|runCommand|invoke/.test(codeBlob),
  "verify path runs no command (copy-paste only)",
);

console.log("");
if (failures === 0) {
  console.log("Bifröst render: ALL ASSERTIONS PASS");
  process.exit(0);
}
console.log(`Bifröst render: ${failures} assertion(s) FAILED`);
process.exit(1);
