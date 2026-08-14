#!/usr/bin/env node
// Sibling of load-substrate-tier-map.py. Workflow scripts cannot require()
// this file — they inline resolveTier + the map. Keep values lockstep with
// knowledge/substrate-tier-map.json.

const fs = require("fs");
const path = require("path");

const MAP_PATH = path.join(__dirname, "..", "knowledge", "substrate-tier-map.json");
const DEFAULT_HOST = "claude";

function loadMap() {
  return JSON.parse(fs.readFileSync(MAP_PATH, "utf8"));
}

function normalizeRow(row) {
  if (typeof row === "string") return { model: row };
  if (row && row.model) {
    const out = { model: row.model };
    if (row.effort) out.effort = row.effort;
    if (row.perspective) out.perspective = row.perspective;
    return out;
  }
  throw new Error("tier row must be a SKU string or {model}");
}

function resolveTier(host, tier, data) {
  const blob = data || loadMap();
  const hosts = blob.hosts || {};
  let h = host && String(host).trim() ? String(host).trim() : DEFAULT_HOST;
  if (!hosts[h]) h = DEFAULT_HOST;
  const table = hosts[h];
  let t = tier && String(tier).trim() ? String(tier).trim() : "balanced";
  if (!table[t]) t = "balanced";
  return normalizeRow(table[t]);
}

function selfTest() {
  const data = loadMap();
  const errors = [];
  const HOSTS = ["claude", "grok", "codex", "copilot"];
  const TIERS = ["fast", "balanced", "top"];
  for (const h of HOSTS) {
    if (!data.hosts[h]) {
      errors.push("missing host " + h);
      continue;
    }
    for (const t of TIERS) {
      if (!data.hosts[h][t]) errors.push("missing " + h + "." + t);
      else {
        const row = resolveTier(h, t, data);
        if (!row.model) errors.push(h + "." + t + " has no model");
        if (/pro$/i.test(row.model) && row.model.toLowerCase().endsWith("-pro")) {
          errors.push(h + "." + t + " is a *-pro slug: " + row.model);
        }
      }
    }
  }
  const gf = resolveTier("grok", "fast", data);
  const gb = resolveTier("grok", "balanced", data);
  const gt = resolveTier("grok", "top", data);
  if (gf.model !== "grok-4.5" || gb.model !== "grok-4.5")
    errors.push("grok fast/balanced must be grok-4.5");
  if (gt.model !== "grok-4.6") errors.push("grok top must be grok-4.6");
  if (gf.effort === gb.effort) errors.push("grok fast vs balanced must differ on effort");
  if (gf.perspective === gb.perspective)
    errors.push("grok fast vs balanced must differ on perspective");
  if (gt.model.startsWith("claude-")) errors.push("grok top must not be claude-*");
  const missing = resolveTier(undefined, "top", data);
  if (missing.model !== "claude-opus-4-8")
    errors.push("default host top should be claude-opus-4-8");
  if (errors.length) {
    console.log("substrate-tier-map.js self-test FAIL:");
    for (const e of errors) console.log("  -", e);
    process.exit(1);
  }
  console.log("substrate-tier-map.js self-test PASS");
}

if (require.main === module) {
  if (process.argv.includes("--self-test")) selfTest();
  else console.log(JSON.stringify(resolveTier(process.argv[2], process.argv[3])));
}

module.exports = { resolveTier, loadMap };
