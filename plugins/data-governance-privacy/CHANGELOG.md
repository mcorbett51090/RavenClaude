# Changelog — data-governance-privacy

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.0] — 2026-06-05

Value-add build-out against the full marketplace menu — adds the scenarios bank, two new topic-specific Mermaid decision-tree knowledge files, and a runnable governance scoring helper; honestly dispositions the code-runtime tier (MCP/LSP/bin/monitors/styles) as N-A for an advisory governance domain. Builds on PR #315's consolidated decision-trees + best-practices + templates.

- **Scenarios bank** (`scenarios/`) — **4** dated, scope-tagged engagement scenarios populating the existing README index (mirrors the marketplace 9-field schema; `product_version: "n/a"` for an advisory vertical; **no real PII** per the plugin's privacy boundary):
  - `2026-06-05-dsar-erasure-at-scale.md` — erasure fan-out across 7 copies, lineage-first, retention carve-out (high confidence).
  - `2026-06-05-pii-discovery-in-the-warehouse.md` — automated discovery + classification + tag-propagation-by-lineage; the derived/copied-PII trap (high confidence).
  - `2026-06-05-cross-border-transfer-gap.md` — SCC/adequacy/DPF gap, the sub-processor chain leg (medium confidence).
  - `2026-06-05-consent-purpose-limitation-drift.md` — consent-as-system-of-record, revocation propagation, ML-training purpose drift (medium confidence).
  Each carries an "Action for the next engineer" lesson and cited, dated authoritative sources (gdpr-info, EDPB, EU Commission, OpenMetadata/Atlas).
- **2 new Mermaid decision-tree knowledge files** complementing PR #315's `data-governance-privacy-decision-trees.md` (which already covered classification / DSR / anonymize-vs-pseudonymize / lawful-basis-on-record / deletion / access / maturity / anonymization-technique):
  - `dgp-lawful-basis-decision-tree.md` — GDPR Art. 6 lawful-basis *selection* (which of the six + the Art. 9 special-category path + what to engineer per basis). Distinguished from #315's "is a basis already on record?" tree.
  - `dgp-transfer-mechanism-decision-tree.md` — GDPR Chapter V transfer-mechanism choice (adequacy / DPF-certified / SCCs+TIA / BCRs / Art. 49 derogation) traversed **per leg, including the sub-processor chain**.
  Both grounded + cited + dated; adequacy/DPF status carries inline `[verify-at-use]` because it is politically volatile.
- **Runnable scoring helper** `scripts/pii_risk_score.py` (stdlib only, Python 3.8+, ruff-clean) — three modes: `classify` (asset → sensitivity tier from observable signals), `dpia-threshold` (GDPR Art. 35 high-risk-indicator screen → DPIA-likely-warranted signal), `reident` (re-identification-risk screen; a held key → pseudonymized → still personal data). **No legal advice baked in** — every output is a triage/prioritization signal that routes the legal determination to the DPO/legal/`regulatory-compliance` (CLAUDE.md §2 #6).

### Honestly N-A for an advisory governance domain (documented, not forced)
The code-runtime tier (code-aware/bundled MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a privacy/governance advisory domain — there is no source language to index and no zero-config read-only governance MCP to bundle. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". The one runtime item with real non-code value — a runnable scoring helper — **was** built.

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**`, `plugins/*/scripts/**`, `plugins/*/knowledge/**`, `plugins/*/CHANGELOG.md` — **no new globs needed**.
- `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` `version` bump `0.2.2` → `0.3.0` (both mirrors).

## [0.2.x] — prior

3 agents (`data-governance-architect`, `privacy-compliance-engineer`, `data-catalog-lineage-engineer`), 5 skills, 4 commands, 1 advisory hook, a consolidated decision-tree knowledge bank, 12 best-practices, and 4 templates (PR #315 consolidated the knowledge/best-practices/templates tier). The engineering of governance — catalog + lineage, classification, privacy mechanics (DSR / consent / minimization / retention / pseudonymization-vs-anonymization), and access governance — not legal advice.
