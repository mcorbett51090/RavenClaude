---
name: design-slas-and-catalog
description: "Define an SLA backed by the OLAs and underpinning contracts that make it deliverable, and a service catalog of standard requests. Reach for this when designing service targets or a request catalog."
---

# Skill: Design SLAs & the service catalog

A customer-facing SLA is only real if the internal and vendor commitments behind it exist (§2 #4).

## Step 1 — Define the service
What the service is, who consumes it, and what "good" means to them. Targets follow the customer's need, not what's easy to measure.

## Step 2 — Set the SLA targets
The customer-facing commitments (availability, response/resolution times by priority). Make them specific, measurable, and *deliverable*.

## Step 3 — Back them with OLAs and UCs
For each SLA target, identify the **OLAs** (commitments between internal IT teams) and **underpinning contracts** (vendor SLAs) that must hold for the SLA to be met. A gap here is a future breach — surface it now.

## Step 4 — Build the service catalog
Define the **standard, pre-approved service requests** (access, equipment, common asks) with their fulfillment paths. A service request is not an incident; route repetitive ones to standard-change models.

## Step 5 — Shift left
Add the knowledge/self-service that lets users self-serve the top request types, and instrument the deflection rate (§2 #7). Use the [`sla-ola-definition`](../../templates/sla-ola-definition.md) template.
