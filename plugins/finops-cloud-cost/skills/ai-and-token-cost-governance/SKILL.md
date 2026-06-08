---
description: "Govern GenAI and LLM inference costs: design per-feature token budgets, build a model-tiering matrix, implement prompt caching and batch strategies, set anomaly alerts on inference spend, and incorporate AI token cost as a first-class line item in the FinOps budget. All model prices are marked verify-at-use."
---

# AI & Token Cost Governance

**Purpose:** make AI/LLM inference costs visible, attributable, bounded, and anomaly-detected so
they are managed alongside cloud compute rather than discovered on the monthly bill.

## The operating loop

1. **Instrument token usage per feature.** Add feature/team tags to every inference API call.
   Log input tokens, output tokens, model name, and latency per request. This is the prerequisite
   for attribution; without it all AI cost lands in a single undifferentiated bucket.
2. **Build per-feature token budgets.** Estimate: daily request volume × average input tokens ×
   input price + average output tokens × output price. Model prices are volatile — look up current
   prices at inference time and mark every estimate `[verify-at-use]`. Set a daily and monthly budget
   per feature and per team. Use `finops_calc.py unit_cost()` for cost-per-request arithmetic.
3. **Build the model-tiering matrix.** For each use case, define the quality bar (accuracy
   requirements, latency requirements) and map to the cheapest model that meets it:
   - Heavyweight frontier model: complex multi-step reasoning, legal/financial analysis, code generation
     for production. Use when quality is non-negotiable and cost is secondary.
   - Lightweight fast model: classification, extraction, summarization, intent routing. High volume
     acceptable; use the smallest model that passes quality regression.
   - Fine-tuned small model: domain-specific high-volume tasks; highest cost efficiency once the fine-
     tuning cost is amortized. Requires quality regression testing on every model update.
   Run a quality regression test before downgrading any production feature to a cheaper model tier.
4. **Design prompt caching.** Identify cache-eligible content:
   - Long static system prompts (>1,024 tokens) that repeat across requests — these are the best
     cache targets. Provider-native prompt caching discounts the cached prefix significantly.
     [verify-at-use: caching mechanics and discounts vary by provider and API version]
   - Semantic caching: embed the user query, match against a cache of recent (query, response) pairs
     by cosine similarity. Appropriate for high-volume low-variability queries. Requires a cache
     invalidation policy (max age, explicit invalidation).
   - Result caching: for fully deterministic outputs (always the same input → same output), cache
     the raw response string. Requires deterministic prompt construction.
5. **Evaluate batch vs real-time.** Async batch inference is 40–60% cheaper on most providers
   [verify-at-use] with 1–24 hour latency. Appropriate for: offline document processing, nightly
   enrichment jobs, non-interactive summarization. Not appropriate for interactive features. Design
   the batch pipeline for each eligible use case; track queue depth and SLA separately.
6. **Set anomaly detection.** Choose a threshold: z-score (cost today vs rolling 14-day mean, alert
   at z>2) or percentage over baseline (>150% of rolling 7-day average). Use `finops_calc.py
   anomaly_z_score()` for the math. Route the alert to the on-call engineer and the feature owner.
   A runbook: (a) identify the feature via the usage tag, (b) check request volume, (c) check
   tokens-per-request (a prompt injection or runaway loop expands output tokens drastically).
7. **Incorporate into the FinOps budget.** AI token cost belongs in the cloud cost model alongside
   EC2 and RDS. Forecast with: projected request volume × tokens-per-request × model price. Build
   two scenarios: baseline (stable model, stable volume) and a 2× volume / model-upgrade scenario.
   Present the range as the budget ask, not a point estimate.

## Anti-patterns

- AI inference cost in "misc API fees" with no feature attribution.
- A hardcoded per-million-token price in any doc or IaC file with no date.
- A model upgrade decision with no cost-impact analysis.
- Batch inference for interactive user-facing features.
- Real-time inference for asynchronous jobs that could tolerate 1-hour latency.
- A caching strategy evaluated on latency/accuracy without cost-per-cache-hit analysis.

## Output

A per-feature token budget (with `[verify-at-use]` prices), a model-tiering matrix with quality-bar
rationale, a caching strategy (eligible prefixes + method + expected savings), an anomaly detection
design (threshold + alert route + runbook), and the AI cost line item in the FinOps budget with two
scenarios.
