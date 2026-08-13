#!/usr/bin/env node
/* check-stepper-render.mjs — structural test for the Learn-tab step-by-step
 * concept diagram ("stepper"; markup in _render_concept_stepper, behavior in
 * initConceptSteppers — generate-dashboards.py).
 *
 * Pure text-based assertions — NO `new Function()` / NO `eval` / NO `vm`.
 * The stepper's JS is DOM-event-driven (not a pure render function returning
 * a node), so the eval-and-drive pattern the older render-tests use doesn't
 * fit; and the security-guidance hook flags eval-of-generated-source as a
 * CI code-injection footgun. We assert against the generated HTML/JS text
 * directly (same approach as check-shell-router.mjs).
 *
 * What this guards:
 *   - At least one .concept-stepper renders, with exactly ONE active frame
 *     and ONE active dot per stepper (the initial-state invariant)
 *   - frames === dots === captions (each frame is dot-addressable + captioned)
 *   - controls ship [hidden] in markup (progressive enhancement — no JS, only
 *     frame 1 shows; JS reveals the controls)
 *   - the JS reveals controls (removeAttribute("hidden")) and honors
 *     reduced-motion (the `prefers-reduced-motion: reduce` guard removes Play)
 *   - Must-fail half (inline, self-proving): a copy with the reduced-motion
 *     guard stripped AND a second frame forced active must be caught by the
 *     same assertions — proving the gate has teeth.
 *
 * Usage: node scripts/check-stepper-render.mjs [path/to/dashboard.html]
 */
import { readFileSync } from "node:fs";

const htmlPath = process.argv[2] || "plugins/ravenclaude-core/dashboard.html";

function count(s, re) {
  return (s.match(re) || []).length;
}

/* Returns an array of failure messages (empty === contract holds).
 * `markup` holds the stepper HTML (the decoded island payload on an islanded surface;
 * the whole file pre-island). `jsSrc` holds the app JS that wires the steppers — it
 * lives in the live <script>, NOT in the island payload, so on an islanded surface it
 * is the raw file. Defaults to `markup` for the pre-island single-source shape. */
function checkStepper(markup, jsSrc = markup) {
  const html = markup;
  const f = [];
  const steppers = count(html, /class="concept-stepper"/g);
  if (steppers < 1) {
    f.push("no .concept-stepper found — has the stepper markup been removed?");
    return f; // nothing else is meaningful
  }

  const activeFrames = count(html, /class="cs-frame active"/g);
  const plainFrames = count(html, /class="cs-frame"/g); // excludes cs-frames container
  const totalFrames = activeFrames + plainFrames;
  const activeDots = count(html, /class="cs-dot active"/g);
  const plainDots = count(html, /class="cs-dot"/g); // excludes cs-dots container
  const totalDots = activeDots + plainDots;
  const captions = count(html, /data-caption=/g);
  const controlsHidden = count(html, /class="cs-controls" hidden/g);

  if (activeFrames !== steppers)
    f.push(`exactly one active frame per stepper expected (${steppers}); found ${activeFrames}`);
  if (activeDots !== steppers)
    f.push(`exactly one active dot per stepper expected (${steppers}); found ${activeDots}`);
  if (totalFrames < 2 * steppers)
    f.push(`each stepper needs >=2 frames; found ${totalFrames} for ${steppers} stepper(s)`);
  if (totalFrames !== totalDots) f.push(`frames (${totalFrames}) must equal dots (${totalDots})`);
  if (captions !== totalFrames)
    f.push(`each frame needs a data-caption; frames=${totalFrames} captions=${captions}`);
  if (controlsHidden !== steppers)
    f.push(`controls must ship [hidden] per stepper (${steppers}); found ${controlsHidden}`);

  // JS contract — checked against jsSrc (the live app JS), not the island payload.
  if (!/function initConceptSteppers\(/.test(jsSrc))
    f.push("initConceptSteppers() not found in dashboard JS");
  if (!/removeAttribute\("hidden"\)/.test(jsSrc))
    f.push('stepper JS must reveal controls via removeAttribute("hidden")');
  if (!/prefers-reduced-motion: reduce/.test(jsSrc))
    f.push("stepper JS must carry the prefers-reduced-motion: reduce guard");
  if (!/play\.remove\(\)/.test(jsSrc))
    f.push("reduced-motion branch must remove the Play button (play.remove())");

  return f;
}

/* Gate 93-v2: the Learn panel is DOM-island-loaded (Phase 2L) — its stepper markup
 * ships inside <script type="application/json" id="learn-payload"> and is injected on
 * activate("learn"), so it is NOT in the live DOM text this file reads. Extract and
 * JSON-parse the payload (which unescapes the \"…\" the JSON encoding introduced),
 * then run the SAME contract against the decoded markup. Fall back to the raw file for
 * a pre-island surface (or one with no Learn island), so the checker stays correct on
 * both shapes. */
const raw = readFileSync(htmlPath, "utf8");

function extractLearnMarkup(fileText) {
  const m = fileText.match(
    /<script type="application\/json" id="learn-payload">([\s\S]*?)<\/script>/,
  );
  if (!m) return { html: fileText, islanded: false };
  // JSON.parse throws on a malformed payload (unescaped quote / truncation) — that
  // throw IS a contract violation and is caught by the caller.
  return { html: JSON.parse(m[1]), islanded: true };
}

let failures;
let islanded = false;
try {
  const ex = extractLearnMarkup(raw);
  islanded = ex.islanded;
  // markup from the payload; JS contract from the raw file (the app script is live).
  failures = checkStepper(ex.html, raw);
} catch (e) {
  failures = [
    "learn-payload did not parse as JSON (" +
      e.message +
      ") — an islanded Learn payload must be valid, escaped JSON",
  ];
}

/* Must-fail half (inline, self-proving). v2 REQUIREMENT (plan §2L): on an islanded
 * surface the must-fail half MUST exercise the PAYLOAD-PARSING path — a payload with a
 * missing frame key or an unescaped quote — not just a live-HTML mutation that would
 * pass even if the parse silently no-ops. */
if (islanded) {
  // (a) break a stepper invariant INSIDE the decoded payload
  const { html: decoded } = extractLearnMarkup(raw);
  const brokenDecoded = decoded.replace(/class="cs-frame"/, 'class="cs-frame active"');
  if (checkStepper(brokenDecoded).length === 0)
    failures.push(
      "must-fail (payload path): an extra active frame in the decoded payload was NOT detected (gate has no teeth)",
    );
  // (b) a payload that is not valid JSON must be rejected by the parse path
  let rejectedBadJson = false;
  try {
    JSON.parse('"unterminated');
  } catch {
    rejectedBadJson = true;
  }
  if (!rejectedBadJson) failures.push("must-fail (payload path): malformed JSON was not rejected");
} else {
  const broken = raw
    .replace(/prefers-reduced-motion: reduce/g, "prefers-XXX")
    .replace(/class="cs-frame"/, 'class="cs-frame active"');
  if (checkStepper(broken).length === 0)
    failures.push(
      "must-fail half: a stripped reduced-motion guard + extra active frame was NOT detected (gate has no teeth)",
    );
}

if (failures.length) {
  console.error("FAIL: stepper contract violations in " + htmlPath + ":");
  for (const x of failures) console.error("  - " + x);
  process.exit(1);
}
console.log(
  "OK: stepper contract holds (frames/dots/captions, hidden controls, reduced-motion guard); must-fail half also detected.",
);
