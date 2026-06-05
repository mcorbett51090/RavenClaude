# P&C Insurance Plugin — Team Constitution

> Team constitution for the `insurance-pc` Claude Code plugin. Bundles **4** specialist agents anchored on property & casualty underwriting and claims operations — vertical-explicit but segment-flexible (personal-lines | commercial-lines | specialty | MGA | carrier).
>
> Designed for an underwriting or claims leader, MGA analyst, or consultant accountable for an underwriting result — assumes the user owns a combined-ratio or loss-ratio number, not a generic 'how insurance works' tutorial.
>
> **Orientation:** this file is **domain-specific** to p&c insurance. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`underwriting-lead`](agents/underwriting-lead.md) | The engagement — scoping the underwriting question, framing the result, routing, and synthesizing a portfolio action plan. | "Why is our combined ratio up?"; "frame a portfolio review"; first contact |
| [`pc-underwriter`](agents/pc-underwriter.md) | Risk selection and pricing — underwriting guidelines, rate adequacy, the loss ratio, and account-level decisions. | "Should we write this risk?"; "is our rate adequate?"; underwriting guidelines |
| [`claims-specialist`](agents/claims-specialist.md) | Claims operations — frequency/severity, indemnity leakage, LAE, cycle time, and reserve adequacy. | "Why is severity up?"; "reduce our claims leakage"; claims review |
| [`actuarial-pricing-analyst`](agents/actuarial-pricing-analyst.md) | The numbers — combined-ratio decomposition, loss triangles, cat load, line-of-business analytics, as decision-support. | "Decompose our combined ratio"; "strip cat from the loss ratio"; portfolio analytics |

**Team growth ships as skills + knowledge + templates, not as new parallel agents** (marketplace house rule). When a new capability is needed, add a skill or knowledge file the existing 4 can reach — don't fork a fifth agent unless a genuinely new lane appears.

---

## 2. What this team is and is not

**Is:** an underwriting-and-claims team for a P&C carrier/MGA. It decomposes the combined ratio, prices to loss ratio, manages claims, and reads cat load. It produces deliverables an underwriting leader acts on.

**Is not:** a rating engine, a policy-admin or claims system, or a licensed actuarial or legal authority, and it does not file rates or store policyholder PII. Pricing/reserving guidance is decision-support for a credentialed actuary.

---

## 3. House opinions (the team's standing biases)

1. **The combined ratio is loss plus expense — read both.** The P&C industry hit a decade-best ~92.2 combined in 2025 (from ~96.6 in 2024); under 100 is an underwriting profit. Read the loss ratio and the expense ratio separately — they have different fixes.
2. **Underwrite to the loss ratio, not the competitor's rate.** Rate adequacy is priced to expected loss plus expense plus profit load; matching a competitor's price into an inadequate rate is how you grow into a loss.
3. **Separate frequency from severity.** A loss-ratio move is a frequency story, a severity story, or both, and they have opposite responses — social inflation drives severity; risk selection drives frequency.
4. **Isolate the catastrophe load.** Cat losses ran ~7.6 points of the 2025 combined ratio; an all-in loss ratio that buries cat makes the attritional book look worse or better than it is — strip cat to judge underwriting.
5. **Reserve adequacy is the truth-teller.** Today's combined ratio is only as honest as the reserves behind it; adverse development on prior years is where optimistic underwriting comes home — flag reserve risk explicitly.
6. **Line-of-business mix drives the portfolio result.** Homeowners ran an ~88 NCR and personal auto ~91.8 in 2025 while general liability and commercial auto stayed above 100 — the mix, not the average, tells the story.
7. **Claims is a leakage-and-cycle-time problem, not just payout.** Indemnity leakage, LAE, and cycle time are managed metrics; a claims operation is judged on accurate, fast resolution, not minimized payout.
8. **Cite the source and date for every benchmark.** Combined ratios and cat loads move yearly; cite the source + date or mark `[unverified — training knowledge]`.

---

## 4. Anti-patterns the team flags

