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
 *     route(): SECTION_ALIAS → plugin-* → observe/act → DASH_OWNER →
 *     the catalog/discover/learn branches. The LIVE default lands on Control, but
 *     this mirror treats an unknown section as UNRESOLVED to keep its teeth (see
 *     resolveIndex). `#/learn/<concept>` resolves to the Learn section; the concept
 *     sub-segment is dropped by the shell (honored only on the standalone surface).
 *   • plugins/ravenclaude-core/dashboard.html — the standalone, hashchange router.
 *     applyHash() → activate(seg0, seg1); activate() falls back to "settings" for
 *     any tab ∉ validTabs (the `.tab-btn[data-tab]` set — P5 retarget off the
 *     deleted "overview" panel). `#/learn/<concept>` opens the concept via
 *     openConcept(sub) — so the concept MUST exist (`data-concept`) for the route
 *     to reach its destination.
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
 * ── The index route→destination table is DERIVED, never declared ─────────────
 * resolveIndex() used to hard-code the dispatch as a literal ladder — including
 * `if (s === "learn") return "viewResources"`. That asserted a CONSTANT, not the
 * two surfaces against each other: PR #903 re-homed `#/learn` (a new
 * SHELL_ROUTE_HOME map), and a hard-coded expectation keeps reporting green
 * however far the live router drifts. The constitution's rule is the opposite —
 * "where two generated surfaces must agree, assert them against EACH OTHER,
 * never against a constant" — so parseRouteDispatch() now reads route()'s own
 * if/else ladder out of the rendered html and resolveIndex() walks THAT, in
 * source order. Rename the branch, retarget the handler, or delete it, and the
 * derived destination moves with it; the committed fixture is what the derived
 * value is compared against. (Gate 200 derives route HOMES the same way, via
 * `_shell_route_homes()` in scripts/check-surface-parity.py.)
 *
 * ── Shipped sibling pages ────────────────────────────────────────────────────
 * The portal is not the only shipped surface that links into the router:
 * pitch.html carries user-facing `href="index.html#/<route>"` links and nothing
 * gated them, so a route rename rots a shipped marketing link silently. Every
 * root-level `*.html` is scanned for cross-file `#/…` hrefs and each is resolved
 * through the SAME derived router — assert-against-each-other again, not a list.
 *
 * Usage:
 *   node scripts/check-committed-routes.mjs            # assert the committed tree
 *   node scripts/check-committed-routes.mjs --emit     # (re)generate the fixture
 *   node scripts/check-committed-routes.mjs --index <p> --dashboard <p> --fixture <p>
 *   node scripts/check-committed-routes.mjs --siblings a.html,b.html
 *   node scripts/check-committed-routes.mjs --self-test
 *   node scripts/check-committed-routes.mjs --must-fail
 *
 * Exit codes: 0 clean, 2 violation / cannot-run (fail-closed). Exit 1 is never
 * used for a finding — a non-blocking exit code is itself a silent fail-open.
 */
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const args = process.argv.slice(2);
function optVal(name, def) {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : def;
}
const EMIT = args.includes("--emit");
const DASH_PATH = optVal("--dashboard", "plugins/ravenclaude-core/dashboard.html");
const INDEX_PATH = optVal("--index", "index.html");
const FIXTURE_PATH = optVal("--fixture", "tests/fixtures/routes/committed-routes.json");
// Shipped sibling pages. Default: every root-level *.html (index.html included —
// it is scanned only for CROSS-FILE hrefs there, its own `#/…` set is the
// `index` surface above). Discovered, never listed, so a new shipped page is
// covered the day it lands instead of the day someone remembers to add it.
const SIBLINGS = optVal("--siblings", null);
const SELF_TEST = args.includes("--self-test");
const MUST_FAIL = args.includes("--must-fail");
const SELF_PATH = fileURLToPath(import.meta.url);

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
/* Index of the delimiter matching the opener at `openIdx`. */
function matchDelim(src, openIdx) {
  const openCh = src[openIdx];
  const closeCh = openCh === "(" ? ")" : openCh === "{" ? "}" : null;
  if (!closeCh) throw new Error(`matchDelim: unsupported opener '${openCh}' at ${openIdx}`);
  let depth = 0;
  for (let i = openIdx; i < src.length; i++) {
    if (src[i] === openCh) depth++;
    else if (src[i] === closeCh) {
      depth--;
      if (depth === 0) return i;
    }
  }
  throw new Error(`matchDelim: unbalanced '${openCh}' opened at ${openIdx}`);
}

