---
name: supply-chain-security
description: "Secure the software supply chain from the consume side: ingest the SBOM, triage CVEs by reachability, pin dependencies with a deliberate update cadence, verify SLSA provenance, and defend against malicious packages."
---

# Supply-Chain Security (consume side)

**Purpose:** secure what the software is made of.

## Enumerate
Consume the **SBOM** (from devops-cicd). Include transitive deps — you can't patch what you can't see.

## Triage by reachability
A vulnerable function you never call is lower priority. Reachability analysis prevents advisory-drowning.

## Pin + update on policy
Lockfiles + pins for reproducibility; deliberate automated-update cadence gated by tests — never blind auto-merge.

## Verify & defend
SLSA **provenance verification** for critical artifacts; defend against **typosquat / dependency-confusion** (scoped registries, scrutinize new deps + install scripts).
