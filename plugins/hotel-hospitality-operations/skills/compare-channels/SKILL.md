---
name: compare-channels
description: "Compare channels at net rate after acquisition cost, not gross rate. Reach for this on a channel or OTA question."
---

# Skill: Compare channels

An OTA booking nets less than a direct booking at the same gross rate (§3 #2).

## Step 1 — Set the gross rate
The room rate the guest pays on each channel.

## Step 2 — Subtract acquisition cost
OTA commission vs direct acquisition cost via `hotel_hospitality_operations_calc.py channel-cost` (§3 #2).

## Step 3 — Compare net rate
The margin each channel actually keeps.

## Step 4 — Value direct demand
Repeat/direct lowers long-run acquisition cost (§3 #2 #6).

## Output
A net-rate comparison naming the better channel for the margin.
