# Knowledge — Community health & governance

> **Last reviewed:** 2026-06-23 · **Confidence:** High (GitHub community-health standards + CNCF/Apache governance norms are well established). The `oss-maintainer-strategist` right-sizes governance to the project from this doc.

Governance is **right-sized to the project**, never copied wholesale. A solo project needs a license + README + a way to report security; a 40-contributor project needs a written decision process and a maintainer ladder.

---

## The community-health file set (GitHub recognizes these)

| File | Purpose | Needed at |
|---|---|---|
| `LICENSE` | the legal grant | **always, before first public commit** |
| `README.md` | what it is, how to use it (marketing) | always |
| `CONTRIBUTING.md` | how to contribute (operations — converts drive-bys) | as soon as you want contributors |
| `CODE_OF_CONDUCT.md` | behavior expectations + enforcement contact | when a community forms |
| `SECURITY.md` | private vulnerability reporting channel + SLA | as soon as anyone depends on you |
| `GOVERNANCE.md` | who decides, how, the maintainer ladder | at multi-maintainer scale |
| `SUPPORT.md` | where to ask questions (vs file bugs) | when issues fill with questions |
| `.github/ISSUE_TEMPLATE/*`, `PULL_REQUEST_TEMPLATE.md` | structure incoming work | when triage load grows |
| `CODEOWNERS` | route reviews automatically | multi-area repos |
| `FUNDING.yml` | sponsorship channels | when sustainability matters |

## Governance models (pick the lightest that fits)

| Model | Decision rule | Fits |
|---|---|---|
| **BDFL** | one person decides; others advise | solo / small, early projects |
| **Maintainer council** | a small group, lazy consensus, tie-break by vote | growing projects, 3-10 maintainers |
| **Meritocratic ladder** | contributor → committer → maintainer → steering, earned by sustained contribution | large projects (Apache-style) |
| **Foundation-governed** | a neutral foundation holds assets/trademarks; a TSC governs | critical infrastructure (CNCF/Apache/Linux Foundation) |

## The contributor funnel (de-risking bus factor)

```
drive-by reporter
  -> first-time contributor  (good-first-issue, a responsive review, a thank-you)
  -> recurring contributor   (help-wanted, mentorship, trust on small areas)
  -> committer / maintainer  (earned commit/triage rights, named in MAINTAINERS)
```

Bus factor is the count of people whose simultaneous departure would stall the project. **One** is a tracked risk, not a fact of life — mitigate by documenting the release process, sharing keys/secrets across ≥2 maintainers, and deliberately growing the funnel.

## CLA vs DCO (operational)

- **DCO** — a `Signed-off-by: Name <email>` line (`git commit -s`) certifying the contributor has the right to submit. Zero paperwork; the default. Enforce with the DCO GitHub App.
- **CLA** — a signed agreement granting the project (or its steward) rights, sometimes enabling relicensing or dual-licensing. Adds friction and a bot gate; justify it (corporate steward, relicensing optionality, dual-license business) or skip it.
- **inbound=outbound** — absent either, the GitHub Terms of Service default is that contributions are offered under the project's license. Fine for many projects; state it in CONTRIBUTING.

## Funding channels

GitHub Sponsors, Open Collective, Tidelift (for dependency-as-a-supported-product), Polar, Thanks.dev. Disclose in `FUNDING.yml`. Funding is **sustainability**, not profit-seeking — it's how a critical project survives its maintainer's day job.

## Provenance
- GitHub "community profile" / community-health-files docs; opensource.guide (GitHub); CNCF & Apache Software Foundation governance patterns; DCO (developercertificate.org). Last reviewed 2026-06-23.
- Templates: [`../templates/contributing-guide.md`](../templates/contributing-guide.md), [`../templates/governance-and-maintainer-ladder.md`](../templates/governance-and-maintainer-ladder.md), [`../templates/security-policy.md`](../templates/security-policy.md).
