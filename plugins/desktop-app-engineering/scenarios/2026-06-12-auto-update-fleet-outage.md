---
scenario_id: 2026-06-12-auto-update-fleet-outage
contributed_at: 2026-06-12
plugin: desktop-app-engineering
product: generic
product_version: "unknown"
scope: likely-general
tags: [auto-update, rollout, rollback, signature, version-floor, channels]
confidence: high
reviewed: false
---

## Problem

A desktop app pushed an auto-update that crashed on launch for a large share of users. Because the updater shipped the new version to **100% of the fleet at once**, the bad build installed everywhere within hours, and — unlike a web deploy — the broken code was now *on each user's machine*. There was no fast way to "roll back the server": every affected user had to receive a *new* update to recover, while support drowned.

## Constraints context

- Desktop auto-update is not a web deploy. Once a client downloads and applies an update, reverting means shipping yet another update — you can't flip a load balancer.
- The updater applied whatever the update feed served, with no **staged rollout** and no **rollback** plan.
- A separate latent risk surfaced in the review: the updater didn't **verify the update's signature** before applying, so the same channel that pushed a bad build could push *malicious* code if the update host or CDN were ever compromised.
- There was no **version floor**, so even after a fix shipped, clients that had disabled or missed updates could linger on the broken build.

## Attempts

- Tried: rushing a fixed build out, again to 100%. It recovered most users but repeated the same all-at-once risk — a second bad build would have been a second fleet-wide outage.
- Tried: a server-side "kill switch" feature flag to disable the broken feature. Helped for a feature-level bug, but did nothing for a build that **crashed on launch** (the flag code never ran).
- Tried (the fix): rebuilt the release process around **signed, staged, reversible** updates.

## Resolution

**A desktop auto-update must be signed, staged, and reversible — because you can't instantly un-install code from the fleet.** The shape that worked:

1. **Verify the signature before applying.** The client checks the update artifact against the release key before installing — TLS alone isn't enough; a compromised host/CDN must not be able to push code.
2. **Channels.** stable / beta, so beta testers absorb risk before the stable fleet sees a build.
3. **Staged rollout.** Ship to a small percentage, watch crash-free-sessions and health metrics, then widen — and **halt** automatically if crash rate spikes.
4. **Rollback + version floor.** Keep the previous version recoverable, and set a minimum-version floor that can force-migrate stragglers off a known-bad build.

The mental model: shipping a desktop update is deploying to thousands of machines you don't control and can't instantly redeploy. Treat it like progressive delivery for a service, with the added rule that the payload must be cryptographically verified because it becomes code on a user's computer.

**Action for the next engineer:** never wire an auto-updater to 100% with no signature check and no rollback. Stage the rollout, verify the signature before apply, keep a rollback, and set a version floor. A launch-crash bug can't be saved by a feature flag — only by not having shipped it to everyone at once.

Cross-reference: complements [`../best-practices/verify-update-signatures-before-apply.md`](../best-practices/verify-update-signatures-before-apply.md), [`../best-practices/stage-rollouts-keep-rollback.md`](../best-practices/stage-rollouts-keep-rollback.md), and the signing/update tree in [`../knowledge/desktop-engineering-decision-trees.md`](../knowledge/desktop-engineering-decision-trees.md). Progressive-delivery infrastructure also relates to `experimentation-growth-engineering`; CI release wiring routes to `devops-cicd`.
