---
name: characterization-testing
description: "Pin a legacy system's current behavior with characterization / golden-master / approval tests before changing it, so a refactor that changes behavior fails loudly. Reach for this before any edit to untested legacy code."
---

# Skill: Characterization testing

A legacy system's behavior *is* its spec — bugs included. Capture it before you touch it (§2 #1).

## Step 1 — Find the seam
Locate a substitution point where you can drive the code and observe its output without editing in place. If there isn't one, get `codebase-archaeologist` to find a seam.

## Step 2 — Capture current behavior (not desired behavior)
Write tests that assert *what the code does today*, even if it's wrong. The point is a tripwire for unintended change, not correctness.

## Step 3 — Use approval/golden-master where outputs are large
For code with no specified expected value, snapshot the output (an approval test) and lock it as the golden master. Diffs against the snapshot surface behavior change.

## Step 4 — Maximize coverage of the change area
Drive the inputs that exercise the branches you're about to touch. Coverage of the *blast radius*, not the whole system.

## Step 5 — Refactor against the net
Now hand off to `refactoring-engineer`: every refactor stays green; any red is an unintended behavior change caught before it ships.
