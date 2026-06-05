# ML Engineering (MLOps) Plugin — Team Constitution

> Team constitution for the `ml-engineering` Claude Code plugin — **4** specialist agents for taking ML models to production and keeping them healthy — reproducible training pipelines and experiment tracking, feature stores and training/serving consistency, model serving and deployment, and monitoring for drift and decay. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`ml-platform-architect`](agents/ml-platform-architect.md) | MLOps architecture: build-vs-buy of the ML platform, the train->register->serve->monitor loop, stack selection (tracking/registry/orchestration/serving), reproducibility strategy, and the team's ML maturity path | "design our MLOps platform", "build or buy the ML stack?", "how do we get models to production reliably?", "what's our ML maturity gap?" |
| [`training-pipeline-engineer`](agents/training-pipeline-engineer.md) | Reproducible training: pipelines (data prep -> train -> evaluate -> register), experiment tracking, the model registry, feature stores and train/serve consistency, leakage-free validation, and hyperparameter tuning | "build a reproducible training pipeline", "our offline model fails in production", "set up a feature store", "is there leakage in this?" |
| [`model-serving-engineer`](agents/model-serving-engineer.md) | Model deployment and serving: online (real-time) vs batch inference, serving infrastructure (containerized endpoints, autoscaling, GPU), low-latency optimization, and safe rollout (shadow, canary, A/B) with the registry as the gate | "deploy this model", "online or batch inference?", "our inference is too slow", "roll out a new model version safely" |
| [`ml-monitoring-engineer`](agents/ml-monitoring-engineer.md) | Production model monitoring: data drift, prediction/concept drift, performance decay (when labels arrive), the retraining trigger, alerting on model health, and closing the loop back to training | "monitor this model in production", "how do we detect drift?", "when should we retrain?", "our model's accuracy is dropping" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Reproducibility is the floor.** Versioned data, code, config, and environment so any model can be rebuilt and explained. A model you can't reproduce is a model you can't debug, audit, or trust.
2. **Training-serving skew is the silent killer.** Features must be computed identically in training and serving — a feature store or shared transformation prevents the skew that makes a 'great' offline model fail in production.
3. **Beware leakage; validate honestly.** No future information, no target leakage, time-aware splits for temporal data. An offline metric inflated by leakage is a production disappointment with a delay.
4. **A model in a notebook is not in production.** Production means a pipeline (train -> register -> serve -> monitor), not a hand-run script. The notebook is where you prototype, not where you ship.
5. **Monitor for drift and decay, with a retraining trigger.** Models rot as the world changes. Monitor input drift, prediction drift, and (when labels arrive) performance; define what triggers retraining before launch.
6. **Is it actually better? Ask the statistician.** Whether a new model's lift is real (not noise) is `applied-statistics`' call; MLOps makes the comparison fair and reproducible.

## 3. Seams (the bridges to neighbouring plugins)

- **'Is this model's improvement statistically real?' and experiment/A-B design** → `applied-statistics`; MLOps makes the comparison fair and reproducible, they judge significance.
- **The data pipelines feeding training/features (batch + streaming)** → `data-platform` / `data-streaming-engineering` / `analytics-engineering`.
- **LLM/RAG/agent applications (prompts, evals, the Claude API/Agent SDK)** → `claude-app-engineering`; this team owns classical/custom-model MLOps.
- **Where models deploy (containers, k8s, cloud GPU)** → `devops-cicd` / `cloud-native-kubernetes` / the cloud plugin.
- **The security/privacy of training data (PII, governance)** → `data-governance-privacy` + `security-engineering`.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer): [`knowledge/ml-engineering-decision-trees.md`](knowledge/ml-engineering-decision-trees.md) (serving online-vs-batch, when-to-retrain, build-vs-buy platform, data-vs-concept drift response, validation split, rollout shadow/canary/direct, retrain automated-vs-human, drift-metric selection + a dated 2026 capability map) and [`knowledge/model-sourcing-and-feature-serving-decision-trees.md`](knowledge/model-sourcing-and-feature-serving-decision-trees.md) (build-vs-fine-tune-vs-prompt model sourcing, and precompute-vs-online feature serving). **Traverse the relevant Mermaid tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (training-serving skew from a split feature source, drift-detection without an actionable trigger, temporal leakage inflating an offline metric, canary rollback of a bad model version). Secondary source; never replaces the knowledge bank or §2's cross-cutting house opinions. The most-likely-to-benefit specialists — `training-pipeline-engineer`, `model-serving-engineer`, `ml-monitoring-engineer` — check the bank when a situation matches.