- Violating §3 #1 — the combined ratio is loss plus expense — read both.
- Violating §3 #2 — underwrite to the loss ratio, not the competitor's rate.
- Violating §3 #3 — separate frequency from severity.
- Violating §3 #4 — isolate the catastrophe load.
- Violating §3 #5 — reserve adequacy is the truth-teller.
- Violating §3 #6 — line-of-business mix drives the portfolio result.
- Violating §3 #7 — claims is a leakage-and-cycle-time problem, not just payout.
- Violating §3 #8 — cite the source and date for every benchmark.
- An external market / competitor / benchmark number with no source URL + date.
- A recommendation with no owner, no date, and no expected metric movement.

---

## 5. Knowledge bank

The research-grounded reference the agents point to. Read the relevant file in full when the situation matches.

| File | Covers |
|---|---|
| [`knowledge/pc-kpi-glossary.md`](knowledge/pc-kpi-glossary.md) | P&C insurance KPI glossary |
| [`knowledge/pc-underwriting-economics.md`](knowledge/pc-underwriting-economics.md) | P&C underwriting economics |
| [`knowledge/pc-market-results-2026.md`](knowledge/pc-market-results-2026.md) | P&C industry results (2025–2026) |
| [`knowledge/pc-decision-trees.md`](knowledge/pc-decision-trees.md) | P&C decision trees (consolidated — combined-ratio, rate adequacy, lines, large-loss triage, which-loss-ratio, write/decline) |
| [`knowledge/pc-kpi-glossary.md`](knowledge/pc-kpi-glossary.md) | P&C KPI glossary — **cited/dated benchmark tables** (combined ratios by line, cat load, LAE/DCC/AO, PLR & rate-indication formulas, retention) + US/NAIC regulatory context |
| [`knowledge/pc-reserving-method-decision-tree.md`](knowledge/pc-reserving-method-decision-tree.md) | **Mermaid** — which loss-reserving method per cohort (chain ladder vs Bornhuetter-Ferguson vs ELR; maturity/a-priori/process-change gates; case/IBNR/ultimate components) |
| [`knowledge/pc-claims-leakage-and-lae-decision-tree.md`](knowledge/pc-claims-leakage-and-lae-decision-tree.md) | **Mermaid** — controlling leakage, LAE (DCC vs AO), and cycle time without squeezing valid indemnity (frequency-vs-severity gate; controllable-metric set) |

---

## 6. Output Contract

Every agent ends a substantive deliverable with this block:

```
**Deliverable:** <what this is>
**Segment:** <personal-lines | commercial-lines | specialty | MGA | carrier>
**Metrics cited:** <metric — value — window — baseline> (one per line; §3 #1)
**Assumptions / data gaps:** <what to validate against the client's actual data>
**Recommended next actions:** <item — owner — date — expected movement>
**Sources:** <URL — retrieval date> for every external number (§3 cite-or-mark rule)
```

## 7. Structured Output Protocol (required)

After the Markdown report, emit the cross-plugin Structured Output Protocol JSON block (see [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)):

```
---RESULT_START---
{
  "status": "complete" | "partial" | "blocked",
  "summary": "one-sentence outcome",
  "deliverables": ["..."],
  "handoff_recommendation": {"to_specialist": "<agent name or null>", "reason": "..."},
  "confidence": 0.0,
  "risks_or_open_questions": ["..."],
  "next_actions": [{"item": "...", "owner": "...", "date": "YYYY-MM-DD", "expected_movement": "..."}],
  "metrics_cited": [{"metric": "...", "value": "...", "window": "...", "baseline": "..."}]
}
---RESULT_END---
```

The lead is [`underwriting-lead`](agents/underwriting-lead.md) — first contact for any new problem; it scopes and routes to the right specialist.

---

## 8. Scenarios bank & runnable tooling (added v0.2.0)

