# AI Coding Model Guidance — Decision Trees

Vendor-neutral model-selection decision trees for the `ai-coding-model-guidance` plugin. Traverse the relevant tree **top-to-bottom before naming a model SKU** — do not keyword-match the developer's task description. Last reviewed: 2026-06-05.

All availability and pricing facts carry `[verify-at-use — YYYY-MM]` markers. The specific model names in the leaves are mapped from the dated lineup in [`cross-tool-model-lineup-2026.md`](cross-tool-model-lineup-2026.md) — re-verify before quoting a client.

---

## Decision Tree: Vendor-neutral task-shape to model-tier

**When this applies:** A developer needs a model recommendation for any AI coding tool (Copilot, Codex, or Grok) and has not yet specified a tier. Observable triggers: "which model should I use?"; "is the default model good enough?"; "I need something better for this task."

**Last verified:** 2026-06-05 against `cross-tool-model-lineup-2026.md` (vendor-neutral methodology; map leaves to vendor SKUs after traversal).

```mermaid
flowchart TD
    START[Task needs a model tier] --> Q1{Is this inline completion or interactive autocomplete - latency under 500ms required?}
    Q1 -->|Yes| INLINE[Fast inline tier - cheapest available; latency first]
    Q1 -->|No| Q2{Is the task autonomous - running unsupervised over many files or steps?}
    Q2 -->|Yes| Q3{Is it high-blast - irreversible production actions?}
    Q3 -->|Yes| FRONTIER[Frontier tier - maximum reasoning; human gate recommended]
    Q3 -->|No| Q4{Can reasoning effort be raised on the current balanced model?}
    Q4 -->|Yes - vendor exposes a reasoning dial| RAISEDIAL[Raise reasoning level first - same model cheaper]
    Q4 -->|No or already at max| FRONTIER
    Q2 -->|No - supervised or one-shot| Q5{Routine single-file or moderate analysis?}
    Q5 -->|Yes| BALANCED[Balanced default tier - best cost-per-resolved-task for most work]
    Q5 -->|No - large multi-file or hard reasoning| Q4
```

**Rationale per leaf:**
- *Fast inline tier* — latency is the binding constraint; quality gap vs balanced is small for single-line completions; always the cheapest choice.
- *Balanced default* — the majority of coding tasks; moderate reasoning, good quality, significantly lower cost than frontier (verify-at-use).
- *Raise reasoning level* — when the vendor exposes a thinking-effort dial (e.g. Codex reasoning flag): upgrade effort before upgrading model; often closes the gap at lower cost.
- *Frontier tier* — autonomous multi-file tasks, hard reasoning tail, or high-blast irreversible actions where the cost of a wrong output exceeds the model premium.

**Tradeoffs summary:**

| Tier | Latency | Cost relative to balanced | Autonomy fit | Use when |
|---|---|---|---|---|
| Fast inline | Lowest | Lowest | None | Autocomplete, one-liner fix |
| Balanced default | Medium | 1x baseline | Supervised | Most daily coding tasks |
| Raised reasoning / same model | Medium-high | Moderate increase | Supervised | Quality gap, reasoning-dial available |
| Frontier | Higher | Significant premium (verify-at-use) | Autonomous | Hard tail; unsupervised; high-blast |

---

## Decision Tree: Copilot model picker — which surface and plan gate applies?

**When this applies:** A developer is using GitHub Copilot and asks about model availability, the picker, or why a model is not showing up. Observable triggers: "I don't see Model X in Copilot"; "which models are available for Copilot chat?"; "can I use the coding agent with this model?"

**Last verified:** 2026-06-05 against `cross-tool-model-lineup-2026.md` Copilot section `[verify-at-use]`.

```mermaid
flowchart TD
    START[Developer asks about a Copilot model] --> Q1{Is the model in the verified Copilot lineup?}
    Q1 -->|No| NOTVERIFIED[Closed-world: not in lineup - offer to research; do not confirm]
    Q1 -->|Yes| Q2{Which surface - completions, chat IDE, coding agent, cloud agent, mobile?}
    Q2 -->|Completions| Q3{What plan - Free, Pro, Business, Enterprise?}
    Q2 -->|Chat IDE or coding agent| Q3
    Q2 -->|Cloud agent or mobile| CHECKPLAN[Check plan gate in lineup - mobile and cloud agent are surface-gated]
    Q3 -->|Free| FREECHECK[Verify free-tier model access in lineup - subset of full picker]
    Q3 -->|Pro or above| AVAILABLE[Model likely available - confirm from lineup entry with date]
    FREECHECK --> GATE{Model in the free-tier sub-list?}
    GATE -->|Yes| AVAILABLE
    GATE -->|No| PLANUPSELL[Model requires Pro or above - explain the plan gate]
```

