# Model selection & 2026 capability map

**Last reviewed:** 2026-05-28 · **Confidence:** medium-high — the Claude platform ships **monthly**, so this is the freshness anchor the Researcher sweep re-dates. Every numeric / GA claim carries a retrieval date; verify before quoting a client.
**Owner:** all agents (the "cite the capability with a retrieval date" discipline, house opinion #14).
**Source:** [release notes](https://platform.claude.com/docs/en/release-notes/overview), [API overview](https://platform.claude.com/docs/en/api/overview), retrieved 2026-05-28.

## Model lineup (2026-05)

| Model | Use for | Notable |
|---|---|---|
| **Opus 4.7** | hardest reasoning, agentic depth | **1M-token context** |
| Opus 4.6 | hardest reasoning (prior) | |
| **Sonnet 4.6** | balanced default for most app work | **1M-token context**; **adaptive thinking** (`thinking:{type:"adaptive"}`); `budget_tokens` **deprecated** on 4.6 |
| **Haiku 4.5** | cheap / fast / high-volume; default eval judge | lowest cost |

**Right-size, don't default to Opus (house opinion #3).** Use a routing ladder: a cheap model (Haiku) triages / classifies, escalate-on-uncertainty to Sonnet, reserve Opus for the genuinely hard tail. Track **cost-per-resolved-task + cache hit rate**, not raw token count ([`claude-app-finops-reliability-and-security.md`](claude-app-finops-reliability-and-security.md)).

## Capability status (dated — verify before quoting)

| Capability | Status (2026-05-28) |
|---|---|
| Messages API, streaming, tool use, vision/PDF | GA |
| **Prompt caching** (5-min + 1-hour TTL; workspace-isolated since Feb 2026) | GA — see [`prompt-caching-playbook.md`](prompt-caching-playbook.md) |
| Structured output via tools | GA |
| **Adaptive thinking** (Sonnet 4.6; `budget_tokens` deprecated on 4.6) | current — verify the exact param name in live docs |
| **1M-token context** (Opus 4.7, Sonnet 4.6) | GA |
| Context editing / compaction | available — verify scope |
| **Batch API** (50% discount, async ~24h) | GA |
| Batch `output-300k-2026-03-24` beta header (max_tokens → 300k on Opus 4.7/4.6 + Sonnet 4.6) | **beta** — keep the header string verified |
| **Files API** | GA — verify retention/limits |
| **Citations** | GA |
| **Computer use** | **GA on claude.ai March 2026**; API tool still requires your sandbox |
| **Code execution tool** | available — verify GA/beta |
| **Memory tool** | **public beta** (Managed Agents: `managed-agents-2026-04-01` header) |
| **Claude Agent SDK** (Python + TS) | GA; separate Agent SDK credit from **2026-06-15** on subscription plans |
| **Managed Agents** (hosted REST) | GA; memory in public beta |
| **MCP** | stable spec; servers over stdio / SSE / Streamable HTTP |

## How to keep this current
On each Researcher sweep: re-run a `platform.claude.com` release-notes + `code.claude.com` changelog check; re-date this file; correct any status that changed; bump the plugin patch version if a *default* changes (e.g., a new flagship model, a GA flip, a pricing-multiplier change). Numeric claims (cache minimums, pricing multipliers, batch limits) live **here**, not baked into the six agent personas — one file refreshes, not six.
