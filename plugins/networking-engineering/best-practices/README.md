# Networking-engineering best-practices

Absolute and strong-default rules the two agents enforce. Each file states *why it
exists*, *how to apply it* (Do/Don't), *edge cases where it does NOT apply*, and its
*provenance*. These are the house opinions from [`../CLAUDE.md`](../CLAUDE.md) §3, in
enforceable form.

| Rule | Status | Gist |
|---|---|---|
| [`no-change-without-a-rollback-path.md`](no-change-without-a-rollback-path.md) | Absolute | Every network change has an auto-revert / saved rollback before it's applied |
| [`allocate-address-space-so-routes-summarize.md`](allocate-address-space-so-routes-summarize.md) | Strong default | Contiguous, hierarchical allocation so routes aggregate at boundaries |
| [`segment-by-trust-boundary-not-convenience.md`](segment-by-trust-boundary-not-convenience.md) | Strong default | Enforcement points where trust changes; management is always separate |
| [`igp-for-reachability-bgp-for-policy.md`](igp-for-reachability-bgp-for-policy.md) | Strong default | Don't run BGP to do an IGP's job or vice versa |
| [`config-as-code-is-the-source-of-truth.md`](config-as-code-is-the-source-of-truth.md) | Strong default | Intent in version control, CI-validated, drift-detected — the device is a render target |

See also the domain-neutral best-practice posture inherited from
[`../../ravenclaude-core/CLAUDE.md`](../../ravenclaude-core/CLAUDE.md).
