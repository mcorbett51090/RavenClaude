# Claude app architecture spec — <APP>

> Owned by `claude-solution-architect`. See `knowledge/claude-build-surface-decision-tree.md`.

## Decision
- **Build surface:** <Workbench | Messages API | Agent SDK | Managed Agents> — why (from the tree):
- **Model(s):** <routing ladder — e.g. Haiku triage → Sonnet 4.6 → Opus 4.7 tail> — why:
- **Deployment target:** <Claude API | Bedrock | Vertex | Foundry> — why (caching/residency/quota/cost):
- **Migration path:** <prototype → production, no rewrite>

## Components
| Layer | Owner agent | Notes |
|---|---|---|
| Prompts / caching / context / tools | prompt-and-context-engineer | breakpoint layout; structured output |
| MCP / hosted server tools | mcp-and-server-tools-engineer | which servers/tools |
| Agent loop (if agentic) | agent-sdk-engineer | subagents/hooks/skills/sessions |
| Evals | eval-engineer | golden set + metric |
| Ops (cost/reliability/observability) | claude-app-ops-engineer | hit rate, backoff, logging |
| Non-Claude app code / UI / data | core / web-design / data-platform / microsoft-fabric | seams |

## Cross-cutting
- **Security:** → `ravenclaude-core/security-reviewer` (injection, secrets, sandboxing)
- **Cost target:** <cost-per-resolved-task budget>
- **Quality gate:** <eval pass-rate threshold in CI>

## Open questions / decisions
- <decision + owner>
