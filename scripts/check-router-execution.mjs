#!/usr/bin/env node
/* check-router-execution.mjs — the EXECUTING shell-router reachability gate,
 * closing gate-coverage gap G2/G3: "no gate executes the real router; sub-nav
 * click-reachability is ungated."
 *
 * WHY THIS EXISTS. The sibling text-parsing gates (check-shell-router.mjs,
 * check-committed-routes.mjs) deliberately never eval — they prove the router
 * SCAFFOLD is shaped right by reading the source as text. That leaves a real
 * hole: nothing RUNS navChildren()/resolveNavActive(), so a change that keeps
 * the map literals well-formed but drops a sub-nav <a href> (or mis-wires the
 * active-section resolver) sails through every gate — the exact "sub-nav
 * click-reachability is ungated" gap. A user then lands on a section whose only
 * way to a page (e.g. #/pipeline, #/web-access — orphaned to hash-only access
 * when SECTION_TABS was retired) has silently vanished from the sidebar.
 *
 * WHAT IT DOES. It EXTRACTS the real source of the four map literals + the two
 * router functions from the generated index.html, evaluates them verbatim in a
 * node:vm context wired with a mutable `location`, an `esc()` HTML-escaper, and
 * the real `D` (window.__RC_DATA__), then EXECUTES navChildren()/resolveNavActive()
 * against a hardcoded FLOOR of routes that MUST stay click-reachable — asserting
 * each renders a `class="nav-subitem"` <a href> and each resolves to the right
 * highlighted NAV section.
 *
 * SECURITY POSTURE. Unlike the text-parsing siblings, this gate DOES eval — a
 * deliberate exception justified by the input: index.html is a trusted,
 * same-org GENERATED artifact (the template itself notes "this payload is a
 * trusted, same-org generated artifact"), and extraction is scoped to six
 * NAMED literals/functions by balanced-delimiter matching, never arbitrary
 * page script. Do NOT copy this eval pattern to a less-trusted input.
 *
 * TEETH. `--mutate <route>` drops that route's sub-nav <a> from the extracted
 * navChildren source BEFORE eval, so the run must go red — proving the assertion
 * actually reads the rendered output. `--selftest` runs `--mutate` for EVERY
 * floor sub-nav route in a subprocess and asserts each one FAILS (a no-op
 * mutation is itself a loud selftest failure), the must-fail proof analogous to
 * check-shell-router.selftest.mjs.
 *
 * Usage:
 *   node scripts/check-router-execution.mjs [path/to/index.html]
 *   node scripts/check-router-execution.mjs --mutate '#/pipeline' [index.html]
 *   node scripts/check-router-execution.mjs --selftest [index.html]
 */
import { readFileSync } from "node:fs";
import { createContext, runInContext } from "node:vm";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const SELF = fileURLToPath(import.meta.url);

/* ── args: an optional positional html path (default index.html) + flags ─────── */
let htmlPath = "index.html";
let mutateRoute = null;
let selftest = false;
{
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--mutate") mutateRoute = argv[++i];
    else if (argv[i] === "--selftest") selftest = true;
    else htmlPath = argv[i];
  }
}

/* ── console style (mirrors check-plugin-detail-render.mjs) ──────────────────── */
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
  console.log(`\nrouter-execution: FAILED (${failures + 1} assertion(s))`);
  process.exit(1);
}

/* ── the FLOOR: routes that MUST stay click-reachable as a sub-nav <a href>,
 * paired with the section whose navChildren() renders them and the NAV section
 * resolveNavActive() must return (so the sidebar highlights correctly). ──────── */
const FLOOR = [
  { section: "control", route: "#/settings" },
  { section: "control", route: "#/pipeline" },
  { section: "control", route: "#/web-access" },
  { section: "activity", route: "#/activity" },
  { section: "activity", route: "#/saga" },
  { section: "activity", route: "#/mimir" },
  { section: "activity", route: "#/streams" },
  { section: "activity", route: "#/norns" },
  { section: "guardrails", route: "#/heimdall" },
  { section: "guardrails", route: "#/vidarr" },
  { section: "guardrails", route: "#/nidhoggr" },
  { section: "catalog", route: "#/team" },
  { section: "catalog", route: "#/trees" },
];

const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/* ── extractBalanced — the crux. Scan from `startMarker`, find the first `open`,
 * and return the source through its matching `close`, correctly SKIPPING:
 *   • string literals — single-quote, double-quote, AND backtick templates,
 *     with their `\` escapes;
 *   • `${ … }` template expressions, tracking their OWN brace depth so the
 *     expression's closing `}` returns to the template rather than miscounting
 *     the target pair (and any nested strings/templates inside the expression);
 *   • line (`// …`) and block (`/* … *\/`) comments — the generated source has
 *     comments carrying apostrophes ("you're"), stray `${tab}`/`#/` and `[data-*]`
 *     brackets that would otherwise open phantom strings/braces.
 * so delimiters inside strings/templates/comments never miscount. ────────────── */
