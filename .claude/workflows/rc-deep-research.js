// ─── Dynamic workflow (Claude Code official feature — research preview) ──────────
// Docs: https://code.claude.com/docs/en/workflows · authoritative guidance:
//   plugins/ravenclaude-core/knowledge/dynamic-workflows.md
// Saved under .claude/workflows/ → invoked as `/rc-deep-research` (or via the
// `ultracode` keyword); reads the global `args` (the research question).
// Renamed from `deep-research` on 2026-06-04: Claude Code now ships a BUNDLED
// `/deep-research`, and bundled-vs-project name precedence is undocumented, so we
// renamed to avoid the collision rather than depend on an unverified shadow rule.
// Runtime caps: ≤16 concurrent agents, 1,000 total/run, no mid-run user input, no
// direct fs/shell from the script (agents do the IO), resumable in-session.
export const meta = {
  name: "rc-deep-research",
  description:
    "Deep research harness — fan-out web searches, fetch sources, adversarially verify claims, synthesize a cited report. Includes an inline substrate adapter that reads .ravenclaude/run-config.json once at startup; when enabled:false (the default) all agent() calls are byte-identical to the pre-port baseline (Gate 51).",
  whenToUse:
    "When the user wants a deep, multi-source, fact-checked research report on any topic. BEFORE invoking, check if the question is specific enough to research directly — if underspecified (e.g., 'what car to buy' without budget/use-case/region), ask 2-3 clarifying questions to narrow scope. Then pass the refined question as args, weaving the answers in.",
  phases: [
    { title: "Scope", detail: "Decompose question (from args) into 5 search angles" },
    { title: "Search", detail: "5 parallel WebSearch agents, one per angle" },
    { title: "Fetch", detail: "URL-dedup, fetch top 15 sources, extract falsifiable claims" },
    {
      title: "Verify",
      detail: "Adversarial per-claim verification (vote count per sourceQuality)",
    },
    { title: "Synthesize", detail: "Merge semantic dupes, rank by confidence, cite sources" },
  ],
};

// ─── Substrate adapter (Phase 2 of docs/plans/2026-06-03-adaptive-run-classifier/plan.md) ───
//
// INVARIANT (Gate 51): when runCfg.enabled === false, adapterOpts() returns {}
// (empty object) on every call, so every agent() invocation's effective behaviour
// is identical to the pre-port runtime-generated baseline.
//
// Tier → Claude model mapping (verified 2026-05-31, [verify-at-use] before Phase 6):
//   fast     → claude-haiku-4-5-20251001   (no extended thinking — RM6)
//   balanced → claude-sonnet-4-6           (adaptive thinking available)
//   top      → claude-opus-4-7             (escalate sparingly)
//
// cache_control: {type:"ephemeral", ttl:"1h"} ONLY on verify phases. The 36-min
// baseline run vastly exceeds the 5-min default TTL; eat the 2× write penalty once
// to keep the verify system block warm for the full run (gap-delta C1, A6).
// The classifier prompt is ~800 tokens — below Haiku 4.5's 4,096-token cache
// minimum — so NO cache_control is applied there (pure write penalty, RM1).

const TIER_MODEL = {
  fast: "claude-haiku-4-5-20251001",
  balanced: "claude-sonnet-4-6",
  top: "claude-opus-4-7",
};

// Tiers that support extended/adaptive thinking (Haiku 4.5 does not — RM6).
const THINKING_TIERS = new Set(["balanced", "top"]);

// Phases that get the 1-hour cache_control on their system block.
const LONG_TTL_PHASES = new Set(["verify_default", "verify_judgment"]);

function adapterOpts(phaseName, runCfg) {
  // Gate 51 invariant: disabled → empty opts, byte-identical to baseline.
  if (!runCfg || !runCfg.enabled) return {};

  const tierLabel = (runCfg.tiers && runCfg.tiers[phaseName]) || "balanced";
  const reasoningLabel = (runCfg.reasoning && runCfg.reasoning[phaseName]) || "medium";
  const model = TIER_MODEL[tierLabel] || TIER_MODEL["balanced"];

  const opts = { model };

  // Thinking: emit ONLY for tiers that support it (RM6).
  if (THINKING_TIERS.has(tierLabel) && reasoningLabel !== "low") {
    opts.thinking = { type: "adaptive" };
  }

  // cache_control: 1-hour TTL only for long-running verify phases (gap-delta C1).
  if (LONG_TTL_PHASES.has(phaseName)) {
    opts.cache_control = { type: "ephemeral", ttl: "1h" };
  }

  return opts;
}

