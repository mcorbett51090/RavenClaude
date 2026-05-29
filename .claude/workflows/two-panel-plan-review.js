export const meta = {
  name: "two-panel-plan-review",
  description:
    "Two fresh-independent expert panels review a strategic plan, fill its gaps, author a tactical build plan, then a different panel cold-reviews the build plan and emits P0/P1 recommendations.",
  whenToUse:
    "When you have a strategic plan (a 'what/why' doc) and want it stress-tested by one expert panel, gap-filled, accompanied by a tactical build plan (a 'how' doc), and then have THAT build plan independently cold-reviewed by a different panel. Useful before committing engineering effort to a non-trivial proposal.",
  phases: [
    {
      title: "Panel 1 review of the strategic plan",
      detail: "4 lenses by default: architect, security, ops, devil's-advocate",
    },
    {
      title: "Synthesize Panel 1 + update plan + author build plan",
      detail: "gap-fill the plan body; emit a tactical build plan; verify both writes",
    },
    {
      title: "Panel 2 cold-review of build plan",
      detail:
        "4 different lenses by default: tester-QA, project-manager, deep-researcher, prompt-engineer",
    },
    {
      title: "Synthesize Panel 2 + P0/P1 recommendations appendix",
      detail: "append a P0/P1 Recommendations section to the build plan",
    },
  ],
};

// ─── Args contract ─────────────────────────────────────────────────────────────
// Pass via Workflow({ name: 'two-panel-plan-review', args: { ... } }).
//
// Required:
//   inputPlanPath: string        — absolute path to the strategic plan to review.
//   outputBuildPlanPath: string  — absolute path where the build plan will be written.
//   contextSummary: string       — 1-paragraph background reviewers need without reading the
//                                   prior chat. Frames the problem domain.
//
// Optional (sensible defaults baked in):
//   panel1Lenses: Array<{key, agentType, lens}>
//     Default: architect / security / ops / devil's-advocate (uses ravenclaude-core agents).
//   panel2Lenses: Array<{key, agentType, lens}>
//     Default: tester-qa / project-manager / deep-researcher / prompt-engineer.
//   severityRubric: string       — P0/P1/P2 rubric prose. Default is the canonical version.
//   buildPlanRequirements: string — extra requirements the build plan must include beyond the
//                                    generic shape. Folded into the synth-1 brief verbatim.
//   panel1Axes: string[]          — extra crux axes Panel 1 must engage. Folded into framing.
//   panel2Axes: string[]          — extra crux axes Panel 2 must engage. Folded into framing.
// ─────────────────────────────────────────────────────────────────────────────────

const a = args || {};

if (!a.inputPlanPath || !a.outputBuildPlanPath || !a.contextSummary) {
  throw new Error(
    "two-panel-plan-review: missing required args. Provide { inputPlanPath, outputBuildPlanPath, contextSummary }. " +
      `Got: ${JSON.stringify({ hasInputPlanPath: !!a.inputPlanPath, hasOutputBuildPlanPath: !!a.outputBuildPlanPath, hasContextSummary: !!a.contextSummary })}`,
  );
}

const PLAN_PATH = a.inputPlanPath;
const BUILD_PATH = a.outputBuildPlanPath;
const CONTEXT = a.contextSummary;

// ─── Defaults ──────────────────────────────────────────────────────────────────

const DEFAULT_SEVERITY_RUBRIC = `
Use this 3-tier severity rubric on EVERY gap you raise:
- **P0** (must-fix before any build starts): a structural defect that, if shipped, defeats the plan's stated purpose, introduces a silent-failure mode, breaks the safety floor, or makes the plan unimplementable. Include only what you can DEFEND as P0 — over-classifying erodes the signal.
- **P1** (must-fix before merge): a real defect that would surface as broken behavior, lost data, undocumented breakage, or a regression in a guarantee the plan claims. Strong enough to block PR approval.
- **P2** (nice-to-fix): rough edges, missing nuance, polish, future-proofing. Not blocking.

For each gap include CONCRETE evidence (quote the plan's exact words / cite the section) and a CONCRETE recommendation (a writable instruction, not a vague "consider"). Vague gaps are worse than no gaps.
`;

