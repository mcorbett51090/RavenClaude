#!/usr/bin/env node
/* device_matrix.mjs: render a site at every screen it will meet and run
 * layout-probe.js on each page, so "pixel-perfect on every screen" is measured
 * rather than eyeballed at two widths.
 *
 * USAGE
 *   node device_matrix.mjs --dir dist                     a built site, served locally
 *   node device_matrix.mjs --url http://localhost:4321/   a running server (repeatable)
 *     --pages /,/menu/,/visit/   paths to test (default: / only)
 *     --manifest FILE            test every page a site manifest lists (repeatable)
 *     --quick                    one viewport per device class (default)
 *     --full                     every row of adaptive-layout's device table
 *     --sweep 320:1600:8         also every 8px from 320 to 1600 (catches the
 *                                in-between widths container queries produce)
 *     --themes light,dark,…      themes on the quick rows (default: all six: light,
 *                                dark, forced, contrast, contrast-dark, motion;
 *                                every theme but motion runs with reduced motion)
 *     --no-photo                 skip the photo-contrast capture (faster)
 *     --no-ink                   skip the text-hidden capture (faster)
 *     --no-print                 skip the print pass
 *     --shots DIR                a FULL-PAGE PNG per page × viewport × theme, for
 *                                visual-regression baselines
 *     --block-shots DIR          a PNG per block, header and footer at 390px and
 *                                1280px in light and dark: the "look at it" step
 *                                (a full page shrinks detail away)
 *     --json FILE                write every finding as JSON
 *     --chrome PATH              a Chromium binary (else CHROME_BIN, else Playwright's)
 *   node device_matrix.mjs --self-test
 *     renders the kit's example site and its stress fixtures and requires both
 *     clean, plants each defect the probe knows in a synthetic page built on the
 *     kit's stylesheets and requires each to be reported, and requires look-alikes
 *     of those defects to pass. A probe that has never failed proves nothing.
 *
 * Every state is probed twice: as loaded, and with every <details> open (a menu,
 * an FAQ answer), reporting what the opened details hold. On each row's first
 * theme every word is checked for ink (text-hidden: captured with the text drawn
 * and hidden, so a cover, a ::before/::after layer or a mask that no element
 * hit-test sees is still found). Any image, font or media file the page asks for
 * that answers 4xx is resource-failed, and a --dir site built for a basePath is
 * served ONLY under that path, as its host serves it. Each page is measured once
 * in its print stylesheet at A4 width. On the widest row the
 * kit's header is measured: a menu switch it can never reach is `nav-hidden`, and
 * the value to pin in chrome.menuBelow is printed. Progress goes to stderr.
 *
 * Breakpoint edges: every width a @media rule in the page's own CSS names is
 * tested at that width and one pixel either side (read from the CSSOM, so a
 * minifier's range syntax `(width<=860px)` and em units are handled).
 *
 * Layout shift must REPEAT to count. Measured 2026-10-27: headless Chromium
 * paints a first frame missing some author styles in about 4–8% of loads of a
 * clean page (padding and font size arrive one frame late; one bundled
 * stylesheet did not change the rate; the mechanism is not known). A shift the
 * page itself causes repeats on every load. So a page state that shifts is
 * reloaded in fresh contexts: shifting in 5 of 5 loads is a finding, and fewer
 * is printed as a note with its count, never hidden. (It was 3 of 3 until a run
 * on a loaded machine, two other browsers busy, reached 3 of 3 on a page that
 * shifted in 0 of 12 loads once the machine was quiet.)
 *
 * Needs Playwright (`npm i -D playwright`, then `npx playwright install chromium`)
 * resolvable from the current directory. Exit: 0 clean, 1 findings, 2 could not run.
 *
 * Chromium is not WebKit: emulation sets the width, DPR, touch and the viewport
 * tag, but has no Safari toolbar, no safe areas and no dynamic viewport. A green
 * run is necessary, not sufficient. Finish on a real iPhone and iPad.
 */
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { createServer } from "node:http";
import { deflateSync } from "node:zlib";
import {
  mkdtempSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
  existsSync,
  statSync,
  rmSync,
  copyFileSync,
  cpSync,
} from "node:fs";
import { join, resolve, extname, dirname, normalize, sep } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const PROBE = readFileSync(join(HERE, "layout-probe.js"), "utf8");
const LAYOUT_CSS = join(HERE, "..", "templates", "block-site", "layout.css");

// ─── viewports (adaptive-layout Step 7; `quick` = one per device class) ──────
const VIEWPORTS = [
  { id: "reflow-320", w: 320, h: 568, dpr: 2, mobile: true, quick: true },
  { id: "iphone-se", w: 375, h: 667, dpr: 2, mobile: true },
  { id: "iphone", w: 390, h: 844, dpr: 3, mobile: true, quick: true },
  { id: "iphone-pro", w: 402, h: 874, dpr: 3, mobile: true },
  { id: "android", w: 420, h: 912, dpr: 2.625, mobile: true },
  { id: "iphone-max", w: 440, h: 956, dpr: 3, mobile: true },
  { id: "iphone-se-land", w: 667, h: 375, dpr: 2, mobile: true },
  { id: "iphone-land", w: 874, h: 402, dpr: 3, mobile: true, quick: true },
  { id: "iphone-max-land", w: 956, h: 440, dpr: 3, mobile: true },
  { id: "duo-outer", w: 382, h: 580, dpr: 3, mobile: true },
  { id: "duo-outer-land", w: 594, h: 368, dpr: 3, mobile: true },
  { id: "duo-inner", w: 669, h: 867, dpr: 3, mobile: true },
  { id: "duo-inner-land", w: 951, h: 585, dpr: 3, mobile: true },
  { id: "duo-split", w: 385, h: 571, dpr: 3, mobile: true },
  { id: "fold-cover", w: 344, h: 882, dpr: 3, mobile: true },
  { id: "fold-open", w: 836, h: 842, dpr: 2.625, mobile: true },
  { id: "ipad-mini", w: 756, h: 1158, dpr: 2, mobile: true },
  { id: "ipad", w: 820, h: 1180, dpr: 2, mobile: true, quick: true },
  { id: "ipad-pro-11", w: 834, h: 1210, dpr: 2, mobile: true },
  { id: "ipad-pro-13", w: 1032, h: 1376, dpr: 2, mobile: true },
  { id: "ipad-pro-13-land", w: 1376, h: 1032, dpr: 2, mobile: true },
  { id: "ipad-split-half", w: 688, h: 1032, dpr: 2, mobile: true },
  { id: "ipad-split-third", w: 375, h: 1032, dpr: 2, mobile: true },
  { id: "laptop-short", w: 1280, h: 720, dpr: 1, mobile: false },
  { id: "laptop", w: 1280, h: 800, dpr: 2, mobile: false, quick: true },
  { id: "laptop-15", w: 1470, h: 956, dpr: 2, mobile: false },
  { id: "desktop", w: 1920, h: 1080, dpr: 1, mobile: false, quick: true },
  { id: "desktop-qhd", w: 2560, h: 1440, dpr: 1, mobile: false },
];

const THEMES = {
  light: { colorScheme: "light", forcedColors: "none" },
  dark: { colorScheme: "dark", forcedColors: "none" },
  forced: { colorScheme: "light", forcedColors: "active" },
  contrast: { colorScheme: "light", forcedColors: "none", contrast: "more" },
  "contrast-dark": { colorScheme: "dark", forcedColors: "none", contrast: "more" },
  // Every other theme runs with reduced motion, so settling is deterministic. This
  // one does not: a reveal-on-scroll or an entrance animation that never ends, or
  // leaves content hidden, shows up here.
  motion: { colorScheme: "light", forcedColors: "none", reducedMotion: "no-preference" },
};

// Installed before any page script: the probe reads it for layout-shift.
const CLS_OBSERVER = `(() => {
  window.__layoutProbe = { cls: 0, sources: [], last: 0 };
  try {
    new PerformanceObserver((list) => {
      for (const e of list.getEntries()) {
        if (e.hadRecentInput) continue;
        window.__layoutProbe.cls += e.value;
        window.__layoutProbe.last = e.startTime;
        const node = (e.sources || []).map((s) => s.node).find((n) => n && n.nodeType === 1);
        if (node) window.__layoutProbe.sources.push(node.tagName.toLowerCase() + (node.className ? '.' + String(node.className).split(' ')[0] : '') + ' ' + e.value.toFixed(3));
      }
    }).observe({ type: 'layout-shift', buffered: true });
  } catch (_) { /* not Chromium: layout-shift is reported as not measured */ }
})();`;

// Make lazy images load, wait for fonts and image decodes, then wait until the
// page has gone 400ms without a layout shift (at most 3s), so a late shift is
// measured on every load rather than only when the probe happens to be slow.
const SETTLE = `(async () => {
  for (const img of document.images) if (img.loading === 'lazy') img.loading = 'eager';
  await Promise.race([
    Promise.all([document.fonts.ready, ...[...document.images].map((i) => i.decode().catch(() => {}))]),
    new Promise((r) => setTimeout(r, 6000)),
  ]);
  // Let every finite animation and transition end: under reduced motion the kit
  // gives each property a 0.01ms transition, and a style read inside it is stale.
  await Promise.race([
    Promise.all(document.getAnimations()
      .filter((a) => a.effect && a.effect.getComputedTiming().endTime !== Infinity)
      .map((a) => a.finished.catch(() => {}))),
    new Promise((r) => setTimeout(r, 2000)),
  ]);
  const start = performance.now();
  const m = window.__layoutProbe;
  while (performance.now() - start < 3000) {
    await new Promise((r) => setTimeout(r, 100));
    const quietSince = Math.max(start, m ? m.last : 0);
    if (performance.now() - quietSince >= 400) break;
  }
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
})()`;

// Every width a @media rule names, as CSS px, from the live CSSOM.
const BREAKPOINTS = `(() => {
  const out = new Set();
  const cq = new Set();
  const px = (n, u) => (u === 'px' ? n : n * 16);
  const scan = (rules) => {
    for (const r of rules || []) {
      const t = r.conditionText || (r.media && r.media.mediaText) || '';
      const isContainer = typeof CSSContainerRule !== 'undefined' && r instanceof CSSContainerRule;
      if (t) {
        for (const m of t.matchAll(/(min-|max-)?width\\s*(?::|[<>]=?)\\s*([\\d.]+)(px|em|rem)/g)) {
          (isContainer ? cq : out).add(Math.round(px(parseFloat(m[2]), m[3])));
        }
        for (const m of t.matchAll(/([\\d.]+)(px|em|rem)\\s*[<>]=?\\s*width/g)) {
          (isContainer ? cq : out).add(Math.round(px(parseFloat(m[1]), m[2])));
        }
      }
      if (r.cssRules) scan(r.cssRules);
    }
  };
  for (const s of document.styleSheets) { try { scan(s.cssRules); } catch (_) { /* cross-origin sheet */ } }
  return { media: [...out].sort((a, b) => a - b), container: [...cq].sort((a, b) => a - b) };
})()`;

function loadPlaywright() {
  const tries = [process.cwd() + "/", import.meta.url];
  for (const base of tries) {
    try {
      return createRequire(base)("playwright");
    } catch (_) {
      /* next */
    }
  }
  return null;
}

// ─── static server for --dir ─────────────────────────────────────────────────
const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css",
  ".js": "text/javascript",
  ".mjs": "text/javascript",
  ".json": "application/json",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".avif": "image/avif",
  ".gif": "image/gif",
  ".ico": "image/x-icon",
  ".woff2": "font/woff2",
  ".woff": "font/woff",
  ".txt": "text/plain",
  ".xml": "application/xml",
  ".webmanifest": "application/manifest+json",
};
/** Serve a built site. `prefixes` are the manifests' basePaths: a site built to
 *  live under /clinic/ links to /clinic/tokens.css, which is dist/tokens.css. */
function serve(root, prefixes = []) {
  const base = resolve(root);
  const server = createServer((req, res) => {
    let p = decodeURIComponent(new URL(req.url, "http://x").pathname);
    const prefix = prefixes.find((x) => x !== "/" && p.startsWith(x));
    if (prefix) p = "/" + p.slice(prefix.length);
    else if (prefixes.some((x) => x !== "/")) {
      // A site built for /shop/ lives only there on its host: a root URL such as
      // /fonts/brand.woff2 in its CSS 404s in production, so it 404s here too.
      res.writeHead(404, { "content-type": TYPES[".html"] }).end("not under the site's basePath");
      return;
    }
    let f = normalize(join(base, p));
    if (f !== base && !f.startsWith(base + sep)) {
      res.writeHead(403).end();
      return;
    }
    if (existsSync(f) && statSync(f).isDirectory()) f = join(f, "index.html");
    else if (!existsSync(f) && existsSync(f + ".html")) f += ".html";
    if (!existsSync(f)) {
      const nf = join(base, "404.html");
      res
        .writeHead(404, { "content-type": TYPES[".html"] })
        .end(existsSync(nf) ? readFileSync(nf) : "not found");
      return;
    }
    res
      .writeHead(200, {
        "content-type": TYPES[extname(f).toLowerCase()] || "application/octet-stream",
      })
      .end(readFileSync(f));
  });
  return new Promise((ok) =>
    server.listen(0, "127.0.0.1", () =>
      ok({ server, origin: `http://127.0.0.1:${server.address().port}` }),
    ),
  );
}

// ─── the run ─────────────────────────────────────────────────────────────────
// Files a page asks for after its stylesheets: an image in a CSS url(), a font,
// a video. One that answers 4xx is a hole in the page the layout checks cannot
// see (a missing background leaves its text on the wrong colour).
const RESOURCE_TYPES = new Set(["image", "font", "media"]);
function watchResources(page) {
  const failed = new Map();
  const origin = () => {
    try {
      return new URL(page.url()).origin;
    } catch {
      return "";
    }
  };
  page.on("response", (r) => {
    if (
      RESOURCE_TYPES.has(r.request().resourceType()) &&
      r.status() >= 400 &&
      r.url().startsWith(origin())
    )
      failed.set(r.url(), `answered ${r.status()}`);
  });
  page.on("requestfailed", (q) => {
    if (
      RESOURCE_TYPES.has(q.resourceType()) &&
      q.url().startsWith(origin()) &&
      !/ERR_ABORTED/.test(q.failure()?.errorText || "")
    )
      failed.set(q.url(), `failed (${q.failure()?.errorText || "no answer"})`);
  });
  return {
    reset: () => failed.clear(),
    findings: () =>
      [...failed].map(([url, why]) => ({
        id: "resource-failed",
        where: new URL(url).pathname,
        msg: `${new URL(url).pathname} ${why}: an image, font or media file the page asks for (check the path, and a basePath site's root-absolute url())`,
      })),
  };
}

