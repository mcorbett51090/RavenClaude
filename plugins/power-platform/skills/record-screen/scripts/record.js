#!/usr/bin/env node

const CLI_TIMESTAMP = Date.now();

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const http = require('http');
const WebSocket = require('ws');

const PORT = 9234;
const STATE_FILE = path.join(os.tmpdir(), 'record-screen-server.json');
const FPS = 5;

// ============================================================
// Arg parsing
// ============================================================

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith('--')) {
        args[key] = next;
        i++;
      } else {
        args[key] = true;
      }
    } else {
      args._.push(argv[i]);
    }
  }
  return args;
}

// ============================================================
// Bridge Server (serve command)
// ============================================================

async function serve() {
  let extensionWs = null;
  const pendingRequests = new Map();
  let recordingState = null; // { outputFile, tempDir, frameCount, startTime, captions }
  let msgId = 0;

  function sendToExtension(type, data = {}) {
    return new Promise((resolve, reject) => {
      if (!extensionWs || extensionWs.readyState !== WebSocket.OPEN) {
        reject(
          new Error(
            'Chrome extension not connected. Make sure it is installed and Chrome is open.'
          )
        );
        return;
      }

      const id = ++msgId;
      const timeout = setTimeout(() => {
        pendingRequests.delete(id);
        reject(new Error('Extension response timeout'));
      }, 30_000);

      pendingRequests.set(id, { resolve, reject, timeout });
      extensionWs.send(JSON.stringify({ type, id, ...data }));
    });
  }

  function readBody(req) {
    return new Promise((resolve) => {
      let body = '';
      req.on('data', (c) => (body += c));
      req.on('end', () => resolve(body));
    });
  }

  // Save an incoming frame to the temp directory
  function saveFrame(base64Data) {
    if (!recordingState) return;
    const name = `frame_${String(recordingState.frameCount).padStart(6, '0')}.jpg`;
    fs.writeFileSync(
      path.join(recordingState.tempDir, name),
      Buffer.from(base64Data, 'base64')
    );
    recordingState.frameCount++;
  }

  // Encode frames to video with FFmpeg
  async function encodeVideo(tempDir, outputFile, frameCount) {
    const ffmpegPath = require('ffmpeg-static');
    const ext = path.extname(outputFile).toLowerCase();

    const ffmpegArgs = [
      '-framerate', String(FPS),
      '-i', path.join(tempDir, 'frame_%06d.jpg'),
      // Scale to even dimensions (required for yuv420p)
      '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
    ];

    if (ext === '.webm') {
      ffmpegArgs.push('-c:v', 'libvpx-vp9', '-crf', '35', '-b:v', '0');
    } else {
      ffmpegArgs.push('-c:v', 'libx264', '-preset', 'fast', '-crf', '28');
    }

    ffmpegArgs.push('-pix_fmt', 'yuv420p', '-y', outputFile);

    await new Promise((resolve, reject) => {
      const proc = spawn(ffmpegPath, ffmpegArgs, {
        stdio: ['ignore', 'pipe', 'pipe'],
      });
      let stderr = '';
      proc.stderr.on('data', (chunk) => { stderr += chunk.toString(); });
      proc.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          console.error('FFmpeg stderr:', stderr.slice(-500));
          reject(new Error(`FFmpeg exit code ${code}`));
        }
      });
      proc.on('error', reject);
    });
  }

  function cleanupTempDir(dir) {
    try {
      fs.readdirSync(dir).forEach((f) => fs.unlinkSync(path.join(dir, f)));
      fs.rmdirSync(dir);
    } catch {}
  }

  // HTTP server for CLI commands
  const server = http.createServer(async (req, res) => {
    res.setHeader('Content-Type', 'application/json');

    try {
      // --- List tabs ---
      if (req.method === 'GET' && req.url === '/api/tabs') {
        const result = await sendToExtension('list_tabs');
        res.end(JSON.stringify({ tabs: result.tabs }));
      }
      // --- Start recording ---
      else if (req.method === 'POST' && req.url === '/api/start') {
        const body = JSON.parse(await readBody(req));

        if (recordingState) {
          res.statusCode = 400;
          res.end(JSON.stringify({ error: 'Already recording. Run stop first.' }));
          return;
        }

        // Create temp dir for frames
        const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'screen-rec-'));

        const result = await sendToExtension('start_recording', {
          tabId: parseInt(body.tabId),
        });

        if (result.type === 'error') {
          cleanupTempDir(tempDir);
          res.statusCode = 500;
          res.end(JSON.stringify({ error: result.error }));
          return;
        }

        recordingState = {
          outputFile: body.outputFile,
          tempDir,
          frameCount: 0,
          startTime: Date.now(),
          captions: [],
        };

        res.end(JSON.stringify({ status: 'recording_started' }));
      }
      // --- Stop recording ---
      else if (req.method === 'POST' && req.url === '/api/stop') {
        if (!recordingState) {
          res.statusCode = 400;
          res.end(JSON.stringify({ error: 'No active recording' }));
          return;
        }

        const { outputFile, tempDir, frameCount, startTime, captions } = recordingState;
        const duration = ((Date.now() - startTime) / 1000).toFixed(1);

        // Tell extension to stop
        try {
          await sendToExtension('stop_recording');
        } catch {}

        // Small delay to catch any last frames in transit
        await new Promise((r) => setTimeout(r, 500));

        const finalFrameCount = recordingState.frameCount;
        const finalCaptions = recordingState.captions;
        recordingState = null;

        if (finalFrameCount === 0) {
          cleanupTempDir(tempDir);
          res.end(
            JSON.stringify({
              status: 'recording_stopped',
              warning: 'No frames captured',
              duration: `${duration}s`,
              frames: 0,
            })
          );
          return;
        }

        // Encode frames to video
        console.log(`Encoding ${finalFrameCount} frames...`);
        await encodeVideo(tempDir, outputFile, finalFrameCount);
        cleanupTempDir(tempDir);

        const sizeMB = (fs.statSync(outputFile).size / 1024 / 1024).toFixed(2);

        // Save captions file alongside the video
        const videoDuration = Math.round((finalFrameCount / FPS) * 10) / 10;
        const wallClockDuration = parseFloat(duration);
        let captionsFile = null;
        if (finalCaptions && finalCaptions.length > 0) {
          // Convert wall clock offsets to video timestamps
          // videoTime = wallClockOffset * (videoDuration / wallClockDuration)
          const ratio = wallClockDuration > 0 ? videoDuration / wallClockDuration : 1;
          const convertedCaptions = finalCaptions.map((c) => ({
            videoTime: Math.round(c.wallClockOffset * ratio * 10) / 10,
            text: c.text,
          }));

          const captionsPath = outputFile.replace(/\.[^.]+$/, '.captions.json');
          const captionsData = {
            videoFile: outputFile,
            videoDuration: videoDuration,
            fps: FPS,
            totalFrames: finalFrameCount,
            captions: convertedCaptions,
          };
          fs.writeFileSync(captionsPath, JSON.stringify(captionsData, null, 2));
          captionsFile = captionsPath;
        }

        res.end(
          JSON.stringify({
            status: 'recording_stopped',
            file: outputFile,
            captionsFile: captionsFile,
            duration: `${duration}s`,
            frames: finalFrameCount,
            size: `${sizeMB}MB`,
          })
        );
      }
      // --- Add caption ---
      else if (req.method === 'POST' && req.url === '/api/caption') {
        if (!recordingState) {
          res.statusCode = 400;
          res.end(JSON.stringify({ error: 'No active recording' }));
          return;
        }

        const body = JSON.parse(await readBody(req));
        const text = body.text || '';
        const wallClockOffset = (Date.now() - recordingState.startTime) / 1000;

        recordingState.captions.push({
          wallClockOffset: Math.round(wallClockOffset * 10) / 10,
          text,
        });

        res.end(JSON.stringify({
          status: 'caption_added',
          wallClockOffset: `${wallClockOffset.toFixed(1)}s`,
          text,
        }));
      }
      // --- Status ---
      else if (req.method === 'GET' && req.url === '/api/status') {
        const connected =
          extensionWs && extensionWs.readyState === WebSocket.OPEN;
        if (recordingState) {
          const duration = (
            (Date.now() - recordingState.startTime) /
            1000
          ).toFixed(1);
          res.end(
            JSON.stringify({
              status: 'recording',
              extensionConnected: connected,
              outputFile: recordingState.outputFile,
              frames: recordingState.frameCount,
              duration: `${duration}s`,
            })
          );
        } else {
          res.end(
            JSON.stringify({ status: 'idle', extensionConnected: connected })
          );
        }
      } else {
        res.statusCode = 404;
        res.end(JSON.stringify({ error: 'Not found' }));
      }
    } catch (err) {
      res.statusCode = 500;
      res.end(JSON.stringify({ error: err.message }));
    }
  });

  // WebSocket server for extension connection
  const wss = new WebSocket.Server({ server, maxPayload: 10 * 1024 * 1024 });

  wss.on('connection', (ws) => {
    console.log('Extension connected.');
    extensionWs = ws;

    ws.on('message', (raw) => {
      let msg;
      try {
        msg = JSON.parse(raw.toString());
      } catch {
        return;
      }

      // Streaming frame — save to disk immediately
      if (msg.type === 'frame') {
        saveFrame(msg.data);
        return;
      }

      // Response to a pending request
      if (msg.id && pendingRequests.has(msg.id)) {
        const { resolve, timeout } = pendingRequests.get(msg.id);
        clearTimeout(timeout);
        pendingRequests.delete(msg.id);
        resolve(msg);
      }
    });

    ws.on('close', () => {
      console.log('Extension disconnected.');
      if (extensionWs === ws) extensionWs = null;
    });
  });

  server.listen(PORT, () => {
    console.log(`Record Screen server running on port ${PORT}`);
    console.log('Waiting for Chrome extension to connect...');

    fs.writeFileSync(
      STATE_FILE,
      JSON.stringify({ pid: process.pid, port: PORT, startTime: Date.now() })
    );
  });

  const cleanup = () => {
    try {
      fs.unlinkSync(STATE_FILE);
    } catch {}
    process.exit(0);
  };
  process.on('SIGINT', cleanup);
  process.on('SIGTERM', cleanup);
}

