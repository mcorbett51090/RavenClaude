# Gemini AI Review Integration

Gemini's multimodal capabilities allow it to watch a recording (or analyze screenshots)
and compare actual behavior against the expected behavior captions.

## Prerequisites

- Gemini API key (stored in `.env.local` as `GEMINI_API_KEY`)
- Gemini model with video/image understanding (gemini-2.0-flash or later)
- Collected evidence: screenshots, GIF/video recording, caption script

## Review Script (Node.js)

Create `tests/visual-review.mjs`:

```javascript
import { GoogleGenerativeAI } from "@google/generative-ai";
import { readFileSync } from "fs";
import { basename } from "path";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

async function reviewVisualTest(mediaPath, captionsPath) {
  const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

  const mediaBuffer = readFileSync(mediaPath);
  const captions = readFileSync(captionsPath, "utf-8");

  const mediaType = mediaPath.endsWith(".webm")
    ? "video/webm"
    : mediaPath.endsWith(".gif")
      ? "image/gif"
      : "image/png";

  const result = await model.generateContent([
    {
      inlineData: {
        mimeType: mediaType,
        data: mediaBuffer.toString("base64"),
      },
    },
    {
      text: `You are a QA engineer reviewing a visual test recording of a web application.

Below are the EXPECTED BEHAVIORS (captions) that describe what should happen at each step.
Your job is to watch the recording and compare what ACTUALLY happened against what was EXPECTED.

EXPECTED BEHAVIORS:
${captions}

For each timestamped event, provide:
1. TIMESTAMP and EVENT ID
2. STATUS: PASS (matches expected), FAIL (does not match), PARTIAL (partially matches), UNCLEAR (cannot determine from recording)
3. EXPECTED: What should have happened (from captions)
4. ACTUAL: What you observed in the recording
5. ISSUE: If FAIL or PARTIAL, describe the specific discrepancy
6. SEVERITY: Critical (app broken), High (feature broken), Medium (UX issue), Low (cosmetic)

Also check for these GENERAL ISSUES even if not in the captions:
- Visual misalignment (elements not properly positioned or overlapping)
- Text truncation or overflow
- Missing loading indicators
- Broken images or icons
- Inconsistent styling (fonts, colors, spacing)
- Accessibility concerns (tiny text, low contrast, missing labels)
- Unresponsive or frozen UI states
- Console errors visible in the recording
- Unexpected pop-ups, overlays, or dialogs
- Layout shifts (elements jumping around)

End with a SUMMARY section:
- Total checks: [number]
- PASS: [number]
- FAIL: [number]
- PARTIAL: [number]
- GENERAL ISSUES found: [number]
- Overall assessment: [one paragraph]
- Top 3 priority fixes: [numbered list]`,
    },
  ]);

  return result.response.text();
}

// CLI usage
const [mediaPath, captionsPath] = process.argv.slice(2);
if (!mediaPath || !captionsPath) {
  console.error("Usage: node visual-review.mjs <media-file> <captions-file>");
  process.exit(1);
}

console.log(`Reviewing ${basename(mediaPath)} against ${basename(captionsPath)}...\n`);
const report = await reviewVisualTest(mediaPath, captionsPath);
console.log(report);
```

## Screenshot-Based Review (Alternative)

If video recording isn't available, send individual screenshots with their captions:

```javascript
async function reviewScreenshots(screenshotDir, captionsPath) {
  const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
  const captions = readFileSync(captionsPath, "utf-8");

  // Read all screenshots in order
  const screenshots = readdirSync(screenshotDir)
    .filter((f) => f.endsWith(".png"))
    .sort()
    .map((f) => ({
      inlineData: {
        mimeType: "image/png",
        data: readFileSync(join(screenshotDir, f)).toString("base64"),
      },
    }));

  const result = await model.generateContent([
    ...screenshots,
    {
      text: `You are a QA engineer reviewing ${screenshots.length} sequential screenshots
of a web application test run. The screenshots are in chronological order.

EXPECTED BEHAVIORS:
${captions}

[same review prompt as above]`,
    },
  ]);

  return result.response.text();
}
```

## Structured Output Mode

For machine-parseable results, request JSON output:

```javascript
const result = await model.generateContent([
  mediaContent,
  {
    text: `[review prompt]

    Return your analysis as a JSON array:
    [
      {
        "event": "EVENT_ID",
        "status": "PASS|FAIL|PARTIAL|UNCLEAR",
        "expected": "...",
        "actual": "...",
        "issue": "...",
        "severity": "Critical|High|Medium|Low",
        "rootCause": "APP_CODE|TEST_SCRIPT|ENVIRONMENT|UNCLEAR",
        "suggestedFix": "..."
      }
    ]`,
  },
]);
```

## Integration with Claude in Chrome

When using Claude in Chrome, you can automate the full pipeline:

1. **Record** using `gif_creator` (start_recording → actions → stop_recording → export)
2. **Capture captions** by logging each action in the structured format
3. **Export GIF** to a known path
4. **Save captions** to a text file
5. **Run the review script** via Bash tool:

```bash
export GEMINI_API_KEY=$(grep "^GEMINI_API_KEY=" .env.local | cut -d= -f2)
node tests/visual-review.mjs ./tests/recordings/test-run.gif ./tests/recordings/captions.txt
```

## Cost Considerations

- Gemini 2.0 Flash is recommended for cost efficiency
- Video analysis costs more than screenshot analysis
- Keep recordings under 2 minutes for best results
- For large apps, run multiple focused test recordings rather than one long session