// ─── Schemas (unchanged from baseline) ───────────────────────────────────────
const CLASSIFIER_SCHEMA = {
  type: "object",
  required: ["task_class", "rationale", "schema_version"],
  properties: {
    task_class: {
      type: "string",
      enum: ["research_loop_vendor_docs", "research_loop_contested", "research_loop_general"],
    },
    rationale: { type: "string" },
    schema_version: { type: "string" },
    tiers: { type: "object", additionalProperties: { type: "string" } },
    reasoning: { type: "object", additionalProperties: { type: "string" } },
    knobs: { type: "object" },
    verify_policy: { type: "object", additionalProperties: { type: "integer" } },
    use_specialized_mcp: { type: "boolean" },
    primary_source_host: { type: "string" },
    batch_verify: { type: "boolean" },
  },
};

// Baseline knobs matching the pre-port hardcoded constants (Gate 51 floor).
const BASELINE_KNOBS = {
  votes_per_claim: 3,
  refutations_required: 2,
  max_fetch: 15,
  max_verify_claims: 25,
  angle_count: 5,
};

const BASELINE_VERIFY_POLICY = {
  primary: 3,
  secondary: 3,
  blog: 3,
  forum: 3,
  unreliable: 3,
};

const SCOPE_SCHEMA = {
  type: "object",
  required: ["question", "angles", "summary"],
  properties: {
    question: { type: "string" },
    summary: { type: "string" },
    angles: {
      type: "array",
      minItems: 3,
      maxItems: 6,
      items: {
        type: "object",
        required: ["label", "query"],
        properties: {
          label: { type: "string" },
          query: { type: "string" },
          rationale: { type: "string" },
        },
      },
    },
  },
};
const SEARCH_SCHEMA = {
  type: "object",
  required: ["results"],
  properties: {
    results: {
      type: "array",
      maxItems: 6,
      items: {
        type: "object",
        required: ["url", "title", "relevance"],
        properties: {
          url: { type: "string" },
          title: { type: "string" },
          snippet: { type: "string" },
          relevance: { enum: ["high", "medium", "low"] },
        },
      },
    },
  },
};
const EXTRACT_SCHEMA = {
  type: "object",
  required: ["claims", "sourceQuality"],
  properties: {
    sourceQuality: { enum: ["primary", "secondary", "blog", "forum", "unreliable"] },
    publishDate: { type: "string" },
    claims: {
      type: "array",
      maxItems: 5,
      items: {
        type: "object",
        required: ["claim", "quote", "importance"],
        properties: {
          claim: { type: "string" },
          quote: { type: "string" },
          importance: { enum: ["central", "supporting", "tangential"] },
        },
      },
    },
  },
};
const VERDICT_SCHEMA = {
  type: "object",
  required: ["refuted", "evidence", "confidence"],
  properties: {
    refuted: { type: "boolean" },
    evidence: { type: "string" },
    confidence: { enum: ["high", "medium", "low"] },
    counterSource: { type: "string" },
  },
};
const REPORT_SCHEMA = {
  type: "object",
  required: ["summary", "findings", "caveats"],
  properties: {
    summary: { type: "string" },
    findings: {
      type: "array",
      items: {
        type: "object",
        required: ["claim", "confidence", "sources", "evidence"],
        properties: {
          claim: { type: "string" },
          confidence: { enum: ["high", "medium", "low"] },
          sources: { type: "array", items: { type: "string" } },
          evidence: { type: "string" },
          vote: { type: "string" },
        },
      },
    },
    caveats: { type: "string" },
    openQuestions: { type: "array", items: { type: "string" } },
  },
};

// ─── Preamble: resolve run config (async, frozen into closure) ────────────────
//
// Step 1: attempt to read .ravenclaude/run-config.json via agent() Read tool.
// Step 2: if enabled:true and task_class missing, call the classifier (one Haiku
//         Messages-API-shaped call via agent() with forced schema:).
// Step 3: snapshot result — all subsequent code uses the frozen `runCfg`.
// NO cache_control on classifier (~800 tokens < Haiku 4.5's 4,096-token minimum).