// ============================================================
// CLI helpers
// ============================================================

function apiRequest(method, urlPath, body = null, timeoutMs = 120_000) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost',
      port: PORT,
      path: urlPath,
      method,
      headers: { 'Content-Type': 'application/json' },
      timeout: timeoutMs,
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (c) => (data += c));
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch {
          reject(new Error(`Invalid response: ${data}`));
        }
      });
    });

    req.on('error', () => {
      reject(
        new Error('Cannot connect to server. Run "node record.js serve" first.')
      );
    });
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timed out'));
    });

    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

async function ensureServer() {
  try {
    await apiRequest('GET', '/api/status', null, 3000);
  } catch {
    console.log('Starting bridge server in background...');
    const proc = spawn(process.execPath, [__filename, 'serve'], {
      detached: true,
      stdio: 'ignore',
    });
    proc.unref();

    for (let i = 0; i < 20; i++) {
      await new Promise((r) => setTimeout(r, 500));
      try {
        await apiRequest('GET', '/api/status', null, 2000);
        console.log('Server started.');
        return;
      } catch {}
    }
    throw new Error('Failed to start bridge server');
  }
}

// ============================================================
// CLI Commands
// ============================================================

async function listTabs() {
  await ensureServer();
  const result = await apiRequest('GET', '/api/tabs');

  if (result.error) {
    console.error(`Error: ${result.error}`);
    process.exit(1);
  }

  const tabs = result.tabs;
  if (!tabs || tabs.length === 0) {
    console.log('No tabs found.');
    return;
  }

  console.log('');
  tabs.forEach((tab) => {
    console.log(`  ${tab.index}) ${tab.title}`);
    console.log(`     ${tab.url}`);
    console.log(`     id: ${tab.id}`);
    console.log('');
  });
  console.log(`${tabs.length} tab(s) found.`);
}

