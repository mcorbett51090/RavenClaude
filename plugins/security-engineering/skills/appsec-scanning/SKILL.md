---
name: appsec-scanning
description: "Stand up tuned application security scanning in CI: SAST + SCA per-PR, DAST on a deployed build, secret-scanning, and triage by exploitability×blast-radius rather than raw CVSS."
---

# AppSec Scanning in CI

**Purpose:** catch vulnerabilities early and act on the real ones.

## The gate
- **SAST** + **SCA** on every PR (fast, tuned).
- **DAST** against a deployed build (post-merge / nightly).
- **Secret scanning** on every commit — a leaked secret is compromised.

## Triage
Rank by **exploitability × blast radius**, not CVSS alone. Reachability beats severity: a 9.8 in dead code < a 6.5 on an unauthenticated endpoint.

## Fix the class
One SQLi -> parameterize everywhere + a lint rule. Don't whack-a-mole instances.

## Route the verdict
Propose the control + residual risk; `security-reviewer` decides ship/no-ship.
