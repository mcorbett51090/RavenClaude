# Incident-response-dfir Plugin — Team Constitution

> Team constitution for the `incident-response-dfir` Claude Code plugin. Two specialist agents — the **dfir-response-lead** (incident command) and the **detection-and-forensics-engineer** (the technical surface) — plus a knowledge bank, skills, templates, and an advisory hook, aimed at one job: **run a security incident from the first triage decision to the blameless post-mortem, and build the detections and forensics that make it possible.**
>
> **Orientation:** this file is **domain-specific** to blue-team DFIR / SOC. For the domain-neutral team constitution inherited by every plugin (architect, coders, reviewers, project-manager, etc.), see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`dfir-response-lead`](agents/dfir-response-lead.md) | Incident lifecycle (NIST 800-61), triage & severity, containment strategy, eradication/recovery, breach coordination, comms, regulatory notification, tabletops | "is this an incident?"; "run our active breach"; "what are our notification obligations?"; "run a tabletop" |
| [`detection-and-forensics-engineer`](agents/detection-and-forensics-engineer.md) | Detection engineering (SIEM/Sigma/ATT&CK), alert tuning, threat hunting, evidence acquisition & forensics (order of volatility, chain of custody), malware triage | "write a Sigma rule"; "hunt for X"; "image this host"; "triage this binary" |

Two agents map to the two genuinely distinct halves of DFIR — *command* (the incident and the humans around it) and *the technical work* (detections, hunts, forensics, malware). They share skills at the seam where analysis and evidence-handling meet the lifecycle.

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates.

---

## 2. Routing rules (Team Lead)

- **"Is this an incident?" / "what severity?"** → `dfir-response-lead` (drives `triage-and-classify-an-incident`).
- **"We have an active incident — what now?"** → `dfir-response-lead` (drives `run-the-incident-lifecycle`).
- **"What are our breach-notification obligations?"** → `dfir-response-lead` (notification-timeline mapping + legal-review flag).
- **"Write a detection / Sigma rule" / "this alert is too noisy"** → `detection-and-forensics-engineer` (drives `engineer-a-detection`).
- **"Hunt for signs of X" / "are we compromised?"** → `detection-and-forensics-engineer` (drives `hunt-for-a-threat`).
- **"Image this host" / "capture memory before we contain" / "triage this binary"** → `detection-and-forensics-engineer` (drives `acquire-and-preserve-evidence`).
- **The appsec vuln / the compliance obligation / the reliability outage / the platform abuse** → escalate (see §10).

---

## 3. Cross-cutting house opinions (the agents enforce)

1. **Contain before you eradicate.** The NIST phases have an order; stop the spread before removing root cause.
2. **Preserve evidence before you remediate.** Capture volatile evidence (memory) first; a hard power-off destroys it.
3. **Severity drives the response, not the noise.** Classify by business impact × scope, not by how alarming an alert looks.
4. **Every detection maps to ATT&CK and ships with a tuning plan.** No mapping = no coverage story; no tuning = alert fatigue.
5. **Hunt from a hypothesis, up the pyramid of pain.** Hunt TTPs (expensive to change), not just hashes/IPs (trivial to change).
6. **Chain of custody or the evidence is worthless.** Hash at collection, log every touch, analyze a verified copy.
7. **Notification timelines are legal deadlines.** GDPR 72h from awareness; flag legal review, don't self-adjudicate reportability.
8. **The post-mortem is blameless.** Root-cause the system, not a person — or the org learns to hide incidents.
9. **The commander coordinates; someone else touches the keyboard on crown jewels.** Keep command and hands-on-forensics separate.
10. **Volatile claims carry a retrieval date** (tooling, ATT&CK version, regulatory specifics) and are re-verified before quoting.

---

## 4. Anti-patterns the agents flag

- Powering off / reimaging a live compromised host before capturing memory (evidence destruction — the hook flags this on IR docs).
- An incident report that names a person as at-fault (blameless violation — the hook flags this on post-mortems).
- Eradicating piecemeal while the adversary is still active and watching.
- Setting severity by an alert's confidence/volume instead of business impact × scope.
- A detection with no ATT&CK mapping or no tuning plan (invisible coverage / future muted rule).
- A "hunt" that's aimless browsing with no falsifiable hypothesis.
- Un-hashed, un-logged evidence with a broken chain of custody.
- Treating the GDPR 72h clock as advisory, or starting it at incident *closure* instead of *awareness*.
- Detonating an unknown binary on a connected/production host; uploading a confidential sample to a public multiscanner.
- A tooling/framework claim quoted with no retrieval date.

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

Inherits the CGP from `ravenclaude-core`. Before either agent says "I can't" or names a severity/detection/acquisition path, it must:

1. **Check the 5 skills** plus core skills.
2. **Traverse the decision tree** ([`knowledge/incident-lifecycle-decision-tree.md`](knowledge/incident-lifecycle-decision-tree.md) or [`knowledge/detection-and-hunting-reference.md`](knowledge/detection-and-hunting-reference.md)) before naming a severity, containment path, or alert disposition — don't keyword-match.
3. **Try the next-easiest defensible path** before declaring blocked.
4. **Escalate with the mandatory phrasing** — what was tried, what was ruled out, the recommended next path.

See the upstream protocol in [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).

---

## 6. Output Contract

```
Question: <what was asked, in the decision tree's terms>
Decision: <severity / containment path / detection / hunt disposition / acquisition plan + WHY (the tree node)>
Artifacts: <the concrete files/plans to add or change (IR plan, Sigma rule, chain-of-custody log, post-mortem)>
Risks / seams: <evidence, legal/notification, or hand-off to another plugin>
Verdict / next step: <plain-language, tied to the responder's goal>
```

