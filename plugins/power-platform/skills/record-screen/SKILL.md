---
name: record-screen
description: Record a Chrome browser tab to video via CLI. Use when the user wants to capture a screen recording of a browser tab. Supports list, start, stop, caption, and status subcommands. No debug mode required — uses a Chrome extension.
argument-hint: "[list | start --tab <n> --out <file> | caption <text> | stop | status]"
allowed-tools: Bash
disable-model-invocation: false
---

# Screen Recording Tool

Records Chrome browser tabs to MP4/WebM video using a Chrome extension + bridge server. No `--remote-debugging-port` flag needed — works with normal Chrome.

## First-time setup

1. Install Node dependencies:
   ```
   cd .claude/skills/record-screen/scripts && npm install
   ```

2. Load the Chrome extension:
   - Open `chrome://extensions` in Chrome
   - Enable **Developer mode** (toggle in top-right)
   - Click **Load unpacked**
   - Select the `.claude/skills/record-screen/extension` folder

That's it. The bridge server auto-starts when you run any command.

## Commands

Run the recording script with:

```
node .claude/skills/record-screen/scripts/record.js $ARGUMENTS
```

### Subcommands

| Command | Description |
|---------|-------------|
| `list` | List available Chrome tabs with their index numbers |
| `start --tab <n> [--out file.mp4]` | Start recording tab number n |
| `caption <text>` | Add a timestamped caption at the current point in the video |
| `stop` | Stop the active recording and save the video + captions file |
| `status` | Check if a recording is active and extension is connected |

### Start options

| Flag | Default | Description |
|------|---------|-------------|
| `--tab <n>` | (required) | Tab number from `list` or Chrome tab ID |
| `--out <file>` | recording.mp4 | Output file path (.mp4 or .webm) |

## Behavior

**If no arguments are provided or just `list`**: Run the list command to show available tabs, then ask the user which tab to record and what to name the output file.

**For `start`**: The recording runs server-side — the command returns immediately. Remind the user to use `/record-screen stop` when finished.

**For `caption`**: Logs a caption at the current video timestamp. The timestamp is recorded server-side and converted to video time when the recording stops, so it aligns precisely with the encoded video.

**For `stop`**: Wait for encoding to complete (may take a few seconds for MP4 transcoding), then report the output file path, duration, file size, and captions file path.

**For `status`**: Shows whether a recording is active and whether the Chrome extension is connected to the bridge server.

## Captions

**You MUST log captions during recording.** For every visible action you take on the page, run the `caption` command **in parallel** (in the same message) as the browser action. This creates a `.captions.json` file alongside the video that maps your actions to video timestamps.

Caption rules:
- Call the caption **in the same tool-call message** as the browser action (parallel execution), NOT sequentially after it
- Use `curl` for captions (NOT `node record.js caption`) — curl starts instantly vs ~1s for Node.js, giving much better timing accuracy
- Only log captions for visible actions (scroll, click, type, navigate). Do NOT log captions for waits, screenshots, or other non-visible actions
- Describe what you are doing, e.g. "Scrolling down", "Clicking the search button", "Typing 'hello' into the search box"
- Keep captions short and factual

Caption command (use this exact format):
```
curl -s -X POST http://localhost:9234/api/caption -H "Content-Type: application/json" -d "{\"text\":\"YOUR CAPTION HERE\"}"
```

Example — call BOTH tools in the same message:
```
[Tool 1 - Browser action]:  scroll down on the page
[Tool 2 - Bash]:            curl -s -X POST http://localhost:9234/api/caption -H "Content-Type: application/json" -d "{\"text\":\"Scrolling down the page\"}"
```

Both execute simultaneously, so the caption timestamp matches when the action happens in the video.

Example workflow:
```
node record.js start --tab 1 --out demo.mp4
# For each action, call the browser tool AND curl caption in parallel:
#   browser: navigate to Wikipedia  +  bash: curl caption "Navigating to Wikipedia"
#   browser: type in search box     +  bash: curl caption "Searching for Claude AI"
#   browser: scroll down            +  bash: curl caption "Scrolling down"
#   browser: click link             +  bash: curl caption "Clicking the Anthropic link"
node record.js stop
```

The captions file is saved as `<video-name>.captions.json` in the same directory as the video. Format:
```json
{
  "videoFile": "demo.mp4",
  "videoDuration": 15.2,
  "fps": 5,
  "totalFrames": 76,
  "captions": [
    { "videoTime": 1.2, "text": "Navigated to Wikipedia main page" },
    { "videoTime": 4.6, "text": "Searched for Claude AI" },
    { "videoTime": 8.0, "text": "Scrolled down the page" },
    { "videoTime": 11.4, "text": "Clicked on the Anthropic link" }
  ]
}
```

## Important notes

- The recorded tab must stay **visible and active** in its Chrome window during recording. The extension uses `captureVisibleTab` which captures whatever is currently shown.
- Frames are captured at ~5 FPS as JPEG screenshots, then encoded to video via FFmpeg on stop.

## Output formats

- `.mp4` — H.264 encoded via FFmpeg (recommended, most compatible)
- `.webm` — VP9 encoded via FFmpeg

## Architecture

The tool has three parts:
1. **Chrome extension** — uses `chrome.tabs.captureVisibleTab()` to take screenshots at 5 FPS and streams them to the bridge server
2. **Bridge server** — Node.js HTTP+WebSocket server on port 9234 that connects CLI to extension, saves frames to disk, and encodes video with FFmpeg
3. **CLI** — sends HTTP commands to the bridge server

The bridge server auto-starts in the background when you run `list`, `start`, `stop`, or `status`. The Chrome extension auto-connects to it.

## Output labels

The script outputs machine-readable labels:
- `RECORDING_STARTED` / `RECORDING_STOPPED` / `RECORDING_ACTIVE` / `NO_ACTIVE_RECORDING`
- `CAPTION_ADDED @ <time>` — caption was logged
- `TAB:` / `FILE:` / `DURATION:` / `SIZE:` / `EXTENSION:` / `CAPTIONS:` — metadata
