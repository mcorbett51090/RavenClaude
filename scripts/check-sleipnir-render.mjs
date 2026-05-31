#!/usr/bin/env node
/* check-sleipnir-render.mjs — behavioral test for the "Sleipnir's stables"
 * worktree widget in the Activity tab (§3.7, added in core v0.76.0).
 *
 * Extracts the REAL renderSleipnir function from the generated dashboard.html and
 * drives it against a tiny DOM stub. Asserts:
 *   - N worktrees → "N worktrees: <names>" (count + listed names)
 *   - exactly 1 → singular "1 worktree:"
 *   - 0 / missing → "no active worktrees" (empty state, no crash)
 *
 * No real browser/jsdom — a minimal document stub records the body text. Mirrors
 * check-nidhoggr-render.mjs.
 *
 * Usage: node scripts/check-sleipnir-render.mjs [path/to/dashboard.html]
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

const body = {
  _text: "",
  set textContent(v) {
    this._text = String(v);
  },
  get textContent() {
    return this._text;
  },
};
global.document = { getElementById: (id) => (id === "sleipnir-body" ? body : null) };

const loaded = new Function(
  `${extract(app, "function renderSleipnir(")}
   return { renderSleipnir };`,
)();

let failures = 0;
function ok(cond, msg) {
  if (cond) console.log("  ✓ " + msg);
  else {
    console.log("  ✗ " + msg);
    failures++;
  }
}

/* N worktrees */
loaded.renderSleipnir({ count: 2, worktrees: ["coder-bar", "coder-foo"] });
ok(
  body.textContent.includes("2 worktrees:") && body.textContent.includes("coder-bar"),
  "N worktrees → count + names",
);

/* singular */
loaded.renderSleipnir({ count: 1, worktrees: ["solo"] });
ok(
  body.textContent.includes("1 worktree:") && !body.textContent.includes("1 worktrees"),
  "exactly 1 → singular label",
);

/* empty */
loaded.renderSleipnir({ count: 0, worktrees: [] });
ok(body.textContent.toLowerCase().includes("no active worktrees"), "0 → empty state");

/* missing/garbage → no crash, empty state */
loaded.renderSleipnir(undefined);
ok(
  body.textContent.toLowerCase().includes("no active worktrees"),
  "undefined → empty state (no crash)",
);

console.log("");
if (failures === 0) {
  console.log("Sleipnir render: ALL ASSERTIONS PASS");
  process.exit(0);
}
console.log(`Sleipnir render: ${failures} assertion(s) FAILED`);
process.exit(1);
