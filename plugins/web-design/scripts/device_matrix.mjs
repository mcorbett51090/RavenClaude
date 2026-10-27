#!/usr/bin/env node
/* device_matrix.mjs: render a site at every screen it will meet and run
 * layout-probe.js on each page, so "pixel-perfect on every screen" is measured
 * rather than eyeballed at two widths.
 *
 * USAGE
 *   node device_matrix.mjs --dir dist                     a built site, served locally
 *   node device_matrix.mjs --url http://localhost:4321/   a running server (repeatable)
 *     --pages /,/menu/,/visit/   paths to test (default: / only)
 *     --quick                    one viewport per device class (default)
 *     --full                     every row of adaptive-layout's device table
 *     --sweep 320:1600:8         also every 8px from 320 to 1600 (catches the
 *                                in-between widths container queries produce)
 *     --themes light,dark,forced themes on the quick rows (default: all three)
 *     --shots DIR                full-page PNG per page × viewport × theme, for
 *                                visual-regression baselines
 *     --json FILE                write every finding as JSON
 *     --chrome PATH              a Chromium binary (else CHROME_BIN, else Playwright's)
 *   node device_matrix.mjs --self-test
 *     plants each defect the probe knows in a synthetic page built on
 *     templates/block-site/tokens.css + layout.css, requires each to be reported, and requires
 *     the clean control page to report nothing at every quick viewport in every
 *     theme. A probe that has never failed proves nothing.
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
 * reloaded twice in fresh contexts: shifting in 3 of 3 loads is a finding, and
 * fewer is printed as a note with its count, never hidden.
 *
 * Needs Playwright (`npm i -D playwright`, then `npx playwright install chromium`)
 * resolvable from the current directory. Exit: 0 clean, 1 findings, 2 could not run.
 *
 * Chromium is not WebKit: emulation sets the width, DPR, touch and the viewport
 * tag, but has no Safari toolbar, no safe areas and no dynamic viewport. A green
 * run is necessary, not sufficient. Finish on a real iPhone and iPad.
 */