async function probePage(page, expectedWidth, skip = []) {
  await page.evaluate(SETTLE);
  return page.evaluate(`${PROBE}\n;layoutProbe(${JSON.stringify({ expectedWidth, skip })})`);
}

/** Load a URL; a page that does not answer 2xx is a failure, never a silent pass. */
const ANALYTICS = /googletagmanager\.com|google-analytics\.com|cloudflareinsights\.com/;
/** Load a URL; a page that does not answer 2xx is a failure, never a silent pass,
 *  and so is a page whose stylesheet or script did not load: everything measured
 *  on it would be the browser's defaults, not the site. */
async function load(page, url) {
  const broken = [];
  const kinds = new Set(["stylesheet", "script"]);
  const onResponse = (r) => {
    if (kinds.has(r.request().resourceType()) && r.status() >= 400)
      broken.push(`${r.url()} answered ${r.status()}`);
  };
  const onFailed = (q) => {
    if (kinds.has(q.resourceType()) && !ANALYTICS.test(q.url())) broken.push(`${q.url()} failed`);
  };
  page.on("response", onResponse);
  page.on("requestfailed", onFailed);
  let res;
  try {
    res = await page.goto(url, { waitUntil: "load" });
  } finally {
    page.off("response", onResponse);
    page.off("requestfailed", onFailed);
  }
  if (!res || res.status() < 200 || res.status() > 299)
    throw new Error(`${url} answered ${res ? res.status() : "nothing"}; check --pages`);
  if (broken.length)
    throw new Error(
      `${url}: ${broken[0]}${broken.length > 1 ? ` (and ${broken.length - 1} more)` : ""}; the page rendered without it, so its layout is not the site's (check --dir, and the manifest's basePath)`,
    );
}

// A layout shift is a finding only when it repeats in every one of this many loads.
const SHIFT_LOADS = 5;

/** Reload a page that shifted in fresh contexts; count the loads that shift again. */
async function reloadShifts(browser, v, theme, url, times) {
  let n = 0;
  for (let i = 0; i < times; i++) {
    const ctx = await newStateContext(browser, v, theme);
    const page = await ctx.newPage();
    await load(page, url);
    const { findings } = await probePage(page, v.w);
    if (findings.some((x) => x.id === "layout-shift")) n++;
    await ctx.close();
  }
  return n;
}

// The kit's header (block_site_render.py): what its brand, links and action
// really need on one row, against the width the renderer switches to the menu
// at, and the widest the header can ever be (--content-max). Measured, so a
// brand font or another script cannot fool it the way the estimate can.
const NAV_FIT = `(async () => {
  const bar = document.querySelector(".site-header__bar");
  const rule = [...document.querySelectorAll("head style")]
    .map((s) => s.textContent.match(/width < ([0-9.]+)rem/)).find(Boolean);
  if (!bar || !bar.querySelector(".site-nav--inline") || !rule) return null;
  const rem = parseFloat(getComputedStyle(document.documentElement).fontSize);
  const st = document.createElement("style");
  st.textContent = ".site-menu{display:none!important}.site-nav--inline{display:block!important}"
    + ".site-header__action{display:inline-flex!important}"
    + ".site-header__bar,.site-nav--inline ul{flex-wrap:nowrap!important}"
    + ".site-header .brand{flex:none!important;max-inline-size:none!important}";
  document.head.append(st);
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  const kids = [...bar.children].filter((k) => getComputedStyle(k).display !== "none");
  const need = kids.reduce((w, k) => w + k.getBoundingClientRect().width, 0)
    + (kids.length - 1) * parseFloat(getComputedStyle(bar).columnGap);
  const probe = document.createElement("div");
  probe.style.inlineSize = "var(--content-max)";
  document.body.append(probe);
  const max = probe.getBoundingClientRect().width;
  probe.remove();
  st.remove();
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  return { need: need / rem, at: parseFloat(rule[1]), max: max / rem };
})()`;

// What a closed <details> hides (a site menu, an FAQ answer) is laid out only
// when it opens, so the probe runs again with every one open, and reports only
// what is inside an opened <details> (plus page-level findings, such as the
// page scrolling sideways). Checks that read what is UNDER an open menu
// (overlap, anchors, fixed bars) are skipped: a dropdown covers the page by design.
const OPEN_SKIP = [
  "layout-shift",
  "font-failed",
  "images",
  "overlap",
  "anchor-obscured",
  "covered",
];
async function detailsOpen(page, width) {
  const n = await page.evaluate(`(() => {
    const shut = [...document.querySelectorAll("details:not([open])")];
    for (const d of shut) { d.setAttribute("data-dm-opened", ""); d.open = true; }
    return shut.length;
  })()`);
  if (!n) return [];
  await page.evaluate(SETTLE);
  const { findings } = await page.evaluate(
    `${PROBE}\n;layoutProbe(${JSON.stringify({ expectedWidth: width, skip: OPEN_SKIP, within: "details[data-dm-opened]" })})`,
  );
  await page.evaluate(`(() => {
    for (const d of document.querySelectorAll("details[data-dm-opened]")) { d.open = false; d.removeAttribute("data-dm-opened"); }
  })()`);
  await page.evaluate(FRAME);
  return findings.map((x) => ({ ...x, msg: `${x.msg} (with every <details> open)` }));
}

async function newStateContext(browser, v, theme) {
  const ctx = await browser.newContext({
    viewport: { width: v.w, height: v.h },
    deviceScaleFactor: v.dpr,
    isMobile: v.mobile,
    hasTouch: v.mobile,
    reducedMotion: "reduce",
    ...THEMES[theme],
  });
  await ctx.addInitScript(CLS_OBSERVER);
  await ctx.route(ANALYTICS, (r) => r.abort());
  return ctx;
}

// ─── photo-contrast: text over a photograph, on composited pixels ────────────
// No colour stands in for a photograph, so the probe's text-contrast check skips
// text over one, and this scores it instead (knowledge/text-over-photo-contrast-
// 2026.md §1): hide every glyph (text-shadow and the element's own background
// stay, because they sit behind the glyphs), capture the VIEWPORT, and score each
// text line's box pixel by pixel against the text colour composited at its own
// alpha × its ancestors' opacity. The 5th-percentile pixel is the reading: a
// bright patch behind a fifth of a line fails, one specular highlight does not.
// 4.5:1, or 3:1 at 24px / 18.66px bold. The percentile is a HEURISTIC; WCAG names
// no sampling rule for a photograph. Ported from the owner's factory, where it
// was built and broken on purpose (RavenPower-website-factory PR #131).
const PHOTO_FIND = `(async () => {
  // Two frames first: under reduced motion a style changed just before this
  // (a mutation, a theme) is still mid-transition, and its colour reads stale.
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  for (const img of document.images) if (img.loading === 'lazy') img.loading = 'eager';
  await Promise.race([
    Promise.all([...document.images].map((i) => i.decode().catch(() => {}))),
    new Promise((r) => setTimeout(r, 4000)),
  ]);
  const SX = scrollX, SY = scrollY;
  const vis = (el) => {
    if (el.closest('[aria-hidden="true"],[hidden],[inert]')) return false;
    if (el.closest('details:not([open]) > :not(summary)')) return false;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.visibility === 'collapse') return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const path = (el) => {
    const parts = [];
    for (let e = el; e && e.nodeType === 1 && parts.length < 4; e = e.parentElement) {
      let s = e.tagName.toLowerCase();
      if (e.id) { s += '#' + e.id; parts.unshift(s); break; }
      if (e.dataset && e.dataset.block) s += '[data-block="' + e.dataset.block + '"]';
      else { const c = [...e.classList].slice(0, 2).join('.'); if (c) s += '.' + c; }
      parts.unshift(s);
    }
    return parts.join(' > ');
  };
  const media = [];
  for (const m of document.body.querySelectorAll('*')) {
    const cs = getComputedStyle(m);
    // A photo, a canvas, or a background image or gradient: no one colour stands
    // in for any of them, so text over them is scored on pixels.
    if (!/^(IMG|VIDEO|CANVAS)$/.test(m.tagName) && !/url\\(|gradient\\(/.test(cs.backgroundImage)) continue;
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = m.getBoundingClientRect();
    if (r.width < 48 || r.height < 48) continue;
    media.push({ el: m, l: r.left + SX, t: r.top + SY, r: r.right + SX, b: r.bottom + SY });
  }
  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const rgba = (css) => {
    cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = css; cx.fillRect(0, 0, 1, 1);
    const d = cx.getImageData(0, 0, 1, 1).data;
    return [d[0], d[1], d[2], d[3] / 255];
  };
  const clipTo = (el, q) => {
    for (let a = el; a && a !== document.body; a = a.parentElement) {
      const cs = getComputedStyle(a);
      if (cs.overflowX === 'visible' && cs.overflowY === 'visible' && cs.clip === 'auto' && cs.clipPath === 'none') continue;
      const r = a.getBoundingClientRect();
      q = { l: Math.max(q.l, r.left + SX), t: Math.max(q.t, r.top + SY), r: Math.min(q.r, r.right + SX), b: Math.min(q.b, r.bottom + SY) };
    }
    return q;
  };
  const groups = new Map();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const range = document.createRange();
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    if (!n.nodeValue.trim()) continue;
    const el = n.parentElement;
    if (!el || el.closest('svg,script,style,noscript,template,canvas') || !vis(el)) continue;
    range.selectNodeContents(n);
    const rects = [...range.getClientRects()]
      .map((r) => clipTo(el, { l: r.left + SX, t: r.top + SY, r: r.right + SX, b: r.bottom + SY }))
      .filter((q) => q.r - q.l >= 2 && q.b - q.t >= 6);
    // Only the part of a line that lies over a photo is scored, and only when
    // that part is a real share of the line: a line box whose top edge grazes a
    // band above it has its glyphs on the flat colour, not on the photo.
    const over = [];
    for (const q of rects) {
      let best = null;
      for (const m of media) {
        if (el.contains(m.el)) continue;
        const i = { l: Math.max(q.l, m.l), t: Math.max(q.t, m.t), r: Math.min(q.r, m.r), b: Math.min(q.b, m.b) };
        if (i.r - i.l < 2 || i.b - i.t < Math.max(6, (q.b - q.t) / 3)) continue;
        if (!best || (i.r - i.l) * (i.b - i.t) > (best.r - best.l) * (best.b - best.t)) best = i;
      }
      if (best) over.push(best);
    }
    if (!over.length) continue;
    if (!groups.has(el)) groups.set(el, []);
    groups.get(el).push(...over);
  }
  const out = [];
  for (const [el, rects] of groups) {
    const cs = getComputedStyle(el);
    if (cs.backgroundClip === 'text' || cs.webkitBackgroundClip === 'text') continue;
    // Forced colours paint the forced color; the fill still reports the author's.
    const fill = matchMedia('(forced-colors: active)').matches ? cs.color : cs.webkitTextFillColor || cs.color;
    const fg = rgba(fill);
    let alpha = fg[3];
    for (let a = el; a && a !== document.documentElement; a = a.parentElement) alpha *= Number(getComputedStyle(a).opacity);
    if (alpha < 0.02) continue;
    const size = parseFloat(cs.fontSize), weight = Number(cs.fontWeight) || 400;
    out.push({ k: out.length, where: path(el), text: el.textContent.trim().replace(/\\s+/g, ' ').slice(0, 40),
      fg: fg.slice(0, 3), alpha, size, large: size >= 24 || (size >= 18.66 && weight >= 700),
      rects, top: Math.min(...rects.map((r) => r.t)), bottom: Math.max(...rects.map((r) => r.b)) });
    el.setAttribute('data-dm-photo', String(out.length - 1));
  }
  return out;
})()`;

// ':root *' outranks a bare '*', so a page's own !important colour cannot survive
// the hide. Whether the hide LANDED is asserted, not assumed.
// The kit's reduced-motion rule gives every property a 0.01ms transition, from a
// layered !important that no unlayered rule can switch off; so the hide waits two
// frames for that transition to end before it is checked and the capture taken.
const PHOTO_HIDE = `(async () => {
  const s = document.createElement('style'); s.setAttribute('data-dm-photo-hide', '');
  s.textContent = ':root *,:root *::before,:root *::after{-webkit-text-fill-color:transparent!important;'
    + 'text-decoration-color:transparent!important;caret-color:transparent!important}'
    + ':root{scroll-behavior:auto!important}';
  document.head.appendChild(s);
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  return [...document.querySelectorAll('[data-dm-photo]')]
    .filter((el) => !/^rgba\\(0, 0, 0, 0\\)$|^transparent$/.test(getComputedStyle(el).webkitTextFillColor))
    .map((el) => el.tagName.toLowerCase() + ' ' + getComputedStyle(el).webkitTextFillColor);
})()`;
const PHOTO_UNHIDE = `(() => { for (const s of document.querySelectorAll('style[data-dm-photo-hide]')) s.remove();
  for (const el of document.querySelectorAll('[data-dm-photo]')) el.removeAttribute('data-dm-photo'); })()`;

