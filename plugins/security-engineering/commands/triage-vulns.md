---
description: "Triage a backlog of findings by exploitability and blast radius, group by class, and route verdicts."
argument-hint: "[scanner output / CVE list]"
---

You are running `/security-engineering:triage-vulns`. Use `appsec-engineer` / `supply-chain-security-engineer`.

## Steps
1. For each finding: reachable? exposed? auth required? blast radius?
2. Rank (not by CVSS alone); traverse the vuln-triage tree.
3. Group by OWASP/dependency class; propose class fixes + scan rules.
4. Route ship/no-ship to security-reviewer.
5. Emit the triage (from `templates/vuln-triage.md`) + Structured Output block.
