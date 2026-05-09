const SERVER_URL = 'ws://localhost:9234';

let ws = null;
let recording = false;
let recordingTabId = null;
let recordingWindowId = null;
let captureTimer = null;
const FPS = 5;

// --- WebSocket connection to CLI bridge server ---

function connect() {
  if (ws && ws.readyState === WebSocket.OPEN) return;

  try {
    ws = new WebSocket(SERVER_URL);
  } catch {
    return;
  }

  ws.onopen = () => {
    console.log('[RecordScreen] Connected to bridge server');
  };

  ws.onmessage = async (event) => {
    let msg;
    try {
      msg = JSON.parse(event.data);
    } catch {
      return;
    }

    switch (msg.type) {
      case 'list_tabs':
        await handleListTabs(msg);
        break;
      case 'start_recording':
        await handleStartRecording(msg);
        break;
      case 'stop_recording':
        await handleStopRecording(msg);
        break;
    }
  };

  ws.onclose = () => {
    ws = null;
  };

  ws.onerror = () => {};
}

function send(data) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(data));
  }
}

// --- Command handlers ---

async function handleListTabs(msg) {
  try {
    const tabs = await chrome.tabs.query({});
    const pages = tabs.filter((t) => t.url && !t.url.startsWith('chrome://'));
    send({
      type: 'tabs_list',
      id: msg.id,
      tabs: pages.map((t, i) => ({
        index: i + 1,
        id: t.id,
        title: t.title || '(untitled)',
        url: t.url,
      })),
    });
  } catch (err) {
    send({ type: 'error', id: msg.id, error: err.message });
  }
}

async function handleStartRecording(msg) {
  const tabId = msg.tabId;

  try {
    // Focus the tab so captureVisibleTab can capture it
    const tab = await chrome.tabs.get(tabId);
    recordingWindowId = tab.windowId;
    await chrome.tabs.update(tabId, { active: true });
    await chrome.windows.update(tab.windowId, { focused: true });

    // Wait for the tab to render before capturing
    await new Promise((r) => setTimeout(r, 500));

    recording = true;
    recordingTabId = tabId;

    // Poll for screenshots using captureVisibleTab
    let capturing = false;
    let framesSent = 0;
    captureTimer = setInterval(async () => {
      if (!recording || capturing) return;
      capturing = true;
      try {
        const dataUrl = await chrome.tabs.captureVisibleTab(recordingWindowId, {
          format: 'jpeg',
          quality: 60,
        });
        if (dataUrl && recording) {
          // Strip the data:image/jpeg;base64, prefix
          const base64 = dataUrl.split(',')[1];
          if (base64) {
            send({ type: 'frame', data: base64 });
            framesSent++;
            if (framesSent <= 3 || framesSent % 10 === 0) {
              console.log('[RecordScreen] Frames sent:', framesSent);
            }
          }
        }
      } catch (err) {
        console.log('[RecordScreen] Capture error:', err.message || err);
      }
      capturing = false;
    }, 1000 / FPS);

    send({ type: 'recording_started', id: msg.id });
  } catch (err) {
    send({ type: 'error', id: msg.id, error: String(err.message || err) });
  }
}

async function handleStopRecording(msg) {
  try {
    recording = false;
    if (captureTimer) {
      clearInterval(captureTimer);
      captureTimer = null;
    }
    recordingTabId = null;
    recordingWindowId = null;
    send({ type: 'recording_stopped', id: msg.id });
  } catch (err) {
    send({ type: 'error', id: msg.id, error: err.message });
  }
}

// --- Keep-alive & reconnection ---

chrome.alarms.create('reconnect', { periodInMinutes: 0.5 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'reconnect') {
    connect();
  }
});

chrome.runtime.onInstalled.addListener(() => connect());
chrome.runtime.onStartup.addListener(() => connect());

// Initial connection
connect();