const RC_PATH = ".ravenclaude/run-config.json";
const RC_READ_SCHEMA = {
  type: "object",
  properties: {
    found: { type: "boolean" },
    enabled: { type: "boolean" },
    content: { type: "object" },
  },
  required: ["found"],
};

const rcRead = await agent(
  "Use the Read tool to read the file at path `" +
    RC_PATH +
    "`. " +
    "If the file exists and is valid JSON, set found:true and return the parsed object as content. " +
    "If absent, unreadable, or invalid JSON, set found:false. Do not error.",
  { label: "rc-read", schema: RC_READ_SCHEMA },
);

let runCfg;
if (!rcRead || !rcRead.found || !rcRead.content || rcRead.content.enabled !== true) {
  // Absent, unreadable, or explicitly disabled — Gate 51 baseline.
  runCfg = {
    enabled: false,
    schema_version: "1",
    knobs: BASELINE_KNOBS,
    verify_policy: BASELINE_VERIFY_POLICY,
    use_specialized_mcp: false,
    batch_verify: false,
    rationale: "baseline (enabled:false)",
  };
} else {
  const raw = rcRead.content;
  // If task_class already set, accept as-is. Otherwise run classifier.
  if (raw.task_class) {
    runCfg = {
      ...raw,
      knobs: raw.knobs || BASELINE_KNOBS,
      verify_policy: raw.verify_policy || BASELINE_VERIFY_POLICY,
    };
  } else {
    // Classifier: one Haiku call, forced tool_choice via schema: parameter.
    // Layout: stable system (classify instruction) above breakpoint; volatile
    // question below. No cache_control — prompt is ~800 tokens, below Haiku 4.5
    // minimum of 4,096 (RM1).
    const QUESTION_PRELIM = (typeof args === "string" && args.trim()) || "";
    const classified = await agent(
      "## Run classifier\n\n" +
        "You are a one-shot classifier for the rc-deep-research workflow. Classify the research question below into one of three task classes:\n\n" +
        "- `research_loop_vendor_docs` — the answer primarily lives in official vendor documentation (e.g. Microsoft Learn, Anthropic docs, AWS docs). Most sources will be primary vendor pages.\n" +
        '- `research_loop_contested` — the question has credible expert disagreement (comparisons, tradeoffs, "X vs Y", policy debates, empirical benchmarks where vendors disagree).\n' +
        "- `research_loop_general` — open-web question: academic, news, practitioner opinion, or multi-domain without a single authoritative vendor source.\n\n" +
        "## Research question\n" +
        QUESTION_PRELIM +
        "\n\n" +
        'Return the task_class, a one-sentence rationale, and schema_version:"1". Structured output only.',
      {
        label: "run-classifier",
        schema: CLASSIFIER_SCHEMA,
        // model pinned to fast tier for this one-shot call (not via adapterOpts —
        // this is a classifier bootstrap call, not a workflow phase).
        model: TIER_MODEL["fast"],
      },
    );

    const taskClass = classified ? classified.task_class : "research_loop_general";
    const rationale = classified
      ? classified.rationale
      : "classifier returned null; defaulting to general";

    // Merge classifier output with raw config; derive tier/knob defaults by task_class.
    const isMicrosoftDocs = taskClass === "research_loop_vendor_docs";
    runCfg = {
      enabled: true,
      schema_version: "1",
      task_class: taskClass,
      rationale,
      tiers: raw.tiers || {
        scope: "balanced",
        search: "fast",
        fetch: "fast",
        verify_default: "fast",
        verify_judgment: "balanced",
        synthesize: "balanced",
      },
      reasoning: raw.reasoning || {
        scope: "medium",
        search: "low",
        fetch: "low",
        verify_default: "low",
        verify_judgment: "high",
        synthesize: "high",
      },
      knobs: raw.knobs || BASELINE_KNOBS,
      verify_policy: raw.verify_policy || BASELINE_VERIFY_POLICY,
      use_specialized_mcp: isMicrosoftDocs,
      primary_source_host: isMicrosoftDocs ? "learn.microsoft.com" : null,
      batch_verify: raw.batch_verify || false,
    };

    // Emit classifier audit (fire-and-forget; no-op on failure).
    try {
      const tsSecs = Math.floor(budget.spent ? budget.spent() : 0);
      await agent(
        "Write the following JSON to `.ravenclaude/runs/run-classifier/run-" +
          tsSecs +
          ".json` using the Write tool. " +
          "Create parent directories if needed. Content:\n\n" +
          JSON.stringify(
            { task_class: taskClass, rationale, tiers: runCfg.tiers, reasoning: runCfg.reasoning },
            null,
            2,
          ),
        { label: "rc-audit-emit" },
      );
    } catch {}
  }
}

