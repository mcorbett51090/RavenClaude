---
name: test-strategy-design
description: "Design a test strategy on the pyramid: map defect classes to the cheapest test level that catches them, prioritize by risk, use coverage as a floor and mutation testing as the quality truth, and decide what not to test."
---

# Test Strategy Design

**Purpose:** a suite that catches real defects cheaply.

## The pyramid
```
  /\   few   E2E (critical journeys)
 /--\  some  integration (component interactions)
/----\ many  unit (logic) — fast & deterministic
```
Invert the **ice-cream cone** (mostly E2E) — it's slow and flaky.

## Match level to defect
- Logic bug -> **unit**
- Component/contract interaction -> **integration**
- Critical user journey -> **E2E** (few)

## Coverage vs quality
Line/branch coverage = **floor** (finds untested code). **Mutation testing** = truth (does the suite fail when code is wrong?). Decide what NOT to test (trivial getters, framework, third-party).
