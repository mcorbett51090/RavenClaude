---
description: "Design a developer community program — model the lurker→champion funnel, find the stuck stage, install the matching intervention (response SLAs, recognition, good-first-issues, ambassador tier), and set the health scorecard."
---

# /design-community-program

Spawn `community-and-ecosystem-manager` to design or fix a developer community program.

## What it does

1. Sizes and instruments the funnel (lurker → asker → answerer → contributor → champion).
2. Finds the stuck stage via [`../scripts/devrel_calc.py`](../scripts/devrel_calc.py) `community_health`.
3. Installs the matching intervention (first-response SLA, answerer recognition, good-first-issues, ambassador tier with a real value exchange).
4. Routes recurring questions to docs as a gap signal.

## Usage

```
/design-community-program
```

Then describe your community (platform, size, current activity). The agent applies
[`developer-community-funnel-design`](../skills/developer-community-funnel-design/SKILL.md) and the
[`community-health-scorecard`](../templates/community-health-scorecard.md) template.

## Good inputs

- Stage populations if known (lurkers, askers, answerers, contributors).
- Current answer rate / time-to-first-response.
