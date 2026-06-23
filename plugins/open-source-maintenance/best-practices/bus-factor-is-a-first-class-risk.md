# Bus factor is a first-class, tracked risk

**Status:** Pattern (strong default; deviate only with a written reason)
**Domain:** Project sustainability / governance
**Applies to:** `open-source-maintenance`

---

## Why this exists

A project where one person holds the release keys, knows the undocumented build steps, and answers every issue has a **bus factor of one** — a single departure (burnout, job change, life event) stalls or kills it, stranding every downstream user. Treating that concentration as "just how it is" is how critical infrastructure quietly becomes unmaintained. It's a risk to be tracked and mitigated, not a permanent condition.

## How to apply

Read the project's bus factor honestly (who, if they vanished tomorrow, would block releases / security fixes / decisions?). Mitigate deliberately: document the release process so it's not in one head, share publish credentials/secrets across ≥2 maintainers, and grow the contributor funnel ([`../knowledge/community-health-and-governance.md`](../knowledge/community-health-and-governance.md)) from drive-by → recurring → maintainer. Pursue funding so sustained maintenance isn't pure volunteer overtime.

**Do:**
- Document the release and security-response processes as runbooks anyone can execute.
- Distribute keys/permissions across at least two trusted people.
- Curate `good-first-issue` and mentor recurring contributors toward commit rights.

**Don't:**
- Hoard publish access or release knowledge as the sole maintainer.
- Treat "I'm the only one who can do this" as acceptable steady state.

## Edge cases / when the rule does NOT apply

- **A genuinely solo hobby project** with no dependents can run at bus factor one — but say so in the README so adopters can judge the risk.
- **A foundation-governed project** distributes this by design; the rule is satisfied structurally.

## See also
- [`../knowledge/community-health-and-governance.md`](../knowledge/community-health-and-governance.md)
- [`./triage-has-an-sla-and-a-decline-path.md`](./triage-has-an-sla-and-a-decline-path.md)
- [`../templates/governance-and-maintainer-ladder.md`](../templates/governance-and-maintainer-ladder.md)

## Provenance
Codifies the bus-factor / "single point of failure" sustainability concern (opensource.guide, CHAOSS health metrics). Last reviewed 2026-06-23.

---

_Last reviewed: 2026-06-23 by `claude`_