const DEFAULT_PANEL1_LENSES = [
  {
    key: "architect",
    agentType: "ravenclaude-core:architect",
    lens: "System architecture — coupling, single-source-of-truth, blast radius, debuggability, fail-loud vs fail-silent classes, multi-process trust model.",
  },
  {
    key: "security",
    agentType: "ravenclaude-core:security-reviewer",
    lens: "Security and trust-boundary integrity — auth chain, credential surface, injection vectors at new ingress paths, secret egress, can guarantees be silently bypassed.",
  },
  {
    key: "ops",
    agentType: "ravenclaude-core:project-manager",
    lens: "Ops / maintainability over a SOLO maintainer's time horizon — observability, debuggability when something fails, support cost when a dependency releases break things, doc-rot risk, upgrade story.",
  },
  {
    key: "devils_advocate",
    agentType: "ravenclaude-core:architect",
    lens: "DEVIL'S ADVOCATE — build the strongest case AGAINST doing this at all. Attack the premise, the framing, the 'this is small/thin' claims, the additive/non-invasive promises. Default toward 'do not build' unless evidence forbids it.",
  },
];

const DEFAULT_PANEL2_LENSES = [
  {
    key: "tester_qa",
    agentType: "ravenclaude-core:tester-qa",
    lens: "Testability — do listed gates actually test what they claim? Are there test fixtures for both the happy path and each failure mode? Are there positive AND negative controls for load-bearing invariants?",
  },
  {
    key: "project_manager",
    agentType: "ravenclaude-core:project-manager",
    lens: "Project execution — task granularity, dependencies between phases, rollout/rollback, version bumping, named owner per phase, time estimate plausibility, RAID-log-worthy risks.",
  },
  {
    key: "deep_researcher",
    agentType: "ravenclaude-core:deep-researcher",
    lens: "Evidence and grounding — is every load-bearing technical claim cited or marked unverified? Are there facts being asserted without a primary source the build plan tells you to fetch?",
  },
  {
    key: "prompt_engineer",
    agentType: "ravenclaude-core:prompt-engineer",
    lens: "Surface design — are the contracts (function signatures, schemas, error envelopes) actually a good shape for the consumer on the other side? Does data round-trip cleanly across each boundary?",
  },
];

const DEFAULT_BUILD_PLAN_REQUIREMENTS = `
The build plan must include:

1. **Header**: a clear title + a status line marking it as v1 awaiting approval + a one-line pointer back to the strategic plan.
2. **Citations table**: every load-bearing technical claim either has a cited primary source verified this session OR carries an \`[unverified]\` marker AND a gate that settles it.
3. **Pre-build gates**: any open questions in the strategic plan get a concrete gate (a command/script that settles them), with (a) the gate, (b) the pass criterion, (c) the disposition if it fails.
4. **Phase-by-phase task tree**: each phase is a numbered task list. For each task, name the file paths it touches, the existing helpers it composes (cite by file:line where possible), its acceptance test, and its gate.
5. **Schemas / contracts**: any new public surface (a function signature, a JSON schema, an MCP tool, an API endpoint, a CLI flag) gets its exact shape specified — type-level, not prose.
6. **Rollout & rollback**: how a consumer enables and disables the feature. The disable path must NOT depend on the feature itself (so it works when the feature is broken).
7. **Telemetry & observability**: where calls log, how to debug a failure, where artifacts land.
8. **Versioning + migration note**: which version this lands under, what the migration note says, whether consumers see any change on \`/plugin marketplace update\`.
9. **Cross-cutting close-out gates**: prettier, audit-gates, freshness checks, manifest version-match, layout allow-list updates.
10. **Effort estimates** per task in order-of-magnitude (quarter-day / half-day / day / multi-day). Honest, no padding.

Target length: ~600-1000 lines of dense, scannable markdown. No filler. Tables only where tabular helps.
`;