## 6. Technical-runtime tier — LSP code intelligence (bundled config, binary installed separately)

ML engineering is a **code** domain (overwhelmingly Python), so the plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) giving agents real-time code intelligence — go-to-definition, find-references, diagnostics on training code, feature transforms, serving handlers — instead of grep-and-guess. Verified against the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference) (LSP servers section) and the Pyright docs (2026-06-05); LSP support landed in Claude Code 2.0.74 `[verify-at-use]`.

| Language | Server | `command` | Install (consumer, separate) |
|---|---|---|---|
| Python | Pyright | `pyright-langserver --stdio` | `pip install pyright` **or** `npm install -g pyright` |

**The plugin ships the *config*, not the *binary*.** Per the plugins reference: "LSP plugins configure how Claude Code connects to a language server, but they don't include the server itself." If `pyright-langserver` isn't on `PATH`, it shows `Executable not found in $PATH` in the `/plugin` Errors tab and Python intelligence degrades — Claude Code and all other tools keep working (the same **loud-but-non-fatal** posture as a missing MCP prerequisite). LSP servers start only after the workspace is trusted, and `/reload-plugins` is needed to pick up a config change mid-session.

> **Python-only on purpose.** The marketplace's `backend-engineering` plugin bundles three language servers (Node/Python/Go) because it's language-agnostic; ML engineering is ~entirely Python (training, serving, feature pipelines), so the config is scoped to Pyright to avoid shipping config for languages this plugin's agents don't reason about. The `pyright-langserver --stdio` invocation + install paths are verified against the Pyright installation docs (2026-06-05). Re-confirm the 2.0.74 LSP-support version at use — it is version-volatile.

## 7. Recommended (not bundled) MCP servers — MLflow / tracking-server context