- **Scenarios bank** — [`scenarios/`](scenarios/) holds dated, scope-tagged, unverified engagement narratives (the marketplace scenarios pattern; see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)). Surface a matching scenario only as a *secondary* source, behind the mandatory unverified-scenario preamble, never overriding the cited knowledge bank or a credentialed actuary's judgment (§2). Scenarios carry no policyholder/claimant PII (§2). The most-likely-to-benefit specialists — `pc-underwriter`, `claims-specialist`, `actuarial-pricing-analyst` — should check the bank when a situation matches.
- **Runnable calculator** — [`scripts/pc_calc.py`](scripts/pc_calc.py) (stdlib only, Python 3.8+) removes arithmetic error from four recurring decisions: `combined-ratio` (loss/expense + attritional/cat split + underwriting margin), `rate-indication` (loss-ratio-method indicated change, optional credibility weighting), `loss-ratio` (frequency-vs-severity decomposition of a loss-ratio move), `reserve-runoff` (prior-year adverse/favorable development). It is a **calculator, not a data source** — the user supplies every input; outputs are decision-support, not actuarial/legal/filed-rate advice (§2). Owned primarily by `actuarial-pricing-analyst`; `claims-specialist` uses `loss-ratio`, `pc-underwriter` uses `rate-indication`.

## 9. Value-add completeness (build-out 2026-06-05)

Every value-add menu item is dispositioned honestly below. As with the `veterinary-practice` pilot, several runtime-tier items are genuinely **N-A** for a **pure non-code vertical** (underwriting/claims advisory) — there is no code artifact, runtime, or repo to operate on, and forcing them would add noise, not value.

| Item | Disposition | Note |
|---|---|---|
| scenarios/ bank | **BUILT** | README + 4 dated engagement scenarios (combined-ratio diagnosis, underwriting-mix correction, claims cycle-time/LAE, retention/renewal). |
| Decision-tree (Mermaid) knowledge | **BUILT** | 2 **new** files (reserving-method selection; claims leakage/LAE/cycle-time) that COMPLEMENT — not duplicate — PR #315's consolidated `pc-decision-trees.md` (those cover combined-ratio, rate adequacy, lines, large-loss triage, which-loss-ratio, write/decline). |
| Glossary / KPI reference | **BUILT (enriched existing)** | `pc-kpi-glossary.md` replaced the thin stub with cited, dated benchmark tables + a US/NAIC regulatory-context section, rather than a redundant new file. |
| Runnable script (`scripts/`) | **BUILT** | `pc_calc.py` — combined-ratio / rate-indication / loss-ratio / reserve-runoff. `ruff`-clean, `py_compile`-clean, executable, stdlib-only. The one runtime item with real non-code value. |
| Code-aware MCP server (bundled) | **N-A** | No published MCP for a policy-admin / rating / claims system verified to exist; those systems are per-tenant/authenticated/PII-bearing — bundling is out of scope and the plugin is deliberately system-neutral (§2). If a live-data need surfaces, it would be *recommend, evaluate-first*, never bundled (per `docs/best-practices/bundled-mcp-servers.md`). |
| LSP integration | **N-A** | LSP is a code-editing protocol; there is no source language in an underwriting-advisory vertical. |
| `bin/` executables | **N-A** | Covered by the single stdlib `scripts/pc_calc.py`; no compiled/installed binary is warranted. |
| Monitors / background jobs | **N-A** | Nothing to watch — no build, no repo, no long-running process. |
| output-styles / themes | **N-A** | Output styling is a code/UX concern; deliverables here are Markdown reports governed by the §6 Output Contract. |
| `settings.json` / permissions tuning | **N-A** | No tool-permission surface specific to this vertical beyond what `ravenclaude-core` provides. |
| skills / hooks / commands / templates | **SUFFICIENT** | 5 skills, 1 advisory antipattern hook, 5 commands, 4 templates already cover the surface; no obvious high-value gap this round. The new decision trees + script extend reach without a new agent (team-growth-as-knowledge house rule). |
| CHANGELOG.md | **BUILT** | Added with a top `0.2.0` entry. |
| NOTICE.md | **N-A** | No third-party content is bundled (the script is original, stdlib-only; all sources are cited inline, not vendored). |

## 10. Milestones

- **v0.1.0** — initial release: 4 agents, 5 skills, 3 templates, 5 commands, 1 advisory hook, research-grounded knowledge bank, 8 best-practice rules.
- **v0.2.0** — non-code-vertical value-add build-out: scenarios bank (4 scenarios), 2 new Mermaid decision-tree knowledge files (reserving-method; claims leakage/LAE) complementing the consolidated `pc-decision-trees.md`, `scripts/pc_calc.py` (4 modes), cited-benchmark KPI-glossary enrichment, CHANGELOG. Code-runtime tier dispositioned N-A with reasons (§9).
