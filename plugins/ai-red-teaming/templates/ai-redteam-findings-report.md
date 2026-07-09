# AI red-team findings report — <system-under-test>

> The findings + remediation record for a red-team engagement. Reached from the
> plan in [`ai-redteam-plan.md`](ai-redteam-plan.md). The order matters:
> **reproduce → triage → remediate defense-in-depth → retest → regress.** A finding
> you can't reproduce is an anecdote; a fix you didn't retest is a hope.

**Engagement:** <name / ID> · **Dates:** <start–end> · **Engineer:** <name> · **Lead:** <name> · **RoE in force:** <yes — see plan>

## Executive summary
- **Attacks run:** <classes executed, at a glance>
- **Findings:** <count by severity — P0 / P1 / P2 / P3>
- **Highest-severity finding:** <one line>
- **Remediation status:** <n fixed & retested · n open>

## Findings
> One block per finding. Reproducibility is mandatory: payload + transcript + model/version + settings.

### Finding <ID> — <short title>
- **Class:** <OWASP LLM Top 10 ID + name · MITRE ATLAS technique>
- **Severity (likelihood × impact):** <P0/P1/P2/P3 — with the reasoning>
- **Attack type:** <direct/indirect injection · jailbreak (roleplay/encoding/many-shot/crescendo) · disclosure/extraction · tool-abuse · multimodal>
- **Reproducible payload:** <the exact input / poisoned content>
- **Transcript / evidence:** <link or excerpt — model, version, temperature, system prompt>
- **Success rate:** <deterministic, or X/N attempts if probabilistic>
- **Observed behavior / impact:** <what it did — unauthorized action, leaked data, bypassed policy>
- **Remediation (defense-in-depth — the layers):**
  - Input guardrail: <...>
  - Output guardrail: <...>
  - Prompt structure (injection-resistant): <...>
  - Least privilege / allow-list: <...>
  - Human-in-the-loop: <...>
  - Output-handling / rate-cost limit: <...>
- **Retest (exact attack re-run):** <blocked / success-rate-driven-to-0 / still-open> · <date>
- **Regression:** <added to the CI harness? — PyRIT / Garak / Promptfoo red-team / Giskard case>
- **Disclosure:** <status for any third-party-affecting finding>

### Finding <ID> — <short title>
- <repeat the block>

## Automated harness
- **Tool:** <PyRIT / Garak / Promptfoo red-team / Giskard — note: feature sets volatile, retrieval date>
- **Attack datasets:** <per class>
- **Scorer / judge:** <how success is scored — e.g. LLM-as-judge with an adversarial rubric>
- **CI gate + regression baseline:** <where it runs · the pass-fail threshold>
- **Distinct from quality eval-regression:** <confirm the adversarial suite is separate from llm-evaluation-engineering's>

## Remediation summary
| Finding | Severity | Remediation layers | Retest | Regressed? |
|---|---|---|---|---|
| <ID> | P0 | <layers> | blocked | yes |
| <ID> | P1 | <layers> | open | — |

## Residual risk & recommendations
- **Still-open findings + interim mitigations:** <...>
- **Coverage gaps found:** <where a human beat the harness — what to add>
- **Re-test cadence:** <re-run the suite on every model/prompt change; re-verify jailbreak techniques after any version bump>

## Seams engaged
- <eval → llm-evaluation-engineering · content-policy → trust-and-safety · non-AI pentest → security-engineering · RAG → ai-rag-engineering · app/agent → claude-app-engineering>

**Closed at:** <timestamp> · **Signed off:** <lead>
