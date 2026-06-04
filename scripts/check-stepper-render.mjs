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

/* Returns an array of failure messages (empty === contract holds). */
function checkStepper(html) {
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

  // JS contract
  if (!/function initConceptSteppers\(/.test(html))
    f.push("initConceptSteppers() not found in dashboard JS");
  if (!/removeAttribute\("hidden"\)/.test(html))
    f.push('stepper JS must reveal controls via removeAttribute("hidden")');
  if (!/prefers-reduced-motion: reduce/.test(html))
    f.push("stepper JS must carry the prefers-reduced-motion: reduce guard");
  if (!/play\.remove\(\)/.test(html))
    f.push("reduced-motion branch must remove the Play button (play.remove())");

  return f;
}

const html = readFileSync(htmlPath, "utf8");
const failures = checkStepper(html);

/* Must-fail half (inline, self-proving): break the two invariants the gate
 * most cares about and confirm the SAME checks flag them. */
{
  const broken = html
    .replace(/prefers-reduced-motion: reduce/g, "prefers-XXX")
    // force a second active frame so the "exactly one active" invariant breaks
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