// runCfg is now frozen for the rest of the run (Panel-A R1, gap-delta C9).
log(
  "run-config: enabled=" +
    runCfg.enabled +
    " task_class=" +
    (runCfg.task_class || "n/a") +
    " rationale=" +
    (runCfg.rationale || "").slice(0, 80),
);

// Derive effective constants from runCfg (or baseline floor).
const VOTES_PER_CLAIM = runCfg.knobs.votes_per_claim;
const REFUTATIONS_REQUIRED = runCfg.knobs.refutations_required;
const MAX_FETCH = runCfg.knobs.max_fetch;
const MAX_VERIFY_CLAIMS = runCfg.knobs.max_verify_claims;

// ─── Phase 0: Scope ───────────────────────────────────────────────────────────
phase("Scope");
const QUESTION = (typeof args === "string" && args.trim()) || "";
if (!QUESTION) {
  return {
    error:
      "No research question provided. Pass it as args: Workflow({name: 'rc-deep-research', args: '<question>'}).",
  };
}

// MCP-first instruction prefix (use_specialized_mcp flag).
const MCP_FETCH_PREFIX =
  runCfg.use_specialized_mcp && runCfg.primary_source_host === "learn.microsoft.com"
    ? "PREFER the `microsoft_docs_search` and `microsoft_docs_fetch` MCP tools over WebFetch for learn.microsoft.com URLs. Use WebFetch only as a fallback when the MCP returns no result.\n\n"
    : "";

const scope = await agent(
  "Decompose this research question into complementary search angles.\n\n" +
    "## Question\n" +
    QUESTION +
    "\n\n" +
    "## Task\n" +
    "Generate 5 distinct web search queries that together cover the question from different angles. Pick angles that suit the question's domain. Examples:\n" +
    "- broad/primary  · academic/technical  · recent news  · contrarian/skeptical  · practitioner/implementation\n" +
    "- For medical: anatomy · common causes · serious differentials · authoritative refs · red flags\n" +
    "- For tech: state-of-art · benchmarks · limitations · industry adoption · cost/tradeoffs\n\n" +
    "Make queries specific enough to surface high-signal results. Avoid redundancy.\n" +
    "Return: the question (verbatim or lightly normalized), a 1-2 sentence decomposition strategy, and the angles.\n\nStructured output only.",
  { label: "scope", schema: SCOPE_SCHEMA, ...adapterOpts("scope", runCfg) },
);
if (!scope) {
  return { error: "Scope agent returned no result — cannot decompose the research question." };
}
log("Q: " + QUESTION.slice(0, 80) + (QUESTION.length > 80 ? "…" : ""));
log(
  "Decomposed into " +
    scope.angles.length +
    " angles: " +
    scope.angles.map((a) => a.label).join(", "),
);

// ─── Dedup state ──────────────────────────────────────────────────────────────
const normURL = (u) => {
  try {
    const p = new URL(u);
    return (p.hostname.replace(/^www\./, "") + p.pathname.replace(/\/$/, "")).toLowerCase();
  } catch {
    return u.toLowerCase();
  }
};
const seen = new Map();
const dupes = [];
const budgetDropped = [];
const relRank = { high: 0, medium: 1, low: 2 };
let fetchSlots = MAX_FETCH;

// ─── Prompts ──────────────────────────────────────────────────────────────────
const SEARCH_PROMPT = (angle) =>
  "## Web Searcher: " +
  angle.label +
  "\n\n" +
  'Research question: "' +
  QUESTION +
  '"\n\n' +
  "Your angle: **" +
  angle.label +
  "** — " +
  (angle.rationale || "") +
  "\n" +
  "Search query: `" +
  angle.query +
  "`\n\n" +
  "## Task\nUse WebSearch with the query above (or a refined version). Return the top 4-6 most relevant results.\n" +
  "Rank by relevance to the ORIGINAL question, not just the search query. Skip obvious SEO spam/content farms.\n" +
  "Include a short snippet capturing why each result is relevant.\n\nStructured output only.";

