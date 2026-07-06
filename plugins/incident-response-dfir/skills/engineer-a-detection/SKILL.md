---
name: engineer-a-detection
description: Turn an observed (or hypothesized) adversary behavior into a durable detection — author a Sigma/SIEM rule, map it to the MITRE ATT&CK technique it covers, and ship a false-positive tuning plan so the rule survives contact with production logs instead of dying in alert fatigue. Returns the rule, its ATT&CK mapping, test cases, and the tuning/allow-list plan. Used by `detection-and-forensics-engineer` (primary).
---

# Skill: engineer-a-detection

> **Invoked by:** `detection-and-forensics-engineer` (primary).
>
> **When to invoke:** "write a detection/Sigma rule for X"; "we keep missing Y"; "this alert is too noisy — tune it"; after a hunt finds a repeatable behavior worth alerting on.
>
> **Output:** a Sigma (or SIEM-native) rule, its MITRE ATT&CK technique ID, test cases (true-positive + benign), and a tuning plan (allow-lists, thresholds, exceptions).

## When to invoke

When a behavior worth alerting on is identified — from an incident, a hunt, threat intel, or a noisy existing rule that needs tuning. Detection-as-code: the output is a reviewable, version-controlled rule, not a console click.

## Output

The rule file, the ATT&CK mapping, sample-log test cases proving it fires (and doesn't over-fire), and the false-positive tuning plan.

## Procedure

1. **State the behavior precisely.** What action, on what data source (process creation, auth log, DNS, cloud audit), leaves what observable? Vague behavior → vague, noisy rule.
2. **Map to MITRE ATT&CK first.** Identify the tactic and technique/sub-technique (e.g. T1059.001 PowerShell under Execution; T1021 Remote Services under Lateral Movement). The mapping is how coverage is reasoned about later — no mapping, no rule. See [`../../knowledge/detection-and-hunting-reference.md`](../../knowledge/detection-and-hunting-reference.md).
3. **Author the Sigma rule.** Write in Sigma (portable across SIEMs) with `title`, `status`, `logsource`, `detection` (selection + condition), `level`, and `tags` including the ATT&CK technique. Prefer robust selectors (behavior/TTP) over brittle ones (a single hash/IP) — climb the pyramid of pain.
4. **Write test cases.** At least one true-positive sample log that must fire, and one benign look-alike that must not. This is the regression suite when you tune later.
5. **Build the tuning plan.** Enumerate expected benign sources (admin tools, backup jobs, vuln scanners), the allow-list/exception strategy, thresholds, and a target false-positive rate. A rule without a tuning plan is a future muted rule.
6. **Set the disposition + severity hint.** What should an analyst do when it fires? Link the triage skill so a firing rule flows into [`../triage-and-classify-an-incident/SKILL.md`](../triage-and-classify-an-incident/SKILL.md).

## Quick reference — Sigma skeleton

| Field | Purpose |
|---|---|
| `title` / `id` / `status` | Human name, UUID, `experimental`→`test`→`stable` maturity |
| `logsource` | product/category/service the rule reads (e.g. `category: process_creation`) |
| `detection` | `selection:` field matches + a `condition:` boolean |
| `level` | `low` / `medium` / `high` / `critical` — the alert weight |
| `tags` | `attack.execution`, `attack.t1059.001` — the ATT&CK mapping |
| `falsepositives` | the documented benign sources (the tuning plan's seed) |

```yaml
title: Suspicious PowerShell EncodedCommand
id: 6e1a...-uuid
status: experimental
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    Image|endswith: '\powershell.exe'
    CommandLine|contains: '-enc'
  condition: selection
falsepositives:
  - Legitimate admin automation using encoded commands (allow-list by host/user)
level: high
tags:
  - attack.execution
  - attack.t1059.001
```

## Guardrails
- **Every detection maps to ATT&CK and has a tuning plan** — no mapping means no coverage story; no tuning plan means alert fatigue. See [`../../best-practices/every-detection-maps-to-attack-and-has-a-tuning-plan.md`](../../best-practices/every-detection-maps-to-attack-and-has-a-tuning-plan.md).
- **Climb the pyramid of pain** — prefer TTP/behavior selectors over a single hash or IP; those are trivial for the adversary to change.
- **Detection-as-code** — version-controlled, reviewed, tested against sample logs; never a one-off SIEM console edit.
- **Tune iteratively, don't mute** — a noisy rule gets an exception, not a delete; deletion loses the coverage.
