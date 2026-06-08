---
name: plan-ota
description: "Design a dual-bank OTA scheme with signed images and automatic rollback before fielding. Reach for this before any device ships."
---

# Skill: Plan OTA and rollback

A device you can't update can't be fixed or secured — a one-way firmware path strands every field bug and CVE (§3 #5).

## Step 1 — Choose the scheme
Dual-bank / A-B images so a bad update never bricks the device (§3 #5).

## Step 2 — Sign the images
Signed/verified images so only authentic firmware boots (§3 #5).

## Step 3 — Automate rollback
Boot-confirm watchdog: a failed boot auto-reverts to the known-good bank (§3 #5).

## Step 4 — Budget the memory
Dual-bank doubles the image footprint — fit it via `embedded_iot_calc.py memory-budget` (§3 #3 #5).

## Output
A dual-bank, signed, auto-rollback OTA design that fits the memory budget, ready before fielding.