const FETCH_PROMPT = (source, angle) =>
  MCP_FETCH_PREFIX +
  "## Source Extractor\n\n" +
  'Research question: "' +
  QUESTION +
  '"\n\n' +
  "Fetch and extract key claims from this source:\n" +
  "**URL:** " +
  source.url +
  "\n**Title:** " +
  source.title +
  "\n**Found via:** " +
  angle +
  " search\n\n" +
  "## Task\n1. Use WebFetch to retrieve the page content.\n" +
  "2. Assess source quality: primary research/institution? secondary reporting? blog/opinion? forum? unreliable?\n" +
  "3. Extract 2-5 FALSIFIABLE claims that bear on the research question. Each claim must:\n" +
  "   - be a concrete, checkable statement (not vague generalities)\n" +
  "   - include a direct quote from the source as support\n" +
  "   - be rated central/supporting/tangential to the research question\n" +
  "4. Note publish date if available.\n\n" +
  'If the fetch fails or the page is irrelevant/paywalled, return claims: [] and sourceQuality: "unreliable".\n\nStructured output only.';

const VERIFY_PROMPT = (claim, v, voteMax) =>
  "## Adversarial Claim Verifier (voter " +
  (v + 1) +
  "/" +
  voteMax +
  ")\n\n" +
  "Be SKEPTICAL. Try to REFUTE this claim. ≥" +
  REFUTATIONS_REQUIRED +
  "/" +
  voteMax +
  " refutations kill it.\n\n" +
  "## Research question\n" +
  QUESTION +
  "\n\n" +
  '## Claim under review\n"' +
  claim.claim +
  '"\n\n' +
  "**Source:** " +
  claim.sourceUrl +
  " (" +
  claim.sourceQuality +
  ")\n" +
  '**Supporting quote:** "' +
  claim.quote +
  '"\n\n' +
  "## Checklist\n" +
  "1. Is the claim actually supported by the quote, or is it an overreach/misread?\n" +
  "2. WebSearch for contradicting evidence — does any credible source dispute or heavily qualify this?\n" +
  "3. Is the source quality sufficient for the claim's strength? (extraordinary claims need primary sources)\n" +
  "4. Is the claim outdated? (check dates — old claims about fast-moving fields are suspect)\n" +
  "5. Is this a marketing claim / press release / cherry-picked benchmark / forum speculation?\n\n" +
  "**refuted=true** if: unsupported by quote / contradicted / low-quality source for strong claim / outdated / marketing fluff.\n" +
  "**refuted=false** ONLY if: claim is well-supported, current, and source quality matches claim strength.\n" +
  "Default to refuted=true if uncertain.\n\nStructured output only. Evidence MUST be specific.";

// ─── Per-claim vote resolver (gap-delta C4 / A4) ──────────────────────────────
//
// Primary: upfront lookup via verify_policy[sourceQuality] (deterministic).
// Optional escalation: if any vote returns confidence:low, fire one additional
// vote at verify_judgment tier.

function resolveVerifyVotes(claim, cfg) {
  const policy = cfg.verify_policy || BASELINE_VERIFY_POLICY;
  return policy[claim.sourceQuality] || VOTES_PER_CLAIM;
}