const SEVERITY_RUBRIC = a.severityRubric || DEFAULT_SEVERITY_RUBRIC;
const PANEL1_LENSES =
  Array.isArray(a.panel1Lenses) && a.panel1Lenses.length ? a.panel1Lenses : DEFAULT_PANEL1_LENSES;
const PANEL2_LENSES =
  Array.isArray(a.panel2Lenses) && a.panel2Lenses.length ? a.panel2Lenses : DEFAULT_PANEL2_LENSES;
const BUILD_PLAN_REQUIREMENTS = a.buildPlanRequirements || DEFAULT_BUILD_PLAN_REQUIREMENTS;
const PANEL1_AXES = Array.isArray(a.panel1Axes) ? a.panel1Axes : [];
const PANEL2_AXES = Array.isArray(a.panel2Axes) ? a.panel2Axes : [];

// ─── Shared schema ─────────────────────────────────────────────────────────────

const GAP_SCHEMA = {
  type: "object",
  additionalProperties: false,
  properties: {
    lens: { type: "string", description: "one-line description of the lens you reviewed from" },
    artifact_present: {
      type: "boolean",
      description:
        "true if you successfully Read the file you were asked to review. False means you must populate gaps with a single P0 meta-gap reporting the missing artifact and STOP.",
    },
    overall_assessment: { type: "string", description: "2-3 sentence summary" },
    strengths: {
      type: "array",
      items: { type: "string" },
      description: "load-bearing things the plan got right; 1-5 items max",
    },
    gaps: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        properties: {
          id: { type: "string", description: 'short stable id (e.g. "arch-1")' },
          severity: { type: "string", enum: ["P0", "P1", "P2"] },
          title: { type: "string" },
          evidence: {
            type: "string",
            description: "concrete evidence — quote / cite the plan section that is wrong/missing",
          },
          recommendation: {
            type: "string",
            description: "concrete writable fix — what to add/remove/change",
          },
        },
        required: ["id", "severity", "title", "evidence", "recommendation"],
      },
    },
  },
  required: ["lens", "artifact_present", "overall_assessment", "gaps"],
};

// ─── Framings ──────────────────────────────────────────────────────────────────

const PRECONDITION_PROTOCOL = `
**MANDATORY PRECONDITION (read this first):** Before reviewing, use the Read tool on the target file. If Read FAILS for any reason (file does not exist, permission denied, empty file):
1. Set \`artifact_present\` to false.
2. Return exactly ONE gap with severity P0, id "meta-1", titled "Target artifact missing or unreadable", evidence quoting the Read error, and a recommendation that the orchestrator confirm the file was written before re-invoking this review.
3. STOP — do not fabricate, do not infer from sibling documents, do not Web-search the topic.

If Read succeeds, set \`artifact_present\` to true and proceed with substantive review.
`;

const PANEL1_FRAMING = `
You are part of a ${PANEL1_LENSES.length}-lens expert panel reviewing a STRATEGIC plan. Your job is GAP ANALYSIS — find what the plan got wrong, missed, or under-specified — NOT to rewrite it. A separate synthesis agent will fold your gaps into an updated plan.

# Target file
${PLAN_PATH}

${PRECONDITION_PROTOCOL}

# Context
${CONTEXT}

${SEVERITY_RUBRIC}

# Crux axes you must engage for any P0/P1 you raise
1. **Trust-boundary integrity / load-bearing-claim soundness.** Does the plan actually deliver what it promises, or are there execution paths where its guarantees silently degrade?
2. **Concrete unstated assumptions.** What load-bearing fact does the plan assume but not verify or cite?
3. **Failure modes the plan doesn't enumerate.**
4. **Verification holes.** Are the plan's gates actually gated by what they claim? Is each "verify" a real test or just prose?
${PANEL1_AXES.length ? PANEL1_AXES.map((x, i) => `${5 + i}. **${x}**`).join("\n") : ""}

Be concrete; cite the plan's exact words. P0s should be defensible to a skeptical reviewer. Return findings per the schema.
`;

