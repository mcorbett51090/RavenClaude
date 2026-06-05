# Data Governance & Privacy Plugin — Team Constitution

> Team constitution for the `data-governance-privacy` Claude Code plugin — **3** specialist agents for making data discoverable, trustworthy, and lawfully used — a data catalog with lineage, classification of sensitive data and PII, privacy mechanics (GDPR/CCPA subject rights, consent, minimization), and access governance/DLP — the engineering of governance, not legal advice. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`data-governance-architect`](agents/data-governance-architect.md) | The governance operating model: data ownership and stewardship, the classification scheme (public/internal/confidential/restricted + PII tagging), governance policies, the council/RACI, and the maturity roadmap | "set up data governance", "who owns this data?", "design our classification scheme", "we have no governance, where do we start?" |
| [`privacy-compliance-engineer`](agents/privacy-compliance-engineer.md) | Privacy mechanics as engineering: data-subject rights (access/erasure/portability) pipelines, consent + lawful-basis tracking, data minimization, retention/deletion automation, and pseudonymization vs anonymization | "build a data-subject-request pipeline", "track consent properly", "automate retention/deletion", "is this anonymized or pseudonymized?" |
| [`data-catalog-lineage-engineer`](agents/data-catalog-lineage-engineer.md) | The data catalog and lineage: sensitive-data/PII discovery and tagging, automated lineage capture, business glossary, metadata management, and access governance/DLP at the data layer | "set up a data catalog", "discover where PII lives", "trace this data's lineage", "who has access to this sensitive data?" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **You can't govern what you can't find.** A catalog with lineage and sensitive-data discovery comes first; policy on un-inventoried data is theater. Classification precedes control.
2. **Privacy by design and by default.** Minimize what you collect, restrict by default, and bake privacy into the data model — don't collect-everything-and-restrict-later. The cheapest PII to protect is the PII you didn't collect.
3. **Know your lawful basis and honor consent.** Every use of personal data has a stated lawful basis; consent (where it's the basis) is granular, recorded, and revocable. Using data beyond its basis is a violation, not a feature.
4. **Data-subject rights are an engineered capability.** Access, erasure, and portability must be executable across every system that holds the person's data — which requires the catalog/lineage to even find it. 'We can't locate all their data' is a failed DSR.
5. **Anonymization is a high bar; pseudonymization isn't anonymization.** Truly anonymized data is out of scope of privacy law; pseudonymized (re-identifiable with a key) is still personal data. Don't conflate them — most 'anonymized' data isn't.
6. **This is governance engineering, not legal advice.** We build the catalog, the DSR pipeline, the classification, and the controls; the legal interpretation and financial-regulatory specifics route out.

## 3. Seams (the bridges to neighbouring plugins)

- **Financial-regulatory obligations (AML/KYC, regulator reporting, jurisdiction-specific rules)** → `regulatory-compliance`; this team does general data governance/privacy engineering, not financial-regulatory.
- **Warehouse row-/column-level security and masking implementation** → `data-platform` (RLS/embed-JWT) and the warehouse; we set the classification + policy they enforce.
- **Microsoft Purview / data governance inside Fabric** → `microsoft-fabric`; we're the tool-neutral governance lane.
- **The security verdict, DLP enforcement, and breach response** → `security-engineering` → `ravenclaude-core/security-reviewer`.
- **Lawful interpretation / contracts / DPAs** → route to legal (out of marketplace scope); we engineer the capability, not the legal opinion.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer) — [`knowledge/data-governance-privacy-decision-trees.md`](knowledge/data-governance-privacy-decision-trees.md) (classification / DSR-handling / anonymize-vs-pseudonymize / lawful-basis-on-record / deletion / access / governance-maturity / anonymization-technique trees + the dated 2026 capability map), plus two topic-specific trees that **complement** it: [`knowledge/dgp-lawful-basis-decision-tree.md`](knowledge/dgp-lawful-basis-decision-tree.md) (GDPR Art. 6 lawful-basis *selection*) and [`knowledge/dgp-transfer-mechanism-decision-tree.md`](knowledge/dgp-transfer-mechanism-decision-tree.md) (Chapter V transfer-mechanism choice, per leg). **Traverse the relevant Mermaid tree top-to-bottom before choosing.** Every regulatory fact is dated; adequacy/DPF status carries `[verify-at-use]` (privacy law varies by jurisdiction and is volatile — §2).
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble) — [`scenarios/`](scenarios/): DSAR erasure at scale, PII discovery in the warehouse, cross-border transfer gap, consent/purpose-limitation drift. Secondary source; never replaces the knowledge bank. **Scenarios carry no real PII** (the plugin's privacy boundary — they describe the engineering pattern, never the data). The most-likely-to-benefit specialists check the bank when a situation matches.

## 6. Runnable scoring helper (`scripts/pii_risk_score.py`)

A stdlib-only (Python 3.8+) scoring helper that turns the signals a steward *observes* into a transparent, repeatable triage signal: `classify` (asset → sensitivity tier), `dpia-threshold` (GDPR Art. 35 high-risk-indicator screen → DPIA-likely-warranted signal), `reident` (re-identification-risk screen; a held key → pseudonymized → still personal data). It is a **scoring helper, not a data source and not legal advice** — the user supplies every signal; outputs are prioritization/triage signals, and **every legal determination routes to the DPO / legal / `regulatory-compliance`** (§2 #6). Owned primarily by `privacy-compliance-engineer` (`dpia-threshold`, `reident`) and `data-governance-architect` (`classify`); pairs with the classification / DPIA / anonymization trees.

## 7. Value-add completeness (build-out 2026-06-05)

Disposition of every value-add menu item (built vs. recorded N-A with reason). This build-out's net-new contribution on top of PR #315's consolidated knowledge/best-practices/templates tier:

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 dated, scope-tagged engagement scenarios (DSAR erasure at scale, PII discovery in the warehouse, cross-border transfer gap, consent/purpose-limitation drift) populating the existing `scenarios/README.md` index + 9-field schema. No real PII (plugin privacy boundary). |
| 2 | **Decision-tree knowledge** | **BUILT** — 2 new topic-specific Mermaid trees complementing #315's: `dgp-lawful-basis-decision-tree.md` (Art. 6 basis *selection* — distinct from #315's "basis already on record?") + `dgp-transfer-mechanism-decision-tree.md` (Chapter V choice, per leg incl. sub-processor chain). Grounded, cited, dated; volatile facts marked `[verify-at-use]`. |
| 3 | **Runnable script (`scripts/`)** | **BUILT** — `pii_risk_score.py` (stdlib, ruff-clean): `classify` / `dpia-threshold` / `reident`. Real non-code value, like the vertical calculators; no legal advice baked in (every output routes the determination to legal). |
| 4 | **Bundled / code-aware MCP server** | **N-A (recommend-not-bundle)** — no zero-config, read-only governance MCP server verified to exist; data catalogs (OpenMetadata/DataHub/Atlas) and DSR platforms are **per-tenant, authenticated, write-capable** and PII-bearing → both disqualify bundling per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md). If a live-catalog need ever surfaces it is *recommend, evaluate-first* through `ravenclaude-core/security-reviewer`, never bundled. No invented servers. |
| 5 | **LSP server** | **N-A** — LSP is a code-editing protocol; a privacy/governance *advisory* domain has no source language to index. (Contrast `backend-engineering`, a code domain that ships `.lsp.json`.) |
| 6 | **bin/ executables** | **N-A** — the single stdlib `scripts/pii_risk_score.py` covers the runtime need; no compiled/installed binary warranted, and an `rc-*` namespace script would duplicate the advisory hook + skills. |
| 7 | **Monitors / background jobs** | **N-A** — nothing to watch; no build, repo, or long-running process in an advisory domain. (Discovery *cadence* is an engineering recommendation in `best-practices/automate-discovery-and-keep-it-current.md`, not a marketplace monitor.) |
| 8 | **output-styles / themes** | **N-A** — deliverables are Markdown governance reports governed by the agents' Output Contract; output styling is a code/UX concern. |
| 9 | **settings.json / permissions tuning** | **N-A** — no tool-permission surface specific to this vertical beyond what `ravenclaude-core` (and the Thing's `file_read_global` secret-deny floor) already provide. |
| 10 | **skills / hooks / commands / templates** | **SUFFICIENT** — 5 skills, 1 advisory anti-pattern hook, 4 commands, 4 templates already cover classification, catalog/lineage, privacy mechanics, retention/deletion, and access governance. The new scenarios + 2 trees + script extend reach without a new agent (team-growth-as-knowledge house rule). No clear gap this round. |
| 11 | **CHANGELOG.md** | **BUILT** — added with a top `0.3.0` entry. |
| 12 | **NOTICE.md** | **N-A** — nothing third-party is bundled; `pii_risk_score.py` is original + stdlib-only, and all sources are cited inline, not vendored. |