// ─── Pipeline: search → dedup → fetch+extract ────────────────────────────────
const searchResults = await pipeline(
  scope.angles,

  (angle) =>
    agent(SEARCH_PROMPT(angle), {
      label: "search:" + angle.label,
      phase: "Search",
      schema: SEARCH_SCHEMA,
      ...adapterOpts("search", runCfg),
    }).then((r) => {
      if (!r) return null;
      log(angle.label + ": " + r.results.length + " results");
      return { angle: angle.label, results: r.results };
    }),

  (searchResult) => {
    const sorted = [...searchResult.results].sort(
      (a, b) => relRank[a.relevance] - relRank[b.relevance],
    );
    const novel = sorted.filter((r) => {
      const key = normURL(r.url);
      if (seen.has(key)) {
        dupes.push({ ...r, angle: searchResult.angle, dupOf: seen.get(key) });
        return false;
      }
      if (fetchSlots <= 0 && relRank[r.relevance] >= 1) {
        budgetDropped.push({ ...r, angle: searchResult.angle });
        return false;
      }
      seen.set(key, { angle: searchResult.angle, title: r.title });
      fetchSlots--;
      return true;
    });
    if (novel.length < searchResult.results.length) {
      log(
        searchResult.angle +
          ": " +
          novel.length +
          " novel (" +
          (searchResult.results.length - novel.length) +
          " filtered)",
      );
    }
    return parallel(
      novel.map((source) => () => {
        let host = "unknown";
        try {
          host = new URL(source.url).hostname.replace(/^www\./, "");
        } catch {}
        return agent(FETCH_PROMPT(source, searchResult.angle), {
          label: "fetch:" + host,
          phase: "Fetch",
          schema: EXTRACT_SCHEMA,
          ...adapterOpts("fetch", runCfg),
        })
          .then((ext) => {
            if (!ext) return null;
            return {
              url: source.url,
              title: source.title,
              angle: searchResult.angle,
              sourceQuality: ext.sourceQuality,
              publishDate: ext.publishDate,
              claims: ext.claims.map((c) => ({
                ...c,
                sourceUrl: source.url,
                sourceQuality: ext.sourceQuality,
              })),
            };
          })
          .catch((e) => {
            log("fetch failed: " + source.url + " — " + (e.message || e));
            return {
              url: source.url,
              title: source.title,
              angle: searchResult.angle,
              sourceQuality: "unreliable",
              claims: [],
            };
          });
      }),
    );
  },
);

const allSources = searchResults.flat().filter(Boolean);
const allClaims = allSources.flatMap((s) => s.claims);
const impRank = { central: 0, supporting: 1, tangential: 2 };
const qualRank = { primary: 0, secondary: 1, blog: 2, forum: 3, unreliable: 4 };

const rankedClaims = [...allClaims]
  .sort(
    (a, b) =>
      impRank[a.importance] - impRank[b.importance] ||
      qualRank[a.sourceQuality] - qualRank[b.sourceQuality],
  )
  .slice(0, MAX_VERIFY_CLAIMS);

log(
  "Fetched " +
    allSources.length +
    " sources → " +
    allClaims.length +
    " claims → verifying top " +
    rankedClaims.length,
);

if (rankedClaims.length === 0) {
  return {
    question: QUESTION,
    summary:
      "No claims extracted. " +
      allSources.length +
      " sources fetched, all empty/failed. " +
      dupes.length +
      " URL dupes, " +
      budgetDropped.length +
      " budget-dropped.",
    findings: [],
    refuted: [],
    sources: allSources.map((s) => ({ url: s.url, quality: s.sourceQuality })),
    stats: {
      angles: scope.angles.length,
      sources: allSources.length,
      claims: 0,
      dupes: dupes.length,
    },
    run_config: {
      enabled: runCfg.enabled,
      task_class: runCfg.task_class,
      rationale: runCfg.rationale,
    },
  };
}

// ─── Verify: per-claim adversarial (policy-driven vote count + optional escalation) ─
// cache_control {ttl:"1h"} applied via adapterOpts for verify_default and verify_judgment
// (gap-delta C1 / A6 — 36-min run exceeds 5-min default TTL).
phase("Verify");

// Batch gate (gap-delta C2 / A5): present in schema, default false in MVP.
const USE_BATCH = runCfg.batch_verify && rankedClaims.length >= 10;
if (USE_BATCH) log("batch_verify: enabled for " + rankedClaims.length + " claims");

const claimTierAudit = [];

