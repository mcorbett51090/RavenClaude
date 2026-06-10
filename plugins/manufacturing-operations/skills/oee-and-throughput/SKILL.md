---
name: oee-and-throughput
description: "Diagnose why the line is slow: compute OEE (availability × performance × quality) with stated denominators, compare takt to cycle time, identify the binding constraint via Theory of Constraints, and Pareto MES/downtime loss — fix the constraint, not a non-bottleneck."
---

# OEE & Throughput

## OEE is a definition, not a vibe
OEE = Availability × Performance × Quality. Each factor has a denominator that can be gamed: Performance needs a stated ideal cycle time (a sandbagged ideal inflates it); Availability needs a stated planned-vs-unplanned downtime split (reclassifying breakdowns as 'planned' flatters it). Refuse to quote OEE until the denominators are named — an undefined number is theater.

## The six big losses
Decompose the loss: breakdowns + setup/changeover (Availability), minor stops + reduced speed (Performance), scrap + rework (Quality). Pareto them and attack the biggest loss *at the constraint* first.

## Find the constraint before optimizing
Theory of Constraints: throughput is governed by the single binding constraint. Identify it (WIP piles up just upstream of it; it starves what's downstream), then exploit → subordinate → elevate. Optimizing a non-bottleneck just makes more WIP — the plant rate doesn't move.

## Takt vs cycle time
Takt = available time ÷ demand. Compare it to measured cycle time honestly: faster than takt makes inventory; slower misses demand. The gap is the diagnostic signal, not the machine's top speed.

## Trust data only as far as it's defined
MES downtime codes drift; an 'unspecified' bucket hides the real loss. A manual tally with honest categories beats a clean MES export with garbage codes.

## Output
An OEE breakdown with stated denominators + the six-big-losses Pareto, a takt-vs-cycle comparison, and a TOC bottleneck identification with the exploit/subordinate/elevate steps. Hand the SMED/kaizen at the constraint to `process-improvement`, the gauge-trust (Gage R&R) and variation-significance questions to `applied-statistics`, and re-planning to the confirmed rate to `production-planner`.
