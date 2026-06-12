---
name: packaging-signing-and-updates
description: "Package, code-sign, and notarize a desktop app for Windows (Authenticode/EV) and macOS (Developer ID + notarytool + staple), and ship a safe signed auto-update (signature verified before apply, channels, staged rollout, rollback, version floor)."
---

# Packaging, Signing & Updates

## Sign, then notarize

| OS | What | Why |
|---|---|---|
| **macOS** | Developer ID sign + **hardened runtime**, then `notarytool` submit + **staple** the ticket | Un-notarized apps are blocked by Gatekeeper |
| **Windows** | Authenticode sign; **EV** cert for instant SmartScreen trust | Standard certs accrue reputation slowly; EV is trusted immediately |
| **Linux** | Sign AppImage/deb/rpm per the target repo's convention | Distro trust + integrity |

**Keys live in CI secrets / an HSM — never on a developer laptop.**

## Safe auto-update (the rules that prevent fleet outages)

1. **Verify the update signature before applying.** An updater that applies an unverified payload is an RCE channel.
2. **Channels** — stable / beta, so testers absorb risk first.
3. **Staged rollout** — ship to a small %, watch crash/health metrics, then widen.
4. **Rollback** — keep the previous version recoverable.
5. **Version floor** — force-migrate clients below a minimum so a broken old build can't linger.

## Tooling (route mechanics to devops-cicd)

- **Electron:** `electron-builder` / Electron Forge + `electron-updater`; per-OS targets, ASAR.
- **Tauri:** the bundler + the **updater plugin** (signed update artifacts).

The signing/notarize/publish *steps* belong in the pipeline — design them here, wire them in `devops-cicd`.

> `notarytool` replaced the deprecated `altool`; Gatekeeper/SmartScreen behavior and cert requirements shift — `[verify-at-use]`.
