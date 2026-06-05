#!/usr/bin/env node
/* check-shell-router.mjs — structural test for the unified single-document
 * portal in index.html. The dashboard sub-app is folded NATIVELY into index.html
 * (no iframes): mounted in #dash-root, shown by the shell router toggling
 * [hidden] and driven via window.__dashApp.show(). (The repo-guide/catalog
 * sub-app was retired — its content is rendered natively by the shell from JSON
 * in the Marketplace + Resources sections, so there's no second host/entry point.)
 *
 * Pure text-based assertions — NO `new Function()` / NO `eval` / NO `vm`. The
 * sibling render-tests (check-heimdall-render.mjs etc.) DO extract source and
 * eval it; we avoid that here (a future contributor copying the pattern to a
 * less-trusted input would have an ACE sink in CI) and assert against the
 * source text directly — weaker than running the code, but safe and sufficient
 * for the regressions we care about (deleting the route set, renaming the
 * helpers, dropping a NAV item, removing the mount host or entry point).
 *
 * What this guards (Gate 70):
 *   - NAV still contains the Dashboard item + the five back-compat shell-native
 *     items (home/team/marketplace/configuration/resources).
 *   - DASH_SECTIONS contains every dashboard-owned top-level route that
 *     committed bookmarks + the gjallarhorn-link + SessionStart capability
 *     banners point at. Removing one silently breaks deep-links.
 *   - payloadKind() preserves the dynamic 'plugin-*' prefix mapping + null.
 *   - resolveNavActive() / route() drive the native dashboard host
 *     (viewDashboard), not iframes.
 *   - The mount host (#dash-root) and the sub-app entry point (window.__dashApp)
 *     are present, and NO <iframe> remains anywhere in the merged page.
 *   - Must-fail half: an emptied DASH_SECTIONS is detected by the same
 *     assertions — proves the regexes probe the right thing.
 *
 * Usage: node scripts/check-shell-router.mjs [path/to/index.html]
 */
import { readFileSync } from "node:fs";

const htmlPath = process.argv[2] || "index.html";
const html = readFileSync(htmlPath, "utf8");

/* Find the <script> body hosting the shell application (the one declaring NAV)
 * — NOT the data blob (__RC_DATA__) nor the folded-in sub-app IIFEs. */
function appScript(src) {
  const matches = [...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
  const app = matches.find((s) => /\bconst NAV\b/.test(s));
  if (!app)
    throw new Error(
      "no <script> in index.html contains `const NAV` — has the shell scaffold been removed?",
    );
  return app;
}

function sliceBetween(src, header, openCh) {
  const start = src.indexOf(header);
  if (start === -1) throw new Error(`anchor not found: ${header}`);
  const closeCh = openCh === "[" ? "]" : openCh === "{" ? "}" : null;
  if (!closeCh) throw new Error(`unsupported openCh: ${openCh}`);
  let i = src.indexOf(openCh, start);
  if (i === -1) throw new Error(`opener '${openCh}' not found after anchor`);
  let depth = 0;
  for (; i < src.length; i++) {
    if (src[i] === openCh) depth++;
    else if (src[i] === closeCh) {
      depth--;
      if (depth === 0) return src.slice(start, i + 1);
    }
  }
  throw new Error(`unbalanced ${openCh}…${closeCh} starting at anchor: ${header}`);
}

function sliceFunction(src, header) {
  return sliceBetween(src, header, "{");
}

const app = appScript(html);

const failures = [];
function assert(cond, msg) {
  if (!cond) failures.push(msg);
}

const NAV_TEXT = sliceBetween(app, "const NAV = ", "[");
const DASH_SECTIONS_TEXT = sliceBetween(app, "const DASH_SECTIONS = ", "[");
const PAYLOAD_KIND_TEXT = sliceFunction(app, "function payloadKind(");
const RESOLVE_NAV_TEXT = sliceFunction(app, "function resolveNavActive(");
const ROUTE_TEXT = sliceFunction(app, "function route(");

/* NAV — must list Dashboard + Catalog + the five back-compat items */
for (const id of ["home", "team", "marketplace", "dashboard", "configuration", "resources"]) {
  const re = new RegExp(`id:\\s*"${id.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&")}"`);
  assert(re.test(NAV_TEXT), `NAV regression: missing item with id "${id}"`);
}

/* DASH_SECTIONS — every top-level dashboard route the committed-bookmark
 * contract depends on must be present. */
const expectedDashboardRoutes = [
  "heimdall",
  "vidarr",
  "norns",
  "nidhoggr",
  "bifrost",
  "mimir",
  "sleipnir",
  "saga",
  "activity",
  "learn",
  "pipeline",
  "comfort-posture",
  "dashboard",
];
for (const r of expectedDashboardRoutes) {
  const re = new RegExp(`"${r}"`);
  assert(
    re.test(DASH_SECTIONS_TEXT),
    `DASH_SECTIONS missing "${r}" (committed-bookmark deep-link contract)`,
  );
}

/* payloadKind() — preserves dynamic plugin-* prefix + catalog mapping + null */
assert(
  /DASH_SECTIONS\.has\(section\)/.test(PAYLOAD_KIND_TEXT),
  "payloadKind() must consult DASH_SECTIONS",
);
assert(
  /startsWith\(["']plugin-["']\)/.test(PAYLOAD_KIND_TEXT),
  "payloadKind() must map plugin-* dynamic routes to the dashboard",
);
assert(
  /return null/.test(PAYLOAD_KIND_TEXT),
  "payloadKind() must return null for unknown sections (router falls to home)",
);

/* resolveNavActive() — back-compat fallbacks via payloadKind() */
assert(
  /NAV\.some/.test(RESOLVE_NAV_TEXT),
  "resolveNavActive() must recognize shell-native NAV ids first",
);
assert(
  /payloadKind\(section\)/.test(RESOLVE_NAV_TEXT),
  "resolveNavActive() must delegate to payloadKind() for folded-in routes",
);
for (const id of ['"dashboard"', '"home"']) {
  assert(RESOLVE_NAV_TEXT.includes(id), `resolveNavActive() must be able to return ${id}`);
}

/* route() — drives the NATIVE dashboard host, not iframes */
assert(
  /viewDashboard\(/.test(ROUTE_TEXT),
  "route() must call viewDashboard() for dashboard routes",
);
assert(
  !/viewPayload\(|<iframe/.test(ROUTE_TEXT),
  "route() must NOT use the retired iframe payload loader",
);

/* Mount host + sub-app entry point present in the merged document */
assert(/id="dash-root"/.test(html), "missing native mount host #dash-root");
assert(/window\.__dashApp\b/.test(html), "dashboard sub-app entry point window.__dashApp missing");
/* No iframe should remain anywhere in the merged portal. */
assert(!/<iframe/i.test(html), "merged portal must contain no <iframe> (native merge)");

/* ── Must-fail half: an emptied DASH_SECTIONS is caught by the SAME route
 * checks above. Proves the gate has teeth. */
{
  const emptySet = "const DASH_SECTIONS = new Set([]);";
  const wouldStillPass = expectedDashboardRoutes.every((r) => new RegExp(`"${r}"`).test(emptySet));
  assert(
    !wouldStillPass,
    "must-fail half: empty DASH_SECTIONS should fail the route-membership assertions",
  );
}

if (failures.length) {
  console.error("FAIL: shell router contract violations in " + htmlPath + ":");
  for (const f of failures) console.error("  - " + f);
  process.exit(1);
}
console.log(
  "OK: native portal router contract holds (NAV + DASH_SECTIONS + payloadKind + resolveNavActive + route + hosts + entry points); must-fail half also detected.",
);