**Rationale per leaf:**
- *Not in lineup* — closed-world rule applies; absence from the verified lineup means do not confirm availability.
- *Free-tier sub-list* — GitHub Copilot Free exposes a subset of models; a model in the full picker may not be in the free sub-list.
- *Plan gate* — Business/Enterprise unlock additional models and org policy controls; Pro unlocks beyond Free.
- *Surface-gated* — cloud agent and mobile have separate availability gates that may differ from the IDE chat picker; check explicitly.

**Tradeoffs summary:**

| Surface | Plan dependency | Key gate | Verify-at-use source |
|---|---|---|---|
| Completions | Plan-gated | Free/Pro/Business model sub-list | Copilot model availability docs |
| Chat IDE | Plan-gated | Same as completions | Copilot model availability docs |
| Coding agent | Plan-gated | Enterprise/Business feature | Copilot docs - agent surface |
| Cloud agent | Surface + plan | Separate availability list | Copilot docs - cloud agent |
| Mobile | Surface + plan | Mobile-specific sub-list | Copilot mobile docs |

---

## Decision Tree: Codex — default model, reasoning dial, or model upgrade?

**When this applies:** A developer using OpenAI Codex CLI or cloud is getting insufficient quality and needs to decide between accepting the default, raising the reasoning level, or upgrading to a bigger model. Observable triggers: "the default Codex model isn't getting this right"; "should I use a higher reasoning setting?"; "do I need the frontier Codex model?"

**Last verified:** 2026-06-05 against `cross-tool-model-lineup-2026.md` Codex section `[verify-at-use]`.

```mermaid
flowchart TD
    START[Codex output quality is insufficient] --> Q1{Is the task latency-sensitive - inline or interactive?}
    Q1 -->|Yes| FAST[Use the fast model - GPT-5.5 or equivalent fast default; reasoning dial off]
    Q1 -->|No - background or supervised run| Q2{Have you tried the default model at its default reasoning level?}
    Q2 -->|No| TRYDEFAULT[Try default first - balanced model at medium reasoning]
    Q2 -->|Yes, still insufficient| Q3{Is the vendor reasoning-level dial available and not at max?}
    Q3 -->|Yes| RAISEIT[Raise reasoning level on the same model - cheaper than a model upgrade]
    Q3 -->|No - at max or not available| Q4{Task is a long unsupervised run or a hard multi-file change?}
    Q4 -->|Yes| FRONTIER_CODEX[Upgrade to frontier Codex model - verify current SKU in lineup]
    Q4 -->|No - scoped task still failing| REVISESCOPE[Revisit task scope and prompt before paying for a model upgrade]
```

**Rationale per leaf:**
- *Fast model* — latency-critical inline tasks; reasoning-dial impact on latency rules out higher-effort levels.
- *Try default first* — the default model resolves a large fraction of everyday coding tasks; don't skip it.
- *Raise reasoning level* — same model, more thinking effort; almost always worth trying before a model upgrade; verify the cost delta (verify-at-use).
- *Frontier Codex model* — long unsupervised agentic runs or demonstrably hard tasks that still fail at max reasoning on the balanced model.
- *Revisit scope* — if a scoped, bounded task still fails at high reasoning, the problem is often prompt clarity or task decomposition, not model tier.

**Tradeoffs summary:**

| Option | Cost delta | Latency delta | When to try | Skip if |
|---|---|---|---|---|
| Default model / medium reasoning | 1x baseline | Lowest | Always first | Task is demonstrably hard tail |
| Raise reasoning level | Moderate increase (verify-at-use) | Moderate increase | Quality gap on same model | Latency is the binding constraint |
| Frontier model upgrade | Large increase (verify-at-use) | Higher | Hard tail; agentic runs | Task is scoped / prompt needs work |