async function startRecording(args) {
  const tabArg = args.tab;
  const outputFile = path.resolve(args.out || 'recording.mp4');

  if (!tabArg) {
    console.error('Error: --tab is required.');
    console.error('Run "node record.js list" to see available tabs.');
    process.exit(1);
  }

  await ensureServer();

  // Resolve tab index to Chrome tab ID
  const tabsResult = await apiRequest('GET', '/api/tabs');
  if (tabsResult.error) {
    console.error(`Error: ${tabsResult.error}`);
    process.exit(1);
  }

  let tabId;
  const index = parseInt(tabArg);
  if (!isNaN(index) && index >= 1 && index <= tabsResult.tabs.length) {
    tabId = tabsResult.tabs[index - 1].id;
  } else {
    tabId = parseInt(tabArg);
  }

  const tabInfo = tabsResult.tabs.find((t) => t.id === tabId);
  const result = await apiRequest('POST', '/api/start', { tabId, outputFile });

  if (result.error) {
    console.error(`Error: ${result.error}`);
    process.exit(1);
  }

  console.log('RECORDING_STARTED');
  console.log(`TAB: ${tabInfo?.title || tabId}`);
  console.log(`FILE: ${outputFile}`);
}

async function stopRecording() {
  await ensureServer();

  console.log('Stopping recording (encoding may take a moment)...');
  const result = await apiRequest('POST', '/api/stop');

  if (result.error) {
    console.error(`Error: ${result.error}`);
    process.exit(1);
  }

  console.log('RECORDING_STOPPED');
  console.log(`DURATION: ${result.duration}`);
  console.log(`FRAMES: ${result.frames}`);
  console.log(`SIZE: ${result.size || 'n/a'}`);
  console.log(`FILE: ${result.file || 'n/a'}`);
  if (result.captionsFile) {
    console.log(`CAPTIONS: ${result.captionsFile}`);
  }
}

