# Test project filters with a dry run before adding them to the production config

**Status:** Pattern
**Domain:** Team portfolio / project tracking
**Applies to:** `team-portfolio`

---

## Why this exists

A project filter that over-matches pulls unrelated activity into a project's count — making the project look more active than it is. A filter that under-matches misses work that belongs to the project — making it look quieter than it is. Both errors undermine the supervisor's trust in the portfolio output. Because filter evaluation happens at collection time, a bad filter contaminates the `portfolio-activity.json` for the entire run. Testing with a dry run before adding the filter to the production config catches these errors before they reach the supervisor's report.

## How to apply

Before adding a project filter to `team-portfolio.json`, test it:

```shell
# Dry-run filter test: run the collector against a test config with only the new project defined
# and inspect the attributed events before updating the production config

python3 scripts/portfolio-collect.py \
  --config /tmp/test-portfolio.json \  # copy of team-portfolio.json with only the new project
  --out /tmp/test-activity.json

# Inspect the project's attributed events:
python3 - <<'PY'
import json
data = json.load(open('/tmp/test-activity.json'))
project = data.get('projects', {}).get('my-new-project', {})
print(f"Attributed events: {len(project.get('events', []))}")
for e in project.get('events', [])[:10]:
    print(f"  {e['type']} | {e['repo']} | {e.get('title', '')[:60]}")
PY
```

Check:
1. Are all attributed events genuinely part of this project? (no over-matching)
2. Are known project PRs/issues present? (no under-matching)
3. Is the event count plausible for the collection window?

Only after the dry run passes all three checks should the filter be added to the production `team-portfolio.json`.

**Do:**
- Run the dry-run test on a recent window that you know the contents of (e.g., a sprint you just completed).
- Check both a title-prefix filter and a label filter if unsure which approach has better precision.

**Don't:**
- Add a project filter by inference ("labels starting with 'website' should work") without verifying against real events.
- Test on a window with no known project activity — a passing test on an empty window is not a passing test.

## Edge cases / when the rule does NOT apply

- A repo-level project filter on a dedicated repo (all activity is attributed to the project by definition) — the dry-run check is still recommended but the over-matching risk is near zero.

## See also

- [`../skills/cross-repo-project-tracking/SKILL.md`](../skills/cross-repo-project-tracking/SKILL.md) — the skill that designs project filters
- [`../knowledge/team-portfolio-decision-trees.md`](../knowledge/team-portfolio-decision-trees.md) — the "Project Filter Design" tree that guides filter type selection

## Provenance

Derived from the `cross-repo-project-tracking` skill's filter-precision guidance. A filter that is "probably right" is not a filter that can be trusted for a supervisor-facing report — the dry run is the evidence bar.

---

_Last reviewed: 2026-06-05 by `claude`_
