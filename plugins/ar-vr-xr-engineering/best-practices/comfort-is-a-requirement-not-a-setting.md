# Comfort is a requirement, not a setting

**Status:** Absolute rule
**Domain:** Interaction / comfort / accessibility
**Applies to:** `ar-vr-xr-engineering`

> Engineering rule, not medical advice. Comfort research and mitigations are `[verify-at-use]`. No PII.

---

## Why this exists

A technically brilliant XR experience that makes users nauseous has shipped nothing. Comfort is not a preference to bury in an options menu — it is an acceptance criterion. Vection (visually-induced self-motion) is the main driver of sim-sickness, so the locomotion scheme, a stable sustained framerate, and the comfort mitigations you ship as **defaults** decide whether a broad audience can finish the experience at all.

## How to apply

- Default to the comfortable scheme: teleport/dash + snap turning for broad or mixed audiences; smooth locomotion is opt-in.
- Ship comfort mitigations (vignette/tunneling, static reference frame, seated mode) **on by default**, not hidden.
- Make the accessible choice the default and the intense mode the opt-in — most users keep the default.
- Validate comfort with real users across a range of people and session lengths, on device.

**Do:** treat a comfort failure as a shipping-blocker; ship a11y options (seated/standing, one-handed, dominant hand, snap turn, captions, adjustable text).
**Don't:** default to smooth locomotion "because it's more immersive"; leave comfort options buried and off.

## Edge cases / when the rule does NOT apply

A narrow, VR-experienced, comfort-tolerant target audience (e.g., an intense enthusiast title) may default to smooth locomotion — but it still ships the comfort options, and it still names the audience trade explicitly.

## See also

- [`../skills/comfort-safety-and-accessibility/SKILL.md`](../skills/comfort-safety-and-accessibility/SKILL.md), [`../skills/xr-interaction-and-locomotion/SKILL.md`](../skills/xr-interaction-and-locomotion/SKILL.md)
- General accessibility standards: [`../../accessibility-engineering/CLAUDE.md`](../../accessibility-engineering/CLAUDE.md)

## Provenance

Codifies `xr-interaction-engineer` house opinion and the locomotion-scheme decision tree. Comfort specifics: [`../knowledge/xr-reference-2026.md`](../knowledge/xr-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
