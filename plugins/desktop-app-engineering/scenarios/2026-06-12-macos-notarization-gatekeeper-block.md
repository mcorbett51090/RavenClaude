---
scenario_id: 2026-06-12-macos-notarization-gatekeeper-block
contributed_at: 2026-06-12
plugin: desktop-app-engineering
product: generic
product_version: "unknown"
scope: likely-general
tags: [macos, signing, notarization, gatekeeper, notarytool, altool]
confidence: medium
reviewed: false
---

## Problem

A team shipped a macOS build and beta users reported it "won't open" — macOS showed *"<App> cannot be opened because the developer cannot be verified"* and, for some, *"<App> is damaged and can't be opened."* The app had been **code-signed** with a Developer ID certificate, so the team assumed signing was the whole story. It wasn't: the build was signed but **not notarized**, and Gatekeeper blocks un-notarized apps from the internet regardless of a valid signature.

## Constraints context

- Signing ≠ notarization on modern macOS. Gatekeeper requires the app to be **notarized by Apple** (a malware scan) **and** to have the notarization ticket **stapled** so it verifies offline.
- The CI script used `altool` for the notarization step, copied from an old guide; `altool`'s notarization path is **deprecated** in favor of `notarytool`, and the step was silently doing nothing useful.
- The hardened runtime was not enabled, which notarization also requires.
- Signing credentials lived in a developer's local Keychain, so only one person could produce a "real" build — and that build still wasn't notarized.

## Attempts

- Tried: telling users to right-click → Open / run `xattr -d com.apple.quarantine`. A workaround, not a fix — you can't ship "ask every user to bypass Gatekeeper."
- Tried: re-signing with a different certificate. No effect — the problem was the missing notarization, not the signature.
- Tried (the fix): added the **hardened runtime**, switched the CI step to **`notarytool`** to submit the signed app to Apple, waited for the notarization result, then **stapled** the ticket to the artifact. Moved the signing identity + app-store-connect API key into **CI secrets** so any pipeline run produces a properly signed, notarized, stapled build.

## Resolution

**On macOS you sign *and* notarize *and* staple — all three — and you do it in CI, not on a laptop.** The reliable shape:

1. **Sign with Developer ID + hardened runtime.** The hardened runtime is a notarization prerequisite, not optional.
2. **Notarize with `notarytool`** (not the deprecated `altool`): submit the signed artifact, wait for Apple's result, fix any rejection (usually a signing/entitlements gap).
3. **Staple the ticket** so Gatekeeper can verify offline — without stapling, a user installing without network access still gets blocked.
4. **Keys in CI secrets/HSM.** The signing identity and the App Store Connect API key live in the pipeline, so builds are reproducible and not gated on one person's machine.
5. **Verify the output** (`spctl --assess` / `stapler validate`) before publishing, to catch a broken step before users do.

The mental model: a valid signature says "we know who built this"; notarization says "Apple scanned it and it's not known malware"; stapling says "you can prove that offline." Gatekeeper wants all three.

**Action for the next engineer:** if a signed macOS app is blocked by Gatekeeper, the missing piece is almost always **notarization + stapling**, and the silent culprit is often a stale `altool` step that should be `notarytool`. Confirm the hardened runtime is on and move signing into CI. Tool names and Gatekeeper policy are version-volatile — `[verify-at-use]` against Apple's current docs.

Cross-reference: complements [`../best-practices/sign-and-notarize-every-release.md`](../best-practices/sign-and-notarize-every-release.md) and the signing/update tree in [`../knowledge/desktop-engineering-decision-trees.md`](../knowledge/desktop-engineering-decision-trees.md). CI pipeline mechanics route to `devops-cicd`.
