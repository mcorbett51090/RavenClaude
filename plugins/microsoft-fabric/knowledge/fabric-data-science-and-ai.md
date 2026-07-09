# Fabric data science & AI (2026)

**Last reviewed:** 2026-05-28 · **Confidence:** medium-high (first-party Microsoft Learn, retrieved 2026-05-28). The Fabric AI surface ships monthly — re-verify GA/preview on the Researcher sweep.
**Owner:** `lakehouse-engineer` (interim, until the deferred `fabric-data-ai-engineer` agent ships in v0.2.0). Pairs with [`fabric-2026-capability-map.md`](fabric-2026-capability-map.md).

The Data Science workload covers the ML lifecycle + the AI-over-OneLake surface. This is the knowledge the deferred `fabric-data-ai-engineer` would drive; until then `lakehouse-engineer` carries it.

## AI over your data (the 2026 headline)
- **Fabric Data Agents — GA (March 2026).** Conversational, **read-only** NL Q&A over Lakehouse / Warehouse / Power BI semantic models / KQL / SQL & mirrored DBs / ontology / Microsoft Graph, via **Azure OpenAI Assistant APIs**. Enforces the **requesting user's** permissions (least-privilege), tenant/workspace policy, and **Purview** governance (DLP, access policies); read-only connections only; optional Azure AI Content Safety. **CI/CD + diagnostics are GA.** Configure with custom instructions/examples. Integrates with **Microsoft Foundry (Foundry IQ)**, **Copilot Studio** (embed as a skill), and **M365 Copilot**. → seam to `azure-cloud` (see [`azure-ai-foundry.md`](../../azure-cloud/knowledge/azure-ai-foundry.md)) and `power-platform` (Copilot Studio).
- **Operations Agents** — autonomous, **ontology-driven**; monitor real-time streams, apply rules/objectives, and act/recommend via **Activator + Power Automate** (with Teams human-approval). Unlike Data Agents (answer questions), Operations Agents act on live conditions. Owned at the streaming layer by `realtime-intelligence-engineer`.
- **AI functions — GA (Nov 2025).** Row-level LLM enrichment in notebooks/Spark (`ai.embed()`, sentiment, entity-extraction, summarize, generate); **multimodal (preview, March 2026)** — images/PDFs via `aifunc.load` / `ai.infer_schema`; default concurrency 200; Azure OpenAI + Foundry models (incl. Claude/LLaMA). **June-2026 GA update (retrieved 2026-07-09, [AI functions](https://learn.microsoft.com/fabric/data-science/ai-functions/overview) / [What's new in Fabric](https://learn.microsoft.com/fabric/fundamentals/whats-new)):** AI Functions now **default to `gpt-5-mini` (low reasoning)** for both pandas and PySpark, and support **`gpt-5.1`** for heavier transforms — model identifiers are volatile, so **`[verify-at-use — current default model]`** before quoting. Durable in the same update: pandas AI Functions **drop the hard `openai` package dependency** (no longer required to install/import `openai` for pandas AI Functions).
- **Copilot for Data Engineering & Data Science** — context-aware notebook assistant (workspace + lakehouse schema + runtime); multi-step generate/refactor/summarize + **Fix with Copilot**.

## ML lifecycle
- **MLflow** is native — experiments + autologging (params/metrics/models). **Cross-workspace logging GA (April 2026)**: log from any env (Fabric notebook / Databricks / Azure ML / local) to any Fabric workspace via `synapseml-mlflow` + `MLFLOW_TRACKING_URI` → dev/test/prod MLOps separation + train-where-data-lives / serve-elsewhere.
- **AutoML — low-code GA (March 2026)** + code-first: classification / regression / forecasting / multiclass; PySpark + Synapse LightGBM + CatBoost/XGBoost/Prophet/AutoARIMA/TFT etc.; MLflow-tracked; Spark or single-node mode.
- **Models**: MLflow registry (version/track), batch scoring in Spark (`SynapseML PREDICT`) or **real-time endpoints**; **Data Wrangler** for low-code prep.
- **Semantic Link — GA (Feb 2026)**: a shared semantic layer connecting AI/BI/data-engineering — use Power BI semantic models directly in notebooks, automate Power BI tasks, streamline Spark/SQL.

## Developer access
- **GraphQL API** — one endpoint to query Warehouses / SQL DBs / Lakehouses / mirrored DBs (schema discovery, generated queries, relationships).
- **Foundry IQ + OneLake files** (Dec 2025) — index/enrich OneLake docs/images/logs directly in Microsoft Foundry knowledge, no duplication.

## House-opinion alignment + governance
- **Data Agents are read-only + permission-respecting + Purview-governed** — the secure default for "let business users ask the data questions." Connector/DLP/identity design still routes through `ravenclaude-core/security-reviewer`.
- **Cite the GA/preview status with a date** (house opinion #9) — this surface moved a lot in late-2025/2026 (Data Agent + AutoML + AI functions all flipped GA); verify before quoting.
- **Statistical validity** of an AI/ML-surfaced metric → `applied-statistics/applied-statistician` ("is it real?"); Fabric gets it computed + served, applied-statistics says whether it's signal.

## Sources (retrieved 2026-05-28)
[Analyze and train data in Fabric](https://learn.microsoft.com/fabric/fundamentals/analyze-train-data), [Fabric data agent concepts](https://learn.microsoft.com/fabric/data-science/concept-data-agent), [What's new — Data Science](https://learn.microsoft.com/fabric/fundamentals/whats-new), [AutoML in Fabric](https://learn.microsoft.com/fabric/data-science/automated-machine-learning-fabric), [AI functions](https://learn.microsoft.com/fabric/data-science/ai-functions/overview), [Semantic Link](https://learn.microsoft.com/fabric/data-science/semantic-link-overview).
