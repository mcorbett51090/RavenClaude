# Security CI gate (pattern)

- [ ] SAST on PR (tuned, signal > noise)
- [ ] SCA / dependency scan on PR (reachability where available)
- [ ] Secret scanning on every commit + pre-commit
- [ ] DAST on deployed build (nightly / pre-release)
- [ ] SBOM consumed + CVE triage current
- [ ] Findings triaged by exploitability; verdicts routed to security-reviewer