const PHOTO_SAMPLE = (b64, cands, dpr) => `(async () => {
  const C = ${JSON.stringify(cands)};
  const SX = scrollX, SY = scrollY, W = innerWidth, H = innerHeight;
  const img = new Image(); img.src = 'data:image/png;base64,${b64}'; await img.decode();
  const k = img.width / W;
  const geometry = { k, kh: img.height / H, dpr: ${dpr}, w: img.width, h: img.height, W, H };
  const cv = document.createElement('canvas'); cv.width = img.width; cv.height = img.height;
  const ctx = cv.getContext('2d', { willReadFrequently: true }); ctx.drawImage(img, 0, 0);
  const data = ctx.getImageData(0, 0, img.width, img.height).data;
  const LIN = Array.from({ length: 256 }, (_, v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); });
  const Y = (r, g, b) => 0.2126 * LIN[Math.round(r)] + 0.7152 * LIN[Math.round(g)] + 0.0722 * LIN[Math.round(b)];
  const underChrome = (el, x, y) => {
    for (let e = document.elementFromPoint(x, y); e; e = e.parentElement) {
      if (e === el || e.contains(el)) return false;
      const p = getComputedStyle(e).position;
      if (p === 'fixed' || p === 'sticky') return true;
    }
    return false;
  };
  const step = Math.max(1, Math.round(k));
  const res = [];
  for (const c of C) {
    const el = document.querySelector('[data-dm-photo="' + c.k + '"]');
    const lines = c.rects.map((q) => ({ l: q.l - SX, t: q.t - SY, r: q.r - SX, b: q.b - SY }))
      .filter((q) => q.t >= 0 && q.b <= H && q.r > 0 && q.l < W);
    if (!el || !lines.length) continue;
    const full = lines.length === c.rects.length;
    const q0 = lines[0];
    if (underChrome(el, Math.min(W - 1, Math.max(0, (q0.l + q0.r) / 2)), (q0.t + q0.b) / 2)) continue;
    const [fr, fgc, fb] = c.fg, a = c.alpha;
    const ratios = [];
    for (const q of lines) {
      const x0 = Math.max(0, Math.round(q.l * k)), x1 = Math.min(img.width, Math.round(q.r * k));
      const y0 = Math.max(0, Math.round(q.t * k)), y1 = Math.min(img.height, Math.round(q.b * k));
      for (let y = y0; y < y1; y += step) for (let x = x0; x < x1; x += step) {
        const i = (y * img.width + x) * 4;
        const br = data[i], bg = data[i + 1], bb = data[i + 2];
        const Lb = Y(br, bg, bb);
        const Lt = Y(a * fr + (1 - a) * br, a * fgc + (1 - a) * bg, a * fb + (1 - a) * bb);
        ratios.push((Math.max(Lb, Lt) + 0.05) / (Math.min(Lb, Lt) + 0.05));
      }
    }
    if (!ratios.length) continue;
    ratios.sort((x, y) => x - y);
    res.push({ k: c.k, full, n: ratios.length, p5: ratios[Math.floor(ratios.length * 0.05)],
      median: ratios[Math.floor(ratios.length / 2)] });
  }
  return { geometry, res };
})()`;

// ─── text a reader can see ───────────────────────────────────────────────────
// Every word on the page is found by its own range, the page is captured with
// the text drawn and again with it hidden, and a word whose pixels never change
// was never visible: something covers it (a badge, a ::before or ::after layer, a
// sticky bar), a mask fades it out, or it is drawn off its clipping box. Pixels,
// because no element hit-test sees a pseudo-element, a mask or a partial cover.
const INK_FIND = `(async () => {
  // A focused control can move (a skip link slides in on focus): nothing is
  // focused, and every finite transition has ended, before a word is found.
  if (document.activeElement && document.activeElement !== document.body) document.activeElement.blur();
  for (const an of document.getAnimations()) {
    try { if (an.effect && an.effect.getComputedTiming().endTime !== Infinity) an.finish(); } catch (e) {}
  }
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  for (const img of document.images) if (img.loading === 'lazy') img.loading = 'eager';
  await Promise.race([
    Promise.all([...document.images].map((i) => i.decode().catch(() => {}))),
    new Promise((r) => setTimeout(r, 4000)),
  ]);
  const SX = scrollX, SY = scrollY;
  const vis = (el) => {
    if (el.closest('[aria-hidden="true"],[hidden],[inert]')) return false;
    if (el.closest('details:not([open]) > :not(summary)')) return false;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.visibility === 'collapse') return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const path = (el) => {
    const parts = [];
    for (let e = el; e && e.nodeType === 1 && parts.length < 4; e = e.parentElement) {
      let s = e.tagName.toLowerCase();
      if (e.id) { s += '#' + e.id; parts.unshift(s); break; }
      if (e.dataset && e.dataset.block) s += '[data-block="' + e.dataset.block + '"]';
      else { const c = [...e.classList].slice(0, 2).join('.'); if (c) s += '.' + c; }
      parts.unshift(s);
    }
    return parts.join(' > ');
  };
  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const rgbaOf = (css) => { cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = css; cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data; return [d[0], d[1], d[2], d[3] / 255]; };
  const alphaOf = (css) => rgbaOf(css)[3];
  const clipTo = (el, q) => {
    for (let a = el; a && a !== document.body; a = a.parentElement) {
      const cs = getComputedStyle(a);
      if (cs.overflowX === 'visible' && cs.overflowY === 'visible' && cs.clip === 'auto' && cs.clipPath === 'none') continue;
      const r = a.getBoundingClientRect();
      q = { l: Math.max(q.l, r.left + SX), t: Math.max(q.t, r.top + SY), r: Math.min(q.r, r.right + SX), b: Math.min(q.b, r.bottom + SY) };
    }
    return q;
  };
  const words = [], els = new Map(), meta = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const range = document.createRange();
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    if (!n.nodeValue.trim()) continue;
    const el = n.parentElement;
    if (!el || el.closest('svg,script,style,noscript,template,canvas,select,textarea') || !vis(el)) continue;
    const cs = getComputedStyle(el);
    // Transparent or zero-opacity text is the probe's 'invisible' check.
    let alpha = alphaOf(cs.webkitTextFillColor || cs.color);
    for (let a = el; a && a !== document.documentElement; a = a.parentElement) alpha *= Number(getComputedStyle(a).opacity);
    const clip = cs.backgroundClip === 'text' || cs.webkitBackgroundClip === 'text';
    if (alpha < 0.02 && !clip) continue;
    const re = /\\S+/g;
    for (let m = re.exec(n.nodeValue); m; m = re.exec(n.nodeValue)) {
      // Letters and digits only: an emoji or a symbol is not drawn in the text colour.
      if (!/[\\p{L}\\p{N}]/u.test(m[0])) continue;
      range.setStart(n, m.index); range.setEnd(n, m.index + m[0].length);
      for (const r of range.getClientRects()) {
        const q = clipTo(el, { l: r.left + SX, t: r.top + SY, r: r.right + SX, b: r.bottom + SY });
        if (q.r - q.l < 3 || q.b - q.t < 6) continue;
        if (!els.has(el)) {
          els.set(el, meta.length);
          const size = parseFloat(cs.fontSize), weight = Number(cs.fontWeight) || 400;
          meta.push({ where: path(el), text: el.textContent.trim().replace(/\\s+/g, ' ').slice(0, 40),
            fill: rgbaOf(cs.webkitTextFillColor || cs.color), large: size >= 24 || (size >= 18.66 && weight >= 700), clip });
          el.setAttribute('data-dm-ink', '');
          if (clip) el.setAttribute('data-dm-ink-clip', '');
        }
        words.push({ e: els.get(el), w: m[0].slice(0, 30), l: q.l, t: q.t, r: q.r, b: q.b });
      }
    }
  }
  return { words, meta, height: document.documentElement.scrollHeight, W: innerWidth, H: innerHeight };
})()`;
// Text drawn by clipping a background to it shows its background: that is
// switched to the whole box, so the word's pixels still change if it is seen.
const INK_HIDE = `(async () => {
  const s = document.createElement('style'); s.setAttribute('data-dm-ink-hide', '');
  s.textContent = ':root *,:root *::before,:root *::after{-webkit-text-fill-color:transparent!important;'
    + 'text-decoration-color:transparent!important;text-emphasis-color:transparent!important;'
    + 'text-shadow:none!important;-webkit-text-stroke-color:transparent!important;caret-color:transparent!important}'
    + ':root [data-dm-ink-clip]{-webkit-background-clip:border-box!important;background-clip:border-box!important}'
    + ':root{scroll-behavior:auto!important}';
  document.head.appendChild(s);
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  return [...document.querySelectorAll('[data-dm-ink]:not([data-dm-ink-clip])')]
    .filter((el) => !/^rgba\\(0, 0, 0, 0\\)$|^transparent$/.test(getComputedStyle(el).webkitTextFillColor))
    .map((el) => el.tagName.toLowerCase() + ' ' + getComputedStyle(el).webkitTextFillColor);
})()`;
const INK_UNHIDE = `(() => { for (const s of document.querySelectorAll('style[data-dm-ink-hide]')) s.remove();
  for (const el of document.querySelectorAll('[data-dm-ink]')) { el.removeAttribute('data-dm-ink'); el.removeAttribute('data-dm-ink-clip'); } })()`;
// A pixel counts as ink when the two captures differ by more than this (summed
// over R, G and B); a word is seen when enough of its box is ink.
const INK_DELTA = 48;
const INK_SHARE = 0.015;
// A word whose strongest pixel reaches less than this share of the luminance
// step its colour should make, and lands under its contrast bar, is faint.
// Whole-pixel stems reach 0.9 and more; a 40% white veil leaves 0.6.
const FAINT_REACH = 0.75;
const LIN_TABLE = Array.from({ length: 256 }, (_, v) => {
  v /= 255;
  return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
});
const lum = ([r, g, b]) =>
  0.2126 * LIN_TABLE[Math.round(r)] +
  0.7152 * LIN_TABLE[Math.round(g)] +
  0.0722 * LIN_TABLE[Math.round(b)];

/** Words on this page that no reader can see. Returns findings. */
async function textInk(page, stats) {
  const found = await page.evaluate(INK_FIND);
  const { words, meta, W, H } = found;
  if (!words.length) return [];
  const scratch = await page.context().newPage();
  const seen = new Uint8Array(words.length);
  const scored = new Uint8Array(words.length);
  // text-faint: the best each word measured, over every capture it is whole in.
  const reach = new Float64Array(words.length).fill(-1);
  const drawnAt = new Float64Array(words.length).fill(-1);
  // At the device's own pixel ratio: a glyph's stem is then whole pixels, so
  // its strongest pixel shows the colour it is really drawn in (text-faint).
  const dpr = await page.evaluate("devicePixelRatio");
  const shot = () => page.screenshot({ type: "png", animations: "disabled", caret: "hide" });
  const scrollAt = async (y) =>
    page.evaluate(
      `(async () => { scrollTo({ left: 0, top: ${y}, behavior: 'instant' }); await ${FRAME}; return scrollY; })()`,
    );
  try {
    // Overlapping viewport-high captures: a word under a sticky bar in one is
    // clear of it in the next, so only a word covered wherever it can be
    // scrolled to is reported.
    const maxY = Math.max(0, found.height - H);
    const step = Math.max(120, Math.floor(H * 0.6));
    const ys = [];
    for (let y = 0; ; y += step) {
      ys.push(Math.min(y, maxY));
      if (y >= maxY) break;
    }
    const drawn = [];
    for (const y of ys) {
      const at = await scrollAt(y);
      drawn.push({ y: at, png: await shot() });
    }
    const missed = await page.evaluate(INK_HIDE);
    if (missed.length)
      throw new Error(
        `hiding the text did NOT land on ${missed.length} element(s) of ${page.url()} (${missed.slice(0, 3).join("; ")}): every word would read as seen`,
      );
    try {
      for (const d of drawn) {
        const at = await scrollAt(d.y);
        if (Math.abs(at - d.y) > 0.5) continue;
        const inView = [];
        words.forEach((q, i) => {
          if (q.t >= d.y && q.b <= d.y + H && q.l >= 0 && q.r <= W)
            inView.push([i, q.l, q.t - d.y, q.r, q.b - d.y]);
        });
        if (!inView.length) continue;
        const hidden = await shot();
        const res = await scratch.evaluate(
          async ({ a64, b64, list, W, H, delta }) => {
            const load = async (b) => {
              const i = new Image();
              i.src = "data:image/png;base64," + b;
              await i.decode();
              return i;
            };
            const [A, B] = await Promise.all([load(a64), load(b64)]);
            const px = (img) => {
              const c = document.createElement("canvas");
              c.width = img.width;
              c.height = img.height;
              const x = c.getContext("2d", { willReadFrequently: true });
              x.drawImage(img, 0, 0);
              return x.getImageData(0, 0, img.width, img.height).data;
            };
            const a = px(A),
              b = px(B);
            const k = A.width / W;
            const LIN = Array.from({ length: 256 }, (_, v) => {
              v /= 255;
              return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
            });
            const Y = (d, j) =>
              0.2126 * LIN[d[j]] + 0.7152 * LIN[d[j + 1]] + 0.0722 * LIN[d[j + 2]];
            const out = [];
            for (const [i, l, t, r, bt] of list) {
              const x0 = Math.max(0, Math.floor(l * k)),
                x1 = Math.min(A.width, Math.ceil(r * k));
              const y0 = Math.max(0, Math.floor(t * k)),
                y1 = Math.min(A.height, Math.ceil(bt * k));
              let n = 0,
                area = 0,
                step = -1,
                la = 0,
                lb = 0,
                lo = 1,
                hi = 0;
              const hist = [new Uint32Array(256), new Uint32Array(256), new Uint32Array(256)];
              for (let y = y0; y < y1; y++)
                for (let x = x0; x < x1; x++) {
                  const j = (y * A.width + x) * 4;
                  area++;
                  const ya = Y(a, j),
                    yb = Y(b, j);
                  if (Math.abs(ya - yb) > step) {
                    step = Math.abs(ya - yb);
                    la = ya;
                    lb = yb;
                  }
                  lo = Math.min(lo, yb);
                  hi = Math.max(hi, yb);
                  hist[0][b[j]]++;
                  hist[1][b[j + 1]]++;
                  hist[2][b[j + 2]]++;
                  if (
                    Math.abs(a[j] - b[j]) +
                      Math.abs(a[j + 1] - b[j + 1]) +
                      Math.abs(a[j + 2] - b[j + 2]) >
                    delta
                  )
                    n++;
                }
              const median = (h) => {
                let c = 0;
                for (let v = 0; v < 256; v++) if ((c += h[v]) * 2 >= area) return v;
                return 255;
              };
              out.push([i, n, area, la, lb, hist.map(median), hi - lo, y1 - y0]);
            }
            return { k, kh: A.height / H, out };
          },
          {
            a64: d.png.toString("base64"),
            b64: hidden.toString("base64"),
            list: inView,
            W,
            H,
            delta: INK_DELTA,
          },
        );
        // ⛔ A capture that is not the viewport at the device's ratio puts every word
        // somewhere else.
        if (Math.abs(res.k - dpr) > 0.05 || Math.abs(res.kh - dpr) > 0.05)
          throw new Error(
            `the ink capture is ${res.k}x the viewport at dpr ${dpr}: every text-hidden reading would be misplaced`,
          );
        for (const [i, n, area, la, lb, bg, spread, tall] of res.out) {
          scored[i] = 1;
          if (n >= Math.max(3, Math.ceil(area * INK_SHARE))) seen[i] = 1;
          const m = meta[words[i].e];
          // On a flat background, in glyphs tall enough to have whole pixels: how
          // much of the step from background to text colour the strongest pixel
          // reaches. A veil, an opacity or a filter over the text lowers it.
          if (m.clip || spread > 0.2 || tall < 24) continue;
          const [fr, fg, fb, fa] = m.fill;
          const want = Math.abs(
            lum([
              fa * fr + (1 - fa) * bg[0],
              fa * fg + (1 - fa) * bg[1],
              fa * fb + (1 - fa) * bg[2],
            ]) - lum(bg),
          );
          if (want < 0.02) continue;
          reach[i] = Math.max(reach[i], Math.abs(la - lb) / want);
          drawnAt[i] = Math.max(drawnAt[i], (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05));
        }
      }
    } finally {
      await page.evaluate(INK_UNHIDE);
      await page.evaluate("scrollTo({ top: 0, behavior: 'instant' })");
    }
  } finally {
    await scratch.close();
  }
  const byEl = new Map();
  words.forEach((q, i) => {
    if (!scored[i]) {
      stats.inkUnscored++;
      return;
    }
    stats.inkWords++;
    if (seen[i]) return;
    if (!byEl.has(q.e)) byEl.set(q.e, []);
    byEl.get(q.e).push(q.w);
  });
  const faint = new Map();
  words.forEach((q, i) => {
    if (!seen[i] || reach[i] < 0) return;
    stats.faintWords++;
    const need = meta[q.e].large ? 3 : 4.5;
    if (reach[i] < FAINT_REACH && drawnAt[i] < need) {
      if (!faint.has(q.e)) faint.set(q.e, []);
      faint.get(q.e).push([q.w, drawnAt[i], reach[i]]);
    }
  });
  const faintFindings = [...faint].map(([e, ws]) => ({
    id: "text-faint",
    where: meta[e].where,
    msg: `${ws.length} word(s) of "${meta[e].text}" are drawn at about ${Math.min(...ws.map((x) => x[1])).toFixed(2)}:1 against what is behind them, under the ${meta[e].large ? 3 : 4.5}:1 they need: their strongest pixel reaches ${Math.round(Math.min(...ws.map((x) => x[2])) * 100)}% of the step their colour should make, so something over them fades them (a veil, an opacity, a filter): "${ws
      .slice(0, 5)
      .map((x) => x[0])
      .join(" ")}"`,
  }));
  return faintFindings.concat(
    [...byEl].map(([e, ws]) => ({
      id: "text-hidden",
      where: meta[e].where,
      msg: `${ws.length} word(s) of "${meta[e].text}" are never drawn where a reader can see them, wherever the page is scrolled: "${ws.slice(0, 6).join(" ")}"${ws.length > 6 ? " …" : ""} (covered by an element or a ::before/::after layer, masked, or faded out)`,
    })),
  );
}

