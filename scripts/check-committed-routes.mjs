#!/usr/bin/env node
/* check-committed-routes.mjs — Gate 51, the by-destination half.
 *
 * The sibling check-shell-router.mjs proves the router *scaffold* exists (NAV +
 * SECTION_ALIAS + DASH_OWNER + the mount host + no iframe). This script proves
 * the stronger contract Phase 2's acceptance depends on: **every committed
 * `#/…` route on both surfaces resolves to a REAL destination** — not the
 * router's catch-all fallback (viewHome on index / overview on the standalone).
 *
 * Two surfaces, two DIFFERENT routers (verified against the source, 2026-07-16):
 *   • index.html — the unified portal shell. A `#/section[/sub]` is dispatched by
 *     route(): LEGACY_VIEW → SECTION_ALIAS → plugin-* → observe/act → DASH_OWNER →
 *     the discover/configure/learn/home switch. An unknown section falls to
 *     viewHome() (a dead deep-link). `#/learn/<concept>` resolves to the Learn
 *     section; the concept sub-segment is dropped by the shell (honored only on
 *     the standalone surface).
 *   • plugins/ravenclaude-core/dashboard.html — the standalone, hashchange router.
 *     applyHash() → activate(seg0, seg1); activate() falls back to "overview" for
 *     any tab ∉ validTabs (the `.tab-btn[data-tab]` set). `#/learn/<concept>`
 *     opens the concept via openConcept(sub) — so the concept MUST exist
 *     (`data-concept`) for the route to reach its destination.
 *
 * The fixture (tests/fixtures/routes/committed-routes.json) is the committed
 * enumeration of every `#/…` on both surfaces → its destination. This checker
 * re-derives that enumeration + resolution from the LIVE html each run and
 * asserts the committed fixture matches, bidirectionally:
 *   • a route committed in the html but absent from the fixture → FAIL
 *     (delete-a-route must-fail half; the fixture stops enumerating everything).
 *   • a route whose destination the html no longer resolves → FAIL
 *     (break-a-destination must-fail half; a DASH_OWNER key removed, a tab
 *     renamed → the deep-link now dead-ends).
 *
 * Pure text-based parsing — NO `new Function()` / NO `eval` / NO `vm`, the same
 * security posture as check-shell-router.mjs (a future contributor copying the
 * pattern to a less-trusted input must not inherit an ACE sink in CI).
 *
 * Usage:
 *   node scripts/check-committed-routes.mjs            # assert the committed tree
 *   node scripts/check-committed-routes.mjs --emit     # (re)generate the fixture
 *   node scripts/check-committed-routes.mjs --index <p> --dashboard <p> --fixture <p>
 */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";

const args = process.argv.slice(2);
function optVal(name, def) {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : def;
}
const EMIT = args.includes("--emit");
const DASH_PATH = optVal("--dashboard", "plugins/ravenclaude-core/dashboard.html");
const INDEX_PATH = optVal("--index", "index.html");
const FIXTURE_PATH = optVal("--fixture", "tests/fixtures/routes/committed-routes.json");

