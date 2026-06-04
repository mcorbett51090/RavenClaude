# Release checklist

- [ ] Same artifact promoted from staging (by digest), not rebuilt
- [ ] SemVer bump decided (major/minor/patch) and changelog generated
- [ ] Rollout strategy chosen (canary / blue-green / flagged) with abort condition
- [ ] Rollback action defined and rehearsed
- [ ] Health signal / SLO gate wired (observability-sre)
- [ ] SBOM + provenance attached; scan clean or finding accepted by security-reviewer
- [ ] Feature flags set to the intended release state
- [ ] Runbook / on-call notified
