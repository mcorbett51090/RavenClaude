---
description: "Design a DevRel program — locate the journey bottleneck, write the mandate and non-goals, choose outcome metrics, sequence the team, and draft the exec narrative."
---

# /design-devrel-program

Spawn `devrel-lead` to design (or refactor) a DevRel program end-to-end.

## What it does

1. Maps the developer journey and locates the bottleneck (awareness / activation / adoption / expansion).
2. Writes the program **mandate and explicit non-goals**.
3. Selects outcome metrics and pairs every vanity input with the outcome it must drive.
4. Sequences the first hires against the bottleneck.
5. Drafts the one-page exec value narrative.

## Usage

```
/design-devrel-program
```

Then describe your product, stage, audience, and any current metrics. The agent returns a program
charter using [`../templates/devrel-strategy-onepager.md`](../templates/devrel-strategy-onepager.md)
and applies the [`devrel-program-design`](../skills/devrel-program-design/SKILL.md) skill.

## Good inputs

- Where developers currently fall out (if known) — sign-up, activation, adoption.
- Existing metrics you report today (so vanity inputs can be re-paired with outcomes).
- Team size and budget constraints for the hiring sequence.