// ─── block screenshots: the "look at it" step ───────────────────────────────
// One PNG per block, header and footer, at a phone (390px) and a laptop
// (1280px), in light and dark: detail a full-page image shrinks away.
async function blockShots(chromium, launch, urls, themes, dir) {
  mkdirSync(dir, { recursive: true });
  const browser = await chromium.launch(launch);
  let n = 0;
  try {
    for (const vpId of ["iphone", "laptop"]) {
      const v = VIEWPORTS.find((x) => x.id === vpId);
      for (const theme of themes.filter((t) => t === "light" || t === "dark")) {
        const ctx = await newStateContext(browser, v, theme);
        const page = await ctx.newPage();
        for (const url of urls) {
          await load(page, url);
          await page.evaluate(SETTLE);
          const slug = new URL(url).pathname.replace(/[^a-z0-9]+/gi, "_") || "_";
          const blocks = page.locator(
            "body > header[data-block], main > [data-block], body > footer[data-block]",
          );
          const count = await blocks.count();
          for (let i = 0; i < count; i++) {
            const id = (await blocks.nth(i).getAttribute("data-block")) || "block";
            await blocks.nth(i).screenshot({
              path: join(
                dir,
                `${slug}__${v.id}-${v.w}__${theme}__${String(i + 1).padStart(2, "0")}-${id}.png`,
              ),
              animations: "disabled",
              caret: "hide",
            });
            n++;
          }
        }
        await ctx.close();
      }
    }
  } finally {
    await browser.close();
  }
  return n;
}

// ─── print ───────────────────────────────────────────────────────────────────
// An A4 page at 96 dpi, less a browser's default margins: the width a printed
// page is laid out at. Print is measured once per page, in the print stylesheet.
const PRINT = { id: "print-a4", w: 718, h: 1000 };
const PRINT_SKIP = [
  "fold",
  "target-size",
  "images",
  "layout-shift",
  "font-failed",
  "chrome-share",
  "anchor-obscured",
  "covered",
  "focus",
];
async function printPass(browser, url) {
  const ctx = await browser.newContext({
    viewport: { width: PRINT.w, height: PRINT.h },
    deviceScaleFactor: 1,
    reducedMotion: "reduce",
  });
  try {
    const page = await ctx.newPage();
    await load(page, url);
    await page.emulateMedia({ media: "print" });
    // Paper drops backgrounds; emulation paints them. Drop them as paper does,
    // so text that relied on one is measured on white.
    await page.addStyleTag({
      content:
        ":root *,:root *::before,:root *::after{background-color:transparent!important;background-image:none!important}html{background:#fff!important}",
    });
    await page.evaluate(SETTLE);
    const { findings } = await page.evaluate(
      `${PROBE}\n;layoutProbe(${JSON.stringify({ expectedWidth: PRINT.w, skip: PRINT_SKIP })})`,
    );
    return findings;
  } finally {
    await ctx.close();
  }
}

const MAX_PHOTO_SHOTS = 12;
const FRAME = `new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)))`;

/** Score every text line over a photo on this page, at this viewport. Returns findings. */
async function photoContrast(page, v, stats) {
  const findings = [];
  const cands = await page.evaluate(PHOTO_FIND);
  if (!cands.length) return findings;
  const missed = await page.evaluate(PHOTO_HIDE);
  if (missed.length) {
    throw new Error(
      `hiding the text did NOT land on ${missed.length} element(s) of ${page.url()} (${missed.slice(0, 3).join("; ")}): the capture would score glyphs against themselves`,
    );
  }
  try {
    const pending = [...cands].sort((x, y) => x.top - y.top);
    for (let shots = 0; pending.length && shots < MAX_PHOTO_SHOTS; shots++) {
      // The first pending line a quarter of the way down: under any top chrome,
      // with the lines below it in the same shot.
      await page.evaluate(
        `(async () => { scrollTo({ top: Math.max(0, ${pending[0].top} - innerHeight / 4), behavior: 'instant' }); await ${FRAME}; })()`,
      );
      const shot = (
        await page.screenshot({ type: "png", animations: "disabled", caret: "hide" })
      ).toString("base64");
      const { geometry: g, res } = await page.evaluate(PHOTO_SAMPLE(shot, pending, v.dpr));
      // ⛔ The capture's geometry is asserted: a capture that is not the viewport at
      // the device's pixel ratio puts every sample somewhere else on the page, and
      // the readings are still plausible numbers.
      if (Math.abs(g.k - g.dpr) > 0.05 || Math.abs(g.kh - g.dpr) > 0.05) {
        throw new Error(
          `the capture is ${g.w}x${g.h} for a ${g.W}x${g.H} viewport at dpr ${g.dpr}: every photo-contrast sample would be misplaced`,
        );
      }
      const scored = res.filter((r) => r.full || r.k === pending[0].k);
      const done = new Set(scored.map((r) => r.k));
      if (!done.has(pending[0].k)) {
        stats.photoUnscored++;
        done.add(pending[0].k);
      }
      for (const r of scored) {
        const c = cands[r.k];
        const need = c.large ? 3 : 4.5;
        stats.photoTexts++;
        if (r.p5 / need < stats.minPhoto) {
          stats.minPhoto = r.p5 / need;
          stats.minPhotoAt = `"${c.text.slice(0, 24)}" ${r.p5.toFixed(2)}:1 on ${new URL(page.url()).pathname} @ ${v.id}`;
        }
        if (r.p5 < need) {
          findings.push({
            id: "photo-contrast",
            where: c.where,
            msg:
              `${Math.round(c.size * 10) / 10}px "${c.text}" measures ${r.p5.toFixed(2)}:1 against the photo behind it ` +
              `(5th-percentile pixel; median ${r.median.toFixed(2)}:1), needs ${need}:1 (SC 1.4.3)`,
          });
        }
      }
      for (let i = pending.length - 1; i >= 0; i--)
        if (done.has(pending[i].k)) pending.splice(i, 1);
    }
    stats.photoUnscored += pending.length;
  } finally {
    await page.evaluate(PHOTO_UNHIDE);
    await page.evaluate("scrollTo({ top: 0, behavior: 'instant' })");
  }
  return findings;
}

async function runMatrix({
  chromium,
  urls,
  viewports,
  themes,
  sweep,
  shots,
  launch,
  photo = true,
  ink = true,
  print = true,
  progress = false,
}) {
  const browser = await chromium.launch(launch);
  const findings = [];
  const notes = new Set();
  const photoStats = { photoTexts: 0, photoUnscored: 0, minPhoto: Infinity, minPhotoAt: "" };
  const inkStats = { inkWords: 0, inkUnscored: 0, faintWords: 0 };
  let states = 0;
  try {
    // Breakpoint edges from the first URL's own CSS.
    const probeCtx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const p0 = await probeCtx.newPage();
    await load(p0, urls[0]);
    const bp = await p0.evaluate(BREAKPOINTS);
    await probeCtx.close();
    const edgeWidths = new Set();
    for (const w of bp.media) for (const d of [-1, 0, 1]) if (w + d >= 280) edgeWidths.add(w + d);
    const edges = [...edgeWidths].map((w) => ({
      id: `edge-${w}`,
      w,
      h: 900,
      dpr: 2,
      mobile: w < 1024,
    }));
    if (bp.container.length)
      notes.add(
        `container-query thresholds in the CSS: ${bp.container.join(", ")}px of container width (covered by --sweep, not by viewport edges)`,
      );

    const navChecked = new Set();
    const shiftNotes = [];
    const rows = [
      ...viewports.map((v) => ({ ...v, themes: v.quick ? themes : ["light"] })),
      ...edges.map((v) => ({ ...v, themes: ["light"] })),
    ];
    // The header is measured on the widest row, where the fluid type is at its largest.
    const navWidth = Math.max(...rows.map((r) => r.w));
    // Progress on stderr, about ten lines a run: a full matrix takes many minutes.
    const total =
      rows.reduce((n, r) => n + r.themes.length, 0) * urls.length +
      (sweep ? (Math.floor((sweep[1] - sweep[0]) / sweep[2]) + 1) * urls.length : 0);
    const started = Date.now();
    let told = 0;
    const tell = () => {
      if (!progress || states - told < Math.max(1, Math.ceil(total / 10))) return;
      told = states;
      const s = Math.round((Date.now() - started) / 1000);
      process.stderr.write(
        `device-matrix: ${states}/${total} states, ${Math.floor(s / 60)}m${s % 60}s\n`,
      );
    };
    for (const v of rows) {
      for (const theme of v.themes) {
        const ctx = await newStateContext(browser, v, theme);
        const page = await ctx.newPage();
        const resources = watchResources(page);
        for (const url of urls) {
          resources.reset();
          await load(page, url);
          let { findings: f, stats } = await probePage(page, v.w);
          states++;
          tell();
          for (const n of stats.notMeasured || []) notes.add(n);
          if (f.some((x) => x.id === "layout-shift")) {
            const shifted = 1 + (await reloadShifts(browser, v, theme, url, SHIFT_LOADS - 1));
            if (shifted < SHIFT_LOADS) {
              f = f.filter((x) => x.id !== "layout-shift");
              shiftNotes.push(
                `${new URL(url).pathname} @ ${v.id} ${theme} (${shifted}/${SHIFT_LOADS})`,
              );
            } else {
              f = f.map((x) =>
                x.id === "layout-shift"
                  ? { ...x, msg: `${x.msg}; shifted in ${SHIFT_LOADS} of ${SHIFT_LOADS} loads` }
                  : x,
              );
            }
          }
          // Text over photos: one viewport per device class (the crop changes with
          // the aspect ratio), in every theme but forced colours. There the browser
          // paints glyphs in the forced colour whatever -webkit-text-fill-color says,
          // so the hide cannot land (its computed-style check would still pass):
          // the method does not apply, and the kit gives the copy an opaque Canvas
          // backplate instead, which --self-test checks.
          if (photo && v.quick && theme !== "forced")
            f = f.concat(await photoContrast(page, v, photoStats));
          else if (photo && v.quick && theme === "forced")
            notes.add(
              "photo-contrast: not scored in forced colours (glyphs paint in the forced colour and cannot be hidden for the capture)",
            );
          // Covered, masked and faded words: in the first theme of every row (a
          // cover is a matter of layout, which the width changes and the theme
          // does not), never in forced colours, where glyphs cannot be hidden.
          if (ink && theme === v.themes[0] && theme !== "forced")
            f = f.concat(await textInk(page, inkStats));
          f = f.concat(await detailsOpen(page, v.w));
          f = f.concat(resources.findings());
          if (v.w === navWidth && !navChecked.has(url)) {
            navChecked.add(url);
            if (print)
              for (const x of await printPass(browser, url))
                findings.push({ ...x, url, vp: `${PRINT.id} ${PRINT.w}px`, theme: "print" });
            const fit = await page.evaluate(NAV_FIT);
            if (fit) {
              const pin = Math.ceil((fit.need + 0.5) * 2) / 2;
              const said = `its brand, links and action need ${fit.need.toFixed(1)}rem on one row; the menu takes over below ${fit.at}rem; the header is at most ${fit.max.toFixed(0)}rem wide`;
              if (fit.at > fit.max && fit.need <= fit.max - 0.5)
                f.push({
                  id: "nav-hidden",
                  where: "header .site-header__bar",
                  msg: `the inline nav never shows at any width: ${said}. Set chrome.menuBelow to ${pin}`,
                });
              else if (fit.at - fit.need > 0.15 * fit.need)
                notes.add(`header: ${said}; chrome.menuBelow: ${pin} would show the links sooner`);
            }
          }
          for (const x of f) findings.push({ ...x, url, vp: `${v.id} ${v.w}×${v.h}`, theme });
          if (shots) {
            mkdirSync(shots, { recursive: true });
            const name = `${new URL(url).pathname.replace(/[^a-z0-9]+/gi, "_") || "_"}__${v.id}__${theme}.png`;
            await page.screenshot({
              path: join(shots, name),
              fullPage: true,
              animations: "disabled",
              caret: "hide",
            });
          }
        }
        await ctx.close();
      }
    }
    if (sweep) {
      const [from, to, step] = sweep;
      const ctx = await browser.newContext({
        viewport: { width: from, height: 900 },
        deviceScaleFactor: 1,
        reducedMotion: "reduce",
      });
      const page = await ctx.newPage();
      for (const url of urls) {
        await load(page, url);
        await page.evaluate(SETTLE);
        for (let w = from; w <= to; w += step) {
          await page.setViewportSize({ width: w, height: 900 });
          await page.evaluate(FRAME);
          const { findings: f } = await page.evaluate(
            `${PROBE}\n;layoutProbe(${JSON.stringify({ expectedWidth: w, skip: ["layout-shift", "font-failed", "images", "overlap", "anchor-obscured", "covered", "focus"] })})`,
          );
          states++;
          tell();
          for (const x of f) findings.push({ ...x, url, vp: `sweep ${w}px`, theme: "light" });
        }
      }
      await ctx.close();
    }
    if (shiftNotes.length)
      notes.add(
        `layout shift that did not repeat in ${SHIFT_LOADS} of ${SHIFT_LOADS} loads, on ${shiftNotes.length} page state(s): not findings (see the header). ${shiftNotes.slice(0, 3).join("; ")}${shiftNotes.length > 3 ? "; …" : ""}`,
      );
    if (inkStats.inkWords || inkStats.inkUnscored)
      notes.add(
        `text-hidden: ${inkStats.inkWords} word placement(s) checked for ink, ${inkStats.faintWords} on a flat background measured for text-faint${inkStats.inkUnscored ? `; ${inkStats.inkUnscored} not checked (wider or taller than the viewport, or off it)` : ""}`,
      );
    if (print)
      notes.add(
        `print: each page measured once in its print stylesheet at ${PRINT.w}px (A4 less margins)`,
      );
    if (photoStats.photoTexts)
      notes.add(
        `photo-contrast: ${photoStats.photoTexts} line(s) over photos scored; lowest ${photoStats.minPhotoAt} (${(photoStats.minPhoto * 100).toFixed(0)}% of its bar)${photoStats.photoUnscored ? `; ${photoStats.photoUnscored} could not be scored` : ""}`,
      );
    return { findings, notes: [...notes], states, breakpoints: bp, photo: photoStats };
  } finally {
    await browser.close();
  }
}

