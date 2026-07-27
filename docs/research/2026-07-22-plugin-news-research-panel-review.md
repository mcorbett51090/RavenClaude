# Plugin news-research + panel review — 2026-07-22

Scheduled routine: research recent news per active plugin, evaluate findings through expert panels, ship a PR for anything that survives. This is the full audit trail; the accompanying PR implements only the verified correctness fixes.

## Scope + method

**167 active plugins** — no "active" subset distinguishes them, and a genuine deep-research + multi-panel + implementation pass across all 167 in one unattended run must respect the repo's accuracy/anti-churn discipline (never bake unverified "news" into plugin content). Approach:

- **Research fan-out (8 parallel agents, all 167 plugins covered)** by thematic cluster (cloud/devops · app-engineering · data/AI · security/compliance · Microsoft-Salesforce-enterprise · healthcare/regulated verticals · finance/legal/real-estate · operations/other). Each agent read the plugin files **and** web-searched, and was required to **ground every candidate**: quote the exact now-stale text from a real file path + name a real dated (post-~2026-01) development + cite a primary source. "The plugin probably says X" was disqualified by construction. The AI model-lineup files were excluded (self-maintaining, refreshed weekly upstream, carry verify-at-use markers).
- **Panel funnel:** Panel 1 (usefulness, 3 seats) → Panel 2 (source-verified detailed review, accuracy seat + design seat) → Panel 3 (tiebreak, only on disagreement).
- **Orchestrator verification:** every survivor's stale quote was re-confirmed against the actual file and its development re-checked against a primary source before editing.

## Funnel at a glance

| Stage | Result |
|---|---|
| Plugins researched | 167 (8 parallel grounded-research agents, web-searched) |
| Clusters returning zero findings | 6 of 8 (security, cloud/devops, app-eng, healthcare, finance/legal, operations tail) |
| Grounded candidate findings | **2** (power-platform P0; generative-web-media P2) |
| Panel 1 — usefulness | 2/2 advanced (both 3/3 USEFUL) |
| Panel 2 — detailed, source-verified | 2/2 IMPLEMENT |
| Panel 3 — tiebreak | not required (no panel disagreement) |
| **Shipped in this PR** | **2 findings, across 5 files (+ 2 lockstep version bumps)** |

**Why so few:** this is the repo's accuracy-first / anti-churn discipline working as intended. Six of eight clusters found the plugins meticulously hedged (`[verify-at-use]`, retrieval dates, "route to counsel", source placeholders instead of hard numbers) and every checkable dated claim accurate as of 2026-07-22 (K8s 1.36 / Gateway API v1.6.0, Azure Files, AWS Graviton5, Salesforce v67.0 `WITH SECURITY_ENFORCED` already fixed by a prior run, OWASP Top 10:2025 finalized, EN 301 549 v3.2.1 still current, NIST SP 800-61r3, CMS nursing-home staffing already shipped as *repealed*, OBBBA 25D/ITC dates correct, PCI DSS v4.0.1 / ISO 20022 correct). Only two shipped claims were rendered stale by a real dated development with a primary source.

## Findings + verdicts

### F1 — power-platform: Code Apps mislabeled PREVIEW (now GA) · **P0 · shipped**

- **Stale text** (`knowledge/power-apps-code-apps-gotchas.md:17`): _"Code Apps are **PREVIEW** as of 2026-06-10 [verified: Microsoft Learn, `power-apps/developer/code-apps/overview`]."_
- **Development:** Microsoft announced Power Apps Code Apps **generally available on 2026-02-05** (primary: [Microsoft Power Platform blog — "Generally available: host and run code apps in Power Apps"](https://www.microsoft.com/en-us/power-platform/blog/power-apps/generally-available-host-and-run-code-apps-in-power-apps/); corroborated by Aric Levin, Power Apps Guide, Bridgeall, paulbien). The plugin's own "verified 2026-06-10 preview" note was simply mistaken — GA predated it by ~4 months. The "treat as preview / not-for-production" posture it implied is now harmful.
- **Panel 1:** 3/3 USEFUL (~0.96). GA is a monotonic, non-reverting status → durable correctness, not churn.
- **Panel 2:** IMPLEMENT-with-fixes. Accuracy seat confirmed the GA date and flagged an arithmetic slip in the draft ("~5 months" → **"~4 months"**, applied). Design seat caught that the **same stale "preview" claim lived in two more files** in the plugin — correcting them is the same defect, not scope creep, and prevents the plugin contradicting itself.
- **Shipped edits (all under the single `0.44.7 → 0.44.8` bump):**
  - `knowledge/power-apps-code-apps-gotchas.md` — line 17 corrected to GA (dated, primary-sourced, with a correction note); header `Last reviewed` bumped with a correction parenthetical.
  - `skills/power-apps-code-apps/resources/overview.md:5` — "preview feature" → "generally available feature (GA 2026-02-05)".
  - `best-practices/apps-code-app-vs-canvas-tradeoffs.md:51` + provenance line — "preview-stage feature" → "GA (since 2026-02-05) but the unsupported list and CLI version still move" (kept the volatility caveat + `[unverified]` marker).
  - `plugin.json` + `marketplace.json` power-platform entry → **0.44.8** (lockstep).
- CLAUDE.md §8a index row unchanged (it never asserted preview).

### F2 — generative-web-media: EU AI Act Art. 50 marking date missed the Digital Omnibus delay · **P2 · shipped**

- **Stale text** (`knowledge/legal-and-provenance-2026.md:62`, file reviewed 2026-07-13): _"**EU AI Act Article 50** transparency/marking and deepfake-disclosure duties are **enforceable 2 Aug 2026**…"_ — folds "marking" into the flat 2 Aug 2026 date and never mentions the Digital Omnibus.
- **Development:** the EU **Digital Omnibus on AI** (European Parliament 16 Jun 2026; **Council final adoption 29 Jun 2026**) grants a grace period on the **Art. 50(2) machine-readable marking/watermarking** obligation — delayed to **2 Dec 2026** for AI systems placed on the market **before 2 Aug 2026**. The broader Art. 50 transparency + deepfake-disclosure duties, and new systems, still bind at 2 Aug 2026. Sourced to law-firm analyses (Gibson Dunn, Sidley, Winston Taylor, Usercentrics) pending the Official Journal text.
- **Panel 1:** 3/3 USEFUL (~0.76). The proposed fix is self-limiting — one hedged clause + a dated `[verify-at-use]` marker, encoding the uncertainty rather than betting on a hard new date.
- **Panel 2:** IMPLEMENT, unanimous, no required fixes. Accuracy seat independently re-verified the Omnibus facts and procedural dates. Design seat confirmed the website-notice snippet (line ~68, conservative earlier date) is correctly left **unchanged**, and no cascade into CLAUDE.md/agents.
- **Shipped edits:** line 62 gains the marking-delay nuance clause (dated, hedged, defers to the OJ); header `Last reviewed` bumped; `plugin.json` + `marketplace.json` generative-web-media entry → **0.1.2** (lockstep).

## Net result

Of 167 plugins swept, **2 findings** survived grounding + three-panel review and shipped: one P0 correctness fix (power-platform Code Apps GA, corrected in 3 files) and one P2 accuracy nuance (generative-web-media EU AI Act marking delay). Consistent with the routine's base rate (2026-07-08: 3 shipped; 2026-07-13: 1). The overwhelming zero-finding result across six clusters is the anti-churn discipline working as designed, not a gap in coverage.
