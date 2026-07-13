# ux-research

> The **UX-research discipline layer** for Claude Code — the team that answers *"is this a real research question, what method rigorously answers it, and how do we turn the evidence into a decision — without research theater or the biases that make research lie?"* Two agents: the **ux-research-lead** (frames the question, selects the method, plans the sample/recruit, runs research-ops, and owns research ethics + participant-PII) and the **research-execution-and-synthesis-specialist** (designs the protocol, moderates without leading, runs usability tests and surveys, and synthesizes raw data into evidence-weighted, bias-checked, prioritized insight).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "How should we study whether the new dashboard works?" | A reframed researchable question, the generative-vs-evaluative / qual-vs-quant / attitudinal-vs-behavioral / moderated-vs-unmoderated method call with rationale, and the decision it informs |
| "Leadership already picked the redesign — run a study that confirms users prefer it." | A research-theater diagnosis (the decision is made — this is validation, not inquiry) and a reframe into a real question, or a recommendation to kill the study and spend the budget elsewhere |
| "How many participants do we need, and where from?" | A sample size matched to the claim (directional ~5 vs statistically-powered), a screener/panel/incentive recruit plan, and the rigor that result can and cannot support |
| "We're recruiting 20 users next week — what do we need for consent and data?" | An informed-consent flow, a data-minimization + de-identification plan, a retention limit set before collection, and sensitive-population care — captured in the research plan |
| "Write the protocol and tasks for a usability test of checkout." | A protocol with goal-based (not step-by-step) tasks, a think-aloud script, task-success + severity criteria, and non-leading moderation prompts |
| "Why does everyone rate our satisfaction survey highly?" | A bias audit flagging leading, double-barreled, social-desirability, and sampling-frame problems, with rewritten neutral items and a rigor caveat |
| "We ran 8 interviews — turn the notes into findings we can act on." | An affinity/thematic synthesis separating observation from interpretation, each finding weighted by evidence strength and severity, prioritized, and tied to a decision |

**Two rules it never breaks:** *a question you already know the answer to is theater* (kill it or reframe it — no study confirms a made decision), and *method follows the question, never the reverse* (you cannot A/B your way to "why", or interview your way to "how many").

## What's inside

- **2 agents** — `ux-research-lead` (question framing, method selection, sample/recruit, research-ops, ethics/participant-PII) and `research-execution-and-synthesis-specialist` (protocol & task design, non-leading moderation, usability testing, survey design, and synthesis from raw notes to prioritized insight).
- **3 skills** — `plan-the-research-study`, `run-usability-and-interview-sessions`, `synthesize-research-into-insight`.
- **2 knowledge files** — a Mermaid UX-research decision tree (research-theater gate, which-method, sample-size & rigor, consent/PII path) with method→answer trade-off tables and the bias catalog, and a dated 2026 UX-research-patterns reference (method matrix, moderation & survey best practices, bias counters, evidence-strength framing, research-ops/repository patterns, ethics/PII discipline, and a tooling map).
- **2 templates** — a research plan and a research findings report.

## Where it sits among the product & design plugins

```
product-management               →  turns insight into ROADMAP / prioritization   ("the decision, not the research")
web-design                       →  the visual / interaction / IA DESIGN itself   ("build the screen; run its a11y audit")
experimentation-growth-engineering →  online A/B & significance AT SCALE           ("is A significantly better than B?")
data-science-research            →  advanced quant / statistical MODELING          ("regression, segmentation, multivariate")
ux-research (HERE)               →  FRAME the question · RUN the study · SYNTHESIZE evidence   ("what do we study, how rigorously, and what did we learn?")
```

This plugin **runs the research discipline** and **feeds** those teams rather than replacing them: it hands the roadmap decision to `product-management`, the design change to `web-design`, the at-scale A/B to `experimentation-growth-engineering`, and the heavy stats to `data-science-research` — while owning the framing, method rigor, moderation craft, ethics, and synthesis that make the evidence trustworthy in the first place.

## Domain stance

Question-first and bias-guarded: the research-theater gate before any study, method-follows-the-question (generative/evaluative · qual/quant · attitudinal/behavioral · moderated/unmoderated), sample-sizing to the claim (directional ~5 vs powered), observation kept separate from interpretation, and participant data treated as PII from first contact (informed consent, minimization, de-identification, retention limits, sensitive-population care). Fluent across usability testing, interviews, surveys, and synthesis (affinity/thematic analysis) — and militant about the bias catalog (confirmation, leading, sampling, recency, social-desirability, availability). Research-platform features, panel quality, and sample-size heuristics carry retrieval dates — re-verify before a stakeholder commitment.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ux-research@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