function report({ findings, notes, states, breakpoints }) {
  const groups = new Map();
  for (const f of findings) {
    // One group per defect: the same check on the same element, wherever it shows.
    const k = [f.id, f.url, f.where].join("|");
    if (!groups.has(k)) groups.set(k, { ...f, at: [] });
    groups.get(k).at.push(`${f.vp}${f.theme === "light" ? "" : " " + f.theme}`);
  }
  console.log(
    `device-matrix: ${states} page states; media breakpoints ${breakpoints.media.length ? `${breakpoints.media.join(", ")}px (each tested ±1px)` : "none"}`,
  );
  for (const n of notes) console.log(`  note  ${n}`);
  if (!states) {
    console.log("device-matrix: 0 page states were tested. THIS IS NOT A PASS.");
    return 2;
  }
  if (!groups.size) {
    console.log("device-matrix: OK, no findings.");
    console.log(
      "Chromium is not WebKit: finish on a real iPhone and iPad (adaptive-layout Step 7).",
    );
    return 0;
  }
  console.log(`device-matrix: ${findings.length} finding(s) in ${groups.size} group(s):`);
  for (const g of groups.values()) {
    const at =
      g.at.length > 4 ? `${g.at.slice(0, 4).join(", ")} +${g.at.length - 4} more` : g.at.join(", ");
    console.log(
      `  ✗ [${g.id}] ${new URL(g.url).pathname} ${g.where}\n      ${g.msg}\n      at ${at}`,
    );
  }
  return 1;
}

// ─── self-test ───────────────────────────────────────────────────────────────
function crc32(buf) {
  let c;
  const table = (crc32.t ||= Array.from({ length: 256 }, (_, n) => {
    c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    return c >>> 0;
  }));
  let crc = 0xffffffff;
  for (const b of buf) crc = table[(crc ^ b) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}
/** A solid-colour RGB PNG of w×h: real raster pixels for the image checks. */
function png(w, h, [r, g, b]) {
  const chunk = (type, data) => {
    const len = Buffer.alloc(4);
    len.writeUInt32BE(data.length);
    const td = Buffer.concat([Buffer.from(type), data]);
    const crc = Buffer.alloc(4);
    crc.writeUInt32BE(crc32(td));
    return Buffer.concat([len, td, crc]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0);
  ihdr.writeUInt32BE(h, 4);
  ihdr.set([8, 2, 0, 0, 0], 8);
  const row = Buffer.alloc(1 + w * 3);
  for (let x = 0; x < w; x++) row.set([r, g, b], 1 + x * 3);
  const raw = Buffer.concat(Array.from({ length: h }, () => row));
  return Buffer.concat([
    Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
    chunk("IHDR", ihdr),
    chunk("IDAT", deflateSync(raw)),
    chunk("IEND", Buffer.alloc(0)),
  ]);
}

const LONG_WORD = "Donaudampfschifffahrtsgesellschaftskapitänswitwe";
const PROSE =
  "Long-running copy that wraps across several lines, so the width of each line can be measured against a comfortable reading measure on every screen it meets.";
/** A synthetic page on the kit's three stylesheets, for planting one defect at a time. */
function page({ head = "", top = "", extra = "", cards = 5 } = {}) {
  const card = (i) =>
    `<article class="card stack"><h3>Feature ${i}</h3><p class="muted">One honest sentence about what this does for a customer.</p></article>`;
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Self-test</title><link rel="stylesheet" href="/tokens.css"><link rel="stylesheet" href="/layout.css"><link rel="stylesheet" href="/blocks.css">${head}</head><body>
${top}
<header data-block="site-header" data-tone="canvas" data-space="none" class="site-header"><div class="site-header__bar"><a class="brand" href="/">Diner</a><nav class="site-nav" aria-label="Main"><ul role="list"><li><a href="/">Home</a></li><li><a href="/menu/">Menu</a></li></ul></nav></div></header>
<main id="main">
<section data-block="hero-full" data-tone="media" data-space="l" aria-labelledby="h1">
  <div data-slot="backdrop"><picture><source media="(max-width: 30em) and (orientation: portrait)" srcset="/portrait.png" width="1200" height="1800"><img src="/landscape.png" width="2560" height="1440" alt=""></picture></div>
  <div class="on-photo stack"><h1 id="h1">Breakfast all day, since 1945</h1><p>A diner that still makes its biscuits by hand every morning.</p><div class="cluster"><a class="button" href="/menu/">See the menu</a><a class="button" data-variant="ghost" href="/visit/">Plan a visit</a></div></div>
</section>
<section data-block="features-grid" data-tone="canvas" aria-labelledby="h2a"><div><h2 id="h2a">Why people come back</h2></div><div><div class="cards">${Array.from({ length: cards }, (_, i) => card(i + 1)).join("")}</div></div></section>
<section data-block="story-split" data-tone="surface" aria-labelledby="h2b"><div class="switcher" style="--switch-at: 44rem"><div class="frame" style="--ratio: 4 / 3"><img src="/story.png" width="1200" height="900" alt="The original counter"></div><div class="prose stack"><h2 id="h2b">Same counter, same recipes</h2><p>${PROSE}</p></div></div></section>
<section data-block="contact-form" data-tone="canvas" aria-labelledby="h2c"><div><form class="stack prose" action="#main"><h2 id="h2c">Ask us anything</h2><div class="field"><label for="em">Email</label><input id="em" type="email" autocomplete="email"></div><div><button class="button" type="submit">Send</button></div></form></div></section>
<section data-block="cta-banner" data-tone="inverse" aria-labelledby="h2d"><div class="cluster"><h2 id="h2d">Hungry yet?</h2><a class="button" href="/book/">Book a table</a></div></section>
${extra}
</main>
<footer data-block="site-footer" data-tone="surface" data-space="s" class="site-footer"><div><p>© Example Diner · 411 Fairhope Ave</p></div></footer>
</body></html>`;
}

const sec = (inner, tone = "canvas") =>
  `<section data-block="m" data-tone="${tone}"><div>${inner}</div></section>`;
const MUTATIONS = [
  {
    expect: "fold",
    vp: "iphone-land",
    why: "a landing page whose h1 starts below a phone-on-its-side's first screen",
    html: { head: `<style>[data-block="hero-full"] { padding-block-start: 30rem; }</style>` },
  },
  {
    expect: "grid-span",
    vp: "laptop",
    why: "an optional middle column left empty: its gaps push the price a gap off its line",
    html: {
      extra: sec(
        `<div style="display: grid; grid-template-columns: 1fr auto auto; column-gap: 1.5rem"><span>Harbour pale ale</span><span></span><span>$7</span></div>`,
      ),
    },
  },
  {
    expect: "off-grid",
    vp: "laptop",
    why: "a list with its markers removed and the browser's 40px indent kept",
    html: {
      extra: sec(
        `<ol style="list-style: none"><li>Trivia night, Tuesday</li><li>Live music, Friday</li><li>Release party, Saturday</li></ol>`,
      ),
    },
  },
  {
    expect: "overlap",
    vp: "iphone",
    why: "a badge over the end of a card's last line, clear of its first",
    html: {
      extra: sec(
        `<article class="card stack" style="position: relative"><h3>Biscuits</h3><p>We have made biscuits by hand every morning since 1945, on the same counter, with the same recipe card. Come early on a Saturday.</p><span style="position: absolute; inset-inline-end: 1rem; inset-block-end: 1rem; padding: 0.5rem 1rem; background: var(--accent); color: var(--on-accent); font-weight: 700">New this week</span></article>`,
      ),
    },
  },
  {
    expect: "overflow",
    vp: "iphone",
    html: {
      extra: sec(
        `<div style="inline-size: 560px; block-size: 8px; background: var(--accent)"></div>`,
      ),
    },
  },
  {
    expect: "zoom-out",
    vp: "iphone",
    html: { head: `<style>body { min-inline-size: 600px; }</style>` },
  },
  {
    expect: "off-grid",
    vp: "laptop",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><p style="margin-inline-start: 7px">Nudged seven pixels off the content line.</p></section>`,
    },
  },
  {
    expect: "off-grid",
    vp: "laptop",
    why: "a block that is not a grid",
    html: {
      extra: `<section data-block="m" data-tone="canvas" style="display: block"><p>Not on the page grid.</p></section>`,
    },
  },
  {
    expect: "off-grid",
    vp: "laptop",
    why: "a measure-limited child placed directly on the line",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><div class="prose"><p>Prose is narrower than the content line, so it belongs INSIDE a slot.</p></div></section>`,
    },
  },
  {
    expect: "off-grid",
    vp: "laptop",
    why: "a ported wrapper that pads its text off the line",
    html: {
      extra: sec(
        `<div style="padding-inline: 15px"><p>A container class from another site.</p></div>`,
      ),
    },
  },
  {
    expect: "off-grid",
    vp: "laptop",
    why: "an embed that runs into the gutter",
    html: {
      extra: sec(
        `<div style="margin-inline-start: -48px; block-size: 40px; background: var(--rule)">Embed</div>`,
      ),
    },
  },
  {
    expect: "off-grid",
    vp: "laptop",
    why: "a photo backdrop boxed inside the content line",
    html: {
      head: `<style>@layer overrides { [data-tone="media"] > [data-slot="backdrop"] { grid-column: content !important; } }</style>`,
    },
  },
  {
    expect: "text-overflow",
    vp: "reflow-320",
    html: {
      extra: sec(`<p style="overflow-wrap: normal; hyphens: manual">${LONG_WORD}${LONG_WORD}</p>`),
    },
  },
  {
    expect: "text-overflow",
    vp: "laptop",
    why: "text spilling out of the bottom of a fixed-height card",
    html: {
      extra: sec(
        `<article class="card" style="block-size: 4rem; inline-size: 14rem"><p>${PROSE}</p></article>`,
      ),
    },
  },
  {
    expect: "text-clipped",
    vp: "iphone",
    html: {
      extra: sec(
        `<p style="inline-size: 9rem; overflow: hidden; white-space: nowrap">A caption far too long for its fixed box</p>`,
      ),
    },
  },
  {
    expect: "clipped",
    vp: "laptop",
    why: "a button wider than the card that clips it",
    html: {
      extra: sec(
        `<article class="card" style="overflow: hidden; inline-size: 12rem"><a class="button" href="/menu/" style="inline-size: 18rem">A button wider than its card</a></article>`,
      ),
    },
  },
  {
    expect: "overlap",
    vp: "laptop",
    why: "a badge painted over a heading",
    html: {
      extra: sec(
        `<div style="position: relative"><h3>A heading under a badge</h3><span style="position: absolute; inset: 0; background: var(--accent); color: var(--on-accent)">New</span></div>`,
      ),
    },
  },
  {
    expect: "heading-widow",
    vp: "laptop",
    html: {
      extra: sec(
        `<h2 style="font-family: monospace; font-size: 20px; inline-size: 11ch; text-wrap: wrap">aaaaa bbbbb c</h2>`,
      ),
    },
  },
  {
    expect: "measure",
    vp: "laptop",
    html: { extra: sec(`<p style="max-inline-size: none">${PROSE} ${PROSE}</p>`) },
  },
  {
    expect: "target-size",
    vp: "iphone",
    html: {
      extra: sec(
        `<div class="cluster" style="--cluster-gap: 2px"><button style="all: unset; inline-size: 14px; block-size: 14px; background: var(--accent)" aria-label="one"></button><button style="all: unset; inline-size: 14px; block-size: 14px; background: var(--accent)" aria-label="two"></button></div>`,
      ),
    },
  },
  {
    expect: "target-size",
    vp: "iphone",
    why: "two small targets whose 24px circles meet",
    html: {
      extra: sec(
        `<div class="cluster" style="--cluster-gap: 6px"><button style="all: unset; inline-size: 14px; block-size: 14px; background: var(--accent)" aria-label="one"></button><button style="all: unset; inline-size: 14px; block-size: 14px; background: var(--accent)" aria-label="two"></button></div>`,
      ),
    },
  },
  {
    expect: "input-zoom",
    vp: "iphone",
    html: { extra: sec(`<label>Name <input style="font-size: 14px"></label>`) },
  },
  {
    expect: "orphan-row",
    vp: "laptop",
    html: {
      extra: sec(
        `<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem"><div>1</div><div>2</div><div>3</div><div>4</div></div>`,
      ),
    },
  },
  {
    expect: "orphan-row",
    vp: "laptop",
    why: "layout.css's count-aware .cards must not be defeated by a hard-coded column count",
    html: {
      head: `<style>@layer overrides { .cards { grid-template-columns: repeat(3, minmax(0, 1fr)) !important; } .cards > * { grid-column: auto !important; } }</style>`,
    },
    cards: 4,
  },
  {
    expect: "grid-span",
    vp: "laptop",
    why: "a count-aware grid that is its own container",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><div class="cards"><article class="card">1</article><article class="card">2</article><article class="card">3</article></div></section>`,
    },
  },
  {
    expect: "nav-wrap",
    vp: "laptop",
    html: {
      extra: sec(
        `<nav class="site-nav" aria-label="Extra" style="inline-size: 12rem"><ul role="list"><li><a href="/">Breakfast</a></li><li><a href="/">Lunch</a></li><li><a href="/">Catering</a></li><li><a href="/">Gift cards</a></li></ul></nav>`,
      ),
    },
  },
  {
    expect: "image-distorted",
    vp: "laptop",
    html: {
      extra: sec(
        `<img src="/story.png" width="1200" height="900" style="inline-size: 600px; block-size: 200px" alt="Squashed">`,
      ),
    },
  },
  {
    expect: "image-ratio",
    vp: "laptop",
    why: "a photo whose file is not the shape the page declares (an EXIF turn, or a wrong size in the manifest)",
    html: {
      extra: sec(
        `<div class="frame" style="--ratio: 4 / 3"><img src="/story.png" width="900" height="1200" alt="Declared portrait, the file is landscape"></div>`,
      ),
    },
  },
  {
    expect: "image-upscaled",
    vp: "iphone",
    html: {
      extra: sec(
        `<div class="frame" style="--ratio: 1"><img src="/small.png" width="64" height="64" alt="A tiny source drawn large"></div>`,
      ),
    },
  },
  {
    expect: "image-oversized",
    vp: "laptop",
    html: {
      extra: sec(
        `<div class="frame" style="--ratio: 1; inline-size: 150px"><img src="/landscape.png" width="2560" height="1440" alt="A huge file in a thumbnail"></div>`,
      ),
    },
  },
  {
    expect: "image-gap",
    vp: "iphone",
    why: "a picture in a photo band that does not fill it",
    html: {
      head: `<style>@layer overrides { [data-tone="media"] > [data-slot="backdrop"] > picture > img { block-size: auto !important; } }</style>`,
    },
  },
  {
    expect: "image-no-size",
    vp: "laptop",
    html: { extra: sec(`<img src="/small.png" alt="No dimensions">`) },
  },
  {
    expect: "frame-ratio",
    vp: "laptop",
    why: "a photo frame stretched beside a taller column",
    html: {
      head: `<style>@layer overrides { .switcher > .frame { align-self: stretch !important; } }</style>`,
      extra: sec(
        `<div class="switcher" style="--switch-at: 44rem"><div class="frame" style="--ratio: 4 / 3"><img src="/story.png" width="1200" height="900" alt="The counter"></div><div class="prose stack" style="min-block-size: 40rem"><p>${PROSE}</p><p>${PROSE}</p><p>${PROSE}</p><p>${PROSE}</p></div></div>`,
      ),
    },
  },
  {
    expect: "image-broken",
    vp: "laptop",
    html: {
      extra: sec(
        `<div class="frame"><img src="/missing.png" width="800" height="600" alt="A photo that never arrives"></div>`,
      ),
    },
  },
  {
    expect: "img-alt",
    vp: "laptop",
    html: {
      extra: sec(`<div class="frame"><img src="/story.png" width="1200" height="900"></div>`),
    },
  },
  {
    expect: "text-contrast",
    vp: "laptop",
    html: { extra: sec(`<p style="color: #b5b5b5">Light grey on the near-white page.</p>`) },
  },
  {
    expect: "text-contrast",
    vp: "laptop",
    why: "a card on an inverse band painted white while its text stays light",
    html: {
      head: `<style>@layer overrides { [data-tone="inverse"] .card { background: #ffffff; } }</style>`,
      extra: sec(
        `<article class="card stack"><h3>On a dark band</h3><p class="muted">Muted text in a card.</p></article>`,
        "inverse",
      ),
    },
  },
  {
    expect: "focus-hidden",
    vp: "laptop",
    html: {
      extra: sec(
        `<p><a href="/menu/" style="outline: none !important">A link with no focus ring</a></p>`,
      ),
    },
  },
  {
    expect: "focus-clipped",
    vp: "laptop",
    html: {
      extra: sec(
        `<div style="overflow: hidden"><a class="button" href="/menu/">A focus ring its box cuts off</a></div>`,
      ),
    },
  },
  {
    expect: "anchor-obscured",
    vp: "laptop",
    html: {
      head: `<style>@layer overrides { .site-header { position: sticky; inset-block-start: 0; z-index: 5; background: var(--canvas); } }</style>`,
      // Room below the target, so the browser can scroll it to the top of the
      // viewport: a target near the page's end can never sit under the bar.
      extra:
        sec(`<p><a href="#target">Jump</a></p>`) +
        `<section id="target" data-block="m" data-tone="surface"><div><p>${PROSE}</p></div></section>` +
        sec(`<div style="block-size: 120vh"></div>`),
    },
  },
  {
    expect: "covered",
    vp: "laptop",
    html: {
      top: `<div style="position: fixed; inset-inline: 0; inset-block-end: 0; block-size: 6rem; background: var(--surface); z-index: 9"></div>`,
    },
  },
  {
    expect: "layout-shift",
    vp: "laptop",
    html: {
      extra: `<script>setTimeout(() => { const d = document.createElement('div'); d.style.blockSize = '300px'; document.querySelector('main').prepend(d); }, 200)</script>`,
    },
  },
  {
    expect: "font-failed",
    vp: "laptop",
    html: {
      head: `<style>@font-face { font-family: "Missing Serif"; src: url("/missing.woff2") format("woff2"); } h1 { font-family: "Missing Serif", serif; }</style>`,
    },
  },
  {
    expect: "chrome-share",
    vp: "iphone-land",
    html: {
      top: `<div style="position: fixed; inset-block-start: 0; inset-inline: 0; block-size: 45vh; background: var(--surface); z-index: 9"></div>`,
    },
  },
  {
    expect: "image-oversized",
    vp: "laptop",
    why: "a srcset whose sizes ask for the widest file when a smaller one covers the box",
    html: {
      extra: sec(
        `<div class="frame" style="--ratio: 1; inline-size: 150px"><img src="/s400.png" srcset="/s400.png 400w, /story.png 1200w, /landscape.png 2560w" sizes="100vw" width="2560" height="1440" alt="Wrong sizes"></div>`,
      ),
    },
  },
  {
    expect: "invisible",
    vp: "laptop",
    why: "a reveal-on-scroll whose script never ran (every block at opacity 0)",
    html: {
      head: `<style>main > [data-block]:not([data-block="hero-full"]) { opacity: 0; }</style>`,
    },
  },
  {
    expect: "word-broken",
    vp: "laptop",
    why: "a figure in a box too narrow for it",
    html: { extra: sec(`<p style="inline-size: 3ch; font-size: 2.5rem">$125,000</p>`) },
  },
  {
    expect: "nav-wrap",
    vp: "iphone",
    why: "a header whose nav wraps under the brand",
    html: { head: `<style>.site-header .brand { min-inline-size: 100%; }</style>` },
  },
  {
    expect: "field-contrast",
    vp: "laptop",
    why: "a field edge at 1.2:1",
    html: { head: `<style>#em { border-color: #e2e2e6; background: transparent; }</style>` },
  },
  {
    expect: "focus-contrast",
    vp: "laptop",
    why: "a focus ring at 1.1:1",
    html: { head: `<style>:root { --focus: #eeeeee; }</style>` },
  },
  {
    expect: "text-overflow",
    vp: "iphone",
    why: "an FAQ answer that overflows only when it is opened",
    details: true,
    html: {
      extra: sec(
        `<details><summary>Can I book for twelve?</summary><p style="white-space: nowrap; max-inline-size: none">${"An answer that never wraps at all. ".repeat(3)}</p></details>`,
      ),
    },
  },
];

