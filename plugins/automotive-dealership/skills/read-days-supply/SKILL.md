---
name: read-days-supply
description: "Read inventory days-supply against a target and quantify floorplan carrying cost. Reach for this on an inventory question."
---

# Skill: Read days-supply

An inventory level without days-supply or floorplan carry is a number out of context (§3 #2).

## Step 1 — Set the sales rate
Units in stock and the average daily sales rate.

## Step 2 — Compute days-supply
Units ÷ daily sales rate via `automotive_dealership_calc.py days-supply` (§3 #2).

## Step 3 — Cost the floorplan
Units × per-unit daily carry → monthly carrying cost.

## Step 4 — Flag the aged units
Price-to-turn the units past target days-supply (§3 #2).

## Output
A days-supply read vs target with the floorplan carrying cost quantified. Traverse Tree 1 in the decision-trees file.
