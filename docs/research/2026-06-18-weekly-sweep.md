# Weekly research sweep — 2026-06-18

**Cadence:** Tier-A news sweep ([`docs/research-routine-two-cadence.md`](../research-routine-two-cadence.md)). Scoped to the ~28 vendor-API-anchored plugins in [`.ravenclaude/plugins/sweep-tiers.yaml`](../../.ravenclaude/plugins/sweep-tiers.yaml); Tier-B methodology verticals were **not** swept for news (honest-by-construction).

**Method:** five parallel cluster research agents (AI/Claude tooling · Microsoft stack · cloud/infra · data/BI · web/security) read each plugin's knowledge files, extracted dated/volatile claims, and re-verified the most volatile against primary sources. Every finding below was then **independently re-verified by the editing session** (not trusted from the subagent) before any edit — the accuracy discipline's "cite the this-session check" bar.

## Honest nulls (no net-new this week)

- **cloud/infra** — terraform-iac, cloud-native-kubernetes, devops-cicd, observability-sre, platform-engineering-idp: 0 corrections. K8s 1.36 "Haru" / userns-GA, Terraform 1.15.6 / OpenTofu 1.12.2 version-floors, OTel status all still accurate.
- **data/BI** — data-platform, database-engineering, analytics-engineering, data-streaming-engineering, tableau: 0 corrections (dbt v2.0-alpha/Fusion, PG18-GA, RDS Extended-Support Yr-3 doubling all verified still-true). One non-urgent advisory: data-streaming-engineering's Flink "1.19" / Kafka-Streams "3.7" *verified-against* strings are behind current (Flink 2.2 / Kafka 4.3) but the cited semantics are unchanged — not a correction; left for a routine refresh.
- **web** — web-design, frontend-engineering: 0 corrections (Core Web Vitals LCP 2.5s/INP 200ms/CLS 0.1, WCAG 2.2, RSC-in-Next all current). **Learn-tab pass: 0 net-new concept candidates** (CSS Anchor Positioning + same-document View Transitions reaching Baseline are capability-map facts, not durable concept cards).
- **MS stack** — power-platform, microsoft-365-copilot (declarative-agent 50/25/4096/45s wall + schema v1.7), microsoft-graph: 0 corrections.
- **security/identity** — auth-identity (OAuth 2.1 still IETF draft, NIST 800-63B-4), cybersecurity-grc (NIST CSF 2.0, no 3.0): 0 corrections.

## Findings that passed review (5)

| # | Plugin(s) | Class | Summary | Primary source (re-verified 2026-06-18) |
|---|---|---|---|---|
| F1 | claude-app-engineering + ai-coding-model-guidance | **Correction (high)** | **Fable 5 / Mythos 5 SUSPENDED 2026-06-12** — Anthropic disabled all public access per a US export-control directive; Opus 4.8 unaffected. Repo presented Fable 5 as live GA flagship + routing/advisor target. | [Anthropic statement](https://www.anthropic.com/news/fable-mythos-access), CNBC, Fortune, Al Jazeera |
| F2 | microsoft-fabric | Correction (low) | Runtime 1.3 is Spark 3.5.5 / **Delta 3.2** (was documented Delta 3.1). | MS-Learn [runtime-1-3](https://learn.microsoft.com/fabric/data-engineering/runtime-1-3) |
| F3 | microsoft-fabric | Addition (low) | Runtime 1.3 **EOS 2026-09-30**, LTS through March 2027 (it's the production default). | MS-Learn [lifecycle](https://learn.microsoft.com/fabric/data-engineering/lifecycle) |
| F4 | ai-coding-model-guidance | Addition (low) | **Grok Build** confirmed: model `grok-build-0.1` (256K, $1/$2 per Mtok), public beta. Upgraded an `[unverified]` rider to a cited entry. | [x.ai/news](https://x.ai/news/grok-build-0-1), [docs.x.ai](https://docs.x.ai/developers/models/grok-build-0.1) |
| F5 | security-engineering | Correction (low) | **OWASP Top 10:2025** is current (2021 superseded); new A03 Software Supply Chain Failures + A10 Mishandling of Exceptional Conditions; SCA remapped A06→A03:2025. | [owasp.org/Top10/2025](https://owasp.org/Top10/2025/) |

## Expert-panel evaluation

**Panel 1 — Usefulness/triage** (Maintainer · Domain-accuracy · Signal-vs-noise seats): **all five USEFUL**, none dropped. F1 ranked the marquee item (two-plugin, actively-misleading correction); F2+F3 bundled as one micro-edit on one row; F4 matures an existing `[unverified]` rider; corrections-over-additions discipline honored (3 of 5 are corrections, the lone standalone addition F3 rides F2's edit at zero marginal blast).

**Panel 2 — Detailed change-review** (Knowledge-file-editor · Consumer-impact · Cross-file-consistency seats): **all five APPROVE-WITH-CHANGES**. Binding changes applied this session:
- Every SUSPENDED/changed marker carries an inline primary-source citation + ISO date (the unanimous cross-seat requirement).
- All edited files' `Last reviewed:` stamps bumped to 2026-06-18.
- F1 coverage widened beyond the proposal to the L5 provenance line, the Opus-4.8 "safety-fallback target" framing (L12), the whole Copilot bullet (not just the pricing window), and the **advisor pairing** re-point to Opus 4.8.
- F4 promoted into the Grok **table** (not just a bullet) for closed-world + citation-gate coherence; "confirmed" wording only shipped after the editor's own x.ai fetch this session. `check-lineup-citations.py` re-run → OK.
- **Migration note** added to claude-app-engineering (a flagship-routing flip changes recommended behavior on `/plugin marketplace update`); F2–F5 are factual/advisory and need none.

**Panel 3 — Tiebreak:** not triggered. Panels 1 and 2 concurred on every finding (USEFUL + APPROVE), so no disagreement required escalation.

## Changes shipped

- claude-app-engineering `0.9.0 → 0.9.1`
- ai-coding-model-guidance `0.3.4 → 0.3.5`
- microsoft-fabric `0.8.1 → 0.8.2`
- security-engineering `0.3.0 → 0.3.1`
- marketplace catalog `0.86.0 → 0.87.0`

Each version bumped in both `plugin.json` and `marketplace.json`; per-plugin CHANGELOGs updated. Gates run pre-push: JSON validity, version-parity, `prettier --check .` (exit 0), `check-lineup-citations.py` (OK).