**Plus the cross-plugin Structured Output Protocol JSON block** ([`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)).

---

## 7. Automated checks (hooks)

The `hooks/` directory ships [`flag-dfir-hygiene-smells.sh`](hooks/flag-dfir-hygiene-smells.sh) — a PreToolUse Write/Edit/MultiEdit advisory hook:

| Check | Triggers on | Rule (§3) |
|---|---|---|
| Incident report/post-mortem naming an individual as at-fault | `*postmortem* / *post-incident* / *incident-report*` `.md` | #8 |
| Runbook/IR-plan with a destructive remediation (power off / shut down / reimage / wipe) and no memory/acquisition/evidence mention | `*runbook* / *incident* / *ir-plan* / *response-plan* / *playbook*` `.md` | #2 |

Advisory by default (`exit 0` with stderr warnings). Set `DFIR_STRICT=1` to make it blocking. Patterns are POSIX ERE only (the `check-grep-ere-pcre.py` gate).

---

## 8. Skills in this plugin

| Skill | Primary consumer | What's inside |
|---|---|---|
| [`skills/triage-and-classify-an-incident/SKILL.md`](skills/triage-and-classify-an-incident/SKILL.md) | `dfir-response-lead` | The is-it-an-incident gate + the impact × scope severity matrix + response tier |
| [`skills/run-the-incident-lifecycle/SKILL.md`](skills/run-the-incident-lifecycle/SKILL.md) | `dfir-response-lead` | The NIST 800-61 phase runbook + containment/eradication/recovery + blameless review |
| [`skills/engineer-a-detection/SKILL.md`](skills/engineer-a-detection/SKILL.md) | `detection-and-forensics-engineer` | Sigma rule + ATT&CK mapping + false-positive tuning plan + test cases |
| [`skills/hunt-for-a-threat/SKILL.md`](skills/hunt-for-a-threat/SKILL.md) | `detection-and-forensics-engineer` | Hypothesis-driven, ATT&CK-guided hunt ranked up the pyramid of pain |
| [`skills/acquire-and-preserve-evidence/SKILL.md`](skills/acquire-and-preserve-evidence/SKILL.md) | both (shared) | Order of volatility + chain of custody + per-source acquisition (the pre-remediation gate) |

## 8a. Knowledge bank

| File | Read when |
|---|---|
| [`knowledge/incident-lifecycle-decision-tree.md`](knowledge/incident-lifecycle-decision-tree.md) | Triaging/running an incident — the Mermaid is-it-an-incident → severity → containment tree + the NIST phases |
| [`knowledge/detection-and-hunting-reference.md`](knowledge/detection-and-hunting-reference.md) | Detection/hunting — the Mermaid alert → triage → escalate/tune/hunt tree + ATT&CK tactics + pyramid of pain |
| [`knowledge/forensics-and-evidence-handling.md`](knowledge/forensics-and-evidence-handling.md) | Acquiring evidence — order of volatility table, chain of custody, acquisition per source |
| [`knowledge/dfir-tooling-2026.md`](knowledge/dfir-tooling-2026.md) | Recommending tooling — SIEM/EDR/forensics/sandbox category map (dated, re-verify at use) |

## 9. Templates in this plugin

| Template | Use for |
|---|---|
| [`templates/incident-response-plan.md`](templates/incident-response-plan.md) | An IR plan structured on the four NIST phases (roles, severity, procedures, notification) |
| [`templates/incident-report-postmortem.md`](templates/incident-report-postmortem.md) | A blameless post-incident report (timeline, root cause, lessons, follow-ups) |
| [`templates/chain-of-custody-log.md`](templates/chain-of-custody-log.md) | Per-evidence chain-of-custody record (hashes, transfers, integrity attestations) |

---

## 10. Escalating out of the incident-response-dfir team

- **`security-engineering`** — the application-security / secure-coding fix for the vulnerability that let them in (this plugin owns the *response*, not the appsec remediation).
- **`cybersecurity-grc`** — governance, risk, audit, and the regulatory-obligation depth behind a notification (this plugin maps and flags; GRC owns the compliance program).
- **`observability-sre`** — a reliability (non-security) incident, and the log-pipeline/telemetry an SRE owns that a detection needs.
- **`trust-and-safety`** — platform abuse / content harm (this plugin is the security-incident lane, not the abuse lane).
- **`ravenclaude-core/project-manager`** — RAID / status for a multi-week remediation or program initiative.

---

## 11. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Structured Output Protocol (upstream): [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- Standards this plugin encodes: NIST SP 800-61**r3** (incident response, CSF 2.0-aligned; Apr 2025 — supersedes the r2 *Computer Security Incident Handling Guide* whose four-phase lifecycle the plugin still runs as an operational structure), NIST SP 800-86 (forensics), RFC 3227 (order of volatility), MITRE ATT&CK, the pyramid of pain, Sigma, GDPR Art. 33/34.
- Adjacent plugins: [`../security-engineering/CLAUDE.md`](../security-engineering/CLAUDE.md), [`../cybersecurity-grc/CLAUDE.md`](../cybersecurity-grc/CLAUDE.md), [`../observability-sre/CLAUDE.md`](../observability-sre/CLAUDE.md), [`../trust-and-safety/CLAUDE.md`](../trust-and-safety/CLAUDE.md)

## 12. Milestones

- **v0.1.0** — initial build-out: 2 agents (dfir-response-lead, detection-and-forensics-engineer), 5 skills, 4 knowledge docs (2 Mermaid decision trees + forensics/evidence handling + a dated 2026 DFIR tooling map), 5 best-practices, 3 templates, 1 advisory hook, CHANGELOG.