const voted = (
  await parallel(
    rankedClaims.map((claim, claimIdx) => () => {
      const voteCount = resolveVerifyVotes(claim, runCfg);
      const verifyPhaseName = "verify_default";
      return parallel(
        Array.from(
          { length: voteCount },
          (_, v) => () =>
            agent(VERIFY_PROMPT(claim, v, voteCount), {
              label: "v" + v + ":" + claim.claim.slice(0, 40),
              phase: "Verify",
              schema: VERDICT_SCHEMA,
              ...adapterOpts(verifyPhaseName, runCfg),
            }),
        ),
      ).then(async (verdicts) => {
        const valid = verdicts.filter(Boolean);
        const refutedCount = valid.filter((v) => v.refuted).length;
        const abstained = voteCount - valid.length;
        let survives = valid.length >= REFUTATIONS_REQUIRED && refutedCount < REFUTATIONS_REQUIRED;

        // Optional escalation: if any voter returned confidence:low, fire one
        // additional vote at verify_judgment tier (gap-delta C4 / A4).
        let escalated = false;
        if (survives && valid.some((v) => v.confidence === "low")) {
          const extra = await agent(VERIFY_PROMPT(claim, voteCount, voteCount + 1), {
            label: "v_esc:" + claim.claim.slice(0, 40),
            phase: "Verify",
            schema: VERDICT_SCHEMA,
            ...adapterOpts("verify_judgment", runCfg),
          });
          if (extra) {
            valid.push(extra);
            if (extra.refuted) {
              const newRefuted = valid.filter((v) => v.refuted).length;
              survives = newRefuted < REFUTATIONS_REQUIRED;
            }
            escalated = true;
          }
        }

        const voteStr =
          valid.length -
          valid.filter((v) => v.refuted).length +
          "-" +
          valid.filter((v) => v.refuted).length;
        log(
          '"' +
            claim.claim.slice(0, 50) +
            '…": ' +
            voteStr +
            (abstained > 0 ? " (" + abstained + " abstain)" : "") +
            (escalated ? " [escalated]" : "") +
            " " +
            (survives ? "✓" : "✗"),
        );

        // Per-claim audit row (gap-delta C4 / RM4).
        claimTierAudit.push({
          claim_idx: claimIdx,
          initial_tier: (runCfg.tiers && runCfg.tiers["verify_default"]) || "fast",
          votes_fired: valid.length,
          escalated_to: escalated
            ? (runCfg.tiers && runCfg.tiers["verify_judgment"]) || "balanced"
            : null,
          final_verdict: survives ? "survive" : "killed",
        });

        return {
          ...claim,
          verdicts: valid,
          refutedVotes: valid.filter((v) => v.refuted).length,
          survives,
        };
      });
    }),
  )
).filter(Boolean);

// Emit claim tier audit (fire-and-forget via agent write, no-op on error).
if (runCfg.enabled && claimTierAudit.length > 0) {
  try {
    const runId = "run-" + Math.floor(budget.spent ? budget.spent() : 0);
    await agent(
      "Write the following JSONL content (one JSON object per line) to `.ravenclaude/runs/" +
        runId +
        "/claim_tier_audit.jsonl` using the Write tool. Create parent directories if needed. Content:\n\n" +
        claimTierAudit.map((r) => JSON.stringify(r)).join("\n"),
      { label: "claim-audit-emit" },
    );
  } catch {}
}

const confirmed = voted.filter((c) => c.survives);
const killed = voted.filter((c) => !c.survives);
log(
  "Verify done: " +
    voted.length +
    " claims → " +
    confirmed.length +
    " confirmed, " +
    killed.length +
    " killed",
);

if (confirmed.length === 0) {
  return {
    question: QUESTION,
    summary:
      "All " +
      voted.length +
      " claims refuted by adversarial verification. Research inconclusive — sources may be low-quality or claims overstated.",
    findings: [],
    refuted: killed.map((c) => ({
      claim: c.claim,
      vote: c.verdicts.length - c.refutedVotes + "-" + c.refutedVotes,
      source: c.sourceUrl,
    })),
    sources: allSources.map((s) => ({
      url: s.url,
      quality: s.sourceQuality,
      claimCount: s.claims.length,
    })),
    stats: {
      angles: scope.angles.length,
      sources: allSources.length,
      claims: allClaims.length,
      verified: voted.length,
      confirmed: 0,
      killed: killed.length,
    },
    run_config: {
      enabled: runCfg.enabled,
      task_class: runCfg.task_class,
      rationale: runCfg.rationale,
    },
  };
}

// ─── Synthesize ───────────────────────────────────────────────────────────────
phase("Synthesize");
const confRank = { high: 0, medium: 1, low: 2 };
const block = confirmed
  .map((c, i) => {
    const best = c.verdicts
      .filter((v) => !v.refuted)
      .sort((a, b) => confRank[a.confidence] - confRank[b.confidence])[0];
    return (
      "### [" +
      i +
      "] " +
      c.claim +
      "\n" +
      "Vote: " +
      (c.verdicts.length - c.refutedVotes) +
      "-" +
      c.refutedVotes +
      " · Source: " +
      c.sourceUrl +
      " (" +
      c.sourceQuality +
      ")\n" +
      'Quote: "' +
      c.quote +
      '"\nVerifier evidence (' +
      best.confidence +
      "): " +
      best.evidence +
      "\n"
    );
  })
  .join("\n");

