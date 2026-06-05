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
 * What this guards (Gate 51 — Slice A 5-section IA):
 *   - NAV = the five task sections (home/discover/configure/observe/learn).
 *   - DASH_SECTIONS still contains every dashboard-owned top-level route that
 *     committed bookmarks + the gjallarhorn-link + SessionStart capability
 *     banners point at. Removing one silently breaks deep-links.
 *   - SECTION_ALIAS maps every legacy top-level route (marketplace/team/
 *     configuration/resources/dashboard) to a REAL NAV section — destination
 *     asserted, not mere presence — so internal links + ⌘K + bookmarks survive.
 *   - DASH_OWNER maps each dashboard tab route to its owning NAV section
 *     (incl. the phantom routes nidhoggr→observe, sleipnir→observe).
 *   - resolveNavActive() / route() drive the native dashboard host (viewDashboard)
 *     + the shell views + plugin-* via __openPlugin, never iframes.
 *   - Mount host (#dash-root) + entry point (window.__dashApp) present; no <iframe>.
 *   - Two must-fail halves: a renamed NAV id and an emptied SECTION_ALIAS each
 *     trip the gate — proves the regexes probe the right thing.
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
const SECTION_ALIAS_TEXT = sliceBetween(app, "const SECTION_ALIAS = ", "{");
const DASH_OWNER_TEXT = sliceBetween(app, "const DASH_OWNER = ", "{");
const RESOLVE_NAV_TEXT = sliceFunction(app, "function resolveNavActive(");
const ROUTE_TEXT = sliceFunction(app, "function route(");

/* NAV — the five task sections (Slice A IA). */
const NAV_IDS = ["home", "discover", "configure", "observe", "learn"];
for (const id of NAV_IDS) {
  const re = new RegExp(`id:\\s*"${id}"`);
  assert(re.test(NAV_TEXT), `NAV regression: missing section id "${id}"`);
}

/* DASH_SECTIONS — every top-level dashboard route the committed-bookmark
 * contract depends on must still be present (resolves via DASH_OWNER). */
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
  assert(
    new RegExp(`"${r}"`).test(DASH_SECTIONS_TEXT),
    `DASH_SECTIONS missing "${r}" (committed-bookmark deep-link contract)`,
  );
}

/* SECTION_ALIAS — every legacy top-level shell route must map to a current NAV
 * section, or internal links + bookmarks + ⌘K break on the rename. Destination
 * is asserted (not mere presence): the alias VALUE must be a real NAV id. */
const expectedAliases = {
  marketplace: "discover",
  team: "discover",
  configuration: "configure",
  resources: "learn",
  dashboard: "observe",
};
for (const [legacy, target] of Object.entries(expectedAliases)) {
  const re = new RegExp(`["']?${legacy}["']?\\s*:\\s*"${target}"`);
  assert(
    re.test(SECTION_ALIAS_TEXT),
    `SECTION_ALIAS must map legacy "${legacy}" → "${target}" (back-compat)`,
  );
  assert(NAV_IDS.includes(target), `alias target "${target}" must be a real NAV section`);
}

/* DASH_OWNER — each dashboard tab route resolves to its owning NAV section
 * (destination, not presence). Spot-check one per section + the phantom routes. */
const expectedOwners = {
  heimdall: "observe",
  saga: "observe",
  nidhoggr: "observe",
  sleipnir: "observe",
  settings: "configure",
  "web-access": "configure",
  simulator: "configure",
  commands: "learn",
  trees: "learn",
  pipeline: "learn",
};
for (const [tab, owner] of Object.entries(expectedOwners)) {
  const re = new RegExp(`["']?${tab}["']?\\s*:\\s*"${owner}"`);
  assert(re.test(DASH_OWNER_TEXT), `DASH_OWNER must map "${tab}" → "${owner}" section`);
  assert(NAV_IDS.includes(owner), `DASH_OWNER target "${owner}" must be a real NAV section`);
}

/* resolveNavActive() — folds legacy + dashboard routes onto NAV sections. */
assert(
  /SECTION_ALIAS\[section\]/.test(RESOLVE_NAV_TEXT),
  "resolveNavActive() must apply SECTION_ALIAS",
);
assert(
  /DASH_OWNER\[section\]/.test(RESOLVE_NAV_TEXT),
  "resolveNavActive() must consult DASH_OWNER",
);
assert(
  /startsWith\(["']plugin-["']\)/.test(RESOLVE_NAV_TEXT),
  "resolveNavActive() must map plugin-* → discover",
);

/* route() — drives the native dashboard host + shell views; never iframes. */
assert(
  /viewDashboard\(/.test(ROUTE_TEXT),
  "route() must call viewDashboard() for dashboard routes",
);
assert(/__openPlugin\(/.test(ROUTE_TEXT), "route() must render plugin-* via __openPlugin");
assert(/SECTION_ALIAS\[section\]/.test(ROUTE_TEXT), "route() must resolve legacy aliases");
assert(
  !/viewPayload\(|<iframe/.test(ROUTE_TEXT),
  "route() must NOT use the retired iframe payload loader",
);

/* Mount host + sub-app entry point present; no iframe anywhere. */
assert(/id="dash-root"/.test(html), "missing native mount host #dash-root");
assert(/window\.__dashApp\b/.test(html), "dashboard sub-app entry point window.__dashApp missing");
assert(!/<iframe/i.test(html), "merged portal must contain no <iframe> (native merge)");

/* ── Must-fail half: prove teeth on BOTH the NAV rename and the alias map.
 * (a) renaming an asserted NAV id must trip the NAV check;
 * (b) emptying SECTION_ALIAS must trip the alias check. */
{
  const navBad = NAV_TEXT.replace('id: "observe"', 'id: "observ"');
  const navWouldPass = NAV_IDS.every((id) => new RegExp(`id:\\s*"${id}"`).test(navBad));
  assert(!navWouldPass, "must-fail: a renamed NAV id should fail the NAV-section check");
  const aliasBad = "const SECTION_ALIAS = {};";
  const aliasWouldPass = Object.entries(expectedAliases).every(([l, t]) =>
    new RegExp(`["']?${l}["']?\\s*:\\s*"${t}"`).test(aliasBad),
  );
  assert(!aliasWouldPass, "must-fail: an emptied SECTION_ALIAS should fail the back-compat check");
}

if (failures.length) {
  console.error("FAIL: shell router contract violations in " + htmlPath + ":");
  for (const f of failures) console.error("  - " + f);
  process.exit(1);
}
console.log(
  "OK: 5-section router contract holds (NAV ids + DASH_SECTIONS + SECTION_ALIAS + DASH_OWNER + resolveNavActive + route + host/entry-point, no iframe); both must-fail halves detected.",
);
