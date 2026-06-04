---
name: data-classification
description: "Design and apply a usable data classification scheme: a small set of levels (public/internal/confidential/restricted) plus a PII/sensitive flag, handling rules per level, and a mapping to enforceable controls — governing the highest-risk data first."
---

# Data Classification

## A scheme people will use
Few levels: **public / internal / confidential / restricted** + a **PII/sensitive** flag. A 12-tier scheme nobody applies governs nothing.

## Handling rules per level
Access, encryption, retention, sharing — defined per level so classification *means* something.

## Map to controls
Each rule -> an enforceable control (masking, access rule, retention job) in the system that owns it. A policy with no control is aspiration.

## Start high-risk
Classify restricted/PII first; expand. Don't boil the ocean.
