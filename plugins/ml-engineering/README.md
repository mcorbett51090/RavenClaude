# ML Engineering (MLOps)

The **ml-engineering** plugin — taking ML models to production and keeping them healthy — reproducible training pipelines and experiment tracking, feature stores and training/serving consistency, model serving and deployment, and monitoring for drift and decay.

## Agents

- **`ml-platform-architect`** — MLOps architecture: build-vs-buy of the ML platform, the train->register->serve->monitor loop, stack selection (tracking/registry/orchestration/serving), reproducibility strategy, and the team's ML maturity path
- **`training-pipeline-engineer`** — Reproducible training: pipelines (data prep -> train -> evaluate -> register), experiment tracking, the model registry, feature stores and train/serve consistency, leakage-free validation, and hyperparameter tuning
- **`model-serving-engineer`** — Model deployment and serving: online (real-time) vs batch inference, serving infrastructure (containerized endpoints, autoscaling, GPU), low-latency optimization, and safe rollout (shadow, canary, A/B) with the registry as the gate
- **`ml-monitoring-engineer`** — Production model monitoring: data drift, prediction/concept drift, performance decay (when labels arrive), the retraining trigger, alerting on model health, and closing the loop back to training

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ml-engineering@ravenclaude
```

## Seams

- **'Is this model's improvement statistically real?' and experiment/A-B design** → `applied-statistics`; MLOps makes the comparison fair and reproducible, they judge significance.
- **The data pipelines feeding training/features (batch + streaming)** → `data-platform` / `data-streaming-engineering` / `analytics-engineering`.
- **LLM/RAG/agent applications (prompts, evals, the Claude API/Agent SDK)** → `claude-app-engineering`; this team owns classical/custom-model MLOps.
- **Where models deploy (containers, k8s, cloud GPU)** → `devops-cicd` / `cloud-native-kubernetes` / the cloud plugin.
- **The security/privacy of training data (PII, governance)** → `data-governance-privacy` + `security-engineering`.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
