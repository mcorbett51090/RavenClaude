#!/usr/bin/env node
// ci-headless-smoke.js — shared Tier-3 headless smoke check for both app starters
// (validate-data-platform-starters.yml, added FORGE dashboard-top1pct P0-4).
//
// Boots against an already-running server (the caller starts it and passes the URL
// via SMOKE_URL), loads the page, and asserts zero JS console errors and no 5xx
// response. Requires no live Cube instance — synthetic env vars are enough for the
// page to render (the seams throw only when actually queried, not on page load,
// per both starters' documented "not yet run against a live Cube instance" scope).
//
// ⛔ Honest limit: Chromium surfaces a blocked-by-CSP resource as a console "error"
// entry, so this DOES catch a CSP violation in practice — but that has not been
// independently confirmed here against a deliberately-broken CSP fixture. Treat the
// CSP-specific half of "this proves the CSP is correct" as unverified until a
// dedicated negative-control run exists.

const { chromium } = require("playwright");

async function main() {
  const url = process.env.SMOKE_URL;
  if (!url) {
    console.error("SMOKE_URL env var is required");
    process.exit(2);
  }

  const errors = [];
  const browser = await chromium.launch();
  const page = await browser.newPage();
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
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
  await browser.close();

  const status = response ? response.status() : 0;
  console.log("HTTP status:", status);
  console.log("Console errors:", JSON.stringify(errors, null, 2));

  if (errors.length > 0) {
    console.error("Headless smoke FAILED: console errors present");
    process.exit(1);
  }
  if (status >= 500) {
    console.error("Headless smoke FAILED: server error status", status);
    process.exit(1);
  }
  console.log("Headless smoke OK: zero console errors, status", status);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
