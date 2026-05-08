# Runbook — *<the exact thing this runbook is for, e.g. "Restart the partner-sync job after a stuck queue">*

> **Audience:** the oncall / operator / future-you who hits this at 2am.
> **Length target:** as short as it can be while still working. No prose between steps. Numbered steps, copy-paste-able commands.
> **BLUF:** the first line below "When to use this" tells the reader whether they're in the right runbook.

**Owner:** *<team or named person who maintains this>*
**Last verified:** YYYY-MM-DD by *<name>*
**Severity this addresses:** *<P1 / P2 / P3 — what page-able situation>*

---

## When to use this
- *<symptom 1 the operator will see>*
- *<symptom 2>*

## When NOT to use this
- *<lookalike symptom that needs a different runbook — link it>*

## Pre-flight (≤ 60 seconds)
1. Confirm you have access: `<command to verify>`
2. Confirm the system is in the expected state: `<command and expected output>`
3. If pre-flight fails, stop and escalate to *<role / channel>*. Do not proceed.

## Procedure

1. *<Step — imperative verb first. One action per step.>*
   ```bash
   <exact command>
   ```
   Expected output: `<one line of what success looks like>`

2. *<Step>*
   ```bash
   <exact command>
   ```

3. *<Step>*
   ```bash
   <exact command>
   ```

## Verify it worked
- *<Check 1 — command + expected output>*
- *<Check 2>*

## If something goes wrong
| Symptom | Likely cause | What to do |
|---------|--------------|------------|
| *<error message or behavior>* | *<cause>* | *<action — or escalate to whom>* |
| *<symptom>* | *<cause>* | *<action>* |

## Rollback
*<How to undo, if applicable. If there's no safe rollback, say so explicitly.>*

## Aftermath
- [ ] Update the incident ticket with what you did and when.
- [ ] If this runbook was wrong, file an issue and tag the owner.
- [ ] If this is the third time this month, escalate the underlying problem.

---

> **Maintenance rule:** this runbook is verified by re-running it at least once per quarter. If "Last verified" is older than 90 days, treat the steps as suspect and verify each one before relying on it.