/* Drop comments before any source SCAN. A gate that reads source is otherwise
 * satisfied by PROSE — route()'s own comments name `viewDashboard("plugin-vars",
 * …)`, `viewHome`, `viewResources()` in branches that call none of them, and the
 * first of those would win the destination match. Whole-line `//` only (every
 * comment in the rendered route() is one), so a regex literal like /^#\/?/ is
 * never mistaken for a comment. */
function stripComments(src) {
  return src
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .split("\n")
    .filter((l) => !/^\s*\/\//.test(l))
    .join("\n");
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

/* ── route() dispatch derivation (index.html) ──────────────────────────────────
 * Reads the if/else ladder route() actually ships and returns it as an ordered
 * list of {kind, …, destination}. NOTHING about the IA is written down here: the
 * branch predicates and the handler each branch lands on are both read out of the
 * source, so a renamed section, a retargeted handler or a deleted branch moves
 * the derived destination and the committed fixture catches the drift. */

// The call a branch body dispatches to. `window.` is optional so
// `window.__openPlugin(…)` and a bare `viewResources()` both derive.
const DEST_CALL_RE = /\b(?:window\.)?(__openPlugin|view[A-Za-z]\w*)\s*\(/;

function branchDestination(bodyRaw) {
  const body = stripComments(bodyRaw);
  const m = DEST_CALL_RE.exec(body);
  if (!m) return null;
  const name = m[1];
  if (name !== "viewDashboard") return name;
  // viewDashboard's FIRST argument names the tab actually landed on — that, not
  // the section, is the destination (#/guardrails lands on heimdall).
  const argsOpen = body.indexOf("(", m.index);
  const args = body.slice(argsOpen + 1, matchDelim(body, argsOpen));
  const first = args.split(",")[0].trim();
  const lit = first.match(/^"([^"]*)"$/);
  if (lit) return `viewDashboard:${lit[1]}`;
  if (first === "section") return "viewDashboard:${section}";
  throw new Error(`route(): viewDashboard() first argument is not derivable: ${first}`);
}

function branchCondition(cond) {
  // `section.startsWith("plugin-") && section !== "plugin-vars"` — prefix branch
  // with its exclusions. Checked first: it also contains `!==` comparisons.
  const prefix = cond.match(/startsWith\(\s*"([^"]*)"\s*\)/);
  if (prefix) {
    const except = [...cond.matchAll(/section\s*!==\s*"([^"]*)"/g)].map((x) => x[1]);
    return { kind: "prefix", prefix: prefix[1], except };
  }
  // `section === "catalog" || section === "discover"`
  const eq = [...cond.matchAll(/section\s*===\s*"([^"]*)"/g)].map((x) => x[1]);
  if (eq.length) return { kind: "equals", sections: eq };
  // `DASH_OWNER[section]`
  const map = cond.match(/\b([A-Za-z_$][\w$]*)\s*\[\s*section\s*\]/);
  if (map) return { kind: "map", map: map[1] };
  return null;
}

function parseRouteDispatch(app) {
  const routeText = sliceBetween(app, "function route(", "{");
  // The dispatch ladder starts at the first `if (…)` whose consequent is a BLOCK.
  // Located structurally, not by name: the `if (SECTION_ALIAS[section]) section =
  // …;` normalisation above it is a single statement, so it is skipped without
  // this parser knowing that any such statement exists.
  let chain = -1;
  for (let i = 0; ;) {
    const k = routeText.indexOf("if (", i);
    if (k === -1) break;
    if (k > 0 && /[\w$]/.test(routeText[k - 1])) {
      i = k + 4;
      continue;
    }
    const close = matchDelim(routeText, routeText.indexOf("(", k));
    if (/^\s*\{/.test(routeText.slice(close + 1))) {
      chain = k;
      break;
    }
    i = close + 1;
  }
  if (chain === -1)
    throw new Error("route(): no block-bodied if/else dispatch ladder found — deleted?");

  const dispatch = [];
  for (let pos = chain; ;) {
    const condOpen = routeText.indexOf("(", pos);
    const condClose = matchDelim(routeText, condOpen);
    const cond = routeText.slice(condOpen + 1, condClose).trim();
    const bodyOpen = routeText.indexOf("{", condClose);
    const bodyClose = matchDelim(routeText, bodyOpen);
    const shape = branchCondition(cond);
    if (!shape) throw new Error(`route(): dispatch condition is not derivable: ${cond}`);
    const destination = branchDestination(routeText.slice(bodyOpen + 1, bodyClose));
    if (!destination) throw new Error(`route(): branch \`${cond}\` reaches no view destination`);
    dispatch.push({ ...shape, destination, cond });

    const after = routeText.slice(bodyClose + 1);
    const mElse = after.match(/^\s*else\s*/);
    if (!mElse) break;
    if (/^if\s*\(/.test(after.slice(mElse[0].length))) {
      pos = bodyClose + 1 + mElse[0].length;
      continue;
    }
    // Terminal `else { … }` — the router's catch-all. Deliberately NOT added to
    // `dispatch`: this mirror keeps an unknown section UNRESOLVED on purpose so a
    // committed href that only reaches the fallback still fails here, while the
    // LIVE fallback (Control) still catches mistyped/non-committed deep links.
    break;
  }
  if (!dispatch.length) throw new Error("route(): dispatch ladder derived empty");
  return dispatch;
}

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
  const tabsText = sliceBetween(app, "const SECTION_TABS = ", "{");
  const navRoutes = uniqSort([...tabsText.matchAll(/route:\s*"(#\/[^"]*)"/g)].map((m) => m[1]));
  return {
    navIds: [...new Set(navIds)],
    navValues: [...navValues],
    alias,
    owner,
    navRoutes,
    // Named maps a derived `MAP[section]` branch can look itself up in. An
    // unknown map name throws in resolveIndex rather than resolving nothing.
    maps: { SECTION_ALIAS: alias, DASH_OWNER: owner },
    dispatch: parseRouteDispatch(app),
  };
}
// Walks the DERIVED route() ladder in source order (parseRouteDispatch). Nothing
// about the IA is written down here — not `learn → viewResources`, not the
// plugin-* exclusion, not the four-destination landings: each is read out of the
// branch it lives in, so the gate asserts the two generated surfaces against EACH
// OTHER rather than against a constant that keeps passing after the router moves.
// Returns the destination handler string, or UNRESOLVED when the section reaches
// only the terminal `else`. NOTE (P5, dashboard-consumption): the LIVE fallback
// lands on Control (a real destination), but this mirror keeps the unknown case
// UNRESOLVED on purpose — it preserves the gate's teeth (a committed href that
// only reaches the catch-all fails here), while the Control safety-net catches
// mistyped/non-committed deep links (proven by the blank-host Playwright
// regression test, not this checker).
function resolveIndex(section, R) {
  let s = section;
  if (R.alias[s]) s = R.alias[s];
  for (const b of R.dispatch) {
    if (b.kind === "prefix") {
      if (s.startsWith(b.prefix) && !b.except.includes(s))
        return { resolved: true, destination: b.destination };
    } else if (b.kind === "equals") {
      if (b.sections.includes(s)) return { resolved: true, destination: b.destination };
    } else if (b.kind === "map") {
      const m = R.maps[b.map];
      if (!m) throw new Error(`route(): branch consults unknown map ${b.map}[section]`);
      if (m[s]) return { resolved: true, destination: b.destination.replace("${section}", s) };
    }
  }
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
// Mirrors activate(tab, sub): unknown tab → "settings" (the P5 fallback); modeled
// here as UNRESOLVED so a committed href to a non-existent tab still fails. learn+sub
// → openConcept(sub), so the concept must exist.
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

/* ── shipped sibling pages (pitch.html and every other root-level *.html) ───
 * Cross-file hrefs only: `href="index.html#/<route>"` / `href="dashboard.html#/…"`.
 * Same-file `href="#/…"` on index/dashboard is the surface enumeration above.
 * Each href is resolved through the SAME derived router as the target surface —
 * no list of expected pitch.html routes is written down here. */
const CROSS_FILE_HREF_RE = /href\s*=\s*["']([^"'#]+\.html)#(\/[^"']*)["']/gi;

function extractCrossFileHrefs(html, sourcePath) {
  const src = basename(sourcePath);
  const out = [];
  for (const m of html.matchAll(CROSS_FILE_HREF_RE)) {
    const target = basename(m[1]);
    if (target !== "index.html" && target !== "dashboard.html") continue;
    out.push({ source: src, target, route: `#${m[2]}`, href: `${m[1]}#${m[2]}` });
  }
  return out;
}

function listSiblingPages(explicit) {
  if (explicit) {
    if (!explicit.length) {
      throw new Error("--siblings is empty — refusing to skip the sibling #/ scan");
    }
    return explicit;
  }
  if (SIBLINGS !== null) {
    const paths = SIBLINGS.split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    if (!paths.length) {
      throw new Error("--siblings is empty — refusing to skip the sibling #/ scan");
    }
    return paths;
  }
  const names = readdirSync(".").filter((n) => n.endsWith(".html") && !n.startsWith("."));
  if (!names.length) {
    throw new Error(
      "no root-level *.html to scan for sibling #/ hrefs — refusing to pass vacuously",
    );
  }
  return names;
}

function resolveSiblingHref(target, route, indexRouter, dashRouter) {
  const [section, sub] = splitRoute(route);
  if (target === "index.html") return resolveIndex(section, indexRouter);
  if (target === "dashboard.html") return resolveDash(section, sub, dashRouter);
  return { resolved: false, destination: `UNRESOLVED:unknown-target:${target}` };
}

function assertSiblings(paths, indexRouter, dashRouter) {
  let hrefCount = 0;
  for (const p of paths) {
    let html;
    try {
      html = readFileSync(p, "utf8");
    } catch (e) {
      failures.push(`sibling ${p}: cannot read: ${e.message}`);
      continue;
    }
    for (const h of extractCrossFileHrefs(html, p)) {
      hrefCount += 1;
      const r = resolveSiblingHref(h.target, h.route, indexRouter, dashRouter);
      A(
        r.resolved,
        `sibling ${h.source}: href "${h.href}" does not resolve ` +
          `(destination ${r.destination}) — rotten shipped #/ link`,
      );
    }
  }
  return hrefCount;
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

/* ── run (emit / assert) ─────────────────────────────────────────────────── */
function runCheck(opts = {}) {
  failures.length = 0;
  const dashPath = opts.dashPath ?? DASH_PATH;
  const indexPath = opts.indexPath ?? INDEX_PATH;
  const fixturePath = opts.fixturePath ?? FIXTURE_PATH;
  const emit = opts.emit ?? false;
  const scanSiblings = opts.scanSiblings !== false && !emit;

  let dashHtml, indexHtml;
  try {
    dashHtml = readFileSync(dashPath, "utf8");
    indexHtml = readFileSync(indexPath, "utf8");
  } catch (e) {
    return { exit: 2, failures: [`cannot read surface html: ${e.message}`], siblingHrefs: 0 };
  }

  let surfaces, indexRouter, dashRouter;
  try {
    surfaces = {
      dashboard: buildSurface("dashboard", dashHtml),
      index: buildSurface("index", indexHtml),
    };
    indexRouter = parseIndexRouter(indexHtml);
    dashRouter = parseDashRouter(dashHtml);
  } catch (e) {
    return { exit: 2, failures: [`cannot derive router: ${e.message}`], siblingHrefs: 0 };
  }

  if (emit) {
    // PB-2 (FORGE dashboard-consumption): --emit regenerates `surfaces` from the
    // live HTML, but the hand-authored `required_routes` FLOOR must be carried
    // through VERBATIM. Without this, removing a required route's href and
    // re-emitting would silently launder the removal (the fixture would simply stop
    // listing it) — the exact anti-laundering hole C5 needs closed. So read the
    // prior fixture and preserve its floor unchanged.
    let priorRequired;
    try {
      priorRequired = JSON.parse(readFileSync(fixturePath, "utf8")).required_routes;
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
    mkdirSync(dirname(fixturePath), { recursive: true });
    writeFileSync(fixturePath, JSON.stringify(out, null, 2) + "\n");
    return { exit: 0, failures: [], surfaces, emitted: fixturePath, siblingHrefs: 0 };
  }

  let fixture;
  try {
    fixture = JSON.parse(readFileSync(fixturePath, "utf8"));
  } catch (e) {
    return {
      exit: 2,
      failures: [
        `cannot read route fixture ${fixturePath}: ${e.message} ` +
          `(run \`node scripts/check-committed-routes.mjs --emit\` to generate it)`,
      ],
      siblingHrefs: 0,
    };
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

  let siblingHrefs = 0;
  if (scanSiblings) {
    try {
      const pages = listSiblingPages(opts.siblings);
      siblingHrefs = assertSiblings(pages, indexRouter, dashRouter);
    } catch (e) {
      failures.push(e.message);
    }
  }

  return {
    exit: failures.length ? 2 : 0,
    failures: [...failures],
    surfaces,
    siblingHrefs,
    dispatch: indexRouter.dispatch,
  };
}

function report(result) {
  if (result.emitted) {
    const d = result.surfaces.dashboard;
    const i = result.surfaces.index;
    console.log(`emitted ${result.emitted}`);
    console.log(
      `  dashboard: ${d.href_count} hrefs → ${d.distinct_static} distinct static routes, ${d.distinct_dynamic} dynamic`,
    );
    console.log(
      `  index:     ${i.href_count} hrefs → ${i.distinct_static} distinct static routes, ${i.distinct_dynamic} dynamic, ${i.nav_routes.length} sub-nav routes`,
    );
    return 0;
  }
  if (result.exit !== 0) {
    console.error(`FAIL: committed-route contract violations (${result.failures.length}):`);
    for (const f of result.failures) console.error("  - " + f);
    return 2;
  }
  const s = result.surfaces;
  console.log(
    `OK: every committed #/… resolves by destination — dashboard ${s.dashboard.href_count} hrefs / ` +
      `${s.dashboard.distinct_static} routes, index ${s.index.href_count} hrefs / ` +
      `${s.index.distinct_static} routes + ${s.index.dynamic_href_templates.length} templates + ` +
      `${s.index.nav_routes.length} sub-nav routes; ` +
      `${result.siblingHrefs} sibling #/ hrefs; all destinations real.`,
  );
  return 0;
}

/* ── teeth ───────────────────────────────────────────────────────────────── */
// The live dispatch arm, not the comment that names the same comparison.
const LEARN_EQ = 'else if (section === "learn")';
const PITCH_LEARN_HREF = 'href="index.html#/learn"';
// Planted rot — assembled so a source-scan of THIS file cannot satisfy a
// sibling-href matcher (self-non-recursion). # noport
const ROTTEN_ROUTE = "#/" + "this-route-does-not-exist";

function retargetLearnBranch(html) {
  const i = html.indexOf(LEARN_EQ);
  if (i === -1) throw new Error(`learn branch not found (${LEARN_EQ})`);
  const close = html.indexOf("} else", i);
  if (close === -1) throw new Error("learn branch has no trailing } else");
  const body = html.slice(i, close);
  if (!body.includes("viewResources()")) {
    throw new Error("learn branch has no viewResources() to retarget — mutation would be a no-op");
  }
  return (
    html.slice(0, i) + body.replace("viewResources()", "viewMarketplace()") + html.slice(close)
  );
}

function plantRottenPitch(html) {
  if (!html.includes(PITCH_LEARN_HREF)) {
    throw new Error(`pitch.html is missing ${PITCH_LEARN_HREF} — cannot plant rot`);
  }
  return html.replace(PITCH_LEARN_HREF, `href="index.html${ROTTEN_ROUTE}"`);
}

function mustFail() {
  const tmp = mkdtempSync(join(tmpdir(), "g205-mustfail-"));
  try {
    const planted = plantRottenPitch(readFileSync("pitch.html", "utf8"));
    const rotten = join(tmp, "pitch-rotten.html");
    writeFileSync(rotten, planted);
    return runCheck({ siblings: [rotten] });
  } catch (e) {
    return { exit: 2, failures: [e.message], siblingHrefs: 0 };
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}

function selfTest() {
  const results = [];
  const note = (ok, msg) => {
    results.push(!!ok);
    console.log(ok ? `  ✓ ${msg}` : `  ✗ ${msg}`);
  };

  const live = runCheck({});
  note(live.exit === 0, "live tree (surfaces + sibling #/ hrefs) is clean");
  note(
    Array.isArray(live.dispatch) &&
      live.dispatch.some((b) => b.kind === "equals" && b.sections.includes("learn")),
    "route() learn branch is DERIVED from source (not a constant ladder)",
  );

  const tmp = mkdtempSync(join(tmpdir(), "g205-selftest-"));
  try {
    const retargeted = retargetLearnBranch(readFileSync(INDEX_PATH, "utf8"));
    const idxPath = join(tmp, "index-retarget.html");
    writeFileSync(idxPath, retargeted);
    const drifted = runCheck({ indexPath: idxPath, scanSiblings: false });
    note(
      drifted.exit === 2 &&
        drifted.failures.some((f) => f.includes("#/learn") && f.includes("drifted")),
      "retargeting the learn branch is exit-2 destination drift (a hard-coded learn→viewResources would stay green)",
    );

    const rottenPath = join(tmp, "pitch-rotten.html");
    writeFileSync(rottenPath, plantRottenPitch(readFileSync("pitch.html", "utf8")));
    const rotten = runCheck({ siblings: [rottenPath] });
    note(
      rotten.exit === 2 && rotten.failures.some((f) => f.includes("this-route-does-not-exist")),
      "a rotten pitch.html #/ href is exit 2",
    );

    const goodPath = join(tmp, "pitch-good.html");
    writeFileSync(
      goodPath,
      '<a href="index.html#/learn">ok</a><a href="index.html#/discover">ok</a>\n',
    );
    const good = runCheck({ siblings: [goodPath] });
    note(good.exit === 0, "a sibling whose #/ hrefs all resolve is silent");

    const missing = runCheck({ siblings: [join(tmp, "no-such-sibling.html")] });
    note(missing.exit === 2, "a missing sibling file fails closed (exit 2)");
  } catch (e) {
    note(false, `self-test threw: ${e.message}`);
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }

  const spawned = spawnSync(process.execPath, [SELF_PATH, "--must-fail"], { encoding: "utf8" });
  note(spawned.status === 2, `--must-fail exits 2 (got ${spawned.status})`);

  const ok = results.every(Boolean);
  console.log(ok ? "\nteeth verified" : "\nTEETH BROKEN");
  return ok ? 0 : 2;
}

/* ── main ─────────────────────────────────────────────────────────────────── */
if (SELF_TEST) process.exit(selfTest());
if (MUST_FAIL) {
  const planted = mustFail();
  process.exit(report(planted));
}
if (EMIT) process.exit(report(runCheck({ emit: true })));
process.exit(report(runCheck({})));
