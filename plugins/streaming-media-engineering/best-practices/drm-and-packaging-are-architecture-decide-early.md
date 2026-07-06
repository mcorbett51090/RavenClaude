# DRM and packaging are architecture — decide early

**Status:** Absolute rule
**Domain:** Architecture / DRM & packaging
**Applies to:** `streaming-media-engineering`

> Engineering rule, not legal/DRM-licensing advice. DRM/packaging specifics are `[verify-at-use]`. No PII.

---

## Why this exists

DRM and the packaging format feel like late, mechanical steps — encrypt the files, wire up a license server — so teams defer them. That is a trap. The **device/browser reach fixes the multi-DRM matrix** (Widevine for Android/Chrome, FairPlay for Apple, PlayReady for Windows/Edge/smart-TVs), and the packaging format (CMAF/CENC) determines whether one set of assets can serve all of them. Retrofitting encryption, key delivery, and a second DRM after the pipeline is built means re-packaging the catalog and reworking the players — a rebuild, not a patch. Decide it with the architecture.

## How to apply

- Derive the required DRM systems from the device/browser reach matrix up front (`[verify-at-use]` each system's reach + security level).
- Package once with CMAF/CENC so a single encryption serves Widevine + FairPlay + PlayReady.
- Design key delivery, license acquisition, and token/signed-URL protection as part of the architecture, not a bolt-on.
- Route DRM key handling and token design through `ravenclaude-core/security-reviewer` for a security verdict.

**Do:** decide the DRM matrix + packaging with the protocol choice; package CMAF/CENC once.
**Don't:** defer DRM until after packaging; hard-wire a single DRM and re-package later.

## Edge cases / when the rule does NOT apply

Free, non-premium, or internal content may need no DRM at all — decide that *explicitly and early* too. "No DRM" is a valid architecture decision; "we'll figure out DRM later" is the failure mode this rule prevents.

## See also

- [`../skills/streaming-architecture-and-protocol-selection/SKILL.md`](../skills/streaming-architecture-and-protocol-selection/SKILL.md)
- Template: [`../templates/streaming-architecture.md`](../templates/streaming-architecture.md)

## Provenance

Codifies `media-streaming-architect` house opinion and the protocol-choice decision tree. DRM/packaging specifics: [`../knowledge/streaming-reference-2026.md`](../knowledge/streaming-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-03 by `claude`_