// Shapes that LOOK like a defect and are not: each must produce none of the ids
// it names. A probe that fires on correct pages gets switched off.
const CLEAN = [
  {
    forbid: ["grid-span"],
    vp: "desktop",
    why: "an auto-fit gallery with fewer photos than columns (its empty tracks collapse with their gutters)",
    html: {
      extra: sec(
        `<div class="auto-grid" data-ragged style="--min-col: 14rem">${[1, 2, 3].map((i) => `<div class="frame"><img src="/story.png" width="1200" height="900" alt="Photo ${i}"></div>`).join("")}</div>`,
      ),
    },
  },
  {
    forbid: ["overlap"],
    vp: "iphone",
    why: "a card made one link by a stretched, empty ::after (a hit area, not paint)",
    html: {
      head: `<style>.whole { position: relative; } .whole a::after { content: ""; position: absolute; inset: 0; }</style>`,
      extra: sec(
        `<article class="card stack whole"><h3><a href="/menu/">The griddle menu</a></h3><p>Pancakes, hash browns and eggs any way, all morning and into the afternoon.</p></article>`,
      ),
    },
  },
  {
    forbid: ["image-oversized", "image-upscaled"],
    vp: "iphone",
    why: "at DPR 3 the browser takes the next candidate up (2560w for a 1062px need): the spacing, not the sizes",
    html: {
      extra: sec(
        `<div class="frame" style="--ratio: 16 / 9; inline-size: 354px"><img src="/landscape.png" srcset="/s400.png 400w, /landscape.png 2560w" sizes="354px" width="2560" height="1440" alt="Right sizes"></div>`,
      ),
    },
  },
  {
    forbid: ["overflow"],
    vp: "iphone",
    why: "a skip link parked at left: -9999px",
    html: { top: `<a href="#main" style="position: absolute; left: -9999px">Skip to content</a>` },
  },
  {
    forbid: ["image-upscaled", "image-oversized"],
    vp: "iphone",
    why: "a correct srcset at DPR 3 (the browser's 1200w pick for a 354px box)",
    html: {
      extra: sec(
        `<div class="frame" style="--ratio: 4 / 3; inline-size: 354px"><img src="/story.png" srcset="/s400.png 400w, /story.png 1200w" sizes="354px" width="1200" height="900" alt="Sharp"></div>`,
      ),
    },
  },
  {
    forbid: ["orphan-row"],
    vp: "laptop",
    why: "a two-column form whose button sits alone on the last row",
    html: {
      extra: sec(
        `<form style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem" action="#main"><div class="field"><label for="a1">One</label><input id="a1"></div><div class="field"><label for="a2">Two</label><input id="a2"></div><div class="field"><label for="a3">Three</label><input id="a3"></div><div class="field"><label for="a4">Four</label><input id="a4"></div><div><button class="button" type="submit">Send</button></div></form>`,
      ),
    },
  },
  {
    forbid: ["orphan-row"],
    vp: "ipad",
    why: "an open-ended .auto-grid marked data-ragged",
    html: {
      extra: sec(
        `<div class="auto-grid" data-ragged><div class="card">1</div><div class="card">2</div><div class="card">3</div></div>`,
      ),
    },
  },
  {
    forbid: ["grid-span", "text-overflow", "measure"],
    vp: "laptop",
    why: "cards inside half a switcher answer to the half, not the slot",
    html: {
      extra: sec(
        `<div class="switcher" style="--switch-at: 44rem"><div><div class="cards" id="half"><article class="card stack"><h3>One</h3><p class="muted">Short.</p></article><article class="card stack"><h3>Two</h3><p class="muted">Short.</p></article><article class="card stack"><h3>Three</h3><p class="muted">Short.</p></article></div></div><div><p>Beside the cards.</p></div></div>`,
      ),
    },
    assert: () =>
      document.querySelector("#half > :first-child").getBoundingClientRect().width > 400,
  },
  {
    forbid: ["focus-clipped", "focus-hidden", "image-gap"],
    vp: "laptop",
    why: "a linked photo in a frame: the link fills it and the ring is drawn on the frame",
    html: {
      extra: sec(
        `<div class="frame" style="--ratio: 4 / 3; inline-size: 20rem"><a href="/menu/"><img src="/story.png" width="1200" height="900" alt="See the menu"></a></div>`,
      ),
    },
    assert: () => {
      const a = document.querySelector('.frame > a[href="/menu/"]');
      return a.getBoundingClientRect().height >= a.parentElement.getBoundingClientRect().height - 1;
    },
  },
];

const KIT_DIR = dirname(LAYOUT_CSS);
const RENDER = join(HERE, "block_site_render.py");
const CHECK = join(HERE, "block_site_check.py");