/* ── shared text helpers (mirrors check-shell-router.mjs; no eval) ─────────── */
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
function appScript(src) {
  const matches = [...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
  const app = matches.find((s) => /\bconst NAV\b/.test(s));
  if (!app) throw new Error("no <script> contains `const NAV` — shell scaffold missing?");
  return app;
}

/* Every literal href="#/…" in document order (raw — includes duplicates so the
 * count reconciles with the headline 188 / 202). A dynamic template literal
 * (`href="#/${…}"`) is captured up to the first `"`, exactly as a grep would. */
function extractHrefs(html) {
  return [...html.matchAll(/href="(#\/[^"]*)"/g)].map((m) => m[1]);
}
const isDynamic = (r) => r.includes("${");
const uniqSort = (arr) => [...new Set(arr)].sort();

/* ── index.html shell router ──────────────────────────────────────────────── */
function parseIndexRouter(html) {
  const app = appScript(html);
  const navText = sliceBetween(app, "const NAV = ", "[");
  const navIds = [];
  const navValues = new Set(); // the values `#/${n.route || n.id}` expands to
  for (const objm of navText.matchAll(/\{([^}]*)\}/g)) {
    const body = objm[1];
    const id = (body.match(/id:\s*"([^"]+)"/) || [])[1];
    if (!id) continue;
    navIds.push(id);
    const route = (body.match(/route:\s*"([^"]+)"/) || [])[1];
    navValues.add(route || id);
  }
  const parseMap = (text) => {
    const o = {};
    for (const m of text.matchAll(/["']?([A-Za-z0-9_-]+)["']?\s*:\s*"([^"]+)"/g)) o[m[1]] = m[2];
    return o;
  };
  const alias = parseMap(sliceBetween(app, "const SECTION_ALIAS = ", "{"));
  const owner = parseMap(sliceBetween(app, "const DASH_OWNER = ", "{"));
  const legacy = parseMap(sliceBetween(app, "const LEGACY_VIEW = ", "{"));
  const tabsText = sliceBetween(app, "const SECTION_TABS = ", "{");
  const navRoutes = uniqSort([...tabsText.matchAll(/route:\s*"(#\/[^"]*)"/g)].map((m) => m[1]));
  return {
    navIds: [...new Set(navIds)],
    navValues: [...navValues],
    alias,
    owner,
    legacy,
    navRoutes,
  };
}
// Mirrors index.html route() dispatch order exactly. Returns the destination
// handler string, or UNRESOLVED when the section is unknown (falls to viewHome).
function resolveIndex(section, R) {
  if (R.legacy[section] === "viewTeam") return { resolved: true, destination: "viewTeam" };
  let s = section;
  if (R.alias[s]) s = R.alias[s];
  // #/plugin-vars (the P1 picker) is EXCLUDED from the plugin-* → __openPlugin
  // branch in route() — it is owned by the dashboard host via DASH_OWNER and
  // dispatches through viewDashboard. Mirror that ordering exactly.
  if (s.startsWith("plugin-") && s !== "plugin-vars")
    return { resolved: true, destination: "__openPlugin" };
  if (s === "observe") return { resolved: true, destination: "viewDashboard:activity" };
  if (s === "act") return { resolved: true, destination: "viewDashboard:commands" };
  if (R.owner[s]) return { resolved: true, destination: `viewDashboard:${s}` };
  if (s === "discover") return { resolved: true, destination: "viewMarketplace" };
  if (s === "configure") return { resolved: true, destination: "viewConfiguration" };
  if (s === "learn") return { resolved: true, destination: "viewResources" };
  if (s === "home") return { resolved: true, destination: "viewHome" };
  return { resolved: false, destination: "UNRESOLVED" };
}

/* ── standalone dashboard.html hashchange router ──────────────────────────── */
function parseDashRouter(html) {
  const validTabs = new Set();
  for (const btn of html.matchAll(/<button\b([^>]*)>/g)) {
    const attrs = btn[1];
    if (!/class="[^"]*\btab-btn\b/.test(attrs)) continue;
    const dt = attrs.match(/\bdata-tab="([^"]+)"/);
    if (dt) validTabs.add(dt[1]);
  }
  const concepts = new Set([...html.matchAll(/data-concept="([^"]+)"/g)].map((m) => m[1]));
  return { validTabs, concepts };
}
// Mirrors activate(tab, sub): unknown tab → overview (dead-end); learn+sub →
// openConcept(sub) so the concept must exist.
function resolveDash(section, sub, R) {
  if (!R.validTabs.has(section)) return { resolved: false, destination: "UNRESOLVED" };
  if (section === "learn" && sub) {
    if (!R.concepts.has(sub)) return { resolved: false, destination: `UNRESOLVED:concept:${sub}` };
    return { resolved: true, destination: `activate:learn|openConcept:${sub}` };
  }
  return { resolved: true, destination: `activate:${section}` };
}

/* ── build one surface's enumeration + resolution from live html ──────────── */
function splitRoute(route) {
  const raw = route.replace(/^#\/?/, "");
  const idx = raw.indexOf("/");
  return idx === -1 ? [raw, null] : [raw.slice(0, idx), raw.slice(idx + 1) || null];
}
function buildSurface(kind, html) {
  const hrefs = extractHrefs(html);
  const staticRoutes = uniqSort(hrefs.filter((r) => !isDynamic(r)));
  const dynamicRoutes = uniqSort(hrefs.filter(isDynamic));

  let router;
  const resolveOne = (route) => {
    const [section, sub] = splitRoute(route);
    const r = kind === "index" ? resolveIndex(section, router) : resolveDash(section, sub, router);
    return { section, sub, destination: r.destination, resolved: r.resolved };
  };
  router = kind === "index" ? parseIndexRouter(html) : parseDashRouter(html);

  const static_href_routes = staticRoutes.map((route) => ({ route, ...resolveOne(route) }));

  // Dynamic href templates (index only). A `#/${…}` first-segment expands to the
  // NAV route||id set; a `#/discover/${…}` has a literal section we can resolve.
  const dynamic_href_templates = dynamicRoutes.map((template) => {
    const afterHash = template.replace(/^#\//, "");
    if (afterHash.startsWith("${")) {
      const expands = router.navValues.map((v) => ({ value: v, ...resolveIndex(v, router) }));
      return {
        template,
        literal_section: null,
        note: "expands to NAV route||id — each value asserted to resolve",
        expands_to: expands,
      };
    }
    const section = afterHash.split("/")[0];
    const r = resolveIndex(section, router);
    return {
      template,
      literal_section: section,
      note: `literal section '${section}' → ${r.destination}`,
      destination: r.destination,
      resolved: r.resolved,
    };
  });

  // Deliberate sub-nav routes declared in the router itself (index SECTION_TABS).
  const nav_routes = (router.navRoutes || []).map((route) => ({ route, ...resolveOne(route) }));

  const surface = {
    href_count: hrefs.length,
    distinct_static: static_href_routes.length,
    distinct_dynamic: dynamic_href_templates.length,
    static_href_routes,
    dynamic_href_templates,
    nav_routes,
  };
  // Surface a machine-checkable router-invariant snapshot for index (every
  // alias / owner value must be a real NAV id — a broken value dead-ends).
  if (kind === "index") {
    surface.router_invariants = {
      nav_ids: router.navIds,
      section_alias: router.alias,
      dash_owner: router.owner,
    };
  }
  return surface;
}

/* ── assertion mode ───────────────────────────────────────────────────────── */
const failures = [];
const A = (cond, msg) => {
  if (!cond) failures.push(msg);
};
function setDiff(a, b) {
  const bs = new Set(b);
  return a.filter((x) => !bs.has(x));
}
function assertSurface(kind, live, fx) {
  if (!fx) {
    failures.push(`fixture is missing surface "${kind}"`);
    return;
  }
  // 1. headline href count reconciles (188 dashboard / 202 index).
  A(
    live.href_count === fx.href_count,
    `${kind}: href_count ${live.href_count} != fixture ${fx.href_count}`,
  );

  // 2. every committed static route is enumerated by the fixture, and vice
  //    versa (bidirectional — the "enumerates every committed #/…" contract).
  const liveRoutes = live.static_href_routes.map((r) => r.route);
  const fxRoutes = fx.static_href_routes.map((r) => r.route);
  const missing = setDiff(liveRoutes, fxRoutes);
  const extra = setDiff(fxRoutes, liveRoutes);
  A(missing.length === 0, `${kind}: committed routes absent from fixture: ${missing.join(", ")}`);
  A(extra.length === 0, `${kind}: fixture routes no longer committed: ${extra.join(", ")}`);

  // 3. every committed static route resolves to a REAL destination, and to the
  //    destination the fixture recorded (break-a-destination catches here).
  const fxDest = new Map(fx.static_href_routes.map((r) => [r.route, r.destination]));
  for (const r of live.static_href_routes) {
    A(r.resolved, `${kind}: route ${r.route} does not resolve (dead-ends on the router fallback)`);
    if (fxDest.has(r.route)) {
      A(
        fxDest.get(r.route) === r.destination,
        `${kind}: route ${r.route} destination drifted: fixture "${fxDest.get(r.route)}" vs live "${r.destination}"`,
      );
    }
  }

  // 4. dynamic href templates enumerated + each resolves.
  const liveTpl = live.dynamic_href_templates.map((t) => t.template);
  const fxTpl = fx.dynamic_href_templates.map((t) => t.template);
  A(
    setDiff(liveTpl, fxTpl).length === 0 && setDiff(fxTpl, liveTpl).length === 0,
    `${kind}: dynamic template set drift — live [${liveTpl.join(", ")}] vs fixture [${fxTpl.join(", ")}]`,
  );
  for (const t of live.dynamic_href_templates) {
    if (t.expands_to) {
      for (const e of t.expands_to)
        A(
          e.resolved,
          `${kind}: dynamic ${t.template} expands to "${e.value}" which does not resolve`,
        );
    } else {
      A(
        t.resolved,
        `${kind}: dynamic template ${t.template} (section "${t.literal_section}") does not resolve`,
      );
    }
  }

  // 5. router-declared sub-nav routes enumerated + each resolves.
  const liveNav = live.nav_routes.map((r) => r.route);
  const fxNav = (fx.nav_routes || []).map((r) => r.route);
  A(
    setDiff(liveNav, fxNav).length === 0 && setDiff(fxNav, liveNav).length === 0,
    `${kind}: nav_routes set drift — live [${liveNav.join(", ")}] vs fixture [${fxNav.join(", ")}]`,
  );
  for (const r of live.nav_routes)
    A(r.resolved, `${kind}: sub-nav route ${r.route} does not resolve`);

  // 6. index router invariants: every alias / owner value is a real NAV id.
  if (kind === "index" && live.router_invariants) {
    const nav = new Set(live.router_invariants.nav_ids);
    for (const [k, v] of Object.entries(live.router_invariants.section_alias))
      A(nav.has(v), `${kind}: SECTION_ALIAS["${k}"] → "${v}" is not a real NAV section`);
    for (const [k, v] of Object.entries(live.router_invariants.dash_owner))
      A(nav.has(v), `${kind}: DASH_OWNER["${k}"] → "${v}" is not a real NAV section`);
  }
}

/* ── main ─────────────────────────────────────────────────────────────────── */
const dashHtml = readFileSync(DASH_PATH, "utf8");
const indexHtml = readFileSync(INDEX_PATH, "utf8");
const surfaces = {
  dashboard: buildSurface("dashboard", dashHtml),
  index: buildSurface("index", indexHtml),
};

if (EMIT) {
  // PB-2 (FORGE dashboard-consumption): --emit regenerates `surfaces` from the
  // live HTML, but the hand-authored `required_routes` FLOOR must be carried
  // through VERBATIM. Without this, removing a required route's href and
  // re-emitting would silently launder the removal (the fixture would simply stop
  // listing it) — the exact anti-laundering hole C5 needs closed. So read the
  // prior fixture and preserve its floor unchanged.
  let priorRequired;
  try {
    priorRequired = JSON.parse(readFileSync(FIXTURE_PATH, "utf8")).required_routes;
  } catch {
    priorRequired = undefined; // first emit / unreadable → no floor to carry
  }
  const out = {
    _note:
      "Committed #/… route enumeration for BOTH portal surfaces → each route's " +
      "resolved destination. Generated by scripts/check-committed-routes.mjs --emit; " +
      "asserted by Gate 51 (check-committed-routes.mjs, no args). Do NOT hand-edit " +
      "the generated dashboard.html/index.html — regenerate them, then re-emit this " +
      "fixture. See docs/dashboard-redesign-plan.md §7 Phase 4a.",
    generated_by: "scripts/check-committed-routes.mjs --emit",
    ...(priorRequired ? { required_routes: priorRequired } : {}),
    surfaces,
  };
  mkdirSync(dirname(FIXTURE_PATH), { recursive: true });
  writeFileSync(FIXTURE_PATH, JSON.stringify(out, null, 2) + "\n");
  const d = surfaces.dashboard;
  const i = surfaces.index;
  console.log(`emitted ${FIXTURE_PATH}`);
  console.log(
    `  dashboard: ${d.href_count} hrefs → ${d.distinct_static} distinct static routes, ${d.distinct_dynamic} dynamic`,
  );
  console.log(
    `  index:     ${i.href_count} hrefs → ${i.distinct_static} distinct static routes, ${i.distinct_dynamic} dynamic, ${i.nav_routes.length} sub-nav routes`,
  );
  process.exit(0);
}

let fixture;
try {
  fixture = JSON.parse(readFileSync(FIXTURE_PATH, "utf8"));
} catch (e) {
  console.error(`FAIL: cannot read route fixture ${FIXTURE_PATH}: ${e.message}`);
  console.error("      (run `node scripts/check-committed-routes.mjs --emit` to generate it)");
  process.exit(1);
}
assertSurface("dashboard", surfaces.dashboard, fixture.surfaces && fixture.surfaces.dashboard);
assertSurface("index", surfaces.index, fixture.surfaces && fixture.surfaces.index);

// required_routes floor (PB-2): a hand-authored, --emit-preserved set of routes
// that MUST remain present AND resolved on each named surface. This is the
// anti-laundering control C5 needs — deleting a required route's href from the
// HTML and re-emitting updates `surfaces` (route gone) but leaves this floor
// listing it, so the removal goes RED here instead of being silently laundered to
// green. Each phase that legitimately retires a floor route must remove it here in
// the same commit AND add a docs/dashboard-removed-routes.md row (a per-phase
// discipline the floor makes visible). Keys beginning with `_` (e.g. `_note`) are
// documentation, not surfaces — skipped so a naive walk can't misread them.
if (fixture.required_routes) {
  for (const [surf, required] of Object.entries(fixture.required_routes)) {
    if (surf.startsWith("_")) continue;
    const live = surfaces[surf];
    if (!live) {
      failures.push(`required_routes names unknown surface "${surf}"`);
      continue;
    }
    const resolvedByRoute = new Map(live.static_href_routes.map((r) => [r.route, r.resolved]));
    for (const route of required) {
      if (!resolvedByRoute.has(route)) {
        failures.push(
          `required_routes floor: ${surf} must still commit "${route}" — it is gone from the ` +
            `live surface (removed without a docs/dashboard-removed-routes.md entry + a floor edit?)`,
        );
      } else {
        A(
          resolvedByRoute.get(route) === true,
          `required_routes floor: ${surf} route "${route}" no longer resolves (dead-ends on the fallback)`,
        );
      }
    }
  }
}

if (failures.length) {
  console.error(`FAIL: committed-route contract violations (${failures.length}):`);
  for (const f of failures) console.error("  - " + f);
  process.exit(1);
}
console.log(
  `OK: every committed #/… resolves by destination — dashboard ${surfaces.dashboard.href_count} hrefs / ` +
    `${surfaces.dashboard.distinct_static} routes, index ${surfaces.index.href_count} hrefs / ` +
    `${surfaces.index.distinct_static} routes + ${surfaces.index.dynamic_href_templates.length} templates + ` +
    `${surfaces.index.nav_routes.length} sub-nav routes; all destinations real.`,
);