function panel2Framing(skipStrategicPlan) {
  return `
You are part of a DIFFERENT ${PANEL2_LENSES.length}-lens expert panel reviewing a tactical BUILD PLAN. CRITICAL: this is a COLD READ. You have NO knowledge of the strategic plan that produced this build plan, no knowledge of any prior expert panel, no knowledge of the verdict process. Your job is to review the build plan ON ITS OWN MERITS as a tactical artifact a coder will execute from.

# Target file
${BUILD_PATH}

${skipStrategicPlan ? `**DO NOT read \`${PLAN_PATH}\` (the strategic plan)** — your independence is the value here. If the build plan references the strategic plan, evaluate the build plan's INTERNAL completeness; assume any unfamiliar term in the build plan needs to be defined or cited there.` : ""}

${PRECONDITION_PROTOCOL}

# Context
${CONTEXT}

${SEVERITY_RUBRIC}

# Crux axes you must engage for any P0/P1 you raise
1. **Executability** — can a coder pick this up and execute it, or are critical paths under-specified?
2. **Testability** — does each phase have a real gate, or is it handwaved?
3. **Rollout safety** — what happens to a consumer mid-build, or when a feature flag is half-on?
4. **Observability** — when this fails in production for a real user, do they have enough telemetry to debug it?
5. **Schema / contract gaps** — are interfaces specified precisely enough that two engineers would implement them identically?
${PANEL2_AXES.length ? PANEL2_AXES.map((x, i) => `${6 + i}. **${x}**`).join("\n") : ""}

P0s should be defensible to a skeptical reviewer who only sees the build plan. Return findings per the schema.
`;
}

// ─── Helpers ───────────────────────────────────────────────────────────────────

function digestPanel(results, lenses, label) {
  return results
    .map(
      (p, i) =>
        `### ${label} / ${lenses[i].key} (${p.lens})\n` +
        `**Assessment:** ${p.overall_assessment}\n` +
        `**Strengths:** ${(p.strengths || []).map((s) => `\n  - ${s}`).join("")}\n` +
        `**Gaps (${p.gaps?.length || 0}):**\n` +
        (p.gaps || [])
          .map(
            (g) =>
              `  - **${g.severity}** \`${g.id}\` ${g.title}\n    Evidence: ${g.evidence}\n    Rec: ${g.recommendation}`,
          )
          .join("\n"),
    )
    .join("\n\n");
}

// ═══════════════════════════════════════════════════════════════════════════════
// Phase 1 — Panel 1 reviews the strategic plan
// ═══════════════════════════════════════════════════════════════════════════════
phase("Panel 1 review of the strategic plan");

const panel1 = await parallel(
  PANEL1_LENSES.map(
    (L) => () =>
      agent(
        `${PANEL1_FRAMING}\n\n# YOUR LENS\n${L.lens}\n\nReview the plan from this lens specifically.`,
        {
          label: `panel1:${L.key}`,
          phase: "Panel 1 review of the strategic plan",
          agentType: L.agentType,
          schema: GAP_SCHEMA,
        },
      ),
  ),
);

const okP1 = panel1.filter(Boolean);
const missingPanel1 = okP1.filter((r) => r && r.artifact_present === false).length;
if (missingPanel1 > 0) {
  log(
    `WARNING: ${missingPanel1}/${okP1.length} Panel 1 lenses reported the strategic plan is missing at ${PLAN_PATH}. Continuing — the synthesis agent will be told.`,
  );
}
const p1Digest = digestPanel(okP1, PANEL1_LENSES, "Panel 1");

log(
  `Panel 1 done: ${okP1.length}/${PANEL1_LENSES.length} lenses. Total gaps: ${okP1.reduce(
    (n, p) => n + (p.gaps?.length || 0),
    0,
  )}.`,
);