async function selfTest(chromium, launch) {
  const dir = mkdtempSync(join(tmpdir(), "device-matrix-selftest-"));
  const src = mkdtempSync(join(tmpdir(), "device-matrix-stress-"));
  let failed = 0;
  const row = (ok, label, detail = "") => {
    if (!ok) failed++;
    console.log(`  ${ok ? "ok  " : "FAIL"} ${label}${detail ? ` — ${detail}` : ""}`);
  };
  // 1. The kit's own output: its example site and its stress fixtures, rendered
  //    by the reference renderer, are the control. Planted defects go on
  //    synthetic pages beside them.
  const py = (args) => execFileSync("python3", args, { encoding: "utf8" });
  py([
    RENDER,
    "render",
    join(KIT_DIR, "example.manifest.json"),
    "--catalog",
    join(KIT_DIR, "catalog.json"),
    "--out",
    dir,
    "--placeholders",
  ]);
  py([CHECK, "fixtures", join(KIT_DIR, "catalog.json"), "--out", join(src, "stress.json")]);
  // Into its own folder (a render into a folder another render wrote removes
  // that render's pages), then copied beside the example to share one server.
  py([
    RENDER,
    "render",
    join(src, "stress.json"),
    "--catalog",
    join(KIT_DIR, "catalog.json"),
    "--out",
    join(src, "stress-dist"),
  ]);
  cpSync(join(src, "stress-dist"), dir, { recursive: true });
  const exampleManifest = JSON.parse(readFileSync(join(KIT_DIR, "example.manifest.json"), "utf8"));
  const example = exampleManifest.pages.map((p) => p.path);
  // The example with a menu switch the header can never reach (nav-hidden must fire).
  const hidden = { ...exampleManifest, chrome: { ...exampleManifest.chrome, menuBelow: 150 } };
  writeFileSync(join(src, "nav-hidden.json"), JSON.stringify(hidden));
  py([
    RENDER,
    "render",
    join(src, "nav-hidden.json"),
    "--catalog",
    join(KIT_DIR, "catalog.json"),
    "--out",
    join(dir, "nav-hidden"),
    "--placeholders",
  ]);
  const stress = JSON.parse(readFileSync(join(src, "stress.json"), "utf8")).pages.map(
    (p) => p.path,
  );
  writeFileSync(join(dir, "landscape.png"), png(2560, 1440, [92, 70, 52]));
  writeFileSync(join(dir, "portrait.png"), png(1200, 1800, [92, 70, 52]));
  writeFileSync(join(dir, "story.png"), png(1200, 900, [140, 120, 96]));
  writeFileSync(join(dir, "s400.png"), png(400, 300, [140, 120, 96]));
  writeFileSync(join(dir, "small.png"), png(64, 64, [40, 90, 160]));
  for (const n of [1, 2, 3, 4, 5, 6])
    writeFileSync(join(dir, `cards-${n}.html`), page({ cards: n }));
  const photoCard = (i) =>
    `<article class="card stack"><div class="frame" style="--ratio: 1"><img src="/story.png" width="1200" height="900" alt="Person ${i}"></div><h3>Person ${i}</h3></article>`;
  for (const n of [1, 3])
    writeFileSync(
      join(dir, `photo-cards-${n}.html`),
      page({
        extra: sec(
          `<div class="cards" id="pc">${Array.from({ length: n }, (_, i) => photoCard(i + 1)).join("")}</div>`,
        ),
      }),
    );
  MUTATIONS.forEach((m, i) =>
    writeFileSync(join(dir, `m${i}.html`), page({ ...m.html, cards: m.cards ?? 5 })),
  );
  CLEAN.forEach((m, i) => writeFileSync(join(dir, `c${i}.html`), page(m.html)));
  writeFileSync(
    join(dir, "nocss.html"),
    page({ head: `<link rel="stylesheet" href="/missing.css">` }),
  );
  // The example built for a subpath, into its own folder, as a site under /shop/ is.
  writeFileSync(join(src, "shop.json"), JSON.stringify({ ...exampleManifest, basePath: "/shop/" }));
  py([
    RENDER,
    "render",
    join(src, "shop.json"),
    "--catalog",
    join(KIT_DIR, "catalog.json"),
    "--out",
    join(dir, "shop"),
    "--placeholders",
  ]);
  // Words no reader can see: a decorative layer, a badge and a mask over the copy.
  const INK_CASES = [
    {
      why: "a ::after layer drawn over the copy",
      html: {
        head: `<style>.veiled { position: relative; } .veiled::after { content: ""; position: absolute; inset: 0; background: var(--surface); }</style>`,
        extra: sec(
          `<div class="card veiled"><p>Copy a decorative layer covers at every width</p></div>`,
        ),
      },
    },
    {
      why: "a badge over the last line of a card",
      html: {
        extra: sec(
          `<div class="card stack" style="position: relative"><h3>Weekend brunch</h3><p>Served from nine until two on Saturdays and Sundays, with the full griddle menu and the last line under a badge</p><span aria-hidden="true" style="position: absolute; inset-inline: 0; inset-block-end: 0; block-size: 3.2em; background: var(--accent)"></span></div>`,
        ),
      },
    },
    {
      why: "a white veil at 85% over a card's copy (it reads at about 1.4:1)",
      expect: "text-faint",
      html: {
        head: `<style>.veiled { position: relative; } .veiled::after { content: ""; position: absolute; inset: 0; background: rgb(255 255 255 / 0.85); pointer-events: none; }</style>`,
        extra: sec(
          `<div class="card veiled stack"><h3>Weekend brunch</h3><p>Served from nine until two on Saturdays and Sundays.</p></div>`,
        ),
      },
    },
    {
      why: "a mask that fades the second paragraph out",
      html: {
        extra: sec(
          `<div class="prose stack" style="-webkit-mask-image: linear-gradient(black 0 40%, transparent 40%); mask-image: linear-gradient(black 0 40%, transparent 40%)"><p>${PROSE}</p><p>The second paragraph, which the mask fades to nothing.</p></div>`,
        ),
      },
    },
  ];
  INK_CASES.forEach((m, i) => writeFileSync(join(dir, `ink${i}.html`), page(m.html)));
  // Look-alikes: all seen, so none may be reported.
  writeFileSync(
    join(dir, "ink-ok.html"),
    page({
      head: `<style>.site-header { position: sticky; inset-block-start: 0; z-index: 5; background: var(--canvas); }</style>`,
      top: `<a class="skip-link button" href="#main">Skip to content</a>`,
      extra: sec(
        `<div class="stack"><h2 style="background: linear-gradient(90deg, #7c2d12, #1e3a8a); -webkit-background-clip: text; background-clip: text; color: transparent">A heading drawn in its gradient</h2>` +
          `<p>Cheers 🍺🍻 from the taproom</p><p><span class="visually-hidden">Read only by a screen reader</span>Seen by everyone</p>` +
          `<div class="card" style="position: relative"><p>Under a light veil that still shows the words</p><span aria-hidden="true" style="position: absolute; inset: 0; background: rgb(255 255 255 / 0.1)"></span></div>` +
          `<p>${PROSE} ${PROSE} ${PROSE}</p></div>`,
      ),
    }),
  );
  writeFileSync(
    join(dir, "res.html"),
    page({ head: `<style>.card { background-image: url(/missing-texture.png); }</style>` }),
  );
  writeFileSync(
    join(dir, "print-wide.html"),
    page({ head: `<style>@media print { .card { inline-size: 900px; } }</style>` }),
  );
  cpSync(join(dir, "shop"), join(dir, "shop-rooturl"), { recursive: true });
  mkdirSync(join(dir, "shop-rooturl", "img"), { recursive: true });
  writeFileSync(join(dir, "shop-rooturl", "img", "texture.png"), png(64, 64, [240, 236, 228]));
  writeFileSync(
    join(dir, "shop-rooturl", "blocks.css"),
    readFileSync(join(dir, "shop-rooturl", "blocks.css"), "utf8") +
      "\n.site-footer { background-image: url(/img/texture.png); }\n",
  );
  writeFileSync(
    join(dir, "gradient.html"),
    page({
      extra: sec(
        `<div class="card" style="background: linear-gradient(#26262c, #34343c)"><p>Dark ink on a dark gradient</p></div>`,
      ),
    }),
  );
  writeFileSync(
    join(dir, "graze.html"),
    page({
      extra:
        `<section data-block="m" data-tone="media" aria-label="Band"><div data-slot="backdrop"><img src="/story.png" width="1200" height="900" alt=""></div><div class="on-photo"><p>Copy on the photo band</p></div></section>` +
        `<section data-block="m" data-tone="canvas" style="padding-block-start: 0"><div><h2 style="margin-block-start: -4px; line-height: 1.6">Flat heading below the band</h2></div></section>`,
    }),
  );
  const { server, origin } = await serve(dir);
  try {
    const quick = VIEWPORTS.filter((v) => v.quick);
    const control = await runMatrix({
      chromium,
      launch,
      urls: example.map((p) => origin + p),
      viewports: quick,
      themes: Object.keys(THEMES),
      sweep: [320, 1600, 40],
    });
    const show = (fs) =>
      fs
        .slice(0, 3)
        .map((f) => `[${f.id}] ${new URL(f.url).pathname} ${f.where} ${f.msg} @ ${f.vp} ${f.theme}`)
        .join(" | ");
    row(
      control.findings.length === 0,
      `control: the kit's example site (${example.length} pages) clean at ${quick.length} viewports × ${Object.keys(THEMES).length} themes + a 320–1600px sweep (${control.states} states)`,
      show(control.findings),
    );
    row(
      control.photo.photoTexts > 0,
      `photo-contrast scored the example's hero copy (${control.photo.photoTexts} lines; lowest ${control.photo.minPhotoAt})`,
    );
    const stressRun = await runMatrix({
      chromium,
      launch,
      urls: stress.map((p) => origin + p),
      viewports: quick,
      themes: ["light"],
      sweep: null,
    });
    row(
      stressRun.findings.length === 0,
      `control: every catalog block at its min, max, longest word and RTL (${stress.length} stress pages) clean at ${quick.length} viewports, photo copy scored on a white photo (${stressRun.states} states)`,
      show(stressRun.findings),
    );
    const hiddenRun = await runMatrix({
      chromium,
      launch,
      urls: [`${origin}/nav-hidden/`],
      viewports: quick.filter((v) => v.w >= 1280),
      themes: ["light"],
      sweep: null,
      photo: false,
    });
    row(
      hiddenRun.findings.some((f) => f.id === "nav-hidden"),
      "must fail: nav-hidden (a menu switch wider than the header can ever be)",
      hiddenRun.findings.map((f) => f.id).join(", ") || "nothing",
    );
    // The count-aware .cards grid, measured: row pattern per item count at a
    // phone, a tablet (two-column range) and a laptop (six-track range).
    const WANT = {
      "reflow-320": {
        1: "1",
        2: "1+1",
        3: "1+1+1",
        4: "1+1+1+1",
        5: "1+1+1+1+1",
        6: "1+1+1+1+1+1",
      },
      ipad: { 1: "1", 2: "2", 3: "2+1", 4: "2+2", 5: "2+2+1", 6: "2+2+2" },
      laptop: { 1: "1", 2: "2", 3: "3", 4: "2+2", 5: "3+2", 6: "3+3" },
    };
    const browser = await chromium.launch(launch);
    try {
      for (const [vpId, byCount] of Object.entries(WANT)) {
        const v = VIEWPORTS.find((x) => x.id === vpId);
        const ctx = await browser.newContext({
          viewport: { width: v.w, height: v.h },
          deviceScaleFactor: v.dpr,
          isMobile: v.mobile,
        });
        const pg = await ctx.newPage();
        for (const [n, want] of Object.entries(byCount)) {
          await load(pg, `${origin}/cards-${n}.html`);
          const got = await pg.evaluate(() => {
            const rows = new Map();
            for (const k of document.querySelector(".cards").children) {
              const t = Math.round(k.getBoundingClientRect().top);
              rows.set(t, (rows.get(t) || 0) + 1);
            }
            return [...rows.entries()]
              .sort((a, b) => a[0] - b[0])
              .map(([, c]) => c)
              .join("+");
          });
          row(
            got === want,
            `count-aware .cards: ${n} item(s) @ ${vpId} lay out ${want}`,
            got === want ? "" : `got ${got}`,
          );
        }
        await ctx.close();
      }
      // Photo cards never stretch: an odd last one keeps a column's width, centred,
      // and a lone one is a centred third on the six-track grid.
      for (const [vpId, n, want] of [
        ["ipad", 3, "equal widths, the last centred"],
        ["laptop", 1, "a centred third"],
      ]) {
        const v = VIEWPORTS.find((x) => x.id === vpId);
        const ctx = await browser.newContext({
          viewport: { width: v.w, height: v.h },
          deviceScaleFactor: v.dpr,
        });
        const pg = await ctx.newPage();
        await load(pg, `${origin}/photo-cards-${n}.html`);
        const m = await pg.evaluate(() => {
          const g = document.querySelector("#pc").getBoundingClientRect();
          const k = [...document.querySelectorAll("#pc > *")].map((e) => e.getBoundingClientRect());
          const last = k[k.length - 1];
          return {
            widths: k.map((r) => Math.round(r.width)),
            centred: Math.abs(last.left + last.width / 2 - (g.left + g.width / 2)) < 2,
            share: last.width / g.width,
          };
        });
        const ok =
          n === 3
            ? Math.abs(m.widths[2] - m.widths[0]) <= 1 && m.centred
            : m.centred && m.share > 0.3 && m.share < 0.36;
        row(ok, `photo cards: ${n} @ ${vpId} lay out as ${want}`, JSON.stringify(m));
        await ctx.close();
      }
      // Themes the tokens promise: "more contrast" must change the dark theme too.
      for (const [theme, same] of [
        ["dark", false],
        ["contrast-dark", true],
        ["contrast", true],
      ]) {
        const ctx = await newStateContext(browser, quick[0], theme);
        const pg = await ctx.newPage();
        await load(pg, `${origin}/`);
        await pg.evaluate(SETTLE);
        const [muted, ink] = await pg.evaluate(() => [
          getComputedStyle(document.querySelector(".card .muted")).color,
          getComputedStyle(document.querySelector(".card h3")).color,
        ]);
        row(
          (muted === ink) === same,
          `${theme}: muted text ${same ? "takes the full ink colour" : "stays muted"} (${muted} vs ${ink})`,
        );
        await ctx.close();
      }
      row(
        control.breakpoints.container.length > 0,
        "breakpoint reader finds the container-query thresholds in layout.css",
        control.breakpoints.container.join(","),
      );
      {
        const ctx = await newStateContext(browser, quick[1], "forced");
        const pg = await ctx.newPage();
        await load(pg, `${origin}/`);
        const [plate, canvas] = await pg.evaluate(() => {
          const probe = document.createElement("div");
          probe.style.background = "Canvas";
          document.body.append(probe);
          const c = getComputedStyle(probe).backgroundColor;
          probe.remove();
          return [
            getComputedStyle(document.querySelector(".on-photo"), "::before").backgroundColor,
            c,
          ];
        });
        row(
          plate === canvas && !/rgba/.test(plate),
          `forced colours: the hero copy sits on an opaque Canvas backplate (${plate})`,
        );
        await ctx.close();
      }

      // 2. Each planted defect is reported, and each look-alike is not.
      const at = async (vpId, url) => {
        const v = VIEWPORTS.find((x) => x.id === vpId);
        const ctx = await newStateContext(browser, v, "light");
        const pg = await ctx.newPage();
        await load(pg, url);
        return { v, ctx, pg };
      };
      for (const [i, m] of MUTATIONS.entries()) {
        const { v, ctx, pg } = await at(m.vp, `${origin}/m${i}.html`);
        let { findings } = await probePage(pg, v.w);
        let hit = findings.some((f) => f.id === m.expect);
        // A defect inside a closed <details> must be invisible to the plain pass
        // and reported by the pass that opens it.
        if (m.details) {
          const opened = await detailsOpen(pg, v.w);
          hit = !hit && opened.some((f) => f.id === m.expect);
          findings = findings.concat(opened);
        }
        if (hit && m.expect === "layout-shift")
          hit =
            (await reloadShifts(browser, v, "light", `${origin}/m${i}.html`, SHIFT_LOADS - 1)) ===
            SHIFT_LOADS - 1;
        row(
          hit,
          `must fail: ${m.expect}${m.why ? ` (${m.why})` : ""} @ ${v.id}`,
          hit ? "" : `got ${findings.map((f) => f.id).join(", ") || "nothing"}`,
        );
        await ctx.close();
      }
      for (const [i, m] of CLEAN.entries()) {
        const { v, ctx, pg } = await at(m.vp, `${origin}/c${i}.html`);
        const { findings } = await probePage(pg, v.w);
        const bad = findings.filter((f) => m.forbid.includes(f.id));
        const held = m.assert ? await pg.evaluate(m.assert) : true;
        row(
          !bad.length && held,
          `must pass: ${m.why} @ ${v.id}`,
          bad.length
            ? bad.map((f) => `[${f.id}] ${f.msg}`).join(" | ")
            : held
              ? ""
              : "its layout assertion failed",
        );
        await ctx.close();
      }
      // text-hidden: each cover, layer and mask is found; the look-alikes are not.
      for (const [i, m] of INK_CASES.entries()) {
        for (const vp of ["iphone", "laptop"]) {
          const { ctx, pg } = await at(vp, `${origin}/ink${i}.html`);
          const st = { inkWords: 0, inkUnscored: 0, faintWords: 0 };
          const f = await textInk(pg, st);
          row(
            f.some((x) => x.id === (m.expect || "text-hidden")),
            `must fail: ${m.expect || "text-hidden"} (${m.why}) @ ${vp}`,
            `${st.inkWords} words checked; got ${f.map((x) => x.msg).join(" | ") || "nothing"}`,
          );
          await ctx.close();
        }
      }
      for (const vp of ["reflow-320", "iphone", "laptop"]) {
        const { ctx, pg } = await at(vp, `${origin}/ink-ok.html`);
        const st = { inkWords: 0, inkUnscored: 0, faintWords: 0 };
        const f = await textInk(pg, st);
        row(
          !f.length && st.inkWords > 50,
          `must pass: text-hidden and text-faint look-alikes (a sticky header, a skip link, a gradient-clipped heading, emoji, a visually-hidden span, a 10% veil, small muted text) @ ${vp}`,
          f.map((x) => `${x.where}: ${x.msg}`).join(" | ") || `only ${st.inkWords} words checked`,
        );
        await ctx.close();
      }
      // photo-contrast: on the stress hero (copy over a near-white photo), both the
      // factory's mutation and a scrim too thin to hold must be reported.
      for (const [why, css] of [
        [
          "every text colour white at 15% opacity",
          `:root *, :root *::before { color: rgb(255 255 255 / 0.15) !important; }`,
        ],
        [
          "a scrim too thin over a white photo",
          `:root { --scrim-weak: 25% !important; --scrim-strong: 35% !important; }`,
        ],
      ]) {
        const { v, ctx, pg } = await at("iphone", `${origin}/stress/hero-full/max/`);
        await pg.addStyleTag({ content: css });
        const st = { photoTexts: 0, photoUnscored: 0, minPhoto: Infinity, minPhotoAt: "" };
        const f = await photoContrast(pg, v, st);
        row(
          f.some((x) => x.id === "photo-contrast"),
          `must fail: photo-contrast (${why}) @ ${v.id}`,
          `${st.photoTexts} lines scored, lowest ${st.minPhotoAt}`,
        );
        await ctx.close();
      }
      {
        // Text over a CSS gradient has no one colour behind it: it is scored on
        // pixels, like a photo.
        const { v, ctx, pg } = await at("laptop", `${origin}/gradient.html`);
        const st = { photoTexts: 0, photoUnscored: 0, minPhoto: Infinity, minPhotoAt: "" };
        const f = await photoContrast(pg, v, st);
        row(
          f.some((x) => x.id === "photo-contrast" && /Dark ink/.test(x.msg)),
          `must fail: photo-contrast (dark ink on a dark CSS gradient) @ ${v.id}`,
          f.map((x) => x.msg).join(" | ") || `${st.photoTexts} lines scored`,
        );
        await ctx.close();
      }
      {
        // Print: buttons print as a black outline (paper drops the fill), and a
        // photo band loses its screen-height minimum.
        const { ctx, pg } = await at("laptop", `${origin}/`);
        await pg.emulateMedia({ media: "print" });
        await pg.evaluate(SETTLE); // the colour change is a (0.01ms) transition too
        const [btn, minH] = await pg.evaluate(() => [
          getComputedStyle(document.querySelector("main .button:not([data-variant])")).color,
          getComputedStyle(document.querySelector('[data-tone="media"]')).minBlockSize,
        ]);
        row(
          btn === "rgb(0, 0, 0)" && (minH === "auto" || minH === "0px"),
          `print: a button prints black (${btn}) and a photo band has no minimum height (${minH})`,
        );
        await ctx.close();
      }
      {
        // A theme set on the page sets the native controls' scheme too.
        const { ctx, pg } = await at("laptop", `${origin}/`);
        const schemes = await pg.evaluate(() => {
          const out = [];
          for (const t of ["dark", "light"]) {
            document.documentElement.dataset.theme = t;
            out.push(getComputedStyle(document.documentElement).colorScheme);
          }
          return out;
        });
        row(
          schemes[0] === "dark" && schemes[1] === "light",
          `color-scheme follows [data-theme] (${schemes.join(", ")})`,
        );
        await ctx.close();
      }
      {
        // A heading on the flat page whose line box grazes the photo band above
        // it by a few px: its glyphs sit on the flat colour, so it is not scored
        // as photo copy (only the part of a line over the photo counts, and only
        // when that part is a third of the line or more).
        const { v, ctx, pg } = await at("laptop", `${origin}/graze.html`);
        const st = { photoTexts: 0, photoUnscored: 0, minPhoto: Infinity, minPhotoAt: "" };
        const f = await photoContrast(pg, v, st);
        const bad = f.filter((x) => /Flat heading/.test(x.msg + x.where));
        row(
          !bad.length && st.photoTexts > 0,
          `must pass: a flat heading whose line box grazes a photo band is not photo copy @ ${v.id}`,
          bad.map((x) => x.msg).join(" | ") || (st.photoTexts ? "" : "nothing was scored"),
        );
        await ctx.close();
      }
    } finally {
      await browser.close();
    }
    // 3. The harness itself never passes a run that tested nothing.
    row(
      (await main(["--url", `${origin}/`, "--pages", "/no-such-page/"])) === 2,
      "harness: a --pages path that answers 404 stops the run (exit 2), with --url too",
    );
    row(
      (await main(["--dir", dir, "--themes", "drak"])) === 2,
      "harness: an unknown theme is refused (exit 2), not silently dropped",
    );
    row(
      (await main(["--dir", dir, "--sweep", "1600:320:8"])) === 2,
      "harness: a sweep that runs backwards (no states) is refused (exit 2)",
    );
    row(
      (await main(["--dir", dir, "--pages", "/nocss.html", "--themes", "light", "--no-photo"])) ===
        2,
      "harness: a page whose stylesheet did not load stops the run (exit 2): its layout is not the site's",
    );
    row(
      (await main([
        "--dir",
        join(dir, "shop"),
        "--manifest",
        join(src, "shop.json"),
        "--themes",
        "light",
        "--no-photo",
      ])) === 0,
      "harness: a site built for a basePath (/shop/) is served and tested there from --dir, and is clean",
    );
    row(
      (await main([
        "--dir",
        join(dir, "shop-rooturl"),
        "--manifest",
        join(src, "shop.json"),
        "--pages",
        "/shop/",
        "--themes",
        "light",
        "--no-photo",
        "--no-ink",
        "--no-print",
      ])) === 1,
      "must fail: a basePath site whose CSS asks for a root URL (/img/…, a 404 on its host) is resource-failed, though the file is in --dir",
    );
    {
      const run = await runMatrix({
        chromium,
        launch,
        urls: [`${origin}/res.html`],
        viewports: quick.filter((v) => v.id === "laptop"),
        themes: ["light"],
        sweep: null,
        photo: false,
        ink: false,
        print: false,
      });
      row(
        run.findings.some((f) => f.id === "resource-failed"),
        "must fail: resource-failed (a background image the CSS asks for answers 404)",
        run.findings.map((f) => f.id).join(", ") || "nothing",
      );
    }
    {
      const pb = await chromium.launch(launch);
      let wide;
      try {
        wide = await printPass(pb, `${origin}/print-wide.html`);
      } finally {
        await pb.close();
      }
      row(
        wide.some((f) => f.id === "overflow"),
        "must fail: overflow in print (a print rule that makes a card wider than the page)",
        wide.map((f) => f.id).join(", ") || "nothing",
      );
    }
  } finally {
    server.close();
    rmSync(dir, { recursive: true, force: true });
    rmSync(src, { recursive: true, force: true });
  }
  console.log(`device-matrix --self-test: ${failed ? `FAILED (${failed} row(s))` : "OK"}`);
  return failed ? 1 : 0;
}

