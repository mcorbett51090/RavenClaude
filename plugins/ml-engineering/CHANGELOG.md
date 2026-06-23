# Changelog — ml-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.4.1] — 2026-06-22

Version bump previously unlogged here; the change that set `0.4.1`:

- Repo review autonomous fixes + B1–B6 deferred items + dead-regex CI guard (#449)

## [0.4.0] — 2026-06-22

Computer-vision value-add — CV deepens the existing MLOps loop as a **sub-domain**, not a separate plugin; no new agent (team-growth-as-knowledge house rule). Additive only; nothing existing removed or changed in a breaking way.

> Recommended version bump: **0.3.0 → 0.4.0** (additive — a new skill, a new knowledge doc, 3 best-practices). Apply the same bump to the `.claude-plugin/marketplace.json` catalog entry (CI fails on version drift); the integrator owns the catalog mirror.

### Added

- **Knowledge — `knowledge/computer-vision-engineering.md`.** Two Mermaid decision trees — (a) **CV task -> architecture** (classification / object detection real-time-vs-accuracy / semantic-vs-instance segmentation / OCR / keypoint) and (b) **inference placement** (cloud batch / on-device edge / edge-opt compile / edge->cloud hybrid / cloud real-time) — plus data & annotation pipeline notes, transfer-learning vs from-scratch, augmentation leakage cautions, evaluation metrics by task (mAP/IoU/Dice/CER/OKS), the scene-vs-frame split trap, the seam back to the core agents, and a dated `[verify-at-use]` 2026 tooling note. Linked from CLAUDE.md §5 alongside the other knowledge docs.
- **Skill — `skills/computer-vision-pipeline/SKILL.md`.** The end-to-end CV lane: data/annotation -> task/architecture choice -> training (transfer-learn first, scene-aware split, augment-after-split) -> eval by task -> serving/edge placement, with the seam back to the training/serving/monitoring/architect agents.
- **Best-practices — 3 one-rule files (22 → 25).** `split-cv-data-by-scene-not-random-frame` (near-duplicate frames leak across a random split), `watch-augmentation-and-label-leakage` (augment train-only-after-split, label-preserving transforms only), `right-size-the-vision-model-for-the-inference-target` (choose/compress for where it runs; re-measure accuracy after every optimization; preprocessing parity). Indexed in `best-practices/README.md`.
- **CLAUDE.md** — a computer-vision MLOps coverage note (top + §5), and the new knowledge doc added to the §5 canonical-knowledge bank.

## [0.3.0] — 2026-06-05

Value-add build-out — completing the full value-add menu against the marketplace recipe. Builds on PR #315 (which added the consolidated knowledge decision-trees, `best-practices/`, and `templates/`). Every menu item is dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)".

> Recommended version bump for this change: **0.2.2 → 0.3.0** (additive — scenarios bank, runtime tier, a new knowledge file; no breaking change). Apply the same bump to the `.claude-plugin/marketplace.json` catalog entry (CI fails on version drift). The build-out left `plugin.json` `version` untouched per the task constraint — the maintainer applies the bump in both mirrors.

### Added

- **scenarios/ bank — 3 net-new field notes (4 total).** `drift-detection-and-retrain-trigger` (a drift dashboard with no threshold-to-action mapping is theater — define the trigger up front, and map a drift signal to *investigate*, not auto-retrain), `temporal-leakage-inflated-offline-metric` (shuffled split on time-ordered data + a label-straddling feature window → AUC 0.97 offline, 0.71 online; the fix lowers the offline number to the honest baseline), `canary-rollback-bad-model-version` (deploy a registry version not a copied file; shadow the breaking change, canary the rest, rehearse the rollback). Join the pre-existing `training-serving-skew-feature-source`; all match the `scenarios/README.md` index + 9-field schema.
- **Decision-tree knowledge — `knowledge/model-sourcing-and-feature-serving-decision-trees.md`.** Two Mermaid trees that complement #315's tree file (which already covered serving online-vs-batch, retrain triggers, build-vs-buy, drift response, validation split, rollout, retrain automation, drift-metric): **build-vs-fine-tune-vs-prompt** (how to source the model) and **precompute-vs-online feature serving** (how a feature reaches the model at serving time). Grounded in the §2 house opinions; dated + `[verify-at-use]`.
- **LSP code-intelligence config.** `.lsp.json` (referenced from `plugin.json` `lspServers`) configuring Pyright for Python — the plugin's near-exclusive language. Ships the config, not the binary; binary installs separately (loud-but-non-fatal if missing). Verified against the Claude Code plugins reference + Pyright docs (2026-06-05).
- **Runnable script — `scripts/drift_check.py`.** A zero-dependency (stdlib-only, Python 3.8+) feature-drift calculator: `psi` (Population Stability Index + conventional bands + per-bin contributions), `ks` (two-sample Kolmogorov–Smirnov + approximate critical value), `chi2` (categorical chi-squared). A calculator, not a monitoring system — no data fetch, no state, no alerts, no retrain decision. Ruff-clean. Owned by `ml-monitoring-engineer`; grounds the drift-metric tree.
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (LSP tier), §7 (recommended-not-bundled MCP — the official MLflow MCP), §8 (runnable tooling), and the value-add completeness disposition table.

### Decisions (recorded, not built)

- **No bundled MCP server.** The official MLflow MCP (researched, not invented) requires a per-instance `MLFLOW_TRACKING_URI`, handles a credential, and is write/delete-capable — it fails the doctrine's zero-config + read-only bar on every axis. Documented the recommended `claude mcp add …` path with a `security-reviewer` gate (and the reference-not-literal credential rule) instead of shipping an `mcpServers` entry. No invented servers.
- **No `bin/`, monitors, output-styles, settings defaults, or themes.** None cleared the "groundable + broadly valuable, doesn't duplicate an existing surface or a per-tenant integration" bar. A live drift *monitor* would need a per-tenant data connection (an MCP/integration concern, not a marketplace artifact).
- **Skills/commands/templates/hooks coverage held sufficient** — 5 skills, 4 commands, 4 templates, 1 advisory hook already cover the surface; the new tree file + drift script extend reach without a new agent (team-growth-as-knowledge house rule).

### Verify-at-use

- LSP support landed in Claude Code 2.0.74; the Pyright install paths (`pip install pyright` / `npm install -g pyright`) and the `pyright-langserver --stdio` invocation. The MLflow MCP version floor (≥ 3.5.1), launch command (`uv run --with 'mlflow>=3.5.1' --extra mcp mlflow mcp run`), env-var names, and verb set. All version-volatile — re-confirm against the vendor before quoting.

## [0.2.x] — earlier

4-agent ML-engineering (MLOps) team (ml-platform-architect, training-pipeline-engineer, model-serving-engineer, ml-monitoring-engineer): 5 skills, the consolidated decision-tree knowledge bank, 12 best-practices, 4 templates, 4 commands, 1 advisory hook (PR #315 added the consolidated trees + best-practices/ + templates/). Seams to applied-statistics, data-platform/data-streaming-engineering, claude-app-engineering, devops-cicd/cloud-native-kubernetes, data-governance-privacy.