// ═══════════════════════════════════════════════════════════════════════════════
// Phase 2 — Synthesize Panel 1, update plan, author build plan
// ═══════════════════════════════════════════════════════════════════════════════
phase("Synthesize Panel 1 + update plan + author build plan");

const synth1Brief = `You are the synthesis writer. TWO STEPS:

# STEP 1 — Update the strategic plan IN PLACE to fill the gaps Panel 1 raised
1. Read the current plan at ${PLAN_PATH}.
2. For EVERY P0 and P1 gap, weave the recommended fix into the plan body (do NOT append a "gaps fixed" appendix — actually edit the substance so the gap is gone). For P2 gaps, fold in only those that improve load-bearing clarity. Preserve voice and structure.
3. When two lenses raise the SAME gap, address it once with the stronger recommendation. When two lenses raise CONTRADICTING gaps, pick the one with stronger evidence and note the dissent in a one-line parenthetical inside the relevant section.
4. Update the plan's status line at the top: include "v2 — gap-filled after panel review" with today's date.
5. Write the updated plan back to ${PLAN_PATH} with the Write tool (full overwrite is fine — you read the original).

# STEP 2 — Author the build plan at ${BUILD_PATH}
This is a NEW file (or full overwrite if it exists). It is the tactical companion to the updated strategic plan.

${BUILD_PLAN_REQUIREMENTS}

# CRITICAL — Read-after-Write verification (mandatory)
After both Writes, you MUST:
1. Read ${PLAN_PATH} — assert it is non-empty AND the new status line you added is present.
2. Read ${BUILD_PATH} — assert it is non-empty AND contains your build plan's title.

If either verification fails, retry the failing Write ONCE. If it fails again, return a structured failure report naming which file failed and the error — do NOT report success on a failed Write.

# Panel 1 gap analyses (the input you must reconcile)
${p1Digest}

Return a brief one-paragraph summary describing what changed in the plan and what the build plan covers. The summary MUST explicitly state "both files verified non-empty" or describe the failure.`;

const synth1 = await agent(synth1Brief, {
  label: "synthesis-1",
  phase: "Synthesize Panel 1 + update plan + author build plan",
});

log(`Synthesis 1 done. Verifying files on disk...`);

// ═══════════════════════════════════════════════════════════════════════════════
// Sanity check — confirm synth-1 actually wrote the build plan before convening Panel 2
// ═══════════════════════════════════════════════════════════════════════════════
const verifyBrief = `You are a verification agent. Use Read on these two files and return a JSON object describing what you found:

1. ${PLAN_PATH}
2. ${BUILD_PATH}

For each: report whether Read succeeded, the line count (rough), and whether the file looks like a substantive document (>100 lines) vs. a stub. Be terse — this is a sanity check before convening Panel 2.`;

const verifySchema = {
  type: "object",
  additionalProperties: false,
  properties: {
    plan_readable: { type: "boolean" },
    plan_line_count: { type: "number" },
    plan_substantive: { type: "boolean" },
    build_readable: { type: "boolean" },
    build_line_count: { type: "number" },
    build_substantive: { type: "boolean" },
    notes: { type: "string" },
  },
  required: [
    "plan_readable",
    "plan_line_count",
    "plan_substantive",
    "build_readable",
    "build_line_count",
    "build_substantive",
    "notes",
  ],
};

const verify = await agent(verifyBrief, {
  label: "verify-writes",
  phase: "Synthesize Panel 1 + update plan + author build plan",
  schema: verifySchema,
});

