---
scenario_id: 2026-06-05-ios-code-signing-release-pipeline
contributed_at: 2026-06-05
plugin: mobile-engineering
product: ios
product_version: "unknown"
scope: likely-general
tags: [code-signing, ci, fastlane, provisioning, release, certificates]
confidence: medium
reviewed: false
---

## Problem

An iOS team's release builds worked on the lead developer's Mac but failed in CI with `No signing certificate "iOS Distribution" found` and, on the rare green build, App Store Connect rejected the upload with a provisioning-profile mismatch. Releases depended on one person's laptop and Keychain — the bus factor was one — and every new CI runner or new team member triggered a half-day of certificate firefighting.

## Constraints context

- Signing identities and provisioning profiles lived in the lead's local Keychain and Xcode's "Automatically manage signing." That's fine for one machine and fatal for shared/ephemeral CI runners that start with an empty Keychain.
- CI ran on clean, ephemeral macOS runners — no persisted Keychain, no pre-installed certificates, no Apple ID session.
- Multiple bundle IDs (app + a notification-service extension + a widget), each needing its own provisioning profile, so "it builds locally" hid the fact that the profiles were resolved implicitly from the local environment.
- Apple's certificate/profile rules and the App Store Connect API are version-volatile `[verify-at-use]` — the team had been copying steps from an old blog post that no longer matched current tooling.

## Attempts

- Tried: exporting the lead's `.p12` and committing it (encrypted) to the repo. Worked once, then rotated out when the cert expired, and committing a signing identity — even encrypted — is a secret-in-repo smell the security review flagged. Rejected.
- Tried: leaning on Xcode "Automatically manage signing" in CI. Failed — automatic signing wants an interactive Apple ID session and a writable Keychain that an ephemeral runner doesn't have. Automatic signing is a *local-dev* convenience, not a CI strategy.
- Tried (the fix): adopted a **declarative, reproducible signing setup**. Used Fastlane `match` to store certificates + profiles in an encrypted, access-controlled remote (a private git repo / cloud bucket) and *fetch + install them into a temporary Keychain on each CI run*, switched the project to **manual** signing with explicit profile names, and authenticated to App Store Connect with an **API key** (issuer ID + key ID + `.p8`) instead of an Apple ID. `[verify-at-use]` — `match`/`gym`/the App Store Connect API surface and Apple's signing requirements change; confirm against current Fastlane + Apple docs before wiring.

## Resolution

**Code signing is part of the build pipeline, and a pipeline must be reproducible on a clean machine — never dependent on one person's Keychain.** The reliable shape:

1. **Signing assets are managed, encrypted, and fetched per-build**, not hand-installed. Fastlane `match` (or an equivalent that stores certs/profiles in an encrypted, access-controlled remote and installs them into a fresh per-run Keychain) makes any runner reproduce the lead's signing environment.
2. **Use manual signing with explicit profiles in CI.** Automatic signing needs an interactive session; manual signing with named profiles is deterministic and debuggable. Every bundle ID (app, extensions, widgets) gets its own explicit profile.
3. **Authenticate to App Store Connect with an API key**, not an Apple ID — no 2FA prompt, no human in the loop, scoped and revocable. Store the `.p8` key + IDs as CI secrets (a **reference**, never committed to the repo).
4. **Treat certs/profiles like the expiring credentials they are.** Track expiry, automate rotation, and make sure a renewal doesn't require the original laptop. The "it only signs on my machine" failure is a bus-factor-of-one waiting to break a release at the worst time.
5. **Design for multiple live versions and phased rollout** downstream of signing — the store is the last mile of the same pipeline, not a separate manual step.

The mental model: if a release can only be cut from one specific Mac, you don't have a release pipeline — you have a person. Make the signing environment reproducible from encrypted, fetched assets so any runner (or teammate) can cut a build.

**Action for the next engineer:** when CI fails with "no signing certificate" or a profile mismatch while local builds pass, stop trying to fix the runner's Keychain by hand. Move to fetched-and-installed signing assets (match-style) + manual signing + an App Store Connect API key, and verify the exact tooling steps against current Fastlane/Apple docs (`[verify-at-use]` — this surface moves).

Cross-reference: complements [`../best-practices/design-for-multiple-live-versions.md`](../best-practices/design-for-multiple-live-versions.md), [`../best-practices/the-store-is-part-of-the-pipeline.md`](../best-practices/the-store-is-part-of-the-pipeline.md), [`../best-practices/secrets-in-the-secure-store.md`](../best-practices/secrets-in-the-secure-store.md), and the [`mobile-release-checklist`](../templates/mobile-release-checklist.md) template. The CI/CD automation itself (runners, Fastlane lanes, store deployment) is the `devops-cicd` lane; this team owns the signing *model* and the release-engineering decisions.
</content>
