# edtech-partner-success

EdTech-flavored Partner Success Manager team — a Claude Code plugin in the [RavenClaude marketplace](../../README.md) that bundles 6 specialist agents anchored on the PSM lane.

**For:** an actual PSM running an actual book of EdTech partners. K-12, higher-ed, corporate L&D, or mixed segments — the plugin is vertical-explicit but segment-agnostic.

**Not for:** a generic customer-success tutorial. Not for an AE running a sales motion. Not for end-customer support.

## Roster

| Agent | Owns |
|---|---|
| `partner-success-manager` | Onboarding, adoption, ongoing pulse, day-to-day partner work (EdTech-specialized) |
| `success-playbook-designer` | The play library — renewal / expansion / recovery / advocacy plays |
| `qbr-composer` | QBR materials end-to-end with explicit commitment tracking |
| `learning-analytics-analyst` | Partner-engagement signals, health-score design, dashboard specs |
| `ferpa-comms-translator` | FERPA-aware multilingual / multi-audience partner & end-user comms |
| `partner-profile-curator` | The durable partner record (outlives any one PSM seat) |

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution, routing rules, and house opinions.

## Install

From a consumer project:

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ravenclaude-core@ravenclaude
/plugin install edtech-partner-success@ravenclaude
/reload-plugins
```

Requires `ravenclaude-core@>=0.7.0` (for the alternate-methods Capability Grounding Protocol).

## What's inside

- **6 agents** (above)
- **13 skills:** partner-health-scoring, health-report-dashboard (a self-contained Power-BI/Tableau-style portfolio report — demo data + a generator that rebuilds it from real data), success-plan-authoring, qbr-composition, rostering-data-quality, advocacy-program-design, adoption-sequencing-k12, implementation-90-day-arc, partner-training-program-design, renewal-play-design, expansion-play-design, recovery-play-design, executive-sponsor-mapping
- **BI report:** **[▶ View rendered in your browser](https://mcorbett51090.github.io/RavenClaude/plugins/edtech-partner-success/report.html)** (or the [raw source](report.html)) — the demo on synthetic data; rebuild from real data with `python3 scripts/generate-bi-report.py` after editing [`bi-report/data.json`](bi-report/data.json)
- **8 templates:** success plan, partner profile, QBR deck outline, touchpoint log, escalation memo, health-score dashboard spec, onboarding checklist, annual partner review
- **1 advisory hook:** `flag-psm-anti-patterns.sh` — flags unverified numeric claims, generic boilerplate, missing dates in action items, multi-partner names in `To:` lines, health-score status without named signals
- **Knowledge bank:** empty at v0.1.0; will accumulate production lessons as the plugin gets used

## Boundaries

This plugin defers to `ravenclaude-core` for: project-management RAID/status, security-reviewer (mandatory for student PII / FERPA work), deep-researcher (current state regulation, current rostering-vendor contract language), documentarian (executive prose). And it stays out of: AE sales motions, generic customer support, classroom instruction.
