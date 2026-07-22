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
 * What this guards (Gate 51 — 4-destination IA, P3 re-cut dashboard-consumption):
 *   - NAV = the four task destinations (control/activity/guardrails/catalog).
 *     Help is a NON-NAV drawer overlay, not a fifth NAV id.
 *   - DASH_SECTIONS still contains every dashboard-owned top-level route that
 *     committed bookmarks + the gjallarhorn-link + SessionStart capability
 *     banners point at. Removing one silently breaks deep-links.
 *   - SECTION_ALIAS maps every legacy/retired top-level route (marketplace/team/
 *     configuration/resources/dashboard/discover/home) to a REAL destination —
 *     destination asserted, not mere presence — so links + ⌘K + bookmarks survive.
 *     Help-drawer routes resolve to their nearest destination, never a drawer id.
 *   - DASH_OWNER maps each dashboard tab route to its owning destination
 *     (incl. the phantom routes nidhoggr→guardrails, sleipnir→activity).
 *   - resolveNavActive() / route() drive the native dashboard host (viewDashboard)
 *     + the shell views + plugin-* via __openPlugin, never iframes.
 *   - Mount host (#dash-root) + entry point (window.__dashApp) present; no <iframe>.
 *   - The #dash-root chrome-hide CSS + the same-origin /__csrf served probe present.
 *   - DASH_TAB_ALIAS-target validity: every alias VALUE is a real fragment tab
 *     (§11.2) — a mistyped target would blank the dashboard host silently.
 *   - Teeth proven EXTERNALLY by check-shell-router.selftest.mjs (renamed NAV id,
 *     emptied SECTION_ALIAS, dropped chrome-hide rule each trip the gate).
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

/* NAV — the four task destinations (P3 IA re-cut, dashboard-consumption). Help is
 * a NON-NAV drawer overlay, not a fifth NAV id — its absorbed routes resolve via
 * SECTION_ALIAS to a real destination, never a drawer target (see the alias check). */
const NAV_IDS = ["control", "activity", "guardrails", "catalog"];
for (const id of NAV_IDS) {
  const re = new RegExp(`id:\\s*"${id}"`);
  assert(re.test(NAV_TEXT), `NAV regression: missing destination id "${id}"`);
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
  marketplace: "catalog",
  team: "catalog",
  configuration: "control",
  resources: "catalog",
  dashboard: "activity",
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
  heimdall: "guardrails",
  vidarr: "guardrails",
  nidhoggr: "guardrails",
  saga: "activity",
  mimir: "activity",
  settings: "control",
  "web-access": "control",
  pipeline: "control",
  commands: "catalog",
  trees: "catalog",
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
/* The dashboard JS self-wraps in its own IIFE (`(() => { … activate … })();`),
 * so `activate` is scoped to that inner closure. The __dashApp.show() entry point
 * MUST be exposed INSIDE that IIFE — if it's appended AFTER the inner `})();`
 * close, `activate` is out of scope, every show() throws a swallowed ReferenceError,
 * and every shell nav click silently falls back to the Overview tab (the regression
 * this guards). The bug fingerprint is a `})();` immediately followed by the
 * exposure; the correct fold has the exposure BEFORE the close. */
assert(
  !/\}\)\(\);\s*window\.__dashApp\s*=/.test(html),
  "window.__dashApp must be exposed INSIDE the dashboard IIFE (before its `})();` close), " +
    "not stranded after it — otherwise activate() is out of scope and shell nav dead-ends on Overview",
);
assert(!/<iframe/i.test(html), "merged portal must contain no <iframe> (native merge)");

/* ── Single chrome + DASH_TAB_ALIAS-target validity (P3 IA re-cut) ────────────
 * The folded dashboard's own cat-bar/tab-bar must be hidden (scoped to #dash-root
 * so the shipped standalone keeps its nav). SECTION_TABS is RETIRED: the four
 * destinations reach their dashboard tabs through DASH_OWNER + route(), not a
 * per-section sub-nav, so its former sub-nav assertions are gone with it. */
const CHROME_HIDE_RE = /#dash-root \.cat-bar,\s*#dash-root \.tab-bar\s*\{\s*display:\s*none/;
assert(CHROME_HIDE_RE.test(html), "the #dash-root chrome-hide CSS rule must be present");

/* DASH_TAB_ALIAS-target validity (§11.2). DASH_TAB_ALIAS maps a shell route to a
 * FRAGMENT tab id; viewDashboard() calls __dashApp.show(DASH_TAB_ALIAS[section] ||
 * section). A value that is NOT a real fragment tab blanks the dashboard host with
 * zero console error — invisible to both Gate 51 scripts before P3, and the exact
 * failure P4's DASH_TAB_ALIAS edit could ship. Assert every VALUE is a member of the
 * fragment's valid-tab set: the <button class="tab-btn" data-tab="…"> list, the same
 * validTabs mechanism activate() derives at generate-dashboards.py. "Destination,
 * not mere presence" — the same discipline this file applies to SECTION_ALIAS/
 * DASH_OWNER targets above. */
const fragmentTabs = new Set();
for (const btn of html.matchAll(/<button\b([^>]*)>/g)) {
  const attrs = btn[1];
  if (!/class="[^"]*\btab-btn\b/.test(attrs)) continue;
  const dt = attrs.match(/\bdata-tab="([^"]+)"/);
  if (dt) fragmentTabs.add(dt[1]);
}
assert(
  fragmentTabs.size > 0,
  'no <button class="tab-btn" data-tab="…"> in the fragment — the valid-tab set is empty (chrome deleted?)',
);
const DASH_TAB_ALIAS_TEXT = sliceBetween(app, "const DASH_TAB_ALIAS = ", "{");
for (const m of DASH_TAB_ALIAS_TEXT.matchAll(/["']?[A-Za-z0-9_-]+["']?\s*:\s*"([^"]+)"/g)) {
  const target = m[1];
  assert(
    fragmentTabs.has(target),
    `DASH_TAB_ALIAS target "${target}" is not a real fragment tab ` +
      `(no <button class="tab-btn" data-tab="${target}">) — it would blank the dashboard host`,
  );
}
/* Served-mode banner reuses the same-origin /__csrf signal — never a new
 * cross-origin probe (DNS-rebinding defense). */
assert(
  /fetch\(["']\/__csrf["']/.test(app),
  "served-mode probe must HEAD the same-origin /__csrf endpoint (no new cross-origin probe)",
);

/* The gate's teeth (that a renamed NAV id, an emptied SECTION_ALIAS, or a
 * dropped chrome-hide rule each trip it) are proven EXTERNALLY by
 * check-shell-router.selftest.mjs, which mutates a fresh render and re-invokes
 * THIS script as a subprocess. The former inline "must-fail" block tested a
 * hardcoded bad string against the same regex the real assertion uses — it
 * never re-ran the gate, so it certified nothing and a weakened re-authoring
 * passed it. It was deleted (FORGE dashboard-consumption, PB-3). Do NOT
 * re-introduce an in-process self-test here: teeth are proven by the external
 * driver, precisely because the IA re-cut re-authors this file but must not
 * touch that driver. */

if (failures.length) {
  console.error("FAIL: shell router contract violations in " + htmlPath + ":");
  for (const f of failures) console.error("  - " + f);
  process.exit(1);
}
console.log(
  "OK: router contract holds (NAV + aliases + DASH_OWNER + route + single-chrome + section sub-nav + served probe, no iframe). Teeth proven externally by check-shell-router.selftest.mjs.",
);
