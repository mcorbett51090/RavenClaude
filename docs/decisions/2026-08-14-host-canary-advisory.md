# D4 — Host behavioral canary is advisory first

**Date:** 2026-08-14 · **Branch:** `harden/pr10-canary` · **Owner:** Matt · **Source:** seed #5 / D4 in `docs/plans/2026-08-13-recurring-defect-hardening/decisions.md`

## Ruling

The host behavioral canary (PR 10 / Gate 207) is **advisory**. A miss surfaces a
warning at install / update / status and does **not** fail the install. It is
not a hard onboarding bar.

Recorded here so the gated build step has an in-tree decision, not only the
plan-folder ruling.

## What this does not change

- Gate 207 itself still fails the **build** (exit 2) when the mechanism is
  broken: a canary that reports success without firing the planted marker, or a
  `hash_trust` host whose re-arm notice is stripped on `update`.
- A host lane whose canary cannot be confirmed to fire still ships as
  `supported: false` in `host-support.json`, not silently assumed working.

## Promotion

Making the canary a mandatory onboarding bar is a later owner call. Do not
flip the installer from warn to fail without a new ruling in this folder.
