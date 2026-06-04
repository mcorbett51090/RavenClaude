# finance — Claude Code plugin

> Corporate finance & FP&A specialist team for the RavenClaude marketplace.

Ships seven specialist agents (FP&A analyst, financial modeler, controller, treasury analyst, valuation analyst, audit-prep specialist, board-pack composer), nine playbook skills (month-end close, variance commentary, model review, board-pack composition, driver-based forecasting, DCF valuation, 13-week cash forecast, SOC control walkthrough, KPI definition), eight working templates, a ten-doc knowledge bank (variance triage, decision trees, ASC 805 / 718 / 740, accrual-cutoff, WACC sourcing, cost accounting, and two FP&A docs — operating model & planning, decision support & unit economics), and one advisory hook that flags common finance anti-patterns on edits.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ravenclaude-core@ravenclaude     # prerequisite
/plugin install finance@ravenclaude
/reload-plugins
```

The plugin requires `ravenclaude-core@>=0.5.0` for the cross-plugin protocols (Grounding, Structured Output, Cited-Adjudicator).

## What's inside

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 7 | [`agents/`](agents/) |
| Skills | 9 | [`skills/`](skills/) |
| Knowledge bank | 10 | [`knowledge/`](knowledge/) |
| Hooks | 1 (advisory) | [`hooks/`](hooks/) |
| Templates | 8 | [`templates/`](templates/) |

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution (roster, routing rules, house opinions, anti-patterns, output contract, escalation paths).

## When to dispatch

```text
"Why is gross margin off this quarter?"      → fpa-analyst
"Build a three-statement model for X"        → financial-modeler
"Help me prep for next month's close"        → controller
"Cash runway looks tight"                    → treasury-analyst
"Need a 409A refresh"                        → valuation-analyst
"Audit kicks off in 6 weeks"                 → audit-prep-specialist
"Quarterly board pack is due Friday"         → board-pack-composer
```

The Team Lead in the consumer's Claude Code session reads this plugin's `CLAUDE.md` and dispatches the right specialist via `ravenclaude-core/skills/spawn-team.md`.

## House opinions (short list)

1. Source-cite every number.
2. No hardcoded numbers in model mechanics.
3. Reconciliation before commentary.
4. Reasonableness over precision.
5. Materiality is a design constraint.
6. Audit trail in every workpaper.
7. Numbers don't ship without commentary.
8. One source of truth per metric.
9. Plain English first, then the technical.
10. Confidentiality by default.

The full list (plus the 13 anti-patterns every agent flags) is in [`CLAUDE.md`](CLAUDE.md) §3 / §4.

## Hooks

- [`hooks/flag-finance-anti-patterns.sh`](hooks/flag-finance-anti-patterns.sh) — PostToolUse Edit/Write/MultiEdit hook. Advisory: flags hardcoded rate-like numbers in model files, plaintext PII patterns (SSN, IBAN, credit card), variance commentary without `Sources:`, forecasts/budgets without `Assumptions:`. Doesn't block edits unless you flip `exit 0` to `exit 1` for a sensitive engagement.

The hook is wired in via [`hooks/hooks.json`](hooks/hooks.json) — when the plugin is installed, Claude Code merges this with the consumer's session hooks automatically.

## License

MIT — same as the rest of the marketplace. See [`../../LICENSE`](../../LICENSE).

## Portfolio report (BI)

A self-contained, Power-BI/Tableau-style **P&L / spend / cash-runway portfolio report — cost-center variance table with drill-downs** ships with this plugin.

> 📊 **[▶ View the report rendered in your browser](https://mcorbett51090.github.io/RavenClaude/plugins/finance/report.html)** — sortable, filterable, with row drill-downs. _(Published, read-only preview of the demo / synthetic data.)_
>
> _(Or [view the raw HTML source](report.html), or download and open locally — no server, no build step.)_

Rebuild from real data by editing [`bi-report/data.json`](bi-report/data.json) and running `python3 scripts/generate-bi-report.py --plugin finance`. Charts are inline SVG (no CDN); the engine + data shape are documented in [`edtech-partner-success/skills/health-report-dashboard`](../edtech-partner-success/skills/health-report-dashboard/SKILL.md).
