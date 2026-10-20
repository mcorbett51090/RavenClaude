#!/usr/bin/env node
// Smoke test for the record.js bridge's network surface (repo-review
// 2026-10-19, domainplugins-4). Starts `node record.js serve` in a temp dir and
// checks that the API refuses browser (Origin) and DNS-rebinding (Host)
// requests, that only a chrome-extension:// origin can connect as the
// extension, that the server listens on loopback only, and that outputFile is
// confined to .mp4/.webm under the bridge's cwd.
//
// Run after `bash setup.sh` (it needs the `ws` dependency):
//   node test-bridge-security.js
// It binds port 9234, so stop any running bridge first. The Chrome extension
// itself cannot run here; check a real recording by hand after changing it.

const { test, before, after } = require("node:test");
const assert = require("node:assert/strict");
const { spawn } = require("node:child_process");
const fs = require("node:fs");
const http = require("node:http");
const net = require("node:net");
const os = require("node:os");
const path = require("node:path");

let WebSocket;
try {
  WebSocket = require("ws");
} catch {
  console.log("SKIP: the ws package is not installed (run setup.sh first).");
  process.exit(0);
}

const PORT = 9234;
const RECORD_JS = path.join(__dirname, "record.js");
let workDir;
let bridge;
let extension;

function request(method, urlPath, { headers = {}, body = null, host = "127.0.0.1" } = {}) {
  return new Promise((resolve, reject) => {
    const req = http.request({ host, port: PORT, path: urlPath, method, headers }, (res) => {
      let data = "";
      res.on("data", (c) => (data += c));
      res.on("end", () => resolve({ status: res.statusCode, body: data }));
    });
    req.on("error", reject);
    if (body !== null) req.write(body);
    req.end();
  });
}

function connectWs(origin) {
  return new Promise((resolve) => {
    const ws = new WebSocket(`ws://127.0.0.1:${PORT}`, { origin });
    ws.on("open", () => resolve({ ok: true, ws }));
    ws.on("unexpected-response", (_req, res) => resolve({ ok: false, status: res.statusCode }));
    ws.on("error", () => resolve({ ok: false, status: 0 }));
  });
}

async function waitForBridge() {
  for (let i = 0; i < 50; i++) {
    try {
      const r = await request("GET", "/api/status");
      if (r.status === 200) return;
    } catch {}
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Error("bridge did not start");
}

before(async () => {
  workDir = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), "rec-bridge-test-")));
  bridge = spawn(process.execPath, [RECORD_JS, "serve"], {
    cwd: workDir,
    stdio: "ignore",
    env: process.env,
  });
  await waitForBridge();
  // A stand-in for the Chrome extension: answers every request with success.
  const conn = await connectWs("chrome-extension://abcdefghijklmnop");
  assert.ok(conn.ok, "a chrome-extension:// origin must be able to connect");
  extension = conn.ws;
  extension.on("message", (raw) => {
    const msg = JSON.parse(raw.toString());
    extension.send(JSON.stringify({ id: msg.id, type: "ok", tabs: [] }));
  });
});

after(() => {
  if (extension) extension.close();
  if (bridge) bridge.kill("SIGTERM");
  fs.rmSync(workDir, { recursive: true, force: true });
});

test("a CLI-shaped request (no Origin, loopback Host) is served", async () => {
  const r = await request("GET", "/api/status");
  assert.equal(r.status, 200);
});

test("any request carrying an Origin header is refused (browser CSRF)", async () => {
  const r = await request("POST", "/api/start", {
    headers: { Origin: "https://evil.example", "Content-Type": "text/plain" },
    body: JSON.stringify({ tabId: 7, outputFile: "x.webm" }),
  });
  assert.equal(r.status, 403);
});

test("a request addressed to another Host is refused (DNS rebinding)", async () => {
  const r = await request("GET", "/api/tabs", { headers: { Host: `evil.example:${PORT}` } });
  assert.equal(r.status, 403);
});

test("a WebSocket client without a chrome-extension:// origin is rejected", async () => {
  const web = await connectWs("https://evil.example");
  assert.equal(web.ok, false);
  const none = await connectWs(undefined);
  assert.equal(none.ok, false);
});

test("the bridge listens on 127.0.0.1 only", { skip: process.platform !== "linux" }, async () => {
  // 127.0.0.2 is loopback on Linux: a wildcard bind accepts it, a 127.0.0.1
  // bind refuses it.
  const reached = await new Promise((resolve) => {
    const s = net.connect({ host: "127.0.0.2", port: PORT });
    s.on("connect", () => {
      s.destroy();
      resolve(true);
    });
    s.on("error", () => resolve(false));
  });
  assert.equal(reached, false);
});

test("outputFile must be .mp4/.webm under the bridge's cwd", async () => {
  const start = (outputFile) =>
    request("POST", "/api/start", {
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tabId: 1, outputFile }),
    });
  assert.equal((await start(path.join(os.tmpdir(), "elsewhere.webm"))).status, 400);
  assert.equal((await start(path.join(workDir, "..", "escape.mp4"))).status, 400);
  assert.equal((await start(path.join(workDir, "notes.txt"))).status, 400);
  const ok = await start(path.join(workDir, "demo.webm"));
  assert.equal(ok.status, 200, ok.body);
  const stop = await request("POST", "/api/stop", {
    headers: { "Content-Type": "application/json" },
  });
  assert.equal(stop.status, 200, stop.body);
});
