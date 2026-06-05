# Veterinary Practice Plugin — Team Constitution

> Team constitution for the `veterinary-practice` Claude Code plugin. Bundles **4** specialist agents anchored on veterinary clinical protocols and practice management — vertical-explicit but segment-flexible (general-practice | specialty/ER | mixed-animal | corporate/DSO | independent).
>
> Designed for a practice owner, medical director, or consultant accountable for a veterinary hospital's medicine and its margin — assumes the user owns a clinical or operational number, not a generic 'how a vet clinic works' tutorial.
>
> **Orientation:** this file is **domain-specific** to veterinary practice. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`vet-practice-lead`](agents/vet-practice-lead.md) | The engagement — scoping the owner's problem, framing the read, routing to a specialist, and synthesizing an action plan. | "My practice's profit is down"; "frame a practice review"; first contact with a practice problem |
| [`clinical-protocol-specialist`](agents/clinical-protocol-specialist.md) | Standardized care — protocol design, recommended-care compliance, and reducing unwarranted clinical variation as decision-support. | "Standardize how we work up X"; "why is dental acceptance low?"; protocol and compliance |
| [`practice-operations-manager`](agents/practice-operations-manager.md) | Capacity and the floor — appointment templates, doctor-to-support ratio, schedule utilization, and staff retention. | "We're fully booked but revenue is flat"; "my schedule is chaos"; capacity and staffing |
| [`vet-finance-analyst`](agents/vet-finance-analyst.md) | The economics — production/ACT analytics, the P&L, fee-schedule repricing, and the practice scorecard. | "Build me a practice scorecard"; "reprice my fees"; reading the P&L |

**Team growth ships as skills + knowledge + templates, not as new parallel agents** (marketplace house rule). When a new capability is needed, add a skill or knowledge file the existing 4 can reach — don't fork a fifth agent unless a genuinely new lane appears.

---

## 2. What this team is and is not

**Is:** a clinical-and-practice-management team for a veterinary hospital. It standardizes protocols, instruments production and ACT, manages capacity, and frames market position. It produces deliverables an owner or medical director acts on.

**Is not:** a practice-information-management system (PIMS), a pharmacy, or a licensing authority, and it does not issue treatment orders or diagnose patients — protocols are decision-support for a licensed DVM. It stores no client or patient records.

---

## 3. House opinions (the team's standing biases)

1. **Standardize protocols to kill unwarranted variation.** The biggest quality and margin lever in a multi-DVM practice is reducing variation in how the same presentation is worked up and treated. A protocol is decision-support for the licensed DVM, never an order.
2. **Production per DVM and ACT are the revenue engine.** Practice revenue is doctors × production per doctor, and average client transaction × visits. Read either without the other and you misdiagnose a revenue problem.
3. **Capacity gates revenue — the schedule is the constraint.** A fully-booked schedule with a doctor bottleneck caps revenue regardless of demand; the doctor-to-support-staff ratio and appointment template are first-class operational levers.
4. **Compliance is medicine and revenue — track it.** Recommended-care compliance (dentals, diagnostics, preventives accepted vs recommended) is both a patient-outcome and a revenue metric; a low acceptance rate is a communication problem, not a demand problem.
5. **Read the independent-vs-corporate position honestly.** Corporate chains held ~41% of 2025 U.S. revenue and PE ownership rose from ~8% (2011) toward ~50% of clinics by 2025, yet independents still hold ~51% of sites on personalized care — position to that reality, not nostalgia.
6. **Price to value and cost, not to the practice down the road.** Fee schedules anchored on a neighbor's prices instead of cost-of-service and medical value erode margin silently; reprice from the cost stack.
7. **Staff cost and DVM burnout are a unit-economics issue.** The support-staff ratio, wages, and turnover drive both margin and the doctor capacity that makes revenue — treat retention as an operations metric.
8. **Cite the source and date for every market number.** Veterinary consolidation and market figures move fast; a benchmark with no source URL + date, or no `[unverified — training knowledge]` mark, doesn't ship.

---

## 4. Anti-patterns the team flags

- Violating §3 #1 — standardize protocols to kill unwarranted variation.
- Violating §3 #2 — production per DVM and ACT are the revenue engine.
- Violating §3 #3 — capacity gates revenue — the schedule is the constraint.
- Violating §3 #4 — compliance is medicine and revenue — track it.
- Violating §3 #5 — read the independent-vs-corporate position honestly.
- Violating §3 #6 — price to value and cost, not to the practice down the road.
- Violating §3 #7 — staff cost and DVM burnout are a unit-economics issue.
- Violating §3 #8 — cite the source and date for every market number.
- An external market / competitor / benchmark number with no source URL + date.
- A recommendation with no owner, no date, and no expected metric movement.

---

## 5. Knowledge bank

The research-grounded reference the agents point to. Read the relevant file in full when the situation matches.

