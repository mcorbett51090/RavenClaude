# Changelog — marketing-operations

All notable changes to this plugin are documented here. Versioning is semver; bump on every user-visible change (AGENTS.md).

## [0.2.0] — 2026-06-22

Execution value-adds: email deliverability + content-marketing engine. No agents added; all existing files unchanged.

- **+2 skills** — `email-deliverability` (SPF/DKIM/DMARC alignment & policy, dedicated-vs-shared IP, warmup, reputation) and `content-engine` (intent briefs, topic clusters/pillar pages, distribution, leading-vs-lagging measurement). Now **7 skills**.
- **+2 knowledge docs** — `knowledge/email-deliverability.md` (2 Mermaid decision trees) and `knowledge/content-marketing-engine.md` (1 Mermaid decision tree). Now a **6-file knowledge bank**.
- **+4 best-practice rules** — `authenticate-spf-dkim-dmarc-before-you-send`, `warm-up-and-protect-sender-reputation`, `brief-every-piece-against-a-search-intent`, `build-topic-clusters-not-orphan-posts`. Now **12 rules**.

## [0.1.0] — 2026-06-08

Initial release.

- **4 agents** — `marketing-ops-lead`, `demand-gen-funnel-analyst`, `attribution-analytics-specialist`, `martech-campaign-architect`, each carrying the full scenario-authoring schema.
- **5 skills + 5 commands** — `diagnose-funnel`, `size-demand`, `read-cac-ltv`, `evaluate-channel-mix`, `audit-attribution-data`.
- **4-file knowledge bank** — KPI glossary, unit economics, 2025–2026 context, and Mermaid decision trees.
- **`scripts/marketingops_calc.py`** — stdlib calculator: `funnel`, `cac-ltv`, `channel-roi`. Decision-support only.
- **4 templates · 8 best-practice rules · scenarios bank · 1 advisory hook**.