const killedBlock =
  killed.length > 0
    ? "\n## Refuted claims (for transparency)\n" +
      killed
        .map(
          (c) =>
            '- "' +
            c.claim +
            '" (' +
            c.sourceUrl +
            ", vote " +
            (c.verdicts.length - c.refutedVotes) +
            "-" +
            c.refutedVotes +
            ")",
        )
        .join("\n")
    : "";

const report = await agent(
  "## Synthesis: research report\n\n" +
    "**Question:** " +
    QUESTION +
    "\n\n" +
    confirmed.length +
    " claims survived " +
    VOTES_PER_CLAIM +
    "-vote adversarial verification. Merge semantic duplicates and synthesize.\n\n" +
    "## Confirmed claims\n" +
    block +
    "\n" +
    killedBlock +
    "\n\n" +
    "## Instructions\n" +
    "1. Identify claims that say the same thing — merge them, combine their sources.\n" +
    "2. Group related claims into coherent findings. Each finding should directly address the research question.\n" +
    "3. Assign confidence per finding: high (multiple primary sources, unanimous votes), medium (secondary sources or split votes), low (single source or blog-quality).\n" +
    "4. Write a 3-5 sentence executive summary answering the research question.\n" +
    "5. Note caveats: what's uncertain, what sources were weak, what time-sensitivity applies.\n" +
    "6. List 2-4 open questions that emerged but weren't answered.\n\nStructured output only.",
  { label: "synthesize", schema: REPORT_SCHEMA, ...adapterOpts("synthesize", runCfg) },
);

if (!report) {
  return {
    question: QUESTION,
    summary:
      "Synthesis step was skipped or failed — returning " +
      confirmed.length +
      " verified claims unmerged.",
    findings: [],
    confirmed: confirmed.map((c) => ({
      claim: c.claim,
      source: c.sourceUrl,
      quote: c.quote,
      vote: c.verdicts.length - c.refutedVotes + "-" + c.refutedVotes,
    })),
    refuted: killed.map((c) => ({
      claim: c.claim,
      vote: c.verdicts.length - c.refutedVotes + "-" + c.refutedVotes,
      source: c.sourceUrl,
    })),
    sources: allSources.map((s) => ({
      url: s.url,
      quality: s.sourceQuality,
      claimCount: s.claims.length,
    })),
    stats: {
      angles: scope.angles.length,
      sources: allSources.length,
      claims: allClaims.length,
      verified: voted.length,
      confirmed: confirmed.length,
      killed: killed.length,
      afterSynthesis: 0,
    },
    run_config: {
      enabled: runCfg.enabled,
      task_class: runCfg.task_class,
      rationale: runCfg.rationale,
    },
  };
}

return {
  question: QUESTION,
  ...report,
  refuted: killed.map((c) => ({
    claim: c.claim,
    vote: c.verdicts.length - c.refutedVotes + "-" + c.refutedVotes,
    source: c.sourceUrl,
  })),
  sources: allSources.map((s) => ({
    url: s.url,
    quality: s.sourceQuality,
    angle: s.angle,
    claimCount: s.claims.length,
  })),
  stats: {
    angles: scope.angles.length,
    sourcesFetched: allSources.length,
    claimsExtracted: allClaims.length,
    claimsVerified: voted.length,
    confirmed: confirmed.length,
    killed: killed.length,
    afterSynthesis: report.findings.length,
    urlDupes: dupes.length,
    budgetDropped: budgetDropped.length,
    agentCalls: 1 + scope.angles.length + allSources.length + voted.length * VOTES_PER_CLAIM + 1,
  },
  run_config: {
    enabled: runCfg.enabled,
    task_class: runCfg.task_class,
    rationale: runCfg.rationale,
    tiers: runCfg.tiers,
    use_specialized_mcp: runCfg.use_specialized_mcp,
    batch_verify: runCfg.batch_verify,
  },
};
