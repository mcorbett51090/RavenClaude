# Content scan digest — 2026-06-10 (first run, interactive)

**Produced by:** in-session web search (the interactive mode of [`scripts/content-scan.py`](../../../scripts/content-scan.py)).
**Queries:** `fractional CFO AI` · `agentic AI coding Claude Code workflow best practices 2026`
**Boundary:** LinkedIn rows are **discovery-only** — title + snippet + link surfaced via normal search; **no article body was fetched or scraped** from LinkedIn (no official content API; scraping is ToS-prohibited + litigated — Proxycurl was sued and shut down in 2025). Open-web rows (Medium/Substack/blogs/docs) are freely fetchable for full text.

---

## Topic 1 — Fractional CFO + AI (Closebook-relevant)

| Source | Title / gist | Link |
| --- | --- | --- |
| discovery (LinkedIn) | Carl Seidman, CPA — "in the next year we'll see more **1-person fractional-CFO firms doing $2–3M**" (repeatable finance automations via repositories of skills/plugins/markdown) | [post](https://www.linkedin.com/posts/carlseidman_i-believe-in-the-next-year-well-see-more-activity-7438331456331878400-1Bts) |
| discovery (LinkedIn) | Carl Seidman — why fractional CFOs scale massively as finance/accounting skills become accessible (FP&A tools "in trouble") | [post](https://www.linkedin.com/posts/carlseidman_this-is-a-reason-i-believe-fractional-cfos-activity-7449559214617804800-uNy1) |
| discovery (LinkedIn) | Ben Murray (SaaS CFO) — AI in fractional CFO practice: automating finance & ops | [post](https://www.linkedin.com/posts/benrmurray_saas-activity-7431812194629230592-ZOg1) |
| discovery (LinkedIn) | Frank Tumminello — how fractional CFOs are transforming finance with tech; scaling a practice | [post](https://www.linkedin.com/posts/frank-a-tumminello_fractional-cfo-technology-scale-your-practice-activity-7390051416989388800-FTFI) |
| discovery (LinkedIn) | Robb Thomas — "Fractional CFOs and AI: Navigating the Next Frontier" (Pulse article) | [article](https://www.linkedin.com/pulse/fractional-cfos-ai-navigating-next-frontier-robb-thomas-dpkhe) |
| discovery (LinkedIn) | Nicolas Boucher — "AI for Fractional CFOs? How does it affect…" | [post](https://www.linkedin.com/posts/bouchernicolas_ai-for-fractional-cfos-how-does-it-affect-activity-7253727531470589952-jXUE) |
| discovery (LinkedIn) | Wouter Born — list of affordable CFOTech tools for fractional CFOs (26 comments) | [post](https://www.linkedin.com/posts/wouterborn_heres-a-list-of-affordable-cfotech-tools-activity-7125092799426813952-7z_X) |

**Closebook signal:** the thesis Carl Seidman is pushing (1-person fractional-CFO firms scaling to $2–3M on repeatable, guard-railed finance automations) is *exactly* Closebook's wedge — these authors are both the ICP and the megaphone. Worth following on the open web for full-text (most cross-post to newsletters/Substacks).

## Topic 2 — Agentic AI coding / Claude Code (marketplace-relevant)

| Source | Title / gist | Link |
| --- | --- | --- |
| code.claude.com | **Best practices for Claude Code** (primary — agentic loop: gather context → act → verify) | [docs](https://code.claude.com/docs/en/best-practices) |
| medium.com | DhanushKumar — "Workflows in Agentic AI — Claude Code workflows" (May 2026) | [article](https://medium.com/@danushidk507/workflows-in-agentic-ai-claude-code-workflows-8cac80792dd8) |
| levelup.gitconnected.com | huizhou92 — "Claude Code Best Practices: 12 Patterns Agentic Engineers Use" (Apr 2026) | [article](https://levelup.gitconnected.com/claude-code-best-practices-12-patterns-agentic-engineers-use-65264e3eb919) |
| mindstudio.ai | "Beyond One-Shot Prompts: 5 Claude Code Workflow Patterns" (sequential / operator / split-and-merge / agent teams / headless) | [article](https://www.mindstudio.ai/blog/claude-code-agentic-workflow-patterns) |
| dev.to | "AI Coding Workflow 2026: what a YC founder's stack taught me about the hard parts" | [article](https://dev.to/kunal_d6a8fea2309e1571ee7/ai-coding-workflow-2026-what-a-yc-founders-stack-taught-me-about-the-hard-parts-guide-28hl) |
| github.com | shanraisshan/claude-code-best-practice — "from vibe coding to agentic engineering" | [repo](https://github.com/shanraisshan/claude-code-best-practice) |

**Marketplace signal:** one quote is on-the-nose for RavenClaude — *"Every best practice in the ecosystem — CLAUDE.md files, subagents, /compact, checkpoints, worktrees — exists to manage [the context-window] constraint."* That directly validates this session's new best-practice (checkpoints as the recovery layer) and the existing context-window/Sleipnir/compaction surface. The "5 workflow patterns" framing (sequential/operator/split-and-merge/agent-teams/headless) is a candidate cross-check against the repo's orchestration trees.

---

## How to reproduce / extend (headless)

```shell
export SEARCH_API_KEY=...   # Brave Search API token: https://brave.com/search/api/
python3 scripts/content-scan.py \
  --queries "fractional CFO AI" "month-end close automation" "agentic AI coding" \
  --count 15 --freshness pm --fetch-bodies \
  --out docs/research/$(date +%F)-content-scan
```

`--fetch-bodies` pulls full text from the open-web hits (Medium/Substack/blogs) and leaves LinkedIn/Reddit as discovery-only rows. Drop `--site linkedin.com` in to do a LinkedIn-only discovery pass (titles+snippets), or omit it for the whole open web.