async function addCaption(args) {
  const text = args._.slice(1).join(' ') || args.text;
  if (!text) {
    console.error('Error: caption text is required.');
    console.error('Usage: node record.js caption "Clicked the login button"');
    process.exit(1);
  }

  // Skip ensureServer() — caption must be fast. Send the CLI_TIMESTAMP
  // captured at process start so the server uses that instead of Date.now().
  const result = await apiRequest('POST', '/api/caption', {
    text,
    timestamp: CLI_TIMESTAMP,
  });

  if (result.error) {
    console.error(`Error: ${result.error}`);
    process.exit(1);
  }

  console.log(`CAPTION_ADDED @ ${result.wallClockOffset}`);
  console.log(`TEXT: ${result.text}`);
}

async function showStatus() {
  await ensureServer();
  const result = await apiRequest('GET', '/api/status');

  if (result.status === 'recording') {
    console.log('RECORDING_ACTIVE');
    console.log(`DURATION: ${result.duration}`);
    console.log(`FRAMES: ${result.frames}`);
    console.log(`FILE: ${result.outputFile}`);
    console.log(
      `EXTENSION: ${result.extensionConnected ? 'connected' : 'disconnected'}`
    );
  } else {
    console.log('NO_ACTIVE_RECORDING');
    console.log(
      `EXTENSION: ${result.extensionConnected ? 'connected' : 'disconnected'}`
    );
  }
}

// ============================================================
// Main
// ============================================================

const args = parseArgs(process.argv.slice(2));
const command = args._[0];

(async () => {
  try {
    switch (command) {
      case 'serve':
        await serve();
        break;
      case 'list':
        await listTabs();
        break;
      case 'start':
        await startRecording(args);
        break;
      case 'stop':
        await stopRecording();
        break;
      case 'caption':
        await addCaption(args);
        break;
      case 'status':
        await showStatus();
        break;
      default:
        console.log(
          `Record Screen Tool — Chrome Extension Based

Usage:
  node record.js serve                           Start the bridge server
  node record.js list                            List available Chrome tabs
  node record.js start --tab <n> --out <file>    Start recording a tab
  node record.js caption <text>                  Add a caption at the current video time
  node record.js stop                            Stop recording & save video
  node record.js status                          Check recording status

Start options:
  --tab <n>      Tab number from list (1,2,3...) or Chrome tab ID  [required]
  --out <file>   Output file path (.mp4 or .webm)                  [default: recording.mp4]

Output formats:
  .mp4           H.264 (encoded via FFmpeg)
  .webm          VP9 (encoded via FFmpeg)

Setup:
  1. Load the Chrome extension from the extension/ directory
     (chrome://extensions > Developer mode > Load unpacked)
  2. The bridge server auto-starts when you run list/start/stop
     (or run "node record.js serve" manually)

Example:
  node record.js list
  node record.js start --tab 1 --out demo.mp4
  node record.js caption "Navigated to login page"
  # ... interact with the browser ...
  node record.js caption "Clicked submit button"
  node record.js stop`
        );
    }
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
})();
