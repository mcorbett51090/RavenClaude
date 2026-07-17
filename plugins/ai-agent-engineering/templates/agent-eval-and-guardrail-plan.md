# Agent eval & guardrail plan — <agent / system name>

> Captured when building the eval harness and guardrail tests for an agent, and the running record of its eval sets, judges, thresholds, and monitoring. Pairs with
> [`agent-architecture-design-doc.md`](agent-architecture-design-doc.md) (the topology/tool side of the same agent).
> **An agent without an eval harness is a demo, not a system.** Volatile model/framework/tooling specifics carry a retrieval date — verify at use.

**Owner:** <name> · **Date:** <YYYY-MM-DD> · **Status:** draft / approved · **Review cadence:** <monthly / per change>

## 1. Offline eval set (representative + adversarial)
| Bucket | # cases | Covers | Grading |
|---|---|---|---|
| Representative | <N> | <the real task distribution> | <exact / rubric / required tool call> |
| Adversarial | <N> | <ambiguity · missing data · tool failure · injection · out-of-scope> | <must-not-do / rubric> |
- **Total cases:** <N> · **Source:** <hand-authored + prod failures fed back>

## 2. Judges & checks
- **Programmatic / exact checks:** <valid JSON? · right tool called? · value in bounds?>
- **LLM-as-judge:** <rubric summary>
  - **Judge model:** <model — retrieved <date>>
  - **Calibration:** <agreement % vs a human-labeled sample of N> · **re-calibrated:** <date>
  - **Method:** <pairwise / rubric-scored — NOT a drifting raw 1-10>

## 3. Regression gate (CI — gate the merge)
| Threshold | Baseline | Gate |
|---|---|---|
| Quality (judge / exact score) | <0.90> | <≥ baseline> |
| Cost (tokens/task) | <20K> | <≤ ceiling> |
| Latency (p95) | <5s> | <≤ SLO> |
- **Runs on:** every prompt / model / tool / topology change
- **On fail:** <block merge · surface the regressed cases>

## 4. Guardrail catalog & tests
| Guardrail | What it enforces | Test asserts |
|---|---|---|
| Input validation | <schema · caller scope> | <malformed / out-of-scope rejected> |
| Prompt-injection defense | <tool/retrieved text = data> | <injected "ignore instructions" in a doc is NOT followed> |
| Tool-permission scoping | <least privilege per tool> | <tool can't act outside its scope> |
| Human-in-the-loop | <irreversible action pauses> | <high-blast action does NOT auto-execute> |
| Output validation | <bounds / format / policy> | <out-of-bounds output caught before it acts> |

## 5. Online monitoring (prod drifts — watch it)
- **Quality:** <sampled judge score · feedback · failure/escalation rate · alert threshold>
- **Cost:** <tokens/task · calls/task · alert threshold>
- **Latency:** <p50 / p95 · alert threshold>
- **Feedback loop:** <prod failures fed back into §1 offline set>

## 6. Red-team pass (before shipping)
| Vector | Attempted | Result | Fix / mitigation | Regression case added? |
|---|---|---|---|---|
| Jailbreak | <…> | <held / broke> | <…> | <yes> |
| Injection (every untrusted input) | <…> | <…> | <…> | <yes> |
| Tool-abuse (unwanted side-effect) | <…> | <…> | <…> | <yes> |
| Data exfiltration | <…> | <…> | <…> | <yes> |
| Cost-bomb (loop / token blowout) | <…> | <…> | <loop-cap / complexity guard> | <yes> |

## 7. Proof (the evidence it's a system, not a demo)
- **Regression gate:** <passing at <commit/date>>
- **Judge calibration:** <agreement %>
- **Guardrail tests:** <N/N passing>
- **Cost/latency rollup:** <tokens/task · calls/task · p95 · cost/task>
- **Red-team:** <findings · fixed / accepted-with-mitigation>

## Seams (not this team)
- **The eval methodology / science (metric design, judge-calibration science):** llm-evaluation-engineering
- **The topology / guardrail strategy:** agentic-systems-architect (this plugin)
- **Running the monitored service (SLOs, alerting, on-call):** observability-sre
- **The retrieval tool being evaluated as a dependency:** ai-rag-engineering

## Open questions / risks
- <list>

**Sign-off:** <tech lead / staff eng> · <date> · *Volatile judge-model / threshold / tooling specifics verified at use (<retrieval date>).*
