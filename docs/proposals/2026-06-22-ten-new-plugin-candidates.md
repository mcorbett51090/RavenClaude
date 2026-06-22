# Ten new-plugin candidates for RavenClaude — research, prioritization, and build status (2026-06-22)

> **Date:** 2026-06-22 · **Author:** Claude Code (autonomous routine) · **Status:** research + one initial build
>
> Task: research and identify 10 plugins **not yet implemented**, prioritize by user demand × technical feasibility, and build out the highest-priority first. This doc is the research deliverable; the build (`plugins/cli-tooling-engineering/`) ships alongside it.

> **Update (2026-06-22, post-merge reconciliation):** while this PR (#464) was open, parallel routine runs merged **many of the candidates below to `main`** — `browser-extension-engineering` (#435), `email-engineering` (#427), `data-orchestration` (#460), `developer-relations` (#431/#448), `trust-and-safety` (#444), and `geospatial-engineering` (#444), among ~14 new plugins (catalog now 116→117). On merge I verified that **`cli-tooling-engineering` is still a distinct, unowned gap** — the newly-added `developer-tooling` plugin is the **build-systems/monorepo** layer (Nx/Turborepo/Bazel/caching), not the CLI/TUI-building lane — so it correctly ships as a new plugin here. The candidate table below is the **state as researched**; the "scoped/unbuilt" labels on the parallel-built rows are now historical. The durable takeaway stands: this routine keeps re-deriving the same roadmap in parallel — **retune it to read the live roster + pick the next genuinely-unbuilt gap** to stop the collisions.

## How this run relates to the prior passes (read first)

This is a **recurring routine**. It has run before, and the marketplace has a **standing decision** the routine must respect:

- **2026-06-09 / 06-10:** role/business-heavy candidate passes; each built exactly one plugin (`engineering-management`, `sales-engineering`).
- **2026-06-11 (#409):** three speculative P0 plugins (`developer-relations`, `higher-education-administration`, `physical-therapy-practice`) were scaffolded to gate-passing standard, then **deliberately parked, not merged** — the documented rationale is **proof-of-craft + build-on-real-demand over catalog breadth** (the marketplace is already ~100 plugins; see `docs/plugin-candidates-2026-06.md` and `docs/idea-board.md`).
- **2026-06-12 (#421):** an app-craft/technical lens; built the #1 pick (`desktop-app-engineering`) + a 10-candidate roadmap (`docs/proposals/2026-06-12-ten-new-plugin-candidates.md`).

**The established, accepted output of this routine is therefore: build the single highest-priority _unbuilt_ gap to full gate-passing quality + refresh the prioritized roadmap — NOT ship 10 speculative shells** (that would fail the frontmatter/scenario gates and dilute the catalog, and it contradicts the parked-#409 decision). This run continues the #421 app-craft roadmap by building its **#2** pick.

## Coverage map (what already ships, so we don't duplicate)

- **App craft:** backend / frontend / mobile / **desktop-app (new, #421)** / api / database / auth-identity — **the remaining structural gap is no _CLI/TUI_ sibling.**
- **Platform & ops:** devops-cicd, cloud-native-kubernetes, terraform-iac, observability-sre, platform-engineering-idp, performance-engineering, finops-cloud-cost, qa-test-automation, security-engineering, cybersecurity-grc.
- **Cloud:** aws / azure / gcp.
- **Data & AI:** data-platform, analytics-engineering, data-streaming, ml-engineering, ai-rag-engineering, data-science-research, applied-statistics, data-governance-privacy, microsoft-fabric, tableau — **gaps: no batch-pipeline _orchestration_ owner (Airflow/Dagster/Prefect); no _computer-vision_ owner.**
- **Specialized eng:** blockchain-web3, embedded-iot, game-development, accessibility-engineering, localization-i18n, search-relevance, experimentation-growth — **gaps: browser extensions, realtime-collaboration, email infra.**
- **Business / verticals:** ~60 plugins (finance, fintech-payments, product/project management, sales, marketing-ops, plus ~50 industry verticals). Business-side carry-overs (developer-relations, GIS, trust-and-safety, IR, M&A, content-SEO, etc.) remain documented in the 06-09/06-10/06-12 passes and are **held pending real demand** per the #409 decision.

## The 10 candidates (prioritized)

Scoring: **Demand** (how often a real practitioner needs this) × **Feasibility** (durable craft, not volatile facts that rot) × **Disjoint** (low overlap with an existing plugin). 1–5 each; Priority = sum. This list carries forward the #421 roadmap, advancing the built one and re-ranking the rest.

| # | Candidate | Demand | Feas. | Disjoint | Priority | Closest existing → seam |
|---|---|---|---|---|---|---|
| 1 | **cli-tooling-engineering** ✅ *(built here)* | 4 | 5 | 5 | 14 | backend/devops → owns building _CLIs/TUIs_: command/flag surface, config precedence, output + exit-code contract, stdin/TTY/signals, completions, single-binary distribution |
| 2 | **browser-extension-engineering** | 4 | 4 | 5 | 13 | frontend → owns MV3 extensions: service worker, content-script isolation, message passing, permission minimization, store review |
| 3 | **realtime-collaboration-engineering** | 4 | 4 | 5 | 13 | frontend/backend → owns multiplayer/collab: CRDT vs OT, WebSocket/WebRTC transport, presence/awareness, offline merge |
| 4 | **data-engineering-orchestration** | 4 | 4 | 4 | 12 | analytics-engineering (dbt) / data-streaming (Kafka) / data-platform (ELT) → owns batch **orchestration** (Airflow/Dagster/Prefect): DAGs, idempotent backfills, retries/SLAs, lineage |
| 5 | **email-deliverability-engineering** | 4 | 4 | 4 | 12 | marketing-operations / backend → owns sending infra: SPF/DKIM/DMARC/BIMI, ESP integration, warmup, bounce/complaint handling, inbox placement |
| 6 | **computer-vision-engineering** | 3 | 4 | 4 | 11 | ml-engineering (generic MLOps) → owns the CV craft: detection/segmentation/OCR, annotation/dataset hygiene, augmentation, edge/realtime inference |
| 7 | **developer-relations** *(carry-over, unbuilt)* | 4 | 4 | 4 | 12 | technical-writing-docs / marketing-operations → advocacy, quickstart/sample-app craft, talks/CFPs, community health, DevRel funnel |
| 8 | **gis-geospatial-engineering** *(carry-over, unbuilt)* | 3 | 3 | 5 | 11 | data-platform / database-engineering → PostGIS, CRS/projections, vector/raster pipelines, tiling, routing |
| 9 | **trust-and-safety-engineering** *(carry-over, unbuilt)* | 3 | 4 | 4 | 11 | security-engineering / data-governance-privacy → moderation, abuse/fraud detection, policy taxonomy, reviewer tooling, T&S metrics |
| 10 | **accessibility-of-native-apps** *(stretch)* | 3 | 3 | 4 | 10 | accessibility-engineering (web/WCAG) → native a11y APIs (UIA / AX / AccessKit) for desktop + TUI; pairs with #1 and desktop-app |

### Per-candidate brief — purpose, approach, dependencies

**1. cli-tooling-engineering** — The command-line sibling the app-craft cluster was missing. *Purpose:* build CLIs and TUIs that feel native to the shell — the command/subcommand + flag/positional surface, config precedence (flags > env > file > default), the output contract (human by default, `--json` on demand, data→stdout/diagnostics→stderr, exit codes as an API, NO_COLOR/TTY detection), reading stdin, signal handling, TUIs (Ink/Bubble Tea/Textual/ratatui) with a non-TTY fallback, shell completions, and distribution (single static binary, Homebrew/Scoop/winget/npm/pipx, a `--version` + update path). *Approach:* 4 agents (cli-architect, cli-implementation-engineer, tui-engineer, cli-distribution-engineer), 5 skills, a decision-tree knowledge bank (command-surface + output/exit-code + framework-choice + distribution trees + a dated 2026 capability map), 12 best-practices, 4 templates, 4 commands, 1 advisory hook, a 3-scenario bank, `.lsp.json` (TS + Rust + Go + Python). *Deps:* ravenclaude-core; seams to backend-engineering (the logic the CLI drives), devops-cicd (CI release/signing), desktop-app-engineering (the GUI sibling), technical-writing-docs (man pages). **← built in this PR.**

**2. browser-extension-engineering** — Manifest V3 extensions across Chrome/Edge/Firefox/Safari: the MV3 service-worker model, content-script isolation + the DOM boundary, `chrome.runtime` message passing, permission/host-permission minimization, storage + sync, and the store review/publishing pipeline. *Approach:* 3 agents (extension-architect, extension-implementation-engineer, extension-store-and-review-specialist). *Deps:* frontend-engineering, auth-identity, security-engineering.

**3. realtime-collaboration-engineering** — Multiplayer/collaborative editing (Figma/Notion-style): CRDT vs OT by merge cost, transport (WebSocket vs WebRTC, SFU vs mesh), presence/awareness, offline reconciliation, the sync server. *Approach:* 3 agents (collab-architect, sync-engine-engineer, presence-and-transport-engineer). *Deps:* frontend-engineering, backend-engineering, data-streaming.

**4. data-engineering-orchestration** — The batch-orchestration lane no plugin owns: DAG/asset modeling, idempotent + backfillable tasks, retries/SLAs/alerting, sensors vs schedules, lineage, the Airflow-vs-Dagster-vs-Prefect choice. *Approach:* 3 agents (orchestration-architect, pipeline-dag-engineer, data-reliability-engineer). *Deps:* analytics-engineering, data-platform, data-streaming. *Risk:* volatile vendor facts — date them.

**5. email-deliverability-engineering** — Transactional + lifecycle email infra: SPF/DKIM/DMARC/BIMI, the ESP/relay choice, IP/domain warmup, list hygiene + bounce/complaint handling, template/MIME craft, inbox-placement monitoring. *Approach:* 3 agents (email-infra-architect, deliverability-engineer, email-template-engineer). *Deps:* marketing-operations, backend-engineering, data-governance-privacy. *Risk:* ESP/deliverability specifics are volatile.

**6. computer-vision-engineering** — The CV specialization `ml-engineering` is too generic for: task framing (classification/detection/segmentation/OCR/pose), annotation + dataset hygiene, augmentation, transfer learning, evaluation (mAP/IoU), edge/realtime inference (ONNX/TensorRT/CoreML). *Approach:* 3 agents (cv-architect, vision-model-engineer, edge-inference-engineer). *Deps:* ml-engineering, data-platform. *Risk:* model/tooling facts volatile.

**7. developer-relations** *(carry-over)* — Advocacy, quickstart/sample-app engineering, talks/CFPs, community health, DevRel funnel metrics. *Deps:* technical-writing-docs, marketing-operations, api-engineering. **Held pending real demand** (parked #409).

**8. gis-geospatial-engineering** *(carry-over)* — PostGIS spatial indexing, CRS/projections, vector/raster pipelines, tiling, routing, map rendering. *Deps:* data-platform, database-engineering. *Risk:* volatile tool facts.

**9. trust-and-safety-engineering** *(carry-over)* — Content moderation, abuse/fraud detection, policy taxonomy, reviewer tooling, T&S metrics. *Deps:* security-engineering, data-governance-privacy.

**10. accessibility-of-native-apps** *(stretch)* — Native accessibility APIs (Windows UI Automation, macOS AX, AccessKit) for desktop apps + TUIs, distinct from `accessibility-engineering`'s web/WCAG lane. *Deps:* accessibility-engineering, desktop-app-engineering, cli-tooling-engineering.

## Prioritization rationale

- **#1 cli-tooling-engineering** is the highest-value, lowest-risk build now: it closes the **last structural hole in the app-craft cluster** (backend/frontend/mobile/desktop/api/database/auth all exist — the CLI/TUI runtime was the remaining sibling), demand is high (nearly every engineering team ships an internal CLI), and feasibility is maximal — the craft is **durable** (the output/exit-code contract, stdin/TTY discipline, config precedence, and distribution mechanics are evergreen; only the framework version-map is dated `[verify-at-use]`). Its seams are clean (logic → backend, CI signing → devops, the GUI sibling → desktop-app). It directly mirrors the proven `desktop-app-engineering`/`mobile-engineering` recipe.
- **#2 browser-extension, #3 realtime-collaboration** are the next tier: durable craft, genuinely unowned lanes, clean seams.
- **#4 orchestration, #5 email-deliverability, #6 computer-vision** carry more volatile vendor/model facts → dated, re-verify-at-use knowledge.
- **#7–#10** are carry-overs/stretch — real and valuable, but business-side carry-overs are **held pending real demand** per the standing #409 decision, and the stretch entry pairs with already-built plugins.

## Build status (this PR)

- **#1 cli-tooling-engineering — BUILT.** Full plugin to the marketplace quality bar: 4 agents (scenario-schema complete, each description ≤300 chars), 5 skills + 4 commands, a decision-tree knowledge bank (command-surface + output/exit-code + framework-choice + distribution Mermaid trees + a config-precedence prior + a dated 2026 capability map), 12 best-practice rules, 4 templates, a 3-scenario bank, 1 advisory anti-pattern hook, `.lsp.json` (TS + Rust + Go + Python), README + CLAUDE.md + CHANGELOG. Registered in `.claude-plugin/marketplace.json` (catalog 0.86.0 → 0.87.0), the `docs/architecture.md` roster, and README (101 → 102 plugins). Globs already covered by `.repo-layout.json` (`plugins/*/**`).
- **#2–#10 — SCOPED, NOT YET BUILT.** Each existing plugin is ~35–45 files of cited, CI-gated content. Building all ten to the depth bar in one pass would fail the frontmatter/scenario gates and dilute the marketplace — the documented anti-pattern. One complete, gate-passing plugin plus this fully-scoped, prioritized roadmap is the higher-value deliverable; the remaining nine are ready to build in priority order (business-side carry-overs awaiting real demand per the #409 decision).

## Blockers / notes

- **No technical blockers** were hit building #1 — git, the layout gate, the frontmatter gate (incl. the 300-char agent cap), and the marketplace-claims structural gate are all green locally (see the PR description for the gate run).
- The only real constraint is **breadth vs depth** (and the standing **build-on-real-demand** policy): ten shallow plugins would fail gates and dilute the catalog, and shipping speculative plugins contradicts the parked-#409 decision. The responsible deliverable is one excellent plugin in the cleanest remaining structural gap + this roadmap.
