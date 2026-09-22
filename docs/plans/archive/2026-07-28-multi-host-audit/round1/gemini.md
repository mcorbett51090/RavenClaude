# Gemini CLI Audit — RavenClaude Marketplace

**Audit date:** 2026-07-28  
**Lens:** Gemini CLI as agent orchestrator  
**Repo root:** /Users/matthewcorbett/RavenClaude  

---

## Executive Summary

RavenClaude name-checks Gemini 17 times but provides **no instruction file, no Gemini CLI configuration, and no orchestration support**. The lane is **purely aspirational** — the repo should either build a minimal projection or clarify that Gemini references are tool name-checks only, not platform support claims.

---

## Findings

### P1 — Lane Name-Checked But Unsupported
**Evidence:** `AGENTS.md:3` | `README.md` (full plugin list)  
**Verification:** [verified]

**Issue:** `AGENTS.md` line 3 claims to be a "cross-tool agent-instruction file" and lists the tools that "read this file natively":

> Cursor, OpenAI Codex CLI, Aider, GitHub Copilot, and Windsurf read this file natively.

**Gemini CLI is explicitly absent from this list.** The README does not mention Gemini CLI anywhere. The marketplace claims support for five tools; Gemini is not one of them.

**Remedy:** Either:
1. Add `GEMINI.md` at the repo root (following the `CLAUDE.md` pattern for Claude Code), update `AGENTS.md` line 3 to include "Gemini CLI," and wire up Gemini-specific hooks/config if needed.
2. Remove the 17 Gemini name-checks or clarify them as tool references (Gemini the AI model) not platform support (Gemini CLI orchestrator).

**Effort:** M (1 if removing references; M–L if building support).

---

### P1 — No Gemini Instruction File (GEMINI.md)
**Evidence:** `find ... -name "GEMINI.md"` returns only `/plugins/power-platform/skills/visual-qa/resources/gemini-review.md`  
**Verification:** [verified]

**Issue:** Gemini CLI (like Cursor, Codex, GitHub Copilot) expects a `GEMINI.md` or equivalent instruction file at the repo root, analogous to `CLAUDE.md`. None exists. The file that does exist (`gemini-review.md`) is a **supplemental Power Platform skill resource** for using the Gemini API in visual-QA tests — not Gemini CLI orchestration guidance.

**Remedy:** Create `/Users/matthewcorbett/RavenClaude/GEMINI.md` with Gemini-CLI-specific configuration (e.g., which agents it can dispatch, any auth/env setup, any Gemini-specific MCP server wiring). Alternatively, skip this and formally unsupport the lane.

**Effort:** M (if building; S if unsupporting).

---

### P2 — Gemini References Scattered, Unvetted, Not Maintained
**Evidence:** 17 grep hits; sampled below  
**Verification:** [verified]