// ─── cli ─────────────────────────────────────────────────────────────────────
async function main(argv) {
  const args = { urls: [], pages: null, manifests: [], themes: Object.keys(THEMES) };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const next = () => argv[++i];
    if (a === "--self-test") args.selfTest = true;
    else if (a === "--dir") args.dir = next();
    else if (a === "--url") args.urls.push(next());
    else if (a === "--pages")
      args.pages = next()
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
    else if (a === "--manifest") args.manifests.push(next());
    else if (a === "--full") args.full = true;
    else if (a === "--quick") args.full = false;
    else if (a === "--sweep") args.sweep = next().split(":").map(Number);
    else if (a === "--themes")
      args.themes = next()
        .split(",")
        .map((s) => s.trim());
    else if (a === "--no-photo") args.noPhoto = true;
    else if (a === "--no-ink") args.noInk = true;
    else if (a === "--no-print") args.noPrint = true;
    else if (a === "--shots") args.shots = resolve(next());
    else if (a === "--block-shots") args.blockShots = resolve(next());
    else if (a === "--json") args.json = resolve(next());
    else if (a === "--chrome") args.chrome = next();
    else {
      console.error(`device-matrix: unknown argument ${a}`);
      return 2;
    }
  }
  const unknown = args.themes.filter((t) => !THEMES[t]);
  if (unknown.length || !args.themes.length) {
    console.error(
      `device-matrix: unknown theme(s) ${unknown.join(", ") || "(none given)"}; choose from ${Object.keys(THEMES).join(", ")}`,
    );
    return 2;
  }
  if (
    args.sweep &&
    (args.sweep.length !== 3 ||
      args.sweep.some((n) => !Number.isFinite(n) || n <= 0) ||
      args.sweep[0] > args.sweep[1])
  ) {
    console.error("device-matrix: --sweep FROM:TO:STEP with FROM <= TO, e.g. 320:1600:8");
    return 2;
  }
  const prefixes = [];
  for (const m of args.manifests) {
    if (!existsSync(m)) {
      console.error(`device-matrix: no such manifest ${m}`);
      return 2;
    }
    const doc = JSON.parse(readFileSync(m, "utf8"));
    // A site served under a subpath is tested there: its links say /clinic/….
    const prefix = doc.basePath || "/";
    if (prefix !== "/") prefixes.push(prefix);
    const fromManifest = doc.pages.map((p) => prefix + p.path.replace(/^\//, ""));
    args.pages = [...(args.pages || []), ...fromManifest];
  }
  const pages = args.pages || ["/"];
  const pw = loadPlaywright();
  if (!pw) {
    console.error(
      "device-matrix: could not load Playwright from this directory. Install it (npm i -D playwright && npx playwright install chromium). THIS IS NOT A PASS.",
    );
    return 2;
  }
  const exe = args.chrome || process.env.CHROME_BIN;
  // Real scrollbars: a desktop browser draws a classic 15px one, and with
  // scrollbar-gutter: stable a page laid out without it measures a width no
  // reader's browser has. Mobile emulation keeps overlay scrollbars, as phones do.
  const launch = {
    ignoreDefaultArgs: ["--hide-scrollbars"],
    ...(exe ? { executablePath: exe } : {}),
  };
  if (args.selfTest) return selfTest(pw.chromium, launch);
  let server;
  const urls = [];
  if (args.dir) {
    if (!existsSync(args.dir)) {
      console.error(`device-matrix: no such directory ${args.dir}`);
      return 2;
    }
    const s = await serve(args.dir, prefixes);
    server = s.server;
    urls.push(...pages.map((p) => s.origin + (p.startsWith("/") ? p : `/${p}`)));
  }
  for (const base of args.urls) {
    if (args.pages) urls.push(...pages.map((p) => new URL(p, base).href));
    else urls.push(base);
  }
  if (!urls.length) {
    console.error("device-matrix: give --dir DIST or --url URL (see the header)");
    return 2;
  }
  try {
    const result = await runMatrix({
      progress: true,
      chromium: pw.chromium,
      launch,
      urls,
      viewports: args.full ? VIEWPORTS : VIEWPORTS.filter((v) => v.quick),
      themes: args.themes,
      sweep: args.sweep,
      shots: args.shots,
      photo: !args.noPhoto,
      ink: !args.noInk,
      print: !args.noPrint,
    });
    if (args.json) writeFileSync(args.json, JSON.stringify(result, null, 2));
    if (args.blockShots) {
      const n = await blockShots(pw.chromium, launch, urls, args.themes, args.blockShots);
      console.log(`device-matrix: ${n} block screenshot(s) in ${args.blockShots}`);
    }
    return report(result);
  } catch (e) {
    console.error(`device-matrix: could not run: ${e && e.message}`);
    return 2;
  } finally {
    if (server) server.close();
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url))
  main(process.argv.slice(2)).then((code) => process.exit(code));
