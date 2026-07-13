# Plugin news-research + panel review — 2026-07-13

Scheduled routine: research recent news per active plugin, evaluate findings through expert panels, ship a PR for anything that survives.

## Scope decision

154 active plugins — no "active" subset distinguishes them. A genuine deep-research + multi-panel + implementation pass across all 154 in one unattended run is neither feasible nor wise, and the repo's accuracy discipline forbids baking unverified "news" into plugin content. Scoped to the **AI/Claude-adjacent plugins** (fastest-moving, most relevant to this Claude-tooling marketplace, and where claims are web-verifiable): `ai-coding-model-guidance`, `claude-app-engineering`, `ai-rag-engineering`, `llm-evaluation-engineering`, `ai-red-teaming`.

**Key structural finding:** these plugins are deliberately **methodology-first** and carry explicit anti-volatility discipline (`closed-world-verified-lineup-only`, `date-and-source any model id — never quote from memory`, `volatile-numbers-carry-a-marker`). They are also actively maintained **fresher than the assistant's Jan-2026 training cutoff** — e.g. `cross-tool-model-lineup-2026.md` last reviewed 2026-07-08 with sweep notes through 2026-07-09; `ai-red-teaming-patterns-2026.md` last reviewed 2026-07-09. Injecting datestamped "news" from ad-hoc single-session searches would add noise or error, not value.

## Candidate findings + panel verdicts

| Finding | Panel 1 (usefulness) | Outcome |
|---|---|---|
| **F1** — refresh `ai-coding-model-guidance` model lineup with "latest" ids (Opus 4.8, Sonnet 5, GPT-5.6, Kimi K2.7) | **REJECT** (unanimous): NOT-USEFUL / HIGH-RISK-violates-closed-world-design / ALREADY-COVERED-and-upstream-is-fresher (0.90–0.95) | Dropped |
| **F2** — add the official **OWASP Top 10 for Agentic Applications (2026)** as a companion taxonomy to `ai-red-teaming` | **SPLIT** (USEFUL 0.7 / HIGH-RISK 0.85 / PARTIALLY-NEW 0.7) — all three set the same bar: *useful iff a real, official, additive OWASP artifact* | Advanced → verified → Panel 2 |
| **F3** — add Claude Code CLI features (nested sub-agents, `/cd`) to `claude-app-engineering` | **REJECT**: scope mismatch (that plugin covers the Agent **SDK for building apps**, not the CLI end-user feature set); volatile; wrong home | Dropped |

### F2 verification (the split's empirical hinge)

The three Panel-1 lenses disagreed but converged on one empirical question, so the "tiebreak" was verification, not another opinion panel:

- **Official & durable:** "OWASP Top 10 for Agentic Applications for 2026" is a genuine OWASP GenAI Security Project release (published Dec 2025; Expert Review Board incl. NIST, European Commission, Alan Turing Institute; adopted by Microsoft Security among others). Not a vendor framing.
- **Distinct & additive:** it is the **ASI** series (ASI01–ASI10), separate from the LLM Top 10; ASI03/06/07/08/10 have no LLM-Top-10 equivalent. `ai-red-teaming` did **not** reference it.
- IDs/titles cross-verified across two independent searches + OWASP resource page, F5, Promptfoo, Microsoft, Adversa, Giskard, Auth0, Zealynx. `genai.owasp.org` 403s automated fetch (consistent with the repo's existing sweep notes), so the artifact carries a dated `[verify-at-use]` marker per plugin discipline.

### Panel 2 (detailed review of the drafted change) — both seats APPROVE-WITH-FIXES

- **Accuracy seat:** all 10 IDs correct; 8/10 titles exact. Required fixes — ASI04 → "Agentic Supply Chain Vulnerabilities" (was "compromise"); ASI08 → "Cascading Failures" (drop inserted "agent"); soften publish date to "December 2025"; label the anchor column as this plugin's cross-walk, not OWASP-canonical. **All applied.**
- **Design seat:** placement correct (beside the LLM Top 10 table, before MITRE ATLAS); appropriately minimal (one knowledge section + dual version bump). Required companion edits — header `Last reviewed` bump, intro enumeration, Provenance bullet + extended volatile bullet, `plugin.json` **and** `marketplace.json` version bump in lockstep, CLAUDE.md §8 knowledge-bank row. **All applied.** Scope-creep avoided: Mermaid tree untouched, taxonomy phrase not cascaded into every description, no CHANGELOG added.

Both panels agree (advance → approve-with-fixes) → **no Panel 3 tiebreak required.**

## Change shipped

`ai-red-teaming` **0.1.0 → 0.2.0** — adds the OWASP Top 10 for Agentic Applications (2026) companion agentic map (ASI01–ASI10) to `knowledge/ai-attack-taxonomy-decision-tree.md`, with LLM-Top-10 cross-walk, a "when to reach for it" note, and a dated volatile marker; plus header/intro/provenance consistency edits and the CLAUDE.md knowledge-bank index row.

## Net result

Of the candidate findings, **one** survived rigorous review (F2). F1 and F3 were correctly rejected — the highest-value AI plugins are already maintained fresher than any single-session sweep could improve, and their methodology-first design is working as intended.