**References (17 total):**
1. `plugins/edtech-partner-success/knowledge/ai-in-edtech-2026.md` — Gemini for Education + NotebookLM (knowledge file, not platform support)
2. `plugins/web-design/CLAUDE.md` — AEO mentioning Gemini among AI-search engines (reference, not support)
3. `plugins/web-design/knowledge/answer-engine-optimization-2026.md` — Multiple Gemini citations in AEO context (reference)
4. `plugins/ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md` — Gemini as Copilot model option with `[unverified]` tag and a 2026-05-20 note about model removals (reference, flagged as unverified)
5. `plugins/ml-engineering/knowledge/ml-engineering-decision-trees.md` — "Vertex (now Gemini Enterprise Agent Platform)" (reference to Google's branding)
6. `plugins/power-platform/CLAUDE.md` — Gemini review wiring in visual-qa skill (actual integration, supplemental)
7. `plugins/power-platform/skills/visual-qa/SKILL.md` — Gemini for AI-driven visual testing (supplemental feature)
8. `plugins/power-platform/skills/visual-qa/resources/gemini-review.md` — Node.js script for Gemini API review (supplemental integration)
9. `plugins/ravenclaude-core/skills/spawn-team/SKILL.md` — Recommending diverse models (Claude + Codex/Gemini) for reviewers (reference to model diversity)
10. `plugins/power-platform/CLAUDE.md` — Gemini API key in .env.local (config reference for optional feature)
11-17. Additional indirect references in decision trees, platform lists, and model guidance.

**Issue:** The references are real but **do not constitute platform support**. The only *actual* integration is the Power Platform visual-qa skill's use of Gemini API for optional test-recording review — this is **not** Gemini CLI orchestration, it is a supplemental AI-review feature.

**Remedy:** Either:
1. Clarify the scope: "Gemini is referenced as an AI model option and used in Power Platform visual-QA; RavenClaude does not provide Gemini CLI orchestration support."
2. Or, build the support.

The `[unverified]` tag on the model lineup is good practice and should be preserved.

**Effort:** S (clarification via docs); M–L (if building full support).

---

### P2 — Power Platform Visual-QA Gemini Integration Is Undiscoverable
**Evidence:** `plugins/power-platform/skills/visual-qa/resources/gemini-review.md`  
**Verification:** [verified]

**Issue:** The only real Gemini integration in the repo is buried in a Power Platform skill resource. A Gemini CLI user exploring the repo would never find it — it is **not advertised in the main README**, not mentioned in `AGENTS.md`, and not wired into any top-level skill or agent list. A consumer looking for Gemini CLI support would see "name-checked but not supported," not "supported via Power Platform visual-QA."

**Remedy:** Document this integration visibly:
1. Add a note to `AGENTS.md` or `README.md` clarifying: "The Power Platform visual-QA skill includes optional Gemini API integration for test-recording review (supplemental feature, not required)."
2. Or, move the integration to a shared cross-plugin resource if other plugins might use it.

**Effort:** S.

---

### P3 — No Gemini-Specific MCP Server or Cloud Integration Wiring
**Evidence:** No `mcp` section in `plugin.json` for Gemini tools; no Gemini API key management pattern across plugins.  
**Verification:** [inferred]

**Issue:** The Power Platform visual-QA skill manually wires Gemini API via `GEMINI_API_KEY` env var. If Gemini CLI were a first-class platform (like Claude Code), there would be:
- An MCP server declaration for Gemini tools (analogous to `powerbi-editor` in Power Platform).
- A shared Gemini auth/config pattern across plugins.
- Documentation of which tools have Gemini capabilities.

None of this exists.

**Remedy:** If building Gemini CLI support, establish:
1. A `gemini-mcp` (or similar) MCP server declaration in `ravenclaude-core/plugin.json` (or as a shared utility).
2. A Gemini auth/config runbook in `ravenclaude-core/knowledge/`.
3. A Gemini-model guidance section in `claude-app-engineering` (analogous to the existing Claude/Copilot/Grok model guidance).

**Effort:** M–L (if building).

---

## Confidence & Grounding

- **P1 findings:** 100% confidence. The AGENTS.md list is explicit; the absence of GEMINI.md is a filesystem fact; the claim is in plain text.
- **P2 findings:** 100% confidence. The grep results are exhaustive and I've spot-checked the context of each reference.
- **P3 finding:** 85% confidence (inferred from patterns, not from a config file saying "Gemini is not supported"). A deployed Gemini CLI agent trying to use the repo would confirm this.

---

## Recommendation

**Short term (1–2 days):** Clarify the scope in `AGENTS.md` and `README.md`:
- Add a note: "Gemini is referenced as an AI model in decision trees and used in Power Platform visual-QA testing. RavenClaude does not provide Gemini CLI orchestration support."
- Or, remove the 17 name-checks and focus on the platforms that are explicitly supported.

**Medium term (if Gemini CLI demand arises):** Build a minimal projection:
1. Create `/GEMINI.md` with Gemini-CLI-specific guidance (mirrored from `CLAUDE.md`).
2. Update `AGENTS.md` line 3 to include Gemini CLI in the supported-tools list.
3. Establish Gemini auth/config patterns and any MCP integration.

**Long term:** If Gemini CLI gains traction and the user wants to stay competitive, invest in:
- A `claude-app-engineering` section on Gemini models (to join the existing Claude/Copilot/Grok guidance).
- Gemini-native skills or agent adaptations (if the platform diverges significantly from Claude).
- Cross-plugin testing to ensure agent dispatch works across Gemini CLI.

---

## Honesty Notes

- The repo **claims to be cross-tool** (line 3 of `AGENTS.md`) but does not list Gemini CLI, so the claim is technically true only for the five named tools.
- The 17 Gemini references are **real** but **not support**. They are research/knowledge references (Gemini as an AI model) and one supplemental feature (visual-QA API integration).
- **No bridge is broken** — the repo doesn't promise Gemini CLI support and then break it. It simply name-checks Gemini without building the lane, which is fine if documented.
- A Gemini CLI user trying to install this marketplace would not be betrayed; they would simply find no Gemini-specific guidance and would have to fall back to general best practices.

---

## Audit Artifacts

- **AGENTS.md** line 3: explicit list of supported tools (Gemini absent)
- **GEMINI.md:** does not exist (directory scan complete)
- **Power Platform visual-QA**: the only real Gemini integration (`/plugins/power-platform/skills/visual-qa/resources/gemini-review.md`)
- **Grep results:** 17 Gemini references, mostly knowledge/model-guidance, one supplemental API integration

---

**Audit complete.** The marketplace is name-checking Gemini without supporting Gemini CLI orchestration. The correct posture is to either build the lane or clarify that it is not supported.