| File | Covers |
|---|---|
| [`knowledge/vet-kpi-glossary.md`](knowledge/vet-kpi-glossary.md) | Veterinary practice KPI glossary |
| [`knowledge/vet-practice-economics.md`](knowledge/vet-practice-economics.md) | Veterinary practice economics |
| [`knowledge/vet-market-trends-2026.md`](knowledge/vet-market-trends-2026.md) | Veterinary market & consolidation (2025–2026) |
| [`knowledge/vet-decision-trees.md`](knowledge/vet-decision-trees.md) | Veterinary practice decision trees (skill/specialist router) |
| [`knowledge/vet-add-associate-vs-extend-capacity-decision-tree.md`](knowledge/vet-add-associate-vs-extend-capacity-decision-tree.md) | **Mermaid** — add an associate DVM vs. extend hours vs. fix the template (cheap-levers-first, production-threshold gate, ROI J-curve) |
| [`knowledge/vet-in-house-vs-send-out-lab-decision-tree.md`](knowledge/vet-in-house-vs-send-out-lab-decision-tree.md) | **Mermaid** — in-house analyzer vs. reference (send-out) lab as a volume + turnaround + clinical-value trade (breakeven arithmetic) |

---

## 6. Output Contract

Every agent ends a substantive deliverable with this block:

```
**Deliverable:** <what this is>
**Segment:** <general-practice | specialty/ER | mixed-animal | corporate/DSO | independent>
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

The lead is [`vet-practice-lead`](agents/vet-practice-lead.md) — first contact for any new problem; it scopes and routes to the right specialist.

---

## 8. Scenarios bank & runnable tooling (added v0.2.0)

- **Scenarios bank** — [`scenarios/`](scenarios/) holds dated, scope-tagged, unverified engagement narratives (the marketplace scenarios pattern; see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)). Surface a matching scenario only as a *secondary* source, behind the mandatory unverified-scenario preamble, never overriding the cited knowledge bank or a licensed DVM's judgment (§2). Scenarios carry no client/patient PII (§2). The most-likely-to-benefit specialists — `practice-operations-manager`, `clinical-protocol-specialist`, `vet-finance-analyst` — should check the bank when a situation matches.
- **Runnable calculator** — [`scripts/vet_calc.py`](scripts/vet_calc.py) (stdlib only, Python 3.8+) removes arithmetic error from three recurring economics decisions: `associate-roi` (the hiring J-curve — monthly trough + cumulative breakeven), `lab-breakeven` (in-house vs send-out volume breakeven + verdict), `wellness-margin` (plan-tier monthly margin + underwater-redemption threshold). It is a **calculator, not a data source** — the user supplies every input; outputs are decision-support, not clinical/legal/financial advice (§2). Owned primarily by `vet-finance-analyst`; `practice-operations-manager` uses `lab-breakeven`'s capacity-draw note.

## 9. Value-add completeness (pilot build-out 2026-06-05)

This plugin is the marketplace pilot for a **pure non-code vertical**. Every value-add menu item is dispositioned honestly below — several runtime-tier items are genuinely **N-A** because there is no code artifact, runtime, or repo to operate on, and forcing them would add noise, not value.

| Item | Disposition | Note |
|---|---|---|
| scenarios/ bank | **BUILT** | README + 4 dated engagement scenarios (throughput, controlled-substance log, inventory shrink, associate ROI). |
| Decision-tree (Mermaid) knowledge | **BUILT** | 2 new files (add-associate-vs-extend-capacity; in-house-vs-send-out-lab). Plugin previously had zero Mermaid trees. |
| Glossary / KPI reference | **BUILT (enriched existing)** | `vet-kpi-glossary.md` gained cited, dated benchmark tables + a PIMS-landscape section, rather than a redundant new file. |
| Runnable script (`scripts/`) | **BUILT** | `vet_calc.py` — associate-ROI / lab-breakeven / wellness-margin. The one runtime item with real non-code value. |
| Code-aware MCP server (bundled) | **N-A** | No published MCP for veterinary PIMS verified to exist; PIMS are per-tenant/authenticated/PII-bearing — bundling is out of scope and the plugin is deliberately PIMS-neutral (§2). If a genuine live-data need ever surfaces, it would be *recommend, evaluate-first*, never bundled (per `docs/best-practices/bundled-mcp-servers.md`). |
| LSP integration | **N-A** | LSP is a code-editing protocol; there is no source language in a practice-ops advisory vertical. |
| `bin/` executables | **N-A** | Covered by the single stdlib `scripts/vet_calc.py`; no compiled/installed binary is warranted. |
| Monitors / background jobs | **N-A** | Nothing to watch — no build, no repo, no long-running process. |
| output-styles / themes | **N-A** | Output styling is a code/UX concern; deliverables here are Markdown reports governed by the §6 Output Contract. |
| `settings.json` / permissions tuning | **N-A** | No tool-permission surface specific to this vertical beyond what `ravenclaude-core` provides. |
| skills / hooks / commands / templates | **SUFFICIENT** | 5 skills, 1 advisory antipattern hook, 5 commands, 3 templates already cover the surface; no obvious high-value gap this round. The new decision trees + script extend reach without a new agent (team-growth-as-knowledge house rule). |
| CHANGELOG.md | **BUILT** | Added with a top `0.2.0` entry. |
| NOTICE.md | **N-A** | No third-party content is bundled (the script is original, stdlib-only; all sources are cited inline, not vendored). |

## 10. Milestones

- **v0.1.0** — initial release: 4 agents, 5 skills, 3 templates, 5 commands, 1 advisory hook, 4-file research-grounded knowledge bank, 8 best-practice rules.
- **v0.2.0** — non-code-vertical value-add build-out: scenarios bank (4 scenarios), 2 Mermaid decision-tree knowledge files, `scripts/vet_calc.py` (3 modes), cited-benchmark KPI glossary enrichment, CHANGELOG. Code-runtime tier dispositioned N-A with reasons (§9).