function extractBalanced(src, startMarker, open, close) {
  const mi = src.indexOf(startMarker);
  if (mi === -1) throw new Error(`marker not found: ${JSON.stringify(startMarker)}`);
  const start = src.indexOf(open, mi);
  if (start === -1)
    throw new Error(`'${open}' not found after marker: ${JSON.stringify(startMarker)}`);

  // `tmpl` — a stack of brace depths, one entry per open `${` we are inside.
  // Non-empty ⇒ we are in a template EXPRESSION (code); its balancing `}` pops
  // back to the template literal instead of counting toward `close`.
  const tmpl = [];
  let str = null; // "'", '"', or "`" while inside a string; null otherwise
  let depth = 0;

  for (let i = start; i < src.length; i++) {
    const c = src[i];
    const n = src[i + 1];

    if (str !== null) {
      if (c === "\\") {
        i++; // escape — skip the next char
        continue;
      }
      if (str === "`") {
        if (c === "$" && n === "{") {
          tmpl.push(0); // enter `${ … }`
          str = null;
          i++; // consume the "{"
          continue;
        }
        if (c === "`") str = null;
        continue;
      }
      if (c === str) str = null; // close ' or "
      continue;
    }

    // not in a string (top-level code OR a template expression)
    if (c === "/" && n === "/") {
      const nl = src.indexOf("\n", i);
      i = nl === -1 ? src.length : nl;
      continue;
    }
    if (c === "/" && n === "*") {
      const e = src.indexOf("*/", i + 2);
      i = e === -1 ? src.length : e + 1;
      continue;
    }
    if (c === "'" || c === '"' || c === "`") {
      str = c;
      continue;
    }

    if (tmpl.length > 0) {
      // inside `${ … }`: track ITS braces; the closing "}" returns to template.
      if (c === "{") tmpl[tmpl.length - 1]++;
      else if (c === "}") {
        if (tmpl[tmpl.length - 1] === 0) {
          tmpl.pop();
          str = "`";
        } else tmpl[tmpl.length - 1]--;
      }
      continue;
    }

    // genuine top-level code: count only the target pair
    if (c === open) depth++;
    else if (c === close) {
      depth--;
      if (depth === 0) return src.slice(start, i + 1);
    }
  }
  throw new Error(`unbalanced ${open}${close} from marker: ${JSON.stringify(startMarker)}`);
}

/* ── drop a single sub-nav anchor (the `--mutate` / selftest teeth). The class
 * attribute carries a `${a("…")}` template placeholder (double quotes inside),
 * so match the whole opening tag by "no `>` until the target href", then the
 * plain-text label to `</a>`. Returns navSrc unchanged if the route is absent
 * (the caller treats that no-op as a loud failure). ─────────────────────────── */
function dropAnchor(navSrc, route) {
  const re = new RegExp(`<a [^>]*href="${escapeRe(route)}">[^<]*</a>`);
  return navSrc.replace(re, "");
}

/* ── read + extract the six sources once (shared by main + selftest). ────────── */
function loadSources(path) {
  const src = readFileSync(path, "utf8");
  const S = {};
  try {
    S.nav = extractBalanced(src, "const NAV = [", "[", "]");
    S.sectionAlias = extractBalanced(src, "const SECTION_ALIAS =", "{", "}");
    S.dashOwner = extractBalanced(src, "const DASH_OWNER =", "{", "}");
    S.dashTabAlias = extractBalanced(src, "const DASH_TAB_ALIAS =", "{", "}");
    S.navChildren = extractBalanced(src, "function navChildren(id)", "{", "}");
    S.resolveNavActive = extractBalanced(src, "function resolveNavActive(section)", "{", "}");
  } catch (e) {
    fatal("extraction failed — a router marker moved or a delimiter miscounted: " + e.message);
  }
  // The real D (window.__RC_DATA__ = {…};  const D = window.__RC_DATA__;)
  const dm = src.match(/window\.__RC_DATA__ = ([\s\S]*?);\s*\n\s*const D = window\.__RC_DATA__;/);
  if (!dm) fatal("window.__RC_DATA__ assignment not found");
  try {
    S.D = JSON.parse(dm[1]);
  } catch (e) {
    fatal("window.__RC_DATA__ is not valid JSON: " + e.message);
  }
  return S;
}

/* ── --selftest: prove the teeth. For EVERY floor sub-nav route, (1) confirm the
 * mutation actually changes the navChildren source (a no-op cannot prove teeth),
 * then (2) spawn this checker with `--mutate <route>` and assert a NON-ZERO exit.
 * Any route the gate stays GREEN on is a blind spot → selftest fails loud. ───── */