This plugin **bundles no MCP server**, on purpose. Per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**; a write-capable or per-consumer-configured server is **recommend-not-bundle**. Every ML-engineering-useful server fails the zero-config-read-only bar — they all reach a per-instance tracking/registry backend — so we document the recommended `claude mcp add …` path instead of shipping an `mcpServers` entry. **No server was invented; the one below is the official MLflow MCP.**

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **MLflow MCP** (official, ships with MLflow ≥ 3.5.1 — [mlflow.org/docs](https://mlflow.org/docs/latest/genai/mcp/)) | Needs a **consumer-specific `MLFLOW_TRACKING_URI`** (your tracking-server URL — can't hardcode), often **authenticated** (`MLFLOW_TRACKING_USERNAME`/`_PASSWORD`/`_TOKEN` = a secret), and exposes **write/delete registry actions** (register, tag, alias, stage/promote, delete runs/experiments/models) → per-consumer config **and** write-capable **and** secret-handling: all three disqualify bundling. | `claude mcp add mlflow --env MLFLOW_TRACKING_URI=https://your-mlflow.example.com -- uv run --with 'mlflow>=3.5.1' --extra mcp mlflow mcp run` — pass the tracking URI as a **reference/env-var, never a literal**; for a secured server add `MLFLOW_TRACKING_TOKEN` from a vault/env, not inline. The write/promote verbs make this a **`security-reviewer` sign-off** before adoption (least-privilege: prefer a read-only tracking token where the deployment supports it). |

**Why none are bundled (the load-bearing reasoning):** the doctrine's decision table sends "per-consumer config OR write-capable OR first-party-from-the-vendor" to **recommend, don't bundle**. The MLflow MCP is first-party-from-the-vendor, needs a per-instance tracking URI, handles a credential, *and* carries write/delete verbs — it trips four of the recommend-not-bundle conditions at once. The credential additionally invokes the Absolute "reference-not-literal" rule + a `security-reviewer` gate. Community MLflow MCP servers exist (e.g. `mlflow-mcp` on PyPI) but are third-party + same per-instance/write profile — `evaluate-first`, never a default. If a genuinely zero-config, read-only, broadly-useful ML server appears, revisit this with Step 4 of [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md).

> Verified 2026-06-05 (web research): the official MLflow MCP server requires MLflow ≥ 3.5.1 and a `MLFLOW_TRACKING_URI`, supports `MLFLOW_TRACKING_USERNAME`/`_PASSWORD`/`_TOKEN` auth, and exposes write/delete registry+run actions (per mlflow.org/docs/latest/genai/mcp/ and the MLflow MCP listings). The launch command, version floor, and verb set are version-volatile — re-confirm against the MLflow docs at use.

## 8. Runnable tooling (added in the value-add build-out)

- **Drift calculator** — [`scripts/drift_check.py`](scripts/drift_check.py) (stdlib only, Python 3.8+) removes arithmetic error from the recurring monitoring question "has this feature drifted enough to investigate?": `psi` (Population Stability Index on a numerical feature, with the conventional <0.1 / 0.1–0.2 / >0.2 bands + per-bin contributions), `ks` (two-sample Kolmogorov–Smirnov statistic + an approximate critical value), `chi2` (chi-squared on a categorical feature). It is a **calculator, not a monitoring system** — it fetches no data, stores no state, fires no alerts, and decides no retrain; the user supplies both samples and the tool shows the formula and the conventional band. The verdict bands are **conventions/approximations** — whether a measured drift or a downstream performance change is statistically *real* routes to `applied-statistics` (§2 #6), and a drift signal maps to *investigate*, not auto-retrain (see [`best-practices/monitor-drift-and-define-the-trigger.md`](best-practices/monitor-drift-and-define-the-trigger.md)). Owned primarily by `ml-monitoring-engineer`; pairs with the "which drift metric" and "data drift or concept drift" trees in [`knowledge/ml-engineering-decision-trees.md`](knowledge/ml-engineering-decision-trees.md). Ruff-clean.

## Value-add completeness (build-out 2026-06-05)

Disposition of every value-add menu item (built vs. recorded N-A with reason). Context: PR #315 already added the consolidated knowledge decision-trees, `best-practices/`, and `templates/`; this build-out adds the scenarios bank + the runtime tier + a complementing decision-tree file.

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 scenarios (training-serving skew from a split feature source, drift-detection without an actionable trigger, temporal leakage inflating an offline metric, canary rollback of a bad model version) matching the existing `scenarios/README.md` index + 9-field schema. (1 of the 4 pre-existed from #315's groundwork; the other 3 were added here.) |
| 2 | **Decision-tree knowledge (NEW, complementing #315)** | **BUILT** — `knowledge/model-sourcing-and-feature-serving-decision-trees.md`: **build-vs-fine-tune-vs-prompt** (model sourcing) + **precompute-vs-online feature serving**. Chosen because #315's tree file already covers serving online-vs-batch, retrain triggers, build-vs-buy platform, drift response, validation split, rollout, retrain automation, and drift-metric — these two were the genuine gaps (how to *source* the model; how to *compute a feature* at serving time). Grounded in §2 house opinions; dated + `[verify-at-use]`. |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §7. The official MLflow MCP (the real, researched server — not invented) needs a per-instance `MLFLOW_TRACKING_URI`, handles a credential, and is write/delete-capable → fails the zero-config-read-only bar on every axis. Documented the recommended `claude mcp add` path with a `security-reviewer` gate instead. |
| 4 | **LSP server** | **BUILT** — `.lsp.json` (Pyright for Python), wired via `plugin.json` `lspServers`. Genuinely useful for a Python-heavy code domain; binary installs separately (§6). Python-only on purpose (vs. backend-engineering's three) since ML is ~entirely Python. |
| 5 | **Runnable script** | **BUILT** — `scripts/drift_check.py` (PSI / KS / chi-squared drift calculator, stdlib-only, ruff-clean). Real value: removes arithmetic error from the monitoring lane and grounds the drift-metric tree. (§8.) |
| 6 | **bin/ / monitors / output-styles / settings / themes** | **N-A** — no `rc-*` binary clears the rule's "namespace + prefer Bash-tool skills" bar better than the existing advisory hook + skills. A live drift *monitor* would need a per-tenant data connection (a `recommend-not-bundle` MCP/integration concern, not a marketplace artifact); output-styles/themes are UX concerns the §-Output-Contract already governs; the plugin is config-light by design. |
| 7 | **skills/hooks/commands/templates** | **Coverage sufficient** — 5 skills, 4 commands, 4 templates, 1 advisory hook already cover platform design, reproducible training + experiment tracking, feature-store consistency, serving, and monitoring. The new decision-tree file + drift script extend reach without a new agent or skill (team-growth-as-knowledge house rule). |
| 8 | **CHANGELOG.md / NOTICE.md** | **CHANGELOG.md BUILT** — added with a top entry for this build-out. **No `NOTICE.md`** — nothing third-party is bundled (the drift script is original + stdlib-only; the MLflow MCP is *referenced*, not vendored). |