import { createRequire } from "node:module";
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
function serve(root) {
  const base = resolve(root);
  const server = createServer((req, res) => {
    let p = decodeURIComponent(new URL(req.url, "http://x").pathname);
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
async function probePage(page, expectedWidth, skip = []) {
  await page.evaluate(SETTLE);
  return page.evaluate(`${PROBE}\n;layoutProbe(${JSON.stringify({ expectedWidth, skip })})`);
}

/** Reload a page that shifted in fresh contexts; count the loads that shift again. */
async function reloadShifts(browser, v, theme, url, times) {
  let n = 0;
  for (let i = 0; i < times; i++) {
    const ctx = await newStateContext(browser, v, theme);
    const page = await ctx.newPage();
    await page.goto(url, { waitUntil: "load" });
    const { findings } = await probePage(page, v.w);
    if (findings.some((x) => x.id === "layout-shift")) n++;
    await ctx.close();
  }
  return n;
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
  await ctx.route(/googletagmanager\.com|google-analytics\.com|cloudflareinsights\.com/, (r) =>
    r.abort(),
  );
  return ctx;
}

async function runMatrix({ chromium, urls, viewports, themes, sweep, shots, launch }) {
  const browser = await chromium.launch(launch);
  const findings = [];
  const notes = new Set();
  let states = 0;
  try {
    // Breakpoint edges from the first URL's own CSS.
    const probeCtx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const p0 = await probeCtx.newPage();
    await p0.goto(urls[0], { waitUntil: "load" });
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

    const rows = [
      ...viewports.map((v) => ({ ...v, themes: v.quick ? themes : ["light"] })),
      ...edges.map((v) => ({ ...v, themes: ["light"] })),
    ];
    for (const v of rows) {
      for (const theme of v.themes) {
        const ctx = await newStateContext(browser, v, theme);
        const page = await ctx.newPage();
        for (const url of urls) {
          await page.goto(url, { waitUntil: "load" });
          let { findings: f, stats } = await probePage(page, v.w);
          states++;
          for (const n of stats.notMeasured || []) notes.add(n);
          if (f.some((x) => x.id === "layout-shift")) {
            const shifted = 1 + (await reloadShifts(browser, v, theme, url, 2));
            if (shifted < 3) {
              f = f.filter((x) => x.id !== "layout-shift");
              notes.add(
                `layout shift on ${new URL(url).pathname} @ ${v.id} ${theme} in ${shifted} of 3 loads: not reproducible, so not a finding (see the header)`,
              );
            } else {
              f = f.map((x) =>
                x.id === "layout-shift" ? { ...x, msg: `${x.msg}; shifted in 3 of 3 loads` } : x,
              );
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
        await page.goto(url, { waitUntil: "load" });
        await page.evaluate(SETTLE);
        for (let w = from; w <= to; w += step) {
          await page.setViewportSize({ width: w, height: 900 });
          await page.evaluate(
            "new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)))",
          );
          const { findings: f } = await page.evaluate(
            `${PROBE}\n;layoutProbe(${JSON.stringify({ expectedWidth: w, skip: ["layout-shift", "font-failed", "images"] })})`,
          );
          states++;
          for (const x of f) findings.push({ ...x, url, vp: `sweep ${w}px`, theme: "light" });
        }
      }
      await ctx.close();
    }
    return { findings, notes: [...notes], states, breakpoints: bp };
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
function page({ head = "", top = "", extra = "", cards = 5 } = {}) {
  const card = (i) =>
    `<article class="card stack"><h3>Feature ${i}</h3><p>One honest sentence about what this does for a customer.</p></article>`;
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Self-test</title><link rel="stylesheet" href="/tokens.css"><link rel="stylesheet" href="/layout.css">
<style>@layer blocks {
  .card { padding: var(--space-m); background: var(--surface); border: 1px solid var(--rule); border-radius: var(--radius-m); }
  .site-nav a { display: inline-flex; align-items: center; min-block-size: 2.75rem; padding-inline: var(--space-2xs); color: inherit; }
  .hero { min-block-size: min(80vh, 44rem); min-block-size: min(80svh, 44rem); align-content: end; }
  .field { display: grid; gap: var(--space-3xs); }
  .field input { padding-inline: var(--space-xs); border: 1px solid var(--rule); border-radius: var(--radius-s); background: var(--surface); color: var(--ink); }
}</style>${head}</head><body>
${top}
<header data-block="site-header" data-tone="canvas" data-space="s"><nav class="site-nav cluster" aria-label="Main"><a href="/">Home</a><a href="/menu/">Menu</a><a href="/visit/">Visit</a><a class="button" href="/book/">Book a table</a></nav></header>
<main>
<section data-block="hero" data-tone="media" class="hero" aria-labelledby="h1">
  <div data-slot="backdrop"><picture><source media="(max-width: 47.99em)" srcset="/portrait.png" width="1200" height="1800"><img src="/landscape.png" width="2560" height="1440" alt="The dining room at opening time"></picture></div>
  <div class="on-photo stack"><h1 id="h1">Breakfast all day, since 1945</h1><p>A diner that still makes its biscuits by hand every morning.</p><div class="cluster"><a class="button" href="/menu/">See the menu</a><a class="button" data-variant="ghost" href="/visit/">Plan a visit</a></div></div>
</section>
<section data-block="features" data-tone="canvas" aria-labelledby="h2a"><h2 id="h2a">Why people come back</h2><div><div class="cards">${Array.from({ length: cards }, (_, i) => card(i + 1)).join("")}</div></div></section>
<section data-block="story" data-tone="surface" aria-labelledby="h2b"><div class="switcher" style="--switch-at: 44rem"><div class="frame" style="--ratio: 4 / 3"><img src="/story.png" width="1200" height="900" alt="The original counter"></div><div class="prose stack"><h2 id="h2b">Same counter, same recipes</h2><p>Long-running copy that should wrap at a comfortable measure on every screen, never stretching edge to edge on a wide monitor.</p></div></div></section>
<section data-block="contact" data-tone="canvas" aria-labelledby="h2c"><div><form class="stack prose" action="#"><h2 id="h2c">Ask us anything</h2><div class="field"><label for="em">Email</label><input id="em" type="email" autocomplete="email"></div><button class="button" type="submit">Send</button></form></div></section>
<section data-block="cta" data-tone="inverse" aria-labelledby="h2d"><div class="cluster" style="justify-content: space-between"><h2 id="h2d">Hungry yet?</h2><a class="button" href="/book/">Book a table</a></div></section>
${extra}
</main>
<footer data-block="site-footer" data-tone="surface" data-space="s"><p>© Example Diner · 411 Fairhope Ave</p></footer>
</body></html>`;
}

const MUTATIONS = [
  {
    expect: "overflow",
    vp: "iphone",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><div><div style="inline-size: 560px; block-size: 8px; background: var(--accent)"></div></div></section>`,
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
    expect: "text-overflow",
    vp: "reflow-320",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><p style="overflow-wrap: normal; hyphens: manual">${LONG_WORD}${LONG_WORD}</p></section>`,
    },
  },
  {
    expect: "text-clipped",
    vp: "iphone",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><p style="inline-size: 9rem; overflow: hidden; white-space: nowrap">A caption far too long for its fixed box</p></section>`,
    },
  },
  {
    expect: "heading-widow",
    vp: "laptop",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><h2 style="font-family: monospace; font-size: 20px; inline-size: 11ch; text-wrap: wrap">aaaaa bbbbb c</h2></section>`,
    },
  },
  {
    expect: "target-size",
    vp: "iphone",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><div class="cluster" style="--cluster-gap: 2px"><button style="all: unset; inline-size: 14px; block-size: 14px; background: var(--accent)" aria-label="one"></button><button style="all: unset; inline-size: 14px; block-size: 14px; background: var(--accent)" aria-label="two"></button></div></section>`,
    },
  },
  {
    expect: "input-zoom",
    vp: "iphone",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><label>Name <input style="font-size: 14px"></label></section>`,
    },
  },
  {
    expect: "orphan-row",
    vp: "laptop",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem"><div>1</div><div>2</div><div>3</div><div>4</div></div></section>`,
    },
  },
  {
    expect: "image-distorted",
    vp: "laptop",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><div><img src="/story.png" width="1200" height="900" style="inline-size: 600px; block-size: 200px" alt="Squashed"></div></section>`,
    },
  },
  {
    expect: "image-upscaled",
    vp: "iphone",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><div class="frame" style="--ratio: 1"><img src="/small.png" width="64" height="64" alt="A tiny source drawn large"></div></section>`,
    },
  },
  {
    expect: "image-no-size",
    vp: "laptop",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><div><img src="/small.png" alt="No dimensions"></div></section>`,
    },
  },
  {
    expect: "image-broken",
    vp: "laptop",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><div class="frame"><img src="/missing.png" width="800" height="600" alt="A photo that never arrives"></div></section>`,
    },
  },
  {
    expect: "img-alt",
    vp: "laptop",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><div class="frame"><img src="/story.png" width="1200" height="900"></div></section>`,
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
    expect: "off-grid",
    vp: "laptop",
    why: "a photo backdrop boxed inside the content line",
    html: {
      head: `<style>@layer overrides { [data-tone="media"] > [data-slot="backdrop"] { grid-column: content !important; } }</style>`,
    },
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
    expect: "chrome-share",
    vp: "iphone-land",
    html: {
      top: `<div style="position: fixed; inset-block-start: 0; inset-inline: 0; block-size: 45vh; background: var(--surface); z-index: 9"></div>`,
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
];

async function selfTest(chromium, launch) {
  const dir = mkdtempSync(join(tmpdir(), "device-matrix-selftest-"));
  const { server, origin } = await (async () => {
    copyFileSync(LAYOUT_CSS, join(dir, "layout.css"));
    copyFileSync(join(dirname(LAYOUT_CSS), "tokens.css"), join(dir, "tokens.css"));
    writeFileSync(join(dir, "landscape.png"), png(2560, 1440, [92, 70, 52]));
    writeFileSync(join(dir, "portrait.png"), png(1200, 1800, [92, 70, 52]));
    writeFileSync(join(dir, "story.png"), png(1200, 900, [140, 120, 96]));
    writeFileSync(join(dir, "small.png"), png(64, 64, [40, 90, 160]));
    writeFileSync(join(dir, "index.html"), page());
    for (const n of [1, 2, 3, 4, 5, 6])
      writeFileSync(join(dir, `cards-${n}.html`), page({ cards: n }));
    MUTATIONS.forEach((m, i) =>
      writeFileSync(join(dir, `m${i}.html`), page({ ...m.html, cards: m.cards ?? 5 })),
    );
    return serve(dir);
  })();
  let failed = 0;
  const row = (ok, label, detail = "") => {
    if (!ok) failed++;
    console.log(`  ${ok ? "ok  " : "FAIL"} ${label}${detail ? ` — ${detail}` : ""}`);
  };
  try {
    // 1. The control: every count of cards, every quick viewport, every theme, clean.
    const quick = VIEWPORTS.filter((v) => v.quick);
    const control = await runMatrix({
      chromium,
      launch,
      urls: [1, 2, 3, 4, 5, 6].map((n) => `${origin}/cards-${n}.html`),
      viewports: quick,
      themes: Object.keys(THEMES),
      sweep: [320, 1600, 40],
    });
    const cf = control.findings;
    row(
      cf.length === 0,
      `control: layout.css blocks with 1–6 cards clean at ${quick.length} viewports × 3 themes + a 320–1600px sweep (${control.states} states)`,
      cf
        .slice(0, 3)
        .map((f) => `[${f.id}] ${f.where} ${f.msg} @ ${f.vp} ${f.theme}`)
        .join(" | "),
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
    const b2 = await chromium.launch(launch);
    try {
      for (const [vpId, byCount] of Object.entries(WANT)) {
        const v = VIEWPORTS.find((x) => x.id === vpId);
        const ctx = await b2.newContext({
          viewport: { width: v.w, height: v.h },
          deviceScaleFactor: v.dpr,
          isMobile: v.mobile,
        });
        const pg = await ctx.newPage();
        for (const [n, want] of Object.entries(byCount)) {
          await pg.goto(`${origin}/cards-${n}.html`, { waitUntil: "load" });
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
    } finally {
      await b2.close();
    }
    row(
      control.breakpoints.container.length > 0,
      "breakpoint reader finds the container-query thresholds in layout.css",
      control.breakpoints.container.join(","),
    );
    // 2. Each planted defect is reported.
    const browser = await chromium.launch(launch);
    try {
      for (const [i, m] of MUTATIONS.entries()) {
        const v = VIEWPORTS.find((x) => x.id === m.vp);
        const ctx = await browser.newContext({
          viewport: { width: v.w, height: v.h },
          deviceScaleFactor: v.dpr,
          isMobile: v.mobile,
          hasTouch: v.mobile,
          reducedMotion: "reduce",
        });
        await ctx.addInitScript(CLS_OBSERVER);
        const pg = await ctx.newPage();
        await pg.goto(`${origin}/m${i}.html`, { waitUntil: "load" });
        const { findings } = await probePage(pg, v.w);
        let hit = findings.some((f) => f.id === m.expect);
        if (hit && m.expect === "layout-shift")
          hit = (await reloadShifts(browser, v, "light", `${origin}/m${i}.html`, 2)) === 2;
        row(
          hit,
          `must fail: ${m.expect}${m.why ? ` (${m.why})` : ""} @ ${v.id}`,
          hit ? "" : `got ${findings.map((f) => f.id).join(", ") || "nothing"}`,
        );
        await ctx.close();
      }
    } finally {
      await browser.close();
    }
  } finally {
    server.close();
    rmSync(dir, { recursive: true, force: true });
  }
  console.log(`device-matrix --self-test: ${failed ? `FAILED (${failed} row(s))` : "OK"}`);
  return failed ? 1 : 0;
}

// ─── cli ─────────────────────────────────────────────────────────────────────
async function main(argv) {
  const args = { urls: [], pages: ["/"], themes: Object.keys(THEMES) };
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
    else if (a === "--full") args.full = true;
    else if (a === "--quick") args.full = false;
    else if (a === "--sweep") args.sweep = next().split(":").map(Number);
    else if (a === "--themes")
      args.themes = next()
        .split(",")
        .filter((t) => THEMES[t]);
    else if (a === "--shots") args.shots = resolve(next());
    else if (a === "--json") args.json = resolve(next());
    else if (a === "--chrome") args.chrome = next();
    else {
      console.error(`device-matrix: unknown argument ${a}`);
      return 2;
    }
  }
  const pw = loadPlaywright();
  if (!pw) {
    console.error(
      "device-matrix: could not load Playwright from this directory. Install it (npm i -D playwright && npx playwright install chromium). THIS IS NOT A PASS.",
    );
    return 2;
  }
  const exe = args.chrome || process.env.CHROME_BIN;
  const launch = exe ? { executablePath: exe } : {};
  if (args.selfTest) return selfTest(pw.chromium, launch);
  if (
    args.sweep &&
    (args.sweep.length !== 3 || args.sweep.some((n) => !Number.isFinite(n) || n <= 0))
  ) {
    console.error("device-matrix: --sweep FROM:TO:STEP, e.g. 320:1600:8");
    return 2;
  }
  let server;
  if (args.dir) {
    if (!existsSync(args.dir)) {
      console.error(`device-matrix: no such directory ${args.dir}`);
      return 2;
    }
    const s = await serve(args.dir);
    server = s.server;
    args.urls.push(...args.pages.map((p) => s.origin + (p.startsWith("/") ? p : `/${p}`)));
  } else if (args.urls.length && args.pages.length > 1) {
    const base = args.urls.shift();
    args.urls.push(...args.pages.map((p) => new URL(p, base).href));
  }
  if (!args.urls.length) {
    console.error("device-matrix: give --dir DIST or --url URL (see the header)");
    return 2;
  }
  try {
    const result = await runMatrix({
      chromium: pw.chromium,
      launch,
      urls: args.urls,
      viewports: args.full ? VIEWPORTS : VIEWPORTS.filter((v) => v.quick),
      themes: args.themes,
      sweep: args.sweep,
      shots: args.shots,
    });
    if (args.json) writeFileSync(args.json, JSON.stringify(result, null, 2));
    return report(result);
  } catch (e) {
    console.error(`device-matrix: could not run: ${e && e.message}`);
    return 2;
  } finally {
    if (server) server.close();
  }
}

main(process.argv.slice(2)).then((code) => process.exit(code));
