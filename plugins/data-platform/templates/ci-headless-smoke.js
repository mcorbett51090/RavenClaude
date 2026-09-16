#!/usr/bin/env node
// ci-headless-smoke.js — shared Tier-3 headless smoke check for both app starters
// (validate-data-platform-starters.yml, added FORGE dashboard-top1pct P0-4;
// axe-core accessibility assertion added P1-8, 2026-09-03).
//
// Boots against an already-running server (the caller starts it and passes the URL
// via SMOKE_URL), loads the page, and asserts:
//   1. zero JS console errors and no 5xx response
//   2. zero serious/critical axe-core violations (WCAG 2.2 AA floor — see
//      best-practices/dashboard-meet-the-accessibility-floor.md)
// Requires no live Cube instance — synthetic Cube/JWT env vars plus
// DATA_PLATFORM_STARTER_CI_SESSION=1 (CI smoke only) so getSession() returns a
// clearly fake stub. Without that env, both starters' getSession() seams throw
// on every `/` load by design (prod throw-loud). Do not claim "seams don't throw
// on page load" — they do unless the CI stub is set.
//
// Expected CI console noise (non-fatal, matched narrowly — do NOT blanket-ignore):
//   • net::ERR_CONNECTION_REFUSED — Chromium logs failed connects to the synthetic
//     CUBE_API_ORIGIN (localhost:4000 by default) as console "error". This smoke
//     intentionally runs with no live Cube; starters degrade without a backend.
//     Only this exact substring is filtered; CSP / pageerror / other console
//     errors still fail the job.
//
// ⛔ Honest limit: Chromium surfaces a blocked-by-CSP resource as a console "error"
// entry, so check (1) DOES catch a CSP violation in practice — but that has not
// been independently confirmed here against a deliberately-broken CSP fixture.
// Treat the CSP-specific half of "this proves the CSP is correct" as unverified
// until a dedicated negative-control run exists.

const { chromium } = require("playwright");
const { AxeBuilder } = require("@axe-core/playwright");

/** Narrow allowlist for console noise that is expected without a live Cube. */
function isExpectedCiConsoleNoise(text) {
  return text.includes("net::ERR_CONNECTION_REFUSED");
}

async function main() {
  const url = process.env.SMOKE_URL;
  if (!url) {
    console.error("SMOKE_URL env var is required");
    process.exit(2);
  }

  const errors = [];
  const ignoredNoise = [];
  const browser = await chromium.launch();
  // axe-core/playwright requires a BrowserContext (not a bare Page from
  // browser.newPage()). Create an explicit context first.
  const context = await browser.newContext();
  const page = await context.newPage();
  page.on("console", (msg) => {
    if (msg.type() !== "error") return;
    const text = msg.text();
    if (isExpectedCiConsoleNoise(text)) {
      ignoredNoise.push(text);
      return;
    }
    errors.push(text);
  });
  page.on("pageerror", (err) => errors.push(String(err)));

  let response;
  try {
    response = await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
  } catch (e) {
    console.error("Failed to load", url, e);
    await browser.close();
    process.exit(1);
  }

  const status = response ? response.status() : 0;
  console.log("HTTP status:", status);
  console.log("Console errors:", JSON.stringify(errors, null, 2));
  if (ignoredNoise.length > 0) {
    console.log(
      "Ignored expected CI console noise (no live Cube):",
      JSON.stringify(ignoredNoise, null, 2),
    );
  }

  const axeResults = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag22aa"])
    .analyze();
  const seriousOrCritical = axeResults.violations.filter(
    (v) => v.impact === "serious" || v.impact === "critical",
  );
  console.log(
    "axe-core violations (serious/critical):",
    JSON.stringify(
      seriousOrCritical.map((v) => ({
        id: v.id,
        impact: v.impact,
        nodes: v.nodes.map((n) => ({
          target: n.target,
          html: typeof n.html === "string" ? n.html.slice(0, 240) : n.html,
          failureSummary: n.failureSummary,
        })),
      })),
      null,
      2,
    ),
  );

  // RTL smoke (FORGE dashboard-top1pct P2-15, 2026-09-03) — a smoke check, NOT
  // a layout certification. This does not claim the dashboard supports RTL
  // visually (Tailwind logical-property/RTL utilities are not wired into
  // either starter); it only asserts that setting dir="rtl" doesn't itself
  // throw a NEW console error — catching the cheapest class of RTL-unaware
  // bug (a script that assumes document.dir === "ltr") without overclaiming
  // full RTL correctness. See best-practices/dashboard-render-in-the-viewer-
  // locale-and-tenant-timezone.md's "RTL is a layout concern distinct from
  // locale/timezone correctness" note for why this bar is deliberately
  // narrow rather than a false "we support RTL" claim.
  const errorsBeforeRtl = errors.length;
  await page.evaluate(() => {
    document.documentElement.setAttribute("dir", "rtl");
  });
  await page.waitForTimeout(200);
  const newErrorsFromRtl = errors.slice(errorsBeforeRtl);
  console.log(
    "New console errors after dir=rtl toggle:",
    JSON.stringify(newErrorsFromRtl, null, 2),
  );

  await browser.close();

  let failed = false;
  if (errorsBeforeRtl > 0) {
    console.error("Headless smoke FAILED: console errors present");
    failed = true;
  }
  if (status >= 500) {
    console.error("Headless smoke FAILED: server error status", status);
    failed = true;
  }
  if (seriousOrCritical.length > 0) {
    console.error(
      `Headless smoke FAILED: ${seriousOrCritical.length} serious/critical axe-core violation(s)`,
    );
    failed = true;
  }
  if (newErrorsFromRtl.length > 0) {
    console.error("Headless smoke FAILED: dir=rtl toggle introduced new console error(s)");
    failed = true;
  }
  if (failed) process.exit(1);

  console.log(
    "Headless smoke OK: zero console errors, status",
    status,
    ", zero serious/critical axe-core violations, dir=rtl toggle introduced no new errors",
  );
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
