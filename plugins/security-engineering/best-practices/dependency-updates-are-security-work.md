# Dependency updates are security work — treat them with the same urgency as CVEs

**Status:** Pattern
**Domain:** Supply chain security
**Applies to:** `security-engineering`

---

## Why this exists

Keeping dependencies current is not just housekeeping — it is a security control. The majority of exploited vulnerabilities have had patches available for weeks or months before exploitation. A dependency that hasn't been updated in six months is statistically likely to carry an unpatched CVE. Automating dependency updates (Dependabot, Renovate) and merging them promptly — not letting them accumulate — keeps the attack surface narrow and the patching effort small.

## How to apply

Enable automated dependency update PRs. Define a policy for how quickly different urgency levels must be merged. Configure the update tool to auto-merge patch updates that pass CI, and route minor/major updates to human review.

```yaml
# .github/dependabot.yml — update every dependency ecosystem weekly
version: 2
updates:
  - package-ecosystem: npm
    directory: "/"
    schedule:
      interval: weekly
    groups:
      all-dependencies:
        patterns: ["*"]
    open-pull-requests-limit: 10
    auto-merge:
      enabled: true          # auto-merge if CI passes and semver is patch

  - package-ecosystem: docker
    directory: "/"
    schedule:
      interval: weekly

  - package-ecosystem: github-actions
    directory: "/"
    schedule:
      interval: weekly
```

Merge policy by urgency:

| Urgency | Trigger | SLA |
|---|---|---|
| Critical CVE (CVSS 9+, reachable) | Security advisory | Patch within 24 hours |
| High CVE (CVSS 7-8, reachable) | Security advisory | Patch within 7 days |
| Patch semver update | Dependabot PR | Auto-merge if CI passes |
| Minor semver update | Dependabot PR | Review and merge within 1 sprint |
| Major semver update | Dependabot PR | Review, plan migration within quarter |

**Do:**
- Enable Dependabot or Renovate on every repository — unautomated updates don't happen.
- Set auto-merge for patch updates that pass CI to reduce human review toil.
- Review Dependabot/Renovate PRs in the weekly team sync — don't let them accumulate.
- Track dependency age as a metric; a repo where the median dependency is 12 months old is a risk.

**Don't:**
- Batch up all dependency updates into a quarterly "dependency sprint" — small, frequent updates are cheaper than large, risky batch upgrades.
- Merge a dependency update without CI passing — even a patch update can break something.
- Suppress Dependabot alerts without a documented reason and a scheduled revisit.

## Edge cases / when the rule does NOT apply

Pinned transitive dependencies in reproducible builds can't always be bumped without changing the lockfile policy. In those cases, run a CVE scanner against the pinned graph and patch selectively.

## See also

- [`../agents/supply-chain-security-engineer.md`](../agents/supply-chain-security-engineer.md) — owns the dependency inventory, CVE triage, and update policy.
- [`./triage-by-exploitability-not-cvss.md`](./triage-by-exploitability-not-cvss.md) — exploitability gates the urgency of a dependency update more accurately than CVSS score alone.

## Provenance

Codifies CISA Known Exploited Vulnerabilities (KEV) catalog patching timelines and the GitHub Dependabot documentation, grounded in the supply-chain-security-engineer's dependency-update policy mandate.

---

_Last reviewed: 2026-06-05 by `claude`_
