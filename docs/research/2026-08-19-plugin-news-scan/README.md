# Plugin-news scan — 2026-08-19 (scheduled routine)

A scheduled routine researched recent developments per active plugin, ran the findings through two
expert panels (usefulness, then detailed review), and shipped the verified subset. This doc is the
**curated backlog** of findings that were **deemed useful but deferred** — every one rests on WebSearch
synthesis because the session's egress proxy blocked its primary source, so under the repo's
Claim-Grounding protocol none may enter shipped knowledge until re-verified against a fetchable primary.

Landed 2026-08-28 via the #987 recut (v0.307.0), not the original draft commit (that commit
rewound `plugin.json` to 0.283.0).

## Shipped this run (verified against code.claude.com/docs/en/changelog)

See `plugins/ravenclaude-core/CLAUDE.md` v0.307.0 milestone. Four Claude Code platform-fact
corrections (stale subagent nesting depth; native concurrency cap; `/reload-plugins` now often optional;
new `archive`/`command` marketplace sources). Re-checked against the changelog through 2.1.250
(2026-08-28); none reversed.

## Deferred — needs a source-verified follow-up (egress had these blocked this session)

| # | Plugin | Finding | Primary source (unfetched) | Priority |
|---|---|---|---|---|
| 1 | microsoft-fabric | **Fabric Data Agents' OpenAI Assistants API retires 2026-08-26** — migrate query→MCP endpoint, SDK→Responses API | learn.microsoft.com/fabric/data-science/data-agent-mcp-server | **P0 deadline PASSED 2026-08-26** — re-verify current status before quoting |
| 2 | tax-preparation-practice | **OBBBA made §199A QBI permanent** + new 2025–2028 deductions (tips/overtime/senior/car-loan); plugin's lever assumes QBI sunset | irs.gov OBBBA TY2026 adjustments | **P0 (wrong-output risk)** |
| 3 | ai-red-teaming | **OWASP GenAI LLM Top 10 2026 (2026-08-04)** renumbered codes the file hard-codes (Excessive Agency LLM06→LLM03; System-Prompt Leakage→Hidden Context Exposure LLM08) | github.com/GenAI-Security-Project/GenAI-LLM-Top10 / genai.owasp.org | **P0 (wrong identifiers in deliverables)** |
| 4 | microsoft-fabric | Fabric Runtime 2.0 now **GA** (Aug 2026), default late Sept; doc says "public preview" | learn.microsoft.com/fabric/data-engineering/runtime-2-0 | P1 |
| 5 | esg-sustainability-reporting | **CA SB 253/261** climate disclosure regime (CARB 2026 dates) absent; live US mandate | ww2.arb.ca.gov | P1 |
| 6 | microsoft-365-copilot | Declarative agent manifest **v1.8** (Jul 2026) supersedes pinned v1.7; adds EmailActions/MeetingActions | learn.microsoft.com/microsoft-365/copilot/extensibility/declarative-agent-manifest-1.8 | P2 |
| 7 | finops-cloud-cost | **FOCUS 1.4** (Jun 2026) billing spec entirely absent from the plugin | finops.org/insights/introducing-focus-1-4/ | P2 |
| 8 | ai-agent-engineering | **MCP 2026-07-28** stateless spec not mentioned (ravenclaude-core already documents it) | blog.modelcontextprotocol.io/posts/2026-07-28/ | P2 |
| 9 | ai-agent-engineering | **A2A protocol v1.0** (Mar 2026, LF) absent | github.com/a2aproject/A2A | P3 |
| 10 | mobile-engineering | **RN New Architecture is now the only architecture** (legacy removed 0.82); cap-map says "GA-ing" | reactnative.dev/blog/2026/06/11/react-native-0.86 | P2 |
| 11 | shopify-app-engineering | **useBuyerJourneyIntercept deprecated** (API 2026-07); migrate to validation Functions | shopify.dev changelog | P2 |
| 12 | web-design | **CSS Anchor Positioning Baseline 2026**; doc omits it | web-platform-dx/web-features#3558 | P3 |
| 13 | data-governance-privacy | **3 new US state privacy laws** effective 2026-01-01 (IN/KY/RI) | IAPP / state statutes | P2 |
| 14 | trust-and-safety | **EU Digital Omnibus (Reg 2026/1744)** Article 5 ban on generative NCII/CSAM tooling | eur-lex / orrick.com | P2 |

## How to clear the backlog

Run a follow-up with egress to the blocked primaries (or verify each on a machine that can reach them).
For each: fetch the primary source, confirm the exact version/date/penalty/code, then draft the plugin
edit with an inline `[verified <date> against <primary>]` marker. Regulatory items (#2, #5, #13, #14)
are highest-risk-if-wrong — confirm exact figures/dates/citations before quoting to a consumer.

Panel verdicts + full raw findings: `.ravenclaude/runs/plugin-news-2026-08-19/` (local, gitignored).