if (!verify || !verify.build_readable || !verify.build_substantive) {
  log(
    `WARNING: synth-1 did not produce a substantive build plan at ${BUILD_PATH} (readable=${verify?.build_readable}, lines=${verify?.build_line_count}). Panel 2 will run anyway and is configured to detect the missing artifact, but expect meta-gap results.`,
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// Phase 3 — Panel 2 cold-reviews the build plan
// ═══════════════════════════════════════════════════════════════════════════════
phase("Panel 2 cold-review of build plan");

const PANEL2_FRAMING = panel2Framing(true);

const panel2 = await parallel(
  PANEL2_LENSES.map(
    (L) => () =>
      agent(
        `${PANEL2_FRAMING}\n\n# YOUR LENS\n${L.lens}\n\nReview the build plan from this lens specifically. Cold read.`,
        {
          label: `panel2:${L.key}`,
          phase: "Panel 2 cold-review of build plan",
          agentType: L.agentType,
          schema: GAP_SCHEMA,
        },
      ),
  ),
);

const okP2 = panel2.filter(Boolean);
const missingPanel2 = okP2.filter((r) => r && r.artifact_present === false).length;
if (missingPanel2 > 0) {
  log(
    `WARNING: ${missingPanel2}/${okP2.length} Panel 2 lenses reported the build plan is missing/unreadable. P0/P1 appendix will still be authored with whatever substantive findings exist.`,
  );
}
const p2Digest = digestPanel(okP2, PANEL2_LENSES, "Panel 2");

log(
  `Panel 2 done: ${okP2.length}/${PANEL2_LENSES.length} lenses. Total gaps: ${okP2.reduce(
    (n, p) => n + (p.gaps?.length || 0),
    0,
  )}.`,
);

// ═══════════════════════════════════════════════════════════════════════════════
// Phase 4 — Synthesize Panel 2, append P0/P1 recommendations
// ═══════════════════════════════════════════════════════════════════════════════
phase("Synthesize Panel 2 + P0/P1 recommendations appendix");

const synth2Brief = `You are the synthesis writer. Append a NEW section to the build plan at ${BUILD_PATH} titled exactly:

\`\`\`
---

## Panel 2 cold review — P0/P1 gaps & recommendations
\`\`\`

In that section:

1. **Preamble (3-5 lines):** explain Panel 2's role and that they reviewed the build plan COLD (no Panel 1 context), to surface gaps independent of the build-plan authors' framing.
2. **P0 gaps** — every P0 raised by ANY lens. For each: title, the lens(es) that raised it (in parens), the evidence, the recommendation. Dedup identical gaps but PRESERVE all lenses that flagged the same issue (strengthens the signal). Order by trust-boundary / executability impact first, then alphabetical.
3. **P1 gaps** — same shape, listed below.
4. **P2 gaps** — collapse to a single bulleted list of one-liners (titles only).
5. **Where Panel 2 disagreed with itself** — explicit subsection if applicable. If two lenses raised contradicting gaps, name the disagreement and Panel 2's recommendation (pick the one with stronger evidence; tie → recommend the safer/more conservative path).
6. **Net recommendation from Panel 2** — one paragraph: is the build plan executable as-is after addressing P0s? Or does it need structural rework first? Confidence level (0-1).

Read the existing build plan first to preserve its content; then append (do NOT rewrite the existing body).

# CRITICAL — Read-after-Write verification (mandatory)
After appending, Read the build plan and assert the new "Panel 2 cold review" header is present AND the section has substantive content (not just the header). If verification fails, retry ONCE. If it fails again, return a structured failure report — do NOT report success on a failed append.

# Panel 2 gap analyses (the input you must reconcile)
${p2Digest}

Return a one-paragraph summary noting the count of P0s, P1s, P2s after dedup, plus one-line net recommendation. Summary MUST explicitly state "appendix verified present" or describe the failure.`;

const synth2 = await agent(synth2Brief, {
  label: "synthesis-2",
  phase: "Synthesize Panel 2 + P0/P1 recommendations appendix",
});

log(`Both panels complete. Plan updated; build plan written with P0/P1 recommendations appendix.`);

return {
  panel1: okP1,
  panel2: okP2,
  synthesis1: synth1,
  synthesis2: synth2,
  verify_writes: verify,
};
