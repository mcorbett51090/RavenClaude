# Sign and notarize every release

**Status:** Absolute rule
**Domain:** Distribution & trust
**Applies to:** `desktop-app-engineering`

---

## Why this exists

An unsigned desktop build is a hostile experience and often an outright block. macOS Gatekeeper refuses to launch un-notarized apps ("cannot be opened because the developer cannot be verified"); Windows SmartScreen throws a full-screen warning on unsigned or low-reputation installers. Users read these as "this app is malware," and most abandon the install. Signing + notarization is not release polish — it's the difference between an app that opens and one that doesn't.

## How to apply

| OS | Steps |
|---|---|
| **macOS** | Sign with a **Developer ID** certificate + the **hardened runtime**, submit to Apple with **`notarytool`**, then **staple** the notarization ticket to the artifact. |
| **Windows** | **Authenticode**-sign the installer + binaries; use an **EV** certificate for immediate SmartScreen trust (a standard cert accrues reputation only as downloads accumulate). |
| **Linux** | Sign the AppImage/deb/rpm per the target repository's convention. |

**Do:**
- Keep signing keys/certs in **CI secrets or an HSM** — never on a developer laptop or in the repo.
- Sign **and** notarize as part of the release pipeline so every published artifact is verified.
- Verify the signature on the built artifact before publishing (catch a misconfigured signing step).

**Don't:**
- Ship "just the beta" unsigned — testers get the scariest warnings and assume the app is broken.
- Use `altool` for macOS notarization — it's deprecated; use `notarytool`.
- Store the cert password in plaintext CI config.

## Edge cases / when the rule does NOT apply

Purely internal tools distributed to a small, managed fleet with the cert pre-trusted via MDM can sometimes defer public-CA signing — but they still sign with the org's trusted cert; "unsigned" is never the answer.

## See also

- [`./verify-update-signatures-before-apply.md`](./verify-update-signatures-before-apply.md) — signing's auto-update counterpart.
- [`../knowledge/desktop-engineering-decision-trees.md`](../knowledge/desktop-engineering-decision-trees.md) — the signing/update decision tree.

## Provenance

Apple notarization docs (`notarytool`, hardened runtime, stapling) and Microsoft Authenticode/SmartScreen guidance. Tool names and trust behavior are version-volatile — `[verify-at-use]`. Codifies CLAUDE.md §2 ("signing is part of the architecture").

---

_Last reviewed: 2026-06-12 by `claude`_
