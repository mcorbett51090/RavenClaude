---
name: coordinate-a-security-release
description: Run a coordinated security release for a privately-reported vulnerability — private fix branch, GHSA/CVE assignment, patched versions on every supported line, an advisory, and disclosure timing. Returns the coordinated-release runbook and the advisory skeleton. The vulnerability ANALYSIS routes to security-engineering; this skill owns the release choreography. Shared by both agents.
---

# Skill: coordinate-a-security-release

> **Invoked by:** `release-and-versioning-engineer` and `oss-maintainer-strategist` (shared).
>
> **When to invoke:** a vulnerability arrives via the private channel; a `SECURITY.md` report needs handling; a public issue accidentally disclosed a vuln.
>
> **Output:** the coordinated-release runbook + an advisory skeleton + disclosure timing.
>
> **Boundary:** this skill owns the *release choreography*. The *vulnerability analysis* (is it exploitable? what's the CVSS? what's the blast radius?) routes to `security-engineering/security-reviewer`.

## The runbook (coordinated disclosure)

1. **Receive privately, acknowledge fast.** Confirm via the `SECURITY.md` channel within the stated SLA. Never discuss specifics in a public issue/PR. If it leaked into a public issue, minimize it (lock/redact) and move to private.
2. **Triage severity (with security-engineering).** Confirm it's real, score it (CVSS), and determine which versions/lines are affected.
3. **Fix in private.** Work on a private fork / GitHub Security Advisory draft workspace — a fix in `main` with a telling message *before* the advisory is a 0-day handed to attackers.
4. **Reserve the identifier.** Open a **GHSA** (GitHub Security Advisory); request a **CVE** through it. Keep it in draft.
5. **Prepare patched releases for every supported line.** Backport the fix to each line within the support window (see [`manage-breaking-changes-and-deprecations`](../manage-breaking-changes-and-deprecations/SKILL.md)). Pre-stage the version bumps and `### Security` changelog entries.
6. **Set the disclosure timeline.** Coordinate with the reporter; the common default is up to 90 days, shortened if actively exploited. Notify major downstreams ahead of public disclosure when warranted.
7. **Release + disclose together.** Publish the patched versions, publish the advisory (GHSA → CVE), credit the reporter, and post the upgrade guidance. The fix becoming public and the advisory becoming public happen at the same moment.

## Advisory skeleton

```
Title: <component> <vuln class> (CVE-YYYY-NNNNN / GHSA-xxxx)
Severity: <CVSS vector + score>  Affected: <version ranges>  Patched: <versions>
Summary: <what an attacker can do, plainly>
Workaround: <if any, before upgrading>
Credit: <reporter>  Timeline: reported <date> -> fixed <date> -> disclosed <date>
```

## Guardrails
- **Private first, always** — see [`../../best-practices/security-reports-go-private-first.md`](../../best-practices/security-reports-go-private-first.md). A public fix commit before disclosure is the cardinal error.
- **Patch every supported line, not just `main`** — users on older supported majors are the most exposed.
- **Credit the reporter** unless they decline — it's the social contract that keeps reports coming privately.
- **The analysis is not yours** — route exploitability/scoring to `security-engineering`; you own the release choreography and the advisory.