if (selftest) {
  const S = loadSources(htmlPath);
  const problems = [];
  for (const f of FLOOR) {
    if (dropAnchor(S.navChildren, f.route) === S.navChildren) {
      problems.push(
        `mutation for ${f.route} changed nothing — the anchor shape drifted; ` +
          `a no-op mutation cannot prove teeth (fix the mutation, do not ignore it)`,
      );
      continue;
    }
    const r = spawnSync(process.execPath, [SELF, "--mutate", f.route, htmlPath], {
      encoding: "utf8",
    });
    if (r.status === 0) {
      problems.push(
        `gate stayed GREEN on --mutate ${f.route} — it is BLIND to a dropped ${f.section} ` +
          `sub-nav link. This is the ungated-reachability gap G2/G3 exists to catch.`,
      );
    }
  }
  if (problems.length) {
    console.error("router-execution selftest: FAILED — the gate's teeth are not proven:");
    for (const p of problems) console.error("  - " + p);
    process.exit(1);
  }
  console.log(
    `router-execution selftest: OK — all ${FLOOR.length} floor sub-nav mutations independently ` +
      `trip the gate as a subprocess; the executing gate's teeth are externally proven.`,
  );
  process.exit(0);
}

/* ── main: extract → (optionally mutate) → eval the real router → EXECUTE it ─── */
const S = loadSources(htmlPath);

let navChildrenSrc = S.navChildren;
if (mutateRoute) {
  const mutated = dropAnchor(navChildrenSrc, mutateRoute);
  if (mutated === navChildrenSrc)
    fatal(
      `--mutate ${mutateRoute}: no sub-nav anchor for that route in navChildren (nothing dropped)`,
    );
  navChildrenSrc = mutated;
  console.log(`  · MUTATION ACTIVE — dropped the sub-nav <a> for ${mutateRoute}; run must go red`);
}

/* Evaluate the four maps + both functions verbatim in a vm context. `location`,
 * `esc`, and `D` are supplied as globals (the control/activity/guardrails
 * branches read only `location`; the catalog branch also reads `esc` + `D`;
 * resolveNavActive reads SECTION_ALIAS/NAV/DASH_OWNER, defined here). */
const esc = (s) =>
  String(s).replace(
    /[&<>"]/g,
    (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[ch],
  );
const sandbox = { location: { hash: "" }, esc, D: S.D };
createContext(sandbox);

const code =
  `const NAV = ${S.nav};\n` +
  `const SECTION_ALIAS = ${S.sectionAlias};\n` +
  `const DASH_OWNER = ${S.dashOwner};\n` +
  `const DASH_TAB_ALIAS = ${S.dashTabAlias};\n` +
  `function navChildren(id) ${navChildrenSrc}\n` +
  `function resolveNavActive(section) ${S.resolveNavActive}\n` +
  `globalThis.navChildren = navChildren;\n` +
  `globalThis.resolveNavActive = resolveNavActive;\n`;
try {
  runInContext(code, sandbox, { filename: "extracted-router.js" });
} catch (e) {
  fatal("the extracted router failed to evaluate (extraction miscounted?): " + e.message);
}
ok(
  typeof sandbox.navChildren === "function" && typeof sandbox.resolveNavActive === "function",
  "extracted navChildren() + resolveNavActive() evaluated into a callable router",
);

/* ── ASSERTION 1: EXECUTE navChildren — every floor route is click-reachable. ── */
console.log("\n  navChildren() — sub-nav click-reachability (executed):");
for (const f of FLOOR) {
  sandbox.location.hash = f.route;
  let out;
  try {
    out = sandbox.navChildren(f.section);
  } catch (e) {
    ok(false, `navChildren("${f.section}") threw for ${f.route}: ${e.message}`);
    continue;
  }
  const hrefRe = new RegExp(`<a class="nav-subitem[^"]*" href="${escapeRe(f.route)}"`);
  ok(
    hrefRe.test(String(out)),
    `${f.section}: renders a nav-subitem <a href="${f.route}"> (click-reachable)`,
  );
}

/* ── ASSERTION 2: EXECUTE resolveNavActive — every floor route highlights right. */
console.log("\n  resolveNavActive() — active-section highlight (executed):");
for (const f of FLOOR) {
  const key = f.route.replace(/^#\//, "");
  let got;
  try {
    got = sandbox.resolveNavActive(key);
  } catch (e) {
    ok(false, `resolveNavActive("${key}") threw: ${e.message}`);
    continue;
  }
  ok(got === f.section, `resolveNavActive("${key}") → "${got}" (expected "${f.section}")`);
}

console.log("");
if (failures === 0) {
  console.log(
    `router-execution: ALL ASSERTIONS PASS — ${FLOOR.length} floor routes click-reachable ` +
      `+ highlight-correct, executed against the real extracted router.`,
  );
  process.exit(0);
}
console.log(`router-execution: ${failures} assertion(s) FAILED`);
process.exit(1);
