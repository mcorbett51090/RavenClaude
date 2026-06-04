# Test strategy — <app>

## Pyramid targets
| Level | Scope | Approx share | Tooling |
|---|---|---|---|
| Unit | logic | ~70% | |
| Integration | component/contract | ~20% | |
| E2E | critical journeys | ~10% | Playwright |

## Critical journeys (E2E)
1. 

## Coverage philosophy
Line/branch as a floor (<x>%); mutation testing on: <critical modules>.

## Not testing
- <trivial getters / framework / third-party>
