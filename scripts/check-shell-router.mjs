#!/usr/bin/env node
/* check-shell-router.mjs — structural test for the unified-dashboard shell
 * in index.html (Phase 1+2 of the unified-dashboard-shell plan,
 * docs/plans/2026-06-04-unified-dashboard-shell/plan.md).
 *
 * Pure text-based assertions — NO `new Function()` / NO `eval` / NO `vm`.
 * The sibling render-tests (check-heimdall-render.mjs etc.) DO extract
 * source from generated dashboard.html and eval it; the security-guidance
 * hook flagged that pattern as a code-injection footgun (a future
 * contributor copying the pattern to a less-trusted input source would
 * have an ACE sink in CI). We avoid it here by asserting against the
 * source text directly with regexes — weaker than running the code, but
 * safer and sufficient for the regressions we actually care about
 * (someone editing or deleting the lookup table, renaming the helpers,
 * or dropping a NAV item).
 *
 * What this guards (Gate 70):
 *   - NAV still contains the Dashboard + Catalog (repo-guide) items the
 *     unified shell added in Phase 1
 *   - PAYLOAD_ROUTES contains every dashboard-owned top-level route that
 *     committed bookmarks + the gjallarhorn-link + SessionStart capability
 *     banners point at. Renaming or removing one of these silently breaks
 *     deep-links.
 *   - PAYLOAD_ROUTES['repo-guide'] maps to repo-guide.html
 *   - payloadFor() preserves the dynamic 'plugin-*' prefix mapping
 *   - resolveNavActive() handles back-compat fallbacks
 *   - Must-fail half: an emptied PAYLOAD_ROUTES (the structural mistake to
 *     guard against) is detected by the same assertions — proves the
 *     regexes actually probe the right thing.
 *
 * Usage: node scripts/check-shell-router.mjs [path/to/index.html]
 */
import { readFileSync } from "node:fs";

const htmlPath = process.argv[2] || "index.html";
const html = readFileSync(htmlPath, "utf8");

/* Find the <script> body that hosts the shell application (the one that
 * declares NAV) — NOT the data blob script that defines __RC_DATA__ (which
 * is much larger and gets matched if we sort by length). `indexOf` + slice,
 * no eval anywhere. */
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

/* ── Positive contract ───────────────────────────────────────────────── */
const failures = [];
function assert(cond, msg) {
  if (!cond) failures.push(msg);
}

const NAV_TEXT = sliceBetween(app, "const NAV = ", "[");
const ROUTES_TEXT = sliceBetween(app, "const PAYLOAD_ROUTES = ", "{");
const PAYLOAD_FOR_TEXT = sliceFunction(app, "function payloadFor(");
const RESOLVE_NAV_TEXT = sliceFunction(app, "function resolveNavActive(");

/* NAV — must list Dashboard + Catalog + the five back-compat items */
for (const id of [
  "home",
  "team",
  "marketplace",
  "dashboard",
  "repo-guide",
  "configuration",
  "resources",
]) {
  const re = new RegExp(`id:\\s*"${id.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&")}"`);
  assert(re.test(NAV_TEXT), `NAV regression: missing item with id "${id}"`);
}

/* PAYLOAD_ROUTES — every top-level dashboard tab maps to dashboard.html */
const DASHBOARD_PATH = "plugins/ravenclaude-core/dashboard.html";
const REPO_GUIDE_PATH = "repo-guide.html";
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
  // Key may be unquoted (heimdall:) or quoted ("comfort-posture":). Match either.
  const keyPattern = /^[A-Za-z_$][\w$]*$/.test(r) ? `(?:${r}|"${r}")` : `"${r}"`;
  const re = new RegExp(
    `${keyPattern}\\s*:\\s*"${DASHBOARD_PATH.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"`,
  );
  assert(
    re.test(ROUTES_TEXT),
    `PAYLOAD_ROUTES["${r}"] must map to ${DASHBOARD_PATH} (committed-bookmark contract)`,
  );
}
const repoGuideRe = new RegExp(
  `"repo-guide"\\s*:\\s*"${REPO_GUIDE_PATH.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"`,
);
assert(
  repoGuideRe.test(ROUTES_TEXT),
  `PAYLOAD_ROUTES["repo-guide"] must map to ${REPO_GUIDE_PATH}`,
);

/* payloadFor() — preserves dynamic prefix + lookup-table fallback */
assert(
  /PAYLOAD_ROUTES\[section\]/.test(PAYLOAD_FOR_TEXT),
  "payloadFor() must look up PAYLOAD_ROUTES[section]",
);
assert(
  /startsWith\(["']plugin-["']\)/.test(PAYLOAD_FOR_TEXT),
  "payloadFor() must map plugin-* dynamic routes to the dashboard",
);
assert(
  /return null/.test(PAYLOAD_FOR_TEXT),
  "payloadFor() must return null for unknown sections (router falls to home)",
);

/* resolveNavActive() — back-compat fallbacks for shell-native + payload-owned */
assert(
  /NAV\.some/.test(RESOLVE_NAV_TEXT),
  "resolveNavActive() must recognize shell-native NAV ids first",
);
assert(
  /payloadFor\(section\)/.test(RESOLVE_NAV_TEXT),
  "resolveNavActive() must delegate to payloadFor() for payload-owned routes",
);
assert(
  /"repo-guide"/.test(RESOLVE_NAV_TEXT),
  "resolveNavActive() must light up the 'repo-guide' nav for repo-guide payloads",
);
assert(
  /"dashboard"/.test(RESOLVE_NAV_TEXT),
  "resolveNavActive() must light up the 'dashboard' nav for dashboard payloads",
);
assert(
  /"home"/.test(RESOLVE_NAV_TEXT),
  "resolveNavActive() must fall back to 'home' for unrecognized sections",
);

/* ── Must-fail half: an emptied PAYLOAD_ROUTES is caught by the SAME
 * regexes above. We don't re-eval the helpers; we verify that the
 * positive-contract regex would have flagged the structural mistake.
 * Asserts the gate has teeth — if the lookup table were stripped, this
 * file's expectations would fail (and the developer would see exactly
 * which routes regressed). */
{
  const emptyRoutesText = "const PAYLOAD_ROUTES = {};";
  const wouldStillPass = expectedDashboardRoutes.every((r) => {
    const keyPattern = /^[A-Za-z_$][\w$]*$/.test(r) ? `(?:${r}|"${r}")` : `"${r}"`;
    const re = new RegExp(
      `${keyPattern}\\s*:\\s*"${DASHBOARD_PATH.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"`,
    );
    return re.test(emptyRoutesText);
  });
  assert(
    !wouldStillPass,
    "must-fail half: empty PAYLOAD_ROUTES should fail the route-mapping assertions",
  );
  assert(
    !repoGuideRe.test(emptyRoutesText),
    "must-fail half: empty PAYLOAD_ROUTES should fail the repo-guide assertion",
  );
}

if (failures.length) {
  console.error("FAIL: shell router contract violations in " + htmlPath + ":");
  for (const f of failures) console.error("  - " + f);
  process.exit(1);
}
console.log(
  "OK: shell router contract holds (NAV + PAYLOAD_ROUTES + payloadFor + resolveNavActive); must-fail half also detected.",
);
