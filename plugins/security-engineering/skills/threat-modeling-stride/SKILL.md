---
name: threat-modeling-stride
description: "Threat-model a design with STRIDE: draw the data-flow diagram and trust boundaries, walk STRIDE per element, rank threats by likelihood×impact, and map each to a mitigation or a routed accepted-risk."
---

# Threat Modeling (STRIDE)

**Purpose:** find design flaws before they ship.

## 1. Draw the DFD
Processes, data stores, external entities, data flows — and the **trust boundaries** they cross.

## 2. STRIDE per element
| Threat | Property violated |
|---|---|
| **S**poofing | Authentication |
| **T**ampering | Integrity |
| **R**epudiation | Non-repudiation |
| **I**nfo disclosure | Confidentiality |
| **D**enial of service | Availability |
| **E**levation of privilege | Authorization |

## 3. Rank & treat
Likelihood × impact. Each credible threat -> **mitigate / transfer / accept**. Acceptance routes to `security-reviewer`. Threats cluster where sensitive data flows.
