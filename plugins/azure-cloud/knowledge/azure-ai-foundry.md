# Microsoft Foundry (Azure AI Foundry) — models & agents

**Last reviewed:** 2026-05-28 · **Confidence:** medium-high (first-party Microsoft Learn, retrieved 2026-05-28). The Foundry surface is renaming + moving fast (classic vs new portal) — verify before quoting.
**Owner:** `app-platform-engineer` (the AI hosting/runtime) + `azure-architect` (when AI is part of the system design). AI-app prompt/agent *logic* is `claude-app-engineering`; this doc is the **Azure hosting layer**.

The Azure AI layer the rest of the stack seams to: **Microsoft Foundry** (the rebrand of *Azure AI Foundry*; portal at **ai.azure.com**) is where you deploy models and run agents on Azure.

## Projects (get the resource shape right — it changed)
- **Foundry projects** (current) — child resources of a **Microsoft Foundry resource** (`Microsoft.CognitiveServices/account` kind `AIServices`); share parent settings (networking, RBAC, cost, policy), with per-project Azure RBAC. The **Foundry API + SDK** (`azure-ai-projects`) compose Agents / Evaluations / Models / Indexes / Data behind a project **endpoint** (`https://<resource>.services.ai.azure.com/api/projects/<project>`).
- **Hub-based projects** (classic) — older Azure-ML-backed shape requiring extra Storage + Key Vault. **The Agent Service uses Foundry-project endpoints (not the old connection string) since May 2025**; new SDK/REST don't support hub-based projects. Migrate hub → Foundry projects (feature parity still catching up — check the support matrix).

## Model catalog — two deployment options (the recurring call)
| | **Serverless / standard deployment** | **Managed compute** |
|---|---|---|
| How | Microsoft-hosted API; pay per token (in/out) | model weights on dedicated VMs you run |
| Bill | per token | VM core-hours |
| When | most models; fastest to stand up; pay-as-you-go | dedicated capacity / specific models / isolation |
| Network | follows the resource's public-network-access flag | configure a managed network |
Both: Entra **and** key auth (prefer Entra/keyless — house opinion #4), Azure AI Content Safety filters. Deploying models *to the Foundry resource* (vs per-project endpoints) gives routing, custom content filters, and **keyless Entra auth** across all models.

## Foundry Agent Service
A **fully-managed** platform to build/deploy/scale agents. Every agent = **model** (from the catalog) + **instructions** (prompt / workflow / hosted-agent code) + **tools** (search, files, API calls). Two builds: **prompt agents** (no-code in the portal) and **Hosted agents** (code — Agent Framework, LangGraph, or your own). The service handles hosting, scaling, **identity, observability, enterprise security**. Bring-your-own-model via a gateway connection (deployment name `<connection>/<model>`).

## Seams (this is a hand-off layer)
- **`claude-app-engineering`** — owns the *agent logic* (prompts, MCP, evals, the Claude Agent SDK). When the app runs **Claude on Azure** (via Foundry model catalog / a custom-engine host), `app-platform-engineer` provisions the Foundry resource + project + networking + identity; claude-app-engineering builds the agent. *Litmus: prompt/tool/eval code → claude-app-engineering; the Foundry resource/project/model-deployment/identity/network → here.*
- **`microsoft-fabric`** — **Fabric Data Agents** integrate with **Foundry IQ** (shared context layer) and OneLake-files knowledge; the Fabric side is `microsoft-fabric` ([`../../microsoft-fabric/knowledge/fabric-data-science-and-ai.md`](../../microsoft-fabric/knowledge/fabric-data-science-and-ai.md)), the Foundry resource/hosting is here.
- **`power-platform`** — a Copilot Studio **custom-engine** agent or M365 Copilot custom-engine agent hosted on Foundry → `power-platform/copilot-studio-engineer` owns the Copilot integration, this owns the Foundry host (see [`../../power-platform/knowledge/copilot-agents-2026.md`](../../power-platform/knowledge/copilot-agents-2026.md)).
- **`ravenclaude-core/security-reviewer`** — model auth (prefer Entra/keyless), content-safety, network isolation, data-privacy posture (managed network / PNA flag) all route through core's security review.

## House-opinion alignment
- **Passwordless** (#4): Entra/keyless model auth over keys; managed identity for the app calling Foundry.
- **Private-by-default** (#6): managed network / Private Endpoint for the Foundry resource; PNA flag off where possible.
- **Cite the capability + date** (#16): "Microsoft Foundry" rebrand, classic-vs-new portal, **Azure AI Inference beta SDK retires 2026-08-26 → OpenAI/v1 API + stable OpenAI SDK** — verify before quoting.

## Sources (retrieved 2026-05-28)
[What is Foundry Agent Service](https://learn.microsoft.com/azure/foundry/agents/overview), [Foundry Models overview](https://learn.microsoft.com/azure/foundry-classic/concepts/foundry-models-overview), [Migrate hub → Foundry projects](https://learn.microsoft.com/azure/foundry-classic/how-to/migrate-project), [Configure project to use Foundry Models](https://learn.microsoft.com/azure/foundry-classic/foundry-models/how-to/quickstart-ai-project), [Bring your own model](https://learn.microsoft.com/azure/foundry/agents/how-to/ai-gateway).
