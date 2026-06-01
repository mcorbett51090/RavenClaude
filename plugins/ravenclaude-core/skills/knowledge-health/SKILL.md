---
name: knowledge-health
description: Surface knowledge-file staleness across all plugins as a Structured Output block. Wraps the `knowledge-health.py` script — sweeps `plugins/*/knowledge/**.md`, groups files by bucket (stale / due_soon / untracked / fresh), and returns a remediation queue. Used by the release checklist and the `ravenclaude doctor` health check. Read this skill before answering "is our knowledge layer current?", "which knowledge files are stale?", or before tagging a marketplace release.
---

# Skill: knowledge-health

This skill is the **read-side surface** for knowledge freshness. The `knowledge-file-staleness-sweep` skill does the deep authoring work (tier classification, named re-verifiers, manual sweep narrative); this one is the **deterministic, scriptable** counterpart that powers automation: the release checklist step, the `ravenclaude doctor` command, and any future dashboard card.

## When to invoke

- **Release checklist** — Step 1.5: run before tagging a marketplace release so a stale knowledge file in the diff is caught at gate-time, not a week after consumers have updated.
- **`ravenclaude doctor`** — one of the health checks; surfaces stale counts in the doctor's report.
- **Ad-hoc** — when the user asks "what's stale?", "which knowledge files need re-verification?", or "is the knowledge layer current?"

## How to invoke

```shell
# Human-readable
python3 plugins/ravenclaude-core/scripts/knowledge-health.py

# JSON for automation / dashboard
python3 plugins/ravenclaude-core/scripts/knowledge-health.py --json

# Custom threshold (default 90 days)
python3 plugins/ravenclaude-core/scripts/knowledge-health.py --threshold-days 180
```

## What the script reads

`plugins/*/knowledge/**/*.md` — every knowledge file across every plugin. It scans the first ~30 lines for a date marker in any of these forms:

- `Last reviewed: 2026-05-21`
- `Last verified: 2026-05-21`
- `last-verified: 2026-05-21`
- `last_verified: 2026-05-21`
- `retrieved: 2026-05-21`

Case-insensitive on the key; ISO-8601 on the value. A file with no recognizable marker lands in the **untracked** bucket — these are gaps, not warnings.

## Buckets

| Bucket | Meaning |
|---|---|
| `stale` | Last verified > threshold-days ago. Re-verify. |
| `due_soon` | Last verified within 30 days of the threshold. Schedule a sweep. |
| `untracked` | No date marker. Add one — these files escape the regular sweep. |
| `fresh` | Last verified within (threshold - 30) days. No action. |

## Pairing with `knowledge-file-staleness-sweep`

The two skills are deliberately separate. `knowledge-file-staleness-sweep` is the **authoring** skill: it's where the Researcher writes the remediation queue with named re-verifiers and Tier 1-5 effort classifications. `knowledge-health` is the **detection** skill: it gives you the inventory and the dates, deterministically, for downstream automation. Use this skill to *find* the work, the staleness-sweep skill to *plan* it.

## Output contract (Structured Output Protocol)

When invoked from a multi-agent dispatch, the skill's output ends with a structured block summarizing the report:

```
---RESULT_START---
{
  "status": "complete",
  "summary": "Knowledge sweep — N stale, N due_soon, N untracked, N fresh.",
  "deliverables": ["staleness inventory by file"],
  "next_actions": ["re-verify stale files (named in the JSON)", "add Last reviewed date to untracked files"],
  "confidence": 1.0
}
---RESULT_END---
```

## See also

- [`scripts/knowledge-health.py`](../../scripts/knowledge-health.py) — the engine.
- [`knowledge-file-staleness-sweep/SKILL.md`](../knowledge-file-staleness-sweep/SKILL.md) — the authoring counterpart.
- [`docs/best-practices/knowledge-categorization-schema.md`](../../knowledge/knowledge-categorization-schema.md) — the Researcher's Tier 1-5 effort taxonomy.
- [`checklists/release-checklist.md`](../../../../checklists/release-checklist.md) — where this skill is wired into the release flow.
